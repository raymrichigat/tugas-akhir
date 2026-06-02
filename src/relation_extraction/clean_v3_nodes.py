"""
clean_v3_nodes.py
=================
Pembersihan node KG v3 yang TERLEWAT di jalur inference NER (jalur v3 tidak
melewati alias clustering yang ada di jalur v2). Menjalankan 4 operasi:

  OP1. ALIAS MERGE (wajib) — apply alias_map.json (case-insensitive) ke semua
       label. Folds variasi ejaan/typo ke canonical (mis. Rasulullah->Muhammad,
       Perang Badar->Perang Badr, Isra' Dan Mi'Raj->Isra' Mi'Raj).
  OP2. CASE-DEDUP — merge node yang namanya identik kecuali kapitalisasi
       (mis. Perang Bu'ats / Perang Bu'Ats -> 1 node). Display = varian
       dengan frequency tertinggi.
  OP3. DROP generic EVENT false-positive — buang node EVENT kata-benda-umum
       {Perang, Malam, Peperangan} + edge yang menyentuhnya. Ini adalah
       manifestasi precision EVENT 0.913 (~9% FP), BUKAN prediksi benar.
  OP4. FIX mislabel 'Jabal Uhud' (EVENT) — gunung = LOCATION. Karena tidak
       punya edge dan sudah ada LOCATION 'Uhud' (freq 20), node ini di-drop
       dan 'Jabal Uhud' dicatat sebagai alias dari 'Uhud'.

CATATAN METODOLOGI (untuk Bab 3/4):
  Operasi ini berada di TAHAP KONSTRUKSI KG (hilir), BUKAN di evaluasi NER.
  F1 NER (0.9537 test / 0.972 vs manual) dihitung di tahap prediksi entity dan
  TIDAK terpengaruh. Output NER mentah (sirah_predicted_v3_entity.csv) sengaja
  tidak disentuh — hanya nodes_v3/edges_v3 yang dibersihkan. Filter bersifat
  rule-based (daftar eksplisit) + di-disclose, bukan ad-hoc cherry-pick.

Kandidat JUDGMENT (tidak di-auto-merge, hanya dilaporkan untuk review manual):
  near-duplicate yang butuh keputusan historis (mis. 'Mi'Raj' vs 'Isra' Mi'Raj',
  'Perang Sawiq' vs 'Perang As-Sawiq'). Default script TIDAK menggabungnya.

Idempotent. Backup ke .bak_clean sebelum overwrite.

Usage:
  # Preview (default, TIDAK menulis apa-apa):
  venv/Scripts/python.exe src/relation_extraction/clean_v3_nodes.py
  # Eksekusi beneran:
  venv/Scripts/python.exe src/relation_extraction/clean_v3_nodes.py --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console default cp1252
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
NODES_V3 = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"
EDGES_V3 = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
ALIAS_MAP = ROOT / "data" / "result" / "alias_clustering" / "alias_map.json"

# OP3: node EVENT kata-benda-umum yang dibuang (case-insensitive match)
GENERIC_EVENT_DROP = {"perang", "malam", "peperangan"}

# OP4: mislabel EVENT->LOCATION yang di-merge ke LOCATION canonical (no edges)
MISLABEL_TO_LOCATION = {"jabal uhud": "Uhud"}

ALIASES_SEP = " | "
CHUNK_SEP = "|"


# ── util ──────────────────────────────────────────────────────────────────────

def split_chunks(s: str) -> list[str]:
    return [c.strip() for c in str(s).split(CHUNK_SEP) if c.strip()]


def split_aliases(s: str) -> list[str]:
    return [a.strip() for a in str(s).split("|") if a.strip()]


def load_alias_lookup() -> dict[str, dict[str, str]]:
    """Return {label: {alias.lower(): canonical}}."""
    raw = json.loads(ALIAS_MAP.read_text(encoding="utf-8-sig"))
    out: dict[str, dict[str, str]] = {}
    for label, mapping in raw.items():
        out[label] = {alias.lower(): canon for alias, canon in mapping.items()}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Bersihkan node KG v3 (alias merge + filter)")
    ap.add_argument("--apply", action="store_true",
                    help="Tulis perubahan ke nodes_v3/edges_v3 (default: preview saja)")
    args = ap.parse_args()
    DRY = not args.apply

    print("=" * 64)
    print(f"CLEAN KG v3 NODES   [{'PREVIEW (dry-run)' if DRY else 'APPLY'}]")
    print("=" * 64)

    nodes = pd.read_csv(NODES_V3, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    edges = pd.read_csv(EDGES_V3, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    la = load_alias_lookup()
    n0, e0 = len(nodes), len(edges)
    print(f"\nLoaded: {n0} nodes, {e0} edges")

    # ── canon(): alias_map case-insensitive ───────────────────────────────────
    def canon(name: str, label: str) -> str:
        return la.get(label, {}).get(name.lower(), name)

    # rename_log: list of (label, old_name, new_name, reason)
    rename_log: list[tuple[str, str, str, str]] = []
    drop_log: list[tuple[str, str, str]] = []   # (label, name, reason)
    review_log: list[str] = []

    # ── OP3 + OP4: tandai drop ─────────────────────────────────────────────────
    drop_node_keys: set[tuple[str, str]] = set()    # (label, name)
    uhud_alias_add: list[str] = []
    for _, r in nodes.iterrows():
        nm, lb = r["name"], r["label"]
        if lb == "EVENT" and nm.lower() in GENERIC_EVENT_DROP:
            drop_node_keys.add((lb, nm))
            drop_log.append((lb, nm, "generic EVENT false-positive (OP3)"))
        elif lb == "EVENT" and nm.lower() in MISLABEL_TO_LOCATION:
            drop_node_keys.add((lb, nm))
            uhud_alias_add.append(nm)
            drop_log.append((lb, nm, f"mislabel -> alias of LOCATION '{MISLABEL_TO_LOCATION[nm.lower()]}' (OP4)"))

    # ── OP1: apply alias canonical ke kolom 'name' ─────────────────────────────
    nodes = nodes[~nodes.apply(lambda r: (r["label"], r["name"]) in drop_node_keys, axis=1)].copy()
    nodes["_canon"] = nodes.apply(lambda r: canon(r["name"], r["label"]), axis=1)
    for _, r in nodes.iterrows():
        if r["_canon"] != r["name"]:
            rename_log.append((r["label"], r["name"], r["_canon"], "alias_map (OP1)"))

    # ── OP2: group by (label, canon.lower()) -> pilih display ──────────────────
    nodes["_key"] = nodes["label"] + "::" + nodes["_canon"].str.lower()
    alias_canon_set = {c for m in la.values() for c in m.values()}

    def pick_display(group: pd.DataFrame) -> str:
        cands = group["_canon"].unique().tolist()
        # 1. casing kurasi dari alias_map menang (sudah di-review manual, paling reliable)
        ac = [c for c in cands if c in alias_canon_set]
        if ac:
            return sorted(ac, key=lambda s: (len(s), s))[0]
        # 2. fallback: frequency tertinggi, tie -> sort deterministik
        cand = group.copy()
        cand["_f"] = pd.to_numeric(cand["frequency"], errors="coerce").fillna(0)
        maxf = cand["_f"].max()
        return sorted(cand[cand["_f"] == maxf]["_canon"].unique().tolist())[0]

    merged_rows = []
    final_name_map: dict[tuple[str, str], str] = {}   # (label, original_name) -> display
    for key, g in nodes.groupby("_key"):
        label = g.iloc[0]["label"]
        display = pick_display(g)
        # log merge antar surface-variant berbeda (selain rename alias yang sudah dicatat)
        variants = g["name"].unique().tolist()
        for v in variants:
            final_name_map[(label, v)] = display
            if v != display and v != canon(v, label):
                pass  # alias rename sudah dicatat di OP1
            elif v != display:
                rename_log.append((label, v, display, "case-dedup (OP2)"))
        # union chunk_ids
        chunks = []
        for c in g["chunk_ids"]:
            chunks += split_chunks(c)
        chunks = list(dict.fromkeys(chunks))   # unique, order-preserving
        # aliases: union existing + non-display surface variants
        al = []
        for a in g["aliases"]:
            al += split_aliases(a)
        al += [v for v in variants if v != display]
        al = [a for a in dict.fromkeys(al) if a and a != display]
        # display row = baris dengan frequency tertinggi (ambil id/periode/page dari situ)
        g2 = g.copy()
        g2["_f"] = pd.to_numeric(g2["frequency"], errors="coerce").fillna(0)
        base = g2.sort_values("_f", ascending=False).iloc[0]
        freq = len(chunks) if chunks else int(base["_f"])
        merged_rows.append({
            "node_id": base["node_id"],
            "name": display,
            "label": label,
            "aliases": ALIASES_SEP.join(al),
            "chunk_ids": CHUNK_SEP.join(chunks) if chunks else base["chunk_ids"],
            "frequency": str(freq),
            "periode_bab": base["periode_bab"],
            "page_range": base["page_range"],
        })

    new_nodes = pd.DataFrame(merged_rows)[
        ["node_id", "name", "label", "aliases", "chunk_ids", "frequency", "periode_bab", "page_range"]
    ]

    # OP4: tambahkan 'Jabal Uhud' ke aliases LOCATION 'Uhud'
    for alias_nm in uhud_alias_add:
        canon_loc = MISLABEL_TO_LOCATION[alias_nm.lower()]
        mask = (new_nodes["label"] == "LOCATION") & (new_nodes["name"] == canon_loc)
        if mask.any():
            i = new_nodes[mask].index[0]
            cur = split_aliases(new_nodes.at[i, "aliases"])
            if alias_nm not in cur:
                cur.append(alias_nm)
                new_nodes.at[i, "aliases"] = ALIASES_SEP.join(cur)

    # ── remap edges ────────────────────────────────────────────────────────────
    def remap_endpoint(name: str, label: str) -> str | None:
        if (label, name) in drop_node_keys:
            return None
        # alias canon dulu, lalu final display
        c = canon(name, label)
        return final_name_map.get((label, name), final_name_map.get((label, c), c))

    kept_edges = []
    dropped_edges = 0
    for _, r in edges.iterrows():
        s = remap_endpoint(r["source_name"], r["source_label"])
        t = remap_endpoint(r["target_name"], r["target_label"])
        if s is None or t is None:
            dropped_edges += 1
            continue
        rr = r.copy()
        rr["source_name"], rr["target_name"] = s, t
        kept_edges.append(rr)
    new_edges = pd.DataFrame(kept_edges)[edges.columns.tolist()] if kept_edges else edges.iloc[0:0].copy()
    # drop full-duplicate edge rows yang lahir dari merge
    before_dedup = len(new_edges)
    new_edges = new_edges.drop_duplicates(
        subset=["source_name", "source_label", "relation_type", "relation_subtype",
                "target_name", "target_label", "chunk_id"]
    ).reset_index(drop=True)
    edge_dups = before_dedup - len(new_edges)

    # ── REVIEW: near-duplicate yang TIDAK di-merge (judgment) ──────────────────
    ev_names = sorted(new_nodes[new_nodes["label"] == "EVENT"]["name"].tolist())
    for i, a in enumerate(ev_names):
        for b in ev_names[i + 1:]:
            al_, bl_ = a.lower(), b.lower()
            if al_ != bl_ and (al_ in bl_ or bl_ in al_) and abs(len(al_) - len(bl_)) <= 6:
                review_log.append(f"{a}  ~?~  {b}")

    # ── REPORT ─────────────────────────────────────────────────────────────────
    print(f"\n── OP1+OP2  RENAME / MERGE ({len(rename_log)}) ──")
    for lb, old, new, why in rename_log:
        print(f"  [{lb:8s}] {old!r:40s} -> {new!r}  ({why})")
    print(f"\n── OP3+OP4  DROP ({len(drop_log)}) ──")
    for lb, nm, why in drop_log:
        print(f"  [{lb:8s}] {nm!r:24s}  {why}")
    print(f"\n── REVIEW (TIDAK di-merge — keputusan historis manual) ({len(review_log)}) ──")
    for line in review_log:
        print(f"  {line}")

    print("\n" + "-" * 64)
    print(f"  nodes : {n0} -> {len(new_nodes)}   (Δ {len(new_nodes) - n0})")
    print(f"  edges : {e0} -> {len(new_edges)}   (Δ {len(new_edges) - e0};"
          f" drop refer-dropped={dropped_edges}, dedup={edge_dups})")
    ev_before = (pd.read_csv(NODES_V3, sep=';', encoding='utf-8-sig', dtype=str)["label"] == "EVENT").sum()
    ev_after = (new_nodes["label"] == "EVENT").sum()
    print(f"  EVENT : {ev_before} -> {ev_after}")
    print("-" * 64)

    if DRY:
        print("\n[PREVIEW] Tidak ada file yang diubah. Jalankan dengan --apply untuk eksekusi.")
        return

    # backup + write
    shutil.copy2(NODES_V3, NODES_V3.with_suffix(".csv.bak_clean"))
    shutil.copy2(EDGES_V3, EDGES_V3.with_suffix(".csv.bak_clean"))
    new_nodes.to_csv(NODES_V3, sep=";", encoding="utf-8-sig", index=False)
    new_edges.to_csv(EDGES_V3, sep=";", encoding="utf-8-sig", index=False)
    print(f"\n[APPLY] Ditulis. Backup: *.csv.bak_clean")
    print("Next: regenerate Cypher v3 ->")
    print("  venv/Scripts/python.exe src/neo4j/import_to_neo4j.py --source v3")
    print("Lalu re-run SNA v3 (node/edge berubah).")


if __name__ == "__main__":
    main()
