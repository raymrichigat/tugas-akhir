"""
apply_period_to_v3.py
======================
Re-derive page_range + periode_bab di nodes_v3.csv + edges_v3.csv dengan
pendekatan v2 yang sudah di-curate manual.

Background:
relation_extraction.py default mapping pakai fuzzy match BAB title yang sering
salah (Perang Badr -> "Satuan-satuan Pasukan Sebelum Perang Badr" 256-265).
v2 sudah di-fix manual via event_period_review_v2.csv → page_range akurat
(Perang Badr 266-304).

Strategy:
  1. EVENT yang juga ada di v2 -> copy page_range dari v2 (manual-curated).
  2. EVENT baru di v3 (Perang Bu'Ats, Mu'Tah, Hunain, dll) -> derive page_range
     dari chunk_ids halaman tempat event muncul:
        - Parse halaman chunks (mis. "266-272" -> ints 266..272)
        - page_start = median - 5, page_end = median + 5
        - clamped ke 1..650 (range Sirah)
  3. Apply event_period mapping (load_periods + page_range matching)
     -> update kolom periode_bab di nodes_v3 + edges_v3.

Backup nodes_v3.csv dan edges_v3.csv ke .bak sebelum overwrite.

Idempotent. Usage:
  venv\\Scripts\\python.exe src/relation_extraction/apply_period_to_v3.py
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
NODES_V3 = RR_DIR / "nodes_v3.csv"
EDGES_V3 = RR_DIR / "edges_v3.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"


def parse_halaman(s: str) -> list[int]:
    """Parse 'halaman' string seperti '266-272' atau '34' -> list of ints."""
    if not isinstance(s, str) or not s.strip():
        return []
    out = []
    for part in re.split(r"[,;]", s):
        part = part.strip()
        m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.extend(range(a, b + 1))
        elif part.isdigit():
            out.append(int(part))
    return out


def derive_page_range_from_chunks(chunk_ids_str: str, chunk_halaman_map: dict[str, str]) -> str:
    """
    Derive page_range dari chunk_ids tempat event muncul.
    Format: 'min-max' dari union halaman semua chunks (clamp).
    """
    if not isinstance(chunk_ids_str, str) or not chunk_ids_str.strip():
        return ""
    chunk_ids = [c.strip() for c in chunk_ids_str.split("|") if c.strip()]
    all_pages: list[int] = []
    for cid in chunk_ids:
        halaman = chunk_halaman_map.get(cid, "")
        all_pages.extend(parse_halaman(halaman))
    if not all_pages:
        return ""
    # Pakai full range min-max — kalau event muncul tersebar, kemungkinan
    # mention casual di luar period utama; period mapper akan pilih period
    # yang dominan via overlap.
    return f"{min(all_pages)}-{max(all_pages)}"


def main():
    print("=" * 60)
    print("APPLY PERIOD MAPPING TO v3 (pendekatan v2 + derive baru)")
    print("=" * 60)

    print(f"\n[1/5] Load v2 nodes (page_range curated) + v3 nodes/edges + chunks...")
    v2_nodes = pd.read_csv(NODES_V2, sep=";", encoding="utf-8-sig").fillna("")
    v3_nodes = pd.read_csv(NODES_V3, sep=";", encoding="utf-8-sig").fillna("")
    v3_edges = pd.read_csv(EDGES_V3, sep=";", encoding="utf-8-sig").fillna("")
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig").fillna("")
    chunk_halaman_map = dict(zip(chunks["chunk_id"].astype(str),
                                  chunks["halaman"].astype(str)))
    print(f"  v2 nodes      : {len(v2_nodes)}")
    print(f"  v3 nodes      : {len(v3_nodes)}")
    print(f"  v3 edges      : {len(v3_edges)}")
    print(f"  chunks halaman: {len(chunk_halaman_map)}")

    # Build v2 EVENT page_range lookup (sudah curated)
    v2_event_pages = {}
    for _, row in v2_nodes[v2_nodes["label"] == "EVENT"].iterrows():
        v2_event_pages[str(row["name"]).strip()] = str(row.get("page_range", "")).strip()
    print(f"  v2 EVENT page_range curated: {len(v2_event_pages)}")

    print(f"\n[2/5] Update page_range tiap EVENT di v3...")
    stats = Counter()
    for idx, row in v3_nodes.iterrows():
        if row["label"] != "EVENT":
            continue
        name = str(row["name"]).strip()
        if name in v2_event_pages and v2_event_pages[name]:
            # Copy dari v2 (curated)
            new_pages = v2_event_pages[name]
            if str(row.get("page_range", "")).strip() != new_pages:
                v3_nodes.at[idx, "page_range"] = new_pages
                stats["copied_from_v2"] += 1
            else:
                stats["already_correct"] += 1
        else:
            # Event baru di v3 - derive dari chunk halaman
            chunk_ids = str(row.get("chunk_ids", ""))
            new_pages = derive_page_range_from_chunks(chunk_ids, chunk_halaman_map)
            if new_pages:
                v3_nodes.at[idx, "page_range"] = new_pages
                stats["derived_new_event"] += 1
                print(f"    + {name:<35s} page_range derived: {new_pages}")
            else:
                stats["no_chunks"] += 1
                print(f"    ! {name:<35s} no chunks, skip")

    print(f"  copied_from_v2     : {stats['copied_from_v2']}")
    print(f"  already_correct    : {stats['already_correct']}")
    print(f"  derived_new_event  : {stats['derived_new_event']}")
    print(f"  no_chunks (skip)   : {stats['no_chunks']}")

    print(f"\n[3/5] Build event_period_map dari page_range yang sudah ke-update...")
    periods = load_periods()
    event_period_map = build_event_period_map(v3_nodes, periods)
    print(f"  EVENT mapped: {len(event_period_map)} / "
          f"{(v3_nodes['label'] == 'EVENT').sum()}")

    unmapped = [n for n in v3_nodes[v3_nodes["label"] == "EVENT"]["name"]
                if str(n).strip() not in event_period_map]
    if unmapped:
        print(f"  unmapped: {len(unmapped)}")
        for name in unmapped[:5]:
            print(f"    - {name}")

    print(f"\n[4/5] Update periode_bab di nodes_v3 + edges_v3...")
    n_nodes_updated = 0
    for idx, row in v3_nodes.iterrows():
        if row["label"] != "EVENT":
            continue
        name = str(row["name"]).strip()
        if name in event_period_map:
            new_label = event_period_map[name]["label"]
            if str(row["periode_bab"]).strip() != new_label:
                v3_nodes.at[idx, "periode_bab"] = new_label
                n_nodes_updated += 1
    print(f"  nodes updated: {n_nodes_updated}")

    n_edges_updated = 0
    for idx, row in v3_edges.iterrows():
        ev_name = None
        if row["source_label"] == "EVENT":
            ev_name = str(row["source_name"]).strip()
        elif row["target_label"] == "EVENT":
            ev_name = str(row["target_name"]).strip()
        if ev_name and ev_name in event_period_map:
            new_label = event_period_map[ev_name]["label"]
            if str(row["periode_bab"]).strip() != new_label:
                v3_edges.at[idx, "periode_bab"] = new_label
                n_edges_updated += 1
    print(f"  edges updated: {n_edges_updated}")

    print(f"\n[5/5] Backup + write...")
    for csv_path in (NODES_V3, EDGES_V3):
        backup = csv_path.with_suffix(".csv.bak")
        shutil.copy2(csv_path, backup)
        print(f"  backup -> {backup}")

    v3_nodes.to_csv(NODES_V3, sep=";", encoding="utf-8-sig", index=False)
    v3_edges.to_csv(EDGES_V3, sep=";", encoding="utf-8-sig", index=False)
    print(f"  -> {NODES_V3}")
    print(f"  -> {EDGES_V3}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    print("\nDistribusi EVENT per period (post-update):")
    ev = v3_nodes[v3_nodes["label"] == "EVENT"]
    for label, cnt in ev["periode_bab"].value_counts().items():
        print(f"  {label:<55s} {cnt}")


if __name__ == "__main__":
    main()
