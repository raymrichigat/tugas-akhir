# Bimbingan Bu Diana — 2026-05-13

> **Bimbingan sebelumnya:** 2026-05-07 (Putaran 3 — Bu Diana minta contrastive learning + augmentation, plus 4 cluster revisi 2026-05-03 yang masih on-going saat itu).
> **Tujuan bimbingan hari ini:** lapor progres sejak 2026-05-07, tunjukkan hasil S2 contrastive, minta arahan untuk S3.

---

## 0. Ringkasan 1 Menit (Talking Points)

Kalau Bu Diana minta executive summary singkat di awal, ini intinya:

1. **4 dari 4 revisi cluster Bu Diana (2026-05-03) sudah selesai.** Periodisasi top-down (15 period), temporal detection intra-sentence, graph-level metrics, dan studi kasus 5 event berperiode jauh — semua sudah ada di `data/result/`.
2. **SRL-NER direstruktur** (per kesepakatan internal 2026-05-11) jadi 3 layer: S1 baseline (sudah selesai, reuse hasil 2026-05-07), S2 contrastive learning (SCL + JSCL, **sudah selesai run 2026-05-12**), S3 augmentation (script siap, belum di-run, depend on approval S2).
3. **Hasil preliminary S2:** kedua varian (SCL & JSCL) menaikkan F1 kelas minoritas vs base model, terutama I_EVENT (+0.07–0.09). Caveat: metrik token-level (sklearn) karena seqeval tidak ke-install di Colab — belum head-to-head dengan S1 di entity-level.
4. **Periodisasi top-down menggantikan fuzzy match BAB.** 15 period (P0–P14), 56 BAB ter-grouped, sudah di-review manual (19 K + 10 F + 12 R + 7 ADD) → `nodes_v2.csv` (892) + `edges_v2.csv` (322) + `import_sirah_v2.cypher` siap diimport ke Neo4j.
5. **Evaluasi graf 2 layer sudah selesai** (lihat §3): **node-level** (centrality — siapa tokoh paling penting, Muhammad di semua metrik) + **graph-level** (density 0.086, transitivity 0.77 = struktur klan/suku terkonfirmasi, diameter 6 + avg path 2.47 = small-world) + community detection 3 metode (Louvain Q=0.327 menang) + studi kasus 5 event berperiode jauh.
6. **Yang butuh keputusan Bu Diana hari ini:** (a) SCL atau JSCL yang dilanjut ke S3? (b) Setujukah pakai token-level metric saja, atau perlu re-evaluate S2 dengan seqeval (script siap, lihat §4)? (c) Validasi hasil periodisasi + temporal + graph metrics + studi kasus 5 event?

---

## 1. Progress Sejak Bimbingan 2026-05-07

### 1.1 Cluster Periodisasi + Temporal + Graph (4 dari 4 revisi Bu Diana 2026-05-03) — ✅ Selesai 2026-05-12

| Revisi | Status | Output |
|---|---|---|
| **#1 Temporal intra-sentence** | ✅ Selesai (yield rendah → insight metodologis) | `detect_temporal_relations.py` → 3 unique relations (1 confirmed by page-order) |
| **#2 Studi kasus 5 event berperiode jauh** | ✅ Selesai | `case_study_events.py` → Badr / Uhud / Hudaibiyah / Khaibar / Tabuk; 60 unique Person, Muhammad satu-satunya hub lintas-5-event |
| **#4 Graph-level metrics** | ✅ Selesai | `sna_graph_metrics.py` → density 0.086, transitivity **0.7723** (klan/suku Arab confirmed), small-world (diameter 6, avg_path 2.47), giant component 90.8% |
| **#4b Community detection comparison** | ✅ Selesai | Louvain proper Q=0.327 / Greedy Q=0.320 / Girvan-Newman Q=0.024. ARI Louvain vs Greedy = 0.56 |

**Plus revisi internal user:** periodisasi top-down (`period_mapping.json`) menggantikan fuzzy match BAB lama. 15 period (P0–P14) di 6 phase. Manual review 39+7=46 event → `nodes_v2.csv` + `edges_v2.csv` + Neo4j `import_sirah_v2.cypher` dengan Period sebagai first-class node.

### 1.2 Cluster SRL-NER — Restrukturisasi + S2 Selesai

**Restrukturisasi (2026-05-11):**
Skenario lama (E1 + S1 class weight + S2 adaptive yang di-run 2026-05-07) **di-arsip** ke `done_running/legacy_class_weight_adaptive/`. Alasan: skenario lama tidak layer-by-layer dan campur 2 kontribusi (class weight + adaptive threshold). Skenario baru = 1 skenario = 1 layer kontribusi:

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, vanilla CE loss | ✅ Selesai (reuse E1 lama, F1 entity seqeval = 0.9587, F1 EVENT entity = 0.816) |
| **S2a — SCL + Baseline** | S1 + Strict Supervised Contrastive (Khosla 2020) | ✅ **Selesai run 2026-05-12** |
| **S2b — JSCL + Baseline** | S1 + Jaccard Sim Contrastive (Dewabharata et al.) | ✅ **Selesai run 2026-05-12** |
| **S3a/S3b — Augmentation + S2** | S2 + Mention Replacement (Dai & Adel 2020) | ⏳ Script siap, augmented data sudah generated (minor 0.14% → 0.28%), tunggu approval |

**Paper rujukan S2:** Dewabharata et al. — *Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts* (file `Contrastive_Learning.pdf` di root). Berisi 3 strategi: BAL (skip per arahan Bu Diana), **SCL** (Eq. 2–3, InfoNCE positive pair = label set identik), **JSCL** (Eq. 4–6, weighted InfoNCE dengan α_ij = Jaccard).

**Adaptasi JSCL ke NER (lock-in):** sentence-level, bag-of-labels BIO exclude `O`, embedding kalimat = mean-pool token embeddings dari encoder BERT. λ_C = 0.3, τ = 0.1.

---

## 2. Hasil S2 — Detail untuk Diskusi

### 2.1 Dinamika Self-Training (jumlah pseudo-label per iter)

| Iter | S1 (baseline) | S2a (SCL) | S2b (JSCL) |
|---:|---:|---:|---:|
| 1 | 187 | 187 | 187 |
| 2 | 32 | 32 | 32 |
| 3 | 14 | 14 | 14 |
| 4 | 2 | 2 | 2 |
| 5 | 1 | 1 | 1 |
| 6 | 1 | 1 | 1 |
| **Total** | **237** | **237** | **237** |

**Observasi:** angka n_above per iter identik di ketiga skenario. Ini menunjukkan threshold 0.9 + sampling 1.0 + seed sama → kalimat yang dipseudo-label sama persis. Yang berbeda adalah **representasi token internal** karena contrastive loss bekerja di tahap training, bukan tahap seleksi pseudo-label.

> **Catatan untuk diskusi:** apakah ini sesuai ekspektasi Bu Diana, atau beliau berharap contrastive juga merubah pool kalimat? Kalau yang kedua, perlu pikirkan ulang integrasi (mis. contrastive juga jadi confidence signal di seleksi).

### 2.2 F1 Token-Level (sklearn, classification_report) — Iter-6 Final

> ⚠️ **Caveat penting:** seqeval tidak ke-install di Colab run, jadi metrik di bawah ini **token-level** (per token klasifikasi 9 label BIO + O), bukan **entity-level** seperti F1=0.9587 di S1. Untuk head-to-head dengan S1, perlu re-evaluate semua skenario dengan seqeval — bisa di-run di lokal.

| Label | Support | S2a (SCL) F1 | S2b (JSCL) F1 |
|---|---:|---:|---:|
| O | 39.449 | 0.998 | 0.998 |
| B_PERSON | 1.189 | 0.977 | 0.979 |
| I_PERSON | 1.113 | 0.979 | 0.983 |
| B_LOCATION | 449 | 0.961 | 0.953 |
| I_LOCATION | 26 | 0.893 | 0.852 |
| B_TIME | 74 | 0.927 | 0.932 |
| I_TIME | 158 | 0.935 | 0.949 |
| **B_EVENT** | **47** | **0.863** | **0.882** |
| **I_EVENT** | **53** | **0.857** | **0.835** |
| Macro avg (9 label incl. O) | — | 0.932 | 0.929 |
| Weighted avg | — | 0.996 | 0.996 |

### 2.3 Improvement Base → Iter-6 (membuktikan self-training tetap bermanfaat)

| Label | S2a base → iter-6 | S2b base → iter-6 |
|---|---:|---:|
| B_EVENT | 0.842 → 0.863 (+0.021) | 0.851 → 0.882 (+0.031) |
| I_EVENT | 0.769 → 0.857 **(+0.088)** | 0.766 → 0.835 (+0.069) |
| I_LOCATION | 0.792 → 0.893 (+0.101) | 0.792 → 0.852 (+0.060) |
| B_TIME | 0.859 → 0.927 (+0.068) | 0.901 → 0.932 (+0.031) |
| I_TIME | 0.896 → 0.935 (+0.039) | 0.880 → 0.949 (+0.069) |
| Macro avg | 0.904 → 0.932 (+0.028) | 0.894 → 0.929 (+0.035) |

**Interpretasi:**
- Kedua varian menaikkan F1 di semua kelas minoritas signifikan (terutama I_EVENT, I_LOCATION, I_TIME).
- SCL unggul di **I_EVENT** (+0.088) dan **I_LOCATION** (+0.101).
- JSCL unggul di **B_EVENT** (akhir 0.882 > SCL 0.863) dan **I_TIME** (+0.069 → 0.949).
- Macro avg keduanya hampir sama (0.929 vs 0.932) — selisih < 0.5%.

### 2.4 SCL vs JSCL — Mana yang Dipilih ke S3?

| Aspek | SCL menang | JSCL menang |
|---|---|---|
| I_EVENT (paling minor di antara EVENT) | ✓ 0.857 | 0.835 |
| B_EVENT | 0.863 | ✓ 0.882 |
| Macro avg | ✓ 0.932 | 0.929 |
| I_LOCATION (kelas paling extreme minor, 26 token) | ✓ 0.893 | 0.852 |
| Stabilitas (precision-recall trade-off) | ✓ balanced | balanced |
| Justifikasi paper | Khosla 2020 (foundational, well-known) | Dewabharata 2024 (paper rujukan Bu Diana, lebih spesifik domain) |

**Rekomendasi sementara:** lanjut **kedua** (S3a = SCL+aug, S3b = JSCL+aug) untuk completeness — biaya marginal kecil (notebook & augmented data sudah siap), benefit besar (jaga opsi kalau Bu Diana minta justifikasi salah satu). Tapi kalau Bu Diana mau hemat waktu, **SCL** sebagai default karena foundational paper-nya lebih clean untuk diceritakan di Bab 4.

---

## 3. Graf + Knowledge Graph — Apa yang Sudah Dievaluasi

### 3.1 Graf yang Dibangun

**Knowledge Graph Sirah v2** (setelah review periodisasi 2026-05-12):

| Komponen | Jumlah | Catatan |
|---|---:|---|
| Node total | 892 | dari `nodes_v2.csv` |
| Period nodes (baru v2) | 15 | P0–P14, first-class entity |
| Person nodes | 781 | tokoh + kabilah/Bani |
| Event nodes | 36 | sebelumnya 41, dikurangi setelah review K/F/R |
| Location nodes | ~30 | Makkah, Madinah, Badr, dst |
| Time nodes | ~30 | tahun, bulan, periode hijriyah |
| Edges total | 322 | dari `edges_v2.csv` (sebelumnya 370 pra-review) |
| Relasi types | 7 | INVOLVED_IN, KELUARGA, SAHABAT, MUSUH, OCCURRED_AT, OCCURRED_ON, PRECEDES |
| IN_PERIOD relations | 36 | Event → Period mapping |

**Pipeline ekstraksi graf:**
1. NER (S1 baseline saat ini) → entity dengan label PERSON / EVENT / TIME / LOCATION.
2. Alias clustering (Jaro-Winkler + manual) → normalisasi varian nama (143 alias → 109 cluster).
3. Relation extraction → pairing proximity-based + pattern-based (regex untuk KELUARGA/SAHABAT/MUSUH) + weighting (proximity + period score).
4. Periodisasi top-down → setiap EVENT di-map ke Period berdasarkan page_range.
5. Generate Cypher → `import_sirah_v2.cypher` (1287 statements).

### 3.2 Evaluasi Node-Level — Centrality (Sudah Ada Sejak Revisi #1 Bu Diana 2026-04-24)

**Pertanyaan yang dijawab:** "Siapa tokoh paling penting di Sirah?"
**File:** `data/result/analysis/sna_metrics.csv` + `sna_summary.md`

| Metrik | Maksud | Top-1 |
|---|---|---|
| **Degree centrality** | Berapa banyak koneksi langsung (proxy untuk popularitas / frekuensi muncul bersama) | Muhammad (105 koneksi, 0.61 dari max) |
| **Betweenness centrality** | Seberapa sering node jadi "jembatan" di shortest path antar tokoh lain (proxy untuk peran broker/penghubung) | Muhammad (0.41) — jelas jadi jembatan utama antar faksi |
| **Closeness centrality** | Seberapa "dekat" rata-rata ke semua node lain (proxy untuk aksesibilitas) | Muhammad |
| **PageRank** | Importance terbobot oleh importance tetangga | Muhammad (0.064) — bukan cuma banyak koneksi, tapi koneksi-koneksinya juga penting |

**Interpretasi untuk Bab 4:** Muhammad mendominasi semua metrik sebagai expected. Tokoh berikutnya: Abu Jahal (musuh utama Quraisy), Ali bin Abu Thalib (sahabat utama), Abu Sufyan bin Harb.

### 3.3 Evaluasi Graph-Level — Revisi #4 Bu Diana 2026-05-03 (Selesai 2026-05-12)

> **Maksud "evaluasi grafnya itu seperti apa":** revisi #4 Bu Diana menyatakan centrality (per node) saja tidak cukup, perlu **metrik yang menggambarkan keseluruhan struktur graf** (bukan per individu). Ini untuk menjawab pertanyaan-pertanyaan tipe **"seberapa rapat / terkluster / terhubung graf Sirah?"** Hasil di `data/result/analysis/graph_metrics_v2.md`.

**Subset yang dievaluasi:** Person co-participation graph (163 nodes, 1135 edges) — graf yang dibangun dari sharing event yang sama + relasi langsung Person-Person.

| Metrik | Nilai | Maksud (Bahasa Awam) | Interpretasi Sirah |
|---|---:|---|---|
| **Density** | 0.086 | Berapa persen koneksi yang mungkin terjadi sebenarnya terjadi. 0=tidak ada hubungan, 1=semua orang kenal semua. | **Sparse but cohesive.** Cuma 8.6% pasangan tokoh punya relasi langsung — wajar untuk teks naratif besar. |
| **Average degree** | 13.93 | Rata-rata jumlah koneksi per orang | Tiap tokoh terhubung ke ~14 tokoh lain. |
| **Average clustering coefficient** | 0.45 | Rata-rata "ke-clusteran" lokal: kalau A kenal B dan C, seberapa sering B juga kenal C? | Moderately clustered di level individu. |
| **Transitivity (global clustering)** | **0.77** | Versi global: rasio segitiga (3 orang saling kenal) ke triplet | **Sangat tinggi.** Ini konsisten dengan struktur klan/suku Arab — kalau tokoh A & B dari Bani yang sama, B & C juga, biasanya A & C kenal juga. |
| **Degree assortativity** | -0.058 | Apakah hub menempel ke hub (positif) atau hub menempel ke daun (negatif) | Mendekati neutral. Tidak terlalu hub-and-spoke (-1), tidak terlalu rich-club (+1). |
| **n_components** | 8 | Jumlah "pulau" graf yang tidak terhubung satu sama lain | Ada 8 grup terpisah — sebagian besar (~91%) tergabung di satu giant component. |
| **Giant component size** | 148 (90.8%) | Ukuran komponen terbesar | 148 dari 163 tokoh saling reachable. |
| **Giant diameter** | 6 | Jarak shortest path terjauh antar 2 tokoh | Bisa "loncat" dari tokoh manapun ke tokoh lain dalam **maksimal 6 langkah**. |
| **Giant avg shortest path** | 2.47 | Rata-rata jarak | Rata-rata 2–3 langkah → **small-world network**. |

**Klaim utama untuk Bab 4:** Graf Sirah menunjukkan **struktur small-world dengan kohesi klan tinggi** (transitivity 0.77). Ini bukan artefak data — ini mencerminkan realitas sosial masyarakat Arab pra-Islam yang berbasis kabilah.

### 3.4 Community Detection — Bagian dari Revisi #4

> **Maksud:** apakah graf bisa dipecah ke kelompok-kelompok komunitas yang masuk akal? Bu Diana minta "uji coba metode lain" selain yang sudah ada.

**Bandingkan 3 metode:**

| Metode | n_communities | Modularity Q | Catatan |
|---|---:|---:|---|
| **Louvain (proper)** | 13 | **0.327** | Standar emas, balanced quality + speed |
| **Greedy modularity** | 15 | 0.320 | Faster tapi quality lebih rendah |
| **Girvan-Newman** | 16 | 0.024 | Over-fragmented, modularity sangat rendah |

**Maksud Modularity Q:** ukuran kualitas pembagian komunitas. **Q > 0.3 = struktur komunitas signifikan.** Q dekat 0 = pembagian acak. Q < 0 = pembagian buruk.

**Maksud ARI (Adjusted Rand Index):** kesepakatan antar 2 partisi. Louvain vs Greedy = 0.56 → moderate agreement. Louvain vs Girvan-Newman = 0.13 → mereka mendeteksi struktur yang sangat berbeda.

**Insight:** Louvain & Greedy keduanya OK (Q ≈ 0.32, ARI 0.56). Girvan-Newman over-fragment (Q hanya 0.024). **Rekomendasi Bab 4:** pakai Louvain proper sebagai default — drop yang Greedy karena di kode lama-nya `sna_analysis.py` salah label (dibilang "Louvain" padahal Greedy).

**Top 4 komunitas terbesar (Louvain):**
- **C1** (50 orang) — campur Quraisy + tokoh Yatsrib pra-Islam: Abrahah, Adam, Adi bin Hatim, …
- **C2** (39 orang) — Quraisy oposisi: Abu Jahal, Abu Sufyan bin Al-Harits, Abu Azzah, Abu Bakar (mungkin overlap awal), …
- **C3** (33 orang) — sahabat dekat & keluarga Nabi: Abdullah bin Abbas, Abu Hurairah, Abdurrahman bin Auf, Ali bin Abu Thalib (overlap), …
- **C4** (21 orang) — sahabat + munafik Madinah: Abdullah bin Atik, Abdullah bin Ubay bin Salul, Ali bin Abu Thalib, Az-Zubair, …

### 3.5 Studi Kasus 5 Event — Revisi #2 Bu Diana (Selesai 2026-05-12)

> **Maksud:** Bu Diana minta validasi bottom-up: "ambil 3–5 event dengan periode berjauhan, lihat keterlibatan, tunjukkan graf, analisis." Tujuannya untuk pastikan pipeline NER + relation extraction menghasilkan sub-graf yang masuk akal sebelum klaim besar di SNA. File `data/result/analysis/case_study_events.md` + `case_study_events_cypher.md`.

| # | Event | Period | Hal | Person | Direct Person-Person relations |
|:-:|---|:-:|:-:|:-:|:-:|
| 1 | Perang Badr | P8 | 266–304 | 39 | 16 (8 KELUARGA, 2 MUSUH, 6 SAHABAT) |
| 2 | Perang Uhud | P9 | 324–375 | 18 | 10 |
| 3 | Perjanjian Hudaibiyah | P11 | 433–450 | 3 | — |
| 4 | Perang Khaibar | P11 | 473–492 | 5 | — |
| 5 | Perang Tabuk | P13 | 558–571 | 6 | 0 |

**Temuan kunci:**
- **Muhammad satu-satunya tokoh muncul di 5/5 event** (hub lintas-period).
- 7 orang muncul di 2 event (Abu Jahal/Abu Sufyan/Abu Azzah/dst — semua di Badr + Uhud, sesuai sejarah).
- **Bias coverage NER terlihat:** Perang Badr 39 person (16 direct relations) vs Perang Tabuk 6 person (0 direct). Ini bukan ground-truth keterlibatan historis — Tabuk historisnya 30.000 pasukan. Ini cerminan **content density** di teks Al-Mubarakfuri (Badr dapat porsi panjang, Tabuk lebih ringkas).

**Klaim untuk Bab 4 (jujur):**
- Pipeline menghasilkan sub-graf yang **konsisten dengan sejarah** untuk event yang teksnya kaya (Badr, Uhud).
- **Limitasi NER coverage** harus diakui untuk event yang teksnya pendek/ringkas.
- Visualisasi 5 sub-graf via Cypher di `case_study_events_cypher.md` siap di-demo di Neo4j Desktop.

### 3.6 Neo4j Knowledge Graph v2

**Cypher file:** `data/result/neo4j/import_sirah_v2.cypher` (1287 statements).
**Konten:** 892 nodes + 15 Period + 322 edges + 36 IN_PERIOD relations + 4 uniqueness constraints.
**Query baru yang bisa di-demo:**
- "List Person yang terlibat di event Periode P8 (Perang Badr & Dampaknya)."
- "Top Person dengan jumlah event terbanyak per period."
- "Density relasi per period (proxy untuk seberapa kaya narasinya)."
- "Path Muhammad ↔ X dalam graf relasi Person-Person."

---

## 4. Re-Evaluasi dengan Seqeval — Cara Run

> **Konteks:** S1 baseline punya angka **F1 entity seqeval = 0.9587**, S2a/S2b cuma punya token-level sklearn karena seqeval **tidak ke-install di Colab run 2026-05-12**. Untuk head-to-head dengan S1, perlu re-evaluate model S2 di lokal.

### 4.1 Prerequisite

| Item | Cek dengan |
|---|---|
| venv aktif | `venv\Scripts\activate` |
| seqeval ter-install | `pip show seqeval` (kalau belum: `pip install seqeval`) |
| transformers, torch, tqdm ter-install | `pip show transformers torch tqdm` |
| `test.csv` ada | di `data/result/pseudo-labelling/SRL-NER/test.csv` ✅ |
| Model weights ada (`model.safetensors`) | dicek otomatis oleh script |

### 4.2 Gotcha — Model Weights yang Hilang

Saat aku scan folder `done_running/S2_Contrastive_Learning/outputs/models/`, beberapa file `model.safetensors` **tidak ke-download dari Colab/Drive**:

| Folder | Weights? |
|---|---|
| S1 base + iter-2..6 | ✅ Semua ada |
| S2a-scl base | ✅ |
| S2a-scl iter-2, 3, 5 | ✅ |
| S2a-scl **iter-4, iter-6** | ❌ MISSING |
| S2b-jscl **base** | ❌ MISSING |
| S2b-jscl iter-2, 3, 5, 6 | ✅ |
| S2b-jscl iter-4 | ❌ MISSING |

**Implikasi:**
- Bisa re-evaluate sekarang: S1 iter-6 (sudah ada angka, harusnya 0.9587), S2a iter-5 (proxy untuk final), **S2b iter-6 (final)**.
- Untuk S2a iter-6 final + S2b base, perlu **re-download dari Google Drive Colab** dulu, atau pakai iter-5 sebagai approximation.

### 4.3 Cara Run

**Eval semua skenario sekaligus (yang weights-nya ada):**

```powershell
venv\Scripts\activate
pip install seqeval                    # sekali saja
python src\pseudo_labelling\SRL-NER\evaluate_seqeval.py --all
```

**Eval satu model spesifik (mis. S2b-jscl iter-6 final):**

```powershell
python src\pseudo_labelling\SRL-NER\evaluate_seqeval.py `
    --model "src\pseudo_labelling\SRL-NER\done_running\S2_Contrastive_Learning\outputs\models\S2b-jscl\bert-only-sirah-ner-S2b-jscl-0.9-iteration-6" `
    --tag "S2b-jscl-iter6"
```

**Output:**
- Console: F1 / precision / recall + per-entity report.
- Markdown: `data/result/pseudo-labelling/SRL-NER/seqeval_results.md` (tabel ringkasan + report).

**Waktu estimasi:** ~3–5 menit per model di CPU (test set ~1.700 entitas), <1 menit di GPU. Boleh jalan saat tidur kalau pakai `--all`.

### 4.4 Yang Dipakai untuk Bimbingan

Kalau sempat di-run sebelum besok:
- Demo angka entity-level S2 di samping S1 untuk argumen "contrastive bantu / tidak."
- Kalau tidak sempat, tetap bisa cerita ke Bu Diana: "metric token-level menunjukkan trend positif, re-evaluation entity-level sedang dijadwalkan."

---

## 5. File yang Bisa Ditunjukkan di Layar

Kalau Bu Diana ingin lihat artifact konkret:

| Topik | File |
|---|---|
| Periodisasi mapping | `data/result/relation_result/period_mapping.json` (15 period, 6 phase) |
| Review event period | `data/result/relation_result/event_period_review_v2.csv` (49 event, K/F/R/ADD applied) |
| Apply log | `data/result/relation_result/review_apply_log.md` |
| Graph-level metrics | `data/result/analysis/graph_metrics_v2.md` (density, transitivity, small-world) |
| Studi kasus 5 event | `data/result/analysis/case_study_events.md` + `case_study_events_cypher.md` |
| Temporal relations | `data/result/relation_result/temporal_relations.csv` (jika sudah ada) |
| Neo4j Cypher v2 | `data/result/neo4j/import_sirah_v2.cypher` |
| S2 notebook + output | `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/notebook/srl_ner_sirah_S2a_scl_colab.ipynb` (lihat sel terakhir untuk classification_report) |
| Paper S2 | `Contrastive_Learning.pdf` (di root) |
| Skenario lengkap | `srl_ner_skenario.md`, `bimbingan.md` |

---

## 6. Pertanyaan untuk Bu Diana (Urutkan dari yang paling kritis)

### Q1 — Pilih varian S2 untuk lanjut ke S3
- Lanjut SCL saja, JSCL saja, atau kedua-duanya?
- Konteks: SCL unggul di kelas paling minor (I_EVENT, I_LOCATION), JSCL unggul di B_EVENT. Macro avg keduanya hampir sama.

### Q2 — Metrik evaluasi
- Apakah token-level macro F1 (sklearn) cukup, atau perlu re-evaluate semua skenario dengan seqeval (entity-level F1)?
- Konteks: S1 sudah ada angka entity-level (0.9587), S2 hanya token-level. Untuk head-to-head perlu seqeval. Re-evaluate = re-run inferensi di test set + hitung seqeval, ~30 menit per skenario di lokal.

### Q3 — Validasi 4 cluster revisi periodisasi
- (a) Periodisasi top-down (15 period, 6 phase) — apakah granularitas oke, atau perlu lebih kasar / halus?
- (b) Temporal detection yield rendah (3 relations dari 9835 kalimat) — apakah cukup sebagai "komplementer" dari periodisasi top-down, atau perlu dieksplorasi metode lain (mis. inter-paragraph)?
- (c) Graph metrics: transitivity 0.77 = sangat tinggi (struktur klan/suku Arab). Apakah ini interpretasi yang akan masuk Bab 4, atau perlu validasi alternatif?
- (d) Studi kasus 5 event: bias coverage NER terlihat (Badr 39 person vs Tabuk 6). Bagaimana cara framing-nya di laporan — sebagai limitasi NER, atau sebagai proxy content density?

### Q4 — Periodisasi & Neo4j
- Tunjukkan `import_sirah_v2.cypher` (15 Period nodes, 36 IN_PERIOD relations). Apakah skema ini cukup untuk demo, atau perlu lebih kaya (mis. relasi antar period)?
- Pilihan demo: live import di Neo4j Desktop vs screenshot statis. Aku siapkan keduanya kalau perlu.

### Q5 — Status klaim Bab 4
- Skenario lama (E1 + S1 class weight + S2 adaptive di legacy folder) — apakah masuk Bab 4 sebagai "studi pendahuluan/ablation", atau cukup dijadikan footnote saja?

---

## 7. Action Plan Setelah Bimbingan (Tinggal Dieksekusi)

Jika Bu Diana approve arah saat ini:

1. **Re-evaluate S2a + S2b dengan seqeval di lokal** (~30 menit per skenario) untuk dapat angka entity-level head-to-head dengan S1.
2. **Run S3a + S3b di Colab** (~3–4 jam GPU per skenario).
3. **Tulis `analisis_skenario_S2_S3.md`** (file template sudah ada di `done_running/`) + update `compare_scenarios.ipynb`.
4. **Pilih winner overall** → inference ke seluruh `sirah_chunks_final.csv` → regenerate `nodes_v3.csv` + `edges_v3.csv` dengan NER baru.
5. **Re-run** temporal detection + relation extraction + SNA + Neo4j Cypher di atas v3 NER.

Jika Bu Diana minta revisi arah:
- Catat detail di `revisi_dosen.md` (Putaran 5).
- Update `bimbingan.md` & `srl_ner_skenario.md` sesuai arahan baru.
- Sesuaikan action plan.

---

## 8. Catatan Mental untuk Diri Sendiri

- **Jangan defensive** kalau Bu Diana tanya kenapa hasil S2 hanya token-level. Akui caveat: seqeval tidak ke-install di Colab, sudah ada plan re-evaluate.
- **Tunjukkan dampak konkret revisi.** Bu Diana sudah memberi 4 cluster revisi — kasih dia evidence bahwa semua sudah ditindak: tabel status di section 1.1 di atas adalah anchor utama.
- **Hindari over-promise.** Untuk S3, jangan janjikan deadline spesifik tanpa konfirmasi durasi GPU Colab dulu.
- **Tujuan utama bimbingan ini: dapatkan keputusan Q1 + Q2.** Itu yang bottleneck untuk progres minggu depan. Q3–Q5 bonus.
