# Laporan Bimbingan — Bagian 1: Pembobotan Relasi

**Mahasiswa:** Rayssa Ravelia (5025211219)
**Pembimbing:** Prof. Dr. Diana Purwitasari
**Topik TA:** Knowledge Graph Sirah Nabawiyah
**Tanggal laporan:** 29 April 2026

---

## 1. Latar Belakang Revisi

Pada bimbingan sebelumnya, dosen memberi catatan revisi pertama:

> *"Bagaimana jika ekstraksi relasi ini dilakukan pembobotan sebagai bentuk apakah dia benar-benar berkaitan dengan entitas satu dengan yang lainnya, agar ketika di Neo4j akan terlihat yang benar-benar berelasi atau tidak. Pendekatan yang disarankan: set periode (event ini berlangsung di periode apa, dibahas di bab berapa sampai berapa), atau tetap dimunculkan tapi ditambahkan bobot (deket secara teks tapi cuma di-mention saja, atau benar-benar terlibat)."*

Sebelum revisi, semua relasi di `edges.csv` muncul sebagai relasi *biner* (ada atau tidak), tanpa indikator seberapa kuat keterhubungan dua entitas. Akibatnya, di Neo4j semua edge terlihat setara — padahal banyak relasi berasal dari ko-okurensi tekstual yang lemah (misal: dua entitas hanya kebetulan disebut di paragraf yang sama tetapi konteksnya tidak menunjukkan keterlibatan langsung).

---

## 2. Definisi Pembobotan

**Pembobotan relasi** adalah pemberian skor numerik **`weight` ∈ [0.0, 1.0]** pada setiap edge di Knowledge Graph untuk merepresentasikan **kekuatan keterhubungan** antara dua entitas.

Bobot ini dibangun dari kombinasi dua sinyal:

| Komponen | Range | Pertanyaan yang dijawab |
|---|---|---|
| **Proximity score** | 0.0 – 0.5 | Seberapa dekat dua entitas muncul dalam teks? (di kalimat sama? berapa karakter jaraknya?) |
| **Period score** | 0.0 – 0.5 | Apakah relasi ini muncul di BAB yang memang membahas event-nya, atau cuma sekadar di-mention di bab lain? |

**Rumus akhir:**
```
weight = proximity_score + period_score      (range 0.0 – 1.0)
```

**Interpretasi nilai:**
- `weight ≥ 0.8` → relasi kuat (di kalimat sama + dibahas di periode/BAB yang sesuai)
- `weight 0.4 – 0.7` → relasi moderat (dekat tapi salah satu komponen lemah)
- `weight ≤ 0.3` → relasi lemah (kemungkinan hanya mention sambil lalu di bab yang tidak membahas event tersebut)

---

## 3. Posisi dalam Pipeline

Pembobotan dilakukan di tahap **Relation Extraction**, tepat setelah pasangan entitas kandidat ditemukan dan sebelum hasilnya disimpan ke `edges.csv`.

```
PDF → OCR → CSV → Preprocessing → Chunking → Manual Labelling → Alias Clustering
                                                                       ↓
                                         ┌────────────────────────────────────────┐
                                         │  Relation Extraction                   │
                                         │   ├─ Cari pasangan kandidat            │
                                         │   ├─ Filter dengan contextual guards   │
                                         │   ├─ Hitung proximity_score            │
                                         │   ├─ Hitung period_score  ◄── PEMBOBOTAN
                                         │   └─ weight = prox + period            │
                                         └────────────────────────────────────────┘
                                                                       ↓
                                                          Neo4j (KG dengan weight)
```

File implementasi:
- `src/relation_extraction/period_mapping.py` — modul perhitungan skor (baru, kontribusi revisi)
- `src/relation_extraction/relation_extraction.py` — pipeline utama yang mengintegrasikan pembobotan

---

## 4. Alur Detail (Step by Step)

### Step 1 — Bangun *Event Period Map* dari TOC

Setiap EVENT dipetakan ke BAB utamanya berdasarkan **fuzzy matching** terhadap `data/toc_groundtruth.json` (61 BAB).

**Cara matching:**
1. Normalisasi nama event & judul BAB (lowercase, strip whitespace).
2. Cek substring (event di dalam judul BAB atau sebaliknya) → skor **0.95**.
3. Jika tidak ada substring match, gunakan `SequenceMatcher.ratio()` (Python `difflib`).
4. Ambil BAB dengan skor tertinggi, dengan **threshold minimum 0.5**.
5. Hitung `page_end` BAB ke-i = `page_start` BAB ke-(i+1) − 1.

**Output:** dictionary `{event_name: {bab_title, page_start, page_end}}`. Dari 41 EVENT total, **39 berhasil ter-mapping** ke BAB.

### Step 2 — Hitung *Proximity Score* (per pasangan entitas)

Diberikan dua entitas A dan B dalam satu chunk:

| Kondisi | Skor |
|---|---|
| A & B berada di **kalimat yang sama** | **0.5** |
| Jarak antar-entitas < 50 karakter | 0.4 |
| Jarak < 100 karakter | 0.3 |
| Jarak < 200 karakter | 0.2 |
| Lebih jauh dari itu | 0.1 |

Pemecahan kalimat memakai regex `(?<=[.!?])\s+` (split di titik/tanya/seru).

### Step 3 — Hitung *Period Score* (per relasi)

Untuk setiap relasi yang melibatkan EVENT:

| Kondisi | Skor |
|---|---|
| Halaman chunk **berada di range BAB utama event** | **0.5** |
| Event **tidak ter-mapping** ke BAB manapun | 0.25 (netral) |
| Halaman chunk **di luar range BAB utama event** | 0.0 |

Untuk relasi tanpa EVENT (Person-Person), period score default = **0.25** (netral).

### Step 4 — Gabungkan & Deduplikasi

Saat dua relasi dengan `(source, target, relation_type)` sama muncul lebih dari sekali (di chunk berbeda), digabung menjadi satu edge dengan:
- `proximity_score` final = **max** dari semua kemunculan (mengambil bukti terkuat)
- `period_score` dihitung dari halaman gabungan
- `frequency` = jumlah kemunculan
- `weight` = `proximity_score + period_score` (dibulatkan 2 desimal)

### Step 5 — Tulis ke `edges.csv`

Kolom output `edges.csv` setelah revisi:
```
source_name; source_label; relation_type; relation_subtype;
target_name; target_label; chunk_id; evidence; halaman;
frequency; weight; periode_bab
```

Tiga kolom yang **baru ditambahkan** sebagai hasil revisi: `weight`, `periode_bab`, `relation_subtype`.

---

## 5. Input dan Output

### Input
| File | Fungsi |
|---|---|
| `data/result/manual_labelling/sirah_prelabelled.csv` | 5.753 entitas valid (PERSON 3.801, LOCATION 1.447, TIME 309, EVENT 196) |
| `data/result/alias_clustering/alias_map.json` | 143 alias, 109 cluster (untuk normalisasi nama kanonik) |
| `data/toc_groundtruth.json` | 61 BAB + sub-bab dengan `page_start` |

### Output
| File | Isi |
|---|---|
| `data/result/relation_result/nodes.csv` | 897 node unik (PERSON 658, TIME 147, LOCATION 51, EVENT 41), EVENT punya tambahan kolom `periode_bab` & `page_range` |
| `data/result/relation_result/edges.csv` | 370 edge dengan `weight` per edge dan `periode_bab` untuk relasi yang melibatkan EVENT |

---

## 6. Hasil

### 6.1 Distribusi Bobot Global

Dari **370 edge** yang dihasilkan:

| Statistik | Nilai |
|---|---|
| Mean | **0.474** |
| Median | 0.500 |
| Min | 0.200 |
| Max | 1.000 |
| Std deviasi | 0.180 |

**Edges yang berhasil mendapat `periode_bab`:** 219 dari 370 (59 %).

### 6.2 Bobot per Tipe Relasi

| Relation Type | Jumlah | Mean weight | Min | Max |
|---|---:|---:|---:|---:|
| INVOLVED_IN | 153 | 0.384 | 0.20 | 1.00 |
| KELUARGA | 91 | 0.550 | 0.55 | 0.55 |
| OCCURRED_ON | 39 | 0.387 | 0.20 | 0.50 |
| OCCURRED_AT | 34 | 0.416 | 0.20 | 0.65 |
| SAHABAT | 25 | 0.550 | 0.55 | 0.55 |
| PRECEDES | 18 | 1.000 | 1.00 | 1.00 |
| MUSUH | 10 | 0.550 | 0.55 | 0.55 |

**Catatan:**
- **PRECEDES = 1.0** karena urutan kronologis antar BAB bersifat deterministik (bukan dari ko-okurensi).
- **KELUARGA / SAHABAT / MUSUH = 0.55** karena tidak melibatkan EVENT, jadi period score = 0.25 (netral) + proximity rata-rata 0.30.

### 6.3 Contoh Relasi pada Tiap Tier Bobot

**Bobot tinggi (= 1.0)** — relasi sangat kuat:
```
Muhammad —[INVOLVED_IN]→ Perang Khaibar    | periode: PERANG KHAIBAR DAN WADIL QURA
Muhammad —[INVOLVED_IN]→ Perang Tabuk      | periode: PERANG TABUK
```
→ Disebut di kalimat yang sama **dan** muncul di BAB yang memang membahas event tersebut.

**Bobot sedang (= 0.5)** — relasi moderat:
```
Imran bin Amr —[INVOLVED_IN]→ Hijrah       | periode: Hijrah ke Habasyah yang Pertama
Perang Yarmuk —[OCCURRED_ON]→ tahun 13 H   | periode: PERANG TABUK
```
→ Dekat secara teks (proximity 0.5), tapi di-mention di BAB yang bukan BAB utama event (period 0.0–0.25), atau sebaliknya.

**Bobot rendah (= 0.2)** — relasi lemah / mention sambil lalu:
```
Hijrah —[OCCURRED_AT]→ Yaman               | periode: Hijrah ke Habasyah yang Pertama
Umar bin Al-Khaththab —[INVOLVED_IN]→ Perang Yarmuk
```
→ Jarak teks > 100 karakter (proximity 0.2) **dan** di luar BAB utama event (period 0.0). Edge tetap muncul di KG, tapi user/peneliti bisa filter `weight < 0.3` di Cypher untuk memfokuskan analisis ke relasi yang kuat.

### 6.4 Manfaat Praktis di Neo4j

Dengan adanya kolom `weight`, di Cypher bisa langsung dilakukan filter atau ranking, misalnya:

```cypher
// Hanya tampilkan relasi kuat
MATCH (a)-[r]->(b) WHERE r.weight >= 0.7 RETURN a, r, b;

// Top 10 keterlibatan tokoh terkuat
MATCH (p:PERSON)-[r:INVOLVED_IN]->(e:EVENT)
RETURN p.name, e.name, r.weight ORDER BY r.weight DESC LIMIT 10;
```

---

## 7. Langkah Berikutnya

1. **Validasi manual sample bobot** — ambil 30 edge acak (10 high / 10 mid / 10 low), cocokkan dengan teks asli untuk validasi apakah skor benar-benar mencerminkan kekuatan relasi.
2. **Tuning threshold** — saat ini cutoff *low / mid / high* belum dibuat resmi; rencana: tentukan cutoff bersama dosen agar konsisten dengan standar visualisasi Neo4j (misal: tampilkan hanya `weight ≥ 0.4`).
3. **Setelah model NER final dijalankan** (LLM-NER & SRL-NER) — re-run pipeline `relation_extraction.py` pada output NER, lalu bandingkan distribusi `weight` antara hasil pre-labelling vs hasil model.
4. **Lanjut ke section 2** — laporan implementasi pseudo-labelling SRL-NER + LLM-NER (sesuai revisi poin 2).

---

## 8. File Terkait

| File | Deskripsi |
|---|---|
| `src/relation_extraction/period_mapping.py` | Modul perhitungan proximity & period score (baru) |
| `src/relation_extraction/relation_extraction.py` | Pipeline relation extraction (di-update untuk integrasi weight) |
| `data/result/relation_result/nodes.csv` | 897 nodes |
| `data/result/relation_result/edges.csv` | 370 edges dengan kolom `weight` & `periode_bab` |
| `data/toc_groundtruth.json` | Ground truth daftar isi 61 BAB (sumber period mapping) |
