# Skenario SRL-NER — S1 / S2 / S3

> **Tanggal revisi terakhir:** 2026-05-20 (post-bimbingan 2026-05-16)
> **Konteks revisi:** Plan 3-skenario sudah **approved Bu Diana di bimbingan 2026-05-16**. S3 di-revisi dengan λ_C tuning sebelum augmentation. Deadline S3: **29 Mei 2026**.

## 0. Ringkasan Skenario

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa handle imbalance, tanpa contrastive, tanpa augmentation | ✅ Selesai (Seq F1 entity = 0.959, reuse hasil E1 lama 2026-05-07) |
| **S2 — Contrastive Learning + Baseline** | S1 + supervised contrastive loss (SCL + JSCL sentence-level, λ_C=0.3) | ✅ Selesai 2026-05-14/15 (S2a SCL final 0.950 / peak 0.953, S2b JSCL final 0.933 / peak 0.940) |
| **S3 — λ_C Tuning + Mention Replacement Augmentation** | (1) Sweep λ_C ∈ {0.1, 0.2, 0.3} di S2 SCL → pilih winner; (2) S2 winner + Mention Replacement (Dai & Adel 2020) | ⏳ Deadline **29 Mei 2026** |

**Filosofi:** layer-by-layer — S2 menambah contrastive ke S1, S3 menambah λ_C tuning + augmentation ke S2. Tujuannya supaya kontribusi tiap komponen ke F1 kelas minoritas (terutama EVENT) bisa diisolasi.

**Latar belakang revisi 2026-05-11 (skema awal):** skenario lama (E1+S1 class-weight + S2 adaptive+CW) sudah dijalankan dan menunjukkan class weight murni belum memuaskan untuk EVENT (F1 stuck di 0.83). Bu Diana putaran 3 menyarankan contrastive learning + sentence augmentation. Kami memutuskan **restrukturisasi total** supaya skema skenario lebih bersih: 1 skenario = 1 layer kontribusi.

**Latar belakang revisi 2026-05-20 (S3 plan baru):** S2 selesai run dengan λ_C=0.3 default, hasil Seq F1 entity (~0.95) sedikit di bawah S1 baseline (0.959). Hipotesis: λ_C=0.3 terlalu agresif → trade-off entity boundary vs token classification. **Sebelum lompat ke augmentation**, S3 dimulai dengan **λ_C sweep** (0.1, 0.2, 0.3) di SCL untuk close the gap. Setelah dapat winner λ_C, baru di-stack augmentation di atasnya. Plan 3-skenario ini approved Bu Diana di bimbingan 2026-05-16.

---

## 1. Kondisi Saat Ini (Baseline = S1)

**Notebook:** `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9.ipynb` (+ varian Colab/Kaggle)
**Pipeline:** BERT iterative self-training (template Bu Diana, dengan Fix A–H untuk Sirah BIO).

### 1.1 Knob yang sudah ada (dari refactor 2026-04-16)

| Knob | Default S1 | Fungsi |
|---|---|---|
| `THRESHOLD` | **0.9** (fix) | Average entity confidence per kalimat ≥ THRESHOLD → masuk pseudo-label |
| `MIN_ENTITY_CONF` | `None` | Reject kalimat kalau ada satu entity dgn conf < nilai ini |
| `SAMPLING_RATE` | `1.0` | Pakai top-K% kalimat confidence tertinggi (1.0 = semua above) |
| `MIN_NEW_SAMPLES` | `0` | Early-stop kalau pseudo-label baru < threshold |
| `aggregation_strategy` | `"simple"` | Strategi agregasi sub-token |
| `MAX_ITERATIONS` | 6 | Jumlah iterasi maksimal |

> Semua knob mengikuti default kode Bu Diana (`BERT_Only_Percobaan_1_Argument_0.9.ipynb`) dan paper Ariyanto et al. 2025.

### 1.2 Distribusi Label Train (`train.csv`, 101.021 token)

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

→ Inilah yang melatarbelakangi **S2 (contrastive)** dan **S3 (augmentation)** sebagai layer tambahan di atas S1.

---

## 2. S1 — Baseline (Fix Threshold, Tanpa Handle Imbalance)

### 2.1 Definisi

S1 = notebook SRL-NER apa adanya, knob default:

```python
THRESHOLD       = 0.9       # fix
SAMPLING_RATE   = 1.0       # pakai semua above 0.9
MIN_ENTITY_CONF = None      # tidak ada filter tambahan
class_weights   = None      # tidak ada handling imbalance
contrastive     = False     # tidak ada SCL/JSCL
augmentation    = False     # tidak ada sentence augmentation
MAX_ITERATIONS  = 6
```

### 2.2 Tujuan

- Replikasi metode paper Ariyanto 2025 (IndoBERT @ threshold 0.9)
- F1 baseline harus mendekati **0.863** (angka paper Ariyanto)
- Berfungsi sebagai **kontrol murni** untuk membandingkan efek S2 (contrastive) dan S3 (augmentation)

### 2.3 Hasil Aktual S1 (= E1 lama, run 2026-05-07)

Hasil run baseline E1 2026-05-07 **direuse sebagai S1** (skenario teknisnya identik). Tidak perlu run ulang.

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
- F1 entity-level **0.9587** — sangat tinggi, melampaui target paper Ariyanto (0.863).
- Tapi **F1 EVENT = 0.816** masih paling rendah dari 4 kelas → motivasi S2/S3.

**Lokasi output:** `src/pseudo_labelling/SRL-NER/done_running/S1_baseline/` (di-rename dari `baseline/` per 2026-05-11).

### 2.4 File yang Berubah

Tidak ada — tinggal reuse hasil run sebelumnya.

### 2.5 Effort

0 jam coding, 0 jam Colab.

---

## 3. S2 — Contrastive Learning + Baseline

### 3.1 Definisi

S2 = S1 + supervised contrastive loss (SCL atau JSCL) di training. Threshold tetap fix 0.9, tidak ada class weight, tidak ada augmentation. Yang berubah **hanya loss function**.

### 3.2 Motivasi

Class weight di skenario lama (drop) bekerja di level loss (CE) — tapi representasi token kelas minoritas masih bisa "tertarik" ke kelas mayoritas `O`. Contrastive learning attack di level berbeda: **representasi**.

> Contrastive learning menarik representasi token sekelas menjadi mirip dan mendorong token beda kelas menjauh → struktur ruang embedding lebih disiplin → klasifikasi minoritas (EVENT) lebih akurat tanpa mengubah threshold pseudo-labelling.

### 3.3 Variasi yang Dibandingkan

**Paper rujukan utama:** Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo — *Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts* (file lokal: `Contrastive_Learning.pdf` di root repo, sebagian besar penulis dari ITS).

Paper ini mendefinisikan 3 strategi contrastive untuk multi-label classification. **Sirah pakai SCL + JSCL** (sesuai permintaan Bu Diana putaran 3, dan BAL tidak dipakai untuk simplifikasi).

| Variasi | Formulasi loss (Eq. paper) | Adaptasi ke NER token-level |
|---|---|---|
| **SCL (Strict Supervised Contrastive Learning)** | Eq. 2–3 paper: `p_ij = exp(sim(z_i,z_j)/τ) / Σ_k exp(sim(z_i,z_k)/τ)`, `L_SCL = Σ_i (-1/|P(i)|) Σ_{j∈P(i)} log p_ij` di mana `P(i)` = anchor `i` dan sample sekelas dalam batch. | Positive pair = token dengan label BIO yang **sama persis** (mis. dua token `B-EVENT`). Negative = token lain dalam batch. InfoNCE klasik, paling mudah implementasi. |
| **JSCL (Jaccard Similarity Contrastive Learning)** | Eq. 4–6 paper: `L_JSCL = -(1/B) Σ_i Σ_j α_ij log(exp(x̂_i·x̂_j/τ) / Σ_k exp(x̂_i·x̂_k/τ))` dengan weighting `α_ij = J_ij / (Σ_k J_ik + ε)` dan `J_ij = |L_i ∩ L_j| / |L_i ∪ L_j|`. | **Adaptasi: sentence-level Jaccard** (lock-in 2026-05-11). Tiap kalimat punya bag-of-labels BIO `{B-PERSON, I-PERSON, B-EVENT, ...}`, Jaccard antar kalimat → weighted InfoNCE pada embedding kalimat (mean-pool). Detail di §3.6.1. |

**Two-phase framework (mengikuti paper):**
- **Phase 1 — Contrastive pre-training:** train IndoBERT encoder dengan `L_SCL` atau `L_JSCL` di labeled+unlabeled data (encoder belajar representasi yang disiplin per-kelas).
- **Phase 2 — Pseudo-label + fine-tune:** classifier head di-fine-tune dengan supervised loss + pseudo-label loss (Eq. 7–9 paper):
  - `L_L = (1/C) Σ_c BCE(y_c, σ(z_c))` (labeled)
  - `L_U = (1/C) Σ_c (p_c > θ) · BCE(y_c, σ(z_c))` (pseudo-labeled, di mana θ = threshold confidence)
  - `L_total = L_L + λ · L_U`

Untuk Sirah NER, Eq. 7–9 perlu adaptasi: BCE → CrossEntropy karena single-label per token. Sisanya bisa direuse.

### 3.4 Knob Hyperparameter (estimasi awal — final menunggu paper)

| Knob | Range awal | Catatan |
|---|---|---|
| `lambda` (λ, bobot SCL) | 0.1–0.5 | Bobot relatif L_SCL terhadap L_CE |
| `tau` (τ, temperature) | 0.07–0.5 | Temperature di softmax contrastive |
| `batch_size` | ≥ 32 | Perlu cukup besar untuk positives/negatives sampling |
| `MAX_ITERATIONS` | 6 | Sama dengan S1 |
| Knob S1 lainnya | sama | Threshold, sampling_rate, dll tidak berubah |

### 3.5 Integrasi ke Pipeline Existing

- Custom Trainer subclass yang menambah loss SCL/JSCL di atas hidden states sebelum classifier head.
- Pseudo-labelling loop tetap sama dengan S1 (THRESHOLD fix 0.9, dropping per-iter via `filter_threshold`).
- Output yang berubah: `iteration_log.csv` perlu kolom tambahan (`lambda_scl`, `tau`, `loss_ce`, `loss_scl`).

### 3.6 Sketsa Kode

**SCL — straightforward (positive pair = token same label):**

```python
import torch, torch.nn.functional as F
from transformers import Trainer

def scl_loss_tokens(hidden, labels, tau=0.1):
    """
    hidden : [B, T, H] token embeddings dari hidden_states[-1]
    labels : [B, T] BIO label id, -100 = ignore (special tokens / sub-word)
    """
    h = hidden.reshape(-1, hidden.size(-1))           # [N, H]
    y = labels.reshape(-1)                             # [N]
    mask_valid = y != -100
    h, y = h[mask_valid], y[mask_valid]               # buang ignore tokens

    h = F.normalize(h, dim=-1)
    sim = h @ h.T / tau                                # [N, N]
    sim = sim - sim.max(dim=-1, keepdim=True).values  # numerical stability

    pos_mask = (y.unsqueeze(0) == y.unsqueeze(1)).float()
    pos_mask.fill_diagonal_(0)                         # exclude self
    log_prob = sim - torch.logsumexp(sim, dim=-1, keepdim=True)
    loss = -(pos_mask * log_prob).sum(dim=-1) / pos_mask.sum(dim=-1).clamp(min=1)
    return loss.mean()


class ContrastiveTrainer(Trainer):
    def __init__(self, *args, lambda_c=0.3, tau=0.1, mode="scl", **kwargs):
        super().__init__(*args, **kwargs)
        self.lambda_c = lambda_c
        self.tau = tau
        self.mode = mode  # "scl" atau "jscl"

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs, labels=labels, output_hidden_states=True)
        loss_ce = outputs.loss
        hidden = outputs.hidden_states[-1]

        if self.mode == "scl":
            loss_c = scl_loss_tokens(hidden, labels, tau=self.tau)
        elif self.mode == "jscl":
            loss_c = jscl_loss_tokens(hidden, labels, tau=self.tau)  # see §3.6.1
        else:
            raise ValueError(self.mode)

        loss = (1 - self.lambda_c) * loss_ce + self.lambda_c * loss_c
        return (loss, outputs) if return_outputs else loss
```

#### 3.6.1 JSCL — Adaptasi Sentence-level Jaccard

**Strategi final (lock-in 2026-05-11):** sentence-level Jaccard.

Paper JSCL Dewabharata et al. dirancang untuk multi-label dokumen (`L_i` = set of labels per dokumen). Sirah NER token-level (1 token = 1 label BIO). Adaptasi yang dipakai:

**Sentence-level Jaccard:**
- **Anchor** adalah **kalimat** (representasi via mean-pool token embeddings yang valid, atau CLS embedding kalau ada).
- **`L_i`** = bag-of-labels BIO unik di kalimat ke-`i`, contoh: `{"B-PERSON", "I-PERSON", "B-EVENT", "O"}`. Bisa pertimbangkan **exclude `O`** supaya Jaccard tidak didominasi label mayoritas — keputusan ini dicatat di §3.6.2 sebagai knob.
- **Jaccard:** `J_ij = |L_i ∩ L_j| / |L_i ∪ L_j|` antar kalimat dalam batch.
- **Weighted InfoNCE** dengan `α_ij = J_ij / (Σ_k≠i J_ik + ε)` mengikuti Eq. 4–6 paper persis.
- Loss: `L_JSCL = -(1/B) Σ_i Σ_j≠i α_ij log(exp(sim(s_i, s_j)/τ) / Σ_k≠i exp(sim(s_i, s_k)/τ))`.

**Kenapa sentence-level (bukan window-level / token-level):**
- Paling konsisten dengan paper Dewabharata yang juga operate di document-level (dokumen → kalimat = analog yang paling natural).
- Jaccard antar kalimat punya signal non-trivial (bisa 0, 0.25, 0.5, 0.75, 1.0) — beda dengan token-level single-label yang degenerate ke 0 atau 1.
- Implementasi clean — tidak perlu hyperparameter window size tambahan.

```python
def jscl_loss_sentence(hidden, labels, tau=0.1, exclude_O=True, O_label_id=0):
    """
    JSCL sentence-level adaptation (mengikuti Eq. 4-6 paper Dewabharata et al.).

    hidden : [B, T, H] token embeddings dari hidden_states[-1]
    labels : [B, T] BIO label id, -100 = ignore (special tokens / sub-word)
    tau : temperature
    exclude_O : kalau True, label "O" di-skip saat membangun bag-of-labels per kalimat
                (mencegah Jaccard didominasi kelas mayoritas)
    O_label_id : id integer label "O" di label2id
    """
    B, T, H = hidden.shape
    mask_valid = (labels != -100).float().unsqueeze(-1)            # [B, T, 1]

    # 1. Sentence representation: mean-pool valid tokens
    sent_h = (hidden * mask_valid).sum(dim=1) / mask_valid.sum(dim=1).clamp(min=1)
    sent_h = F.normalize(sent_h, dim=-1)                            # [B, H]

    # 2. Bag-of-labels per sentence (multi-hot)
    num_labels = int(labels[labels != -100].max().item()) + 1
    L = torch.zeros(B, num_labels, device=hidden.device)
    for b in range(B):
        valid = labels[b][labels[b] != -100]
        if exclude_O:
            valid = valid[valid != O_label_id]
        if valid.numel() > 0:
            L[b].scatter_(0, valid.unique(), 1.0)

    # 3. Jaccard score antar kalimat
    inter = L @ L.T                                                 # [B, B]
    union = L.sum(dim=-1, keepdim=True) + L.sum(dim=-1).unsqueeze(0) - inter
    J = inter / (union + 1e-8)                                      # [B, B]

    # 4. Weighting α_ij = J_ij / (Σ_k≠i J_ik + ε)
    mask_off_diag = 1 - torch.eye(B, device=hidden.device)
    J_off = J * mask_off_diag
    alpha = J_off / (J_off.sum(dim=-1, keepdim=True) + 1e-8)

    # 5. Weighted InfoNCE (Eq. 4 paper)
    sim = sent_h @ sent_h.T / tau                                   # [B, B]
    sim = sim - sim.max(dim=-1, keepdim=True).values                # stability
    # Mask self di denominator
    sim_masked = sim.masked_fill(torch.eye(B, dtype=torch.bool, device=hidden.device), float('-inf'))
    log_prob = sim - torch.logsumexp(sim_masked, dim=-1, keepdim=True)
    loss = -(alpha * log_prob * mask_off_diag).sum() / B
    return loss
```

#### 3.6.2 Knob JSCL Sentence-level

| Knob | Default | Catatan |
|---|---|---|
| `tau` (τ) | 0.1 | Temperature InfoNCE — sweep 0.07–0.5 sesuai paper |
| `lambda_c` (λ) | 0.3 | Bobot loss contrastive di `L_total = (1-λ)L_CE + λL_JSCL` |
| `exclude_O` | `True` | Skip label `O` di bag-of-labels. **Rekomendasi True** karena `O` muncul di hampir semua kalimat → Jaccard akan sangat tinggi tanpa diskriminasi |
| `batch_size` | ≥ 32 | Butuh batch cukup besar supaya ada variasi bag-of-labels antar kalimat |
| `sentence_repr` | mean-pool | Alternatif: CLS embedding (kalau jelas batas-batas kalimat di tokenizer) |

### 3.7 Pro & Kontra

**Pro:**
- State-of-the-art untuk imbalanced classification + low-resource NER.
- Attack imbalance di level representasi (orthogonal vs class weight di loss).
- Tidak menambah data — masih bisa di-train di Colab T4.

**Kontra:**
- Tambah hyperparameter (λ, τ) — perlu sweep mini.
- Memori lebih (perlu pairwise distance dalam batch).
- Definisi JSCL belum konkret → perlu konfirmasi paper terlebih dahulu.

### 3.8 Effort

4-6 jam coding (per variasi SCL/JSCL) + 3-4 jam Colab GPU.

### 3.9 Prasyarat Sebelum Coding

1. ✅ **Paper SCL/JSCL konkret** — `Contrastive_Learning.pdf` (Dewabharata et al.) di root repo. Formulasi SCL (Eq. 2–3) dan JSCL (Eq. 4–6) sudah jelas.
2. ✅ **Adaptasi JSCL ke NER** — lock-in **sentence-level Jaccard** (lihat §3.6.1). Sketsa kode siap di §3.6 + §3.6.1.
3. ⏳ **Konfirmasi Bu Diana** — apakah SCL + JSCL sebagai 2 sub-skenario (S2a/S2b) atau cukup salah satu yang ditampilkan di Bab 4.

---

## 4. S3 — λ_C Tuning + Mention Replacement Augmentation

> **Revisi 2026-05-20:** Plan S3 di-rewrite total post-bimbingan 2026-05-16. Sebelumnya: S3 = S2 (λ_C=0.3) + augmentation. Sekarang: S3 = (1) λ_C sweep di S2 SCL → winner, (2) S2 winner + Mention Replacement augmentation. Deadline **29 Mei 2026**.

### 4.1 Definisi

S3 punya **dua sub-tahap berurutan**:

**S3.1 — λ_C sweep** di S2 SCL:
- Run S2 SCL dengan **3 nilai λ_C: 0.1, 0.2, 0.3** (default 0.3 = run yang sudah selesai)
- 6 iterasi self-training × 10 epoch per λ_C (sama dengan S2)
- Pilih winner berdasarkan **Seq F1 entity-level test set**
- Tujuan: close the gap S2 (~0.95) vs S1 (0.959) → ekspektasi λ_C lebih kecil mengurangi trade-off boundary vs token

**S3.2 — Mention Replacement augmentation** (Dai & Adel 2020) di atas S3.1 winner:
- Ambil model S2 SCL dengan λ_C winner
- Augment train set: untuk tiap kalimat yang punya entity kelas minor (EVENT, I-LOCATION, B-TIME), generate 1–3 kalimat baru dengan mengganti entity-nya dengan entity sekelas dari pool
- Re-run 6 iterasi self-training × 10 epoch dengan train_augmented.csv
- Hasil = output utama S3

### 4.2 Motivasi

**Untuk S3.1 (λ_C tuning):**
- S2 default λ_C=0.3 → token-level F1 naik (~0.995 vs S1 ~0.99) tapi entity-level Seq F1 turun (~0.95 vs S1 0.959)
- Gap kecil 0.01 tapi konsisten → hipotesis: λ_C=0.3 terlalu agresif → contrastive loss over-prioritize per-token similarity, mengompromi entity boundary detection
- λ_C lebih kecil (0.1, 0.2) → balance lebih baik antara CE loss (entity boundary) dan contrastive loss (representasi disiplin)

**Untuk S3.2 (Mention Replacement):**
- EVENT support cuma 51 di test set, B-EVENT/I-EVENT 0.13%/0.14% di train. Sample-nya **memang sedikit** — tuning λ_C tetap bekerja dengan kalimat yang sama
- Bu Diana putaran 3: *"oversampling bisa tapi susah. Augmentasi sentence-based (1 kalimat yang fokusnya ke minor) ditambahkan ke data train"*
- Mention Replacement (Dai & Adel COLING 2020) = strategi paling sederhana & robust untuk NER augmentation: cuma swap entity dengan pool sekelas, struktur sintaktik kalimat tetap

### 4.3 Strategi Augmentasi: Mention Replacement (Dai & Adel COLING 2020)

**Cara kerja:**
1. **Build entity pool** dari train set per-kelas: `pool[B-EVENT] = [entity1, entity2, ...]`
2. Untuk tiap kalimat di train yang mengandung entity kelas minor target:
   - Untuk tiap entity di kalimat, **probability `p` ganti dengan entity random dari pool sekelas** (preserve BIO tagging)
   - Generate **`n` augmented variant** per kalimat
3. Append augmented sentences ke `train.csv` → `train_augmented.csv`

**Contoh:**
- Original: `Pada saat [Perang Badar]_EVENT, kaum muslimin menang.`
- Augmented #1: `Pada saat [Perang Uhud]_EVENT, kaum muslimin menang.`
- Augmented #2: `Pada saat [Perjanjian Hudaibiyah]_EVENT, kaum muslimin menang.`

**Kelas target prioritas:** B-EVENT, I-EVENT, I-LOCATION, B-TIME, I-TIME (kelas dengan F1 < 0.82 di S2 SCL).

**Catatan:** Augmented data sudah disiapkan di `data/result/pseudo-labelling/SRL-NER/train_augmented.csv` (script siap, distribusi minor naik 2-3×). Tinggal feed ke pipeline S2 winner.

### 4.4 Knob Hyperparameter

| Knob | Default | Fungsi |
|---|---|---|
| **S3.1 — λ_C sweep** | | |
| `lambda_c_grid` | `[0.1, 0.2, 0.3]` | Sweep di S2 SCL |
| `tau` | 0.1 | Tetap sama |
| Knob S2 lainnya | sama | THRESHOLD=0.9, MAX_ITERATIONS=6, dst |
| **S3.2 — Augmentation** | | |
| `replace_prob` | 0.7 | Probability per-entity diganti |
| `n_augment_per_minor_sentence` | 2 | Berapa variant per kalimat minor |
| `target_classes` | `["B-EVENT", "I-EVENT", "I-LOCATION", "B-TIME", "I-TIME"]` | Kelas yang ditarget |
| `lambda_c` | (winner dari S3.1) | Pakai hasil sweep |

### 4.5 Integrasi ke Pipeline

**S3.1:** loop `for λ_C in [0.1, 0.2, 0.3]:` di Colab notebook (3× durasi run S2 SCL = ~6-8 jam GPU T4 total). Output per-λ_C disimpan di folder terpisah supaya bisa di-compare side-by-side.

**S3.2:** sekali run dengan `train_augmented.csv` sebagai input + λ_C winner (~3-4 jam GPU T4). Output di `done_running/S3_augmented_SCL/`.

### 4.6 Pro & Kontra

**Pro:**
- λ_C sweep → empirical resolution dari hipotesis "λ_C=0.3 terlalu agresif" — datadriven decision
- Mention Replacement = standar literatur NER augmentation (Dai & Adel 2020 paling banyak disitir)
- Layer-by-layer tetap clean: S3 = S2 (di-tune) + augmentation, tidak loncat 2 layer sekaligus

**Kontra:**
- Tambah 6-8 jam GPU untuk sweep (vs single run S3 augment = 3-4 jam) — fit ke deadline 29 Mei tapi tipis
- Mention Replacement berisiko semantic drift: "Perang Badar" diganti "Perang Tabuk" di konteks Quraisy → secara sejarah salah. Mitigasi: validasi manual sample 20-30 augmented sentences sebelum train.

### 4.7 Effort

- **S3.1:** 2 jam coding (loop λ_C + logging) + 6-8 jam Colab GPU
- **S3.2:** 2-3 jam coding (Mention Replacement script — sebagian sudah siap di `train_augmented.csv`) + 3-4 jam Colab
- **Total: ~13-17 jam** dalam 9 hari (deadline 29 Mei)

### 4.8 Prasyarat Sebelum Run

1. ✅ S2 SCL + JSCL sudah selesai (2026-05-14/15) → S2 SCL λ_C=0.3 jadi salah satu titik di sweep S3.1
2. ✅ Mention Replacement script + `train_augmented.csv` siap (sudah dibuat sebelumnya)
3. ⏳ Validasi manual sample augmented sentences (20-30 kalimat) sebelum run S3.2

### 4.9 Output yang Diharapkan

**S3.1 (λ_C sweep):**
- Tabel Seq F1 per λ_C × per iterasi
- Pilih λ_C dengan Seq F1 entity-level final tertinggi (atau peak tertinggi, dijustifikasi)
- Target: ≥ S1 baseline 0.959 (close the gap)

**S3.2 (augmentation):**
- F1 EVENT naik signifikan dari S2 (target ≥ 0.85)
- F1 entity-level overall stabil atau naik vs S3.1 winner

---

## 5. Timeline & Status

| Skenario | Status | Trigger lanjut |
|---|---|---|
| **S1** | ✅ Selesai (reuse E1 2026-05-07) | – |
| **S2** | ✅ Selesai 2026-05-14/15 (S2a SCL + S2b JSCL, λ_C=0.3) | – |
| **S3.1 (λ_C sweep)** | ⏳ Plan post-bimbingan 2026-05-16 | Approved Bu Diana, deadline 29 Mei 2026 |
| **S3.2 (augmentation)** | ⏳ Depend on S3.1 | Mention Replacement script + train_augmented.csv siap |

**Action items menuju deadline 29 Mei 2026:**

1. ⏳ **Run S3.1** — λ_C sweep (0.1, 0.2, 0.3) di S2 SCL → pilih winner berdasarkan Seq F1 entity (~6-8 jam GPU T4)
2. ⏳ **Validasi manual** sample augmented sentences (20-30 kalimat dari train_augmented.csv) — pastikan tidak ngawur secara sejarah
3. ⏳ **Run S3.2** — Mention Replacement augmentation di atas S3.1 winner (~3-4 jam GPU T4)
4. ⏳ **Inference NER terbaik** ke seluruh `sirah_chunks_final.csv`
5. ⏳ **Regenerate** `nodes_v3.csv` + `edges_v3.csv` dari output NER
6. ⏳ **Comparison report** SRL-NER vs manual labelling (untuk bimbingan berikutnya)

---

## 6. Referensi Paper Pendukung

### 6.A. Untuk S1 (Baseline)

| # | Paper | Link | Relevansi |
|---|---|---|---|
| **A.1** ⭐⭐⭐ | **Transformer-Based SRL for Crisis Events Using Semi-Supervised Learning** (Ariyanto, Purwitasari, Fatichah, Ravana, Andrian, Parwata — IEEE Access Sept 2025) | https://ieeexplore.ieee.org/document/11097773 | Paper pembimbing — wajib disitir. Algorithm 1 = pipeline Sirah. IndoBERT @ 0.9, F1 = 0.863 target. |
| **A.2** | **Self-Training: A Survey** (Amini et al., Neurocomputing 2024) | https://arxiv.org/abs/2202.12040 | Overview self-training untuk Bab 2. |
| **A.3** | **IPerFEX-2023: Indonesian Financial Entity Extraction with IndoBERT-BiGRU-CRF** (Saputra et al., Journal of Big Data 2024) | https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-00987-6 | Konfirmasi pemilihan IndoBERT untuk NER Bahasa Indonesia. |

### 6.B. Untuk S2 (Contrastive Learning)

| # | Paper | Link | Relevansi |
|---|---|---|---|
| **B.1** ⭐⭐⭐ | **Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label Classification of Indonesian Regulatory Texts** (Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo) | `Contrastive_Learning.pdf` (lokal di root repo) | **Paper rujukan utama untuk S2.** Mendefinisikan **SCL** (Eq. 2–3) dan **JSCL** (Eq. 4–6) yang dipakai Sirah, plus framework two-phase (contrastive pre-training + pseudo-label fine-tuning) yang selaras dengan pipeline self-training Sirah. Sebagian besar penulis dari ITS. |
| **B.2** ⭐⭐ | **Supervised Contrastive Learning** (Khosla et al., NeurIPS 2020) | https://arxiv.org/abs/2004.11362 | Foundational SCL — formulasi loss original. Disitir untuk justifikasi konsep SCL secara umum (paper B.1 juga rujuk ini). |
| **B.3** ⭐ | **CONTaiNER: Few-Shot Named Entity Recognition via Contrastive Learning** (Das et al., ACL 2022) | https://aclanthology.org/2022.acl-long.439/ | Contrastive learning untuk **NER token-level** — relevan untuk justifikasi adaptasi paper B.1 (yang document-level) ke setting NER Sirah. |
| **B.4** | **ContrastNER: Contrastive-based Prompt Tuning for Few-shot NER** (Layegh et al., 2023) | TBD — cari ulang | Aplikasi SCL ke NER few-shot. Supporting reference. |

### 6.C. Untuk S3 (Sentence Augmentation NER)

| # | Paper | Link | Relevansi |
|---|---|---|---|
| **C.1** ⭐⭐ | **An Analysis of Simple Data Augmentation for Named Entity Recognition** (Dai & Adel, COLING 2020) | https://aclanthology.org/2020.coling-main.343/ | Survey + benchmark teknik augmentasi NER (label-wise token replacement, mention replacement, sentence cropping). Kandidat utama untuk S3 template substitution. |
| **C.2** ⭐ | **DAGA: Data Augmentation with a Generation Approach for Low-resource Tagging Tasks** (Ding et al., EMNLP 2020) | https://aclanthology.org/2020.emnlp-main.488/ | Generative augmentation untuk NER low-resource. Kalau S3 pakai LLM paraphrase. |
| **C.3** | **Sentence-Level Resampling for Named Entity Recognition** (Akkasi & Moens, NAACL 2022) | https://aclanthology.org/2022.naacl-main.156/ | Resampling sentence-level untuk imbalance. Pembanding metode. |

### 6.D. Top 5 Sitasi Prioritas

Kalau hanya bisa sitir 5 paper di Bab 2 sub-bab pseudo-labelling/contrastive/augmentation:

1. **A.1 — Ariyanto et al. IEEE Access 2025** ⭐⭐⭐ — baseline pembanding (wajib, pembimbing sama)
2. **B.1 — Dewabharata et al.** ⭐⭐⭐ — paper utama S2 (SCL + JSCL formulasi)
3. **B.3 — CONTaiNER ACL 2022** ⭐ — contrastive untuk NER token-level (justifikasi adaptasi)
4. **C.1 — Dai & Adel COLING 2020** ⭐⭐ — augmentasi NER (benchmark) untuk S3
5. **A.2 — Self-Training Survey 2024** — overview self-training (Bab 2)

Sisanya (A.3, B.2, B.4, C.2, C.3) bisa disitir sebagai supporting references.

---

## 7. Status Pertanyaan Bu Diana (Resolved Post-Bimbingan 2026-05-16)

### 7.1 Klarifikasi Skenario

1. **Restrukturisasi skenario** (S1=baseline, S2=baseline+contrastive, S3=S2+augmentation)?
   → ✅ **Approved** Bu Diana di bimbingan 2026-05-16.

2. **S2 — SCL vs JSCL**: cukup salah satu atau kedua varian?
   → ✅ **Kedua varian sudah dijalankan** (S2a SCL + S2b JSCL). Hasil: SCL > JSCL konsisten ~+0.01.

3. **S3 — strategi augmentasi**: template, back-translation, atau GPT?
   → ✅ **Mention Replacement (Dai & Adel COLING 2020)** dipilih — paling robust + ada di literatur. Augmented data sudah siap di `train_augmented.csv`.

4. **Skenario class-weight murni** sebagai pembanding pure?
   → 🟡 **Tidak dibahas eksplisit**. Tetap di-arsip di `legacy_class_weight_adaptive/` sebagai studi pendahuluan / ablation pembanding di Bab 4.

### 7.2 Posisi di Laporan

5. **Bab 4 — klaim utama** S1+S2+S3 vs class-weight/adaptive lama?
   → 🟡 **Tidak dibahas**. Default plan: S1+S2+S3 jadi klaim utama, class-weight/adaptive jadi sub-bab "Studi Pendahuluan".

6. **F1 EVENT** masih jadi metrik kunci?
   → 🟡 **Tidak dibahas**. Default: Seq F1 entity-level + per-class breakdown EVENT keduanya disajikan.

### 7.3 Timeline

7. **Urutan prioritas**: S1+S2 cukup, S1+S3, atau wajib semua?
   → ✅ **Wajib semua** dengan deadline **29 Mei 2026**.

8. **Boleh start coding S2 sebelum dapat paper JSCL teman**?
   → ✅ Sudah selesai (paper Dewabharata et al. + sentence-level Jaccard adaptasi).

### 7.4 Pertanyaan/Tambahan Baru dari Bu Diana di Bimbingan 2026-05-16

**Untuk bimbingan berikutnya** (di luar scope skenario S1/S2/S3, tapi terkait pipeline NER):

- ⚠️ **LLM verb extraction**: lempar Sirah ke LLM, ekstrak kata kerja/kata terkait event → tambahkan sebagai Event entity (antisipasi support EVENT yang masih kecil)
- ⚠️ **Frekuensi entitas per period**: amati frekuensi kemunculan PERSON/EVENT/LOCATION per periodisasi → justifikasi pengaruh
- ⚠️ **Pipeline end-to-end** dengan output SRL-NER (bukan manual labelling) — comparison report wajib
- ⚠️ **Pembukuan per-Bab** dimulai sesuai update terbaru

---

## 8. Output yang Diharapkan

Setelah skenario S1+S2+S3 selesai:

### 8.1 Tabel Hasil Utama (Bab 4)

| Skenario | F1 entity-level | F1 PERSON | F1 LOCATION | F1 TIME | F1 EVENT |
|---|---:|---:|---:|---:|---:|
| **S1 — Baseline** | 0.959 ✅ | 0.972 | 0.954 | 0.883 | 0.816 |
| **S2 — Baseline + Contrastive** | ? | ? | ? | ? | ? (target naik) |
| **S3 — S2 + Augmentation** | ? | ? | ? | ? | ? (target tertinggi) |

### 8.2 Plot

- F1 vs iterasi (3 skenario, dari `iteration_log.csv`).
- F1 per-entitas bar chart (S1 vs S2 vs S3, fokus highlight EVENT).
- Loss curves S2: `L_CE` vs `L_SCL` per epoch (kalau pakai SCL).

### 8.3 Analisis

- Kontribusi marginal tiap layer: ΔF1(S2−S1) untuk efek contrastive, ΔF1(S3−S2) untuk efek augmentation.
- Mana yang paling membantu kelas EVENT — contrastive (representasi) atau augmentation (data)?

### 8.4 Rekomendasi Pipeline Final

- Skenario pemenang dipakai untuk inferensi ke seluruh `sirah_chunks_final.csv`.
- Input pembentukan Knowledge Graph.

---

## 9. Arsip: Skenario Lama (Class Weight + Adaptive Threshold)

> **Status:** Tidak masuk klaim utama TA. Hasil run masih tersimpan di `done_running/legacy_class_weight_adaptive/` sebagai bukti eksplorasi metodologi.

### 9.1 Ringkasan Skenario Lama yang Dijalankan

| Skenario lama | Komponen | Hasil F1 entity | F1 EVENT |
|---|---|---|---|
| E1 lama (= S1 baru) | Fix 0.9, no CW | **0.959** | 0.816 |
| S1 lama | Fix 0.9 + class weight inverse freq (clip 50) | 0.908 | 0.835 |
| S2 lama | Adaptive 0.9→0.7 + class weight | 0.843 | 0.830 |

**Temuan utama:**
- Class weight memang menaikkan F1 EVENT (+1.9%) dan recall semua kelas.
- Tapi precision turun signifikan (S2 lama: precision 0.74 = 26% noise).
- Adaptive threshold STOP cepat (iter 2) karena pseudo-label pool habis.

**Kenapa di-drop dari skenario aktif?**
- Class weight bekerja di level loss saja — Bu Diana putaran 3 ingin attack imbalance di level lain (representasi via contrastive, data via augmentation).
- Trade-off precision-recall yang terlalu tajam (S2 lama precision 0.74) → tidak ideal untuk KG.
- Skenario baru lebih bersih: 1 layer = 1 kontribusi, mudah di-isolasi efeknya.

### 9.2 Detail Hasil Lama

Detail lengkap (per-iterasi log, confusion matrix, error pattern, P-R trade-off) tersimpan di:
- `done_running/legacy_class_weight_adaptive/analisis_skenario_srlner.md`
- `done_running/legacy_class_weight_adaptive/compare_scenarios.ipynb`
- `done_running/legacy_class_weight_adaptive/S1_classweight/` (model + log + evaluation skenario lama class weight)
- `done_running/legacy_class_weight_adaptive/S2_adaptive/` (model + log + evaluation skenario lama adaptive)

> Data baseline (E1 lama = S1 baru) dibagi pakai dengan skenario aktif → tersimpan di `done_running/S1_baseline/`, bukan duplikat di legacy folder.

### 9.3 Kalau Bu Diana Minta Lihat Lagi

- File-nya tetap ada, tidak di-delete.
- Bisa direferensikan di Bab 4 sebagai studi pendahuluan / ablation pembanding.
- Klaim yang masih bisa dipakai: "class weight inverse frequency menaikkan F1 EVENT +1.9% di Sirah, tapi menurunkan precision overall" — bisa jadi argumen kenapa kami pindah ke contrastive learning.

---

## 10. Action Item Sesi Berikutnya (Post-Bimbingan 2026-05-16, Deadline 29 Mei 2026)

1. ✅ Plan 3-skenario approved Bu Diana — proceed.
2. ✅ Paper S2 + S3 sudah teridentifikasi (Dewabharata et al. + Dai & Adel 2020).
3. ✅ S2 SCL + JSCL selesai run 2026-05-14/15.
4. ⏳ **Run S3.1** — λ_C sweep (0.1, 0.2, 0.3) di S2 SCL → pilih winner (~6-8 jam GPU T4 di Colab)
5. ⏳ **Validasi manual** sample augmented sentences (20-30 kalimat) sebelum run S3.2
6. ⏳ **Run S3.2** — Mention Replacement augmentation di atas S3.1 winner (~3-4 jam GPU T4)
7. ⏳ **Inference NER terbaik** ke seluruh `sirah_chunks_final.csv`
8. ⏳ **Regenerate `nodes_v3.csv` + `edges_v3.csv`** dari output NER
9. ⏳ **Comparison report** SRL-NER vs manual labelling untuk bimbingan berikutnya
10. ⏳ **Update CLAUDE.md** + mulai pembukuan Bab 4 sesuai arahan Bu Diana

Detail outcome bimbingan: `../bimbingan/2026-05-16_outcome.md`. Detail propagasi: `../bimbingan/revisi_dosen.md` Putaran 5.
