"""
clean_v4_events.py
==================
Bersihkan node EVENT KG v4_hybrid (dedup alias bentuk-pendek + buang FP) supaya
setara kebersihan v3. Analog `clean_v3_nodes.py` OP1/OP2/OP3 tetapi khusus EVENT.

Operasi:
  MERGE  — gabung nama bentuk-pendek ke kanonik penuh (mis. "Uhud"->"Perang Uhud",
           "Isra'"/"Mi'raj"/"Isra' Dan Mi'raj"->"Isra' Mi'raj", "Hudaibiyah"->
           "Perjanjian Hudaibiyah"). Chunk_ids + aliases + frequency di-union;
           semua edge yang menyentuhnya di-remap ke node kanonik.
  DROP   — buang node EVENT false-positive {Al-Umawi} (nisba/rujukan, bukan
           peristiwa) + edge yang menyentuhnya. Manifestasi precision EVENT.

SENGAJA TIDAK di-merge (keputusan historis, sama dgn v3 REVIEW):
  Perang Badr Kubra / Ula / Shughra  = pertempuran berbeda (Badr besar/awal/kecil).
  Baiat Aqabah / Baiat Aqabah Kubra  = baiat pertama vs kedua (kedua = Kubra).
  Post-Sirah (Yarmuk, Yamamah, Riddah) = peristiwa nyata yg disebut, dipertahankan.

CATATAN: operasi di tahap konstruksi KG (hilir), F1 NER tidak terpengaruh.
Idempotent. Backup *.csv.bak_events. Preview default; --apply untuk eksekusi.

Usage:
  venv/Scripts/python.exe src/relation_extraction/clean_v4_events.py
  venv/Scripts/python.exe src/relation_extraction/clean_v4_events.py --apply
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
RR = ROOT / "data" / "result" / "relation_result"
NODES = RR / "nodes_v4_hybrid.csv"
EDGES = RR / "edges_v4_hybrid.csv"

# nama bentuk-pendek EVENT -> kanonik penuh
EVENT_MERGE = {
    "Badr": "Perang Badr",
    "Uhud": "Perang Uhud",
    "Khaibar": "Perang Khaibar",
    "Hunain": "Perang Hunain",
    "Hudaibiyah": "Perjanjian Hudaibiyah",
    "Hamra'ul Asad": "Perang Hamra'ul Asad",
    "Isra'": "Isra' Mi'raj",
    "Mi'raj": "Isra' Mi'raj",
    "Isra' Dan Mi'raj": "Isra' Mi'raj",
}
EVENT_DROP = {"Al-Umawi"}

ALIASES_SEP = " | "
CHUNK_SEP = "|"


def split_chunks(s: str) -> list[str]:
    return [c.strip() for c in str(s).split(CHUNK_SEP) if c.strip()]


def split_aliases(s: str) -> list[str]:
    return [a.strip() for a in str(s).split("|") if a.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description="Bersihkan node EVENT KG v4_hybrid (dedup + FP)")
    ap.add_argument("--apply", action="store_true", help="Tulis ke nodes/edges_v4_hybrid (default: preview)")
    args = ap.parse_args()
    DRY = not args.apply

    print("=" * 64)
    print(f"CLEAN v4_hybrid EVENT   [{'PREVIEW' if DRY else 'APPLY'}]")
    print("=" * 64)

    nodes = pd.read_csv(NODES, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    edges = pd.read_csv(EDGES, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    n0, e0 = len(nodes), len(edges)
    ev0 = (nodes["label"] == "EVENT").sum()
    print(f"\nLoaded: {n0} nodes ({ev0} EVENT), {e0} edges")

    def canon_event(name: str, label: str) -> str:
        if label == "EVENT":
            return EVENT_MERGE.get(name, name)
        return name

    # ── DROP FP ──
    drop_keys = {("EVENT", nm) for nm in EVENT_DROP if ((nodes["label"] == "EVENT") & (nodes["name"] == nm)).any()}

    ev = nodes[(nodes["label"] == "EVENT") & (~nodes.apply(lambda r: (r["label"], r["name"]) in drop_keys, axis=1))].copy()
    other = nodes[nodes["label"] != "EVENT"].copy()

    # ── MERGE EVENT by canonical name ──
    ev["_canon"] = ev["name"].map(lambda nm: EVENT_MERGE.get(nm, nm))
    merged_rows = []
    merge_log = []
    for canon, g in ev.groupby("_canon"):
        variants = g["name"].unique().tolist()
        chunks = []
        for c in g["chunk_ids"]:
            chunks += split_chunks(c)
        chunks = list(dict.fromkeys(chunks))
        al = []
        for a in g["aliases"]:
            al += split_aliases(a)
        al += [v for v in variants if v != canon]
        al = [a for a in dict.fromkeys(al) if a and a != canon]
        g2 = g.copy()
        g2["_f"] = pd.to_numeric(g2["frequency"], errors="coerce").fillna(0)
        # baris dasar: yang namanya == canon kalau ada, else frequency tertinggi
        base = g2[g2["name"] == canon]
        base = base.iloc[0] if len(base) else g2.sort_values("_f", ascending=False).iloc[0]
        merged_rows.append({
            "node_id": base["node_id"], "name": canon, "label": "EVENT",
            "aliases": ALIASES_SEP.join(al),
            "chunk_ids": CHUNK_SEP.join(chunks) if chunks else base["chunk_ids"],
            "frequency": str(len(chunks) if chunks else int(base["_f"])),
            "periode_bab": base["periode_bab"], "page_range": base["page_range"],
        })
        if len([v for v in variants if v != canon]):
            merge_log.append((canon, [v for v in variants if v != canon]))

    new_ev = pd.DataFrame(merged_rows)
    new_nodes = pd.concat([other, new_ev], ignore_index=True)[nodes.columns.tolist()]

    # ── remap edges ──
    def remap(name: str, label: str):
        if (label, name) in drop_keys:
            return None
        return canon_event(name, label)

    kept, dropped = [], 0
    for _, r in edges.iterrows():
        s = remap(r["source_name"], r["source_label"])
        t = remap(r["target_name"], r["target_label"])
        if s is None or t is None:
            dropped += 1
            continue
        rr = r.copy(); rr["source_name"], rr["target_name"] = s, t
        kept.append(rr)
    new_edges = pd.DataFrame(kept)[edges.columns.tolist()] if kept else edges.iloc[0:0].copy()
    before = len(new_edges)
    new_edges = new_edges.drop_duplicates(
        subset=["source_name", "source_label", "relation_type", "relation_subtype",
                "target_name", "target_label", "chunk_id"]).reset_index(drop=True)
    dedup = before - len(new_edges)

    # ── report ──
    print(f"\n── MERGE ({len(merge_log)}) ──")
    for canon, vs in merge_log:
        print(f"  {vs} -> {canon!r}")
    print(f"\n── DROP FP ({len(drop_keys)}) ──")
    for lb, nm in drop_keys:
        print(f"  [{lb}] {nm!r}")
    print("\n" + "-" * 64)
    print(f"  nodes : {n0} -> {len(new_nodes)}   EVENT: {ev0} -> {(new_nodes['label']=='EVENT').sum()}")
    print(f"  edges : {e0} -> {len(new_edges)}   (drop refer-dropped={dropped}, dedup={dedup})")
    print("-" * 64)

    if DRY:
        print("\n[PREVIEW] Tidak ada file diubah. Jalankan --apply untuk eksekusi.")
        return

    shutil.copy2(NODES, NODES.with_suffix(".csv.bak_events"))
    shutil.copy2(EDGES, EDGES.with_suffix(".csv.bak_events"))
    new_nodes.to_csv(NODES, sep=";", encoding="utf-8-sig", index=False)
    new_edges.to_csv(EDGES, sep=";", encoding="utf-8-sig", index=False)
    print("\n[APPLY] Ditulis. Backup: *.csv.bak_events")
    print("Next: regenerate scoped + re-run SNA/event_centrality.")


if __name__ == "__main__":
    main()
