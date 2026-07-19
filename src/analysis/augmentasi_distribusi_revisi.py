#!/usr/bin/env python3
"""
augmentasi_distribusi_revisi.py — Chart distribusi kelas sebelum vs sesudah augmentasi,
dengan anotasi RASIO ketimpangan (revisi sidang Dosen-1 poin 6 & 7).

Angka dihitung dari data nyata yang melatih model:
  - PRE  : train.csv
  - POST : train_augmented_v2.csv   (mention replacement, target kelas minoritas)

Menegaskan (Dosen-1 #7): augmentasi MENGURANGI ketimpangan (PERSON:EVENT 17.4:1 -> 9.0:1),
BUKAN menyeimbangkan seluruh kelas. Kelas mayoritas PERSON ikut naik (efek samping: kalimat
target minoritas masih memuat entitas PERSON lain yang ikut terduplikasi).

Output: data/result/analysis/bab4_viz/augmentasi_distribusi_revisi.png
Jalankan: venv\\Scripts\\python src\\analysis\\augmentasi_distribusi_revisi.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRL = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
# File augmentasi FINAL yang benar-benar melatih model done_newest (mention replacement +
# sejumlah kecil paraphrase). BUKAN train_augmented_v2.csv (versi pra-final, mention saja).
AUG_FINAL = (ROOT / "data" / "result" / "manual_labelling" / "gold_review" /
             "training_bundle_corrected_gold_20260704" / "train_augmented_final" /
             "train_augmented_final.csv")
OUT = ROOT / "data" / "result" / "analysis" / "bab4_viz" / "augmentasi_distribusi_revisi.png"

TYPES = ["PERSON", "LOCATION", "TIME", "EVENT"]
C_PRE, C_POST = "#9e9e9e", "#2e8b57"


def counts(df: pd.DataFrame) -> dict:
    lab = df["label"].astype(str)
    c = {t: int(lab.str.contains(t).sum()) for t in TYPES}
    c["O"] = int((lab == "O").sum())
    return c


def main() -> None:
    pre = counts(pd.read_csv(SRL / "train.csv"))
    post = counts(pd.read_csv(AUG_FINAL))

    r_pre = pre["PERSON"] / pre["EVENT"]
    r_post = post["PERSON"] / post["EVENT"]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    x = np.arange(len(TYPES))
    w = 0.38
    b1 = ax.bar(x - w / 2, [pre[t] for t in TYPES], w, label="Sebelum augmentasi", color=C_PRE)
    b2 = ax.bar(x + w / 2, [post[t] for t in TYPES], w, label="Sesudah augmentasi", color=C_POST)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n(+{100*(post[t]-pre[t])/pre[t]:.0f}%)" for t in TYPES])
    ax.set_ylabel("Jumlah token entitas (B + I)")
    ax.set_title("Distribusi kelas entitas sebelum vs sesudah augmentasi\n"
                 "(mention replacement — target kelas minoritas EVENT & LOCATION)",
                 fontsize=11)
    for bars in (b1, b2):
        for r in bars:
            ax.annotate(f"{int(r.get_height()):,}".replace(",", "."),
                        (r.get_x() + r.get_width() / 2, r.get_height()),
                        ha="center", va="bottom", fontsize=8, xytext=(0, 1),
                        textcoords="offset points")
    ax.set_ylim(0, max(post.values()) * 1.12 if False else post["PERSON"] * 1.15)
    ax.legend(loc="upper right")

    # anotasi rasio ketimpangan PERSON:EVENT (di area kosong tengah, tak menutup batang)
    txt = (f"Rasio ketimpangan PERSON : EVENT\n"
           f"  sebelum  ≈ {r_pre:.1f} : 1\n"
           f"  sesudah  ≈ {r_post:.1f} : 1\n"
           f"→ ketimpangan BERKURANG, belum seimbang")
    ax.text(0.40, 0.82, txt, transform=ax.transAxes, va="top", ha="left", fontsize=9,
            bbox=dict(boxstyle="round", fc="#fff3cd", ec="#d0b000", alpha=0.95))
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    plt.close(fig)

    print(f"[OK] -> {OUT}")
    for t in TYPES:
        print(f"  {t:9s} {pre[t]:6d} -> {post[t]:6d}  (+{100*(post[t]-pre[t])/pre[t]:.0f}%)")
    print(f"  O         {pre['O']:6d} -> {post['O']:6d}")
    print(f"  Rasio PERSON:EVENT  {r_pre:.1f}:1 -> {r_post:.1f}:1")


if __name__ == "__main__":
    main()
