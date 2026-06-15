#!/usr/bin/env python3
"""
build_class_weights.py — (re)generate bobot kelas untuk skenario **S2 Weighted Cross-Entropy**
(revisi Bu Diana 2026-06-05, lihat docs/skenario/skenario_baru_2026-06.md).

Sumber : data/result/pseudo-labelling/SRL-NER/train.csv  (gold dikoreksi; kolom `label` BIO dash)
Output : data/result/pseudo-labelling/SRL-NER/class_weights.json

Script ini MEREPRODUKSI persis `class_weights.json` yang sudah ada (skema label_order /
token_counts / balanced_raw / sqrt_tempered_norm_O1) — tujuannya mendokumentasikan cara
angkanya dihitung + idempotent (re-run = byte sama, tidak ada churn git).

Dua varian bobot (token-level):
  - balanced_raw          : N / (K * count[c]). EKSTREM (riwayat: precision kolaps run legacy 2026-05-07).
  - sqrt_tempered_norm_O1 : sqrt(balanced_raw) dinormalisasi O=1.0. **REKOMENDASI**.

Key JSON = format DASH (B-EVENT). Di notebook id2label underscore (B_EVENT) → konversi saat lookup.

No-GPU, stdlib only. Jalankan:
    venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_class_weights.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

# urutan entity di label_order (mengikuti file canonical yang sudah ada)
ENTITY_ORDER = ["PERSON", "LOCATION", "EVENT", "TIME"]
NOTE = (
    "Rekomendasi pakai sqrt_tempered_norm_O1 (balanced mentah terlalu ekstrem -> "
    "precision kolaps spt legacy 2026-05-07)."
)


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def build_label_order(present: set[str]) -> list[str]:
    order = ["O"]
    for t in ENTITY_ORDER:
        for p in ("B", "I"):
            lab = f"{p}-{t}"
            if lab in present:
                order.append(lab)
    # label asing (kalau ada) ditempel di belakang biar tidak hilang
    order += [c for c in sorted(present) if c not in order]
    return order


def compute(train_csv: Path) -> dict:
    counts: Counter[str] = Counter()
    with train_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "label" not in reader.fieldnames:
            raise SystemExit(
                f"[err] kolom 'label' tidak ada di {train_csv} (kolom: {reader.fieldnames})"
            )
        for row in reader:
            lab = (row.get("label") or "").strip() or "O"
            counts[lab] += 1

    label_order = build_label_order(set(counts))
    total = sum(counts.values())
    k = len(label_order)

    balanced_raw = {c: round(total / (k * counts[c]), 3) for c in label_order}
    sqrt_full = {c: math.sqrt(total / (k * counts[c])) for c in label_order}
    o_ref = sqrt_full.get("O", 1.0) or 1.0
    sqrt_norm = {c: round(sqrt_full[c] / o_ref, 3) for c in label_order}

    return {
        "label_order": label_order,
        "token_counts": {c: counts[c] for c in label_order},
        "balanced_raw": balanced_raw,
        "sqrt_tempered_norm_O1": sqrt_norm,
        "note": NOTE,
    }


def main() -> None:
    repo = find_repo_root(Path(__file__))
    ap = argparse.ArgumentParser(description="(Re)generate class_weights.json untuk S2 Weighted-CE.")
    ap.add_argument("--train", type=Path,
                    default=repo / "data/result/pseudo-labelling/SRL-NER/train.csv")
    ap.add_argument("--out", type=Path,
                    default=repo / "data/result/pseudo-labelling/SRL-NER/class_weights.json")
    args = ap.parse_args()

    if not args.train.exists():
        raise SystemExit(f"[err] train tidak ditemukan: {args.train}")

    result = compute(args.train)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[ok] {args.out.relative_to(repo)}  ({args.out.stat().st_size} bytes)")
    total = sum(result["token_counts"].values())
    print(f"     total token = {total:,} | {len(result['label_order'])} kelas")
    print(f"     {'label':<12}{'count':>8}{'balanced':>10}{'sqrt_O1':>9}")
    for c in result["label_order"]:
        print(
            f"     {c:<12}{result['token_counts'][c]:>8,}"
            f"{result['balanced_raw'][c]:>10.3f}{result['sqrt_tempered_norm_O1'][c]:>9.3f}"
        )


if __name__ == "__main__":
    main()
