# Konvensi Warna Grafik (D1.8) — Konsistensi Warna ↔ Legenda

> Menjawab **Dosen-1 poin 8**. Tujuan: satu palet warna dipakai **konsisten di semua grafik**,
> dan **legenda selalu cocok** dengan warna batang/garis. Terapkan palet ini ke seluruh grafik
> hasil di buku (termasuk yang dibuat manual di Word/Excel).

## Palet per GRUP skenario (grafik perbandingan skenario)

| Grup | Isi | Warna | Hex |
|---|---|---|---|
| Grup A | Penanganan imbalance (Baseline, Weighted-CE, SCL, JSCL, Augmentation) | biru | `#3b6ea5` |
| Grup P | Modul POS-tag | oranye | `#e0843d` |
| Grup B | Model pra-latih lain (cahya, DistilBERT, IndoBERT-cased, RoBERTa) | hijau | `#4c9f70` |

> Skenario **pemenang (augmentation) tidak diberi warna berbeda** — warna batang tetap sesuai
> grupnya (Grup A biru). Penanda pemenang cukup **label angka di-bold + "(menang)"**, sehingga
> warna batang tetap konsisten dan legenda tidak pernah bertentangan dengan batang.

## Palet per KELAS entitas (grafik F1 per kelas)

| Kelas | Warna | Hex |
|---|---|---|
| PERSON | biru | `#3b6ea5` |
| LOCATION | hijau | `#4c9f70` |
| EVENT | merah | `#c0504d` |
| TIME | oranye | `#e0a458` |

## Palet SEBELUM / SESUDAH (grafik augmentasi)

| Kondisi | Warna | Hex |
|---|---|---|
| Sebelum | abu-abu | `#9e9e9e` |
| Sesudah | hijau | `#2e8b57` |

---

## Grafik yang sudah mengikuti konvensi (angka GT-terkoreksi + warna cocok)

| Grafik | Berkas | Skrip |
|---|---|---|
| Perbandingan F1 semua skenario | `bab4_viz/f1_skenario_semua_revisi.png` | `src/analysis/hasil_f1_skenario_revisi.py` |
| F1 agregat/per-kelas UC1–UC3 | `bab4_viz/f1_uc{1,2,3}_{agregat,perkelas}.png` | `src/analysis/bab4_visualizations.py` |
| Distribusi augmentasi | `bab4_viz/augmentasi_distribusi_revisi.png` | `src/analysis/augmentasi_distribusi_revisi.py` |

## Grafik USANG yang perlu diganti/di-update

| Grafik | Masalah |
|---|---|
| `error_analysis_done_newest/viz/f1_by_scenario.png` | angka **pra-GT-terkoreksi** (augment 0,946 ≠ 0,9756). Ganti dengan `f1_skenario_semua_revisi.png`. |

> **Catatan:** grafik hasil di repo umumnya sudah konsisten warna. Jika grafik yang dipermasalahkan
> penguji ada di **file Word/PPT** (bukan di repo), samakan warnanya mengikuti tabel palet di atas —
> khususnya pastikan entri legenda "augmentation" memakai warna yang sama dengan batangnya.
