#!/usr/bin/env python3
"""
fix_eval_last_iteration.py — perbaiki sel evaluasi notebook turunan S1 yang HARDCODE
`iteration-6`. Self-training bisa konvergen sebelum iter-6 → folder model itu tak ada →
HFValidationError ("Repo id must be in the form ..."). Notebook contrastive sudah punya
auto-detect `_find_last_iteration`; script ini menyalin blok itu ke notebook S1-derived
dan mengganti path hardcoded jadi LAST_MODEL_PATH.

Idempotent. Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\fix_eval_last_iteration.py
"""
from __future__ import annotations
import json
from pathlib import Path

SRC_ROBUST = "srl_ner_sirah_S2a_scl_colab.ipynb"   # sumber blok _find_last_iteration
TARGETS = [
    "srl_ner_sirah_0.9_colab.ipynb",
    "srl_ner_sirah_S2_weighted_ce_colab.ipynb",
    "srl_ner_sirah_S4_augmentation_colab.ipynb",
    "srl_ner_sirah_GrupB_cahya_colab.ipynb",
    "srl_ner_sirah_GrupB_distilbert_colab.ipynb",
]
OLD = 'os.path.join(model_dir ,f"{experiment_name}-0.9-iteration-6")'


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def main() -> None:
    repo = find_repo_root(Path(__file__))
    nbdir = repo / "src/pseudo_labelling/SRL-NER"

    s2a = json.loads((nbdir / SRC_ROBUST).read_text(encoding="utf-8"))
    robust = next((c["source"] for c in s2a["cells"]
                   if c.get("cell_type") == "code" and "_find_last_iteration" in "".join(c.get("source", []))), None)
    if robust is None:
        raise SystemExit("[err] blok _find_last_iteration tak ditemukan di " + SRC_ROBUST)

    for name in TARGETS:
        p = nbdir / name
        if not p.exists():
            print("  SKIP (tak ada):", name); continue
        nb = json.loads(p.read_text(encoding="utf-8"))
        full = "".join("".join(c.get("source", [])) for c in nb["cells"])
        if "_find_last_iteration" in full:
            print("  sudah ada fix:", name); continue
        eval_idx = next((i for i, c in enumerate(nb["cells"])
                         if c.get("cell_type") == "code" and "0.9-iteration-6" in "".join(c.get("source", []))), None)
        if eval_idx is None:
            print("  sel eval tak ketemu:", name); continue
        # ganti path hardcoded -> LAST_MODEL_PATH
        nb["cells"][eval_idx]["source"] = [l.replace(OLD, "LAST_MODEL_PATH")
                                           for l in nb["cells"][eval_idx]["source"]]
        # sisipkan blok robust SEBELUM sel eval
        nb["cells"].insert(eval_idx, {"cell_type": "code", "metadata": {},
                                      "execution_count": None, "outputs": [], "source": list(robust)})
        p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print("  [FIXED]:", name)


if __name__ == "__main__":
    main()
