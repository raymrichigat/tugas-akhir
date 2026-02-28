"""
Chunking + Seed Generation untuk Dataset Sirah Nabawiyah
1. Baca sirah_simple_clean.csv (hasil preprocessing)
2. Split teks per sub-bab menjadi chunks ≤1500 karakter dengan overlap 1 kalimat
3. Buat chunk_id unik (doc_id 6 digit - chunk_index 3 digit)
4. Sampling stratified per bab (maks 25 chunk/bab) untuk template anotasi manual
5. Ekspor sirah_chunks_final.csv dan sirah_manual_seed.csv
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_CSV = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\preprocessing_result\sirah_simple_clean.csv")
OUT_CHUNKS = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\chunking_result\sirah_chunks_final.csv")
OUT_SEED = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\chunking_result\sirah_manual_seed.csv")

MAX_CHARS = 1500
PER_BAB = 25
RANDOM_STATE = 42


# ── Fungsi chunking ─────────────────────────────────────────────────────────
def split_chunks_with_overlap(text: str, max_chars=MAX_CHARS):
    """
    Split teks menjadi chunks ≤max_chars karakter.
    Overlap: kalimat terakhir chunk sebelumnya diulang di chunk berikutnya.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    t = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+", t)
    sents = [s.strip() for s in sents if s.strip()]

    if not sents:
        return []

    chunks = []
    buf = ""
    last_sent = ""

    for s in sents:
        if len(buf) + 1 + len(s) <= max_chars:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                chunks.append(buf)
                last_sent = s  # kalimat yang tidak muat
                # Overlap: mulai chunk baru dengan kalimat terakhir chunk sebelumnya + kalimat baru
                prev_sents = re.split(r"(?<=[.!?])\s+", buf)
                overlap = prev_sents[-1] if prev_sents else ""
                buf = (overlap + " " + s).strip() if overlap else s
            else:
                # Kalimat tunggal > max_chars, masukkan apa adanya
                buf = s

    if buf:
        chunks.append(buf)

    return chunks


def make_chunk_id(doc_id: int, chunk_index: int) -> str:
    """Format: 000000-001"""
    return f"{doc_id:06d}-{chunk_index:03d}"


# ── Pipeline utama ───────────────────────────────────────────────────────────
def main():
    # =====================================================================
    # TAHAP 1: CHUNKING
    # =====================================================================
    print("=" * 60)
    print("TAHAP 1: CHUNKING")
    print("=" * 60)

    df = pd.read_csv(IN_CSV, sep=";", encoding="utf-8-sig").fillna("")
    print(f"Rows dari preprocessing: {len(df)}")

    rows = []
    for idx, r in df.iterrows():
        chunks = split_chunks_with_overlap(r["teks_clean"])
        if not chunks:
            continue
        for i, c in enumerate(chunks, start=1):
            rows.append({
                "chunk_id": make_chunk_id(idx, i),
                "doc_id": idx,
                "chunk_index": i,
                "judul_bab": r["judul_bab"],
                "judul_sub_bab": r["judul_sub_bab"],
                "halaman": r["halaman"],
                "teks_chunk": c,
            })

    df_chunks = pd.DataFrame(rows)

    # Pastikan output dir ada
    OUT_CHUNKS.parent.mkdir(parents=True, exist_ok=True)

    df_chunks.to_csv(OUT_CHUNKS, index=False, sep=";", encoding="utf-8-sig")
    print(f"Total chunks: {len(df_chunks)}")
    print(f"Output: {OUT_CHUNKS}")

    # =====================================================================
    # TAHAP 2: SEED GENERATION (SAMPLING UNTUK ANOTASI MANUAL)
    # =====================================================================
    print(f"\n{'=' * 60}")
    print("TAHAP 2: SEED GENERATION")
    print("=" * 60)

    # Stratified sampling: maks PER_BAB chunk per bab
    seed = (
        df_chunks.groupby("judul_bab", group_keys=False)
        .apply(lambda g: g.sample(n=min(len(g), PER_BAB), random_state=RANDOM_STATE),
               include_groups=False)
        .reset_index(drop=True)
    )

    # Re-attach kolom yang hilang karena include_groups=False
    # Kita sampling ulang dengan cara yang lebih aman
    seed = (
        df_chunks.groupby("judul_bab", group_keys=False)
        .apply(lambda g: g.sample(n=min(len(g), PER_BAB), random_state=RANDOM_STATE))
        .reset_index(drop=True)
    )

    print(f"Seed size: {len(seed)}")
    print(f"\nTop 10 bab:")
    print(seed[["judul_bab"]].value_counts().head(10).to_string())

    # Tambah kolom anotasi manual (kosong)
    cols = ["chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab", "halaman", "teks_chunk"]
    seed_out = seed[cols].copy()
    seed_out["entity_text"] = ""
    seed_out["label"] = ""
    seed_out["notes"] = ""
    seed_out["start_char"] = ""
    seed_out["end_char"] = ""

    seed_out.to_csv(OUT_SEED, index=False, sep=";", encoding="utf-8-sig")
    print(f"\nOutput: {OUT_SEED}")

    # =====================================================================
    # RINGKASAN
    # =====================================================================
    print(f"\n{'=' * 60}")
    print("RINGKASAN")
    print("=" * 60)
    print(f"  Input rows       : {len(df)}")
    print(f"  Total chunks     : {len(df_chunks)}")
    print(f"  Seed untuk anotasi: {len(seed)}")
    print(f"  Maks chunk/bab   : {PER_BAB}")


if __name__ == "__main__":
    main()
