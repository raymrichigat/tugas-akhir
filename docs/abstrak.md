<!-- SUMBER: docs/Buku-TA-Genta-fixed.pdf (buku terbaru), diekstrak 2026-07-19. Cermin TEKS untuk rujukan revisi; tabel/gambar/persamaan dipipihkan. Backup .md lama: abstrak.md.bak_pre_pdf_sync -->

<!-- Halaman depan · PDF 17 -->
ABSTRAK

PENDEKATAN NAMED-ENTITY RECOGNITION DALAM PEMBANGUNAN
KNOWLEDGE GRAPH SIRAH NABAWIYAH

Nama Mahasiswa / NRP
: Genta Putra Prayoga / 5025221040
Departemen
: Teknik Informatika FTIRS - ITS
Dosen Pembimbing
: Dini Adni Navastara, S.Kom., M.Sc.
Dosen Ko-pembimbing
: Ratih Nur Esti Anggraini, S.Kom, M.Sc., Ph.D.

Abstrak
Sirah Nabawiyah memuat informasi mengenai tokoh, peristiwa, waktu, dan lokasi dalam
sejarah Islam. Namun, penyajiannya sebagai teks naratif menyebabkan hubungan antarentitas
sulit ditelusuri secara sistematis. Penelitian ini bertujuan membangun knowledge graph Sirah
Nabawiyah berbahasa Indonesia menggunakan Named-Entity Recognition (NER), Neo4j, dan
Social Network Analysis (SNA) untuk penelusuran dan analisis hubungan antarentitas.
Penelitian dilakukan melalui ekstraksi teks menggunakan OCR, prapemrosesan,
pemecahan teks menjadi chunk, pelabelan semiotomatis, serta pelatihan NER berbasis
IndoBERT dengan strategi iterative self-training. Orientasi peran semantik digunakan untuk
menentukan entitas Person, Event, Location, dan Time. Entitas hasil ekstraksi dinormalisasi
<!-- ✳ REVISI (Bu Ratih #1): "alias clustering" → "normalisasi alias" -->
melalui normalisasi alias, dihubungkan berdasarkan pola relasi, diperkaya dengan periodisasi,
dan disimpan dalam Neo4j. Evaluasi mencakup tiga skenario NER, SNA, dan enam kueri
fungsional.
Hasil terbaik dicapai IndoBERT uncased dengan augmentasi data dan F1-score mikro
sebesar 0,9756. Knowledge graph yang dibangun memuat 1.192 simpul dan 728 relasi.
Proyeksi jaringan antartokoh terdiri atas 137 simpul dan 1.853 sisi serta menghasilkan delapan
komunitas dengan modularitas Louvain sebesar 0,2831. Muhammad menempati posisi tertinggi
pada seluruh ukuran sentralitas. Keenam kueri fungsional berhasil dijalankan, menghasilkan
jawaban tidak kosong, dan dapat ditelusuri ke sumber, meskipun sebagian relasi
masih memerlukan verifikasi terhadap teks sumber.

Kata kunci: IndoBERT; Knowledge Graph; Named-Entity Recognition; Sirah Nabawiyah;
Social Network Analysis.

<!-- Halaman depan · PDF 19 -->
ABSTRACT

NAMED-ENTITY RECOGNITION–BASED CONSTRUCTION OF A SIRAH
NABAWIYAH KNOWLEDGE GRAPH

Full Name / Student ID
: Genta Putra Prayoga / 5025221040
Department
: Informatics ELECTICS - ITS
Advisor
: Dini Adni Navastara, S.Kom., M.Sc.
Co-advisor
: Ratih Nur Esti Anggraini, S.Kom, M.Sc., Ph.D.

Abstract
Sirah Nabawiyah contains information about people, events, times, and locations in
Islamic history. However, its narrative form makes relationships among entities difficult to trace
systematically. This study aims to construct an Indonesian Sirah Nabawiyah knowledge graph
using Named-Entity Recognition (NER), Neo4j, and Social Network Analysis (SNA) for
relational exploration and analysis.
This research involved OCR-based text extraction, preprocessing, segmentation into
chunks, semi-automatic labeling, and IndoBERT-based NER training through iterative self-
training. A semantic-role orientation was used to define Person, Event, Location, and Time
entities. <!-- ✳ REVISI (Bu Ratih #1): alias clustering → alias normalization -->Extracted entities were normalized through alias normalization, connected using relation
patterns, enriched with periodization, and stored in Neo4j. Evaluation comprised three NER
scenarios, SNA, and six functional queries.
The best result was achieved by uncased IndoBERT with data augmentation, obtaining a
micro F1-score of 0.9756. The knowledge graph contained 1,192 nodes and 728 relationships.
The projected person network comprised 137 nodes and 1,853 edges, forming eight
communities with a Louvain modularity of 0.2831. Muhammad ranked highest across all
centrality measures. All six functional queries ran successfully, returned nonempty results, and
were traceable to the source, although some relationships still require
verification against the source text.

Keywords: IndoBERT; Knowledge Graph; Named-Entity Recognition; Sirah
Nabawiyah; Social Network Analysis
