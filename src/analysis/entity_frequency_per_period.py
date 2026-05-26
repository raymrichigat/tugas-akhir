"""
entity_frequency_per_period.py
==============================
Hitung frekuensi kemunculan PERSON / EVENT / LOCATION / TIME per 15 period
(P0-P14) berdasarkan `nodes_v2.csv` (manual labelling) + chunk-to-period mapping
via `sirah_chunks_final.csv`.

Latar belakang revisi 2026-05-16 (Bu Diana):
> "Untuk ekstraksi relasi ini bisa di amati frekuensi (kemunculan dalam suatu
>  periodisasi) nah ini gapapa dicoba untuk dijustifikasi bagaimana hasilnya"

**Catatan teknis penting:**
Field `periode_bab` di `nodes_v2.csv` hanya populated untuk **EVENT** (36 dari 892
nodes), karena hanya Event yang punya anchor temporal langsung. Untuk PERSON /
LOCATION / TIME yang muncul di banyak period, kita resolve period via:

    nodes_v2.chunk_ids (mis. "000354-001 | 000071-003")
      -> split per chunk_id
      -> lookup sirah_chunks_final.csv: chunk_id -> halaman
      -> parse first page
      -> map to period via period_mapping.json page_start <= page <= page_end

Tiap entitas bisa muncul di **beberapa period** (mis. Muhammad muncul di P0-P14).
Kita count "berapa kali entitas ini di-mention per period" = jumlah chunk_ids
entitas itu yang masuk period tersebut.

Tujuan analisis:
  - Lihat dominasi entitas per periode Sirah (Makkah pra-Hijrah vs Madinah pasca).
  - Justifikasi struktur naratif buku Mubarakfuri lewat distribusi entitas.
  - Sebagai baseline untuk komparasi setelah inference NER selesai (rerun di v3).

Input:
  - data/result/relation_result/nodes_v2.csv  (manual labelling, 892 nodes)
  - data/result/relation_result/period_mapping.json (15 period P0-P14)
  - data/result/chunking_result/sirah_chunks_final.csv (chunk_id -> halaman)

Output:
  - data/result/analysis/entity_freq_per_period.csv     — long format
  - data/result/analysis/entity_freq_per_period_pivot.csv — pivoted (period x label)
  - data/result/analysis/entity_freq_per_period.png     — bar chart per label
  - data/result/analysis/entity_freq_per_period_summary.md — narrative summary
  - data/result/analysis/top_entities_per_period.csv    — top-5 entitas per period x label

Idempotent. Usage:
  python entity_frequency_per_period.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NODES_CSV = ROOT / "data" / "result" / "relation_result" / "nodes_v2.csv"
PERIOD_JSON = ROOT / "data" / "result" / "relation_result" / "period_mapping.json"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ENTITY_TYPES = ("PERSON", "EVENT", "LOCATION", "TIME")
PERIOD_ORDER = [f"P{i}" for i in range(15)]


def load_period_meta() -> tuple[dict[str, dict], list[dict]]:
    with open(PERIOD_JSON, encoding="utf-8") as f:
        periods = json.load(f)
    meta = {
        p["period_id"]: {
            "label": p["label"],
            "phase": p["phase"],
            "page_start": p["page_start"],
            "page_end": p["page_end"],
        }
        for p in periods
    }
    return meta, periods


def build_chunk_to_period(periods: list[dict]) -> dict[str, str]:
    """Map chunk_id -> period_id via halaman (first page)."""
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig")
    chunks["first_page"] = chunks["halaman"].astype(str).str.extract(r"^(\d+)").astype(float)
    chunk_to_period: dict[str, str] = {}
    for _, row in chunks.iterrows():
        if pd.isna(row["first_page"]):
            continue
        page = int(row["first_page"])
        for period in periods:
            if period["page_start"] <= page <= period["page_end"]:
                chunk_to_period[row["chunk_id"]] = period["period_id"]
                break
    return chunk_to_period


def split_chunk_ids(s: str) -> list[str]:
    """Split kolom `chunk_ids` yang formatnya 'a | b | c' atau ekstrak ID 6-3 digit."""
    if not isinstance(s, str):
        return []
    parts = [p.strip() for p in s.split("|") if p.strip()]
    cleaned = []
    for p in parts:
        m = re.search(r"\d{6}-\d{3}", p)
        if m:
            cleaned.append(m.group(0))
    return cleaned


def main():
    period_meta, periods = load_period_meta()
    chunk_to_period = build_chunk_to_period(periods)
    print(f"[load] {len(chunk_to_period)} chunks mapped to period")

    nodes = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig")
    nodes = nodes[nodes["label"].isin(ENTITY_TYPES)].copy()
    print(f"[filter] {len(nodes)} nodes (PERSON/EVENT/LOCATION/TIME)")

    # ─── Resolve period per entity x chunk_id ──────────────────────────────
    # Build long format: [name, label, period_id, chunk_id]
    rows_per_chunk: list[dict] = []
    n_unmapped_chunks = 0
    for _, row in nodes.iterrows():
        chunk_ids = split_chunk_ids(row.get("chunk_ids", ""))
        if not chunk_ids:
            continue
        for cid in chunk_ids:
            pid = chunk_to_period.get(cid)
            if pid is None:
                n_unmapped_chunks += 1
                continue
            rows_per_chunk.append({
                "name": row["name"],
                "label": row["label"],
                "period_id": pid,
                "chunk_id": cid,
            })
    df_long_chunks = pd.DataFrame(rows_per_chunk)
    print(f"[resolve] {len(df_long_chunks)} (entity, chunk_id) tuples assigned to period")
    print(f"          {n_unmapped_chunks} chunk_ids unmapped (page out of range)")

    # ─── Aggregate ────────────────────────────────────────────────────────
    # Three metrics:
    #   (a) unique_entities    — jumlah unique entity nama yang muncul di period
    #   (b) total_occurrences  — sum count entity x chunk muncul di period
    #   (c) chunks_with_entity — jumlah chunk distinct di period yang punya min 1 entity
    rows = []
    for pid in PERIOD_ORDER:
        sub = df_long_chunks[df_long_chunks["period_id"] == pid]
        for etype in ENTITY_TYPES:
            sub_e = sub[sub["label"] == etype]
            unique_entities = sub_e["name"].nunique()
            total_occurrences = len(sub_e)
            chunks_with_entity = sub_e["chunk_id"].nunique()
            rows.append({
                "period_id": pid,
                "period_label": period_meta[pid]["label"],
                "phase": period_meta[pid]["phase"],
                "entity_type": etype,
                "unique_entities": unique_entities,
                "total_occurrences": total_occurrences,
                "chunks_with_entity": chunks_with_entity,
            })

    df_long = pd.DataFrame(rows)
    long_path = OUT_DIR / "entity_freq_per_period.csv"
    df_long.to_csv(long_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"[write] {long_path}")

    # ─── Pivot ────────────────────────────────────────────────────────────
    pivot_unique = df_long.pivot_table(
        index=["period_id", "period_label", "phase"],
        columns="entity_type",
        values="unique_entities",
        aggfunc="sum",
    ).fillna(0).astype(int).reset_index()
    pivot_unique = pivot_unique.reindex(
        columns=["period_id", "period_label", "phase"] + list(ENTITY_TYPES)
    )
    pivot_unique["TOTAL"] = pivot_unique[list(ENTITY_TYPES)].sum(axis=1)
    pivot_unique = pivot_unique.sort_values("period_id", key=lambda s: s.str[1:].astype(int))

    pivot_occ = df_long.pivot_table(
        index=["period_id", "period_label", "phase"],
        columns="entity_type",
        values="total_occurrences",
        aggfunc="sum",
    ).fillna(0).astype(int).reset_index()
    pivot_occ = pivot_occ.reindex(
        columns=["period_id", "period_label", "phase"] + list(ENTITY_TYPES)
    )
    pivot_occ["TOTAL"] = pivot_occ[list(ENTITY_TYPES)].sum(axis=1)
    pivot_occ = pivot_occ.sort_values("period_id", key=lambda s: s.str[1:].astype(int))

    pivot_combined_path = OUT_DIR / "entity_freq_per_period_pivot.csv"
    with open(pivot_combined_path, "w", encoding="utf-8-sig") as f:
        f.write("# Pivot: unique entities per period x entity_type\n")
        pivot_unique.to_csv(f, index=False, sep=";", lineterminator="\n")
        f.write("\n# Pivot: total occurrences (entity-chunk tuples) per period x entity_type\n")
        pivot_occ.to_csv(f, index=False, sep=";", lineterminator="\n")
    print(f"[write] {pivot_combined_path}")

    # ─── Top-N entities per period x label ────────────────────────────────
    top_rows = []
    for pid in PERIOD_ORDER:
        sub_p = df_long_chunks[df_long_chunks["period_id"] == pid]
        for etype in ENTITY_TYPES:
            sub_pe = sub_p[sub_p["label"] == etype]
            top = sub_pe["name"].value_counts().head(5)
            for rank, (name, count) in enumerate(top.items(), start=1):
                top_rows.append({
                    "period_id": pid,
                    "period_label": period_meta[pid]["label"],
                    "entity_type": etype,
                    "rank": rank,
                    "name": name,
                    "occurrences": count,
                })
    df_top = pd.DataFrame(top_rows)
    top_path = OUT_DIR / "top_entities_per_period.csv"
    df_top.to_csv(top_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"[write] {top_path}")

    # ─── Visualisasi ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    pivot_for_unique = (
        df_long.pivot_table(
            index="period_id", columns="entity_type",
            values="unique_entities", aggfunc="sum",
        )
        .fillna(0)
        .reindex(PERIOD_ORDER)
        .fillna(0)
    )
    pivot_for_unique[list(ENTITY_TYPES)].plot(
        kind="bar", ax=axes[0],
        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
    )
    axes[0].set_title("Unique Entitas per Period (manual labelling, nodes_v2.csv)")
    axes[0].set_xlabel("Period")
    axes[0].set_ylabel("Jumlah unique entitas")
    axes[0].legend(title="Entity type")
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    pivot_for_occ = (
        df_long.pivot_table(
            index="period_id", columns="entity_type",
            values="total_occurrences", aggfunc="sum",
        )
        .fillna(0)
        .reindex(PERIOD_ORDER)
        .fillna(0)
    )
    pivot_for_occ[list(ENTITY_TYPES)].plot(
        kind="bar", ax=axes[1],
        color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
    )
    axes[1].set_title("Total Occurrences per Period (entity x chunk_id)")
    axes[1].set_xlabel("Period")
    axes[1].set_ylabel("Total occurrences")
    axes[1].legend(title="Entity type")
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    png_path = OUT_DIR / "entity_freq_per_period.png"
    plt.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"[write] {png_path}")

    # ─── Narrative summary (markdown, plain table format) ─────────────────
    def df_to_md_table(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        header = "| " + " | ".join(cols) + " |"
        sep = "|" + "|".join(["---"] * len(cols)) + "|"
        body_rows = []
        for _, r in df.iterrows():
            body_rows.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        return "\n".join([header, sep] + body_rows)

    lines = [
        "# Frekuensi Entitas per Period — Manual Labelling (nodes_v2.csv)",
        "",
        "**Sumber:** `nodes_v2.csv` (892 nodes hasil manual labelling Sirah Mubarakfuri,",
        "post review periodisasi 2026-05-12). Mapping chunk_id → period via",
        "`sirah_chunks_final.csv` (halaman) + `period_mapping.json` v2 (page range).",
        "",
        f"**Coverage:** {len(df_long_chunks)} (entity, chunk) tuples successfully assigned",
        f"to 1 dari 15 period. {n_unmapped_chunks} unmapped (chunk halaman > 600, end-matter).",
        "",
        "## Pivot — Unique Entities per Period",
        "",
        "Setiap kolom hitung **unique** entity name yang muncul di period itu.",
        "Catatan: entity yang sama bisa muncul di beberapa period (mis. Muhammad",
        "muncul di P0-P14), jadi sum kolom > unique-entity-total di nodes_v2.",
        "",
        df_to_md_table(pivot_unique),
        "",
        "## Pivot — Total Occurrences per Period",
        "",
        "Hitung pasangan (entity, chunk_id) — proxy untuk seberapa sering entity",
        "muncul dalam narasi period. Lebih tinggi = lebih banyak penyebutan.",
        "",
        df_to_md_table(pivot_occ),
        "",
        "## Observasi awal",
        "",
    ]

    if "PERSON" in pivot_unique.columns:
        max_p = pivot_unique.loc[pivot_unique["PERSON"].idxmax()]
        min_p = pivot_unique.loc[pivot_unique["PERSON"].idxmin()]
        lines.append(
            f"- **PERSON dominan di** {max_p['period_id']} "
            f"(`{max_p['period_label']}`) dengan **{max_p['PERSON']}** unique entitas."
        )
        lines.append(
            f"- **PERSON paling sedikit di** {min_p['period_id']} "
            f"(`{min_p['period_label']}`) dengan **{min_p['PERSON']}** unique entitas."
        )
    if "EVENT" in pivot_unique.columns:
        max_e = pivot_unique.loc[pivot_unique["EVENT"].idxmax()]
        lines.append(
            f"- **EVENT dominan di** {max_e['period_id']} "
            f"(`{max_e['period_label']}`) dengan **{max_e['EVENT']}** unique events."
        )
        zero_e = pivot_unique[pivot_unique["EVENT"] == 0]
        if len(zero_e) > 0:
            zlist = ", ".join(zero_e["period_id"].tolist())
            lines.append(
                f"- **Period tanpa EVENT entitas:** {zlist} "
                f"(kandidat untuk EVENT augmentation target)."
            )
    if "LOCATION" in pivot_unique.columns:
        max_l = pivot_unique.loc[pivot_unique["LOCATION"].idxmax()]
        lines.append(
            f"- **LOCATION dominan di** {max_l['period_id']} "
            f"(`{max_l['period_label']}`) dengan **{max_l['LOCATION']}** unique lokasi."
        )

    lines += [
        "",
        "## Top 5 Entitas per Period (PERSON saja, untuk gambaran narasi)",
        "",
    ]
    person_top = df_top[df_top["entity_type"] == "PERSON"].copy()
    if len(person_top):
        for pid in PERIOD_ORDER:
            sub = person_top[person_top["period_id"] == pid].head(5)
            if len(sub) == 0:
                continue
            label = period_meta[pid]["label"]
            lines.append(f"### {pid} — {label}")
            lines.append("")
            for _, r in sub.iterrows():
                lines.append(f"  {r['rank']}. **{r['name']}** ({r['occurrences']} occurrences)")
            lines.append("")

    lines += [
        "## Implikasi untuk Bab 4",
        "",
        "1. Dominasi entitas per period dapat dipakai sebagai justifikasi struktur naratif",
        "   buku Mubarakfuri — period dengan event-density tinggi (mis. P8 Perang Badr,",
        "   P9 Pasca-Badr) mengandung lebih banyak entitas PERSON & EVENT.",
        "2. Period dengan EVENT pool kecil konsisten dengan filosofi buku Sirah yang fokus",
        "   pada karakter & dakwah (banyak PERSON, sedikit EVENT) pada fase pra-peperangan.",
        "3. Saat dijalankan di output SRL-NER (post-S3.1/S3.2), kita bisa quantify",
        "   dampak augmentation terhadap distribusi minor classes (B-EVENT, I-LOCATION)",
        "   per period — apakah augmentation menyamaratakan atau mempertahankan struktur.",
        "",
    ]

    summary_path = OUT_DIR / "entity_freq_per_period_summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[write] {summary_path}")

    print("\n=== Pivot Unique Entities ===")
    print(pivot_unique.to_string(index=False))


if __name__ == "__main__":
    main()
