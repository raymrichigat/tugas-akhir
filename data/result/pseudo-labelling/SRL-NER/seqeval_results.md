# Seqeval Entity-Level Evaluation

> Dihasilkan oleh `src/pseudo_labelling/SRL-NER/evaluate_seqeval.py`

> Metric: seqeval span-based (entity-level), bukan token-level sklearn.


## 1. Ringkasan F1

| Tag | F1 entity | Precision | Recall |
|---|---:|---:|---:|
| S1-baseline-base | 0.9237 | 0.9135 | 0.9342 |
| S1-baseline-iter6 | 0.9529 | 0.9468 | 0.9592 |
| S2a-scl-base | 0.8900 | 0.8618 | 0.9200 |
| S2a-scl-iter5 | 0.9221 | 0.9077 | 0.9370 |
| S2a-scl-iter6 | 0.9129 | 0.8957 | 0.9308 |
| S2b-jscl-iter5 | 0.8811 | 0.8506 | 0.9138 |
| S2b-jscl-iter6 | 0.8927 | 0.8605 | 0.9274 |
| S3.1-scl-lambda01-base | 0.9247 | 0.9193 | 0.9302 |
| S3.1-scl-lambda01-iter6 | 0.9489 | 0.9394 | 0.9586 |
| S3.1-scl-lambda02-base | 0.9254 | 0.9087 | 0.9427 |
| S3.1-scl-lambda02-iter5 | 0.9482 | 0.9364 | 0.9603 |
| S3.1-scl-lambda03-base | 0.9209 | 0.9112 | 0.9308 |
| S3.1-scl-lambda03-iter4 | 0.9534 | 0.9439 | 0.9631 |
| S3.2-scl-aug-base | 0.9332 | 0.9159 | 0.9512 |
| S3.2-scl-aug-iter4 | 0.9549 | 0.9440 | 0.9660 |

## 2. Per-entity classification_report

### S1-baseline-base

```
              precision    recall  f1-score   support

       EVENT     0.7692    0.7843    0.7767        51
    LOCATION     0.9113    0.9376    0.9243       449
      PERSON     0.9345    0.9487    0.9416      1189
        TIME     0.7073    0.7838    0.7436        74

   micro avg     0.9135    0.9342    0.9237      1763
   macro avg     0.8306    0.8636    0.8465      1763
weighted avg     0.9143    0.9342    0.9241      1763
```

### S1-baseline-iter6

```
              precision    recall  f1-score   support

       EVENT     0.8077    0.8235    0.8155        51
    LOCATION     0.9615    0.9465    0.9540       449
      PERSON     0.9586    0.9739    0.9662      1189
        TIME     0.7857    0.8919    0.8354        74

   micro avg     0.9468    0.9592    0.9529      1763
   macro avg     0.8784    0.9090    0.8928      1763
weighted avg     0.9477    0.9592    0.9532      1763
```

### S2a-scl-base

```
              precision    recall  f1-score   support

       EVENT     0.7692    0.7843    0.7767        51
    LOCATION     0.9189    0.9332    0.9260       449
      PERSON     0.8549    0.9319    0.8918      1189
        TIME     0.7051    0.7432    0.7237        74

   micro avg     0.8618    0.9200    0.8900      1763
   macro avg     0.8120    0.8482    0.8295      1763
weighted avg     0.8625    0.9200    0.8901      1763
```

### S2a-scl-iter5

```
              precision    recall  f1-score   support

       EVENT     0.8125    0.7647    0.7879        51
    LOCATION     0.9401    0.9443    0.9422       449
      PERSON     0.9043    0.9453    0.9243      1189
        TIME     0.8333    0.8784    0.8553        74

   micro avg     0.9077    0.9370    0.9221      1763
   macro avg     0.8726    0.8832    0.8774      1763
weighted avg     0.9078    0.9370    0.9220      1763
```

### S2a-scl-iter6

```
              precision    recall  f1-score   support

       EVENT     0.8478    0.7647    0.8041        51
    LOCATION     0.9346    0.9555    0.9449       449
      PERSON     0.8862    0.9302    0.9077      1189
        TIME     0.8481    0.9054    0.8758        74

   micro avg     0.8957    0.9308    0.9129      1763
   macro avg     0.8792    0.8889    0.8831      1763
weighted avg     0.8958    0.9308    0.9128      1763
```

### S2b-jscl-iter5

```
              precision    recall  f1-score   support

       EVENT     0.8696    0.7843    0.8247        51
    LOCATION     0.9469    0.9532    0.9501       449
      PERSON     0.8173    0.9066    0.8596      1189
        TIME     0.8442    0.8784    0.8609        74

   micro avg     0.8506    0.9138    0.8811      1763
   macro avg     0.8695    0.8806    0.8738      1763
weighted avg     0.8529    0.9138    0.8817      1763
```

### S2b-jscl-iter6

```
              precision    recall  f1-score   support

       EVENT     0.8200    0.8039    0.8119        51
    LOCATION     0.9209    0.9599    0.9400       449
      PERSON     0.8486    0.9243    0.8849      1189
        TIME     0.7356    0.8649    0.7950        74

   micro avg     0.8605    0.9274    0.8927      1763
   macro avg     0.8313    0.8883    0.8579      1763
weighted avg     0.8615    0.9274    0.8930      1763
```

### S3.1-scl-lambda01-base

```
              precision    recall  f1-score   support

       EVENT     0.7455    0.8039    0.7736        51
    LOCATION     0.9168    0.9332    0.9249       449
      PERSON     0.9453    0.9453    0.9453      1189
        TIME     0.6747    0.7568    0.7134        74

   micro avg     0.9193    0.9302    0.9247      1763
   macro avg     0.8206    0.8598    0.8393      1763
weighted avg     0.9209    0.9302    0.9254      1763
```

### S3.1-scl-lambda01-iter6

```
              precision    recall  f1-score   support

       EVENT     0.8163    0.7843    0.8000        51
    LOCATION     0.9553    0.9510    0.9531       449
      PERSON     0.9454    0.9748    0.9598      1189
        TIME     0.8312    0.8649    0.8477        74

   micro avg     0.9394    0.9586    0.9489      1763
   macro avg     0.8870    0.8937    0.8902      1763
weighted avg     0.9393    0.9586    0.9488      1763
```

### S3.1-scl-lambda02-base

```
              precision    recall  f1-score   support

       EVENT     0.7736    0.8039    0.7885        51
    LOCATION     0.9152    0.9376    0.9263       449
      PERSON     0.9268    0.9588    0.9425      1189
        TIME     0.6977    0.8108    0.7500        74

   micro avg     0.9087    0.9427    0.9254      1763
   macro avg     0.8283    0.8778    0.8518      1763
weighted avg     0.9098    0.9427    0.9259      1763
```

### S3.1-scl-lambda02-iter5

```
              precision    recall  f1-score   support

       EVENT     0.8400    0.8235    0.8317        51
    LOCATION     0.9449    0.9555    0.9502       449
      PERSON     0.9453    0.9731    0.9590      1189
        TIME     0.8125    0.8784    0.8442        74

   micro avg     0.9364    0.9603    0.9482      1763
   macro avg     0.8857    0.9076    0.8962      1763
weighted avg     0.9366    0.9603    0.9482      1763
```

### S3.1-scl-lambda03-base

```
              precision    recall  f1-score   support

       EVENT     0.6964    0.7647    0.7290        51
    LOCATION     0.9069    0.9332    0.9199       449
      PERSON     0.9376    0.9479    0.9427      1189
        TIME     0.6914    0.7568    0.7226        74

   micro avg     0.9112    0.9308    0.9209      1763
   macro avg     0.8081    0.8506    0.8285      1763
weighted avg     0.9125    0.9308    0.9215      1763
```

### S3.1-scl-lambda03-iter4

```
              precision    recall  f1-score   support

       EVENT     0.8367    0.8039    0.8200        51
    LOCATION     0.9448    0.9532    0.9490       449
      PERSON     0.9588    0.9781    0.9684      1189
        TIME     0.7857    0.8919    0.8354        74

   micro avg     0.9439    0.9631    0.9534      1763
   macro avg     0.8815    0.9068    0.8932      1763
weighted avg     0.9444    0.9631    0.9536      1763
```

### S3.2-scl-aug-base

```
              precision    recall  f1-score   support

       EVENT     0.8302    0.8627    0.8462        51
    LOCATION     0.9345    0.9532    0.9438       449
      PERSON     0.9257    0.9638    0.9444      1189
        TIME     0.7195    0.7973    0.7564        74

   micro avg     0.9159    0.9512    0.9332      1763
   macro avg     0.8525    0.8943    0.8727      1763
weighted avg     0.9165    0.9512    0.9335      1763
```

### S3.2-scl-aug-iter4

```
              precision    recall  f1-score   support

       EVENT     0.9000    0.8824    0.8911        51
    LOCATION     0.9395    0.9688    0.9539       449
      PERSON     0.9514    0.9714    0.9613      1189
        TIME     0.8831    0.9189    0.9007        74

   micro avg     0.9440    0.9660    0.9549      1763
   macro avg     0.9185    0.9354    0.9267      1763
weighted avg     0.9440    0.9660    0.9549      1763
```
