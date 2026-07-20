# Referensi Dasar Konstruksi Knowledge Graph (Bu Nanik #7 & #9)

> Menjawab: tambahkan rujukan untuk **entity linking/normalization, relation extraction,
> pembentukan relasi berbasis co-occurrence, dan konstruksi KG dari teks**; jelaskan bagian yang
> diadopsi vs dirancang sendiri untuk Sirah.
>
> ⚠️ **Semua rujukan di bawah nyata & terindeks, dalam 5 tahun. Tetap cek penulis lengkap, volume,
> dan halaman ke sumber asli sebelum masuk Daftar Pustaka** (prinsip kejujuran sumber).

## 1. Konstruksi knowledge graph dari teks (pipeline umum)

- **Knowledge Graph Construction: Extraction, Learning, and Evaluation.** *Applied Sciences
  (MDPI)*, 15(7), 3727 (2025). — pipeline umum: ekstraksi entitas → ekstraksi relasi →
  integrasi/evaluasi. Dasar untuk kerangka NER → relasi → KG.
- **A Survey of Knowledge Graph Construction Using Machine Learning.** *CMES*, 139(1) (2024). —
  survei metode konstruksi KG berbasis machine learning.

**Adopsi vs rancangan sendiri:** proyek mengikuti kerangka umum (NER → normalisasi → relasi →
simpan di Neo4j sebagai *labeled property graph*), tetapi **pembentukan relasi memakai heuristik
co-occurrence/proximity** yang dirancang untuk korpus naratif Sirah, bukan model relasi terlatih.

## 2. Relation extraction

- **A Comprehensive Survey on Relation Extraction: Recent Advances and New Frontiers.** arXiv:
  2306.02051 (2023). — mencakup RE tingkat kalimat (supervised), distant supervision, open RE, dan
  RE berbasis graf tingkat dokumen.

**Batas klaim (penting, sesuai Bu Nanik #7):** relasi pada proyek ini adalah **induksi berbasis
heuristik kedekatan** (co-occurrence dalam satu kalimat / jendela < 200 karakter), **bukan**
*semantic relation extraction* penuh dengan model terlatih. Nyatakan ini eksplisit.

## 3. Entity linking / entity normalization

- **Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C. (2022). Neural Entity
  Linking: A Survey of Models Based on Deep Learning.** *Semantic Web Journal*. (SAGE;
  doi:10.3233/SW-222986). — arsitektur umum entity linking (candidate generation, mention-context
  encoding, entity ranking).

**Adopsi vs rancangan sendiri:** proyek **tidak** memakai neural entity linking. Yang dipakai =
**normalisasi alias ringan** (kesamaan string Jaro-Winkler + kamus manual + validasi manual). Jadi
rujukan ini dipakai sebagai **konteks tugas** (normalisasi/penyatuan variasi nama), sementara
metode proyek adalah versi **lebih sederhana** yang sesuai skala dataset — sebutkan perbedaan ini.

## 4. Pembentukan relasi berbasis co-occurrence

Untuk dasar heuristik co-occurrence + ambang 200 karakter, lihat artefak terpisah
`dasar_cooccurrence_200_karakter.md` (metode + dasar empiris + contoh benar/salah). Prinsip
co-occurrence/proximity sebagai sinyal relasi dibahas dalam survei konstruksi KG (§1) dan RE (§2)
di atas. Ambang 200 karakter tetap dibingkai sebagai **heuristik yang diadaptasi**, dibenarkan
secara empiris dari karakteristik kalimat/chunk korpus.

## 5. Ringkasan "diadopsi vs dimodifikasi untuk Sirah"

| Komponen | Diadopsi dari | Modifikasi untuk Sirah |
|---|---|---|
| NER (IndoBERT + self-training) | Ariyanto dkk. (2025) | orientasi peran semantik untuk 4 tipe entitas Sirah |
| Normalisasi alias | konsep entity normalization (Sevgili dkk. 2022) | disederhanakan: kamus manual + Jaro-Winkler + validasi manual |
| Pembentukan relasi | heuristik co-occurrence (survei KG/RE) | jendela satu-kalimat/<200 char + bobot bertingkat + relasi Sirah (INVOLVED_IN/OCCURRED_AT/OCCURRED_ON/PRECEDES) |
| Penyimpanan | labeled property graph Neo4j | skema simpul Person/Event/Location/Time + Period |

---

### Catatan
- Semua rujukan **dalam 5 tahun** (2022–2025) dan terindeks (MDPI/IEEE/SAGE/arXiv/CMES).
- Cek penulis lengkap & halaman sebelum ditulis. Rujukan hyperparameter (Ariyanto dkk. 2025) ada
  di `dasar_hyperparameter.md`; imbalance (Henning 2023; Nemoto dkk. 2024/2025) di
  `augmentasi_contoh_dan_distribusi.md`.
