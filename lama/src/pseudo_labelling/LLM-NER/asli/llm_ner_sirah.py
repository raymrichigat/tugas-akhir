"""
LLM-NER Sirah Nabawiyah — Instruction Fine-Tuning dengan QLoRA

Mengikuti metodologi dari thesis Andrian (5025211079, pembimbing: Prof. Dr. Diana Purwitasari).
Pendekatan: Instruction Fine-Tuning (bukan API prompting) menggunakan SFTTrainer + QLoRA
pada LLM open-source (SahabatAI / SEA-LION / LLAMA 3.1).

Pipeline:
  A. Persiapan data (CoNLL BIO -> prompt Alpaca)
  B. Setup model + QLoRA (4-bit NF4)
  C. Training dengan SFTTrainer
  D. Inferensi dengan retry mechanism
  E. Evaluasi dengan seqeval

Entitas: PERSON, EVENT, LOCATION, TIME (diadaptasi dari EVE, LOC, ORG, PLOC, ARG milik Andrian)

Cara pakai (di Colab/Kaggle — butuh GPU):
  1. Upload train.csv dan test.csv ke environment
  2. Jalankan script ini atau notebook .ipynb

Dependencies:
  pip install torch transformers trl peft bitsandbytes accelerate seqeval unsloth
"""

import os
import ast
import pandas as pd
from pathlib import Path
from collections import defaultdict

# ── Konfigurasi Path ─────────────────────────────────────────────────────────
# Default: lokal Windows. Override di Colab/Kaggle.
BASE_DIR = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_TRAIN = BASE_DIR / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "train.csv"
IN_TEST = BASE_DIR / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
OUT_DIR = BASE_DIR / "data" / "result" / "pseudo-labelling" / "LLM-NER"

# ── Konfigurasi Model ────────────────────────────────────────────────────────
# Model options (HuggingFace model IDs):
#   - "GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct" (SahabatAI — best for Indonesian)
#   - "aisingapore/llama3-8b-cpt-sea-lionv3-instruct" (SEA-LION — multilingual SEA)
#   - "meta-llama/Llama-3.1-8B-Instruct" (LLAMA 3.1 — base model)
MODEL_NAME = "GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct"
MODEL_OUTPUT_DIR = "./result_llm_ner_sirah"

# ── Konfigurasi Training ─────────────────────────────────────────────────────
BATCH_SIZE = 16
NUM_EPOCHS = 30
LEARNING_RATE = 1e-4
MAX_SEQ_LENGTH = 512

# ── Konfigurasi QLoRA ────────────────────────────────────────────────────────
LORA_R = 64
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

# ── Konfigurasi Inferensi ────────────────────────────────────────────────────
MAX_RETRIES = 5
MAX_NEW_TOKENS = 512

# ── Format Prompt (Alpaca-style, Bahasa Indonesia) ───────────────────────────
# Diadaptasi dari Prompt 3.8 Andrian untuk entitas Sirah Nabawiyah

ALPACA_PROMPT = """Di bawah ini adalah sebuah instruksi yang menjelaskan tugas, dipasangkan dengan sebuah masukan yang memberikan konteks lebih lanjut. Tulislah respons yang sesuai untuk menyelesaikan permintaan tersebut.

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

EOS_TOKEN = "<|eot_id|>"


# ═══════════════════════════════════════════════════════════════════════════════
# A. PERSIAPAN DATA
# ═══════════════════════════════════════════════════════════════════════════════

def load_conll_data(filepath):
    """
    Baca data CoNLL (text_id, id, token, pos_tag, label)
    dan groupby text_id -> list of (tokens, labels) per kalimat.
    """
    df = pd.read_csv(filepath, encoding="utf-8")
    has_label = "label" in df.columns
    subset = ["token", "label"] if has_label else ["token"]
    df = df.dropna(subset=subset)

    grouped = df.groupby("text_id", sort=False)
    sentences = []
    for text_id, group in grouped:
        tokens = group["token"].tolist()
        labels = group["label"].tolist() if has_label else ["O"] * len(tokens)

        # Validasi
        if len(tokens) != len(labels):
            continue
        if len(tokens) < 2:
            continue

        sentences.append({
            "text_id": text_id,
            "tokens": tokens,
            "labels": labels,
        })

    return sentences


def check_length(row):
    """Cek apakah panjang token == panjang label dan minimal 2 token."""
    return len(row["tokens"]) == len(row["labels"]) and len(row["tokens"]) > 2


def prepare_instruction_data(train_path, test_path, val_ratio=0.2):
    """
    Siapkan data untuk instruction fine-tuning.
    Returns: train_df, val_df, test_df — masing-masing dengan kolom 'text' berisi prompt Alpaca.
    """
    print("Loading train data...")
    train_sentences = load_conll_data(train_path)
    print(f"  {len(train_sentences)} sentences loaded from train")

    print("Loading test data...")
    test_sentences = load_conll_data(test_path)
    print(f"  {len(test_sentences)} sentences loaded from test")

    # Validasi panjang
    train_sentences = [s for s in train_sentences if check_length(s)]
    test_sentences = [s for s in test_sentences if check_length(s)]

    # Deduplikasi
    seen = set()
    deduped = []
    for s in train_sentences:
        key = (tuple(s["tokens"]), tuple(s["labels"]))
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    train_sentences = deduped
    print(f"  After dedup: {len(train_sentences)} train sentences")

    # Split train -> train + val
    from sklearn.model_selection import train_test_split
    train_split, val_split = train_test_split(
        train_sentences, test_size=val_ratio, random_state=42
    )
    print(f"  Train: {len(train_split)}, Val: {len(val_split)}, Test: {len(test_sentences)}")

    # Format ke prompt Alpaca
    def format_to_alpaca(sentences):
        rows = []
        for s in sentences:
            token_str = str(s["tokens"])
            label_str = str(s["labels"])
            text = ALPACA_PROMPT.format(token_str, label_str) + EOS_TOKEN
            rows.append({
                "text_id": s["text_id"],
                "text": text,
                "tokens": s["tokens"],
                "labels": s["labels"],
            })
        return pd.DataFrame(rows)

    train_df = format_to_alpaca(train_split)
    val_df = format_to_alpaca(val_split)
    test_df = format_to_alpaca(test_sentences)

    return train_df, val_df, test_df


# ═══════════════════════════════════════════════════════════════════════════════
# B. SETUP MODEL + QLoRA
# ═══════════════════════════════════════════════════════════════════════════════

def setup_model(model_name=MODEL_NAME, max_seq_length=MAX_SEQ_LENGTH):
    """
    Inisialisasi model + tokenizer + QLoRA.
    Menggunakan Unsloth untuk efisiensi (jika tersedia), fallback ke transformers + peft.
    """
    try:
        from unsloth import FastLanguageModel
        print(f"  Using Unsloth for {model_name}")

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,  # auto-detect
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

        return model, tokenizer, True  # True = using Unsloth

    except ImportError:
        print(f"  Unsloth not available, using transformers + peft")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

        # QLoRA config (Kode Semu 3.7 Andrian)
        nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=False,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=nf4_config,
            device_map="auto",
        )

        model.gradient_checkpointing_enable()
        model = prepare_model_for_kbit_training(model)

        # LoRA config
        lora_config = LoraConfig(
            r=LORA_R,
            lora_alpha=LORA_ALPHA,
            lora_dropout=LORA_DROPOUT,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"],
        )

        model = get_peft_model(model, lora_config)
        return model, tokenizer, False  # False = not using Unsloth


# ═══════════════════════════════════════════════════════════════════════════════
# C. TRAINING
# ═══════════════════════════════════════════════════════════════════════════════

def train_model(model, tokenizer, train_df, val_df, using_unsloth=False):
    """
    Training menggunakan SFTTrainer (Kode Semu 3.9 Andrian).
    """
    from transformers import TrainingArguments, DataCollatorForSeq2Seq
    from trl import SFTTrainer
    from datasets import Dataset

    # Convert DataFrame ke HuggingFace Dataset
    train_dataset = Dataset.from_pandas(train_df[["text"]])
    val_dataset = Dataset.from_pandas(val_df[["text"]])

    # TrainingArguments (Kode Semu 3.10 Andrian)
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

    # SFTTrainer config (Kode Semu 3.9 Andrian)
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

    print("  Starting training...")
    trainer.train()
    print("  Training complete!")

    return trainer


# ═══════════════════════════════════════════════════════════════════════════════
# D. INFERENSI DENGAN RETRY
# ═══════════════════════════════════════════════════════════════════════════════

def run_inference(model, tokenizer, test_df, using_unsloth=False):
    """
    Inferensi pada test set dengan retry mechanism (Kode Semu 3.12 Andrian).
    """
    import torch

    if using_unsloth:
        from unsloth import FastLanguageModel
        FastLanguageModel.for_inference(model)

    predictions = []

    for idx, row in test_df.iterrows():
        token_input = row["tokens"]
        token_str = str(token_input)

        # Build prompt tanpa respons (untuk inferensi)
        prompt = ALPACA_PROMPT.format(token_str, "")

        response_list = []
        attempt = 0

        while len(response_list) != len(token_input) and attempt < MAX_RETRIES:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    use_cache=True,
                    do_sample=False,
                )

            decoded = tokenizer.decode(outputs[0], skip_special_tokens=False)

            # Extract response setelah "### Respons:"
            if "### Respons:" in decoded:
                response_text = decoded.split("### Respons:")[-1].strip()
                # Remove EOS token
                response_text = response_text.replace(EOS_TOKEN, "").strip()
            else:
                response_text = ""

            # Convert string ke list
            try:
                response_list = ast.literal_eval(response_text)
                if not isinstance(response_list, list):
                    response_list = []
            except (ValueError, SyntaxError):
                response_list = []

            attempt += 1

        # Fallback: jika tetap gagal, padding/truncate
        if len(response_list) != len(token_input):
            if len(response_list) > len(token_input):
                response_list = response_list[:len(token_input)]
            else:
                response_list.extend(["O"] * (len(token_input) - len(response_list)))

        predictions.append(response_list)

        if (idx + 1) % 50 == 0:
            print(f"    Inference progress: {idx + 1}/{len(test_df)}")

    return predictions


# ═══════════════════════════════════════════════════════════════════════════════
# E. EVALUASI
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_model(y_true, y_pred):
    """
    Evaluasi dengan seqeval (Kode Semu 3.11 Andrian).
    Returns: dict of metrics.
    """
    import evaluate

    metric = evaluate.load("seqeval")
    all_metrics = metric.compute(predictions=y_pred, references=y_true)

    print(f"\n  Precision: {all_metrics['overall_precision']:.4f}")
    print(f"  Recall   : {all_metrics['overall_recall']:.4f}")
    print(f"  F1-score : {all_metrics['overall_f1']:.4f}")
    print(f"  Accuracy : {all_metrics['overall_accuracy']:.4f}")

    # Per-entity metrics
    for entity_type in ["PERSON", "EVENT", "LOCATION", "TIME"]:
        if entity_type in all_metrics:
            e = all_metrics[entity_type]
            print(f"  {entity_type:10s}: P={e['precision']:.4f} R={e['recall']:.4f} "
                  f"F1={e['f1']:.4f} (n={e['number']})")

    return all_metrics


def save_predictions(test_df, predictions, out_dir):
    """Simpan prediksi ke CSV."""
    rows = []
    for i, (_, row) in enumerate(test_df.iterrows()):
        tokens = row["tokens"]
        true_labels = row["labels"]
        pred_labels = predictions[i] if i < len(predictions) else ["O"] * len(tokens)

        for j, token in enumerate(tokens):
            rows.append({
                "text_id": row["text_id"],
                "token": token,
                "true_label": true_labels[j] if j < len(true_labels) else "O",
                "pred_label": pred_labels[j] if j < len(pred_labels) else "O",
            })

    pred_df = pd.DataFrame(rows)
    pred_path = Path(out_dir) / "llm_ner_predictions.csv"
    pred_df.to_csv(pred_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"  Predictions saved to: {pred_path}")


def save_metrics(all_metrics, out_dir):
    """Simpan metrik evaluasi ke file."""
    metrics_path = Path(out_dir) / "llm_ner_metrics.txt"
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write(f"Model: {MODEL_NAME}\n")
        f.write(f"Epochs: {NUM_EPOCHS}\n")
        f.write(f"Batch size: {BATCH_SIZE}\n")
        f.write(f"Learning rate: {LEARNING_RATE}\n")
        f.write(f"LoRA r: {LORA_R}, alpha: {LORA_ALPHA}\n")
        f.write(f"\n--- Overall ---\n")
        f.write(f"Precision: {all_metrics['overall_precision']:.4f}\n")
        f.write(f"Recall   : {all_metrics['overall_recall']:.4f}\n")
        f.write(f"F1-score : {all_metrics['overall_f1']:.4f}\n")
        f.write(f"Accuracy : {all_metrics['overall_accuracy']:.4f}\n")

        for entity_type in ["PERSON", "EVENT", "LOCATION", "TIME"]:
            if entity_type in all_metrics:
                e = all_metrics[entity_type]
                f.write(f"\n--- {entity_type} ---\n")
                f.write(f"Precision: {e['precision']:.4f}\n")
                f.write(f"Recall   : {e['recall']:.4f}\n")
                f.write(f"F1-score : {e['f1']:.4f}\n")
                f.write(f"Support  : {e['number']}\n")

    print(f"  Metrics saved to: {metrics_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("LLM-NER SIRAH NABAWIYAH")
    print("Instruction Fine-Tuning dengan QLoRA")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)

    # A. Persiapan data
    print("\n[A] Persiapan data...")
    train_df, val_df, test_df = prepare_instruction_data(IN_TRAIN, IN_TEST)

    # B. Setup model
    print("\n[B] Setup model + QLoRA...")
    model, tokenizer, using_unsloth = setup_model()
    print(f"  Model loaded: {MODEL_NAME}")
    print(f"  Using Unsloth: {using_unsloth}")

    # C. Training
    print("\n[C] Training...")
    trainer = train_model(model, tokenizer, train_df, val_df, using_unsloth)

    # D. Inferensi
    print("\n[D] Inferensi pada test set...")
    predictions = run_inference(model, tokenizer, test_df, using_unsloth)

    # E. Evaluasi
    print("\n[E] Evaluasi...")
    y_true = test_df["labels"].tolist()
    y_pred = predictions
    all_metrics = evaluate_model(y_true, y_pred)

    # Simpan output
    print("\n[F] Saving output...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    save_predictions(test_df, predictions, OUT_DIR)
    save_metrics(all_metrics, OUT_DIR)

    print(f"\n{'='*60}")
    print("SELESAI!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
