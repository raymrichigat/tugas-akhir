"""
Social Network Analysis (SNA) — Knowledge Graph Sirah Nabawiyah

Menganalisis jaringan sosial tokoh-tokoh dalam Sirah Nabawiyah berdasarkan
co-participation dalam event yang sama.

Metrik yang dihitung:
  - Degree Centrality: siapa paling banyak koneksi
  - Betweenness Centrality: siapa bridge antar kelompok
  - Closeness Centrality: siapa paling sentral
  - PageRank: siapa paling "authoritative"
  - Community Detection: Louvain (kelompok/faksi)

Output:
  - sna_metrics.csv: metrik per node
  - sna_summary.md: ringkasan analisis
  - sna_person_network.png: visualisasi jaringan

Cara pakai:
  python sna_analysis.py
"""

import argparse
import pandas as pd
import networkx as nx
from pathlib import Path
from collections import defaultdict

# ── Konfigurasi ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
RR_DIR = BASE_DIR / "data" / "result" / "relation_result"

# Threshold weight relasi INVOLVED_IN untuk membangun graf co-participation.
# Edge co-mention lemah (<0.3 = proximity jauh & di luar BAB utama) dibuang agar
# tidak membentuk clique palsu di event ramai (lihat kasus Amr Bin Umayyah,
# docs/bimbingan/2026-06-04 A.1.3). Co-participation lalu di-bobot Σ min(w1, w2).
WEIGHT_THRESHOLD = 0.3


def resolve_paths(version: str):
    """Pilih nodes/edges/out_dir berdasarkan version (v1|v2|v3)."""
    if version == "v1":
        nodes = RR_DIR / "nodes.csv"
        edges = RR_DIR / "edges.csv"
        out = BASE_DIR / "data" / "result" / "analysis"
    elif version == "v2":
        nodes = RR_DIR / "nodes_v2.csv"
        edges = RR_DIR / "edges_v2.csv"
        out = BASE_DIR / "data" / "result" / "analysis"
    elif version == "v3":
        nodes = RR_DIR / "nodes_v3.csv"
        edges = RR_DIR / "edges_v3.csv"
        out = BASE_DIR / "data" / "result" / "analysis" / "v3"
    elif version == "v4":
        nodes = RR_DIR / "nodes_v4.csv"
        edges = RR_DIR / "edges_v4.csv"
        out = BASE_DIR / "data" / "result" / "analysis" / "v4"
    elif version == "v4_hybrid":
        nodes = RR_DIR / "nodes_v4_hybrid.csv"
        edges = RR_DIR / "edges_v4_hybrid.csv"
        out = BASE_DIR / "data" / "result" / "analysis" / "v4_hybrid"
    elif version == "v4_scoped":
        # v4_hybrid dengan node PERSON nasab-only di-scope keluar
        # (lihat src/relation_extraction/clean_v4_hybrid_genealogy.py)
        nodes = RR_DIR / "nodes_v4_scoped.csv"
        edges = RR_DIR / "edges_v4_scoped.csv"
        out = BASE_DIR / "data" / "result" / "analysis" / "v4_scoped"
    else:
        raise ValueError(f"Unknown version: {version}")
    return nodes, edges, out


def load_graph(nodes_path, edges_path):
    """Bangun NetworkX graph dari nodes.csv dan edges.csv."""
    nodes_df = pd.read_csv(nodes_path, sep=";", encoding="utf-8-sig").fillna("")
    edges_df = pd.read_csv(edges_path, sep=";", encoding="utf-8-sig").fillna("")

    G = nx.Graph()

    # Tambah nodes dengan atribut
    for _, row in nodes_df.iterrows():
        G.add_node(row["name"], label=row["label"], frequency=row["frequency"],
                    aliases=row.get("aliases", ""),
                    periode_bab=row.get("periode_bab", ""))

    # Tambah edges dengan atribut
    for _, row in edges_df.iterrows():
        weight = row.get("weight", 0.5)
        G.add_edge(row["source_name"], row["target_name"],
                    relation_type=row["relation_type"],
                    weight=weight,
                    frequency=row["frequency"],
                    relation_subtype=row.get("relation_subtype", ""))

    print(f"  Full graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G, nodes_df, edges_df


def build_person_coparticipation_graph(edges_df):
    """
    Bangun subgraph Person-only: dua person terhubung jika sama-sama
    INVOLVED_IN event yang sama (hanya relasi dengan weight >= WEIGHT_THRESHOLD).
    Edge weight = Σ min(w1, w2) atas event bersama, di mana w = weight relasi
    INVOLVED_IN (proximity + period) tiap person ke event tsb.
    Juga termasuk relasi Person-Person langsung (KELUARGA, SAHABAT, MUSUH).
    """
    # 1. Co-participation via shared events (threshold + weighted)
    #    Hanya INVOLVED_IN dengan weight >= WEIGHT_THRESHOLD yang dipakai;
    #    bobot pasangan = Σ min(w1, w2) per event bersama (bukan hitung event).
    involved_in = edges_df[edges_df["relation_type"] == "INVOLVED_IN"].copy()
    involved_in["weight"] = pd.to_numeric(
        involved_in["weight"], errors="coerce").fillna(WEIGHT_THRESHOLD)
    involved_in = involved_in[involved_in["weight"] >= WEIGHT_THRESHOLD]

    # event → {person: weight terkuat person itu ke event}
    event_person_w = defaultdict(dict)
    for _, row in involved_in.iterrows():
        ev, p, w = row["target_name"], row["source_name"], float(row["weight"])
        if p not in event_person_w[ev] or w > event_person_w[ev][p]:
            event_person_w[ev][p] = w

    # Build co-participation edges: weight = Σ min(w1, w2) per shared event
    copart_weights = defaultdict(float)
    copart_events = defaultdict(set)
    for event_name, pw in event_person_w.items():
        persons_list = sorted(pw.keys())
        for i in range(len(persons_list)):
            for j in range(i + 1, len(persons_list)):
                p1, p2 = persons_list[i], persons_list[j]
                copart_weights[(p1, p2)] += min(pw[p1], pw[p2])
                copart_events[(p1, p2)].add(event_name)

    G = nx.Graph()

    # Tambah co-participation edges
    for (p1, p2), weight in copart_weights.items():
        events = " | ".join(sorted(copart_events[(p1, p2)]))
        G.add_edge(p1, p2, weight=round(weight, 3), shared_events=events,
                    relation_type="CO_PARTICIPATION")

    # 2. Tambah relasi Person-Person langsung
    person_rels = edges_df[edges_df["relation_type"].isin(["KELUARGA", "SAHABAT", "MUSUH"])]
    for _, row in person_rels.iterrows():
        src = row["source_name"]
        tgt = row["target_name"]
        if G.has_edge(src, tgt):
            # Update existing edge
            G[src][tgt]["weight"] += row.get("weight", 0.5)
            G[src][tgt]["relation_type"] += f" | {row['relation_type']}"
        else:
            G.add_edge(src, tgt, weight=row.get("weight", 0.5),
                        relation_type=row["relation_type"],
                        relation_subtype=row.get("relation_subtype", ""))

    print(f"  Person co-participation graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_centrality_metrics(G):
    """Hitung semua centrality metrics."""
    metrics = {}

    print("  Computing degree centrality...")
    degree = nx.degree_centrality(G)

    print("  Computing betweenness centrality...")
    betweenness = nx.betweenness_centrality(G, weight="weight")

    print("  Computing closeness centrality...")
    closeness = nx.closeness_centrality(G)

    print("  Computing PageRank...")
    pagerank = nx.pagerank(G, weight="weight")

    for node in G.nodes():
        metrics[node] = {
            "name": node,
            "degree_centrality": round(degree.get(node, 0), 6),
            "betweenness_centrality": round(betweenness.get(node, 0), 6),
            "closeness_centrality": round(closeness.get(node, 0), 6),
            "pagerank": round(pagerank.get(node, 0), 6),
            "degree": G.degree(node),
        }

    return metrics


def detect_communities(G):
    """Deteksi komunitas menggunakan Louvain (greedy modularity)."""
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        communities = greedy_modularity_communities(G, weight="weight")
        community_map = {}
        for i, community in enumerate(communities):
            for node in community:
                community_map[node] = i
        print(f"  Communities detected: {len(set(community_map.values()))}")
        return community_map
    except Exception as e:
        print(f"  Community detection failed: {e}")
        return {}


def generate_report(metrics, community_map, G, out_dir):
    """Generate ringkasan SNA."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Sort by different metrics
    by_degree = sorted(metrics.values(), key=lambda x: -x["degree_centrality"])
    by_betweenness = sorted(metrics.values(), key=lambda x: -x["betweenness_centrality"])
    by_closeness = sorted(metrics.values(), key=lambda x: -x["closeness_centrality"])
    by_pagerank = sorted(metrics.values(), key=lambda x: -x["pagerank"])

    lines = []
    lines.append("# Social Network Analysis — Sirah Nabawiyah\n")
    lines.append(f"**Jumlah node (Person):** {G.number_of_nodes()}")
    lines.append(f"**Jumlah edge:** {G.number_of_edges()}")
    lines.append(f"**Density:** {nx.density(G):.4f}")

    if nx.is_connected(G):
        lines.append(f"**Diameter:** {nx.diameter(G)}")
        lines.append(f"**Avg shortest path:** {nx.average_shortest_path_length(G):.2f}")
    else:
        components = list(nx.connected_components(G))
        lines.append(f"**Connected components:** {len(components)}")
        largest = max(components, key=len)
        lines.append(f"**Largest component:** {len(largest)} nodes")

    lines.append("")

    # Top 20 by each metric
    lines.append("## Top 20 — Degree Centrality (paling banyak koneksi)\n")
    lines.append("| Rank | Nama | Degree | Centrality |")
    lines.append("|------|------|--------|------------|")
    for i, m in enumerate(by_degree[:20], 1):
        lines.append(f"| {i} | {m['name']} | {m['degree']} | {m['degree_centrality']:.4f} |")

    lines.append("")
    lines.append("## Top 20 — Betweenness Centrality (bridge antar kelompok)\n")
    lines.append("| Rank | Nama | Betweenness |")
    lines.append("|------|------|-------------|")
    for i, m in enumerate(by_betweenness[:20], 1):
        lines.append(f"| {i} | {m['name']} | {m['betweenness_centrality']:.4f} |")

    lines.append("")
    lines.append("## Top 20 — Closeness Centrality (paling sentral)\n")
    lines.append("| Rank | Nama | Closeness |")
    lines.append("|------|------|-----------|")
    for i, m in enumerate(by_closeness[:20], 1):
        lines.append(f"| {i} | {m['name']} | {m['closeness_centrality']:.4f} |")

    lines.append("")
    lines.append("## Top 20 — PageRank (paling authoritative)\n")
    lines.append("| Rank | Nama | PageRank |")
    lines.append("|------|------|----------|")
    for i, m in enumerate(by_pagerank[:20], 1):
        lines.append(f"| {i} | {m['name']} | {m['pagerank']:.4f} |")

    # Community analysis
    if community_map:
        lines.append("")
        lines.append("## Komunitas (Louvain Modularity)\n")
        comm_members = defaultdict(list)
        for node, comm_id in community_map.items():
            comm_members[comm_id].append(node)

        for comm_id in sorted(comm_members.keys()):
            members = comm_members[comm_id]
            # Sort members by PageRank
            members_sorted = sorted(members,
                                     key=lambda n: metrics.get(n, {}).get("pagerank", 0),
                                     reverse=True)
            top_members = members_sorted[:10]
            lines.append(f"### Komunitas {comm_id + 1} ({len(members)} anggota)")
            lines.append(f"Tokoh utama: {', '.join(top_members)}")
            lines.append("")

    report_text = "\n".join(lines)
    report_path = out_dir / "sna_summary.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"  Report saved to: {report_path}")


def save_metrics_csv(metrics, community_map, out_dir):
    """Simpan metrik ke CSV."""
    rows = []
    for name, m in metrics.items():
        m["community"] = community_map.get(name, -1)
        rows.append(m)

    df = pd.DataFrame(rows)
    df = df.sort_values("pagerank", ascending=False)

    csv_path = out_dir / "sna_metrics.csv"
    df.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"  Metrics saved to: {csv_path}")


def visualize_network(G, metrics, community_map, out_dir):
    """Visualisasi jaringan Person-Person."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  WARNING: matplotlib tidak terinstall, skip visualisasi")
        return

    fig, ax = plt.subplots(1, 1, figsize=(20, 16))

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42, weight="weight")

    # Node sizes based on PageRank
    pageranks = [metrics.get(n, {}).get("pagerank", 0.001) for n in G.nodes()]
    max_pr = max(pageranks) if pageranks else 1
    node_sizes = [max(100, (pr / max_pr) * 3000) for pr in pageranks]

    # Node colors based on community
    if community_map:
        colors = [community_map.get(n, 0) for n in G.nodes()]
    else:
        colors = [0] * G.number_of_nodes()

    # Edge widths based on weight
    edge_weights = [G[u][v].get("weight", 1) for u, v in G.edges()]
    max_ew = max(edge_weights) if edge_weights else 1
    edge_widths = [max(0.3, (w / max_ew) * 3) for w in edge_weights]

    # Draw
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.3, edge_color="gray", ax=ax)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=colors,
                            cmap=plt.cm.Set3, alpha=0.8, ax=ax)

    # Labels hanya untuk node dengan PageRank tinggi (top 30)
    top_nodes = sorted(G.nodes(), key=lambda n: metrics.get(n, {}).get("pagerank", 0),
                        reverse=True)[:30]
    labels = {n: n for n in top_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight="bold", ax=ax)

    ax.set_title("Social Network Analysis — Tokoh Sirah Nabawiyah\n"
                  "(node size = PageRank, color = community)",
                  fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    img_path = out_dir / "sna_person_network.png"
    plt.savefig(img_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Visualization saved to: {img_path}")


def main():
    parser = argparse.ArgumentParser(description="SNA — Sirah Nabawiyah")
    parser.add_argument("--version", choices=["v1", "v2", "v3", "v4", "v4_hybrid", "v4_scoped"], default="v3",
                        help="Pilih versi nodes/edges (default: v3)")
    args = parser.parse_args()

    in_nodes, in_edges, out_dir = resolve_paths(args.version)

    print("=" * 60)
    print(f"SOCIAL NETWORK ANALYSIS — Sirah Nabawiyah [{args.version}]")
    print("=" * 60)
    print(f"  nodes : {in_nodes.name}")
    print(f"  edges : {in_edges.name}")
    print(f"  out   : {out_dir}")

    # 1. Load graph
    print("\n[1/5] Loading graph...")
    G_full, nodes_df, edges_df = load_graph(in_nodes, in_edges)

    # 2. Build Person co-participation graph
    print("\n[2/5] Building Person co-participation graph...")
    G_person = build_person_coparticipation_graph(edges_df)

    if G_person.number_of_nodes() == 0:
        print("  No person nodes found in graph. Aborting.")
        return

    # 3. Compute centrality metrics
    print("\n[3/5] Computing centrality metrics...")
    metrics = compute_centrality_metrics(G_person)

    # 4. Detect communities
    print("\n[4/5] Detecting communities...")
    community_map = detect_communities(G_person)

    # 5. Output
    print("\n[5/5] Generating output...")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_metrics_csv(metrics, community_map, out_dir)
    generate_report(metrics, community_map, G_person, out_dir)
    visualize_network(G_person, metrics, community_map, out_dir)

    # Ringkasan
    print(f"\n{'='*60}")
    print("RINGKASAN SNA")
    print(f"{'='*60}")

    by_pagerank = sorted(metrics.values(), key=lambda x: -x["pagerank"])
    print("\nTop 10 tokoh (PageRank):")
    for i, m in enumerate(by_pagerank[:10], 1):
        comm = community_map.get(m["name"], "?")
        print(f"  {i:2d}. {m['name']:40s} PR={m['pagerank']:.4f}  "
              f"Deg={m['degree']:3d}  Betw={m['betweenness_centrality']:.4f}  "
              f"Comm={comm}")

    if community_map:
        n_communities = len(set(community_map.values()))
        print(f"\nJumlah komunitas: {n_communities}")

    print(f"\n{'='*60}")
    print("SELESAI!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
