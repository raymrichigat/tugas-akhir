# Cypher Queries untuk Visualisasi Studi Kasus di Neo4j

Setelah import `import_sirah_v2.cypher`, copy-paste query di bawah ke Neo4j Browser
untuk visualisasi tiap event.

// === Perang Badr ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {name: "Perang Badr"})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {name: "Perang Badr"})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {name: "Perang Badr"})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {name: "Perang Badr"})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {name: "Perang Uhud"})
RETURN p.name;


// === Perang Uhud ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {name: "Perang Uhud"})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {name: "Perang Uhud"})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {name: "Perang Uhud"})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {name: "Perang Uhud"})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {name: "Perang Uhud"})
RETURN p.name;


// === Perjanjian Hudaibiyah ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {name: "Perjanjian Hudaibiyah"})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {name: "Perjanjian Hudaibiyah"})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {name: "Perjanjian Hudaibiyah"})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {name: "Perjanjian Hudaibiyah"})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {name: "Perang Uhud"})
RETURN p.name;


// === Perang Khaibar ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {name: "Perang Khaibar"})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {name: "Perang Khaibar"})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {name: "Perang Khaibar"})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {name: "Perang Khaibar"})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {name: "Perang Uhud"})
RETURN p.name;


// === Perang Tabuk ===

// 1. Sub-graph lengkap: event + semua Person/Location/Time terkait
MATCH (e:Event {name: "Perang Tabuk"})
OPTIONAL MATCH (p:Person)-[:INVOLVED_IN]->(e)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(loc:Location)
OPTIONAL MATCH (e)-[:OCCURRED_ON]->(t:Time)
RETURN e, p, loc, t;

// 2. Tokoh paling sentral di event (paling banyak relasi Person-Person)
MATCH (e:Event {name: "Perang Tabuk"})<-[:INVOLVED_IN]-(p:Person)
OPTIONAL MATCH (p)-[r:KELUARGA|SAHABAT|MUSUH]-(other:Person)
RETURN p.name, count(DISTINCT other) AS n_relations
ORDER BY n_relations DESC LIMIT 5;

// 3. Event ini berada di period mana + event lain di period sama
MATCH (e:Event {name: "Perang Tabuk"})-[:IN_PERIOD]->(period:Period)
OPTIONAL MATCH (other:Event)-[:IN_PERIOD]->(period)
RETURN e.name, period.label, period.phase, collect(DISTINCT other.name) AS event_lain_di_period_sama;

// 4. Co-participation: tokoh yang ikut event ini DAN event tertentu lainnya
//   (ganti "Perang Uhud" dengan event lain untuk explore)
MATCH (e1:Event {name: "Perang Tabuk"})<-[:INVOLVED_IN]-(p:Person)-[:INVOLVED_IN]->(e2:Event {name: "Perang Uhud"})
RETURN p.name;

