"""
build_event_period_review_v2.py
================================
Generate `event_period_review_v2.csv` — versi baru review file untuk human-in-the-loop
curation EVENT → period assignment, mengikuti periodisasi top-down (`period_mapping.json`).

Format baru:
  - 1 row per event (existing + ADD candidates)
  - Grouped & sorted by period_id (P0 → P14)
  - Pre-filled `suggested_action` berdasarkan analisis Claude (2026-05-12)
  - Kolom `ACTION` kosong untuk diisi user (K / F / R / ADD)
  - Kolom `CORRECT_PERIOD_ID` + `CORRECT_PAGES` untuk override saat F atau ADD
  - Header row dengan `period_label` + `period_pages` di tiap section

Output:
  data/result/relation_result/event_period_review_v2.csv

Idempotent. Re-run akan overwrite file (sebelum user edit).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

# Lokal import — sibling module
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from event_period import load_periods, build_event_period_map, parse_page_string

BASE_DIR = HERE.parents[1]   # ...\TA_sirah
NODES_CSV = BASE_DIR / "data" / "result" / "relation_result" / "nodes.csv"
OUT_CSV = BASE_DIR / "data" / "result" / "relation_result" / "event_period_review_v2.csv"


# ── Pre-filled suggestions dari analisis Claude (2026-05-12) ────────────────
# Format: event_name → (action, correct_period_id, correct_pages, notes)
SUGGESTIONS = {
    # Period 1
    "Perang Fijar":          ("K", "", "", "Mapping persis, score 1.0"),

    # Period 4 — Hijrah ambigu
    "Hijrah":                ("F", "P6", "218-232", "Ambigu — di Sirah biasanya merujuk Hijrah ke Madinah, bukan Habasyah. Pindah ke P6."),

    # Period 5
    "Isra' Mi'raj":          ("K", "", "", "Mapping persis"),
    "Baiat Aqabah":          ("K", "", "", "BAIAT AQABAH PERTAMA, OK"),
    "Baiat Aqabah Kubra":    ("K", "", "", "Kubra=KEDUA, OK"),

    # Period 7 — Perang Badr generic, harusnya P8
    "Perang Badr":           ("F", "P8", "266-304", "Generic 'Perang Badr' → PERANG BADR KUBRA (P8)"),

    # Period 8 — banyak noise
    "Perang Badr Aisyah":    ("R", "", "", "Noise NER: 'Aisyah' nama orang salah ter-attach"),
    "Perang Badr Beberapa":  ("R", "", "", "Noise NER: 'Beberapa' adverb"),
    "Perang Badr Kubra":     ("K", "", "", "Mapping persis"),
    "Perang Badr Shughra":   ("F", "P9", "385-389", "Shughra=Kecil, beda dgn Kubra=Besar. Map ke 'Perang Badr yang Kedua'"),
    "Perang Badr Ula":       ("F", "P9", "385-389", "Ula=Pertama, salah ke Kubra"),
    "Perang Khaibar Bekas":  ("R", "", "", "Noise: 'Bekas' tidak relevan. Kalau dipertahankan, F ke P11"),
    "Fathul Makkah":         ("F", "P12", "524-536", "Salah period — should be P12 'Penaklukan Makkah' (Pasukan Islam Masuk Makkah)"),
    "Perang Uhud":           ("F", "P9", "324-375", "Current page (305-307) = subbab transisi. Real Perang Uhud di p.324-375 (P9)"),
    "Perang Bani Qainuqa'":  ("K", "", "", "Mapping persis"),
    "Perang Asafan":         ("R", "", "", "'Asafan/Usfan tidak ada di TOC. Kalau ada konteks valid → F"),
    "Perang Safawan":        ("K", "", "", "Safawan = transliterasi varian As-Sawiq, OK"),
    "Perang Bu'ats":         ("R", "", "", "Perang Bu'ats = pra-Islam (sebelum Nabi hijrah), bukan Sirah Nabawi"),
    "Perang Bukhtanashar":   ("R", "", "", "Bukhtanashar = Nebuchadnezzar (Raja Babilonia pra-Masehi). Pasti noise"),
    "Perang Buwath":         ("K", "", "", "Buwath = Burhan? Cek konteks — kalau memang ekspedisi awal, OK"),
    "Perang Khandaq":        ("F", "P10", "390-404", "Khandaq=Ahzab, should be P10 'PERANG AHZAB ATAU KHANDAQ'"),
    "Perang Riddah":         ("R", "", "", "Perang Riddah = kemurtadan SETELAH wafat Nabi, bukan Sirah"),

    # Period 9
    "Perang Uhud Jabal":     ("K", "", "", "'Uhud Jabal'=Bukit Uhud, refer ke Perang Uhud, OK"),
    "Perang Bani Al":        ("R", "", "", "'Al' truncated NER cut, noise"),
    "Perang Bani Mushthaliq": ("F", "P10", "390-432", "Mushthaliq ≠ Nadhir. Should be P10 (Perang Khandaq hingga Bani Mushthaliq)"),
    "Perang Bani Nadhir":    ("K", "", "", "Mapping persis"),
    "Perang Dzul Usyairah":  ("F", "P8", "266-304", "Ekspedisi awal post-Hijrah, periode awal Perang Badr era. Cek halaman tepat"),

    # Period 10
    "Perang Bani Quraizhah": ("K", "", "", "Mapping persis"),

    # Period 11
    "Perjanjian Hudaibiyah": ("K", "", "", "Mapping persis"),
    "Perang Khaibar":        ("K", "", "", "PERANG KHAIBAR DAN WADIL QURA, OK"),
    "Ghazwah Dzatu Qarad":   ("F", "P11", "470-472", "Dzu Qarad ≠ Dzatur Riqa'. Ada subbab 'MANUVER MILITER SETELAH HUDAIBIYAH (PERANG GHABAH/DZU QARAD)'"),
    "Perang Dzatur Riqa'":   ("K", "", "", "Mapping persis"),

    # Period 12
    "Ghazwah Mu'tah":        ("K", "", "", "Ghazwah=Perang, OK"),
    "Perang Mu'tah":         ("K", "", "", "Mapping persis"),

    # Period 13
    "Perang Abwa'":          ("F", "P8", "266-304", "Abwa' = ekspedisi awal post-Hijrah, bukan Tabuk era. Cek halaman tepat"),
    "Perang Hunain":         ("K", "", "", "Mapping persis"),
    "Perang Tabuk":          ("K", "", "", "Mapping persis"),
    "Perang Tha'if":         ("K", "", "", "Mapping persis"),
    "Perang Yarmuk":         ("R", "", "", "Perang Yarmuk = melawan Romawi SETELAH wafat Nabi, bukan Sirah"),

    # Unmapped (page_range = nan)
    "Isra'":                 ("R", "", "", "Split duplikat dari 'Isra' Mi'raj' yang sudah ada"),
    "Mi'raj":                ("R", "", "", "Split duplikat dari 'Isra' Mi'raj' yang sudah ada"),
}


# ── ADD candidates untuk period kosong ──────────────────────────────────────
# Format: period_id → list of (event_name, pages, notes)
ADD_CANDIDATES = {
    "P0": [],   # Konteks Arab Jahiliyah — biarkan kosong (deskriptif, bukan kronologis)

    "P2": [     # Awal Kenabian & Mandat Dakwah (94-105)
        ("Wahyu Pertama", "94-99", "Turunnya wahyu pertama di Gua Hira"),
        ("Bi'tsah Nabawiyah", "94-99", "Pengangkatan Muhammad sebagai Nabi"),
    ],

    "P3": [     # Dakwah Sirriyah (106-109)
        ("Dakwah Sirriyah", "106-109", "Periode dakwah sembunyi-sembunyi 3 tahun pertama"),
    ],

    "P6": [     # Hijrah ke Madinah (214-232)
        # 'Hijrah' existing akan di-Fix ke P6 (lihat SUGGESTIONS)
        # Kandidat tambahan kalau perlu:
        # ("Hijrah ke Madinah", "218-232", "Event hijrah eksplisit (kalau 'Hijrah' di-keep di P4)"),
    ],

    "P14": [    # Masuknya Umat & Haji Wada' (576-600)
        ("Haji Wada'", "594-600", "Haji perpisahan / haji wada' Nabi"),
        ("Khutbah Wada'", "594-600", "Khutbah perpisahan Nabi di Arafah"),
        # Wafat Nabi sebenarnya di BAB 57 (p.601+) yang TIDAK masuk period_mapping.json.
        # Discuss dengan user: tambah period P15 untuk wafat, atau biarkan di luar scope.
    ],
}


# ── Main generation ──────────────────────────────────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"[load] {NODES_CSV.name}")
    nodes_df = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig")
    event_nodes = nodes_df[nodes_df["label"] == "EVENT"].copy()
    print(f"  {len(event_nodes)} EVENT nodes")

    periods = load_periods()
    print(f"[load] {len(periods)} periods")

    event_map = build_event_period_map(nodes_df, periods)
    print(f"[map ] {len(event_map)} events auto-mapped, "
          f"{len(event_nodes) - len(event_map)} unmapped (page_range nan/invalid)")

    # Group EVENT by period_id (auto-mapped from page_range)
    by_period: dict[str, list[dict]] = {p["period_id"]: [] for p in periods}
    by_period["UNMAPPED"] = []

    for _, ev in event_nodes.iterrows():
        ev_name = ev["name"]
        info = event_map.get(ev_name)
        page_range = ev.get("page_range", "")
        # Convert nan → empty string for clean CSV
        if pd.isna(page_range) if isinstance(page_range, float) else False:
            page_range = ""
        else:
            page_range = str(page_range) if not pd.isna(page_range) else ""

        period_id = info["period_id"] if info else "UNMAPPED"
        by_period[period_id].append({
            "event_name": ev_name,
            "page_range": page_range,
            "frequency": ev.get("frequency", ""),
        })

    # Build period lookup for headers
    period_info = {p["period_id"]: p for p in periods}

    # Write CSV
    rows = []
    for period in periods:
        pid = period["period_id"]
        events = by_period.get(pid, [])
        # ALWAYS include header row even for empty periods (so user sees them)
        header_label = f"=== {pid} {period['phase']} | \"{period['label']}\" (p.{period['page_start']}-{period['page_end']}) ==="

        if not events and not ADD_CANDIDATES.get(pid):
            # Period kosong, no candidates → tunjukkan dengan baris kosong
            rows.append({
                "period_id": pid,
                "period_label": period["label"],
                "phase": period["phase"],
                "period_pages": f"{period['page_start']}-{period['page_end']}",
                "event_name": "(period kosong — tidak ada EVENT auto + tidak ada ADD candidate)",
                "event_page_range": "",
                "frequency": "",
                "suggested_action": "",
                "ACTION": "",
                "CORRECT_PERIOD_ID": "",
                "CORRECT_PAGES": "",
                "NOTES": "Period descriptive, kemungkinan tidak butuh EVENT",
            })
            continue

        # Existing events
        for ev in sorted(events, key=lambda e: parse_page_string(e["page_range"])[:1] or [0]):
            suggestion = SUGGESTIONS.get(ev["event_name"], ("", "", "", ""))
            sug_action, sug_period, sug_pages, sug_notes = suggestion
            rows.append({
                "period_id": pid,
                "period_label": period["label"],
                "phase": period["phase"],
                "period_pages": f"{period['page_start']}-{period['page_end']}",
                "event_name": ev["event_name"],
                "event_page_range": ev["page_range"],
                "frequency": ev["frequency"],
                "suggested_action": sug_action,
                "ACTION": "",
                "CORRECT_PERIOD_ID": sug_period,
                "CORRECT_PAGES": sug_pages,
                "NOTES": sug_notes,
            })

        # ADD candidates
        for ev_name, pages, notes in ADD_CANDIDATES.get(pid, []):
            rows.append({
                "period_id": pid,
                "period_label": period["label"],
                "phase": period["phase"],
                "period_pages": f"{period['page_start']}-{period['page_end']}",
                "event_name": ev_name,
                "event_page_range": "",
                "frequency": "",
                "suggested_action": "ADD",
                "ACTION": "",
                "CORRECT_PERIOD_ID": pid,
                "CORRECT_PAGES": pages,
                "NOTES": f"(ADD candidate) {notes}",
            })

    # Unmapped events
    if by_period.get("UNMAPPED"):
        for ev in by_period["UNMAPPED"]:
            suggestion = SUGGESTIONS.get(ev["event_name"], ("", "", "", ""))
            sug_action, sug_period, sug_pages, sug_notes = suggestion
            rows.append({
                "period_id": "UNMAPPED",
                "period_label": "(no period — page_range invalid)",
                "phase": "",
                "period_pages": "",
                "event_name": ev["event_name"],
                "event_page_range": ev["page_range"],
                "frequency": ev["frequency"],
                "suggested_action": sug_action,
                "ACTION": "",
                "CORRECT_PERIOD_ID": sug_period,
                "CORRECT_PAGES": sug_pages,
                "NOTES": sug_notes,
            })

    # Write
    fieldnames = [
        "period_id", "period_label", "phase", "period_pages",
        "event_name", "event_page_range", "frequency",
        "suggested_action", "ACTION", "CORRECT_PERIOD_ID", "CORRECT_PAGES", "NOTES",
    ]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[write] {OUT_CSV}")
    print(f"  {len(rows)} rows total")

    # Stats
    existing = sum(1 for r in rows if r["suggested_action"] in ("K", "F", "R", ""))
    adds = sum(1 for r in rows if r["suggested_action"] == "ADD")
    by_sug = {"K": 0, "F": 0, "R": 0, "ADD": 0, "(none)": 0}
    for r in rows:
        s = r["suggested_action"] or "(none)"
        by_sug[s] = by_sug.get(s, 0) + 1
    print(f"\n  Suggestion summary:")
    for k in ("K", "F", "R", "ADD", "(none)"):
        if by_sug.get(k, 0) > 0:
            print(f"    {k:>5} : {by_sug[k]:>3} rows")


if __name__ == "__main__":
    main()
