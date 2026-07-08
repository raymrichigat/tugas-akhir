#!/usr/bin/env python3
"""
visualize_done_newest_errors_detail.py — versi RINCI (mirror struktur `error_viz` lama)
untuk run baru `done_newest` (gold terkoreksi). Memakai ulang `collect()` dari
`visualize_done_newest_errors.py` (rekonstruksi prediksi TANPA model, no-GPU).

Output di data/result/analysis/error_analysis_done_newest/:
  per_skenario/<short>/confusion_matrix.png   — confusion 5x5 (count, log10 biru)
  per_skenario/<short>/error_per_kelas.png    — bar FN vs FP per kelas
  by_group/<sX>_confusion.png                 — grid confusion 1 grup
  by_group/<sX>_compare.png                   — panel 2x2 (total/FN/FP/FN-rate)

Grup (mengikuti error_viz lama):
  s1 Handle Imbalance : baseline, weighted-CE, SCL, JSCL, augment
  s2 Model Comparison : baseline, cahya, distilbert, cased, roberta
  s3 POS-tag Module   : baseline, POS-tag
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from visualize_done_newest_errors import collect  # noqa: E402

OUTROOT = Path(__file__).resolve().parents[3] / "data/result/analysis/error_analysis_done_newest"
PS_DIR = OUTROOT / "per_skenario"
BG_DIR = OUTROOT / "by_group"

# TYPES sesuai collect(); urutan tampil (O di depan, seperti error_viz lama)
SRC = ["PERSON", "LOCATION", "EVENT", "TIME", "O"]
DISP = ["O", "PERSON", "LOCATION", "EVENT", "TIME"]
PERM = [SRC.index(t) for t in DISP]
KELAS = ["PERSON", "LOCATION", "EVENT", "TIME"]
KCOL = {"PERSON": "#4C72B0", "LOCATION": "#55A868", "EVENT": "#C44E52", "TIME": "#8172B3"}

GROUPS = {
    "s1": ("S1 - Handle Imbalance", ["baseline", "weighted-CE", "SCL", "JSCL", "augment"]),
    "s2": ("S2 - Model Comparison", ["baseline", "cahya", "distilbert", "cased", "roberta"]),
    "s3": ("S3 - POS-tag Module", ["baseline", "POS-tag"]),
}


def fn_by_class(cm):
    o = SRC.index("O")
    return {c: int(cm[SRC.index(c), o]) for c in KELAS}


def fp_by_class(cm):
    o = SRC.index("O")
    return {c: int(cm[o, SRC.index(c)]) for c in KELAS}


def total_error(cm):
    return int(cm.sum() - np.trace(cm))


def support(cm):
    return {c: int(cm[SRC.index(c), :].sum()) for c in KELAS}


def draw_confusion(ax, cm, title):
    cmd = cm[np.ix_(PERM, PERM)]
    ax.imshow(np.log10(cmd + 1), cmap="Blues")
    ax.set_title(title)
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels(DISP, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(DISP, fontsize=8)
    vmax = np.log10(cmd + 1).max()
    for i in range(5):
        for j in range(5):
            v = int(cmd[i, j])
            ax.text(j, i, str(v), ha="center", va="center", fontsize=7,
                    color="white" if np.log10(v + 1) > 0.6 * vmax else "black")


def plot_per_skenario(rows_by_short):
    for short, r in rows_by_short.items():
        d = PS_DIR / short
        d.mkdir(parents=True, exist_ok=True)
        cm = r["cm"]

        # confusion
        fig, ax = plt.subplots(figsize=(5, 5))
        draw_confusion(ax, cm, f"{short}: confusion (log10)")
        ax.set_ylabel("Gold"); ax.set_xlabel("Prediksi")
        fig.tight_layout()
        fig.savefig(d / "confusion_matrix.png", dpi=150)
        plt.close(fig)

        # error per kelas (FN vs FP)
        fn = fn_by_class(cm); fp = fp_by_class(cm)
        fig, ax = plt.subplots(figsize=(7.5, 3.5))
        xs = np.arange(len(KELAS)); w = 0.38
        ax.bar(xs - w / 2, [fn[c] for c in KELAS], w, label="FN (terlewat)", color="#C44E52")
        ax.bar(xs + w / 2, [fp[c] for c in KELAS], w, label="FP (over-deteksi)", color="#DD8452")
        ax.set_xticks(xs); ax.set_xticklabels(KELAS)
        ax.set_ylabel("token")
        ax.set_title(f"{short}: error per kelas (total {total_error(cm)})")
        ax.legend()
        fig.tight_layout()
        fig.savefig(d / "error_per_kelas.png", dpi=150)
        plt.close(fig)


def plot_by_group(rows_by_short):
    BG_DIR.mkdir(parents=True, exist_ok=True)
    for sid, (title, shorts) in GROUPS.items():
        shorts = [s for s in shorts if s in rows_by_short]
        rs = [rows_by_short[s] for s in shorts]

        # ---- confusion grid ----
        n = len(rs)
        ncol = min(n, 3)
        nrow = int(np.ceil(n / ncol))
        fig, axes = plt.subplots(nrow, ncol, figsize=(5 * ncol, 4.6 * nrow), squeeze=False)
        for ax in axes.ravel():
            ax.axis("off")
        for r, ax in zip(rs, axes.ravel()):
            ax.axis("on")
            draw_confusion(ax, r["cm"], r["short"])
        fig.suptitle(title, fontsize=13)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(BG_DIR / f"{sid}_confusion.png", dpi=140)
        plt.close(fig)

        # ---- compare panel 2x2 ----
        fig, ax = plt.subplots(2, 2, figsize=(14, 9))
        xs = np.arange(n)
        labels = shorts

        # (0,0) total error
        tot = [total_error(r["cm"]) for r in rs]
        ax[0, 0].bar(xs, tot, color="#4C72B0")
        for i, t in enumerate(tot):
            ax[0, 0].text(i, t + max(tot) * 0.01, str(t), ha="center", va="bottom", fontsize=9)
        ax[0, 0].set_title("Total error")
        ax[0, 0].set_ylabel("total token error")
        ax[0, 0].set_xticks(xs); ax[0, 0].set_xticklabels(labels, rotation=30, ha="right")

        # (0,1) FN per kelas (stacked)
        bottoms = np.zeros(n)
        for c in KELAS:
            vals = np.array([fn_by_class(r["cm"])[c] for r in rs])
            ax[0, 1].bar(xs, vals, bottom=bottoms, label=c, color=KCOL[c])
            bottoms += vals
        ax[0, 1].set_title("FN per kelas (entitas terlewat)")
        ax[0, 1].set_ylabel("FN (token)"); ax[0, 1].set_xlabel("skenario")
        ax[0, 1].set_xticks(xs); ax[0, 1].set_xticklabels(labels, rotation=30, ha="right")

        # (1,0) FP per kelas (stacked)
        bottoms = np.zeros(n)
        for c in KELAS:
            vals = np.array([fp_by_class(r["cm"])[c] for r in rs])
            ax[1, 0].bar(xs, vals, bottom=bottoms, label=c, color=KCOL[c])
            bottoms += vals
        ax[1, 0].set_title("FP per kelas (over-deteksi)")
        ax[1, 0].set_ylabel("FP (token)"); ax[1, 0].set_xlabel("skenario")
        ax[1, 0].set_xticks(xs); ax[1, 0].set_xticklabels(labels, rotation=30, ha="right")

        # (1,1) FN-rate per kelas (%) grouped
        w = 0.2
        for k, c in enumerate(KELAS):
            rate = [100.0 * fn_by_class(r["cm"])[c] / max(support(r["cm"])[c], 1) for r in rs]
            ax[1, 1].bar(xs + (k - 1.5) * w, rate, w, label=c, color=KCOL[c])
        ax[1, 1].set_title("FN-rate per kelas (sensitif minoritas)")
        ax[1, 1].set_ylabel("% gold terlewat"); ax[1, 1].set_xlabel("skenario")
        ax[1, 1].set_xticks(xs); ax[1, 1].set_xticklabels(labels, rotation=30, ha="right")

        handles, lab = ax[0, 1].get_legend_handles_labels()
        fig.legend(handles, lab, loc="upper center", ncol=4, frameon=True)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(BG_DIR / f"{sid}_compare.png", dpi=140)
        plt.close(fig)


def main():
    rows = collect()
    rows_by_short = {r["short"]: r for r in rows}
    plot_per_skenario(rows_by_short)
    plot_by_group(rows_by_short)
    print(f"[OK] per_skenario ({len(rows_by_short)}) -> {PS_DIR}")
    print(f"[OK] by_group ({len(GROUPS)} grup) -> {BG_DIR}")


if __name__ == "__main__":
    main()
