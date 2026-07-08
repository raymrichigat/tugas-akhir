# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **48**
- Event-Event edges: **395**
- Density          : **0.3502**
- Components       : 7
- Largest component: 42 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 0.0778 | 33 | 66 |
| 2 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0654 | 34 | 55 |
| 3 | Perang Khandaq | Perang Burhan | 0.0533 | 33 | 24 |
| 4 | Isra | ISRA’ DAN MI’RAJ | 0.0391 | 30 | 17 |
| 5 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0356 | 28 | 3 |
| 6 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 0.0353 | 29 | 15 |
| 7 | Baiat Aqabah Kubra | BAIAT AQABAH KEDUA | 0.0341 | 28 | 4 |
| 8 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 0.0328 | 27 | 13 |
| 9 | Perang Dzul Usyairah | Perang Dumatul Jandal | 0.0327 | 28 | 1 |
| 10 | Perang Bani Al-Ashfar | Perang Bani Nadhir | 0.0294 | 27 | 1 |
| 11 | Perang Dzatur Riqa | Perang Dzatur Riqa’ | 0.0290 | 26 | 3 |
| 12 | Al-Umawi | Al-Qur’an | 0.0279 | 27 | 1 |
| 13 | Perang Tha'if | Perang Tha’if | 0.0278 | 27 | 4 |
| 14 | Perang Fijar | Perang Fijar | 0.0268 | 27 | 3 |
| 15 | Perang Tabuk | PERANG TABUK | 0.0268 | 26 | 8 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.1360 | 34 |
| 2 | Isra | ISRA’ DAN MI’RAJ | 0.1112 | 30 |
| 3 | Perang Khandaq | Perang Burhan | 0.0959 | 33 |
| 4 | Perang Fijar | Perang Fijar | 0.0459 | 27 |
| 5 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 0.0414 | 27 |
| 6 | Perang Abwa | PERANG TABUK | 0.0144 | 27 |
| 7 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 0.0135 | 29 |
| 8 | Perang Bani Quraizhah | PERANG BANI QURAIZHAH | 0.0128 | 12 |
| 9 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 0.0124 | 33 |
| 10 | Perang Tha'if | Perang Tha’if | 0.0121 | 27 |
| 11 | Hunain | PERANG HUNAIN | 0.0108 | 26 |
| 12 | Perang Bani Mushthaliq | Perang Bani Nadhir | 0.0108 | 26 |
| 13 | Ahzab | SATUAN-SATUAN PERANG ANTARA PERANG UHUD DAN AHZAB | 0.0108 | 26 |
| 14 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0105 | 28 |
| 15 | Perang Hunain | PERANG HUNAIN | 0.0101 | 26 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 34 | 69 | 55 |
| 2 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 33 | 86 | 66 |
| 3 | Perang Khandaq | Perang Burhan | 33 | 56 | 24 |
| 4 | Isra | ISRA’ DAN MI’RAJ | 30 | 35 | 17 |
| 5 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 29 | 40 | 15 |
| 6 | Baiat Aqabah Kubra | BAIAT AQABAH KEDUA | 28 | 39 | 4 |
| 7 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 28 | 41 | 3 |
| 8 | Perang Dzul Usyairah | Perang Dumatul Jandal | 28 | 37 | 1 |
| 9 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 27 | 37 | 13 |
| 10 | Perang Tha'if | Perang Tha’if | 27 | 31 | 4 |
| 11 | Perang Fijar | Perang Fijar | 27 | 27 | 3 |
| 12 | Perang Abwa | PERANG TABUK | 27 | 28 | 1 |
| 13 | Al-Umawi | Al-Qur’an | 27 | 31 | 1 |
| 14 | Perang Bani Al-Ashfar | Perang Bani Nadhir | 27 | 33 | 1 |
| 15 | Perjanjian Hudaibiyah | PERJANJIAN HUDAIBIYAH | 26 | 30 | 14 |

## Komunitas Event (Louvain)

### Komunitas 1 — 18 event
Top events: Perang Badr, Perang Uhud, Perang Khandaq, Uhud, Hudaibiyah, Baiat Aqabah Kubra, Perang Dzul Usyairah, Perang Bani Quraizhah
Period coverage: AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD, BAIAT AQABAH KEDUA, PERANG BADR KUBRA, PERANG BANI QURAIZHAH, PERANG TABUK, PERJANJIAN HUDAIBIYAH, Perang As-Sawiq, Perang Bani Nadhir, Perang Bani Qainuqa’, Perang Burhan, Perang Dumatul Jandal, Peringatan di Makkah, Satuan-satuan Pasukan Sebelum Perang Badr

### Komunitas 2 — 22 event
Top events: Isra, Perang Khaibar, Perang Bani Al-Ashfar, Perang Dzatur Riqa, Al-Umawi, Perang Tha'if, Perang Fijar, Perang Tabuk
Period coverage: Al-Qur’an, BAIAT AQABAH PERTAMA, ISRA’ DAN MI’RAJ, PERANG HUNAIN, PERANG KHAIBAR DAN WADIL QURA, PERANG MU’TAH, PERANG TABUK, PERJANJIAN HUDAIBIYAH, Perang Bani Nadhir, Perang Burhan, Perang Dzatur Riqa’, Perang Fijar, Perang Tha’if, SATUAN-SATUAN PERANG ANTARA PERANG UHUD DAN AHZAB

### Komunitas 3 — 2 event
Top events: Al-Isra, Hijrah
Period coverage: Al-Qur’an, Hijrah ke Habasyah yang Pertama

### Komunitas 4 — 1 event
Top events: Perang Bukhtanashar
Period coverage: Perang Burhan

### Komunitas 5 — 1 event
Top events: Perang Badr Kubra
Period coverage: PERANG BADR KUBRA

### Komunitas 6 — 1 event
Top events: Jabal Uhud
Period coverage: PERANG UHUD

### Komunitas 7 — 1 event
Top events: Perang Hamra'ul Asad
Period coverage: Perang Hamra’ul-Asad

### Komunitas 8 — 1 event
Top events: Hamra'ul Asad
Period coverage: Perang Hamra’ul-Asad

### Komunitas 9 — 1 event
Top events: Perang Badr Shughra
Period coverage: PERANG BADR KUBRA


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.