# SRL-NER Pipeline (BERT + Iterative Self-Training)

Panduan untuk memahami isi `srl_ner_sirah_0.9_colab.ipynb`: apa yang dilakukan tiap bagian, cara membaca outputnya, artinya, dan langkah berikutnya.

---

## 1. Apa yang dilakukan notebook ini?

Notebook melatih **BERT NER** (token classification) untuk Sirah Nabawiyah dengan strategi **iterative self-training (pseudo-labelling)**:

```
seed kecil (train.csv, sudah dilabel manual)
        │
        ▼
   Train BASE model (IndoBERT)
        │
        ▼
┌──────────────────────────────────────────────┐
│  Loop 6 iterasi:                             │
│   1. Predict unlabelled.csv pakai model      │
│   2. Ambil prediksi yang confidence ≥ 0.9    │
│   3. Tambahkan ke train data (cumulative)    │
│   4. Retrain model                           │
└──────────────────────────────────────────────┘
        │
        ▼
   Evaluasi di test.csv
```

**Tujuan:** memperbesar dataset berlabel tanpa anotasi manual tambahan, dengan asumsi prediksi confidence tinggi sudah cukup akurat untuk dipakai sebagai "pseudo ground truth".

---

## 2. Struktur cell di notebook

| Cell # | Fungsi |
|---|---|
| 0 | Markdown judul |
| 1–6 | Install dependency (`transformers`, `accelerate`, `seaborn`) |
| 7 | Import libraries |
| 8 | Markdown: "Load and prepare datasets" |
| 9–10 | Mount Google Drive |
| **11** | **Setup paths** (`dataset_dir`, `model_dir`, `eval_dir`) + load `train.csv` |
| 12 | Smoke test (cek GPU + file CSV) |
| 13 | (NaN check, commented) |
| 14 | Buat `label2id` & `id2label` dari label di train |
| 15 | Markdown |
| 16 | Definisi tokenizer + `tokenize_and_align_labels()` + helper |
| 17 | Tokenisasi train data → HF Dataset |
| 18 | Markdown |
| 19 | Definisi `compute_metrics()` + `train_model()` |
| **20** | **Train BASE model** (35% seed → IndoBERT NER) |
| 21 | Markdown |
| 22 | Definisi `extract_entities_from_result()` + `filter_threshold()` |
| 23 | Markdown ("Confidence 0.9") |
| **24–26** | **Iterasi 1**: load `unlabelled.csv`, predict, filter ≥0.9, retrain |
| **27–32** | **Iterasi 2**: pakai sisa "below 0.9" iter 1, predict, filter, retrain |
| **33–36** | **Iterasi 3** |
| **37–40** | **Iterasi 4** |
| **41–44** | **Iterasi 5** |
| **45–47** | **Iterasi 6** |
| 48 | Markdown |
| 49–50 | Definisi fungsi evaluasi (overall, per-label, confusion matrix, misclassified) |
| 51–55 | **Evaluasi model FINAL** (iterasi 6) di `test.csv` |
| 56–57 | **Evaluasi BASE model** di `test.csv` (untuk perbandingan) |

---

## 3. Output apa saja yang dihasilkan?

Semua tersimpan di Google Drive (`MyDrive/TA-Sirah/output/`):

### `models/`
| Folder | Isi |
|---|---|
| `bert-only-sirah-ner-base/` | Model setelah training awal (cuma seed) |
| `bert-only-sirah-ner-0.9-iteration-2/` | Model setelah iterasi 1 selesai (retrained dgn pseudo-label iter 1) |
| `bert-only-sirah-ner-0.9-iteration-3/` | Model setelah iter 2 |
| ... | ... |
| `bert-only-sirah-ner-0.9-iteration-6/` | **Model FINAL** (setelah 6 iterasi) |

> Catatan: penomoran `iteration-2` agak menyesatkan — folder `iteration-2` artinya model **untuk** iterasi ke-2 (yaitu hasil retraining setelah iter 1). Yang terakhir (`iteration-6`) = paling matang.

### `evaluation/`
| File | Isi |
|---|---|
| `bert-only-sirah-ner-above-0.9.xlsx` | Token + label hasil prediksi iter 1 dengan confidence **≥ 0.9** (dipakai sebagai pseudo-label) |
| `bert-only-sirah-ner-below-0.9.xlsx` | Token yang **gagal lewat threshold** di iter 1 (akan dicoba lagi di iter 2) |
| `bert-only-sirah-ner-iterative-N-above-0.9.xlsx` | Sama, untuk iterasi ke-N (2..6) |
| `bert-only-sirah-ner-iterative-N-below-0.9.xlsx` | Sisa unlabelled setelah iter ke-N |
| `bert-only-sirah-ner-confidence-0.9-misclassified.xlsx` | Token di test set yang model salah prediksi |
| `bert-only-sirah-ner-iterative-6-correct.xlsx` | Token test set yang diprediksi benar |
| `bert-only-sirah-ner-iterative-6-incorrect.xlsx` | Token test set yang salah |
| Confusion matrix heatmap | Inline plot di notebook |

### `datasets/` (di-extend tiap iterasi)
| File | Isi |
|---|---|
| `bert-only-sirah-ner-above-0.9-retraining.csv` | Pseudo-label iter 1 dalam format CoNLL siap retrain |
| `bert-only-sirah-ner-iterative-N-above-0.9-retraining.csv` | Sama, untuk iter ke-N |

---

## 4. Cara membaca hasilnya

### A. Output training (per epoch, di stdout notebook)

```
Epoch  Training Loss  Validation Loss  Precision  Recall  F1
1      0.45           0.32             0.71       0.68    0.69
2      0.21           0.25             0.78       0.76    0.77
...
```

- **Training loss turun, val loss naik** → overfitting (kurangi epoch / pakai early stop)
- **Val loss & F1 stabil** → konvergen, OK
- **F1 < 0.5 di epoch akhir** → seed terlalu kecil atau label tidak konsisten → fix data dulu

### B. File `*-above-0.9.xlsx` & `*-below-0.9.xlsx`

Kolom:
- `text_id` : ID chunk asal
- `tokens`  : daftar token (atau token tunggal kalau sudah di-explode)
- `predicted_label` : label hasil prediksi (`B_PERSON`, `O`, dll)
- `confidence` : skor rata-rata kalimat

**Interpretasi jumlah:**
- `len(above) >> len(below)` di iter 1 → model sudah confident sejak awal (seed cukup representatif)
- `len(above)` sangat kecil → model belum yakin → seed perlu diperbesar
- `len(above)` per iterasi terus naik → self-training "berbuah"; kalau **stagnan/turun** sejak iter 3, berarti loop sudah jenuh — tidak ada gunanya iterasi 4–6

### C. Evaluasi akhir (cell 51–55, 56–57)

Notebook print 2 hal untuk **base** dan **final (iter 6)**:

**1. Overall metrics (weighted):**
```
Accuracy : 0.84
Precision: 0.82
Recall   : 0.84
F1       : 0.83
```

**2. Per-label metrics (`classification_report`):**
```
              precision  recall  f1-score  support
B_PERSON      0.88       0.85    0.87      120
I_PERSON      0.84       0.82    0.83      210
B_LOCATION    0.79       0.76    0.77       65
...
O             0.95       0.97    0.96      1500
```

**Cara baca:**
- **Bandingkan base vs final**: kalau F1 naik → self-training berhasil. Kalau **turun** → pseudo-label memperkenalkan noise (label salah masuk train) → turunkan threshold lebih ketat (0.95?) atau hentikan di iterasi yang masih naik.
- **Per-label**: cek apakah label yang minoritas (`B_TIME`, `B_EVENT`) ikut membaik atau cuma yang mayoritas. Self-training cenderung **memperkuat label mayoritas** dan **mengabaikan minoritas**.
- **Support**: jumlah token per label di test set. Kalau support ≤ 10 → metric per-label tidak reliable.

**3. Confusion matrix heatmap:**
- Diagonal terang = prediksi benar
- Off-diagonal yang terang = pola kesalahan (mis. `B_PERSON` sering ditebak `B_LOCATION` → mungkin nama tempat & nama orang sering tertukar di teks Sirah)

**4. `*-misclassified.xlsx`:**
Ini paling berharga untuk debug. Cek manual ~20 baris:
- Kalau salahnya **konsisten pada pola tertentu** (mis. semua "Bani Quraizah" diprediksi `O`) → label di seed tidak konsisten → fix di `pre_labelling.py`
- Kalau salahnya acak → masalahnya kapasitas model / data terlalu kecil

---

## 5. Apa artinya hasilnya?

Setelah notebook selesai, kamu punya:

1. **Model NER terlatih** untuk Sirah, bisa langsung dipakai untuk extract entitas (PERSON/EVENT/TIME/LOCATION) dari teks Sirah baru
2. **Pseudo-labelled data** (gabungan `*-above-0.9-retraining.csv` semua iterasi) — bisa dipakai sebagai dataset NER yang jauh lebih besar dari seed manual
3. **Baseline metric** (F1 base vs F1 final) → masuk ke laporan TA bab evaluasi

**Yang perlu kamu validasi:**
- Apakah F1 final > F1 base? (kalau tidak, pseudo-labelling **gagal**)
- Apakah peningkatan terjadi di **semua label** atau hanya label tertentu?
- Apakah `len(above)` naik konsisten tiap iterasi atau jenuh? (kalau jenuh di iter 3, iter 4–6 cuma buang waktu)

---

## 6. Langkah berikutnya setelah notebook selesai

### A. Kalau hasilnya bagus (F1 ≥ 0.75, naik dari base):

1. **Pakai model final untuk inferensi semua chunk** Sirah:
   - Load `bert-only-sirah-ner-0.9-iteration-6/`
   - Run prediksi di seluruh `sirah_chunks_final.csv`
   - Hasil: setiap chunk punya daftar entitas → input untuk **Relation Extraction**

2. **Lanjut ke Relation Extraction** (`src/relation_extraction/`):
   - Untuk setiap pasangan entitas dalam satu chunk, klasifikasi relasinya (`berperang_dengan`, `terjadi_di`, `terjadi_pada`, dll.)
   - Bisa pakai SRL, rule-based, atau LLM

3. **Build Knowledge Graph di Neo4j**:
   - Tiap entitas → Node (`:Person`, `:Event`, `:Location`, `:Time`)
   - Tiap relasi → Edge
   - Visualisasi & query graph

### B. Kalau hasilnya kurang bagus:

1. **F1 base sudah jelek (< 0.5)** → masalah di data, bukan di self-training:
   - Cek konsistensi label di `sirah_prelabelled.csv` (`generate_entity_review.py` bisa bantu)
   - Tambah seed manual labelling
   - Cek tokenisasi (apakah subword BERT memecah nama Arab dengan baik?)

2. **F1 base OK tapi final turun** → pseudo-label memperkenalkan noise:
   - Naikkan threshold ke 0.95
   - Kurangi jumlah iterasi (4 sudah cukup)
   - Tambahkan filter: buang prediksi yang seluruh kalimatnya `O` (kemungkinan model "menyerah")

3. **Label minoritas tetap jelek** (`B_EVENT` F1 < 0.3):
   - Class imbalance — coba `class_weight` di loss function
   - Atau augmentasi seed: tambah anotasi manual khusus event

### C. Untuk laporan TA:

Tabel yang wajib ada di bab Evaluasi:
| Model | Precision | Recall | F1 | Δ vs base |
|---|---|---|---|---|
| Base (seed only) | ... | ... | ... | — |
| Iter 1 | ... | ... | ... | +x% |
| Iter 2 | ... | ... | ... | +x% |
| ... | | | | |
| Iter 6 (final) | ... | ... | ... | +x% |

Plus:
- Per-label F1 base vs final (bar chart)
- Confusion matrix final (heatmap)
- Jumlah pseudo-label terkumpul tiap iterasi (line chart)
- Contoh kualitatif: 5 prediksi benar + 5 salah dengan analisis

---

## 7. Troubleshooting cepat

| Error | Sebab | Fix |
|---|---|---|
| `FileNotFoundError: ./result` | `rmtree("./result")` hard-coded | Sudah diperbaiki ke `_trainer_tmp` |
| `Trainer.__init__() got 'tokenizer'` | transformers ≥ 4.46 | Ganti `tokenizer=` → `processing_class=` (sudah dipatch) |
| `DataCollator got 'processing_class'` | Patch terlalu luas | DataCollator tetap pakai `tokenizer=` (sudah direvert) |
| `CUDA out of memory` | Batch terlalu besar | Turunkan `per_device_train_batch_size` ke 8 |
| `ValueError: stratify` | Label di seed kurang dari 2 sampel | Tambah seed atau matikan stratify |
| Loss = NaN | Learning rate ketinggian / label rusak | Cek `label2id` mencakup semua label di data |

---

## 8. Arsitektur "SRL-NER" — apa & pakai model apa?

### Catatan nama
Folder ini bernama **SRL-NER** mengikuti penamaan referensi (notebook asli Bu Diana
`BERT_Only_Percobaan_1_Argument_0.9.ipynb` → kolom labelnya bernama `argument`,
yang merujuk pada **argumen-argumen dalam Semantic Role Labeling**: ARG0, ARG1, dst.).

**Tapi sebenarnya arsitekturnya bukan SRL klasik** (yang punya parser sintaksis +
predicate identification + argument classification). Yang dipakai adalah:

> **BERT token classification dengan tagging BIO**, dilatih lewat *iterative
> self-training* (pseudo-labelling threshold 0.9).

Skema arsitekturnya:

```
Input teks chunk
       │
       ▼
┌─────────────────────────┐
│ WordPiece Tokenizer     │   indolem/indobert-base-uncased
│ (sub-word splitting)    │
└─────────────────────────┘
       │  → token IDs + attention mask
       ▼
┌─────────────────────────┐
│ IndoBERT Encoder        │   12 layer transformer, hidden=768
│ (pretrained Bahasa Indo)│
└─────────────────────────┘
       │  → contextual embedding tiap token (768-d)
       ▼
┌─────────────────────────┐
│ Linear classification   │   Dense(768 → num_labels)
│ head (token-level)      │   num_labels = jumlah tag BIO
└─────────────────────────┘
       │  → softmax → label tiap token
       ▼
   B-PERSON  I-PERSON  O  O  B-LOCATION  ...
```

### Tahapan pipeline (high-level)

| Tahap | Modul | Output |
|---|---|---|
| 1. Pretrained model | `AutoModelForTokenClassification.from_pretrained("indolem/indobert-base-uncased")` | weights awal |
| 2. Tokenisasi seed | `AutoTokenizer` + `tokenize_and_align_labels()` | input_ids + label_ids |
| 3. Train base | HF `Trainer` (lr=2e-5, batch=16, epoch=10) | model base |
| 4. Pseudo-label | `pipeline("ner", aggregation_strategy="simple")` + `filter_threshold(0.9)` | above-0.9.xlsx, below-0.9.xlsx |
| 5. Retrain (cumulative) | `Trainer` ulang, train += above_iter_n | model iter-N |
| 6. Loop 6× | Iter 2..6 pakai sisa below dari iter sebelumnya | model final iter-6 |
| 7. Evaluasi | `seqeval` / classification_report | precision/recall/F1 per label |

### Model yang dipakai

| Komponen | Nama | Kenapa |
|---|---|---|
| Encoder | **`indolem/indobert-base-uncased`** | Pretrained khusus Bahasa Indonesia, masuk akal karena teks Sirah terjemahan Indonesia |
| Tokenizer | `AutoTokenizer` (WordPiece) | Bawaan IndoBERT, vocab Indonesian umum |
| Task head | `AutoModelForTokenClassification` | Token-level classification (BIO tagging) |
| Trainer | HuggingFace `Trainer` | Standar HF |
| Pipeline inferensi | `transformers.pipeline("ner")` | Wrapper untuk predict + entity grouping |

**Catatan model:** IndoBERT-base **bukan** model yang khusus dilatih untuk teks
keagamaan / nama Arab. Vocab-nya umum, jadi nama-nama Arab seperti "Yasar",
"Quraizah", "Khadijah" akan dipecah jadi banyak sub-word (lihat §9).

---

## 9. Kenapa output saya muncul `##ar bin yas` dan sejenisnya?

### Penyebab: WordPiece sub-word tokenization

BERT (termasuk IndoBERT) tidak bekerja di level kata, tapi di level **sub-word**.
Tokenizer WordPiece akan memecah kata yang **tidak ada di vocab** menjadi pecahan
yang lebih kecil:

```
Input  : "Yasar bin Suraqah"
Token  : ["yas", "##ar", "bin", "sur", "##aq", "##ah"]
            ↑       ↑              ↑      ↑      ↑
            kata    lanjutan       kata   lanjutan...
            baru
```

Awalan `##` artinya **"sub-word lanjutan dari token sebelumnya"** — bukan kata
mandiri. Saat di-decode kembali, harusnya mereka digabung jadi `"yasar"` & `"suraqah"`.

Output `##ar bin yas` muncul karena:
1. Nama "Yasar" tidak ada di vocab IndoBERT → dipecah jadi `["yas", "##ar"]`
2. Saat menampilkan hasil prediksi (`extract_entities_from_result()` /
   pipeline NER), kode mengambil **token versi tokenizer** (sub-word), bukan token
   asli dari `unlabelled.csv`
3. `aggregation_strategy="simple"` di pipeline tidak selalu berhasil menggabung
   sub-word kalau label antar sub-word berbeda atau scorenya tidak konsisten

Jadi yang kamu lihat adalah **artefak tampilan**, bukan label yang salah.
Modelnya tetap memprediksi label per sub-word; cuma cara menampilkannya yang
masih berupa potongan WordPiece.

### Apakah ini karena saya pakai Span labelling, bukan BIO?

**Bukan.** Ini perlu dipisah jadi 2 hal yang berbeda:

| Aspek | Span labelling | BIO labelling |
|---|---|---|
| **Format anotasi** | `(start_char, end_char, label)` | Tag per token: `B-X / I-X / O` |
| **Tujuan** | Cara menyimpan anotasi | Cara training model |
| **Bisa dikonversi?** | ✅ Ya, `prepare_bert_data.py` melakukannya |

Kamu **sebenarnya juga pakai BIO** — span labelling cuma format anotasi awalnya.
Lihat alurnya:

```
sirah_prelabelled.csv          (span: start_char, end_char, entity_text, label)
        │
        ▼  prepare_bert_data.py:
        │   - tokenize_with_offsets()  → kata + posisi karakter
        │   - assign_bio_label()       → konversi span → BIO per kata
        ▼
train.csv / test.csv / unlabelled.csv   (BIO: B-PERSON, I-PERSON, O, ...)
        │
        ▼
Notebook BERT (yang dipakai sekarang) → BIO sudah jadi input training
```

Jadi pendekatan kamu **identik** dengan referensi: sama-sama BIO di level training.
Span labelling cuma "format anotasi mentah" yang lebih fleksibel & gampang
divalidasi manual; sebelum masuk model selalu di-konversi ke BIO dulu.

### Penyebab sebenarnya (rangkuman)

`##ar bin yas` muncul karena **3 hal yang sama sekali tidak terkait dengan span vs BIO**:

1. **WordPiece sub-word splitting** — IndoBERT memecah nama Arab yang tidak ada
   di vocab. Ini sifat dasar tokenizer BERT, bukan bug.
2. **Pipeline output menampilkan sub-word, bukan kata original** — fungsi
   `extract_entities_from_result()` mengambil string dari output `pipeline("ner")`
   yang isinya sudah versi sub-word.
3. **`aggregation_strategy="simple"` kadang gagal merge** — kalau label antar
   sub-word ("yas" diprediksi `B-PERSON`, "##ar" diprediksi `O`), sub-word tidak
   digabung.

### Cara fix

**Opsi 1 — Ganti aggregation strategy** (1 baris):
Cari pipeline NER di cell `filter_threshold` (cell ~22), ganti:
```python
nlp = pipeline("ner", model=..., tokenizer=..., aggregation_strategy="simple")
```
jadi:
```python
nlp = pipeline("ner", model=..., tokenizer=..., aggregation_strategy="first")
```

Strategi pilihan:
- `"first"` → ambil label dari sub-word pertama, paling stabil untuk NER
- `"max"`   → ambil sub-word dengan confidence tertinggi
- `"average"` → rata-rata semua sub-word

**Opsi 2 — Post-processing manual** (lebih eksplisit):
Tambahkan helper untuk merge sub-word `##`:
```python
def merge_subwords(tokens, labels):
    out_tok, out_lab = [], []
    for t, l in zip(tokens, labels):
        if t.startswith("##") and out_tok:
            out_tok[-1] += t[2:]
        else:
            out_tok.append(t); out_lab.append(l)
    return out_tok, out_lab
```

**Opsi 3 — Map balik ke kata original** (paling benar tapi paling banyak ubah):
Jangan tampilkan token dari pipeline output. Pakai `text_id` + index untuk
ambil kata dari `unlabelled.csv` (kolom `token` aslinya). Hasilnya selalu kata
utuh karena `prepare_bert_data.py` sudah split per kata, bukan per sub-word.

### Catatan jangka panjang

Kalau nama Arab sangat banyak dan model sering "ragu" di sub-word, pertimbangkan
ganti encoder dari `indolem/indobert-base-uncased` ke yang vocab-nya lebih
multilingual / mengandung istilah Arab:

- `bert-base-multilingual-cased` (mBERT, vocab 104 bahasa)
- `xlm-roberta-base` (lebih besar vocab, lebih baik di nama asing)
- `cahya/bert-base-indonesian-1.5G` (alternatif IndoBERT, vocab beda)

Tapi ini optimization opsional — fix display dulu (Opsi 1), evaluasi metric F1
nya berapa, baru putuskan apakah perlu ganti model.

---

## 11. Ringkasan singkat

> Notebook ini melatih NER BERT dari seed kecil, lalu memperbesar dataset secara otomatis dengan memprediksi data unlabelled dan mengambil prediksi yang yakin (≥0.9), diulang 6×. Hasilnya: model NER untuk Sirah + dataset pseudo-labelled. Yang penting kamu cek: **F1 final harus naik dari base**, dan peningkatan harus terjadi di **semua label**, bukan hanya yang mayoritas. Setelah itu, model siap dipakai untuk inferensi seluruh corpus Sirah → input ke Relation Extraction → Knowledge Graph di Neo4j.
