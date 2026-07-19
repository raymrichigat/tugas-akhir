# Dasar Empiris Ambang Co-occurrence 200 Karakter (Bu Nanik #6)

> Dari `analyze_cooccurrence_window.py`. Menjawab: angka 200 karakter didasarkan pada **analisis karakteristik kalimat/chunk korpus**, bukan angka sembarang.


## 1. Distribusi panjang kalimat (karakter)

- Jumlah kalimat: 10,457
- Median: **100** | rata-rata: 125 | persentil-75: 157 | persentil-90: 236
- Kalimat **≤ 200 karakter: 84.9%** (≤150: 72.8%)

Artinya jendela 200 karakter kira-kira menampung **satu kalimat penuh** untuk mayoritas kalimat (≈85%), plus margin kecil ke kalimat tetangga — sejalan dengan aturan utama *satu kalimat* yang dilengkapi jendela jarak.


## 2. Distribusi jarak antar-entitas berurutan (gap tepi, dalam chunk)

- Jumlah pasangan: 5,353 | median: **64** | rata-rata: 114 | persentil-90: 280

| Ambang | % pasangan di bawahnya | Bobot proximity |
|---:|---:|---:|
| < 50 char | 42.7% | 0,4 |
| < 100 char | 64.1% | 0,3 |
| < 200 char | 82.7% | 0,2 |

Jendela 200 karakter menangkap **mayoritas co-occurrence lokal** (82.7% pasangan), dan **tingkatan bobot (50/100/200) sejalan dengan kepadatan data** — makin dekat entitas, makin banyak & makin diberi bobot tinggi.


**Gambar:** `cooccurrence_window_dist.png` (histogram + garis ambang).

