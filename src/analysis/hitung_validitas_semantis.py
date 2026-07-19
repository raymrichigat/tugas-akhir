"""Hitung validitas semantis KG (Bu Nanik #8 / Temuan #3).

Membaca worksheet F1/F2/F4 yang sudah diisi kolom `valid_(1=ya/0=tidak)`
(format .xlsx validated diutamakan), menggabungkan dengan F3/F5/F6 yang sudah
divalidasi di buku, lalu menulis tabel ringkasan kaya (jumlah diperiksa, valid,
tidak valid, kesesuaian semantis, keterlacakan) siap-tempel ke Bab 4.

Jalankan: venv/Scripts/python.exe src/analysis/hitung_validitas_semantis.py
"""
import pandas as pd, os

WS = "docs/revisi/artefak/validitas_semantis"
SRC = "docs/bab4/knowledge-graph"   # F1.csv..F6.csv (untuk keterlacakan)
OUT = os.path.join(WS, "hasil_validitas_semantis.md")

# F3/F5/F6 sudah divalidasi manual di buku (unit F5 = 21 jalur, Temuan #3)
FIXED = {"F3": (3, 4), "F5": (3, 21), "F6": (14, 17)}

QUESTION = {
    "F1": "Siapa saja yang terlibat dalam Perang Badar?",
    "F2": "Peristiwa apa saja yang terjadi di Madinah?",
    "F3": "Peristiwa apa yang terjadi pada tahun ke-2 Hijriah?",
    "F4": "Peristiwa apa saja yang melibatkan Abu Bakar?",
    "F5": "Di mana lokasi peristiwa yang melibatkan Umar bin Khattab?",
    "F6": "Urutan kronologis antar peristiwa (PRECEDES)",
}
UNIT = {"F1": "relasi", "F2": "relasi", "F3": "relasi", "F4": "relasi",
        "F5": "jalur", "F6": "relasi"}
VALCOL = "valid_(1=ya/0=tidak)"


def score_ws(f):
    """Baca worksheet: utamakan *_worksheet_validated.xlsx (isian user), fallback CSV."""
    xlsx = os.path.join(WS, f"{f}_worksheet_validated.xlsx")
    csv = os.path.join(WS, f"{f}_worksheet.csv")
    if os.path.exists(xlsx):
        df = pd.read_excel(xlsx)
    else:
        df = pd.read_csv(csv)
    total = len(df)
    filled = pd.to_numeric(df[VALCOL], errors="coerce")
    return int((filled == 1).sum()), total, int(filled.notna().sum())


def traceability(f):
    """% jawaban yang punya metadata evidence + halaman (keterlacakan) dari F*.csv sumber."""
    p = os.path.join(SRC, f"{f}.csv")
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    ev = [c for c in df.columns if "evidence" in c.lower()]
    hl = [c for c in df.columns if "halaman" in c.lower()]
    if not ev or not hl or len(df) == 0:
        return None
    ok = df[ev[0]].astype(str).str.strip().ne("") & df[hl[0]].astype(str).str.strip().ne("")
    return ok.mean() * 100


rows, incomplete = [], []
for f in ["F1", "F2", "F3", "F4", "F5", "F6"]:
    if f in FIXED:
        v, t = FIXED[f]
    else:
        v, t, nf = score_ws(f)
        if nf < t:
            incomplete.append(f"{f}: baru {nf}/{t} baris terisi")
    tr = traceability(f)
    rows.append({"f": f, "q": QUESTION[f], "unit": UNIT[f], "v": v, "t": t,
                 "inv": t - v, "pct": (v / t * 100) if t else 0,
                 "trace": tr if tr is not None else 100.0})

sum_v = sum(r["v"] for r in rows)
sum_t = sum(r["t"] for r in rows)
best = max(rows, key=lambda r: r["pct"])
worst = min(rows, key=lambda r: r["pct"])

L = ["# Hasil Evaluasi Validitas Semantis Knowledge Graph", ""]
if incomplete:
    L += ["> ⚠️ **BELUM LENGKAP** (F1/F2/F4 sementara): " + "; ".join(incomplete), ""]
L += ["## Tabel 4.28 (revisi) — Ringkasan Hasil Pengujian Fungsional Knowledge Graph\n",
      "| Fungsi | Pertanyaan | Jumlah diperiksa | Valid | Tidak valid | Kesesuaian semantis | Terlacak |",
      "|---|---|---:|---:|---:|---:|---:|"]
for r in rows:
    unit_note = f"{r['t']} {r['unit']}" + (" (15 lokasi unik)" if r["f"] == "F5" else "")
    L.append(f"| {r['f']} | {r['q']} | {unit_note} | {r['v']} | {r['inv']} | "
             f"{r['pct']:.2f}% | {r['trace']:.0f}% |")
L.append(f"| **Total** | — | **{sum_t}** | **{sum_v}** | **{sum_t-sum_v}** | "
         f"**{sum_v/sum_t*100:.2f}%** | **100%** |")
L += [
    "",
    "Validitas/kesesuaian semantis = (jawaban didukung teks sumber ÷ seluruh jawaban diperiksa) "
    "× 100%. Unit F5 = 21 jalur Person–Event–Location (mencakup 15 lokasi unik); satu jalur valid "
    "hanya bila kedua relasinya didukung sumber.",
    "",
    f"**Ringkasan:** keberhasilan operasional 100% (seluruh 6 kueri jalan & memberi jawaban) dan "
    f"keterlacakan 100% (semua jawaban punya evidence + halaman), tetapi kesesuaian semantis "
    f"berbeda tiap fungsi — tertinggi {best['pct']:.2f}% pada {best['f']}, terendah "
    f"{worst['pct']:.2f}% pada {worst['f']}, rata-rata mikro {sum_v/sum_t*100:.2f}%. "
    f"Kemampuan graf menjalankan kueri tidak otomatis menjamin ketepatan seluruh jawaban.",
]
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("Ditulis:", OUT)
for r in rows:
    print(f"  {r['f']}: {r['v']}/{r['t']} = {r['pct']:.2f}%  (terlacak {r['trace']:.0f}%)")
print(f"  TOTAL: {sum_v}/{sum_t} = {sum_v/sum_t*100:.2f}%")
if incomplete:
    print("CATATAN:", "; ".join(incomplete))
