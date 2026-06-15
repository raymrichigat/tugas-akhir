"""
LLM-NER + Iterative Self-Training (Pseudo-Labelling) untuk Sirah Nabawiyah

Extension dari llm_ner_sirah.py dengan iterative self-training pada data unlabelled.
Pendekatan ini ADDITION DI ATAS metode Andrian (yang hanya supervised + augmentasi).

Pipeline:
  Iter 0: Train LLM-NER di seed (train.csv) → eval baseline
  Iter n:
    1. Inference pada remaining unlabelled.csv → ambil prediksi + confidence
    2. Filter: confidence >= MIN_CONFIDENCE
    3. Sampling: top-K% kalimat dengan confidence tertinggi (SAMPLING_RATE)
    4. Append ke training set
    5. Re-train LLM-NER (LoRA adapter di-init ulang)
    6. Eval pada val set (held-out, fixed across iter)

Stop conditions:
  - len(remaining_unlabelled) == 0
  - new_samples_added < MIN_NEW_SAMPLES
  - val_f1 improvement < MIN_F1_DELTA
  - iter == MAX_ITERATIONS

Confidence scoring:
  Average token-level probability dari model.generate (output_scores=True),
  dengan penalti × 0.7^(retries-1) kalau model butuh retry.

Cara pakai (di Colab/Kaggle — butuh GPU besar, lebih lama dari single-train):
  python llm_ner_sirah_selftraining.py

Output:
  - data/result/pseudo-labelling/LLM-NER/iteration_log.csv  (metrik per iter)
  - data/result/pseudo-labelling/LLM-NER/train_iter{N}.csv  (snapshot training set)
  - data/result/pseudo-labelling/LLM-NER/llm_ner_predictions_iter{N}.csv

Dependencies: sama seperti llm_ner_sirah.py + tqdm
"""

import os
import ast
import math
import gc
import torch
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Reuse dari llm_ner_sirah
import llm_ner_sirah
from llm_ner_sirah import (
    BASE_DIR, IN_TRAIN, IN_TEST,
    MODEL_NAME, MAX_SEQ_LENGTH,
    BATCH_SIZE, LEARNING_RATE,
    MAX_RETRIES, MAX_NEW_TOKENS,
    ALPACA_PROMPT, EOS_TOKEN,
    load_conll_data, prepare_instruction_data,
    setup_model, train_model, evaluate_model,
)

# ── Path Tambahan ────────────────────────────────────────────────────────────
IN_UNLABELLED = BASE_DIR / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "unlabelled.csv"
OUT_DIR_ST = BASE_DIR / "data" / "result" / "pseudo-labelling" / "LLM-NER"

# ── Konfigurasi Self-Training ────────────────────────────────────────────────
MAX_ITERATIONS = 5         # batas iterasi (selain stop condition lain)
MIN_CONFIDENCE = 0.85      # threshold avg token probability (range 0-1)
SAMPLING_RATE = 0.5        # ambil top-K% kalimat per iterasi (anti-noise)
MIN_NEW_SAMPLES = 50       # stop kalau filter < ini (early stop)
MIN_F1_DELTA = 0.01        # stop kalau peningkatan val F1 < ini (konvergen)
EPOCHS_PER_ITER = 10       # epoch per iterasi (lebih kecil dari 30 di llm_ner_sirah)


# ═══════════════════════════════════════════════════════════════════════════════
# A. INFERENSI DENGAN CONFIDENCE
# ═══════════════════════════════════════════════════════════════════════════════

def run_inference_with_confidence(model, tokenizer, df, using_unsloth=False, desc="Inferring"):
    """
    Inferensi pada DataFrame, returns (predictions, confidences).

    Confidence per kalimat:
      base_conf = exp(mean(log_prob_per_generated_token))
      final_conf = base_conf * 0.7^(retries - 1)

    Range confidence: 0.0 (rendah) – 1.0 (tinggi).
    """
    if using_unsloth:
        try:
            from unsloth import FastLanguageModel
            FastLanguageModel.for_inference(model)
        except Exception:
            pass

    predictions = []
    confidences = []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc=desc):
        token_input = row["tokens"]
        token_str = str(token_input)
        prompt = ALPACA_PROMPT.format(token_str, "")

        response_list = []
        base_confidence = 0.0
        attempt = 0

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
                    sequences = outputs.sequences
                    scores = outputs.scores
                except TypeError:
                    # Fallback kalau output_scores tidak didukung (e.g. unsloth path)
                    sequences = model.generate(
                        **inputs,
                        max_new_tokens=MAX_NEW_TOKENS,
                        use_cache=True,
                        do_sample=False,
                    )
                    scores = None

            # Hitung confidence dari logprob
            if scores is not None:
                generated_ids = sequences[0, input_len:]
                log_probs = []
                for step_idx, score in enumerate(scores):
                    if step_idx >= len(generated_ids):
                        break
                    probs = torch.softmax(score[0], dim=-1)
                    chosen_id = generated_ids[step_idx].item()
                    log_probs.append(math.log(probs[chosen_id].item() + 1e-12))
                base_confidence = math.exp(sum(log_probs) / len(log_probs)) if log_probs else 0.0
            else:
                # Fallback: confidence default tinggi, dikoreksi oleh retry penalty
                base_confidence = 0.95

            # Decode + parse
            decoded = tokenizer.decode(sequences[0], skip_special_tokens=False)
            if "### Respons:" in decoded:
                response_text = decoded.split("### Respons:")[-1].strip()
                response_text = response_text.replace(EOS_TOKEN, "").strip()
            else:
                response_text = ""

            try:
                response_list = ast.literal_eval(response_text)
                if not isinstance(response_list, list):
                    response_list = []
            except (ValueError, SyntaxError):
                response_list = []

            attempt += 1

        # Padding/truncate fallback (sama seperti llm_ner_sirah.py)
        needed_fallback = False
        if len(response_list) != len(token_input):
            needed_fallback = True
            if len(response_list) > len(token_input):
                response_list = response_list[:len(token_input)]
            else:
                response_list.extend(["O"] * (len(token_input) - len(response_list)))

        # Confidence final = base * retry_penalty
        retry_penalty = 0.7 ** max(0, attempt - 1)
        final_confidence = base_confidence * retry_penalty
        if needed_fallback:
            final_confidence *= 0.5  # extra penalty kalau butuh padding

        predictions.append(response_list)
        confidences.append(final_confidence)

    return predictions, confidences


# ═══════════════════════════════════════════════════════════════════════════════
# B. FILTER PSEUDO-LABEL BERDASARKAN CONFIDENCE
# ═══════════════════════════════════════════════════════════════════════════════

def filter_by_confidence(df, predictions, confidences,
                          min_conf=MIN_CONFIDENCE, sampling_rate=SAMPLING_RATE):
    """
    Filter prediksi yang confidence-nya >= min_conf, lalu sampling top-K%.

    Returns:
        df_taken: DataFrame dengan kolom (text_id, tokens, labels, confidence)
        taken_ids: set text_id yang diambil (untuk dihapus dari unlabelled pool)
    """
    rows = []
    for i, (_, row) in enumerate(df.iterrows()):
        if confidences[i] >= min_conf:
            rows.append({
                "text_id": row["text_id"],
                "tokens": row["tokens"],
                "labels": predictions[i],
                "confidence": confidences[i],
            })

    df_filtered = pd.DataFrame(rows)
    if len(df_filtered) == 0:
        return df_filtered, set()

    # Sort by confidence desc, ambil top K%
    df_filtered = df_filtered.sort_values("confidence", ascending=False).reset_index(drop=True)
    n_take = max(1, int(len(df_filtered) * sampling_rate))
    df_taken = df_filtered.head(n_take).reset_index(drop=True)

    taken_ids = set(df_taken["text_id"].tolist())
    return df_taken, taken_ids


# ═══════════════════════════════════════════════════════════════════════════════
# C. UTILITY: Append pseudo-label ke training set
# ═══════════════════════════════════════════════════════════════════════════════

def append_pseudo_to_train(train_df, df_pseudo):
    """
    Append pseudo-labelled data ke training set dengan format Alpaca yang sama.
    """
    new_rows = []
    for _, row in df_pseudo.iterrows():
        token_str = str(row["tokens"])
        label_str = str(row["labels"])
        text = ALPACA_PROMPT.format(token_str, label_str) + EOS_TOKEN
        new_rows.append({
            "text_id": row["text_id"],
            "text": text,
            "tokens": row["tokens"],
            "labels": row["labels"],
        })
    return pd.concat([train_df, pd.DataFrame(new_rows)], ignore_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# D. UTILITY: Convert unlabelled CoNLL → DataFrame format
# ═══════════════════════════════════════════════════════════════════════════════

def load_unlabelled_as_df(filepath):
    """
    Baca unlabelled.csv (format CoNLL) → DataFrame dengan kolom yang sama
    dengan train_df / val_df / test_df di llm_ner_sirah.py.
    """
    sentences = load_conll_data(filepath)
    rows = []
    for s in sentences:
        token_str = str(s["tokens"])
        text = ALPACA_PROMPT.format(token_str, "") + EOS_TOKEN
        rows.append({
            "text_id": s["text_id"],
            "text": text,
            "tokens": s["tokens"],
            "labels": s["labels"],  # mostly "O" karena unlabelled
        })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# E. ITERATIVE SELF-TRAINING LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def self_training_loop():
    """
    Main loop: train → eval → infer unlabelled → filter → append → repeat.
    """
    print("=" * 70)
    print("LLM-NER + ITERATIVE SELF-TRAINING (PSEUDO-LABELLING)")
    print(f"Model: {MODEL_NAME}")
    print(f"Max iter: {MAX_ITERATIONS} | Min conf: {MIN_CONFIDENCE} | "
          f"Sampling: {SAMPLING_RATE} | Epochs/iter: {EPOCHS_PER_ITER}")
    print("=" * 70)

    OUT_DIR_ST.mkdir(parents=True, exist_ok=True)

    # ── Setup data ──────────────────────────────────────────────────────────
    print("\n[Setup] Loading seed train + val + test...")
    train_df, val_df, test_df = prepare_instruction_data(IN_TRAIN, IN_TEST)
    print(f"  Seed sizes: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

    print("\n[Setup] Loading unlabelled pool...")
    unlabelled_df = load_unlabelled_as_df(IN_UNLABELLED)
    print(f"  Unlabelled: {len(unlabelled_df)} sentences")

    # Override NUM_EPOCHS module-wide untuk iterasi (lebih kecil)
    original_epochs = llm_ner_sirah.NUM_EPOCHS
    llm_ner_sirah.NUM_EPOCHS = EPOCHS_PER_ITER

    cumulative_train = train_df.copy()
    log_rows = []
    prev_f1 = 0.0

    try:
        # ── Loop ─────────────────────────────────────────────────────────────
        for iter_idx in range(MAX_ITERATIONS + 1):  # iter 0 = baseline
            print(f"\n{'═'*70}")
            print(f"ITERATION {iter_idx} / {MAX_ITERATIONS}")
            print(f"  Train size: {len(cumulative_train)}")
            print(f"  Remaining unlabelled: {len(unlabelled_df)}")
            print(f"{'═'*70}")

            # ── Step 1: Train ────────────────────────────────────────────────
            print(f"\n[Iter {iter_idx}.1] Training {EPOCHS_PER_ITER} epochs...")
            model, tokenizer, using_unsloth = setup_model()
            train_model(model, tokenizer, cumulative_train, val_df, using_unsloth)

            # ── Step 2: Eval pada val ────────────────────────────────────────
            print(f"\n[Iter {iter_idx}.2] Evaluating on val set...")
            val_predictions, _ = run_inference_with_confidence(
                model, tokenizer, val_df, using_unsloth, desc="Val"
            )
            val_metrics = evaluate_model(val_df["labels"].tolist(), val_predictions)
            val_f1 = val_metrics["overall_f1"]
            delta = val_f1 - prev_f1 if iter_idx > 0 else 0.0
            print(f"  Val F1: {val_f1:.4f} (delta vs prev iter: {delta:+.4f})")

            # ── Step 3: Eval pada test (untuk tracking) ──────────────────────
            print(f"\n[Iter {iter_idx}.3] Evaluating on test set...")
            test_predictions, _ = run_inference_with_confidence(
                model, tokenizer, test_df, using_unsloth, desc="Test"
            )
            test_metrics = evaluate_model(test_df["labels"].tolist(), test_predictions)
            test_f1 = test_metrics["overall_f1"]
            print(f"  Test F1: {test_f1:.4f}")

            # Save predictions per iter
            _save_predictions_iter(test_df, test_predictions, OUT_DIR_ST, iter_idx)

            log_rows.append({
                "iteration": iter_idx,
                "train_size": len(cumulative_train),
                "remaining_unlabelled": len(unlabelled_df),
                "val_f1": val_f1,
                "val_precision": val_metrics["overall_precision"],
                "val_recall": val_metrics["overall_recall"],
                "test_f1": test_f1,
                "test_precision": test_metrics["overall_precision"],
                "test_recall": test_metrics["overall_recall"],
                "new_pseudo_added": 0,
            })

            # ── Stop checks ──────────────────────────────────────────────────
            if iter_idx > 0 and delta < MIN_F1_DELTA:
                print(f"\n[STOP] Val F1 improvement {delta:+.4f} < {MIN_F1_DELTA}")
                break
            if len(unlabelled_df) == 0:
                print("\n[STOP] No more unlabelled data")
                break
            if iter_idx == MAX_ITERATIONS:
                print(f"\n[STOP] Reached MAX_ITERATIONS={MAX_ITERATIONS}")
                break

            # ── Step 4: Inferensi pada unlabelled ────────────────────────────
            print(f"\n[Iter {iter_idx}.4] Inferring on {len(unlabelled_df)} unlabelled...")
            unlab_predictions, unlab_confidences = run_inference_with_confidence(
                model, tokenizer, unlabelled_df, using_unsloth, desc="Unlabelled"
            )

            # ── Step 5: Filter & sampling ────────────────────────────────────
            df_pseudo, taken_ids = filter_by_confidence(
                unlabelled_df, unlab_predictions, unlab_confidences,
                min_conf=MIN_CONFIDENCE, sampling_rate=SAMPLING_RATE
            )
            n_new = len(df_pseudo)
            n_above = sum(1 for c in unlab_confidences if c >= MIN_CONFIDENCE)
            print(f"\n[Iter {iter_idx}.5] Filter result:")
            print(f"  Above threshold {MIN_CONFIDENCE}: {n_above}/{len(unlabelled_df)}")
            print(f"  Taken (top {int(SAMPLING_RATE*100)}%): {n_new}")
            log_rows[-1]["new_pseudo_added"] = n_new

            if n_new < MIN_NEW_SAMPLES:
                print(f"\n[STOP] New samples ({n_new}) < MIN_NEW_SAMPLES ({MIN_NEW_SAMPLES})")
                break

            # ── Step 6: Append + remove from pool ────────────────────────────
            print(f"\n[Iter {iter_idx}.6] Appending {n_new} pseudo-labels to train set...")
            cumulative_train = append_pseudo_to_train(cumulative_train, df_pseudo)
            unlabelled_df = unlabelled_df[~unlabelled_df["text_id"].isin(taken_ids)].reset_index(drop=True)

            # Save snapshot
            snap_path = OUT_DIR_ST / f"train_iter{iter_idx + 1}.csv"
            cumulative_train[["text_id", "tokens", "labels"]].to_csv(
                snap_path, index=False, sep=";", encoding="utf-8-sig"
            )
            print(f"  Train snapshot saved: {snap_path}")

            prev_f1 = val_f1

            # Free memory
            del model, tokenizer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    finally:
        # Restore module epochs
        llm_ner_sirah.NUM_EPOCHS = original_epochs

    # ── Save iteration log ──────────────────────────────────────────────────
    log_df = pd.DataFrame(log_rows)
    log_path = OUT_DIR_ST / "iteration_log.csv"
    log_df.to_csv(log_path, index=False, encoding="utf-8")

    print(f"\n{'═'*70}")
    print("SELF-TRAINING SELESAI")
    print(f"{'═'*70}")
    print(f"\nIteration log saved to: {log_path}")
    print("\nSummary:")
    print(log_df.to_string(index=False))


def _save_predictions_iter(test_df, predictions, out_dir, iter_idx):
    """Save predictions per iteration (untuk tracking)."""
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
    pred_path = Path(out_dir) / f"llm_ner_predictions_iter{iter_idx}.csv"
    pd.DataFrame(rows).to_csv(pred_path, index=False, sep=";", encoding="utf-8-sig")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    self_training_loop()
