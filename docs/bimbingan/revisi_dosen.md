# Revisi Dosen — Bu Diana

Catatan raw dari pertemuan revisi dengan Bu Diana. Format: bullet point pendek apa adanya, lalu di-propagasi ke dokumen skenario terkait (`../skenario/srl_ner.md`, `../skenario/graf_pengujian.md`, `../skenario/temporal.md`, `bimbingan_template.md`).

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
2. Konfirmasi Bu Diana scope final (lihat `../skenario/srl_ner.md` §7.1).
3. Update `../skenario/srl_ner.md` §3.6 + §4.3 dengan formulasi loss + strategi augmentasi konkret setelah dapat paper.

> Propagasi: skenario baru ada di `../skenario/srl_ner.md` (rewrite total), `bimbingan_template.md`, `../../CLAUDE.md`. Hasil run lama tetap ada di `../../src/pseudo_labelling/SRL-NER/done_running/legacy_class_weight_adaptive/`.

---

## Putaran 5 — 2026-05-16 (Bimbingan Aktual)

> Bimbingan dual-focus: evaluasi Knowledge Graph (cluster #2 + #4) + hasil SRL-NER S2 contrastive (cluster #3). Catatan mentah outcome ada di `2026-05-16_outcome.md`.

**Graf — Centrality (revisi tambahan)**
- Centrality jangan hanya untuk node Person — **Event juga harus dihitung centrality-nya** (degree, betweenness, closeness, PageRank)
- Lihat juga "bagaimana node lain berpengaruh terhadap event" (sudut pandang non-Event ke Event)

**Graf — Community detection**
- Tidak ada masukan tentang metode (Louvain/Greedy/Girvan-Newman OK)
- Yang diminta: **interpretasi lebih dalam**:
  - Modularity Q = 0.327 itu apa artinya secara konkret?
  - 13 komunitas itu apa interpretasinya per komunitas?
  - Tampilkan **wordcloud per-komunitas** (mis. wordcloud "zaman kejayaan Rasulullah" untuk salah satu komunitas)
  - Representasi grafis komunitas seperti apa (visual)?
  - **Kenapa node X masuk ke komunitas Y** (kualitatif, sample beberapa tokoh)?
  - **Tujuan terbentuknya komunitas itu untuk apa** (tambahan dari teman) — interpretasi semantik

**Graf — Studi kasus 5 event**
- Tambahkan analisis **event yang berelasi** dengan event sample
- Contoh: Perjanjian Hudaibiyah → event apa yang co-occur di period yang sama (P11)? Atau yang punya relasi (OCCURRED_AT/INVOLVED_IN) overlap?

**Graf — Visualisasi**
- Tidak ditunjukkan saat bimbingan, tapi Bu Diana **prefer visualisasi via Neo4j** (bukan PNG static)

**SRL-NER — S2 hasil**
- Tidak ada feedback langsung tentang gap Seq F1 (0.95 vs 0.959) — penjelasan saat bimbingan masih kurang clear
- Dual-metric (token sklearn vs entity seqeval) tidak dikomentari
- Interpretasi: **implicit OK** — Bu Diana tidak object, tapi belum ada arahan eksplisit "lanjut" atau "tune dulu"

**SRL-NER — Plan 3-skenario (mahasiswa propose, sudah approved)**
- Skenario 1: Baseline (S1 reuse hasil 2026-05-07)
- Skenario 2: SCL vs JSCL (S2a + S2b sudah selesai 14-15 Mei)
- Skenario 3: Best dari Skenario 2 + Augmented
- **Keputusan mahasiswa untuk Skenario 3:** tune λ_C dulu (0.3 → 0.1/0.2) untuk recover gap entity-level S2 vs S1, baru jalankan augmentation di atas winner. Bukan langsung augment dengan λ_C=0.3.

**SRL-NER — Approval & Deadline**
- ✅ S3 approved
- ⏰ **Deadline: 29 Mei 2026** (9 hari dari 2026-05-20)

**Arahan Baru**
- **Frekuensi entitas per period**: amati frekuensi kemunculan entitas (PERSON/EVENT/LOCATION) per periodisasi → justifikasi kontribusi
- **LLM untuk verb extraction**: lempar Sirah ke LLM → ekstrak **kata kerja / kata terkait event** → jadi Event entity tambahan (antisipasi karena Event saat ini terlalu sedikit, support 51 di test)

**Pertanyaan/Tambahan dari Teman**
- "NER itu sebenarnya sudah ada hubungan semantik antar entitas dalam satu kalimat" — confirmed: IndoBERT contextualized embedding sudah implicit belajar relasi posisional/sintaktik antar token. Tapi **untuk relasi eksplisit antar entitas**, pipeline saat ini pakai post-hoc proximity + pattern (`relation_extraction.py`) — bukan dari NER langsung. Future: bisa pakai LLM (sejalan dengan arahan Bu Diana di atas) atau Relation Extraction berbasis BERT (separate task).

**Pekerjaan yang Di-cancel**
- Tidak ada (semua existing scope tetap)

**Rencana Bimbingan Berikutnya**
- Pipeline harus sudah **running end-to-end** (dari awal sampai akhir)
- Graf sudah pakai **output SRL-NER** (bukan manual labelling)
- **Comparison report**: hasil SRL-NER vs manual labelling (jangan lupa dibedakan)
- Mulai **pembukuan per-Bab** sesuai update terbaru

**Catatan Bebas**
- Perbaiki periodisasi yang sekiranya perlu diperbaiki
- Quote: *"Semangat mengerjakan, bismillah selesai untuk skripsi nya ini"*

**Action Items (urut prioritas, total ~7-8 hari kerja, deadline 29 Mei)**
1. **Tune λ_C sweep** (0.1, 0.2, 0.3) di S2 SCL — pilih winner berdasarkan Seq F1 entity (~6-8 jam GPU)
2. **Run S3** (winner + Mention Replacement augmentation) (~3-4 jam GPU)
3. **Inference NER terbaik** ke seluruh `sirah_chunks_final.csv`
4. **Regenerate `nodes_v3.csv` + `edges_v3.csv`** dari output NER
5. **Comparison report**: SRL-NER vs manual labelling (diff Person/Event/Time/Location, coverage Tabuk dll)
6. **Centrality untuk node Event** (degree, betweenness, closeness, PageRank) — revisi tambahan Bu Diana
7. **Wordcloud per-komunitas** (13 Louvain) + interpretasi semantik
8. **Q-value interpretasi** + analisis "kenapa node X masuk komunitas Y" (sample 3-5 tokoh per komunitas)
9. **Analisis event-related** untuk 5 case study (event co-occur per period + relasi overlap)
10. **Frekuensi entitas per-period** (tabel: tiap entitas muncul di period mana, berapa kali)
11. **LLM verb extraction** → tambah Event entity (prompt template + run di sample chunks dulu, scale up kalau workable)
12. **Update CLAUDE.md** + mulai pembukuan Bab 4

> Propagasi: ringkasan masuk ke `bimbingan_template.md` (Section 0 status + Section 5 pertanyaan dengan jawaban), `../skenario/srl_ner.md` (update §S3 dengan tune λ_C dulu + deadline + Mention Replacement plan), `../../CLAUDE.md` (Catatan progres terakhir + tabel skenario aktif). Detail mentah tetap di `2026-05-16_outcome.md`.

---

## Putaran 6 — 2026-06-05 (Bimbingan Aktual)

> Bimbingan setelah deliverable 4 Juni. Next bimbingan: **11 Juni 2026**. Nada catatan dosen tegas ("jangan nunggu disuruh, ulik-ulik sendiri") — maksudnya minta mahasiswa lebih proaktif eksplorasi skenario, bukan menunggu instruksi.

**EDA & dataset**
- Tambahkan **EDA**: informasi dataset bagaimana, **tahapan pembentukan data**, **menampilkan data** (contoh).

**Penambahan skenario (proaktif — "jangan nunggu disuruh, ulik-ulik parameter, analisis hasilnya")**
- **Model lain**: cahya-bert, distil-bert (kalau ada versi Indonesia), atau model lain bila ada.
- **Handle imbalance** dibandingkan eksplisit: **weighted cross-entropy**, **CL (contrastive)**, **augmentasi**.
- **POS-tag**: uji apakah penggunaan POS-tag *sebelum* masuk model berpengaruh.
- Eksplorasi mandiri: variasi/ubah parameter → analisis bagaimana hasilnya.

**Bagian Analisis**
- Data yang rendah itu di **label/kelas apa**, dan **kenapa** terjadi seperti itu.

**Bagian Pembahasan (tidak hanya nilai → mengarah ke data)**
- Analisis NER: yang **performa rendah / misklasifikasi / tidak terdeteksi** itu **karena apa**.
- Cek: satu kalimat di ground truth ada **3 entitas tapi terdeteksi 2** (atau sebaliknya).
- Yang **misklasifikasi** → cari tahu **mengapa** hasilnya seperti itu.

**Tambahan informasi (klarifikasi teknik)**
- Teknik augmentasi: **coba parafrase**.
- **Augmentasi = menambah data secara riil**; **CL = mirip pembobotan** (bentuk representasi, bukan tambah data) → komplementer.
- Pertanyaan terbuka: **apakah bobot CL perlu menggunakan weighted** (per-kelas)?

**Status penanganan (per 2026-06-09)**
- ✅ EDA selesai → `data/result/analysis/eda/` (script `src/analysis/eda_ner_dataset.py`).
- ✅ Analisis kelas rendah + pembahasan error selesai → `data/result/analysis/error_analysis/` (script `src/pseudo_labelling/SRL-NER/error_analysis.py`).
- ✅ Deliverable siap-tampil → `2026-06-11.md` (5 bagian).
- 🔄 Skenario baru (weighted-CE / parafrase / POS-tag / model cahya & distilbert) = rancangan + run awal (GPU tersedia).

> Propagasi: deliverable di `2026-06-11.md`; ringkas progres ke `../../CLAUDE.md`. Temuan kunci: error NER didominasi **deteksi (miss/over)** bukan misklasifikasi tipe; sebagian FP EVENT/TIME = **inkonsistensi gold** (semi-auto keyed kapitalisasi `Perang` 40/40 vs `perang` 26/26); artefak OCR (tanda baca nempel, token kepecah) = sumber boundary error (LOCATION 45,7%).

---

## Putaran 7 — 2026-06-12 (Bimbingan Aktual)

> Fokus: interpretasi & validasi graf (SNA). Semua poin mengarah ke **Bab 4** (analisis jaringan), tidak menyentuh Bab 1. Catatan mentah + action item lengkap di `2026-06-12.md`. Semua analisis no-GPU (dari `nodes_v3.csv` + `edges_v3.csv`).

**Graf — Identifikasi komunitas**
- Jelaskan komunitas yang terbentuk itu kelompok apa (anggota + tema), bukan sekadar jumlahnya. (Sudah ada deteksi + wordcloud dari Putaran 5; tinggal dirapikan jadi narasi/tabel per komunitas.)

**Graf — Nama tanpa keterlibatan**
- Ada PERSON yang muncul sebagai node tapi tidak punya relasi keterlibatan (`INVOLVED_IN`). Cek: ketiadaan keterlibatan itu nyata atau gap ekstraksi. Logikanya, kalau seseorang disebut, mestinya terlibat dalam sesuatu.
- Action: cari node PERSON degree 0 / tanpa `INVOLVED_IN`, telusuri ke teks asal, simpulkan nyata vs artefak.

**Graf — Tokoh tak dikenal tiba-tiba sentral**
- Nama tak familiar yang muncul tinggi di centrality perlu dianalisis: kenapa muncul, nyata atau artefak.
- Sudah tervalidasi 1 kasus: **Amr Bin Umayyah** = artefak (over-ekstraksi `INVOLVED_IN` proximity). Action: generalisasi ke top-N centrality, cek silang ke teks/literatur Sirah.

**Benang merah:** "nama tanpa keterlibatan" (under) dan "tiba-tiba sentral" (over) sama-sama soal kualitas relasi `INVOLVED_IN` berbasis proximity. Jadikan satu alur pembahasan keterbatasan graf di Bab 4 (sejalan Putaran 6: pembahasan mengarah ke data).

**Status (per 2026-06-16):** baru dicatat, belum dikerjakan. Prioritas setelah Bab 1 dibukukan.

> Propagasi: detail di `2026-06-12.md`; ringkas ke `../../CLAUDE.md` + memory.
