# BAB 2 TINJAUAN PUSTAKA

<!-- SINKRON STRUKTURAL dengan buku `docs/Buku-TA-Genta.pdf` (hlm 6-32).
     Sumber sahih = buku Word/PDF. File ini = cermin struktur + prosa; persamaan, tabel, dan
     gambar ditandai sebagai placeholder [Persamaan/Tabel/Gambar X] yang isinya ada di buku.
     Perbaikan §2.3.3 (disclaimer SRL, opsi 2) diterapkan. Saran lain (nama Yifan/Du, kurung
     sitasi, pola APA, typo Persamaan 2.13) sudah dikoreksi user di Word. SNA sengaja digabung
     ke §2.7 atas permintaan pembimbing. -->

## 2.1 Hasil Penelitian Terdahulu

Penelitian ini merujuk pada sejumlah penelitian terdahulu yang berkaitan dengan tiga topik utama, yaitu pembangunan *knowledge graph* (graf pengetahuan), ekstraksi informasi melalui *Named-Entity Recognition* (NER) dan ekstraksi relasi, serta pemanfaatan *graph database* seperti Neo4j untuk penyimpanan dan penelusuran pengetahuan berbasis relasi. Penelitian-penelitian tersebut menjadi landasan untuk memahami tahapan umum konstruksi *knowledge graph*, pendekatan yang lazim diterapkan pada berbagai domain, serta bentuk evaluasi yang biasa digunakan untuk menilai kelayakan hasil konstruksi graf.

Penelitian terdahulu berjudul "A Comprehensive Survey on Automatic Knowledge Graph Construction" oleh Zhong et al. (2024) menyajikan tinjauan sistematis terkait perkembangan metode konstruksi *knowledge graph* secara otomatis. Studi ini mengkaji lebih dari 300 metode dan mengelompokkan proses konstruksi ke dalam tiga tahap utama, yaitu *knowledge acquisition*, *knowledge refinement*, dan *knowledge evolution*.

Penelitian kedua berjudul "A Knowledge Graph Construction Method for Complex Products Improvement Design" oleh Ren et al. (2024) membahas konstruksi *knowledge graph* pada domain produk kompleks. Metodenya melibatkan pengumpulan data multi-sumber, ekstraksi pengetahuan, serta pemodelan *function-behavior-structure* (FBS), dengan graf dikonstruksi di bawah panduan ontologi.

Penelitian ketiga berjudul "Automatic knowledge-graph creation from historical documents: The Chilean dictatorship as a case study" oleh Díaz et al. (2024) berfokus pada konstruksi *knowledge graph* dari dokumen historis. Penelitian ini menggunakan *Large Language Models* (LLM) untuk mengenali entitas dan relasi, dengan interaksi yang *grounded* pada ontologi sederhana untuk menekan halusinasi, lalu dievaluasi terhadap *gold standard graph*.

Penelitian keempat "BioKGrapher: Initial evaluation of automated knowledge graph construction from biomedical literature" oleh Schäfer et al. (2024) memperkenalkan alat konstruksi *knowledge graph* otomatis dari publikasi biomedis skala besar. Metodenya diawali *Named Entity Recognition and Linking* (NER+NEL), normalisasi ke UMLS, pembobotan konsep, lalu integrasi menjadi *knowledge graph* hierarkis.

Penelitian kelima "Construction of a Traditional Chinese Medicine Dao Yin Science Knowledge Graph Based on Neo4j" oleh Xie et al. (2023) membangun *knowledge graph* domain Dao Yin memakai BERT-CRF untuk NER disertai pengecekan manual, lalu diimplementasikan di Neo4j dan ditelusuri melalui *Cypher*.

Penelitian keenam "Construction of Military Knowledge Graph Based on Neo4j and MongoDB" oleh He et al. (2022) mengusulkan *panoramic military knowledge graph* yang menyatukan pengetahuan multi-sumber pada level semantik, dengan hasil disimpan pada Neo4j dan MongoDB.

Penelitian ketujuh "Enhanced Entity Recognition of Islamic Hadiths based-on Hybrid LSTM and AraBERT Model" oleh Nados (2024) melatih model NER untuk teks hadis berbahasa Arab memakai skema BIO. Model hibrida AraBERT-LSTM mencapai akurasi sekitar 0,981, melampaui model tunggal.

Penelitian kedelapan "Graph-based Named Entity Information Retrieval from News Articles using Neo4j" oleh Chaudhary et al. (2024) mengonversi teks mentah menjadi *knowledge graph* dengan mengintegrasikan *entity linking* dan *relation extraction* secara terpadu, lalu disimpan di Neo4j.

Penelitian kesembilan "Knowledge Extraction from Multilingual and Historical Texts for Advanced Question Answering" oleh Graciotti (2023) menggabungkan pendekatan *Semantic Web* dan *Natural Language Processing* untuk *question answering* pada teks diakronik, serta menyoroti tantangan *noise* OCR dan bias *entity linking* pada entitas historis.

Penelitian terakhir berjudul "The Construction of Knowledge Graph of Newspaper Distribution in Yan'an Period and Frontend Visualization" oleh Yifan (2023) mengusulkan konstruksi *knowledge graph* (ekstraksi informasi, penggabungan, pengolahan, penyimpanan) dilengkapi visualisasi *front-end*, menghasilkan graf dengan 15 ontologi, 27.349 relasi, 4.074 surat kabar, dan 10.616 entitas.
[Tabel 2.1: Hasil Penelitian Terdahulu — perbandingan Penelitian, Sumber Data, Metode, Analisis untuk 10 studi di atas]

Berdasarkan penelitian terdahulu, terlihat bahwa konstruksi *knowledge graph* umumnya memerlukan tahapan ekstraksi entitas dan relasi, pemodelan skema, serta penyimpanan graf yang umumnya menggunakan Neo4j agar pengetahuan dapat ditelusuri melalui kueri graf. Namun, sebagian besar studi masih berfokus pada domain berita, biomedis, militer, atau arsip sejarah tertentu, dan belum ada yang secara spesifik membangun *knowledge graph* untuk Sirah Nabawiyah berbahasa Indonesia dengan kategori entitas minimal seperti *Person*, *Event*, *Location*, dan *Time*. Selain itu, pendekatan ekstraksi berbasis SRL semi-*supervised* yang hemat data (Ariyanto et al., 2025) belum pernah dipadukan dengan konstruksi *knowledge graph* Sirah, dan *Social Network Analysis* terhadap *knowledge graph* sejarah Islam juga belum disentuh. Penelitian ini menutup celah tersebut dengan mengadaptasi alur konstruksi *knowledge graph* untuk domain Sirah, mulai dari ekstraksi entitas berbasis SRL dengan *iterative self-training*, pembangunan graf di Neo4j, hingga evaluasi terbatas untuk memastikan kualitas ekstraksi entitas dan relasi serta kelayakan graf untuk penelusuran relasional.

## 2.2 Sirah Nabawiyah

Sirah Nabawiyah merupakan kisah sejarah yang merekam perjalanan hidup Nabi Muhammad SAW beserta kondisi masyarakat dan berbagai peristiwa yang terjadi pada masanya (Solihin, 2022). Dalam tradisi keilmuan Islam, Sirah memiliki hubungan yang erat dengan hadis, tempat hadis menjadi salah satu sumber utama dalam penyusunan Sirah, sedangkan Sirah membantu menjelaskan hadis melalui latar belakang peristiwa dan urutan waktunya. Kajian ilmiah kontemporer juga banyak membahas hubungan keduanya, termasuk pandangan bahwa hadis merupakan bagian dari Sirah, tetapi tidak seluruh isi Sirah termasuk dalam ruang lingkup hadis (Kharis, 2024).

Dalam perkembangan penulisan sejarah Islam, Sirah telah disusun sejak masa awal dan menjadi rujukan penting setelah kajian hadis atau sunnah. Karya-karya klasik, seperti Sirah Ibn Ishaq yang kemudian disempurnakan oleh Ibn Hisham, menunjukkan upaya sistematis untuk menyajikan perjalanan hidup Nabi secara berurutan serta menghimpun berbagai riwayat dalam satu narasi (Prayogi et al., 2022). Penelitian modern memandang karya-karya tersebut sebagai fondasi penting dalam studi Sirah, sekaligus mengkajinya menggunakan pendekatan historiografi kontemporer melalui analisis metode penulisan, karakteristik narasi, dan perbandingan antar karya Sirah modern. Oleh karena itu, Sirah tidak hanya dipahami sebagai teks keagamaan, tetapi juga sebagai karya sejarah yang ditulis dengan berbagai pendekatan (Abror & Rahma, 2024).

Dari segi bentuk penyajian, Sirah umumnya ditulis sebagai narasi yang mengikuti urutan waktu dan memuat unsur-unsur faktual, seperti tokoh, peristiwa, lokasi, dan waktu. Hubungan antara unsur-unsur tersebut sering kali tidak dijelaskan secara langsung, melainkan tersirat dalam susunan kalimat dan paragraf, sehingga informasi mengenai hubungan antar-entitas tersebar di berbagai bagian teks. Berdasarkan karakteristik tersebut, Sirah Nabawiyah dapat dipandang sebagai korpus naratif, yaitu kumpulan teks yang kaya akan informasi mengenai tokoh dan peristiwa. Karakteristik ini menjadi landasan penelitian yang mencakup pembentukan korpus, pembersihan hasil *Optical Character Recognition* (OCR) atau pengenalan teks dari gambar, serta ekstraksi entitas dan relasi agar informasi yang terkandung di dalamnya dapat disusun secara lebih terstruktur dalam basis data graf.

## 2.3 Named-Entity Recognition Berbasis Semantic Role Labelling

*Named-Entity Recognition* berbasis *Semantic Role Labeling* merupakan pendekatan ekstraksi informasi yang tidak hanya menempatkan entitas sebagai unit teks yang perlu dikenali, tetapi juga sebagai bagian dari struktur makna dalam suatu peristiwa. Dalam teks naratif, informasi umumnya tersusun melalui keterlibatan tokoh, kejadian, lokasi, dan waktu yang saling berkaitan. Kajian ekstraksi naratif menempatkan narasi sebagai rangkaian peristiwa yang melibatkan beberapa aktor, berlangsung pada lokasi tertentu, dan tersusun dalam urutan temporal tertentu (Santana et al., 2023). Karakter tersebut selaras dengan teks Sirah Nabawiyah yang memuat perjalanan tokoh, rangkaian peristiwa, tempat kejadian, serta fase waktu yang membentuk struktur historis.

Dalam kerangka *information extraction*, teks alami perlu diubah menjadi pengetahuan terstruktur agar dapat dianalisis lebih lanjut. Entitas, relasi, dan peristiwa menjadi komponen utama yang diekstraksi dari teks untuk mendukung berbagai proses komputasional, termasuk pembangunan *knowledge graph* (Xu et al., 2024). Pada posisi ini, NER berperan untuk mengenali unit informasi berupa entitas, sedangkan orientasi peran semantik ala SRL membantu menjelaskan peran entitas tersebut dalam suatu peristiwa. Pendekatan ini sejalan dengan kajian Ariyanto et al. (2025) yang menempatkan NER dan SRL sebagai bagian dari *information extraction* pada teks berbahasa Indonesia.

### 2.3.1 Named-Entity Recognition

*Named-Entity Recognition* (NER) adalah tugas dalam NLP untuk mengenali *span* teks yang menyebut entitas bernama dan mengklasifikasikannya ke dalam kategori semantik yang telah ditentukan, seperti *person*, *location*, dan *organization* (J. Li et al., 2022). Dalam penerapannya, NER tidak hanya membantu memahami isi teks secara semantik, tetapi juga menjadi fondasi bagi berbagai tugas lanjutan seperti *information extraction* dan *relation extraction*, sistem tanya jawab, serta konstruksi struktur pengetahuan seperti *knowledge base* dan *knowledge graph* (Xu et al., 2024; Zhao et al., 2024). Jenis label entitas yang biasa digunakan dalam NER ditunjukkan pada Tabel 2.2, dan seluruh label tersebut dapat disesuaikan dengan kebutuhan atau konteks analisis pada domain tertentu.

[Tabel 2.2: Contoh Daftar Label NER — PERSON, LOC, ORG, DATE, TIME, EVENT beserta deskripsinya]

[Gambar 2.1: Contoh Hasil Penerapan NER pada Teks Bahasa Inggris (Chaudhary et al., 2024)]

Sebagai gambaran, Gambar 2.1 menunjukkan penerapan NER pada potongan paragraf teks berbahasa Inggris. Setiap entitas yang ditemukan diberi label dengan warna berbeda, seperti PERSON untuk "Tencent", ORG untuk "Google", "IBM", dan "Microsoft", serta DATE untuk "2018-2024" dan "2017". Gambaran ini menunjukkan NER menandai dan mengelompokkan elemen penting dalam teks sehingga informasi menjadi lebih terstruktur.

Pada pendekatan *sequence labeling*, NER dilakukan dengan memberikan label pada setiap token dalam kalimat. Salah satu skema pelabelan yang umum digunakan adalah BIO atau *Begin-Inside-Outside*. Skema BIO membedakan token awal entitas, token lanjutan dari entitas yang sama, dan token yang tidak termasuk entitas, sehingga model tidak hanya mengenali jenis entitas tetapi juga batas awal dan akhir entitas dalam teks (J. Li et al., 2022). Penjelasan setiap label BIO dirangkum pada Tabel 2.3.

[Tabel 2.3: Penjelasan Label BIO — B-XXX (awal entitas), I-XXX (lanjutan entitas), O (di luar entitas)]

Perkembangan *deep learning* membuat NER tidak lagi bergantung pada aturan manual atau fitur linguistik eksplisit. Model NER modern umumnya terdiri atas representasi input, *context encoder*, dan *tag decoder*, yang mencerminkan proses representasi token, pemahaman konteks, dan prediksi label entitas (J. Li et al., 2022). Pada bahasa Indonesia, NER masih menghadapi tantangan berupa keterbatasan korpus dan inkonsistensi anotasi yang dapat memengaruhi akurasi model (Oryza et al., 2020), sehingga penting bagi penelitian ini untuk menjaga konsistensi anotasi pada korpus Sirah Nabawiyah yang bersifat domain spesifik.

Dalam penelitian ini, entitas yang digunakan meliputi *Person*, *Event*, *Location*, dan *Time*. Pemilihan kategori tersebut disesuaikan dengan karakter Sirah Nabawiyah sebagai teks naratif-historis. *Person* merepresentasikan tokoh, *Event* merepresentasikan peristiwa penting, *Location* merepresentasikan tempat kejadian, sedangkan *Time* merepresentasikan waktu atau fase peristiwa.

### 2.3.2 Semantic Role Labelling

*Semantic Role Labeling* (SRL) merupakan tugas NLP yang merepresentasikan makna kalimat melalui struktur predikat dan argumen. Predikat biasanya menunjukkan tindakan, keadaan, atau peristiwa, sedangkan argumen menunjukkan unsur yang terlibat dalam predikat tersebut. Kajian *Universal Proposition Bank* 2.0 menempatkan SRL sebagai analisis semantik dangkal yang membantu menjembatani struktur sintaksis menuju representasi makna melalui identifikasi predikat, penentuan makna predikat, identifikasi argumen, dan pemberian label peran semantik pada setiap argumen (Jindal et al., 2022).

Dalam *information extraction*, SRL berfungsi memperjelas hubungan antara predikat dan argumen dalam teks tidak terstruktur. Kajian sistematis tentang SRL pada data *low-resource* menempatkan SRL sebagai salah satu tugas penting untuk mengidentifikasi peran semantik sehingga pemahaman terhadap teks dapat diperkaya (Ariyanto et al., 2025). Posisi ini penting karena teks naratif sering kali menyimpan hubungan antarentitas secara implisit melalui struktur kalimat, bukan melalui relasi yang ditulis secara eksplisit.

Pada teks Sirah Nabawiyah, kebutuhan terhadap orientasi peran muncul karena tokoh, lokasi, waktu, dan peristiwa sering berada dalam satu rangkaian narasi. Kalimat seperti "Nabi Muhammad hijrah ke Madinah" tidak hanya memuat entitas *Person* dan *Location*, tetapi juga memuat peristiwa dan arah keterlibatan tokoh di dalamnya. NER dapat mengenali "Nabi Muhammad" sebagai *Person*, "hijrah" sebagai *Event*, dan "Madinah" sebagai *Location*, sedangkan kerangka peran semantik membantu memahami bahwa tokoh tersebut berperan sebagai pihak yang terlibat dalam peristiwa hijrah dan Madinah berperan sebagai tujuan atau lokasi peristiwa.

### 2.3.3 SRL-Based Named-Entity Recognition

*SRL-Based Named-Entity Recognition* dalam penelitian ini mengacu pada pendekatan *information extraction* yang mengaitkan pengenalan entitas dengan peran semantik dalam suatu peristiwa. Pendekatan ini selaras dengan kajian Ariyanto et al. (2025) yang menempatkan *Named-Entity Recognition* dan *Semantic Role Labeling* sebagai bagian penting dalam ekstraksi informasi teks Indonesia. Dalam kerangka tersebut, NER digunakan untuk mengenali entitas, sedangkan orientasi peran semantik ala SRL dipakai sebagai dasar konseptual dalam menentukan kategori entitas yang diekstraksi.

Penguatan hubungan antara NER dan SRL juga terlihat pada dataset peristiwa krisis berbahasa Indonesia yang dikembangkan oleh Ariyanto et al. (2025). Dataset tersebut menyediakan label argumen untuk tugas SRL dan label entitas untuk tugas NER dalam satu kerangka data, yang menunjukkan bahwa entitas dan peran semantik dapat digunakan secara saling melengkapi dalam *information extraction*. Gagasan ini relevan dengan penelitian Sirah Nabawiyah karena teks yang digunakan juga memuat struktur peristiwa yang melibatkan tokoh, lokasi, waktu, dan kejadian tertentu. Dalam penelitian ini, pendekatan *SRL-Based NER* tidak dimaksudkan untuk menggantikan NER, melainkan untuk memperkuat hasil pengenalan entitas melalui konteks peran semantik. Entitas *Person*, *Event*, *Location*, dan *Time* tidak hanya dikenali sebagai label, tetapi juga diarahkan untuk dipahami melalui keterlibatannya dalam suatu peristiwa. Tokoh dapat berperan sebagai pelaku, saksi, lawan, atau pihak yang terlibat, lokasi dapat berfungsi sebagai tempat kejadian atau tujuan perpindahan, sedangkan waktu dapat menunjukkan urutan atau fase historis. Perlu ditegaskan bahwa penelitian ini tidak menjalankan pengurai (*parser*) SRL secara penuh. Orientasi peran tersebut diwujudkan secara praktis pada tahap pelabelan awal semi-otomatis (Subbab 3.5.1) melalui pencocokan kamus entitas (*gazetteer*) dan pola ekspresi reguler (*regex*), sehingga istilah *SRL-Based* di sini mengikuti kerangka konseptual Ariyanto et al. (2025) sebagai landasan pemikiran, bukan sebagai modul SRL yang dijalankan pada teks.

Hubungan antara SRL dan *knowledge graph* terlihat pada metode yang mengubah teks menjadi graf berbasis *frame*. TakeFive, misalnya, merupakan metode *semantic role labeling* yang melakukan *dependency parsing*, mengidentifikasi kata yang memunculkan *frame* leksikal, menemukan *role* dan *filler* untuk tiap *frame*, lalu memformalkan hasilnya sebagai *knowledge graph* (Alam et al., 2021). Pendekatan tersebut menunjukkan bahwa peran semantik dapat menjadi jembatan antara analisis kalimat dan representasi pengetahuan berbasis relasi. Dengan demikian, kerangka *SRL-Based NER* dalam penelitian ini diposisikan sebagai jembatan konseptual antara pengenalan entitas dan pembangunan *knowledge graph* Sirah Nabawiyah: NER menghasilkan entitas utama dari teks, sedangkan orientasi peran membantu menafsirkan peran entitas tersebut dalam struktur peristiwa, yang kemudian diarahkan untuk membentuk relasi seperti tokoh-terlibat-dalam-peristiwa, peristiwa-terjadi-di-lokasi, dan peristiwa-terjadi-pada-waktu tertentu.
## 2.4 Transformer-Based Model untuk Sequence Labeling

*Transformer-based model* merupakan pendekatan pemodelan bahasa yang banyak digunakan dalam tugas *Natural Language Processing*, termasuk *sequence labeling*. Pada tugas *sequence labeling*, setiap token dalam suatu urutan teks diberi label tertentu sesuai konteksnya. NER termasuk tugas *sequence labeling* karena model perlu menentukan label entitas pada setiap token, misalnya apakah token tersebut termasuk *Person*, *Event*, *Location*, *Time*, atau bukan entitas.

Perkembangan model berbasis *Transformer* menjadi penting dalam NER karena model ini mampu menghasilkan representasi token yang mempertimbangkan konteks kalimat. Kajian mutakhir menunjukkan bahwa pendekatan berbasis *Transformer* dan LLM menjadi bagian penting dalam perkembangan NER modern karena kemampuannya menangkap konteks (Keraghel et al., 2024). Kajian lain menempatkan mekanisme *self-attention* sebagai mekanisme utama yang membantu model menangkap ketergantungan kontekstual antar-token secara lebih efektif dibandingkan pendekatan berbasis fitur manual (Fu, 2025). Oleh karena itu, pendekatan *Transformer-based model* relevan digunakan pada penelitian ini karena teks Sirah Nabawiyah memiliki struktur naratif yang panjang, kaya tokoh, serta memuat hubungan antar-kata yang bergantung pada konteks peristiwa.

### 2.4.1 Transformer

*Transformer* merupakan arsitektur *deep learning* yang banyak digunakan dalam pemrosesan bahasa alami karena kemampuannya membangun representasi kontekstual dari urutan token. Paaß dan Giesselbach (2023) menjelaskan bahwa model bahasa berbasis *attention* memproses teks sebagai urutan token dan menghasilkan *contextual embedding* untuk setiap token. Rahali dan Akhloufi (2023) menyatakan bahwa arsitektur *Transformer* menggunakan *self-attention* untuk menangkap ketergantungan jarak jauh dalam urutan masukan, sehingga makna suatu token dipengaruhi oleh token lain dalam konteks yang sama. Hal ini sejalan dengan Patwardhan et al. (2023) yang menjelaskan bahwa model *Transformer* seperti BERT mampu mempelajari representasi kontekstual kata berdasarkan konteks token di sekitarnya. Selain itu, Sajun et al. (2024) menggambarkan arsitektur *Transformer* sebagai model yang terdiri atas komponen utama seperti *multi-head attention*, *feed-forward network*, *positional encoding*, serta struktur *encoder* dan *decoder*, sebagaimana ditunjukkan pada Gambar 2.2.
Pada tugas NER, kemampuan menangkap konteks sangat penting karena label suatu token sering bergantung pada token di sekitarnya, misalnya suatu kata dapat dikenali sebagai nama tokoh apabila muncul bersama gelar, kata kerja tertentu, atau konteks peristiwa. Kajian NER berbasis *Transformer* pada dokumen hukum Indonesia menunjukkan bahwa model seperti IndoBERT, IndoRoBERTa, mBERT, dan XLM-RoBERTa dapat mengenali entitas pada domain spesifik dengan performa kompetitif (Yulianti et al., 2024). Ilustrasi pemanfaatan *Transformer* dalam pelabelan token ditunjukkan pada Gambar 2.3.

[Gambar 2.2: Ilustrasi Arsitektur Transformer (Sajun et al., 2024)]
[Gambar 2.3: Ilustrasi Pelabelan Token dengan Transformer (Schweter & Akbik, 2021)]

Pada Gambar 2.3, setiap token masukan diproses bersama konteks di sekitarnya sehingga menghasilkan representasi kontekstual yang kemudian digunakan untuk memprediksi label token, misalnya B-LOC untuk token awal entitas lokasi dan O untuk token yang tidak termasuk entitas. Dalam penelitian ini, *Transformer* diposisikan sebagai dasar arsitektur model untuk menghasilkan representasi token dari teks Sirah Nabawiyah sebelum dilakukan klasifikasi token pada proses *sequence labeling*.

### 2.4.2 BERT dan IndoBERT

BERT merupakan salah satu model berbasis *Transformer encoder* yang banyak digunakan dalam tugas NLP karena mampu menghasilkan representasi kata secara kontekstual. Dalam tugas NER, BERT digunakan untuk menghasilkan *embedding* setiap token berdasarkan konteks kalimatnya, yang kemudian diproses oleh lapisan klasifikasi untuk menentukan label entitas. Penerapan BERT dalam NER domain khusus terlihat pada penelitian Ge et al. (2024) yang menggunakan BERT untuk memperoleh representasi kata sebelum diproses dalam model BERT-BiLSTM-CRF pada domain *dietary elderly*. Secara arsitektural, BERT dibangun dari tumpukan *Transformer encoder*, dengan setiap *encoder layer* memuat *input representation*, *attention mechanism*, dan *feedforward neural network*, sebagaimana ilustrasi pada Gambar 2.4.

[Gambar 2.4: Ilustrasi Arsitektur BERT (Ge et al., 2024)]

Pada konteks bahasa Indonesia, model *pre-trained* berbasis BERT menjadi penting karena karakteristik bahasa, kosakata, dan struktur kalimatnya berbeda dari bahasa Inggris. Model yang dilatih pada korpus Indonesia dapat memberikan representasi token yang lebih sesuai untuk teks berbahasa Indonesia (Yulianti et al., 2024). Dalam penelitian ini, digunakan lima model berbasis *Transformer* sebagai skenario perbandingan. Model `indolem/indobert-base-uncased` digunakan sebagai *baseline*, sedangkan empat model lain digunakan sebagai pembanding untuk melihat pengaruh variasi model *pre-trained* terhadap performa NER. Informasi model yang digunakan ditunjukkan pada Tabel 2.4.

[Tabel 2.4: Perbandingan Model yang Digunakan — indolem/indobert-base-uncased (baseline), cahya/bert-base-indonesian-1.5G, cahya/distilbert-base-indonesian, indobenchmark/indobert-base-p1, cahya/roberta-base-indonesian-1.5G]

Dengan membandingkan kelima model tersebut, penelitian ini dapat melihat model mana yang paling sesuai untuk mengenali entitas *Person*, *Event*, *Location*, dan *Time* pada teks Sirah Nabawiyah.

## 2.5 Strategi Penanganan Ketidakseimbangan Label

Ketidakseimbangan label merupakan salah satu tantangan dalam tugas NER, terutama pada pendekatan *sequence labeling*. Sebagian besar token biasanya berlabel O karena tidak termasuk entitas, sedangkan token yang merepresentasikan entitas seperti *Person*, *Event*, *Location*, dan *Time* muncul dalam jumlah lebih sedikit. Kondisi ini dapat membuat model lebih mudah mempelajari kelas mayoritas dan kurang sensitif terhadap kelas minoritas (Nemoto et al., 2025). Selain itu, strategi *re-weighting* token juga digunakan untuk mengurangi dominasi kelas mayoritas dalam proses pembelajaran model NER (Luo et al., 2023). Berdasarkan karakteristik tersebut, penelitian ini mempertimbangkan beberapa strategi, yaitu *class weight*, *data augmentation*, *supervised contrastive learning*, dan *joint supervised contrastive learning*.

### 2.5.1 Class Weight

*Class weight* merupakan strategi penanganan ketidakseimbangan label dengan memberikan bobot berbeda pada setiap kelas ketika menghitung fungsi *loss*. Kelas dengan jumlah sampel lebih sedikit diberi bobot lebih besar, dan sebaliknya. Pendekatan ini berkaitan dengan *weighted cross-entropy*, yaitu modifikasi *cross-entropy* yang mempertimbangkan bobot kelas dalam optimasi (Nemoto et al., 2025).

[Persamaan 2.1: bobot mentah kelas, w_c^raw = N / (C × n_c), dengan N=jumlah token, C=jumlah kelas, n_c=jumlah token kelas c]

Dalam penelitian ini, bobot mentah tidak dipakai langsung karena bobot kelas minoritas dapat menjadi terlalu besar. Bobot dinormalisasi terhadap label O dan diberi *tempering* akar kuadrat agar perbedaan bobot antar-label tetap proporsional.

[Persamaan 2.2: w_c = sqrt(w_c^raw / w_O^raw)]
[Persamaan 2.3: bentuk setara, w_c = sqrt(n_O / n_c)]
[Persamaan 2.4: weighted cross-entropy, L_WCE, memakai bobot w di atas]

Pendekatan ini sejalan dengan *re-weighting* pada NER, yaitu pemberian bobot terhadap token atau kelas agar model tidak terlalu didominasi label mayoritas (Luo et al., 2023).

### 2.5.2 Data Augmentation

*Data augmentation* merupakan strategi menambah variasi data latih melalui pembentukan sampel baru dari data yang tersedia. Pada NER, augmentasi harus dilakukan hati-hati karena perubahan token dapat memengaruhi batas entitas dan label BIO. Elwing Torres et al. (2026) mengevaluasi teknik seperti *mention replacement* dan *contextual word replacement* pada NER domain *low-resource*, dan menyimpulkan bahwa augmentasi membantu ketika data latih terbatas tetapi jumlah serta jenisnya perlu disesuaikan dengan karakteristik dataset.

[Persamaan 2.5: D_aug = D ∪ {T_k(x_i, y_i)}, dengan D=dataset awal, T_k=transformasi ke-k, y_i=label yang harus tetap konsisten]

Dalam konteks NER, salah satu bentuk augmentasi adalah mengganti *mention* entitas dengan *mention* lain bertipe sama sehingga struktur label tetap terjaga. Chen et al. (2024) juga menunjukkan bahwa *data augmentation* dapat diterapkan pada NER medis untuk meningkatkan variasi data ketika data berlabel terbatas.
### 2.5.3 Supervised Contrastive Learning

*Supervised Contrastive Learning* (SCL) merupakan strategi pembelajaran representasi yang mendorong sampel berlabel sama agar berdekatan, sementara sampel berlabel berbeda dibuat lebih berjauhan. Pada NER, prinsip ini dapat diterapkan pada level token sehingga token dengan label entitas sama memiliki representasi yang lebih konsisten. Das et al. (2022) melalui CONTaiNER menerapkan *contrastive learning* pada *few-shot* NER untuk mendekatkan representasi token dari kategori sama dan menjauhkan token dari kategori berbeda.

[Persamaan 2.6: L_SCL, dengan B=ukuran batch, P(i)=sampel positif berlabel sama dengan anchor i, A(i)=seluruh pembanding, z=embedding, sim(.)=fungsi kesamaan, tau=temperature]

Dalam penelitian ini, SCL dapat membantu model membentuk representasi token yang lebih diskriminatif, terutama pada label entitas yang jumlahnya lebih sedikit.

### 2.5.4 Joint Supervised Contrastive Learning

*Joint Supervised Contrastive Learning* (JSCL) merupakan pengembangan dari *supervised contrastive learning* dengan mempertimbangkan kemiripan antarlabel secara lebih fleksibel. Representasi tidak hanya dipelajari berdasarkan kesamaan label identik, tetapi juga tingkat kesamaan antarlabel. Pendekatan yang digunakan memanfaatkan kesamaan Jaccard untuk mengatur kedekatan representasi berdasarkan *overlap* label.

[Persamaan 2.7: kesamaan Jaccard, J(y_i, y_j) = |y_i ∩ y_j| / (|y_i ∪ y_j| + eps)]
[Persamaan 2.8: bobot pasangan, alpha_ij dinormalisasi dari J(y_i, y_j)]
[Persamaan 2.9: L_JSCL memakai bobot alpha_ij]
[Persamaan 2.10: loss gabungan, L_total = L_CE + lambda × L_JSCL]

Dalam skenario NER, JSCL memberi ruang pada relasi antarlabel yang tidak sepenuhnya identik, misalnya label dengan kategori entitas sama tetapi posisi BIO berbeda, sehingga representasi token diarahkan berdasarkan tingkat kedekatan semantik atau struktural antarlabel, bukan sekadar benar-salah label secara kaku.

## 2.6 POS Tagging

*Part-of-Speech Tagging* atau POS *tagging* merupakan proses pemberian label kelas kata pada setiap token dalam teks, seperti nomina, verba, adjektiva, adverbia, numeralia, dan preposisi. Dalam NLP, POS *tagging* membantu sistem mengenali fungsi gramatikal suatu kata dalam kalimat, dan menjadi tahap pendukung bagi tugas lain seperti *parsing*, *information extraction*, *machine translation*, serta analisis semantik (Chiche & Yitagesu, 2022). Ilustrasi sederhana proses POS *tagging* ditunjukkan pada Tabel 2.5.

[Tabel 2.5: Contoh Penggunaan POS Tagging — Token, POS Tag, Keterangan, Contoh label NER; mis. "Nabi" PROPN B-PERSON, "hijrah" VERB B-EVENT, "Madinah" PROPN B-LOCATION, "tahun/622/M" TIME]

Pada teks naratif, termasuk Sirah Nabawiyah, informasi penting tidak hanya muncul sebagai entitas tetapi juga melalui struktur gramatikal kalimat. Tokoh biasanya muncul sebagai nomina atau *proper noun*, tindakan dan peristiwa sering direpresentasikan melalui verba, sedangkan lokasi dan waktu dapat dikenali melalui kombinasi nomina, numeralia, preposisi, atau keterangan waktu. Dalam konteks NER, POS *tagging* dapat digunakan sebagai informasi pendukung karena kelas kata tertentu sering berkaitan dengan kemunculan entitas. Penelitian Y. Chen et al. (2023) pada NER bahasa Korea menunjukkan bahwa penggunaan fitur linguistik spesifik bahasa dapat memengaruhi performa pengenalan entitas.

Perkembangan POS *tagging* juga mengikuti perkembangan *deep learning* dan *Transformer*. H. Li et al. (2022) mengembangkan pendekatan POS *tagging* yang menggabungkan *rule-based preprocessing* dan *Transformer*. Untuk bahasa Indonesia dan bahasa daerah, POS *tagging* memiliki tantangan tersendiri akibat keterbatasan korpus beranotasi; Enrique et al. (2024) meneliti POS *tagging* bahasa Jawa sebagai bahasa *low-resource* memanfaatkan *transfer learning* lintas bahasa dan model *Transformer* seperti IndoBERT, mBERT, dan XLM-RoBERTa. Dalam penelitian ini, POS *tagging* diposisikan sebagai informasi linguistik pendukung untuk membantu analisis token pada teks Sirah Nabawiyah, bukan sebagai tujuan utama.

## 2.7 Knowledge Graph
*Knowledge Graph* merupakan representasi pengetahuan dalam bentuk graf yang menghubungkan entitas melalui relasi semantik. Peng et al. (2023) menjelaskan bahwa *knowledge graph* direpresentasikan sebagai graf berarah yang terdiri atas *node* (entitas, objek, atau konsep) dan *edge* (relasi semantik antar-entitas). Satuan dasar dalam *knowledge graph* dapat dipahami sebagai *triple*, yaitu kombinasi subjek, predikat, dan objek; Ji et al. (2022) menuliskannya sebagai *head*, *relation*, dan *tail*. Misalnya, informasi "Nabi Muhammad hijrah ke Madinah" dapat direpresentasikan sebagai *triple* (Nabi Muhammad, hijrah ke, Madinah).

[Gambar 2.5: Ilustrasi triple pada Knowledge Graph (Ji et al., 2022)]

*Knowledge graph* memiliki beberapa komponen utama, yaitu entitas, relasi, atribut, dan skema. Choi dan Jung (2025) menjelaskan bahwa konstruksi *knowledge graph* mencakup proses *extraction*, *learning*, dan *evaluation*. Zhong et al. (2024) merinci tahapan *automatic knowledge graph construction* seperti *named entity recognition*, *entity typing*, *entity linking*, *relation extraction*, dan *knowledge graph refinement*, yang menunjukkan NER berperan sebagai langkah awal karena entitas yang dikenali menjadi dasar pembentukan *node*.

Pada teks Sirah Nabawiyah, *knowledge graph* relevan karena teks memuat banyak informasi naratif yang saling berkaitan (tokoh, peristiwa, tempat, waktu). Untuk penyimpanan dan pengelolaannya, penelitian ini menggunakan Neo4j yang menerapkan model *labeled property graph* (menyimpan *node*, *relationship*, *label*, dan *property*) serta bahasa kueri *Cypher* untuk menelusuri pola relasi.

Setelah *knowledge graph* terbentuk, graf dapat dianalisis menggunakan *Social Network Analysis* (SNA). Dalam penelitian ini, SNA bukan metode utama ekstraksi, melainkan pendekatan pendukung untuk membaca struktur hubungan pada graf. Menurut Adniati et al. (2023), SNA menerapkan konsep teori graf, dengan simpul sebagai representasi aktor atau entitas dan sisi sebagai representasi hubungan.

[Persamaan 2.11: G = (V, E), dengan V=himpunan simpul, E=himpunan sisi]

Fitur analisis graf yang digunakan pada penelitian ini mencakup ukuran sentralitas dan ukuran tingkat graf berikut.

[Persamaan 2.12: degree centrality, C_D(v) = deg(v) / (n-1)]
[Persamaan 2.13: betweenness centrality, C_B(v) = jumlah rasio jalur terpendek s ke t yang melewati v][Persamaan 2.14: closeness centrality, C_C(v) = (n-1) / jumlah jarak terpendek d(u,v)]
[Persamaan 2.15: density (graf tak berarah), D = 2m / (n(n-1))]
[Persamaan 2.16: modularity Louvain, Q]
[Persamaan 2.17: proyeksi co-participation antartokoh, A_PP = B B^T]
[Persamaan 2.18: PageRank, PR(i)]
[Persamaan 2.19: local clustering coefficient, C_v = 2 e_v / (k_v (k_v - 1))]
[Persamaan 2.20: transitivity, T = 3 × jumlah segitiga / jumlah triplet terhubung]

*Degree centrality* menunjukkan jumlah hubungan langsung suatu simpul; *betweenness centrality* menunjukkan peran simpul sebagai penghubung jalur terpendek; *closeness centrality* menunjukkan kedekatan struktural terhadap simpul lain (Adniati et al., 2023). *Density* mengukur kepadatan jaringan, dan deteksi komunitas dengan *Louvain method* berbasis *modularity* digunakan untuk melihat pengelompokan tokoh (Anuar et al., 2024). Graf antartokoh dibentuk melalui hubungan *co-participation* (dua tokoh terlibat pada peristiwa sama), *PageRank* menilai kepentingan relatif simpul (Zhang et al., 2021), sedangkan *clustering coefficient* dan *transitivity* mengukur kecenderungan terbentuknya hubungan segitiga (Sosa et al., 2021). Analisis juga dapat dilakukan melalui pembentukan sub-graf untuk mengamati lima peristiwa besar, serta graf lokasi untuk melihat lokasi yang berperan sentral. Hasil analisis ini tidak dimaknai sebagai penilaian historis atau keagamaan terhadap suatu tokoh, tetapi sebagai gambaran struktural berdasarkan relasi yang berhasil diekstraksi dari teks.

Selain analisis struktural dengan SNA di atas, kelayakan *knowledge graph* sebagai produk akhir juga perlu dinilai dari sisi fungsionalnya, yaitu apakah graf mampu menjalankan fungsi yang menjadi tujuan pembangunannya. Berbeda dengan metrik yang mengukur akurasi atau karakteristik struktur, evaluasi fungsional bersifat berbasis kebutuhan (*black-box*), yaitu graf diuji dengan mengajukan sejumlah pertanyaan penelusuran lalu menilai apakah graf dapat menjawabnya dengan benar dan dapat dipertanggungjawabkan ke sumbernya, tanpa memeriksa implementasi internalnya. [SITASI: sumber 2020+ tentang evaluasi fungsional atau berbasis tugas (*task-based*) pada *knowledge graph*]

Pendekatan yang lazim digunakan untuk maksud ini adalah *competency questions* (pertanyaan kompetensi), yaitu sekumpulan pertanyaan yang ditetapkan terlebih dahulu dan harus mampu dijawab oleh *knowledge graph* atau ontologi. *Competency questions* berperan ganda, yaitu sebagai spesifikasi kebutuhan yang menentukan cakupan pengetahuan yang harus direpresentasikan, sekaligus sebagai alat validasi karena keberhasilan graf dinilai dari kemampuannya menjawab pertanyaan-pertanyaan tersebut. [SITASI: sumber 2020+ tentang *competency questions* untuk evaluasi ontologi atau *knowledge graph*] Pada penelitian ini, *competency questions* diwujudkan sebagai sejumlah kebutuhan fungsional yang didefinisikan lebih dahulu, lalu diterjemahkan menjadi kueri *Cypher* dan diuji pada graf, sebagaimana dirinci pada Bab 3.
<!-- [CATATAN] Dua [SITASI] di atas perlu diisi sumber NYATA 2020-2026 (jangan mengarang).
     Konsep competency questions berasal dari Gruninger & Fox (1995) = terlalu lama untuk sumber utama;
     boleh disebut sebagai asal-usul HANYA bila pembimbing izinkan + ditemani sumber 2020+.
     Kata kunci pencarian: "competency questions knowledge graph/ontology evaluation 2020..2026",
     "task-based / functional evaluation knowledge graph". Anchor yang sudah dimiliki: Choi & Jung (2025)
     di subbab ini menyebut tahap evaluation pada konstruksi KG = pijakan generik bila perlu. -->

## 2.8 Metrik Evaluasi

Evaluasi pada *Named-Entity Recognition* (NER) dilakukan untuk mengukur kemampuan model dalam mengenali dan mengklasifikasikan entitas secara benar, dengan memperhatikan kesesuaian batas entitas dan jenis entitas terhadap anotasi sebenarnya. Evaluasi NER umumnya menggunakan tiga metrik utama, yaitu *precision*, *recall*, dan *F1-score*, serta dapat dilakukan dengan pendekatan *exact match* (batas dan tipe entitas harus sama persis) atau *relaxed match* (mempertimbangkan kecocokan parsial) (Seow et al., 2025). Karena distribusi label dalam NER sering tidak seimbang (Nemoto et al., 2025), ketiga metrik tersebut lebih sesuai daripada akurasi.

**1. Precision.** *Precision* mengukur proporsi prediksi entitas yang benar dibandingkan seluruh entitas yang diprediksi. Nilai *precision* tinggi menunjukkan sedikit *false positive* (Keraghel et al., 2024).

[Persamaan 2.21: Precision = TP / (TP + FP)]

**2. Recall.** *Recall* mengukur proporsi entitas sebenarnya yang berhasil dikenali model, sehingga menunjukkan kemampuan menangkap sebanyak mungkin entitas pada teks (Keraghel et al., 2024).

[Persamaan 2.22: Recall = TP / (TP + FN)]

**3. F1-Score.** *F1-score* merupakan rata-rata harmonik antara *precision* dan *recall*, memberikan ukuran seimbang antara ketepatan prediksi dan kemampuan menemukan entitas, terutama pada data dengan distribusi label tidak seimbang (Keraghel et al., 2024; Seow et al., 2025).

[Persamaan 2.23: F1 = 2 × Precision × Recall / (Precision + Recall)]
[Persamaan 2.24: F1 = 2TP / (2TP + FP + FN)]

**4. Micro Average dan Macro Average.** Evaluasi NER juga dirangkum menggunakan *micro-F1* dan *macro-F1* (Le-Duc et al., 2025). *Micro-F1* menjumlahkan seluruh TP, FP, dan FN dari semua kelas terlebih dahulu sehingga lebih dipengaruhi kelas mayoritas, sedangkan *macro-F1* menghitung F1 tiap kelas lalu merata-ratakannya sehingga lebih sensitif terhadap kelas minoritas. Pada MultiCoNER II, *entity-level macro-F1* digunakan sebagai metrik *leaderboard* karena memperlakukan seluruh label setara (Tan et al., 2023; Fetahu et al., 2023).

[Persamaan 2.25: F1_micro]
[Persamaan 2.26: F1_macro = (1/C) × jumlah F1 tiap kelas]

Karena penelitian ini menangani ketidakseimbangan label, *macro-F1* penting untuk melihat performa terhadap label minoritas, sementara *micro-F1* digunakan untuk melihat performa model secara umum.

