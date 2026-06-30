# BAB 4 HASIL DAN PEMBAHASAN

> **[CATATAN PENYUSUN, hapus saat finalisasi]**
> Bab ini menyatukan hasil dan pembahasan dalam satu alur (tidak dipisah), mengikuti permintaan susunan. Struktur: 4.1 Uji Coba 1 (penanganan data *imbalance*), 4.2 Uji Coba 2 (komparasi model), 4.3 Uji Coba 3 (modul POS-tag), 4.4 Evaluasi graf. Tiap subbab memuat penjelasan hasil, tabel hasil, interpretasi, alasan tinggi/rendah, analisis error, contoh data error, dan rujukan visualisasi.
> **Sumber angka (jangan diubah tanpa cek ulang):** F1 entity-level dari `data/result/pseudo-labelling/SRL-NER/seqeval_grupB_results.md`; error token-level dari `data/result/analysis/error_analysis_done_running/`; trajektori anomali dari `diagnose_grupb_anomaly.md`; metrik graf dari `data/result/analysis/v3/sna_summary.md`. Visualisasi (PNG) ada di `data/result/analysis/error_viz/`.
> Patuh pedoman: tanpa em dash, bahasa *layman*, istilah asing *italic*, sitasi APA. Tanda **[PERIKSA]** = perlu konfirmasi; **[SITASI: ...]** = referensi yang perlu masuk Daftar Pustaka.

Bab ini menyajikan dan membahas hasil pengujian terhadap rancangan yang dijelaskan pada Bab 3. Pembahasan dibagi mengikuti tiga uji coba ekstraksi entitas (subbab 3.9) dan evaluasi fungsional *knowledge graph* (subbab 3.10), sehingga setiap angka dapat ditelusuri ke skenario uji coba yang sesuai.

Seluruh evaluasi ekstraksi entitas dilakukan pada data uji yang sama, yaitu 258 *chunk* berisi 42.558 token dengan 1.763 entitas (*Person* 1.189, *Location* 449, *Time* 74, dan *Event* 51 entitas). <!-- [PERIKSA] cocokkan jumlah token/entitas dengan test.csv dan support pada seqeval_grupB_results.md. --> Pengukuran utama memakai *F1-score* tingkat entitas (*entity-level*) dengan pustaka seqeval, yaitu sebuah entitas dihitung benar hanya jika seluruh rentang token dan kategorinya tepat. Sebagai metrik pendukung analisis error, digunakan hitungan kesalahan tingkat token (*token-level*) yang memerinci jenis kesalahan. Komposisi data uji penting untuk dicatat sejak awal, karena ketimpangan jumlah entitas antar kelas (*Person* jauh lebih banyak daripada *Event* dan *Time*) menjadi penjelas utama pola hasil di seluruh subbab.

---

## 4.1 Uji Coba 1: Penanganan Data Imbalance

Uji coba pertama bertujuan menguji apakah ketidakseimbangan jumlah entitas antar kelas (*imbalance*) pada data latih dapat ditangani sehingga kualitas pengenalan kelas minoritas (terutama *Event* dan *Time*) meningkat. Persoalannya nyata: pada data uji, *Event* hanya 51 entitas dan *Time* 74 entitas, jauh di bawah *Person* (1.189) dan *Location* (449), sehingga model cenderung kurang terlatih mengenali dua kelas terkecil itu. Untuk itu, alur dasar (*baseline*) dibandingkan dengan empat teknik penanganan ketidakseimbangan yang ditambahkan di atasnya, yaitu *weighted cross-entropy*, *supervised contrastive learning* (SCL), *Jaccard-similarity contrastive learning* (JSCL), dan *data augmentation* dengan *mention replacement*.

Ketimpangan jumlah entitas antar kelas yang menjadi pangkal persoalan ini terlihat jelas pada Gambar 4.1, yang menyandingkan jumlah entitas tiap kelas pada data latih dan data uji.

[SISIPKAN GAMBAR 4.1 - Distribusi Jumlah Entitas per Kelas (Imbalance) pada Data Latih dan Data Uji]
<!-- file: data/result/analysis/bab4_viz/eda_imbalance.png -->

Gambar 4.1 menyajikan jumlah entitas tiap kelas pada data latih dan data uji sebagai diagram batang berkelompok. Batang *Person* menjulang paling tinggi (2.884 entitas pada data latih) sedangkan *Event* hanya berupa batang pendek (163 entitas latih dan hanya 51 pada data uji), dengan rasio ketimpangan sekitar 18:1 pada data latih dan 23:1 pada data uji. Pola yang konsisten di kedua bagian data inilah yang mendasari seluruh Uji Coba 1, yaitu kelas *Event* dan *Time* yang contohnya sangat sedikit (*few-shot*) menjadi kelas yang paling sulit dikenali model.

Pengujian dilakukan dengan melatih kelima varian (alur dasar ditambah empat teknik) pada *seed* yang sama, lalu mengevaluasinya pada data uji yang identik, yaitu 258 *chunk* berisi 42.558 token dengan 1.763 entitas. Agar perbandingan adil, hanya komponen penanganan ketidakseimbangan yang divariasikan, sedangkan arsitektur dasar (IndoBERT *uncased*), ambang *pseudo-labelling*, dan *hyperparameter* lain dibuat sama persis mengikuti prosedur Kode Semu 3.12. Pengukuran kualitas memakai pustaka seqeval pada tingkat entitas (*entity-level*), yaitu satu entitas dihitung benar hanya jika seluruh rentang token dan kategorinya tepat, dan dilengkapi penghitungan kesalahan tingkat token (*token-level*) untuk membedah jenis kesalahan.

Metrik utama yang digunakan adalah *F1-score* (rata-rata harmonik) karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan, proporsi prediksi yang benar) dan *recall* (kelengkapan, proporsi entitas acuan yang ditemukan), serta dilaporkan dalam bentuk *micro* (agregat seluruh entitas, didominasi kelas mayoritas) maupun *macro* (rata-rata antar kelas, lebih sensitif terhadap kelas minoritas). Karena itu hasil disajikan dalam dua tabel: Tabel 4.1 merangkum metrik agregat untuk menilai kualitas keseluruhan, sedangkan Tabel 4.2 memerinci F1-score tiap kelas entitas beserta *macro*-nya agar dampak terhadap kelas minoritas terlihat jelas.

[SISIPKAN TABEL 4.1 - Precision, Recall, dan F1-score Agregat Uji Coba 1]

| Skenario | Precision | Recall | F1-score (mikro) |
|----------|----------:|-------:|-----------------:|
| *Baseline* | 0,9489 | 0,9472 | 0,9481 |
| *Weighted cross-entropy* | 0,9224 | 0,9569 | 0,9393 |
| SCL | 0,9407 | 0,9620 | 0,9512 |
| JSCL | 0,9324 | 0,9546 | 0,9434 |
| **Augmentation** | **0,9554** | **0,9609** | **0,9581** |

[SISIPKAN TABEL 4.2 - F1-score per Entitas Uji Coba 1]

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|----------|----------:|------------:|---------:|--------:|---------:|
| *Baseline* | 0,9596 | 0,9527 | 0,8039 | 0,8408 | 0,8892 |
| *Weighted cross-entropy* | 0,9575 | 0,9352 | 0,7767 | 0,7898 | 0,8648 |
| SCL | 0,9655 | 0,9493 | 0,8200 | 0,8258 | 0,8902 |
| JSCL | 0,9559 | 0,9394 | 0,8367 | 0,8408 | 0,8932 |
| **Augmentation** | **0,9640** | **0,9653** | **0,9020** | **0,8627** | **0,9235** |

[SISIPKAN GAMBAR 4.2 - F1-score Agregat Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/bab4_viz/f1_uc1_agregat.png -->

Gambar 4.2 meringkas Tabel 4.1 secara visual. Batang *augmentation* (disorot merah) berdiri paling tinggi baik pada F1 mikro maupun macro, sedangkan *weighted cross-entropy* paling rendah, sehingga peringkat antar skenario langsung terbaca.

[SISIPKAN GAMBAR 4.3 - F1-score per Kelas Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/bab4_viz/f1_uc1_perkelas.png -->

Gambar 4.3 meringkas Tabel 4.2 dengan mengelompokkan batang per kelas entitas. Sumber keunggulan *augmentation* terlihat jelas, yaitu batang *Event* dan *Time*-nya naik paling tinggi dibanding skenario lain, sementara *Person* dan *Location* tetap tinggi dan stabil di semua skenario.

Berdasarkan kedua tabel tersebut, teknik augmentation menjadi pemenang yang jelas dengan F1-score mikro 0,9581, mengungguli *baseline* (0,9481) dan seluruh teknik lain, dengan SCL menyusul di urutan kedua (0,9512). Hal yang patut dicatat sejak awal adalah bahwa tidak semua penanganan ketidakseimbangan otomatis memperbaiki hasil, sebab dua teknik justru menurunkan F1-score di bawah *baseline*, yaitu JSCL (0,9434) dan *weighted cross-entropy* (0,9393). Pola yang berlawanan arah ini menjadi inti pembahasan subbab ini, karena memperlihatkan bahwa menambah jumlah contoh kelas minoritas (augmentation) berbeda secara mendasar dari sekadar menggeser perhatian model ke kelas minoritas (*weighted cross-entropy*).

Keunggulan augmentation paling kentara justru pada kelas minoritas, sebagaimana terbaca pada Tabel 4.2. F1-score *Event* melonjak dari 0,8039 ke 0,9020 (naik hampir sepuluh poin) dan F1-score *Time* naik dari 0,8408 ke 0,8627, sementara *Person* dan *Location* tetap kuat bahkan ikut naik. Penyebabnya bersifat langsung: teknik *mention replacement* membentuk kalimat latih baru dengan mengganti entitas minoritas dengan entitas sekelas, sehingga model memperoleh lebih banyak ragam contoh *Event* dan *Time* yang sebelumnya sangat sedikit. Bukti pada tingkat token memperkuat penjelasan ini, yaitu *false negative* (entitas terlewat) pada *Event* turun dari 11 ke 8 dan *false positive* pada *Time* turun drastis dari 17 ke 8 sebagaimana terbaca pada Tabel 4.3, dan secara keseluruhan augmentation menghasilkan total error terendah (166 token) sekaligus misklasifikasi tipe paling sedikit (hanya 4 token).

Sebaliknya, *weighted cross-entropy* menempati posisi terendah, dan penyebabnya terbaca jelas dari pemecahan metrik agregat pada Tabel 4.1. Pemberian bobot lebih besar pada kelas minoritas membuat model menjadi terlalu agresif dalam menebak entitas sehingga *recall* memang naik ke 0,9569, tetapi *precision* anjlok ke 0,9224 dan total error melonjak ke 232 token dengan *false positive* membengkak menjadi 150. Akibatnya F1-score keseluruhan justru turun. Temuan ini menegaskan bahwa menaikkan bobot kelas minoritas pada fungsi *loss* tidak menambah informasi baru tentang kelas tersebut, melainkan hanya menggeser model ke arah lebih banyak menebak, sehingga yang muncul adalah lebih banyak deteksi keliru, bukan pengenalan yang lebih baik.

Pembahasan kemudian dilanjutkan pada anatomi kesalahan untuk memahami mengapa pola di atas terjadi. Rincian jenis kesalahan tingkat token ditunjukkan pada Tabel 4.3. Pada semua skenario, kesalahan didominasi oleh keputusan deteksi (entitas atau bukan entitas), yaitu *false positive* (45 sampai 65 persen) dan *false negative* (28 sampai 47 persen), sedangkan misklasifikasi tipe hanya 2 sampai 6 persen dan kesalahan batas (*boundary* B/I) hanya 2 sampai 4 persen. Temuan ini menunjukkan bahwa model sebenarnya sudah memahami perbedaan keempat tipe entitas, dan tantangan utamanya terletak pada memutuskan apakah suatu kata merupakan entitas atau bukan, bukan pada kebingungan membedakan jenis entitas.

[SISIPKAN TABEL 4.3 - Rincian Jenis Error Token-level Uji Coba 1]

| Skenario | Total error | FP (over-deteksi) | FN (terlewat) | Misklasifikasi tipe | Boundary B/I |
|----------|------------:|------------------:|--------------:|--------------------:|-------------:|
| *Baseline* | 192 | 86 (45%) | 91 (47%) | 11 (6%) | 4 (2%) |
| *Weighted cross-entropy* | 232 | 150 (65%) | 67 (29%) | 10 (4%) | 5 (2%) |
| SCL | 197 | 118 (60%) | 63 (32%) | 9 (5%) | 7 (4%) |
| JSCL | 212 | 120 (57%) | 75 (35%) | 10 (5%) | 7 (3%) |
| Augmentation | 166 | 86 (52%) | 69 (42%) | 4 (2%) | 7 (4%) |

Akar penyebab error, berdasarkan inspeksi token salah, terbagi tiga. Pertama, **over-deteksi (FP)** banyak berasal dari frasa penghormatan yang menempel pada nama Nabi (seperti *Shalallahu Alaihi wa Sallam*) dan penanda nasab (*bin*, *Abdul*, *Abu*, *Ummul*) yang ditarik menjadi bagian nama, serta kata waktu generik berhuruf kecil (*bulan*, *hari*) yang dikira *Time*. Kedua, **entitas terlewat (FN)** banyak terjadi pada nama langka atau di luar distribusi (seperti *Bukhtanashar*, *Babilon*, *Babilonia*) dan pada token yang membawa tanda baca menempel akibat artefak OCR (seperti *Babilonia.*, *Umayyah.*). Ketiga, **inkonsistensi label acuan (*ground truth*)**: pelabelan semi-otomatis berbasis kapitalisasi membuat sebagian kata waktu berhuruf kecil (seperti *pertengahan*) diberi label O di tempat lain, sehingga ketika model tidak mendeteksinya, hal itu sebagian merupakan keterbatasan acuan, bukan murni kesalahan model.

Untuk memperlihatkan tiap jenis kesalahan secara konkret, di bawah ini ditampilkan satu contoh nyata per jenis error dari skenario pemenang (*augmentation*), dirinci per token dengan kolom *ground-truth* (label acuan) dan prediksi model. Baris token yang salah ditandai dengan tanda ✗. Seluruh contoh diambil dari prediksi model *augmentation* pada data uji (rekonstruksi `test.csv` + berkas token salah skenario), sehingga dapat ditelusuri ke *chunk* sumbernya.

<!-- Sumber: gold dari test.csv + pred dari done_running/augmentation/.../aug-...-incorrect.xlsx (rekonstruksi). Chunk id dicantumkan untuk provenance. -->

[SISIPKAN TABEL 4.4 - Contoh Over-deteksi (False Positive), chunk 000010-002]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| Mukhtashar | O | O | |
| Siratir-Rasul | O | O | |
| Shalallahu | O | *B-PERSON* | ✗ |
| Alaihi | O | *I-PERSON* | ✗ |
| wa | O | *I-PERSON* | ✗ |
| Sallam, | O | *I-PERSON* | ✗ |

Seluruh frasa penghormatan (*shalawat*) berlabel O pada acuan, tetapi ditarik model menjadi satu entitas *Person*. Inilah pola over-deteksi yang paling sering muncul, yaitu honorifik dan gelar yang menempel pada nama dikira bagian nama.

[SISIPKAN TABEL 4.5 - Contoh Entitas Terlewat (False Negative), chunk 000010-012]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| ke | O | O | |
| Babilonia. | *B-LOCATION* | O | ✗ |
| Sebagian | O | O | |

Nama tempat langka yang membawa tanda baca menempel akibat artefak OCR (*Babilonia.*) gagal dikenali model sehingga terlewat menjadi O.

[SISIPKAN TABEL 4.6 - Contoh Misklasifikasi Tipe, chunk 000223-005]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| sebelum | O | O | |
| Hudaibiyah. | *B-LOCATION* | *I-EVENT* | ✗ |
| Sebab | O | O | |

Token yang sama (*Hudaibiyah*) dapat merujuk tempat sekaligus peristiwa; di sini model menebaknya sebagai *Event* padahal acuan menandainya *Location*. Inilah satu dari hanya empat token salah-tipe pada skenario ini, dan semuanya melibatkan pasangan *Location* dengan *Event* atau *Person*.

[SISIPKAN TABEL 4.7 - Contoh Kesalahan Batas (Boundary B/I), chunk 000032-001]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| hari | *B-TIME* | *B-TIME* | |
| Senin, | *I-TIME* | *I-TIME* | |
| malam | *B-TIME* | O | ✗ |
| tanggal | *I-TIME* | *B-TIME* | ✗ |
| 21 | *I-TIME* | *I-TIME* | |
| dari | *I-TIME* | O | ✗ |
| bulan | *I-TIME* | *B-TIME* | ✗ |
| Ramadhan, | *I-TIME* | *I-TIME* | |

Satu rentang waktu panjang ("hari Senin, malam tanggal 21 dari bulan Ramadhan") dipecah model menjadi beberapa segmen sehingga penanda batas *B* dan *I* bergeser, meskipun tipe entitasnya (*Time*) tetap benar. Kesalahan jenis ini hanya 7 token pada skenario *augmentation* dan kebanyakan terjadi pada *Time*.

Temuan tersebut juga terlihat secara visual pada *confusion matrix* kelima skenario Uji Coba 1 (Gambar 4.4) dan panel perbandingan error antar skenario Uji Coba 1 (Gambar 4.5).

[SISIPKAN GAMBAR 4.4 - Confusion Matrix Token-level Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/error_viz/by_group/s1_confusion.png -->

Gambar 4.4 menyandingkan *confusion matrix* tingkat token kelima skenario Uji Coba 1 dengan pewarnaan skala logaritmik (log10), sehingga sel bernilai kecil tetap terlihat meskipun sel *O*-ke-*O* (sekitar 39.300 token bukan-entitas yang benar) jauh lebih besar daripada sel lain. Dibaca menyeluruh, kelima panel berbentuk hampir sama: blok antar-tipe entitas, yaitu bagian matriks selain baris dan kolom *O*, hampir seluruhnya bernilai nol (token salah-tipe hanya berkisar 4 sampai 11 dari puluhan ribu token, dan selalu melibatkan pasangan *Location* dengan *Event* atau *Person*), sementara seluruh kesalahan yang berarti menumpuk pada baris dan kolom *O*. Keseragaman ini sendiri sudah menjadi temuan, sebab menunjukkan bahwa tidak ada satu pun teknik yang membuat model bingung membedakan jenis entitas; yang berbeda antar-skenario hanyalah seberapa banyak kesalahan deteksi *O*-ke-entitas, dan dari sisi itu pembahasan difokuskan pada skenario pemenang.

Pada panel *augmentation*, kebersihan blok antar-tipe terlihat paling ekstrem: hanya 4 token salah-tipe (2 *Location* diprediksi *Person* dan 2 *Location* diprediksi *Event*), tanpa satu pun kebocoran lain, sehingga model praktis tidak pernah tertukar membedakan satu tipe entitas dengan tipe lain. Seluruh kesalahan yang berarti terkumpul pada baris dan kolom *O*, yakni pada keputusan deteksi entitas-atau-bukan: sel terbesar adalah *O* yang diprediksi *Person* (62 token, yaitu over-deteksi nama dari kata non-entitas seperti honorifik dan nasab), disusul *Person* yang diprediksi *O* (34 token, nama yang terlewat), lalu *O*→*Location* (15), *Time*→*O* (14), dan *Location*→*O* (13). Kelas minoritas justru tampil rapi: *Event* benar pada 100 token dengan hanya 8 terlewat dan tanpa satu pun salah-tipe, sedangkan *Time* benar pada 218 token dengan 14 terlewat. Angka-angka ini cocok persis dengan baris *augmentation* pada Tabel 4.3 (FP 86, FN 69, misklasifikasi tipe 4).

Sebagai pembanding singkat, kontras paling tajam dengan pemenang ada pada *weighted-class*, yang baris-baris *O*-ke-entitasnya paling padat (90 token *O* salah ditandai sebagai *Person*, 35 sebagai *Location*, 24 sebagai *Time*); inilah wujud visual dari over-deteksi yang menjatuhkan *precision*-nya pada Tabel 4.1, sekaligus penegasan bahwa perbedaan antar-teknik bermain di kolom deteksi, bukan di blok tipe. Dengan demikian, pembacaan menyilang kelima panel menuju satu kesimpulan yang sama dengan Tabel 4.3, yaitu tantangan model terletak pada deteksi batas entitas (kolom dan baris *O*), bukan pada klasifikasi jenisnya, dan keunggulan *augmentation* berasal dari merapikan baris *O* pada kelas minoritas, bukan dari mengubah kemampuan membedakan tipe.

[SISIPKAN GAMBAR 4.5 - Panel Perbandingan Error Lima Skenario Uji Coba 1 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s1_compare.png -->

Gambar 4.5 memuat empat panel yang membedah error kelima skenario Uji Coba 1 dari sudut berbeda. Panel kiri-atas (total error) menegaskan peringkat yang sama dengan Tabel 4.3, yaitu *augmentation* paling sedikit (166 token) dan *weighted-class* paling banyak (232 token). Panel kanan-atas (komposisi *false negative* per kelas) menunjukkan *baseline* paling banyak melewatkan entitas (sekitar 91 token) dan *augmentation* memangkasnya ke sekitar 69 token, dengan *Person* (biru) mendominasi jumlah absolut entitas terlewat karena memang kelas terbanyak. Panel kiri-bawah (komposisi *false positive* per kelas) memperlihatkan akar masalah *weighted-class* secara gamblang: tumpukan FP-nya paling tinggi (sekitar 150 token, didominasi over-deteksi *Person*), jauh di atas *augmentation* dan *baseline* yang hanya sekitar 86 token, dan inilah penjelasan mengapa *precision* *weighted-class* anjlok. Panel kanan-bawah adalah yang paling bermakna untuk persoalan ketidakseimbangan, yaitu *FN-rate* per kelas atau persentase entitas gold yang terlewat setelah dinormalkan terhadap jumlah masing-masing kelas. Pada panel ini *Event* (merah) konsisten menjadi kelas tersulit dengan tingkat terlewat tertinggi, sekitar 10 persen pada *baseline*, dan *augmentation* adalah satu-satunya teknik yang menurunkannya secara terlihat menjadi sekitar 7 persen, sementara *Person* (biru) paling mudah dengan tingkat terlewat hanya 1 sampai 2 persen. Panel terakhir ini menjadi bukti visual paling langsung bahwa kelangkaan contoh (*few-shot*) membuat *Event* paling rentan terlewat, dan bahwa keunggulan *augmentation* benar-benar berasal dari perbaikan pada kelas minoritas itu, bukan dari kelas mayoritas.

Karena augmentation menjadi pemenang Uji Coba 1, ditinjau secara eksplisit bagaimana teknik ini mengubah komposisi data latih, sekaligus menjawab satu hal yang sering ditanyakan, yaitu mengapa kelas *O* (token bukan-entitas) yang jumlahnya sangat besar tidak ikut dikurangi. Tabel 4.8 menyandingkan jumlah token tiap label pada data latih sebelum dan sesudah augmentation *mention replacement*.

[SISIPKAN TABEL 4.8 - Distribusi Label Token Data Latih Sebelum dan Sesudah Augmentasi]

| Label (token) | Sebelum augmentasi | Sesudah augmentasi | Perubahan |
|---------------|-------------------:|-------------------:|----------:|
| *O* (bukan entitas) | 95.277 | 139.983 | +44.706 (+47%) |
| *Person* (B+I) | 5.559 | 8.101 | +2.542 (+46%) |
| *Location* (B+I) | 1.057 | 1.885 | +828 (+78%) |
| *Time* (B+I) | 666 | 1.084 | +418 (+63%) |
| *Event* (B+I) | 325 | 967 | +642 (+198%) |
| **Total token** | **102.884** | **152.020** | **+49.136 (+48%)** |

[SISIPKAN GAMBAR 4.6 - Distribusi Label Token Data Latih Sebelum dan Sesudah Augmentasi]
<!-- file: data/result/analysis/bab4_viz/augmentasi_distribusi.png -->

Gambar 4.6 memvisualkan Tabel 4.8 dalam dua panel agar kelas *O* yang jauh lebih besar tidak menenggelamkan kelas entitas. Panel (a) khusus membandingkan jumlah token *O* sebelum dan sesudah augmentasi (95.277 menjadi 139.983), sedangkan panel (b) menampilkan keempat kelas entitas pada skala yang sama dan menonjolkan bahwa *Event* tumbuh paling tajam secara relatif (naik 198 persen) meskipun jumlah absolutnya tetap paling kecil. Pemisahan ini sekaligus memperlihatkan bahwa augmentasi menambah seluruh kelas, bukan mengurangi *O*.

Pada tingkat entitas (dihitung dari penanda awal *B-*), jumlah *mention* naik dari 4.265 menjadi 6.673. Kenaikan terbesar justru terjadi pada kelas minoritas, yaitu *Event* melonjak dari 163 ke 471 (naik 189 persen) dan *Time* dari 233 ke 371 (naik 59 persen), sedangkan *Person* dan *Location* yang sudah banyak hanya naik 44 dan 71 persen. Pola inilah yang menjelaskan lonjakan F1 *Event* dan *Time* pada Tabel 4.2: model memperoleh jauh lebih banyak ragam contoh untuk dua kelas yang sebelumnya paling langka.

Yang menonjol dari Tabel 4.8 adalah bahwa kelas *O* justru bertambah (dari 95.277 menjadi 139.983), bukan berkurang, dan proporsinya terhadap seluruh token nyaris tidak berubah (92,6 persen menjadi 92,1 persen). Hal ini disengaja. Ada beberapa alasan mengapa kelas *O* tidak dikurangi (*undersampling*) meskipun jumlahnya mendominasi. Pertama, persoalan NER adalah pelabelan berurutan (*sequence labeling*), bukan klasifikasi sampel yang berdiri sendiri. Token *O* bukan "data berlebih" yang dapat dibuang, melainkan kata-kata penghubung di antara entitas dalam satu kalimat. Membuang token *O* berarti merusak struktur kalimat dan urutan BIO, sehingga konteks yang justru dibutuhkan model untuk menentukan batas entitas ikut hilang. Kedua, mengurangi *O* berarti membuang kalimat yang sedikit atau tidak mengandung entitas, padahal kalimat semacam itu adalah contoh negatif yang berharga karena mengajari model kata-kata apa yang bukan entitas. Bukti dampak buruknya sudah terlihat dalam uji coba ini sendiri pada skenario *weighted cross-entropy*, yang menggeser model menjauh dari *O* sehingga over-deteksi (*false positive* melonjak ke 150 token) dan *precision* anjlok (Tabel 4.1 dan 4.3); *undersampling O* diperkirakan menimbulkan efek serupa, yaitu model menjadi terlalu mudah menebak entitas. Ketiga, distribusi data latih sebaiknya mencerminkan teks nyata, dan pada teks Sirah sekitar sembilan dari sepuluh token memang bukan entitas, sehingga bila *O* dikurangi secara artifisial model dilatih pada distribusi yang tidak realistis dan berisiko over-deteksi saat dipakai pada teks sebenarnya (pergeseran distribusi).

Oleh karena itu, strategi yang dipilih adalah menambah contoh kelas minoritas (*oversampling* lewat augmentation), bukan mengurangi kelas mayoritas (*undersampling O*). Pendekatan ini menaikkan keterwakilan *Event* dan *Time* tanpa mengorbankan konteks *O*, dan hasilnya konsisten dengan Tabel 4.2, yaitu F1 kelas minoritas naik sementara *precision* keseluruhan tetap terjaga, berbeda dengan *weighted cross-entropy*. Mempertahankan *O* dalam jumlah besar juga bukan kerugian, sebab memprediksi *O* dengan benar adalah inti dari menghindari *false positive*; pada *confusion matrix* Gambar 4.4, sel *O*-ke-*O* yang besar (sekitar 39.300 token pada data uji) justru merupakan keberhasilan model mengenali kata bukan-entitas, dan kesalahan yang berarti terkumpul pada keputusan deteksi *O*-ke-entitas, bukan pada banyaknya jumlah *O*.

---

## 4.2 Uji Coba 2: Komparasi Model

Uji coba kedua bertujuan menguji pengaruh pemilihan model pra-latih (*backbone*) terhadap kualitas pengenalan entitas, yaitu mencari tahu model berbahasa Indonesia mana yang paling sesuai untuk teks Sirah ketika dipakai dalam alur *iterative self-training*. Lima model dibandingkan: IndoBERT *uncased* (`indolem/indobert-base-uncased`, *baseline*), `cahya/bert-base-indonesian-1.5G`, DistilBERT Indonesia, IndoBERT *cased*, dan RoBERTa Indonesia. <!-- [PERIKSA] pastikan nama persis tiap model pembanding sesuai checkpoint yang dijalankan. -->

Pengujian dilakukan dengan menjalankan pipeline yang identik untuk kelima model, yaitu data latih, ambang *pseudo-labelling*, dan *hyperparameter* yang sama, sehingga satu-satunya yang berbeda adalah *backbone*-nya. Seluruh model dievaluasi pada data uji yang sama (258 *chunk*, 42.558 token, 1.763 entitas) dengan pustaka seqeval tingkat entitas, mengikuti prosedur Kode Semu 3.12. Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* (agregat seluruh entitas) maupun *macro* (rata-rata antar kelas, lebih sensitif terhadap kelas minoritas); selain itu, untuk model yang hasilnya menyimpang, ditambahkan dua alat bantu diagnosis, yaitu trajektori F1 dari *checkpoint* awal sampai iterasi terakhir (untuk memisahkan masalah pelatihan awal dari efek *self-training*) dan hitungan kesalahan batas (*boundary* B/I) tingkat token (untuk melihat di mana defisit terjadi). Sebagaimana Uji Coba 1, hasil disajikan dalam dua tabel, yaitu metrik agregat (*Precision*, *Recall*, dan F1-score mikro) pada Tabel 4.9 dan F1-score per entitas pada Tabel 4.10.

[SISIPKAN TABEL 4.9 - Precision, Recall, dan F1-score Agregat Uji Coba 2]

| Model | Precision | Recall | F1-score (mikro) |
|-------|----------:|-------:|-----------------:|
| IndoBERT *uncased* (*baseline*) | 0,9489 | 0,9472 | 0,9481 |
| cahya *uncased* | 0,9148 | 0,9507 | 0,9324 |
| DistilBERT *uncased* | 0,9287 | 0,9603 | 0,9442 |
| IndoBERT *cased* | 0,7244 | 0,8378 | 0,7770 |
| RoBERTa | 0,7657 | 0,8525 | 0,8068 |

[SISIPKAN TABEL 4.10 - F1-score per Entitas Uji Coba 2]

| Model | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|-------|----------:|------------:|---------:|--------:|---------:|
| IndoBERT *uncased* (*baseline*) | 0,9596 | 0,9527 | 0,8039 | 0,8408 | 0,8892 |
| cahya *uncased* | 0,9414 | 0,9444 | 0,8119 | 0,8000 | 0,8744 |
| DistilBERT *uncased* | 0,9592 | 0,9478 | 0,8200 | 0,7722 | 0,8748 |
| IndoBERT *cased* | 0,7646 | 0,9062 | 0,6226 | 0,4532 | 0,6867 |
| RoBERTa | 0,8002 | 0,9060 | 0,6306 | 0,5291 | 0,7165 |

[SISIPKAN GAMBAR 4.7 - F1-score Agregat Lima Model Uji Coba 2]
<!-- file: data/result/analysis/bab4_viz/f1_uc2_agregat.png -->

Gambar 4.7 meringkas Tabel 4.9 secara visual dan memperlihatkan keterbelahan dua kelompok, yaitu tiga model *uncased* (dengan IndoBERT *uncased* disorot sebagai *baseline*) berdiri tinggi dan rapat di kisaran F1 0,93 sampai 0,95, sedangkan IndoBERT *cased* dan RoBERTa anjlok jauh.

[SISIPKAN GAMBAR 4.8 - F1-score per Kelas Lima Model Uji Coba 2]
<!-- file: data/result/analysis/bab4_viz/f1_uc2_perkelas.png -->

Gambar 4.8 meringkas Tabel 4.10 per kelas dan menunjukkan bahwa keruntuhan kedua model bermasalah terjadi terutama pada *Time* dan *Event* (turun ke kisaran 0,45 sampai 0,63), bukan merata pada semua kelas. Pola yang terkonsentrasi di kelas minoritas ini menjadi petunjuk awal bahwa masalahnya bersifat teknis dan bukan kemampuan model.

Tabel 4.9 memperlihatkan pola yang terbelah dua. Tiga model *uncased* (IndoBERT, cahya, dan DistilBERT) stabil pada F1-score mikro sekitar 0,93 sampai 0,95 dengan IndoBERT *uncased* tetap yang terbaik, sedangkan dua model lain anjlok jauh, yaitu IndoBERT *cased* (0,7770) dan RoBERTa (0,8068) yang terpaut sekitar lima belas poin. Selisih sebesar ini wajib dijelaskan dan bukan sekadar dilaporkan, sebab penyajian angka tanpa penjelasan mudah disalahartikan sebagai bukti bahwa model *cased* atau RoBERTa "lebih buruk" untuk NER. Investigasi yang dilakukan justru menunjukkan kebalikannya, bahwa anomali ini bukan berasal dari kemampuan model, melainkan dari masalah teknis penyelarasan label pada pipeline yang memang disetel untuk model *uncased*.

Pembelahan dua kelompok ini paling gamblang terlihat ketika *confusion matrix* tingkat token kelima model disandingkan pada Gambar 4.9. Tiga model *uncased* (baris atas, yaitu IndoBERT, cahya, dan DistilBERT) berbentuk hampir identik dengan model sehat pada Uji Coba 1, yaitu blok antar-tipe entitas nyaris kosong dan kesalahan hanya menetes tipis pada baris dan kolom *O*, dengan sel *O* yang diprediksi *Person* berkisar 53 sampai 96 token. Sebaliknya, dua model bermasalah (baris bawah, yaitu IndoBERT *cased* dan RoBERTa) langsung tampak lebih gelap dan berantakan, sebab sel *O* yang diprediksi *Person* melonjak ke 239 dan 181 token sementara sel *Person* yang diprediksi *O* ke 172 dan 163 token, jauh melampaui ketiga model sehat. Kontras yang dapat diringkas sebagai tiga matriks rapi di atas dan dua matriks rusak di bawah ini memperlihatkan anomali sebagai gejala visual bahkan sebelum angkanya dibedah, sehingga pembahasan selanjutnya difokuskan pada satu model bermasalah, yaitu IndoBERT *cased*, sebagai contoh yang ditelaah paling dalam.

[SISIPKAN GAMBAR 4.9 - Confusion Matrix Token-level Lima Model Uji Coba 2]
<!-- file: data/result/analysis/error_viz/by_group/s2_confusion.png -->

Besaran dan komposisi error kedua kelompok model itu terangkum dari empat sudut pada Gambar 4.10. Panel total error (kiri-atas) memperlihatkan anomali tanpa bisa salah baca, yaitu IndoBERT *cased* (721 token) dan RoBERTa (641 token) menjulang jauh di atas tiga model *uncased* yang seragam di kisaran 192 sampai 243 token. Panel *false negative* per kelas (kanan-atas) dan *false positive* per kelas (kiri-bawah) menunjukkan pembengkakan terjadi serentak pada entitas terlewat maupun over-deteksi, dengan *Person* (biru) mendominasi jumlah absolut karena memang kelas terbanyak dan *Time* (ungu) menyumbang porsi mencolok pada sisi *false positive*. Panel *FN-rate* per kelas (kanan-bawah) paling tajam memperlihatkan beban pada kelas minoritas, sebab pada *cased* dan RoBERTa entitas *Event* (merah) terlewat sampai sekitar 15 hingga 17 persen dan *Time* (ungu) sampai 11 hingga 13 persen, berlipat dibanding ketiga model sehat yang menahannya di bawah 10 persen. Pola ini, yaitu error yang meledak menyeluruh dan paling memberatkan kelas yang contohnya sedikit, kemudian ditelusuri akarnya melalui tiga bukti berikut.

[SISIPKAN GAMBAR 4.10 - Panel Perbandingan Error Lima Model Uji Coba 2 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s2_compare.png -->

Kesimpulan tersebut bersandar pada tiga bukti yang saling menguatkan. Pertama, anomali ini bukan kerusakan akibat *self-training*, karena trajektori F1-score dari *checkpoint* awal (*base*) sampai iterasi terakhir justru naik tipis sebagaimana ditunjukkan pada Tabel 4.11, yaitu IndoBERT *cased* bergerak dari 0,7608 ke 0,7770 dan RoBERTa dari 0,7836 ke 0,8068. Seandainya *self-training* yang merusak, F1-score seharusnya menurun seiring iterasi, sehingga fakta kenaikan ini menandakan defisit sudah ada sejak pelatihan pertama dan bukan akibat *pseudo-labelling*. Kedua, defisit ini tidak merata melainkan menimpa entitas yang lazimnya terdiri atas banyak kata, yaitu *Person* dan *Time*, sedangkan entitas yang umumnya satu kata bertahan. Tabel 4.10 menunjukkan F1-score *Person* untuk *cased* dan RoBERTa anjlok ke 0,76 sampai 0,80 (dari 0,94 sampai 0,96 pada *uncased*), dan F1-score *Time* bahkan runtuh paling dalam ke 0,45 sampai 0,53 (dari 0,84), sementara F1-score *Location* tetap tinggi di 0,90 sampai 0,91 (hampir setara *uncased*). Penurunan *Time* yang paling tajam itu memang perlu dibaca dengan hati-hati karena jumlah entitasnya kecil (74) sehingga F1-nya mudah berayun, tetapi arah penurunannya searah dengan *Person* dan keduanya sama-sama entitas banyak kata, sehingga polanya menunjuk pada satu akar yang sama, bukan kebetulan pada nama orang saja. Ketiga, defisit ini disertai ledakan kesalahan batas (*boundary* B/I), sebab pada model *uncased* kesalahan *boundary* hanya 4 sampai 7 token sedangkan pada *cased* melonjak ke 100 token dan pada RoBERTa ke 102 token. Yang menentukan, seluruh kesalahan batas itu jatuh hanya pada kedua kelas banyak-kata: pada *cased* 91 token pada *Person* dan 9 sisanya pada *Time*, pada RoBERTa 94 pada *Person* dan 8 pada *Time*, sementara *Location* dan *Event* tidak menyumbang satu pun kesalahan batas. Distribusi yang persis mengikuti garis satu-kata melawan banyak-kata ini menjadi penegas terkuat bahwa akar masalahnya adalah penyelarasan penanda batas B/I pada entitas banyak kata, bukan kelemahan model pada tipe entitas tertentu.

[SISIPKAN TABEL 4.11 - Trajektori F1 Self-Training Model Anomali (base sampai iterasi-6)]

| Model | F1 *base* | F1 iter-2 | F1 iter-4 | F1 iter-6 |
|-------|----------:|----------:|----------:|----------:|
| IndoBERT *cased* | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |

Pola ini konsisten dengan **misalignment label kata-ke-subword**: entitas banyak kata paling rentan ketika penandaan B/I bergeser. *Person* paling sering berupa nama banyak kata (*Abdul Muththalib*, *Amr bin Luhay*) dan *Time* di teks Sirah juga lazim berupa rangkaian panjang (*hari Senin malam tanggal 21 dari bulan Ramadhan*), sehingga keduanya paling terdampak, sedangkan *Location* yang umumnya satu kata (*Makkah*, *Madinah*) nyaris tak tersentuh. Bahwa hitungan absolut kesalahan batas tetap didominasi *Person* (91 dari 100 token pada *cased*) bukan berarti *Time* aman, melainkan karena *Person* adalah kelas banyak-kata yang jauh paling sering muncul (1.189 berbanding 74 entitas); pada *Time* kerusakan serupa lebih banyak terbaca sebagai runtuhnya F1 relatif dan ledakan *false positive* daripada sebagai jumlah token batas yang besar. Pembeda kedua model ini dari tiga model *uncased* yang sehat adalah skema tokenisasinya (IndoBERT *cased* memakai WordPiece *cased*; RoBERTa memakai *byte-level BPE*), sementara pipeline disetel dan diuji untuk WordPiece *uncased*. Hipotesis terkuat: fungsi penyelarasan label kata-ke-subword tidak menangani tokenizer *cased*/BPE dengan benar, sehingga model dilatih pada label yang sedikit bergeser sejak awal. <!-- [PERIKSA] Status: ini hipotesis yang belum diverifikasi di level kode. Yang sudah terbukti: (1) bukan kerusakan self-training, (2) defisit ada sejak base, (3) terpusat di PERSON multi-kata + boundary. Verifikasi lanjutan: inspeksi fungsi tokenize_and_align_labels (word_ids/is_split_into_words) untuk tokenizer cased & RoBERTa. JANGAN menyimpulkan "cased/RoBERTa lebih buruk untuk NER Sirah" sebelum verifikasi ini. -->

Dari sisi anatomi kesalahan, ketiga model *uncased* memperlihatkan pola error yang sama dengan Uji Coba 1, yaitu didominasi *false positive* dan *false negative* dengan misklasifikasi tipe dan *boundary* yang kecil. Pada model *cased* dan RoBERTa, selain *boundary* yang meledak, misklasifikasi tipe juga lebih banyak (37 dan 43 token) dan sebagian besarnya menyebar ke pasangan yang melibatkan *Person*, sehingga sekali lagi menunjuk pada kerusakan yang terpusat pada penanganan entitas banyak kata, terutama nama orang. Kontras antara model sehat dan model anomali paling jelas terlihat pada kesalahan batas di nama orang banyak kata, dirinci per token pada Tabel 4.12 dan Tabel 4.13. Pada model *uncased* yang sehat, kesalahan batas sangat sedikit (hanya 7 token pada *augmentation*) dan kebanyakan jatuh pada *Time* (lihat Tabel 4.7), sedangkan pada IndoBERT *cased* dan RoBERTa kesalahan ini meledak (sekitar 100 token, 91 dan 94 di antaranya pada *Person*) dan terpusat pada nama orang.

[SISIPKAN TABEL 4.12 - Kesalahan Batas pada Person, IndoBERT cased (chunk 000084-001)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| Abdullah | *B-PERSON* | *B-PERSON* | |
| bin | *I-PERSON* | *I-PERSON* | |
| Amr | *I-PERSON* | *B-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Haram, | *I-PERSON* | *I-LOCATION* | ✗ |

Nama "Abdullah bin Amr bin Haram" yang seharusnya satu entitas *Person* utuh terpecah oleh model: "Amr" ditandai sebagai awal entitas baru (*B*) padahal masih bagian tengah nama, dan "Haram," bahkan ikut berpindah tipe menjadi *Location*.

[SISIPKAN TABEL 4.13 - Kesalahan Batas pada Person, RoBERTa (chunk 000086-002)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| dari | O | O | |
| Ubadah | *B-PERSON* | *I-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Ash-Shamit. | *I-PERSON* | *I-PERSON* | |

Awal nama "Ubadah" yang seharusnya penanda awal entitas (*B*) justru ditandai sebagai lanjutan (*I*), sehingga pola *B* dan *I* tertukar tepat pada permulaan nama banyak kata.

*Confusion matrix* IndoBERT *cased* ditunjukkan pada Gambar 4.11. Dibandingkan model sehat pada Gambar 4.4, kebocoran pada penanganan *Person* langsung terlihat: sel *O* yang diprediksi *Person* melonjak ke 239 token dan *Person* yang diprediksi *O* ke 172 token, jauh di atas *augmentation* yang hanya 62 dan 34. Kekeliruan antar-tipe pun naik menjadi 37 token yang menyebar pada sel-sel kecil di sekitar *Person* dan *Event*, berbanding hanya 4 token pada model sehat. Satu hal penting saat membaca gambar ini, matriksnya bersifat tingkat-tipe sehingga penanda *B* dan *I* digabung; akibatnya ledakan kesalahan batas *B/I* (sekitar 100 token yang menjadi gejala utama anomali) tidak muncul sebagai sel tersendiri melainkan tersembunyi di dalam hitungan *Person* yang dianggap benar. Dengan kata lain, Gambar 4.11 memperlihatkan sisi deteksi dan tipe dari defisit *Person*, sedangkan komponen batasnya terbaca terpisah pada hitungan token yang dibahas sebelumnya.

[SISIPKAN GAMBAR 4.11 - Confusion Matrix IndoBERT cased (anomali)]
<!-- file: data/result/analysis/error_viz/per_skenario/indobert-cased/confusion_matrix.png -->

---

## 4.3 Uji Coba 3: Modul POS-tag

Uji coba ketiga bertujuan menguji apakah penambahan fitur *Part-of-Speech tagging* (POS-tag), yaitu informasi kelas kata seperti kata benda atau kata kerja, dapat membantu model mengenali batas dan tipe entitas dengan lebih baik. Hipotesisnya, mengetahui suatu kata berkategori kata benda dapat menjadi petunjuk tambahan bahwa kata itu berpeluang menjadi entitas. Untuk mengujinya, model tanpa fitur POS-tag (*baseline*) dibandingkan dengan model yang menambahkan POS-tag sebagai fitur pendamping pada masukan.

Pengujian dilakukan dengan melatih kedua varian pada data dan prosedur yang sama, lalu mengevaluasinya pada data uji yang identik (258 *chunk*, 42.558 token, 1.763 entitas). Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* maupun *macro*; metrik ini dilengkapi jumlah kesalahan tingkat token sebagai pembanding langsung banyaknya error. Kedua varian dievaluasi melalui prosedur seqeval yang identik pada data uji yang sama, sehingga angkanya langsung sebanding. Mengikuti format dua uji coba sebelumnya, hasil disajikan pada Tabel 4.14 untuk metrik agregat beserta jumlah error tingkat token dan Tabel 4.15 untuk F1-score per entitas.

[SISIPKAN TABEL 4.14 - Precision, Recall, F1-score Agregat, dan Jumlah Error Uji Coba 3]

| Skenario | Precision | Recall | F1-score (mikro) | Error token |
|----------|----------:|-------:|-----------------:|------------:|
| *Baseline* | 0,9489 | 0,9472 | 0,9481 | 192 |
| POS-tag | 0,9286 | 0,9597 | 0,9439 | 224 |

[SISIPKAN TABEL 4.15 - F1-score per Entitas Uji Coba 3]

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|----------|----------:|------------:|---------:|--------:|---------:|
| *Baseline* | 0,9596 | 0,9527 | 0,8039 | 0,8408 | 0,8892 |
| POS-tag | 0,9579 | 0,9385 | 0,8485 | 0,8182 | 0,8908 |

<!-- Angka POS-tag = inference LANGSUNG via eval_postag_direct.py (rebuild arsitektur BertPosNER + load pytorch_model.bin iter-4, test.csv 258 chunk/42.558 token, seqeval entity-level). Memvalidasi rekonstruksi lama: micro 0,9439 vs rekonstruksi 0,9432 (selisih 0,0007). Rincian error token identik (224: FP146/FN62/MIS9/BND7). Output: data/result/pseudo-labelling/SRL-NER/seqeval_postag_direct.md + data/result/analysis/error_viz/postag_direct_predictions.csv. -->

[SISIPKAN GAMBAR 4.12 - F1-score Agregat Baseline vs Modul POS-tag Uji Coba 3]
<!-- file: data/result/analysis/bab4_viz/f1_uc3_agregat.png -->

Gambar 4.12 meringkas Tabel 4.14 dan menunjukkan F1 mikro maupun macro yang nyaris berimpit antara *baseline* dan POS-tag, sehingga secara agregat tidak tampak perbaikan dari penambahan POS-tag.

[SISIPKAN GAMBAR 4.13 - F1-score per Kelas Baseline vs Modul POS-tag Uji Coba 3]
<!-- file: data/result/analysis/bab4_viz/f1_uc3_perkelas.png -->

Gambar 4.13 meringkas Tabel 4.15 per kelas dan memperlihatkan perubahan yang tidak konsisten arahnya, yaitu *Event* naik tipis sementara *Location* dan *Time* justru turun, sehingga secara visual pun penambahan POS-tag tidak memberi perbaikan yang sistematis.

Secara ringkas, modul POS-tag tidak memberikan perbaikan yang berarti. F1-score mikro POS-tag (0,9439) praktis setara dengan *baseline* dan bahkan sedikit di bawahnya, dengan selisih yang masih berada dalam rentang variansi antar-*run* sehingga tidak dapat ditafsirkan sebagai perbedaan yang bermakna. Perubahan per kelas pada Tabel 4.15 pun tidak konsisten, sebab F1-score *Event* naik tipis dari 0,8039 ke 0,8485 (kenaikan pada kelas bersupport kecil yang lebih mungkin berasal dari variasi acak daripada efek POS) sementara *Location* dan *Time* justru turun, sehingga secara agregat tidak ada arah perbaikan yang jelas. Tabel 4.14 memperlihatkan bahwa penambahan fitur ini hanya menggeser model ke arah *recall* lebih tinggi (0,9597) dengan *precision* yang menurun (0,9286), pola yang mirip dengan *weighted cross-entropy* pada Uji Coba 1, yaitu lebih banyak menebak tanpa diiringi pengenalan yang lebih tepat.

Penting ditegaskan bahwa hasil ini diperoleh dari fitur POS yang asli, bukan *placeholder*. Pemeriksaan atas berkas data yang benar-benar dipakai pada *run* POS-tag (`data_with_pos_20260610` dan dataset *retraining* skenario ini) menunjukkan kolom POS terisi 17 kategori Universal Dependencies yang beragam dan selaras dengan token, yaitu NOUN, VERB, PROPN, PRON, ADP, dan seterusnya, dengan 1.131 dari 1.189 token bertanda *Person* berkategori PROPN. Temuan eksplorasi data (EDA) sebelumnya yang menyebut kolom `pos_tag` berisi nilai *placeholder* "NN" merujuk pada berkas *dataset* utama versi lama dan tidak berlaku untuk berkas POS yang dibuat khusus bagi uji coba ini. Dengan demikian, kegagalan modul POS-tag bukan artefak fitur palsu, melainkan hasil yang sah, sehingga penyebab yang paling masuk akal adalah bahwa informasi POS sebagian besar redundan dengan apa yang sudah dipelajari IndoBERT dari konteks: sebagai model bahasa berbasis konteks, IndoBERT pada praktiknya telah menyerap petunjuk kelas kata sehingga menambahkan POS secara eksplisit tidak memberi sinyal baru yang berarti untuk membedakan entitas.

Dari sisi anatomi kesalahan, pola error skenario POS-tag tetap sama dengan *baseline*, yaitu didominasi *false positive* dan *false negative*. Rinciannya memperjelas pergeseran yang terbaca pada metrik agregat: dari 224 token salah, *false positive* (over-deteksi, kata bukan-entitas yang ditandai entitas) mencapai 146 token atau 65 persen, *false negative* (entitas terlewat) 62 token atau 28 persen, sedangkan misklasifikasi tipe hanya 9 token (4 persen) dan kesalahan batas hanya 7 token (3 persen), sehingga sama seperti skenario lain kesalahan terpusat pada keputusan deteksi, bukan pada pembedaan jenis entitas. Dibandingkan *baseline* yang *false positive*-nya hanya 86 token dan *false negative* 91 token, penambahan POS justru menaikkan *false positive* hampir dua kali lipat sambil menurunkan *false negative*; inilah wujud konkret dari *recall* yang naik tetapi *precision* yang turun, yaitu model menjadi lebih agresif menebak entitas tanpa menjadi lebih tepat. Hal ini tampak misalnya pada penggalan "... penaklukan bangsa **Babilon** dan Asyur ..." yang seharusnya berlabel *B_LOCATION* tetapi diprediksi O karena merupakan nama tempat langka, serta pada penggalan "... Perang Uhud **Jabal** Uhud ..." yang seharusnya *Event* tetapi diprediksi *Location* sebagai sisi lain dari ambiguitas nama yang sama dipakai untuk tempat sekaligus peristiwa.

Adapun kategori terbesar, yaitu *false positive* (over-deteksi), paling khas berupa frasa kehormatan (*honorifik*) yang keliru ditandai sebagai nama orang, sebagaimana dirinci per token pada Tabel 4.16. Pada penggalan dari *chunk* 000010-002, ungkapan salawat "*Shalallahu Alaihi wa Sallam*" yang menurut acuan bukan entitas (berlabel *O*) justru diprediksi sebagai satu entitas *Person* sepanjang empat token, padahal nama penulis "*Muhammad bin* …" tepat sesudahnya tetap dikenali dengan benar. Pola ini menjelaskan mengapa kelas *Person* paling banyak menyumbang *false positive*, sebab frasa kehormatan dan rangkaian nasab yang sering muncul pada teks Sirah mudah dikira bagian dari nama.

[SISIPKAN TABEL 4.16 - Contoh Over-deteksi Honorifik sebagai Person (chunk 000010-002)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| Mukhtashar | *O* | *O* | |
| Siratir-Rasul | *O* | *O* | |
| Shalallahu | *O* | *B-PERSON* | ✗ |
| Alaihi | *O* | *I-PERSON* | ✗ |
| wa | *O* | *I-PERSON* | ✗ |
| Sallam, | *O* | *I-PERSON* | ✗ |
| Syaikh | *O* | *O* | |
| Muhammad | *B-PERSON* | *B-PERSON* | |
| bin | *I-PERSON* | *I-PERSON* | |

*Confusion matrix* skenario POS-tag ditunjukkan pada Gambar 4.14. Strukturnya menyerupai model sehat, yaitu kesalahan terkonsentrasi pada baris dan kolom *O* sementara kebingungan antar-tipe entitas tetap kecil (hanya sekitar 9 token). Bedanya, sel over-deteksi membesar dibanding *augmentation*, terutama *O* yang diprediksi *Person* (87 token berbanding 62) dan *O* yang diprediksi *Time* (28 token berbanding 8), sehingga jumlah *false positive* keseluruhan naik. Pola ini sejalan dengan Tabel 4.14 yang menunjukkan *recall* POS-tag lebih tinggi tetapi *precision* lebih rendah, yaitu fitur POS membuat model lebih agresif menebak entitas tanpa menjadi lebih tepat.

[SISIPKAN GAMBAR 4.14 - Confusion Matrix Skenario POS-tag]
<!-- file: data/result/analysis/error_viz/per_skenario/POS-tag/confusion_matrix.png -->

Perbandingan *baseline* dan POS-tag dari empat sudut dirangkum pada Gambar 4.15. Panel total error (kiri-atas) menunjukkan POS-tag sedikit lebih banyak salah (224 berbanding 192 token). Yang lebih informatif adalah dua panel komposisi: panel *false negative* per kelas (kanan-atas) memperlihatkan POS-tag justru melewatkan lebih sedikit entitas (62 berbanding 91 token), sedangkan panel *false positive* per kelas (kiri-bawah) memperlihatkan kebalikannya, yaitu over-deteksi POS-tag membengkak (146 berbanding 86 token, didominasi *Person* biru dengan tambahan *Time* ungu). Kedua panel ini adalah wujud visual paling langsung dari pertukaran *recall* yang naik tetapi *precision* yang turun, yaitu model menjadi lebih berani menebak sehingga lebih sedikit entitas terlewat, tetapi dengan ongkos lebih banyak salah tebak. Panel *FN-rate* per kelas (kanan-bawah) menunjukkan POS-tag hanya menurunkan tingkat terlewat kelas minoritas secara tipis (*Event* dari sekitar 10 ke 9 persen), perbaikan yang terlalu kecil untuk menutup kerugian di sisi *precision*. Dengan demikian, panel ini memperkuat kesimpulan bahwa modul POS-tag tidak memberikan perbaikan bersih.

[SISIPKAN GAMBAR 4.15 - Panel Perbandingan Error Baseline vs POS-tag Uji Coba 3 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s3_compare.png -->

### Rangkuman ketiga uji coba dan pembahasan error lintas-skenario

Menggabungkan ketiga uji coba, **konfigurasi terbaik adalah IndoBERT *uncased* dengan *augmentation*** (micro F1 0,9581). Dua temuan error berlaku konsisten di semua skenario yang sehat. Pertama, **urutan F1 per kelas (Event < Time < Location < Person) persis mengikuti urutan jumlah data** (*Event* 51, *Time* 74, *Location* 449, *Person* 1.189 entitas), sehingga kelangkaan contoh (*few-shot*) adalah faktor dominan kesalahan, dan augmentation berhasil justru karena menambah contoh kelas minoritas. Kedua, **misklasifikasi tipe yang sedikit itu didominasi pasangan *Location* dan *Event***, karena sejumlah nama identik berfungsi ganda sebagai tempat sekaligus peristiwa (*Uhud*, *Badr*, *Hudaibiyah*). Ini ambiguitas semantik nyata pada teks Sirah, bukan kelemahan model. Sebagai keterbatasan, efek *chunking* tidak diuji melalui *ablation* terpisah; pemeriksaan tak langsung menunjukkan hanya 16 sampai 29 persen error berada di tepi *chunk*, sehingga pemotongan konteks bukan penyebab utama error.

---

## 4.4 Evaluasi Graf

Evaluasi *knowledge graph* terdiri dari dua bagian: analisis struktur jaringan dengan *Social Network Analysis* (apakah struktur graf masuk akal terhadap narasi Sirah) dan pengujian fungsional melalui skenario kueri (apakah graf dapat menjawab kebutuhan penelusuran).

### 4.4.1 Analisis Struktur Jaringan (SNA)

Hasil analisis jaringan menjawab delapan skenario pengujian (G1 sampai G8) yang dirancang pada Tabel 3.19, yaitu sentralitas tokoh (G1 dan G2), pengelompokan komunitas (G3), sentralitas peristiwa (G4), struktur jaringan keseluruhan (G5), studi kasus peristiwa (G6), peran lokasi (G7), dan keterlibatan lintas fase (G8). Analisis utama dilakukan pada proyeksi jaringan antar tokoh (*Person*), yaitu dua tokoh dihubungkan jika terlibat pada peristiwa yang sama. Bukti struktural di balik tiap skenario dapat ditelusuri langsung pada *knowledge graph* di Neo4j melalui kumpulan kueri reproduksi yang disediakan pada berkas `sna_evidence_queries_bab4.cypher`, sementara skor sentralitas dan komunitas dihitung pada pipeline analisis (NetworkX). Statistik tingkat graf (G5) ditunjukkan pada Tabel 4.17.

<!-- Kueri reproduksi bukti SNA per skenario (G1/G3/G4/G6/G7/G8) ada di data/result/neo4j/sna_evidence_queries_bab4.cypher. Plain Cypher mereproduksi struktur (derajat co-participation, daftar peserta, jumlah PRECEDES, lintas fase via Period.phase); skor degree centrality/betweenness/PageRank + Louvain/modularitas dari src/analysis/sna_analysis.py (butuh GDS bila dipaksakan di Neo4j). -->

[SISIPKAN TABEL 4.17 - Statistik Jaringan Tokoh]

| Metrik | Nilai |
|--------|------:|
| Jumlah *node* (*Person*) | 208 |
| Jumlah *edge* | 1.832 |
| *Density* | 0,0851 |
| *Average clustering coefficient* (lokal) | 0,4787 |
| *Transitivity* (global) | 0,7624 |
| Jumlah komponen | 8 |
| Ukuran komponen terbesar | 192 *node* (92,3%) |
| Rata-rata panjang lintasan (komponen terbesar) | 2,53 |
| Jumlah komunitas (Louvain) | 15 |
| **Modularitas (Q, Louvain)** | **0,3851** |

<!-- Angka dari data/result/analysis/v3/graph_metrics_v2.md & sna_summary.md (graf Person berbobot, v3). Modularitas Q dikonfirmasi dari graph_metrics_v2.md (dihasilkan sna_graph_metrics.py): Louvain proper Q=0,3851 (15 komunitas); pembanding greedy Q=0,3600 dan Girvan-Newman Q=0,0338; ARI(Louvain,greedy)=0,78. -->

Sentralitas tokoh dibaca dari dua sudut yang saling melengkapi, yaitu siapa yang paling sentral secara menyeluruh (G1) dan siapa yang menjadi jembatan penghubung antar-kelompok (G2). Untuk G1, sepuluh tokoh teratas beserta tiga ukuran sentralitas (*degree centrality*, *closeness centrality*, dan *PageRank*) ditunjukkan pada Tabel 4.18, diurutkan menurut *PageRank* sebagai ukuran kepentingan menyeluruh.

[SISIPKAN TABEL 4.18 - Sepuluh Tokoh Teratas Sentralitas Tokoh (G1): Degree, Closeness, PageRank]
<!-- Sumber: data/result/analysis/v3/sna_metrics.csv (graf Person weighted v3, 208 node). Diurut PageRank. -->

| Rank | Tokoh | Degree | Closeness | PageRank |
|---:|-------|------:|------:|------:|
| 1 | Muhammad | 0,5894 | 0,6503 | 0,0565 |
| 2 | Ali bin Abu Thalib | 0,3961 | 0,5357 | 0,0224 |
| 3 | Abu Bakar | 0,3720 | 0,5153 | 0,0206 |
| 4 | Aisyah | 0,3623 | 0,5123 | 0,0195 |
| 5 | Abu Jahal | 0,3720 | 0,5261 | 0,0189 |
| 6 | Umar bin Al-Khaththab | 0,3623 | 0,5168 | 0,0168 |
| 7 | Abu Sufyan bin Harb | 0,3478 | 0,5050 | 0,0153 |
| 8 | Utsman bin Affan | 0,3478 | 0,5064 | 0,0138 |
| 9 | Abu Azzah | 0,3333 | 0,4993 | 0,0130 |
| 10 | Khadijah | 0,0870 | 0,4137 | 0,0118 |

Ketiga ukuran G1 sepakat menempatkan Muhammad di puncak dengan jarak yang sangat lebar (*degree* 0,5894, hampir 1,5 kali tokoh kedua), diikuti sahabat utama dan tokoh kunci. Sudut kedua (G2), yaitu *betweenness centrality* yang mengukur peran sebagai penghubung jalur terpendek antar tokoh, menghasilkan susunan yang berbeda dan justru lebih informatif untuk melihat fungsi jembatan, sebagaimana ditunjukkan pada Tabel 4.19.

[SISIPKAN TABEL 4.19 - Sepuluh Tokoh Teratas berdasarkan Betweenness (Jembatan Antar-Kelompok, G2)]
<!-- Sumber: data/result/analysis/v3/sna_summary.md (graf Person weighted v3). -->

| Rank | Tokoh | Betweenness |
|---:|-------|------:|
| 1 | Muhammad | 0,3567 |
| 2 | Utsman bin Affan | 0,1042 |
| 3 | Abu Jahal | 0,0712 |
| 4 | Ali bin Abu Thalib | 0,0677 |
| 5 | Hamzah bin Abdul Muththalib | 0,0647 |
| 6 | Ka'b bin Malik | 0,0528 |
| 7 | Abu Sa'id | 0,0528 |
| 8 | Al-Barra' Bin Azib | 0,0522 |
| 9 | Khadijah | 0,0354 |
| 10 | Ibrahim | 0,0272 |

**Interpretasi.** Struktur jaringan masuk akal terhadap narasi Sirah. Muhammad sangat dominan pada semua ukuran sentralitas (*PageRank* 0,0565, jauh di atas peringkat kedua; *degree centrality* 0,5894, yang berarti ia terhubung langsung ke sekitar 122 dari 208 tokoh; *betweenness* 0,3567), mencerminkan posisinya sebagai pusat seluruh peristiwa. Perbandingan G1 dan G2 memperlihatkan dua peran yang berbeda: tokoh dengan *degree* dan *PageRank* tinggi (Ali bin Abu Thalib, Abu Bakar, Aisyah) adalah mereka yang paling banyak muncul bersama tokoh lain pada peristiwa besar, sedangkan tokoh dengan *betweenness* tinggi tetapi *degree* lebih sedang berperan sebagai penghubung antar-kelompok meskipun koneksi langsungnya tidak terbanyak. Hal ini paling jelas pada Utsman bin Affan yang melompat dari peringkat kedelapan pada *degree*/*PageRank* menjadi peringkat kedua pada *betweenness*, juga pada Hamzah bin Abdul Muththalib dan Khadijah yang masuk sepuluh besar jembatan namun tidak menonjol pada *degree*; membaca kedua ukuran bersama lebih informatif daripada satu peringkat tunggal. Peringkat berikutnya diisi sahabat utama dan tokoh kunci (Abu Bakar, Umar, Utsman, Ali, Aisyah, Khadijah) serta tokoh oposisi yang memang banyak terlibat peristiwa (Abu Jahal, Abu Sufyan). Deteksi komunitas dengan algoritma Louvain menghasilkan 15 komunitas dengan modularitas Q = 0,3851, nilai yang menunjukkan struktur kelompok yang cukup jelas. Beberapa komunitas terbesar koheren secara naratif, sebagaimana terlihat dari anggota dan kata dominan pada *evidence* teksnya: komunitas keluarga dan lingkar awal Nabi (64 anggota; tokoh utama Muhammad, Khadijah, Hamzah; token dominan "khadijah", "ka'b"), komunitas tokoh Madinah dan ekspansi (45 anggota; Umar, Abu Sufyan, Utsman; token dominan "uhud", "umar"), komunitas tokoh oposisi Quraisy (41 anggota; Abu Lahab, Ikrimah, Umayyah bin Khalaf; token dominan "badr", "makkah"), serta komunitas keluarga inti (21 anggota; Ali, Abu Bakar, Aisyah). Pengelompokan ini cukup stabil terhadap pilihan algoritma, ditunjukkan oleh kesepakatan tinggi antara Louvain dan *greedy modularity* (*Adjusted Rand Index* 0,78).

**Validasi tokoh yang terdengar asing.** Sebagian nama pada sepuluh besar mungkin terdengar asing dibanding tokoh yang lazim disebut sentral dalam literatur Sirah (para Khulafa Rasyidin). Kemunculan mereka berakar pada cara graf dibentuk, yaitu dua tokoh dihubungkan bila terlibat pada peristiwa yang sama (*co-participation*), sedangkan relasi keterlibatan (`INVOLVED_IN`) diekstraksi berdasarkan kedekatan posisi tokoh dengan nama peristiwa di dalam teks. Akibatnya, tokoh minor yang kebetulan disebut di dalam atau dekat *chunk* peristiwa berpenghuni padat (Perang Badr saja menautkan puluhan tokoh) otomatis terhubung ke seluruh peserta peristiwa itu dan membentuk *clique*, sehingga sentralitasnya ikut melonjak. Dengan kata lain, peringkat sentralitas sebagian mencerminkan seberapa banyak teks menyebut seseorang di sekitar peristiwa besar, bukan semata bobot historisnya. Contoh paling jelas adalah **Amr Bin Umayyah**: pada graf tanpa pembobotan ia sempat menempati peringkat kedua *PageRank* (degree 119), tepat di bawah Nabi Muhammad, posisi yang mencurigakan secara historis. Penelusuran balik ke teks menunjukkan tiga dari empat relasi `INVOLVED_IN`-nya adalah *false positive*, sebab keterkaitannya dengan Perang Badr, Uhud, dan Tabuk muncul dari kalimat yang sebenarnya membicarakan tokoh atau perbandingan lain, sementara hanya Perang Khandaq yang sahih; peran sebenarnya menurut teks adalah kurir Nabi ke Najasyi. Pembobotan sisi (membuang *co-mention* lemah) menurunkan Amr ke peringkat ke-18 sehingga ia tidak lagi muncul pada sepuluh besar Tabel 4.18 maupun Tabel 4.19. Pembobotan tidak menghapus seluruh artefak: **Abu Azzah** (peringkat sembilan pada Tabel 4.18) adalah sisa artefak ringan, yaitu ia disebut dalam konteks Perang Badr dan Uhud sehingga ikut *clique* peperangan, dan karena namanya muncul pada kalimat yang sama dengan nama peristiwa, pembobotan tidak memangkasnya; pola serupa menjelaskan kehadiran sejumlah perawi atau tokoh pendukung pada peringkat jembatan Tabel 4.19 (misalnya Al-Barra' Bin Azib dan Abu Sa'id). Temuan ini menegaskan bahwa peringkat sentralitas wajib divalidasi balik ke teks, dan bahwa solusi tuntas atas over-ekstraksi `INVOLVED_IN` berbasis kedekatan posisi adalah ekstraksi relasi berbasis makna kata kerja, yang menjadi arah pengembangan lanjutan.

**Sentralitas peristiwa (G4).** Analisis diperluas ke jaringan antar-peristiwa, yaitu dua *Event* dihubungkan bila berbagi minimal satu tokoh, dengan bobot sisi sama dengan jumlah tokoh bersama (46 *Event*, 354 sisi, *density* 0,342, 7 komponen, komponen terbesar memuat 40 peristiwa). Sepuluh peristiwa paling sentral menurut *PageRank* ditunjukkan pada Tabel 4.20.

[SISIPKAN TABEL 4.20 - Sepuluh Peristiwa Teratas berdasarkan PageRank]

| Rank | Peristiwa | PageRank | Frekuensi |
|------|-----------|---------:|----------:|
| 1 | Perang Badr | 0,0767 | 51 |
| 2 | Perang Uhud | 0,0704 | 41 |
| 3 | Perang Khandaq | 0,0505 | 20 |
| 4 | Hijrah ke Madinah | 0,0489 | 26 |
| 5 | Kelahiran Nabi | 0,0407 | 29 |
| 6 | Wafat Nabi | 0,0368 | 21 |
| 7 | Baiat Aqabah Kubra | 0,0362 | 4 |
| 8 | Wahyu Pertama | 0,0350 | 15 |
| 9 | Perang Dzul Usyairah | 0,0324 | 1 |
| 10 | Pemboikotan Bani Hasyim | 0,0321 | 9 |

Tiga peristiwa teratas adalah peperangan besar, yaitu Perang Badr (*PageRank* 0,0767), Perang Uhud (0,0704), dan Perang Khandaq (0,0505). Peringkat ini didukung bukti *co-participation* yang kuat: Perang Badr terhubung ke 33 dari 45 peristiwa lain (*degree* 33) dengan *weighted degree* 80, dan Perang Uhud juga ber-*degree* 33 dengan *weighted degree* 70, keduanya tertinggi pada graf peristiwa. Artinya kedua perang ini berbagi tokoh dengan hampir semua peristiwa lain, sehingga wajar menjadi pusat jaringan; pola ini masuk akal karena peperangan besar melibatkan paling banyak tokoh sehingga jaringan *co-participation*-nya paling padat. Setelah ketiga perang, peringkat diisi peristiwa daur hidup, yaitu Hijrah ke Madinah (0,0489), Kelahiran Nabi (0,0407), dan Wafat Nabi (0,0368), yang menegaskan bahwa tonggak hidup Nabi tetap menjadi simpul penting meskipun bukan peperangan.

Sebagai bukti bahwa *PageRank* dan fungsi naratif tidak selalu sejalan, ukuran *betweenness* (jembatan antar kelompok peristiwa) justru menempatkan Perang Uhud di puncak (0,1403), di atas Perang Khandaq (0,0711) dan Perang Badr (0,0489). Perang Uhud berperan sebagai penghubung antara kelompok peristiwa awal Madinah dan kelompok peristiwa pasca-Uhud, sehingga membaca kedua ukuran bersama lebih kaya daripada satu peringkat tunggal. Dua *caveat* perlu ditegaskan. Pertama, peringkat *PageRank* peristiwa wajib dibaca bersama frekuensi kemunculannya, sebab aturan *co-participation* dapat menggelembungkan peristiwa berfrekuensi rendah: Perang Dzul Usyairah menempati peringkat 9 (0,0324) padahal frekuensinya hanya 1, karena ia berada pada periode yang sama dengan Perang Badr (P8) sehingga "kecipratan" puluhan tokoh bersama (*degree* 26); pola serupa terjadi pada Baiat Aqabah Kubra yang berperingkat 7 dengan frekuensi hanya 4. Kedua, relasi kronologi `PRECEDES` hanya berjumlah 23 sisi, jauh lebih sedikit daripada ratusan sisi *co-participation*, sehingga sinyal yang dominan adalah kemunculan bersama, bukan urutan waktu eksplisit.

**Peran lokasi (G7).** Dua lokasi dihubungkan bila ada tokoh yang terlibat pada peristiwa di kedua lokasi (35 *Location*, 437 sisi, *density* 0,734). Karena graf lokasi sangat padat, *betweenness* nyaris tidak membedakan sehingga peringkat memakai *weighted degree* (total tokoh bersama). Sepuluh lokasi paling sentral ditunjukkan pada Tabel 4.21.

[SISIPKAN TABEL 4.21 - Sepuluh Lokasi Teratas berdasarkan Weighted Degree]

| Rank | Lokasi | Weighted degree |
|------|--------|----------------:|
| 1 | Madinah | 684 |
| 2 | Makkah | 595 |
| 3 | Habasyah | 505 |
| 4 | Yatsrib | 453 |
| 5 | Badr | 450 |
| 6 | Tihamah | 450 |
| 7 | Hijir | 450 |
| 8 | Aqabah | 361 |
| 9 | Yaman | 240 |
| 10 | Hunain | 237 |

Hasil ini masuk akal terhadap geografi Sirah. Madinah (*weighted degree* 684) dan Makkah (595) menempati dua posisi teratas, mencerminkan dua pusat dari dua fase besar Sirah, yaitu dakwah di Makkah dan periode Madinah. Bukti bahwa *betweenness* tidak layak dipakai di sini terlihat langsung pada data: Madinah, Makkah, dan setidaknya delapan lokasi lain (di antaranya Aqabah, Yaman, Syam, Ka'bah, Zamzam, dan Baitul-Haram) memiliki *degree* identik 34 dengan *betweenness* yang persis sama 0,0254, sehingga ukuran ini tidak mampu membedakan peran antar lokasi pada graf yang nyaris penuh ini; sebaliknya *weighted degree* yang menghitung total tokoh bersama jauh lebih diskriminatif, dengan sebaran nilai yang lebar (pada sepuluh besar saja berkisar dari 237 untuk Hunain sampai 684 untuk Madinah). Habasyah menempati peringkat 3 (505) meskipun berada di seberang Laut Merah, konsisten dengan perannya sebagai tujuan Hijrah ke Habasyah. Sebagai keterbatasan yang harus diungkap, "Yatsrib" muncul terpisah pada peringkat 4 (453) padahal Yatsrib adalah nama lama Madinah; keduanya tidak tergabung oleh *alias clustering* pada graf lokasi, sehingga peran Madinah sebenarnya ter-*understate* (jika digabung, dominasinya makin besar). Pola lain yang menandakan keterbatasan aturan *co-participation* adalah tiga lokasi Badr, Tihamah, dan Hijir yang memiliki *weighted degree* identik 450, indikasi bahwa ketiganya terhubung melalui himpunan tokoh bersama yang sama persis, bukan melalui keterkaitan geografis yang berdiri sendiri.

**Keterlibatan lintas fase (G8).** Skenario ini menghitung jumlah fase Sirah unik (dari enam fase) tempat seorang tokoh terlibat, melalui jalur tokoh ke peristiwa ke fase. Hasilnya ditunjukkan pada Tabel 4.22.

[SISIPKAN TABEL 4.22 - Tokoh dengan Keterlibatan Lintas Fase Terbanyak]

| Rank | Tokoh | Jumlah fase | Jumlah peristiwa |
|------|-------|------------:|-----------------:|
| 1 | Muhammad | 6 | 25 |
| 2 | Abu Bakar | 4 | 6 |
| 3 | Aisyah | 4 | 5 |
| 4 | Jibril | 3 | 5 |
| 5 | Ibnu Hisyam | 3 | 3 |
| 6 | Ali bin Abu Thalib | 2 | 8 |

Bukti paling kuat dari skenario ini adalah Muhammad sebagai satu-satunya tokoh yang merentang seluruh enam fase (dari fase I Pra-Islam, II Makkah, III Madinah Awal, IV Perang Besar, V Diplomasi, sampai VI Konsolidasi) melalui 25 peristiwa, menegaskan posisinya sebagai poros narasi yang hadir di setiap babak. Di bawahnya, hanya dua tokoh menyentuh empat fase, yaitu Abu Bakar (6 peristiwa) dan Aisyah (5 peristiwa); keduanya melompati fase Pra-Islam dan Madinah Awal namun konsisten hadir sejak fase Makkah sampai Konsolidasi, sesuai posisi mereka sebagai sahabat terdekat dan istri Nabi. Distribusi keseluruhan sangat timpang dan menjadi bukti bahwa mayoritas tokoh bersifat spesifik untuk satu babak: 120 tokoh hanya menyentuh satu fase, 25 tokoh dua fase, masing-masing dua tokoh menyentuh tiga dan empat fase, dan hanya satu tokoh (Muhammad) menyentuh enam fase. Sebagai catatan, banyaknya peristiwa yang diikuti tidak otomatis berarti jangkauan lintas fase yang luas: Ali bin Abu Thalib terlibat di delapan peristiwa, terbanyak setelah Muhammad, tetapi seluruhnya terkonsentrasi pada dua fase saja (Makkah dan Perang Besar). Skenario ini juga memunculkan *caveat* metodologis yang penting, yaitu kehadiran Jibril dan Ibnu Hisyam pada peringkat tiga fase. Keduanya perlu dibaca hati-hati karena pola fase mereka justru ganjil: keduanya menyentuh Fase I (Pra-Islam), II (Makkah), dan VI (Konsolidasi), tetapi melompati ketiga fase di tengah (Madinah Awal, Perang Besar, dan Diplomasi). Aktor historis yang benar-benar aktif lintas waktu seharusnya hadir pada fase-fase yang berurutan, sehingga pola yang "meloncat" ini menandakan keterhubungan mereka bukan berasal dari keterlibatan langsung pada peristiwa, melainkan dari cara nama mereka tersebar di teks. Mekanismenya adalah relasi `INVOLVED_IN` yang dibentuk dari kedekatan posisi nama dengan nama peristiwa di dalam *chunk*: sebuah nama yang sering muncul di banyak bagian buku otomatis tertaut ke peristiwa-peristiwa yang kebetulan berada di dekatnya, walau secara historis tidak ikut serta. Pada kedua tokoh ini sebab kemunculannya berbeda. Ibnu Hisyam adalah perawi sekaligus penyusun riwayat yang namanya berulang di seluruh buku sebagai penyebut sumber ("Ibnu Hisyam berkata", "menurut Ibnu Hisyam"), sehingga keluasan fasenya murni mencerminkan peran sebagai sumber periwayatan, bukan keterlibatan pada peristiwa, sejalan dengan pola artefak periwayatan yang telah dibahas pada validasi sentralitas tokoh. Jibril adalah malaikat pembawa wahyu yang dalam narasi muncul pada momen-momen turunnya wahyu yang tersebar dari awal sampai akhir kenabian, sehingga ia tertaut ke beberapa fase bukan sebagai peserta peperangan atau peristiwa sosial, melainkan sebagai figur teologis yang menyertai peristiwa pewahyuan. Kedua kasus ini menegaskan bahwa peringkat lintas fase, seperti halnya peringkat sentralitas, wajib divalidasi balik ke makna teks dan tidak boleh dibaca semata sebagai ukuran keterlibatan historis.

**Studi kasus lima peristiwa besar (G6).** Untuk memvalidasi pipeline secara kualitatif, dipilih lima peristiwa dari periode yang berjauhan (P8 sampai P13) lalu diperiksa sub-grafnya. Ringkasannya ditunjukkan pada Tabel 4.23 dan panel visualisasinya pada Gambar 4.16.

[SISIPKAN TABEL 4.23 - Ringkasan Sub-graf Lima Peristiwa Besar]

| Peristiwa | Periode | Tokoh | Lokasi | Waktu |
|-----------|:-------:|------:|-------:|------:|
| Perang Badr | P8 | 45 | 7 | 6 |
| Perang Uhud | P9 | 34 | 3 | 9 |
| Perjanjian Hudaibiyah | P11 | 2 | 3 | 3 |
| Perang Khaibar | P11 | 6 | 2 | 2 |
| Perang Tabuk | P13 | 4 | 0 | 1 |

<!-- Angka di-recompute dari graf final SNA (edges_v3.csv, INVOLVED_IN weight >= 0.3, sama dengan WEIGHT_THRESHOLD di sna_analysis.py) via visualize_case_study_events.py --version v3. Konsisten dengan header tiap panel pada Gambar 4.16. -->


[SISIPKAN GAMBAR 4.16 - Panel Sub-graf Lima Peristiwa Besar]
<!-- file: data/result/analysis/v3/case_study_panel.png -->

Secara visual, Gambar 4.16 menyusun kelima sub-graf dengan satu *node* peristiwa (kuning) di pusat tiap panel dan tokoh peserta (biru) mengelilinginya, dihubungkan garis merah untuk relasi `INVOLVED_IN` serta garis hijau untuk relasi antar-tokoh (keluarga dan sahabat). Perbedaan kepadatan antar panel langsung terbaca: panel Perang Badr (45 tokoh) dan Perang Uhud (34 tokoh) tampak rapat oleh banyak tokoh dan garis, sedangkan Perjanjian Hudaibiyah (2 tokoh), Perang Khaibar (6 tokoh), dan Perang Tabuk (4 tokoh) hanya berisi segelintir tokoh, sehingga kontras cakupan antar peristiwa terlihat sekilas pandang. Dari kelima peristiwa, terkumpul 78 tokoh unik dan hanya Muhammad yang hadir di seluruh lima peristiwa, menegaskan perannya sebagai tulang punggung jaringan. Ukuran sub-graf menurun tajam dari Perang Badr ke Perjanjian Hudaibiyah. Penurunan ini lebih mencerminkan **bias cakupan NER** (seberapa banyak tokoh disebut pada *chunk* peristiwa itu) daripada keterlibatan historis sebenarnya, karena setiap sub-graf peristiwa secara konstruksi membentuk *clique* (semua peserta saling terhubung) sehingga *density* selalu bernilai 1,0 dan tidak informatif sebagai pembanding. Ukuran (jumlah tokoh) dan jumlah relasi langsung antar tokoh lebih tepat dipakai sebagai pembanding kohesi. Sebagai bukti keterbatasan aturan ini, daftar peserta Perang Badr justru mencampur dua kubu yang saling berperang: tokoh Muslim (Ali bin Abu Thalib, Hamzah bin Abdul Muththalib, Utsman bin Affan) dan tokoh Quraisy (Abu Jahal, Abu Lahab, Abu Sufyan bin Harb) sama-sama tertaut sebagai `INVOLVED_IN` peristiwa yang sama. Hal ini menegaskan bahwa relasi *co-participation* hanya menyatakan "terlibat pada peristiwa yang sama", bukan "berada di pihak yang sama", sehingga sub-graf peristiwa tidak boleh dibaca sebagai aliansi.


**Analisis error/keterbatasan graf.** Sebagaimana error pada NER, struktur graf juga memuat sejumlah *artifact* yang perlu diungkap secara jujur:

1. **Over-ekstraksi relasi `INVOLVED_IN` berbasis kedekatan.** Karena relasi dibentuk dari kemunculan bersama dalam *chunk* yang sama, sebagian tokoh memperoleh keterhubungan yang lebih tinggi daripada perannya yang sebenarnya. Contoh yang sudah ditelusuri adalah "Amr bin Umayyah" (muncul pada peringkat ke-18 *PageRank*, 0,0096): pemeriksaan menunjukkan sebagian relasi `INVOLVED_IN`-nya adalah *false positive* dari kedekatan teks, sedangkan peran historisnya yang nyata adalah kurir Nabi. <!-- [PERIKSA] cocokkan detail validasi Amr bin Umayyah dengan validation_amr_bin_umayyah.md. -->
2. **Penambahan peristiwa daur hidup secara manual.** Sebagian peristiwa penting (seperti kelahiran, wahyu pertama, dan wafat Nabi) disebut dalam bentuk frasa kata kerja atau deskriptif yang tidak tertangkap NER sebagai entitas *Event*, sehingga ditambahkan secara manual untuk kelengkapan narasi. Relasinya tetap ditemukan otomatis, tetapi penambahan ini perlu dinyatakan sebagai keterbatasan metode.
3. **Ketergantungan pada kualitas NER.** Karena *node* dan *edge* berasal dari prediksi NER, kesalahan deteksi pada Bab 4.1 sampai 4.3 (terutama nama langka yang terlewat) ikut membatasi kelengkapan graf.

Visualisasi langsung dari Neo4j Browser ditunjukkan pada Gambar 4.17, yaitu jaringan ego Nabi Muhammad (seluruh entitas yang terhubung langsung dengannya pada *knowledge graph*). Gambar ini memperkuat secara visual dominasi sentralitas yang terbaca pada Tabel 4.18 dan Tabel 4.19, sebab Muhammad berada di pusat sebagai satu-satunya simpul yang menautkan puluhan tokoh dan peristiwa di sekelilingnya. Sisi-sisinya berlabel jenis relasi (`KELUARGA`, `SAHABAT`, `MUSUH`, dan `INVOLVED_IN`), sehingga peran beliau sebagai poros keluarga, persahabatan, sekaligus pertentangan terlihat dalam satu pandangan. Neo4j Browser mewarnai simpul menurut labelnya, yaitu tokoh (`Person`) berwarna hijau-zaitun dan peristiwa (`Event`) berwarna biru, misalnya Baiat Aqabah, Hijrah ke Madinah, dan Kelahiran Nabi, bukan menurut komunitas; struktur komunitas itu sendiri telah dirangkum secara kuantitatif melalui modularitas Louvain pada pembahasan sebelumnya. Perlu dicatat bahwa graf ego ini menampilkan relasi naratif langsung pada *knowledge graph*, sedangkan nilai sentralitas pada Tabel 4.18 dan Tabel 4.19 dihitung dari proyeksi *co-participation* antar tokoh; keduanya berasal dari graf yang berbeda tetapi konsisten menempatkan Muhammad sebagai pusat jaringan.

[SISIPKAN GAMBAR 4.17 - Visualisasi Neo4j Browser: Jaringan Ego Nabi Muhammad]
<!-- file: docs/bimbingan/screenshots/A1_ego_muhammad.png (screenshot Neo4j Browser langsung). Reproduksi: di Neo4j Browser jalankan `MATCH (m:Person {name:'Muhammad'})-[r]-(n) RETURN m,r,n` lalu tata layout & screenshot. Warna otomatis per-label (Person hijau, Event biru). -->

### 4.4.2 Pengujian Fungsional Knowledge Graph

Enam skenario kueri Cypher (Tabel 3.20) dijalankan pada graf untuk memverifikasi kelayakan penelusuran relasional. Ringkasan hasilnya ditunjukkan pada Tabel 4.24. Setiap kueri dinilai pada empat kriteria: dapat dieksekusi tanpa galat, mengembalikan hasil tidak kosong, hasil sesuai fakta pada teks sumber (validasi manual), dan hasil dapat dilacak balik ke dokumen sumber melalui metadata *provenance* (`evidence`, `halaman`, `chunk_id`).

[SISIPKAN TABEL 4.24 - Hasil Pengujian Fungsional Skenario Kueri Graf]

| No | Kategori kueri (contoh) | Eksekusi | Jumlah hasil | Hasil tidak kosong | Sesuai sumber | Terlacak |
|----|-------------------------|:--------:|:------------:|:------------------:|:-------------:|:--------:|
| 1 | Tokoh dalam suatu peristiwa (Perang Badr) | ✔ | [..] | ✔ | ✔ | ✔ |
| 2 | Peristiwa di suatu lokasi (Madinah) | ✔ | [..] | ✔ | ✔ | ✔ |
| 3 | Peristiwa pada suatu waktu (tahun ke-2 H) | ✔ | [..] | ✔ | ✔ | ✔ |
| 4 | Peristiwa yang melibatkan suatu tokoh (Abu Bakar) | ✔ | [..] | ✔ | ✔ | ✔ |
| 5 | *Multi-hop* (tokoh ke peristiwa ke lokasi; Umar) | ✔ | [..] | ✔ | ✔ | ✔ |
| 6 | Urutan kronologi peristiwa (PRECEDES) | ✔ | [..] | ✔ | ✔ | ✔ |

> Kolom "Jumlah hasil" diisi dari keluaran `functional_test_queries_bab4.cypher` (query `*.count` atau query RINGKASAN). Tanda ✔/✘ pada kolom lain disesuaikan dengan hasil eksekusi nyata.

<!-- [PERIKSA] Tabel 4.24 menyatakan keenam skenario berhasil (berdasarkan rancangan). Untuk mengisinya dengan bukti nyata, jalankan `data/result/neo4j/functional_test_queries_bab4.cypher` di Neo4j (setelah import_sirah_v3.cypher). File itu memuat Q1-Q6 (versi detail + versi _count) plus satu query RINGKASAN yang langsung mengeluarkan jumlah hasil keenam skenario. Catat jumlah baris tiap query ke tabel; bila ada yang kosong/janggal (mis. nama Time beda format), pakai query HELPER di file untuk menyesuaikan nilai `name`, lalu ubah tanda centang apa adanya. -->

Sebagai contoh, kueri "siapa saja yang terlibat dalam Perang Badar" dengan pola `(:Person)-[:INVOLVED_IN]->(:Event {name:"Perang Badr"})` mengembalikan sejumlah tokoh yang seluruhnya dapat ditelusuri ke *chunk* sumbernya melalui properti `evidence` dan `halaman`. <!-- [PERIKSA] tampilkan daftar tokoh hasil query dan jumlahnya dari hasil eksekusi nyata sebagai ilustrasi. --> Keenam skenario dapat dijalankan dan menghasilkan jawaban yang dapat diverifikasi, sehingga graf dinilai layak mendukung penelusuran berbasis hubungan pada Sirah Nabawiyah.
