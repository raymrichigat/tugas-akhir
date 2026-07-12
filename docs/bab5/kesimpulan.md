# BAB 5 KESIMPULAN DAN SARAN

<!-- SINKRON STRUKTURAL dengan buku `docs/Buku-TA-Genta.pdf` (hlm 89-90), per 2026-07-12.
     Struktur mengikuti buku (4 kesimpulan + 4 saran). ANGKA sudah dimutakhirkan ke benchmark
     BARU (GT-terkoreksi + KG v4) agar konsisten dengan Bab 4 .md hasil migrasi 10 Juli:
       - data uji 254 chunk / 49.739 token / 1.969 entitas (Person 1.302 / Location 474 / Time 118 / Event 75)
       - augmentation F1 mikro 0,9756; Event 0,9342->0,9542; Time 0,7983->0,9038
       - SNA v4 (scoped): 137 simpul / 1.853 sisi / density 0,199 / Louvain 8 komunitas / Q 0,2831
     ⚠️ Buku Word/PDF Bab 5 MASIH pakai angka lama (0,9581/208 node/Q 0,3851) -> perlu di-update di Word.
     Catatan: draf .md sebelumnya memuat 8 saran + poin konstruksi KG terpisah; di sini diringkas
     mengikuti struktur buku. Bila ingin versi lebih rinci, lihat riwayat git file ini. -->

## 5.1 Kesimpulan

Berdasarkan hasil pengujian dan pembahasan yang telah dilakukan, diperoleh kesimpulan sebagai berikut.

1. Persiapan data teks Sirah Nabawiyah dilakukan melalui beberapa tahapan, yaitu pemindaian teks menggunakan OCR (*Optical Character Recognition*), pembersihan dan pemrosesan awal teks (*preprocessing*), pemotongan teks menjadi bagian-bagian pendek (*chunking*), serta pelabelan entitas. Pelabelan awal dilakukan secara semi-otomatis menggunakan skema BIO berbasis pola dan kamus entitas pada empat kelas, yaitu *Person*, *Event*, *Location*, dan *Time*. Selanjutnya, variasi penulisan nama yang merujuk pada entitas yang sama disatukan melalui penyatuan alias (*alias clustering*) agar acuan entitas menjadi lebih konsisten. Tahapan ini menghasilkan data uji sebanyak 254 *chunk* yang terdiri atas 49.739 token dan 1.969 entitas, dengan rincian 1.302 entitas *Person*, 474 entitas *Location*, 118 entitas *Time*, dan 75 entitas *Event*. Distribusi tersebut menunjukkan adanya ketidakseimbangan kelas yang cukup tajam, terutama pada kelas *Event* dan *Time* sebagai kelas minoritas.

2. Model ekstraksi entitas dikembangkan menggunakan pendekatan NER berbasis IndoBERT yang dilatih secara semi-*supervised* melalui *iterative self-training*. Pada pendekatan ini, model mula-mula dilatih menggunakan data berlabel awal, kemudian secara bertahap diperkaya dengan prediksi berkeyakinan tinggi dari data yang belum berlabel. Berdasarkan tiga skenario uji coba, hasil terbaik diperoleh pada model IndoBERT *uncased* dengan teknik *data augmentation* melalui *mention replacement*. Konfigurasi ini menghasilkan *F1-score* mikro tingkat entitas sebesar 0,9756, dengan *precision* sebesar 0,9756 dan *recall* sebesar 0,9756. Teknik *augmentation* terbukti efektif dalam meningkatkan pengenalan entitas yang jarang muncul, terutama pada kelas *Time* yang meningkat dari 0,7983 menjadi 0,9038 dan kelas *Event* yang meningkat dari 0,9342 menjadi 0,9542. Meskipun demikian, kesalahan model masih didominasi oleh keputusan deteksi, yaitu membedakan entitas dari kata biasa, serta lebih banyak terkonsentrasi pada kelas dengan jumlah data paling sedikit. Perbandingan model juga menunjukkan bahwa model *uncased* memberikan hasil terbaik, sedangkan penurunan performa pada model *cased* dan RoBERTa lebih berkaitan dengan masalah teknis penyelarasan label. Selain itu, penambahan modul POS-tag belum memberikan peningkatan performa yang berarti pada konfigurasi yang diuji.

3. Evaluasi hasil ekstraksi dan analisis graf menunjukkan bahwa model NER mampu mengenali entitas dengan performa tinggi, sedangkan kelayakan graf dapat ditinjau melalui pengujian fungsional dan *Social Network Analysis* (SNA). Pada pengujian fungsional, enam skenario kueri *Cypher* yang mewakili kebutuhan pencarian berbasis hubungan dapat dijalankan dengan baik. Keenam skenario tersebut meliputi pencarian tokoh dalam peristiwa, peristiwa pada suatu lokasi, peristiwa pada suatu waktu, peristiwa yang melibatkan tokoh tertentu, penelusuran *multi-hop*, dan urutan kronologis peristiwa. Seluruh skenario menghasilkan jawaban yang dapat ditelusuri kembali ke teks sumbernya.

4. Pada analisis SNA terhadap proyeksi jaringan antartokoh, graf yang terbentuk terdiri atas 137 simpul dan 1.853 sisi dengan nilai *density* sebesar 0,199. Struktur jaringan tersebut menunjukkan pola yang sesuai dengan narasi Sirah, dengan tokoh Muhammad memiliki dominasi yang kuat pada seluruh ukuran sentralitas. Selain itu, deteksi komunitas menggunakan algoritma Louvain menghasilkan 8 komunitas dengan nilai modularitas sebesar 0,2831, yang secara umum koheren secara naratif. Meskipun demikian, analisis ini juga menunjukkan adanya keterbatasan metode, yaitu munculnya beberapa tokoh dengan sentralitas berlebih akibat over-ekstraksi relasi `INVOLVED_IN` yang dibentuk berdasarkan kedekatan kemunculan dalam teks.

## 5.2 Saran

Berdasarkan keterbatasan yang ditemukan selama penelitian, beberapa saran untuk pengembangan lanjutan adalah sebagai berikut.

1. Metode ekstraksi relasi perlu ditingkatkan, khususnya pada relasi `INVOLVED_IN`. Pada penelitian ini, relasi masih dibentuk berdasarkan kedekatan kemunculan tokoh dan peristiwa dalam *chunk* yang sama, sehingga berpotensi menimbulkan *over-extraction* maupun *under-extraction*. Penelitian selanjutnya disarankan menambahkan ekstraksi relasi berbasis kata kerja atau predikat tindakan agar hubungan antar-entitas lebih mencerminkan peran sebenarnya dalam narasi.

2. Pendeteksian entitas *Event* perlu diperluas agar tidak hanya bergantung pada nama peristiwa eksplisit. Beberapa peristiwa penting, seperti kelahiran Nabi, wahyu pertama, dan wafat Nabi, dapat muncul dalam bentuk frasa deskriptif atau konstruksi kata kerja. Oleh karena itu, penelitian lanjutan dapat mengembangkan metode *event extraction* berbasis pola verbal agar penambahan peristiwa tidak terlalu bergantung pada proses manual.

3. Kualitas pelabelan dan pemodelan NER perlu diperbaiki. Pemeriksaan manual terhadap *ground truth* perlu diperketat, terutama pada entitas yang tidak konsisten akibat kapitalisasi. Selain itu, fungsi penyelarasan label kata ke *subword* perlu diperbaiki agar perbandingan model *uncased*, *cased*, dan RoBERTa dapat dilakukan secara lebih adil. Modul POS-tag juga sebaiknya diuji kembali menggunakan keluaran *POS tagger* yang sesungguhnya, bukan nilai *placeholder*.

4. Cakupan dan pemanfaatan *knowledge graph* perlu diperluas. Tahap penyatuan alias perlu diperkuat, terutama pada variasi nama lokasi seperti Yatsrib dan Madinah, agar graf lebih ringkas dan akurat. Penelitian selanjutnya juga disarankan menguji metode pada sumber Sirah lain serta mengembangkan pemanfaatan graf, misalnya untuk sistem tanya-jawab atau visualisasi sejarah Sirah.
