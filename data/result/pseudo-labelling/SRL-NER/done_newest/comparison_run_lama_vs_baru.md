# Perbandingan Run Lama (`done_running`) vs Run Baru (`done_newest`)

> Ringkas: **run lama = gold LAMA**, **run baru = gold TERKOREKSI** (hasil re-annotation atas arahan Bu Dini Adni). Karena **test set-nya berbeda**, angka F1 absolut **tidak boleh diadu head-to-head**. Yang valid dibandingkan adalah **peringkat antar-skenario** dan **arah kesimpulan** — dan itulah fokus dokumen ini.
>
> Sumber angka:
> - Run lama: `data/result/pseudo-labelling/SRL-NER/seqeval_grupB_results.md` (Grup A+B) + `seqeval_postag_direct.md` (POS-tag, inferensi langsung).
> - Run baru: `data/result/pseudo-labelling/SRL-NER/done_newest/seqeval_done_newest_results.md`.

---

## 0. Kenapa angka tidak comparable (baca dulu)

Ada **dua** hal yang berubah antar-run, dua-duanya menggeser angka tanpa ada kaitannya dengan "model jadi lebih baik/buruk":

**(1) Test set berubah — gold di-re-annotate.** Jumlah entitas gold di test naik:

| Kelas | Support test LAMA | Support test BARU | Perubahan |
|---|---:|---:|---:|
| PERSON | 1.189 | 1.285 | +96 |
| LOCATION | 449 | 449 | 0 |
| EVENT | 51 | 73 | +22 |
| TIME | 74 | 98 | +24 |
| **Total** | **1.763** | **1.905** | **+142** |

Yang paling naik justru **EVENT & TIME** — dua kelas paling sulit dengan F1 terendah. Karena micro-F1 itu rata-rata tertimbang jumlah entitas, menambah entitas di kelas sulit **secara mekanis menurunkan micro-F1**, bahkan andai modelnya identik. Jadi penurunan tipis di hampir semua skenario **sebagian besar efek test set, bukan degradasi model**. (LOCATION tidak berubah → paling mendekati apple-to-apple.)

**(2) Iterasi yang dilaporkan berbeda.** Run lama melaporkan tiap skenario di **checkpoint terakhir yang tersimpan** — dan untuk sebagian skenario checkpoint terakhir itu **<6** (SCL = iteration-4, augmentation = iteration-5, POS-tag = iteration-4, sisanya iteration-6). Ini **bukan** cherry-pick puncak di tengah run: SCL/augmentation/POS-tag berhenti lebih awal karena **kolam pseudo-label-nya habis** (`below=0`), jadi iteration-4/5 itu justru **titik konvergen final** mereka (lihat §1b untuk bukti per-iterasi). Run baru **seragam iteration-6** untuk semua tanpa peduli sudah plateau atau belum. Efeknya: menyandingkan "checkpoint-final run lama" vs "iteration-6 run baru" bukan perbandingan titik yang sama, sehingga sebagian geseran peringkat (mis. SCL) adalah **artefak beda titik-lapor**, bukan sinyal kualitas model.

> **Catatan penomoran (supaya tidak bingung dengan §1b):** checkpoint `iteration-1` = model seed (belum ada pseudo-label). Tiap **ronde prediksi** menambah satu paket pseudo-label lalu menyimpan checkpoint berikutnya, jadi **checkpoint tertinggi = (jumlah ronde prediksi) + 1**. Di §1b kolom "ronde prediksi" dihitung dari file `above/below-0.9.xlsx`; angka checkpoint di seqeval = ronde + 1. Contoh: SCL kolam habis di **ronde-3** → checkpoint final **iteration-4**.

> **Kesimpulan bagian ini:** jangan tulis "F1 turun dari 0,9581 ke 0,9458 berarti augmentasi memburuk". Yang benar: *dua benchmark berbeda*; bandingkan **peringkat** dan **pola**, bukan selisih absolut.

---

## 1. Perbandingan F1 entity-level (micro) semua skenario

| Skenario | F1 LAMA | F1 BARU | Δ | Peringkat LAMA → BARU |
|---|---:|---:|---:|:--:|
| S4-augmentation | 0.9581 | 0.9458 | −0.0123 | **#1 → #1** |
| S3a-SCL | 0.9512 | 0.9409 | −0.0103 | #2 → #4 |
| S1-baseline | 0.9481 | 0.9420 | −0.0061 | #3 → #3 |
| B-distilbert | 0.9442 | 0.9347 | −0.0095 | #4 → #5 |
| S5-POS-tag | 0.9439\* | 0.9430 | −0.0009 | #5 → #2 |
| S3b-JSCL | 0.9434 | 0.9344 | −0.0090 | #6 → #6 |
| S2-weighted-CE | 0.9393 | 0.9333 | −0.0060 | #7 → #7 |
| B-cahya-1.5G | 0.9324 | 0.9295 | −0.0029 | #8 → #8 |
| B-roberta | 0.8068 | 0.8049 | −0.0019 | #9 → #9 |
| B-indobert-cased | 0.7770 | 0.7755 | −0.0015 | #10 → #10 |

\* POS-tag lama dari `eval_postag_direct.py` (inferensi langsung iter-4), bukan dari tabel seqeval utama (butuh rebuild arsitektur `BertPosNER`). Run baru POS-tag = rekonstruksi iter-6.

**Bacaan:**
- **Semua Δ negatif & kecil** (−0.001 s/d −0.012) → geseran seragam, konsisten dengan penjelasan "test lebih berat", bukan satu model kolaps.
- **Peringkat sangat stabil di dua ujung:** augmentasi **#1 di kedua run**; cased **#10** & roberta **#9** di kedua run; cahya **#8** & weighted-CE **#7** di kedua run.
- **Yang bergeser cuma di klaster tengah uncased** (baseline/SCL/JSCL/distilbert/POS-tag) yang memang berdempet di rentang ~0.93–0.95; pergeseran SCL (#2→#4) & POS-tag (#5→#2) sebagian **artefak beda titik-lapor** — run lama pakai checkpoint konvergen (<6), run baru pakai iteration-6 (lihat §0 poin 2 & §1b) — bukan sinyal kuat.

---

## 1b. Konvergensi self-training run lama (rekonstruksi dari file `above/below-0.9`)

Dihitung langsung dari `*-above-0.9.xlsx` / `*-below-0.9.xlsx` tiap skenario di `done_running`, dengan **satuan = `text_id` unik (chunk)** — metodologi sama seperti analisis konvergensi run baru di `docs/bimbingan/2026-07-07.md` §2.1. Total kolam unlabelled run lama = **237 chunk** (konsisten di kesepuluh skenario; run baru = 250).

- `n_above` = chunk dipromosikan tiap **ronde prediksi**. Gate = **rata-rata confidence token entitas (label ≠ `O`) ≥ 0,9** — token `O` tak dihitung, dan chunk tanpa prediksi entitas otomatis `below` (dari kode `filter_threshold()`; lihat koreksi mekanisme di 2026-07-07 §2.1).
- "Sisa kolam" = chunk `below` unik di ronde terakhir yang tersimpan.
- **Ronde prediksi vs checkpoint:** checkpoint di seqeval = ronde + 1 (lihat catatan penomoran di §0 poin 2).

| Skenario | `n_above` per ronde (1→6) | Ronde akhir | Sisa kolam | Checkpoint final | Status konvergensi |
|---|---|:--:|:--:|:--:|---|
| **scl** | 196, 39, 2 | 0 | **0** | iteration-4 | ✅ **kolam habis** (ronde-3, `below=0`) |
| **augmentation** | 217, 14, 4, 2 | 0 | **0** | iteration-5 | ✅ **kolam habis** (ronde-4, `below=0`) |
| **pos-tag** | 226, 10, 0, 1 | 0 | **0** | iteration-4 | ✅ **kolam habis** (ronde-4, `below=0`) |
| baseline | 190, 34, 8, 4, 0, 0 | 0 | 1 | iteration-6 | ✅ plateau (ronde-5) |
| indobert-cased | 156, 31, 36, 11, 1, 0 | 0 | 2 | iteration-6 | ✅ plateau (ronde-6) |
| cahya | 181, 47, 3, 2, 0, 0 | 0 | 4 | iteration-6 | ✅ plateau (ronde-5) |
| weighted-CE | 206, 24, 3, 2, 0, **1** | 1 | 1 | iteration-6 | ⚠️ berombak (0→1 di ronde-6) |
| distilbert | 178, 41, 11, 1, 2, **3** | 3 | 1 | iteration-6 | ⚠️ blm plateau |
| jscl | 177, 38, 12, 3, 1, **1** | 1 | 5 | iteration-6 | ⚠️ blm plateau |
| roberta | 143, 65, 12, 6, 3, **3** | 3 | 5 | iteration-6 | ⚠️ blm plateau |

> Verifikasi: kumulatif `n_above` + sisa kolam `below` = **237** untuk kesepuluh skenario ✓.

**Bacaan:**
1. **Tidak semua konvergen sama.** 3 skenario (**scl, augmentation, pos-tag**) malah **menghabiskan kolam** (`below→0`) — rata-rata confidence entitas semua chunk unlabelled akhirnya tembus 0,9, jadi loop berhenti karena **tak ada sisa**, bukan kena batas iterasi. Ini konvergensi lebih tuntas daripada run baru (di run baru semua skenario menyisakan ~10–19 chunk residu permanen, mis. kutipan Al-Qur'an/doa — lihat 2026-07-07 §2.1).
2. **4 plateau** dengan residu kecil (baseline, cased, cahya; weighted-CE plateau tapi berombak 0→1 di ronde terakhir).
3. **3 belum plateau** di ronde terakhir yang tersimpan: **jscl (1), distilbert (3), roberta (3)** — masih mempromosikan chunk. **roberta paling belum stabil** (residu 5, masih promosi 3), konsisten dengan pola anomalinya di run baru & Grup B.
4. **Implikasi untuk §0 poin 2:** karena scl/aug/pos-tag konvergen di <6, checkpoint final mereka memang iteration-4/5/4 — **titik konvergen sah, bukan puncak yang dipetik**.

⚠️ **Catatan jujur — belum ditelusuri:** kenapa run lama bisa menghabiskan kolam (237→0) untuk sebagian skenario, sedangkan run baru selalu menyisakan residu (~10–19 dari 250)? Kolam beda (237 vs 250) **dan** gold beda (lama vs terkoreksi). Belum ada verifikasi sebab pastinya — jangan diklaim sebagai temuan sebelum ditelusuri.

---

## 2. Perbandingan per-kelas (fokus minoritas EVENT & TIME)

Karena EVENT & TIME yang paling terdampak re-annotation, ini inti perubahan kesimpulan.

**Baseline:**

| Kelas | F1 LAMA | F1 BARU | Δ |
|---|---:|---:|---:|
| PERSON | 0.9596 | 0.9577 | −0.0019 |
| LOCATION | 0.9527 | 0.9440 | −0.0087 |
| EVENT | 0.8039 | 0.8800 | **+0.0761** |
| TIME | 0.8408 | 0.7890 | **−0.0518** |

**Augmentation (winner kedua run):**

| Kelas | F1 LAMA | F1 BARU | Δ |
|---|---:|---:|---:|
| PERSON | 0.9640 | 0.9653 | +0.0013 |
| LOCATION | 0.9653 | 0.9453 | −0.0200 |
| EVENT | 0.9020 | 0.8874 | −0.0146 |
| TIME | 0.8627 | 0.7580 | **−0.1047** |

**Bacaan:**
- **EVENT baseline NAIK** (0.80→0.88) setelah gold dikoreksi. Interpretasi jujur: sebagian yang dulu dihitung "salah deteksi EVENT" ternyata **memang EVENT yang belum teranotasi** di gold lama (mis. `perang` huruf kecil). Setelah gold dirapikan, prediksi model jadi dihitung benar. Ini **mendukung temuan lama** soal inkonsistensi kapitalisasi gold.
- **TIME TURUN tajam** di kedua skenario (augmentasi −0.10). Gold baru menambah 24 entitas TIME, dan tambahan itu tampaknya kasus yang lebih sulit → F1 TIME turun. Ini menandai TIME sebagai kelas paling rapuh dan paling sensitif terhadap definisi anotasi.

---

## 3. Perubahan kesimpulan penting: macro-F1 augmentasi

| Skenario | macro-F1 LAMA | macro-F1 BARU | Δ |
|---|---:|---:|---:|
| S1-baseline | 0.8892 | 0.8927 | +0.0035 |
| S4-augmentation | **0.9235** | **0.8890** | **−0.0345** |

Ini poin paling penting untuk kejujuran ke Bu Dini:

- **Run lama:** augmentasi menang **micro DAN macro** secara meyakinkan (macro 0.9235 ≫ baseline 0.8892) → mendukung hipotesis "augmentasi menutup gap kelas minoritas".
- **Run baru:** augmentasi tetap menang **micro** (via PERSON), **tapi macro-nya (0.8890) sedikit DI BAWAH baseline (0.8927)** — karena TIME-nya jatuh. Artinya klaim "augmentasi mengangkat kelas minoritas" **tidak tereplikasi** di bawah gold terkoreksi.

> Ini bukan kabar buruk, ini temuan. Yang berubah cuma *sebab* augmentasi menang: **run lama = angkat minoritas; run baru = kuatkan PERSON**. Layak disebut eksplisit di Bab 4 sebagai batas klaim.

---

## 4. Apa yang BERTAHAN vs BERUBAH (ringkasan untuk dibahas)

**Bertahan (kesimpulan robust di kedua gold — aman ditulis):**
1. **Augmentasi = skenario terbaik (micro-F1)** di kedua run.
2. **Model cased & roberta kolaps** (F1 ~0.78–0.81) di kedua run — konsisten dengan diagnosis misalignment tokenizer di PERSON, bukan mutu model.
3. **POS-tag ≈ baseline** (selisih < 0.001–0.002) di kedua run → **POS-tag tidak membantu** (rekonstruksi tervalidasi).
4. **weighted-CE < baseline** di kedua run.
5. **cahya & distilbert (uncased) stabil di ~0.93–0.94** di kedua run.

**Berubah (efek re-annotation — perlu disebut sebagai batas klaim):**
1. Keunggulan minoritas augmentasi (**macro-F1**) **tidak tereplikasi**; TIME turun.
2. EVENT baseline **naik** → bukti tambahan inkonsistensi gold lama sudah sebagian terkoreksi.
3. Peringkat internal klaster uncased sedikit bergeser (SCL & POS-tag) — sebagian artefak iterasi.

**TIDAK boleh disimpulkan:**
- "Model memburuk karena F1 turun." (Salah — test beda + iterasi beda.)
- Selisih F1 lama−baru sebagai ukuran perbaikan/penurunan kualitas model.

---

## 5. Cara menyajikan ke Bu Dini (1 kalimat)

> "Setelah gold diperbaiki, angka absolut tidak bisa diadu dengan run lama karena test-nya beda, tapi **kesimpulan utamanya bertahan** — augmentasi tetap terbaik, cased/roberta tetap kolaps, POS-tag tetap tidak membantu — dan satu klaim melemah dengan jujur: keunggulan augmentasi di kelas minoritas (macro-F1) tidak lagi tampak, terutama karena TIME."

---

_Catatan reproduksi: dokumen ini sintesis dua laporan seqeval yang sudah ada (tanpa menjalankan model). Bila gold berubah lagi, regen `seqeval_grupB_results.md`/`seqeval_done_newest_results.md` dulu, lalu perbarui tabel di sini._
