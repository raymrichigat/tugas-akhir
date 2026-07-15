# Panduan Neo4j untuk §4.5 Evaluasi Knowledge Graph

Panduan praktis: gambar apa yang butuh screenshot Neo4j, query persisnya, dan cara mengisi Tabel 4.25. Ikuti berurutan.

---

## Langkah 0 — Prasyarat (WAJIB, sekali saja)

1. Buka **Neo4j Desktop** → buat/aktifkan satu DBMS kosong → **Open with Neo4j Browser**.
2. Import knowledge graph v4 (model pemenang, augmentation). Di Browser, jalankan isi berkas:
   ```
   data/result/neo4j/import_sirah_v4_hybrid.cypher
   ```
   Cara cepat: buka berkas itu, salin seluruh isinya ke Browser, Run. (Atau `:source` bila pakai cypher-shell.)
   > ⚠️ Pakai **`import_sirah_v4_hybrid.cypher`** — BUKAN v2/v3/v4 (non-hybrid). Ini yang konsisten dengan seluruh angka §4.5.
3. Cek berhasil — angka yang benar:
   ```cypher
   MATCH (n) RETURN count(n) AS node;   // 1192 (1177 entitas + 15 Period)
   MATCH ()-[r]->() RETURN count(r) AS edge;   // 728 (693 antar entitas + 35 IN_PERIOD)
   ```
   > Catatan: CSV memuat 705 baris relasi, tetapi 12 di antaranya triple identik (beda bukti/halaman) yang digabung `MERGE` jadi satu edge, sehingga graf akhir 693 + 35 = **728**. Ini normal, bukan galat.
4. **Tulis label komunitas** (khusus untuk Gambar 4.18). Jalankan isi berkas:
   ```
   data/result/neo4j/set_community_v4.cypher
   ```
   Ini menambah properti `community` (hasil deteksi komunitas dari analisis Python) ke tiap simpul Person, karena Neo4j tak bisa mendeteksi komunitas sendiri tanpa plugin GDS. Cek: `MATCH (p:Person) WHERE p.community=0 RETURN count(p);` harus mengembalikan **66**.

Setelah graf ter-load, kerjakan gambar di bawah. Tiap screenshot: jalankan query → tata layout (drag simpul biar rapi) → tombol kamera/expand → simpan PNG.

---

## Langkah 1 — Gambar yang butuh screenshot Neo4j (6 gambar)

| Gambar | Isi | Query Cypher | Catatan |
|---|---|---|---|
| **4.16** | Contoh KG: sub-graf Perang Badr | `MATCH (e:Event {name:"Perang Badr"})-[r]-(n) RETURN e,r,n LIMIT 60` | Warna otomatis per-label. Tunjukkan tokoh+lokasi+waktu yang tertaut. |
| **4.17 (kiri)** | Ego **co-participation** Muhammad | (query di bawah — lewat Event) | ~101 tokoh (degree proyeksi 108). **WAJIB lewat Event**, bukan relasi langsung, agar cocok degree centrality Tabel 4.19. |
| **4.17 (kanan)** | Ego **co-participation** Abu Bakar | (query di bawah — lewat Event) | ~70 tokoh. Sandingkan dgn Muhammad **pada skala/zoom sama** biar kontras degree terlihat. |
| **4.18** | Sub-graf komunitas terbesar (66 anggota) | (query di bawah) | Perlu `set_community_v4.cypher` dulu (Langkah 0.4). Menampilkan komunitas 0 UTUH (66 tokoh), bukan 6 pilihan. |
| **4.19** | Sub-graf 5 peristiwa besar (studi kasus) | (query gabungan di bawah) | 5 gugus event dalam satu tampilan; Badr/Uhud padat, Tabuk jarang; Muhammad menaut kelimanya. Alternatif: 5 screenshot terpisah. |
| **4.20** | Kesalahan graf: INVOLVED_IN palsu Amr bin Umayyah | `MATCH (p:Person {name:"Amr bin Umayyah"})-[r:INVOLVED_IN]->(e:Event) RETURN p,r,e` | Harus muncul **4 relasi** (Badr/Uhud/Tabuk/Khandaq); 3 di antaranya false-positive (bahasannya sudah di prosa §4.5.5). |
| **4.22** | Hasil kueri fungsional F1 (tokoh Perang Badr) | `MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event {name:"Perang Badr"}) RETURN p,r,e` | Ilustrasi keluaran fungsional dalam bentuk graf. |

**Query Gambar 4.17** (ego co-participation — WAJIB lewat Event, bukan relasi langsung):
```cypher
// kiri: Muhammad (ganti name jadi "Abu Bakar" untuk panel kanan)
MATCH (m:Person {name:"Muhammad"})-[r1:INVOLVED_IN]->(e:Event)<-[r2:INVOLVED_IN]-(p:Person)
WHERE r1.weight >= 0.3 AND r2.weight >= 0.3
RETURN m, e, p
```
Kenapa lewat Event: *degree centrality* Tabel 4.19 dihitung pada proyeksi antar tokoh (dua tokoh terhubung bila berbagi peristiwa). Query relasi langsung `(m)-[r]-(n)` hanya menampilkan KELUARGA/SAHABAT/MUSUH + Event, jadi TIDAK memperlihatkan ~108 tetangga tokoh itu. Simpul Event yang muncul di tengah adalah perantara co-participation, bukan kesalahan. Threshold `weight >= 0.3` = `WEIGHT_THRESHOLD` di `sna_analysis.py`. Hasil: Muhammad ~101 tetangga vs Abu Bakar ~70.

**Query Gambar 4.18** (komunitas terbesar 66 anggota — perlu properti `community`):
```cypher
MATCH (p:Person {community:0})-[r]-(q:Person {community:0}) RETURN p,r,q
```
Prasyarat: jalankan `data/result/neo4j/set_community_v4.cypher` lebih dulu (Langkah 0.4) — file itu menulis label komunitas ke tiap simpul (Neo4j tak bisa deteksi komunitas sendiri tanpa GDS). Hasil: 66 tokoh komunitas terbesar + seluruh relasi internalnya (padat = itu tujuannya). Rincian keanggotaan semua komunitas → `docs/lampiran/lampiran_komunitas_tokoh.md`.

**Query Gambar 4.19** (5 peristiwa besar, satu tampilan gabungan):
```cypher
MATCH (p:Person)-[r:INVOLVED_IN]->(e:Event)
WHERE e.name IN ["Perang Badr","Perang Uhud","Perjanjian Hudaibiyah","Perang Khaibar","Perang Tabuk"]
RETURN p,r,e
```
Lima simpul Event jadi pusat lima gugus tokoh. Kontras kepadatan (Badr/Uhud padat vs Tabuk jarang) langsung terlihat, dan Muhammad tampak menaut kelimanya. Angka acuan = Tabel 4.24. Bila ingin persis seperti panel lama (lima kotak terpisah), ambil 5 screenshot dengan mengganti `name` satu per satu.

### Gambar 4.21 — ego relasi LANGSUNG (BEDA dari 4.17)
**Gambar 4.21** (§4.5.5, "Jaringan ego Nabi Muhammad") memakai ego **relasi langsung** pada KG, bukan co-participation:
```cypher
MATCH (m:Person {name:'Muhammad'})-[r]-(n) RETURN m,r,n
```
Ini menampilkan relasi naratif langsung (KELUARGA/SAHABAT/MUSUH + INVOLVED_IN ke Event) dan buku sudah mengungkap bahwa graf ini **berbeda** dari proyeksi co-participation yang dipakai Tabel 4.19/4.20.
> ⚠️ **4.17 ≠ 4.21.** Gambar 4.17 = ego **co-participation** (lewat Event, untuk cocokkan degree centrality); Gambar 4.21 = ego **relasi langsung** (naratif). Query-nya beda, jadi **dua screenshot terpisah** — TIDAK bisa dipakai ulang. (Koreksi dari catatan sebelumnya.)
> Screenshot lama `docs/bimbingan/screenshots/A1_ego_muhammad.png` JANGAN dipakai — dari KG lama (masih ada event lifecycle Kelahiran/Hijrah Madinah yang tak ada di v4). Ambil ulang dari graf v4.

---

> **Catatan:** seluruh gambar §4.5 kini Neo4j (tidak ada lagi matplotlib). Gambar 4.19 yang dulu panel matplotlib (`v4_hybrid/case_study_panel.png`) sudah diganti jadi screenshot Neo4j (query di atas). File matplotlib itu tak dipakai lagi di buku.

---

## Langkah 2 — Mengisi Tabel 4.25 (Pengujian Fungsional F1–F6)

1. Jalankan **satu query RINGKASAN** ini (ada di ujung `functional_test_queries_bab4.cypher`) — langsung keluar 6 angka sekaligus:
   ```cypher
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
   ```
2. Salin keenam angka (q1..q6) ke kolom **"Jumlah hasil"** Tabel 4.25 (F1→q1, F2→q2, ... F6→q6).
3. **Kalau ada yang keluar 0** (biasanya F2/F3 karena beda ejaan/format nama), jalankan HELPER dulu untuk lihat nilai `name` yang tersedia, lalu sesuaikan kata kunci di query:
   - Lokasi (F2): `MATCH (l:Location) RETURN l.name ORDER BY l.name;`
   - Waktu (F3): `MATCH (t:Time) RETURN t.name ORDER BY t.name;` (cari format "2 H"/"2 Hijriyah")
   Ganti `"madinah"`/`"2 h"` di query sesuai temuan, lalu jalankan ulang.
4. Kolom lain (Eksekusi / Tidak kosong / Sesuai sumber / Terlacak) diisi ✔/✘ apa adanya. "Sesuai sumber" & "Terlacak" dicek dari query **detail** (Q1.detail dst di file yang sama) yang menampilkan kolom `evidence` + `halaman`.

> Berkas lengkap (Q1–Q6 detail + count + helper): `data/result/neo4j/functional_test_queries_bab4.cypher`.

---

## Ringkasan checklist

- [ ] Import `import_sirah_v4_hybrid.cypher` (Langkah 0)
- [ ] Screenshot **4.16** (Perang Badr), **4.17-kiri** (ego co-participation Muhammad, lewat Event), **4.17-kanan** (ego co-participation Abu Bakar, lewat Event), **4.18** (komunitas inti), **4.19** (5 peristiwa besar), **4.20** (Amr artefak), **4.21** (ego relasi LANGSUNG Muhammad — beda dari 4.17), **4.22** (F1 Perang Badr)
- [ ] Jalankan query RINGKASAN → isi 6 angka Tabel 4.25 (Langkah 2)
- [ ] Verifikasi "sesuai sumber"/"terlacak" via query detail (kolom evidence/halaman)

**Total: 8 screenshot** (4.16, 4.17-kiri, 4.17-kanan, 4.18, 4.19, 4.20, 4.21, 4.22) + 1 query ringkasan. Semua Neo4j, tanpa matplotlib. **Catatan: 4.17 (co-participation lewat Event) dan 4.21 (relasi langsung) BEDA query → screenshot terpisah.**

> Query bukti struktural tambahan (untuk pembahasan artefak: dua kubu Badr, Yatsrib-vs-Madinah) ada di `data/result/neo4j/sna_evidence_queries_bab4.cypher` — opsional, hanya bila ingin bukti tekstual di luar screenshot.
