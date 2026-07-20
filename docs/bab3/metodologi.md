<!-- SUMBER: docs/Buku-TA-Genta-fixed.pdf (buku terbaru), diekstrak 2026-07-19. Cermin TEKS untuk rujukan revisi; tabel/gambar/persamaan dipipihkan. Backup .md lama: metodologi.md.bak_pre_pdf_sync -->

# BAB 3 METODOLOGI

## 3.1 Perancangan Sistem

Penelitian tugas akhir ini bertujuan untuk membangun Knowledge Graph Sirah Nabawiyah menggunakan pendekatan Named-Entity Recognition berbasis Semantic Role Labeling. Untuk mencapai tujuan tersebut, penelitian ini dilakukan melalui beberapa tahapan utama. Alur pengerjaan penelitian ditampilkan dalam bentuk flowchart sebagaimana ditunjukkan pada Gambar 3.1.

Gambar 3.1 Diagram Alir Metodologi Penelitian ini membutuhkan dukungan perangkat keras dan perangkat lunak sebagai penunjang seluruh proses pengerjaan, mulai dari tahap pengolahan data hingga konstruksi Knowledge Graph. Perangkat keras yang digunakan dalam penelitian ini adalah laptop sebagai media utama. Spesifikasi perangkat keras tersebut dapat dilihat pada Tabel 3.1. **Tabel 3.1 Spesifikasi Perangkat Keras Penelitian**

| Komponen | Spesifikasi |
|---|---|
| Prosesor | Intel Core i7-8750H @ 2.20GHz |
| RAM | 16 GB |
| Penyimpanan | 1 TB |
| GPU | opsional |

Khusus pada tahap pelatihan model SRL-Based Named-Entity Recognition berbasis IndoBERT yang membutuhkan akselerasi Graphics Processing Unit (GPU), proses pelatihan dilakukan melalui lingkungan komputasi awan Google Colab dengan dukungan GPU NVIDIA Tesla T4. Sementara itu, tahapan lain seperti preparasi dataset, preprocessing data, chunking, anotasi, ekstraksi relasi, dan konstruksi Knowledge Graph dapat dijalankan menggunakan CPU pada komputer lokal. Dengan demikian, penggunaan GPU pada komputer lokal bersifat opsional dan tidak menjadi kebutuhan utama dalam keseluruhan proses penelitian.

Seluruh proses implementasi dilakukan menggunakan bahasa pemrograman Python pada lingkungan Jupyter Notebook. Penggunaan Jupyter Notebook bertujuan untuk memudahkan proses eksperimen secara bertahap, pengujian setiap modul, serta pencatatan keluaran dari masing-masing tahapan. Daftar perangkat lunak dan pustaka utama yang digunakan dalam penelitian ini ditunjukkan pada Tabel 3.2. **Tabel 3.2 Spesifikasi Perangkat Lunak Penelitian**

| Komponen | Nama Perangkat Lunak | Spesifikasi | Fungsi |
|---|---|---|---|
| Bahasa Pemrograman | Python | Versi 3.10.6 | Bahasa utama implementasi seluruh tahap pipeline |
| Lingkungan Kerja | Jupyter Notebook, Google Colab | GPU T4 | Eksekusi eksperimen bertahap dan pelatihan model dengan akselerasi GPU |
| OCR | PaddleOCR | Versi 2.7.0.3, konfigurasi Bahasa Indonesia | Mengekstraksi teks dari citra hasil pindai halaman PDF |
| Konversi PDF ke citra | PyMuPDF, Pillow | PyMuPDF 1.20.2, Pillow 10.0.0 | Mengubah tiap halaman PDF menjadi citra untuk diproses OCR |
| Pemodelan NER | PyTorch, Hugging Face Transformers, IndoBERT | PyTorch 2.12.0, Transformers 5.9.0, model indolem/indobert- base-uncased | Melatih dan menjalankan model NER berbasis IndoBERT |
| Evaluasi NER | seqeval, scikit-learn | seqeval 1.2.2, scikit-learn 1.7.2 | Menghitung metrik evaluasi entitas (presisi, recall, F1) |
| Pengolahan Data | pandas, numpy | pandas 2.3.3, numpy 1.23.5 | Manipulasi dan pengolahan data tabular antar tahap |
| Pencocokan String | jellyfish | Jaro-Winkler | Mengelompokkan variasi penulisan nama entitas (alias clustering) |
| Basis Data Graf | Neo4j Desktop | Versi 2.1.3 | Menyimpan dan mengueri Knowledge Graph |
| Analisis Jaringan | Network-X, python- louvain | NetworkX 3.4.2 | Analisis jaringan sosial (sentralitas, deteksi komunitas) |
| Utilitas | regex, tqdm | regex 2026.5.9, tqdm 4.67.1 | Pencocokan pola teks dan penampil progres proses |

## 3.2 Preparasi Dataset

Tahap preparasi dataset bertujuan mengubah dokumen Sirah Nabawiyah berformat PDF hasil pindai menjadi dataset teks terstruktur yang siap diolah. Sumber data adalah buku Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan Kathur Suhardi) sebanyak sekitar 633 halaman dalam Bahasa Indonesia. Diagram alir tahap ini ditunjukkan pada Gambar 3.2. Dokumen Sirah Nabawiyah yang digunakan dalam penelitian ini berbentuk berkas PDF hasil pindai (scan), sehingga tidak memiliki lapisan teks digital yang dapat langsung diproses. Oleh karena itu, setiap halaman PDF terlebih dahulu dirender menjadi citra, kemudian teks pada citra tersebut diekstraksi menggunakan PaddleOCR dengan konfigurasi bahasa Indonesia. Hasil ekstraksi OCR disimpan dalam bentuk berkas teks polos untuk setiap halaman dengan pola penamaan page_[nomor].txt. Dengan demikian, data masukan tahap ini terdiri atas dua komponen utama, yaitu kumpulan berkas teks per halaman dalam format .txt hasil OCR, dan berkas daftar isi acuan (ground truth) dalam format JSON. Berkas daftar isi ini memuat judul bab dan sub-bab beserta nomor halaman awalnya. Kedua komponen ini digunakan sebagai masukan pada tahap preparasi dataset, yang terdiri atas dua langkah utama, yaitu ekstraksi dokumen terstruktur dan konversi hasil ekstraksi ke dalam berkas CSV.

Gambar 3.2 Diagram Alir Preparasi Dataset Tahapan berikutnya adalah ekstraksi dokumen terstruktur, dimana pada tahap ini kumpulan teks per halaman disusun kembali mengikuti struktur dokumen pada daftar isi (Table of Contents). Langkah pertama, daftar isi diubah menjadi indeks pencarian berupa pemetaan antara nomor halaman dan kumpulan judul bab atau subbab yang dimulai pada halaman tersebut. Selanjutnya, setiap berkas halaman dibaca secara berurutan. Bagian footer berulang seperti teks "Sirah Nabawiyah", kata "halaman", dan nomor halaman yang umumnya terdapat pada dua baris terakhir, dihapus agar tidak masuk ke dalam isi dokumen. Setelah proses pembersihan footer, setiap baris teks diperiksa untuk menentukan apakah baris tersebut merupakan judul bab, judul subbab, atau isi paragraf. Pemeriksaan dilakukan dengan mencocokkan baris teks terhadap indeks daftar isi menggunakan exact matching. Apabila tidak ditemukan kecocokan secara langsung, proses dilanjutkan dengan fuzzy matching menggunakan rasio kemiripan string dengan ambang batas 0,92. Pendekatan ini digunakan karena hasil OCR dapat mengalami kesalahan pengenalan karakter atau memecah satu judul menjadi beberapa baris. Untuk mengatasi kondisi tersebut, kandidat judul dibentuk dari gabungan satu hingga tiga baris berurutan. Apabila suatu baris atau gabungan baris teridentifikasi sebagai judul bab atau subbab, maka baris tersebut digunakan untuk membuka konteks bab atau subbab baru. Sebaliknya, apabila baris tidak cocok dengan judul pada daftar isi, maka baris tersebut diperlakukan sebagai paragraf isi dan dilekatkan pada subbab yang sedang aktif. Setelah seluruh halaman selesai diproses, isi dari setiap subbab digabungkan menjadi satu rangkaian teks terstruktur. Langkah- langkah dari proses ekstraksi dokumen terstruktur ini ditunjukkan pada Kode Semu 3.1. INPUT:
- ocr_dir: folder berkas teks OCR per halaman dengan format page_[nomor].txt
- toc_data: daftar isi acuan yang memuat judul bab/sub-bab dan halaman mulai OUTPUT: document: dokumen terstruktur dalam format JSON dengan struktur bab -> sub-bab -> teks

1. BEGIN
2.     toc_index <- BuildTocIndex(toc_data)
3.     document <- []
4.     current_bab <- NULL
5.     current_subbab <- NULL 6.

7.     FOR EACH file IN SortByPageNumber(ocr_dir) DO 8.
9.         page <- ParsePageNumber(file)
10.         lines <- ReadNonEmptyLines(file)
11.         lines <- StripFooter(lines) 12.
13.         i <- 0 14.
15.         WHILE i < LENGTH(lines) DO 16.
17.             candidates <- BuildCandidates(lines, i)
18.             match <- BestTocMatch(candidates, page, toc_index) 19.
20.             IF match <> NULL THEN 21.
22.                 IF match.type = "BAB" THEN
23.                     current_bab <- {
24.                         bab_title: match.title,
25.                         subbab: []
26.                     } 27.
28.                     document.APPEND(current_bab)
29.                     current_subbab <- NULL 30.
31.                 ELSE IF match.type = "SUBBAB" THEN
32.                     current_subbab <- {
33.                         subbab_title: match.title,
34.                         content: [],
35.                         pages: [page]
36.                     } 37.
38.                     current_bab.subbab.APPEND(current_subbab)
39.                 END IF
40.                 i <- i + match.lines_used
41.             ELSE
42.                 EnsureActiveBabSubbab(current_bab, current_subbab)
43.                 current_subbab.content.APPEND(lines[i])
44.                 AddPageIfNew(current_subbab.pages, page)
45.                 i <- i + 1
46.             END IF
47.         END WHILE
48.     END FOR 49.
50.     document <- MergeContentPerSubbab(document)
51.     SaveJSON(document, "document_full.json") 52.
53.     RETURN document
54. END Kode Semu 3.1 Ekstraksi Data dengan Output JSON Keluaran langkah ekstraksi adalah dokumen terstruktur berformat JSON yang menyusun teks secara hierarkis, dimana setiap bab memuat daftar sub-bab, dan setiap sub-bab memuat judul, isi teks, serta daftar halaman sumber. Contoh potongan keluaran dari langkah ini dapat dilihat pada kode sumber berikut ini. Tabel 3.3 Contoh Keluaran Ekstraksi Data dengan format JSON [   {

"bab_title": "Letak Geografis dan Kaum Bangsa Arab",     "subbab": [       {         "subbab_title": "Sebab Penulisan Sirah Nabawiyah",         "content": ["Pada hakikatnya istilah Sirah Nabawiyah merupakan ungkapan tentang risalah yang dibawa Rasulullah kepada manusia ..."],         "pages": [21, 22]       }     ]   } ]

Dokumen JSON terstruktur kemudian diratakan (flatten) menjadi tabel agar mudah diolah pada tahap selanjutnya. Setiap pasangan bab dan sub-bab menjadi satu baris dengan empat kolom: judul_bab, judul_sub_bab, halaman, dan teks. Daftar nomor halaman yang berurutan diringkas menjadi bentuk rentang agar ringkas, misalnya [21, 22, 23, 26] menjadi "21-23, 26". Tabel hasil disimpan sebagai berkas CSV dengan pemisah titik koma (;) dan pengodean utf-8-sig. Penerapan langkah ini ditunjukkan pada Kode Semu 3.2. INPUT:     document: dokumen terstruktur JSON hasil ekstraksi OUTPUT:     dataset: berkas CSV per sub-bab dengan atribut judul_bab, judul_sub_bab, halaman, dan teks

1. BEGIN 2.
3.     rows <- [] 4.
5.     FOR EACH bab IN document DO
6.         FOR EACH sub IN bab.subbab DO
7.             halaman <- PagesToRanges(sub.pages)
8.             teks <- JoinLines(sub.content)
9.             row <- {
10.                 judul_bab     : bab.bab_title,
11.                 judul_sub_bab : sub.subbab_title,
12.                 halaman       : halaman,
13.                 teks          : teks
14.             }
15.             rows.APPEND(row)
16.         END FOR
17.     END FOR 18.
19.     dataset <- ToDataFrame(rows) 20.
21.     SaveCSV(
22.         dataset,
23.         "sirah_simple.csv",
24.         sep = ";",
25.         encoding = "utf-8-sig"
26.     ) 27.
28.     RETURN dataset
29. END

Kode Semu 3.2 Konversi Data JSON menjadi CSV Kode Semu 3.2 menunjukkan tahapan umum proses perataan (flattening) dokumen JSON terstruktur menjadi bentuk tabel. Proses ini diawali dengan menelusuri struktur dokumen dua tingkat, yaitu bab dan sub-bab yang berada di dalamnya. Pada setiap sub-bab, daftar nomor halaman diringkas ke dalam bentuk rentang halaman, sedangkan potongan isi teks digabungkan menjadi satu kesatuan teks utuh. Selanjutnya, informasi tersebut disusun bersama judul bab dan judul sub-bab menjadi satu baris data. Setelah seluruh sub-bab selesai diproses, kumpulan baris data tersebut diubah menjadi dataframe dan disimpan dalam format CSV. Hasil akhir dari proses ini berupa dataset tabular yang terdiri atas kolom judul_bab, judul_sub_bab, halaman, dan teks. Struktur dataset tersebut dijelaskan pada Tabel 3.4, dengan setiap baris merepresentasikan satu sub-bab beserta isi teksnya. Dengan demikian, keluaran dari tahap ini menyajikan teks Sirah dalam format yang lebih ringkas dan mudah diolah pada tahap selanjutnya, tanpa menghilangkan keterhubungan teks dengan bab, sub-bab, dan halaman sumbernya. **Tabel 3.4 Struktur Keluaran Dataset**

| Nama Kolom | Tipe Data | Deskripsi | Contoh Nilai |
|---|---|---|---|
| judul_bab | String | Nama bab utama hasil segmentasi berdasarkan daftar isi | POSISI BANGSA ARAB DAN KAUMNYA |
| judul_sub_bab | String | Nama sub-bab di bawah bab terkait | Posisi Bangsa Arab |
| halaman | String | Rentang halaman sumber konten sub-bab | 34-35 |
| teks | String | Isi teks sub-bab yang sudah dibersihkan dan digabung | Menurut bahasa, Arab artinya padang pasir, tanah gundul, dan gersang yang tiada air dan tanamannya … |

## 3.3 Preprocessing

Tahap preprocessing bertujuan untuk membersihkan dataset dari noise hasil OCR serta menstabilkan teks agar lebih siap digunakan pada proses ekstraksi entitas dan relasi. Kualitas hasil OCR sangat berpengaruh terhadap tahapan berikutnya, sehingga preprocessing menjadi tahap yang penting dalam alur penelitian ini. Diagram alir tahap preprocessing ditunjukkan pada Gambar 3.3.

Gambar 3.3 Diagram Alir Tahapan Preprocessing Proses preprocessing diawali dengan menyaring baris data yang tidak relevan, yaitu baris dengan label UNKNOWN BAB sebagai hasil segmentasi yang tidak berhasil, serta bagian bibliografi atau daftar pustaka. Penyaringan ini dilakukan agar data yang diproses hanya mencakup konten naratif utama. Setelah itu, dilakukan normalisasi dan pembersihan ringan (light cleanup) pada setiap teks. Tahapan ini mencakup penghapusan karakter non-printable dan karakter tak terlihat seperti zero-width space, penghapusan simbol non-informatif yang sering muncul pada hasil OCR, seperti @, *, #, simbol bullet, &, |, <>, [], ~, dan ^, serta normalisasi variasi apostrof dan tanda ain dalam transliterasi Arab menjadi satu bentuk apostrof standar. Normalisasi ini diperlukan agar penulisan nama seperti Ka'bah dan Qur'an menjadi konsisten. Selain itu, tahap ini juga memperbaiki spasi berlebih pada partikel Arab seperti Al- dan Ar-, misalnya bentuk Al- Julunda dikoreksi menjadi Al-Julunda. Tahap selanjutnya adalah pembersihan gibberish, yaitu penghapusan token atau kalimat tidak bermakna yang muncul akibat kesalahan OCR. Pembersihan dilakukan secara bertingkat, meliputi tingkat token, segmen, dan kalimat. Pada tingkat token, sistem menghapus bentuk tidak wajar seperti campuran huruf dan angka, misalnya K1Aq. Pada tingkat segmen, sistem menghapus rangkaian tiga token aneh atau lebih yang muncul secara berurutan. Pada tingkat kalimat, sistem menghapus kalimat yang memiliki proporsi token aneh sebesar 50% atau lebih. Token yang dikategorikan sebagai aneh mencakup angka murni, huruf kapital tunggal, campuran huruf besar dan kecil yang tidak wajar, serta token pendek yang bukan termasuk kata umum Bahasa Indonesia maupun singkatan keagamaan yang lazim dalam teks Sirah, seperti SAW, SWT, RA, AS, dan HR. Proses ditutup dengan menghapus baris yang menjadi kosong setelah pembersihan. Implementasi pada tahap ini ditunjukkan pada Kode Semu 3.3. INPUT: raw_dataset: CSV hasil preparasi dataset OUTPUT: clean_dataset: CSV dengan tambahan kolom teks_clean

1. BEGIN
2.     clean_dataset <- [] 3.
4.     FOR EACH row IN raw_dataset DO
5.         IF row.judul_bab IN {"UNKNOWN BAB", "BIBLIOGRAFI"} THEN
6.             CONTINUE
7.         END IF 8.
9.         text <- row.teks
10.         text <- RemoveNonPrintable(text)
11.         text <- RemoveNonInformativeSymbols(text)
12.         text <- NormalizeApostrophe(text)
13.         text <- FixArabicPrefixSpacing(text)
14.         text <- RemoveGibberish(text) 15.
16.         IF Trim(text) <> "" THEN
17.             row.teks_clean <- text
18.             clean_dataset.APPEND(row)
19.         END IF
20.     END FOR
21.     SaveCSV(clean_dataset, "sirah_simple_clean.csv")
22.     RETURN clean_dataset
23. END Kode Semu 3.3 Preprocessing Teks Hasil OCR Hasil akhir dari proses ini berupa dataset bersih yang memuat kolom judul_bab, judul_sub_bab, halaman, dan teks_clean. Keluaran tahap ini tidak hanya berfungsi untuk

menghilangkan noise hasil OCR, tetapi juga menjaga konsistensi penulisan nama entitas yang mengandung prefiks dan apostrof Arab agar teks lebih siap digunakan pada tahap chunking dan ekstraksi entitas. Sebagai contoh, fragmen OCR Al- Julunda diperbaiki menjadi Al-Julunda, sedangkan penulisan apostrof yang tidak konsisten seperti Ka`bah diseragamkan menjadi Ka'bah. Perbaikan ini membantu mempertahankan bentuk nama entitas secara lebih konsisten sehingga dapat mendukung proses NER pada tahap berikutnya. Contoh perubahan nyata pada beberapa kalimat dari korpus untuk tiap jenis operasi preprocessing ditunjukkan pada Tabel 3.5. **Tabel 3.5 Contoh Perubahan Hasil Preprocessing**

| Operasi | Sebelum | Sesudah |
|---|---|---|
| Perbaikan spasi prefiks Arab (Al-/Ar-) | Al- Ahzab | Al-Ahzab |
|  | Al- Walid | Al-Walid |
|  | Mariah Al- Qibtiyah | Mariah Al-Qibtiyah |
| Normalisasi varian apostrof/ain | Qur`an | Qur'an |
|  | Isra`kan | Isra'kan |
|  | Al-Qur`anul | Al-Qur'anul |
| Penghapusan simbol non-informatif | Muhammad & | Muhammad |
|  | Muththalib & | Muththalib |
|  | Rasulullah @ | Rasulullah |
| Pembersihan gibberish (token/segmen/kalimat) | ... bin Sawa 430 431 6. | ... bin Sawa |
|  | (021) 8507590, 8506702 Fax. | (seluruh kalimat dihapus) |
|  | xI Ls xO J JI J O aa O s!LcK ... | (seluruh kalimat dihapus) | xI Ls xO J JI J O aa O s!LcK ... (seluruh kalimat dihapus)

## 3.4 Chunking

Tahap chunking bertujuan untuk memecah teks pada setiap sub-bab menjadi potongan teks (chunk) yang lebih kecil, tetapi tetap mempertahankan kesinambungan konteks. Pemecahan ini diperlukan karena teks pada satu sub-bab dapat memiliki panjang yang cukup besar sehingga kurang efisien untuk proses anotasi maupun pemrosesan NER. Diagram alir tahap chunking ditunjukkan pada Gambar 3.4.

Gambar 3.4 Diagram Alir Tahapan Chunking Proses chunking diawali dengan segmentasi teks bersih menjadi beberapa kalimat berdasarkan tanda akhir kalimat, seperti titik, tanda tanya, dan tanda seru. Kalimat-kalimat tersebut kemudian digabungkan secara berurutan ke dalam satu chunk dengan batas maksimum 1500 karakter. Proses penggabungan dilakukan tanpa memotong kalimat di bagian tengah agar makna kalimat tetap utuh. Untuk menjaga kesinambungan konteks antar-chunk, diterapkan mekanisme overlap, yaitu satu kalimat terakhir dari chunk sebelumnya diulang pada chunk berikutnya. Implementasi pada tahap ini ditunjukkan pada Kode Semu 3.4.

INPUT  : clean_dataset (CSV hasil preprocessing)          MAX_CHARS = 1500 OUTPUT : chunks (CSV potongan teks beserta metadata) ALGORITMA

1. BEGIN
2. chunks <- []
3. chunk_id <- 0 4.
5. FOR EACH doc IN clean_dataset DO 6.
7.     sentences <- SplitIntoSentences(doc.teks_clean)   // pemisahan berdasarkan . ? !
8.     buf <- ""
9.     prev_sent <- "" 10.
11.     FOR EACH s IN sentences DO 12.
13.         IF LENGTH(buf) + LENGTH(s) <= MAX_CHARS THEN
14.             buf <- Trim(buf + " " + s) 15.
16.         ELSE
17.             IF Trim(buf) <> "" THEN
18.                 chunks.APPEND(MakeChunk(chunk_id, doc, buf))
19.                 chunk_id <- chunk_id + 1
20.             END IF 21.
22.             buf <- Trim(prev_sent + " " + s) // menggunakan satu kalimat terakhir sebagai overlap 23.
24.         END IF
25.         prev_sent <- s
26.     END FOR 27.
28.     IF Trim(buf) <> "" THEN
29.         chunks.APPEND(MakeChunk(chunk_id, doc, buf))
30.         chunk_id <- chunk_id + 1
31.     END IF
32. END FOR 33.
34. SaveCSV(chunks, "sirah_chunks_final.csv") 35.
36. RETURN chunks
37. END Kode Semu 3.4 Chunking Data Kode Semu 3.4 menunjukkan tahapan umum pemecahan teks sub-bab menjadi chunk berukuran terkendali. Proses dimulai dengan memecah teks bersih menjadi kalimat, lalu memasukkan kalimat tersebut satu per satu ke dalam penampung selama total panjang teks belum melebihi batas 1500 karakter. Jika penambahan kalimat berikutnya menyebabkan batas tersebut terlampaui, isi penampung disimpan sebagai satu chunk. Selanjutnya, penampung baru dibentuk dengan menyertakan satu kalimat terakhir dari chunk sebelumnya sebagai overlap. Mekanisme ini digunakan agar hubungan konteks antar-chunk tetap terjaga. Setiap chunk yang terbentuk diberi identitas unik dan metadata sumber agar dapat dilacak kembali ke dokumen asalnya. Metadata tersebut mencakup informasi bab, sub-bab, dan halaman sumber. Sisa kalimat yang masih berada di dalam penampung pada akhir pemrosesan juga disimpan sebagai chunk terakhir. Hasil akhir dari tahap ini berupa kumpulan chunk dengan

identitas unik, yang dibentuk dari gabungan nomor dokumen dan urutan chunk, serta dilengkapi atribut sumbernya. Dengan demikian, keluaran tahap ini menyajikan teks dalam potongan yang lebih ringkas dan efisien untuk proses anotasi maupun NER, tanpa menghilangkan keterhubungannya dengan lokasi asal dalam dokumen Sirah. Atribut setiap chunk dijelaskan pada Penjelasan Hasil Keluaran ChunkingTabel 3.6. **Tabel 3.6 Penjelasan Hasil Keluaran Chunking**

| Nama Kolom | Tipe Data | Deskripsi | Nilai |
|---|---|---|---|
| chunk_id | String | Identitas unik setiap chunk | 000000-001 |
| doc_id | String | Identitas dokumen atau sub-bab asal | 0 |
| chunk_index |  | Urutan chunk dalam dokumen | 1 |
| judul_bab | String | Bab sumber | POSISI BANGSA ARAB DAN KAUMNYA |
| judul_sub_bab | String | Sub-bab sumber | UNLABELED SECTION |
| halaman | String | Halaman sumber pada dokumen asli | 34 |
| teks_chunk | String | Isi potongan teks | "Pada hakikatnya istilah Sirah Nabawiyah merupakan ungkapan tentang risalah yang dibawa Rasulullah kepada manusia, untuk mengeluarkan mereka dari kegelapan kepada cahaya, dari penyembahan terhadap hamba kepada penyembahan Allah. ..." |

## 3.5 Pelabelan Data

Tahap pelabelan data bertujuan untuk membentuk data anotasi yang memiliki dua fungsi utama, yaitu sebagai seed data atau data berlabel awal untuk melatih model NER pada proses iterative self-training, serta sebagai data acuan (ground truth) untuk keperluan evaluasi. Tahap ini terdiri atas tiga langkah utama, yaitu penyiapan kandidat anotasi secara semi-otomatis, koreksi manual, dan konversi anotasi ke dalam format token BIO beserta pembagian data latih dan data uji. Diagram alir tahap pelabelan data ditunjukkan pada Gambar 3.5.

Gambar 3.5 Diagram Alir Tahapan Pelabelan Data

### 3.5.1 Anotasi Semi-Otomatis

Proses anotasi manual secara penuh membutuhkan waktu dan biaya yang besar, sehingga pada tahap awal kandidat entitas dibentuk secara semi-otomatis menggunakan pencocokan kamus entitas (gazetteer) dan pola regular expression (regex). Strategi anotasi semi-otomatis yang digunakan dalam penelitian ini disesuaikan dengan empat jenis label entitas, yaitu PERSON, EVENT, LOCATION, dan TIME. Pada label PERSON, kandidat entitas diperoleh melalui pencocokan terhadap kamus nama tokoh utama dalam Sirah, seperti Rasulullah, Abu Bakar, dan Umar bin Al-Khaththab. Selain itu, digunakan pola regex untuk mendeteksi nama Arab dengan nasab, seperti pola Nama bin/binti Nama, serta prefiks majemuk seperti Abu, Ummu, dan Ibnu. Pola ini juga digunakan untuk membantu memperbaiki nama yang terpotong akibat kesalahan OCR, misalnya bentuk Ka'b bin Al yang dapat diperluas menjadi Ka'b bin Al-Khaththab apabila sesuai dengan kandidat yang ditemukan. Pada label EVENT, kandidat entitas diperoleh melalui pencocokan kamus peristiwa, seperti Perang Badar, Hijrah, dan Fathu Makkah. Selain itu, digunakan pola generik untuk mendeteksi nama peperangan, seperti Perang [Nama] dan Ghazwah [Nama]. Pada label LOCATION, kandidat entitas diperoleh melalui pencocokan kamus lokasi, seperti Makkah, Madinah, Gua Hira, dan Ka'bah. Sementara itu, pada label TIME, kandidat entitas diperoleh melalui pola regex untuk ungkapan waktu, seperti tahun ke-N Hijriah/Masehi, bulan [nama bulan Hijriah], hari [nama hari], serta nama-nama bulan Hijriah dari Muharram hingga Dzulhijjah. Kandidat entitas yang saling tumpang tindih kemudian dibersihkan menggunakan aturan deduplikasi. Dalam aturan ini, kandidat dengan rentang teks yang lebih panjang atau lebih spesifik diprioritaskan dibandingkan kandidat yang lebih pendek. Keluaran dari tahap anotasi semi-otomatis berupa berkas pra-anotasi dengan satu baris untuk setiap entitas. Setiap baris memuat teks entitas, label entitas, serta posisi awal dan akhir karakter dalam teks, yaitu start_char dan end_char. Implementasi tahap anotasi semi-otomatis ditunjukkan pada Kode Semu 3.5. INPUT  : - chunks (CSV potongan teks) - GAZETTEER (kamus PERSON/EVENT/LOCATION per tipe) - REGEX (pola nasab, perang, ungkapan waktu, bulan Hijriah)

OUTPUT : prelabelled (CSV satu baris per entitas)

ALGORITMA:

1. BEGIN
2. prelabelled <- [] 3.
4. FOR EACH chunk IN chunks DO 5.
6.     text <- NormalizeQuotes(chunk.teks_chunk)
7.     ents <- [] 8.
9.     ents <- ents + MatchGazetteer(text, GAZETTEER.PERSON, "PERSON")
10.     ents <- ents + MatchRegexNasab(text, REGEX.PERSON, "PERSON") 11.
12.     ents <- ents + MatchGazetteer(text, GAZETTEER.EVENT, "EVENT")
13.     ents <- ents + MatchRegex(text, REGEX.PERANG, "EVENT") 14.
15.     ents <- ents + MatchGazetteer(text, GAZETTEER.LOCATION, "LOCATION") 16.
17.     ents <- ents + MatchRegex(text, REGEX.TIME, "TIME") 18.
19.     // Menghapus entitas duplikat dengan memprioritaskan span terpanjang
20.     ents <- DeduplicateByLongestSpan(ents) 21.
22.     FOR EACH e IN ents DO
23.         prelabelled.APPEND({
24.             chunk.chunk_id,
25.             chunk.teks_chunk,

26.             e.text,
27.             e.label,
28.             e.start_char,
29.             e.end_char
30.         })
31.     END FOR
32. END FOR 33.
34. SaveCSV(prelabelled, "sirah_prelabelled.csv") 35.
36. RETURN prelabelled
37. END Kode Semu 3.5 Pelabelan Awal Semi-Otomatis Kode Semu 3.5 menunjukkan tahapan umum pembentukan kandidat anotasi entitas secara semi-otomatis dari kumpulan chunk. Proses diawali dengan menormalisasi tanda kutip pada teks di setiap chunk agar bentuk penulisan entitas menjadi lebih konsisten. Setelah itu, sistem mencari kandidat entitas untuk empat jenis label, yaitu PERSON, EVENT, LOCATION, dan TIME, dengan menggunakan dua pendekatan utama, yaitu pencocokan kamus entitas (gazetteer) dan pencocokan pola regular expression (regex). Pola regex yang digunakan mencakup pola nama Arab bernasab, nama peperangan, serta ungkapan waktu. Kandidat entitas yang saling tumpang tindih kemudian dibersihkan melalui proses deduplikasi dengan memprioritaskan rentang teks yang lebih panjang atau lebih spesifik. Setiap kandidat yang tersisa dicatat sebagai satu baris data yang memuat identitas chunk, teks entitas, label, serta posisi awal dan akhir karakter. Hasil akhir dari proses ini berupa berkas pra-anotasi dengan satu baris untuk setiap entitas. Dengan demikian, keluaran dari tahap ini menyediakan kandidat anotasi awal dengan cakupan yang cukup luas, tetapi tetap memerlukan verifikasi manual untuk memastikan ketepatan label dan batas entitas. Pendekatan ini digunakan untuk mempercepat proses pelabelan dibandingkan anotasi manual secara penuh. Sebagai contoh, sebagian kandidat entitas dari salah satu chunk dengan identitas 000354-001 ditunjukkan pada Tabel 3.7. **Tabel 3.7 Contoh Kandidat Pra-anotasi Semi-Otomatis**

| Entitas | Label | start_char | end_char |
|---|---|---|---|
| bulan Dzul Qi'dah | TIME | 5 | 22 |
| Rasulullah | PERSON | 50 | 60 |
| Abu Bakar Ash-Shiddiq | PERSON | 70 | 91 |
| Ali bin Abu Thalib | PERSON | 316 | 334 |
| Abu Bakar | PERSON | 431 | 440 | Abu Bakar Ash-Shiddiq PERSON Ali bin Abu Thalib PERSON Abu Bakar PERSON

### 3.5.2 Koreksi Manual

Berkas pra-anotasi yang dihasilkan pada tahap sebelumnya kemudian ditinjau dan dikoreksi secara manual oleh peneliti. Koreksi ini dilakukan dengan berpedoman pada empat label utama. Label PERSON digunakan untuk nama tokoh atau individu, termasuk nama kabilah atau kelompok Bani apabila diperlakukan sebagai entitas pelaku dalam teks, misalnya Abu Bakar dan Bani Quraizhah. Label EVENT digunakan untuk nama peristiwa, seperti Perang Badar dan Hijrah. Label LOCATION digunakan untuk nama tempat, seperti Makkah, Madinah, dan Gua Hira. Adapun label TIME digunakan untuk ungkapan waktu atau periode, seperti tahun ke-2 Hijriah dan bulan Ramadhan.

Proses koreksi manual mencakup penambahan entitas yang belum terdeteksi, penghapusan kandidat entitas yang tidak sesuai, serta perbaikan batas awal dan akhir entitas. Tahap ini penting untuk memastikan bahwa data anotasi yang digunakan pada proses pelatihan dan evaluasi memiliki kualitas yang lebih terkontrol. Contoh daftar label beserta keterangannya ditunjukkan pada Tabel 3.8. **Tabel 3.8 Skema Label Entitas**

| Label | Keterangan | Contoh |
|---|---|---|
| PERSON | Nama tokoh, individu, atau kabilah/Bani | Muhammad, Abu Bakar, Bani Quraizhah |
| EVENT | Nama peristiwa | Perang Badar, Hijrah, Fathu Makkah |
| LOCATION | Nama tempat atau wilayah | Makkah, Madinah, Gua Hira |
| TIME | Ungkapan waktu atau periode | tahun ke-2 Hijriah, bulan Ramadhan |

### 3.5.3 Konversi Menjadi Format BIO

Anotasi tingkat rentang (span) selanjutnya dikonversi ke dalam format token-per-baris menggunakan skema penandaan Begin-Inside-Outside (BIO). Format ini diperlukan karena model NER memproses data sebagai tugas sequence labeling. Teks pada setiap chunk ditokenisasi berdasarkan spasi, sekaligus dicatat posisi karakter dari setiap token. Setelah itu, setiap token diberi label sesuai posisinya terhadap rentang entitas. Token awal dari suatu entitas diberi tag B-LABEL, token lanjutan dari entitas yang sama diberi tag I-LABEL, sedangkan token yang bukan bagian dari entitas diberi tag O. Skema BIO digunakan karena merupakan salah satu formulasi standar dalam tugas NER sebagai sequence labeling, sebagaimana dijelaskan pada Bab 2 Subbab 2.3.1. Implementasi konversi BIO ditunjukkan pada Kode Semu 3.6. INPUT : - prelabelled (CSV satu baris per entitas) - all_chunks (CSV seluruh chunk) - TEST_SIZE = 0.3 OUTPUT : train, test, unlabelled (CSV format token BIO)

1. ALGORITMA:
2. BEGIN
3. ents_by_chunk <- GroupEntitiesByChunk(prelabelled)
4. labeled_rows <- [] 5.
6. FOR EACH (cid, text, ents) IN ents_by_chunk DO
7.     tokens <- TokenizeWithOffsets(text)  // menghasilkan token, start_char, end_char 8.
9.     FOR EACH (tok, s, e) IN tokens DO
10.         tag <- "O" 11.
12.         FOR EACH ent IN SortByLongestSpan(ents) DO
13.             IF Overlap(s, e, ent.start_char, ent.end_char) THEN
14.                 IF s == ent.start_char THEN
15.                     tag <- "B-" + ent.label
16.                 ELSE
17.                     tag <- "I-" + ent.label
18.                 END IF 19.
20.                 BREAK 21.

22.             END IF
23.         END FOR 24.
25.         labeled_rows.APPEND({
26.             text_id: cid,
27.             token: tok,
28.             label: tag
29.         }) 30.
31.     END FOR
32. END FOR 33.
34. // Membagi data berlabel menjadi data latih dan data uji
35. (train_ids, test_ids) <- StratifiedSplitByBab(ents_by_chunk, TEST_SIZE) 36.
37. train <- Rows(labeled_rows, train_ids)
38. test  <- Rows(labeled_rows, test_ids) 39.
40. // Chunk yang tidak memiliki hasil pre-labelling dijadikan data tidak berlabel
41. unlabelled_chunks <- all_chunks NOT IN ents_by_chunk
42. unlabelled <- TokenizeNoLabel(unlabelled_chunks) 43.
44. SaveCSV(train, "sirah_train_bio.csv")
45. SaveCSV(test, "sirah_test_bio.csv")
46. SaveCSV(unlabelled, "sirah_unlabelled_bio.csv") 47.
48. RETURN train, test, unlabelled
49. END Kode Semu 3.6 Konversi ke BIO dan Pembagian Data Kode Semu 3.6 menunjukkan tahapan umum konversi anotasi span menjadi format token berlabel BIO sekaligus proses pembagian data. Proses diawali dengan mengelompokkan entitas berdasarkan chunk asalnya. Selanjutnya, setiap chunk ditokenisasi sambil mencatat posisi karakter dari masing-masing token. Token kemudian diberi tag BIO berdasarkan kesesuaiannya dengan rentang entitas. Apabila terdapat entitas yang saling tumpang tindih, entitas dengan rentang yang lebih panjang diprioritaskan agar batas entitas yang lebih spesifik tetap dipertahankan. Setelah seluruh token diberi label, data berlabel dibagi pada tingkat chunk, bukan pada tingkat token, untuk mencegah terjadinya kebocoran data antara data latih dan data uji. Pembagian dilakukan secara stratified berdasarkan bab, dengan komposisi 70% sebagai data latih atau seed data dan 30% sebagai data uji atau ground truth. Sementara itu, chunk lain di luar data seed digunakan sebagai data tak berlabel untuk proses pseudo-labelling. Hasil akhir dari tahap ini berupa tiga berkas, yaitu data latih, data uji, dan data tak berlabel dalam format token BIO. Dengan demikian, keluaran tahap ini menyediakan data dalam bentuk sequence labeling yang dapat langsung digunakan untuk melatih dan mengevaluasi model NER, sekaligus menjaga pemisahan data secara bersih agar tidak terjadi kebocoran antara data latih dan data uji. Format token berlabel terdiri atas beberapa kolom, yaitu text_id, id, token, pos_tag, dan label. Kolom text_id menunjukkan identitas chunk, kolom id menunjukkan identitas token dalam chunk, kolom token berisi kata hasil tokenisasi, kolom pos_tag berisi nilai tetap NN sebagai placeholder yang mengikuti format notebook acuan,

sedangkan kolom label berisi tag BIO. Kolom pos_tag tidak digunakan dalam proses pelatihan model. Contoh hasil penandaan BIO ditunjukkan pada Tabel 3.9. **Tabel 3.9 Contoh Penandaan BIO**

| Token | Label |
|---|---|
| Rasulullah | B-PERSON |
| hijrah | O |
| ke | O |
| Madinah | B-LOCATION |
| pada | O |
| tahun | B-TIME |
| pertama | I-TIME |
| Hijriah | I-TIME | Hijriah I-TIME

Sebagai gambaran hasil agregat, berkas pra-anotasi memuat sekitar 6.000 baris entitas. Setelah proses konversi dan pembagian data, data latih berisi sekitar 101.021 token, sedangkan data uji berisi sekitar 42.558 token dengan 1.772 entitas. Distribusi label pada data latih menunjukkan adanya ketidakseimbangan kelas yang cukup tajam dan dirangkum pada Tabel 3.10. Distribusi ini menjadi dasar pertimbangan dalam penerapan strategi penanganan kelas minoritas pada tahap NER. **Tabel 3.10 Distribusi Label Data Latih**

| Token | Label | Persentase |
|---|---|---|
| O | 94.070 | 93,1% |
| B-PERSON | 2.634 | 2,61% |
| I-PERSON | 2.289 | 2,27% |
| B-LOCATION | 1.013 | 1,00% |
| I-TIME | 442 | 0,44% |
| B-TIME | 236 | 0,23% |
| I-EVENT | 137 | 0,14% |
| B-EVENT | 128 | 0,13% |
| I-LOCATION | 72 | 0,07% | 0,07%

Tabel 3.10 memperlihatkan bahwa kelas O sangat dominan dibandingkan label entitas lainnya. Selain itu, entitas EVENT serta sebagian entitas TIME dan LOCATION tergolong sebagai kelas minoritas ekstrem, dengan rasio ketidakseimbangan mencapai 25 banding 1. Kondisi ini menjadi salah satu alasan perlunya teknik penanganan ketidakseimbangan kelas pada tahap pemodelan NER berikutnya.

## 3.6 Ekstraksi Entitas

Tahap ekstraksi entitas bertujuan untuk memperluas cakupan anotasi dari seed data yang terbatas ke seluruh korpus. Penelitian ini menggunakan model NER berbasis IndoBERT dengan strategi semi-supervised learning melalui iterative self-training, mengikuti pendekatan (Ariyanto et al., 2025). Model dibangun menggunakan indolem/indobert-base- uncased sebagai model token classification dengan skema penandaan BIO. Diagram alir tahap ekstraksi entitas ditunjukkan pada Gambar 3.6.

Gambar 3.6 Diagram Alir Tahapan Ekstraksi Entitas Pada strategi iterative self-training, model terlebih dahulu dilatih melalui proses fine- tuning menggunakan seed data berlabel. Setelah itu, model digunakan untuk memprediksi label pada data tak berlabel. Hanya prediksi dengan tingkat keyakinan tinggi yang diterima sebagai label semu (pseudo-label) dan ditambahkan ke dalam data latih untuk proses pelatihan ulang. Proses ini dilakukan secara berulang hingga tidak terdapat label semu baru yang memenuhi kriteria atau hingga mencapai batas jumlah iterasi yang telah ditentukan. Dalam penelitian ini, sebuah kalimat diterima sebagai label semu apabila rata-rata keyakinan entitas pada kalimat tersebut mencapai ambang batas (threshold) 0,9. Implementasi tahap ini ditunjukkan pada Kode Semu 3.7. INPUT : - train (data BIO berlabel sebagai seed) - test (data BIO berlabel untuk evaluasi) - unlabelled_full (chunk tanpa anotasi manual) - THRESHOLD = 0.9 - MAX_ITER = 6 OUTPUT : - best_model - entities_all (gabungan entitas manual dan prediksi NER) ALGORITMA:

1. BEGIN
2. model <- FineTuneIndoBERT(train)    // fine-tuning IndoBERT dengan skema BIO
3. pool <- unlabelled_full              // data tidak berlabel untuk self-training
4. labeled <- train
5. best_model <- model 6.
7. FOR i <- 1 TO MAX_ITER DO

8.

9.     preds <- model.Predict(pool, aggregation = "simple") 10.
11.     accepted <- {
12.         kalimat IN preds :
13.         AvgEntityConfidence(kalimat) >= THRESHOLD
14.     } 15.
16.     IF accepted IS EMPTY THEN
17.         BREAK                          // tidak ada pseudo-label baru
18.     END IF 19.
20.     pseudo_labelled <- ToBIO(accepted) 21.
22.     labeled <- labeled + pseudo_labelled
23.     pool <- pool - accepted 24.
25.     model <- FineTuneIndoBERT(labeled) 26.
27.     IF SeqEvalF1(model, test) > SeqEvalF1(best_model, test) THEN
28.         best_model <- model
29.     END IF
30. END FOR 31.
32. entities_pred <- best_model.Predict(unlabelled_full) 33.
34. entities_manual <- LoadEntities(train) + LoadEntities(test) 35.
36. entities_all <- Merge(
37.     entities_manual,
38.     entities_pred,
39.     priority = "manual"
40. ) 41.
42. RETURN best_model, entities_all
43. END Kode Semu 3.7 Iterative Self-Training NER Kode Semu 3.7 menunjukkan tahapan umum perluasan anotasi entitas dari seed data terbatas ke seluruh korpus melalui iterative self-training. Proses diawali dengan melatih model IndoBERT sebagai token classification berskema BIO menggunakan data berlabel awal. Selanjutnya, model memprediksi label pada kumpulan data tak berlabel. Kalimat yang memiliki rata-rata keyakinan entitas mencapai ambang batas 0,9 diterima sebagai label semu dan ditambahkan ke dalam data latih. Setelah itu, model dilatih ulang dan dievaluasi menggunakan data uji. Model disimpan sebagai model terbaik apabila memperoleh peningkatan skor seqeval F1 pada data uji. Proses tersebut diulang hingga tidak terdapat label semu baru yang memenuhi ambang batas atau hingga mencapai batas maksimum enam iterasi. Setelah proses self-training mencapai kondisi konvergen, model terbaik digunakan untuk memprediksi entitas pada seluruh chunk tak berlabel. Hasil prediksi tersebut kemudian digabungkan dengan anotasi manual dari data latih dan data uji. Apabila terjadi tumpang tindih antara anotasi manual dan prediksi otomatis, anotasi manual diprioritaskan karena telah melalui proses verifikasi manusia. Hasil akhir dari tahap ini berupa model NER terbaik dan daftar entitas gabungan yang mencakup seluruh chunk korpus beserta label dan posisi karakternya. Dengan demikian, tahap ini tidak

hanya menghasilkan model pengenal entitas, tetapi juga memperluas anotasi entitas ke seluruh korpus secara semi-supervised tanpa harus melakukan pelabelan manual terhadap seluruh teks Sirah. Hyperparameter pelatihan dijelaskan pada Tabel 3.11. Nilai-nilai ini mengikuti notebook acuan pembimbing dan metode Ariyanto et al. (2025). **Tabel 3.11 Hyperparameter Pelatihan NER**

| Parameter | Nilai | Keterangan |
|---|---|---|
| Model dasar | indolem/indobert-base- uncased | IndoBERT uncased, panjang token maksimum 512 |
| Learning rate | 2e-5 | Laju pembelajaran fine-tuning |
| Batch size | 16 | Ukuran batch latih dan evaluasi |
| Epoch tiap iterasi | 10 | Jumlah epoch tiap iterasi self-training |
| Threshold | 0,9 | Ambang rata-rata keyakinan entitas per kalimat |
| Sampling rate | 1,0 | Memakai semua kalimat di atas ambang |
| Agg. Strategy | Simple | Strategi agregasi sub-token |
| Iterasi maksimum | 6 | Batas iterasi self-training |

Keluaran dari tahap ini berupa daftar entitas gabungan untuk seluruh chunk korpus. Pada chunk yang telah memiliki anotasi manual, yaitu data latih dan data uji dari tahap pelabelan data, anotasi manual dipertahankan sebagai sumber utama karena memiliki kualitas yang lebih terkontrol dibandingkan prediksi otomatis. Sementara itu, pada chunk yang tidak memiliki anotasi manual, entitas diperoleh dari hasil prediksi model NER terbaik yang dihasilkan melalui proses iterative self-training. Kedua sumber entitas tersebut kemudian digabungkan sehingga korpus dapat direpresentasikan dalam bentuk daftar entitas berlabel dengan atribut chunk_id, entity_text, label, start_char, dan end_char. Daftar entitas gabungan ini selanjutnya digunakan sebagai masukan pada tahap penyatuan nama entitas. Sebagai contoh keluaran, sebagian entitas hasil ekstraksi NER pada chunk 000099- 001 (halaman 233) ditunjukkan pada Tabel 3.12. **Tabel 3.12 Contoh Keluaran Ekstraksi Entitas NER**

| Entitas | Label | start_char | end_char |
|---|---|---|---|
| Madinah | LOCATION | 8 | 15 |
| Perjanjian Hudaibiyah | EVENT | 280 | 301 |
| Fathu Makkah | EVENT | 423 | 435 |
| bulan Ramadhan | TIME | 441 | 455 |
| Rasulullah | PERSON | 740 | 750 |
| bulan Rabi'ul Awwal | TIME | 756 | 775 | TIME

## 3.7 Konstruksi Knowledge Graph

Tahap konstruksi knowledge graph menyusun struktur graf dari daftar entitas hasil ekstraksi melalui empat bagian yang berurutan: penyatuan variasi nama entitas (alias clustering) agar satu entitas tidak terpecah menjadi banyak node, pembentukan relasi antar entitas menjadi pasangan node-edge, periodisasi peristiwa yang menambahkan dimensi waktu berupa atribut periode dan relasi urutan kronologis antar peristiwa, lalu pemuatan node dan edge tersebut ke basis data graf Neo4j. Diagram alir keseluruhan tahap konstruksi knowledge graph ditunjukkan pada Gambar 3.7.

Gambar 3.7 Diagram Alir Tahapan Konstruksi Knowledge Graph

### 3.7.1 Alias Clustering

Tahap penyatuan nama bertujuan untuk menormalisasi variasi penulisan nama entitas ke dalam satu bentuk kanonik. Dalam teks Sirah, satu entitas dapat disebut dengan beberapa variasi nama. Sebagai contoh, Umar, Umar bin Al-Khaththab, dan Ibnul Khaththab dapat merujuk pada tokoh yang sama. Apabila variasi tersebut tidak dinormalisasi, setiap variasi nama akan direpresentasikan sebagai node yang berbeda pada knowledge graph, meskipun sebenarnya merujuk pada entitas yang sama. Oleh karena itu, tahap ini dilakukan setelah proses ekstraksi entitas agar peta alias yang dibentuk dapat mencakup variasi nama yang muncul di seluruh korpus. Diagram alir tahap penyatuan nama ditunjukkan pada Gambar 3.8.

Gambar 3.8 Diagram Alir Tahapan Alias Clustering Proses penyatuan nama dilakukan melalui dua tahap utama. Tahap pertama adalah pengelompokan manual (manual clustering) terhadap entitas yang telah dipastikan merujuk pada objek yang sama berdasarkan pengetahuan domain. Pengelompokan ini mencakup entitas berlabel PERSON, LOCATION, dan EVENT. Tahap kedua adalah pencocokan kemiripan string menggunakan algoritma Jaro-Winkler. Algoritma ini digunakan karena memberikan bobot lebih besar pada kesamaan prefiks, sehingga sesuai dengan karakteristik sebagian nama Arab yang memiliki kemiripan pada bagian awal nama, sementara variasinya sering muncul pada bagian akhir.

Ambang kemiripan ditetapkan sebesar 0,93, lebih tinggi daripada ambang umum 0,85. Penetapan ambang yang lebih ketat dilakukan karena banyak nama Arab memiliki pola struktural yang mirip, tetapi merujuk pada entitas yang berbeda, misalnya Abu Bakar dan Abu Bashir. Untuk mengurangi risiko false positive, diterapkan sejumlah aturan pengaman. Aturan tersebut mencakup kewajiban kemiripan bagian pembeda setelah prefiks majemuk di atas 0,90, kecocokan bagian patronimik seperti bin atau binti, rasio panjang kedua nama tidak kurang dari 0,80, serta penggunaan daftar pasangan terlarang (exclude pairs) untuk nama yang mirip secara leksikal tetapi berbeda entitas, seperti Sa'd bin Mu'adz dan Sa'd bin Ubadah. Implementasi tahap ini ditunjukkan pada Kode Semu 3.8. INPUT  : - entities_all   (entitas hasil NER) - manual_clusters (klaster manual per label) - JW_THRESHOLD = 0.93

OUTPUT : alias_map (peta variasi nama -> nama kanonik)

ALGORITMA:

1. BEGIN
2. alias_map <- {} 3.
4. // Tahap 1: pemetaan berdasarkan klaster manual
5. FOR EACH (label, canonical, aliases) IN manual_clusters DO
6.     FOR EACH a IN aliases DO
7.         alias_map[label + "::" + a] <- canonical
8.     END FOR
9. END FOR 10.
11. // Tahap 2: pemetaan otomatis menggunakan Jaro-Winkler
12. FOR EACH label IN {PERSON, EVENT, LOCATION} DO
13.     names <- SortByLengthDesc(UniqueNames(entities_all, label))
14.     mapped <- {}
15.     FOR i <- 0 TO LENGTH(names) - 2 DO
16.         FOR j <- i + 1 TO LENGTH(names) - 1 DO
17.             IF names[j] IN mapped THEN
18.                 CONTINUE
19.             END IF 20.
21.             score <- JaroWinkler(names[i], names[j]) 22.
23.             IF score >= JW_THRESHOLD
24.                AND PassGuards(names[i], names[j])
25.                AND (names[i], names[j]) NOT IN EXCLUDE_PAIRS
26.             THEN
27.                 alias_map[label + "::" + names[j]] <- names[i]
28.                 mapped.ADD(names[j])
29.             END IF
30.         END FOR
31.     END FOR
32. END FOR
33. SaveJSON(alias_map, "alias_map.json")
34. RETURN alias_map
35. END Kode Semu 3.8 Alias Clustering Kode Semu 3.8 menunjukkan tahapan umum penyatuan variasi penulisan nama entitas ke dalam satu bentuk kanonik. Proses diawali dengan pengelompokan manual, yaitu memetakan

sejumlah variasi nama yang telah dipastikan merujuk pada entitas yang sama ke nama kanoniknya. Selanjutnya, pada setiap label entitas dilakukan pencocokan kemiripan string menggunakan algoritma Jaro-Winkler. Nama-nama entitas diurutkan dari bentuk yang paling panjang agar bentuk nama yang lebih lengkap dapat digunakan sebagai acuan kanonik. Sepasang nama hanya disatukan apabila memenuhi beberapa kriteria, yaitu skor kemiripan mencapai ambang 0,93, lolos seluruh aturan pengaman, dan tidak termasuk dalam daftar pasangan terlarang. Hasil akhir dari proses ini berupa peta alias yang memetakan setiap variasi nama ke bentuk kanoniknya, serta laporan klaster yang digunakan untuk peninjauan manual. Dengan demikian, tahap ini memastikan bahwa satu entitas yang ditulis dalam beberapa variasi tetap direpresentasikan sebagai satu node pada knowledge graph. Hal ini penting agar relasi dan analisis jaringan tidak terpecah akibat duplikasi nama. Output dari tahap ini berupa berkas alias_map.json yang memuat pemetaan variasi nama ke bentuk kanonik. Sebagai gambaran hasil, tahap ini menghasilkan sekitar 143 variasi nama yang dipetakan ke dalam sekitar 109 klaster kanonik. Peta alias tersebut kemudian digunakan pada tahap pembentukan relasi dan konstruksi graf agar setiap entitas dapat direpresentasikan secara konsisten sebagai satu node. Contoh pemetaan variasi nama ke bentuk kanoniknya ditunjukkan pada Tabel 3.13. **Tabel 3.13 Contoh Pemetaan Variasi Nama ke Bentuk Kanonik**

| Variasi Nama | Bentuk Kanonik | Jenis Variasi |
|---|---|---|
| Rasulullah | Muhammad | Sebutan berbeda |
| Muhammad bin Abdullah |  | Nama bernasab |
| Abu Bakar Ash-Shiddiq | Abu Bakar | Gelar tambahan |
| Abu Bakkar |  | Variasi ejaan (artefak OCR) |
| Umar | Umar bin Al-Khaththab | Bentuk pendek |
| Umar bin Al-Khathab |  | Variasi ejaan (artefak OCR) |
| Abu Sofyan | Abu Sufyan bin Harb | Variasi ejaan | (artefak OCR) Umar Umar bin Al-Khaththab Bentuk pendek Umar bin Al-Khathab Variasi ejaan (artefak OCR) Abu Sofyan Abu Sufyan bin Harb Variasi ejaan

### 3.7.2 Pembentukan Relasi

Tahap pembentukan relasi bertujuan untuk menghubungkan entitas hasil ekstraksi ke dalam pasangan node-edge sehingga terbentuk struktur pengetahuan yang siap dimasukkan ke basis data graf. Diagram alir tahap pembentukan relasi ditunjukkan pada Gambar 3.9. Proses pembentukan relasi diawali dengan normalisasi nama entitas menggunakan peta alias dari tahap sebelumnya. Normalisasi ini dilakukan agar entitas yang sama, meskipun ditulis dalam beberapa variasi, tetap dikenali sebagai satu node. Setelah itu, relasi dibentuk berdasarkan kemunculan bersama (co-occurrence) entitas dalam chunk yang sama dengan mempertimbangkan kedekatan posisi antar-kemunculan entitas (proximity). Dua entitas dianggap berada dalam konteks yang sama apabila muncul dalam satu kalimat atau berada pada jarak kurang dari 200 karakter. Dalam penelitian ini, entitas EVENT diperlakukan sebagai pusat keterhubungan karena peristiwa dalam teks Sirah berperan sebagai penghubung antara tokoh, lokasi, dan waktu. Relasi inti yang dibentuk mengikuti kombinasi label entitas, sebagaimana dijelaskan pada Tabel 3.14.

Gambar 3.9 Diagram Alir Tahapan Pembentukan Relasi **Tabel 3.14 Rancangan Tipe Relasi Inti**

| Pasangan Entitas | Tipe Relasi | Makna |
|---|---|---|
| PERSON ke EVENT | INVOLVED_IN | Tokoh terlibat dalam peristiwa |
| EVENT ke LOCATION | OCCURRED_AT | Peristiwa terjadi di suatu tempat |
| EVENT ke TIME | OCCURRED_ON | Peristiwa terjadi pada suatu waktu |

Selain relasi inti, penelitian ini juga membentuk relasi antartokoh, yaitu KELUARGA, SAHABAT, dan MUSUH. Relasi tersebut dikenali melalui pola kata pemicu pada kalimat bukti, misalnya kata putra, menikahi, sahabat, dan memerangi Relasi yang sama dari konteks berbeda kemudian digabung melalui proses deduplikasi. Pada tahap ini, bukti pendukung dari berbagai konteks dihimpun, sedangkan bobot relasi (weight) dihitung untuk menunjukkan kekuatan hubungan antar-entitas. Implementasi tahap pembentukan relasi ditunjukkan pada Kode Semu 3.9. INPUT  : - entities_all (entitas hasil NER) - alias_map    (peta nama kanonik) - chunks       (teks untuk konteks dan evidence)

OUTPUT : nodes, edges (CSV node dan edge)

ALGORITMA:

1. BEGIN
2. FOR EACH e IN entities_all DO
3.     e.canonical <- alias_map.GET(e.label + "::" + e.text, e.text)
4. END FOR 5.
6. edges <- [] 7.
8. FOR EACH chunk IN GroupByChunk(entities_all) DO 9.
10.     events    <- Filter(chunk, "EVENT")
11.     persons   <- Filter(chunk, "PERSON")
12.     locations <- Filter(chunk, "LOCATION")
13.     times     <- Filter(chunk, "TIME")

14.

15.     FOR EACH ev IN events DO
16.         FOR EACH p IN persons DO
17.             IF SameContext(p, ev)
18.                AND NOT InvalidInvolvedIn(p, Evidence(p, ev))
19.             THEN
20.                 edges.APPEND(Edge(p, "INVOLVED_IN", ev))
21.             END IF
22.         END FOR 23.
24.         FOR EACH l IN locations DO
25.             IF SameContext(ev, l)
26.                AND NOT InvalidOccurredAt(ev, l, Evidence(ev, l))
27.             THEN
28.                 edges.APPEND(Edge(ev, "OCCURRED_AT", l))
29.             END IF
30.         END FOR 31.
32.         FOR EACH t IN times DO
33.             IF SameContext(ev, t)
34.                AND NOT InvalidOccurredOn(ev, t, Evidence(ev, t))
35.             THEN
36.                 edges.APPEND(Edge(ev, "OCCURRED_ON", t))
37.             END IF
38.         END FOR 39.
40.     END FOR 41.
42.     edges <- edges + PersonPersonRelations(persons, chunk)

// KELUARGA/SAHABAT/MUSUH 43.

44. END FOR 45.
46. edges <- Deduplicate(edges)          // gabung evidence dan hitung weight
47. nodes <- BuildUniqueNodes(entities_all) 48.
49. SaveCSV(nodes, "nodes.csv")
50. SaveCSV(edges, "edges.csv") 51.
52. RETURN nodes, edges
53. END Kode Semu 3.9 Pembentukan Relasi Kode Semu 3.9 menunjukkan tahapan umum pembentukan relasi antar-entitas menjadi pasangan node-edge. Proses dimulai dengan menormalisasi nama setiap entitas menggunakan peta alias agar variasi penulisan dikenali sebagai satu node. Selanjutnya, entitas dikelompokkan berdasarkan chunk asalnya dan dipisahkan menurut tipe labelnya. Untuk setiap entitas peristiwa dalam sebuah chunk, sistem membentuk relasi ke tokoh melalui INVOLVED_IN, ke lokasi melalui OCCURRED_AT, dan ke waktu melalui OCCURRED_ON, selama pasangan entitas tersebut berada dalam konteks yang sama dan lolos pemeriksaan guard. Sementara itu, relasi antar-tokoh seperti KELUARGA, SAHABAT, dan MUSUH dibentuk berdasarkan kemunculan pola kata pemicu pada kalimat bukti. Relasi yang sama dari beberapa konteks kemudian digabung dengan tetap menyimpan evidence dan menghitung bobot relasi. Daftar node unik dibangun dari seluruh entitas yang telah dinormalisasi. Hasil akhir dari proses ini berupa berkas daftar node (nodes.csv) dan

daftar edge (edges.csv) yang masing-masing dilengkapi atribut dan provenance. Dengan demikian, keluaran tahap ini tidak hanya merepresentasikan entitas sebagai titik dalam graf, tetapi juga memuat keterhubungan bermakna antara tokoh, peristiwa, lokasi, dan waktu yang siap dimuat ke dalam basis data graf. Atribut node dan edge dijelaskan pada Tabel 3.15 dan Tabel 3.16. **Tabel 3.15 Atribut Node**

| Kolom | Deskripsi | Contoh Nilai |
|---|---|---|
| node_id | Identitas unik node (hash dari label dan nama kanonik) | 48f98905d5c8 |
| name | Nama entitas dalam bentuk kanonik | Muhammad |
| label | Tipe entitas (PERSON/EVENT/LOCATION/TIME) | PERSON |
| aliases | Variasi nama lain yang dipetakan ke node ini | Rasulullah / Muhammad Bin Abdullah |
| frequency | Jumlah kemunculan entitas | 719 |
| chunk_ids | Daftar chunk sumber | 000000-001 / 000002-005 / 000002- 011 / ... |

**Tabel 3.16 Atribut Edge**

| Kolom | Deskripsi | Contoh Nilai |
|---|---|---|
| source_name, source_label | Node asal dan tipenya | Amr bin Al-Ash, PERSON |
| relation_type | Tipe relasi (INVOLVED_IN, OCCURRED_AT, OCCURRED_ON, KELUARGA, SAHABAT, MUSUH) | INVOLVED_IN |
| target_name, target_label | Node tujuan dan tipenya | Perang Badr, EVENT |
| weight | Bobot relasi (gabungan skor kedekatan dan skor periode) | 0,5 |
| frequency | Jumlah chunk yang mendukung relasi | 2 |
| evidence, halaman, chunk_id | Bukti dan provenance relasi | "... riwayat Ibnu Ishaq ...", 133-137, 000052- 006 / 000052-007 |

Bobot relasi dihitung dari kombinasi skor kedekatan (proximity) entitas dalam teks dan skor periode (kesesuaian relasi dengan periode peristiwa, lihat subbab 3.7.3). Contoh hasil satu relasi adalah (Person: Abu Bakar) - [INVOLVED_IN] → (Event: Hijrah ke Madinah) dengan evidence berupa cuplikan kalimat sumber dan weight tertentu. Beberapa contoh edge nyata untuk tiap tipe relasi ditunjukkan pada Tabel 3.17. Keluaran tahap ini berupa nodes.csv dan edges.csv. **Tabel 3.17 Contoh Edge Hasil Pembentukan Relasi**

| Sumber (label) | Relasi | Tujuan (label) | weight | halaman |
|---|---|---|---|---|
| Amr bin Al-Ash (Person) | INVOLVED_IN | Perang Badr (Event) | 0,5 | 133-137 |
| Perang Badr (Event) | OCCURRED_AT | Yatsrib (Location) | 0,5 | 165-168 |
| Perang Yarmuk (Event) | OCCURRED_ON | Tahun 13 H (Time) | 0,5 | 47-48 |
| Ibrahim (Person) | KELUARGA | Isma'il (Person) | 0,55 | - | 0,55 -

### 3.7.3 Periodisasi Peristiwa

Tahap periodisasi bertujuan untuk menempatkan setiap entitas peristiwa (EVENT) ke dalam periode kronologis Sirah serta membentuk relasi urutan antar peristiwa. Periodisasi dilakukan dengan memanfaatkan struktur daftar isi buku sebagai acuan urutan kronologis, karena narasi Sirah pada umumnya disusun secara runtut berdasarkan perkembangan peristiwa. Diagram alir tahap periodisasi ditunjukkan pada Gambar 3.10.

Gambar 3.10 Diagram Alir Tahapan Periodisasi Peristiwa Proses periodisasi dilakukan secara top-down. Bab-bab pada daftar isi terlebih dahulu dikelompokkan secara semantik ke dalam sejumlah periode besar, seperti periode sebelum kenabian, periode dakwah di Makkah, periode Madinah, dan periode-periode lanjutan lainnya. Setelah itu, setiap node EVENT dipetakan ke bab tempat peristiwa tersebut paling banyak muncul. Bab dengan frekuensi kemunculan tertinggi kemudian digunakan untuk menentukan periode peristiwa beserta rentang halamannya. Berdasarkan urutan halaman pada bab sumber, peristiwa-peristiwa kemudian diurutkan secara kronologis. Peristiwa yang berada pada urutan lebih awal dihubungkan dengan peristiwa berikutnya menggunakan relasi PRECEDES. Dengan cara ini, knowledge graph tidak hanya memuat hubungan antara peristiwa, tokoh, lokasi, dan waktu, tetapi juga merepresentasikan alur kronologis antar-peristiwa. Implementasi tahap ini ditunjukkan pada Kode Semu 3.10. INPUT  : nodes, edges, periods

OUTPUT : basis data graf Neo4j

ALGORITMA:

1. BEGIN
2. // Constraint keunikan
3. FOR EACH L IN {Person, Event, Location, Time} DO
4.     Run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:" + L + ") REQUIRE n.name IS UNIQUE")
5. END FOR 6.
7. Run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Period) REQUIRE n.period_id IS UNIQUE") 8.
9. // Node Period
10. FOR EACH p IN periods DO
11.     Run("MERGE (n:Period {period_id: $id}) SET n += $props", p)
12. END FOR 13.
14. // Node entitas
15. FOR EACH n IN nodes DO 16.
17.     label <- MapLabel(n.label)        // PERSON -> Person, dst. 18.

19.     Run("MERGE (x:" + label + " {name: $name}) SET x += $props", n) 20.
21. END FOR 22.
23. // Edge relasi
24. FOR EACH e IN edges DO 25.
26.     Run(
27.         "MATCH (a:" + e.src_label + " {name:$s}), " +
28.         "(b:" + e.tgt_label + " {name:$t}) " +
29.         "MERGE (a)-[r:" + e.relation_type + "]->(b) " +
30.         "SET r += $props",
31.         e
32.     ) 33.
34. END FOR 35.
36. // Relasi Event ke Period
37. FOR EACH ev IN nodes WHERE ev.label = EVENT AND ev.periode <> "" DO 38.
39.     Run(
40.         "MATCH (e:Event {name:$ev}), " +
41.         "(p:Period {period_id:$pid}) " +
42.         "MERGE (e)-[:IN_PERIOD]->(p)"
43.     ) 44.
45. END FOR 46.
47. RETURN graph
48. END Kode Semu 3.10 Periodisasi dan Kronologi Peristiwa Kode Semu 3.10 menunjukkan tahapan umum penempatan setiap peristiwa ke dalam periode kronologis Sirah sekaligus pembentukan urutan antar-peristiwa. Proses dimulai dengan memetakan setiap node EVENT ke bab tempat peristiwa tersebut paling sering muncul. Bab tersebut kemudian digunakan untuk menentukan periode dan rentang halaman berdasarkan pengelompokan periode yang telah disusun dari daftar isi. Selanjutnya, peristiwa yang memiliki frekuensi kemunculan memadai diurutkan berdasarkan halaman bab secara kronologis. Urutan tersebut kemudian dirapikan agar tidak menghasilkan urutan ganda dari bab yang sama. Setelah urutan kronologis terbentuk, sistem membangun relasi PRECEDES antara satu peristiwa dan peristiwa berikutnya. Relasi ini membentuk rantai kronologi yang menggambarkan alur peristiwa dalam narasi Sirah. Hasil pemetaan periode kemudian disimpan sebagai berkas keluaran. Hasil akhir dari tahap ini berupa peta periode setiap peristiwa beserta rentang halamannya, serta kumpulan relasi PRECEDES antar-peristiwa. Dengan demikian, tahap periodisasi memberikan dimensi waktu pada knowledge graph, sehingga setiap peristiwa tidak hanya terhubung dengan tokoh dan tempat, tetapi juga tersusun dalam urutan kronologis. Sebagai gambaran hasil, daftar isi dikelompokkan menjadi sekitar 15 periode dengan kode P0 sampai P14, yang tergabung ke dalam beberapa fase besar. Setiap peristiwa yang cukup sering muncul memperoleh atribut periode_bab dan page_range, serta dapat terhubung dengan peristiwa berikutnya melalui relasi PRECEDES. Relasi tersebut membentuk rantai kronologi peristiwa dari awal hingga akhir narasi Sirah. Contoh pemetaan beberapa peristiwa ke dalam periode dan rentang halaman secara kronologis ditunjukkan pada Tabel 3.18.

**Tabel 3.18 Contoh Pemetaan Peristiwa ke Periode**

| Peristiwa | periode_bab | page_range | frequency |
|---|---|---|---|
| Kelahiran Nabi | Nasab & Kelahiran Nabi | 73-93 | 29 |
| Hijrah Ke Habasyah | Dakwah Jahriyah & Tekanan Quraisy | 133-160 | 13 |
| Hijrah Ke Madinah | Hijrah ke Madinah | 214-232 | 26 |
| Perang Badr | Perang Badr & Dampaknya | 266-304 | 51 |
| Fathul Makkah | Perang Mu'tah & Penaklukan Makkah | 524-536 | 3 |

### 3.7.4 Konstruksi Graf di Neo4j

Bagian ini bertujuan untuk membangun basis data graf di Neo4j berdasarkan daftar node dan edge yang telah dihasilkan pada tahap sebelumnya. Diagram alir proses pemuatan graf ke Neo4j ditunjukkan pada Gambar 3.11.

Gambar 3.11 Diagram Alir Tahapan Konstruksi Knowledge Graph Skema graf yang digunakan terdiri atas empat label node utama, yaitu Person, Event, Location, dan Time, serta satu label tambahan, yaitu Period, untuk merepresentasikan periode kronologis. Tipe relasi inti yang digunakan meliputi INVOLVED_IN, OCCURRED_AT, dan OCCURRED_ON. Selain itu, digunakan pula relasi IN_PERIOD untuk menghubungkan Event dengan Period, serta relasi tambahan berupa KELUARGA, SAHABAT, MUSUH, dan PRECEDES. Untuk menjaga integritas data, dibuat constraint keunikan pada properti name di setiap label node. Constraint ini bertujuan untuk mencegah terbentuknya dua node yang merepresentasikan entitas yang sama. Proses impor node dan relasi dilakukan menggunakan perintah MERGE, sehingga node atau relasi yang telah ada tidak dibuat ulang, tetapi hanya diperbarui propertinya apabila diperlukan. Skrip Cypher dihasilkan secara otomatis dari berkas nodes.csv dan edges.csv, kemudian dapat dijalankan melalui driver Bolt atau disalin ke Neo4j Browser. Implementasi tahap ini ditunjukkan pada Kode Semu 3.11. INPUT  : nodes, edges, periods

OUTPUT : basis data graf Neo4j

ALGORITMA:

1. BEGIN
2. // Constraint keunikan
3. FOR EACH L IN {Person, Event, Location, Time} DO
4.     Run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:" + L + ") REQUIRE n.name IS UNIQUE")
5. END FOR

6.

7. Run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Period) REQUIRE n.period_id IS UNIQUE") 8.
9. // Node Period
10. FOR EACH p IN periods DO
11.     Run("MERGE (n:Period {period_id: $id}) SET n += $props", p)
12. END FOR 13.
14. // Node entitas
15. FOR EACH n IN nodes DO 16.
17.     label <- MapLabel(n.label)        // PERSON -> Person, dst. 18.
19.     Run("MERGE (x:" + label + " {name: $name}) SET x += $props", n) 20.
21. END FOR 22.
23. // Edge relasi
24. FOR EACH e IN edges DO 25.
26.     Run(
27.         "MATCH (a:" + e.src_label + " {name:$s}), " +
28.         "(b:" + e.tgt_label + " {name:$t}) " +
29.         "MERGE (a)-[r:" + e.relation_type + "]->(b) " +
30.         "SET r += $props",
31.         e
32.     ) 33.
34. END FOR 35.
36. // Relasi Event ke Period
37. FOR EACH ev IN nodes WHERE ev.label = EVENT AND ev.periode <> "" DO 38.
39.     Run(
40.         "MATCH (e:Event {name:$ev}), " +
41.         "(p:Period {period_id:$pid}) " +
42.         "MERGE (e)-[:IN_PERIOD]->(p)"
43.     ) 44.
45. END FOR 46.
47. RETURN graph
48. END Kode Semu 3.11 Konstruksi Knowledge Graph di Neo4j Kode Semu 3.11 menunjukkan tahapan umum pemuatan daftar node dan edge ke dalam basis data graf Neo4j. Proses dimulai dengan membuat constraint keunikan pada properti penanda untuk setiap label node, termasuk label Period, agar tidak terjadi duplikasi data. Selanjutnya, sistem membuat node periode dan node entitas menggunakan perintah MERGE. Dengan pendekatan ini, node yang sudah tersedia akan diperbarui propertinya, bukan dibuat sebagai node baru. Tahap berikutnya adalah pembentukan relasi. Setiap relasi dibuat dengan mencocokkan node asal dan node tujuan, kemudian membentuk relasi menggunakan perintah MERGE beserta properti yang menyertainya. Setiap peristiwa yang memiliki atribut periode juga dihubungkan ke node periode melalui relasi IN_PERIOD. Penggunaan MERGE secara

konsisten membuat proses impor bersifat idempotent, sehingga skrip dapat dijalankan ulang tanpa menggandakan data. Hasil akhir dari tahap ini berupa basis data graf Neo4j yang memuat seluruh entitas, relasi inti, relasi antar-tokoh, relasi kronologis, serta keterhubungan peristiwa dengan periode. Dengan demikian, keluaran tahap ini menyediakan representasi knowledge graph yang siap dikueri untuk penelusuran relasional maupun analisis jaringan pada tahap berikutnya. Properti node mencakup name, node_id, frequency, aliases, serta periode_bab dan page_range khusus untuk node Event. Sementara itu, properti relasi mencakup weight, frequency, evidence, dan halaman. Sebagai contoh, kueri Cypher MATCH (p:Person)- [:INVOLVED_IN]->(e:Event {name: "Perang Badar"}) RETURN p.name dapat digunakan untuk menampilkan daftar tokoh yang terlibat dalam Perang Badar berdasarkan struktur graf yang telah dibangun.

## 3.8 Pengujian dan Evaluasi Hasil Ekstraksi NER

Evaluasi hasil ekstraksi NER bertujuan untuk mengukur kemampuan model dalam mengenali dan mengklasifikasikan entitas secara objektif. Evaluasi dilakukan menggunakan data uji, yaitu 30% data ground truth dari tahap pelabelan yang tidak digunakan dalam proses pelatihan maupun pseudo-labelling. Dengan demikian, hasil evaluasi dapat merepresentasikan kemampuan generalisasi model terhadap data yang belum pernah dilihat sebelumnya. Prediksi model dibandingkan dengan label acuan (ground truth) pada tingkat entitas (entity-level) menggunakan pustaka seqeval. Pada evaluasi tingkat entitas, sebuah prediksi hanya dianggap benar apabila rentang token dan kategori entitasnya sesuai sepenuhnya dengan anotasi acuan. Metrik yang dihitung meliputi Precision, Recall, dan F1-score untuk setiap label, serta nilai agregat berupa macro-average dan micro-average. Macro-average digunakan untuk melihat rata-rata performa antar-label dengan bobot yang sama, sehingga performa pada kelas minoritas seperti EVENT dan TIME tetap terwakili. Sementara itu, micro-average digunakan untuk melihat performa keseluruhan berdasarkan total prediksi benar, salah, dan terlewat. Rumus metrik evaluasi mengacu pada Bab 2 Subbab 2.8. Prosedur evaluasi yang sama digunakan pada seluruh skenario uji coba agar hasil antar- percobaan dapat dibandingkan secara konsisten. Pseudocode evaluasi NER ditunjukkan pada Kode Semu 3.12. INPUT  : model (NER terbaik), test (ground truth BIO)

OUTPUT : metrics (P, R, F1 per label + macro + micro)

ALGORITMA:

1. BEGIN
2. y_true <- BIOSequences(test) 3.
4. y_pred <- model.Predict(TokensOf(test)) 5.
6. metrics <- SeqEval(y_true, y_pred)    // entity-level dengan span exact match 7.
8. Report(
9.     metrics.per_label,
10.     metrics.macro_f1,
11.     metrics.micro_f1

12. ) 13.
14. RETURN metrics
15. END Kode Semu 3.12 Evaluasi NER Kode Semu 3.12 menunjukkan tahapan umum evaluasi kualitas hasil NER pada data uji. Proses dimulai dengan mengambil urutan label sebenarnya (ground truth) dalam format BIO dari data uji. Selanjutnya, model NER terbaik digunakan untuk memprediksi label pada token yang sama. Urutan label hasil prediksi kemudian dibandingkan dengan urutan label acuan pada tingkat entitas menggunakan pustaka seqeval. Dalam perbandingan ini, entitas hanya dihitung benar apabila seluruh rentang token dan kategori labelnya tepat. Dari hasil perbandingan tersebut, sistem menghitung Precision, Recall, dan F1-score untuk setiap label, serta nilai agregat macro-average dan micro-average. Hasil akhir dari tahap ini berupa kumpulan metrik evaluasi per label dan metrik agregat. Dengan demikian, keluaran tahap evaluasi memberikan ukuran objektif terhadap kemampuan model dalam mengenali entitas pada data yang tidak digunakan selama proses pelatihan, sehingga dapat menjadi dasar pembahasan kualitas model NER pada Bab 4. Untuk menguji metode secara lebih mendalam, penelitian ini merancang tiga skenario uji coba. Setiap skenario memvariasikan satu komponen pada alur ekstraksi NER, sedangkan prosedur evaluasi dan data uji yang digunakan tetap sama. Penggunaan prosedur evaluasi yang konsisten memungkinkan hasil antar skenario dibandingkan secara lebih adil. Rancangan ketiga skenario uji coba tersebut dirangkum pada Tabel 3.19. **Tabel 3.19 Rancangan Uji Coba Evaluasi NER**

| Skenario | Penjelasan | Metrik Evaluasi |
|---|---|---|
| Uji Coba 1: Penanganan ketidakseimbangan kelas | Memvariasikan teknik penanganan data tidak seimbang (alur dasar vs weighted cross-entropy vs contrastive learning vs augmentation) untuk menguji pengaruhnya terhadap kelas minoritas | Precision, Recall, dan F1-Score (per label dan macro-average) |
| Uji Coba 2: Perbandingan model | Memvariasikan model dasar (backbone) pada iterative self-training untuk menguji model pra-latih mana yang paling sesuai | Precision, Recall, dan F1-Score (per label dan agregat antar model) |
| Uji Coba 3: Pengaruh modul POS-tag | Memvariasikan ada atau tidaknya modul POS-tag untuk menguji pengaruh informasi POS-tag terhadap prediksi entitas | Precision, Recall, dan F1-Score (per label, dengan dan tanpa POS- tag) |

### 3.8.1 Uji Coba 1: Penanganan Ketidakseimbangan Kelas

Uji coba pertama bertujuan untuk menguji pengaruh teknik penanganan ketidakseimbangan kelas terhadap performa model NER. Berdasarkan distribusi label yang ditunjukkan pada Tabel 3.7, kelas EVENT serta sebagian kelas TIME dan LOCATION tergolong sebagai kelas minoritas. Kondisi ini berpotensi membuat model lebih mudah mengenali kelas mayoritas, tetapi kurang optimal dalam mengenali entitas yang jumlah kemunculannya lebih sedikit. Pada uji coba ini, alur dasar (baseline) dibandingkan dengan tiga teknik penanganan ketidakseimbangan kelas. Teknik pertama adalah weighted cross-entropy, yaitu pemberian bobot lebih besar pada kelas minoritas dalam fungsi loss agar kesalahan prediksi pada kelas tersebut memperoleh perhatian lebih besar selama pelatihan. Teknik kedua adalah supervised contrastive learning sebagaimana diperkenalkan oleh Khosla et al. (2021), yaitu penambahan komponen loss yang mendorong representasi token dari kelas yang sama menjadi lebih dekat, sementara representasi token dari kelas berbeda dibuat lebih terpisah. Teknik ketiga adalah data augmentation melalui mention replacement sebagaimana digunakan oleh Dai dan Adel (2020), yaitu pembentukan kalimat latih baru dengan mengganti sebutan entitas kelas minoritas menggunakan entitas lain dari kelas yang sama, dengan tetap mempertahankan skema penandaan BIO. Seluruh varian dilatih menggunakan seed data yang sama dan dievaluasi dengan prosedur yang telah dijelaskan pada Kode Semu 3.12. Hasil evaluasi kemudian dibandingkan berdasarkan nilai F1-score per label dan nilai macro-average untuk melihat sejauh mana setiap teknik mampu meningkatkan performa pada kelas minoritas..

### 3.8.2 Uji Coba 2: Komparasi Model Pra-Latih

Uji coba kedua bertujuan untuk membandingkan performa beberapa model pra-latih (backbone) ketika digunakan dalam alur iterative self-training yang sama. Model dasar IndoBERT, yaitu indolem/indobert-base-uncased, dibandingkan dengan beberapa model alternatif berbahasa Indonesia, baik model cased maupun uncased. Perbandingan ini dilakukan untuk mengetahui pengaruh pemilihan backbone terhadap kemampuan model dalam mengenali dan mengklasifikasikan entitas. Agar perbandingan antar model tetap adil, setiap model dijalankan menggunakan pipeline yang sama, meliputi data latih dan data uji yang identik, ambang pseudo-labelling yang sama, serta konfigurasi hyperparameter yang seragam. Seluruh hasil prediksi dievaluasi menggunakan prosedur pada Kode Semu 3.12. Performa masing-masing model kemudian dibandingkan berdasarkan metrik Precision, Recall, dan F1-score, baik pada tingkat label maupun agregat.

### 3.8.3 Uji Coba 3: Penambahan Fitur POS

Uji coba ketiga bertujuan untuk menguji pengaruh penambahan informasi Part-of-Speech tagging atau POS-tag terhadap performa prediksi entitas. Pada uji coba ini, model tanpa modul POS-tag dibandingkan dengan model yang menambahkan informasi POS-tag sebagai fitur pendamping pada masukan. Pengujian ini dilakukan untuk melihat apakah informasi kelas kata dapat membantu model dalam mengenali batas entitas dan membedakan tipe entitas. Kedua varian dilatih menggunakan data yang sama dan dievaluasi pada data uji yang sama dengan prosedur sebagaimana dijelaskan pada Kode Semu 3.12. Hasil evaluasi kemudian dibandingkan berdasarkan nilai F1-score per label dan metrik agregat untuk menilai apakah penambahan fitur POS-tag memberikan peningkatan performa yang signifikan terhadap hasil ekstraksi entitas.

## 3.9 Analisis Jaringan dan Pengujian Fungsional Knowledge Graph

Setelah knowledge graph terbentuk, dilakukan analisis jaringan untuk memahami strukturnya sekaligus pengujian fungsional untuk memverifikasi kelayakannya dalam penelusuran relasional.

### 3.9.1 Analisis Jaringan dengan Social Network Analysis

Bagian ini menganalisis struktur knowledge graph yang terbentuk menggunakan Social Network Analysis (SNA), terutama pada jaringan antar tokoh (Person) yang terhubung melalui keterlibatan bersama pada peristiwa yang sama. Analisis bertujuan mengetahui tokoh dan peristiwa yang paling berperan serta kelompok tokoh yang sering muncul bersama. Analisis jaringan dilakukan melalui beberapa tahap. Pertama, dibentuk proyeksi jaringan tokoh, yaitu jaringan yang menghubungkan dua tokoh apabila keduanya terlibat dalam peristiwa yang sama (co-participation). Bobot sisi pada jaringan ini digunakan untuk menunjukkan kekuatan keterhubungan antar-tokoh. Kedua, dihitung metrik sentralitas pada tingkat node, meliputi degree centrality, betweenness centrality, closeness centrality, dan PageRank (Elmezain et al., 2021; Zhang et al., 2021). Ketiga, dihitung metrik pada tingkat graf, yaitu kepadatan jaringan (density), koefisien pengelompokan (transitivity), ukuran jaringan, dan jumlah komponen. Keempat, dilakukan deteksi komunitas menggunakan algoritma Louvain, dengan kualitas pembagian komunitas diukur berdasarkan nilai modularitas (Q) (Anuar et al., 2024). Analisis jaringan ini dirancang ke dalam delapan skenario pengujian, yaitu G1 sampai G7, yang mencakup analisis pada tingkat tokoh, graf keseluruhan, peristiwa, lokasi, dan keterlibatan lintas fase, sebagaimana ditunjukkan pada Tabel 3.20. Pseudocode untuk perhitungan metrik inti pada jaringan tokoh disajikan pada Kode Semu 3.13. **Tabel 3.20 Rancangan Skenario Pengujian Analisis Jaringan**

| Kode | Skenario (Pertanyaan yang dijawab) | Entitas | Metode |
|---|---|---|---|
| G1 | Tokoh mana yang paling sentral dan paling terlibat | Person | Degree centrality |
| G2 | Tokoh mana yang menjadi penghubung/jembatan antar kelompok | Person | Betweenness centrality |
| G3 | Apakah tokoh terbagi menjadi kelompok- kelompok | Person | Deteksi komunitas (Louvain) |
| G4 | Peristiwa mana yang paling sentral dalam narasi | Event | Co-participation (PageRank/degree) |
| G5 | Bagaimana karakter struktur jaringan keseluruhan | Graf keseluruhan | Density, clustering, transitivity |
| G6 | Bagaimana wujud sub-graf lima peristiwa besar | Event (5) | Ekstraksi sub-graf dan analisisnya |
| G7 | Lokasi mana yang punya peran sentral | Location | Graf lokasi |
| G8 | Tokoh mana yang terlibat di paling banyak babak (fase) | Person → Event → fase | Jumlah fase unik tempat tokoh terlibat |

INPUT  : graph (knowledge graph) OUTPUT : metrik_centrality, komunitas, metrik_graf ALGORITMA:

1. BEGIN 2.
3. // sisi berbobot berdasarkan co-participation pada Event
4. G <- ProjectPersonNetwork(graph)
5. degree <- DegreeCentrality(G)
6. between <- BetweennessCentrality(G)
7. close <- ClosenessCentrality(G)
8. pagerank <- PageRank(G, weighted = TRUE)
9. density <- Density(G)
10. transit <- Transitivity(G)
11. komunitas <- Louvain(G)                // modularitas Q
12. SaveMetrics(

13.     degree,
14.     between,
15.     close,
16.     pagerank,
17.     density,
18.     transit,
19.     komunitas
20. )
21. RETURN metrik_centrality, komunitas, metrik_graf
22. END Kode Semu 3.13 Analisis Jaringan SNA Kode Semu 3.13 menunjukkan tahapan umum analisis struktur knowledge graph dengan Social Network Analysis. Proses dimulai dengan membentuk proyeksi jaringan tokoh, yaitu dua tokoh dihubungkan apabila sama-sama terlibat pada peristiwa yang sama (co- participation) dengan bobot sisi mencerminkan kekuatan keterhubungan. Selanjutnya dihitung ukuran sentralitas tingkat node, yaitu degree, betweenness, closeness, dan PageRank berbobot, untuk mengetahui tokoh yang paling berperan. Setelah itu dihitung ukuran tingkat graf seperti kepadatan dan koefisien pengelompokan, lalu dilakukan deteksi komunitas dengan algoritma Louvain yang kualitasnya diukur oleh nilai modularitas. Hasil akhir dari proses ini berupa tabel metrik sentralitas per tokoh, metrik tingkat graf, dan daftar komunitas. Dengan demikian, keluaran bagian ini memberi gambaran kuantitatif tentang tokoh dan peristiwa paling sentral serta kelompok tokoh yang sering muncul bersama, yang interpretasinya dibahas pada Bab 4. Output bagian ini berupa tabel metrik sentralitas per tokoh, metrik tingkat graf, dan daftar komunitas. Nilai-nilai metrik dan interpretasinya (misalnya tokoh paling sentral dan kelompok komunitas) disajikan dan dibahas pada Bab 4.

### 3.9.2 Evaluasi Fungsional Knowledge Graph

Evaluasi fungsional graf bertujuan untuk memastikan bahwa knowledge graph yang telah dibangun mampu menjalankan fungsi utamanya, yaitu mendukung penelusuran informasi berdasarkan hubungan antar entitas. Evaluasi ini memiliki fokus yang berbeda dari dua evaluasi sebelumnya. Evaluasi kualitas NER pada Subbab 3.8 menilai kemampuan model dalam mengenali entitas menggunakan metrik seperti F1-score, sedangkan analisis SNA pada Subbab
3.9.1 digunakan untuk mengkaji struktur jaringan melalui metrik sentralitas dan komunitas.
Sementara itu, evaluasi fungsional menilai apakah graf dapat digunakan untuk menelusuri informasi relasional dalam Sirah Nabawiyah. Dengan demikian, jika evaluasi sebelumnya berfokus pada akurasi model dan struktur jaringan, evaluasi fungsional berfokus pada kegunaan graf yang telah dibangun. Evaluasi fungsional dilakukan menggunakan pengujian berbasis kebutuhan (black-box). Pengujian ini menilai kemampuan graf dalam menjalankan fungsi yang telah ditetapkan tanpa membahas proses internal pembentukannya. Oleh karena itu, fungsi-fungsi yang harus dipenuhi oleh graf ditentukan terlebih dahulu sebelum pengujian dilakukan. Pertanyaan seperti “siapa saja yang terlibat dalam suatu peristiwa?” atau “di mana lokasi peristiwa yang melibatkan tokoh tertentu?” memerlukan penelusuran hubungan antar simpul. Kemampuan menelusuri hubungan tersebut menjadi salah satu alasan informasi Sirah Nabawiyah direpresentasikan dalam bentuk graf. Fungsi yang diuji disusun berdasarkan tujuan penelitian pada Subbab 1.4 dan kebutuhan penelusuran informasi yang telah dijelaskan pada bagian latar belakang. Knowledge graph dinyatakan layak secara fungsional apabila mampu memenuhi enam fungsi yang didefinisikan pada Tabel 3.21. Setiap fungsi diuji melalui satu skenario kueri Cypher yang mewakili kebutuhan penelusuran tersebut. Definisi setiap fungsi beserta skenario kueri dan pola relasi yang digunakan ditunjukkan pada Tabel 3.21. **Tabel 3.21 Skenario Kueri Evaluasi Graf**

| Fungsi | Kebutuhan Fungsional | Skenario Kueri (Contoh Pertanyaan) | Pola Relasi |
|---|---|---|---|
| F1 | Menemukan tokoh yang terlibat pada suatu peristiwa | Siapa saja yang terlibat dalam Perang Badar? | (Person)-[INVOLVED_IN]- >(Event) |
| F2 | Menemukan peristiwa yang terjadi di suatu lokasi | Peristiwa apa saja yang terjadi di Madinah? | (Event)-[OCCURRED_AT]- >(Location) |
| F3 | Menemukan peristiwa yang terjadi pada suatu waktu | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah? | (Event)-[OCCURRED_ON]- >(Time) |
| F4 | Menemukan peristiwa yang melibatkan tokoh tertentu | Peristiwa apa saja yang melibatkan Abu Bakar? | (Person)-[INVOLVED_IN]- >(Event) |
| F5 | Menelusuri rantai relasi lintas- entitas (multi-hop), yaitu melewati lebih dari satu relasi sekaligus | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | (Person)-[INVOLVED_IN]- >(Event)-[OCCURRED_AT]- >(Location) |
| F6 | Menelusuri urutan kronologis antar peristiwa | Urutan peristiwa berdasarkan relasi mendahului | (Event)-[PRECEDES]- >(Event) |

Keberhasilan setiap fungsi dinilai dengan menjalankan skenario kueri pada graf, kemudian memeriksa hasilnya berdasarkan empat kriteria. Pertama, kueri dapat dijalankan tanpa menghasilkan galat, yang menunjukkan bahwa kueri dapat diproses sesuai dengan struktur graf yang digunakan. Kedua, kueri menghasilkan data, yang menunjukkan bahwa entitas dan relasi yang dibutuhkan tersedia serta saling terhubung dalam graf. Kriteria ini diterapkan pada kasus pengujian yang telah diketahui memiliki jawaban dalam teks sumber. Ketiga, informasi yang dihasilkan sesuai dengan fakta dalam teks Sirah Nabawiyah berdasarkan pemeriksaan manual. Kriteria ini memastikan bahwa hasil kueri tidak hanya tersedia, tetapi juga sesuai dengan sumber data. Keempat, hasil kueri dapat ditelusuri kembali ke dokumen sumber melalui metadata provenance, seperti evidence (potongan teks bukti) dan halaman. Kriteria tersebut memastikan bahwa setiap informasi yang dihasilkan oleh graf memiliki sumber yang jelas dan dapat dipertanggungjawabkan. Keluaran pengujian disajikan dalam bentuk tabel hasil eksekusi kueri yang memuat status keberhasilan dan jumlah hasil yang diperoleh. Beberapa hasil kueri juga ditampilkan sebagai contoh untuk memperlihatkan kemampuan graf dalam menjawab kebutuhan penelusuran. Berdasarkan keseluruhan hasil tersebut, dilakukan penilaian terhadap kelayakan knowledge graph dalam mendukung penelusuran informasi relasional pada Sirah Nabawiyah.

<!-- ================================================================= -->
<!-- ✳ SISIPAN REVISI SIDANG — teks baru untuk bab ini (letak ada di tiap blok). -->
<!-- Perbaikan kecil sudah disisipkan inline di badan bab (cari penanda ✳ REVISI). -->
<!-- ================================================================= -->

## A. Ganti istilah "alias clustering" → "normalisasi alias"
Ganti di Subbab 3.7.1, Gambar 3.8, Kode Semu 3.8, dan seluruh narasi. Kalimat pembuka subbab:

> Penyatuan variasi nama entitas dilakukan melalui normalisasi alias, yaitu pemetaan berbagai
> variasi penulisan nama ke satu bentuk kanonik. Proses ini memanfaatkan daftar padanan yang
> disusun manual serta ukuran kemiripan string Jaro-Winkler sebagai pengaman, kemudian
> divalidasi manual. Jaro-Winkler di sini berperan sebagai ukuran kemiripan string, bukan sebagai
> algoritma clustering, sehingga keluarannya berupa peta alias, bukan klaster yang dievaluasi.

## B. Contoh Chunking (subbab chunking)

Teks setiap sub-bab dipecah menjadi potongan (chunk) berukuran paling banyak 1500 karakter dengan mempertahankan batas kalimat, sehingga tidak ada kalimat yang terpotong di tengah. Antar chunk diberi tumpang tindih (overlap) berupa satu kalimat, yaitu kalimat terakhir suatu chunk diulang sebagai kalimat pertama chunk berikutnya, agar konteks pada batas antar chunk tidak terputus. Metadata bab, sub-bab, dan halaman dipertahankan pada setiap chunk. Sebagai contoh, sub-bab "Kekuasaan di Berbagai Penjuru Arab" (halaman 53–54) yang melebihi 1500 karakter dipecah menjadi dua chunk. Kalimat "Sehingga adakalanya jika seorang pemimpin murka, sekian ribu mata pedang akan ikut berbicara tanpa perlu bertanya apa yang membuat pemimpin kabilah itu murka." menjadi kalimat overlap: kalimat tersebut menutup chunk pertama dan sekaligus membuka chunk kedua.

## C. Definisi Token, Subtoken, Chunk, Batch (subbab tokenisasi)

Perlu dibedakan empat istilah berikut. Chunk adalah potongan teks yang dapat memuat beberapa kalimat dan menjadi unit yang diberikan ke model. Token atau kata adalah unit hasil tokenisasi awal yang diberi label BIO. Subtoken adalah pecahan token yang dihasilkan tokenizer WordPiece IndoBERT dan menjadi unit yang benar-benar diproses model. Batch adalah kumpulan beberapa sequence yang diproses bersamaan pada satu langkah pelatihan. IndoBERT melakukan klasifikasi token atas satu urutan token yang memiliki konteks, bukan mengklasifikasikan setiap kata secara terpisah. Panjang maksimum sequence adalah 512 subtoken.

Karena satu kata dapat dipecah menjadi beberapa subtoken, label BIO yang berada pada tingkat kata diselaraskan ke tingkat subtoken dengan aturan berikut: hanya subtoken pertama dari setiap kata yang diberi label, sedangkan subtoken lanjutan dan token khusus ([CLS] dan [SEP]) diberi nilai -100 sehingga diabaikan oleh fungsi kerugian. Sebagai contoh, kata "Umair" dipecah menjadi subtoken "uma" dan "##ir"; hanya "uma" yang menerima label I-PERSON, sedangkan "##ir" diberi -100. Penyelarasan ini diimplementasikan menggunakan fungsi word_ids() dari tokenizer.

## D. Dasar Ambang Co-occurrence 200 Karakter (subbab pembentukan relasi)

Dua entitas dianggap berada dalam konteks yang sama apabila berada pada kalimat yang sama atau berjarak kurang dari 200 karakter satu sama lain. Ambang 200 karakter didasarkan pada karakteristik korpus. Panjang kalimat pada korpus memiliki median 100 karakter dan sekitar 84,9% kalimat berada pada 200 karakter atau kurang, sehingga jendela 200 karakter kira-kira menampung satu kalimat penuh beserta sedikit margin ke kalimat tetangga. Selain itu, sekitar 82,7% pasangan entitas yang berurutan dalam satu chunk berjarak kurang dari 200 karakter. Kedekatan juga menentukan bobot relasi secara bertingkat, yaitu 0,4 untuk jarak kurang dari 50 karakter, 0,3 untuk kurang dari 100 karakter, dan 0,2 untuk kurang dari 200 karakter. Dengan demikian, tidak seluruh entitas dalam satu sub-bab otomatis dihubungkan, melainkan hanya yang memenuhi syarat konteks tersebut. Ambang 200 karakter ini merupakan heuristik yang diadaptasi untuk korpus naratif Sirah.

Sebagai contoh relasi yang benar, kalimat "Abdurrahman bin Auf menuturkan, 'Tatkala aku sedang berada di tengah barisan pada Perang Badr…'" menghasilkan relasi keterlibatan Abdurrahman bin Auf pada Perang Badr yang didukung konteks satu kalimat. Sebaliknya, relasi dapat keliru pada tiga pola: adanya negasi (misalnya "Abu Lahab tidak ikut serta" pada Perang Badr), penyebut yang merupakan perawi dan bukan pelaku, serta penyebutan peristiwa lain yang kebetulan berdekatan.

## E. Prosedur Pengujian Validitas Semantis (subbab evaluasi fungsional)

Selain memeriksa keterlaksanaan kueri, setiap hasil yang dikembalikan oleh keenam fungsi diperiksa kesesuaiannya terhadap teks sumber. Unit pemeriksaan mengikuti bentuk keluaran tiap fungsi: pada F1–F4 berupa pasangan entitas dan relasi; pada F5 berupa jalur tokoh, peristiwa, dan lokasi yang dinyatakan sesuai hanya apabila kedua relasi pada jalur tersebut didukung teks sumber; dan pada F6 berupa pasangan peristiwa dengan relasi mendahului. Karena satu lokasi pada F5 dapat dicapai melalui beberapa jalur, unit penilaian adalah 21 jalur yang dikembalikan kueri, bukan 15 lokasi unik. Suatu hasil dinyatakan valid apabila potongan bukti pada halaman sumber secara langsung mendukung hubungan yang terbentuk, dan dinyatakan tidak valid apabila bukti menyangkal hubungan, hanya menyebutkan entitas secara berdekatan, atau merujuk peristiwa lain. Jawaban yang hanya benar sebagian diperlakukan sebagai tidak valid agar penilaian bersifat ketat. Pemeriksaan dilakukan secara manual oleh penulis dengan merujuk ke teks terjemahan Al-Mubarakfuri. Sebagai keterbatasan, pemeriksaan dilakukan oleh satu orang sehingga tidak terdapat pengukuran kesepakatan antar-anotator.

## F. Penanganan Negasi sebagai Keterbatasan

Pembentukan relasi berbasis kedekatan tidak memeriksa negasi. Akibatnya, kalimat yang menyatakan ketidakterlibatan dapat tetap menghasilkan relasi keterlibatan. Sebagai contoh, kalimat "Saat Perang Badr, Abu Lahab tidak ikut serta" tetap menghasilkan relasi Abu Lahab terlibat pada Perang Badr. Deteksi negasi tidak diterapkan pada penelitian ini dan dinyatakan sebagai keterbatasan.

## G. Dasar Pemilihan Hyperparameter (subbab pelatihan model)

Nilai hyperparameter tidak ditetapkan secara sembarang, melainkan diadopsi sebagai nilai awal dari penelitian acuan yang menangani tugas sejenis, yaitu NER berbasis IndoBERT dengan iterative self-training pada bahasa Indonesia berdaya rendah (Ariyanto dkk., 2025), lalu diterapkan dan diuji kembali pada dataset Sirah Nabawiyah. Learning rate 2e-5 dipilih karena merupakan nilai yang umum efektif untuk model berbasis transformer dan cukup kecil untuk menjaga kestabilan pelatihan. Batch size 16 dipilih untuk mengoptimalkan pemakaian memori GPU tanpa mengorbankan efisiensi. Pelatihan dilakukan selama 10 epoch dengan early stopping untuk mencegah overfitting, disertai weight decay 0,01 untuk memperbaiki generalisasi. Ambang confidence 0,9 digunakan pada penyaringan pseudo-label; pada penelitian acuan, ambang 0,7, 0,8, dan 0,9 telah dibandingkan dan 0,9 memberikan hasil terbaik karena hanya menerima prediksi berkepercayaan tinggi. Confidence sebuah prediksi dihitung sebagai rata-rata skor confidence seluruh token dalam teks. Adapun jumlah iterasi self-training dibatasi maksimal enam iterasi sebagai titik henti praktis karena peningkatan F1 sudah landai; batasan ini merupakan penyesuaian pada penelitian ini, bukan berasal dari penelitian acuan.

## H. Alur NER ke Knowledge Graph dengan Satu Contoh (subbab konstruksi KG)

Alur konstruksi ditelusuri melalui satu contoh data yang sama. Dari chunk pada halaman 165–168, kalimat "Tatkala Abu Jahal mengajaknya pergi saat Perang Badr…" ditokenisasi dan diberi label BIO, sehingga "Abu Jahal" berlabel B-PERSON dan I-PERSON serta "Perang Badr" berlabel B-EVENT dan I-EVENT. Hasil ekstraksi menghasilkan dua entitas, yaitu Abu Jahal bertipe Person dan Perang Badr bertipe Event. Kedua nama dinormalisasi ke bentuk kanonik melalui normalisasi alias. Karena kedua entitas berada dalam satu kalimat, keduanya menjadi pasangan kandidat relasi. Pasangan Person dan Event dipetakan menjadi relasi INVOLVED_IN dengan bobot sesuai kedekatan. Selanjutnya dibentuk simpul Abu Jahal dan simpul Perang Badr beserta sisi INVOLVED_IN di antaranya, lalu disimpan ke Neo4j. Relasi ini tetap dapat ditelusuri ke halaman sumber melalui properti bukti.

## I. Protokol Koreksi Manual (subbab pelabelan)

Pelabelan awal dilakukan secara semi-otomatis menggunakan kamus entitas dan pola ekspresi reguler, kemudian diperiksa kembali melalui satu pass review manual untuk memperbaiki kualitas anotasi. Cara semi-otomatis cepat tetapi menghasilkan kesalahan sistematis, yaitu entitas yang terlewat, batas entitas yang salah, kesalahan tipe (terutama nama yang dapat berupa lokasi atau peristiwa), entitas palsu, dan nama yang terpecah akibat artefak OCR. Contoh perbaikan meliputi "India" yang semula tidak teranotasi menjadi Location, kata "610" pada "610 M" yang dimasukkan sebagai bagian entitas Time, "peperangan Badr" yang semula Location diperbaiki menjadi Event, penyebutan pada rujukan kitab seperti "bab Ghazwah Dzatu Qarad" yang dibatalkan menjadi bukan entitas, serta "Mush ab" yang disambung menjadi "Mush'ab". Koreksi mengacu pada pedoman anotasi yang mengunci keputusan pelabelan dan diterapkan pada satu sumber kebenaran di tingkat span. Koreksi dilakukan oleh penulis sebagai anotator tunggal, sehingga tidak terdapat anotator kedua maupun pengukuran kesepakatan antar-anotator; hal ini dinyatakan sebagai keterbatasan.
