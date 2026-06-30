# Analisis Error NER Berbasis Data — `done_running`

> Sumber: file `*-incorrect.xlsx` (error token-level pada test set) tiap skenario + `test.csv` (42,558 token, 258 chunk). Skor entity-level (seqeval) ada di `seqeval_grupB_results.md`; di sini fokus **mengapa** error terjadi.

**Catatan iterasi:** file error disimpan pada iterasi terakhir tiap skenario (SCL & POS-tag = iter-4, sisanya iter-6). Kategori error bersifat token-level (BIO), sedangkan F1 ringkasan bersifat entity-level, jadi angka absolut bisa beda tipis tapi pola error konsisten.


## S1-baseline  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **192**
- FP (over-deteksi, gold=O): **86** (45%)
- FN (entitas terlewat, pred=O): **91** (47%)
- Misklasifikasi tipe (entitas, tipe salah): **11** (6%)
- Boundary B/I (tipe benar, batas salah): **4** (2%)

- FN per kelas: {'LOCATION': 23, 'PERSON': 45, 'TIME': 12, 'EVENT': 11}
- FP per kelas (label prediksi): {'PERSON': 53, 'TIME': 17, 'LOCATION': 14, 'EVENT': 2}
- Pasangan misklasifikasi: {'PERSON->EVENT': 1, 'LOCATION->EVENT': 3, 'EVENT->LOCATION': 4, 'LOCATION->PERSON': 2, 'EVENT->PERSON': 1}

## S2-weighted-CE  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **232**
- FP (over-deteksi, gold=O): **150** (65%)
- FN (entitas terlewat, pred=O): **67** (29%)
- Misklasifikasi tipe (entitas, tipe salah): **10** (4%)
- Boundary B/I (tipe benar, batas salah): **5** (2%)

- FN per kelas: {'LOCATION': 21, 'TIME': 11, 'PERSON': 24, 'EVENT': 11}
- FP per kelas (label prediksi): {'LOCATION': 35, 'PERSON': 90, 'TIME': 24, 'EVENT': 1}
- Pasangan misklasifikasi: {'LOCATION->EVENT': 3, 'EVENT->LOCATION': 4, 'PERSON->EVENT': 1, 'PERSON->LOCATION': 1, 'EVENT->PERSON': 1}

## S2a-SCL  (`bert-only-sirah-ner-S2a-scl-iterative-4-incorrect.xlsx`)

- Total token error: **197**
- FP (over-deteksi, gold=O): **118** (60%)
- FN (entitas terlewat, pred=O): **63** (32%)
- Misklasifikasi tipe (entitas, tipe salah): **9** (5%)
- Boundary B/I (tipe benar, batas salah): **7** (4%)

- FN per kelas: {'TIME': 9, 'PERSON': 28, 'LOCATION': 15, 'EVENT': 11}
- FP per kelas (label prediksi): {'PERSON': 69, 'LOCATION': 26, 'TIME': 22, 'EVENT': 1}
- Pasangan misklasifikasi: {'LOCATION->EVENT': 2, 'EVENT->LOCATION': 3, 'PERSON->LOCATION': 1, 'LOCATION->PERSON': 2, 'EVENT->PERSON': 1}

## S2b-JSCL  (`bert-only-sirah-ner-S2b-jscl-iterative-6-incorrect.xlsx`)

- Total token error: **212**
- FP (over-deteksi, gold=O): **120** (57%)
- FN (entitas terlewat, pred=O): **75** (35%)
- Misklasifikasi tipe (entitas, tipe salah): **10** (5%)
- Boundary B/I (tipe benar, batas salah): **7** (3%)

- FN per kelas: {'LOCATION': 19, 'TIME': 12, 'PERSON': 34, 'EVENT': 10}
- FP per kelas (label prediksi): {'PERSON': 72, 'LOCATION': 30, 'TIME': 17, 'EVENT': 1}
- Pasangan misklasifikasi: {'LOCATION->EVENT': 2, 'EVENT->LOCATION': 5, 'LOCATION->PERSON': 2, 'EVENT->PERSON': 1}

## S4-augmentation  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **166**
- FP (over-deteksi, gold=O): **86** (52%)
- FN (entitas terlewat, pred=O): **69** (42%)
- Misklasifikasi tipe (entitas, tipe salah): **4** (2%)
- Boundary B/I (tipe benar, batas salah): **7** (4%)

- FN per kelas: {'LOCATION': 13, 'PERSON': 34, 'TIME': 14, 'EVENT': 8}
- FP per kelas (label prediksi): {'PERSON': 62, 'LOCATION': 15, 'TIME': 8, 'EVENT': 1}
- Pasangan misklasifikasi: {'LOCATION->EVENT': 2, 'LOCATION->PERSON': 2}

## S5-POS-tag  (`bert-pos-sirah-ner-iterative-4-incorrect.xlsx`)

- Total token error: **224**
- FP (over-deteksi, gold=O): **146** (65%)
- FN (entitas terlewat, pred=O): **62** (28%)
- Misklasifikasi tipe (entitas, tipe salah): **9** (4%)
- Boundary B/I (tipe benar, batas salah): **7** (3%)

- FN per kelas: {'LOCATION': 17, 'TIME': 10, 'PERSON': 25, 'EVENT': 10}
- FP per kelas (label prediksi): {'PERSON': 87, 'LOCATION': 30, 'TIME': 28, 'EVENT': 1}
- Pasangan misklasifikasi: {'EVENT->LOCATION': 4, 'LOCATION->EVENT': 1, 'PERSON->LOCATION': 1, 'LOCATION->PERSON': 2, 'EVENT->PERSON': 1}

## B-indobert-cased  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **721**
- FP (over-deteksi, gold=O): **322** (45%)
- FN (entitas terlewat, pred=O): **262** (36%)
- Misklasifikasi tipe (entitas, tipe salah): **37** (5%)
- Boundary B/I (tipe benar, batas salah): **100** (14%)
- Boundary B/I per kelas (gold): {'PERSON': 91, 'TIME': 9}  → 100% di kelas banyak-kata; LOCATION & EVENT = 0

- FN per kelas: {'LOCATION': 40, 'PERSON': 172, 'TIME': 31, 'EVENT': 19}
- FP per kelas (label prediksi): {'PERSON': 239, 'LOCATION': 20, 'TIME': 55, 'EVENT': 8}
- Pasangan misklasifikasi: {'PERSON->LOCATION': 8, 'LOCATION->EVENT': 7, 'TIME->PERSON': 3, 'EVENT->PERSON': 4, 'EVENT->LOCATION': 7, 'LOCATION->PERSON': 5, 'EVENT->TIME': 1, 'PERSON->TIME': 2}

## B-cahya-1.5G  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **243**
- FP (over-deteksi, gold=O): **144** (59%)
- FN (entitas terlewat, pred=O): **82** (34%)
- Misklasifikasi tipe (entitas, tipe salah): **10** (4%)
- Boundary B/I (tipe benar, batas salah): **7** (3%)

- FN per kelas: {'PERSON': 35, 'LOCATION': 24, 'TIME': 12, 'EVENT': 11}
- FP per kelas (label prediksi): {'PERSON': 96, 'LOCATION': 19, 'TIME': 26, 'EVENT': 3}
- Pasangan misklasifikasi: {'PERSON->EVENT': 1, 'EVENT->LOCATION': 5, 'LOCATION->EVENT': 2, 'PERSON->LOCATION': 1, 'EVENT->PERSON': 1}

## B-distilbert  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **216**
- FP (over-deteksi, gold=O): **142** (66%)
- FN (entitas terlewat, pred=O): **59** (27%)
- Misklasifikasi tipe (entitas, tipe salah): **11** (5%)
- Boundary B/I (tipe benar, batas salah): **4** (2%)

- FN per kelas: {'LOCATION': 18, 'TIME': 14, 'PERSON': 17, 'EVENT': 10}
- FP per kelas (label prediksi): {'PERSON': 90, 'LOCATION': 22, 'TIME': 29, 'EVENT': 1}
- Pasangan misklasifikasi: {'PERSON->EVENT': 1, 'LOCATION->EVENT': 2, 'EVENT->LOCATION': 4, 'PERSON->LOCATION': 1, 'LOCATION->PERSON': 2, 'EVENT->PERSON': 1}

## B-roberta  (`bert-only-sirah-ner-iterative-6-incorrect.xlsx`)

- Total token error: **641**
- FP (over-deteksi, gold=O): **260** (41%)
- FN (entitas terlewat, pred=O): **236** (37%)
- Misklasifikasi tipe (entitas, tipe salah): **43** (7%)
- Boundary B/I (tipe benar, batas salah): **102** (16%)
- Boundary B/I per kelas (gold): {'PERSON': 94, 'TIME': 8}  → 100% di kelas banyak-kata; LOCATION & EVENT = 0

- FN per kelas: {'LOCATION': 30, 'PERSON': 163, 'TIME': 27, 'EVENT': 16}
- FP per kelas (label prediksi): {'PERSON': 181, 'LOCATION': 24, 'TIME': 49, 'EVENT': 6}
- Pasangan misklasifikasi: {'TIME->PERSON': 4, 'PERSON->LOCATION': 5, 'PERSON->EVENT': 5, 'PERSON->TIME': 4, 'LOCATION->PERSON': 7, 'LOCATION->EVENT': 6, 'EVENT->LOCATION': 8, 'EVENT->PERSON': 3, 'LOCATION->TIME': 1}


# Ringkasan lintas skenario (token-level error)

| Skenario | Total err | FP | FN | Mis-tipe | Boundary |
|---|---:|---:|---:|---:|---:|
| S1-baseline | 192 | 86 | 91 | 11 | 4 |
| S2-weighted-CE | 232 | 150 | 67 | 10 | 5 |
| S2a-SCL | 197 | 118 | 63 | 9 | 7 |
| S2b-JSCL | 212 | 120 | 75 | 10 | 7 |
| S4-augmentation | 166 | 86 | 69 | 4 | 7 |
| S5-POS-tag | 224 | 146 | 62 | 9 | 7 |
| B-indobert-cased | 721 | 322 | 262 | 37 | 100 |
| B-cahya-1.5G | 243 | 144 | 82 | 10 | 7 |
| B-distilbert | 216 | 142 | 59 | 11 | 4 |
| B-roberta | 641 | 260 | 236 | 43 | 102 |

# FN & FP per kelas entitas (token-level)

| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |
|---|---|---|---|---|
| S1-baseline | 45/53 | 23/14 | 11/2 | 12/17 |
| S2-weighted-CE | 24/90 | 21/35 | 11/1 | 11/24 |
| S2a-SCL | 28/69 | 15/26 | 11/1 | 9/22 |
| S2b-JSCL | 34/72 | 19/30 | 10/1 | 12/17 |
| S4-augmentation | 34/62 | 13/15 | 8/1 | 14/8 |
| S5-POS-tag | 25/87 | 17/30 | 10/1 | 10/28 |
| B-indobert-cased | 172/239 | 40/20 | 19/8 | 31/55 |
| B-cahya-1.5G | 35/96 | 24/19 | 11/3 | 12/26 |
| B-distilbert | 17/90 | 18/22 | 10/1 | 14/29 |
| B-roberta | 163/181 | 30/24 | 16/6 | 27/49 |

# Efek kapitalisasi pada FP/FN (uji temuan 'Perang' vs 'perang')

- **S1-baseline**: 67% token FP berawalan huruf besar; 74% token FN berawalan huruf besar.
- **S4-augmentation**: 73% token FP berawalan huruf besar; 78% token FN berawalan huruf besar.
- **B-indobert-cased**: 75% token FP berawalan huruf besar; 82% token FN berawalan huruf besar.

**S4-augmentation** — token FP tersering: [('bin', 6), ('Ummul', 4), ('Fadhl', 4), ('bulan', 3), ('Abdul', 3), ('"', 2), ('Bahrain,', 2), ('Hajar', 2), ('Az-Zubair', 2), ('Shalallahu', 1)]
**S4-augmentation** — token FN tersering: [('Al-Abbas', 3), ('Bukhtanashar', 2), ('dari', 2), ('Abul', 2), ('"Muhammad', 2), ('Ghazwah', 2), ('622', 2), ('M,', 2), ('Umayyah.', 2), ('Khaibar', 2)]

**S1-baseline** — token FP tersering: [('bin', 6), ('bulan', 3), ('Abu', 2), ('H', 2), ('Abdul', 2), ('Ummul', 2), ('Fadhl', 2), ('Authas.', 2), ('Shalallahu', 1), ('Alaihi', 1)]
**S1-baseline** — token FN tersering: [('Bilal', 3), ('Baiat', 3), ('pertengahan', 2), ('hari-hari', 2), ('dari', 2), ('"Muhammad', 2), ('Ghazwah', 2), ('Umayyah.', 2), ('Bilal,', 2), ('Umayyah', 2)]

# Proxy dampak chunking: posisi token error dalam chunk

> Tidak ada ablation 'tanpa chunking' di eksperimen ini, jadi efek chunking diuji tak-langsung: apakah error memusat di **tepi chunk** (10% awal/akhir token) tempat konteks terpotong.

| Skenario | err di tepi chunk (%) | err di tengah (%) |
|---|---:|---:|
| S1-baseline | 23 | 77 |
| S2-weighted-CE | 22 | 78 |
| S2a-SCL | 22 | 78 |
| S2b-JSCL | 25 | 75 |
| S4-augmentation | 16 | 84 |
| S5-POS-tag | 21 | 79 |
| B-indobert-cased | 29 | 71 |
| B-cahya-1.5G | 21 | 79 |
| B-distilbert | 19 | 81 |
| B-roberta | 27 | 73 |

_(Catatan: pemetaan posisi pakai kemunculan pertama token dalam chunk; perkiraan, bukan presisi indeks.)_
---

# Analisis interpretatif (untuk Bab 4 pembahasan)

## A. Karakteristik error secara umum
Pada **semua** skenario uncased yang sehat (S1–S5, cahya, distilbert), error terbagi rata antara
**FP (over-deteksi, 45–66%)** dan **FN (terlewat, 27–47%)**, sedangkan **misklasifikasi tipe hanya 2–6%**
dan **boundary B/I hanya 2–4%**. Artinya: **model sudah memahami perbedaan 4 tipe entitas**;
masalah utamanya adalah **keputusan deteksi (entitas vs bukan)**, bukan kebingungan jenis entitas.

## B. Penyebab FP (over-deteksi) — berbasis data
1. **Frasa honorifik** yang menempel pada nama Nabi: `Shalallahu`/`Alaihi`/`wa`/`Sallam` diprediksi
   `B/I_PERSON` padahal gold = O. Pola ini berulang di semua skenario (contoh chunk `000010-002`).
   Model belajar "kata setelah Rasulullah = bagian nama".
2. **Penanda nasab** `bin`, `Abdul`, `Abu`, `Ummul`, `Fadhl` diprediksi PERSON di konteks non-nama.
3. **Kata waktu generik** (`bulan`, `nafar`, `hari`) diprediksi TIME → menjelaskan precision TIME terendah.

## C. Penyebab FN (terlewat) — berbasis data
1. **Nama langka / luar-distribusi**: `Bukhtanashar`, `As-Samhudi`, `Babilon`, `Babilonia` — muncul
   sangat jarang di korpus Sirah sehingga tak terpelajari (few-shot).
2. **Artefak OCR boundary**: **38% token FN pada skenario pemenang membawa tanda baca yang menempel**
   (`Babilonia.`, `Umayyah.`, `Hudaibiyah.`) → bentuk permukaan tak cocok dengan token bersih saat training.
3. **Kata waktu huruf kecil** (`pertengahan`, `malam`) = inkonsistensi gold (manual labelling semi-auto
   berbasis kapitalisasi). Token huruf-kecil sering di-gold O di tempat lain → model wajar tak mendeteksi.

## D. Misklasifikasi tipe — pasangan dominan LOCATION ↔ EVENT
Pasangan paling sering tertukar adalah **LOCATION ↔ EVENT** (7 dari 11 misklasifikasi baseline;
2 dari 4 pada augmentasi). Penyebab: **ambiguitas nama yang identik untuk tempat dan peristiwa** —
`Uhud`, `Badr`, `Hudaibiyah` adalah nama lokasi sekaligus nama perang. Contoh paling jelas
`...mengawali Perang Uhud Jabal Uhud...` di mana `Uhud` pertama (EVENT) dan kedua (LOCATION)
hanya dibedakan oleh kata kunci `Perang`/`Jabal`. Ini ambiguitas semantik nyata, bukan kelemahan model.

## E. Mengapa kelas minoritas (EVENT, TIME) lebih sering salah
Urutan F1 per kelas (EVENT < TIME < LOCATION < PERSON) **persis** mengikuti urutan jumlah data
(EVENT 51, TIME 74, LOCATION 449, PERSON 1189 entitas di test). Few-shot adalah faktor dominan.
Augmentasi (S4) menaikkan F1 EVENT 0.80→0.90 dan TIME 0.84→0.86 justru karena menambah contoh
sintetis kelas minoritas — FN EVENT turun (11→8) dan FP TIME turun drastis (17→8), bukti langsung
hipotesis "augmentasi menutup gap kelas minoritas".

## F. Anomali model cased (IndoBERT-cased) & RoBERTa
Kedua model ini **bukan sekadar 'lebih jelek'** — pola error-nya **berbeda struktural**:
- **Boundary B/I melonjak**: 100 (cased) & 102 (roberta) vs hanya 2–7 di model uncased.
- **PERSON FN meledak**: 172 (cased) & 163 (roberta) vs 17–45 di uncased.
Ini ciri **misalignment label B/I akibat skema subword berbeda** (RoBERTa BPE; IndoBERT-p1 cased
mem-split token berbeda dari uncased), bukan ketidakmampuan memahami entitas. **Kesimpulan jujur:
angka 0.777/0.807 belum bisa dipakai untuk menyimpulkan "cased lebih buruk" sebelum dicek alignment
B/I dan jumlah iterasi/base run** — konsisten dengan catatan PENDING di memori proyek.

## G. Dampak chunking
Tidak ada ablation "tanpa chunking" pada eksperimen ini, jadi klaim langsung tidak bisa dibuat.
Proxy posisi: **16–29% error berada di tepi chunk** (10% awal/akhir), sisanya di tengah — error
tidak terkonsentrasi ekstrem di batas chunk, jadi pemotongan konteks **bukan** penyebab error
utama. Yang lebih berpengaruh adalah karakteristik token (OCR, kapitalisasi, kelangkaan) di atas.
Untuk klaim kuat soal chunking, perlu eksperimen terpisah (mis. chunk overlap vs non-overlap) — saat
ini belum tersedia, dan ini sebaiknya ditandai sebagai keterbatasan.
