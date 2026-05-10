"""
prepare_bert_data.py
====================
Mengkonversi anotasi span-level (sirah_prelabelled.csv) ke format CoNLL
token-per-baris yang dibutuhkan pipeline BERT NER.

Apa yang dilakukan script ini (urutan):
  1. Baca sirah_prelabelled.csv -> kumpulkan semua entitas per chunk
  2. Tokenisasi teks_chunk menjadi kata-kata, lacak posisi karakter tiap kata
  3. Tandai tiap kata dengan label BIO (B-PERSON, I-PERSON, O, dst.)
  4. Split chunk berlabel -> 70% train.csv + 30% test.csv (stratified per bab)
  5. Baca sirah_chunks_final.csv -> ambil chunk yang TIDAK ada di seed
  6. Tokenisasi chunk unlabeled (tanpa label) -> unlabelled.csv

Format output (mengikuti format notebook referensi):
  Berlabel  : text_id | id | token | pos_tag | label
  Unlabeled : text_id | id | token | pos_tag
"""

import re
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_LABELLED  = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\manual_labelling\sirah_prelabelled.csv")
IN_ALL_CHUNKS = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\chunking_result\sirah_chunks_final.csv")

OUT_DIR      = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\pseudo-labelling\SRL-NER")

TEST_SIZE    = 0.3    # 30% untuk test/evaluasi
RANDOM_STATE = 42


# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 1: TOKENISASI DENGAN POSISI KARAKTER
# ─────────────────────────────────────────────────────────────────────────────

def tokenize_with_offsets(text: str) -> list[tuple[str, int, int]]:
    """
    Pecah teks menjadi kata-kata dan catat posisi karakter tiap kata.

    Contoh:
      Input : "Abu Bakar pergi ke Madinah."
      Output: [("Abu", 0, 3), ("Bakar", 4, 9), ("pergi", 10, 15),
               ("ke", 16, 18), ("Madinah.", 19, 27)]

    Kenapa perlu posisi karakter?
      Karena anotasi di sirah_prelabelled.csv menyimpan posisi entitas
      dalam bentuk start_char/end_char. Kita perlu tahu kata mana yang
      masuk ke dalam rentang posisi itu.
    """
    return [
        (m.group(), m.start(), m.end())
        for m in re.finditer(r"\S+", text)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 2: PEMBERIAN LABEL BIO
# ─────────────────────────────────────────────────────────────────────────────

def assign_bio_label(tok_start: int, tok_end: int, entities: list[dict]) -> str:
    """
    Tentukan label BIO untuk satu token berdasarkan posisi karakternya.

    Aturan BIO:
      B-LABEL : token pertama dari suatu entitas (Begin)
      I-LABEL : token lanjutan entitas yang sama (Inside)
      O       : bukan bagian dari entitas manapun (Outside)

    Contoh untuk entitas PERSON "Abu Bakar" di posisi 0-9:
      Token "Abu"   (0-3)  -> B-PERSON  (awal entitas, tok_start == ent_start)
      Token "Bakar" (4-9)  -> I-PERSON  (lanjutan, tok_start > ent_start)
      Token "pergi" (10-15)-> O

    Jika ada overlap antar entitas (seharusnya jarang setelah dedup),
    entitas yang lebih panjang diprioritaskan.
    """
    # Urutkan entitas: yang lebih panjang diperiksa duluan (prioritas lebih spesifik)
    sorted_ents = sorted(entities, key=lambda e: -(e["end_char"] - e["start_char"]))

    for ent in sorted_ents:
        es  = int(ent["start_char"])
        ee  = int(ent["end_char"])
        lbl = ent["label"]

        # Token sepenuhnya di dalam span entitas
        if tok_start >= es and tok_end <= ee:
            return f"B-{lbl}" if tok_start == es else f"I-{lbl}"

        # Token overlap sebagian dengan span entitas (kasus OCR / tokenisasi kasar)
        if tok_start < ee and tok_end > es:
            return f"B-{lbl}" if tok_start <= es else f"I-{lbl}"

    return "O"


# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 3: KONVERSI SATU CHUNK -> BARIS-BARIS CoNLL
# ─────────────────────────────────────────────────────────────────────────────

def chunk_to_rows(chunk_id: str, text: str,
                  entities: list[dict], include_label: bool = True) -> list[dict]:
    """
    Ubah satu chunk teks + daftar entitasnya menjadi list baris CoNLL.

    Tiap baris mewakili satu token (kata) dengan kolom:
      text_id  : ID chunk (misal "000354-001")
      id       : ID token dalam chunk (misal "000354-001.001")
      token    : kata itu sendiri (misal "Rasulullah")
      pos_tag  : POS tag — diisi "NN" semua karena tidak ada POS tagger
                 (kolom ini tetap dibutuhkan agar format sama dengan referensi)
      label    : tag BIO (misal "B-PERSON") — hanya jika include_label=True
    """
    tokens = tokenize_with_offsets(text)
    rows = []

    for i, (token, tok_start, tok_end) in enumerate(tokens, start=1):
        row = {
            "text_id": chunk_id,
            "id":      f"{chunk_id}.{i:03d}",
            "token":   token,
            "pos_tag": "NN",   # placeholder, tidak dipakai saat training BERT
        }
        if include_label:
            row["label"] = assign_bio_label(tok_start, tok_end, entities)
        rows.append(row)

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# BAGIAN 4: PIPELINE UTAMA
# ─────────────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 4A. Baca data berlabel ────────────────────────────────────────────────
    # sirah_prelabelled.csv punya SATU BARIS PER ENTITAS.
    # Chunk yang punya 5 entitas -> 5 baris.
    # Chunk yang kosong (tidak ada entitas) -> 1 baris dengan label kosong.
    print("Membaca data berlabel...")
    df_lab = pd.read_csv(IN_LABELLED, sep=";", encoding="utf-8-sig").fillna("")
    print(f"  Total baris : {len(df_lab)}")
    print(f"  Total chunk : {df_lab['chunk_id'].nunique()}")

    # ── 4B. Kelompokkan entitas per chunk ─────────────────────────────────────
    # Dari format "satu baris per entitas" -> dict {chunk_id: [entitas1, entitas2, ...]}
    chunk_meta = {}   # chunk_id -> (teks_chunk, judul_bab)
    chunk_ents = {}   # chunk_id -> list of entity dicts

    for _, row in df_lab.iterrows():
        cid  = row["chunk_id"]
        text = str(row["teks_chunk"])
        bab  = str(row["judul_bab"])

        if cid not in chunk_meta:
            chunk_meta[cid] = (text, bab)
            chunk_ents[cid] = []

        # Hanya tambahkan jika baris ini punya label dan posisi yang valid
        lbl = str(row.get("label", "")).strip()
        sc  = str(row.get("start_char", "")).strip()
        ec  = str(row.get("end_char", "")).strip()

        try:
            sc_int = int(float(sc))
            ec_int = int(float(ec))
            valid_pos = True
        except (ValueError, TypeError):
            valid_pos = False

        if lbl and valid_pos:
            chunk_ents[cid].append({
                "entity_text": str(row.get("entity_text", "")),
                "label":       lbl,
                "start_char":  sc_int,
                "end_char":    ec_int,
            })

    print(f"  Chunk dengan entitas : "
          f"{sum(1 for v in chunk_ents.values() if v)} / {len(chunk_meta)}")

    # ── 4C. Konversi semua chunk berlabel -> CoNLL rows ────────────────────────
    print("\nMengkonversi span -> BIO token-per-baris...")
    all_labeled_rows = []
    chunk_ids_labeled = list(chunk_meta.keys())

    for cid in chunk_ids_labeled:
        text, _ = chunk_meta[cid]
        entities = chunk_ents[cid]
        rows = chunk_to_rows(cid, text, entities, include_label=True)
        all_labeled_rows.extend(rows)

    df_conll = pd.DataFrame(all_labeled_rows)

    # Statistik distribusi label
    label_counts = df_conll["label"].value_counts()
    print("  Distribusi label:")
    for lbl, cnt in label_counts.items():
        print(f"    {lbl:<12}: {cnt}")

    # ── 4D. Split train / test (stratified per bab) ───────────────────────────
    # Split dilakukan di LEVEL CHUNK (bukan token) agar tidak ada data leakage.
    # Satu chunk utuh masuk train atau test, tidak dipecah.
    print(f"\nSplit train/test ({int((1-TEST_SIZE)*100)}/{int(TEST_SIZE*100)})...")

    chunk_bab_df = pd.DataFrame([
        {"chunk_id": cid, "judul_bab": chunk_meta[cid][1]}
        for cid in chunk_ids_labeled
    ])

    try:
        train_ids, test_ids = train_test_split(
            chunk_bab_df["chunk_id"],
            test_size=TEST_SIZE,
            stratify=chunk_bab_df["judul_bab"],
            random_state=RANDOM_STATE,
        )
        print("  Stratified split berhasil (per bab).")
    except ValueError:
        # Fallback: beberapa bab hanya punya 1 chunk, stratified tidak bisa
        train_ids, test_ids = train_test_split(
            chunk_bab_df["chunk_id"],
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )
        print("  Fallback ke random split (ada bab dengan chunk terlalu sedikit).")

    train_set = set(train_ids)
    test_set  = set(test_ids)

    df_train = df_conll[df_conll["text_id"].isin(train_set)].reset_index(drop=True)
    df_test  = df_conll[df_conll["text_id"].isin(test_set)].reset_index(drop=True)

    print(f"  Train : {df_train['text_id'].nunique()} chunks, {len(df_train)} token")
    print(f"  Test  : {df_test['text_id'].nunique()} chunks, {len(df_test)} token")

    # ── 4E. Buat unlabelled dari chunk di luar seed ───────────────────────────
    # Ambil semua chunk dari sirah_chunks_final.csv,
    # lalu buang yang sudah ada di sirah_manual_seed (chunk berlabel).
    print("\nMembuat data unlabelled...")
    df_all = pd.read_csv(IN_ALL_CHUNKS, sep=";", encoding="utf-8-sig").fillna("")

    seed_chunk_ids = set(chunk_ids_labeled)
    df_unlabelled_src = df_all[~df_all["chunk_id"].isin(seed_chunk_ids)].copy()
    print(f"  Chunk unlabelled : {len(df_unlabelled_src)} "
          f"(dari {len(df_all)} total, seed={len(seed_chunk_ids)})")

    unlabelled_rows = []
    for _, row in df_unlabelled_src.iterrows():
        rows = chunk_to_rows(
            row["chunk_id"], str(row["teks_chunk"]),
            entities=[], include_label=False
        )
        unlabelled_rows.extend(rows)

    df_unlabelled = pd.DataFrame(unlabelled_rows)
    print(f"  Total token unlabelled : {len(df_unlabelled)}")

    # ── 4F. Simpan semua output ───────────────────────────────────────────────
    path_train = OUT_DIR / "train.csv"
    path_test  = OUT_DIR / "test.csv"
    path_unlab = OUT_DIR / "unlabelled.csv"

    df_train.to_csv(path_train, index=False)
    df_test.to_csv(path_test,  index=False)
    df_unlabelled.to_csv(path_unlab, index=False)

    print(f"\nOutput disimpan ke: {OUT_DIR}")
    print(f"  train.csv      : {path_train.name}  ({len(df_train)} baris)")
    print(f"  test.csv       : {path_test.name}   ({len(df_test)} baris)")
    print(f"  unlabelled.csv : {path_unlab.name}  ({len(df_unlabelled)} baris)")

    # ── 4G. Preview ──────────────────────────────────────────────────────────
    print("\nPreview train.csv (15 baris pertama):")
    print(df_train.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
