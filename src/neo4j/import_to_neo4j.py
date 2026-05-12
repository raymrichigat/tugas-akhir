"""
Import Knowledge Graph ke Neo4j — Sirah Nabawiyah
Membaca nodes.csv & edges.csv dari relation_extraction, lalu:
  1. Generate file Cypher (.cypher) untuk import manual via Neo4j Browser
  2. Jika neo4j driver terinstall, import langsung via Bolt protocol

Cara pakai:
  # Generate Cypher saja (tanpa koneksi):
  python import_to_neo4j.py

  # Import langsung ke Neo4j:
  python import_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <password>

  # Jika ingin hapus data lama dulu:
  python import_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <password> --clear
"""

import argparse
import json
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
RR_DIR = BASE_DIR / "data" / "result" / "relation_result"
OUT_DIR = BASE_DIR / "data" / "result" / "neo4j"

IN_NODES_V1 = RR_DIR / "nodes.csv"
IN_EDGES_V1 = RR_DIR / "edges.csv"
IN_NODES_V2 = RR_DIR / "nodes_v2.csv"
IN_EDGES_V2 = RR_DIR / "edges_v2.csv"
PERIOD_JSON = RR_DIR / "period_mapping.json"

OUT_CYPHER_V1 = OUT_DIR / "import_sirah.cypher"
OUT_CYPHER_V2 = OUT_DIR / "import_sirah_v2.cypher"


def escape_cypher(s: str) -> str:
    """Escape string untuk Cypher literal."""
    if not isinstance(s, str):
        return str(s)
    return s.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


def generate_cypher(nodes_df: pd.DataFrame, edges_df: pd.DataFrame,
                    periods: list[dict] | None = None) -> str:
    """
    Generate Cypher queries untuk import ke Neo4j.

    Kalau `periods` diisi (v2 mode), Period akan dibuat sebagai first-class node
    dan EVENT akan punya relasi `IN_PERIOD` ke Period.
    """
    lines = []

    version_tag = "v2 (with Period nodes)" if periods else "v1 (no Period nodes)"
    lines.append("// ============================================================")
    lines.append(f"// Knowledge Graph Sirah Nabawiyah — Import Script [{version_tag}]")
    lines.append("// Auto-generated oleh import_to_neo4j.py")
    lines.append("// ============================================================")
    lines.append("")

    # Constraints & indexes
    lines.append("// -- Constraints --")
    for label in ["Person", "Event", "Location", "Time"]:
        lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.name IS UNIQUE;")
    if periods:
        lines.append("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Period) REQUIRE n.period_id IS UNIQUE;")
    lines.append("")

    # Period nodes (v2 only)
    if periods:
        lines.append("// -- Period nodes (v2: top-down periodization, 15 periods) --")
        for p in periods:
            pid = p["period_id"]
            label = escape_cypher(p["label"])
            phase = escape_cypher(p["phase"])
            desc = escape_cypher(p.get("description", ""))
            page_start = p["page_start"]
            page_end = p["page_end"]
            bab_ids = p.get("bab_ids", [])
            bab_count = len(bab_ids)
            props = (
                f'period_id: "{pid}", '
                f'label: "{label}", '
                f'phase: "{phase}", '
                f'description: "{desc}", '
                f'page_start: {page_start}, '
                f'page_end: {page_end}, '
                f'bab_count: {bab_count}'
            )
            lines.append(f'MERGE (n:Period {{period_id: "{pid}"}}) SET n += {{{props}}};')
        lines.append("")

    # Nodes
    lines.append("// -- Nodes --")
    label_map = {"PERSON": "Person", "EVENT": "Event", "LOCATION": "Location", "TIME": "Time"}

    for _, row in nodes_df.iterrows():
        neo_label = label_map.get(row["label"], row["label"])
        name = escape_cypher(row["name"])
        node_id = row["node_id"]
        freq = row["frequency"]
        aliases = escape_cypher(str(row.get("aliases", "")))

        props = f'name: "{name}", node_id: "{node_id}", frequency: {freq}'
        if aliases:
            props += f', aliases: "{aliases}"'

        # Tambah periode_bab dan page_range untuk EVENT
        periode_bab = escape_cypher(str(row.get("periode_bab", "")))
        page_range = escape_cypher(str(row.get("page_range", "")))
        if periode_bab:
            props += f', periode_bab: "{periode_bab}"'
        if page_range:
            props += f', page_range: "{page_range}"'

        lines.append(f'MERGE (n:{neo_label} {{name: "{name}"}}) SET n += {{{props}}};')

    lines.append("")

    # Edges
    lines.append("// -- Edges --")
    src_label_map = {"PERSON": "Person", "EVENT": "Event", "LOCATION": "Location", "TIME": "Time"}

    for _, row in edges_df.iterrows():
        src_label = src_label_map.get(row["source_label"], row["source_label"])
        tgt_label = src_label_map.get(row["target_label"], row["target_label"])
        src_name = escape_cypher(row["source_name"])
        tgt_name = escape_cypher(row["target_name"])
        rel_type = row["relation_type"]
        freq = row["frequency"]
        evidence = escape_cypher(str(row.get("evidence", ""))[:200])
        halaman = escape_cypher(str(row.get("halaman", "")))
        weight = row.get("weight", 0.5)
        periode_bab = escape_cypher(str(row.get("periode_bab", "")))
        relation_subtype = escape_cypher(str(row.get("relation_subtype", "")))

        props = (
            f'r.frequency = {freq}, r.halaman = "{halaman}", '
            f'r.weight = {weight}, '
            f'r.evidence = "{evidence}"'
        )
        if periode_bab:
            props += f', r.periode_bab = "{periode_bab}"'
        if relation_subtype:
            props += f', r.relation_subtype = "{relation_subtype}"'

        lines.append(
            f'MATCH (a:{src_label} {{name: "{src_name}"}}), (b:{tgt_label} {{name: "{tgt_name}"}}) '
            f'MERGE (a)-[r:{rel_type}]->(b) '
            f'SET {props};'
        )

    # Event -> Period relationships (v2 only)
    if periods:
        # Build period_label → period_id lookup
        label_to_pid = {p["label"]: p["period_id"] for p in periods}
        event_nodes = nodes_df[nodes_df["label"] == "EVENT"]
        lines.append("")
        lines.append("// -- Event → Period (IN_PERIOD) --")
        in_period_count = 0
        for _, row in event_nodes.iterrows():
            ev_name = escape_cypher(row["name"])
            periode_label = str(row.get("periode_bab", "")).strip()
            if periode_label in label_to_pid:
                pid = label_to_pid[periode_label]
                lines.append(
                    f'MATCH (e:Event {{name: "{ev_name}"}}), (p:Period {{period_id: "{pid}"}}) '
                    f'MERGE (e)-[:IN_PERIOD]->(p);'
                )
                in_period_count += 1
        lines.append(f"// IN_PERIOD relations created: {in_period_count}")

    lines.append("")
    lines.append("// -- Selesai --")
    total_msg = f"// Total: {len(nodes_df)} nodes, {len(edges_df)} edges"
    if periods:
        total_msg += f", {len(periods)} Period nodes"
    lines.append(total_msg)

    return "\n".join(lines)


def import_via_driver(uri: str, user: str, password: str, cypher: str, clear: bool = False):
    """Import langsung ke Neo4j via Python driver."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("ERROR: neo4j driver tidak terinstall.")
        print("Install: pip install neo4j")
        return False

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        driver.verify_connectivity()
        print(f"  Terhubung ke Neo4j: {uri}")
    except Exception as e:
        print(f"ERROR: Tidak bisa terhubung ke Neo4j: {e}")
        return False

    with driver.session() as session:
        if clear:
            print("  Menghapus data lama...")
            session.run("MATCH (n) DETACH DELETE n")
            print("  Data lama dihapus.")

        # Execute setiap statement secara terpisah
        statements = [s.strip() for s in cypher.split(";") if s.strip() and not s.strip().startswith("//")]
        total = len(statements)
        print(f"  Menjalankan {total} Cypher statements...")

        for i, stmt in enumerate(statements, 1):
            try:
                session.run(stmt)
            except Exception as e:
                print(f"  WARNING pada statement #{i}: {e}")
                print(f"    Statement: {stmt[:100]}...")

            if i % 100 == 0:
                print(f"    ...{i}/{total}")

        print(f"  Selesai! {total} statements dijalankan.")

    driver.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="Import KG Sirah ke Neo4j")
    parser.add_argument("--source", choices=["v1", "v2", "auto"], default="auto",
                        help="Pilih data source: v1=nodes.csv, v2=nodes_v2.csv (default: auto-detect)")
    parser.add_argument("--uri", help="Neo4j Bolt URI (contoh: bolt://localhost:7687)")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", help="Neo4j password")
    parser.add_argument("--clear", action="store_true", help="Hapus data lama sebelum import")
    args = parser.parse_args()

    print("=" * 60)
    print("IMPORT KG SIRAH NABAWIYAH KE NEO4J")
    print("=" * 60)

    # Source selection
    if args.source == "auto":
        use_v2 = IN_NODES_V2.exists() and IN_EDGES_V2.exists()
    else:
        use_v2 = (args.source == "v2")

    if use_v2:
        nodes_path, edges_path, out_path = IN_NODES_V2, IN_EDGES_V2, OUT_CYPHER_V2
        print("\n  Source: v2 (apply_review_to_kg.py output) + Period nodes")
    else:
        nodes_path, edges_path, out_path = IN_NODES_V1, IN_EDGES_V1, OUT_CYPHER_V1
        print("\n  Source: v1 (raw relation_extraction output, no Period nodes)")

    # 1. Baca data
    print("\n[1/3] Membaca nodes & edges...")
    nodes_df = pd.read_csv(nodes_path, sep=";", encoding="utf-8-sig").fillna("")
    edges_df = pd.read_csv(edges_path, sep=";", encoding="utf-8-sig").fillna("")
    print(f"  Nodes: {len(nodes_df)}")
    print(f"  Edges: {len(edges_df)}")

    periods = None
    if use_v2 and PERIOD_JSON.exists():
        with open(PERIOD_JSON, encoding="utf-8") as f:
            periods = json.load(f)
        print(f"  Periods: {len(periods)}")

    # 2. Generate Cypher
    print("\n[2/3] Generating Cypher...")
    cypher = generate_cypher(nodes_df, edges_df, periods=periods)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(cypher, encoding="utf-8")
    print(f"  Cypher script: {out_path}")

    # 3. Import ke Neo4j (jika ada koneksi)
    if args.uri and args.password:
        print("\n[3/3] Importing ke Neo4j...")
        success = import_via_driver(args.uri, args.user, args.password, cypher, args.clear)
        if not success:
            print("\n  Fallback: gunakan file .cypher di Neo4j Browser")
    else:
        print("\n[3/3] Tidak ada koneksi Neo4j. Untuk import:")
        print(f"  Opsi 1: Copy-paste isi {out_path} ke Neo4j Browser")
        print(f"  Opsi 2: Jalankan ulang dengan --uri dan --password:")
        print(f"    python import_to_neo4j.py --uri bolt://localhost:7687 --password <pw>")

    # Statistik
    print(f"\n{'='*60}")
    print("RINGKASAN")
    print(f"{'='*60}")
    print(f"Nodes: {len(nodes_df)} ({nodes_df['label'].value_counts().to_dict()})")
    print(f"Edges: {len(edges_df)} ({edges_df['relation_type'].value_counts().to_dict()})")

    # Sample Cypher queries untuk eksplorasi
    print(f"\n--- Contoh Query Neo4j ---")
    print("// Lihat semua node:")
    print("MATCH (n) RETURN n LIMIT 50;")
    print("")
    print("// Siapa saja yang terlibat di Perang Badr?")
    print('MATCH (p:Person)-[:INVOLVED_IN]->(e:Event {name: "Perang Badr"}) RETURN p.name;')
    print("")
    print("// Di mana Perang Uhud terjadi?")
    print('MATCH (e:Event {name: "Perang Uhud"})-[:OCCURRED_AT]->(l:Location) RETURN l.name;')
    print("")
    print("// Timeline: event apa saja & kapan?")
    print("MATCH (e:Event)-[:OCCURRED_ON]->(t:Time) RETURN e.name, t.name ORDER BY t.name;")
    print("")
    print("// Tokoh paling banyak terlibat event:")
    print("MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event)")
    print("RETURN p.name, count(e) AS events ORDER BY events DESC LIMIT 20;")
    print("")
    print("// Relasi keluarga:")
    print("MATCH (a:Person)-[r:KELUARGA]->(b:Person)")
    print("RETURN a.name, r.relation_subtype, b.name LIMIT 20;")
    print("")
    print("// Sahabat & sekutu:")
    print("MATCH (a:Person)-[r:SAHABAT]->(b:Person)")
    print("RETURN a.name, r.relation_subtype, b.name LIMIT 20;")
    print("")
    print("// Musuh:")
    print("MATCH (a:Person)-[r:MUSUH]->(b:Person)")
    print("RETURN a.name, b.name LIMIT 20;")
    print("")
    print("// Kronologi event:")
    print("MATCH (a:Event)-[r:PRECEDES]->(b:Event)")
    print("RETURN a.name, b.name ORDER BY r.halaman;")
    print("")
    print("// Relasi dengan weight tinggi:")
    print("MATCH ()-[r]->() WHERE r.weight >= 0.7")
    print("RETURN type(r), startNode(r).name, endNode(r).name, r.weight")
    print("ORDER BY r.weight DESC LIMIT 30;")

    if use_v2:
        print("")
        print("--- Query khusus v2 (Period node) ---")
        print("")
        print("// Lihat semua period berurutan:")
        print('MATCH (p:Period) RETURN p.period_id, p.label, p.phase, p.page_start, p.page_end ORDER BY p.page_start;')
        print("")
        print("// Event apa saja di Period P8 (Perang Badr & Dampaknya):")
        print('MATCH (e:Event)-[:IN_PERIOD]->(p:Period {period_id: "P8"}) RETURN e.name, e.frequency ORDER BY e.frequency DESC;')
        print("")
        print("// Tokoh yang muncul di banyak period (tokoh lintas-zaman):")
        print('MATCH (person:Person)-[:INVOLVED_IN]->(:Event)-[:IN_PERIOD]->(p:Period)')
        print('RETURN person.name, count(DISTINCT p) AS n_periods ORDER BY n_periods DESC LIMIT 20;')
        print("")
        print("// Density per period (jumlah event + jumlah tokoh):")
        print('MATCH (p:Period)<-[:IN_PERIOD]-(e:Event)')
        print('OPTIONAL MATCH (e)<-[:INVOLVED_IN]-(person:Person)')
        print('RETURN p.period_id, p.label, count(DISTINCT e) AS n_events, count(DISTINCT person) AS n_persons')
        print('ORDER BY p.page_start;')


if __name__ == "__main__":
    main()
