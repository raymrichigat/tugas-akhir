"""
clean_v4_hybrid_genealogy.py
============================
Scoping graf Person v4_hybrid untuk analisis SNA: buang node PERSON yang hanya
tertaut ke narasi lewat **garis nasab / silsilah keluarga** (KELUARGA) tanpa
pernah ikut peristiwa mana pun.

MOTIVASI (bimbingan 2026-07-10 lanjutan):
  Model pemenang (S4-augmentation) menangkap lebih banyak rantai nasab
  (Adam -> Nuh -> Ibrahim -> ... -> Ma'ad -> ... -> Abdullah -> Muhammad).
  Rantai KELUARGA ini membuat leluhur pra-Islam (Ma'ad, Matausyalakh, Syalakh,
  Abdullah) memperoleh PageRank/betweenness tinggi PADAHAL mereka tidak pernah
  ikut satu peristiwa pun yang dinarasikan. Ini artefak struktur (chain nasab
  menggelembungkan sentralitas leluhur), bukan sentralitas sosial nyata --
  paralel dengan kasus over-ekstraksi INVOLVED_IN (Amr bin Umayyah).

KRITERIA DROP (rule-based, terdokumentasi, BUKAN cherry-pick per-nama):
  Node PERSON di-scope-keluar bila memenuhi SEMUA:
    (a) 0 partisipasi peristiwa  -> tidak muncul di edge INVOLVED_IN (weight>=0.3)
    (b) tidak punya ikatan sosial eksplisit -> tidak muncul di edge SAHABAT/MUSUH
  => tersisa hanya taut KELUARGA/nasab. Node semacam ini berada DI LUAR jaringan
     ko-partisipasi peristiwa yang menjadi objek analisis SNA (Bab 4.4), sehingga
     di-scope keluar dari graf. Node EVENT/LOCATION/TIME/PERIOD tidak tersentuh.

PENTING — INI *SCOPING SNA*, BUKAN PENGHAPUSAN KG:
  KG kanonik (`nodes_v4_hybrid.csv` + `edges_v4_hybrid.csv`) TIDAK diubah — semua
  entitas hasil ekstraksi tetap utuh sebagai basis pengetahuan (Neo4j, uji
  fungsional Bab 4.4.2, studi kasus). Skrip ini hanya MENULIS berkas turunan
  ber-scope (`nodes_v4_scoped.csv` + `edges_v4_scoped.csv`) yang dipakai SEBAGAI
  INPUT analisis sentralitas/komunitas SNA (Bab 4.4.1) via `--version v4_scoped`.

CATATAN METODOLOGI (untuk Bab 4):
  - Scoping sejajar dgn definisi "dua tokoh terhubung bila terlibat peristiwa
    yang sama". Node terbuang = tokoh yang tak pernah terlibat peristiwa (hanya
    disebut dalam silsilah), sehingga sentralitas tingginya adalah artefak rantai.
  - F1 NER TIDAK terpengaruh (operasi di tahap analisis graf, hilir).
  - Reversibel & non-destruktif: KG kanonik tak disentuh; berkas scoped terpisah.

Idempotent. Preview default; --apply untuk menulis berkas scoped.
Usage:
  venv/Scripts/python.exe src/relation_extraction/clean_v4_hybrid_genealogy.py
  venv/Scripts/python.exe src/relation_extraction/clean_v4_hybrid_genealogy.py --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
RR = ROOT / "data" / "result" / "relation_result"
NODES = RR / "nodes_v4_hybrid.csv"          # KG kanonik (input, TIDAK diubah)
EDGES = RR / "edges_v4_hybrid.csv"
NODES_OUT = RR / "nodes_v4_scoped.csv"      # berkas scoped (output SNA)
EDGES_OUT = RR / "edges_v4_scoped.csv"

WEIGHT_THRESHOLD = 0.3   # sama dgn WEIGHT_THRESHOLD di sna_analysis.py


def main() -> None:
    ap = argparse.ArgumentParser(description="Scope graf Person v4_hybrid (buang node nasab-only)")
    ap.add_argument("--apply", action="store_true",
                    help="Tulis berkas scoped nodes/edges_v4_scoped (default: preview)")
    args = ap.parse_args()
    DRY = not args.apply

    print("=" * 66)
    print(f"SCOPE v4_hybrid — buang node PERSON nasab-only   [{'PREVIEW' if DRY else 'APPLY'}]")
    print("=" * 66)

    nodes = pd.read_csv(NODES, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    edges = pd.read_csv(EDGES, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    n0, e0 = len(nodes), len(edges)
    print(f"\nLoaded: {n0} nodes, {e0} edges")

    w = pd.to_numeric(edges["weight"], errors="coerce").fillna(WEIGHT_THRESHOLD)

    # (a) peserta peristiwa: endpoint PERSON di INVOLVED_IN (w>=0.3)
    inv = edges[(edges["relation_type"] == "INVOLVED_IN") & (w >= WEIGHT_THRESHOLD)]
    participants: set[str] = set()
    for _, r in inv.iterrows():
        if r["source_label"] == "PERSON":
            participants.add(r["source_name"])
        if r["target_label"] == "PERSON":
            participants.add(r["target_name"])

    # (b) punya ikatan sosial eksplisit (SAHABAT/MUSUH)
    soc = edges[edges["relation_type"].isin(["SAHABAT", "MUSUH"])]
    social: set[str] = set(soc["source_name"]) | set(soc["target_name"])

    persons = nodes[nodes["label"] == "PERSON"]
    keep_mask = persons["name"].isin(participants | social)
    drop_names = set(persons[~keep_mask]["name"])

    # family-degree (KELUARGA) untuk pelaporan
    kel = edges[edges["relation_type"] == "KELUARGA"]
    kel_deg: dict[str, int] = {}
    for _, r in kel.iterrows():
        for x in (r["source_name"], r["target_name"]):
            kel_deg[x] = kel_deg.get(x, 0) + 1

    # ── apply drop ──
    new_nodes = nodes[~((nodes["label"] == "PERSON") & (nodes["name"].isin(drop_names)))].copy()
    ep_drop = edges.apply(
        lambda r: (r["source_label"] == "PERSON" and r["source_name"] in drop_names)
        or (r["target_label"] == "PERSON" and r["target_name"] in drop_names),
        axis=1,
    )
    new_edges = edges[~ep_drop].copy()

    # ── report ──
    print(f"\nPERSON total          : {len(persons)}")
    print(f"  peserta peristiwa   : {len(participants & set(persons['name']))}")
    print(f"  punya SAHABAT/MUSUH : {len(social & set(persons['name']))}")
    print(f"  DIBUANG (nasab-only): {len(drop_names)}")

    top = sorted(drop_names, key=lambda n: -kel_deg.get(n, 0))[:20]
    print("\n── 20 node terbuang dgn family-degree tertinggi (rantai nasab utama) ──")
    for nm in top:
        print(f"  {nm:36s} kel_edges={kel_deg.get(nm, 0)}")

    print("\n" + "-" * 66)
    print(f"  nodes : {n0} -> {len(new_nodes)}   (Δ {len(new_nodes) - n0})")
    print(f"  edges : {e0} -> {len(new_edges)}   (Δ {len(new_edges) - e0})")
    for lb in ("PERSON", "EVENT", "LOCATION", "TIME"):
        b = (nodes["label"] == lb).sum(); a = (new_nodes["label"] == lb).sum()
        print(f"  {lb:9s}: {b} -> {a}")
    print("-" * 66)

    if DRY:
        print("\n[PREVIEW] Tidak ada file ditulis. Jalankan --apply untuk menulis berkas scoped.")
        return

    new_nodes.to_csv(NODES_OUT, sep=";", encoding="utf-8-sig", index=False)
    new_edges.to_csv(EDGES_OUT, sep=";", encoding="utf-8-sig", index=False)
    print(f"\n[APPLY] Ditulis berkas scoped (KG kanonik TIDAK diubah):")
    print(f"  -> {NODES_OUT}")
    print(f"  -> {EDGES_OUT}")
    print("Next: re-run SNA pakai berkas scoped ->")
    print("  python src/analysis/sna_analysis.py       --version v4_scoped")
    print("  python src/analysis/sna_graph_metrics.py  --version v4_scoped")
    print("  python src/analysis/event_centrality.py   --version v4_scoped")
    print("  python src/analysis/community_wordcloud.py --version v4_scoped")


if __name__ == "__main__":
    main()
