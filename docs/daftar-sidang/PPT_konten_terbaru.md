# Konten PPT Sidang — Genta Putra Prayoga (5025221040) — VERSI TERBARU

> **Cara pakai.** Tiap blok = 1 slide. Bagian **Konten** = teks siap-tempel ke desain slide. Bagian **🖼️** = aset visual pendukung.
>
> **Sumber angka:** SEMUA diselaraskan ke **buku terbaru** (`docs/bab4/hasil_pembahasan.md` + `docs/bab5/kesimpulan.md`), yaitu benchmark **done_newest + ground-truth uji terkoreksi** (aug F1 **0,9756**) dan **Knowledge Graph v4** (SNA ber-scope, Q Louvain **0,2831**). Menggantikan `PPT_konten_revisi.md` (arsip, angka grupB lama).
>
> **Augmentasi = mention replacement + parafrase** (bukan mention saja). **POS-tag kini sedikit di ATAS baseline** (narasi UC3 berubah).
>
> **[PERIKSA]** = perlu diisi dari eksekusi Neo4j nyata sebelum sidang (Tabel fungsional + screenshot). Query di `data/result/neo4j/*_bab4.cypher`.

---

# SEKSI 0 — PEMBUKA

## Slide 1 — Judul
- PENDEKATAN NAMED-ENTITY RECOGNITION DALAM PEMBANGUNAN KNOWLEDGE GRAPH SIRAH NABAWIYAH
- Genta Putra Prayoga — 5025221040
- Dosen Pembimbing: Dini Adni Navastara, S.Kom., M.Sc.
- Dosen Ko-Pembimbing: Ratih Nur Esti Anggraini, S.Kom., M.Sc., Ph.D.

## Slide 2 — Outline
- 01 · Latar Belakang
- 02 · Rumusan Masalah
- 03 · Metode
- 04 · Implementasi
- 05 · Hasil dan Pembahasan
- 06 · Kesimpulan dan Saran

---

# SEKSI 1 — LATAR BELAKANG

## Slide 3 — Latar Belakang (Masalah)
> Sirah Nabawiyah kaya informasi tokoh, peristiwa, lokasi, dan waktu, tetapi tersaji sebagai narasi panjang sehingga sulit ditelusuri secara relasional.

- **Informasi tersebar dalam narasi panjang** — tokoh, peristiwa, lokasi, waktu disajikan kronologis dalam teks panjang.
- **Pencarian kata kunci belum cukup** — sulit menjawab pertanyaan relasional: "Siapa yang terlibat?", "Peristiwa apa di lokasi X?".
- **Relasi tidak eksplisit** — keterkaitan antar-entitas tidak tersimpan, perlu penelusuran manual.

> Diperlukan pendekatan yang mampu **menyimpan dan menelusuri hubungan** secara eksplisit.

## Slide 4 — Latar Belakang (Solusi: Knowledge Graph)
> **Knowledge Graph** merepresentasikan hubungan tokoh, peristiwa, lokasi, dan waktu secara eksplisit.

1. **Teks Sirah Nabawiyah** (Bahasa Indonesia) → data.
2. **Ekstraksi Entitas (NER)** berbasis SRL, semi-supervised (*iterative self-training*).
3. **Entitas utama (4):** Person · Location · Event · Time.
4. **Relasi inti:**
   - `INVOLVED_IN` — **Person → Event** (keterlibatan tokoh)
   - `OCCURRED_AT` — **Event → Location** (lokasi peristiwa)
   - `OCCURRED_ON` — **Event → Time** (waktu peristiwa)
   - `PRECEDES` — **Event → Event** (urutan kronologi)
   - Relasi antar-tokoh — **Person → Person** (`KELUARGA`, `SAHABAT`, `MUSUH`)
5. **Knowledge Graph (Neo4j).**

---

# SEKSI 2 — RUMUSAN MASALAH

## Slide 5 — Rumusan Masalah
1. Bagaimana **menyiapkan** data teks Sirah Nabawiyah agar menjadi dataset siap pakai?
2. Bagaimana **mengekstraksi entitas** menggunakan NER berbasis SRL dengan *iterative self-training*?
3. Bagaimana **membangun knowledge graph** berbasis entitas Person, Event, Location, Time beserta relasinya di Neo4j?
4. Bagaimana **mengevaluasi** hasil NER (tiga uji coba) serta **menganalisis knowledge graph** (Social Network Analysis + pengujian fungsional)?

---

# SEKSI 3 — METODE

## Slide 6 — Metode Penelitian
1. Preparasi Data
2. Preprocessing & Chunking
3. Pelabelan Data
4. Ekstraksi Entitas
5. Konstruksi Knowledge Graph
6. Pengujian & Evaluasi

---

# SEKSI 4 — IMPLEMENTASI

## Slide 7 — Preparasi Data
> Mengubah buku Sirah (PDF pindaian) menjadi dataset teks terstruktur.

- **~633 halaman** — Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan Kathur Suhardi), Bahasa Indonesia.
- **PaddleOCR** → ekstraksi teks dari pindaian.
- **1 · Ekstraksi dokumen terstruktur** — teks per halaman disusun ulang mengikuti daftar isi; footer berulang dihapus; judul bab/subbab dikenali via *exact* + *fuzzy matching* (0,92) → JSON hierarkis.
- **2 · Konversi ke CSV** — tiap baris = satu subbab (judul_bab, judul_sub_bab, halaman, teks).

## Slide 8 — Preprocessing & Chunking
**Preprocessing** — membersihkan teks OCR:
- Saring baris tak relevan; hapus karakter non-*printable* & simbol non-informatif.
- Normalisasi apostrof/ain Arab (Ka`bah → Ka'bah); perbaiki spasi prefiks (Al- Walid → Al-Walid).
- Bersihkan *gibberish* di tingkat token, segmen, kalimat.

**Chunking** — memecah teks per subbab jadi *chunk* menjaga konteks:
- Gabung kalimat ke *chunk* maks 1.500 karakter (kalimat tak dipotong); overlap 1 kalimat; tiap *chunk* diberi ID + metadata.

## Slide 9 — Pelabelan Data
> Membentuk data anotasi sebagai *seed* pelatihan NER sekaligus *ground truth* evaluasi.

1. **Anotasi semi-otomatis** — kandidat entitas via *gazetteer* (kamus) + pola *regex* (PERSON/nasab, EVENT/perang, LOCATION, TIME); dedup prioritas *span* terpanjang.
2. **Koreksi manual** — pra-anotasi ditinjau (tambah terlewat, hapus salah, perbaiki batas), berpedoman 4 label.
3. **Konversi BIO** — anotasi *span* → token-per-baris (Begin-Inside-Outside); dibagi latih/uji (*test size* 0,3).

## Slide 10 — Ekstraksi Entitas (SRL-NER + Self-Training)
> NER berbasis IndoBERT dilatih semi-supervised via *iterative self-training* untuk memperluas anotasi dari *seed* ke seluruh korpus.

- **Berbasis SRL** — orientasi peran: pelaku→Person, tempat→Location, waktu→Time, peristiwa→Event (via pola & kamus, **bukan** parsing penuh).
- **Iterative self-training** — latih *seed* → prediksi data tak berlabel → prediksi berkeyakinan tinggi jadi *pseudo-label* → latih ulang.
- **Kriteria pseudo-label** — *chunk* diterima bila **rata-rata keyakinan token entitas ≥ 0,9**; diulang sampai konvergen.
- Konfigurasi: **IndoBERT uncased** · *threshold* **0,9** · maks **6 iterasi**.

## Slide 11 — Konstruksi Knowledge Graph
> Menyusun graf: satukan variasi nama → bentuk relasi → tambah dimensi waktu → muat ke Neo4j.

- **Alias Clustering** — variasi nama → bentuk kanonik (manual + Jaro-Winkler 0,93); ~143 variasi → ~109 klaster.
- **Pembentukan relasi** — dari *co-occurrence*; EVENT sebagai pusat keterhubungan; tiap relasi menyimpan *provenance*.
- **Periodisasi peristiwa** — EVENT dipetakan ke periode (P0–P14); `PRECEDES` untuk kronologi.
- **Pemuatan ke Neo4j** — node (Person/Event/Location/Time/Period) & edge via `MERGE` + *constraint* keunikan.

🖼️ Diagram 4 tahap: `docs/daftar-sidang/slide11_diagram_konstruksi_kg.md`

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

## Slide 13 — Uji Coba 1: HASIL (Penanganan Imbalance)
> *Baseline* vs 4 teknik penanganan minoritas pada pipeline identik. Metrik: F1 *entity-level* (seqeval).

| Skenario | F1 mikro | Macro F1 | F1 Event | F1 Time |
|---|---:|---:|---:|---:|
| Baseline | 0,9536 | 0,9136 | 0,9342 | 0,7983 |
| Weighted CE | 0,9480 | 0,9156 | 0,9231 | 0,8347 |
| SCL | 0,9546 | 0,9236 | 0,9600 | 0,8170 |
| JSCL | 0,9451 | 0,9062 | 0,9600 | 0,7572 |
| **Augmentation** | **0,9756** | **0,9543** | **0,9542** | **0,9038** |

**🔑 Temuan Kunci:** Augmentation terbaik (F1 mikro **0,9756**); lonjakan terbesar di **Time** 0,80→**0,90**. Augmentasi = **mention replacement + parafrase**.

🖼️ `data/result/analysis/bab4_viz/f1_uc1_perkelas.png`

## Slide 14 — Uji Coba 1: PEMBAHASAN (mengapa + error)
- **Kenapa augmentation menang?** Menambah **ragam contoh** kelas minoritas: teknik *mention replacement* (dominan) + parafrase kalimat yang menjaga entitas. Distribusi entitas naik **4.247 → 6.780** (Event +196%, Time +59%).
- **Kenapa Weighted CE & JSCL di bawah baseline?** Membobot minoritas membuat model **over-deteksi** (FP naik) tanpa menambah informasi baru.
- **Anatomi error:** didominasi **keputusan deteksi** (FP+FN); **salah-tipe hanya 2–6%**. Augmentation = total error terendah (**78 token**). Model **paham 4 tipe**; tantangan = "entitas atau bukan".

> **Simpulan UC1:** menambah contoh minoritas (*oversampling*) mengalahkan sekadar menggeser perhatian model (*weighted CE*).

🖼️ `data/result/analysis/error_viz/by_group/s1_compare.png`

## Slide 15 — Uji Coba 2: HASIL (Komparasi Model)
> Lima *backbone* pra-latih pada pipeline identik (hanya model yang divariasikan).

| Model (backbone) | F1 mikro | Macro F1 | Kelompok |
|---|---:|---:|:--|
| **IndoBERT uncased** (baseline) | **0,9536** | 0,9136 | stabil |
| cahya bert-indonesian | 0,9286 | 0,8811 | stabil |
| DistilBERT Indonesia | 0,9353 | 0,8852 | stabil |
| IndoBERT cased | 0,7774 | 0,6893 | **anomali** |
| RoBERTa Indonesia | 0,8069 | 0,7490 | **anomali** |

**🔑 Temuan Kunci:** tiga model *uncased* stabil (0,93–0,95), **IndoBERT uncased terbaik**; IndoBERT *cased* & RoBERTa anjlok (0,78–0,81).

🖼️ `data/result/analysis/bab4_viz/f1_uc2_agregat.png`

## Slide 16 — Uji Coba 2: PEMBAHASAN (kenapa cased & RoBERTa anjlok?)
**BUKAN karena model jelek** — akar masalah = **misalignment label kata-ke-subword** (pipeline disetel untuk tokenizer *uncased*). Tiga bukti:
- **Bukan efek self-training** — F1 dari *base* justru naik tipis (cased 0,7608→0,7770) → defisit **sejak awal**.
- **Terpusat di entitas banyak-kata** (Person & Time); Location (1 kata) tetap tinggi (~0,87).
- **Boundary B/I meledak** ke **138 token** (cased) / **133** (RoBERTa) vs 7–12 uncased; 122/114 di antaranya pada Person.

> ⚠️ **Framing wajib:** rendahnya cased/RoBERTa = **artefak penyelarasan label**, bukan bukti model buruk untuk NER Sirah.

🖼️ `data/result/analysis/error_viz/by_group/s2_confusion.png` (panel "3 rapi vs 2 rusak")

## Slide 17 — Uji Coba 3: HASIL (Modul POS-tag)
> Model **tanpa** vs **dengan** fitur POS-tag (POS asli via *tagger*, bukan *placeholder*).

| Skenario | Precision | Recall | F1 mikro | Error token |
|---|---:|---:|---:|---:|
| Baseline | 0,9524 | 0,9548 | 0,9536 | 165 |
| POS-tag | 0,9628 | 0,9467 | **0,9547** | 164 |

**🔑 Temuan Kunci:** POS-tag **tidak memberi perbaikan bersih** — F1 mikro 0,9547 ≈ baseline 0,9536 (selisih 0,0011, di dalam variansi antar-*run*).

🖼️ `data/result/analysis/bab4_viz/f1_uc3_agregat.png`

## Slide 18 — Uji Coba 3: PEMBAHASAN (mengapa + error)
- **Kenapa POS-tag tak membantu? Redundan.** IndoBERT kontekstual **sudah menyerap** petunjuk kelas kata; POS eksplisit tak menambah sinyal.
- **Pola pertukaran:** precision naik (0,9628) tapi recall turun (0,9467) → model lebih **berhati-hati** menebak (FP turun **55→40**), tetapi lebih banyak entitas terlewat (FN naik **98→106**).
- **FN terbanyak = Location langka** (mis. "Pakistan") yang terlewat.
- **Catatan jujur:** POS **asli** (bukan placeholder) → hasilnya **sah**, bukan artefak fitur palsu.

🖼️ `data/result/analysis/error_viz/by_group/s3_compare.png`

## Slide 19 — Evaluasi KG: Konstruksi & Tokoh Berpengaruh (G1/G2)
Konstruksi KG menyatukan empat jenis entitas (tokoh, peristiwa, lokasi, waktu) beserta periodisasi ke dalam satu kerangka; posisi tiap tokoh lalu diukur dengan beberapa metrik sentralitas yang masing-masing menangkap **dimensi berbeda** — Degree (keterhubungan langsung), Closeness (kedekatan ke seluruh jaringan), PageRank (pengaruh berbobot), dan Betweenness (peran jembatan antar-kelompok).

> **KG utuh:** **1.192 node** (901 Person · 167 Time · 74 Location · 35 Event · 15 Period); **728 relasi** (693 antar-entitas unik + 35 IN_PERIOD; 705 catatan awal, 12 duplikat digabung `MERGE`). Proyeksi jaringan tokoh (ber-scope peserta peristiwa): **137 node · 1.853 edge · density 0,199**.

**G1 — Tokoh paling sentral (urut PageRank)**
| # | Tokoh | Degree | Closeness | PageRank |
|---:|---|---:|---:|---:|
| 1 | Muhammad | 0,7941 | 0,7906 | 0,0509 |
| 2 | Ali bin Abu Thalib | 0,5735 | 0,6516 | 0,0240 |
| 3 | Abu Jahal | 0,5515 | 0,6516 | 0,0230 |
| 4 | Umar bin Al-Khaththab | 0,5809 | 0,6552 | 0,0223 |
| 5 | Abu Bakar | 0,5441 | 0,6376 | 0,0212 |

**G2 — Jembatan (Betweenness):** Muhammad (0,2808) ≫ Jabir bin Abdullah (0,0635) · Ali (0,0441) · Abu Bakar (0,0294).

**Temuan:** berbeda dari jejaring yang pengaruhnya tersebar (mis. jaringan kolaborasi peneliti, di mana tokoh paling produktif belum tentu paling sentral), di sini keempat metrik **konvergen pada Muhammad** — beliau sekaligus paling terhubung, paling dekat, paling berpengaruh, dan jembatan utama antar-kelompok. Ini menegaskan struktur naratif Sirah yang berpusat pada satu tokoh.

🖼️ Perbandingan ego **Muhammad vs Abu Bakar** (Neo4j; sentralitas kasat mata) · ego Muhammad (Neo4j)

## Slide 20 — Evaluasi KG: Komunitas & Validasi Artefak
Kelayakan graf ditinjau dari dua sisi: apakah **kelompok** yang terbentuk masuk akal secara naratif, dan apakah ada tokoh yang **sentralitasnya semu** akibat cara relasi dibentuk.

- **Struktur masuk akal:** Muhammad dominan **di semua** ukuran (terhubung langsung ke ±108 dari 137 tokoh) → pusat seluruh peristiwa.
- **Komunitas:** Louvain → **8 komunitas**, modularitas **Q = 0,2831** (kelompok masih terlihat namun melembut karena jaringan padat; ARI Louvain–greedy 0,47). Dua terbesar: lingkar Muslim inti (66) & komunitas campuran Quraisy–pejuang (47).
- **Validasi jujur (artefak):** relasi `INVOLVED_IN` dibentuk dari **kedekatan teks**, sehingga sebagian nama melonjak semu. Contoh **Amr bin Umayyah** — tanpa pembobotan sempat **#2 PageRank**, padahal 3 dari 4 relasinya *false positive*; peran nyatanya kurir Nabi. Setelah pembobotan+scoping turun ke **#12**.

> **Simpulan:** peringkat sentralitas **wajib divalidasi balik ke teks**; solusi tuntas = ekstraksi relasi berbasis kata kerja (future work).

🖼️ Sub-graf **satu komunitas** (Neo4j, lingkar Muslim inti) · screenshot **kesalahan graf** (INVOLVED_IN palsu Amr bin Umayyah, Neo4j)

## Slide 21 — Evaluasi KG: Peristiwa, Lokasi & Studi Kasus (G4/G7/G6)
Selain tokoh, sentralitas **peristiwa** dan **lokasi** mengungkap apa yang paling banyak diliput teks — sekaligus memperlihatkan **bias cakupan ekstraksi**, bukan skala historis sebenarnya.

**G4 — Peristiwa paling sentral (PageRank):** Perang Badr (0,0965) · Uhud (0,0889) · Khandaq (0,0674) · Hudaibiyah (0,0442) · Baiat Aqabah Kubra (0,0424). → didominasi peperangan. *Keterbatasan jujur:* peristiwa daur hidup (kelahiran, wahyu, wafat) tak muncul karena disebut lewat frasa kata kerja, tak tertangkap NER.

**G7 — Lokasi paling sentral (weighted degree):** Madinah (661) · Habasyah (561) · Makkah (561) · Syam (530) · Yatsrib (528). → dua pusat fase Sirah (Makkah–Madinah). *Catatan:* "Yatsrib" = nama lama Madinah, belum tergabung alias.

**G6 — Studi kasus 5 peristiwa (tokoh/lokasi/waktu):** Badr 44/9/6 · Uhud 41/3/10 · Hudaibiyah 7/5/4 · Khaibar 7/2/1 · Tabuk 4/0/1. Hanya **Muhammad** hadir di kelima peristiwa. Perbedaan ukuran mencerminkan **bias cakupan NER**, bukan skala historis.

🖼️ `data/result/analysis/v4_hybrid/case_study_panel*.png` (panel 5 sub-graf)

## Slide 22 — Evaluasi KG: Pengujian Fungsional (Competency Questions)
> Enam **fungsi** (F1–F6) yang harus dipenuhi graf, diuji lewat kueri Cypher. Tiap fungsi dinilai: dapat dieksekusi · hasil tidak kosong · sesuai teks sumber · terlacak (*provenance*).

| Fungsi | Kebutuhan Fungsional | Contoh kueri |
|---|---|---|
| F1 | Tokoh yang terlibat pada suatu peristiwa | Siapa terlibat Perang Badr? |
| F2 | Peristiwa yang terjadi di suatu lokasi | Peristiwa di Madinah? |
| F3 | Peristiwa yang terjadi pada suatu waktu | Peristiwa tahun ke-2 H? |
| F4 | Peristiwa yang melibatkan tokoh tertentu | Peristiwa Abu Bakar? |
| F5 | Rantai relasi lintas-entitas (*multi-hop*) | Lokasi peristiwa yang melibatkan Umar? |
| F6 | Urutan kronologis antar peristiwa | Urutan `PRECEDES` |

> Keenam fungsi **berhasil dipenuhi**; jawaban terlacak balik ke *chunk* sumber (`evidence`, `halaman`, `chunk_id`) → graf layak mendukung penelusuran relasional Sirah.

🖼️ Screenshot hasil kueri F1 (Neo4j Browser). **[PERIKSA]** isi jumlah hasil tiap kueri dari `functional_test_queries_bab4.cypher`.

---

# SEKSI 6 — KESIMPULAN & SARAN

## Slide 23 — Kesimpulan
- **RM1 — Persiapan data:** OCR → preprocessing → chunking → pelabelan BIO + alias clustering. Data uji **254 chunk, 49.739 token, 1.969 entitas**; Event (75) & Time (118) minoritas tajam.
- **RM2 — Ekstraksi entitas:** NER IndoBERT + *iterative self-training*; terbaik **uncased + augmentation (mention replacement + parafrase)** → F1 mikro **0,9756**. Minoritas terangkat: Time 0,80→0,90, Event 0,93→0,95.
- **RM3 — Konstruksi graf:** KG di Neo4j (4 entitas + relasi inti + antar-tokoh + `PRECEDES`); tiap relasi menyimpan *provenance*.
- **RM4 — Evaluasi & analisis:** 6 fungsi (F1–F6) berhasil & terlacak; SNA (137 node, 1.853 edge, density 0,199) → Muhammad dominan & **8 komunitas** (Q **0,2831**). Keterbatasan: sentralitas berlebih akibat over-ekstraksi `INVOLVED_IN`.

## Slide 24 — Saran
1. **Ekstraksi relasi berbasis kata kerja** — ganti/lengkapi `INVOLVED_IN` berbasis kedekatan (rawan over/under-extraction) dengan predikat tindakan, agar artefak seperti "Amr bin Umayyah" berkurang.
2. **Deteksi Event dari konstruksi verbal** — banyak peristiwa (kelahiran, wahyu pertama, wafat) muncul sebagai frasa deskriptif; kembangkan agar tak lagi ditambah manual.
3. **Perbaiki penyelarasan label & uji ulang** — perbaiki fungsi *word-to-subword* agar perbandingan cased/RoBERTa adil; perketat pemeriksaan *ground truth*.
4. **Perkuat alias & perluas cakupan** — satukan alias lokasi (Yatsrib–Madinah); uji pada sumber Sirah lain; kembangkan pemanfaatan graf (tanya-jawab / visualisasi).

## Slide 25 — Penutup
Terima kasih — untuk setiap koreksi, pertanyaan, dan masukan sepanjang proses ini.

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
> Kesimpulan: **misalignment label kata-ke-subword** pada tokenizer cased/BPE, bukan kelemahan model.

## Backup B4 — Before/After Augmentasi (data latih)
| Label (token) | Sebelum | Sesudah | Perubahan |
|---|---:|---:|---:|
| O | 108.815 | 163.352 | +50% |
| Person (B+I) | 5.519 | 8.311 | +51% |
| Location (B+I) | 1.038 | 1.875 | +81% |
| Time (B+I) | 664 | 1.107 | +67% |
| Event (B+I) | 317 | 943 | **+198%** |

> Augmentasi menambah **semua kelas** (bukan mengurangi O); Event tumbuh paling tajam. Entitas: 4.247 → 6.780.

---

# Lampiran — [PERIKSA] sebelum cetak
1. **Uji fungsional (Slide 22):** isi jumlah hasil tiap kueri dari eksekusi nyata `functional_test_queries_bab4.cypher` di Neo4j (setelah `import_sirah_v4_hybrid.cypher`).
2. **Gambar/visual:** siapkan screenshot Neo4j (Contoh KG, ego Muhammad, perbandingan ego Muhammad vs Abu Bakar, komunitas sub-graf, kesalahan graf Amr, hasil kueri F1) — query di `data/result/neo4j/sna_evidence_queries_bab4.cypher` + komentar `[SISIPKAN GAMBAR]` di buku Bab 4.
3. **Konsistensi:** angka slide sudah = buku terbaru (done_newest + gold terkoreksi + KG v4). Jangan campur dengan deck lama (`PPT_konten_revisi.md`, grupB).
