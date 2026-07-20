# Naskah final — BAB 4 (siap copas)

## A. Confusion matrix (narasi pengiring gambar)

Gambar confusion matrix disajikan pada tingkat entitas dengan lima kelas, yaitu O, Person, Location,
Event, dan Time, dengan warna menyatakan proporsi per baris. Untuk keterbacaan, pada bagian utama
ditampilkan satu confusion matrix terbaik pada setiap kelompok skenario, sedangkan confusion matrix
seluruh skenario ditempatkan pada lampiran. Dari confusion matrix skenario terbaik terlihat bahwa
kesalahan model didominasi oleh kesalahan deteksi, yaitu entitas yang terlewat dan entitas palsu,
sedangkan kesalahan tipe antar kelas sangat sedikit. Hal ini menunjukkan bahwa model telah memahami
perbedaan keempat tipe entitas, dan sisa kesalahan terletak pada batas span serta deteksi entitas.

## B. Perbaikan klaim augmentasi (ganti kalimat "menyeimbangkan")

Data augmentation berhasil menurunkan tingkat ketimpangan kelas, ditunjukkan oleh berkurangnya rasio
Person terhadap Event dari sekitar 17,4 banding 1 menjadi sekitar 8,8 banding 1, meskipun distribusi
antarkelas belum seimbang. Tiga hal dibedakan secara eksplisit, yaitu bertambahnya jumlah data,
berkurangnya rasio ketimpangan, dan tidak tercapainya kondisi seimbang. Keberhasilan augmentasi
dalam menangani ketimpangan tidak diukur dari tercapainya rasio satu banding satu, melainkan dari
peningkatan kinerja kelas minoritas. Setelah augmentasi, F1-score kelas Time meningkat dari 0,798
menjadi 0,904 dan kelas Event dari 0,934 menjadi 0,954, sementara kelas Person tetap terjaga. Dengan
demikian, augmentasi meningkatkan kemampuan model mengenali kelas yang lebih jarang.

## C. Perbandingan Ground Truth dan Prediksi (tabel baru)

Tabel berikut membandingkan entitas acuan dengan prediksi model terbaik pada data uji.

| Entitas (acuan) | Ground truth | Prediksi | Kategori |
|---|---|---|---|
| Jazirah Arab | LOCATION | LOCATION | Benar |
| Haritsah bin Amr | PERSON | PERSON | Benar |
| Badr | LOCATION | EVENT | Salah tipe |
| bulan Maret 571 M | TIME | Maret 571 M | Kesalahan batas |
| Cina | LOCATION | Tidak terdeteksi | False negative |
| timur | Tidak ada | LOCATION | False positive |

Dari 1969 entitas acuan, sebanyak 1921 diprediksi benar, 3 mengalami kesalahan tipe, 20 mengalami
kesalahan batas, dan 25 tidak terdeteksi, serta terdapat 25 entitas prediksi yang bersifat palsu.
Kesalahan tipe yang sangat sedikit menegaskan bahwa masalah utama terletak pada deteksi dan batas
entitas, bukan pada klasifikasi tipe.

## D. Tabel 4.28 (revisi judul + isi kuantitatif)

Ganti judul Tabel 4.28 menjadi "Ringkasan Hasil Pengujian Fungsional Knowledge Graph". Ganti isi
kolom biner menjadi kuantitatif seperti berikut.

| Fungsi | Jumlah diperiksa | Valid | Tidak valid | Kesesuaian semantis | Terlacak |
|---|---:|---:|---:|---:|---:|
| F1 | 58 relasi | 14 | 44 | 24,14% | 100% |
| F2 | 10 relasi | 2 | 8 | 20,00% | 100% |
| F3 | 4 relasi | 3 | 1 | 75,00% | 100% |
| F4 | 4 relasi | 0 | 4 | 0,00% | 100% |
| F5 | 21 jalur (15 lokasi unik) | 3 | 18 | 14,29% | 100% |
| F6 | 17 relasi | 14 | 3 | 82,35% | 100% |
| Total | 114 | 36 | 78 | 31,58% | 100% |

Paragraf setelah tabel:

> Hasil pengujian menunjukkan bahwa keberhasilan operasional mencapai 100% karena seluruh enam kueri
> dapat dijalankan dan menghasilkan data, dan keterlacakan juga mencapai 100% karena seluruh relasi
> yang diuji memiliki metadata bukti dan halaman. Meskipun demikian, tingkat kesesuaian semantis
> berbeda pada setiap fungsi. Perbedaan ini menunjukkan bahwa kemampuan graf menjalankan kueri tidak
> secara otomatis menjamin ketepatan seluruh jawaban. Rendahnya kesesuaian semantis pada beberapa
> fungsi terutama dipengaruhi oleh pembentukan relasi berbasis kedekatan, pengabaian negasi, serta
> propagasi kesalahan pada penelusuran multi-hop.

> Catatan: Tabel 4.29 tetap digunakan untuk contoh ketidaksesuaian hasil dengan teks sumber.
