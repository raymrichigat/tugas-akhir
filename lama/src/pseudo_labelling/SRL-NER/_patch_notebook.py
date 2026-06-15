"""One-shot patcher: adapt the reference BERT notebook to Sirah NER."""
import json, re
from pathlib import Path

P = Path(__file__).parent / "bert_ner_sirah_0.9.ipynb"
nb = json.loads(P.read_text(encoding="utf-8"))

ROOT = r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah"
DATASET = ROOT + r"\data\result\pseudo-labelling\SRL-NER"
BERT_OUT = ROOT + r"\data\result\pseudo-labelling\BERT-NER"
MODEL = BERT_OUT + r"\models"
EVAL = BERT_OUT + r"\evaluation"

PATH_BLOCK = f"""_name = 'bert-only'
_type = 'sirah-ner'
experiment_name = f'{{_name}}-{{_type}}'

import os
root_dir    = r"{ROOT}"
dataset_dir = r"{DATASET}"
model_dir   = r"{MODEL}"
eval_dir    = r"{EVAL}"
os.makedirs(model_dir, exist_ok=True)
os.makedirs(eval_dir,  exist_ok=True)

df_train = pd.read_csv(os.path.join(dataset_dir, 'train.csv'))
df_train["token"] = df_train["token"].apply(str)
df_train["label"] = df_train["label"].apply(lambda x: x.replace("-", "_"))
df_train.loc[df_train[df_train.isna().any(axis=1)].index, 'token'] = 'nan'
"""

def repl(s: str) -> str:
    s = s.replace("bert-only-argumen-o.8", "bert-only-sirah-ner")
    s = s.replace("bert-only-argument", "bert-only-sirah-ner")
    s = s.replace("bert-only-argumen", "bert-only-sirah-ner")
    s = s.replace("train-35.csv", "train.csv")
    s = s.replace("unlabelled-65.csv", "unlabelled.csv")
    # rename label column: argument -> label  (also catches predicted_argument)
    s = s.replace("predicted_argument", "predicted_label")
    s = s.replace("os.path.join(root_dir, 'evaluation', experiment_name)", "eval_dir")
    s = s.replace('os.path.join(root_dir, "evaluation", experiment_name, ', 'os.path.join(eval_dir, ')
    s = s.replace('output_dir="./result"', 'output_dir=os.path.join(model_dir, "_trainer_tmp")')
    s = re.sub(r"\bargument\b", "label", s)
    return s

changed = []
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    new = src
    if "_type =" in src and "root_dir" in src:
        new = PATH_BLOCK
    elif "os.listdir('D:" in src or 'os.listdir("D:' in src:
        new = "os.listdir(dataset_dir)\n"
    elif "os.getcwd" in src and "D:" in src:
        new = "import os\nos.getcwd()\n"
    else:
        new = repl(src)
    if new != src:
        cell["source"] = new.splitlines(keepends=True)
        changed.append(i)
    if cell.get("cell_type") == "code":
        cell["outputs"] = []
        cell["execution_count"] = None

P.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("changed cells:", changed)
print("total cells:", len(nb["cells"]))
