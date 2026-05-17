# Seqeval Addendum — Tinggal Paste ke Akhir Notebook Colab S2a / S2b

> **Tujuan:** Dapatkan F1 **entity-level** (seqeval) untuk S2a iter-6 + S2b iter-6 supaya bisa head-to-head dengan S1 baseline (yang punya F1 entity seqeval = 0.9587).
>
> **Cara pakai:** Buka notebook Colab kamu (`srl_ner_sirah_S2a_scl_colab.ipynb` atau `srl_ner_sirah_S2b_jscl_colab.ipynb`) di Colab, scroll ke bagian akhir. Setelah cell yang menampilkan `classification_report` di iter-6 (cell evaluation existing), **tambah 3 cell baru di bawah ini**. Tidak perlu re-train, tidak perlu re-run cell sebelumnya — variabel `df_test` sudah punya `predicted_label`.

---

## Cell 1 — Install seqeval

```python
!pip install -q seqeval
```

## Cell 2 — Re-evaluate dengan Seqeval (Entity-Level)

```python
# Seqeval addendum — entity-level F1 (span-based), bukan token-level sklearn.
# Pakai df_test yang sudah punya kolom 'predicted_label' dari cell evaluation iter-6.

from seqeval.metrics import (
    classification_report as seq_classification_report,
    f1_score as seq_f1_score,
    precision_score as seq_precision_score,
    recall_score as seq_recall_score,
)

# Guard: pastikan df_test punya kolom predicted_label
assert "predicted_label" in df_test.columns, \
    "df_test belum di-predict. Run cell 'get_predicted_label_on_test_dataset(...)' iter-6 dulu."

def bio_to_dash(label: str) -> str:
    """seqeval mengharapkan B-X / I-X (dash), notebook pakai B_X / I_X (underscore)."""
    if isinstance(label, str) and label.startswith(("B_", "I_")):
        return label.replace("_", "-", 1)
    return label

# Group per text_id → list-of-list, sesuai format seqeval
true_seqs, pred_seqs = [], []
for tid in df_test["text_id"].unique():
    sub = df_test[df_test["text_id"] == tid]
    true_seqs.append([bio_to_dash(l) for l in sub["label"].astype(str).tolist()])
    pred_seqs.append([bio_to_dash(l) for l in sub["predicted_label"].astype(str).tolist()])

# Metric ringkasan
seq_f1 = seq_f1_score(true_seqs, pred_seqs)
seq_p = seq_precision_score(true_seqs, pred_seqs)
seq_r = seq_recall_score(true_seqs, pred_seqs)

print(f"=== Seqeval entity-level — {experiment_name} iter-6 ===")
print(f"F1 entity    : {seq_f1:.4f}")
print(f"Precision    : {seq_p:.4f}")
print(f"Recall       : {seq_r:.4f}")
print()
print(seq_classification_report(true_seqs, pred_seqs, digits=4))
```

## Cell 3 — (Opsional) Eval untuk Base Model Juga

```python
# Kalau mau angka base model juga (untuk plot base→iter-6 trajectory).
# df_test_base sudah punya predicted_label dari cell evaluation existing base.

if "df_test_base" in dir() and "predicted_label" in df_test_base.columns:
    true_seqs_b, pred_seqs_b = [], []
    for tid in df_test_base["text_id"].unique():
        sub = df_test_base[df_test_base["text_id"] == tid]
        true_seqs_b.append([bio_to_dash(l) for l in sub["label"].astype(str).tolist()])
        pred_seqs_b.append([bio_to_dash(l) for l in sub["predicted_label"].astype(str).tolist()])

    seq_f1_b = seq_f1_score(true_seqs_b, pred_seqs_b)
    print(f"=== Seqeval entity-level — {experiment_name} BASE ===")
    print(f"F1 entity    : {seq_f1_b:.4f}")
    print(f"Precision    : {seq_precision_score(true_seqs_b, pred_seqs_b):.4f}")
    print(f"Recall       : {seq_recall_score(true_seqs_b, pred_seqs_b):.4f}")
    print()
    print(seq_classification_report(true_seqs_b, pred_seqs_b, digits=4))
else:
    print("[skip] df_test_base belum di-predict — jalankan cell evaluation base dulu kalau perlu.")
```

---

## Kalau df_test Belum Di-predict (Karena Restart Runtime)

Kalau kamu restart runtime Colab dan variabel `df_test` hilang, jalankan cell ini dulu sebelum 3 cell di atas:

```python
# Re-load test set dari Drive (asumsi path Colab standar yang dipakai notebook)
import os
import pandas as pd

dataset_dir = os.path.join(root_dir, 'dataset')  # root_dir dari cell awal notebook
df_test = pd.read_csv(os.path.join(dataset_dir, "test.csv"))
df_test["token"] = df_test["token"].astype(str)

# Predict ulang dengan model iter-6 final
get_predicted_label_on_test_dataset(
    model_path=os.path.join(model_dir, f"{experiment_name}-0.9-iteration-6"),
    df=df_test,
)
```

Setelah itu langsung jalankan Cell 1 + 2 + 3 di atas.

---

## Output yang Diharapkan

Setelah jalan, kamu akan dapat output seperti ini di Colab (contoh format):

```
=== Seqeval entity-level — bert-only-sirah-ner-S2b-jscl iter-6 ===
F1 entity    : 0.9XXX
Precision    : 0.9XXX
Recall       : 0.9XXX

              precision    recall  f1-score   support

       EVENT     0.XXXX    0.XXXX    0.XXXX        47
    LOCATION     0.XXXX    0.XXXX    0.XXXX       449
      PERSON     0.XXXX    0.XXXX    0.XXXX      1189
        TIME     0.XXXX    0.XXXX    0.XXXX        74

   micro avg     0.XXXX    0.XXXX    0.XXXX      1759
   macro avg     0.XXXX    0.XXXX    0.XXXX      1759
weighted avg    0.XXXX    0.XXXX    0.XXXX      1759
```

Angka **F1 EVENT entity-level** dari report di atas yang akan dibandingkan dengan F1 EVENT S1 = 0.816.

---

## Setelah Dapat Angka

Tinggal paste angka ke `bimbingan_2026_05_13.md` §2.2 sebagai baris baru, atau tulis ringkasan kecil di `done_running/analisis_skenario_S2_S3.md` (file template sudah ada).
