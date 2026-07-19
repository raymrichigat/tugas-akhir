#!/usr/bin/env python3
"""
recompute_gt_corrected.py — Hitung ulang F1 entity-level (seqeval) + confusion matrix
SEMUA skenario `done_newest` dengan **ground-truth test yang sudah dikoreksi** (arahan
Bu Dini 2026-07-10), TANPA menjalankan model.

Instruksi Bu Dini (2026-07-10):
  "gunakan true label yg sudah diperbaiki kemarin. Hanya prediksi label yg diganti
   dengan skenario tanpa augmentasi."
  → satu gold terkoreksi (dari `label baru.xlsx`, 166 token) dipakai untuk SEMUA skenario;
    prediksi tiap skenario direkonstruksi dari `*-incorrect.xlsx`-nya sendiri (beku).

Sumber koreksi gold: `done_newest/label baru.xlsx` = file incorrect skenario augmentation
(242 baris, selaras 1:1) dengan kolom `true_label` diperbaiki manual. 166 baris berubah.
⚠️ CAVEAT KEADILAN: gold diturunkan HANYA dari kesalahan augmentation → augmentation paling
diuntungkan. Wajib disclosure kalau angka masuk buku. (Opsi A per keputusan Bu Dini.)

Metode rekonstruksi prediksi = identik `seqeval_done_newest.py` (tervalidasi reproduksi
F1 resmi PERSIS): pred := gold_LAMA; override posisi yang ada di `*-incorrect.xlsx` (urut).
Penempatan koreksi gold: susuri test.csv urut, tempatkan tiap baris `label baru`
(selaras aug-incorrect) ke kemunculan pertama (text_id, token, true_OLD) yang match.

Output:
  data/result/analysis/gt_corrected_2026_07_10/
    ├── recompute_gt_corrected_results.md   (tabel before→after + per-label + report)
    └── confusion/<skenario>.png             (confusion token-level 5 kelas, gold terkoreksi)

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\recompute_gt_corrected.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seqeval.metrics import classification_report as seq_report
from seqeval.metrics import f1_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).resolve().parents[3]
DN = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "done_newest"
TEST_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
LABEL_BARU = DN / "label baru.xlsx"
AUG_INC = DN / "augmentation/output_S4_augmentation/evaluation/bert-only-sirah-ner-iterative-6-incorrect.xlsx"

OUT_DIR = ROOT / "data" / "result" / "analysis" / "gt_corrected_2026_07_10"
OUT_MD = OUT_DIR / "recompute_gt_corrected_results.md"
CONF_DIR = OUT_DIR / "confusion"

SCENARIOS = {
    "S1-baseline (indolem uncased)": DN / "baseline/output_S1_baseline/evaluation",
    "S2-weighted-CE":                DN / "weighted_class/output_S2_weighted_ce/evaluation",
    "S3a-SCL":                       DN / "scl/output_S3a_scl/evaluation",
    "S3b-JSCL":                      DN / "jscl/output_S3b_jscl/evaluation",
    "S4-augmentation":               DN / "augmentation/output_S4_augmentation/evaluation",
    "S5-POS-tag":                    DN / "pos_tag/output_pos_tag/evaluation",
    "B-indobert-cased (p1)":         DN / "indobert-base-p1/output_GrupB_cased/evaluation",
    "B-roberta (indo)":              DN / "roberta/output_GrupB_roberta/evaluation",
    "B-cahya-bert-1.5G":             DN / "cahya-bert-base/output_GrupB_cahya/evaluation",
    "B-distilbert":                  DN / "distilbert/output_GrupB_distilbert/evaluation",
}
LABELS = ["PERSON", "LOCATION", "EVENT", "TIME"]
CONF_CLASSES = ["O", "PERSON", "LOCATION", "EVENT", "TIME"]


def to_dash(lbl: str) -> str:
    lbl = str(lbl)
    if lbl.startswith(("B_", "I_")):
        return lbl.replace("_", "-", 1)
    return lbl


def ent_type(lbl: str) -> str:
    """B-PERSON/I-PERSON -> PERSON; O -> O. Untuk confusion token-level 5 kelas."""
    lbl = str(lbl)
    if lbl.startswith(("B-", "I-")):
        return lbl[2:]
    return "O"


def pick_iter_file(eval_dir: Path, suffix: str) -> Path | None:
    cands = sorted(eval_dir.glob(f"*-{suffix}.xlsx"))
    if not cands:
        return None
    def iter_num(p: Path) -> int:
        parts = p.stem.split("-")
        for i, tok in enumerate(parts):
            if tok == "iterative" and i + 1 < len(parts) and parts[i + 1].isdigit():
                return int(parts[i + 1])
        return 1
    return max(cands, key=iter_num)


def build_corrected_gold(gold: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Terapkan 166 koreksi (label baru vs aug-incorrect) ke kolom gold. Return gold_corrected."""
    lb = pd.read_excel(LABEL_BARU)
    ai = pd.read_excel(AUG_INC)
    for df in (lb, ai):
        df.columns = [c.strip() for c in df.columns]
    assert len(lb) == len(ai), "label baru vs aug-incorrect beda jumlah baris"
    tid = lb["text_id"].astype(str).tolist()
    tok = lb["token"].astype(str).tolist()
    true_old = ai["true_label"].astype(str).map(to_dash).tolist()   # gold LAMA (utk placement)
    true_new = lb["true_label"].astype(str).map(to_dash).tolist()   # gold BARU

    g_tid = gold["text_id"].tolist()
    g_tok = gold["token"].tolist()
    g_lab = gold["label"].tolist()
    corrected = list(g_lab)

    pi = 0
    n_applied = 0
    for j in range(len(gold)):
        if pi < len(lb) and g_tid[j] == tid[pi] and g_tok[j] == tok[pi] and g_lab[j] == true_old[pi]:
            if corrected[j] != true_new[pi]:
                n_applied += 1
            corrected[j] = true_new[pi]
            pi += 1
    info = {"n_rows": len(lb), "n_placed": pi, "n_changed": n_applied}
    return pd.Series(corrected, index=gold.index), info


def reconstruct_pred(eval_dir: Path, gold: pd.DataFrame) -> tuple[pd.Series, dict]:
    """pred := gold_LAMA; override dari *-incorrect.xlsx (metode resmi seqeval_done_newest)."""
    f_inc = pick_iter_file(eval_dir, "incorrect")
    if f_inc is None:
        raise FileNotFoundError(f"tidak ada *-incorrect.xlsx di {eval_dir}")
    inc = pd.read_excel(f_inc)
    inc.columns = [c.strip() for c in inc.columns]
    inc_tid = inc["text_id"].astype(str).tolist()
    inc_tok = inc["token"].astype(str).tolist()
    inc_true = inc["true_label"].astype(str).map(to_dash).tolist()
    inc_pred = inc["pred_label"].astype(str).map(to_dash).tolist()

    pred = gold["label"].tolist()
    tid = gold["text_id"].tolist()
    tok = gold["token"].tolist()
    lab = gold["label"].tolist()
    pi = 0
    for j in range(len(gold)):
        if pi < len(inc) and str(tid[j]) == inc_tid[pi] and tok[j] == inc_tok[pi] and lab[j] == inc_true[pi]:
            pred[j] = inc_pred[pi]
            pi += 1
    return pd.Series(pred, index=gold.index), {"file": f_inc.name, "n_inc": len(inc), "n_placed": pi}


def seqs_by_chunk(gold_lab: pd.Series, text_id: pd.Series, pred: pd.Series) -> tuple[list, list]:
    g = pd.DataFrame({"text_id": text_id.values, "lab": gold_lab.values, "pred": pred.values})
    ts, ps = [], []
    for _, sub in g.groupby("text_id", sort=False):
        ts.append(sub["lab"].tolist())
        ps.append(sub["pred"].tolist())
    return ts, ps


def per_label_f1(report: str) -> dict:
    out = {}
    for line in report.splitlines():
        p = line.split()
        if len(p) >= 5 and p[0] in LABELS:
            out[p[0]] = p[3]
    return out


def plot_confusion(gold_lab: pd.Series, pred: pd.Series, title: str, path: Path) -> None:
    yt = [ent_type(x) for x in gold_lab]
    yp = [ent_type(x) for x in pred]
    cm = confusion_matrix(yt, yp, labels=CONF_CLASSES)
    cm_row = cm.astype(float)
    rs = cm_row.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    cm_norm = cm_row / rs
    fig, ax = plt.subplots(figsize=(8.6, 7.0))
    im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(CONF_CLASSES))); ax.set_xticklabels(CONF_CLASSES, rotation=40, ha="right", fontsize=13)
    ax.set_yticks(range(len(CONF_CLASSES))); ax.set_yticklabels(CONF_CLASSES, fontsize=13)
    ax.set_xlabel("Prediksi", fontsize=14); ax.set_ylabel("Acuan (gold terkoreksi)", fontsize=14)
    ax.set_title(title, fontsize=15)
    for i in range(len(CONF_CLASSES)):
        for j in range(len(CONF_CLASSES)):
            c = "white" if cm_norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{cm[i, j]}", ha="center", va="center", color=c, fontsize=14)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Proporsi per baris (recall kelas)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONF_DIR.mkdir(parents=True, exist_ok=True)

    gold = pd.read_csv(TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["text_id"] = gold["text_id"].astype(str)
    gold["label"] = gold["label"].astype(str).map(to_dash)
    print(f"[OK] test.csv {len(gold):,} token / {gold['text_id'].nunique()} chunk")

    gold_new, ci = build_corrected_gold(gold)
    print(f"[OK] koreksi gold: {ci['n_changed']} token berubah "
          f"(placed {ci['n_placed']}/{ci['n_rows']} baris label baru)")

    rows = []
    for tag, ed in SCENARIOS.items():
        if not ed.is_dir():
            print(f"[SKIP] {tag}"); continue
        pred, pi = reconstruct_pred(ed, gold)
        # BEFORE (gold lama) vs AFTER (gold terkoreksi)
        ts_o, ps_o = seqs_by_chunk(gold["label"], gold["text_id"], pred)
        ts_n, ps_n = seqs_by_chunk(gold_new, gold["text_id"], pred)
        f1_old = f1_score(ts_o, ps_o)
        f1_new = f1_score(ts_n, ps_n)
        rep_new = seq_report(ts_n, ps_n, digits=4)
        pl = per_label_f1(rep_new)
        plot_confusion(gold_new, pred, f"{tag}", CONF_DIR / f"{tag.split()[0]}.png")
        print(f"{tag:32s} F1 {f1_old:.4f} -> {f1_new:.4f}  ({f1_new-f1_old:+.4f})")
        rows.append({"tag": tag, "f1_old": f1_old, "f1_new": f1_new,
                     "P": precision_score(ts_n, ps_n), "R": recall_score(ts_n, ps_n),
                     "pl": pl, "rep": rep_new, "pi": pi})

    rows_sorted = sorted(rows, key=lambda r: r["f1_new"], reverse=True)
    L = ["# Recompute F1 — Ground-Truth Test Terkoreksi (arahan Bu Dini 2026-07-10)\n",
         "> Dihasilkan `recompute_gt_corrected.py`. Entity-level seqeval, **tanpa menjalankan model**. "
         "Satu gold terkoreksi (166 token dari `label baru.xlsx`) dipakai semua skenario; "
         "prediksi tiap skenario direkonstruksi dari `*-incorrect.xlsx`-nya (beku). "
         f"test.csv = {len(gold):,} token / {gold['text_id'].nunique()} chunk.\n",
         "\n> ⚠️ **Caveat keadilan:** koreksi gold diturunkan hanya dari kesalahan skenario "
         "**augmentasi**, sehingga augmentasi paling diuntungkan. Wajib disebut jika angka masuk buku.\n",
         "\n## F1 entity-level: asli → terkoreksi (urut F1 terkoreksi)\n",
         "| Skenario | F1 lama | F1 terkoreksi | Δ | PERSON | LOCATION | EVENT | TIME |",
         "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows_sorted:
        pl = r["pl"]
        L.append(f"| {r['tag']} | {r['f1_old']:.4f} | **{r['f1_new']:.4f}** | {r['f1_new']-r['f1_old']:+.4f} | "
                 f"{pl.get('PERSON','-')} | {pl.get('LOCATION','-')} | {pl.get('EVENT','-')} | {pl.get('TIME','-')} |")
    best = rows_sorted[0]
    L.append(f"\n**Winner: `{best['tag']}` — F1 terkoreksi = {best['f1_new']:.4f}.**\n")
    L.append(f"\nKoreksi gold: **{ci['n_changed']} token** berubah (dari {ci['n_rows']} baris `label baru.xlsx`).\n")
    L.append("\nConfusion matrix per skenario (token-level, 5 kelas, gold terkoreksi): "
             "lihat `confusion/<skenario>.png`.\n")
    L.append("\n## Classification report per skenario (gold terkoreksi)\n")
    for r in rows_sorted:
        L.append(f"### {r['tag']}  (F1 {r['f1_new']:.4f})\n```\n{r['rep'].rstrip()}\n```\n")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[OK] -> {OUT_MD}")
    print(f"[OK] confusion PNG -> {CONF_DIR}")


if __name__ == "__main__":
    main()
