"""
build_v4_entity_from_token.py
==============================
Re-build entity-level CSV dari token-level BIO untuk inference v4
(model winner **S4-augmentation**, benchmark gold-terkoreksi, F1 entity 0.9458).

Ini port dari `build_v3_entity_from_token.py` dengan path v4. Alasan tetap perlu:
HF pipeline `aggregation_strategy='first'` kadang men-fragment entity multi-kata
yang punya special char (apostrof/dash), mis. "Ubaidah" + "bin al - harits".
Token-level BIO tetap benar, jadi kita decode span dari token → entity utuh.

Input:
  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v4_token.csv
  data/result/chunking_result/sirah_chunks_final.csv (lookup posisi char)

Output (overwrite versi fragmented dari Colab, backup .bak dulu):
  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v4_entity.csv

Idempotent. Usage:
  venv\\Scripts\\python.exe src/relation_extraction/build_v4_entity_from_token.py
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INF_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "inference" / "v4"
TOKEN_CSV = INF_DIR / "sirah_predicted_v4_token.csv"
ENTITY_CSV = INF_DIR / "sirah_predicted_v4_entity.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"


def decode_bio_spans(tokens, labels):
    """Decode BIO -> list of (start_tok_idx, end_tok_idx_exclusive, label_type)."""
    spans = []
    i = 0
    n = len(labels)
    while i < n:
        lab = labels[i]
        if lab == "O" or "_" not in lab:
            i += 1
            continue
        prefix, etype = lab.split("_", 1)
        if prefix not in ("B", "I"):
            i += 1
            continue
        j = i + 1
        while j < n and labels[j] == f"I_{etype}":
            j += 1
        spans.append((i, j, etype))
        i = j
    return spans


def find_token_char_positions(text, tokens):
    """Map tiap token -> (start_char, end_char) di teks asli (whitespace-split align)."""
    positions = []
    pos = 0
    for tok in tokens:
        idx = text.find(tok, pos)
        if idx == -1:
            idx = pos
        end = idx + len(tok)
        positions.append((idx, end))
        pos = end
    return positions


def main():
    p = argparse.ArgumentParser(description="Rebuild v4 entity-level from token-level BIO")
    p.add_argument("--token", type=Path, default=TOKEN_CSV)
    p.add_argument("--entity", type=Path, default=ENTITY_CSV)
    p.add_argument("--chunks", type=Path, default=CHUNKS_CSV)
    args = p.parse_args()

    print("=" * 60)
    print("BUILD v4 ENTITY-LEVEL FROM TOKEN-LEVEL BIO (S4-augmentation)")
    print("=" * 60)

    print(f"\n[1/4] Load token-level: {args.token}")
    df_tok = pd.read_csv(args.token, encoding="utf-8-sig")
    df_tok["token"] = df_tok["token"].astype(str)
    df_tok["predicted_label"] = df_tok["predicted_label"].astype(str)
    print(f"  total rows   : {len(df_tok)}")
    print(f"  unique chunks: {df_tok['text_id'].nunique()}")

    print(f"\n[2/4] Load chunks teks: {args.chunks}")
    df_chunks = pd.read_csv(args.chunks, sep=";", encoding="utf-8-sig")
    chunk_text_map = dict(zip(df_chunks["chunk_id"].astype(str), df_chunks["teks_chunk"].astype(str)))
    chunk_halaman_map = dict(zip(df_chunks["chunk_id"].astype(str), df_chunks["halaman"].astype(str)))
    print(f"  chunks       : {len(df_chunks)}")

    print(f"\n[3/4] Decode BIO spans + reconstruct entity_text dari posisi char...")
    entity_rows = []
    n_chunks_processed = 0
    for chunk_id, sub in df_tok.groupby("text_id", sort=False):
        sub = sub.sort_index()
        tokens = sub["token"].tolist()
        labels = sub["predicted_label"].tolist()
        text = chunk_text_map.get(str(chunk_id), "")
        if not text:
            continue
        n_chunks_processed += 1
        positions = find_token_char_positions(text, tokens)
        for start_tok, end_tok_excl, etype in decode_bio_spans(tokens, labels):
            char_start = positions[start_tok][0]
            char_end = positions[end_tok_excl - 1][1]
            entity_text = text[char_start:char_end]
            cleaned = entity_text.strip(" \t\n.,;:!?\"'()[]{}")
            if cleaned and cleaned != entity_text:
                offset = entity_text.find(cleaned)
                char_start = char_start + offset
                char_end = char_start + len(cleaned)
                entity_text = cleaned
            elif not cleaned:
                continue
            entity_rows.append({
                "chunk_id": chunk_id,
                "halaman": chunk_halaman_map.get(str(chunk_id), ""),
                "entity_text": entity_text,
                "entity_label": etype,
                "start_char": char_start,
                "end_char": char_end,
                "confidence": 0.99,  # BIO span derived
            })

    df_ent = pd.DataFrame(entity_rows)
    print(f"  chunks processed: {n_chunks_processed}")
    print(f"  entities decoded: {len(df_ent)}")
    for lab, cnt in df_ent["entity_label"].value_counts().items():
        n_unique = df_ent[df_ent["entity_label"] == lab]["entity_text"].nunique()
        print(f"    {lab:<10s}: {cnt} mentions, {n_unique} unique")
    n_multi = (df_ent["entity_text"].str.split().str.len() > 1).sum()
    print(f"  multi-word entities: {n_multi} ({100*n_multi/len(df_ent):.1f}%)")

    print(f"\n[4/4] Backup + write {args.entity}...")
    if args.entity.exists():
        backup = args.entity.with_suffix(".csv.bak")
        shutil.copy2(args.entity, backup)
        print(f"  backup -> {backup}")
    df_ent.to_csv(args.entity, sep=";", encoding="utf-8-sig", index=False)
    print(f"  -> {args.entity}")

    print("\n" + "=" * 60)
    print("SELESAI — next: build_v4_hybrid_entity.py (untuk versi hibrida)")
    print("=" * 60)


if __name__ == "__main__":
    main()
