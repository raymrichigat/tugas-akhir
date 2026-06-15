"""
_build_S1.py
============
Build srl_ner_sirah_S1_classweight_*.ipynb dari baseline srl_ner_sirah_0.9_*.ipynb.

S1 = Fix Threshold (0.9) + Class Weight (inverse frequency).
Logika baseline E1 dipertahankan; yang diubah hanya:
  1. Tambah cell baru SETELAH label2id setup → compute class weights
  2. Modifikasi cell train_model → pakai WeightedTrainer subclass

Idempotent: bisa di-run berulang, akan re-generate file output.

Usage:
  python _build_S1.py
"""

import json
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).parent

VARIANTS = [
    ("srl_ner_sirah_0.9.ipynb",        "srl_ner_sirah_S1_classweight.ipynb"),
    ("srl_ner_sirah_0.9_colab.ipynb",  "srl_ner_sirah_S1_classweight_colab.ipynb"),
    ("srl_ner_sirah_0.9_kaggle.ipynb", "srl_ner_sirah_S1_classweight_kaggle.ipynb"),
]


# ── Cell baru: compute class weights ─────────────────────────────────────────
CLASS_WEIGHT_CELL_SOURCE = """# === [S1] Compute class weights (inverse frequency) ===
import torch
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

# Hitung distribusi label di seed (df_train)
labels_in_train = df_train["label"].dropna().tolist()
label_counts = Counter(labels_in_train)
print("Distribusi label train:")
total_lbl = sum(label_counts.values())
for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
    pct = 100 * cnt / total_lbl
    print(f"  {lbl:<14} {cnt:>6}  {pct:>5.2f}%")

# Hitung class weight inverse frequency
import numpy as np
classes_arr = sorted(label_counts.keys(), key=lambda x: label2id[x])
y_arr = labels_in_train
weights_np = compute_class_weight('balanced', classes=np.array(classes_arr), y=y_arr)

# Clipping untuk stabilitas — bobot ekstrem (>50x) bisa bikin training NaN
WEIGHT_CLIP_MAX = 50.0
weights_np_clipped = [min(float(w), WEIGHT_CLIP_MAX) for w in weights_np]

# Re-order tensor sesuai id2label index (penting untuk match logits)
class_weights_tensor = torch.zeros(len(label_list), dtype=torch.float)
for lbl, w in zip(classes_arr, weights_np_clipped):
    class_weights_tensor[label2id[lbl]] = w

print(f"\\nClass weights (clipped to max {WEIGHT_CLIP_MAX:.0f}):")
for lbl, w in zip(classes_arr, weights_np_clipped):
    print(f"  {lbl:<14} {w:>7.2f}")
"""


# ── WeightedTrainer subclass code (akan disisipkan di cell train_model) ──────
WEIGHTED_TRAINER_CODE = """
# === [S1] WeightedTrainer subclass — apply class weights ke CrossEntropyLoss ===
class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        weight = self._class_weights.to(logits.device) if self._class_weights is not None else None
        loss_fct = torch.nn.CrossEntropyLoss(weight=weight, ignore_index=-100)
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


"""


def find_cell_index(nb, predicate):
    for i, c in enumerate(nb["cells"]):
        if predicate(c):
            return i
    return -1


def src_str(cell) -> str:
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def set_src(cell, text: str):
    cell["source"] = text.splitlines(keepends=True)


def make_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def build_one(base_path: Path, out_path: Path):
    nb = json.loads(base_path.read_text(encoding="utf-8"))

    # ─ Step 1: drop existing outputs (S1 belum di-run) ─
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    # ─ Step 1b: rename experiment_name → tambah suffix -S1 (output isolation) ─
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = src_str(c)
        modified = False
        if "experiment_name = f'{_name}-{_type}'" in src:
            src = src.replace(
                "experiment_name = f'{_name}-{_type}'",
                "experiment_name = f'{_name}-{_type}-S1'",
            )
            modified = True
        # Hardcoded prefix di cell 22 → bind ke experiment_name
        if 'prefix = "bert-only-sirah-ner" if i == 1 else f"bert-only-sirah-ner-iterative-{i}"' in src:
            src = src.replace(
                'prefix = "bert-only-sirah-ner" if i == 1 else f"bert-only-sirah-ner-iterative-{i}"',
                'prefix = experiment_name if i == 1 else f"{experiment_name}-iterative-{i}"',
            )
            modified = True
        # Rename hardcoded eval/log paths supaya tidak overwrite baseline:
        #   "bert-only-sirah-ner-iterative-6" -> f"{experiment_name}-iterative-6"
        #   "bert-only-sirah-ner-confidence-0.9-misclassified.xlsx" -> f"{experiment_name}-confidence-0.9-misclassified.xlsx"
        #   "iteration_log.csv" -> f"iteration_log_{experiment_name}.csv"
        replacements = [
            ('"bert-only-sirah-ner-confidence-0.9-misclassified.xlsx"',
             'f"{experiment_name}-confidence-0.9-misclassified.xlsx"'),
            ('"bert-only-sirah-ner-iterative-6"',
             'f"{experiment_name}-iterative-6"'),
            ('"iteration_log.csv"', 'f"iteration_log_{experiment_name}.csv"'),
        ]
        for old, new in replacements:
            if old in src:
                src = src.replace(old, new)
                modified = True
        if modified:
            set_src(c, src)

    # ─ Step 2: cari cell label2id, sisipkan cell class weights setelahnya ─
    label_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code" and "label_list = sorted(df_train" in src_str(c),
    )
    if label_idx == -1:
        raise RuntimeError(f"Cannot find label_list cell in {base_path.name}")

    # Hindari duplikasi kalau script di-run ulang
    next_cell = nb["cells"][label_idx + 1] if label_idx + 1 < len(nb["cells"]) else None
    if next_cell and next_cell["cell_type"] == "code" and "[S1] Compute class weights" in src_str(next_cell):
        # Replace existing S1 cell
        nb["cells"][label_idx + 1] = make_code_cell(CLASS_WEIGHT_CELL_SOURCE)
    else:
        nb["cells"].insert(label_idx + 1, make_code_cell(CLASS_WEIGHT_CELL_SOURCE))

    # ─ Step 3: modifikasi cell train_model (data_collator + def train_model) ─
    train_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code"
        and "def train_model" in src_str(c)
        and "DataCollatorForTokenClassification" in src_str(c),
    )
    if train_idx == -1:
        raise RuntimeError(f"Cannot find train_model cell in {base_path.name}")

    src = src_str(nb["cells"][train_idx])

    # 3a. Inject WeightedTrainer class definition before `def train_model`
    if "class WeightedTrainer" not in src:
        marker = "def train_model("
        if marker not in src:
            raise RuntimeError(f"Cannot locate 'def train_model(' in {base_path.name}")
        src = src.replace(marker, WEIGHTED_TRAINER_CODE.lstrip() + marker, 1)

    # 3b. Replace `trainer = Trainer(` with `trainer = WeightedTrainer(`
    if "trainer = Trainer(" in src:
        src = src.replace("trainer = Trainer(", "trainer = WeightedTrainer(")

    # 3c. Inject class_weights argument into the WeightedTrainer call
    # Cari blok `trainer = WeightedTrainer(\n ... compute_metrics=compute_metrics,\n    )`
    # Pendekatan simpel: cari "compute_metrics=compute_metrics,\n    )" lalu tambahkan class_weights line sebelum penutup
    OLD_END = "compute_metrics=compute_metrics,\n    )"
    NEW_END = "compute_metrics=compute_metrics,\n        class_weights=class_weights_tensor,\n    )"
    if OLD_END in src and "class_weights=class_weights_tensor" not in src:
        src = src.replace(OLD_END, NEW_END, 1)

    set_src(nb["cells"][train_idx], src)

    # ─ Step 4: update markdown title (cosmetic) ─
    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        if "S1" not in title_src:
            new_title = "# SRL-NER Sirah — S1 (Fix Threshold 0.9 + Class Weight)\n\n" + title_src
            set_src(nb["cells"][0], new_title)

    # ─ Step 5: tambah catatan eksperimen di metadata (opsional, untuk traceability) ─
    nb.setdefault("metadata", {})
    nb["metadata"]["sirah_experiment"] = "S1_classweight"

    # ─ Save ─
    out_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {out_path.name}")


def main():
    for base_name, out_name in VARIANTS:
        base = HERE / base_name
        out = HERE / out_name
        if not base.exists():
            print(f"SKIP {base_name} (not found)")
            continue
        build_one(base, out)


if __name__ == "__main__":
    main()
