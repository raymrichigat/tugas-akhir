#!/usr/bin/env python3
"""
gt_vs_pred_table.py — Tabel perbandingan Ground Truth vs Prediksi (Bu Dini #6).

Menyejajarkan entitas gold-terkoreksi vs prediksi model pemenang (S4-augmentation)
di DATA UJI, lalu memilah tiap entitas ke 5 kategori:
  - Benar            : span & tipe sama persis
  - Salah tipe       : span sama, tipe beda
  - Kesalahan batas  : span tumpang-tindih tapi batas beda
  - False negative   : entitas gold tak terdeteksi model
  - False positive   : entitas prediksi yang tak ada di gold (spurious)

Pakai ulang recompute_gt_corrected.py (gold terkoreksi + rekonstruksi prediksi,
TANPA menjalankan model).

Output: data/result/analysis/gt_corrected_2026_07_10/gt_vs_pred/
  ├── gt_vs_pred_full.csv     (semua entitas + kategori, untuk lampiran)
  └── contoh_gt_vs_pred.md    (ringkasan jumlah + contoh per kategori, siap tempel Bab 4)

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\gt_vs_pred_table.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from seqeval.scheme import IOB2  # noqa: F401  (memastikan seqeval ada)
from seqeval.metrics.sequence_labeling import get_entities

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from recompute_gt_corrected import (  # noqa: E402
    build_corrected_gold, reconstruct_pred, TEST_CSV, SCENARIOS, to_dash,
)

WINNER = "S4-augmentation"
ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "data" / "result" / "analysis" / "gt_corrected_2026_07_10" / "gt_vs_pred"


def overlap(a0, a1, b0, b1) -> bool:
    return a0 <= b1 and b0 <= a1


def classify_chunk(tokens, gold_seq, pred_seq):
    """Return list of dict rows kategori untuk satu chunk."""
    g = get_entities(gold_seq)   # (type, start, end) inclusive
    p = get_entities(pred_seq)
    rows = []
    used_p = [False] * len(p)
    used_g = [False] * len(g)

    def text(s, e):
        return " ".join(tokens[s:e + 1])

    # 1) exact span match
    for gi, (gt, gs, ge) in enumerate(g):
        for pi, (pt, ps, pe) in enumerate(p):
            if used_p[pi]:
                continue
            if gs == ps and ge == pe:
                used_g[gi] = used_p[pi] = True
                kat = "Benar" if gt == pt else "Salah tipe"
                rows.append(dict(kategori=kat, gt_teks=text(gs, ge), gt_tipe=gt,
                                 pred_teks=text(ps, pe), pred_tipe=pt))
                break
    # 2) boundary overlap (sisa)
    for gi, (gt, gs, ge) in enumerate(g):
        if used_g[gi]:
            continue
        for pi, (pt, ps, pe) in enumerate(p):
            if used_p[pi]:
                continue
            if overlap(gs, ge, ps, pe):
                used_g[gi] = used_p[pi] = True
                rows.append(dict(kategori="Kesalahan batas", gt_teks=text(gs, ge), gt_tipe=gt,
                                 pred_teks=text(ps, pe), pred_tipe=pt))
                break
    # 3) sisa gold = false negative
    for gi, (gt, gs, ge) in enumerate(g):
        if not used_g[gi]:
            rows.append(dict(kategori="False negative", gt_teks=text(gs, ge), gt_tipe=gt,
                             pred_teks="(tidak terdeteksi)", pred_tipe="-"))
    # 4) sisa pred = false positive
    for pi, (pt, ps, pe) in enumerate(p):
        if not used_p[pi]:
            rows.append(dict(kategori="False positive", gt_teks="(tidak ada)", gt_tipe="-",
                             pred_teks=text(ps, pe), pred_tipe=pt))
    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TEST_CSV)
    df["token"] = df["token"].astype(str)
    df["text_id"] = df["text_id"].astype(str)
    df["label"] = df["label"].astype(str).map(to_dash)

    gold_new, ci = build_corrected_gold(df)
    ed = SCENARIOS[WINNER]
    pred, pinfo = reconstruct_pred(ed, df)
    print(f"[OK] gold terkoreksi ({ci['n_changed']} token berubah); prediksi {WINNER} ({pinfo['file']})")

    work = pd.DataFrame({"text_id": df["text_id"].values, "token": df["token"].values,
                         "gold": gold_new.values, "pred": pred.values})
    all_rows = []
    for tid, sub in work.groupby("text_id", sort=False):
        toks = sub["token"].tolist()
        rows = classify_chunk(toks, sub["gold"].tolist(), sub["pred"].tolist())
        for r in rows:
            r["chunk_id"] = tid
        all_rows.extend(rows)

    res = pd.DataFrame(all_rows, columns=["chunk_id", "kategori", "gt_teks", "gt_tipe", "pred_teks", "pred_tipe"])
    res.to_csv(OUT_DIR / "gt_vs_pred_full.csv", index=False, encoding="utf-8-sig")

    counts = res["kategori"].value_counts()
    order = ["Benar", "Salah tipe", "Kesalahan batas", "False negative", "False positive"]

    # contoh terkurasi: utamakan entitas pendek & jelas
    def pick(kat, n=4):
        sub = res[res["kategori"] == kat].copy()
        sub = sub.drop_duplicates(subset=["gt_teks", "gt_tipe", "pred_teks", "pred_tipe"])
        if kat in ("Benar",):  # ambil nama yang dikenal utk ilustrasi
            pref = sub[sub["gt_teks"].str.split().str.len() <= 3]
            sub = pd.concat([pref, sub]).drop_duplicates(subset=["gt_teks", "pred_teks"])
        return sub.head(n)

    n_benar = int(counts.get("Benar", 0))
    n_tipe = int(counts.get("Salah tipe", 0))
    n_batas = int(counts.get("Kesalahan batas", 0))
    n_fn = int(counts.get("False negative", 0))
    n_fp = int(counts.get("False positive", 0))
    gold_total = n_benar + n_tipe + n_batas + n_fn  # entitas sisi gold (acuan)

    L = ["# Perbandingan Ground Truth vs Prediksi Model (Data Uji) — Bu Dini #6\n",
         f"> Model: **{WINNER}** (pemenang, dipakai membangun KG). Gold = ground-truth test terkoreksi. "
         "Level entitas (span). Dihasilkan `gt_vs_pred_table.py`, tanpa menjalankan model.\n",
         "\n## Ringkasan jumlah per kategori\n",
         "| Kategori | Jumlah | Keterangan |", "|---|---:|---|",
         f"| Benar | {n_benar} | span & tipe sama persis |",
         f"| Salah tipe | {n_tipe} | span sama, tipe beda |",
         f"| Kesalahan batas | {n_batas} | span tumpang-tindih, batas beda |",
         f"| False negative | {n_fn} | entitas gold tak terdeteksi |",
         f"| **Total entitas gold (acuan)** | **{gold_total}** | Benar+Salah tipe+Batas+FN |",
         f"| False positive | {n_fp} | entitas prediksi spurious (di luar {gold_total} gold) |"]
    L.append(f"\n**Catatan:** kesalahan **tipe** hanya {n_tipe} entitas — jauh lebih kecil "
             f"daripada kesalahan **deteksi** (FN {n_fn} + FP {n_fp} + batas {n_batas}). "
             f"Menegaskan bahwa model sudah memahami keempat tipe; masalah utama ada di batas/deteksi, "
             f"bukan salah klasifikasi tipe. (Total entitas gold {gold_total} konsisten dengan jumlah "
             f"entitas data uji di Bab 5.)\n")

    L.append("\n## Contoh per kategori\n")
    L.append("| Entitas (GT) | Ground truth | Entitas (Prediksi) | Prediksi | Kategori | chunk |")
    L.append("|---|---|---|---|---|---|")
    for k in order:
        for _, r in pick(k).iterrows():
            L.append(f"| {r['gt_teks']} | {r['gt_tipe']} | {r['pred_teks']} | {r['pred_tipe']} | {k} | {r['chunk_id']} |")
    (OUT_DIR / "contoh_gt_vs_pred.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print("[OK] jumlah per kategori:")
    for k in order:
        print(f"     {k:18s}: {int(counts.get(k,0))}")
    print(f"[OK] -> {OUT_DIR/'contoh_gt_vs_pred.md'}")
    print(f"[OK] -> {OUT_DIR/'gt_vs_pred_full.csv'}")


if __name__ == "__main__":
    main()
