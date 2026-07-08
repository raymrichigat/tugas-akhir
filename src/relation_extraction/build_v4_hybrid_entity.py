"""
build_v4_hybrid_entity.py
=========================
Bangun versi **HIBRIDA** entity-level untuk KG v4:
  - 844 chunk berlabel (train + test)  -> pakai GOLD (sirah_prelabelled.csv, confidence 1.0)
  - 250 chunk unlabelled               -> pakai PREDIKSI model v4 (S4-augmentation)

Motivasi (diskusi 2026-07-08): 844 chunk sudah punya ground-truth manual, jadi
untuk versi hibrida kita pakai gold di situ (lebih akurat dari prediksi ~95%),
dan hanya mengandalkan model NER untuk 250 chunk yang memang belum berlabel.

Bandingkan dengan versi SERAGAM (`inference/sirah_predicted_v4_entity.csv`) yang
memakai prediksi model untuk SEMUA 1094 chunk (KG murni produk NER).

Prasyarat: inference v4 sudah dijalankan + entity bersih sudah dibuat via
`build_v4_entity_from_token.py` → `inference/sirah_predicted_v4_entity.csv`.

Input:
  data/result/manual_labelling/sirah_prelabelled.csv                     (gold, 844 chunk)
  data/result/pseudo-labelling/SRL-NER/unlabelled.csv                    (daftar 250 chunk unlabelled)
  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v4_entity.csv  (prediksi v4, 1094 chunk)

Output:
  data/result/pseudo-labelling/SRL-NER/hibrida/sirah_predicted_v4_hybrid_entity.csv

Idempotent. Usage:
  venv\\Scripts\\python.exe src/relation_extraction/build_v4_hybrid_entity.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRL_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
GOLD_CSV = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
UNLABELLED_CSV = SRL_DIR / "unlabelled.csv"
PRED_CSV = SRL_DIR / "inference" / "v4" / "sirah_predicted_v4_entity.csv"
OUT_CSV = SRL_DIR / "hibrida" / "sirah_predicted_v4_hybrid_entity.csv"

ENTITY_SCHEMA = ["chunk_id", "halaman", "entity_text", "entity_label",
                 "start_char", "end_char", "confidence", "source"]


def _detect_id_col(df):
    for c in ("text_id", "chunk_id"):
        if c in df.columns:
            return c
    raise KeyError("Tidak menemukan kolom id chunk (text_id/chunk_id)")


def main():
    p = argparse.ArgumentParser(description="Build hybrid v4 entity CSV (gold 844 + pred 250)")
    p.add_argument("--gold", type=Path, default=GOLD_CSV)
    p.add_argument("--unlabelled", type=Path, default=UNLABELLED_CSV)
    p.add_argument("--pred", type=Path, default=PRED_CSV)
    p.add_argument("--output", type=Path, default=OUT_CSV)
    args = p.parse_args()

    print("=" * 60)
    print("BUILD v4 HYBRID ENTITY (gold 844 + prediksi model 250)")
    print("=" * 60)

    # --- 1) Daftar chunk unlabelled (yg dipakai prediksi model) ---
    print(f"\n[1/4] Daftar chunk unlabelled: {args.unlabelled}")
    df_unl = pd.read_csv(args.unlabelled, encoding="utf-8-sig")
    id_col = _detect_id_col(df_unl)
    unlabelled_ids = set(df_unl[id_col].astype(str).unique())
    print(f"  chunk unlabelled: {len(unlabelled_ids)}")

    # --- 2) GOLD entity untuk 844 chunk berlabel ---
    print(f"\n[2/4] Gold entity: {args.gold}")
    df_gold = pd.read_csv(args.gold, sep=";", encoding="utf-8-sig")
    df_gold = df_gold[df_gold["label"].notna() & (df_gold["label"].astype(str).str.strip() != "")]
    df_gold = df_gold[df_gold["entity_text"].notna() & (df_gold["entity_text"].astype(str).str.strip() != "")]
    # Buang chunk yang ternyata unlabelled (harusnya sudah disjoint, tapi jaga-jaga)
    df_gold = df_gold[~df_gold["chunk_id"].astype(str).isin(unlabelled_ids)]
    gold_rows = pd.DataFrame({
        "chunk_id": df_gold["chunk_id"].astype(str),
        "halaman": df_gold["halaman"].astype(str),
        "entity_text": df_gold["entity_text"].astype(str),
        "entity_label": df_gold["label"].astype(str),
        "start_char": df_gold["start_char"],
        "end_char": df_gold["end_char"],
        "confidence": 1.0,
        "source": "gold",
    })
    print(f"  entity gold      : {len(gold_rows)} (dari {gold_rows['chunk_id'].nunique()} chunk)")

    # --- 3) PREDIKSI model untuk 250 chunk unlabelled ---
    print(f"\n[3/4] Prediksi model v4: {args.pred}")
    df_pred = pd.read_csv(args.pred, sep=";", encoding="utf-8-sig")
    df_pred = df_pred[df_pred["chunk_id"].astype(str).isin(unlabelled_ids)].copy()
    pred_rows = pd.DataFrame({
        "chunk_id": df_pred["chunk_id"].astype(str),
        "halaman": df_pred["halaman"].astype(str),
        "entity_text": df_pred["entity_text"].astype(str),
        "entity_label": df_pred["entity_label"].astype(str),
        "start_char": df_pred["start_char"],
        "end_char": df_pred["end_char"],
        "confidence": df_pred["confidence"],
        "source": "pred",
    })
    print(f"  entity prediksi  : {len(pred_rows)} (dari {pred_rows['chunk_id'].nunique()} chunk)")

    # --- 4) Gabung + tulis ---
    print(f"\n[4/4] Gabung + tulis: {args.output}")
    df_out = pd.concat([gold_rows, pred_rows], ignore_index=True)[ENTITY_SCHEMA]
    n_chunk = df_out["chunk_id"].nunique()
    print(f"  total entity     : {len(df_out)} (dari {n_chunk} chunk)")
    print(f"  komposisi sumber :")
    for src, cnt in df_out["source"].value_counts().items():
        print(f"    {src:<6s}: {cnt} entity")
    print(f"  per-label        :")
    for lab, cnt in df_out["entity_label"].value_counts().items():
        print(f"    {lab:<10s}: {cnt}")

    if n_chunk != 1094:
        print(f"  [WARN] total chunk {n_chunk} != 1094 — cek overlap gold/unlabelled.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(args.output, sep=";", encoding="utf-8-sig", index=False)
    print(f"  -> {args.output}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print("\nCatatan: file ini drop-in compatible dgn build_v3_prelabelled_from_inference.py")
    print("  (kolom 'source' diabaikan downstream). Untuk rebuild KG hibrida:")
    print("  python src/relation_extraction/build_v3_prelabelled_from_inference.py \\")
    print("      --input " + str(args.output) + " \\")
    print("      --output data/result/manual_labelling/sirah_prelabelled_v4_hybrid.csv")


if __name__ == "__main__":
    main()
