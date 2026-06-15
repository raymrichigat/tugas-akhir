#!/usr/bin/env python3
"""
build_grup_b_backbones.py — siapkan notebook turnkey untuk skenario revisi 5 Juni.

(a) Bangun 2 notebook **Grup B — perbandingan backbone** sebagai turunan S1 baseline:
      - cahya/bert-base-indonesian-1.5G   (uncased)
      - cahya/distilbert-base-indonesian  (uncased)
    Basis = S1 baseline (config sama, HANYA backbone yang beda → isolasi efek backbone bersih).
    Catatan: baseline aktual = indolem/indobert-base-uncased (juga uncased) → lihat
    project_baseline_model_uncased; untuk uji "kapital berpengaruh?" tambah model CASED terpisah.

(b) Isolasi folder output Drive untuk carry-over S1/S3/S4 supaya tidak saling menimpa
    saat dijalankan berurutan (S2 weighted-CE sudah diisolasi sebelumnya).

Output Drive per notebook (extract bundle ke /content/drive/MyDrive/TA-Sirah):
  S1 baseline      -> output_S1_baseline
  S2 weighted-CE   -> output_S2_weighted_ce   (sudah)
  S3 contrastive   -> output_S3_contrastive
  S4 augmentation  -> output_S4_augmentation
  GrupB cahya      -> output_GrupB_cahya
  GrupB distilbert -> output_GrupB_distilbert

No-GPU. Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_grup_b_backbones.py
"""
from __future__ import annotations

import json
from pathlib import Path

BASE_MODEL = "indolem/indobert-base-uncased"
OUT_DRIVE = "/content/drive/MyDrive/TA-Sirah/output'"
S1_TITLE = "# BERT Percobaan 1 (35% train and 65% unlabelled)"


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def save(nb: dict, p: Path) -> None:
    p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


def replace_in_cells(nb: dict, repls: list[tuple[str, str]]) -> dict[str, int]:
    counts = {old: 0 for old, _ in repls}
    for c in nb["cells"]:
        new = []
        for line in c.get("source", []):
            for old, rep in repls:
                if old in line:
                    line = line.replace(old, rep)
                    counts[old] += 1
            new.append(line)
        c["source"] = new
    return counts


def strip_outputs(nb: dict) -> None:
    for c in nb["cells"]:
        if c.get("cell_type") == "code":
            c["outputs"] = []
            c["execution_count"] = None


def main() -> None:
    repo = find_repo_root(Path(__file__))
    nbdir = repo / "src/pseudo_labelling/SRL-NER"
    s1 = nbdir / "srl_ner_sirah_0.9_colab.ipynb"
    if not s1.exists():
        raise SystemExit(f"[err] S1 baseline tidak ada: {s1}")

    # ---- (a) Grup B ----
    backbones = [
        ("cahya/bert-base-indonesian-1.5G", "GrupB_cahya",
         "# Grup B — cahya/bert-base-indonesian-1.5G (uncased), turunan S1 baseline"),
        ("cahya/distilbert-base-indonesian", "GrupB_distilbert",
         "# Grup B — cahya/distilbert-base-indonesian (uncased), turunan S1 baseline"),
    ]
    for model, tag, title in backbones:
        nb = load(s1)
        strip_outputs(nb)
        c = replace_in_cells(nb, [
            (BASE_MODEL, model),
            (OUT_DRIVE, f"/content/drive/MyDrive/TA-Sirah/output_{tag}'"),
            (S1_TITLE, title),
        ])
        out = nbdir / f"srl_ner_sirah_{tag}_colab.ipynb"
        save(nb, out)
        print(f"[Grup B] {out.name}: model_swap={c[BASE_MODEL]} output_iso={c[OUT_DRIVE]} title={c[S1_TITLE]}")

    # ---- (b) isolasi output carry-over ----
    isolate = {
        "srl_ner_sirah_0.9_colab.ipynb": "output_S1_baseline",
        "srl_ner_sirah_S2a_scl_colab.ipynb": "output_S3_contrastive",
        "srl_ner_sirah_S3_2_scl_aug_colab.ipynb": "output_S4_augmentation",
    }
    for fname, folder in isolate.items():
        p = nbdir / fname
        if not p.exists():
            print(f"[isolasi] SKIP (tak ada): {fname}")
            continue
        nb = load(p)  # JANGAN strip outputs carry-over (rekaman eksperimen dipertahankan)
        c = replace_in_cells(nb, [(OUT_DRIVE, f"/content/drive/MyDrive/TA-Sirah/{folder}'")])
        save(nb, p)
        print(f"[isolasi] {fname} -> {folder}  (replaced={c[OUT_DRIVE]})")


if __name__ == "__main__":
    main()
