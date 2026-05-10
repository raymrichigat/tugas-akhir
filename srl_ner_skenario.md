# Skenario SRL-NER + Referensi — E1/E3/E4

**Tanggal:** 2026-05-03
**Konteks:** Menjawab revisi Bu Diana di `revisi_dosen.md` (poin NER):
> *"SRL NER ini perlu di definisikan skenario nya seperti apa (seperti thresholdnya saja kah atau ada yang lainnya)"*
> *"Untuk perbandingan Threshold bisa digunakan seperti fix threshold atau adaptif (kalau terlalu rendah akan otomatis diturunkan)"*
> *"Kalau unbalanced perlu di handling dan ini ada berbagai macam (definisikan dulu skenario seperti apa, perlu effort nya lebih lagi)"*

Dokumen ini = **bahan diskusi** sebelum implementasi. Setelah disetujui Bu Diana, skenario yang dipilih akan diimplementasikan ke notebook SRL-NER (`src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9*.ipynb`).

> **Ruang lingkup:** TA fokus ke **3 eksperimen (E1, E3, E4)** — kombinasi minimal yang menjawab kedua revisi (threshold + unbalanced) tanpa membengkakkan eksperimen.

---

## 1. Kondisi saat ini (baseline)

**Notebook:** `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9.ipynb` (+ varian Colab/Kaggle)
**Pipeline:** BERT iterative self-training (mengikuti template Bu Diana, dengan Fix A–H untuk Sirah BIO).

### 1.1 Knob yang sudah ada (dari refactor 2026-04-16)

| Knob | Default | Fungsi |
|---|---|---|
| `THRESHOLD` | **0.9** (fix) | Average entity confidence per kalimat ≥ THRESHOLD → masuk pseudo-label |
| `MIN_ENTITY_CONF` | `None` | Reject kalimat kalau ada **satu** entity dgn conf < nilai ini |
| `SAMPLING_RATE` | `1.0` | Pakai top-K% kalimat confidence tertinggi (1.0 = semua above) |
| `MIN_NEW_SAMPLES` | `0` | Early-stop kalau pseudo-label baru < threshold |
| `aggregation_strategy` | `"simple"` | Strategi agregasi sub-token |
| `MAX_ITERATIONS` | (di for-loop) | Jumlah iterasi maksimal |

### 1.2 Distribusi label train (`train.csv`, 101.021 tokens)

| Label | Count | % | Catatan |
|---|---:|---:|---|
| `O` | 94,070 | **93.1%** | Mendominasi |
| B-PERSON | 2,634 | 2.61% | Entitas terbanyak |
| I-PERSON | 2,289 | 2.27% | |
| B-LOCATION | 1,013 | 1.00% | |
| I-TIME | 442 | 0.44% | |
| B-TIME | 236 | 0.23% | |
| I-EVENT | 137 | 0.14% | **Langka** |
| B-EVENT | 128 | 0.13% | **Langka** |
| I-LOCATION | 72 | 0.07% | **Sangat langka** |

**Implikasi:**
- Kelas `O` mendominasi → model bisa mendapat akurasi tinggi dengan selalu predict `O`.
- `EVENT` (B+I = 0.27%) dan `I-LOCATION` (0.07%) adalah **kelas minoritas ekstrem**.
- Risiko: model bagus di PERSON tapi buruk di EVENT → fitur graf event-centric (yang justru diminta Bu Diana di revisi temporal) jadi tidak reliable.

---

## 2. Skenario Threshold (yang dipakai)

### 2.A — Fixed threshold (baseline pembanding)

- THRESHOLD tetap di nilai konstan **0.9** sepanjang iterasi (= replikasi metode paper Ariyanto 2025).
- **Pro:** sederhana, deterministik, mudah dijelaskan di Bab 3.
- **Kontra:** kalau iterasi awal model masih lemah → hampir tidak ada pseudo-label yang lolos → self-training mandek.
- **Kapan dipakai:** sebagai baseline (E1 dan E3).

### 2.B — Adaptive threshold (dropping-only)

Threshold otomatis turun bila pseudo-label yang lolos terlalu sedikit. Tidak naik kembali (one-way) untuk menjaga simplicity.

**Algoritma:**
```
THRESHOLD_INIT     = 0.9
THRESHOLD_MIN      = 0.7
THRESHOLD_STEP     = 0.05
TARGET_MIN_SAMPLES = 200   # minimal kalimat baru per iterasi

for iter in range(MAX_ITERATIONS):
    threshold = THRESHOLD_INIT
    above = filter(predictions, threshold)
    while len(above) < TARGET_MIN_SAMPLES and threshold > THRESHOLD_MIN:
        threshold -= THRESHOLD_STEP   # turun ke 0.85, 0.80, 0.75, 0.70
        above = filter(predictions, threshold)
    if len(above) < TARGET_MIN_SAMPLES:
        break  # benar-benar mentok
    train += above
    retrain()
```

**Pro:**
- Mengatasi "cold start" iterasi pertama.
- Selaras dengan literatur self-training (FreeMatch / FlexMatch / Yu 2023, lihat §5).

**Kontra:**
- Tambah hyperparameter (THRESHOLD_MIN, THRESHOLD_STEP, TARGET_MIN_SAMPLES).
- Perlu dijelaskan di Bab 3 (tambah sub-bab metodologi).

**Kapan dipakai:** E4.

> **Alternatif yang TIDAK dipakai** (untuk transparansi):
> - Two-way threshold (turun + naik) → kompleksitas tambahan tanpa benefit jelas
> - Per-class threshold → tambah ×N hyperparameter, sulit di-tune dalam timeline TA
> - Confidence percentile (top-K%) → kualitas pseudo-label tidak ada lower-bound

---

## 3. Skenario Unbalanced Handling (yang dipakai)

Berdasarkan distribusi di §1.2, `EVENT` dan `I-LOCATION` butuh perhatian khusus.

### 3.A — Class weight pada loss function

Kalkulasi class weight inverse frequency:
```python
from sklearn.utils.class_weight import compute_class_weight
weights = compute_class_weight('balanced', classes=labels, y=y_train)
# Pass ke CrossEntropyLoss(weight=weights) via custom Trainer subclass
```

**Estimasi nilai weight untuk Sirah** (rumus `n_samples / (n_classes × n_samples_per_class)`):
- O: ~0.12 (turun karena dominan)
- B-PERSON: ~4.3, I-PERSON: ~4.9
- B-LOCATION: ~11.1
- B-EVENT: ~88, I-EVENT: ~82 (naik karena minoritas ekstrem)
- I-LOCATION: ~155 (paling tinggi)

**Pro:**
- Modifikasi minimal (~5 baris di custom Trainer); didukung HuggingFace native.
- Standar di literatur NER imbalanced (lihat MoM Learning di §5).

**Kontra:**
- Bisa overweight kelas langka → false positive EVENT meningkat.
- Weight ekstrem (155×) bisa bikin training tidak stabil → mungkin perlu clipping.

**Kapan dipakai:** E3 dan E4.

### 3.F — Tidak menangani (kontrol)

E1 sengaja tidak pakai handling apapun untuk jadi pembanding murni.

> **Alternatif yang TIDAK dipakai** (untuk transparansi):
> - **Focal loss** — perlu tuning α, γ (tambah 2 hyperparameter); class weight cukup untuk Sirah
> - **Oversampling** — risiko overfitting di kalimat unik dengan EVENT
> - **Data augmentation** — butuh tooling Bahasa Indonesia (Word2Vec/T5-id), effort tinggi
> - **Threshold per-class** — overlap dengan adaptive threshold di E4

---

## 4. Eksperimen yang Akan Dijalankan

### 4.1 Tabel ringkasan

| Eksperimen | Threshold | Unbalanced | Effort | Tujuan |
|---|---|---|---|---|
| **E1 — Baseline** | Fix 0.9 | Tidak ada | Rendah (sudah ada) | Replikasi paper Ariyanto, target F1 ≈ 0.863 |
| **E3 — Class weight only** | Fix 0.9 | Class weight | Sedang | Uji efek class weight murni |
| **E4 — Adaptive + class weight** | Adaptif 0.9→0.7 | Class weight | Sedang | Skenario terlengkap, jawab kedua revisi |

Matriks 2×2 (E2 dan E5 tidak dipakai):

| | Fix threshold | Adaptive threshold |
|---|---|---|
| **No class weight** | **E1** ✅ | ~~E2~~ (skipped) |
| **Class weight** | **E3** ✅ | **E4** ✅ |

### 4.2 Penjelasan konkret tiap eksperimen

#### **E1 — Baseline**

**Yang dijalankan:** notebook SRL-NER apa adanya, knob:
```python
THRESHOLD       = 0.9      # fix
SAMPLING_RATE   = 1.0      # pakai semua above 0.9
MIN_ENTITY_CONF = None     # tidak ada filter tambahan
class_weights   = None     # tidak ada handling
MAX_ITERATIONS  = 5
```

**Tujuan:**
- Replikasi metode paper Ariyanto 2025 (IndoBERT @ threshold 0.9)
- F1 baseline harus mendekati **0.863** (angka paper)
- Kalau hasil jauh lebih rendah → ada bug pipeline Sirah yang harus diperbaiki **sebelum** lanjut E3/E4

**File yang berubah:** tidak ada (tinggal run notebook existing)
**Effort:** ~0 jam coding, ~2-3 jam Colab

#### **E3 — Class weight only**

**Yang dijalankan:** E1 + custom Trainer subclass yang pakai weighted CrossEntropyLoss.

**Modifikasi kode (sketsa):**
```python
import torch
from transformers import Trainer
from sklearn.utils.class_weight import compute_class_weight

# Hitung weight di awal training
y_train_flat = [label for sent in train_labels for label in sent]
class_labels = sorted(set(y_train_flat))
weights = compute_class_weight('balanced', classes=class_labels, y=y_train_flat)
class_weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights_tensor, ignore_index=-100)
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss
```

**Threshold tetap fix 0.9** — yang berubah hanya loss-nya.

**Tujuan:**
- Uji apakah class weight saja sudah cukup memperbaiki F1 minoritas (terutama EVENT)
- Bandingkan dengan E1 untuk mengisolasi efek class weight

**File yang berubah:** notebook SRL-NER (custom Trainer class, weights computation)
**Effort:** ~2 jam coding + verifikasi, ~2-3 jam Colab

#### **E4 — Adaptive threshold + class weight (paling lengkap)**

**Yang dijalankan:** E3 + adaptive threshold dropping-only di section pseudo-labelling.

**Modifikasi kode (sketsa, di luar custom Trainer dari E3):**
```python
# Hyperparameter baru
THRESHOLD_INIT     = 0.9
THRESHOLD_MIN      = 0.7
THRESHOLD_STEP     = 0.05
TARGET_MIN_SAMPLES = 200

for i in range(MAX_ITERATIONS):
    threshold = THRESHOLD_INIT
    above_df = filter_threshold(model_path, ..., threshold=threshold, ...)
    n_above = above_df['text_id'].nunique() if len(above_df) else 0

    # Adaptive: turunkan threshold kalau kurang
    while n_above < TARGET_MIN_SAMPLES and threshold > THRESHOLD_MIN:
        threshold -= THRESHOLD_STEP
        above_df = filter_threshold(model_path, ..., threshold=threshold, ...)
        n_above = above_df['text_id'].nunique() if len(above_df) else 0

    if n_above < TARGET_MIN_SAMPLES:
        print(f"[iter {i}] adaptive mentok di {threshold}, stop")
        break

    iter_log.append({"iter": i, "threshold_used": threshold, "n_above": n_above, ...})
    # Class weight dari E3 tetap aktif di re-train
    train_df = pd.concat([train_df, above_df])
    retrain_with_weighted_loss(train_df, val_df)
```

**Tujuan:**
- Skenario terlengkap — kombinasi adaptive + class weight
- Jawab langsung kedua revisi Bu Diana sekaligus
- Bandingkan dengan E3 (lihat efek tambahan adaptive) dan E1 (efek total kombinasi)

**File yang berubah:** notebook SRL-NER (adaptive loop di pseudo-labelling section + custom Trainer dari E3)
**Effort:** ~1 jam tambahan kalau E3 sudah jadi, ~2-3 jam Colab

### 4.3 Justifikasi: kenapa E1+E3+E4 (bukan 5 eksperimen)?

**Matrix 2×2 E1/E3/E4 cukup untuk menjawab semua pertanyaan riset utama:**

| Perbandingan | Menjawab |
|---|---|
| E1 vs E3 | "Apakah class weight membantu di atas baseline?" |
| E1 vs E4 | "Apakah kombinasi keduanya signifikan vs baseline?" |
| E3 vs E4 | "Apakah adaptive threshold tambah value di atas class weight?" |
| Per-label F1 EVENT (E1, E3, E4) | "Apakah handling imbalance memperbaiki kelas paling minoritas?" |

**E2 (adaptive only) skipped** karena:
- Hipotesis: class weight = strategi yang tackle imbalance ekstrem (93% O) lebih langsung
- Kalau adaptive saja sudah cukup tanpa class weight, itu surprising — tapi bukan hipotesis utama
- Trade-off effort: 3 eksperimen × ~5 iterasi × ~30 menit = ~7.5 jam GPU (manageable di Colab free tier)

**E5 (per-class threshold) skipped** karena:
- Tambah 4–9 hyperparameter (1 threshold per BIO label) → sulit di-tune
- Sebagian benefit-nya sudah dicakup oleh class weight di E3/E4
- Kalau Bu Diana minta, bisa ditambah sebagai eksperimen bonus di akhir

---

## 5. Referensi Paper Pendukung (2021–2026)

Paper yang bisa dirujuk di Bab 2/3 untuk justifikasi pemilihan eksperimen E1, E3, dan E4. Dikelompokkan ke 3 grup sesuai komponen yang dipakai:
- **A. Adaptive threshold** (mendukung E4 — adaptive 0.9→0.7)
- **B. Class weight / imbalance handling NER** (mendukung E3 dan E4)
- **C. Konteks SRL Indonesia + IndoBERT NER** (mendukung E1 baseline + bahasa)

> Paper untuk metode yang **tidak dipakai** (focal loss, oversampling, augmentation, per-class threshold) sengaja tidak dimasukkan supaya bibliografi rapat.

### 5.A. Adaptive Threshold Pseudo-Labelling (untuk E4)

#### A.1 — FreeMatch: Self-adaptive Thresholding for Semi-supervised Learning ⭐
- **Penulis & Tahun:** Wang et al., ICLR 2023
- **Link:** https://arxiv.org/abs/2205.07246
- **OpenReview:** https://openreview.net/forum?id=PDrUPTXJI_A
- **Inti:** Menggantikan fixed threshold dengan **Self-Adaptive Thresholding (SAT)** — global threshold + class-specific threshold yang dihitung dari Exponential Moving Average (EMA) confidence model. Tambahan: class fairness regularization untuk mencegah bias ke majority class.
- **Hasil:** Error reduction 5.78% di CIFAR-10 (1 label/class), 13.59% di STL-10 (4 labels/class) versus FlexMatch.
- **Plus untuk E4 Sirah:**
  - Gold standard untuk adaptive threshold di SSL — sering disitir (1000+ citations)
  - Justifikasi argumen umum: "fixed threshold suboptimal, adaptive lebih baik"
  - Konsep "auto-adjust threshold" persis yang Bu Diana minta
- **Minus / catatan:**
  - Eksperimennya di image classification, bukan NER → di skenario kita pakai versi **lebih sederhana** (dropping-only, bukan EMA penuh)
  - EMA butuh batch besar untuk stabil; dropping-only Sirah lebih ringan computasional

#### A.2 — A Class-Rebalancing Self-Training Framework for Distantly-Supervised NER ⭐⭐
- **Penulis & Tahun:** Yu et al., ACL Findings 2023
- **Link:** https://aclanthology.org/2023.findings-acl.703/
- **Inti:** **Paling langsung relevan** untuk E4. Mengatasi masalah self-training pada NER yang biased ke high-performance class. Solusi mencakup: (1) **class-wise flexible threshold** untuk seleksi kandidat per kelas, (2) class-rebalancing sampling, (3) re-labeling untuk perbaiki noisy pseudo-labels.
- **Plus untuk E4 Sirah:**
  - **NER + self-training + adaptive threshold + class imbalance** dalam satu paper — exactly mendukung E4 (gabungan adaptive threshold + class weight) dan sebagian E3 (class weight)
  - Bisa langsung disitir di Bab 3 sebagai justifikasi metodologi gabungan
  - ACL Findings 2023 — venue kuat
- **Minus / catatan:**
  - Konteks distantly-supervised NER (pakai gazetteer/knowledge base) — bukan persis pseudo-labelling Sirah, tapi prinsip transfer dengan mudah
  - Implementasi mereka kompleks (3 komponen) — Sirah pakai sub-komponen saja

#### A.3 — FlexMatch: Boosting Semi-Supervised Learning with Curriculum Pseudo-Labeling
- **Penulis & Tahun:** Zhang et al., NeurIPS 2021
- **Link:** https://arxiv.org/abs/2110.08263
- **Inti:** Predecessor FreeMatch. Konsep **curriculum pseudo-labelling** — threshold turun untuk kelas yang masih sulit dipelajari model. Filosofi sama dengan dropping-only di E4: kalau model belum confidence, jangan paksakan threshold tinggi.
- **Plus untuk E4 Sirah:**
  - Disitir untuk konsep "curriculum" — model belajar bertahap dari kalimat mudah ke sulit
  - Lebih simpel dari FreeMatch — dekat dengan dropping-only di skenario
- **Minus / catatan:**
  - Sudah dianggap obsoleted oleh FreeMatch di benchmark image, tapi masih relevan sebagai konsep dasar
  - Sebaiknya disitir bareng FreeMatch (history) bukan sendirian

### 5.B. Class Weight / Imbalance Handling NER (untuk E3 dan E4)

#### B.1 — Majority or Minority: Data Imbalance Learning Method for NER (MoM) ⭐⭐
- **Penulis & Tahun:** Akkasi et al., arxiv 2024
- **Link:** https://arxiv.org/abs/2401.11431
- **Inti:** Long-tail distribution di NER dengan banyak minority class + 1 majority class (kelas O). Solusi: tambahkan loss yang dihitung **hanya pada token majority class** ke loss konvensional, supaya model tidak mengabaikan O sambil tetap belajar minority. Plug-in, model-agnostic.
- **Plus untuk E3/E4 Sirah:**
  - **Sangat relevan** — Sirah persis long-tail dengan O dominan 93%
  - Justifikasi langsung untuk perlunya imbalance handling di NER
  - Implementasi mereka simpel (modifikasi loss) — paralel dengan pendekatan class weight Sirah
- **Minus / catatan:**
  - Belum di-peer-review (arxiv preprint per pengecekan terakhir) — kekuatan sitasi lebih lemah dari ACL/NeurIPS
  - Eksperimen di English NER datasets — perlu disebut bahwa Sirah replikasi konsep, bukan persis metode

#### B.2 — Self-Training: A Survey
- **Penulis & Tahun:** Amini et al., Neurocomputing 2024
- **Link:** https://www.sciencedirect.com/science/article/pii/S0925231224016758
- **Versi arxiv (open):** https://arxiv.org/abs/2202.12040
- **Inti:** Survey komprehensif tentang self-training: confidence-based selection, threshold strategies, noise handling, application areas. Membahas bagaimana imbalance + threshold berinteraksi.
- **Plus untuk E1/E3/E4 Sirah:**
  - **Wajib disitir** sebagai overview di Bab 2 (kajian pustaka self-training)
  - Memberikan framework taxonomi yang kuat — bisa untuk justifikasi posisi metode E4 (adaptive + handling) di lanskap self-training
  - Sitasi tinggi → kredibel
- **Minus / catatan:**
  - Survey, bukan metode baru — tidak bisa jadi rujukan utama untuk metode spesifik
  - Sangat panjang (60+ halaman), perlu skim sub-section yang relevan saja

#### B.3 — Sentence-Level Resampling for Named Entity Recognition (alternatif)
- **Penulis & Tahun:** Akkasi & Moens, NAACL 2022
- **Link:** https://aclanthology.org/2022.naacl-main.156/
- **Inti:** Alternatif untuk imbalance handling — resampling di level kalimat berdasarkan distribusi entity, bukan modify loss. Tidak dipakai langsung di Sirah, tapi disebut sebagai pembanding metode di Bab 2.
- **Plus untuk Sirah (sebagai pembanding):**
  - Memperkaya Bab 2 — tunjukkan ada banyak strategi imbalance, dan Sirah memilih class weight karena alasan X
  - NAACL — venue kuat
- **Minus / catatan:**
  - Tidak diimplementasikan di Sirah (tidak masuk eksperimen E1/E3/E4)
  - Hanya disitir sebagai "pembanding metode" di kajian pustaka

### 5.C. Konteks: SRL Indonesia + IndoBERT (untuk E1 baseline + bahasa)

#### C.1 — Transformer-Based SRL for Crisis Events Using Semi-Supervised Learning (Ariyanto et al.) ⭐⭐⭐
- **Penulis & Tahun:** Ariyanto, Purwitasari, Fatichah, Ravana, Andrian, Parwata, IEEE Access Sept 2025
- **Link Paper:** https://ieeexplore.ieee.org/document/11097773 (DOI: 10.1109/ACCESS.2025.3604068)
- **Link Disertasi (lokal):** `7025221021-Doctoral.pdf` di root repo
- **Inti:** Paper baseline yang akan direplikasi di **E1**. Algorithm 1 (Self-Training with Filtering Function) = pipeline yang dipakai Sirah. Tested fixed threshold 0.7/0.8/0.9 → IndoBERT @ 0.9 menang dengan F1 **0.863**.
- **Plus untuk Sirah:**
  - **Pembimbing yang sama (Bu Diana)** — pasti expected disitir di Bab 2 dan Bab 4
  - Method 100% transferable ke Sirah (sama-sama pseudo-labelling SRL Indonesia, sama-sama IndoBERT, sama-sama imbalanced)
  - F1 0.863 = target E1 Sirah → kalau hasil Sirah dekat angka ini, validasi pipeline sukses
  - Memberikan justifikasi pemilihan IndoBERT (paper sudah benchmark 4 model: IndoBERT, IndoRoBERTa, GPT-2, Komodo)
- **Minus / catatan:**
  - Domain Twitter crisis events ≠ narasi historis — label SRL berbeda (15 specific labels vs 4 generic Sirah)
  - Tidak menangani imbalance secara eksplisit → justru ini gap yang Sirah isi di E3/E4

#### C.2 — IPerFEX-2023: Indonesian Financial Entity Extraction with IndoBERT-BiGRU-CRF
- **Penulis & Tahun:** Saputra et al., Journal of Big Data 2024
- **Link:** https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-00987-6
- **Inti:** IndoBERT untuk NER Bahasa Indonesia di domain finansial. Konfirmasi IndoBERT bagus untuk domain-specific NER.
- **Plus untuk Sirah:**
  - Konfirmasi pemilihan IndoBERT untuk Bahasa Indonesia sudah tepat
  - Domain-specific NER Bahasa Indonesia → pendamping argumen Sirah (juga domain-specific)
  - Open access (gratis akses)
- **Minus / catatan:**
  - Domain finansial sangat beda dari narasi sejarah
  - Mereka pakai BiGRU+CRF di atas IndoBERT — Sirah tidak (token classification head simpel saja)

#### C.3 — Dataset Enhancement and Multilingual Transfer for NER in Indonesian
- **Penulis & Tahun:** Khairunnisa et al., ACM TALLIP 2023
- **Link:** https://dl.acm.org/doi/10.1145/3592854
- **Inti:** Augmentasi dataset NER Bahasa Indonesia + transfer learning dari bahasa lain. Membahas tantangan low-resource Bahasa Indonesia.
- **Plus untuk Sirah:**
  - Justifikasi kuat untuk "Bahasa Indonesia = low-resource untuk NER" → motivasi self-training Sirah
  - Bisa disitir di Bab 1 (motivasi) atau awal Bab 2
- **Minus / catatan:**
  - Generic NER (PER/ORG/LOC), bukan domain spesifik
  - Paywalled — perlu akses ITS

### 5.D. Mapping Paper ⇄ Eksperimen

| Eksperimen | Komponen | Paper rujukan utama |
|---|---|---|
| **E1 Baseline (fix 0.9)** | Replikasi metode pembanding | C.1 (Ariyanto 2025) ⭐⭐⭐ |
| **E3 Class weight only** | Weighted loss untuk imbalance | B.1 (MoM) + B.2 (Survey) |
| **E4 Adaptive + class weight** | Threshold dropping + class weight | A.2 (Yu 2023) ⭐⭐ — paling cocok jadi rujukan utama |
| **E4 — komponen adaptive saja** | Justifikasi adaptive threshold | A.1 (FreeMatch) + A.3 (FlexMatch) |
| **Konteks bahasa** | Bahasa Indonesia + IndoBERT | C.2 + C.3 |
| **Konteks self-training** | Overview metodologi | B.2 (Survey) |

### 5.E. Top 5 Sitasi Prioritas

Kalau hanya bisa sitir 5 paper di Bab 2 sub-bab pseudo-labelling/imbalance, prioritas:

1. **C.1 — Ariyanto et al. IEEE Access 2025** ⭐⭐⭐ — baseline pembanding (wajib disitir, pembimbing sama)
2. **A.2 — Yu et al. ACL 2023** ⭐⭐ — paling langsung relevan (NER + self-training + adaptive threshold + class imbalance dalam 1 paper)
3. **B.1 — MoM Learning 2024** ⭐⭐ — imbalance handling untuk NER long-tail
4. **A.1 — FreeMatch ICLR 2023** ⭐ — gold standard adaptive threshold (justifikasi konsep umum)
5. **B.2 — Self-Training Survey 2024** — overview komprehensif self-training

Sisanya (A.3, B.3, C.2, C.3) bisa disitir sebagai supporting references kalau butuh memperkaya konteks atau pembanding.

### 5.F. Cara Akses Paper

| Tipe | Akses |
|---|---|
| **arxiv** | Gratis, link langsung di atas |
| **ACL Anthology** | Gratis, link langsung di atas |
| **NeurIPS / OpenReview** | Gratis, link langsung di atas |
| **IEEE Access (paper Ariyanto)** | **Open Access — gratis** |
| **Journal of Big Data (Springer)** | Open Access — gratis |
| **Neurocomputing (Elsevier)** | Paywalled — pakai akses institusi ITS atau versi arxiv |
| **ACM Digital Library** | Paywalled — pakai akses ITS |

**Catatan akses ITS:** Untuk paper paywalled, kalau Anda sudah login ke jaringan ITS (atau pakai VPN ITS dari rumah), biasanya akses langsung terbuka via library.its.ac.id.

---

## 6. Pertanyaan & Bahan Diskusi untuk Bu Diana

### 6.1 Pertanyaan klarifikasi (sebelum coding)

1. **Setuju dengan scope 3 eksperimen (E1+E3+E4)?** Atau perlu tambah E2 (adaptive only) untuk isolasi efek adaptive?
2. **Threshold adaptif dropping-only** (turun 0.9→0.7) sudah cukup, atau perlu two-way (turun + naik)?
3. **Class weight** (inverse frequency) sudah cukup, atau perlu bandingkan dengan focal loss juga?
4. **Model** — tetap pakai IndoBERT base (current), atau coba IndoBERT-large / XLM-R / lainnya? Bu Diana di revisi bilang "kalau tidak mau ribet bisa pakai yang ada" — apakah ini lampu hijau untuk tetap di IndoBERT base?
5. **Metrik perbandingan** — F1 entity-level (seqeval) saja, atau perlu juga per-label F1 untuk tunjukkan dampak handling EVENT?
6. **Posisi di laporan** — ini dilaporkan sebagai sub-bab Bab 3 (Skenario Eksperimen) + tabel hasil di Bab 4? Atau struktur lain?

### 6.2 Bahan diskusi dengan rujukan paper

Saat konsultasi, paper-paper di §5 bisa dipakai untuk:
- **Justifikasi metode adaptive threshold E4:** rujuk A.1 (FreeMatch) dan A.2 (Yu 2023) sebagai precedent
- **Justifikasi class weight E3/E4:** rujuk B.1 (MoM) sebagai precedent NER imbalanced
- **Justifikasi tetap pakai IndoBERT:** rujuk C.1 (Ariyanto) yang sudah benchmark 4 model
- **Justifikasi self-training framework:** rujuk B.2 (Survey 2024) sebagai overview
- **Justifikasi target F1 baseline ≈ 0.863:** rujuk C.1 (paper pembimbing) sebagai angka pembanding

---

## 7. Implementasi (setelah skenario disepakati)

Estimasi effort & file yang berubah:

| Eksperimen | File yang berubah | Estimasi |
|---|---|---|
| E1 (baseline) | Sudah ada, tinggal run | 0 jam coding, ~2-3 jam Colab |
| E3 (class weight) | Custom `Trainer` subclass dengan weighted loss | ~2 jam coding |
| E4 (adaptive + cw) | Adaptive loop + Trainer dari E3 | ~1 jam tambahan |
| Logging & tabel | `iteration_log.csv` perlu kolom tambahan (`threshold_used`, `class_weights_active`) | ~1 jam |

**Total estimasi:** ~4-5 jam coding + ~7-8 jam run di Colab.

**Prasyarat sebelum coding:**
- Approval Bu Diana untuk scope 3 eksperimen
- Verifikasi E1 (baseline) bisa jalan tanpa error → konfirmasi pipeline Sirah valid

---

## 8. Output yang diharapkan

Setelah eksperimen selesai:

1. **Tabel hasil utama** (Bab 4):

| Eksperimen | F1 Overall | F1 PERSON | F1 LOCATION | F1 TIME | F1 EVENT |
|---|---:|---:|---:|---:|---:|
| E1 (baseline) | (target ≈ 0.86) | ? | ? | ? | ? |
| E3 (class weight) | ? | ? | ? | ? | ? (target naik) |
| E4 (adaptive + cw) | ? | ? | ? | ? | ? (target tertinggi) |

2. **Plot F1 vs iterasi** untuk 3 eksperimen (dari `iteration_log.csv`)
3. **Plot threshold_used vs iterasi** khusus E4 (tunjukkan dynamic adaptation)
4. **Analisis** mana yang terbaik untuk EVENT (kunci untuk Knowledge Graph kronologis sesuai revisi temporal Bu Diana)
5. **Rekomendasi pipeline final** — eksperimen pemenang dipakai untuk inferensi ke seluruh `sirah_chunks_final.csv`
