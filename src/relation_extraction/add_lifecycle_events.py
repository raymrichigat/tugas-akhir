"""
add_lifecycle_events.py
========================
Tambah 8 life-cycle events Nabi ke nodes_v3 + auto-discover relasi
ke PERSON/LOCATION/TIME/Period yang sudah ada.

Latar belakang:
NER S3.2 menangkap 44 EVENT proper-noun-named (peperangan, perjanjian)
tapi miss life-cycle events Nabi karena disebut dalam verb-construction
("beliau wafat") atau descriptive phrase ("malam turunnya wahyu pertama"),
bukan noun phrase entity bernama.

Approach: hybrid
1. Manual definisi 8 event (label, period, page_range, anchor bab/sub-bab).
2. Auto-discover INVOLVED_IN: scan PERSON yang muncul di chunks anchor.
3. Auto-discover OCCURRED_AT: scan LOCATION yang muncul di chunks anchor.
4. Auto-discover OCCURRED_ON: scan TIME yang muncul di chunks anchor.
5. IN_PERIOD ditambahkan saat regenerate Cypher (deterministik dari period_id).

Output:
- nodes_v3.csv: +8 row EVENT baru (id, label EVENT, periode_bab, page_range)
- edges_v3.csv: +N row INVOLVED_IN/OCCURRED_AT/OCCURRED_ON
- backup .bak2 (preserve .bak existing dari period mapping run).

Idempotent. Cek apakah event sudah ada (by name) sebelum add.

Usage:
  venv/Scripts/python.exe src/relation_extraction/add_lifecycle_events.py
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

NODES_V3 = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"
EDGES_V3 = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
PRELABELLED_V3 = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "inference" / "sirah_predicted_v3_entity.csv"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"


# ── Definisi 8 life-cycle events ──────────────────────────────────────────────
LIFECYCLE_EVENTS = [
    {
        "name": "Kelahiran Nabi",
        "period_label": "Nasab & Kelahiran Nabi",
        "page_range": "73-93",
        "anchor_bab": ["KELAHIRAN DAN EMPAT PULUH TAHUN SEBELUM NUBUWAH"],
        "anchor_subbab": [],
        "page_filter": (73, 93),
    },
    {
        "name": "Wahyu Pertama",
        "period_label": "Awal Kenabian & Mandat Dakwah",
        "page_range": "94-105",
        "anchor_bab": ["DI BAWAH LINDUNGAN NUBUWAH DAN RISALAH"],
        "anchor_subbab": [],
        "page_filter": (94, 105),
    },
    {
        "name": "Hijrah Ke Habasyah",
        "period_label": "Dakwah Jahriyah & Tekanan Quraisy",
        "page_range": "133-160",
        "anchor_bab": [],
        "anchor_subbab": [
            "Hijrah ke Habasyah yang Pertama",
            "Tipu Muslihat Quraisy dalam Menghadapi Orang-Orang Muslim yang Hijrah ke Habasyah",
        ],
        "page_filter": (130, 165),
    },
    {
        "name": "Pemboikotan Bani Hasyim",
        "period_label": "Dakwah Jahriyah & Tekanan Quraisy",
        "page_range": "152-160",
        "anchor_bab": ["PEMBOIKOTAN SECARA MENYELURUH"],
        "anchor_subbab": [],
        "page_filter": (148, 165),
    },
    {
        "name": "Tahun Berduka",
        "period_label": "Dakwah Jahriyah & Tekanan Quraisy",
        "page_range": "165-175",
        "anchor_bab": ["TAHUN BERDUKA"],
        "anchor_subbab": [],
        "page_filter": (160, 180),
    },
    {
        "name": "Hijrah Ke Madinah",
        "period_label": "Hijrah ke Madinah",
        "page_range": "214-232",
        "anchor_bab": [],
        "anchor_subbab": [],  # bab varian: "PERMULAAN HIJRAH", "RASULULLAH HIJRAH"
        "anchor_bab_keywords": ["HIJRAH"],  # custom keyword filter
        "page_filter": (214, 232),
    },
    {
        "name": "Haji Wada'",
        "period_label": "Penaklukan Makkah hingga Akhir Kenabian",
        "page_range": "596-610",
        "anchor_bab": ["HAJI WADA'", "HAJI WADA’"],  # apostrof normal + curly
        "anchor_subbab": [],
        "page_filter": (590, 615),
    },
    {
        "name": "Wafat Nabi",
        "period_label": "Penaklukan Makkah hingga Akhir Kenabian",
        "page_range": "601-610",
        "anchor_bab": ["KEMBALI KE HARIBAAN ILAHI"],
        "anchor_subbab": [],
        "page_filter": (598, 615),
    },
]


def stable_id(name: str) -> str:
    """Generate 12-char hex id konsisten dengan format nodes_v3."""
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:12]


def find_anchor_chunks(chunks: pd.DataFrame, ev: dict) -> pd.DataFrame:
    """Filter chunks yang relevan untuk event ini."""
    df = chunks.copy()

    masks = []
    if ev.get("anchor_bab"):
        masks.append(df["judul_bab"].isin(ev["anchor_bab"]))
    if ev.get("anchor_subbab"):
        masks.append(df["judul_sub_bab"].isin(ev["anchor_subbab"]))
    if ev.get("anchor_bab_keywords"):
        kw_pat = "|".join(ev["anchor_bab_keywords"])
        masks.append(df["judul_bab"].str.contains(kw_pat, case=False, regex=True, na=False))

    if masks:
        # OR di antara masks
        combined = masks[0]
        for m in masks[1:]:
            combined = combined | m
        df = df[combined]

    # Page filter sebagai constraint tambahan
    if ev.get("page_filter"):
        lo, hi = ev["page_filter"]
        # Parse first page from "halaman" (mis. "266-272" -> 266)
        df = df.copy()
        df["first_page"] = df["halaman"].astype(str).str.extract(r"^(\d+)").astype(float)
        df = df[(df["first_page"] >= lo) & (df["first_page"] <= hi)]

    return df


def discover_relations(
    ev: dict,
    chunks: pd.DataFrame,
    prelabelled: pd.DataFrame,
    nodes_df: pd.DataFrame,
) -> dict[str, list[dict]]:
    """
    Auto-discover INVOLVED_IN, OCCURRED_AT, OCCURRED_ON dari entity yang
    muncul di anchor chunks.
    Return: dict[label -> list of {entity_name, count}]
    """
    anchor_chunks = find_anchor_chunks(chunks, ev)
    chunk_ids = set(anchor_chunks["chunk_id"].astype(str))

    # Filter prelabelled rows yang chunk_id-nya masuk anchor
    sub = prelabelled[prelabelled["chunk_id"].astype(str).isin(chunk_ids)]

    # Group by label
    out: dict[str, Counter] = {"PERSON": Counter(), "LOCATION": Counter(), "TIME": Counter()}

    # Build set of entity yang ada di nodes_v3 (case-sensitive name)
    valid_names_per_label = {
        label: set(nodes_df[nodes_df["label"] == label]["name"].astype(str))
        for label in ["PERSON", "LOCATION", "TIME"]
    }

    for _, row in sub.iterrows():
        ent_label = str(row.get("entity_label", "")).strip()
        ent_name = str(row.get("entity_text", "")).strip()
        if not ent_label or not ent_name:
            continue
        if ent_label not in out:
            continue
        # Normalize: title-case to match nodes_v3 convention
        # nodes_v3 punya format mixed (Title Case + alias), gunakan yang exact match
        if ent_name in valid_names_per_label[ent_label]:
            out[ent_label][ent_name] += 1

    # Convert to ordered list
    relations = {}
    for label, counter in out.items():
        relations[label] = [
            {"name": name, "count": cnt}
            for name, cnt in counter.most_common()
        ]
    return relations


def build_evidence_text(ev: dict, chunks: pd.DataFrame, ent_name: str) -> str:
    """Cari snippet text evidence pertama yang mention ent_name di anchor chunks."""
    anchor_chunks = find_anchor_chunks(chunks, ev)
    for _, row in anchor_chunks.iterrows():
        text = str(row.get("teks_chunk", ""))
        if ent_name in text:
            idx = text.find(ent_name)
            start = max(0, idx - 80)
            end = min(len(text), idx + len(ent_name) + 80)
            snippet = text[start:end].strip()
            return f"...{snippet}..."
    return ""


def main():
    print("=" * 60)
    print("ADD LIFE-CYCLE EVENTS — KG v3 enrichment")
    print("=" * 60)

    print("\n[1/6] Loading data...")
    nodes = pd.read_csv(NODES_V3, sep=";", encoding="utf-8-sig").fillna("")
    edges = pd.read_csv(EDGES_V3, sep=";", encoding="utf-8-sig").fillna("")
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig").fillna("")
    prelabelled = pd.read_csv(PRELABELLED_V3, sep=";", encoding="utf-8-sig").fillna("")

    print(f"  nodes_v3      : {len(nodes)}")
    print(f"  edges_v3      : {len(edges)}")
    print(f"  chunks        : {len(chunks)}")
    print(f"  prelabelled   : {len(prelabelled)}")

    # Backup
    print("\n[2/6] Backup (.bak2)...")
    shutil.copy2(NODES_V3, NODES_V3.with_suffix(".csv.bak2"))
    shutil.copy2(EDGES_V3, EDGES_V3.with_suffix(".csv.bak2"))
    print(f"  -> {NODES_V3.with_suffix('.csv.bak2').name}")
    print(f"  -> {EDGES_V3.with_suffix('.csv.bak2').name}")

    # Process tiap event
    new_node_rows = []
    new_edge_rows = []
    existing_event_names = set(nodes[nodes["label"] == "EVENT"]["name"].astype(str))
    summary = []

    print("\n[3/6] Processing 8 life-cycle events...")
    for ev in LIFECYCLE_EVENTS:
        name = ev["name"]
        if name in existing_event_names:
            print(f"  [SKIP] '{name}' sudah ada di nodes_v3")
            continue

        anchor_chunks = find_anchor_chunks(chunks, ev)
        n_chunks = len(anchor_chunks)
        chunk_ids_str = " | ".join(anchor_chunks["chunk_id"].astype(str).tolist())

        print(f"\n  [+] {name}")
        print(f"      anchor chunks  : {n_chunks}")
        print(f"      page_range     : {ev['page_range']}")
        print(f"      period         : {ev['period_label']}")

        node_id = stable_id(name)
        new_node_rows.append({
            "node_id": node_id,
            "name": name,
            "label": "EVENT",
            "aliases": "",
            "chunk_ids": chunk_ids_str if n_chunks <= 30 else " | ".join(
                anchor_chunks["chunk_id"].astype(str).tolist()[:30]
            ),
            "frequency": n_chunks,
            "periode_bab": ev["period_label"],
            "page_range": ev["page_range"],
        })

        # Discover relasi
        relations = discover_relations(ev, chunks, prelabelled, nodes)
        n_person = len(relations["PERSON"])
        n_loc = len(relations["LOCATION"])
        n_time = len(relations["TIME"])
        print(f"      auto-discover  : PERSON={n_person}, LOCATION={n_loc}, TIME={n_time}")

        # Build edges — filter top-K to avoid noise
        # PERSON: top-30 by count, min count 2 (untuk reduce noise pronouns)
        person_edges = [r for r in relations["PERSON"] if r["count"] >= 2][:30]
        # LOCATION: top-15, min count 1
        loc_edges = relations["LOCATION"][:15]
        # TIME: top-15, min count 1
        time_edges = relations["TIME"][:15]

        print(f"      filtered edges : PERSON={len(person_edges)}, LOCATION={len(loc_edges)}, TIME={len(time_edges)}")

        for r in person_edges:
            evidence = build_evidence_text(ev, chunks, r["name"])
            new_edge_rows.append({
                "source_name": r["name"],
                "source_label": "PERSON",
                "relation_type": "INVOLVED_IN",
                "relation_subtype": "",
                "target_name": name,
                "target_label": "EVENT",
                "chunk_id": chunk_ids_str.split(" | ")[0] if chunk_ids_str else "",
                "evidence_text": evidence[:200],
                "page_range": ev["page_range"],
                "frequency": r["count"],
                "weight": min(0.5 + 0.05 * r["count"], 1.0),
                "periode_bab": ev["period_label"],
            })

        for r in loc_edges:
            evidence = build_evidence_text(ev, chunks, r["name"])
            new_edge_rows.append({
                "source_name": name,
                "source_label": "EVENT",
                "relation_type": "OCCURRED_AT",
                "relation_subtype": "",
                "target_name": r["name"],
                "target_label": "LOCATION",
                "chunk_id": chunk_ids_str.split(" | ")[0] if chunk_ids_str else "",
                "evidence_text": evidence[:200],
                "page_range": ev["page_range"],
                "frequency": r["count"],
                "weight": min(0.5 + 0.05 * r["count"], 1.0),
                "periode_bab": ev["period_label"],
            })

        for r in time_edges:
            evidence = build_evidence_text(ev, chunks, r["name"])
            new_edge_rows.append({
                "source_name": name,
                "source_label": "EVENT",
                "relation_type": "OCCURRED_ON",
                "relation_subtype": "",
                "target_name": r["name"],
                "target_label": "TIME",
                "chunk_id": chunk_ids_str.split(" | ")[0] if chunk_ids_str else "",
                "evidence_text": evidence[:200],
                "page_range": ev["page_range"],
                "frequency": r["count"],
                "weight": min(0.5 + 0.05 * r["count"], 1.0),
                "periode_bab": ev["period_label"],
            })

        summary.append({
            "event": name,
            "anchor_chunks": n_chunks,
            "person_edges": len(person_edges),
            "location_edges": len(loc_edges),
            "time_edges": len(time_edges),
        })

    # Append + save
    print(f"\n[4/6] Appending {len(new_node_rows)} new EVENT nodes...")
    if new_node_rows:
        nodes_new = pd.concat([nodes, pd.DataFrame(new_node_rows)], ignore_index=True)
    else:
        nodes_new = nodes
    nodes_new.to_csv(NODES_V3, sep=";", encoding="utf-8-sig", index=False)
    print(f"  total nodes_v3 : {len(nodes)} -> {len(nodes_new)}")

    print(f"\n[5/6] Appending {len(new_edge_rows)} new edges...")
    if new_edge_rows:
        # Pastikan kolom new_edge_rows sama dengan edges existing
        new_edges_df = pd.DataFrame(new_edge_rows)
        # Re-align columns
        existing_cols = list(edges.columns)
        for col in existing_cols:
            if col not in new_edges_df.columns:
                new_edges_df[col] = ""
        new_edges_df = new_edges_df[existing_cols]
        edges_new = pd.concat([edges, new_edges_df], ignore_index=True)
    else:
        edges_new = edges
    edges_new.to_csv(EDGES_V3, sep=";", encoding="utf-8-sig", index=False)
    print(f"  total edges_v3 : {len(edges)} -> {len(edges_new)}")

    print(f"\n[6/6] Summary:")
    print(f"  {'Event':<30s} {'Chunks':>7s} {'Person':>7s} {'Loc':>5s} {'Time':>5s}")
    print(f"  {'-'*30} {'-'*7} {'-'*7} {'-'*5} {'-'*5}")
    for s in summary:
        print(f"  {s['event']:<30s} {s['anchor_chunks']:>7d} "
              f"{s['person_edges']:>7d} {s['location_edges']:>5d} {s['time_edges']:>5d}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
