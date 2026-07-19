# Evaluasi Validitas Semantis Knowledge Graph (Bu Nanik #8 / Temuan #3)

> Menjawab revisi: pengujian fungsional **tidak cukup** hanya dengan "kueri berhasil dijalankan".
> Tiap fungsi F1–F6 harus dilaporkan **berapa jawaban yang benar-benar didukung teks sumber**.

## Rumus

> **Validitas semantis = (jumlah jawaban yang didukung sumber ÷ seluruh jawaban yang diperiksa) × 100%**

Unit yang diperiksa = **setiap baris jawaban yang dikembalikan kueri** (bukan entitas unik).
Untuk F5, penyebut = **21 jalur** yang dikembalikan (bukan 15 lokasi unik) — sesuai Temuan #3.

## Enam pertanyaan kompetensi (dari Tabel 3.21)

| Fungsi | Pertanyaan | Pola relasi | Jumlah jawaban |
|---|---|---|---:|
| F1 | Siapa saja yang terlibat dalam Perang Badar? | (Person)-[INVOLVED_IN]->(Event) | 58 |
| F2 | Peristiwa apa saja yang terjadi di Madinah? | (Event)-[OCCURRED_AT]->(Location) | 10 |
| F3 | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah? | (Event)-[OCCURRED_ON]->(Time) | 4 |
| F4 | Peristiwa apa saja yang melibatkan Abu Bakar? | (Person)-[INVOLVED_IN]->(Event) | 4 |
| F5 | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | (Person)-[INVOLVED_IN]->(Event)-[OCCURRED_AT]->(Location) | 21 |
| F6 | Urutan kronologis antar peristiwa | (Event)-[PRECEDES]->(Event) | 17 |

## Status penilaian

| Fungsi | Valid | Total | Validitas | Status |
|---|---:|---:|---:|---|
| F1 | ? | 58 | ? | ⬜ **perlu dinilai** → `F1_worksheet.csv` |
| F2 | ? | 10 | ? | ⬜ **perlu dinilai** → `F2_worksheet.csv` |
| F3 | 3 | 4 | 75,00% | ✅ sudah (di buku) |
| F4 | ? | 4 | ? | ⬜ **perlu dinilai** → `F4_worksheet.csv` |
| F5 | 3 | 21 | 14,29% | ✅ sudah (di buku) |
| F6 | 14 | 17 | 82,35% | ✅ sudah (di buku) |

## Cara mengisi worksheet (F1, F2, F4)

1. Buka `F1_worksheet.csv` / `F2_worksheet.csv` / `F4_worksheet.csv` di Excel.
2. Baca kolom **`evidence`** (kalimat sumber) + **`halaman`**. Kalau perlu, buka buku Mubarakfuri di halaman itu.
3. Isi kolom **`valid_(1=ya/0=tidak)`**:
   - **1** = teks sumber benar-benar mendukung relasi (mis. tokoh memang terlibat Perang Badar).
   - **0** = tidak didukung (mis. cuma disebut berdekatan, subjek beda, atau justru **negasi**).
4. Kolom **`kandidat_masalah`** = petunjuk otomatis (BUKAN keputusan). Ditandai bila evidence memuat kata negasi ("tidak/belum/bukan/tanpa") atau tidak menyebut kata kunci (Badr/Madinah/Bakar). Tetap **kamu** yang memutuskan.
5. Kolom `catatan` opsional (alasan singkat, mis. "tidak ikut serta").

> ⚠️ **Penilaian ini keputusan manusia.** Skrip hanya menyiapkan bukti + menandai kandidat; kebenaran historis Sirah tidak boleh diputuskan otomatis.

## Setelah selesai mengisi

Jalankan penghitung untuk merangkum semua fungsi jadi tabel Bab 4:

```
venv/Scripts/python.exe src/analysis/hitung_validitas_semantis.py
```

Output: `hasil_validitas_semantis.md` (tabel per fungsi + rata-rata keseluruhan, siap tempel ke Bab 4).
