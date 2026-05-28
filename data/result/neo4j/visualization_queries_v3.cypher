// ============================================================
// Knowledge Graph Sirah Nabawiyah v3 — Visualisasi Queries
// ============================================================
// Queries siap di-paste ke Neo4j Browser setelah import_sirah_v3.cypher
// ter-load. Setiap query menghasilkan sub-graph yang siap di-screenshot
// untuk slide bimbingan / Bab 4 TA.
//
// Cara pakai:
//   1. Jalankan import_sirah_v3.cypher (one-shot)
//   2. Copy-paste query Q1-Q12 di bawah satu per satu
//   3. Di Neo4j Browser: klik node → atur color/size by property
//   4. Export: Export → PNG (full-graph) atau SVG
// ============================================================


// ┌───────────────────────────────────────────────────────────┐
// │ A. PER-PERIOD SUB-GRAPHS (15 period total, 6 phase)       │
// └───────────────────────────────────────────────────────────┘

// Q1 — Periode P8 (Perang Badr & Dampaknya)
// Visualisasi semua entitas yang muncul di period P8 + relasinya.
MATCH (p:Period {period_id: "P8"})<-[:IN_PERIOD]-(e:Event)
MATCH path = (e)-[r]-(other)
WHERE NOT other:Period
RETURN p, e, r, other
LIMIT 200;


// Q2 — Periode P9 (Perang Uhud & Pasca Uhud)
MATCH (p:Period {period_id: "P9"})<-[:IN_PERIOD]-(e:Event)
MATCH path = (e)-[r]-(other)
WHERE NOT other:Period
RETURN p, e, r, other
LIMIT 200;


// Q3 — Periode P11 (Hudaibiyah & Diplomasi)
MATCH (p:Period {period_id: "P11"})<-[:IN_PERIOD]-(e:Event)
MATCH path = (e)-[r]-(other)
WHERE NOT other:Period
RETURN p, e, r, other
LIMIT 200;


// Q4 — Semua Period nodes + Event-IN_PERIOD (chronology overview)
// Untuk slide overview struktur temporal Sirah.
MATCH (p:Period)<-[r:IN_PERIOD]-(e:Event)
RETURN p, r, e
ORDER BY p.period_id;


// ┌───────────────────────────────────────────────────────────┐
// │ B. CASE STUDY 5 EVENT PILIHAN (Bu Diana request)          │
// └───────────────────────────────────────────────────────────┘

// Q5 — Perang Badr (top PR Event = 0.0816)
// Tampilkan semua Person yang INVOLVED_IN, Location/Time terkait, Period.
MATCH (e:Event {name: "Perang Badr"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:HAPPENED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
OPTIONAL MATCH (e)-[r5:PRECEDES]-(e2:Event)
RETURN e, r1, p, r2, loc, r3, t, r4, per, r5, e2
LIMIT 100;


// Q6 — Perang Uhud (PR=0.0692)
MATCH (e:Event {name: "Perang Uhud"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:HAPPENED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
OPTIONAL MATCH (e)-[r5:PRECEDES]-(e2:Event)
RETURN e, r1, p, r2, loc, r3, t, r4, per, r5, e2
LIMIT 100;


// Q7 — Perang Khaibar (PR=0.0368)
MATCH (e:Event {name: "Perang Khaibar"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:HAPPENED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 100;


// Q8 — Perjanjian Hudaibiyah (PR=0.0331)
MATCH (e:Event {name: "Perjanjian Hudaibiyah"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:HAPPENED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 100;


// Q9 — Perang Tabuk (PR=0.0322 di top 10 event v3)
MATCH (e:Event {name: "Perang Tabuk"})
OPTIONAL MATCH (e)<-[r1:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (e)-[r2:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[r3:HAPPENED_ON]->(t:Time)
OPTIONAL MATCH (e)-[r4:IN_PERIOD]->(per:Period)
RETURN e, r1, p, r2, loc, r3, t, r4, per
LIMIT 100;


// ┌───────────────────────────────────────────────────────────┐
// │ C. PER-COMMUNITY SUB-GRAPHS (Louvain dari sna_metrics)    │
// │   3 community besar di v3: 89, 61, 57 anggota             │
// └───────────────────────────────────────────────────────────┘

// PRE-REQUISITE: import community_id ke Neo4j sebagai property
// Jalankan dulu untuk attach community label dari sna_metrics.csv:
//
//   LOAD CSV WITH HEADERS FROM 'file:///sna_metrics.csv' AS row
//   FIELDTERMINATOR ';'
//   MATCH (p:Person {name: row.name})
//   SET p.community = toInteger(row.community), p.pagerank = toFloat(row.pagerank);
//
// (Copy sna_metrics.csv v3 ke import dir Neo4j dulu)

// Q10 — Komunitas 0 (komunitas terbesar Greedy = 89 anggota)
MATCH (p:Person {community: 0})
OPTIONAL MATCH (p)-[r:INVOLVED_IN]->(e:Event)
RETURN p, r, e
LIMIT 200;


// Q11 — Komunitas 1 (61 anggota)
MATCH (p:Person {community: 1})
OPTIONAL MATCH (p)-[r:INVOLVED_IN]->(e:Event)
RETURN p, r, e
LIMIT 200;


// Q12 — Komunitas 2 (57 anggota)
MATCH (p:Person {community: 2})
OPTIONAL MATCH (p)-[r:INVOLVED_IN]->(e:Event)
RETURN p, r, e
LIMIT 200;


// ┌───────────────────────────────────────────────────────────┐
// │ D. EGO-NETWORK TOKOH KUNCI                                │
// └───────────────────────────────────────────────────────────┘

// Q13 — Ego-network Muhammad (rank #1 PR)
// Hop 1: KELUARGA, SAHABAT, MUSUH langsung + Event INVOLVED_IN.
MATCH (n:Person {name: "Muhammad"})
OPTIONAL MATCH (n)-[r1:KELUARGA|SAHABAT|MUSUH]-(p:Person)
OPTIONAL MATCH (n)-[r2:INVOLVED_IN]->(e:Event)
RETURN n, r1, p, r2, e
LIMIT 150;


// Q14 — Ego-network Abu Bakar
MATCH (n:Person {name: "Abu Bakar"})
OPTIONAL MATCH (n)-[r1:KELUARGA|SAHABAT|MUSUH]-(p:Person)
OPTIONAL MATCH (n)-[r2:INVOLVED_IN]->(e:Event)
RETURN n, r1, p, r2, e
LIMIT 100;


// Q15 — Ego-network Abu Sufyan (musuh utama Quraisy)
MATCH (n:Person {name: "Abu Sufyan bin Harb"})
OPTIONAL MATCH (n)-[r1:KELUARGA|SAHABAT|MUSUH]-(p:Person)
OPTIONAL MATCH (n)-[r2:INVOLVED_IN]->(e:Event)
RETURN n, r1, p, r2, e
LIMIT 100;


// ┌───────────────────────────────────────────────────────────┐
// │ E. PRECEDES CHAIN (kronologi event)                       │
// └───────────────────────────────────────────────────────────┘

// Q16 — Semua PRECEDES edges + Period (untuk validasi urutan kronologis)
MATCH (e1:Event)-[r:PRECEDES]->(e2:Event)
OPTIONAL MATCH (e1)-[:IN_PERIOD]->(p1:Period)
OPTIONAL MATCH (e2)-[:IN_PERIOD]->(p2:Period)
RETURN e1, r, e2, p1, p2;


// ┌───────────────────────────────────────────────────────────┐
// │ F. STATISTIK DESCRIPTIVE (untuk slide angka)              │
// └───────────────────────────────────────────────────────────┘

// Q17 — Count semua node per label
MATCH (n)
RETURN labels(n) AS labels, count(n) AS cnt
ORDER BY cnt DESC;

// Q18 — Count semua relasi per type
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(r) AS cnt
ORDER BY cnt DESC;

// Q19 — Top 10 Person dengan paling banyak INVOLVED_IN
MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event)
RETURN p.name AS person, count(e) AS n_events
ORDER BY n_events DESC
LIMIT 10;

// Q20 — Top 10 Event dengan paling banyak Person INVOLVED_IN
MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event)
RETURN e.name AS event, count(p) AS n_persons
ORDER BY n_persons DESC
LIMIT 10;
