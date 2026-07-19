# Dasar Ambang Co-occurrence 200 Karakter + Contoh Relasi Benar/Salah (Bu Nanik #6)

> Menjawab: (a) dasar penggunaan satu kalimat / jarak < 200 karakter, (b) dasar angka 200,
> (c) contoh relasi benar dan salah, (d) apakah semua entitas dalam satu subbab otomatis
> terhubung. Angka dari `analyze_cooccurrence_window.py` (analisis korpus, tanpa model).

---

## 1. Bagaimana relasi ditentukan (metode)

Dua entitas dihubungkan bila berada dalam **konteks yang sama**, yang didefinisikan sebagai
(`relation_extraction.py`, fungsi `are_in_same_context`):

1. **Berada pada kalimat yang sama** (aturan utama), **ATAU**
2. **Jarak tepi-terdekatnya < 200 karakter** (pelengkap lintas-kalimat).

Kedekatan juga menentukan **bobot relasi** secara bertingkat (`period_mapping.py`):

| Jarak antar-entitas | Bobot proximity |
|---|---:|
| < 50 karakter | 0,4 |
| < 100 karakter | 0,3 |
| < 200 karakter | 0,2 |

Jadi **tidak** semua entitas dalam satu subbab otomatis terhubung — hanya yang **sekalimat atau
berjarak < 200 karakter**, dan pasangan yang lebih jauh diberi bobot lebih rendah.

## 2. Dasar angka 200 karakter (analisis karakteristik kalimat/chunk)

Angka 200 **bukan sembarang** — didasarkan pada karakteristik korpus:

**Panjang kalimat (10.457 kalimat):** median **100** karakter, persentil-75 = 157, persentil-90
= 236. **84,9% kalimat ≤ 200 karakter.** → Jendela 200 karakter kira-kira menampung **satu
kalimat penuh** bagi mayoritas kalimat, plus margin kecil ke kalimat tetangga. Ini konsisten
dengan aturan utama *satu kalimat* yang dilengkapi jendela jarak.

**Jarak antar-entitas berurutan (5.353 pasangan):** median **64** karakter; **82,7% pasangan
berjarak < 200 karakter.** Kepadatan per ambang:

| Ambang | % pasangan di bawahnya | Bobot |
|---:|---:|---:|
| < 50 char | 42,7% | 0,4 |
| < 100 char | 64,1% | 0,3 |
| < 200 char | 82,7% | 0,2 |

→ Jendela 200 karakter **menangkap mayoritas co-occurrence lokal**, dan tingkatan bobot
(50/100/200) **sejalan dengan kepadatan data** — makin dekat entitas, makin sering muncul dan
makin tinggi bobotnya. **Gambar:** `data/result/analysis/relation_window/cooccurrence_window_dist.png`.

**Framing untuk buku (jujur):** ambang 200 karakter adalah **heuristik yang diadaptasi** untuk
korpus ini, dibenarkan secara empiris oleh distribusi di atas. Pendekatan menghubungkan entitas
berdasarkan co-occurrence dalam satu kalimat atau jendela terbatas merupakan pendekatan yang
lazim pada ekstraksi relasi berbasis co-occurrence. *(Rujukan pelengkap opsional — verifikasi &
pastikan ≤5 tahun sebelum dipakai: survei ekstraksi relasi arXiv:2306.02051 (2023); survei
"Knowledge Graph Construction: Extraction, Learning, and Evaluation", Applied Sciences, MDPI
(2025). Cek penulis & detail sebelum menuliskan.)*

## 3. Contoh relasi BENAR (positif) — didukung konteks sekalimat

| Relasi | Bukti (evidence) | Halaman |
|---|---|---|
| Abdurrahman bin Auf —INVOLVED_IN→ Perang Badr | *"…Abdurrahman bin Auf menuturkan, 'Tatkala aku sedang berada di tengah barisan pada **Perang Badr**…'"* | 287–293 |
| Abdurrahman —INVOLVED_IN→ Perang Badr | *"…Pada **Perang Badr** itu **Abdurrahman** melewati Umayyah bin Khalaf…"* | 289–293 |

Tokoh dan peristiwa berada dalam **satu kalimat** dengan predikat keterlibatan yang jelas.

## 4. Contoh relasi SALAH (negatif) — tiga pola kegagalan proximity

| Relasi (salah) | Bukti | Mengapa salah |
|---|---|---|
| Abu Lahab —INVOLVED_IN→ Perang Badr | *"Saat Perang Badr, Abu Lahab **tidak ikut serta**…"* (hal 295–297) | **Negasi** — kalimat menyatakan ketidakterlibatan |
| Abdullah bin Abbas —INVOLVED_IN→ Perang Badr | *"…Ibnu Abbas berkata, 'Setelah Rasulullah memperoleh kemenangan… pada **Perang Badr**…'"* (hal 312–314) | **Perawi**, bukan pelaku — Ibnu Abbas hanya meriwayatkan |
| Abdullah bin Jahsy —INVOLVED_IN→ Perang Badr | *"Insiden yang dipicu satuan pasukan **Abdullah bin Jahsy**…"* (hal 256–265) | **Peristiwa berbeda** (ekspedisi Nakhlah) yang kebetulan dekat pembahasan Badr |

Ketiga kasus lolos aturan kedekatan tetapi **tidak benar secara semantis** — inilah keterbatasan
ekstraksi berbasis proximity (lihat juga `keterbatasan_negasi_relasi.md` untuk pola negasi, dan
hasil validitas semantis yang mengkuantifikasi kesalahan ini per fungsi).

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Logika relasi (window 200 + bobot) | `src/relation_extraction/relation_extraction.py`, `period_mapping.py` |
| Skrip analisis dasar empiris | `src/relation_extraction/analyze_cooccurrence_window.py` |
| Statistik + chart | `data/result/analysis/relation_window/` |
| Contoh benar/salah | `docs/revisi/artefak/validitas_semantis/F1_worksheet_validated.xlsx`, `keterbatasan_negasi_relasi.md` |
