#!/usr/bin/env python3
"""
build_S2_weighted_ce.py — bangun notebook **S2 Weighted Cross-Entropy** sebagai turunan
notebook S1 baseline (revisi Bu Diana 2026-06-05). Reproducible: kalau S1 berubah, rebuild.

Satu-satunya perubahan metodologis vs S1: `Trainer` -> `WeightedLossTrainer`
(CrossEntropyLoss berbobot per-kelas dari class_weights.json). Pipeline lain identik
→ perbandingan terkontrol (head-to-head dengan CL & Augmentation).

Sumber : done_running/S1_baseline/notebook/srl_ner_sirah_0_9_colab.ipynb
Output : src/pseudo_labelling/SRL-NER/srl_ner_sirah_S2_weighted_ce_colab.ipynb

Catatan: notebook baseline pakai `indolem/indobert-base-uncased` (BUKAN indobenchmark) dan
label di-convert underscore (B_EVENT) → class_weights.json di-key dash (B-EVENT), dikonversi
saat lookup. Model TIDAK diubah (orthogonal terhadap weighted-CE).

No-GPU. Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_S2_weighted_ce.py
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


NEW_MD = [
    "## S2 — Weighted Cross-Entropy\n",
    "\n",
    "Turunan **S1 baseline** (lihat `build_S2_weighted_ce.py`). Satu-satunya perubahan:\n",
    "`Trainer` diganti `WeightedLossTrainer` — loss CrossEntropy berbobot per-kelas.\n",
    "Bobot dari `class_weights.json` varian `sqrt_tempered_norm_O1` (hasil `build_class_weights.py`).\n",
    "\n",
    "> **Wajib:** upload `class_weights.json` ke `dataset_dir` di Drive (bareng train/test/unlabelled).\n",
    "> Output di-isolasi ke folder `output_S2_weighted_ce` supaya tidak menimpa hasil S1.\n",
]

NEW_CODE = [
    "# === S2: bobot kelas + WeightedLossTrainer ===\n",
    "import json, torch\n",
    "\n",
    "_cw_path = os.path.join(dataset_dir, 'class_weights.json')\n",
    "_cw = json.load(open(_cw_path, encoding='utf-8'))['sqrt_tempered_norm_O1']\n",
    "\n",
    "def _to_dash(u):  # id2label notebook = underscore (B_EVENT); key JSON = dash (B-EVENT)\n",
    "    return u.replace('_', '-', 1) if u[:2] in ('B_', 'I_') else u\n",
    "\n",
    "CLASS_WEIGHTS = torch.tensor(\n",
    "    [_cw[_to_dash(id2label[i])] for i in range(len(id2label))], dtype=torch.float)\n",
    "print('[weighted-CE] bobot per-kelas:',\n",
    "      {id2label[i]: round(CLASS_WEIGHTS[i].item(), 2) for i in range(len(id2label))})\n",
    "\n",
    "class WeightedLossTrainer(Trainer):\n",
    "    \"\"\"Trainer dengan CrossEntropy berbobot per-kelas (sisanya identik Trainer biasa).\"\"\"\n",
    "    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):\n",
    "        labels = inputs.pop('labels')\n",
    "        outputs = model(**inputs)\n",
    "        loss_fct = torch.nn.CrossEntropyLoss(\n",
    "            weight=CLASS_WEIGHTS.to(outputs.logits.device), ignore_index=-100)\n",
    "        loss = loss_fct(outputs.logits.view(-1, model.config.num_labels), labels.view(-1))\n",
    "        return (loss, outputs) if return_outputs else loss\n",
    "# Tip: kalau precision turun tajam, kecilkan bobot (akar lagi: w**0.5) atau cap min(w, 10).\n",
]


def main() -> None:
    repo = find_repo_root(Path(__file__))
    src_nb = repo / "src/pseudo_labelling/SRL-NER/done_running/S1_baseline/notebook/srl_ner_sirah_0_9_colab.ipynb"
    out_nb = repo / "src/pseudo_labelling/SRL-NER/srl_ner_sirah_S2_weighted_ce_colab.ipynb"

    if not src_nb.exists():
        raise SystemExit(f"[err] notebook S1 tidak ditemukan: {src_nb}")

    nb = json.loads(src_nb.read_text(encoding="utf-8"))
    cells = nb["cells"]

    n_title = n_root = n_filelist = n_trainer = 0
    train_cell_idx = None

    for idx, cell in enumerate(cells):
        # bersihkan output + execution_count
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

        src = cell.get("source", [])
        new_src = []
        for line in src:
            if "BERT Percobaan 1" in line:
                line = line.replace(
                    "# BERT Percobaan 1 (35% train and 65% unlabelled)",
                    "# S2 — Weighted Cross-Entropy (turunan S1, 35% train + 65% unlabelled)",
                )
                n_title += 1
            if "root_dir    = '/content/drive/MyDrive/TA-Sirah/output'" in line:
                line = line.replace(
                    "/content/drive/MyDrive/TA-Sirah/output'",
                    "/content/drive/MyDrive/TA-Sirah/output_S2_weighted_ce'",
                )
                n_root += 1
            if "for f in ['train.csv', 'test.csv', 'unlabelled.csv']:" in line:
                line = line.replace(
                    "['train.csv', 'test.csv', 'unlabelled.csv']",
                    "['train.csv', 'test.csv', 'unlabelled.csv', 'class_weights.json']",
                )
                n_filelist += 1
            if "trainer = Trainer(" in line:
                line = line.replace("trainer = Trainer(", "trainer = WeightedLossTrainer(")
                n_trainer += 1
                train_cell_idx = idx
            new_src.append(line)
        cell["source"] = new_src

    if train_cell_idx is None:
        raise SystemExit("[err] sel 'trainer = Trainer(' tidak ditemukan — struktur notebook berubah?")

    # sisipkan markdown + code (definisi WeightedLossTrainer) tepat sebelum sel train_model
    md_cell = {"cell_type": "markdown", "metadata": {}, "source": NEW_MD}
    code_cell = {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": NEW_CODE,
    }
    cells.insert(train_cell_idx, code_cell)
    cells.insert(train_cell_idx, md_cell)

    out_nb.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[ok] {out_nb.relative_to(repo)}")
    print(f"     patch: title={n_title} root_dir={n_root} filelist={n_filelist} trainer={n_trainer}")
    print(f"     sel WeightedLossTrainer disisipkan sebelum index {train_cell_idx} (sel train_model)")
    print("     total cells:", len(cells))


if __name__ == "__main__":
    main()
