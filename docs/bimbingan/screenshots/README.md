# Checklist Screenshot Neo4j — untuk Bagian A (interpretasi graf) `2026-06-04.md`

> **Tujuan:** tiap screenshot = satu visualisasi yang akan ditafsirkan di Bagian A.
> **Cara pakai:** ikuti urutan di bawah. Simpan tiap gambar dengan **nama file persis** seperti di kolom "Simpan sebagai" (folder ini). Centang `[x]` kalau sudah.
> **Setelah selesai:** kabari Claude → gambar dibuka & ditulis interpretasi jujurnya ke Bagian A.
> **Sumber query:** `data/result/neo4j/visualization_queries_v3.cypher` (seri **Q**) + `data/result/neo4j/scenario_queries_v3_weighted.cypher` (seri **G**, sudah *weighted* `weight ≥ 0.3`).

---

## 0. Prasyarat (sekali saja, sebelum ambil screenshot apa pun)

- [ ] **0a.** KG v3 ter-import. Cek: `MATCH (n) RETURN labels(n)[0] AS label, count(*) ORDER BY count(*) DESC;` — kalau kosong, jalankan `import_sirah_v3.cypher`.
- [ ] **0b.** Copy `data/result/analysis/v3/sna_metrics.csv` → folder **import** Neo4j (Neo4j Desktop: `⋯` pada DBMS → *Open folder → Import*), rename `sna_metrics_v3.csv`.
- [ ] **0c.** Jalankan **BAGIAN 0** dari `scenario_queries_v3_weighted.cypher` (blok `LOAD CSV ... SET p.pagerank ... p.community`).
- [ ] **0d.** Verifikasi properti termuat: `MATCH (p:Person) WHERE p.community IS NOT NULL RETURN count(p);` → harus ~208.
- [ ] **0e.** (opsional) Naikkan batas render: ⚙ **Settings** (kiri-bawah Browser) → *Initial Node Display* & *Max neighbours* → set ke ~500. Wajib untuk view komunitas (G3.b, LIMIT 400).

**Cara ambil gambar (semua view):** rapikan layout di kanvas → **Win + Shift + S** (Snipping Tool) → seleksi area kanvas → simpan ke folder ini dengan nama di bawah. Set **Caption = name** di panel gaya node (klik label `Person`/`Event` di atas kanvas).

---

## A.1 — Ego-network tokoh kunci (siapa yang sentral)

| # | Query | Simpan sebagai | Yang dicari | ✓ |
|---|---|---|---|---|
| 1 | **Q13** | `A1_ego_muhammad.png` | Muhammad di tengah, jari-jari ke KELUARGA/SAHABAT/MUSUH + event | [ ] |
| 2 | **Q14** | `A1_ego_abubakar.png` | Ego Abu Bakar (pembanding) | [ ] |
| 3 | **Q15** | `A1_ego_abusufyan.png` | Ego Abu Sufyan (sisi lawan/Quraisy) | [ ] |

> 💡 Konsistensi *weighted*: pada `Q13–Q15`, bila ingin selaras dengan tabel SNA, tambahkan `WHERE r2.weight >= 0.3` di baris `INVOLVED_IN`. Untuk relasi KELUARGA/SAHABAT/MUSUH tidak perlu (bukan co-participation).
> ⚠️ Ingat: bentuk "bintang" ego **otomatis** untuk tokoh mana pun — gambar ini ILUSTRASI, bukti sentral tetap dari angka betweenness.

---

## A.2 — Komunitas berwarna (ada kelompok apa) — ⚠️ TRICKY

| # | Query | Simpan sebagai | Yang dicari | ✓ |
|---|---|---|---|---|
| 4 | **G3.b** | `A2_komunitas_all.png` | Seluruh Person, **warna per komunitas** | [ ] |
| 5 | **G3.c** (community:0) | `A2_komunitas_0.png` | Satu komunitas terbesar saja | [ ] |

> ⚠️ **Browser tidak bisa warnai per nilai-properti** (`community`) — semua `Person` jadi satu warna. Pilihan:
> - **Neo4j Bloom** → *rule-based styling* by `community` (paling benar; cek menu-nya sendiri, beda antar versi), **atau**
> - **Hack label sementara** di Browser: `MATCH (p:Person) WHERE p.community IS NOT NULL CALL apoc.create.addLabels(p,['C'+p.community]) YIELD node RETURN count(*)` (butuh APOC) — tiap komunitas jadi label → otomatis beda warna. Hapus lagi setelah screenshot.
> - **Fallback:** pakai `data/result/analysis/v3/sna_person_network.png` (matplotlib, sudah berwarna komunitas) — **bukan Neo4j**, tapi jujur & langsung jadi.
>
> 💎 **Bonus before/after (kisah Amr → kenapa weighted):** screenshot `G3.b` **tanpa** filter `weight` (Amr ramai) vs **dengan** `weight ≥ 0.3` (Amr menyusut) → simpan `A2_amr_naif.png` & `A2_amr_weighted.png`. Opsional tapi kuat.

---

## A.3 — Studi kasus 5 event (kepadatan graf = kepadatan teks)

Pakai seri **G6** (sudah *weighted* `weight ≥ 0.3` → peserta ramping & jujur):

| # | Query | Simpan sebagai | Yang dicari | ✓ |
|---|---|---|---|---|
| 6 | **G6.a** | `A3_badr.png` | Perang Badr + peserta kuat (paling padat) | [ ] |
| 7 | **G6.b** | `A3_uhud.png` | Perang Uhud | [ ] |
| 8 | **G6.c** | `A3_hudaibiyah.png` | Perjanjian Hudaibiyah | [ ] |
| 9 | **G6.d** | `A3_khaibar.png` | Perang Khaibar | [ ] |
| 10 | **G6.e** | `A3_tabuk.png` | Perang Tabuk | [ ] |

> 💡 Tujuan interpretatif: bandingkan **kepadatan** kelima gambar. Badr jauh lebih ramai → bukan karena "lebih penting", tapi porsi teks Mubarakfuri terbesar.

---

## A.4 — Overview periode (struktur temporal)

| # | Query | Simpan sebagai | Yang dicari | ✓ |
|---|---|---|---|---|
| 11 | **Q4** | `A4_period_overview.png` | 15 Period + Event `IN_PERIOD` (sebaran event per periode) | [ ] |

> 💡 Lihat periode mana yang "kosong"/sedikit event vs padat → terkait catatan "event sangat sedikit" + enrichment lifecycle.

---

## A.5 — Rantai kronologi (PRECEDES)

| # | Query | Simpan sebagai | Yang dicari | ✓ |
|---|---|---|---|---|
| 12 | **Q16** | `A5_precedes.png` | Panah Event→Event + Period asal/tujuan | [ ] |

> ℹ️ Rantai PRECEDES v3 sudah **kronologis benar** (Fijar → … → Wafat Nabi, 22 panah; `fix_precedes_v3.py`). Catatan "bug Fathul Makkah→Uhud" di CLAUDE.md sudah usang. Gap kecil yang masih ada: rantai mulai dari **Perang Fijar**, Kelahiran Nabi belum disambung ke kepalanya.

---

## A.6 — Angka pendukung (opsional, screenshot tabel)

Tidak wajib gambar graf — cukup screenshot hasil **tabel** kalau mau dilampirkan:

| # | Query | Simpan sebagai | ✓ |
|---|---|---|---|
| 13 | **G5.a** (count node per label) | `A6_count_node.png` | [ ] |
| 14 | **G5.b** (count relasi per tipe) | `A6_count_relasi.png` | [ ] |
| 15 | **G1.a** (Top-10 PageRank) | `A6_top10_pagerank.png` | [ ] |

---

## Ringkasan prioritas

Kalau waktu terbatas, **3 yang paling penting** untuk dikirim ke Claude (karena *layout-dependent*, tak bisa ditafsir tanpa gambar asli):
1. `A2_komunitas_all.png` (atau fallback matplotlib)
2. `A3_badr.png`
3. `A1_ego_muhammad.png`

View lain (ego pembanding, rantai, period) bisa ditulis Claude dari bentuk query-nya lebih dulu.
