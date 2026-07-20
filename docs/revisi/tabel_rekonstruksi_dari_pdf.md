# Tabel Direkonstruksi dari PDF (akurat, cek-silang dgn Word)


**Tabel 2.1 Hasil Penelitian Terdahulu**

| Penelitian | Sumber Data | Metode | Analisis |
|---|---|---|---|
| A Comprehensive Survey on Automatic Knowledge Graph Construction (Zhong et al., 2024) | Survey >300 metode KGC | Review sistematis; memetakan KGC ke tahap akuisisi– refinement– evolution | Penelitian ini menunjukkan bahwa konstruksi knowledge graph dapat dipahami sebagai proses bertahap, mulai dari akuisisi pengetahuan (ekstraksi entitas dan relasi, serta coreference resolution) hingga penyempurnaan dan evolusi graf. Kerangka ini membantu |


**Tabel 2.2 Contoh Daftar Label NER**

| Label | Deskripsi |
|---|---|
| PERSON | Nama orang atau tokoh, bisa berupa nama asli atau nama panggilan |
| LOC | Nama lokasi geografis, seperti nama tempat, kota, gunung, dll |
| ORG | Nama organisasi atau institusi |
| DATE | Informasi waktu bisa berupa tanggal atau periode |
| TIME | Sama seperti “DATE” tetapi dengan durasi kurang dari 1 hari atau waktu spesifik tertentu |
| EVENT | Nama sebuah kejadian, seperti perang, |


**Tabel 2.3 Penjelasan Label BIO**

| Label | Keterangan |
|---|---|
| B-XXX | Menandai awal token dari entitas XXX |
| I-XXX | Menandai lanjutan token dari entitas XXX yang sama dengan tag sebelumnya |
| O | Menandai token yang berada di luar entitas |


**Tabel 2.4 Perbandingan Model yang digunakan**

| Model | Peran | Karakter Umum |
|---|---|---|
| indolem/indobert-base-uncased | Baseline | IndoBERT uncased untuk bahasa Indonesia |
| cahya/bert-base-indonesian- 1.5G | Model Pembanding | BERT-base uncased yang dilatih pada korpus bahasa Indonesia |
| cahya/distilbert-base- indonesian |  | Versi distilasi dari Indonesian BERT base model |
| indobenchmark/indobert-base- p1 |  | IndoBERT phase 1 berbasis objective MLM dan NSP |
| cahya/roberta-base-indonesian- 1.5G |  | Variasi RoBERTa untuk bahasa Indonesia |


**Tabel 2.5 Contoh Penggunaan POS Tagging**

| Token | POS Tag | Keterangan | Contoh label NER |
|---|---|---|---|
| Nabi | PROPN | Nama diri/gelar tokoh | B-PERSON |
| Muhammad | PROPN | nama diri | I-PERSON |
| hijrah | VERB | tindakan/peristiwa | B-EVENT |
| ke | ADP | preposisi | O |
| Madinah | PROPN | nama tempat | B-LOCATION |
| pada | ADP | preposisi waktu | O |
| tahun | NOUN | penanda waktu | B-TIME |
| 622 | NUM | numeralia | I-TIME |
| M | PROPN/SYM | penanda kalender | I-TIME |


**Tabel 3.1 Spesifikasi Perangkat Keras Penelitian**

| Komponen | Spesifikasi |
|---|---|
| Prosesor | Intel Core i7-8750H @ 2.20GHz |
| RAM | 16 GB |
| Penyimpanan | 1 TB |
| GPU | opsional |


**Tabel 3.2 Spesifikasi Perangkat Lunak Penelitian**

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


**Tabel 3.4 Struktur Keluaran Dataset**

| Nama Kolom | Tipe Data | Deskripsi | Contoh Nilai |
|---|---|---|---|
| judul_bab | String | Nama bab utama hasil segmentasi berdasarkan daftar isi | POSISI BANGSA ARAB DAN KAUMNYA |
| judul_sub_bab | String | Nama sub-bab di bawah bab terkait | Posisi Bangsa Arab |
| halaman | String | Rentang halaman sumber konten sub-bab | 34-35 |
| teks | String | Isi teks sub-bab yang sudah dibersihkan dan digabung | Menurut bahasa, Arab artinya padang pasir, tanah gundul, dan gersang yang tiada air dan tanamannya … |


**Tabel 3.5 Contoh Perubahan Hasil Preprocessing**

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
|  | xI Ls xO J JI J O aa O s!LcK ... | (seluruh kalimat dihapus) |


**Tabel 3.6 Penjelasan Hasil Keluaran Chunking**

| Nama Kolom | Tipe Data | Deskripsi | Nilai |
|---|---|---|---|
| chunk_id | String | Identitas unik setiap chunk | 000000-001 |
| doc_id | String | Identitas dokumen atau sub-bab asal | 0 |
| chunk_index |  | Urutan chunk dalam dokumen | 1 |
| judul_bab | String | Bab sumber | POSISI BANGSA ARAB DAN KAUMNYA |
| judul_sub_bab | String | Sub-bab sumber | UNLABELED SECTION |
| halaman | String | Halaman sumber pada dokumen asli | 34 |
| teks_chunk | String | Isi potongan teks | "Pada hakikatnya istilah Sirah Nabawiyah merupakan ungkapan tentang risalah yang dibawa Rasulullah kepada manusia, untuk mengeluarkan mereka dari kegelapan kepada cahaya, dari penyembahan terhadap hamba kepada penyembahan Allah. ..." |


**Tabel 3.7 Contoh Kandidat Pra-anotasi Semi-Otomatis**

| Entitas | Label | start_char | end_char |
|---|---|---|---|
| bulan Dzul Qi'dah | TIME | 5 | 22 |
| Rasulullah | PERSON | 50 | 60 |
| Abu Bakar Ash-Shiddiq | PERSON | 70 | 91 |
| Ali bin Abu Thalib | PERSON | 316 | 334 |
| Abu Bakar | PERSON | 431 | 440 |


**Tabel 3.8 Skema Label Entitas**

| Label | Keterangan | Contoh |
|---|---|---|
| PERSON | Nama tokoh, individu, atau kabilah/Bani | Muhammad, Abu Bakar, Bani Quraizhah |
| EVENT | Nama peristiwa | Perang Badar, Hijrah, Fathu Makkah |
| LOCATION | Nama tempat atau wilayah | Makkah, Madinah, Gua Hira |
| TIME | Ungkapan waktu atau periode | tahun ke-2 Hijriah, bulan Ramadhan |


**Tabel 3.9 Contoh Penandaan BIO**

| Token | Label |
|---|---|
| Rasulullah | B-PERSON |
| hijrah | O |
| ke | O |
| Madinah | B-LOCATION |
| pada | O |
| tahun | B-TIME |
| pertama | I-TIME |
| Hijriah | I-TIME |


**Tabel 3.10 Distribusi Label Data Latih**

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
| I-LOCATION | 72 | 0,07% |


**Tabel 3.11 Hyperparameter Pelatihan NER**

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


**Tabel 3.12 Contoh Keluaran Ekstraksi Entitas NER**

| Entitas | Label | start_char | end_char |
|---|---|---|---|
| Madinah | LOCATION | 8 | 15 |
| Perjanjian Hudaibiyah | EVENT | 280 | 301 |
| Fathu Makkah | EVENT | 423 | 435 |
| bulan Ramadhan | TIME | 441 | 455 |
| Rasulullah | PERSON | 740 | 750 |
| bulan Rabi'ul Awwal | TIME | 756 | 775 |


**Tabel 3.13 Contoh Pemetaan Variasi Nama ke Bentuk Kanonik**

| Variasi Nama | Bentuk Kanonik | Jenis Variasi |
|---|---|---|
| Rasulullah | Muhammad | Sebutan berbeda |
| Muhammad bin Abdullah |  | Nama bernasab |
| Abu Bakar Ash-Shiddiq | Abu Bakar | Gelar tambahan |
| Abu Bakkar |  | Variasi ejaan (artefak OCR) |
| Umar | Umar bin Al-Khaththab | Bentuk pendek |
| Umar bin Al-Khathab |  | Variasi ejaan (artefak OCR) |
| Abu Sofyan | Abu Sufyan bin Harb | Variasi ejaan |


**Tabel 3.14 Rancangan Tipe Relasi Inti**

| Pasangan Entitas | Tipe Relasi | Makna |
|---|---|---|
| PERSON ke EVENT | INVOLVED_IN | Tokoh terlibat dalam peristiwa |
| EVENT ke LOCATION | OCCURRED_AT | Peristiwa terjadi di suatu tempat |
| EVENT ke TIME | OCCURRED_ON | Peristiwa terjadi pada suatu waktu |


**Tabel 3.15 Atribut Node**

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


**Tabel 3.17 Contoh Edge Hasil Pembentukan Relasi**

| Sumber (label) | Relasi | Tujuan (label) | weight | halaman |
|---|---|---|---|---|
| Amr bin Al-Ash (Person) | INVOLVED_IN | Perang Badr (Event) | 0,5 | 133-137 |
| Perang Badr (Event) | OCCURRED_AT | Yatsrib (Location) | 0,5 | 165-168 |
| Perang Yarmuk (Event) | OCCURRED_ON | Tahun 13 H (Time) | 0,5 | 47-48 |
| Ibrahim (Person) | KELUARGA | Isma'il (Person) | 0,55 | - |


**Tabel 3.18 Contoh Pemetaan Peristiwa ke Periode**

| Peristiwa | periode_bab | page_range | frequency |
|---|---|---|---|
| Kelahiran Nabi | Nasab & Kelahiran Nabi | 73-93 | 29 |
| Hijrah Ke Habasyah | Dakwah Jahriyah & Tekanan Quraisy | 133-160 | 13 |
| Hijrah Ke Madinah | Hijrah ke Madinah | 214-232 | 26 |
| Perang Badr | Perang Badr & Dampaknya | 266-304 | 51 |
| Fathul Makkah | Perang Mu'tah & Penaklukan Makkah | 524-536 | 3 |


**Tabel 3.19 Rancangan Uji Coba Evaluasi NER**

| Skenario | Penjelasan | Metrik Evaluasi |
|---|---|---|
| Uji Coba 1: Penanganan ketidakseimbangan kelas | Memvariasikan teknik penanganan data tidak seimbang (alur dasar vs weighted cross-entropy vs contrastive learning vs augmentation) untuk menguji pengaruhnya terhadap kelas minoritas | Precision, Recall, dan F1-Score (per label dan macro-average) |
| Uji Coba 2: Perbandingan model | Memvariasikan model dasar (backbone) pada iterative self-training untuk menguji model pra-latih mana yang paling sesuai | Precision, Recall, dan F1-Score (per label dan agregat antar model) |
| Uji Coba 3: Pengaruh modul POS-tag | Memvariasikan ada atau tidaknya modul POS-tag untuk menguji pengaruh informasi POS-tag terhadap prediksi entitas | Precision, Recall, dan F1-Score (per label, dengan dan tanpa POS- tag) |


**Tabel 3.20 Rancangan Skenario Pengujian Analisis Jaringan**

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


**Tabel 3.21 Skenario Kueri Evaluasi Graf**

| Fungsi | Kebutuhan Fungsional | Skenario Kueri (Contoh Pertanyaan) | Pola Relasi |
|---|---|---|---|
| F1 | Menemukan tokoh yang terlibat pada suatu peristiwa | Siapa saja yang terlibat dalam Perang Badar? | (Person)-[INVOLVED_IN]- >(Event) |
| F2 | Menemukan peristiwa yang terjadi di suatu lokasi | Peristiwa apa saja yang terjadi di Madinah? | (Event)-[OCCURRED_AT]- >(Location) |
| F3 | Menemukan peristiwa yang terjadi pada suatu waktu | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah? | (Event)-[OCCURRED_ON]- >(Time) |
| F4 | Menemukan peristiwa yang melibatkan tokoh tertentu | Peristiwa apa saja yang melibatkan Abu Bakar? | (Person)-[INVOLVED_IN]- >(Event) |
| F5 | Menelusuri rantai relasi lintas- entitas (multi-hop), yaitu melewati lebih dari satu relasi sekaligus | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | (Person)-[INVOLVED_IN]- >(Event)-[OCCURRED_AT]- >(Location) |
| F6 | Menelusuri urutan kronologis antar peristiwa | Urutan peristiwa berdasarkan relasi mendahului | (Event)-[PRECEDES]- >(Event) |


**Tabel 4.1 Statistik Data Latih dan Data Uji**

| Statistik | Data latih (train) | Data uji (test) |
|---|---|---|
| Jumlah chunk | 590 | 254 |
| Jumlah token | 116.353 | 49.739 |
| Jumlah entitas | 4.247 | 1.969 |
| Person | 2.920 | 1.302 |
| Location | 972 | 474 |
| Event | 167 | 75 |
| Time | 188 | 118 |


**Tabel 4.2 Precision, Recall, dan F1-score Agregat Uji Coba 1**

| Skenario | Precision | Recall | F1-score (mikro) |
|---|---|---|---|
| Baseline | 0,9524 | 0,9548 | 0,9536 |
| Weighted cross-entropy | 0,9427 | 0,9533 | 0,9480 |
| SCL | 0,9543 | 0,9548 | 0,9546 |
| JSCL | 0,9415 | 0,9487 | 0,9451 |
| Augmentation | 0,9756 | 0,9756 | 0,9756 |


**Tabel 4.3 F1-score per Kelas Entitas pada Uji Coba 1**

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | Macro F1 |
|---|---|---|---|---|---|
| Baseline | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| Weighted cross-entropy | 0,9616 | 0,9432 | 0,9231 | 0,8347 | 0,9156 |
| SCL | 0,9687 | 0,9488 | 0,9600 | 0,8170 | 0,9236 |
| JSCL | 0,9611 | 0,9467 | 0,9600 | 0,7572 | 0,9062 |
| Augmentation | 0,9835 | 0,9755 | 0,9542 | 0,9038 | 0,9543 |


**Tabel 4.4 Rincian Jenis Kesalahan Tingkat Token pada Uji Coba 1**

| Skenario | Total Error | FP (over- detection) | FN (entitas terlewat) | Misklasifikasi Tipe | Kesalahan Batas B/I |
|---|---|---|---|---|---|
| Baseline | 165 | 55 | 98 | 5 | 7 |
| Weighted cross- entropy | 174 | 69 | 84 | 11 | 10 |
| SCL | 178 | 62 | 102 | 7 | 7 |
| JSCL | 185 | 69 | 93 | 12 | 11 |
| Augmentation | 78 | 25 | 41 | 4 | 8 |


**Tabel 4.5 Contoh False Positive pada Chunk 000007-007**

| Token | Ground-truth | Prediksi |
|---|---|---|
| . | O | O |
| Hijabah | O | B-LOCATION |
| atau | O | O |
| Wewenang | O | O |


**Tabel 4.6 Contoh False Negative pada Chunk 000001-002**

| Token | Ground-truth | Prediksi |
|---|---|---|
| India | B-LOCATION | B-LOCATION |
| Dan | O | O |
| Cina | B-LOCATION | O |
| . | O | O |


**Tabel 4.7 Contoh Kesalahan Klasifikasi Tipe pada Chunk 000338-001**

| Token | Ground-truth | Prediksi |
|---|---|---|
| di | O | O |
| Hudaibiyah. | B-LOCATION | B-EVENT |
| . | O | O |


**Tabel 4.8 Contoh Kesalahan Batas Entitas pada Chunk 000018-001**

| Token | Ground-truth | Prediksi |
|---|---|---|
| Senin | B-TIME | B-TIME |
| pagi | I-TIME | I-TIME |
| , | I-TIME | I-TIME |
| tanggal | B-TIME | I-TIME |
| 9 | I-TIME | I-TIME |
| Rabi’ul | I-TIME | I-TIME |
| Awwal | I-TIME | I-TIME |


**Tabel 4.9 Distribusi Label Token Sebelum dan Sesudah Augmentasi**

| Label token | Sebelum augmentasi | Sesudah augmentasi | Perubahan |
|---|---|---|---|
| O (bukan entitas) | 108.815 | 163.352 | +54.537 (+50%) |
| Person (B+I) | 5.519 | 8.311 | +2.792 (+51%) |
| Location (B+I) | 1.038 | 1.875 | +837 (+81%) |
| Time (B+I) | 664 | 1.107 | +443 (+67%) |
| Event (B+I) | 317 | 943 | +626 (+198%) |
| Total token | 116.353 | 175.588 | +59.235 (+51%) |


**Tabel 4.10 Precision, Recall, dan F1-score Agregat Uji Coba 2**

| Model | Precision | Recall | F1-score (mikro) |
|---|---|---|---|
| IndoBERT uncased (baseline) | 0,9524 | 0,9548 | 0,9536 |
| Cahya uncased | 0,9388 | 0,9187 | 0,9286 |
| DistilBERT uncased | 0,9502 | 0,9208 | 0,9353 |
| IndoBERT cased | 0,7289 | 0,8329 | 0,7774 |
| RoBERTa | 0,7654 | 0,8532 | 0,8069 |


**Tabel 4.11 F1-score per Kelas Entitas pada Uji Coba 2**

| Model | F1 Person | F1 Location | F1 Event | F1 Time | F1 makro |
|---|---|---|---|---|---|
| IndoBERT uncased (baseline) | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| Cahya uncased | 0,9493 | 0,9232 | 0,9315 | 0,7203 | 0,8811 |
| DistilBERT uncased | 0,9581 | 0,9232 | 0,9116 | 0,7479 | 0,8852 |
| IndoBERT cased | 0,7843 | 0,8717 | 0,5549 | 0,5461 | 0,6893 |
| RoBERTa | 0,8135 | 0,8766 | 0,7654 | 0,5404 | 0,7490 |


**Tabel 4.12 Perubahan F1 Model Anomali Selama Self-Training**

| Model | F1 base | F1 iterasi 2 | F1 iterasi 4 | F1 iterasi 6 |
|---|---|---|---|---|
| IndoBERT cased | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |


**Tabel 4.13 Kesalahan Batas Person pada IndoBERT Cased, Chunk 000013-004**

| Token | Ground-truth | Prediksi |
|---|---|---|
| dari | O | O |
| Amr | B-PERSON | I-PERSON |
| bin | I-PERSON | I-PERSON |
| Syu’aib | I-PERSON | B-PERSON |
| . | O | O |


**Tabel 4.14 Kesalahan Batas Person pada RoBERTa, Chunk 000007-006**

| Token | Ground-truth | Prediksi |
|---|---|---|
| dari | O | O |
| Amr | B-PERSON | I-PERSON |
| bin | I-PERSON | I-PERSON |
| Syu’aib | I-PERSON | I-PERSON |


**Tabel 4.15 Precision, Recall, F1-score Agregat, dan Jumlah Kesalahan Uji Coba 3**

| Skenario | Precision | Recall | F1-score (mikro) |
|---|---|---|---|
| Baseline | 0,9524 | 0,9548 | 0,9536 |
| POS | 0,9628 | 0,9467 | 0,9547 |


**Tabel 4.16 F1-score per Kelas Entitas pada Uji Coba 3**

| Skenario | F1 Person | F1 Location | F1 Event | F1 Time | F1 makro |
|---|---|---|---|---|---|
| Baseline | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| POS | 0,9693 | 0,9466 | 0,9333 | 0,8376 | 0,9217 |


**Tabel 4.17 Rincian Jenis Kesalahan Tingkat Token pada Uji Coba 3**

| Skenario | Total Error | FP (over- detection) | FN (entitas terlewat) | Misklasifikasi Tipe | Kesalahan Batas B/I |
|---|---|---|---|---|---|
| Baseline | 165 | 55 | 98 | 5 | 7 |
| POS | 164 | 40 | 106 | 10 | 8 |


**Tabel 4.18 Contoh False Negative pada Chunk 000002-004**

| Token | Ground-truth | Prediksi |
|---|---|---|
| pula | O | O |
| ke | O | O |
| Pakistan | B-LOCATION | O |
| , | O | O |
| dan | O | O |


**Tabel 4.19 Komposisi Node Knowledge Graph**

| Label simpul | Jumlah | Keterangan |
|---|---|---|
| Person | 901 | Tokoh yang disebutkan dalam teks |
| Time | 167 | Waktu yang disebutkan dalam teks |
| Location | 74 | Lokasi yang disebutkan dalam teks |
| Event | 35 | Peristiwa dalam Sirah Nabawiyah |
| Period | 15 | Fase kronologis Sirah Nabawiyah |
| Total | 1.192 | Seluruh simpul yang tersimpan dalam Neo4j |


**Tabel 4.20 Komposisi Edge Knowledge Graph**

| Jenis relasi | Jumlah | Keterangan |
|---|---|---|
| KELUARGA | 312 | Hubungan kekerabatan antar tokoh |
| INVOLVED_IN | 229 | Keterlibatan tokoh dalam peristiwa |
| OCCURRED_AT | 44 | Hubungan peristiwa dengan lokasi |
| OCCURRED_ON | 46 | Hubungan peristiwa dengan waktu |
| SAHABAT | 33 | Hubungan persahabatan antar tokoh |
| PRECEDES | 17 | Urutan kronologis antar peristiwa |
| MUSUH | 12 | Hubungan permusuhan antar tokoh |
| Subtotal relasi antar entitas | 693 | Relasi unik setelah penggabungan duplikat |
| IN_PERIOD | 35 | Hubungan peristiwa dengan periode |
| Total | 728 | Seluruh relasi yang tersimpan dalam Neo4j |


**Tabel 4.21 Statistik Jaringan Tokoh**

| Metrik | Nilai |
|---|---|
| Jumlah node (Person) | 137 |
| Jumlah edge | 1.853 |
| Kepadatan (density) | 0,1989 |
| Rata-rata koefisien pengelompokan lokal | 0,7100 |
| Transitivity global | 0,7957 |
| Jumlah komponen | 5 |
| Ukuran komponen terbesar | 128 simpul |
| Rata-rata panjang lintasan pada komponen terbesar | 1,96 |
| Jumlah komunitas Louvain | 8 |
| Modularitas Louvain | 0,2831 |


**Tabel 4.22 Sepuluh Tokoh dengan Nilai Sentralitas Tertinggi**

| Peringkat | Tokoh | Degree centrality | Closeness centrality | PageRank |
|---|---|---|---|---|
| 1 | Muhammad | 0,7941 | 0,7906 | 0,0509 |
| 2 | Ali bin Abu Thalib | 0,5735 | 0,6516 | 0,0240 |
| 3 | Abu Jahal | 0,5515 | 0,6516 | 0,0230 |
| 4 | Umar bin Al-Khaththab | 0,5809 | 0,6552 | 0,0223 |
| 5 | Abu Bakar | 0,5441 | 0,6376 | 0,0212 |
| 6 | Abu Sufyan bin Harb | 0,5368 | 0,6376 | 0,0193 |
| 7 | Aisyah | 0,5221 | 0,6275 | 0,0186 |
| 8 | Abu Azzah | 0,5147 | 0,6242 | 0,0161 |
| 9 | Khunais bin Hudzafah | 0,5147 | 0,6242 | 0,0161 |
| 10 | Utsman bin Affan | 0,5221 | 0,6308 | 0,0158 |


**Tabel 4.23 Sepuluh Tokoh dengan Nilai Betweenness Centrality Tertinggi**

| Peringkat | Tokoh | Betweenness centrality |
|---|---|---|
| 1 | Muhammad | 0,2808 |
| 2 | Jabir bin Abdullah | 0,0635 |
| 3 | Ummu Kultsum | 0,0548 |
| 4 | Husain bin Ali | 0,0548 |
| 5 | Ali bin Abu Thalib | 0,0441 |
| 6 | Abdullah bin Ubay bin Salul | 0,0393 |
| 7 | Al-Barra' bin Azib | 0,0380 |
| 8 | Ibnu Hajar | 0,0380 |
| 9 | Salamah bin Al-Akwa' | 0,0373 |
| 10 | Abu Bakar | 0,0294 |


**Tabel 4.24 Sepuluh Peristiwa dengan Nilai PageRank Tertinggi**

| Peringkat | Peristiwa | PageRank | Frekuensi |
|---|---|---|---|
| 1 | Perang Badr | 0,0965 | 53 |
| 2 | Perang Uhud | 0,0889 | 43 |
| 3 | Perang Khandaq | 0,0674 | 20 |
| 4 | Perjanjian Hudaibiyah | 0,0442 | 20 |
| 5 | Baiat Aqabah Kubra | 0,0424 | 4 |
| 6 | Perang Dzul Usyairah | 0,0404 | 1 |
| 7 | Perang Khaibar | 0,0382 | 12 |
| 8 | Perang Bani Al-Ashfar | 0,0353 | 1 |
| 9 | Perang Dzatur Riqa' | 0,0348 | 2 |
| 10 | Perang Tha'if | 0,0344 | 4 |


**Tabel 4.25 Sepuluh Lokasi dengan Nilai Weighted Degree Tertinggi**

| Peringkat | Lokasi | Weighted degree |
|---|---|---|
| 1 | Madinah | 661 |
| 2 | Habasyah | 561 |
| 3 | Makkah | 561 |
| 4 | Syam | 530 |
| 5 | Yatsrib | 528 |
| 6 | Ash-Shafra | 525 |
| 7 | Tihamah | 525 |
| 8 | Badr | 525 |
| 9 | Najd | 525 |
| 10 | Aqabah | 297 |


**Tabel 4.26 Tokoh dengan Keterlibatan Lintas Fase Terbanyak**

| Peringkat | Tokoh | Jumlah fase | Jumlah peristiwa |
|---|---|---|---|
| 1 | Muhammad | 5 | 22 |
| 2 | Umar bin Al-Khaththab | 3 | 5 |
| 3 | Abu Bakar | 3 | 4 |
| 4 | Ali bin Abu Thalib | 2 | 7 |
| 5 | Zaid bin Haritsah | 2 | 5 |
| 6 | Aisyah | 2 | 4 |


**Tabel 4.27 Ringkasan Subgraf Lima Peristiwa Besar**

| Peristiwa | Periode | Jumlah tokoh | Jumlah lokasi | Jumlah waktu |
|---|---|---|---|---|
| Perang Badr | P8 | 44 | 9 | 6 |
| Perang Uhud | P9 | 41 | 3 | 10 |
| Perjanjian Hudaibiyah | P11 | 7 | 5 | 4 |
| Perang Khaibar | P11 | 7 | 2 | 1 |
| Perang Tabuk | P13 | 4 | 0 | 1 |


**Tabel 4.28 Contoh Ketidaksesuaian Hasil dengan Teks Sumber**

| Fungsi | Skenario pengujian | Eksekusi | Jumlah hasil | Tidak kosong | Sesuai sumber | Terlacak |
|---|---|---|---|---|---|---|
| F1 | Menemukan tokoh yang terlibat dalam Perang Badr | berhasil | 58 tokoh | ya | tidak | ya |
| F2 | Menemukan peristiwa yang terjadi di Madinah | berhasil | 10 peristiwa | ya | tidak | ya |
| F3 | Menemukan peristiwa yang terjadi pada tahun 2 H | berhasil | 4 peristiwa | ya | tidak | ya |
| F4 | Menemukan peristiwa yang melibatkan Abu Bakar | berhasil | 4 peristiwa | ya | tidak | ya |
| F5 | Menelusuri lokasi peristiwa yang melibatkan Umar bin Al- Khaththab | berhasil | 15 lokasi | ya | tidak | ya |
| F6 | Menelusuri urutan kronologis antarperistiwa | berhasil | 17 relasi | ya | tidak | ya |


**Tabel 4.29 Contoh Ketidaksesuaian Hasil dengan Teks Sumber**

| Fungsi | Contoh hasil graf | Potongan evidence | Hasil pemeriksaan |
|---|---|---|---|
| F1 | Abu Lahab terlibat dalam Perang Badr | “Saat Perang Badr, Abu Lahab tidak ikut serta.” | Tidak sesuai. Bukti secara langsung menyangkal keterlibatan Abu Lahab. Relasi terbentuk karena konteks negasi belum dipertimbangkan. |
| F2 | Perang As-Sawiq terjadi di Madinah | “Urusan di Madinah beliau serahkan kepada Abu Lubabah...” | Tidak sesuai. Madinah merupakan wilayah yang ditinggalkan dan diserahkan kepada seorang wakil, bukan lokasi berlangsungnya Perang As-Sawiq. |
| F3 | Perang Badr terjadi pada bulan Syawwal 2 Hijriah | “Peperangan ini terjadi pada bulan Syawwal 2 Hijriyah, selang tujuh hari sepulang dari Badr.” | Tidak sesuai. Keterangan waktu tersebut merujuk pada peperangan setelah kepulangan dari Badr, bukan Perang Badr. |
| F4 | Abu Bakar terlibat dalam Baiat Aqabah Kubra | “Dua bulan lebih beberapa hari setelah Baiat Aqabah Kubra ... tersisa di Makkah kecuali Rasulullah, Abu Bakar dan Ali.” | Tidak sesuai. Abu Bakar disebut dalam konteks keadaan setelah Baiat Aqabah Kubra, bukan sebagai peserta peristiwa tersebut. |
| F5 | Peristiwa yang melibatkan Umar dalam Perang Badr berlangsung di Ash-Shafra | Keterlibatan: “Umar ... sedang membicarakan kemuliaan ... di Perang Badr.” Lokasi: “...meninggal dunia di Ash- Shafra’, empat atau lima hari setelah Perang Badr...” | Tidak sesuai. Bukti pertama hanya menunjukkan Umar sedang membicarakan Perang Badr, sedangkan bukti kedua menempatkan Ash-Shafra dalam perjalanan pulang setelah peristiwa. |
| F6 | Fathul Makkah mendahului Perang Uhud | “Fathul Makkah (BAB: Peringatan di Makkah) → Perang Uhud (BAB: Aktivitas Pasukan antara Perang Badr dan Perang Uhud).” | Tidak sesuai. Bukti hanya menunjukkan urutan posisi penyebutan dalam dokumen. Secara kronologis, Perang Uhud terjadi sebelum Fathul Makkah. |


**Tabel 4.30 Ringkasan Keterbatasan Knowledge Graph**

| Aspek | Keterbatasan | Dampak terhadap hasil |
|---|---|---|
| Cakupan entitas | Graf bergantung pada entitas yang berhasil dikenali oleh model NER. Peristiwa yang dinyatakan melalui kata kerja atau uraian deskriptif tidak selalu dikenali sebagai entitas Event. | Peristiwa penting seperti kelahiran, turunnya wahyu pertama, dan wafat Nabi belum seluruhnya muncul sebagai simpul peristiwa. |
| Pembentukan relasi | Relasi dibentuk berdasarkan kedekatan kemunculan entitas dalam bagian teks yang sama. | Tokoh, lokasi, atau waktu dapat terhubung dengan peristiwa meskipun hanya disebut dalam konteks sebelum atau setelah peristiwa tersebut. |
| Pemahaman konteks | Pembentukan relasi belum sepenuhnya mempertimbangkan negasi, peran sintaksis, dan cakupan keterangan dalam kalimat. | Pernyataan seperti “Abu Lahab tidak ikut serta” masih dapat membentuk relasi INVOLVED_IN. |
| Makna relasi | Relasi INVOLVED_IN belum membedakan bentuk keterlibatan, peran tokoh, dan pihak yang diwakili. | Tokoh dari pihak Muslim dan Quraisy dapat berada dalam subgraf peristiwa yang sama tanpa keterangan mengenai peran atau kubunya. |
| Normalisasi entitas | Beberapa nama yang merujuk pada entitas sama masih disimpan sebagai simpul berbeda. | Nama seperti Madinah dan Yatsrib dapat diperlakukan sebagai dua lokasi yang berbeda sehingga memengaruhi jumlah simpul dan hubungan. |
| Relasi kronologis | Sebagian relasi PRECEDES dibentuk berdasarkan urutan penyebutan dalam dokumen. | Urutan kemunculan dalam teks dapat menghasilkan hubungan kronologis yang terbalik ketika suatu peristiwa lama disebut kembali pada pembahasan berikutnya. |
| Penelusuran multi-hop | Jawaban penelusuran lintas entitas bergantung pada ketepatan setiap relasi yang dilalui. | Kesalahan pada satu relasi dapat diteruskan dan menghasilkan lokasi atau peristiwa yang tidak sesuai pada akhir penelusuran. |
| Provenance | Seluruh relasi memiliki evidence dan halaman, tetapi isi bukti tidak selalu mendukung hubungan secara langsung. | Jawaban dapat ditelusuri kembali ke sumber, tetapi tetap memerlukan pemeriksaan manual untuk memastikan kebenarannya. |
| Cakupan sumber | Graf dibangun dari sumber Sirah yang digunakan dalam penelitian ini. | Graf merepresentasikan isi dan cara penyajian sumber tersebut, bukan seluruh variasi riwayat Sirah Nabawiyah. |
