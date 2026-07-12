# Skenario G7 & G8 — Hasil (KG v3 cleaned)

> Dihasilkan oleh `src/analysis/scenario_g7_g8.py`. Sumber: `nodes_v3.csv` + `edges_v3.csv` + `period_mapping.json`.


## G7 — Lokasi dengan peran sentral

Graf lokasi: dua LOCATION terhubung bila ada tokoh yang terlibat di peristiwa pada **kedua** lokasi (bobot = jumlah tokoh bersama).


- Node lokasi: **17** | Edge: **136** | Density: **1.000**


> ⚠️ **Betweenness di sini nyaris tidak diskriminatif** (graf lokasi sangat padat — banyak lokasi terhubung ke hampir semua lokasi lain karena tokoh sentral seperti Muhammad hadir di peristiwa lintas hampir semua tempat). Peringkat utama karena itu pakai **weighted degree** (total tokoh-bersama), yang jauh lebih informatif.


### Top-15 lokasi (urut Weighted degree)

| Rank | Lokasi | Weighted degree | Degree | Betweenness |
|---:|---|---:|---:|---:|
| 1 | Madinah | 661 | 16 | 0.0000 |
| 2 | Habasyah | 561 | 16 | 0.0000 |
| 3 | Makkah | 561 | 16 | 0.0000 |
| 4 | Syam | 530 | 16 | 0.0000 |
| 5 | Yatsrib | 528 | 16 | 0.0000 |
| 6 | Ash-Shafra | 525 | 16 | 0.0000 |
| 7 | Tihamah | 525 | 16 | 0.0000 |
| 8 | Badr | 525 | 16 | 0.0000 |
| 9 | Najd | 525 | 16 | 0.0000 |
| 10 | Aqabah | 297 | 16 | 0.0000 |
| 11 | Jabal Uhud | 289 | 16 | 0.0000 |
| 12 | Yaman | 120 | 16 | 0.0000 |
| 13 | Khandaq | 106 | 16 | 0.0000 |
| 14 | Khaibar | 104 | 16 | 0.0000 |
| 15 | Jazirah Arab | 83 | 16 | 0.0000 |

## G8 — Keberagaman fase keterlibatan tokoh

Jumlah **fase Sirah unik** (dari 6 fase) tempat seorang tokoh terlibat, via `INVOLVED_IN` → event → `periode_bab` → fase. Tinggi = tokoh muncul lintas banyak babak.


- Event ter-petakan ke fase: **35**


### Top-15 tokoh (urut jumlah fase unik)

| Rank | Tokoh | Jml fase | Jml event | Fase yang disinggahi |
|---:|---|---:|---:|---|
| 1 | Muhammad | 5 | 22 | I (Pra-Islam) · II (Makkah) · IV (Perang Besar) · V (Diplomasi) · VI (Konsolidasi) |
| 2 | Umar bin Al-Khaththab | 3 | 5 | I (Pra-Islam) · IV (Perang Besar) · V (Diplomasi) |
| 3 | Abu Bakar | 3 | 4 | II (Makkah) · IV (Perang Besar) · V (Diplomasi) |
| 4 | Ali bin Abu Thalib | 2 | 7 | II (Makkah) · IV (Perang Besar) |
| 5 | Zaid bin Haritsah | 2 | 5 | IV (Perang Besar) · V (Diplomasi) |
| 6 | Aisyah | 2 | 4 | IV (Perang Besar) · V (Diplomasi) |
| 7 | Abdullah bin Ubay bin Salul | 2 | 4 | II (Makkah) · IV (Perang Besar) |
| 8 | Amr bin Umayyah | 2 | 4 | IV (Perang Besar) · VI (Konsolidasi) |
| 9 | Hamzah bin Abdul Muththalib | 2 | 3 | IV (Perang Besar) · VI (Konsolidasi) |
| 10 | Jabir bin Abdullah | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |
| 11 | Abu Hurairah | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |
| 12 | Abu Musa | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |
| 13 | Ibnu Hajar | 2 | 2 | II (Makkah) · IV (Perang Besar) |
| 14 | Amr bin Al-Ash | 2 | 2 | IV (Perang Besar) · V (Diplomasi) |
| 15 | Abu Salamah bin Abdul Asad | 2 | 2 | II (Makkah) · IV (Perang Besar) |

### Distribusi (berapa tokoh menyinggahi N fase)

| Jml fase | Jml tokoh |
|---:|---:|
| 5 | 1 |
| 3 | 2 |
| 2 | 17 |
| 1 | 124 |
