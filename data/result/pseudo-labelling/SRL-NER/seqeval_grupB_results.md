# Seqeval Grup A + Grup B (done_running)

> Dihasilkan `run_eval_done_running.py`. Entity-level seqeval, test.csv sama untuk semua.


## Ringkasan

| Skenario | model | F1 | Precision | Recall | F1 EVENT | F1 TIME |
|---|---|---:|---:|---:|---:|---:|
| S1-baseline (indolem uncased) | bert-only-sirah-ner-0.9-iteration-6 | 0.9481 | 0.9489 | 0.9472 | 0.8039 | 0.8408 |
| S2-weighted-CE | bert-only-sirah-ner-0.9-iteration-6 | 0.9393 | 0.9224 | 0.9569 | 0.7767 | 0.7898 |
| S2a-SCL | bert-only-sirah-ner-S2a-scl-0.9-iteration-4 | 0.9512 | 0.9407 | 0.9620 | 0.8200 | 0.8258 |
| S2b-JSCL | bert-only-sirah-ner-S2b-jscl-0.9-iteration-6 | 0.9434 | 0.9324 | 0.9546 | 0.8367 | 0.8408 |
| S4-augmentation | bert-only-sirah-ner-0.9-iteration-5 | 0.9581 | 0.9554 | 0.9609 | 0.9020 | 0.8627 |
| GrupB-indobert-cased | bert-only-sirah-ner-0.9-iteration-6 | 0.7770 | 0.7244 | 0.8378 | 0.6226 | 0.4532 |
| GrupB-cahya-bert-1.5G | bert-only-sirah-ner-0.9-iteration-6 | 0.9324 | 0.9148 | 0.9507 | 0.8119 | 0.8000 |
| GrupB-distilbert | bert-only-sirah-ner-0.9-iteration-6 | 0.9442 | 0.9287 | 0.9603 | 0.8200 | 0.7722 |
| GrupB-roberta | bert-only-sirah-ner-0.9-iteration-6 | 0.8068 | 0.7657 | 0.8525 | 0.6306 | 0.5291 |

## Per-kelas lengkap

### S1-baseline (indolem uncased) (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.8039    0.8039    0.8039        51
    LOCATION     0.9636    0.9421    0.9527       449
      PERSON     0.9604    0.9588    0.9596      1189
        TIME     0.7952    0.8919    0.8408        74

   micro avg     0.9489    0.9472    0.9481      1763
   macro avg     0.8808    0.8992    0.8892      1763
weighted avg     0.9497    0.9472    0.9483      1763
```

### S2-weighted-CE (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.7692    0.7843    0.7767        51
    LOCATION     0.9221    0.9488    0.9352       449
      PERSON     0.9407    0.9748    0.9575      1189
        TIME     0.7470    0.8378    0.7898        74

   micro avg     0.9224    0.9569    0.9393      1763
   macro avg     0.8448    0.8864    0.8648      1763
weighted avg     0.9229    0.9569    0.9395      1763
```

### S2a-SCL (bert-only-sirah-ner-S2a-scl-0.9-iteration-4)
```
              precision    recall  f1-score   support

       EVENT     0.8367    0.8039    0.8200        51
    LOCATION     0.9390    0.9599    0.9493       449
      PERSON     0.9555    0.9756    0.9655      1189
        TIME     0.7901    0.8649    0.8258        74

   micro avg     0.9407    0.9620    0.9512      1763
   macro avg     0.8803    0.9011    0.8902      1763
weighted avg     0.9409    0.9620    0.9513      1763
```

### S2b-JSCL (bert-only-sirah-ner-S2b-jscl-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.8723    0.8039    0.8367        51
    LOCATION     0.9301    0.9488    0.9394       449
      PERSON     0.9449    0.9672    0.9559      1189
        TIME     0.7952    0.8919    0.8408        74

   micro avg     0.9324    0.9546    0.9434      1763
   macro avg     0.8856    0.9029    0.8932      1763
weighted avg     0.9328    0.9546    0.9434      1763
```

### S4-augmentation (bert-only-sirah-ner-0.9-iteration-5)
```
              precision    recall  f1-score   support

       EVENT     0.9020    0.9020    0.9020        51
    LOCATION     0.9707    0.9599    0.9653       449
      PERSON     0.9600    0.9680    0.9640      1189
        TIME     0.8354    0.8919    0.8627        74

   micro avg     0.9554    0.9609    0.9581      1763
   macro avg     0.9170    0.9305    0.9235      1763
weighted avg     0.9558    0.9609    0.9583      1763
```

### GrupB-indobert-cased (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.6000    0.6471    0.6226        51
    LOCATION     0.9197    0.8931    0.9062       449
      PERSON     0.7026    0.8385    0.7646      1189
        TIME     0.3566    0.6216    0.4532        74

   micro avg     0.7244    0.8378    0.7770      1763
   macro avg     0.6447    0.7501    0.6867      1763
weighted avg     0.7404    0.8378    0.7835      1763
```

### GrupB-cahya-bert-1.5G (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.8200    0.8039    0.8119        51
    LOCATION     0.9424    0.9465    0.9444       449
      PERSON     0.9184    0.9655    0.9414      1189
        TIME     0.7654    0.8378    0.8000        74

   micro avg     0.9148    0.9507    0.9324      1763
   macro avg     0.8615    0.8885    0.8744      1763
weighted avg     0.9152    0.9507    0.9325      1763
```

### GrupB-distilbert (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.8367    0.8039    0.8200        51
    LOCATION     0.9447    0.9510    0.9478       449
      PERSON     0.9402    0.9790    0.9592      1189
        TIME     0.7262    0.8243    0.7722        74

   micro avg     0.9287    0.9603    0.9442      1763
   macro avg     0.8620    0.8896    0.8748      1763
weighted avg     0.9294    0.9603    0.9444      1763
```

### GrupB-roberta (bert-only-sirah-ner-0.9-iteration-6)
```
              precision    recall  f1-score   support

       EVENT     0.5833    0.6863    0.6306        51
    LOCATION     0.9101    0.9020    0.9060       449
      PERSON     0.7543    0.8520    0.8002      1189
        TIME     0.4348    0.6757    0.5291        74

   micro avg     0.7657    0.8525    0.8068      1763
   macro avg     0.6706    0.7790    0.7165      1763
weighted avg     0.7756    0.8525    0.8108      1763
```
