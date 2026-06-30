# Pedoman Anotasi Entitas (Gold Data NER) — Sirah Nabawiyah

> Dokumen ini mengunci **keputusan anotasi** untuk gold data NER proyek.
> Tujuannya: setiap label di `sirah_prelabelled.csv` bisa dipertanggungjawabkan
> secara konsisten (penting untuk sidang). Semua aturan di sini diterapkan lewat
> `src/manual_labelling/pre_labelling.py` (otomatis) + satu pass review manual
> (untuk kasus ambigu kontekstual).
>
> Status: **draft kerja** untuk putaran perbaikan gold (revisi Bu Dini Adni,
> Juni 2026). Sumber teks: Mubarakfuri, terjemahan Kathur Suhardi.

---

## 0. Ruang lingkup & skema

- **4 tipe entitas:** `PERSON`, `EVENT`, `LOCATION`, `TIME`.
- **Skema token:** BIO (`B-`, `I-`, `O`). Konversi span → BIO dilakukan otomatis
  oleh `prepare_bert_data.py`; **jangan edit BIO tangan** — perbaiki di level
  span (`sirah_prelabelled.csv`), lalu regenerasi.
- **Sumber kebenaran (single source of truth):** `sirah_prelabelled.csv`
  (satu baris per entitas, dengan `start_char`/`end_char`).

### Prinsip umum boundary span
1. Span memuat **nama entitas itu sendiri**, tanpa kata fungsi di luar nama
   (preposisi/artikel Indonesia: "di", "ke", "dari", "sang") **kecuali** kata itu
   memang bagian baku nama (mis. "Gua Hira", "Bukit Shafa", "Jazirah Arab").
2. **Tanda baca yang menempel akibat OCR ikut dibersihkan** dari boundary (lihat §6).
3. Bila dua entitas tumpang-tindih, ambil **span terpanjang/terspesifik**
   (mis. "Perang Badr" sebagai EVENT mengalahkan "Badr" sebagai LOCATION).

---

## 1. PERSON

Mencakup **individu** (Muhammad, Abu Bakar) **dan nama kabilah/Bani**
(Bani Quraizhah, Bani Nadhir) — sesuai kesepakatan proyek.

### 1.1 Nama dengan nasab
Nama Arab dengan rantai nasab di-anotasi **utuh sampai ujung rantai**:
- "Ali bin Abu Thalib" → satu PERSON (bukan "Ali" saja).
- "Abdullah bin Ubay bin Salul" → satu PERSON utuh.
- Nama terpotong akibat batas chunk/OCR ("Ka'b bin Al-") di-extend bila lanjutannya
  ada di teks (ditangani `_EXTEND_RE` di kode).

### 1.2 Honorifik / gelar → **DIMASUKKAN ke span PERSON** (keputusan proyek)
Keputusan: frasa honorifik yang **menempel langsung** setelah nama tokoh
dimasukkan sebagai bagian entitas PERSON (lanjut sebagai `I-PERSON`).
- "Muhammad Shallallahu Alaihi wa Sallam" → **satu** PERSON utuh.
- "...Umar Radhiyallahu Anhu..." → "Umar Radhiyallahu Anhu" satu PERSON.

Honorifik yang dicakup (semua variasi ejaan & kapital):
`Shallallahu Alaihi wa Sallam`, `Alaihissalam` / `Alaihis Salam`,
`Radhiyallahu Anhu/Anha/Anhuma`, `Rahimahullah`.

> ⚠️ **Catatan kejujuran (untuk Bab 4 & sidang):** dalam korpus ini honorifik
> **tertulis penuh sangat langka** (≈2–3 kemunculan di 1.094 chunk; terjemahan
> Kathur Suhardi memakai "Rasulullah"/"Nabi"/"beliau" alih-alih menuliskan
> honorifik). Jadi aturan ini **konsistensi, bukan penggerak skor** — dampaknya
> ke F1 dapat diabaikan. Tetap didokumentasikan agar skema anotasi koheren.
> Konvensi NER umum justru **mengecualikan** honorifik; pilihan memasukkannya di
> sini adalah keputusan proyek yang disengaja dan harus disebut eksplisit.

### 1.3 Yang BUKAN PERSON
- Kata ganti / sebutan generik tanpa nama: "beliau", "Nabi" (tanpa nama),
  "Rasul" berdiri sendiri → **O** (kecuali "Rasulullah" sebagai sebutan baku Nabi
  = PERSON, sesuai list).
- "Allah" dan asma-Nya → **O** (di luar 4 tipe entitas proyek).

---

## 2. EVENT

Peristiwa bersejarah: perang, perjanjian, baiat, hijrah, penaklukan, isra mi'raj,
peristiwa siklus hidup Nabi.

### 2.1 Pola "Perang/Ghazwah X"
- "Perang Badr", "Perang Uhud", "Ghazwah ..." → EVENT utuh (termasuk kata
  "Perang"/"Ghazwah").

### 2.2 Kapitalisasi **bukan** penentu (perbaikan isu gold)
Isu lama: gold semi-auto mengandalkan kapital, sehingga `Perang` (kapital)→EVENT
tapi `perang` (huruf kecil)→O. **Keputusan: huruf besar/kecil tidak menentukan.**
- "perang Bani Quraizhah", "perang Mu'tah" (huruf kecil) → tetap EVENT.
- Diterapkan via perluasan regex EVENT agar case-insensitive pada kata pemicu
  ("perang"/"ghazwah"), bukan via patch terpisah.

### 2.3 Nama medan-perang berdiri sendiri → **kontekstual** (LOCATION vs EVENT)
"Badr", "Uhud", "Khaibar", "Hudaibiyah", "Tabuk", "Khandaq", "Hunain" tanpa kata
"Perang" di depan **ambigu** dan tidak bisa diputuskan regex. Aturan:
- **EVENT** bila kalimat menunjuk peristiwanya: "sepulang dari Badr",
  "kemenangan di Uhud", "pasca Hudaibiyah", "korban Uhud".
- **LOCATION** bila menunjuk tempat fisik: "menuju Badr", "tiba di Badr",
  "wadi/sumur Badr", "penduduk Khaibar", "benteng Khaibar".

Disambiguasi dilakukan **manual** lewat worksheet
`data/result/manual_labelling/gold_review/location_event_review.md`
(146 kandidat). Default regex saat ini = LOCATION; review menaikkan sebagian
ke EVENT.

### 2.4 Peristiwa siklus hidup tanpa kata pemicu
Peristiwa seperti "wafatnya Nabi", "turunnya wahyu pertama", "kelahiran Nabi"
sering muncul sebagai **frasa verba/deskriptif**, bukan nama-baku → **sulit/ tidak
ditangkap NER**. Untuk gold, anotasi hanya bila ada **nama-baku peristiwa**;
event siklus-hidup ditangani terpisah di tahap konstruksi KG (enrichment), dan
keterbatasan ini **disebut eksplisit** di Bab 4 (bukan diklaim hasil NER murni).

---

## 3. LOCATION

Tempat fisik: kota, wilayah, landmark, gua, bukit, sumur, pasar, sungai.
- Nama majemuk baku diambil utuh: "Gua Hira", "Bukit Shafa", "Masjidil Haram",
  "Jazirah Arab", "Baitul Maqdis".
- Nama medan-perang default LOCATION, **kecuali** konteks = peristiwa (§2.3).

---

## 4. TIME

Penanda waktu: tahun (Hijriah/Masehi/nubuwah/SM), tanggal, bulan Hijriah,
hari, periode relatif.
- "tahun ke-10 kenabian", "bulan Ramadhan", "tanggal 17 Ramadhan",
  "3 tahun setelah hijrah", "hari Senin", "Lailatul Qadr".
- Span memuat seluruh frasa waktu, termasuk kata "tahun"/"bulan"/"tanggal"/"hari"
  sebagai pembuka frasa (sesuai pola `_TIME_PATTERNS`).

---

## 5. Daftar entitas false-positive yang harus dijaga (guard)

Berdasarkan inspeksi gold saat ini:
- **"Badr" → PERSON (2×)** = SALAH (artefak pattern `bin/binti`). Harus di-guard:
  nama medan-perang tidak boleh jadi PERSON.
- Kata pembuka kalimat berkapital ("Kemudian", "Maka", "Setelah", dst.) yang
  lolos sebagai nama → sudah ditangani `_INDO_STOPWORDS`, pertahankan & perluas
  bila ditemukan kasus baru.

---

## 6. Artefak OCR & boundary

OCR sering menempelkan tanda baca atau memecah kata. Berdasarkan hitungan di
seluruh korpus (184.649 token), artefak dibagi 3 tingkat penanganan:

### Tingkat 1 — Tanda baca menempel ✅ DIPERBAIKI (sistematis, token-level)
**≈25.807 token (14%)** punya tanda baca menempel ("Babilonia.", "Madinah,",
"Uhud:"). Ini biang utama "boundary error". Diperbaiki di **tokenisasi**
(`prepare_bert_data.py` → `_split_punct`): tanda baca pembuka/penutup dipisah jadi
token sendiri (otomatis berlabel O), inti kata tetap memegang label entitas.
Apostrof (') & hyphen (-) **tidak** dipisah karena bagian internal nama Arab
(Ka'b, Isra', Al-Khaththab). Offset karakter dijaga presisi → pencocokan span
gold tetap benar.

### Tingkat 2 — Nama terbelah pasca-hyphen ✅ DIPERBAIKI (aturan tertarget)
Nama yang terpecah spasi setelah hyphen ("Baitul- Haram", "An- Nu'man")
disatukan kembali (`prepare_bert_data.py` → `_merge_arabic_splits`): token
berakhiran "-" berawal huruf besar + token berikutnya huruf besar → digabung.
Kata-ulang Indonesia huruf kecil ("orang-" + "orang") **tidak** ikut tergabung.
Jumlah kecil (artikel standalone ≈37, token berakhir "-" ≈351 yg mayoritas
justru kata-ulang).

### Tingkat 3 — Ekor panjang OCR ⚠️ TIDAK diperbaiki (limitasi terdokumentasi)
Sisa artefak yang **langka** dan tidak bisa dibetulkan andal oleh aturan:
- **Kata nempel** (spasi hilang): "SyaikhAbdullah", "firmanAllah", "riwayatAbu"
  — **≈46 token (0,02%)**.
- **Apostrof hilang**: "Fir'aun" → "Fir Aun" — sangat langka.
- **Kata-ulang kepotong**: "orang-" + "orang" yang tidak tersambung.

**Keputusan:** dibiarkan sebagai **limitasi OCR sisa** dan disebut eksplisit di
Bab 4. Alasan: total <0,3% token, tersebar, dan tidak menggerakkan F1 secara
berarti; mengoreksi teks OCR sumber secara menyeluruh berisiko tinggi dengan
ROI rendah. Tidak dibuat kamus koreksi (keputusan 2026-06-28).

### Lain-lain
- **Kutip unicode** (' ' " ") dinormalisasi ke ASCII sebelum matching di
  `pre_labelling.py` (`_normalize_quotes`).

> Konsekuensi: Tingkat 1 mengubah **jumlah token** seluruh dataset → train/test/
> unlabelled wajib diregenerasi, dan ini bagian dari "run dari awal".

---

## 7. Alur kerja perbaikan gold (ringkas)

```
1. Edit aturan sistematis  -> pre_labelling.py  (honorifik, guard FP, kapitalisasi, OCR)
2. Review manual ambigu    -> location_event_review.csv  (isi kolom `keputusan`)
3. Apply review            -> apply_location_event_review.py
4. Regenerasi BIO          -> prepare_bert_data.py  (train/test baru, RANDOM_STATE=42)
5. Regenerasi turunan      -> augmentasi + class_weights
6. Re-run skenario (GPU)   -> S1/S2/S3 grup A/B/C
7. Re-eval + update buku   -> seqeval, ganti angka Bab 4 (tandai angka lama USANG)
```

> **Konsekuensi yang disadari:** karena **test set ikut diperbaiki**, seluruh F1
> lama (0,9537 dst.) menjadi **USANG** dan tidak apple-to-apple dengan hasil baru.
> Semua skenario wajib di-run ulang agar perbandingan adil.

---

## 8. Log keputusan (diperbarui saat ada kasus baru)

| Tanggal | Keputusan | Alasan |
|---|---|---|
| 2026-06-28 | Honorifik masuk span PERSON | Keputusan proyek (konsistensi); dampak F1 ≈ nol krn langka |
| 2026-06-28 | Kapitalisasi bukan penentu EVENT | "perang" huruf kecil tetap EVENT; memperbaiki bias gold |
| 2026-06-28 | Medan-perang standalone = kontekstual | Review manual 146 kandidat (LOCATION↔EVENT) |
| 2026-06-28 | "Badr"/medan-perang ≠ PERSON | Guard FP pattern nasab |
| 2026-06-28 | Test ikut diperbaiki → re-benchmark | Arahan Bu Dini Adni "run dari awal" |
| 2026-06-28 | OCR Tingkat 1 (tanda baca) dipisah di tokenisasi | 14% token; biang boundary error; fix aman & reproducible |
| 2026-06-28 | OCR Tingkat 2 (nama pasca-hyphen) digabung | "Baitul- Haram"→"Baitul-Haram"; set kecil |
| 2026-06-28 | OCR Tingkat 3 (kata-nempel dll) → limitasi | <0,3% token, ROI rendah; tanpa kamus koreksi |
