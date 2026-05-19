# Skenario Temporal Detection — Hybrid Pattern + Bab + Position

**Tanggal:** 2026-05-06
**Konteks:** Menjawab revisi Bu Diana di `../bimbingan/revisi_dosen.md` (cluster #1):
> *"Temporal dalam satu kalimat (?) perlu di deteksi (bisa dilihat dari urutan kejadian di Sirah / urutan bab nya)"*
>
> *"Lalu pembentukan graf, memperhatikan Temporal waktu, baru ke fitur graf nya"*

Dokumen ini = **bahan diskusi** sebelum implementasi. Setelah disetujui Bu Diana, skenario yang dipilih akan diintegrasikan ke `src/relation_extraction/relation_extraction.py`.

> **Ruang lingkup:** TA fokus pada **3 sumber sinyal temporal** (pattern matching, urutan bab, posisi token) yang digabung secara berlapis (hybrid). Pendekatan dependency parsing **TIDAK dipakai** karena parser Bahasa Indonesia kualitasnya terbatas + effort tinggi.

---

## 1. Masalah yang ingin dipecahkan

### 1.1 Status saat ini (sebelum temporal detection)

Pipeline relation extraction Sirah saat ini menggunakan:
- **Proximity score** — relasi terbentuk berdasarkan jarak antar token dalam chunk (tidak ada urutan)
- **Period mapping** — `period_mapping.py` map EVENT → BAB utama (level bab, bukan kalimat)

**Outputnya:** `edges.csv` punya kolom `weight` (proximity + period score), tapi **tidak ada urutan kronologis** antar entitas/event.

### 1.2 Contoh problem konkret

Kalimat dari Sirah:
> *"Setelah Perang Badar, Rasulullah kembali ke Madinah dan bertemu Abu Bakar."*

Saat ini menghasilkan:
| source | target | relation | weight |
|---|---|---|---|
| Rasulullah | Perang Badar | INVOLVED_IN | 0.85 |
| Perang Badar | Madinah | OCCURRED_AT | 0.70 |
| Rasulullah | Abu Bakar | (proximity) | 0.65 |

**Yang hilang:** urutan kronologis. Pertemuan Rasulullah-Abu Bakar terjadi **SETELAH** Perang Badar, tapi info ini hilang. Kata "Setelah" yang ada di kalimat **tidak dimanfaatkan**.

### 1.3 Apa yang Bu Diana minta

> *"graf harus memperhatikan temporal waktu, baru ke fitur graf nya"*

Implikasi konkret:
1. Tiap edge harus punya **urutan temporal** (sebelum/sesudah/bersamaan)
2. Sumber sinyal: **kalimat itu sendiri** (kata penghubung) + **urutan bab buku**
3. Pembentukan graf **bertahap**: build chronology dulu, baru centrality/community/dll.

---

## 2. Pendekatan kandidat (review)

### 2.A Pattern Matching (rule-based) — Bahasa Indonesia

Deteksi kata kunci temporal di kalimat dan terapkan aturan urutan.

**Pro:**
- Cepat implementasi (~1-2 hari)
- Transparan, mudah dijelaskan
- Match persis permintaan Bu Diana ("temporal **dalam satu kalimat**")
- Bahasa Indonesia narrative formal (Sirah) punya pattern konsisten

**Kontra:**
- Terbatas pada pattern eksplisit
- Kalimat tanpa kata kunci → tidak ter-handle
- Pattern ambigu (e.g., "sambil" bisa parallel atau urutan)

**Coverage estimasi (Sirah):** ~30-40% pasangan event/entitas

### 2.B Urutan Bab (book-level chronology)

Pakai `toc_groundtruth.json` + `period_mapping.py` (sudah ada). Asumsi: BAB 5 mendahului BAB 12 secara kronologis.

**Status:** sudah ada infrastructure, perlu fix mapping yang salah (lihat `event_period_review.csv`).

**Pro:**
- Sudah ada di codebase
- Reliable: urutan bab di Sirah = urutan kronologis sebenarnya
- Coverage tinggi (semua event yang ter-map ke bab)

**Kontra:**
- Coarse-grained (level bab, bukan kalimat)
- Event dalam 1 bab tidak ter-bedakan urutannya

**Coverage estimasi:** ~50-60% (after period mapping fix)

### 2.C Dependency Parsing — **TIDAK DIPAKAI**

Pakai parser Bahasa Indonesia (Stanza, UDPipe-id) untuk analisis sintaksis. Identifikasi: subject-verb-object, advcl (adverbial clause), conj, dll.

**Kenapa tidak dipakai:**
- Parser Bahasa Indonesia kualitasnya **~80% akurasi** (vs English ~95%)
- Domain narasi sejarah Arab-Indonesia bukan training data parser umum
- Implementasi rumit, debug sulit
- Effort ~1 minggu tanpa jaminan hasil signifikan

> Disimpan sebagai **alternative untuk future improvement**, bukan dalam scope TA ini.

### 2.D Position-based (default fallback)

Kalau dalam 1 chunk ada multiple events tanpa kata kunci, pakai urutan posisi (kiri ke kanan).

**Pro:**
- Paling simpel, fallback bagus
- Cocok untuk narasi linier (mayoritas Sirah)

**Kontra:**
- Asumsi linear order — tidak selalu benar (flashback/anachronism narrative)

**Coverage estimasi:** ~10-20% (residual setelah A dan B)

---

## 3. Skenario terpilih: **Hybrid Layered (A + B + D)**

### 3.1 Algoritma

Untuk setiap **pasangan entitas (e1, e2)** dalam graf, tentukan urutan temporal melalui 3 lapisan prioritas:

```
def detect_temporal_order(e1, e2, sentence_context, chunk_context):
    
    # LAPISAN 1: Pattern matching di kalimat (highest priority)
    cue = find_temporal_cue(sentence_context, e1, e2)
    if cue is not None:
        return {
            "relation":   cue.relation,    # BEFORE / AFTER / CONCURRENT
            "source":     "pattern",
            "confidence": 0.9,
            "trigger":    cue.keyword,     # contoh: "setelah", "lalu"
        }
    
    # LAPISAN 2: Urutan bab (kalau di bab berbeda)
    bab_e1 = get_bab(e1)  # via event_period_manual.json
    bab_e2 = get_bab(e2)
    if bab_e1 and bab_e2 and bab_e1.page_start != bab_e2.page_start:
        return {
            "relation":   "BEFORE" if bab_e1.page_start < bab_e2.page_start else "AFTER",
            "source":     "chapter",
            "confidence": 0.7,
            "trigger":    f"bab {bab_e1.title} vs {bab_e2.title}",
        }
    
    # LAPISAN 3: Position-based (fallback)
    if e1.start_char < e2.start_char:
        return {
            "relation":   "BEFORE",
            "source":     "position",
            "confidence": 0.3,
            "trigger":    "left-to-right order",
        }
    else:
        return {
            "relation":   "AFTER",
            "source":     "position",
            "confidence": 0.3,
            "trigger":    "left-to-right order",
        }
```

### 3.2 Output yang ditambahkan ke `edges.csv`

| Kolom baru | Tipe | Contoh |
|---|---|---|
| `temporal_relation` | string | `BEFORE` / `AFTER` / `CONCURRENT` / `UNKNOWN` |
| `temporal_source` | string | `pattern` / `chapter` / `position` |
| `temporal_confidence` | float | 0.3 - 0.9 |
| `temporal_trigger` | string | "setelah" / "bab vs bab" / "left-to-right" |

### 3.3 Confidence value

| Source | Confidence | Alasan |
|---|---:|---|
| `pattern` | 0.9 | Eksplisit dari kalimat — paling reliable |
| `chapter` | 0.7 | Reliable di level bab, tapi tidak granular |
| `position` | 0.3 | Heuristik lemah, asumsi linear narrative |

> **Catatan:** kalau Bu Diana minta cuma 1 source dipakai (bukan hybrid), lihat §6 (pertanyaan klarifikasi).

---

## 4. Pattern Temporal Bahasa Indonesia (untuk Lapisan 1)

### 4.1 Daftar pattern yang akan dipakai

Disusun berdasarkan diksi formal Bahasa Indonesia yang umum di Sirah Nabawiyah:

#### Group A — BEFORE/AFTER explicit
| Pattern (regex) | Relation antar e1, e2 | Contoh kalimat |
|---|---|---|
| `\bsebelum\s+` | "sebelum e1, e2" → e2 → e1 | *"Sebelum hijrah, Nabi berdakwah secara sembunyi-sembunyi"* |
| `\bsetelah\s+` | "setelah e1, e2" → e1 → e2 | *"Setelah Perang Badar, kaum Muslim semakin kuat"* |
| `\bsesudah\s+` | sama dengan setelah | *"Sesudah hijrah, dibangun masjid Quba"* |
| `\busai\s+` | sama dengan setelah | *"Usai perang, beliau pulang ke Madinah"* |
| `\bsebelumnya\b` | "Y, sebelumnya X" → X → Y | *"Beliau berhijrah; sebelumnya berdakwah di Makkah"* |
| `\bsetelahnya\b` | "X, setelahnya Y" → X → Y | *"Perang Badar, dan setelahnya Perang Uhud"* |

#### Group B — Succession / sequence
| Pattern | Relation | Contoh |
|---|---|---|
| `\blalu\b` | e1 → e2 | *"Beliau hijrah, lalu membangun masjid"* |
| `\bkemudian\b` | e1 → e2 | *"Pertama-tama berdakwah, kemudian berhijrah"* |
| `\bselanjutnya\b` | e1 → e2 | *"Beliau menang, selanjutnya pulang"* |
| `\btak lama kemudian\b` | e1 → e2 (close) | *"Hijrah tiba, tak lama kemudian lahirlah madrasah Madinah"* |
| `\bakhirnya\b` | e1 → e2 (final) | *"Setelah lama berjuang, akhirnya menang"* |
| `\bberikutnya\b` | e1 → e2 | *"Tahun berikutnya terjadi Perang Uhud"* |

#### Group C — Concurrent / co-temporal
| Pattern | Relation | Contoh |
|---|---|---|
| `\bsambil\b` | e1 = e2 (concurrent) | *"Beliau berdoa sambil menunggu wahyu"* |
| `\bketika\s+` | e1 = e2 atau e1 → e2 | *"Ketika hijrah, beliau didampingi Abu Bakar"* |
| `\bsaat\s+` | e1 = e2 | *"Saat Perang Badar, jumlah Muslim 313 orang"* |
| `\btatkala\s+` | e1 = e2 | *"Tatkala fajar menyingsing, perang dimulai"* |
| `\bbersamaan\b` | e1 = e2 | *"Wahyu turun bersamaan dengan kelahiran Hasan"* |
| `\bkala itu\b` | reference to current time | *"Kala itu, masyarakat Madinah masih terbagi"* |
| `\bsaat itu juga\b` | e1 = e2 (instantaneous) | *"Saat itu juga, beliau berdoa"* |

#### Group D — Absolute time anchors
| Pattern | Tindakan | Contoh |
|---|---|---|
| `\bpada\s+(hari\|tahun\|bulan)\s+\w+` | Tag sebagai TIME absolute | *"Pada tahun ke-13 dari kenabian"* |
| `\btahun\s+\d+\s*H\b` | Tag sebagai TIME absolute | *"tahun 2 H"* |
| `\bbulan\s+(Rabiul\|Ramadhan\|Syawal\|...)\b` | Tag sebagai TIME absolute | *"bulan Ramadhan"* |
| `\b(awal\|akhir\|pertengahan)\s+(tahun\|bulan)\b` | Tag fuzzy time | *"awal tahun"* |

#### Group E — Negation/Exception (handle dengan hati-hati)
| Pattern | Catatan |
|---|---|
| `\btidak sebelum\b`, `\bbukan setelah\b` | Negasi — bisa membatalkan inference |
| `\bbahkan sebelum\b` | Penekanan, biasanya BEFORE valid |

### 4.2 Algoritma matching pattern

```python
def find_temporal_cue(sentence: str, e1_pos: int, e2_pos: int):
    """
    Cari kata kunci temporal di kalimat yang relevan dengan pasangan (e1, e2).
    Kata kunci HARUS posisinya di antara atau dekat dengan e1/e2.
    
    Return: TemporalCue(relation, keyword, confidence) atau None
    """
    # Iterasi tiap group pattern
    for group, patterns in TEMPORAL_PATTERNS.items():
        for regex, relation_fn in patterns:
            for match in re.finditer(regex, sentence, re.IGNORECASE):
                cue_pos = match.start()
                # Check kalau cue posisinya antara e1 dan e2 (atau dekat)
                e_min, e_max = min(e1_pos, e2_pos), max(e1_pos, e2_pos)
                if e_min - 50 < cue_pos < e_max + 50:
                    rel = relation_fn(e1_pos, e2_pos, cue_pos)
                    return TemporalCue(relation=rel, keyword=match.group(), confidence=0.9)
    
    return None
```

### 4.3 Pattern yang TIDAK dipakai (perlu hati-hati)

| Pattern | Alasan tidak dipakai |
|---|---|
| `\b(dulu\|dahulu)\b` | Ambigu — bisa berarti "before" atau idiom ("zaman dahulu") |
| `\bnanti\b` | Future tense, jarang di narasi historis |
| `\bsebenarnya\b` | Bukan temporal, marker discourse |

---

## 5. Eksperimen Validasi

### 5.1 T1 — Pattern matching only (validasi precision)

**Tujuan:** ukur akurasi pattern matching saja (Lapisan 1).

**Setup:**
- Sample 30-50 kalimat dari Sirah yang mengandung minimal 1 kata kunci temporal
- Apply pattern detection → keluar prediction (BEFORE/AFTER/CONCURRENT)
- Manual verification: berapa% prediction yang benar

**Metrik:**
- Precision per group (A/B/C/D)
- Confusion matrix (BEFORE/AFTER/CONCURRENT/UNKNOWN)

**Target:** precision ≥ 80% per group (acceptable untuk narasi formal)

### 5.2 T2 — Hybrid coverage analysis

**Tujuan:** ukur berapa% pasangan event/entitas di graf yang dapat sinyal temporal.

**Setup:**
- Run hybrid (A + B + D) pada seluruh `edges.csv`
- Hitung distribusi `temporal_source`:
  - % pattern (Lapisan 1)
  - % chapter (Lapisan 2)
  - % position (Lapisan 3)
  - % UNKNOWN

**Target:** coverage ≥ 95% (sisa UNKNOWN dihandle sebagai missing data)

### 5.3 T3 — Studi kasus: Perang Badr (sesuai revisi Bu Diana)

**Tujuan:** validasi end-to-end dengan event anchor.

**Setup:**
- Ambil 1 anchor event: **Perang Badar** (`Perang Badr Kubra`)
- Cari semua entitas yang relasi dengan Perang Badar
- Susun timeline kronologis pakai temporal detection
- Visualisasi: timeline + sub-graph

**Hasil yang diharapkan:**
```
Sebelum Perang Badar:
  - Hijrah ke Madinah
  - Pengiriman utusan
  - Persiapan pasukan

Saat Perang Badar:
  - Pertempuran
  - Tokoh terlibat: Muhammad, Abu Bakar, Umar, Hamzah, Abu Jahal, ...

Setelah Perang Badar:
  - Pulang ke Madinah
  - Pembagian harta rampasan
  - Perang Uhud (next major event)
```

### 5.4 T4 — Comparison: tanpa temporal vs dengan temporal

**Tujuan:** ukur dampak temporal pada SNA fitur graf.

**Setup:**
- Run SNA dengan graf saat ini (tanpa temporal)
- Run SNA dengan graf yang temporal-aware (filter edge berdasarkan urutan)
- Bandingkan: PageRank, betweenness centrality, community detection

**Metrik:**
- Apakah ranking tokoh berubah?
- Apakah komunitas berubah?

---

## 6. Implementasi

### 6.1 File yang berubah / ditambah

| File | Tindakan |
|---|---|
| `src/relation_extraction/temporal_detection.py` | **Baru** — fungsi `detect_temporal_order()` + pattern definitions |
| `src/relation_extraction/relation_extraction.py` | Modify — call `detect_temporal_order()` untuk tiap edge |
| `src/relation_extraction/period_mapping.py` | Sudah ada — pakai `event_period_manual.json` (hasil review) |
| `data/result/relation_result/edges.csv` | Schema update — tambah 4 kolom temporal_* |

### 6.2 Estimasi effort

| Tahap | Estimasi |
|---|---|
| Pattern definition (Group A-E) | 4 jam |
| `detect_temporal_order()` implementation | 4 jam |
| Integration ke `relation_extraction.py` | 2 jam |
| T1 validation (manual review 30-50 kalimat) | 4 jam |
| T2 coverage analysis | 1 jam |
| T3 studi kasus Perang Badar | 3 jam |
| T4 comparison SNA | 2 jam |
| **Total** | **~20 jam** (3-4 hari kerja) |

### 6.3 Prasyarat sebelum coding

1. ✅ EVENT-BAB chronology mapping sudah benar (`event_period_review.csv` sudah di-apply)
2. ⏳ Approval Bu Diana untuk scope hybrid (A + B + D)
3. ⏳ Konfirmasi Bu Diana: sudah cukup atau perlu eksperimen tambahan?

---

## 7. Referensi Paper Pendukung

Paper untuk justifikasi metodologi di Bab 2/3 laporan TA. Dikelompokkan ke 3 grup.

### 7.A Temporal Information Extraction (TIE) — General

#### A.1 — TimeML & TIMEX3 specification
- **Penulis:** Pustejovsky et al., 2003 (TimeML); ISO-TimeML standard
- **Link:** https://catalog.ldc.upenn.edu/LDC2006T08 (TimeBank corpus)
- **Inti:** Standard annotation untuk temporal expressions (TIMEX3) dan temporal relations (TLINK). Define BEFORE/AFTER/SIMULTANEOUS/INCLUDES/dll.
- **Plus untuk Sirah:** Framework standar yang bisa diadopsi untuk relation labels (BEFORE/AFTER/CONCURRENT)

#### A.2 — Temporal Relation Extraction Survey
- **Penulis:** Zhou & Chen, 2024 (NAACL Findings)
- **Link:** https://aclanthology.org/2024.findings-naacl.187/
- **Inti:** Survey komprehensif TIE methods: rule-based, ML-based, transformer-based.
- **Plus untuk Sirah:** Justifikasi pemilihan rule-based untuk Bahasa Indonesia (low-resource)

### 7.B Indonesian Temporal Processing

#### B.1 — Indonesian Temporal Tagging
- **Penulis:** Mahendra et al., 2018 (PACLIC)
- **Link:** https://aclanthology.org/Y18-1062/
- **Inti:** Annotation guidelines untuk temporal expressions di Bahasa Indonesia. Membahas pattern "tahun X H", "bulan Rabiul Awwal", dll.
- **Plus untuk Sirah:** Direkomendasikan untuk Group D (absolute time anchors)

#### B.2 — UD Indonesian Treebank
- **Penulis:** Alfina et al., 2019
- **Link:** https://universaldependencies.org/treebanks/id_gsd/
- **Inti:** Universal Dependencies parser untuk Indonesian. Berisi adverbial clauses (`advcl`), temporal modifiers (`obl:tmod`).
- **Plus untuk Sirah:** Disebut sebagai alternative metode (Opsi C) yang TIDAK dipakai, tapi disitir sebagai pembanding.

### 7.C Event Ordering in Narrative Texts

#### C.1 — Event Coreference & Ordering in Historical Narrative
- **Penulis:** Cassidy & Bethard, 2017
- **Link:** https://aclanthology.org/D17-1284/
- **Inti:** Event ordering di teks naratif sejarah. Pattern matching untuk kata kunci urutan.
- **Plus untuk Sirah:** Domain dekat (narasi sejarah), pattern dapat diadaptasi.

#### C.2 — Narrative Schema Induction
- **Penulis:** Chambers & Jurafsky, 2008 (ACL)
- **Link:** https://aclanthology.org/P08-1090/
- **Inti:** Induksi event sequence dari narasi.
- **Plus untuk Sirah:** Foundation paper untuk event ordering.

### 7.D Mapping Paper ⇄ Skenario

| Komponen | Paper Rujukan |
|---|---|
| Pattern matching (Lapisan 1) | C.1 (Cassidy 2017) + B.1 (Mahendra 2018) |
| Annotation framework (relation labels) | A.1 (TimeML) |
| Justifikasi rule-based for low-resource | A.2 (Zhou 2024) |
| Bab-level chronology (Lapisan 2) | C.2 (Chambers 2008) — narrative schema |
| Indonesian context | B.1 (Mahendra) + B.2 (UD-id, sebagai comparison) |

### 7.E Top 4 Sitasi Prioritas

Kalau Bab 2 sub-bab temporal terbatas:
1. **A.1 — TimeML** ⭐⭐⭐ — framework standard, wajib disitir
2. **B.1 — Mahendra 2018** ⭐⭐ — Bahasa Indonesia specific
3. **A.2 — Zhou 2024** ⭐⭐ — survey TIE, justifikasi metode
4. **C.1 — Cassidy 2017** ⭐ — narrative event ordering

---

## 8. Pertanyaan & Bahan Diskusi untuk Bu Diana

### 8.1 Pertanyaan klarifikasi (sebelum coding)

1. **Setuju dengan scope hybrid (A + B + D)?** Atau Ibu mau saya pakai 1 sumber saja (mis. cuma pattern, atau cuma bab)?
2. **Dependency parsing (Opsi C) di-skip** — Ibu setuju atau perlu coba juga sebagai pembanding?
3. **Confidence values** — saya pakai 0.9/0.7/0.3 untuk pattern/chapter/position. Ibu mau threshold lain?
4. **Relation labels** — saya pakai 4 label (BEFORE/AFTER/CONCURRENT/UNKNOWN). Cukup atau perlu lebih granular (mis. INCLUDES/OVERLAPS dari TimeML)?
5. **Pattern Bahasa Indonesia** — list ~30 pattern di §4.1 sudah cukup atau Ibu mau saya tambah lagi?
6. **Output ke `edges.csv`** — 4 kolom baru (`temporal_relation`, `temporal_source`, `temporal_confidence`, `temporal_trigger`) cukup atau perlu lebih?

### 8.2 Pertanyaan strategis

7. **Validasi T1 (precision)** — sample 30-50 kalimat. Ibu mau saya tunjukkan ground truth-nya juga, atau cukup precision number?
8. **Studi kasus T3 (Perang Badar)** — selaras dengan revisi #2 Ibu (sampling event). Akan di-merge ke `graf_pengujian.md` G4, atau dipisah?
9. **Posisi di laporan TA** — sub-bab Bab 3 (metodologi temporal) + tabel hasil di Bab 4? Atau sub-bab tersendiri?

### 8.3 Bahan diskusi dengan rujukan paper

Saat konsultasi, paper di §7 bisa dipakai untuk:
- **Justifikasi pattern matching:** rujuk C.1 (Cassidy 2017) untuk narrative + B.1 (Mahendra 2018) untuk Indonesian
- **Justifikasi rule-based vs ML:** rujuk A.2 (Zhou 2024) — survey menunjukkan rule-based masih kompetitif untuk low-resource language
- **Justifikasi label scheme:** rujuk A.1 (TimeML) — standard yang sudah established

---

## 9. Output yang diharapkan

Setelah implementasi selesai:

### 9.1 Tabel hasil utama (Bab 4)

**Coverage analysis:**

| Source | n_edges | % | confidence avg |
|---|---:|---:|---:|
| pattern  | ? | ? | 0.9 |
| chapter  | ? | ? | 0.7 |
| position | ? | ? | 0.3 |
| unknown  | ? | ? | - |

**Precision per pattern group (T1):**

| Group | n_sample | n_correct | precision |
|---|---:|---:|---:|
| A (BEFORE/AFTER explicit) | ? | ? | ? |
| B (Succession) | ? | ? | ? |
| C (Concurrent) | ? | ? | ? |
| D (Absolute time) | ? | ? | ? |

### 9.2 Visualisasi

1. **Timeline Perang Badar** — kronologi event pre/during/post Badar (T3)
2. **Sub-graph temporal-aware** — filter graf hanya pre-Badar atau hanya post-Badar
3. **Distribusi temporal_source** — pie chart % pattern/chapter/position

### 9.3 Integrasi pipeline

- `edges.csv` ter-update dengan 4 kolom temporal_*
- Neo4j Cypher import ter-update untuk include temporal properties
- SNA bisa di-filter berdasarkan temporal range (mis. cuma analisis era Madinah)

---

## 10. Hubungan dengan revisi Bu Diana yang lain

Skenario temporal ini **prasyarat** untuk:

1. **Revisi #2 (Sampling event)** — studi kasus Perang Badar, Hijrah, dst. Tanpa temporal, sub-graph studi kasus tidak punya urutan.
2. **Revisi #4 (Graph metrics)** — community detection bisa di-evaluasi per era temporal (sebelum hijrah, era Madinah, era Fathu Makkah).

**Urutan kerja yang disarankan:**
1. ✅ Skenario SRL-NER (sudah ACC)
2. ⏳ Skenario Graf (tunggu ACC)
3. ⏳ Skenario Temporal **(dokumen ini)** — ACC dulu sebelum coding
4. Implementasi temporal (~20 jam)
5. Re-run relation extraction dengan temporal-aware
6. Re-run SNA + studi kasus dengan graf yang sudah temporal-aware

---

## 11. Status

- 📝 **Dokumen ini** — draft 2026-05-06, menunggu approval Bu Diana
- 🔄 **EVENT-BAB chronology fix** — sedang di-review (`event_period_review.csv`)
- ⏳ **Implementasi** — belum mulai, menunggu approval scope

**Catatan untuk konsultasi:** dokumen ini bisa dipakai paralel dengan hasil S1/S2 SRL-NER. Bu Diana akan melihat 2 progress: hasil eksperimen NER + dokumen perencanaan temporal.
