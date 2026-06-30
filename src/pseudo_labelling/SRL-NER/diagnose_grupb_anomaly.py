#!/usr/bin/env python3
"""
diagnose_grupb_anomaly.py — diagnosa anomali F1 rendah pada Grup B (IndoBERT-cased & RoBERTa).

Pertanyaan: apakah base/iter-awal sudah bagus lalu DIRUSAK self-training (temuan menarik),
atau memang jelek dari fine-tuning dasar? Eval seqeval entity-level untuk base + iter-2..6
tiap backbone, tampilkan trajektori F1 + per-kelas. No-GPU (CPU).

Output: data/result/analysis/error_analysis_done_running/diagnose_grupb_anomaly.md
"""
from __future__ import annotations
from pathlib import Path
import re, sys
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from evaluate_seqeval import evaluate_model  # noqa: E402

ROOT = HERE.parents[2]
DONE = ROOT / "data/result/pseudo-labelling/SRL-NER/done_running"
TEST = ROOT / "data/result/pseudo-labelling/SRL-NER/test.csv"
OUT = ROOT / "data/result/analysis/error_analysis_done_running/diagnose_grupb_anomaly.md"

SCEN = {
    "cased": DONE / "indobert-base-p1/output_GrupB_cased/models",
    "roberta": DONE / "roberta/output_GrupB_roberta/models",
}

def parse_class(report: str, cls: str) -> str:
    for line in report.splitlines():
        p = line.split()
        if p and p[0] == cls and len(p) >= 4:
            return p[3]
    return "-"

def main():
    df = pd.read_csv(TEST)
    df["token"] = df["token"].astype(str)
    df["label"] = df["label"].astype(str)

    rows = []   # (scen, ckpt_label, f1, prec, rec, report)
    for scen, mdir in SCEN.items():
        ckpts = []
        base = mdir / "bert-only-sirah-ner-base"
        if (base / "model.safetensors").exists() or (base / "pytorch_model.bin").exists():
            ckpts.append(("base", base))
        for d in sorted(mdir.glob("*iteration-*")):
            m = re.search(r"iteration-(\d+)$", d.name)
            if m and ((d / "model.safetensors").exists() or (d / "pytorch_model.bin").exists()):
                ckpts.append((f"iter-{m.group(1)}", d))
        ckpts.sort(key=lambda x: (x[0] != "base", int(re.sub(r"\D", "", x[0]) or 0)))
        for lbl, p in ckpts:
            tag = f"{scen}-{lbl}"
            try:
                r = evaluate_model(p, df, tag)
                rows.append((scen, lbl, r["f1"], r["precision"], r["recall"], r["report"]))
            except Exception as e:  # noqa: BLE001
                print(f"[ERR] {tag}: {e}")
                rows.append((scen, lbl, None, None, None, str(e)))

    L = ["# Diagnosa anomali Grup B (cased & RoBERTa) — trajektori self-training\n",
         "> `diagnose_grupb_anomaly.py`, seqeval entity-level, test.csv sama. "
         "Tujuan: pisahkan 'rusak oleh self-training' vs 'jelek dari base'.\n",
         "\n## Trajektori F1 per checkpoint\n",
         "| Backbone | Checkpoint | F1 | Precision | Recall | F1 EVENT | F1 TIME | F1 PERSON | F1 LOCATION |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for scen, lbl, f1, pr, rc, rep in rows:
        if f1 is None:
            L.append(f"| {scen} | {lbl} | ERR | | | | | | |"); continue
        L.append(f"| {scen} | {lbl} | {f1:.4f} | {pr:.4f} | {rc:.4f} | "
                 f"{parse_class(rep,'EVENT')} | {parse_class(rep,'TIME')} | "
                 f"{parse_class(rep,'PERSON')} | {parse_class(rep,'LOCATION')} |")
    L.append("\n## classification_report lengkap per checkpoint\n")
    for scen, lbl, f1, pr, rc, rep in rows:
        if f1 is None: continue
        L.append(f"### {scen}-{lbl}\n```\n{rep.rstrip()}\n```\n")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[OK] -> {OUT}")
    print("\n".join(L[3:6 + len(rows)]))

if __name__ == "__main__":
    main()
