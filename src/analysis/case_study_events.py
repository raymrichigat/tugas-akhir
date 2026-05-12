"""
case_study_events.py
====================
Studi kasus 3-5 event berperiode jauh — revisi Bu Diana cluster #2 (2026-05-03):

  > "Kasus perang badar, diamati keterlibatan nya apa saja lalu diamati graf nya
  > (sampling beberapa event). Kalo misalnya kesalahan dari awal, nanti akan
  > berpengaruh ke perhitungan fitur nya (ambil beberapa contoh 3 atau 5 fitur,
  > dengan periode yang jauh. Tunjukkan dalam graf seperti apa lalu di analisis)."

Pendekatan:
  1. Pilih 5 event yang span periode berjauhan (P8 → P13, ~300 halaman jarak).
  2. Untuk tiap event, extract sub-graph: {event} ∪ {Person INVOLVED_IN}
     ∪ {Location OCCURRED_AT} ∪ {Time OCCURRED_ON}.
  3. Hitung sub-graph metrics:
     - n_persons, n_locations, n_times
     - Person-Person co-participation density dalam sub-graph
     - Top 5 Person by degree dalam sub-graph
  4. Output:
     - markdown report dengan table per event
     - Cypher queries untuk visualisasi di Neo4j

Input:
  - data/result/relation_result/nodes_v2.csv
  - data/result/relation_result/edges_v2.csv

Output:
  - data/result/analysis/case_study_events.md
  - data/result/analysis/case_study_events_cypher.md
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
NODES_CSV = BASE_DIR / "data" / "result" / "relation_result" / "nodes_v2.csv"
EDGES_CSV = BASE_DIR / "data" / "result" / "relation_result" / "edges_v2.csv"
OUT_DIR = BASE_DIR / "data" / "result" / "analysis"


# ── Pilihan 5 event studi kasus ──────────────────────────────────────────────
# Format: event_name, period_id, period_label, justifikasi pemilihan
CASE_STUDIES = [
    ("Perang Badr",             "P8",  "Perang Badr & Dampaknya",
     "Frequency tertinggi (44) — peperangan kunci awal periode Madinah, milestone teologis (penaklukan Quraisy pertama)"),
    ("Perang Uhud",             "P9",  "Perang Uhud & Satuan Pasukan Pasca Uhud",
     "Kekalahan strategis pertama umat Islam; trauma & konsolidasi pasca-perang"),
    ("Perjanjian Hudaibiyah",   "P11", "Hudaibiyah & Babak Baru Diplomasi",
     "Diplomatic milestone — gencatan senjata yang membuka era ekspansi non-militer"),
    ("Perang Khaibar",          "P11", "Hudaibiyah & Babak Baru Diplomasi",
     "Post-Hudaibiyah, melawan komunitas Yahudi terbesar di sekitar Madinah"),
    ("Perang Tabuk",            "P13", "Hunain, Tabuk & Puncak Kekuatan Islam",
     "Ekspedisi militer terakhir Nabi — terhadap Romawi, mencapai batas utara Jazirah Arab"),
]


# ── Sub-graph extraction ─────────────────────────────────────────────────────
def extract_event_subgraph(event_name: str, edges_df: pd.DataFrame, nodes_df: pd.DataFrame) -> dict:
    """
    Extract sub-graph centered on `event_name`. Returns dict with:
      - event: event node info
      - persons: list of Person names INVOLVED_IN event
      - locations: list of Location names OCCURRED_AT event
      - times: list of Time names OCCURRED_ON event
      - person_pairs: list of (p1, p2, n_shared) — co-participation dengan
        person lain via event ini (cuma kalau pernah co-occur di event yang sama)
    """
    # Person -INVOLVED_IN-> Event
    persons = edges_df[
        (edges_df["relation_type"] == "INVOLVED_IN")
        & (edges_df["target_name"] == event_name)
    ]["source_name"].unique().tolist()

    # Event -OCCURRED_AT-> Location
    locations = edges_df[
        (edges_df["relation_type"] == "OCCURRED_AT")
        & (edges_df["source_name"] == event_name)
    ]["target_name"].unique().tolist()

    # Event -OCCURRED_ON-> Time
    times = edges_df[
        (edges_df["relation_type"] == "OCCURRED_ON")
        & (edges_df["source_name"] == event_name)
    ]["target_name"].unique().tolist()

    # Person-Person co-participation: pairs of persons yang sama-sama INVOLVED_IN event ini
    person_pairs = list(combinations(sorted(persons), 2))

    # Get event node info
    ev_row = nodes_df[(nodes_df["name"] == event_name) & (nodes_df["label"] == "EVENT")]
    event_info = ev_row.iloc[0].to_dict() if len(ev_row) else {"name": event_name}

    return {
        "event": event_info,
        "persons": persons,
        "locations": locations,
        "times": times,
        "person_pairs": person_pairs,
    }


def compute_subgraph_metrics(sub: dict, edges_df: pd.DataFrame) -> dict:
    """
    Hitung metrics untuk sub-graph:
      - n_persons, n_locations, n_times, n_pairs
      - person-person density (clique kalau semua persons saling kenal — by definition co-participation in event)
      - top 5 person by degree dalam GLOBAL graph (PageRank atau degree)
      - top 5 person by frequency (jumlah event total yang mereka ikuti)
    """
    persons = sub["persons"]
    n_persons = len(persons)
    n_pairs = len(sub["person_pairs"])
    max_possible_pairs = n_persons * (n_persons - 1) / 2 if n_persons > 1 else 0
    density_in_event = 1.0 if n_pairs > 0 and n_pairs == max_possible_pairs else 0.0
    # Note: untuk sub-graph dari single event, semua person yang INVOLVED_IN otomatis form clique
    # (semuanya pairwise terhubung via this event). Density = 1.0 by construction.

    # Top persons by global involvement frequency
    involvement = edges_df[edges_df["relation_type"] == "INVOLVED_IN"]
    global_freq = involvement.groupby("source_name").size().to_dict()
    persons_sorted = sorted(persons, key=lambda p: -global_freq.get(p, 0))
    top5_by_freq = [(p, global_freq.get(p, 0)) for p in persons_sorted[:5]]

    # Person-Person direct relations (KELUARGA/SAHABAT/MUSUH) dalam scope persons ini
    direct_relations = []
    direct_filter = edges_df[
        edges_df["relation_type"].isin(["KELUARGA", "SAHABAT", "MUSUH"])
        & edges_df["source_name"].isin(persons)
        & edges_df["target_name"].isin(persons)
    ]
    for _, e in direct_filter.iterrows():
        direct_relations.append({
            "source": e["source_name"],
            "target": e["target_name"],
            "type": e["relation_type"],
            "subtype": e.get("relation_subtype", ""),
        })

    return {
        "n_persons": n_persons,
        "n_locations": len(sub["locations"]),
        "n_times": len(sub["times"]),
        "n_pairs": n_pairs,
        "density_in_event": density_in_event,
        "top5_by_global_freq": top5_by_freq,
        "direct_person_relations": direct_relations,
        "n_direct_relations": len(direct_relations),
    }


# ── Cypher query generation ──────────────────────────────────────────────────
def generate_cypher_queries(event_name: str) -> str:
    """Generate Cypher queries untuk visualisasi event sub-graph di Neo4j."""
    safe = event_name.replace('"', '\\"')
    return f"""// === {event_name} ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {{name: "{safe}"}})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {{name: "{safe}"}})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {{name: "{safe}"}})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {{name: "{safe}"}})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {{name: "Perang Uhud"}})
RETURN p.name;
"""


# ── Markdown report ──────────────────────────────────────────────────────────
def format_event_section(event_info: dict, period_id: str, period_label: str,
                         justifikasi: str, sub: dict, metrics: dict) -> list[str]:
    """Format 1 section markdown per event."""
    lines = [
        f"### {event_info['name']}",
        "",
        f"**Period:** `{period_id}` — *{period_label}*",
        f"**Halaman:** {event_info.get('page_range', '?')}",
        f"**Justifikasi pemilihan:** {justifikasi}",
        "",
        f"**Sub-graph metrics:**",
        "",
        f"| Metric | Value |",
        f"|---|---:|",
        f"| Person involved | {metrics['n_persons']} |",
        f"| Location attached | {metrics['n_locations']} |",
        f"| Time attached | {metrics['n_times']} |",
        f"| Pairwise person co-participation | {metrics['n_pairs']} |",
        f"| Density person-clique (by definition all INVOLVED_IN sama event = clique) | {metrics['density_in_event']} |",
        f"| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | {metrics['n_direct_relations']} |",
        "",
    ]

    # Top 5 person by global involvement
    lines += [
        f"**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**",
        "",
        f"| Rank | Person | Total events di-INVOLVED_IN |",
        f"|:---:|---|---:|",
    ]
    for i, (p, freq) in enumerate(metrics["top5_by_global_freq"], 1):
        lines.append(f"| {i} | {p} | {freq} |")

    lines += [
        "",
        f"**Locations:** {', '.join(sub['locations']) if sub['locations'] else '_(tidak ada)_'}",
        "",
        f"**Times:** {', '.join(sub['times']) if sub['times'] else '_(tidak ada)_'}",
        "",
    ]

    if metrics["direct_person_relations"]:
        lines += [
            f"**Direct Person-Person relations dalam scope ({metrics['n_direct_relations']}):**",
            "",
        ]
        # Group by relation type
        by_type: dict[str, list] = {}
        for r in metrics["direct_person_relations"]:
            by_type.setdefault(r["type"], []).append(r)
        for rtype, rels in by_type.items():
            lines.append(f"- **{rtype}** ({len(rels)}):")
            for r in rels[:5]:
                subtype = f" ({r['subtype']})" if r["subtype"] else ""
                lines.append(f"  - `{r['source']}` ↔ `{r['target']}`{subtype}")
            if len(rels) > 5:
                lines.append(f"  - ... (+{len(rels) - 5} lagi)")
        lines.append("")

    # All persons (limited)
    if sub["persons"]:
        lines += [
            f"**Semua Person yang terlibat ({len(sub['persons'])}):**",
            "",
            "<details><summary>klik untuk expand</summary>",
            "",
            ", ".join(sorted(sub["persons"])),
            "",
            "</details>",
            "",
        ]

    return lines


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"[load] {NODES_CSV.name} + {EDGES_CSV.name}")
    nodes_df = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig").fillna("")
    edges_df = pd.read_csv(EDGES_CSV, sep=";", encoding="utf-8-sig").fillna("")
    print(f"  {len(nodes_df)} nodes, {len(edges_df)} edges")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    md_lines = [
        "# Studi Kasus 5 Event Berperiode Jauh — Knowledge Graph Sirah",
        "",
        "Studi kasus mengikuti revisi Bu Diana cluster #2 (2026-05-03):",
        '> *"Kasus Perang Badar, diamati keterlibatan nya apa saja lalu diamati graf nya... ambil beberapa contoh 3 atau 5 event, dengan periode yang jauh. Tunjukkan dalam graf seperti apa lalu di analisis."*',
        "",
        "5 event dipilih dari rentang periodisasi P8 → P13 (page 266 → 571, total ~300 halaman jarak).",
        "",
        "## 1. Ringkasan 5 Event",
        "",
        "| # | Event | Period | Halaman | Persons | Locations | Times |",
        "|:---:|---|---|---|---:|---:|---:|",
    ]

    cypher_lines = [
        "# Cypher Queries untuk Visualisasi Studi Kasus di Neo4j",
        "",
        "Setelah import `import_sirah_v2.cypher`, copy-paste query di bawah ke Neo4j Browser",
        "untuk visualisasi tiap event.",
        "",
    ]

    all_metrics = []
    for i, (event_name, period_id, period_label, justifikasi) in enumerate(CASE_STUDIES, 1):
        print(f"\n[event {i}] {event_name} ({period_id})")
        sub = extract_event_subgraph(event_name, edges_df, nodes_df)
        metrics = compute_subgraph_metrics(sub, edges_df)
        print(f"  persons={metrics['n_persons']} loc={metrics['n_locations']} "
              f"time={metrics['n_times']} direct_rels={metrics['n_direct_relations']}")
        all_metrics.append((event_name, period_id, sub, metrics, justifikasi, period_label))

        md_lines.append(
            f"| {i} | **{event_name}** | {period_id} | {sub['event'].get('page_range', '?')} | "
            f"{metrics['n_persons']} | {metrics['n_locations']} | {metrics['n_times']} |"
        )

    # Combined statistics
    total_unique_persons = set()
    for _, _, sub, _, _, _ in all_metrics:
        total_unique_persons.update(sub["persons"])

    md_lines += [
        "",
        f"**Total unique Person yang muncul di salah satu dari 5 event:** {len(total_unique_persons)}",
        "",
    ]

    person_event_count = Counter()
    person_events = defaultdict(list)
    for ev_name, _, sub, _, _, _ in all_metrics:
        for p in sub["persons"]:
            person_event_count[p] += 1
            person_events[p].append(ev_name)

    multi_event_persons = sorted(
        [(p, c) for p, c in person_event_count.items() if c >= 2],
        key=lambda x: -x[1]
    )
    cross_period_persons = [(p, c) for p, c in multi_event_persons if c >= 3]

    md_lines.append(f"**Person yang muncul di ≥2 event ({len(multi_event_persons)} orang):**")
    md_lines.append("")
    md_lines.append("| Person | Total event | Events |")
    md_lines.append("|---|---:|---|")
    for p, c in multi_event_persons[:20]:
        events_list = ", ".join(person_events[p])
        md_lines.append(f"| {p} | {c} / 5 | {events_list} |")

    if len(multi_event_persons) > 20:
        md_lines.append(f"| ... | | (+{len(multi_event_persons) - 20} lagi) |")

    md_lines += [
        "",
        "## 2. Detail per Event",
        "",
    ]

    for event_name, period_id, sub, metrics, justifikasi, period_label in all_metrics:
        md_lines.extend(format_event_section(
            sub["event"], period_id, period_label, justifikasi, sub, metrics
        ))
        cypher_lines.append(generate_cypher_queries(event_name))
        cypher_lines.append("")

    md_lines += [
        "## 3. Analisis Komparatif",
        "",
        "### 3.1 Density per event",
        "",
        "Setiap event yang punya ≥2 Person otomatis form **clique** di sub-graph "
        "(semua Person INVOLVED_IN sama event → pairwise terhubung via shared participation). "
        "Density per-event-subgraph = 1.0 by construction. ",
        "",
        "Implikasi: density bukan metric yang informatif untuk single event. Yang informatif:",
        "- **Size** (n_persons) — semakin besar event, semakin banyak orang terlibat",
        "- **Direct Person-Person relations** dalam scope — quality of relationships",
        "- **Cross-event overlap** — tokoh yang lintas-zaman = bridge structural",
        "",
        "### 3.2 Cross-event analysis",
        "",
        f"Dari 5 event ini, **{len(cross_period_persons)} Person** muncul di ≥3 event "
        "(lihat tabel di section 1). Tokoh-tokoh ini adalah **hubs lintas-zaman** — mereka "
        "membentuk struktur backbone Knowledge Graph Sirah.",
        "",
        "Hipotesis untuk dianalisis di Bab 4:",
        "- Tokoh hubs lintas-zaman = sahabat utama yang terlibat di mayoritas event Sirah",
        "- Tokoh single-event = peripheral (mungkin partisipan specific atau noise NER)",
        "- Density direct relations berkorelasi dengan **kohesi internal** event "
        "(perang besar punya lebih banyak relasi keluarga/sahabat antar peserta)",
        "",
        "### 3.3 Limitasi",
        "",
        "- Sub-graph hanya dari relasi yang **ter-ekstraksi NER + relation_extraction**. "
        "Tokoh yang real-life terlibat tapi tidak disebut di teks chunk akan miss.",
        "- Density=1.0 by construction → tidak bisa membandingkan kohesi antar event "
        "secara langsung dari metric ini. Pakai n_persons + direct_relations sebagai proxy.",
        "- Event yang frequency rendah (mis. Hudaibiyah freq=11) cenderung punya Person count "
        "lebih sedikit — bias coverage NER, bukan ground truth keterlibatan historis.",
        "",
    ]

    out_md = OUT_DIR / "case_study_events.md"
    out_cypher = OUT_DIR / "case_study_events_cypher.md"
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    out_cypher.write_text("\n".join(cypher_lines), encoding="utf-8")

    print(f"\n[write] {out_md.name}")
    print(f"[write] {out_cypher.name}")

    # Quick summary print
    print(f"\n[summary]")
    print(f"  5 events analyzed")
    print(f"  total unique Person: {len(total_unique_persons)}")
    print(f"  cross-period Person (≥3 events): {len(cross_period_persons)}")
    print(f"  top hub: {cross_period_persons[0][0]} ({cross_period_persons[0][1]}/5)" if cross_period_persons else "")


if __name__ == "__main__":
    main()
