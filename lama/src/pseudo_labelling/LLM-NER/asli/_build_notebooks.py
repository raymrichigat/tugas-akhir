"""
Generator script untuk membuat 2 notebook BASELINE SUPERVISED (metode asli Andrian):
  - llm_ner_sirah_colab.ipynb   (Google Colab)
  - llm_ner_sirah_kaggle.ipynb  (Kaggle)

Ini adalah versi single-shot training sesuai metode asli di thesis Andrian
(tanpa iterative self-training). Dijalankan sekali untuk timpa file lama.
Idempotent — bisa di-rerun untuk regenerate.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

ALPACA_PROMPT_CELL = '''ALPACA_PROMPT = """Di bawah ini adalah sebuah instruksi yang menjelaskan tugas, dipasangkan dengan sebuah masukan yang memberikan konteks lebih lanjut. Tulislah respons yang sesuai untuk menyelesaikan permintaan tersebut.

### Instruksi:
Anda adalah seorang ahli linguistik berpengalaman dalam Named Entity Recognition (NER) dan mampu mengidentifikasi entitas dalam berbagai gaya teks, mulai dari narasi sejarah formal hingga teks deskriptif. Tugas Anda adalah mengekstrak token entitas dalam format BIO (Begin, Inside, Outside) dari teks yang diberikan. Jenis entitas yang dikenali meliputi: Tokoh (PERSON), Peristiwa (EVENT), Lokasi (LOCATION), dan Waktu (TIME).
Ikuti ketentuan berikut:
1. Berikan output dalam bentuk daftar token yang dilabeli dengan jenis entitasnya menggunakan format BIO. Gunakan "B-" untuk awal entitas, "I-" untuk bagian dalam entitas, dan "O" untuk token yang bukan bagian dari entitas.
2. Pastikan jumlah label entitas sama dengan jumlah token dalam setiap data teks.
3. Labeli token yang bukan entitas dengan "O" (Outside).
4. Nama tokoh yang mengandung nasab (bin/binti/ibnu) harus dilabeli sebagai satu entitas PERSON utuh (semua token B-PERSON/I-PERSON).
5. Kenali jenis entitas dengan akurat baik dalam narasi sejarah formal maupun teks deskriptif.
6. Pastikan panjang daftar label entitas yang dihasilkan sama dengan panjang daftar token input.

### Definisi Entitas:
-PERSON (Tokoh): Token atau frasa yang merujuk pada nama individu, tokoh sejarah, nabi, sahabat, atau nama kabilah/Bani (misalnya, "Muhammad", "Abu Bakar", "Bani Quraisy").
-EVENT (Peristiwa): Token atau frasa yang menggambarkan peristiwa bersejarah (misalnya, "Perang Badr", "Hijrah", "Perjanjian Hudaibiyah").
-LOCATION (Lokasi): Tempat spesifik seperti kota, wilayah, gunung, atau bangunan (misalnya, "Makkah", "Madinah", "Gua Hira", "Bukit Uhud").
-TIME (Waktu): Elemen temporal seperti tahun, bulan, periode, atau penanda waktu (misalnya, "tahun ke-10 kenabian", "bulan Ramadhan", "6 H").

### Input:
{}
<|eot_id|>
### Respons:
{}"""

EOS_TOKEN = "<|eot_id|>"'''


HYPERPARAM_CELL = '''# Konfigurasi model — pilih salah satu
MODEL_NAME = "GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct"  # Best for Indonesian
# MODEL_NAME = "aisingapore/llama3-8b-cpt-sea-lionv3-instruct"  # Multilingual SEA
# MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"               # Base

MODEL_OUTPUT_DIR = str(OUT_DIR / "model_output")

# Konfigurasi training (sama persis Andrian)
BATCH_SIZE = 16
NUM_EPOCHS = 30
LEARNING_RATE = 1e-4
MAX_SEQ_LENGTH = 512

# Konfigurasi QLoRA (Tabel 4.5 Andrian)
LORA_R = 64
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

# Konfigurasi inferensi
MAX_RETRIES = 5
MAX_NEW_TOKENS = 512

print(f"Model: {MODEL_NAME}")
print(f"Training: epochs={NUM_EPOCHS}, batch={BATCH_SIZE}, lr={LEARNING_RATE}")'''


DATA_LOADING_CELL = '''import pandas as pd
from sklearn.model_selection import train_test_split

def load_conll_data(filepath):
    df = pd.read_csv(filepath, encoding="utf-8")
    has_label = "label" in df.columns
    subset = ["token", "label"] if has_label else ["token"]
    df = df.dropna(subset=subset)
    grouped = df.groupby("text_id", sort=False)
    sentences = []
    for text_id, group in grouped:
        tokens = group["token"].tolist()
        labels = group["label"].tolist() if has_label else ["O"] * len(tokens)
        if len(tokens) == len(labels) and len(tokens) > 2:
            sentences.append({"text_id": text_id, "tokens": tokens, "labels": labels})
    return sentences

train_sentences = load_conll_data(IN_TRAIN)
test_sentences = load_conll_data(IN_TEST)
print(f"Loaded: train={len(train_sentences)}, test={len(test_sentences)}")

# Deduplikasi train
seen = set()
deduped = []
for s in train_sentences:
    key = (tuple(s["tokens"]), tuple(s["labels"]))
    if key not in seen:
        seen.add(key)
        deduped.append(s)
train_sentences = deduped

# Split 80/20
train_split, val_split = train_test_split(train_sentences, test_size=0.2, random_state=42)
print(f"After split: train={len(train_split)}, val={len(val_split)}, test={len(test_sentences)}")

# Format ke Alpaca prompt
def format_to_alpaca(sentences):
    rows = []
    for s in sentences:
        text = ALPACA_PROMPT.format(str(s["tokens"]), str(s["labels"])) + EOS_TOKEN
        rows.append({"text_id": s["text_id"], "text": text, "tokens": s["tokens"], "labels": s["labels"]})
    return pd.DataFrame(rows)

train_df = format_to_alpaca(train_split)
val_df = format_to_alpaca(val_split)
test_df = format_to_alpaca(test_sentences)

print(f"\\nContoh prompt (500 char pertama):")
print(train_df.iloc[0]["text"][:500])'''


SETUP_MODEL_CELL = '''# Setup model + QLoRA via Unsloth (Kode Semu 3.7 Andrian)
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    bias="none",
    use_gradient_checkpointing="unsloth",
)

print(f"Model loaded: {MODEL_NAME}")
model.print_trainable_parameters()'''


TRAIN_CELL = '''# Training dengan SFTTrainer (Kode Semu 3.9 Andrian)
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from trl import SFTTrainer
from datasets import Dataset

train_dataset = Dataset.from_pandas(train_df[["text"]])
val_dataset = Dataset.from_pandas(val_df[["text"]])

training_args = TrainingArguments(
    output_dir=MODEL_OUTPUT_DIR,
    save_strategy="no",
    eval_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=NUM_EPOCHS,
    logging_steps=10,
    fp16=True,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=False,
    dataset_num_proc=2,
    data_collator=DataCollatorForSeq2Seq(tokenizer),
)

print("Starting training...")
trainer.train()
print("Training complete!")'''


INFERENCE_CELL = '''# Inferensi dengan retry mechanism (Kode Semu 3.12 Andrian)
import ast
import torch
from tqdm import tqdm

FastLanguageModel.for_inference(model)
predictions = []

for idx, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Inference"):
    token_input = row["tokens"]
    prompt = ALPACA_PROMPT.format(str(token_input), "")
    response_list = []
    attempt = 0

    while len(response_list) != len(token_input) and attempt < MAX_RETRIES:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, use_cache=True, do_sample=False)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=False)

        if "### Respons:" in decoded:
            response_text = decoded.split("### Respons:")[-1].strip().replace(EOS_TOKEN, "").strip()
        else:
            response_text = ""

        try:
            response_list = ast.literal_eval(response_text)
            if not isinstance(response_list, list):
                response_list = []
        except (ValueError, SyntaxError):
            response_list = []
        attempt += 1

    # Padding/truncate fallback
    if len(response_list) != len(token_input):
        if len(response_list) > len(token_input):
            response_list = response_list[:len(token_input)]
        else:
            response_list.extend(["O"] * (len(token_input) - len(response_list)))

    predictions.append(response_list)

print(f"Inference complete: {len(predictions)} predictions")'''


EVAL_CELL = '''# Evaluasi seqeval (Kode Semu 3.11 Andrian)
import evaluate

y_true = test_df["labels"].tolist()
y_pred = predictions

metric = evaluate.load("seqeval")
all_metrics = metric.compute(predictions=y_pred, references=y_true)

print("=" * 50)
print("EVALUASI LLM-NER (Metode Asli Andrian)")
print("=" * 50)
print(f"Precision: {all_metrics['overall_precision']:.4f}")
print(f"Recall   : {all_metrics['overall_recall']:.4f}")
print(f"F1-score : {all_metrics['overall_f1']:.4f}")
print(f"Accuracy : {all_metrics['overall_accuracy']:.4f}")

for entity_type in ["PERSON", "EVENT", "LOCATION", "TIME"]:
    if entity_type in all_metrics:
        e = all_metrics[entity_type]
        print(f"  {entity_type:10s}: P={e['precision']:.4f} R={e['recall']:.4f} F1={e['f1']:.4f} (n={e['number']})")'''


SAVE_CELL = '''# Simpan output
rows = []
for i, (_, row) in enumerate(test_df.iterrows()):
    tokens = row["tokens"]
    true_labels = row["labels"]
    pred_labels = predictions[i]
    for j, token in enumerate(tokens):
        rows.append({
            "text_id": row["text_id"],
            "token": token,
            "true_label": true_labels[j] if j < len(true_labels) else "O",
            "pred_label": pred_labels[j] if j < len(pred_labels) else "O",
        })
pred_df = pd.DataFrame(rows)
pred_path = OUT_DIR / "llm_ner_predictions.csv"
pred_df.to_csv(pred_path, index=False, sep=";", encoding="utf-8-sig")
print(f"Predictions: {pred_path}")

metrics_path = OUT_DIR / "llm_ner_metrics.txt"
with open(metrics_path, "w", encoding="utf-8") as f:
    f.write(f"Model: {MODEL_NAME}\\n")
    f.write(f"Epochs: {NUM_EPOCHS}\\n")
    f.write(f"Precision: {all_metrics['overall_precision']:.4f}\\n")
    f.write(f"Recall: {all_metrics['overall_recall']:.4f}\\n")
    f.write(f"F1-score: {all_metrics['overall_f1']:.4f}\\n")
    f.write(f"Accuracy: {all_metrics['overall_accuracy']:.4f}\\n")
    for entity_type in ["PERSON", "EVENT", "LOCATION", "TIME"]:
        if entity_type in all_metrics:
            e = all_metrics[entity_type]
            f.write(f"\\n{entity_type}: P={e['precision']:.4f} R={e['recall']:.4f} F1={e['f1']:.4f} n={e['number']}\\n")
print(f"Metrics: {metrics_path}")
print("\\nSelesai!")'''


def colab_cells():
    return [
        ("md", '''# LLM-NER Sirah Nabawiyah — Metode Asli Andrian (Baseline)

**Metodologi:** Mengikuti thesis Andrian (5025211079, pembimbing Prof. Dr. Diana Purwitasari) — Instruction Fine-Tuning + QLoRA, **single-shot training tanpa augmentasi atau self-training**.

**Entitas:** PERSON, EVENT, LOCATION, TIME

**Platform:** Google Colab (GPU T4/A100)

---

## Setup

1. Upload `train.csv` dan `test.csv` ke `MyDrive/TA-Sirah/data/`
2. Run all cells berurutan
3. Output ke `MyDrive/TA-Sirah/output/LLM-NER/asli/`

**Estimasi waktu:** ~1-2 jam (T4) / ~30 menit (A100) — single training cycle.

> Notebook ini = **baseline pure Andrian**. Untuk versi self-training (TA), pakai notebook di folder `pseudo/`.'''),
        ("code", '''# Cell 1: Install dependencies
!pip install -q unsloth
!pip install -q --no-deps trl peft accelerate bitsandbytes
!pip install -q seqeval evaluate scikit-learn'''),
        ("code", '''# Cell 2: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')'''),
        ("code", '''# Cell 3: Konfigurasi path (Colab)
from pathlib import Path

DRIVE_BASE = Path("/content/drive/MyDrive/TA-Sirah")
IN_TRAIN = DRIVE_BASE / "data" / "train.csv"
IN_TEST = DRIVE_BASE / "data" / "test.csv"
OUT_DIR = DRIVE_BASE / "output" / "LLM-NER" / "asli"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Train:  {IN_TRAIN} (exists: {IN_TRAIN.exists()})")
print(f"Test:   {IN_TEST} (exists: {IN_TEST.exists()})")
print(f"Output: {OUT_DIR}")'''),
        ("code", "# Cell 4: Hyperparameters\n" + HYPERPARAM_CELL),
        ("code", "# Cell 5: Prompt Alpaca (Bahasa Indonesia, Prompt 3.8 Andrian)\n" + ALPACA_PROMPT_CELL),
        ("code", "# Cell 6: Load data + format helpers\n" + DATA_LOADING_CELL),
        ("code", "# Cell 7: Setup model + QLoRA\n" + SETUP_MODEL_CELL),
        ("code", "# Cell 8: Training\n" + TRAIN_CELL),
        ("code", "# Cell 9: Inference\n" + INFERENCE_CELL),
        ("code", "# Cell 10: Evaluasi\n" + EVAL_CELL),
        ("code", "# Cell 11: Save output\n" + SAVE_CELL),
    ]


def kaggle_cells():
    return [
        ("md", '''# LLM-NER Sirah Nabawiyah — Metode Asli Andrian (Baseline)

**Metodologi:** Mengikuti thesis Andrian (5025211079, pembimbing Prof. Dr. Diana Purwitasari) — Instruction Fine-Tuning + QLoRA, **single-shot training tanpa augmentasi atau self-training**.

**Entitas:** PERSON, EVENT, LOCATION, TIME

**Platform:** Kaggle (P100 / T4 x2 / A100)

---

## Setup

1. Buat Dataset Kaggle bernama `sirah-ner-llm` berisi `train.csv` dan `test.csv`
2. Add Dataset ke notebook (sidebar → Add Data)
3. Aktifkan GPU di Settings (P100 minimal)
4. Run all cells berurutan
5. Output ke `/kaggle/working/LLM-NER/asli/`

**Estimasi waktu:** ~1-2 jam (P100) / ~30 menit (A100).

> Notebook ini = **baseline pure Andrian**. Untuk versi self-training (TA), pakai notebook di folder `pseudo/`.'''),
        ("code", '''# Cell 1: Install dependencies
!pip install -q unsloth
!pip install -q --no-deps trl peft accelerate bitsandbytes
!pip install -q seqeval evaluate scikit-learn'''),
        ("code", '''# Cell 2: Konfigurasi path (Kaggle)
from pathlib import Path

KAGGLE_INPUT = Path("/kaggle/input/sirah-ner-llm")
IN_TRAIN = KAGGLE_INPUT / "train.csv"
IN_TEST = KAGGLE_INPUT / "test.csv"

OUT_DIR = Path("/kaggle/working/LLM-NER/asli")
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Train:  {IN_TRAIN} (exists: {IN_TRAIN.exists()})")
print(f"Test:   {IN_TEST} (exists: {IN_TEST.exists()})")
print(f"Output: {OUT_DIR}")'''),
        ("code", "# Cell 3: Hyperparameters\n" + HYPERPARAM_CELL),
        ("code", "# Cell 4: Prompt Alpaca (Bahasa Indonesia, Prompt 3.8 Andrian)\n" + ALPACA_PROMPT_CELL),
        ("code", "# Cell 5: Load data + format helpers\n" + DATA_LOADING_CELL),
        ("code", "# Cell 6: Setup model + QLoRA\n" + SETUP_MODEL_CELL),
        ("code", "# Cell 7: Training\n" + TRAIN_CELL),
        ("code", "# Cell 8: Inference\n" + INFERENCE_CELL),
        ("code", "# Cell 9: Evaluasi\n" + EVAL_CELL),
        ("code", "# Cell 10: Save output\n" + SAVE_CELL),
    ]


def build_notebook(cells_spec):
    cells = []
    for kind, source in cells_spec:
        if kind == "md":
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": source.split("\n"),
            })
        else:
            cells.append({
                "cell_type": "code",
                "metadata": {},
                "source": source.split("\n"),
                "execution_count": None,
                "outputs": [],
            })
    for c in cells:
        src = c["source"]
        for i in range(len(src) - 1):
            src[i] = src[i] + "\n"
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


def main():
    colab_nb = build_notebook(colab_cells())
    kaggle_nb = build_notebook(kaggle_cells())

    colab_path = HERE / "llm_ner_sirah_colab.ipynb"
    kaggle_path = HERE / "llm_ner_sirah_kaggle.ipynb"

    with open(colab_path, "w", encoding="utf-8") as f:
        json.dump(colab_nb, f, indent=1, ensure_ascii=False)
    with open(kaggle_path, "w", encoding="utf-8") as f:
        json.dump(kaggle_nb, f, indent=1, ensure_ascii=False)

    print(f"Wrote: {colab_path}")
    print(f"Wrote: {kaggle_path}")


if __name__ == "__main__":
    main()
