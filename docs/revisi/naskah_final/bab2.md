# Naskah final — BAB 2 (siap copas)

## 2.x Confusion Matrix (subbab baru)

Confusion matrix merupakan tabel yang membandingkan label acuan dengan label prediksi model untuk
setiap kelas, sehingga memperlihatkan bukan hanya jumlah prediksi yang benar tetapi juga pola
kesalahan antarkelas. Baris menyatakan kelas acuan dan kolom menyatakan kelas prediksi. Sel pada
diagonal berisi prediksi yang benar, sedangkan sel di luar diagonal menunjukkan kekeliruan
klasifikasi antarkelas.

Pada penelitian ini confusion matrix disajikan pada dua tingkat yang perlu dibedakan secara tegas.
Tingkat entitas menggunakan empat tipe entitas, yaitu Person, Location, Event, dan Time, untuk
menilai kecocokan tipe pada entitas yang terdeteksi. Tingkat token menggunakan skema BIO dengan
sembilan kelas, yaitu label O serta label B- dan I- untuk masing-masing tipe entitas, sehingga
evaluasi pada tingkat token bukan sekadar empat kelas. Dari confusion matrix dapat diturunkan nilai
precision, recall, dan F1-score untuk setiap kelas.

## 2.x Ketidakseimbangan Kelas dan Penanganannya (tambahan)

Ketidakseimbangan kelas terjadi ketika jumlah contoh antarkelas sangat berbeda. Pada NER,
ketidakseimbangan bersifat berjenjang. Pada tingkat token, label O jauh mendominasi seluruh token
entitas. Pada tingkat kelas entitas, tipe tertentu seperti Person jauh lebih banyak daripada tipe
yang lebih jarang seperti Event dan Time. Henning dkk. (2023) menyatakan bahwa model NLP cenderung
berkinerja buruk pada kelas yang jarang muncul, dan penanganannya dapat berupa penambahan data
melalui augmentasi, penyesuaian bobot pada fungsi kerugian, atau perubahan representasi. Tidak
terdapat ambang universal yang menyatakan sebuah dataset telah seimbang. Keberhasilan penanganan
ketidakseimbangan diukur dari peningkatan kinerja kelas minoritas tanpa mengorbankan kelas
mayoritas (Nemoto dkk., 2024), bukan dari tercapainya rasio satu banding satu.

## 2.x Model Pra-latih Cased dan Uncased (tambahan, sebelum pembahasan hasil)

Model bahasa pra-latih dapat dibedakan menjadi cased dan uncased berdasarkan perlakuannya terhadap
huruf kapital. Model cased mempertahankan informasi kapitalisasi sehingga penulisan dengan huruf
kapital dan huruf kecil diperlakukan berbeda, sedangkan model uncased menormalkan seluruh huruf
menjadi huruf kecil sesuai mekanisme tokenizer-nya. Karakteristik ini relevan untuk NER pada teks
Sirah Nabawiyah karena nama tokoh, lokasi, waktu, dan peristiwa umumnya diawali huruf kapital.
Model uncased menghilangkan sinyal kapitalisasi tersebut, sementara model cased mempertahankannya.

## 2.7 Pengujian Fungsional dan Validitas Semantis (tambahan setelah paragraf competency questions)

Evaluasi berbasis competency questions dalam penelitian ini digunakan untuk menilai kesesuaian
knowledge graph dengan tujuan penelusuran yang telah ditetapkan. Evaluasi tersebut tidak
dimaksudkan untuk mengukur kelengkapan seluruh fakta dalam knowledge graph atau membandingkan
keseluruhan isi graf dengan gold standard. Penilaian dilakukan pada dua tingkat, yaitu keberhasilan
operasional kueri dan ketepatan semantis jawaban. Keberhasilan operasional menunjukkan bahwa pola
penelusuran dapat dijalankan, sedangkan ketepatan semantis menunjukkan bahwa hubungan yang
dikembalikan oleh kueri didukung oleh konteks teks sumber.

Selain kelayakan fungsional, ketepatan isi knowledge graph dinilai dari proporsi jawaban kueri yang
benar-benar didukung teks sumber. Karena tidak tersedia acuan lengkap seluruh relasi yang
seharusnya ada, ketepatan tersebut diperkirakan dengan memeriksa secara manual setiap jawaban yang
dikembalikan kueri terhadap sumber, lalu dinyatakan sebagai validitas semantis dan dihitung dengan
Persamaan (2.x):

> kesesuaian semantis fungsi ke-i = (jumlah jawaban yang didukung sumber ÷ jumlah seluruh jawaban
> yang diperiksa) × 100%

## 2.x Dasar Konstruksi Knowledge Graph (tambahan rujukan)

Pembentukan knowledge graph dari teks umumnya mengikuti tahapan ekstraksi entitas, ekstraksi
relasi, dan integrasi ke dalam graf (survei konstruksi knowledge graph, 2024–2025). Penyatuan
variasi nama entitas ke bentuk kanonik merupakan bagian dari tugas entity normalization (Sevgili
dkk., 2022). Pada penelitian ini, penyatuan nama dilakukan dengan pendekatan yang lebih sederhana,
yaitu normalisasi alias berbasis kesamaan string Jaro-Winkler dan validasi manual, bukan model
entity linking berbasis pembelajaran. Demikian pula, relasi antar entitas dibentuk melalui induksi
heuristik berbasis kedekatan, bukan semantic relation extraction penuh dengan model relasi terlatih.

> ⚠️ Lengkapi sitasi persis (penulis, tahun, halaman) dari `docs/revisi/artefak/referensi_konstruksi_kg.md`.

## Perbaikan notasi Persamaan (2.13) betweenness

Cari kalimat "…menunjukkan jumlah jalur terpendek dari simpul 𝒕 ke simpul 𝒕 yang melewati simpul v"
dan betulkan menjadi "…menunjukkan jumlah jalur terpendek dari simpul **𝒔** ke simpul **𝒕** yang
melewati simpul v".
