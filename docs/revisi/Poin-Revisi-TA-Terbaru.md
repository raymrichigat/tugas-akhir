# Poin Revisi Tugas Akhir Terbaru

## Identitas dan Ruang Lingkup

Dokumen ini menggabungkan catatan revisi dari Pak Aldi, Bu Nanik, Bu Ratih, dan Bu Dini dengan hasil penelaahan rekaman sidang serta pemeriksaan buku Tugas Akhir berjudul pembangunan *knowledge graph* Sirah Nabawiyah. Poin-poin berikut disajikan sebagai uraian revisi, bukan sebagai daftar centang.

Status yang digunakan dalam dokumen ini adalah sebagai berikut:

- **Belum terpenuhi** berarti substansi atau komponen yang diminta belum ditemukan secara memadai di dalam buku.
- **Sebagian terpenuhi** berarti komponen sudah tersedia, tetapi masih memerlukan perbaikan, penambahan contoh, penjelasan, atau penyesuaian format.
- **Sudah dibahas, perlu dipoles** berarti substansi utama sudah tersedia dan revisi lebih diarahkan pada konsistensi, penempatan, keterbacaan, atau ketepatan klaim.

## Ringkasan Revisi Utama

Revisi paling penting berkaitan dengan kejelasan alur dari data teks hingga terbentuknya *knowledge graph*, ketepatan istilah normalisasi alias, dasar penentuan *hyperparameter* dan relasi, contoh data pada setiap tahap, serta pengukuran kualitas *knowledge graph* yang tidak hanya menyatakan bahwa kueri berhasil dijalankan. Selain itu, masih terdapat sejumlah persoalan format dan kesalahan konkret, seperti awal bab pada halaman genap, placeholder nomor lampiran, judul tabel yang berulang, serta rujukan persamaan yang belum konsisten.

---

## Revisi dari Pak Aldi

### 1. Tata Letak Buku Tugas Akhir

Setiap bab perlu dimulai pada halaman ganjil. Berdasarkan daftar isi dan penomoran halaman saat ini, Bab 4 dimulai pada halaman 70 dan Bab 5 dimulai pada halaman 120. Penempatan tersebut perlu diperiksa kembali terhadap ketentuan bahwa halaman pembuka bab berada pada halaman ganjil. Halaman kosong juga perlu diperiksa agar tidak ditempatkan pada sisi yang justru menyebabkan pembuka bab berada pada halaman genap.

Untuk tabel yang berlanjut ke halaman berikutnya, kepala tabel harus diulang. Pemeriksaan khusus perlu dilakukan pada Tabel 2.1 serta tabel-tabel panjang lainnya. Jika tabel hanya memiliki sedikit baris, judul dan isi tabel sebaiknya dipertahankan pada halaman yang sama serta tidak dipisahkan secara tidak perlu.

**Status:** sebagian terpenuhi; memerlukan pemeriksaan tata letak menyeluruh setelah seluruh revisi isi selesai.

### 2. Format Penulisan Persamaan pada Bab 2

Kalimat umum seperti “persamaan dapat dilihat di bawah ini” perlu dihindari. Setiap persamaan harus dirujuk menggunakan nomor yang spesifik, misalnya “Perhitungan *degree centrality* ditunjukkan pada Persamaan (2.12).” Setelah persamaan ditampilkan, penjelasan juga sebaiknya menyebut nomor tersebut, bukan hanya menggunakan kalimat “Pada persamaan tersebut.”

Seluruh nomor persamaan perlu dipastikan benar-benar dirujuk dalam paragraf. Pada bagian *knowledge graph* dan SNA, Persamaan (2.11) sampai dengan Persamaan (2.19) masih perlu diaudit karena beberapa penjelasannya menggunakan rujukan umum. Terdapat pula kesalahan penjelasan *betweenness centrality*: frasa “jalur dari simpul t ke simpul t” harus diperbaiki menjadi “jalur dari simpul s ke simpul t.”

**Status:** sebagian terpenuhi; penomoran sudah tersedia, tetapi penggunaannya dalam narasi belum konsisten.

### 3. Confusion Matrix

Bab 2 perlu memuat penjelasan konseptual mengenai *confusion matrix* yang sesuai dengan bentuk klasifikasi pada penelitian. Jumlah kelas harus dijelaskan secara eksplisit, yaitu apakah matriks menggunakan sembilan label BIO—`O`, `B-PERSON`, `I-PERSON`, `B-LOCATION`, `I-LOCATION`, `B-TIME`, `I-TIME`, `B-EVENT`, dan `I-EVENT`—atau menggunakan lima kelas setelah label B dan I digabung berdasarkan tipe entitas.

Bab 4 sudah memuat beberapa *confusion matrix* pada halaman 77, 83, 86, dan 91. Namun, ukuran angka dan label perlu diperbesar agar dapat dibaca pada versi cetak. *Confusion matrix* utama dapat dipertahankan dalam Bab 4, sedangkan hasil lengkap setiap model atau skenario dapat dipindahkan ke lampiran apabila membuat pembahasan terlalu panjang.

**Status:** sebagian terpenuhi; matriks hasil sudah tersedia, tetapi teori, konsistensi kelas, dan keterbacaannya masih perlu diperbaiki.

### 4. Caption Tabel

Judul atau *caption* tabel harus berada pada halaman yang sama dengan tabelnya. Pemeriksaan khusus perlu dilakukan pada tabel sekitar halaman 40 serta seluruh tabel yang berpindah halaman setelah perubahan tata letak. Hindari kondisi ketika *caption* berada pada bagian bawah suatu halaman, sedangkan isi tabel baru dimulai pada halaman berikutnya.

**Status:** memerlukan pemeriksaan format akhir.

### 5. Dasar Penentuan Hyperparameter

Tabel 3.11 pada sekitar halaman 51–52 telah mencantumkan *learning rate* `2e-5`, *batch size* `16`, 10 *epoch* per iterasi, ambang *confidence* `0,9`, dan maksimal enam iterasi. Namun, penjelasan bahwa nilai tersebut mengikuti *notebook* acuan pembimbing dan Ariyanto et al. belum cukup sebagai justifikasi ilmiah.

Setiap parameter utama perlu diberi alasan. Penjelasan dapat memuat kesesuaian dengan penelitian terdahulu, karakteristik dan ukuran dataset, keterbatasan memori komputasi, kestabilan pelatihan, serta hasil uji pendahuluan apabila pernah dilakukan. Perlu dijelaskan pula apakah konfigurasi Ariyanto et al. terbukti sebagai konfigurasi terbaik atau hanya dijadikan nilai awal yang kemudian diadaptasi.

**Status:** belum terpenuhi secara memadai.

### 6. Penanganan Imbalance Class

Buku telah menampilkan perubahan distribusi label sebelum dan sesudah augmentasi pada halaman 78–79. Akan tetapi, perlu ditambahkan contoh konkret augmentasi, misalnya satu kalimat sebelum dan sesudah *mention replacement* atau parafrase, disertai label BIO agar konsistensi label dapat diperiksa.

Data saat ini menunjukkan bahwa token `O` bertambah dari 108.815 menjadi 163.352, sedangkan token Event bertambah dari 317 menjadi 943. Rasio Person terhadap Event berkurang dari sekitar 17,4:1 menjadi 8,8:1. Hasil tersebut menunjukkan bahwa augmentasi **mengurangi ketimpangan**, tetapi tidak membuktikan bahwa dataset menjadi sepenuhnya seimbang. Oleh karena itu, istilah “menyeimbangkan data” sebaiknya diganti menjadi “mengurangi ketimpangan kelas” atau “menambah variasi contoh kelas minoritas.”

Tidak ada satu ambang universal yang otomatis menyatakan dataset NER seimbang. Penilaian perlu didasarkan pada proporsi kelas, rasio antarkelas, performa per kelas, serta pengaruhnya terhadap *precision*, *recall*, dan F1-score. Jika kelas mayoritas hendak ditekan, pengurangan sebaiknya dilakukan pada tingkat pemilihan kalimat atau chunk, bukan dengan menghapus token `O` secara individual karena token tersebut membentuk konteks dan urutan BIO.

**Status:** sebagian terpenuhi; hasil distribusi sudah tersedia, tetapi contoh augmentasi dan ketepatan klaim masih perlu diperbaiki.

### 7. Legenda Visualisasi Data

Visualisasi pada sekitar halaman 73 dan 81 perlu menggunakan warna yang konsisten untuk model atau skenario yang sama. Warna tidak perlu berubah hanya untuk menandai nilai terbaik. Hasil terbaik dapat ditunjukkan menggunakan huruf tebal, pola garis, penanda, atau anotasi tanpa mengubah pemetaan warna pada legenda.

**Status:** perlu dipoles pada tahap finalisasi gambar.

### 8. Keterangan Token Tanda Titik

Token tanda titik (`.`) sebaiknya dihapus dari contoh apabila tidak memiliki fungsi analitis. Jika tetap dipertahankan karena merupakan keluaran tokenizer atau pembatas kalimat, fungsinya perlu dijelaskan. Aturan ini harus konsisten antara contoh prapemrosesan, data latih, dan masukan model.

**Status:** belum dijelaskan secara eksplisit.

### 9. Perbandingan Model Pre-trained

Pengertian model *cased* dan *uncased* sebaiknya diperkenalkan pada Bab 2 atau Bab 3 sebelum hasil perbandingan dibahas. Penjelasan dapat menyebutkan bahwa model *cased* mempertahankan informasi huruf kapital, sedangkan model *uncased* menormalisasi kapitalisasi sesuai mekanisme tokenizer/modelnya.

Pembahasan pada halaman 84–86 mengenai IndoBERT cased, IndoBERT uncased, RoBERTa, tokenisasi subword, dan penyelarasan label sudah baik. Pembahasan tersebut tidak perlu ditulis ulang, tetapi landasan konsepnya perlu dipindahkan atau diringkas pada bab teori/metodologi.

**Status:** sudah dibahas, perlu dipindahkan atau diperkenalkan lebih awal.

### 10. Lampiran

Lampiran tidak boleh kosong. Lampiran dapat diisi dengan *confusion matrix* lengkap, contoh data train, hasil prediksi NER, contoh kesalahan, kueri Cypher, tabel validasi jawaban, serta visualisasi subgraf per peristiwa.

Pada halaman 110 masih terdapat teks “Lampiran [sesuaikan nomor lampiran].” Placeholder tersebut harus diganti dengan nomor lampiran yang benar dan lampiran yang dirujuk harus benar-benar tersedia. Jika materi lampiran tidak jadi dimasukkan, kalimat rujukannya harus dihapus.

**Status:** belum terpenuhi dan menjadi revisi format prioritas tinggi.

---

## Revisi dari Bu Nanik

### 1. Contoh Proses NER dalam Konteks Sirah Nabawiyah

Buku perlu menampilkan satu contoh deteksi entitas menggunakan kalimat asli dari korpus Sirah Nabawiyah. Contoh tersebut sebaiknya memperlihatkan teks masukan, hasil tokenisasi, label BIO, hasil prediksi, serta entitas akhir yang dibentuk kembali dari token.

Tabel 3.9 dan Tabel 3.12 telah memberikan contoh BIO dan hasil NER, tetapi contohnya masih terpisah. Keduanya sebaiknya dihubungkan menjadi satu contoh berjalan agar pembaca dapat mengikuti perubahan data dari awal sampai akhir.

**Status:** sebagian terpenuhi.

### 2. Tampilan Data Train

Format data train perlu ditampilkan secara lengkap. Contoh minimal memuat teks asli, `text_id` atau identitas chunk, urutan token, label BIO, metadata halaman/subbab, dan POS-tag apabila kolom tersebut memang digunakan. Jika POS-tag hanya berupa nilai `NN` sebagai placeholder dan tidak digunakan model, hal tersebut harus dinyatakan dengan jelas agar tidak menimbulkan kesan bahwa fitur POS benar-benar menjadi masukan pada seluruh eksperimen.

**Status:** sebagian terpenuhi; struktur kolom sudah dijelaskan, tetapi contoh lengkap dan konteks asal data masih perlu ditambahkan.

### 3. Pendefinisian Token dan Cara Pemakaian pada Model

Istilah token, kata, dan subtoken perlu dibedakan. Chunk merupakan unit teks yang diberikan ke tokenizer/model, token atau subtoken merupakan unit representasi yang diproses model, sedangkan prediksi akhir diberikan pada setiap token dan kemudian digabungkan kembali menjadi entitas.

Metodologi perlu memastikan apakah pelatihan dilakukan per chunk, per kalimat, atau melalui batch yang berisi sejumlah chunk. Jelaskan pula batas maksimal token, mekanisme pemotongan, *padding*, dan penyelarasan label ketika satu kata dipecah menjadi beberapa subtoken. Jika implementasi menggunakan `word_ids()`, mekanismenya perlu disebutkan pada Bab 3 dan tidak hanya dibahas sebagai analisis hasil pada Bab 4.

**Status:** sebagian terpenuhi; pembahasan teknis sudah muncul pada Bab 4, tetapi belum cukup eksplisit pada metodologi.

### 4. Alur dari NER Menuju Knowledge Graph

Alur konstruksi perlu dijelaskan secara runtut melalui satu contoh yang sama: teks Sirah → chunk → token dan label BIO → entitas hasil NER → normalisasi nama → pemilihan pasangan entitas → penentuan jenis relasi → pembentukan node dan edge → penyimpanan ke Neo4j.

Gambar 3.7 sampai dengan Gambar 3.9 sudah memberikan diagram tahapan, tetapi perlu dilengkapi contoh data konkret agar hubungan antarbagian tidak hanya terlihat secara konseptual.

**Status:** sebagian terpenuhi.

### 5. Penggunaan Istilah Clustering

Istilah “alias clustering” perlu diganti karena proses yang dilakukan menghasilkan `alias_map` berupa pemetaan variasi nama ke nama kanonik, bukan proses clustering yang dievaluasi menggunakan kualitas klaster. Istilah yang lebih tepat adalah “Normalisasi Alias”, “Penyatuan Variasi Nama”, atau “Penyatuan Alias Berbasis Jaro–Winkler dan Validasi Manual.”

Penggantian istilah harus dilakukan secara konsisten pada abstrak Indonesia dan Inggris, daftar isi, Subbab 3.7.1, Gambar 3.8, Kode Semu 3.8, pembahasan hasil, dan kesimpulan. Jaro–Winkler perlu disebut sebagai ukuran kemiripan string, bukan sebagai algoritma clustering.

**Status:** belum terpenuhi dan menjadi revisi terminologi prioritas tinggi.

### 6. Metode Penentuan Relasi

Penentuan relasi berdasarkan *co-occurrence*, satu kalimat, atau jarak kurang dari 200 karakter perlu didukung penelitian terdahulu atau dijelaskan sebagai heuristik yang diadaptasi untuk korpus penelitian. Angka 200 karakter harus memiliki dasar, misalnya hasil uji pendahuluan atau analisis karakteristik kalimat/chunk.

Tahap pembentukan relasi perlu dilengkapi contoh positif dan negatif. Contoh positif menunjukkan pasangan entitas yang memang membentuk relasi, sedangkan contoh negatif menunjukkan entitas yang berdekatan tetapi tidak memiliki hubungan semantis karena negasi, subjek berbeda, atau konteks kalimat berbeda. Aturan `InvalidInvolvedIn`, `InvalidOccurredAt`, dan `InvalidOccurredOn` dalam kode semu juga perlu dijelaskan secara operasional.

**Status:** sebagian terpenuhi; algoritma dan kode semu sudah tersedia, tetapi dasar teori, ambang, dan contoh validasinya belum cukup.

### 7. Dasar Teknik Konstruksi Knowledge Graph

Perlu dijelaskan penelitian yang diadopsi untuk membentuk node, edge, jenis relasi, normalisasi entitas, serta penyimpanan menggunakan *labeled property graph* Neo4j. Jika konstruksi merupakan gabungan beberapa pendekatan, buku harus menjelaskan bagian yang diadopsi dan bagian yang merupakan rancangan penelitian sendiri.

Klaim juga perlu dibatasi: relasi yang terbentuk melalui kedekatan entitas merupakan relasi hasil induksi heuristik, bukan hasil *semantic relation extraction* penuh.

**Status:** belum terpenuhi secara memadai.

### 8. Pengukuran Kualitas Knowledge Graph

Evaluasi perlu membedakan tiga aspek. Pertama, evaluasi NER menilai kualitas ekstraksi entitas. Kedua, SNA mendeskripsikan struktur graf dan tidak secara otomatis membuktikan kebenaran semantis. Ketiga, pengujian fungsional menilai apakah graf dapat menjawab kebutuhan penelusuran yang dirumuskan melalui *competency questions*.

Selain keberhasilan menjalankan kueri, jawaban perlu divalidasi terhadap teks sumber. Untuk setiap fungsi, laporkan jumlah jawaban yang valid, tidak valid, dan persentase validitas semantis. Rumus yang dapat digunakan adalah:

\[
\text{Validitas semantis} = \frac{\text{jumlah jawaban yang didukung sumber}}{\text{seluruh jawaban yang diperiksa}} \times 100\%
\]

Hasil yang sudah dapat dihitung dari tabel saat ini antara lain F3 sebesar 3 dari 4 jawaban atau 75%, F5 sebesar 3 dari 21 jalur atau 14,29%, dan F6 sebesar 14 dari 17 jawaban atau 82,35%. F1, F2, dan F4 perlu dihitung berdasarkan seluruh jawaban yang dikembalikan kueri.

Kesimpulan evaluasi harus membedakan kelayakan operasional dan validitas semantis. Graf dapat dinyatakan layak secara operasional apabila semua kueri dapat dijalankan, tetapi belum dapat dinyatakan benar secara semantis apabila masih terdapat jawaban yang tidak didukung teks sumber.

**Status:** sebagian terpenuhi; pengujian dan pembahasan keterbatasan sudah tersedia, tetapi hasil kuantitatif validitas semantis belum lengkap.

---

## Revisi dari Bu Ratih

### 1. Perbaikan Abstrak

Abstrak perlu menggunakan istilah yang konsisten dan tidak memberikan klaim berlebihan. Istilah “alias clustering” harus diganti. Bagian evaluasi juga perlu membedakan evaluasi NER, analisis struktur dengan SNA, dan pengujian fungsional *knowledge graph*.

Abstrak sebaiknya menyatakan bahwa enam kueri berhasil dijalankan secara operasional, tetapi validasi manual masih menemukan relasi yang tidak didukung konteks sumber. Dengan demikian, abstrak tidak hanya menampilkan keberhasilan sistem, tetapi juga batas validitas hasilnya.

**Status:** sebagian terpenuhi; substansi hasil sudah tersedia, tetapi terminologi dan ketepatan klaim perlu diperbaiki.

### 2. Tata Letak dan Format Penulisan

Revisi ini sejalan dengan catatan Pak Aldi dan Bu Dini. Awal bab harus ditempatkan pada halaman ganjil, kepala tabel perlu diulang ketika tabel melampaui satu halaman, dan tabel dengan sedikit isi tidak boleh dipisahkan secara tidak perlu.

**Status:** memerlukan pemeriksaan format akhir.

### 3. Notasi Persamaan

Setiap variabel, indeks, himpunan, fungsi, dan parameter pada persamaan harus dijelaskan. Penjelasan perlu konsisten dengan simbol yang ditampilkan. Audit khusus diperlukan pada persamaan SNA, fungsi kerugian, Jaccard, serta persamaan augmentasi agar tidak terdapat simbol yang muncul tanpa definisi.

**Status:** sebagian terpenuhi; sebagian besar variabel telah dijelaskan, tetapi masih perlu audit konsistensi.

### 4. Contoh Penerapan Chunking

Tambahkan contoh teks sebelum dan sesudah chunking. Jelaskan alasan panjang chunk, penggunaan overlap jika ada, penanganan kalimat yang terpotong, jumlah token maksimal, serta bagaimana metadata halaman atau subbab dipertahankan. Contoh ini perlu menggunakan teks Sirah yang benar-benar masuk ke pipeline.

**Status:** belum terpenuhi secara konkret.

### 5. Koreksi Manual

Alasan pengoreksian manual perlu dijelaskan. Koreksi diperlukan karena pelabelan berbasis kamus, regex, OCR, atau pseudo-label dapat menghasilkan kesalahan batas entitas, kesalahan tipe, entitas yang terlewat, dan entitas palsu.

Tambahkan contoh sebelum dan sesudah koreksi manual serta pedoman yang digunakan. Buku juga perlu menjelaskan siapa yang melakukan koreksi dan bagaimana konsistensinya dijaga. Jika tidak terdapat anotator kedua atau pengukuran kesepakatan anotator, hal tersebut harus dinyatakan sebagai keterbatasan.

**Status:** belum terpenuhi secara memadai.

### 6. Contoh Label BIO

Tabel 3.9 dapat dipertahankan, tetapi sebaiknya diperluas menggunakan satu kalimat lengkap. Setiap token ditampilkan bersama label BIO dan alasan batas entitasnya. Contoh tersebut idealnya menjadi bagian dari contoh berjalan yang sama dengan proses NER dan konstruksi graf.

**Status:** sebagian terpenuhi.

### 7. Alias Clustering dan Jaro–Winkler

Istilah harus diganti karena Jaro–Winkler merupakan ukuran kemiripan string. Jika istilah clustering tetap digunakan, penelitian harus menjelaskan algoritma pembentukan klaster, pemilihan konfigurasi terbaik, dan evaluasi kualitas klaster. Karena implementasi saat ini lebih berupa peta alias, pilihan yang lebih aman adalah menggantinya dengan istilah “normalisasi alias.”

Ambang 0,93 juga perlu didukung alasan empiris atau uji beberapa nilai ambang. Contoh pasangan benar dan salah dapat ditambahkan untuk menunjukkan fungsi aturan pengaman dan `exclude pairs`.

**Status:** belum terpenuhi.

### 8. Keterbacaan Confusion Matrix

Angka, label sumbu, dan legenda pada *confusion matrix* perlu diperbesar. Jika matriks sembilan kelas terlalu padat, tampilkan versi resolusi tinggi atau orientasi lanskap di lampiran dan gunakan matriks agregat yang lebih ringkas dalam Bab 4.

**Status:** perlu dipoles.

---

## Revisi dari Bu Dini

### 1. Tata Letak dan Format Penulisan

Revisi mencakup awal bab pada halaman ganjil, kepala tabel berulang, dan pencegahan pemisahan tabel dengan isi sedikit. Penyesuaian tata letak sebaiknya dilakukan setelah revisi substansi selesai karena penambahan paragraf, tabel, dan gambar akan mengubah pagination.

**Status:** memerlukan pemeriksaan format akhir.

### 2. Perbaikan Augmentasi

Augmentasi perlu lebih diarahkan pada kelas minoritas, terutama Event dan Time. Metode saat ini meningkatkan kedua kelas tersebut, tetapi token kelas mayoritas juga meningkat karena augmentasi menambahkan kalimat secara utuh.

Apabila implementasi tidak diubah, klaim harus dibatasi menjadi “augmentasi mengurangi ketimpangan kelas dan meningkatkan F1 kelas minoritas.” Apabila dosen meminta penekanan kelas mayoritas secara metodologis, penyesuaian dapat dilakukan melalui pemilihan atau *sampling* chunk yang terlalu dominan kelas mayoritas. Token `O` tidak sebaiknya dihapus secara individual karena dapat merusak konteks dan urutan label.

**Status:** sebagian terpenuhi; memerlukan penyesuaian klaim atau metode.

### 3. Output Graf

Visualisasi graf dalam buku perlu diperbesar agar nama node, jenis relasi, arah panah, warna kategori, dan legenda terbaca pada versi cetak. Visualisasi gabungan dapat dibatasi pada node penting, sedangkan subgraf lengkap ditempatkan di lampiran.

**Status:** perlu dipoles.

### 4. Daftar Pustaka

Font daftar pustaka perlu disesuaikan dengan pedoman penulisan institusi dan dibuat konsisten dengan bagian lain. Periksa pula ukuran font, spasi, indentasi menggantung, kapitalisasi judul, serta konsistensi format DOI atau URL.

**Status:** memerlukan pemeriksaan format.

### 5. Output Data Train

Tambahkan tabel contoh format data training yang memperlihatkan teks asli, `text_id`, nomor token, token, label BIO, metadata halaman/subbab, serta POS-tag jika digunakan. Contoh harus konsisten dengan berkas yang benar-benar digunakan untuk pelatihan.

**Status:** sebagian terpenuhi.

### 6. Output NER: Ground Truth dan Prediksi

Tambahkan tabel perbandingan *ground truth* dan prediksi model. Tabel perlu menandai prediksi benar, *false positive*, *false negative*, kesalahan tipe, dan kesalahan batas entitas. Contoh sebaiknya berasal dari data uji, bukan dari data latih.

Contoh format yang dapat digunakan:

| Token/Entitas | Ground truth | Prediksi | Kategori hasil |
|---|---|---|---|
| Rasulullah | PERSON | PERSON | Benar |
| Madinah | LOCATION | EVENT | Salah tipe |
| bulan Ramadhan | TIME | Tidak terdeteksi | False negative |

**Status:** sebagian terpenuhi; contoh kesalahan sudah dibahas pada Bab 4, tetapi belum disajikan sebagai perbandingan langsung yang utuh.

### 7. Alur NER Menuju Knowledge Graph

Penjelasan perlu dibuat runtut dengan satu contoh data yang sama sampai menjadi node dan edge. Revisi ini sama dengan catatan Bu Nanik dan sebaiknya diselesaikan melalui satu tabel atau gambar proses menyeluruh, bukan melalui penambahan penjelasan yang terpisah-pisah.

**Status:** sebagian terpenuhi.

### 8. Analisis Error

Analisis error perlu menghubungkan jenis kesalahan dengan penyebab dan dampaknya. Pada NER, bahas *false positive*, *false negative*, kesalahan tipe entitas, kesalahan batas BIO, tokenisasi subword, dan ketimpangan kelas. Pada *knowledge graph*, bahas negasi, kedekatan penyebutan yang tidak berarti relasi, cakupan lokasi/waktu yang keliru, alias yang salah, dan penggunaan urutan dokumen sebagai urutan kronologis.

Setiap kategori sebaiknya disertai contoh teks sumber, keluaran sistem, keluaran yang seharusnya, penyebab, dan usulan perbaikan. Pembahasan halaman 84–86 serta 111–117 sudah menjadi dasar yang baik dan perlu diringkas menjadi taksonomi error yang lebih sistematis.

**Status:** sudah dibahas, perlu disusun lebih sistematis.

---

## Temuan Tambahan dari Pemeriksaan Buku

### 1. Perbaikan Tujuan Penelitian

Pada halaman 3, frasa “menilai kelayakan struktur graf” berpotensi memberikan klaim yang terlalu luas. SNA mendeskripsikan struktur jaringan, sedangkan pengujian fungsional menilai kegunaan graf untuk kebutuhan tertentu. Rumusan yang lebih tepat adalah:

> Mendeskripsikan struktur jaringan serta menilai kelayakan fungsional knowledge graph Sirah Nabawiyah untuk penelusuran relasional.

### 2. Kesalahan Caption Tabel 4.28

Tabel 4.28 dan Tabel 4.29 menggunakan judul yang sama. Tabel 4.28 sebaiknya diberi judul:

> Ringkasan Hasil Pengujian Fungsional Knowledge Graph

Tabel 4.29 dapat tetap digunakan untuk menampilkan contoh ketidaksesuaian hasil dengan teks sumber.

### 3. Protokol Validasi Manual Knowledge Graph

Metodologi perlu menjelaskan unit yang diperiksa, kriteria jawaban valid, cara menangani jawaban sebagian benar, serta siapa yang melakukan validasi. Untuk F5, unit evaluasi harus berupa 21 jalur yang dikembalikan kueri, bukan hanya 15 lokasi unik. Hal ini penting agar penyebut dalam perhitungan validitas sesuai dengan keluaran aktual.

### 4. Batas Klaim SNA

Nilai *degree centrality*, *betweenness centrality*, PageRank, density, dan modularity menggambarkan struktur graf hasil ekstraksi. Nilai tersebut tidak secara otomatis menunjukkan pengaruh historis tokoh atau membuktikan bahwa seluruh relasi benar. Kesimpulan harus mempertahankan batas interpretasi ini.

### 5. Konsistensi Istilah

Istilah berikut perlu digunakan secara konsisten di seluruh buku:

- “normalisasi alias” sebagai pengganti “alias clustering”;
- “mengurangi ketimpangan kelas” sebagai pengganti “menyeimbangkan kelas”, kecuali terdapat bukti bahwa data benar-benar seimbang;
- “analisis struktur graf” untuk SNA;
- “evaluasi fungsional” atau “kelayakan operasional” untuk pengujian kueri;
- “validitas semantis jawaban” untuk pemeriksaan hasil terhadap teks sumber;
- “induksi relasi berbasis heuristik” untuk relasi yang dibentuk dari *co-occurrence* dan proximity.

### 6. Perbaikan Redaksional pada Bab 5

Kalimat pembuka Bab 5 saat ini mengandung pengulangan kata “dan”. Kalimat tersebut dapat diperbaiki menjadi:

> Berdasarkan hasil pengujian dan pembahasan yang telah dilakukan, diperoleh kesimpulan sebagai berikut.

Kesimpulan evaluasi fungsional juga sebaiknya dilengkapi angka validitas semantis per fungsi agar tidak hanya bersifat deskriptif.

---

## Urutan Prioritas Pengerjaan

### Prioritas 1 — Kesalahan yang Harus Diselesaikan Sebelum Finalisasi

Bagian ini mencakup penggantian placeholder lampiran halaman 110, perbaikan judul Tabel 4.28, penggantian istilah “alias clustering”, penyesuaian tujuan penelitian, perbaikan rujukan dan notasi persamaan, serta koreksi kesalahan redaksional pada Bab 5.

### Prioritas 2 — Penguatan Metodologi

Bagian ini mencakup alasan *hyperparameter*, definisi token/subtoken, contoh chunking, protokol koreksi manual, dasar ambang 200 karakter, rujukan metode konstruksi graf, aturan validasi relasi, dan contoh proses dari teks hingga Neo4j.

### Prioritas 3 — Penguatan Hasil dan Evaluasi

Bagian ini mencakup perbandingan *ground truth* dengan prediksi, contoh augmentasi, analisis error sistematis, perhitungan validitas semantis setiap fungsi, serta pembedaan antara keberhasilan operasional, kebenaran semantis, dan analisis struktur graf.

### Prioritas 4 — Tata Letak dan Keterbacaan

Bagian ini mencakup awal bab pada halaman ganjil, halaman kosong, *repeated header*, posisi caption tabel, pembesaran *confusion matrix* dan output graf, konsistensi legenda, format daftar pustaka, serta penataan lampiran.

## Kesimpulan Umum

Sebagian besar catatan dosen telah mulai diakomodasi dalam buku, terutama keberadaan *confusion matrix*, pembahasan ketimpangan kelas, penjelasan model cased/uncased, diagram konstruksi graf, pengujian enam fungsi, dan pembahasan keterbatasan relasi. Akan tetapi, komponen tersebut masih tersebar dan beberapa klaim belum didukung ukuran yang cukup jelas. Revisi akhir sebaiknya tidak hanya menambah materi baru, tetapi juga menyatukan contoh yang sudah ada menjadi satu alur yang dapat diikuti pembaca, memperbaiki istilah, serta membuat evaluasi *knowledge graph* lebih terukur dan dapat direproduksi.
