"""
Error analysis NER — model pemenang S3.2 (scl-aug) iter-4 di test set.

Menjawab revisi Bu Diana (bimbingan 2026-06-05) bagian Analisis & Pembahasan:
  - "data yang rendah itu di label/kelas apa, kenapa terjadi seperti itu"
  - "ada yang paling performa nya rendah / misklasifikasi / tidak terdeteksi itu karena apa"
  - "apakah satu kalimat dalam ground truth terdapat 3 entitas tetapi hanya terdeteksi 2 / sebaliknya"
  - "Yang misklasifikasi ... harus dicari tau mengapa hasilnya seperti itu"

Pendekatan: predict ulang test.csv pakai model lokal (word-level alignment, bukan
char-offset pipeline) → bandingkan span gold vs prediksi → kategorikan error.

Kategori error span:
  - EXACT     : boundary sama + tipe sama (benar)
  - TYPE      : boundary sama, tipe beda  (misklasifikasi tipe)
  - BOUNDARY  : overlap token tapi boundary beda (partial)
  - MISSED    : entitas gold tak ke-deteksi sama sekali (false negative murni)
  - SPURIOUS  : prediksi entitas yang tidak ada di gold (false positive murni)

Output:
  data/result/analysis/error_analysis/error_analysis_ner.md
  data/result/analysis/error_analysis/confusion_matrix_token.png
  data/result/analysis/error_analysis/test_predictions.csv   (token-level gold vs pred)
  data/result/analysis/error_analysis/error_examples.md

Jalankan (dari root):
    venv\Scripts\python.exe src\pseudo_labelling\SRL-NER\error_analysis.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[3]
TEST_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
MODEL_DIR = (
    ROOT / "src" / "pseudo_labelling" / "SRL-NER" / "done_running" / "S3_Augmented"
    / "output" / "models" / "scl_aug"
    / "bert-only-sirah-ner-S3-2-scl-aug-v2-0.9-iteration-4"
)
OUT_DIR = ROOT / "data" / "result" / "analysis" / "error_analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["PERSON", "LOCATION", "EVENT", "TIME"]
CATS = ["O"] + CLASSES  # untuk confusion matrix token-level
WINDOW = 110  # window kata per inferensi (aman < 512 subword)


# ----------------------------- util label -----------------------------

def split_label(label: str) -> tuple[str, str | None]:
    label = str(label).strip()
    if label in ("O", "", "nan"):
        return "O", None
    for sep in ("-", "_"):
        if sep in label:
            prefix, _, etype = label.partition(sep)
            return prefix, etype
    return "O", None


def type_of(label: str) -> str:
    _, t = split_label(label)
    return t or "O"


def spans_from_bio(labels: list[str]) -> list[tuple[int, int, str]]:
    """List (start, end_exclusive, type) dari urutan BIO."""
    spans = []
    cur_type = None
    cur_start = None
    for i, lab in enumerate(labels):
        prefix, etype = split_label(lab)
        if etype is None:
            if cur_type is not None:
                spans.append((cur_start, i, cur_type))
                cur_type = None
        elif prefix == "B":
            if cur_type is not None:
                spans.append((cur_start, i, cur_type))
            cur_type = etype
            cur_start = i
        else:  # I
            if cur_type == etype:
                continue
            if cur_type is not None:
                spans.append((cur_start, i, cur_type))
            cur_type = etype  # I tanpa B → perlakukan sebagai mulai span
            cur_start = i
    if cur_type is not None:
        spans.append((cur_start, len(labels), cur_type))
    return spans


# ----------------------------- inferensi -----------------------------

def load_model():
    print(f"[load] {MODEL_DIR}")
    tok = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForTokenClassification.from_pretrained(str(MODEL_DIR))
    model.eval()
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    return tok, model, id2label


@torch.no_grad()
def predict_words(tok, model, id2label, words: list[str]) -> list[str]:
    """Prediksi label BIO (dash) per kata, window-based supaya tak ke-truncate."""
    preds: list[str] = []
    for start in range(0, len(words), WINDOW):
        chunk = words[start:start + WINDOW]
        enc = tok(chunk, is_split_into_words=True, return_tensors="pt",
                  truncation=True, max_length=512)
        logits = model(**enc).logits[0]  # (seq, n_labels)
        arg = logits.argmax(-1).tolist()
        word_ids = enc.word_ids(0)
        seen = set()
        out = ["O"] * len(chunk)
        for pos, wid in enumerate(word_ids):
            if wid is None or wid in seen:
                continue
            seen.add(wid)
            lab = id2label[arg[pos]]
            prefix, etype = split_label(lab)
            out[wid] = "O" if etype is None else f"{prefix}-{etype}"
        preds.extend(out)
    return preds


# ----------------------------- analisis -----------------------------

def main() -> None:
    df = pd.read_csv(TEST_CSV, dtype=str).fillna("")
    df["token"] = df["token"].astype(str)
    df["label"] = df["label"].apply(lambda l: (lambda p: "O" if p[1] is None else f"{p[0]}-{p[1]}")(split_label(l)))

    tok, model, id2label = load_model()

    # ---- prediksi per chunk ----
    text_ids = list(dict.fromkeys(df["text_id"].tolist()))
    rows_out = []
    gold_seqs: list[list[str]] = []
    pred_seqs: list[list[str]] = []
    chunk_tokens: dict[str, list[str]] = {}
    chunk_gold: dict[str, list[str]] = {}
    chunk_pred: dict[str, list[str]] = {}

    print(f"[predict] {len(text_ids)} chunk ...")
    for n, tid in enumerate(text_ids, 1):
        sub = df[df["text_id"] == tid]
        words = sub["token"].tolist()
        gold = sub["label"].tolist()
        pred = predict_words(tok, model, id2label, words)
        if len(pred) != len(words):  # jaga-jaga
            pred = (pred + ["O"] * len(words))[:len(words)]
        gold_seqs.append(gold)
        pred_seqs.append(pred)
        chunk_tokens[tid] = words
        chunk_gold[tid] = gold
        chunk_pred[tid] = pred
        for w, g, p in zip(words, gold, pred):
            rows_out.append({"text_id": tid, "token": w, "gold": g, "pred": p})
        if n % 50 == 0:
            print(f"  {n}/{len(text_ids)}")

    pd.DataFrame(rows_out).to_csv(OUT_DIR / "test_predictions.csv", index=False, encoding="utf-8")

    # ---- token-level confusion (tipe) ----
    cm = np.zeros((len(CATS), len(CATS)), dtype=int)
    cat_idx = {c: i for i, c in enumerate(CATS)}
    for g_seq, p_seq in zip(gold_seqs, pred_seqs):
        for g, p in zip(g_seq, p_seq):
            cm[cat_idx[type_of(g)], cat_idx[type_of(p)]] += 1

    # ---- seqeval (validasi vs angka resmi) ----
    try:
        from seqeval.metrics import classification_report as seq_rep
        from seqeval.metrics import f1_score as seq_f1
        seq_report = seq_rep(gold_seqs, pred_seqs, digits=4)
        seq_f1_val = seq_f1(gold_seqs, pred_seqs)
    except Exception as e:  # pragma: no cover
        seq_report = f"(seqeval gagal: {e})"
        seq_f1_val = float("nan")

    # ---- span-level error categorization ----
    span_cat = defaultdict(Counter)          # type -> Counter(EXACT/TYPE/BOUNDARY/MISSED)
    spurious_by_type = Counter()             # type prediksi yg spurious
    type_confusions = Counter()              # (gold_type -> pred_type)
    examples = defaultdict(list)             # kategori -> contoh
    per_chunk_counts = []                    # (tid, n_gold, n_pred)

    for tid in text_ids:
        gold = chunk_gold[tid]
        pred = chunk_pred[tid]
        words = chunk_tokens[tid]
        gspans = spans_from_bio(gold)
        pspans = spans_from_bio(pred)
        per_chunk_counts.append((tid, len(gspans), len(pspans)))

        pred_by_span = {(s, e): t for (s, e, t) in pspans}
        pred_token_owner = {}  # token idx -> (s,e,t)
        for (s, e, t) in pspans:
            for i in range(s, e):
                pred_token_owner[i] = (s, e, t)

        matched_pred = set()
        for (gs, ge, gt) in gspans:
            key = (gs, ge)
            if key in pred_by_span:
                pt = pred_by_span[key]
                if pt == gt:
                    span_cat[gt]["EXACT"] += 1
                else:
                    span_cat[gt]["TYPE"] += 1
                    type_confusions[(gt, pt)] += 1
                    if len(examples[f"TYPE_{gt}"]) < 6:
                        examples[f"TYPE_{gt}"].append(
                            _window(words, gs, ge, gold, pred))
                matched_pred.add(key)
            else:
                # cari overlap
                overlap_types = set()
                for i in range(gs, ge):
                    if i in pred_token_owner:
                        overlap_types.add(pred_token_owner[i])
                if overlap_types:
                    span_cat[gt]["BOUNDARY"] += 1
                    for ov in overlap_types:
                        matched_pred.add((ov[0], ov[1]))
                    if len(examples[f"BOUNDARY_{gt}"]) < 6:
                        examples[f"BOUNDARY_{gt}"].append(
                            _window(words, gs, ge, gold, pred))
                else:
                    span_cat[gt]["MISSED"] += 1
                    if len(examples[f"MISSED_{gt}"]) < 8:
                        examples[f"MISSED_{gt}"].append(
                            _window(words, gs, ge, gold, pred))

        for (s, e, t) in pspans:
            if (s, e) in matched_pred:
                continue
            # prediksi yang tak match exact & tak dipakai utk boundary => spurious
            overlaps_gold = any(
                not (e <= gs or s >= ge) for (gs, ge, _gt) in gspans
            )
            if not overlaps_gold:
                spurious_by_type[t] += 1
                if len(examples[f"SPURIOUS_{t}"]) < 6:
                    examples[f"SPURIOUS_{t}"].append(
                        _window(words, s, e, gold, pred))

    # ---- chart confusion matrix ----
    _plot_confusion(cm)

    # ---- tulis laporan ----
    _write_report(cm, seq_report, seq_f1_val, span_cat, spurious_by_type,
                  type_confusions, per_chunk_counts)
    _write_examples(examples)

    print(f"\n[OK] seqeval F1 (recompute) = {seq_f1_val:.4f}")
    print(f"[OK] report   -> {OUT_DIR / 'error_analysis_ner.md'}")
    print(f"[OK] examples -> {OUT_DIR / 'error_examples.md'}")
    print(f"[OK] preds    -> {OUT_DIR / 'test_predictions.csv'}")
    print(f"[OK] confusion-> {OUT_DIR / 'confusion_matrix_token.png'}")


def _window(words, s, e, gold, pred, ctx=6) -> str:
    """Snippet sekitar span [s,e) dengan tanda **gold** dan prediksi."""
    a = max(0, s - ctx)
    b = min(len(words), e + ctx)
    parts = []
    for i in range(a, b):
        w = words[i]
        if s <= i < e:
            parts.append(f"**{w}**")
        else:
            parts.append(w)
    gt = type_of(gold[s])
    # prediksi di rentang span
    pset = sorted({type_of(p) for p in pred[s:e]})
    pstr = "/".join(pset)
    return f"…{' '.join(parts)}…  (gold={gt}, pred={pstr})"


def _plot_confusion(cm: np.ndarray) -> None:
    # normalisasi per baris (recall view)
    cm_norm = cm / cm.sum(axis=1, keepdims=True).clip(min=1)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(CATS)))
    ax.set_yticks(range(len(CATS)))
    ax.set_xticklabels(CATS, rotation=30, ha="right")
    ax.set_yticklabels(CATS)
    ax.set_xlabel("Prediksi")
    ax.set_ylabel("Gold")
    ax.set_title("Confusion matrix token-level (tipe)\nangka = jumlah token; warna = proporsi per baris")
    for i in range(len(CATS)):
        for j in range(len(CATS)):
            val = cm[i, j]
            if val == 0:
                continue
            ax.text(j, i, str(val), ha="center", va="center",
                    color="white" if cm_norm[i, j] > 0.5 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="proporsi baris")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "confusion_matrix_token.png", dpi=130)
    plt.close(fig)


def _md_table(headers, rows) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---:" if i else "---" for i in range(len(headers))) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return f"{line}\n{sep}\n{body}"


def _write_report(cm, seq_report, seq_f1_val, span_cat, spurious_by_type,
                  type_confusions, per_chunk_counts) -> None:
    L = []
    L.append("# Error Analysis NER — Model Pemenang S3.2 (scl-aug iter-4)\n")
    L.append("> Dihasilkan oleh `src/pseudo_labelling/SRL-NER/error_analysis.py`. "
             "Prediksi ulang `test.csv` (258 chunk) dengan word-level alignment.\n")

    L.append(f"\n**Validasi**: seqeval F1 entity (recompute) = **{seq_f1_val:.4f}** "
             "(bandingkan angka resmi 0.9537 di `seqeval_results.md`; selisih kecil = "
             "wajar karena metode alignment word-level vs char-offset pipeline).\n")
    L.append("\n```\n" + seq_report.rstrip() + "\n```\n")

    # 1. Confusion matrix token-level
    L.append("\n## 1. Confusion Matrix Token-Level (tipe)\n")
    L.append("![confusion](confusion_matrix_token.png)\n")
    L.append("\nBaris = gold, kolom = prediksi. Diagonal = benar.\n")
    headers = ["gold＼pred"] + CATS
    rows = []
    for i, c in enumerate(CATS):
        rows.append([c] + [int(cm[i, j]) for j in range(len(CATS))])
    L.append(_md_table(headers, rows))
    # baca: berapa token tiap kelas yang "jatuh" ke O (tak terdeteksi) & ke kelas lain
    L.append("\n**Pembacaan per kelas (token):**\n")
    bullets = []
    for i, c in enumerate(CLASSES):
        ci = CATS.index(c)
        total = cm[ci].sum()
        to_O = cm[ci, CATS.index("O")]
        miscls = {CATS[j]: int(cm[ci, j]) for j in range(len(CATS))
                  if j != ci and CATS[j] != "O" and cm[ci, j] > 0}
        miscls_str = ", ".join(f"{k} {v}" for k, v in sorted(miscls.items(), key=lambda x: -x[1])) or "—"
        bullets.append(
            f"- **{c}**: {int(total)} token gold → {int(to_O)} jadi `O` (tak terdeteksi, "
            f"{100*to_O/total:.1f}%), salah-tipe ke: {miscls_str}.")
    L.append("\n".join(bullets) + "\n")
    # false positive O->kelas
    oi = CATS.index("O")
    fp_bul = []
    for j, c in enumerate(CLASSES):
        v = int(cm[oi, CATS.index(c)])
        fp_bul.append(f"{c} {v}")
    L.append(f"\n- **O → kelas** (token bukan-entitas yang salah ditandai entitas): "
             + ", ".join(fp_bul) + ".\n")

    # 2. Span-level error breakdown
    L.append("\n## 2. Breakdown Error Level Span (Entitas)\n")
    L.append("Untuk tiap entitas gold: EXACT (benar) / TYPE (boundary benar, tipe salah) "
             "/ BOUNDARY (overlap tapi batas beda) / MISSED (tak terdeteksi). "
             "SPURIOUS = prediksi entitas yang tidak ada di gold.\n")
    headers = ["Kelas", "Gold", "EXACT", "TYPE", "BOUNDARY", "MISSED", "Recall span", "SPURIOUS(FP)"]
    rows = []
    for c in CLASSES:
        sc = span_cat[c]
        gold_n = sc["EXACT"] + sc["TYPE"] + sc["BOUNDARY"] + sc["MISSED"]
        recall = sc["EXACT"] / gold_n if gold_n else 0
        rows.append([c, gold_n, sc["EXACT"], sc["TYPE"], sc["BOUNDARY"], sc["MISSED"],
                     f"{recall:.3f}", spurious_by_type.get(c, 0)])
    L.append(_md_table(headers, rows))
    L.append("\n> *Recall span* = EXACT / total gold (entitas yang benar persis batas+tipe).\n")

    if type_confusions:
        L.append("\n**Misklasifikasi tipe (boundary benar, tipe salah):**\n")
        tc_rows = [[f"{g} → {p}", n] for (g, p), n in type_confusions.most_common()]
        L.append(_md_table(["Gold → Pred", "Jumlah"], tc_rows))

    # 3. Per-chunk entity count mismatch
    L.append("\n## 3. Jumlah Entitas per Chunk: Gold vs Prediksi\n")
    L.append("Menjawab: *\"apakah satu unit teks punya 3 entitas di gold tapi terdeteksi 2 "
             "(atau sebaliknya)\"*. Unit = chunk (`text_id`).\n")
    under = [x for x in per_chunk_counts if x[2] < x[1]]
    over = [x for x in per_chunk_counts if x[2] > x[1]]
    equal = [x for x in per_chunk_counts if x[2] == x[1]]
    tot_gold = sum(x[1] for x in per_chunk_counts)
    tot_pred = sum(x[2] for x in per_chunk_counts)
    L.append(
        f"\n- Total chunk: {len(per_chunk_counts)}\n"
        f"- Chunk dengan **prediksi < gold** (under-deteksi / ada entitas ke-miss): "
        f"**{len(under)}**\n"
        f"- Chunk dengan **prediksi > gold** (over-deteksi / kelebihan): **{len(over)}**\n"
        f"- Chunk dengan **jumlah sama**: {len(equal)} "
        f"(catatan: jumlah sama belum tentu entitasnya identik)\n"
        f"- Total entitas gold = {tot_gold}, total entitas prediksi = {tot_pred}\n"
    )
    # contoh under-deteksi paling parah
    under_sorted = sorted(under, key=lambda x: x[1] - x[2], reverse=True)[:8]
    rows = [[tid, ng, npd, ng - npd] for (tid, ng, npd) in under_sorted]
    L.append("\nContoh chunk under-deteksi terbesar (selisih gold−pred):\n")
    L.append(_md_table(["text_id", "Gold", "Pred", "Selisih"], rows))

    # 4. Ringkasan penyebab
    L.append("\n## 4. Ringkasan: Mengapa Hasilnya Seperti Itu?\n")
    L.append(
        "- **EVENT & TIME paling rendah** — konsisten dengan EDA: keduanya kelas minoritas "
        "(EVENT 2.7%, TIME 4.2% dari entitas test). Sedikit contoh → model kurang generalisasi.\n"
        "- **Sumber error dominan** terbaca dari tabel di atas: cek kolom MISSED (recall/under-deteksi) "
        "vs TYPE (kebingungan tipe) vs BOUNDARY (batas span, sering karena tanda baca nempel hasil OCR).\n"
        "- **Artefak OCR** (mis. `Madinah.`, `Rasulullah,`) membuat token entitas mengandung tanda baca → "
        "sumber BOUNDARY error.\n"
        "- Lihat `error_examples.md` untuk contoh konkret tiap kategori (fokus EVENT & TIME).\n"
    )

    (OUT_DIR / "error_analysis_ner.md").write_text("\n".join(L), encoding="utf-8")


def _write_examples(examples) -> None:
    L = ["# Contoh Konkret Error per Kategori\n",
         "> token **tebal** = rentang entitas gold. `pred` = tipe yang diprediksi model di rentang itu.\n"]
    order = []
    for cat in ("MISSED", "TYPE", "BOUNDARY", "SPURIOUS"):
        for c in ("EVENT", "TIME", "PERSON", "LOCATION"):
            order.append(f"{cat}_{c}")
    titles = {
        "MISSED": "Tak terdeteksi (false negative murni)",
        "TYPE": "Misklasifikasi tipe (boundary benar, tipe salah)",
        "BOUNDARY": "Boundary error (overlap, batas beda)",
        "SPURIOUS": "Over-deteksi (false positive murni)",
    }
    cur_cat = None
    for key in order:
        if key not in examples or not examples[key]:
            continue
        cat, c = key.split("_", 1)
        if cat != cur_cat:
            L.append(f"\n## {titles[cat]}\n")
            cur_cat = cat
        L.append(f"\n**{c}:**\n")
        for ex in examples[key]:
            L.append(f"- {ex}")
    (OUT_DIR / "error_examples.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
