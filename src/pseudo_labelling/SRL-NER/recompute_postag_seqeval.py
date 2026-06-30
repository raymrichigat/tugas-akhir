#!/usr/bin/env python3
"""
recompute_postag_seqeval.py — hitung F1 entity-level (seqeval) untuk skenario pos-tag
TANPA inference (model pos-tag tidak punya config.json + arsitektur custom butuh fitur POS).

Metode: rekonstruksi urutan prediksi dari
  - test.csv               -> gold BERURUTAN (kolom 'id' = text_id.NNN menjamin urutan token)
  - <skenario>-incorrect.xlsx -> token yang SALAH + pred_label-nya
pred = gold untuk semua token, lalu override posisi yang ada di incorrect (greedy, urut).

VALIDASI: metode diuji dulu pada skenario yg sudah punya F1 resmi (baseline/scl/cased).
Kalau cocok (selisih < ~0.005), barulah pos-tag dipercaya.

No-GPU. Output dicetak ke stdout (tidak menimpa file apa pun).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from seqeval.metrics import f1_score, classification_report

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRL = ROOT / "data/result/pseudo-labelling/SRL-NER"
DONE = SRL / "done_running"
TEST = SRL / "test.csv"

# skenario -> (path incorrect.xlsx, F1 resmi utk validasi atau None)
SCN = {
    "baseline":  ("baseline/output_S1_baseline/evaluation/bert-only-sirah-ner-iterative-6-incorrect.xlsx", 0.9481),
    "scl":       ("scl/output_S2a_scl/evaluation/bert-only-sirah-ner-S2a-scl-iterative-4-incorrect.xlsx", 0.9512),
    "cased":     ("indobert-base-p1/output_GrupB_cased/evaluation/bert-only-sirah-ner-iterative-6-incorrect.xlsx", 0.7770),
    "pos-tag":   ("pos-tag/output_pos_tag/evaluation/bert-pos-sirah-ner-iterative-4-incorrect.xlsx", None),
}


def norm(l: str) -> str:
    if not isinstance(l, str):
        return "O"
    return l.replace("B_", "B-").replace("I_", "I-")


def reconstruct(test: pd.DataFrame, inc_path: Path):
    inc = pd.read_excel(inc_path)
    inc["tl"] = inc["true_label"].map(norm)
    inc["pl"] = inc["pred_label"].map(norm)
    inc_by_chunk = {tid: g for tid, g in inc.groupby("text_id")}

    gold_seqs, pred_seqs = [], []
    for tid, g in test.groupby("text_id", sort=False):
        g = g.sort_values("id")
        toks = g["token"].astype(str).tolist()
        gold = g["label"].astype(str).tolist()
        pred = gold.copy()
        sub = inc_by_chunk.get(tid)
        if sub is not None:
            used = set()
            for _, r in sub.iterrows():
                placed = False
                # 1) cocokkan token + gold yg belum dipakai (urut kiri->kanan)
                for k in range(len(toks)):
                    if k not in used and toks[k] == str(r["token"]) and gold[k] == r["tl"]:
                        pred[k] = r["pl"]; used.add(k); placed = True; break
                # 2) fallback: cocokkan token saja
                if not placed:
                    for k in range(len(toks)):
                        if k not in used and toks[k] == str(r["token"]):
                            pred[k] = r["pl"]; used.add(k); placed = True; break
        gold_seqs.append(gold)
        pred_seqs.append(pred)
    return gold_seqs, pred_seqs


def main():
    test = pd.read_csv(TEST)
    test["token"] = test["token"].astype(str)
    print(f"[OK] test.csv {len(test)} token, {test['text_id'].nunique()} chunk\n")

    print(f"{'skenario':12} {'F1_rekon':>9} {'F1_resmi':>9} {'selisih':>8}  status")
    print("-" * 55)
    valid_ok = True
    postag_report = None
    for name, (rel, official) in SCN.items():
        gs, ps = reconstruct(test, DONE / rel)
        f1 = f1_score(gs, ps)
        if official is not None:
            diff = abs(f1 - official)
            ok = diff < 0.005
            valid_ok &= ok
            print(f"{name:12} {f1:9.4f} {official:9.4f} {diff:8.4f}  {'OK' if ok else 'BEDA!'}")
        else:
            print(f"{name:12} {f1:9.4f} {'-':>9} {'-':>8}  (target)")
            postag_report = classification_report(gs, ps, digits=4)
            postag_f1 = f1

    print("\nValidasi metode:", "LULUS (rekonstruksi ~ resmi)" if valid_ok else "GAGAL - jangan dipakai")
    if valid_ok and postag_report is not None:
        print(f"\n=== pos-tag entity-level (seqeval), F1 = {postag_f1:.4f} ===")
        print(postag_report)


if __name__ == "__main__":
    main()
