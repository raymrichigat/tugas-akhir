// =====================================================================
// QUERY BUKTI SNA — Bab 4 §4.4.1 (Skenario G1, G3, G4, G6, G7, G8)
// =====================================================================
// Tujuan: mereproduksi BUKTI STRUKTURAL di balik tiap klaim pembahasan
// SNA, langsung dari knowledge graph v3 di Neo4j (import_sirah_v3.cypher).
//
// PENTING — batasan kejujuran:
//   * Query di bawah mereproduksi STRUKTUR graf (siapa terhubung ke siapa,
//     daftar peserta, jumlah event/tokoh/fase bersama). Angka ini yang
//     dipakai sebagai bukti di teks.
//   * SKOR sentralitas final (degree centrality 0,5894; betweenness;
//     PageRank) + komunitas Louvain + modularitas Q dihitung di pipeline
//     Python/NetworkX (src/analysis/sna_analysis.py), BUKAN di Cypher.
//     Plain Cypher tidak menghitung betweenness/PageRank/Louvain tanpa
//     pustaka Neo4j GDS. Bagian itu ditandai [PYTHON/GDS] di bawah.
//   * Graf proyeksi tokoh memakai filter INVOLVED_IN weight >= 0.3
//     (WEIGHT_THRESHOLD di sna_analysis.py). Filter ini disertakan agar
//     hitungan cocok dengan tabel; tanpa filter -> angka lebih besar.
// =====================================================================


// ---------------------------------------------------------------------
// G1 — Sentralitas tokoh: bukti dominasi Nabi Muhammad
// Klaim teks: "degree centrality 0,5894 berarti terhubung ke ~122 dari
//             208 tokoh". Query mengembalikan derajat co-participation
//             Muhammad pada graf proyeksi tokoh (filter weight >= 0.3).
// Harapan: ~122.
// ---------------------------------------------------------------------
MATCH (m:Person {name: 'Muhammad'})-[r1:INVOLVED_IN]->(:Event)<-[r2:INVOLVED_IN]-(o:Person)
WHERE o <> m AND r1.weight >= 0.3 AND r2.weight >= 0.3
RETURN count(DISTINCT o) AS derajat_co_participation_muhammad;

// (pembanding) total tokoh pada graf = 208
MATCH (p:Person) RETURN count(p) AS total_person_node;


// ---------------------------------------------------------------------
// G3 — Komunitas  [PYTHON/GDS]
// Klaim teks: 4 komunitas terbesar (64/45/41/21 anggota) + token dominan.
// Louvain + ukuran komunitas dihitung di Python (sna_analysis.py) dan
// disajikan di data/result/analysis/v3/community_wordclouds_summary.md.
// Plain Cypher tidak bisa. Jika pustaka GDS terpasang, contoh:
//   CALL gds.graph.project('persons','Person',
//       {INVOLVED_IN:{type:'INVOLVED_IN'}});   // perlu proyeksi co-participation
//   CALL gds.louvain.stream('persons') YIELD nodeId, communityId
//   RETURN communityId, count(*) AS ukuran ORDER BY ukuran DESC;
// -> Untuk skripsi, cukup rujuk output Python; tidak perlu dipaksakan Cypher.


// ---------------------------------------------------------------------
// G4 — Sentralitas peristiwa: bukti Perang Badr & Uhud paling terhubung
// Klaim teks: "Perang Badr terhubung ke 33 dari 45 peristiwa lain".
// Dua Event terhubung bila berbagi >=1 tokoh (co-participation antar-event).
// Harapan: event_degree_badr ~33 (struktur; skor PageRank dari Python).
// ---------------------------------------------------------------------
MATCH (e1:Event {name: 'Perang Badr'})<-[:INVOLVED_IN]-(:Person)-[:INVOLVED_IN]->(e2:Event)
WHERE e1 <> e2
RETURN count(DISTINCT e2) AS event_degree_badr;

// weighted degree (total tokoh-bersama lintas event tetangga) — harapan ~80
MATCH (e1:Event {name: 'Perang Badr'})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event)
WHERE e1 <> e2
RETURN count(p) AS weighted_degree_badr_kira2;

// bukti caveat: PRECEDES (kronologi) jumlahnya kecil — DATA TERBARU = 23
MATCH (:Event)-[r:PRECEDES]->(:Event)
RETURN count(r) AS jumlah_precedes;   // 23 (bukan 12 yang usang)

// bukti caveat: Perang Dzul Usyairah frekuensi 1 tapi co-participation tinggi
MATCH (e:Event {name: 'Perang Dzul Usyairah'})
OPTIONAL MATCH (e)<-[:INVOLVED_IN]-(:Person)-[:INVOLVED_IN]->(e2:Event) WHERE e2 <> e
RETURN e.frequency AS frekuensi, count(DISTINCT e2) AS event_degree;


// ---------------------------------------------------------------------
// G6 — Studi kasus: bukti co-participation mencampur DUA KUBU di Perang Badr
// Klaim teks: tokoh Muslim (Ali, Hamzah, Utsman) & Quraisy (Abu Jahal,
//             Abu Lahab, Abu Sufyan) sama-sama INVOLVED_IN Perang Badr.
// ---------------------------------------------------------------------
MATCH (p:Person)-[:INVOLVED_IN]->(:Event {name: 'Perang Badr'})
RETURN p.name AS peserta_perang_badr
ORDER BY p.name;

// fokus ke enam nama yang dikutip di teks
MATCH (p:Person)-[:INVOLVED_IN]->(:Event {name: 'Perang Badr'})
WHERE p.name IN ['Ali bin Abu Thalib','Hamzah bin Abdul Muththalib','Utsman bin Affan',
                 'Abu Jahal','Abu Lahab','Abu Sufyan bin Harb']
RETURN p.name AS terkonfirmasi ORDER BY p.name;


// ---------------------------------------------------------------------
// G7 — Peran lokasi: bukti Madinah dominan & betweenness tak diskriminatif
// Dua Location terhubung bila ada tokoh yang terlibat di peristiwa pada
// KEDUA lokasi. Query memberi derajat lokasi (jumlah lokasi tetangga).
// Klaim teks: Madinah, Makkah, dll. punya degree identik 34.
// ---------------------------------------------------------------------
MATCH (l1:Location {name: 'Madinah'})<-[:OCCURRED_AT]-(:Event)<-[:INVOLVED_IN]-(:Person)
      -[:INVOLVED_IN]->(:Event)-[:OCCURRED_AT]->(l2:Location)
WHERE l1 <> l2
RETURN count(DISTINCT l2) AS degree_lokasi_madinah;   // harapan ~34

// weighted degree (total tokoh-bersama) Madinah — harapan ~684
MATCH (l1:Location {name: 'Madinah'})<-[:OCCURRED_AT]-(:Event)<-[:INVOLVED_IN]-(p:Person)
      -[:INVOLVED_IN]->(:Event)-[:OCCURRED_AT]->(l2:Location)
WHERE l1 <> l2
RETURN count(*) AS weighted_degree_madinah_kira2;

// bukti keterbatasan alias: Yatsrib terpisah dari Madinah (dua node berbeda)
MATCH (l:Location) WHERE l.name IN ['Madinah','Yatsrib'] RETURN l.name;


// ---------------------------------------------------------------------
// G8 — Keterlibatan lintas fase: bukti Muhammad merentang 6 fase
// Jalur: Person -INVOLVED_IN-> Event -IN_PERIOD-> Period(.phase).
// Period.phase berisi 6 fase ("Fase I — ...", dst).
// Klaim teks: Muhammad 6 fase/25 event; Abu Bakar 4/6; Aisyah 4/5;
//             distribusi 120/25/2/2/1.
// ---------------------------------------------------------------------
MATCH (p:Person)-[:INVOLVED_IN]->(e:Event)-[:IN_PERIOD]->(per:Period)
RETURN p.name AS tokoh,
       count(DISTINCT per.phase) AS jumlah_fase,
       count(DISTINCT e)         AS jumlah_event
ORDER BY jumlah_fase DESC, jumlah_event DESC
LIMIT 10;

// distribusi: berapa tokoh menyinggahi N fase (harapan 6->1, 4->2, 3->2, 2->25, 1->120)
MATCH (p:Person)-[:INVOLVED_IN]->(:Event)-[:IN_PERIOD]->(per:Period)
WITH p, count(DISTINCT per.phase) AS nfase
RETURN nfase, count(p) AS jumlah_tokoh
ORDER BY nfase DESC;

// daftar 6 fase yang ada di graf (verifikasi Period.phase)
MATCH (per:Period) RETURN DISTINCT per.phase AS fase ORDER BY fase;
