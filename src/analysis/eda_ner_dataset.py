"""
EDA dataset NER (SRL-NER) — informasi dataset, tahapan pembentukan data,
distribusi label/kelas, dan contoh data berlabel.

Menjawab revisi Bu Diana (bimbingan 2026-06-05):
  "tambahkan EDA, informasi dataset nya bagaimana, tahapan pembentukan data, menampilkan data"
  + bahan untuk analisis "data yang rendah itu di label/kelas apa".

Sumber: data/result/pseudo-labelling/SRL-NER/{train,test,unlabelled}.csv
  Kolom: text_id, id, token, pos_tag, label  (label skema BIO: O / B-XXX / I-XXX)

Output:
  data/result/analysis/eda/eda_ner_dataset.md       (laporan markdown)
  data/result/analysis/eda/label_distribution.png   (bar chart entitas per kelas)
  data/result/analysis/eda/entities_per_sentence.png (histogram jumlah entitas/kalimat)

Jalankan (Windows PowerShell, dari root project):
    venv\Scripts\python.exe src\analysis\eda_ner_dataset.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRL_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
OUT_DIR = ROOT / "data" / "result" / "analysis" / "eda"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["PERSON", "LOCATION", "EVENT", "TIME"]
CLASS_COLOR = {
    "PERSON": "#4C72B0",
    "LOCATION": "#55A868",
    "EVENT": "#C44E52",
    "TIME": "#8172B3",
}


def split_label(label: str) -> tuple[str, str | None]:
    """'B-LOCATION'/'B_LOCATION' -> ('B','LOCATION'); 'O' -> ('O', None)."""
    label = str(label).strip()
    if label in ("O", "", "nan"):
        return "O", None
    for sep in ("-", "_"):
        if sep in label:
            prefix, _, etype = label.partition(sep)
            return prefix, etype
    return "O", None


def load_split(name: str) -> pd.DataFrame | None:
    path = SRL_DIR / f"{name}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, dtype=str).fillna("")
    df["token"] = df["token"].astype(str)
    if "label" not in df.columns:
        df["label"] = "O"
    return df


def count_entities(df: pd.DataFrame) -> tuple[Counter, Counter, int]:
    """Return (entity_spans per type, entity_tokens per type, n_sentences).

    Entity span = setiap B-XXX memulai 1 entitas; I-XXX lanjutan.
    """
    span_counter: Counter = Counter()
    token_counter: Counter = Counter()
    for _text_id, sub in df.groupby("text_id", sort=False):
        for lab in sub["label"]:
            prefix, etype = split_label(lab)
            if etype is None:
                continue
            token_counter[etype] += 1
            if prefix == "B":
                span_counter[etype] += 1
    n_sentences = df["text_id"].nunique()
    return span_counter, token_counter, n_sentences


def per_sentence_entity_stats(df: pd.DataFrame):
    """Distribusi jumlah entitas (span) per kalimat + berapa kalimat punya tiap tipe."""
    per_sent_count: list[int] = []
    sent_with_type: Counter = Counter()
    for _text_id, sub in df.groupby("text_id", sort=False):
        n_ent = 0
        types_here = set()
        for lab in sub["label"]:
            prefix, etype = split_label(lab)
            if etype is None:
                continue
            if prefix == "B":
                n_ent += 1
                types_here.add(etype)
        per_sent_count.append(n_ent)
        for t in types_here:
            sent_with_type[t] += 1
    return per_sent_count, sent_with_type


def reconstruct(sub: pd.DataFrame) -> str:
    """Rangkai kalimat dengan menandai entitas: kata [PERSON: Abu Bakar]."""
    out: list[str] = []
    buff: list[str] = []
    buff_type: str | None = None

    def flush():
        nonlocal buff, buff_type
        if buff:
            out.append(f"[{buff_type}: {' '.join(buff)}]")
            buff = []
            buff_type = None

    for _, row in sub.iterrows():
        prefix, etype = split_label(row["label"])
        tok = str(row["token"])
        if etype is None:
            flush()
            out.append(tok)
        elif prefix == "B":
            flush()
            buff = [tok]
            buff_type = etype
        else:  # I-
            if buff and buff_type == etype:
                buff.append(tok)
            else:
                flush()
                buff = [tok]
                buff_type = etype
    flush()
    return " ".join(out)


def find_examples(df: pd.DataFrame, etype: str, n: int = 3) -> list[str]:
    """Cari n kalimat yang mengandung entitas tipe `etype`."""
    examples: list[str] = []
    for _text_id, sub in df.groupby("text_id", sort=False):
        has = any(split_label(l)[1] == etype for l in sub["label"])
        if has and len(sub) <= 40:
            examples.append(reconstruct(sub))
        if len(examples) >= n:
            break
    return examples


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---:" if i else "---" for i in range(len(headers))) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return f"{line}\n{sep}\n{body}"


def main() -> None:
    splits = {name: load_split(name) for name in ("train", "test", "unlabelled")}
    splits = {k: v for k, v in splits.items() if v is not None}

    stats = {}
    for name, df in splits.items():
        span_c, token_c, n_sent = count_entities(df)
        n_tokens = len(df)
        n_entity_tokens = sum(token_c.values())
        stats[name] = {
            "df": df,
            "n_sentences": n_sent,
            "n_tokens": n_tokens,
            "spans": span_c,
            "tokens": token_c,
            "n_entity_spans": sum(span_c.values()),
            "n_entity_tokens": n_entity_tokens,
            "pct_entity_tokens": 100 * n_entity_tokens / n_tokens if n_tokens else 0,
            "avg_tokens_per_sent": n_tokens / n_sent if n_sent else 0,
        }

    # ---------- chart 1: distribusi entitas per kelas (train vs test) ----------
    label_splits = [s for s in ("train", "test") if s in stats]
    x = range(len(CLASSES))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, sname in enumerate(label_splits):
        vals = [stats[sname]["spans"].get(c, 0) for c in CLASSES]
        offs = [xi + (i - 0.5) * width for xi in x]
        bars = ax.bar(offs, vals, width=width, label=sname,
                      color=[CLASS_COLOR[c] for c in CLASSES], alpha=0.7 if i else 1.0,
                      edgecolor="black", linewidth=0.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(CLASSES)
    ax.set_ylabel("Jumlah entitas (span)")
    ax.set_title("Distribusi entitas per kelas — train vs test\n(EVENT & TIME = kelas minoritas)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "label_distribution.png", dpi=130)
    plt.close(fig)

    # ---------- chart 2: histogram jumlah entitas per kalimat (train) ----------
    per_sent_train, sent_with_type_train = per_sentence_entity_stats(stats["train"]["df"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    maxc = max(per_sent_train) if per_sent_train else 0
    bins = range(0, min(maxc, 12) + 2)
    ax.hist([min(c, 11) for c in per_sent_train], bins=bins, align="left",
            color="#4C72B0", edgecolor="black", linewidth=0.5, rwidth=0.85)
    ax.set_xlabel("Jumlah entitas per chunk (11 = 11+)")
    ax.set_ylabel("Jumlah chunk (train)")
    ax.set_title("Distribusi jumlah entitas per chunk (train)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "entities_per_sentence.png", dpi=130)
    plt.close(fig)

    # ---------- markdown report ----------
    L: list[str] = []
    L.append("# EDA Dataset NER (SRL-NER)\n")
    L.append("> Dihasilkan oleh `src/analysis/eda_ner_dataset.py`. "
             "Menjawab revisi bimbingan 2026-06-05 (EDA + informasi dataset + tahapan "
             "pembentukan data + menampilkan data).\n")

    # A. Tahapan pembentukan data
    L.append("\n## A. Tahapan Pembentukan Data\n")
    L.append("Pipeline pembentukan dataset NER (dari buku cetak → data train siap model):\n")
    L.append(
        "1. **PDF buku** Sirah Nabawiyah (Al-Mubarakfuri, terj. Kathur Suhardi, 633 hal.) "
        "→ render 633 PNG halaman.\n"
        "2. **OCR (PaddleOCR)** per halaman → teks mentah (`data/result/ocr_txt/page_*.txt`).\n"
        "3. **Konversi CSV** → satu tabel teks per baris.\n"
        "4. **Preprocessing** (pembersihan teks) → `preprocessing_result/`.\n"
        "5. **Chunking** → unit **chunk** ber-`text_id` (≈ paragraf, satu chunk bisa "
        "berisi beberapa kalimat). Total 1.094 chunk.\n"
        "6. **Manual labelling semi-otomatis** (regex + keyword + alias clustering) → "
        "seed berlabel BIO 4 kelas (PERSON/LOCATION/EVENT/TIME).\n"
        "7. **Split** → `train.csv` (seed berlabel), `test.csv` (gold evaluasi), "
        "`unlabelled.csv` (untuk self-training).\n"
        "8. **BERT iterative self-training** (THRESHOLD=0.9) → menambah label pseudo "
        "dari `unlabelled.csv` tiap iterasi.\n"
    )

    # B. Informasi dataset (ukuran)
    L.append("\n## B. Informasi Dataset (Ukuran)\n")
    rows = []
    for name in ("train", "test", "unlabelled"):
        if name not in stats:
            continue
        s = stats[name]
        rows.append([
            name,
            f"{s['n_sentences']:,}",
            f"{s['n_tokens']:,}",
            f"{s['avg_tokens_per_sent']:.1f}",
            f"{s['n_entity_spans']:,}" if name != "unlabelled" else "—",
            f"{s['pct_entity_tokens']:.1f}%" if name != "unlabelled" else "—",
        ])
    L.append(md_table(
        ["Split", "Chunk", "Token", "Avg token/chunk", "Entitas (span)", "% token entitas"],
        rows,
    ))
    L.append("\n> Catatan 1: `text_id` = **chunk** (≈ paragraf, bisa multi-kalimat), bukan "
             "kalimat tunggal. Total 1.094 chunk (599 train + 258 test + 237 unlabelled).\n")
    L.append("\n> Catatan 2: kolom `pos_tag` ada di CSV tetapi **semua bernilai `NN` (placeholder)** "
             "— POS-tag belum benar-benar dipakai sebagai fitur. (Relevan untuk skenario POS-tag.)\n")

    # C. Distribusi label / kelas
    L.append("\n## C. Distribusi Label / Kelas (Bukti Imbalance)\n")
    L.append("![distribusi](label_distribution.png)\n")
    for name in ("train", "test"):
        if name not in stats:
            continue
        s = stats[name]
        total_span = s["n_entity_spans"]
        rows = []
        for c in CLASSES:
            n = s["spans"].get(c, 0)
            ntok = s["tokens"].get(c, 0)
            pct = 100 * n / total_span if total_span else 0
            rows.append([c, f"{n:,}", f"{pct:.1f}%", f"{ntok:,}"])
        # imbalance ratio
        counts = [s["spans"].get(c, 0) for c in CLASSES]
        nonzero = [c for c in counts if c]
        ratio = max(counts) / min(nonzero) if nonzero else 0
        L.append(f"\n**{name}** (total {total_span:,} entitas span):\n")
        L.append(md_table(["Kelas", "Entitas (span)", "% dari entitas", "Token (B+I)"], rows))
        L.append(f"\n> Rasio imbalance (kelas terbanyak : tersedikit) ≈ **{ratio:.1f} : 1**.\n")

    # D. Statistik level chunk
    L.append("\n## D. Statistik Level Chunk (train)\n")
    L.append("![entitas per chunk](entities_per_sentence.png)\n")
    n_zero = sum(1 for c in per_sent_train if c == 0)
    n_total = len(per_sent_train)
    avg_ent = sum(per_sent_train) / n_total if n_total else 0
    L.append(
        f"\n- Chunk tanpa entitas sama sekali: **{n_zero:,} / {n_total:,} "
        f"({100*n_zero/n_total:.1f}%)**\n"
        f"- Rata-rata entitas per chunk: **{avg_ent:.2f}**\n"
        f"- Maksimum entitas dalam satu chunk: **{max(per_sent_train) if per_sent_train else 0}**\n"
    )
    rows = [[c, f"{sent_with_type_train.get(c, 0):,}"] for c in CLASSES]
    L.append("\nJumlah chunk (train) yang mengandung minimal 1 entitas tiap tipe:\n")
    L.append(md_table(["Kelas", "Jumlah chunk"], rows))

    # E. Contoh data berlabel
    L.append("\n## E. Menampilkan Data (Contoh Berlabel)\n")
    L.append("Format: token biasa ditulis apa adanya; entitas ditandai `[TIPE: teks]`.\n")
    for etype in CLASSES:
        L.append(f"\n**Contoh entitas {etype}:**\n")
        exs = find_examples(stats["train"]["df"], etype, n=2)
        if not exs:
            exs = find_examples(stats["test"]["df"], etype, n=2)
        for e in exs:
            L.append(f"- {e}")

    # F. Ringkasan untuk pembahasan
    L.append("\n## F. Ringkasan untuk Pembahasan\n")
    test_spans = stats.get("test", stats["train"])["spans"]
    sorted_classes = sorted(CLASSES, key=lambda c: test_spans.get(c, 0))
    L.append(
        f"- Kelas **paling sedikit** (test): **{sorted_classes[0]}** "
        f"({test_spans.get(sorted_classes[0],0)} entitas) dan **{sorted_classes[1]}** "
        f"({test_spans.get(sorted_classes[1],0)} entitas).\n"
        "- Ini sejalan dengan F1 per-kelas terendah pada EVENT & TIME "
        "(lihat `error_analysis_ner.md`).\n"
        "- Imbalance + jumlah contoh sedikit → hipotesis utama penyebab performa rendah, "
        "yang diuji lebih lanjut di error analysis.\n"
    )

    out_md = OUT_DIR / "eda_ner_dataset.md"
    out_md.write_text("\n".join(L), encoding="utf-8")
    print(f"[OK] EDA report  -> {out_md}")
    print(f"[OK] chart       -> {OUT_DIR / 'label_distribution.png'}")
    print(f"[OK] chart       -> {OUT_DIR / 'entities_per_sentence.png'}")

    # ringkasan console
    for name in ("train", "test", "unlabelled"):
        if name in stats:
            s = stats[name]
            print(f"  {name:11s}: {s['n_sentences']:>6,} kalimat | {s['n_tokens']:>7,} token "
                  f"| {s['n_entity_spans']:>5,} entitas")


if __name__ == "__main__":
    main()
