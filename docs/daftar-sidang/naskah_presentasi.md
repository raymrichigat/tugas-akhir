# Naskah Presentasi Sidang — Genta Putra Prayoga (5025221040)

> **Cara pakai.** Naskah lisan per slide (mengikuti `PPT_konten_terbaru.md`). Bukan untuk dibaca kata-per-kata — pahami alurnya, ucapkan dengan bahasamu sendiri. Target durasi **±15–18 menit** (tempo santai ±35–45 detik/slide, slide hasil sedikit lebih lama). Tanda **[klik]** = ganti slide. **[jeda]** = beri jeda sejenak.
>
> Angka sudah = buku final. Bila waktu mepet, slide yang boleh dipercepat/lompati ditandai *(opsional)*.

---

## Slide 1 — Judul
Assalamualaikum warahmatullahi wabarakatuh. Selamat pagi Bapak/Ibu dosen penguji dan pembimbing. Perkenalkan, saya Genta Putra Prayoga, NRP 5025221040. Izinkan saya mempresentasikan Tugas Akhir saya berjudul **"Pendekatan Named-Entity Recognition dalam Pembangunan Knowledge Graph Sirah Nabawiyah"**, di bawah bimbingan Ibu Dini Adni Navastara dan Ibu Ratih Nur Esti Anggraini. **[klik]**

## Slide 2 — Outline *(opsional, bisa cepat)*
Presentasi ini akan mencakup enam bagian: latar belakang, rumusan masalah, metode, implementasi, hasil dan pembahasan, lalu ditutup dengan kesimpulan dan saran. **[klik]**

## Slide 3 — Latar Belakang (Masalah)
Sirah Nabawiyah kaya akan informasi tokoh, peristiwa, lokasi, dan waktu. Namun semua itu tersaji sebagai **narasi panjang yang kronologis**, sehingga sulit ditelusuri secara relasional. Pencarian kata kunci biasa tidak cukup untuk menjawab pertanyaan seperti "siapa saja yang terlibat dalam suatu peristiwa" atau "peristiwa apa yang terjadi di suatu lokasi", karena keterkaitan antar-entitas itu **tidak tersimpan secara eksplisit** — harus ditelusuri manual. Maka dibutuhkan pendekatan yang bisa menyimpan dan menelusuri hubungan itu secara eksplisit. **[klik]**

## Slide 4 — Latar Belakang (Solusi: Knowledge Graph)
Solusinya adalah **Knowledge Graph** — representasi yang menyimpan tokoh, peristiwa, lokasi, dan waktu beserta hubungannya secara eksplisit. Alurnya: teks Sirah diproses dengan **NER** untuk mengekstrak empat jenis entitas — Person, Location, Event, Time — lalu dihubungkan dengan relasi inti seperti keterlibatan tokoh pada peristiwa, lokasi, dan waktu peristiwa, serta relasi antar-tokoh, dan disimpan di Neo4j. **[klik]**

## Slide 5 — Rumusan Masalah
Ada empat rumusan masalah: **pertama**, bagaimana menyiapkan data teks Sirah menjadi dataset siap pakai; **kedua**, bagaimana mengekstrak entitas menggunakan NER berbasis SRL dengan iterative self-training; **ketiga**, bagaimana membangun knowledge graph-nya di Neo4j; dan **keempat**, bagaimana mengevaluasi hasil NER melalui tiga uji coba serta menganalisis knowledge graph tersebut. **[klik]**

## Slide 6 — Metode Penelitian
Metode dirancang dalam lima tahap berurutan: preparasi data, preprocessing dan chunking, pelabelan data, ekstraksi entitas, konstruksi knowledge graph, lalu pengujian dan evaluasi. Saya akan jelaskan tiap tahap secara ringkas. **[klik]**

## Slide 7 — Preparasi Data
Sumber datanya buku Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri, terjemahan Bahasa Indonesia, sekitar 633 halaman hasil pindaian. Teksnya diekstrak dengan **PaddleOCR**, lalu disusun ulang mengikuti daftar isi — footer berulang dihapus, judul bab dikenali lewat pencocokan, menghasilkan struktur JSON hierarkis yang lalu dikonversi ke CSV per subbab. **[klik]**

## Slide 8 — Preprocessing & Chunking
Teks OCR dibersihkan: menyaring baris tak relevan, menghapus karakter non-informatif, menormalisasi apostrof Arab, dan memperbaiki spasi. Setelah bersih, teks dipecah menjadi **chunk** — potongan berukuran maksimal 1.500 karakter dengan aturan **kalimat tidak dipotong** dan overlap satu kalimat antar-chunk untuk menjaga konteks. Batas karakter dipakai di tahap ini karena chunking terjadi sebelum tokenisasi; ukurannya jauh di bawah batas token model. **[klik]**

## Slide 9 — Pelabelan Data
Pelabelan membentuk data anotasi yang berfungsi ganda: sebagai *seed* pelatihan sekaligus *ground truth* evaluasi. Prosesnya semi-otomatis — kandidat entitas dikenali lewat kamus dan pola regex, lalu **dikoreksi manual** dengan pedoman empat label. Terakhir, anotasi span dikonversi ke format BIO dan dibagi menjadi data latih dan uji. **[klik]**

## Slide 10 — Ekstraksi Entitas (NER berbasis SRL + Self-Training)
Inti metodenya. NER-nya **berbasis IndoBERT** dan mengambil kerangka konsep **Semantic Role Labeling** — artinya entitas dilihat dari perannya: pelaku menjadi Person, tempat menjadi Location, waktu menjadi Time, peristiwa menjadi Event. Perlu saya tegaskan, ini kerangka peran semantik lewat pola dan kamus, **bukan pengurai predikat-argumen penuh**. Modelnya dilatih semi-supervised dengan **iterative self-training**: dilatih dari seed, memprediksi data tak berlabel, prediksi yang **rata-rata keyakinannya di atas 0,9** diterima jadi pseudo-label, lalu model dilatih ulang — diulang sampai konvergen, maksimal enam iterasi. **[klik]**

## Slide 11 — Konstruksi Knowledge Graph
Setelah entitas diekstrak, graf disusun dalam empat tahap: **alias clustering** menyatukan variasi nama ke bentuk kanonik dengan bantuan Jaro-Winkler; **pembentukan relasi** dari kemunculan bersama, dengan Event sebagai pusat keterhubungan dan tiap relasi menyimpan bukti sumbernya; **periodisasi** memetakan peristiwa ke fase kronologis; lalu dimuat ke **Neo4j** dengan MERGE dan constraint keunikan agar tidak ada node ganda. **[klik]**

## Slide 11b — Skenario Pengujian
Sebelum masuk hasil, ini peta pengujiannya. Evaluasi terdiri dari **tiga uji coba NER** dan **analisis graf**, semuanya menjawab rumusan masalah keempat, dan dijalankan pada **pipeline serta data uji yang identik** supaya perbandingannya adil. Uji Coba 1 menguji teknik penanganan kelas minoritas, Uji Coba 2 membandingkan lima model pra-latih, Uji Coba 3 menguji penambahan fitur POS. Lalu analisis graf dan enam pengujian fungsional. **[klik]**

## Slide 12 — Anotasi Data & Ketidakseimbangan Kelas
Ini kunci untuk membaca semua hasil. Data uji yang dipakai konsisten: 254 chunk, hampir 50 ribu token, dengan 1.969 entitas. Yang penting, distribusinya **sangat timpang** — Person mendominasi, sementara **Event dan Time sangat minoritas**, rasionya sekitar 17 banding 1. Ketimpangan inilah yang jadi dasar Uji Coba 1. **[klik]**

## Slide 13 — Uji Coba 1: Hasil (Penanganan Imbalance)
Di sini saya bandingkan baseline dengan empat teknik penanganan minoritas, pada pipeline yang sama, diukur dengan F1 entity-level. Hasilnya, **augmentasi data adalah yang terbaik** dengan F1 mikro **0,9756**, unggul di hampir semua metrik. Lonjakan terbesarnya di kelas **Time**, dari 0,80 ke 0,90. Saya jujur di sini: F1 Event tertinggi sebenarnya di SCL dan JSCL, tapi keduanya tidak seimbang secara keseluruhan. Augmentasi yang saya pakai adalah kombinasi *mention replacement* dan parafrase. **[klik]**

## Slide 14 — Uji Coba 1: Pembahasan
Kenapa augmentasi menang? Karena ia **menambah ragam contoh** untuk kelas minoritas — jumlah entitas latih naik dari 4.247 ke 6.780, dengan Event tumbuh paling tajam. Sebaliknya, weighted cross-entropy dan JSCL justru di bawah baseline karena hanya menggeser bobot tanpa menambah informasi baru, sehingga model jadi over-deteksi. Dan temuan penting: kesalahan model **didominasi keputusan deteksi** — apakah suatu kata entitas atau bukan — bukan salah menentukan tipe. Salah-tipe hanya sekitar dua sampai enam persen. Jadi model sudah paham keempat tipe; tantangannya di deteksi. **[klik]**

## Slide 15 — Uji Coba 2: Hasil (Komparasi Model)
Uji Coba 2 membandingkan lima model backbone. Tiga model **uncased** stabil di kisaran F1 0,93 sampai 0,95, dengan **IndoBERT uncased terbaik**. Sementara IndoBERT **cased** dan **RoBERTa** anjlok ke 0,78 dan 0,81. Yang menarik, anjloknya **terpusat di kelas Person dan Time**, sedangkan Location tetap tinggi. **[klik]**

## Slide 16 — Uji Coba 2: Pembahasan
Saya perlu tekankan: hasil ini **tidak membuktikan model cased atau RoBERTa lebih buruk**. Polanya justru **mengindikasikan masalah penyelarasan label kata-ke-subword** pada pipeline. Tiga buktinya: pertama, defisitnya sudah ada sejak model dasar, jadi bukan efek self-training; kedua, terpusat di entitas banyak-kata seperti nama orang; dan ketiga, kesalahan batas B-I meledak sampai lebih dari seratus token, mayoritas pada Person. Ini ciri khas ketidakcocokan penyelarasan label pada tokenizer cased dan BPE, bukan kelemahan modelnya. **[klik]**

## Slide 17 — Uji Coba 3: Hasil (Modul POS-tag)
Uji Coba 3 menguji penambahan fitur POS-tag, memakai POS asli dari tagger, bukan placeholder. Hasilnya, POS-tag **belum menunjukkan perbaikan yang meyakinkan** — F1 mikro 0,9547 praktis setara baseline 0,9536, hanya selisih 0,0011. Dan per kelasnya tidak konsisten: Time naik, tapi Location dan Event justru turun. **[klik]**

## Slide 18 — Uji Coba 3: Pembahasan
Kenapa POS tidak membantu? Karena **redundan** — IndoBERT yang kontekstual sudah menyerap petunjuk kelas kata, jadi POS eksplisit tidak menambah sinyal baru. Yang terjadi hanya pergeseran: precision naik tapi recall turun, artinya model jadi lebih berhati-hati menebak tapi lebih banyak melewatkan entitas. Saya catat jujur, karena POS-nya asli, hasil ini sah — memang begitu perilakunya pada konfigurasi yang diuji. **[klik]**

## Slide 19 — Evaluasi KG: Konstruksi Knowledge Graph
Masuk ke knowledge graph. Graf dibangun dari prediksi NER konfigurasi terbaik tadi, lalu dimuat ke Neo4j. Hasilnya **1.192 simpul** — didominasi 901 tokoh — dan **728 relasi**. Satu catatan teknis: ekstraksi awal menghasilkan 705 catatan relasi, tapi 12 di antaranya duplikat dan digabung otomatis lewat MERGE menjadi 693 relasi unik, ditambah 35 relasi periode. Contoh nyatanya bisa dilihat pada subgraf Perang Badr, di mana simpul Event menjadi penghubung antara tokoh, lokasi, dan waktu. **[klik]**

## Slide 19b — Evaluasi KG: Tokoh Berpengaruh
Dari graf itu dibentuk proyeksi jaringan antar-tokoh — 137 tokoh yang benar-benar terlibat peristiwa — lalu diukur sentralitasnya dengan empat metrik yang masing-masing menangkap dimensi berbeda. Hasilnya, **keempat metrik konvergen pada Muhammad** — beliau paling terhubung, paling dekat ke seluruh jaringan, paling berpengaruh, sekaligus jembatan utama antar-kelompok. Ini menegaskan struktur naratif Sirah yang berpusat pada satu tokoh. Saya beri catatan jujur: peringkat betweenness selain Muhammad perlu dibaca hati-hati karena jaringannya padat. **[klik]**

## Slide 20 — Evaluasi KG: Komunitas & Validasi Artefak
Deteksi komunitas dengan Louvain menghasilkan delapan komunitas dengan modularitas 0,2831 — kelompoknya masih terlihat tapi batasnya melembut karena jaringan padat. Dua terbesar adalah lingkar Muslim inti dan komunitas campuran. **[jeda]** Dan ini bagian yang saya anggap penting untuk kejujuran penelitian: relasi keterlibatan dibentuk dari **kedekatan teks**, sehingga sebagian nama bisa melonjak semu. Contohnya Amr bin Umayyah — tanpa pembobotan sempat peringkat dua PageRank, padahal tiga dari empat relasinya false positive; peran aslinya kurir Nabi. Setelah pembobotan dan scoping, dia turun ke peringkat dua belas. Pelajarannya: peringkat sentralitas **wajib divalidasi balik ke teks**. **[klik]**

## Slide 21 — Evaluasi KG: Peristiwa, Lokasi & Studi Kasus
Analisis diperluas ke peristiwa dan lokasi. Peristiwa paling sentral didominasi peperangan — Badr, Uhud, Khandaq. Saya akui keterbatasan di sini: peristiwa daur hidup seperti kelahiran atau wafat tidak muncul karena disebut lewat frasa kata kerja, tidak tertangkap NER. Untuk lokasi, Madinah dan Makkah teratas — dua pusat fase Sirah. Catatan, "Yatsrib" masih terpisah dari "Madinah" karena keduanya sinonim semantik, bukan variasi ejaan. Pada studi kasus lima peristiwa besar, hanya Muhammad yang hadir di kelimanya, dan perbedaan ukuran subgraf lebih mencerminkan **bias cakupan ekstraksi**, bukan skala historis sebenarnya. **[klik]**

## Slide 22 — Evaluasi KG: Pengujian Fungsional
Terakhir, pengujian fungsional dengan enam kueri. Semua kueri **berhasil dieksekusi, mengembalikan hasil, dan terlacak ke sumber** — jadi secara struktur, graf mampu menjawab enam pola penelusuran relasional. Namun saya beri tanda jujur: pada kriteria **kesesuaian sumber, semuanya "tidak"** — bukan karena semua jawaban salah, tapi karena tiap fungsi punya minimal satu hasil yang tidak didukung teks. Contohnya, graf menyatakan Abu Lahab terlibat Perang Badr, padahal bukti teksnya justru menyatakan ia tidak ikut. Jadi kesimpulannya: graf **layak untuk penelusuran awal**, tapi belum bisa jadi sumber jawaban mandiri tanpa verifikasi ke teks. Akar masalahnya sama — over-ekstraksi relasi berbasis kedekatan. **[klik]**

## Slide 23 — Kesimpulan
Menyimpulkan keempat rumusan masalah. **Pertama**, data berhasil disiapkan lewat OCR, preprocessing, chunking, dan pelabelan. **Kedua**, ekstraksi entitas terbaik dicapai IndoBERT uncased dengan augmentasi, F1 mikro **0,9756**, dan kelas minoritas terangkat. **Ketiga**, knowledge graph berhasil dibangun di Neo4j lengkap dengan provenance. **Keempat**, keenam fungsi penelusuran berjalan dan terlacak, analisis SNA menunjukkan Muhammad dominan dan delapan komunitas — dengan catatan keterbatasan berupa over-ekstraksi relasi. **[klik]**

## Slide 24 — Saran
Empat arah pengembangan. Yang paling utama: **mengganti ekstraksi relasi berbasis kedekatan dengan berbasis kata kerja** dan penanganan negasi, agar artefak seperti Amr bin Umayyah berkurang. Lalu, deteksi peristiwa dari konstruksi verbal agar peristiwa daur hidup tertangkap; perbaikan penyelarasan label agar perbandingan model adil; serta penguatan alias dan perluasan cakupan. **[klik]**

## Slide 25 — Penutup
Sebagai penutup, knowledge graph terbukti membantu menemukan hubungan dalam Sirah, tetapi setiap jawaban tetap perlu diverifikasi ke teks sumbernya. Terima kasih atas setiap koreksi, pertanyaan, dan masukan sepanjang proses ini. Saya siap menerima pertanyaan dan masukan dari Bapak dan Ibu. Wassalamualaikum warahmatullahi wabarakatuh.

---

## Catatan penyampaian
- **Kalimat jujur** (Amr bin Umayyah, cased/RoBERTa artefak, fungsional 0/6, peristiwa daur hidup) **jangan dilewati** — dosen menghargai kesadaran keterbatasan, dan ini justru memperkuat, bukan melemahkan.
- Kalau ditanya di tengah, jawab singkat lalu **kembali ke alur** ("baik, saya lanjutkan…").
- Jika waktu menipis di menit ke-15: percepat Slide 2, 7, 8, dan gabungkan pembahasan (14, 16, 18) ke satu-dua kalimat; **jangan** korbankan Slide 13, 19b, 20, 22 (temuan inti).
- Latih transisi antar-bagian: setelah metode (Slide 11) → "sekarang saya masuk ke hasil pengujian"; setelah NER (Slide 18) → "dari model terbaik ini, saya bangun knowledge graph-nya".
- Untuk pertanyaan mendalam, rujuk `docs/pertanyaan/jawaban.md` + `kartu_contekan.md`.
