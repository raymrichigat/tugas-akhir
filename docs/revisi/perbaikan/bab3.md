# Perbaikan BAB 3 — hasil akhir

## P-3.1. Contoh NER berjalan: kalimat→token→BIO→entitas→node (Bu Nanik #1, Bu Ratih #6) 🧰

Sumber: `docs/revisi/artefak/contoh_ner_dan_data_latih.md` (contoh Mush'ab bin Umair → Makkah).
Satukan Tabel 3.9 (BIO) + Tabel 3.12 (hasil NER) jadi **satu contoh berjalan**.

## P-3.1b. Alur NER → KG UTUH satu contoh (Bu Nanik #5, Bu Dini #7) 🧰
Sumber: `docs/revisi/artefak/contoh_ner_ke_kg_utuh.md` — SATU data (Abu Jahal → Perang Badr, chunk
000071-003) ditelusuri 8 tahap: teks → BIO → entitas → normalisasi alias → pasangan → relasi
INVOLVED_IN (w=0,5) → node/edge → Cypher Neo4j. Jadikan satu gambar/tabel alur menyeluruh (Bu Dini
minta jangan terpisah-pisah).

## P-3.2. Satu record data latih utuh (Bu Nanik #2, Bu Dini #5) 🧰

Sumber: idem — record `000384-001` (chunk_id, teks, token, BIO, metadata, POS). **Nyatakan POS =
placeholder `NN`** bila tidak dipakai model.

## P-3.3. Ganti "alias clustering" → "normalisasi alias" (Bu Nanik #5, Bu Ratih #7) 🧰

Rename di Subbab 3.7.1, Gambar 3.8, Kode Semu 3.8. Dasar & perbandingan vs Rayssa:
`docs/revisi/artefak/perbandingan_alias_clustering_rayssa.md`. Jaro-Winkler = **ukuran kemiripan
string**, bukan algoritma clustering. **Justifikasi ambang 0,93:**
`docs/revisi/artefak/justifikasi_ambang_jaro_winkler.md`.

## P-3.4. Dasar ambang co-occurrence 200 karakter + contoh benar/salah (Bu Nanik #6) 🧰

Sumber: `docs/revisi/artefak/dasar_cooccurrence_200_karakter.md`. Metode = sekalimat **atau**
<200 char + bobot bertingkat; dasar empiris (kalimat median 100 char, 84,9% ≤200; jarak entitas
82,7% <200). Contoh positif (Abdurrahman bin Auf) + negatif 3 pola (negasi/perawi/beda-peristiwa).

## P-3.5. Prosedur validitas semantis KG (Bu Nanik #8) 🧰

Sumber: `teks_bab2_bab3_validitas_semantis.md` bagian B — unit per fungsi (F5 = per jalur, valid
bila **kedua** relasi didukung), kriteria valid/tidak, jawaban sebagian benar = tidak valid,
pemeriksa manual, keterbatasan 1-anotator (sekaligus Bu Ratih #5).

## P-3.6. Negasi sebagai KETERBATASAN (Bu Nanik #6, Bu Dini #8) 🧰

Sumber: `docs/revisi/artefak/keterbatasan_negasi_relasi.md` (bukti Abu Lahab → Perang Badr).

## P-3.6b. Dasar pemilihan hyperparameter (Pak Aldi #5) 🧰
Sumber: `docs/revisi/artefak/dasar_hyperparameter.md`. Nilai (lr 2e-5 / batch 16 / 10 epoch +
early stopping / weight decay 0,01 / seed 42 / threshold 0,9 / IndoBERT uncased) + alasan tiap
parameter dari **referensi nyata: Ariyanto dkk. (2025), IEEE Access** (DOI 10.1109/ACCESS.2025.3604068
— first author Mbak Amelia). Framing: nilai awal dari penelitian acuan sejenis, diuji ulang di
Sirah. ⚠️ Jujur: maks 6 iterasi = titik henti praktis, BUKAN dari referensi.

## P-3.7. Contoh chunking sebelum/sesudah (Bu Ratih #4) 🧰
Sumber: `docs/revisi/artefak/contoh_chunking.md`. Param: ≤1500 char, overlap 1 kalimat, batas
kalimat dijaga, metadata bab/sub-bab/halaman. Contoh nyata sub-bab "Kekuasaan di Berbagai Penjuru
Arab" (hal 53–54) → 2 chunk dengan kalimat overlap terlihat.

## P-3.8. Definisi token/subtoken/chunk/batch + penyelarasan BIO↔subtoken (Bu Nanik #3/#4) 🧰
Sumber: `docs/revisi/artefak/definisi_token_subtoken.md`. Definisi 4 istilah + contoh split nyata
("Mush'ab"→`mush`+`'`+`ab`; "Umair"→`uma`+`##ir`) + kode `tokenize_and_align_labels` asli (subtoken
pertama = label, lanjutan & special = `-100`; `word_ids()`; max 512). Pindahkan dari Bab 4 ke
metodologi.

## P-3.9. Protokol koreksi manual (Bu Ratih #5) 🧰⚠️
Sumber: `docs/revisi/artefak/protokol_koreksi_manual.md` (+ showcase asli
`data/result/manual_labelling/gold_review/koreksi_gold_showcase.md` + pedoman
`docs/anotasi_guideline.md`). Alasan koreksi (semi-auto→error) + 99 koreksi terkategori (kelewat/
batas/LOC↔EVENT/palsu/OCR/tipe) + contoh before→after + anotator tunggal (keterbatasan, no IAA).
**⚠️ KONFIRMASI framing dulu:** ini koreksi saat MEMBUAT gold (metodologi, boleh); jangan tertukar
dgn koreksi GT-test pasca-hasil (arahan lama: lisan saja). Tanya pembimbing seberapa detail.
