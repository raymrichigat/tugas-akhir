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

**Tidak.** Berdasarkan literatur *imbalanced learning* di NLP:

- **Tidak ada ambang universal** yang menyatakan sebuah dataset sudah "seimbang". Ketimpangan
  bersifat gradual: makin besar *Imbalance Ratio* (IR, rasio jumlah kelas mayoritas terhadap
  minoritas), makin besar kecenderungan performa kelas minoritas menurun. Henning dkk. (2023)
  menegaskan bahwa ketimpangan kelas merupakan masalah umum pada tugas NLP, termasuk klasifikasi
  token seperti NER, yang menurunkan kinerja pada kelas minoritas dan biasanya ditangani melalui
  penyesuaian data atau fungsi kerugian.
- Secara deskriptif rasio dapat digambarkan dari ringan hingga berat, tetapi ini istilah umum,
  **bukan standar baku berambang tetap**. Yang dapat dinyatakan secara faktual: augmentasi
  **menurunkan** rasio PERSON:EVENT dari **≈17,4:1 menjadi ≈8,8:1** — berkurang cukup jauh, tetapi
  **masih jauh dari seimbang (≈1:1)**.

Maka kesimpulan yang dipakai di buku **diperbaiki** menjadi:

> **"Data augmentation berhasil menurunkan tingkat ketimpangan kelas (rasio PERSON:EVENT dari
> ≈17,4:1 menjadi ≈8,8:1), meskipun distribusi antarkelas belum seimbang."**

Tiga hal dibedakan eksplisit: (1) **jumlah data bertambah**; (2) **rasio ketimpangan berkurang**
(inilah yang dicapai); (3) **kondisi benar-benar seimbang (≈1:1) tidak tercapai**.

> 🔎 **Sitasi (recent, dalam 5 tahun):** Henning, S., Beluch, W., Fraser, A., & Friedrich, A.
> (2023). *A Survey of Methods for Addressing Class Imbalance in Deep-Learning Based Natural
> Language Processing.* Proceedings of EACL 2023 (`aclanthology.org/2023.eacl-main.38`; arXiv
> 2210.04675). **Menggantikan López dkk. (2013)** yang di luar 5 tahun. Catatan jujur: **jangan**
> menuliskan ambang numerik low/moderate/high (≤2 / 2–9 / >9) sebagai standar berkutip — itu
> konvensi deskriptif, bukan definisi baku, dan tidak perlu diklaim bersumber.

### "Menangani" ketimpangan ≠ "menyeimbangkan" (dukungan literatur, ≤5 tahun)

Penanganan ketimpangan kelas **tidak bertujuan menyamakan jumlah antarkelas menjadi 1:1**,
melainkan mengurangi kecenderungan model memihak kelas mayoritas dan **meningkatkan kinerja kelas
minoritas**. Henning dkk. (2023) menyatakan bahwa model NLP cenderung berkinerja buruk pada kelas
yang jarang muncul, dan augmentasi data merupakan salah satu metode untuk menangani ketimpangan
tersebut yang bahkan sering memberi peningkatan **lebih besar** dibanding penyeimbangan ulang
(resampling) atau modifikasi fungsi kerugian. Khusus pada NER yang berdistribusi *long-tail*,
Nemoto dkk. (2024) menegaskan bahwa keberhasilan penanganan ketimpangan diukur dari **peningkatan
kinerja kelas minoritas tanpa mengorbankan kelas mayoritas**.

Sejalan dengan itu, augmentasi pada penelitian ini meningkatkan F1 kelas minoritas (**TIME 0,80 →
0,90; EVENT 0,93 → 0,95**) sekaligus tetap menjaga kelas mayoritas (PERSON 0,97 → 0,98). Maka
augmentasi **dapat dinyatakan menangani ketimpangan kelas**, meskipun distribusi antarkelas belum
seimbang. Klaim yang tepat: *"menangani/mengurangi ketimpangan"* (didukung peningkatan minoritas),
**bukan** *"menyeimbangkan data"*.

> Catatan: temuan Henning dkk. (2023) bahwa augmentasi cenderung unggul dibanding resampling/loss
> **selaras dengan hasil penelitian ini** — augmentasi menjadi skenario pemenang di atas
> weighted-CE dan contrastive (SCL/JSCL).

**Rujukan (verifikasi sebelum Daftar Pustaka):**
- Henning, S., Beluch, W., Fraser, A., & Friedrich, A. (2023). *A Survey of Methods for Addressing
  Class Imbalance in Deep-Learning Based Natural Language Processing.* Proceedings of EACL 2023
  (`aclanthology.org/2023.eacl-main.38`; arXiv 2210.04675).
- Nemoto, S., Kitada, S., & Iyatomi, H. (2024). *Majority or Minority: Data Imbalance Learning
  Method for Named Entity Recognition.* arXiv:2401.11431 (juga terbit di IEEE, `IEEE Xplore
  10816423` — cek nama jurnal & tahun terbit final di IEEE).

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
