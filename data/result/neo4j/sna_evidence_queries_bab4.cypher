// =====================================================================
// QUERY BUKTI SNA — Bab 4 §4.5 (Skenario G1, G3, G4, G6, G7, G8)
// =====================================================================
// Tujuan: mereproduksi BUKTI STRUKTURAL di balik tiap klaim pembahasan
// SNA, langsung dari knowledge graph v4 di Neo4j (import_sirah_v4_hybrid.cypher).
//
// PENTING — batasan kejujuran:
//   * Query di bawah mereproduksi STRUKTUR graf (siapa terhubung ke siapa,
//     daftar peserta, jumlah event/tokoh/fase bersama). Angka struktur ini
//     yang dipakai sebagai bukti di teks.
//   * SKOR sentralitas final (degree centrality 0,7941; betweenness;
//     PageRank) + komunitas Louvain + modularitas Q dihitung di pipeline
//     Python/NetworkX (src/analysis/sna_analysis.py), BUKAN di Cypher.
//     Plain Cypher tidak menghitung betweenness/PageRank/Louvain tanpa
//     pustaka Neo4j GDS. Bagian itu ditandai [PYTHON/GDS] di bawah.
//   * ⚠️ SCOPING: KG utuh di Neo4j berisi 1.177 node (901 Person). Namun
//     analisis sentralitas tokoh (Tabel 4.17-4.19) dihitung pada PROYEKSI
//     ber-scope 137 tokoh peserta peristiwa (tokoh nasab-only dibuang) +
//     filter INVOLVED_IN weight >= 0.3. Karena itu, jumlah tetangga
//     co-participation (mis. derajat Muhammad ~108) dapat direproduksi di
//     Neo4j, tetapi total simpul (137 pada analisis) != count(Person)=901
//     di Neo4j, dan skor centrality persisnya tetap dari Python.
// =====================================================================


// ---------------------------------------------------------------------
// G1 — Sentralitas tokoh: bukti dominasi Nabi Muhammad
// Klaim teks: "degree centrality 0,7941 berarti terhubung ke ~108 dari
//             137 tokoh" (pada graf proyeksi ber-scope).
// Query mengembalikan derajat co-participation Muhammad (filter weight >= 0.3).
// Harapan: tinggi (~108); Muhammad tokoh paling terhubung.
// ---------------------------------------------------------------------
MATCH (m:Person {name: 'Muhammad'})-[r1:INVOLVED_IN]->(:Event)<-[r2:INVOLVED_IN]-(o:Person)
WHERE o <> m AND r1.weight >= 0.3 AND r2.weight >= 0.3
RETURN count(DISTINCT o) AS derajat_co_participation_muhammad;

// (pembanding) total Person pada KG UTUH di Neo4j = 901 (bukan 137).
// Angka 137 adalah subset tokoh peserta peristiwa pada graf analisis (Python).
MATCH (p:Person) RETURN count(p) AS total_person_node_kg_utuh;


// ---------------------------------------------------------------------
// G3 — Komunitas  [PYTHON/GDS]
// Klaim teks: Louvain 8 komunitas, modularitas Q = 0,2831; 2 komunitas
//             terbesar 66 (lingkar Muslim inti) dan 47 (campuran) anggota.
// Louvain + ukuran komunitas dihitung di Python (sna_analysis.py) dan
// disajikan di data/result/analysis/v4_scoped/.
// Plain Cypher tidak bisa. Jika pustaka GDS terpasang, contoh:
//   CALL gds.graph.project('persons','Person',
//       {INVOLVED_IN:{type:'INVOLVED_IN'}});   // perlu proyeksi co-participation
//   CALL gds.louvain.stream('persons') YIELD nodeId, communityId
//   RETURN communityId, count(*) AS ukuran ORDER BY ukuran DESC;
// -> Untuk skripsi, cukup rujuk output Python; tidak perlu dipaksakan Cypher.


// ---------------------------------------------------------------------
// G4 — Sentralitas peristiwa: bukti Perang Badr & Uhud paling terhubung
// Klaim teks: graf antar-peristiwa 35 Event, 264 sisi; Perang Badr salah
//             satu peristiwa paling sentral (PageRank teratas, Tabel 4.20).
// Dua Event terhubung bila berbagi >=1 tokoh (co-participation antar-event).
// Harapan: event_degree_badr tinggi (dari total 35 event).
// ---------------------------------------------------------------------
MATCH (e1:Event {name: 'Perang Badr'})<-[:INVOLVED_IN]-(:Person)-[:INVOLVED_IN]->(e2:Event)
WHERE e1 <> e2
RETURN count(DISTINCT e2) AS event_degree_badr;

// weighted degree (total tokoh-bersama lintas event tetangga) — struktur; skor dari Python
MATCH (e1:Event {name: 'Perang Badr'})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event)
WHERE e1 <> e2
RETURN count(p) AS weighted_degree_badr_kira2;

// bukti caveat: PRECEDES (kronologi) jumlahnya kecil — DATA v4 = 17
MATCH (:Event)-[r:PRECEDES]->(:Event)
RETURN count(r) AS jumlah_precedes;   // 17 (v4_hybrid)

// bukti caveat: Perang Dzul Usyairah frekuensi rendah tapi co-participation tinggi
MATCH (e:Event {name: 'Perang Dzul Usyairah'})
OPTIONAL MATCH (e)<-[:INVOLVED_IN]-(:Person)-[:INVOLVED_IN]->(e2:Event) WHERE e2 <> e
RETURN e.frequency AS frekuensi, count(DISTINCT e2) AS event_degree;


// ---------------------------------------------------------------------
// G6 — Studi kasus: bukti co-participation mencampur DUA KUBU di Perang Badr
// Klaim teks: tokoh Muslim (Ali, Hamzah, Utsman) & Quraisy (Abu Jahal,
//             Abu Lahab, Abu Sufyan) sama-sama INVOLVED_IN Perang Badr.
//             Perang Badr menautkan 44 tokoh (Tabel 4.23).
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
// Klaim teks: graf lokasi LENGKAP 17 node (density 1,0), sehingga tiap
//             lokasi berderajat identik 16 dan betweenness seragam nol;
//             peringkat pakai weighted degree (Madinah teratas).
// ---------------------------------------------------------------------
MATCH (l1:Location {name: 'Madinah'})<-[:OCCURRED_AT]-(:Event)<-[:INVOLVED_IN]-(:Person)
      -[:INVOLVED_IN]->(:Event)-[:OCCURRED_AT]->(l2:Location)
WHERE l1 <> l2
RETURN count(DISTINCT l2) AS degree_lokasi_madinah;   // harapan ~16 (graf lokasi lengkap 17 node)

// weighted degree (total tokoh-bersama) Madinah — harapan ~661 (Tabel 4.21)
MATCH (l1:Location {name: 'Madinah'})<-[:OCCURRED_AT]-(:Event)<-[:INVOLVED_IN]-(p:Person)
      -[:INVOLVED_IN]->(:Event)-[:OCCURRED_AT]->(l2:Location)
WHERE l1 <> l2
RETURN count(*) AS weighted_degree_madinah_kira2;

// bukti keterbatasan alias: Yatsrib terpisah dari Madinah (dua node berbeda, bila ada)
MATCH (l:Location) WHERE l.name IN ['Madinah','Yatsrib'] RETURN l.name;


// ---------------------------------------------------------------------
// G8 — Keterlibatan lintas fase: bukti Muhammad merentang 5 dari 6 fase
// Jalur: Person -INVOLVED_IN-> Event -IN_PERIOD-> Period(.phase).
// Period.phase berisi 6 fase ("Fase I — ...", dst).
// Klaim teks: Muhammad 5 fase/22 event; Umar & Abu Bakar 3 fase;
//             distribusi 124 tokoh (1 fase)/17 (2 fase)/2 (3 fase)/1 (5 fase).
// ---------------------------------------------------------------------
MATCH (p:Person)-[:INVOLVED_IN]->(e:Event)-[:IN_PERIOD]->(per:Period)
RETURN p.name AS tokoh,
       count(DISTINCT per.phase) AS jumlah_fase,
       count(DISTINCT e)         AS jumlah_event
ORDER BY jumlah_fase DESC, jumlah_event DESC
LIMIT 10;

// distribusi: berapa tokoh menyinggahi N fase (harapan 5->1, 3->2, 2->17, 1->124)
MATCH (p:Person)-[:INVOLVED_IN]->(:Event)-[:IN_PERIOD]->(per:Period)
WITH p, count(DISTINCT per.phase) AS nfase
RETURN nfase, count(p) AS jumlah_tokoh
ORDER BY nfase DESC;

// daftar fase yang ada di graf (verifikasi Period.phase)
MATCH (per:Period) RETURN DISTINCT per.phase AS fase ORDER BY fase;
