# Perbaikan BAB 3 — hasil akhir

## P-3.1. Contoh NER berjalan: kalimat→token→BIO→entitas→node (Bu Nanik #1, Bu Ratih #6) 🧰

Sumber: `docs/revisi/artefak/contoh_ner_dan_data_latih.md` (contoh Mush'ab bin Umair → Makkah).
Satukan Tabel 3.9 (BIO) + Tabel 3.12 (hasil NER) jadi **satu contoh berjalan**.

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

## P-3.7. BELUM ADA — perlu ditulis 📝
- **Contoh chunking sebelum/sesudah** (Bu Ratih #4): teks Sirah nyata + alasan panjang chunk +
  overlap + penanganan kalimat terpotong + metadata halaman.
- **Definisi token/subtoken/chunk/batch** + penyelarasan BIO↔subtoken (strategi subtoken pertama,
  `word_ids()`) (Bu Nanik #3/#4) — pindahkan dari analisis Bab 4 ke metodologi.
- **Protokol koreksi manual** + alasan (Bu Ratih #5).
