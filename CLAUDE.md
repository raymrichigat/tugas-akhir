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
| NER Pipeline (SRL-based, BERT iterative self-training) | ✅ **S1 ✅ + S2 ✅ + S3.1 ✅ + S3.2 ✅ (selesai 2026-05-26).** Final winner: **S3.2-scl-aug-iter4 = TEST F1 entity 0.9537** (melampaui S1=0.9518 dengan +0.0019). EVENT melonjak 0.7708→0.8454 (+0.0746). Augmentation v2 + λ_C=0.3 winning combo. Detail seqeval di `data/result/pseudo-labelling/SRL-NER/seqeval_results.md`. |
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

### Catatan progres terakhir (sesi: 2026-05-22→26 S3.1 sweep + S3.2 winner + Priority D)

**S3.2 menang!** SRL-NER pipeline selesai 2026-05-26 dengan TEST F1 entity = **0.9537** — pertama kali melampaui S1 baseline (0.9518) dengan margin +0.0019. Augmentation v2 (period-aware mention replacement, 260 augmented sentences) + λ_C=0.3 (winner S3.1) = winning combo.

**Hasil seqeval head-to-head (test set 258 kalimat, 1759 entities):**

| Tag | F1 entity | EVENT | TIME | Δ vs S1 |
|---|---:|---:|---:|---:|
| S1-baseline-iter6 | 0.9518 | 0.7677 | 0.8354 | — |
| S3.1-lambda03-iter4 | 0.9522 | 0.7708 | 0.8354 | +0.0004 |
| **S3.2-scl-aug-iter4** | **0.9537** | **0.8454** | **0.9007** | **+0.0019** ✅ |

Highlights S3.2: F1 EVENT melonjak 0.7708→0.8454 (+0.0746) sesuai hipotesis Bu Diana. F1 TIME juga naik 0.8354→0.9007 (+0.0653). Konvergen 4 iter dalam 46.5 menit.

**Priority D (5 deliverables) selesai paralel sambil S3.2 jalan:**
- ✅ #7 Centrality node Event (`event_centrality.{csv,_summary.md,_network.png}`) — 36 Event nodes, 15 komunitas. Top PageRank: Perang Badr > Khandaq > Uhud.
- ✅ #8 Wordcloud per komunitas (8 PNG + summary md, Q=0.317 = moderate, interpretasi 8 komunitas Person network).
- ✅ #9 Frekuensi entitas per-period (sudah pre-existing dari sesi sebelumnya).
- ✅ #10 Analisis event-related case study (sudah pre-existing — `edge_validation_summary.md`).
- ✅ #11 LLM verb extraction POC (`llm_verb_extraction_poc.py` + 18 EVENT + 28 SVO triplet, structured prompt single-batch chat).

> 📜 **Detail historis lengkap** (sesi 2026-04-16 s/d 2026-05-26, termasuk S3.1 sweep + S3.2 winner + Priority D) ada di **`progress_log.md`** di root.

**Action item aktif (post-S3.2 winner):**
1. ⏳ Inference NER terbaik (S3.2-scl-aug-iter4) → regenerate `nodes_v3.csv` + `edges_v3.csv` di seluruh `sirah_chunks_final.csv`.
2. ⏳ Comparison report SRL-NER best vs manual labelling ground truth.
3. ⏳ Manual validation 5-10 sample LLM verb extraction (cross-check ke teks Mubarakfuri) untuk dapat angka precision konkret.
4. ⏳ Tulis paragraf hasil di laporan / slide bimbingan untuk semua 5 deliverable Priority D.
5. ⏳ Visualisasi Neo4j (bukan PNG static) — screenshot + cypher query saved.
6. ⏳ Scale-up LLM verb extraction (Opsi B: 50 chunks via batch chat ~25 menit; atau Opsi C: full coverage via API ~$6-10).
7. ⏳ 2 bug pending (post-deadline): `OCCURRED_AT weight=2.0` + `PRECEDES stale v1 mapping`.

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
