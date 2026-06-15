"""
_build_S3_augmented.py
======================
Build skenario **S3 (Sentence-based Augmentation + S2)** dari notebook S2 yang sudah
dihasilkan oleh `_build_S2_contrastive.py`.

S3 = S2 + augmented training data. Yang berubah dari S2:
  1. Load `train_augmented.csv` (output `augment_minor_classes.py`) bukan `train.csv`.
  2. `experiment_name` suffix: `-S2a-scl`  → `-S3a-scl-aug`
                                `-S2b-jscl` → `-S3b-jscl-aug`
  3. Title cell prefix update.

Loss function (SCL / JSCL) + knob lambda/tau **tidak berubah** — hanya data train yang
diganti. Filosofi S3 = orthogonal data-level intervention di atas model-level S2.

Prerequisite:
  - `_build_S2_contrastive.py` sudah dijalankan (6 notebook S2 ada di folder ini).
  - `augment_minor_classes.py` sudah dijalankan (file
    `data/result/pseudo-labelling/SRL-NER/train_augmented.csv` exists).

Idempotent. Usage:
  python _build_S3_augmented.py

Output (6 notebook total):
  srl_ner_sirah_S3a_scl_aug.ipynb          (lokal)
  srl_ner_sirah_S3a_scl_aug_colab.ipynb    (Colab/Drive)
  srl_ner_sirah_S3a_scl_aug_kaggle.ipynb   (Kaggle)
  srl_ner_sirah_S3b_jscl_aug.ipynb         (lokal)
  srl_ner_sirah_S3b_jscl_aug_colab.ipynb   (Colab/Drive)
  srl_ner_sirah_S3b_jscl_aug_kaggle.ipynb  (Kaggle)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# (S2 base file, S3 output file)
VARIANTS = [
    # S3a (SCL + augmentation)
    ("srl_ner_sirah_S2a_scl.ipynb",         "srl_ner_sirah_S3a_scl_aug.ipynb",        "S3a (SCL + Sentence Augmentation)"),
    ("srl_ner_sirah_S2a_scl_colab.ipynb",   "srl_ner_sirah_S3a_scl_aug_colab.ipynb",  "S3a (SCL + Sentence Augmentation)"),
    ("srl_ner_sirah_S2a_scl_kaggle.ipynb",  "srl_ner_sirah_S3a_scl_aug_kaggle.ipynb", "S3a (SCL + Sentence Augmentation)"),
    # S3b (JSCL + augmentation)
    ("srl_ner_sirah_S2b_jscl.ipynb",        "srl_ner_sirah_S3b_jscl_aug.ipynb",        "S3b (JSCL + Sentence Augmentation)"),
    ("srl_ner_sirah_S2b_jscl_colab.ipynb",  "srl_ner_sirah_S3b_jscl_aug_colab.ipynb",  "S3b (JSCL + Sentence Augmentation)"),
    ("srl_ner_sirah_S2b_jscl_kaggle.ipynb", "srl_ner_sirah_S3b_jscl_aug_kaggle.ipynb", "S3b (JSCL + Sentence Augmentation)"),
]


def src_str(cell) -> str:
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def set_src(cell, text: str):
    cell["source"] = text.splitlines(keepends=True)


def transform_text(src: str) -> tuple[str, bool]:
    """
    Apply S2 → S3 transformations on a code cell's source text.
    Returns (new_src, modified).
    """
    modified = False
    new_src = src

    # 1. swap train.csv → train_augmented.csv di pd.read_csv calls + smoke test list
    patterns = [
        # Read train CSV
        ("pd.read_csv(os.path.join(dataset_dir, 'train.csv'))",
         "pd.read_csv(os.path.join(dataset_dir, 'train_augmented.csv'))"),
        ("pd.read_csv(os.path.join(dataset_dir, \"train.csv\"))",
         "pd.read_csv(os.path.join(dataset_dir, \"train_augmented.csv\"))"),
        # Smoke test file existence list
        ("['train.csv', 'test.csv', 'unlabelled.csv']",
         "['train_augmented.csv', 'test.csv', 'unlabelled.csv']"),
        # Comment yang menjelaskan upload requirements
        ("# Upload train.csv / test.csv / unlabelled.csv ke folder Drive berikut:",
         "# Upload train_augmented.csv / test.csv / unlabelled.csv ke folder Drive berikut:\n# (train_augmented.csv = output augment_minor_classes.py — lihat data/result/pseudo-labelling/SRL-NER/)"),
    ]
    for old, new in patterns:
        if old in new_src and new not in new_src:
            new_src = new_src.replace(old, new)
            modified = True

    # 2. rename experiment_name suffix
    rename_pairs = [
        ("experiment_name = f'{_name}-{_type}-S2a-scl'",
         "experiment_name = f'{_name}-{_type}-S3a-scl-aug'"),
        ("experiment_name = f'{_name}-{_type}-S2b-jscl'",
         "experiment_name = f'{_name}-{_type}-S3b-jscl-aug'"),
    ]
    for old, new in rename_pairs:
        if old in new_src:
            new_src = new_src.replace(old, new)
            modified = True

    # 3. update mode-tag di knob cell print f-string
    knob_pairs = [
        ("[S2/S2a-scl]", "[S3/S3a-scl-aug]"),
        ("[S2/S2b-jscl]", "[S3/S3b-jscl-aug]"),
    ]
    for old, new in knob_pairs:
        if old in new_src:
            new_src = new_src.replace(old, new)
            modified = True

    return new_src, modified


def build_one(base_path: Path, out_path: Path, title_subtitle: str):
    nb = json.loads(base_path.read_text(encoding="utf-8"))

    # Step 1: strip outputs
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    # Step 2: transform code cells
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        new_src, modified = transform_text(src_str(c))
        if modified:
            set_src(c, new_src)

    # Step 3: title cell update
    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        # Replace existing S2 title prefix if any
        s2_prefixes = [
            "# SRL-NER Sirah — S2a (SCL — Strict Supervised Contrastive Learning)",
            "# SRL-NER Sirah — S2b (JSCL — Jaccard Similarity Contrastive Learning, sentence-level)",
        ]
        for old in s2_prefixes:
            if old in title_src:
                title_src = title_src.replace(old, f"# SRL-NER Sirah — {title_subtitle}", 1)
                break
        else:
            # No S2 prefix found, prepend
            if "Augmentation" not in title_src:
                title_src = f"# SRL-NER Sirah — {title_subtitle}\n\n" + title_src
        set_src(nb["cells"][0], title_src)

    # Step 4: metadata tag
    nb.setdefault("metadata", {})
    if "S3a" in title_subtitle:
        nb["metadata"]["sirah_experiment"] = "S3_aug_scl"
    elif "S3b" in title_subtitle:
        nb["metadata"]["sirah_experiment"] = "S3_aug_jscl"

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
