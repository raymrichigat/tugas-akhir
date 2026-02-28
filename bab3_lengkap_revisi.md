# BAB 3 METODOLOGI

## 3.1 Metode dan Alur Kerja

Penelitian ini bertujuan membangun basis data graf Sirah Nabawiyah berbasis Named-Entity Recognition dengan memanfaatkan teknik pemrosesan bahasa alami. Sistem yang dikembangkan terdiri dari beberapa tahapan: preparasi dataset dari dokumen Sirah Nabawiyah, preprocessing untuk membersihkan noise hasil OCR, chunking untuk membagi teks menjadi unit yang lebih kecil, manual labelling pada sebagian data sebagai seed dan ground truth, pseudo-labelling berbasis NER menggunakan dua skenario (SRL-based dan LLM-based), pembentukan relasi antar entitas, serta konstruksi knowledge graph di Neo4j. Tahap akhir berupa pengujian dan evaluasi untuk memvalidasi kualitas ekstraksi entitas dan memverifikasi kelayakan struktur graf. Diagram alir sistem secara keseluruhan ditunjukkan pada Gambar 3.1.

[SISIPKAN GAMBAR 3.1 - Diagram Alir Sistem]

---

### 3.1.1 Preparasi Dataset

Tahap preparasi dataset bertujuan untuk mengubah dokumen Sirah Nabawiyah dalam format PDF (hasil scan) menjadi dataset teks terstruktur yang siap digunakan untuk tahapan selanjutnya. Proses ini terdiri dari tiga tahapan utama: OCR tiap halaman, segmentasi konten berdasarkan struktur daftar isi (Table of Contents), dan ekspor dataset ke format CSV.

**Langkah-langkah preparasi dataset adalah sebagai berikut:**

**Langkah 1: Konversi PDF ke Citra**
Setiap halaman dokumen PDF dikonversi menjadi citra (image) menggunakan library pdf2image. Konversi ini diperlukan karena dokumen Sirah berupa hasil scan yang tidak memiliki layer teks digital.

**Langkah 2: Praproses Citra**
Citra hasil konversi melalui praproses untuk meningkatkan kualitas pembacaan OCR, meliputi:
- Penyesuaian resolusi/ukuran citra
- Reduksi noise pada citra
- Peningkatan kontras agar karakter lebih jelas

**Langkah 3: Ekstraksi Teks dengan OCR**
Setiap citra halaman diproses menggunakan PaddleOCR dengan konfigurasi bahasa Indonesia untuk mengekstraksi teks. Hasil pengenalan karakter disusun kembali menjadi teks dan disimpan sebagai berkas .txt per halaman dengan format penamaan `page_[nomor].txt`.

**Langkah 4: Segmentasi Berdasarkan Struktur Daftar Isi**
Kumpulan teks hasil OCR per halaman disusun kembali mengikuti struktur dokumen berdasarkan acuan daftar isi (Table of Contents). Proses ini meliputi:
- Pencocokan judul bab dan sub-bab menggunakan kombinasi exact matching dan fuzzy matching
- Pembersihan bagian footer yang berulang (seperti teks "Sirah Nabawiyah" dan nomor halaman)
- Penggabungan isi teks dalam sub-bab yang sama menjadi satu string
- Penyimpanan hasil dalam format JSON sebagai dokumen terstruktur

**Langkah 5: Ekspor ke Format CSV**
Dokumen terstruktur dikonversi ke format CSV untuk membentuk dataset akhir. Struktur dataset hasil preparasi ditunjukkan pada Tabel 3.1.

[SISIPKAN TABEL 3.1 - Struktur Dataset Sirah Nabawiyah]

| Nama Kolom     | Tipe Data | Deskripsi                                           |
|----------------|-----------|-----------------------------------------------------|
| judul_bab      | String    | Nama bab utama hasil segmentasi berdasarkan TOC     |
| judul_sub_bab  | String    | Nama sub-bab yang berada di bawah bab terkait       |
| halaman        | String    | Informasi halaman sumber konten sub-bab             |
| teks           | String    | Isi teks sub-bab yang telah dibersihkan dan digabung|

**Output:** Dataset dalam format CSV berisi teks Sirah Nabawiyah yang terstruktur berdasarkan bab dan sub-bab.

---

### 3.1.2 Preprocessing Data

Tahap preprocessing bertujuan untuk membersihkan dataset dari noise hasil OCR dan menyiapkan teks agar lebih stabil untuk tahap ekstraksi entitas dan relasi. Kualitas hasil OCR sangat mempengaruhi performa tahapan selanjutnya, sehingga preprocessing menjadi tahap kritis dalam pipeline penelitian ini.

**Langkah-langkah preprocessing data adalah sebagai berikut:**

**Langkah 1: Penyaringan Baris Tidak Relevan**
Menyaring dan menghapus baris yang tidak termasuk konten utama, seperti:
- Bagian dengan label "UNKNOWN BAB" (hasil segmentasi yang gagal)
- Bagian bibliografi atau daftar pustaka
- Bagian lampiran yang tidak relevan

**Langkah 2: Normalisasi Teks**
Melakukan normalisasi untuk menstandarkan format teks, meliputi:
- Menghapus karakter non-printing (karakter kontrol yang tidak terlihat)
- Merapikan spasi berlebih (multiple spaces menjadi single space)
- Menghapus simbol-simbol non-informatif yang sering muncul pada hasil OCR
- Normalisasi tanda baca yang tidak konsisten

**Langkah 3: Pembersihan Gibberish**
Mengidentifikasi dan menghapus token atau kalimat yang tidak bermakna akibat kesalahan OCR, seperti:
- Rangkaian karakter acak yang tidak membentuk kata
- Kalimat dengan proporsi karakter aneh yang tinggi
- Fragmen teks yang terpotong tidak wajar

**Langkah 4: Validasi Hasil Preprocessing**
Melakukan pengecekan manual pada sampel data untuk memastikan:
- Teks hasil preprocessing dapat dibaca dengan baik
- Tidak ada informasi penting yang terhapus
- Format teks konsisten di seluruh dataset

**Output:** Dataset CSV dengan teks yang telah dibersihkan dan dinormalisasi, siap untuk tahap chunking.

---

### 3.1.3 Chunking

Tahap chunking bertujuan untuk membagi teks pada setiap sub-bab menjadi potongan-potongan (chunks) yang lebih kecil namun tetap mempertahankan konteks. Pemecahan ini diperlukan karena teks per sub-bab dapat berukuran panjang sehingga kurang efisien untuk proses anotasi manual maupun pemrosesan NER.

**Langkah-langkah chunking adalah sebagai berikut:**

**Langkah 1: Segmentasi Kalimat**
Memecah teks menjadi kalimat-kalimat individual berdasarkan tanda baca akhir kalimat:
- Tanda titik (.)
- Tanda tanya (?)
- Tanda seru (!)

**Langkah 2: Penggabungan Kalimat Menjadi Chunk**
Menggabungkan beberapa kalimat menjadi satu chunk dengan parameter:
- Batas maksimum panjang chunk: 1500 karakter
- Chunk tidak memotong di tengah kalimat

**Langkah 3: Penerapan Overlap Antar Chunk**
Menerapkan overlap untuk menjaga kesinambungan konteks antar chunk:
- Overlap: 1 kalimat terakhir dari chunk sebelumnya diulang pada chunk berikutnya
- Overlap membantu mempertahankan konteks entitas yang mungkin terpecah antar chunk

**Langkah 4: Pemberian Identitas dan Metadata**
Setiap chunk diberi identitas unik dan metadata untuk keterlacakan:
- `chunk_id`: Identitas unik setiap chunk
- `doc_id`: Identitas dokumen/sub-bab asal
- `chunk_index`: Urutan chunk dalam dokumen
- `judul_bab`, `judul_sub_bab`, `halaman`: Metadata sumber

**Langkah 5: Ekspor Hasil Chunking**
Menyimpan hasil chunking ke dalam file CSV baru dengan struktur yang mencakup metadata dan teks chunk.

**Output:** Dataset CSV berisi kumpulan chunk dengan metadata lengkap, siap untuk tahap manual labelling.

---

### 3.1.4 Manual Labelling

Tahap manual labelling bertujuan untuk membentuk data anotasi yang akan digunakan sebagai seed untuk pseudo-labelling dan sebagai ground truth untuk evaluasi. Proses anotasi dilakukan secara manual oleh peneliti dengan menandai entitas dalam teks sesuai skema label yang telah ditentukan.

**Langkah-langkah manual labelling adalah sebagai berikut:**

**Langkah 1: Sampling Data untuk Anotasi**
Memilih subset data dari hasil chunking dengan strategi sampling yang representatif:
- Pengambilan sampel dilakukan per bab untuk menghindari dominasi bab tertentu
- Maksimal 25 chunk per bab diambil sebagai sampel
- Random seed digunakan untuk konsistensi dan reproduksibilitas

**Langkah 2: Persiapan Template Anotasi**
Menyiapkan template anotasi dalam format spreadsheet (Excel/CSV) dengan kolom:
- Metadata chunk (chunk_id, judul_bab, judul_sub_bab, halaman)
- teks_chunk: Teks yang akan dianotasi
- entity_text: Teks entitas yang ditemukan
- label: Label entitas (PERSON, EVENT, LOCATION, TIME)

**Langkah 3: Proses Anotasi Manual**
Melakukan anotasi dengan membaca setiap chunk dan mengidentifikasi entitas:
- **PERSON**: Nama tokoh atau individu (contoh: "Abu Bakar", "Rasulullah", "Khadijah")
- **EVENT**: Nama peristiwa (contoh: "Perang Badar", "Hijrah", "Fathu Makkah")
- **LOCATION**: Nama lokasi geografis (contoh: "Mekah", "Madinah", "Gua Hira")
- **TIME**: Informasi waktu atau periode (contoh: "tahun ke-2 Hijriah", "bulan Ramadhan")

**Langkah 4: Pembagian Data Anotasi**
Membagi data hasil anotasi menjadi dua bagian yang tidak tumpang tindih:
- **Data Seed (70%)**: Digunakan sebagai acuan dalam proses pseudo-labelling
- **Data Ground Truth (30%)**: Disimpan terpisah untuk evaluasi, tidak digunakan saat pseudo-labelling

**Langkah 5: Validasi Hasil Anotasi**
Melakukan pengecekan kualitas anotasi:
- Review konsistensi pelabelan antar chunk
- Memastikan tidak ada entitas yang terlewat (terutama entitas penting)
- Verifikasi kebenaran label yang diberikan

**Output:** Dataset anotasi manual yang terbagi menjadi data seed dan data ground truth.

---

### 3.1.5 Pseudo-labelling Berbasis NER

Tahap pseudo-labelling bertujuan untuk memperluas cakupan anotasi entitas dari data seed ke seluruh data yang belum berlabel. Proses ini dilakukan menggunakan dua skenario ekstraksi yang berbeda: SRL-based NER dan LLM-based NER. Kedua skenario dijalankan secara paralel untuk menghasilkan dua set entitas berlabel yang akan dibandingkan performanya.

**Langkah-langkah pseudo-labelling adalah sebagai berikut:**

**Langkah 1: Persiapan Data Input**
Menyiapkan data yang akan diproses:
- Data seed sebagai referensi/contoh
- Data yang belum berlabel (sisa chunk di luar data seed dan ground truth)

**Langkah 2: Ekstraksi dengan Skenario A (SRL-based NER)**
Melakukan ekstraksi entitas menggunakan pendekatan Semantic Role Labeling:

a) **Parsing Dependensi dan SRL**
   - Memproses setiap chunk dengan model NLP untuk mendapatkan struktur dependensi
   - Mengidentifikasi predikat (kata kerja) sebagai pusat peristiwa
   - Mengekstraksi argumen semantik (ARG0, ARG1, ARGM-LOC, ARGM-TMP)

b) **Mapping Role ke Label Entitas**
   - ARG0 (pelaku/agent) → kandidat PERSON
   - ARG1 (objek/theme) → kandidat EVENT atau PERSON (berdasarkan konteks)
   - ARGM-LOC (lokasi) → kandidat LOCATION
   - ARGM-TMP (waktu) → kandidat TIME

c) **Validasi dan Filtering**
   - Memfilter kandidat berdasarkan pola linguistik (kapitalisasi, kata kunci)
   - Menerapkan aturan domain untuk meningkatkan presisi

**Langkah 3: Ekstraksi dengan Skenario B (LLM-based NER)**
Melakukan ekstraksi entitas menggunakan Large Language Model:

a) **Perancangan Prompt**
   - Menyusun prompt yang mendefinisikan skema label (PERSON, EVENT, LOCATION, TIME)
   - Menyertakan contoh dari data seed (few-shot learning)
   - Menentukan format output terstruktur (JSON)

b) **Eksekusi Prompt pada LLM**
   - Mengirimkan setiap chunk beserta prompt ke LLM API
   - Menerima respons dalam format JSON berisi daftar entitas

c) **Parsing dan Validasi Output**
   - Mem-parsing respons JSON dari LLM
   - Memvalidasi format dan kelengkapan output
   - Menangani kasus error atau respons tidak valid

**Langkah 4: Normalisasi Hasil Ekstraksi**
Melakukan normalisasi pada hasil kedua skenario:
- Menyeragamkan format penulisan entitas
- Menghapus duplikasi entitas dalam satu chunk
- Memetakan variasi penulisan ke bentuk kanonik

**Langkah 5: Penyimpanan Hasil**
Menyimpan hasil pseudo-labelling dalam format yang konsisten:
- Hasil Skenario A (SRL-based): `entities_srl.csv`
- Hasil Skenario B (LLM-based): `entities_llm.csv`
- Setiap record berisi: chunk_id, entity_text, label, start_pos, end_pos

**Output:** Dua set entitas berlabel dari kedua skenario, siap untuk tahap pembentukan relasi.

---

### 3.1.6 Pembentukan Relasi

Tahap pembentukan relasi bertujuan untuk menghubungkan entitas yang telah diekstraksi menjadi pasangan node-edge sehingga terbentuk struktur pengetahuan yang dapat dimasukkan ke basis data graf. Proses ini dilakukan pada hasil ekstraksi dari kedua skenario secara terpisah.

**Langkah-langkah pembentukan relasi adalah sebagai berikut:**

**Langkah 1: Identifikasi Kandidat Pasangan Entitas**
Mengidentifikasi pasangan entitas yang berpotensi memiliki relasi:
- Memasangkan entitas yang muncul dalam chunk yang sama
- Membatasi pasangan berdasarkan kedekatan posisi dalam teks
- Memprioritaskan pasangan yang melibatkan EVENT sebagai penghubung

**Langkah 2: Penentuan Tipe Relasi**
Menentukan tipe relasi berdasarkan kombinasi label entitas:

| Pasangan Entitas       | Tipe Relasi    | Deskripsi                              |
|------------------------|----------------|----------------------------------------|
| PERSON → EVENT         | INVOLVED_IN    | Tokoh terlibat dalam peristiwa         |
| EVENT → LOCATION       | OCCURRED_AT    | Peristiwa terjadi di lokasi tertentu   |
| EVENT → TIME           | OCCURRED_ON    | Peristiwa terjadi pada waktu tertentu  |

**Langkah 3: Ekstraksi Relasi dari Konteks**
Mengekstraksi relasi berdasarkan konteks kalimat:
- Menganalisis struktur kalimat untuk mengkonfirmasi relasi
- Menggunakan kata kunci pemicu relasi (contoh: "di", "pada", "ketika", "terlibat")
- Memvalidasi relasi dengan konteks semantik

**Langkah 4: Penyimpanan Provenance**
Menyimpan informasi sumber (provenance) untuk setiap relasi:
- chunk_id: Identitas chunk sumber
- halaman: Nomor halaman dalam dokumen asli
- evidence: Cuplikan kalimat sebagai bukti relasi

**Langkah 5: Deduplikasi dan Normalisasi Relasi**
Membersihkan hasil ekstraksi relasi:
- Menggabungkan relasi yang sama dari konteks berbeda
- Memetakan entitas ke bentuk kanonik
- Menghapus relasi duplikat

**Langkah 6: Ekspor Edge List**
Menyimpan hasil relasi dalam format edge list:
- Hasil Skenario A: `relations_srl.csv`
- Hasil Skenario B: `relations_llm.csv`
- Struktur: source_id, source_label, relation_type, target_id, target_label, chunk_id, evidence

**Output:** Dua set edge list dari kedua skenario, siap untuk konstruksi graf.

---

### 3.1.7 Konstruksi Knowledge Graph di Neo4j

Tahap konstruksi knowledge graph bertujuan untuk membangun basis data graf di Neo4j berdasarkan entitas dan relasi yang telah diekstraksi. Proses ini menghasilkan dua graf terpisah: Graf A dari hasil SRL-based NER dan Graf B dari hasil LLM-based NER.

**Langkah-langkah konstruksi knowledge graph adalah sebagai berikut:**

**Langkah 1: Perancangan Skema Graf**
Mendefinisikan skema graf yang akan digunakan:

a) **Label Node:**
   - Person: Menyimpan entitas tokoh/individu
   - Event: Menyimpan entitas peristiwa
   - Location: Menyimpan entitas lokasi
   - Time: Menyimpan entitas waktu

b) **Tipe Relationship:**
   - INVOLVED_IN: Person → Event
   - OCCURRED_AT: Event → Location
   - OCCURRED_ON: Event → Time

c) **Properti Node:**
   - name: Nama entitas (kanonik)
   - aliases: Variasi nama/sebutan lain
   - source_chunks: Daftar chunk_id sumber

**Langkah 2: Inisialisasi Database Neo4j**
Menyiapkan environment Neo4j:
- Membuat database baru untuk Graf A dan Graf B
- Mengatur konfigurasi koneksi
- Membuat constraint untuk mencegah duplikasi node

**Langkah 3: Pembuatan Constraint dan Index**
Membuat constraint dan index untuk optimasi:
- Uniqueness constraint pada properti name untuk setiap label
- Index pada properti yang sering digunakan dalam kueri

**Langkah 4: Import Node**
Memasukkan node ke dalam graf:
- Membaca file entitas (entities_srl.csv atau entities_llm.csv)
- Membuat node dengan label sesuai tipe entitas
- Menambahkan properti name dan metadata

**Langkah 5: Import Relationship**
Memasukkan relationship ke dalam graf:
- Membaca file relasi (relations_srl.csv atau relations_llm.csv)
- Mencocokkan source dan target node
- Membuat relationship dengan tipe yang sesuai
- Menambahkan properti provenance (chunk_id, evidence)

**Langkah 6: Validasi Graf**
Melakukan validasi hasil konstruksi:
- Memeriksa jumlah node per label
- Memeriksa jumlah relationship per tipe
- Menjalankan kueri sederhana untuk memastikan graf dapat diakses
- Memverifikasi tidak ada orphan node (node tanpa relationship)

**Output:** Dua basis data graf Neo4j (Graf A dan Graf B) yang siap untuk pengujian dan evaluasi.

---

### 3.1.8 Pengujian dan Evaluasi

Tahap pengujian dan evaluasi bertujuan untuk memvalidasi kualitas hasil ekstraksi entitas serta memverifikasi kelayakan struktur basis data graf dalam mendukung penelusuran informasi relasional pada domain Sirah Nabawiyah. Evaluasi dalam penelitian ini terbagi menjadi dua bagian utama, yaitu evaluasi hasil Named Entity Recognition (NER) dan evaluasi fungsional basis data graf.

#### 3.1.8.1 Evaluasi Hasil Named Entity Recognition

Evaluasi NER bertujuan untuk mengukur kemampuan kedua skenario ekstraksi (SRL-based NER dan LLM-based NER) dalam mengenali dan mengklasifikasikan entitas dari teks Sirah Nabawiyah.

**Langkah-langkah evaluasi NER adalah sebagai berikut:**

**Langkah 1: Persiapan Data Uji**
- Mengambil data ground truth (30% dari hasil manual labelling)
- Memastikan data uji tidak pernah digunakan dalam proses pseudo-labelling
- Memverifikasi distribusi label yang representatif

**Langkah 2: Eksekusi Ekstraksi pada Data Uji**
- Menjalankan SRL-based NER pada data uji
- Menjalankan LLM-based NER pada data uji yang sama
- Menyimpan hasil prediksi kedua skenario

**Langkah 3: Pencocokan Prediksi dengan Ground Truth**
- Membandingkan entitas hasil prediksi dengan ground truth
- Menggunakan kriteria exact match (teks dan label harus sama)
- Menghitung True Positive (TP), False Positive (FP), False Negative (FN) per label

**Langkah 4: Perhitungan Metrik**
- Menghitung Precision, Recall, F1-score untuk setiap label
- Menghitung Macro-average F1-score sebagai metrik agregat
- Menyusun tabel perbandingan kedua skenario

**Langkah 5: Analisis Perbandingan**
- Membandingkan performa SRL-based vs LLM-based
- Mengidentifikasi label yang mudah/sulit diekstraksi
- Menganalisis pola kesalahan yang sering terjadi

**Output:** Tabel metrik evaluasi NER dan analisis perbandingan kedua skenario.

#### 3.1.8.2 Evaluasi Fungsional Basis Data Graf

Evaluasi fungsional graf bertujuan untuk memverifikasi bahwa struktur graf dapat mendukung penelusuran informasi relasional dan membandingkan kelayakan Graf A dan Graf B.

**Langkah-langkah evaluasi graf adalah sebagai berikut:**

**Langkah 1: Perancangan Skenario Kueri**
Menyusun kueri Cypher yang merepresentasikan kebutuhan penelusuran informasi:

| No | Kategori        | Contoh Pertanyaan                                          | Pola Relasi                                                 |
|----|-----------------|------------------------------------------------------------|------------------------------------------------------------|
| 1  | Berbasis Tokoh  | Siapa saja yang terlibat dalam Perang Badar?               | (Person)-[INVOLVED_IN]->(Event)                            |
| 2  | Berbasis Lokasi | Peristiwa apa saja yang terjadi di Madinah?                | (Event)-[OCCURRED_AT]->(Location)                          |
| 3  | Berbasis Waktu  | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah?        | (Event)-[OCCURRED_ON]->(Time)                              |
| 4  | Tokoh-Peristiwa | Peristiwa apa saja yang melibatkan Abu Bakar?              | (Person)-[INVOLVED_IN]->(Event)                            |
| 5  | Multi-hop       | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | (Person)-[INVOLVED_IN]->(Event)-[OCCURRED_AT]->(Location)  |
| 6  | Timeline        | Urutkan peristiwa di Mekah berdasarkan waktu               | (Event)-[OCCURRED_AT]->(Location) + (Event)-[OCCURRED_ON]->(Time) |

**Langkah 2: Eksekusi Kueri pada Kedua Graf**
- Menjalankan setiap kueri pada Graf A (SRL-based)
- Menjalankan kueri yang sama pada Graf B (LLM-based)
- Mencatat hasil dan waktu eksekusi

**Langkah 3: Verifikasi Hasil Kueri**
- Memeriksa keberhasilan eksekusi (tidak error)
- Memeriksa hasil tidak kosong
- Memvalidasi kebenaran hasil dengan teks sumber
- Memeriksa keterlacakan (traceability)

**Langkah 4: Perbandingan Struktur Graf**
- Membandingkan jumlah node per label antara Graf A dan Graf B
- Membandingkan jumlah relationship per tipe
- Mengidentifikasi perbedaan cakupan informasi

**Langkah 5: Penilaian Kelayakan**
- Menghitung tingkat keberhasilan kueri untuk masing-masing graf
- Menyusun analisis perbandingan kelayakan Graf A vs Graf B

**Output:** Tabel hasil kueri, statistik perbandingan graf, dan analisis kelayakan.

---

## 3.2 Spesifikasi Lingkungan

### 3.2.1 Perangkat Keras

Eksperimen komputasi pada penelitian ini dijalankan pada lingkungan perangkat keras komputer lokal dengan spesifikasi sebagai berikut:

| Komponen   | Spesifikasi                              |
|------------|------------------------------------------|
| Prosesor   | Intel(R) Core(TM) i7-8750H @ 2.20GHz     |
| RAM        | 16 GB                                    |
| Penyimpanan| 1 TB                                     |
| GPU        | Opsional (untuk akselerasi model NLP)    |

### 3.2.2 Perangkat Lunak

Seluruh proses penelitian diimplementasikan menggunakan perangkat lunak sebagai berikut:

| Kategori             | Perangkat Lunak                                    |
|----------------------|----------------------------------------------------|
| Bahasa Pemrograman   | Python 3.x                                         |
| IDE                  | Jupyter Notebook                                   |
| OCR                  | PaddleOCR (konfigurasi Bahasa Indonesia)           |
| PDF Processing       | pdf2image, Poppler                                 |
| NLP Libraries        | Stanza, spaCy, Transformers                        |
| LLM API              | OpenAI API / Google Gemini API                     |
| Graph Database       | Neo4j Desktop 2.1.1                                |
| Neo4j Driver         | neo4j (Python driver)                              |
| Data Processing      | pandas, numpy                                      |
| Utilities            | tqdm, regex                                        |

---

## 3.3 Rencana Implementasi

Rancangan implementasi sistem konstruksi basis data graf Sirah Nabawiyah dijelaskan melalui pseudocode yang merepresentasikan alur kerja utama dari setiap komponen sistem.

### 3.3.1 Pseudocode Preparasi Dataset

Kode Semu 3.1 menunjukkan alur kerja preparasi dataset dari dokumen PDF hingga menjadi dataset CSV terstruktur.

```
INPUT  : pdf_path (path ke file PDF Sirah Nabawiyah)
         toc_data (data daftar isi untuk segmentasi)
OUTPUT : dataset (CSV berisi teks terstruktur per sub-bab)

ALGORITMA:
1.  BEGIN
2.      // Langkah 1: Konversi PDF ke citra
3.      images ← ConvertPDFToImages(pdf_path)
4.      
5.      // Langkah 2-3: OCR setiap halaman
6.      ocr_results ← []
7.      FOR EACH page_image IN images DO
8.          preprocessed ← PreprocessImage(page_image)
9.          text ← PaddleOCR.Extract(preprocessed, lang="id")
10.         ocr_results.APPEND({page_num, text})
11.     END FOR
12.     
13.     // Langkah 4: Segmentasi berdasarkan TOC
14.     structured_docs ← []
15.     FOR EACH section IN toc_data DO
16.         matched_text ← ""
17.         FOR EACH page IN section.page_range DO
18.             page_text ← ocr_results[page].text
19.             page_text ← RemoveFooter(page_text)
20.             matched_text ← matched_text + page_text
21.         END FOR
22.         structured_docs.APPEND({
23.             judul_bab: section.bab,
24.             judul_sub_bab: section.sub_bab,
25.             halaman: section.page_range,
26.             teks: matched_text
27.         })
28.     END FOR
29.     
30.     // Langkah 5: Ekspor ke CSV
31.     dataset ← ConvertToCSV(structured_docs)
32.     SaveCSV(dataset, "sirah_dataset.csv")
33.     
34.     RETURN dataset
35. END
```

### 3.3.2 Pseudocode Preprocessing dan Chunking

Kode Semu 3.2 menunjukkan alur kerja preprocessing data dan chunking teks.

```
INPUT  : raw_dataset (CSV hasil preparasi dataset)
OUTPUT : chunks_dataset (CSV berisi chunk dengan metadata)

ALGORITMA:
1.  BEGIN
2.      // Preprocessing
3.      clean_dataset ← []
4.      FOR EACH row IN raw_dataset DO
5.          // Langkah 1: Filter baris tidak relevan
6.          IF row.judul_bab = "UNKNOWN" OR row.judul_bab = "BIBLIOGRAFI" THEN
7.              CONTINUE
8.          END IF
9.          
10.         // Langkah 2: Normalisasi teks
11.         text ← row.teks
12.         text ← RemoveNonPrintingChars(text)
13.         text ← NormalizeWhitespace(text)
14.         text ← RemoveNonInformativeSymbols(text)
15.         
16.         // Langkah 3: Pembersihan gibberish
17.         text ← RemoveGibberish(text)
18.         
19.         row.teks ← text
20.         clean_dataset.APPEND(row)
21.     END FOR
22.     
23.     // Chunking
24.     chunks_dataset ← []
25.     chunk_id ← 0
26.     FOR EACH doc IN clean_dataset DO
27.         // Langkah 1: Segmentasi kalimat
28.         sentences ← SplitIntoSentences(doc.teks)
29.         
30.         // Langkah 2-3: Gabung kalimat dengan overlap
31.         current_chunk ← ""
32.         chunk_sentences ← []
33.         FOR EACH sentence IN sentences DO
34.             IF LENGTH(current_chunk + sentence) > 1500 THEN
35.                 // Simpan chunk saat ini
36.                 chunks_dataset.APPEND({
37.                     chunk_id: chunk_id,
38.                     doc_id: doc.id,
39.                     judul_bab: doc.judul_bab,
40.                     judul_sub_bab: doc.judul_sub_bab,
41.                     halaman: doc.halaman,
42.                     teks_chunk: current_chunk
43.                 })
44.                 chunk_id ← chunk_id + 1
45.                 
46.                 // Overlap: ambil kalimat terakhir
47.                 current_chunk ← chunk_sentences[LAST]
48.                 chunk_sentences ← [chunk_sentences[LAST]]
49.             END IF
50.             current_chunk ← current_chunk + " " + sentence
51.             chunk_sentences.APPEND(sentence)
52.         END FOR
53.         
54.         // Simpan chunk terakhir
55.         IF current_chunk ≠ "" THEN
56.             chunks_dataset.APPEND({...})
57.         END IF
58.     END FOR
59.     
60.     SaveCSV(chunks_dataset, "sirah_chunks.csv")
61.     RETURN chunks_dataset
62. END
```

### 3.3.3 Pseudocode SRL-based NER

Kode Semu 3.3 menunjukkan alur kerja ekstraksi entitas menggunakan pendekatan Semantic Role Labeling.

```
INPUT  : chunks_dataset (CSV berisi chunk teks)
         seed_data (data seed dari manual labelling)
OUTPUT : entities_srl (CSV berisi entitas hasil ekstraksi SRL)

ALGORITMA:
1.  BEGIN
2.      // Inisialisasi NLP pipeline
3.      nlp_pipeline ← InitializeStanzaPipeline(lang="id")
4.      
5.      entities_srl ← []
6.      
7.      FOR EACH chunk IN chunks_dataset DO
8.          chunk_text ← chunk.teks_chunk
9.          
10.         // Langkah 1: Parsing dependensi dan SRL
11.         doc ← nlp_pipeline.Process(chunk_text)
12.         
13.         FOR EACH sentence IN doc.sentences DO
14.             // Identifikasi predikat (kata kerja)
15.             predicates ← GetPredicates(sentence)
16.             
17.             FOR EACH predicate IN predicates DO
18.                 // Ekstraksi argumen semantik
19.                 srl_result ← ExtractSemanticRoles(sentence, predicate)
20.                 
21.                 // Langkah 2: Mapping role ke label entitas
22.                 
23.                 // ARG0 (pelaku) → PERSON
24.                 IF srl_result.ARG0 EXISTS THEN
25.                     candidate ← srl_result.ARG0.text
26.                     IF IsValidPersonName(candidate) THEN
27.                         entities_srl.APPEND({
28.                             chunk_id: chunk.chunk_id,
29.                             entity_text: candidate,
30.                             label: "PERSON",
31.                             start_pos: srl_result.ARG0.start,
32.                             end_pos: srl_result.ARG0.end
33.                         })
34.                     END IF
35.                 END IF
36.                 
37.                 // ARGM-LOC (lokasi) → LOCATION
38.                 IF srl_result.ARGM_LOC EXISTS THEN
39.                     candidate ← srl_result.ARGM_LOC.text
40.                     IF IsValidLocation(candidate) THEN
41.                         entities_srl.APPEND({
42.                             chunk_id: chunk.chunk_id,
43.                             entity_text: candidate,
44.                             label: "LOCATION",
45.                             start_pos: srl_result.ARGM_LOC.start,
46.                             end_pos: srl_result.ARGM_LOC.end
47.                         })
48.                     END IF
49.                 END IF
50.                 
51.                 // ARGM-TMP (waktu) → TIME
52.                 IF srl_result.ARGM_TMP EXISTS THEN
53.                     candidate ← srl_result.ARGM_TMP.text
54.                     entities_srl.APPEND({
55.                         chunk_id: chunk.chunk_id,
56.                         entity_text: candidate,
57.                         label: "TIME",
58.                         start_pos: srl_result.ARGM_TMP.start,
59.                         end_pos: srl_result.ARGM_TMP.end
60.                     })
61.                 END IF
62.                 
63.                 // Predicate → EVENT (jika merupakan peristiwa penting)
64.                 event_candidate ← ExtractEventPhrase(sentence, predicate)
65.                 IF IsValidEvent(event_candidate) THEN
66.                     entities_srl.APPEND({
67.                         chunk_id: chunk.chunk_id,
68.                         entity_text: event_candidate,
69.                         label: "EVENT",
70.                         start_pos: predicate.start,
71.                         end_pos: predicate.end
72.                     })
73.                 END IF
74.             END FOR
75.         END FOR
76.     END FOR
77.     
78.     // Langkah 3: Normalisasi dan deduplikasi
79.     entities_srl ← NormalizeEntities(entities_srl)
80.     entities_srl ← RemoveDuplicates(entities_srl)
81.     
82.     SaveCSV(entities_srl, "entities_srl.csv")
83.     RETURN entities_srl
84. END

// Fungsi pembantu untuk validasi
FUNCTION IsValidPersonName(text)
    // Cek kapitalisasi, kata kunci nama Arab/Islam
    IF StartsWithCapital(text) OR ContainsIslamicNamePattern(text) THEN
        RETURN TRUE
    END IF
    RETURN FALSE
END FUNCTION

FUNCTION IsValidLocation(text)
    // Cek dengan gazetteer lokasi Sirah
    location_keywords ← ["Mekah", "Madinah", "Gua", "Bukit", "Lembah", ...]
    RETURN ContainsAny(text, location_keywords)
END FUNCTION

FUNCTION IsValidEvent(text)
    // Cek dengan daftar peristiwa Sirah
    event_keywords ← ["Perang", "Hijrah", "Bai'at", "Fathu", "Isra", ...]
    RETURN ContainsAny(text, event_keywords)
END FUNCTION
```

### 3.3.4 Pseudocode LLM-based NER

Kode Semu 3.4 menunjukkan alur kerja ekstraksi entitas menggunakan Large Language Model.

```
INPUT  : chunks_dataset (CSV berisi chunk teks)
         seed_data (data seed untuk few-shot examples)
OUTPUT : entities_llm (CSV berisi entitas hasil ekstraksi LLM)

ALGORITMA:
1.  BEGIN
2.      // Langkah 1: Persiapan prompt template
3.      system_prompt ← ConstructSystemPrompt()
4.      few_shot_examples ← PrepareFewShotExamples(seed_data)
5.      
6.      entities_llm ← []
7.      
8.      FOR EACH chunk IN chunks_dataset DO
9.          // Langkah 2: Konstruksi prompt untuk chunk
10.         user_prompt ← ConstructUserPrompt(chunk.teks_chunk, few_shot_examples)
11.         
12.         // Langkah 3: Panggil LLM API
13.         TRY
14.             response ← CallLLMAPI(
15.                 system_prompt: system_prompt,
16.                 user_prompt: user_prompt,
17.                 temperature: 0.1,
18.                 response_format: "json"
19.             )
20.             
21.             // Langkah 4: Parsing respons JSON
22.             extracted_entities ← ParseJSON(response)
23.             
24.             // Validasi dan simpan hasil
25.             FOR EACH entity IN extracted_entities DO
26.                 IF IsValidLabel(entity.label) THEN
27.                     entities_llm.APPEND({
28.                         chunk_id: chunk.chunk_id,
29.                         entity_text: entity.text,
30.                         label: entity.label,
31.                         start_pos: FindPosition(chunk.teks_chunk, entity.text),
32.                         end_pos: FindEndPosition(chunk.teks_chunk, entity.text)
33.                     })
34.                 END IF
35.             END FOR
36.             
37.         CATCH error
38.             LogError(chunk.chunk_id, error)
39.             CONTINUE
40.         END TRY
41.     END FOR
42.     
43.     // Langkah 5: Normalisasi dan deduplikasi
44.     entities_llm ← NormalizeEntities(entities_llm)
45.     entities_llm ← RemoveDuplicates(entities_llm)
46.     
47.     SaveCSV(entities_llm, "entities_llm.csv")
48.     RETURN entities_llm
49. END

FUNCTION ConstructSystemPrompt()
    prompt ← "Kamu adalah sistem ekstraksi entitas untuk teks Sirah Nabawiyah.
    
    Tugasmu adalah mengidentifikasi dan mengekstraksi entitas dari teks yang diberikan.
    
    Label entitas yang digunakan:
    - PERSON: Nama tokoh atau individu (contoh: Abu Bakar, Rasulullah, Khadijah)
    - EVENT: Nama peristiwa penting (contoh: Perang Badar, Hijrah, Fathu Makkah)
    - LOCATION: Nama lokasi geografis (contoh: Mekah, Madinah, Gua Hira)
    - TIME: Informasi waktu atau periode (contoh: tahun ke-2 Hijriah, bulan Ramadhan)
    
    Berikan output dalam format JSON array:
    [
        {\"text\": \"nama entitas\", \"label\": \"LABEL\"},
        ...
    ]
    
    Hanya ekstrak entitas yang jelas disebutkan dalam teks. Jangan menambahkan entitas yang tidak ada."
    
    RETURN prompt
END FUNCTION

FUNCTION PrepareFewShotExamples(seed_data)
    examples ← []
    // Ambil 3-5 contoh representatif dari seed data
    sampled ← SampleByLabel(seed_data, n_per_label=2)
    
    FOR EACH sample IN sampled DO
        examples.APPEND({
            input: sample.teks_chunk,
            output: sample.entities
        })
    END FOR
    
    RETURN examples
END FUNCTION

FUNCTION ConstructUserPrompt(text, examples)
    prompt ← "Berikut adalah contoh ekstraksi entitas:\n\n"
    
    FOR EACH example IN examples DO
        prompt ← prompt + "Teks: " + example.input + "\n"
        prompt ← prompt + "Entitas: " + FormatJSON(example.output) + "\n\n"
    END FOR
    
    prompt ← prompt + "Sekarang ekstrak entitas dari teks berikut:\n"
    prompt ← prompt + "Teks: " + text + "\n"
    prompt ← prompt + "Entitas:"
    
    RETURN prompt
END FUNCTION
```

### 3.3.5 Pseudocode Pembentukan Relasi

Kode Semu 3.5 menunjukkan alur kerja pembentukan relasi antar entitas.

```
INPUT  : entities_data (CSV berisi entitas hasil ekstraksi)
         chunks_dataset (CSV berisi chunk untuk konteks)
OUTPUT : relations (CSV berisi relasi antar entitas)

ALGORITMA:
1.  BEGIN
2.      relations ← []
3.      
4.      // Kelompokkan entitas berdasarkan chunk_id
5.      entities_by_chunk ← GroupByChunkID(entities_data)
6.      
7.      FOR EACH chunk_id, chunk_entities IN entities_by_chunk DO
8.          chunk_text ← GetChunkText(chunks_dataset, chunk_id)
9.          
10.         // Langkah 1: Identifikasi kandidat pasangan
11.         // Fokus pada EVENT sebagai penghubung
12.         events ← Filter(chunk_entities, label="EVENT")
13.         persons ← Filter(chunk_entities, label="PERSON")
14.         locations ← Filter(chunk_entities, label="LOCATION")
15.         times ← Filter(chunk_entities, label="TIME")
16.         
17.         FOR EACH event IN events DO
18.             
19.             // Langkah 2: Relasi PERSON → EVENT (INVOLVED_IN)
20.             FOR EACH person IN persons DO
21.                 IF AreInSameContext(person, event, chunk_text) THEN
22.                     evidence ← ExtractEvidence(chunk_text, person, event)
23.                     relations.APPEND({
24.                         source_id: GenerateID(person),
25.                         source_text: person.entity_text,
26.                         source_label: "PERSON",
27.                         relation_type: "INVOLVED_IN",
28.                         target_id: GenerateID(event),
29.                         target_text: event.entity_text,
30.                         target_label: "EVENT",
31.                         chunk_id: chunk_id,
32.                         evidence: evidence
33.                     })
34.                 END IF
35.             END FOR
36.             
37.             // Langkah 3: Relasi EVENT → LOCATION (OCCURRED_AT)
38.             FOR EACH location IN locations DO
39.                 IF AreInSameContext(event, location, chunk_text) THEN
40.                     evidence ← ExtractEvidence(chunk_text, event, location)
41.                     relations.APPEND({
42.                         source_id: GenerateID(event),
43.                         source_text: event.entity_text,
44.                         source_label: "EVENT",
45.                         relation_type: "OCCURRED_AT",
46.                         target_id: GenerateID(location),
47.                         target_text: location.entity_text,
48.                         target_label: "LOCATION",
49.                         chunk_id: chunk_id,
50.                         evidence: evidence
51.                     })
52.                 END IF
53.             END FOR
54.             
55.             // Langkah 4: Relasi EVENT → TIME (OCCURRED_ON)
56.             FOR EACH time IN times DO
57.                 IF AreInSameContext(event, time, chunk_text) THEN
58.                     evidence ← ExtractEvidence(chunk_text, event, time)
59.                     relations.APPEND({
60.                         source_id: GenerateID(event),
61.                         source_text: event.entity_text,
62.                         source_label: "EVENT",
63.                         relation_type: "OCCURRED_ON",
64.                         target_id: GenerateID(time),
65.                         target_text: time.entity_text,
66.                         target_label: "TIME",
67.                         chunk_id: chunk_id,
68.                         evidence: evidence
69.                     })
70.                 END IF
71.             END FOR
72.         END FOR
73.     END FOR
74.     
75.     // Langkah 5: Deduplikasi relasi
76.     relations ← DeduplicateRelations(relations)
77.     
78.     SaveCSV(relations, "relations.csv")
79.     RETURN relations
80. END

FUNCTION AreInSameContext(entity1, entity2, text)
    // Cek apakah dua entitas berada dalam kalimat yang sama
    // atau dalam jarak yang cukup dekat
    pos1 ← FindPosition(text, entity1.entity_text)
    pos2 ← FindPosition(text, entity2.entity_text)
    
    // Dalam satu kalimat
    sentence1 ← GetSentenceAt(text, pos1)
    sentence2 ← GetSentenceAt(text, pos2)
    
    IF sentence1 = sentence2 THEN
        RETURN TRUE
    END IF
    
    // Atau dalam jarak maksimal 200 karakter
    IF ABS(pos1 - pos2) < 200 THEN
        RETURN TRUE
    END IF
    
    RETURN FALSE
END FUNCTION

FUNCTION ExtractEvidence(text, entity1, entity2)
    // Ekstrak kalimat yang mengandung kedua entitas sebagai bukti
    pos1 ← FindPosition(text, entity1.entity_text)
    pos2 ← FindPosition(text, entity2.entity_text)
    
    start ← MIN(pos1, pos2) - 50
    end ← MAX(pos1, pos2) + LENGTH(entity2.entity_text) + 50
    
    start ← MAX(0, start)
    end ← MIN(LENGTH(text), end)
    
    RETURN text[start:end]
END FUNCTION
```

### 3.3.6 Pseudocode Konstruksi Knowledge Graph di Neo4j

Kode Semu 3.6 menunjukkan alur kerja konstruksi knowledge graph di Neo4j.

```
INPUT  : entities_data (CSV berisi entitas)
         relations_data (CSV berisi relasi)
         db_name (nama database Neo4j)
OUTPUT : Neo4j graph database

ALGORITMA:
1.  BEGIN
2.      // Langkah 1: Inisialisasi koneksi Neo4j
3.      driver ← Neo4jDriver.Connect(uri, username, password)
4.      session ← driver.Session(database=db_name)
5.      
6.      // Langkah 2: Buat constraint untuk mencegah duplikasi
7.      session.Run("CREATE CONSTRAINT person_name IF NOT EXISTS 
8.                   FOR (p:Person) REQUIRE p.name IS UNIQUE")
9.      session.Run("CREATE CONSTRAINT event_name IF NOT EXISTS 
10.                  FOR (e:Event) REQUIRE e.name IS UNIQUE")
11.     session.Run("CREATE CONSTRAINT location_name IF NOT EXISTS 
12.                  FOR (l:Location) REQUIRE l.name IS UNIQUE")
13.     session.Run("CREATE CONSTRAINT time_name IF NOT EXISTS 
14.                  FOR (t:Time) REQUIRE t.name IS UNIQUE")
15.     
16.     // Langkah 3: Import Node
17.     node_count ← {Person: 0, Event: 0, Location: 0, Time: 0}
18.     
19.     FOR EACH entity IN entities_data DO
20.         label ← CapitalizeFirst(entity.label)  // "PERSON" → "Person"
21.         
22.         // Gunakan MERGE untuk menghindari duplikasi
23.         query ← "MERGE (n:" + label + " {name: $name})
24.                  ON CREATE SET n.source_chunks = [$chunk_id]
25.                  ON MATCH SET n.source_chunks = n.source_chunks + $chunk_id"
26.         
27.         session.Run(query, {
28.             name: NormalizeName(entity.entity_text),
29.             chunk_id: entity.chunk_id
30.         })
31.         
32.         node_count[label] ← node_count[label] + 1
33.     END FOR
34.     
35.     Print("Node created:", node_count)
36.     
37.     // Langkah 4: Import Relationship
38.     rel_count ← {INVOLVED_IN: 0, OCCURRED_AT: 0, OCCURRED_ON: 0}
39.     
40.     FOR EACH relation IN relations_data DO
41.         source_label ← CapitalizeFirst(relation.source_label)
42.         target_label ← CapitalizeFirst(relation.target_label)
43.         rel_type ← relation.relation_type
44.         
45.         query ← "MATCH (source:" + source_label + " {name: $source_name})
46.                  MATCH (target:" + target_label + " {name: $target_name})
47.                  MERGE (source)-[r:" + rel_type + "]->(target)
48.                  ON CREATE SET r.evidence = [$evidence], r.chunk_ids = [$chunk_id]
49.                  ON MATCH SET r.evidence = r.evidence + $evidence,
50.                               r.chunk_ids = r.chunk_ids + $chunk_id"
51.         
52.         session.Run(query, {
53.             source_name: NormalizeName(relation.source_text),
54.             target_name: NormalizeName(relation.target_text),
55.             evidence: relation.evidence,
56.             chunk_id: relation.chunk_id
57.         })
58.         
59.         rel_count[rel_type] ← rel_count[rel_type] + 1
60.     END FOR
61.     
62.     Print("Relationships created:", rel_count)
63.     
64.     // Langkah 5: Validasi graf
65.     validation_queries ← [
66.         "MATCH (n:Person) RETURN count(n) AS person_count",
67.         "MATCH (n:Event) RETURN count(n) AS event_count",
68.         "MATCH (n:Location) RETURN count(n) AS location_count",
69.         "MATCH (n:Time) RETURN count(n) AS time_count",
70.         "MATCH ()-[r:INVOLVED_IN]->() RETURN count(r) AS involved_in_count",
71.         "MATCH ()-[r:OCCURRED_AT]->() RETURN count(r) AS occurred_at_count",
72.         "MATCH ()-[r:OCCURRED_ON]->() RETURN count(r) AS occurred_on_count"
73.     ]
74.     
75.     FOR EACH query IN validation_queries DO
76.         result ← session.Run(query)
77.         Print(result)
78.     END FOR
79.     
80.     // Langkah 6: Tutup koneksi
81.     session.Close()
82.     driver.Close()
83.     
84.     Print("Graph construction completed for database:", db_name)
85. END

FUNCTION NormalizeName(name)
    // Normalisasi nama entitas ke bentuk kanonik
    name ← Trim(name)
    name ← RemoveExtraSpaces(name)
    name ← CapitalizeWords(name)
    
    // Normalisasi alias umum
    aliases ← {
        "Nabi Muhammad": "Rasulullah",
        "Muhammad SAW": "Rasulullah",
        "Nabi SAW": "Rasulullah",
        ...
    }
    
    IF name IN aliases.keys() THEN
        RETURN aliases[name]
    END IF
    
    RETURN name
END FUNCTION
```

---

## 3.4 Urutan Pelaksanaan Penelitian

Penelitian Tugas Akhir ini akan dilaksanakan selama 16 minggu. Lini masa pengerjaan ditunjukkan pada Tabel 3.X.

[SISIPKAN TABEL 3.X - Lini Masa Pengerjaan]

| Deskripsi Kegiatan                              | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |10 |11 |12 |13 |14 |15 |16 |
|-------------------------------------------------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Studi literatur                                 | ■ | ■ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| Eksplorasi Program                              | ■ | ■ | ■ |   |   |   |   |   |   |   |   |   |   |   |   |   |
| Preparasi Dataset dan Preprocessing Data        |   |   | ■ | ■ | ■ |   |   |   |   |   |   |   |   |   |   |   |
| Implementasi Manual Labelling dan Pseudo-labelling |   |   |   |   | ■ | ■ | ■ | ■ |   |   |   |   |   |   |   |   |
| Implementasi Pembentukan Relasi dan Konstruksi Graf |   |   |   |   |   |   |   | ■ | ■ | ■ |   |   |   |   |   |   |
| Evaluasi Sistem                                 |   |   |   |   |   |   |   |   |   | ■ | ■ |   |   |   |   |   |
| Analisis Hasil dan Perbaikan                    |   |   |   |   |   |   |   |   |   |   | ■ | ■ |   |   |   |   |
| Pelaporan Kemajuan                              |   |   |   |   |   |   |   | ■ |   |   |   |   |   |   |   |   |
| Penulisan Laporan Tugas Akhir                   |   |   |   |   |   |   |   |   |   |   |   | ■ | ■ | ■ |   |   |
| Revisi dan Finalisasi Laporan                   |   |   |   |   |   |   |   |   |   |   |   |   |   | ■ | ■ | ■ |
