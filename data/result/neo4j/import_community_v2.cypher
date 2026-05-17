// ============================================================================
// import_community_v2.cypher
// ----------------------------------------------------------------------------
// Tujuan: import hasil community detection + metrik SNA per-Person dari
//         data/result/analysis/sna_metrics.csv ke Neo4j.
//
// Setelah di-run, tiap node Person yang ada di sna_metrics.csv akan punya
// property tambahan: community, pagerank, degree, degree_centrality,
// betweenness_centrality, closeness_centrality.
//
// Lalu di Neo4j Browser bisa visualisasi dengan color by community
// (klik Person node → bawah panel kanan → "Color" → pilih property "community").
//
// ----------------------------------------------------------------------------
// PRE-REQUISITE:
//   1. Sudah jalankan import_sirah_v2.cypher (Person nodes sudah ada).
//   2. File sna_metrics.csv sudah di-copy ke folder import/ Neo4j Desktop.
//      Cara cari folder import/:
//        - Buka Neo4j Desktop → DBMS → klik "..." → "Open folder" → "Import"
//        - Atau ada di: <neo4j-data>/dbmss/dbms-<id>/import/
//      Copy file: data/result/analysis/sna_metrics.csv → import/sna_metrics.csv
//
// CARA RUN:
//   Copy seluruh isi file ini, paste di Neo4j Browser, klik Run.
//   Bisa juga paste per-section satu-satu kalau mau lihat output bertahap.
//
// CATATAN METODOLOGIS:
//   Kolom "community" di CSV adalah hasil sna_analysis.py (Greedy modularity,
//   Q ≈ 0.32). Untuk perbandingan dengan Louvain proper (Q=0.3269), lihat
//   graph_metrics_v2.md hasil dari sna_graph_metrics.py. Untuk visualisasi
//   demo Neo4j, Greedy result sudah cukup karena partisi mirip (ARI 0.56).
// ============================================================================


// ============================================================================
// STEP 1 — Load community + metrik SNA per-Person
// ============================================================================
LOAD CSV WITH HEADERS FROM 'file:///sna_metrics.csv' AS row
FIELDTERMINATOR ';'
MATCH (p:Person {name: row.name})
SET p.community              = toInteger(row.community),
    p.pagerank               = toFloat(row.pagerank),
    p.degree                 = toInteger(row.degree),
    p.degree_centrality      = toFloat(row.degree_centrality),
    p.betweenness_centrality = toFloat(row.betweenness_centrality),
    p.closeness_centrality   = toFloat(row.closeness_centrality);


// ============================================================================
// STEP 2 — Verifikasi: berapa Person ter-update?
// ============================================================================
MATCH (p:Person)
RETURN
  count(p)                                       AS total_person,
  sum(CASE WHEN p.community IS NOT NULL THEN 1 ELSE 0 END) AS ada_community,
  sum(CASE WHEN p.community IS NULL     THEN 1 ELSE 0 END) AS tanpa_community;
// Harapan: ada_community = 174 (jumlah Person di sna_metrics.csv),
//          tanpa_community = sisa Person yang isolated / tidak ada di SNA graph.


// ============================================================================
// STEP 3 — Distribusi komunitas (sesuai sna_metrics.csv)
// ============================================================================
MATCH (p:Person) WHERE p.community IS NOT NULL
RETURN
  p.community AS community_id,
  count(p)    AS n_person
ORDER BY n_person DESC;
// Harapan (16 komunitas, total 174 Person):
//   C0: 74, C1: 39, C2: 26, C3: 6, C4: 4, C5-7: 3 each, C8-15: 2 each


// ============================================================================
// STEP 4 — Anggota tiap komunitas besar (top-3, dengan tokoh utama)
// ============================================================================
MATCH (p:Person) WHERE p.community IS NOT NULL
WITH p.community AS community_id, collect(p.name) AS members, count(p) AS size
WHERE size >= 6
RETURN community_id, size, members[..10] AS contoh_anggota_top10
ORDER BY size DESC;
// Harapan: C0 (74 orang) berisi tokoh Yatsrib + tokoh general,
//          C1 (39) berisi Quraisy oposisi (Abu Jahal, Abu Sufyan, dst.),
//          C2 (26) berisi sahabat & keluarga Nabi.


// ============================================================================
// STEP 5 — Visualisasi sub-graf community besar (untuk demo Bu Diana)
// ============================================================================
// 5A. Tampilkan top-3 community + relasi internal antar anggotanya
MATCH (p:Person)-[r]-(p2:Person)
WHERE p.community IS NOT NULL
  AND p.community = p2.community
  AND p.community IN [0, 1, 2]
RETURN p, r, p2;

// 5B. Tampilkan Muhammad + tetangganya (lintas komunitas, jadi terlihat
//     fungsi Muhammad sebagai bridge antar komunitas)
MATCH (m:Person {name: "Muhammad"})-[r]-(p:Person)
RETURN m, r, p
LIMIT 100;


// ============================================================================
// STEP 6 — Tip warna di Neo4j Browser
// ============================================================================
// Setelah STEP 1 selesai, di Neo4j Browser:
//   1. Klik salah satu node Person di canvas
//   2. Di panel kanan, klik label "Person" (di atas, warna biru)
//   3. Di section "Color" → pilih property "community"
//   4. Neo4j otomatis assign warna berbeda per community
//
// Atau via setting: klik tombol gear (Browser settings) →
// "Connect result nodes" diaktifkan biar relasi terlihat saat
// visualize subset.


// ============================================================================
// STEP 7 — Query bonus: tokoh paling penting per komunitas (PageRank)
// ============================================================================
MATCH (p:Person) WHERE p.community IS NOT NULL AND p.pagerank IS NOT NULL
WITH p.community AS community_id, p
ORDER BY p.pagerank DESC
WITH community_id, collect({name: p.name, pagerank: p.pagerank})[..3] AS top3
RETURN community_id, top3
ORDER BY community_id;
// Output: 3 tokoh dengan PageRank tertinggi per komunitas — bisa di-narasikan
// sebagai "leader" di tiap kelompok.
