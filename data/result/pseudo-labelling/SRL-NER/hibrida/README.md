# Folder `hibrida/` — versi KG hibrida (gold + prediksi)

Versi alternatif input KG: **gold di mana tersedia, prediksi model di sisanya.**

## Komposisi (1094 chunk)

| Sumber | Cakupan | Keterangan |
|--------|---------|-----------|
| **gold** | 844 chunk berlabel (799 berisi entitas, ~6152 entitas) | dari `sirah_prelabelled.csv`, confidence = 1.0 |
| **prediksi** | 250 chunk unlabelled | dari model **S4-augmentation** (v4), confidence asli |

45 chunk berlabel bertipe all-O (tanpa entitas) → wajar tidak menyumbang node.

## Isi

| Path | Isi |
|------|-----|
| `sirah_predicted_v4_hybrid_entity.csv` | entity-level gabungan (kolom `source` = `gold`/`pred`). Dibuat oleh `build_v4_hybrid_entity.py`. |

## Cara buat (setelah inference v4 seragam ada)

```
1. Pastikan inference/sirah_predicted_v4_entity.csv sudah ada
   (Colab -> build_v4_entity_from_token.py)
2. python src/relation_extraction/build_v4_hybrid_entity.py
3. python src/relation_extraction/build_v3_prelabelled_from_inference.py \
       --input  data/result/pseudo-labelling/SRL-NER/hibrida/sirah_predicted_v4_hybrid_entity.csv \
       --output data/result/manual_labelling/sirah_prelabelled_v4_hybrid.csv
4. (rebuild nodes/edges v4-hibrida -> alias clustering -> periodisasi -> Neo4j -> SNA)
```

## Kapan pakai yang mana

- **SERAGAM** (`../inference/`): KG murni produk NER — **rekomendasi untuk narasi TA**.
- **HIBRIDA** (folder ini): KG sedikit lebih akurat; kontribusi murni NER hanya di 250 chunk. Cocok kalau fokusnya kualitas graf akhir, bukan demonstrasi model.
```
