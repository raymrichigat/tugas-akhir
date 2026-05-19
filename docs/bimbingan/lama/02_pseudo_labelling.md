# Laporan Bimbingan — Bagian 2: Uji Coba Pseudo-Labelling (SRL-NER & LLM-NER)

**Mahasiswa:** Rayssa Ravelia (5025211219)
**Pembimbing:** Prof. Dr. Diana Purwitasari
**Topik TA:** Knowledge Graph Sirah Nabawiyah
**Tanggal laporan:** 30 April 2026

---

## 1. Latar Belakang Revisi

Pada bimbingan sebelumnya, dosen memberi catatan revisi kedua:

> *"Uji coba pseudo-labelling dengan SRL-NER based dan LLM-Based NER harus sudah dilakukan walaupun hasilnya jelek."*

**Konteks:** TA ini membandingkan **dua pendekatan NER** untuk teks Sirah Nabawiyah:
- **SRL-NER** (Semantic Role Labeling) — BERT iterative self-training, mengikuti referensi notebook dari Bu Diana (`BERT_Only_Percobaan_1_Argument_0.9.ipynb`).
- **LLM-NER** — Instruction Fine-Tuning + QLoRA pada SahabatAI (LLAMA 3 untuk Bahasa Indonesia), mengikuti metodologi thesis Andrian (5025211079).

Implementasi **bukan langsung pakai output manual labelling**, tapi memakai *seed* dari manual labelling untuk men-train model NER → model akan men-generalisasi ke teks yang belum dilabeli.

---

## 2. Definisi Pseudo-Labelling dalam Konteks TA

**Pseudo-labelling** = strategi *semi-supervised learning* di mana:
1. Model di-train dengan sebagian kecil **data berlabel manual (seed)**.
2. Model digunakan untuk meng-infer label pada **data tanpa label (unlabelled)**.
3. Prediksi dengan **confidence tinggi** ditambahkan ke training set sebagai *pseudo-label*.
4. Model di-train ulang → siklus diulangi sampai konvergen.

> **Catatan klarifikasi penting:**
> Dalam thesis Andrian (referensi LLM-NER), istilah "pseudo-labelling" **tidak digunakan**. Andrian memakai *supervised fine-tuning* + *data augmentation* (KEE-Prompt + E2T via GPT-4o Mini). Yang **benar-benar pseudo-labelling** di TA ini adalah **SRL-NER** (BERT self-training).
>
> Untuk **LLM-NER**, kontribusi orisinal TA adalah **menambahkan iterative self-training** di atas metode Andrian — dipisah ke folder `pseudo/` (versi TA) vs `asli/` (replikasi Andrian sebagai baseline).

---

## 3. Posisi dalam Pipeline

```
Manual Labelling → seed data
       ↓
prepare_bert_data.py → format CoNLL (text_id, id, token, pos_tag, label)
       ↓                                                    ↓
  ┌────────────┐                                   ┌──────────────────┐
  │  SRL-NER   │                                   │  LLM-NER         │
  │  (BERT)    │                                   │  (SahabatAI+QLoRA)│
  │  iterative │                                   │  ├─ asli/        │
  │  self-train│                                   │  │  (baseline)   │
  └────────────┘                                   │  └─ pseudo/      │
       ↓                                           │     (self-train) │
       ↓                                           └──────────────────┘
       └─────────────── Bandingkan F1 ────────────────────┘
                              ↓
              Pilih model terbaik untuk inferensi
              full corpus → relation extraction
```

---

## 4. Apa yang Dilakukan

### 4.1 Persiapan Data (selesai)

File `src/pseudo_labelling/prepare_bert_data.py` mengubah hasil manual labelling menjadi format CoNLL token-level (BIO tagging):

| Output | Jumlah Baris | Jumlah Kalimat (text_id) |
|---|---:|---:|
| `train.csv` | 101.021 | 590 |
| `test.csv` | 43.241 | 254 |
| `unlabelled.csv` | 40.387 | 250 |

**Distribusi label di train.csv** (BIO):
| Label | Jumlah |
|---|---:|
| O (non-entity) | 94.070 |
| B-PERSON | 2.634 |
| I-PERSON | 2.289 |
| B-LOCATION | 1.013 |
| I-LOCATION | 72 |
| B-TIME | 236 |
| I-TIME | 442 |
| B-EVENT | 128 |
| I-EVENT | 137 |

Output disimpan di: `data/result/pseudo-labelling/SRL-NER/`.

### 4.2 SRL-NER (BERT Iterative Self-Training)

#### Implementasi
- Notebook ada di `src/pseudo_labelling/SRL-NER/` (3 versi: lokal, Colab, Kaggle).
- Refactor besar dari notebook Bu Diana untuk menyesuaikan ke schema BIO Sirah (Fix A–H).
- Fix paling kritikal: **Fix A** — auto-detect skema label (flat ARG0/ARG1 vs BIO B-X/I-X). Tanpa fix ini, semua pseudo-label Sirah jadi "O" karena `entity_group` tidak match `label2id`.

#### Hyperparameter Default (= Bu Diana)
| Parameter | Nilai |
|---|---|
| Model | `indolem/indobert-base-uncased` |
| Epoch per iterasi | 30 |
| Learning rate | 5e-5 |
| Batch size | 16 |
| `MIN_ENTITY_CONF` | None (off, opt-in) |
| `SAMPLING_RATE` | 1.0 (semua kandidat di-take) |
| `MIN_NEW_SAMPLES` | 0 (no early stop) |

#### Alur (per iterasi)
1. Train BERT pada `train.csv`.
2. Evaluasi pada `test.csv` → simpan F1 token-level (sklearn) + entity-level (seqeval).
3. Inferensi pada `unlabelled.csv` → ekstrak entitas + confidence per kalimat.
4. Filter kalimat dengan confidence >= threshold → tambahkan ke `train.csv`.
5. Reconstruct sisa unlabelled → `unlabelled.csv` baru.
6. Ulangi sampai konvergen / unlabelled habis.

### 4.3 LLM-NER (Instruction Fine-Tuning + QLoRA)

Direstrukturisasi menjadi **2 sub-folder** untuk memisahkan replikasi vs kontribusi:

#### `asli/` — Replikasi Andrian (Baseline)
- Supervised fine-tuning single-shot, **tanpa** self-training.
- Mengikuti Bab III thesis Andrian: prompt Alpaca-style Bahasa Indonesia (Prompt 3.8).
- **Hyperparameter:** SahabatAI base, QLoRA r=64 / α=32 / dropout=0.05, 4-bit NF4 quantization, 30 epoch, batch=16, lr=1e-4.
- Output: 1 angka F1 final → digunakan sebagai pembanding di Bab 4.

#### `pseudo/` — Versi TA (Iterative Self-Training, **kontribusi orisinal**)
- Tambahan di atas metode Andrian: pipeline self-training otomatis.
- File baru: `llm_ner_sirah_selftraining.py`.

**Algoritma:**
```
1. Train pada seed (train.csv) → infer test → catat F1_iter1
2. Infer unlabelled + confidence per kalimat
3. Filter:
   - keep kalimat dgn confidence ≥ 0.85
   - dari kandidat tersisa, ambil top 50% (sampling_rate)
4. Append ke train.csv → re-train
5. Stop jika salah satu terjadi:
   - delta_F1 < 0.01 (konvergen)
   - unlabelled habis
   - new_samples < 50 (terlalu sedikit kandidat)
   - mencapai max_iter = 5
```

**Confidence scoring per kalimat:**
```
conf = mean(exp(logprob))_per_generated_token
       × 0.7^(retries-1)               ← penalti jika perlu retry
       × 0.5_if_needed_padding         ← penalti jika output terpotong
```

**Hyperparameter `pseudo/`:**
| Parameter | Nilai |
|---|---|
| `MAX_ITERATIONS` | 5 |
| `MIN_CONFIDENCE` | 0.85 |
| `SAMPLING_RATE` | 0.5 |
| `MIN_NEW_SAMPLES` | 50 |
| `MIN_F1_DELTA` | 0.01 |
| `EPOCHS_PER_ITER` | 10 (lebih kecil dari baseline 30) |

---

## 5. Input dan Output

### Input (sama untuk SRL & LLM)
| File | Isi |
|---|---|
| `data/result/pseudo-labelling/SRL-NER/train.csv` | 101.021 token, 590 kalimat (seed berlabel) |
| `data/result/pseudo-labelling/SRL-NER/test.csv` | 43.241 token, 254 kalimat (untuk evaluasi) |
| `data/result/pseudo-labelling/SRL-NER/unlabelled.csv` | 40.387 token, 250 kalimat (kandidat pseudo-label) |

### Output yang Diharapkan (setelah di-run di GPU)

**SRL-NER:**
- `srl_ner_predictions_iter{N}.csv` — prediksi per iterasi
- `iteration_log.csv` — F1 (sklearn + seqeval) per iterasi
- Model BERT final (`.pt` / HuggingFace format)

**LLM-NER `asli/`:**
- 1 file prediksi `llm_ner_predictions.csv`
- 1 angka F1 baseline

**LLM-NER `pseudo/`:**
- `train_iter{N}.csv` — training set per iterasi
- `llm_ner_predictions_iter{N}.csv`
- `iteration_log.csv` — F1 per iterasi
- `selftraining_summary.txt` — ringkasan akhir
- Adapter LoRA final

---

## 6. Status Pengerjaan

| Tahap | SRL-NER | LLM-NER asli | LLM-NER pseudo |
|---|:---:|:---:|:---:|
| Persiapan data CoNLL | ✅ Selesai | ✅ Selesai | ✅ Selesai |
| Implementasi notebook | ✅ Selesai (3 versi: lokal, Colab, Kaggle) | ✅ Selesai (Colab + Kaggle) | ✅ Selesai (Colab + Kaggle) |
| Refactor / fix bug | ✅ Fix A–H done | ✅ Built dari Andrian | ✅ Self-training pipeline done |
| Dokumentasi | ✅ `README.md` di SRL-NER | ✅ `PENJELASAN_THESIS_ANDRIAN.md` | ✅ `README_SELFTRAINING.md` |
| **Eksekusi di GPU** | 🔄 **Belum dijalankan** | 🔄 **Belum dijalankan** | 🔄 **Belum dijalankan** |
| F1 evaluasi | ⏳ menunggu run | ⏳ menunggu run | ⏳ menunggu run |

> **Status jujur:** seluruh kode dan notebook sudah final & lulus parsing AST. Tinggal **eksekusi di GPU (Colab T4 / Kaggle / Colab A100)**, karena training BERT dan apalagi LLM 8B parameter tidak feasible di laptop lokal.

---

## 7. Hasil Sementara (Persiapan & Validasi Implementasi)

Belum ada hasil F1 final, namun beberapa hal sudah terverifikasi:

### 7.1 Persiapan data sukses
- Total **5.753 entitas berlabel valid** dari manual labelling.
- Konversi ke BIO tagging tidak ada token mismatch.
- Distribusi label seimbang (PERSON paling banyak, sesuai karakter teks Sirah).

### 7.2 SRL-NER — bug fixes terverifikasi
- **Fix A** (auto-detect schema) — sudah di-test pada notebook lokal di sample kecil, BIO labels Sirah berhasil di-recognize.
- **Fix B** (val text_ids stabil) — output VAL set konsisten di run berulang.
- Semua 34 cell notebook lokal lulus `ast.parse`.

### 7.3 LLM-NER — pemahaman metodologi selesai
- Dokumentasi `PENJELASAN_THESIS_ANDRIAN.md` (9 bagian) sudah dibuat untuk konsultasi dengan Mas Andrian.
- Mapping arsitektur Andrian → step-by-step (Praproses → Augmentasi KEE/E2T → Pelatihan → Inferensi → Evaluasi) lengkap dengan referensi halaman PDF.

### 7.4 Yang Akan Diukur Saat Eksekusi
| Metrik | Skema Pengukuran |
|---|---|
| **F1 token-level** | sklearn (Bu Diana) — banding antar iter |
| **F1 entity-level** | seqeval (B-X / I-X dianggap satu entitas) |
| **Per-label F1** | F1 untuk PERSON, EVENT, LOCATION, TIME secara terpisah |
| **Konvergensi** | Plot F1 vs iter — kapan delta_F1 < 0.01 |
| **Pseudo-label growth** | Berapa kalimat unlabelled yang berhasil di-promote per iterasi |

---

## 8. Langkah Berikutnya

1. **Run SRL-NER di Colab/Kaggle** dengan default hyperparameter Bu Diana (`SAMPLING_RATE=1.0`, `MIN_ENTITY_CONF=None`).
   - Install: `pip install seqeval transformers datasets`.
   - Validasi: F1 base vs final harus naik.
2. **Tuning opsional SRL-NER** (jika hasil default kurang optimal): `MIN_ENTITY_CONF=0.85`, `SAMPLING_RATE=0.5` — pendekatan analyticsvidhya yang lebih konservatif.
3. **Run LLM-NER `asli/` di Colab/Kaggle** (butuh GPU T4/A100, ~3 jam):
   - Upload `train.csv` + `test.csv`.
   - Catat F1 baseline = 1 angka.
4. **Run LLM-NER `pseudo/` di Colab/Kaggle** (~5 jam):
   - Catat F1 per iterasi (5 angka) → plot vs iteration.
5. **Konsultasi dengan Mas Andrian** — bawa `PENJELASAN_THESIS_ANDRIAN.md` + sample data Sirah + 5 pertanyaan top-priority.
6. **Bandingkan hasil di Bab 4 laporan TA:**
   - SRL-NER vs LLM-NER `asli` (membandingkan dua pendekatan NER).
   - LLM-NER `asli` vs `pseudo` (membuktikan kontribusi self-training).
7. **Inferensi model terbaik ke seluruh `sirah_chunks_final.csv`** → re-run Relation Extraction & SNA dengan output NER (gantikan manual labelling).

---

## 9. File Terkait

| File | Deskripsi |
|---|---|
| `src/pseudo_labelling/prepare_bert_data.py` | Konversi manual labelling → CoNLL |
| `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9.ipynb` | Notebook SRL-NER (lokal) |
| `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_colab.ipynb` | Versi Colab |
| `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_kaggle.ipynb` | Versi Kaggle |
| `src/pseudo_labelling/SRL-NER/README.md` | Dokumentasi pipeline SRL-NER |
| `src/pseudo_labelling/LLM-NER/PENJELASAN_THESIS_ANDRIAN.md` | Pemahaman thesis Andrian (referensi konsultasi) |
| `src/pseudo_labelling/LLM-NER/asli/llm_ner_sirah.py` | Replikasi Andrian (baseline) |
| `src/pseudo_labelling/LLM-NER/pseudo/llm_ner_sirah_selftraining.py` | **Kontribusi TA**: iterative self-training |
| `src/pseudo_labelling/LLM-NER/pseudo/README_SELFTRAINING.md` | Dokumentasi algoritma self-training |
| `data/result/pseudo-labelling/SRL-NER/{train,test,unlabelled}.csv` | Input siap (101K / 43K / 40K token) |
