# Artefak Revisi Sidang — Augmentasi: Metode, Contoh, dan Distribusi Kelas

> Menjawab **Dosen-1 poin 6** (augmentasi menghasilkan data tambahan + contoh sebelum/sesudah
> paraphrasing & mention replacement + distribusi kelas) dan **poin 7** (perbaiki klaim
> "menyeimbangkan kelas"). Semua angka & contoh **dari data nyata** yang melatih model pemenang:
> `train.csv` → `train_augmented_final.csv` (file yang benar-benar di-load notebook `done_newest`).

---

## 1. Metode augmentasi yang dipakai (dua teknik)

Penelitian ini memakai **dua teknik augmentasi**:

1. **Mention replacement** (utama, 288 varian) — mengganti mention entitas kelas minoritas
   dengan mention lain bertipe sama dari daftar kandidat; label BIO dipertahankan.
2. **Paraphrasing** (pelengkap, 6 varian) — memparafrasekan kalimat dengan LLM, label
   di-align ulang ke hasil parafrase.

Komposisi data latih akhir (`train_augmented_final.csv`): **590 chunk asli + 288 mention
replacement + 6 paraphrase = 884 chunk**.

**Konfigurasi mention replacement (dari `augmentation_log_v2.json`):**

| Parameter | Nilai | Arti |
|---|---|---|
| `n_augment` | 2 | tiap kalimat sumber → hingga 2 varian |
| `replace_prob` | 0,7 | peluang tiap mention minoritas diganti |
| `minor_labels` | `B-EVENT`, `I-EVENT`, `I-LOCATION` | kelas target |
| `seed` | 42 | reprodusibilitas |

**Kelas target augmentasi = EVENT dan LOCATION** (paling minoritas), sesuai hipotesis
pembimbing bahwa augmentasi diarahkan untuk menutup celah kelas minoritas. Pada paraphrasing,
seluruh mention entitas dipertahankan persis sehingga label BIO tetap valid.

---

## 2. Contoh teks sebelum & sesudah augmentasi

### 2a. Mention replacement (nyata, `chunk asli` → varian `-aug1`)

**Contoh A — mention EVENT** (`chunk 000351-002`):

| | Teks |
|---|---|
| Sebelum | "Tetapi setelah **Perang Tabuk** ini, pengiriman utusan kepada beliau lebih intens …" |
| Sesudah | "Tetapi setelah **Perang Uhud** ini, pengiriman utusan kepada beliau lebih intens …" |

`Tabuk` (`I-EVENT`) → `Uhud` (`I-EVENT`) — struktur & label tetap, identitas peristiwa bervariasi.

**Contoh B — mention LOCATION** (`chunk 000012-001`):

| | Teks |
|---|---|
| Sebelum | "… kondisi politik dan agama di **Jazirah Arab**, kini kita akan membahas …" |
| Sesudah | "… kondisi politik dan agama di **Syam**, kini kita akan membahas …" |

`Jazirah Arab` (`B-LOCATION I-LOCATION`) → `Syam` (`B-LOCATION`).

### 2b. Paraphrasing (nyata, `chunk 000358-005` → `_para1`)

| | Teks |
|---|---|
| Sebelum | "Sekalipun di sana ada agama samawi, tetapi agama ini sudah kehilangan taringnya, tidak lagi mempunyai kekuasaan, sudah tersusupi penyimpangan dan pengubahan, sehingga yang menyisa hanya upacara-upacara yang kaku tanpa memiliki kehidupan ruh …" |
| Sesudah | "Sekalipun di sana terdapat agama samawi, agama itu telah kehilangan kekuatannya, tak lagi memiliki kuasa, dan telah tercemar oleh penyimpangan serta pengubahan, sehingga yang tersisa hanyalah upacara kaku tanpa ruh kehidupan …" |

> Struktur kalimat diparafrasekan (pilihan kata & susunan diubah) sementara entitas `Jazirah
> Arab` (LOCATION) tetap dipertahankan, sehingga label BIO pada hasil parafrase tetap sesuai.

---

## 3. Distribusi kelas sebelum vs sesudah augmentasi

Dari `train.csv` (sebelum) dan `train_augmented_final.csv` (sesudah). Jumlah = token entitas (B+I).

| Kelas entitas | Sebelum | Sesudah | Perubahan |
|---|---:|---:|---:|
| PERSON (mayoritas) | 5.519 | 8.311 | +51 % |
| LOCATION | 1.038 | 1.875 | +81 % |
| TIME | 664 | 1.107 | +67 % |
| EVENT (paling minoritas) | 317 | 943 | **+197 %** |
| O (bukan entitas) | 108.815 | 163.352 | +50 % |

**Gambar:** `data/result/analysis/bab4_viz/augmentasi_distribusi_revisi.png`.

---

## 4. Perbaikan klaim: "mengurangi ketimpangan", bukan "menyeimbangkan" (Dosen-1 #7)

Rasio ketimpangan mayoritas–minoritas terparah (**PERSON : EVENT**):

| | Rasio PERSON : EVENT |
|---|---|
| Sebelum augmentasi | ≈ **17,4 : 1** |
| Sesudah augmentasi | ≈ **8,8 : 1** |

### Apakah 8,8:1 sudah "tidak imbalance"? (jawaban berbasis literatur)

**Tidak.** Berdasarkan literatur *imbalanced learning*:

- **Tidak ada ambang universal.** Konvensi yang lazim dipakai: dataset dianggap imbalanced bila
  *Imbalance Ratio* (IR) **> 1,5** — di atas nilai ini performa kelas minoritas biasanya menurun
  signifikan (banyak studi memakai IR 1,5 sebagai batas seleksi dataset imbalanced).
- Sebagian kajian mengkategorikan: **IR rendah ≤ 2, sedang 2–9, tinggi > 9**. Dengan skema ini,
  augmentasi memindahkan dataset dari **ketimpangan tinggi (17,4:1)** ke **ketimpangan sedang
  (8,8:1)** — **masih imbalanced**, jauh dari seimbang (≈1:1).

Maka kesimpulan yang dipakai di buku **diperbaiki** menjadi:

> **"Data augmentation berhasil menurunkan tingkat ketimpangan kelas dari kategori tinggi
> (rasio PERSON:EVENT ≈17,4:1) ke kategori sedang (≈8,8:1), meskipun distribusi antarkelas
> belum seimbang."**

Tiga hal dibedakan eksplisit: (1) **jumlah data bertambah**; (2) **rasio ketimpangan berkurang**
(inilah yang dicapai); (3) **kondisi benar-benar seimbang (≈1:1) tidak tercapai**.

> 🔎 **Untuk sitasi buku (perlu diverifikasi penulis proyek):** rujukan yang relevan & dapat
> diperiksa — López, Fernández, García dkk., *"An insight into classification with imbalanced
> data: Empirical results and current trends…"*, **Information Sciences (2013)**
> (`sci2s.ugr.es`). Ambang kategori low/moderate/high (≤2 / 2–9 / >9) muncul di beberapa kajian
> lebih baru — **pastikan sumber persisnya sebelum menuliskan angka ambang** agar tidak salah
> atribusi. Jangan menyalin ambang tanpa mengecek papernya langsung.

### Mengapa PERSON (mayoritas) ikut naik +51 %?

Target augmentasi adalah EVENT & LOCATION, tetapi **kalimat yang memuat entitas minoritas hampir
selalu juga memuat entitas PERSON**. Saat kalimat itu diduplikasi jadi varian augmentasi, entitas
PERSON di dalamnya **ikut terduplikasi** (efek samping). Karena itu kenaikan EVENT (+197 %) jauh
lebih tajam daripada PERSON (+51 %) — rasio ketimpangan tetap membaik walau jumlah absolut
mayoritas juga naik.

---

### Sumber data (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Data latih sebelum augmentasi | `data/result/pseudo-labelling/SRL-NER/train.csv` |
| Data latih sesudah augmentasi (FINAL, melatih model) | `…/training_bundle_corrected_gold_20260704/train_augmented_final/train_augmented_final.csv` |
| Log augmentasi (config + distribusi) | `data/result/pseudo-labelling/SRL-NER/augmentation_log_v2.json` |
| Skrip chart distribusi | `src/analysis/augmentasi_distribusi_revisi.py` |
