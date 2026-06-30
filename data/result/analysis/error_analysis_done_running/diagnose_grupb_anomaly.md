# Diagnosa anomali Grup B (cased & RoBERTa) — trajektori self-training

> `diagnose_grupb_anomaly.py`, seqeval entity-level, test.csv sama. Tujuan: pisahkan 'rusak oleh self-training' vs 'jelek dari base'.


## Trajektori F1 per checkpoint

| Backbone | Checkpoint | F1 | Precision | Recall | F1 EVENT | F1 TIME | F1 PERSON | F1 LOCATION |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| cased | base | 0.7608 | 0.7116 | 0.8174 | 0.5357 | 0.4804 | 0.7504 | 0.8858 |
| cased | iter-2 | 0.7821 | 0.7303 | 0.8417 | 0.5794 | 0.4817 | 0.7778 | 0.8844 |
| cased | iter-3 | 0.7644 | 0.7098 | 0.8281 | 0.5421 | 0.4753 | 0.7552 | 0.8901 |
| cased | iter-4 | 0.7772 | 0.7239 | 0.8389 | 0.6126 | 0.5026 | 0.7632 | 0.8989 |
| cased | iter-5 | 0.7793 | 0.7289 | 0.8372 | 0.5636 | 0.5226 | 0.7664 | 0.9017 |
| cased | iter-6 | 0.7770 | 0.7244 | 0.8378 | 0.6226 | 0.4532 | 0.7646 | 0.9062 |
| roberta | base | 0.7836 | 0.7414 | 0.8310 | 0.6598 | 0.5000 | 0.7763 | 0.8849 |
| roberta | iter-2 | 0.8018 | 0.7577 | 0.8514 | 0.7200 | 0.4949 | 0.7915 | 0.9083 |
| roberta | iter-3 | 0.7811 | 0.7330 | 0.8361 | 0.6286 | 0.4787 | 0.7718 | 0.8906 |
| roberta | iter-4 | 0.7945 | 0.7555 | 0.8378 | 0.6733 | 0.5054 | 0.7825 | 0.9020 |
| roberta | iter-5 | 0.7926 | 0.7520 | 0.8378 | 0.6538 | 0.5236 | 0.7809 | 0.9012 |
| roberta | iter-6 | 0.8068 | 0.7657 | 0.8525 | 0.6306 | 0.5291 | 0.8002 | 0.9060 |

## classification_report lengkap per checkpoint

### cased-base
```
              precision    recall  f1-score   support

       EVENT     0.4918    0.5882    0.5357        51
    LOCATION     0.9087    0.8641    0.8858       449
      PERSON     0.6923    0.8192    0.7504      1189
        TIME     0.3769    0.6622    0.4804        74

   micro avg     0.7116    0.8174    0.7608      1763
   macro avg     0.6174    0.7334    0.6631      1763
weighted avg     0.7283    0.8174    0.7673      1763
```

### cased-iter-2
```
              precision    recall  f1-score   support

       EVENT     0.5536    0.6078    0.5794        51
    LOCATION     0.9007    0.8686    0.8844       449
      PERSON     0.7132    0.8553    0.7778      1189
        TIME     0.3932    0.6216    0.4817        74

   micro avg     0.7303    0.8417    0.7821      1763
   macro avg     0.6402    0.7384    0.6808      1763
weighted avg     0.7429    0.8417    0.7868      1763
```

### cased-iter-3
```
              precision    recall  f1-score   support

       EVENT     0.5179    0.5686    0.5421        51
    LOCATION     0.8962    0.8842    0.8901       449
      PERSON     0.6962    0.8251    0.7552      1189
        TIME     0.3557    0.7162    0.4753        74

   micro avg     0.7098    0.8281    0.7644      1763
   macro avg     0.6165    0.7485    0.6657      1763
weighted avg     0.7277    0.8281    0.7716      1763
```

### cased-iter-4
```
              precision    recall  f1-score   support

       EVENT     0.5667    0.6667    0.6126        51
    LOCATION     0.9070    0.8909    0.8989       449
      PERSON     0.7009    0.8377    0.7632      1189
        TIME     0.4050    0.6622    0.5026        74

   micro avg     0.7239    0.8389    0.7772      1763
   macro avg     0.6449    0.7643    0.6943      1763
weighted avg     0.7371    0.8389    0.7825      1763
```

### cased-iter-5
```
              precision    recall  f1-score   support

       EVENT     0.5254    0.6078    0.5636        51
    LOCATION     0.9151    0.8886    0.9017       449
      PERSON     0.7075    0.8360    0.7664      1189
        TIME     0.4160    0.7027    0.5226        74

   micro avg     0.7289    0.8372    0.7793      1763
   macro avg     0.6410    0.7588    0.6886      1763
weighted avg     0.7429    0.8372    0.7847      1763
```

### cased-iter-6
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

### roberta-base
```
              precision    recall  f1-score   support

       EVENT     0.6957    0.6275    0.6598        51
    LOCATION     0.8879    0.8820    0.8849       449
      PERSON     0.7311    0.8276    0.7763      1189
        TIME     0.3841    0.7162    0.5000        74

   micro avg     0.7414    0.8310    0.7836      1763
   macro avg     0.6747    0.7633    0.7053      1763
weighted avg     0.7554    0.8310    0.7890      1763
```

### roberta-iter-2
```
              precision    recall  f1-score   support

       EVENT     0.7347    0.7059    0.7200        51
    LOCATION     0.9124    0.9042    0.9083       449
      PERSON     0.7410    0.8495    0.7915      1189
        TIME     0.3952    0.6622    0.4949        74

   micro avg     0.7577    0.8514    0.8018      1763
   macro avg     0.6958    0.7804    0.7287      1763
weighted avg     0.7700    0.8514    0.8067      1763
```

### roberta-iter-3
```
              precision    recall  f1-score   support

       EVENT     0.6111    0.6471    0.6286        51
    LOCATION     0.9018    0.8797    0.8906       449
      PERSON     0.7125    0.8419    0.7718      1189
        TIME     0.3947    0.6081    0.4787        74

   micro avg     0.7330    0.8361    0.7811      1763
   macro avg     0.6550    0.7442    0.6924      1763
weighted avg     0.7444    0.8361    0.7856      1763
```

### roberta-iter-4
```
              precision    recall  f1-score   support

       EVENT     0.6800    0.6667    0.6733        51
    LOCATION     0.9020    0.9020    0.9020       449
      PERSON     0.7374    0.8335    0.7825      1189
        TIME     0.4196    0.6351    0.5054        74

   micro avg     0.7555    0.8378    0.7945      1763
   macro avg     0.6847    0.7593    0.7158      1763
weighted avg     0.7643    0.8378    0.7981      1763
```

### roberta-iter-5
```
              precision    recall  f1-score   support

       EVENT     0.6415    0.6667    0.6538        51
    LOCATION     0.9190    0.8842    0.9012       449
      PERSON     0.7313    0.8377    0.7809      1189
        TIME     0.4274    0.6757    0.5236        74

   micro avg     0.7520    0.8378    0.7926      1763
   macro avg     0.6798    0.7661    0.7149      1763
weighted avg     0.7637    0.8378    0.7971      1763
```

### roberta-iter-6
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

---

# Interpretasi diagnosa (untuk Bab 4)

## Temuan decisive: BUKAN kerusakan self-training
F1 dari **base → iter-6** justru **naik tipis** di kedua backbone:
- **cased**: 0.7608 → 0.7770 (+0.016)
- **roberta**: 0.7836 → 0.8068 (+0.023)

Trajektori datar-naik ini **menyingkirkan hipotesis "self-training merusak model"**. Anomali F1
rendah sudah **ada sejak checkpoint base** (fine-tune supervised pertama pada seed), bukan akibat
iterasi pseudo-label. Self-training bekerja normal (sedikit memperbaiki), persis seperti pada model
uncased — ia hanya tidak bisa menambal defisit yang sudah ada di base.

## Lokasi defisit: kelas PERSON + boundary, bukan merata
Bandingkan F1 per-kelas di base/iter-6:
- **PERSON**: cased 0.75–0.78, roberta 0.78–0.80 — vs **uncased 0.94–0.96**. Gap ~0.16–0.20.
- **LOCATION**: cased/roberta 0.89–0.91 — **hampir setara uncased** (~0.95). Nyaris tak terdampak.
- EVENT/TIME rendah di mana-mana (few-shot), jadi bukan pembeda.

Jadi defisit **terkonsentrasi di PERSON**. Dipadukan dengan analisis error sebelumnya
(boundary B/I melonjak 100/102 vs 2–7; PERSON FN 172/163 vs 17–45), polanya konsisten:
entitas PERSON sering **multi-token** (`Abdul Muththalib`, `Amr bin Luhay`) sehingga paling rentan
terhadap **misalignment label B/I ↔ subword**; LOCATION yang sering satu token (`Makkah`, `Madinah`)
nyaris tak terdampak.

## Akar masalah (hipotesis terkuat, perlu 1 verifikasi)
Pembeda cased & roberta dari tiga model uncased yang sehat: **skema tokenisasi berbeda**
(IndoBERT-p1 = WordPiece *cased*; RoBERTa = byte-level BPE) vs WordPiece *uncased* (indolem/cahya/distilbert).
Pipeline NER ini dirancang/diuji untuk IndoBERT uncased. Hipotesis paling konsisten:
**penyelarasan label kata→subword (atau special-token/prefix-space) tidak ditangani benar untuk
tokenizer cased/BPE**, sehingga model dilatih pada label yang sedikit bergeser → boundary error
sistematis sejak base.

**Status kejujuran:** ini **hipotesis**, belum dibuktikan di level kode. Yang **sudah terbukti**:
(1) bukan kerusakan self-training, (2) defisit ada sejak base, (3) terkonsentrasi di PERSON multi-token + boundary.

**Rekomendasi penyajian:** JANGAN tulis "cased/RoBERTa lebih buruk untuk NER Sirah". Tulis: di bawah
pipeline yang tak diubah (di-tune untuk IndoBERT uncased), penggantian ke backbone cased/BPE menurunkan
F1 **sejak fine-tune pertama** — paling konsisten dengan penanganan tokenizer/label, dan perlu diperbaiki
sebelum kesimpulan apa pun. Verifikasi lanjutan (bila mau): inspeksi fungsi `tokenize_and_align_labels`
di notebook untuk `is_split_into_words`/`word_ids()` pada tokenizer cased & RoBERTa.
