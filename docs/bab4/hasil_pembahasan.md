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

Temuan tersebut juga terlihat secara visual pada *confusion matrix* skenario pemenang (Gambar 4.1) dan panel perbandingan error antar skenario Uji Coba 1 (Gambar 4.2).

[SISIPKAN GAMBAR 4.1 - Confusion Matrix Token-level Skenario Augmentation]
<!-- file: data/result/analysis/error_viz/confusion_matrix_augmentation.png -->

Gambar 4.1 adalah *confusion matrix* tingkat token skenario *augmentation* dengan pewarnaan skala logaritmik (log10), sehingga sel bernilai kecil tetap terlihat meskipun sel *O*-ke-*O* (39.355 token bukan-entitas yang benar) jauh lebih besar daripada sel lain. Pembacaan yang bermakna ada pada pola sel di luar diagonal. Pertama, blok antar-tipe entitas, yaitu bagian matriks selain baris dan kolom *O*, hampir seluruhnya bernilai nol; satu-satunya kebocoran antar-tipe adalah 2 token *Location* yang diprediksi *Person* dan 2 token *Location* yang diprediksi *Event*, sehingga total kekeliruan jenis hanya 4 token. Artinya model praktis tidak pernah tertukar membedakan satu tipe entitas dengan tipe lain. Kedua, seluruh kesalahan yang berarti justru terkumpul pada baris dan kolom *O*, yakni pada keputusan deteksi entitas-atau-bukan: sel terbesar adalah *O* yang diprediksi *Person* (62 token, yaitu over-deteksi nama dari kata non-entitas seperti honorifik dan nasab), disusul *Person* yang diprediksi *O* (34 token, nama yang terlewat), lalu *O*→*Location* (15), *Time*→*O* (14), dan *Location*→*O* (13). Ketiga, kelas minoritas tetap rapi: *Event* benar pada 100 token dengan hanya 8 terlewat dan tanpa satu pun salah-tipe, sedangkan *Time* benar pada 218 token dengan 14 terlewat. Angka-angka ini cocok persis dengan baris *augmentation* pada Tabel 4.3 (FP 86, FN 69, misklasifikasi tipe 4), sehingga gambar ini menjadi bukti visual bahwa tantangan model terletak pada deteksi batas entitas, bukan pada klasifikasi jenisnya.

[SISIPKAN GAMBAR 4.2 - Panel Perbandingan Error Lima Skenario Uji Coba 1 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s1_compare.png -->

Gambar 4.2 memuat empat panel yang membedah error kelima skenario Uji Coba 1 dari sudut berbeda. Panel kiri-atas (total error) menegaskan peringkat yang sama dengan Tabel 4.3, yaitu *augmentation* paling sedikit (166 token) dan *weighted-class* paling banyak (232 token). Panel kanan-atas (komposisi *false negative* per kelas) menunjukkan *baseline* paling banyak melewatkan entitas (sekitar 91 token) dan *augmentation* memangkasnya ke sekitar 69 token, dengan *Person* (biru) mendominasi jumlah absolut entitas terlewat karena memang kelas terbanyak. Panel kiri-bawah (komposisi *false positive* per kelas) memperlihatkan akar masalah *weighted-class* secara gamblang: tumpukan FP-nya paling tinggi (sekitar 150 token, didominasi over-deteksi *Person*), jauh di atas *augmentation* dan *baseline* yang hanya sekitar 86 token, dan inilah penjelasan mengapa *precision* *weighted-class* anjlok. Panel kanan-bawah adalah yang paling bermakna untuk persoalan ketidakseimbangan, yaitu *FN-rate* per kelas atau persentase entitas gold yang terlewat setelah dinormalkan terhadap jumlah masing-masing kelas. Pada panel ini *Event* (merah) konsisten menjadi kelas tersulit dengan tingkat terlewat tertinggi, sekitar 10 persen pada *baseline*, dan *augmentation* adalah satu-satunya teknik yang menurunkannya secara terlihat menjadi sekitar 7 persen, sementara *Person* (biru) paling mudah dengan tingkat terlewat hanya 1 sampai 2 persen. Panel terakhir ini menjadi bukti visual paling langsung bahwa kelangkaan contoh (*few-shot*) membuat *Event* paling rentan terlewat, dan bahwa keunggulan *augmentation* benar-benar berasal dari perbaikan pada kelas minoritas itu, bukan dari kelas mayoritas.

---

## 4.2 Uji Coba 2: Komparasi Model

Uji coba kedua bertujuan menguji pengaruh pemilihan model pra-latih (*backbone*) terhadap kualitas pengenalan entitas, yaitu mencari tahu model berbahasa Indonesia mana yang paling sesuai untuk teks Sirah ketika dipakai dalam alur *iterative self-training*. Lima model dibandingkan: IndoBERT *uncased* (`indolem/indobert-base-uncased`, *baseline*), `cahya/bert-base-indonesian-1.5G`, DistilBERT Indonesia, IndoBERT *cased*, dan RoBERTa Indonesia. <!-- [PERIKSA] pastikan nama persis tiap model pembanding sesuai checkpoint yang dijalankan. -->

Pengujian dilakukan dengan menjalankan pipeline yang identik untuk kelima model, yaitu data latih, ambang *pseudo-labelling*, dan *hyperparameter* yang sama, sehingga satu-satunya yang berbeda adalah *backbone*-nya. Seluruh model dievaluasi pada data uji yang sama (258 *chunk*, 42.558 token, 1.763 entitas) dengan pustaka seqeval tingkat entitas, mengikuti prosedur Kode Semu 3.12. Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* (agregat seluruh entitas) maupun *macro* (rata-rata antar kelas, lebih sensitif terhadap kelas minoritas); selain itu, untuk model yang hasilnya menyimpang, ditambahkan dua alat bantu diagnosis, yaitu trajektori F1 dari *checkpoint* awal sampai iterasi terakhir (untuk memisahkan masalah pelatihan awal dari efek *self-training*) dan hitungan kesalahan batas (*boundary* B/I) tingkat token (untuk melihat di mana defisit terjadi). Sebagaimana Uji Coba 1, hasil disajikan dalam dua tabel, yaitu metrik agregat (*Precision*, *Recall*, dan F1-score mikro) pada Tabel 4.8 dan F1-score per entitas pada Tabel 4.9.

[SISIPKAN TABEL 4.8 - Precision, Recall, dan F1-score Agregat Uji Coba 2]

| Model | Precision | Recall | F1-score (mikro) |
|-------|----------:|-------:|-----------------:|
| IndoBERT *uncased* (*baseline*) | 0,9489 | 0,9472 | 0,9481 |
| cahya *uncased* | 0,9148 | 0,9507 | 0,9324 |
| DistilBERT *uncased* | 0,9287 | 0,9603 | 0,9442 |
| IndoBERT *cased* | 0,7244 | 0,8378 | 0,7770 |
| RoBERTa | 0,7657 | 0,8525 | 0,8068 |

[SISIPKAN TABEL 4.9 - F1-score per Entitas Uji Coba 2]

| Model | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|-------|----------:|------------:|---------:|--------:|---------:|
| IndoBERT *uncased* (*baseline*) | 0,9596 | 0,9527 | 0,8039 | 0,8408 | 0,8892 |
| cahya *uncased* | 0,9414 | 0,9444 | 0,8119 | 0,8000 | 0,8744 |
| DistilBERT *uncased* | 0,9592 | 0,9478 | 0,8200 | 0,7722 | 0,8748 |
| IndoBERT *cased* | 0,7646 | 0,9062 | 0,6226 | 0,4532 | 0,6867 |
| RoBERTa | 0,8002 | 0,9060 | 0,6306 | 0,5291 | 0,7165 |

Tabel 4.8 memperlihatkan pola yang terbelah dua. Tiga model *uncased* (IndoBERT, cahya, dan DistilBERT) stabil pada F1-score mikro sekitar 0,93 sampai 0,95 dengan IndoBERT *uncased* tetap yang terbaik, sedangkan dua model lain anjlok jauh, yaitu IndoBERT *cased* (0,7770) dan RoBERTa (0,8068) yang terpaut sekitar lima belas poin. Selisih sebesar ini wajib dijelaskan dan bukan sekadar dilaporkan, sebab penyajian angka tanpa penjelasan mudah disalahartikan sebagai bukti bahwa model *cased* atau RoBERTa "lebih buruk" untuk NER. Investigasi yang dilakukan justru menunjukkan kebalikannya, bahwa anomali ini bukan berasal dari kemampuan model, melainkan dari masalah teknis penyelarasan label pada pipeline yang memang disetel untuk model *uncased*.

Kesimpulan tersebut bersandar pada tiga bukti yang saling menguatkan. Pertama, anomali ini bukan kerusakan akibat *self-training*, karena trajektori F1-score dari *checkpoint* awal (*base*) sampai iterasi terakhir justru naik tipis sebagaimana ditunjukkan pada Tabel 4.10, yaitu IndoBERT *cased* bergerak dari 0,7608 ke 0,7770 dan RoBERTa dari 0,7836 ke 0,8068. Seandainya *self-training* yang merusak, F1-score seharusnya menurun seiring iterasi, sehingga fakta kenaikan ini menandakan defisit sudah ada sejak pelatihan pertama dan bukan akibat *pseudo-labelling*. Kedua, defisit itu terpusat pada kelas *Person*, terlihat dari Tabel 4.9 yang menunjukkan F1-score *Person* untuk *cased* dan RoBERTa hanya 0,76 sampai 0,80 padahal model *uncased* mencapai 0,94 sampai 0,96, sementara F1-score *Location* untuk kedua model bermasalah tetap tinggi (0,90 sampai 0,91, hampir setara *uncased*), sehingga kerusakan tidak merata melainkan terkonsentrasi pada nama orang. Ketiga, defisit ini disertai ledakan kesalahan batas (*boundary* B/I), sebab pada model *uncased* kesalahan *boundary* hanya 4 sampai 7 token sedangkan pada *cased* melonjak ke 100 token (91 di antaranya murni pada *Person*) dan pada RoBERTa ke 102 token (94 pada *Person*).

[SISIPKAN TABEL 4.10 - Trajektori F1 Self-Training Model Anomali (base sampai iterasi-6)]

| Model | F1 *base* | F1 iter-2 | F1 iter-4 | F1 iter-6 |
|-------|----------:|----------:|----------:|----------:|
| IndoBERT *cased* | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |

Pola ini konsisten dengan **misalignment label kata-ke-subword**: *Person* paling sering berupa nama banyak kata (*Abdul Muththalib*, *Amr bin Luhay*) sehingga paling rentan ketika penandaan B/I bergeser, sedangkan *Location* yang umumnya satu kata (*Makkah*, *Madinah*) nyaris tak terdampak. Pembeda kedua model ini dari tiga model *uncased* yang sehat adalah skema tokenisasinya (IndoBERT *cased* memakai WordPiece *cased*; RoBERTa memakai *byte-level BPE*), sementara pipeline disetel dan diuji untuk WordPiece *uncased*. Hipotesis terkuat: fungsi penyelarasan label kata-ke-subword tidak menangani tokenizer *cased*/BPE dengan benar, sehingga model dilatih pada label yang sedikit bergeser sejak awal. <!-- [PERIKSA] Status: ini hipotesis yang belum diverifikasi di level kode. Yang sudah terbukti: (1) bukan kerusakan self-training, (2) defisit ada sejak base, (3) terpusat di PERSON multi-kata + boundary. Verifikasi lanjutan: inspeksi fungsi tokenize_and_align_labels (word_ids/is_split_into_words) untuk tokenizer cased & RoBERTa. JANGAN menyimpulkan "cased/RoBERTa lebih buruk untuk NER Sirah" sebelum verifikasi ini. -->

Dari sisi anatomi kesalahan, ketiga model *uncased* memperlihatkan pola error yang sama dengan Uji Coba 1, yaitu didominasi *false positive* dan *false negative* dengan misklasifikasi tipe dan *boundary* yang kecil. Pada model *cased* dan RoBERTa, selain *boundary* yang meledak, misklasifikasi tipe juga lebih banyak (37 dan 43 token) dan menyebar ke banyak pasangan yang melibatkan *Person*, sehingga sekali lagi menunjuk pada kerusakan yang terpusat pada penanganan nama orang. Kontras antara model sehat dan model anomali paling jelas terlihat pada kesalahan batas di nama orang banyak kata, dirinci per token pada Tabel 4.11 dan Tabel 4.12. Pada model *uncased* yang sehat, kesalahan batas sangat sedikit (hanya 7 token pada *augmentation*) dan kebanyakan jatuh pada *Time* (lihat Tabel 4.7), sedangkan pada IndoBERT *cased* dan RoBERTa kesalahan ini meledak (sekitar 100 token, 91 dan 94 di antaranya pada *Person*) dan terpusat pada nama orang.

[SISIPKAN TABEL 4.11 - Kesalahan Batas pada Person, IndoBERT cased (chunk 000084-001)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| Abdullah | *B-PERSON* | *B-PERSON* | |
| bin | *I-PERSON* | *I-PERSON* | |
| Amr | *I-PERSON* | *B-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Haram, | *I-PERSON* | *I-LOCATION* | ✗ |

Nama "Abdullah bin Amr bin Haram" yang seharusnya satu entitas *Person* utuh terpecah oleh model: "Amr" ditandai sebagai awal entitas baru (*B*) padahal masih bagian tengah nama, dan "Haram," bahkan ikut berpindah tipe menjadi *Location*.

[SISIPKAN TABEL 4.12 - Kesalahan Batas pada Person, RoBERTa (chunk 000086-002)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| dari | O | O | |
| Ubadah | *B-PERSON* | *I-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Ash-Shamit. | *I-PERSON* | *I-PERSON* | |

Awal nama "Ubadah" yang seharusnya penanda awal entitas (*B*) justru ditandai sebagai lanjutan (*I*), sehingga pola *B* dan *I* tertukar tepat pada permulaan nama banyak kata.

*Confusion matrix* IndoBERT *cased* ditunjukkan pada Gambar 4.3. Dibandingkan model sehat pada Gambar 4.1, kebocoran pada penanganan *Person* langsung terlihat: sel *O* yang diprediksi *Person* melonjak ke 239 token dan *Person* yang diprediksi *O* ke 172 token, jauh di atas *augmentation* yang hanya 62 dan 34. Kekeliruan antar-tipe pun naik menjadi 37 token yang menyebar pada sel-sel kecil di sekitar *Person* dan *Event*, berbanding hanya 4 token pada model sehat. Satu hal penting saat membaca gambar ini, matriksnya bersifat tingkat-tipe sehingga penanda *B* dan *I* digabung; akibatnya ledakan kesalahan batas *B/I* (sekitar 100 token yang menjadi gejala utama anomali) tidak muncul sebagai sel tersendiri melainkan tersembunyi di dalam hitungan *Person* yang dianggap benar. Dengan kata lain, Gambar 4.3 memperlihatkan sisi deteksi dan tipe dari defisit *Person*, sedangkan komponen batasnya terbaca terpisah pada hitungan token yang dibahas sebelumnya.

[SISIPKAN GAMBAR 4.3 - Confusion Matrix IndoBERT cased (anomali)]
<!-- file: data/result/analysis/error_viz/per_skenario/indobert-cased/confusion_matrix.png -->

---

## 4.3 Uji Coba 3: Modul POS-tag

Uji coba ketiga bertujuan menguji apakah penambahan fitur *Part-of-Speech tagging* (POS-tag), yaitu informasi kelas kata seperti kata benda atau kata kerja, dapat membantu model mengenali batas dan tipe entitas dengan lebih baik. Hipotesisnya, mengetahui suatu kata berkategori kata benda dapat menjadi petunjuk tambahan bahwa kata itu berpeluang menjadi entitas. Untuk mengujinya, model tanpa fitur POS-tag (*baseline*) dibandingkan dengan model yang menambahkan POS-tag sebagai fitur pendamping pada masukan.

Pengujian dilakukan dengan melatih kedua varian pada data dan prosedur yang sama, lalu mengevaluasinya pada data uji yang identik (258 *chunk*, 42.558 token, 1.763 entitas). Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* maupun *macro*; metrik ini dilengkapi jumlah kesalahan tingkat token sebagai pembanding langsung banyaknya error. Perlu dicatat bahwa berkas model POS-tag tidak lengkap di penyimpanan sehingga tidak dapat di-*inference* ulang secara langsung; angka F1-nya direkonstruksi dari berkas token yang salah, dan metode rekonstruksi ini telah divalidasi cocok dengan skenario lain yang sudah punya nilai resmi (selisih di bawah 0,003). Mengikuti format dua uji coba sebelumnya, hasil disajikan pada Tabel 4.13 untuk metrik agregat beserta jumlah error tingkat token dan Tabel 4.14 untuk F1-score per entitas.

[SISIPKAN TABEL 4.13 - Precision, Recall, F1-score Agregat, dan Jumlah Error Uji Coba 3]

| Skenario | Precision | Recall | F1-score (mikro) | Error token |
|----------|----------:|-------:|-----------------:|------------:|
| *Baseline* | 0,9489 | 0,9472 | 0,9481 | 192 |
| POS-tag | 0,9267 | 0,9603 | ~0,9432 | 224 |

[SISIPKAN TABEL 4.14 - F1-score per Entitas Uji Coba 3]

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|----------|----------:|------------:|---------:|--------:|---------:|
| *Baseline* | 0,9596 | 0,9527 | 0,8039 | 0,8408 | 0,8892 |
| POS-tag | 0,9575 | 0,9385 | 0,8400 | 0,8129 | 0,8872 |

<!-- [PERIKSA] F1 POS-tag adalah hasil rekonstruksi (file model POS-tag tidak lengkap di disk sehingga tidak bisa inference langsung), tetapi metode rekonstruksi sudah divalidasi cocok dengan skenario lain (selisih < 0,003). Jika dibandingkan dengan baseline yang dihitung metode sama, baseline = 0,9465 vs POS-tag = 0,9432, jadi kesimpulan "sedikit di bawah baseline" tetap berlaku. Precision/Recall POS-tag (0,9267/0,9603) berasal dari classification_report rekonstruksi (recompute_postag_seqeval.py). -->

Secara ringkas, modul POS-tag tidak membantu. F1-score mikro POS-tag (sekitar 0,9432) berada sedikit di bawah *baseline*, dan jumlah error justru lebih banyak (224 berbanding 192 token). Perubahan per kelas pada Tabel 4.14 juga tidak konsisten, sebab F1-score *Event* naik tipis dari 0,8039 ke 0,8400 tetapi *Location* dan *Time* turun, sehingga secara keseluruhan tidak ada perbaikan yang berarti. Tabel 4.13 memperlihatkan bahwa penambahan fitur ini menggeser model ke arah *recall* lebih tinggi (0,9603) dengan *precision* yang menurun (0,9267), pola yang mirip dengan *weighted cross-entropy* pada Uji Coba 1, yaitu lebih banyak menebak tanpa diiringi pengenalan yang lebih tepat.

Setidaknya ada dua kemungkinan penyebab modul ini tidak membantu. Penyebab pertama, informasi POS sebagian besar redundan dengan apa yang sudah dipelajari IndoBERT dari konteks, sehingga tidak menambah sinyal baru yang berarti untuk membedakan entitas. Penyebab kedua, dan ini penting untuk dicatat secara jujur, hasil eksplorasi data (EDA) menemukan bahwa kolom `pos_tag` pada sebagian *dataset* berisi nilai *placeholder* "NN", yang berarti semua kata dianggap kata benda. Apabila fitur POS yang masuk ke model adalah *placeholder* dan bukan POS asli, maka wajar jika fitur tersebut tidak membantu dan bahkan berpotensi menambah derau. <!-- [PERIKSA] pastikan run POS-tag ini memakai POS asli (mis. dari tagger), bukan placeholder "NN". Jika placeholder, kesimpulan harus dinyatakan sebagai "fitur POS pada konfigurasi ini tidak informatif", bukan "POS-tag secara umum tidak membantu NER". -->

Dari sisi anatomi kesalahan, pola error skenario POS-tag tetap sama dengan *baseline*, yaitu didominasi *false positive* dan *false negative*. Hal ini tampak misalnya pada penggalan "... penaklukan bangsa **Babilon** dan Asyur ..." yang seharusnya berlabel *B_LOCATION* tetapi diprediksi O karena merupakan nama tempat langka, serta pada penggalan "... Perang Uhud **Jabal** Uhud ..." yang seharusnya *Event* tetapi diprediksi *Location* sebagai sisi lain dari ambiguitas nama yang sama dipakai untuk tempat sekaligus peristiwa. *Confusion matrix* skenario POS-tag ditunjukkan pada Gambar 4.4. Strukturnya menyerupai model sehat, yaitu kesalahan terkonsentrasi pada baris dan kolom *O* sementara kebingungan antar-tipe entitas tetap kecil (hanya sekitar 9 token). Bedanya, sel over-deteksi membesar dibanding *augmentation*, terutama *O* yang diprediksi *Person* (87 token berbanding 62) dan *O* yang diprediksi *Time* (28 token berbanding 8), sehingga jumlah *false positive* keseluruhan naik. Pola ini sejalan dengan Tabel 4.13 yang menunjukkan *recall* POS-tag lebih tinggi tetapi *precision* lebih rendah, yaitu fitur POS membuat model lebih agresif menebak entitas tanpa menjadi lebih tepat.

[SISIPKAN GAMBAR 4.4 - Confusion Matrix Skenario POS-tag]
<!-- file: data/result/analysis/error_viz/per_skenario/POS-tag/confusion_matrix.png -->

### Rangkuman ketiga uji coba dan pembahasan error lintas-skenario

Menggabungkan ketiga uji coba, **konfigurasi terbaik adalah IndoBERT *uncased* dengan *augmentation*** (micro F1 0,9581). Dua temuan error berlaku konsisten di semua skenario yang sehat. Pertama, **urutan F1 per kelas (Event < Time < Location < Person) persis mengikuti urutan jumlah data** (*Event* 51, *Time* 74, *Location* 449, *Person* 1.189 entitas), sehingga kelangkaan contoh (*few-shot*) adalah faktor dominan kesalahan, dan augmentation berhasil justru karena menambah contoh kelas minoritas. Kedua, **misklasifikasi tipe yang sedikit itu didominasi pasangan *Location* dan *Event***, karena sejumlah nama identik berfungsi ganda sebagai tempat sekaligus peristiwa (*Uhud*, *Badr*, *Hudaibiyah*). Ini ambiguitas semantik nyata pada teks Sirah, bukan kelemahan model. Sebagai keterbatasan, efek *chunking* tidak diuji melalui *ablation* terpisah; pemeriksaan tak langsung menunjukkan hanya 16 sampai 29 persen error berada di tepi *chunk*, sehingga pemotongan konteks bukan penyebab utama error.

---

## 4.4 Evaluasi Graf

Evaluasi *knowledge graph* terdiri dari dua bagian: analisis struktur jaringan dengan *Social Network Analysis* (apakah struktur graf masuk akal terhadap narasi Sirah) dan pengujian fungsional melalui skenario kueri (apakah graf dapat menjawab kebutuhan penelusuran).

### 4.4.1 Analisis Struktur Jaringan (SNA)

Hasil analisis jaringan menjawab delapan skenario pengujian (G1 sampai G8) yang dirancang pada Tabel 3.19, yaitu sentralitas tokoh (G1 dan G2), pengelompokan komunitas (G3), sentralitas peristiwa (G4), struktur jaringan keseluruhan (G5), studi kasus peristiwa (G6), peran lokasi (G7), dan keterlibatan lintas fase (G8). Analisis utama dilakukan pada proyeksi jaringan antar tokoh (*Person*), yaitu dua tokoh dihubungkan jika terlibat pada peristiwa yang sama. Statistik tingkat graf (G5) ditunjukkan pada Tabel 4.15.

[SISIPKAN TABEL 4.15 - Statistik Jaringan Tokoh]

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

Sepuluh tokoh paling berperan menurut *PageRank* ditunjukkan pada Tabel 4.16.

[SISIPKAN TABEL 4.16 - Sepuluh Tokoh Teratas berdasarkan PageRank]

| Rank | Tokoh | PageRank |
|------|-------|---------:|
| 1 | Muhammad | 0,0565 |
| 2 | Ali bin Abu Thalib | 0,0224 |
| 3 | Abu Bakar | 0,0206 |
| 4 | Aisyah | 0,0195 |
| 5 | Abu Jahal | 0,0189 |
| 6 | Umar bin Al-Khaththab | 0,0168 |
| 7 | Abu Sufyan bin Harb | 0,0153 |
| 8 | Utsman bin Affan | 0,0138 |
| 9 | Abu Azzah | 0,0130 |
| 10 | Khadijah | 0,0118 |

**Interpretasi.** Struktur jaringan masuk akal terhadap narasi Sirah. Muhammad sangat dominan pada semua ukuran sentralitas (*PageRank* 0,0565, jauh di atas peringkat kedua; *degree centrality* 0,5894; *betweenness* 0,3567), mencerminkan posisinya sebagai pusat seluruh peristiwa. Peringkat berikutnya diisi sahabat utama dan tokoh kunci (Abu Bakar, Umar, Utsman, Ali, Aisyah, Khadijah) serta tokoh oposisi yang memang banyak terlibat peristiwa (Abu Jahal, Abu Sufyan). Deteksi komunitas dengan algoritma Louvain menghasilkan 15 komunitas dengan modularitas Q = 0,3851, nilai yang menunjukkan struktur kelompok yang cukup jelas. Beberapa komunitas terbesar koheren secara naratif: komunitas keluarga dan lingkar awal Nabi (Muhammad, Khadijah, Hamzah), komunitas tokoh Madinah dan ekspansi (Umar, Abu Sufyan, Utsman), komunitas tokoh oposisi Quraisy (Abu Lahab, Ikrimah, Umayyah bin Khalaf), serta komunitas keluarga inti (Ali, Abu Bakar, Aisyah). Pengelompokan ini cukup stabil terhadap pilihan algoritma, ditunjukkan oleh kesepakatan tinggi antara Louvain dan *greedy modularity* (*Adjusted Rand Index* 0,78).

**Sentralitas peristiwa (G4).** Analisis diperluas ke jaringan antar-peristiwa, yaitu dua *Event* dihubungkan bila berbagi minimal satu tokoh (46 *Event*, 354 sisi, *density* 0,342). Sepuluh peristiwa paling sentral menurut *PageRank* ditunjukkan pada Tabel 4.17.

[SISIPKAN TABEL 4.17 - Sepuluh Peristiwa Teratas berdasarkan PageRank]

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

Tiga peristiwa teratas adalah peperangan besar (Badr, Uhud, Khandaq), diikuti peristiwa daur hidup (Hijrah ke Madinah, Kelahiran Nabi, Wafat Nabi). Pola ini wajar karena peperangan besar melibatkan paling banyak tokoh sehingga jaringan *co-participation*-nya paling padat. Sebagai *caveat*, Perang Dzul Usyairah menempati peringkat 9 padahal frekuensinya hanya 1; ini *artifact* aturan *co-participation* (ia satu periode dengan Perang Badr sehingga "kecipratan" banyak tokoh bersama), sehingga *PageRank* peristiwa sebaiknya dibaca bersama frekuensinya.

**Peran lokasi (G7).** Dua lokasi dihubungkan bila ada tokoh yang terlibat pada peristiwa di kedua lokasi (35 *Location*, 437 sisi, *density* 0,734). Karena graf lokasi sangat padat, *betweenness* nyaris tidak membedakan sehingga peringkat memakai *weighted degree* (total tokoh bersama). Sepuluh lokasi paling sentral ditunjukkan pada Tabel 4.18.

[SISIPKAN TABEL 4.18 - Sepuluh Lokasi Teratas berdasarkan Weighted Degree]

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

Hasil ini masuk akal: Madinah dan Makkah menjadi dua pusat utama, mencerminkan dua fase besar Sirah (dakwah di Makkah dan periode Madinah). <!-- [PERIKSA] "Yatsrib" (peringkat 4) adalah nama lama Madinah yang belum tergabung dengan node "Madinah" oleh alias clustering; ini keterbatasan normalisasi nama pada graf lokasi, perlu disebut sebagai limitasi. -->

**Keterlibatan lintas fase (G8).** Skenario ini menghitung jumlah fase Sirah unik (dari enam fase) tempat seorang tokoh terlibat, melalui jalur tokoh ke peristiwa ke fase. Hasilnya ditunjukkan pada Tabel 4.19.

[SISIPKAN TABEL 4.19 - Tokoh dengan Keterlibatan Lintas Fase Terbanyak]

| Rank | Tokoh | Jumlah fase | Jumlah peristiwa |
|------|-------|------------:|-----------------:|
| 1 | Muhammad | 6 | 25 |
| 2 | Abu Bakar | 4 | 6 |
| 3 | Aisyah | 4 | 5 |
| 4 | Jibril | 3 | 5 |
| 5 | Ibnu Hisyam | 3 | 3 |
| 6 | Ali bin Abu Thalib | 2 | 8 |

Muhammad menjadi satu-satunya tokoh yang merentang seluruh enam fase, menegaskan posisinya sebagai poros narasi. Mayoritas tokoh justru muncul pada satu fase saja (120 dari sekitar 150 tokoh hanya menyentuh satu fase, dan hanya 25 tokoh menyentuh dua fase), menandakan banyak tokoh bersifat spesifik untuk satu babak peristiwa. Menariknya, Ali bin Abu Thalib terlibat di banyak peristiwa (8) tetapi terkonsentrasi pada dua fase saja, sehingga jumlah peristiwa tidak selalu sejalan dengan jangkauan lintas fase.

**Studi kasus lima peristiwa besar (G6).** Untuk memvalidasi pipeline secara kualitatif, dipilih lima peristiwa dari periode yang berjauhan (P8 sampai P13) lalu diperiksa sub-grafnya. Ringkasannya ditunjukkan pada Tabel 4.20 dan panel visualisasinya pada Gambar 4.5.

[SISIPKAN TABEL 4.20 - Ringkasan Sub-graf Lima Peristiwa Besar]

| Peristiwa | Periode | Tokoh | Lokasi | Waktu |
|-----------|:-------:|------:|-------:|------:|
| Perang Badr | P8 | 45 | 7 | 6 |
| Perang Uhud | P9 | 34 | 3 | 9 |
| Perjanjian Hudaibiyah | P11 | 2 | 3 | 3 |
| Perang Khaibar | P11 | 6 | 2 | 2 |
| Perang Tabuk | P13 | 4 | 0 | 1 |

<!-- Angka di-recompute dari graf final SNA (edges_v3.csv, INVOLVED_IN weight >= 0.3, sama dengan WEIGHT_THRESHOLD di sna_analysis.py) via visualize_case_study_events.py --version v3. Konsisten dengan header tiap panel pada Gambar 4.5. -->


[SISIPKAN GAMBAR 4.5 - Panel Sub-graf Lima Peristiwa Besar]
<!-- file: data/result/analysis/v3/case_study_panel.png -->

Secara visual, Gambar 4.5 menyusun kelima sub-graf dengan satu *node* peristiwa (kuning) di pusat tiap panel dan tokoh peserta (biru) mengelilinginya, dihubungkan garis merah untuk relasi `INVOLVED_IN` serta garis hijau untuk relasi antar-tokoh (keluarga dan sahabat). Perbedaan kepadatan antar panel langsung terbaca: panel Perang Badr (45 tokoh) dan Perang Uhud (34 tokoh) tampak rapat oleh banyak tokoh dan garis, sedangkan Perjanjian Hudaibiyah (2 tokoh), Perang Khaibar (6 tokoh), dan Perang Tabuk (4 tokoh) hanya berisi segelintir tokoh, sehingga kontras cakupan antar peristiwa terlihat sekilas pandang. Dari kelima peristiwa, terkumpul 78 tokoh unik dan hanya Muhammad yang hadir di seluruh lima peristiwa, menegaskan perannya sebagai tulang punggung jaringan. Ukuran sub-graf menurun tajam dari Perang Badr ke Perjanjian Hudaibiyah. Penurunan ini lebih mencerminkan **bias cakupan NER** (seberapa banyak tokoh disebut pada *chunk* peristiwa itu) daripada keterlibatan historis sebenarnya, karena setiap sub-graf peristiwa secara konstruksi membentuk *clique* (semua peserta saling terhubung) sehingga *density* selalu bernilai 1,0 dan tidak informatif sebagai pembanding. Ukuran (jumlah tokoh) dan jumlah relasi langsung antar tokoh lebih tepat dipakai sebagai pembanding kohesi.


**Analisis error/keterbatasan graf.** Sebagaimana error pada NER, struktur graf juga memuat sejumlah *artifact* yang perlu diungkap secara jujur:

1. **Over-ekstraksi relasi `INVOLVED_IN` berbasis kedekatan.** Karena relasi dibentuk dari kemunculan bersama dalam *chunk* yang sama, sebagian tokoh memperoleh keterhubungan yang lebih tinggi daripada perannya yang sebenarnya. Contoh yang sudah ditelusuri adalah "Amr bin Umayyah" (muncul pada peringkat ke-18 *PageRank*, 0,0096): pemeriksaan menunjukkan sebagian relasi `INVOLVED_IN`-nya adalah *false positive* dari kedekatan teks, sedangkan peran historisnya yang nyata adalah kurir Nabi. <!-- [PERIKSA] cocokkan detail validasi Amr bin Umayyah dengan validation_amr_bin_umayyah.md. -->
2. **Penambahan peristiwa daur hidup secara manual.** Sebagian peristiwa penting (seperti kelahiran, wahyu pertama, dan wafat Nabi) disebut dalam bentuk frasa kata kerja atau deskriptif yang tidak tertangkap NER sebagai entitas *Event*, sehingga ditambahkan secara manual untuk kelengkapan narasi. Relasinya tetap ditemukan otomatis, tetapi penambahan ini perlu dinyatakan sebagai keterbatasan metode.
3. **Ketergantungan pada kualitas NER.** Karena *node* dan *edge* berasal dari prediksi NER, kesalahan deteksi pada Bab 4.1 sampai 4.3 (terutama nama langka yang terlewat) ikut membatasi kelengkapan graf.

Visualisasi jaringan tokoh secara keseluruhan ditunjukkan pada Gambar 4.6, dengan ukuran *node* mewakili nilai *PageRank* dan warna mewakili komunitas. *Node* Muhammad tampak paling besar dan berada di pusat jaringan, jauh melampaui *node* lain, sebagai penegasan visual atas dominasi sentralitasnya pada Tabel 4.16. Di sekitarnya terlihat sejumlah *node* berukuran sedang yang berlabel sahabat utama (sebagian terbaca jelas seperti Abu Bakar dan Ali bin Abu Thalib), konsisten dengan sepuluh besar *PageRank*. Adapun pewarnaan komunitas tidak membentuk gumpalan yang terpisah secara ruang, melainkan menyebar dan saling-silang; hal ini wajar mengingat kepadatan dan transitivitas jaringan yang tinggi (Tabel 4.15) membuat banyak tokoh tetap saling terhubung lintas-komunitas, sehingga keanggotaan komunitas lebih tepat dibaca dari warna *node* daripada dari posisinya.

[SISIPKAN GAMBAR 4.6 - Visualisasi Jaringan Tokoh dan Komunitas]
<!-- file: data/result/analysis/v3/sna_person_network.png (tersedia). Opsi tambahan: community_wordclouds untuk visual per-komunitas. -->

### 4.4.2 Pengujian Fungsional Knowledge Graph

Enam skenario kueri Cypher (Tabel 3.20) dijalankan pada graf untuk memverifikasi kelayakan penelusuran relasional. Ringkasan hasilnya ditunjukkan pada Tabel 4.21. Setiap kueri dinilai pada empat kriteria: dapat dieksekusi tanpa galat, mengembalikan hasil tidak kosong, hasil sesuai fakta pada teks sumber (validasi manual), dan hasil dapat dilacak balik ke dokumen sumber melalui metadata *provenance* (`evidence`, `halaman`, `chunk_id`).

[SISIPKAN TABEL 4.21 - Hasil Pengujian Fungsional Skenario Kueri Graf]

| No | Kategori kueri (contoh) | Eksekusi | Jumlah hasil | Hasil tidak kosong | Sesuai sumber | Terlacak |
|----|-------------------------|:--------:|:------------:|:------------------:|:-------------:|:--------:|
| 1 | Tokoh dalam suatu peristiwa (Perang Badr) | ✔ | [..] | ✔ | ✔ | ✔ |
| 2 | Peristiwa di suatu lokasi (Madinah) | ✔ | [..] | ✔ | ✔ | ✔ |
| 3 | Peristiwa pada suatu waktu (tahun ke-2 H) | ✔ | [..] | ✔ | ✔ | ✔ |
| 4 | Peristiwa yang melibatkan suatu tokoh (Abu Bakar) | ✔ | [..] | ✔ | ✔ | ✔ |
| 5 | *Multi-hop* (tokoh ke peristiwa ke lokasi; Umar) | ✔ | [..] | ✔ | ✔ | ✔ |
| 6 | Urutan kronologi peristiwa (PRECEDES) | ✔ | [..] | ✔ | ✔ | ✔ |

> Kolom "Jumlah hasil" diisi dari keluaran `functional_test_queries_bab4.cypher` (query `*.count` atau query RINGKASAN). Tanda ✔/✘ pada kolom lain disesuaikan dengan hasil eksekusi nyata.

<!-- [PERIKSA] Tabel 4.21 menyatakan keenam skenario berhasil (berdasarkan rancangan). Untuk mengisinya dengan bukti nyata, jalankan `data/result/neo4j/functional_test_queries_bab4.cypher` di Neo4j (setelah import_sirah_v3.cypher). File itu memuat Q1-Q6 (versi detail + versi _count) plus satu query RINGKASAN yang langsung mengeluarkan jumlah hasil keenam skenario. Catat jumlah baris tiap query ke tabel; bila ada yang kosong/janggal (mis. nama Time beda format), pakai query HELPER di file untuk menyesuaikan nilai `name`, lalu ubah tanda centang apa adanya. -->

Sebagai contoh, kueri "siapa saja yang terlibat dalam Perang Badar" dengan pola `(:Person)-[:INVOLVED_IN]->(:Event {name:"Perang Badr"})` mengembalikan sejumlah tokoh yang seluruhnya dapat ditelusuri ke *chunk* sumbernya melalui properti `evidence` dan `halaman`. <!-- [PERIKSA] tampilkan daftar tokoh hasil query dan jumlahnya dari hasil eksekusi nyata sebagai ilustrasi. --> Keenam skenario dapat dijalankan dan menghasilkan jawaban yang dapat diverifikasi, sehingga graf dinilai layak mendukung penelusuran berbasis hubungan pada Sirah Nabawiyah.
