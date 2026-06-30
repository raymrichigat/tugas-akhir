"""
eval_postag_direct.py — Inference LANGSUNG model POS-tag + seqeval entity-level F1.

Tujuan: menghilangkan kebutuhan "rekonstruksi F1 dari berkas *-incorrect.xlsx".
Model POS-tag disimpan hanya sebagai `pytorch_model.bin` (state_dict mentah, tanpa
config/tokenizer) dan arsitekturnya custom (IndoBERT 768 + POS-emb 32 -> concat 800 ->
Linear 9). Skrip ini MEMBANGUN ULANG arsitektur itu (sama persis dengan notebook
srl_ner_sirah_pos_tag_colab.ipynb), memuat bobotnya, lalu inference di test.csv dan
menghitung F1 entity-level dengan seqeval — head-to-head adil dengan skenario lain.

Jalankan (butuh akses ke `indolem/indobert-base-uncased`, ter-cache atau online):
    python src/pseudo_labelling/SRL-NER/eval_postag_direct.py
    python src/pseudo_labelling/SRL-NER/eval_postag_direct.py --iter 4   # default

Output:
    - console: classification_report seqeval (micro + per-kelas)
    - data/result/pseudo-labelling/SRL-NER/seqeval_postag_direct.md
    - data/result/analysis/error_viz/postag_direct_predictions.csv (token, gold, pred)
"""
import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
from transformers import AutoConfig, AutoModel, AutoTokenizer
from transformers.modeling_outputs import TokenClassifierOutput

try:
    from seqeval.metrics import (classification_report, f1_score,
                                 precision_score, recall_score)
except ImportError:
    sys.exit("[ERR] seqeval belum terpasang. Jalankan: pip install seqeval")

# ── Resolusi ROOT repo ────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve()
for _ in range(8):
    if (ROOT / "CLAUDE.md").exists():
        break
    ROOT = ROOT.parent

MODEL_NAME = "indolem/indobert-base-uncased"          # sama dgn notebook (uncased)
DATA_DIR = ROOT / "data/result/pseudo-labelling/SRL-NER/data_with_pos_20260610"
MODELS_DIR = ROOT / "data/result/pseudo-labelling/SRL-NER/done_running/pos-tag/output_pos_tag/models"
OUT_MD = ROOT / "data/result/pseudo-labelling/SRL-NER/seqeval_postag_direct.md"
OUT_PRED = ROOT / "data/result/analysis/error_viz/postag_direct_predictions.csv"

# ── POS vocab (persis notebook cell 9) ────────────────────────────────────────
UPOS_LIST = [
    "PAD", "UNK",
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ",
    "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
    "SCONJ", "SYM", "VERB", "X", "NN",
]
pos2id = {p: i for i, p in enumerate(UPOS_LIST)}
NUM_POS = len(pos2id)
POS_DIM = 32

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Arsitektur custom (persis notebook cell 11) ───────────────────────────────
class BertPosNER(nn.Module):
    """IndoBERT hidden (768) + POS embedding (32) -> concat (800) -> Dropout -> Linear."""

    def __init__(self, bert_module, num_labels, num_pos, pos_dim=32, dropout=0.1):
        super().__init__()
        self.bert = bert_module
        self.pos_emb = nn.Embedding(num_pos, pos_dim, padding_idx=0)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(bert_module.config.hidden_size + pos_dim, num_labels)
        self.num_labels = num_labels

    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None,
                pos_ids=None, labels=None, **kwargs):
        h = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                      token_type_ids=token_type_ids).last_hidden_state
        p = self.pos_emb(pos_ids if pos_ids is not None else torch.zeros_like(input_ids))
        out = self.dropout(torch.cat([h, p], dim=-1))
        logits = self.classifier(out)
        return TokenClassifierOutput(logits=logits)


def build_label_list(train_csv: Path):
    """label_list persis notebook: sorted(unique, key=(name[1:], name[0]))."""
    df = pd.read_csv(train_csv)
    labels = df["label"].fillna("O").unique().tolist()
    label_list = sorted(labels, key=lambda name: (name[1:], name[0]))
    id2label = {i: l for i, l in enumerate(label_list)}
    return label_list, id2label


def load_pos_model(checkpoint_dir: Path, num_labels: int):
    config = AutoConfig.from_pretrained(MODEL_NAME)
    bert = AutoModel.from_config(config)
    model = BertPosNER(bert, num_labels, NUM_POS, POS_DIM)
    state = torch.load(checkpoint_dir / "pytorch_model.bin", map_location="cpu")
    model.load_state_dict(state)               # strict: harus cocok 100%
    return model.to(DEVICE).eval()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", default="4", help="iterasi checkpoint POS-tag (default 4)")
    ap.add_argument("--test", default=str(DATA_DIR / "test.csv"))
    args = ap.parse_args()

    ckpt = MODELS_DIR / f"bert-pos-sirah-ner-0.9-iteration-{args.iter}"
    if not (ckpt / "pytorch_model.bin").exists():
        sys.exit(f"[ERR] checkpoint tidak ada: {ckpt}")

    label_list, id2label = build_label_list(DATA_DIR / "train.csv")
    print(f"[info] label_list ({len(label_list)}): {label_list}")
    print(f"[info] device={DEVICE} checkpoint={ckpt.name}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, model_max_length=512)
    model = load_pos_model(ckpt, len(label_list))

    df = pd.read_csv(args.test)
    df["token"] = df["token"].astype(str)
    if "pos_tag" not in df.columns:
        df["pos_tag"] = "NN"

    y_true, y_pred, pred_rows = [], [], []
    text_ids = df["text_id"].unique().tolist()

    for tid in text_ids:
        grp = df[df["text_id"] == tid]
        tokens = grp["token"].tolist()
        gold = grp["label"].fillna("O").tolist()
        pos_strs = grp["pos_tag"].astype(str).tolist()

        enc = tokenizer(tokens, truncation=True, is_split_into_words=True, return_tensors="pt")
        word_ids = enc.word_ids()
        pos_raw = [pos2id.get(p, pos2id["UNK"]) for p in pos_strs]
        pos_aligned = [0 if w is None else pos_raw[w] for w in word_ids]
        pos_tensor = torch.tensor([pos_aligned], dtype=torch.long)

        with torch.no_grad():
            out = model(input_ids=enc["input_ids"].to(DEVICE),
                        attention_mask=enc["attention_mask"].to(DEVICE),
                        token_type_ids=enc.get("token_type_ids").to(DEVICE) if "token_type_ids" in enc else None,
                        pos_ids=pos_tensor.to(DEVICE))
        logits = out.logits[0].cpu()

        preds, prev = [], None
        for w, row in zip(word_ids, logits):
            if w is None or w == prev:
                prev = w
                continue
            preds.append(id2label[int(row.argmax())])
            prev = w
        # tail terpotong (chunk > 512 subword) -> isi 'O' agar sejajar gold
        if len(preds) < len(tokens):
            preds += ["O"] * (len(tokens) - len(preds))

        y_true.append(gold)
        y_pred.append(preds)
        for tok, g, p in zip(tokens, gold, preds):
            pred_rows.append({"text_id": tid, "token": tok, "gold": g, "pred": p})

    report = classification_report(y_true, y_pred, digits=4)
    micro_f1 = f1_score(y_true, y_pred)
    micro_p = precision_score(y_true, y_pred)
    micro_r = recall_score(y_true, y_pred)

    print("\n" + report)
    print(f"micro  P={micro_p:.4f}  R={micro_r:.4f}  F1={micro_f1:.4f}")
    print("(rekonstruksi sebelumnya ~0.9432; selisih kecil = wajar)")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_PRED.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# Seqeval POS-tag — inference LANGSUNG (bukan rekonstruksi)\n\n")
        f.write(f"> `eval_postag_direct.py`, checkpoint iter-{args.iter}, test.csv "
                f"({df['text_id'].nunique()} chunk / {len(df)} token). Entity-level seqeval.\n\n")
        f.write(f"**micro**  Precision={micro_p:.4f}  Recall={micro_r:.4f}  **F1={micro_f1:.4f}**\n\n")
        f.write("```\n" + report + "\n```\n")
    pd.DataFrame(pred_rows).to_csv(OUT_PRED, index=False)
    print(f"\n[saved] {OUT_MD}")
    print(f"[saved] {OUT_PRED}")


if __name__ == "__main__":
    main()
