#!/usr/bin/env python3
"""
error_breakdown_gt_corrected.py — Rincian error token-level (FP/FN/misklasifikasi-tipe/
boundary B-I) SEMUA skenario `done_newest` pada **ground-truth test terkoreksi** (Bu Dini
2026-07-10). Melengkapi `recompute_gt_corrected.py` (yang keluarkan F1/confusion).

Kategori (per token, gold_corrected vs pred, keduanya BIO dash):
  - FP  (over-deteksi) : gold == O  & pred != O
  - FN  (terlewat)     : gold != O  & pred == O
  - MIS (salah tipe)   : gold != O  & pred != O  & tipe(gold) != tipe(pred)
  - BND (batas B/I)    : gold != O  & pred != O  & tipe sama & gold != pred
Juga FN/FP per kelas (untuk panel perbandingan Bab 4).

Reuse fungsi rekonstruksi & koreksi gold dari recompute_gt_corrected.py (impor).

Output: data/result/analysis/gt_corrected_2026_07_10/error_breakdown_gt_corrected.md
Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\error_breakdown_gt_corrected.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rgc", HERE / "recompute_gt_corrected.py")
rgc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rgc)

OUT_MD = rgc.OUT_DIR / "error_breakdown_gt_corrected.md"
ENT = ["PERSON", "LOCATION", "EVENT", "TIME"]


def breakdown(gold: pd.Series, pred: pd.Series) -> dict:
    fp = fn = mis = bnd = 0
    fn_c = {e: 0 for e in ENT}
    fp_c = {e: 0 for e in ENT}
    for g, p in zip(gold, pred):
        if g == p:
            continue
        gt, pt = rgc.ent_type(g), rgc.ent_type(p)
        if g == "O":                      # gold O, pred entitas -> FP
            fp += 1; fp_c[pt] += 1
        elif p == "O":                    # gold entitas, pred O -> FN
            fn += 1; fn_c[gt] += 1
        elif gt != pt:                    # tipe beda -> misclass
            mis += 1
        else:                             # tipe sama, B/I beda -> boundary
            bnd += 1
    tot = fp + fn + mis + bnd
    return {"total": tot, "FP": fp, "FN": fn, "MIS": mis, "BND": bnd,
            "fn_c": fn_c, "fp_c": fp_c}


def main() -> None:
    gold = pd.read_csv(rgc.TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["text_id"] = gold["text_id"].astype(str)
    gold["label"] = gold["label"].astype(str).map(rgc.to_dash)
    gold_new, ci = rgc.build_corrected_gold(gold)
    print(f"[OK] gold terkoreksi: {ci['n_changed']} token berubah")

    rows = []
    for tag, ed in rgc.SCENARIOS.items():
        if not ed.is_dir():
            continue
        pred, _ = rgc.reconstruct_pred(ed, gold)
        b = breakdown(gold_new, pred)
        rows.append((tag, b))
        print(f"{tag:32s} total={b['total']:4d} FP={b['FP']:3d} FN={b['FN']:3d} "
              f"MIS={b['MIS']:2d} BND={b['BND']:3d}")

    def pct(n, t):
        return f"{n} ({round(100*n/t)}%)" if t else f"{n} (0%)"

    L = ["# Rincian Error Token-level — Gold Terkoreksi (Bu Dini 2026-07-10)\n",
         "> Dihasilkan `error_breakdown_gt_corrected.py`. Kategori: FP=over-deteksi (O→entitas), "
         "FN=terlewat (entitas→O), MIS=salah tipe, BND=batas B/I. Gold terkoreksi (166 token).\n",
         "\n## Ringkasan per skenario\n",
         "| Skenario | Total error | FP (over) | FN (terlewat) | Misklasifikasi | Boundary B/I |",
         "|---|---:|---:|---:|---:|---:|"]
    for tag, b in rows:
        L.append(f"| {tag} | {b['total']} | {pct(b['FP'],b['total'])} | {pct(b['FN'],b['total'])} | "
                 f"{pct(b['MIS'],b['total'])} | {pct(b['BND'],b['total'])} |")

    L.append("\n## FN per kelas\n")
    L.append("| Skenario | " + " | ".join(ENT) + " |")
    L.append("|---|" + "---:|" * len(ENT))
    for tag, b in rows:
        L.append(f"| {tag} | " + " | ".join(str(b['fn_c'][e]) for e in ENT) + " |")

    L.append("\n## FP per kelas\n")
    L.append("| Skenario | " + " | ".join(ENT) + " |")
    L.append("|---|" + "---:|" * len(ENT))
    for tag, b in rows:
        L.append(f"| {tag} | " + " | ".join(str(b['fp_c'][e]) for e in ENT) + " |")

    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[OK] -> {OUT_MD}")


if __name__ == "__main__":
    main()
