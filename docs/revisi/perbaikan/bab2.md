# Perbaikan BAB 2 — hasil akhir

## P-2.1. Teori Confusion Matrix (Pak Aldi #3) 📝

Tambahkan subbab konsep confusion matrix + **tegaskan level**: entity-level 4 tipe
(PERSON/LOCATION/EVENT/TIME) **atau** token-level BIO 9 kelas (`O`, `B-`/`I-` tiap entitas).
Hubungkan ke precision/recall/F1. (Contoh gambar hasil ada di Bab 4 / lampiran.)

## P-2.2. Teori class imbalance + "menangani ≠ menyeimbangkan" (Pak Aldi #6/#7) 🧰

Sumber teks & sitasi: `docs/revisi/artefak/augmentasi_contoh_dan_distribusi.md` §"Menangani ≠
menyeimbangkan". Poin: ketimpangan gradual, tidak ada ambang universal; **augmentasi = metode
menangani** (Henning dkk. 2023); NER long-tail, sukses = minoritas naik tanpa korban mayoritas
(Nemoto dkk. 2024/2025). **Bedakan dua tingkat:** token `O` (mayoritas asli) vs antar-entitas
(PERSON terbanyak). Rujukan ≤5 tahun (Henning 2023; Nemoto 2024/2025).

## P-2.3. Batas evaluasi fungsional + teori validitas semantis (Bu Nanik #8) 🧰

Sumber: `docs/revisi/artefak/validitas_semantis/teks_bab2_bab3_validitas_semantis.md` bagian A
(§1a paragraf pembatas klaim *fitness for purpose* + §1b rumus). **Tanpa referensi eksternal
baru** — competency-questions §2.7 (Greco/Keet & Khan/Farrugia/Illueca 2025) sudah menopang.
Rumus: kesesuaian semantis = (jawaban didukung sumber ÷ diperiksa) × 100%.

## P-2.4. Model cased vs uncased diperkenalkan lebih awal (Pak Aldi #9) 📝

Pembahasan hasil cased/uncased/RoBERTa di hal 84–86 **jangan ditulis ulang**; pindahkan/ringkas
**landasan konsepnya** (cased simpan kapital; uncased normalisasi kapital) ke Bab 2/3 sebelum hasil.

## P-2.5. Perbaiki notasi Persamaan (Pak Aldi #2, Bu Ratih #3) ✅/📝

- **Typo betweenness Persamaan (2.13):** `σ_st(v)` saat ini "…jumlah jalur terpendek dari simpul
  **𝑡 ke simpul 𝑡**…" → betulkan "…dari simpul **𝑠 ke simpul 𝑡**…".
- Audit semua simbol (SNA, loss, Jaccard, augmentasi) agar tiap variabel didefinisikan; rujuk tiap
  persamaan dengan nomor eksplisit.

## P-2.6. Rujukan konstruksi KG, entity linking, relation extraction (Bu Nanik #7/#9) 🧰
Sumber: `docs/revisi/artefak/referensi_konstruksi_kg.md` — rujukan nyata ≤5 tahun (KG construction
MDPI Appl.Sci 2025 / CMES 2024; RE survey arXiv 2306.02051 2023; entity linking Sevgili dkk. 2022
Semantic Web) + tabel "diadopsi vs dimodifikasi untuk Sirah" + batas klaim (relasi = induksi
heuristik, bukan semantic RE penuh; normalisasi alias = versi sederhana, bukan neural EL). Cek
penulis/halaman sebelum tulis.
