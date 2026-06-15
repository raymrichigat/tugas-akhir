#!/usr/bin/env python3
"""
add_runtime_timer.py — bungkus sel training tiap notebook skenario dengan timer wall-clock.

Menambah pengukuran **waktu latih per skenario** (untuk perbandingan Bab 4, bukan cuma F1).
Timer membungkus sel self-training (`for i in range(1, N_ITERATIONS ...)`) → mencakup bootstrap
+ semua iterasi self-training + inference antar-iterasi (= total compute skenario). Hasilnya
di-print `[RUNTIME] ...` + disimpan ke `runtime_skenario.txt` di `eval_dir` masing-masing.

Idempotent (skip kalau timer sudah ada). Re-runnable kalau notebook dibangun ulang.
No-GPU. Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\add_runtime_timer.py
"""
from __future__ import annotations
import json
from pathlib import Path

NOTEBOOKS = [
    "srl_ner_sirah_0.9_colab.ipynb",            # S1 baseline
    "srl_ner_sirah_S2_weighted_ce_colab.ipynb", # S2 weighted-CE
    "srl_ner_sirah_S2a_scl_colab.ipynb",        # S3a SCL
    "srl_ner_sirah_S2b_jscl_colab.ipynb",       # S3b JSCL
    "srl_ner_sirah_S4_augmentation_colab.ipynb",# S4 augmentasi gabungan
    "srl_ner_sirah_S3_2_scl_aug_colab.ipynb",   # ref: SCL+Aug combined
    "srl_ner_sirah_GrupB_cahya_colab.ipynb",    # Grup B cahya
    "srl_ner_sirah_GrupB_distilbert_colab.ipynb",  # Grup B distilbert
]
ANCHOR = "for i in range(1, N_ITERATIONS"
START = "import time as _t; _RT0 = _t.time()  # [runtime timer start]\n"
END = [
    "\n",
    "# === [runtime timer] total blok training (download model pertama + semua iterasi self-training) ===\n",
    "_RT = _t.time() - _RT0\n",
    "print('[RUNTIME] skenario ini: %.2f menit (%.0f detik)' % (_RT/60, _RT))\n",
    "try:\n",
    "    with open(os.path.join(eval_dir, 'runtime_skenario.txt'), 'w') as _f:\n",
    "        _f.write('runtime_detik=%.0f menit=%.2f' % (_RT, _RT/60))\n",
    "    print('  runtime tersimpan ->', os.path.join(eval_dir, 'runtime_skenario.txt'))\n",
    "except Exception as _e:\n",
    "    print('  (gagal simpan runtime:', _e, ')')\n",
]


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def main() -> None:
    repo = find_repo_root(Path(__file__))
    nbdir = repo / "src/pseudo_labelling/SRL-NER"
    for name in NOTEBOOKS:
        p = nbdir / name
        if not p.exists():
            print("SKIP (tak ada):", name)
            continue
        nb = json.loads(p.read_text(encoding="utf-8"))
        status = "ANCHOR tak ketemu"
        for c in nb["cells"]:
            if c.get("cell_type") != "code":
                continue
            joined = "".join(c.get("source", []))
            if ANCHOR in joined:
                if "_RT0 = _t.time()" in joined:
                    status = "sudah ada timer"
                else:
                    c["source"] = [START] + c["source"] + END
                    p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
                    status = "+timer ditambah"
                break
        print(f"  {status:<18} {name}")


if __name__ == "__main__":
    main()
