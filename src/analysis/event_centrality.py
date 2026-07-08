"""
event_centrality.py
====================
Social Network Analysis untuk node EVENT (revisi Bu Diana 2026-05-16).

Latar belakang:
SNA awal (sna_analysis.py) hanya menghitung centrality untuk Person (174 nodes).
Bu Diana minta diperluas ke node Event juga supaya bisa identifikasi:
  - Event mana yang paling sentral dalam narasi Sirah (PageRank).
  - Event mana yang jadi bridge antara fase historis (betweenness).
  - Cluster event yang co-occur (community).

Strategi co-participation untuk Event:
  Dua Event dianggap terhubung jika **share Person** yang sama (INVOLVED_IN).
  Edge weight = jumlah Person yang co-participate di kedua event.

  Contoh: Perang Badr ↔ Perang Uhud ter-edge karena banyak sahabat (Muhammad,
  Abu Bakar, Umar, dll.) ikut di kedua perang. Weight = jumlah Person bersama.

Tambahan: relasi Event-Event langsung (PRECEDES) ditambahkan sebagai edge
dengan weight tambahan, untuk capture kronologi.

Input:
  - data/result/relation_result/nodes_v2.csv
  - data/result/relation_result/edges_v2.csv

Output:
  - data/result/analysis/event_centrality.csv
  - data/result/analysis/event_centrality_summary.md
  - data/result/analysis/event_network.png

Idempotent. Usage:
  python src/analysis/event_centrality.py
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IN_NODES = ROOT / "data" / "result" / "relation_result" / "nodes_v2.csv"
IN_EDGES = ROOT / "data" / "result" / "relation_result" / "edges_v2.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = pd.read_csv(IN_NODES, sep=";", encoding="utf-8-sig").fillna("")
    edges = pd.read_csv(IN_EDGES, sep=";", encoding="utf-8-sig").fillna("")
    return nodes, edges


def build_event_coparticipation_graph(
    nodes_df: pd.DataFrame, edges_df: pd.DataFrame
) -> tuple[nx.Graph, dict[str, dict]]:
    """
    Build Event-Event graph:
      - Edge if 2 events share at least 1 Person via INVOLVED_IN
      - Weight = number of shared persons
      - Plus PRECEDES edges (chronological)
    """
    event_meta = {
        row["name"]: {
            "frequency": int(row.get("frequency", 0)) if str(row.get("frequency", "")).strip() else 0,
            "periode_bab": row.get("periode_bab", ""),
            "page_range": row.get("page_range", ""),
        }
        for _, row in nodes_df.iterrows()
        if row["label"] == "EVENT"
    }

    involved = edges_df[edges_df["relation_type"] == "INVOLVED_IN"]

    event_persons: dict[str, set[str]] = defaultdict(set)
    for _, row in involved.iterrows():
        event_persons[row["target_name"]].add(row["source_name"])

    G = nx.Graph()

    for ev, meta in event_meta.items():
        G.add_node(
            ev,
            label="EVENT",
            frequency=meta["frequency"],
            periode_bab=meta["periode_bab"],
            page_range=meta["page_range"],
        )

    events_sorted = sorted(event_persons.keys())
    shared_log: dict[tuple[str, str], list[str]] = {}
    for i in range(len(events_sorted)):
        for j in range(i + 1, len(events_sorted)):
            e1, e2 = events_sorted[i], events_sorted[j]
            shared = event_persons[e1] & event_persons[e2]
            if shared:
                G.add_edge(
                    e1, e2,
                    weight=len(shared),
                    shared_persons=" | ".join(sorted(shared)),
                    edge_type="CO_PARTICIPATION",
                )
                shared_log[(e1, e2)] = sorted(shared)

    precedes = edges_df[edges_df["relation_type"] == "PRECEDES"]
    n_precedes_added = 0
    for _, row in precedes.iterrows():
        src, tgt = row["source_name"], row["target_name"]
        if src not in event_meta or tgt not in event_meta:
            continue
        if G.has_edge(src, tgt):
            G[src][tgt]["weight"] += 1
            G[src][tgt]["edge_type"] = (
                f"{G[src][tgt].get('edge_type', '')} | PRECEDES".strip(" |")
            )
        else:
            G.add_edge(src, tgt, weight=1, edge_type="PRECEDES", shared_persons="")
        n_precedes_added += 1

    print(f"  Event nodes        : {G.number_of_nodes()}")
    print(f"  Event-Event edges  : {G.number_of_edges()}")
    print(f"  Co-participation   : {len(shared_log)} pairs")
    print(f"  PRECEDES merged    : {n_precedes_added}")

    return G, event_meta


def compute_centrality(G: nx.Graph) -> dict[str, dict]:
    print("  computing degree centrality...")
    deg = nx.degree_centrality(G)
    print("  computing betweenness centrality (weighted)...")
    bet = nx.betweenness_centrality(G, weight="weight")
    print("  computing closeness centrality...")
    clo = nx.closeness_centrality(G)
    print("  computing pagerank...")
    pr = nx.pagerank(G, weight="weight")

    out: dict[str, dict] = {}
    for n in G.nodes():
        out[n] = {
            "name": n,
            "degree": G.degree(n),
            "weighted_degree": int(sum(G[n][nb].get("weight", 1) for nb in G.neighbors(n))),
            "degree_centrality": round(deg.get(n, 0), 6),
            "betweenness_centrality": round(bet.get(n, 0), 6),
            "closeness_centrality": round(clo.get(n, 0), 6),
            "pagerank": round(pr.get(n, 0), 6),
        }
    return out


def detect_communities(G: nx.Graph) -> dict[str, int]:
    try:
        from networkx.algorithms.community import louvain_communities
        comms = louvain_communities(G, weight="weight", seed=42)
    except Exception:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = list(greedy_modularity_communities(G, weight="weight"))

    out: dict[str, int] = {}
    for i, c in enumerate(comms):
        for n in c:
            out[n] = i
    print(f"  communities: {len(comms)}")
    return out


def write_csv(metrics: dict[str, dict], event_meta: dict[str, dict],
              comm_map: dict[str, int]) -> Path:
    rows = []
    for name, m in metrics.items():
        meta = event_meta.get(name, {})
        rows.append({
            **m,
            "frequency": meta.get("frequency", 0),
            "periode_bab": meta.get("periode_bab", ""),
            "page_range": meta.get("page_range", ""),
            "community": comm_map.get(name, -1),
        })
    df = pd.DataFrame(rows).sort_values("pagerank", ascending=False)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "event_centrality.csv"
    df.to_csv(out_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"  -> {out_path}")
    return out_path


def write_summary(G: nx.Graph, metrics: dict[str, dict],
                  event_meta: dict[str, dict], comm_map: dict[str, int]) -> Path:
    by_pr = sorted(metrics.values(), key=lambda x: -x["pagerank"])
    by_bet = sorted(metrics.values(), key=lambda x: -x["betweenness_centrality"])
    by_deg = sorted(metrics.values(), key=lambda x: -x["degree"])

    lines: list[str] = []
    lines.append("# Event Centrality Analysis — Knowledge Graph Sirah\n")
    lines.append("**Tanggal:** 2026-05-26\n")
    lines.append("**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event "
                "(sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau "
                "share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. "
                "PRECEDES (kronologi) ditambahkan sebagai weight extra.\n")
    lines.append("## Ringkasan Graf\n")
    lines.append(f"- Event nodes      : **{G.number_of_nodes()}**")
    lines.append(f"- Event-Event edges: **{G.number_of_edges()}**")
    lines.append(f"- Density          : **{nx.density(G):.4f}**")
    if nx.is_connected(G):
        lines.append(f"- Connected        : Yes (single component)")
        lines.append(f"- Diameter         : {nx.diameter(G)}")
        lines.append(f"- Avg path length  : {nx.average_shortest_path_length(G):.2f}")
    else:
        comps = list(nx.connected_components(G))
        lines.append(f"- Components       : {len(comps)}")
        lines.append(f"- Largest component: {len(max(comps, key=len))} events")

    lines.append("\n## Top 15 Event — PageRank (paling sentral di narasi)\n")
    lines.append("| Rank | Event | Period | PageRank | Degree | Frekuensi |")
    lines.append("|---:|---|---|---:|---:|---:|")
    for i, m in enumerate(by_pr[:15], 1):
        meta = event_meta.get(m["name"], {})
        lines.append(
            f"| {i} | {m['name']} | {meta.get('periode_bab','')} | "
            f"{m['pagerank']:.4f} | {m['degree']} | {meta.get('frequency',0)} |"
        )

    lines.append("\n## Top 15 Event — Betweenness (jembatan antar fase)\n")
    lines.append("| Rank | Event | Period | Betweenness | Degree |")
    lines.append("|---:|---|---|---:|---:|")
    for i, m in enumerate(by_bet[:15], 1):
        meta = event_meta.get(m["name"], {})
        lines.append(
            f"| {i} | {m['name']} | {meta.get('periode_bab','')} | "
            f"{m['betweenness_centrality']:.4f} | {m['degree']} |"
        )

    lines.append("\n## Top 15 Event — Degree (paling banyak co-participation)\n")
    lines.append("| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |")
    lines.append("|---:|---|---|---:|---:|---:|")
    for i, m in enumerate(by_deg[:15], 1):
        meta = event_meta.get(m["name"], {})
        lines.append(
            f"| {i} | {m['name']} | {meta.get('periode_bab','')} | "
            f"{m['degree']} | {m['weighted_degree']} | {meta.get('frequency',0)} |"
        )

    if comm_map:
        lines.append("\n## Komunitas Event (Louvain)\n")
        comm_members: dict[int, list[str]] = defaultdict(list)
        for n, cid in comm_map.items():
            comm_members[cid].append(n)
        for cid in sorted(comm_members.keys()):
            members = comm_members[cid]
            members_sorted = sorted(
                members,
                key=lambda n: metrics.get(n, {}).get("pagerank", 0),
                reverse=True,
            )
            lines.append(f"### Komunitas {cid+1} — {len(members)} event")
            lines.append(f"Top events: {', '.join(members_sorted[:8])}")
            periods = sorted({event_meta.get(n, {}).get("periode_bab", "") for n in members if event_meta.get(n, {}).get("periode_bab")})
            if periods:
                lines.append(f"Period coverage: {', '.join(p for p in periods if p)}")
            lines.append("")

    lines.append("\n## Catatan Interpretasi\n")
    lines.append("- **PageRank tertinggi** = event yang paling banyak \"didukung\" oleh "
                 "event lain (banyak shared persons + co-occur dengan event sentral).")
    lines.append("- **Betweenness tinggi** = event yang ada di jalur shortest path antar "
                 "kelompok event lain (jembatan antar fase Sirah).")
    lines.append("- **Co-participation rule** punya bias: event dengan banyak Person "
                 "(mis. Perang Badr 39 person) otomatis punya degree tinggi. "
                 "Pakai weighted_degree + frekuensi untuk konteks tambahan.")
    lines.append("- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation "
                 "tetap dominan signal.")

    out_path = OUT_DIR / "event_centrality_summary.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {out_path}")
    return out_path


def visualize(G: nx.Graph, metrics: dict[str, dict],
              comm_map: dict[str, int]) -> Path | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not installed, skip viz")
        return None

    fig, ax = plt.subplots(figsize=(16, 12))
    pos = nx.spring_layout(G, k=1.5, iterations=80, seed=42, weight="weight")

    pr_vals = [metrics[n]["pagerank"] for n in G.nodes()]
    max_pr = max(pr_vals) if pr_vals else 1
    sizes = [max(150, (p / max_pr) * 3000) for p in pr_vals]

    colors = [comm_map.get(n, 0) for n in G.nodes()]

    weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_w = max(weights) if weights else 1
    widths = [max(0.4, (w / max_w) * 4) for w in weights]

    nx.draw_networkx_edges(G, pos, width=widths, alpha=0.35, edge_color="gray", ax=ax)
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors,
                           cmap=plt.cm.Set2, alpha=0.85, ax=ax)
    top = sorted(G.nodes(), key=lambda n: metrics[n]["pagerank"], reverse=True)[:25]
    nx.draw_networkx_labels(G, pos, {n: n for n in top}, font_size=8,
                            font_weight="bold", ax=ax)

    ax.set_title("Event Network — Knowledge Graph Sirah Nabawiyah\n"
                 "(node size = PageRank, color = community Louvain, edge = co-participation Person)",
                 fontsize=13, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    out_path = OUT_DIR / "event_network.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> {out_path}")
    return out_path


def main():
    import argparse
    global IN_NODES, IN_EDGES, OUT_DIR

    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["v2", "v3", "v4", "v4_hybrid"], default="v3",
                    help="Pilih versi nodes/edges (default: v3)")
    args = ap.parse_args()

    if args.version in ("v4", "v4_hybrid"):
        suffix = "_hybrid" if args.version == "v4_hybrid" else ""
        IN_NODES = ROOT / "data" / "result" / "relation_result" / f"nodes_v4{suffix}.csv"
        IN_EDGES = ROOT / "data" / "result" / "relation_result" / f"edges_v4{suffix}.csv"
        OUT_DIR = ROOT / "data" / "result" / "analysis" / args.version
    elif args.version == "v3":
        IN_NODES = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"
        IN_EDGES = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
        OUT_DIR = ROOT / "data" / "result" / "analysis" / "v3"

    print("=" * 60)
    print(f"EVENT CENTRALITY — Knowledge Graph Sirah [{args.version}]")
    print("=" * 60)

    print(f"\n[1/5] loading {IN_NODES.name} + {IN_EDGES.name}...")
    nodes_df, edges_df = load_data()
    print(f"  nodes={len(nodes_df)}  edges={len(edges_df)}")

    print("\n[2/5] building Event co-participation graph...")
    G, event_meta = build_event_coparticipation_graph(nodes_df, edges_df)

    if G.number_of_nodes() == 0:
        print("  no Event nodes found, abort")
        return

    print("\n[3/5] computing centrality metrics...")
    metrics = compute_centrality(G)

    print("\n[4/5] detecting communities...")
    comm_map = detect_communities(G)

    print("\n[5/5] writing outputs...")
    write_csv(metrics, event_meta, comm_map)
    write_summary(G, metrics, event_meta, comm_map)
    visualize(G, metrics, comm_map)

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)
    by_pr = sorted(metrics.values(), key=lambda x: -x["pagerank"])
    print("\nTop 10 Event by PageRank:")
    for i, m in enumerate(by_pr[:10], 1):
        meta = event_meta.get(m["name"], {})
        print(f"  {i:2d}. {m['name']:<40s} PR={m['pagerank']:.4f}  "
              f"Deg={m['degree']:3d}  Period={meta.get('periode_bab','')}")


if __name__ == "__main__":
    main()
