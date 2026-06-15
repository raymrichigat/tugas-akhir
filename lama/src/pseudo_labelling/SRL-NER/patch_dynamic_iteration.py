"""
patch_dynamic_iteration.py
==========================
Fix bug evaluation cell di S3.1 (dan S2a/S2b) yang hardcode `iteration-6`.

**Bug:** kalau self-training stop early (mis. iter-4 karena n_above=0), file
model `iteration-6` tidak ada → transformers fallback ke hf_hub_download →
HFValidationError karena path absolute Drive di-treat sebagai HF repo ID.

**Fix:**
  1. Inject helper cell `LAST_ITER` yang scan model_dir untuk find iter tertinggi
     yang ada filenya. Pattern: `{experiment_name}-0.9-iteration-{N}` atau
     `{experiment_name}-base` (kalau baseline saja yang tersimpan).
  2. Replace hardcode `iteration-6` → f-string dengan {LAST_ITER}.

Idempotent. Usage:
  python patch_dynamic_iteration.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

LAST_ITER_HELPER_CELL = '''# === [PATCH] Auto-detect iterasi terakhir model yang tersimpan ===
# Self-training kadang stop early kalau n_above=0 (no pseudo-label baru di atas
# threshold). Hardcode `iteration-6` jadi error kalau file model tidak ada.
# Cell ini scan model_dir untuk find iter tertinggi yang valid.
import re

def _find_last_iteration(model_dir, experiment_name):
    """Returns int N for last `iteration-{N}` model directory yang exist."""
    pattern = re.compile(rf"^{re.escape(experiment_name)}-0\\.9-iteration-(\\d+)$")
    if not os.path.isdir(model_dir):
        return None
    iters = []
    for entry in os.listdir(model_dir):
        m = pattern.match(entry)
        if m:
            full_path = os.path.join(model_dir, entry)
            # Verify it's actually a model dir (has config.json)
            if os.path.exists(os.path.join(full_path, "config.json")):
                iters.append(int(m.group(1)))
    return max(iters) if iters else None

LAST_ITER = _find_last_iteration(model_dir, experiment_name)
if LAST_ITER is None:
    print(f"[WARN] No iteration-N model found in {model_dir}. Falling back to base model.")
    LAST_MODEL_PATH = os.path.join(model_dir, f"{experiment_name}-base")
    LAST_MODEL_TAG = "base"
else:
    LAST_MODEL_PATH = os.path.join(model_dir, f"{experiment_name}-0.9-iteration-{LAST_ITER}")
    LAST_MODEL_TAG = f"iterative-{LAST_ITER}"
    print(f"[OK] Last iteration found: {LAST_ITER}")
    print(f"     Model path: {LAST_MODEL_PATH}")
    print(f"     Tag       : {LAST_MODEL_TAG}")
'''


# Replacement patterns: (old_string, new_string)
REPLACEMENTS = [
    (
        'model_path=os.path.join(model_dir ,f"{experiment_name}-0.9-iteration-6")',
        'model_path=LAST_MODEL_PATH',
    ),
    (
        'model_path=os.path.join(model_dir, f"{experiment_name}-0.9-iteration-6")',
        'model_path=LAST_MODEL_PATH',
    ),
    (
        'f"{experiment_name}-iterative-6"',
        'f"{experiment_name}-{LAST_MODEL_TAG}"',
    ),
]

NOTEBOOKS = [
    "srl_ner_sirah_S2a_scl.ipynb",
    "srl_ner_sirah_S2a_scl_colab.ipynb",
    "srl_ner_sirah_S2a_scl_kaggle.ipynb",
    "srl_ner_sirah_S2b_jscl.ipynb",
    "srl_ner_sirah_S2b_jscl_colab.ipynb",
    "srl_ner_sirah_S2b_jscl_kaggle.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda01.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda01_colab.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda01_kaggle.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda02.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda02_colab.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda02_kaggle.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda03.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda03_colab.ipynb",
    "srl_ner_sirah_S3_1_scl_lambda03_kaggle.ipynb",
]


def make_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def patch_notebook(path: Path) -> str:
    if not path.exists():
        return "missing"
    nb = json.loads(path.read_text(encoding="utf-8"))

    # Step 1: check if helper cell already injected
    helper_exists = False
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        if "[PATCH] Auto-detect iterasi terakhir" in src:
            helper_exists = True
            break

    # Step 2: find first cell that uses iteration-6, inject helper before it
    # (only if helper not yet exists)
    n_replaced = 0
    inject_idx = None
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        if "iteration-6" in src or "iterative-6" in src:
            if inject_idx is None and not helper_exists:
                inject_idx = i

    if inject_idx is not None:
        nb["cells"].insert(inject_idx, make_code_cell(LAST_ITER_HELPER_CELL))

    # Step 3: apply replacements
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        original = src
        for old, new in REPLACEMENTS:
            if old in src:
                src = src.replace(old, new)
                n_replaced += 1
        if src != original:
            c["source"] = src.splitlines(keepends=True)

    if n_replaced or inject_idx is not None:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return f"patched (helper={'+' if inject_idx is not None else 'exist'}, replacements={n_replaced})"
    return "no_change"


def main():
    for name in NOTEBOOKS:
        result = patch_notebook(HERE / name)
        print(f"  {name:<55} {result}")


if __name__ == "__main__":
    main()
