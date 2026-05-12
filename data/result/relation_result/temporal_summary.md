# Temporal Relations — Intra-Sentence Detection

Hasil deteksi temporal relations antar EVENT dalam satu kalimat menggunakan
pendekatan rule-based dengan temporal cues Bahasa Indonesia.

Metode mengikuti revisi Bu Diana cluster #1 (2026-05-03): *"Temporal dalam satu kalimat perlu di deteksi (bisa dilihat dari urutan kejadian di Sirah)"*.

## 1. Statistik Ekstraksi

| Metric | Count |
|---|---:|
| Total kalimat di chunks | 9835 |
| Kalimat dengan 2+ EVENT | 11 |
| Kalimat dengan temporal cue | 4 |
| Raw relations diekstrak | 4 |
| Unique relations setelah dedup | 3 |
| PRECEDES intra-sentence | 1 |
| CONCURRENT (relasi baru) | 2 |

## 2. Comparison: Intra-Sentence vs Page-Order PRECEDES

PRECEDES sebelumnya dibangun dari **urutan halaman BAB** (page-order chronology).
Sekarang ditambahkan PRECEDES dari **kalimat eksplisit** (intra-sentence).

| Source | Count | Catatan |
|---|---:|---|
| Page-order PRECEDES (existing edges_v2.csv) | 12 | Berbasis page_start event |
| Intra-sentence PRECEDES (new) | 1 | Berbasis cue "sebelum/setelah/kemudian" |
| **Intersection** (kedua metode confirm) | **1** | Strong evidence — multi-source |
| Only intra-sentence (NEW finding) | 0 | Tidak terdeteksi page-order — kemungkinan event dalam BAB sama |
| Only page-order (uncovered by sentence) | 11 | Tidak ada kalimat eksplisit yang link 2 event ini |

### 2.1 Confirmed by both methods (top 10)

- `Perjanjian Hudaibiyah` → `Perang Khaibar`

## 3. Top 15 by Frequency

| Source | Relation | Target | Freq | Cue Words |
|---|---|---|---:|---|
| Perang Hunain | CONCURRENT | Perang Uhud | 2 | pada saat |
| Perang Badr | CONCURRENT | Perang Uhud | 1 | saat |
| Perjanjian Hudaibiyah | PRECEDES | Perang Khaibar | 1 | sebelum |

## 4. Cue Type Distribution

| Cue Type | Count |
|---|---:|
| during | 2 |
| before | 1 |

## 5. Limitasi & Catatan

- **Rule-based**: tidak handle anaphora atau coreference (mis. "setelah itu" yang merujuk event di kalimat sebelumnya).
- **Word-boundary match**: event yang nama-nya substring dari event lain (mis. "Perang Badr" vs "Perang Badr Kubra") di-handle via length-sorted regex.
- **Cue ambiguous**: "setelah" vs "setelah itu" — "setelah itu" dipetakan sebagai "then" (urutan event implicit), "setelah" sebagai "after" (inverted). Aturan ini dipakai supaya "X setelah itu Y" tidak salah interpretasi.
- **Event vocab**: pakai 36 EVENT dari nodes_v2.csv post-review. Event noise/ambigu sudah di-R sebelumnya.
- **No confidence score** sementara — tiap relasi dianggap valid kalau cue + 2 events match. Future: tambah skor confidence berdasarkan jumlah cue alternatif atau parse tree.

## 6. Integrasi ke Knowledge Graph

Hasil ini bisa di-merge ke `edges_v2.csv` sebagai tambahan relasi PRECEDES & CONCURRENT.
Rekomendasi: gunakan **union** dari page-order dan intra-sentence PRECEDES untuk maximum recall,
dengan kolom `source_method` untuk track asal-usul relasi.

File source: `temporal_relations.csv` (3 unique relations)