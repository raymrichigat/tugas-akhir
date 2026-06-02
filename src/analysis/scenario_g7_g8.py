"""
scenario_g7_g8.py
=================
Menghitung dua skenario graf yang sebelumnya hanya rancangan:

- **G7 — Lokasi dengan peran sentral.**
  Bangun graf lokasi: dua LOCATION terhubung bila ada PERSON yang terlibat
  (INVOLVED_IN) di EVENT yang terjadi (OCCURRED_AT) di kedua lokasi tersebut.
  Bobot edge = jumlah tokoh bersama. Lalu hitung betweenness + degree.

- **G8 — Keberagaman fase keterlibatan tokoh.**
  Untuk tiap PERSON: kumpulkan EVENT yang dia ikuti (INVOLVED_IN), petakan tiap
  event ke FASE Sirah (lewat periode_bab → period_mapping.json), hitung jumlah
  FASE unik. Tokoh yang muncul di banyak fase = tokoh "lintas-babak".

Sumber: data/result/relation_result/{nodes,edges}_v3.csv (sep ';') +
        data/result/relation_result/period_mapping.json
Output: data/result/analysis/v3/scenario_g7_g8.md (+ print ringkasan).

Idempotent, read-only terhadap data KG (cuma menulis file analisis baru).
Usage: python src/analysis/scenario_g7_g8.py
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
REL = BASE / "data" / "result" / "relation_result"
OUT = BASE / "data" / "result" / "analysis" / "v3"
NODES_CSV = REL / "nodes_v3.csv"
EDGES_CSV = REL / "edges_v3.csv"
PERIOD_JSON = REL / "period_mapping.json"
OUT_MD = OUT / "scenario_g7_g8.md"

TOP_N = 15


def load_data():
    nodes = pd.read_csv(NODES_CSV, sep=";", dtype=str).fillna("")
    edges = pd.read_csv(EDGES_CSV, sep=";", dtype=str).fillna("")
    periods = json.loads(PERIOD_JSON.read_text(encoding="utf-8"))
    label_to_phase = {p["label"].strip(): p["phase"] for p in periods}
    # Override untuk label custom dari enrichment lifecycle (apply_period_to_v3)
    # yang bukan salah satu 15 label periode kanonik:
    label_to_phase.setdefault(
        "Penaklukan Makkah hingga Akhir Kenabian",
        "Fase VI — Konsolidasi & Akhir Kenabian")
    return nodes, edges, label_to_phase


# ---------------------------------------------------------------- G8
def compute_g8(nodes, edges, label_to_phase):
    """Keberagaman fase keterlibatan tokoh."""
    ev = nodes[nodes["label"] == "EVENT"]
    event_to_phase = {}
    unmapped = set()
    for _, r in ev.iterrows():
        lbl = r["periode_bab"].strip()
        phase = label_to_phase.get(lbl)
        if phase:
            event_to_phase[r["name"]] = phase
        elif lbl:
            unmapped.add(lbl)

    inv = edges[(edges["relation_type"] == "INVOLVED_IN")
                & (edges["source_label"] == "PERSON")
                & (edges["target_label"] == "EVENT")]

    person_phases: dict[str, set] = {}
    person_events: dict[str, set] = {}
    for _, r in inv.iterrows():
        person, event = r["source_name"], r["target_name"]
        person_events.setdefault(person, set()).add(event)
        ph = event_to_phase.get(event)
        if ph:
            person_phases.setdefault(person, set()).add(ph)

    rows = []
    for person, phases in person_phases.items():
        rows.append({
            "person": person,
            "n_fase": len(phases),
            "n_event": len(person_events.get(person, set())),
            "fase": " | ".join(sorted(phases)),
        })
    df = pd.DataFrame(rows).sort_values(
        ["n_fase", "n_event"], ascending=False).reset_index(drop=True)
    return df, sorted(unmapped), len(event_to_phase)


# ---------------------------------------------------------------- G7
def compute_g7(edges):
    """Lokasi dengan peran sentral (graf lokasi via tokoh bersama)."""
    occ = edges[(edges["relation_type"] == "OCCURRED_AT")
                & (edges["source_label"] == "EVENT")
                & (edges["target_label"] == "LOCATION")]
    event_to_locs: dict[str, set] = {}
    for _, r in occ.iterrows():
        event_to_locs.setdefault(r["source_name"], set()).add(r["target_name"])

    inv = edges[(edges["relation_type"] == "INVOLVED_IN")
                & (edges["source_label"] == "PERSON")
                & (edges["target_label"] == "EVENT")]
    person_to_locs: dict[str, set] = {}
    for _, r in inv.iterrows():
        person, event = r["source_name"], r["target_name"]
        for loc in event_to_locs.get(event, ()):  # lokasi event yg dia ikuti
            person_to_locs.setdefault(person, set()).add(loc)

    # Projeksi: lokasi-lokasi yang berbagi tokoh
    G = nx.Graph()
    G.add_nodes_from({l for locs in event_to_locs.values() for l in locs})
    for locs in person_to_locs.values():
        for a, b in combinations(sorted(locs), 2):
            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)

    if G.number_of_nodes() == 0:
        return pd.DataFrame(), G

    btw = nx.betweenness_centrality(G, weight=None, normalized=True)
    deg = dict(G.degree())
    wdeg = dict(G.degree(weight="weight"))
    rows = [{
        "lokasi": n,
        "betweenness": round(btw[n], 4),
        "degree": deg[n],
        "weighted_degree": wdeg[n],
    } for n in G.nodes()]
    df = pd.DataFrame(rows).sort_values(
        ["weighted_degree", "degree"], ascending=False).reset_index(drop=True)
    return df, G


# ---------------------------------------------------------------- output
def main():
    nodes, edges, label_to_phase = load_data()
    g8, unmapped, n_mapped = compute_g8(nodes, edges, label_to_phase)
    g7, gloc = compute_g7(edges)

    lines = []
    lines.append("# Skenario G7 & G8 — Hasil (KG v3 cleaned)\n")
    lines.append("> Dihasilkan oleh `src/analysis/scenario_g7_g8.py`. "
                 "Sumber: `nodes_v3.csv` + `edges_v3.csv` + `period_mapping.json`.\n")

    # G7
    dens = nx.density(gloc)
    lines.append("\n## G7 — Lokasi dengan peran sentral\n")
    lines.append("Graf lokasi: dua LOCATION terhubung bila ada tokoh yang "
                 "terlibat di peristiwa pada **kedua** lokasi (bobot = jumlah "
                 "tokoh bersama).\n")
    lines.append(f"\n- Node lokasi: **{gloc.number_of_nodes()}** | "
                 f"Edge: **{gloc.number_of_edges()}** | "
                 f"Density: **{dens:.3f}**\n")
    lines.append("\n> ⚠️ **Betweenness di sini nyaris tidak diskriminatif** "
                 "(graf lokasi sangat padat — banyak lokasi terhubung ke hampir "
                 "semua lokasi lain karena tokoh sentral seperti Muhammad hadir "
                 "di peristiwa lintas hampir semua tempat). Peringkat utama "
                 "karena itu pakai **weighted degree** (total tokoh-bersama), "
                 "yang jauh lebih informatif.\n")
    lines.append(f"\n### Top-{TOP_N} lokasi (urut Weighted degree)\n")
    lines.append("| Rank | Lokasi | Weighted degree | Degree | Betweenness |")
    lines.append("|---:|---|---:|---:|---:|")
    for i, r in g7.head(TOP_N).iterrows():
        lines.append(f"| {i+1} | {r['lokasi']} | {r['weighted_degree']} | "
                     f"{r['degree']} | {r['betweenness']:.4f} |")

    # G8
    lines.append(f"\n## G8 — Keberagaman fase keterlibatan tokoh\n")
    lines.append("Jumlah **fase Sirah unik** (dari 6 fase) tempat seorang tokoh "
                 "terlibat, via `INVOLVED_IN` → event → `periode_bab` → fase. "
                 "Tinggi = tokoh muncul lintas banyak babak.\n")
    lines.append(f"\n- Event ter-petakan ke fase: **{n_mapped}**")
    if unmapped:
        lines.append(f"\n- ⚠️ periode_bab tak cocok ke 6 fase: {unmapped}")
    lines.append(f"\n\n### Top-{TOP_N} tokoh (urut jumlah fase unik)\n")
    lines.append("| Rank | Tokoh | Jml fase | Jml event | Fase yang disinggahi |")
    lines.append("|---:|---|---:|---:|---|")
    for i, r in g8.head(TOP_N).iterrows():
        fase_short = r["fase"].replace("Fase ", "").replace(
            " — Pra-Islam & Latar Belakang", " (Pra-Islam)").replace(
            " — Periode Makkah", " (Makkah)").replace(
            " — Periode Madinah Awal", " (Madinah Awal)").replace(
            " — Periode Peperangan Besar", " (Perang Besar)").replace(
            " — Diplomasi & Ekspansi", " (Diplomasi)").replace(
            " — Konsolidasi & Akhir Kenabian", " (Konsolidasi)").replace(
            " | ", " · ")  # hindari '|' yang memecah sel tabel markdown
        lines.append(f"| {i+1} | {r['person']} | {r['n_fase']} | "
                     f"{r['n_event']} | {fase_short} |")

    # distribusi G8
    dist = g8["n_fase"].value_counts().sort_index(ascending=False)
    lines.append(f"\n### Distribusi (berapa tokoh menyinggahi N fase)\n")
    lines.append("| Jml fase | Jml tokoh |")
    lines.append("|---:|---:|")
    for k, v in dist.items():
        lines.append(f"| {k} | {v} |")

    OUT.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ringkasan ke console
    print(f"[G7] lokasi graph: {gloc.number_of_nodes()} node / "
          f"{gloc.number_of_edges()} edge / density {nx.density(gloc):.3f}")
    print("[G7] Top-10 (urut weighted_degree):")
    print(g7.head(10).to_string(index=False))
    print(f"\n[G8] {n_mapped} event ter-petakan; unmapped={unmapped}")
    print("[G8] Top-10 keberagaman fase:")
    print(g8.head(10)[["person", "n_fase", "n_event"]].to_string(index=False))
    print(f"\n[OUT] {OUT_MD}")


if __name__ == "__main__":
    main()
