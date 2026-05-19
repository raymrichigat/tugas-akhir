# CLAUDE.md — Proyek Tugas Akhir: Knowledge Graph Sirah Nabawiyah

## Deskripsi Proyek
Membangun Knowledge Graph dari teks Sirah Nabawiyah (Bahasa Indonesia) menggunakan pendekatan NER (Named Entity Recognition) berbasis SRL (Semantic Role Labeling) dengan BERT iterative self-training, lalu menyimpan hasilnya di Neo4j dan dianalisis dengan SNA.

**Sumber data:** Buku "Sirah Nabawiyah" oleh Syaikh Shafiyyurrahman Al-Mubarakfuri, terjemahan Kathur Suhardi (633 halaman, Bahasa Indonesia)

> **Catatan revisi 2026-05-03:** LLM-NER **tidak jadi digunakan** (keputusan Bu Diana). Fokus penuh ke **SRL-NER** saja. Folder `src/pseudo_labelling/LLM-NER/` dipertahankan sebagai arsip eksplorasi, tidak masuk pipeline final.

---

## Tech Stack
- **Bahasa:** Python (Jupyter Notebook `.ipynb` + `.py`)
- **Database:** Neo4j (Knowledge Graph)
- **OCR:** PaddleOCR (`ocr_paddle.py`)
- **NER:** **SRL-based** saja (Semantic Role Labeling, BERT iterative self-training).
  - LLM-NER (QLoRA, mengikuti thesis Andrian) sudah diimplementasikan tapi **tidak dipakai** per revisi 2026-05-03 — disimpan di `src/pseudo_labelling/LLM-NER/` sebagai arsip.
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
│   │   ├── bab3_lengkap_revisi.md
│   │   └── bab3_revisi_paragraf.md
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
    |   ├── LLM-NER/                          ← ❌ DEPRECATED (lihat DEPRECATED.md)
    |   |   ├── DEPRECATED.md                 ← penanda dibatalkan (revisi 2026-05-03)
    |   |   ├── PENJELASAN_THESIS_ANDRIAN.md  ← referensi metodologi Andrian (arsip)
    |   |   ├── asli/                          ← penerapan asli Andrian (baseline supervised)
    |   |   |   ├── llm_ner_sirah.py
    |   |   |   ├── llm_ner_sirah_colab.ipynb
    |   |   |   ├── llm_ner_sirah_kaggle.ipynb
    |   |   |   └── _build_notebooks.py
    |   |   └── pseudo/                        ← versi TA: + iterative self-training
    |   |       ├── llm_ner_sirah.py           ← copy untuk import
    |   |       ├── llm_ner_sirah_selftraining.py  ← ★ kontribusi self-training
    |   |       ├── llm_ner_sirah_colab.ipynb
    |   |       ├── llm_ner_sirah_kaggle.ipynb
    |   |       ├── README_SELFTRAINING.md
    |   |       └── _build_notebooks.py
    |   ├── SRL-NER/
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
| NER Pipeline (SRL-based, BERT iterative self-training) | 🔄 **S1 ✅ + S2 ✅ + S3 ⏳ (deadline 29 Mei 2026).** S1 baseline reuse hasil E1 lama (Seq F1 entity=0.959). S2 selesai 2026-05-14/15: S2a SCL final 0.950/peak 0.953, S2b JSCL final 0.933/peak 0.940. **Plan S3 baru post-bimbingan 2026-05-16:** (1) λ_C sweep (0.1/0.2/0.3) di S2 SCL untuk close gap entity-level vs S1, (2) Mention Replacement augmentation di atas winner. Approved Bu Diana. |
| NER Pipeline (LLM-based, Instruction Fine-Tuning + QLoRA) | ❌ **Tidak jadi dipakai** (revisi 2026-05-03). Arsip + `DEPRECATED.md` di `src/pseudo_labelling/LLM-NER/`. |
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

### Catatan progres terakhir (sesi: 2026-05-16 bimbingan + 2026-05-20 propagasi outcome)

**Bimbingan Bu Diana 2026-05-16 sudah dilaksanakan**, dual-focus graf + S2 SRL-NER. Outcome resmi sudah dipropagasi ke `docs/bimbingan/revisi_dosen.md` Putaran 5 + `docs/bimbingan/bimbingan_template.md` + `docs/skenario/srl_ner.md`. Catatan mentah di `docs/bimbingan/2026-05-16_outcome.md`.

**Keputusan utama dari bimbingan:**

1. ✅ **Plan 3-skenario approved** Bu Diana (S1 baseline / S2 SCL+JSCL / S3 = best dari S2 + augmentation).
2. ⏰ **Deadline S3: 29 Mei 2026** (~9 hari).
3. 🔄 **S3 plan di-revisi**: tune λ_C dulu (sweep 0.1/0.2/0.3 di S2 SCL) untuk close gap entity-level S2 (0.95) vs S1 (0.959), baru stack augmentation di atas winner. Bukan langsung augment dengan default λ_C=0.3.
4. 📋 **Revisi tambahan untuk graf** (perlu dikerjakan sebelum bimbingan berikutnya):
   - Centrality juga untuk node Event (selain Person)
   - Wordcloud per-komunitas + interpretasi semantik tiap komunitas + arti Q-value
   - Analisis event-related untuk 5 case study (event co-occur per period)
   - Visualisasi prefer Neo4j (bukan PNG static)
5. 📋 **Arahan baru pipeline NER**:
   - Frekuensi entitas per period → justifikasi
   - LLM verb extraction → tambah Event entity (antisipasi support EVENT kecil)
6. 📋 **Bimbingan berikutnya**: pipeline running end-to-end dengan output SRL-NER, comparison report SRL-NER vs manual labelling, mulai pembukuan per-Bab.

**Action item aktif (deadline 29 Mei):**
1. ⏳ Run S3.1 — λ_C sweep di S2 SCL (~6-8 jam GPU T4)
2. ⏳ Validasi manual augmented sentences (20-30 sample)
3. ⏳ Run S3.2 — Mention Replacement augmentation di atas winner λ_C (~3-4 jam GPU T4)
4. ⏳ Inference NER terbaik → regenerate `nodes_v3.csv` + `edges_v3.csv`
5. ⏳ Comparison report SRL-NER vs manual labelling
6. ⏳ Centrality untuk Event + wordcloud per-komunitas + analisis event-related case study + frekuensi entitas per-period
7. ⏳ LLM verb extraction (POC dulu di sample chunks)
8. ⏳ 2 bug pending: `OCCURRED_AT weight=2.0` + `PRECEDES stale v1 mapping` (post-deadline kalau mepet)

> 📜 **Detail historis lengkap** (sesi 2026-04-16 s/d 2026-05-15, termasuk run S2 + persiapan bimbingan) dipindahkan ke **`progress_log.md`** di root. Buka file itu kalau perlu konteks/kronologi pekerjaan terdahulu.

### Skenario SRL-NER aktif (per 2026-05-20)

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa class weight, contrastive, augmentation | ✅ Reuse hasil E1 lama (Seq F1 entity=0.959, F1 EVENT=0.816) |
| **S2a — SCL + Baseline** | S1 + Strict Supervised Contrastive (Khosla 2020), λ_C=0.3 | ✅ Selesai 2026-05-14/15. Seq F1 final iter-6 = 0.950, peak 0.953. Token F1 = 0.9955. |
| **S2b — JSCL + Baseline** | S1 + Jaccard Sim Contrastive (Dewabharata et al.), λ_C=0.3 | ✅ Selesai 2026-05-14/15. Seq F1 final iter-6 = 0.933, peak 0.940. Token F1 = 0.9945. |
| **S3.1 — λ_C sweep** | S2 SCL dengan λ_C ∈ {0.1, 0.2, 0.3} → pilih winner | ⏳ Plan post-bimbingan, deadline 29 Mei. ~6-8 jam GPU T4. |
| **S3.2 — Mention Replacement Augmentation** | S3.1 winner + Dai & Adel 2020 augmentation | ⏳ Depend on S3.1, ~3-4 jam GPU T4. |

Detail metodologi + sketsa kode di `docs/skenario/srl_ner.md`. Detail per-epoch S2 di `src/pseudo_labelling/SRL-NER/S2-seqeval.md`. Paper rujukan: `Contrastive_Learning.pdf` (Dewabharata dkk., ITS — SCL+JSCL untuk multi-label).

**Catatan honest:** Seq F1 entity-level S2 (~0.95) sedikit di bawah S1 baseline 0.959 (gap ~0.01). Token-level F1 S2 (~0.995) justru lebih tinggi dari S1. Hipotesis: λ_C=0.3 terlalu agresif → trade-off antara per-token classification vs entity boundary. SCL > JSCL konsisten ~+0.01. **S3.1 λ_C sweep adalah upaya empirical untuk close the gap** sebelum lompat ke augmentation.

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

## Catatan untuk Claude
- Kalau mengedit notebook `.ipynb`, pastikan struktur cell tetap rapi
- Kalau ada kode baru, simpan juga versi `.py`-nya di folder yang sama
- Output selalu disimpan ke subfolder yang sesuai di `data/result/`
- Tanyakan dulu sebelum mengubah logika preprocessing atau chunking yang sudah ada
- Kalau ingin menambah changelog sesi baru, tulis ringkasan singkat di section **"Catatan progres terakhir"** dan **append detail lengkap ke `progress_log.md`** — jangan biarkan CLAUDE.md membengkak lagi (target <40k karakter).
