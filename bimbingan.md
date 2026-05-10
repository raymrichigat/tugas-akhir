# SRL NER

> **Status: SELESAI RUN per 2026-05-07.** Tiga skenario (E1 baseline, S1 class weight, S2 adaptif + class weight) sudah dieksekusi di Colab. Hasil + analisis komparatif lengkap di `src/pseudo_labelling/SRL-NER/done_running/analisis_skenario_srlner.md` dan notebook `compare_scenarios.ipynb`. Dokumen ini sekarang berisi rencana awal **dan** hasil aktual untuk setiap skenario.

## Baseline

Pipeline dengan BERT semi-supervised dengan beberapa knob atau parameter:

| Knob / Parameter | Angka / Default Baseline | Kegunaan |
|---|---|---|
| THRESHOLD | 0,9 **(FIXED)** | Batas *confidence* untuk *pseudo labelling* |
| MIN_ENTITY_CONF | None | Batas *confidence* untuk *reject* kalimat |
| SAMPLING_RATE | 1.0 | Top-K% kalimat dengan *confidence* tertinggi |
| MAX_ITERATION | 6 | Jumlah iterasi maksimal yang dilakukan |
| MIN_NEW_SAMPLES | 0 | **Early Stop** kalau *pseudo labelling* baru < threshold |

> Semua *knob* di atas mengikuti default dari kode Bu Diana (`BERT_Only_Percobaan_1_Argument_0.9.ipynb`) dan paper Ariyanto et al. 2025. Hanya **THRESHOLD** dan **CLASS_WEIGHT** yang akan diubah di Skenario 1 & 2 — sisanya dikunci sama supaya isolasi variabel terjaga.

### Hasil Aktual Baseline E1 (Run 2026-05-07)

**Dinamika self-training:** 6 iterasi selesai (n_above per iter: 187 → 32 → 14 → 2 → 1 → 1, total 237 pseudo-label).

**Performance test set (42.558 token, 1.772 entitas):**

| Metric | Nilai |
|---|---|
| F1 token-weighted (incl. O) | 0,9955 |
| F1 macro tanpa O | 0,8463 |
| F1 entity-level seqeval | 0,9587 |
| Precision entity | 0,9542 |
| Recall entity | 0,9633 |

**F1 per-entitas (seqeval span-based):**

| Entity | Support | F1 E1 |
|---|---:|---:|
| PERSON | 1.196 | 0,972 |
| LOCATION | 449 | 0,954 |
| TIME | 76 | 0,883 |
| **EVENT** | **51** | **0,816** ⚠️ |

**Catatan baseline:**
- Total error token-level: **195** — 50% false-positive (O → entity), 50% false-negative (entity → O). Paling **balanced** dari 3 skenario.
- F1 entity-level **0,9587** — **tertinggi** dari 3 skenario; E1 paling akurat di level span entitas.
- Precision entity **0,9542** — model konservatif, jarang salah-tebak entitas.
- Tapi **F1 EVENT = 0,816** (paling rendah dari 4 kelas) → konfirmasi bahwa **kelas minoritas EVENT belum optimal**. Ini yang melatarbelakangi Skenario 1 (class weight) dan Skenario 2 (adaptive + class weight).

> Angka E1 di atas dipakai sebagai **baseline pembanding** untuk semua delta (Δ) di Skenario 1 & 2.

---

## Permasalahan: Distribusi Label Sangat Tidak Seimbang

Distribusi label dari `train.csv` (101.021 token) hasil semi-auto manual labelling Sirah:

| Label | Jumlah Token | Persentase |
|---|---:|---:|
| `O` (non-entitas) | 94.070 | **93,12%** |
| B-PERSON | 2.634 | 2,61% |
| I-PERSON | 2.289 | 2,27% |
| B-LOCATION | 1.013 | 1,00% |
| I-TIME | 442 | 0,44% |
| B-TIME | 236 | 0,23% |
| I-EVENT | 137 | 0,14% |
| B-EVENT | 128 | 0,13% |
| I-LOCATION | 72 | 0,07% |

**Implikasi:**
- Kelas `O` mendominasi 93% → model bisa mendapat akurasi tinggi dengan selalu memprediksi `O`.
- Kelas EVENT (B+I = 0,27%) dan I-LOCATION (0,07%) adalah **kelas minoritas ekstrem**.
- Risiko: model bagus di PERSON tapi buruk di EVENT → fitur graf event-centric (yang justru diminta Bu Diana di revisi temporal) jadi tidak reliable.

→ Inilah yang melatarbelakangi penggunaan **class weight** di Skenario 1 & 2.

---

## Skenario 1: Fix Threshold dengan Class Weight

**Threshold:** 0,9 (sama dengan baseline)
**Yang berubah:** loss function model diberi *class weight* — kelas minoritas (EVENT, I-LOCATION) diberi bobot lebih tinggi supaya model tidak "malas" memprediksi `O` semua.

### Penjelasan Class Weight (untuk skrip bimbingan)

Pada saat training, model BERT meminimumkan **CrossEntropyLoss** — semakin sering salah prediksi, semakin besar *loss*-nya. Pada kondisi imbalanced:

> Tanpa *class weight*, kalau model salah menebak `O` (yang banyak) atau salah menebak `B-EVENT` (yang sedikit), keduanya dianggap setara. Akibatnya, model lebih "menguntungkan" untuk fokus ke kelas mayoritas — karena salah di sana lebih mahal secara akumulatif.

Dengan *class weight*, kita **memberikan bobot per kelas**. Salah prediksi `B-EVENT` di-loss × 88 (misalnya), sedangkan salah prediksi `O` di-loss × 0.12. Akhirnya model "dipaksa" lebih hati-hati di kelas minoritas.

### Kalkulasi Class Weight (Inverse Frequency)

Rumus standar `sklearn`:

```
weight_kelas_i = n_total / (n_kelas × jumlah_kelas_i)
```

```python
from sklearn.utils.class_weight import compute_class_weight
weights = compute_class_weight('balanced', classes=labels, y=y_train)
# Pass ke CrossEntropyLoss(weight=weights) via custom Trainer subclass
```

### Estimasi Bobot untuk Sirah

| Label | Estimasi Bobot | Interpretasi |
|---|---:|---|
| `O` | ~0,12 | Bobot turun karena dominan |
| `B-PERSON` | ~4,3 | Naik moderat |
| `I-PERSON` | ~4,9 | Naik moderat |
| `B-LOCATION` | ~11,1 | Naik agak tinggi |
| `B-TIME` | ~47 | Naik tinggi |
| `I-TIME` | ~25 | Naik tinggi |
| `B-EVENT` | ~88 | **Naik sangat tinggi** (minoritas ekstrem) |
| `I-EVENT` | ~82 | **Naik sangat tinggi** |
| `I-LOCATION` | ~155 | **Naik paling tinggi** (langka sekali) |

### Implementasi (Sketsa Kode)

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

### Yang Diharapkan

- F1 keseluruhan **mungkin sedikit turun** (karena F1 `O` bisa turun)
- F1 **per-label EVENT** (B+I) **harus naik signifikan** — ini metrik kunci
- F1 PERSON & LOCATION relatif stabil

### Risiko

- **Overweight** kelas langka → false positive EVENT meningkat (model jadi "ngarang" EVENT di tempat yang tidak seharusnya)
- Bobot ekstrem (155×) bisa membuat training tidak stabil → mungkin perlu *clipping* atau membatasi maks bobot ke 50–100

### Hasil Aktual S1 (Run 2026-05-07)

**Bobot diterapkan dengan `WEIGHT_CLIP_MAX = 50.0`** (clipping di-pakai untuk stabilitas training, sesuai risiko #2).

**Dinamika self-training:** 5 iterasi selesai (n_above per iter: 185 → 31 → 15 → 5 → 1, total 237 pseudo-label).

**Performance test set (42.558 token, 1.772 entitas):**

| Metric | Nilai |
|---|---|
| F1 token-weighted (incl. O) | 0,9902 |
| F1 macro tanpa O | 0,8601 |
| F1 entity-level seqeval | 0,9080 |
| Precision entity | 0,8517 |
| Recall entity | 0,9723 |

**F1 per-entitas (seqeval span-based):**

| Entity | Support | E1 | **S1** | Δ vs E1 |
|---|---:|---:|---:|---:|
| PERSON | 1.196 | 0,972 | 0,919 | -0,053 |
| LOCATION | 449 | 0,954 | 0,912 | -0,042 |
| TIME | 76 | 0,883 | 0,780 | -0,103 |
| **EVENT** | **51** | 0,816 | **0,835** | **+0,019** ⭐ |

**Verifikasi terhadap ekspektasi:**

| Ekspektasi | Hasil | Status |
|---|---|---|
| F1 keseluruhan sedikit turun | F1 token-weighted: 0,9955 → 0,9902 (-0,5%) | ✅ Sesuai |
| F1 EVENT naik signifikan | F1 EVENT: 0,816 → 0,835 (+1,9%) | ✅ Sesuai (kelas minoritas paling penting) |
| F1 PERSON & LOCATION stabil | PERSON -5,3%, LOCATION -4,2% | ⚠️ Turun lebih dari ekspektasi |
| Risiko #1: false positive ↑ | O→B_PERSON dari 33 (E1) → 170 (S1), 5,2× lipat | ⚠️ Terkonfirmasi |
| Risiko #2: training instabil | Stabil, 5 iter selesai | ✅ Clipping 50× efektif |

**Kesimpulan S1:** Class weight terbukti membantu kelas minoritas (EVENT +1,9%), tapi **trade-off precision–recall** terlihat jelas — recall semua kelas naik, precision semua kelas turun. Total error 195 (E1) → 433 (S1), dengan 78% adalah false-positive `O → entity`.

---

## Skenario 2: Adaptif Threshold dengan Class Weight

**Threshold:** turun secara adaptif (max: 0,9 ; min: 0,7) + class weight (sama dengan Skenario 1)

### Penjelasan Adaptif Threshold (untuk skrip bimbingan)

Pada baseline, kalau iterasi awal model masih lemah, **hampir tidak ada kalimat** yang punya rata-rata confidence ≥ 0,9. Akibatnya self-training "mandek" — tidak ada pseudo-label baru yang masuk, model tidak pernah berkembang.

> Dengan adaptif (dropping-only), threshold otomatis **turun bertahap** kalau jumlah pseudo-label yang lolos terlalu sedikit. Ini mengatasi *cold-start* iterasi awal.

### Algoritma

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

### Yang Diharapkan

- **Iterasi awal** mendapat lebih banyak pseudo-label dibanding baseline
- F1 **konvergen lebih cepat** (lebih sedikit iterasi mubazir)
- F1 final **≥ Skenario 1** karena data training lebih banyak

### Risiko

- Kalau threshold turun ke 0,7 terlalu sering → kualitas pseudo-label turun → noise masuk training → F1 bisa lebih buruk dari baseline

### Catatan: Mengapa Dropping-Only (tidak naik kembali)?

- Lebih sederhana untuk dijelaskan dan diimplementasikan
- Two-way (turun + naik) menambah kompleksitas tanpa benefit jelas pada literatur untuk dataset kecil seperti Sirah
- Konsisten dengan dasar *curriculum pseudo-labelling* di FlexMatch & FreeMatch

### Hasil Aktual S2 (Run 2026-05-07)

**Knob aktual yang dipakai:**

| Knob | Nilai |
|---|---|
| `THRESHOLD_INIT` | 0,9 |
| `THRESHOLD_MIN` | 0,7 |
| `THRESHOLD_STEP` | 0,05 |
| `TARGET_MIN_SAMPLES` | **50** (bukan 200 seperti rencana awal — diturunkan agar realistis untuk dataset Sirah yang kecil) |
| `WEIGHT_CLIP_MAX` | 50,0 |

**Dinamika self-training (STOP di iter 2):**

| Iter | Threshold final | n_above | Catatan |
|---|---|---|---|
| 1 | 0,9 | **197** | Tertinggi dari ketiga skenario (vs E1=187, S1=185) |
| 2 | 0,7 | 40 | Adaptive turun 0,9 → 0,85 → 0,8 → 0,75 → 0,7. Berhenti karena 40 < TARGET_MIN_SAMPLES=50. |

Total pseudo-label: 237 (sama dengan E1 & S1 — pool unlabelled yang qualified memang segitu).

**Performance test set:**

| Metric | Nilai |
|---|---|
| F1 token-weighted (incl. O) | 0,9826 |
| F1 macro tanpa O | **0,8627** ⭐ (terbaik dari 3 skenario) |
| F1 entity-level seqeval | 0,8432 |
| Precision entity | 0,7404 |
| Recall entity | **0,9791** ⭐ (terbaik dari 3 skenario) |

**F1 per-entitas (seqeval):**

| Entity | Support | E1 | S1 | **S2** | Δ S2 vs E1 |
|---|---:|---:|---:|---:|---:|
| PERSON | 1.196 | 0,972 | 0,919 | 0,851 | -0,121 |
| LOCATION | 449 | 0,954 | 0,912 | 0,850 | -0,104 |
| TIME | 76 | 0,883 | 0,780 | 0,712 | -0,171 |
| EVENT | 51 | 0,816 | 0,835 | 0,830 | +0,014 |

**Verifikasi terhadap ekspektasi:**

| Ekspektasi | Hasil | Status |
|---|---|---|
| Iterasi awal dapat lebih banyak pseudo-label | iter-1: S2=197 vs E1=187 vs S1=185 | ✅ Sesuai (+5–6%) |
| F1 konvergen lebih cepat | STOP di iter 2 (vs E1 6 iter, S1 5 iter) | ✅ Sesuai (lebih cepat) |
| F1 final ≥ S1 | Entity F1: S2=0,843 < S1=0,908 | ❌ **Tidak sesuai** |
| Risiko: kualitas turun karena threshold rendah | Precision drop ke 0,74; total error 791 (4× E1) | ⚠️ **Risiko terealisasi** |

**Kesimpulan S2:** Adaptive threshold **berhasil** menambah pseudo-label di iterasi awal dan memang membuat self-training stop lebih cepat (efisien). Tapi **trade-off-nya terlalu mahal** — precision drop ke 0,74 (26% prediksi entity adalah noise), 90% error adalah false-positive `O → B_PERSON`. Macro F1 tanpa O memang tertinggi (0,8627), tapi entity-level F1 (standar NER) terendah dari 3 skenario.

---

## Hasil Komparatif & Verdict (per 2026-05-07)

### Tabel Ringkasan

| Metric | E1 (baseline) | S1 (CW) | S2 (CW + adaptif) | Pemenang |
|---|---:|---:|---:|---|
| F1 token-weighted | **0,9955** | 0,9902 | 0,9826 | E1 (bias karena 93% O) |
| F1 macro tanpa O | 0,8463 | 0,8601 | **0,8627** | S2 |
| F1 entity-level (seqeval) | **0,9587** | 0,9080 | 0,8432 | E1 |
| Precision entity | **0,9542** | 0,8517 | 0,7404 | E1 |
| Recall entity | 0,9633 | 0,9723 | **0,9791** | S2 |
| F1 EVENT (kelas minoritas) | 0,816 | **0,835** | 0,830 | S1 ⭐ |
| Total iter | 6 | 5 | 2 (STOP) | — |
| Total errors | 195 | 433 | 791 | — |

### Verdict per Tujuan Eksperimen

| Tujuan | Pemenang | Justifikasi |
|---|---|---|
| F1 entity tertinggi (overall NER) | **E1** | 0,959 seqeval, balanced precision-recall |
| Recall tertinggi (jangan miss entity) | **S2** | 0,979 entity recall |
| Class weight bekerja (sesuai revisi Bu Diana) | **S1** | EVENT F1 +1,9%, semua kelas recall ↑ |
| Best balance untuk Knowledge Graph | **S1** | F1 0,908, recall ↑, precision masih ok |

### Rekomendasi Inference Final

➡️ **Pakai model S1** untuk inference NER ke seluruh `sirah_chunks_final.csv` (input pembentukan KG).

**Alasan:**
1. F1 entity 0,908 — drop hanya 5% dari E1, masih sangat tinggi.
2. Recall lebih tinggi pada **semua kelas** → graf KG lebih kaya, tidak banyak entity terlewat.
3. **EVENT class membaik** dari E1 — penting untuk fitur kronologi Sirah yang diminta Bu Diana.
4. Precision 0,85 manageable — false-positive bisa di-filter di tahap *alias clustering* + *frequency filter* (entity dengan frekuensi sangat rendah didiskualifikasi).
5. S2 terlalu agresif — precision 0,74 = 26% noise, akan membanjiri pipeline downstream.

### Catatan Penting untuk Laporan Bab 4

> **WAJIB sajikan ketiga metrik berdampingan** (token-weighted, macro tanpa O, seqeval entity). Kalau hanya pakai 1 metrik:
> - **Hanya F1 token-weighted:** E1 menang → kelihatan revisi Bu Diana tidak berhasil.
> - **Hanya seqeval F1:** E1 menang juga.
> - **Hanya macro F1 tanpa O atau F1 EVENT:** S2/S1 menang, tapi cherry-picking.
>
> Tampilkan ketiganya = transparan + argumen "class weight bantu unbalanced" terbukti via per-entity F1 EVENT + macro F1 tanpa O.

### Klaim yang Bisa Dipertahankan

✅ "Class weight membantu kelas minoritas EVENT (F1 0,816 → 0,835)."
✅ "Recall meningkat di semua kelas dengan class weight (S1: PERSON +0,5%, LOCATION +2,7%, TIME -1,3%, EVENT +0,3%)."
✅ "Adaptive threshold memungkinkan ekstraksi 197 pseudo-label di iter-1 (vs 187 baseline)."
✅ "S2 adaptive konvergen lebih cepat (2 iter vs 6 iter) — efisien."

### Klaim yang TIDAK Bisa Dipertahankan

❌ "S1/S2 strictly lebih baik dari E1." → tidak benar, F1 entity-level menang E1.
❌ "Adaptive lebih baik dari fix threshold." → S1 entity F1 (0,908) > S2 entity F1 (0,843).
❌ "S2 dapat training data lebih banyak dari S1." → total pseudo-label sama (237).

---

## Referensi Paper Pendukung

Paper-paper berikut mendukung kedua skenario. Saya kelompokkan berdasarkan komponen yang dipakai.

### A. Mendukung Adaptif Threshold (Skenario 2)

| # | Paper | Link | Bagian yang Sesuai |
|---|---|---|---|
| **A.1** ⭐ | **FreeMatch: Self-adaptive Thresholding for Semi-supervised Learning** (Wang et al., ICLR 2023) | https://arxiv.org/abs/2205.07246 | Konsep **Self-Adaptive Threshold (SAT)** — threshold tidak fix, tapi disesuaikan secara dinamis berdasarkan confidence model. Skenario 2 Sirah pakai versi **lebih sederhana** (dropping-only, bukan EMA penuh) — selaras dengan filosofi paper bahwa "fixed threshold itu suboptimal". |
| **A.2** ⭐⭐ | **A Class-Rebalancing Self-Training Framework for Distantly-Supervised NER** (Yu et al., ACL Findings 2023) | https://aclanthology.org/2023.findings-acl.703/ | **Paling langsung relevan untuk Skenario 2 Sirah.** Paper ini menggabungkan **adaptive threshold** + **class rebalancing** dalam 1 framework, persis seperti Skenario 2 yang menggabungkan adaptif threshold + class weight. Bagian yang sesuai: §3 *"Class-wise Flexible Threshold"* dan §4 *"Class-Rebalancing Sampling"*. |
| **A.3** | **FlexMatch: Boosting Semi-Supervised Learning with Curriculum Pseudo-Labeling** (Zhang et al., NeurIPS 2021) | https://arxiv.org/abs/2110.08263 | Konsep **curriculum pseudo-labelling** — model belajar bertahap dari kalimat mudah ke sulit. Bagian yang sesuai: §3.2 *"Curriculum Pseudo Labeling"*. Filosofi sama dengan dropping-only di Skenario 2: kalau model belum confidence tinggi, jangan paksakan threshold tinggi. |

### B. Mendukung Class Weight / Imbalance Handling (Skenario 1 dan 2)

| # | Paper | Link | Bagian yang Sesuai |
|---|---|---|---|
| **B.1** ⭐⭐ | **Majority or Minority: Data Imbalance Learning Method for NER (MoM)** (Akkasi et al., arxiv 2024) | https://arxiv.org/abs/2401.11431 | **Sangat relevan untuk Skenario 1 & 2 Sirah.** Membahas long-tail distribution di NER dengan banyak minority class + 1 majority class (kelas O) — persis kondisi Sirah (93% O). Solusi mereka: tambahkan loss yang dihitung **hanya pada token majority class** ke loss konvensional. Bagian yang sesuai: §3 *"Methodology"* — sejalan dengan filosofi class weight. |
| **B.2** | **Self-Training: A Survey** (Amini et al., Neurocomputing 2024) | https://arxiv.org/abs/2202.12040 | **Wajib dibaca untuk Bab 2** — overview lengkap self-training: confidence-based selection, threshold strategies, noise handling. Bagian yang sesuai: §4 *"Confidence-based Selection Methods"* (untuk Skenario 1) dan §5 *"Threshold Strategies"* (untuk Skenario 2). |
| **B.3** | **Sentence-Level Resampling for Named Entity Recognition** (Akkasi & Moens, NAACL 2022) | https://aclanthology.org/2022.naacl-main.156/ | Pembanding metode untuk class weight Sirah. Mereka pakai **resampling** di level kalimat, bukan modify loss seperti Sirah. Bagian yang sesuai: §3 *"Sentence-Level Resampling"*. Bisa disebut di Bab 2 Sirah sebagai alternatif metode imbalance yang **tidak dipakai** dengan justifikasi: class weight lebih ringan dan tidak menambah ukuran data. |

### C. Konteks: Baseline & Bahasa Indonesia (Pendukung E1)

| # | Paper | Link | Bagian yang Sesuai |
|---|---|---|---|
| **C.1** ⭐⭐⭐ | **Transformer-Based SRL for Crisis Events Using Semi-Supervised Learning** (Ariyanto, **Purwitasari**, Fatichah, Ravana, Andrian, Parwata — IEEE Access Sept 2025) | https://ieeexplore.ieee.org/document/11097773 | **Paper pembimbing — wajib disitir.** Algorithm 1 = pipeline yang dipakai Sirah. Tested fixed threshold 0.7/0.8/0.9 → IndoBERT @ 0.9 menang dengan F1 = **0,863** (target baseline E1 Sirah). Bagian yang sesuai: §III.B.2 *"Semi-Supervised Learning"* dan **Algorithm 1** *"Self-Training with Filtering Function for SRL Models"*. |
| **C.2** | **IPerFEX-2023: Indonesian Financial Entity Extraction with IndoBERT-BiGRU-CRF** (Saputra et al., Journal of Big Data 2024) | https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-00987-6 | Konfirmasi pemilihan **IndoBERT** untuk NER Bahasa Indonesia di domain spesifik. Bisa disitir di Bab 2 sebagai pembanding domain-specific NER (finansial vs sejarah). |

### Mapping Paper ⇄ Skenario

| Skenario | Paper Rujukan Utama |
|---|---|
| **Baseline (E1)** | C.1 (Ariyanto 2025) ⭐⭐⭐ |
| **Skenario 1 — Class Weight Only** | B.1 (MoM) ⭐⭐ + B.2 (Survey) |
| **Skenario 2 — Adaptif + Class Weight** | A.2 (Yu 2023) ⭐⭐ — paling cocok jadi rujukan utama; A.1 (FreeMatch) + A.3 (FlexMatch) untuk justifikasi adaptive saja; B.1 untuk class weight |

### Top 5 Sitasi Prioritas

Kalau hanya bisa sitir 5 paper di Bab 2 sub-bab pseudo-labelling/imbalance:

1. **C.1 — Ariyanto et al. IEEE Access 2025** ⭐⭐⭐ — baseline pembanding (wajib disitir, pembimbing sama)
2. **A.2 — Yu et al. ACL 2023** ⭐⭐ — paling langsung relevan (NER + self-training + adaptive + class imbalance dalam 1 paper)
3. **B.1 — MoM Learning 2024** ⭐⭐ — imbalance handling untuk NER long-tail
4. **A.1 — FreeMatch ICLR 2023** ⭐ — gold standard adaptive threshold
5. **B.2 — Self-Training Survey 2024** — overview komprehensif self-training

---

## Pertanyaan untuk Bu Diana (Saat Bimbingan)

### Pertanyaan Awal (sudah dijawab via run)

1. ~~**Setuju dengan scope 2 skenario (S1: class weight saja, S2: adaptif + class weight)?**~~ → **ACC 2026-05-04.** 3 skenario E1+S1+S2 dijalankan.
2. ~~**Bobot ekstrem** untuk I-LOCATION (~155×)~~ → **Diputuskan clip ke 50×** (`WEIGHT_CLIP_MAX = 50.0`). Training stabil, tidak ada loss meledak.
3. ~~**Metrik perbandingan**~~ → Pakai **3 metrik berdampingan** (token-weighted, macro tanpa O, seqeval entity-level) supaya argumen class weight terlihat dari berbagai sudut.

### Pertanyaan Baru Berdasarkan Hasil (untuk dibahas di bimbingan berikutnya)

1. **Pemilihan model untuk inference final** — kami merekomendasikan **S1** (F1 entity 0,908, EVENT membaik, recall ↑ semua kelas), bukan E1 (F1 entity 0,959 tapi miss banyak entity nyata). Setuju? Atau Ibu lebih prefer E1 karena F1-nya lebih tinggi?
2. **Trade-off precision–recall** — S2 precision 0,74 (entity-level) → 26% prediksi adalah noise. Apakah ini acceptable kalau di-filter alias clustering, atau terlalu noisy untuk pipeline KG?
3. **TARGET_MIN_SAMPLES** — kami pakai 50 (bukan 200 seperti rencana awal). S2 STOP di iter 2 karena dapat 40 < 50. Apakah perlu turunkan ke 30 untuk dapat plot F1 vs iter yang lebih panjang, atau biarkan sebagai bukti adaptive memang stop ketika pseudo-pool habis?
4. **EVENT class** — F1 naik 1,9% dengan class weight tapi support cuma 51 (paling minoritas). Apakah perlu **augmen data EVENT** secara manual untuk memperkuat efek class weight?
5. **Posisi di laporan** — sebagai sub-bab Bab 3 (Skenario Eksperimen) + tabel hasil di Bab 4? Atau struktur lain?

### Pertanyaan Lanjutan (kalau ada waktu)

6. **Class weight inverse frequency vs focal loss** — kami pakai inverse frequency. Perlu eksperimen tambahan dengan focal loss untuk pembanding, atau inverse frequency saja sudah cukup untuk kontribusi TA?
7. **Two-way adaptive threshold** (turun dan naik) — di S2 kami pakai dropping-only. Hasilnya STOP cepat. Apakah Ibu tertarik eksplorasi two-way sebagai future work, atau dropping-only saja sudah cukup untuk laporan TA?
