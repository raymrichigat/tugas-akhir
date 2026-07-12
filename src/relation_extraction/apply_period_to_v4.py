"""
apply_period_to_v4.py
======================
Terapkan pemetaan periode kanonik ke EVENT KG v4_hybrid, meniru
`apply_period_to_v3.py`. Diperlukan karena `periode_bab` event v4 masih berupa
judul bab MENTAH hasil fuzzy-match (mis. Perang Badr -> "Satuan-satuan Pasukan
Sebelum Perang Badr"), sehingga 0/… cocok ke `period_mapping.json` dan skenario
G8 (keterlibatan lintas fase) tak bisa dihitung.

Strategi (identik v3):
  1. EVENT yang juga ada di v2 -> copy page_range CURATED dari nodes_v2.csv.
  2. EVENT lain -> derive page_range dari halaman chunk kemunculannya.
  3. build_event_period_map (overlap page_range vs period) -> update kolom
     `periode_bab` di nodes_v4_hybrid + edges_v4_hybrid dengan LABEL periode kanonik.

Backup *.csv.bak_period. Idempotent.
Usage:
  venv\\Scripts\\python.exe src/relation_extraction/apply_period_to_v4.py
"""

from __future__ import annotations

import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from event_period import load_periods, build_event_period_map  # noqa: E402

ROOT = HERE.parents[1]
RR_DIR = ROOT / "data" / "result" / "relation_result"
NODES_V2 = RR_DIR / "nodes_v2.csv"
NODES_V4 = RR_DIR / "nodes_v4_hybrid.csv"
EDGES_V4 = RR_DIR / "edges_v4_hybrid.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"


def parse_halaman(s: str) -> list[int]:
    if not isinstance(s, str) or not s.strip():
        return []
    out = []
    for part in re.split(r"[,;]", s):
        part = part.strip()
        m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", part)
        if m:
            out.extend(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out


def derive_page_range_from_chunks(chunk_ids_str: str, chunk_halaman_map: dict) -> str:
    if not isinstance(chunk_ids_str, str) or not chunk_ids_str.strip():
        return ""
    chunk_ids = [c.strip() for c in chunk_ids_str.split("|") if c.strip()]
    all_pages: list[int] = []
    for cid in chunk_ids:
        all_pages.extend(parse_halaman(chunk_halaman_map.get(cid, "")))
    if not all_pages:
        return ""
    return f"{min(all_pages)}-{max(all_pages)}"


def main():
    print("=" * 60)
    print("APPLY PERIOD MAPPING TO v4_hybrid (curated v2 + derive)")
    print("=" * 60)

    v2 = pd.read_csv(NODES_V2, sep=";", encoding="utf-8-sig").fillna("")
    nodes = pd.read_csv(NODES_V4, sep=";", encoding="utf-8-sig").fillna("")
    edges = pd.read_csv(EDGES_V4, sep=";", encoding="utf-8-sig").fillna("")
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig").fillna("")
    chmap = dict(zip(chunks["chunk_id"].astype(str), chunks["halaman"].astype(str)))

    v2_pages = {str(r["name"]).strip(): str(r.get("page_range", "")).strip()
                for _, r in v2[v2["label"] == "EVENT"].iterrows()}

    stats = Counter()
    for idx, row in nodes.iterrows():
        if row["label"] != "EVENT":
            continue
        name = str(row["name"]).strip()
        if v2_pages.get(name):
            nodes.at[idx, "page_range"] = v2_pages[name]; stats["from_v2"] += 1
        else:
            pr = derive_page_range_from_chunks(str(row.get("chunk_ids", "")), chmap)
            if pr:
                nodes.at[idx, "page_range"] = pr; stats["derived"] += 1
            else:
                stats["no_pages"] += 1
    print(f"  page_range: from_v2={stats['from_v2']} derived={stats['derived']} no_pages={stats['no_pages']}")

    periods = load_periods()
    epm = build_event_period_map(nodes, periods)
    n_ev = int((nodes["label"] == "EVENT").sum())
    print(f"  EVENT mapped ke period: {len(epm)} / {n_ev}")
    unmapped = [n for n in nodes[nodes["label"] == "EVENT"]["name"] if str(n).strip() not in epm]
    if unmapped:
        print(f"  unmapped ({len(unmapped)}): {unmapped[:8]}")

    n_up = 0
    for idx, row in nodes.iterrows():
        if row["label"] != "EVENT":
            continue
        name = str(row["name"]).strip()
        if name in epm and str(row["periode_bab"]).strip() != epm[name]["label"]:
            nodes.at[idx, "periode_bab"] = epm[name]["label"]; n_up += 1
    e_up = 0
    for idx, row in edges.iterrows():
        ev = None
        if row["source_label"] == "EVENT":
            ev = str(row["source_name"]).strip()
        elif row["target_label"] == "EVENT":
            ev = str(row["target_name"]).strip()
        if ev and ev in epm and str(row["periode_bab"]).strip() != epm[ev]["label"]:
            edges.at[idx, "periode_bab"] = epm[ev]["label"]; e_up += 1
    print(f"  nodes periode_bab updated: {n_up} | edges: {e_up}")

    shutil.copy2(NODES_V4, NODES_V4.with_suffix(".csv.bak_period"))
    shutil.copy2(EDGES_V4, EDGES_V4.with_suffix(".csv.bak_period"))
    nodes.to_csv(NODES_V4, sep=";", encoding="utf-8-sig", index=False)
    edges.to_csv(EDGES_V4, sep=";", encoding="utf-8-sig", index=False)
    print("  [OK] ditulis (backup *.csv.bak_period)")

    print("\nDistribusi EVENT per period:")
    for label, cnt in nodes[nodes["label"] == "EVENT"]["periode_bab"].value_counts().items():
        print(f"  {str(label)[:52]:<52s} {cnt}")


if __name__ == "__main__":
    main()
