# Error Analysis NER — Model Pemenang S3.2 (scl-aug iter-4)

> Dihasilkan oleh `src/pseudo_labelling/SRL-NER/error_analysis.py`. Prediksi ulang `test.csv` (258 chunk) dengan word-level alignment.


**Validasi**: seqeval F1 entity (recompute) = **0.9498** (bandingkan angka resmi 0.9537 di `seqeval_results.md`; selisih kecil = wajar karena metode alignment word-level vs char-offset pipeline).


```
              precision    recall  f1-score   support

       EVENT     0.8367    0.8723    0.8542        47
    LOCATION     0.9371    0.9621    0.9495       449
      PERSON     0.9482    0.9697    0.9588      1189
        TIME     0.8462    0.8919    0.8684        74

   micro avg     0.9379    0.9619    0.9498      1759
   macro avg     0.8920    0.9240    0.9077      1759
weighted avg     0.9381    0.9619    0.9498      1759
```


## 1. Confusion Matrix Token-Level (tipe)

![confusion](confusion_matrix_token.png)


Baris = gold, kolom = prediksi. Diagonal = benar.

| gold＼pred | O | PERSON | LOCATION | EVENT | TIME |
| --- | ---: | ---: | ---: | ---: | ---: |
| O | 39326 | 71 | 34 | 9 | 9 |
| PERSON | 37 | 2265 | 0 | 0 | 0 |
| LOCATION | 12 | 2 | 459 | 2 | 0 |
| EVENT | 7 | 1 | 0 | 92 | 0 |
| TIME | 15 | 0 | 0 | 0 | 217 |

**Pembacaan per kelas (token):**

- **PERSON**: 2302 token gold → 37 jadi `O` (tak terdeteksi, 1.6%), salah-tipe ke: —.
- **LOCATION**: 475 token gold → 12 jadi `O` (tak terdeteksi, 2.5%), salah-tipe ke: PERSON 2, EVENT 2.
- **EVENT**: 100 token gold → 7 jadi `O` (tak terdeteksi, 7.0%), salah-tipe ke: PERSON 1.
- **TIME**: 232 token gold → 15 jadi `O` (tak terdeteksi, 6.5%), salah-tipe ke: —.


- **O → kelas** (token bukan-entitas yang salah ditandai entitas): PERSON 71, LOCATION 34, EVENT 9, TIME 9.


## 2. Breakdown Error Level Span (Entitas)

Untuk tiap entitas gold: EXACT (benar) / TYPE (boundary benar, tipe salah) / BOUNDARY (overlap tapi batas beda) / MISSED (tak terdeteksi). SPURIOUS = prediksi entitas yang tidak ada di gold.

| Kelas | Gold | EXACT | TYPE | BOUNDARY | MISSED | Recall span | SPURIOUS(FP) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PERSON | 1189 | 1153 | 0 | 14 | 22 | 0.970 | 46 |
| LOCATION | 449 | 432 | 2 | 3 | 12 | 0.962 | 28 |
| EVENT | 47 | 41 | 0 | 3 | 3 | 0.872 | 4 |
| TIME | 74 | 66 | 0 | 6 | 2 | 0.892 | 5 |

> *Recall span* = EXACT / total gold (entitas yang benar persis batas+tipe).


**Misklasifikasi tipe (boundary benar, tipe salah):**

| Gold → Pred | Jumlah |
| --- | ---: |
| LOCATION → PERSON | 2 |

## 3. Jumlah Entitas per Chunk: Gold vs Prediksi

Menjawab: *"apakah satu unit teks punya 3 entitas di gold tapi terdeteksi 2 (atau sebaliknya)"*. Unit = chunk (`text_id`).


- Total chunk: 258
- Chunk dengan **prediksi < gold** (under-deteksi / ada entitas ke-miss): **18**
- Chunk dengan **prediksi > gold** (over-deteksi / kelebihan): **49**
- Chunk dengan **jumlah sama**: 191 (catatan: jumlah sama belum tentu entitasnya identik)
- Total entitas gold = 1759, total entitas prediksi = 1804


Contoh chunk under-deteksi terbesar (selisih gold−pred):

| text_id | Gold | Pred | Selisih |
| --- | ---: | ---: | ---: |
| 000138-004 | 12 | 8 | 4 |
| 000074-004 | 4 | 1 | 3 |
| 000014-001 | 6 | 3 | 3 |
| 000016-002 | 9 | 6 | 3 |
| 000285-004 | 21 | 18 | 3 |
| 000010-012 | 18 | 16 | 2 |
| 000360-002 | 6 | 5 | 1 |
| 000359-005 | 6 | 5 | 1 |

## 4. Ringkasan: Mengapa Hasilnya Seperti Itu?

- **EVENT & TIME paling rendah** — konsisten dengan EDA: keduanya kelas minoritas (EVENT 2.7%, TIME 4.2% dari entitas test). Sedikit contoh → model kurang generalisasi.
- **Sumber error dominan** terbaca dari tabel di atas: cek kolom MISSED (recall/under-deteksi) vs TYPE (kebingungan tipe) vs BOUNDARY (batas span, sering karena tanda baca nempel hasil OCR).
- **Artefak OCR** (mis. `Madinah.`, `Rasulullah,`) membuat token entitas mengandung tanda baca → sumber BOUNDARY error.
- Lihat `error_examples.md` untuk contoh konkret tiap kategori (fokus EVENT & TIME).
