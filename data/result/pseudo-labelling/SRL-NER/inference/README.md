# Folder `inference/` — hasil inference NER ke seluruh korpus

Berisi hasil model NER melabeli **seluruh 1094 chunk** Sirah (untuk konstruksi Knowledge Graph).

## Isi

| Path | Isi |
|------|-----|
| `v4/sirah_predicted_v4_token.csv` | **v4 SERAGAM** — token-level BIO, model **S4-augmentation** (gold terkoreksi, F1 0.9458). Semua 1094 chunk dari model. |
| `v4/sirah_predicted_v4_entity.csv` | **v4 SERAGAM** — entity-level (dipakai rantai KG), 7968 entitas. Dibersihkan dari token via `build_v4_entity_from_token.py` (`.bak` = versi fragmented dari Colab). |
| `v4/inference_runtime_v4.json` | metadata run inference v4 (1094 chunk, 31 detik). |
| `v3-lama/` | **arsip v3** — winner LAMA (S3.2, gold sebelum koreksi). Sengaja disimpan sebagai pembanding. |

## Dua versi KG (keputusan 2026-07-08)

- **SERAGAM** (folder ini): prediksi model untuk **semua 1094 chunk**. KG = murni produk NER; narasi TA "KG dibangun oleh model NER" paling kuat.
- **HIBRIDA** (`../hibrida/`): **gold** untuk 844 chunk berlabel (799 chunk berisi entitas) + **prediksi** untuk 250 chunk unlabelled. Sedikit lebih akurat, tapi kontribusi murni NER hanya di 250 chunk.

## Alur regenerate (setelah inference Colab)

```
# versi SERAGAM
1. (Colab) srl_ner_sirah_inference_v4_augmentation_colab.ipynb -> download token+entity ke folder ini
2. python src/relation_extraction/build_v4_entity_from_token.py        # rebuild entity bersih
3. python src/relation_extraction/build_v3_prelabelled_from_inference.py \
       --input  data/result/pseudo-labelling/SRL-NER/inference/sirah_predicted_v4_entity.csv \
       --output data/result/manual_labelling/sirah_prelabelled_v4.csv
4. (rebuild nodes/edges v4 -> alias clustering -> periodisasi -> Neo4j -> SNA)

# versi HIBRIDA -> lihat ../hibrida/README.md
```
