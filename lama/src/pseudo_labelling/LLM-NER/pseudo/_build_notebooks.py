"""
Generator script untuk membuat 2 notebook self-training:
  - llm_ner_sirah_colab.ipynb   (Google Colab)
  - llm_ner_sirah_kaggle.ipynb  (Kaggle)

Dijalankan sekali untuk timpa file lama. Idempotent — bisa di-rerun untuk regenerate.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# ── Shared cells (sama untuk Colab + Kaggle) ──────────────────────────────────

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

# Konfigurasi training
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
MAX_SEQ_LENGTH = 512
EPOCHS_PER_ITER = 10  # lebih kecil dari baseline (30) krn iteratif

# Konfigurasi QLoRA
LORA_R = 64
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

# Konfigurasi inferensi
MAX_RETRIES = 5
MAX_NEW_TOKENS = 512

# Konfigurasi self-training
MAX_ITERATIONS = 5      # batas iterasi
MIN_CONFIDENCE = 0.85   # threshold avg token probability (0-1)
SAMPLING_RATE = 0.5     # ambil top-K% kalimat per iter (anti-noise)
MIN_NEW_SAMPLES = 50    # stop kalau filter < ini
MIN_F1_DELTA = 0.01     # stop kalau peningkatan val F1 < ini

print(f"Model: {MODEL_NAME}")
print(f"Self-training: max_iter={MAX_ITERATIONS}, min_conf={MIN_CONFIDENCE}, sampling={SAMPLING_RATE}")'''


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

def format_to_alpaca(sentences):
    rows = []
    for s in sentences:
        text = ALPACA_PROMPT.format(str(s["tokens"]), str(s["labels"])) + EOS_TOKEN
        rows.append({"text_id": s["text_id"], "text": text, "tokens": s["tokens"], "labels": s["labels"]})
    return pd.DataFrame(rows)

# Load seed train + test
train_sentences = load_conll_data(IN_TRAIN)
test_sentences = load_conll_data(IN_TEST)

# Deduplikasi train
seen = set()
deduped = []
for s in train_sentences:
    key = (tuple(s["tokens"]), tuple(s["labels"]))
    if key not in seen:
        seen.add(key)
        deduped.append(s)
train_sentences = deduped

# Split 80/20 (val_split fixed across iter karena random_state=42)
train_split, val_split = train_test_split(train_sentences, test_size=0.2, random_state=42)

train_df = format_to_alpaca(train_split)
val_df = format_to_alpaca(val_split)
test_df = format_to_alpaca(test_sentences)

# Load unlabelled pool (semua awalnya bukan train)
unlabelled_sentences = load_conll_data(IN_UNLABELLED)
unlabelled_df = format_to_alpaca(unlabelled_sentences)

print(f"Seed train: {len(train_df)}")
print(f"Val (held-out, fixed): {len(val_df)}")
print(f"Test: {len(test_df)}")
print(f"Unlabelled pool: {len(unlabelled_df)}")'''


HELPERS_CELL = '''import ast
import math
import gc
import torch
from tqdm import tqdm
from unsloth import FastLanguageModel
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from trl import SFTTrainer
from datasets import Dataset
import evaluate

seqeval_metric = evaluate.load("seqeval")


def setup_model_fresh():
    """Inisialisasi ulang model + LoRA dari base. Dipanggil tiap iterasi."""
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
    return model, tokenizer


def train_one_iter(model, tokenizer, train_df_iter, val_df, iter_idx, model_output_dir):
    """Train satu iterasi. Returns trained model."""
    train_dataset = Dataset.from_pandas(train_df_iter[["text"]])
    val_dataset = Dataset.from_pandas(val_df[["text"]])

    training_args = TrainingArguments(
        output_dir=str(model_output_dir / f"iter{iter_idx}"),
        save_strategy="no",
        eval_strategy="epoch",
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS_PER_ITER,
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
    trainer.train()
    return trainer


def inference_with_confidence(model, tokenizer, df, desc="Infer"):
    """Inferensi + confidence scoring per kalimat."""
    FastLanguageModel.for_inference(model)
    predictions, confidences = [], []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc=desc):
        token_input = row["tokens"]
        prompt = ALPACA_PROMPT.format(str(token_input), "")
        response_list = []
        base_conf = 0.0
        attempt = 0
        needed_fallback = False

        while len(response_list) != len(token_input) and attempt < MAX_RETRIES:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_len = inputs.input_ids.shape[1]
            with torch.no_grad():
                try:
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=MAX_NEW_TOKENS,
                        use_cache=True,
                        do_sample=False,
                        output_scores=True,
                        return_dict_in_generate=True,
                    )
                    sequences, scores = outputs.sequences, outputs.scores
                except TypeError:
                    sequences = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, use_cache=True, do_sample=False)
                    scores = None

            if scores is not None:
                gen_ids = sequences[0, input_len:]
                log_probs = []
                for step_idx, score in enumerate(scores):
                    if step_idx >= len(gen_ids):
                        break
                    probs = torch.softmax(score[0], dim=-1)
                    log_probs.append(math.log(probs[gen_ids[step_idx].item()].item() + 1e-12))
                base_conf = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
            else:
                base_conf = 0.95  # fallback default

            decoded = tokenizer.decode(sequences[0], skip_special_tokens=False)
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

        if len(response_list) != len(token_input):
            needed_fallback = True
            if len(response_list) > len(token_input):
                response_list = response_list[:len(token_input)]
            else:
                response_list.extend(["O"] * (len(token_input) - len(response_list)))

        retry_penalty = 0.7 ** max(0, attempt - 1)
        final_conf = base_conf * retry_penalty * (0.5 if needed_fallback else 1.0)
        predictions.append(response_list)
        confidences.append(final_conf)

    return predictions, confidences


def evaluate_predictions(y_true, y_pred):
    m = seqeval_metric.compute(predictions=y_pred, references=y_true)
    return m


def filter_by_confidence(df, predictions, confidences, min_conf, sampling_rate):
    rows = []
    for i, (_, row) in enumerate(df.iterrows()):
        if confidences[i] >= min_conf:
            rows.append({
                "text_id": row["text_id"],
                "tokens": row["tokens"],
                "labels": predictions[i],
                "confidence": confidences[i],
            })
    df_f = pd.DataFrame(rows)
    if len(df_f) == 0:
        return df_f, set()
    df_f = df_f.sort_values("confidence", ascending=False).reset_index(drop=True)
    n_take = max(1, int(len(df_f) * sampling_rate))
    df_taken = df_f.head(n_take).reset_index(drop=True)
    return df_taken, set(df_taken["text_id"].tolist())


def append_pseudo_to_train(train_df_curr, df_pseudo):
    new_rows = []
    for _, row in df_pseudo.iterrows():
        text = ALPACA_PROMPT.format(str(row["tokens"]), str(row["labels"])) + EOS_TOKEN
        new_rows.append({
            "text_id": row["text_id"],
            "text": text,
            "tokens": row["tokens"],
            "labels": row["labels"],
        })
    return pd.concat([train_df_curr, pd.DataFrame(new_rows)], ignore_index=True)


def free_memory(*objs):
    for o in objs:
        del o
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


print("Helper functions ready.")'''


SELFTRAINING_LOOP_CELL = '''# ITERATIVE SELF-TRAINING LOOP

cumulative_train = train_df.copy()
remaining_unlabelled = unlabelled_df.copy()
log_rows = []
prev_val_f1 = 0.0
stop_reason = "completed"

for iter_idx in range(MAX_ITERATIONS + 1):  # iter 0 = baseline
    print(f"\\n{'═'*70}")
    print(f"ITERATION {iter_idx} / {MAX_ITERATIONS}")
    print(f"  Train size: {len(cumulative_train)}")
    print(f"  Remaining unlabelled: {len(remaining_unlabelled)}")
    print(f"{'═'*70}")

    # 1. Train fresh model dengan cumulative train
    print(f"\\n[Iter {iter_idx}.1] Training {EPOCHS_PER_ITER} epochs...")
    model, tokenizer = setup_model_fresh()
    trainer = train_one_iter(model, tokenizer, cumulative_train, val_df, iter_idx, OUT_DIR)

    # 2. Eval pada val
    print(f"\\n[Iter {iter_idx}.2] Eval val...")
    val_preds, _ = inference_with_confidence(model, tokenizer, val_df, desc="Val")
    val_metrics = evaluate_predictions(val_df["labels"].tolist(), val_preds)
    val_f1 = val_metrics["overall_f1"]
    delta = val_f1 - prev_val_f1 if iter_idx > 0 else 0.0
    print(f"  Val F1: {val_f1:.4f} (delta: {delta:+.4f})")

    # 3. Eval pada test (untuk tracking, bukan untuk decision)
    print(f"\\n[Iter {iter_idx}.3] Eval test...")
    test_preds, _ = inference_with_confidence(model, tokenizer, test_df, desc="Test")
    test_metrics = evaluate_predictions(test_df["labels"].tolist(), test_preds)
    test_f1 = test_metrics["overall_f1"]
    print(f"  Test F1: {test_f1:.4f}")

    # Save predictions per iter
    pred_rows = []
    for i, (_, row) in enumerate(test_df.iterrows()):
        for j, token in enumerate(row["tokens"]):
            pred_rows.append({
                "text_id": row["text_id"], "token": token,
                "true_label": row["labels"][j] if j < len(row["labels"]) else "O",
                "pred_label": test_preds[i][j] if j < len(test_preds[i]) else "O",
            })
    pd.DataFrame(pred_rows).to_csv(
        OUT_DIR / f"llm_ner_predictions_iter{iter_idx}.csv",
        index=False, sep=";", encoding="utf-8-sig"
    )

    log_rows.append({
        "iteration": iter_idx,
        "train_size": len(cumulative_train),
        "remaining_unlabelled": len(remaining_unlabelled),
        "val_f1": val_f1,
        "val_precision": val_metrics["overall_precision"],
        "val_recall": val_metrics["overall_recall"],
        "test_f1": test_f1,
        "test_precision": test_metrics["overall_precision"],
        "test_recall": test_metrics["overall_recall"],
        "new_pseudo_added": 0,
    })

    # Stop checks
    if iter_idx > 0 and delta < MIN_F1_DELTA:
        stop_reason = f"val F1 delta {delta:+.4f} < {MIN_F1_DELTA} (konvergen)"
        free_memory(model, tokenizer, trainer)
        break
    if len(remaining_unlabelled) == 0:
        stop_reason = "unlabelled pool habis"
        free_memory(model, tokenizer, trainer)
        break
    if iter_idx == MAX_ITERATIONS:
        stop_reason = f"hit MAX_ITERATIONS={MAX_ITERATIONS}"
        free_memory(model, tokenizer, trainer)
        break

    # 4. Inference pada unlabelled
    print(f"\\n[Iter {iter_idx}.4] Infer unlabelled ({len(remaining_unlabelled)})...")
    unlab_preds, unlab_confs = inference_with_confidence(
        model, tokenizer, remaining_unlabelled, desc="Unlabelled"
    )

    # 5. Filter & sampling
    df_pseudo, taken_ids = filter_by_confidence(
        remaining_unlabelled, unlab_preds, unlab_confs, MIN_CONFIDENCE, SAMPLING_RATE
    )
    n_above = sum(1 for c in unlab_confs if c >= MIN_CONFIDENCE)
    n_new = len(df_pseudo)
    print(f"\\n[Iter {iter_idx}.5] Filter:")
    print(f"  Above conf {MIN_CONFIDENCE}: {n_above}/{len(remaining_unlabelled)}")
    print(f"  Top {int(SAMPLING_RATE*100)}% taken: {n_new}")
    log_rows[-1]["new_pseudo_added"] = n_new

    if n_new < MIN_NEW_SAMPLES:
        stop_reason = f"new samples {n_new} < MIN_NEW_SAMPLES {MIN_NEW_SAMPLES}"
        free_memory(model, tokenizer, trainer)
        break

    # 6. Append + remove from pool
    print(f"\\n[Iter {iter_idx}.6] Appending pseudo-labels...")
    cumulative_train = append_pseudo_to_train(cumulative_train, df_pseudo)
    remaining_unlabelled = remaining_unlabelled[
        ~remaining_unlabelled["text_id"].isin(taken_ids)
    ].reset_index(drop=True)

    # Save snapshot
    cumulative_train[["text_id", "tokens", "labels"]].to_csv(
        OUT_DIR / f"train_iter{iter_idx + 1}.csv",
        index=False, sep=";", encoding="utf-8-sig"
    )

    prev_val_f1 = val_f1
    free_memory(model, tokenizer, trainer)

print(f"\\n{'═'*70}")
print(f"SELF-TRAINING SELESAI — stop reason: {stop_reason}")
print(f"{'═'*70}")'''


SAVE_RESULTS_CELL = '''# Save iteration log + summary

log_df = pd.DataFrame(log_rows)
log_path = OUT_DIR / "iteration_log.csv"
log_df.to_csv(log_path, index=False, encoding="utf-8")

print(f"Iteration log: {log_path}\\n")
print(log_df.to_string(index=False))

# Save summary
summary_path = OUT_DIR / "selftraining_summary.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(f"LLM-NER Self-Training Summary\\n")
    f.write(f"{'='*60}\\n")
    f.write(f"Model: {MODEL_NAME}\\n")
    f.write(f"Stop reason: {stop_reason}\\n")
    f.write(f"Total iterations: {len(log_rows)}\\n")
    f.write(f"Final train size: {log_rows[-1]['train_size']}\\n")
    f.write(f"Baseline (iter 0) test F1: {log_rows[0]['test_f1']:.4f}\\n")
    f.write(f"Final test F1: {log_rows[-1]['test_f1']:.4f}\\n")
    f.write(f"Improvement: {log_rows[-1]['test_f1'] - log_rows[0]['test_f1']:+.4f}\\n\\n")
    f.write("Per-iteration:\\n")
    f.write(log_df.to_string(index=False))
print(f"\\nSummary: {summary_path}")'''


# ── Cells khusus per platform ────────────────────────────────────────────────

def colab_cells():
    return [
        ("md", '''# LLM-NER Sirah + Iterative Self-Training (Pseudo-Labelling)

**Metodologi dasar:** Mengikuti thesis Andrian (5025211079, pembimbing Prof. Dr. Diana Purwitasari) — Instruction Fine-Tuning + QLoRA.

**Tambahan:** Iterative self-training pada data unlabelled (kontribusi adaptasi untuk Sirah).

**Entitas:** PERSON, EVENT, LOCATION, TIME

**Platform:** Google Colab (GPU T4/A100)

---

## Setup

1. Upload ke `MyDrive/TA-Sirah/data/`:
   - `train.csv` (seed labelled)
   - `test.csv` (test set)
   - `unlabelled.csv` (chunk Sirah belum dilabeli)
2. Jalankan semua cell berurutan
3. Output ke `MyDrive/TA-Sirah/output/LLM-NER/pseudo/`

**Estimasi waktu:** ~4 jam (T4) / ~1.5 jam (A100) untuk 5 iterasi.'''),
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
IN_UNLABELLED = DRIVE_BASE / "data" / "unlabelled.csv"
OUT_DIR = DRIVE_BASE / "output" / "LLM-NER" / "pseudo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Train:      {IN_TRAIN} (exists: {IN_TRAIN.exists()})")
print(f"Test:       {IN_TEST} (exists: {IN_TEST.exists()})")
print(f"Unlabelled: {IN_UNLABELLED} (exists: {IN_UNLABELLED.exists()})")
print(f"Output:     {OUT_DIR}")'''),
        ("code", "# Cell 4: Hyperparameters\n" + HYPERPARAM_CELL),
        ("code", "# Cell 5: Prompt Alpaca (Bahasa Indonesia, Prompt 3.8 Andrian)\n" + ALPACA_PROMPT_CELL),
        ("code", "# Cell 6: Load data + format helpers\n" + DATA_LOADING_CELL),
        ("code", "# Cell 7: Helper functions (model setup, train, infer+confidence, filter)\n" + HELPERS_CELL),
        ("code", "# Cell 8: ITERATIVE SELF-TRAINING LOOP\n\n" + SELFTRAINING_LOOP_CELL),
        ("code", "# Cell 9: Save log + summary\n" + SAVE_RESULTS_CELL),
    ]


def kaggle_cells():
    return [
        ("md", '''# LLM-NER Sirah + Iterative Self-Training (Pseudo-Labelling)

**Metodologi dasar:** Mengikuti thesis Andrian (5025211079, pembimbing Prof. Dr. Diana Purwitasari) — Instruction Fine-Tuning + QLoRA.

**Tambahan:** Iterative self-training pada data unlabelled (kontribusi adaptasi untuk Sirah).

**Entitas:** PERSON, EVENT, LOCATION, TIME

**Platform:** Kaggle (P100 / T4 x2 / A100)

---

## Setup

1. Buat Dataset Kaggle bernama `sirah-ner-llm` berisi:
   - `train.csv` (seed labelled)
   - `test.csv` (test set)
   - `unlabelled.csv` (chunk Sirah belum dilabeli)
2. Add dataset ke notebook ini (sidebar → Add Data)
3. Aktifkan GPU di Settings (P100 minimal, A100 ideal)
4. Jalankan semua cell berurutan
5. Output ke `/kaggle/working/LLM-NER/pseudo/`

**Estimasi waktu:** ~4 jam (P100) / ~1.5 jam (A100) untuk 5 iterasi.'''),
        ("code", '''# Cell 1: Install dependencies
!pip install -q unsloth
!pip install -q --no-deps trl peft accelerate bitsandbytes
!pip install -q seqeval evaluate scikit-learn'''),
        ("code", '''# Cell 2: Konfigurasi path (Kaggle)
from pathlib import Path

# Input dataset (read-only di Kaggle)
KAGGLE_INPUT = Path("/kaggle/input/sirah-ner-llm")
IN_TRAIN = KAGGLE_INPUT / "train.csv"
IN_TEST = KAGGLE_INPUT / "test.csv"
IN_UNLABELLED = KAGGLE_INPUT / "unlabelled.csv"

# Output (writable)
OUT_DIR = Path("/kaggle/working/LLM-NER/pseudo")
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Train:      {IN_TRAIN} (exists: {IN_TRAIN.exists()})")
print(f"Test:       {IN_TEST} (exists: {IN_TEST.exists()})")
print(f"Unlabelled: {IN_UNLABELLED} (exists: {IN_UNLABELLED.exists()})")
print(f"Output:     {OUT_DIR}")'''),
        ("code", "# Cell 3: Hyperparameters\n" + HYPERPARAM_CELL),
        ("code", "# Cell 4: Prompt Alpaca (Bahasa Indonesia, Prompt 3.8 Andrian)\n" + ALPACA_PROMPT_CELL),
        ("code", "# Cell 5: Load data + format helpers\n" + DATA_LOADING_CELL),
        ("code", "# Cell 6: Helper functions (model setup, train, infer+confidence, filter)\n" + HELPERS_CELL),
        ("code", "# Cell 7: ITERATIVE SELF-TRAINING LOOP\n\n" + SELFTRAINING_LOOP_CELL),
        ("code", "# Cell 8: Save log + summary\n" + SAVE_RESULTS_CELL),
    ]


def build_notebook(cells_spec):
    """Convert (kind, source) pairs → ipynb dict."""
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

    # ipynb requires source elements to end with \n except last
    for c in cells:
        src = c["source"]
        for i in range(len(src) - 1):
            src[i] = src[i] + "\n"

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.10",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }
    return nb


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
