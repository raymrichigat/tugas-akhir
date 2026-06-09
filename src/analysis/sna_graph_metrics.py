"""
sna_graph_metrics.py
====================
Graph-level Social Network Analysis untuk Knowledge Graph Sirah (revisi Bu Diana
cluster #4, 2026-05-03).

Menambah ke `sna_analysis.py` yang sudah ada (yang fokus per-node centrality):
  - Graph-level metrics: density, clustering coefficient, transitivity, network size,
    components, diameter, assortativity, average degree
  - Community detection comparison: Louvain (proper) vs Greedy Modularity vs
    Girvan-Newman (top split), dengan modularity score & ARI pairwise

Input default: `data/result/relation_result/nodes_v2.csv` + `edges_v2.csv`
(hasil apply_review_to_kg.py — periodisasi yang sudah dibersihkan).
Fallback ke `nodes.csv` + `edges.csv` kalau v2 belum ada.

Output:
  - data/result/analysis/graph_metrics_v2.md   (report markdown)
  - data/result/analysis/graph_metrics_v2.json (programmatic)

Usage:
  python sna_graph_metrics.py
  python sna_graph_metrics.py --use-v1   # paksa pakai nodes.csv (bukan _v2)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RR_DIR = BASE_DIR / "data" / "result" / "relation_result"
OUT_DIR = BASE_DIR / "data" / "result" / "analysis"

# Lihat sna_analysis.py: filter co-mention lemah (INVOLVED_IN weight < 0.3)
# lalu bobot co-participation = Σ min(w1, w2). Harus konsisten dgn sna_analysis.
WEIGHT_THRESHOLD = 0.3


# ── Graph build (reuse logic dari sna_analysis.py) ───────────────────────────
def build_person_graph(edges_df: pd.DataFrame) -> nx.Graph:
    """
    Bangun Person-Person co-participation graph.

    Edge dibangun dari:
      1. Co-participation: dua Person yang INVOLVED_IN event yang sama → edge
         (hanya weight >= WEIGHT_THRESHOLD; bobot = Σ min(w1, w2) per event)
      2. Relasi Person-Person langsung (KELUARGA, SAHABAT, MUSUH) → edge atau
         tambahan weight kalau edge sudah ada
    """
    involved_in = edges_df[edges_df["relation_type"] == "INVOLVED_IN"].copy()
    involved_in["weight"] = pd.to_numeric(
        involved_in["weight"], errors="coerce").fillna(WEIGHT_THRESHOLD)
    involved_in = involved_in[involved_in["weight"] >= WEIGHT_THRESHOLD]

    event_person_w: dict[str, dict] = defaultdict(dict)
    for _, row in involved_in.iterrows():
        ev, p, w = row["target_name"], row["source_name"], float(row["weight"])
        if p not in event_person_w[ev] or w > event_person_w[ev][p]:
            event_person_w[ev][p] = w

    copart_weights: dict[tuple, float] = defaultdict(float)
    for pw in event_person_w.values():
        for p1, p2 in combinations(sorted(pw.keys()), 2):
            copart_weights[(p1, p2)] += min(pw[p1], pw[p2])

    G = nx.Graph()
    for (p1, p2), w in copart_weights.items():
        G.add_edge(p1, p2, weight=round(w, 3), relation_type="CO_PARTICIPATION")

    person_rels = edges_df[edges_df["relation_type"].isin(["KELUARGA", "SAHABAT", "MUSUH"])]
    for _, row in person_rels.iterrows():
        src, tgt = row["source_name"], row["target_name"]
        if G.has_edge(src, tgt):
            G[src][tgt]["weight"] += row.get("weight", 0.5)
        else:
            G.add_edge(src, tgt, weight=row.get("weight", 0.5),
                       relation_type=row["relation_type"])
    return G


# ── Graph-level metrics ──────────────────────────────────────────────────────
def compute_graph_metrics(G: nx.Graph) -> dict:
    """
    Hitung graph-level metrics. Returns flat dict with numeric values.
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()

    components = list(nx.connected_components(G))
    n_components = len(components)
    giant = max(components, key=len) if components else set()
    G_giant = G.subgraph(giant).copy() if giant else nx.Graph()

    metrics = {
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "density": nx.density(G),
        "average_degree": (2 * n_edges / n_nodes) if n_nodes else 0,
        "n_components": n_components,
        "giant_component_size": len(giant),
        "giant_component_ratio": (len(giant) / n_nodes) if n_nodes else 0,
        "average_clustering_coefficient": nx.average_clustering(G, weight=None),
        "transitivity_global": nx.transitivity(G),
        "degree_assortativity": nx.degree_assortativity_coefficient(G) if n_edges > 0 else float("nan"),
    }

    # Path-based metrics hanya pada giant component (kalau disconnected, infinite distance)
    if G_giant.number_of_nodes() > 1:
        metrics["giant_diameter"] = nx.diameter(G_giant)
        metrics["giant_avg_shortest_path"] = nx.average_shortest_path_length(G_giant)
        metrics["giant_radius"] = nx.radius(G_giant)
    else:
        metrics["giant_diameter"] = 0
        metrics["giant_avg_shortest_path"] = 0
        metrics["giant_radius"] = 0

    return metrics


# ── Community detection (multi-method) ───────────────────────────────────────
def detect_louvain(G: nx.Graph) -> list[set]:
    """Louvain proper (NetworkX 2.7+)."""
    try:
        from networkx.algorithms.community import louvain_communities
        return list(louvain_communities(G, weight="weight", seed=42))
    except ImportError:
        print("  [louvain] louvain_communities tidak available, fallback ke greedy_modularity")
        from networkx.algorithms.community import greedy_modularity_communities
        return list(greedy_modularity_communities(G, weight="weight"))


def detect_greedy(G: nx.Graph) -> list[set]:
    """Greedy modularity (sama dengan yang dipakai sna_analysis.py existing)."""
    from networkx.algorithms.community import greedy_modularity_communities
    return list(greedy_modularity_communities(G, weight="weight"))


def detect_girvan_newman(G: nx.Graph, max_communities: int = 16) -> list[set]:
    """
    Girvan-Newman iterative split. Stop saat dapat `max_communities` partisi atau habis.
    Slow: O(m² n) per iteration; untuk ~200 nodes / ~1000 edges masih feasible.
    """
    from networkx.algorithms.community import girvan_newman

    # Iterate ke max_communities partisi
    comp_gen = girvan_newman(G)
    best = None
    for partition in comp_gen:
        best = [set(c) for c in partition]
        if len(best) >= max_communities:
            break
    return best if best else [set(G.nodes())]


def communities_to_map(communities: list[set]) -> dict[str, int]:
    """[{a, b}, {c, d}] → {a: 0, b: 0, c: 1, d: 1}."""
    return {node: i for i, com in enumerate(communities) for node in com}


def modularity(G: nx.Graph, communities: list[set]) -> float:
    """Modularity score (newman-girvan)."""
    return nx.algorithms.community.modularity(G, communities, weight="weight")


def adjusted_rand_index(map1: dict, map2: dict) -> float:
    """
    Pairwise ARI antar dua community partitioning. Tidak butuh sklearn—pakai
    implementasi manual sederhana karena kita cuma butuh sekali.
    """
    try:
        from sklearn.metrics import adjusted_rand_score
        nodes = sorted(set(map1.keys()) & set(map2.keys()))
        labels1 = [map1[n] for n in nodes]
        labels2 = [map2[n] for n in nodes]
        return float(adjusted_rand_score(labels1, labels2))
    except ImportError:
        return float("nan")


# ── Report generation ────────────────────────────────────────────────────────
def format_metric(value, fmt: str = ".4f") -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float) and (value != value):  # NaN
        return "NaN"
    if isinstance(value, float):
        return format(value, fmt)
    return str(value)


def generate_report(
    metrics: dict,
    community_runs: dict[str, dict],
    ari_matrix: dict,
    out_dir: Path,
    source_note: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Graph-Level Metrics & Community Detection Comparison",
        "",
        f"**Sumber data:** {source_note}",
        f"**Generated by:** `sna_graph_metrics.py`",
        "",
        "## 1. Graph-Level Metrics",
        "",
        "| Metric | Value | Interpretasi |",
        "|---|---:|---|",
        f"| n_nodes | {metrics['n_nodes']} | Jumlah Person (node) di graf |",
        f"| n_edges | {metrics['n_edges']} | Jumlah relasi (co-participation + Person-Person) |",
        f"| average_degree | {format_metric(metrics['average_degree'], '.2f')} | Rata-rata koneksi per orang |",
        f"| density | {format_metric(metrics['density'])} | Rasio actual edges vs possible edges (0=sparse, 1=complete graph) |",
        f"| average_clustering_coefficient | {format_metric(metrics['average_clustering_coefficient'])} | Rata-rata seberapa cluster tetangga tiap node (lokal) |",
        f"| transitivity_global | {format_metric(metrics['transitivity_global'])} | Global clustering: rasio segitiga / triplet (kohesi keseluruhan) |",
        f"| degree_assortativity | {format_metric(metrics['degree_assortativity'])} | Positif = high-degree connect to high-degree; negatif = high connect to low (hub-and-spoke) |",
        f"| n_components | {metrics['n_components']} | Jumlah connected components (kalau >1, graf tidak fully connected) |",
        f"| giant_component_size | {metrics['giant_component_size']} | Ukuran komponen terbesar |",
        f"| giant_component_ratio | {format_metric(metrics['giant_component_ratio'])} | % node dalam giant component |",
        f"| giant_diameter | {metrics['giant_diameter']} | Diameter giant component (jarak terjauh dua node) |",
        f"| giant_radius | {metrics['giant_radius']} | Radius giant component |",
        f"| giant_avg_shortest_path | {format_metric(metrics['giant_avg_shortest_path'], '.2f')} | Rata-rata path length di giant component |",
        "",
        "## 2. Community Detection Comparison",
        "",
        "Bandingkan **3 metode community detection**:",
        "- **Louvain (proper)** — `nx.community.louvain_communities()` (NetworkX 2.7+).",
        "- **Greedy Modularity** — `nx.community.greedy_modularity_communities()` (yang dipakai `sna_analysis.py` existing, secara teknis BUKAN Louvain meskipun di kode lama dilabeli 'Louvain').",
        "- **Girvan-Newman** — iterative edge removal, capped di 16 partisi.",
        "",
        "### 2.1 Modularity & Jumlah Komunitas",
        "",
        "| Method | n_communities | Modularity Q | Catatan |",
        "|---|---:|---:|---|",
    ]
    for method, info in community_runs.items():
        catatan = ""
        if method == "louvain":
            catatan = "Standar emas balanced quality+speed"
        elif method == "greedy":
            catatan = "Faster tapi quality lebih rendah; legacy di `sna_analysis.py`"
        elif method == "girvan_newman":
            catatan = "Slow tapi interpretable (edge-betweenness based)"
        lines.append(
            f"| {method} | {info['n_communities']} | {format_metric(info['modularity'])} | {catatan} |"
        )

    lines += [
        "",
        "### 2.2 Pairwise Adjusted Rand Index (ARI)",
        "",
        "ARI mengukur **kesepakatan** antara 2 partisi (0=random, 1=identical).",
        "ARI tinggi → metode-metode menemukan struktur komunitas yang serupa.",
        "",
    ]
    methods = list(community_runs.keys())
    header = "| Method | " + " | ".join(methods) + " |"
    sep = "|---|" + "---:|" * len(methods)
    lines.append(header)
    lines.append(sep)
    for m1 in methods:
        cells = [m1]
        for m2 in methods:
            cells.append(format_metric(ari_matrix.get((m1, m2), 1.0 if m1 == m2 else float("nan"))))
        lines.append("| " + " | ".join(cells) + " |")

    # Top members per komunitas (pakai metode terbaik by modularity)
    best_method = max(community_runs.items(), key=lambda kv: kv[1]["modularity"])[0]
    lines += [
        "",
        f"### 2.3 Top members per community ({best_method}, top modularity)",
        "",
        f"Method pemenang berdasarkan modularity: **{best_method}** "
        f"(Q={format_metric(community_runs[best_method]['modularity'])}, "
        f"{community_runs[best_method]['n_communities']} komunitas).",
        "",
    ]
    communities = community_runs[best_method]["communities"]
    for i, com in enumerate(sorted(communities, key=len, reverse=True), 1):
        members = sorted(com)
        sample = members[:8]
        more = f" (+{len(members) - 8} lagi)" if len(members) > 8 else ""
        lines.append(f"- **C{i}** ({len(members)} anggota): {', '.join(sample)}{more}")

    lines += [
        "",
        "## 3. Klaim yang Bisa Dipertahankan (untuk Bab 4)",
        "",
        f"- Knowledge Graph Sirah ini punya **{metrics['n_nodes']} Person** dengan **{metrics['n_edges']} relasi** "
        f"(density {format_metric(metrics['density'])}).",
        f"- Struktur komunitas terdeteksi: **{community_runs[best_method]['n_communities']} kelompok** "
        f"(modularity {format_metric(community_runs[best_method]['modularity'])}) — menunjukkan adanya **faksi/kelompok diskursus** yang berbeda.",
        f"- Clustering coefficient {format_metric(metrics['average_clustering_coefficient'])} (lokal) "
        f"vs {format_metric(metrics['transitivity_global'])} (global) — interpretasi: "
        f"{'banyak tetangga node yang juga saling terhubung (kohesi lokal tinggi)' if metrics['average_clustering_coefficient'] > 0.3 else 'kohesi lokal moderat/rendah'}.",
        f"- Degree assortativity {format_metric(metrics['degree_assortativity'])}: "
        f"{'positif assortativity → tokoh sentral cenderung terhubung dengan tokoh sentral lain' if metrics['degree_assortativity'] > 0.1 else 'cenderung disassortative (hub-and-spoke), tokoh sentral menjadi penghubung banyak orang biasa' if metrics['degree_assortativity'] < -0.1 else 'mendekati neutral'}.",
        "",
        f"- ARI antara Louvain & Greedy: {format_metric(ari_matrix.get(('louvain', 'greedy'), float('nan')))} "
        f"({'agreement tinggi — pilihan algoritma tidak banyak mempengaruhi hasil' if ari_matrix.get(('louvain', 'greedy'), 0) > 0.7 else 'agreement moderat — metode menghasilkan struktur yang berbeda, perlu pertimbangan saat klaim komunitas'}).",
        "",
    ]

    (out_dir / "graph_metrics_v2.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  Report saved to: {out_dir / 'graph_metrics_v2.md'}")


def save_json(metrics: dict, community_runs: dict, ari_matrix: dict, out_dir: Path) -> None:
    json_safe_community = {}
    for method, info in community_runs.items():
        json_safe_community[method] = {
            "n_communities": info["n_communities"],
            "modularity": info["modularity"],
            "community_sizes": [len(c) for c in info["communities"]],
        }
    json_safe_ari = {f"{m1}__{m2}": v for (m1, m2), v in ari_matrix.items()}
    out = {
        "graph_metrics": metrics,
        "community_detection": json_safe_community,
        "ari_pairwise": json_safe_ari,
    }
    (out_dir / "graph_metrics_v2.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  JSON saved to: {out_dir / 'graph_metrics_v2.json'}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--use-v1", action="store_true",
                    help="paksa pakai nodes.csv (bukan nodes_v2.csv)")
    ap.add_argument("--version", choices=["v1", "v2", "v3"], default=None,
                    help="Pilih versi nodes/edges (override --use-v1)")
    args = ap.parse_args()

    if args.version == "v3":
        nodes_path = RR_DIR / "nodes_v3.csv"
        edges_path = RR_DIR / "edges_v3.csv"
        source_note = "v3 (`nodes_v3.csv` + `edges_v3.csv`) — hasil NER S3.2 winner"
        out_dir = OUT_DIR / "v3"
    elif args.version == "v2" or (args.version is None and not args.use_v1
                                   and (RR_DIR / "nodes_v2.csv").exists()):
        nodes_path = RR_DIR / "nodes_v2.csv"
        edges_path = RR_DIR / "edges_v2.csv"
        source_note = "v2 (`nodes_v2.csv` + `edges_v2.csv`) — sudah apply review periodisasi"
        out_dir = OUT_DIR
    else:
        nodes_path = RR_DIR / "nodes.csv"
        edges_path = RR_DIR / "edges.csv"
        source_note = "v1 (`nodes.csv` + `edges.csv`) — periodisasi belum dibersihkan"
        out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[load] {nodes_path.name} + {edges_path.name}")
    edges_df = pd.read_csv(edges_path, sep=";", encoding="utf-8-sig").fillna("")

    G = build_person_graph(edges_df)
    print(f"  Person graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("\n[metrics] computing graph-level metrics...")
    metrics = compute_graph_metrics(G)
    for k, v in metrics.items():
        print(f"  {k:<35s} = {format_metric(v) if isinstance(v, float) else v}")

    print("\n[community] running 3 detection methods...")
    methods = {
        "louvain": detect_louvain,
        "greedy": detect_greedy,
        "girvan_newman": lambda g: detect_girvan_newman(g, max_communities=16),
    }
    community_runs = {}
    for name, fn in methods.items():
        print(f"  - {name} ...")
        communities = fn(G)
        community_runs[name] = {
            "communities": communities,
            "n_communities": len(communities),
            "modularity": modularity(G, communities),
        }
        print(f"      {len(communities)} communities, Q={community_runs[name]['modularity']:.4f}")

    print("\n[ari] pairwise community agreement...")
    ari_matrix = {}
    for m1 in methods:
        for m2 in methods:
            if m1 == m2:
                ari_matrix[(m1, m2)] = 1.0
            else:
                ari_matrix[(m1, m2)] = adjusted_rand_index(
                    communities_to_map(community_runs[m1]["communities"]),
                    communities_to_map(community_runs[m2]["communities"]),
                )
    for (m1, m2), v in ari_matrix.items():
        if m1 < m2:
            print(f"  ARI({m1}, {m2}) = {v:.4f}")

    print("\n[report] generating...")
    generate_report(metrics, community_runs, ari_matrix, out_dir, source_note)
    save_json(metrics, community_runs, ari_matrix, out_dir)


if __name__ == "__main__":
    main()
