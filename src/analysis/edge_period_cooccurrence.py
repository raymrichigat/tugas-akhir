"""
edge_period_cooccurrence.py
============================
Analisis frekuensi co-occurrence relasi (source-target pair) per period sebagai
justifikasi/filter validitas relasi di Knowledge Graph Sirah.

Latar belakang revisi 2026-05-16 (Bu Diana):
> "Untuk ekstraksi relasi ini bisa di amati frekuensi (kemunculan dalam suatu
>  periodisasi) nah ini gapapa dicoba untuk dijustifikasi bagaimana hasilnya"

**Interpretasi (post-klarifikasi):** bukan frekuensi entitas per period, tapi
frekuensi co-occurrence relasi per period — untuk filter relasi spurious dari
proximity-based extraction.

**Contoh kasus motivasi:**
  Perang Uhud --[OCCURRED_AT]--> Aqabah (freq=1)
  Perang Uhud --[OCCURRED_AT]--> Madinah (freq=3)  ← correct
  Perang Uhud --[OCCURRED_AT]--> Hunain (freq=1)

Aqabah natural period = P5 (Baiat Aqabah pre-Hijrah), Hunain = P13.
Perang Uhud natural period = P9. Co-occurrence Uhud-Aqabah dan Uhud-Hunain
adalah artifact proximity rule, bukan relasi historis.

**Algoritma:**
1. Untuk tiap edge di edges_v2.csv, split chunk_id (pipe-separated)
2. Map tiap chunk → period via sirah_chunks_final.csv + period_mapping.json
3. Count co-occurrence per period (n_chunks_in_period)
4. Untuk EVENT entities, lookup natural period dari nodes_v2.csv (page_range)
5. Period alignment check: edge co-occur period match dengan natural period EVENT?
6. Verdict heuristic:
     KEEP   if frequency >= 2 AND period_aligned
     REVIEW if frequency >= 2 AND NOT period_aligned (worth manual check)
     REVIEW if frequency = 1 AND period_aligned (single mention, but in correct period)
     DROP   if frequency = 1 AND NOT period_aligned (likely spurious proximity)
     REVIEW if no EVENT in edge (period alignment N/A) — fallback to frequency
            >= 2 = KEEP, else REVIEW

Input:
  - data/result/relation_result/edges_v2.csv
  - data/result/relation_result/nodes_v2.csv
  - data/result/relation_result/period_mapping.json
  - data/result/chunking_result/sirah_chunks_final.csv

Output:
  - data/result/analysis/edge_period_cooccurrence.csv
  - data/result/analysis/edge_validation_summary.csv
  - data/result/analysis/edge_validation_summary.md

Idempotent. Usage:
  python edge_period_cooccurrence.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EDGES_CSV = ROOT / "data" / "result" / "relation_result" / "edges_v2.csv"
NODES_CSV = ROOT / "data" / "result" / "relation_result" / "nodes_v2.csv"
PERIOD_JSON = ROOT / "data" / "result" / "relation_result" / "period_mapping.json"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PERIOD_ORDER = [f"P{i}" for i in range(15)]


def load_period_meta() -> tuple[dict[str, dict], list[dict]]:
    with open(PERIOD_JSON, encoding="utf-8") as f:
        periods = json.load(f)
    meta = {p["period_id"]: p for p in periods}
    return meta, periods


def build_chunk_to_period(periods: list[dict]) -> dict[str, str]:
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig")
    chunks["first_page"] = chunks["halaman"].astype(str).str.extract(r"^(\d+)").astype(float)
    out = {}
    for _, row in chunks.iterrows():
        if pd.isna(row["first_page"]):
            continue
        p = int(row["first_page"])
        for period in periods:
            if period["page_start"] <= p <= period["page_end"]:
                out[row["chunk_id"]] = period["period_id"]
                break
    return out


def page_range_to_periods(page_range: str, periods: list[dict]) -> list[str]:
    """
    Parse page_range (mis. "266-304" atau "324-375") ke daftar period_id yang
    overlap dengan range itu. Untuk EVENT yang spans multiple period, semua di-include.
    """
    if not isinstance(page_range, str):
        return []
    m = re.match(r"^(\d+)\s*-\s*(\d+)$", page_range.strip())
    if m:
        start, end = int(m.group(1)), int(m.group(2))
    else:
        m2 = re.match(r"^(\d+)$", page_range.strip())
        if not m2:
            return []
        start = end = int(m2.group(1))
    out = []
    for period in periods:
        # overlap check
        if not (end < period["page_start"] or start > period["page_end"]):
            out.append(period["period_id"])
    return out


def split_chunk_ids(s) -> list[str]:
    """Parse 'a | b | c' atau extract 6-3 digit IDs."""
    if not isinstance(s, str):
        return []
    parts = [p.strip() for p in s.split("|") if p.strip()]
    out = []
    for p in parts:
        m = re.search(r"\d{6}-\d{3}", p)
        if m:
            out.append(m.group(0))
    return out


def main():
    period_meta, periods = load_period_meta()
    chunk_to_period = build_chunk_to_period(periods)
    print(f"[load] {len(chunk_to_period)} chunks mapped to period")

    # Build entity → natural_periods (set of period_ids)
    nodes = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig")
    entity_natural_periods: dict[tuple[str, str], list[str]] = {}
    for _, row in nodes.iterrows():
        key = (row["name"], row["label"])
        if pd.notna(row.get("page_range")):
            entity_natural_periods[key] = page_range_to_periods(row["page_range"], periods)
        else:
            entity_natural_periods[key] = []

    # Count how many EVENT entities have natural period
    event_with_period = sum(
        1 for (_, lab), p in entity_natural_periods.items()
        if lab == "EVENT" and p
    )
    n_events = sum(1 for (_, lab) in entity_natural_periods if lab == "EVENT")
    print(f"[load] {len(nodes)} nodes; {event_with_period}/{n_events} EVENT punya natural period")

    # Load edges
    edges = pd.read_csv(EDGES_CSV, sep=";", encoding="utf-8-sig")
    print(f"[load] {len(edges)} edges")

    # ─── Build long-format: per (edge_idx, period_id, n_chunks_in_period) ──
    cooc_rows = []
    for idx, edge in edges.iterrows():
        chunk_ids = split_chunk_ids(edge.get("chunk_id"))
        if not chunk_ids:
            continue
        period_counts = Counter()
        for cid in chunk_ids:
            pid = chunk_to_period.get(cid)
            if pid:
                period_counts[pid] += 1

        # Get natural periods for source & target if any is EVENT
        src_periods = entity_natural_periods.get(
            (edge["source_name"], edge["source_label"]), []
        )
        tgt_periods = entity_natural_periods.get(
            (edge["target_name"], edge["target_label"]), []
        )
        # Take EVENT-side natural periods as ground truth
        event_periods = []
        if edge["source_label"] == "EVENT":
            event_periods.extend(src_periods)
        if edge["target_label"] == "EVENT":
            event_periods.extend(tgt_periods)
        event_periods = sorted(set(event_periods))
        has_event = bool(event_periods)

        for pid, n in period_counts.items():
            aligned = pid in event_periods if has_event else None
            cooc_rows.append({
                "edge_idx": idx,
                "source_name": edge["source_name"],
                "source_label": edge["source_label"],
                "relation_type": edge["relation_type"],
                "target_name": edge["target_name"],
                "target_label": edge["target_label"],
                "period_id": pid,
                "period_label": period_meta[pid]["label"],
                "n_chunks_in_period": n,
                "event_natural_periods": ",".join(event_periods) if event_periods else "",
                "aligned": aligned,
            })

    df_cooc = pd.DataFrame(cooc_rows)
    cooc_path = OUT_DIR / "edge_period_cooccurrence.csv"
    df_cooc.to_csv(cooc_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"[write] {cooc_path}")

    # ─── Verdict per edge ──────────────────────────────────────────────────
    verdict_rows = []
    for idx, edge in edges.iterrows():
        chunk_ids = split_chunk_ids(edge.get("chunk_id"))
        period_counts = Counter()
        for cid in chunk_ids:
            pid = chunk_to_period.get(cid)
            if pid:
                period_counts[pid] += 1

        total_freq = int(edge.get("frequency", 0)) if pd.notna(edge.get("frequency")) else len(chunk_ids)
        n_periods_covered = len(period_counts)
        dominant_period = period_counts.most_common(1)[0][0] if period_counts else None
        dominant_count = period_counts.most_common(1)[0][1] if period_counts else 0

        src_periods = entity_natural_periods.get(
            (edge["source_name"], edge["source_label"]), []
        )
        tgt_periods = entity_natural_periods.get(
            (edge["target_name"], edge["target_label"]), []
        )
        event_periods = []
        if edge["source_label"] == "EVENT":
            event_periods.extend(src_periods)
        if edge["target_label"] == "EVENT":
            event_periods.extend(tgt_periods)
        event_periods = sorted(set(event_periods))
        has_event = bool(event_periods)

        # Check alignment of dominant period
        if has_event:
            aligned_dominant = dominant_period in event_periods
            # Alignment ratio: % chunks in aligned periods
            aligned_chunks = sum(n for p, n in period_counts.items() if p in event_periods)
            alignment_ratio = aligned_chunks / sum(period_counts.values()) if period_counts else 0.0
        else:
            aligned_dominant = None
            alignment_ratio = None

        # Verdict heuristic
        if has_event:
            if total_freq >= 2 and aligned_dominant:
                verdict = "KEEP"
                reason = "freq>=2 + dominant period aligned with event"
            elif total_freq >= 2 and not aligned_dominant:
                verdict = "REVIEW"
                reason = f"freq>=2 but dominant period {dominant_period} != event natural period {event_periods}"
            elif total_freq == 1 and aligned_dominant:
                verdict = "REVIEW"
                reason = "single mention, but in aligned period"
            else:  # freq==1 and not aligned
                verdict = "DROP"
                reason = f"single mention in non-aligned period {dominant_period} (event natural: {event_periods})"
        else:
            # No event — fallback to frequency-only
            if total_freq >= 2:
                verdict = "KEEP"
                reason = "freq>=2, no event anchor (period alignment N/A)"
            else:
                verdict = "REVIEW"
                reason = "freq=1, no event anchor — manual review"

        verdict_rows.append({
            "edge_idx": idx,
            "source_name": edge["source_name"],
            "source_label": edge["source_label"],
            "relation_type": edge["relation_type"],
            "target_name": edge["target_name"],
            "target_label": edge["target_label"],
            "total_frequency": total_freq,
            "n_periods_covered": n_periods_covered,
            "dominant_period": dominant_period,
            "dominant_count": dominant_count,
            "event_natural_periods": ",".join(event_periods) if event_periods else "",
            "aligned_dominant": aligned_dominant,
            "alignment_ratio": (
                round(alignment_ratio, 3) if alignment_ratio is not None else ""
            ),
            "verdict": verdict,
            "reason": reason,
        })

    df_verdict = pd.DataFrame(verdict_rows)
    verdict_path = OUT_DIR / "edge_validation_summary.csv"
    df_verdict.to_csv(verdict_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"[write] {verdict_path}")

    # ─── Stats & narrative summary (markdown) ──────────────────────────────
    n_total = len(df_verdict)
    n_keep = (df_verdict["verdict"] == "KEEP").sum()
    n_review = (df_verdict["verdict"] == "REVIEW").sum()
    n_drop = (df_verdict["verdict"] == "DROP").sum()

    by_relation = df_verdict.groupby(["relation_type", "verdict"]).size().unstack(fill_value=0)
    by_relation = by_relation.reindex(columns=["KEEP", "REVIEW", "DROP"], fill_value=0)
    by_relation["TOTAL"] = by_relation.sum(axis=1)

    # Top suspicious edges (DROP, sorted by relation_type)
    drops = df_verdict[df_verdict["verdict"] == "DROP"].copy()
    drops_by_rel = drops.groupby("relation_type").size().sort_values(ascending=False)

    # Top edges that need review per relation type
    reviews = df_verdict[df_verdict["verdict"] == "REVIEW"]
    reviews_by_rel = reviews.groupby("relation_type").size().sort_values(ascending=False)

    def df_to_md(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        header = "| " + " | ".join(str(c) for c in cols) + " |"
        sep = "|" + "|".join(["---"] * len(cols)) + "|"
        rows = []
        for _, r in df.iterrows():
            rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        return "\n".join([header, sep] + rows)

    lines = [
        "# Edge Validation via Co-occurrence per Period",
        "",
        "**Tanggal:** 2026-05-22",
        "",
        "**Latar belakang:** Bu Diana di bimbingan 2026-05-16 minta analisis frekuensi",
        "co-occurrence relasi per period sebagai justifikasi validitas relasi di KG.",
        "",
        "**Motivasi:** ekstraksi relasi pakai proximity rule global → menghasilkan relasi",
        "spurious seperti `Perang Uhud --OCCURRED_AT--> Aqabah` (semantically wrong;",
        "Uhud period P9, Aqabah natural period P5).",
        "",
        "## Summary",
        "",
        f"- Total edges di edges_v2.csv: **{n_total}**",
        f"- KEEP   (high-confidence): **{n_keep}** ({100*n_keep/n_total:.1f}%)",
        f"- REVIEW (need manual confirm): **{n_review}** ({100*n_review/n_total:.1f}%)",
        f"- DROP   (likely spurious): **{n_drop}** ({100*n_drop/n_total:.1f}%)",
        "",
        "## Verdict per Relation Type",
        "",
        df_to_md(by_relation.reset_index()),
        "",
        "## DROP Distribution per Relation",
        "",
    ]
    for rel, n in drops_by_rel.items():
        lines.append(f"- `{rel}`: **{n}** edges flagged DROP")
    lines.append("")

    lines += [
        "## Top 15 DROP Edges (most suspicious)",
        "",
        "Edge yang **single mention di period yang tidak align** dengan natural period EVENT.",
        "",
    ]
    drop_sample = drops.sort_values(["relation_type", "source_name"]).head(15)
    sample_cols = ["source_name", "relation_type", "target_name",
                   "total_frequency", "dominant_period", "event_natural_periods"]
    lines.append(df_to_md(drop_sample[sample_cols]))
    lines.append("")

    lines += [
        "## Specific Case: Perang Uhud Relations",
        "",
        "Validasi anekdot dari kasus motivasi Bu Diana.",
        "",
    ]
    uhud = df_verdict[
        (df_verdict["source_name"] == "Perang Uhud") |
        (df_verdict["target_name"] == "Perang Uhud")
    ].copy()
    uhud_cols = ["source_name", "relation_type", "target_name",
                 "total_frequency", "dominant_period", "alignment_ratio", "verdict"]
    lines.append(df_to_md(uhud[uhud_cols]))
    lines.append("")

    lines += [
        "## Implikasi & Next Action",
        "",
        f"1. **Filter strict:** drop {n_drop} edges → edges_v3.csv punya "
        f"{n_total - n_drop} edges. Trade-off: edges turun "
        f"{100*n_drop/n_total:.1f}%, semantic accuracy naik.",
        f"2. **Manual review {n_review} REVIEW edges** sebelum apply ke v3 — terutama",
        "   yang freq>=2 tapi period mismatch (kemungkinan ada nuansa naratif).",
        "3. **Fix proximity extraction** di `relation_extraction.py`:",
        "   - Tambah period-aware filter saat scanning kalimat",
        "   - Jangan create edge antara entitas dari period yang jauh berbeda",
        "4. **Validasi case study:** Perang Uhud-Aqabah, Perang Uhud-Hunain confirmed",
        "   spurious. Run pattern check serupa untuk Perang Badr, Perjanjian Hudaibiyah, dll.",
        "",
        "## Catatan Jujur",
        "",
        "- **Heuristic verdict bukan ground truth** — kasus borderline (event yang valid",
        "  spans multiple periods, mis. Perjanjian Hudaibiyah berimplikasi sampai Fathu",
        "  Makkah) bisa false-flag DROP. Wajib manual review sebelum apply.",
        "- **Edges tanpa EVENT** (PERSON-PERSON KELUARGA, dll) tidak bisa di-validate",
        "  via period alignment — fallback frequency-only. Kasus seperti family relation",
        "  yang cuma single-mention butuh manual review.",
        "- **Page_range EVENT** di nodes_v2 kadang melebar ke beberapa period (mis.",
        "  Perang Khaibar 473-492 = P11 saja). Tapi event yang spans 2-3 period akan",
        "  match ke semua period itu (overlap detection).",
        "",
    ]

    summary_path = OUT_DIR / "edge_validation_summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[write] {summary_path}")

    # Print quick stats to stdout
    print()
    print(f"=== Summary ===")
    print(f"  Total edges     : {n_total}")
    print(f"  KEEP            : {n_keep} ({100*n_keep/n_total:.1f}%)")
    print(f"  REVIEW          : {n_review} ({100*n_review/n_total:.1f}%)")
    print(f"  DROP            : {n_drop} ({100*n_drop/n_total:.1f}%)")
    print()
    print("Verdict by relation_type:")
    print(by_relation.to_string())


if __name__ == "__main__":
    main()
