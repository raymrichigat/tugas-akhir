"""
patch_contrastive_trainer.py
============================
One-off patch script untuk fix bug di compute_loss `ContrastiveTrainer`.

Bug: `return (loss, outputs) if return_outputs else loss` — outputs adalah
ModelOutput penuh dengan hidden_states (karena output_hidden_states=True).
Saat Trainer downstream call evaluation, dia extract `pred.predictions` jadi
tuple (logits, hidden_states_tuple). numpy 2.x raise `inhomogeneous shape`
di `np.argmax(pred.predictions, axis=2)` di compute_metrics.

Fix: kembali ke pattern success notebook (`done_running/.../srl_ner_sirah_S2a_scl_colab_new.ipynb`):
    if return_outputs:
        return loss, {"logits": logits}
    return loss

Affected notebooks:
  - srl_ner_sirah_S2a_scl{,_colab,_kaggle}.ipynb  (source — untuk future rebuild compat)
  - srl_ner_sirah_S2b_jscl{,_colab,_kaggle}.ipynb (source)
  - srl_ner_sirah_S3_1_scl_lambda0{1,2,3}{,_colab,_kaggle}.ipynb  (target untuk run S3.1)

Idempotent. Usage:
  python patch_contrastive_trainer.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

OLD_PATTERN = "        return (loss, outputs) if return_outputs else loss"
NEW_PATTERN = """        # FIX: return only logits dict, jangan ModelOutput penuh.
        # ModelOutput membawa hidden_states (output_hidden_states=True),
        # menyebabkan pred.predictions jadi tuple di Trainer evaluate
        # → np.argmax error di numpy 2.x. Match pattern success S2a run.
        if return_outputs:
            return loss, {"logits": logits}
        return loss"""

NOTEBOOKS = [
    # Source S2 notebooks (untuk future rebuild S3 dari sini)
    "srl_ner_sirah_S2a_scl.ipynb",
    "srl_ner_sirah_S2a_scl_colab.ipynb",
    "srl_ner_sirah_S2a_scl_kaggle.ipynb",
    "srl_ner_sirah_S2b_jscl.ipynb",
    "srl_ner_sirah_S2b_jscl_colab.ipynb",
    "srl_ner_sirah_S2b_jscl_kaggle.ipynb",
    # S3.1 notebooks (target run aktif)
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


def patch_notebook(path: Path) -> str:
    """Returns 'patched', 'already_fixed', 'not_found', or 'missing'."""
    if not path.exists():
        return "missing"
    nb = json.loads(path.read_text(encoding="utf-8"))
    n_patched = 0
    n_already = 0
    for cell in nb.get("cells", []):
        if cell["cell_type"] != "code":
            continue
        src = cell["source"]
        if isinstance(src, list):
            text = "".join(src)
        else:
            text = src
        if "class ContrastiveTrainer" not in text:
            continue
        if "return loss, {\"logits\": logits}" in text and OLD_PATTERN not in text:
            n_already += 1
            continue
        if OLD_PATTERN in text:
            new_text = text.replace(OLD_PATTERN, NEW_PATTERN)
            cell["source"] = new_text.splitlines(keepends=True)
            n_patched += 1
    if n_patched:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return f"patched ({n_patched} cell)"
    if n_already:
        return "already_fixed"
    return "not_found"


def main():
    for name in NOTEBOOKS:
        result = patch_notebook(HERE / name)
        print(f"  {name:<50} {result}")


if __name__ == "__main__":
    main()
