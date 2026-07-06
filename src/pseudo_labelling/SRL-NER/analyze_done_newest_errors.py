#!/usr/bin/env python3
"""
analyze_done_newest_errors.py — analisis error NER berbasis DATA untuk run baru `done_newest`,
dikelompokkan PER GRUP skenario. Membaca `*-incorrect.xlsx` (error token-level pada test set)
+ test.csv (gold) untuk kategorisasi: FP / FN / misklasifikasi tipe / boundary (B/I), per kelas,
pasangan confusion, efek kapitalisasi, dan posisi token dalam chunk (proxy chunking).

Grup:
  A (penanganan imbalance): baseline, weighted-CE, SCL, JSCL, augmentation
  P (fitur POS-tag)       : pos-tag
  B (model bahasa lain)   : indobert-cased, roberta, cahya-1.5G, distilbert

Angka F1 entity-level ada di `seqeval_done_newest_results.md`; di sini fokus **mengapa** error.
No-GPU. Tidak melatih / tidak re-predict; murni baca artefak prediksi yang sudah tersimpan.

Output: data/result/analysis/error_analysis_done_newest/error_analysis_done_newest.md
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DN = ROOT / "data/result/pseudo-labelling/SRL-NER/done_newest"
TEST = ROOT / "data/result/pseudo-labelling/SRL-NER/test.csv"
OUTDIR = ROOT / "data/result/analysis/error_analysis_done_newest"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "error_analysis_done_newest.md"

# tag -> (grup, eval_dir)
SC = {
    "S1-baseline":      ("A", DN / "baseline/output_S1_baseline/evaluation"),
    "S2-weighted-CE":   ("A", DN / "weighted_class/output_S2_weighted_ce/evaluation"),
    "S3a-SCL":          ("A", DN / "scl/output_S3a_scl/evaluation"),
    "S3b-JSCL":         ("A", DN / "jscl/output_S3b_jscl/evaluation"),
    "S4-augmentation":  ("A", DN / "augmentation/output_S4_augmentation/evaluation"),
    "S5-POS-tag":       ("P", DN / "pos_tag/output_pos_tag/evaluation"),
    "B-indobert-cased": ("B", DN / "indobert-base-p1/output_GrupB_cased/evaluation"),
    "B-roberta":        ("B", DN / "roberta/output_GrupB_roberta/evaluation"),
    "B-cahya-1.5G":     ("B", DN / "cahya-bert-base/output_GrupB_cahya/evaluation"),
    "B-distilbert":     ("B", DN / "distilbert/output_GrupB_distilbert/evaluation"),
}
GRUP_NAMA = {
    "A": "Grup A — penanganan imbalance (baseline / weighted-CE / SCL / JSCL / augmentation)",
    "P": "Grup P — fitur POS-tag",
    "B": "Grup B — model bahasa lain (cased / roberta / cahya / distilbert)",
}
KELAS = ["PERSON", "LOCATION", "EVENT", "TIME"]


def typ(lbl: str) -> str:
    lbl = str(lbl)
    if lbl in ("O", "nan", ""):
        return "O"
    return lbl.replace("B_", "").replace("I_", "").replace("B-", "").replace("I-", "")


def bio(lbl: str) -> str:
    lbl = str(lbl)
    return lbl.split("_")[0].split("-")[0] if lbl not in ("O", "nan", "") else "O"


def find_incorrect(d: Path) -> Path | None:
    """Ambil *-incorrect.xlsx dgn iterasi tertinggi."""
    cands = sorted(d.glob("*-incorrect.xlsx"))
    if not cands:
        return None

    def itnum(p: Path) -> int:
        parts = p.stem.split("-")
        for i, t in enumerate(parts):
            if t == "iterative" and i + 1 < len(parts) and parts[i + 1].isdigit():
                return int(parts[i + 1])
        return 1
    return max(cands, key=itnum)


def categorize(t_true: str, t_pred: str) -> str:
    if t_true == "O" and t_pred != "O":
        return "FP (over-deteksi)"
    if t_true != "O" and t_pred == "O":
        return "FN (terlewat)"
    if t_true != "O" and t_pred != "O" and t_true != t_pred:
        return "Misklasifikasi tipe"
    if t_true == t_pred and t_true != "O":
        return "Boundary (B/I)"
    return "lain"


def main():
    gold = pd.read_csv(TEST)
    gold["token"] = gold["token"].astype(str)
    gold["pos_in_chunk"] = gold.groupby("text_id").cumcount()

    L = []
    P = L.append
    P("# Analisis Error NER Berbasis Data — `done_newest` (per grup)\n")
    P(f"> Sumber: `*-incorrect.xlsx` (error token-level test set) tiap skenario + `test.csv` "
      f"({len(gold):,} token, {gold['text_id'].nunique()} chunk). "
      f"Skor entity-level (seqeval) di `seqeval_done_newest_results.md`; di sini fokus **mengapa** error.\n")
    P("**Catatan:** kategori error di sini bersifat token-level (BIO), sedangkan F1 ringkasan bersifat "
      "entity-level (span) — angka absolut bisa beda tipis, tapi pola error konsisten. Semua skenario "
      "pakai file error iterasi terakhir yang tersimpan (iter-6).\n")

    store = {}       # tag -> df error beranotasi
    summ = {}        # tag -> dict ringkasan
    per_class = {}   # tag -> {kelas: (fn, fp)}

    for tag, (grup, d) in SC.items():
        f = find_incorrect(d)
        if f is None:
            summ[tag] = None
            continue
        df = pd.read_excel(f)
        df.columns = [c.strip() for c in df.columns]
        df["true_label"] = df["true_label"].astype(str)
        df["pred_label"] = df["pred_label"].astype(str)
        df["token"] = df["token"].astype(str)
        df["t_true"] = df["true_label"].map(typ)
        df["t_pred"] = df["pred_label"].map(typ)
        df["cat"] = [categorize(tt, tp) for tt, tp in zip(df.t_true, df.t_pred)]
        store[tag] = df

        cats = df["cat"].value_counts().to_dict()
        n = len(df)
        summ[tag] = {
            "file": f.name, "n": n,
            "FP": cats.get("FP (over-deteksi)", 0),
            "FN": cats.get("FN (terlewat)", 0),
            "MIS": cats.get("Misklasifikasi tipe", 0),
            "BND": cats.get("Boundary (B/I)", 0),
        }
        fn_by = Counter(df[df.cat == "FN (terlewat)"]["t_true"])
        fp_by = Counter(df[df.cat == "FP (over-deteksi)"]["t_pred"])
        per_class[tag] = {c: (fn_by.get(c, 0), fp_by.get(c, 0)) for c in KELAS}

    # ============ bagian per-grup ============
    for grup in ["A", "P", "B"]:
        P(f"\n---\n\n# {GRUP_NAMA[grup]}\n")
        tags = [t for t, (g, _) in SC.items() if g == grup and summ.get(t)]

        # tabel komposisi error grup
        P("### Komposisi error (token-level)\n")
        P("| Skenario | Total err | FP | FN | Mis-tipe | Boundary |")
        P("|---|---:|---:|---:|---:|---:|")
        for t in tags:
            s = summ[t]
            P(f"| {t} | {s['n']} | {s['FP']} | {s['FN']} | {s['MIS']} | {s['BND']} |")

        # FN/FP per kelas
        P("\n### FN / FP per kelas entitas\n")
        P("| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |")
        P("|---|---|---|---|---|")
        for t in tags:
            cells = [f"{per_class[t][c][0]}/{per_class[t][c][1]}" for c in KELAS]
            P(f"| {t} | " + " | ".join(cells) + " |")

        # pasangan misklasifikasi tipe dominan per skenario
        P("\n### Pasangan misklasifikasi tipe (gold→pred) dominan\n")
        for t in tags:
            df = store[t]
            mis = Counter(df[df.cat == "Misklasifikasi tipe"].apply(
                lambda r: f"{r.t_true}->{r.t_pred}", axis=1))
            P(f"- **{t}**: {dict(mis.most_common(6)) if mis else '—'}")

    # ============ efek kapitalisasi (temuan 'Perang' vs 'perang') ============
    P("\n---\n\n# Efek kapitalisasi pada FP/FN\n")
    P("> Menguji temuan inkonsistensi gold: token entitas berawalan huruf besar cenderung "
      "ke-anotasi, huruf kecil tidak. Kalau FP condong huruf besar & FN condong huruf besar, "
      "sebagian 'error' sebetulnya batas anotasi gold, bukan murni salah model.\n")
    P("| Skenario | %FP awal-kapital | %FN awal-kapital | #FP | #FN |")
    P("|---|---:|---:|---:|---:|")
    for tag in SC:
        if not summ.get(tag):
            continue
        df = store[tag]
        fp = df[df.cat == "FP (over-deteksi)"]
        fn = df[df.cat == "FN (terlewat)"]
        fp_cap = (fp["token"].str[:1].str.isupper()).mean() * 100 if len(fp) else 0
        fn_cap = (fn["token"].str[:1].str.isupper()).mean() * 100 if len(fn) else 0
        P(f"| {tag} | {fp_cap:.0f} | {fn_cap:.0f} | {len(fp)} | {len(fn)} |")

    # token FP/FN tersering untuk baseline + winner (augmentation)
    P("\n### Token FP/FN tersering (baseline vs winner augmentation)\n")
    for tag in ["S1-baseline", "S4-augmentation"]:
        if not summ.get(tag):
            continue
        df = store[tag]
        fp_tok = Counter(df[df.cat == "FP (over-deteksi)"]["token"]).most_common(10)
        fn_tok = Counter(df[df.cat == "FN (terlewat)"]["token"]).most_common(10)
        P(f"- **{tag} — FP tersering**: {fp_tok}")
        P(f"- **{tag} — FN tersering**: {fn_tok}")

    # ============ proxy chunking: posisi error dalam chunk ============
    P("\n---\n\n# Proxy dampak chunking: posisi token error dalam chunk\n")
    P("> Tanpa ablation 'tanpa chunking', efek chunking diuji tak-langsung: apakah error memusat "
      "di **tepi chunk** (10% awal/akhir token) tempat konteks terpotong.\n")
    gold_idx = {}
    for tid, g in gold.groupby("text_id"):
        m = max(1, len(g) - 1)
        gold_idx[tid] = {tok: i / m for i, tok in zip(g["pos_in_chunk"], g["token"])}
    P("| Skenario | err di tepi (%) | err di tengah (%) |")
    P("|---|---:|---:|")
    for tag in SC:
        if not summ.get(tag):
            continue
        df = store[tag]
        edge = mid = 0
        for tid, tok in zip(df["text_id"], df["token"]):
            rel = gold_idx.get(tid, {}).get(tok)
            if rel is None:
                continue
            if rel <= 0.10 or rel >= 0.90:
                edge += 1
            else:
                mid += 1
        tot = edge + mid or 1
        P(f"| {tag} | {edge/tot*100:.0f} | {mid/tot*100:.0f} |")
    P("\n_(Pemetaan posisi pakai kemunculan pertama token dalam chunk; perkiraan, bukan indeks presisi.)_")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"[OK] -> {OUT}\n")
    print("=== RINGKAS (grup | skenario | n | FP | FN | Mis | Bnd) ===")
    for tag, (grup, _) in SC.items():
        s = summ.get(tag)
        if s:
            print(f"{grup} | {tag:16s} | n={s['n']:4d} FP={s['FP']:4d} FN={s['FN']:4d} MIS={s['MIS']:3d} BND={s['BND']:3d}")


if __name__ == "__main__":
    main()
