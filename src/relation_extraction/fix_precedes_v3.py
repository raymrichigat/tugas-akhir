"""
fix_precedes_v3.py
==================
Quick fix bug PRECEDES yang teridentifikasi sebelum bimbingan 2026-05-30.

Bug:
- Perang Badr -> Fathul Makkah (salah, ada banyak event di antara)
- Fathul Makkah -> Perang Uhud (reversed; Uhud terjadi 5 tahun SEBELUM Fathul Makkah)

Akar masalah:
relation_extraction.py anchor PRECEDES ke first-mention event di teks.
"Fathul Makkah" disebut pertama kali di halaman 256 sebagai foreshadowing
(BAB "Peringatan di Makkah"), bukan event aktual yang ada di halaman 502+.

Strategi quick fix:
1. Backup edges_v3.csv ke .bak3 (sudah dilakukan manual sebelum run)
2. Drop semua existing PRECEDES edges
3. Rewrite chronology benar berdasarkan tahun H/M Sirah Mubarakfuri
4. Integrate lifecycle events (Kelahiran, Wahyu Pertama, Hijrah Madinah, dst)
5. Re-generate Cypher v3

Source-of-truth chronology (terjemahan Mubarakfuri Kathur Suhardi):
  - Pra-nubuwah: Perang Fijar (~590 M)
  - Nubuwah Makkah: Wahyu Pertama (610) -> Hijrah Habasyah (615) -> Pemboikotan
    (617-620) -> Tahun Berduka (620) -> Baiat Aqabah (621) -> Baiat Aqabah
    Kubra (622) -> Hijrah Madinah (622, akhir 13 Nubuwah)
  - Madinah peperangan: Badr (2 H, 624) -> Uhud (3 H, 625) -> Bani Nadhir (4 H,
    625) -> Khandaq (5 H, 627) -> Bani Mushthaliq (5-6 H) -> Hudaibiyah (6 H,
    628) -> Khaibar (7 H, 628) -> Mu'tah (8 H, 629) -> Fathul Makkah (8 H, 630)
    -> Hunain (8 H, 630) -> Tha'if (8 H, 630) -> Tabuk (9 H, 630)
  - Akhir: Haji Wada' (10 H, 632) -> Wafat Nabi (11 H, 632)

Idempotent. Usage:
  venv/Scripts/python.exe src/relation_extraction/fix_precedes_v3.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EDGES_V3 = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
NODES_V3 = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"


# Chronology yang benar - urutan persis sesuai sejarah Sirah
# Format: (source_event, target_event, page_anchor_for_evidence, period_label)
PRECEDES_CHRONOLOGY = [
    # Pra-nubuwah & Makkah
    ("Perang Fijar", "Wahyu Pertama", 87, "Awal Kenabian & Mandat Dakwah"),
    ("Wahyu Pertama", "Hijrah Ke Habasyah", 95, "Dakwah Jahriyah & Tekanan Quraisy"),
    ("Hijrah Ke Habasyah", "Pemboikotan Bani Hasyim", 135, "Dakwah Jahriyah & Tekanan Quraisy"),
    ("Pemboikotan Bani Hasyim", "Tahun Berduka", 153, "Dakwah Jahriyah & Tekanan Quraisy"),
    ("Tahun Berduka", "Isra' Dan Mi'Raj", 168, "Dakwah di Luar Makkah & Isra Mi'raj"),
    ("Isra' Dan Mi'Raj", "Baiat Aqabah", 191, "Dakwah di Luar Makkah & Isra Mi'raj"),
    ("Baiat Aqabah", "Baiat Aqabah Kubra", 198, "Dakwah di Luar Makkah & Isra Mi'raj"),
    ("Baiat Aqabah Kubra", "Hijrah Ke Madinah", 203, "Hijrah ke Madinah"),
    # Madinah peperangan utama
    ("Hijrah Ke Madinah", "Perang Badr", 220, "Membangun Masyarakat Madinah"),
    ("Perang Badr", "Perang Uhud", 304, "Perang Badr & Dampaknya"),
    ("Perang Uhud", "Perang Bani Nadhir", 374, "Perang Uhud & Satuan Pasukan Pasca Uhud"),
    ("Perang Bani Nadhir", "Perang Khandaq", 386, "Perang Khandaq hingga Bani Mushthaliq"),
    ("Perang Khandaq", "Perang Bani Mushthaliq", 410, "Perang Khandaq hingga Bani Mushthaliq"),
    ("Perang Bani Mushthaliq", "Perjanjian Hudaibiyah", 432, "Hudaibiyah & Babak Baru Diplomasi"),
    ("Perjanjian Hudaibiyah", "Perang Khaibar", 450, "Hudaibiyah & Babak Baru Diplomasi"),
    ("Perang Khaibar", "Perang Mu'Tah", 492, "Perang Mu'tah & Penaklukan Makkah"),
    ("Perang Mu'Tah", "Fathul Makkah", 502, "Perang Mu'tah & Penaklukan Makkah"),
    ("Fathul Makkah", "Perang Hunain", 530, "Hunain, Tabuk & Puncak Kekuatan Islam"),
    ("Perang Hunain", "Perang Tha'If", 538, "Hunain, Tabuk & Puncak Kekuatan Islam"),
    ("Perang Tha'If", "Perang Tabuk", 544, "Hunain, Tabuk & Puncak Kekuatan Islam"),
    # Akhir kenabian
    ("Perang Tabuk", "Haji Wada'", 580, "Penaklukan Makkah hingga Akhir Kenabian"),
    ("Haji Wada'", "Wafat Nabi", 605, "Penaklukan Makkah hingga Akhir Kenabian"),
]


def main():
    print("=" * 60)
    print("FIX PRECEDES BUG — KG v3")
    print("=" * 60)

    print("\n[1/4] Loading data...")
    edges = pd.read_csv(EDGES_V3, sep=";", encoding="utf-8-sig").fillna("")
    nodes = pd.read_csv(NODES_V3, sep=";", encoding="utf-8-sig").fillna("")
    print(f"  edges_v3 total: {len(edges)}")

    # Verify all events di chronology exist di nodes_v3
    print("\n[2/4] Verifying events exist in nodes_v3...")
    event_names = set(nodes[nodes["label"] == "EVENT"]["name"].astype(str))
    missing = []
    for src, tgt, _, _ in PRECEDES_CHRONOLOGY:
        if src not in event_names:
            missing.append(src)
        if tgt not in event_names:
            missing.append(tgt)
    missing = sorted(set(missing))
    if missing:
        print(f"  [WARN] {len(missing)} event di chronology TIDAK ada di nodes_v3:")
        for m in missing:
            print(f"    - {m}")
        print("  Stop. Cek nama event di chronology atau skip yang tidak ada.")
        # Tetap lanjut dengan filter
    else:
        print(f"  All {len(PRECEDES_CHRONOLOGY) * 2} event references resolved")

    # Drop existing PRECEDES
    print("\n[3/4] Dropping existing PRECEDES edges + writing new chronology...")
    n_before = (edges["relation_type"] == "PRECEDES").sum()
    edges_kept = edges[edges["relation_type"] != "PRECEDES"].copy()
    print(f"  dropped: {n_before} stale PRECEDES rows")

    # Build new PRECEDES rows
    new_rows = []
    skipped = 0
    for src, tgt, page, period in PRECEDES_CHRONOLOGY:
        if src not in event_names or tgt not in event_names:
            skipped += 1
            continue
        new_rows.append({
            "source_name": src,
            "source_label": "EVENT",
            "relation_type": "PRECEDES",
            "relation_subtype": "",
            "target_name": tgt,
            "target_label": "EVENT",
            "chunk_id": "",
            "evidence": f"{src} -> {tgt} (chronology Sirah Mubarakfuri)",
            "halaman": str(page),
            "frequency": 1,
            "weight": 1.0,
            "periode_bab": period,
        })

    print(f"  writing : {len(new_rows)} new PRECEDES rows (skipped {skipped} unresolved)")

    # Re-align columns to match existing schema
    new_df = pd.DataFrame(new_rows)
    for col in edges.columns:
        if col not in new_df.columns:
            new_df[col] = ""
    new_df = new_df[edges.columns.tolist()]

    edges_new = pd.concat([edges_kept, new_df], ignore_index=True)
    edges_new.to_csv(EDGES_V3, sep=";", encoding="utf-8-sig", index=False)
    print(f"  total edges_v3: {len(edges)} -> {len(edges_new)}")

    print("\n[4/4] Verifying new PRECEDES chain...")
    new_precedes = edges_new[edges_new["relation_type"] == "PRECEDES"]
    print(f"  total PRECEDES: {len(new_precedes)}")
    print(f"\n  Chain:")
    for _, row in new_precedes.iterrows():
        print(f"    {row['source_name']:<28s} -> {row['target_name']}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print("\nNext step: re-generate Cypher v3:")
    print("  venv/Scripts/python.exe src/neo4j/import_to_neo4j.py")


if __name__ == "__main__":
    main()
