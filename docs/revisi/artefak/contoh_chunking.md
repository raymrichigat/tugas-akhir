# Contoh Chunking (Sebelum & Sesudah) + Parameter (Bu Ratih #4)

> Menjawab: contoh teks sebelum/sesudah chunking, alasan panjang chunk, overlap, penanganan
> kalimat terpotong, dan pemeliharaan metadata. Sumber logika: `src/chunking/chunking_and_seed.py`
> (`split_chunks_with_overlap`). Contoh dari teks Sirah nyata yang masuk pipeline.

## Parameter chunking

| Parameter | Nilai | Alasan |
|---|---|---|
| Batas panjang | **≤ 1500 karakter** per chunk | cukup memuat beberapa kalimat berkonteks, tetapi tetap di bawah batas 512 token IndoBERT setelah tokenisasi |
| Satuan pemotongan | **kalimat** (regex `.!?`) | batas kalimat dijaga — **tidak pernah memotong di tengah kalimat** |
| Overlap | **1 kalimat** (kalimat terakhir chunk sebelumnya diulang di awal chunk berikutnya) | menjaga kontinuitas konteks antar-chunk agar entitas/relasi di batas chunk tidak hilang |
| Ruang lingkup | dipotong **per sub-bab** | metadata bab/sub-bab/halaman tetap konsisten dalam satu chunk |
| Kalimat tunggal > 1500 char | dimasukkan apa adanya | kasus langka (mis. daftar nasab panjang tanpa titik) |

**Metadata yang dipertahankan** tiap chunk: `chunk_id` (doc_id 6 digit - index 3 digit), `judul_bab`,
`judul_sub_bab`, `halaman`, `teks_chunk`.

## Contoh nyata — sub-bab "Kekuasaan di Berbagai Penjuru Arab" (Bab: Kekuasaan dan Imarah di Kalangan Bangsa Arab, hal 53–54)

Sub-bab ini melebihi 1500 karakter sehingga dipecah menjadi **2 chunk** (1182 + 1158 karakter).

**Sebelum (satu teks sub-bab, > 1500 karakter):**

> "…seperti layaknya seorang pemimpin diktator yang perkasa. **Sehingga adakalanya jika seorang
> pemimpin murka, sekian ribu mata pedang akan ikut berbicara tanpa perlu bertanya apa yang membuat
> pemimpin kabilah itu murka.** Hanya saja persaingan untuk mendapatkan kursi pemimpin di antara
> mereka…"

**Sesudah (dipecah, dengan overlap 1 kalimat):**

| chunk_id | Potongan teks |
|---|---|
| `000008-001` | "…seperti layaknya seorang pemimpin diktator yang perkasa. **Sehingga adakalanya jika seorang pemimpin murka, sekian ribu mata pedang akan ikut berbicara tanpa perlu bertanya apa yang membuat pemimpin kabilah itu murka.**" ← berakhir di sini |
| `000008-002` | "**Sehingga adakalanya jika seorang pemimpin murka, sekian ribu mata pedang akan ikut berbicara tanpa perlu bertanya apa yang membuat pemimpin kabilah itu murka.** Hanya saja persaingan untuk mendapatkan kursi pemimpin di antara mereka…" ← dimulai dari kalimat overlap |

Kalimat **bercetak tebal** adalah **overlap**: kalimat terakhir `000008-001` diulang sebagai
kalimat pertama `000008-002`. Dengan begitu, batas antar-chunk tidak memutus konteks, dan tidak ada
kalimat yang terpotong separuh.

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Logika chunking | `src/chunking/chunking_and_seed.py` (`split_chunks_with_overlap`, `MAX_CHARS=1500`) |
| Hasil chunk | `data/result/chunking_result/sirah_chunks_final.csv` (contoh: `000008-001`, `000008-002`) |
