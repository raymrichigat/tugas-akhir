# Legacy: Skenario Class Weight + Adaptive Threshold

> **Status:** Arsip. Didrop dari klaim utama TA per restrukturisasi skenario **2026-05-11**.

## Apa yang ada di sini?

Hasil run **3 skenario lama** yang dieksekusi 2026-05-07 di Colab:

| Skenario lama | Komponen | Folder | F1 entity | F1 EVENT |
|---|---|---|---|---|
| E1 baseline | Fix 0.9, no class weight | (sekarang di `../S1_baseline/` — reuse jadi S1 baru) | **0.959** | 0.816 |
| S1 class weight | Fix 0.9 + class weight inverse freq (clip 50×) | `S1_classweight/` | 0.908 | **0.835** |
| S2 adaptive + CW | Adaptive 0.9→0.7 + class weight | `S2_adaptive/` | 0.843 | 0.830 |

## Kenapa Didrop?

Lihat `bimbingan.md` §7.3 dan `srl_ner_skenario.md` §9 di root. Singkatnya:
- Bu Diana putaran 3 (2026-05-07) minta attack imbalance di level lain (representasi via contrastive, data via augmentation).
- Trade-off precision-recall di skenario lama terlalu tajam (S2 adaptive precision drop ke 0.74).
- Skema baru S1/S2/S3 lebih bersih: 1 skenario = 1 layer kontribusi.

## Apakah Bisa Direferensikan di Laporan?

Ya. Bab 4 bisa pakai hasil ini sebagai **sub-bab "Studi Pendahuluan"** dengan klaim:

> *"Class weight inverse frequency menaikkan F1 EVENT +1.9% di Sirah, tapi menurunkan precision overall ~5–10%. Hal ini memotivasi pendekatan berbeda — contrastive learning (S2 baru) di level representasi dan sentence augmentation (S3 baru) di level data."*

## File Penting

- `analisis_skenario_srlner.md` — analisis komparatif 11 section (executive summary, dinamika pseudo-labelling, 3 metrik, per-entity, error pattern, verdict, rekomendasi, bahan diskusi Bu Diana, lampiran numerik).
- `compare_scenarios.ipynb` — notebook 25 cells (plot pseudo-label per iter, per-entity bar chart, confusion matrix side-by-side, P-R trade-off scatter dengan iso-F1 contour).
- `summary_comparison.csv` — ringkasan numerik 3 skenario.
- `fig_*.png` — 4 plot pendukung (confusion, per-entity, P-R trade-off, pseudo per iter).

## Catatan Path

Notebook `compare_scenarios.ipynb` di sini awalnya mereferensikan `../baseline/`. Karena folder itu sudah di-rename jadi `../../S1_baseline/`, kalau mau re-run notebook ini perlu update path-nya dulu.
