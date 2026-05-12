# Revisi Dosen — Bu Diana

Catatan raw dari pertemuan revisi dengan Bu Diana. Format: bullet point pendek apa adanya, lalu di-propagasi ke dokumen skenario terkait (`srl_ner_skenario.md`, `graf_pengujian_skenario.md`, `temporal_skenario.md`, `bimbingan.md`).

---

## Putaran 1 — 2026-05-03

**Masukan**
- Temporal dalam satu kalimat (?) perlu di deteksi (bisa dilihat dari urutan kejadian di Sirah / urutan bab nya)
- Lalu pembentukan graf, memperhatikan Temporal waktu, baru ke fitur graf nya

**Uji coba**
- Kasus perang badar, diamati keterlibatan nya apa saja lalu diamati graf nya (sampling beberapa event). Kalo misalnya kesalahan dari awal, nanti akan berpengaruh ke perhitungan fitur nya (ambil beberapa contoh 3 atau 5 fitur, dengan periode yang jauh. Tunjukkan dalam graf seperti apa lalu di analisis, untuk yang lain juga seperti apa)

**NER**
- LLM-NER tidak jadi digunakan, jadinya menggunakan SRL-NER saja
- SRL NER ini perlu di definisikan skenario nya seperti apa (seperti thresholdnya saja kah atau ada yang lainnya)
- Untuk perbandingan Threshold bisa digunakan seperti fix threshold atau adaptif (kalau terlalu rendah akan otomatis diturunkan)
- Kalau mau mengganti model silahkan, tetapi kalau tidak mau ribet bisa myang lainnya dahulu
- Kalau unbalanced perlu di handling dan ini ada berbagai macam (definisikan dulu skenario seperti apa, perlu effort nya lebih lagi)

**Graf**
- Perlu uji coba lain selain centrality (community atau lainnya)
- Centrality → fokus ke node (fokus ke graf gede nya, seperti clustering, ukuran network nya berapa, seperti density, dkk)

---

## Putaran 3 — 2026-05-07

> Pertemuan ini dilakukan **setelah** run 3 skenario SRL-NER (E1 + S1 + S2) selesai. Bu Diana melihat hasil run dan kasih saran skenario lanjutan untuk handling kelas minoritas (EVENT) yang masih belum optimal di S1/S2.

**Tambahan skenario SRL-NER**
- Coba tambah skenario tentang **contrastive learning (pembobotan)** antara **JSCL** vs **SCL**
- Kesulitan **multi-label** bisa diatasi dengan **oversampling** (Bisa, tetapi susah)
- Alternatif: **augmentasi sentence-based** — 1 kalimat yang fokusnya ke kelas minor, ditambahkan ke data train
- Catatan: Bu Diana tidak menyebut paper spesifik untuk JSCL/SCL; disarankan **bertanya ke teman yang sudah pernah implementasi** untuk referensi konkret

> Propagasi: detail skenario awalnya disusun jadi S3+S4 di atas skenario lama (class weight + adaptive). **Per 2026-05-11, skenario direstrukturisasi total** — lihat Putaran 4 di bawah.

---

## Putaran 4 — 2026-05-11 (Restrukturisasi Skenario)

> Bukan pertemuan baru dengan Bu Diana. Ini keputusan internal mahasiswa untuk **merombak struktur skenario** supaya lebih bersih dan layer-by-layer, sambil mengakomodasi masukan putaran 3 (contrastive + augmentation). Akan dikonfirmasi ke Bu Diana di bimbingan berikutnya.

**Skenario baru (menggantikan E1+S1 class weight+S2 adaptive lama dan S3+S4 putaran 3):**

| Skenario | Komponen |
|---|---|
| **S1 — Baseline** | Fix THRESHOLD=0.9, tanpa handle imbalance, tanpa contrastive, tanpa augmentation |
| **S2 — Contrastive Learning + Baseline** | S1 + supervised contrastive loss (SCL/JSCL) |
| **S3 — Sentence-based Augmentation + S2** | S2 + augmentasi kalimat fokus kelas minor (EVENT, TIME, I-LOCATION) |

**Alasan restrukturisasi:**
- Skenario lama (class weight + adaptive) sudah dijalankan 2026-05-07 — class weight murni belum cukup untuk EVENT (F1 stuck 0.83), trade-off precision-recall terlalu tajam (S2 lama precision 0.74).
- Bu Diana putaran 3 minta tambah contrastive learning + sentence augmentation. Awalnya direncanakan jadi S3+S4 di atas skenario lama → terlalu banyak skenario (E1+S1+S2+S3+S4) dan tidak isolasi efek dengan jelas.
- Restrukturisasi baru: 1 skenario = 1 layer kontribusi (baseline → +contrastive → +augmentation). Lebih mudah dianalisis kontribusi marginal tiap komponen.

**Yang tidak hilang:**
- Hasil run E1 baseline lama → direuse sebagai S1 baru (skenario teknis identik).
- Hasil run S1/S2 lama (class weight + adaptive) tetap disimpan di `done_running/legacy_class_weight_adaptive/` — bisa direferensikan di Bab 4 sebagai studi pendahuluan / ablation pembanding.

**Status:**
- **S1** ✅ selesai (reuse hasil E1 lama: F1 entity=0.959, F1 EVENT=0.816).
- **S2** ⏳ menunggu paper SCL/JSCL konkret dari teman + konfirmasi Bu Diana.
- **S3** ⏳ depend on S2.

**Action item sebelum coding:**
1. Hubungi teman untuk paper SCL/JSCL konkret.
2. Konfirmasi Bu Diana scope final (lihat `srl_ner_skenario.md` §7.1).
3. Update `srl_ner_skenario.md` §3.6 + §4.3 dengan formulasi loss + strategi augmentasi konkret setelah dapat paper.

> Propagasi: skenario baru ada di `srl_ner_skenario.md` (rewrite total), `bimbingan.md`, `CLAUDE.md`. Hasil run lama tetap ada di `src/pseudo_labelling/SRL-NER/done_running/legacy_class_weight_adaptive/`.
