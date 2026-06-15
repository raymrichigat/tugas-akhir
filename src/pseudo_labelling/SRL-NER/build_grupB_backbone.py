#!/usr/bin/env python3
"""
build_grupB_backbone.py — bangun notebook **Grup B (perbandingan backbone)** sebagai
turunan notebook S1 baseline LIVE (revisi Bu Diana 2026-06-05). Reproducible: kalau S1
berubah, rebuild.

Satu-satunya perubahan metodologis vs S1: **MODEL_NAME** (tokenizer + model) diganti.
Pipeline lain (data, split, hyperparameter, self-training, label underscore, patch
"auto-detect iterasi terakhir" + runtime timer) IDENTIK → perbandingan terkontrol.

Konteks penting (lihat memory `baseline-srl-ner-pakai-indobert-uncased-bukan-cased`):
baseline aktual = `indolem/indobert-base-uncased` (UNCASED). Maka backbone yang benar-benar
mengisolasi efek kapitalisasi adalah yang **cased** = `indobenchmark/indobert-base-p1`.
Dasar metode = paper Bu Diana (Transformer-Based SRL ...) yang memang membandingkan
beberapa transformer (BERT/RoBERTa/GPT-2/Llama-2) → ganti foundation model = setia ke metode.

Sumber : src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_colab.ipynb   (base LIVE, ter-patch)
Output : src/pseudo_labelling/SRL-NER/srl_ner_sirah_<slug>_colab.ipynb

Catatan: `GrupB_cahya` (cahya/bert-1.5G) & `GrupB_distilbert` dibuat manual 2026-06-10 dari
base yang sama → biasanya cukup regenerate `cased` + `roberta` saja (yang belum ada).

No-GPU. Jalankan:
  venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_grupB_backbone.py            # default: cased
  venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_grupB_backbone.py roberta
  venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_grupB_backbone.py cahya       # menimpa file manual!
  venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\build_grupB_backbone.py cahya-distil # menimpa file manual!
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASELINE_MODEL = "indolem/indobert-base-uncased"
TITLE_SRC = "# BERT Percobaan 1 (35% train and 65% unlabelled)"
# cocokkan path output apa pun (output, output_S1_baseline, dst.) → diganti per-slug
ROOT_RE = re.compile(r"(/content/drive/MyDrive/TA-Sirah/)output[\w.\-]*'")

# preset backbone Grup B. slug -> dipakai untuk nama notebook + folder output (isolasi).
BACKBONES = {
    "cased": {
        "model": "indobenchmark/indobert-base-p1",
        "slug": "GrupB_cased",
        "casing": "cased",
        "note": (
            "cased (vocab 31.923) - inti eksperimen kapitalisasi: baseline indolem UNCASED "
            "mengecilkan huruf (Perang vs perang tak terbedakan), model cased pertahankan sinyal kapital."
        ),
    },
    "cahya": {
        "model": "cahya/bert-base-indonesian-1.5G",
        "slug": "GrupB_cahya",
        "casing": "uncased",
        "note": "uncased (vocab 32.000) - pembanding antar-model uncased.",
    },
    "cahya-distil": {
        "model": "cahya/distilbert-base-indonesian",
        "slug": "GrupB_distilbert",
        "casing": "uncased",
        "note": "uncased, DistilBERT (lebih kecil/cepat) - pembanding antar-model uncased.",
    },
    "roberta": {
        "model": "cahya/roberta-base-indonesian-1.5G",
        "slug": "GrupB_roberta",
        "casing": "case-preserving",
        "prefix_space": True,  # byte-level BPE + is_split_into_words=True → wajib add_prefix_space
        "note": (
            "RoBERTa (arsitektur beda dari BERT - meniru paper yang bandingin BERT vs RoBERTa). "
            "Byte-level BPE -> add_prefix_space=True (auto-patch). Pasangan terkontrol vs cahya/bert-1.5G. "
            "Model card kosong -> detail pretraining tak terdokumentasi (lebih lemah untuk disitasi)."
        ),
    },
}


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def build(repo: Path, key: str) -> None:
    bb = BACKBONES[key]
    model, slug = bb["model"], bb["slug"]

    src_nb = repo / "src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_colab.ipynb"
    out_nb = repo / f"src/pseudo_labelling/SRL-NER/srl_ner_sirah_{slug}_colab.ipynb"

    if not src_nb.exists():
        raise SystemExit(f"[err] notebook base S1 live tidak ditemukan: {src_nb}")

    nb = json.loads(src_nb.read_text(encoding="utf-8"))

    # buang widget-state tqdm yang ke-bawa dari run S1 (bisa ratusan KB, bikin notebook bengkak)
    had_widgets = bool(nb.get("metadata", {}).pop("widgets", None))

    new_title = f"# Grup B — {model} ({bb['casing']}), turunan S1 baseline"
    needs_prefix = bool(bb.get("prefix_space"))
    n_title = n_root = n_model = n_prefix = 0

    for cell in nb["cells"]:
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

        new_src = []
        for line in cell.get("source", []):
            if TITLE_SRC in line:
                line = line.replace(TITLE_SRC, new_title)
                n_title += 1
            if "root_dir" in line and "TA-Sirah/output" in line:
                line, n = ROOT_RE.subn(rf"\g<1>output_{slug}'", line)
                n_root += n
            if f'"{BASELINE_MODEL}"' in line:
                line = line.replace(f'"{BASELINE_MODEL}"', f'"{model}"')
                n_model += 1
                # RoBERTa byte-level BPE + is_split_into_words=True → wajib add_prefix_space=True
                if needs_prefix and "AutoTokenizer.from_pretrained(" in line:
                    line = line.replace(
                        ", model_max_length=512)", ", model_max_length=512, add_prefix_space=True)"
                    )
                    n_prefix += 1
            new_src.append(line)
        cell["source"] = new_src

    if n_title != 1:
        raise SystemExit(f"[err] judul ter-patch {n_title}x (harusnya 1). Cek pola TITLE_SRC.")
    if n_root < 1:
        raise SystemExit("[err] root_dir tidak ter-patch. Pola path TA-Sirah/output... berubah?")
    if n_model != 2:
        raise SystemExit(
            f"[err] referensi model = {n_model} (harusnya 2: tokenizer + model_name). "
            "Struktur notebook base berubah? Cek manual."
        )
    if needs_prefix and n_prefix != 1:
        raise SystemExit(
            f"[err] add_prefix_space gagal disisipkan (n_prefix={n_prefix}). "
            "Pola ', model_max_length=512)' di sel tokenizer berubah? Cek manual."
        )

    out_nb.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"[ok] {out_nb.relative_to(repo)}")
    print(f"     backbone: {BASELINE_MODEL} -> {model} ({bb['casing']})")
    print(f"     {bb['note']}")
    print(
        f"     patch: title={n_title} root_dir={n_root} model_ref={n_model} "
        f"add_prefix_space={n_prefix} widgets_stripped={had_widgets}"
    )
    print(f"     total cells: {len(nb['cells'])}")


def main() -> None:
    repo = find_repo_root(Path(__file__))
    key = sys.argv[1] if len(sys.argv) > 1 else "cased"
    if key not in BACKBONES:
        raise SystemExit(f"[err] backbone '{key}' tidak dikenal. Pilihan: {', '.join(BACKBONES)}")
    build(repo, key)


if __name__ == "__main__":
    main()
