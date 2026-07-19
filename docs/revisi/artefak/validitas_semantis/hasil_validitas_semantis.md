# Hasil Evaluasi Validitas Semantis Knowledge Graph

## Tabel 4.28 (revisi) — Ringkasan Hasil Pengujian Fungsional Knowledge Graph

| Fungsi | Pertanyaan | Jumlah diperiksa | Valid | Tidak valid | Kesesuaian semantis | Terlacak |
|---|---|---:|---:|---:|---:|---:|
| F1 | Siapa saja yang terlibat dalam Perang Badar? | 58 relasi | 14 | 44 | 24.14% | 100% |
| F2 | Peristiwa apa saja yang terjadi di Madinah? | 10 relasi | 2 | 8 | 20.00% | 100% |
| F3 | Peristiwa apa yang terjadi pada tahun ke-2 Hijriah? | 4 relasi | 3 | 1 | 75.00% | 100% |
| F4 | Peristiwa apa saja yang melibatkan Abu Bakar? | 4 relasi | 0 | 4 | 0.00% | 100% |
| F5 | Di mana lokasi peristiwa yang melibatkan Umar bin Khattab? | 21 jalur (15 lokasi unik) | 3 | 18 | 14.29% | 100% |
| F6 | Urutan kronologis antar peristiwa (PRECEDES) | 17 relasi | 14 | 3 | 82.35% | 100% |
| **Total** | — | **114** | **36** | **78** | **31.58%** | **100%** |

Validitas/kesesuaian semantis = (jawaban didukung teks sumber ÷ seluruh jawaban diperiksa) × 100%. Unit F5 = 21 jalur Person–Event–Location (mencakup 15 lokasi unik); satu jalur valid hanya bila kedua relasinya didukung sumber.

**Ringkasan:** keberhasilan operasional 100% (seluruh 6 kueri jalan & memberi jawaban) dan keterlacakan 100% (semua jawaban punya evidence + halaman), tetapi kesesuaian semantis berbeda tiap fungsi — tertinggi 82.35% pada F6, terendah 0.00% pada F4, rata-rata mikro 31.58%. Kemampuan graf menjalankan kueri tidak otomatis menjamin ketepatan seluruh jawaban.
