# Audit Kualitas Manual Labelling (Gold)

> Read-only. Sumber: `data/result/manual_labelling/sirah_prelabelled.csv`. Script: `src/manual_labelling/audit_labels.py`. **Belum mengubah apa pun** — ini daftar kandidat untuk di-review sebelum perbaikan + re-run.


Total entitas gold: **6013** di **803 chunk**. Distribusi: PERSON 4073, LOCATION 1434, TIME 307, EVENT 199.


## Ringkasan temuan

| Temuan | Jumlah | File |
| --- | --- | --- |
| 1. Offset mismatch (slice ≠ entity_text) | 0 | offset_mismatch.csv |
| 2. Span dgn tanda baca di ujung | 0 | punctuation_spans.csv |
| 3. Konflik surface→label (>1 kelas) | 0 | conflict_surface_label.csv |
| 4. Kandidat under-annotation | 59 | under_annotation_candidates.csv |
| 5. Duplikat/overlap span | 0 | duplicate_overlap.csv |
| 6. Entitas mencurigakan | 0 | (inline) |

## 1. Offset mismatch

✅ Tidak ada — offset semua konsisten.

## 2. Tanda baca di dalam span (artefak OCR)

**0** entitas dengan titik/koma/kurung di ujung (kandidat artefak OCR). Per kelas: —.


> Catatan: 52 entitas berakhiran apostrof (`Isra'`, `Tha'if`, `Al-Akwa'`) **TIDAK** dihitung sebagai error — itu transliterasi Arab yang sah.

Contoh:


## 3. Konflik surface → label

✅ Tidak ada konflik surface→label.

## 4. Under-annotation (akar masalah kapitalisasi)

Pola `perang/ghazwah/sariyah` + kata kapital di seluruh gold:
- Trigger **kapital** (`Perang X`): 162, ter-label EVENT: 162 (100%)
- Trigger **huruf kecil** (`perang X`): 12, **tidak** ter-label: 4 (33%)

→ Konsisten dengan regex `pre_labelling.py` `_EVENT_PERANG_RE` yang mensyaratkan `Perang` kapital. Mention huruf kecil sistematis ke-skip di gold.

- `000005-003`: …`perang Kisra`… (huruf kecil, tak ter-label)
- `000223-004`: …`perang Zaid`… (huruf kecil, tak ter-label)
- `000223-002`: …`perang Zaid`… (huruf kecil, tak ter-label)
- `000331-001`: …`perang Tha'if`… (huruf kecil, tak ter-label)

Selain itu, 59 surface proper-noun muncul ≥3× di teks tapi <60% ter-label (lihat `under_annotation_candidates.csv`). Top 10:

| surface | muncul | terlabel | coverage |
| --- | --- | --- | --- |
| abu thalib | 107 | 56 | 0.52 |
| ka'b | 94 | 52 | 0.55 |
| zaid | 86 | 35 | 0.41 |
| hijrah | 85 | 4 | 0.05 |
| badr | 74 | 22 | 0.3 |
| umayyah | 54 | 10 | 0.19 |
| uhud | 44 | 16 | 0.36 |
| khalid | 39 | 11 | 0.28 |
| utsman | 36 | 18 | 0.5 |
| ramadhan | 33 | 2 | 0.06 |

## 5. Duplikat / overlap span

0 pasang. ✅ Tidak ada.

## 6. Entitas mencurigakan (1 huruf / angka saja)

0. ✅ Tidak ada.

## Rekomendasi urutan perbaikan

1. **Offset & duplikat** → fix struktural dulu (paling jelas salah).
2. **Konflik surface→label** dengan share rendah → review manual, samakan.
3. **Tanda baca di span** → trim (bisa otomatis, tapi cek dulu yang sah seperti `Tha'if`).
4. **Under-annotation** → keputusan kebijakan: mau case-insensitive untuk EVENT? Ini menambah entitas → ubah angka. **Diskusikan dengan Bu Diana** karena mengubah test gold.
5. Setelah fix → re-run `prepare_bert_data.py` (instan) → re-train (GPU).
