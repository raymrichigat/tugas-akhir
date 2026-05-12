"""
apply_review_to_kg.py
=====================
Terapkan hasil review periodisasi (event_period_review_v2.csv) ke nodes.csv + edges.csv.

Produces:
  - data/result/relation_result/nodes_v2.csv
  - data/result/relation_result/edges_v2.csv
  - data/result/relation_result/review_apply_log.md (catatan perubahan)

Action mapping:
  K (Keep)   → nothing changes
  F (Fix)    → update kolom `periode_bab` (= period_label baru) di nodes & edges
  R (Remove) → drop EVENT node dari nodes.csv + drop semua edges yang mention event itu
  ADD        → tambah ghost EVENT node baru (chunk_ids='', frequency=0, page_range=CORRECT_PAGES)

Schema tetap (backward-compatible):
  nodes.csv: node_id;name;label;aliases;chunk_ids;frequency;periode_bab;page_range
  edges.csv: source_name;source_label;relation_type;relation_subtype;target_name;target_label;
             chunk_id;evidence;halaman;frequency;weight;periode_bab

Catatan semantik:
  Kolom `periode_bab` dulu berisi judul BAB hasil fuzzy match. Sekarang berisi
  `period_label` (mis. "Perang Badr & Dampaknya") dari period_mapping.json v2.
  Schema tidak berubah, hanya isi-nya semantically beda → kalau downstream code
  cuma display kolom ini, masih jalan.

Idempotent. Usage:
  python apply_review_to_kg.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

# Sibling import
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from event_period import (
    load_periods, load_review, apply_review,
    BASE_DIR,
)

NODES_IN = BASE_DIR / "data" / "result" / "relation_result" / "nodes.csv"
EDGES_IN = BASE_DIR / "data" / "result" / "relation_result" / "edges.csv"
NODES_OUT = BASE_DIR / "data" / "result" / "relation_result" / "nodes_v2.csv"
EDGES_OUT = BASE_DIR / "data" / "result" / "relation_result" / "edges_v2.csv"
LOG_OUT = BASE_DIR / "data" / "result" / "relation_result" / "review_apply_log.md"


def _gen_node_id(name: str, label: str) -> str:
    """Hash pendek (12 hex char) untuk node_id baru, konsisten dengan existing."""
    h = hashlib.md5(f"{name}|{label}".encode("utf-8")).hexdigest()
    return h[:12]


def apply_to_nodes(nodes_df: pd.DataFrame,
                   event_period_map: dict,
                   removed_events: set,
                   added_events: list,
                   ) -> tuple[pd.DataFrame, dict]:
    """
    Returns:
        df_out      : nodes_v2 DataFrame
        stats       : dict {kept, fixed, removed, added}
    """
    stats = {"kept": 0, "fixed": 0, "removed": 0, "added": 0, "untouched_non_event": 0}

    out_rows = []
    for _, row in nodes_df.iterrows():
        name = str(row["name"]).strip()
        label = str(row["label"]).strip()

        if label != "EVENT":
            out_rows.append(row.to_dict())
            stats["untouched_non_event"] += 1
            continue

        # EVENT node
        if name in removed_events:
            stats["removed"] += 1
            continue

        if name in event_period_map:
            info = event_period_map[name]
            new_row = row.to_dict()
            new_row["periode_bab"] = info["label"]   # rewrite semantically
            # Kalau ada `correct_pages` (dari F atau ADD), update page_range
            if "correct_pages" in info and info["correct_pages"]:
                new_row["page_range"] = info["correct_pages"]
            out_rows.append(new_row)
            if info.get("source") == "F":
                stats["fixed"] += 1
            else:
                stats["kept"] += 1
        else:
            # EVENT tidak ada di event_period_map (mungkin blank action) — keep as-is
            out_rows.append(row.to_dict())
            stats["kept"] += 1

    # ADD events sebagai ghost nodes
    existing_names = {str(r["name"]).strip() for r in out_rows if str(r.get("label", "")).strip() == "EVENT"}
    for entry in added_events:
        ev_name = entry["event_name"]
        if ev_name in existing_names:
            continue   # already exists somehow
        out_rows.append({
            "node_id": _gen_node_id(ev_name, "EVENT"),
            "name": ev_name,
            "label": "EVENT",
            "aliases": "",
            "chunk_ids": "",        # ghost node — tidak ada chunk evidence
            "frequency": 0,
            "periode_bab": entry["period_label"],
            "page_range": entry.get("correct_pages", ""),
        })
        stats["added"] += 1

    df_out = pd.DataFrame(out_rows, columns=nodes_df.columns)
    return df_out, stats


def apply_to_edges(edges_df: pd.DataFrame,
                   event_period_map: dict,
                   removed_events: set,
                   ) -> tuple[pd.DataFrame, dict]:
    """
    Returns:
        df_out  : edges_v2 DataFrame
        stats   : dict {kept, fixed_period, removed_by_node}
    """
    stats = {"kept": 0, "fixed_period": 0, "removed_by_node": 0}

    out_rows = []
    for _, row in edges_df.iterrows():
        src_name = str(row["source_name"]).strip()
        src_label = str(row["source_label"]).strip()
        tgt_name = str(row["target_name"]).strip()
        tgt_label = str(row["target_label"]).strip()

        # Drop edge kalau source/target dihapus
        if (src_label == "EVENT" and src_name in removed_events) or \
           (tgt_label == "EVENT" and tgt_name in removed_events):
            stats["removed_by_node"] += 1
            continue

        new_row = row.to_dict()

        # Update periode_bab kolom berdasarkan event (kalau ada salah satu adalah EVENT)
        event_name = None
        if src_label == "EVENT":
            event_name = src_name
        elif tgt_label == "EVENT":
            event_name = tgt_name

        if event_name and event_name in event_period_map:
            info = event_period_map[event_name]
            old_periode = str(row.get("periode_bab", "")).strip()
            new_periode = info["label"]
            if old_periode != new_periode:
                new_row["periode_bab"] = new_periode
                stats["fixed_period"] += 1
            else:
                stats["kept"] += 1
        else:
            stats["kept"] += 1

        out_rows.append(new_row)

    df_out = pd.DataFrame(out_rows, columns=edges_df.columns)
    return df_out, stats


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    # Load source
    print(f"[load] {NODES_IN.name}")
    nodes_df = pd.read_csv(NODES_IN, sep=";", encoding="utf-8-sig")
    print(f"  {len(nodes_df)} nodes (EVENT={(nodes_df['label']=='EVENT').sum()})")

    print(f"[load] {EDGES_IN.name}")
    edges_df = pd.read_csv(EDGES_IN, sep=";", encoding="utf-8-sig")
    print(f"  {len(edges_df)} edges")

    # Load periods + review
    periods = load_periods()
    review_df = load_review()
    print(f"[load] {len(periods)} periods, {len(review_df)} review rows")

    # Apply review → get cleaned event_period_map
    event_period_map, removed_events, added_events = apply_review(review_df, periods)
    print(f"\n[review] {len(event_period_map)} events in cleaned map "
          f"({len(removed_events)} removed, {len(added_events)} added)")

    # Apply to nodes & edges
    nodes_v2, node_stats = apply_to_nodes(nodes_df, event_period_map, removed_events, added_events)
    edges_v2, edge_stats = apply_to_edges(edges_df, event_period_map, removed_events)

    # Stats
    print(f"\n[nodes_v2] {len(nodes_v2)} rows")
    print(f"  kept EVENT       : {node_stats['kept']}")
    print(f"  fixed EVENT      : {node_stats['fixed']}")
    print(f"  removed EVENT    : {node_stats['removed']}")
    print(f"  added EVENT (ghost): {node_stats['added']}")
    print(f"  non-EVENT untouched: {node_stats['untouched_non_event']}")

    print(f"\n[edges_v2] {len(edges_v2)} rows")
    print(f"  kept           : {edge_stats['kept']}")
    print(f"  period updated : {edge_stats['fixed_period']}")
    print(f"  removed by node: {edge_stats['removed_by_node']}")

    # Write
    nodes_v2.to_csv(NODES_OUT, sep=";", index=False, encoding="utf-8-sig")
    edges_v2.to_csv(EDGES_OUT, sep=";", index=False, encoding="utf-8-sig")
    print(f"\n[write] {NODES_OUT.name}")
    print(f"[write] {EDGES_OUT.name}")

    # Write markdown log
    lines = [
        "# Apply Review to KG — Log",
        "",
        f"**Source files:** `{NODES_IN.name}`, `{EDGES_IN.name}`",
        f"**Review file:** `event_period_review_v2.csv`",
        f"**Output files:** `{NODES_OUT.name}`, `{EDGES_OUT.name}`",
        "",
        "## Nodes Changes",
        "",
        f"| Action | Count |",
        f"|---|---:|",
        f"| EVENT keep        | {node_stats['kept']} |",
        f"| EVENT fixed (F)   | {node_stats['fixed']} |",
        f"| EVENT removed (R) | {node_stats['removed']} |",
        f"| EVENT added (ADD) | {node_stats['added']} |",
        f"| non-EVENT untouched | {node_stats['untouched_non_event']} |",
        f"| **Total nodes_v2** | **{len(nodes_v2)}** |",
        "",
        "## Edges Changes",
        "",
        f"| Action | Count |",
        f"|---|---:|",
        f"| keep                  | {edge_stats['kept']} |",
        f"| period_label updated  | {edge_stats['fixed_period']} |",
        f"| removed (event R'd)   | {edge_stats['removed_by_node']} |",
        f"| **Total edges_v2** | **{len(edges_v2)}** |",
        "",
        "## Events Removed (R)",
        "",
    ]
    for name in sorted(removed_events):
        lines.append(f"- `{name}`")
    lines.append("")
    lines.append("## Events Added (ADD, ghost nodes)")
    lines.append("")
    for entry in added_events:
        lines.append(f"- `{entry['event_name']}` → **{entry['period_id']}** ({entry['period_label']}, p.{entry['correct_pages']})")
    lines.append("")
    lines.append("## Events Fixed (F)")
    lines.append("")
    for name, info in sorted(event_period_map.items()):
        if info.get("source") == "F":
            lines.append(f"- `{name}` → **{info['period_id']}** ({info['label']}, p.{info['page_start']}-{info['page_end']})")
    lines.append("")

    LOG_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[write] {LOG_OUT.name}")


if __name__ == "__main__":
    main()
