# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **52**
- Event-Event edges: **421**
- Density          : **0.3175**
- Components       : 10
- Largest component: 43 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 0.0695 | 35 | 66 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0602 | 34 | 55 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0428 | 32 | 24 |
| 4 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0427 | 30 | 26 |
| 5 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0390 | 31 | 29 |
| 6 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0341 | 28 | 21 |
| 7 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0328 | 30 | 15 |
| 8 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0316 | 27 | 4 |
| 9 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 0.0294 | 29 | 9 |
| 10 | Perang Bani Al-Ashfar | Perang Mu'tah & Penaklukan Makkah | 0.0293 | 27 | 1 |
| 11 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 0.0293 | 27 | 13 |
| 12 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0288 | 29 | 1 |
| 13 | Perang | Dakwah Jahriyah & Tekanan Quraisy | 0.0281 | 28 | 1 |
| 14 | Perang Dzatur Riqa | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0271 | 27 | 3 |
| 15 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0271 | 28 | 4 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.1302 | 34 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0654 | 32 |
| 3 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0400 | 30 |
| 4 | Perang Badr | Perang Badr & Dampaknya | 0.0396 | 35 |
| 5 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0370 | 31 |
| 6 | Mi'Raj | Awal Kenabian & Mandat Dakwah | 0.0325 | 5 |
| 7 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 0.0245 | 28 |
| 8 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0244 | 29 |
| 9 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0194 | 30 |
| 10 | Peperangan | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0124 | 28 |
| 11 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0117 | 28 |
| 12 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 0.0114 | 29 |
| 13 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0109 | 28 |
| 14 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 0.0068 | 27 |
| 15 | Perang Bu'ats | Membangun Masyarakat Madinah | 0.0068 | 27 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 35 | 81 | 66 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 34 | 67 | 55 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 32 | 47 | 24 |
| 4 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 31 | 44 | 29 |
| 5 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 30 | 37 | 15 |
| 6 | Hijrah Ke Madinah | Hijrah ke Madinah | 30 | 52 | 26 |
| 7 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 29 | 32 | 1 |
| 8 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 29 | 35 | 9 |
| 9 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 28 | 31 | 13 |
| 10 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 28 | 32 | 4 |
| 11 | Perang | Dakwah Jahriyah & Tekanan Quraisy | 28 | 34 | 1 |
| 12 | Peperangan | Perang Uhud & Satuan Pasukan Pasca Uhud | 28 | 30 | 1 |
| 13 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 28 | 41 | 21 |
| 14 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 27 | 36 | 13 |
| 15 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 27 | 31 | 8 |

## Komunitas Event (Louvain)

### Komunitas 1 — 14 event
Top events: Perang Badr, Perang Uhud, Perang Khandaq, Hijrah Ke Madinah, Wafat Nabi, Baiat Aqabah Kubra, Perang Bani Al-Ashfar, Perang As-Sawiq
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hijrah ke Madinah, Konteks Arab Jahiliyah, Penaklukan Makkah hingga Akhir Kenabian, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 2 — 1 event
Top events: Hudaibiyah
Period coverage: Hudaibiyah & Babak Baru Diplomasi

### Komunitas 3 — 1 event
Top events: Perang Bukhtanashar
Period coverage: Konteks Arab Jahiliyah

### Komunitas 4 — 1 event
Top events: Isra' Dan Mi'Raj
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj

### Komunitas 5 — 1 event
Top events: Isra' Mi'Raj
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj

### Komunitas 6 — 18 event
Top events: Perang Khaibar, Perang, Perang Dzatur Riqa, Perang Tha'If, Perjanjian Hudaibiyah, Perang Tabuk, Peperangan, Perang Bu'Ats
Period coverage: Dakwah Jahriyah & Tekanan Quraisy, Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Hunain, Tabuk & Puncak Kekuatan Islam, Membangun Masyarakat Madinah, Nasab & Kelahiran Nabi, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 7 — 1 event
Top events: Perang Safawan
Period coverage: Perang Badr & Dampaknya

### Komunitas 8 — 3 event
Top events: Perang Dzul Usyairah, Perang Badr Ula, Perang Bani Quraizhah
Period coverage: Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 9 — 1 event
Top events: Perang Badr Kubra
Period coverage: Perang Badr & Dampaknya

### Komunitas 10 — 1 event
Top events: Jabal Uhud
Period coverage: Perang Badr & Dampaknya

### Komunitas 11 — 1 event
Top events: Perang Hamra'Ul Asad
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 12 — 1 event
Top events: Perang Badr Shughra
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 13 — 8 event
Top events: Kelahiran Nabi, Wahyu Pertama, Pemboikotan Bani Hasyim, Tahun Berduka, Mi'Raj, Hijrah Ke Habasyah, Malam, Haji Wada'
Period coverage: Awal Kenabian & Mandat Dakwah, Dakwah Jahriyah & Tekanan Quraisy, Nasab & Kelahiran Nabi, Penaklukan Makkah hingga Akhir Kenabian


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.