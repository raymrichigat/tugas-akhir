# Training Bundle — Gold TERKOREKSI (2026-06-30)

Versi data setelah re-annotation gold (arahan Bu Dini Adni):
- Aturan nasab (genealogi dipecah per-nama), apostrof OCR, LOC<->EVENT (145),
  gold_audit (67 koreksi span).
- TEST IKUT DIPERBAIKI -> F1 lama (0.9537 dst.) USANG, tidak comparable.

## Isi
**Default (pos_tag = `NN` placeholder — untuk S1/S2 + grup A/B):**
- train.csv / test.csv / unlabelled.csv  : BIO (text_id,id,token,pos_tag,label)
- class_weights.json                      : untuk skenario Weighted-CE (regen dari train baru)
- train_augmented_v2.csv                  : untuk skenario Augmentation (mention replacement, seed=42)
- augmentation_log_v2.json                : log augmentasi

**Varian POS-tag (pos_tag RIIL via stanza `id` — KHUSUS skenario 3 / grup C Ablation POS-tag):**
- train_postag.csv / test_postag.csv / unlabelled_postag.csv / train_augmented_v2_postag.csv
  : token & baris IDENTIK dengan versi default, hanya kolom pos_tag yang diisi UPOS riil.

## Distribusi gold final
PERSON 4205 | LOCATION 1421 | TIME 286 | EVENT 240
(TIME 310->286 setelah fix batas span 2026-07-01: ekspresi tanggal Hijriah
multi-kata + tahun ekor + rentang "atau" digabung jadi 1 span.)

## Catatan
- Semua skenario (S1/S2/S3, grup A/B/C) WAJIB re-train + re-eval di benchmark ini.
