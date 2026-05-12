# Skenario SRL-NER — S1 / S2 / S3

> **Tanggal revisi terakhir:** 2026-05-11
> **Konteks revisi:** Skenario dirombak menggantikan rencana lama (class weight + adaptive threshold). Skenario lama tetap di-arsip di `done_running/legacy_class_weight_adaptive/` sebagai bukti eksplorasi, tidak masuk klaim utama TA.

## 0. Ringkasan Skenario

| Skenario | Komponen | Status |
|---|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa handle imbalance, tanpa contrastive, tanpa augmentation | ✅ Hasil run reuse dari E1 lama (2026-05-07) |
| **S2 — Contrastive Learning + Baseline** | S1 + supervised contrastive loss (SCL + JSCL sentence-level, rujuk paper Dewabharata et al. `Contrastive_Learning.pdf`) | ⏳ Paper + adaptasi sudah lock-in, tunggu approval Bu Diana → coding |
| **S3 — Sentence-based Augmentation + S2** | S2 + augmentasi kalimat fokus kelas minor (EVENT, TIME, I-LOCATION) | ⏳ Depend on S2, tunggu paper augmentasi konkret |

**Filosofi:** layer-by-layer — S2 menambah satu komponen ke S1 (contrastive), S3 menambah satu lagi ke S2 (augmentation). Tujuannya supaya kontribusi tiap komponen ke F1 kelas minoritas (terutama EVENT) bisa diisolasi.

**Latar belakang revisi 2026-05-11:** skenario lama (E1+S1 class-weight + S2 adaptive+CW) sudah dijalankan dan menunjukkan class weight murni belum memuaskan untuk EVENT (F1 stuck di 0.83). Bu Diana putaran 3 menyarankan contrastive learning + sentence augmentation. Kami memutuskan **restrukturisasi total** supaya skema skenario lebih bersih: 1 skenario = 1 layer kontribusi.

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

## 4. S3 — Sentence-based Augmentation + S2

### 4.1 Definisi

S3 = S2 (baseline + contrastive) + augmentasi data: generate kalimat baru fokus ke kelas minor (`B-EVENT`, `I-EVENT`, `I-LOCATION`, opsional `B-TIME`/`I-TIME`) lalu append ke train set sebelum training.

### 4.2 Motivasi

- EVENT support cuma 51 kalimat di test, dan B-EVENT/I-EVENT cuma 0.13%/0.14% di train. **Sample kalimat-nya memang sedikit** — class weight + contrastive tetap bekerja dengan kalimat yang sama.
- Bu Diana putaran 3: *"oversampling bisa tapi susah. Augmentasi sentence-based (1 kalimat yang fokusnya ke minor) ditambahkan ke data train"*.
- Augmentasi sentence-based = generate kalimat baru → variasi konteks naik tanpa duplikasi murni.

### 4.3 Strategi Augmentasi (kandidat — final menunggu paper teman)

| Strategi | Cara kerja | Kelas target | Effort |
|---|---|---|---|
| **Template substitution** | Ganti entity di kalimat existing (mis. ganti nama PERSON di kalimat EVENT) dengan entity sekelas dari pool | EVENT, TIME, LOCATION | Rendah |
| **Context expansion** | Tambah kalimat anchor di sebelum/sesudah yang menyebut entity minor | EVENT | Sedang |
| **Back-translation (id→en→id)** | Translate kalimat EVENT ke English, lalu translate balik | Semua, terutama EVENT | Sedang (butuh API) |
| **GPT paraphrase** | Pakai LLM untuk paraphrase kalimat EVENT, makna sama struktur beda | EVENT, TIME | Sedang-tinggi |

**Strategi final:** menunggu paper referensi dari teman + konfirmasi Bu Diana.

### 4.4 Knob Hyperparameter

| Knob | Default | Fungsi |
|---|---|---|
| `n_augment_per_minor_sentence` | 1–3 | Berapa kalimat augmentasi per kalimat minor original |
| `target_classes` | `["B-EVENT", "I-EVENT", "I-LOCATION"]` | Kelas yang ditarget augmentasi |
| `augmentation_strategy` | TBD | Pilih 1 atau kombinasi dari §4.3 |
| Semua knob S2 | sama | Contrastive λ/τ, threshold, dll tetap |

### 4.5 Integrasi ke Pipeline Existing

- Tambah **cell di awal notebook** untuk generate augmented sentences sebelum training (sekali, bukan per-iter self-training).
- Output: `train_augmented.csv` (existing train + augmented) → feed ke pipeline normal yang sudah berisi S2.
- **Tidak mengubah** loss/threshold/contrastive — augmentasi adalah **pre-processing data**.

### 4.6 Pro & Kontra

**Pro:**
- Data-level intervention — orthogonal terhadap S2 (model tidak diubah).
- Bisa dikombinasi dengan S2 dengan minimal coupling.
- Mudah dijelaskan di Bab 3.

**Kontra:**
- Kualitas augmented sentence tergantung strategi:
  - Template substitution → bisa hasilkan kalimat tidak natural.
  - Back-translation → butuh API + kualitas translation.
  - GPT paraphrase → ironis (LLM-NER dibatalkan, tapi LLM dipakai untuk augment).
- Risiko semantic drift — entity dipindah ke konteks yang salah secara sejarah Sirah (mis. "Perang Badar" dipindah ke konteks Madinah pasca-Fathu Makkah).

### 4.7 Effort

3-4 jam (template) atau 6-8 jam (back-translation/GPT) + 2-3 jam Colab.

### 4.8 Prasyarat Sebelum Coding

1. **S2 sudah selesai** — S3 layer di atas S2.
2. **Paper augmentasi NER konkret dari teman** — kandidat default Dai & Adel COLING 2020, DAGA EMNLP 2020.
3. **Validasi manual sampel augmented sentence** — sebelum di-train, cek 20–30 kalimat hasil augmentasi untuk pastikan tidak ngawur secara sejarah.

---

## 5. Timeline & Status

| Skenario | Status | Trigger lanjut |
|---|---|---|
| **S1** | ✅ Selesai (reuse E1 2026-05-07) | – |
| **S2** | ⏳ Menunggu approval Bu Diana | Paper + adaptasi sudah lock-in (sentence-level Jaccard). Bisa langsung coding setelah approval. |
| **S3** | ⏳ Menunggu | S2 selesai + paper augmentasi konkret |

**Yang harus dilakukan sebelum coding S2/S3:**

1. ✅ Paper contrastive konkret sudah ada (`Contrastive_Learning.pdf` — Dewabharata et al.).
2. ✅ Adaptasi JSCL ke NER sudah lock-in: **sentence-level Jaccard** (§3.6.1).
3. ⏳ Konfirmasi Bu Diana scope final: S1+S2+S3, atau S1+S2 cukup (S3 jadi future work). + SCL+JSCL keduanya atau cukup salah satu.
4. ⏳ Hubungi teman / cari paper augmentasi konkret untuk S3 (Dai & Adel COLING 2020 sebagai default kalau tidak ada info lain).

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

## 7. Pertanyaan untuk Bu Diana (Next Bimbingan)

### 7.1 Klarifikasi Skenario Baru

1. **Setuju dengan restrukturisasi skenario** (S1=baseline murni, S2=baseline+contrastive, S3=S2+augmentation)? Atau ingin tetap skenario lama (class weight + adaptive) ditambah putaran 3 (contrastive + augmentation)?
2. **S2 — SCL vs JSCL**: cukup salah satu (SCL standar Khosla 2020), atau wajib bandingkan kedua varian sebagai ablation?
3. **S3 — strategi augmentasi**: template substitution (sederhana) atau back-translation/GPT (kompleks tapi natural)?
4. **Apakah perlu ada skenario class-weight murni** (S1 + class weight saja) sebagai pembanding pure terhadap pendekatan baru, mengingat hasil S1 lama (class weight) menunjukkan EVENT F1 +1.9%? Atau cukup dijelaskan di lampiran/arsip?

### 7.2 Posisi di Laporan

5. **Bab 4 — apakah klaim utama** S1+S2+S3 (skenario baru), dan eksplorasi class-weight/adaptive lama dikutip sebagai "studi pendahuluan" di sub-bab terpisah?
6. **F1 EVENT** masih jadi metrik kunci? Atau pindah ke macro F1 tanpa O?

### 7.3 Timeline

7. **Kalau timeline TA terbatas**, urutan prioritas: S1+S2 cukup (S3 future work), S1+S3 (skip contrastive), atau wajib semua?
8. **Boleh start coding S2 sebelum dapat paper JSCL teman**, dengan asumsi pakai SCL standar dulu sebagai placeholder?

### 7.4 Bahan Diskusi dengan Rujukan Paper

- Justifikasi SCL untuk imbalanced NER: rujuk **B.1 (Khosla 2020)** + **B.2 (ContrastNER 2023)**.
- Justifikasi augmentasi sentence-based NER: rujuk **C.1 (Dai & Adel 2020)** + **C.2 (DAGA 2020)**.
- Justifikasi baseline IndoBERT @ 0.9: rujuk **A.1 (Ariyanto 2025)** dengan target F1 0.863 — Sirah sudah mencapai 0.9587.

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

## 10. Action Item Sesi Berikutnya

1. ✅ Paper S2 sudah teridentifikasi — `Contrastive_Learning.pdf` (Dewabharata et al.), berisi SCL + JSCL.
2. ✅ Adaptasi JSCL ke NER sudah lock-in: **sentence-level Jaccard** (§3.6.1). Sketsa kode siap.
3. ⏳ **Hubungi teman / cari** paper augmentasi konkret untuk S3 (default Dai & Adel COLING 2020).
4. ⏳ **Konfirmasi Bu Diana** scope final skenario baru (lihat §7.1) + apakah SCL + JSCL keduanya wajib atau cukup salah satu.
5. ⏳ **Mulai coding S2** setelah action item #4 selesai (jangan langsung S3 — depend on S2).
6. ⏳ **Jangan run di Colab** sebelum approval Bu Diana.
