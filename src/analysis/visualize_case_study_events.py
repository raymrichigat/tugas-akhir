"""
Visualisasi 5 sub-graf studi kasus event (revisi Bu Diana #2, 2026-05-03).

Untuk tiap event di EVENTS:
  - Event node di tengah (kuning besar)
  - Person nodes di sekeliling (ukuran ∝ jumlah event participation di seluruh KG)
  - INVOLVED_IN edges: abu-abu tipis
  - KELUARGA edges: merah
  - SAHABAT edges: hijau
  - MUSUH edges: oranye
  - Label hanya top-10 person by total participation untuk jaga kerapian

Output:
  data/result/analysis/case_study_<event>.png   (5 file)
  data/result/analysis/case_study_panel.png      (gabungan 5-panel untuk slide tunggal)

Cara run (dari root project):
    venv\Scripts\activate
    python src\analysis\visualize_case_study_events.py
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NODES_CSV = ROOT / "data" / "result" / "relation_result" / "nodes_v2.csv"
EDGES_CSV = ROOT / "data" / "result" / "relation_result" / "edges_v2.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis"

# Event yang dipilih untuk studi kasus (sama dengan case_study_events.md)
EVENTS = [
    ("Perang Badr", "P8", "266-304"),
    ("Perang Uhud", "P9", "324-375"),
    ("Perjanjian Hudaibiyah", "P11", "433-450"),
    ("Perang Khaibar", "P11", "473-492"),
    ("Perang Tabuk", "P13", "558-571"),
]

EDGE_STYLES = {
    "INVOLVED_IN": {"color": "#888888", "width": 0.8, "alpha": 0.35, "style": "solid"},
    "KELUARGA":    {"color": "#d62728", "width": 2.0, "alpha": 0.85, "style": "solid"},
    "SAHABAT":     {"color": "#2ca02c", "width": 2.0, "alpha": 0.85, "style": "solid"},
    "MUSUH":       {"color": "#ff7f0e", "width": 2.0, "alpha": 0.85, "style": "dashed"},
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig")
    edges = pd.read_csv(EDGES_CSV, sep=";", encoding="utf-8-sig")
    nodes.columns = [c.strip() for c in nodes.columns]
    edges.columns = [c.strip() for c in edges.columns]
    return nodes, edges


def compute_total_event_participation(edges: pd.DataFrame) -> dict[str, int]:
    """Berapa banyak event yang di-INVOLVED_IN oleh tiap Person (proxy importance)."""
    inv = edges[edges["relation_type"] == "INVOLVED_IN"]
    counts: dict[str, int] = defaultdict(int)
    for _, r in inv.iterrows():
        if r["source_label"] == "PERSON" and r["target_label"] == "EVENT":
            counts[r["source_name"]] += 1
    return dict(counts)


def build_subgraph(event_name: str, edges: pd.DataFrame) -> tuple[nx.MultiGraph, set[str]]:
    """Bangun subgraf untuk satu event: event + person yang INVOLVED_IN + direct P-P relations."""
    G = nx.MultiGraph()

    # 1. Person yang INVOLVED_IN ke event ini
    inv = edges[
        (edges["relation_type"] == "INVOLVED_IN")
        & (edges["target_name"] == event_name)
        & (edges["source_label"] == "PERSON")
        & (edges["target_label"] == "EVENT")
    ]
    persons = set(inv["source_name"].unique())

    if not persons:
        return G, persons

    G.add_node(event_name, kind="EVENT")
    for p in persons:
        G.add_node(p, kind="PERSON")
        G.add_edge(p, event_name, relation_type="INVOLVED_IN")

    # 2. Direct Person-Person relations dalam scope
    pp = edges[
        (edges["relation_type"].isin(["KELUARGA", "SAHABAT", "MUSUH"]))
        & (edges["source_label"] == "PERSON")
        & (edges["target_label"] == "PERSON")
        & (edges["source_name"].isin(persons))
        & (edges["target_name"].isin(persons))
    ]
    for _, r in pp.iterrows():
        if r["source_name"] == r["target_name"]:
            continue
        G.add_edge(r["source_name"], r["target_name"], relation_type=r["relation_type"])

    return G, persons


def draw_subgraph(
    G: nx.MultiGraph,
    event_name: str,
    period: str,
    page_range: str,
    importance: dict[str, int],
    ax: plt.Axes,
) -> None:
    if G.number_of_nodes() == 0:
        ax.text(0.5, 0.5, f"(no data for {event_name})", ha="center", va="center")
        ax.axis("off")
        return

    persons = [n for n, d in G.nodes(data=True) if d.get("kind") == "PERSON"]

    # Layout: event di tengah (0,0), persons di lingkaran sekitar
    pos = {event_name: (0.0, 0.0)}
    n_p = len(persons)
    # Sort persons by importance — yang penting di atas (12 o'clock), lalu searah jarum jam
    persons_sorted = sorted(persons, key=lambda p: -importance.get(p, 0))
    import math

    for i, p in enumerate(persons_sorted):
        angle = math.pi / 2 - (2 * math.pi * i / max(n_p, 1))
        radius = 1.0
        pos[p] = (radius * math.cos(angle), radius * math.sin(angle))

    # Draw edges per relation_type
    for rel_type, style in EDGE_STYLES.items():
        e_list = [(u, v) for u, v, d in G.edges(data=True) if d.get("relation_type") == rel_type]
        if not e_list:
            continue
        nx.draw_networkx_edges(
            G, pos, edgelist=e_list,
            edge_color=style["color"], width=style["width"], alpha=style["alpha"],
            style=style["style"], ax=ax,
        )

    # Draw nodes
    event_size = 2000
    max_imp = max(importance.values()) if importance else 1
    person_sizes = [
        max(100, 100 + (importance.get(p, 0) / max_imp) * 700)
        for p in persons
    ]
    nx.draw_networkx_nodes(G, pos, nodelist=[event_name], node_color="#ffd700",
                            node_size=event_size, edgecolors="#8b6914",
                            linewidths=2, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=persons, node_color="#4a90d9",
                            node_size=person_sizes, edgecolors="#1f3a5f",
                            linewidths=0.5, alpha=0.85, ax=ax)

    # Labels: event always, person top-10 by importance
    label_set = {event_name: event_name}
    top_persons = sorted(persons, key=lambda p: -importance.get(p, 0))[:10]
    for p in top_persons:
        label_set[p] = p
    nx.draw_networkx_labels(G, pos, labels=label_set, font_size=7,
                            font_weight="bold", ax=ax)

    # Title + stat counts
    n_involved = sum(1 for _, _, d in G.edges(data=True) if d.get("relation_type") == "INVOLVED_IN")
    n_kel = sum(1 for _, _, d in G.edges(data=True) if d.get("relation_type") == "KELUARGA")
    n_sah = sum(1 for _, _, d in G.edges(data=True) if d.get("relation_type") == "SAHABAT")
    n_mus = sum(1 for _, _, d in G.edges(data=True) if d.get("relation_type") == "MUSUH")

    title = f"{event_name}\n[{period}] hal {page_range} · {len(persons)} Person · "
    title += f"INVOLVED_IN={n_involved} · KEL={n_kel} · SAH={n_sah} · MUS={n_mus}"
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.axis("off")
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)


def add_legend(fig: plt.Figure) -> None:
    """Tambah legend untuk warna edge + node."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#ffd700", edgecolor="#8b6914", label="EVENT"),
        Patch(facecolor="#4a90d9", edgecolor="#1f3a5f", label="PERSON (size ∝ jumlah event)"),
        Line2D([0], [0], color="#888888", lw=1, label="INVOLVED_IN"),
        Line2D([0], [0], color="#d62728", lw=2, label="KELUARGA"),
        Line2D([0], [0], color="#2ca02c", lw=2, label="SAHABAT"),
        Line2D([0], [0], color="#ff7f0e", lw=2, linestyle="--", label="MUSUH"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=6,
                bbox_to_anchor=(0.5, -0.02), fontsize=9, frameon=False)


def main() -> None:
    nodes, edges = load_data()
    importance = compute_total_event_participation(edges)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Save 5 individual PNGs
    print("=" * 60)
    print("Generating individual sub-graph PNGs...")
    print("=" * 60)
    subgraphs: dict[str, nx.MultiGraph] = {}
    for event_name, period, page_range in EVENTS:
        G, persons = build_subgraph(event_name, edges)
        subgraphs[event_name] = G

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        draw_subgraph(G, event_name, period, page_range, importance, ax)
        add_legend(fig)
        plt.tight_layout()

        safe_name = event_name.replace(" ", "_").replace("'", "")
        out_path = OUT_DIR / f"case_study_{safe_name}.png"
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  [OK] {out_path.name} — {len(persons)} Person")

    # 2. Save combined 5-panel PNG (untuk slide tunggal)
    print()
    print("=" * 60)
    print("Generating combined 5-panel PNG...")
    print("=" * 60)
    fig, axes = plt.subplots(2, 3, figsize=(22, 14))
    axes_flat = axes.flatten()
    for i, (event_name, period, page_range) in enumerate(EVENTS):
        G = subgraphs[event_name]
        draw_subgraph(G, event_name, period, page_range, importance, axes_flat[i])
    # Sembunyikan panel ke-6 (tidak dipakai)
    axes_flat[5].axis("off")
    add_legend(fig)
    plt.suptitle("Studi Kasus 5 Event Berperiode Jauh — Knowledge Graph Sirah Nabawiyah",
                  fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    out_panel = OUT_DIR / "case_study_panel.png"
    plt.savefig(out_panel, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {out_panel.name}")

    print()
    print(f"Semua output di: {OUT_DIR}")


if __name__ == "__main__":
    main()
