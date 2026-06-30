# Audit Gold — "Tiap entitas salah di bagian mana" (tafsiran B)

> ⚠️ **DIAGNOSTIK SEMENTARA — BUKAN HASIL FINAL.** Kolom prediksi berasal dari **model LAMA** (S3.2 winner di disk), dipakai HANYA sebagai alat menemukan gold yang kelewat/aneh. Setelah SEMUA model dilatih ULANG (pasca perbaikan gold), worksheet ini di-refresh dengan prediksi model BARU. Jangan dipakai sebagai angka/hasil.

Sumber sinyal: ketidaksepakatan model vs gold di TEST (`test_predictions.csv`). Total token tak sepakat: **114** dari 49744 (0.2%).

## Distribusi per kategori ketidaksepakatan

- **A. gold=O, model=ENTITAS (kandidat gold KELEWAT / model FP)** : 63
- **B. gold=ENTITAS, model=O (kandidat gold KELEBIHAN / model FN)** : 40
- **C. beda TIPE (kandidat salah-tipe)** : 11

## Distribusi per USULAN penyebab ("salah di bagian mana")

- ANOTASI_KELEWAT (regex tak menangkap nama berkapital) : 43
- MODEL_MISS atau gold KELEBIHAN (perlu cek konteks) : 39
- KAPITALISASI/huruf-kecil (gold=O, perlu cek) : 13
- SALAH_TIPE (gold vs model beda tipe) : 8
- OCR/ANGKA (token mengandung digit) : 5
- HONORIFIK (gold=O, harus ikut PERSON) : 3
- AMBIGU_LOC_EVENT (lihat worksheet terpisah) : 3

> Kolom `penyebab_usulan` = tebakan otomatis. Keputusan final diisi manual di `gold_audit.csv` (kolom `keputusan` + `koreksi`).

Kategori penyebab (rujuk `docs/anotasi_guideline.md`):
- **HONORIFIK** — gold=O, harusnya ikut PERSON (§1.2).
- **ANOTASI_KELEWAT** — regex tak menangkap entitas (gold FN).
- **AMBIGU_LOC_EVENT** — lihat worksheet `location_event_review`.
- **OCR/ANGKA** — artefak OCR / token angka (§6).
- **SALAH_TIPE** — tipe gold keliru.
- **MODEL_MISS / gold KELEBIHAN** — perlu cek: gold benar atau model salah.
