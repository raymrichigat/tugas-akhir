# Skenario G7 & G8 — Hasil (KG v3 cleaned)

> Dihasilkan oleh `src/analysis/scenario_g7_g8.py`. Sumber: `nodes_v3.csv` + `edges_v3.csv` + `period_mapping.json`.


## G7 — Lokasi dengan peran sentral

Graf lokasi: dua LOCATION terhubung bila ada tokoh yang terlibat di peristiwa pada **kedua** lokasi (bobot = jumlah tokoh bersama).


- Node lokasi: **35** | Edge: **437** | Density: **0.734**


> ⚠️ **Betweenness di sini nyaris tidak diskriminatif** (graf lokasi sangat padat — banyak lokasi terhubung ke hampir semua lokasi lain karena tokoh sentral seperti Muhammad hadir di peristiwa lintas hampir semua tempat). Peringkat utama karena itu pakai **weighted degree** (total tokoh-bersama), yang jauh lebih informatif.


### Top-15 lokasi (urut Weighted degree)

| Rank | Lokasi | Weighted degree | Degree | Betweenness |
|---:|---|---:|---:|---:|
| 1 | Madinah | 684 | 34 | 0.0254 |
| 2 | Makkah | 595 | 34 | 0.0254 |
| 3 | Habasyah | 505 | 25 | 0.0020 |
| 4 | Yatsrib | 453 | 25 | 0.0020 |
| 5 | Badr | 450 | 25 | 0.0020 |
| 6 | Tihamah | 450 | 25 | 0.0020 |
| 7 | Hijir | 450 | 25 | 0.0020 |
| 8 | Aqabah | 361 | 34 | 0.0254 |
| 9 | Yaman | 240 | 34 | 0.0254 |
| 10 | Hunain | 237 | 23 | 0.0005 |
| 11 | Syam | 235 | 34 | 0.0254 |
| 12 | Ka'bah | 223 | 34 | 0.0254 |
| 13 | Zamzam | 146 | 34 | 0.0254 |
| 14 | Baitul- Haram | 132 | 34 | 0.0254 |
| 15 | Laut Merah | 126 | 26 | 0.0035 |

## G8 — Keberagaman fase keterlibatan tokoh

Jumlah **fase Sirah unik** (dari 6 fase) tempat seorang tokoh terlibat, via `INVOLVED_IN` → event → `periode_bab` → fase. Tinggi = tokoh muncul lintas banyak babak.


- Event ter-petakan ke fase: **46**


### Top-15 tokoh (urut jumlah fase unik)

| Rank | Tokoh | Jml fase | Jml event | Fase yang disinggahi |
|---:|---|---:|---:|---|
| 1 | Muhammad | 6 | 25 | I (Pra-Islam) · II (Makkah) · III (Madinah Awal) · IV (Perang Besar) · V (Diplomasi) · VI (Konsolidasi) |
| 2 | Abu Bakar | 4 | 6 | II (Makkah) · IV (Perang Besar) · V (Diplomasi) · VI (Konsolidasi) |
| 3 | Aisyah | 4 | 5 | II (Makkah) · IV (Perang Besar) · V (Diplomasi) · VI (Konsolidasi) |
| 4 | Jibril | 3 | 5 | I (Pra-Islam) · II (Makkah) · VI (Konsolidasi) |
| 5 | Ibnu Hisyam | 3 | 3 | I (Pra-Islam) · II (Makkah) · VI (Konsolidasi) |
| 6 | Ali bin Abu Thalib | 2 | 8 | II (Makkah) · IV (Perang Besar) |
| 7 | Abu Jahal | 2 | 5 | II (Makkah) · IV (Perang Besar) |
| 8 | Umar bin Al-Khaththab | 2 | 4 | I (Pra-Islam) · IV (Perang Besar) |
| 9 | Abdullah bin Ubay bin Salul | 2 | 4 | II (Makkah) · IV (Perang Besar) |
| 10 | Hamzah bin Abdul Muththalib | 2 | 4 | I (Pra-Islam) · IV (Perang Besar) |
| 11 | Amr Bin Umayyah | 2 | 4 | IV (Perang Besar) · VI (Konsolidasi) |
| 12 | Abu Thalib | 2 | 4 | I (Pra-Islam) · II (Makkah) |
| 13 | Jabir bin Abdullah | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |
| 14 | Abu Hurairah | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |
| 15 | Abu Musa | 2 | 3 | IV (Perang Besar) · V (Diplomasi) |

### Distribusi (berapa tokoh menyinggahi N fase)

| Jml fase | Jml tokoh |
|---:|---:|
| 6 | 1 |
| 4 | 2 |
| 3 | 2 |
| 2 | 25 |
| 1 | 120 |
