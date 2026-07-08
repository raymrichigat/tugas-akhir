"""
community_wordcloud.py
=======================
Wordcloud per komunitas Louvain (revisi Bu Diana 2026-05-16).

Tujuan:
  - Visualisasi konten/topik tiap komunitas SNA Sirah berdasarkan **evidence text**
    (kalimat narasi yang menghasilkan edge).
  - Interpretasi semantik: komunitas X tentang fase apa? Tokoh utama? Lokasi?
  - Kontekstualisasi Q-value Louvain (Q=0.327) — apakah komunitas yang ditemukan
    benar-benar koheren secara naratif, bukan artifact algoritma.

Sumber data:
  - data/result/analysis/sna_metrics.csv     — community assignment per Person
  - data/result/relation_result/edges_v2.csv — evidence text untuk setiap relasi

Algoritma:
  1. Load community map dari sna_metrics.csv (Person → community_id).
  2. Untuk tiap edge, tentukan komunitas (dari source/target Person):
       - Kalau source & target sama-sama Person dan di komunitas yang sama,
         evidence di-attribute ke komunitas itu.
       - Kalau Person-Event/Time/Location, evidence di-attribute ke komunitas
         dari Person source.
  3. Concat evidence text per komunitas, drop stopwords + custom Sirah-stopwords.
  4. Generate wordcloud + ekstrak top-30 token + entity count per komunitas.
  5. Output: 1 PNG per komunitas (≥3 anggota) + summary md dengan interpretasi.

Filter komunitas:
  Komunitas dengan <3 anggota di-skip (12 komunitas isi 2 orang) — wordcloud
  dengan korpus terlalu kecil tidak meaningful.

Output:
  - data/result/analysis/community_wordclouds/community_{id}.png  (per komunitas)
  - data/result/analysis/community_wordclouds_summary.md           (interpretasi + Q-value)

Idempotent. Usage:
  venv\\Scripts\\python.exe src/analysis/community_wordcloud.py
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SNA_CSV = ROOT / "data" / "result" / "analysis" / "sna_metrics.csv"
EDGES_CSV = ROOT / "data" / "result" / "relation_result" / "edges_v2.csv"
NODES_CSV = ROOT / "data" / "result" / "relation_result" / "nodes_v2.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis" / "community_wordclouds"
SUMMARY_MD = ROOT / "data" / "result" / "analysis" / "community_wordclouds_summary.md"

MIN_COMMUNITY_SIZE = 3

INDONESIAN_STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "ini", "itu",
    "adalah", "ialah", "atau", "tetapi", "namun", "akan", "sudah", "telah",
    "tidak", "bukan", "ada", "tak", "saja", "juga", "hanya", "sangat", "lebih",
    "kurang", "agar", "supaya", "karena", "sebab", "ketika", "saat", "sambil",
    "maka", "jika", "kalau", "bila", "sehingga", "lalu", "kemudian", "setelah",
    "sebelum", "selama", "selain", "kecuali", "yaitu", "yakni", "antara",
    "tentang", "terhadap", "menjadi", "menjadikan", "para", "sebuah", "satu",
    "dua", "tiga", "beberapa", "semua", "seluruh", "tiap", "setiap", "diri",
    "mereka", "kami", "kita", "kamu", "engkau", "anda", "beliau", "dia",
    "ia", "aku", "saya", "lah", "pun", "lah", "ku", "mu", "nya",
    "saw", "sw", "subhanahu", "ta'ala", "berkata", "katanya", "kata", "ujarnya",
    "kemudian", "selanjutnya", "akhirnya", "sebelumnya", "demikian",
    "pula", "begitu", "begitupun", "demikianlah", "tersebut", "terlebih",
    "bahwa", "sebagaimana", "sebagai", "termasuk", "yaitu", "yakni",
    "satu", "kepada", "oleh", "dalam", "bagi", "atas", "bawah", "samping",
    "depan", "belakang", "sini", "situ", "sana", "mana", "manakala",
    "bersama", "telah", "sudah", "belum", "masih", "akan", "ingin", "mau",
    "harus", "boleh", "bisa", "dapat", "perlu",
}

SIRAH_FILLER = {
    "bin", "bint", "abu", "ibnu", "putra", "putri", "anak", "ayah", "ibu",
    "kepada", "perkataan", "ucapnya", "lalu", "kemudian", "demikian",
    "pula", "begitu", "yaitu", "yakni", "tersebut", "terhadap", "tentang",
    "ada", "rasulullah", "nabi", "muhammad", "saw",
    "shallallahu", "alaihi", "wa", "sallam", "as", "ra",
    "ayat", "surah", "hadits", "riwayat", "sahih", "lemah",
}

STOPWORDS = INDONESIAN_STOPWORDS | SIRAH_FILLER

TOKEN_PATTERN = re.compile(r"\b[A-Za-zÀ-ÿ'\-]+\b", re.UNICODE)


def tokenize(text: str) -> list[str]:
    raw = TOKEN_PATTERN.findall(text.lower())
    return [t for t in raw if t not in STOPWORDS and len(t) >= 3]


def load_community_map(sna_csv: Path) -> tuple[dict[str, int], pd.DataFrame]:
    df = pd.read_csv(sna_csv, sep=";", encoding="utf-8-sig")
    return dict(zip(df["name"], df["community"])), df


def load_evidence(edges_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(edges_csv, sep=";", encoding="utf-8-sig").fillna("")
    return df


def attribute_evidence_to_community(
    edges_df: pd.DataFrame, comm_map: dict[str, int]
) -> dict[int, list[str]]:
    """
    Each edge's evidence is attributed to the source Person's community.
    Edges where source is not Person (or not in comm_map) → skip.
    """
    comm_evidence: dict[int, list[str]] = defaultdict(list)
    for _, row in edges_df.iterrows():
        src = row["source_name"]
        if src not in comm_map:
            continue
        cid = int(comm_map[src])
        evidence = str(row.get("evidence", "")).strip()
        if evidence and evidence not in {"", "nan"}:
            comm_evidence[cid].append(evidence)
    return comm_evidence


def get_top_persons_per_community(sna_df: pd.DataFrame, top_k: int = 8) -> dict[int, list[str]]:
    sna_df = sna_df.sort_values("pagerank", ascending=False)
    out: dict[int, list[str]] = defaultdict(list)
    for _, row in sna_df.iterrows():
        cid = int(row["community"])
        if len(out[cid]) < top_k:
            out[cid].append(row["name"])
    return out


def render_wordcloud(community_id: int, text: str, out_dir: Path) -> Path | None:
    try:
        from wordcloud import WordCloud
    except ImportError:
        print("  [WARN] wordcloud not installed, skip")
        return None
    if not text.strip():
        return None

    wc = WordCloud(
        width=1200,
        height=700,
        background_color="white",
        max_words=80,
        stopwords=STOPWORDS,
        collocations=False,
        random_state=42,
        colormap="viridis",
    ).generate(text)

    out_path = out_dir / f"community_{community_id:02d}.png"
    wc.to_file(str(out_path))
    return out_path


def compute_modularity_q(comm_map: dict[str, int]) -> float | None:
    """
    Recompute Q-value Louvain di Person co-participation graph supaya bisa
    dilaporkan akurat di summary.

    Sumber graf: rebuild dari edges_v2.csv (mirror sna_analysis.py logic).
    """
    try:
        import networkx as nx
        from networkx.algorithms.community.quality import modularity
    except ImportError:
        return None

    edges_df = load_evidence(EDGES_CSV)
    involved = edges_df[edges_df["relation_type"] == "INVOLVED_IN"]
    # Threshold + weighted co-participation (konsisten dgn sna_analysis.py):
    # buang co-mention lemah, bobot pasangan = Σ min(w1, w2) per event bersama.
    WEIGHT_THRESHOLD = 0.3
    event_person_w: dict[str, dict[str, float]] = defaultdict(dict)
    for _, row in involved.iterrows():
        try:
            w = float(row.get("weight", WEIGHT_THRESHOLD))
        except (TypeError, ValueError):
            w = WEIGHT_THRESHOLD
        if w < WEIGHT_THRESHOLD:
            continue
        ev, p = row["target_name"], row["source_name"]
        if p not in event_person_w[ev] or w > event_person_w[ev][p]:
            event_person_w[ev][p] = w

    G = nx.Graph()
    copart: dict[tuple[str, str], float] = defaultdict(float)
    for ev, pw in event_person_w.items():
        ps_list = sorted(pw.keys())
        for i in range(len(ps_list)):
            for j in range(i + 1, len(ps_list)):
                copart[(ps_list[i], ps_list[j])] += min(pw[ps_list[i]], pw[ps_list[j]])
    for (p1, p2), w in copart.items():
        G.add_edge(p1, p2, weight=round(w, 3))

    person_rels = edges_df[edges_df["relation_type"].isin(["KELUARGA", "SAHABAT", "MUSUH"])]
    for _, row in person_rels.iterrows():
        s, t = row["source_name"], row["target_name"]
        try:
            w = float(row.get("weight", 0.5))
        except (TypeError, ValueError):
            w = 0.5
        if G.has_edge(s, t):
            G[s][t]["weight"] += w
        else:
            G.add_edge(s, t, weight=w)

    comm_groups: dict[int, set[str]] = defaultdict(set)
    for n in G.nodes():
        if n in comm_map:
            comm_groups[int(comm_map[n])].add(n)

    if not comm_groups:
        return None
    return float(modularity(G, list(comm_groups.values()), weight="weight"))


def main():
    import argparse
    global SNA_CSV, EDGES_CSV, NODES_CSV, OUT_DIR, SUMMARY_MD

    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["v2", "v3", "v4", "v4_hybrid"], default="v3",
                    help="Pilih versi nodes/edges (default: v3)")
    args = ap.parse_args()

    if args.version in ("v4", "v4_hybrid"):
        suffix = "_hybrid" if args.version == "v4_hybrid" else ""
        vdir = ROOT / "data" / "result" / "analysis" / args.version
        SNA_CSV = vdir / "sna_metrics.csv"
        EDGES_CSV = ROOT / "data" / "result" / "relation_result" / f"edges_v4{suffix}.csv"
        NODES_CSV = ROOT / "data" / "result" / "relation_result" / f"nodes_v4{suffix}.csv"
        OUT_DIR = vdir / "community_wordclouds"
        SUMMARY_MD = vdir / "community_wordclouds_summary.md"
    elif args.version == "v3":
        SNA_CSV = ROOT / "data" / "result" / "analysis" / "v3" / "sna_metrics.csv"
        EDGES_CSV = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
        NODES_CSV = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"
        OUT_DIR = ROOT / "data" / "result" / "analysis" / "v3" / "community_wordclouds"
        SUMMARY_MD = ROOT / "data" / "result" / "analysis" / "v3" / "community_wordclouds_summary.md"

    print("=" * 60)
    print(f"COMMUNITY WORDCLOUD — Knowledge Graph Sirah [{args.version}]")
    print("=" * 60)

    print(f"\n[1/5] loading sna_metrics + {EDGES_CSV.name}...")
    comm_map, sna_df = load_community_map(SNA_CSV)
    edges_df = load_evidence(EDGES_CSV)
    print(f"  persons in SNA: {len(comm_map)}")
    print(f"  edges total   : {len(edges_df)}")

    print("\n[2/5] attributing evidence text to communities...")
    comm_evidence = attribute_evidence_to_community(edges_df, comm_map)
    sizes = sna_df["community"].value_counts().sort_index()
    eligible = [int(cid) for cid, sz in sizes.items() if sz >= MIN_COMMUNITY_SIZE]
    print(f"  communities total       : {len(sizes)}")
    print(f"  eligible (size >= {MIN_COMMUNITY_SIZE}) : {len(eligible)}")
    print(f"  skipped (size < {MIN_COMMUNITY_SIZE})   : {len(sizes) - len(eligible)}")

    print("\n[3/5] computing modularity Q (Louvain proper)...")
    q_value = compute_modularity_q(comm_map)
    print(f"  Q = {q_value:.4f}" if q_value is not None else "  Q = N/A")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[4/5] rendering wordcloud + extract top tokens per community...")
    top_persons = get_top_persons_per_community(sna_df)

    summary_rows: list[dict] = []
    for cid in eligible:
        evidences = comm_evidence.get(cid, [])
        full_text = " ".join(evidences)
        tokens = tokenize(full_text)
        top_tokens = Counter(tokens).most_common(15)

        png_path = render_wordcloud(cid, full_text, OUT_DIR)
        png_rel = png_path.relative_to(ROOT) if png_path else None

        size = int(sizes.get(cid, 0))
        n_evidences = len(evidences)
        members = top_persons.get(cid, [])

        print(f"  comm {cid:02d}: size={size:3d}  evidences={n_evidences:4d}  "
              f"png={'OK' if png_path else 'SKIP'}")

        summary_rows.append({
            "community": cid,
            "size": size,
            "n_evidences": n_evidences,
            "top_persons": members,
            "top_tokens": top_tokens,
            "png": png_rel,
        })

    print("\n[5/5] writing summary md...")
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Community Wordcloud + Interpretasi — Knowledge Graph Sirah\n")
    lines.append("**Tanggal:** 2026-05-26\n")
    lines.append("**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas "
                 "Louvain + interpretasi semantik + arti Q-value.\n")

    lines.append("## Tentang Q-value Louvain (Modularity)\n")
    if q_value is not None:
        lines.append(f"**Q (recomputed, weighted) = `{q_value:.4f}`**\n")
    lines.append("Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur "
                 "komunitas dibanding edge yang acak (random rewiring null model):")
    lines.append("- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).")
    lines.append("- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.")
    lines.append("- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.")
    lines.append("- **Q > 0.7**   : sangat kuat (jarang di network natural).\n")
    if q_value is not None:
        if q_value < 0.25:
            interp = "**lemah** — komunitas yang ditemukan kemungkinan artifact algoritma."
        elif q_value < 0.4:
            interp = ("**moderate** — struktur komunitas ada tapi tidak clear-cut. "
                      "Banyak Person punya koneksi ke beberapa komunitas, "
                      "konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) "
                      "berinteraksi luas lintas fase historis.")
        elif q_value < 0.6:
            interp = "**kuat** — komunitas terbukti koheren."
        else:
            interp = "**sangat kuat** — graf sangat ter-segregasi."
        lines.append(f"Interpretasi untuk Sirah: Q={q_value:.3f} → {interp}\n")
    lines.append("Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 "
                 "vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman "
                 "konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.\n")

    lines.append("\n## Komunitas yang Di-render Wordcloud\n")
    lines.append(f"Filter: minimal {MIN_COMMUNITY_SIZE} anggota. {len(eligible)} dari "
                 f"{len(sizes)} komunitas memenuhi syarat. {len(sizes) - len(eligible)} "
                 "komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).\n")

    for s in summary_rows:
        lines.append(f"### Komunitas {s['community']} — {s['size']} anggota, "
                     f"{s['n_evidences']} evidence\n")
        if s["png"]:
            lines.append(f"![wordcloud {s['community']}]({s['png'].as_posix()})\n")
        lines.append(f"**Top tokoh (PageRank):** {', '.join(s['top_persons'])}\n")
        if s["top_tokens"]:
            tt = ", ".join(f"{tok}({cnt})" for tok, cnt in s["top_tokens"][:10])
            lines.append(f"**Top tokens:** {tt}\n")
        lines.append("**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens "
                     "+ tokoh utama — fase apa, tema apa, lokasi dominan]_\n")

    lines.append("\n## Catatan Implementasi\n")
    lines.append("- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, "
                 "rasulullah, nabi, saw, hadits, riwayat).")
    lines.append("- Tokenization: regex `\\b[A-Za-z'\\-]+\\b` lower-cased, drop token <3 char.")
    lines.append("- Evidence di-attribute ke komunitas source Person — kalau source bukan "
                 "Person (mis. Event-Time OCCURRED_ON), evidence skip.")
    lines.append("- Wordcloud max 80 words, layout deterministic seed 42.")
    lines.append("- Interpretasi semantik per komunitas **wajib diisi manual** — bukan "
                 "sesuatu yang bisa di-auto dari token frequency saja.")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {SUMMARY_MD}")

    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
