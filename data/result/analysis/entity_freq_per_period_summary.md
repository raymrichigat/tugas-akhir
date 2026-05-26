# Frekuensi Entitas per Period — Manual Labelling (nodes_v2.csv)

**Sumber:** `nodes_v2.csv` (892 nodes hasil manual labelling Sirah Mubarakfuri,
post review periodisasi 2026-05-12). Mapping chunk_id → period via
`sirah_chunks_final.csv` (halaman) + `period_mapping.json` v2 (page range).

**Coverage:** 3737 (entity, chunk) tuples successfully assigned
to 1 dari 15 period. 247 unmapped (chunk halaman > 600, end-matter).

## Pivot — Unique Entities per Period

Setiap kolom hitung **unique** entity name yang muncul di period itu.
Catatan: entity yang sama bisa muncul di beberapa period (mis. Muhammad
muncul di P0-P14), jadi sum kolom > unique-entity-total di nodes_v2.

| period_id | period_label | phase | PERSON | EVENT | LOCATION | TIME | TOTAL |
|---|---|---|---|---|---|---|---|
| P0 | Konteks Arab Jahiliyah | Fase I — Pra-Islam & Latar Belakang | 89 | 0 | 34 | 20 | 143 |
| P1 | Nasab & Kelahiran Nabi | Fase I — Pra-Islam & Latar Belakang | 77 | 1 | 13 | 7 | 98 |
| P2 | Awal Kenabian & Mandat Dakwah | Fase II — Periode Makkah | 20 | 0 | 4 | 11 | 35 |
| P3 | Dakwah Sirriyah | Fase II — Periode Makkah | 36 | 0 | 3 | 0 | 39 |
| P4 | Dakwah Jahriyah & Tekanan Quraisy | Fase II — Periode Makkah | 81 | 2 | 10 | 5 | 98 |
| P5 | Dakwah di Luar Makkah & Isra Mi'raj | Fase II — Periode Makkah | 107 | 6 | 17 | 8 | 138 |
| P6 | Hijrah ke Madinah | Fase II — Periode Makkah | 52 | 1 | 11 | 14 | 78 |
| P7 | Membangun Masyarakat Madinah | Fase III — Periode Madinah Awal | 50 | 9 | 12 | 13 | 84 |
| P8 | Perang Badr & Dampaknya | Fase IV — Periode Peperangan Besar | 77 | 4 | 12 | 10 | 103 |
| P9 | Perang Uhud & Satuan Pasukan Pasca Uhud | Fase IV — Periode Peperangan Besar | 82 | 8 | 11 | 14 | 115 |
| P10 | Perang Khandaq hingga Bani Mushthaliq | Fase IV — Periode Peperangan Besar | 100 | 6 | 13 | 22 | 141 |
| P11 | Hudaibiyah & Babak Baru Diplomasi | Fase V — Diplomasi & Ekspansi | 107 | 7 | 17 | 18 | 149 |
| P12 | Perang Mu'tah & Penaklukan Makkah | Fase V — Diplomasi & Ekspansi | 70 | 5 | 12 | 4 | 91 |
| P13 | Hunain, Tabuk & Puncak Kekuatan Islam | Fase VI — Konsolidasi & Akhir Kenabian | 79 | 4 | 17 | 12 | 112 |
| P14 | Masuknya Umat & Haji Wada' | Fase VI — Konsolidasi & Akhir Kenabian | 54 | 3 | 21 | 32 | 110 |

## Pivot — Total Occurrences per Period

Hitung pasangan (entity, chunk_id) — proxy untuk seberapa sering entity
muncul dalam narasi period. Lebih tinggi = lebih banyak penyebutan.

| period_id | period_label | phase | PERSON | EVENT | LOCATION | TIME | TOTAL |
|---|---|---|---|---|---|---|---|
| P0 | Konteks Arab Jahiliyah | Fase I — Pra-Islam & Latar Belakang | 158 | 0 | 153 | 22 | 333 |
| P1 | Nasab & Kelahiran Nabi | Fase I — Pra-Islam & Latar Belakang | 152 | 2 | 61 | 7 | 222 |
| P2 | Awal Kenabian & Mandat Dakwah | Fase II — Periode Makkah | 53 | 0 | 15 | 18 | 86 |
| P3 | Dakwah Sirriyah | Fase II — Periode Makkah | 44 | 0 | 4 | 0 | 48 |
| P4 | Dakwah Jahriyah & Tekanan Quraisy | Fase II — Periode Makkah | 208 | 4 | 36 | 9 | 257 |
| P5 | Dakwah di Luar Makkah & Isra Mi'raj | Fase II — Periode Makkah | 232 | 12 | 92 | 8 | 344 |
| P6 | Hijrah ke Madinah | Fase II — Periode Makkah | 135 | 1 | 42 | 17 | 195 |
| P7 | Membangun Masyarakat Madinah | Fase III — Periode Madinah Awal | 120 | 10 | 61 | 16 | 207 |
| P8 | Perang Badr & Dampaknya | Fase IV — Periode Peperangan Besar | 181 | 19 | 65 | 10 | 275 |
| P9 | Perang Uhud & Satuan Pasukan Pasca Uhud | Fase IV — Periode Peperangan Besar | 173 | 26 | 57 | 16 | 272 |
| P10 | Perang Khandaq hingga Bani Mushthaliq | Fase IV — Periode Peperangan Besar | 283 | 20 | 61 | 32 | 396 |
| P11 | Hudaibiyah & Babak Baru Diplomasi | Fase V — Diplomasi & Ekspansi | 275 | 16 | 113 | 27 | 431 |
| P12 | Perang Mu'tah & Penaklukan Makkah | Fase V — Diplomasi & Ekspansi | 138 | 6 | 39 | 5 | 188 |
| P13 | Hunain, Tabuk & Puncak Kekuatan Islam | Fase VI — Konsolidasi & Akhir Kenabian | 170 | 10 | 68 | 16 | 264 |
| P14 | Masuknya Umat & Haji Wada' | Fase VI — Konsolidasi & Akhir Kenabian | 103 | 6 | 68 | 42 | 219 |

## Observasi awal

- **PERSON dominan di** P5 (`Dakwah di Luar Makkah & Isra Mi'raj`) dengan **107** unique entitas.
- **PERSON paling sedikit di** P2 (`Awal Kenabian & Mandat Dakwah`) dengan **20** unique entitas.
- **EVENT dominan di** P7 (`Membangun Masyarakat Madinah`) dengan **9** unique events.
- **Period tanpa EVENT entitas:** P0, P2, P3 (kandidat untuk EVENT augmentation target).
- **LOCATION dominan di** P0 (`Konteks Arab Jahiliyah`) dengan **34** unique lokasi.

## Top 5 Entitas per Period (PERSON saja, untuk gambaran narasi)

### P0 — Konteks Arab Jahiliyah

  1. **Ibrahim** (16 occurrences)
  2. **Isma'il** (12 occurrences)
  3. **Muhammad** (8 occurrences)
  4. **Ibnu Hisyam** (5 occurrences)
  5. **Kisra** (4 occurrences)

### P1 — Nasab & Kelahiran Nabi

  1. **Muhammad** (21 occurrences)
  2. **Ibnu Hisyam** (15 occurrences)
  3. **Abdul Muththalib** (13 occurrences)
  4. **Abu Thalib** (6 occurrences)
  5. **Halimah** (5 occurrences)

### P2 — Awal Kenabian & Mandat Dakwah

  1. **Muhammad** (14 occurrences)
  2. **Jibril** (6 occurrences)
  3. **Khadijah** (5 occurrences)
  4. **Waraqah bin Naufal** (4 occurrences)
  5. **Musa bin Imran** (3 occurrences)

### P3 — Dakwah Sirriyah

  1. **Muhammad** (4 occurrences)
  2. **Ibnu Hisyam** (4 occurrences)
  3. **Abu Bakar** (2 occurrences)
  4. **Ali bin Abu Thalib** (2 occurrences)
  5. **Ibnu Luhai'ah** (1 occurrences)

### P4 — Dakwah Jahriyah & Tekanan Quraisy

  1. **Muhammad** (36 occurrences)
  2. **Abu Thalib** (18 occurrences)
  3. **Abu Jahal** (13 occurrences)
  4. **Ibnu Ishaq** (9 occurrences)
  5. **Umar bin Al-Khaththab** (7 occurrences)

### P5 — Dakwah di Luar Makkah & Isra Mi'raj

  1. **Muhammad** (34 occurrences)
  2. **Ibnu Hisyam** (9 occurrences)
  3. **Mush'ab bin Umair** (8 occurrences)
  4. **As'ad bin Zurarah** (6 occurrences)
  5. **Ibnu Ishaq** (6 occurrences)

### P6 — Hijrah ke Madinah

  1. **Muhammad** (27 occurrences)
  2. **Abu Bakar** (19 occurrences)
  3. **Aisyah** (5 occurrences)
  4. **Abu Jahal** (4 occurrences)
  5. **Ibnu Ishaq** (4 occurrences)

### P7 — Membangun Masyarakat Madinah

  1. **Muhammad** (40 occurrences)
  2. **Abdullah bin Jahsy** (4 occurrences)
  3. **Ibnu Hisyam** (4 occurrences)
  4. **Abdullah bin Salam** (4 occurrences)
  5. **Ibnu Ishaq** (3 occurrences)

### P8 — Perang Badr & Dampaknya

  1. **Muhammad** (39 occurrences)
  2. **Abu Sufyan bin Harb** (6 occurrences)
  3. **Ka'b bin Malik** (6 occurrences)
  4. **Ka'b bin Al-Asyraf** (6 occurrences)
  5. **Ibnu Hisyam** (5 occurrences)

### P9 — Perang Uhud & Satuan Pasukan Pasca Uhud

  1. **Muhammad** (37 occurrences)
  2. **Abu Sufyan bin Harb** (9 occurrences)
  3. **Ali bin Abu Thalib** (8 occurrences)
  4. **Umar bin Al-Khaththab** (5 occurrences)
  5. **Ibnu Hisyam** (5 occurrences)

### P10 — Perang Khandaq hingga Bani Mushthaliq

  1. **Muhammad** (64 occurrences)
  2. **Abdullah bin Ubay bin Salul** (11 occurrences)
  3. **Zaid bin Haritsah** (10 occurrences)
  4. **Aisyah** (7 occurrences)
  5. **Ka'b bin Asad** (7 occurrences)

### P11 — Hudaibiyah & Babak Baru Diplomasi

  1. **Muhammad** (65 occurrences)
  2. **Umar bin Al-Khaththab** (11 occurrences)
  3. **Najasyi** (9 occurrences)
  4. **Heraklius** (7 occurrences)
  5. **Ali bin Abu Thalib** (7 occurrences)

### P12 — Perang Mu'tah & Penaklukan Makkah

  1. **Muhammad** (28 occurrences)
  2. **Abu Sufyan bin Harb** (12 occurrences)
  3. **Abdullah bin Rawahah** (6 occurrences)
  4. **Umar bin Al-Khaththab** (4 occurrences)
  5. **Ali bin Abu Thalib** (4 occurrences)

### P13 — Hunain, Tabuk & Puncak Kekuatan Islam

  1. **Muhammad** (48 occurrences)
  2. **Malik bin Auf** (7 occurrences)
  3. **Uyainah bin Hishn** (5 occurrences)
  4. **Adi bin Hatim** (4 occurrences)
  5. **Al-Aqra' bin Habis** (4 occurrences)

### P14 — Masuknya Umat & Haji Wada'

  1. **Muhammad** (29 occurrences)
  2. **Ali bin Abu Thalib** (4 occurrences)
  3. **Usamah bin Zaid** (3 occurrences)
  4. **Abu Bakar** (3 occurrences)
  5. **Ka'b bin Malik** (3 occurrences)

## Implikasi untuk Bab 4

1. Dominasi entitas per period dapat dipakai sebagai justifikasi struktur naratif
   buku Mubarakfuri — period dengan event-density tinggi (mis. P8 Perang Badr,
   P9 Pasca-Badr) mengandung lebih banyak entitas PERSON & EVENT.
2. Period dengan EVENT pool kecil konsisten dengan filosofi buku Sirah yang fokus
   pada karakter & dakwah (banyak PERSON, sedikit EVENT) pada fase pra-peperangan.
3. Saat dijalankan di output SRL-NER (post-S3.1/S3.2), kita bisa quantify
   dampak augmentation terhadap distribusi minor classes (B-EVENT, I-LOCATION)
   per period — apakah augmentation menyamaratakan atau mempertahankan struktur.
