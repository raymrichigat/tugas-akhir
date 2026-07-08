"""
build_v3_prelabelled_from_inference.py
========================================
Convert hasil inference NER S3.2 winner ke format `sirah_prelabelled.csv`,
supaya bisa langsung di-feed ke `relation_extraction.py` untuk regenerate
Knowledge Graph v3.

Background (2026-05-28):
Inference final S3.2 (model winner, F1 entity 0.9537) menghasilkan
`sirah_predicted_v3_entity.csv` dengan format minimal:
  chunk_id, halaman, entity_text, entity_label, start_char, end_char, confidence

Tapi `relation_extraction.py` butuh schema lebih lengkap (mirror format
manual labelling):
  chunk_id, doc_id, chunk_index, judul_bab, judul_sub_bab, halaman,
  teks_chunk, entity_text, label, notes, start_char, end_char

Script ini melakukan:
  1. Load entity prediction (sirah_predicted_v3_entity.csv)
  2. Capitalize entity_text (model output lowercase, schema downstream Title Case)
  3. Filter confidence >= MIN_CONFIDENCE (default 0.7) untuk drop noise
  4. Join dengan sirah_chunks_final.csv untuk dapat doc_id, judul_bab, teks_chunk
  5. Save ke sirah_prelabelled_v3.csv

Output:
  data/result/manual_labelling/sirah_prelabelled_v3.csv

Usage:
  python src/relation_extraction/build_v3_prelabelled_from_inference.py
  python src/relation_extraction/build_v3_prelabelled_from_inference.py --min-confidence 0.8
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INFERENCE_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "inference" / "sirah_predicted_v3_entity.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
OUT_CSV = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled_v3.csv"

DEFAULT_MIN_CONFIDENCE = 0.7


def main():
    p = argparse.ArgumentParser(description="Convert NER inference -> sirah_prelabelled_v3 schema")
    p.add_argument("--min-confidence", type=float, default=DEFAULT_MIN_CONFIDENCE,
                   help=f"Drop entities below this confidence (default {DEFAULT_MIN_CONFIDENCE})")
    p.add_argument("--input", type=Path, default=INFERENCE_CSV)
    p.add_argument("--chunks", type=Path, default=CHUNKS_CSV)
    p.add_argument("--output", type=Path, default=OUT_CSV)
    args = p.parse_args()

    print("=" * 60)
    print("BUILD v3 PRELABELLED FROM INFERENCE")
    print("=" * 60)

    print(f"\n[1/5] Load entity prediction: {args.input}")
    df_ent = pd.read_csv(args.input, sep=";", encoding="utf-8-sig")
    print(f"  total entities    : {len(df_ent)}")
    print(f"  unique chunks     : {df_ent['chunk_id'].nunique()}")
    print(f"  label distribution:")
    for lab, cnt in df_ent["entity_label"].value_counts().items():
        print(f"    {lab:<10s}: {cnt}")

    print(f"\n[2/5] Filter confidence >= {args.min_confidence}")
    n_before = len(df_ent)
    df_ent = df_ent[df_ent["confidence"] >= args.min_confidence].copy()
    n_after = len(df_ent)
    print(f"  kept: {n_after} / {n_before} ({100*n_after/n_before:.1f}%)")
    print(f"  filtered out: {n_before - n_after}")

    print(f"\n[3/5] Capitalize entity_text (model output lowercase)")
    # Model NER output adalah lowercase (sesuai tokenizer indolem-base-uncased).
    # Title-case supaya schema downstream (relation_extraction, alias clustering)
    # konsisten dengan format manual labelling.
    df_ent["entity_text"] = df_ent["entity_text"].astype(str).str.title()
    # Koreksi kata-sambung nasab: gold pakai 'bin'/'binti' huruf KECIL (1268/45x),
    # sedangkan .title() menghasilkan 'Bin'/'Binti' → nama panjang jadi tak match
    # alias_map (mis. "Ali Bin Abu Thalib" vs kanonik "Ali bin Abu Thalib") ⟹
    # node terpecah. Kecilkan kembali agar konsisten dgn konvensi gold.
    df_ent["entity_text"] = df_ent["entity_text"].str.replace(r"\bBin\b", "bin", regex=True)
    df_ent["entity_text"] = df_ent["entity_text"].str.replace(r"\bBinti\b", "binti", regex=True)
    # Koreksi casing pasca-apostrof: .title() mengapitalkan huruf setelah "'"
    # (Ma'ad->Ma'Ad, Bu'ats->Bu'Ats). Konvensi gold: huruf setelah apostrof KECIL.
    df_ent["entity_text"] = df_ent["entity_text"].str.replace(
        r"'([A-Za-z])", lambda m: "'" + m.group(1).lower(), regex=True)

    # Drop EVENT generik non-spesifik (FP over-extraction): "Perang"/"Peperangan"/"Malam"
    # bukan nama peristiwa (cf clean_v3_nodes OP3). Nama pendek event asli
    # (Badr/Uhud/Isra/Khaibar/…) TETAP dipertahankan.
    GENERIC_EVENT = {"perang", "peperangan", "malam"}
    mask_generic = (df_ent["entity_label"] == "EVENT") & \
        (df_ent["entity_text"].str.strip().str.lower().isin(GENERIC_EVENT))
    if int(mask_generic.sum()):
        dropped = sorted(df_ent.loc[mask_generic, "entity_text"].unique())
        print(f"  drop {int(mask_generic.sum())} mention EVENT generik: {dropped}")
        df_ent = df_ent[~mask_generic].copy()

    print(f"\n[4/5] Join dengan chunks metadata: {args.chunks}")
    df_chunks = pd.read_csv(args.chunks, sep=";", encoding="utf-8-sig")
    print(f"  total chunks: {len(df_chunks)}")

    # Join on chunk_id
    df_merged = df_ent.merge(
        df_chunks[["chunk_id", "doc_id", "chunk_index", "judul_bab",
                   "judul_sub_bab", "halaman", "teks_chunk"]],
        on="chunk_id",
        how="left",
        suffixes=("_inf", ""),
    )

    # Pakai halaman dari chunks (lebih akurat formatnya), drop halaman dari inference
    if "halaman_inf" in df_merged.columns:
        df_merged = df_merged.drop(columns=["halaman_inf"])

    n_orphan = df_merged["doc_id"].isna().sum()
    if n_orphan > 0:
        print(f"  [WARN] {n_orphan} entity tanpa chunk metadata (drop)")
        df_merged = df_merged.dropna(subset=["doc_id"])

    # Rename entity_label -> label (sesuai schema sirah_prelabelled)
    df_merged = df_merged.rename(columns={"entity_label": "label"})

    # Add notes column (kosong)
    df_merged["notes"] = ""

    print(f"\n[5/5] Reorder + write: {args.output}")
    schema = [
        "chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab",
        "halaman", "teks_chunk", "entity_text", "label", "notes",
        "start_char", "end_char",
    ]
    df_out = df_merged[schema].copy()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(args.output, sep=";", encoding="utf-8-sig", index=False)
    print(f"  rows written: {len(df_out)}")
    print(f"  per-label final:")
    for lab, cnt in df_out["label"].value_counts().items():
        n_unique = df_out[df_out["label"] == lab]["entity_text"].nunique()
        print(f"    {lab:<10s}: {cnt} mentions, {n_unique} unique")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print(f"\nNext step:")
    print(f"  Edit src/relation_extraction/relation_extraction.py")
    print(f"  Set IN_PRELABELLED ke: {args.output}")
    print(f"  Set OUT_NODES ke: data/result/relation_result/nodes_v3.csv")
    print(f"  Set OUT_EDGES ke: data/result/relation_result/edges_v3.csv")
    print(f"  python src/relation_extraction/relation_extraction.py")


if __name__ == "__main__":
    main()
