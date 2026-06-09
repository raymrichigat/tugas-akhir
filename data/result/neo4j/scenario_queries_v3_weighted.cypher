// =============================================================================
// Knowledge Graph Sirah Nabawiyah v3 — QUERY HASIL SKENARIO (G1–G8), WEIGHTED
// =============================================================================
// Tujuan: menampilkan SELURUH hasil skenario graf (G1–G8) di Neo4j Browser,
//         KONSISTEN dengan angka presentasi 2026-06-04 (graf Person *weighted*).
//
// Prinsip weighted (lihat docs/bimbingan/2026-06-04.md A.1.3):
//   - Relasi INVOLVED_IN lemah (weight < 0.3 = co-mention jauh / di luar BAB
//     utama event) DIBUANG saat analisis → di query ini ditiru dengan
//     `WHERE r.weight >= 0.3`.
//   - Ini meniru filter yang sama yang dipakai sna_analysis.py, sehingga
//     tampilan Neo4j konsisten dengan tabel SNA (mis. Amr Bin Umayyah TIDAK
//     lagi tampak sentral).
//
// PENTING — dari mana angka berasal:
//   - PageRank / Betweenness / Closeness / Community = dihitung di PYTHON
//     (sna_analysis.py, graf weighted) lalu DIMUAT sebagai properti node
//     (Bagian 0). Neo4j Community Edition (tanpa GDS) tidak menghitung ulang.
//   - Degree / jumlah peserta / keberagaman fase = dihitung LIVE di Cypher
//     dengan filter weight >= 0.3.
//   - density / transitivity / modularity Q = dari Python (graph_metrics_v2.md);
//     ditulis sebagai referensi di komentar (tidak bisa native tanpa GDS).
//
// TIDAK perlu re-import KG. import_sirah_v3.cypher tetap dipakai apa adanya.
// =============================================================================


// ┌───────────────────────────────────────────────────────────────────────┐
// │ BAGIAN 0 — PRASYARAT: muat hasil SNA weighted sebagai properti node     │
// └───────────────────────────────────────────────────────────────────────┘
// Langkah:
//   1. Copy `data/result/analysis/v3/sna_metrics.csv` ke folder import Neo4j
//      (Neo4j Desktop: tombol "..." DBMS → Open folder → Import), rename jadi
//      `sna_metrics_v3.csv`.
//   2. Jalankan blok di bawah SEKALI. Ini menempel pagerank/betweenness/
//      closeness/community (hasil graf weighted) ke node Person.
//   3. Person yang ter-drop oleh threshold tidak ada di CSV → propertinya null
//      (memang sengaja: mereka keluar dari graf analisis).

LOAD CSV WITH HEADERS FROM 'file:///sna_metrics_v3.csv' AS row
FIELDTERMINATOR ';'
MATCH (p:Person {name: row.name})
SET p.pagerank    = toFloat(row.pagerank),
    p.betweenness = toFloat(row.betweenness_centrality),
    p.closeness   = toFloat(row.closeness_centrality),
    p.degree_cent = toFloat(row.degree_centrality),
    p.degree_sna  = toInteger(row.degree),
    p.community   = toInteger(row.community);


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G1 — TOKOH PALING SENTRAL (Top-10 PageRank, weighted)                   │
// └───────────────────────────────────────────────────────────────────────┘
// Referensi (graf weighted): Muhammad 0.0565 > Ali 0.0224 > Abu Bakar 0.0206
//   > Aisyah 0.0195 > Abu Jahal 0.0189 > Umar 0.0168 > Abu Sufyan 0.0153
//   > Utsman 0.0138 > Abu Azzah 0.0130 > Khadijah 0.0118
// Catatan: Amr Bin Umayyah (#4 di graf naif) turun ke #18 → tidak di top-10.

// G1.a — Tabel Top-10
MATCH (p:Person) WHERE p.pagerank IS NOT NULL
RETURN p.name                              AS tokoh,
       round(p.pagerank   * 10000) / 10000.0 AS pagerank,
       p.degree_sna                        AS degree,
       round(p.degree_cent  * 10000) / 10000.0 AS degree_centrality,
       round(p.betweenness * 10000) / 10000.0 AS betweenness,
       p.community                         AS komunitas
ORDER BY p.pagerank DESC
LIMIT 10;

// G1.b — Visual: ego-network 5 tokoh teratas (ukuran node ∝ pagerank di Browser)
MATCH (p:Person) WHERE p.pagerank IS NOT NULL
WITH p ORDER BY p.pagerank DESC LIMIT 5
MATCH (p)-[r:INVOLVED_IN]->(e:Event) WHERE r.weight >= 0.3
RETURN p, r, e
LIMIT 200;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G2 — TOKOH JEMBATAN ANTAR-KELOMPOK (Top-10 Betweenness, weighted)       │
// └───────────────────────────────────────────────────────────────────────┘
// Referensi: Muhammad 0.357 > Utsman 0.104 > Abu Jahal 0.071 > Ali 0.068
//   > Hamzah 0.065 > Ka'b bin Malik 0.053 > Abu Sa'id 0.053 > Al-Barra' 0.052
//   > Khadijah 0.035 > Ibrahim 0.027

MATCH (p:Person) WHERE p.betweenness IS NOT NULL
RETURN p.name                                AS tokoh,
       round(p.betweenness * 10000) / 10000.0 AS betweenness,
       p.degree_sna                          AS degree,
       round(p.pagerank    * 10000) / 10000.0 AS pagerank
ORDER BY p.betweenness DESC
LIMIT 10;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G3 — KOMUNITAS TOKOH (Louvain/Greedy, weighted)                         │
// └───────────────────────────────────────────────────────────────────────┘
// Referensi (graf weighted): Louvain Q=0.385 (15 komunitas);
//   ARI(Louvain,Greedy)=0.78. Greedy (kolom community) 4 terbesar ≈ 64/45/41/21.

// G3.a — Ukuran tiap komunitas + tokoh PR teratasnya
// (urut di WITH dulu agar collect mempertahankan urutan → kompatibel Neo4j 4.x & 5.x)
MATCH (p:Person) WHERE p.community IS NOT NULL
WITH p ORDER BY p.pagerank DESC
RETURN p.community            AS komunitas,
       count(*)               AS anggota,
       collect(p.name)[0..5]  AS tokoh_utama
ORDER BY anggota DESC;

// G3.b — Visual semua komunitas (di Browser: color node by property `community`)
MATCH (p:Person) WHERE p.community IS NOT NULL
OPTIONAL MATCH (p)-[r:INVOLVED_IN]->(e:Event) WHERE r.weight >= 0.3
RETURN p, r, e
LIMIT 400;

// G3.c — Satu komunitas saja (ganti angka 0 → 1/2/3 sesuai G3.a)
MATCH (p:Person {community: 0})
OPTIONAL MATCH (p)-[r:INVOLVED_IN]->(e:Event) WHERE r.weight >= 0.3
RETURN p, r, e
LIMIT 200;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G4 — PERISTIWA PALING SENTRAL (Event)                                   │
// └───────────────────────────────────────────────────────────────────────┘
// CATATAN JUJUR: graf Event BELUM di-weight (scope = graf Person). PageRank
// event tetap count-based: Perang Badr 0.077 > Uhud 0.070 > Khandaq 0.051
// > Hijrah Ke Madinah 0.049 > Kelahiran Nabi 0.041 ... (event_centrality_summary.md).
// Query di bawah menampilkan proksi LIVE = jumlah peserta (weight>=0.3) per event.

MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event) WHERE r.weight >= 0.3
RETURN e.name              AS peristiwa,
       count(DISTINCT p)   AS n_peserta_kuat,
       e.periode_bab       AS periode
ORDER BY n_peserta_kuat DESC
LIMIT 10;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G5 — STRUKTUR JARINGAN KESELURUHAN (graph-level)                        │
// └───────────────────────────────────────────────────────────────────────┘
// Referensi graf Person weighted (graph_metrics_v2.md, v3):
//   208 node / 1832 edge · density 0.0851 · transitivity 0.7624
//   avg clustering 0.4787 · components 8 · giant 192 (92.3%)
//   diameter 7 · avg path 2.53 · assortativity -0.027
// (density/transitivity/path butuh GDS untuk native — lihat Appendix.)

// G5.a — Jumlah node per label (KG penuh)
MATCH (n)
RETURN labels(n)[0] AS label, count(*) AS jumlah
ORDER BY jumlah DESC;

// G5.b — Jumlah relasi per tipe (KG penuh) + rata-rata weight
MATCH ()-[r]->()
RETURN type(r) AS relasi, count(*) AS jumlah,
       round(avg(r.weight) * 1000) / 1000.0 AS avg_weight
ORDER BY jumlah DESC;

// G5.c — Efek threshold: berapa INVOLVED_IN tersisa setelah filter weight>=0.3
MATCH ()-[r:INVOLVED_IN]->()
RETURN sum(CASE WHEN r.weight >= 0.3 THEN 1 ELSE 0 END) AS lolos_threshold,
       sum(CASE WHEN r.weight <  0.3 THEN 1 ELSE 0 END) AS dibuang,
       count(*)                                         AS total;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G6 — STUDI KASUS 5 EVENT (sub-graph, weighted)                          │
// └───────────────────────────────────────────────────────────────────────┘
// Hanya peserta dengan weight >= 0.3 yang tampil → clique Badr/Uhud lebih
// ramping & jujur (tidak ada peserta co-mention palsu).

// G6.a — Perang Badr
MATCH (e:Event {name: "Perang Badr"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person) WHERE r1.weight >= 0.3
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:OCCURRED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 150;

// G6.b — Perang Uhud
MATCH (e:Event {name: "Perang Uhud"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person) WHERE r1.weight >= 0.3
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:OCCURRED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 150;

// G6.c — Perjanjian Hudaibiyah
MATCH (e:Event {name: "Perjanjian Hudaibiyah"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person) WHERE r1.weight >= 0.3
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:OCCURRED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 150;

// G6.d — Perang Khaibar
MATCH (e:Event {name: "Perang Khaibar"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person) WHERE r1.weight >= 0.3
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:OCCURRED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 150;

// G6.e — Perang Tabuk
MATCH (e:Event {name: "Perang Tabuk"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person) WHERE r1.weight >= 0.3
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:OCCURRED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 150;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G7 — LOKASI DENGAN PERAN SENTRAL                                        │
// └───────────────────────────────────────────────────────────────────────┘
// CATATAN JUJUR: angka weighted_degree resmi (Madinah 684 > Makkah 595 >
// Habasyah 505) dari scenario_g7_g8.py (graf lokasi, BELUM di-weight ulang).
// Query di bawah = proksi LIVE: lokasi diurut berdasarkan jumlah event yang
// terjadi di sana + jumlah tokoh "kuat" yang menjangkau lokasi itu.

MATCH (loc:Location)<-[:OCCURRED_AT]-(e:Event)
OPTIONAL MATCH (e)<-[r:INVOLVED_IN]-(p:Person) WHERE r.weight >= 0.3
RETURN loc.name            AS lokasi,
       count(DISTINCT e)   AS n_event,
       count(DISTINCT p)   AS n_tokoh_kuat
ORDER BY n_tokoh_kuat DESC, n_event DESC
LIMIT 10;


// ┌───────────────────────────────────────────────────────────────────────┐
// │ G8 — KEBERAGAMAN FASE KETERLIBATAN TOKOH                                │
// └───────────────────────────────────────────────────────────────────────┘
// Referensi: Muhammad hadir di 6/6 fase; Ali 8 event tapi cuma 2 fase
// (scenario_g7_g8.py, pakai 6 fase). Query di bawah memakai PERIODE (15 period)
// sebagai granularitas — angkanya beda granularitas dgn "fase", tapi konsep sama:
// tokoh yang tersebar di banyak periode = jangkauan naratif luas.

MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event)-[:IN_PERIOD]->(per:Period)
WHERE r.weight >= 0.3
RETURN p.name                  AS tokoh,
       count(DISTINCT per)     AS n_periode,
       count(DISTINCT e)       AS n_event
ORDER BY n_periode DESC, n_event DESC
LIMIT 15;


// =============================================================================
// APPENDIX (OPSIONAL) — Hitung ulang metrik NATIVE di Neo4j dengan GDS
// =============================================================================
// HANYA jika plugin Graph Data Science (GDS) terpasang. Ini memproyeksikan
// graf co-participation WEIGHTED langsung di Neo4j lalu menghitung PageRank/
// Louvain/Betweenness sendiri. Hasilnya bisa SEDIKIT BEDA dari Python (beda
// implementasi & normalisasi) — angka acuan presentasi tetap dari Python.
//
// A1 — Proyeksikan graf Person co-participation (weight>=0.3) via Cypher projection
//   CALL gds.graph.project.cypher(
//     'person_copart_w',
//     'MATCH (p:Person) WHERE p.pagerank IS NOT NULL RETURN id(p) AS id',
//     'MATCH (p1:Person)-[r1:INVOLVED_IN]->(e:Event)<-[r2:INVOLVED_IN]-(p2:Person)
//      WHERE r1.weight >= 0.3 AND r2.weight >= 0.3 AND id(p1) < id(p2)
//      RETURN id(p1) AS source, id(p2) AS target,
//             count(DISTINCT e) AS weight'
//   );
//
// A2 — PageRank weighted
//   CALL gds.pageRank.stream('person_copart_w', {relationshipWeightProperty: 'weight'})
//   YIELD nodeId, score
//   RETURN gds.util.asNode(nodeId).name AS tokoh, score
//   ORDER BY score DESC LIMIT 10;
//
// A3 — Louvain (komunitas) + modularity
//   CALL gds.louvain.stream('person_copart_w', {relationshipWeightProperty: 'weight'})
//   YIELD nodeId, communityId
//   RETURN communityId, count(*) AS anggota
//   ORDER BY anggota DESC;
//
// A4 — Bersihkan proyeksi setelah selesai
//   CALL gds.graph.drop('person_copart_w');
// =============================================================================
