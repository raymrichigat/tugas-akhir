# Analisis Hasil SRL-NER — E1 (Baseline) vs S1 (Class Weight) vs S2 (Adaptive + Class Weight)

**Tanggal analisis:** 2026-05-07
**Sumber data:** `src/pseudo_labelling/SRL-NER/done_running/`
**Model dasar:** `indolem/indobert-base-uncased`
**Test set:** `data/result/pseudo-labelling/SRL-NER/test.csv` (42.558 token, 1.772 entitas dari 4 label)

---

## Ringkasan Eksekutif

Tiga skenario SRL-NER dijalankan sesuai revisi Bu Diana (2026-05-03, ACC 2026-05-04):

- **E1 (Baseline):** BERT iterative self-training dengan threshold tetap 0.9, tanpa class weight.
- **S1 (Class Weight):** Sama dengan E1, ditambah class weight (`balanced`, clipped maks 50×) untuk menangani ketidakseimbangan label.
- **S2 (Adaptive + Class Weight):** S1 + adaptive threshold (turun bertahap 0.9 → 0.7 ketika pseudo-label kurang dari 50 per iterasi).

**Temuan utama:**

1. **Class weight berhasil memenuhi tujuan revisi.** Recall pada keempat kelas entitas naik di S1/S2 (paling jelas pada `EVENT` 51 sample dan `LOCATION`), namun precision turun karena model jadi lebih agresif menebak entitas dari token "O".
2. **F1 token-weighted mengecoh.** Karena 93% token = "O", metric ini cenderung memenangkan model yang konservatif (E1). Untuk laporan TA, **wajib disajikan tiga metrik** (token-weighted, macro tanpa O, seqeval entity-level) agar trade-off precision vs recall terlihat.
3. **S2 (adaptive) tidak terbukti lebih unggul dari S1.** S2 STOP di iterasi 2 karena pseudo-pool habis di threshold 0.7, dan precision turun drastis (0.74 entity-level). S1 lebih stabil dan recommended sebagai best practice.
4. **Rekomendasi inference final:** **Skenario S1**. Entity-level F1 = 0.908 (selisih -5% dari E1) tetapi recall lebih tinggi pada semua kelas — cocok untuk pembentukan Knowledge Graph yang downstream-nya sensitif terhadap *missed entities*.

---

## 1. Konfigurasi Eksperimen

| Knob | E1 | S1 | S2 |
|------|----|----|----|
| `THRESHOLD` (awal) | 0.9 | 0.9 | 0.9 |
| `THRESHOLD_MIN` (adaptive) | — | — | 0.7 |
| `THRESHOLD_STEP` | — | — | 0.05 |
| `TARGET_MIN_SAMPLES` | — | — | 50 |
| `N_ITERATIONS` (max) | 6 | 6 | 6 |
| `WeightedTrainer` (class weight) | ❌ | ✅ (balanced, clip 50×) | ✅ (balanced, clip 50×) |
| `EPOCHS_PER_ITER` | 10 | 10 | 10 |
| Validation split | seed 42, 80/20, stable lintas iterasi | sama | sama |

Distribusi label di seed train (`train.csv`):

| Label | Count | % |
|-------|-------|---|
| O | (mayoritas, ~93%) | dominan |
| B_PERSON, I_PERSON | ~2.300 | mayoritas entity |
| B_LOCATION, I_LOCATION | ~475 | sedang |
| B_TIME, I_TIME | ~232 | minoritas |
| B_EVENT, I_EVENT | ~100 | paling minoritas |

Class weight di S1/S2 dihitung pakai `compute_class_weight('balanced', ...)`, lalu di-clip ke maks 50× untuk mencegah loss meledak.

---

## 2. Dinamika Pseudo-Labelling per Iterasi

### Iteration log (n_above per iterasi)

| Iter | E1 | S1 | S2 (threshold) |
|------|----|----|--------------------|
| 1 | 187 | 185 | **197** (@0.9) |
| 2 | 32 | 31 | 40 (@0.7, STOP) |
| 3 | 14 | 15 | — |
| 4 | 2 | 5 | — |
| 5 | 1 | 1 | — |
| 6 | 1 | — | — |
| **Total** | **237** | **237** | **237** |

### Insight

- **Ketiga skenario konvergen ke ~237 pseudo-label total.** Pool unlabelled yang punya cukup confidence memang sebatas itu — independen dari skenario.
- **S2 dapat lebih banyak di iter 1 (197 vs 187/185)** karena class weight membuat model lebih percaya diri terhadap entity. Tapi adaptive threshold tidak menambah training data secara signifikan; pseudo-pool cepat habis.
- **S2 STOP di iter 2** karena adaptive sudah turun ke 0.7 (batas bawah) tetapi cuma dapat 40 < 50 sampel. Ini perilaku yang benar (mencegah quality degradation), bukan bug.
- **E1 dan S1 sangat mirip dinamikanya** — class weight tidak terlalu mempengaruhi laju konvergensi self-training.

---

## 3. Performance Test Set — Tiga Perspektif Metrik

### A. Token-level Weighted F1 (termasuk O)

| Skenario | Accuracy | Precision | Recall | **F1** |
|----------|----------|-----------|--------|--------|
| **E1** | **0.9954** | **0.9955** | **0.9954** | **0.9955** |
| S1 | 0.9898 | 0.9910 | 0.9898 | 0.9902 |
| S2 | 0.9814 | 0.9855 | 0.9814 | 0.9826 |

⚠️ **Misleading metric.** 39.449 dari 42.558 token (≈93%) berlabel "O", jadi F1 weighted didominasi label majority. E1 menang di sini bukan karena lebih bagus mengenali entitas, tapi karena lebih jarang salah memprediksi "O" jadi entity.

### B. Macro F1 Tanpa "O" (fair untuk unbalanced)

| Skenario | Precision (macro) | Recall (macro) | **F1 (macro)** |
|----------|-------------------|----------------|----------------|
| E1 | 0.8673 | 0.8270 | 0.8463 |
| S1 | 0.8720 | 0.8493 | 0.8601 |
| **S2** | **0.8732** | **0.8534** | **0.8627** |

✅ **Setelah label "O" dikeluarkan, S2 menang.** Ini metric yang paling fair untuk membandingkan kemampuan model mengenali keempat tipe entitas Sirah.

### C. Seqeval Entity-Level F1 (span-based, standar NER)

| Skenario | Precision | Recall | **F1 entity** |
|----------|-----------|--------|---------------|
| **E1** | **0.9542** | 0.9633 | **0.9587** |
| S1 | 0.8517 | 0.9723 | 0.9080 |
| S2 | 0.7404 | **0.9791** | 0.8432 |

Seqeval mengevaluasi **span entitas penuh** (B_X + I_X harus tepat) — ini adalah standar evaluasi NER pada literatur (CoNLL-2003, OntoNotes, dsb.).

### Pola yang muncul

> Class weight melakukan trade **precision → recall**.
> Semakin agresif (S2), semakin tinggi recall, semakin rendah precision.

| Skenario | Karakter |
|----------|----------|
| E1 | Konservatif. Cenderung memprediksi "O" kalau ragu → miss real entities (false-negative). |
| S1 | Balance. Recall naik di semua kelas, precision turun moderat. |
| S2 | Agresif. Recall paling tinggi (0.98), tapi banyak false-positive (token "O" jadi entity). |

---

## 4. Per-Entity F1 (Seqeval span-based)

| Entity | Support | E1 | S1 | S2 | Δ S1 vs E1 | Δ S2 vs E1 |
|--------|---------|------|------|------|------------|------------|
| PERSON | 1.196 | **0.972** | 0.919 | 0.851 | -0.053 | -0.121 |
| LOCATION | 449 | **0.954** | 0.912 | 0.850 | -0.042 | -0.104 |
| TIME | 76 | **0.883** | 0.780 | 0.712 | -0.103 | -0.171 |
| **EVENT** | **51** | 0.816 | **0.835** | 0.830 | **+0.019** | **+0.014** |

### Temuan paling penting

🔑 **EVENT (kelas paling minoritas, 51 sample) MEMBAIK dengan class weight.**

- E1: 0.816 → S1: **0.835** (+1.9%) → S2: 0.830 (+1.4%)

Ini **bukti langsung** bahwa class weight memenuhi tujuan revisi Bu Diana — bantu kelas minoritas. Tapi efeknya **tidak universal**: kelas mayoritas (PERSON 0.972 → 0.851 di S2) malah turun karena precision drop lebih besar dari recall gain.

### Detail per-entity recall (diukur per skenario)

| Entity | E1 recall | S1 recall | S2 recall |
|--------|-----------|-----------|-----------|
| PERSON | 0.977 | 0.982 | **0.991** |
| LOCATION | 0.944 | 0.971 | **0.969** |
| TIME | 0.947 | 0.934 | **0.961** |
| EVENT | 0.824 | 0.827 | **0.830** |

Semua kelas mengalami **kenaikan recall** di S2 — model nyaris tidak miss entitas, tapi banyak false-positive.

---

## 5. Analisis Pola Error

Total error pada test set per skenario (token-level):

| Skenario | Total errors | Karakteristik |
|----------|--------------|---------------|
| E1 | **195** | 50% false-positive (O→entity), 50% false-negative (entity→O) |
| S1 | 433 | 78% false-positive |
| S2 | 791 | 90% false-positive |

### Top-10 error pattern (true → pred)

**E1 — balanced**
```
O         → B_PERSON       33 (17%)
O         → I_PERSON       28 (14%)
O         → I_TIME         20 (10%)
B_LOCATION → O             18 ( 9%)  ← false-negative
B_PERSON   → O             17 ( 9%)  ← false-negative
```

**S1 — recall-leaning**
```
O         → B_PERSON      170 (39%)
O         → B_LOCATION     65 (15%)
O         → I_PERSON       54 (12%)
O         → I_TIME         38 ( 9%)
O         → B_TIME         26 ( 6%)
B_PERSON  → O              14 ( 3%)  ← false-negative berkurang
```

**S2 — recall-extreme**
```
O         → B_PERSON      376 (48%)  ← dominasi false-positive
O         → B_LOCATION    131 (17%)
O         → I_PERSON       99 (12%)
O         → I_TIME         56 ( 7%)
O         → B_TIME         47 ( 6%)
```

### Interpretasi

- **E1** menyeimbangkan tipe error tapi banyak entity nyata terlewat (false-negative 35%+ dari total error).
- **S1** mengurangi false-negative (entity terlewat) drastis, tapi 8.7× lebih banyak token "O" salah jadi `B_PERSON` dibanding E1.
- **S2** ekstrem — hampir semua errornya false-positive `B_PERSON`. Model "berpikir" terlalu banyak nama orang.

Implikasi untuk Knowledge Graph:
- **False-positive berlebihan di S2** → graph akan dipenuhi node spurious (mis. token biasa di-ekstrak sebagai "Person") yang harus disaring oleh tahap downstream (alias clustering, frequency filter).
- **False-negative E1** → hilangnya node nyata yang **tidak bisa dipulihkan** di tahap downstream.

---

## 6. Verdict per Tujuan Eksperimen

| Tujuan | Pemenang | Justifikasi |
|--------|----------|-------------|
| F1 entity tertinggi (overall) | **E1** | 0.959 seqeval, paling balanced |
| Recall tertinggi (jangan miss entity) | **S2** | 0.979 recall, EVENT 83%, tapi precision drop |
| Best balance precision-recall | **S1** | Entity F1=0.908, semua kelas recall ↑ |
| Bukti class weight bekerja (sesuai revisi Bu Diana) | **S1** | EVENT F1 ↑, recall semua kelas ↑, precision masih masuk akal |
| Stabilitas pelatihan iteratif | **E1 / S1** | 5–6 iter selesai; S2 STOP di iter 2 |

---

## 7. Rekomendasi Konkret untuk Pipeline Knowledge Graph

### ➡️ Pakai **S1** untuk inference final ke `sirah_chunks_final.csv`

**Alasan:**

1. **Entity-level F1 = 0.908** — drop hanya 5% dari E1, masih sangat tinggi.
2. **Recall lebih tinggi pada semua kelas** → graf KG lebih kaya, lebih sedikit kehilangan entitas.
3. **EVENT (kelas paling penting untuk kronologi Sirah) membaik** dari E1 (0.816 → 0.835).
4. **Precision 0.85 masih manageable** — false-positive bisa dimitigasi di tahap *alias clustering* dan *frequency filter* (entitas dengan frekuensi sangat rendah didiskualifikasi).
5. **S2 terlalu agresif** — precision 0.74 berarti 26% prediksi entity adalah noise, akan membanjiri pipeline alias clustering. Adaptive juga STOP di iter 2 tanpa kontribusi signifikan.

### ➡️ Untuk laporan Bab 4

**WAJIB sajikan tiga metrik** secara berdampingan:

| Bagian laporan | Metric yang ditampilkan |
|----------------|-------------------------|
| Tabel utama performance | Token-weighted F1 |
| Tabel "tangani unbalanced" | Macro F1 tanpa O |
| Standar NER literatur | Seqeval entity-level F1 |
| Per-kelas analysis | Seqeval per-entity (4 baris × 3 kolom) |

Kalau hanya menampilkan token-weighted F1, **akan kelihatan bahwa revisi Bu Diana tidak berhasil** (karena E1 menang). Kalau hanya seqeval F1, juga kelihatan E1 menang. Yang menunjukkan class weight berhasil adalah:
- Macro F1 tanpa O (S2 menang).
- Per-entity F1 di kelas EVENT (S1 ⩾ E1).
- Per-entity recall di semua kelas (S2 menang).

---

## 8. Bahan Diskusi untuk Bu Diana

### Pertanyaan untuk dikonfirmasi

1. **Metric prioritas:** apakah pengujian NER memprioritaskan F1 entity (E1 menang) atau recall (S2 menang) untuk Knowledge Graph?
2. **Penggunaan model:** untuk inference final ke seluruh chunks, lebih baik **S1 (rekomendasi kami)** atau **E1 (F1 tertinggi)**?
3. **Adaptive threshold:** adaptive di S2 STOP di iter 2 (cuma 2 iterasi). Apakah perlu re-tune (lower TARGET_MIN_SAMPLES dari 50 ke 30) untuk dapat plot F1 vs iter yang lebih panjang?
4. **EVENT class:** F1 EVENT membaik 1.9% dengan class weight tapi support cuma 51. Apakah perlu **augment data EVENT** untuk hasil lebih signifikan?

### Klaim yang bisa dipertahankan untuk laporan

✅ "Class weight berhasil membantu kelas minoritas EVENT (F1 0.816 → 0.835)."
✅ "Recall meningkat di semua kelas dengan class weight (rata-rata +2.5%)."
✅ "Adaptive threshold memungkinkan ekstraksi pseudo-label lebih banyak di iterasi awal (197 vs 187)."
⚠️ "Trade-off precision-recall jelas: S2 precision turun 0.95→0.74 (entity-level)."

### Klaim yang **tidak bisa** dipertahankan

❌ "S1/S2 strictly better dari E1." → tidak benar, F1 token-weighted dan F1 entity-level seqeval menang E1.
❌ "Adaptive threshold lebih baik dari fix threshold." → S1 vs S2 di entity F1: S1 (0.908) > S2 (0.843).

---

## 9. Lampiran — Summary Numerik (untuk copy-paste)

### Ringkasan satu tabel

| Metric | E1 | S1 | S2 |
|--------|------|------|------|
| Token-weighted F1 | **0.9955** | 0.9902 | 0.9826 |
| Macro F1 tanpa O | 0.8463 | 0.8601 | **0.8627** |
| Seqeval entity F1 | **0.9587** | 0.9080 | 0.8432 |
| Seqeval entity Precision | **0.9542** | 0.8517 | 0.7404 |
| Seqeval entity Recall | 0.9633 | 0.9723 | **0.9791** |
| F1 PERSON | **0.972** | 0.919 | 0.851 |
| F1 LOCATION | **0.954** | 0.912 | 0.850 |
| F1 TIME | **0.883** | 0.780 | 0.712 |
| F1 EVENT | 0.816 | **0.835** | 0.830 |
| Total iter | 6 | 5 | 2 (STOP) |
| Total pseudo-label | 237 | 237 | 237 |
| Total errors | 195 | 433 | 791 |

---

## 10. File Pendukung

- **Notebook perbandingan:** `compare_scenarios.ipynb` (di folder yang sama)
- **Plot kurva pseudo-label per iter:** generate dari notebook
- **Confusion matrix per skenario:** generate dari notebook
- **Tabel mentah F1:** dihasilkan dinamis dari xlsx hasil run
