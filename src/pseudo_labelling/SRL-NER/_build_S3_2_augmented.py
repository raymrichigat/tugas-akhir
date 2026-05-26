"""
_build_S3_2_augmented.py
========================
Build skenario **S3.2 (SCL λ_C=0.3 + Mention Replacement Augmentation v2)** dari
notebook winner S3.1-lambda03 yang sudah ada.

Latar belakang (2026-05-26):
S3.1 λ_C sweep selesai, winner = λ_C=0.3 iter-4 (TEST F1 entity = 0.9522, sedikit di
atas S1=0.9518). Plan post-bimbingan 2026-05-16 Bu Diana: stack augmentation di atas
winner λ_C, bukan di atas λ_C arbitrary. Augmentation: train_augmented_v2.csv (period-
aware mention replacement, 260 augmented sentences di atas 599 original = 859 total).

Yang berubah dari S3.1-lambda03:
  1. Load `train_augmented_v2.csv` bukan `train.csv`.
  2. `experiment_name` suffix: `-S3-1-scl-lambda03` → `-S3-2-scl-aug-v2`.
  3. Title cell: "S3.1 (SCL λ_C=0.3 — λ_C Sweep)" → "S3.2 (SCL λ_C=0.3 + Mention Replacement v2)"
  4. Knob description di S3.1 cell.
  5. Smoke-test file existence list.

Yang TIDAK berubah:
  - λ_C = 0.3, τ = 0.1, contrastive_mode = 'scl'
  - N_ITERATIONS=6, THRESHOLD=0.9, sampling_rate=1.0, agg=simple
  - Validation split logic (fixed seed 42 by text_id)
  - Self-training pipeline atas unlabelled.csv

Prerequisite (sudah ada di repo):
  - `srl_ner_sirah_S3_1_scl_lambda03*.ipynb` (winner, hasil S3.1 sweep)
  - `data/result/pseudo-labelling/SRL-NER/train_augmented_v2.csv` (output augment_minor_classes_v2.py)

Idempotent. Usage:
  python src/pseudo_labelling/SRL-NER/_build_S3_2_augmented.py

Output (3 notebook):
  srl_ner_sirah_S3_2_scl_aug.ipynb
  srl_ner_sirah_S3_2_scl_aug_colab.ipynb
  srl_ner_sirah_S3_2_scl_aug_kaggle.ipynb
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# (S3.1 base file, S3.2 output file)
VARIANTS = [
    ("srl_ner_sirah_S3_1_scl_lambda03.ipynb",
     "srl_ner_sirah_S3_2_scl_aug.ipynb",
     "S3.2 (SCL λ_C=0.3 + Mention Replacement Augmentation v2)"),
    ("srl_ner_sirah_S3_1_scl_lambda03_colab.ipynb",
     "srl_ner_sirah_S3_2_scl_aug_colab.ipynb",
     "S3.2 (SCL λ_C=0.3 + Mention Replacement Augmentation v2)"),
    ("srl_ner_sirah_S3_1_scl_lambda03_kaggle.ipynb",
     "srl_ner_sirah_S3_2_scl_aug_kaggle.ipynb",
     "S3.2 (SCL λ_C=0.3 + Mention Replacement Augmentation v2)"),
]


def src_str(cell) -> str:
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def set_src(cell, text: str):
    cell["source"] = text.splitlines(keepends=True)


def transform_text(src: str) -> tuple[str, bool]:
    """Apply S3.1-lambda03 → S3.2 transformations on a code/markdown cell."""
    modified = False
    new_src = src

    patterns = [
        # 1. Swap train.csv → train_augmented_v2.csv di pd.read_csv calls
        ("pd.read_csv(os.path.join(dataset_dir, 'train.csv'))",
         "pd.read_csv(os.path.join(dataset_dir, 'train_augmented_v2.csv'))"),
        ("pd.read_csv(os.path.join(dataset_dir, \"train.csv\"))",
         "pd.read_csv(os.path.join(dataset_dir, \"train_augmented_v2.csv\"))"),
        # 2. Smoke test file list
        ("['train.csv', 'test.csv', 'unlabelled.csv']",
         "['train_augmented_v2.csv', 'test.csv', 'unlabelled.csv']"),
        # 3. Comment yang menjelaskan upload requirements
        ("# Upload train.csv / test.csv / unlabelled.csv ke folder Drive berikut:",
         "# Upload train_augmented_v2.csv / test.csv / unlabelled.csv ke folder Drive berikut:\n"
         "# (train_augmented_v2.csv = output augment_minor_classes_v2.py — period-aware mention replacement)"),
        # 4. experiment_name rename
        ("experiment_name = f'{_name}-{_type}-S3-1-scl-lambda03'",
         "experiment_name = f'{_name}-{_type}-S3-2-scl-aug-v2'"),
        # 5. Knob print prefix
        ("[S3.1/lambda03]", "[S3.2/scl-aug-v2]"),
        # 6. Knob block comment (S3.1 → S3.2 framing)
        ("# === [S3.1] Knob Contrastive Learning — λ_C Sweep ===",
         "# === [S3.2] Knob Contrastive Learning — Winner λ_C + Augmentation ==="),
        ("# Skenario S3.1: tune λ_C di S2 SCL untuk close gap entity-level vs S1 baseline.\n"
         "# Hipotesis: λ_C=0.3 default terlalu agresif → contrastive over-prioritize per-token\n"
         "# similarity dengan mengkompromi entity boundary detection. Sweep λ_C ∈ {0.1, 0.2, 0.3}.\n"
         "#\n"
         "# Variant aktif notebook ini: λ_C = 0.3",
         "# Skenario S3.2: stack mention replacement augmentation di atas winner λ_C dari S3.1.\n"
         "# S3.1 result: λ_C=0.3 iter-4 → TEST F1 entity = 0.9522 (sedikit di atas S1=0.9518).\n"
         "# Hipotesis S3.2: augmentation v2 (period-aware, 260 augmented sentences) close residual\n"
         "# gap di kelas minoritas (B-EVENT, I-EVENT, I-LOCATION) tanpa anakronistik.\n"
         "#\n"
         "# Konfigurasi: λ_C = 0.3 (winner), τ = 0.1 (default S2/S3.1)"),
        # 7. Runtime timer label
        ("[S3.1 TIMER]", "[S3.2 TIMER]"),
        ("# === [S3.1] Runtime Timer — START ===",
         "# === [S3.2] Runtime Timer — START ==="),
        ("# === [S3.1] Runtime Timer — END + write log ===",
         "# === [S3.2] Runtime Timer — END + write log ==="),
        ("Catat wall-clock start untuk analisis runtime per skenario (request Bu Diana).",
         "Catat wall-clock start untuk analisis runtime S3.2 (augmentation overhead expected ~+10-15%)."),
        # 8. Iteration loop comment
        ("# Skenario S3.1: tune λ_C di S2 SCL untuk close gap entity-level vs S1 baseline.",
         "# Skenario S3.2: λ_C=0.3 (winner) + train_augmented_v2.csv (mention replacement augmentation)."),
    ]

    for old, new in patterns:
        if old in new_src and (new not in new_src or new == old):
            new_src = new_src.replace(old, new)
            modified = True

    return new_src, modified


def transform_markdown_title(src: str, new_title: str) -> str:
    """Replace S3.1 lambda03 title prefix in first markdown cell."""
    s31_titles = [
        "# SRL-NER Sirah — S3.1 (SCL λ_C=0.3 — λ_C Sweep)",
        "# SRL-NER Sirah — S3.1 (SCL λ_C=0.3)",
    ]
    new_header = f"# SRL-NER Sirah — {new_title}"
    for old in s31_titles:
        if old in src:
            return src.replace(old, new_header, 1)

    s31_subs = [
        "Skenario S3.1 — λ_C Sweep di S2 SCL untuk close gap entity-level vs S1 baseline.",
    ]
    new_sub = ("Skenario S3.2 — winner λ_C=0.3 (S3.1 hasil) + Mention Replacement Augmentation v2 "
               "(period-aware, blacklist + Quran/hadits guard).")
    for old_sub in s31_subs:
        if old_sub in src:
            src = src.replace(old_sub, new_sub, 1)

    return src


def build_one(base_path: Path, out_path: Path, title_subtitle: str):
    nb = json.loads(base_path.read_text(encoding="utf-8"))

    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    for c in nb["cells"]:
        new_src, modified = transform_text(src_str(c))
        if modified:
            set_src(c, new_src)

    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        title_src = transform_markdown_title(title_src, title_subtitle)
        set_src(nb["cells"][0], title_src)

    nb.setdefault("metadata", {})
    nb["metadata"]["sirah_experiment"] = "S3_2_scl_aug_v2"

    out_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {out_path.name}")


def main():
    for base_name, out_name, title in VARIANTS:
        base = HERE / base_name
        out = HERE / out_name
        if not base.exists():
            print(f"SKIP base notebook missing: {base_name}")
            continue
        build_one(base, out, title)


if __name__ == "__main__":
    main()
