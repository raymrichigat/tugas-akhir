#!/usr/bin/env python3
"""
confusion_dosen_revisi.py — Confusion matrix DUA LEVEL untuk revisi sidang (Dosen-1 poin 4).

Dosen minta confusion matrix dibedakan level-nya secara tegas:
  (a) ENTITY-LEVEL (span)  → 4 tipe entitas (PERSON/LOCATION/EVENT/TIME) + margin
      deteksi (TAK TERDETEKSI = FN span, SPURIOUS = FP span). Untuk Bab 4.
  (b) TOKEN-LEVEL BIO       → 9 kelas (B-/I- tiap entitas + O). Untuk lampiran.
      "bukan sekadar 4 kelas".

Sumber angka = IDENTIK `recompute_gt_corrected.py` (gold terkoreksi 2026-07-10, tanpa
menjalankan model). Fungsi koreksi gold & rekonstruksi prediksi di-reuse dari modul itu.

Entity-level span confusion (exact-boundary match):
  - gold span (s,e,tG) & pred span (s,e,tP) dengan batas SAMA  -> sel (tG, tP)
  - gold span tanpa pasangan batas di pred                     -> sel (tG, 'TAK TERDETEKSI')  [FN]
  - pred span tanpa pasangan batas di gold                     -> sel ('SPURIOUS', tP)          [FP]
  Diagonal 4x4 = benar; off-diagonal 4x4 = SALAH TIPE; margin = SALAH DETEKSI.

Output:
  data/result/analysis/gt_corrected_2026_07_10/confusion_revisi/
    ├── entity_level/<skenario>.png      (span, 4 tipe + margin deteksi)
    ├── bio_token/<skenario>.png         (token BIO, 9 kelas)
    └── confusion_revisi_summary.md      (ringkasan + interpretasi winner)

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\confusion_dosen_revisi.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seqeval.metrics.sequence_labeling import get_entities
from sklearn.metrics import confusion_matrix

# reuse logika resmi gold-terkoreksi + rekonstruksi prediksi
from recompute_gt_corrected import (
    SCENARIOS, TEST_CSV, LABELS,
    to_dash, build_corrected_gold, reconstruct_pred, seqs_by_chunk,
)

OUT_DIR = TEST_CSV.parents[4] / "data" / "result" / "analysis" / "gt_corrected_2026_07_10" / "confusion_revisi"
ENT_DIR = OUT_DIR / "entity_level"
BIO_DIR = OUT_DIR / "bio_token"
SUMMARY = OUT_DIR / "confusion_revisi_summary.md"

WINNER = "S4-augmentation"

BIO_CLASSES = ["B-PERSON", "I-PERSON", "B-LOCATION", "I-LOCATION",
               "B-EVENT", "I-EVENT", "B-TIME", "I-TIME", "O"]
# entity-level: baris = gold (+ SPURIOUS/FP), kolom = pred (+ TAK TERDETEKSI/FN)
ENT_ROWS = LABELS + ["SPURIOUS (FP)"]
ENT_COLS = LABELS + ["TAK TERDETEKSI (FN)"]


def entity_confusion(ts: list[list[str]], ps: list[list[str]]) -> np.ndarray:
    """Confusion span-level exact-boundary. Return matrix (len ENT_ROWS x len ENT_COLS)."""
    ri = {t: i for i, t in enumerate(LABELS)}
    ci = {t: i for i, t in enumerate(LABELS)}
    SP = len(LABELS)      # baris SPURIOUS
    MISS = len(LABELS)    # kolom TAK TERDETEKSI
    M = np.zeros((len(ENT_ROWS), len(ENT_COLS)), dtype=int)
    for gseq, pseq in zip(ts, ps):
        gold = {(s, e): t for t, s, e in get_entities(gseq)}
        pred = {(s, e): t for t, s, e in get_entities(pseq)}
        for (s, e), tg in gold.items():
            if (s, e) in pred:
                M[ri[tg], ci[pred[(s, e)]]] += 1     # batas cocok -> (gold, pred)
            else:
                M[ri[tg], MISS] += 1                  # gold tak berpasangan -> FN
        for (s, e), tp in pred.items():
            if (s, e) not in gold:
                M[SP, ci[tp]] += 1                    # pred tak berpasangan -> FP
    return M


def _annot_grid(ax, M, rows, cols, title, num_fs=15, tick_fs=13, label_fs=13, title_fs=15):
    mx = M.max() if M.max() > 0 else 1
    ax.imshow(M, cmap="Blues", vmin=0, vmax=mx)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=40, ha="right", fontsize=tick_fs)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=tick_fs)
    ax.set_xlabel("Prediksi model", fontsize=label_fs); ax.set_ylabel("Acuan (gold terkoreksi)", fontsize=label_fs)
    ax.set_title(title, fontsize=title_fs)
    for i in range(len(rows)):
        for j in range(len(cols)):
            v = M[i, j]
            c = "white" if v > 0.5 * mx else ("#999" if v == 0 else "black")
            ax.text(j, i, f"{v}", ha="center", va="center", color=c, fontsize=num_fs)


def plot_entity(M: np.ndarray, title: str, path: Path,
                figsize=(8.4, 7.0), num_fs=15, tick_fs=12.5) -> None:
    fig, ax = plt.subplots(figsize=figsize)
    _annot_grid(ax, M, ENT_ROWS, ENT_COLS, title, num_fs=num_fs, tick_fs=tick_fs)
    # garis pemisah blok inti 4x4 vs margin deteksi
    ax.axhline(len(LABELS) - 0.5, color="crimson", lw=1.6, ls="--")
    ax.axvline(len(LABELS) - 0.5, color="crimson", lw=1.6, ls="--")
    fig.tight_layout(); fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def plot_bio(ts: list[list[str]], ps: list[list[str]], title: str, path: Path) -> None:
    yt = [x for seq in ts for x in seq]
    yp = [x for seq in ps for x in seq]
    cm = confusion_matrix(yt, yp, labels=BIO_CLASSES)
    cm_norm = cm.astype(float)
    rs = cm_norm.sum(axis=1, keepdims=True); rs[rs == 0] = 1
    cm_norm /= rs
    # 9 kelas padat -> perbesar + orientasi lega (Bu Ratih #8)
    fig, ax = plt.subplots(figsize=(11.0, 9.2))
    ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(BIO_CLASSES))); ax.set_xticklabels(BIO_CLASSES, rotation=40, ha="right", fontsize=12)
    ax.set_yticks(range(len(BIO_CLASSES))); ax.set_yticklabels(BIO_CLASSES, fontsize=12)
    ax.set_xlabel("Prediksi model", fontsize=13); ax.set_ylabel("Acuan (gold terkoreksi)", fontsize=13)
    ax.set_title(title, fontsize=14)
    for i in range(len(BIO_CLASSES)):
        for j in range(len(BIO_CLASSES)):
            v = cm[i, j]
            if v == 0:
                continue
            c = "white" if cm_norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{v}", ha="center", va="center", color=c, fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def interpret(M: np.ndarray) -> dict:
    core = M[:len(LABELS), :len(LABELS)]
    diag = int(np.trace(core))
    type_err = int(core.sum() - diag)                       # salah tipe (off-diagonal 4x4)
    fn = int(M[:len(LABELS), len(LABELS)].sum())            # tak terdeteksi
    fp = int(M[len(LABELS), :len(LABELS)].sum())            # spurious
    return {"benar": diag, "salah_tipe": type_err, "fn": fn, "fp": fp,
            "det_err": fn + fp, "total_gold": diag + type_err + fn}


def main() -> None:
    for d in (ENT_DIR, BIO_DIR):
        d.mkdir(parents=True, exist_ok=True)

    gold = pd.read_csv(TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["text_id"] = gold["text_id"].astype(str)
    gold["label"] = gold["label"].astype(str).map(to_dash)
    gold_new, ci = build_corrected_gold(gold)
    print(f"[OK] gold terkoreksi: {ci['n_changed']} token berubah")

    summ = []
    winner_M = None
    for tag, ed in SCENARIOS.items():
        if not ed.is_dir():
            continue
        pred, _ = reconstruct_pred(ed, gold)
        ts, ps = seqs_by_chunk(gold_new, gold["text_id"], pred)
        M = entity_confusion(ts, ps)
        short = tag.split()[0]
        plot_entity(M, f"Entity-level (span) — {tag}", ENT_DIR / f"{short}.png")
        plot_bio(ts, ps, f"Token-level BIO (9 kelas) — {tag}", BIO_DIR / f"{short}.png")
        it = interpret(M)
        summ.append({"tag": tag, **it})
        if tag == WINNER:
            winner_M = M
        print(f"{tag:32s} benar {it['benar']:4d} | salah-tipe {it['salah_tipe']:3d} | "
              f"FN {it['fn']:3d} | FP {it['fp']:3d}")

    # Gambar UTAMA Bab 4 = skenario pemenang, entity-level, ekstra besar & jelas
    if winner_M is not None:
        plot_entity(winner_M, f"Confusion Matrix Entity-level (4 tipe) — {WINNER}",
                    ENT_DIR / "_BAB4_UTAMA.png",
                    figsize=(9.6, 8.0), num_fs=18, tick_fs=14)
        print(f"[OK] gambar utama Bab 4 -> {ENT_DIR / '_BAB4_UTAMA.png'}")

    summ.sort(key=lambda r: r["benar"], reverse=True)
    w = next((r for r in summ if r["tag"] == WINNER), summ[0])
    L = [
        "# Confusion Matrix Dua Level — Revisi Sidang (Dosen-1 poin 4)\n",
        "> Dibuat `confusion_dosen_revisi.py`. Angka = gold terkoreksi 2026-07-10, tanpa "
        "menjalankan model (reuse `recompute_gt_corrected.py`). **Dua level dibedakan tegas:**\n",
        "\n- **Entity-level (span, Bab 4):** 4 tipe entitas + margin deteksi. Blok inti 4×4 = "
        "kecocokan tipe (diagonal benar, off-diagonal SALAH TIPE). Kolom *TAK TERDETEKSI* = span "
        "gold yang tak diprediksi (FN). Baris *SPURIOUS* = span pred yang tak ada di gold (FP). "
        "File: `entity_level/<skenario>.png`.",
        "- **Token-level BIO (lampiran):** 9 kelas `B-`/`I-` tiap entitas + `O` — memperlihatkan "
        "bahwa evaluasi token BIO **bukan 4 kelas**. File: `bio_token/<skenario>.png`.\n",
        "\n## Ringkasan entity-level (urut jumlah span benar)\n",
        "| Skenario | Span benar | Salah tipe | Tak terdeteksi (FN) | Spurious (FP) | Total error deteksi |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in summ:
        star = " (pemenang)" if r["tag"] == WINNER else ""
        L.append(f"| {r['tag']}{star} | {r['benar']} | {r['salah_tipe']} | {r['fn']} | "
                 f"{r['fp']} | {r['det_err']} |")
    L.append(
        f"\n## Interpretasi (skenario pemenang `{WINNER}`)\n\n"
        f"Dari **{w['total_gold']}** entitas acuan: **{w['benar']} benar**, hanya "
        f"**{w['salah_tipe']} salah tipe** (antar-kelas), **{w['fn']} tak terdeteksi**, "
        f"**{w['fp']} spurious**. **Kesimpulan yang bisa ditulis di Bab 4:** kesalahan model "
        f"**didominasi deteksi (FN+FP = {w['det_err']}), bukan kekeliruan tipe entitas "
        f"({w['salah_tipe']})** — model sudah memahami perbedaan 4 tipe; sisa kesalahan ada di "
        f"batas span / entitas yang terlewat, konsisten dengan temuan few-shot pada kelas minoritas.\n"
    )
    SUMMARY.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[OK] -> {SUMMARY}")
    print(f"[OK] entity-level PNG -> {ENT_DIR}")
    print(f"[OK] BIO token PNG    -> {BIO_DIR}")


if __name__ == "__main__":
    main()
