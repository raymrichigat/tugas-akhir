# [ARSIP] Revisi Konten PPT Sidang Akhir — Genta Putra Prayoga (5025221040)

> ⚠️ **FILE ARSIP — angka LAMA (benchmark grupB / done_running).** Deck AKTIF untuk sidang = **`PPT_konten_terbaru.md`** (done_newest + gold terkoreksi + KG v4: aug 0,9756; 137 node; test 254/49.739/1.969). File ini dipertahankan hanya sebagai rujukan sejarah, JANGAN dipakai untuk sidang.

> **Cara pakai dokumen ini.** Tiap blok = 1 slide. Bagian **Konten** = teks final siap di-*paste* ke desain slide-mu (struktur mengikuti gaya deck acuan Audrey: tiap uji coba punya slide **Hasil** dan slide **Pembahasan** terpisah). Bagian **🔧 Perubahan** = apa yang beda dari deck lama supaya kamu bisa review cepat.
>
> **Sumber angka:** seluruh angka diselaraskan ke **buku** (`docs/bab4/hasil_pembahasan.md` + `docs/bab5/kesimpulan.md`), sesuai keputusan. Angka F1 uji coba 1/2/3 di deck lama **sudah benar** (cocok buku); yang diperbaiki terutama **tabel distribusi**, **skema relasi**, dan **konsistensi**.
>
> **⚠️ Catatan penting (jangan dilewat):** angka ini = **gold LAMA (grup B)**, sama dengan yang ada di buku sekarang. Hasil **re-anotasi gold terkoreksi belum dihitung** (itu yang sedang kamu siapkan lewat run augmentasi). Kalau nanti re-run selesai & buku di-update, **deck ini ikut di-update**. F1 baru **tidak comparable** dengan yang di sini.
>
> **[PERIKSA]** = angka yang buku sendiri tandai perlu dicek ulang ke `test.csv` / `seqeval_grupB_results.md`. Jangan hitung ulang dari `test.csv` yang ada di repo sekarang — itu sudah gold BARU, beda benchmark.

---

## Ringkasan perubahan besar

| # | Slide lama | Masalah | Perbaikan |
|---|-----------|---------|-----------|
| 1 | Slide 2 (Outline) | Mencantumkan "Tujuan" & "Implementasi" & "Hasil Uji Coba" & "Pembahasan" terpisah, tapi tak ada slide Tujuan; urutan tak match isi | Outline 6 seksi gaya Audrey: Latar Belakang · Rumusan Masalah · Metode · Implementasi · Hasil & Pembahasan · Kesimpulan & Saran |
| 2 | Slide 4 | `OCCURRED_AT` & `OCCURRED_ON` sama-sama ditulis "(Person – Event)" — **SALAH** | `OCCURRED_AT` = Event–Location; `OCCURRED_ON` = Event–Time |
| 3 | Slide 9 | Judul "Preprocessing & Chunking" padahal isi soal anotasi/pelabelan | Judul → **Pelabelan Data** |
| 4 | Slide 13 | Event train 144/test 47, total test 1.759, train 4.246 | Event train **163**/test **51**, total test **1.763**, train **4.265** (ikut buku) |
| 5 | Slide 13 | Typo "% **toal** Entitas" | "% total Entitas" |
| 6 | Slide 17–18 | SNA cuma 1 tabel (top-6 PageRank) + 1 slide pembahasan | Diperluas gaya Audrey: Hasil (G1 top-10 + G2 betweenness), Pembahasan (komunitas + validasi artefak), Peristiwa/Lokasi (G4/G7/G6), Uji Fungsional (6 Cypher) |
| 7 | Slide 14–16 | Hasil & pembahasan digabung per slide | Dipisah per uji coba: **Hasil** = 1 tabel kompak + **Temuan Kunci** ringkas (headline "apa"); **Pembahasan** = "mengapa" + anatomi error |

---

# SEKSI 0 — PEMBUKA

## Slide 1 — Judul  *(tetap)*
**Konten:**
- PENDEKATAN NAMED-ENTITY RECOGNITION DALAM PEMBANGUNAN KNOWLEDGE GRAPH SIRAH NABAWIYAH
- Genta Putra Prayoga — 5025221040
- Dosen Pembimbing: Dini Adni Navastara, S.Kom., M.Sc.
- Dosen Ko-Pembimbing: Ratih Nur Esti Anggraini, S.Kom., M.Sc., Ph.D.

🔧 **Perubahan:** tidak ada.

---

## Slide 2 — Outline  *(revisi)*
**Konten (gaya Audrey, bernomor):**
- 01 · Latar Belakang
- 02 · Rumusan Masalah
- 03 · Metode
- 04 · Implementasi
- 05 · Hasil dan Pembahasan
- 06 · Kesimpulan dan Saran

🔧 **Perubahan:** hapus item "Tujuan", "Hasil Uji Coba", dan "Pembahasan" yang berdiri sendiri (tak ada slide-nya / tumpang tindih). Deck acuan tidak memakai slide Tujuan; kalau prodimu mewajibkan Tujuan, tambahkan 1 slide setelah Rumusan Masalah.

---

# SEKSI 1 — LATAR BELAKANG

## Slide 3 — Latar Belakang (Masalah)  *(tetap, rapikan)*
**Konten:**
> Sirah Nabawiyah kaya akan informasi tokoh, peristiwa, lokasi, dan waktu, tetapi tersaji dalam narasi panjang sehingga sulit ditelusuri secara relasional.

- **Informasi tersebar dalam narasi panjang** — tokoh, peristiwa, lokasi, dan waktu disajikan kronologis dalam teks panjang dan kompleks.
- **Pencarian kata kunci belum cukup** — sulit menjawab pertanyaan relasional seperti "Siapa yang terlibat?", "Peristiwa apa yang terjadi di lokasi X?".
- **Relasi tidak eksplisit** — keterkaitan antar-entitas tidak tersimpan, sehingga perlu penelusuran manual.

> Diperlukan pendekatan yang mampu **menyimpan dan menelusuri hubungan** dalam Sirah secara eksplisit.

🔧 **Perubahan:** perbaiki kapital "Panjang" → "panjang"; sisanya tetap.

---

## Slide 4 — Latar Belakang (Solusi: Knowledge Graph)  *(revisi PENTING)*
**Konten:**
> Pendekatan **Knowledge Graph** merepresentasikan hubungan tokoh, peristiwa, lokasi, dan waktu dari Sirah Nabawiyah secara eksplisit.

Alur gagasan:
1. **Teks Sirah Nabawiyah** (berbahasa Indonesia) → data.
2. **Ekstraksi Entitas (NER)** berbasis SRL, strategi semi-supervised (*iterative self-training*).
3. **Entitas utama (4):** Person (tokoh) · Location (lokasi) · Event (kejadian) · Time (waktu).
4. **Relasi inti:**
   - `INVOLVED_IN` — **Person → Event** (keterlibatan tokoh pada peristiwa)
   - `OCCURRED_AT` — **Event → Location** (lokasi peristiwa)
   - `OCCURRED_ON` — **Event → Time** (waktu peristiwa)
   - `PRECEDES` — **Event → Event** (urutan kronologi)
   - Relasi antar-tokoh — **Person → Person** (`KELUARGA`, `SAHABAT`, `MUSUH`)
5. **Knowledge Graph (Neo4j).**

🔧 **Perubahan (WAJIB):** deck lama menulis `OCCURRED_AT` dan `OCCURRED_ON` dua-duanya "(Person – Event)" — itu salah. Yang benar: `OCCURRED_AT` = Event–Location, `OCCURRED_ON` = Event–Time (lihat Bab 5 poin 3). Tambahkan juga `PRECEDES` (Event–Event) yang sebelumnya tercecer.

---

# SEKSI 2 — RUMUSAN MASALAH

## Slide 5 — Rumusan Masalah  *(tetap, urutkan 1→4)*
**Konten:**
1. Bagaimana **menyiapkan** data teks Sirah Nabawiyah agar menjadi dataset yang siap digunakan?
2. Bagaimana **mengekstraksi entitas** dari teks Sirah Nabawiyah menggunakan NER berbasis SRL dengan strategi *iterative self-training*?
3. Bagaimana **membangun knowledge graph** berbasis entitas Person, Event, Location, Time beserta relasinya menggunakan Neo4j?
4. Bagaimana **mengevaluasi** hasil NER melalui tiga skenario uji coba serta **menganalisis knowledge graph** (termasuk Social Network Analysis dan pengujian fungsional graf)?

🔧 **Perubahan:** urutkan menaik 1→4 (deck lama tampil acak 3-2-1-4). Isi tetap.

---

# SEKSI 3 — METODE

## Slide 6 — Metode Penelitian  *(tetap)*
**Konten (6 tahap berurutan):**
1. Preparasi Data
2. Preprocessing & Chunking
3. Pelabelan Data
4. Ekstraksi Entitas
5. Konstruksi Knowledge Graph
6. Pengujian & Evaluasi

🔧 **Perubahan:** tidak ada (opsional: perbaiki spasi "MetodePenelitian" → "Metode Penelitian").

---

# SEKSI 4 — IMPLEMENTASI

## Slide 7 — Preparasi Data  *(tetap)*
**Konten:**
> Mengubah buku Sirah Nabawiyah (PDF hasil pindai) menjadi dataset teks terstruktur siap olah.

- **~633 halaman** — Sirah Nabawiyah karya Syaikh Shafiyyurrahman Al-Mubarakfuri (terjemahan Kathur Suhardi), Bahasa Indonesia.
- **PaddleOCR** → ekstraksi teks dari pindaian.
- **1 · Ekstraksi dokumen terstruktur** — teks OCR per halaman disusun ulang mengikuti daftar isi (TOC); footer berulang dihapus; judul bab/subbab dikenali via *exact* + *fuzzy matching* (ambang 0,92) → JSON hierarkis (bab → subbab → teks).
- **2 · Konversi ke CSV** — JSON diratakan jadi tabel; tiap baris = satu subbab (kolom: judul_bab, judul_sub_bab, halaman, teks).

🔧 **Perubahan:** tidak ada.

---

## Slide 8 — Preprocessing & Chunking  *(tetap)*
**Konten:**
**Preprocessing** — membersihkan teks OCR agar konsisten & bebas *noise*:
- Saring baris tak relevan (UNKNOWN BAB, bibliografi).
- Hapus karakter non-*printable* & simbol non-informatif (@, *, #).
- Normalisasi apostrof/ain Arab (Ka`bah → Ka'bah); perbaiki spasi prefiks Arab (Al- Walid → Al-Walid).
- Bersihkan *gibberish* di tingkat token, segmen, & kalimat.

**Chunking** — memecah teks per subbab jadi *chunk* menjaga konteks:
- Segmentasi kalimat; gabung ke *chunk* maks 1.500 karakter (kalimat tak dipotong di tengah).
- Overlap 1 kalimat antar-*chunk*; tiap *chunk* diberi ID unik + metadata (bab, subbab, halaman).

🔧 **Perubahan:** tidak ada.

---

## Slide 9 — Pelabelan Data  *(revisi judul)*
**Konten:**
> Membentuk data anotasi sebagai *seed* pelatihan NER sekaligus *ground truth* evaluasi.

1. **Anotasi semi-otomatis** — kandidat entitas dibentuk otomatis via *gazetteer* (kamus) + pola *regex* untuk PERSON (nama & nasab), EVENT (perang/ghazwah), LOCATION, TIME; kandidat tumpang-tindih dideduplikasi (prioritas *span* terpanjang).
2. **Koreksi manual** — pra-anotasi ditinjau & dikoreksi (tambah entitas terlewat, hapus salah, perbaiki batas), berpedoman 4 label.
3. **Konversi BIO** — anotasi *span* → format token-per-baris (Begin-Inside-Outside) karena NER diproses sebagai *sequence labeling*; data dibagi latih/uji (*test size* 0,3).

🔧 **Perubahan (WAJIB):** judul slide lama keliru "Preprocessing & Chunking" → ganti **"Pelabelan Data"**.

---

## Slide 10 — Ekstraksi Entitas (SRL-NER + Self-Training)  *(tetap)*
**Konten:**
> NER berbasis IndoBERT dilatih semi-supervised via *iterative self-training* untuk memperluas anotasi dari *seed* terbatas ke seluruh korpus.

- **Berbasis SRL** — orientasi peran kalimat: pelaku→Person, tempat→Location, waktu→Time, peristiwa→Event (via pola & kamus, **bukan** parsing penuh).
- **Iterative self-training** — latih dengan *seed* → prediksi data tak berlabel → prediksi berkeyakinan tinggi jadi *pseudo-label* → latih ulang.
- **Kriteria pseudo-label** — kalimat diterima bila rata-rata keyakinan entitas ≥ 0,9; diulang sampai konvergen.
- Konfigurasi: **IndoBERT uncased** · *threshold* **0,9** · maks **6 iterasi** · **~237** *chunk* tak berlabel.

🔧 **Perubahan:** tidak ada (deck sudah jujur: "via pola & kamus, bukan parsing penuh").

---

## Slide 11 — Konstruksi Knowledge Graph  *(tetap)*
**Konten:**
> Menyusun graf dari daftar entitas: satukan variasi nama → bentuk relasi → tambah dimensi waktu → muat ke Neo4j.

- **Alias Clustering** — variasi nama disatukan ke bentuk kanonik (manual + Jaro-Winkler, ambang 0,93); ~143 variasi → ~109 klaster.
- **Pembentukan relasi** — dari *co-occurrence* (1 kalimat / <200 karakter); EVENT sebagai pusat keterhubungan.
- **Periodisasi peristiwa** — EVENT dipetakan ke periode (P0–P14) dari daftar isi; `PRECEDES` untuk urutan kronologis.
- **Pemuatan ke Neo4j** — node (Person/Event/Location/Time/Period) & edge via `MERGE` dengan *constraint* keunikan.
- Tipe relasi: `INVOLVED_IN` · `OCCURRED_AT` · `OCCURRED_ON` · `PRECEDES` · relasi antar-tokoh.

🖼️ **Diagram (PERLU DIPERBAIKI):** flowchart lama hanya menggambar tahap Neo4j saja. Diagram terkoreksi (4 tahap: Alias Clustering → Pembentukan Relasi → Periodisasi → Pemuatan Neo4j) ada di **`docs/daftar-sidang/slide11_diagram_konstruksi_kg.md`** (mermaid ringkas + detail).

🔧 **Perubahan:** ganti flowchart yang hanya mencakup pemuatan Neo4j dengan diagram 4-tahap sesuai konten slide (rujuk `docs/bab3/flowchart/` 3.7–3.10).

---

# SEKSI 5 — HASIL DAN PEMBAHASAN

## Slide 12 — Profil Data & Ketidakseimbangan Kelas  *(revisi angka)*
**Konten:**
> Seluruh evaluasi NER memakai data uji yang sama; komposisi kelas sangat timpang → jadi kunci pembacaan semua hasil.

**Split data**
| Split | Chunk | Token | Entitas |
|---|---:|---:|---:|
| Train | 599 | 102.884 | 4.265 |
| Test | 258 | 42.558 | 1.763 |
| Unlabelled | 237 | 39.207 | — |

**Distribusi entitas per kelas**
| Kelas | Train | % | Test | % |
|---|---:|---:|---:|---:|
| Person | 2.884 | 67,6 | 1.189 | 67,4 |
| Location | 985 | 23,1 | 449 | 25,5 |
| Time | 233 | 5,5 | 74 | 4,2 |
| Event | 163 | 3,8 | 51 | 2,9 |

> **Temuan:** ketimpangan ekstrem — Person mendominasi; **Event & Time** kelas minoritas (rasio ± **18:1** di train, **23:1** di test). Inilah dasar Uji Coba 1.

🖼️ **Aset visual:** `data/result/analysis/bab4_viz/eda_imbalance.png` (bar chart train vs test)

🔧 **Perubahan (WAJIB, ikut buku):** Event train 144→**163**, test 47→**51**; total train 4.246→**4.265**, total test 1.759→**1.763**; typo "toal"→"total". **[PERIKSA]** cocokkan ke `seqeval_grupB_results.md`/`test.csv` (buku pun menandai ini perlu cek). Sekarang jadi konsisten dengan slide Kesimpulan.

---

## Slide 13 — Uji Coba 1: HASIL (Penanganan Imbalance)  *(revisi: tabel kompak + Temuan Kunci)*
**Konten:**
> Membandingkan *baseline* dengan 4 teknik penanganan kelas minoritas pada pipeline identik. Metrik: F1 *entity-level* (seqeval).

| Skenario | F1 mikro | Macro F1 | F1 Event | F1 Time |
|---|---:|---:|---:|---:|
| Baseline | 0,9481 | 0,8892 | 0,8039 | 0,8408 |
| Weighted CE | 0,9393 | 0,8648 | 0,7767 | 0,7898 |
| SCL | 0,9512 | 0,8902 | 0,8200 | 0,8258 |
| JSCL | 0,9434 | 0,8932 | 0,8367 | 0,8408 |
| **Augmentation** | **0,9581** | **0,9235** | **0,9020** | **0,8627** |

**🔑 Temuan Kunci (callout ringkas):** Augmentation terbaik (F1 mikro **0,9581**); lonjakan di kelas minoritas — Event 0,80→**0,90**, Time 0,84→**0,86**.

🖼️ **Aset visual:** `data/result/analysis/bab4_viz/f1_uc1_perkelas.png` (opsional, dampingi/ganti tabel)

🔧 **Perubahan:** **1 tabel kompak** (F1 mikro/Macro/Event/Time) — buang tabel agregat P/R & per-kelas penuh (terlalu berat). Precision/Recall pindah ke Pembahasan/lisan. Temuan Kunci = callout ringkas di sini (bukan pembahasan panjang).

---

## Slide 14 — Uji Coba 1: PEMBAHASAN (mengapa + error)  *(revisi)*
**Konten:**
- **Kenapa augmentation menang?** *Mention replacement* menambah **ragam contoh** kelas minoritas (Event/Time) yang tadinya sangat sedikit — bukan sekadar menggeser perhatian model.
- **Kenapa Weighted CE & JSCL justru di bawah baseline?** Membobot kelas minoritas membuat model **over-deteksi**: recall naik (0,957) tapi precision anjlok (0,922), FP membengkak ke **150 token**. Menaikkan bobot ≠ menambah informasi baru.
- **Anatomi error (semua skenario):** didominasi **keputusan deteksi** — FP 45–65% + FN 28–47%; **salah-tipe hanya 2–6%**, boundary 2–4%. Artinya model **paham 4 tipe**; tantangannya "entitas atau bukan".

> **Simpulan UC1:** menambah contoh minoritas (*oversampling* via augmentasi) mengalahkan sekadar menggeser perhatian model (*weighted CE*).

🖼️ **Aset visual:** `data/result/analysis/error_viz/by_group/s1_compare.png` (panel total/FN/FP/FN-rate per kelas)

🔧 **Perubahan:** fokus ke **"mengapa" + anatomi error** (tidak mengulang angka tabel). Ringkasan hasil sudah jadi Temuan Kunci di slide Hasil.

---

## Slide 15 — Uji Coba 2: HASIL (Komparasi Model)  *(revisi: tabel kompak + Temuan Kunci)*
**Konten:**
> Lima *backbone* pra-latih pada pipeline identik (hanya model yang divariasikan).

| Model (backbone) | F1 mikro | Macro F1 | Kelompok |
|---|---:|---:|:--|
| **IndoBERT uncased** (baseline) | **0,9481** | 0,8892 | stabil |
| cahya bert-indonesian | 0,9324 | 0,8744 | stabil |
| DistilBERT Indonesia | 0,9442 | 0,8748 | stabil |
| IndoBERT cased | 0,7770 | 0,6867 | **anomali** |
| RoBERTa Indonesia | 0,8068 | 0,7165 | **anomali** |

**🔑 Temuan Kunci:** tiga model *uncased* stabil (0,93–0,95), **IndoBERT uncased terbaik**; IndoBERT *cased* & RoBERTa anjlok (0,78–0,81).

🖼️ **Aset visual:** `data/result/analysis/bab4_viz/f1_uc2_agregat.png`

🔧 **Perubahan:** **1 tabel kompak** (F1 mikro/Macro/Kelompok) — buang kolom P/R & tabel per-kelas penuh. Detail per-kelas → Pembahasan/backup.

---

## Slide 16 — Uji Coba 2: PEMBAHASAN (mengapa + error)  *(revisi PENTING — hindari salah tafsir)*
**Konten — kenapa cased & RoBERTa anjlok? BUKAN karena model jelek:**
Akar masalah = **misalignment label kata-ke-subword** (pipeline disetel untuk tokenizer *uncased*). Tiga bukti:
- **Bukan efek self-training** — F1 dari *base* justru naik tipis (cased 0,7608→0,7770) → defisit **ada sejak awal**.
- **Terpusat di entitas banyak-kata** (Person & Time); Location (umumnya 1 kata) tetap tinggi (~0,90).
- **Boundary B/I meledak** ke ~100 token (vs 4–7 uncased), 91–94 di antaranya pada nama Person.

> ⚠️ **Framing wajib:** rendahnya cased/RoBERTa = **artefak penyelarasan label**, bukan bukti model buruk untuk NER Sirah.

🖼️ **Aset visual:** `data/result/analysis/error_viz/by_group/s2_confusion.png` (panel "3 rapi vs 2 rusak" — pesan kebaca sekilas)

🔧 **Perubahan:** fokus **"mengapa anomali" + 3 bukti** (ringkasan hasil sudah jadi Temuan Kunci di slide Hasil). Poin gampang salah tafsir penguji.

---

## Slide 17 — Uji Coba 3: HASIL (Modul POS-tag)  *(revisi: tabel kompak + Temuan Kunci)*
**Konten:**
> Membandingkan model **tanpa** vs **dengan** fitur POS-tag (POS asli via *tagger*, bukan *placeholder*).

| Skenario | Precision | Recall | F1 mikro | Error token |
|---|---:|---:|---:|---:|
| Baseline | 0,9489 | 0,9472 | **0,9481** | **192** |
| POS-tag | 0,9286 | 0,9597 | 0,9439 | 224 |

**🔑 Temuan Kunci:** POS-tag **tidak memberi perbaikan bersih** — F1 mikro 0,9439 ≈ / sedikit di bawah baseline (0,9481).

🖼️ **Aset visual:** `data/result/analysis/bab4_viz/f1_uc3_agregat.png`

🔧 **Perubahan:** **1 tabel** (P/R/F1 + Error token) — kolom P/R justru inti cerita UC3 (recall↑ precision↓). Tabel per-kelas → backup.

---

## Slide 18 — Uji Coba 3: PEMBAHASAN (mengapa + error)  *(revisi)*
**Konten:**
- **Kenapa POS-tag tak membantu? Redundan.** IndoBERT sebagai model kontekstual **sudah menyerap** petunjuk kelas kata, jadi POS eksplisit tak menambah sinyal baru.
- **Pola pertukaran:** recall naik (0,9597) tapi precision turun (0,9286) → model lebih agresif menebak (FP **86→146**), mirip Weighted CE.
- **FP dominan = frasa honorifik** (mis. *Shalallahu Alaihi wa Sallam*) keliru ditandai Person.
- **Catatan jujur:** POS **asli** (bukan placeholder) → kegagalannya **sah**, bukan artefak fitur palsu.

🖼️ **Aset visual:** `data/result/analysis/error_viz/by_group/s3_compare.png` (FP naik, FN turun)

🔧 **Perubahan:** fokus **"mengapa redundan" + FP honorifik**; ringkasan hasil sudah jadi Temuan Kunci di slide Hasil.

---

## Slide 19 — Evaluasi Graf: HASIL — Sentralitas Tokoh (G1 & G2)  *(BARU/perluas)*
**Konten:**
> Proyeksi jaringan tokoh (dua tokoh terhubung bila terlibat peristiwa yang sama). **208 node · 1.832 edge · density 0,0851**.

**G1 — Tokoh paling sentral (urut PageRank)**
| # | Tokoh | Degree | Closeness | PageRank |
|---:|---|---:|---:|---:|
| 1 | Muhammad | 0,5894 | 0,6503 | 0,0565 |
| 2 | Ali bin Abu Thalib | 0,3961 | 0,5357 | 0,0224 |
| 3 | Abu Bakar | 0,3720 | 0,5153 | 0,0206 |
| 4 | Aisyah | 0,3623 | 0,5123 | 0,0195 |
| 5 | Abu Jahal | 0,3720 | 0,5261 | 0,0189 |
| 6 | Umar bin Al-Khaththab | 0,3623 | 0,5168 | 0,0168 |
| 7 | Abu Sufyan bin Harb | 0,3478 | 0,5050 | 0,0153 |
| 8 | Utsman bin Affan | 0,3478 | 0,5064 | 0,0138 |
| 9 | Abu Azzah | 0,3333 | 0,4993 | 0,0130 |
| 10 | Khadijah | 0,0870 | 0,4137 | 0,0118 |

**G2 — Jembatan antar-kelompok (Betweenness):** Muhammad (0,3567) ≫ Utsman (0,1042) · Abu Jahal (0,0712) · Ali (0,0677) · Hamzah (0,0647).

🖼️ **Aset visual:** `docs/bimbingan/screenshots/A1_ego_muhammad.png` (ego Nabi — visual sentralitas paling kuat) atau `data/result/analysis/v3/sna_person_network.png`

🔧 **Perubahan:** perluas dari top-6 PageRank saja → top-10 + Degree/Closeness + betweenness (G2). Semua dari buku Tabel 4.18–4.19.

---

## Slide 20 — Evaluasi Graf: PEMBAHASAN — Komunitas & Validasi  *(BARU)*
**Konten — Temuan Kunci:**
- **Struktur masuk akal:** Muhammad dominan **di semua** ukuran (terhubung langsung ke ±122 dari 208 tokoh) → pusat seluruh peristiwa.
- **Dua peran berbeda:** *degree/PageRank* tinggi = sering muncul bersama (Ali, Abu Bakar, Aisyah); *betweenness* tinggi = penghubung (Utsman lompat #8→#2).
- **Komunitas:** Louvain → **15 komunitas**, modularitas **Q = 0,3851** (struktur kelompok cukup jelas; stabil, ARI Louvain–greedy 0,78). Contoh koheren: keluarga/lingkar awal Nabi, tokoh Madinah & ekspansi, oposisi Quraisy.
- **Validasi jujur (artefak):** beberapa nama terdengar asing karena relasi `INVOLVED_IN` dibentuk dari **kedekatan teks**. Contoh **Amr bin Umayyah** — tanpa pembobotan sempat **#2 PageRank** (di bawah Nabi), padahal 3 dari 4 relasinya *false positive*; peran nyatanya kurir Nabi. Setelah pembobotan turun ke **#18**.

> **Simpulan:** peringkat sentralitas **wajib divalidasi balik ke teks**; solusi tuntas over-ekstraksi = ekstraksi relasi berbasis kata kerja (future work).

🖼️ **Aset visual:** `data/result/analysis/v3/sna_person_network.png` (node berwarna per komunitas) + `docs/bimbingan/screenshots/A2_komunitas_all.png`

🔧 **Perubahan:** slide baru — menggabung interpretasi + komunitas + kejujuran artefak (buku 4.4.1). Ini yang membedakan "analisis" dari sekadar "angka".

---

## Slide 21 — Evaluasi Graf: Peristiwa, Lokasi & Studi Kasus (G4/G7/G6)  *(BARU, opsional-padat)*
**Konten:**
**G4 — Peristiwa paling sentral (PageRank):** Perang Badr (0,0767) · Uhud (0,0704) · Khandaq (0,0505) · Hijrah ke Madinah (0,0489) · Kelahiran Nabi (0,0407) · Wafat Nabi (0,0368). → 3 perang besar + tonggak daur hidup Nabi.

**G7 — Lokasi paling sentral (weighted degree):** Madinah (684) · Makkah (595) · Habasyah (505) · Yatsrib (453) · Badr (450). → dua pusat fase Sirah (Makkah–Madinah). *Catatan:* "Yatsrib" = nama lama Madinah, belum tergabung alias.

**G6 — Studi kasus 5 peristiwa (jumlah tokoh):** Perang Badr 45 · Uhud 34 · Khaibar 6 · Hudaibiyah 2 · Tabuk 4. Hanya **Muhammad** hadir di kelima peristiwa. Perbedaan ukuran mencerminkan **bias cakupan NER**, bukan skala historis.

🖼️ **Aset visual:** `data/result/analysis/v3/event_network.png` (jaringan peristiwa) + `data/result/analysis/v3/case_study_panel.png` (5 sub-graf)

🔧 **Perubahan:** slide baru merangkum G4/G7/G6 (buku Tabel 4.20–4.23). Kalau terlalu padat, pecah jadi 2 slide.

---

## Slide 22 — Evaluasi Graf: Pengujian Fungsional  *(BARU)*
**Konten:**
> Enam skenario kueri Cypher menguji kelayakan penelusuran relasional. Tiap kueri dinilai: bisa dieksekusi · hasil tidak kosong · sesuai teks sumber · terlacak (*provenance*).

| No | Kueri | Hasil |
|---|---|:---:|
| 1 | Tokoh dalam suatu peristiwa (Perang Badr) | ✔ |
| 2 | Peristiwa di suatu lokasi (Madinah) | ✔ |
| 3 | Peristiwa pada suatu waktu (tahun ke-2 H) | ✔ |
| 4 | Peristiwa yang melibatkan tokoh (Abu Bakar) | ✔ |
| 5 | Multi-hop (tokoh → peristiwa → lokasi; Umar) | ✔ |
| 6 | Urutan kronologi peristiwa (`PRECEDES`) | ✔ |

> Keenam skenario **berhasil** dijalankan & jawabannya dapat ditelusuri balik ke *chunk* sumber (properti `evidence`, `halaman`, `chunk_id`) → graf layak mendukung penelusuran relasional Sirah.

🔧 **Perubahan:** slide baru (buku Tabel 4.24). **[PERIKSA]** isi "jumlah hasil" tiap kueri dari eksekusi nyata `functional_test_queries_bab4.cypher` sebelum sidang.

---

# SEKSI 6 — KESIMPULAN & SARAN

## Slide 23 — Kesimpulan  *(revisi angka)*
**Konten (jawab 4 rumusan masalah):**
- **RM1 — Persiapan data:** OCR → preprocessing → chunking → pelabelan BIO (Person/Event/Location/Time) + alias clustering. Menghasilkan data uji **258 chunk, 42.558 token, 1.763 entitas** dengan Event (51) & Time (74) sebagai minoritas tajam.
- **RM2 — Ekstraksi entitas:** NER IndoBERT + *iterative self-training*; konfigurasi terbaik **uncased + augmentation** → F1 mikro **0,9581** (precision 0,9554, recall 0,9609). Augmentation mengangkat minoritas: Event 0,80→0,90, Time 0,84→0,86.
- **RM3 — Konstruksi graf:** KG di Neo4j dengan 4 entitas + relasi inti (`INVOLVED_IN`, `OCCURRED_AT`, `OCCURRED_ON`, `PRECEDES`) + relasi antar-tokoh; tiap relasi menyimpan *provenance* (bukti, halaman, chunk).
- **RM4 — Evaluasi & analisis:** 6 kueri Cypher berhasil & terlacak; SNA (208 node, 1.832 edge, density 0,0851) menunjukkan Muhammad dominan & **15 komunitas** koheren (Q **0,3851**). Keterbatasan: sentralitas berlebih akibat over-ekstraksi `INVOLVED_IN`.

🔧 **Perubahan:** samakan angka ke buku (1.763 entitas, Event 51). Deck lama sudah mendekati; tinggal konsistenkan.

---

## Slide 24 — Saran  *(revisi, ambil dari Bab 5)*
**Konten (arah pengembangan):**
1. **Ekstraksi relasi berbasis kata kerja** — ganti/lengkapi `INVOLVED_IN` berbasis kedekatan (rawan over/under-extraction) dengan predikat tindakan (mis. LLM), agar artefak seperti "Amr bin Umayyah" berkurang.
2. **Deteksi Event dari konstruksi verbal** — banyak peristiwa (kelahiran, wahyu pertama, wafat) muncul sebagai frasa deskriptif; kembangkan agar tak lagi ditambah manual.
3. **Perbaiki penyelarasan label & uji ulang** — perbaiki fungsi *word-to-subword* agar perbandingan model cased/RoBERTa adil; perketat pemeriksaan *ground truth* (inkonsistensi kapitalisasi).
4. **Perkuat alias & perluas cakupan** — satukan alias lokasi (mis. Yatsrib–Madinah); uji pada sumber Sirah lain; kembangkan pemanfaatan graf (tanya-jawab / visualisasi sejarah).

🔧 **Perubahan:** rapikan jadi 4 butir tematik dari 8 butir Bab 5 (padat untuk slide). Kalau mau lengkap, pakai 8 butir Bab 5.

---

## Slide 25 — Penutup  *(tetap/opsional)*
**Konten:** Terima kasih — untuk setiap koreksi, pertanyaan, dan masukan sepanjang proses ini.

---

# SEKSI 7 — SLIDE BACKUP (ERROR) — taruh SETELAH penutup, buka hanya bila ditanya

> Slide-slide ini **tidak dipresentasikan** secara default. Fungsinya cadangan saat penguji menggali "contoh error konkret", "kenapa cased anjlok", atau "buktikan errornya deteksi bukan tipe". Menjaga alur utama tetap ringkas sambil tetap siap.

## Backup B1 — Anatomi Error Token-level (semua skenario UC1)
**Konten:**
> Kesalahan didominasi keputusan **deteksi**, bukan salah-tipe (konsisten di semua skenario).

| Skenario | Total error | FP (over-deteksi) | FN (terlewat) | Salah tipe | Boundary B/I |
|---|---:|---:|---:|---:|---:|
| Baseline | 192 | 86 (45%) | 91 (47%) | 11 (6%) | 4 (2%) |
| Weighted CE | 232 | 150 (65%) | 67 (29%) | 10 (4%) | 5 (2%) |
| SCL | 197 | 118 (60%) | 63 (32%) | 9 (5%) | 7 (4%) |
| JSCL | 212 | 120 (57%) | 75 (35%) | 10 (5%) | 7 (3%) |
| **Augmentation** | **166** | 86 (52%) | 69 (42%) | **4 (2%)** | 7 (4%) |

> Salah-tipe hanya 2–6% → model **paham 4 tipe**; tantangan = "entitas atau bukan".

🖼️ **Aset visual:** `data/result/analysis/error_viz/confusion_matrix_augmentation.png`

---

## Backup B2 — Tiga Akar Error (contoh token nyata, skenario pemenang)
**Konten:**
- **Over-deteksi (FP) — honorifik jadi Person.** `Shalallahu / Alaihi / wa / Sallam,` → semua diprediksi *Person* padahal acuan O. (chunk 000010-002)
- **Terlewat (FN) — nama langka + artefak OCR.** `Babilonia.` (B-LOCATION) → diprediksi O karena tanda baca menempel. (chunk 000010-012)
- **Salah tipe — nama ganda tempat/peristiwa.** `Hudaibiyah.` acuan B-LOCATION → diprediksi I-EVENT. (chunk 000223-005)
- **Boundary B/I — rentang waktu panjang terpecah.** "hari Senin, malam tanggal 21 dari bulan Ramadhan" → segmen B/I bergeser, tipe (*Time*) tetap benar. (chunk 000032-001)

> Sumber: contoh dari buku Bab 4 (Tabel 4.4–4.7), dapat ditelusuri ke chunk.

---

## Backup B3 — Kenapa cased & RoBERTa anjlok (bukan model jelek)
**Konten:**
- **Trajektori F1 dari base naik tipis** → defisit ada sejak awal, bukan efek self-training:

| Model | F1 base | iter-2 | iter-4 | iter-6 |
|---|---:|---:|---:|---:|
| IndoBERT cased | 0,7608 | 0,7821 | 0,7772 | 0,7770 |
| RoBERTa | 0,7836 | 0,8018 | 0,7945 | 0,8068 |

- **Boundary B/I meledak** ke ~100 token (vs 4–7 uncased), 91–94 di antaranya di **Person** multi-kata.
- Contoh: "Abdullah bin **Amr** bin **Haram,**" → "Amr" ditandai B baru, "Haram," pindah tipe ke Location. (chunk 000084-001)

> Kesimpulan: **misalignment label kata-ke-subword** pada tokenizer cased/BPE, bukan kelemahan model.

🖼️ **Aset visual:** `data/result/analysis/error_viz/per_skenario/indobert-cased/confusion_matrix.png`

---

# Lampiran — Daftar [PERIKSA] sebelum cetak

1. **Distribusi data (Slide 12):** cocokkan Event train 163 / test 51 & total 4.265/1.763 ke `seqeval_grupB_results.md` + `test.csv` **versi grup B** (BUKAN test.csv repo sekarang = gold baru).
2. **Uji fungsional (Slide 22):** isi jumlah hasil tiap kueri dari eksekusi nyata `functional_test_queries_bab4.cypher` di Neo4j (setelah `import_sirah_v3.cypher`).
3. **Gambar/visual:** siapkan PNG pendukung (confusion matrix panel UC1/UC2, `sna_person_network.png`, ego Muhammad Neo4j, `case_study_panel.png`) — path ada di komentar `<!-- file: ... -->` pada `docs/bab4/hasil_pembahasan.md`.
4. **Bila re-run gold terkoreksi selesai:** SEMUA angka F1 & distribusi berubah dan **tidak comparable** dengan versi ini — update buku Bab 4 dulu, baru sinkronkan deck.
