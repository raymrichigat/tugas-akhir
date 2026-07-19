# Teks siap-tempel: Evaluasi Kualitas KG / Validitas Semantis (Bu Nanik #8)

> Melengkapi seluruh bab untuk poin "pengujian fungsional belum cukup". Prinsip: evaluasi
> fungsionalmu **sudah benar** — yang dilakukan hanya **mengkuantifikasi** pemeriksaan manual
> yang sudah ada + memperjelas batas klaim. Angka final: **Tabel 4.28 di
> `hasil_validitas_semantis.md`** (total 36/114 = 31,58%; F6 tertinggi 82,35%, F4 terendah 0%).
>
> ℹ️ **Tanpa referensi eksternal baru**: cukup kuantifikasi + rujukan competency-questions 2025
> yang sudah ada di §2.7 (Greco; Keet & Khan; Farrugia; Illueca Fernández). Paulheim 2017 & Gao
> 2019 **tidak dipakai** (di luar 5 tahun terakhir).
>
> ⚠️ **Recall tidak dihitung**: kita hanya punya *precision* jawaban yang dikembalikan, bukan
> daftar seluruh relasi yang seharusnya ada → jangan paksakan recall/F1 relasi di penelitian ini.

---

## 0. TUJUAN penelitian (hal 3–4, poin ke-4)

Ganti frasa "…untuk menguji kualitas ekstraksi entitas dan **kelayakan struktur graf**…"
menjadi (SNA hanya *mendeskripsikan* struktur, tidak menilai kelayakannya):

> Mengevaluasi hasil NER melalui tiga skenario uji coba serta menganalisis knowledge graph yang
> dibangun melalui Social Network Analysis dan pengujian fungsional, untuk menguji kualitas
> ekstraksi entitas, **mendeskripsikan struktur jaringan**, dan **menilai kelayakan graf dalam
> mendukung penelusuran informasi** pada Sirah Nabawiyah.

Pemetaan jadi jelas: NER → kualitas ekstraksi; SNA → deskripsi struktur; pengujian fungsional →
kelayakan penelusuran.

---

## 1. BAB 2 — sisipan setelah paragraf competency questions (§2.7)

**1a. Paragraf pembatas klaim** (menjawab "kueri berhasil ≠ graf berkualitas"):

> Evaluasi berbasis competency questions dalam penelitian ini digunakan untuk menilai
> kesesuaian knowledge graph dengan tujuan penelusuran yang telah ditetapkan (fitness for
> purpose). Evaluasi tersebut tidak dimaksudkan untuk mengukur kelengkapan seluruh fakta dalam
> knowledge graph atau membandingkan keseluruhan isi graf dengan gold standard. Penilaian
> dilakukan pada dua tingkat, yaitu keberhasilan operasional kueri dan ketepatan semantis
> jawaban. Keberhasilan operasional menunjukkan bahwa pola penelusuran dapat dijalankan,
> sedangkan ketepatan semantis menunjukkan bahwa hubungan yang dikembalikan oleh kueri didukung
> oleh konteks teks sumber.

**1b. Dasar ketepatan kuantitatif** (rumus validitas semantis; tanpa referensi eksternal baru):

> Selain kelayakan fungsional, ketepatan isi knowledge graph dinilai dari proporsi jawaban kueri
> yang benar-benar didukung teks sumber. Karena tidak tersedia acuan lengkap seluruh relasi yang
> seharusnya ada, ketepatan tersebut diperkirakan dengan memeriksa secara manual setiap jawaban
> yang dikembalikan kueri terhadap sumber, lalu dinyatakan sebagai validitas (kesesuaian) semantis
> dan dihitung dengan Persamaan (2.x):

> **kesesuaian semantis (fungsi ke-i) = (N_valid,i ÷ N_diperiksa,i) × 100%**

> dengan N_valid,i = jumlah hasil fungsi ke-i yang didukung teks sumber, dan N_diperiksa,i =
> jumlah seluruh hasil fungsi ke-i yang diperiksa.

---

## 2. BAB 3 — prosedur pengujian (§3.9.2, hal 67–68)

> Selain memeriksa keterlaksanaan kueri, setiap hasil yang dikembalikan oleh keenam fungsi
> diperiksa kesesuaiannya terhadap teks sumber. Unit pemeriksaan mengikuti bentuk keluaran tiap
> fungsi: pada F1–F4 berupa pasangan entitas dan relasi yang dihasilkan; pada F5 berupa jalur
> Person–Event–Location, yang dinyatakan sesuai hanya apabila **kedua** relasi pada jalur tersebut
> didukung oleh teks sumber; dan pada F6 berupa pasangan Event–PRECEDES–Event. Karena satu lokasi
> pada F5 dapat dicapai melalui beberapa jalur, unit penilaian adalah 21 jalur yang dikembalikan
> kueri (mencakup 15 lokasi unik), bukan 15 lokasi.
>
> Suatu hasil dinyatakan valid apabila potongan evidence atau teks pada halaman sumber secara
> langsung mendukung hubungan yang terbentuk. Hasil dinyatakan tidak valid apabila bukti
> menyangkal hubungan (mis. terdapat negasi), hanya menyebutkan entitas secara berdekatan tanpa
> hubungan semantis, atau merujuk pada peristiwa lain. Jawaban yang hanya benar sebagian
> diperlakukan sebagai tidak valid agar penilaian bersifat ketat dan tidak melebih-lebihkan hasil.
>
> Pemeriksaan dilakukan secara manual oleh penulis dengan merujuk langsung ke teks terjemahan
> Sirah Nabawiyah karya Al-Mubarakfuri, lalu kesesuaian semantis tiap fungsi dihitung dengan
> Persamaan (2.x). Sebagai keterbatasan, pemeriksaan dilakukan oleh satu orang sehingga tidak
> terdapat pengukuran kesepakatan antar-anotator (inter-annotator agreement); konsistensi dijaga
> dengan menerapkan kriteria penilaian yang sama untuk seluruh fungsi.

> (Paragraf keterbatasan satu-anotator ini sekaligus menjawab **Bu Ratih #5**.)

---

## 3. BAB 4 — Tabel 4.28 (revisi) + redaksi setelah tabel (hal 111–114)

**3a.** Ganti Tabel 4.28 dari kolom biner "Sesuai sumber (ya/tidak)" menjadi tabel kuantitatif
(judul juga diperbaiki): lihat **`hasil_validitas_semantis.md`** — kolom Jumlah diperiksa | Valid
| Tidak valid | Kesesuaian semantis | Terlacak. Ringkas: F1 24,14% · F2 20% · F3 75% · F4 0% ·
F5 14,29% · F6 82,35% · total 31,58% (operational & terlacak 100%).

**3b.** Paragraf setelah tabel:

> Hasil pengujian menunjukkan bahwa keberhasilan operasional mencapai 100% karena seluruh enam
> kueri dapat dijalankan dan menghasilkan data. Keterlacakan juga mencapai 100% karena seluruh
> relasi yang diuji memiliki metadata evidence dan halaman. Meskipun demikian, tingkat kesesuaian
> semantis berbeda pada setiap fungsi. Perbedaan tersebut menunjukkan bahwa kemampuan graf
> menjalankan kueri tidak secara otomatis menjamin ketepatan seluruh jawaban yang dihasilkan.

---

## 4. BAB 4 — hubungkan ke keterbatasan (hal 115–117)

Setelah pembahasan keterbatasan (yang sudah lengkap), tambahkan satu kalimat penghubung ke angka:

> Rendahnya tingkat kesesuaian semantis pada beberapa fungsi terutama dipengaruhi oleh pembentukan
> relasi berbasis kedekatan, pengabaian negasi, serta propagasi kesalahan pada penelusuran
> multi-hop.

---

## 5. BAB 5 — Kesimpulan (hal 121) & Saran (hal 122)

**5a. Kesimpulan** — pertahankan kalimat "layak operasional tetapi belum berdiri sendiri",
tambahkan angka:

> Seluruh enam skenario kueri berhasil dijalankan sehingga tingkat keberhasilan operasional
> mencapai 100%, dan seluruh hasil dapat ditelusuri melalui metadata evidence dan halaman. Namun,
> tingkat kesesuaian semantis berbeda pada setiap fungsi, dengan nilai tertinggi 82,35% pada F6
> dan nilai terendah 0% pada F4 (rata-rata 31,58%).

**5b. Saran** — bedakan evaluasi sekarang vs lanjutan, dan jangan paksakan recall:

> Penelitian ini menghitung tingkat kesesuaian jawaban yang dikembalikan kueri (precision jawaban).
> Penelitian selanjutnya dapat menyusun gold standard relasi beranotasi manual untuk menghitung
> precision, recall, dan F1-score seluruh relasi. Recall menyeluruh belum dapat dihitung pada
> penelitian ini karena tidak tersedia daftar lengkap seluruh relasi yang seharusnya ada.

---

## Rujukan

**Tidak ada referensi eksternal baru yang diperlukan.** Validitas semantis di sini adalah
*operasionalisasi* pemeriksaan manual yang sudah dilakukan, bukan metode baru dari luar. Dasar
teori evaluasi berbasis kueri sudah ditopang rujukan competency-questions yang ada di §2.7 dan
semuanya dalam 5 tahun terakhir: Greco 2025; Keet & Khan 2025; Farrugia dkk. 2025; Illueca
Fernández dkk. 2025.

> Catatan: Paulheim (2017) dan Gao dkk. (2019) sempat dipertimbangkan sebagai dasar metode
> pemeriksaan precision atas sampel, tetapi **tidak dipakai** karena berada di luar batas 5 tahun
> terakhir. Bila sewaktu-waktu diperlukan dasar tertulis untuk metode ini, carilah rujukan
> sejenis terbitan 2021 ke atas.
