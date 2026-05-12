# Done Running — SRL-NER

Folder ini berisi hasil run skenario SRL-NER. Struktur direvisi per **2026-05-11** untuk mengakomodasi restrukturisasi skenario (lihat `srl_ner_skenario.md` dan `bimbingan.md` di root project).

## Struktur

```
done_running/
├── README.md                              ← file ini
├── compare_scenarios.ipynb                ← notebook perbandingan 5 skenario (template, fill after run)
├── analisis_skenario_S2_S3.md             ← analisis komparatif markdown (template, fill after run)
├── S1_baseline/                           ← Skenario aktif S1 (= E1 lama, reuse)
│   ├── dataset/
│   ├── notebook/
│   └── output/
│       ├── evaluation/
│       └── models/
├── S2a_scl/                               ← Skenario aktif S2a SCL (akan dibuat saat run)
├── S2b_jscl/                              ← Skenario aktif S2b JSCL
├── S3a_scl_aug/                           ← Skenario aktif S3a SCL + Augmentation
├── S3b_jscl_aug/                          ← Skenario aktif S3b JSCL + Augmentation
└── legacy_class_weight_adaptive/          ← Arsip skenario lama (didrop dari klaim utama)
    ├── README.md
    ├── S1_classweight/                    ← (skenario lama: fix 0.9 + class weight)
    ├── S2_adaptive/                       ← (skenario lama: adaptive 0.9→0.7 + class weight)
    ├── analisis_skenario_srlner.md        ← analisis komparatif 3 skenario lama
    ├── compare_scenarios.ipynb            ← notebook perbandingan
    ├── fig_*.png                          ← plot pendukung analisis lama
    └── summary_comparison.csv             ← ringkasan numerik 3 skenario lama
```

## Skenario Aktif

| Skenario | Folder | Status |
|---|---|---|
| **S1 — Baseline** | `S1_baseline/` | ✅ Selesai (run 2026-05-07, awalnya disebut E1) |
| **S2a — SCL + Baseline** | `S2a_scl/` | ⏳ Notebook siap, tunggu run Colab |
| **S2b — JSCL + Baseline** | `S2b_jscl/` | ⏳ Notebook siap, tunggu run Colab |
| **S3a — SCL + Augmentation** | `S3a_scl_aug/` | ⏳ Notebook siap, tunggu run Colab |
| **S3b — JSCL + Augmentation** | `S3b_jscl_aug/` | ⏳ Notebook siap, tunggu run Colab |

## Cara Pakai Compare Notebook

1. **Setelah run 4 skenario** (S2a/S2b/S3a/S3b) di Colab, download model checkpoints ke folder masing-masing.
2. Buka `compare_scenarios.ipynb` di sini → set `DATASET_DIR` ke lokasi `test.csv` kamu.
3. Run cell #4 (evaluate). Pertama kali = inference per skenario (lambat, butuh GPU); cache disimpan di `compare_cache.json`.
4. Cell #5-10 generate tabel + plot otomatis (output: `summary_comparison_5skenarios.csv`, `per_entity_f1_5skenarios.csv`, 4 PNG).
5. Isi `analisis_skenario_S2_S3.md` dengan angka konkret dari hasil di cell-cell tadi (cari placeholder `__`).

## Catatan

- **`S1_baseline/`** sebelumnya bernama `baseline/`. Di-rename 2026-05-11 untuk konsistensi penamaan dengan skenario baru.
- **`legacy_class_weight_adaptive/`** berisi hasil run skenario lama (class weight + adaptive threshold) yang sudah dijalankan 2026-05-07 tapi didrop dari klaim utama TA per restrukturisasi 2026-05-11. Tetap disimpan sebagai studi pendahuluan / ablation pembanding di Bab 4.
- Notebook `compare_scenarios.ipynb` di legacy folder mereferensikan path `../baseline/` — perlu update ke `../S1_baseline/` kalau mau re-run.

Detail teknis tiap skenario → `srl_ner_skenario.md` di root project.
