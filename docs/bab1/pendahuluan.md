<!-- SUMBER: docs/Buku-TA-Genta-fixed.pdf (buku terbaru), diekstrak 2026-07-19. Cermin TEKS untuk rujukan revisi; tabel/gambar/persamaan dipipihkan. Backup .md lama: pendahuluan.md.bak_pre_pdf_sync -->

<!-- Halaman buku 1 · PDF 35 -->
BAB 1
PENDAHULUAN
1.1 Latar Belakang
Sirah Nabawiyah memiliki peran penting dalam pengetahuan Islam, tidak hanya sebagai
catatan sejarah tentang kehidupan Nabi Muhammad SAW, tetapi juga sebagai dasar untuk
memahami konteks turunnya wahyu, strategi dakwah, serta rujukan dalam pembelajaran nilai,
akhlak, keteladanan, dan kepemimpinan dalam Islam (Abror & Rahma, 2024; Kusumah et al.,
2022). Dalam kajian akademik, Sirah juga dipandang sebagai sumber historiografi yang kaya
karena memuat keterkaitan antara praktik ritual, interaksi sosial, nilai moral, dan data historis,
termasuk informasi tentang tokoh, peristiwa, lokasi, dan waktu dalam sejarah awal Islam (Abror
& Rahma, 2024; Pratama, 2022). Namun, karena informasi Sirah umumnya disajikan sebagai
narasi panjang yang tersusun kronologis, banyak pembaca baik akademisi maupun masyarakat
umum seringkali memerlukan penelusuran teks secara menyeluruh ketika ingin menemukan
informasi tertentu atau membandingkan gaya penulisan, kecenderungan interpretasi, dan
pemilihan sumber pada karya Sirah modern maupun klasik (Pratama, 2022).
Dalam praktiknya, kebutuhan pencarian informasi pada Sirah tidak hanya sebatas
menemukan bagian teks yang membahas suatu topik, tetapi juga menjawab pertanyaan yang
spesifik. Contohnya, siapa saja tokoh yang terlibat dalam suatu peristiwa, peristiwa apa saja
yang terjadi di suatu lokasi, atau bagaimana urutan kejadian berdasarkan waktu. Kebutuhan
seperti ini sulit dipenuhi oleh pencarian berbasis kata kunci biasa. Dalam bidang pencarian
informasi atau Information Retrieval (IR), masalah ini dikenal sebagai vocabulary mismatch,
yaitu ketidakcocokan antara kata yang diketik pengguna dengan kata yang muncul di dokumen,
sehingga hasil pencarian sering kurang tepat atau kurang lengkap (Hambarde dan Proenca,
2023). Tantangan ini bertambah besar ketika dokumen yang ditelusuri panjang, karena
pengguna harus merangkum sendiri informasi dari teks yang banyak dan rumit. Oleh sebab itu,
berbagai pendekatan baru terus dikembangkan untuk membantu memahami dokumen panjang
secara lebih efisien (Gana et al., 2025).
Pencarian informasi pada Sirah Nabawiyah juga dipengaruhi oleh sifat pengetahuannya
yang saling terhubung, yaitu adanya keterkaitan erat antara tokoh, peristiwa, lokasi, dan waktu.
Penyimpanan dalam bentuk teks biasa kurang cocok untuk menjawab pertanyaan tentang
hubungan tersebut, karena keterkaitan antar informasi tidak tersimpan secara langsung. Sebagai
alternatif, pengetahuan dapat disimpan dalam bentuk knowledge graph, yaitu graf yang
menggambarkan pengetahuan sebagai kumpulan simpul (node) dan garis penghubung (edge).
Unit informasi paling sederhana dinyatakan sebagai dua simpul yang dihubungkan oleh satu
relasi (Zhong et al., 2024). Knowledge graph menyimpan entitas beserta hubungan antar entitas
secara eksplisit, sehingga lebih mudah ditelusuri berdasarkan hubungannya (Ren et al., 2024).
Penyimpanan ini dapat dikelola menggunakan graph database seperti Neo4j, sehingga
hubungan antar tokoh dan peristiwa bisa ditelusuri secara langsung melalui kueri graf (Ren et
al., 2024; Zhong et al., 2024).
Untuk membangun knowledge graph dari teks Sirah Nabawiyah, diperlukan proses
ekstraksi informasi, yaitu proses mengubah teks tidak terstruktur menjadi bentuk yang dapat
dimodelkan sebagai graf. Tahap utama dalam proses ini adalah Named-Entity Recognition
(NER), yaitu pengenalan entitas penting dalam teks seperti orang (Person), lokasi (Location),

<!-- Halaman buku 2 · PDF 36 -->
waktu (Time), serta peristiwa (Event) sebagai pusat yang menghubungkan narasi. Setelah
entitas dikenali, hubungan antarentitas dan peristiwa dibentuk sehingga menjadi relasi
penghubung pada graf. Pendekatan pembangunan knowledge graph dengan Neo4j telah
diterapkan pada berbagai bidang, misalnya pada pembangunan knowledge graph pengobatan
tradisional yang memanfaatkan NER dan menyediakan penelusuran melalui kueri Cypher (Xie
et al., 2023). Penelitian lain memandang pembangunan knowledge graph sebagai rangkaian
proses, mulai dari pemodelan pengetahuan, ekstraksi entitas dan relasi, penggabungan
pengetahuan, hingga penyimpanan, dengan Neo4j sebagai media penyimpanan agar
pengetahuan dapat ditelusuri berbasis graf (He et al., 2022). Dengan demikian, ekstraksi entitas
dan relasi dari teks menjadi landasan yang sesuai untuk membangun knowledge graph Sirah
Nabawiyah menggunakan Neo4j.
Teks Sirah Nabawiyah berbahasa Indonesia termasuk data dengan sumber berlabel terbatas
(low-resource), artinya jumlah data yang sudah diberi label untuk melatih model masih sedikit,
sementara menyiapkannya secara manual mahal dan memakan waktu. Untuk mengatasi
keterbatasan ini, penelitian ini menggunakan NER berbasis Semantic Role Labeling (SRL)
yang dilatih dengan strategi semi-supervised melalui iterative self-training. Istilah berbasis
SRL di sini merujuk pada orientasi peran dalam kalimat, yaitu pelaku dipetakan
menjadi Person, keterangan tempat menjadi Location, keterangan waktu menjadi Time, dan
peristiwa menjadi Event. Orientasi peran ini diwujudkan melalui pola dan kamus entitas saat
penyiapan label awal serta mengikuti garis metode self-training dari Ariyanto et al. (2025),
bukan melalui penguraian tata bahasa predikat-argumen secara penuh. Pada strategi ini, model
mula-mula dilatih dengan sedikit data berlabel, lalu model tersebut dipakai untuk menebak label
pada data yang belum berlabel. Hanya tebakan dengan tingkat keyakinan tinggi yang dipakai
untuk melatih ulang model, dan langkah ini diulang secara bertahap (Ariyanto et al., 2025).
Berdasarkan uraian di atas, penelitian ini berfokus pada pembangunan knowledge graph
Sirah Nabawiyah menggunakan Neo4j dengan empat label utama, yaitu Person, Event,
Location, dan Time. Entitas dan peristiwa diekstraksi dari teks Sirah berbahasa Indonesia
menggunakan NER berbasis SRL, kemudian dimodelkan sebagai simpul dan dihubungkan
melalui relasi inti, yaitu INVOLVED_IN untuk menunjukkan keterlibatan tokoh dalam peristiwa,
OCCURRED_AT untuk menunjukkan lokasi terjadinya peristiwa, dan OCCURRED_ON untuk
menunjukkan waktu terjadinya peristiwa. Graf juga dilengkapi dengan relasi antar-tokoh dan
relasi urutan kronologis antar-peristiwa. Hasil NER dievaluasi menggunakan metrik precision,
recall, dan F1-score melalui tiga skenario uji coba, yaitu penanganan ketidakseimbangan kelas,
perbandingan model, dan pengaruh modul POS-tag. Kelayakan graf diperiksa melalui
pengujian fungsional dengan menjalankan sejumlah skenario kueri Cypher yang mewakili
kebutuhan penelusuran berbasis hubungan, sehingga dapat diketahui apakah graf mampu
menjawab pertanyaan penelusuran tersebut. Graf yang terbentuk juga dianalisis menggunakan
Social Network Analysis (SNA) untuk mengukur peran tiap simpul dan struktur jaringan secara
keseluruhan. Analisis ini mencakup ukuran sentralitas, seperti degree, betweenness, closeness,
dan PageRank, ukuran tingkat graf seperti kepadatan dan koefisien pengelompokan, serta
deteksi komunitas untuk mengetahui tokoh dan peristiwa yang paling berperan dalam jaringan
relasi Sirah Nabawiyah.

<!-- Halaman buku 3 · PDF 37 -->
1.2 Rumusan Masalah
Berdasarkan latar belakang permasalahan yang telah diuraikan sebelumnya, penelitian ini
diarahkan untuk mengkaji proses konstruksi basis data graf Sirah Nabawiyah secara sistematis,
mulai dari tahap penyiapan data teks hingga evaluasi terbatas terhadap hasil ekstraksi dan
struktur graf yang dibangun. Untuk itu, rumusan masalah dalam penelitian ini adalah sebagai
berikut:
1. Bagaimana menyiapkan data teks Sirah Nabawiyah agar menjadi dataset yang siap
digunakan?
2. Bagaimana mengekstraksi entitas dari teks Sirah Nabawiyah menggunakan Named-
Entity Recognition (NER) berbasis SRL dengan strategi iterative self-training?
3. Bagaimana membangun knowledge graph berbasis entitas Person, Event, Location, dan
Time beserta relasinya menggunakan Neo4j?
4. Bagaimana mengevaluasi hasil NER melalui tiga skenario uji coba serta menganalisis
knowledge graph yang dibangun, termasuk analisis jaringan menggunakan Social
Network Analysis dan pengujian fungsional graf?
1.3 Batasan Masalah
Agar penelitian tetap terfokus dan dapat diselesaikan sesuai ruang lingkup Tugas Akhir,
ditetapkan sejumlah batasan berikut:
1. Data yang digunakan berupa teks Sirah Nabawiyah berbahasa Indonesia, bersumber dari
buku Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan
Kathur Suhardi).
2. Label entitas minimal terdiri dari Person, Event, Location, dan Time.
3. Ekstraksi entitas menggunakan NER berbasis SRL (iterative self-training berbasis
BERT dengan model IndoBERT)
4. Relasi yang dibangun mencakup relasi inti, yaitu keterlibatan tokoh pada peristiwa,
lokasi terjadinya peristiwa, dan waktu terjadinya peristiwa, serta dilengkapi relasi antar
tokoh (kekeluargaan, persahabatan, dan permusuhan) dan relasi urutan kronologis antar
peristiwa.
5. Penelitian dibatasi sampai tahap pembangunan knowledge graph dan analisisnya, bukan
pada pengembangan aplikasi tanya-jawab atau chatbot secara penuh.
1.4 Tujuan
Penelitian ini bertujuan membangun knowledge graph Sirah Nabawiyah menggunakan
Neo4j melalui proses ekstraksi entitas dan relasi dari teks Sirah berbahasa Indonesia, serta
menganalisis hasilnya. Tujuan spesifik penelitian ini adalah sebagai berikut:
1. Menyiapkan data teks Sirah Nabawiyah menjadi dataset yang siap digunakan.
2. Mengekstraksi entitas dari teks Sirah Nabawiyah menggunakan Named-Entity
Recognition (NER) berbasis SRL dengan strategi iterative self-training.
3. Merancang skema dan membangun knowledge graph berbasis entitas Person, Event,
Location, dan Time beserta relasinya menggunakan Neo4j.
<!-- ✳ REVISI (Temuan #1): SNA hanya mendeskripsikan struktur; pisahkan tiga peran (NER/SNA/fungsional) -->
4. Mengevaluasi hasil NER melalui tiga skenario uji coba serta menganalisis knowledge
graph yang dibangun, termasuk analisis jaringan menggunakan Social Network
Analysis dan pengujian fungsional graf, untuk menguji kualitas ekstraksi entitas,
mendeskripsikan struktur jaringan, dan menilai

<!-- Halaman buku 4 · PDF 38 -->
kelayakan graf dalam mendukung penelusuran informasi pada Sirah
Nabawiyah.
Luaran utama penelitian ini berbentuk knowledge graph Sirah Nabawiyah yang tersimpan
dan dapat ditelusuri pada graph database Neo4j melalui kueri Cypher. Selain itu, penelitian ini
juga menghasilkan dataset teks Sirah berlabel entitas dan model NER terlatih sebagai luaran
pendukung. Dengan demikian, luaran penelitian ini berupa graf pengetahuan beserta data dan
modelnya, bukan aplikasi atau program siap pakai bagi pengguna akhir.
1.5 Manfaat
Penelitian Tugas Akhir ini diharapkan memberikan sejumlah manfaat. Penelitian ini
memberikan kontribusi pada kajian ekstraksi informasi dari teks naratif melalui pemodelan
berbasis graf, sekaligus menjadi referensi penerapan NER dan ekstraksi relasi untuk
pembangunan knowledge graph pada bidang sejarah dan keislaman. Selain itu, penelitian ini
menghasilkan knowledge graph Sirah Nabawiyah yang dapat ditelusuri menggunakan Neo4j
untuk pencarian informasi berbasis hubungan, sehingga mempermudah penyusunan skenario
pencarian seperti tokoh dan peristiwa yang terkait, lokasi kejadian, serta urutan waktu peristiwa.
Hasil penelitian ini juga membantu pengguna, baik pelajar, peneliti, maupun masyarakat, untuk
mengakses informasi Sirah secara lebih terstruktur dan mudah ditelusuri, serta mendukung
pengembangan aplikasi lanjutan seperti sistem tanya-jawab berbasis graf atau visualisasi
sejarah Sirah.
