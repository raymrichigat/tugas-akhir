# Analisis Error NER Berbasis Data — `done_newest` (per grup)

> Sumber: `*-incorrect.xlsx` (error token-level test set) tiap skenario + `test.csv` (49,739 token, 254 chunk). Skor entity-level (seqeval) di `seqeval_done_newest_results.md`; di sini fokus **mengapa** error.

**Catatan:** kategori error di sini bersifat token-level (BIO), sedangkan F1 ringkasan bersifat entity-level (span) — angka absolut bisa beda tipis, tapi pola error konsisten. Semua skenario pakai file error iterasi terakhir yang tersimpan (iter-6).


---

# Grup A — penanganan imbalance (baseline / weighted-CE / SCL / JSCL / augmentation)

### Komposisi error (token-level)

| Skenario | Total err | FP | FN | Mis-tipe | Boundary |
|---|---:|---:|---:|---:|---:|
| S1-baseline | 237 | 153 | 56 | 6 | 22 |
| S2-weighted-CE | 263 | 175 | 50 | 10 | 28 |
| S3a-SCL | 249 | 158 | 58 | 8 | 25 |
| S3b-JSCL | 259 | 170 | 54 | 8 | 27 |
| S4-augmentation | 242 | 168 | 44 | 5 | 25 |

### FN / FP per kelas entitas

| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |
|---|---|---|---|---|
| S1-baseline | 19/80 | 19/33 | 4/6 | 14/34 |
| S2-weighted-CE | 20/89 | 21/32 | 3/8 | 6/46 |
| S3a-SCL | 19/79 | 21/41 | 4/4 | 14/34 |
| S3b-JSCL | 23/88 | 18/34 | 3/4 | 10/44 |
| S4-augmentation | 16/62 | 17/43 | 4/6 | 7/57 |

### Pasangan misklasifikasi tipe (gold→pred) dominan

- **S1-baseline**: {'LOCATION->EVENT': 3, 'LOCATION->PERSON': 1, 'PERSON->LOCATION': 1, 'EVENT->LOCATION': 1}
- **S2-weighted-CE**: {'LOCATION->EVENT': 5, 'PERSON->LOCATION': 2, 'LOCATION->PERSON': 1, 'EVENT->LOCATION': 1, 'LOCATION->TIME': 1}
- **S3a-SCL**: {'LOCATION->EVENT': 3, 'LOCATION->TIME': 2, 'LOCATION->PERSON': 1, 'PERSON->LOCATION': 1, 'EVENT->LOCATION': 1}
- **S3b-JSCL**: {'PERSON->LOCATION': 3, 'LOCATION->EVENT': 3, 'LOCATION->PERSON': 1, 'EVENT->LOCATION': 1}
- **S4-augmentation**: {'LOCATION->EVENT': 4, 'LOCATION->PERSON': 1}

---

# Grup P — fitur POS-tag

### Komposisi error (token-level)

| Skenario | Total err | FP | FN | Mis-tipe | Boundary |
|---|---:|---:|---:|---:|---:|
| S5-POS-tag | 226 | 134 | 60 | 7 | 25 |

### FN / FP per kelas entitas

| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |
|---|---|---|---|---|
| S5-POS-tag | 21/74 | 26/19 | 4/6 | 9/35 |

### Pasangan misklasifikasi tipe (gold→pred) dominan

- **S5-POS-tag**: {'LOCATION->EVENT': 3, 'PERSON->LOCATION': 2, 'LOCATION->PERSON': 1, 'EVENT->LOCATION': 1}

---

# Grup B — model bahasa lain (cased / roberta / cahya / distilbert)

### Komposisi error (token-level)

| Skenario | Total err | FP | FN | Mis-tipe | Boundary |
|---|---:|---:|---:|---:|---:|
| B-indobert-cased | 786 | 368 | 241 | 35 | 142 |
| B-roberta | 688 | 319 | 198 | 34 | 137 |
| B-cahya-1.5G | 274 | 127 | 116 | 7 | 24 |
| B-distilbert | 254 | 115 | 102 | 10 | 27 |

### FN / FP per kelas entitas

| Skenario | PERSON FN/FP | LOCATION FN/FP | EVENT FN/FP | TIME FN/FP |
|---|---|---|---|---|
| B-indobert-cased | 132/236 | 49/29 | 26/30 | 34/73 |
| B-roberta | 124/207 | 33/35 | 11/9 | 30/68 |
| B-cahya-1.5G | 45/68 | 37/19 | 7/3 | 27/37 |
| B-distilbert | 45/53 | 32/17 | 6/2 | 19/43 |

### Pasangan misklasifikasi tipe (gold→pred) dominan

- **B-indobert-cased**: {'PERSON->LOCATION': 9, 'EVENT->LOCATION': 7, 'LOCATION->EVENT': 7, 'LOCATION->PERSON': 6, 'PERSON->TIME': 3, 'LOCATION->TIME': 2}
- **B-roberta**: {'LOCATION->PERSON': 10, 'PERSON->LOCATION': 8, 'LOCATION->TIME': 6, 'LOCATION->EVENT': 5, 'EVENT->LOCATION': 2, 'PERSON->TIME': 1}
- **B-cahya-1.5G**: {'PERSON->LOCATION': 2, 'LOCATION->EVENT': 2, 'LOCATION->PERSON': 1, 'EVENT->PERSON': 1, 'EVENT->LOCATION': 1}
- **B-distilbert**: {'LOCATION->EVENT': 5, 'LOCATION->PERSON': 2, 'EVENT->LOCATION': 2, 'PERSON->LOCATION': 1}

---

# Efek kapitalisasi pada FP/FN

> Menguji temuan inkonsistensi gold: token entitas berawalan huruf besar cenderung ke-anotasi, huruf kecil tidak. Kalau FP condong huruf besar & FN condong huruf besar, sebagian 'error' sebetulnya batas anotasi gold, bukan murni salah model.

| Skenario | %FP awal-kapital | %FN awal-kapital | #FP | #FN |
|---|---:|---:|---:|---:|
| S1-baseline | 71 | 77 | 153 | 56 |
| S2-weighted-CE | 71 | 88 | 175 | 50 |
| S3a-SCL | 74 | 79 | 158 | 58 |
| S3b-JSCL | 70 | 83 | 170 | 54 |
| S4-augmentation | 63 | 84 | 168 | 44 |
| S5-POS-tag | 66 | 87 | 134 | 60 |
| B-indobert-cased | 70 | 86 | 368 | 241 |
| B-roberta | 79 | 82 | 319 | 198 |
| B-cahya-1.5G | 68 | 84 | 127 | 116 |
| B-distilbert | 61 | 81 | 115 | 102 |

### Token FP/FN tersering (baseline vs winner augmentation)

- **S1-baseline — FP tersering**: [('bin', 12), ('bulan', 8), ('Hajar', 6), ('Abbas', 5), ('Baitul-Haram', 4), ('Abu', 4), ('Manaf', 3), ('binti', 3), ('Az-Zubair', 3), ('Qushay', 2)]
- **S1-baseline — FN tersering**: [('Wadi', 4), ('Nakhlah', 4), ('Abdul', 3), ("As'ad", 3), ('atau', 2), ("Al-Isra'", 2), ('tahun', 2), ('41', 2), ('Khandaq', 2), ('Shafa', 2)]
- **S4-augmentation — FP tersering**: [('bin', 12), ('bulan', 9), ('Hajar', 5), ('Abbas', 5), ('Baitul-Haram', 4), ('Abu', 4), ('H', 4), ('Aswad', 3), ('binti', 3), ('tahun', 3)]
- **S4-augmentation — FN tersering**: [('Wadi', 4), ('Nakhlah', 4), ('bulan', 2), ('Abdul', 2), ('Hijrah', 2), ("As'ad", 2), ('Khandaq', 2), ('Hunain', 2), ('Cina', 1), ('Selain', 1)]

---

# Proxy dampak chunking: posisi token error dalam chunk

> Tanpa ablation 'tanpa chunking', efek chunking diuji tak-langsung: apakah error memusat di **tepi chunk** (10% awal/akhir token) tempat konteks terpotong.

| Skenario | err di tepi (%) | err di tengah (%) |
|---|---:|---:|
| S1-baseline | 35 | 65 |
| S2-weighted-CE | 32 | 68 |
| S3a-SCL | 31 | 69 |
| S3b-JSCL | 35 | 65 |
| S4-augmentation | 35 | 65 |
| S5-POS-tag | 35 | 65 |
| B-indobert-cased | 27 | 73 |
| B-roberta | 24 | 76 |
| B-cahya-1.5G | 31 | 69 |
| B-distilbert | 32 | 68 |

_(Pemetaan posisi pakai kemunculan pertama token dalam chunk; perkiraan, bukan indeks presisi.)_