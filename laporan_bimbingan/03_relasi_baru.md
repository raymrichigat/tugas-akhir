# Laporan Bimbingan — Bagian 3: Penambahan Relasi Antar Entitas

**Mahasiswa:** Rayssa Ravelia (5025211219)
**Pembimbing:** Prof. Dr. Diana Purwitasari
**Topik TA:** Knowledge Graph Sirah Nabawiyah
**Tanggal laporan:** 30 April 2026

---

## 1. Latar Belakang Revisi

Pada bimbingan sebelumnya, dosen memberi catatan revisi ketiga:

> *"Penambahan relasi antar entitas seperti:*
> *- Relasi orang dengan orang → sahabat, musuh, atau anak*
> *- Peristiwa dengan peristiwa → hijrah lalu badar lalu uhud lalu perang khandaq"*

**Kondisi sebelum revisi:** Knowledge Graph hanya memiliki tiga tipe relasi yang semuanya **berpusat pada EVENT**:
- `INVOLVED_IN` (PERSON → EVENT)
- `OCCURRED_AT` (EVENT → LOCATION)
- `OCCURRED_ON` (EVENT → TIME)

Akibatnya, KG kehilangan dua dimensi penting Sirah Nabawiyah:
1. **Hubungan sosial antar tokoh** (siapa keluarga siapa, siapa sahabat siapa, siapa lawan siapa) — padahal silsilah & aliansi sangat sentral di teks Sirah.
2. **Urutan kronologis antar peristiwa** — padahal narasi Sirah disusun secara kronologis (Hijrah → Badar → Uhud → Khandaq → Hudaibiyah → Khaibar → Fathul Makkah → Tabuk).

---

## 2. Definisi Relasi Baru

Ditambahkan **4 tipe relasi baru** ke schema Knowledge Graph:

### 2.1 Relasi Person-Person (3 tipe)

| Tipe | Subtipe | Definisi |
|---|---|---|
| **`KELUARGA`** | `anak`, `orangtua`, `pasangan`, `saudara`, `paman/bibi`, `cucu/keponakan` | Hubungan kekerabatan biologis atau pernikahan |
| **`SAHABAT`** | `sahabat`, `sekutu` | Aliansi/dukungan/persahabatan antar tokoh |
| **`MUSUH`** | `musuh` | Permusuhan, peperangan personal, atau pertentangan |

### 2.2 Relasi Event-Event (1 tipe)

| Tipe | Definisi |
|---|---|
| **`PRECEDES`** | Event A terjadi **sebelum** Event B secara kronologis (berdasarkan urutan BAB di buku) |

**Schema relasi total** setelah revisi: 7 tipe (3 lama + 4 baru).

---

## 3. Posisi dalam Pipeline

Relasi-relasi baru dibangun di tahap **Relation Extraction**, **paralel** dengan ekstraksi relasi lama, sebelum tahap deduplikasi & pembobotan:

```
Manual Labelling → Alias Clustering
       ↓
┌─────────────────────────────────────────────────┐
│ Relation Extraction                             │
│  ├─ build_relations()                           │
│  │    → INVOLVED_IN, OCCURRED_AT, OCCURRED_ON   │
│  ├─ build_person_person_relations()  ◄── BARU   │
│  │    → KELUARGA, SAHABAT, MUSUH                │
│  ├─ deduplicate_relations()                     │
│  └─ build_event_chronology()         ◄── BARU   │
│       → PRECEDES                                │
└─────────────────────────────────────────────────┘
       ↓
Pembobotan & Output edges.csv
```

Implementasi:
- `src/relation_extraction/relation_extraction.py` — fungsi `build_person_person_relations()` & `build_event_chronology()` ditambahkan.

---

## 4. Alur Detail (Step by Step)

### 4.1 Relasi Person-Person (KELUARGA / SAHABAT / MUSUH)

Pendekatan: **co-occurrence + regex pattern matching pada evidence**.

#### Step 1 — Iterasi per chunk
Untuk setiap chunk, ambil semua entitas berlabel `PERSON`. Skip chunk yang punya kurang dari 2 PERSON.

#### Step 2 — Generate semua pasangan PERSON
Buat semua kombinasi `(p1, p2)` (kombinasi, bukan permutasi). Untuk tiap pasangan:

#### Step 3 — Filter dengan 3 guard
| Guard | Tujuan |
|---|---|
| **Span overlap check** | Skip pasangan yang span karakter-nya overlap (artinya bagian dari satu nama panjang, misal "Abu Bakar" overlap dengan "Abu Bakar Ash-Shiddiq") |
| **Self-relation check** | Skip jika `canonical_name` sama (alias map sudah menyatukan ke nama yang sama) |
| **Substring check** | Skip jika satu nama adalah substring nama lain (misal "Muhammad" vs "Muhammad bin Abdullah") |
| **Narrator check** | Skip jika salah satu adalah perawi/penulis kitab (Ibnu Hisyam, Ibnu Ishaq, Ath-Thabari, dst — bukan tokoh sejarah) |

#### Step 4 — Cek proximity
Pasangan harus berada di kalimat sama **atau** dalam jarak < 150 karakter. Kalau lebih jauh → skip (terlalu jauh untuk disebut berelasi).

#### Step 5 — Ekstrak evidence
Ambil cuplikan teks ±50 karakter di sekitar kedua entitas sebagai bukti.

#### Step 6 — Pattern matching pada evidence

Regex dijalankan pada evidence untuk menentukan tipe relasi. Pattern dicoba **berurutan**: KELUARGA dulu (paling spesifik), lalu SAHABAT, lalu MUSUH (paling umum).

**Contoh pola KELUARGA** (8 pola):
```python
r"(?:putra|puteri|anak)\s+(?:dari\s+)?{person}"      → subtype: anak
r"{person}\s+(?:bin|binti|ibnu)\s+"                   → subtype: anak
r"(?:ayah|bapak|ibu|ibunda)\s+(?:dari\s+)?{person}"  → subtype: orangtua
r"(?:istri|suami|isteri)\s+(?:dari\s+)?{person}"     → subtype: pasangan
r"(?:menikah|menikahi|mengawini)\s+(?:dengan\s+)?{person}" → subtype: pasangan
r"(?:saudara|adik|kakak)\s+(?:dari\s+)?{person}"     → subtype: saudara
r"(?:paman|bibi)\s+(?:dari\s+)?{person}"             → subtype: paman/bibi
r"(?:cucu|keponakan)\s+(?:dari\s+)?{person}"         → subtype: cucu/keponakan
```

**Contoh pola SAHABAT** (4 pola):
```python
r"(?:sahabat|teman)\s+(?:dekat\s+)?(?:dari\s+)?{person}" → sahabat
r"(?:membela|menolong|mendukung|membantu)\s+{person}"   → sekutu
r"(?:bersama|bersekutu|bergabung)\s+(?:dengan\s+)?{person}" → sekutu
r"(?:setia|loyal)\s+(?:kepada|terhadap)\s+{person}"     → sahabat
```

**Contoh pola MUSUH** (4 pola):
```python
r"(?:musuh|lawan|penentang)\s+(?:dari\s+)?{person}"    → musuh
r"(?:memerangi|menyerang|melawan|membunuh)\s+{person}" → musuh
r"(?:menentang|memusuhi|membenci)\s+{person}"          → musuh
r"(?:berperang|bertempur)\s+(?:melawan\s+)?{person}"   → musuh
```

Jika satu pola match → relasi disimpan dengan `relation_subtype` sesuai pola, lalu **break** (satu pasangan = satu relasi).

### 4.2 Relasi Event-Event (PRECEDES)

Pendekatan: **urutan kronologis berdasarkan BAB**.

#### Step 1 — Filter EVENT
Ambil EVENT nodes yang:
- Sudah ter-mapping ke BAB (via `event_period_map` dari modul `period_mapping.py`)
- Memiliki `frequency >= 2` (event yang cuma muncul sekali kemungkinan noise)

#### Step 2 — Sort by `page_start` BAB
Event diurutkan berdasarkan halaman awal BAB utamanya (kronologis sesuai urutan buku).

#### Step 3 — Deduplikasi BAB
Jika beberapa event berada di BAB yang sama (page_start sama), hanya event pertama yang diambil. Tujuannya supaya rantai PRECEDES merepresentasikan **transisi antar BAB**, bukan event-event di dalam satu BAB.

#### Step 4 — Bangun rantai PRECEDES
Untuk setiap pasangan event berurutan `(eventᵢ, eventᵢ₊₁)`, buat satu edge:
```
eventᵢ -[PRECEDES]-> eventᵢ₊₁
```

#### Step 5 — Set weight = 1.0
Karena urutan BAB bersifat deterministik (langsung dari struktur buku), weight di-set 1.0 secara default — bukan dari kombinasi proximity + period seperti relasi lain.

---

## 5. Input dan Output

### Input
| File | Isi |
|---|---|
| `data/result/manual_labelling/sirah_prelabelled.csv` | 5.753 entitas (sumber pasangan PERSON) |
| `data/result/alias_clustering/alias_map.json` | Untuk normalisasi nama kanonik (cegah duplikasi pasangan) |
| `data/toc_groundtruth.json` | Sumber urutan BAB untuk PRECEDES |

### Output
Kolom baru di `edges.csv`:
- **`relation_subtype`** — sub-kategori (misal: `anak`, `pasangan`, `sekutu`)
- Tipe relasi baru di kolom `relation_type`: `KELUARGA`, `SAHABAT`, `MUSUH`, `PRECEDES`

---

## 6. Hasil

> **Catatan keterkaitan dengan Section 01 (Pembobotan):**
> Section ini membahas **revisi #3 (penambahan tipe relasi)**, bukan revisi #1 (pembobotan). Namun karena keduanya diimplementasikan di pipeline yang sama (`relation_extraction.py`), kolom `weight` dari Section 01 **juga diaplikasikan ke relasi baru di sini**. Jadi:
> - Tabel di section 6.1 melaporkan **jumlah edge per tipe** (revisi #3).
> - Kolom `weight` pada tiap edge baru (revisi #1) sudah dihitung dengan rumus yang sama: KELUARGA/SAHABAT/MUSUH = 0.55 (proximity 0.30 + period netral 0.25), PRECEDES = 1.0 (deterministik dari urutan BAB).
>
> Dengan kata lain: **Section 01 = "rating bintang"**, **Section 03 = "jenis hubungan baru"**. Dua hal terpisah yang kebetulan dijalankan bersamaan.

### 6.1 Distribusi Total

Dari **370 edge** total, relasi baru menyumbang **144 edge (39 %)**:

| Tipe Relasi | Jumlah | Persentase |
|---|---:|---:|
| INVOLVED_IN (lama) | 153 | 41.4 % |
| **KELUARGA** (baru) | **91** | **24.6 %** |
| OCCURRED_ON (lama) | 39 | 10.5 % |
| OCCURRED_AT (lama) | 34 | 9.2 % |
| **SAHABAT** (baru) | **25** | **6.8 %** |
| **PRECEDES** (baru) | **18** | **4.9 %** |
| **MUSUH** (baru) | **10** | **2.7 %** |

**Sebelum revisi:** 291 edges (3 tipe). **Sesudah revisi:** 370 edges (7 tipe) → kenaikan 27 %.

### 6.2 Distribusi Subtype KELUARGA

| Subtype | Jumlah |
|---|---:|
| `anak` | 58 |
| `pasangan` | 24 |
| `saudara` | 5 |
| `orangtua` | 3 |
| `paman/bibi` | 1 |

Subtype `anak` mendominasi karena banyak nasab muncul lewat pola "X **bin/binti** Y" yang sangat khas di teks Sirah.

### 6.3 Contoh Relasi yang Dihasilkan

**KELUARGA:**
```
Ibrahim          —[KELUARGA:orangtua]→  Isma'il
Mudhadh bin Amr  —[KELUARGA:pasangan]→ Isma'il
Muhammad         —[KELUARGA:anak]    →  Ibrahim
Haritsah bin Amr —[KELUARGA:anak]    →  Haritsah bin Tsa'labah
```

**SAHABAT:**
```
As'ad bin Zurarah —[SAHABAT:sekutu]→ Mush'ab bin Umair
```
*Evidence: "...kedudukan As'ad sebagai da'i yang ulung bersama Mush'ab bin Umair..."*

**MUSUH:**
```
Umar bin Al-Khaththab —[MUSUH:musuh]→ Muhammad   (sebelum masuk Islam)
Abu Sufyan bin Harb   —[MUSUH:musuh]→ Muhammad
Ibnu Qami'ah          —[MUSUH:musuh]→ Muhammad   (pelukai di Perang Uhud)
```

**PRECEDES — Rantai Kronologis Lengkap (18 edge):**
```
Perang Fijar          → Hijrah
Hijrah                → Isra' Mi'raj
Isra' Mi'raj          → Baiat Aqabah
Baiat Aqabah          → Baiat Aqabah Kubra
Baiat Aqabah Kubra    → Perang Badr
Perang Badr           → Perang Badr Aisyah
Perang Badr Aisyah    → Fathul Makkah
Fathul Makkah         → Perang Uhud
Perang Uhud           → Perang Asafan
Perang Asafan         → Perang Khandaq
Perang Khandaq        → Perang Bani Mushthaliq
Perang Bani Mushthaliq → Perjanjian Hudaibiyah
Perjanjian Hudaibiyah → Perang Khaibar
Perang Khaibar        → Perang Dzatur Riqa'
Perang Dzatur Riqa'   → Perang Mu'tah
Perang Mu'tah         → Perang Hunain
Perang Hunain         → Perang Tha'if
Perang Tha'if         → Perang Tabuk
```

Membentuk timeline naratif Sirah Nabawiyah dari masa pra-kenabian hingga Perang Tabuk (tahun 9 H).

### 6.4 Manfaat di Neo4j

Dengan tambahan 4 tipe relasi ini, dimungkinkan query yang sebelumnya tidak bisa:

```cypher
// Silsilah keluarga Nabi Muhammad
MATCH p = (n:Person {name: "Muhammad"})-[:KELUARGA*1..3]-(m:Person)
RETURN p;

// Tokoh-tokoh yang pernah menjadi musuh lalu masuk Islam
MATCH (a:Person)-[:MUSUH]->(b:Person {name: "Muhammad"})
MATCH (a)-[:INVOLVED_IN]->(e:Event)
WHERE e.name CONTAINS "Fathul" OR e.name CONTAINS "Hunain"
RETURN DISTINCT a.name;

// Timeline event sebelum & sesudah Perang Badar
MATCH path = (e:Event {name: "Perang Badr"})-[:PRECEDES*1..3]-(other:Event)
RETURN path;
```

### 6.5 Validasi & Catatan Limitasi

**Hal yang sudah baik:**
- Pola `bin/binti` sangat akurat untuk relasi nasab (anak-orangtua) — sesuai konvensi Bahasa Arab dalam terjemahan.
- Rantai PRECEDES sesuai dengan timeline historis yang umum diketahui.
- Guard untuk perawi & substring-name efektif mencegah duplikasi & noise dari nama panjang.

**Limitasi yang perlu di-acknowledge:**
1. **False positive SAHABAT akibat kata "bersama"** — beberapa pasangan keliru dianggap sekutu padahal "bersama" merujuk konteks lain (contoh: "Bilal bin Rabah bergabung bersama Abu Thalib" — secara kronologis tidak mungkin). Solusi ke depan: tambah filter temporal/contextual.
2. **Relasi temporal belum di-handle** — Umar bin Khaththab tercatat sebagai MUSUH Muhammad (dari periode pra-Islam), tetapi setelah masuk Islam beliau adalah sahabat utama. KG saat ini tidak punya dimensi waktu pada relasi.
3. **PRECEDES terlalu kasar** — hanya berdasarkan urutan BAB, padahal beberapa BAB membahas event lintas tahun (misal BAB "Perjanjian Hudaibiyah" juga menyinggung pra-Hudaibiyah). Tidak ada perbedaan jarak waktu antar event.
4. **Pola regex masih bahasa Indonesia formal** — variasi seperti "kakanda", "putera", atau gaya bahasa lama belum tertangkap.

---

## 7. Langkah Berikutnya

1. **Validasi manual sample** — ambil 30 edge acak dari tiap tipe baru (10 KELUARGA, 10 SAHABAT, 10 MUSUH) dan cek manual di teks asli untuk hitung precision.
2. **Tambah filter temporal pada SAHABAT/MUSUH** — sebelum approve relasi, cek apakah kedua tokoh hidup di periode yang sama (manfaatkan `periode_bab` tokoh).
3. **Refine pola SAHABAT** — kata "bersama" terlalu generik; pertimbangkan ganti dengan pola lebih spesifik seperti "berjuang bersama", "berhijrah bersama", "bersama-sama membela".
4. **Setelah model NER final dijalankan** — re-run `build_person_person_relations()` pada hasil NER, bandingkan kuantitas & kualitas relasi.
5. **Lanjut ke section 4** — laporan Social Network Analysis (sesuai revisi poin 4) yang memanfaatkan relasi-relasi baru ini sebagai input graph.

---

## 8. File Terkait

| File | Deskripsi |
|---|---|
| `src/relation_extraction/relation_extraction.py` | Pipeline utama. Fungsi yang relevan: `build_person_person_relations()`, `build_event_chronology()` |
| `src/relation_extraction/period_mapping.py` | Penyedia event_period_map untuk PRECEDES |
| `data/result/relation_result/edges.csv` | Output. Kolom baru: `relation_subtype`. Tipe baru di `relation_type`: KELUARGA, SAHABAT, MUSUH, PRECEDES |
| `data/result/relation_result/nodes.csv` | Tidak berubah strukturnya — hanya jadi sumber daftar PERSON & EVENT untuk relasi baru |
