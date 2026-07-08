# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **45**
- Event-Event edges: **390**
- Density          : **0.3939**
- Components       : 7
- Largest component: 39 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 0.0799 | 33 | 66 |
| 2 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0670 | 34 | 55 |
| 3 | Perang Khandaq | Perang Burhan | 0.0554 | 33 | 24 |
| 4 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0369 | 28 | 3 |
| 5 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 0.0365 | 29 | 15 |
| 6 | Baiat Aqabah Kubra | BAIAT AQABAH KEDUA | 0.0353 | 28 | 4 |
| 7 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 0.0339 | 27 | 13 |
| 8 | Perang Dzul Usyairah | Perang Dumatul Jandal | 0.0338 | 28 | 1 |
| 9 | Perang Dzatur Riqa' | Perang Dzatur Riqa’ | 0.0299 | 26 | 3 |
| 10 | Perang Bani Al-Ashfar | Perang Bani Nadhir | 0.0294 | 27 | 1 |
| 11 | Isra' |  | 0.0290 | 27 | 18 |
| 12 | Al-Umawi | Al-Qur’an | 0.0288 | 27 | 1 |
| 13 | Perang Tha'if | Perang Tha’if | 0.0287 | 27 | 4 |
| 14 | Perang Tabuk | PERANG TABUK | 0.0276 | 26 | 8 |
| 15 | Perjanjian Hudaibiyah | PERJANJIAN HUDAIBIYAH | 0.0276 | 26 | 13 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.1442 | 34 |
| 2 | Perang Khandaq | Perang Burhan | 0.0989 | 33 |
| 3 | Isra' |  | 0.0443 | 27 |
| 4 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 0.0430 | 27 |
| 5 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 0.0156 | 33 |
| 6 | Perang Abwa' | PERANG TABUK | 0.0152 | 27 |
| 7 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 0.0142 | 29 |
| 8 | Perang Tha'if | Perang Tha’if | 0.0119 | 27 |
| 9 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 0.0116 | 28 |
| 10 | Perang Bani Quraizhah | PERANG BANI QURAIZHAH | 0.0111 | 11 |
| 11 | Baiat Aqabah Kubra | BAIAT AQABAH KEDUA | 0.0107 | 28 |
| 12 | Hunain | PERANG HUNAIN | 0.0105 | 26 |
| 13 | Perang Bani Mushthaliq | Perang Bani Nadhir | 0.0105 | 26 |
| 14 | Perang Fijar | Perang Fijar | 0.0104 | 26 |
| 15 | Hijrah | Hijrah ke Habasyah yang Pertama | 0.0104 | 26 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 34 | 68 | 55 |
| 2 | Perang Badr | Satuan-satuan Pasukan Sebelum Perang Badr | 33 | 85 | 66 |
| 3 | Perang Khandaq | Perang Burhan | 33 | 56 | 24 |
| 4 | Hudaibiyah | PERJANJIAN HUDAIBIYAH | 29 | 40 | 15 |
| 5 | Baiat Aqabah Kubra | BAIAT AQABAH KEDUA | 28 | 39 | 4 |
| 6 | Uhud | AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD | 28 | 41 | 3 |
| 7 | Perang Dzul Usyairah | Perang Dumatul Jandal | 28 | 37 | 1 |
| 8 | Isra' |  | 27 | 28 | 18 |
| 9 | Perang Khaibar | PERANG KHAIBAR DAN WADIL QURA | 27 | 37 | 13 |
| 10 | Perang Tha'if | Perang Tha’if | 27 | 31 | 4 |
| 11 | Perang Abwa' | PERANG TABUK | 27 | 28 | 1 |
| 12 | Perang Bani Al-Ashfar | Perang Bani Nadhir | 27 | 32 | 1 |
| 13 | Al-Umawi | Al-Qur’an | 27 | 31 | 1 |
| 14 | Perjanjian Hudaibiyah | PERJANJIAN HUDAIBIYAH | 26 | 30 | 13 |
| 15 | Perang Tabuk | PERANG TABUK | 26 | 30 | 8 |

## Komunitas Event (Louvain)

### Komunitas 1 — 19 event
Top events: Perang Badr, Perang Uhud, Perang Khandaq, Uhud, Hudaibiyah, Baiat Aqabah Kubra, Perang Dzul Usyairah, Perang Bani Al-Ashfar
Period coverage: AKTIVITAS PASUKAN ANTARA PERANG BADR DAN PERANG UHUD, BAIAT AQABAH KEDUA, PERANG BADR KUBRA, PERANG BANI QURAIZHAH, PERANG TABUK, PERJANJIAN HUDAIBIYAH, Perang As-Sawiq, Perang Bani Nadhir, Perang Bani Qainuqa’, Perang Burhan, Perang Dumatul Jandal, Peringatan di Makkah, Satuan-satuan Pasukan Sebelum Perang Badr

### Komunitas 2 — 20 event
Top events: Perang Khaibar, Perang Dzatur Riqa', Isra', Al-Umawi, Perang Tha'if, Perang Tabuk, Perjanjian Hudaibiyah, Perang Mu'tah
Period coverage: Al-Qur’an, BAIAT AQABAH PERTAMA, Hijrah ke Habasyah yang Pertama, PERANG HUNAIN, PERANG KHAIBAR DAN WADIL QURA, PERANG MU’TAH, PERANG TABUK, PERJANJIAN HUDAIBIYAH, Perang Bani Nadhir, Perang Burhan, Perang Dzatur Riqa’, Perang Fijar, Perang Tha’if

### Komunitas 3 — 1 event
Top events: Isra' Dan Mi'raj
Period coverage: ISRA’ DAN MI’RAJ

### Komunitas 4 — 1 event
Top events: Isra' Mi'raj
Period coverage: ISRA’ DAN MI’RAJ

### Komunitas 5 — 1 event
Top events: Perang Badr Kubra
Period coverage: PERANG BADR KUBRA

### Komunitas 6 — 1 event
Top events: Perang Badr Shughra
Period coverage: PERANG BADR KUBRA

### Komunitas 7 — 1 event
Top events: Perang Hamra'ul Asad
Period coverage: Perang Hamra’ul-Asad

### Komunitas 8 — 1 event
Top events: Hamra'ul Asad
Period coverage: Perang Hamra’ul-Asad


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.