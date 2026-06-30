"""
generate_location_event_review.py
=================================
Membuat worksheet review manual untuk ambiguitas LOCATION vs EVENT.

Latar belakang
--------------
Nama lokasi medan pertempuran (Badr, Uhud, Khaibar, ...) di teks Sirah bisa
berarti DUA hal tergantung konteks kalimat:
  - LOCATION : tempat fisik   ("Nabi menuju Badr", "sumur di Badr")
  - EVENT    : peristiwa perang ("sepulang dari Badr", "kemenangan Badr")

`pre_labelling.py` (regex) SELALU menandai bentuk berdiri-sendiri sebagai
LOCATION karena nama-nama ini ada di LOCATION_EXACT. Disambiguasi kontekstual
TIDAK bisa dilakukan regex — perlu dibaca per kalimat oleh annotator.

Script ini mengekstrak SETIAP kemunculan standalone (Badr/Uhud/dst. tanpa kata
"Perang" di depan) beserta KALIMAT KONTEKS-nya, lalu menulis worksheet:
  - location_event_review.csv  -> untuk diisi kolom `keputusan` (LOCATION/EVENT)
  - location_event_review.md   -> versi enak dibaca

Heuristik `usulan` hanya PETUNJUK lemah (kata-kunci konteks), bukan keputusan.
Keputusan final ada di kolom `keputusan` yang diisi manual.

Output dipakai oleh `apply_location_event_review.py` (tahap berikutnya) untuk
meng-apply koreksi ke sirah_prelabelled.csv.
"""

import re
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_GOLD = ROOT / "data/result/manual_labelling/sirah_prelabelled.csv"
OUT_DIR = ROOT / "data/result/manual_labelling/gold_review"

# Nama medan pertempuran yang juga muncul sebagai bagian nama EVENT ("Perang X")
DUAL_TERMS = [
    "Badr", "Uhud", "Khandaq", "Khaibar", "Hunain",
    "Hudaibiyah", "Tabuk", "Ahzab", "Mu'tah", "Bu'ats", "Fijar",
]

# Kata-kunci konteks -> petunjuk lemah arah label
EVENT_HINTS = [
    "perang", "peperangan", "pertempuran", "ghazwah", "kemenangan",
    "kekalahan", "pasca", "usai", "sepulang", "sesudah", "setelah",
    "sebelum", "terjadi", "berkecamuk", "menyerang", "pasukan",
]
LOCATION_HINTS = [
    "menuju", "ke ", "di ", "dari ", "sampai", "tiba", "lembah",
    "sumur", "penduduk", "wilayah", "daerah", "kota", "kampung",
    "perkampungan", "benteng", "tanah", "jalan",
]

CTX = 90  # jumlah karakter konteks kiri/kanan


def is_bare(text: str) -> bool:
    t = text.strip().lower()
    return any(t == d.lower() for d in DUAL_TERMS)


def make_context(teks: str, start: int, end: int):
    """Ambil potongan kiri-MATCH-kanan + kalimat penuh seputar entitas."""
    s = max(0, start - CTX)
    e = min(len(teks), end + CTX)
    left = teks[s:start].replace("\n", " ").strip()
    match = teks[start:end]
    right = teks[end:e].replace("\n", " ").strip()
    # Kalimat penuh: dari titik/awal sebelum start s.d. titik setelah end
    ls = teks.rfind(".", 0, start)
    rs = teks.find(".", end)
    ls = 0 if ls < 0 else ls + 1
    rs = len(teks) if rs < 0 else rs + 1
    kalimat = teks[ls:rs].replace("\n", " ").strip()
    return left, match, right, kalimat


def suggest(kalimat: str) -> str:
    low = kalimat.lower()
    ev = sum(1 for h in EVENT_HINTS if h in low)
    lo = sum(1 for h in LOCATION_HINTS if h in low)
    if ev > lo:
        return "EVENT?"
    if lo > ev:
        return "LOCATION?"
    return "?"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_GOLD, sep=";", encoding="utf-8-sig").fillna("")
    df = df[df["label"] != ""]

    rows = []
    for _, r in df.iterrows():
        if not is_bare(str(r["entity_text"])):
            continue
        try:
            sc = int(float(r["start_char"]))
            ec = int(float(r["end_char"]))
        except (ValueError, TypeError):
            continue
        teks = str(r["teks_chunk"])
        left, match, right, kalimat = make_context(teks, sc, ec)
        rows.append({
            "chunk_id": r["chunk_id"],
            "halaman": r["halaman"],
            "entity_text": match,
            "label_sekarang": r["label"],
            "usulan_heuristik": suggest(kalimat),
            "keputusan": "",          # diisi manual: LOCATION / EVENT
            "catatan": "",            # opsional
            "kalimat_konteks": kalimat,
            "konteks_kiri": left,
            "konteks_kanan": right,
        })

    out = pd.DataFrame(rows)
    # Urutkan biar yang sejenis berdekatan -> review lebih cepat
    out = out.sort_values(["entity_text", "chunk_id"]).reset_index(drop=True)
    out.insert(0, "no", range(1, len(out) + 1))

    csv_path = OUT_DIR / "location_event_review.csv"
    out.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")

    # Versi markdown enak dibaca
    md = ["# Worksheet Review: LOCATION vs EVENT",
          "",
          f"Total kandidat: **{len(out)}** kemunculan standalone "
          "(Badr/Uhud/Khaibar/dst. tanpa kata \"Perang\" di depan).",
          "",
          "**Cara isi:** untuk tiap baris, baca `kalimat_konteks`, lalu tentukan "
          "apakah maksudnya **tempat fisik (LOCATION)** atau **peristiwa perang "
          "(EVENT)**. Isi kolom `keputusan` di file CSV "
          "(`location_event_review.csv`). Kolom `usulan_heuristik` hanya petunjuk "
          "kasar dari kata-kunci, BUKAN keputusan.",
          "",
          "Aturan ringkas (lihat `docs/anotasi_guideline.md`):",
          "- **LOCATION** kalau menunjuk tempat: \"menuju Badr\", \"di Khaibar\", "
          "\"sumur Badr\", \"penduduk Khaibar\".",
          "- **EVENT** kalau menunjuk peristiwa perangnya: \"sepulang dari Badr\", "
          "\"kemenangan di Uhud\", \"pasca Hudaibiyah\".",
          "",
          "---",
          ""]
    cur = None
    for _, r in out.iterrows():
        if r["entity_text"] != cur:
            cur = r["entity_text"]
            md.append(f"\n## {cur}\n")
        md.append(
            f"**[{r['no']}]** _(chunk {r['chunk_id']}, hal {r['halaman']}, "
            f"sekarang={r['label_sekarang']}, usul={r['usulan_heuristik']})_  \n"
            f"> {r['kalimat_konteks']}\n\n"
            f"`keputusan: ____`\n"
        )
    md_path = OUT_DIR / "location_event_review.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    print(f"Total kandidat review : {len(out)}")
    print("Distribusi usulan heuristik:")
    print(out["usulan_heuristik"].value_counts().to_string())
    print(f"\nWorksheet CSV : {csv_path}")
    print(f"Worksheet MD  : {md_path}")


if __name__ == "__main__":
    main()
