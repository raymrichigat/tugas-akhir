"""Hitung validitas semantis KG (Bu Nanik #8 / Temuan #3).

Membaca worksheet F1/F2/F4 yang sudah diisi kolom `valid_(1=ya/0=tidak)`,
menggabungkan dengan F3/F5/F6 yang sudah divalidasi di buku, lalu menulis
tabel ringkasan siap-tempel ke Bab 4.

Jalankan: venv/Scripts/python.exe src/analysis/hitung_validitas_semantis.py
"""
import pandas as pd, os

WS = "docs/revisi/artefak/validitas_semantis"
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
VALCOL = "valid_(1=ya/0=tidak)"


def score_ws(f):
    """Baca worksheet: utamakan *_worksheet_validated.xlsx (hasil isian user), fallback CSV."""
    xlsx = os.path.join(WS, f"{f}_worksheet_validated.xlsx")
    csv = os.path.join(WS, f"{f}_worksheet.csv")
    if os.path.exists(xlsx):
        df, src = pd.read_excel(xlsx), os.path.basename(xlsx)
    else:
        df, src = pd.read_csv(csv), os.path.basename(csv)
    total = len(df)
    filled = pd.to_numeric(df[VALCOL], errors="coerce")
    n_filled = filled.notna().sum()
    valid = int((filled == 1).sum())
    return valid, total, int(n_filled), src


rows, incomplete = [], []
for f in ["F1", "F2", "F3", "F4", "F5", "F6"]:
    if f in FIXED:
        v, t = FIXED[f]
        rows.append((f, QUESTION[f], v, t, v / t * 100, "buku"))
    else:
        v, t, nf, src = score_ws(f)
        if nf < t:
            incomplete.append(f"{f}: baru {nf}/{t} baris terisi")
        rows.append((f, QUESTION[f], v, t, (v / t * 100) if t else 0, src))

sum_v = sum(r[2] for r in rows)
sum_t = sum(r[3] for r in rows)

lines = ["# Hasil Evaluasi Validitas Semantis Knowledge Graph", ""]
if incomplete:
    lines += ["> ⚠️ **BELUM LENGKAP** (angka F1/F2/F4 sementara): " + "; ".join(incomplete), ""]
lines += [
    "| Fungsi | Pertanyaan | Jawaban valid | Total jawaban | Validitas semantis |",
    "|---|---|---:|---:|---:|",
]
for f, q, v, t, pct, src in rows:
    lines.append(f"| {f} | {q} | {v} | {t} | {pct:.2f}% |")
lines.append(f"| **Total** | — | **{sum_v}** | **{sum_t}** | **{sum_v/sum_t*100:.2f}%** |")
lines += [
    "",
    "Validitas semantis = (jawaban didukung teks sumber ÷ seluruh jawaban diperiksa) × 100%. "
    "Unit F5 = 21 jalur yang dikembalikan kueri (bukan 15 lokasi unik).",
    "",
    "**Interpretasi:** seluruh kueri dapat dijalankan (layak operasional), namun sebagian jawaban "
    "belum didukung teks sumber sehingga graf lebih tepat untuk penelusuran awal dengan verifikasi "
    "terhadap sumber.",
]
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("Ditulis:", OUT)
if incomplete:
    print("CATATAN:", "; ".join(incomplete))
