# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **36**
- Event-Event edges: **150**
- Density          : **0.2381**
- Components       : 14
- Largest component: 23 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 0.0818 | 19 | 44 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0695 | 19 | 24 |
| 3 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0654 | 18 | 27 |
| 4 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0576 | 18 | 4 |
| 5 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0553 | 18 | 1 |
| 6 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 0.0516 | 16 | 10 |
| 7 | Perang Dzatur Riqa' | Hudaibiyah & Babak Baru Diplomasi | 0.0496 | 16 | 3 |
| 8 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 0.0467 | 17 | 2 |
| 9 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0441 | 16 | 8 |
| 10 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 0.0438 | 16 | 11 |
| 11 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0419 | 16 | 6 |
| 12 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0419 | 16 | 2 |
| 13 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 0.0419 | 16 | 2 |
| 14 | Perang Mu'tah | Perang Mu'tah & Penaklukan Makkah | 0.0419 | 16 | 2 |
| 15 | Perang Buwath | Perang Badr & Dampaknya | 0.0399 | 16 | 1 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0697 | 18 |
| 2 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 0.0398 | 17 |
| 3 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0312 | 18 |
| 4 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0245 | 19 |
| 5 | Perang Badr | Perang Badr & Dampaknya | 0.0211 | 19 |
| 6 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0140 | 18 |
| 7 | Perang Fijar | Nasab & Kelahiran Nabi | 0.0066 | 16 |
| 8 | Perang Abwa' | Perang Badr & Dampaknya | 0.0066 | 16 |
| 9 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0061 | 16 |
| 10 | Perang Mu'tah | Perang Mu'tah & Penaklukan Makkah | 0.0058 | 16 |
| 11 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 0.0058 | 16 |
| 12 | Perang Bani Quraizhah | Perang Khandaq hingga Bani Mushthaliq | 0.0056 | 5 |
| 13 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0056 | 16 |
| 14 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 0.0046 | 16 |
| 15 | Perang Buwath | Perang Badr & Dampaknya | 0.0044 | 16 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 19 | 36 | 44 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 19 | 30 | 24 |
| 3 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 18 | 25 | 27 |
| 4 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 18 | 25 | 4 |
| 5 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 18 | 24 | 1 |
| 6 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 17 | 18 | 2 |
| 7 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 16 | 19 | 11 |
| 8 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 16 | 23 | 10 |
| 9 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 16 | 19 | 8 |
| 10 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 16 | 18 | 6 |
| 11 | Perang Fijar | Nasab & Kelahiran Nabi | 16 | 16 | 3 |
| 12 | Perang Dzatur Riqa' | Hudaibiyah & Babak Baru Diplomasi | 16 | 22 | 3 |
| 13 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 16 | 18 | 2 |
| 14 | Perang Mu'tah | Perang Mu'tah & Penaklukan Makkah | 16 | 18 | 2 |
| 15 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 16 | 18 | 2 |

## Komunitas Event (Louvain)

### Komunitas 1 — 10 event
Top events: Perang Badr, Perang Khandaq, Perang Uhud, Baiat Aqabah Kubra, Perang Dzul Usyairah, Perang Badr Ula, Perang Bani Quraizhah, Perang Safawan
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 2 — 13 event
Top events: Perang Khaibar, Perang Dzatur Riqa', Baiat Aqabah, Perang Tabuk, Perjanjian Hudaibiyah, Perang Hunain, Perang Tha'if, Perang Bani Mushthaliq
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Hunain, Tabuk & Puncak Kekuatan Islam, Nasab & Kelahiran Nabi, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah

### Komunitas 3 — 1 event
Top events: Perang Bani Nadhir
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 4 — 1 event
Top events: Perang Uhud Jabal
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 5 — 1 event
Top events: Ghazwah Dzatu Qarad
Period coverage: Hudaibiyah & Babak Baru Diplomasi

### Komunitas 6 — 1 event
Top events: Ghazwah Mu'tah
Period coverage: Perang Mu'tah & Penaklukan Makkah

### Komunitas 7 — 1 event
Top events: Perang Badr Kubra
Period coverage: Perang Badr & Dampaknya

### Komunitas 8 — 1 event
Top events: Perang Badr Shughra
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 9 — 1 event
Top events: Wahyu Pertama
Period coverage: Awal Kenabian & Mandat Dakwah

### Komunitas 10 — 1 event
Top events: Bi'tsah Nabawiyah
Period coverage: Awal Kenabian & Mandat Dakwah

### Komunitas 11 — 1 event
Top events: Dakwah Sirriyah
Period coverage: Dakwah Sirriyah

### Komunitas 12 — 1 event
Top events: Hijrah ke Madinah
Period coverage: Hijrah ke Madinah

### Komunitas 13 — 1 event
Top events: Haji Wada'
Period coverage: Masuknya Umat & Haji Wada'

### Komunitas 14 — 1 event
Top events: Khutbah Wada'
Period coverage: Masuknya Umat & Haji Wada'

### Komunitas 15 — 1 event
Top events: Hijrah ke Habasyah
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.