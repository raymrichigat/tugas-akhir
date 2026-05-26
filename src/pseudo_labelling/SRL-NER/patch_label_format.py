"""
patch_label_format.py
=====================
Fix bug label format conversion di evaluation cells. Notebook S3.1 (dan beberapa
S2 awal) pakai `replace("-", "_")` yang convert label dari format BIO standard
`B-PERSON` → `B_PERSON`. Tapi seqeval cuma kenal format dash → trigger warning
"B_PERSON seems not to be NE tag" dan seqeval F1 di final eval jadi bogus.

Success notebook (`done_running/.../srl_ner_sirah_S2a_scl_colab_new.ipynb`)
pakai direction kebalikan: `replace("_", "-")` (underscore → dash). Itu yang
benar — convert dari format internal model (yang pakai underscore) kembali ke
format seqeval (dash).

Bug ini ada di notebook awal `srl_ner_sirah_S2a_scl_colab.ipynb` (di root folder)
yang aku pakai sebagai base saat build S3.1. Patch fix ke direction yang benar.

**Affected notebooks:**
  - srl_ner_sirah_S2a_scl{,_colab,_kaggle}.ipynb
  - srl_ner_sirah_S2b_jscl{,_colab,_kaggle}.ipynb
  - srl_ner_sirah_S3_1_scl_lambda0{1,2,3}{,_colab,_kaggle}.ipynb

Idempotent. Usage:
  python patch_label_format.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

# Match all 4 occurrences (cell 11/23/29/34 in success, 11/30/35 + tmp_df in mine)
REPLACEMENTS = [
    ('df_train["label"].apply(lambda x: x.replace("-", "_"))',
     'df_train["label"].apply(lambda x: x.replace("_", "-"))'),
    ('df_test["label"].apply(lambda x: x.replace("-", "_"))',
     'df_test["label"].apply(lambda x: x.replace("_", "-"))'),
    ('df_test_base["label"].apply(lambda x: x.replace("-", "_"))',
     'df_test_base["label"].apply(lambda x: x.replace("_", "-"))'),
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
        return f"patched ({n_replaced} occurrences)"
    return "no_change_or_already_fixed"


def main():
    for name in NOTEBOOKS:
        result = patch_notebook(HERE / name)
        print(f"  {name:<55} {result}")


if __name__ == "__main__":
    main()
