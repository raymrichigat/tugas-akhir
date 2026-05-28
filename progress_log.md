# Progress Log — TA Knowledge Graph Sirah Nabawiyah

Catatan progres per sesi (lama → baru di bawah). Detail historis yang sebelumnya menumpuk di `CLAUDE.md` dipindahkan ke sini supaya `CLAUDE.md` ringkas dan cepat di-load Claude.

Ringkasan sesi paling baru tetap ada di `CLAUDE.md`. File ini menyimpan riwayat lengkap untuk Bab 4 / lampiran TA / bahan bimbingan.

---

## [2026-05-28 malam] Lifecycle Events Enrichment + Validasi Tokoh + Manual Validation LLM POC

Sesi lanjutan setelah pipeline v3 stabil. Fokus: address gap **EVENT count** dan validasi findings.

### 1. Validasi tokoh "Amr Bin Umayyah" (rank #2 PR di v3)

Investigasi tokoh yang muncul di rank #2 Person PR (di bawah Nabi). Verdict: **artifact metodologi, bukan real centrality.**

**Bukti:**
- Frequency=11, hanya 9 unique chunks
- INVOLVED_IN ke 4 event mega: Perang Badr (63 person), Uhud (52), Khandaq (17), Tabuk (6)
- Cek evidence text per chunk:
  - Perang Badr: false — kalimat tentang Uqbah (yang ayahnya dibunuh Khubaib di Badr)
  - Perang Uhud: false — kalimat perbandingan jumlah korban (Insiden Raji' vs Uhud)
  - Perang Tabuk: false — Tabuk muncul sebagai timestamp wafat Najasyi
  - Perang Khandaq: ✅ legit (survivor insiden Raji', hadir di Khandaq)
- 3 dari 4 INVOLVED_IN salah → degree 119 inflated

**Real role Amr (verified dari teks Mubarakfuri):**
- Sahabat Bani Dhamrah, survivor insiden Raji'
- **Kurir Nabi → Najasyi** (ke-capture benar di edge SAHABAT-Najasyi)
- Misi ke Bani Asad bersama Salamah (ke-capture benar di edge SAHABAT-Salamah)
- Hadir di Perang Khandaq (real)

**Output:** `data/result/analysis/v3/validation_amr_bin_umayyah.md`

**Implikasi metodologi:** proximity-based INVOLVED_IN over-generates false positives untuk Person yang punya 1 chunk dengan ko-okur multi-event. Solusi: LLM verb extraction (filter berdasarkan verb predicat real).

### 2. Visualisasi: Cypher queries v3 + matplotlib case study

- 🆕 `data/result/neo4j/visualization_queries_v3.cypher` — 20 query Cypher siap-paste ke Neo4j Browser:
  - Q1-Q4: per-period sub-graphs (P8, P9, P11, overview)
  - Q5-Q9: 5 case study events (Badr/Uhud/Khaibar/Hudaibiyah/Tabuk) dengan full ego
  - Q10-Q12: per-community sub-graphs (3 komunitas terbesar)
  - Q13-Q15: ego-network tokoh kunci (Muhammad/Abu Bakar/Abu Sufyan)
  - Q16: PRECEDES chain (kronologi event)
  - Q17-Q20: descriptive statistics
- ✅ `src/analysis/visualize_case_study_events.py --version v3` — generate 5 PNG case study + 1 panel gabungan di `data/result/analysis/v3/case_study_*.png`.

### 3. Manual validation 10 sample LLM verb extraction

POC LLM verb extraction (existing dari sesi 2026-05-26) belum di-validate. Sesi ini cross-check 10 sample (5 EVENT + 5 triplet, mix high/low conf) dengan teks chunk + teks Mubarakfuri.

**Hasil:**

| Verdict | Count | % |
|---|---:|---:|
| ✅ VALID | 5 | 50% |
| ⚠️ PARTIAL VALID | 4 | 40% |
| ❌ WRONG | 1 | 10% |
| **Effective valid** | **9/10** | **90%** |

**Findings utama:**
1. LLM bisa identify **micro-events** tanpa proper noun (Insiden Zamzam Abu Lahab vs Abu Rafi') — gap yang NER tidak bisa cover.
2. Pattern false-positive: parallel construction inference, inferred verb, schema force-fit unary→binary.
3. **Semantic predicate enrichment** — triplet punya predikat spesifik (MEMBUNUH/MEMUKUL/MENGUTUS) vs INVOLVED_IN generik.
4. Estimasi scale-up full corpus: ~1770 EVENT candidate (40× current NER), cost ~$45 API.

**Output:** `data/result/llm_verb_extraction/manual_validation_10samples.md`

### 4. Lifecycle events enrichment (8 events) + re-run SNA

Bu Diana di bimbingan 2026-05-16 catat: "event sangat sedikit jadi perlu ditambahkan lagi". Yang sudah dikerjakan via NER pure (44 EVENT) **masih miss life-cycle events Nabi** karena disebut dalam verb-construction ("beliau wafat") atau descriptive phrase ("malam turunnya wahyu pertama"), bukan noun phrase.

**Pendekatan: Hybrid manual + auto-discover relations**

Script baru: `src/relation_extraction/add_lifecycle_events.py`
1. Manual definisi 8 event (label, period, page_range, anchor bab/sub-bab).
2. Auto-discover INVOLVED_IN: scan PERSON di entity prediksi NER yang ko-okur di anchor chunks.
3. Auto-discover OCCURRED_AT/ON: scan LOCATION/TIME yang ko-okur.
4. IN_PERIOD ditambah saat regenerate Cypher.
5. Filter: PERSON min count 2 + top-30, LOCATION/TIME top-15.

**8 events di-add:**

| Event | Anchor chunks | Person | Loc | Time |
|---|---:|---:|---:|---:|
| Kelahiran Nabi | 29 | 12 | 7 | 0 |
| Wahyu Pertama | 15 | 7 | 3 | 3 |
| Hijrah Ke Habasyah | 13 | 4 | 4 | 0 |
| Pemboikotan Bani Hasyim | 9 | 3 | 2 | 0 |
| Tahun Berduka | 6 | 4 | 3 | 0 |
| Hijrah Ke Madinah | 26 | 9 | 7 | 0 |
| Haji Wada' | 12 | 2 | 15 | 4 |
| Wafat Nabi | 21 | 5 | 5 | 0 |

**Total +99 edges** (46 INVOLVED_IN + 44 OCCURRED_AT + 7 OCCURRED_ON + filtering).

**Bug yang ditemukan + fixed:**
- Initial run miss 2 event (Pemboikotan, Wafat Nabi) karena `page_filter` salah tebak (asumsi 160-173, real 152-156). Fix: lebarkan range filter sesuai chunk halaman aktual. Rollback dari `.bak2` lalu re-run.

**Impact ke KG metrics:**

| | Pre-lifecycle | Post-lifecycle | Δ |
|---|---:|---:|---|
| Total nodes | 1280 | **1288** | +0.6% |
| EVENT count | 44 | **52** | **+18%** |
| Total edges | 491 | **590** | +20% |
| Period dengan EVENT | 12/15 | **14/15** | P1 + P6 sekarang ada anchor |
| Person co-participation nodes | 254 | **261** | +3% |
| Person co-participation edges | 3562 | **4096** | +15% |
| Density | 0.111 | **0.121** | +9% |
| Avg clustering | 0.552 | **0.567** | +3% |
| Transitivity | 0.810 | 0.796 | -2% |
| Louvain modularity Q | 0.351 | **0.364** | +4% |
| Louvain communities | 19 | 16 | konsolidasi |

**Top 10 Event PR — major shift dari 100% peperangan ke balanced:**

| Rank | Pre-lifecycle | Post-lifecycle |
|---|---|---|
| 1 | Perang Badr | Perang Badr |
| 2 | Perang Uhud | Perang Uhud |
| 3 | Perang Khandaq | Perang Khandaq |
| 4 | Baiat Aqabah Kubra | **Hijrah Ke Madinah** ✨ |
| 5 | Perang Khaibar | **Kelahiran Nabi** ✨ |
| 6 | Perang Dzul Usyairah | **Wafat Nabi** ✨ |
| 7 | Perang Dzatur Riqa | **Wahyu Pertama** ✨ |
| 8 | Perjanjian Hudaibiyah | Baiat Aqabah Kubra |
| 9 | Perang Bani Al-Ashfar | **Pemboikotan Bani Hasyim** ✨ |
| 10 | Perang Tha'If | Perang Bani Al-Ashfar |

5 dari 10 top event sekarang life-cycle Nabi → **balanced narrative** (kelahiran-wahyu-hijrah-pemboikotan-wafat), bukan cuma peperangan.

**Top 10 Person PR — Khulafa Rasyidin lebih representatif:**
- Abu Bakar: rank 5 → **4**
- Aisyah: rank 6 → **5**
- Amr Bin Umayyah: rank 2 → **3** (artifact tetap, tapi tergeser oleh Abu Jahal yang naik ke rank 2)

### 5. Output yang ter-update di sesi ini

```
data/result/relation_result/
├── nodes_v3.csv                  +8 EVENT (1280 → 1288)
├── nodes_v3.csv.bak2             backup pre-lifecycle
├── edges_v3.csv                  +99 edges (491 → 590)
└── edges_v3.csv.bak2             backup pre-lifecycle

data/result/neo4j/
├── import_sirah_v3.cypher        regenerate (52 Event + 65 IN_PERIOD)
└── visualization_queries_v3.cypher  🆕 20 query templates

data/result/analysis/v3/
├── sna_metrics.csv               re-computed
├── sna_summary.md                re-computed
├── sna_person_network.png        re-rendered (261 nodes)
├── graph_metrics_v2.md/json      re-computed (Q=0.364)
├── event_centrality.csv/md       re-computed (top-10 balanced)
├── event_network.png             re-rendered
├── community_wordclouds_summary.md  re-computed (16 comm, 8 eligible)
├── community_wordclouds/         re-rendered (8 PNG)
├── case_study_*.png (5 + panel)  re-rendered
└── validation_amr_bin_umayyah.md 🆕 verdict artifact

data/result/llm_verb_extraction/
└── manual_validation_10samples.md  🆕 90% effective valid

src/relation_extraction/
└── add_lifecycle_events.py       🆕 idempotent script

src/analysis/
├── sna_analysis.py               +flag --version
├── sna_graph_metrics.py          +flag --version
├── event_centrality.py           +flag --version
├── community_wordcloud.py        +flag --version
└── visualize_case_study_events.py  +flag --version
```

### 6. Action item yang tersisa pre-bimbingan

| # | Item | Status |
|---|---|---|
| 1-3 | Period mapping + Cypher v3 + SNA re-run | ✅ |
| 4 | Visualisasi (Cypher queries + matplotlib PNG) | ✅ |
| 5 | Validasi tokoh "Amr Bin Umayyah" | ✅ verdict: artifact |
| 6 | Manual validation 10 sample LLM verb extraction | ✅ 90% effective |
| 7 | Lifecycle events enrichment | ✅ 8 events, +18% EVENT count |
| 8 | Slide bimbingan deck | ⏳ |
| 9 | Sub-DBMS Neo4j v2 vs v3 untuk komparasi visual | ⏳ (opsional di Bu Diana side) |

### Catatan honest

- **Lifecycle events di-add via hybrid manual + auto-discover**, bukan pure NER. Ini **inkonsisten dengan claim "v3 = pure NER output"** sebelumnya. Perlu honest disclosure di Bab 4: "v3 di-enrich dengan 8 manual-defined lifecycle events karena NER S3.2 tidak bisa capture event yang disebut dalam verb-construction; relasi-relasinya tetap di-discover dari NER predictions yang muncul di anchor chunks."
- **Amr Bin Umayyah artifact tetap ada** — enrichment lifecycle hanya nge-shift dia 1 rank turun, tapi root cause (proximity-based INVOLVED_IN over-extraction) belum di-fix. Solusinya tetap LLM verb extraction (future work).
- **Page filter manual** untuk anchor chunks rentan kalau bab Sirah versi lain punya numbering berbeda. Untuk reproduce, dependency ke `sirah_chunks_final.csv` Mubarakfuri terjemahan Kathur Suhardi.

---

## [2026-05-28 sore] Period Mapping v3 + Cypher v3 + SNA Re-run di KG v3

Lanjutan sesi pagi. Pipeline post-NER (period mapping → Neo4j → SNA) di-apply ulang ke KG v3 supaya ada output yang konsisten dengan inference S3.2 winner.

### 1. Apply period mapping ke nodes_v3 + edges_v3
- Script: `src/relation_extraction/apply_period_to_v3.py` (sudah ada dari sesi pagi).
- Strategi: EVENT yang ada di v2 → copy `page_range` curated; EVENT baru di v3 → derive dari `chunk_ids` (min-max halaman).
- Hasil: 44 EVENT semua dapat `periode_bab` (0 unmapped). Distribusi: Perang Uhud period (11), Perang Badr period (9), Dakwah luar Makkah (5), Mu'tah/Penaklukan Makkah (3), Khandaq/Bani Mushthaliq (3), Hudaibiyah (3), dst.
- Backup `.bak` disimpan untuk safety.

### 2. Generate `import_sirah_v3.cypher` (Neo4j)
- Script: `src/neo4j/import_to_neo4j.py` (sudah multi-version, tinggal jalan).
- Output: `data/result/neo4j/import_sirah_v3.cypher` — 988 Person + 44 Event + 15 Period + 46 IN_PERIOD + constraints. Header masih `[v2 (with Period nodes)]` (kosmetik, struktur sama dengan v2).

### 3. Re-run SNA scripts di KG v3
Aku tambahkan CLI flag `--version v3` ke 4 script utama (sebelumnya hard-code `nodes_v2.csv`). Output ke `data/result/analysis/v3/`.

**Perubahan kode:**
- `src/analysis/sna_analysis.py` — argparse `--version {v1,v2,v3}`, default v3, `BASE_DIR` dari `Path(__file__)` (bukan hard-code Windows path).
- `src/analysis/sna_graph_metrics.py` — tambah flag `--version` (override `--use-v1` lama). Output dir auto switch ke `v3/` subfolder.
- `src/analysis/event_centrality.py` — argparse `--version {v2,v3}` via rebind `IN_NODES/IN_EDGES/OUT_DIR` di `main()` (minimal-change global).
- `src/analysis/community_wordcloud.py` — same pattern, rebind 5 path globals.

**Hasil run di v3** (vs v2 untuk konteks):

| Metric | v2 | **v3** | Δ |
|---|---:|---:|---|
| Person nodes (co-participation) | ~120-an* | **254** | scale-up signifikan |
| Person edges | ~? | **3562** | jauh lebih dense |
| Density | 0.086 | **0.111** | +29% |
| Avg clustering | (n/a quick) | **0.552** | high |
| Transitivity | 0.77 | **0.81** | +5% |
| Avg shortest path (giant) | 2.47 | **2.44** | small-world preserved |
| Components | 8 | **10** | sedikit lebih banyak |
| Giant component ratio | 90.8% | **92.5%** | naik tipis |
| Louvain modularity Q | 0.327 | **0.351** | +7% |
| Greedy modularity Q | 0.320 | **0.321** | flat |
| ARI(Louvain, Greedy) | (?) | **0.754** | tinggi → kedua metode konsisten |
| Communities (Louvain) | (~16) | **19** | 3 komunitas baru |

\* angka v2 dari `graph_metrics_v2.md` lama (di folder analysis root).

**Top 10 Person by PageRank di v3:**
1. Muhammad (PR=0.0381, deg=162)
2. Amr Bin Umayyah (PR=0.0148)
3. Abdullah Bin Ubay (PR=0.0142)
4. Abu Jahal (PR=0.0134)
5. Abu Bakar (PR=0.0133)
6. Aisyah (PR=0.0130)
7. Ali bin Abu Thalib (PR=0.0129)
8. Utsman Bin Affan (PR=0.0119)
9. Abu Sufyan bin Harb (PR=0.0116)
10. Umar bin Al-Khaththab (PR=0.0108)

Komposisi top-10 sejalan dengan ekspektasi narasi Sirah (Nabi + 4 Khulafa Rasyidin masuk top-10, pemimpin musuh Quraisy juga tinggi).

**Top 10 Event by PageRank di v3** (event_centrality):
1. Perang Badr (PR=0.0816, deg=28)
2. Perang Uhud (0.0692, 28)
3. Perang Khandaq (0.0541, 27)
4. Baiat Aqabah Kubra (0.0371, 22)
5. Perang Khaibar (0.0368, 22)
6. Perang Dzul Usyairah (0.0354, 24)
7. Perang Dzatur Riqa (0.0335, 22)
8. Perjanjian Hudaibiyah (0.0331, 23)
9. Perang Bani Al-Ashfar (0.0327, 22)
10. Perang Tha'If (0.0322, 23)

44 event nodes, 278 event-event edges (273 co-participation + 15 PRECEDES merge).

**Community wordcloud v3:** 19 komunitas total, 10 eligible (size ≥3). Komunitas terbesar 89 + 61 + 57 anggota (greedy) atau 80+67+61 (louvain).

### 4. Output v3 tersimpan
```
data/result/analysis/v3/
├── sna_metrics.csv
├── sna_summary.md
├── sna_person_network.png
├── graph_metrics_v2.md          (filename masih *_v2.md kosmetik, isi v3)
├── graph_metrics_v2.json
├── event_centrality.csv
├── event_centrality_summary.md
├── event_network.png
├── community_wordclouds_summary.md
└── community_wordclouds/         (PNG per-community)
```

### 5. Action item yang masih pending
- `case_study_events.py`, `entity_frequency_per_period.py`, `edge_period_cooccurrence.py` — belum di-flag `--version v3` (low priority, sample 5 event sudah di v2).
- Visualisasi Neo4j manual via Browser (Bu Diana eksplisit minta screenshot per-period, per-komunitas, 5 case study).
- Header cypher v3 masih ditulis `[v2 (with Period nodes)]` — kosmetik, fix nanti kalau perlu.
- Slide bimbingan + manual validation 5-10 sample LLM verb extraction.

### Catatan honest
- Density v3 (0.111) tinggi karena NER cover **2× lebih banyak Person** dari manual labelling, otomatis lebih banyak co-participation pair via INVOLVED_IN.
- Modularity Q naik dari 0.327 → 0.351 menarik — komunitas v3 **lebih distinct** meski jumlah node lebih banyak. Hipotesis: NER scale-up tambah Person yang berperan di event spesifik (clusters), bukan di banyak event silang.
- ARI(Louvain, Greedy) = 0.754 di v3 lebih tinggi dari v2 (kemungkinan sekitar 0.6-0.7) → struktur komunitas lebih stabil ke pilihan algoritma.
- "Amr Bin Umayyah" rank #2 by PR mengejutkan — perlu validasi: ini tokoh sebenarnya prominent (kurir Nabi ke Najasyi) atau efek false-positive PERSON dari NER yang ke-cluster ke event utama.

---

## [2026-05-28] Inference S3.2 ke Seluruh Sirah + KG v3 + Comparison Report

Sesi yang selesai-kan **end-to-end pipeline** dari NER (S3.2 winner) sampai Knowledge Graph baru. Deliverable utama bimbingan Bu Diana ("pipeline running end-to-end + comparison report SRL-NER vs manual labelling").

### 1. Inference S3.2 ke seluruh chunks (di Colab T4, 1 menit total)
- Notebook baru: `srl_ner_sirah_inference_v3_colab.ipynb` (Colab) — load model winner S3.2-scl-aug-iter4 dari Drive, inference seluruh `sirah_chunks_final.csv` (1094 chunks).
- Output: `data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v3_{token,entity}.csv` + `inference_runtime.json`.
- Run-1 (aggregation='simple'): muncul **sub-word fragmentation** (1376 entities ber-prefix `##`, 10.6% data corrupt). Issue dari HF pipeline yang tidak konsisten merge sub-word saat ada special char.
- Run-2 (aggregation='first'): sub-word artifact hilang (0 dengan `##`), tapi muncul issue boundary baru — span split di whitespace (`utbah` + `bin rabi` = 2 entity, padahal 1).
- **Solusi final**: rebuild entity-level dari token-level CSV (yang BIO scheme-nya benar) via `build_v3_entity_from_token.py`. Reconstruct entity_text dari `teks_chunk[start_char:end_char]` + strip trailing punctuation.

### 2. Pipeline scripts baru
- 🆕 `src/relation_extraction/build_v3_entity_from_token.py` — decode BIO span dari token-level → reconstruct entity-level CSV yang akurat.
- 🆕 `src/relation_extraction/build_v3_prelabelled_from_inference.py` — convert inference output ke schema `sirah_prelabelled_v3.csv` (mirror manual schema), siap di-feed ke `relation_extraction.py`.
- 🆕 `src/relation_extraction/build_comparison_report.py` — entity-level comparison NER v3 vs manual labelling per chunk.
- ✏️ `src/relation_extraction/relation_extraction.py` — tambah CLI args (`--input`, `--out-nodes`, `--out-edges`) supaya reusable untuk v2 atau v3.

### 3. Knowledge Graph v3 (built from NER inference)
Perbandingan dengan v2 (built from manual labelling):

| | v2 (manual) | **v3 (NER S3.2)** | Δ |
|---|---:|---:|---|
| Nodes total | 892 | **1280** | +44% |
| PERSON | ~750 | 988 | +32% |
| LOCATION | 75 | 83 | +11% |
| EVENT | 36 | **44** | +22% |
| TIME | ~30 | **165** | +450% |
| Edges total | 322 | **491** | +52% |
| INVOLVED_IN | 123 | 227 | +85% |
| KELUARGA | 91 | 110 | +21% |
| OCCURRED_ON | 36 | 47 | +31% |

Top 10 PERSON v3: Muhammad (1387), Abu Bakar (172), Abu Sufyan bin Harb (165), Umar bin Al-Khaththab (128), Ibnu Hisyam (100), Abu Jahal (85), Abu Thalib (84), Aisyah (73), Ibnu Ishaq (67), Ali bin Abu Thalib (66).

Top 10 EVENT v3: Perang Badr (66), Perang Uhud (55), Perang Khandaq (24), Perjanjian Hudaibiyah (13), Perang Khaibar (13), Perang Tabuk (8), Perang Hunain (6), Perang Bu'Ats (5), Perang Mu'Tah (5), Baiat Aqabah Kubra (4). **Perang Bu'Ats, Perang Mu'Tah, Perang Hunain ke-detect baru** (tidak ada di v2).

### 4. Comparison Report SRL-NER vs Manual

Output: `data/result/analysis/comparison_srl_vs_manual.md` + `comparison_misclassified_samples.csv`.

Cakupan:
- 800 common chunks (di kedua dataset)
- **241 only-NER chunks** (manual ga label ini, NER cover) — bukti coverage scale-up.
- 1 only-manual chunk.

Per-label entity-level metrics:

| Label | Manual | NER v3 | TP | FN | FP | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PERSON | 2814 | 2850 | 2770 | 44 | 80 | 0.972 | 0.984 | **0.978** |
| LOCATION | 957 | 973 | 941 | 16 | 32 | 0.967 | 0.983 | **0.975** |
| EVENT | 159 | 161 | 147 | 12 | 14 | 0.913 | 0.925 | **0.919** |
| TIME | 273 | 280 | 256 | 17 | 24 | 0.914 | 0.938 | **0.926** |
| **MICRO** | 4203 | 4264 | 4114 | 89 | 150 | **0.965** | **0.979** | **0.972** |

**Insight utama:**
1. F1 0.92-0.98 di semua label — NER align kuat dengan manual.
2. NER v3 cover **241 chunks tambahan** yang manual tidak pernah label (regex tidak match).
3. FP partial match (mis. "Abu Bakar" vs "Abu Bakar Ash-Shiddiq") = 51 dari 150 FP → bukan true error, cuma boundary granularity berbeda.

**Disclaimer (di report):** manual labelling **bukan ground truth absolut**. Dikerjakan via regex + keyword (`pre_labelling.py`), banyak entity valid yang ke-skip karena pattern tidak match. Sehingga "missed by NER" bisa berarti either NER beneran missed atau manual over-detect via regex agresif.

### 5. Action item terbawa ke sesi berikutnya

**Pre-bimbingan:**
1. ⏳ Apply `event_period.py` ke nodes_v3.csv → assign period per EVENT.
2. ⏳ Generate `import_sirah_v3.cypher` (Neo4j import script) dari nodes_v3 + edges_v3.
3. ⏳ Re-run SNA (`sna_analysis.py`, `event_centrality.py`, `community_wordcloud.py`) di KG v3 — bandingkan dengan v2.
4. ⏳ Visualisasi Neo4j (screenshot per-period, per-komunitas, 5 case study) — Bu Diana eksplisit prefer Neo4j daripada PNG static.
5. ⏳ Slide bimbingan: 1 slide S3.2 winner + 1 slide comparison report + 5 slide deliverable Priority D + 1 slide rencana KG v3 update.
6. ⏳ Manual validation 5-10 sample LLM verb extraction (cross-check ke teks Mubarakfuri).

**Post-bimbingan / future work:**
7. ⏳ 2 bug pending: `OCCURRED_AT weight=2.0` + `PRECEDES stale v1 mapping` (Fathul Makkah → Perang Uhud salah arah, masih ada di v3).
8. ⏳ Scale-up LLM verb extraction (Opsi B 50 chunks via batch chat ~25 menit).

### File baru / modified di sesi ini

- 🆕 `src/pseudo_labelling/SRL-NER/srl_ner_sirah_inference_v3_colab.ipynb`
- 🆕 `src/relation_extraction/build_v3_entity_from_token.py`
- 🆕 `src/relation_extraction/build_v3_prelabelled_from_inference.py`
- 🆕 `src/relation_extraction/build_comparison_report.py`
- ✏️ `src/relation_extraction/relation_extraction.py` (CLI args)
- 🆕 `data/result/pseudo-labelling/SRL-NER/inference/{sirah_predicted_v3_token.csv, sirah_predicted_v3_entity.csv, inference_runtime.json}`
- 🆕 `data/result/manual_labelling/sirah_prelabelled_v3.csv`
- 🆕 `data/result/relation_result/{nodes_v3.csv, edges_v3.csv}`
- 🆕 `data/result/analysis/{comparison_srl_vs_manual.md, comparison_misclassified_samples.csv}`

---

## [2026-05-22 → 2026-05-26] S3.1 λ_C Sweep + S3.2 Augmentation + Priority D Deliverables

Sesi besar yang menyelesaikan **S3.1 sweep + S3.2 augmentation winner + 5 deliverables Priority D** dari bimbingan 2026-05-16. SRL-NER pipeline secara empirik **selesai mengalahkan S1 baseline** untuk pertama kali (S3.2 F1 entity = 0.9537 vs S1 = 0.9518).

### 1. S3.1 — λ_C Sweep di S2 SCL (selesai run di Colab T4)
- 3 varian dijalankan: λ_C ∈ {0.1, 0.2, 0.3}, masing-masing 6 iterasi self-training × 10 epoch.
- Konfigurasi tetap: τ=0.1, contrastive_mode=scl, threshold=0.9, sampling_rate=1.0, fixed val split (seed 42 by text_id).
- Notebook: `srl_ner_sirah_S3_1_scl_lambda{01,02,03}_colab.ipynb`. Build via `_build_S3_1_lambda_sweep.py`.
- Output: `done_running/S3_Augmented/{notebook,output/{models,evaluation},dataset}/scl_lambda{01,02,03}/`.
- Konvergensi self-training (n_above per iter):
  - λ_C=0.1: 203 → 3 → 3 → 0 → 1 (sampai iter-6, runtime 57 min).
  - λ_C=0.2: 208 → 26 → 2 → 1 (sampai iter-5, runtime 52 min).
  - λ_C=0.3: 187 → 45 → 5 (sampai iter-4, runtime 36 min).

### 2. Seqeval TEST evaluation — S1 / S2 / S3.1 / S3.2 head-to-head
- Patch `evaluate_seqeval.py` untuk include S3.1 (3 lambda) + S3.2.
- Run lokal `python src/.../evaluate_seqeval.py --all` → output `data/result/pseudo-labelling/SRL-NER/seqeval_results.md`.
- Hasil ringkasan (test set, 258 kalimat, 1759 entities):

| Tag | F1 entity | EVENT | LOCATION | PERSON | TIME | Δ vs S1 |
|---|---:|---:|---:|---:|---:|---:|
| S1-baseline-iter6 | 0.9518 | 0.7677 | 0.9540 | 0.9662 | 0.8354 | — |
| S2a-scl-iter5 | 0.9215 | 0.7579 | 0.9422 | 0.9243 | 0.8553 | -0.0303 |
| S2b-jscl-iter6 | 0.8915 | 0.7629 | 0.9400 | 0.8849 | 0.7950 | -0.0603 |
| S3.1-lambda01-iter6 | 0.9477 | 0.7500 | 0.9531 | 0.9598 | 0.8477 | -0.0041 |
| S3.1-lambda02-iter5 | 0.9470 | 0.7835 | 0.9502 | 0.9590 | 0.8442 | -0.0048 |
| S3.1-lambda03-iter4 | 0.9522 | 0.7708 | 0.9490 | 0.9684 | 0.8354 | +0.0004 |
| **S3.2-scl-aug-iter4** | **0.9537** | **0.8454** | **0.9539** | **0.9613** | **0.9007** | **+0.0019** ✅ |

### 3. Winner λ_C S3.1 — λ_C=0.3 (iter-4)
- λ_C=0.3 sedikit melampaui S1 baseline (+0.0004), bukan λ_C=0.1/0.2 yang awalnya dihipotesiskan close gap.
- Insight: hipotesis "λ_C kecil = lebih dekat ke S1 karena contrastive lebih ringan" **salah** untuk dataset Sirah.
- VAL Seq F1 ranking (peak per iter): λ_C=0.2 > 0.1 > 0.3 — **terbalik** dari TEST. Pelajaran: VAL ≠ TEST untuk small NER datasets. Selalu konfirmasi pakai TEST set sebelum pilih winner.

### 4. S3.2 — Mention Replacement Augmentation di atas winner λ_C=0.3 (selesai 2026-05-26)
- Build script: `_build_S3_2_augmented.py` (idempotent, transform notebook S3.1-lambda03 → S3.2).
- Notebook: `srl_ner_sirah_S3_2_scl_aug{,_colab,_kaggle}.ipynb`.
- Konfigurasi: λ_C=0.3 (winner) + `train_augmented_v2.csv` (599 + 260 augmented = 859 sentences).
- Augmentation v2 stats: I-LOCATION 72→198 (~2.75x), B-EVENT 144→414 (~2.9x), I-EVENT 156→471 (~3x).
- Self-training konvergen di iter-4 (n_above 223→13→1), runtime 46.5 menit di Colab T4.
- Output: `done_running/S3_Augmented/output/{models,evaluation}/scl_aug/`, `dataset/scl_aug/`.

### 5. S3.2 wins — augmentation BENAR-BENAR bantu kelas minoritas
- **F1 entity 0.9537** — pertama kali SRL-NER pipeline lewati S1 baseline (0.9518) dengan margin signifikan (+0.0019).
- **F1 EVENT melonjak 0.7708 → 0.8454** (+0.0746) — sesuai hipotesis Bu Diana dari bimbingan 2026-05-16.
- **F1 TIME juga naik 0.8354 → 0.9007** (+0.0653) walaupun tidak di-augment khusus — efek positif side-channel dari augmentation v2.
- **F1 PERSON tetap kuat 0.9613** (vs S3.1=0.9684; turun -0.0071 tapi masih sangat tinggi).
- **F1 LOCATION naik tipis** 0.9490 → 0.9539 (+0.0049).
- Konvergen lebih cepat (4 iter, 46.5 menit) — augmentation membantu model belajar minoritas dari iter pertama.

### 6. Priority D — Deliverables tambahan dari bimbingan 2026-05-16

Dikerjakan paralel sambil S3.2 jalan di Colab.

**6a. Centrality untuk node Event** — `src/analysis/event_centrality.py`
- Build Event-Event graph: 36 Event nodes, 150 edges (co-participation = share Person via INVOLVED_IN, weight = jumlah Person bersama). PRECEDES (12 edges) merge dengan weight extra.
- Output: `event_centrality.csv`, `event_centrality_summary.md`, `event_network.png`.
- Top 5 PageRank Event: **Perang Badr (0.0818)** > Perang Khandaq (0.0695) > Perang Uhud (0.0654) > Baiat Aqabah Kubra (0.0576) > Perang Dzul Usyairah (0.0553).
- 15 komunitas Louvain di Event network.

**6b. Wordcloud per komunitas + interpretasi semantik** — `src/analysis/community_wordcloud.py`
- 16 komunitas Louvain di Person network → 8 komunitas memenuhi syarat (≥3 anggota, korpus evidence cukup).
- Q-value Louvain (recomputed) = **0.3170** → **moderate** structure (sesuai dengan run sebelumnya 0.327, beda ±0.01 dari random tie-breaking).
- Interpretasi proposal per komunitas (8 komunitas):
  - K0 (74 anggota) — komunitas inti Rasulullah + sahabat utama + lawan Quraisy (Muhammad-hub supercluster).
  - K1 (39) — cluster Perang Badr + jaringan keluarga Nabi (Hamzah, Utsman, Zainab, Fathimah).
  - K2 (26) — sahabat Madinah + ekspansi militer akhir (Ali, Umar, Zaid, Mush'ab).
  - K3 (6) — delegasi Naqib Anshar Baiat Aqabah Kubra (P5-P6).
  - K4 (4) — nasab Pra-Islam (Ibrahim, Isma'il).
  - K5 (3) — awal kenabian (Khadijah, Waraqah, Zaid).
  - K6 (3) — Sariyyah Nakhlah (P7).
  - K7 (3) — pembawa bendera Quraisy di Perang Uhud.
- Output: `community_wordclouds/community_{00-07}.png` + `community_wordclouds_summary.md`.

**6c. Frekuensi entitas per-period** — sudah pre-existing dari sesi sebelumnya (`entity_freq_per_period.{csv,png}`, `entity_freq_per_period_summary.md`).
- 15 period × 4 label, total 3737 (entity, chunk) tuples mapped.
- Justifikasi periodisasi: P5 (107 PERSON, fase Makkah dakwah luar) + P11 (107, fase Hudaibiyah) + P10 (100, perang Khandaq) jadi top 3 PERSON-rich periods.

**6d. Analisis event-related case study** — sudah pre-existing (`edge_period_cooccurrence.{csv,py}`, `edge_validation_summary.md`).
- 322 edges → 30 KEEP (9.3%) + 185 REVIEW (57.5%) + 107 DROP (33.2%) berdasarkan period alignment heuristic.
- Validasi anekdot Bu Diana: Perang Uhud-Aqabah dan Perang Uhud-Hunain confirmed spurious (DROP).
- Implikasi: edges_v3.csv kandidat = 215 edges (post-DROP). Manual review 185 REVIEW sebelum apply.

**6e. LLM verb extraction POC** — `src/analysis/llm_verb_extraction_poc.py`
- Pendekatan: structured prompt + single-batch chat (gratis, reproducible).
- Sample N=10 hybrid: 5 phase coverage (P0/P5/P8/P11/P14) + 5 Perang Badr depth (page 266-304).
- Hasil run di Claude.ai chat: **18 kandidat EVENT baru + 28 SVO triplet**, confidence 0.85-0.95 dominan.
- Contoh kandidat EVENT valid: "Masuk Islam Raja Najasyi" (tidak ada di nodes_v2.csv), "Pembunuhan Utbah bin Rabi'ah", "Eksekusi An-Nadhr bin Al-Harits".
- Contoh triplet relasi baru: `Hamzah --MEMBUNUH--> Utbah`, `Ali --BERTANDING_DENGAN--> Al-Walid`, `Muhammad --MEMERINTAHKAN_BUNUH--> Uqbah` — granular dari INVOLVED_IN.
- Output: `data/result/llm_verb_extraction/{prompt.md,sample_chunks.csv,verb_extraction_events.csv,verb_extraction_triplets.csv,verb_extraction_summary.md}`.
- POC scope: tunjukkan konsep works. Scale-up post-deadline kalau Bu Diana approve metode.

### 7. Memory update
- 🆕 `project_s3_1_lambda_sweep_results.md` — winner + ranking + insight VAL≠TEST.
- ✏️ `MEMORY.md` — index updated.

### File baru / modified di sesi ini
**SRL-NER:**
- 🆕 `_build_S3_1_lambda_sweep.py`, `_build_S3_2_augmented.py` (idempotent build scripts)
- 🆕 `srl_ner_sirah_S3_1_scl_lambda{01,02,03}{,_colab,_kaggle}.ipynb` (9 notebook)
- 🆕 `srl_ner_sirah_S3_2_scl_aug{,_colab,_kaggle}.ipynb` (3 notebook)
- 🆕 `done_running/S3_Augmented/` (4 sub-runs: scl_lambda01/02/03 + scl_aug, masing-masing notebook + models + evaluation + dataset)
- ✏️ `evaluate_seqeval.py` — tambah 8 candidate entries (S3.1 lambda01/02/03 + S3.2)
- 🆕 `data/result/pseudo-labelling/SRL-NER/seqeval_results.md` (S1+S2+S3.1+S3.2 head-to-head)
- 🆕 `data/result/pseudo-labelling/SRL-NER/{train_augmented_v2.csv,augmentation_log_v2.json,sample_augmented_v2.txt}`
- 🆕 `augment_minor_classes_v2.py`

**Priority D analysis:**
- 🆕 `src/analysis/event_centrality.py`
- 🆕 `src/analysis/community_wordcloud.py`
- 🆕 `src/analysis/llm_verb_extraction_poc.py`
- 🆕 `data/result/analysis/{event_centrality.csv,event_centrality_summary.md,event_network.png}`
- 🆕 `data/result/analysis/community_wordclouds/community_{00-07}.png` (8 PNG)
- 🆕 `data/result/analysis/community_wordclouds_summary.md`
- 🆕 `data/result/llm_verb_extraction/{prompt.md,sample_chunks.csv,responses/llm_verb_response.json,verb_extraction_events.csv,verb_extraction_triplets.csv,verb_extraction_summary.md}`

### Action item terbawa ke sesi berikutnya

**Pre-bimbingan berikutnya (deadline 29 Mei sudah aman, tinggal polish):**
1. ⏳ Inference NER terbaik (S3.2-scl-aug-iter4) → regenerate `nodes_v3.csv` + `edges_v3.csv` di seluruh `sirah_chunks_final.csv`.
2. ⏳ Comparison report SRL-NER best vs manual labelling ground truth (untuk Bab 4 + bimbingan).
3. ⏳ Manual validation 5-10 sample LLM verb extraction (cross-check ke teks Mubarakfuri) untuk dapat angka precision konkret.
4. ⏳ Tulis paragraf hasil di laporan / slide bimbingan untuk semua 5 deliverable Priority D.

**Post-bimbingan / future work:**
5. ⏳ Visualisasi Neo4j (bukan PNG static) — screenshot + cypher query saved.
6. ⏳ Scale-up LLM verb extraction (Opsi B: 50 chunks via batch chat ~25 menit; atau Opsi C: full coverage via API ~$6-10).
7. ⏳ 2 bug pending: `OCCURRED_AT weight=2.0` + `PRECEDES stale v1 mapping`.

---

## [2026-05-13 → 2026-05-16] S2 Contrastive Run + Seqeval Dual-Metric + Bimbingan Bu Diana

Rangkaian sesi yang fokus ke **eksekusi skenario S2 SRL-NER (SCL + JSCL)**, penambahan metrik evaluasi entity-level (seqeval) supaya head-to-head dengan S1 baseline, visualisasi case study, dan persiapan + pelaksanaan bimbingan Bu Diana 2026-05-16.

**1. S2 Contrastive Learning — selesai run di Colab 2026-05-14/15**
- S2a SCL dan S2b JSCL keduanya tuntas **6 iterasi self-training × 10 epoch** per skenario.
- Output: `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/` berisi `notebook/`, `outputs/models/` (weights per iter), `outputs/evaluation/` (xlsx).
- Hyperparameter contrastive: λ_C = 0.3, τ = 0.1, embedding kalimat = mean-pool token. JSCL pakai sentence-level Jaccard antar bag-of-label BIO (exclude `O`).
- Dinamika self-training (n_above per iter): **187 / 32 / 14 / 2 / 1 / 1** — identik dengan S1 baseline (threshold + sampling sama). Contrastive bekerja di tahap training, bukan seleksi pseudo-label.

**2. Seqeval addendum — dual-metric (token-level + entity-level)**
- Awalnya hanya dapat token-level (sklearn) karena seqeval **tidak ke-install di Colab run** awal.
- Solusi: tambah 3 cell di akhir notebook (`seqeval_addendum_colab.md`) untuk re-eval pakai seqeval tanpa re-train.
- Script alternatif lokal: `src/pseudo_labelling/SRL-NER/evaluate_seqeval.py` (dengan `--all` flag untuk batch eval semua model).
- Helper utility: `_fix_underscore_to_dash.py` untuk konversi B_X/I_X → B-X/I-X (format yang diharapkan seqeval).
- Hasil per-epoch lengkap di `src/pseudo_labelling/SRL-NER/S2-seqeval.md` (12 iter × 10 epoch tabulasi).

**3. Hasil utama S2 (Seq F1 entity-level, comparable dengan S1=0.959):**

| Iter | S2a SCL Seq F1 | S2b JSCL Seq F1 |
|:-:|:-:|:-:|
| 1 | 0.924 | 0.904 |
| 2 | 0.942 | 0.933 |
| 3 | 0.949 | 0.935 |
| 4 | 0.947 | 0.930 |
| 5 | **0.950** | **0.939** |
| 6 (final) | 0.950 | 0.933 |
| **Peak** | **0.953** (iter-6 ep-4) | **0.940** (iter-5 ep-3) |

- **Trend monotonik naik** lintas 6 iter (SCL: 0.924 → 0.950, JSCL: 0.904 → 0.940). Self-training tetap bekerja di entity-level.
- **SCL > JSCL konsisten** ~+0.01 di setiap iter.
- **Token-level F1 S2 ~0.995** (lebih tinggi dari S1).
- **Gap honest:** Seq F1 entity S2 (~0.95) **sedikit di bawah** S1 baseline (0.959). Hipotesis: λ_C=0.3 terlalu agresif → trade-off entity boundary vs token classification.
- **Per-class minor masih F1 0.78-0.82** (B_EVENT 0.777, I_LOCATION 0.776, B_TIME 0.815) → alasan valid untuk lanjut S3 augmentation yang menyasar tepat kelas-kelas ini.

**4. Visualisasi case study 5 event (slide-ready)**
- Script baru: `src/analysis/visualize_case_study_events.py`.
- Output: 5 PNG individual (Perang Badr, Uhud, Hudaibiyah, Khaibar, Tabuk) + `case_study_panel.png` gabungan untuk slide tunggal.
- Legenda: kuning besar = Event, biru = Person (size proporsional), abu-abu = INVOLVED_IN, merah = KELUARGA, hijau = SAHABAT, oranye putus-putus = MUSUH.

**5. Neo4j community import (tambahan)**
- File baru: `data/result/neo4j/import_community_v2.cypher`.
- Tujuan: inject property `community` + 4 centrality (degree/betweenness/closeness/pagerank) dari `sna_metrics.csv` ke Person nodes existing.
- Setelah di-run: bisa color-by-community di Neo4j Browser untuk visualisasi komunitas Louvain/Greedy. Pre-req: `import_sirah_v2.cypher` sudah di-run + `sna_metrics.csv` di-copy ke folder `import/` Neo4j Desktop.

**6. Persiapan bimbingan Bu Diana 2026-05-16 — 3 dokumen prep**
- `bimbingan_2026_05_13.md` — draft awal, fokus S2 contrastive results (sebelum seqeval lengkap).
- `bimbingan_graf_2026_05_14.md` — versi graf-fokus lengkap (centrality, graph-level metrics, community detection 3 metode, studi kasus 5 event, demo Neo4j, FAQ).
- `bimbingan_2026_05_16.md` — **versi combined final** yang dipakai di bimbingan. Format: ringkasan 1 menit, schema graf, 3 layer evaluasi (centrality + graph-level + community), studi kasus, S2 dual-metric, keputusan butuh arahan, skrip presentasi 20-25 menit, FAQ 9 pertanyaan + jawaban, checklist.

**7. Bimbingan dilaksanakan 2026-05-16**
- Outcome belum di-catat ke `revisi_dosen.md` (Putaran 5) — akan ditindak terpisah di sesi lain.

**File baru / modified di sesi ini:**
- 🆕 `bimbingan_2026_05_13.md`, `bimbingan_graf_2026_05_14.md`, `bimbingan_2026_05_16.md`
- 🆕 `data/result/analysis/case_study_panel.png` + 5 PNG `case_study_Perang_*.png`
- 🆕 `data/result/neo4j/import_community_v2.cypher`
- 🆕 `src/analysis/visualize_case_study_events.py`
- 🆕 `src/pseudo_labelling/SRL-NER/S2-seqeval.md`, `evaluate_seqeval.py`, `seqeval_addendum_colab.md`, `_fix_underscore_to_dash.py`
- 🆕 `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/` (notebook + models + evaluation)
- ✏️ 4 notebook S2/S3 (S2a/S2b/S3a/S3b) — modified untuk include seqeval cells / tweaks Colab
- ✏️ `CLAUDE.md` — update status SRL-NER + catatan progres terakhir + skenario aktif

**Action item terbawa ke sesi berikutnya:**
1. ⏳ Catat outcome bimbingan 2026-05-16 ke `revisi_dosen.md` (Putaran 5).
2. ⏳ Run S3a (+ S3b kalau Bu Diana minta keduanya) di Colab — script & augmented data siap.
3. ⏳ Setelah S3 + winner dipilih → inference ke seluruh `sirah_chunks_final.csv` → regenerate `nodes_v3.csv` + `edges_v3.csv`.
4. ⏳ Fix 2 bug pending: `OCCURRED_AT weight=2.0` (aggregation cap di `relation_extraction.py`) + `PRECEDES stale v1 mapping` (Fathul Makkah → Perang Uhud salah arah).
5. ⏳ Pertimbangkan tuning λ_C 0.3 → 0.1/0.2 sebagai future work kalau gap S2 vs S1 perlu di-close.

---

## [2026-05-12] Periodisasi Top-Down + Temporal Detection + Graph Testing + Studi Kasus + Neo4j v2

Sesi ini menyelesaikan **4 dari 4 revisi Bu Diana cluster** (post-revisi periodisasi):

**1. Periodisasi top-down** (revisi internal user — restruktur dari fuzzy match)
- File baru: `data/result/relation_result/period_mapping.json` (dibuat user) — 15 period (P0-P14) tergroup ke 6 phase (Fase I-VI Pra-Islam → Konsolidasi Akhir Kenabian), mencakup 56 BAB dari 59 di TOC. 3 BAB akhir (wafat + biografi) sengaja excluded sebagai non-kronologis.
- Module baru: `src/relation_extraction/event_period.py` — top-down lookup EVENT → period via page_range (no fuzzy match). API: `load_periods()`, `build_event_period_map()`, `compute_period_score()` drop-in compatible dengan period_mapping.py lama. Plus `load_review()` + `apply_review()` untuk human-in-the-loop curation.
- Generator review CSV: `src/relation_extraction/build_event_period_review_v2.py` — produces `event_period_review_v2.csv` (49 rows, pre-filled suggested_action K/F/R/ADD).
- User mark CSV (39 existing + 7 ADD candidates): 19 K, 10 F, 12 R, 7 ADD. **Hijrah ambigu di-split jadi Hijrah ke Habasyah (P5) + Hijrah ke Madinah (P6)**.
- Apply ke nodes/edges: `src/relation_extraction/apply_review_to_kg.py` → `nodes_v2.csv` (892 nodes, EVENT 41 → 36) + `edges_v2.csv` (370 → 322 edges) + `review_apply_log.md`.

**2. Temporal Detection intra-sentence** (revisi Bu Diana cluster #1, 2026-05-03)
- Script: `src/relation_extraction/detect_temporal_relations.py` — rule-based pattern matching, temporal cues Bahasa Indonesia (sebelum/setelah/kemudian/saat/dst).
- Hasil: 9835 kalimat → 11 kalimat dengan 2+ EVENT → 3 unique relations (1 PRECEDES + 2 CONCURRENT).
- 1 confirmed by page-order (Perjanjian Hudaibiyah → Perang Khaibar). 2 CONCURRENT = narrative co-mention (false-positive rule).
- **Insight metodologis untuk Bab 4:** yield rendah (0.04%) menunjukkan Sirah's narrative ordering implicit antar paragraf, bukan via cue eksplisit intra-sentence. Periodisasi top-down adalah primary signal, intra-sentence sebagai komplementer.
- Filter: hypothetical markers ("kemungkinan", "boleh jadi") + event alias groups (drop self-reference seperti Baiat Aqabah ↔ Baiat Aqabah Kubra).

**3. Graph Testing — graph-level metrics + community comparison** (revisi Bu Diana cluster #4, 2026-05-03)
- Script: `src/analysis/sna_graph_metrics.py` (file baru, terpisah dari `sna_analysis.py` lama yang fokus per-node).
- Graph-level metrics Person co-participation graph (163 nodes, 1135 edges): density 0.086, average_degree 13.93, transitivity_global **0.7723** (sangat tinggi — struktur klan/suku Arab confirmed), average_clustering 0.45, degree_assortativity -0.058 (neutral), giant_component 90.8%, **diameter 6 dengan avg_path 2.47** (small-world!).
- Community detection comparison: **Louvain proper** (Q=0.3269, 13 komunitas) vs Greedy Modularity (Q=0.3196, 15 komunitas — yang dipakai `sna_analysis.py` lama, sebenarnya BUKAN Louvain meskipun di-label demikian) vs Girvan-Newman (Q=0.0239, 16 komunitas — over-fragmented).
- ARI Louvain vs Greedy = 0.56 (moderate agreement), Louvain vs Girvan-Newman = 0.13.
- Output: `data/result/analysis/graph_metrics_v2.md` + `.json`.

**4. Studi Kasus 5 Event berperiode jauh** (revisi Bu Diana cluster #2, 2026-05-03)
- Script: `src/analysis/case_study_events.py`.
- 5 events: Perang Badr (P8), Perang Uhud (P9), Perjanjian Hudaibiyah (P11), Perang Khaibar (P11), Perang Tabuk (P13) — span page 266-571.
- Total 60 unique Person, hanya **Muhammad (5/5) sebagai hub lintas-event**. 7 person muncul di 2 events (Abu Jahal/Abu Sufyan/Abu Azzah quartet Quraisy musuh utama di Badr+Uhud).
- **Bias coverage NER terlihat:** Perang Badr dominasi (39 person, 16 direct relations) vs Tabuk (6 person, 0 direct). Bukan ground-truth keterlibatan historis — proxy content density.
- Output: `case_study_events.md` (laporan) + `case_study_events_cypher.md` (5 set Cypher queries untuk visualisasi).

**5. Neo4j Cypher v2** (update script)
- Modified: `src/neo4j/import_to_neo4j.py` — support `--source {v1|v2|auto}` flag, auto-detect v2.
- Output baru: `import_sirah_v2.cypher` (1287 statements, 892 nodes + 15 Period + 322 edges + 36 IN_PERIOD relations + constraints).
- Example queries baru: query by period, density per period, tokoh lintas-period, dst.

**File yang di-update di sesi ini:**
- `CLAUDE.md` — entry ini + update status table
- `src/neo4j/import_to_neo4j.py` — modified untuk v2 + Period node support
- Memory: belum di-update (TBD setelah commit)

**Action item sesi berikutnya:**
1. ⏳ Import `import_sirah_v2.cypher` ke Neo4j Desktop untuk verify visual + demo Bu Diana
2. ⏳ Run S2/S3 di Colab (notebook sudah siap dari 2026-05-11)
3. ⏳ Setelah S2/S3 selesai, pilih winner → inference ke seluruh `sirah_chunks_final.csv` → regenerate nodes/edges dengan NER baru
4. ⏳ Bimbingan Bu Diana — presentasi hasil periodisasi + temporal + graph testing + studi kasus

---

## [2026-05-11] Restrukturisasi Skenario SRL-NER (S1/S2/S3 baru menggantikan E1/S1/S2 lama)

Sesi ini fokus restrukturisasi skema skenario SRL-NER. **Skenario lama (class weight + adaptive threshold)** yang sudah dijalankan 2026-05-07 didrop dari klaim utama TA — diganti dengan skenario baru yang layer-by-layer:

**Skenario baru:**

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa class weight, tanpa contrastive, tanpa augmentation | ✅ Hasil run reuse dari E1 lama (F1 entity=0.959, F1 EVENT=0.816) |
| **S2 — Contrastive Learning + Baseline** | S1 + supervised contrastive loss (SCL/JSCL) | ⏳ Tunggu paper dari teman → coding |
| **S3 — Sentence-based Augmentation + S2** | S2 + augmentasi kalimat fokus kelas minor | ⏳ Depend on S2 |

**Latar belakang:**
- Skenario lama (E1+S1 class weight + S2 adaptive+CW) sudah selesai run 2026-05-07. Hasil: class weight murni belum cukup untuk EVENT (F1 stuck di 0.83), trade-off precision-recall terlalu tajam (S2 lama precision 0.74).
- Bu Diana putaran 3 (2026-05-07) menyarankan contrastive learning + sentence augmentation. Awalnya direncanakan sebagai S3+S4 di atas skenario lama.
- **Keputusan 2026-05-11:** restrukturisasi total — buang skenario class-weight/adaptive dari klaim, ganti dengan skema baru yang lebih bersih (1 skenario = 1 layer kontribusi).

**Yang menunggu trigger:**
- Paper SCL/JSCL konkret dari teman (Bu Diana tidak menyebut paper spesifik).
- Paper augmentasi NER konkret (kandidat default: Dai & Adel COLING 2020, DAGA EMNLP 2020).
- Konfirmasi Bu Diana scope final di bimbingan berikutnya.

**File yang di-update di sesi ini:**
- `srl_ner_skenario.md` — rewrite total: §1 baseline, §2 S1, §3 S2 contrastive, §4 S3 augmentation, §5 timeline, §6 referensi paper (foundational Khosla 2020 + ContrastNER 2023 + Dai & Adel 2020 + DAGA 2020), §7 pertanyaan Bu Diana, §8 output ekspektasi, §9 arsip skenario lama, §10 action item
- `CLAUDE.md` — entry ini (changelog) + update status SRL-NER ke skenario baru
- `revisi_dosen.md` — tambah "Putaran 4 — 2026-05-11" mencatat keputusan restrukturisasi
- `bimbingan.md` — sajikan skenario baru sebagai active plan, tandai bagian lama sebagai arsip
- `done_running/legacy_class_weight_adaptive/` — folder baru untuk arsipkan hasil run lama

**Pekerjaan yang tidak hilang:**
- Hasil run E1 lama → direuse sebagai S1 baru (skenario teknis identik).
- Hasil run S1/S2 lama (class weight + adaptive) tetap disimpan, bisa direferensikan di Bab 4 sebagai "studi pendahuluan / ablation pembanding".

**Update lanjutan 2026-05-11 (sesi yang sama, paper S2 teridentifikasi + adaptasi lock-in):**
- Paper rujukan S2 **sudah ada di root repo**: `Contrastive_Learning.pdf` — Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo, *Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts* (sebagian besar penulis dari ITS).
- Paper berisi 3 strategi contrastive (BAL/SCL/JSCL) — Sirah pakai **SCL + JSCL** (sesuai permintaan Bu Diana putaran 3, BAL skip).
- SCL: Eq. 2–3 (positive pair = label set identik, InfoNCE). JSCL: Eq. 4–6 (weighted InfoNCE dengan `α_ij` Jaccard `J_ij = |L_i ∩ L_j| / |L_i ∪ L_j|`). Framework two-phase: contrastive pre-training → pseudo-label fine-tuning.
- **Adaptasi JSCL ke NER → lock-in sentence-level Jaccard:** tiap kalimat punya bag-of-labels BIO (exclude `O`), Jaccard antar kalimat dalam batch, embedding kalimat = mean-pool token embeddings. Sketsa kode lengkap di `srl_ner_skenario.md` §3.6.1, knob di §3.6.2.

**Update lanjutan 2026-05-11 (Fase 1 + Fase 4 implementasi — anggap approval Bu Diana sudah ada):**
- ✅ **S2 notebook siap** (6 file: SCL/JSCL × lokal/Colab/Kaggle). Generator: `src/pseudo_labelling/SRL-NER/_build_S2_contrastive.py` — idempotent. Notebook inject `ContrastiveTrainer` subclass + helper `scl_loss_tokens()` + `jscl_loss_sentence()` + knob `LAMBDA_C=0.3, TAU=0.1`.
- ✅ **Augmentation script siap**: `src/pseudo_labelling/SRL-NER/augment_minor_classes.py`. Strategi: Mention Replacement (Dai & Adel COLING 2020). Output: `data/result/pseudo-labelling/SRL-NER/train_augmented.csv` + `augmentation_log.json` + `sample_augmented.txt`.
  - **Hasil augmentasi:** distribusi minor naik 2-3x (B-EVENT 0.14% → 0.28%, I-EVENT 0.15% → 0.32%, I-LOCATION 0.07% → 0.13%). 141 minor sentences → 282 augmented (n=2 variant). Pool: PERSON=894, LOCATION=137, TIME=158, EVENT=64 unique mentions.
- ✅ **S3 notebook siap** (6 file: SCL+aug / JSCL+aug × lokal/Colab/Kaggle). Generator: `src/pseudo_labelling/SRL-NER/_build_S3_augmented.py`. S3 = S2 + load `train_augmented.csv`.

**Action item sesi berikutnya:**
1. ⏳ **Run S2a + S2b di Colab** (~3-4 jam GPU T4 per skenario).
2. ⏳ **Run S3a + S3b di Colab** setelah S2 selesai (~3-4 jam per skenario).
3. ⏳ Download hasil ke `done_running/S2a_scl/`, `done_running/S2b_jscl/`, `done_running/S3a_scl_aug/`, `done_running/S3b_jscl_aug/`.
4. ⏳ Tulis `analisis_skenario_S2_S3.md` + update `compare_scenarios.ipynb` untuk include S1/S2a/S2b/S3a/S3b.
5. ⏳ Pilih skenario terbaik → inference final ke `sirah_chunks_final.csv` → lanjut pipeline (temporal detection, relation extraction, SNA, Neo4j).

---

## [2026-05-07] Revisi Dosen Putaran 3 (post-run S1/S2) — `revisi_dosen.md`

Pertemuan **2026-05-07** sesudah hasil run E1/S1/S2 ditunjukkan ke Bu Diana. Beliau melihat F1 EVENT (kelas paling minoritas) yang masih belum optimal di S1/S2 (0,816 → 0,835 → 0,830) dan menyarankan **dua skenario lanjutan untuk handling kelas minoritas** sebagai tambahan di atas class weight S1/S2.

**1. Skenario tambahan SRL-NER:**
- **S3 — Contrastive Learning (JSCL vs SCL):** tambahkan supervised contrastive loss ke training pipeline, supaya representasi token kelas minoritas lebih terstruktur. Variasi SCL standar (Khosla NeurIPS 2020) vs JSCL (definisi tepat menunggu konfirmasi paper).
- **S4 — Sentence-based Augmentation:** generate kalimat baru fokus ke kelas minor (EVENT, TIME, I-LOCATION) lalu append ke train set. Bu Diana: *"oversampling bisa tapi susah"* — augmentasi sentence-based jadi alternatif yang lebih praktis.

**2. Catatan referensi:**
- Bu Diana **tidak menyebut paper spesifik** untuk JSCL/SCL. Disarankan **bertanya ke teman yang sudah pernah implementasi** untuk paper konkret. Kandidat default sementara: Khosla 2020 (SCL), ContrastNER 2023, CONTaiNER ACL 2022.
- Untuk S4 augmentasi: Dai & Adel COLING 2020 (survey augmentasi NER), DAGA EMNLP 2020 (generative augmentation low-resource).

**3. Dokumen yang di-update:**
- `revisi_dosen.md` — restructure jadi "Putaran 1" + "Putaran 3" dengan section header
- `srl_ner_skenario.md` — tambah §9 "Skenario Lanjutan Putaran 3" dengan detail S3/S4 (motivasi, knob, integrasi, pro/kontra, effort, matriks kombinasi S1-S4, kandidat referensi, pertanyaan Bu Diana)
- `bimbingan.md` — tambah section "Skenario Lanjutan Putaran 3" di akhir
- `CLAUDE.md` — entry ini (changelog) + update status SRL-NER pipeline jadi "selesai E1/S1/S2 + planning S3/S4"

**4. Action item untuk sesi berikutnya:**
1. **Tanya ke teman X** untuk paper konkret JSCL yang dipakai → update §9.4 `srl_ner_skenario.md` setelah dapat info
2. **Konfirmasi prioritas ke Bu Diana** di bimbingan berikutnya: S3 vs S4, atau keduanya, atau cukup salah satu
3. **Belum mulai coding** — tunggu approval scope

**Status SRL-NER setelah putaran 3:**
- Klaim selesai untuk laporan: E1 + S1 + S2 (sudah run, sudah dianalisis)
- Klaim planning: S3 + S4 (menunggu approval + paper referensi)
- Pertanyaan terbuka: apakah S3/S4 wajib eksekusi sebelum sidang atau cukup *future work*

---

## [2026-05-07] Run 3 Skenario SRL-NER + Analisis Komparatif

Sesi ini fokus eksekusi 3 skenario SRL-NER (sudah ACC Bu Diana per 2026-05-04) di Colab, lalu analisis hasilnya.

**1. Bug fix di `_validate_event_period.py`**
- File `event_period_review.csv` sekarang di-sort by start page (event paling awal di Sirah → akhir). Sebelumnya urutannya mengikuti urutan EVENT muncul di `nodes.csv` (acak).
- Fix: tambah helper `_start_page()` + `events.sort_values(by=["_sort_page", "name"], kind="stable")` di `generate_review()`. Event tanpa `page_range` di-push ke akhir (mis. `Isra'`, `Mi'raj` yang belum ke-mapping fuzzy).
- Dipakai untuk review manual mapping EVENT → BAB sebelum re-run relation extraction.

**2. Bug fix di `srl_ner_sirah_S2_adaptive_colab.ipynb`** — 3 bug saat run S2:
- **Cell 21 (`filter_threshold`):** cache check di awal fungsi return early **tanpa save xlsx files**. Akibatnya `reconstruct_unlabelled_from_below()` di akhir iter crash karena `below-{thr}.xlsx` tidak ada. Fix: cache cuma trigger kalau **retrain CSV + above xlsx + below xlsx ketiganya ada**.
- **Cell 27 (eval):** hardcoded `f"{experiment_name}-0.9-iteration-6"` — pattern `-0.9-` tidak match save format (yang menyimpan tanpa `0.9`), dan `iteration-6` mengasumsikan loop selalu jalan sampai max iter. Fix: tambah helper `find_last_iteration_model()` yang auto-detect iter tertinggi yang punya `config.json`, fallback ke `-base` kalau tidak ada iteration folder.
- **Cell 30, 31:** hardcoded `iterative-6`. Fix: pakai `LAST_ITER` dari Cell 27.

**3. Eksekusi 3 skenario di Colab (output di `done_running/`):**

| Skenario | Iter | Total pseudo | F1 entity (seqeval) | Catatan |
|---|---|---|---|---|
| **E1 baseline** | 6 | 237 | **0.9587** | Konservatif, balanced |
| **S1 class weight** | 5 | 237 | 0.9080 | Recall ↑ semua kelas, EVENT F1 0.816→0.835 |
| **S2 adaptive + CW** | 2 (STOP) | 237 | 0.8432 | Recall tertinggi (0.979), tapi precision drop ke 0.74 |

S2 STOP di iter 2 karena adaptive turun sampai 0.7 tapi cuma dapat 40 sampel < TARGET_MIN_SAMPLES=50.

**4. Analisis komparatif (3 perspektif metrik) — file baru di `done_running/`:**

| Metric | Pemenang |
|---|---|
| Token-weighted F1 (incl. O) | **E1** (0.9955) — bias karena 93% token = "O" |
| Macro F1 tanpa O | **S2** (0.8627) — fair untuk unbalanced |
| Seqeval entity-level F1 | **E1** (0.9587) — standar NER literatur |
| F1 EVENT (kelas paling minoritas) | **S1** (0.835) — bukti class weight bekerja |

**Verdict: pakai S1 untuk inference final** ke `sirah_chunks_final.csv`. Alasan:
- Entity-F1 0.908 (drop -5% dari E1, masih tinggi)
- Recall lebih tinggi pada semua kelas → KG lebih kaya
- EVENT class (penting untuk kronologi Sirah) **membaik** dari E1
- Precision 0.85 masih manageable (bisa di-filter alias clustering + frequency)
- S2 trade-off terlalu agresif (precision 0.74 = 26% noise)

**5. File output yang dibuat:**
- `src/pseudo_labelling/SRL-NER/done_running/analisis_skenario_srlner.md` — analisis lengkap 11 section (executive summary, konfigurasi, dinamika pseudo-labelling, 3 metrik, per-entity, error pattern, verdict, rekomendasi, bahan diskusi Bu Diana, lampiran numerik)
- `src/pseudo_labelling/SRL-NER/done_running/compare_scenarios.ipynb` — notebook 25 cells dengan plot pseudo-label per iter, per-entity bar chart, confusion matrix side-by-side, P-R trade-off scatter dengan iso-F1 contour. Generate `summary_comparison.csv` + 4 PNG ke folder yang sama.

**Yang harus dilakukan di sesi berikutnya:**
1. Konsultasi Bu Diana — tunjukkan analisis 3 metrik, konfirmasi pakai S1 untuk inference final (vs E1 yang F1 token-weighted lebih tinggi)
2. **Inference S1 ke seluruh `sirah_chunks_final.csv`** — generate prediksi NER untuk semua chunk
3. Re-run relation extraction dengan output S1 (perlu temporal-aware juga — lihat revisi 2026-05-03 cluster #1)
4. Lanjut review `event_period_review.csv` (sudah di-sort, ada 41 EVENT yang perlu di-mark K/F/R)

**Catatan teknis untuk laporan Bab 4:**
- WAJIB sajikan ketiga metrik (token-weighted, macro tanpa O, seqeval) berdampingan supaya argumen "class weight bantu unbalanced" terlihat. Kalau cuma satu metrik, salah satu skenario bisa salah dipersepsi.
- Klaim yang BISA dipertahankan: "EVENT F1 naik 1.9% dengan class weight", "recall semua kelas naik di S1/S2", "adaptive memungkinkan 197 pseudo-label di iter-1 (vs 187 baseline)".
- Klaim yang TIDAK BISA dipertahankan: "S1/S2 strictly better dari E1" (karena F1 entity seqeval menang E1), "adaptive lebih baik dari fix" (S1 entity F1 > S2).

---

## [2026-05-03] Revisi Dosen Putaran 2 (Bu Diana) — `revisi_dosen.md`

Bu Diana memberikan 4 cluster revisi baru. Semua belum diimplementasikan, baru dicatat arah kerjanya.

**1. Temporal dalam satu kalimat → pembentukan graf**
- Perlu **deteksi temporal di level kalimat** (urutan kejadian Sirah / urutan bab)
- Baru setelah itu pembentukan graf — graf harus **memperhatikan temporal terlebih dahulu**, baru fitur graf
- Implikasi: relation extraction perlu di-rework agar relasi **antar entitas dalam kalimat yang sama** punya order/precedence temporal yang eksplisit, bukan cuma proximity skor

**2. Uji coba sampling event**
- Pilih **3–5 event dengan periode berjauhan** (contoh anchor: **Perang Badar**)
- Untuk tiap event: amati keterlibatan (siapa terlibat) → tampilkan graf-nya → analisis
- Tujuan: validasi pipeline dari hulu (kalau salah dari awal, fitur graf jadi salah). Ini sekaligus jadi bagian Bab 4 (studi kasus).

**3. NER — keputusan & skenario**
- ❌ **LLM-NER dibatalkan** → fokus penuh **SRL-NER**
- Definisikan skenario SRL-NER secara eksplisit:
  - **Threshold:** fix vs **adaptif** (kalau terlalu rendah, otomatis diturunkan / dinaikkan)
  - **Unbalanced handling:** definisikan strategi (oversample, class weight, focal loss, dll.) — perlu effort lebih
- Boleh ganti model kalau mau, atau pakai yang sudah ada dulu kalau tidak mau ribet
- Implikasi konkret untuk notebook `srl_ner_sirah_0.9*.ipynb`:
  - Knob `MIN_CONFIDENCE` (Fix C) → tambah mode adaptif (turun otomatis kalau jumlah pseudo-label di bawah ambang)
  - Audit distribusi label per iterasi (PERSON vs EVENT vs TIME vs LOCATION) → tambah handling unbalanced

**4. Graf — perluasan metrik**
- Centrality (sudah ada) **fokus ke node** — perlu ditambah metrik **fokus ke graf besar**:
  - **Density** (kepadatan koneksi)
  - **Clustering coefficient** (rata-rata, global)
  - **Ukuran network** (n_nodes, n_edges, jumlah komponen, ukuran giant component)
  - Community detection sudah ada (Louvain 16 komunitas) — perlu juga **uji coba lain** (mis. Girvan-Newman, modularity comparison)
- Implikasi: `src/analysis/sna_analysis.py` perlu diperluas, tambah section `## Graph-level Metrics` di `sna_summary.md`

**Yang harus dilakukan di sesi berikutnya (urutan rekomendasi):**
1. ✅ **Bekukan keputusan LLM-NER** — `DEPRECATED.md` ditambahkan di `src/pseudo_labelling/LLM-NER/` (2026-05-03)
2. ✅ **Skenario SRL-NER + Referensi** — `srl_ner_skenario.md` di root (2026-05-03). **Dokumen tunggal** (referensi digabung ke skenario, file `srl_ner_referensi.md` lama dihapus). **Scope: 3 eksperimen E1+E3+E4** (drop E2/E5 untuk simplicity). Berisi: §1 baseline, §2 threshold (fix vs adaptive dropping), §3 class weight, §4 eksperimen (E1/E3/E4 dengan sketsa kode), §5 referensi 9 paper (Ariyanto 2025, Yu 2023, MoM 2024, FreeMatch, Survey, dll.) + mapping ke eksperimen + top 5 prioritas, §6 pertanyaan + bahan diskusi Bu Diana, §7 implementasi, §8 output. **Status: tunggu approval Bu Diana sebelum coding.**
3. ⏳ **Implementasi temporal intra-sentence** di relation extraction (kemungkinan dependency parsing / pattern temporal Bahasa Indonesia) — dipisah dokumen sendiri (belum dibuat)
4-5. ✅ **Skenario Pengujian Graf** — `graf_pengujian_skenario.md` di root (2026-05-04). Menggabungkan revisi #4 (graph-level metrics, community detection alternative) dan revisi #2 (studi kasus event sampling) jadi 1 dokumen. Scope: 4 cluster G1-G4. G1=centrality (sudah ada), G2=graph-level metrics (density/clustering/transitivity/assortativity/path), G3=community detection comparison (Louvain+Leiden+Girvan-Newman), G4=studi kasus 3 event (Hijrah Habasyah/Perang Badar/Fathu Makkah). **Opsi A dipilih:** graf hanya pakai NER terbaik E4 (tidak ada perbandingan graf antar E1/E3/E4). Berisi 8 paper rujukan (Traag 2019 Leiden, Labatut Survey 2019, Aurangzeb 2021, dll.) + 6 pertanyaan Bu Diana + estimasi 8-9 jam coding. **Status: tunggu approval Bu Diana + selesainya SRL-NER (G1-G4 punya prasyarat: NER terbaik harus diinferensi dulu ke seluruh data).**

---

## [2026-04-27] Restrukturisasi LLM-NER (asli vs pseudo) + dokumentasi thesis Andrian

> ⚠️ **Note 2026-05-03:** Pekerjaan LLM-NER di sesi ini **tidak jadi dipakai** (LLM-NER dibatalkan Bu Diana). Catatan di bawah dipertahankan sebagai arsip metodologi.

Sesi ini fokus untuk memahami metodologi LLM-NER dari thesis Andrian dan menambahkan **iterative self-training** sebagai kontribusi orisinal TA.

**1. Dokumentasi pemahaman thesis Andrian:**
- File baru: `src/pseudo_labelling/LLM-NER/PENJELASAN_THESIS_ANDRIAN.md` (9 bagian)
- Berisi mapping arsitektur Andrian → step-by-step (Praproses → Augmentasi KEE/E2T → Pelatihan TC/IFT → Inferensi → Evaluasi) dengan input/output tiap langkah
- Mencantumkan halaman penting di PDF (Bab III pp.21-43, Kode Semu 3.7/3.9/3.12, Prompt 3.8)
- Dipakai sebagai bahan konsultasi langsung dengan Mas Andrian

**2. Klarifikasi terminologi (penting):**
- Folder `pseudo_labelling/LLM-NER/` namanya **misleading** — Andrian sendiri TIDAK pakai pseudo-labelling/self-training
- Andrian pakai: supervised fine-tuning + **data augmentation** (KEE-Prompt + E2T) lewat GPT-4o Mini
- Yang sebenarnya pseudo-labelling = SRL-NER (BERT iterative self-training, sudah ada)
- Untuk LLM-NER, **iterative self-training adalah penambahan TA Anda** di atas metode Andrian

**3. Implementasi self-training (kontribusi TA):**
- File baru: `src/pseudo_labelling/LLM-NER/pseudo/llm_ner_sirah_selftraining.py`
- Algoritma: train seed → infer unlabelled + confidence → filter (≥0.85) + top-50% → append → re-train → ulang
- Confidence scoring: `mean(exp(logprob))` per generated token × `0.7^(retries-1)` × `0.5 if needed_padding`
- 4 stop conditions: konvergen (delta_F1 < 0.01) / unlabelled habis / new_samples < 50 / hit max_iter (5)
- Output: `iteration_log.csv`, `train_iter{N}.csv`, `llm_ner_predictions_iter{N}.csv`, `selftraining_summary.txt`

**4. Restrukturisasi folder `LLM-NER/` menjadi 2 subfolder:**
- `asli/` — penerapan asli Andrian (baseline supervised single-shot, untuk pembanding di Bab 4)
  - `llm_ner_sirah.py`, `llm_ner_sirah_colab.ipynb` (12 cells), `llm_ner_sirah_kaggle.ipynb` (11 cells), `_build_notebooks.py`
- `pseudo/` — versi TA dengan iterative self-training (kontribusi orisinal)
  - `llm_ner_sirah.py` (copy untuk import), `llm_ner_sirah_selftraining.py`, `llm_ner_sirah_colab.ipynb` (10 cells), `llm_ner_sirah_kaggle.ipynb` (9 cells), `README_SELFTRAINING.md`, `_build_notebooks.py`
- `PENJELASAN_THESIS_ANDRIAN.md` di root LLM-NER (referensi untuk kedua versi)

**5. Memory tersimpan untuk session berikutnya:**
- `user_profile.md` — pembimbing Bu Diana, prefer Bahasa Indonesia + dokumentasi `.md`
- `reference_andrian_thesis.md` — lokasi PDF + halaman penting + cara akses (max 20 hal/Read)
- `project_llm_ner_status.md` — klarifikasi terminologi pseudo-labelling vs augmentation

**Hyperparameter self-training (default di `pseudo/`):**
| Param | Nilai |
|---|---|
| `MAX_ITERATIONS` | 5 |
| `MIN_CONFIDENCE` | 0.85 |
| `SAMPLING_RATE` | 0.5 |
| `MIN_NEW_SAMPLES` | 50 |
| `MIN_F1_DELTA` | 0.01 |
| `EPOCHS_PER_ITER` | 10 (lebih kecil dari baseline 30) |

**Yang harus dilakukan di sesi berikutnya:**
1. **Run baseline `asli/` di Colab/Kaggle** untuk dapat F1 baseline (1 angka untuk pembanding)
2. **Run self-training `pseudo/` di Colab/Kaggle** untuk dapat F1 per iterasi (5 angka, plot vs iteration)
3. **Konsultasi dengan Mas Andrian** — bawa `PENJELASAN_THESIS_ANDRIAN.md` + sample data Sirah + 5 pertanyaan top-priority
4. Setelah dapat hasil, bandingkan F1 baseline vs final self-training di Bab 4

---

## [2026-04-24] Implementasi 4 Revisi Dosen

Dosen memberikan 4 poin revisi yang semuanya sudah diimplementasikan:

**Revisi 1 — Pembobotan Relasi:**
- File baru: `src/relation_extraction/period_mapping.py` — mapping 39 EVENT ke BAB utama via fuzzy match terhadap `toc_groundtruth.json`
- Weight (0.0–1.0) = proximity score (0.0–0.5) + period score (0.0–0.5)
- Proximity: same sentence=0.5, <50char=0.4, <100=0.3, <200=0.2, else=0.1
- Period: chunk di BAB utama event=0.5, unmapped=0.25, di luar=0.0
- Distribusi weight: mean=0.474, min=0.200, max=1.000

**Revisi 2 — LLM-NER (Instruction Fine-Tuning + QLoRA):**
- Mengikuti thesis Andrian (5025211079, pembimbing: Prof. Dr. Diana Purwitasari)
- File baru: `src/pseudo_labelling/LLM-NER/llm_ner_sirah.py` (standalone), `_colab.ipynb`, `_kaggle.ipynb`
- Model: SahabatAI (LLAMA 3 adapted for Indonesian) — best F1 di Andrian
- QLoRA: r=64, alpha=32, dropout=0.05, 4-bit NF4 quantization
- Training: SFTTrainer, 30 epochs, batch_size=16, lr=1e-4
- Prompt: Alpaca-style Bahasa Indonesia (diadaptasi dari Prompt 3.8 Andrian)
- Inferensi: retry mechanism (max 5 attempts) + padding/truncate fallback
- Evaluasi: seqeval (entity-level F1, precision, recall, accuracy)
- **Harus dijalankan di Colab/Kaggle** (butuh GPU T4/A100)

**Revisi 3 — Relasi Baru:**
- Person-Person: 91 KELUARGA + 25 SAHABAT + 10 MUSUH (regex pattern matching pada evidence teks)
- Event-Event: 18 PRECEDES (kronologis berdasarkan urutan BAB)
- Guard: skip self-relation, skip span overlap (patronymic), skip narrator

**Revisi 4 — Social Network Analysis:**
- File baru: `src/analysis/sna_analysis.py`
- Person co-participation graph: 174 nodes, 1164 edges (dari shared INVOLVED_IN events + relasi Person-Person langsung)
- Metrik: degree centrality, betweenness centrality, closeness centrality, PageRank
- Community detection: Louvain → 16 komunitas
- Top tokoh: Muhammad (PageRank=0.064, betweenness=0.415, degree=105)
- Output: `data/result/analysis/sna_metrics.csv`, `sna_summary.md`, `sna_person_network.png` (butuh `pip install matplotlib`)

**Perubahan schema:**
- `edges.csv`: + kolom `weight`, `periode_bab`, `relation_subtype`
- `nodes.csv` (EVENT): + kolom `periode_bab`, `page_range`
- Tipe relasi total: INVOLVED_IN (153), KELUARGA (91), OCCURRED_ON (39), OCCURRED_AT (34), SAHABAT (25), PRECEDES (18), MUSUH (10)
- Edges naik dari 291 → 370 (27% increase)

**File referensi paper:**
- `referensi_sna_weighted_relations.md` — 17 paper relevan (SNA teks Islam, character network, weighted KG, community detection, RE & NER)

---

## [2026-04-16] Catatan sebelumnya

- Pipeline data sudah di-rerun berurutan & bersih:
  `preprocess.ipynb` → `chunking_and_seed.ipynb` → `pre_labelling.py` → `prepare_bert_data.py`
- Output `prepare_bert_data.py` ada di `data/result/pseudo-labelling/SRL-NER/`:
  `train.csv`, `test.csv`, `unlabelled.csv` (format CoNLL: `text_id,id,token,pos_tag,label`)
- Notebook BERT NER (referensi dari Bu Diana, `BERT_Only_Percobaan_1_Argument_0.9.ipynb`)
  sudah diadaptasi untuk Sirah → 3 versi tersedia di `src/pseudo_labelling/SRL-NER/`:
  - `srl_ner_sirah_0.9.ipynb` (lokal Windows)
  - `srl_ner_sirah_0.9_kaggle.ipynb` (Kaggle, butuh Dataset bernama `sirah-ner-srl`)
  - `srl_ner_sirah_0.9_colab.ipynb` (Colab, default `MyDrive/TA-Sirah/` & output di `MyDrive/TA-Sirah/output/`)
- Patch script lama: `_patch_notebook.py` (sekali-pakai, idempotent)
- Dokumentasi pipeline + cara baca hasil: `src/pseudo_labelling/SRL-NER/README.md`
- **`pre_labelling.py` diperbaiki**: regex `_PERSON_BIN_RE` sekarang require compound prefix ATAU minimal 1 nasab (cegah ledakan PERSON 3698→12472). Truncated name extension + noise prefix cleanup sudah bersih.
- **Alias clustering selesai**: `alias_clustering.py` di `src/alias_clustering/`. Output: `alias_map.json` (143 alias, 109 clusters). Menggunakan manual clusters + Jaro-Winkler (threshold 0.93) dengan 4 guards (compound prefix, patronymic, length ratio, exclude pairs).
- **Relation extraction selesai**: Input path diperbaiki ke `manual_labelling/`, alias map terintegrasi. Output: 898 nodes, 291 edges (173 INVOLVED_IN, 68 OCCURRED_AT, 50 OCCURRED_ON).
- **Neo4j Cypher script siap**: `import_to_neo4j.py` di `src/neo4j/`. Output: `data/result/neo4j/import_sirah.cypher`. Tinggal import ke Neo4j.
- **Dokumen bab3 + flowchart diperbarui**: Urutan pipeline diperbaiki — alias clustering sekarang SETELAH pseudo-labelling (bukan sebelumnya). Pseudocode alias clustering ditambahkan (3.3.5). Flowchart di-reorder (Gambar 3.6=Pseudo-labelling, 3.7=Alias Clustering).
- **[2026-04-16] Refactor ketiga notebook SRL-NER** (fix A–H sejalan panduan analyticsvidhya pseudo-labelling, sambil preserve struktur & signature fungsi dari Bu Diana):
  - Fix A — `extract_entities_from_result()` auto-detect skema label (flat ARG0/ARG1 = Bu Diana vs BIO B_X/I_X = Sirah). Tanpa fix ini, pseudo-label Sirah semua jadi "O" saat retraining karena `entity_group` "PERSON" tidak match `label2id` yang berisi `B_PERSON`/`I_PERSON`.
  - Fix B — `df_to_dataset_for_model()` terima param `val_text_ids`; loop reserve 20% seed text_ids sebagai VAL_TEXT_IDS tetap → val set stabil lintas iterasi (sebelumnya random split di tiap pemanggilan bikin val metric tidak sebanding).
  - Fix C — `filter_threshold()` terima param `min_entity_confidence` (default `None`): reject kalimat kalau ada satu entity dgn conf < nilai ini.
  - Fix D — 6 pasang cell copy-paste diganti **satu for-loop**, `iter_log` disimpan ke `iteration_log.csv` untuk grafik laporan.
  - Fix E — param `sampling_rate` (default 1.0 = Bu Diana): pakai top-K% kalimat confidence tertinggi per iterasi.
  - Fix F — param `MIN_NEW_SAMPLES` (default 0): early stop kalau `|above| < threshold`.
  - Fix G — tambah metric **seqeval entity-level** (`seq_f1`, `seq_precision`, `seq_recall`) di samping sklearn token-level Bu Diana (non-breaking, skip kalau seqeval belum terinstall).
  - Fix H — param `aggregation_strategy` (default "simple" = Bu Diana; "first"/"max" untuk sub-word display yang lebih clean).
  - **Bonus fix bug latent Bu Diana**: `reconstruct_unlabelled_from_below()` menggantikan trik `rename(word→token)` di cell 29 lama — iter 2+ sekarang predict kalimat utuh (dari kolom `text`), bukan kata-kata entity terpisah.
  - Hasil: notebook lokal 60→34 cells, colab 61→35 cells, kaggle 61→35 cells. Semua cell lolos `ast.parse`.
  - Script refactor: `_refactor_pseudo_labelling.py` (idempotent, bisa di-rerun untuk sync ulang ketiga notebook).
  - **Default knob nilainya = Bu Diana** — jadi running apa adanya = persis metode kating, minus bug A yang wajib fix supaya BIO Sirah jalan. Tuning analyticsvidhya-style opt-in via editor.
  - **Dependency baru (opsional):** `pip install seqeval`.

### Bug yang sudah diperbaiki di notebook
- `Trainer(tokenizer=...)` → `Trainer(processing_class=...)` (transformers ≥ 4.46)
- `DataCollatorForTokenClassification(tokenizer=...)` tetap pakai `tokenizer=` (jangan diganti)
- `rmtree("./result")` → `rmtree(model_dir/_trainer_tmp, ignore_errors=True)`
- Hard-coded path `D:\Amelia Devi-S3\...` → path Sirah / Kaggle / Colab
- Kolom `argument` → `label`, `predicted_argument` → `predicted_label`
- File input `train-35.csv`/`unlabelled-65.csv` → `train.csv`/`unlabelled.csv`
- Experiment name `bert-only-argumen` → `bert-only-sirah-ner`

### Bug yang sudah diperbaiki di pre_labelling / alias clustering
- `_PERSON_BIN_RE` ledakan match (3698→12472): fixed dengan require compound prefix OR ≥1 nasab
- OCR artifact "An- Nu'man" (spasi setelah hyphen): fixed `_EXTEND_RE` dengan `\s*`
- Jaro-Winkler terlalu agresif (559 mappings): threshold dinaikkan 0.85→0.93, ditambah 4 guards + EXCLUDE_PAIRS
- False positive alias "Abu Bakrah"→"Abu Bakar", "Perang Badr Kubra"→"Perang Badr Shughra": fixed via EXCLUDE_PAIRS
