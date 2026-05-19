# Bimbingan SRL-NER — Bahan Diskusi Bu Diana

> **Tanggal revisi terakhir:** 2026-05-20 (post-bimbingan 2026-05-16)
> **Status skenario:** Plan 3-skenario sudah **approved Bu Diana di bimbingan 2026-05-16**. Deadline S3: **29 Mei 2026**.

---

## 0. Ringkasan Status

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa class weight, tanpa contrastive, tanpa augmentation | ✅ Selesai (Seq F1 entity = 0.959, reuse hasil E1 lama 2026-05-07) |
| **S2 — Contrastive Learning + Baseline** | S1 + supervised contrastive loss (SCL + JSCL sentence-level, paper Dewabharata et al.) | ✅ Selesai 2026-05-14/15 (S2a SCL final 0.950 / peak 0.953, S2b JSCL final 0.933 / peak 0.940) |
| **S3 — Sentence-based Augmentation + S2** | Tune λ_C sweep di S2 SCL → pilih winner → Mention Replacement augmentation (Dai & Adel 2020) | ⏳ Plan baru post-2026-05-16, deadline **29 Mei 2026** |

**Filosofi skenario baru:** layer-by-layer. S2 = S1 + contrastive. S3 = S2 + augmentation. Tujuannya supaya kontribusi tiap komponen terhadap F1 kelas minoritas (terutama EVENT) bisa diisolasi dengan jelas.

**Update post-bimbingan 2026-05-16:** Plan S3 di-revisi — sebelum jalankan augmentation, tune dulu hyperparameter `λ_C` (0.1, 0.2, 0.3) untuk recover gap entity-level S2 (0.95) vs S1 (0.959). Augmentation di-stack di atas winner λ_C tuning, bukan di atas λ_C=0.3 default.

Detail teknis lengkap di `../skenario/srl_ner.md`. Outcome bimbingan mentah di `2026-05-16_outcome.md`.

---

## 1. Permasalahan: Distribusi Label Sangat Tidak Seimbang

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

→ Inilah yang melatarbelakangi **S2 (contrastive)** dan **S3 (augmentation)** sebagai layer tambahan di atas S1.

---

## 2. S1 — Baseline (Sudah Selesai)

**Definisi:** notebook SRL-NER apa adanya, knob default Bu Diana (mengikuti paper Ariyanto 2025).

```python
THRESHOLD       = 0.9      # fix
SAMPLING_RATE   = 1.0
MIN_ENTITY_CONF = None
class_weights   = None     # ← tidak ada handling imbalance
contrastive     = False    # ← tidak ada SCL/JSCL
augmentation    = False    # ← tidak ada augmentasi
MAX_ITERATIONS  = 6
```

### 2.1 Hasil Aktual S1 (= reuse E1 lama, run 2026-05-07)

**Dinamika self-training:** 6 iterasi selesai (n_above per iter: 187 → 32 → 14 → 2 → 1 → 1, total 237 pseudo-label).

**Performance test set (42.558 token, 1.772 entitas):**

| Metric | Nilai |
|---|---|
| F1 token-weighted (incl. O) | 0.9955 |
| F1 macro tanpa O | 0.8463 |
| F1 entity-level seqeval | **0.9587** |
| Precision entity | 0.9542 |
| Recall entity | 0.9633 |

**F1 per-entitas (seqeval span-based):**

| Entity | Support | F1 S1 |
|---|---:|---:|
| PERSON | 1.196 | 0.972 |
| LOCATION | 449 | 0.954 |
| TIME | 76 | 0.883 |
| **EVENT** | **51** | **0.816** ⚠️ |

**Catatan:**
- F1 entity-level **0.9587** — melampaui target paper Ariyanto (0.863).
- Tapi **F1 EVENT = 0.816** masih paling rendah → motivasi S2/S3.

---

## 3. S2 — Contrastive Learning + Baseline (Belum Run)

**Definisi:** S1 + supervised contrastive loss (SCL atau JSCL) di training. Threshold tetap fix 0.9. Yang berubah **hanya loss function**.

### 3.1 Motivasi (Bahasa untuk Skrip Bimbingan)

> Class weight (yang sudah dicoba di skenario lama) bekerja di level **loss CrossEntropy** — ia memberi bobot lebih besar pada error di kelas minoritas. Tapi representasi token kelas minoritas di **embedding space** masih bisa "tertarik" ke kelas mayoritas `O` karena dominansinya 93%.

> Contrastive learning attack di level berbeda: **representasi**. Token sekelas (mis. semua `B-EVENT`) ditarik supaya embedding-nya mirip; token beda kelas didorong menjauh. Hasilnya: ruang embedding lebih disiplin per-kelas → klasifikasi minoritas (terutama EVENT) lebih akurat.

### 3.2 Variasi yang Dibandingkan

**Paper rujukan utama:** `Contrastive_Learning.pdf` (Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo — *Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts*). Penulis sebagian besar dari ITS. File ada di root repo.

Paper ini punya 3 strategi contrastive (BAL/SCL/JSCL). Sirah pakai **SCL + JSCL** (sesuai permintaan Bu Diana putaran 3, BAL skip untuk simplifikasi).

| Variasi | Formulasi loss (Eq. paper) | Catatan adaptasi NER |
|---|---|---|
| **SCL (Strict Supervised Contrastive Learning)** | Eq. 2–3: positive pair = sample dengan label set identik, optimized via InfoNCE | Sirah token-level: positive pair = token dengan label BIO yang sama (mis. dua `B-EVENT`). Implementasi straightforward. |
| **JSCL (Jaccard Similarity Contrastive Learning)** | Eq. 4–6: weighted InfoNCE dengan `α_ij = J_ij / (Σ J_ik + ε)`, `J_ij = |L_i ∩ L_j| / |L_i ∪ L_j|` | **Adaptasi: sentence-level Jaccard** (lock-in 2026-05-11). Tiap kalimat punya bag-of-labels BIO (exclude `O`), Jaccard antar kalimat → weighted InfoNCE pada embedding kalimat (mean-pool). |

**Two-phase framework (dari paper, cocok untuk pipeline Sirah self-training):**
- **Phase 1:** train encoder IndoBERT dengan `L_SCL` atau `L_JSCL` di labeled+unlabeled data.
- **Phase 2:** classifier head di-fine-tune dengan supervised loss + pseudo-label loss (Eq. 7–9 paper). Total loss `L_total = L_L + λ · L_U`.

Detail formulasi + sketch kode → `../skenario/srl_ner.md` §3.3, §3.6.

### 3.3 Knob Hyperparameter (Estimasi Awal)

| Knob | Range | Catatan |
|---|---|---|
| `lambda` (λ) | 0.1–0.5 | Bobot relatif L_SCL terhadap L_CE |
| `tau` (τ) | 0.07–0.5 | Temperature di softmax contrastive |
| `batch_size` | ≥ 32 | Perlu cukup besar untuk positives/negatives |
| Knob S1 lainnya | sama | Threshold, sampling_rate, dll tidak berubah |

### 3.4 Risiko

- Tambah hyperparameter (λ, τ) → perlu sweep mini.
- Memori lebih → mungkin perlu kurangi batch atau pakai gradient checkpointing.
- Definisi JSCL belum konkret → wajib konfirmasi paper sebelum coding.

### 3.5 Effort

4-6 jam coding (per variasi SCL/JSCL) + 3-4 jam Colab GPU.

### 3.6 Yang Diharapkan

- F1 entity-level **stabil atau sedikit naik** dari S1 (0.959).
- **F1 EVENT naik signifikan** dari 0.816 → target ≥ 0.85.
- Recall semua kelas naik tanpa precision turun drastis (vs S1 lama class weight yang precision turun 5–10%).

---

## 4. S3 — Sentence-based Augmentation + S2 (Belum Run)

**Definisi:** S2 + augmentasi data — generate kalimat baru fokus ke kelas minor (`B-EVENT`, `I-EVENT`, `I-LOCATION`, opsional `B-TIME`/`I-TIME`) lalu append ke train set sebelum training.

### 4.1 Motivasi

> Class weight dan contrastive learning bekerja di model — tapi sample kalimat EVENT memang **sedikit** (support cuma 51 di test). Augmentasi sentence-based menambah **variasi konteks** kelas minor tanpa duplikasi murni (yang berisiko overfitting).

Bu Diana putaran 3 (2026-05-07): *"oversampling bisa tapi susah. Augmentasi sentence-based (1 kalimat yang fokusnya ke minor) ditambahkan ke data train"*.

### 4.2 Strategi Augmentasi (Kandidat)

| Strategi | Cara kerja | Kelas target | Effort |
|---|---|---|---|
| **Template substitution** | Ganti entity di kalimat existing (mis. ganti nama PERSON di kalimat EVENT) dengan entity sekelas dari pool | EVENT, TIME, LOCATION | Rendah |
| **Context expansion** | Tambah kalimat anchor di sebelum/sesudah yang menyebut entity minor | EVENT | Sedang |
| **Back-translation (id→en→id)** | Translate kalimat EVENT ke English, lalu translate balik | Semua, terutama EVENT | Sedang (butuh API) |
| **GPT paraphrase** | Pakai LLM untuk paraphrase kalimat EVENT, makna sama struktur beda | EVENT, TIME | Sedang-tinggi (ironis: LLM-NER dibatalkan tapi LLM dipakai untuk augment) |

**Strategi final:** menunggu paper referensi dari teman + konfirmasi Bu Diana.

### 4.3 Knob Hyperparameter

| Knob | Default | Fungsi |
|---|---|---|
| `n_augment_per_minor_sentence` | 1–3 | Berapa kalimat augmentasi per kalimat original |
| `target_classes` | `["B-EVENT", "I-EVENT", "I-LOCATION"]` | Kelas yang ditarget |
| `augmentation_strategy` | TBD | Pilih 1 atau kombinasi dari §4.2 |

### 4.4 Risiko

- Kualitas augmented sentence sangat tergantung strategi (template bisa hasilkan kalimat tidak natural, GPT butuh validasi).
- **Semantic drift** — entity dipindah ke konteks yang salah secara sejarah Sirah (mis. "Perang Badar" muncul di konteks Madinah pasca-Fathu Makkah). Perlu validasi manual sampel 20–30 kalimat sebelum di-train.

### 4.5 Effort

3-4 jam (template) atau 6-8 jam (back-translation/GPT) + 2-3 jam Colab.

### 4.6 Yang Diharapkan

- F1 EVENT tertinggi dari ketiga skenario (target ≥ S2).
- F1 entity-level tetap di sekitar 0.95+.

---

## 5. Pertanyaan untuk Bu Diana — dengan Jawaban dari Bimbingan 2026-05-16

### 5.1 Klarifikasi Skenario Baru

1. **Setuju dengan restrukturisasi skenario** (S1=baseline murni, S2=baseline+contrastive, S3=S2+augmentation)?
   → ✅ **Approved**. Plan 3-skenario di-acc Bu Diana.

2. **S2 — SCL vs JSCL**: cukup salah satu, atau wajib bandingkan kedua varian?
   → ✅ **Wajib dua-duanya** (sudah dijalankan). Hasil: SCL > JSCL konsisten ~+0.01.

3. **S3 — strategi augmentasi**: template substitution, back-translation, atau GPT?
   → 🔄 **Mention Replacement (Dai & Adel 2020)** dipilih. Augmented data sudah siap. **Update post-bimbingan**: tune λ_C dulu sebelum augmentation untuk close the gap entity-level S2 vs S1.

4. **Apakah perlu skenario class-weight murni** sebagai pembanding pure?
   → 🟡 **Tidak dibahas eksplisit**. Tetap di-arsip di `legacy_class_weight_adaptive/` sebagai studi pendahuluan / ablation pembanding di Bab 4.

### 5.2 Posisi di Laporan

5. **Bab 4 — klaim utama** S1+S2+S3 vs class-weight/adaptive lama?
   → 🟡 **Tidak dibahas eksplisit di bimbingan**. Default plan: S1+S2+S3 jadi klaim utama, class-weight/adaptive jadi sub-bab "Studi Pendahuluan".

6. **F1 EVENT** masih jadi metrik kunci? Atau pindah ke macro F1 tanpa O?
   → 🟡 **Tidak dibahas**. Default: tetap pakai keduanya (Seq F1 entity-level + per-class breakdown EVENT).

### 5.3 Timeline

7. Urutan prioritas: **S1+S2 cukup**, **S1+S3**, atau **wajib semua**?
   → ✅ **Wajib semua** (S1+S2+S3) dengan deadline **29 Mei 2026**.

8. **Boleh start coding S2 sebelum dapat paper JSCL dari teman**?
   → ✅ Sudah selesai (paper Dewabharata et al. dipakai, sentence-level Jaccard adaptasi).

### 5.4 Bahan Diskusi dengan Rujukan Paper

- Justifikasi SCL untuk imbalanced NER: rujuk **Khosla et al. NeurIPS 2020** + **ContrastNER 2023**.
- Justifikasi augmentasi sentence-based NER: rujuk **Dai & Adel COLING 2020** + **DAGA EMNLP 2020**.
- Justifikasi baseline IndoBERT @ 0.9: rujuk **Ariyanto et al. IEEE Access 2025** — target F1 0.863, Sirah sudah mencapai 0.9587.

### 5.5 Pertanyaan/Tambahan Baru dari Bu Diana di Bimbingan 2026-05-16

**Graf:**
- ⚠️ Centrality jangan hanya untuk node Person — **Event juga harus punya centrality** (degree, betweenness, closeness, PageRank). Ditambah analisis "bagaimana node lain berpengaruh ke event" (sudut pandang non-Event ke Event).
- ⚠️ Community detection — interpretasi lebih dalam: arti modularity Q konkret, interpretasi tiap komunitas, **wordcloud per-komunitas**, kenapa node X masuk komunitas Y, tujuan terbentuknya komunitas.
- ⚠️ Studi kasus 5 event — tambah **analisis event yang berelasi** (mis. Hudaibiyah → event apa di P11 yang co-occur atau punya relasi overlap).
- ⚠️ Visualisasi prefer **Neo4j live** (bukan PNG static).

**SRL-NER:**
- ⚠️ **LLM verb extraction** — lempar Sirah ke LLM, ekstrak kata kerja/kata terkait event → tambahkan sebagai Event entity (antisipasi support EVENT yang masih kecil).
- ⚠️ **Frekuensi entitas per period** — amati frekuensi kemunculan PERSON/EVENT/LOCATION per periodisasi → justifikasi pengaruh.

**Bimbingan berikutnya:**
- Pipeline harus running end-to-end dengan output SRL-NER (bukan manual labelling).
- **Comparison report** SRL-NER vs manual labelling (jangan lupa dibedakan).
- Mulai pembukuan per-Bab sesuai update terbaru.

---

## 6. Action Item Post-Bimbingan 2026-05-16 (Deadline 29 Mei 2026)

1. ✅ Plan 3-skenario approved Bu Diana — proceed.
2. ⏳ **Tune λ_C sweep** (0.1, 0.2, 0.3) di S2 SCL → pilih winner berdasarkan Seq F1 entity (~6-8 jam GPU T4 di Colab).
3. ⏳ **Run S3** (winner λ_C + Mention Replacement augmentation Dai & Adel 2020) (~3-4 jam GPU).
4. ⏳ **Inference NER terbaik** ke seluruh `sirah_chunks_final.csv` → regenerate `nodes_v3.csv` + `edges_v3.csv`.
5. ⏳ **Comparison report**: SRL-NER vs manual labelling (jumlah entitas per-tipe, coverage event, dll).
6. ⏳ **Centrality untuk node Event** (revisi tambahan Bu Diana).
7. ⏳ **Wordcloud per-komunitas** (13 Louvain) + interpretasi semantik.
8. ⏳ **Q-value interpretasi** + analisis "kenapa node X masuk komunitas Y".
9. ⏳ **Analisis event-related** untuk 5 case study (event co-occur per period + relasi overlap).
10. ⏳ **Frekuensi entitas per-period** (tabel: tiap entitas muncul di period mana, berapa kali).
11. ⏳ **LLM verb extraction** → tambah Event entity (prompt template + run sample, scale up jika workable).
12. ⏳ **Update CLAUDE.md** + mulai pembukuan Bab 4.

Detail mentah outcome bimbingan: `2026-05-16_outcome.md`. Detail propagasi: `revisi_dosen.md` Putaran 5.

---

## 7. Arsip — Skenario Lama (Class Weight + Adaptive Threshold)

> **Status:** Sudah dijalankan 2026-05-07 tapi **didrop dari klaim utama TA** per restrukturisasi 2026-05-11. Tetap disimpan di `done_running/legacy_class_weight_adaptive/` sebagai studi pendahuluan / ablation pembanding.

### 7.1 Skenario Lama yang Sudah Dijalankan

| Skenario lama | Komponen | F1 entity | F1 EVENT |
|---|---|---:|---:|
| E1 lama (= S1 baru) | Fix 0.9, no CW | **0.959** | 0.816 |
| S1 lama | Fix 0.9 + class weight inverse freq (clip 50×) | 0.908 | 0.835 |
| S2 lama | Adaptive 0.9→0.7 + class weight | 0.843 | 0.830 |

### 7.2 Temuan dari Skenario Lama

✅ **Class weight membantu kelas minoritas EVENT** (F1 0.816 → 0.835, +1.9%).
✅ **Recall meningkat di semua kelas dengan class weight** (S1 lama: PERSON +0.5%, LOCATION +2.7%, EVENT +0.3%).
✅ **Adaptive threshold memungkinkan ekstraksi 197 pseudo-label di iter-1** (vs 187 baseline).
✅ **S2 lama adaptive konvergen lebih cepat** (2 iter vs 6 iter).

❌ Trade-off precision-recall terlalu tajam: S1 lama precision turun 5–10%, S2 lama precision drop ke 0.74 (26% noise).
❌ F1 entity-level S1/S2 lama < E1 lama → class weight murni tidak strictly better.

### 7.3 Kenapa Didrop dari Klaim Utama?

- Bu Diana putaran 3 minta attack imbalance di level lain (representasi via contrastive, data via augmentation).
- Skenario lama menambah skenario di atas E1 (jadi 5 skenario total kalau gabung putaran 3) → terlalu banyak, sulit isolasi efek tiap komponen.
- Skenario baru lebih bersih: 1 layer = 1 kontribusi.

### 7.4 Posisi Hasil Lama di Laporan

- Bab 4: bisa dijadikan **sub-bab "Studi Pendahuluan"** sebelum sub-bab "Skenario Utama (S1/S2/S3)".
- Klaim yang bisa dipertahankan: "*Class weight inverse frequency menaikkan F1 EVENT +1.9% di Sirah, tapi menurunkan precision overall. Hal ini memotivasi pendekatan berbeda — contrastive learning (S2) di level representasi dan sentence augmentation (S3) di level data*".

### 7.5 File Hasil Lama

- `done_running/S1_baseline/` (= E1 baseline lama, reuse jadi S1 baru — di-rename dari `baseline/`)
- `done_running/legacy_class_weight_adaptive/S1_classweight/` (skenario lama class weight)
- `done_running/legacy_class_weight_adaptive/S2_adaptive/` (skenario lama adaptive + CW)
- `done_running/legacy_class_weight_adaptive/analisis_skenario_srlner.md`
- `done_running/legacy_class_weight_adaptive/compare_scenarios.ipynb`
- `done_running/legacy_class_weight_adaptive/README.md` (penjelasan arsip)

---

## 8. Referensi Paper Pendukung

### 8.A. Untuk S1 (Baseline)

| # | Paper | Link |
|---|---|---|
| **A.1** ⭐⭐⭐ | **Transformer-Based SRL for Crisis Events Using Semi-Supervised Learning** (Ariyanto, Purwitasari, Fatichah, Ravana, Andrian, Parwata — IEEE Access Sept 2025) — paper pembimbing | https://ieeexplore.ieee.org/document/11097773 |
| **A.2** | **Self-Training: A Survey** (Amini et al., Neurocomputing 2024) | https://arxiv.org/abs/2202.12040 |

### 8.B. Untuk S2 (Contrastive Learning)

| # | Paper | Link |
|---|---|---|
| **B.1** ⭐⭐⭐ | **Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts** (Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo) — **paper utama S2** (SCL + JSCL formulasi, framework two-phase) | `Contrastive_Learning.pdf` (lokal di root repo) |
| **B.2** ⭐⭐ | **Supervised Contrastive Learning** (Khosla et al., NeurIPS 2020) — foundational SCL | https://arxiv.org/abs/2004.11362 |
| **B.3** ⭐ | **CONTaiNER: Few-Shot NER via Contrastive Learning** (Das et al., ACL 2022) — contrastive untuk NER token-level | https://aclanthology.org/2022.acl-long.439/ |
| **B.4** | **ContrastNER: Contrastive-based Prompt Tuning for Few-shot NER** (Layegh et al., 2023) — supporting | TBD |

### 8.C. Untuk S3 (Sentence Augmentation NER)

| # | Paper | Link |
|---|---|---|
| **C.1** ⭐⭐ | **An Analysis of Simple Data Augmentation for NER** (Dai & Adel, COLING 2020) | https://aclanthology.org/2020.coling-main.343/ |
| **C.2** ⭐ | **DAGA: Data Augmentation with a Generation Approach** (Ding et al., EMNLP 2020) | https://aclanthology.org/2020.emnlp-main.488/ |
| **C.3** | **Sentence-Level Resampling for NER** (Akkasi & Moens, NAACL 2022) | https://aclanthology.org/2022.naacl-main.156/ |

Detail bahasan + Top 5 prioritas → lihat `../skenario/srl_ner.md` §6.
