# Perbaikan BAB 4 — hasil akhir

## P-4.1. Confusion matrix diperbesar + penempatan (Pak Aldi #3, Bu Ratih #8) 🧰

- **Di Bab 4:** satu confusion **terbaik per grup**, ukuran penuh (5 kelas standar, gold
  terkoreksi). File: `data/result/analysis/gt_corrected_2026_07_10/confusion/*.png` (mis.
  `S4-augmentation.png` untuk Grup 1). Legenda 0–1 = **proporsi per baris (recall)**.
- **Di Lampiran:** sisanya. **Jangan** panel 5-skenario dijejal (itu penyebab "kecil").
- Angka lama grup B (`error_viz/by_group/*_confusion.png`) **usang** — ganti ke yang gold-terkoreksi.

## P-4.2. Tabel GT vs Prediksi (Bu Dini #6) 🧰

Sumber: `data/result/analysis/gt_corrected_2026_07_10/gt_vs_pred/contoh_gt_vs_pred.md`. Kategori:
Benar 1921 / Salah tipe 3 / Kesalahan batas 20 / FN 25 / FP 25 (gold 1969 = cocok Bab 5). Contoh
per kategori sudah gaya Bu Dini (Entitas GT | GT | Prediksi | Kategori).

## P-4.3. Augmentasi: contoh + distribusi + perbaiki klaim (Pak Aldi #6/#7, Bu Dini #2) 🧰

Sumber: `docs/revisi/artefak/augmentasi_contoh_dan_distribusi.md` + chart
`bab4_viz/augmentasi_distribusi_revisi.png`. Klaim: "menurunkan ketimpangan 17,4:1→8,8:1, **belum
seimbang**". Bukti berhasil = F1 minoritas naik (TIME +0,106; EVENT +0,020).

## P-4.4. Warna grafik = legenda (Pak Aldi #8, Bu Dini #3) 🧰

Chart kanonik `bab4_viz/f1_skenario_semua_revisi.png` (warna per-grup cocok legenda, pemenang
di-bold, tanpa hatch). Konvensi: `docs/revisi/artefak/konvensi_warna_grafik.md`.

## P-4.5. Tabel 4.28 (Bu Nanik #8, Temuan #2/#3) 🧰

- **Judul:** ganti "Contoh Ketidaksesuaian Hasil dengan Teks Sumber" →
  **"Ringkasan Hasil Pengujian Fungsional Knowledge Graph"** (judul lama tetap untuk Tabel 4.29).
- **Isi:** ganti kolom biner ya/tidak → kuantitatif. Sumber:
  `docs/revisi/artefak/validitas_semantis/hasil_validitas_semantis.md` (Jumlah diperiksa | Valid |
  Tidak valid | Kesesuaian semantis | Terlacak). Total **36/114 = 31,58%**; operasional & terlacak 100%.
- **F5 unit = 21 jalur** (bukan 15 lokasi), "21 jalur, terdiri atas 15 lokasi unik".

## P-4.6. Redaksi setelah tabel + hubungan ke keterbatasan (Bu Nanik #8) 🧰

Paragraf: operasional 100%, terlacak 100%, kesesuaian semantis berbeda tiap fungsi → kueri jalan
≠ jawaban benar. + kalimat penghubung: rendahnya kesesuaian = proximity + negasi + propagasi
multi-hop. Teks lengkap di `teks_bab2_bab3_validitas_semantis.md` bagian 3–4.

## P-4.7. Analisis error sistematis (Bu Dini #8) 🧰/📝

Susun taksonomi: NER (FP/FN/salah tipe/salah batas/subword/imbalance) + KG (negasi/kedekatan/
cakupan lokasi-waktu/alias/urutan dokumen). Tiap kategori: teks sumber → keluaran → seharusnya →
penyebab. Bahan: confusion, gt_vs_pred, `keterbatasan_negasi_relasi.md`, validitas semantis.

## P-4.8. Negasi & "kueri berhasil ≠ jawaban benar" (D2.8, Bu Nanik #11) 🧰
Sudah tercakup P-4.6/P-4.7 + `keterbatasan_negasi_relasi.md`.
