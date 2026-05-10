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
| NER Pipeline (SRL-based, BERT iterative self-training) | ✅ **Selesai run 3 skenario E1 + S1 + S2** (2026-05-07). Hasil + analisis komparatif di `src/pseudo_labelling/SRL-NER/done_running/` (file `analisis_skenario_srlner.md` + notebook `compare_scenarios.ipynb`). **Rekomendasi: pakai S1 untuk inference final** (entity-F1=0.908, recall lebih tinggi, EVENT class membaik dari E1). |
| NER Pipeline (LLM-based, Instruction Fine-Tuning + QLoRA) | ❌ **Tidak jadi dipakai** (revisi 2026-05-03). Arsip + `DEPRECATED.md` di `src/pseudo_labelling/LLM-NER/`. |
| Temporal Detection (intra-sentence + urutan bab) | 🔄 **Baru** — perlu deteksi temporal dalam satu kalimat sebelum pembentukan graf |
| Relation Extraction + Pembobotan | ✅ Selesai (897 nodes, 370 edges — weighted, + relasi baru). Perlu re-run setelah temporal detection. |
| Relasi Person-Person (KELUARGA/SAHABAT/MUSUH) | ✅ Selesai (91 KELUARGA, 25 SAHABAT, 10 MUSUH) |
| Relasi Event Kronologis (PRECEDES) | ✅ Selesai (18 relasi PRECEDES antar event) |
| Social Network Analysis | 🔄 Centrality selesai (174 nodes, 1164 edges, 16 komunitas). **Perlu tambah graph-level metrics** (density, clustering coefficient, network size). |
| Uji coba sampling 3–5 event berperiode jauh | 🔄 **Baru** — Perang Badar dkk., amati keterlibatan + graf + analisis |
| Build Knowledge Graph (Neo4j) | ✅ Cypher script diperbarui (`import_sirah.cypher`), tinggal import |

### Catatan progres terakhir (sesi terakhir: 2026-05-07)

#### [2026-05-07] Run 3 Skenario SRL-NER + Analisis Komparatif

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

#### [2026-05-03] Revisi Dosen Putaran 2 (Bu Diana) — `revisi_dosen.md`

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

#### [2026-04-27] Restrukturisasi LLM-NER (asli vs pseudo) + dokumentasi thesis Andrian

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

#### [2026-04-24] Implementasi 4 Revisi Dosen
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

#### [2026-04-16] Catatan sebelumnya
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

### Yang harus dilakukan di sesi berikutnya (catatan 2026-04-16, sudah disuperseded sebagian oleh revisi 2026-05-03)

> ⚠️ Lihat juga **"Yang harus dilakukan di sesi berikutnya"** di section **[2026-05-03] Revisi Dosen Putaran 2** di atas — itu adalah daftar prioritas terbaru.

1. **Run SRL-NER notebook di Colab/Kaggle** (default knobs = Bu Diana, plus fix A-H). Install `seqeval` lebih dulu.
   - Validasi: F1 base vs final (harus naik), per-label F1, `iteration_log.csv` untuk plot
   - Tuning opsional: `MIN_ENTITY_CONF=0.85`, `SAMPLING_RATE=0.5`
   - **TAMBAHAN dari revisi 2026-05-03:** definisikan skenario threshold (fix vs adaptif) + unbalanced handling sebelum run final
2. ~~Run LLM-NER notebook~~ → **Dibatalkan** (revisi 2026-05-03)
3. **Install matplotlib & re-run SNA** — `pip install matplotlib` lalu `python src/analysis/sna_analysis.py` untuk generate `sna_person_network.png`
   - **TAMBAHAN:** perluas dengan graph-level metrics (density, clustering coefficient, ukuran network)
4. **Import Neo4j** — jalankan `import_sirah.cypher` atau `import_to_neo4j.py --uri bolt://localhost:7687`
5. Kalau hasil NER OK → **inferensi model final ke seluruh `sirah_chunks_final.csv`** → re-run Relation Extraction + SNA dengan data baru
   - **TAMBAHAN:** Relation Extraction perlu temporal-aware (intra-sentence ordering) sebelum re-run

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
