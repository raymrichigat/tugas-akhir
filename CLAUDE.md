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
| NER Pipeline (SRL-based, BERT iterative self-training) | 🔄 **S1 ✅ + S2 ✅ + S3 ⏳.** S1 baseline reuse hasil E1 lama (Seq F1 entity=0.959). **S2 selesai run 2026-05-14/15** di Colab dengan dual-metric (token-level sklearn + entity-level seqeval): S2a SCL final 0.950/peak 0.953, S2b JSCL final 0.933/peak 0.940 — trend monotonik naik lintas 6 iterasi, gap kecil ~0.01 vs S1. Detail per-epoch di `src/pseudo_labelling/SRL-NER/S2-seqeval.md`. **S3 augmentation** (Mention Replacement Dai & Adel 2020) script + data siap, belum run — tunggu approval Bu Diana untuk pilih SCL vs SCL+JSCL. |
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

### Catatan progres terakhir (sesi: 2026-05-13 s/d 2026-05-16 — S2 selesai + bimbingan)

Rangkaian sesi 2026-05-13 → 2026-05-16 fokus ke **eksekusi S2 + persiapan & pelaksanaan bimbingan Bu Diana**:

1. **S2 Contrastive Learning selesai run** (Colab, 14-15 Mei). S2a SCL dan S2b JSCL keduanya tuntas 6 iterasi self-training × 10 epoch. Output di `src/pseudo_labelling/SRL-NER/done_running/S2_Contrastive_Learning/` (notebook + models + evaluation xlsx).
2. **Dual-metric evaluation** — selain token-level sklearn (yang sudah ada), ditambahkan **entity-level seqeval** via `evaluate_seqeval.py` (lokal) + `seqeval_addendum_colab.md` (cell tambahan untuk re-eval di Colab tanpa re-train). Hasil epoch-by-epoch + ringkasan final di `src/pseudo_labelling/SRL-NER/S2-seqeval.md`.
3. **Hasil S2 (Seq F1 entity-level, comparable dengan S1 baseline 0.959):** S2a SCL final iter-6 = **0.950** (peak 0.953 di iter-6 ep-4), S2b JSCL final iter-6 = **0.933** (peak 0.940 di iter-5 ep-3). Trend **monotonik naik** lintas iterasi (SCL: 0.924 → 0.950, JSCL: 0.904 → 0.940). SCL > JSCL konsisten ~+0.01. Gap ~0.01 vs S1 — kemungkinan λ_C=0.3 terlalu agresif (trade-off entity boundary vs token classification).
4. **Visualisasi case study 5 event** — 5 PNG individual (Badr/Uhud/Hudaibiyah/Khaibar/Tabuk) + `case_study_panel.png` gabungan via `src/analysis/visualize_case_study_events.py`. Siap untuk slide bimbingan.
5. **Neo4j community import script tambahan** — `data/result/neo4j/import_community_v2.cypher` untuk inject property community + centrality dari `sna_metrics.csv` ke Person nodes (color by community di Neo4j Browser).
6. **3 dokumen prep bimbingan disiapkan:** `bimbingan_2026_05_13.md` (S2-fokus), `bimbingan_graf_2026_05_14.md` (graf-fokus lengkap), dan `bimbingan_2026_05_16.md` (combined final — graf + S2 dual-metric, skrip presentasi 20-25 menit + Q&A).
7. **Bimbingan Bu Diana 2026-05-16 sudah dilaksanakan** — outcome belum di-catat di file ini (akan ditindak terpisah).

**Action item terbawa ke sesi sekarang:**
1. ⏳ Catat outcome bimbingan 2026-05-16 ke `revisi_dosen.md` (Putaran 5) + propagasi ke `bimbingan.md`/`srl_ner_skenario.md` sesuai arahan baru.
2. ⏳ Run S3a (+ S3b kalau Bu Diana minta keduanya) di Colab — script & augmented data siap (~3-4 jam GPU T4/skenario).
3. ⏳ Pertimbangkan tuning λ_C (0.3 → 0.1/0.2) sebagai future work kalau gap S2 vs S1 mau di-close.
4. ⏳ Setelah S3 selesai + winner dipilih → inference ke seluruh `sirah_chunks_final.csv` → regenerate `nodes_v3.csv` + `edges_v3.csv` dengan NER baru → re-run relation extraction + SNA + Neo4j Cypher.
5. ⏳ 2 bug pending: `OCCURRED_AT weight=2.0` (aggregation bug di `relation_extraction.py`) + `PRECEDES stale v1 mapping` (anchor ke first-mention bukan page_range v2, Fathul Makkah → Perang Uhud salah arah). Dijadwalkan post-bimbingan.

> 📜 **Detail historis lengkap** (sesi 2026-04-16 s/d 2026-05-11, termasuk bug fixes notebook & pre_labelling/alias clustering, dan revisi dosen putaran 1-4) dipindahkan ke **`progress_log.md`** di root. Buka file itu kalau perlu konteks/kronologi pekerjaan terdahulu.

### Skenario SRL-NER aktif (per 2026-05-16)

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa class weight, contrastive, augmentation | ✅ Reuse hasil E1 lama (Seq F1 entity=0.959, F1 EVENT=0.816) |
| **S2a — SCL + Baseline** | S1 + Strict Supervised Contrastive (Khosla 2020) | ✅ **Selesai 2026-05-14/15.** Seq F1 final iter-6 = 0.950, peak 0.953 (iter-6 ep-4). Token F1 = 0.9955. |
| **S2b — JSCL + Baseline** | S1 + Jaccard Sim Contrastive (Dewabharata et al.) | ✅ **Selesai 2026-05-14/15.** Seq F1 final iter-6 = 0.933, peak 0.940 (iter-5 ep-3). Token F1 = 0.9945. |
| **S3a — SCL + Augmentation** | S2a + Mention Replacement (Dai & Adel 2020) | ⏳ Script & `train_augmented.csv` siap, belum run. Default rekomendasi: lanjut SCL saja (Bu Diana approve pending). |
| **S3b — JSCL + Augmentation** | S2b + Mention Replacement | ⏳ Opsional, run jika Bu Diana minta kedua varian. |

Detail metodologi + sketsa kode di `srl_ner_skenario.md`. Detail per-epoch S2 di `src/pseudo_labelling/SRL-NER/S2-seqeval.md`. Paper rujukan: `Contrastive_Learning.pdf` (Dewabharata dkk., ITS — SCL+JSCL untuk multi-label). Skenario lama (class weight + adaptive threshold dari 2026-05-07) di-arsip di `done_running/legacy_class_weight_adaptive/` — tidak masuk klaim utama, hanya dipakai sebagai ablation pembanding di Bab 4.

Catatan jujur S2: Seq F1 entity-level ~0.95 sedikit di bawah S1 baseline 0.959 (gap ~0.01). Token-level F1 S2 (~0.995) justru lebih tinggi dari S1. Hipotesis: λ_C=0.3 terlalu agresif → trade-off antara per-token classification vs entity boundary. SCL > JSCL konsisten ~+0.01 di semua iter. Action plan: lanjut S3 dulu, kalau gap belum tertutup baru tuning λ_C di future work.

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
