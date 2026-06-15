"""
_build_S2.py
============
Build srl_ner_sirah_S2_adaptive_*.ipynb dari baseline srl_ner_sirah_0.9_*.ipynb.

S2 = Adaptif Threshold (0.9 → 0.7 dropping-only) + Class Weight (inverse frequency).
Mewarisi semua perubahan S1 (class weights + WeightedTrainer), TAMBAH:
  - Hyperparameter THRESHOLD_INIT/MIN/STEP/TARGET_MIN_SAMPLES
  - Main loop diganti versi adaptif (drop threshold sampai dapat min samples)
  - iteration_log tambah kolom threshold_used (untuk plot threshold dinamis)
  - experiment_name suffix '-S2' supaya output di Drive ter-isolasi

Idempotent. Usage:
  python _build_S2.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

VARIANTS = [
    ("srl_ner_sirah_0.9.ipynb",        "srl_ner_sirah_S2_adaptive.ipynb"),
    ("srl_ner_sirah_0.9_colab.ipynb",  "srl_ner_sirah_S2_adaptive_colab.ipynb"),
    ("srl_ner_sirah_0.9_kaggle.ipynb", "srl_ner_sirah_S2_adaptive_kaggle.ipynb"),
]


# ── S1 cell: compute class weights (sama persis dengan _build_S1.py) ─────────
CLASS_WEIGHT_CELL_SOURCE = """# === [S2] Compute class weights (inverse frequency) ===
import torch
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

labels_in_train = df_train["label"].dropna().tolist()
label_counts = Counter(labels_in_train)
print("Distribusi label train:")
total_lbl = sum(label_counts.values())
for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
    pct = 100 * cnt / total_lbl
    print(f"  {lbl:<14} {cnt:>6}  {pct:>5.2f}%")

import numpy as np
classes_arr = sorted(label_counts.keys(), key=lambda x: label2id[x])
y_arr = labels_in_train
weights_np = compute_class_weight('balanced', classes=np.array(classes_arr), y=y_arr)

# Clipping untuk stabilitas — bobot ekstrem (>50x) bisa bikin training NaN
WEIGHT_CLIP_MAX = 50.0
weights_np_clipped = [min(float(w), WEIGHT_CLIP_MAX) for w in weights_np]

class_weights_tensor = torch.zeros(len(label_list), dtype=torch.float)
for lbl, w in zip(classes_arr, weights_np_clipped):
    class_weights_tensor[label2id[lbl]] = w

print(f"\\nClass weights (clipped to max {WEIGHT_CLIP_MAX:.0f}):")
for lbl, w in zip(classes_arr, weights_np_clipped):
    print(f"  {lbl:<14} {w:>7.2f}")
"""


# ── S1 code: WeightedTrainer subclass ────────────────────────────────────────
WEIGHTED_TRAINER_CODE = """
# === [S2] WeightedTrainer subclass — apply class weights ke CrossEntropyLoss ===
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


# ── S2: replacement untuk main loop cell (cell 22 di baseline) ───────────────
# Kita REPLACE seluruh isi cell 22 dengan versi adaptif.
S2_LOOP_CELL = '''# ============================================================
# [S2] Iterative pseudo-labelling loop with ADAPTIVE THRESHOLD
# ============================================================
# - Threshold mulai dari THRESHOLD_INIT (0.9). Kalau jumlah pseudo-label yang
#   lolos < TARGET_MIN_SAMPLES, threshold turun bertahap (0.85, 0.80, ...) sampai
#   dapat cukup atau mencapai THRESHOLD_MIN (0.7). Dropping-only (tidak naik).
# - iter_log mencatat threshold_used per iterasi → bisa di-plot.
# - Inherits S1 (class weights via WeightedTrainer di train_model).

# === Knob baseline (sama dengan E1/S1) ===
N_ITERATIONS    = 6
THRESHOLD       = 0.9        # legacy var untuk reconstruct_unlabelled (path file)
SAMPLING_RATE   = 1.0
MIN_ENTITY_CONF = None
MIN_NEW_SAMPLES = 0
AGG_STRATEGY    = "simple"

# === Knob adaptif S2 ===
THRESHOLD_INIT     = 0.9     # threshold awal tiap iterasi
THRESHOLD_MIN      = 0.7     # batas bawah; tidak akan turun di bawah ini
THRESHOLD_STEP     = 0.05    # langkah penurunan
TARGET_MIN_SAMPLES = 50      # minimal kalimat lolos per iter; kalau < ini, drop threshold

# Stable validation split (fix B)
import random as _random
_seed_ids = sorted(df_train["text_id"].unique().tolist())
_rng = _random.Random(42)
_rng.shuffle(_seed_ids)
_n_val = max(1, int(round(len(_seed_ids) * 0.2)))
VAL_TEXT_IDS = _seed_ids[:_n_val]
print(f"[val split] {len(VAL_TEXT_IDS)} / {len(_seed_ids)} seed text_ids reserved for validation")

# Load unlabelled
df_unlabelled = pd.read_csv(os.path.join(dataset_dir, 'unlabelled.csv'))
df_unlabelled["token"] = df_unlabelled["token"].apply(str)

# Bootstrap: train base model on seed
train_val_base = df_to_dataset_for_model(df_train, val_text_ids=VAL_TEXT_IDS)
print(train_val_base)

train_model(
    model_name="indolem/indobert-base-uncased",
    train_dataset=train_val_base["train"],
    val_dataset=train_val_base["validation"],
    model_output_path=os.path.join(model_dir, f"{experiment_name}-base"),
)

# Iterative loop dengan adaptive threshold
pseudo_dfs = []
iter_log = []
current_unlabelled = df_unlabelled
current_model_name = f"{experiment_name}-base"

for i in range(1, N_ITERATIONS + 1):
    if len(current_unlabelled) == 0:
        print(f"[iter {i}] no unlabelled chunks left -> STOP (self-training converged at iter {i-1})")
        break

    prev_model_path = os.path.join(model_dir, current_model_name)
    base_prefix = experiment_name if i == 1 else f"{experiment_name}-iterative-{i}"

    # === ADAPTIVE: mulai threshold tinggi, turun bertahap kalau kurang ===
    threshold = THRESHOLD_INIT
    prefix = base_prefix
    above_df = filter_threshold(
        model_path=prev_model_path,
        df=current_unlabelled,
        threshold=threshold,
        output_dir=eval_dir,
        output_filename_prefix=prefix,
        sampling_rate=SAMPLING_RATE,
        min_entity_confidence=MIN_ENTITY_CONF,
        aggregation_strategy=AGG_STRATEGY,
    )
    n_above = int(above_df["text_id"].nunique()) if len(above_df) else 0

    while n_above < TARGET_MIN_SAMPLES and threshold > THRESHOLD_MIN:
        threshold = round(threshold - THRESHOLD_STEP, 2)
        prefix = f"{base_prefix}-t{threshold}"  # nama beda biar tidak overwrite cache
        print(f"[iter {i}] only {n_above} above @ {threshold + THRESHOLD_STEP:.2f} -> drop ke {threshold}")
        above_df = filter_threshold(
            model_path=prev_model_path,
            df=current_unlabelled,
            threshold=threshold,
            output_dir=eval_dir,
            output_filename_prefix=prefix,
            sampling_rate=SAMPLING_RATE,
            min_entity_confidence=MIN_ENTITY_CONF,
            aggregation_strategy=AGG_STRATEGY,
        )
        n_above = int(above_df["text_id"].nunique()) if len(above_df) else 0

    print(f"[iter {i}] FINAL threshold={threshold}, above: {n_above} sentences")
    iter_log.append({"iter": i, "threshold_used": threshold, "n_above": n_above})

    if n_above < TARGET_MIN_SAMPLES:
        print(f"[iter {i}] adaptive mentok di {threshold} (still < TARGET_MIN_SAMPLES={TARGET_MIN_SAMPLES}) -> STOP")
        # Tetap include pseudo-label yang ada (bukan zero) sebelum stop
        if n_above > 0:
            pseudo_dfs.append(above_df)
        break

    if MIN_NEW_SAMPLES > 0 and n_above < MIN_NEW_SAMPLES:
        print(f"[iter {i}] early-stop: {n_above} < MIN_NEW_SAMPLES={MIN_NEW_SAMPLES}")
        break

    pseudo_dfs.append(above_df)

    # No retrain after the last iteration (matches Bu Diana)
    if i < N_ITERATIONS:
        new_model_name = f"{experiment_name}-iteration-{i+1}"
        combined = pd.concat([df_train] + pseudo_dfs, ignore_index=True)
        train_val_iter = df_to_dataset_for_model(combined, val_text_ids=VAL_TEXT_IDS)
        print(train_val_iter)

        train_model(
            model_name=prev_model_path,
            train_dataset=train_val_iter["train"],
            val_dataset=train_val_iter["validation"],
            model_output_path=os.path.join(model_dir, new_model_name),
        )
        current_model_name = new_model_name

        # Next-iter unlabelled = below-threshold sentences DARI THRESHOLD YANG DIPAKAI
        below_path = os.path.join(eval_dir, f"{prefix}-below-{threshold}.xlsx")
        current_unlabelled = reconstruct_unlabelled_from_below(below_path)

# Save iter log dengan kolom threshold_used (untuk plot adaptive)
pd.DataFrame(iter_log).to_csv(os.path.join(eval_dir, f"iteration_log_{experiment_name}.csv"), index=False)
print("\\nIteration log:")
print(pd.DataFrame(iter_log).to_string(index=False))

# Convenience aliases so downstream eval cells keep their variable names
final_iter = iter_log[-1]["iter"] if iter_log else 0
above_09_df = pseudo_dfs[0] if pseudo_dfs else pd.DataFrame()
'''


# ── Helpers (sama dengan _build_S1.py) ───────────────────────────────────────
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

    # Step 1: drop existing outputs
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    # Step 2: rename experiment_name → -S2 + path isolation
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = src_str(c)
        modified = False
        if "experiment_name = f'{_name}-{_type}'" in src:
            src = src.replace(
                "experiment_name = f'{_name}-{_type}'",
                "experiment_name = f'{_name}-{_type}-S2'",
            )
            modified = True
        replacements = [
            ('"bert-only-sirah-ner-confidence-0.9-misclassified.xlsx"',
             'f"{experiment_name}-confidence-0.9-misclassified.xlsx"'),
            ('"bert-only-sirah-ner-iterative-6"',
             'f"{experiment_name}-iterative-6"'),
        ]
        for old, new in replacements:
            if old in src:
                src = src.replace(old, new)
                modified = True
        if modified:
            set_src(c, src)

    # Step 3: insert class weights cell setelah label2id
    label_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code" and "label_list = sorted(df_train" in src_str(c),
    )
    if label_idx == -1:
        raise RuntimeError(f"Cannot find label_list cell in {base_path.name}")

    next_cell = nb["cells"][label_idx + 1] if label_idx + 1 < len(nb["cells"]) else None
    if next_cell and next_cell["cell_type"] == "code" and "[S2] Compute class weights" in src_str(next_cell):
        nb["cells"][label_idx + 1] = make_code_cell(CLASS_WEIGHT_CELL_SOURCE)
    else:
        nb["cells"].insert(label_idx + 1, make_code_cell(CLASS_WEIGHT_CELL_SOURCE))

    # Step 4: modifikasi cell train_model — inject WeightedTrainer + class_weights arg
    train_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code"
        and "def train_model" in src_str(c)
        and "DataCollatorForTokenClassification" in src_str(c),
    )
    if train_idx == -1:
        raise RuntimeError(f"Cannot find train_model cell in {base_path.name}")

    src = src_str(nb["cells"][train_idx])
    if "class WeightedTrainer" not in src:
        src = src.replace("def train_model(", WEIGHTED_TRAINER_CODE.lstrip() + "def train_model(", 1)
    if "trainer = Trainer(" in src:
        src = src.replace("trainer = Trainer(", "trainer = WeightedTrainer(")
    OLD_END = "compute_metrics=compute_metrics,\n    )"
    NEW_END = "compute_metrics=compute_metrics,\n        class_weights=class_weights_tensor,\n    )"
    if OLD_END in src and "class_weights=class_weights_tensor" not in src:
        src = src.replace(OLD_END, NEW_END, 1)
    set_src(nb["cells"][train_idx], src)

    # Step 5: REPLACE main loop cell dengan versi adaptif
    loop_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code"
        and "Iterative pseudo-labelling loop" in src_str(c)
        and "N_ITERATIONS" in src_str(c),
    )
    if loop_idx == -1:
        raise RuntimeError(f"Cannot find main iterative loop cell in {base_path.name}")
    set_src(nb["cells"][loop_idx], S2_LOOP_CELL)

    # Step 6: title update
    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        if "S2" not in title_src:
            new_title = "# SRL-NER Sirah — S2 (Adaptive Threshold 0.9→0.7 + Class Weight)\n\n" + title_src
            set_src(nb["cells"][0], new_title)

    nb.setdefault("metadata", {})
    nb["metadata"]["sirah_experiment"] = "S2_adaptive_classweight"

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
