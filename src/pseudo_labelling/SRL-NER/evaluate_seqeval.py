"""
Re-evaluate trained NER model with seqeval (entity-level F1).

Tujuan: dapat angka F1 entity-level (span-based) yang head-to-head dengan S1 baseline
(yang sudah punya F1 entity seqeval = 0.9587). Notebook S2 di Colab tidak ke-install
seqeval, jadi metric S2 yang ada baru token-level sklearn. Script ini menambal itu.

Cara pakai (Windows PowerShell, dari root project):

    # 1. Aktifkan venv
    venv\Scripts\activate

    # 2. Install seqeval kalau belum
    pip install seqeval

    # 3a. Eval satu model spesifik
    python src\pseudo_labelling\SRL-NER\evaluate_seqeval.py `
        --model "src\pseudo_labelling\SRL-NER\done_running\S2_Contrastive_Learning\outputs\models\S2b-jscl\bert-only-sirah-ner-S2b-jscl-0.9-iteration-6" `
        --tag "S2b-jscl-iter6"

    # 3b. Eval semua skenario sekaligus (S1, S2a, S2b — base + iter terakhir yang ada weights)
    python src\pseudo_labelling\SRL-NER\evaluate_seqeval.py --all

Output: console + file markdown di `data/result/pseudo-labelling/SRL-NER/seqeval_results.md`
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

try:
    from seqeval.metrics import classification_report as seq_classification_report
    from seqeval.metrics import f1_score as seq_f1_score
    from seqeval.metrics import precision_score as seq_precision_score
    from seqeval.metrics import recall_score as seq_recall_score
except ImportError:
    print("[ERR] seqeval tidak terinstall. Jalankan: pip install seqeval", file=sys.stderr)
    sys.exit(1)

try:
    from transformers import pipeline
except ImportError:
    print("[ERR] transformers tidak terinstall. Jalankan: pip install transformers torch", file=sys.stderr)
    sys.exit(1)

from tqdm import tqdm

# ---------- konstanta path (relatif ke root project) ----------

ROOT = Path(__file__).resolve().parents[3]
TEST_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
OUT_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
OUT_MD = OUT_DIR / "seqeval_results.md"

DONE = ROOT / "src" / "pseudo_labelling" / "SRL-NER" / "done_running"

# Semua kandidat model. Iterasi terakhir yang ada weights-nya bervariasi per skenario
# karena beberapa file model.safetensors tidak ke-download dari Colab.
CANDIDATES = {
    "S1-baseline-base": DONE / "S1_baseline" / "output" / "models" / "bert-only-sirah-ner-base",
    "S1-baseline-iter6": DONE / "S1_baseline" / "output" / "models" / "bert-only-sirah-ner-0.9-iteration-6",
    "S2a-scl-base": DONE / "S2_Contrastive_Learning" / "outputs" / "models" / "S2a-scl" / "bert-only-sirah-ner-S2a-scl-base",
    "S2a-scl-iter5": DONE / "S2_Contrastive_Learning" / "outputs" / "models" / "S2a-scl" / "bert-only-sirah-ner-S2a-scl-0.9-iteration-5",
    "S2a-scl-iter6": DONE / "S2_Contrastive_Learning" / "outputs" / "models" / "S2a-scl" / "bert-only-sirah-ner-S2a-scl-0.9-iteration-6",
    "S2b-jscl-iter5": DONE / "S2_Contrastive_Learning" / "outputs" / "models" / "S2b-jscl" / "bert-only-sirah-ner-S2b-jscl-0.9-iteration-5",
    "S2b-jscl-iter6": DONE / "S2_Contrastive_Learning" / "outputs" / "models" / "S2b-jscl" / "bert-only-sirah-ner-S2b-jscl-0.9-iteration-6",
    # S3.1 lambda sweep — pick base + final iter yang punya weights per varian.
    # Konvergensi: lambda01 sampai iter-6, lambda02 sampai iter-5, lambda03 sampai iter-4.
    "S3.1-scl-lambda01-base": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda01" / "bert-only-sirah-ner-S3-1-scl-lambda01-base",
    "S3.1-scl-lambda01-iter6": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda01" / "bert-only-sirah-ner-S3-1-scl-lambda01-0.9-iteration-6",
    "S3.1-scl-lambda02-base": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda02" / "bert-only-sirah-ner-S3-1-scl-lambda02-base",
    "S3.1-scl-lambda02-iter5": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda02" / "bert-only-sirah-ner-S3-1-scl-lambda02-0.9-iteration-5",
    "S3.1-scl-lambda03-base": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda03" / "bert-only-sirah-ner-S3-1-scl-lambda03-base",
    "S3.1-scl-lambda03-iter4": DONE / "S3_Augmented" / "output" / "models" / "scl_lambda03" / "bert-only-sirah-ner-S3-1-scl-lambda03-0.9-iteration-4",
    # S3.2 augmentation di atas winner λ_C=0.3, train_augmented_v2.csv (260 augmented sentences).
    # Konvergen di iter-4 (n_above 223 -> 13 -> 1).
    "S3.2-scl-aug-base": DONE / "S3_Augmented" / "output" / "models" / "scl_aug" / "bert-only-sirah-ner-S3-2-scl-aug-v2-base",
    "S3.2-scl-aug-iter4": DONE / "S3_Augmented" / "output" / "models" / "scl_aug" / "bert-only-sirah-ner-S3-2-scl-aug-v2-0.9-iteration-4",
}


def has_weights(model_dir: Path) -> bool:
    """True kalau folder berisi model.safetensors atau pytorch_model.bin."""
    if not model_dir.is_dir():
        return False
    return any((model_dir / fn).exists() for fn in ("model.safetensors", "pytorch_model.bin"))


def extract_entities_from_result(tokens: list[str], result: list[dict], bio_scheme: bool = True) -> list[str]:
    """Map HF pipeline output ke BIO labels, sejalan dengan extract_entities_from_result di notebook."""
    predicted_entities: list[str] = []
    current_index = 0
    prev_span_id = None

    for token in tokens:
        hit = None
        for idx, entry in enumerate(result):
            if entry["start"] <= current_index < entry["end"]:
                hit = idx
                break

        if hit is None:
            label = "O"
            prev_span_id = None
        else:
            group = result[hit]["entity_group"]
            if bio_scheme:
                if group.startswith(("B_", "I_")):
                    label = group
                else:
                    label = f"B_{group}" if hit != prev_span_id else f"I_{group}"
            else:
                label = group
            prev_span_id = hit

        predicted_entities.append(label)
        current_index += len(token) + 1

    return predicted_entities


def bio_to_dash(label: str) -> str:
    """seqeval mengharapkan B-X / I-X (dash), bukan B_X / I_X (underscore)."""
    if label.startswith(("B_", "I_")):
        return label.replace("_", "-", 1)
    return label


def evaluate_model(model_dir: Path, df_test: pd.DataFrame, tag: str) -> dict:
    """Predict test set + hitung seqeval entity-level. Return dict metric."""
    print(f"\n[{tag}] Loading model dari {model_dir} ...")
    ner = pipeline(
        "token-classification",
        model=str(model_dir),
        aggregation_strategy="simple",
    )

    true_seqs: list[list[str]] = []
    pred_seqs: list[list[str]] = []

    text_ids = df_test["text_id"].unique().tolist()
    for text_id in tqdm(text_ids, desc=f"[{tag}] predicting"):
        sub = df_test[df_test["text_id"] == text_id]
        tokens = sub["token"].astype(str).tolist()
        true_labels = sub["label"].astype(str).tolist()

        text = " ".join(tokens)
        result = ner(text)

        pred_labels = extract_entities_from_result(tokens, result, bio_scheme=True)

        true_seqs.append([bio_to_dash(l) for l in true_labels])
        pred_seqs.append([bio_to_dash(l) for l in pred_labels])

    f1 = seq_f1_score(true_seqs, pred_seqs)
    prec = seq_precision_score(true_seqs, pred_seqs)
    rec = seq_recall_score(true_seqs, pred_seqs)
    report = seq_classification_report(true_seqs, pred_seqs, digits=4)

    print(f"\n[{tag}] seqeval entity-level:")
    print(f"  F1        : {f1:.4f}")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(report)

    return {
        "tag": tag,
        "model_dir": str(model_dir),
        "f1": float(f1),
        "precision": float(prec),
        "recall": float(rec),
        "report": report,
    }


def write_markdown(results: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Seqeval Entity-Level Evaluation\n")
    lines.append("> Dihasilkan oleh `src/pseudo_labelling/SRL-NER/evaluate_seqeval.py`\n")
    lines.append("> Metric: seqeval span-based (entity-level), bukan token-level sklearn.\n")
    lines.append("\n## 1. Ringkasan F1\n")
    lines.append("| Tag | F1 entity | Precision | Recall |")
    lines.append("|---|---:|---:|---:|")
    for r in results:
        lines.append(f"| {r['tag']} | {r['f1']:.4f} | {r['precision']:.4f} | {r['recall']:.4f} |")
    lines.append("\n## 2. Per-entity classification_report\n")
    for r in results:
        lines.append(f"### {r['tag']}\n")
        lines.append("```\n" + r["report"].rstrip() + "\n```\n")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] Tulis hasil ke {OUT_MD}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=str, default=None, help="Path ke folder model (config.json + model.safetensors)")
    ap.add_argument("--tag", type=str, default="custom", help="Label untuk output")
    ap.add_argument("--all", action="store_true", help="Evaluate semua kandidat yang punya weights")
    args = ap.parse_args()

    if not TEST_CSV.exists():
        print(f"[ERR] test.csv tidak ditemukan di {TEST_CSV}", file=sys.stderr)
        sys.exit(1)
    df_test = pd.read_csv(TEST_CSV)
    df_test["token"] = df_test["token"].astype(str)
    df_test["label"] = df_test["label"].astype(str)
    print(f"[OK] Loaded test.csv — {len(df_test)} rows, {df_test['text_id'].nunique()} sentences")

    targets: list[tuple[str, Path]] = []

    if args.all:
        for tag, p in CANDIDATES.items():
            if has_weights(p):
                targets.append((tag, p))
            else:
                print(f"[SKIP] {tag} — tidak ada model.safetensors di {p}")
    elif args.model:
        p = Path(args.model)
        if not has_weights(p):
            print(f"[ERR] {p} tidak punya model.safetensors / pytorch_model.bin", file=sys.stderr)
            sys.exit(2)
        targets.append((args.tag, p))
    else:
        ap.print_help()
        sys.exit(0)

    results = [evaluate_model(model_dir, df_test, tag) for tag, model_dir in targets]
    write_markdown(results)


if __name__ == "__main__":
    main()
