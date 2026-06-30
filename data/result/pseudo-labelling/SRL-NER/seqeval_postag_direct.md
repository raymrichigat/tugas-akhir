# Seqeval POS-tag — inference LANGSUNG (bukan rekonstruksi)

> `eval_postag_direct.py`, checkpoint iter-4, test.csv (258 chunk / 42558 token). Entity-level seqeval.

**micro**  Precision=0.9286  Recall=0.9597  **F1=0.9439**

```
              precision    recall  f1-score   support

       EVENT     0.8750    0.8235    0.8485        51
    LOCATION     0.9262    0.9510    0.9385       449
      PERSON     0.9408    0.9756    0.9579      1189
        TIME     0.7875    0.8514    0.8182        74

   micro avg     0.9286    0.9597    0.9439      1763
   macro avg     0.8824    0.9004    0.8908      1763
weighted avg     0.9288    0.9597    0.9439      1763

```
