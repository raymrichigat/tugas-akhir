# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **52**
- Event-Event edges: **425**
- Density          : **0.3205**
- Components       : 10
- Largest component: 43 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 0.0676 | 35 | 66 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0585 | 33 | 55 |
| 3 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0435 | 30 | 26 |
| 4 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0409 | 31 | 24 |
| 5 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0377 | 31 | 29 |
| 6 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0350 | 29 | 21 |
| 7 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0334 | 31 | 15 |
| 8 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0312 | 27 | 4 |
| 9 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 0.0310 | 29 | 9 |
| 10 | Perang Bani Al-Ashfar | Perang Mu'tah & Penaklukan Makkah | 0.0290 | 27 | 1 |
| 11 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 0.0290 | 27 | 13 |
| 12 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0285 | 29 | 1 |
| 13 | Perang | Dakwah Jahriyah & Tekanan Quraisy | 0.0278 | 28 | 1 |
| 14 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0268 | 28 | 8 |
| 15 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0268 | 28 | 4 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.1041 | 33 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0535 | 31 |
| 3 | Perang Badr | Perang Badr & Dampaknya | 0.0463 | 35 |
| 4 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0445 | 31 |
| 5 | Mi'Raj | Awal Kenabian & Mandat Dakwah | 0.0324 | 5 |
| 6 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 0.0310 | 28 |
| 7 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0290 | 31 |
| 8 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0236 | 29 |
| 9 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0195 | 30 |
| 10 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0189 | 28 |
| 11 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0180 | 29 |
| 12 | Perang Mu'Tah | Perang Mu'tah & Penaklukan Makkah | 0.0138 | 28 |
| 13 | Peperangan | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0119 | 28 |
| 14 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0106 | 28 |
| 15 | Tahun Berduka | Dakwah Jahriyah & Tekanan Quraisy | 0.0103 | 9 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 35 | 81 | 66 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 33 | 67 | 55 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 31 | 47 | 24 |
| 4 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 31 | 44 | 29 |
| 5 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 31 | 39 | 15 |
| 6 | Hijrah Ke Madinah | Hijrah ke Madinah | 30 | 54 | 26 |
| 7 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 29 | 32 | 1 |
| 8 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 29 | 37 | 9 |
| 9 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 29 | 42 | 21 |
| 10 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 28 | 32 | 8 |
| 11 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 28 | 29 | 6 |
| 12 | Perang Mu'Tah | Perang Mu'tah & Penaklukan Makkah | 28 | 30 | 5 |
| 13 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 28 | 32 | 4 |
| 14 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 28 | 29 | 2 |
| 15 | Perang | Dakwah Jahriyah & Tekanan Quraisy | 28 | 34 | 1 |

## Komunitas Event (Louvain)

### Komunitas 1 — 3 event
Top events: Perang Dzul Usyairah, Perang Badr Ula, Perang Bani Quraizhah
Period coverage: Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 2 — 18 event
Top events: Perang Khaibar, Perang, Perang Tabuk, Perang Tha'If, Perang Mu'Tah, Perjanjian Hudaibiyah, Perang Dzatur Riqa, Baiat Aqabah
Period coverage: Dakwah Jahriyah & Tekanan Quraisy, Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Hunain, Tabuk & Puncak Kekuatan Islam, Membangun Masyarakat Madinah, Nasab & Kelahiran Nabi, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 3 — 1 event
Top events: Perang Asafan
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 4 — 1 event
Top events: Hudaibiyah
Period coverage: Hudaibiyah & Babak Baru Diplomasi

### Komunitas 5 — 1 event
Top events: Perang Bukhtanashar
Period coverage: Konteks Arab Jahiliyah

### Komunitas 6 — 1 event
Top events: Isra' Mi'Raj
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj

### Komunitas 7 — 1 event
Top events: Perang Safawan
Period coverage: Perang Badr & Dampaknya

### Komunitas 8 — 1 event
Top events: Perang Badr Kubra
Period coverage: Perang Badr & Dampaknya

### Komunitas 9 — 1 event
Top events: Jabal Uhud
Period coverage: Perang Badr & Dampaknya

### Komunitas 10 — 1 event
Top events: Perang Hamra'Ul Asad
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 11 — 1 event
Top events: Perang Badr Shughra
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 12 — 9 event
Top events: Kelahiran Nabi, Wahyu Pertama, Pemboikotan Bani Hasyim, Tahun Berduka, Mi'Raj, Hijrah Ke Habasyah, Haji Wada', Malam
Period coverage: Awal Kenabian & Mandat Dakwah, Dakwah Jahriyah & Tekanan Quraisy, Dakwah di Luar Makkah & Isra Mi'raj, Nasab & Kelahiran Nabi, Penaklukan Makkah hingga Akhir Kenabian

### Komunitas 13 — 13 event
Top events: Perang Badr, Perang Uhud, Hijrah Ke Madinah, Perang Khandaq, Wafat Nabi, Baiat Aqabah Kubra, Perang Bani Al-Ashfar, Perang As-Sawiq
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hijrah ke Madinah, Konteks Arab Jahiliyah, Penaklukan Makkah hingga Akhir Kenabian, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.