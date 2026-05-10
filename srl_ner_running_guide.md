# SRL-NER Running Guide — E1 Baseline + S1 Class Weight + S2 Adaptif

**Tanggal:** 2026-05-04
**Tujuan:** panduan step-by-step untuk menjalankan 3 eksperimen yang sudah ACC Bu Diana (lihat `bimbingan.md`).
**Durasi total:** ~10–13 jam wall-clock (4–5 jam coding + 7–8 jam GPU Colab).

---

## ⚙️ Pre-Flight Checklist (sebelum buka Colab)

### 0.1 Akun & resource
- [ ] Akun Google Colab (gratis cukup — tapi **Colab Pro lebih nyaman** karena GPU T4/A100 lebih lama dan tidak putus)
- [ ] Google Drive dengan **minimal 5 GB kosong** (3 model × ~500 MB + dataset + log)
- [ ] (Alternatif) Akun Kaggle — gratis, GPU T4 ×2 dengan kuota 30 jam/minggu

### 0.2 File yang harus diupload ke Drive

Buat folder `MyDrive/TA-Sirah/` di Google Drive, lalu upload **3 file** dari disk lokal:

| Source (lokal) | Target (Drive) |
|---|---|
| `data/result/pseudo-labelling/SRL-NER/train.csv` | `MyDrive/TA-Sirah/train.csv` |
| `data/result/pseudo-labelling/SRL-NER/test.csv` | `MyDrive/TA-Sirah/test.csv` |
| `data/result/pseudo-labelling/SRL-NER/unlabelled.csv` | `MyDrive/TA-Sirah/unlabelled.csv` |

> **Tips:** kalau pakai Kaggle, buat **Dataset baru** dengan nama `sirah-ner-srl` berisi 3 file di atas, lalu attach ke notebook.

### 0.3 File notebook
- [ ] **Untuk Colab:** upload `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_colab.ipynb` ke Colab (atau buka via "Open notebook" → "Upload")
- [ ] **Untuk Kaggle:** upload `srl_ner_sirah_0.9_kaggle.ipynb` ke Kaggle Notebook

### 0.4 Verifikasi GPU di Colab
Setelah notebook terbuka:
- Menu `Runtime` → `Change runtime type` → **GPU** (T4 atau A100)
- Jalankan cell verifikasi:
```python
import torch
print(torch.cuda.is_available())   # True
print(torch.cuda.get_device_name())  # "Tesla T4" atau "NVIDIA A100"
```

---

# 📊 Fase 1 — E1 Baseline (Replikasi Paper Ariyanto)

**Tujuan:** validasi pipeline Sirah, target F1 ≈ 0.863.
**Coding effort:** **0 jam** (notebook sudah siap)
**GPU time:** ~2–3 jam (6 iterasi × ~25 menit)

## 1.1 Langkah eksekusi

1. Buka `srl_ner_sirah_0.9_colab.ipynb` di Colab
2. Pastikan GPU aktif (Step 0.4)
3. **Run all cells** — `Runtime` → `Run all`
4. Saat cell 11 (`drive.mount`) → klik link, otentikasi Google
5. Tinggal tunggu — log akan terlihat di tiap cell

## 1.2 Apa yang harus dipantau

Selama loop iterasi (cell 22), perhatikan output:
```
[iter 1] above threshold: 850 sentences
[iter 2] above threshold: 920 sentences
[iter 3] above threshold: 980 sentences
...
```

**Tanda sehat:**
- `n_above` naik atau stabil (bukan turun drastis)
- F1 di tabel epoch terakhir > 0.7 (idealnya mendekati 0.86)

**Tanda bermasalah:**
- `n_above < 100` di iter 1 → seed terlalu kecil atau model tidak belajar
- F1 turun antar iterasi → pseudo-label memperkenalkan noise
- Loss = `NaN` → cek label di train.csv (lihat troubleshooting §6)

## 1.3 Output yang harus dikumpulkan untuk E1

Setelah notebook selesai, **download file berikut dari Drive** ke folder lokal `data/result/pseudo-labelling/SRL-NER/runs/E1_baseline/`:

| File di Drive | Apa isinya |
|---|---|
| `output/evaluation/iteration_log.csv` | F1 per iterasi (untuk plot) |
| `output/evaluation/bert-only-sirah-ner-iterative-6-correct.xlsx` | Token test set yang benar |
| `output/evaluation/bert-only-sirah-ner-iterative-6-incorrect.xlsx` | Token test set yang salah |
| `output/evaluation/bert-only-sirah-ner-confidence-0.9-misclassified.xlsx` | Confusion analysis |

**Catat angka berikut di buku catatan / spreadsheet:**

| Metrik | E1 |
|---|---:|
| F1 overall (weighted, base model) | ___ |
| F1 overall (weighted, iter-6 final) | ___ |
| F1 entity-level (seqeval, iter-6) | ___ |
| F1 per-label PERSON | ___ |
| F1 per-label LOCATION | ___ |
| F1 per-label TIME | ___ |
| F1 per-label EVENT | ___ |
| Total pseudo-label terkumpul (semua iter) | ___ |

## 1.4 Decision point setelah E1

- ✅ **F1 overall ≥ 0.80**: pipeline OK → lanjut ke Fase 2
- ⚠️ **F1 antara 0.65–0.80**: pipeline bisa jalan, tapi mungkin perlu tuning. Lanjut Fase 2 dulu, lihat apakah class weight bantu
- ❌ **F1 < 0.65**: pipeline bermasalah → **STOP**, debug dulu sebelum lanjut S1/S2 (cek label konsistensi di `train.csv`)

---

# 🎚️ Fase 2 — S1 Class Weight (Fix Threshold + Inverse Frequency)

**Tujuan:** uji apakah class weight memperbaiki F1 EVENT (yang minoritas ekstrem).
**Coding effort:** ~2 jam
**GPU time:** ~2–3 jam

## 2.1 Persiapan: simpan notebook E1 sebagai S1

Di Colab:
- `File` → `Save a copy in Drive` → namanya `srl_ner_sirah_S1_classweight.ipynb`
- Buka copy yang baru disimpan

## 2.2 Modifikasi #1 — Tambah cell baru SETELAH cell 14 (label2id)

**Posisi:** sisipkan cell baru di antara cell 14 dan cell 15.

```python
# === [S1] Compute class weights (inverse frequency) ===
import torch
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

# Hitung distribusi label di seed (df_train)
labels_in_train = df_train["label"].dropna().tolist()
label_counts = Counter(labels_in_train)
print("Distribusi label train:")
for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
    pct = 100 * cnt / sum(label_counts.values())
    print(f"  {lbl:<14} {cnt:>6}  {pct:>5.2f}%")

# Hitung class weight inverse frequency (dengan ID urutan label_list)
classes_arr = sorted(label_counts.keys(), key=lambda x: label2id[x])
y_arr = labels_in_train
weights_np = compute_class_weight('balanced', classes=classes_arr, y=y_arr)

# Optional: clipping untuk stabilitas (bobot ekstrem 155× bisa bikin loss tidak stabil)
WEIGHT_CLIP_MAX = 50.0
weights_np_clipped = [min(w, WEIGHT_CLIP_MAX) for w in weights_np]

# Tensor untuk pass ke loss function
class_weights_tensor = torch.tensor(weights_np_clipped, dtype=torch.float)
print("\nClass weights (clipped to max 50):")
for lbl, w in zip(classes_arr, weights_np_clipped):
    print(f"  {lbl:<14} {w:>7.2f}")
```

> **Cek output:** `O` harus dapat bobot terkecil (~0.12), `B_EVENT/I_EVENT/I_LOCATION` harus dapat bobot tertinggi (~50 setelah clipping). Kalau terbalik → ada bug di mapping `label2id`.

## 2.3 Modifikasi #2 — Ganti `Trainer` jadi `WeightedTrainer` di cell 19

**Posisi:** cell yang berisi definisi `train_model()`. Tambah class baru DI ATAS fungsi `train_model`, lalu ubah baris `Trainer(...)` jadi `WeightedTrainer(...)`.

```python
# === [S1] WeightedTrainer subclass ===
class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self._class_weights is not None:
            weight = self._class_weights.to(logits.device)
        else:
            weight = None

        loss_fct = torch.nn.CrossEntropyLoss(weight=weight, ignore_index=-100)
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss
```

Lalu **dalam fungsi `train_model()`**, ganti baris:
```python
trainer = Trainer(
    model_init=model_init,
    args=training_args,
    ...
)
```
menjadi:
```python
trainer = WeightedTrainer(
    model_init=model_init,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    class_weights=class_weights_tensor,    # ← TAMBAHAN S1
)
```

## 2.4 Run S1

- `Runtime` → `Run all`
- Tunggu ~2–3 jam
- Pantau hal sama seperti E1 (n_above per iter, F1 progress)

## 2.5 Output S1

Download ke `data/result/pseudo-labelling/SRL-NER/runs/S1_classweight/` (struktur sama dengan E1).

**Catat angka:**

| Metrik | S1 |
|---|---:|
| F1 overall (weighted) | ___ |
| F1 entity-level (seqeval) | ___ |
| F1 per-label EVENT (kunci!) | ___ |

**Bandingkan dengan E1:**
- ✅ F1 EVENT naik ≥ 5% absolut → class weight berhasil
- ⚠️ F1 overall turun > 3% → class weight overcompensate, perlu turunkan `WEIGHT_CLIP_MAX` ke 30 atau 20
- ❌ F1 EVENT tidak naik → mungkin masalah lain (data EVENT memang sangat minim, tidak bisa diselesaikan dengan class weight saja)

---

# 🎚️ Fase 3 — S2 Adaptif Threshold + Class Weight

**Tujuan:** uji apakah adaptive threshold tambah value di atas class weight.
**Coding effort:** ~1 jam tambahan dari S1
**GPU time:** ~2–3 jam

## 3.1 Persiapan: simpan S1 sebagai S2

Di Colab:
- `File` → `Save a copy in Drive` (dari notebook S1) → namanya `srl_ner_sirah_S2_adaptive.ipynb`

## 3.2 Modifikasi #1 — Tambah hyperparameter di cell 22 (knob cell)

**Posisi:** ganti bagian deklarasi knob di cell 22, dari:
```python
N_ITERATIONS    = 6
THRESHOLD       = 0.9
SAMPLING_RATE   = 1.0
MIN_ENTITY_CONF = None
MIN_NEW_SAMPLES = 0
AGG_STRATEGY    = "simple"
```

menjadi:
```python
# === [S2] Hyperparameter ===
N_ITERATIONS    = 6
THRESHOLD       = 0.9         # tetap dipakai sebagai THRESHOLD_INIT
SAMPLING_RATE   = 1.0
MIN_ENTITY_CONF = None
MIN_NEW_SAMPLES = 0
AGG_STRATEGY    = "simple"

# Adaptive threshold (dropping-only)
THRESHOLD_INIT     = 0.9
THRESHOLD_MIN      = 0.7
THRESHOLD_STEP     = 0.05
TARGET_MIN_SAMPLES = 200      # minimal kalimat baru per iterasi
```

## 3.3 Modifikasi #2 — Ganti loop iterasi di cell 22

**Posisi:** cari blok `for i in range(1, N_ITERATIONS + 1):` di cell 22. Ganti seluruh isi for-loop menjadi:

```python
for i in range(1, N_ITERATIONS + 1):
    prev_model_path = os.path.join(model_dir, current_model_name)
    prefix = "bert-only-sirah-ner" if i == 1 else f"bert-only-sirah-ner-iterative-{i}"

    # === [S2] Adaptive threshold dropping-only ===
    threshold = THRESHOLD_INIT
    above_df = filter_threshold(
        model_path=prev_model_path,
        df=current_unlabelled,
        threshold=threshold,
        output_dir=eval_dir,
        output_filename_prefix=prefix,
        sampling_rate=SAMPLING_RATE,
        min_entity_confidence=MIN_ENTITY_CONF,
        aggregation_strategy=AGG_STRATEGY,
    )
    n_above = int(above_df["text_id"].nunique()) if len(above_df) else 0

    while n_above < TARGET_MIN_SAMPLES and threshold > THRESHOLD_MIN:
        threshold = round(threshold - THRESHOLD_STEP, 2)
        print(f"[iter {i}] dropping threshold to {threshold}")
        above_df = filter_threshold(
            model_path=prev_model_path,
            df=current_unlabelled,
            threshold=threshold,
            output_dir=eval_dir,
            output_filename_prefix=f"{prefix}-t{threshold}",   # nama file beda biar tidak overwrite
            sampling_rate=SAMPLING_RATE,
            min_entity_confidence=MIN_ENTITY_CONF,
            aggregation_strategy=AGG_STRATEGY,
        )
        n_above = int(above_df["text_id"].nunique()) if len(above_df) else 0

    print(f"[iter {i}] threshold={threshold}, above: {n_above} sentences")
    iter_log.append({
        "iter": i,
        "threshold_used": threshold,    # ← TAMBAHAN S2: log threshold dinamis
        "n_above": n_above,
    })

    if n_above < TARGET_MIN_SAMPLES:
        print(f"[iter {i}] adaptive mentok di {threshold}, stop")
        break

    if MIN_NEW_SAMPLES > 0 and n_above < MIN_NEW_SAMPLES:
        print(f"[iter {i}] early-stop: {n_above} < MIN_NEW_SAMPLES={MIN_NEW_SAMPLES}")
        break

    pseudo_dfs.append(above_df)

    if i < N_ITERATIONS:
        new_model_name = f"{experiment_name}-S2-iteration-{i+1}"
        combined = pd.concat([df_train] + pseudo_dfs, ignore_index=True)
        train_val_iter = df_to_dataset_for_model(combined, val_text_ids=VAL_TEXT_IDS)
        print(train_val_iter)

        train_model(
            model_name=prev_model_path,
            train_dataset=train_val_iter["train"],
            val_dataset=train_val_iter["validation"],
            model_output_path=os.path.join(model_dir, new_model_name),
        )
        current_model_name = new_model_name

        below_path = os.path.join(eval_dir, f"{prefix}-below-{threshold}.xlsx")
        if not os.path.exists(below_path):
            # Adaptive jalan, file below dipakai dari run terakhir
            below_path = os.path.join(eval_dir, f"{prefix}-t{threshold}-below-{threshold}.xlsx")
        current_unlabelled = reconstruct_unlabelled_from_below(below_path)
```

> **Catatan:** S2 mewarisi `WeightedTrainer` dari S1, jadi class weight tetap aktif. Kalau Bu Diana minta versi S2 tanpa class weight, ganti `WeightedTrainer` balik ke `Trainer` di `train_model()`.

## 3.4 Run S2

Sama seperti S1: `Runtime` → `Run all` → tunggu ~2–3 jam.

## 3.5 Output S2

Download ke `data/result/pseudo-labelling/SRL-NER/runs/S2_adaptive_cw/`.

**Catat angka:**

| Metrik | S2 |
|---|---:|
| F1 overall (weighted) | ___ |
| F1 entity-level (seqeval) | ___ |
| F1 per-label EVENT | ___ |
| Threshold tiap iterasi | iter 1: ___, iter 2: ___, ... |

**Bandingkan dengan S1:**
- ✅ F1 naik DAN n_above > S1 → adaptive berhasil mengatasi cold-start
- ⚠️ F1 sama dengan S1 → adaptive tidak diperlukan untuk Sirah (threshold 0.9 sudah OK)
- ❌ F1 turun → adaptive masuk ke threshold rendah terlalu sering, noise masuk training

---

# 📈 Fase 4 — Tabel Hasil Final & Analisis

## 4.1 Tabel utama untuk Bab 4 laporan

| Eksperimen | F1 Overall | F1 PERSON | F1 LOCATION | F1 TIME | F1 EVENT | F1 (seqeval) |
|---|---:|---:|---:|---:|---:|---:|
| **E1 Baseline** | ___ | ___ | ___ | ___ | ___ | ___ |
| **S1 Class Weight** | ___ | ___ | ___ | ___ | ___ | ___ |
| **S2 Adaptif + CW** | ___ | ___ | ___ | ___ | ___ | ___ |

## 4.2 Plot yang harus dihasilkan

1. **Line chart: F1 vs iterasi** (3 garis untuk E1/S1/S2 di 1 plot)
2. **Line chart: n_above vs iterasi** (3 garis)
3. **Bar chart: F1 per-label E1 vs S1 vs S2** (4 grup label × 3 bar)
4. **Khusus S2: Line chart threshold dinamis vs iterasi** (tunjukkan kapan dropping terjadi)

## 4.3 Decision: pipeline final pemenang

Setelah membandingkan, pilih satu eksperimen sebagai pemenang untuk **inferensi seluruh `sirah_chunks_final.csv`** → ini akan jadi input untuk Relation Extraction & SNA.

Kriteria pemilihan:
- Prioritas utama: **F1 EVENT** (karena penting untuk graf kronologis)
- Tie-breaker: F1 overall + stabilitas (n_above tidak fluktuatif)

---

# 🛠️ Troubleshooting

## 6.1 Error & solusi cepat

| Error | Penyebab | Fix |
|---|---|---|
| `CUDA out of memory` | Batch terlalu besar di Colab GPU | Turunkan `per_device_train_batch_size` ke 8 di cell 19 |
| `FileNotFoundError: train.csv` | File belum ter-upload ke Drive | Cek path `/content/drive/MyDrive/TA-Sirah/train.csv` benar |
| `Loss = NaN` setelah pakai class weight | Bobot terlalu ekstrem (155×) | Turunkan `WEIGHT_CLIP_MAX` dari 50 → 20 di cell baru S1 |
| `compute_class_weight: y contains classes not in classes` | Ada label di train tapi tidak di label_list | Cek konsistensi label di `train.csv` |
| Colab disconnect di iter 4 | Free tier 12-jam limit | Pakai Colab Pro, atau split jadi 2 sesi (run 3 iter dulu, save model, lanjut 3 iter) |
| `pseudo_dfs` kosong setelah iter 1 | n_above = 0 | Threshold terlalu tinggi (E1) atau model tidak belajar — cek F1 base model |

## 6.2 Debug n_above = 0 di iter 1

Kalau di E1 iter 1 dapat `n_above = 0`, kemungkinan:
1. Base model tidak belajar (cek F1 epoch terakhir base)
2. `aggregation_strategy="simple"` gagal aggregate sub-word → confidence menjadi tidak masuk akal
3. Threshold 0.9 terlalu tinggi untuk seed kecil

**Fix cepat:** turunkan `THRESHOLD = 0.85` dulu, jalan E1 lagi, lihat n_above. Kalau OK di 0.85, ini sinyal bahwa S2 (adaptif) memang dibutuhkan.

## 6.3 Kapan harus pakai Kaggle (bukan Colab)

- Kalau Colab disconnect berulang (free tier sering kena timeout)
- Kalau butuh GPU lebih lama (Kaggle gratis 30 jam/minggu T4)
- Kalau perlu run paralel — Kaggle bisa run 2 notebook sekaligus

---

# 📋 Checklist Akhir

Setelah ketiga eksperimen selesai:

- [ ] 3 folder run terisi: `runs/E1_baseline/`, `runs/S1_classweight/`, `runs/S2_adaptive_cw/`
- [ ] Tabel F1 ringkas (Fase 4.1) sudah terisi semua sel
- [ ] 4 plot tersimpan di `data/result/pseudo-labelling/SRL-NER/plots/`
- [ ] Pipeline pemenang terpilih
- [ ] `iteration_log.csv` ke-3 sudah disimpan untuk lampiran laporan
- [ ] Best model dari pemenang siap dipakai untuk **inferensi seluruh dataset** → input Relation Extraction

---

# 🎯 Yang Harus Dilakukan SETELAH 3 Eksperimen Selesai

1. **Inferensi model pemenang ke `sirah_chunks_final.csv`** → hasilkan `sirah_chunks_NER.csv` dengan kolom entitas
2. **Re-run Relation Extraction** dengan data NER baru (input ke `src/relation_extraction/relation_extraction.py`)
3. **Re-run SNA** untuk metrik graph-level (lihat `graf_pengujian_skenario.md`)
4. **Lanjut implementasi temporal intra-sentence** (revisi 2026-05-03 cluster #1)

---

> **Pesan untuk diri sendiri:** Jangan terburu-buru langsung S1/S2 sebelum E1 valid. Kalau E1 F1 < 0.65, **investigasi seed quality dulu** (cek `sirah_prelabelled.csv` konsistensi label) — jangan tutupi masalah data dengan class weight.
