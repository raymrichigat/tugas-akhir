"""
Idempotent: ubah notebook SRL-NER S2/S3 yang masih hardcode underscore BIO
(`B_PERSON`, `I_PERSON`) jadi dash (`B-PERSON`, `I-PERSON`) supaya seqeval
ngerti format-nya.

3 jenis perubahan per notebook:
  1. `replace("-", "_")` di CSV load → `replace("_", "-")` (flip arah)
  2. `startswith(("B_", "I_"))` di _BIO_SCHEME + extract_entities → `("B-", "I-")`
  3. f-string `f"B_{group}"`, `f"I_{group}"` → `f"B-{group}"`, `f"I-{group}"`

Jalankan: `python src\pseudo_labelling\SRL-NER\_fix_underscore_to_dash.py`
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NOTEBOOKS = [
    "src\pseudo_labelling\SRL-NER\srl_ner_sirah_S3a_scl_aug_colab.ipynb",
    "src\pseudo_labelling\SRL-NER\srl_ner_sirah_S3b_jscl_aug_colab.ipynb",
]

# Pattern (src) → (dst). Diaplikasikan ke tiap baris source cell.
REPLACEMENTS = [
    # 1. flip arah konversi label saat CSV load
    ('replace("-", "_")', 'replace("_", "-")'),
    # 2. underscore BIO prefix di startswith()
    ('startswith(("B_", "I_"))', 'startswith(("B-", "I-"))'),
    # 3. f-string underscore di extract_entities_from_result
    ('f"B_{group}"', 'f"B-{group}"'),
    ('f"I_{group}"', 'f"I-{group}"'),
]

# Defensive injection: tambah label normalization PERSIS sebelum `return tmp_df`
# di blok cache-hit `filter_threshold`, supaya kalau ada cache CSV underscore
# dari run lama, otomatis di-convert ke dash.
INJECT_BEFORE_RETURN = 'tmp_df["token"] = tmp_df["token"].apply(str)\n'
INJECT_LINE = '        tmp_df["label"] = tmp_df["label"].apply(lambda x: x.replace("_", "-") if isinstance(x, str) and (x.startswith("B_") or x.startswith("I_")) else x)\n'


def patch_notebook(nb_path: Path) -> dict:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    stats = {pat: 0 for pat, _ in REPLACEMENTS}

    stats["inject_cache_normalize"] = 0

    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        new_source = []
        injected_in_this_cell = False
        for line in cell.get("source", []):
            for src, dst in REPLACEMENTS:
                if src in line:
                    line = line.replace(src, dst)
                    stats[src] += 1
            new_source.append(line)
            # Defensive: kalau ini cell yang punya cache-hit filter_threshold,
            # dan baris ini = `tmp_df["token"] = tmp_df["token"].apply(str)`,
            # inject normalization line setelahnya (sekali per cell, idempotent
            # check pakai INJECT_LINE.strip() agar tidak double-inject).
            if (
                INJECT_BEFORE_RETURN.strip() in line
                and "cache_path" in "".join(cell.get("source", []))
                and not injected_in_this_cell
                and INJECT_LINE.strip() not in "".join(cell.get("source", []))
            ):
                new_source.append(INJECT_LINE)
                stats["inject_cache_normalize"] += 1
                injected_in_this_cell = True
        cell["source"] = new_source

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    return stats


def main() -> None:
    for rel in NOTEBOOKS:
        nb_path = ROOT / rel
        if not nb_path.exists():
            print(f"[SKIP] {rel} — file tidak ada")
            continue
        stats = patch_notebook(nb_path)
        print(f"[OK]   {rel}")
        for pat, n in stats.items():
            marker = "[+]" if n > 0 else "[ ]"
            print(f"       {marker} {n}x  {pat}")


if __name__ == "__main__":
    main()
