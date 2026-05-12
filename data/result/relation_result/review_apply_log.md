# Apply Review to KG — Log

**Source files:** `nodes.csv`, `edges.csv`
**Review file:** `event_period_review_v2.csv`
**Output files:** `nodes_v2.csv`, `edges_v2.csv`

## Nodes Changes

| Action | Count |
|---|---:|
| EVENT keep        | 19 |
| EVENT fixed (F)   | 10 |
| EVENT removed (R) | 12 |
| EVENT added (ADD) | 7 |
| non-EVENT untouched | 856 |
| **Total nodes_v2** | **892** |

## Edges Changes

| Action | Count |
|---|---:|
| keep                  | 126 |
| period_label updated  | 196 |
| removed (event R'd)   | 48 |
| **Total edges_v2** | **322** |

## Events Removed (R)

- `Hijrah`
- `Isra'`
- `Mi'raj`
- `Perang Asafan`
- `Perang Badr Aisyah`
- `Perang Badr Beberapa`
- `Perang Bani Al`
- `Perang Bu'ats`
- `Perang Bukhtanashar`
- `Perang Khaibar Bekas`
- `Perang Riddah`
- `Perang Yarmuk`

## Events Added (ADD, ghost nodes)

- `Wahyu Pertama` → **P2** (Awal Kenabian & Mandat Dakwah, p.94-99)
- `Bi'tsah Nabawiyah` → **P2** (Awal Kenabian & Mandat Dakwah, p.94-99)
- `Dakwah Sirriyah` → **P3** (Dakwah Sirriyah, p.106-109)
- `Hijrah ke Madinah` → **P6** (Hijrah ke Madinah, p.218-232)
- `Haji Wada'` → **P14** (Masuknya Umat & Haji Wada', p.594-600)
- `Khutbah Wada'` → **P14** (Masuknya Umat & Haji Wada', p.594-600)
- `Hijrah ke Habasyah` → **P5** (Dakwah di Luar Makkah & Isra Mi'raj, p.130-151)

## Events Fixed (F)

- `Fathul Makkah` → **P12** (Perang Mu'tah & Penaklukan Makkah, p.502-536)
- `Ghazwah Dzatu Qarad` → **P11** (Hudaibiyah & Babak Baru Diplomasi, p.433-501)
- `Perang Abwa'` → **P8** (Perang Badr & Dampaknya, p.266-323)
- `Perang Badr` → **P8** (Perang Badr & Dampaknya, p.266-323)
- `Perang Badr Shughra` → **P9** (Perang Uhud & Satuan Pasukan Pasca Uhud, p.324-389)
- `Perang Badr Ula` → **P9** (Perang Uhud & Satuan Pasukan Pasca Uhud, p.324-389)
- `Perang Bani Mushthaliq` → **P10** (Perang Khandaq hingga Bani Mushthaliq, p.390-432)
- `Perang Dzul Usyairah` → **P8** (Perang Badr & Dampaknya, p.266-323)
- `Perang Khandaq` → **P10** (Perang Khandaq hingga Bani Mushthaliq, p.390-432)
- `Perang Uhud` → **P9** (Perang Uhud & Satuan Pasukan Pasca Uhud, p.324-389)
