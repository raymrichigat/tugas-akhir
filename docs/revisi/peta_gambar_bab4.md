# Peta Gambar Bab 4 → Berkas Gambar

> Rujukan file gambar untuk tiap "Gambar 4.x" saat menyisipkan ke Word.
> Basis path: `data/result/...`. Semua angka = benchmark GT-terkoreksi (done_newest).

## A. Grafik F1 & distribusi (SUDAH ADA — dari `src/analysis/bab4_visualizations.py`)
Folder: `data/result/analysis/bab4_viz/`

| Gambar | Isi | Berkas |
|---|---|---|
| 4.1 | Distribusi jumlah entitas data latih vs uji (batang berkelompok) | `bab4_viz/eda_imbalance.png` |
| 4.2 | F1 agregat 5 skenario Uji Coba 1 | `bab4_viz/f1_uc1_agregat.png` |
| 4.3 | F1 per-kelas Uji Coba 1 | `bab4_viz/f1_uc1_perkelas.png` |
| 4.6 | Distribusi token sebelum/sesudah augmentasi (2 panel O \| entitas) | `bab4_viz/augmentasi_distribusi.png` (alternatif: `augmentasi_distribusi_revisi.png`) |
| 4.7 | F1 agregat 5 model Uji Coba 2 | `bab4_viz/f1_uc2_agregat.png` |
| 4.8 | F1 per-kelas Uji Coba 2 | `bab4_viz/f1_uc2_perkelas.png` |
| 4.12 | F1 agregat Uji Coba 3 (POS) | `bab4_viz/f1_uc3_agregat.png` |
| 4.13 | F1 per-kelas Uji Coba 3 (POS) | `bab4_viz/f1_uc3_perkelas.png` |

Regenerasi: `python src/analysis/bab4_visualizations.py`

## B. Confusion matrix (SUDAH ADA — dari `recompute_gt_corrected.py`)
⚠️ **PILIH SATU versi** (lihat catatan konsistensi di bawah):
- 5 kelas (O + 4 tipe): `data/result/analysis/gt_corrected_2026_07_10/confusion/`
- 9 kelas BIO: `data/result/analysis/gt_corrected_2026_07_10/confusion_revisi/bio_token/`

| Gambar | Isi | Berkas (folder pilihan) |
|---|---|---|
| 4.4 | Confusion model terbaik Uji Coba 1 (augmentasi) | `.../S4-augmentation.png` |
| 4.9 | Confusion model terbaik Uji Coba 2 (IndoBERT uncased) | `.../S1-baseline.png` |
| 4.11 | Confusion IndoBERT phase-1 (judul di dalam gambar sudah "IndoBERT phase-1") | `.../B-indobert-cased.png` |
| 4.14 | Confusion model dengan fitur POS | `.../S5-POS-tag.png` |

Catatan: nama berkas `B-indobert-cased.png` masih memakai kata "cased", tetapi **judul di dalam gambar sudah "IndoBERT phase-1"** (hanya nama berkas yang belum di-rename).

## C. Perbandingan kesalahan (⚠️ PERLU DICEK / kemungkinan regen)
| Gambar | Isi | Kandidat berkas |
|---|---|---|
| 4.5 | Perbandingan kesalahan 5 skenario Uji Coba 1 | `error_analysis_done_newest/by_group/s1_compare.png` |
| 4.10 | Perbandingan kesalahan 5 model Uji Coba 2 | `error_analysis_done_newest/by_group/s2_compare.png` |
| 4.15 | Perbandingan kesalahan baseline vs POS Uji Coba 3 | `error_analysis_done_newest/by_group/s3_compare.png` |

⚠️ **Verifikasi dulu**: pastikan angka pada gambar cocok dengan Tabel 4.4 / Tabel kesalahan di teks (mis. UC1 baseline 165, augmentasi 78). Bila gambar masih dari run lama, regenerasi agar sesuai benchmark GT-terkoreksi.

## D. Gambar graf — SCREENSHOT Neo4j (kamu buat sendiri)
Jalankan kueri lalu screenshot hasil di Neo4j Browser.
Kueri: `data/result/neo4j/sna_evidence_queries_bab4.cypher` & `functional_test_queries_bab4.cypher`

| Gambar | Isi | Kueri |
|---|---|---|
| 4.16 | Subgraf Peristiwa Perang Badr | `sna_evidence_queries_bab4.cypher` |
| 4.17 | Jaringan ego Muhammad | `sna_evidence_queries_bab4.cypher` |
| 4.18 | Jaringan ego Abu Bakar | `sna_evidence_queries_bab4.cypher` |
| 4.19 | Subgraf komunitas terbesar (community = 0) | `sna_evidence_queries_bab4.cypher` |
| 4.20 | Sentralitas peristiwa (5 simpul Event + tokoh) | `sna_evidence_queries_bab4.cypher` |
| 4.21 | Hasil kueri fungsional | `functional_test_queries_bab4.cypher` |

## Catatan konsistensi confusion (Pak Aldi #3)
§2.8 mendefinisikan dua tingkat: **entitas = 4 tipe** dan **token = 9 kelas BIO**.
Caption Bab 4 saat ini berbunyi "Confusion Matrix Tingkat Token".
- Jika ingin **konsisten dengan §2.8**, pakai versi **9 kelas BIO** (`confusion_revisi/bio_token/`).
- Jika ingin versi **5 kelas** yang lebih mudah dibaca (`confusion/`), ubah caption/teks menjadi
  mis. "confusion matrix tingkat token yang digabung per tipe entitas" agar tidak bertentangan
  dengan pernyataan "sembilan kelas BIO" di §2.8, atau tampilkan versi 9 kelas di Lampiran.
