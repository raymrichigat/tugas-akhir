# Koreksi: "IndoBERT cased" adalah Misnomer (model sebenarnya UNCASED)

> Draf koreksi untuk direview sebelum diterapkan ke Bab 2/4/5. **Angka hasil TIDAK berubah** —
> yang dikoreksi hanya (a) label model dan (b) satu kalimat penjelasan yang salah faktual.
> Dibuat 2026-07-20 setelah penelusuran run + verifikasi model card.

## 1. Bukti (definitif, dari run sendiri)

| Bukti | Isi |
|---|---|
| Folder/notebook skenario | `done_newest/indobert-base-p1/notebook/srl_ner_sirah_GrupB_cased_colab.ipynb` |
| Model yang di-load di notebook | `AutoTokenizer/AutoModel.from_pretrained("indobenchmark/indobert-base-p1")` |
| Model card HuggingFace | judul: *"IndoBERT Base Model (phase1 - **uncased**)"* |
| `tokenizer_config.json` (base + semua 6 iterasi) | **`"do_lower_case": true`** |
| Baseline pembanding (indolem) | `"do_lower_case": true` (juga uncased) |

**Kesimpulan:** skenario yang di buku disebut **"IndoBERT cased"** sebenarnya menjalankan
`indobenchmark/indobert-base-p1`, sebuah model **uncased** yang **me-lowercase masukan**
(`do_lower_case=true`). Model ini **tidak mempertahankan kapitalisasi**. Baik baseline maupun
skenario ini sama-sama uncased; perbedaannya ada pada **checkpoint/vocabulary IndoBERT**
(indolem vs indobenchmark), **bukan** pada casing.

## 2. Dampak

- Anomali kinerjanya **NYATA** (F1 mikro 0,7774; F1 Person 0,7843; batas B/I melonjak) — angka tetap.
- Yang **salah** hanya: (a) **label** "IndoBERT cased"; (b) **satu kalimat** yang menyebut
  penyebabnya "mempertahankan kapitalisasi".
- Penjelasan **RoBERTa** (byte-level BPE) **tetap valid** — RoBERTa memang beda tokenisasi.
- Sisa narasi §4.3 sudah aman (sudah menyebut "penyelarasan label subword", "belum pasti").

## 3. Istilah pengganti yang disarankan

**"IndoBERT cased" → "IndoBERT phase-1"** (rujuk `indobenchmark/indobert-base-p1`; konsisten
dengan Tabel 2.4 yang sudah menyebutnya "IndoBERT phase 1"). Alternatif: "IndoBERT IndoBenchmark".

## 4. Perbaikan per lokasi (before → after)

### 4.1 Kalimat yang SALAH FAKTUAL — WAJIB (Bab 4 §4.3, dekat Tabel 4.13)

**Before:**
> IndoBERT cased menggunakan tokenisasi WordPiece dengan mempertahankan kapitalisasi, sedangkan
> RoBERTa menggunakan byte-level byte pair encoding.

**After:**
> IndoBERT phase-1 menggunakan tokenizer WordPiece dengan vocabulary yang berbeda dari IndoBERT
> uncased yang menjadi baseline; keduanya sama-sama uncased dan me-lowercase masukan
> (`do_lower_case` aktif), sehingga perbedaannya terletak pada vocabulary antar-checkpoint, bukan
> pada perlakuan kapitalisasi. Sementara itu, RoBERTa menggunakan byte-level byte pair encoding.

### 4.2 Tambahan klarifikasi (disarankan) — 1 kalimat di §4.3 setelah kalimat "…tidak langsung ditafsirkan bahwa model cased dan RoBERTa secara umum kurang sesuai…"

**Sisipkan:**
> Perlu dicatat bahwa IndoBERT phase-1 tetap merupakan model uncased, sehingga rendahnya
> kinerjanya tidak disebabkan oleh perlakuan kapitalisasi, melainkan diduga berkaitan dengan
> perbedaan vocabulary/tokenizer antar-checkpoint dan penyelarasan label pada tingkat subword.

### 4.3 Rename label (mekanis, tidak mengubah makna)

Ganti **"IndoBERT cased" → "IndoBERT phase-1"** dan **"IndoBERT Cased" → "IndoBERT phase-1"**
di seluruh kemunculan:

- Bab 4 §4.3: kalimat pengantar (daftar 5 model), Tabel 4.10, Tabel 4.11, Tabel 4.12, narasi
  Gambar 4.7–4.11, judul **Tabel 4.13** ("…pada IndoBERT Cased…"), judul **Gambar 4.11**
  ("Confusion Matrix IndoBERT Cased").
- Bab 5 butir 4: "IndoBERT cased dan RoBERTa" → "IndoBERT phase-1 dan RoBERTa".
- Bab 2 Tabel 2.4: **tidak perlu diubah** (sudah memakai nama asli `indobenchmark/indobert-base-p1`
  / "IndoBERT phase 1"). Teori cased/uncased di §2.4.2 juga **tetap** (konsep umum, benar).

Perkiraan: ±27 kemunculan "IndoBERT cased" di Bab 4/5.

## 5. Catatan integritas

Ini mengoreksi **kesalahan faktual pada pembahasan hasil skripsi yang sudah disidangkan**.
Angka dan kesimpulan besar (IndoBERT uncased = terbaik 0,9536; augmentasi = winner 0,9756) **tidak
berubah**. Namun karena menyentuh interpretasi hasil, sebaiknya **diinformasikan ke Bu Dini/Bu
Ratih** sebelum finalisasi. Konsisten dengan catatan analisis sebelumnya: defisit "cased/RoBERTa"
sudah ada sejak checkpoint awal (bukan efek self-training) dan terkonsentrasi di kesalahan batas
PERSON banyak-kata — sejalan dengan penyebab tokenizer/vocabulary, bukan kapitalisasi.
