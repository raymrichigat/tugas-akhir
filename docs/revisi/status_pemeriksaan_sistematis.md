# Status Pemeriksaan Sistematis Poin Revisi vs Teks Buku (.md)

> Dibuat 2026-07-20. Mengecek tiap poin `Poin-Revisi-TA-Terbaru.md` terhadap teks buku `.md`
> (abstrak, bab1-5) **saat ini**. Legenda: ✅ sudah di teks buku · ⚠️ sebagian (ada tapi kurang
> lengkap) · ❌ belum di teks buku · 🖥️ format/tata-letak = dikerjakan di Word (di luar .md).

## Pak Aldi
| # | Poin | Status | Catatan |
|---|---|:-:|---|
| 1 | Tata letak (bab halaman ganjil) | 🖥️ | Word |
| 2 | Rujuk persamaan bernomor + betweenness "s ke t" | ✅ | betweenness (2.13) sudah "𝑠 ke 𝑡"; persamaan dirujuk bernomor |
| 3 | Confusion matrix (teori + kelas 9 BIO/5) | ✅ | teori §2.8; Bab 4 kini tampil terbaik saja + Lampiran A |
| 4 | Caption tabel | 🖥️ | Word; **Tabel 4.28 caption sudah dibetulkan** ✅ |
| 5 | Dasar hyperparameter | ✅ | §3.6 (Ariyanto 2025, per-parameter) |
| 6 | Imbalance: contoh augmentasi + distribusi | ✅ | **baru ditambah** (contoh Tabuk→Uhud + rasio 17,4:1→8,8:1) |
| 7 | Legenda warna grafik | ✅ | chart diperbaiki (warna=legenda, pemenang bold) |
| 8 | **Fungsi token tanda titik (.)** | ❌ | disinggung di Bab 4 (OCR), **belum dijelaskan di metodologi Bab 3** |
| 9 | Cased vs uncased diperkenalkan Bab 2 | ✅ | §2.4.2 |
| 10 | Lampiran tidak kosong + placeholder | ⚠️ | rujukan Lampiran A/B sudah di .md; **isi lampiran = Word** |

## Bu Nanik
| # | Poin | Status | Catatan |
|---|---|:-:|---|
| 1 | **Contoh NER berjalan (kalimat→BIO→entitas)** | ✅ | §3.6 kini pakai kalimat **Abu Jahal** yang sama dgn §3.7 (benang merah NER→KG utuh, ada kalimat penghubung eksplisit). Tabel 3.9/3.12 tetap sbg ilustrasi tambahan (4 tipe label + keluaran multi-entitas) |
| 2 | **Record data latih utuh** | ⚠️ | kolom (text_id/id/pos_tag/label) dijelaskan; **belum ada tabel contoh 1 record terisi lengkap** |
| 3 | Definisi token/subtoken/batch | ✅ | §3.6 (word_ids, -100) |
| 4 | Alur NER→KG | ✅ | Abu Jahal §3.7 |
| 5 | "alias clustering"→normalisasi alias | ✅ | 4 tempat + klarifikasi JW |
| 6 | Metode relasi 200-char + contoh + aturan Invalid* | ✅ | 200-char + contoh benar/salah + negasi ✅; aturan Invalid\* diuraikan operasional §3.7.2; **rujukan paper co-occurrence** (Choi & Jung 2025 + Zhao et al. 2023) ditambah §2.7/§3.7.2 |
| 7 | Referensi konstruksi KG + batas heuristik | ✅ | §2.7 (Zhong 2024, Sevgili 2022) |
| 8 | Pengukuran kualitas KG (validitas semantis) | ✅ | §2.7/§3.9.2/§4.5.8 (31,58%) |

## Bu Ratih
| # | Poin | Status | Catatan |
|---|---|:-:|---|
| 1 | Abstrak istilah + batas validitas | ✅ | ID+EN |
| 2 | Tata letak | 🖥️ | Word |
| 3 | Notasi persamaan (semua variabel dijelaskan) | ✅ | tiap persamaan diberi keterangan simbol |
| 4 | Contoh chunking sebelum/sesudah | ✅ | §3.4 (contoh "Kekuasaan di Berbagai Penjuru Arab") |
| 5 | Koreksi manual + anotator tunggal | ✅ | §3.5.2 |
| 6 | Contoh BIO 1 kalimat lengkap | ✅ | §3.6 contoh berjalan (Abu Jahal) kini menampilkan token→BIO→entitas satu kalimat utuh yang menyambung ke §3.7; Tabel 3.9 tetap sbg contoh 4 tipe label |
| 7 | **JW 0,93 justifikasi empiris** | ⚠️ | ada alasan (0,93 vs 0,85 + guard + exclude); **belum ada hasil uji beberapa ambang (sweep)** |
| 8 | Keterbacaan confusion matrix | ✅ | diperbesar |

## Bu Dini
| # | Poin | Status | Catatan |
|---|---|:-:|---|
| 1 | Tata letak | 🖥️ | Word |
| 2 | Augmentasi minoritas + klaim | ✅ | baru |
| 3 | Output graf diperbesar | 🖥️ | Word/gambar |
| 4 | Font daftar pustaka | 🖥️ | Word |
| 5 | **Output data train (tabel)** | ⚠️ | sama Nanik #2 |
| 6 | GT vs prediksi | ✅ | §4.2 (1969 → 1921 benar) |
| 7 | Alur NER→KG | ✅ | Abu Jahal |
| 8 | Analisis error taksonomi | ✅ | §4.2 (Tabel 4.4–4.8 + pembahasan) |

## Temuan Tambahan
| # | Poin | Status |
|---|---|:-:|
| 1 | Tujuan penelitian (SNA deskripsi) | ✅ |
| 2 | Caption Tabel 4.28 | ✅ |
| 3 | Protokol validasi (F5 = 21 jalur) | ✅ |
| 4 | Batas klaim SNA | ✅ |
| 5 | Konsistensi istilah | ✅ |
| 6 | Redaksional Bab 5 pembuka | ✅ |

## Ringkasan GAP — SEMUA DITUTUP (2026-07-20)
1. **Pak Aldi #8** — ✅ **DIPUTUSKAN: hapus baris token "." dan ","** dari seluruh contoh Bab 4 (Tabel 4.5–4.8, 4.13, 4.16) + "Hudaibiyah." → "Hudaibiyah"; Bab 3 sudah bersih. (Bukan penjelasan fungsi, tapi penghapusan sesuai opsi Pak Aldi.)
2. **Bu Nanik #2 / Bu Dini #5** — ✅ tabel **1 record data latih** (chunk 000384-001) ditambah ke §3.5.3 (text_id/id/token/pos_tag=NN/BIO + metadata; tanda baca dibuang) + poin "Khaibar LOC vs EVENT".
3. **Bu Nanik #1 / Bu Ratih #6** — ✅ **contoh NER berjalan** (Mush'ab bin Umair → Makkah) ditambah ke §3.6 (token→BIO→entitas→node).
4. **Bu Ratih #7** — ✅ **sweep ambang JW** (0,85=359 … 0,93=103 … 0,95=90; 255/256 borderline beda entitas + contoh) ditambah ke §3.7.1.
5. **Bu Nanik #6** — ✅ aturan **InvalidInvolvedIn/OccurredAt/OccurredOn** diuraikan operasional di §3.7.2 (dari kode `relation_extraction.py`: perawi/ayat-Quran/"meninggal dunia" dll; berbasis pola, negasi tetap keterbatasan).

**Semua GAP teks buku CLOSED.** Sisanya murni format/Word (halaman ganjil, header tabel, font pustaka, isi fisik lampiran, perbesar gambar).
