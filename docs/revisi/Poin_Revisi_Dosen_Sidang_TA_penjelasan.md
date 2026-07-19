# Poin dan Penjelasan Revisi Dosen Sidang Tugas Akhir

Dokumen ini disusun berdasarkan rekaman `Sidang.mp3`. Pembagian dosen mengikuti pergantian sesi pertanyaan dalam rekaman. Sesi dosen pertama berlangsung kurang lebih pada menit 15:58–43:04, sedangkan sesi dosen kedua dimulai kurang lebih pada menit 43:07 hingga akhir rekaman.

## A. Revisi dari Dosen Pertama

### 1. Bentuk hubungan dalam knowledge graph perlu diperjelas

Dosen meminta agar knowledge graph tidak hanya ditampilkan sebagai kumpulan node yang mengelilingi sebuah event. Visualisasi tersebut memang memperlihatkan bahwa suatu event terhubung dengan beberapa tokoh, waktu, dan lokasi, tetapi belum menunjukkan hubungan yang lebih spesifik di antara informasi-informasi tersebut.

Sebagai contoh, pada Perang Badar terdapat beberapa tokoh dan beberapa entitas waktu. Graf yang sekarang belum dapat menjelaskan seorang tokoh tertentu hadir pada waktu yang mana. Semua PERSON dan TIME hanya sama-sama terhubung dengan EVENT Perang Badar. Oleh karena itu, perlu ditampilkan satu contoh alur relasi yang lengkap, misalnya **Perang Badar → tokoh yang terlibat → waktu keterlibatan → lokasi**. Jika struktur graf yang digunakan memang belum dapat menghubungkan seorang tokoh dengan waktu yang spesifik, hal tersebut harus dijelaskan sebagai keterbatasan penelitian dan tidak boleh dikesankan seolah-olah sudah dapat dijawab oleh graf.

Dosen juga menanyakan keberadaan bobot pada relasi. Apabila relasi memiliki bobot, buku perlu menjelaskan makna bobot, sumber nilainya, dan cara perhitungannya. Jika bobot hanya digunakan pada proyeksi jaringan tokoh untuk SNA, perbedaannya dengan relasi pada knowledge graph utama juga harus ditegaskan.

### 2. Tata letak Buku TA perlu diperiksa kembali

Dosen menemukan beberapa masalah pada tata letak buku. Setiap judul bab seharusnya dimulai pada halaman ganjil. Oleh karena itu, perlu diperiksa kembali apakah masih ada judul bab yang dimulai pada halaman genap atau terdapat halaman kosong yang ditempatkan secara tidak tepat.

Selain itu, tabel yang berlanjut ke halaman berikutnya harus menampilkan kembali header kolomnya. Tanpa header yang berulang, pembaca akan kesulitan memahami isi kolom pada halaman lanjutan. Seluruh tabel panjang perlu diperiksa untuk memastikan judul kolom tetap muncul setelah perpindahan halaman.

### 3. Rujukan terhadap persamaan harus lebih spesifik

Dalam paragraf penjelasan, persamaan sebaiknya dirujuk menggunakan nomor yang sudah diberikan. Kalimat seperti “persamaan dapat dilihat di bawah ini” dinilai kurang tepat karena tidak menunjukkan persamaan yang dimaksud secara jelas.

Penulisannya perlu diubah menjadi, misalnya, “Perhitungan precision dapat dilihat pada Persamaan (2.1).” Pola yang sama perlu diterapkan pada seluruh persamaan agar nomor persamaan yang sudah dibuat benar-benar berfungsi sebagai rujukan dalam teks.

### 4. Confusion matrix perlu ditambahkan dan dijelaskan levelnya

Dosen meminta confusion matrix yang sesuai dengan empat tipe entitas penelitian, yaitu PERSON, EVENT, LOCATION, dan TIME. Confusion matrix dapat membantu menunjukkan kelas mana yang paling sering tertukar oleh model, bukan hanya menampilkan nilai precision, recall, dan F1-score.

Namun, level evaluasinya harus dijelaskan dengan hati-hati. Jika confusion matrix disusun pada tingkat tipe entitas, matriks dapat memperlihatkan empat kelas tersebut. Jika disusun pada tingkat token BIO, kelasnya bukan hanya empat karena terdapat `B-PERSON`, `I-PERSON`, dan pola serupa untuk entitas lain, ditambah label `O`. Confusion matrix utama dapat ditempatkan di Bab 4, sedangkan matriks lengkap dari seluruh skenario dapat dipindahkan ke lampiran agar pembahasan utama tidak terlalu padat.

### 5. Dasar pemilihan hyperparameter harus diperkuat

Hyperparameter penelitian tidak cukup dijelaskan hanya dengan menyatakan bahwa nilainya mengikuti notebook atau penelitian Arianto. Dataset penelitian terdahulu berbeda dengan dataset Sirah Nabawiyah, sehingga pemakaian nilai yang sama memerlukan alasan yang lebih kuat.

Buku perlu menjelaskan dasar pemilihan learning rate, batch size, jumlah epoch, threshold penerimaan pseudo-label, batas iterasi, serta hyperparameter penting lainnya. Penjelasannya dapat berasal dari penelitian terdahulu, karakteristik model IndoBERT, keterbatasan komputasi, atau hasil percobaan awal. Jika hyperparameter diadaptasi dari penelitian lain, tuliskan bahwa nilai tersebut dijadikan nilai awal dan diterapkan kembali pada dataset penelitian ini, bukan langsung diklaim sebagai konfigurasi terbaik tanpa pengujian.

### 6. Perbedaan metode penanganan ketidakseimbangan kelas perlu dijelaskan

Dosen meminta penjelasan yang lebih tegas mengenai cara kerja setiap metode. Weighted cross-entropy menangani ketimpangan dengan memberikan bobot loss yang lebih besar kepada kelas minoritas. Metode ini tidak menambah jumlah data. Supervised contrastive learning juga tidak mengubah jumlah data, tetapi membantu model membentuk representasi entitas dari kelas yang sama agar lebih dekat dan kelas yang berbeda agar lebih terpisah.

Data augmentation berbeda dari kedua metode tersebut karena benar-benar menghasilkan data tambahan. Oleh sebab itu, buku perlu menampilkan contoh teks sebelum dan sesudah paraphrasing atau mention replacement, sekaligus memperlihatkan perubahan distribusi setiap kelas. Pembaca perlu mengetahui kelas mana yang menjadi target augmentasi dan bagaimana proses augmentasi mempertahankan label BIO agar tetap benar.

### 7. Klaim bahwa augmentasi “menyeimbangkan kelas” perlu diperbaiki

Dosen mempermasalahkan kesimpulan bahwa data augmentation telah menyeimbangkan kelas. Berdasarkan contoh rasio yang dibahas, ketimpangan berkurang dari sekitar 18:1 menjadi 9:1. Perubahan tersebut menunjukkan adanya pengurangan jarak antara kelas mayoritas dan minoritas, tetapi distribusinya masih belum sepenuhnya seimbang.

Karena itu, kalimat yang lebih aman adalah: **“Data augmentation berhasil mengurangi tingkat ketimpangan distribusi kelas, meskipun distribusi antarkelas belum sepenuhnya seimbang.”** Buku juga perlu menjelaskan mengapa kelas PERSON sebagai kelas mayoritas ikut bertambah setelah augmentasi. Hal tersebut dapat terjadi karena satu kalimat hasil paraphrasing atau mention replacement masih memuat entitas lain selain kelas minoritas yang menjadi target. Dengan penjelasan ini, hasil augmentasi tidak sekadar dinilai dari bertambahnya data, tetapi dari perubahan rasio kelas dan dampaknya terhadap nilai evaluasi per entitas.

### 8. Warna grafik dan legenda harus konsisten

Dosen menemukan grafik yang warna garis atau batangnya tidak sesuai dengan legenda. Ketidaksesuaian tersebut dapat membuat pembaca salah membedakan hasil baseline, augmentation, dan metode lainnya.

Semua grafik perlu diperiksa ulang. Warna yang digunakan pada data harus sama dengan warna pada legenda, serta konsisten di seluruh gambar. Jika augmentation selalu berwarna merah pada satu grafik, sebaiknya warna yang sama digunakan untuk augmentation pada grafik lain, kecuali ada alasan desain yang jelas.

### 9. Penggunaan tanda baca sebagai token perlu dievaluasi

Dosen menemukan contoh token yang hanya berupa tanda titik. Hal ini memunculkan pertanyaan apakah semua tanda baca memang diperlukan dalam pemodelan. Alasan mempertahankan tanda baca untuk menjaga konteks kalimat dapat diterima, tetapi tidak berarti seluruh tanda baca harus diperlakukan tanpa penyaringan.

Perlu dibedakan antara tanda baca yang berfungsi sebagai batas kalimat dan tanda baca yang menjadi bagian dari nama atau bentuk penulisan tertentu. Aturan prapemrosesan dapat dibuat lebih spesifik agar tanda baca yang tidak informatif dapat dibersihkan tanpa merusak nama tokoh atau lokasi. Jika tanda baca tetap digunakan, buku harus menjelaskan kontribusinya terhadap tokenisasi dan prediksi NER.

### 10. Perbedaan model cased dan uncased perlu dijelaskan

Pada bagian perbandingan model, terdapat model cased dan uncased, tetapi perbedaannya belum dijelaskan dengan cukup jelas. Model cased mempertahankan perbedaan huruf kapital, sedangkan model uncased menormalisasi kapitalisasi.

Perbedaan tersebut relevan bagi NER karena huruf kapital dapat menjadi petunjuk nama tokoh, lokasi, waktu, atau peristiwa. Namun, teks hasil OCR juga dapat memiliki kapitalisasi yang tidak konsisten. Buku perlu menghubungkan karakteristik tersebut dengan hasil eksperimen sehingga alasan model uncased atau cased memperoleh hasil tertentu tidak hanya dijelaskan melalui angka F1-score.

### 11. Lampiran yang kosong harus diisi atau dihapus

Dosen menemukan bagian lampiran yang masih kosong. Lampiran tersebut dapat digunakan untuk menyimpan confusion matrix seluruh skenario, contoh lengkap data augmentasi, hasil evaluasi per label, contoh kueri Cypher, dan bukti pengujian fungsional graf.

Jika tidak ada materi tambahan yang perlu ditampilkan, bagian lampiran kosong sebaiknya dihapus. Lampiran tidak boleh dipertahankan hanya sebagai judul tanpa isi.

---

## B. Revisi dari Dosen Kedua

### 1. Kontribusi dan proses NER harus terlihat secara konkret

Karena judul penelitian memuat Named-Entity Recognition dan pembangunan knowledge graph, kedua proses tersebut harus sama-sama terlihat jelas. Dosen belum memperoleh gambaran konkret mengenai bentuk masukan NER dan hasil yang dikeluarkan model.

Buku perlu menambahkan satu contoh lengkap yang dimulai dari kalimat asli, hasil tokenisasi, label BIO setiap token, entitas yang berhasil diekstraksi, hingga perubahan entitas tersebut menjadi node dalam graf. Misalnya, kalimat “Rasulullah pergi ke Madinah” dapat ditampilkan sebagai token `Rasulullah` dengan label `B-PERSON`, token `Madinah` dengan label `B-LOCATION`, dan token lain dengan label `O`. Setelah itu, tunjukkan bahwa hasil akhirnya adalah entitas PERSON “Rasulullah” dan LOCATION “Madinah”.

Contoh tersebut akan membantu pembaca memahami bahwa NER tidak langsung menghasilkan graf, tetapi menghasilkan entitas yang kemudian diproses dalam tahapan konstruksi knowledge graph.

### 2. Bentuk data latih yang sebenarnya perlu ditampilkan

Dosen menilai contoh data yang ada belum menggambarkan satu record data latih secara lengkap. Buku perlu menampilkan satu contoh yang berisi `chunk_id`, teks asli, daftar token, label BIO, metadata halaman atau subbab, dan POS-tag apabila digunakan.

Perlu dijelaskan pula bahwa token-token dalam contoh berasal dari satu kalimat atau satu chunk yang sama. Dengan demikian, pembaca dapat melihat hubungan antara teks naratif, hasil tokenisasi, label manual, dan format data yang benar-benar dimasukkan ke proses pelatihan.

### 3. Istilah chunk, token, subtoken, dan batch harus dibedakan

Dosen meminta penjelasan yang lebih mendasar mengenai unit data. Chunk adalah potongan teks yang dapat memuat satu atau beberapa kalimat. Token adalah unit kata atau tanda baca hasil tokenisasi awal. Subtoken adalah pecahan token yang dihasilkan oleh tokenizer IndoBERT atau WordPiece ketika suatu kata tidak terdapat secara utuh dalam kosakata model. Batch adalah kumpulan beberapa sequence yang diproses secara bersamaan pada satu langkah pelatihan.

Penjelasan tersebut penting agar tidak muncul kesan bahwa model mengklasifikasikan setiap kata secara terpisah tanpa konteks. IndoBERT menerima satu urutan token dan memprediksi label untuk setiap posisi token dengan mempertimbangkan konteks token lain dalam urutan yang sama.

### 4. Penyelarasan label BIO dengan subtoken perlu dijelaskan

Ketika satu kata dipecah menjadi beberapa subtoken, label BIO dari kata asal harus diselaraskan dengan hasil tokenisasi model. Buku perlu menjelaskan strategi yang benar-benar digunakan dalam kode, misalnya hanya memberikan label pada subtoken pertama dan mengabaikan subtoken berikutnya dengan nilai `-100`, atau meneruskan label yang sesuai kepada seluruh subtoken.

Selain itu, jelaskan unit yang dimasukkan ke model, apakah berupa satu kalimat atau satu chunk dengan panjang maksimum tertentu. Penjelasan ini harus konsisten dengan implementasi agar pembaca memahami alur data dari anotasi manual sampai pelatihan model.

### 5. Alur dari hasil NER menuju knowledge graph harus dibuat runtut

Dosen meminta proses pembangunan graf dijelaskan sebagai tahapan yang jelas. Setelah model NER menghasilkan prediksi, hasil dari seluruh chunk digabungkan. Entitas yang mempunyai variasi nama kemudian dinormalisasi, duplikasi dihapus, node dibentuk, relasi ditentukan, dan seluruh hasil dimuat ke Neo4j. Setelah itu barulah dilakukan pengujian fungsional dan SNA.

Urutan tersebut sebaiknya ditampilkan melalui diagram alur dan satu contoh data yang mengikuti seluruh proses. Dengan begitu, pembaca tidak hanya melihat graf akhir, tetapi memahami bagaimana satu entitas dari teks akhirnya menjadi node dan memperoleh relasi tertentu.

### 6. Istilah “alias clustering” perlu diperbaiki

Dosen mempertanyakan penggunaan istilah clustering karena proses yang dilakukan terdiri atas pengelompokan manual, perhitungan Jaro–Winkler similarity, dan penggunaan threshold kemiripan. Proses tersebut tidak otomatis sama dengan clustering yang mempunyai algoritma pembentukan cluster dan evaluasi cluster.

Istilah yang lebih tepat adalah **“normalisasi alias berbasis Jaro–Winkler similarity dan validasi manual”** atau **“pengelompokan alias berbasis kemiripan”**. Jika istilah clustering tetap dipertahankan, penelitian harus menjelaskan algoritma clustering, cara menentukan jumlah cluster, cara memilih hasil terbaik, dan metrik evaluasinya. Penggunaan istilah yang lebih tepat akan menghindari pertanyaan mengenai silhouette score, SSE, atau evaluasi cluster lain yang sebenarnya tidak digunakan dalam implementasi.

### 7. Metode penentuan relasi perlu memiliki dasar yang kuat

Relasi dalam graf saat ini ditentukan menggunakan co-occurrence, yaitu entitas berada dalam satu kalimat atau berjarak sekitar 200 karakter. Dosen meminta alasan pemilihan batas tersebut dan dasar penelitian yang mendukungnya.

Buku perlu menjelaskan apakah semua entitas yang muncul berdekatan langsung dianggap terhubung, atau masih terdapat pemeriksaan konteks. Sertakan contoh relasi yang berhasil dibentuk dengan benar dan contoh relasi yang salah. Batas 200 karakter tidak boleh tampak sebagai angka yang dipilih tanpa dasar; angka tersebut perlu didukung referensi, hasil eksperimen, atau penjelasan bahwa ia merupakan aturan heuristik yang memiliki keterbatasan.

### 8. Kesalahan relasi akibat negasi harus ditangani atau dinyatakan sebagai keterbatasan

Dosen menyoroti risiko relasi palsu pada kalimat yang mengandung negasi. Contohnya, kalimat “Abu Jahal tidak mengikuti Perang Badar” dapat menyebabkan Abu Jahal terhubung melalui relasi `INVOLVED_IN` karena PERSON dan EVENT muncul berdekatan. Padahal, makna kalimat justru menyatakan ketidakterlibatan.

Perbaikan dapat dilakukan dengan menambahkan deteksi negasi, memeriksa kata kerja relasional, atau memvalidasi konteks kalimat sebelum relasi dibuat. Sampel relasi juga dapat diperiksa secara manual untuk menghitung ketepatannya. Jika penanganan negasi belum menjadi bagian penelitian, kelemahan ini harus ditulis secara eksplisit sebagai keterbatasan metode pembentukan relasi.

### 9. Konstruksi knowledge graph harus didukung penelitian terdahulu

Dosen menilai metode pembentukan graf tidak boleh hanya berasal dari percobaan atau keputusan peneliti sendiri. Buku perlu menambahkan referensi mengenai entity normalization, entity linking, relation extraction, pembentukan relasi berbasis co-occurrence, dan konstruksi knowledge graph dari teks.

Setelah menemukan referensi yang sesuai, jelaskan bagian yang diadopsi dan bagian yang dimodifikasi untuk karakteristik teks Sirah Nabawiyah. Dengan demikian, aturan pembentukan node dan relasi mempunyai dasar metodologis yang dapat dipertanggungjawabkan.

### 10. Evaluasi kualitas knowledge graph perlu ditambahkan

Pengujian fungsional dengan menjalankan kueri belum cukup untuk menyatakan bahwa knowledge graph memiliki kualitas yang baik. Kueri yang berhasil dijalankan hanya membuktikan bahwa struktur graf dapat diakses dan menghasilkan data, bukan bahwa seluruh node dan relasinya benar secara semantik.

Dosen menyarankan mencari metode evaluasi kualitas knowledge graph dari penelitian terdahulu. Aspek yang dapat dipertimbangkan meliputi ketepatan node, ketepatan relasi, konsistensi skema, kelengkapan relasi, validitas semantik, serta keterlacakan hasil ke kalimat sumber. Salah satu pendekatan yang relevan adalah memeriksa sampel relasi secara manual dan menghitung precision relasi. Jika metode evaluasi tambahan digunakan, dasar teorinya perlu ditempatkan pada Bab 2, prosedurnya pada Bab 3, dan hasilnya pada Bab 4.

### 11. Keberhasilan kueri harus dibedakan dari kebenaran jawaban

Graf tidak dapat dinyatakan sepenuhnya valid hanya karena kueri berhasil dijalankan, hasilnya tidak kosong, dan setiap hasil memiliki sumber teks. Sumber teks tersebut masih perlu diperiksa untuk memastikan maknanya benar-benar mendukung relasi yang dibentuk.

Kesimpulan yang lebih tepat adalah: **“Knowledge graph dapat menjalankan kebutuhan penelusuran yang diuji, tetapi ketepatan semantik beberapa relasi masih memerlukan validasi lebih lanjut.”** Kesimpulan ini konsisten dengan temuan bahwa beberapa relasi dapat dilacak ke kalimat sumber, tetapi kalimat tersebut tidak selalu mendukung hubungan yang dihasilkan.

---

## C. Urutan Prioritas Revisi

### Prioritas pertama: substansi dan validitas penelitian

Perbaikan pertama sebaiknya difokuskan pada metode pembentukan relasi, kesalahan akibat negasi, evaluasi kualitas knowledge graph, klaim mengenai ketidakseimbangan kelas, dan dasar pemilihan hyperparameter. Bagian-bagian ini berhubungan langsung dengan validitas kesimpulan penelitian sehingga lebih penting daripada perbaikan tampilan.

### Prioritas kedua: kejelasan metodologi

Setelah substansi utama diperkuat, tambahkan contoh input–proses–output NER, bentuk data latih, penjelasan token dan subtoken, alur NER menuju knowledge graph, serta perbaikan istilah alias clustering. Tujuannya agar pembaca dapat merekonstruksi proses penelitian tanpa harus menebak implementasinya.

### Prioritas ketiga: penyajian dan format dokumen

Tahap terakhir mencakup perbaikan halaman awal bab, header tabel, rujukan persamaan, confusion matrix, warna grafik, dan lampiran. Walaupun bersifat penyajian, seluruh bagian ini tetap harus diperbaiki agar Buku TA konsisten dan mudah diperiksa.

## D. Catatan

Beberapa kata, nama, angka, dan nomor halaman dalam rekaman kurang jelas. Oleh karena itu, angka serta nomor halaman yang disebutkan perlu dicocokkan kembali dengan Buku TA dan PPT sebelum revisi final dilakukan.
