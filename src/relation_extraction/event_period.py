"""
event_period.py
===============
Pemetaan EVENT → PERIOD berdasarkan **periodisasi top-down** (post-revisi 2026-05-12).

Pendekatan baru menggantikan `period_mapping.py` (lama, fuzzy match BAB) dengan
lookup page range langsung ke `data/result/relation_result/period_mapping.json`.

Sumber data:
  - `data/result/relation_result/period_mapping.json` — 15 period (P0-P14), 6 phase,
    grouping 56 BAB dengan page_start/page_end eksplisit. Tidak butuh fuzzy match
    karena setiap BAB sudah punya period definitif.

Kelebihan vs `period_mapping.py` lama:
  - Tidak ada false-positive substring match (mis. "Hijrah" → "Hijrah ke Habasyah")
  - Period-nya **bermakna semantically** (mis. "Awal Kenabian & Mandat Dakwah")
    bukan judul BAB random
  - Cocok untuk grouping di Knowledge Graph (period = node, EVENT = anggota period)

API:
  - load_periods(filepath=...)               → list[dict] dari JSON
  - parse_page_string(halaman_str)           → list[int] (handle "266", "266-270", "266 | 267")
  - get_period_for_page(page, periods)       → dict | None
  - get_period_for_pages(halaman, periods)   → dict | None (first matching page)
  - build_event_period_map(nodes_df, periods) → dict {event_name: period_info}
  - is_in_event_period(halaman, event_period) → bool
  - compute_period_score(halaman, event_name, event_period_map) → float (0.0/0.25/0.5)

Backward-compatible dengan `relation_extraction.py`:
  - Signature `compute_period_score()` sama dengan `period_mapping.py` lama,
    jadi bisa drop-in replacement: tinggal ubah import.

CLI:
  python event_period.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

# ── Konfigurasi path ─────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]   # ...\TA_sirah
PERIOD_JSON_PATH = BASE_DIR / "data" / "result" / "relation_result" / "period_mapping.json"
NODES_CSV_PATH = BASE_DIR / "data" / "result" / "relation_result" / "nodes.csv"
REVIEW_CSV_PATH = BASE_DIR / "data" / "result" / "relation_result" / "event_period_review_v2.csv"

# Marker text yang dipakai di row "(period kosong)" — bukan event nama beneran.
_MARKER_PREFIXES = ("(period kosong", "(no period", "(ADD candidate")


# ── Loading ──────────────────────────────────────────────────────────────────
def load_periods(filepath: Path = PERIOD_JSON_PATH) -> list[dict]:
    """
    Load periods dari `period_mapping.json`.

    Returns:
        list of period dicts. Each period has keys:
          - period_id (str, e.g., "P0", "P14")
          - label (str, semantic label)
          - phase (str, "Fase I — Pra-Islam & Latar Belakang", etc.)
          - description (str)
          - page_start (int)
          - page_end (int)
          - bab_ids (list[int])
          - babs (list[dict] dengan title, page_start, page_end, subbab)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Page parsing ─────────────────────────────────────────────────────────────
def parse_page_string(halaman_str) -> list[int]:
    """
    Parse string halaman ke list of integer pages.

    Format yang didukung:
      - "256"          → [256]
      - "256-260"      → [256, 257, 258, 259, 260]
      - "266 | 267"    → [266, 267]
      - "256-260 | 270" → [256, 257, 258, 259, 260, 270]

    Returns:
        list[int]. Empty list kalau input invalid/None.
    """
    if halaman_str is None or (isinstance(halaman_str, float) and pd.isna(halaman_str)):
        return []
    if not isinstance(halaman_str, str):
        halaman_str = str(halaman_str)

    pages: list[int] = []
    for part in halaman_str.split("|"):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start_s, end_s = part.split("-", 1)
                start, end = int(start_s.strip()), int(end_s.strip())
                pages.extend(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                pages.append(int(part))
            except ValueError:
                continue
    return pages


# ── Period lookup ────────────────────────────────────────────────────────────
def get_period_for_page(page: int, periods: list[dict]) -> Optional[dict]:
    """
    Cari period yang range page-nya mencakup `page`.

    Returns:
        Period dict, atau None kalau page di luar semua period.
    """
    for period in periods:
        if period["page_start"] <= page <= period["page_end"]:
            return period
    return None


def get_period_for_pages(halaman_str, periods: list[dict]) -> Optional[dict]:
    """
    Untuk chunk yang span multiple page, return period dari page pertama yang match.

    Returns:
        Period dict, atau None kalau tidak ada page yang match any period.
    """
    pages = parse_page_string(halaman_str)
    for page in pages:
        period = get_period_for_page(page, periods)
        if period is not None:
            return period
    return None


# ── EVENT → period mapping ───────────────────────────────────────────────────
def build_event_period_map(
    nodes_df: pd.DataFrame,
    periods: list[dict],
    use_column: str = "page_range",
) -> dict[str, dict]:
    """
    Bangun mapping EVENT name → period dict via `page_range` kolom di nodes.csv.

    Args:
        nodes_df: DataFrame `nodes.csv` (sep=";", encoding="utf-8-sig").
                  Wajib punya kolom: name, label, dan `use_column` (default "page_range").
        periods: list of period dicts dari `load_periods()`.
        use_column: nama kolom yang berisi page range tiap EVENT. Default "page_range".

    Returns:
        dict {event_name: {period_id, label, phase, page_start, page_end, bab_count}}.
        EVENT yang page_range invalid atau outside semua period akan di-skip.
    """
    event_period_map: dict[str, dict] = {}
    event_nodes = nodes_df[nodes_df["label"] == "EVENT"]

    for _, event in event_nodes.iterrows():
        event_name = event["name"]
        page_range = event.get(use_column, "")
        period = get_period_for_pages(page_range, periods)
        if period is not None:
            event_period_map[event_name] = {
                "period_id": period["period_id"],
                "label": period["label"],
                "phase": period["phase"],
                "page_start": period["page_start"],
                "page_end": period["page_end"],
                "bab_count": len(period.get("bab_ids", [])),
            }

    return event_period_map


# ── Score computation (compatible dengan relation_extraction.py) ─────────────
def is_in_event_period(halaman_str, event_period: dict | None) -> bool:
    """Apakah halaman chunk berada dalam range period event."""
    if event_period is None:
        return False
    pages = parse_page_string(halaman_str)
    page_start = event_period["page_start"]
    page_end = event_period["page_end"]
    return any(page_start <= p <= page_end for p in pages)


# ── Review CSV loader (K/F/R/ADD decisions) ─────────────────────────────────
def _is_marker_text(value) -> bool:
    """Cek apakah event_name adalah text marker bukan event sungguhan."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    s = str(value).strip()
    if not s:
        return True
    return any(s.startswith(prefix) for prefix in _MARKER_PREFIXES)


def _resolve_event_name(row) -> str:
    """
    Ambil event_name dari row review CSV.

    User kadang pakai `period_label` sebagai event_name kalau `event_name` adalah
    marker text "(period kosong)" — fall back ke period_label dalam kasus itu.
    """
    name = row.get("event_name", "")
    if _is_marker_text(name):
        name = row.get("period_label", "")
    return str(name).strip() if not pd.isna(name) else ""


def load_review(filepath: Path = REVIEW_CSV_PATH) -> pd.DataFrame:
    """
    Load review CSV (event_period_review_v2.csv).

    Returns:
        DataFrame dengan kolom termasuk ACTION (K/F/R/ADD), CORRECT_PERIOD_ID,
        CORRECT_PAGES, dll. Empty rows / blank ACTION akan kept di df.
    """
    return pd.read_csv(filepath, sep=";", encoding="utf-8-sig")


def apply_review(
    review_df: pd.DataFrame,
    periods: list[dict],
) -> tuple[dict[str, dict], set[str], list[dict]]:
    """
    Apply K/F/R/ADD decisions dari review CSV → event_period_map yang sudah bersih.

    Logic per ACTION:
      - K   : keep mapping current (period dari `period_id` kolom)
      - F   : override period dengan `CORRECT_PERIOD_ID`
      - R   : remove event (add ke removed_events set, tidak masuk event_period_map)
      - ADD : tambah event baru. event_name dari `event_name` (atau fallback `period_label`
              kalau marker). period_id dari `CORRECT_PERIOD_ID`.
      - (blank/nan) : skipped — marker row untuk period kosong tidak menambah event

    Args:
        review_df: DataFrame dari load_review().
        periods: list of period dicts dari load_periods().

    Returns:
        event_period_map : dict {event_name: period_info_dict}
        removed_events   : set of event_name yang ACTION='R'
        added_events     : list of new event entries (untuk regenerate nodes.csv)
    """
    periods_by_id = {p["period_id"]: p for p in periods}

    event_period_map: dict[str, dict] = {}
    removed_events: set[str] = set()
    added_events: list[dict] = []

    for _, row in review_df.iterrows():
        action_raw = row.get("ACTION", "")
        if action_raw is None or (isinstance(action_raw, float) and pd.isna(action_raw)):
            continue
        action = str(action_raw).strip().upper()
        if not action:
            continue

        event_name = _resolve_event_name(row)
        if not event_name:
            continue

        if action == "K":
            pid = str(row.get("period_id", "")).strip()
            if pid in periods_by_id:
                p = periods_by_id[pid]
                event_period_map[event_name] = _period_info(p, source="K")

        elif action == "F":
            pid = str(row.get("CORRECT_PERIOD_ID", "")).strip()
            if pid in periods_by_id:
                p = periods_by_id[pid]
                event_period_map[event_name] = _period_info(p, source="F",
                                                            correct_pages=row.get("CORRECT_PAGES", ""))

        elif action == "R":
            removed_events.add(event_name)

        elif action == "ADD":
            pid = str(row.get("CORRECT_PERIOD_ID", "")).strip()
            if pid in periods_by_id:
                p = periods_by_id[pid]
                info = _period_info(p, source="ADD",
                                    correct_pages=row.get("CORRECT_PAGES", ""))
                event_period_map[event_name] = info
                added_events.append({
                    "event_name": event_name,
                    "period_id": p["period_id"],
                    "period_label": p["label"],
                    "phase": p["phase"],
                    "page_start": p["page_start"],
                    "page_end": p["page_end"],
                    "correct_pages": str(row.get("CORRECT_PAGES", "")).strip(),
                    "notes": str(row.get("NOTES", "")).strip(),
                })

    return event_period_map, removed_events, added_events


def _period_info(period: dict, source: str, correct_pages: str = "") -> dict:
    """Build dict entry untuk event_period_map dari period record."""
    info = {
        "period_id": period["period_id"],
        "label": period["label"],
        "phase": period["phase"],
        "page_start": period["page_start"],
        "page_end": period["page_end"],
        "source": source,
    }
    cp = str(correct_pages).strip() if correct_pages else ""
    if cp and cp.lower() != "nan":
        info["correct_pages"] = cp
    return info


def compute_period_score(
    halaman_str,
    event_name: str,
    event_period_map: dict[str, dict],
) -> float:
    """
    Compute period_score (0.0–0.5) untuk pembobotan relasi.

    Signature & semantik sama dengan `period_mapping.py` lama, jadi
    relation_extraction.py bisa drop-in replace import:
        # OLD: from period_mapping import compute_period_score
        # NEW: from event_period import compute_period_score

    Scoring:
      - Chunk halaman di dalam range period event → 0.5
      - Event tidak ter-mapping ke period (rare) → 0.25 (neutral)
      - Chunk halaman di luar period event → 0.0
    """
    event_period = event_period_map.get(event_name)
    if event_period is None:
        return 0.25
    if is_in_event_period(halaman_str, event_period):
        return 0.5
    return 0.0


# ── CLI / smoke test ─────────────────────────────────────────────────────────
def _print_summary(periods: list[dict], event_map: dict[str, dict]) -> None:
    """Print event→period grouping untuk inspection."""
    by_period: dict[str, list[str]] = {}
    for ev_name, info in event_map.items():
        by_period.setdefault(info["period_id"], []).append(ev_name)

    # Build period_id → label lookup
    period_labels = {p["period_id"]: p["label"] for p in periods}
    period_pages = {p["period_id"]: (p["page_start"], p["page_end"]) for p in periods}

    print(f"\n{'=' * 70}")
    print(f"EVENT → PERIOD MAPPING (top-down via page_range)")
    print(f"{'=' * 70}")
    print(f"Total: {len(event_map)} EVENTs mapped to {len(by_period)} periods\n")

    for pid in sorted(by_period.keys(), key=lambda p: int(p[1:])):
        events = sorted(by_period[pid])
        ps, pe = period_pages[pid]
        print(f"\n{pid}  p.{ps:>3}-{pe:>3}  \"{period_labels[pid]}\"  ({len(events)} event)")
        for ev_name in events:
            print(f"    • {ev_name}")


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 fix
    except AttributeError:
        pass

    periods = load_periods()
    print(f"Loaded {len(periods)} periods from {PERIOD_JSON_PATH.name}")

    # ── Mode 1: auto-map from page_range (no review) ─────────────────────────
    if NODES_CSV_PATH.exists():
        nodes_df = pd.read_csv(NODES_CSV_PATH, sep=";", encoding="utf-8-sig")
        print(f"Loaded {len(nodes_df)} nodes (EVENT = {(nodes_df['label']=='EVENT').sum()})")

        auto_map = build_event_period_map(nodes_df, periods)
        print(f"\n[AUTO-MAPPED] {len(auto_map)} events from page_range fuzzy lookup")

    # ── Mode 2: review-aware mapping (apply K/F/R/ADD) ───────────────────────
    if REVIEW_CSV_PATH.exists():
        review_df = load_review(REVIEW_CSV_PATH)
        print(f"\nLoaded review CSV: {len(review_df)} rows")

        event_map, removed, added = apply_review(review_df, periods)
        print(f"\n[REVIEW-APPLIED] event_period_map: {len(event_map)} events")
        print(f"  K (Keep)   : {sum(1 for v in event_map.values() if v.get('source') == 'K')}")
        print(f"  F (Fix)    : {sum(1 for v in event_map.values() if v.get('source') == 'F')}")
        print(f"  ADD        : {sum(1 for v in event_map.values() if v.get('source') == 'ADD')}")
        print(f"  R (Removed): {len(removed)} events excluded")

        _print_summary(periods, event_map)

        if removed:
            print(f"\n REMOVED events ({len(removed)}):")
            for name in sorted(removed):
                print(f"    - {name}")

        if added:
            print(f"\n ADD events ({len(added)}):")
            for entry in added:
                print(f"    + {entry['event_name']:<30s} -> {entry['period_id']} ({entry['period_label']}, p.{entry['correct_pages']})")
    elif NODES_CSV_PATH.exists():
        # Fallback: tunjukkan auto-map saja kalau review belum ada
        _print_summary(periods, auto_map)
    else:
        print(f"\nNodes file missing: {NODES_CSV_PATH}")
