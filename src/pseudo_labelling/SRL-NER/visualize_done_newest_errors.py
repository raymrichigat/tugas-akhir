#!/usr/bin/env python3
"""
visualize_done_newest_errors.py — visualisasi hasil eval + error run baru `done_newest`,
dikelompokkan per grup skenario. Memakai ulang rekonstruksi prediksi (tanpa model) dari
`seqeval_done_newest.py`. No-GPU, tidak load model.

Menghasilkan 4 PNG di data/result/analysis/error_analysis_done_newest/viz/:
  1. f1_by_scenario.png       — F1 entity-level per skenario, warna per grup + garis baseline.
  2. perclass_f1.png          — F1 per kelas (PERSON/LOCATION/EVENT/TIME) per skenario.
  3. error_composition.png    — komposisi error token-level (FP/FN/Mis/Boundary) per skenario.
  4. confusion_panels.png     — panel confusion tipe (row-normalized) 10 skenario, tersusun per grup.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seqeval.metrics import classification_report as seq_report
from seqeval.metrics import f1_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from seqeval_done_newest import SCENARIOS, TEST_CSV, reconstruct, seqs_by_chunk, to_dash  # noqa: E402

OUTDIR = Path(__file__).resolve().parents[3] / "data/result/analysis/error_analysis_done_newest/viz"
OUTDIR.mkdir(parents=True, exist_ok=True)

# tag pendek + grup (selaras urutan SCENARIOS di seqeval_done_newest)
META = {
    "S1-baseline (indolem uncased)": ("baseline", "A"),
    "S2-weighted-CE":                ("weighted-CE", "A"),
    "S3a-SCL":                       ("SCL", "A"),
    "S3b-JSCL":                      ("JSCL", "A"),
    "S4-augmentation":               ("augment", "A"),
    "S5-POS-tag":                    ("POS-tag", "P"),
    "B-indobert-cased (p1)":         ("cased", "B"),
    "B-roberta (indo)":              ("roberta", "B"),
    "B-cahya-bert-1.5G":             ("cahya", "B"),
    "B-distilbert":                  ("distilbert", "B"),
}
GRUP_COLOR = {"A": "#4C72B0", "P": "#DD8452", "B": "#55A868"}
KELAS = ["PERSON", "LOCATION", "EVENT", "TIME"]
TYPES = ["PERSON", "LOCATION", "EVENT", "TIME", "O"]


def typ(lbl: str) -> str:
    lbl = str(lbl)
    if lbl in ("O", "nan", ""):
        return "O"
    return lbl.replace("B-", "").replace("I-", "").replace("B_", "").replace("I_", "")


def collect() -> list[dict]:
    gold = pd.read_csv(TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["label"] = gold["label"].astype(str).map(to_dash)
    gold["text_id"] = gold["text_id"].astype(str)
    gtype = gold["label"].map(typ).values

    rows = []
    for tag, ed in SCENARIOS.items():
        if not ed.is_dir():
            continue
        pred, _ = reconstruct(ed, gold)
        pr = pred.map(to_dash)
        ptype = pr.map(typ).values

        ts, ps = seqs_by_chunk(gold, pr)
        f1 = f1_score(ts, ps)
        rep = seq_report(ts, ps, digits=4, output_dict=True)
        perclass = {c: rep.get(c, {}).get("f1-score", np.nan) for c in KELAS}

        # error token-level composition
        gt, pt = gtype, ptype
        fp = int(((gt == "O") & (pt != "O")).sum())
        fn = int(((gt != "O") & (pt == "O")).sum())
        mis = int(((gt != "O") & (pt != "O") & (gt != pt)).sum())
        # boundary: tipe sama tapi label BIO beda (butuh label mentah)
        bnd = int(((gold["label"].map(typ).values == pr.map(typ).values)
                   & (gold["label"].values != pr.values)
                   & (gt != "O")).sum())

        # confusion tipe (row-normalized recall)
        cm = np.zeros((5, 5), dtype=float)
        idx = {t: i for i, t in enumerate(TYPES)}
        for a, b in zip(gt, pt):
            cm[idx[a], idx[b]] += 1
        cmn = cm / np.clip(cm.sum(axis=1, keepdims=True), 1, None)

        short, grup = META[tag]
        rows.append({"tag": tag, "short": short, "grup": grup, "f1": f1,
                     "perclass": perclass, "fp": fp, "fn": fn, "mis": mis, "bnd": bnd,
                     "cm": cm, "cmn": cmn})
    return rows


def plot_f1(rows):
    fig, ax = plt.subplots(figsize=(11, 5))
    xs = np.arange(len(rows))
    vals = [r["f1"] for r in rows]
    cols = [GRUP_COLOR[r["grup"]] for r in rows]
    bars = ax.bar(xs, vals, color=cols, edgecolor="black", linewidth=0.4)
    base = next(r["f1"] for r in rows if r["short"] == "baseline")
    ax.axhline(base, ls="--", color="gray", lw=1)
    ax.text(len(rows) - 0.5, base + 0.003, f"baseline {base:.4f}", ha="right", va="bottom",
            color="gray", fontsize=8)
    winner = max(rows, key=lambda r: r["f1"])
    for r, b in zip(rows, bars):
        ax.text(b.get_x() + b.get_width() / 2, r["f1"] + 0.004, f"{r['f1']:.3f}",
                ha="center", va="bottom", fontsize=8,
                fontweight="bold" if r is winner else "normal")
    ax.set_xticks(xs)
    ax.set_xticklabels([r["short"] for r in rows], rotation=30, ha="right")
    ax.set_ylabel("F1 entity-level (seqeval)")
    ax.set_ylim(0.72, 1.0)
    ax.set_title("F1 entity-level per skenario (run baru `done_newest`)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=GRUP_COLOR[g]) for g in ["A", "P", "B"]]
    ax.legend(handles, ["Grup A (imbalance)", "Grup P (POS-tag)", "Grup B (model lain)"],
              loc="lower left", fontsize=8)
    ax.grid(axis="y", ls=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUTDIR / "f1_by_scenario.png", dpi=150)
    plt.close(fig)


def plot_perclass(rows):
    fig, ax = plt.subplots(figsize=(12, 5.5))
    n = len(rows)
    w = 0.2
    xs = np.arange(n)
    palette = {"PERSON": "#4C72B0", "LOCATION": "#55A868", "EVENT": "#C44E52", "TIME": "#8172B3"}
    for k, c in enumerate(KELAS):
        vals = [r["perclass"][c] for r in rows]
        ax.bar(xs + (k - 1.5) * w, vals, w, label=c, color=palette[c], edgecolor="black", linewidth=0.3)
    ax.set_xticks(xs)
    ax.set_xticklabels([r["short"] for r in rows], rotation=30, ha="right")
    ax.set_ylabel("F1 per kelas (seqeval)")
    ax.set_ylim(0.4, 1.0)
    ax.set_title("F1 per kelas entitas per skenario — sorotan kelas minoritas EVENT/TIME")
    ax.legend(ncol=4, fontsize=9, loc="lower left")
    ax.grid(axis="y", ls=":", alpha=0.4)
    # garis pemisah grup
    for i in range(1, n):
        if rows[i]["grup"] != rows[i - 1]["grup"]:
            ax.axvline(i - 0.5, color="gray", ls="--", lw=0.8, alpha=0.6)
    fig.tight_layout()
    fig.savefig(OUTDIR / "perclass_f1.png", dpi=150)
    plt.close(fig)


def plot_composition(rows):
    fig, ax = plt.subplots(figsize=(11, 5))
    xs = np.arange(len(rows))
    fp = np.array([r["fp"] for r in rows])
    fn = np.array([r["fn"] for r in rows])
    mis = np.array([r["mis"] for r in rows])
    bnd = np.array([r["bnd"] for r in rows])
    ax.bar(xs, fp, label="FP (over-deteksi)", color="#DD8452")
    ax.bar(xs, fn, bottom=fp, label="FN (terlewat)", color="#4C72B0")
    ax.bar(xs, mis, bottom=fp + fn, label="Misklasifikasi tipe", color="#C44E52")
    ax.bar(xs, bnd, bottom=fp + fn + mis, label="Boundary (B/I)", color="#8172B3")
    for i, tot in enumerate(fp + fn + mis + bnd):
        ax.text(i, tot + 5, str(int(tot)), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xs)
    ax.set_xticklabels([r["short"] for r in rows], rotation=30, ha="right")
    ax.set_ylabel("Jumlah token error")
    ax.set_title("Komposisi error token-level per skenario (FP mendominasi; mis-tipe minim)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", ls=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUTDIR / "error_composition.png", dpi=150)
    plt.close(fig)


def plot_confusion_panels(rows):
    fig, axes = plt.subplots(2, 5, figsize=(20, 9))
    fig.subplots_adjust(wspace=0.55, hspace=0.5, left=0.05, right=0.9, top=0.9, bottom=0.1)
    for r, ax in zip(rows, axes.ravel()):
        cmn = r["cmn"]
        im = ax.imshow(cmn, cmap="Oranges", vmin=0, vmax=1)
        ax.set_title(f"{r['short']} (G{r['grup']})\nF1={r['f1']:.3f}", fontsize=9)
        ax.set_xticks(range(5)); ax.set_yticks(range(5))
        ax.set_xticklabels(TYPES, rotation=90, fontsize=7)
        ax.set_yticklabels(TYPES, fontsize=7)
        for a in range(5):
            for b in range(5):
                v = cmn[a, b]
                if v >= 0.005:
                    ax.text(b, a, f"{v:.2f}", ha="center", va="center", fontsize=6,
                            color="white" if v > 0.6 else "black")
        if ax in axes[:, 0]:
            ax.set_ylabel("gold", fontsize=8)
        if ax in axes[1, :]:
            ax.set_xlabel("prediksi", fontsize=8)
    fig.suptitle("Confusion tipe (row-normalized / recall) per skenario — diagonal tinggi = tipe benar; "
                 "cased EVENT recall turun (0.75), sisa error cased/roberta didominasi precision (lihat komposisi FP)",
                 fontsize=12)
    cax = fig.add_axes([0.92, 0.25, 0.012, 0.5])
    fig.colorbar(im, cax=cax, label="proporsi (per baris gold)")
    fig.savefig(OUTDIR / "confusion_panels.png", dpi=140)
    plt.close(fig)


def main():
    rows = collect()
    plot_f1(rows)
    plot_perclass(rows)
    plot_composition(rows)
    plot_confusion_panels(rows)
    print(f"[OK] 4 PNG -> {OUTDIR}")
    for f in sorted(OUTDIR.glob("*.png")):
        print("  -", f.name)


if __name__ == "__main__":
    main()
