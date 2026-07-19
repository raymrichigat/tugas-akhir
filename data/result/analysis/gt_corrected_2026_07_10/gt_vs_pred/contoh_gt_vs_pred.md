# Perbandingan Ground Truth vs Prediksi Model (Data Uji) — Bu Dini #6

> Model: **S4-augmentation** (pemenang, dipakai membangun KG). Gold = ground-truth test terkoreksi. Level entitas (span). Dihasilkan `gt_vs_pred_table.py`, tanpa menjalankan model.


## Ringkasan jumlah per kategori

| Kategori | Jumlah | Keterangan |
|---|---:|---|
| Benar | 1921 | span & tipe sama persis |
| Salah tipe | 3 | span sama, tipe beda |
| Kesalahan batas | 20 | span tumpang-tindih, batas beda |
| False negative | 25 | entitas gold tak terdeteksi |
| **Total entitas gold (acuan)** | **1969** | Benar+Salah tipe+Batas+FN |
| False positive | 25 | entitas prediksi spurious (di luar 1969 gold) |

**Catatan:** kesalahan **tipe** hanya 3 entitas — jauh lebih kecil daripada kesalahan **deteksi** (FN 25 + FP 25 + batas 20). Menegaskan bahwa model sudah memahami keempat tipe; masalah utama ada di batas/deteksi, bukan salah klasifikasi tipe. (Total entitas gold 1969 konsisten dengan jumlah entitas data uji di Bab 5.)


## Contoh per kategori

| Entitas (GT) | Ground truth | Entitas (Prediksi) | Prediksi | Kategori | chunk |
|---|---|---|---|---|---|
| Jazirah Arab | LOCATION | Jazirah Arab | LOCATION | Benar | 000001-002 |
| India | LOCATION | India | LOCATION | Benar | 000001-002 |
| Haritsah bin Amr | PERSON | Haritsah bin Amr | PERSON | Benar | 000002-003 |
| Hijaz | LOCATION | Hijaz | LOCATION | Benar | 000002-003 |
| Badr | LOCATION | Badr | EVENT | Salah tipe | 000148-004 |
| Jabal Uhud | LOCATION | Jabal Uhud | EVENT | Salah tipe | 000157-003 |
| Hudaibiyah | LOCATION | Hudaibiyah | EVENT | Salah tipe | 000338-001 |
| bulan Maret 571 M | TIME | Maret 571 M | TIME | Kesalahan batas | 000017-008 |
| Abdul Ka'bah | PERSON | Ka'bah | PERSON | Kesalahan batas | 000017-009 |
| Senin pagi , | TIME | Senin pagi , tanggal 9 Rabi'ul Awwal | TIME | Kesalahan batas | 000018-001 |
| tanggal 20 atau 22 bulan April tahun 571 M | TIME | tanggal 20 | TIME | Kesalahan batas | 000018-001 |
| Cina | LOCATION | (tidak terdeteksi) | - | False negative | 000001-002 |
| Wadi Nakhlah | LOCATION | (tidak terdeteksi) | - | False negative | 000010-001 |
| Ukazh | LOCATION | (tidak terdeteksi) | - | False negative | 000014-001 |
| Dzil-Majaz | LOCATION | (tidak terdeteksi) | - | False negative | 000014-001 |
| (tidak ada) | - | timur | LOCATION | False positive | 000001-002 |
| (tidak ada) | - | Isma' | PERSON | False positive | 000002-004 |
| (tidak ada) | - | Hijabah | LOCATION | False positive | 000007-007 |
| (tidak ada) | - | hijabah | LOCATION | False positive | 000007-009 |
