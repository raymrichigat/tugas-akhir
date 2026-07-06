# Seqeval Entity-Level — `done_newest` (re-run penuh 10 skenario)

> Dihasilkan `seqeval_done_newest.py`. Entity-level (span) seqeval, **tanpa menjalankan model**: prediksi test direkonstruksi dari `*-correct.xlsx` + `*-incorrect.xlsx`. test.csv sama untuk semua (49,739 token / 254 chunk).


## Ringkasan (F1 entity-level, urut skenario)

| Skenario | F1 | Precision | Recall | PERSON | LOCATION | EVENT | TIME |
|---|---:|---:|---:|---:|---:|---:|---:|
| S1-baseline (indolem uncased) | 0.9420 | 0.9255 | 0.9591 | 0.9577 | 0.9440 | 0.8800 | 0.7890 |
| S2-weighted-CE | 0.9333 | 0.9131 | 0.9543 | 0.9495 | 0.9361 | 0.8571 | 0.7838 |
| S3a-SCL | 0.9409 | 0.9254 | 0.9570 | 0.9581 | 0.9376 | 0.8919 | 0.7814 |
| S3b-JSCL | 0.9344 | 0.9158 | 0.9538 | 0.9474 | 0.9463 | 0.9054 | 0.7534 |
| S4-augmentation | 0.9458 | 0.9304 | 0.9617 | 0.9653 | 0.9453 | 0.8874 | 0.7580 |
| S5-POS-tag | 0.9430 | 0.9354 | 0.9507 | 0.9571 | 0.9484 | 0.8649 | 0.8037 |
| B-indobert-cased (p1) | 0.7755 | 0.7160 | 0.8457 | 0.7784 | 0.8849 | 0.5263 | 0.5421 |
| B-roberta (indo) | 0.8049 | 0.7517 | 0.8661 | 0.8048 | 0.8921 | 0.7500 | 0.5434 |
| B-cahya-bert-1.5G | 0.9295 | 0.9242 | 0.9349 | 0.9455 | 0.9380 | 0.8889 | 0.7315 |
| B-distilbert | 0.9347 | 0.9340 | 0.9354 | 0.9544 | 0.9357 | 0.8690 | 0.7431 |

**Winner: `S4-augmentation` — F1 = 0.9458.**


## Diagnostik rekonstruksi

| Skenario | file incorrect | #error token | ditempatkan | token-acc |
|---|---|---:|---:|---:|
| S1-baseline (indolem uncased) | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 237 | 237 | 0.9952 |
| S2-weighted-CE | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 263 | 263 | 0.9947 |
| S3a-SCL | bert-only-sirah-ner-S2a-scl-iterative-6-incorrect.xlsx | 249 | 249 | 0.9950 |
| S3b-JSCL | bert-only-sirah-ner-S2b-jscl-iterative-6-incorrect.xlsx | 259 | 259 | 0.9948 |
| S4-augmentation | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 242 | 242 | 0.9951 |
| S5-POS-tag | bert-pos-sirah-ner-iterative-6-incorrect.xlsx | 226 | 226 | 0.9955 |
| B-indobert-cased (p1) | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 786 | 786 | 0.9842 |
| B-roberta (indo) | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 688 | 688 | 0.9862 |
| B-cahya-bert-1.5G | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 274 | 274 | 0.9945 |
| B-distilbert | bert-only-sirah-ner-iterative-6-incorrect.xlsx | 254 | 254 | 0.9949 |

## Classification report per skenario (seqeval)

### S1-baseline (indolem uncased)
```
              precision    recall  f1-score   support

       EVENT     0.8571    0.9041    0.8800        73
    LOCATION     0.9307    0.9577    0.9440       449
      PERSON     0.9468    0.9689    0.9577      1285
        TIME     0.7167    0.8776    0.7890        98

   micro avg     0.9255    0.9591    0.9420      1905
   macro avg     0.8628    0.9271    0.8927      1905
weighted avg     0.9277    0.9591    0.9428      1905
```

### S2-weighted-CE
```
              precision    recall  f1-score   support

       EVENT     0.8148    0.9041    0.8571        73
    LOCATION     0.9259    0.9465    0.9361       449
      PERSON     0.9344    0.9650    0.9495      1285
        TIME     0.7016    0.8878    0.7838        98

   micro avg     0.9131    0.9543    0.9333      1905
   macro avg     0.8442    0.9258    0.8816      1905
weighted avg     0.9159    0.9543    0.9343      1905
```

### S3a-SCL
```
              precision    recall  f1-score   support

       EVENT     0.8800    0.9041    0.8919        73
    LOCATION     0.9224    0.9532    0.9376       449
      PERSON     0.9475    0.9689    0.9581      1285
        TIME     0.7179    0.8571    0.7814        98

   micro avg     0.9254    0.9570    0.9409      1905
   macro avg     0.8670    0.9208    0.8922      1905
weighted avg     0.9272    0.9570    0.9416      1905
```

### S3b-JSCL
```
              precision    recall  f1-score   support

       EVENT     0.8933    0.9178    0.9054        73
    LOCATION     0.9310    0.9621    0.9463       449
      PERSON     0.9348    0.9603    0.9474      1285
        TIME     0.6720    0.8571    0.7534        98

   micro avg     0.9158    0.9538    0.9344      1905
   macro avg     0.8578    0.9244    0.8881      1905
weighted avg     0.9188    0.9538    0.9356      1905
```

### S4-augmentation
```
              precision    recall  f1-score   support

       EVENT     0.8590    0.9178    0.8874        73
    LOCATION     0.9290    0.9621    0.9453       449
      PERSON     0.9579    0.9728    0.9653      1285
        TIME     0.6860    0.8469    0.7580        98

   micro avg     0.9304    0.9617    0.9458      1905
   macro avg     0.8580    0.9249    0.8890      1905
weighted avg     0.9333    0.9617    0.9469      1905
```

### S5-POS-tag
```
              precision    recall  f1-score   support

       EVENT     0.8533    0.8767    0.8649        73
    LOCATION     0.9549    0.9421    0.9484       449
      PERSON     0.9508    0.9634    0.9571      1285
        TIME     0.7414    0.8776    0.8037        98

   micro avg     0.9354    0.9507    0.9430      1905
   macro avg     0.8751    0.9149    0.8935      1905
weighted avg     0.9373    0.9507    0.9436      1905
```

### B-indobert-cased (p1)
```
              precision    recall  f1-score   support

       EVENT     0.4592    0.6164    0.5263        73
    LOCATION     0.8879    0.8820    0.8849       449
      PERSON     0.7159    0.8529    0.7784      1285
        TIME     0.4229    0.7551    0.5421        98

   micro avg     0.7160    0.8457    0.7755      1905
   macro avg     0.6215    0.7766    0.6829      1905
weighted avg     0.7315    0.8457    0.7817      1905
```

### B-roberta (indo)
```
              precision    recall  f1-score   support

       EVENT     0.6897    0.8219    0.7500        73
    LOCATION     0.8911    0.8931    0.8921       449
      PERSON     0.7492    0.8693    0.8048      1285
        TIME     0.4311    0.7347    0.5434        98

   micro avg     0.7517    0.8661    0.8049      1905
   macro avg     0.6903    0.8297    0.7476      1905
weighted avg     0.7640    0.8661    0.8098      1905
```

### B-cahya-bert-1.5G
```
              precision    recall  f1-score   support

       EVENT     0.9014    0.8767    0.8889        73
    LOCATION     0.9498    0.9265    0.9380       449
      PERSON     0.9400    0.9510    0.9455      1285
        TIME     0.6695    0.8061    0.7315        98

   micro avg     0.9242    0.9349    0.9295      1905
   macro avg     0.8652    0.8901    0.8760      1905
weighted avg     0.9269    0.9349    0.9305      1905
```

### B-distilbert
```
              precision    recall  f1-score   support

       EVENT     0.8750    0.8630    0.8690        73
    LOCATION     0.9475    0.9243    0.9357       449
      PERSON     0.9570    0.9518    0.9544      1285
        TIME     0.6750    0.8265    0.7431        98

   micro avg     0.9340    0.9354    0.9347      1905
   macro avg     0.8636    0.8914    0.8755      1905
weighted avg     0.9371    0.9354    0.9358      1905
```
