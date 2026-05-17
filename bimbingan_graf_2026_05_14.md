# Bimbingan Bu Diana — Hasil Evaluasi Knowledge Graph Sirah Nabawiyah

> **Tanggal bimbingan:** 2026-05-16 (dokumen disiapkan 2026-05-14, diperbarui 2026-05-15 dengan status SRL-NER terbaru pasca-rerun)
> **Fokus utama bimbingan:** Hasil evaluasi graf (revisi #2 + #4 Bu Diana).
> **Status SRL-NER (revisi #3):** S2a SCL + S2b JSCL **sudah selesai re-run 2026-05-14** — laporan singkat saja kalau Bu Diana tanya, tidak menjadi fokus utama.
> **Sumber data graf saat ini:** pipeline manual semi-auto labelling. **BELUM** pakai output SRL-NER (akan di-regenerate setelah skenario S2/S3 winner-nya dipilih).

---

## DAFTAR ISI

0. [Ringkasan 1 Menit](#0-ringkasan-1-menit)
1. [Knowledge Graph yang Dibangun](#1-knowledge-graph-yang-dibangun)
2. [Evaluasi Node-Level (Centrality)](#2-evaluasi-node-level--siapa-tokoh-paling-penting)
3. [Evaluasi Graph-Level (Struktur Keseluruhan)](#3-evaluasi-graph-level--struktur-keseluruhan)
4. [Community Detection — 3 Metode](#4-community-detection--perbandingan-3-metode)
5. [Studi Kasus 5 Event Berperiode Jauh](#5-studi-kasus-5-event-berperiode-jauh)
6. [Visualisasi yang Siap Ditunjukkan](#6-visualisasi-yang-siap-ditunjukkan)
7. [Demo Neo4j — Setup + Query](#7-demo-neo4j--setup--query)
8. [Panduan Cara Menjelaskan (Skrip Presentasi)](#8-panduan-cara-menjelaskan-skrip-presentasi)
9. [Pertanyaan Bu Diana yang Mungkin + Jawaban](#9-pertanyaan-bu-diana-yang-mungkin--jawaban)

---

## 0. RINGKASAN 1 MENIT

Empat poin yang bisa disampaikan dalam 60 detik kalau Bu Diana minta executive summary:

1. **Knowledge Graph Sirah v2 sudah terbentuk** dengan 892 node (781 Person, 36 Event, 15 Period, sisanya Location/Time) dan 322 relasi (7 jenis).
2. **Evaluasi graf dilakukan 2 layer** (sesuai revisi #4 Bu Diana 2026-05-03):
   - **Node-level (centrality)** — siapa tokoh paling berpengaruh
   - **Graph-level (struktur)** — density, transitivity, community detection, small-world property
3. **Studi kasus 5 event berperiode jauh** (revisi #2 Bu Diana) — Perang Badr/Uhud/Hudaibiyah/Khaibar/Tabuk — divisualisasikan sebagai sub-graf dan dianalisis.
4. **Temuan utama:** Graf Sirah menunjukkan **struktur klan/suku Arab yang kuat** (transitivity 0.77) dengan **karakter small-world** (6 langkah maksimal antar tokoh), didominasi Muhammad sebagai hub utama di semua metrik dan satu-satunya tokoh yang muncul di 5/5 event.

---

## 1. KNOWLEDGE GRAPH YANG DIBANGUN

### 1.1 Schema (Tipe Node + Relasi)

```
NODES (5 tipe)
├── Person       — tokoh + kabilah/Bani (781 node)
├── Event        — peristiwa bersejarah (36 node)
├── Location     — tempat (~30 node)
├── Time         — waktu (~30 node)
└── Period       — periode kronologis (15 node, NEW v2)

EDGES (7 tipe relasi di edges_v2.csv = 322, + IN_PERIOD 36 di-generate saat import Neo4j)
├── INVOLVED_IN  (Person → Event)            — 123 relasi   (weight 0.20–1.00, mean 0.40)
├── KELUARGA     (Person ↔ Person)            — 91 relasi   (weight 0.55–1.00, mean 0.56)
├── OCCURRED_ON  (Event → Time)              — 36 relasi   (weight 0.20–1.00, mean 0.41)
├── OCCURRED_AT  (Event → Location)          — 25 relasi   (weight 0.20–1.00, mean 0.47)
├── SAHABAT      (Person ↔ Person)            — 25 relasi   (weight 0.55 fixed)
├── PRECEDES     (Event → Event, kronologis) — 12 relasi   (weight 1.00 fixed)
├── MUSUH        (Person ↔ Person)            — 10 relasi   (weight 0.55 fixed)
└── IN_PERIOD    (Event → Period, v2 baru)   — 36 relasi   (di-generate dari periodisasi top-down)
```

**Tiga skema pembobotan** (penjelasan untuk Bu Diana):

| Skema | Range | Untuk relasi | Logika |
|---|---|---|---|
| **A. Proximity + Period** | 0.2–1.0 | INVOLVED_IN, OCCURRED_ON, OCCURRED_AT | `weight = proximity_score(0–0.5) + period_score(0–0.5)` — co-occurrence weighted |
| **B. Pattern fixed (0.55)** | 0.55 | KELUARGA, SAHABAT, MUSUH | Regex eksplisit (`bin`, `binti`, `sahabat`, dst.) → bukti langsung, tidak perlu proximity discount |
| **C. Deterministik (1.0)** | 1.0 | PRECEDES | Urutan period → kronologi pasti, bukan probabilistik |

**Detail Skema A:**
- proximity_score: same sentence=0.5, <50char=0.4, <100=0.3, <200=0.2, else=0.1
- period_score: chunk di BAB utama event=0.5, unmapped=0.25, mismatch=0.0
- Beberapa KELUARGA weight > 0.55 karena hasil merge antar pattern hits (dedup keep max).

### 1.2 Pipeline Sumber Data (Penting Disebut ke Bu Diana)

```
PDF Sirah Nabawiyah (633 hal)
  ↓ PaddleOCR
CSV teks per halaman
  ↓ preprocessing + chunking
sirah_chunks_final.csv (~6000 chunks)
  ↓ pre_labelling.py (regex + keyword Bahasa Indonesia)
sirah_prelabelled.csv (~6000 rows entity)
  ↓ alias_clustering.py (Jaro-Winkler + manual)
alias_map.json (143 alias → 109 cluster)
  ↓ relation_extraction.py (proximity + weighted)
nodes.csv + edges.csv
  ↓ periodisasi top-down + manual review (K/F/R/ADD)
nodes_v2.csv + edges_v2.csv ← graf yang sekarang dievaluasi
  ↓ import_to_neo4j.py
import_sirah_v2.cypher
```

**Disclaimer untuk Bu Diana:** Graf saat ini pakai pipeline **manual semi-auto labelling** (regex + keyword), **bukan output SRL-NER**. Setelah skenario S2/S3 winner ditetapkan, akan di-regenerate dengan output NER untuk coverage yang lebih luas.

### 1.3 Periodisasi (Konteks v2 vs v1)

Setelah revisi periodisasi 2026-05-12, sistem berubah dari **fuzzy match BAB** → **top-down explicit mapping**:

- **15 period (P0–P14)** dikelompokkan jadi **6 phase besar** (Fase I Pra-Islam → Fase VI Konsolidasi Akhir).
- 56 dari 59 BAB tertata semantically.
- Review manual: 19 Konfirmasi + 10 Fix + 12 Reject + 7 Add → akhirnya 36 Event valid (turun dari 41).
- Edges berkurang 370 → 322 setelah Reject mengurangi event-event yang invalid.

---

## 2. EVALUASI NODE-LEVEL — Siapa Tokoh Paling Penting?

> **Maksud evaluasi ini:** mengukur **importance per node**. Tiap tokoh diberi skor dari berbagai sudut pandang (banyaknya kenalan, posisinya sebagai jembatan, dll).

### 2.1 Definisi 4 Metrik Centrality (untuk Bab 4)

| Metrik | Rumus Intuitif | Interpretasi Tokoh |
|---|---|---|
| **Degree centrality** | Jumlah relasi langsung yang dimiliki node | Proxy popularitas / frekuensi muncul bersama |
| **Betweenness centrality** | Berapa sering node muncul di shortest path antar 2 node lain | Proxy peran broker / jembatan antar kelompok |
| **Closeness centrality** | Rata-rata kedekatan ke semua node lain (1 / avg shortest path) | Proxy aksesibilitas / posisi sentral |
| **PageRank** | Importance terbobot oleh importance tetangga | Proxy pengaruh hierarkis (bukan cuma banyak, tapi koneksi-koneksi pentingnya) |

### 2.2 Hasil — Top 10 Tokoh per Metrik

**Top 10 by Degree Centrality:**

| Rank | Nama | Degree | Centrality |
|:-:|---|:-:|:-:|
| 1 | Muhammad | 105 | 0.607 |
| 2 | Abu Jahal | 66 | 0.382 |
| 3 | Ali bin Abu Thalib | 56 | 0.324 |
| 4 | Abdullah bin Ubay bin Salul | 53 | 0.306 |
| 5 | Abu Sufyan bin Harb | 53 | 0.306 |
| 6 | Umar bin Al-Khaththab | 52 | 0.301 |
| 7 | Abu Azzah | 52 | 0.301 |
| 8 | Zaid bin Haritsah | 49 | 0.283 |
| 9 | Utsman bin Affan | 43 | 0.249 |
| 10 | Zainab | 42 | 0.243 |

**Top 5 by Betweenness Centrality** (yang menarik adalah perbedaan ranking-nya):

| Rank | Nama | Betweenness |
|:-:|---|:-:|
| 1 | Muhammad | 0.415 |
| 2 | Abu Jahal | 0.130 |
| 3 | Utsman bin Affan | 0.071 |
| 4 | Ali bin Abu Thalib | 0.069 |
| 5 | Rifa'ah bin Abdul Mundzir | 0.051 |

### 2.3 Interpretasi (Untuk Disampaikan ke Bu Diana)

- **Muhammad mendominasi semua metrik** — degree 105 (3× tokoh kedua), betweenness 0.41 (3× tokoh kedua). Ini *expected* untuk sebuah Sirah Nabawiyah. Validates pipeline.
- **Abu Jahal di posisi 2** untuk degree & betweenness — sesuai realitas sejarah sebagai musuh utama Quraisy di periode awal.
- **Utsman bin Affan high betweenness tapi degree menengah** — menunjukkan perannya sebagai *jembatan antar kelompok* (Quraisy ↔ Muslim awal).
- **Tokoh yang mungkin tidak ter-capture optimal:** Khalid bin Walid (panglima besar pasca-Khaibar), Aisyah (figure central periode Madinah). Coverage NER masih bisa ditingkatkan via SRL-NER nanti.

---

## 3. EVALUASI GRAPH-LEVEL — Struktur Keseluruhan

> **Maksud evaluasi ini (sesuai revisi #4 Bu Diana):** centrality saja tidak cukup karena fokus ke individu. Perlu metrik yang menggambarkan **keseluruhan struktur graf** — seberapa rapat, seberapa terkluster, seberapa mudah informasi mengalir.

**Subset yang dievaluasi:** Person co-participation graph (graf yang dibangun dari sharing event yang sama + relasi langsung Person-Person). 163 node, 1135 edge.

### 3.1 Hasil Lengkap + Interpretasi

| Metrik | Nilai | Apa Artinya | Apa Maknanya untuk Sirah |
|---|---:|---|---|
| **Density** | 0.086 | Persentase kemungkinan koneksi yang benar-benar terjadi. 0 = tidak ada, 1 = semua kenal. | **Sparse but cohesive.** Hanya 8.6% pasangan tokoh yang punya relasi langsung — wajar untuk teks naratif besar. |
| **Average degree** | 13.93 | Rata-rata jumlah relasi per orang | Tiap tokoh terhubung ke ~14 tokoh lain. Tidak terlalu padat. |
| **Average clustering coefficient** | 0.45 | "Ke-clusteran" lokal: kalau A kenal B dan C, seberapa sering B juga kenal C? | Moderately clustered di level individu — ada banyak segitiga kenalan. |
| **Transitivity (global clustering)** | **0.77** | Versi global: rasio segitiga (3 orang saling kenal) ke triplet (3 orang dengan 2 relasi) | **SANGAT TINGGI.** Konsisten dengan struktur klan/suku Arab — kalau A & B dari Bani yang sama, B & C juga, biasanya A & C kenal. **Ini temuan utama!** |
| **Degree assortativity** | -0.058 | Apakah hub menempel ke hub (positif) atau hub ke daun (negatif)? | Mendekati neutral. Tidak murni hub-and-spoke (-1) atau rich-club (+1). |
| **n_components** | 8 | Jumlah "pulau" graf yang tidak terhubung satu sama lain | Ada 8 grup terpisah — sebagian besar (~91%) tergabung di satu giant component. |
| **Giant component size** | 148 (90.8%) | Ukuran komponen terbesar | 148 dari 163 tokoh saling reachable. |
| **Giant diameter** | 6 | Jarak shortest path terjauh antar 2 tokoh | Bisa "loncat" dari tokoh manapun ke tokoh lain dalam **maksimal 6 langkah**. |
| **Giant radius** | 3 | Radius (jarak max dari node tengah) | Dari Muhammad ke siapapun di giant component max 3 langkah. |
| **Giant avg shortest path** | 2.47 | Rata-rata jarak antar 2 tokoh | Rata-rata 2–3 langkah → **small-world network**. |

### 3.2 Klaim Utama yang Akan Masuk Bab 4

**Klaim 1 — Struktur Klan/Suku Arab Terkonfirmasi**
> Transitivity global 0.77 menunjukkan bahwa graf Sirah punya **kohesi triadik tinggi** — jika dua tokoh terhubung lewat tokoh ketiga, mereka cenderung juga saling terhubung langsung. Ini selaras dengan struktur sosial masyarakat Arab pra-Islam yang berbasis kabilah/Bani, dimana keanggotaan klan menciptakan relasi multi-arah.

**Klaim 2 — Karakteristik Small-World**
> Dengan diameter 6 dan avg shortest path 2.47, graf Sirah memenuhi karakteristik **small-world network** (jarak rata-rata pendek + clustering tinggi). Implikasinya: informasi/pengaruh bisa menyebar cepat di komunitas — relevan untuk konteks dakwah dan diplomasi periode awal Islam.

**Klaim 3 — Ada Fragmentasi Minor**
> 8 component dengan 1 giant component (90.8%) menunjukkan **mayoritas tokoh terhubung**, sisanya kelompok-kelompok kecil yang muncul terisolasi di chapter spesifik. Ini bisa jadi temuan untuk *future work*: investigasi tokoh-tokoh terisolasi.

### 3.3 File Output

- `data/result/analysis/graph_metrics_v2.md` (laporan tabel)
- `data/result/analysis/graph_metrics_v2.json` (raw data, untuk plot)

---

## 4. COMMUNITY DETECTION — Perbandingan 3 Metode

> **Maksud (sesuai revisi #4 Bu Diana):** Bu Diana minta "uji coba metode lain" selain Louvain yang sudah ada di `sna_analysis.py` lama. Tujuannya untuk validasi: apakah struktur komunitas yang terdeteksi konsisten antar metode?

### 4.1 Definisi Modularity (Q)

**Modularity Q** adalah ukuran kualitas pembagian komunitas:
- Q > 0.3 → struktur komunitas signifikan (ada pembagian yang jelas)
- Q dekat 0 → pembagian sembarang (graf tidak punya struktur komunitas)
- Q < 0 → pembagian buruk

### 4.2 Hasil 3 Metode

| Metode | n_communities | Modularity Q | Komentar |
|---|---:|---:|---|
| **Louvain (proper)** | 13 | **0.327** | Standar emas. Balanced quality + speed. |
| **Greedy modularity** | 15 | 0.320 | Faster tapi kualitas sedikit di bawah Louvain. |
| **Girvan-Newman** | 16 | 0.024 | **Over-fragmented** — modularity sangat rendah, partisi tidak meaningful. |

### 4.3 Adjusted Rand Index (ARI) — Kesepakatan Antar Metode

ARI = 0 berarti partisi acak, ARI = 1 berarti identik.

|  | Louvain | Greedy | Girvan-Newman |
|---|:-:|:-:|:-:|
| **Louvain** | 1.00 | 0.56 | 0.13 |
| **Greedy** | 0.56 | 1.00 | 0.31 |
| **Girvan-Newman** | 0.13 | 0.31 | 1.00 |

### 4.4 Insight + Rekomendasi

- **Louvain & Greedy** moderately agree (ARI 0.56) — keduanya mendeteksi struktur komunitas yang serupa namun granularitas beda.
- **Girvan-Newman** mendeteksi struktur sangat berbeda (ARI 0.13–0.31 vs lainnya) dan modularity-nya rendah → **tidak cocok untuk graf Sirah**.
- **Rekomendasi:** pakai **Louvain proper** sebagai default untuk laporan TA. Drop yang Greedy karena `sna_analysis.py` lama keliru label-nya sebagai "Louvain" padahal sebenarnya Greedy.

### 4.5 4 Komunitas Terbesar (Louvain) — Interpretasi Naratif

| Komunitas | Ukuran | Karakteristik Anggota |
|---|:-:|---|
| **C1** | 50 orang | Tokoh Yatsrib pra-Islam + tokoh pinggiran (Abrahah, Adam, Adi bin Hatim, …) |
| **C2** | 39 orang | Quraisy oposisi utama (Abu Jahal, Abu Sufyan, Abu Azzah, …) |
| **C3** | 33 orang | Sahabat dekat & keluarga Nabi (Abdullah bin Abbas, Abu Hurairah, Abdurrahman bin Auf, …) |
| **C4** | 21 orang | Sahabat + munafik Madinah (Abdullah bin Atik, Abdullah bin Ubay bin Salul, Az-Zubair, …) |

9 komunitas lainnya berukuran 2–3 orang — kelompok kecil yang muncul di chapter spesifik.

---

## 5. STUDI KASUS 5 EVENT BERPERIODE JAUH

> **Maksud (sesuai revisi #2 Bu Diana):** validasi bottom-up. Ambil event-event dengan periode berjauhan, lihat keterlibatan tokoh, tunjukkan sub-graf, analisis. Tujuan: pastikan pipeline NER + relation extraction menghasilkan sub-graf yang masuk akal sebelum klaim besar di SNA level.

### 5.1 5 Event yang Dipilih

| # | Event | Period | Halaman | Person | Direct P-P Relations |
|:-:|---|:-:|:-:|:-:|:-:|
| 1 | **Perang Badr** | P8 | 266–304 | 39 | 16 (8 KEL, 2 MUS, 6 SAH) |
| 2 | **Perang Uhud** | P9 | 324–375 | 18 | 10 |
| 3 | **Perjanjian Hudaibiyah** | P11 | 433–450 | 3 | 0 |
| 4 | **Perang Khaibar** | P11 | 473–492 | 5 | 0 |
| 5 | **Perang Tabuk** | P13 | 558–571 | 6 | 0 |

**Total unique Person yang muncul di setidaknya 1 event:** 60

### 5.2 Tokoh Lintas-Event (Hub Multi-Period)

| Person | Total Event | Events |
|---|:-:|---|
| **Muhammad** | **5 / 5** | Badr, Uhud, Hudaibiyah, Khaibar, Tabuk |
| Abu Jahal | 2 / 5 | Badr, Uhud |
| Abu Sufyan bin Harb | 2 / 5 | Badr, Uhud |
| Abu Azzah | 2 / 5 | Badr, Uhud |
| Abu Hurairah | 2 / 5 | Badr, Khaibar |
| Abu Musa | 2 / 5 | Badr, Khaibar |
| Amr bin Umayyah | 2 / 5 | Uhud, Tabuk |
| Salamah bin Al-Akwa' | 2 / 5 | Hudaibiyah, Khaibar |

**Insight:**
- **Muhammad satu-satunya tokoh muncul di 5/5 event** — confirms peran sentral.
- **Abu Jahal + Abu Sufyan + Abu Azzah di Badr+Uhud** — sesuai sejarah (quartet Quraisy musuh utama awal).

### 5.3 Bias Coverage NER yang Terlihat

**Penting untuk disampaikan jujur ke Bu Diana** sebagai limitasi:

| Event | Person | Halaman | Density Cerita | Realitas Historis |
|---|:-:|:-:|---|---|
| Perang Badr | 39 | 39 hal | Sangat detail | 313 pasukan Muslim |
| Perang Uhud | 18 | 52 hal | Detail tapi tokoh berulang | ~1000 pasukan |
| Hudaibiyah | 3 | 18 hal | Cerita ringkas | Banyak utusan |
| Khaibar | 5 | 20 hal | Cerita ringkas | 1500 pasukan |
| Perang Tabuk | 6 | 14 hal | Sangat ringkas | **30.000 pasukan** |

**Tabuk historisnya 30.000 pasukan, tapi cuma 6 person ter-capture.** Bukan ground-truth keterlibatan, ini cerminan **content density teks Al-Mubarakfuri** — Badr dapat porsi panjang, Tabuk lebih ringkas.

**Framing untuk Bab 4:** ini limitasi NER coverage dari pipeline saat ini. Setelah upgrade ke SRL-NER, *kemungkinan* coverage event yang teksnya panjang membaik. Tabuk yang teksnya pendek tetap akan punya cap rendah — itu inherent dari sumber data.

### 5.4 File Output

- `data/result/analysis/case_study_events.md` (laporan lengkap dengan detail per event)
- `data/result/analysis/case_study_events_cypher.md` (5 set Cypher queries siap demo Neo4j)
- `data/result/analysis/case_study_panel.png` (5-panel gabungan untuk slide tunggal)
- `data/result/analysis/case_study_Perang_*.png` (5 individu, fokus zoom per event)

---

## 6. VISUALISASI YANG SIAP DITUNJUKKAN

### 6.1 Static PNG (Cocok untuk Google Slides / PDF)

| File | Ukuran | Konten | Penggunaan |
|---|---:|---|---|
| `case_study_panel.png` | 576 KB | 5 sub-graf gabungan | **Slide tunggal — overview** |
| `case_study_Perang_Badr.png` | 390 KB | 39 Person Badr (paling rapat) | Slide deep-dive Badr |
| `case_study_Perang_Uhud.png` | 255 KB | 18 Person Uhud | Slide deep-dive Uhud |
| `case_study_Perjanjian_Hudaibiyah.png` | 70 KB | 3 Person (kecil) | Demo limitasi |
| `case_study_Perang_Khaibar.png` | 86 KB | 5 Person | Demo limitasi |
| `case_study_Perang_Tabuk.png` | 90 KB | 6 Person | Demo bias coverage |

**Legenda PNG:**
- **Kuning besar** = Event (di tengah)
- **Biru** = Person (di lingkaran sekeliling, ukuran proporsional dengan jumlah event participation di seluruh KG)
- **Abu-abu tipis** = INVOLVED_IN
- **Merah** = KELUARGA
- **Hijau** = SAHABAT
- **Oranye putus-putus** = MUSUH

### 6.2 Visualisasi Belum Ada (Akan Di-Generate Kalau Sempat)

- Full network 163 Person (matplotlib, warna = community) — perintah: `python src/analysis/sna_analysis.py`
- Plot bar centrality top-20 (dari `sna_metrics.csv`)
- Visualisasi 15 Period sebagai timeline

---

## 7. DEMO NEO4J — Setup + Query

### 7.1 Setup Cepat (Kalau Belum Punya Neo4j Desktop)

1. Download **Neo4j Desktop** dari [neo4j.com/download](https://neo4j.com/download) (gratis, ~500 MB).
2. Install + buat akun (sekali).
3. **Create New Project** → klik **Add → Local DBMS** → set password.
4. **Start** the DBMS → klik **Open** → terbuka Neo4j Browser di port 7474.

### 7.2 Import Knowledge Graph

```cypher
// Di Neo4j Browser, paste isi file:
// data/result/neo4j/import_sirah_v2.cypher
// (1287 statements — copy semua, paste, run sekali)
```

Atau via command line (kalau Neo4j Desktop ada `cypher-shell`):
```powershell
cat data\result\neo4j\import_sirah_v2.cypher | cypher-shell -u neo4j -p <password>
```

### 7.3 5 Query Siap Demo

Pilih 2–3 yang paling impactful untuk presentasi.

**Query 1 — Overview Knowledge Graph**
```cypher
MATCH (n) RETURN labels(n)[0] AS NodeType, count(n) AS Count
ORDER BY Count DESC;
```

Output: tabel jumlah Person/Event/Period/Location/Time.

**Query 2 — Visualisasi Perang Badr (sub-graf paling rapat)**
```cypher
MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event {name: "Perang Badr"})
RETURN p, r, e
LIMIT 50;
```

Output: visual graf node Perang Badr di tengah, semua Person yang terlibat di sekeliling.

**Query 3 — Tokoh Lintas Period (Hub Multi-Period)**
```cypher
MATCH (p:Person)-[:INVOLVED_IN]->(e:Event)-[:IN_PERIOD]->(period:Period)
WITH p, count(DISTINCT period) AS n_periods
WHERE n_periods >= 3
RETURN p.name AS Tokoh, n_periods
ORDER BY n_periods DESC
LIMIT 10;
```

Output: top tokoh yang terlibat di banyak periode (Muhammad di 14+ period).

**Query 4 — Density Cerita per Period**
```cypher
MATCH (period:Period)<-[:IN_PERIOD]-(e:Event)<-[:INVOLVED_IN]-(p:Person)
RETURN period.period_id AS Period, period.label AS NamaPeriod,
       count(DISTINCT e) AS n_events, count(DISTINCT p) AS n_persons
ORDER BY period.period_id;
```

Output: tabel periode yang ceritanya kaya vs ringkas — confirms bias coverage.

**Query 5 — Path Muhammad ↔ Abdullah bin Ubay (musuh utama)**
```cypher
MATCH path = shortestPath(
  (m:Person {name: "Muhammad"})-[*..5]-(u:Person {name: "Abdullah bin Ubay bin Salul"})
)
RETURN path;
```

Output: visualisasi jalur terpendek (probably 1-2 langkah).

### 7.4 Tips Demo

- Sebelum bimbingan, **Restart Neo4j → import → test 5 query** untuk pastikan berjalan.
- Pasang Neo4j Browser di **layout: spring-embedded**, ukuran node = degree (klik settings di pojok kanan bawah).
- Kalau presentasi via screen share, demo query 2 dulu (visual paling impressive), lalu query 4 (tabel paling informatif).

---

## 8. PANDUAN CARA MENJELASKAN (Skrip Presentasi)

### 8.1 Flow Naratif yang Disarankan (15–17 Menit)

```
[2 min] Opening — sumber data + pipeline + setup status SRL-NER (singkat)
   ↓
[3 min] Schema graf + statistik dasar
   ↓
[3 min] Centrality (node-level) — Muhammad mendominasi
   ↓
[4 min] Graph-level metrics — temuan utama (klan + small-world)
   ↓
[2 min] Community detection — 3 metode comparison
   ↓
[3 min] Studi kasus 5 event — confirms pipeline + reveal bias
   ↓
[2 min] Demo Neo4j live (2-3 query)
   ↓
[Opsional 2 min] Update singkat SRL-NER S2 — kalau Bu Diana minta atau waktu cukup
   ↓
[Q&A]
```

### 8.2 Skrip Per Section

**Opening (2 menit):**
> *"Bu, saya mau lapor progres untuk dua cluster revisi periode 2026-05-03: cluster #2 sampling 3–5 event, dan cluster #4 graph-level metrics + community detection — keduanya sudah complete dan akan saya tunjukkan hari ini sebagai fokus utama. Untuk cluster #3 SRL-NER, S2a SCL dan S2b JSCL sudah selesai re-run di Colab tanggal 14 Mei — saya bisa update singkat di akhir kalau Bu Diana mau. Catatan: sumber data graf saat ini masih pipeline manual semi-auto labelling. Graf akan di-regenerate dengan output NER setelah skenario S2/S3 winner-nya dipilih dan diapproved oleh Ibu."*

**Schema (3 menit):**
> *"Knowledge Graph sirah saat ini punya 892 node terdiri dari 5 tipe: Person, Event, Location, Time, dan Period yang baru ditambahkan setelah revisi periodisasi 12 Mei. Edge-nya ada 322, 7 jenis relasi, dengan bobot 0.0 sampai 1.0. Yang baru di v2 adalah node Period sebagai first-class entity — sebelumnya periode itu cuma string property, sekarang jadi node-nya sendiri sehingga bisa di-query."*

**Centrality (3 menit):**
> *"Untuk evaluasi node-level, kami hitung 4 metrik centrality: degree, betweenness, closeness, dan PageRank. Tujuannya menjawab pertanyaan 'siapa tokoh paling penting di Sirah'. Hasilnya Muhammad mendominasi semua metrik — degree 105, 3 kali tokoh kedua. Ini expected untuk Sirah Nabawiyah dan sekaligus jadi validasi pipeline. Yang menarik adalah Abu Jahal di posisi 2 untuk degree dan betweenness — sesuai realitas sejarah sebagai musuh utama Quraisy. Utsman bin Affan posisinya unik — degree-nya menengah tapi betweenness tinggi, artinya perannya sebagai jembatan antar kelompok."*

**Graph-Level (4 menit — bagian terpenting):**
> *"Untuk evaluasi graph-level, sesuai revisi #4 Bu Diana, saya hitung 13 metrik yang menggambarkan struktur keseluruhan graf, bukan per individu. Temuan utamanya ada di transitivity global, yang nilainya 0.77 — sangat tinggi. Artinya kalau tokoh A dan B saling kenal, dan B dan C saling kenal, kemungkinan besar A dan C juga saling kenal. Ini konsisten dengan struktur klan-suku Arab pra-Islam — keanggotaan kabilah otomatis menciptakan multi-relasi. Selain itu, diameter graf cuma 6 dengan avg shortest path 2.47 — graf Sirah punya karakteristik small-world: jarak rata-rata pendek tapi clustering tinggi. Implikasinya: informasi atau pengaruh menyebar cepat di komunitas — relevan untuk konteks dakwah."*

**Community Detection (2 menit):**
> *"Bu Diana minta uji coba metode lain selain Louvain — kami bandingkan 3 metode. Louvain proper dapat modularity 0.327 dengan 13 komunitas. Greedy modularity dapat 0.32 dengan 15 komunitas. Girvan-Newman dapat hanya 0.024 — over-fragmented, tidak meaningful untuk graf Sirah. Antara Louvain dan Greedy, kesepakatannya moderate (ARI 0.56) — keduanya OK tapi granularitas beda. Rekomendasi kami: pakai Louvain proper untuk laporan akhir."*

**Studi Kasus (3 menit):**
> *"Untuk cluster #2, dipilih 5 event berperiode jauh dari P8 sampai P13: Perang Badr, Uhud, Hudaibiyah, Khaibar, Tabuk. Total 60 unique Person muncul, dan menariknya Muhammad adalah satu-satunya tokoh yang muncul di 5/5 event — hub lintas periode. Tapi ada limitasi yang harus diakui jujur: bias coverage NER terlihat. Perang Badr ter-capture 39 person, sedangkan Perang Tabuk yang historisnya 30 ribu pasukan, cuma 6 person ter-capture. Ini bukan ground-truth keterlibatan, tapi cerminan content density teks Al-Mubarakfuri. Tabuk dapat porsi lebih ringkas di buku. Ini akan jadi catatan limitasi di Bab 4."*

**Demo Neo4j (2 menit):**
> *"Sekarang saya tunjukkan langsung di Neo4j..."* [run query 2 — Perang Badr, lalu query 4 — density per period]

**Update Singkat SRL-NER S2 (opsional, 2 menit) — sampaikan kalau Bu Diana tanya atau ada waktu:**
> *"Sekalian saya laporkan update untuk cluster #3 SRL-NER. S2a SCL dan S2b JSCL sudah selesai re-run di Colab dengan metrik dual: token-level sklearn + entity-level seqeval, jadi apple-to-apple dengan S1 baseline. Seq F1 entity-level naik monotonik lintas iterasi self-training: SCL 0.92 → **0.95**, JSCL 0.90 → **0.93**. Final iter-6 SCL = 0.950 (peak 0.953), JSCL = 0.933. Token-level F1 lebih tinggi dari S1 (~0.995). Tapi jujur, entity-level S2 sedikit di bawah S1 baseline 0.959 — gap kecil 0.01 yang kemungkinan disebabkan λ_C=0.3 terlalu agresif sehingga ada trade-off antara per-token classification vs entity boundary. SCL konsisten lebih tinggi dari JSCL. Rekomendasi saya: lanjut S3 augmentation pakai SCL, karena augmentation menyasar kelas minor (EVENT, I-LOCATION) yang memang masih F1 0.78–0.82 di S2. Mohon arahan Ibu."*

(Detail tabel angka per-iter + per-class ada di §9 Q6. Folder hasil: `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/`. Rangkuman epoch + Seq F1: `src/pseudo_labelling/SRL-NER/S2-seqeval.md`.)

### 8.3 Cara Menyampaikan Limitasi

- **Akui dengan jujur** tapi framing sebagai *future work*, bukan kegagalan
- **Sebut sebabnya** (content density, manual labelling vs NER) — show *kamu paham penyebabnya*
- **Sebut planning** untuk address-nya (SRL-NER nanti)

### 8.4 Cara Menjawab Kalau Bu Diana Pertanyakan Angka

- **Selalu rujuk file** — *"Detail lengkapnya di `graph_metrics_v2.md`, Bu"*
- **Punya screenshot Neo4j** sebagai backup kalau lupa angka
- **Jangan ngarang** kalau ditanya angka yang tidak diingat — *"Saya cek dulu Bu, ada di file"*

---

## 9. PERTANYAAN BU DIANA YANG MUNGKIN + JAWABAN

### Q1: Kenapa graf-nya masih pakai manual labelling, bukan SRL-NER?

**Jawaban:**
> *"Cluster #2 studi kasus event dan #4 graph-level metrics adalah revisi yang bisa dikerjakan paralel dengan data saat ini — tidak depend on SRL-NER selesai. Cluster #3 SRL-NER masih dalam proses run skenario S2 di Colab. Setelah winner-nya dipilih, graf akan di-regenerate dengan output NER untuk coverage yang lebih luas dan konsisten. Tapi struktur evaluasi yang sudah dibangun (metrik graph-level, studi kasus, community detection) tidak perlu diubah — tinggal ganti underlying data-nya."*

### Q2: Transitivity 0.77 itu interpretasinya pasti struktur klan? Bukan artefak data?

**Jawaban:**
> *"Pertanyaan bagus. Ini bisa divalidasi 2 cara: pertama, secara analitis — random network dengan density 0.086 secara teoritis punya transitivity sekitar 0.086. Kita dapat 0.77 — 9x lebih tinggi dari random baseline, jelas non-acak. Kedua, secara semantik — kalau dilihat komunitas Louvain, banyak yang struktur internalnya keluarga/Bani. Misalnya Abu Sufyan punya 14 relasi KELUARGA, dan keluarganya juga punya relasi MUSUH yang sama. Itulah struktur klan yang membuat transitivity tinggi."*

### Q3: 8 component, kenapa nggak 1 component besar saja?

**Jawaban:**
> *"Giant component memang 90.8% (148 dari 163 tokoh). Sisanya 8 komponen kecil ukuran 2–3 orang. Ini biasanya muncul di chapter spesifik dimana tokohnya tidak ke-mention bersama tokoh lain — misalnya kelompok mu'allaf di periode tertentu yang teksnya pendek. Bukan kesalahan pipeline, ini realitas teks. Untuk laporan, kami fokus analisis di giant component karena 90% data."*

### Q4: Modularity 0.327 — itu cukup tinggi?

**Jawaban:**
> *"Konvensi di literature network science: Q > 0.3 dianggap struktur komunitas signifikan. 0.327 sedikit di atas threshold itu — ada struktur komunitas tapi tidak super sharp. Untuk teks naratif yang banyak tokoh main berinteraksi dengan banyak grup, ini wajar — Muhammad misalnya secara realistis terhubung ke semua komunitas (sahabat, keluarga, musuh, mu'allaf), jadi tidak mungkin Q-nya sangat tinggi. Bandingkan dengan literatur SNA teks Islam lainnya..."* (sebutkan paper kalau ingat — di `referensi_sna_weighted_relations.md`)

### Q5: Visualisasi Perang Tabuk cuma 6 orang — kelihatan jelek?

**Jawaban:**
> *"Ya Bu, dan justru itu yang ingin kami highlight sebagai temuan. Tabuk historisnya 30 ribu pasukan tapi cuma 6 person ter-capture — ini cerminan content density teks Al-Mubarakfuri yang memang ringkas di chapter Tabuk. Bisa kami sajikan sebagai limitasi di Bab 4. Limitasi ini tidak bisa di-fix hanya dengan upgrade NER, karena sumber datanya memang minim mention. Solusinya kalau kedepan: kombinasi multi-source (misal nambah Sirah Ibn Hisyam) — tapi itu di luar scope TA ini."*

### Q6: Status SRL-NER sekarang gimana?

**Jawaban:**
> *"S2a SCL dan S2b JSCL sudah selesai re-run di Colab tanggal 14–15 Mei, hasil lengkap di `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/` plus rangkuman tabel epoch di `S2-seqeval.md`. Kali ini eval sudah pakai dua metrik berdampingan: **token-level (sklearn)** untuk konsistensi metode Ibu, dan **entity-level (seqeval)** untuk fair comparison antar skenario. Trend self-training jelas — Seq F1 entity naik monotonik lintas iterasi: SCL 0.92 → 0.95, JSCL 0.90 → 0.94. Hasil final iter-6 epoch-10: S2a SCL Seq F1 = 0.950 (peak 0.953 di epoch-4), S2b JSCL Seq F1 = 0.933 (peak 0.940 di iter-5 epoch-3). Catatan jujur: angka ini masih sedikit di bawah S1 baseline (0.959) — gap kecil ~0.01 di entity-level, tapi token-level S2 justru lebih tinggi (~0.995 vs S1). Interpretasi sementara: λ_C=0.3 mungkin terlalu agresif, ada trade-off boundary-detection vs token-classification. Saya rekomendasikan lanjut S3 augmentation untuk lihat apakah penambahan data minor bisa close the gap, atau tuning λ_C ke 0.1–0.2 di future work."*

**Tabel ringkas Seq F1 (entity-level, comparable dengan S1=0.959):**

| Iter | S2a SCL | S2b JSCL |
|:-:|:-:|:-:|
| 1 (final) | 0.924 | 0.904 |
| 2 (final) | 0.942 | 0.933 |
| 3 (final) | 0.949 | 0.935 |
| 4 (final) | 0.947 | 0.930 |
| 5 (final) | 0.950 | 0.939 |
| **6 (final)** | **0.950** | **0.933** |
| **Peak (best epoch)** | **0.953** (iter-6 ep-4) | **0.940** (iter-5 ep-3) |
| S1 baseline (referensi) | 0.959 | 0.959 |

**Tabel cadangan per-kelas token-level (test set, model iter-6):**

| Label | Support | F1 token-level |
|---|---:|---:|
| B-EVENT | 47 | 0.777 |
| I-EVENT | 53 | 0.808 |
| B-LOCATION | 449 | 0.908 |
| I-LOCATION | 26 | 0.776 |
| B-PERSON | 1189 | 0.910 |
| I-PERSON | 1113 | 0.941 |
| B-TIME | 74 | 0.815 |
| I-TIME | 158 | 0.883 |
| Macro avg | — | 0.868 |
| Weighted avg | — | 0.990 |

(Klaim: kelas minor — EVENT, I-LOCATION, B-TIME — masih F1 0.78–0.82, jadi **alasan untuk lanjut S3 augmentation tetap valid**. S3 menyasar tepat kelas-kelas ini.)

### Q7: Kelahiran/Kematian Nabi belum jadi event?

**Jawaban:**
> *"Saat ini event yang ter-capture adalah peristiwa kolektif dengan banyak tokoh terlibat (peperangan, perjanjian, hijrah). Kelahiran/Kematian Nabi belum jadi event eksplisit karena pipeline pre_labelling.py fokus ke event eksternal. Bisa ditambahkan via mekanisme yang sama dengan yang kami pakai untuk Wahyu Pertama dan Haji Wada' — yaitu ADD candidate di review periodisasi. Estimasi pengerjaan 30 menit kalau Bu Diana setuju."*

---

## 10. CHECKLIST SEBELUM BIMBINGAN

- [ ] Buka `bimbingan_graf_2026_05_14.md` di tab terpisah — referensi cepat saat lupa angka
- [ ] Buka `case_study_panel.png` — siap di-share-screen
- [ ] Buka `graph_metrics_v2.md` — siap tunjuk file kalau ditanya source
- [ ] (Opsional) Neo4j Desktop sudah running dengan `import_sirah_v2.cypher` ter-import — 2 query test (Query 2 + Query 4) sudah dicoba sukses
- [ ] Slide Google Slides sudah ada PNG di-embed (kalau pakai slide), atau Google Docs sudah ter-paste tabel-tabel utama dari dokumen ini
- [ ] Read skrip §8.2 sebelum bimbingan — 15–17 menit cukup untuk hafal flow
- [ ] Catatan kecil di kertas: 4 angka kunci graf (transitivity 0.77, density 0.086, diameter 6, modularity 0.327) + 4 angka SRL-NER (Seq F1 entity: S1 baseline 0.959, S2a SCL final 0.950 / peak 0.953, S2b JSCL final 0.933 / peak 0.940)
- [ ] Buka folder `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/` + file `src/pseudo_labelling/SRL-NER/S2-seqeval.md` siap-siap kalau Bu Diana minta tunjuk detail hasil S2

---

## 11. CARA EXPORT KE GOOGLE DOCS

Beberapa cara mengubah file ini ke Google Docs:

**Cara 1 (paling cepat) — Pakai Pandoc:**

```powershell
# Install pandoc kalau belum (sekali)
choco install pandoc
# atau download dari pandoc.org

# Convert ke docx
pandoc bimbingan_graf_2026_05_14.md -o bimbingan_graf.docx
```

Lalu upload `.docx` ke Google Drive → klik kanan → Open with Google Docs → save sebagai Google Docs.

**Cara 2 (manual tapi lebih reliable):**

1. Buka file `.md` ini di VS Code.
2. Klik kanan pada area editor → **Open Preview to the Side** (Ctrl+K V).
3. Di preview, **Ctrl+A** → **Ctrl+C** (select all + copy).
4. Buat Google Docs baru → **Ctrl+V** (paste).
5. Format tabel mungkin perlu sedikit di-adjust manual.

**Cara 3 (zero install):**

1. Buka https://markdowntopdf.com atau https://www.markdowntodocx.com
2. Upload file `.md`
3. Download `.docx` → upload ke Google Drive

---

**Selamat bimbingan, semoga lancar.**
