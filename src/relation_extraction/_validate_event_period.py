"""
_validate_event_period.py
=========================
Validator untuk EVENT → BAB chronology di nodes.csv.

Banyak mapping fuzzy-match di period_mapping.py yang SALAH karena substring
match terlalu agresif. Tool ini bantu kamu review + koreksi manual.

ALUR:
  1. python _validate_event_period.py --generate-review
     -> Buat data/result/relation_result/event_period_review.csv
        Berisi: event_name, current_bab, current_pages, top5_suggestions, [kosong]

  2. Buka di Excel, isi 3 kolom:
     - ACTION         : K (keep current), F (fix), R (remove as noise)
     - CORRECT_BAB    : (kalau F) judul BAB yang benar — copy dari kolom suggestions
     - CORRECT_PAGES  : (kalau F) format "start-end", contoh "266-304"

  3. python _validate_event_period.py --apply
     -> Generate event_period_manual.json (override fuzzy match)
     -> Update nodes.csv dengan mapping yang benar
     -> Hapus EVENT yang ditandai R (noise)
     -> Backup nodes.csv -> nodes.csv.bak

USAGE:
  python _validate_event_period.py --generate-review
  python _validate_event_period.py --apply
  python _validate_event_period.py --list-bab          # tampilkan semua BAB di TOC
"""

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TOC_PATH    = ROOT / "data" / "toc_groundtruth.json"
NODES_PATH  = ROOT / "data" / "result" / "relation_result" / "nodes.csv"
EDGES_PATH  = ROOT / "data" / "result" / "relation_result" / "edges.csv"
REVIEW_PATH = ROOT / "data" / "result" / "relation_result" / "event_period_review.csv"
MANUAL_JSON = ROOT / "data" / "result" / "relation_result" / "event_period_manual.json"

VALID_ACTIONS = {"K", "F", "R", ""}  # K=keep, F=fix, R=remove, empty=undecided


# ── TOC loader ───────────────────────────────────────────────────────────────
def load_toc():
    with open(TOC_PATH, "r", encoding="utf-8") as f:
        toc_raw = json.load(f)
    babs = [e for e in toc_raw if e.get("level") == "BAB"]
    for i, b in enumerate(babs):
        b["page_end"] = babs[i + 1]["page_start"] - 1 if i + 1 < len(babs) else 633
    return babs


def get_bab_entries(toc):
    """Flatten BAB + subbab jadi list of {title, page_start, page_end}."""
    entries = []
    for bab in toc:
        entries.append({
            "title": bab["title"],
            "page_start": bab["page_start"],
            "page_end": bab["page_end"],
        })
        for sub in bab.get("subbab", []):
            entries.append({
                "title": sub["title"],
                "page_start": sub["page_start"],
                "page_end": bab["page_end"],
            })
    return entries


def list_all_bab():
    babs = load_toc()
    print(f"Total BAB: {len(babs)}")
    for i, b in enumerate(babs, 1):
        n_sub = len(b.get("subbab", []))
        print(f"  {i:2}. p.{b['page_start']:>3}-{b['page_end']:>3}: {b['title']}  ({n_sub} subbab)")


# ── Top-K suggester (fuzzy + substring) ──────────────────────────────────────
def _normalize(t: str) -> str:
    return " ".join(t.lower().strip().split())


def _score(event_name: str, bab_title: str) -> float:
    en = _normalize(event_name)
    bn = _normalize(bab_title)
    # Substring match → bonus
    if en == bn:
        return 1.0
    if en in bn or bn in en:
        return 0.92
    return SequenceMatcher(None, en, bn).ratio()


def top_k_matches(event_name: str, entries: list, k: int = 5):
    scored = [(e, _score(event_name, e["title"])) for e in entries]
    scored.sort(key=lambda x: -x[1])
    return scored[:k]


# ── Step 1: generate review CSV ──────────────────────────────────────────────
def _start_page(page_range: str) -> int:
    """Ambil start page dari 'start-end'. Return inf kalau kosong/invalid (push ke akhir)."""
    if not isinstance(page_range, str) or not page_range.strip():
        return 10**9
    pg = parse_pages(page_range)
    return pg[0] if pg else 10**9


def generate_review():
    nodes = pd.read_csv(NODES_PATH, sep=";", encoding="utf-8-sig")
    events = nodes[nodes["label"] == "EVENT"].copy()
    events["_sort_page"] = events["page_range"].apply(_start_page)
    events = events.sort_values(by=["_sort_page", "name"], kind="stable").drop(columns=["_sort_page"])
    print(f"Total EVENT nodes: {len(events)}")

    toc = load_toc()
    entries = get_bab_entries(toc)
    print(f"Total BAB entries (BAB + subbab) di TOC: {len(entries)}")

    rows = []
    for _, ev in events.iterrows():
        name = ev["name"]
        current_bab = str(ev.get("periode_bab", "")) if pd.notna(ev.get("periode_bab")) else ""
        current_pages = str(ev.get("page_range", "")) if pd.notna(ev.get("page_range")) else ""

        top5 = top_k_matches(name, entries, k=5)
        suggestions_str = " | ".join(
            f"[{s:.2f}] {e['title']} (p.{e['page_start']}-{e['page_end']})"
            for e, s in top5
        )

        rows.append({
            "event_name":    name,
            "current_bab":   current_bab,
            "current_pages": current_pages,
            "top5_suggestions": suggestions_str,
            "ACTION":        "",   # K / F / R
            "CORRECT_BAB":   "",
            "CORRECT_PAGES": "",
            "NOTES":         "",
        })

    df = pd.DataFrame(rows, columns=[
        "event_name", "current_bab", "current_pages",
        "top5_suggestions",
        "ACTION", "CORRECT_BAB", "CORRECT_PAGES", "NOTES",
    ])

    REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(REVIEW_PATH, sep=";", encoding="utf-8-sig", index=False)
    print(f"\nReview CSV: {REVIEW_PATH}")
    print()
    print("CARA REVIEW (di Excel):")
    print("  1. Baca kolom 'event_name' + 'current_bab' + 'current_pages' (mapping sekarang)")
    print("  2. Lihat 'top5_suggestions' (kandidat top-5 dari TOC)")
    print("  3. Isi kolom 'ACTION':")
    print("       K = Keep (mapping current sudah benar)")
    print("       F = Fix  (mapping salah, perlu dikoreksi)")
    print("       R = Remove (event ini noise/false positive, hapus dari nodes)")
    print("  4. Kalau ACTION=F:")
    print("       - CORRECT_BAB    : copy judul BAB dari suggestions, atau ketik manual")
    print("       - CORRECT_PAGES  : format 'start-end' (contoh: '266-304')")
    print("  5. (Opsional) NOTES : alasan singkat untuk dokumentasi")
    print()
    print("Untuk lihat full daftar BAB di TOC:")
    print(f"  python {Path(__file__).name} --list-bab")
    print()
    print("Setelah selesai review, jalankan:")
    print(f"  python {Path(__file__).name} --apply")


# ── Step 2: apply (update nodes.csv + simpan manual mapping) ─────────────────
def parse_pages(s: str) -> tuple[int, int] | None:
    s = s.strip()
    if not s:
        return None
    parts = s.replace("–", "-").split("-")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return None


def apply_review():
    if not REVIEW_PATH.exists():
        sys.exit(f"ERROR: review CSV tidak ada di {REVIEW_PATH}\n"
                 f"Generate dulu: python {Path(__file__).name} --generate-review")

    df_review = pd.read_csv(REVIEW_PATH, sep=";", encoding="utf-8-sig").fillna("")
    df_review["ACTION"] = df_review["ACTION"].astype(str).str.strip().str.upper()

    invalid = df_review[~df_review["ACTION"].isin(VALID_ACTIONS)]
    if len(invalid):
        print("ERROR: Ada ACTION tidak valid (harus K / F / R / kosong):")
        print(invalid[["event_name", "ACTION"]].to_string(index=False))
        sys.exit(1)

    # Stats
    n_keep = (df_review["ACTION"] == "K").sum()
    n_fix  = (df_review["ACTION"] == "F").sum()
    n_rem  = (df_review["ACTION"] == "R").sum()
    n_und  = (df_review["ACTION"] == "").sum()
    print(f"Review summary:")
    print(f"  Keep   (K): {n_keep}")
    print(f"  Fix    (F): {n_fix}")
    print(f"  Remove (R): {n_rem}")
    print(f"  Undecided  : {n_und}")
    if n_und:
        print(f"\n  PERINGATAN: {n_und} event masih kosong (akan diperlakukan sebagai Keep)")

    # Build manual mapping (untuk override fuzzy match)
    manual_map = {}
    events_to_remove = set()
    warnings = []

    for _, r in df_review.iterrows():
        name = r["event_name"]
        action = r["ACTION"]

        if action == "R":
            events_to_remove.add(name)
            continue

        if action == "F":
            correct_bab = str(r["CORRECT_BAB"]).strip()
            pages_str   = str(r["CORRECT_PAGES"]).strip()
            if not correct_bab:
                warnings.append(f"  - {name}: ACTION=F tapi CORRECT_BAB kosong → SKIP")
                continue
            pg = parse_pages(pages_str)
            if pg is None:
                warnings.append(f"  - {name}: ACTION=F tapi CORRECT_PAGES tidak valid '{pages_str}' → SKIP")
                continue
            manual_map[name] = {
                "bab_title":  correct_bab,
                "page_start": pg[0],
                "page_end":   pg[1],
            }

        if action == "K":
            # Tetap simpan ke manual_map sebagai source of truth
            current_bab   = str(r["current_bab"]).strip()
            current_pages = str(r["current_pages"]).strip()
            pg = parse_pages(current_pages)
            if current_bab and pg:
                manual_map[name] = {
                    "bab_title":  current_bab,
                    "page_start": pg[0],
                    "page_end":   pg[1],
                }

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(w)

    # Save manual mapping JSON
    MANUAL_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(MANUAL_JSON, "w", encoding="utf-8") as f:
        json.dump(manual_map, f, indent=2, ensure_ascii=False)
    print(f"\nManual mapping JSON saved: {MANUAL_JSON}")
    print(f"  {len(manual_map)} event mappings")
    print(f"  {len(events_to_remove)} events flagged untuk remove")

    # Update nodes.csv
    nodes = pd.read_csv(NODES_PATH, sep=";", encoding="utf-8-sig")
    if "label" not in nodes.columns:
        sys.exit("ERROR: nodes.csv tidak punya kolom 'label'")

    n_before = len(nodes)

    # Remove noise events
    if events_to_remove:
        nodes = nodes[~nodes["name"].isin(events_to_remove)].reset_index(drop=True)

    # Update periode_bab + page_range untuk EVENT
    for idx, row in nodes.iterrows():
        if row["label"] != "EVENT":
            continue
        name = row["name"]
        if name in manual_map:
            m = manual_map[name]
            nodes.at[idx, "periode_bab"] = m["bab_title"]
            nodes.at[idx, "page_range"] = f"{m['page_start']}-{m['page_end']}"

    # Backup
    backup_path = NODES_PATH.with_suffix(".csv.bak")
    if backup_path.exists():
        backup_path.unlink()
    NODES_PATH.replace(backup_path)
    nodes.to_csv(NODES_PATH, sep=";", encoding="utf-8-sig", index=False)

    n_after = len(nodes)
    print(f"\nnodes.csv updated:")
    print(f"  Before: {n_before} nodes")
    print(f"  After : {n_after} nodes  ({n_before - n_after} removed)")
    print(f"  Backup: {backup_path.name}")

    # Update edges.csv (hapus edges yang refer ke removed events)
    if events_to_remove and EDGES_PATH.exists():
        edges = pd.read_csv(EDGES_PATH, sep=";", encoding="utf-8-sig")
        # Cari semua node_id yang dihapus
        # Asumsi: edges punya kolom source_name / target_name atau source / target
        edge_cols = list(edges.columns)
        # Try common column patterns
        if "source_name" in edge_cols and "target_name" in edge_cols:
            mask_keep = ~(edges["source_name"].isin(events_to_remove) |
                         edges["target_name"].isin(events_to_remove))
        elif "source" in edge_cols and "target" in edge_cols:
            mask_keep = ~(edges["source"].isin(events_to_remove) |
                         edges["target"].isin(events_to_remove))
        else:
            print(f"  WARNING: edges.csv kolom tidak standar — skip auto-cleanup edges")
            mask_keep = None

        if mask_keep is not None:
            n_edges_before = len(edges)
            edges_clean = edges[mask_keep].reset_index(drop=True)
            edges_backup = EDGES_PATH.with_suffix(".csv.bak")
            if edges_backup.exists():
                edges_backup.unlink()
            EDGES_PATH.replace(edges_backup)
            edges_clean.to_csv(EDGES_PATH, sep=";", encoding="utf-8-sig", index=False)
            print(f"\nedges.csv updated:")
            print(f"  Before: {n_edges_before} edges")
            print(f"  After : {len(edges_clean)} edges  ({n_edges_before - len(edges_clean)} removed)")
            print(f"  Backup: {edges_backup.name}")

    print("\nDONE. Langkah berikutnya:")
    print("  - Review nodes.csv & edges.csv yang sudah di-update")
    print("  - Re-run analysis (SNA, Neo4j) kalau perlu")


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Validator EVENT → BAB chronology mapping.")
    p.add_argument("--generate-review", action="store_true",
                   help="Generate event_period_review.csv untuk diisi manual di Excel")
    p.add_argument("--apply", action="store_true",
                   help="Apply review CSV → update nodes.csv + simpan event_period_manual.json")
    p.add_argument("--list-bab", action="store_true",
                   help="List semua BAB di TOC (referensi saat fill review)")
    args = p.parse_args()

    if args.list_bab:
        list_all_bab()
    elif args.generate_review:
        generate_review()
    elif args.apply:
        apply_review()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
