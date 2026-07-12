# Recompute F1 — Ground-Truth Test Terkoreksi (arahan Bu Dini 2026-07-10)

> Dihasilkan `recompute_gt_corrected.py`. Entity-level seqeval, **tanpa menjalankan model**. Satu gold terkoreksi (166 token dari `label baru.xlsx`) dipakai semua skenario; prediksi tiap skenario direkonstruksi dari `*-incorrect.xlsx`-nya (beku). test.csv = 49,739 token / 254 chunk.


> ⚠️ **Caveat keadilan:** koreksi gold diturunkan hanya dari kesalahan skenario **augmentasi**, sehingga augmentasi paling diuntungkan. Wajib disebut jika angka masuk buku.


## F1 entity-level: asli → terkoreksi (urut F1 terkoreksi)

| Skenario | F1 lama | F1 terkoreksi | Δ | PERSON | LOCATION | EVENT | TIME |
|---|---:|---:|---:|---:|---:|---:|---:|
| S4-augmentation | 0.9458 | **0.9756** | +0.0298 | 0.9835 | 0.9755 | 0.9542 | 0.9038 |
| S5-POS-tag | 0.9430 | **0.9547** | +0.0117 | 0.9693 | 0.9466 | 0.9333 | 0.8376 |
| S3a-SCL | 0.9409 | **0.9546** | +0.0137 | 0.9687 | 0.9488 | 0.9600 | 0.8170 |
| S1-baseline (indolem uncased) | 0.9420 | **0.9536** | +0.0116 | 0.9690 | 0.9530 | 0.9342 | 0.7983 |
| S2-weighted-CE | 0.9333 | **0.9480** | +0.0147 | 0.9616 | 0.9432 | 0.9231 | 0.8347 |
| S3b-JSCL | 0.9344 | **0.9451** | +0.0107 | 0.9611 | 0.9467 | 0.9600 | 0.7572 |
| B-distilbert | 0.9347 | **0.9353** | +0.0006 | 0.9581 | 0.9232 | 0.9116 | 0.7479 |
| B-cahya-bert-1.5G | 0.9295 | **0.9286** | -0.0009 | 0.9493 | 0.9232 | 0.9315 | 0.7203 |
| B-roberta (indo) | 0.8049 | **0.8069** | +0.0020 | 0.8135 | 0.8766 | 0.7654 | 0.5404 |
| B-indobert-cased (p1) | 0.7755 | **0.7774** | +0.0020 | 0.7843 | 0.8717 | 0.5549 | 0.5461 |

**Winner: `S4-augmentation` — F1 terkoreksi = 0.9756.**


Koreksi gold: **166 token** berubah (dari 242 baris `label baru.xlsx`).


Confusion matrix per skenario (token-level, 5 kelas, gold terkoreksi): lihat `confusion/<skenario>.png`.


## Classification report per skenario (gold terkoreksi)

### S4-augmentation  (F1 0.9756)
```
              precision    recall  f1-score   support

       EVENT     0.9359    0.9733    0.9542        75
    LOCATION     0.9849    0.9662    0.9755       474
      PERSON     0.9824    0.9846    0.9835      1302
        TIME     0.8926    0.9153    0.9038       118

   micro avg     0.9756    0.9756    0.9756      1969
   macro avg     0.9489    0.9599    0.9543      1969
weighted avg     0.9758    0.9756    0.9757      1969
```

### S5-POS-tag  (F1 0.9547)
```
              precision    recall  f1-score   support

       EVENT     0.9333    0.9333    0.9333        75
    LOCATION     0.9797    0.9156    0.9466       474
      PERSON     0.9693    0.9693    0.9693      1302
        TIME     0.8448    0.8305    0.8376       118

   micro avg     0.9628    0.9467    0.9547      1969
   macro avg     0.9318    0.9122    0.9217      1969
weighted avg     0.9630    0.9467    0.9546      1969
```

### S3a-SCL  (F1 0.9546)
```
              precision    recall  f1-score   support

       EVENT     0.9600    0.9600    0.9600        75
    LOCATION     0.9591    0.9388    0.9488       474
      PERSON     0.9642    0.9731    0.9687      1302
        TIME     0.8205    0.8136    0.8170       118

   micro avg     0.9543    0.9548    0.9546      1969
   macro avg     0.9259    0.9214    0.9236      1969
weighted avg     0.9542    0.9548    0.9545      1969
```

### S1-baseline (indolem uncased)  (F1 0.9536)
```
              precision    recall  f1-score   support

       EVENT     0.9221    0.9467    0.9342        75
    LOCATION     0.9654    0.9409    0.9530       474
      PERSON     0.9643    0.9739    0.9690      1302
        TIME     0.7917    0.8051    0.7983       118

   micro avg     0.9524    0.9548    0.9536      1969
   macro avg     0.9108    0.9166    0.9136      1969
weighted avg     0.9526    0.9548    0.9536      1969
```

### S2-weighted-CE  (F1 0.9480)
```
              precision    recall  f1-score   support

       EVENT     0.8889    0.9600    0.9231        75
    LOCATION     0.9586    0.9283    0.9432       474
      PERSON     0.9525    0.9708    0.9616      1302
        TIME     0.8145    0.8559    0.8347       118

   micro avg     0.9427    0.9533    0.9480      1969
   macro avg     0.9036    0.9288    0.9156      1969
weighted avg     0.9433    0.9533    0.9481      1969
```

### S3b-JSCL  (F1 0.9451)
```
              precision    recall  f1-score   support

       EVENT     0.9600    0.9600    0.9600        75
    LOCATION     0.9569    0.9367    0.9467       474
      PERSON     0.9545    0.9677    0.9611      1302
        TIME     0.7360    0.7797    0.7572       118

   micro avg     0.9415    0.9487    0.9451      1969
   macro avg     0.9019    0.9110    0.9062      1969
weighted avg     0.9422    0.9487    0.9454      1969
```

### B-distilbert  (F1 0.9353)
```
              precision    recall  f1-score   support

       EVENT     0.9306    0.8933    0.9116        75
    LOCATION     0.9612    0.8882    0.9232       474
      PERSON     0.9671    0.9493    0.9581      1302
        TIME     0.7417    0.7542    0.7479       118

   micro avg     0.9502    0.9208    0.9353      1969
   macro avg     0.9001    0.8713    0.8852      1969
weighted avg     0.9508    0.9208    0.9354      1969
```

### B-cahya-bert-1.5G  (F1 0.9286)
```
              precision    recall  f1-score   support

       EVENT     0.9577    0.9067    0.9315        75
    LOCATION     0.9612    0.8882    0.9232       474
      PERSON     0.9500    0.9485    0.9493      1302
        TIME     0.7203    0.7203    0.7203       118

   micro avg     0.9388    0.9187    0.9286      1969
   macro avg     0.8973    0.8659    0.8811      1969
weighted avg     0.9392    0.9187    0.9286      1969
```

### B-roberta (indo)  (F1 0.8069)
```
              precision    recall  f1-score   support

       EVENT     0.7126    0.8267    0.7654        75
    LOCATION     0.9000    0.8544    0.8766       474
      PERSON     0.7619    0.8725    0.8135      1302
        TIME     0.4611    0.6525    0.5404       118

   micro avg     0.7654    0.8532    0.8069      1969
   macro avg     0.7089    0.8015    0.7490      1969
weighted avg     0.7752    0.8532    0.8105      1969
```

### B-indobert-cased (p1)  (F1 0.7774)
```
              precision    recall  f1-score   support

       EVENT     0.4898    0.6400    0.5549        75
    LOCATION     0.8991    0.8460    0.8717       474
      PERSON     0.7257    0.8533    0.7843      1302
        TIME     0.4571    0.6780    0.5461       118

   micro avg     0.7289    0.8329    0.7774      1969
   macro avg     0.6429    0.7543    0.6893      1969
weighted avg     0.7423    0.8329    0.7824      1969
```
