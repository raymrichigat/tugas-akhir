# Kerangka Buku Tugas Akhir

> Outline untuk bimbingan 18 Juni 2026. Status tiap bagian ditandai. Mengikuti pedoman: tanpa em dash, layman, sitasi APA. Sumber konten = proposal, `CLAUDE.md`, docs skenario, dan hasil analisis di `data/result/`.
> Legenda status: ✅ draft jadi, 🟡 kerangka/sebagian, ⏳ nunggu data/konfirmasi.

## Halaman depan
Daftar Isi, Daftar Gambar, Daftar Tabel, Daftar Kode Sumber. (Otomatis dari template LaTeX.)

---

## BAB 1 PENDAHULUAN  ✅
Draft lengkap di `docs/bab1/pendahuluan.md`.
- 1.1 Latar Belakang
- 1.2 Rumusan Masalah (4 poin)
- 1.3 Batasan Masalah
- 1.4 Tujuan (4 poin, sejajar rumusan)
- 1.5 Manfaat

## BAB 2 TINJAUAN PUSTAKA  🟡
- **2.1 Hasil Penelitian Terdahulu** — tabel + ulasan penelitian terkait yang sudah ada di proposal: konstruksi *knowledge graph* (Zhong et al., 2024; Ren et al., 2024), KG dari dokumen historis berbasis LLM (Díaz et al., 2024), KG berbasis NER + Neo4j + Cypher (Xie et al., 2023; He et al., 2022), serta metode SRL semi-*supervised* (Ariyanto et al., 2025). Ditutup dengan posisi penelitian ini dibanding mereka.
- **2.2 Dasar Teori** — Sirah Nabawiyah sebagai sumber data; *Named-Entity Recognition*; *Semantic Role Labeling*; *iterative self-training* (semi-*supervised*); *knowledge graph*; *graph database* Neo4j dan kueri *Cypher*; *Social Network Analysis* (sentralitas dan deteksi komunitas).

## BAB 3 METODOLOGI  🟡 (sub-bab final nunggu konfirmasi teman)
- **3.1 Perancangan Sistem** — alur umum pipeline: PDF, OCR (PaddleOCR), pembersihan teks (*preprocessing*), pemotongan teks (*chunking*), pelabelan awal (semi-otomatis), pelatihan NER SRL dengan *iterative self-training*, penyatuan nama (*alias clustering*), ekstraksi relasi, pembangunan *knowledge graph* di Neo4j, dan analisis jaringan (SNA).
- Usulan sub-bab lanjutan (menunggu konfirmasi): 3.2 Penyiapan Dataset, 3.3 Skenario NER (S1 baseline, penanganan imbalance, contrastive, augmentasi, perbandingan backbone, POS-tag), 3.4 Pembentukan Knowledge Graph, 3.5 Analisis Jaringan. <!-- [PERIKSA] cocokkan dengan struktur dari teman -->

## BAB 4 HASIL DAN PEMBAHASAN  ⏳ (materi banyak sudah ada, perlu dirangkai)
- **4.x Eksplorasi Data (EDA)** — sudah ada di `data/result/analysis/eda/`.
- **4.x Hasil NER + skenario** — perbandingan S1 sampai S4 (baseline, weighted-CE, contrastive, augmentasi), **perbandingan backbone Grup B (indobert-cased, cahya-bert, distilbert, roberta)**, dan POS-tag (Grup C bila ada). Plus pembahasan error: error didominasi deteksi (miss/over) bukan salah tipe, dan inkonsistensi gold (kapitalisasi).  ⏳ butuh angka F1 Grup B.
- **4.x Perbandingan SRL-NER vs Manual Labelling** — sudah ada (`comparison_srl_vs_manual.md`).
- **4.x Knowledge Graph** — statistik nodes/edges v3, periodisasi.
- **4.x Analisis Jaringan (SNA)** — sentralitas (Person + Event), deteksi komunitas, dan **pembahasan keterbatasan graf** (revisi 12 Juni): node terisolasi/tanpa keterlibatan (R7.2), tokoh tak dikenal yang tiba-tiba sentral (R7.3, kasus Amr Bin Umayyah), identifikasi komunitas (R7.1).
- **4.x Studi Kasus Event** — Perang Badar dan beberapa event lain.

## BAB 5 KESIMPULAN DAN SARAN  🟡
- **5.1 Kesimpulan** — menjawab 4 rumusan masalah (penyiapan data, ekstraksi NER, pembangunan KG, evaluasi dan analisis).
- **5.2 Saran** — *future work*: ekstraksi relasi berbasis LLM untuk mengatasi keterbatasan proximity (over dan under edge), penambahan event, dan validasi centrality lebih lanjut.

---

## Halaman belakang
Daftar Pustaka, Lampiran, Biodata Penulis.

## Catatan untuk bimbingan 18 Juni
- Bagian yang sudah bisa ditunjukkan: Bab 1 (draft jadi) + kerangka Bab 2-5 ini + hasil Grup B (begitu angka diisi).
- Yang ditanyakan ke dosen: konfirmasi struktur Bab 3 dan Bab 4, dan cara menjawab revisi 12 Juni (R7.1-R7.3) di Bab 4.
