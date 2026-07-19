# Tracking Perubahan Buku TA per Bab — Revisi Sidang

> Peta 22 poin revisi (Dosen-1 = **D1.x**, Dosen-2 = **D2.x**) ke **bab/berkas yang diubah**,
> supaya perubahan mudah dilacak saat mengedit buku di Word. Sumber poin:
> `docs/revisi/Poin_Revisi_Dosen_Sidang_TA.md` (+ `_penjelasan.md`).
>
> **Status:** ⬜ belum · 🟡 proses · 🧰 artefak siap (tinggal tulis di Word) · ✅ selesai di buku
> · 📝 murni penulisan · ⚠️ perlu keputusan

Terakhir diperbarui: 2026-07-17.

---

## Ringkasan lintas-bab (tiap poin bisa menyentuh >1 bab)

| Poin | Ringkas | Bab 2 | Bab 3 | Bab 4 | Bab 5 | Lamp. | Format |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| D1.1 | Bentuk & bobot relasi KG + keterbatasan PERSON–TIME | | ● | ● | | | |
| D1.2 | Tata letak (bab halaman ganjil, header tabel) | | | | | | ● |
| D1.3 | Rujukan nomor persamaan | ● | ● | ● | | | |
| D1.4 | Confusion matrix (teori + hasil + lampiran) | ● | | ● | | ● | |
| D1.5 | Dasar pemilihan hyperparameter | | ● | | | | |
| D1.6 | Beda weighted-CE / SCL / augmentasi + contoh + distribusi | ● | ● | ● | | ● | |
| D1.7 | Perbaiki klaim augmentasi "menyeimbangkan" | | | ● | | | |
| D1.8 | Warna grafik = legenda | | | ● | | | |
| D1.9 | Evaluasi tanda baca sebagai token | | ● | ● | | | |
| D1.10 | Perbedaan model cased vs uncased | ● | | ● | | | |
| D1.11 | Isi / hapus lampiran kosong | | | | | ● | |
| D2.1 | Contoh konkret NER: kalimat→BIO→entitas→node | | ● | ● | | | |
| D2.2 | Bentuk 1 record data latih utuh | | ● | | | | |
| D2.3 | Istilah chunk/token/subtoken/batch | ● | ● | | | | |
| D2.4 | Penyelarasan label BIO ↔ subtoken | | ● | | | | |
| D2.5 | Alur NER → knowledge graph (runtut + diagram) | | ● | | | | |
| D2.6 | Ganti istilah "alias clustering" → normalisasi alias | ● | ● | | | | |
| D2.7 | Dasar batas co-occurrence ~200 karakter + referensi | ● | ● | | | | |
| D2.8 | Kesalahan relasi akibat negasi | | ● | ● | ● | | |
| D2.9 | Referensi konstruksi KG (entity linking/RE/co-occurrence) | ● | ● | | | | |
| D2.10 | Evaluasi kualitas KG (teori/prosedur/hasil) | ● | ● | ● | | ● | |
| D2.11 | Bedakan "kueri berhasil" vs "jawaban benar" | | | ● | ● | | |

---

## BAB 2 — Tinjauan Pustaka & Dasar Teori

| Poin | Perubahan | Status | Artefak / catatan |
|---|---|:-:|---|
| D1.4 | **Tambah subbab teori Confusion Matrix**: definisi, level entity vs token-BIO, hubungan ke precision/recall/F1. | 🧰📝 | Angka & gambar contoh sudah ada (lihat Bab 4). Perlu paragraf teori. |
| D1.10 | Teori model **cased vs uncased** (cased simpan kapital; uncased normalisasi) + relevansinya utk NER nama diri. | 📝 | Temuan proyek: defisit cased/roberta ada sejak base (misalignment tokenizer), bukan self-training. |
| D2.3 | Definisi **chunk / token / subtoken / batch** (boleh di Bab 2 atau Bab 3). | 📝 | |
| D2.6 | Kalau istilah diganti, jelaskan dasar **normalisasi alias / Jaro–Winkler** (bukan "clustering"). | 📝 | Lihat catatan D2.6 di Bab 3. |
| D2.7 | Referensi **relation extraction berbasis co-occurrence** + dasar jendela ~200 karakter. | ⬜📝 | Perlu cari 1–2 paper co-occurrence RE. |
| D2.9 | Referensi **entity linking / entity normalization / relation extraction / konstruksi KG dari teks**. | ⬜📝 | Perlu sitasi nyata (jangan mengarang). |
| D2.10 | **Dasar teori evaluasi kualitas KG** (ketepatan node/relasi, konsistensi skema, precision relasi manual). | 🟡📝 | ⚠️ Evaluasi FUNGSIONAL (competency questions F1–F6) SUDAH ADA di §2.7 — tapi penguji bilang itu BELUM CUKUP. Yang kurang = evaluasi KUALITAS KUANTITATIF (precision relasi). Fungsional dipertahankan, kualitas ditambah. + isi 2 `[SITASI]` kosong §2.7. |
| D1.6 | Dasar teori **class imbalance** + Imbalance Ratio (untuk klaim D1.7). | 🟡📝 | Referensi terverifikasi: López–Fernández–García, *Information Sciences* 2013; konvensi IR>1,5. **Ambang low/mod/high (≤2/2–9/>9) verifikasi paper dulu.** |
| D1.3 | Rujuk semua persamaan Bab 2 dengan nomor eksplisit ("… pada Persamaan (2.x)"). | ⬜📝 | |

## BAB 3 — Metodologi

| Poin | Perubahan | Status | Artefak / catatan |
|---|---|:-:|---|
| D2.1 | Tambah **contoh konkret NER**: kalimat asli → tokenisasi → BIO → entitas → node. | 🧰 | `docs/revisi/artefak/contoh_ner_dan_data_latih.md` (contoh Mush'ab bin Umair → Makkah). |
| D2.2 | Tampilkan **1 record data latih utuh** (chunk_id, teks, token, POS, BIO, metadata bab/hal). | 🧰 | idem — record `000384-001` (semua 4 tipe; "Khaibar" LOCATION vs EVENT). |
| D2.4 | Jelaskan **penyelarasan BIO ↔ subtoken** (strategi label subtoken pertama, sisanya `-100`). | ⬜📝 | Perlu verifikasi strategi persis di kode tokenisasi. |
| D2.5 | **Alur NER → KG** 8 tahap (prediksi→gabung→normalisasi→dedup→node→relasi→Neo4j→uji) + diagram. | ⬜📝 | Sudah ada flowchart drawio; sesuaikan urutan. |
| D2.6 | **Ganti istilah "alias clustering"** → "normalisasi alias berbasis Jaro–Winkler + validasi manual" di seluruh buku. | 🧰📝 | **Keputusan: RENAME** (proses = kamus manual + JW safety-net, tanpa algoritma/evaluasi cluster). Bukti + perbandingan vs Rayssa: `docs/revisi/artefak/perbandingan_alias_clustering_rayssa.md`. |
| D2.7 | Dasar metode relasi: jendela co-occurrence ~200 karakter + apakah semua entitas otomatis terhubung. | ⬜📝 | |
| D2.8 | **Tulis sebagai KETERBATASAN** (keputusan user: tidak implementasi deteksi negasi). | 🟡📝 | Perlu: contoh relasi salah akibat negasi (mis. "Abu Jahal tidak mengikuti Perang Badar") + kalimat keterbatasan di Bab 3 & Bab 4/5. Bisa dibantu cari contoh nyata di korpus. |
| D1.1 | Perjelas **skema relasi KG** (PERSON–EVENT, EVENT–LOCATION/TIME, PERSON–PERSON) + definisi bobot. | ⬜📝 | |
| D1.5 | **Dasar pemilihan hyperparameter** (LR, batch, epoch, threshold, max-iter) — bukan sekadar "ikut notebook". | ⬜📝 | Framing: nilai awal dari penelitian acuan, diuji ulang di dataset Sirah. |
| D1.6 | Jelaskan cara kerja weighted-CE (bobot loss) / SCL (representasi) / augmentasi (tambah data). | 🧰📝 | Rumus SCL/JSCL/weighted-CE sudah ada di deliverable bimbingan sebelumnya. |
| D1.9 | Alasan **tanda baca dipertahankan** + aturan pengecualian tanda baca pada nama. | ⬜📝 | |
| D2.10 | **Prosedur pengujian kualitas KG** (sampling relasi + hitung precision manual). | ⬜📝 | Terkait skrip D2.10 (rencana). |
| D1.3 | Rujuk persamaan Bab 3 dengan nomor. | ⬜📝 | |

## BAB 4 — Hasil & Pembahasan

| Poin | Perubahan | Status | Artefak / catatan |
|---|---|:-:|---|
| D1.4 | **Confusion matrix entity-level (4 tipe)** sebagai gambar utama Bab 4. | ✅🧰 | `…/gt_corrected_2026_07_10/confusion_revisi/entity_level/S4-augmentation.png` + `confusion_revisi_summary.md`. Temuan: error deteksi ≫ salah-tipe. |
| D1.6 | Contoh augmentasi (before/after) + **distribusi kelas** pra/pasca. | 🧰 | `augmentasi_contoh_dan_distribusi.md` + `bab4_viz/augmentasi_distribusi_revisi.png`. |
| D1.7 | **Perbaiki klaim** augmentasi: "menurunkan ketimpangan (17,4:1→8,8:1), belum seimbang". | 🧰📝 | idem. |
| D1.8 | **Samakan warna grafik ↔ legenda** di semua chart hasil pengujian. | 🧰📝 | Chart kanonik: `bab4_viz/f1_skenario_semua_revisi.png` (angka GT-terkoreksi + warna per-grup cocok). Konvensi palet: `docs/revisi/artefak/konvensi_warna_grafik.md`. ⚠️ Cek chart di file Word/PPT — samakan ke palet. |
| D1.10 | Pembahasan hasil **cased vs uncased** dihubungkan ke karakteristik OCR/kapitalisasi. | 📝 | |
| D2.1 | Tunjukkan hasil NER (BIO) yang menjadi node — bisa ditaruh di Bab 4 juga. | 🧰 | idem Bab 3. |
| D2.8 | Tulis sebagai **keterbatasan** + contoh relasi salah akibat negasi. | 🟡📝 | Keputusan: keterbatasan (bukan implementasi). |
| D2.11 | Bedakan **"kueri berhasil" vs "jawaban benar"** pada evaluasi fungsional KG. | 📝 | Kalimat kesimpulan lebih hati-hati. |
| D2.10 | **Hasil evaluasi kualitas KG** (precision relasi dari sampling manual). | ⬜ | Terkait skrip D2.10. |
| D1.9 | Pembahasan efek tanda baca pada tokenisasi/prediksi (kalau relevan). | ⬜📝 | |
| D1.3 | Rujuk persamaan/tabel/gambar Bab 4 dengan nomor. | ⬜📝 | |

## BAB 5 — Kesimpulan & Saran

| Poin | Perubahan | Status | Artefak / catatan |
|---|---|:-:|---|
| D2.11 | Kesimpulan KG lebih hati-hati (dapat menjalankan penelusuran, ketepatan semantik perlu validasi). | 📝 | |
| D2.8 | Kalau negasi jadi keterbatasan → masuk saran/future work. | ⬜📝 | |

## LAMPIRAN

| Poin | Perubahan | Status | Artefak / catatan |
|---|---|:-:|---|
| D1.4 | **Confusion matrix seluruh skenario** (entity-level + token-BIO). | 🧰 | `…/confusion_revisi/entity_level/*.png` & `…/bio_token/*.png` (10 skenario). |
| D1.11 | **Isi lampiran kosong** (confusion semua skenario, contoh augmentasi, F1 per label, contoh Cypher, bukti uji fungsional) atau hapus. | ⬜📝 | |
| D1.6 | Contoh lengkap data augmentasi. | 🧰 | |
| D2.10 | Bukti sampling evaluasi kualitas KG. | ⬜ | |

## FORMAT DOKUMEN (lintas bab, dikerjakan di Word)

| Poin | Perubahan | Status |
|---|---|:-:|
| D1.2 | Tiap judul bab mulai **halaman ganjil**; cek halaman kosong/genap. | ⬜📝 |
| D1.2 | **Ulangi header** pada tabel yang berpindah halaman. | ⬜📝 |
| D1.3 | Rujuk semua persamaan dengan nomor eksplisit. | ⬜📝 |
| D1.8 | Konsistensi warna grafik ↔ legenda. | ⬜ |
| D1.11 | Rapikan lampiran (isi atau hapus). | ⬜📝 |

---

## Catatan keputusan

**Sudah diputuskan (2026-07-18):**
- ✅ **D2.6** — **RENAME** "alias clustering" → "normalisasi alias berbasis Jaro–Winkler + validasi manual". (Proses ≠ clustering Rayssa: tak ada algoritma/evaluasi cluster.)
- ✅ **D2.8** — **KETERBATASAN**, bukan implementasi deteksi negasi.
- ✅ **D1.6 paraphrase** — data paraphrase diregenerasi bersih dari kalimat Sirah yang sama (mention entitas dipertahankan, BIO valid) via `regen_paraphrase_clean.py`; tertulis di `train_augmented_final.csv`. Contoh di artefak = versi bersih.

**Masih terbuka (⚠️):**
1. **D2.10 evaluasi kualitas KG** — metrik mana yang dipakai (precision relasi manual + konsistensi skema + traceability)?
