# Perbaikan Buku per Bab — Indeks

> Konsolidasi seluruh revisi sidang menjadi "begini hasilnya di buku", per bab. Acuan poin:
> `docs/revisi/Poin-Revisi-TA-Terbaru.md` (4 dosen: Pak Aldi, Bu Nanik, Bu Ratih, Bu Dini).
>
> Status: ✅ teks final siap salin · 🧰 dari artefak di `docs/revisi/artefak/` · 📝 tulis sendiri

| Berkas | Isi |
|---|---|
| `00_abstrak.md` | rename alias + kalimat batas validitas (ringkas) |
| `bab1.md` | rewrite tujuan #4 (SNA deskripsi vs kelayakan) |
| `bab2.md` | teori confusion, imbalance (Henning/Nemoto), batas eval + validitas semantis, cased/uncased, notasi persamaan |
| `bab3.md` | contoh NER berjalan, record latih, rename alias + JW 0,93, dasar 200-char, prosedur validitas, negasi; **belum: chunking, token/subtoken, protokol koreksi** |
| `bab4.md` | confusion (best/grup + lampiran), GT vs prediksi, augmentasi + klaim, warna grafik, Tabel 4.28 kuantitatif, error taksonomi |
| `bab5.md` | pembuka (dobel "dan"), angka validitas, saran precision vs future, batas SNA |
| `format_dan_lampiran.md` | halaman ganjil, header tabel, persamaan, lampiran, 6 kesalahan wajib |

## Artefak pendukung (di `docs/revisi/artefak/`)
- `contoh_ner_dan_data_latih.md`, `augmentasi_contoh_dan_distribusi.md`,
  `konvensi_warna_grafik.md`, `perbandingan_alias_clustering_rayssa.md`,
  `justifikasi_ambang_jaro_winkler.md`, `keterbatasan_negasi_relasi.md`,
  `dasar_cooccurrence_200_karakter.md`, `contekan_imbalance_pak_aldi_GPT.md`,
  `validitas_semantis/` (worksheet + hasil + teks bab2/3).

## Gambar/data siap pakai
- `data/result/analysis/gt_corrected_2026_07_10/confusion/` (confusion 5-kelas, gold terkoreksi)
- `.../confusion_revisi/bio_token/` (BIO 9-kelas, lampiran)
- `.../gt_vs_pred/contoh_gt_vs_pred.md`
- `.../relation_window/` (dasar 200-char + chart)
- `data/result/analysis/bab4_viz/` (chart F1, distribusi augmentasi)

## Catatan
- **Pak Aldi #5 hyperparameter** ✅ artefak `artefak/dasar_hyperparameter.md` (referensi Ariyanto
  dkk. 2025 IEEE Access). Tinggal konfirmasi final ke Mbak Amelia.
