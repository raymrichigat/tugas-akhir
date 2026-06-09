# Panduan Re-train Semua Skenario di Gold Dikoreksi

> Dibuat 2026-06-09. Konteks: setelah audit manual labelling, gold diperbaiki (+8 EVENT, fix kapitalisasi `perang X`). Data train/test/unlabelled/augmented sudah di-regenerate. Dokumen ini = checklist untuk re-train **semua skenario** di Colab agar model belajar gold yang diperbaiki.

## Apa yang berubah (dan yang TIDAK)
- **Berubah:** hanya **data** — `train.csv` & `test.csv` masing-masing +4 span EVENT (`perang X` huruf kecil), `train_augmented_v2.csv` ikut regenerate. Total perubahan: 8 entitas dari 6.005.
- **TIDAK berubah:** struktur split (terverifikasi identik), notebook training, hyperparameter, arsitektur.
- **Ekspektasi jujur:** karena perubahan kecil, angka akan bergeser **tipis**. Manfaat utama (EVENT F1 +0,046 dari koreksi gold) **sudah** terlihat tanpa re-train (lihat `2026-06-11.md` Bagian 3b). Re-train ini untuk **integritas end-to-end** + agar model ikut belajar 4 event train baru.

## File data yang di-upload ke Colab
Semua sudah corrected di `data/result/pseudo-labelling/SRL-NER/`. Bundle siap-pakai:
- **`corrected_gold_data_20260609.zip`** (berisi 4 file di bawah) — upload ini, extract di Drive ke lokasi yang sama seperti run sebelumnya.

| File | Dipakai oleh |
|---|---|
| `train.csv` | S1, S2a, S2b, S3.1 |
| `test.csv` | semua skenario (evaluasi) |
| `unlabelled.csv` | semua (self-training) |
| `train_augmented_v2.csv` | **S3.2** (sebagai train berlabel) |

> Backup gold/data lama ada di suffix `.bak_20260609_*` dan `.bak_oldgold` (jangan dihapus — untuk perbandingan before/after).

## Lineup final → notebook → urutan prioritas

> **Lineup dikunci 2026-06-09** (lihat `../skenario/skenario_baru_2026-06.md`). Yang dilatih = **anggota lineup final**, bukan semua run lama. **S3.1 λ-sweep & S2b JSCL TIDAK masuk tabel final** (tuning/pembanding internal) — tidak perlu di-re-train.

**Grup A — penanganan imbalance** (carry-over + baru):
| Prioritas | Skenario | Notebook (Colab) | Input train | Asal |
|---|---|---|---|---|
| **1** | S1 Baseline | `srl_ner_sirah_0.9_colab.ipynb` | `train.csv` | lama ✓ |
| **2** | S4 Augmentation (winner) | `srl_ner_sirah_S3_2_scl_aug_colab.ipynb` | `train_augmented_v2.csv` | lama ✓ |
| 3 | S3 Contrastive (SCL λ=0.3) | `srl_ner_sirah_S2a_scl_colab.ipynb` | `train.csv` | lama ✓ |
| 4 | **S2 Weighted-CE** | (patch notebook S1, lihat scaffold doc) | `train.csv` + `class_weights.json` | **baru** |

**Grup B (backbone)** & **Grup C (POS-tag)**: lihat `../skenario/skenario_baru_2026-06.md` — dijalankan setelah Grup A, pakai config terbaiknya.

> **Saran urutan:** Grup A dulu (S1 & S4 = head-to-head utama), lalu S3 & S2, baru Grup B/C. Semua di gold dikoreksi.

## Setelah training (per model)
1. Download folder model iterasi terakhir (yang ada `model.safetensors` + `config.json` + `tokenizer.json`).
2. Taruh di `src/pseudo_labelling/SRL-NER/done_running/.../` (boleh folder baru, mis. `..._corrected/`).
3. Re-evaluasi lokal (tanpa GPU) untuk dapat angka entity-level:
   ```powershell
   venv\Scripts\python.exe src\pseudo_labelling\SRL-NER\evaluate_seqeval.py `
       --model "PATH\KE\MODEL\RETRAINED" --tag "S3.2-retrained-corrected"
   ```
4. Error analysis (opsional, untuk pembahasan): edit `MODEL_DIR` di `error_analysis.py` ke model baru lalu jalankan.

## Checklist
- [ ] Upload `corrected_gold_data_20260609.zip` ke Drive, extract ke path notebook.
- [ ] Re-train S1 → download model → `evaluate_seqeval` → catat F1.
- [ ] Re-train S3.2 → download model → `evaluate_seqeval` → catat F1.
- [ ] (Opsional) S2a / S2b / S3.1.
- [ ] Update tabel hasil di `2026-06-11.md` dengan angka retrained.

## Catatan untuk Bab 4 (kejujuran)
- Perbaikan gold dilakukan **by-rule** (case-insensitive event detection), **bukan** meniru output model → tidak bias ke model.
- Skala EVENT yang kecil (~191 entitas) tetap keterbatasan fundamental; solusi jangka panjang = LLM verb extraction (future work), bukan tweak regex.
