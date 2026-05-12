# Studi Kasus 5 Event Berperiode Jauh — Knowledge Graph Sirah

Studi kasus mengikuti revisi Bu Diana cluster #2 (2026-05-03):
> *"Kasus Perang Badar, diamati keterlibatan nya apa saja lalu diamati graf nya... ambil beberapa contoh 3 atau 5 event, dengan periode yang jauh. Tunjukkan dalam graf seperti apa lalu di analisis."*

5 event dipilih dari rentang periodisasi P8 → P13 (page 266 → 571, total ~300 halaman jarak).

## 1. Ringkasan 5 Event

| # | Event | Period | Halaman | Persons | Locations | Times |
|:---:|---|---|---|---:|---:|---:|
| 1 | **Perang Badr** | P8 | 266-304 | 39 | 4 | 6 |
| 2 | **Perang Uhud** | P9 | 324-375 | 18 | 3 | 6 |
| 3 | **Perjanjian Hudaibiyah** | P11 | 433-450 | 3 | 1 | 1 |
| 4 | **Perang Khaibar** | P11 | 473-492 | 5 | 2 | 2 |
| 5 | **Perang Tabuk** | P13 | 558-571 | 6 | 0 | 1 |

**Total unique Person yang muncul di salah satu dari 5 event:** 60

**Person yang muncul di ≥2 event (8 orang):**

| Person | Total event | Events |
|---|---:|---|
| Muhammad | 5 / 5 | Perang Badr, Perang Uhud, Perjanjian Hudaibiyah, Perang Khaibar, Perang Tabuk |
| Abu Jahal | 2 / 5 | Perang Badr, Perang Uhud |
| Abu Sufyan bin Harb | 2 / 5 | Perang Badr, Perang Uhud |
| Abu Azzah | 2 / 5 | Perang Badr, Perang Uhud |
| Abu Hurairah | 2 / 5 | Perang Badr, Perang Khaibar |
| Abu Musa | 2 / 5 | Perang Badr, Perang Khaibar |
| Amr bin Umayyah | 2 / 5 | Perang Uhud, Perang Tabuk |
| Salamah bin Al-Akwa' | 2 / 5 | Perjanjian Hudaibiyah, Perang Khaibar |

## 2. Detail per Event

### Perang Badr

**Period:** `P8` — *Perang Badr & Dampaknya*
**Halaman:** 266-304
**Justifikasi pemilihan:** Frequency tertinggi (44) — peperangan kunci awal periode Madinah, milestone teologis (penaklukan Quraisy pertama)

**Sub-graph metrics:**

| Metric | Value |
|---|---:|
| Person involved | 39 |
| Location attached | 4 |
| Time attached | 6 |
| Pairwise person co-participation | 741 |
| Density person-clique (by definition all INVOLVED_IN sama event = clique) | 1.0 |
| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | 16 |

**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**

| Rank | Person | Total events di-INVOLVED_IN |
|:---:|---|---:|
| 1 | Muhammad | 17 |
| 2 | Ali bin Abu Thalib | 6 |
| 3 | Zaid bin Haritsah | 4 |
| 4 | Abu Hurairah | 3 |
| 5 | Abu Musa | 3 |

**Locations:** Yatsrib, Madinah, Badr, Makkah

**Times:** bulan Syawwal 2 H, bulan Dzul Hijjah, bulan Jumada, bulan Rabi'ul Awwal, Jumadil Ula, tahun 3 H

**Direct Person-Person relations dalam scope (16):**

- **KELUARGA** (8):
  - `Muhammad` ↔ `Abu Lahab` (pasangan)
  - `Abu Sufyan bin Harb` ↔ `Abu Jahal` (anak)
  - `Abu Lahab` ↔ `Abu Jahal` (anak)
  - `Muhammad` ↔ `Abu Jahal` (anak)
  - `Hamzah bin Abdul Muththalib` ↔ `Abu Jahal` (anak)
  - ... (+3 lagi)
- **MUSUH** (2):
  - `Umar bin Al-Khaththab` ↔ `Muhammad` (musuh)
  - `Abu Sufyan bin Harb` ↔ `Muhammad` (musuh)
- **SAHABAT** (6):
  - `Umar bin Al-Khaththab` ↔ `Abu Jahal` (sekutu)
  - `Umair bin Wahb` ↔ `Shafwan bin Umayyah` (sekutu)
  - `Wahb bin Umair` ↔ `Shafwan bin Umayyah` (sekutu)
  - `Muhammad` ↔ `Shafwan bin Umayyah` (sekutu)
  - `Abu Sufyan bin Harb` ↔ `Hakim bin Hizam` (sekutu)
  - ... (+1 lagi)

**Semua Person yang terlibat (39):**

<details><summary>klik untuk expand</summary>

Abdullah bin Abbas, Abdullah bin Abu Rabi'ah, Abdullah bin Ubay bin Salul, Abdurrahman bin Auf, Abu Azzah, Abu Hurairah, Abu Jahal, Abu Lahab, Abu Lubabah bin Abdul, Abu Musa, Abu Rasulullah, Abu Sufyan bin Harb, Abul Ash bin Ar-Rabi', Al-Abbas bin Abdul Muththalib, Ali bin Abu Thalib, Amr bin Al-Ash, Furat bin Hayyan, Hakim bin Hizam, Hamzah bin Abdul Muththalib, Hasan bin Ali, Hujair bin Abu Ihab, Husain bin Ali, Ibnu Ummi, Ikrimah bin Abu Jahal, Khunais bin Hudzafah, Kurz bin Jabir, Muhammad, Najasyi, Shafwan bin Umayyah, Siba bin Arfazhah, Ukkasyah bin Mihshan, Umair bin Wahb, Umar bin Al-Khaththab, Ummu Kultsum, Utsman bin Affan, Wahb bin Umair, Zaid bin Ad-Dastinah, Zaid bin Haritsah, Zainab

</details>

### Perang Uhud

**Period:** `P9` — *Perang Uhud & Satuan Pasukan Pasca Uhud*
**Halaman:** 324-375
**Justifikasi pemilihan:** Kekalahan strategis pertama umat Islam; trauma & konsolidasi pasca-perang

**Sub-graph metrics:**

| Metric | Value |
|---|---:|
| Person involved | 18 |
| Location attached | 3 |
| Time attached | 6 |
| Pairwise person co-participation | 153 |
| Density person-clique (by definition all INVOLVED_IN sama event = clique) | 1.0 |
| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | 10 |

**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**

| Rank | Person | Total events di-INVOLVED_IN |
|:---:|---|---:|
| 1 | Muhammad | 17 |
| 2 | Amr bin Umayyah | 3 |
| 3 | Abu Bakar | 2 |
| 4 | Abu Azzah | 2 |
| 5 | Abu Sufyan bin Harb | 2 |

**Locations:** Aqabah, Madinah, Hunain

**Times:** bulan Muharram 3 H, bulan Jumada, bulan Rabi'ul Awwal 4 H, bulan Jumadil Ula, bulan Muharram 4 H, tahun 4 H

**Direct Person-Person relations dalam scope (10):**

- **KELUARGA** (8):
  - `Abu Sufyan bin Harb` ↔ `Abu Jahal` (anak)
  - `Abu Bakar` ↔ `Muhammad` (anak)
  - `Muhammad` ↔ `Aisyah` (pasangan)
  - `Muhammad` ↔ `Abu Jahal` (anak)
  - `Ka'b bin Al-Asyraf` ↔ `Muhammad` (anak)
  - ... (+3 lagi)
- **SAHABAT** (1):
  - `Muhammad` ↔ `Abu Bakar` (sekutu)
- **MUSUH** (1):
  - `Abu Sufyan bin Harb` ↔ `Muhammad` (musuh)

**Semua Person yang terlibat (18):**

<details><summary>klik untuk expand</summary>

Abdullah bin Jahsy, Abu Azzah, Abu Bakar, Abu Jahal, Abu Salamah bin Abdul Asad, Abu Sufyan bin Harb, Aisyah, Amr bin Umayyah, As'ad bin Zurarah, Hilal bin Amir bin Sha'sha'ah, Ibnu Abdi, Ka'b bin Al-Asyraf, Khalid bin Al-Walid, Muhammad, Ubay bin Khalaf, Ummu Salamah, Urwah bin Az-Zubair, Yalail bin Abdi

</details>

### Perjanjian Hudaibiyah

**Period:** `P11` — *Hudaibiyah & Babak Baru Diplomasi*
**Halaman:** 433-450
**Justifikasi pemilihan:** Diplomatic milestone — gencatan senjata yang membuka era ekspansi non-militer

**Sub-graph metrics:**

| Metric | Value |
|---|---:|
| Person involved | 3 |
| Location attached | 1 |
| Time attached | 1 |
| Pairwise person co-participation | 3 |
| Density person-clique (by definition all INVOLVED_IN sama event = clique) | 1.0 |
| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | 0 |

**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**

| Rank | Person | Total events di-INVOLVED_IN |
|:---:|---|---:|
| 1 | Muhammad | 17 |
| 2 | Salamah bin Al-Akwa' | 2 |
| 3 | Abrahah | 1 |

**Locations:** Hudaibiyah

**Times:** bulan Ramadhan

**Semua Person yang terlibat (3):**

<details><summary>klik untuk expand</summary>

Abrahah, Muhammad, Salamah bin Al-Akwa'

</details>

### Perang Khaibar

**Period:** `P11` — *Hudaibiyah & Babak Baru Diplomasi*
**Halaman:** 473-492
**Justifikasi pemilihan:** Post-Hudaibiyah, melawan komunitas Yahudi terbesar di sekitar Madinah

**Sub-graph metrics:**

| Metric | Value |
|---|---:|
| Person involved | 5 |
| Location attached | 2 |
| Time attached | 2 |
| Pairwise person co-participation | 10 |
| Density person-clique (by definition all INVOLVED_IN sama event = clique) | 1.0 |
| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | 0 |

**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**

| Rank | Person | Total events di-INVOLVED_IN |
|:---:|---|---:|
| 1 | Muhammad | 17 |
| 2 | Abu Hurairah | 3 |
| 3 | Abu Musa | 3 |
| 4 | Salamah bin Al-Akwa' | 2 |
| 5 | Amir bin Al-Akwa' | 1 |

**Locations:** Khaibar, Hudaibiyah

**Times:** bulan Rabi'ul Awwal, Jumadil Ula

**Semua Person yang terlibat (5):**

<details><summary>klik untuk expand</summary>

Abu Hurairah, Abu Musa, Amir bin Al-Akwa', Muhammad, Salamah bin Al-Akwa'

</details>

### Perang Tabuk

**Period:** `P13` — *Hunain, Tabuk & Puncak Kekuatan Islam*
**Halaman:** 558-571
**Justifikasi pemilihan:** Ekspedisi militer terakhir Nabi — terhadap Romawi, mencapai batas utara Jazirah Arab

**Sub-graph metrics:**

| Metric | Value |
|---|---:|
| Person involved | 6 |
| Location attached | 0 |
| Time attached | 1 |
| Pairwise person co-participation | 15 |
| Density person-clique (by definition all INVOLVED_IN sama event = clique) | 1.0 |
| Direct Person-Person relations (KELUARGA/SAHABAT/MUSUH) dalam scope | 0 |

**Top 5 Person yang terlibat (sorted by total event participation di seluruh KG):**

| Rank | Person | Total events di-INVOLVED_IN |
|:---:|---|---:|
| 1 | Muhammad | 17 |
| 2 | Amr bin Umayyah | 3 |
| 3 | Al-Harits bin Abdi | 1 |
| 4 | Nu'man bin Qail | 1 |
| 5 | Mu'adz bin Jabal | 1 |

**Locations:** _(tidak ada)_

**Times:** tahun 9 H

**Semua Person yang terlibat (6):**

<details><summary>klik untuk expand</summary>

Al-Harits bin Abdi, Amr bin Umayyah, Malik bin An-Namath, Mu'adz bin Jabal, Muhammad, Nu'man bin Qail

</details>

## 3. Analisis Komparatif

### 3.1 Density per event

Setiap event yang punya ≥2 Person otomatis form **clique** di sub-graph (semua Person INVOLVED_IN sama event → pairwise terhubung via shared participation). Density per-event-subgraph = 1.0 by construction. 

Implikasi: density bukan metric yang informatif untuk single event. Yang informatif:
- **Size** (n_persons) — semakin besar event, semakin banyak orang terlibat
- **Direct Person-Person relations** dalam scope — quality of relationships
- **Cross-event overlap** — tokoh yang lintas-zaman = bridge structural

### 3.2 Cross-event analysis

Dari 5 event ini, **1 Person** muncul di ≥3 event (lihat tabel di section 1). Tokoh-tokoh ini adalah **hubs lintas-zaman** — mereka membentuk struktur backbone Knowledge Graph Sirah.

Hipotesis untuk dianalisis di Bab 4:
- Tokoh hubs lintas-zaman = sahabat utama yang terlibat di mayoritas event Sirah
- Tokoh single-event = peripheral (mungkin partisipan specific atau noise NER)
- Density direct relations berkorelasi dengan **kohesi internal** event (perang besar punya lebih banyak relasi keluarga/sahabat antar peserta)

### 3.3 Limitasi

- Sub-graph hanya dari relasi yang **ter-ekstraksi NER + relation_extraction**. Tokoh yang real-life terlibat tapi tidak disebut di teks chunk akan miss.
- Density=1.0 by construction → tidak bisa membandingkan kohesi antar event secara langsung dari metric ini. Pakai n_persons + direct_relations sebagai proxy.
- Event yang frequency rendah (mis. Hudaibiyah freq=11) cenderung punya Person count lebih sedikit — bias coverage NER, bukan ground truth keterlibatan historis.
