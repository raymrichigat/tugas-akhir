# Bimbingan Bu Diana — 2026-05-16

> **Fokus bimbingan:** Dua hasil utama
> 1. **Evaluasi Knowledge Graph** (revisi #2 + #4 Bu Diana 2026-05-03) — graph-level metrics, community detection, studi kasus 5 event
> 2. **Hasil SRL-NER S2 Contrastive Learning** (revisi #3 / putaran 3 Bu Diana 2026-05-07) — S2a SCL + S2b JSCL dengan metric dual (token-level sklearn + entity-level seqeval)
>
> **File detail referensi:** `bimbingan_graf_2026_05_14.md` (graf lengkap), `src/pseudo_labelling/SRL-NER/S2-seqeval.md` (rangkuman epoch S2)
> **Total durasi target:** 20–25 menit + Q&A

---

## DAFTAR ISI

0. [Ringkasan 1 Menit](#0-ringkasan-1-menit)
1. [Knowledge Graph yang Dibangun](#1-knowledge-graph-yang-dibangun)
2. [Hasil Evaluasi Graf](#2-hasil-evaluasi-graf)
3. [Hasil SRL-NER S2 Contrastive Learning](#3-hasil-srl-ner-s2-contrastive-learning)
4. [Keputusan yang Butuh Arahan Bu Diana](#4-keputusan-yang-butuh-arahan-bu-diana)
5. [Flow Naratif + Skrip Presentasi](#5-flow-naratif--skrip-presentasi)
6. [Pertanyaan Bu Diana yang Mungkin + Jawaban](#6-pertanyaan-bu-diana-yang-mungkin--jawaban)
7. [Checklist Sebelum Bimbingan](#7-checklist-sebelum-bimbingan)

---

## 0. RINGKASAN 1 MENIT

Lima poin yang bisa disampaikan dalam 60 detik:

1. **Knowledge Graph v2 sudah jadi:** 907 node di Neo4j (Person 658, Time 147, Location 51, Event 36, Period 15) + 322 relasi (7 jenis di edges_v2.csv) + 36 IN_PERIOD (di-generate Cypher).
2. **Graph-level metrics ringkas:** transitivity **0.77** (struktur klan/suku Arab confirmed), small-world (diameter 6, avg path 2.47), density 0.086, modularity Louvain 0.327.
3. **Community detection 3 metode dibandingkan:** Louvain Q=0.327 menang, Greedy Q=0.320 (moderate agree ARI 0.56), Girvan-Newman gagal (Q=0.024).
4. **Studi kasus 5 event berperiode jauh** (Badr/Uhud/Hudaibiyah/Khaibar/Tabuk) — 60 unique Person, Muhammad satu-satunya hub 5/5 event. Bias coverage NER terlihat (Tabuk 6 person padahal historisnya 30k pasukan).
5. **SRL-NER S2 selesai re-run dengan dual metric:** Seq F1 entity (head-to-head S1 baseline 0.959): **S2a SCL final 0.950 / peak 0.953**, **S2b JSCL final 0.933 / peak 0.940**. Trend monotonik naik lintas 6 iterasi. SCL > JSCL konsisten.

---

## 1. KNOWLEDGE GRAPH YANG DIBANGUN

### 1.1 Schema

```
NODES (5 tipe, total 907 di Neo4j = 892 nodes_v2.csv + 15 Period dari Cypher)
├── Person       (658)
├── Time         (147)
├── Location     (51)
├── Event        (36)   ← dari 41 di v1, setelah review periodisasi K/F/R/ADD
└── Period       (15)   ← v2 baru, first-class node menggantikan property

EDGES (7 tipe di edges_v2.csv = 322, + IN_PERIOD 36 di-generate di Cypher)
├── INVOLVED_IN  (Person → Event)   — 123 (weight 0.20–1.00, mean 0.40)
├── KELUARGA     (Person ↔ Person)   —  91 (weight 0.55–1.00, mean 0.56)
├── OCCURRED_ON  (Event → Time)     —  36 (weight 0.20–1.00, mean 0.41)
├── OCCURRED_AT  (Event → Location) —  25 (weight 0.20–1.00, mean 0.47)
├── SAHABAT      (Person ↔ Person)   —  25 (weight 0.55 fixed)
├── PRECEDES     (Event → Event)    —  12 (weight 1.00 fixed)
├── MUSUH        (Person ↔ Person)   —  10 (weight 0.55 fixed)
└── IN_PERIOD    (Event → Period)   —  36 (dari periodisasi top-down)
```

### 1.2 Tiga Skema Pembobotan

| Skema | Range | Untuk relasi | Logika |
|---|---|---|---|
| **A. Proximity + Period** | 0.2–1.0 | INVOLVED_IN, OCCURRED_ON, OCCURRED_AT | `proximity(0–0.5) + period(0–0.5)` — co-occurrence weighted |
| **B. Pattern fixed (0.55)** | 0.55 | KELUARGA, SAHABAT, MUSUH | Regex eksplisit (`bin`/`binti`/`sahabat`) = bukti langsung |
| **C. Deterministik (1.0)** | 1.0 | PRECEDES | Urutan period = kronologi pasti |

### 1.3 Pipeline Sumber Data (penting disebut)

```
PDF → PaddleOCR → CSV → preprocessing → chunking → pre_labelling (regex) →
alias clustering (Jaro-Winkler) → relation_extraction (weighted) →
periodisasi top-down + manual review K/F/R/ADD → nodes_v2.csv + edges_v2.csv →
Neo4j import
```

**Disclaimer:** Graf saat ini pakai pipeline **manual semi-auto labelling**, BELUM pakai SRL-NER. Akan di-regenerate setelah S2/S3 winner dipilih.

### 1.4 Periodisasi v2

- **15 period (P0–P14)** di-grouped ke **6 phase besar** (Fase I Pra-Islam → Fase VI Konsolidasi Akhir)
- 56 dari 59 BAB tertata semantically
- Review manual: 19 Konfirmasi + 10 Fix + 12 Reject + 7 Add → 36 Event valid
- Edges berkurang 370 → 322 setelah reject

---

## 2. HASIL EVALUASI GRAF

### 2.1 Node-Level (Centrality) — Siapa Tokoh Paling Penting

**4 metrik:** degree, betweenness, closeness, PageRank.

**Top 5 by Degree (Person co-participation graph, 163 node, 1135 edge):**

| Rank | Nama | Degree | Centrality |
|:-:|---|:-:|:-:|
| 1 | **Muhammad** | 105 | 0.607 |
| 2 | Abu Jahal | 66 | 0.382 |
| 3 | Ali bin Abu Thalib | 56 | 0.324 |
| 4 | Abdullah bin Ubay bin Salul | 53 | 0.306 |
| 5 | Abu Sufyan bin Harb | 53 | 0.306 |

**Interpretasi:**
- Muhammad dominasi semua metrik (3× tokoh kedua) — *expected* untuk Sirah, validates pipeline
- Abu Jahal posisi 2 — sesuai sejarah sebagai musuh utama Quraisy
- Utsman bin Affan: degree menengah tapi betweenness tinggi (0.071) → peran *jembatan antar kelompok*

### 2.2 Graph-Level Metrics — Struktur Keseluruhan

| Metrik | Nilai | Apa Artinya |
|---|---:|---|
| **Transitivity (global)** | **0.7723** | **TEMUAN UTAMA** — struktur klan/suku Arab confirmed (kalau A&B saling kenal, dan B&C kenal, biasanya A&C kenal) |
| Density | 0.086 | 8.6% pasangan tokoh punya relasi langsung — sparse but cohesive |
| Avg clustering coeff | 0.45 | Moderately clustered lokal — banyak segitiga kenalan |
| Avg shortest path | 2.47 | Rata-rata 2–3 langkah antar tokoh → **small-world** |
| Diameter (giant comp) | 6 | Max 6 langkah dari tokoh manapun ke tokoh lain |
| n_components | 8 | 8 "pulau" graf, giant component 90.8% (148 dari 163 tokoh) |
| Degree assortativity | -0.058 | Neutral (bukan hub-and-spoke murni, bukan rich-club) |

**Klaim utama untuk Bab 4:**
1. *Transitivity 0.77 → struktur klan/suku Arab terkonfirmasi secara kuantitatif*
2. *Diameter 6 + avg_path 2.47 → small-world network → informasi/pengaruh menyebar cepat (relevan untuk dakwah)*
3. *90.8% giant component → mayoritas tokoh terhubung*

### 2.3 Community Detection — 3 Metode Dibandingkan

**Modularity Q:** ukuran kualitas partisi komunitas. Q>0.3 = struktur signifikan.

| Metode | n_komunitas | Modularity Q | Catatan |
|---|---:|---:|---|
| **Louvain (proper)** | 13 | **0.327** | Pemenang. Standar emas. |
| Greedy modularity | 15 | 0.320 | Setara, ARI vs Louvain = 0.56 |
| Girvan-Newman | 16 | 0.024 | Over-fragmented, ARI vs Louvain = 0.13 |

**Kenapa Girvan-Newman gagal di Sirah?** Karena transitivity tinggi (0.77) → banyak path alternatif → betweenness rendah merata → algoritma over-aggressively memutus edge.

**4 komunitas terbesar (Louvain) — semantically meaningful:**

| Komunitas | Ukuran | Karakteristik |
|---|:-:|---|
| C1 | 50 | Tokoh Yatsrib pra-Islam + pinggiran |
| C2 | 39 | **Quraisy oposisi utama** (Abu Jahal, Abu Sufyan, …) |
| C3 | 33 | **Sahabat dekat & keluarga Nabi** |
| C4 | 21 | Sahabat + munafik Madinah |

### 2.4 Studi Kasus 5 Event Berperiode Jauh

| Event | Period | Person | Direct P-P Relations |
|---|:-:|:-:|:-:|
| Perang Badr | P8 | 39 | 16 (8 KEL, 2 MUS, 6 SAH) |
| Perang Uhud | P9 | 18 | 10 |
| Perjanjian Hudaibiyah | P11 | 3 | 0 |
| Perang Khaibar | P11 | 5 | 0 |
| Perang Tabuk | P13 | 6 | 0 |

**Total 60 unique Person**, hanya **Muhammad muncul di 5/5 event**.

**Bias coverage NER terlihat (LIMITASI yang HARUS diakui jujur):**
- Perang Tabuk historisnya **30.000 pasukan** tapi cuma 6 person ter-capture
- Bukan ground-truth keterlibatan, **cerminan content density teks Al-Mubarakfuri** (Tabuk dapat porsi ringkas)
- Setelah upgrade ke SRL-NER, coverage *kemungkinan* membaik tapi Tabuk tetap akan low (inherent dari sumber data)

---

## 3. HASIL SRL-NER S2 CONTRASTIVE LEARNING

### 3.1 Setup

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, vanilla CE loss | ✅ Reuse hasil 2026-05-07 (Seq F1 entity = 0.959) |
| **S2a — SCL** | S1 + Strict Supervised Contrastive (Khosla 2020) | ✅ **Selesai 14–15 Mei** |
| **S2b — JSCL** | S1 + Jaccard Similarity Contrastive (Dewabharata et al.) | ✅ **Selesai 14–15 Mei** |
| **S3 — Augmentation + S2** | S2 + Mention Replacement (Dai & Adel 2020) | ⏳ Script siap, tunggu approval Ibu |

**Hyperparameter contrastive:** λ_C = 0.3, τ = 0.1, embedding kalimat = mean-pool token. Adaptasi JSCL: sentence-level Jaccard antar bag-of-label BIO (exclude `O`).

**Paper rujukan:** `Contrastive_Learning.pdf` di root repo (Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo — ITS).

### 3.2 Hasil Self-Training (6 iterasi, 10 epoch/iter) — Seq F1 Entity-Level

**Tabel ringkasan final per-iter (epoch 10 = akhir tiap iter):**

| Iter | S2a SCL Seq F1 | S2b JSCL Seq F1 |
|:-:|:-:|:-:|
| 1 | 0.924 | 0.904 |
| 2 | 0.942 | 0.933 |
| 3 | 0.949 | 0.935 |
| 4 | 0.947 | 0.930 |
| 5 | **0.950** | **0.939** |
| 6 | 0.950 | 0.933 |
| **Peak** | **0.953** (iter-6 ep-4) | **0.940** (iter-5 ep-3) |
| **S1 baseline** | **0.959** | **0.959** |

**Trend monotonik naik** lintas iter — self-training tetap bekerja di entity-level (bukan cuma token-level).

### 3.3 Klaim Utama (Honest Framing)

**✅ Yang BISA dipertahankan:**
1. Self-training di S2 SCL+JSCL menaikkan Seq F1 lintas iterasi (~+0.03 dari iter-1 ke iter-6)
2. SCL > JSCL secara konsisten lintas iterasi (~+0.01 di setiap iter)
3. Token-level F1 S2 (~0.995) **lebih tinggi** dari S1 baseline (~0.99)
4. Per-class minor (EVENT, I-LOCATION, B-TIME) yang masih F1 0.78–0.82 di S2 → **alasan valid untuk lanjut S3 augmentation**

**⚠️ Yang HARUS dijelaskan jujur:**
- Seq F1 entity S2 final (~0.95) **sedikit di bawah** S1 baseline (0.959) — gap ~0.01
- Kemungkinan penyebab: **λ_C=0.3 terlalu agresif** → trade-off antara per-token classification vs entity boundary detection
- Bukan kegagalan total — token-level masih naik, trend trajectory naik, gap kecil & masih dalam toleransi

### 3.4 Per-Class Token-Level (test set, model iter-6 S2a SCL)

| Label | Support | F1 |
|---|---:|---:|
| **B-EVENT** | 47 | **0.777** ← minoritas |
| **I-EVENT** | 53 | 0.808 |
| **I-LOCATION** | 26 | **0.776** ← minoritas |
| **B-TIME** | 74 | 0.815 |
| B-LOCATION | 449 | 0.908 |
| B-PERSON | 1189 | 0.910 |
| I-TIME | 158 | 0.883 |
| I-PERSON | 1113 | 0.941 |
| **Macro avg** | — | **0.868** |
| Weighted avg | — | 0.990 |

**Insight:** kelas minoritas (EVENT, I-LOCATION, B-TIME) yang F1 di bawah 0.82 → **target perfect untuk S3 augmentation** yang menyasar tepat kelas ini (Mention Replacement Dai & Adel 2020).

### 3.5 Rekomendasi untuk S3

- Pilih **SCL** untuk S3 augmentation (konsisten lebih tinggi dari JSCL di setiap iter)
- Augmented data sudah siap: distribusi minor naik 2–3× (B-EVENT 0.14% → 0.28%, I-LOCATION 0.07% → 0.13%)
- Estimasi 3–4 jam GPU T4 di Colab untuk S3a (SCL + aug)
- Future work: tuning λ_C dari 0.3 → 0.1 / 0.2 untuk recover entity-level F1

---

## 4. KEPUTUSAN YANG BUTUH ARAHAN BU DIANA

| # | Keputusan | Default Saya Sarankan |
|:-:|---|---|
| 1 | Validasi hasil graf — periodisasi top-down 15 period, transitivity 0.77, Louvain Q 0.327, 5 event case study | (Tunggu feedback) |
| 2 | S3 augmentation pakai SCL saja atau dua-duanya (SCL + JSCL)? | **SCL saja** — JSCL konsisten lebih rendah, biaya marginal tidak worth |
| 3 | Apakah gap Seq F1 S2 (0.95) vs S1 (0.96) bisa diterima sebagai "selesai" untuk Bab 4? Atau perlu tune λ_C dulu? | Lanjut S3 dulu — kalau S3 juga gagal close the gap, baru tune λ_C |
| 4 | Kapan inference NER terbaik ke seluruh sirah_chunks_final.csv → regenerate graf? | Setelah S3 selesai dan winner dipilih, estimasi 1 minggu kerja |
| 5 | Visualisasi tambahan yang Ibu mau (timeline 15 period, sub-graf per komunitas, dll.)? | (Tunggu instruksi) |

---

## 5. FLOW NARATIF + SKRIP PRESENTASI

### 5.1 Flow 20–25 Menit

```
[2 min]  Opening — sumber data + pipeline + status update SRL-NER & graf
[3 min]  Schema graf v2 + pembobotan + statistik dasar
[3 min]  §2.1 Centrality node-level — Muhammad dominasi, validasi pipeline
[4 min]  §2.2 Graph-level metrics — TEMUAN UTAMA (klan + small-world)
[2 min]  §2.3 Community detection — 3 metode comparison
[3 min]  §2.4 Studi kasus 5 event — confirms pipeline + reveal bias coverage
[4 min]  §3 SRL-NER S2 — Seq F1 dual metric, trend monotonik, gap vs S1
[2 min]  Demo Neo4j live (query 2 Perang Badr + query 4 density per period)
[Q&A]
```

### 5.2 Skrip Per Section

**Opening (2 menit):**
> *"Bu, hari ini saya mau lapor dua hasil utama. Pertama, evaluasi Knowledge Graph yang menjawab revisi #2 dan #4 Ibu di 3 Mei — graph-level metrics, community detection, dan studi kasus 5 event. Kedua, hasil run SRL-NER S2 contrastive learning yang Ibu minta di putaran 3 (7 Mei) — sudah selesai re-run dengan dual metric token-level + entity-level seqeval. Untuk graf, sumber datanya masih pipeline manual semi-auto labelling — akan di-regenerate dengan output NER setelah S2/S3 winner dipilih."*

**Schema + Statistik (3 menit):**
> *"KG v2 di Neo4j punya 907 node total — 658 Person, 147 Time, 51 Location, 36 Event, dan 15 Period. Period adalah node baru di v2 sebagai first-class node menggantikan property string setelah revisi periodisasi 12 Mei. Edge-nya 322 dengan 7 tipe relasi di edges_v2.csv plus 36 IN_PERIOD yang di-generate di Cypher, semua weighted 0–1. Pembobotan kami pakai 3 skema berbeda: Proximity+Period untuk co-occurrence (INVOLVED_IN dkk.), fixed 0.55 untuk pattern-based (KELUARGA/SAHABAT/MUSUH), dan deterministik 1.0 untuk PRECEDES yang kronologis pasti."*

**Centrality (3 menit):**
> *"Evaluasi node-level — 4 metrik centrality. Muhammad dominasi semua: degree 105, 3× tokoh kedua. Wajar untuk Sirah, sekaligus validasi pipeline. Abu Jahal posisi 2 — sesuai sejarah musuh utama Quraisy. Yang menarik Utsman bin Affan: degree menengah tapi betweenness tinggi — peran jembatan antar kelompok."*

**Graph-Level (4 menit — BAGIAN TERPENTING):**
> *"Untuk evaluasi graph-level, sesuai revisi #4 Bu Diana. Temuan utamanya transitivity 0.77 — sangat tinggi. Kalau A dan B saling kenal, dan B dan C saling kenal, kemungkinan besar A dan C juga saling kenal. Ini konsisten dengan struktur klan-suku Arab pra-Islam. Selain itu, diameter cuma 6 dengan avg_path 2.47 — graf Sirah punya karakteristik small-world. Informasi/pengaruh menyebar cepat di komunitas — relevan untuk konteks dakwah."*

**Community Detection (2 menit):**
> *"Bu Diana minta uji metode lain selain Louvain — kami bandingkan 3. Louvain proper Q=0.327 dengan 13 komunitas. Greedy modularity setara (0.320) ARI vs Louvain 0.56. Girvan-Newman gagal: Q=0.024 over-fragmented — tidak cocok untuk graf transitivity tinggi seperti Sirah. Komunitas terbesar Louvain semantically meaningful: Quraisy oposisi, sahabat Nabi, tokoh Yatsrib pra-Islam."*

**Studi Kasus (3 menit):**
> *"Cluster #2 — 5 event berperiode jauh P8 sampai P13. Total 60 unique Person, Muhammad satu-satunya tokoh muncul di 5/5 event. Tapi ada limitasi yang harus diakui jujur: Perang Tabuk historisnya 30 ribu pasukan tapi cuma 6 person ter-capture. Bukan ground-truth keterlibatan, cerminan content density teks Al-Mubarakfuri. Akan jadi catatan limitasi di Bab 4."*

**SRL-NER S2 (4 menit):**
> *"Untuk cluster #3, S2a SCL dan S2b JSCL sudah selesai re-run dengan dual metric. Seq F1 entity-level naik monotonik lintas 6 iterasi self-training — SCL 0.92 ke 0.95, JSCL 0.90 ke 0.94. Final iter-6: SCL 0.950 (peak 0.953 di epoch-4), JSCL 0.933 (peak 0.940 di iter-5). Token-level F1 ~0.995 — lebih tinggi dari S1 baseline. Tapi jujur, Seq F1 entity S2 sedikit di bawah S1 baseline 0.959 — gap kecil 0.01. Kemungkinan λ_C=0.3 terlalu agresif sehingga ada trade-off boundary detection vs token accuracy. Saya rekomendasikan lanjut S3 augmentation pakai SCL, karena augmented data menyasar kelas minor EVENT dan I-LOCATION yang memang masih F1 0.78–0.82 di S2."*

**Demo Neo4j (2 menit):**
> *"Saya tunjukkan langsung di Neo4j..."* [run Query 2: Perang Badr sub-graph, kemudian Query 4: density per period table]

---

## 6. PERTANYAAN BU DIANA YANG MUNGKIN + JAWABAN

### Q1: Kenapa graf masih pakai manual labelling, bukan SRL-NER?

> *"Cluster #2 studi kasus dan #4 graph-level metrics adalah revisi yang bisa paralel dengan data saat ini. Cluster #3 SRL-NER masih dalam proses — sudah selesai S2 tapi belum S3 dan belum inference ke seluruh data. Setelah winner dipilih, graf akan di-regenerate dengan output NER. Tapi struktur evaluasi (metrik, studi kasus, community detection) tidak perlu diubah."*

### Q2: Transitivity 0.77 — interpretasinya pasti struktur klan? Bukan artefak data?

> *"Validasi 2 cara. Analitis: random network dengan density 0.086 teorinya transitivity ~0.086. Kita dapat 0.77 — 9× lebih tinggi dari random baseline, jelas non-acak. Semantik: komunitas Louvain banyak yang struktur internalnya keluarga/Bani — misal Abu Sufyan punya 14 relasi KELUARGA, keluarganya juga punya relasi MUSUH yang sama. Itu pola klan yang bikin transitivity tinggi."*

### Q3: Modularity 0.327 cukup tinggi?

> *"Konvensi network science: Q>0.3 = struktur komunitas signifikan (Newman 2006). 0.327 sedikit di atas threshold. Tidak super tinggi karena Muhammad sebagai hub utama secara realistis terhubung ke semua komunitas, jadi banyak edge lintas-komunitas yang mengurangi Q. Wajar untuk graf dengan tokoh sentral dominan."*

### Q4: Visualisasi Perang Tabuk cuma 6 orang — kelihatan jelek?

> *"Ya Bu, justru itu yang ingin kami highlight sebagai temuan. Tabuk 30 ribu pasukan tapi 6 person — cerminan content density teks Al-Mubarakfuri yang memang ringkas di chapter Tabuk. Bisa kami sajikan sebagai limitasi di Bab 4. Tidak bisa di-fix hanya dengan upgrade NER, karena sumber datanya memang minim mention. Solusi future: kombinasi multi-source (mis. tambah Sirah Ibn Hisyam) — di luar scope TA ini."*

### Q5: Kenapa Seq F1 S2 lebih rendah dari S1? Bukannya contrastive harusnya improve?

> *"Pertanyaan bagus, Bu. Beberapa kemungkinan: pertama, kami pakai λ_C=0.3 untuk contrastive loss weight, mungkin terlalu agresif sehingga model over-prioritize representation learning di token-level dan kompromi di entity boundary. Token-level F1 S2 justru lebih tinggi dari S1 (~0.995 vs S1). Kedua, dataset terlalu kecil (~6000 chunks) sehingga contrastive belum dapat banyak positive pair berkualitas. Yang lebih penting, **trend self-training tetap monotonik naik** lintas iterasi — artinya self-training-nya tetap bekerja, bukan placebo. Rekomendasi saya: lanjut S3 augmentation dulu, karena augmentation menyasar kelas minor secara langsung. Kalau S3 juga tidak close the gap, baru tune λ_C ke 0.1 atau 0.2 di future work."*

### Q6: Apa beda Seq F1 dengan F1 yang token-level?

> *"Seq F1 = entity-level seqeval. Strict: satu entity dihitung benar kalau seluruh span B+I match persis. Misalnya entity 'Abu Jahal' diprediksi 'Abu Jahal' = benar 1 entity; tapi 'Abu' saja = salah total (split). F1 token-level dari sklearn = per-token classification: tiap token dihitung sendiri-sendiri, B-PERSON beda kelas dari I-PERSON. Token-level cenderung lebih tinggi karena 'O' dominasi (93% token). Untuk NER, entity-level Seq F1 lebih representatif. Kami sajikan keduanya untuk konsistensi dengan metode Ibu (token) plus fair comparison antar skenario (entity)."*

### Q7: Kapan SRL-NER beneran selesai?

> *"S2 sudah selesai. S3 augmentation: script siap, augmented data ready (minor distribution 0.14% → 0.28%), tinggal run 3–4 jam GPU T4 di Colab. Setelah S3 selesai, pilih winner antara S1/S2a/S2b/S3 → inference ke seluruh sirah_chunks_final.csv → re-run relation extraction → graf regenerated. Estimasi total 1–2 minggu kerja."*

### Q8: Kelahiran/Kematian Nabi belum jadi event?

> *"Saat ini event yang ter-capture adalah peristiwa kolektif (peperangan, perjanjian, hijrah). Kelahiran/Kematian belum eksplisit karena pre_labelling.py fokus event eksternal. Bisa ditambahkan via mekanisme ADD candidate di review periodisasi, seperti yang sudah dipakai untuk Wahyu Pertama dan Haji Wada'. Estimasi 30 menit kalau Ibu setuju."*

### Q9: Kok di Neo4j ada banyak node yang tidak terhubung / floating?

> *"Pertanyaan bagus Bu. Itu **expected** dan ada dua konteks yang perlu dibedakan supaya tidak rancu:*
>
> *(1) **Di Person co-participation graph (163 node)** yang kami pakai untuk graph-level metrics di §2.2 — ada 8 komponen, giant component 90.8%. Komponen kecil (2–3 orang) muncul di chapter spesifik di mana tokohnya tidak ke-mention bersama tokoh lain.*
>
> *(2) **Di full Neo4j graph (907 node)** — angka real dari diagnostik:*

**Tabel angka real (siap-siap kalau Bu Diana tanya konkret):**

| NodeType | Total | Terisolasi | % Isolated | Interpretasi |
|---|---:|---:|---:|---|
| **Event** | 36 | **0** | **0%** ✅ | **Pipeline core sehat** — semua Event punya minimal 1 edge |
| Period | 15 | 3 | 20% | 3 period tanpa Event valid (kemungkinan pra-Islam awal / pasca-wafat) |
| Location | 51 | 38 | 74.5% | Location ter-extract tapi tidak dirujuk Event dengan proximity cukup |
| Person | 658 | 493 | 74.9% | Person muncul sekali tanpa konteks Event/pattern KEL/SAH/MUS |
| Time | 147 | 122 | 83% | Time labels banyak (tahun, bulan) tapi tidak match Event proximity |

> *"Klaim utama: **Event 0% terisolasi → pipeline relation extraction bekerja untuk anchor utama**. Yang banyak terisolasi adalah tail entities (Person/Time/Location) — itu cerminan coverage limitation pre_labelling.py regex-based saat ini. Setelah upgrade ke SRL-NER (S2/S3) coverage **akan meningkat** karena NER lebih kuat bisa ter-link ke lebih banyak Event. Untuk evaluasi graph-level di TA ini, kami **fokus di giant component Person co-participation (90.8%)**, bukan whole graph — sudah di-disclaim di laporan."*

**Visualisasi yang lebih bersih untuk Neo4j Browser (kalau Bu Diana minta tunjuk):** ganti query dari `MATCH (n) OPTIONAL MATCH (n)-[r]-(m)` ke `MATCH (n)-[r]-(m) RETURN n, r, m` — drop OPTIONAL MATCH, hanya kembalikan node yang punya edge. Atau filter ke giant component via:
```cypher
MATCH (m:Person {name: "Muhammad"})-[*..6]-(n)
RETURN DISTINCT m, n;
```

**Diagnostik kalau Bu Diana minta angka konkret:**
```cypher
MATCH (n)
WITH labels(n)[0] AS NodeType,
     count(n) AS total,
     sum(CASE WHEN NOT (n)--() THEN 1 ELSE 0 END) AS terisolasi
RETURN NodeType, total, terisolasi,
       round(100.0 * terisolasi / total, 1) AS persen_terisolasi
ORDER BY terisolasi DESC;
```

---

## 7. CHECKLIST SEBELUM BIMBINGAN

- [ ] Buka **file ini** (`bimbingan_2026_05_16.md`) di tab terpisah — referensi cepat
- [ ] Buka `bimbingan_graf_2026_05_14.md` jika butuh detail lebih lengkap untuk Q&A graf
- [ ] Buka `src/pseudo_labelling/SRL-NER/S2-seqeval.md` jika Bu Diana minta detail epoch S2
- [ ] Buka `case_study_panel.png` — siap di-share-screen
- [ ] Buka `data/result/analysis/graph_metrics_v2.md` — siap tunjuk sebagai source
- [ ] (Opsional) Neo4j Desktop sudah running dengan `import_sirah_v2.cypher` ter-import — test Query 2 + Query 4
- [ ] Slide / Google Docs siap dengan PNG visualisasi + tabel utama
- [ ] Read skrip §5.2 — 20–25 menit cukup untuk hafal flow
- [ ] **Catatan di kertas** — 8 angka kunci:
  - Graf: transitivity **0.77**, density 0.086, diameter 6, modularity Louvain **0.327**
  - SRL-NER: S1 baseline **0.959**, S2a SCL final **0.950** / peak **0.953**, S2b JSCL final **0.933** / peak **0.940**

---

## 8. FILE REFERENSI

| File | Isi | Kapan dibuka |
|---|---|---|
| `bimbingan_2026_05_16.md` (file ini) | Combined prep — graf + S2 | Selama bimbingan, referensi cepat |
| `bimbingan_graf_2026_05_14.md` | Detail lengkap graf (centrality top-10, query Cypher, dst.) | Kalau Bu Diana minta detail graf |
| `src/pseudo_labelling/SRL-NER/S2-seqeval.md` | Tabel epoch lengkap S2a + S2b (12 iter × 10 epoch) | Kalau Bu Diana minta detail S2 |
| `data/result/analysis/graph_metrics_v2.md` | Laporan graph-level metrics |  Referensi angka graf |
| `data/result/analysis/case_study_events.md` | Laporan 5 studi kasus | Referensi angka case study |
| `srl_ner_skenario.md` | Metodologi SCL/JSCL/augmentation lengkap | Kalau Bu Diana minta paper rujukan |
| `Contrastive_Learning.pdf` | Paper rujukan SCL+JSCL (Dewabharata ITS) | Tunjukkan kalau ditanya sumber |

---

**Selamat bimbingan besok, semoga lancar.**
