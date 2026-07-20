# Protokol Koreksi Manual Anotasi (Bu Ratih #5)

> Menjawab: alasan koreksi manual, contoh sebelum/sesudah, pedoman, siapa yang mengoreksi +
> konsistensi, serta keterbatasan (anotator tunggal). Sumber nyata:
> `data/result/manual_labelling/gold_review/koreksi_gold_showcase.md` (+ `.csv`) dan
> `docs/anotasi_guideline.md`.

## Ruang lingkup

Artefak ini mendokumentasikan **koreksi manual sebagai bagian dari pembuatan gold**: pelabelan
**semi-otomatis** (kamus + regex) diikuti **satu pass review manual** untuk memperbaiki kualitas
anotasi. Fokusnya pada **cara gold dibentuk sebelum evaluasi** — sebagai bagian metodologi
anotasi. Ini menjawab Bu Ratih #5 dan tidak masuk ke pembahasan perbandingan F1.

## 1. Mengapa koreksi manual diperlukan

Pelabelan awal dilakukan **semi-otomatis** (`pre_labelling.py`: kamus entitas + pola regex).
Cara ini cepat tetapi menghasilkan kesalahan sistematis yang harus diperbaiki manual:

- **Entitas terlewat** — nama di luar kamus/pola tidak tertangkap.
- **Batas entitas salah** — sebagian token nama tertinggal (`B-`/`I-` tidak lengkap).
- **Salah tipe** — terutama nama yang bisa tempat **atau** peristiwa (LOCATION vs EVENT).
- **Entitas palsu** — pola menandai token yang sebenarnya bukan entitas (mis. judul kitab/rujukan hadis).
- **Artefak OCR** — apostrof hilang jadi spasi sehingga nama terpecah.

## 2. Jumlah & kategori koreksi (dari showcase)

`koreksi_gold_showcase.md` mengkategorikan **99 koreksi** representatif:

| Kategori | Jumlah |
|---|---:|
| Entitas kelewat | 29 |
| Batas entitas diperbaiki | 28 |
| Ambiguitas LOCATION vs EVENT | 27 |
| Salah anotasi (dibuang) | 9 |
| OCR apostrof (nama ter-split) | 4 |
| Salah tipe | 1 |
| Rantai nasab dipecah | 1 |

Di data, kolom `notes` pada `sirah_prelabelled.csv` menandai koreksi yang diterapkan:
**332 `gold_audit` + 95 `fix_time_boundary`**.

## 3. Contoh sebelum → sesudah (nyata)

| Kategori | Konteks | Sebelum | Sesudah |
|---|---|---|---|
| Entitas kelewat | "…membentang ke **India** dan Cina…" (000001-002) | `O` | `B-LOCATION` |
| Entitas kelewat | "…Al-Harits, **Az-Zubair**, Abu Thalib…" (000017-009) | `O` | `B-PERSON` |
| Batas entitas | "…tanggal 10 Agustus **610** M…" (000032-001) | `O` | `I-TIME` (bagian dari "610 M") |
| Batas entitas | "…di manaAbu **Bakar** dan Muhammad…" (000071-005) | `O` | `I-PERSON` (bagian dari "Abu Bakar") |
| LOCATION→EVENT | "…penjelasan dari Allah tentang **peperangan Badr**…" (000145-001) | `LOCATION` | `EVENT` |
| LOCATION→EVENT | "…setelah **penaklukkan Khaibar** pada tahun 7 H…" (000384-001) | `LOCATION` | `EVENT` |
| Entitas palsu (dibuang) | "…Shahih Al-Bukhari, bab **Ghazwah** Dzatu Qarad…" (000255-002) | `B-EVENT` | `O` (rujukan kitab, bukan peristiwa) |
| Entitas palsu (dibuang) | "…laksanakan puasa **Ramadhan** kalian…" (000359-005) | `B-TIME` | `O` (bulan ibadah, bukan penanda waktu peristiwa) |
| OCR apostrof | "**Mush ab**" → "Mush'ab"; "**Tha if**" → "Tha'if" | nama terpecah | tersambung |

## 4. Pelaksana, pedoman, dan konsistensi

- **Pelaksana:** koreksi dilakukan oleh **penulis** (anotator tunggal).
- **Pedoman:** mengacu pada **`docs/anotasi_guideline.md`** yang mengunci keputusan anotasi
  (skema 4 tipe + BIO, prinsip boundary: buang kata fungsi & tanda baca OCR, ambil span
  terpanjang/terspesifik seperti "Perang Badr" > "Badr").
- **Konsistensi dijaga** dengan menerapkan aturan pedoman yang **sama** ke seluruh korpus, dan
  perbaikan dilakukan di **satu sumber kebenaran** (`sirah_prelabelled.csv`, level span) lalu
  BIO diregenerasi otomatis — bukan menyunting BIO tangan.

## 5. Keterbatasan (WAJIB dinyatakan)

Anotasi & koreksi dilakukan oleh **satu orang** sehingga **tidak ada anotator kedua** dan
**tidak ada pengukuran kesepakatan antar-anotator** (mis. Cohen's kappa). Konsistensi hanya
dijaga melalui pedoman tertulis. Ini merupakan keterbatasan penelitian.

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Showcase koreksi (before→after) | `data/result/manual_labelling/gold_review/koreksi_gold_showcase.md` / `.csv` |
| Pedoman anotasi | `docs/anotasi_guideline.md` |
| Skrip pelabelan awal & koreksi | `src/manual_labelling/pre_labelling.py`, `apply_gold_audit.py`, `fix_time_boundaries.py` |
| Backup pra-koreksi | `sirah_prelabelled.csv.bak_before_apply`, `.bak_before_time` |
