# Seqeval Entity-Level Evaluation

> Dihasilkan oleh `src/pseudo_labelling/SRL-NER/evaluate_seqeval.py`

> Metric: seqeval span-based (entity-level), bukan token-level sklearn.


## 1. Ringkasan F1

| Tag | F1 entity | Precision | Recall |
|---|---:|---:|---:|
| S1-baseline-base | 0.9225 | 0.9113 | 0.9341 |
| S1-baseline-iter6 | 0.9518 | 0.9446 | 0.9591 |
| S2a-scl-base | 0.8888 | 0.8597 | 0.9198 |
| S2a-scl-iter5 | 0.9215 | 0.9060 | 0.9375 |
| S2a-scl-iter6 | 0.9123 | 0.8941 | 0.9312 |
| S2b-jscl-iter5 | 0.8798 | 0.8485 | 0.9136 |
| S2b-jscl-iter6 | 0.8915 | 0.8584 | 0.9272 |
| S3.1-scl-lambda01-base | 0.9235 | 0.9170 | 0.9301 |
| S3.1-scl-lambda01-iter6 | 0.9477 | 0.9372 | 0.9585 |
| S3.1-scl-lambda02-base | 0.9242 | 0.9065 | 0.9426 |
| S3.1-scl-lambda02-iter5 | 0.9470 | 0.9342 | 0.9602 |
| S3.1-scl-lambda03-base | 0.9197 | 0.9089 | 0.9306 |
| S3.1-scl-lambda03-iter4 | 0.9522 | 0.9416 | 0.9630 |
| S3.2-scl-aug-base | 0.9320 | 0.9137 | 0.9511 |
| S3.2-scl-aug-iter4 | 0.9537 | 0.9418 | 0.9659 |

## 2. Per-entity classification_report

### S1-baseline-base

```
              precision    recall  f1-score   support

       EVENT     0.6923    0.7660    0.7273        47
    LOCATION     0.9113    0.9376    0.9243       449
      PERSON     0.9345    0.9487    0.9416      1189
        TIME     0.7073    0.7838    0.7436        74

   micro avg     0.9113    0.9341    0.9225      1759
   macro avg     0.8114    0.8590    0.8342      1759
weighted avg     0.9126    0.9341    0.9231      1759
```

### S1-baseline-iter6

```
              precision    recall  f1-score   support

       EVENT     0.7308    0.8085    0.7677        47
    LOCATION     0.9615    0.9465    0.9540       449
      PERSON     0.9586    0.9739    0.9662      1189
        TIME     0.7857    0.8919    0.8354        74

   micro avg     0.9446    0.9591    0.9518      1759
   macro avg     0.8592    0.9052    0.8808      1759
weighted avg     0.9460    0.9591    0.9523      1759
```

### S2a-scl-base

```
              precision    recall  f1-score   support

       EVENT     0.6923    0.7660    0.7273        47
    LOCATION     0.9189    0.9332    0.9260       449
      PERSON     0.8549    0.9319    0.8918      1189
        TIME     0.7051    0.7432    0.7237        74

   micro avg     0.8597    0.9198    0.8888      1759
   macro avg     0.7928    0.8436    0.8172      1759
weighted avg     0.8606    0.9198    0.8890      1759
```

### S2a-scl-iter5

```
              precision    recall  f1-score   support

       EVENT     0.7500    0.7660    0.7579        47
    LOCATION     0.9401    0.9443    0.9422       449
      PERSON     0.9043    0.9453    0.9243      1189
        TIME     0.8333    0.8784    0.8553        74

   micro avg     0.9060    0.9375    0.9215      1759
   macro avg     0.8569    0.8835    0.8699      1759
weighted avg     0.9063    0.9375    0.9216      1759
```

### S2a-scl-iter6

```
              precision    recall  f1-score   support

       EVENT     0.7826    0.7660    0.7742        47
    LOCATION     0.9346    0.9555    0.9449       449
      PERSON     0.8862    0.9302    0.9077      1189
        TIME     0.8481    0.9054    0.8758        74

   micro avg     0.8941    0.9312    0.9123      1759
   macro avg     0.8629    0.8893    0.8757      1759
weighted avg     0.8942    0.9312    0.9123      1759
```

### S2b-jscl-iter5

```
              precision    recall  f1-score   support

       EVENT     0.7826    0.7660    0.7742        47
    LOCATION     0.9469    0.9532    0.9501       449
      PERSON     0.8173    0.9066    0.8596      1189
        TIME     0.8442    0.8784    0.8609        74

   micro avg     0.8485    0.9136    0.8798      1759
   macro avg     0.8477    0.8761    0.8612      1759
weighted avg     0.8506    0.9136    0.8805      1759
```

### S2b-jscl-iter6

```
              precision    recall  f1-score   support

       EVENT     0.7400    0.7872    0.7629        47
    LOCATION     0.9209    0.9599    0.9400       449
      PERSON     0.8486    0.9243    0.8849      1189
        TIME     0.7356    0.8649    0.7950        74

   micro avg     0.8584    0.9272    0.8915      1759
   macro avg     0.8113    0.8841    0.8457      1759
weighted avg     0.8594    0.9272    0.8919      1759
```

### S3.1-scl-lambda01-base

```
              precision    recall  f1-score   support

       EVENT     0.6727    0.7872    0.7255        47
    LOCATION     0.9168    0.9332    0.9249       449
      PERSON     0.9453    0.9453    0.9453      1189
        TIME     0.6747    0.7568    0.7134        74

   micro avg     0.9170    0.9301    0.9235      1759
   macro avg     0.8024    0.8556    0.8273      1759
weighted avg     0.9194    0.9301    0.9245      1759
```

### S3.1-scl-lambda01-iter6

```
              precision    recall  f1-score   support

       EVENT     0.7347    0.7660    0.7500        47
    LOCATION     0.9553    0.9510    0.9531       449
      PERSON     0.9454    0.9748    0.9598      1189
        TIME     0.8312    0.8649    0.8477        74

   micro avg     0.9372    0.9585    0.9477      1759
   macro avg     0.8666    0.8891    0.8777      1759
weighted avg     0.9374    0.9585    0.9478      1759
```

### S3.1-scl-lambda02-base

```
              precision    recall  f1-score   support

       EVENT     0.6981    0.7872    0.7400        47
    LOCATION     0.9152    0.9376    0.9263       449
      PERSON     0.9268    0.9588    0.9425      1189
        TIME     0.6977    0.8108    0.7500        74

   micro avg     0.9065    0.9426    0.9242      1759
   macro avg     0.8095    0.8736    0.8397      1759
weighted avg     0.9081    0.9426    0.9249      1759
```

### S3.1-scl-lambda02-iter5

```
              precision    recall  f1-score   support

       EVENT     0.7600    0.8085    0.7835        47
    LOCATION     0.9449    0.9555    0.9502       449
      PERSON     0.9453    0.9731    0.9590      1189
        TIME     0.8125    0.8784    0.8442        74

   micro avg     0.9342    0.9602    0.9470      1759
   macro avg     0.8657    0.9039    0.8842      1759
weighted avg     0.9346    0.9602    0.9472      1759
```

### S3.1-scl-lambda03-base

```
              precision    recall  f1-score   support

       EVENT     0.6250    0.7447    0.6796        47
    LOCATION     0.9069    0.9332    0.9199       449
      PERSON     0.9376    0.9479    0.9427      1189
        TIME     0.6914    0.7568    0.7226        74

   micro avg     0.9089    0.9306    0.9197      1759
   macro avg     0.7902    0.8456    0.8162      1759
weighted avg     0.9111    0.9306    0.9206      1759
```

### S3.1-scl-lambda03-iter4

```
              precision    recall  f1-score   support

       EVENT     0.7551    0.7872    0.7708        47
    LOCATION     0.9448    0.9532    0.9490       449
      PERSON     0.9588    0.9781    0.9684      1189
        TIME     0.7857    0.8919    0.8354        74

   micro avg     0.9416    0.9630    0.9522      1759
   macro avg     0.8611    0.9026    0.8809      1759
weighted avg     0.9425    0.9630    0.9525      1759
```

### S3.2-scl-aug-base

```
              precision    recall  f1-score   support

       EVENT     0.7547    0.8511    0.8000        47
    LOCATION     0.9345    0.9532    0.9438       449
      PERSON     0.9257    0.9638    0.9444      1189
        TIME     0.7195    0.7973    0.7564        74

   micro avg     0.9137    0.9511    0.9320      1759
   macro avg     0.8336    0.8914    0.8611      1759
weighted avg     0.9147    0.9511    0.9325      1759
```

### S3.2-scl-aug-iter4

```
              precision    recall  f1-score   support

       EVENT     0.8200    0.8723    0.8454        47
    LOCATION     0.9395    0.9688    0.9539       449
      PERSON     0.9514    0.9714    0.9613      1189
        TIME     0.8831    0.9189    0.9007        74

   micro avg     0.9418    0.9659    0.9537      1759
   macro avg     0.8985    0.9329    0.9153      1759
weighted avg     0.9420    0.9659    0.9538      1759
```
