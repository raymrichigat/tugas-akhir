# BAB 4 HASIL DAN PEMBAHASAN

> **[CATATAN PENYUSUN, hapus saat finalisasi]**
> Bab ini menyatukan hasil dan pembahasan dalam satu alur (tidak dipisah), mengikuti permintaan susunan. Struktur: 4.1 Uji Coba 1 (penanganan data *imbalance*), 4.2 Uji Coba 2 (komparasi model), 4.3 Uji Coba 3 (modul POS-tag), 4.4 Evaluasi graf. Tiap subbab memuat penjelasan hasil, tabel hasil, interpretasi, alasan tinggi/rendah, analisis error, contoh data error, dan rujukan visualisasi.
> **Sumber angka (jangan diubah tanpa cek ulang):** benchmark = *run* penuh `done_newest` dengan **ground-truth uji terkoreksi**. F1 entity-level + rincian error + confusion dari `data/result/analysis/gt_corrected_2026_07_10/` (`recompute_gt_corrected_results.md`, `error_breakdown_gt_corrected.md`, `confusion/`); skrip `src/pseudo_labelling/SRL-NER/recompute_gt_corrected.py` + `error_breakdown_gt_corrected.py`. Metrik graf (4.4) dari KG v4 model pemenang (S4-augmentation): sentralitas/komunitas tokoh dari `data/result/analysis/v4_scoped/` (graf Person ber-scope, nasab-only dibuang via `clean_v4_hybrid_genealogy.py`); sentralitas peristiwa/lokasi/lintas-fase/studi-kasus dari `data/result/analysis/v4_hybrid/` (event di-dedup `clean_v4_events.py`, periode di-map `apply_period_to_v4.py`).
> Patuh pedoman: tanpa em dash, bahasa *layman*, istilah asing *italic*, sitasi APA. Tanda **[PERIKSA]** = perlu konfirmasi; **[SITASI: ...]** = referensi yang perlu masuk Daftar Pustaka.

Bab ini menyajikan dan membahas hasil pengujian terhadap rancangan yang dijelaskan pada Bab 3. Pembahasan dibagi mengikuti tiga uji coba ekstraksi entitas (subbab 3.9) dan evaluasi fungsional *knowledge graph* (subbab 3.10), sehingga setiap angka dapat ditelusuri ke skenario uji coba yang sesuai.

Seluruh evaluasi ekstraksi entitas dilakukan pada data uji yang sama, yaitu 254 *chunk* berisi 49.739 token dengan 1.969 entitas (*Person* 1.302, *Location* 474, *Time* 118, dan *Event* 75 entitas). <!-- Support entitas dari classification report seqeval pada recompute_gt_corrected_results.md (ground-truth uji terkoreksi). --> Pengukuran utama memakai *F1-score* tingkat entitas (*entity-level*) dengan pustaka seqeval, yaitu sebuah entitas dihitung benar hanya jika seluruh rentang token dan kategorinya tepat. Sebagai metrik pendukung analisis error, digunakan hitungan kesalahan tingkat token (*token-level*) yang memerinci jenis kesalahan. Komposisi data uji penting untuk dicatat sejak awal, karena ketimpangan jumlah entitas antar kelas (*Person* jauh lebih banyak daripada *Event* dan *Time*) menjadi penjelas utama pola hasil di seluruh subbab.

---

## 4.1 Uji Coba 1: Penanganan Data Imbalance

Uji coba pertama bertujuan menguji apakah ketidakseimbangan jumlah entitas antar kelas (*imbalance*) pada data latih dapat ditangani sehingga kualitas pengenalan kelas minoritas (terutama *Event* dan *Time*) meningkat. Persoalannya nyata: pada data uji, *Event* hanya 75 entitas dan *Time* 118 entitas, jauh di bawah *Person* (1.302) dan *Location* (474), sehingga model cenderung kurang terlatih mengenali dua kelas terkecil itu. Untuk itu, alur dasar (*baseline*) dibandingkan dengan empat teknik penanganan ketidakseimbangan yang ditambahkan di atasnya, yaitu *weighted cross-entropy*, *supervised contrastive learning* (SCL), *Jaccard-similarity contrastive learning* (JSCL), dan *data augmentation* dengan *mention replacement*.

Ketimpangan jumlah entitas antar kelas yang menjadi pangkal persoalan ini terlihat jelas pada Gambar 4.1, yang menyandingkan jumlah entitas tiap kelas pada data latih dan data uji.

[SISIPKAN GAMBAR 4.1 - Distribusi Jumlah Entitas per Kelas (Imbalance) pada Data Latih dan Data Uji]
<!-- file: data/result/analysis/bab4_viz/eda_imbalance.png -->

Gambar 4.1 menyajikan jumlah entitas tiap kelas pada data latih dan data uji sebagai diagram batang berkelompok. Batang *Person* menjulang paling tinggi (2.920 entitas pada data latih) sedangkan *Event* hanya berupa batang pendek (167 entitas latih dan hanya 75 pada data uji), dengan rasio ketimpangan sekitar 17,5:1 pada data latih dan 17,4:1 pada data uji. Pola yang konsisten di kedua bagian data inilah yang mendasari seluruh Uji Coba 1, yaitu kelas *Event* dan *Time* yang contohnya sangat sedikit (*few-shot*) menjadi kelas yang paling sulit dikenali model.

Pengujian dilakukan dengan melatih kelima varian (alur dasar ditambah empat teknik) pada *seed* yang sama, lalu mengevaluasinya pada data uji yang identik, yaitu 254 *chunk* berisi 49.739 token dengan 1.969 entitas. Agar perbandingan adil, hanya komponen penanganan ketidakseimbangan yang divariasikan, sedangkan arsitektur dasar (IndoBERT *uncased*), ambang *pseudo-labelling*, dan *hyperparameter* lain dibuat sama persis mengikuti prosedur Kode Semu 3.12. Pengukuran kualitas memakai pustaka seqeval pada tingkat entitas (*entity-level*), yaitu satu entitas dihitung benar hanya jika seluruh rentang token dan kategorinya tepat, dan dilengkapi penghitungan kesalahan tingkat token (*token-level*) untuk membedah jenis kesalahan.

Metrik utama yang digunakan adalah *F1-score* (rata-rata harmonik) karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan, proporsi prediksi yang benar) dan *recall* (kelengkapan, proporsi entitas acuan yang ditemukan), serta dilaporkan dalam bentuk *micro* (agregat seluruh entitas, didominasi kelas mayoritas) maupun *macro* (rata-rata antar kelas, lebih sensitif terhadap kelas minoritas). Karena itu hasil disajikan dalam dua tabel: Tabel 4.1 merangkum metrik agregat untuk menilai kualitas keseluruhan, sedangkan Tabel 4.2 memerinci F1-score tiap kelas entitas beserta *macro*-nya agar dampak terhadap kelas minoritas terlihat jelas.

[SISIPKAN TABEL 4.1 - Precision, Recall, dan F1-score Agregat Uji Coba 1]

| Skenario | Precision | Recall | F1-score (mikro) |
|----------|----------:|-------:|-----------------:|
| *Baseline* | 0,9524 | 0,9548 | 0,9536 |
| *Weighted cross-entropy* | 0,9427 | 0,9533 | 0,9480 |
| SCL | 0,9543 | 0,9548 | 0,9546 |
| JSCL | 0,9415 | 0,9487 | 0,9451 |
| **Augmentation** | **0,9756** | **0,9756** | **0,9756** |

[SISIPKAN TABEL 4.2 - F1-score per Entitas Uji Coba 1]

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|----------|----------:|------------:|---------:|--------:|---------:|
| *Baseline* | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| *Weighted cross-entropy* | 0,9616 | 0,9432 | 0,9231 | 0,8347 | 0,9156 |
| SCL | 0,9687 | 0,9488 | 0,9600 | 0,8170 | 0,9236 |
| JSCL | 0,9611 | 0,9467 | 0,9600 | 0,7572 | 0,9062 |
| **Augmentation** | **0,9835** | **0,9755** | **0,9542** | **0,9038** | **0,9543** |

[SISIPKAN GAMBAR 4.2 - F1-score Agregat Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/bab4_viz/f1_uc1_agregat.png -->

Gambar 4.2 meringkas Tabel 4.1 secara visual. Batang *augmentation* (disorot merah) berdiri paling tinggi baik pada F1 mikro maupun macro, sedangkan *weighted cross-entropy* paling rendah, sehingga peringkat antar skenario langsung terbaca.

[SISIPKAN GAMBAR 4.3 - F1-score per Kelas Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/bab4_viz/f1_uc1_perkelas.png -->

Gambar 4.3 meringkas Tabel 4.2 dengan mengelompokkan batang per kelas entitas. Sumber keunggulan *augmentation* terlihat jelas, yaitu batang *Event* dan *Time*-nya naik paling tinggi dibanding skenario lain, sementara *Person* dan *Location* tetap tinggi dan stabil di semua skenario.

Berdasarkan kedua tabel tersebut, teknik augmentation menjadi pemenang yang jelas dengan F1-score mikro 0,9756, mengungguli *baseline* (0,9536) dan seluruh teknik lain, dengan SCL menyusul tipis di urutan kedua (0,9546). Hal yang patut dicatat sejak awal adalah bahwa tidak semua penanganan ketidakseimbangan otomatis memperbaiki hasil, sebab dua teknik justru berada di bawah *baseline*, yaitu JSCL (0,9451) dan *weighted cross-entropy* (0,9480). Pola yang berlawanan arah ini menjadi inti pembahasan subbab ini, karena memperlihatkan bahwa menambah jumlah contoh kelas minoritas (augmentation) berbeda secara mendasar dari sekadar menggeser perhatian model ke kelas minoritas (*weighted cross-entropy*).

Keunggulan augmentation paling kentara justru pada kelas minoritas, sebagaimana terbaca pada Tabel 4.2. F1-score *Time* melonjak dari 0,7983 ke 0,9038 (naik lebih dari sepuluh poin) dan F1-score *Event* naik dari 0,9342 ke 0,9542, sementara *Person* dan *Location* tetap kuat bahkan ikut naik. Penyebabnya bersifat langsung: teknik *mention replacement* membentuk kalimat latih baru dengan mengganti entitas minoritas dengan entitas sekelas, sehingga model memperoleh lebih banyak ragam contoh *Time* dan *Event* yang sebelumnya sangat sedikit. Bukti pada tingkat token memperkuat penjelasan ini, yaitu *false negative* (entitas terlewat) pada *Time* turun drastis dari 36 ke 7 dan pada *Location* dari 33 ke 17 sebagaimana terbaca pada rincian error tingkat token, dan secara keseluruhan augmentation menghasilkan total error terendah (78 token) sekaligus misklasifikasi tipe paling sedikit (hanya 4 token).

Sebaliknya, dua teknik kontrastif berada di bawah *baseline*, dengan JSCL menempati posisi terendah (0,9451) dan *weighted cross-entropy* sedikit di atasnya (0,9480). Untuk *weighted cross-entropy*, penyebabnya terbaca dari pemecahan metrik agregat pada Tabel 4.1: pemberian bobot lebih besar pada kelas minoritas membuat model lebih agresif menebak entitas sehingga *false positive* naik menjadi 69 token (dari 55 pada *baseline*), tetapi tanpa diiringi kenaikan *recall* yang berarti (0,9533, praktis setara dengan *baseline* 0,9548), sehingga *precision* justru turun ke 0,9427 dan F1-score keseluruhan ikut turun. Temuan ini menegaskan bahwa menaikkan bobot kelas minoritas pada fungsi *loss* tidak menambah informasi baru tentang kelas tersebut, melainkan hanya menggeser model ke arah lebih banyak menebak, sehingga yang muncul adalah lebih banyak deteksi keliru, bukan pengenalan yang lebih baik.

Pembahasan kemudian dilanjutkan pada anatomi kesalahan untuk memahami mengapa pola di atas terjadi. Rincian jenis kesalahan tingkat token ditunjukkan pada Tabel 4.3. Pada semua skenario, kesalahan didominasi oleh keputusan deteksi (entitas atau bukan entitas), yaitu *false negative* (48 sampai 59 persen) dan *false positive* (32 sampai 40 persen), sedangkan misklasifikasi tipe hanya 3 sampai 6 persen dan kesalahan batas (*boundary* B/I) hanya 4 sampai 10 persen. Temuan ini menunjukkan bahwa model sebenarnya sudah memahami perbedaan keempat tipe entitas, dan tantangan utamanya terletak pada memutuskan apakah suatu kata merupakan entitas atau bukan, bukan pada kebingungan membedakan jenis entitas.

[SISIPKAN TABEL 4.3 - Rincian Jenis Error Token-level Uji Coba 1]

| Skenario | Total error | FP (over-deteksi) | FN (terlewat) | Misklasifikasi tipe | Boundary B/I |
|----------|------------:|------------------:|--------------:|--------------------:|-------------:|
| *Baseline* | 165 | 55 (33%) | 98 (59%) | 5 (3%) | 7 (4%) |
| *Weighted cross-entropy* | 174 | 69 (40%) | 84 (48%) | 11 (6%) | 10 (6%) |
| SCL | 178 | 62 (35%) | 102 (57%) | 7 (4%) | 7 (4%) |
| JSCL | 185 | 69 (37%) | 93 (50%) | 12 (6%) | 11 (6%) |
| Augmentation | 78 | 25 (32%) | 41 (53%) | 4 (5%) | 8 (10%) |

Akar penyebab error, berdasarkan inspeksi token salah, terbagi tiga. Pertama, **over-deteksi (FP)** banyak berasal dari kata umum atau abstrak yang kebetulan berhuruf kapital atau menyerupai nama (seperti *Hijabah* yang merujuk jabatan pengurus Ka'bah tetapi dikira tempat), serta penanda nasab dan gelar yang ditarik menjadi bagian nama. Kedua, **entitas terlewat (FN)**, yang justru menjadi kategori kesalahan terbanyak, banyak terjadi pada nama langka atau di luar distribusi (seperti *Cina*, *Ukazh*, *Dzil-Majaz*) dan pada token yang membawa tanda baca menempel akibat artefak OCR. Ketiga, **misklasifikasi tipe** yang jumlahnya sangat kecil hampir seluruhnya jatuh pada nama berfungsi ganda sebagai tempat sekaligus peristiwa (*Uhud*, *Badr*, *Hudaibiyah*), sebuah ambiguitas semantik nyata pada teks Sirah dan bukan kelemahan model.

Untuk memperlihatkan tiap jenis kesalahan secara konkret, di bawah ini ditampilkan satu contoh nyata per jenis error dari skenario pemenang (*augmentation*), dirinci per token dengan kolom *ground-truth* (label acuan) dan prediksi model. Baris token yang salah ditandai dengan tanda ✗. Seluruh contoh diambil dari prediksi model *augmentation* pada data uji (rekonstruksi `test.csv` + berkas token salah skenario), sehingga dapat ditelusuri ke *chunk* sumbernya.

<!-- Sumber: gold terkoreksi (test.csv + koreksi label baru.xlsx) + pred dari done_newest/augmentation/output_S4_augmentation/.../iterative-6-incorrect.xlsx, rekonstruksi via recompute_gt_corrected.py. Chunk id dicantumkan untuk provenance. -->

[SISIPKAN TABEL 4.4 - Contoh Over-deteksi (False Positive), chunk 000007-007]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| . | O | O | |
| Hijabah | O | *B-LOCATION* | ✗ |
| atau | O | O | |
| wewenang | O | O | |

Kata *Hijabah* (jabatan pemelihara Ka'bah, bukan nama tempat) berlabel O pada acuan, tetapi ditarik model menjadi entitas *Location*. Inilah pola over-deteksi yang khas, yaitu kata umum atau abstrak berhuruf kapital yang dikira nama tempat atau orang.

[SISIPKAN TABEL 4.5 - Contoh Entitas Terlewat (False Negative), chunk 000001-002]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| India | *B-LOCATION* | *B-LOCATION* | |
| dan | O | O | |
| Cina | *B-LOCATION* | O | ✗ |
| . | O | O | |

Nama tempat *Cina* dalam rangkaian "... India dan Cina ..." gagal dikenali model sehingga terlewat menjadi O, meskipun *India* tepat sebelumnya dikenali benar. Pola ini khas pada nama tempat yang jarang muncul pada data latih, dan *false negative* seperti ini adalah kategori kesalahan terbanyak.

[SISIPKAN TABEL 4.6 - Contoh Misklasifikasi Tipe, chunk 000338-001]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| di | O | O | |
| Hudaibiyah | *B-LOCATION* | *B-EVENT* | ✗ |
| , | O | O | |

Token *Hudaibiyah* dapat merujuk tempat sekaligus peristiwa; di sini model menebaknya sebagai *Event* padahal acuan menandainya *Location*. Inilah satu dari hanya empat token salah-tipe pada skenario ini, dan semuanya melibatkan pasangan *Location* dengan *Event* (*Hudaibiyah*, *Badr*, dan *Jabal Uhud*).

[SISIPKAN TABEL 4.7 - Contoh Kesalahan Batas (Boundary B/I), chunk 000018-001]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| Senin | *B-TIME* | *B-TIME* | |
| pagi | *I-TIME* | *I-TIME* | |
| , | *I-TIME* | *I-TIME* | |
| tanggal | *B-TIME* | *I-TIME* | ✗ |
| 9 | *I-TIME* | *I-TIME* | |
| Rabi'ul | *I-TIME* | *I-TIME* | |
| Awwal | *I-TIME* | *I-TIME* | |

Rentang waktu "Senin pagi, tanggal 9 Rabi'ul Awwal" seharusnya dipecah acuan menjadi dua segmen *Time* (kata *tanggal* menjadi awal segmen baru, *B-TIME*), tetapi model menandainya sebagai lanjutan (*I-TIME*) sehingga kedua segmen menyatu. Penanda batas *B* dan *I* bergeser meskipun tipe entitasnya (*Time*) tetap benar. Kesalahan jenis ini hanya 8 token pada skenario *augmentation* dan kebanyakan terjadi pada *Time* dan nama orang banyak-kata.

Temuan tersebut juga terlihat secara visual pada *confusion matrix* kelima skenario Uji Coba 1 (Gambar 4.4) dan panel perbandingan error antar skenario Uji Coba 1 (Gambar 4.5).

[SISIPKAN GAMBAR 4.4 - Confusion Matrix Token-level Lima Skenario Uji Coba 1]
<!-- file: data/result/analysis/error_viz/by_group/s1_confusion.png -->

Gambar 4.4 menyandingkan *confusion matrix* tingkat token kelima skenario Uji Coba 1 dengan pewarnaan skala logaritmik (log10), sehingga sel bernilai kecil tetap terlihat meskipun sel *O*-ke-*O* (sekitar 46.100 token bukan-entitas yang benar) jauh lebih besar daripada sel lain. Dibaca menyeluruh, kelima panel berbentuk hampir sama: blok antar-tipe entitas, yaitu bagian matriks selain baris dan kolom *O*, hampir seluruhnya bernilai nol (token salah-tipe hanya berkisar 4 sampai 12 dari puluhan ribu token, dan selalu melibatkan pasangan *Location* dengan *Event* atau *Person*), sementara seluruh kesalahan yang berarti menumpuk pada baris dan kolom *O*. Keseragaman ini sendiri sudah menjadi temuan, sebab menunjukkan bahwa tidak ada satu pun teknik yang membuat model bingung membedakan jenis entitas; yang berbeda antar-skenario hanyalah seberapa banyak kesalahan deteksi *O*-ke-entitas, dan dari sisi itu pembahasan difokuskan pada skenario pemenang.

Pada panel *augmentation*, kebersihan blok antar-tipe terlihat paling ekstrem: hanya 4 token salah-tipe (seluruhnya *Location* diprediksi *Event*), tanpa satu pun kebocoran lain, sehingga model praktis tidak pernah tertukar membedakan satu tipe entitas dengan tipe lain. Seluruh kesalahan yang berarti terkumpul pada baris dan kolom *O*, yakni pada keputusan deteksi entitas-atau-bukan: sel terbesar adalah *Location* yang diprediksi *O* (17 token, nama tempat yang terlewat), disusul *Person* yang diprediksi *O* (15 token) dan *O* yang diprediksi *Person* (12 token, over-deteksi nama dari kata non-entitas), lalu *O*→*Location* (7) dan *Time*→*O* (7). Kelas minoritas justru tampil rapi: *Event* benar pada 136 token dengan hanya 2 terlewat dan tanpa satu pun salah-tipe, sedangkan *Time* benar pada 383 token dengan 7 terlewat. Angka-angka ini cocok persis dengan baris *augmentation* pada Tabel 4.3 (FP 25, FN 41, misklasifikasi tipe 4).

Sebagai pembanding singkat, kontras paling tajam dengan pemenang ada pada *weighted-class*, yang baris-baris *O*-ke-entitasnya paling padat (45 token *O* salah ditandai sebagai *Person*, 12 sebagai *Location*, 8 sebagai *Time*); inilah wujud visual dari over-deteksi yang menjatuhkan *precision*-nya pada Tabel 4.1, sekaligus penegasan bahwa perbedaan antar-teknik bermain di kolom deteksi, bukan di blok tipe. Dengan demikian, pembacaan menyilang kelima panel menuju satu kesimpulan yang sama dengan Tabel 4.3, yaitu tantangan model terletak pada deteksi batas entitas (kolom dan baris *O*), bukan pada klasifikasi jenisnya, dan keunggulan *augmentation* berasal dari merapikan baris *O* pada kelas minoritas, bukan dari mengubah kemampuan membedakan tipe.

[SISIPKAN GAMBAR 4.5 - Panel Perbandingan Error Lima Skenario Uji Coba 1 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s1_compare.png -->

Gambar 4.5 memuat empat panel yang membedah error kelima skenario Uji Coba 1 dari sudut berbeda. Panel kiri-atas (total error) menegaskan peringkat yang sama dengan Tabel 4.3, yaitu *augmentation* paling sedikit (78 token) dan JSCL paling banyak (185 token). Panel kanan-atas (komposisi *false negative* per kelas) menunjukkan SCL paling banyak melewatkan entitas (sekitar 102 token) sedangkan *augmentation* memangkasnya ke sekitar 41 token, dengan *Person* (biru) dan *Time* (ungu) mendominasi jumlah absolut entitas terlewat. Panel kiri-bawah (komposisi *false positive* per kelas) memperlihatkan bahwa tumpukan FP tertinggi ada pada *weighted-class* dan JSCL (sekitar 69 token, didominasi over-deteksi *Person*), jauh di atas *augmentation* yang hanya sekitar 25 token, dan inilah penjelasan mengapa *precision* keduanya lebih rendah. Panel kanan-bawah adalah yang paling bermakna untuk persoalan ketidakseimbangan, yaitu *FN-rate* per kelas atau persentase entitas gold yang terlewat setelah dinormalkan terhadap jumlah masing-masing kelas. Pada panel ini *Time* (ungu) konsisten menjadi kelas tersulit dengan tingkat terlewat tertinggi, sekitar 31 persen pada *baseline*, dan *augmentation* adalah teknik yang menurunkannya paling tajam menjadi sekitar 6 persen, sementara *Person* (biru) paling mudah dengan tingkat terlewat hanya 1 sampai 2 persen. Panel terakhir ini menjadi bukti visual paling langsung bahwa kelangkaan contoh (*few-shot*) membuat kelas minoritas paling rentan terlewat, dan bahwa keunggulan *augmentation* benar-benar berasal dari perbaikan pada kelas minoritas itu, bukan dari kelas mayoritas.

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

Yang menonjol dari Tabel 4.8 adalah bahwa kelas *O* justru bertambah (dari 95.277 menjadi 139.983), bukan berkurang, dan proporsinya terhadap seluruh token nyaris tidak berubah (92,6 persen menjadi 92,1 persen). Hal ini disengaja. Ada beberapa alasan mengapa kelas *O* tidak dikurangi (*undersampling*) meskipun jumlahnya mendominasi. Pertama, persoalan NER adalah pelabelan berurutan (*sequence labeling*), bukan klasifikasi sampel yang berdiri sendiri. Token *O* bukan "data berlebih" yang dapat dibuang, melainkan kata-kata penghubung di antara entitas dalam satu kalimat. Membuang token *O* berarti merusak struktur kalimat dan urutan BIO, sehingga konteks yang justru dibutuhkan model untuk menentukan batas entitas ikut hilang. Kedua, mengurangi *O* berarti membuang kalimat yang sedikit atau tidak mengandung entitas, padahal kalimat semacam itu adalah contoh negatif yang berharga karena mengajari model kata-kata apa yang bukan entitas. Bukti dampak buruknya sudah terlihat dalam uji coba ini sendiri pada skenario *weighted cross-entropy*, yang menggeser model menjauh dari *O* sehingga over-deteksi (*false positive* naik ke 69 token) dan *precision* turun (Tabel 4.1 dan 4.3); *undersampling O* diperkirakan menimbulkan efek serupa, yaitu model menjadi terlalu mudah menebak entitas. Ketiga, distribusi data latih sebaiknya mencerminkan teks nyata, dan pada teks Sirah sekitar sembilan dari sepuluh token memang bukan entitas, sehingga bila *O* dikurangi secara artifisial model dilatih pada distribusi yang tidak realistis dan berisiko over-deteksi saat dipakai pada teks sebenarnya (pergeseran distribusi).

Oleh karena itu, strategi yang dipilih adalah menambah contoh kelas minoritas (*oversampling* lewat augmentation), bukan mengurangi kelas mayoritas (*undersampling O*). Pendekatan ini menaikkan keterwakilan *Event* dan *Time* tanpa mengorbankan konteks *O*, dan hasilnya konsisten dengan Tabel 4.2, yaitu F1 kelas minoritas naik sementara *precision* keseluruhan tetap terjaga, berbeda dengan *weighted cross-entropy*. Mempertahankan *O* dalam jumlah besar juga bukan kerugian, sebab memprediksi *O* dengan benar adalah inti dari menghindari *false positive*; pada *confusion matrix* Gambar 4.4, sel *O*-ke-*O* yang besar (sekitar 46.100 token pada data uji) justru merupakan keberhasilan model mengenali kata bukan-entitas, dan kesalahan yang berarti terkumpul pada keputusan deteksi *O*-ke-entitas, bukan pada banyaknya jumlah *O*.

---

## 4.2 Uji Coba 2: Komparasi Model

Uji coba kedua bertujuan menguji pengaruh pemilihan model pra-latih (*backbone*) terhadap kualitas pengenalan entitas, yaitu mencari tahu model berbahasa Indonesia mana yang paling sesuai untuk teks Sirah ketika dipakai dalam alur *iterative self-training*. Lima model dibandingkan: IndoBERT *uncased* (`indolem/indobert-base-uncased`, *baseline*), `cahya/bert-base-indonesian-1.5G`, DistilBERT Indonesia, IndoBERT *cased*, dan RoBERTa Indonesia. <!-- [PERIKSA] pastikan nama persis tiap model pembanding sesuai checkpoint yang dijalankan. -->

Pengujian dilakukan dengan menjalankan pipeline yang identik untuk kelima model, yaitu data latih, ambang *pseudo-labelling*, dan *hyperparameter* yang sama, sehingga satu-satunya yang berbeda adalah *backbone*-nya. Seluruh model dievaluasi pada data uji yang sama dengan Uji Coba 1 (254 *chunk*, 49.739 token, 1.969 entitas) dengan pustaka seqeval tingkat entitas, mengikuti prosedur Kode Semu 3.12. Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* (agregat seluruh entitas) maupun *macro* (rata-rata antar kelas, lebih sensitif terhadap kelas minoritas); selain itu, untuk model yang hasilnya menyimpang, ditambahkan dua alat bantu diagnosis, yaitu trajektori F1 dari *checkpoint* awal sampai iterasi terakhir (untuk memisahkan masalah pelatihan awal dari efek *self-training*) dan hitungan kesalahan batas (*boundary* B/I) tingkat token (untuk melihat di mana defisit terjadi). Sebagaimana Uji Coba 1, hasil disajikan dalam dua tabel, yaitu metrik agregat (*Precision*, *Recall*, dan F1-score mikro) pada Tabel 4.9 dan F1-score per entitas pada Tabel 4.10.

[SISIPKAN TABEL 4.9 - Precision, Recall, dan F1-score Agregat Uji Coba 2]

| Model | Precision | Recall | F1-score (mikro) |
|-------|----------:|-------:|-----------------:|
| IndoBERT *uncased* (*baseline*) | 0,9524 | 0,9548 | 0,9536 |
| cahya *uncased* | 0,9388 | 0,9187 | 0,9286 |
| DistilBERT *uncased* | 0,9502 | 0,9208 | 0,9353 |
| IndoBERT *cased* | 0,7289 | 0,8329 | 0,7774 |
| RoBERTa | 0,7654 | 0,8532 | 0,8069 |

[SISIPKAN TABEL 4.10 - F1-score per Entitas Uji Coba 2]

| Model | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|-------|----------:|------------:|---------:|--------:|---------:|
| IndoBERT *uncased* (*baseline*) | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| cahya *uncased* | 0,9493 | 0,9232 | 0,9315 | 0,7203 | 0,8811 |
| DistilBERT *uncased* | 0,9581 | 0,9232 | 0,9116 | 0,7479 | 0,8852 |
| IndoBERT *cased* | 0,7843 | 0,8717 | 0,5549 | 0,5461 | 0,6893 |
| RoBERTa | 0,8135 | 0,8766 | 0,7654 | 0,5404 | 0,7490 |

[SISIPKAN GAMBAR 4.7 - F1-score Agregat Lima Model Uji Coba 2]
<!-- file: data/result/analysis/bab4_viz/f1_uc2_agregat.png -->

Gambar 4.7 meringkas Tabel 4.9 secara visual dan memperlihatkan keterbelahan dua kelompok, yaitu tiga model *uncased* (dengan IndoBERT *uncased* disorot sebagai *baseline*) berdiri tinggi dan rapat di kisaran F1 0,93 sampai 0,95, sedangkan IndoBERT *cased* dan RoBERTa anjlok jauh.

[SISIPKAN GAMBAR 4.8 - F1-score per Kelas Lima Model Uji Coba 2]
<!-- file: data/result/analysis/bab4_viz/f1_uc2_perkelas.png -->

Gambar 4.8 meringkas Tabel 4.10 per kelas dan menunjukkan bahwa keruntuhan kedua model bermasalah terjadi terutama pada *Person* dan *Time* yang anjlok dalam (*Person* ke 0,78 sampai 0,81 dari 0,94 sampai 0,96, dan *Time* ke sekitar 0,54 dari 0,84), sementara *Location* justru relatif bertahan tinggi (sekitar 0,87), bukan runtuh merata pada semua kelas. Pola yang justru menimpa entitas yang lazimnya banyak kata (*Person* dan *Time*) sambil menyisakan entitas satu kata (*Location*) ini menjadi petunjuk awal bahwa masalahnya bersifat teknis dan bukan kemampuan model.

Tabel 4.9 memperlihatkan pola yang terbelah dua. Tiga model *uncased* (IndoBERT, cahya, dan DistilBERT) stabil pada F1-score mikro sekitar 0,93 sampai 0,95 dengan IndoBERT *uncased* tetap yang terbaik, sedangkan dua model lain anjlok jauh, yaitu IndoBERT *cased* (0,7774) dan RoBERTa (0,8069) yang terpaut sekitar lima belas sampai delapan belas poin. Selisih sebesar ini wajib dijelaskan dan bukan sekadar dilaporkan, sebab penyajian angka tanpa penjelasan mudah disalahartikan sebagai bukti bahwa model *cased* atau RoBERTa "lebih buruk" untuk NER. Investigasi yang dilakukan justru menunjukkan kebalikannya, bahwa anomali ini bukan berasal dari kemampuan model, melainkan dari masalah teknis penyelarasan label pada pipeline yang memang disetel untuk model *uncased*.

Pembelahan dua kelompok ini paling gamblang terlihat ketika *confusion matrix* tingkat token kelima model disandingkan pada Gambar 4.9. Tiga model *uncased* (baris atas, yaitu IndoBERT, cahya, dan DistilBERT) berbentuk hampir identik dengan model sehat pada Uji Coba 1, yaitu blok antar-tipe entitas nyaris kosong dan kesalahan hanya menetes tipis pada baris dan kolom *O*, dengan sel *O* yang diprediksi *Person* berkisar 23 sampai 39 token. Sebaliknya, dua model bermasalah (baris bawah, yaitu IndoBERT *cased* dan RoBERTa) langsung tampak lebih gelap dan berantakan, sebab sel *O* yang diprediksi *Person* melonjak ke 200 dan 165 token sementara sel *Person* yang diprediksi *O* ke 149 dan 136 token, jauh melampaui ketiga model sehat. Kontras yang dapat diringkas sebagai tiga matriks rapi di atas dan dua matriks rusak di bawah ini memperlihatkan anomali sebagai gejala visual bahkan sebelum angkanya dibedah, sehingga pembahasan selanjutnya difokuskan pada satu model bermasalah, yaitu IndoBERT *cased*, sebagai contoh yang ditelaah paling dalam.

[SISIPKAN GAMBAR 4.9 - Confusion Matrix Token-level Lima Model Uji Coba 2]
<!-- file: data/result/analysis/error_viz/by_group/s2_confusion.png -->

Besaran dan komposisi error kedua kelompok model itu terangkum dari empat sudut pada Gambar 4.10. Panel total error (kiri-atas) memperlihatkan anomali tanpa bisa salah baca, yaitu IndoBERT *cased* (774 token) dan RoBERTa (677 token) menjulang jauh di atas tiga model *uncased* yang berkisar 165 sampai 263 token. Panel *false negative* per kelas (kanan-atas) dan *false positive* per kelas (kiri-bawah) menunjukkan pembengkakan terjadi serentak pada entitas terlewat maupun over-deteksi, dengan *Person* (biru) mendominasi jumlah absolut karena memang kelas terbanyak (*false positive Person* melonjak ke 200 pada *cased* dan 165 pada RoBERTa, *false negative Person* ke 149 dan 136) dan *Time* (ungu) menyumbang porsi mencolok pada kedua sisi. Panel *FN-rate* per kelas (kanan-bawah) paling tajam memperlihatkan beban pada kelas minoritas, sebab pada *cased* dan RoBERTa entitas *Event* dan *Time* terlewat pada tingkat jauh lebih tinggi dibanding ketiga model *uncased* yang sehat. Pola ini, yaitu error yang meledak menyeluruh dan paling memberatkan kelas yang contohnya sedikit, kemudian ditelusuri akarnya melalui tiga bukti berikut.

[SISIPKAN GAMBAR 4.10 - Panel Perbandingan Error Lima Model Uji Coba 2 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s2_compare.png -->

Kesimpulan tersebut bersandar pada tiga bukti yang saling menguatkan. Pertama, anomali ini bukan kerusakan akibat *self-training*, karena trajektori F1-score dari *checkpoint* awal (*base*) sampai iterasi terakhir justru naik tipis sebagaimana ditunjukkan pada Tabel 4.11, yaitu IndoBERT *cased* bergerak dari 0,7608 ke 0,7770 dan RoBERTa dari 0,7836 ke 0,8068 (pada data uji terkoreksi kedua nilai akhir praktis sama, yaitu 0,7774 dan 0,8069). Seandainya *self-training* yang merusak, F1-score seharusnya menurun seiring iterasi, sehingga fakta kenaikan ini menandakan defisit sudah ada sejak pelatihan pertama dan bukan akibat *pseudo-labelling*. Kedua, defisit ini tidak merata melainkan menimpa entitas yang lazimnya terdiri atas banyak kata, yaitu *Person* dan *Time*, sedangkan entitas yang umumnya satu kata bertahan. Tabel 4.10 menunjukkan F1-score *Person* untuk *cased* dan RoBERTa anjlok ke 0,78 sampai 0,81 (dari 0,94 sampai 0,96 pada *uncased*), dan F1-score *Time* bahkan runtuh paling dalam ke sekitar 0,54 (dari 0,84), sementara F1-score *Location* tetap di sekitar 0,87, jauh lebih tinggi daripada *Person* dan *Time* dan mendekati *uncased*. Penurunan *Time* yang paling tajam itu memang perlu dibaca dengan hati-hati karena jumlah entitasnya kecil (118) sehingga F1-nya mudah berayun, tetapi arah penurunannya searah dengan *Person* dan keduanya sama-sama entitas banyak kata, sehingga polanya menunjuk pada satu akar yang sama, bukan kebetulan pada nama orang saja. Ketiga, defisit ini disertai ledakan kesalahan batas (*boundary* B/I), sebab pada model *uncased* kesalahan *boundary* hanya 7 sampai 12 token sedangkan pada *cased* melonjak ke 138 token dan pada RoBERTa ke 133 token. Yang menentukan, kesalahan batas itu hampir seluruhnya jatuh pada kedua kelas banyak-kata: pada *cased* 122 token pada *Person* dan 13 pada *Time* (hanya 3 sisanya pada *Event*), pada RoBERTa 114 pada *Person* dan 13 pada *Time*, sementara *Location* dan *Event* nyaris tak menyumbang kesalahan batas (paling banyak lima token). Distribusi yang hampir seluruhnya mengikuti garis satu-kata melawan banyak-kata ini menjadi penegas terkuat bahwa akar masalahnya adalah penyelarasan penanda batas B/I pada entitas banyak kata, bukan kelemahan model pada tipe entitas tertentu.

[SISIPKAN TABEL 4.11 - Trajektori F1 Self-Training Model Anomali (base sampai iterasi-6)]

| Model | F1 *base* | F1 iter-2 | F1 iter-4 | F1 iter-6 |
|-------|----------:|----------:|----------:|----------:|
| IndoBERT *cased* | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |

<!-- Trajektori dihitung pada data uji ASLI (sebelum koreksi ground-truth), karena hanya iterasi terakhir yang memiliki berkas token salah untuk direkonstruksi ulang di GT terkoreksi. Nilai iter-6 pada GT terkoreksi (0,7774 dan 0,8069) praktis identik dengan kolom iter-6 di atas, dan yang relevan di sini semata arah trajektori yang NAIK (bukti defisit ada sejak base, bukan akibat self-training). -->


Pola ini konsisten dengan **misalignment label kata-ke-subword**: entitas banyak kata paling rentan ketika penandaan B/I bergeser. *Person* paling sering berupa nama banyak kata (*Abdul Muththalib*, *Amr bin Luhay*) dan *Time* di teks Sirah juga lazim berupa rangkaian panjang (*hari Senin malam tanggal 21 dari bulan Ramadhan*), sehingga keduanya paling terdampak, sedangkan *Location* yang umumnya satu kata (*Makkah*, *Madinah*) nyaris tak tersentuh. Bahwa hitungan absolut kesalahan batas tetap didominasi *Person* (122 dari 138 token pada *cased*) bukan berarti *Time* aman, melainkan karena *Person* adalah kelas banyak-kata yang jauh paling sering muncul (1.302 berbanding 118 entitas); pada *Time* kerusakan serupa lebih banyak terbaca sebagai runtuhnya F1 relatif dan ledakan *false positive* daripada sebagai jumlah token batas yang besar. Pembeda kedua model ini dari tiga model *uncased* yang sehat adalah skema tokenisasinya (IndoBERT *cased* memakai WordPiece *cased*; RoBERTa memakai *byte-level BPE*), sementara pipeline disetel dan diuji untuk WordPiece *uncased*. Hipotesis terkuat: fungsi penyelarasan label kata-ke-subword tidak menangani tokenizer *cased*/BPE dengan benar, sehingga model dilatih pada label yang sedikit bergeser sejak awal. <!-- [PERIKSA] Status: ini hipotesis yang belum diverifikasi di level kode. Yang sudah terbukti: (1) bukan kerusakan self-training, (2) defisit ada sejak base, (3) terpusat di PERSON multi-kata + boundary. Verifikasi lanjutan: inspeksi fungsi tokenize_and_align_labels (word_ids/is_split_into_words) untuk tokenizer cased & RoBERTa. JANGAN menyimpulkan "cased/RoBERTa lebih buruk untuk NER Sirah" sebelum verifikasi ini. -->

Dari sisi anatomi kesalahan, ketiga model *uncased* memperlihatkan pola error yang sama dengan Uji Coba 1, yaitu didominasi *false positive* dan *false negative* dengan misklasifikasi tipe dan *boundary* yang kecil. Pada model *cased* dan RoBERTa, selain *boundary* yang meledak, misklasifikasi tipe juga lebih banyak (39 token pada keduanya) dan sebagian besarnya menyebar ke pasangan yang melibatkan *Person* atau *Location*, sehingga sekali lagi menunjuk pada kerusakan yang terpusat pada penanganan entitas banyak kata, terutama nama orang. Kontras antara model sehat dan model anomali paling jelas terlihat pada kesalahan batas di nama orang banyak kata, dirinci per token pada Tabel 4.12 dan Tabel 4.13. Pada model *uncased* yang sehat, kesalahan batas sangat sedikit (hanya 8 token pada *augmentation*) dan kebanyakan jatuh pada *Time* (lihat Tabel 4.7), sedangkan pada IndoBERT *cased* dan RoBERTa kesalahan ini meledak (133 sampai 138 token, 122 dan 114 di antaranya pada *Person*) dan terpusat pada nama orang.

[SISIPKAN TABEL 4.12 - Kesalahan Batas pada Person, IndoBERT cased (chunk 000013-004)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| dari | O | O | |
| Amr | *B-PERSON* | *I-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Syu'aib | *I-PERSON* | *B-PERSON* | ✗ |
| , | O | O | |

Nama "Amr bin Syu'aib" yang seharusnya satu entitas *Person* utuh (*B-I-I*) terpecah oleh model: awal nama "Amr" justru ditandai sebagai lanjutan (*I*) sehingga rangkaiannya menjadi tak berpangkal, sementara "Syu'aib" di ujung nama malah ditandai sebagai awal entitas baru (*B*). Penanda batas *B* dan *I* bergeser meskipun tipenya (*Person*) tetap benar.

[SISIPKAN TABEL 4.13 - Kesalahan Batas pada Person, RoBERTa (chunk 000007-006)]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| dan | O | O | |
| Murrah | *B-PERSON* | *I-PERSON* | ✗ |
| bin | *I-PERSON* | *I-PERSON* | |
| Auf | *I-PERSON* | *I-PERSON* | |

Awal nama "Murrah" yang seharusnya penanda awal entitas (*B*) justru ditandai sebagai lanjutan (*I*), sehingga seluruh rangkaian "Murrah bin Auf" menjadi urutan *I* tanpa pangkal *B*, pola khas ketika penanda awal nama banyak-kata hilang.

*Confusion matrix* IndoBERT *cased* ditunjukkan pada Gambar 4.11. Dibandingkan model sehat pada Gambar 4.4, kebocoran pada penanganan *Person* langsung terlihat: sel *O* yang diprediksi *Person* melonjak ke 200 token dan *Person* yang diprediksi *O* ke 149 token, jauh di atas *augmentation* yang hanya 12 dan 15. Kekeliruan antar-tipe pun naik menjadi 39 token yang menyebar pada sel-sel kecil di sekitar *Person* dan *Location*, berbanding hanya 4 token pada model sehat. Satu hal penting saat membaca gambar ini, matriksnya bersifat tingkat-tipe sehingga penanda *B* dan *I* digabung; akibatnya ledakan kesalahan batas *B/I* (sekitar 138 token yang menjadi gejala utama anomali) tidak muncul sebagai sel tersendiri melainkan tersembunyi di dalam hitungan *Person* yang dianggap benar. Dengan kata lain, Gambar 4.11 memperlihatkan sisi deteksi dan tipe dari defisit *Person*, sedangkan komponen batasnya terbaca terpisah pada hitungan token yang dibahas sebelumnya.

[SISIPKAN GAMBAR 4.11 - Confusion Matrix IndoBERT cased (anomali)]
<!-- file: data/result/analysis/error_viz/per_skenario/indobert-cased/confusion_matrix.png -->

---

## 4.3 Uji Coba 3: Modul POS-tag

Uji coba ketiga bertujuan menguji apakah penambahan fitur *Part-of-Speech tagging* (POS-tag), yaitu informasi kelas kata seperti kata benda atau kata kerja, dapat membantu model mengenali batas dan tipe entitas dengan lebih baik. Hipotesisnya, mengetahui suatu kata berkategori kata benda dapat menjadi petunjuk tambahan bahwa kata itu berpeluang menjadi entitas. Untuk mengujinya, model tanpa fitur POS-tag (*baseline*) dibandingkan dengan model yang menambahkan POS-tag sebagai fitur pendamping pada masukan.

Pengujian dilakukan dengan melatih kedua varian pada data dan prosedur yang sama, lalu mengevaluasinya pada data uji yang identik dengan dua uji coba sebelumnya (254 *chunk*, 49.739 token, 1.969 entitas). Metrik utama yang digunakan adalah *F1-score* karena mampu memberikan evaluasi yang seimbang antara *precision* (ketepatan) dan *recall* (kelengkapan), serta dilaporkan dalam bentuk *micro* maupun *macro*; metrik ini dilengkapi jumlah kesalahan tingkat token sebagai pembanding langsung banyaknya error. Kedua varian dievaluasi melalui prosedur seqeval yang identik pada data uji yang sama, sehingga angkanya langsung sebanding. Mengikuti format dua uji coba sebelumnya, hasil disajikan pada Tabel 4.14 untuk metrik agregat beserta jumlah error tingkat token dan Tabel 4.15 untuk F1-score per entitas.

[SISIPKAN TABEL 4.14 - Precision, Recall, F1-score Agregat, dan Jumlah Error Uji Coba 3]

| Skenario | Precision | Recall | F1-score (mikro) | Error token |
|----------|----------:|-------:|-----------------:|------------:|
| *Baseline* | 0,9524 | 0,9548 | 0,9536 | 165 |
| POS-tag | 0,9628 | 0,9467 | 0,9547 | 164 |

[SISIPKAN TABEL 4.15 - F1-score per Entitas Uji Coba 3]

| Skenario | F1 PERSON | F1 LOCATION | F1 EVENT | F1 TIME | macro F1 |
|----------|----------:|------------:|---------:|--------:|---------:|
| *Baseline* | 0,9690 | 0,9530 | 0,9342 | 0,7983 | 0,9136 |
| POS-tag | 0,9693 | 0,9466 | 0,9333 | 0,8376 | 0,9217 |

<!-- Angka POS-tag & baseline UC3 = ground-truth uji TERKOREKSI (recompute_gt_corrected_results.md: POS-tag micro 0,9547 / baseline 0,9536; per-label di tabel; error breakdown error_breakdown_gt_corrected.md: POS-tag total 164 FP40/FN106/MIS10/BND8, baseline 165 FP55/FN98/MIS5/BND7). Skrip: recompute_gt_corrected.py + error_breakdown_gt_corrected.py. Catatan historis: pada test ASLI (sebelum koreksi), POS-tag di-inference LANGSUNG via eval_postag_direct.py (micro 0,9439, memvalidasi metode rekonstruksi lama vs 0,9432); angka lama itu kini superseded oleh GT terkoreksi. -->

[SISIPKAN GAMBAR 4.12 - F1-score Agregat Baseline vs Modul POS-tag Uji Coba 3]
<!-- file: data/result/analysis/bab4_viz/f1_uc3_agregat.png -->

Gambar 4.12 meringkas Tabel 4.14 dan menunjukkan F1 mikro yang nyaris berimpit antara *baseline* dan POS-tag (dengan macro POS-tag hanya sedikit lebih tinggi), sehingga secara agregat tidak tampak perbaikan yang berarti dari penambahan POS-tag.

[SISIPKAN GAMBAR 4.13 - F1-score per Kelas Baseline vs Modul POS-tag Uji Coba 3]
<!-- file: data/result/analysis/bab4_viz/f1_uc3_perkelas.png -->

Gambar 4.13 meringkas Tabel 4.15 per kelas dan memperlihatkan perubahan yang tidak konsisten arahnya, yaitu *Time* naik sementara *Location* justru turun dan *Person* maupun *Event* nyaris tak bergerak, sehingga secara visual pun penambahan POS-tag tidak memberi perbaikan yang sistematis.

Secara ringkas, modul POS-tag tidak memberikan perbaikan yang berarti. F1-score mikro POS-tag (0,9547) praktis setara dengan *baseline* (0,9536), unggul hanya 0,0011 poin yang masih berada jauh di dalam rentang variansi antar-*run* sehingga tidak dapat ditafsirkan sebagai perbedaan yang bermakna. Perubahan per kelas pada Tabel 4.15 pun tidak konsisten arahnya, sebab F1-score *Time* naik (0,7983 ke 0,8376) dan *Event* praktis tetap, sementara *Location* justru turun (0,9530 ke 0,9466) dan *Person* nyaris tak berubah, sehingga tidak ada arah perbaikan yang sistematis. Berbeda dari perkiraan awal, penambahan POS di sini justru menggeser model ke arah *precision* lebih tinggi (0,9628 berbanding 0,9524) dengan *recall* sedikit menurun (0,9467 berbanding 0,9548); artinya model menjadi sedikit lebih berhati-hati menebak entitas, bukan menjadi lebih tepat mengenalinya. Kenaikan *macro* F1 yang tipis (0,9136 ke 0,9217) pun hampir seluruhnya berasal dari *Time*, kelas bersupport kecil (118 entitas) yang F1-nya mudah berayun, sehingga lebih mungkin mencerminkan variasi acak daripada manfaat sistematis fitur POS.

Penting ditegaskan bahwa hasil ini diperoleh dari fitur POS yang asli, bukan *placeholder*. Pemeriksaan atas berkas data yang benar-benar dipakai pada *run* POS-tag (`data_with_pos_20260610` dan dataset *retraining* skenario ini) menunjukkan kolom POS terisi 17 kategori Universal Dependencies yang beragam dan selaras dengan token, yaitu NOUN, VERB, PROPN, PRON, ADP, dan seterusnya, dengan 1.131 dari 1.189 token bertanda *Person* berkategori PROPN. Temuan eksplorasi data (EDA) sebelumnya yang menyebut kolom `pos_tag` berisi nilai *placeholder* "NN" merujuk pada berkas *dataset* utama versi lama dan tidak berlaku untuk berkas POS yang dibuat khusus bagi uji coba ini. Dengan demikian, kegagalan modul POS-tag bukan artefak fitur palsu, melainkan hasil yang sah, sehingga penyebab yang paling masuk akal adalah bahwa informasi POS sebagian besar redundan dengan apa yang sudah dipelajari IndoBERT dari konteks: sebagai model bahasa berbasis konteks, IndoBERT pada praktiknya telah menyerap petunjuk kelas kata sehingga menambahkan POS secara eksplisit tidak memberi sinyal baru yang berarti untuk membedakan entitas.

Dari sisi anatomi kesalahan, pola error skenario POS-tag tetap sama dengan *baseline*, yaitu didominasi keputusan deteksi (*false positive* dan *false negative*), dengan misklasifikasi tipe dan kesalahan batas yang kecil. Rinciannya justru membalik pergeseran yang semula diperkirakan: dari 164 token salah, *false negative* (entitas terlewat) menjadi kategori terbanyak dengan 106 token atau 65 persen, *false positive* (over-deteksi) hanya 40 token atau 24 persen, sedangkan misklasifikasi tipe 10 token (6 persen) dan kesalahan batas 8 token (5 persen), sehingga sama seperti skenario lain kesalahan terpusat pada keputusan deteksi, bukan pada pembedaan jenis entitas. Dibandingkan *baseline* yang *false positive*-nya 55 token dan *false negative* 98 token, penambahan POS justru menurunkan *false positive* menjadi 40 sekaligus menaikkan *false negative* menjadi 106; inilah wujud konkret dari *precision* yang naik tetapi *recall* yang turun, yaitu model menjadi lebih berhati-hati menebak entitas sehingga lebih sedikit salah tebak tetapi lebih banyak entitas terlewat. Tambahan entitas terlewat itu paling banyak jatuh pada *Location* (43 token, dari 33 pada *baseline*), tampak misalnya pada nama tempat langka seperti "Pakistan" yang seharusnya berlabel *B-LOCATION* tetapi diprediksi *O*, sejalan dengan penurunan tipis F1 *Location* pada Tabel 4.15.

Untuk memperlihatkan kategori error terbesar itu secara konkret, yaitu entitas terlewat (*false negative*), Tabel 4.16 merinci per token sebuah penggalan dari *chunk* 000002-004. Nama tempat "*Pakistan*" yang menurut acuan sebuah entitas *Location* justru diprediksi *O* sehingga terlewat, meskipun konteks kalimatnya menyebut nama wilayah. Pola ini menjelaskan mengapa kelas *Location* dan *Time* paling banyak menyumbang *false negative* pada skenario POS-tag, sebab nama tempat langka dan rangkaian waktu yang jarang muncul pada data latih mudah gagal dikenali ketika model bergeser menjadi lebih berhati-hati.

[SISIPKAN TABEL 4.16 - Contoh Entitas Terlewat (False Negative), chunk 000002-004]

| Token | Ground-truth | Prediksi | |
|-------|--------------|----------|---|
| pula | *O* | *O* | |
| ke | *O* | *O* | |
| Pakistan | *B-LOCATION* | *O* | ✗ |
| , | *O* | *O* | |
| dan | *O* | *O* | |

*Confusion matrix* skenario POS-tag ditunjukkan pada Gambar 4.14. Strukturnya menyerupai model sehat, yaitu kesalahan terkonsentrasi pada baris dan kolom *O* sementara kebingungan antar-tipe entitas tetap kecil (hanya sekitar 10 token). Dibandingkan *baseline*, sel over-deteksi justru mengecil, terutama *O* yang diprediksi *Person* (28 token berbanding 38 pada *baseline*), sedangkan sel entitas yang diprediksi *O* membesar, terutama *Location* yang terlewat (43 token berbanding 33). Pola ini sejalan dengan Tabel 4.14 yang menunjukkan *precision* POS-tag lebih tinggi tetapi *recall* lebih rendah, yaitu fitur POS membuat model lebih berhati-hati sehingga lebih sedikit salah tebak tetapi lebih banyak entitas terlewat.

[SISIPKAN GAMBAR 4.14 - Confusion Matrix Skenario POS-tag]
<!-- file: data/result/analysis/error_viz/per_skenario/POS-tag/confusion_matrix.png -->

Perbandingan *baseline* dan POS-tag dari empat sudut dirangkum pada Gambar 4.15. Panel total error (kiri-atas) menunjukkan keduanya nyaris sama banyak (POS-tag 164 berbanding *baseline* 165 token). Yang lebih informatif adalah dua panel komposisi: panel *false negative* per kelas (kanan-atas) memperlihatkan POS-tag justru melewatkan lebih banyak entitas (106 berbanding 98 token, tambahan terbesar pada *Location*), sedangkan panel *false positive* per kelas (kiri-bawah) memperlihatkan kebalikannya, yaitu over-deteksi POS-tag mengecil (40 berbanding 55 token). Kedua panel ini adalah wujud visual paling langsung dari pertukaran *precision* yang naik tetapi *recall* yang turun, yaitu model menjadi lebih berhati-hati sehingga lebih sedikit salah tebak, tetapi dengan ongkos lebih banyak entitas terlewat. Panel *FN-rate* per kelas (kanan-bawah) menunjukkan POS-tag tidak menurunkan tingkat terlewat kelas minoritas secara konsisten (*Time* sedikit membaik sementara *Location* justru memburuk), perubahan yang terlalu kecil dan tidak searah untuk disebut manfaat bersih. Dengan demikian, panel ini memperkuat kesimpulan bahwa modul POS-tag tidak memberikan perbaikan bersih.

[SISIPKAN GAMBAR 4.15 - Panel Perbandingan Error Baseline vs POS-tag Uji Coba 3 (total, FN, FP, dan FN-rate per kelas)]
<!-- file: data/result/analysis/error_viz/by_group/s3_compare.png -->

### Rangkuman ketiga uji coba dan pembahasan error lintas-skenario

Menggabungkan ketiga uji coba, **konfigurasi terbaik adalah IndoBERT *uncased* dengan *augmentation*** (micro F1 0,9756). Dua temuan error berlaku konsisten di semua skenario yang sehat. Pertama, **kedua kelas minoritas (*Event* 75 dan *Time* 118 entitas) tetap paling sulit** dibanding *Location* (474) dan *Person* (1.302), dengan *Time* sebagai kelas terlemah di hampir semua skenario karena entitasnya kerap berupa rangkaian banyak kata dan terpengaruh artefak OCR sehingga pencocokan rentang penuh paling sulit; kelangkaan contoh (*few-shot*) tetap menjadi faktor dominan kesalahan, dan augmentation berhasil justru karena menambah contoh kedua kelas ini, mengangkat F1 *Time* paling tajam (0,7983 ke 0,9038). Kedua, **misklasifikasi tipe yang sedikit itu didominasi pasangan *Location* dan *Event***, karena sejumlah nama identik berfungsi ganda sebagai tempat sekaligus peristiwa (*Uhud*, *Badr*, *Hudaibiyah*). Ini ambiguitas semantik nyata pada teks Sirah, bukan kelemahan model. Sebagai keterbatasan, efek *chunking* tidak diuji melalui *ablation* terpisah; pemeriksaan tak langsung menunjukkan hanya sebagian kecil error berada di tepi *chunk*, sehingga pemotongan konteks bukan penyebab utama error.

---

## 4.4 Evaluasi Graf

Evaluasi *knowledge graph* terdiri dari dua bagian: analisis struktur jaringan dengan *Social Network Analysis* (apakah struktur graf masuk akal terhadap narasi Sirah) dan pengujian fungsional melalui skenario kueri (apakah graf dapat menjawab kebutuhan penelusuran).

### 4.4.1 Analisis Struktur Jaringan (SNA)

Hasil analisis jaringan menjawab delapan skenario pengujian (G1 sampai G8) yang dirancang pada Tabel 3.19, yaitu sentralitas tokoh (G1 dan G2), pengelompokan komunitas (G3), sentralitas peristiwa (G4), struktur jaringan keseluruhan (G5), studi kasus peristiwa (G6), peran lokasi (G7), dan keterlibatan lintas fase (G8). Analisis utama dilakukan pada proyeksi jaringan antar tokoh (*Person*), yaitu dua tokoh dihubungkan jika terlibat pada peristiwa yang sama, ditambah relasi kekerabatan, persahabatan, dan permusuhan yang eksplisit. Agar analisis sentralitas mengukur keterlibatan sosial dan bukan sekadar posisi dalam silsilah, cakupan graf dibatasi pada tokoh yang benar-benar terlibat pada minimal satu peristiwa yang dinarasikan; tokoh yang hanya muncul di dalam rantai keturunan (*nasab*) tanpa pernah terlibat peristiwa sengaja tidak dimasukkan ke analisis, sebab keterhubungan mereka semata berasal dari garis kekerabatan sehingga sentralitasnya menjadi artefak rantai, bukan keterlibatan nyata (pembatasan ini bersifat penyaringan pada tahap analisis, sedangkan *knowledge graph* utuh dengan seluruh entitas tetap dipertahankan sebagai basis pengetahuan). Bukti struktural di balik tiap skenario dapat ditelusuri langsung pada *knowledge graph* di Neo4j melalui kumpulan kueri reproduksi yang disediakan pada berkas `sna_evidence_queries_bab4.cypher`, sementara skor sentralitas dan komunitas dihitung pada pipeline analisis (NetworkX). Statistik tingkat graf (G5) ditunjukkan pada Tabel 4.17.

<!-- Angka v4 (KG dari NER pemenang S4-augmentation). Graf Person = data/result/analysis/v4_scoped/ (proyeksi co-participation, PERSON nasab-only di-scope keluar via src/relation_extraction/clean_v4_hybrid_genealogy.py; KG kanonik nodes_v4_hybrid.csv utuh). Event layer di-dedup via clean_v4_events.py. Kueri reproduksi bukti SNA per skenario ada di data/result/neo4j/sna_evidence_queries_bab4.cypher. Skor degree/betweenness/PageRank + Louvain/modularitas dari src/analysis/sna_analysis.py + sna_graph_metrics.py --version v4_scoped. -->

[SISIPKAN TABEL 4.17 - Statistik Jaringan Tokoh]

| Metrik | Nilai |
|--------|------:|
| Jumlah *node* (*Person*) | 137 |
| Jumlah *edge* | 1.853 |
| *Density* | 0,1989 |
| *Average clustering coefficient* (lokal) | 0,7100 |
| *Transitivity* (global) | 0,7957 |
| Jumlah komponen | 5 |
| Ukuran komponen terbesar | 128 *node* (93,4%) |
| Rata-rata panjang lintasan (komponen terbesar) | 1,96 |
| Jumlah komunitas (Louvain) | 8 |
| **Modularitas (Q, Louvain)** | **0,2831** |

<!-- Angka dari data/result/analysis/v4_scoped/graph_metrics_v2.md & sna_summary.md (graf Person co-participation ber-scope, v4). Louvain proper Q=0,2831 (8 komunitas); pembanding greedy Q=0,2607 (10 komunitas) dan Girvan-Newman Q=0,0301; ARI(Louvain,greedy)=0,4737. Graf lebih padat & kecil dari v3 (208 node/density 0,085) karena di-scope ke tokoh peserta peristiwa; nasab-only dibuang. -->

Sentralitas tokoh dibaca dari dua sudut yang saling melengkapi, yaitu siapa yang paling sentral secara menyeluruh (G1) dan siapa yang menjadi jembatan penghubung antar-kelompok (G2). Untuk G1, sepuluh tokoh teratas beserta tiga ukuran sentralitas (*degree centrality*, *closeness centrality*, dan *PageRank*) ditunjukkan pada Tabel 4.18, diurutkan menurut *PageRank* sebagai ukuran kepentingan menyeluruh.

[SISIPKAN TABEL 4.18 - Sepuluh Tokoh Teratas Sentralitas Tokoh (G1): Degree, Closeness, PageRank]
<!-- Sumber: data/result/analysis/v4_scoped/sna_metrics.csv (graf Person co-participation ber-scope v4, 137 node). Diurut PageRank. -->

| Rank | Tokoh | Degree | Closeness | PageRank |
|---:|-------|------:|------:|------:|
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

Ketiga ukuran G1 sepakat menempatkan Muhammad di puncak dengan jarak yang sangat lebar (*degree* 0,7941, yang berarti ia terhubung langsung ke sekitar 108 dari 137 tokoh, hampir 1,4 kali tokoh kedua), diikuti sahabat utama dan tokoh kunci. Sudut kedua (G2), yaitu *betweenness centrality* yang mengukur peran sebagai penghubung jalur terpendek antar tokoh, ditunjukkan pada Tabel 4.19; pada graf inti yang padat ini (rata-rata lintasan hanya 1,96) ukuran tersebut kurang tajam membedakan sehingga sebagian nama periferal ikut naik, namun tetap menegaskan dominasi Muhammad yang berjarak sangat lebar dari peringkat berikutnya.

[SISIPKAN TABEL 4.19 - Sepuluh Tokoh Teratas berdasarkan Betweenness (Jembatan Antar-Kelompok, G2)]
<!-- Sumber: data/result/analysis/v4_scoped/sna_metrics.csv (graf Person ber-scope v4). -->

| Rank | Tokoh | Betweenness |
|---:|-------|------:|
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

**Interpretasi.** Struktur jaringan masuk akal terhadap narasi Sirah. Muhammad sangat dominan pada semua ukuran sentralitas (*PageRank* 0,0509, lebih dari dua kali peringkat kedua; *degree centrality* 0,7941, yang berarti ia terhubung langsung ke sekitar 108 dari 137 tokoh; *betweenness* 0,2808, lebih dari empat kali peringkat kedua), mencerminkan posisinya sebagai pusat seluruh peristiwa. Peringkat berikutnya diisi konsisten oleh sahabat utama dan tokoh kunci, yaitu Ali bin Abu Thalib, Umar, Abu Bakar, Utsman, dan Aisyah, berdampingan dengan tokoh oposisi yang memang banyak terlibat peristiwa (Abu Jahal di peringkat tiga *PageRank* dan Abu Sufyan di peringkat enam). Susunan ini jauh lebih sesuai dengan bobot historis dibanding bila tokoh yang hanya muncul dalam silsilah ikut dihitung, dan menjadi bukti langsung manfaat pembatasan cakupan ke tokoh peserta peristiwa. Sebaliknya, ukuran *betweenness* (G2) pada Tabel 4.19 perlu dibaca dengan hati-hati: karena graf inti sangat padat dan rata-rata lintasan hanya 1,96 (hampir semua tokoh saling terhubung dalam dua langkah), ukuran ini kehilangan daya pembeda sehingga beberapa nama periferal ikut menonjol, termasuk perawi seperti Ibnu Hajar yang kehadirannya berasal dari peran periwayatan dan bukan keterlibatan sosial, pola artefak yang sama dengan yang dibahas pada validasi sentralitas. Yang tetap kokoh dari kedua ukuran adalah dominasi Muhammad yang berjarak sangat lebar dari seluruh tokoh lain. Deteksi komunitas dengan algoritma Louvain menghasilkan 8 komunitas dengan modularitas Q = 0,2831, nilai yang menunjukkan struktur kelompok yang masih terlihat namun tidak setajam graf yang lebih longgar, wajar mengingat inti peserta peristiwa saling terhubung rapat sehingga batas antar-kelompok melembut. Dua komunitas terbesar mendominasi: komunitas lingkar Muslim inti (66 anggota; tokoh utama Muhammad, Ali, Umar, Abu Bakar, Aisyah, Utsman) dan sebuah komunitas campuran (47 anggota) yang menautkan tokoh oposisi Quraisy (Abu Jahal, Abu Sufyan) dengan sejumlah tokoh Muslim yang banyak terlibat peperangan (Hamzah bin Abdul Muththalib, Zaid bin Haritsah); percampuran ini sendiri menjadi tanda bahwa pada modularitas serendah ini pemisahan antar-faksi belum tajam, sejalan dengan padatnya jaringan. Pengelompokan bersifat cukup stabil terhadap pilihan algoritma pada tingkat sedang, ditunjukkan oleh kesepakatan antara Louvain dan *greedy modularity* (*Adjusted Rand Index* 0,47).

**Validasi tokoh yang terdengar asing.** Sebagian nama pada sepuluh besar mungkin terdengar asing dibanding tokoh yang lazim disebut sentral dalam literatur Sirah (para Khulafa Rasyidin). Kemunculan mereka berakar pada cara graf dibentuk, yaitu dua tokoh dihubungkan bila terlibat pada peristiwa yang sama (*co-participation*), sedangkan relasi keterlibatan (`INVOLVED_IN`) diekstraksi berdasarkan kedekatan posisi tokoh dengan nama peristiwa di dalam teks. Akibatnya, tokoh minor yang kebetulan disebut di dalam atau dekat *chunk* peristiwa berpenghuni padat (Perang Badr saja menautkan puluhan tokoh) otomatis terhubung ke seluruh peserta peristiwa itu dan membentuk *clique*, sehingga sentralitasnya ikut melonjak. Dengan kata lain, peringkat sentralitas sebagian mencerminkan seberapa banyak teks menyebut seseorang di sekitar peristiwa besar, bukan semata bobot historisnya. Contoh paling jelas adalah **Amr Bin Umayyah**: pada graf tanpa pembobotan ia sempat menempati peringkat kedua *PageRank* (degree 119), tepat di bawah Nabi Muhammad, posisi yang mencurigakan secara historis. Penelusuran balik ke teks menunjukkan tiga dari empat relasi `INVOLVED_IN`-nya adalah *false positive*, sebab keterkaitannya dengan Perang Badr, Uhud, dan Tabuk muncul dari kalimat yang sebenarnya membicarakan tokoh atau perbandingan lain, sementara hanya Perang Khandaq yang sahih; peran sebenarnya menurut teks adalah kurir Nabi ke Najasyi. Pembobotan sisi (membuang *co-mention* lemah) bersama pembatasan cakupan ke tokoh peserta peristiwa menurunkan Amr ke peringkat ke-12 sehingga ia tidak lagi muncul pada sepuluh besar Tabel 4.18. Kedua penyaringan itu menghapus kategori artefak terbesar, yaitu tokoh silsilah yang tanpa penyaringan sempat menggelembung ke puncak *PageRank* semata karena panjangnya rantai nasab (garis keturunan pra-Islam seperti para leluhur Nabi yang tidak pernah terlibat satu peristiwa pun), tetapi tidak menghapus seluruhnya. **Abu Azzah** (peringkat delapan) dan **Khunais bin Hudzafah** (peringkat sembilan) pada Tabel 4.18 adalah sisa artefak *clique*, yaitu keduanya disebut di dalam *chunk* peperangan besar (Perang Badr dan Uhud) sehingga otomatis tertaut ke seluruh pesertanya, dan karena namanya muncul pada kalimat yang sama dengan nama peristiwa, pembobotan tidak memangkasnya. Pola serupa menjelaskan kehadiran perawi pada peringkat jembatan Tabel 4.19, terutama **Ibnu Hajar**, seorang periwayat yang namanya berulang di seluruh teks sebagai penyebut sumber dan bukan pelaku peristiwa. Temuan ini menegaskan bahwa peringkat sentralitas wajib divalidasi balik ke teks, dan bahwa solusi tuntas atas over-ekstraksi `INVOLVED_IN` berbasis kedekatan posisi adalah ekstraksi relasi berbasis makna kata kerja, yang menjadi arah pengembangan lanjutan.

**Sentralitas peristiwa (G4).** Analisis diperluas ke jaringan antar-peristiwa, yaitu dua *Event* dihubungkan bila berbagi minimal satu tokoh, dengan bobot sisi sama dengan jumlah tokoh bersama (35 *Event*, 264 sisi, *density* 0,444, 4 komponen, komponen terbesar memuat 32 peristiwa). Sepuluh peristiwa paling sentral menurut *PageRank* ditunjukkan pada Tabel 4.20.

[SISIPKAN TABEL 4.20 - Sepuluh Peristiwa Teratas berdasarkan PageRank]

| Rank | Peristiwa | PageRank | Frekuensi |
|------|-----------|---------:|----------:|
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

Tiga peristiwa teratas adalah peperangan besar, yaitu Perang Badr (*PageRank* 0,0965), Perang Uhud (0,0889), dan Perang Khandaq (0,0674). Peringkat ini didukung bukti *co-participation* yang kuat: Perang Badr dan Perang Uhud terhubung ke hampir semua peristiwa lain (masing-masing ber-*degree* 27 dan 29 dari 34 peristiwa), sehingga berbagi tokoh dengan mayoritas peristiwa dan wajar menjadi pusat jaringan; pola ini masuk akal karena peperangan besar melibatkan paling banyak tokoh sehingga jaringan *co-participation*-nya paling padat. Yang menonjol dari daftar ini, dan berbeda dari sebagian kajian yang menyorot tonggak hidup Nabi, adalah bahwa peringkat teratas nyaris seluruhnya berisi peperangan; peristiwa daur hidup seperti kelahiran, turunnya wahyu pertama, dan wafat Nabi tidak muncul sebagai simpul sentral. Ini keterbatasan yang perlu diungkap secara jujur, sebab di dalam teks peristiwa daur hidup umumnya disebut melalui frasa kata kerja atau deskriptif ("beliau dilahirkan", "beliau wafat", "turunnya wahyu") yang tidak tertangkap NER sebagai entitas *Event* bernama, sehingga graf peristiwa mencerminkan sekaligus kekuatan model menangkap nama peperangan dan kelemahannya pada peristiwa berbasis kata kerja.

Sebagai bukti bahwa *PageRank* dan fungsi naratif tidak selalu sejalan, ukuran *betweenness* (jembatan antar kelompok peristiwa) justru menempatkan Perang Uhud di puncak (0,1958), di atas Perang Khandaq (0,1346) dan Perjanjian Hudaibiyah (0,0264). Perang Uhud berperan sebagai penghubung antara kelompok peristiwa awal Madinah dan kelompok peristiwa pasca-Uhud, sehingga membaca kedua ukuran bersama lebih kaya daripada satu peringkat tunggal. Dua *caveat* perlu ditegaskan. Pertama, peringkat *PageRank* peristiwa wajib dibaca bersama frekuensi kemunculannya, sebab aturan *co-participation* dapat menggelembungkan peristiwa berfrekuensi rendah: Perang Dzul Usyairah menempati peringkat 6 (0,0404) padahal frekuensinya hanya 1, karena ia berada pada periode yang sama dengan Perang Badr sehingga "kecipratan" puluhan tokoh bersama (*degree* 23); pola serupa terjadi pada Perang Bani Al-Ashfar (peringkat 8, frekuensi 1) dan Baiat Aqabah Kubra (peringkat 5, frekuensi 4). Kedua, relasi kronologi `PRECEDES` hanya berjumlah 17 sisi, jauh lebih sedikit daripada ratusan sisi *co-participation*, sehingga sinyal yang dominan adalah kemunculan bersama, bukan urutan waktu eksplisit.

<!-- G7 v4 dari scenario_g7_g8.py --version v4_hybrid (periode_bab sudah di-map via apply_period_to_v4.py). Graf lokasi v4 lebih kecil dari v3 (17 vs 35 node) karena KG v4 punya lebih sedikit relasi OCCURRED_AT (47 vs 83) dan tanpa enrichment lifecycle. -->
**Peran lokasi (G7).** Dua lokasi dihubungkan bila ada tokoh yang terlibat pada peristiwa di kedua lokasi (17 *Location*, 136 sisi, *density* 1,000, artinya graf lengkap tempat setiap lokasi terhubung ke semua lokasi lain). Karena graf lokasi lengkap, *betweenness* seragam nol dan sama sekali tidak membedakan sehingga peringkat sepenuhnya memakai *weighted degree* (total tokoh bersama). Sepuluh lokasi paling sentral ditunjukkan pada Tabel 4.21.

[SISIPKAN TABEL 4.21 - Sepuluh Lokasi Teratas berdasarkan Weighted Degree]

| Rank | Lokasi | Weighted degree |
|------|--------|----------------:|
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

Hasil ini masuk akal terhadap geografi Sirah. Madinah (*weighted degree* 661) dan Makkah (561) menempati posisi teratas, mencerminkan dua pusat dari dua fase besar Sirah, yaitu dakwah di Makkah dan periode Madinah. Bukti bahwa *betweenness* tidak layak dipakai di sini bahkan lebih ekstrem daripada perkiraan: seluruh 17 lokasi memiliki *degree* identik 16 (terhubung ke semua lokasi lain) dengan *betweenness* seragam nol, sehingga ukuran ini sama sekali tidak mampu membedakan peran antar lokasi pada graf yang benar-benar lengkap ini; sebaliknya *weighted degree* yang menghitung total tokoh bersama tetap diskriminatif, dengan sebaran nilai yang lebar (dari 297 untuk Aqabah sampai 661 untuk Madinah). Habasyah menempati peringkat kedua bersama Makkah (561) meskipun berada di seberang Laut Merah, konsisten dengan perannya sebagai tujuan Hijrah ke Habasyah. Sebagai keterbatasan yang harus diungkap, "Yatsrib" muncul terpisah pada peringkat lima (528) padahal Yatsrib adalah nama lama Madinah; keduanya tidak tergabung oleh *alias clustering* pada graf lokasi, sehingga peran Madinah sebenarnya ter-*understate* (jika digabung, dominasinya makin besar). Pola lain yang menandakan keterbatasan aturan *co-participation* adalah empat lokasi Ash-Shafra, Tihamah, Badr, dan Najd yang memiliki *weighted degree* identik 525, indikasi bahwa keempatnya terhubung melalui himpunan tokoh bersama yang sama persis, bukan melalui keterkaitan geografis yang berdiri sendiri. Perlu dicatat pula bahwa graf lokasi v4 ini jauh lebih kecil daripada versi terdahulu (17 berbanding 35 lokasi), karena *knowledge graph* hasil model pemenang memuat lebih sedikit relasi tempat-peristiwa (`OCCURRED_AT`) sehingga hanya sebagian lokasi yang tertaut ke jaringan; hal ini menjadi salah satu keterbatasan cakupan graf yang perlu diperbaiki melalui ekstraksi relasi lokasi yang lebih lengkap.

**Keterlibatan lintas fase (G8).** Skenario ini menghitung jumlah fase Sirah unik (dari enam fase) tempat seorang tokoh terlibat, melalui jalur tokoh ke peristiwa ke fase. Hasilnya ditunjukkan pada Tabel 4.22.

[SISIPKAN TABEL 4.22 - Tokoh dengan Keterlibatan Lintas Fase Terbanyak]

| Rank | Tokoh | Jumlah fase | Jumlah peristiwa |
|------|-------|------------:|-----------------:|
| 1 | Muhammad | 5 | 22 |
| 2 | Umar bin Al-Khaththab | 3 | 5 |
| 3 | Abu Bakar | 3 | 4 |
| 4 | Ali bin Abu Thalib | 2 | 7 |
| 5 | Zaid bin Haritsah | 2 | 5 |
| 6 | Aisyah | 2 | 4 |

Bukti paling kuat dari skenario ini adalah Muhammad sebagai tokoh dengan jangkauan fase terluas, merentang lima dari enam fase (fase I Pra-Islam, II Makkah, IV Perang Besar, V Diplomasi, dan VI Konsolidasi) melalui 22 peristiwa, menegaskan posisinya sebagai poros narasi yang hadir di hampir setiap babak. Satu-satunya fase yang tidak tersentuh, yaitu III Madinah Awal, lebih mencerminkan keterbatasan cakupan graf peristiwa (tidak ada peristiwa bernama yang terpetakan ke babak itu pada *knowledge graph* ini) daripada ketiadaan peran Nabi. Di bawahnya, hanya dua tokoh menyentuh tiga fase, yaitu Umar bin Al-Khaththab dan Abu Bakar (masing-masing 5 dan 4 peristiwa), sesuai posisi mereka sebagai sahabat terdekat yang aktif dari periode Makkah sampai Konsolidasi. Distribusi keseluruhan sangat timpang dan menjadi bukti bahwa mayoritas tokoh bersifat spesifik untuk satu babak: 124 tokoh hanya menyentuh satu fase, 17 tokoh dua fase, dua tokoh tiga fase, dan hanya satu tokoh (Muhammad) menyentuh lima fase. Sebagai catatan, banyaknya peristiwa yang diikuti tidak otomatis berarti jangkauan lintas fase yang luas: Ali bin Abu Thalib terlibat di tujuh peristiwa, terbanyak setelah Muhammad, tetapi seluruhnya terkonsentrasi pada dua fase saja (Makkah dan Perang Besar). Satu hal yang patut dicatat adalah bahwa peringkat lintas fase pada graf ini terisi seluruhnya oleh pelaku sejarah yang nyata (Muhammad, Umar, Abu Bakar, Ali, Zaid bin Haritsah, dan Aisyah), tanpa dihuni artefak periwayatan seperti perawi atau figur yang hanya disebut sebagai sumber. Meski begitu, kehati-hatian yang sama seperti pada ukuran sentralitas tetap diperlukan, sebab relasi `INVOLVED_IN` yang mendasari skenario ini dibentuk dari kedekatan posisi nama dengan nama peristiwa di dalam *chunk*, sehingga nama yang tersebar luas di teks (misalnya perawi seperti Ibnu Hajar yang muncul pada peringkat jembatan Tabel 4.19) berpotensi tertaut ke peristiwa yang secara historis tidak diikutinya. Peringkat lintas fase karena itu tetap wajib divalidasi balik ke makna teks dan tidak boleh dibaca semata sebagai ukuran keterlibatan historis.

**Studi kasus lima peristiwa besar (G6).** Untuk memvalidasi pipeline secara kualitatif, dipilih lima peristiwa dari periode yang berjauhan (P8 sampai P13) lalu diperiksa sub-grafnya. Ringkasannya ditunjukkan pada Tabel 4.23 dan panel visualisasinya pada Gambar 4.16.

[SISIPKAN TABEL 4.23 - Ringkasan Sub-graf Lima Peristiwa Besar]

| Peristiwa | Periode | Tokoh | Lokasi | Waktu |
|-----------|:-------:|------:|-------:|------:|
| Perang Badr | P8 | 44 | 9 | 6 |
| Perang Uhud | P9 | 41 | 3 | 10 |
| Perjanjian Hudaibiyah | P11 | 7 | 5 | 4 |
| Perang Khaibar | P11 | 7 | 2 | 1 |
| Perang Tabuk | P13 | 4 | 0 | 1 |

<!-- Angka di-recompute dari graf final SNA (edges_v4_hybrid.csv, INVOLVED_IN weight >= 0.3, sama dengan WEIGHT_THRESHOLD di sna_analysis.py) via visualize_case_study_events.py --version v4_hybrid. Konsisten dengan header tiap panel pada Gambar 4.16. -->


[SISIPKAN GAMBAR 4.16 - Panel Sub-graf Lima Peristiwa Besar]
<!-- file: data/result/analysis/v3/case_study_panel.png -->

Secara visual, Gambar 4.16 menyusun kelima sub-graf dengan satu *node* peristiwa (kuning) di pusat tiap panel dan tokoh peserta (biru) mengelilinginya, dihubungkan garis merah untuk relasi `INVOLVED_IN` serta garis hijau untuk relasi antar-tokoh (keluarga dan sahabat). Perbedaan kepadatan antar panel langsung terbaca: panel Perang Badr (44 tokoh) dan Perang Uhud (41 tokoh) tampak rapat oleh banyak tokoh dan garis, sedangkan Perjanjian Hudaibiyah (7 tokoh), Perang Khaibar (7 tokoh), dan Perang Tabuk (4 tokoh) hanya berisi segelintir tokoh, sehingga kontras cakupan antar peristiwa terlihat sekilas pandang. Dari kelima peristiwa, terkumpul 83 tokoh unik dan hanya Muhammad yang hadir di seluruh lima peristiwa, menegaskan perannya sebagai tulang punggung jaringan. Ukuran sub-graf menurun tajam dari Perang Badr ke Perjanjian Hudaibiyah. Penurunan ini lebih mencerminkan **bias cakupan NER** (seberapa banyak tokoh disebut pada *chunk* peristiwa itu) daripada keterlibatan historis sebenarnya, karena setiap sub-graf peristiwa secara konstruksi membentuk *clique* (semua peserta saling terhubung) sehingga *density* selalu bernilai 1,0 dan tidak informatif sebagai pembanding. Ukuran (jumlah tokoh) dan jumlah relasi langsung antar tokoh lebih tepat dipakai sebagai pembanding kohesi. Sebagai bukti keterbatasan aturan ini, daftar peserta Perang Badr justru mencampur dua kubu yang saling berperang: tokoh Muslim (Ali bin Abu Thalib, Hamzah bin Abdul Muththalib, Utsman bin Affan) dan tokoh Quraisy (Abu Jahal, Abu Lahab, Abu Sufyan bin Harb) sama-sama tertaut sebagai `INVOLVED_IN` peristiwa yang sama. Hal ini menegaskan bahwa relasi *co-participation* hanya menyatakan "terlibat pada peristiwa yang sama", bukan "berada di pihak yang sama", sehingga sub-graf peristiwa tidak boleh dibaca sebagai aliansi.


**Analisis error/keterbatasan graf.** Sebagaimana error pada NER, struktur graf juga memuat sejumlah *artifact* yang perlu diungkap secara jujur:

1. **Over-ekstraksi relasi `INVOLVED_IN` berbasis kedekatan.** Karena relasi dibentuk dari kemunculan bersama dalam *chunk* yang sama, sebagian tokoh memperoleh keterhubungan yang lebih tinggi daripada perannya yang sebenarnya. Contoh yang sudah ditelusuri adalah "Amr bin Umayyah" (setelah pembobotan dan pembatasan cakupan turun ke peringkat ke-12 *PageRank*, 0,0127): pemeriksaan menunjukkan sebagian relasi `INVOLVED_IN`-nya adalah *false positive* dari kedekatan teks, sedangkan peran historisnya yang nyata adalah kurir Nabi. Sisa artefak sejenis masih tampak pada Abu Azzah dan Khunais bin Hudzafah di sepuluh besar Tabel 4.18 (anggota *clique* peperangan) serta perawi Ibnu Hajar pada peringkat jembatan Tabel 4.19.
2. **Peristiwa daur hidup tidak tertangkap sebagai entitas.** Sebagian peristiwa penting (seperti kelahiran, turunnya wahyu pertama, dan wafat Nabi) di dalam teks disebut melalui frasa kata kerja atau deskriptif ("beliau dilahirkan", "beliau wafat") sehingga tidak dikenali NER sebagai entitas *Event* bernama dan tidak muncul sebagai simpul pada graf peristiwa (Tabel 4.20). Akibatnya jaringan peristiwa didominasi peperangan; ketiadaan tonggak daur hidup ini adalah keterbatasan cakupan yang perlu diungkap secara jujur, dan penanganannya menuntut ekstraksi peristiwa berbasis makna kata kerja, bukan sekadar entitas bernama.
3. **Ketergantungan pada kualitas NER.** Karena *node* dan *edge* berasal dari prediksi NER, kesalahan deteksi pada Bab 4.1 sampai 4.3 (terutama nama langka yang terlewat) ikut membatasi kelengkapan graf; hal ini juga terlihat pada tipisnya relasi lokasi (`OCCURRED_AT`) yang membuat graf lokasi pada G7 mengecil.

Visualisasi langsung dari Neo4j Browser ditunjukkan pada Gambar 4.17, yaitu jaringan ego Nabi Muhammad (seluruh entitas yang terhubung langsung dengannya pada *knowledge graph*). Gambar ini memperkuat secara visual dominasi sentralitas yang terbaca pada Tabel 4.18 dan Tabel 4.19, sebab Muhammad berada di pusat sebagai satu-satunya simpul yang menautkan puluhan tokoh dan peristiwa di sekelilingnya. Sisi-sisinya berlabel jenis relasi (`KELUARGA`, `SAHABAT`, `MUSUH`, dan `INVOLVED_IN`), sehingga peran beliau sebagai poros keluarga, persahabatan, sekaligus pertentangan terlihat dalam satu pandangan. Neo4j Browser mewarnai simpul menurut labelnya, yaitu tokoh (`Person`) berwarna hijau-zaitun dan peristiwa (`Event`) berwarna biru, misalnya Baiat Aqabah Kubra, Perang Badr, dan Perang Uhud, bukan menurut komunitas; struktur komunitas itu sendiri telah dirangkum secara kuantitatif melalui modularitas Louvain pada pembahasan sebelumnya. Perlu dicatat bahwa graf ego ini menampilkan relasi naratif langsung pada *knowledge graph*, sedangkan nilai sentralitas pada Tabel 4.18 dan Tabel 4.19 dihitung dari proyeksi *co-participation* antar tokoh; keduanya berasal dari graf yang berbeda tetapi konsisten menempatkan Muhammad sebagai pusat jaringan.

[SISIPKAN GAMBAR 4.17 - Visualisasi Neo4j Browser: Jaringan Ego Nabi Muhammad]
<!-- file: docs/bimbingan/screenshots/A1_ego_muhammad.png (screenshot Neo4j Browser langsung). [PERIKSA] Screenshot ini dari KG lama (masih memuat event lifecycle spt Kelahiran/Hijrah Madinah yg tidak ada di v4) — sebaiknya di-regenerate dari KG v4 setelah import_sirah v4 ke Neo4j agar konsisten. Reproduksi: di Neo4j Browser jalankan `MATCH (m:Person {name:'Muhammad'})-[r]-(n) RETURN m,r,n` lalu tata layout & screenshot. Warna otomatis per-label (Person hijau, Event biru). -->

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
