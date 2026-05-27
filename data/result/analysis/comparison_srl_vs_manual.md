# Comparison Report — SRL-NER (S3.2 v3) vs Manual Labelling

**Tanggal:** 2026-05-28

**Latar belakang:** Revisi Bu Diana 2026-05-16 — pipeline running end-to-end dengan output SRL-NER, comparison report SRL-NER vs manual labelling.

**Sumber data:**
- Manual labelling : `data/result/manual_labelling/sirah_prelabelled.csv` (regex + keyword pre-labelling)
- NER inference v3 : `data/result/manual_labelling/sirah_prelabelled_v3.csv` (model S3.2-scl-aug-iter4 winner, F1 entity 0.9537 di test set)

## Disclaimer Penting

Manual labelling **bukan ground truth absolut**. Manual dikerjakan via regex + keyword matching (`pre_labelling.py`), yang punya bias:
- Hanya match pattern yang sudah didefinisikan (mis. "bin/binti" untuk PERSON)
- Banyak entity valid yang ke-skip karena tidak ada pattern matching
- Tidak konsisten penanganan boundary entity

Sehingga **"missed by NER"** (FN) bisa berarti:
- (a) NER beneran missed entity yang seharusnya di-detect, ATAU
- (b) Manual over-detect via regex agresif, NER skip karena confidence rendah

Demikian juga **"extra by NER"** (FP) bisa berarti:
- (a) NER false positive (over-detection), ATAU
- (b) Entity valid yang manual ke-skip karena tidak ada pattern

## Cakupan

- Common chunks (di kedua dataset)  : **800**
- Only-manual chunks               : 1 (manual punya, NER tidak)
- Only-NER chunks (extra coverage) : **241** (NER tambah 241 chunks yang manual tidak label)

NER v3 cover **1041** chunks vs manual 801 chunks (+240 chunks).

## Hasil Perbandingan Per-Label (Common Chunks Saja)

Manual treated as reference. Per-label entity-level matching dengan normalisasi (lower-case, strip whitespace + punctuation).

| Label | Manual | NER v3 | TP | FN | FP | FP partial | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PERSON | 2814 | 2850 | 2770 | 44 | 80 | 27 | 0.9719 | 0.9844 | 0.9781 |
| LOCATION | 957 | 973 | 941 | 16 | 32 | 1 | 0.9671 | 0.9833 | 0.9751 |
| EVENT | 159 | 161 | 147 | 12 | 14 | 7 | 0.9130 | 0.9245 | 0.9187 |
| TIME | 273 | 280 | 256 | 17 | 24 | 16 | 0.9143 | 0.9377 | 0.9259 |
| **MICRO** | 4203 | 4264 | 4114 | 89 | 150 | — | **0.9648** | **0.9788** | **0.9718** |

**Catatan kolom:**
- `Manual` / `NER v3`: jumlah unique entity per label di common chunks
- `TP` (True Positive): entity sama persis di kedua dataset
- `FN` (False Negative): di manual, tidak di NER (missed by NER)
- `FP` (False Positive): di NER, tidak di manual (extra by NER)
- `FP partial`: subset FP yang punya partial match dengan FN — biasanya boundary mismatch (mis. "Abu Bakar" vs "Abu Bakar Ash-Shiddiq"), bukan true false positive
- Precision = TP / (TP + FP), Recall = TP / (TP + FN)

## Interpretasi Hasil

- Recall PERSON = 0.984 — moderate-good.
- **Precision PERSON tinggi (0.972)** — NER prediksi PERSON terpercaya.
- **EVENT detection**: NER 161 unique vs manual 159 unique. F1 = 0.919.
- **LOCATION**: F1 = 0.975.
- **TIME**: F1 = 0.926.

**Coverage sebagai keuntungan utama NER:**
- Manual cover 801 chunks (regex tidak cukup pattern).
- NER cover 1041 chunks (full coverage corpus 1094).
- NER tambah **241 chunks** yang manual tidak label sama sekali.
- Implikasi: KG v3 (build from NER) lebih lengkap dari KG v2 (build from manual).

## Sample Misclassifications

5 contoh per kategori per label di `data/result/analysis/comparison_misclassified_samples.csv`. Untuk error analysis manual.

### PERSON

**missed_by_NER** (10 total, top 5):
- `abul muluk` (chunk 000002-003)  ↔ manual: `nan`
- `dar bin qushay` (chunk 000002-011)  ↔ manual: `nan`
- `isa` (chunk 000004-003)  ↔ manual: `nan`
- `dzu nuwas` (chunk 000004-003)  ↔ manual: `nan`
- `ma'ad bin bagian` (chunk 000016-001)  ↔ manual: `nan`

**extra_by_NER** (10 total, top 5):
- `ya'rub` (chunk 000002-001)
- `isma` (chunk 000002-008)
- `lyas bin qubaishah` (chunk 000005-003)
- `shalallahu alaihi wa` (chunk 000010-002)
- `habasyah` (chunk 000010-014)

**partial_match_NER** (10 total, top 5):
- `abdud-dar bin qushay` (chunk 000002-011)  ↔ manual: `dar bin qushay`
- `ma'ad bin` (chunk 000016-001)  ↔ manual: `ma'ad bin bagian`
- `hasyim bin abdu manaf` (chunk 000017-001)  ↔ manual: `hasyim bin abdu`
- `abu dzu-` (chunk 000019-005)  ↔ manual: `abu dzu- aib`
- `al-arqam bin abil-arqam` (chunk 000039-002)  ↔ manual: `al-arqam bin abil`

### LOCATION

**missed_by_NER** (10 total, top 5):
- `habasyah` (chunk 000010-014)  ↔ manual: `nan`
- `dzil-majaz` (chunk 000014-001)  ↔ manual: `nan`
- `majinnah` (chunk 000014-001)  ↔ manual: `nan`
- `ukazh` (chunk 000014-001)  ↔ manual: `nan`
- `habasyah` (chunk 000017-008)  ↔ manual: `nan`

**extra_by_NER** (10 total, top 5):
- `india` (chunk 000001-002)
- `timur tengah` (chunk 000001-002)
- `bahrain` (chunk 000002-003)
- `baitul-haram` (chunk 000002-005)
- `arab` (chunk 000004-003)

**partial_match_NER** (1 total, top 5):
- `dzul marwah` (chunk 000301-001)  ↔ manual: `marwah`

### EVENT

**missed_by_NER** (10 total, top 5):
- `hijrah` (chunk 000002-002)  ↔ manual: `nan`
- `hijrah` (chunk 000051-006)  ↔ manual: `nan`
- `isra` (chunk 000080-002)  ↔ manual: `nan`
- `hijrah` (chunk 000089-001)  ↔ manual: `nan`
- `perang badr aisyah` (chunk 000098-002)  ↔ manual: `nan`

**extra_by_NER** (7 total, top 5):
- `malam` (chunk 000035-002)
- `perang al-yamamah` (chunk 000138-002)
- `perang as-sawiq` (chunk 000153-002)
- `perjanjian hudaibiyah` (chunk 000223-005)
- `perjanjian hudaibiyah` (chunk 000247-001)

**partial_match_NER** (7 total, top 5):
- `perang badr` (chunk 000098-002)  ↔ manual: `perang badr aisyah`
- `perang badr` (chunk 000098-003)  ↔ manual: `perang badr aisyah`
- `perang badr` (chunk 000114-013)  ↔ manual: `perang badr beberapa`
- `jabal uhud` (chunk 000157-003)  ↔ manual: `perang uhud jabal`
- `perang uhud` (chunk 000157-003)  ↔ manual: `perang uhud jabal`

### TIME

**missed_by_NER** (10 total, top 5):
- `tanggal 9 rabi` (chunk 000018-001)  ↔ manual: `nan`
- `malam tanggal 21 dari bulan ramadhan` (chunk 000032-001)  ↔ manual: `nan`
- `pertengahan hari-hari tasyriq` (chunk 000084-001)  ↔ manual: `nan`
- `tanggal 12 september` (chunk 000090-002)  ↔ manual: `nan`
- `tahun 622 m` (chunk 000090-002)  ↔ manual: `nan`

**extra_by_NER** (8 total, top 5):
- `bulan dzul-` (chunk 000026-001)
- `bulan` (chunk 000032-002)
- `hari jum'at` (chunk 000104-001)
- `bulan 213` (chunk 000224-001)
- `bulan rabi'ul 4` (chunk 000285-006)

**partial_match_NER** (10 total, top 5):
- `tanggal 9 rabi'ul` (chunk 000018-001)  ↔ manual: `tanggal 9 rabi`
- `tanggal 21` (chunk 000032-001)  ↔ manual: `malam tanggal 21 dari bulan ramadhan`
- `hari-hari tasyriq` (chunk 000084-001)  ↔ manual: `pertengahan hari-hari tasyriq`
- `tahun 622` (chunk 000090-002)  ↔ manual: `tahun 622 m`
- `tanggal 12` (chunk 000090-002)  ↔ manual: `tanggal 12 september`

## Kesimpulan

1. **Coverage NER lebih luas**: 1041 chunks vs manual 801 (+241 only-NER chunks).
2. **Micro F1 entity = 0.9718** di common chunks.
3. NER bukan untuk replace manual, tapi untuk **scale-up coverage** dari ~600 chunks manual ke 1094 chunks full.
4. Manual masih bermanfaat untuk **anchor entity high-precision** di subset yang ke-curate.
5. KG v3 yang dibangun dari NER inference punya 1280 nodes (vs 892 v2 manual) dan 491 edges (vs 322 v2) — graf lebih lengkap.
