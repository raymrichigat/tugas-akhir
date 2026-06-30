#!/usr/bin/env python3
"""
analyze_done_running_errors.py — analisis error NER mendalam (berbasis DATA) untuk semua
skenario di done_running. Membaca file *-incorrect.xlsx (error token-level pada test set)
+ test.csv (gold) untuk mengkategorikan kesalahan: FP / FN / misklasifikasi tipe / boundary,
per kelas, confusion pair, efek kapitalisasi, dan posisi token dalam chunk (proxy chunking).

Output: data/result/analysis/error_analysis_done_running/error_analysis_done_running.md
No-GPU. Tidak melatih / tidak re-predict; murni baca artefak prediksi yang sudah ada.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
DONE = ROOT / "data/result/pseudo-labelling/SRL-NER/done_running"
TEST = ROOT / "data/result/pseudo-labelling/SRL-NER/test.csv"
OUTDIR = ROOT / "data/result/analysis/error_analysis_done_running"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "error_analysis_done_running.md"

# tag -> (eval_dir, label casing). Urutan untuk tabel.
SC = {
    "S1-baseline":      DONE/"baseline/output_S1_baseline/evaluation",
    "S2-weighted-CE":   DONE/"weighted-class/drive-download-20260611T025134Z-3-001/output_S2_weighted_ce/evaluation",
    "S2a-SCL":          DONE/"scl/output_S2a_scl/evaluation",
    "S2b-JSCL":         DONE/"jscl/output_S2b_jscl/evaluation",
    "S4-augmentation":  DONE/"augmentation/output_S4_augmentation/evaluation",
    "S5-POS-tag":       DONE/"pos-tag/output_pos_tag/evaluation",
    "B-indobert-cased": DONE/"indobert-base-p1/output_GrupB_cased/evaluation",
    "B-cahya-1.5G":     DONE/"cahya-bert-base/output_GrupB_cahya/evaluation",
    "B-distilbert":     DONE/"distilbert/output_GrupB_distilbert/evaluation",
    "B-roberta":        DONE/"roberta/output_GrupB_roberta/evaluation",
}

def typ(lbl: str) -> str:
    lbl = str(lbl)
    if lbl in ("O", "nan", ""):
        return "O"
    return lbl.replace("B_", "").replace("I_", "").replace("B-", "").replace("I-", "")

def bio(lbl: str) -> str:
    lbl = str(lbl)
    return lbl.split("_")[0].split("-")[0] if lbl not in ("O","nan","") else "O"

def find_incorrect(d: Path) -> Path | None:
    c = sorted(d.glob("*incorrect.xlsx"))
    return c[0] if c else None

def categorize(t_true: str, t_pred: str, b_true: str, b_pred: str) -> str:
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
    # panjang chunk + posisi token utk proxy chunking
    chunk_len = gold.groupby("text_id").size().to_dict()
    gold["pos_in_chunk"] = gold.groupby("text_id").cumcount()

    L = []
    P = L.append
    P("# Analisis Error NER Berbasis Data — `done_running`\n")
    P(f"> Sumber: file `*-incorrect.xlsx` (error token-level pada test set) tiap skenario + `test.csv` "
      f"({len(gold):,} token, {gold['text_id'].nunique()} chunk). "
      f"Skor entity-level (seqeval) ada di `seqeval_grupB_results.md`; di sini fokus **mengapa** error terjadi.\n")
    P("**Catatan iterasi:** file error disimpan pada iterasi terakhir tiap skenario "
      "(SCL & POS-tag = iter-4, sisanya iter-6). Kategori error bersifat token-level "
      "(BIO), sedangkan F1 ringkasan bersifat entity-level, jadi angka absolut bisa beda tipis "
      "tapi pola error konsisten.\n")

    summary = []
    per_class_rows = []
    confusion_global = Counter()
    examples_store = {}

    for tag, d in SC.items():
        f = find_incorrect(d)
        if f is None:
            P(f"\n## {tag}\n_(file incorrect tidak ditemukan)_\n"); continue
        df = pd.read_excel(f)
        df = df.rename(columns={c: c.strip() for c in df.columns})
        df["true_label"] = df["true_label"].astype(str)
        df["pred_label"] = df["pred_label"].astype(str)
        df["token"] = df["token"].astype(str)
        df["t_true"] = df["true_label"].map(typ)
        df["t_pred"] = df["pred_label"].map(typ)
        df["cat"] = [categorize(tt, tp, bio(a), bio(b))
                     for tt, tp, a, b in zip(df.t_true, df.t_pred, df.true_label, df.pred_label)]

        n = len(df)
        cats = df["cat"].value_counts().to_dict()
        fp = cats.get("FP (over-deteksi)", 0)
        fn = cats.get("FN (terlewat)", 0)
        mis = cats.get("Misklasifikasi tipe", 0)
        bnd = cats.get("Boundary (B/I)", 0)
        summary.append((tag, n, fp, fn, mis, bnd, f.name))

        # per-class: FN per gold-type, FP per pred-type
        fn_by = Counter(df[df.cat=="FN (terlewat)"]["t_true"])
        fp_by = Counter(df[df.cat=="FP (over-deteksi)"]["t_pred"])
        mis_by = Counter(df[df.cat=="Misklasifikasi tipe"].apply(lambda r: f"{r.t_true}->{r.t_pred}", axis=1))
        for c in ["PERSON","LOCATION","EVENT","TIME"]:
            per_class_rows.append((tag, c, fn_by.get(c,0), fp_by.get(c,0)))

        # confusion (true_type -> pred_type) untuk skenario uncased utama digabung
        for tt, tp in zip(df.t_true, df.t_pred):
            confusion_global[(tag, tt, tp)] += 1

        examples_store[tag] = df

        P(f"\n## {tag}  (`{f.name}`)\n")
        P(f"- Total token error: **{n}**")
        P(f"- FP (over-deteksi, gold=O): **{fp}** ({fp/n*100:.0f}%)")
        P(f"- FN (entitas terlewat, pred=O): **{fn}** ({fn/n*100:.0f}%)")
        P(f"- Misklasifikasi tipe (entitas, tipe salah): **{mis}** ({mis/n*100:.0f}%)")
        P(f"- Boundary B/I (tipe benar, batas salah): **{bnd}** ({bnd/n*100:.0f}%)\n")
        P(f"- FN per kelas: {dict(fn_by)}")
        P(f"- FP per kelas (label prediksi): {dict(fp_by)}")
        if mis_by:
            P(f"- Pasangan misklasifikasi: {dict(mis_by)}")

    # ---- tabel ringkas lintas skenario ----
    P("\n\n# Ringkasan lintas skenario (token-level error)\n")
    P("| Skenario | Total err | FP | FN | Mis-tipe | Boundary |")
    P("|---|---:|---:|---:|---:|---:|")
    for tag,n,fp,fn,mis,bnd,_ in summary:
        P(f"| {tag} | {n} | {fp} | {fn} | {mis} | {bnd} |")

    # ---- per-kelas FN/FP lintas skenario ----
    P("\n# FN & FP per kelas entitas (token-level)\n")
    P("| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |")
    P("|---|---|---|---|---|")
    pc = defaultdict(dict)
    for tag,c,fn_,fp_ in per_class_rows:
        pc[tag][c] = (fn_,fp_)
    for tag in SC:
        if tag not in pc: continue
        cells = []
        for c in ["PERSON","LOCATION","EVENT","TIME"]:
            fn_,fp_ = pc[tag].get(c,(0,0))
            cells.append(f"{fn_}/{fp_}")
        P(f"| {tag} | " + " | ".join(cells) + " |")

    # ---- analisis kapitalisasi (gold inconsistency) pada baseline & winner ----
    P("\n# Efek kapitalisasi pada FP/FN (uji temuan 'Perang' vs 'perang')\n")
    for tag in ["S1-baseline","S4-augmentation","B-indobert-cased"]:
        if tag not in examples_store: continue
        df = examples_store[tag]
        fp = df[df.cat=="FP (over-deteksi)"]
        fn = df[df.cat=="FN (terlewat)"]
        fp_cap = (fp["token"].str[:1].str.isupper()).mean()*100 if len(fp) else 0
        fn_cap = (fn["token"].str[:1].str.isupper()).mean()*100 if len(fn) else 0
        P(f"- **{tag}**: {fp_cap:.0f}% token FP berawalan huruf besar; {fn_cap:.0f}% token FN berawalan huruf besar.")
    # token FP/FN paling sering (baseline winner)
    for tag in ["S4-augmentation","S1-baseline"]:
        df = examples_store[tag]
        fp_tok = Counter(df[df.cat=="FP (over-deteksi)"]["token"]).most_common(10)
        fn_tok = Counter(df[df.cat=="FN (terlewat)"]["token"]).most_common(10)
        P(f"\n**{tag}** — token FP tersering: {fp_tok}")
        P(f"**{tag}** — token FN tersering: {fn_tok}")

    # ---- proxy chunking: posisi error dalam chunk ----
    P("\n# Proxy dampak chunking: posisi token error dalam chunk\n")
    P("> Tidak ada ablation 'tanpa chunking' di eksperimen ini, jadi efek chunking diuji tak-langsung: "
      "apakah error memusat di **tepi chunk** (10% awal/akhir token) tempat konteks terpotong.\n")
    gpos = gold.set_index(["text_id"]).copy()
    P("| Skenario | err di tepi chunk (%) | err di tengah (%) |")
    P("|---|---:|---:|")
    # map (text_id, token order) — error file tak punya pos; estimasi posisi via merge urutan kemunculan token dalam chunk
    # gunakan first occurrence index dlm chunk dari gold
    gold_idx = {}
    for tid, g in gold.groupby("text_id"):
        gold_idx[tid] = {tok: i/ max(1,len(g)-1) for i,tok in zip(g["pos_in_chunk"], g["token"])}
    for tag in SC:
        if tag not in examples_store: continue
        df = examples_store[tag]
        edge=mid=0
        for tid, tok in zip(df["text_id"], df["token"]):
            rel = gold_idx.get(tid, {}).get(tok)
            if rel is None: continue
            if rel <= 0.10 or rel >= 0.90: edge+=1
            else: mid+=1
        tot = edge+mid or 1
        P(f"| {tag} | {edge/tot*100:.0f} | {mid/tot*100:.0f} |")
    P("\n_(Catatan: pemetaan posisi pakai kemunculan pertama token dalam chunk; perkiraan, bukan presisi indeks.)_")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"[OK] -> {OUT}")
    # juga print ringkasan ke stdout untuk inspeksi cepat
    print("\n".join(L[: L.index("\n\n# Ringkasan lintas skenario (token-level error)\n")+60]) if False else "")
    print("=== SUMMARY ===")
    for r in summary: print(r[:6])

if __name__ == "__main__":
    main()
