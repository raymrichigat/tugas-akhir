"""
revert_label_format.py
======================
Revert patch label format dari `replace("_", "-")` kembali ke `replace("-", "_")`.

**Alasan revert:**
Patch `replace("_", "-")` memang fix seqeval warning di final evaluation cell,
TAPI bikin bug baru:
  - filter_threshold pakai `_BIO_SCHEME = any(lab.startswith(("B_", "I_")) ...)`
  - Setelah patch, label format jadi dash (`B-PERSON`) → BIO_SCHEME=False
  - filter_threshold masuk ke "flat scheme" branch → return label tanpa prefix
    (e.g. "PERSON" instead of "B_PERSON"/"B-PERSON")
  - Pseudo-label `PERSON` di-concat ke df_train, lalu di-map dengan label2id
  - label2id cuma punya `B-PERSON`/`I-PERSON`/`O` → KeyError: 'PERSON'

**Trade-off:**
Format underscore (B_PERSON) di label2id:
  ✓ filter_threshold + extract_entities_from_result work correctly
  ✓ Training pipeline + token-level F1 valid
  ✓ seq F1 per-iter di iteration_log (compute_metrics) tetap valid karena
    pakai id2label yang format underscore
  ✗ seqeval F1 DI FINAL EVAL CELL bogus (warning "B_PERSON not NE tag")

Cara fix yang minimal-invasive: revert format ke underscore (lambda01 run
sebelumnya sudah validated end-to-end dengan format ini, token F1=0.9954).
Kalau perlu seq F1 final eval valid → tambah convert step di evaluation cell
saja (bukan di seluruh pipeline).

Idempotent. Usage:
  python revert_label_format.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

REPLACEMENTS = [
    ('df_train["label"].apply(lambda x: x.replace("_", "-"))',
     'df_train["label"].apply(lambda x: x.replace("-", "_"))'),
    ('df_test["label"].apply(lambda x: x.replace("_", "-"))',
     'df_test["label"].apply(lambda x: x.replace("-", "_"))'),
    ('df_test_base["label"].apply(lambda x: x.replace("_", "-"))',
     'df_test_base["label"].apply(lambda x: x.replace("-", "_"))'),
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


def patch_notebook(path: Path) -> str:
    if not path.exists():
        return "missing"
    nb = json.loads(path.read_text(encoding="utf-8"))
    n_replaced = 0
    for c in nb.get("cells", []):
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
    if n_replaced:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return f"reverted ({n_replaced} occurrences)"
    return "no_change_needed"


def main():
    for name in NOTEBOOKS:
        result = patch_notebook(HERE / name)
        print(f"  {name:<55} {result}")


if __name__ == "__main__":
    main()
