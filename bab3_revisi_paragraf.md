# BAB 3 METODOLOGI

## 3.1 Metode dan Alur Kerja

Penelitian ini bertujuan membangun basis data graf Sirah Nabawiyah berbasis Named-Entity Recognition dengan memanfaatkan teknik pemrosesan bahasa alami. Sistem yang dikembangkan terdiri dari beberapa tahapan: preparasi dataset dari dokumen Sirah Nabawiyah, preprocessing untuk membersihkan noise hasil OCR, chunking untuk membagi teks menjadi unit yang lebih kecil, manual labelling pada sebagian data sebagai seed dan ground truth, pseudo-labelling berbasis NER menggunakan dua skenario (SRL-based dan LLM-based), pembentukan relasi antar entitas, serta konstruksi knowledge graph di Neo4j. Tahap akhir berupa pengujian dan evaluasi untuk memvalidasi kualitas ekstraksi entitas dan memverifikasi kelayakan struktur graf. Diagram alir sistem secara keseluruhan ditunjukkan pada Gambar 3.1.

[SISIPKAN GAMBAR 3.1 - Diagram Alir Sistem]

---

### 3.1.1 Preparasi Dataset

Tahap preparasi dataset bertujuan untuk mengubah dokumen Sirah Nabawiyah dalam format PDF (hasil scan) menjadi dataset teks terstruktur yang siap digunakan untuk tahapan selanjutnya. Proses ini terdiri dari tiga tahapan utama: OCR tiap halaman, segmentasi konten berdasarkan struktur daftar isi (Table of Contents), dan ekspor dataset ke format CSV. Diagram alir tahap preparasi dataset ditunjukkan pada Gambar 3.2.

[SISIPKAN GAMBAR 3.2 - Diagram Alir Preparasi Dataset]

Proses preparasi dataset diawali dengan konversi setiap halaman dokumen PDF menjadi citra (image) menggunakan library pdf2image. Konversi ini diperlukan karena dokumen Sirah berupa hasil scan yang tidak memiliki layer teks digital. Selanjutnya, citra hasil konversi melalui tahap praproses untuk meningkatkan kualitas pembacaan OCR, meliputi penyesuaian resolusi, reduksi noise, dan peningkatan kontras agar karakter lebih jelas.

Setelah praproses citra selesai, setiap halaman diproses menggunakan PaddleOCR dengan konfigurasi bahasa Indonesia untuk mengekstraksi teks. Hasil pengenalan karakter disusun kembali menjadi teks dan disimpan sebagai berkas .txt per halaman dengan format penamaan page_[nomor].txt. Contoh hasil OCR untuk beberapa halaman ditunjukkan pada Tabel 3.1.

[SISIPKAN TABEL 3.1 - Hasil OCR Sirah Nabawiyah]

Kumpulan teks hasil OCR per halaman kemudian disusun kembali mengikuti struktur dokumen berdasarkan acuan daftar isi (Table of Contents). Proses ini meliputi pencocokan judul bab dan sub-bab menggunakan kombinasi exact matching dan fuzzy matching, pembersihan bagian footer yang berulang seperti teks "Sirah Nabawiyah" dan nomor halaman, serta penggabungan isi teks dalam sub-bab yang sama menjadi satu string. Hasil segmentasi disimpan dalam format JSON sebagai dokumen terstruktur.

Tahap terakhir adalah mengonversi dokumen terstruktur tersebut ke format CSV untuk membentuk dataset akhir. Struktur dataset hasil preparasi ditunjukkan pada Tabel 3.2, yang terdiri dari kolom judul_bab, judul_sub_bab, halaman, dan teks.

[SISIPKAN TABEL 3.2 - Struktur Dataset Sirah Nabawiyah]

---

### 3.1.2 Preprocessing Data

Tahap preprocessing bertujuan untuk membersihkan dataset dari noise hasil OCR dan menyiapkan teks agar lebih stabil untuk tahap ekstraksi entitas dan relasi. Kualitas hasil OCR sangat mempengaruhi performa tahapan selanjutnya, sehingga preprocessing menjadi tahap kritis dalam pipeline penelitian ini. Diagram alir tahap preprocessing data ditunjukkan pada Gambar 3.3.

[SISIPKAN GAMBAR 3.3 - Diagram Alir Preprocessing Data]

Proses preprocessing diawali dengan penyaringan baris yang tidak relevan dari dataset. Baris-baris yang tidak termasuk konten utama seperti bagian dengan label "UNKNOWN BAB" (hasil segmentasi yang gagal), bagian bibliografi, dan bagian lampiran yang tidak relevan dihapus dari dataset. Penyaringan ini memastikan hanya konten utama Sirah Nabawiyah yang diproses pada tahap selanjutnya.

Selanjutnya dilakukan normalisasi teks untuk menstandarkan format. Proses normalisasi meliputi penghapusan karakter non-printing (karakter kontrol yang tidak terlihat), perapian spasi berlebih (multiple spaces menjadi single space), penghapusan simbol-simbol non-informatif yang sering muncul pada hasil OCR, serta normalisasi tanda baca yang tidak konsisten. Normalisasi ini penting untuk memastikan konsistensi format teks di seluruh dataset.

Tahap berikutnya adalah pembersihan gibberish, yaitu mengidentifikasi dan menghapus token atau kalimat yang tidak bermakna akibat kesalahan OCR. Gibberish dapat berupa rangkaian karakter acak yang tidak membentuk kata, kalimat dengan proporsi karakter aneh yang tinggi, atau fragmen teks yang terpotong tidak wajar. Pembersihan gibberish dilakukan untuk meningkatkan kualitas teks sebelum tahap ekstraksi entitas.

Proses preprocessing diakhiri dengan validasi hasil melalui pengecekan manual pada sampel data. Validasi memastikan teks hasil preprocessing dapat dibaca dengan baik, tidak ada informasi penting yang terhapus, dan format teks konsisten di seluruh dataset. Output dari tahap ini adalah dataset CSV dengan teks yang telah dibersihkan dan dinormalisasi, siap untuk tahap chunking.

---

### 3.1.3 Chunking

Tahap chunking bertujuan untuk membagi teks pada setiap sub-bab menjadi potongan-potongan (chunks) yang lebih kecil namun tetap mempertahankan konteks. Pemecahan ini diperlukan karena teks per sub-bab dapat berukuran panjang sehingga kurang efisien untuk proses anotasi manual maupun pemrosesan NER. Diagram alir tahap chunking ditunjukkan pada Gambar 3.4.

[SISIPKAN GAMBAR 3.4 - Diagram Alir Chunking]

Proses chunking diawali dengan segmentasi kalimat, yaitu memecah teks menjadi kalimat-kalimat individual berdasarkan tanda baca akhir kalimat seperti tanda titik, tanda tanya, dan tanda seru. Segmentasi berbasis kalimat dipilih untuk memastikan setiap chunk tidak terpotong di tengah kalimat sehingga konteks tetap terjaga.

Setelah segmentasi, beberapa kalimat digabungkan menjadi satu chunk dengan batas maksimum panjang 1500 karakter. Penggabungan dilakukan secara berurutan hingga mencapai batas maksimum, kemudian chunk baru dimulai. Untuk menjaga kesinambungan konteks antar chunk, diterapkan mekanisme overlap di mana satu kalimat terakhir dari chunk sebelumnya diulang pada chunk berikutnya. Overlap ini membantu mempertahankan konteks entitas yang mungkin terpecah antar chunk.

Setiap chunk diberi identitas unik dan metadata untuk memudahkan pelacakan ke sumber asli. Metadata yang disimpan meliputi chunk_id sebagai identitas unik setiap chunk, doc_id sebagai identitas dokumen asal, chunk_index sebagai urutan chunk dalam dokumen, serta judul_bab, judul_sub_bab, dan halaman sebagai informasi sumber. Hasil chunking diekspor ke dalam file CSV baru yang siap digunakan pada tahap manual labelling.

---

### 3.1.4 Manual Labelling

Tahap manual labelling bertujuan untuk membentuk data anotasi yang akan digunakan sebagai seed untuk pseudo-labelling dan sebagai ground truth untuk evaluasi. Proses anotasi dilakukan secara manual oleh peneliti dengan menandai entitas dalam teks sesuai skema label yang telah ditentukan. Diagram alir tahap manual labelling ditunjukkan pada Gambar 3.5.

[SISIPKAN GAMBAR 3.5 - Diagram Alir Manual Labelling]

Proses manual labelling diawali dengan sampling data dari hasil chunking. Pemilihan sampel dilakukan dengan strategi pengambilan per bab untuk menghindari dominasi bab tertentu, dengan maksimal 25 chunk per bab diambil sebagai sampel. Random seed digunakan untuk memastikan konsistensi dan reproduksibilitas pemilihan sampel. Template anotasi disiapkan dalam format spreadsheet dengan kolom metadata chunk (chunk_id, judul_bab, judul_sub_bab, halaman), teks_chunk, entity_text, dan label.

Proses anotasi dilakukan dengan membaca setiap chunk dan mengidentifikasi entitas sesuai skema label yang telah ditentukan. Label PERSON digunakan untuk nama tokoh atau individu seperti Abu Bakar, Rasulullah, dan Khadijah. Label EVENT digunakan untuk nama peristiwa seperti Perang Badar, Hijrah, dan Fathu Makkah. Label LOCATION digunakan untuk nama lokasi geografis seperti Mekah, Madinah, dan Gua Hira. Label TIME digunakan untuk informasi waktu atau periode seperti tahun ke-2 Hijriah dan bulan Ramadhan.

Setelah anotasi selesai, data hasil anotasi dibagi menjadi dua bagian yang tidak tumpang tindih. Sebesar 70% data digunakan sebagai data seed yang menjadi acuan dalam proses pseudo-labelling, sedangkan 30% sisanya disimpan terpisah sebagai data ground truth yang khusus digunakan untuk evaluasi. Pemisahan ini penting untuk menjaga validitas evaluasi karena data ground truth tidak boleh digunakan saat proses pseudo-labelling. Tahap terakhir adalah validasi hasil anotasi untuk memastikan konsistensi pelabelan, tidak ada entitas penting yang terlewat, dan kebenaran label yang diberikan.

---

### 3.1.5 Pseudo-labelling Berbasis NER

Tahap pseudo-labelling bertujuan untuk memperluas cakupan anotasi entitas dari data seed ke seluruh data yang belum berlabel. Proses ini dilakukan menggunakan dua skenario ekstraksi yang berbeda: SRL-based NER dan LLM-based NER. Kedua skenario dijalankan secara paralel untuk menghasilkan dua set entitas berlabel yang akan dibandingkan performanya. Diagram alir tahap pseudo-labelling ditunjukkan pada Gambar 3.6.

[SISIPKAN GAMBAR 3.6 - Diagram Alir Pseudo-labelling Berbasis NER]

Proses pseudo-labelling diawali dengan persiapan data input yang terdiri dari data seed sebagai referensi dan data yang belum berlabel (sisa chunk di luar data seed dan ground truth). Selanjutnya, ekstraksi entitas dilakukan menggunakan dua skenario secara paralel.

Skenario pertama adalah SRL-based NER yang memanfaatkan pendekatan Semantic Role Labeling. Proses dimulai dengan parsing dependensi dan SRL untuk mengidentifikasi predikat (kata kerja) sebagai pusat peristiwa dan mengekstraksi argumen semantik. Hasil parsing kemudian dipetakan ke label entitas di mana ARG0 (pelaku/agent) dipetakan ke kandidat PERSON, ARGM-LOC (lokasi) dipetakan ke kandidat LOCATION, ARGM-TMP (waktu) dipetakan ke kandidat TIME, dan predikat yang merupakan peristiwa penting dipetakan ke kandidat EVENT. Kandidat entitas kemudian divalidasi dan difilter berdasarkan pola linguistik dan aturan domain untuk meningkatkan presisi.

Skenario kedua adalah LLM-based NER yang memanfaatkan Large Language Model. Proses dimulai dengan perancangan prompt yang mendefinisikan skema label, menyertakan contoh dari data seed (few-shot learning), dan menentukan format output terstruktur dalam bentuk JSON. Setiap chunk beserta prompt dikirimkan ke LLM API, dan respons dalam format JSON yang berisi daftar entitas diterima. Output dari LLM kemudian di-parsing dan divalidasi untuk memastikan format dan kelengkapan sesuai dengan skema yang ditentukan.

Hasil ekstraksi dari kedua skenario kemudian dinormalisasi dengan menyeragamkan format penulisan entitas, menghapus duplikasi dalam satu chunk, dan memetakan variasi penulisan ke bentuk kanonik. Hasil akhir disimpan dalam dua file terpisah: entities_srl.csv untuk hasil skenario SRL-based dan entities_llm.csv untuk hasil skenario LLM-based.

---

### 3.1.6 Pembentukan Relasi

Tahap pembentukan relasi bertujuan untuk menghubungkan entitas yang telah diekstraksi menjadi pasangan node-edge sehingga terbentuk struktur pengetahuan yang dapat dimasukkan ke basis data graf. Proses ini dilakukan pada hasil ekstraksi dari kedua skenario secara terpisah. Diagram alir tahap pembentukan relasi ditunjukkan pada Gambar 3.7.

[SISIPKAN GAMBAR 3.7 - Diagram Alir Pembentukan Relasi]

Proses pembentukan relasi diawali dengan identifikasi kandidat pasangan entitas yang berpotensi memiliki relasi. Pasangan entitas diidentifikasi berdasarkan kemunculan dalam chunk yang sama dan kedekatan posisi dalam teks. Entitas bertipe EVENT diprioritaskan sebagai penghubung karena dalam domain Sirah, peristiwa menjadi pusat keterhubungan antara tokoh, lokasi, dan waktu.

Penentuan tipe relasi dilakukan berdasarkan kombinasi label entitas yang membentuk pasangan. Pasangan PERSON dan EVENT menghasilkan relasi INVOLVED_IN yang menunjukkan keterlibatan tokoh dalam peristiwa. Pasangan EVENT dan LOCATION menghasilkan relasi OCCURRED_AT yang menunjukkan lokasi terjadinya peristiwa. Pasangan EVENT dan TIME menghasilkan relasi OCCURRED_ON yang menunjukkan waktu terjadinya peristiwa. Rancangan tipe relasi ditunjukkan pada Tabel 3.3.

[SISIPKAN TABEL 3.3 - Rancangan Tipe Relasi]

Ekstraksi relasi dari konteks dilakukan dengan menganalisis struktur kalimat untuk mengkonfirmasi relasi, menggunakan kata kunci pemicu relasi seperti "di", "pada", "ketika", dan "terlibat", serta memvalidasi relasi dengan konteks semantik. Setiap relasi yang diekstraksi dilengkapi dengan informasi provenance berupa chunk_id, halaman, dan evidence (cuplikan kalimat sebagai bukti relasi) untuk memungkinkan pelacakan kembali ke sumber.

Tahap terakhir adalah deduplikasi dan normalisasi relasi dengan menggabungkan relasi yang sama dari konteks berbeda, memetakan entitas ke bentuk kanonik, dan menghapus relasi duplikat. Hasil akhir diekspor dalam format edge list ke dua file terpisah: relations_srl.csv untuk hasil skenario SRL-based dan relations_llm.csv untuk hasil skenario LLM-based.

---

### 3.1.7 Konstruksi Knowledge Graph di Neo4j

Tahap konstruksi knowledge graph bertujuan untuk membangun basis data graf di Neo4j berdasarkan entitas dan relasi yang telah diekstraksi. Proses ini menghasilkan dua graf terpisah: Graf A dari hasil SRL-based NER dan Graf B dari hasil LLM-based NER. Diagram alir tahap konstruksi knowledge graph ditunjukkan pada Gambar 3.8.

[SISIPKAN GAMBAR 3.8 - Diagram Alir Konstruksi Knowledge Graph]

Proses konstruksi diawali dengan perancangan skema graf yang mendefinisikan struktur data dalam Neo4j. Skema graf terdiri dari empat label node yaitu Person untuk entitas tokoh, Event untuk entitas peristiwa, Location untuk entitas lokasi, dan Time untuk entitas waktu. Tiga tipe relationship didefinisikan yaitu INVOLVED_IN yang menghubungkan Person ke Event, OCCURRED_AT yang menghubungkan Event ke Location, dan OCCURRED_ON yang menghubungkan Event ke Time. Setiap node memiliki properti name untuk nama entitas dalam bentuk kanonik, aliases untuk variasi nama atau sebutan lain, dan source_chunks untuk daftar chunk_id sumber.

Setelah skema dirancang, dilakukan inisialisasi database Neo4j dengan membuat database baru untuk masing-masing graf dan mengatur konfigurasi koneksi. Constraint dan index kemudian dibuat untuk mencegah duplikasi node dan mengoptimasi kueri. Uniqueness constraint diterapkan pada properti name untuk setiap label node sehingga tidak ada dua node dengan nama yang sama dalam satu label.

Proses import node dilakukan dengan membaca file entitas dan membuat node dengan label sesuai tipe entitas. Perintah MERGE digunakan untuk menghindari duplikasi di mana node baru dibuat jika belum ada, atau properti diperbarui jika node sudah ada. Setelah semua node dibuat, proses import relationship dilakukan dengan membaca file relasi, mencocokkan source dan target node berdasarkan nama, dan membuat relationship dengan tipe yang sesuai. Setiap relationship dilengkapi dengan properti evidence dan chunk_ids untuk menyimpan informasi provenance.

Tahap terakhir adalah validasi graf untuk memastikan konstruksi berhasil. Validasi meliputi pemeriksaan jumlah node per label, pemeriksaan jumlah relationship per tipe, pengujian kueri sederhana untuk memastikan graf dapat diakses, dan verifikasi tidak ada orphan node (node tanpa relationship). Output dari tahap ini adalah dua basis data graf Neo4j yang siap untuk pengujian dan evaluasi.

---

### 3.1.8 Pengujian dan Evaluasi

Tahap pengujian dan evaluasi bertujuan untuk memvalidasi kualitas hasil ekstraksi entitas serta memverifikasi kelayakan struktur basis data graf dalam mendukung penelusuran informasi relasional pada domain Sirah Nabawiyah. Evaluasi dalam penelitian ini terbagi menjadi dua bagian utama, yaitu evaluasi hasil Named Entity Recognition (NER) dan evaluasi fungsional basis data graf. Desain evaluasi secara keseluruhan ditunjukkan pada Tabel 3.4, dan diagram alir tahap pengujian dan evaluasi ditunjukkan pada Gambar 3.9.

[SISIPKAN TABEL 3.4 - Ringkasan Desain Evaluasi]

| Aspek Evaluasi          | Metode                                          | Metrik/Output                                      |
|-------------------------|------------------------------------------------|---------------------------------------------------|
| Kualitas Ekstraksi NER  | Perbandingan prediksi vs ground truth          | Precision, Recall, F1-score per label dan agregat |
| Kualitas Graf           | Pengujian kueri Cypher + perbandingan struktur | Tingkat keberhasilan kueri, statistik node/edge   |

[SISIPKAN GAMBAR 3.9 - Diagram Alir Pengujian dan Evaluasi]

#### 3.1.8.1 Evaluasi Hasil Named Entity Recognition

Evaluasi NER bertujuan untuk mengukur kemampuan kedua skenario ekstraksi (SRL-based NER dan LLM-based NER) dalam mengenali dan mengklasifikasikan entitas dari teks Sirah Nabawiyah. Evaluasi ini dilakukan dengan membandingkan hasil prediksi entitas terhadap data ground truth yang telah dianotasi secara manual. Selain mengukur performa masing-masing skenario, evaluasi juga bertujuan untuk membandingkan kedua pendekatan guna mengidentifikasi kelebihan dan kekurangan masing-masing metode dalam konteks domain Sirah.

Proses evaluasi NER diawali dengan persiapan data uji yang diambil dari data ground truth (30% dari hasil manual labelling). Data uji ini tidak pernah digunakan dalam proses pseudo-labelling sehingga dapat memberikan gambaran objektif tentang kemampuan generalisasi model. Distribusi label dalam data uji dipastikan representatif mencakup keempat tipe entitas (PERSON, EVENT, LOCATION, dan TIME).

Selanjutnya, kedua skenario ekstraksi dijalankan pada data uji yang sama. Skenario SRL-based NER dan LLM-based NER masing-masing menghasilkan prediksi entitas yang kemudian dibandingkan dengan ground truth. Pencocokan prediksi dengan ground truth menggunakan kriteria exact match di mana teks entitas dan label harus sama persis agar dianggap sebagai prediksi yang benar. Berdasarkan hasil pencocokan, setiap prediksi dikategorikan ke dalam True Positive (TP) untuk prediksi benar, False Positive (FP) untuk prediksi yang tidak sesuai ground truth, dan False Negative (FN) untuk entitas yang tidak berhasil diprediksi.

Perhitungan metrik evaluasi dilakukan untuk setiap label entitas dan secara agregat. Metrik yang digunakan meliputi Precision yang mengukur proporsi prediksi benar dari seluruh prediksi yang dihasilkan, Recall yang mengukur proporsi entitas yang berhasil ditemukan dari seluruh entitas yang seharusnya ada, dan F1-score yang merupakan rata-rata harmonik dari Precision dan Recall. Macro-average F1-score dihitung sebagai metrik agregat dengan merata-ratakan F1-score semua label. Rumus perhitungan metrik mengacu pada penjelasan di Bab 2.

Tahap terakhir adalah analisis perbandingan untuk membandingkan performa SRL-based NER dengan LLM-based NER. Analisis mencakup identifikasi label mana yang paling mudah atau sulit diekstraksi oleh masing-masing metode, serta pola kesalahan yang sering terjadi seperti entitas yang terlewat atau salah klasifikasi label. Output dari evaluasi NER berupa tabel perbandingan metrik kedua skenario per label, metrik agregat, dan analisis kualitatif mengenai karakteristik performa masing-masing pendekatan.

#### 3.1.8.2 Evaluasi Fungsional Basis Data Graf

Evaluasi fungsional graf bertujuan untuk memverifikasi bahwa struktur graf yang dibangun dapat mendukung penelusuran informasi relasional pada domain Sirah Nabawiyah. Mengingat penelitian ini menghasilkan dua graf terpisah dari kedua skenario ekstraksi, evaluasi juga bertujuan untuk membandingkan kelayakan Graf A (hasil SRL-based NER) dan Graf B (hasil LLM-based NER) dalam menjawab kueri relasional.

Evaluasi fungsional dilakukan melalui pendekatan pengujian berbasis skenario kueri (query-based functional testing). Pendekatan ini dipilih karena tujuan utama konstruksi graf adalah untuk mendukung penelusuran informasi berbasis relasi, sehingga kemampuan graf dalam menjawab kueri menjadi indikator utama kelayakannya.

Proses evaluasi diawali dengan perancangan skenario kueri yang merepresentasikan berbagai kebutuhan penelusuran informasi pada domain Sirah Nabawiyah. Kueri dirancang untuk menguji berbagai pola relasi dalam graf, mencakup kueri berbasis tokoh, kueri berbasis lokasi, kueri berbasis waktu, dan kueri multi-hop yang melibatkan lebih dari satu pola relasi. Rancangan skenario kueri ditunjukkan pada Tabel 3.5.

[SISIPKAN TABEL 3.5 - Skenario Kueri Evaluasi Graf]

| No | Kategori        | Contoh Pertanyaan                                          | Pola Relasi                                                 |
|----|-----------------|------------------------------------------------------------|------------------------------------------------------------|
| 1  | Berbasis Tokoh  | Siapa saja yang terlibat dalam Perang Badar?               | (Person)-[INVOLVED_IN]->(Event)                            |
| 2  | Berbasis Lokasi | Peristiwa apa saja yang terjadi di Madinah?                | (Event)-[OCCURRED_AT]->(Location)                          |
| 3  | Berbasis Waktu  | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah?        | (Event)-[OCCURRED_ON]->(Time)                              |
| 4  | Tokoh-Peristiwa | Peristiwa apa saja yang melibatkan Abu Bakar?              | (Person)-[INVOLVED_IN]->(Event)                            |
| 5  | Multi-hop       | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | (Person)-[INVOLVED_IN]->(Event)-[OCCURRED_AT]->(Location)  |
| 6  | Timeline        | Urutkan peristiwa di Mekah berdasarkan waktu               | (Event)-[OCCURRED_AT]->(Location) + (Event)-[OCCURRED_ON]->(Time) |

Setiap kueri Cypher yang telah dirancang dijalankan pada kedua graf. Hasil yang dikembalikan oleh masing-masing graf dicatat untuk analisis lebih lanjut. Verifikasi hasil kueri dilakukan untuk memastikan kebenaran dan kelayakan hasil melalui beberapa kriteria: kueri dapat dieksekusi tanpa error, hasil kueri tidak kosong yang menunjukkan graf memiliki data relevan, hasil kueri sesuai dengan fakta dalam teks sumber melalui validasi manual, dan hasil kueri dapat dilacak kembali ke dokumen sumber melalui metadata provenance.

Selain evaluasi berbasis kueri, dilakukan juga perbandingan statistik struktur antara Graf A dan Graf B. Perbandingan mencakup jumlah node per label (Person, Event, Location, Time) dan jumlah relationship per tipe (INVOLVED_IN, OCCURRED_AT, OCCURRED_ON). Perbandingan ini bertujuan untuk mengidentifikasi perbedaan cakupan informasi yang berhasil diekstraksi oleh masing-masing skenario.

Output dari evaluasi fungsional graf meliputi tabel hasil eksekusi kueri untuk kedua graf yang mencakup status keberhasilan dan jumlah hasil, tabel perbandingan statistik struktur graf, contoh hasil kueri dari masing-masing graf sebagai ilustrasi, serta analisis perbandingan kelayakan Graf A dan Graf B dalam mendukung penelusuran informasi relasional pada domain Sirah Nabawiyah.

---

## 3.2 Spesifikasi Lingkungan

### 3.2.1 Perangkat Keras

Eksperimen komputasi pada penelitian ini dijalankan pada lingkungan perangkat keras komputer lokal sebagai media utama pengolahan data, mulai dari ekstraksi teks berbasis OCR, penyusunan dataset, prapemrosesan, chunking, hingga proses anotasi manual dan integrasi ke Neo4j. Spesifikasi perangkat yang digunakan meliputi prosesor Intel(R) Core(TM) i7-8750H @ 2.20GHz, RAM 16 GB, serta penyimpanan 1 TB. Pada implementasi OCR dan pemrosesan NLP, komputasi dapat berjalan pada CPU, sehingga kebutuhan GPU bersifat opsional dan lebih relevan apabila pada tahap lanjutan dilakukan eksperimen model berbasis deep learning atau LLM secara lokal.

### 3.2.2 Perangkat Lunak

Seluruh proses penelitian diimplementasikan menggunakan bahasa pemrograman Python pada lingkungan Jupyter Notebook untuk memudahkan eksperimen bertahap dan pencatatan keluaran tiap modul. Ekstraksi teks dilakukan menggunakan PaddleOCR dengan konfigurasi bahasa Indonesia, sedangkan konversi PDF ke citra dilakukan menggunakan library pdf2image dengan dukungan Poppler. Pengolahan data tabular dan manipulasi dataset dilakukan menggunakan library pandas dan numpy, sementara proses utilitas memanfaatkan library tqdm untuk progress monitoring dan modul regex untuk pemrosesan string.

Untuk pemrosesan NLP pada skenario SRL-based NER, digunakan library Stanza dengan model bahasa Indonesia untuk parsing dependensi dan ekstraksi struktur semantik. Pada skenario LLM-based NER, digunakan API dari penyedia LLM seperti OpenAI atau Google Gemini untuk melakukan ekstraksi entitas berbasis prompting. Konstruksi knowledge graph dilakukan menggunakan Neo4j Desktop sebagai DBMS graf dengan bahasa kueri Cypher, serta library neo4j untuk Python sebagai driver koneksi. Seluruh keluaran antara seperti hasil OCR per halaman, dokumen terstruktur JSON, dataset CSV chunking, dan hasil anotasi disimpan dalam format berkas terpisah agar alur kerja dapat direplikasi dan dievaluasi kembali.

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
2.      // Konversi PDF ke citra
3.      images ← ConvertPDFToImages(pdf_path)
4.      
5.      // OCR setiap halaman
6.      ocr_results ← []
7.      FOR EACH page_image IN images DO
8.          preprocessed ← PreprocessImage(page_image)
9.          text ← PaddleOCR.Extract(preprocessed, lang="id")
10.         ocr_results.APPEND({page_num, text})
11.     END FOR
12.     
13.     // Segmentasi berdasarkan TOC
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
30.     // Ekspor ke CSV
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
5.          // Filter baris tidak relevan
6.          IF row.judul_bab = "UNKNOWN" OR row.judul_bab = "BIBLIOGRAFI" THEN
7.              CONTINUE
8.          END IF
9.          
10.         // Normalisasi teks
11.         text ← row.teks
12.         text ← RemoveNonPrintingChars(text)
13.         text ← NormalizeWhitespace(text)
14.         text ← RemoveNonInformativeSymbols(text)
15.         text ← RemoveGibberish(text)
16.         
17.         row.teks ← text
18.         clean_dataset.APPEND(row)
19.     END FOR
20.     
21.     // Chunking
22.     chunks_dataset ← []
23.     chunk_id ← 0
24.     FOR EACH doc IN clean_dataset DO
25.         sentences ← SplitIntoSentences(doc.teks)
26.         
27.         current_chunk ← ""
28.         chunk_sentences ← []
29.         FOR EACH sentence IN sentences DO
30.             IF LENGTH(current_chunk + sentence) > 1500 THEN
31.                 // Simpan chunk saat ini
32.                 chunks_dataset.APPEND({
33.                     chunk_id: chunk_id,
34.                     doc_id: doc.id,
35.                     judul_bab: doc.judul_bab,
36.                     judul_sub_bab: doc.judul_sub_bab,
37.                     halaman: doc.halaman,
38.                     teks_chunk: current_chunk
39.                 })
40.                 chunk_id ← chunk_id + 1
41.                 
42.                 // Overlap: ambil kalimat terakhir
43.                 current_chunk ← chunk_sentences[LAST]
44.                 chunk_sentences ← [chunk_sentences[LAST]]
45.             END IF
46.             current_chunk ← current_chunk + " " + sentence
47.             chunk_sentences.APPEND(sentence)
48.         END FOR
49.         
50.         // Simpan chunk terakhir
51.         IF current_chunk ≠ "" THEN
52.             chunks_dataset.APPEND({...})
53.         END IF
54.     END FOR
55.     
56.     SaveCSV(chunks_dataset, "sirah_chunks.csv")
57.     RETURN chunks_dataset
58. END
```

### 3.3.3 Pseudocode SRL-based NER

Kode Semu 3.3 menunjukkan alur kerja ekstraksi entitas menggunakan pendekatan Semantic Role Labeling.

```
INPUT  : chunks_dataset (CSV berisi chunk teks)
OUTPUT : entities_srl (CSV berisi entitas hasil ekstraksi SRL)

ALGORITMA:
1.  BEGIN
2.      // Inisialisasi NLP pipeline
3.      nlp_pipeline ← InitializeStanzaPipeline(lang="id")
4.      entities_srl ← []
5.      
6.      FOR EACH chunk IN chunks_dataset DO
7.          chunk_text ← chunk.teks_chunk
8.          doc ← nlp_pipeline.Process(chunk_text)
9.          
10.         FOR EACH sentence IN doc.sentences DO
11.             predicates ← GetPredicates(sentence)
12.             
13.             FOR EACH predicate IN predicates DO
14.                 srl_result ← ExtractSemanticRoles(sentence, predicate)
15.                 
16.                 // ARG0 (pelaku) → PERSON
17.                 IF srl_result.ARG0 EXISTS THEN
18.                     candidate ← srl_result.ARG0.text
19.                     IF IsValidPersonName(candidate) THEN
20.                         entities_srl.APPEND({
21.                             chunk_id: chunk.chunk_id,
22.                             entity_text: candidate,
23.                             label: "PERSON",
24.                             start_pos: srl_result.ARG0.start,
25.                             end_pos: srl_result.ARG0.end
26.                         })
27.                     END IF
28.                 END IF
29.                 
30.                 // ARGM-LOC (lokasi) → LOCATION
31.                 IF srl_result.ARGM_LOC EXISTS THEN
32.                     candidate ← srl_result.ARGM_LOC.text
33.                     IF IsValidLocation(candidate) THEN
34.                         entities_srl.APPEND({
35.                             chunk_id: chunk.chunk_id,
36.                             entity_text: candidate,
37.                             label: "LOCATION",
38.                             start_pos: srl_result.ARGM_LOC.start,
39.                             end_pos: srl_result.ARGM_LOC.end
40.                         })
41.                     END IF
42.                 END IF
43.                 
44.                 // ARGM-TMP (waktu) → TIME
45.                 IF srl_result.ARGM_TMP EXISTS THEN
46.                     candidate ← srl_result.ARGM_TMP.text
47.                     entities_srl.APPEND({
48.                         chunk_id: chunk.chunk_id,
49.                         entity_text: candidate,
50.                         label: "TIME",
51.                         start_pos: srl_result.ARGM_TMP.start,
52.                         end_pos: srl_result.ARGM_TMP.end
53.                     })
54.                 END IF
55.                 
56.                 // Predicate → EVENT
57.                 event_candidate ← ExtractEventPhrase(sentence, predicate)
58.                 IF IsValidEvent(event_candidate) THEN
59.                     entities_srl.APPEND({
60.                         chunk_id: chunk.chunk_id,
61.                         entity_text: event_candidate,
62.                         label: "EVENT",
63.                         start_pos: predicate.start,
64.                         end_pos: predicate.end
65.                     })
66.                 END IF
67.             END FOR
68.         END FOR
69.     END FOR
70.     
71.     // Normalisasi dan deduplikasi
72.     entities_srl ← NormalizeEntities(entities_srl)
73.     entities_srl ← RemoveDuplicates(entities_srl)
74.     
75.     SaveCSV(entities_srl, "entities_srl.csv")
76.     RETURN entities_srl
77. END
```

### 3.3.4 Pseudocode LLM-based NER

Kode Semu 3.4 menunjukkan alur kerja ekstraksi entitas menggunakan Large Language Model.

```
INPUT  : chunks_dataset (CSV berisi chunk teks)
         seed_data (data seed untuk few-shot examples)
OUTPUT : entities_llm (CSV berisi entitas hasil ekstraksi LLM)

ALGORITMA:
1.  BEGIN
2.      // Persiapan prompt
3.      system_prompt ← ConstructSystemPrompt()
4.      few_shot_examples ← PrepareFewShotExamples(seed_data)
5.      entities_llm ← []
6.      
7.      FOR EACH chunk IN chunks_dataset DO
8.          user_prompt ← ConstructUserPrompt(chunk.teks_chunk, few_shot_examples)
9.          
10.         TRY
11.             response ← CallLLMAPI(
12.                 system_prompt: system_prompt,
13.                 user_prompt: user_prompt,
14.                 temperature: 0.1,
15.                 response_format: "json"
16.             )
17.             
18.             extracted_entities ← ParseJSON(response)
19.             
20.             FOR EACH entity IN extracted_entities DO
21.                 IF IsValidLabel(entity.label) THEN
22.                     entities_llm.APPEND({
23.                         chunk_id: chunk.chunk_id,
24.                         entity_text: entity.text,
25.                         label: entity.label,
26.                         start_pos: FindPosition(chunk.teks_chunk, entity.text),
27.                         end_pos: FindEndPosition(chunk.teks_chunk, entity.text)
28.                     })
29.                 END IF
30.             END FOR
31.             
32.         CATCH error
33.             LogError(chunk.chunk_id, error)
34.             CONTINUE
35.         END TRY
36.     END FOR
37.     
38.     // Normalisasi dan deduplikasi
39.     entities_llm ← NormalizeEntities(entities_llm)
40.     entities_llm ← RemoveDuplicates(entities_llm)
41.     
42.     SaveCSV(entities_llm, "entities_llm.csv")
43.     RETURN entities_llm
44. END

FUNCTION ConstructSystemPrompt()
    prompt ← "Kamu adalah sistem ekstraksi entitas untuk teks Sirah Nabawiyah.
    Tugasmu adalah mengidentifikasi dan mengekstraksi entitas dari teks.
    
    Label entitas:
    - PERSON: Nama tokoh (contoh: Abu Bakar, Rasulullah)
    - EVENT: Nama peristiwa (contoh: Perang Badar, Hijrah)
    - LOCATION: Nama lokasi (contoh: Mekah, Madinah)
    - TIME: Informasi waktu (contoh: tahun ke-2 Hijriah)
    
    Output dalam format JSON array:
    [{\"text\": \"nama entitas\", \"label\": \"LABEL\"}, ...]"
    
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
3.      entities_by_chunk ← GroupByChunkID(entities_data)
4.      
5.      FOR EACH chunk_id, chunk_entities IN entities_by_chunk DO
6.          chunk_text ← GetChunkText(chunks_dataset, chunk_id)
7.          
8.          // Kelompokkan entitas berdasarkan label
9.          events ← Filter(chunk_entities, label="EVENT")
10.         persons ← Filter(chunk_entities, label="PERSON")
11.         locations ← Filter(chunk_entities, label="LOCATION")
12.         times ← Filter(chunk_entities, label="TIME")
13.         
14.         FOR EACH event IN events DO
15.             // Relasi PERSON → EVENT (INVOLVED_IN)
16.             FOR EACH person IN persons DO
17.                 IF AreInSameContext(person, event, chunk_text) THEN
18.                     evidence ← ExtractEvidence(chunk_text, person, event)
19.                     relations.APPEND({
20.                         source_id: GenerateID(person),
21.                         source_text: person.entity_text,
22.                         source_label: "PERSON",
23.                         relation_type: "INVOLVED_IN",
24.                         target_id: GenerateID(event),
25.                         target_text: event.entity_text,
26.                         target_label: "EVENT",
27.                         chunk_id: chunk_id,
28.                         evidence: evidence
29.                     })
30.                 END IF
31.             END FOR
32.             
33.             // Relasi EVENT → LOCATION (OCCURRED_AT)
34.             FOR EACH location IN locations DO
35.                 IF AreInSameContext(event, location, chunk_text) THEN
36.                     evidence ← ExtractEvidence(chunk_text, event, location)
37.                     relations.APPEND({
38.                         source_id: GenerateID(event),
39.                         source_text: event.entity_text,
40.                         source_label: "EVENT",
41.                         relation_type: "OCCURRED_AT",
42.                         target_id: GenerateID(location),
43.                         target_text: location.entity_text,
44.                         target_label: "LOCATION",
45.                         chunk_id: chunk_id,
46.                         evidence: evidence
47.                     })
48.                 END IF
49.             END FOR
50.             
51.             // Relasi EVENT → TIME (OCCURRED_ON)
52.             FOR EACH time IN times DO
53.                 IF AreInSameContext(event, time, chunk_text) THEN
54.                     evidence ← ExtractEvidence(chunk_text, event, time)
55.                     relations.APPEND({
56.                         source_id: GenerateID(event),
57.                         source_text: event.entity_text,
58.                         source_label: "EVENT",
59.                         relation_type: "OCCURRED_ON",
60.                         target_id: GenerateID(time),
61.                         target_text: time.entity_text,
62.                         target_label: "TIME",
63.                         chunk_id: chunk_id,
64.                         evidence: evidence
65.                     })
66.                 END IF
67.             END FOR
68.         END FOR
69.     END FOR
70.     
71.     relations ← DeduplicateRelations(relations)
72.     SaveCSV(relations, "relations.csv")
73.     RETURN relations
74. END
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
2.      // Inisialisasi koneksi Neo4j
3.      driver ← Neo4jDriver.Connect(uri, username, password)
4.      session ← driver.Session(database=db_name)
5.      
6.      // Buat constraint untuk mencegah duplikasi
7.      session.Run("CREATE CONSTRAINT person_name IF NOT EXISTS 
8.                   FOR (p:Person) REQUIRE p.name IS UNIQUE")
9.      session.Run("CREATE CONSTRAINT event_name IF NOT EXISTS 
10.                  FOR (e:Event) REQUIRE e.name IS UNIQUE")
11.     session.Run("CREATE CONSTRAINT location_name IF NOT EXISTS 
12.                  FOR (l:Location) REQUIRE l.name IS UNIQUE")
13.     session.Run("CREATE CONSTRAINT time_name IF NOT EXISTS 
14.                  FOR (t:Time) REQUIRE t.name IS UNIQUE")
15.     
16.     // Import Node
17.     FOR EACH entity IN entities_data DO
18.         label ← CapitalizeFirst(entity.label)
19.         query ← "MERGE (n:" + label + " {name: $name})
20.                  ON CREATE SET n.source_chunks = [$chunk_id]
21.                  ON MATCH SET n.source_chunks = n.source_chunks + $chunk_id"
22.         session.Run(query, {
23.             name: NormalizeName(entity.entity_text),
24.             chunk_id: entity.chunk_id
25.         })
26.     END FOR
27.     
28.     // Import Relationship
29.     FOR EACH relation IN relations_data DO
30.         source_label ← CapitalizeFirst(relation.source_label)
31.         target_label ← CapitalizeFirst(relation.target_label)
32.         rel_type ← relation.relation_type
33.         
34.         query ← "MATCH (source:" + source_label + " {name: $source_name})
35.                  MATCH (target:" + target_label + " {name: $target_name})
36.                  MERGE (source)-[r:" + rel_type + "]->(target)
37.                  ON CREATE SET r.evidence = [$evidence], r.chunk_ids = [$chunk_id]
38.                  ON MATCH SET r.evidence = r.evidence + $evidence,
39.                               r.chunk_ids = r.chunk_ids + $chunk_id"
40.         session.Run(query, {
41.             source_name: NormalizeName(relation.source_text),
42.             target_name: NormalizeName(relation.target_text),
43.             evidence: relation.evidence,
44.             chunk_id: relation.chunk_id
45.         })
46.     END FOR
47.     
48.     // Validasi graf
49.     Print("Node Person:", session.Run("MATCH (n:Person) RETURN count(n)"))
50.     Print("Node Event:", session.Run("MATCH (n:Event) RETURN count(n)"))
51.     Print("Node Location:", session.Run("MATCH (n:Location) RETURN count(n)"))
52.     Print("Node Time:", session.Run("MATCH (n:Time) RETURN count(n)"))
53.     Print("Rel INVOLVED_IN:", session.Run("MATCH ()-[r:INVOLVED_IN]->() RETURN count(r)"))
54.     Print("Rel OCCURRED_AT:", session.Run("MATCH ()-[r:OCCURRED_AT]->() RETURN count(r)"))
55.     Print("Rel OCCURRED_ON:", session.Run("MATCH ()-[r:OCCURRED_ON]->() RETURN count(r)"))
56.     
57.     session.Close()
58.     driver.Close()
59.     Print("Graph construction completed for database:", db_name)
60. END
```

---

## 3.4 Urutan Pelaksanaan Penelitian

Penelitian Tugas Akhir ini akan dilaksanakan selama 16 minggu dari Januari sampai dengan Mei 2026. Lini masa pengerjaan Tugas Akhir ditunjukkan pada Tabel 3.6.

[SISIPKAN TABEL 3.6 - Lini Masa Pengerjaan Tugas Akhir]
