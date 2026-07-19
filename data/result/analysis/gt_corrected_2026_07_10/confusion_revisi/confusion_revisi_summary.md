# Confusion Matrix Dua Level — Revisi Sidang (Dosen-1 poin 4)

> Dibuat `confusion_dosen_revisi.py`. Angka = gold terkoreksi 2026-07-10, tanpa menjalankan model (reuse `recompute_gt_corrected.py`). **Dua level dibedakan tegas:**


- **Entity-level (span, Bab 4):** 4 tipe entitas + margin deteksi. Blok inti 4×4 = kecocokan tipe (diagonal benar, off-diagonal SALAH TIPE). Kolom *TAK TERDETEKSI* = span gold yang tak diprediksi (FN). Baris *SPURIOUS* = span pred yang tak ada di gold (FP). File: `entity_level/<skenario>.png`.
- **Token-level BIO (lampiran):** 9 kelas `B-`/`I-` tiap entitas + `O` — memperlihatkan bahwa evaluasi token BIO **bukan 4 kelas**. File: `bio_token/<skenario>.png`.


## Ringkasan entity-level (urut jumlah span benar)

| Skenario | Span benar | Salah tipe | Tak terdeteksi (FN) | Spurious (FP) | Total error deteksi |
|---|---:|---:|---:|---:|---:|
| S4-augmentation ⭐ | 1921 | 3 | 45 | 45 | 90 |
| S1-baseline (indolem uncased) | 1880 | 3 | 86 | 91 | 177 |
| S3a-SCL | 1880 | 4 | 85 | 86 | 171 |
| S2-weighted-CE | 1877 | 6 | 86 | 108 | 194 |
| S3b-JSCL | 1868 | 6 | 95 | 110 | 205 |
| S5-POS-tag | 1864 | 6 | 99 | 66 | 165 |
| B-distilbert | 1813 | 6 | 150 | 89 | 239 |
| B-cahya-bert-1.5G | 1809 | 3 | 157 | 115 | 272 |
| B-roberta (indo) | 1680 | 18 | 271 | 497 | 768 |
| B-indobert-cased (p1) | 1640 | 15 | 314 | 595 | 909 |

## Interpretasi (skenario pemenang `S4-augmentation`)

Dari **1969** entitas acuan: **1921 benar**, hanya **3 salah tipe** (antar-kelas), **45 tak terdeteksi**, **45 spurious**. **Kesimpulan yang bisa ditulis di Bab 4:** kesalahan model **didominasi deteksi (FN+FP = 90), bukan kekeliruan tipe entitas (3)** — model sudah memahami perbedaan 4 tipe; sisa kesalahan ada di batas span / entitas yang terlewat, konsisten dengan temuan few-shot pada kelas minoritas.
