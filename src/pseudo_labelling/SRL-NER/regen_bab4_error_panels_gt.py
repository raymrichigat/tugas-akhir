#!/usr/bin/env python3
"""
regen_bab4_error_panels_gt.py — Regenerasi 6 panel error Bab 4 (confusion grid +
compare grid per grup uji coba) memakai **ground-truth test terkoreksi**
(arahan Bu Dini 2026-07-10), TANPA menjalankan model.

Menggantikan versi lama `error_comparison_by_group.ipynb` yang masih terikat
`done_running` (benchmark grupB) + gold ASLI. Skrip ini memakai sumber
`done_newest` + gold terkoreksi (166 token) yang identik dengan
`recompute_gt_corrected.py` (F1 resmi tereproduksi PERSIS).

Output -> data/result/analysis/error_viz/by_group/
  s1_confusion.png  s1_compare.png   (Uji Coba 1: 5 skenario imbalance) → Gambar 4.4 / 4.5
  s2_confusion.png  s2_compare.png   (Uji Coba 2: 5 model)              → Gambar 4.9 / 4.10
  s3_confusion.png  s3_compare.png   (Uji Coba 3: baseline vs POS-tag)  → panel UC3

Angka konsisten dengan gt_corrected_2026_07_10/recompute_gt_corrected_results.md
dan error_breakdown_gt_corrected.md (total error, FP/FN per kelas).

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\regen_bab4_error_panels_gt.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Reuse logika resmi (gold terkoreksi + rekonstruksi prediksi beku)
from recompute_gt_corrected import (
    ROOT, TEST_CSV, LABELS,
    to_dash, ent_type, build_corrected_gold, reconstruct_pred, SCENARIOS,
)

OUT = ROOT / "data" / "result" / "analysis" / "error_viz" / "by_group"
COLORS = {"PERSON": "#4C72B0", "LOCATION": "#55A868", "EVENT": "#C44E52", "TIME": "#8172B3"}
ORDER = ["O"] + LABELS

# Grup uji coba -> (tag skenario di SCENARIOS, nama tampil pada sumbu)
GROUPS = {
    "s1": ("Uji Coba 1 — Penanganan Imbalance", [
        ("S1-baseline (indolem uncased)", "baseline"),
        ("S2-weighted-CE",                "weighted-CE"),
        ("S3a-SCL",                       "SCL"),
        ("S3b-JSCL",                      "JSCL"),
        ("S4-augmentation",               "augmentation"),
    ]),
    "s2": ("Uji Coba 2 — Perbandingan Model", [
        ("S1-baseline (indolem uncased)", "IndoBERT uncased"),
        ("B-cahya-bert-1.5G",             "cahya uncased"),
        ("B-distilbert",                  "DistilBERT"),
        ("B-indobert-cased (p1)",         "IndoBERT cased"),
        ("B-roberta (indo)",              "RoBERTa"),
    ]),
    "s3": ("Uji Coba 3 — Modul POS-tag", [
        ("S1-baseline (indolem uncased)", "baseline"),
        ("S5-POS-tag",                    "POS-tag"),
    ]),
}


def error_category(g_lbl: str, p_lbl: str) -> str:
    g, p = ent_type(g_lbl), ent_type(p_lbl)
    if g_lbl == p_lbl:
        return "BENAR"
    if g == "O" and p != "O":
        return "FP"
    if g != "O" and p == "O":
        return "FN"
    if g != "O" and p != "O" and g != p:
        return "MIS"
    return "BND"  # boundary B/I


def build_token_frames(gold: pd.DataFrame, gold_new: pd.Series) -> dict:
    """Per skenario -> DataFrame token-level (gtype/ptype/ecat) di gold TERKOREKSI."""
    frames = {}
    for tag, eval_dir in SCENARIOS.items():
        if not eval_dir.is_dir():
            print(f"[SKIP] {tag}")
            continue
        pred, _ = reconstruct_pred(eval_dir, gold)
        d = pd.DataFrame({
            "text_id": gold["text_id"].values,
            "gold": gold_new.values,
            "pred": pred.values,
        })
        d["gtype"] = [ent_type(x) for x in d["gold"]]
        d["ptype"] = [ent_type(x) for x in d["pred"]]
        d["ecat"] = [error_category(a, b) for a, b in zip(d["gold"], d["pred"])]
        frames[tag] = d
    return frames


def metrics_row(d: pd.DataFrame) -> dict:
    rec = {"total_error": int((d["ecat"] != "BENAR").sum())}
    sup = d[d["gtype"] != "O"].groupby("gtype").size()
    for k in LABELS:
        fnk = int(((d["ecat"] == "FN") & (d["gtype"] == k)).sum())
        rec[f"FN_{k}"] = fnk
        rec[f"FP_{k}"] = int(((d["ecat"] == "FP") & (d["ptype"] == k)).sum())
        rec[f"FNrate_{k}"] = round(fnk / sup.get(k, 1) * 100, 1)
    return rec


def plot_confusion(key: str, title: str, group: list, frames: dict) -> None:
    scns = [(t, nm) for t, nm in group if t in frames]
    ncol = min(3, len(scns))
    nrow = int(np.ceil(len(scns) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 4.2 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for ax in axes[len(scns):]:
        ax.axis("off")
    for ax, (tag, nm) in zip(axes, scns):
        d = frames[tag]
        cm = (pd.crosstab(d["gtype"], d["ptype"])
              .reindex(index=ORDER, columns=ORDER).fillna(0).astype(int))
        ax.imshow(np.log10(cm.values + 1), cmap="Blues")
        ax.set_xticks(range(len(ORDER))); ax.set_xticklabels(ORDER, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(ORDER))); ax.set_yticklabels(ORDER, fontsize=8)
        ax.set_xlabel("Prediksi", fontsize=8); ax.set_ylabel("Acuan", fontsize=8)
        ax.set_title(nm, fontsize=10)
        mx = np.log10(cm.values.max() + 1)
        for i in range(len(ORDER)):
            for j in range(len(ORDER)):
                v = cm.values[i, j]
                ax.text(j, i, f"{v}", ha="center", va="center", fontsize=6,
                        color="white" if np.log10(v + 1) > mx * 0.6 else "black")
    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    path = OUT / f"{key}_confusion.png"
    fig.savefig(path, bbox_inches="tight", dpi=130)
    plt.close(fig)
    print("  ->", path.name)


def plot_compare(key: str, title: str, group: list, frames: dict) -> None:
    scns = [(t, nm) for t, nm in group if t in frames]
    names = [nm for _, nm in scns]
    M = pd.DataFrame([metrics_row(frames[t]) for t, _ in scns], index=names)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    axes = axes.ravel()
    x = range(len(names))
    # (1) total error
    bars = axes[0].bar(x, M["total_error"], color="#4C72B0")
    axes[0].set_xticks(list(x)); axes[0].set_xticklabels(names, rotation=30, ha="right")
    axes[0].set_ylabel("total token error"); axes[0].set_title("Total error")
    for b, v in zip(bars, M["total_error"]):
        axes[0].text(b.get_x() + b.get_width() / 2, v, str(int(v)), ha="center", va="bottom", fontsize=8)
    # (2) FN per kelas (stacked) — entitas terlewat
    fn = M[[f"FN_{k}" for k in LABELS]]; fn.columns = LABELS
    fn.plot(kind="bar", stacked=True, ax=axes[1], color=[COLORS[k] for k in LABELS], legend=False)
    axes[1].set_xticklabels(names, rotation=30, ha="right")
    axes[1].set_ylabel("FN (token)"); axes[1].set_title("FN per kelas (entitas terlewat)")
    # (3) FP per kelas (stacked) — over-deteksi
    fp = M[[f"FP_{k}" for k in LABELS]]; fp.columns = LABELS
    fp.plot(kind="bar", stacked=True, ax=axes[2], color=[COLORS[k] for k in LABELS], legend=False)
    axes[2].set_xticklabels(names, rotation=30, ha="right")
    axes[2].set_ylabel("FP (token)"); axes[2].set_title("FP per kelas (over-deteksi)")
    # (4) FN-rate per kelas — sensitif minoritas
    fr = M[[f"FNrate_{k}" for k in LABELS]]; fr.columns = LABELS
    fr.plot(kind="bar", ax=axes[3], color=[COLORS[k] for k in LABELS], legend=False)
    axes[3].set_xticklabels(names, rotation=30, ha="right")
    axes[3].set_ylabel("% gold terlewat"); axes[3].set_title("FN-rate per kelas (sensitif minoritas)")

    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[k]) for k in LABELS]
    fig.legend(handles, LABELS, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle(title, fontsize=12, fontweight="bold", y=1.05)
    fig.tight_layout()
    path = OUT / f"{key}_compare.png"
    fig.savefig(path, bbox_inches="tight", dpi=130)
    plt.close(fig)
    print("  ->", path.name, "| total_error:", dict(M["total_error"].astype(int)))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gold = pd.read_csv(TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["text_id"] = gold["text_id"].astype(str)
    gold["label"] = gold["label"].astype(str).map(to_dash)
    gold_new, ci = build_corrected_gold(gold)
    print(f"[OK] test.csv {len(gold):,} token / {gold['text_id'].nunique()} chunk; "
          f"koreksi {ci['n_changed']} token")

    frames = build_token_frames(gold, gold_new)
    for key, (title, group) in GROUPS.items():
        print(f"[{key}] {title}")
        plot_confusion(key, title, group, frames)
        plot_compare(key, title, group, frames)
    print("[DONE] ->", OUT)


if __name__ == "__main__":
    main()
