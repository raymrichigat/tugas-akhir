#!/usr/bin/env python3
"""
run_eval_done_running.py — hitung F1 entity-level (seqeval) untuk SEMUA skenario yang
tersimpan di `done_running` (Grup A + Grup B), pakai test.csv yang sama → tabel adil.

Menutup gap: `evaluate_seqeval.py --all` punya daftar path lama dan belum ada Grup B.
Script ini auto-detect iterasi terakhir (yang ada model.safetensors) per skenario.

Output: data/result/pseudo-labelling/SRL-NER/seqeval_grupB_results.md (TIDAK menimpa
seqeval_results.md lama). No-GPU.

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\run_eval_done_running.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from evaluate_seqeval import evaluate_model  # noqa: E402

ROOT = HERE.parents[2]
DONE = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "done_running"
TEST_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
OUT_MD = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "seqeval_grupB_results.md"

# tag -> folder output skenario (di dalamnya ada models/<iterasi>)
SCENARIOS = {
    "S1-baseline (indolem uncased)": DONE / "baseline" / "output_S1_baseline",
    "S2-weighted-CE": DONE / "weighted-class" / "drive-download-20260611T025134Z-3-001" / "output_S2_weighted_ce",
    "S2a-SCL": DONE / "scl" / "output_S2a_scl",
    "S2b-JSCL": DONE / "jscl" / "output_S2b_jscl",
    "S4-augmentation": DONE / "augmentation" / "output_S4_augmentation",
    "GrupB-indobert-cased": DONE / "indobert-base-p1" / "output_GrupB_cased",
    "GrupB-cahya-bert-1.5G": DONE / "cahya-bert-base" / "output_GrupB_cahya",
    "GrupB-distilbert": DONE / "distilbert" / "output_GrupB_distilbert",
    "GrupB-roberta": DONE / "roberta" / "output_GrupB_roberta",
}


def has_weights(d: Path) -> bool:
    return d.is_dir() and any((d / fn).exists() for fn in ("model.safetensors", "pytorch_model.bin"))


def pick_last_model(output_dir: Path) -> Path | None:
    """Pilih model dgn nomor iterasi tertinggi yang punya weights; fallback ke -base."""
    models = output_dir / "models"
    if not models.is_dir():
        return None
    best_iter, best_path, base_path = -1, None, None
    for d in models.iterdir():
        if not has_weights(d):
            continue
        m = re.search(r"iteration-(\d+)$", d.name)
        if m:
            n = int(m.group(1))
            if n > best_iter:
                best_iter, best_path = n, d
        elif d.name.endswith("base"):
            base_path = d
    return best_path or base_path


def parse_class_f1(report: str, cls: str) -> str:
    for line in report.splitlines():
        parts = line.split()
        if parts and parts[0] == cls and len(parts) >= 4:
            return parts[3]  # precision recall f1 support -> f1 di indeks 3
    return "-"


def main() -> None:
    df = pd.read_csv(TEST_CSV)
    df["token"] = df["token"].astype(str)
    df["label"] = df["label"].astype(str)
    print(f"[OK] test.csv {len(df)} baris, {df['text_id'].nunique()} chunk")

    results = []
    for tag, out_dir in SCENARIOS.items():
        mp = pick_last_model(out_dir)
        if mp is None:
            print(f"[SKIP] {tag}: tidak ada model berweights di {out_dir}")
            continue
        print(f"\n=== {tag} -> {mp.name} ===")
        try:
            r = evaluate_model(mp, df, tag)
            r["model_used"] = mp.name
            results.append(r)
        except Exception as e:  # noqa: BLE001
            print(f"[ERR] {tag}: {e}")

    # tulis markdown ringkas
    lines = ["# Seqeval Grup A + Grup B (done_running)\n",
             "> Dihasilkan `run_eval_done_running.py`. Entity-level seqeval, test.csv sama untuk semua.\n",
             "\n## Ringkasan\n",
             "| Skenario | model | F1 | Precision | Recall | F1 EVENT | F1 TIME |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for r in results:
        lines.append(
            f"| {r['tag']} | {r['model_used']} | {r['f1']:.4f} | {r['precision']:.4f} | "
            f"{r['recall']:.4f} | {parse_class_f1(r['report'],'EVENT')} | {parse_class_f1(r['report'],'TIME')} |"
        )
    lines.append("\n## Per-kelas lengkap\n")
    for r in results:
        lines.append(f"### {r['tag']} ({r['model_used']})\n```\n{r['report'].rstrip()}\n```\n")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] hasil -> {OUT_MD}")
    print("\n".join(lines[3:6 + len(results)]))


if __name__ == "__main__":
    main()
