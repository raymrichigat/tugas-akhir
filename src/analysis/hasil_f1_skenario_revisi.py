#!/usr/bin/env python3
"""
hasil_f1_skenario_revisi.py — Chart F1 per skenario KANONIK untuk revisi (Dosen-1 poin 8:
warna grafik harus konsisten dengan legenda).

Menggunakan **satu palet warna terdokumentasi** yang konsisten:
  - Grup A (penanganan imbalance) : biru   #3b6ea5
  - Grup P (POS-tag)              : oranye #e0843d
  - Grup B (model pra-latih lain) : hijau  #4c9f70
  - Skenario PEMENANG augmentation : diberi HATCH + label ⭐ (warna tetap biru Grup A,
    tidak diganti-ganti antar grafik) sehingga legenda selalu cocok dengan batang.

Angka = ground-truth uji TERKOREKSI (Bu Dini 2026-07-10), identik sumber
`data/result/analysis/gt_corrected_2026_07_10/recompute_gt_corrected_results.md`.

Output: data/result/analysis/bab4_viz/f1_skenario_semua_revisi.png
Jalankan: venv\\Scripts\\python src\\analysis\\hasil_f1_skenario_revisi.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "result" / "analysis" / "bab4_viz" / "f1_skenario_semua_revisi.png"

# palet konsisten per grup (terdokumentasi — dipakai sama di semua grafik hasil)
WARNA_GRUP = {"A": "#3b6ea5", "P": "#e0843d", "B": "#4c9f70"}
NAMA_GRUP = {"A": "Grup A — penanganan imbalance",
             "P": "Grup P — modul POS-tag",
             "B": "Grup B — model pra-latih lain"}

# (label, F1 entity-level terkoreksi, grup, is_winner)
DATA = [
    ("Baseline",     0.9536, "A", False),
    ("Weighted-CE",  0.9480, "A", False),
    ("SCL",          0.9546, "A", False),
    ("JSCL",         0.9451, "A", False),
    ("Augmentation", 0.9756, "A", True),
    ("POS-tag",      0.9547, "P", False),
    ("cahya\nuncased", 0.9286, "B", False),
    ("DistilBERT",   0.9353, "B", False),
    ("IndoBERT\ncased", 0.7774, "B", False),
    ("RoBERTa",      0.8069, "B", False),
]
BASELINE = 0.9536


def main() -> None:
    labels = [d[0] for d in DATA]
    vals = [d[1] for d in DATA]
    grup = [d[2] for d in DATA]
    win = [d[3] for d in DATA]

    fig, ax = plt.subplots(figsize=(11, 5.6))
    x = range(len(DATA))
    bars = ax.bar(x, vals, width=0.68,
                  color=[WARNA_GRUP[g] for g in grup],
                  edgecolor="black", linewidth=0.5)

    ax.axhline(BASELINE, ls="--", color="#555", lw=1)
    ax.text(len(DATA) - 0.5, BASELINE + 0.004, f"baseline {BASELINE:.4f}",
            ha="right", va="bottom", fontsize=8, color="#555")

    for i, (b, v, w) in enumerate(zip(bars, vals, win)):
        tag = f"{v:.4f}" + (" (menang)" if w else "")
        ax.annotate(tag, (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom",
                    fontsize=9, fontweight="bold" if w else "normal",
                    xytext=(0, 2), textcoords="offset points")

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0.72, 1.0)
    ax.set_ylabel("F1-score entity-level (seqeval, gold terkoreksi)")
    ax.set_title("Perbandingan F1 seluruh skenario (ground-truth uji terkoreksi)")
    ax.grid(axis="y", ls=":", alpha=0.5)

    legend_items = [Patch(facecolor=WARNA_GRUP[g], edgecolor="black", label=NAMA_GRUP[g])
                    for g in ["A", "P", "B"]]
    ax.legend(handles=legend_items, loc="lower left", frameon=True, fontsize=9)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    print(f"[OK] -> {OUT}")


if __name__ == "__main__":
    main()
