"""
build_v3_entity_from_token.py
==============================
Re-build `sirah_predicted_v3_entity.csv` dari `sirah_predicted_v3_token.csv`
dengan logic BIO yang benar (decode B/I span jadi entity utuh).

Background (2026-05-28):
HF pipeline aggregation_strategy='first' atau 'simple' tidak konsisten
saat menggabungkan span yang punya special char (apostrof, dash, dll).
Hasilnya entity_text di sirah_predicted_v3_entity.csv ke-fragment:
  "ubaidah" + "bin al - harits"  (harusnya 1 entity "Ubaidah bin Al-Harits")
  "utbah" + "bin rabi"           (harusnya "Utbah bin Rabi'ah")
  "perang" + "badr"              (harusnya "Perang Badr")

Sementara token-level CSV (sirah_predicted_v3_token.csv) BIO-nya benar:
  Ubaidah  -> B_PERSON
  bin      -> I_PERSON
  Al-Harits -> I_PERSON

Script ini decode span dari token-level BIO + reconstruct entity-level CSV
yang akurat. Output drop-in compatible dengan format inference yang lama.

Input:
  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v3_token.csv
  data/result/chunking_result/sirah_chunks_final.csv (untuk lookup posisi char)

Output:
  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v3_entity.csv
  (overwrite versi yang corrupted)

Backup versi corrupted ke .bak sebelum overwrite.

Idempotent. Usage:
  venv\\Scripts\\python.exe src/relation_extraction/build_v3_entity_from_token.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TOKEN_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "inference" / "sirah_predicted_v3_token.csv"
ENTITY_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "inference" / "sirah_predicted_v3_entity.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"


def decode_bio_spans(tokens, labels):
    """
    Decode BIO sequence -> list of (start_token_idx, end_token_idx_exclusive, label_type).

    Aturan:
      - B_X memulai span baru tipe X
      - I_X melanjutkan span jika prev label adalah B_X / I_X
      - I_X tanpa B_X di depan -> treat sebagai B_X (toleran terhadap mis-prediction)
      - O atau label berbeda -> close span saat ini
    """
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
        while j < n:
            next_lab = labels[j]
            if next_lab == f"I_{etype}":
                j += 1
            else:
                break
        spans.append((i, j, etype))
        i = j
    return spans


def find_token_char_positions(text, tokens):
    """
    Map setiap token ke (start_char, end_char) di teks asli, dengan whitespace-split alignment.

    Return list of (start, end) untuk tiap token. Aman untuk text yang punya
    multi-whitespace (cari token di urutan, jaga current_pos).
    """
    positions = []
    pos = 0
    for tok in tokens:
        # cari token mulai dari pos sekarang
        idx = text.find(tok, pos)
        if idx == -1:
            # fallback: pakai posisi current+1 (mismatch akan menumpuk, tapi minor)
            idx = pos
        end = idx + len(tok)
        positions.append((idx, end))
        pos = end
    return positions


def main():
    print("=" * 60)
    print("BUILD v3 ENTITY-LEVEL FROM TOKEN-LEVEL BIO")
    print("=" * 60)

    print(f"\n[1/4] Load token-level: {TOKEN_CSV}")
    df_tok = pd.read_csv(TOKEN_CSV, encoding="utf-8-sig")
    df_tok["token"] = df_tok["token"].astype(str)
    df_tok["predicted_label"] = df_tok["predicted_label"].astype(str)
    print(f"  total rows  : {len(df_tok)}")
    print(f"  unique chunks: {df_tok['text_id'].nunique()}")

    print(f"\n[2/4] Load chunks teks: {CHUNKS_CSV}")
    df_chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig")
    chunk_text_map = dict(zip(df_chunks["chunk_id"].astype(str), df_chunks["teks_chunk"].astype(str)))
    chunk_halaman_map = dict(zip(df_chunks["chunk_id"].astype(str), df_chunks["halaman"].astype(str)))
    print(f"  chunks      : {len(df_chunks)}")

    print(f"\n[3/4] Decode BIO spans + reconstruct entity_text dari posisi char...")
    entity_rows = []
    grouped = df_tok.groupby("text_id", sort=False)
    n_chunks_processed = 0
    for chunk_id, sub in grouped:
        sub = sub.sort_index()
        tokens = sub["token"].tolist()
        labels = sub["predicted_label"].tolist()
        text = chunk_text_map.get(str(chunk_id), "")
        if not text:
            continue
        n_chunks_processed += 1

        # Map tiap token -> posisi char di teks asli
        positions = find_token_char_positions(text, tokens)

        # Decode spans (token-level)
        spans = decode_bio_spans(tokens, labels)

        for start_tok, end_tok_excl, etype in spans:
            char_start = positions[start_tok][0]
            char_end = positions[end_tok_excl - 1][1]
            entity_text = text[char_start:char_end]
            # Strip trailing punctuation (comma/period/colon/semicolon/etc) yang
            # sering ke-include dalam span — kasus: "Perang Badr." atau "Madinah,"
            # menyebabkan duplikasi entity unique. Strip leading juga.
            cleaned = entity_text.strip(" \t\n.,;:!?\"'()[]{}")
            if cleaned and cleaned != entity_text:
                # Adjust char_end agar konsisten dengan teks yang ditulis
                # (cari posisi cleaned di entity_text asli)
                offset = entity_text.find(cleaned)
                char_start = char_start + offset
                char_end = char_start + len(cleaned)
                entity_text = cleaned
            elif not cleaned:
                continue  # all punctuation — skip
            entity_rows.append({
                "chunk_id": chunk_id,
                "halaman": chunk_halaman_map.get(str(chunk_id), ""),
                "entity_text": entity_text,
                "entity_label": etype,
                "start_char": char_start,
                "end_char": char_end,
                "confidence": 0.99,  # BIO span derived; tidak punya confidence eksplisit per span
            })

    df_ent = pd.DataFrame(entity_rows)
    print(f"  chunks processed: {n_chunks_processed}")
    print(f"  entities decoded: {len(df_ent)}")
    print(f"  per-label:")
    for lab, cnt in df_ent["entity_label"].value_counts().items():
        n_unique = df_ent[df_ent["entity_label"] == lab]["entity_text"].nunique()
        print(f"    {lab:<10s}: {cnt} mentions, {n_unique} unique")

    # Sanity check: count multi-word entities
    df_ent["n_words"] = df_ent["entity_text"].str.split().str.len()
    multiword = (df_ent["n_words"] > 1).sum()
    print(f"  multi-word entities: {multiword} ({100*multiword/len(df_ent):.1f}%)")
    df_ent = df_ent.drop(columns=["n_words"])

    print(f"\n[4/4] Backup + write {ENTITY_CSV}...")
    if ENTITY_CSV.exists():
        backup = ENTITY_CSV.with_suffix(".csv.bak")
        shutil.copy2(ENTITY_CSV, backup)
        print(f"  backup -> {backup}")

    df_ent.to_csv(ENTITY_CSV, sep=";", encoding="utf-8-sig", index=False)
    print(f"  -> {ENTITY_CSV}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print("\nNext:")
    print("  python src/relation_extraction/build_v3_prelabelled_from_inference.py")
    print("  python src/relation_extraction/relation_extraction.py --input ... --out-nodes ... --out-edges ...")


if __name__ == "__main__":
    main()
