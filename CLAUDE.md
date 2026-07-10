# CLAUDE.md — Proyek Tugas Akhir: Knowledge Graph Sirah Nabawiyah

## Deskripsi Proyek
Membangun Knowledge Graph dari teks Sirah Nabawiyah (Bahasa Indonesia) menggunakan pendekatan NER (Named Entity Recognition) berbasis SRL (Semantic Role Labeling) dengan BERT iterative self-training, lalu menyimpan hasilnya di Neo4j dan dianalisis dengan SNA.

**Sumber data:** Buku "Sirah Nabawiyah" oleh Syaikh Shafiyyurrahman Al-Mubarakfuri, terjemahan Kathur Suhardi (633 halaman, Bahasa Indonesia)

> **Catatan revisi 2026-05-03:** LLM-NER **tidak jadi digunakan** (keputusan Bu Diana). Fokus penuh ke **SRL-NER** saja. Folder LLM-NER **dipindah ke `lama/src/pseudo_labelling/LLM-NER/`** (cleanup repo 2026-06-10) sebagai arsip eksplorasi, tidak masuk pipeline final.

---

## Tech Stack
- **Bahasa:** Python (Jupyter Notebook `.ipynb` + `.py`)
- **Database:** Neo4j (Knowledge Graph)
- **OCR:** PaddleOCR (`ocr_paddle.py`)
- **NER:** **SRL-based** saja (Semantic Role Labeling, BERT iterative self-training).
  - LLM-NER (QLoRA, mengikuti thesis Andrian) sudah diimplementasikan tapi **tidak dipakai** per revisi 2026-05-03 — disimpan di `lama/src/pseudo_labelling/LLM-NER/` sebagai arsip (dipindah dari src/ saat cleanup 2026-06-10).
- **SNA:** NetworkX
  - **Node-level (centrality):** degree, betweenness, closeness, PageRank
  - **Graph-level:** density, average clustering coefficient, ukuran network, komponen
  - **Community detection:** Louvain
- **Environment:** Windows (PowerShell), virtual environment di folder `venv`

---

## Entitas yang Diekstrak (NER Labels)
| Label | Keterangan |
|-------|-----------|
| `PERSON` | Tokoh, nama orang, Bani (contoh: Muhammad, Abu Bakar, Bani Quraizah) |
| `EVENT` | Peristiwa bersejarah (contoh: Perang Badar, Hijrah) |
| `TIME` | Waktu, tahun, periode (contoh: tahun ke-10 kenabian) |
| `LOCATION` | Tempat, kota, wilayah (contoh: Makkah, Madinah, Gua Hira) |

---

## Struktur Folder
```
TA_sirah/
├── CLAUDE.md                          ← file ini
├── progress_log.md                    ← riwayat changelog sesi (terpisah supaya CLAUDE.md ringkas)
├── docs/                              ← semua dokumentasi proyek (.md files)
│   ├── bimbingan/                     ← catatan bimbingan + revisi dosen
│   │   ├── revisi_dosen.md            ← raw catatan revisi Bu Diana per putaran
│   │   ├── bimbingan_template.md      ← template diskusi untuk bimbingan SRL-NER
│   │   ├── 2026-05-13.md              ← prep bimbingan S2-fokus
│   │   ├── 2026-05-14_graf.md         ← prep bimbingan graf-fokus lengkap
│   │   ├── 2026-05-16.md              ← prep bimbingan combined (graf + S2)
│   │   ├── 2026-05-16_outcome.md      ← outcome bimbingan 2026-05-16 (catatan mentah)
│   │   └── lama/                      ← arsip laporan bimbingan lama (01–04)
│   ├── skenario/                      ← skenario teknis & metodologi
│   │   ├── srl_ner.md                 ← skenario S1/S2/S3 SRL-NER (metodologi lengkap)
│   │   ├── srl_ner_running_guide.md   ← panduan step-by-step run skenario
│   │   ├── graf_pengujian.md          ← skenario uji coba graf (G1/G2/G3/G4)
│   │   └── temporal.md                ← skenario temporal detection
│   ├── bab3/                          ← draft Bab 3 metodologi
│   │   ├── metodologi.md              ← Bab 3 BERLAKU (SRL-NER real: IndoBERT BIO + self-training)
│   │   └── bab3_revisi_paragraf.md
│   │   (bab3_lengkap_revisi.md → docs/archive/bab3_lengkap_revisi_USANG.md, USANG cleanup 2026-07-10)
│   ├── referensi/                     ← rujukan paper
│   │   └── sna_weighted_relations.md
│   └── archive/                       ← (kosong, disiapkan untuk file lama)
├── data/
│   ├── pages/                         ← 633 halaman PDF yang sudah di-render jadi PNG
│   ├── result/
│   │   ├── ocr_txt/                   ← hasil OCR mentah
│   │   ├── csv_result/                ← hasil konversi ke CSV
│   │   ├── preprocessing_result/      ← hasil preprocessing teks
│   │   ├── chunking_result/           ← hasil chunking
│   │   ├── manual_labelling/          ← hasil manual_labelling
│   │   ├── alias_clustering/          ← hasil alias clustering (alias_map.json, alias_clusters.md)
│   │   ├── pseudo-labelling/          ← hasil pseudo labelling dengan NER
|   |   |   ├── LLM-NER/               ← hasil pseudo labelling dengan LLM-Based NER
|   |   |   ├── SRL-NER/               ← hasil pseudo labelling dengan SRL-Based NER
│   │   ├── relation_result/           ← hasil ekstraksi relasi (nodes.csv, edges.csv) — weighted + relasi baru
│   │   ├── neo4j/                     ← hasil untuk inputan neo4j (import_sirah.cypher)
│   │   ├── analysis/                  ← hasil SNA (sna_metrics.csv, sna_summary.md, sna_person_network.png)
│   │   └── toc_result/                ← hasil ekstraksi daftar isi
│   └── toc_groundtruth.json           ← ground truth daftar isi
│
└── src/
    ├── build_knowledge/
    │   ├── ocr_paddle.py              ← OCR dengan PaddleOCR
    │   ├── toc_fulldocument.py        ← ekstraksi struktur dokumen/TOC
    │   └── convert_csv.py             ← konversi hasil OCR ke CSV
    ├── preprocessing/
    │   ├── preprocess.ipynb           ← notebook preprocessing
    │   └── preprocess.py              ← script preprocessing teks
    ├── chunking/
    │   ├── chunking_and_seed.ipynb    ← notebook chunking + seeding data
    │   ├── chunking_and_seed.ipynb    ← notebook chunking + seeding data
    ├── manual_labelling/
    │   ├── pre_labelling.py           ← semi-auto manual labelling (regex + keyword)
    │   └── generate_entity_review.py  ← generate entity_review.md untuk QA
    ├── alias_clustering/
    │   └── alias_clustering.py        ← clustering variasi nama entitas (manual + Jaro-Winkler)
    ├── pseudo_labelling/
    |   ├── (LLM-NER/ → dipindah ke lama/src/pseudo_labelling/LLM-NER/ — arsip deprecated, cleanup 2026-06-10)
    |   ├── SRL-NER/                          ← (scaffolding _build_*/patch_* dipindah ke lama/, cleanup 2026-06-10)
    ├── relation_extraction/
    │   ├── relation_extraction.py     ← ekstraksi relasi weighted + Person-Person + Event chronology
    │   └── period_mapping.py          ← mapping EVENT → BAB utama (fuzzy match TOC)
    ├── analysis/
    │   └── sna_analysis.py            ← Social Network Analysis (centrality, community detection)
    └── neo4j/
        └── import_to_neo4j.py         ← generate Cypher / import langsung ke Neo4j
```

---

## Status Pengerjaan
| Tahap | Status |
|-------|--------|
| OCR (PaddleOCR) | ✅ Selesai |
| Konversi ke CSV | ✅ Selesai |
| Preprocessing teks | ✅ Selesai (re-run terakhir bersih) |
| Chunking | ✅ Selesai (re-run terakhir bersih) |
| Manual Labelling (semi-auto pre_labelling) | ✅ Selesai (`sirah_prelabelled.csv`, 6000 rows) |
| Alias Clustering | ✅ Selesai (143 alias, 109 clusters → `alias_map.json`) |
| Konversi seed → format BERT (CoNLL) | ✅ Selesai (`prepare_bert_data.py`) |
| NER Pipeline (SRL-based, BERT iterative self-training) | ✅ **S1 ✅ + S2 ✅ + S3.1 ✅ + S3.2 ✅ (selesai 2026-05-26).** Final winner: **S3.2-scl-aug-iter4 = TEST F1 entity 0.9537** (melampaui S1=0.9518 dengan +0.0019). EVENT melonjak 0.7708→0.8454 (+0.0746). Augmentation v2 + λ_C=0.3 winning combo. Detail seqeval di `data/result/pseudo-labelling/SRL-NER/seqeval_results.md`. |
| NER Pipeline (LLM-based, Instruction Fine-Tuning + QLoRA) | ❌ **Tidak jadi dipakai** (revisi 2026-05-03). Arsip + `DEPRECATED.md` di `lama/src/pseudo_labelling/LLM-NER/` (dipindah 2026-06-10). |
| Periodisasi top-down (`period_mapping.json`) | ✅ **Baru 2026-05-12** — 15 period (P0-P14), 6 phase, 56 BAB ter-grouped semantically. Menggantikan fuzzy match BAB lama. Module: `src/relation_extraction/event_period.py`. |
| Manual review event → period (K/F/R/ADD curation) | ✅ Selesai (2026-05-12, `event_period_review_v2.csv`). 19 K + 10 F + 12 R + 7 ADD applied via `apply_review_to_kg.py` → `nodes_v2.csv` + `edges_v2.csv`. |
| Temporal Detection (intra-sentence) | ✅ **Selesai 2026-05-12** (rule-based, terbatas). 9835 kalimat → 3 unique relations (1 confirmed by page-order, 2 narrative co-mention). Yield rendah → struktur naratif Sirah ordering implicit. Script: `detect_temporal_relations.py`. |
| Relation Extraction + Pembobotan | ✅ Selesai (897 → 892 nodes, 370 → 322 edges di v2 setelah review periodisasi). Weighted + relasi baru. |
| Relasi Person-Person (KELUARGA/SAHABAT/MUSUH) | ✅ Selesai (91 KELUARGA, 25 SAHABAT, 10 MUSUH) |
| Relasi Event Kronologis (PRECEDES) | ✅ Selesai (12 PRECEDES di edges_v2.csv, 1 dikonfirmasi intra-sentence) |
| Social Network Analysis — node-level (centrality) | ✅ Selesai (Louvain, betweenness, closeness, PageRank di `sna_analysis.py`) |
| Social Network Analysis — graph-level (revisi #4 Bu Diana) | ✅ **Selesai 2026-05-12** (density 0.086, transitivity 0.77, avg_path 2.47, 8 components, giant 90.8%). Community comparison: Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Script: `sna_graph_metrics.py`. |
| Uji coba sampling 5 event berperiode jauh (revisi #2 Bu Diana) | ✅ **Selesai 2026-05-12** (Perang Badr/Uhud/Hudaibiyah/Khaibar/Tabuk; 60 unique Person; bias coverage NER terlihat — Perang Badr dominasi 39 person). Script: `case_study_events.py`. |
| Build Knowledge Graph (Neo4j) v2 dengan Period node | ✅ **Selesai 2026-05-12** (`import_sirah_v2.cypher`, 15 Period nodes + IN_PERIOD relations, support query per-period) |
| Inference S3.2 winner ke seluruh chunks | ✅ **Selesai 2026-05-28** (Colab T4, 1 menit). Output: `data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v3_{token,entity}.csv` (12,082 entities di 1094 chunks). |
| Knowledge Graph v3 (built from NER inference) | ✅ **Selesai 2026-05-28**. `nodes_v3.csv` (1280 nodes, +44% vs v2) + `edges_v3.csv` (491 edges, +52% vs v2). EVENT 36→44, PERSON +32%, TIME +450%. |
| Comparison report SRL-NER vs manual labelling | ✅ **Selesai 2026-05-28** — `comparison_srl_vs_manual.md`. Per-label F1: PERSON=0.978, LOCATION=0.975, EVENT=0.919, TIME=0.926. Micro F1=0.972 di 800 common chunks. |
| Periodisasi v3 (apply ke nodes_v3 + edges_v3) | ✅ **Selesai 2026-05-28 sore**. 44 EVENT semua dapat `periode_bab` (0 unmapped). `apply_period_to_v3.py` copy page_range curated dari v2 + derive baru dari chunk halaman untuk EVENT v3-only. |
| Neo4j import script v3 (`import_sirah_v3.cypher`) | ✅ **Selesai 2026-05-28 sore**. 988 Person + 44 Event + 15 Period + 46 IN_PERIOD + constraints. |
| SNA re-run di KG v3 | ✅ **Selesai 2026-05-28 sore**. 4 script (sna_analysis, sna_graph_metrics, event_centrality, community_wordcloud) di-add CLI flag `--version v3`. Output di `data/result/analysis/v3/`. **Person graph: 254 nodes, 3562 edges, density 0.111, transitivity 0.81, Louvain Q=0.351 (vs v2 Q=0.327, +7%), 19 communities, ARI(Louvain,Greedy)=0.754.** Top 10 PR: Muhammad, Amr Bin Umayyah, Abdullah Bin Ubay, Abu Jahal, Abu Bakar, Aisyah, Ali, Utsman, Abu Sufyan, Umar. Top 10 Event PR: Perang Badr, Uhud, Khandaq, Baiat Aqabah Kubra, Khaibar, Dzul Usyairah, Dzatur Riqa, Hudaibiyah, Bani Al-Ashfar, Tha'If. |
| Validasi tokoh "Amr Bin Umayyah" rank #2 PR | ✅ **Selesai 2026-05-28 malam** — `validation_amr_bin_umayyah.md`. Verdict: **artifact metodologi**, bukan real centrality. 3 dari 4 INVOLVED_IN false-positive (Badr/Uhud/Tabuk; hanya Khandaq legit). Real role: kurir Nabi → Najasyi (sudah ke-capture benar di SAHABAT). Akar masalah: proximity-based INVOLVED_IN over-extraction. |
| Manual validation 10 sample LLM verb extraction | ✅ **Selesai 2026-05-28 malam** — `manual_validation_10samples.md`. **90% effective valid** (5 VALID + 4 PARTIAL + 1 WRONG). Findings: LLM strong di micro-events tanpa proper noun + semantic predicate (MEMBUNUH/MEMUKUL/MENGUTUS). Pattern false-positive: parallel construction inference + schema force-fit unary→binary. |
| Lifecycle events enrichment (8 events) | ✅ **Selesai 2026-05-28 malam** — `add_lifecycle_events.py` (hybrid manual + auto-discover). +8 EVENT (Kelahiran Nabi, Wahyu Pertama, Hijrah ke Habasyah, Pemboikotan Bani Hasyim, Tahun Berduka, Hijrah ke Madinah, Haji Wada', Wafat Nabi). +99 edges auto-discovered (46 INVOLVED_IN + 44 OCCURRED_AT + 7 OCCURRED_ON + 2 IN_PERIOD baru). EVENT count 44→52 (+18%). Period dengan EVENT 12/15→14/15. Louvain Q 0.351→0.364. **Top 10 Event PR sekarang balanced narrative** (5 dari 10 = lifecycle: Hijrah Madinah, Kelahiran, Wafat, Wahyu Pertama, Pemboikotan), bukan 100% peperangan. |
| Visualisasi Neo4j (Cypher + matplotlib) | ✅ **Selesai 2026-05-28 malam** — `visualization_queries_v3.cypher` (20 query: per-period, 5 case study, per-community, ego-network, descriptive stats) + `case_study_*.png` (5 PNG + panel) re-rendered ke v3 enriched. |

### Catatan progres terakhir (sesi: 2026-06-09 — EDA + Error Analysis NER untuk revisi bimbingan 5 Juni)

Revisi bimbingan **2026-06-05** (next bimbingan **11 Juni**) minta: EDA, analisis kelas rendah, pembahasan error (bukan cuma angka), + skenario baru (model lain, weighted-CE, POS-tag, parafrase). Fokus sesi ini = **EDA + error analysis (no-GPU, selesai)**; skenario baru = rancangan (GPU tersedia).

**Output baru:**
- **EDA** — `src/analysis/eda_ner_dataset.py` → `data/result/analysis/eda/` (eda_ner_dataset.md + 2 chart). Temuan: `text_id`=chunk (1.094 chunk), EVENT 2,7%/TIME 4,2% (test) = minoritas, **imbalance ≈25:1**. `pos_tag` di CSV semua `NN` (placeholder — belum dipakai).
- **Error analysis** — `src/pseudo_labelling/SRL-NER/error_analysis.py` → `data/result/analysis/error_analysis/` (report + confusion PNG + error_examples.md + test_predictions.csv). Re-predict test lokal pakai model pemenang S3.2 iter-4 (bobot ada di disk; F1 recompute 0,9498 ≈ resmi 0,9537).
- **Deliverable** — `docs/bimbingan/2026-06-11.md` (5 bagian, peta revisi→status).

**Temuan kunci (untuk Bab 4 pembahasan):**
1. Error NER **didominasi deteksi (miss/over), BUKAN misklasifikasi tipe** — confusion antar-kelas hanya ~5 token. Model paham 4 tipe; masalahnya boundary/detection.
2. **Inkonsistensi gold** (manual labelling semi-auto keyed kapitalisasi): `Perang` kapital **40/40→EVENT** vs `perang` kecil **26/26→O**. Model deteksi lowercase → "FP" yang sebetulnya benar ⟹ precision EVENT/TIME ter-*underestimate*.
3. **Artefak OCR** = boundary error: % token entitas gold ber-tanda-baca-nempel LOCATION 45,7% / EVENT 28% / TIME 18,5% / PERSON 16,4%.
4. Model **over-deteksi** keseluruhan: 1.804 pred > 1.759 gold (49 chunk over vs 18 under).
5. F1 per-kelas mengikuti urutan jumlah data persis (EVENT<TIME<LOCATION<PERSON) → few-shot = faktor utama.

**Verifikasi model skenario C:** `cahya/bert-base-indonesian-1.5G` & `cahya/distilbert-base-indonesian` **ada di HF**, tapi **uncased** (vs IndoBERT cased) → ganti = hilangkan sinyal kapital (eksperimen relevan dgn temuan #2). **Belum di-scaffold/run.**

### Catatan progres terakhir (sesi: 2026-06-05 — Interpretasi visual Neo4j + sync angka weighted + PRECEDES Kelahiran)

Deliverable `docs/bimbingan/2026-06-04.md` **Bagian A direstruktur jadi visualisasi-first dari Neo4j** (A.0 panduan baca → A.1 ego Muhammad → A.2 komunitas → A.3 studi kasus → A.4 periode → A.5 PRECEDES; metrik lama turun jadi **Lampiran A.6–A.10**). Screenshot Neo4j ditafsir dari gambar asli (folder `docs/bimbingan/screenshots/` + `README.md` checklist). **Temuan visual:** Neo4j Browser mewarnai **per-LABEL** bukan per-komunitas (untuk komunitas → pakai PNG matplotlib `sna_person_network.png`); perbandingan ego **Muhammad (40+) vs Abu Bakar (16) vs Abu Sufyan (8)** = bukti sentralitas visual paling kuat.

**⚠️ SYNC ANGKA (supersede angka count-based di tabel "v3 cleaned" 2026-05-30 di bawah):** graf Person SNA sekarang **WEIGHTED** (threshold INVOLVED_IN ≥0,3 + bobot pasangan Σ min(w₁,w₂)). **Angka resmi deliverable: graf Person 208 node / 1832 edge, density 0,085, Louvain 15 komunitas Q=0,385, ARI 0,78.** (Angka lama 239 node / 11–12 komunitas / Q 0,350 = count-based, **USANG**.) Amr Bin Umayyah artifact #4→#18, Khadijah masuk top-10. **Jangan tertukar 2 graf:** KG penuh = **1191 node / 586 edge**; graf Person SNA (proyeksi co-participation) = **208 node / 1832 edge**.

**PRECEDES (2026-06-05):** ditambah `Kelahiran Nabi → Perang Fijar` di `fix_precedes_v3.py` + re-run → rantai **24 event / 23 panah** (Kelahiran → … → Wafat Nabi). Sekalian fix bug laten nama node `Isra' Mi'raj` (sebelumnya ter-skip krn nama usang "Isra' Dan Mi'Raj" di script). KG penuh 585→**586 edge**. Cypher v3 di-regenerate. Backup CSV: `edges_v3.csv.bak_precedes_kelahiran`.

---

### Catatan progres terakhir (sesi: 2026-06-03 — Deliverable bimbingan 4 Juni + skenario G7/G8)

Disiapkan dokumen tunggal siap-tampil **`docs/bimbingan/2026-06-04.md`** (4 bagian): **A** interpretasi graf (apa yang diperoleh, bukan sekadar angka); **B** tabel skenario NER (tangga S1→S2→S3, winner F1 0,9537 — gain murni di kelas minoritas/macro-avg via augmentasi, contrastive sendiri tak menggerakkan minoritas); **C** rancangan + hasil skenario graf **G1–G8** (top-10 siap Bab 4 + glosarium istilah bahasa awam + perbandingan v2↔v3); **D** studi kasus QASiNa (9,6% upper-bound). Dua skenario graf baru dihitung via `src/analysis/scenario_g7_g8.py`: **G7 lokasi sentral** (weighted_degree: Madinah 684 > Makkah 595; betweenness degenerate krn graf lokasi padat) & **G8 keberagaman fase tokoh** (Muhammad 6/6 fase; Ali 8 event tapi cuma 2 fase). Catatan penyajian NER: λ-sweep & S3.1 dikeluarkan dari tabel skenario (tuning, bukan skenario), S2 pakai angka run terkontrol 0,9522 + disclosure varians run-to-run, S3.2→S3.

> Detail lengkap di `progress_log.md` → `[2026-06-03]`.

### Catatan progres 2026-05-30 — Cleanup node KG v3

**Cleanup node v3 — alias merge + filter false-positive.** Menutup gap pipeline: jalur inference NER tidak pernah melewati alias clustering (yang ada di jalur v2). Script baru `src/relation_extraction/clean_v3_nodes.py` (idempotent, `--apply`, backup `.bak_clean`) menjalankan 4 operasi di tahap konstruksi KG (BUKAN ubah evaluasi NER — F1 0.9537/0.972 tidak berubah):
- **OP1** alias_map case-insensitive (~70 rename: Rasulullah→Muhammad, Ali Bin Abi Thalib→Ali bin Abu Thalib).
- **OP2** case-dedup (~36 merge: Perang Bu'Ats→Perang Bu'ats, Tha'If→Tha'if).
- **OP3** drop generic EVENT FP (`Perang`, `Malam`, `Peperangan` — manifestasi precision EVENT 0.913).
- **OP4** fix mislabel `Jabal Uhud` (EVENT→alias LOCATION `Uhud`).
- REVIEW (disengaja TIDAK di-merge, keputusan historis): Baiat Aqabah~Kubra, Isra' Mi'raj~Mi'Raj, Perang Badr~Badr Kubra/Ula.

**Hasil utama (perbandingan):**

| | v3 enriched | **v3 cleaned (2026-05-30)** |
|---|---:|---:|
| Nodes total | 1288 | **1191** |
| EVENT | 52 | **46** |
| Edges total | 590/597 | **585** |
| PERSON node | ~988 | **899** |
| Person graph nodes / edges | 261 / 4096 | **239 / 3277** |
| Density | 0.121 | **0.1152** |
| Louvain Q (proper) | 0.364 | **0.3499** |
| Communities | 16 | **11–12** |

**Top 10 Person PR (v3 cleaned):**
Muhammad → **Ali bin Abu Thalib** (⬆ dari ~#7 — efek konsolidasi alias) → Abu Bakar → **Amr Bin Umayyah** (⬇ ke #4, artifact ter-mitigasi) → Abu Jahal → Abdullah bin Ubay → Aisyah → Umar → Utsman → Abu Sufyan. **Temuan:** alias merge memperbaiki centrality, bukan cuma kosmetik.

**Top 10 Event PR (v3 cleaned):**
Perang Badr → Uhud → Khandaq → **Hijrah Ke Madinah** ✨ → **Kelahiran Nabi** ✨ → **Wafat Nabi** ✨ → Baiat Aqabah Kubra → **Wahyu Pertama** ✨ → Perang Dzul Usyairah → **Pemboikotan Bani Hasyim** ✨. (5 lifecycle tetap di top-10 → balanced narrative dipertahankan.)

> Detail lengkap di `progress_log.md` → `[2026-05-30] Cleanup node KG v3`.

**Findings utama:**
1. **Validasi Amr Bin Umayyah:** rank #2 PR adalah artifact (3 dari 4 INVOLVED_IN false-positive). Real role: kurir Nabi → Najasyi. Akar masalah: proximity-based INVOLVED_IN over-extraction.
2. **POC LLM verb extraction validated:** 90% effective valid (5 VALID + 4 PARTIAL + 1 WRONG). Strong di micro-events tanpa proper noun + semantic predicate. Estimasi scale-up full corpus ~1770 EVENT (40× current), cost ~$45 API.
3. **Lifecycle enrichment justified:** Bu Diana 2026-05-16 catat "event sangat sedikit jadi perlu ditambahkan lagi". 8 events (Kelahiran/Wahyu/Hijrah Habasyah/Pemboikotan/Tahun Berduka/Hijrah Madinah/Haji Wada'/Wafat) di-add hybrid manual + auto-discover relasi.

**Comparison NER v3 vs Manual labelling (Bu Diana request, masih valid):**

| Label | Precision | Recall | F1 |
|---|---:|---:|---:|
| PERSON | 0.972 | 0.984 | **0.978** |
| LOCATION | 0.967 | 0.983 | **0.975** |
| EVENT | 0.913 | 0.925 | **0.919** |
| TIME | 0.914 | 0.938 | **0.926** |
| **MICRO** | **0.965** | **0.979** | **0.972** |

**Output v3 enriched (semua sudah re-computed):**
- `data/result/relation_result/{nodes,edges}_v3.csv` (+8 EVENT, +99 edges)
- `data/result/neo4j/import_sirah_v3.cypher` (52 Event + 65 IN_PERIOD)
- `data/result/neo4j/visualization_queries_v3.cypher` 🆕 (20 query templates)
- `data/result/analysis/v3/` (sna_metrics + summary + person_network.png + graph_metrics + event_centrality + community_wordclouds + case_study x6 + validation_amr.md)
- `data/result/llm_verb_extraction/manual_validation_10samples.md` 🆕

> 📜 **Detail historis lengkap** ada di **`progress_log.md`** di root.

**Action item aktif (pre-bimbingan):**
1. ✅ Apply `event_period.py` ke nodes_v3.csv → assign period per EVENT.
2. ✅ Generate `import_sirah_v3.cypher` (Neo4j import script) dari v3.
3. ✅ Re-run SNA scripts di KG v3.
4. ✅ Visualisasi (Cypher queries + matplotlib PNG).
5. ✅ Validasi tokoh "Amr Bin Umayyah" (verdict: artifact).
6. ✅ Manual validation 10 sample LLM verb extraction (90% effective valid).
7. ✅ Lifecycle events enrichment (+8 EVENT, +99 edges, top-10 balanced).
8. ⏳ Slide bimbingan: 1 S3.2 winner + 1 comparison + 1 KG v3 enriched + lifecycle + validasi findings.
9. ⏳ Setup Neo4j Desktop dual-DBMS untuk side-by-side v2 vs v3 visual (Bu Diana request).

**Post-bimbingan / future work:**
10. ⏳ Scale-up LLM verb extraction (Opsi B 50 chunks via batch chat ~25 menit, atau Opsi C full corpus via API ~$45).
11. ⏳ 1 bug pending: `OCCURRED_AT weight=2.0`. (`PRECEDES stale v1 mapping` ✅ **RESOLVED** 2026-06-05 — rantai kronologi benar via `fix_precedes_v3.py`, Kelahiran Nabi disambung; bug "Fathul Makkah→Uhud" tidak ada lagi di v3.)
12. ⏳ Validasi tambahan top-50 PR Person — cocokkan dengan literatur Sirah untuk identify other artifacts.
13. ⏳ `case_study_events.py`, `entity_frequency_per_period.py`, `edge_period_cooccurrence.py` — belum di-flag `--version v3` (low priority).

### Catatan honest pre-bimbingan

- **v3 enriched bukan "pure NER"** — 8 lifecycle events di-add manual karena NER tidak bisa capture event yang disebut dalam verb-construction ("beliau wafat") atau descriptive phrase ("turunnya wahyu pertama"). Relasi-relasinya tetap auto-discovered dari NER predictions di anchor chunks. Disclosure ini perlu di Bab 4.
- **Amr Bin Umayyah artifact tetap ada** di v3 enriched — lifecycle hanya nge-shift dia 1 rank turun, tidak fix root cause. Solusi LLM verb extraction tetap di future work.
- **Page filter manual** untuk anchor chunks rentan kalau bab Sirah versi lain punya numbering berbeda. Reproduce ter-tied ke Mubarakfuri terjemahan Kathur Suhardi.

### Skenario SRL-NER aktif (per 2026-05-26)

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa class weight, contrastive, augmentation | ✅ TEST Seq F1 entity = 0.9518 (re-eval seqeval lokal). |
| **S2a — SCL + Baseline** | S1 + Strict Supervised Contrastive (Khosla 2020), λ_C=0.3 | ✅ TEST Seq F1 = 0.9215. |
| **S2b — JSCL + Baseline** | S1 + Jaccard Sim Contrastive (Dewabharata et al.), λ_C=0.3 | ✅ TEST Seq F1 = 0.8915. SCL > JSCL konsisten. |
| **S3.1 — λ_C sweep** | S2 SCL dengan λ_C ∈ {0.1, 0.2, 0.3} → pilih winner | ✅ Selesai 2026-05-26. **Winner λ_C=0.3 iter-4 = 0.9522** (>S1). λ_C=0.1=0.9477, λ_C=0.2=0.9470. |
| **S3.2 — Mention Replacement Augmentation** | S3.1 winner (λ_C=0.3) + train_augmented_v2.csv (260 augmented sentences) | ✅ **Selesai 2026-05-26. WINNER FINAL = 0.9537** (EVENT 0.8454, TIME 0.9007). 4 iter, 46.5 min Colab T4. |

Detail metodologi + sketsa kode di `docs/skenario/srl_ner.md`. Hasil seqeval lengkap di `data/result/pseudo-labelling/SRL-NER/seqeval_results.md`.

**Catatan honest:** S3.2 lewati S1 baseline dengan margin tipis (+0.0019) tapi **per-class minoritas naik signifikan**. F1 EVENT +0.0746, F1 TIME +0.0653. Hipotesis Bu Diana di bimbingan 2026-05-16 ("augmentation untuk close gap kelas minor") **terbukti benar**. PERSON tetap kuat (0.9613), LOCATION naik tipis (+0.0049). Self-training konvergen lebih cepat (4 iter vs 6 iter di S3.1 λ=0.1) — augmentation membantu model belajar minoritas dari iter pertama.

---

## Pipeline
```
PDF → OCR (PaddleOCR) → CSV → Preprocessing → Chunking
    → Manual Labelling (semi-auto, regex + keyword)
    → NER: SRL-NER (BERT iterative self-training)  ← LLM-NER dibatalkan
    → Alias Clustering (manual clusters + Jaro-Winkler)
    → Temporal Detection (intra-sentence + urutan bab)  ← BARU (revisi 2026-05-03)
    → Relation Extraction (proximity + temporal-aware, weighted, + Person-Person + Event chronology)
    → Social Network Analysis
        ├─ Node-level: centrality (degree, betweenness, closeness, PageRank)
        └─ Graph-level: density, clustering coefficient, network size, community detection  ← diperluas
    → Studi kasus 3–5 event (Perang Badar dkk.) → sub-graph + analisis
    → Neo4j Knowledge Graph
```

---

## Hal Penting yang Perlu Diingat
- Dataset dalam **Bahasa Indonesia**, bukan Arab
- Nama tokoh bisa bervariasi ejaannya (contoh: "Muhammad", "Rasulullah", "Nabi SAW") — perlu normalisasi
- Entitas `PERSON` mencakup nama individu **dan** nama kabilah/Bani
- Jangan edit file di `data/pages/` (gambar PNG asli hasil render PDF)
- Virtual environment ada di folder `venv/` — jangan dimodifikasi strukturnya
- Format output antarpipeline: **CSV**

---

## Perintah yang Sering Dipakai
```powershell
# Aktifkan virtual environment (Windows)
venv\Scripts\activate

# Jalankan Jupyter Notebook
jupyter notebook

# Install dependencies
pip install -r requirements.txt
```

---

## Prinsip Komunikasi (dari `instruksi.txt`)

**Utamakan kejujuran, akurasi, dan kejelasan di atas terdengar yakin.** Prioritas: jawaban yang benar + transparan tentang apa yang diketahui, belum diketahui, atau sedang disimpulkan.

**1. Ketidakpastian** — kalau belum yakin, bilang. Pakai frasa seperti:
- "Saya belum sepenuhnya yakin, tapi…"
- "Ini sebaiknya dicek lagi…"
- "Berdasarkan informasi yang tersedia…"
- "Ini perkiraan terbaik saya, bukan fakta terkonfirmasi"

Jangan sajikan informasi belum pasti seolah fakta. Kalau jawaban depend on konteks yang belum ada, sebut konteks apa yang kurang. Kalau ada beberapa kemungkinan, jelaskan kemungkinan utamanya — jangan paksa satu jawaban.

**2. Sumber** — jangan mengarang. Jangan buat-buat: judul paper, URL, penulis, studi, statistik, buku, kutipan, atau referensi sejarah (termasuk hadits/riwayat Sirah). Kalau tidak bisa sebut sumber nyata yang bisa dicek, katakan saja. Kalau jawaban berdasarkan pengetahuan umum, jelaskan dengan jujur. Prioritaskan dokumentasi resmi, sumber primer, paper peer-reviewed.

**3. Angka & Statistik** — beri tanda kalau belum benar-benar pasti. Pakai frasa "kurang lebih", "angka ini mungkin sudah berubah", "cek ke sumber utama". Jangan mengarang angka. Berikan range hanya kalau masuk akal.

**4. Informasi Terbaru** — jangan menebak hal yang mungkin sudah berubah (versi software, library, fitur model, data pasar). Bilang informasinya mungkin perlu di-cek ulang.

**5. Orang & Kutipan** — jangan mengaitkan kutipan ke orang nyata kecuali yakin. Kalau ragu: "Saya belum bisa memastikan kutipan ini akurat" atau "Saya tidak tahu sumber asli kutipan ini". Pisahkan fakta terkonfirmasi dari interpretasi.

**Konteks proyek ini:** karena ini Sirah Nabawiyah, hati-hati ekstra dengan klaim historis (peristiwa, tahun, tokoh, kutipan riwayat). Kalau aku bilang "Perang X terjadi tahun Y" tanpa cek, itu pelanggaran prinsip ini. Default: rujuk balik ke teks Mubarakfuri yang sudah di-OCR di repo, atau bilang belum di-verifikasi.

---

## Catatan untuk Claude
- Kalau mengedit notebook `.ipynb`, pastikan struktur cell tetap rapi
- Kalau ada kode baru, simpan juga versi `.py`-nya di folder yang sama
- Output selalu disimpan ke subfolder yang sesuai di `data/result/`
- Tanyakan dulu sebelum mengubah logika preprocessing atau chunking yang sudah ada
- Kalau ingin menambah changelog sesi baru, tulis ringkasan singkat di section **"Catatan progres terakhir"** dan **append detail lengkap ke `progress_log.md`** — jangan biarkan CLAUDE.md membengkak lagi (target <40k karakter).
