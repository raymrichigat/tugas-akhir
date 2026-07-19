# Poin Revisi Dosen Sidang Tugas Akhir

Dokumen ini disusun berdasarkan rekaman sidang pada file `Sidang.mp3`. Pembagian dosen mengikuti pergantian sesi pertanyaan dalam rekaman: sesi dosen pertama berlangsung kurang lebih pada menit 15:58–43:04, sedangkan sesi dosen kedua dimulai kurang lebih pada menit 43:07 hingga akhir rekaman.

## A. Revisi dari Dosen Pertama

### 1. Memperjelas bentuk dan hubungan dalam knowledge graph

- [ ] Tampilkan satu contoh relasi yang lengkap, bukan hanya kumpulan node yang mengelilingi sebuah event.
- [ ] Gunakan contoh konkret, misalnya: **Perang Badar → tokoh yang terlibat → waktu keterlibatan → lokasi**.
- [ ] Jelaskan hubungan PERSON–EVENT, EVENT–LOCATION, EVENT–TIME, dan PERSON–PERSON.
- [ ] Jelaskan apakah relasi memiliki bobot serta bagaimana bobot tersebut dihitung.
- [ ] Jelaskan cara mengetahui seorang tokoh terlibat pada waktu yang mana apabila satu event mempunyai beberapa entitas TIME.
- [ ] Jika graf belum dapat menjawab hubungan tokoh dengan waktu yang spesifik, nyatakan secara tegas sebagai keterbatasan penelitian.

### 2. Memperbaiki tata letak Buku TA

- [ ] Pastikan setiap judul bab dimulai pada halaman ganjil.
- [ ] Periksa kembali keberadaan halaman kosong, halaman genap, dan posisi judul bab.
- [ ] Ulangi header tabel ketika tabel berlanjut ke halaman berikutnya.
- [ ] Periksa tabel yang terpotong atau berpindah halaman tanpa header.

### 3. Memperbaiki rujukan persamaan

- [ ] Hindari kalimat umum seperti “persamaan dapat dilihat di bawah ini”.
- [ ] Rujuk nomor persamaan secara langsung, misalnya: “Perhitungan precision dapat dilihat pada Persamaan (2.1).”
- [ ] Pastikan semua nomor persamaan yang sudah dibuat benar-benar digunakan dalam paragraf penjelas.

### 4. Menambahkan confusion matrix

- [ ] Tambahkan confusion matrix yang sesuai dengan empat tipe entitas: PERSON, EVENT, LOCATION, dan TIME.
- [ ] Tampilkan confusion matrix utama pada Bab 4 dan pindahkan hasil lengkap setiap skenario ke lampiran jika jumlahnya terlalu banyak.
- [ ] Tegaskan level confusion matrix yang digunakan.
  - Entity-level dapat menggunakan empat tipe entitas.
  - Token-level BIO mencakup label `B-` dan `I-` untuk setiap entitas serta label `O`, sehingga bukan sekadar empat kelas.

### 5. Memperkuat dasar pemilihan hyperparameter

- [ ] Jangan hanya menyatakan bahwa hyperparameter mengikuti notebook atau penelitian sebelumnya.
- [ ] Jelaskan dasar pemilihan learning rate, batch size, epoch, threshold, maximum iteration, dan hyperparameter lainnya.
- [ ] Jelaskan bahwa hyperparameter penelitian terdahulu diadaptasi dan diuji kembali pada dataset Sirah Nabawiyah.
- [ ] Tambahkan referensi ilmiah yang mendukung pemilihan hyperparameter tersebut untuk kasus sejenis.
- [ ] Jika memungkinkan, konfirmasikan dasar pemilihannya kepada peneliti yang dijadikan acuan.

### 6. Memperjelas metode penanganan ketidakseimbangan kelas

- [ ] Jelaskan bahwa weighted cross-entropy mengubah bobot loss, bukan jumlah data.
- [ ] Jelaskan bahwa supervised contrastive learning memengaruhi representasi dan fungsi pembelajaran, bukan jumlah data.
- [ ] Jelaskan bahwa data augmentation benar-benar menghasilkan data tambahan.
- [ ] Tampilkan contoh teks sebelum dan sesudah paraphrasing.
- [ ] Tampilkan contoh penerapan mention replacement.
- [ ] Tampilkan distribusi setiap kelas sebelum dan sesudah augmentasi.
- [ ] Jelaskan kelas yang menjadi target utama augmentasi.

### 7. Memperbaiki klaim keberhasilan data augmentation

Dosen mempertanyakan apakah perubahan rasio ketimpangan sekitar **18:1 menjadi 9:1** sudah dapat disebut seimbang.

- [ ] Jangan langsung menyimpulkan bahwa data augmentation berhasil menyeimbangkan seluruh kelas.
- [ ] Gunakan kesimpulan yang lebih hati-hati, misalnya:

> Data augmentation berhasil mengurangi tingkat ketimpangan distribusi kelas, meskipun distribusi antarkelas belum sepenuhnya seimbang.

- [ ] Tambahkan referensi atau ukuran yang mendukung penilaian tingkat ketidakseimbangan kelas.
- [ ] Jelaskan mengapa jumlah PERSON sebagai kelas mayoritas ikut bertambah setelah augmentasi.
- [ ] Bedakan antara peningkatan jumlah data, pengurangan rasio ketimpangan, dan kondisi kelas yang benar-benar seimbang.

### 8. Memperbaiki grafik hasil pengujian

- [ ] Samakan warna garis atau batang dengan warna pada legenda.
- [ ] Jika augmentation ditampilkan dengan warna tertentu, legenda augmentation harus menggunakan warna yang sama.
- [ ] Periksa kembali grafik lain yang mempunyai ketidaksesuaian warna serupa.

### 9. Mengevaluasi kembali penggunaan tanda baca

- [ ] Jelaskan alasan tanda baca dipertahankan dalam proses tokenisasi.
- [ ] Pertimbangkan apakah semua tanda baca perlu dimasukkan sebagai token.
- [ ] Bedakan tanda baca yang menjadi bagian penting dari nama dengan tanda baca penutup kalimat.
- [ ] Jika tanda baca dipertahankan, jelaskan kontribusinya terhadap konteks dan batas kalimat.
- [ ] Buat aturan pengecualian khusus untuk tanda baca yang terdapat pada nama, alih-alih mempertahankan seluruh tanda baca tanpa penyaringan.

### 10. Menjelaskan model cased dan uncased

- [ ] Jelaskan bahwa model cased mempertahankan informasi huruf kapital.
- [ ] Jelaskan bahwa model uncased menormalisasi kapitalisasi.
- [ ] Jelaskan alasan kedua jenis model tersebut dibandingkan.
- [ ] Hubungkan karakteristik model dengan nama tokoh, lokasi, waktu, dan peristiwa dalam teks Sirah Nabawiyah.

### 11. Memperbaiki bagian lampiran

- [ ] Jangan meninggalkan judul atau bagian lampiran dalam keadaan kosong.
- [ ] Isi lampiran dengan hasil tambahan yang relevan, seperti:
  - Confusion matrix seluruh skenario;
  - Contoh data augmentasi;
  - Hasil evaluasi lengkap per label;
  - Contoh kueri Cypher; dan
  - Bukti hasil pengujian fungsional.
- [ ] Hapus bagian lampiran apabila memang tidak digunakan.

---

## B. Revisi dari Dosen Kedua

### 1. Memperjelas kontribusi NER dalam penelitian

Karena judul penelitian memuat NER dan knowledge graph, kedua bagian tersebut harus terlihat jelas dalam buku.

- [ ] Tambahkan satu contoh kalimat asli.
- [ ] Tampilkan hasil tokenisasi kalimat tersebut.
- [ ] Tampilkan label BIO untuk setiap token.
- [ ] Tampilkan entitas PERSON, EVENT, LOCATION, dan TIME yang berhasil diekstraksi.
- [ ] Tunjukkan bagaimana hasil NER tersebut menjadi node dalam knowledge graph.

Contoh penyajian:

| Token | Label BIO |
| --- | --- |
| Rasulullah | B-PERSON |
| pergi | O |
| ke | O |
| Madinah | B-LOCATION |

Hasil ekstraksi:

- PERSON: Rasulullah
- LOCATION: Madinah

### 2. Menampilkan bentuk data latih yang sebenarnya

- [ ] Tampilkan satu record data latih secara utuh.
- [ ] Sertakan `chunk_id`, teks asli, daftar token, label BIO, metadata halaman atau subbab, serta POS-tag apabila digunakan.
- [ ] Tampilkan bentuk data yang benar-benar diberikan kepada model.
- [ ] Jelaskan bahwa daftar token berasal dari satu kalimat atau chunk yang sama, bukan potongan token yang tidak berhubungan.

### 3. Memperjelas istilah chunk, token, subtoken, dan batch

- [ ] Jelaskan **chunk** sebagai potongan teks yang masih dapat memuat beberapa kalimat.
- [ ] Jelaskan **token** sebagai unit kata atau tanda baca hasil tokenisasi.
- [ ] Jelaskan **subtoken** sebagai pecahan token yang dihasilkan tokenizer IndoBERT/WordPiece.
- [ ] Jelaskan **batch** sebagai kumpulan sequence yang diproses secara bersamaan ketika pelatihan.
- [ ] Tegaskan bahwa IndoBERT melakukan token classification terhadap satu urutan token yang memiliki konteks, bukan mengklasifikasikan setiap kata secara terpisah tanpa konteks.

### 4. Memperjelas penyelarasan token–subtoken dan label BIO

- [ ] Jelaskan kondisi ketika satu kata dipecah menjadi beberapa subtoken.
- [ ] Jelaskan cara label BIO diselaraskan dengan subtoken.
- [ ] Nyatakan apakah hanya subtoken pertama yang diberi label dan subtoken berikutnya diabaikan, atau label diteruskan ke seluruh subtoken.
- [ ] Tegaskan unit masukan model, apakah berupa kalimat, chunk, atau sequence dengan panjang maksimum tertentu.

### 5. Memperjelas alur NER menuju knowledge graph

- [ ] Uraikan tahapan secara runtut:
  1. Prediksi entitas oleh model NER;
  2. Penggabungan hasil dari seluruh chunk;
  3. Normalisasi nama atau alias;
  4. Penghapusan entitas duplikat;
  5. Pembentukan node;
  6. Penentuan relasi;
  7. Penyimpanan ke Neo4j; dan
  8. Pengujian serta analisis graf.
- [ ] Jangan hanya menampilkan hasil graf tanpa menjelaskan proses pembentukannya.

### 6. Memperbaiki istilah “alias clustering”

Proses yang digunakan terdiri atas pengelompokan manual, Jaro–Winkler similarity, dan threshold kemiripan. Oleh karena itu, istilah yang lebih aman adalah:

> Normalisasi alias berbasis Jaro–Winkler similarity dan validasi manual.

- [ ] Pertimbangkan mengganti istilah “alias clustering” menjadi “normalisasi alias” atau “pengelompokan alias berbasis kemiripan”.
- [ ] Jika tetap menggunakan istilah clustering, jelaskan algoritma clustering, penentuan jumlah cluster, pemilihan hasil terbaik, dan metrik evaluasinya.
- [ ] Pastikan nama metode Jaro–Winkler ditulis dengan benar dan dijelaskan cara penggunaannya.

### 7. Memperjelas metode penentuan relasi

- [ ] Jelaskan alasan dua entitas dianggap memiliki hubungan.
- [ ] Jelaskan penggunaan satu kalimat atau jarak sekitar 200 karakter sebagai batas co-occurrence.
- [ ] Berikan dasar pemilihan batas 200 karakter.
- [ ] Tambahkan referensi penelitian yang menggunakan pendekatan serupa.
- [ ] Tampilkan contoh relasi yang benar dan relasi yang salah.
- [ ] Jelaskan apakah semua entitas dalam satu subbab event otomatis dihubungkan atau tetap melalui pemeriksaan konteks.

### 8. Menangani kesalahan relasi akibat negasi

Contoh permasalahan:

> Abu Jahal tidak mengikuti Perang Badar.

Aturan kedekatan dapat keliru menghasilkan relasi:

`Abu Jahal — INVOLVED_IN → Perang Badar`

Padahal kalimat tersebut menyatakan ketidakterlibatan.

- [ ] Tambahkan aturan deteksi negasi.
- [ ] Periksa kata kerja atau frasa yang menentukan makna hubungan.
- [ ] Lakukan validasi konteks sebelum membuat relasi.
- [ ] Lakukan pemeriksaan manual terhadap sampel relasi.
- [ ] Jika belum dapat diperbaiki, masukkan kesalahan akibat negasi sebagai keterbatasan penelitian.

### 9. Menambahkan dasar penelitian untuk konstruksi knowledge graph

- [ ] Tambahkan referensi mengenai entity linking atau entity normalization.
- [ ] Tambahkan referensi mengenai relation extraction.
- [ ] Tambahkan referensi mengenai pembentukan relasi berbasis co-occurrence.
- [ ] Tambahkan referensi mengenai pembangunan knowledge graph dari teks.
- [ ] Jelaskan bagian metode terdahulu yang diadopsi dan bagian yang dimodifikasi untuk data Sirah Nabawiyah.

### 10. Menambahkan evaluasi kualitas knowledge graph

Pengujian fungsional melalui kueri belum cukup untuk menyatakan bahwa knowledge graph berkualitas baik.

- [ ] Cari metode evaluasi kualitas knowledge graph dari penelitian sebelumnya.
- [ ] Pertimbangkan aspek berikut:
  - Ketepatan node;
  - Ketepatan relasi;
  - Konsistensi skema;
  - Kelengkapan relasi;
  - Validitas semantik;
  - Traceability ke kalimat sumber; dan
  - Precision relasi berdasarkan pemeriksaan manual.
- [ ] Tambahkan dasar teorinya pada Bab 2.
- [ ] Tambahkan prosedur pengujiannya pada Bab 3.
- [ ] Tampilkan hasil evaluasinya pada Bab 4.

### 11. Membedakan “kueri berhasil” dan “jawaban benar”

- [ ] Jangan menyatakan graf sepenuhnya valid hanya karena kueri dapat dijalankan, hasilnya tidak kosong, dan hasil mempunyai sumber teks.
- [ ] Bedakan keberhasilan teknis kueri dengan kebenaran semantik jawabannya.
- [ ] Gunakan kesimpulan yang lebih tepat, misalnya:

> Knowledge graph dapat menjalankan kebutuhan penelusuran yang diuji, tetapi ketepatan semantik beberapa relasi masih memerlukan validasi lebih lanjut.

---

## C. Urutan Prioritas Revisi

### Prioritas 1 — Substansi dan validitas penelitian

- [ ] Perkuat metode pembentukan relasi knowledge graph.
- [ ] Tangani atau jelaskan kesalahan relasi akibat negasi.
- [ ] Tambahkan evaluasi kualitas knowledge graph.
- [ ] Perbaiki klaim penanganan ketidakseimbangan kelas.
- [ ] Perkuat dasar pemilihan hyperparameter.

### Prioritas 2 — Kejelasan metodologi

- [ ] Tambahkan contoh input–proses–output NER.
- [ ] Jelaskan token, subtoken, chunk, batch, dan penyelarasan label BIO.
- [ ] Tampilkan bentuk data latih yang sebenarnya.
- [ ] Perbaiki istilah alias clustering.
- [ ] Perjelas alur NER hingga menjadi knowledge graph.

### Prioritas 3 — Penyajian dan format dokumen

- [ ] Perbaiki halaman awal setiap bab.
- [ ] Ulangi header tabel yang berpindah halaman.
- [ ] Perbaiki rujukan nomor persamaan.
- [ ] Tambahkan confusion matrix.
- [ ] Samakan warna grafik dengan legenda.
- [ ] Isi atau hapus lampiran kosong.

## D. Catatan

Beberapa kata, nama, angka, dan nomor halaman dalam rekaman kurang jelas. Oleh karena itu, angka serta nomor halaman yang disebutkan perlu dicocokkan kembali dengan Buku TA dan PPT sebelum revisi final dilakukan.
