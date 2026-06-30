# BAB 2 TINJAUAN PUSTAKA

> **[CATATAN PENYUSUN, hapus saat finalisasi]**
> Struktur Dasar Teori memakai **versi pilar (ramping)** sesuai arahan Bu Dini: **5 subbab total termasuk Penelitian Terdahulu** (mengikuti gaya buku teman, 4-5 subbab). Tiap pilar adalah teori inti, BUKAN penjelasan langkah demi langkah (langkah teknis ada di Bab 3).
> Peleburan dari struktur granular proposal: **OCR** dilebur ke subbab Sirah; **SRL + Iterative Self-Training** masuk ke dalam **NER**; **Neo4j + Ekstraksi Relasi** masuk ke dalam **Knowledge Graph**; **metrik evaluasi (Precision/Recall/F1)** dipertahankan sebagai subbab 2.6 (struktur jadi 6 subbab termasuk Penelitian Terdahulu, sesuai permintaan).
> Subbab utama tetap 6 (ramping), tetapi tiap **pilar gabungan dipecah jadi anak subbab (2.x.y)** agar konsep yang dilebur tetap tertata: 2.2 (2.2.1 Sirah, 2.2.2 OCR), 2.3 (2.3.1 NER, 2.3.2 SRL, 2.3.3 Self-Training/BERT), 2.4 (2.4.1 KG, 2.4.2 Ekstraksi Relasi, 2.4.3 Neo4j/Cypher), 2.6 (2.6.1 Evaluasi NER, 2.6.2 Evaluasi KG). 2.1 dan 2.5 tetap utuh tanpa anak subbab.
> Tiga perubahan isi dari proposal: **LLM-Based NER dihapus** (fokus SRL); **Iterative Self-Training/BERT** dan **Social Network Analysis** ditambahkan; **Ariyanto et al. (2025)** masuk ke 2.1.
> Patuh pedoman: tanpa em dash, layman, istilah asing *italic*, sitasi APA. Sumber wajib 2020-2026.
> Tanda **[DARI PROPOSAL]** = isi/sitasi sudah ada di proposal, tinggal salin teks lengkapnya. **[BARU]** = konten baru. **[PERIKSA]** = perlu konfirmasi. **[OPSI 4 SUBBAB]** = cara meramping jadi 4 subbab bila diminta.

Bab ini terdiri dari dua bagian. Bagian pertama (2.1) meninjau penelitian terdahulu yang relevan dengan pembangunan *knowledge graph* dari teks, ekstraksi entitas dengan NER, dan pembelajaran semi-*supervised* pada bahasa dengan sumber berlabel terbatas. Bagian kedua (2.2 sampai 2.6) menguraikan dasar teori yang menjadi landasan penelitian, yaitu Sirah Nabawiyah sebagai sumber data, *Named-Entity Recognition* berbasis SRL dengan *iterative self-training*, *knowledge graph* dan Neo4j, *Social Network Analysis*, serta metrik evaluasi.

## 2.1 Hasil Penelitian Terdahulu

> **[DARI PROPOSAL]** Narasi 10 penelitian sudah lengkap di proposal. Salin apa adanya, lalu **tambahkan** paragraf Ariyanto et al. (2025) dan revisi paragraf penutup. Tabel 2.1 sudah memuat 10 penelitian proposal + baris Ariyanto et al. (2025).

Penelitian ini berada pada irisan tiga topik, yaitu pembangunan *knowledge graph* (*knowledge graph construction*), ekstraksi informasi melalui NER dan ekstraksi relasi, serta pemanfaatan *graph database* seperti Neo4j untuk penyimpanan dan penelusuran pengetahuan berbasis relasi. Penelitian terdahulu berikut menjadi landasan untuk memahami tahapan umum konstruksi *knowledge graph*, pendekatan yang lazim diterapkan, serta bentuk evaluasi yang biasa digunakan. Ringkasan perbandingannya ditunjukkan pada Tabel 2.1.

[SISIPKAN TABEL 2.1 - Ringkasan Penelitian Terdahulu]

| Penelitian | Sumber Data | Metode | Relevansi terhadap Penelitian Ini |
|---|---|---|---|
| Zhong et al. (2024) | Survei >300 metode KGC | Review sistematis; tahap *acquisition*, *refinement*, *evolution* | Acuan tahapan pipeline konstruksi KG. |
| Ren et al. (2024) | Data heterogen siklus hidup produk | Pemodelan *function-behavior-structure*; ontologi | Pentingnya perancangan skema sebelum membangun graf. |
| Díaz et al. (2024) | Dokumen historis + *gold standard* | LLM; *grounding* ontologi; evaluasi vs *gold standard* | Relevan untuk domain historis. |
| Schäfer et al. (2024) | Literatur biomedis (PubMed IDs) | NER+NEL; normalisasi UMLS; KG hierarkis | Contoh evaluasi berbasis metrik (F1 sampai 0,6). |
| Xie et al. (2023) | 3152 dokumen Dao Yin | BERT-CRF + *proofreading*; Neo4j dan Cypher | Pipeline praktis NER ke relasi ke Neo4j. |
| He et al. (2022) | Intelijen militer multi-sumber | Penyatuan dan fusi semantik; Neo4j dan MongoDB | Referensi fusi/penyelarasan pengetahuan. |
| Nados (2024) | Dataset hadis (Arab), 8 tipe entitas | BIO tagging; AraBERT vs LSTM vs hibrida | Bukti NER efektif pada teks Islam; perlu adaptasi bahasa. |
| Chaudhary et al. (2024) | Artikel berita | *Entity linking* + *relation extraction*; Neo4j | Mendukung pipeline terpadu pembentukan graf. |
| Graciotti (2023) | Korpus historis (*Musical Heritage*) | *Semantic Web* + NLP; menangani *noise* OCR | Tantangan teks historis yang juga ada pada Sirah. |
| Du (2023) | Surat kabar periode Yan'an | *Information extraction* + *knowledge fusion*; visualisasi | Bukti KG efektif untuk korpus historis besar. |
| **Ariyanto et al. (2025)** [BARU] | Teks Twitter krisis (*low-resource*) | SRL berbasis *Transformer* + *iterative self-training* | **Sumber utama metode ekstraksi penelitian ini.** |

<!-- [PERIKSA] Judul penelitian ke-10 di proposal tertulis "Yifan (2023)" tetapi sitasinya "(Du, 2023)". Samakan satu nama. Tabel ini versi ringkas; kolom relevansi versi panjang ada di proposal. -->

**[BARU] Paragraf Ariyanto et al. (2025), sisipkan setelah Du (2023):** Penelitian oleh Ariyanto et al. (2025) menerapkan *Semantic Role Labeling* berbasis *Transformer* dengan strategi *iterative self-training* untuk teks krisis pada bahasa dengan sumber berlabel terbatas. Pada strategi ini, model dilatih dengan sedikit data berlabel, lalu dipakai untuk menebak label pada data yang belum berlabel, dan hanya tebakan dengan keyakinan tinggi yang dipakai untuk melatih ulang model secara bertahap. Penelitian ini menjadi rujukan metodologi utama pada penelitian Tugas Akhir ini, karena teks Sirah berbahasa Indonesia juga tergolong data dengan sumber berlabel terbatas. Perbedaannya, Ariyanto et al. (2025) menggunakan data Twitter, sedangkan penelitian ini menerapkannya pada teks naratif Sirah yang panjang dan tersusun kronologis.

**[BARU/REVISI] Paragraf penutup 2.1:** Berdasarkan penelitian terdahulu, terlihat bahwa konstruksi *knowledge graph* umumnya memerlukan ekstraksi entitas dan relasi, pemodelan skema, serta penyimpanan graf (seringnya Neo4j) agar pengetahuan dapat ditelusuri melalui kueri graf. Namun, sebagian besar studi berfokus pada domain berita, biomedis, militer, atau arsip sejarah tertentu, dan belum ada yang secara spesifik membangun *knowledge graph* untuk Sirah Nabawiyah berbahasa Indonesia dengan label minimal *Person*, *Event*, *Location*, dan *Time*. Selain itu, ekstraksi berbasis SRL semi-*supervised* yang hemat data (Ariyanto et al., 2025) belum pernah dipadukan dengan konstruksi KG Sirah, dan analisis jaringan (*Social Network Analysis*) terhadap KG sejarah Islam belum disentuh oleh penelitian yang ditinjau. Penelitian ini menutup celah tersebut.

## 2.2 Sirah Nabawiyah

> **[DARI PROPOSAL 2.2.1]** Salin teks proposal. Sitasi: Solihin (2022), Kharis (2024), Prayogi et al. (2022), Abror & Rahma (2024). **Paragraf OCR di bawah adalah hasil peleburan subbab OCR proposal ke sini** (sitasi OCR: Kushavaha 2024, Francis & Sangeetha 2025, Song 2026, Viana da Silva et al. 2023).
> <!-- [PERIKSA] Kunci sitasi Sirah di Bab 1 (Pratama/Kusumah) berbeda dari proposal 2.2.1 (Solihin/Kharis/Prayogi/Abror & Rahma). Samakan agar konsisten. -->

### 2.2.1 Sirah Nabawiyah

Sirah Nabawiyah merupakan narasi historis yang merekam perjalanan hidup Nabi Muhammad SAW beserta konteks sosial dan peristiwa yang menyertainya (Solihin, 2022). Dalam tradisi keilmuan Islam, Sirah memiliki keterkaitan erat dengan hadis dan menjadi rujukan penting dalam kajian keislaman (Kharis, 2024). Karya klasik seperti Sirah Ibn Ishaq yang disempurnakan Ibn Hisham menunjukkan upaya sistematis menuturkan kehidupan Nabi secara runtut (Prayogi et al., 2022), dan kajian modern menempatkan karya-karya tersebut sebagai fondasi sekaligus mengkajinya melalui analisis metode penulisan dan studi komparatif (Abror & Rahma, 2024).

Dari sisi bentuk teks, Sirah umumnya disajikan sebagai narasi kronologis dengan unit faktual seperti tokoh, peristiwa, lokasi, dan waktu yang hubungan antarunitnya sering tersirat dalam struktur kalimat. Pada penelitian ini, sumber data adalah buku *Sirah Nabawiyah* karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan Kathur Suhardi), berjumlah sekitar 633 halaman dalam Bahasa Indonesia. <!-- [PERIKSA] cocokkan judul, penerjemah, dan jumlah halaman dengan sampul buku. --> Satu tokoh dapat memiliki banyak variasi penyebutan (misalnya "Muhammad", "Rasulullah", "Nabi SAW"), dan entitas *Person* juga mencakup nama kabilah atau Bani, sehingga diperlukan penyatuan nama agar tidak terhitung sebagai entitas berbeda.

### 2.2.2 Optical Character Recognition

Karena buku sumber berupa hasil pemindaian, teks digital diperoleh melalui *Optical Character Recognition* (OCR), yaitu proses mengubah dokumen citra menjadi teks yang dapat diolah komputer (Kushavaha, 2024). Keluaran OCR sering mengandung *noise* seperti salah karakter, spasi tidak konsisten, dan artefak *header-footer* (Francis & Sangeetha, 2025) yang dapat menurunkan performa tugas yang sensitif pada batas token dan entitas seperti NER (Song, 2026), sehingga umumnya diperlukan pembersihan atau pasca-pemrosesan keluaran OCR (Viana da Silva et al., 2023).

## 2.3 Named-Entity Recognition berbasis SRL dengan Iterative Self-Training

> **[GABUNGAN]** Pilar metode ekstraksi. Isi dari proposal 2.2.3 (NER) + 2.2.3.1 (SRL), ditambah konten **[BARU]** Iterative Self-Training/BERT (pengganti LLM-Based NER yang dihapus). Sitasi NER: Li et al. (2022), Xu et al. (2024), Zhao et al. (2024). Sitasi SRL: Jindal et al. (2022), Santana et al. (2023), Alam et al. (2021).

### 2.3.1 Named-Entity Recognition

*Named-Entity Recognition* (NER) adalah tugas dalam NLP untuk mengenali potongan teks (*span*) yang menyebut entitas bernama dan mengklasifikasikannya ke kategori semantik yang telah ditentukan (Li et al., 2022). NER menjadi fondasi bagi tugas lanjutan seperti ekstraksi relasi dan konstruksi *knowledge graph* (Xu et al., 2024; Zhao et al., 2024). Pada penelitian ini digunakan empat label, yaitu *Person*, *Event*, *Location*, dan *Time*, dengan contoh daftar label ditunjukkan pada Tabel 2.2 dan contoh penerapan NER pada Gambar 2.1.

[SISIPKAN TABEL 2.2 - Contoh Daftar Label NER]
[SISIPKAN GAMBAR 2.1 - Contoh Hasil Penerapan NER pada Teks] <!-- [PERIKSA] Gambar 2.1 di proposal bersumber (Vyas, 2018), berumur >5 tahun. Ganti dengan contoh NER buatan sendiri atau sumber 2020+, atau konfirmasi gambar ilustratif boleh seminal. -->

Secara umum, NER diformulasikan sebagai *sequence labeling* menggunakan skema seperti BIO/IOB untuk menandai awal dan kelanjutan entitas pada tingkat token. Pendekatan modern berbasis representasi kontekstual (*Transformer*) unggul karena mampu membedakan entitas berdasarkan konteks kalimat, terutama pada teks naratif yang memiliki ambiguitas rujukan dan variasi bentuk penyebutan.

### 2.3.2 Semantic Role Labeling

Penelitian ini membangun kandidat entitas menggunakan *Semantic Role Labeling* (SRL), yaitu teknik *semantic parsing* tingkat dangkal yang merepresentasikan makna kalimat dalam bentuk struktur predikat-argumen, sehingga informasi inti seperti "siapa melakukan apa, kepada siapa, kapan, dan di mana" dapat diidentifikasi secara eksplisit (Jindal et al., 2022). Dalam SRL, predikat menjadi pusat kejadian, sedangkan argumen dan keterangan dilabeli sesuai perannya (Santana et al., 2023). Peran-peran ini dipetakan menjadi kandidat entitas, yaitu pelaku menjadi kandidat *Person*, keterangan lokasi menjadi *Location*, keterangan waktu menjadi *Time*, dan predikat beserta argumennya menandai *Event*. Strategi memanfaatkan keluaran SRL untuk membentuk struktur graf ini sejalan dengan penelitian yang menunjukkan keluaran SRL dapat diformalisasi menjadi representasi graf berbasis peran dan peristiwa (Alam et al., 2021).

### 2.3.3 Iterative Self-Training berbasis BERT

Model klasifikasi entitas yang dipakai berbasis BERT (*Bidirectional Encoder Representations from Transformers*), yaitu model bahasa berarsitektur *Transformer* yang telah dilatih awal (*pretrained*) pada teks besar dan mampu memahami makna kata berdasarkan konteksnya. Karena data berbahasa Indonesia, digunakan varian IndoBERT (Koto et al., 2020). [SITASI: Koto et al. (2020), IndoLEM and IndoBERT, COLING.] <!-- [PERIKSA] notebook S1/S2/S3 memakai indolem/indobert-base-uncased (uncased). --> Karena data berlabel terbatas, model dilatih dengan strategi semi-*supervised* berupa *iterative self-training* (Ariyanto et al., 2025): model mula-mula dilatih dengan sedikit data berlabel awal (*seed*), lalu dipakai untuk menebak label pada data tak berlabel, dan hanya tebakan dengan keyakinan tinggi yang ditambahkan sebagai label semu (*pseudo-label*) untuk melatih ulang model, diulang beberapa iterasi sampai kinerja stabil.

Untuk mengatasi ketidakseimbangan jumlah data antar kelas (entitas *Event* dan *Time* jauh lebih sedikit dibanding *Person* dan *Location*), penelitian ini juga mengeksplorasi *supervised contrastive learning*, yaitu teknik agar representasi entitas sekelas saling mendekat dan antar-kelas saling menjauh (Khosla et al., 2020), serta *data augmentation* dengan penggantian sebutan entitas (*mention replacement*). Rincian skenario dan hasilnya dibahas pada Bab 3 dan Bab 4. Hasil NER dievaluasi menggunakan *Precision*, *Recall*, dan *F1-score* pada tingkat entitas (*entity-level*); definisi metrik selengkapnya diuraikan pada subbab 2.6.

## 2.4 Knowledge Graph dan Neo4j

> **[GABUNGAN]** Pilar representasi. Isi dari proposal 2.2.4 (KG) + 2.2.5 (Neo4j) + 2.2.6 (Ekstraksi Relasi). Sitasi KG: Ji et al. (2021), Chen et al. (2023), Cai et al. (2022). Neo4j: Neo4j (n.d.-a sampai n.d.-d). Ekstraksi relasi: Yang et al. (2022), Diaz-Garcia & Lopez (2025), Zhou et al. (2022), Li et al. (2023). Gambar 2.2 (Ji et al., 2021) + Gambar 2.3 (Chaudhary et al., 2024).

### 2.4.1 Knowledge Graph

*Knowledge graph* (KG) adalah representasi pengetahuan berbasis graf yang memodelkan entitas beserta relasi di antaranya, sehingga informasi tidak hanya tersimpan sebagai narasi tetapi menjadi struktur yang dapat ditelusuri secara relasional (Ji et al., 2021). KG umumnya dipahami sebagai graf yang merekam fakta dalam bentuk *triple* *head-relation-tail* (Chen et al., 2023), sebagaimana ditunjukkan pada Gambar 2.2. Karena KG sering tidak lengkap, penelitian tentang *knowledge graph completion* berkembang untuk melengkapi fakta yang hilang (Cai et al., 2022). Pada penelitian ini, KG Sirah dibangun dengan empat jenis simpul (*Person*, *Event*, *Location*, *Time*) dan relasi inti `INVOLVED_IN`, `OCCURRED_AT`, dan `OCCURRED_ON`.

[SISIPKAN GAMBAR 2.2 - Contoh Entitas dan Relasi dalam Knowledge Graph (Ji et al., 2021)]

### 2.4.2 Ekstraksi Relasi

Relasi antar simpul dibentuk melalui ekstraksi relasi (*relation extraction*), yaitu proses mengidentifikasi hubungan semantik antara dua unit informasi di dalam teks, umumnya dilakukan setelah entitas dikenali oleh NER (Yang et al., 2022; Diaz-Garcia & Lopez, 2025). Metode ekstraksi relasi mencakup pendekatan *supervised/neural*, *pattern-based/rule-based*, dan *Open Information Extraction* (Zhou et al., 2022). Pada teks naratif panjang, relasi sering bersifat implisit dan berjarak lintas kalimat, sehingga ekstraksinya lebih menantang dan kadang memerlukan penalaran konteks dokumen (Li et al., 2023).

### 2.4.3 Neo4j dan Cypher

*Knowledge graph* tersebut disimpan menggunakan Neo4j, yaitu *graph database* yang menyimpan data dalam bentuk *property graph*, yaitu graf yang terdiri dari *node* dan *relationship* yang keduanya dapat memiliki atribut (Neo4j, n.d.-a). Neo4j menyediakan bahasa kueri *Cypher* yang mendukung *pattern matching* untuk menelusuri relasi pada graf (Neo4j, n.d.-b), contohnya ditunjukkan pada Gambar 2.3. Neo4j juga mendukung transaksi dengan properti ACID serta *constraints* dan *indexes* untuk menjaga integritas dan mempercepat kueri (Neo4j, n.d.-c; Neo4j, n.d.-d). Kualitas *knowledge graph* yang terbangun dapat dinilai melalui dimensi seperti akurasi, kelengkapan, dan konsistensi (Xue & Zou, 2022).

[SISIPKAN GAMBAR 2.3 - Contoh Implementasi Neo4j (Chaudhary et al., 2024)]

## 2.5 Social Network Analysis

> **[BARU]** Pilar analisis. Sitasi sudah TERVERIFIKASI (OpenAlex, 2020+): Elmezain et al. (2021) untuk sentralitas, Zhang et al. (2021) untuk PageRank, Anuar et al. (2024) untuk Louvain.

*Social Network Analysis* (SNA) adalah analisis untuk memahami struktur sebuah jaringan, yaitu mengukur peran tiap *node* dan pola hubungan di dalamnya. Pada penelitian ini, SNA diterapkan pada *knowledge graph* yang terbentuk, terutama pada jaringan antar tokoh (*Person*) yang terhubung melalui keterlibatan bersama pada peristiwa yang sama, untuk mengetahui tokoh dan peristiwa yang paling berperan dalam narasi Sirah.

Analisis tingkat *node* dilakukan dengan ukuran sentralitas (*centrality*), yang menjadi indikator penting kedudukan sebuah simpul dalam jaringan (Elmezain et al., 2021). Penelitian ini menggunakan empat ukuran. *Degree centrality* mengukur banyaknya hubungan langsung sebuah *node*. *Betweenness centrality* mengukur seberapa sering sebuah *node* menjadi jembatan pada jalur terpendek antar *node* lain. *Closeness centrality* mengukur seberapa dekat sebuah *node* terhadap semua *node* lain. *PageRank* mengukur kepentingan sebuah *node* berdasarkan seberapa banyak dan seberapa penting *node* lain yang terhubung dengannya, dengan memperhitungkan arah dan bobot hubungan (Zhang et al., 2021).

Selain tingkat *node*, dilakukan analisis tingkat graf seperti kepadatan (*density*), koefisien pengelompokan (*clustering coefficient* atau *transitivity*), ukuran jaringan, dan jumlah komponen. Penelitian ini juga melakukan deteksi komunitas (*community detection*), yaitu pengelompokan *node* yang lebih rapat terhubung di dalam kelompok dibanding antar kelompok, menggunakan algoritme Louvain dengan kualitas pembagian diukur oleh nilai modularitas (*modularity*, dilambangkan Q) (Anuar et al., 2024). Hasil SNA digunakan untuk menafsirkan struktur sosial dalam narasi Sirah, misalnya mengidentifikasi tokoh sentral dan kelompok tokoh yang sering muncul bersama.

## 2.6 Evaluasi

> **[DARI PROPOSAL 2.2.7]** Salin teks proposal (Precision/Recall/F1 + Persamaan 2.1-2.3 + evaluasi graf). Sitasi: Zhao et al. (2024); untuk NER: Lian et al. (2024), Zeynali Tazehkandi & Nowkarizi (2020), Powers (2020), Ding et al. (2025), Effland & Collins (2021), Ehrmann et al. (2024), Liu et al. (2025); untuk graf: Anuyah et al. (2024), Choi & Jung (2025), He et al. (2022), Xie et al. (2023), Díaz et al. (2024). **[REVISI]** Ganti Paulheim (2017, >5 tahun) dengan Xue & Zou (2022) untuk evaluasi kualitas KG.

Evaluasi pada penelitian ini mencakup dua aspek, yaitu evaluasi hasil NER dan evaluasi struktur *knowledge graph* (Zhao et al., 2024).

### 2.6.1 Evaluasi Hasil NER

Kualitas hasil NER diukur menggunakan *Precision*, *Recall*, dan *F1-score* yang dihitung dari tiga besaran dasar, yaitu *True Positive* (TP, entitas yang benar dikenali), *False Positive* (FP, teks yang salah dikenali sebagai entitas atau salah kategori), dan *False Negative* (FN, entitas yang seharusnya dikenali tetapi terlewat). *Precision* mengukur ketepatan, yaitu dari semua entitas yang ditebak model, berapa proporsi yang benar (Lian et al., 2024). *Recall* mengukur kelengkapan, yaitu dari semua entitas yang seharusnya ada, berapa proporsi yang berhasil ditemukan (Zeynali Tazehkandi & Nowkarizi, 2020). *F1-score* adalah rata-rata harmonik dari keduanya, yang lebih representatif pada data dengan kelas tidak seimbang (Powers, 2020). Rumus ketiganya ditunjukkan pada Persamaan 2.1 sampai 2.3.

Precision = TP / (TP + FP)   ... (2.1)

Recall = TP / (TP + FN)   ... (2.2)

F1-score = 2 × (Precision × Recall) / (Precision + Recall)   ... (2.3)

Karena entitas dapat terdiri dari beberapa kata, evaluasi dilakukan pada tingkat entitas (*entity-level*), yaitu sebuah entitas dianggap benar hanya jika seluruh rentang kata dan kategorinya tepat. Selain F1 per kelas, dilaporkan *macro-average* (rata-rata antar kelas dengan bobot sama, sehingga kelas minoritas *Event* dan *Time* terwakili) dan *micro-average* (gabungan seluruh entitas). Evaluasi terhadap data acuan (*ground truth*) sebagian lazim pada domain historis atau naratif panjang karena anotasi penuh berbiaya besar (Ding et al., 2025; Effland & Collins, 2021; Ehrmann et al., 2024; Liu et al., 2025).

### 2.6.2 Evaluasi Knowledge Graph

Evaluasi struktur *knowledge graph* dilakukan secara fungsional berbasis skenario kueri *Cypher* yang mewakili kebutuhan penelusuran relasional, lalu dinilai secara kualitatif-deskriptif berdasarkan ketercapaian hasil kueri, konsistensi hubungan, dan keterlacakan (*traceability*) ke teks sumber (He et al., 2022; Xie et al., 2023; Díaz et al., 2024; Anuyah et al., 2024; Choi & Jung, 2025). Kualitas graf juga dapat ditinjau dari dimensi seperti akurasi, kelengkapan, dan konsistensi (Xue & Zou, 2022). Selain evaluasi fungsional tersebut, struktur graf dianalisis secara kuantitatif menggunakan *Social Network Analysis* (subbab 2.5).

---

> **[CATATAN PENYUSUN] Ringkasan rekonsiliasi + audit kebaruan sumber (cutoff 2020-2026):**
>
> **Peleburan struktur (granular proposal → pilar buku):**
> - OCR (proposal 2.2.2) → dilebur ke **2.2 Sirah** (paragraf OCR).
> - SRL (2.2.3.1) + Iterative Self-Training/BERT (baru) → dilebur ke **2.3 NER**.
> - Neo4j (2.2.5) + Ekstraksi Relasi (2.2.6) → dilebur ke **2.4 Knowledge Graph**.
> - Evaluasi/metrik (2.2.7) → **dipertahankan sebagai subbab 2.6 Evaluasi** (total 6 subbab termasuk Penelitian Terdahulu, sesuai permintaan user).
> - LLM-Based NER (2.2.3.2) + Gambar PromptNER → **dihapus**.
>
> **[OPSI 4 SUBBAB]** Bila ingin persis 4 subbab seperti teman: lebur **2.2 Sirah** ke pengantar 2.1 / latar belakang Bab 1 (Sirah sudah dibahas di Bab 1), sehingga tersisa 2.1 Penelitian Terdahulu, 2.2 NER, 2.3 Knowledge Graph, 2.4 SNA. Risiko: konteks domain dan OCR jadi minim di Bab 2; rekomendasi tetap 5 subbab.
>
> **Sitasi pre-2020 yang sudah diatasi (anchor 2020+ terverifikasi OpenAlex):**
> - IndoBERT → **Koto, F., Rahimi, A., Lau, J. H., & Baldwin, T. (2020).** *IndoLEM and IndoBERT.* COLING 2020, 757-770.
> - Eval NER/seqeval → **Ehrmann et al. (2024)** (sudah di proposal).
> - KG quality → **Xue, B., & Zou, L. (2022).** IEEE TKDE. DOI 10.1109/TKDE.2022.3150080.
> - Louvain → **Anuar, S. H. H., et al. (2024).** Pertanika J. Sci. & Technol. 32(3), 1285-1300. DOI 10.47836/pjst.32.3.16.
> - PageRank → **Zhang, P., Wang, T., & Yan, J. (2021).** Physica A, 586, 126438. DOI 10.1016/j.physa.2021.126438.
> - Centrality → **Elmezain, M., Othman, E. A., & Ibrahim, H. M. (2021).** Mathematics, 9(22), 2850. DOI 10.3390/math9222850.
> - BERT (Devlin 2019) → tidak perlu disitasi langsung; klaim disandarkan ke Koto et al. (2020) + Ariyanto et al. (2025).
>
> **Masih perlu perhatian:** Vyas (2018, Gambar 2.1) >5 tahun (ganti gambar/sumber); kunci sitasi Sirah Bab 1 vs Bab 2 perlu disamakan; nama penulis #10 (Yifan vs Du). Sumber lain mayoritas 2021-2026 (aman). **Verifikasi tiap entri sebelum masuk `pustaka.bib`; jangan mengarang.**
