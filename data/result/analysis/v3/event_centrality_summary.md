# Event Centrality Analysis — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — extend SNA ke node Event (sebelumnya cuma Person). Co-participation rule: dua Event terhubung kalau share minimal 1 Person via INVOLVED_IN, weight = jumlah Person bersama. PRECEDES (kronologi) ditambahkan sebagai weight extra.

## Ringkasan Graf

- Event nodes      : **46**
- Event-Event edges: **354**
- Density          : **0.3420**
- Components       : 7
- Largest component: 40 events

## Top 15 Event — PageRank (paling sentral di narasi)

| Rank | Event | Period | PageRank | Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 0.0767 | 33 | 51 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0704 | 33 | 41 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0505 | 30 | 20 |
| 4 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0489 | 29 | 26 |
| 5 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0407 | 28 | 29 |
| 6 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0368 | 26 | 21 |
| 7 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0362 | 26 | 4 |
| 8 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0350 | 28 | 15 |
| 9 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 0.0324 | 26 | 1 |
| 10 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 0.0321 | 26 | 9 |
| 11 | Perang Khaibar | Hudaibiyah & Babak Baru Diplomasi | 0.0307 | 24 | 9 |
| 12 | Perang Bani Al-Ashfar | Perang Mu'tah & Penaklukan Makkah | 0.0307 | 24 | 1 |
| 13 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0289 | 25 | 4 |
| 14 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0281 | 25 | 6 |
| 15 | Perang Mu'Tah | Perang Mu'tah & Penaklukan Makkah | 0.0275 | 25 | 4 |

## Top 15 Event — Betweenness (jembatan antar fase)

| Rank | Event | Period | Betweenness | Degree |
|---:|---|---|---:|---:|
| 1 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.1403 | 33 |
| 2 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 0.0711 | 30 |
| 3 | Perang Badr | Perang Badr & Dampaknya | 0.0489 | 33 |
| 4 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 0.0477 | 28 |
| 5 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 0.0394 | 25 |
| 6 | Hijrah Ke Madinah | Hijrah ke Madinah | 0.0327 | 29 |
| 7 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 0.0254 | 25 |
| 8 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 0.0254 | 28 |
| 9 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 0.0163 | 25 |
| 10 | Perang Mu'Tah | Perang Mu'tah & Penaklukan Makkah | 0.0145 | 25 |
| 11 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 0.0142 | 26 |
| 12 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 0.0139 | 26 |
| 13 | Tahun Berduka | Dakwah Jahriyah & Tekanan Quraisy | 0.0123 | 8 |
| 14 | Perang Abwa | Membangun Masyarakat Madinah | 0.0105 | 24 |
| 15 | Perang Fijar | Nasab & Kelahiran Nabi | 0.0104 | 24 |

## Top 15 Event — Degree (paling banyak co-participation)

| Rank | Event | Period | Degree | Weighted Degree | Frekuensi |
|---:|---|---|---:|---:|---:|
| 1 | Perang Badr | Perang Badr & Dampaknya | 33 | 80 | 51 |
| 2 | Perang Uhud | Perang Uhud & Satuan Pasukan Pasca Uhud | 33 | 70 | 41 |
| 3 | Perang Khandaq | Perang Khandaq hingga Bani Mushthaliq | 30 | 50 | 20 |
| 4 | Hijrah Ke Madinah | Hijrah ke Madinah | 29 | 53 | 26 |
| 5 | Kelahiran Nabi | Nasab & Kelahiran Nabi | 28 | 42 | 29 |
| 6 | Wahyu Pertama | Awal Kenabian & Mandat Dakwah | 28 | 36 | 15 |
| 7 | Baiat Aqabah Kubra | Dakwah di Luar Makkah & Isra Mi'raj | 26 | 39 | 4 |
| 8 | Pemboikotan Bani Hasyim | Dakwah Jahriyah & Tekanan Quraisy | 26 | 33 | 9 |
| 9 | Perang Dzul Usyairah | Perang Badr & Dampaknya | 26 | 34 | 1 |
| 10 | Wafat Nabi | Penaklukan Makkah hingga Akhir Kenabian | 26 | 39 | 21 |
| 11 | Baiat Aqabah | Dakwah di Luar Makkah & Isra Mi'raj | 25 | 26 | 2 |
| 12 | Perang Hunain | Hunain, Tabuk & Puncak Kekuatan Islam | 25 | 26 | 6 |
| 13 | Perang Mu'Tah | Perang Mu'tah & Penaklukan Makkah | 25 | 28 | 4 |
| 14 | Perang Tabuk | Hunain, Tabuk & Puncak Kekuatan Islam | 25 | 29 | 6 |
| 15 | Perang Tha'If | Perang Uhud & Satuan Pasukan Pasca Uhud | 25 | 30 | 4 |

## Komunitas Event (Louvain)

### Komunitas 1 — 1 event
Top events: Hudaibiyah
Period coverage: Hudaibiyah & Babak Baru Diplomasi

### Komunitas 2 — 1 event
Top events: Perang Asafan
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 3 — 1 event
Top events: Perang Badr Kubra
Period coverage: Perang Badr & Dampaknya

### Komunitas 4 — 1 event
Top events: Perang Badr Shughra
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 5 — 1 event
Top events: Perang Bukhtanashar
Period coverage: Konteks Arab Jahiliyah

### Komunitas 6 — 17 event
Top events: Perang Badr, Perang Uhud, Perang Khandaq, Hijrah Ke Madinah, Wafat Nabi, Baiat Aqabah Kubra, Perang Dzul Usyairah, Perang Bani Al-Ashfar
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hijrah ke Madinah, Konteks Arab Jahiliyah, Penaklukan Makkah hingga Akhir Kenabian, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 7 — 1 event
Top events: Perang Hamra'Ul Asad
Period coverage: Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 8 — 15 event
Top events: Perang Khaibar, Perang Tha'If, Perang Tabuk, Perang Mu'Tah, Perjanjian Hudaibiyah, Perang Buwath, Perang Dzatur Riqa, Baiat Aqabah
Period coverage: Dakwah di Luar Makkah & Isra Mi'raj, Hudaibiyah & Babak Baru Diplomasi, Hunain, Tabuk & Puncak Kekuatan Islam, Membangun Masyarakat Madinah, Nasab & Kelahiran Nabi, Perang Badr & Dampaknya, Perang Khandaq hingga Bani Mushthaliq, Perang Mu'tah & Penaklukan Makkah, Perang Uhud & Satuan Pasukan Pasca Uhud

### Komunitas 9 — 8 event
Top events: Kelahiran Nabi, Wahyu Pertama, Pemboikotan Bani Hasyim, Tahun Berduka, Hijrah Ke Habasyah, Haji Wada', Mi'Raj, Isra' Mi'raj
Period coverage: Awal Kenabian & Mandat Dakwah, Dakwah Jahriyah & Tekanan Quraisy, Dakwah di Luar Makkah & Isra Mi'raj, Nasab & Kelahiran Nabi, Penaklukan Makkah hingga Akhir Kenabian


## Catatan Interpretasi

- **PageRank tertinggi** = event yang paling banyak "didukung" oleh event lain (banyak shared persons + co-occur dengan event sentral).
- **Betweenness tinggi** = event yang ada di jalur shortest path antar kelompok event lain (jembatan antar fase Sirah).
- **Co-participation rule** punya bias: event dengan banyak Person (mis. Perang Badr 39 person) otomatis punya degree tinggi. Pakai weighted_degree + frekuensi untuk konteks tambahan.
- **PRECEDES kronologi** punya kontribusi kecil (12 edges) — co-participation tetap dominan signal.