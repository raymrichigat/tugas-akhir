# Konten PPT Sidang — Genta Putra Prayoga (5025221040) — VERSI TERBARU

> **Cara pakai.** Tiap blok = 1 slide. Teks utama = konten siap-tempel. Bagian **🖼️** = aset visual pendukung. Bagian **🎨 Panduan layout** = petunjuk penempatan konten pada `PPT.pptx` milik Genta.
>
> **Sumber angka:** SEMUA diselaraskan ke **buku terbaru** (`docs/bab4/hasil_pembahasan.md` + `docs/bab5/kesimpulan.md`), yaitu benchmark **done_newest + ground-truth uji terkoreksi** (aug F1 **0,9756**) dan **Knowledge Graph v4** (SNA ber-scope, Q Louvain **0,2831**). Menggantikan `PPT_konten_revisi.md` (arsip, angka grupB lama).
>
> **Augmentasi = mention replacement + parafrase** (bukan mention saja). **POS-tag kini sedikit di ATAS baseline** (narasi UC3 berubah).
>
> **[PERIKSA]** = perlu diisi dari eksekusi Neo4j nyata sebelum sidang (Tabel fungsional + screenshot). Query di `data/result/neo4j/*_bab4.cypher`.

---

# PANDUAN VISUAL — BERDASARKAN PPT MILIK GENTA

> **Acuan utama:** `PPT.pptx` milik Genta. Pertahankan identitasnya: latar putih, judul biru tua, footer biru, aksen kuning, logo ITS/Departemen, dan penomoran slide.
>
> **Pembanding:** `5025221055_PPTAKHIR.pptx` milik teman hanya digunakan untuk mempelajari hierarki informasi, proporsi visual, dan cara menonjolkan temuan. Jangan menyalin susunan, label RQ, warna kategori, atau komposisi slide secara identik.

## Aturan desain umum

- Gunakan rasio **16:9** dan margin kiri-kanan yang konsisten dengan `PPT.pptx`.
- Judul slide tetap di kiri atas. Gunakan judul sebagai **pesan utama**, bukan hanya nama bagian, khususnya pada slide hasil.
- Maksimal **satu visual utama** dan **satu temuan kunci** pada setiap slide.
- Untuk slide hasil, gunakan komposisi **60–65% visual** dan **35–40% interpretasi**.
- Hindari menampilkan tabel lengkap **dan** grafik yang memuat angka sama dalam satu slide (redundan) — pilih salah satu sebagai visual utama. Untuk slide hasil UC, **tabel metrik penuh boleh jadi visual utama** (lihat "Keputusan isi"); yang dipindahkan ke backup adalah rincian *tingkat token* (FP/FN/boundary), bukan metrik utama.
- Hindari grid empat card berulang. Gunakan bidang datar, garis pemisah tipis, alur, atau satu panel visual besar agar tetap berbeda dari PPT pembanding.
- Gunakan warna entitas secara konsisten: **Person = biru**, **Event = jingga**, **Location = hijau**, **Time = ungu**, **Period = abu-abu**.
- Screenshot Neo4j harus dipotong ke subgraf yang relevan. Nama simpul utama wajib terbaca; jangan menampilkan graf penuh sebagai kumpulan titik kecil.
- Istilah Inggris dicetak miring bila berupa istilah, sedangkan nama properti/relasi graf ditulis sebagai kode, misalnya `INVOLVED_IN`.
- Jika durasi presentasi hanya **15–20 menit**, Slide 2 dapat dihapus dan pasangan Slide 13–14, 15–16, serta 17–18 dapat digabung. Detail analisis kesalahan dipindahkan ke backup.

## Pola layout yang digunakan

| Kode | Pola | Penggunaan |
|---|---|---|
| L1 | Judul/klaim di atas; visual besar 60% kiri; interpretasi 40% kanan | Slide hasil eksperimen dan SNA |
| L2 | Diagram alur memenuhi lebar slide; keterangan singkat di bawah | Metode dan pipeline |
| L3 | Contoh konkret 45% kiri; proses/penjelasan 55% kanan | Preprocessing, pelabelan, validasi error |
| L4 | Angka utama pada pita tipis atas; visual utama di tengah; batas interpretasi di bawah | Statistik KG dan pengujian fungsional |

## Pemetaan terhadap `PPT.pptx` yang sekarang

`PPT.pptx` berisi 23 slide dan masih menggunakan sebagian hasil versi lama. Gunakan pemetaan berikut ketika memperbarui file PowerPoint:

| Slide pada `PPT.pptx` | Tindakan |
|---|---|
| 1–11 | Pertahankan template dan struktur visual; perbarui teks mengikuti Slide 1–11 pada dokumen ini |
| 12 — Pengujian dan Evaluasi | Opsional; pertahankan hanya bila waktu presentasi cukup. Jika dihapus, jelaskan tiga uji coba pada transisi menuju hasil |
| 13 | Perbarui menjadi Slide 12 — Anotasi dan Ketidakseimbangan Kelas |
| 14–15 | Perbarui menjadi Slide 13–14 — UC1; hapus angka hasil versi lama |
| 16–17 | Perbarui menjadi Slide 15–16 — UC2; gunakan framing “indikasi misalignment” |
| 18–19 | Perbarui menjadi Slide 17–18 — UC3 dengan hasil POS terbaru |
| 20 | Ganti dengan Slide 19 (Konstruksi KG) + Slide 19b (Tokoh Berpengaruh, sentralitas v4) — dua slide terpisah |
| 21 — Sintesis lama | Ganti menjadi Slide 20 dan/atau 21 — komunitas, validasi artefak, peristiwa, dan lokasi |
| 22 — Kesimpulan lama | Pindahkan setelah slide pengujian fungsional dan perbarui menggunakan Slide 23 |
| 23 — Saran lama | Perbarui menggunakan Slide 24 |
| Belum tersedia | Tambahkan slide pengujian fungsional yang akurat (Slide 22) dan slide penutup (Slide 25) |

### Angka lama yang wajib dihapus dari `PPT.pptx`

- F1 augmentasi **0,9581** → gunakan **0,9756**.
- Hasil POS **0,9439** atau baseline **0,9481** → gunakan POS **0,9547** dan baseline **0,9536**.
- Pernyataan recall POS naik dan precision turun → hasil terbaru adalah **precision naik, recall turun**.
- Sentralitas lama Muhammad, jumlah **15 komunitas**, dan Q **0,3851** → gunakan hasil v4: **8 komunitas**, Q **0,2831**, serta nilai sentralitas pada Slide 19b.
- Statistik data uji lama **258 chunk, 42.558 token, 1.763 entitas** → gunakan **254 chunk, 49.739 token, 1.969 entitas**.
- Kesimpulan “seluruh fungsi berhasil dipenuhi” → ganti dengan keberhasilan operasional dan keterbatasan kesesuaian sumber pada Slide 22.

## Keputusan isi: metrik mana yang tampil di slide utama?

Prinsipnya: **tampilkan tabel metrik LENGKAP untuk semua skenario pembanding langsung di slide utama** (transparansi penuh), dengan **baris pemenang disorot** dan **satu kalimat headline** sebagai pemandu baca. Pola ini mengikuti deck sidang pembimbing yang sama (Bu Dini Adni), yang menampilkan tabel hasil penuh di slide utama tanpa memindahkannya ke backup. Backup hanya untuk **rincian tingkat token** (FP/FN/boundary), trajektori iterasi, dan data pendukung — bukan untuk menyembunyikan metrik utama.

| Uji coba | Di slide utama (tabel penuh) | Di backup |
|---|---|---|
| UC1 — Imbalance | Precision, Recall, F1 mikro, Macro, + F1 per-kelas (Person/Location/Event/Time) untuk **5 skenario** | Rincian error token-level (FP/FN/salah-tipe/boundary) |
| UC2 — Model | Sda., untuk **5 model** | Trajektori F1 base→iter-6 model anomali |
| UC3 — POS | Sda., untuk **Baseline & POS** | Rincian FP/FN + contoh kesalahan |

> **Aturan praktis:** tampilkan seluruh skenario **dan** seluruh metrik utama — dosen ingin melihat dasar perbandingan penuh. Jaga keterbacaan: sorot baris pemenang (aksen kuning), beri headline interpretif, dan **jangan** menggandakan tabel yang sama dua kali dalam satu slide (kesalahan yang terlihat di deck pembanding).

## Keputusan isi: sentralitas tokoh

- **G1** menggunakan Degree, Closeness, dan PageRank serta diurutkan berdasarkan PageRank.
- **G2** menggunakan Betweenness dan memiliki urutan tokoh yang berbeda.
- Karena urutannya berbeda, Betweenness **tidak tepat hanya ditambahkan sebagai kolom** pada tabel G1. Gunakan **dua tabel Top 5 berdampingan**: tabel G1 dan tabel G2.
- Tabel Top 10 lengkap dan ego graph Muhammad–Abu Bakar ditempatkan pada backup.

---

# SEKSI 0 — PEMBUKA

## Slide 1 — Judul
- PENDEKATAN NAMED-ENTITY RECOGNITION DALAM PEMBANGUNAN KNOWLEDGE GRAPH SIRAH NABAWIYAH
- Genta Putra Prayoga — 5025221040
- Dosen Pembimbing: Dini Adni Navastara, S.Kom., M.Sc.
- Dosen Ko-Pembimbing: Ratih Nur Esti Anggraini, S.Kom., M.Sc., Ph.D.

**🎨 Panduan layout — pertahankan layout asli PPT Genta.** Judul menempati sekitar 65% area kiri. Nama, NRP, dan pembimbing ditempatkan di bawah judul dengan hierarki lebih kecil. Area kanan cukup diisi motif graf transparan atau satu ikon knowledge graph; jangan menambah paragraf. Pertahankan aksen garis/pita kuning milik PPT Genta.

## Slide 2 — Outline
- 01 · Latar Belakang
- 02 · Rumusan Masalah
- 03 · Metode
- 04 · Implementasi
- 05 · Hasil dan Pembahasan
- 06 · Kesimpulan dan Saran

**🎨 Panduan layout — opsional.** Jika tetap digunakan, susun enam bagian sebagai daftar vertikal sederhana dengan nomor besar 01–06 di kiri dan satu garis horizontal tipis. Hindari enam card. Jika durasi 15–20 menit, hapus slide ini dan sampaikan alur secara lisan.

---

# SEKSI 1 — LATAR BELAKANG

## Slide 3 — Latar Belakang (Masalah)
> Sirah Nabawiyah kaya informasi tokoh, peristiwa, lokasi, dan waktu, tetapi tersaji sebagai narasi panjang sehingga sulit ditelusuri secara relasional.

- **Informasi tersebar dalam narasi panjang** — tokoh, peristiwa, lokasi, waktu disajikan kronologis dalam teks panjang.
- **Pencarian kata kunci belum cukup** — sulit menjawab pertanyaan relasional: "Siapa yang terlibat?", "Peristiwa apa di lokasi X?".
- **Relasi tidak eksplisit** — keterkaitan antar-entitas tidak tersimpan, perlu penelusuran manual.

> Diperlukan pendekatan yang mampu **menyimpan dan menelusuri hubungan** secara eksplisit.

**🎨 Panduan layout — L3.** Kiri 42%: tampilkan potongan satu paragraf Sirah sebagai contoh narasi panjang dengan empat jenis entitas diberi warna. Kanan 58%: tiga masalah disusun vertikal dengan kata kunci besar—**tersebar**, **tidak relasional**, **relasi implisit**. Letakkan kalimat kebutuhan pada pita kuning tipis di bagian bawah. Ini menggantikan tiga card pada PPT lama.

## Slide 4 — Latar Belakang (Solusi: Knowledge Graph)
> **Knowledge Graph** merepresentasikan hubungan tokoh, peristiwa, lokasi, dan waktu secara eksplisit.

1. **Teks Sirah Nabawiyah** (Bahasa Indonesia) → data.
2. **Ekstraksi Entitas (NER)** berbasis SRL (kerangka peran semantik), semi-supervised (*iterative self-training*).
3. **Entitas utama (4):** Person · Location · Event · Time.
4. **Relasi inti:**
   - `INVOLVED_IN` — **Person → Event** (keterlibatan tokoh)
   - `OCCURRED_AT` — **Event → Location** (lokasi peristiwa)
   - `OCCURRED_ON` — **Event → Time** (waktu peristiwa)
   - `PRECEDES` — **Event → Event** (urutan kronologi)
   - Relasi antar-tokoh — **Person → Person** (`KELUARGA`, `SAHABAT`, `MUSUH`)
5. **Knowledge Graph (Neo4j).**

**🎨 Panduan layout — L2.** Ubah daftar menjadi satu alur mendatar: `Teks Sirah → NER → Person/Event/Location/Time → Relasi → Neo4j`. Gunakan warna konsisten untuk empat entitas. Tampilkan hanya tiga relasi inti pada alur; `PRECEDES` dan relasi antar-tokoh diletakkan sebagai catatan kecil di bawah agar diagram tidak penuh.

---

# SEKSI 2 — RUMUSAN MASALAH

## Slide 5 — Rumusan Masalah
1. Bagaimana **menyiapkan** data teks Sirah Nabawiyah agar menjadi dataset siap pakai?
2. Bagaimana **mengekstraksi entitas** menggunakan NER berbasis SRL dengan *iterative self-training*?
3. Bagaimana **membangun knowledge graph** berbasis entitas Person, Event, Location, Time beserta relasinya di Neo4j?
4. Bagaimana **mengevaluasi** hasil NER (tiga uji coba) serta **menganalisis knowledge graph** (Social Network Analysis + pengujian fungsional)?

**🎨 Panduan layout.** Gunakan daftar 01–04 berjajar vertikal: nomor besar pada kolom kiri sempit, pertanyaan pada kolom kanan. Tebalkan hanya verba utama **menyiapkan**, **mengekstraksi**, **membangun**, dan **mengevaluasi**. Jangan menggunakan susunan empat card seperti PPT pembanding.

---

# SEKSI 3 — METODE

## Slide 6 — Metode Penelitian
1. Preparasi Data
2. Preprocessing & Chunking
3. Pelabelan Data
4. Ekstraksi Entitas
5. Konstruksi Knowledge Graph
6. Pengujian & Evaluasi

**🎨 Panduan layout — L2.** Pertahankan diagram alir milik PPT Genta, tetapi perbesar hingga menempati sekitar dua pertiga slide. Daftar tahap di kiri cukup berupa enam label pendek. Gunakan satu jalur baca yang jelas dari kiri ke kanan; hindari konektor yang berputar atau bersilangan.

---

# SEKSI 4 — IMPLEMENTASI

## Slide 7 — Preparasi Data
> Mengubah buku Sirah (PDF pindaian) menjadi dataset teks terstruktur.

- **~633 halaman** — Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan Kathur Suhardi), Bahasa Indonesia.
- **PaddleOCR** → ekstraksi teks dari pindaian.
- **1 · Ekstraksi dokumen terstruktur** — teks per halaman disusun ulang mengikuti daftar isi; footer berulang dihapus; judul bab/subbab dikenali via *exact* + *fuzzy matching* (0,92) → JSON hierarkis.
- **2 · Konversi ke CSV** — tiap baris = satu subbab (judul_bab, judul_sub_bab, halaman, teks).

**🎨 Panduan layout.** Bagian atas berupa pita angka: **±633 halaman → OCR → JSON → CSV**. Bagian bawah menampilkan dua tahap besar secara mendatar, bukan dua card terpisah. Sisipkan satu contoh kecil struktur `bab → subbab → teks` di sisi kanan agar keluaran JSON mudah dipahami.

## Slide 8 — Preprocessing & Chunking
**Preprocessing** — membersihkan teks OCR:
- Saring baris tak relevan; hapus karakter non-*printable* & simbol non-informatif.
- Normalisasi apostrof/ain Arab (Ka`bah → Ka'bah); perbaiki spasi prefiks (Al- Walid → Al-Walid).
- Bersihkan *gibberish* di tingkat token, segmen, kalimat.

**Chunking** — memecah teks per subbab jadi *chunk* menjaga konteks:
- Gabung kalimat ke *chunk* maks 1.500 karakter (kalimat tak dipotong); overlap 1 kalimat; tiap *chunk* diberi ID + metadata.

**🎨 Panduan layout — L3.** Kiri: contoh **sebelum–sesudah preprocessing** menggunakan dua atau tiga baris teks OCR nyata. Kanan: ilustrasi tiga chunk yang saling tumpang tindih satu kalimat. Detail aturan pembersihan ditempatkan dalam tiga baris pendek di bawah contoh, bukan sebagai daftar panjang.

## Slide 9 — Pelabelan Data
> Membentuk data anotasi sebagai *seed* pelatihan NER sekaligus *ground truth* evaluasi.

1. **Anotasi semi-otomatis** — kandidat entitas via *gazetteer* (kamus) + pola *regex* (PERSON/nasab, EVENT/perang, LOCATION, TIME); dedup prioritas *span* terpanjang.
2. **Koreksi manual** — pra-anotasi ditinjau (tambah terlewat, hapus salah, perbaiki batas), berpedoman 4 label.
3. **Konversi BIO** — anotasi *span* → token-per-baris (Begin-Inside-Outside); dibagi latih/uji (*test size* 0,3).

**🎨 Panduan layout.** Gunakan alur tiga tahap memenuhi lebar slide: **pra-anotasi → koreksi manual → BIO**. Di bawah alur, tampilkan satu contoh kalimat yang sama pada ketiga tahap. Warna label entitas harus konsisten; contoh konkret lebih penting daripada paragraf penjelasan.

## Slide 10 — Ekstraksi Entitas (NER Berbasis SRL + Self-Training)
> NER berbasis IndoBERT dilatih semi-supervised via *iterative self-training* untuk memperluas anotasi dari *seed* ke seluruh korpus.

- **Berbasis SRL (kerangka peran semantik)** — pelaku→Person, tempat→Location, waktu→Time, peristiwa→Event (melalui pola & kamus, **bukan** pengurai predikat–argumen SRL penuh).
- **Iterative self-training** — latih *seed* → prediksi data tak berlabel → prediksi berkeyakinan tinggi jadi *pseudo-label* → latih ulang.
- **Kriteria pseudo-label** — *chunk* diterima bila **rata-rata keyakinan token entitas ≥ 0,9**; diulang sampai konvergen.
- Konfigurasi: **IndoBERT uncased** · *threshold* **0,9** · maks **6 iterasi**.

**🎨 Panduan layout — L1.** Kiri 38%: empat pemetaan peran semantik dan tiga konfigurasi utama. Kanan 62%: siklus besar `latih seed → prediksi unlabelled → seleksi ≥0,9 → pseudo-label → latih ulang`. Gunakan panah membentuk satu loop bersih. Kalimat “bukan pengurai SRL penuh” diletakkan sebagai catatan batas metode di bawah.

## Slide 11 — Konstruksi Knowledge Graph
> Menyusun graf: satukan variasi nama → bentuk relasi → tambah dimensi waktu → muat ke Neo4j.

- **Alias Clustering** — variasi nama → bentuk kanonik (manual + Jaro-Winkler 0,93); ~143 variasi → ~109 klaster.
- **Pembentukan relasi** — dari *co-occurrence*; EVENT sebagai pusat keterhubungan; tiap relasi menyimpan *provenance*.
- **Periodisasi peristiwa** — EVENT dipetakan ke periode (P0–P14); `PRECEDES` untuk kronologi.
- **Pemuatan ke Neo4j** — node (Person/Event/Location/Time/Period) & edge via `MERGE` + *constraint* keunikan.

🖼️ Diagram 4 tahap: `docs/daftar-sidang/slide11_diagram_konstruksi_kg.md`

**🎨 Panduan layout — L2.** Gunakan empat tahap horizontal dengan satu contoh yang berlanjut: variasi nama → nama kanonik → relasi dengan evidence → node/edge Neo4j. Letakkan `143 variasi → 109 klaster` sebagai angka sorotan di tahap pertama. Daftar seluruh tipe relasi cukup menjadi legenda tipis di bagian bawah.

## Slide 11b — Skenario Pengujian (peta Uji Coba → Rumusan Masalah)
> Sisipkan sebagai slide transisi tepat sebelum bagian Hasil (renumber saat ke PowerPoint). Meniru pola "Skenario Pengujian" pada deck pembimbing yang sama — memberi dosen peta jelas *mengapa* tiap uji coba ada sebelum melihat angkanya.

> Evaluasi disusun sebagai **tiga uji coba NER** dan **analisis graf**, seluruhnya menjawab **RM4**, dijalankan pada pipeline dan data uji yang identik agar perbandingan adil.

| Uji coba | Pertanyaan yang dijawab | Pembanding |
|---|---|---|
| **UC1 — Penanganan imbalance** | Teknik apa yang paling menaikkan F1 kelas minoritas? | baseline · weighted-CE · SCL · JSCL · augmentasi |
| **UC2 — Komparasi model** | *Backbone* pra-latih mana yang terbaik? | IndoBERT uncased/cased · Cahya · DistilBERT · RoBERTa |
| **UC3 — Fitur POS** | Apakah menambah fitur POS-tag menaikkan performa? | baseline vs +POS-tag |
| **Analisis graf (G1–G8) + uji fungsional (F1–F6)** | Siapa tokoh/peristiwa sentral, komunitas apa, apakah graf menjawab kueri relasional? | metrik SNA + 6 competency question |

> **RM1** (persiapan data) & **RM3** (konstruksi graf) sudah dijawab pada tahap Implementasi (Slide 7–11); **RM2** = metode ekstraksi itu sendiri (Slide 10). Slide ini memetakan blok **evaluasi (RM4)**.

**🎨 Panduan layout.** Empat baris uji coba di kiri (nomor + nama tebal), kolom "pertanyaan" di tengah, "pembanding" di kanan sebagai pil kecil. Beri satu pita atas: **3 uji coba NER → RM4 · analisis graf → RM4**. Hindari empat card seragam; pakai tabel bergaris tipis.

---

# SEKSI 5 — HASIL DAN PEMBAHASAN

## Slide 12 — Anotasi Data & Ketidakseimbangan Kelas
> Seluruh evaluasi NER memakai data uji yang sama; komposisi kelas sangat timpang → kunci pembacaan semua hasil.

**Statistik dataset** (total korpus 1.094 *chunk*)
| Split | Chunk | Token | Entitas |
|---|---:|---:|---:|
| Train (*seed*) | 590 | 116.353 | 4.247 |
| Test | 254 | 49.739 | 1.969 |
| Unlabelled | 250 | 46.668 | — |

> *Unlabelled* = *chunk* tanpa anotasi manual, jadi kolam *pseudo-labelling* pada *iterative self-training* (entitas belum berlabel).

**Distribusi entitas per kelas**
| Kelas | Train | Test |
|---|---:|---:|
| Person | 2.920 | 1.302 |
| Location | 972 | 474 |
| Time | 188 | 118 |
| Event | 167 | 75 |

> **Temuan:** ketimpangan ekstrem (**±17,5:1**) — Person mendominasi; **Event & Time** kelas minoritas *few-shot*. Inilah dasar Uji Coba 1.

🖼️ `data/result/analysis/bab4_viz/eda_imbalance.png`

**🎨 Panduan layout — L4.** Atas: tiga angka ringkas **590 train · 254 test · 250 unlabelled**. Tengah kiri 65%: grafik distribusi entitas. Kanan 35%: angka besar **17,5 : 1** dan satu interpretasi bahwa Event–Time merupakan kelas minoritas. Tabel statistik lengkap dipindahkan ke backup atau catatan pembicara.

## Slide 13 — Uji Coba 1: HASIL (Penanganan Imbalance)
> *Baseline* vs 4 teknik penanganan minoritas pada pipeline identik. Metrik: F1 *entity-level* (seqeval).

| Skenario | P | R | F1 mikro | Macro | Person | Location | Event | Time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 0,9524 | 0,9548 | 0,9536 | 0,9136 | 0,9690 | 0,9530 | 0,9342 | 0,7983 |
| Weighted CE | 0,9427 | 0,9533 | 0,9480 | 0,9156 | 0,9616 | 0,9432 | 0,9231 | 0,8347 |
| SCL | 0,9543 | 0,9548 | 0,9546 | 0,9236 | 0,9687 | 0,9488 | **0,9600** | 0,8170 |
| JSCL | 0,9415 | 0,9487 | 0,9451 | 0,9062 | 0,9611 | 0,9467 | **0,9600** | 0,7572 |
| **Augmentation** | **0,9756** | **0,9756** | **0,9756** | **0,9543** | **0,9835** | **0,9755** | 0,9542 | **0,9038** |

**🔑 Temuan Kunci:** Augmentation terbaik hampir di semua metrik (F1 mikro **0,9756**, Macro **0,9543**); lonjakan terbesar di **Time** 0,80→**0,90**. *Catatan:* F1 Event tertinggi ada di SCL/JSCL (0,9600), tapi keduanya kalah seimbang secara keseluruhan. Augmentasi = **mention replacement + parafrase**.

🖼️ Opsional: `data/result/analysis/bab4_viz/f1_uc1_perkelas.png` sebagai grafik pendamping.

**🎨 Panduan layout.** Tampilkan **tabel penuh 5 skenario × 8 metrik** sebagai visual utama (dosen ingin lihat dasar perbandingan lengkap). **Sorot baris Augmentation** dengan aksen kuning; beri tanda kecil pada sel Event 0,9600 SCL/JSCL agar kejujuran "bukan menang di semua kelas" terlihat. Di kanan/atas tabel letakkan angka besar **0,9756** + panah **Time 0,7983→0,9038**. Jaga font tabel cukup besar; jangan gandakan tabel.

## Slide 14 — Uji Coba 1: PEMBAHASAN (mengapa + error)
- **Kenapa augmentation menang?** Menambah **ragam contoh** kelas minoritas: teknik *mention replacement* (dominan) + parafrase kalimat yang menjaga entitas. Distribusi entitas naik **4.247 → 6.780** (Event +196%, Time +59%).
- **Kenapa Weighted CE & JSCL di bawah baseline?** Membobot minoritas membuat model **over-deteksi** (FP naik) tanpa menambah informasi baru.
- **Anatomi error:** didominasi **keputusan deteksi** (FP+FN); **salah-tipe hanya 2–6%**. Augmentation = total error terendah (**78 token**). Model **paham 4 tipe**; tantangan = "entitas atau bukan".

> **Simpulan UC1:** menambah ragam contoh kelas minoritas lebih efektif daripada sekadar mengubah pembobotan pada fungsi *loss*.

🖼️ `data/result/analysis/error_viz/by_group/s1_compare.png`

**🎨 Panduan layout — L1.** Kiri: visual error menempati 58–60%. Kanan: urutan sebab-akibat **ragam data bertambah → FN turun → F1 meningkat**. Weighted CE dan JSCL cukup diberi satu catatan peringatan bahwa FP meningkat. Hindari paragraf penuh seperti Slide 15 pada PPT lama.

## Slide 15 — Uji Coba 2: HASIL (Komparasi Model)
> Lima *backbone* pra-latih pada pipeline identik (hanya model yang divariasikan).

| Model | P | R | F1 mikro | Macro | Person | Location | Event | Time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **IndoBERT uncased** | 0,9524 | 0,9548 | **0,9536** | **0,9136** | 0,9690 | 0,9530 | 0,9342 | 0,7983 |
| Cahya uncased | 0,9388 | 0,9187 | 0,9286 | 0,8811 | 0,9493 | 0,9232 | 0,9315 | 0,7203 |
| DistilBERT uncased | 0,9502 | 0,9208 | 0,9353 | 0,8852 | 0,9581 | 0,9232 | 0,9116 | 0,7479 |
| IndoBERT cased ⚠ | 0,7289 | 0,8329 | 0,7774 | 0,6893 | 0,7843 | 0,8717 | 0,5549 | 0,5461 |
| RoBERTa ⚠ | 0,7654 | 0,8532 | 0,8069 | 0,7490 | 0,8135 | 0,8766 | 0,7654 | 0,5404 |

**🔑 Temuan Kunci:** tiga model *uncased* stabil (F1 0,93–0,95), **IndoBERT uncased terbaik**; IndoBERT *cased* & RoBERTa (⚠) anjlok — dan anjloknya **terpusat di Person & Time** (Location tetap ~0,87), petunjuk masalah penyelarasan label, bukan model buruk.

🖼️ Opsional: `data/result/analysis/bab4_viz/f1_uc2_agregat.png` sebagai grafik pendamping.

**🎨 Panduan layout.** Tampilkan **tabel penuh 5 model × 8 metrik**. Beri **garis pemisah** antara tiga model *uncased* stabil dan dua anomali (⚠). Sorot baris IndoBERT uncased. Arahkan mata ke kolom **Person/Event/Time** pada dua baris anomali (di situ jatuhnya) untuk menyiapkan pembahasan Slide 16. Jangan sembunyikan per-kelas — justru per-kelas yang membuktikan ini artefak alignment.

## Slide 16 — Uji Coba 2: PEMBAHASAN (kenapa cased & RoBERTa anjlok?)
**Hasil tidak membuktikan model cased/RoBERTa lebih buruk secara umum.** Pola kesalahan **mengindikasikan masalah penyelarasan label kata-ke-subword** pada pipeline. Tiga bukti:
- **Bukan efek self-training** — F1 dari *base* justru naik tipis (cased 0,7608→0,7770) → defisit **sejak awal**.
- **Terpusat di entitas banyak-kata** (Person & Time); Location (1 kata) tetap tinggi (~0,87).
- **Boundary B/I meledak** ke **138 token** (cased) / **133** (RoBERTa) vs 7–12 uncased; 122/114 di antaranya pada Person.

> ⚠️ **Framing wajib:** rendahnya cased/RoBERTa = **artefak penyelarasan label**, bukan bukti model buruk untuk NER Sirah.

🖼️ `data/result/analysis/error_viz/by_group/s2_confusion.png` (panel "3 rapi vs 2 rusak")

**🎨 Panduan layout.** Gunakan komposisi perbandingan visual: tiga confusion matrix model stabil di sisi kiri dan dua model anomali di sisi kanan, dipisahkan garis vertikal. Di bawahnya tampilkan tiga bukti dalam satu baris pendek. Gunakan kata **indikasi**, bukan **akar masalah**, karena penelitian belum melakukan eksperimen khusus untuk membuktikan penyebab secara kausal.

## Slide 17 — Uji Coba 3: HASIL (Modul POS-tag)
> Model **tanpa** vs **dengan** fitur POS-tag (POS asli via *tagger*, bukan *placeholder*).

| Skenario | P | R | F1 mikro | Macro | Person | Location | Event | Time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 0,9524 | **0,9548** | 0,9536 | 0,9136 | 0,9690 | **0,9530** | **0,9342** | 0,7983 |
| POS-tag | **0,9628** | 0,9467 | **0,9547** | **0,9217** | **0,9693** | 0,9466 | 0,9333 | **0,8376** |

**🔑 Temuan Kunci:** POS-tag **belum menunjukkan perbaikan yang meyakinkan** — F1 mikro 0,9547 ≈ baseline 0,9536 (selisih 0,0011, tanpa multi-*seed*/uji signifikansi). Per-kelas pun **tidak konsisten arahnya**: Time naik (0,80→0,84) tapi Location & Event justru turun → menguatkan bahwa POS *redundan* di atas IndoBERT kontekstual.

🖼️ `data/result/analysis/bab4_viz/f1_uc3_agregat.png`

**🎨 Panduan layout.** Tampilkan **tabel penuh 2 baris × 8 metrik**. Sorot pola pertukaran `precision ↑` `recall ↓`, dan warnai per-kelas yang **naik (Time)** vs **turun (Location/Event)** dengan panah berlawanan — bukti visual "tidak konsisten". Selisih F1 mikro **+0,0011** ditulis kecil; rincian FP/FN 55→40 / 98→106 ke Slide 18. Jangan pakai angka POS versi lama `PPT.pptx`.

## Slide 18 — Uji Coba 3: PEMBAHASAN (mengapa + error)
- **Kenapa POS-tag tak membantu? Redundan.** IndoBERT kontekstual **sudah menyerap** petunjuk kelas kata; POS eksplisit tak menambah sinyal.
- **Pola pertukaran:** precision naik (0,9628) tapi recall turun (0,9467) → model lebih **berhati-hati** menebak (FP turun **55→40**), tetapi lebih banyak entitas terlewat (FN naik **98→106**).
- **FN terbanyak = Location langka** (mis. "Pakistan") yang terlewat.
- **Catatan jujur:** POS **asli** (bukan placeholder) → hasilnya **sah**, bukan artefak fitur palsu.

🖼️ `data/result/analysis/error_viz/by_group/s3_compare.png`

**🎨 Panduan layout — L3.** Kiri: diagram pertukaran **FP 55→40** dan **FN 98→106** menggunakan dua panah berlawanan. Kanan: visual error dan satu contoh Location langka yang terlewat. Kesimpulan “POS redundan” diletakkan sebagai satu baris tegas di bagian bawah, disertai kata **pada konfigurasi yang diuji**.

## Slide 19 — Evaluasi KG: Konstruksi Knowledge Graph
> Informasi yang semula tersebar dalam narasi disatukan menjadi **satu graf terhubung yang dapat ditelusuri** — simpul Event menjadi penghubung antar jenis entitas.

Knowledge graph dibangun dari prediksi NER konfigurasi terbaik (IndoBERT uncased + augmentasi), dimuat ke Neo4j via `MERGE` + *constraint* keunikan; tiap relasi menyimpan *provenance* (evidence + halaman).

**Komposisi simpul (total 1.192) · relasi (total 728)**
| Simpul | Jml | · | Relasi | Jml |
|---|---:|:--:|---|---:|
| Person | 901 | · | KELUARGA | 312 |
| Time | 167 | · | INVOLVED_IN | 229 |
| Location | 74 | · | OCCURRED_ON | 46 |
| Event | 35 | · | OCCURRED_AT | 44 |
| Period | 15 | · | SAHABAT · PRECEDES · MUSUH | 33 · 17 · 12 |
| | | · | IN_PERIOD | 35 |

> Ekstraksi awal **705** catatan relasi → **693 unik** setelah 12 duplikat digabung `MERGE` (bukti ganda tetap disimpan) + **35** IN_PERIOD = **728**.

🖼️ **Gambar 4.16** — subgraf **Perang Badr** (Neo4j): Event menaut tokoh (`INVOLVED_IN`), lokasi (`OCCURRED_AT`), waktu (`OCCURRED_ON`).

**🎨 Panduan layout — L4.** Pita atas: **1.192 simpul · 728 relasi**. Tengah = screenshot subgraf Perang Badr (contoh KG) sebagai visual utama. Bawah = dua tabel komposisi ringkas (simpul kiri, relasi kanan), warna simpul per jenis entitas konsisten. Ini slide **"apa yang dibangun"**, belum analisis.

## Slide 19b — Evaluasi KG: Tokoh Berpengaruh (G1/G2)
> Sisipkan tepat setelah Slide 19 (renumber saat ke PowerPoint). Posisi tiap tokoh diukur dengan empat metrik sentralitas yang menangkap **dimensi berbeda** — Degree (keterhubungan langsung), Closeness (kedekatan ke seluruh jaringan), PageRank (pengaruh berbobot), Betweenness (peran jembatan antar-kelompok).

> Analisis pada **proyeksi jaringan tokoh** (ber-scope peserta peristiwa): **137 node · 1.853 edge · density 0,199**.

**G1 — Tokoh paling sentral (urut PageRank)**
| # | Tokoh | Degree | Closeness | PageRank |
|---:|---|---:|---:|---:|
| 1 | Muhammad | 0,7941 | 0,7906 | 0,0509 |
| 2 | Ali bin Abu Thalib | 0,5735 | 0,6516 | 0,0240 |
| 3 | Abu Jahal | 0,5515 | 0,6516 | 0,0230 |
| 4 | Umar bin Al-Khaththab | 0,5809 | 0,6552 | 0,0223 |
| 5 | Abu Bakar | 0,5441 | 0,6376 | 0,0212 |

**G2 — Tokoh penghubung (urut Betweenness)**
| # | Tokoh | Betweenness |
|---:|---|---:|
| 1 | Muhammad | 0,2808 |
| 2 | Jabir bin Abdullah | 0,0635 |
| 3 | Ummu Kultsum | 0,0548 |
| 4 | Husain bin Ali | 0,0548 |
| 5 | Ali bin Abu Thalib | 0,0441 |

**🔑 Temuan:** keempat metrik **konvergen pada Muhammad** — paling terhubung, paling dekat, paling berpengaruh, sekaligus jembatan utama antar-kelompok. Struktur naratif Sirah berpusat pada satu tokoh. *Catatan jujur:* peringkat Betweenness selain Muhammad perlu dibaca hati-hati (jaringan padat, rata-rata lintasan pendek, sebagian relasi terpengaruh kedekatan penyebutan teks).

🖼️ Ego graph Muhammad vs Abu Bakar → Backup B6 (kontras sentralitas kasat mata).

**🎨 Panduan layout.** Pita atas menampilkan statistik ringkas **137 tokoh · 1.853 edge · density 0,199**. Di bawahnya gunakan dua tabel berdampingan: kiri 62% untuk G1 (Degree–Closeness–PageRank) dan kanan 38% untuk G2 (Betweenness). Sorot baris Muhammad pada kedua tabel. Jangan menambahkan Betweenness sebagai kolom tabel G1 karena tabel G1 diurutkan berdasarkan PageRank dan peringkat Betweenness memiliki susunan tokoh berbeda.

## Slide 20 — Evaluasi KG: Komunitas & Validasi Artefak
Kelayakan graf ditinjau dari dua sisi: apakah **kelompok** yang terbentuk masuk akal secara naratif, dan apakah ada tokoh yang **sentralitasnya semu** akibat cara relasi dibentuk.

- **Struktur masuk akal:** Muhammad dominan **di semua** ukuran (terhubung langsung ke ±108 dari 137 tokoh) → pusat seluruh peristiwa.
- **Komunitas:** Louvain → **8 komunitas**, modularitas **Q = 0,2831** (kelompok masih terlihat namun melembut karena jaringan padat; ARI Louvain–greedy 0,47). Dua terbesar: lingkar Muslim inti (66) & komunitas campuran Quraisy–pejuang (47).
- **Validasi jujur (artefak):** relasi `INVOLVED_IN` dibentuk dari **kedekatan teks**, sehingga sebagian nama melonjak semu. Contoh **Amr bin Umayyah** — tanpa pembobotan sempat **#2 PageRank**, padahal 3 dari 4 relasinya *false positive*; peran nyatanya kurir Nabi. Setelah pembobotan+scoping turun ke **#12**.

> **Simpulan:** peringkat sentralitas **wajib divalidasi balik ke teks**; solusi tuntas = ekstraksi relasi berbasis kata kerja (future work).

🖼️ Sub-graf **satu komunitas** (Neo4j, lingkar Muslim inti) · screenshot **kesalahan graf** (INVOLVED_IN palsu Amr bin Umayyah, Neo4j)

**🎨 Panduan layout — L1.** Kiri 60%: subgraf komunitas terbesar. Kanan atas: **8 komunitas** dan **Q = 0,2831**. Kanan bawah: mini studi kasus Amr bin Umayyah dalam format `sebelum → validasi evidence → setelah filtering`. Gunakan warna merah hanya untuk menandai relasi yang tidak sesuai, bukan sebagai warna kategori utama.

## Slide 21 — Evaluasi KG: Peristiwa, Lokasi & Studi Kasus (G4/G7/G6)
Selain tokoh, sentralitas **peristiwa** dan **lokasi** mengungkap apa yang paling banyak diliput teks — sekaligus memperlihatkan **bias cakupan ekstraksi**, bukan skala historis sebenarnya.

**G4 — Peristiwa paling sentral (PageRank):** Perang Badr (0,0965) · Uhud (0,0889) · Khandaq (0,0674) · Hudaibiyah (0,0442) · Baiat Aqabah Kubra (0,0424). → didominasi peperangan. *Keterbatasan jujur:* peristiwa daur hidup (kelahiran, wahyu, wafat) tak muncul karena disebut lewat frasa kata kerja, tak tertangkap NER.

**G7 — Lokasi paling sentral (weighted degree):** Madinah (661) · Habasyah (561) · Makkah (561) · Syam (530) · Yatsrib (528). → dua pusat fase Sirah (Makkah–Madinah). *Catatan:* "Yatsrib" = nama lama Madinah, belum tergabung alias.

**G6 — Studi kasus 5 peristiwa (tokoh/lokasi/waktu):** Badr 44/9/6 · Uhud 41/3/10 · Hudaibiyah 7/5/4 · Khaibar 7/2/1 · Tabuk 4/0/1. **Muhammad menjadi satu-satunya tokoh yang terhubung dengan kelima peristiwa dalam graf.** Perbedaan ukuran mencerminkan **bias cakupan ekstraksi**, bukan skala historis.

🖼️ `data/result/analysis/v4_hybrid/case_study_panel*.png` (panel 5 sub-graf)

**🎨 Panduan layout.** Bagi slide menjadi dua kolom: kiri untuk lima peristiwa teratas, kanan untuk lima lokasi teratas. Gunakan bar horizontal pendek, bukan tabel. Studi kasus lima peristiwa menjadi pita visual di bagian bawah berupa lima lingkaran berukuran berdasarkan jumlah tokoh. Jika ruang tidak cukup, pindahkan G6 ke backup; jangan mengecilkan label hingga tidak terbaca.

## Slide 22 — Evaluasi KG: Operasional Berhasil, Ketepatan Semantis Terbatas
> Enam fungsi F1–F6 diuji menggunakan empat kriteria: kueri dapat dieksekusi, hasil tidak kosong, seluruh hasil sesuai teks sumber, dan jawaban dapat ditelusuri melalui *provenance*.

| Kriteria | Hasil |
|---|:---:|
| Kueri berhasil dieksekusi | **6/6 ✓** |
| Hasil tidak kosong | **6/6 ✓** |
| Jawaban dapat ditelusuri ke sumber | **6/6 ✓** |
| Seluruh hasil sesuai konteks sumber | **0/6 ✕** |

> **Makna 0/6:** bukan berarti seluruh jawaban salah. Setiap fungsi masih memiliki setidaknya satu hasil yang tidak didukung konteks sumber.

**Contoh:** relasi Abu Lahab–Perang Badr terbentuk sebagai `INVOLVED_IN`, padahal *evidence* menyatakan bahwa Abu Lahab tidak ikut serta.

> **Simpulan:** graf layak secara operasional untuk penelusuran awal, tetapi belum dapat menjadi sumber jawaban mandiri tanpa verifikasi terhadap teks Sirah.

🖼️ Screenshot hasil kueri F1 dan potongan *evidence* Abu Lahab. **[PERIKSA]** gunakan hasil eksekusi nyata dari `functional_test_queries_bab4.cypher`.

**🎨 Panduan layout — L4.** Bagian atas menampilkan empat kriteria sebagai satu baris angka besar: **6/6 · 6/6 · 6/6 · 0/6**. Bagian bawah menggunakan komposisi 55/45: screenshot kueri F1 di kiri dan contoh kontradiksi Abu Lahab di kanan. Gunakan hijau untuk tiga kriteria operasional dan jingga/merah untuk kesesuaian sumber. Daftar F1–F6 dipindahkan ke Backup B5.

---

# SEKSI 6 — KESIMPULAN & SARAN

## Slide 23 — Kesimpulan
- **RM1 — Persiapan data:** OCR → preprocessing → chunking → pelabelan BIO + alias clustering. Data uji **254 chunk, 49.739 token, 1.969 entitas**; Event (75) & Time (118) minoritas tajam.
- **RM2 — Ekstraksi entitas:** NER IndoBERT + *iterative self-training*; terbaik **uncased + augmentation (mention replacement + parafrase)** → F1 mikro **0,9756**. Minoritas terangkat: Time 0,80→0,90, Event 0,93→0,95.
- **RM3 — Konstruksi graf:** KG di Neo4j (4 entitas + relasi inti + antar-tokoh + `PRECEDES`); tiap relasi menyimpan *provenance*.
- **RM4 — Evaluasi & analisis:** enam kueri berhasil dijalankan, tidak kosong, dan terlacak, tetapi setiap fungsi masih memuat setidaknya satu hasil yang tidak didukung konteks sumber. SNA (137 node, 1.853 edge, density 0,199) menunjukkan Muhammad dominan dan terbentuk **8 komunitas** (Q **0,2831**). Graf layak untuk eksplorasi awal, bukan sebagai sumber jawaban mandiri.

**🎨 Panduan layout.** Gunakan empat baris RM1–RM4, bukan empat card. Setiap baris terdiri atas nomor berwarna, satu kalimat hasil, dan satu angka utama di sisi kanan. RM4 dibuat sedikit lebih tinggi karena memuat keberhasilan operasional sekaligus keterbatasan semantis.

## Slide 24 — Saran
1. **Ekstraksi relasi berbasis kata kerja** — ganti/lengkapi `INVOLVED_IN` berbasis kedekatan (rawan over/under-extraction) dengan predikat tindakan, agar artefak seperti "Amr bin Umayyah" berkurang.
2. **Deteksi Event dari konstruksi verbal** — banyak peristiwa (kelahiran, wahyu pertama, wafat) muncul sebagai frasa deskriptif; kembangkan agar tak lagi ditambah manual.
3. **Perbaiki penyelarasan label & uji ulang** — perbaiki fungsi *word-to-subword* agar perbandingan cased/RoBERTa adil; perketat pemeriksaan *ground truth*.
4. **Perkuat alias & perluas cakupan** — satukan alias lokasi (Yatsrib–Madinah); uji pada sumber Sirah lain; kembangkan pemanfaatan graf (tanya-jawab / visualisasi).

**🎨 Panduan layout.** Susun empat saran sebagai urutan prioritas vertikal dengan garis penghubung: **relasi → event verbal → alignment → alias/cakupan**. Beri nomor besar 01–04 dan maksimal dua baris per saran. Hindari empat card berukuran sama.

## Slide 25 — Penutup
> **Knowledge graph membantu menemukan hubungan dalam Sirah, tetapi setiap jawaban tetap perlu diverifikasi ke teks sumber.**

Terima kasih — untuk setiap koreksi, pertanyaan, dan masukan sepanjang proses ini.

**🎨 Panduan layout.** Letakkan pesan utama di tengah sebagai satu kalimat besar, kemudian “Terima kasih” dan identitas singkat di bawah. Gunakan motif node-edge tipis sebagai dekorasi. Jangan meniru ikon mengambang atau komposisi penutup PPT teman.

---

# SEKSI 7 — SLIDE BACKUP (buka bila ditanya)

## Backup B1 — Anatomi Error Token-level (semua skenario UC1)
> Kesalahan didominasi keputusan **deteksi**, bukan salah-tipe.

| Skenario | Total error | FP (over) | FN (terlewat) | Salah tipe | Boundary B/I |
|---|---:|---:|---:|---:|---:|
| Baseline | 165 | 55 (33%) | 98 (59%) | 5 (3%) | 7 (4%) |
| Weighted CE | 174 | 69 (40%) | 84 (48%) | 11 (6%) | 10 (6%) |
| SCL | 178 | 62 (35%) | 102 (57%) | 7 (4%) | 7 (4%) |
| JSCL | 185 | 69 (37%) | 93 (50%) | 12 (6%) | 11 (6%) |
| **Augmentation** | **78** | 25 (32%) | 41 (53%) | **4 (5%)** | 8 (10%) |

> Salah-tipe kecil → model **paham 4 tipe**; tantangan = "entitas atau bukan".

## Backup B2 — Tiga Akar Error (contoh token nyata, gold terkoreksi)
- **Over-deteksi (FP):** honorifik/gelar keliru ditandai Person.
- **Terlewat (FN):** nama langka + artefak OCR (tanda baca menempel), mis. "Cina", "Pakistan".
- **Salah tipe:** nama ganda tempat/peristiwa (Hudaibiyah: Location vs Event).
- **Boundary B/I:** rentang waktu banyak-kata terpecah; tipe (*Time*) tetap benar.

## Backup B3 — Kenapa cased & RoBERTa anjlok (bukan model jelek)
- **Trajektori F1 dari base naik tipis** → defisit sejak awal, bukan efek self-training:

| Model | F1 base | iter-2 | iter-4 | iter-6 |
|---|---:|---:|---:|---:|
| IndoBERT cased | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |

- **Boundary B/I meledak** ke **138** (cased) / **133** (RoBERTa) token, 122/114 pada Person banyak-kata.
> Kesimpulan: hasil **mengindikasikan misalignment label kata-ke-subword** pada tokenizer cased/BPE; hasil tersebut tidak membuktikan kelemahan model secara umum.

## Backup B4 — Before/After Augmentasi (data latih)
| Label (token) | Sebelum | Sesudah | Perubahan |
|---|---:|---:|---:|
| O | 108.815 | 163.352 | +50% |
| Person (B+I) | 5.519 | 8.311 | +51% |
| Location (B+I) | 1.038 | 1.875 | +81% |
| Time (B+I) | 664 | 1.107 | +67% |
| Event (B+I) | 317 | 943 | **+198%** |

> Augmentasi menambah **semua kelas** (bukan mengurangi O); Event tumbuh paling tajam. Entitas: 4.247 → 6.780.

## Backup B5 — Enam Competency Questions Pengujian Fungsional

| Fungsi | Kebutuhan Fungsional | Contoh kueri | Jumlah hasil |
|---|---|---|---:|
| F1 | Tokoh yang terhubung dengan peristiwa | Siapa yang terlibat Perang Badr? | 58 tokoh |
| F2 | Peristiwa berdasarkan lokasi | Peristiwa apa yang terjadi di Madinah? | 10 peristiwa |
| F3 | Peristiwa berdasarkan waktu | Peristiwa apa yang terjadi pada tahun 2 H? | 4 peristiwa |
| F4 | Peristiwa berdasarkan tokoh | Peristiwa apa yang melibatkan Abu Bakar? | 4 peristiwa |
| F5 | Penelusuran lintas entitas | Di mana lokasi peristiwa yang melibatkan Umar? | 15 lokasi unik |
| F6 | Urutan kronologis | Pasangan peristiwa apa yang terhubung `PRECEDES`? | 17 relasi |

> Semua kueri berhasil dieksekusi, tidak kosong, dan terlacak. Akan tetapi, setiap fungsi memiliki minimal satu hasil yang tidak didukung konteks sumber sehingga kesesuaian penuh adalah 0/6.

**🎨 Panduan layout backup.** Gunakan tabel penuh karena slide ini hanya dibuka ketika dosen meminta rincian F1–F6. Sorot kolom jumlah hasil dan tambahkan legenda kecil untuk empat kriteria pengujian.

## Backup B6 — Sentralitas Tokoh Lengkap

**G1 — Sepuluh tokoh berdasarkan PageRank**

| # | Tokoh | Degree | Closeness | PageRank |
|---:|---|---:|---:|---:|
| 1 | Muhammad | 0,7941 | 0,7906 | 0,0509 |
| 2 | Ali bin Abu Thalib | 0,5735 | 0,6516 | 0,0240 |
| 3 | Abu Jahal | 0,5515 | 0,6516 | 0,0230 |
| 4 | Umar bin Al-Khaththab | 0,5809 | 0,6552 | 0,0223 |
| 5 | Abu Bakar | 0,5441 | 0,6376 | 0,0212 |
| 6 | Abu Sufyan bin Harb | 0,5368 | 0,6376 | 0,0193 |
| 7 | Aisyah | 0,5221 | 0,6275 | 0,0186 |
| 8 | Abu Azzah | 0,5147 | 0,6242 | 0,0161 |
| 9 | Khunais bin Hudzafah | 0,5147 | 0,6242 | 0,0161 |
| 10 | Utsman bin Affan | 0,5221 | 0,6308 | 0,0158 |

**G2 — Sepuluh tokoh berdasarkan Betweenness**

| # | Tokoh | Betweenness |
|---:|---|---:|
| 1 | Muhammad | 0,2808 |
| 2 | Jabir bin Abdullah | 0,0635 |
| 3 | Ummu Kultsum | 0,0548 |
| 4 | Husain bin Ali | 0,0548 |
| 5 | Ali bin Abu Thalib | 0,0441 |
| 6 | Abdullah bin Ubay bin Salul | 0,0393 |
| 7 | Al-Barra' bin Azib | 0,0380 |
| 8 | Ibnu Hajar | 0,0380 |
| 9 | Salamah bin Al-Akwa' | 0,0373 |
| 10 | Abu Bakar | 0,0294 |

🖼️ Jaringan ego Muhammad dan Abu Bakar sebagai pendukung visual.

> **Catatan interpretasi:** Betweenness tokoh selain Muhammad perlu dibaca hati-hati karena jaringan padat, rata-rata lintasan hanya 1,96, dan sebagian relasi masih dipengaruhi kedekatan penyebutan dalam teks.

**🎨 Panduan layout backup.** Jika kedua tabel tidak terbaca dalam satu slide, pecah menjadi B6a (G1) dan B6b (G2 + ego graph). Backup boleh lebih rinci daripada slide utama.

## Backup B7 — Metrik Lengkap Uji Coba (catatan)

Tabel metrik lengkap UC1/UC2/UC3 (Precision, Recall, F1 mikro, Macro, + F1 per-kelas) **kini sudah tampil penuh di slide utama** (Slide 13, 15, 17) mengikuti pola transparansi deck pembimbing. Backup ini tidak lagi menampilkan tabel duplikat; yang tersisa di backup hanya **rincian tingkat token** (B1 anatomi error, B2 tiga akar error, B3 trajektori model anomali, B4 before/after augmentasi).

---

# Lampiran — [PERIKSA] sebelum cetak
1. **Uji fungsional (Slide 22):** isi jumlah hasil tiap kueri dari eksekusi nyata `functional_test_queries_bab4.cypher` di Neo4j (setelah `import_sirah_v4_hybrid.cypher`).
2. **Gambar/visual:** siapkan screenshot Neo4j (Contoh KG, ego Muhammad, perbandingan ego Muhammad vs Abu Bakar, komunitas sub-graf, kesalahan graf Amr, hasil kueri F1) — query di `data/result/neo4j/sna_evidence_queries_bab4.cypher` + komentar `[SISIPKAN GAMBAR]` di buku Bab 4.
3. **Konsistensi:** angka slide sudah = buku terbaru (done_newest + gold terkoreksi + KG v4). Jangan campur dengan deck lama (`PPT_konten_revisi.md`, grupB).
