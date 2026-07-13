// =============================================================================
// PENGUJIAN FUNGSIONAL KNOWLEDGE GRAPH — untuk mengisi Tabel 4.24 (Bab 4)
// =============================================================================
// Tujuan: menjalankan 6 skenario kueri (sesuai Tabel 3.21) lalu mencatat, untuk
//         tiap skenario, empat kriteria penilaian pada Tabel 4.24:
//           (1) Eksekusi tanpa galat   -> query jalan tanpa error
//           (2) Hasil tidak kosong     -> jumlah baris > 0 (pakai query _count)
//           (3) Sesuai sumber          -> cek manual kolom `evidence` + `halaman`
//           (4) Terlacak (provenance)  -> kolom `evidence`/`halaman`/`chunk_id` ada
//
// Skema graf (dikonfirmasi dari import_sirah_v4_hybrid.cypher):
//   Node    : Person, Event, Location, Time, Period (semua punya properti `name`;
//             Period pakai `period_id`)
//   Relasi  : (Person)-[:INVOLVED_IN]->(Event)
//             (Event)-[:OCCURRED_AT]->(Location)
//             (Event)-[:OCCURRED_ON]->(Time)
//             (Event)-[:PRECEDES]->(Event)
//             (Event)-[:IN_PERIOD]->(Period)
//             relasi antar tokoh: KELUARGA / SAHABAT / MUSUH
//   Properti edge inti: weight, frequency, halaman, evidence, periode_bab
//
// Prasyarat: jalankan import_sirah_v4_hybrid.cypher dulu (graf sudah ter-load).
// Catatan weight: untuk pengujian fungsional, filter weight TIDAK dipakai (kita
//   menguji apakah graf bisa menjawab). Bila ingin tampilan "bersih" yang sama
//   dengan tabel SNA, tambahkan `AND r.weight >= 0.3` pada query INVOLVED_IN.
// =============================================================================


// ┌───────────────────────────────────────────────────────────────────────┐
// │ HELPER — cek nilai `name` yang tersedia (jalankan bila contoh di bawah   │
// │ mengembalikan 0 baris karena beda ejaan/kapitalisasi)                    │
// └───────────────────────────────────────────────────────────────────────┘
// H.1 — daftar Location (untuk Q2)
MATCH (l:Location) RETURN l.name ORDER BY l.name;
// H.2 — daftar Time (untuk Q3); format contoh: "Tahun 2 H", "Tahun 13 H"
MATCH (t:Time) RETURN t.name ORDER BY t.name;
// H.3 — daftar Event (untuk Q1) dan Person (untuk Q4/Q5)
MATCH (e:Event) RETURN e.name ORDER BY e.name;
MATCH (p:Person) RETURN p.name ORDER BY p.name;


// =============================================================================
// Q1 — KUERI BERBASIS TOKOH: "Siapa saja yang terlibat dalam Perang Badar?"
//   Pola: (Person)-[:INVOLVED_IN]->(Event)
// =============================================================================
// Q1.detail (lihat hasil + provenance untuk verifikasi 'sesuai sumber')
MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event {name: "Perang Badr"})
RETURN p.name AS tokoh, r.weight AS weight, r.halaman AS halaman, r.evidence AS evidence
ORDER BY r.weight DESC;

// Q1.count (untuk kolom 'jumlah hasil' Tabel 4.24)
MATCH (p:Person)-[:INVOLVED_IN]->(e:Event {name: "Perang Badr"})
RETURN count(DISTINCT p) AS jumlah_tokoh;


// =============================================================================
// Q2 — KUERI BERBASIS LOKASI: "Peristiwa apa saja yang terjadi di Madinah?"
//   Pola: (Event)-[:OCCURRED_AT]->(Location)
// =============================================================================
// Q2.detail (CONTAINS agar tahan variasi ejaan; ganti "Madinah" bila perlu)
MATCH (e:Event)-[r:OCCURRED_AT]->(l:Location)
WHERE toLower(l.name) CONTAINS "madinah"
RETURN l.name AS lokasi, e.name AS peristiwa, r.halaman AS halaman, r.evidence AS evidence
ORDER BY l.name, e.name;

// Q2.count
MATCH (e:Event)-[:OCCURRED_AT]->(l:Location)
WHERE toLower(l.name) CONTAINS "madinah"
RETURN count(DISTINCT e) AS jumlah_peristiwa;


// =============================================================================
// Q3 — KUERI BERBASIS WAKTU: "Peristiwa apa yang terjadi pada tahun ke-2 Hijriah?"
//   Pola: (Event)-[:OCCURRED_ON]->(Time)
// =============================================================================
// Q3.detail (CONTAINS "2 H"; cek dulu format lewat H.2 lalu sesuaikan)
MATCH (e:Event)-[r:OCCURRED_ON]->(t:Time)
WHERE toLower(t.name) CONTAINS "2 h"
RETURN t.name AS waktu, e.name AS peristiwa, r.halaman AS halaman, r.evidence AS evidence
ORDER BY t.name, e.name;

// Q3.count
MATCH (e:Event)-[:OCCURRED_ON]->(t:Time)
WHERE toLower(t.name) CONTAINS "2 h"
RETURN count(DISTINCT e) AS jumlah_peristiwa;


// =============================================================================
// Q4 — KUERI TOKOH-PERISTIWA: "Peristiwa apa saja yang melibatkan Abu Bakar?"
//   Pola: (Person)-[:INVOLVED_IN]->(Event)
// =============================================================================
// Q4.detail
MATCH (p:Person {name: "Abu Bakar"})-[r:INVOLVED_IN]->(e:Event)
RETURN e.name AS peristiwa, e.periode_bab AS periode, r.weight AS weight,
       r.halaman AS halaman, r.evidence AS evidence
ORDER BY r.weight DESC;

// Q4.count
MATCH (p:Person {name: "Abu Bakar"})-[:INVOLVED_IN]->(e:Event)
RETURN count(DISTINCT e) AS jumlah_peristiwa;


// =============================================================================
// Q5 — KUERI MULTI-HOP: "Di mana lokasi peristiwa yang melibatkan Umar?"
//   Pola: (Person)-[:INVOLVED_IN]->(Event)-[:OCCURRED_AT]->(Location)
// =============================================================================
// Q5.detail (nama kanonik: "Umar bin Al-Khaththab")
MATCH (p:Person {name: "Umar bin Al-Khaththab"})-[:INVOLVED_IN]->(e:Event)-[:OCCURRED_AT]->(l:Location)
RETURN p.name AS tokoh, e.name AS peristiwa, l.name AS lokasi
ORDER BY e.name;

// Q5.count
MATCH (p:Person {name: "Umar bin Al-Khaththab"})-[:INVOLVED_IN]->(e:Event)-[:OCCURRED_AT]->(l:Location)
RETURN count(DISTINCT l) AS jumlah_lokasi, count(DISTINCT e) AS jumlah_peristiwa;


// =============================================================================
// Q6 — KUERI KRONOLOGI: "Urutan peristiwa berdasarkan relasi mendahului"
//   Pola: (Event)-[:PRECEDES]->(Event)
// =============================================================================
// Q6.detail (pasangan mendahului)
MATCH (e1:Event)-[:PRECEDES]->(e2:Event)
RETURN e1.name AS sebelum, e2.name AS sesudah, e1.periode_bab AS periode_sebelum
ORDER BY e1.page_range;

// Q6.count
MATCH (:Event)-[r:PRECEDES]->(:Event)
RETURN count(r) AS jumlah_relasi_precedes;


// =============================================================================
// RINGKASAN OTOMATIS — satu hasil berisi jumlah hasil tiap skenario (Tabel 4.24)
// =============================================================================
MATCH (p:Person)-[:INVOLVED_IN]->(:Event {name: "Perang Badr"})
WITH count(DISTINCT p) AS q1
MATCH (e2:Event)-[:OCCURRED_AT]->(l2:Location) WHERE toLower(l2.name) CONTAINS "madinah"
WITH q1, count(DISTINCT e2) AS q2
MATCH (e3:Event)-[:OCCURRED_ON]->(t3:Time) WHERE toLower(t3.name) CONTAINS "2 h"
WITH q1, q2, count(DISTINCT e3) AS q3
MATCH (:Person {name: "Abu Bakar"})-[:INVOLVED_IN]->(e4:Event)
WITH q1, q2, q3, count(DISTINCT e4) AS q4
MATCH (:Person {name: "Umar bin Al-Khaththab"})-[:INVOLVED_IN]->(:Event)-[:OCCURRED_AT]->(l5:Location)
WITH q1, q2, q3, q4, count(DISTINCT l5) AS q5
MATCH (:Event)-[r6:PRECEDES]->(:Event)
RETURN q1 AS Q1_tokoh_Badr, q2 AS Q2_event_Madinah, q3 AS Q3_event_tahun2H,
       q4 AS Q4_event_AbuBakar, q5 AS Q5_lokasi_Umar, count(r6) AS Q6_precedes;
// =============================================================================
