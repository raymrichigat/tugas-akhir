# Rincian Error Token-level — Gold Terkoreksi (Bu Dini 2026-07-10)

> Dihasilkan `error_breakdown_gt_corrected.py`. Kategori: FP=over-deteksi (O→entitas), FN=terlewat (entitas→O), MIS=salah tipe, BND=batas B/I. Gold terkoreksi (166 token).


## Ringkasan per skenario

| Skenario | Total error | FP (over) | FN (terlewat) | Misklasifikasi | Boundary B/I |
|---|---:|---:|---:|---:|---:|
| S1-baseline (indolem uncased) | 165 | 55 (33%) | 98 (59%) | 5 (3%) | 7 (4%) |
| S2-weighted-CE | 174 | 69 (40%) | 84 (48%) | 11 (6%) | 10 (6%) |
| S3a-SCL | 178 | 62 (35%) | 102 (57%) | 7 (4%) | 7 (4%) |
| S3b-JSCL | 185 | 69 (37%) | 93 (50%) | 12 (6%) | 11 (6%) |
| S4-augmentation | 78 | 25 (32%) | 41 (53%) | 4 (5%) | 8 (10%) |
| S5-POS-tag | 164 | 40 (24%) | 106 (65%) | 10 (6%) | 8 (5%) |
| B-indobert-cased (p1) | 774 | 292 (38%) | 305 (39%) | 39 (5%) | 138 (18%) |
| B-roberta (indo) | 677 | 243 (36%) | 262 (39%) | 39 (6%) | 133 (20%) |
| B-cahya-bert-1.5G | 263 | 58 (22%) | 187 (71%) | 6 (2%) | 12 (5%) |
| B-distilbert | 228 | 41 (18%) | 168 (74%) | 9 (4%) | 10 (4%) |

## FN per kelas

| Skenario | PERSON | LOCATION | EVENT | TIME |
|---|---:|---:|---:|---:|
| S1-baseline (indolem uncased) | 26 | 33 | 3 | 36 |
| S2-weighted-CE | 27 | 35 | 1 | 21 |
| S3a-SCL | 29 | 33 | 2 | 38 |
| S3b-JSCL | 29 | 31 | 2 | 31 |
| S4-augmentation | 15 | 17 | 2 | 7 |
| S5-POS-tag | 28 | 43 | 2 | 33 |
| B-indobert-cased (p1) | 149 | 73 | 24 | 59 |
| B-roberta (indo) | 136 | 58 | 10 | 58 |
| B-cahya-bert-1.5G | 65 | 65 | 6 | 51 |
| B-distilbert | 64 | 60 | 6 | 38 |

## FP per kelas

| Skenario | PERSON | LOCATION | EVENT | TIME |
|---|---:|---:|---:|---:|
| S1-baseline (indolem uncased) | 38 | 11 | 3 | 3 |
| S2-weighted-CE | 45 | 12 | 4 | 8 |
| S3a-SCL | 40 | 17 | 0 | 5 |
| S3b-JSCL | 40 | 16 | 1 | 12 |
| S4-augmentation | 12 | 7 | 2 | 4 |
| S5-POS-tag | 28 | 4 | 2 | 6 |
| B-indobert-cased (p1) | 200 | 22 | 26 | 44 |
| B-roberta (indo) | 165 | 29 | 6 | 43 |
| B-cahya-bert-1.5G | 39 | 11 | 0 | 8 |
| B-distilbert | 23 | 9 | 0 | 9 |