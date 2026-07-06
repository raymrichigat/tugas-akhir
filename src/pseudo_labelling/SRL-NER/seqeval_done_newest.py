#!/usr/bin/env python3
"""
seqeval_done_newest.py — F1 entity-level (seqeval) untuk SEMUA skenario di `done_newest`
TANPA menjalankan model. Prediksi test set direkonstruksi dari artefak yang sudah disimpan
notebook: `*-correct.xlsx` (pred==gold) + `*-incorrect.xlsx` (pred!=gold, urutan asli terjaga).

Metode rekonstruksi (per test.csv yang urut):
  pred := gold untuk semua token; lalu override posisi yang ada di file `incorrect`.
  Karena file incorrect mempertahankan urutan kemunculan asli, tiap baris incorrect
  dipetakan ke kemunculan pertama (text_id, token, true_label) yang cocok saat menyusuri
  test.csv secara urut. correct.xlsx dipakai sebagai cross-check jumlah.
  (Ambiguitas hanya muncul kalau token+gold identik berulang dalam 1 chunk dan salah satunya
   error — sangat jarang, dampak ke F1 entity-level < 0.001.)

Head-to-head: test.csv yang sama untuk semua skenario. No-GPU, tidak load model.

Output: data/result/pseudo-labelling/SRL-NER/done_newest/seqeval_done_newest_results.md
Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\seqeval_done_newest.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from seqeval.metrics import classification_report as seq_report
from seqeval.metrics import f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[3]
DN = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "done_newest"
TEST_CSV = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "test.csv"
OUT_MD = DN / "seqeval_done_newest_results.md"

# Urutan tabel: Grup A (imbalance) -> pos-tag -> Grup B (model lain).
SCENARIOS = {
    "S1-baseline (indolem uncased)": DN / "baseline/output_S1_baseline/evaluation",
    "S2-weighted-CE":                DN / "weighted_class/output_S2_weighted_ce/evaluation",
    "S3a-SCL":                       DN / "scl/output_S3a_scl/evaluation",
    "S3b-JSCL":                      DN / "jscl/output_S3b_jscl/evaluation",
    "S4-augmentation":               DN / "augmentation/output_S4_augmentation/evaluation",
    "S5-POS-tag":                    DN / "pos_tag/output_pos_tag/evaluation",
    "B-indobert-cased (p1)":         DN / "indobert-base-p1/output_GrupB_cased/evaluation",
    "B-roberta (indo)":              DN / "roberta/output_GrupB_roberta/evaluation",
    "B-cahya-bert-1.5G":             DN / "cahya-bert-base/output_GrupB_cahya/evaluation",
    "B-distilbert":                  DN / "distilbert/output_GrupB_distilbert/evaluation",
}

LABELS = ["PERSON", "LOCATION", "EVENT", "TIME"]


def to_dash(lbl: str) -> str:
    """B_PERSON / I_PERSON (underscore, dari xlsx) -> B-PERSON / I-PERSON (seqeval)."""
    lbl = str(lbl)
    if lbl.startswith(("B_", "I_")):
        return lbl.replace("_", "-", 1)
    return lbl


def pick_iter_file(eval_dir: Path, suffix: str) -> Path | None:
    """Ambil file *-<iter>-<suffix>.xlsx dgn nomor iterasi tertinggi (suffix: correct/incorrect)."""
    cands = sorted(eval_dir.glob(f"*-{suffix}.xlsx"))
    if not cands:
        return None
    def iter_num(p: Path) -> int:
        # ...iterative-N-<suffix>.xlsx -> N; tanpa 'iterative' (iter-1) -> 1
        parts = p.stem.split("-")
        for i, tok in enumerate(parts):
            if tok == "iterative" and i + 1 < len(parts) and parts[i + 1].isdigit():
                return int(parts[i + 1])
        return 1
    return max(cands, key=iter_num)


def reconstruct(eval_dir: Path, gold: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Kembalikan Series pred (align dgn `gold` yang urut) + info diagnostik."""
    f_inc = pick_iter_file(eval_dir, "incorrect")
    f_cor = pick_iter_file(eval_dir, "correct")
    if f_inc is None:
        raise FileNotFoundError(f"tidak ada *-incorrect.xlsx di {eval_dir}")

    inc = pd.read_excel(f_inc)
    inc.columns = [c.strip() for c in inc.columns]
    inc["token"] = inc["token"].astype(str)
    inc["true_label"] = inc["true_label"].astype(str).map(to_dash)
    inc["pred_label"] = inc["pred_label"].astype(str).map(to_dash)

    n_correct = None
    if f_cor is not None:
        cor = pd.read_excel(f_cor)
        n_correct = len(cor)

    pred = gold["label"].tolist()  # start: pred == gold (semua token 'correct')
    tok = gold["token"].tolist()
    tid = gold["text_id"].tolist()
    lab = gold["label"].tolist()

    # susuri test.csv urut; tempatkan tiap baris incorrect (yg juga urut) ke kemunculan
    # pertama (text_id, token, true) yang belum terpakai.
    pi = 0
    inc_tid = inc["text_id"].astype(str).tolist()
    inc_tok = inc["token"].tolist()
    inc_true = inc["true_label"].tolist()
    inc_pred = inc["pred_label"].tolist()
    for j in range(len(gold)):
        if pi < len(inc) and str(tid[j]) == inc_tid[pi] and tok[j] == inc_tok[pi] and lab[j] == inc_true[pi]:
            pred[j] = inc_pred[pi]
            pi += 1

    info = {
        "file_inc": f_inc.name,
        "n_inc": len(inc),
        "n_inc_placed": pi,
        "n_correct_file": n_correct,
        "token_acc": (pd.Series(pred).values == gold["label"].values).mean(),
    }
    return pd.Series(pred, index=gold.index), info


def seqs_by_chunk(gold: pd.DataFrame, pred: pd.Series) -> tuple[list, list]:
    true_seqs, pred_seqs = [], []
    g = gold.copy()
    g["pred"] = pred.values
    for _, sub in g.groupby("text_id", sort=False):
        true_seqs.append(sub["label"].tolist())
        pred_seqs.append(sub["pred"].tolist())
    return true_seqs, pred_seqs


def parse_report(report: str) -> dict:
    out = {}
    for line in report.splitlines():
        p = line.split()
        if len(p) >= 5 and p[0] in LABELS:
            out[p[0]] = {"precision": p[1], "recall": p[2], "f1": p[3], "support": p[4]}
    return out


def main() -> None:
    gold = pd.read_csv(TEST_CSV)
    gold["token"] = gold["token"].astype(str)
    gold["label"] = gold["label"].astype(str).map(to_dash)
    gold["text_id"] = gold["text_id"].astype(str)
    print(f"[OK] test.csv {len(gold):,} token, {gold['text_id'].nunique()} chunk\n")

    rows = []
    for tag, ed in SCENARIOS.items():
        if not ed.is_dir():
            print(f"[SKIP] {tag}: dir tidak ada ({ed})")
            continue
        try:
            pred, info = reconstruct(ed, gold)
        except Exception as e:  # noqa: BLE001
            print(f"[ERR] {tag}: {e}")
            continue
        ts, ps = seqs_by_chunk(gold, pred)
        f1 = f1_score(ts, ps)
        pr = precision_score(ts, ps)
        rc = recall_score(ts, ps)
        rep = seq_report(ts, ps, digits=4)
        pc = parse_report(rep)
        warn = "" if info["n_inc_placed"] == info["n_inc"] else f"  ⚠ placed {info['n_inc_placed']}/{info['n_inc']}"
        cross = "" if info["n_correct_file"] is None or info["n_correct_file"] + info["n_inc"] == len(gold) \
            else f"  ⚠ correct+incorrect={info['n_correct_file']+info['n_inc']}≠{len(gold)}"
        print(f"{tag:32s} F1={f1:.4f} P={pr:.4f} R={rc:.4f}  ({info['file_inc']}, "
              f"err={info['n_inc']}, tok-acc={info['token_acc']:.4f}){warn}{cross}")
        rows.append({"tag": tag, "f1": f1, "pr": pr, "rc": rc, "rep": rep, "pc": pc, "info": info})

    # ---- tulis markdown ----
    L = ["# Seqeval Entity-Level — `done_newest` (re-run penuh 10 skenario)\n",
         "> Dihasilkan `seqeval_done_newest.py`. Entity-level (span) seqeval, **tanpa menjalankan "
         "model**: prediksi test direkonstruksi dari `*-correct.xlsx` + `*-incorrect.xlsx`. "
         f"test.csv sama untuk semua ({len(gold):,} token / {gold['text_id'].nunique()} chunk).\n",
         "\n## Ringkasan (F1 entity-level, urut skenario)\n",
         "| Skenario | F1 | Precision | Recall | PERSON | LOCATION | EVENT | TIME |",
         "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        pc = r["pc"]
        cell = lambda c: pc.get(c, {}).get("f1", "-")  # noqa: E731
        L.append(f"| {r['tag']} | {r['f1']:.4f} | {r['pr']:.4f} | {r['rc']:.4f} | "
                 f"{cell('PERSON')} | {cell('LOCATION')} | {cell('EVENT')} | {cell('TIME')} |")

    best = max(rows, key=lambda r: r["f1"]) if rows else None
    if best:
        L.append(f"\n**Winner: `{best['tag']}` — F1 = {best['f1']:.4f}.**\n")

    L.append("\n## Diagnostik rekonstruksi\n")
    L.append("| Skenario | file incorrect | #error token | ditempatkan | token-acc |")
    L.append("|---|---|---:|---:|---:|")
    for r in rows:
        i = r["info"]
        L.append(f"| {r['tag']} | {i['file_inc']} | {i['n_inc']} | {i['n_inc_placed']} | {i['token_acc']:.4f} |")

    L.append("\n## Classification report per skenario (seqeval)\n")
    for r in rows:
        L.append(f"### {r['tag']}\n```\n{r['rep'].rstrip()}\n```\n")

    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[OK] -> {OUT_MD}")


if __name__ == "__main__":
    main()
