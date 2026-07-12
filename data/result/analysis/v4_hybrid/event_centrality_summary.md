# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **35**
- Event-Event edges: **264**
- Density          : **0.4437**
- Components       : 4
- Largest component: 32 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 0.0965 | 27 | 53 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0889 | 29 | 43 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0674 | 28 | 20 |
| 4 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 0.0442 | 24 | 20 |
| 5 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0424 | 23 | 4 |
| 6 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0404 | 23 | 1 |
| 7 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 0.0382 | 21 | 12 |
| 8 | Perang Bani Al-Ashfar | Perang Mu'tah & Penaklukan Makkah | 0.0353 | 22 | 1 |
| 9 | Perang Dzatur Riqa' | Hudaibiyah & Babak Baru Diplomasi | 0.0348 | 21 | 2 |
| 10 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0344 | 22 | 4 |
| 11 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0328 | 21 | 6 |
| 12 | Perang Mu'tah | Perang Mu'tah & Penaklukan Makkah | 0.0327 | 21 | 5 |
| 13 | Perang Bu'ats | Dakwah di Luar Makkah & Isra Mi'raj | 0.0317 | 21 | 6 |
| 14 | Perang Buwath | Perang Badr & Dampaknya | 0.0315 | 21 | 1 |
| 15 | Perang Abwa' | Perang Badr & Dampaknya | 0.0307 | 22 | 1 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.1958 | 29 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.1346 | 28 |
| 3 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 0.0264 | 24 |
| 4 | Perang Abwa' | Perang Badr & Dampaknya | 0.0225 | 22 |
| 5 | Perang Badr | Perang Badr & Dampaknya | 0.0186 | 27 |
| 6 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0170 | 22 |
| 7 | Perang Bani Quraizhah | Perang Khandaq hingga Bani Mushthaliq | 0.0165 | 10 |
| 8 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 0.0150 | 21 |
| 9 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0149 | 23 |
| 10 | Perang Fijar | Nasab & Kelahiran Nabi | 0.0148 | 21 |
| 11 | Hijrah | Konteks Arab Jahiliyah | 0.0147 | 21 |
| 12 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0133 | 21 |
| 13 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 0.0130 | 21 |
| 14 | Perang Al-Yamamah | Perang Badr & Dampaknya | 0.0102 | 21 |
| 15 | Perang Buwath | Perang Badr & Dampaknya | 0.0098 | 21 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 29 | 65 | 43 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 28 | 48 | 20 |
| 3 | Perang Badr | Perang Badr & Dampaknya | 27 | 74 | 53 |
| 4 | Perjanjian Hudaibiyah | Hudaibiyah & Babak Baru Diplomasi | 24 | 34 | 20 |
| 5 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 23 | 33 | 4 |
| 6 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 23 | 31 | 1 |
| 7 | Perang Abwa' | Perang Badr & Dampaknya | 22 | 23 | 1 |
| 8 | Perang Bani Al-Ashfar | Perang Mu'tah & Penaklukan Makkah | 22 | 27 | 1 |
| 9 | Perang Tha'if | Hunain, Tabuk & Puncak Kekuatan Islam | 22 | 26 | 4 |
| 10 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 21 | 23 | 2 |
| 11 | Hijrah | Konteks Arab Jahiliyah | 21 | 23 | 3 |
| 12 | Isra' Mi'raj | Dakwah di Luar Makkah & Isra Mi'raj | 21 | 22 | 9 |
| 13 | Perang Al-Yamamah | Perang Badr & Dampaknya | 21 | 22 | 1 |
| 14 | Perang Bani Mushthaliq | Perang Khandaq hingga Bani Mushthaliq | 21 | 21 | 2 |
| 15 | Perang Bu'ats | Dakwah di Luar Makkah & Isra Mi'raj | 21 | 24 | 6 |

## Komunitas Event (Louvain)

### Komunitas 1 — 16 event
Top events: Perang Khaibar, Perang Bani Al-Ashfar, Perang Dzatur Riqa', Perang Tha'if, Perang Tabuk, Perang Mu'tah, Perang Bu'ats, Perang Buwath
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Hunain, Tabuk & Puncak Kekuatan Islam, Konteks Arab Jahiliyah, Nasab & Kelahiran Nabi, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah

### Komunitas 2 — 1 event
Top events: Perang Badr Kubra
Period coverage: Perang Badr & Dampaknya

### Komunitas 3 — 1 event
Top events: Perang Badr Shughra
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 4 — 1 event
Top events: Perang Hamra'ul Asad
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 5 — 16 event
Top events: Perang Badr, Perang Uhud, Perang Khandaq, Perjanjian Hudaibiyah, Baiat Aqabah Kubra, Perang Dzul Usyairah, Perang Bani Quraizhah, Perang Badr Ula
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Konteks Arab Jahiliyah, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.