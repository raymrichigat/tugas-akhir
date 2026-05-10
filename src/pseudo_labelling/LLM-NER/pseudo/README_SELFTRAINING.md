# LLM-NER + Iterative Self-Training (Pseudo-Labelling)

> Extension dari `llm_ner_sirah.py` yang menambahkan **iterative self-training** pada data unlabelled.
> Ini adalah **kontribusi tambahan di atas metode Andrian** (Andrian sendiri tidak pakai self-training).

File: `llm_ner_sirah_selftraining.py`

---

## Konsep

Berbeda dari Andrian yang pakai **data augmentation** (sintetis dari LLM eksternal seperti GPT-4o Mini), pendekatan ini pakai **self-training**: model LLM-NER itu sendiri yang melabeli data unlabelled untuk memperbanyak training set.

```
Iter 0:  Train SahabatAI di seed (train.csv) → eval baseline F1
                              ↓
Iter 1:  Inference ke unlabelled → ambil prediksi + confidence
            ↓
         Filter: confidence ≥ 0.85, ambil top 50%
            ↓
         Append ke train → re-train
            ↓
         Eval → catat metrik
                              ↓
Iter N:  ulang sampai konvergen / unlabelled habis / hit max iter
```

---

## Cara Pakai

### Opsi 1: Jalankan via .ipynb (paling mudah)
- **Colab**: Upload `pseudo/llm_ner_sirah_colab.ipynb` ke Colab, taruh data CSV di `MyDrive/TA-Sirah/data/`, Run All.
- **Kaggle**: Upload `pseudo/llm_ner_sirah_kaggle.ipynb` ke Kaggle, buat Dataset `sirah-ner-llm` berisi 3 CSV, Run All.

Notebook ini **standalone** (semua fungsi inline) — tidak perlu upload .py file lain.

### Opsi 2: Jalankan via .py
```bash
cd src/pseudo_labelling/LLM-NER/pseudo
python llm_ner_sirah_selftraining.py
```

Butuh `pseudo/llm_ner_sirah.py` di folder yang sama (sudah ada copy untuk import). Kalau di Colab/Kaggle, upload kedua file:
1. `llm_ner_sirah.py`
2. `llm_ner_sirah_selftraining.py`

Lalu override `BASE_DIR` di `llm_ner_sirah.py` ke path Colab/Kaggle.

> ⚠️ **Tidak realistis di GPU lokal**. Butuh GPU 40 GB+ VRAM. Jalankan di Colab/Kaggle.

---

## Hyperparameter Tunable

| Param | Default | Arti |
|---|---|---|
| `MAX_ITERATIONS` | 5 | Batas iterasi (selain stop condition lain) |
| `MIN_CONFIDENCE` | 0.85 | Threshold confidence per kalimat (0.0–1.0) |
| `SAMPLING_RATE` | 0.5 | Top-K% kalimat yang lolos filter (anti-noise) |
| `MIN_NEW_SAMPLES` | 50 | Stop kalau filter < ini (tidak cukup data baru) |
| `MIN_F1_DELTA` | 0.01 | Stop kalau peningkatan val F1 < ini (konvergen) |
| `EPOCHS_PER_ITER` | 10 | Epoch per iterasi (lebih kecil dari 30 baseline) |

### Tuning suggestions
- **`MIN_CONFIDENCE` lebih tinggi (0.90)** → pseudo-label lebih bersih tapi sedikit, butuh lebih banyak iter.
- **`SAMPLING_RATE` lebih kecil (0.3)** → konservatif, kurangi error compounding.
- **`EPOCHS_PER_ITER` lebih besar (20)** → convergence per iter lebih bagus, tapi lebih lambat.

---

## Confidence Scoring

LLM generative tidak punya softmax probability per token seperti BERT, tapi kita bisa hitung **average log-probability dari token yang di-generate**:

```
base_conf = exp(mean(log_prob_per_generated_token))
retry_penalty = 0.7 ^ (retries - 1)        # makin sering retry, makin rendah
fallback_penalty = 0.5 if needed_padding   # kalau butuh padding/truncate
final_conf = base_conf × retry_penalty × fallback_penalty
```

Kalau `output_scores=True` tidak didukung backend (mis. unsloth path tertentu), fall back ke `base_conf = 0.95` lalu retry penalty yang menentukan.

---

## Output

Folder `data/result/pseudo-labelling/LLM-NER/`:

| File | Isi |
|---|---|
| `iteration_log.csv` | Metrik per iterasi (val_f1, test_f1, n_pseudo_added, dll) |
| `train_iter{N}.csv` | Snapshot training set setelah iter N (seed + pseudo) |
| `llm_ner_predictions_iter{N}.csv` | Prediksi test set per iter (untuk debug) |

### Contoh `iteration_log.csv`
```csv
iteration,train_size,remaining_unlabelled,val_f1,val_precision,val_recall,test_f1,test_precision,test_recall,new_pseudo_added
0,1200,4800,0.7234,0.7156,0.7314,0.7198,0.7102,0.7297,1200
1,2400,3600,0.7512,0.7445,0.7580,0.7456,0.7389,0.7524,1100
2,3500,2500,0.7689,0.7621,0.7758,0.7634,0.7567,0.7702,890
...
```

---

## Stop Conditions (mana yang trigger duluan)

1. **Konvergen**: `val_f1 - prev_val_f1 < MIN_F1_DELTA` → model tidak belajar dari pseudo-label baru
2. **Unlabelled habis**: semua data sudah dilabeli atau diserap
3. **New samples sedikit**: `n_new < MIN_NEW_SAMPLES` → model tidak lagi confident pada sisa unlabelled
4. **Hit max iter**: `iter == MAX_ITERATIONS` → safety net

---

## Estimasi Waktu

Asumsi GPU T4 16GB di Colab Free:
- Per iterasi: ~45 menit (10 epoch training + inference val/test/unlabelled)
- 5 iterasi: ~4 jam total
- Bisa lebih lama kalau unlabelled.csv besar (>5000 sentences)

Asumsi GPU A100 40GB di Colab Pro:
- Per iterasi: ~15 menit
- 5 iterasi: ~1.5 jam

---

## Catatan untuk Skripsi

### Yang bisa diklaim sebagai kontribusi
1. **Adaptasi metode Andrian ke domain narasi sejarah Islam** (Sirah Nabawiyah)
2. **Penambahan iterative self-training** di atas pipeline LLM-NER (Andrian tidak pakai)
3. **Confidence scoring untuk LLM generative** (logprob averaging + retry penalty)

### Risiko self-training
- **Error compounding**: pseudo-label yang salah di iter 1 akan dipakai untuk train iter 2
- Mitigasi: confidence threshold tinggi (0.85), sampling rate < 1.0 (0.5), early stop pada konvergen
- Plot `iteration_log.csv` untuk monitor: kalau test_f1 mulai turun = stop manual

### Yang sebaiknya dilaporkan di Bab 4 (Evaluasi)
- Tabel iteration log (val_f1 + test_f1 per iter)
- Grafik F1 vs iteration
- Confusion matrix iter 0 (baseline) vs iter terakhir
- Per-entity F1: PERSON, EVENT, LOCATION, TIME — apakah semua naik atau ada yang stagnan/turun

---

## Hubungan dengan File Lain

```
src/pseudo_labelling/LLM-NER/
├── PENJELASAN_THESIS_ANDRIAN.md          ← Referensi: metodologi Andrian
├── asli/                                  ← Penerapan asli Andrian (baseline)
│   ├── _build_notebooks.py
│   ├── llm_ner_sirah.py                   ← supervised fine-tuning (single-shot)
│   ├── llm_ner_sirah_colab.ipynb
│   └── llm_ner_sirah_kaggle.ipynb
└── pseudo/                                ← Versi TA: + iterative self-training
    ├── _build_notebooks.py
    ├── llm_ner_sirah.py                   ← copy dari asli/ (untuk import)
    ├── llm_ner_sirah_selftraining.py      ← ★ kontribusi self-training
    ├── llm_ner_sirah_colab.ipynb          ← Colab dengan iter loop
    ├── llm_ner_sirah_kaggle.ipynb         ← Kaggle dengan iter loop
    └── README_SELFTRAINING.md             ← (file ini)
```

`pseudo/llm_ner_sirah_selftraining.py` **import** dari `pseudo/llm_ner_sirah.py` (reuse setup_model, train_model, prepare_instruction_data, evaluate_model). Modifikasi pada `pseudo/llm_ner_sirah.py` akan otomatis affect self-training.

> **Penting**: `asli/llm_ner_sirah.py` dan `pseudo/llm_ner_sirah.py` adalah copy yang sama. Kalau Anda modifikasi salah satu (misal tweak ALPACA_PROMPT), sinkronkan manual atau hanya modifikasi versi pseudo (yang dipakai untuk TA).
