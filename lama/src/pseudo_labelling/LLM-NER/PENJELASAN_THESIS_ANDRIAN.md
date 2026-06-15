# Penjelasan Thesis Andrian — LLM-Based NER

> Sumber: **"NER dengan Augmentasi Data dan Fine Tuning berbasis Text Generation menggunakan Large Language Model"**
> Andrian (NRP 5025211079, Teknik Informatika ITS, 2025)
> Pembimbing: Prof. Dr. Diana Purwitasari, S.Kom., M.Sc.
> Ko-pembimbing: Dini Adni Navastara, S.Kom., M.Sc.

Dokumen ini meringkas arsitektur dan langkah-langkah dari TA Mas Andrian agar mudah dimengerti, sekaligus memetakan apa yang sudah/belum diadopsi di proyek Sirah.

---

## 1. Inti Penelitian Andrian

Masalah utama: **NER bahasa Indonesia kekurangan data berlabel.** Model tradisional seperti IndoBERT (token classification) butuh data banyak; LLM punya kemampuan generalisasi lebih baik tapi mahal di-train.

Solusi yang diusulkan:
1. **Augmentasi data berbasis text generation** menggunakan LLM untuk memperbanyak variasi data latih.
2. **Instruction Fine-Tuning** LLM (LLAMA-3 family) dengan QLoRA agar efisien.
3. Membandingkan dua pendekatan training: **Token Classification** (klasik) vs **Instruction Fine-Tuning** (generatif).

Dataset yang digunakan:
- **Twitter** (Bahasa Indonesia, topik bencana alam): 3150 train + 1000 test
- **Bali** (cerita tradisional): 4343 train + 2229 test (untuk uji generalisasi lintas-domain)

Entitas Twitter: `EVE` (Event), `LOC` (Lokasi spesifik), `PLOC` (Pseudo-Location/wilayah luas), `ORG` (Organisasi), `ARG` (Argumen — waktu/korban/objek).

---

## 2. Arsitektur Umum

Andrian merancang dua alur paralel:

### Alur A — Tanpa Augmentasi (Gambar 3.2)
```
Dataset Twitter → Pemodelan NER (Token Classification ATAU Instruction Fine-Tuning) → Evaluasi
```

### Alur B — Dengan Augmentasi (Gambar 3.1)
```
Dataset Twitter ──┬─→ KEE-Prompt Generation ──→ Data Sintetis 1 ──┐
                  └─→ Entity-to-Text Generation → Data Sintetis 2 ──┤
                                                                     ↓
                                          Data Latih Baru (asli + sintetis)
                                                     ↓
                              Pemodelan NER (TC atau IFT) → Evaluasi
```

Dua jalur augmentasi dijalankan **terpisah dan dibandingkan** (tidak digabung).

---

## 3. Lima Langkah Utama (Berurutan)

### Langkah 1 — Persiapan Dataset (Pra-proses)

Referensi: **Kode Semu 3.1 Praproses Dataset**.

| Aspek | Detail |
|---|---|
| **Input** | CSV mentah dengan kolom `text_id`, `token`, `pos_tag`, `entity` |
| **Proses** | (1) Hapus baris kosong, (2) Group-by `text_id` → list per kalimat, (3) Acak (seed=42), (4) Split 80/20 train/val, (5) Filter `len(token) == len(entity) AND len > 2`, (6) Hapus duplikat |
| **Output** | `train_df` & `val_df` siap-pakai (terstruktur, bersih) |

> **Catatan**: Test set sudah dipisah sebelumnya. Yang di-split di sini hanya train→train+val.

---

### Langkah 2 — Augmentasi Data (Opsional, untuk Uji Coba 2 & 3)

Andrian menerapkan **dua metode augmentasi paralel**, lalu membandingkan mana yang lebih efektif untuk tiap jenis entitas.

#### 2A. KEE-Prompt Generation (Knowledge Entity Extraction)

Referensi: **Kode Semu 3.2, 3.3, 3.5** dan **Prompt 3.1–3.6**.

Filosofi: minta LLM **bikin kalimat sintetis baru dari nol**, dengan dipandu oleh contoh kalimat asli.

**Diagram alir (Gambar 3.3):**
```
Dataset Twitter
    ↓
Ekstraksi 5 komentar acak sebagai contoh tugas
    ↓
Bentuk Prompt KEE (4 komponen: Deskripsi Tugas + Definisi Entitas + Penekanan Tugas + Contoh Tugas)
    ↓
Query ke GPT-4o Mini (via OpenRouter API)
    ↓
Validasi hasil dengan Prompt validasi (Prompt 3.6)
    ↓
Apakah masih ada data yang belum diproses? → Ya: ulang | Tidak: selesai
    ↓
Dataset baru hasil augmentasi
```

**Struktur Prompt KEE:**
- **Deskripsi Tugas** (Prompt 3.1): "You are an experienced twitter user… generate 5 synthetic data samples…"
- **Penekanan Tugas** (Prompt 3.2): aturan teknis (BIO format, jumlah label = jumlah token, LOC vs PLOC, dll)
- **Definisi Entitas** (Prompt 3.3): definisi formal tiap label (EVE, LOC, ORG, PLOC, ARG)
- **Contoh Tugas** (Prompt 3.4): 3–5 sampel jadi (tokens + pos_tags + entities) sebagai few-shot
- **Prompt Penugasan** (Prompt 3.5): perintah eksplisit "generate 5 samples"
- **Prompt Validasi** (Prompt 3.6): tahap kedua — LLM diminta review hasil sendiri

| Aspek | Detail |
|---|---|
| **Input** | 5 kalimat asli dari dataset (diambil per batch) + 5 prompt component |
| **Proses** | LLM diberi instruksi dengan few-shot, diminta hasilkan 5 kalimat baru lengkap dengan token + POS + label BIO |
| **Output** | JSON `{tokens, pos_tags, entities}` untuk tiap sample baru |
| **Hasil di thesis** | Dataset KEE-1 dan KEE-2 (dua iterasi/varian); ORG naik **+177%** |

#### 2B. Entity-to-Text Generation (E2T)

Referensi: **Kode Semu 3.4, 3.6** dan **Prompt 3.7**.

Filosofi: **gunakan ulang entitas yang sudah ada**, hanya bangun ulang kalimat sekitarnya. Lebih konservatif dari KEE.

**Diagram alir (Gambar 3.4):**
```
Dataset Twitter
    ↓
Ekstraksi daftar entitas tiap komentar
    ↓
Modifikasi daftar entitas: Add / Replace / Delete / Swap (acak)
    ↓
Bentuk Prompt dengan instruksi + daftar entitas baru
    ↓
Query ke GPT-4o Mini → hasilkan teks baru
    ↓
Validasi: apakah semua entitas dari daftar muncul di teks baru?
    ├─ Ya: penandaan entitas → simpan
    └─ Tidak: buang
    ↓
Loop sampai semua komentar diproses
    ↓
Dataset baru
```

**Empat operasi modifikasi entitas (Tabel 2.6–2.9):**
1. **Add** — tambah entitas dari pool global yang punya tipe sama
2. **Delete** — hapus 1 entitas acak
3. **Replace** — ganti 1 entitas dengan entitas lain bertipe sama (mis. "jakarta" → "bekang")
4. **Swap** — tukar posisi 2 entitas

| Aspek | Detail |
|---|---|
| **Input** | Komentar asli + daftar entitasnya yang sudah dimodifikasi |
| **Proses** | LLM dipaksa menghasilkan teks koheren yang **tetap mengandung daftar entitas tersebut** |
| **Output** | Kalimat baru + label BIO (hasil pencocokan ulang) |
| **Hasil di thesis** | Dataset E2T-1 dan E2T-2; LOC naik **+212%** |

> **Insight kunci**: KEE = breadth (variasi entitas baru), E2T = depth (variasi konteks untuk entitas yang sama). Saling melengkapi.

---

### Langkah 3 — Pelatihan Model

Andrian membandingkan **dua metode pelatihan**, masing-masing pada model berbeda.

#### 3A. Token Classification (Baseline)

Referensi: **Kode Semu 3.8, 3.10** dan **Gambar 3.5**.

**Model**: IndoBERT (juga dicoba di SahabatAI/SEA-LION/LLAMA 3.1 sebagai pembanding token-classification)

**Pipeline:**
```
1. Buat dict id2label & label2id
2. Inisialisasi tokenizer (e.g., IndoBERT tokenizer)
3. Tokenisasi dataset → output sub-words
4. Selaraskan label dengan hasil tokenisasi (Kode Semu 3.8)
   - Sub-word pertama → label asli
   - Sub-word lanjutan → -100 (di-ignore loss)
5. Siapkan DataCollatorForTokenClassification
6. Cek VRAM:
   - Cukup → langsung train
   - Kurang → quantize model + tambah LoRA
7. Train dengan Trainer (AdamW, 10 epoch awal, batch=16, lr=1e-4)
8. Evaluate dengan seqeval per epoch
```

| Aspek | Detail |
|---|---|
| **Input** | `train_df` + `val_df` dari Langkah 1 |
| **Output** | Model yang langsung memprediksi label per token |
| **Hasil tanpa augmentasi (Tabel 4.8)** | IndoBERT F1=**0.711**, SahabatAI=0.508, SEA-LION=0.476, LLAMA 3.1=0.465 |

#### 3B. Instruction Fine-Tuning (Pendekatan Utama)

Referensi: **Kode Semu 3.7, 3.9** dan **Gambar 3.6**.

**Model utama**: SahabatAI (LLAMA-3 8B fine-tuned bahasa Indonesia), SEA-LION (Asia Tenggara), LLAMA 3.1 8B Instruct.

**Pipeline:**
```
1. Format dataset → prompt teks (Alpaca-style, Bahasa Indonesia)
2. Inisialisasi model + tokenizer
3. Cek VRAM → kuantisasi NF4 4-bit (Kode Semu 3.7)
4. Tambah LoRA adapter (r=64, alpha=32, dropout=0.05)
5. Train dengan SFTTrainer (Kode Semu 3.9)
   - dataset_text_field="text"
   - max_seq_length=ditentukan
   - DataCollatorForSeq2Seq
   - 30 epoch, batch=16, lr=1e-4
6. Inference satu-per-satu dengan retry mechanism
7. Konversi string output → list entity
8. Padding/truncate jika panjang ≠ jumlah token
9. Evaluate dengan seqeval
```

**Konfigurasi QLoRA (Tabel 4.5, Kode Semu 3.7):**
| Parameter | Nilai |
|---|---|
| Quantization | NF4 4-bit |
| `bnb_4bit_use_double_quant` | False |
| `bnb_4bit_compute_dtype` | bfloat16 |
| LoRA `r` | 64 (untuk model besar; 1024 untuk model kecil) |
| `lora_alpha` | 32 |
| `lora_dropout` | 0.05 |
| `bias` | none |
| `task_type` | TOKEN_CLS / CAUSAL_LM |
| **Trainable params** | hanya **6.86M dari 7.51B (~0.0913%)** |

**Format Prompt Alpaca** (Prompt 3.8 Bahasa Indonesia):
```
Di bawah ini adalah sebuah instruksi yang menjelaskan tugas...

### Instruksi:
Anda adalah seorang ahli linguistik berpengalaman dalam Named Entity Recognition (NER)...
Tugas Anda adalah mengekstrak token entitas dalam format BIO...

Ikuti ketentuan berikut:
1. Berikan output dalam bentuk daftar token yang dilabeli...
2. Pastikan jumlah label entitas sama dengan jumlah token...
[6 ketentuan total]

### Definisi Entitas:
-EVE (Event): ...
-LOC (Lokasi): ...
[dst per label]

### Input:
{daftar_token}
<|eot_id|>
### Respons:
{daftar_label_BIO}
```

| Aspek | Detail |
|---|---|
| **Input** | `train_df` yang sudah diformat ke prompt Alpaca + label BIO sebagai response |
| **Output** | LLM yang bisa menerima list token dan generate list label |
| **Hasil dengan augmentasi (Abstrak)** | SahabatAI F1=**0.7192** (Twitter), **0.8044** (Bali), > IndoBERT (0.711) |

---

### Langkah 4 — Inferensi (Khusus untuk IFT)

Referensi: **Kode Semu 3.12 Inferensi Model menggunakan Instruction Fine-Tuning**.

Output Token Classification = sudah berupa list of label → langsung evaluasi.
Output IFT = string raw → perlu konversi.

**Algoritma retry:**
```python
for setiap kalimat di test_df:
    response_list = []
    attempt = 0
    while len(response_list) != len(token_input) AND attempt < max_retries(=5):
        outputs = model.generate(prompt, max_new_tokens=512, use_cache=True)
        response_text = extract setelah "### Respons:"
        try:
            response_list = ast.literal_eval(response_text)
            if not isinstance(response_list, list): response_list = []
        except: response_list = []
        attempt += 1

    # Fallback: kalau tetap gagal, padding/truncate
    if len(response_list) > len(token_input): potong
    elif len(response_list) < len(token_input): pad dengan "O"
```

| Aspek | Detail |
|---|---|
| **Input** | Test set + model terlatih |
| **Output** | List of list label, panjangnya sudah disesuaikan dengan jumlah token input |
| **Kunci** | `max_retries=5`; mekanisme ini penting karena LLM generatif kadang output tidak konsisten format |

---

### Langkah 5 — Evaluasi

Referensi: **Kode Semu 3.11** dan **Bagian 2.2.4**.

**Library**: `seqeval` (entity-level F1, bukan token-level).

**Mengapa seqeval, bukan sklearn token-level?**
- Seqeval **mengabaikan label "O"** → fokus pada keberhasilan model di entitas yang relevan
- Seqeval mengevaluasi **per-entity** (B-PER + I-PER harus benar semua untuk dianggap benar)
- Lebih realistis untuk NER dibanding accuracy token-by-token

```python
import evaluate
metric = evaluate.load("seqeval")
all_metrics = metric.compute(predictions=y_pred, references=y_true)
# all_metrics berisi: overall_precision, overall_recall, overall_f1,
#                     overall_accuracy, dan per-entity (PER, LOC, ORG, dll)
```

| Metrik | Formula |
|---|---|
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1-score | 2 × (P × R) / (P + R) |

---

## 4. Komponen Kunci — Mengapa Pendekatan Ini Bekerja

### a. QLoRA (Dettmers et al., 2023)
- **NF4 quantization**: bobot 32-bit float → 4-bit NormalFloat. Memory turun ~8×, akurasi nyaris sama.
- **LoRA adapter**: hanya melatih matriks low-rank ΔW = BA (di mana A: r×d, B: d×r). Sisa parameter di-freeze.
- Hasil: bisa fine-tune LLM 8B di GPU 40 GB dengan **<1% trainable params**.

### b. Instruction Tuning (Wei et al., FLAN)
- LLM yang sudah pre-trained di banyak instruksi → bisa zero/few-shot di task baru.
- Format Alpaca menyatukan **task description + input + expected output** dalam satu prompt → model belajar memetakan instruksi ke output.

### c. Pemilihan Model LLM (Tabel 2.13)
| Model | Karakteristik | Mengapa dipilih |
|---|---|---|
| **LLAMA 3.1 8B Instruct** | Multilingual base | Baseline arsitektur LLAMA |
| **SahabatAI** | LLAMA 3 + 448K instruksi Bahasa Indonesia | Spesialis Indonesia (juga punya Jawa, Sunda) |
| **SEA-LION v3** | LLAMA 3 + CPT 200B token Asia Tenggara | Spesialis regional 11 bahasa |

Hipotesis Andrian: **semakin spesifik adaptasi bahasa → semakin baik performa NER**. Hasil membuktikan SahabatAI memang yang terbaik.

---

## 5. Hasil Utama Thesis (Bab IV)

### Tanpa Augmentasi (Token Classification, Tabel 4.8)
| Model | Precision | Recall | F1 |
|---|---|---|---|
| **IndoBERT** | 0.687 | 0.737 | **0.711** |
| SahabatAI | 0.458 | 0.572 | 0.508 |
| SEA-LION | 0.421 | 0.549 | 0.476 |
| LLAMA 3.1 | 0.420 | 0.542 | 0.465 |

> Pelajaran: untuk pure token classification, IndoBERT (BERT-based) **kalahkan LLM**. LLM butuh metode yang sesuai dengan arsitekturnya (generative).

### Dengan Augmentasi + Instruction Fine-Tuning (Abstrak)
| Model | F1 Twitter | F1 Bali |
|---|---|---|
| **SahabatAI (IFT + KEE)** | **0.7968** | — |
| SahabatAI (IFT) | 0.7192 | **0.8044** |
| SEA-LION (IFT) | 0.7175 | — |
| LLAMA 3.1 (IFT) | 0.7081 | — |
| GPT-4o Mini sebagai generator | 0.7831 | — |
| IndoBERT (TC) | 0.711 | — |

### Per-Entity Insight
- **KEE Prompt Generation** efektif untuk **ORG** (+177%) — karena LLM bisa create variasi nama organisasi baru.
- **Entity-to-Text Generation** efektif untuk **LOC** (+212%) — karena LOC banyak variasi konteks dengan kata-kata penanda ('di', 'dari').
- **IndoBERT mengalami penurunan** kalau ditambah data augmentasi (overfitting noise), sedangkan **LLM justru naik konsisten**.

---

## 6. Pemetaan ke Proyek Sirah

### Apa yang sudah diadopsi di `src/pseudo_labelling/LLM-NER/asli/llm_ner_sirah.py`

| Komponen Andrian | Status di Sirah | Catatan |
|---|---|---|
| Praproses dataset (Kode Semu 3.1) | ✅ | `prepare_instruction_data()` |
| Format prompt Alpaca Bahasa Indonesia (Prompt 3.8) | ✅ | Diadaptasi: ARG/ORG/PLOC → PERSON/EVENT/LOCATION/TIME |
| QLoRA NF4 + LoRA r=64/alpha=32/dropout=0.05 (Kode Semu 3.7) | ✅ | `setup_model()` |
| SFTTrainer config (Kode Semu 3.9) | ✅ | `train_model()` |
| Inferensi dengan retry (Kode Semu 3.12) | ✅ | `run_inference()` |
| Evaluasi seqeval (Kode Semu 3.11) | ✅ | `evaluate_model()` |
| Hyperparameter (30 epoch, batch=16, lr=1e-4, max_retries=5) | ✅ | Sama persis |

### Apa yang berbeda dari Andrian

| Aspek | Andrian | Sirah |
|---|---|---|
| **Domain** | Twitter bencana alam (informal) + Bali (narasi) | Sirah Nabawiyah (narasi sejarah formal) |
| **Entitas** | EVE, LOC, PLOC, ORG, ARG (5) | PERSON, EVENT, LOCATION, TIME (4) |
| **Sumber data** | Web scraping Twitter (3150) | OCR PaddleOCR dari PDF buku (6000 chunks) |
| **Manual labelling** | Penuh manual | Semi-auto via regex (`pre_labelling.py`) |

### Apa yang **belum** diadopsi (kandidat extension)

| Komponen Andrian | Status di Sirah | Pertimbangan |
|---|---|---|
| **KEE-Prompt Generation augmentation** | ❌ | Bisa: minta GPT generate cerita Sirah sintetis dari few-shot |
| **Entity-to-Text Generation augmentation** | ❌ | Bisa: ambil daftar entitas dari kalimat asli, bikin variasi narasi |
| **Multi-model comparison** (SahabatAI vs SEA-LION vs LLAMA 3.1) | 🔄 | Sirah baru pakai SahabatAI; bisa benchmark 3 model seperti Andrian |
| **Token Classification baseline** (IndoBERT) | ❌ | Belum ada IndoBERT baseline di Sirah; SRL-NER pakai BERT lain |
| **Pseudo-labelling iterative self-training** | ❌ | **Andrian tidak pakai ini** — pseudo-labelling adalah konsep berbeda dari self-training. Yang dipakai Andrian adalah **data augmentation** (sintetis dari LLM), bukan self-labeling pada unlabeled data |

> **Catatan penting tentang istilah**: di proyek Sirah, folder `pseudo_labelling/` berisi dua subfolder (LLM-NER & SRL-NER). SRL-NER pakai **iterative self-training** (predict unlabelled → filter confidence → tambah ke train → ulang), itulah yang sebenarnya disebut "pseudo-labelling" dalam literature. LLM-NER (mengikuti Andrian) **tidak pakai self-training**, melainkan **data augmentation** lewat LLM. Keduanya berbeda konsep meski sama-sama bertujuan memperbanyak data efektif.

---

## 7. Cara Membaca Implementasi Andrian (Untuk Dipelajari)

Urutan baca yang direkomendasikan:
1. **Bab III bagian 3.1 Metode** (hal. 21–33) — gambaran besar
2. **Diagram alir Gambar 3.1, 3.2** — pipeline keseluruhan
3. **Diagram alir Gambar 3.5, 3.6** — detail pelatihan TC vs IFT
4. **Prompt 3.8** (hal. 35) — contoh format prompt yang dipakai untuk IFT
5. **Kode Semu 3.7** (hal. 40) — konfigurasi QLoRA
6. **Kode Semu 3.9** (hal. 41) — training SFTTrainer
7. **Kode Semu 3.12** (hal. 43) — inferensi dengan retry
8. **Bab IV Tabel 4.8 & 4.9** — hasil tanpa vs dengan augmentasi

---

## 8. Daftar Kode Semu (Pseudocode) di Thesis Andrian

| Kode | Deskripsi | Halaman |
|---|---|---|
| 3.1 | Praproses Dataset | 37 |
| 3.2 | Pembuatan Batch untuk KEE-Prompt Generation | 37 |
| 3.3 | Integrasi API dengan OpenAI 4o Mini | 38 |
| 3.4 | Penyaringan Token dan Entitas Unik | 39 |
| 3.5 | Augmentasi Data dengan KEE-Prompt Generation | 39 |
| 3.6 | Pembersihan Data Hasil Augmentasi Entity-to-Text Generation | 40 |
| **3.7** | **QLoRA Model LLM** ⭐ | 40 |
| 3.8 | Pelarasan Hasil Tokenisasi dengan Label | 41 |
| **3.9** | **Pelatihan model menggunakan Instruction Fine-Tuning** ⭐ | 41 |
| 3.10 | Pelatihan model menggunakan Token Classification | 42 |
| 3.11 | Evaluasi Hasil Pelatihan Model | 43 |
| **3.12** | **Inferensi Model menggunakan Instruction Fine-Tuning** ⭐ | 43 |

⭐ = paling penting untuk implementasi LLM-NER.

---

## 9. Daftar Prompt di Thesis Andrian

| Prompt | Deskripsi | Halaman |
|---|---|---|
| 2.1 | Contoh Deskripsi Tugas (KEE) | 12 |
| 2.2 | Contoh Definisi Entitas (KEE) | 12 |
| 2.3 | Contoh Penekanan Tugas (KEE) | 12 |
| 2.4 | Contoh "Contoh Tugas" (few-shot) | 13 |
| 2.5 | Contoh Masukan IFT (English version) | 15 |
| 2.6 | Contoh Luaran IFT | 19 |
| 3.1 | Deskripsi Tugas KEE-Prompt Generation | 24 |
| 3.2 | Penekanan Tugas KEE-Prompt Generation | 28 |
| 3.3 | Definisi Entitas KEE-Prompt Generation | 29 |
| 3.4 | Contoh Tugas KEE-Prompt Generation | 29 |
| 3.5 | Penugasan KEE-Prompt Generation | 29 |
| 3.6 | Tahap Validasi KEE-Prompt Generation | 29 |
| 3.7 | Entity-to-Text Generation | 34 |
| **3.8** | **Input Instruction Fine-Tuning Bahasa Indonesia** ⭐ | 35 |

⭐ = prompt yang dipakai sebagai dasar `ALPACA_PROMPT` di `llm_ner_sirah.py`.
