"""
audit_gold_vs_model.py
======================
Worksheet AUDIT GOLD (tafsiran B): untuk tiap entitas yang "salah", tentukan
salahnya di bagian mana — apakah GOLD-nya yang keliru, dan kalau ya, di tahap
mana asalnya (anotasi regex kelewat / kapitalisasi / OCR boundary / honorifik /
ambiguitas LOCATION-EVENT), atau justru MODEL yang salah (gold benar).

Sinyal: ketidaksepakatan model vs gold di TEST (`test_predictions.csv`).
Kenapa pakai ini? Karena span gold yang sudah ada relatif bersih di permukaan;
error gold yang nyata justru "tak kelihatan" (entitas yang kelewat jadi O).
Disagreement model-vs-gold mem-permukaan-kan kandidat itu (mis. honorifik yang
model deteksi tapi gold=O).

Output:
  - gold_audit_summary.md  -> peta "salah di bagian mana" + jumlah per kategori
  - gold_audit.csv         -> 1 baris per token-tak-sepakat, kolom utk diisi:
        keputusan   : GOLD_SALAH / MODEL_SALAH / AMBIGU
        koreksi     : label BIO benar bila GOLD_SALAH (mis. I-PERSON / O)
        penyebab    : (terisi otomatis sbg usulan, boleh dikoreksi)
        catatan     : opsional
  - gold_audit.md          -> versi enak dibaca, dikelompokkan per kategori

Catatan cakupan: audit ini menilai gold di TEST set. Perbaikan SISTEMATIS
(honorifik, kapitalisasi, dsb.) tetap diterapkan ke SELURUH dataset via
pre_labelling.py; worksheet ini menangkap kasus konkret + memvalidasi polanya.
"""

import re
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_PRED = ROOT / "data/result/analysis/error_analysis/test_predictions.csv"
OUT_DIR = ROOT / "data/result/manual_labelling/gold_review"

CTX = 7  # token konteks kiri/kanan

HONORIFIK = {
    "shalallahu", "shallallahu", "alaihi", "wa", "sallam",
    "radhiyallahu", "anhu", "anha", "anhuma", "alaihissalam", "rahimahullah",
}
LOC_EVENT = {"badr", "uhud", "khandaq", "khaibar", "hunain",
             "hudaibiyah", "tabuk", "ahzab"}


def base(tag: str) -> str:
    """Ambil tipe entitas dari tag BIO ('B-PERSON' -> 'PERSON', 'O' -> 'O')."""
    if not tag or tag == "O":
        return "O"
    return tag.split("-", 1)[1] if "-" in tag else tag


def disagreement_type(g: str, p: str) -> str:
    ge, pe = base(g) != "O", base(p) != "O"
    if not ge and pe:
        return "A"   # gold=O, model=entitas  -> kandidat gold KELEWAT / model FP
    if ge and not pe:
        return "B"   # gold=entitas, model=O  -> kandidat gold KELEBIHAN / model FN
    return "C"        # beda tipe              -> kandidat salah-tipe


def guess_cause(token: str, g: str, p: str, dtype: str) -> str:
    """Usulan otomatis 'salah di bagian mana' (boleh dikoreksi manual)."""
    tl = token.lower().strip(".,;:!?\"'()[]")
    if tl in HONORIFIK:
        return "HONORIFIK (gold=O, harus ikut PERSON)"
    if tl in LOC_EVENT:
        return "AMBIGU_LOC_EVENT (lihat worksheet terpisah)"
    if any(c.isdigit() for c in token):
        return "OCR/ANGKA (token mengandung digit)"
    if dtype == "C":
        return "SALAH_TIPE (gold vs model beda tipe)"
    if dtype == "A":
        # gold=O tapi model deteksi entitas; kapital -> kemungkinan gold kelewat
        if token[:1].isupper():
            return "ANOTASI_KELEWAT (regex tak menangkap nama berkapital)"
        return "KAPITALISASI/huruf-kecil (gold=O, perlu cek)"
    # dtype == B: gold entitas, model O
    return "MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_PRED).fillna("O")

    # Susun konteks per text_id (urutan token sudah sekuensial di file)
    rows = []
    for tid, grp in df.groupby("text_id", sort=False):
        toks = grp["token"].tolist()
        golds = grp["gold"].tolist()
        preds = grp["pred"].tolist()
        for i, (tok, g, p) in enumerate(zip(toks, golds, preds)):
            if g == p:
                continue
            # Lewati token TANDA BACA MURNI: gold pasti O, jadi ketidaksepakatan
            # di sini = artefak model lama (dilatih pada tokenisasi lama tanpa
            # split tanda baca), BUKAN error gold. Akan hilang setelah retrain.
            if not re.search(r"[A-Za-z0-9]", tok):
                continue
            lo = max(0, i - CTX)
            hi = min(len(toks), i + CTX + 1)
            left = " ".join(toks[lo:i])
            right = " ".join(toks[i + 1:hi])
            dtype = disagreement_type(g, p)
            rows.append({
                "text_id": tid,
                "kategori": dtype,
                "token": tok,
                "gold": g,
                "model_pred": p,
                "penyebab_usulan": guess_cause(tok, g, p, dtype),
                "keputusan": "",     # GOLD_SALAH / MODEL_SALAH / AMBIGU
                "koreksi": "",       # label BIO benar bila GOLD_SALAH
                "catatan": "",
                "konteks": f"...{left} 〚{tok}〛 {right}...",
            })

    out = pd.DataFrame(rows)
    KATNAMA = {
        "A": "A. gold=O, model=ENTITAS (kandidat gold KELEWAT / model FP)",
        "B": "B. gold=ENTITAS, model=O (kandidat gold KELEBIHAN / model FN)",
        "C": "C. beda TIPE (kandidat salah-tipe)",
    }

    csv_path = OUT_DIR / "gold_audit.csv"
    out.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")

    # ── Ringkasan: peta "salah di bagian mana" ────────────────────────────────
    summ = ["# Audit Gold — \"Tiap entitas salah di bagian mana\" (tafsiran B)",
            "",
            "> ⚠️ **DIAGNOSTIK SEMENTARA — BUKAN HASIL FINAL.** Kolom prediksi berasal "
            "dari **model LAMA** (S3.2 winner di disk), dipakai HANYA sebagai alat "
            "menemukan gold yang kelewat/aneh. Setelah SEMUA model dilatih ULANG "
            "(pasca perbaikan gold), worksheet ini di-refresh dengan prediksi model "
            "BARU. Jangan dipakai sebagai angka/hasil.",
            "",
            f"Sumber sinyal: ketidaksepakatan model vs gold di TEST "
            f"(`test_predictions.csv`). Total token tak sepakat: **{len(out)}** "
            f"dari {len(df)} ({100*len(out)/len(df):.1f}%).",
            "",
            "## Distribusi per kategori ketidaksepakatan", ""]
    for k in ["A", "B", "C"]:
        summ.append(f"- **{KATNAMA[k]}** : {int((out['kategori']==k).sum())}")
    summ += ["", "## Distribusi per USULAN penyebab "
             "(\"salah di bagian mana\")", ""]
    for cause, n in out["penyebab_usulan"].value_counts().items():
        summ.append(f"- {cause} : {n}")
    summ += ["",
             "> Kolom `penyebab_usulan` = tebakan otomatis. Keputusan final diisi "
             "manual di `gold_audit.csv` (kolom `keputusan` + `koreksi`).",
             "",
             "Kategori penyebab (rujuk `docs/anotasi_guideline.md`):",
             "- **HONORIFIK** — gold=O, harusnya ikut PERSON (§1.2).",
             "- **ANOTASI_KELEWAT** — regex tak menangkap entitas (gold FN).",
             "- **AMBIGU_LOC_EVENT** — lihat worksheet `location_event_review`.",
             "- **OCR/ANGKA** — artefak OCR / token angka (§6).",
             "- **SALAH_TIPE** — tipe gold keliru.",
             "- **MODEL_MISS / gold KELEBIHAN** — perlu cek: gold benar atau model salah.",
             ""]
    (OUT_DIR / "gold_audit_summary.md").write_text("\n".join(summ), encoding="utf-8")

    # ── Versi markdown enak dibaca, per kategori ──────────────────────────────
    md = ["# Worksheet Audit Gold (detail per kasus)",
          "",
          "> ⚠️ **DIAGNOSTIK SEMENTARA (model LAMA, bukan hasil final).** Dipakai untuk "
          "menemukan gold yang kelewat/aneh sebelum retrain. Di-refresh ulang setelah "
          "semua model dilatih ulang.",
          "",
          "Untuk tiap baris: baca `konteks` (token bermasalah ditandai 〚...〛), "
          "lalu di `gold_audit.csv` isi:",
          "- `keputusan`: **GOLD_SALAH** (gold-nya keliru) / **MODEL_SALAH** "
          "(gold benar, model yang salah) / **AMBIGU**.",
          "- `koreksi`: kalau GOLD_SALAH, tulis label BIO yang benar "
          "(mis. `I-PERSON`, `B-LOCATION`, atau `O`).",
          ""]
    for k in ["A", "B", "C"]:
        sub = out[out["kategori"] == k]
        md.append(f"\n## {KATNAMA[k]} — {len(sub)} kasus\n")
        for _, r in sub.iterrows():
            md.append(
                f"**{r['token']}** (gold=`{r['gold']}` vs model=`{r['model_pred']}`) "
                f"— _usul: {r['penyebab_usulan']}_  \n"
                f"  {r['konteks']}  \n"
                f"  `keputusan: ____   koreksi: ____`\n")
    (OUT_DIR / "gold_audit.md").write_text("\n".join(md), encoding="utf-8")

    print(f"Token tak sepakat : {len(out)}")
    print("Per kategori      :",
          {k: int((out['kategori'] == k).sum()) for k in ['A', 'B', 'C']})
    print("\nTop usulan penyebab:")
    print(out["penyebab_usulan"].value_counts().to_string())
    print(f"\nOutput -> {OUT_DIR}")
    print("  gold_audit_summary.md / gold_audit.csv / gold_audit.md")


if __name__ == "__main__":
    main()
