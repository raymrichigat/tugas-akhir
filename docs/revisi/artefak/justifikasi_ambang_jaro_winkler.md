# Justifikasi Empiris Ambang Jaro-Winkler 0,93 (Bu Ratih #7)

> Menjawab revisi: ambang **0,93** pada normalisasi alias perlu **alasan empiris**, bukan
> sekadar "dinaikkan dari 0,85". Sumber angka: `src/alias_clustering/jw_threshold_sweep.py`
> → `data/result/alias_clustering/jw_threshold_sweep/`.

## Metode

Ambang diuji pada rentang **0,85–0,95** pada tahap *safety-net* Jaro-Winkler, dengan guard
yang sama (compound-prefix Abu/Ibnu, kesamaan patronimik setelah "bin/binti", rasio panjang
nama, dan daftar `exclude-pairs`). Untuk tiap ambang dihitung berapa pasangan nama yang akan
digabung sebagai satu entitas.

## Hasil: jumlah pasangan tergabung per ambang

| Ambang | Pasangan tergabung | Keterangan |
|---:|---:|---|
| 0,85 | 359 | default Rayssa |
| 0,88 | 183 | |
| 0,90 | 137 | |
| 0,92 | 115 | |
| **0,93** | **103** | **dipakai** |
| 0,95 | 90 | terlalu ketat |

Menurunkan ambang ke 0,85 menambah **256 pasangan** dibanding 0,93.

## Temuan kunci: pasangan tambahan itu hampir semuanya BEDA entitas

Dari 256 pasangan borderline (0,85 ≤ JW < 0,93), **255 pasangan bukan variasi nama yang sama**
(hanya 1 yang tercatat sebagai variasi sah). Artinya menurunkan ambang **tidak menambah
normalisasi yang benar**, justru menimbulkan penggabungan keliru. Contoh pasangan yang akan
**salah digabung** bila ambang diturunkan ke 0,85:

| Nama A | Nama B | JW | Keterangan |
|---|---|---:|---|
| Umayyah bin Zaid | Usamah bin Zaid | 0,921 | dua orang berbeda |
| Perang Tabuk | Perang Yarmuk | 0,920 | dua peristiwa berbeda |
| Perang Khaibar | Perang Khunain | 0,914 | dua peristiwa berbeda |
| Perang Bani Qainuqa' | Perang Bani Quraizhah | 0,914 | dua kabilah/peristiwa berbeda |
| Perang Badr Kubra | Perang Badr Ula | 0,926 | Badr besar vs Badr kecil |
| Taimi bin Murrah | Tamim bin Murrah | 0,922 | dua nasab berbeda |
| Perang Buwath | Perang Mu'tah | 0,920 | dua peristiwa berbeda |

## Mengapa 0,93, bukan lebih rendah atau lebih tinggi

- **Lebih rendah (0,85–0,92):** memasukkan ratusan pasangan beda-entitas di atas → merusak graf
  (satu simpul salah menyatukan dua tokoh/peristiwa). Presisi turun tajam.
- **0,93:** menyisakan penggabungan JW pada tingkat kemiripan yang praktis hanya muncul dari
  **variasi ejaan / artefak OCR** (mis. huruf hilang atau tertukar), bukan nama berbeda.
- **Lebih tinggi (0,95):** mulai membuang variasi ejaan yang sah.

## Pembagian peran: manual cluster vs Jaro-Winkler (saling melengkapi)

Ambang JW sengaja dibuat **konservatif (mengutamakan presisi)** karena variasi nama yang
*mirip makna tetapi jauh secara ejaan* sudah ditangani daftar **manual cluster**, bukan JW.
Contoh: **"Perang Ahzab" = "Perang Khandaq"** (JW hanya 0,879, tidak akan tergabung oleh ambang
berapa pun yang wajar) — ini disatukan lewat manual cluster. Jadi JW cukup menangani variasi
ejaan berkemiripan tinggi, sementara sinonim/nama-alternatif ditangani manual.

## Keterbatasan (jujur)

Ambang 0,93 juga **melewatkan beberapa variasi sah** yang skornya tepat di bawah ambang, mis.
"Utbah bin Rabi'ah" vs "Uthbah bin Rabi'" (0,926) dan "Salaman" vs "Salman" (0,928). Ini
konsekuensi memilih **presisi di atas recall** — untuk knowledge graph, penggabungan keliru
(dua entitas jadi satu simpul) lebih merugikan daripada satu variasi yang terlewat, sehingga
ambang tinggi lebih aman. Variasi penting yang terlewat dapat ditambahkan manual ke daftar
cluster bila ditemukan saat review.

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Skrip sweep | `src/alias_clustering/jw_threshold_sweep.py` |
| Semua pasangan lolos-guard + skor JW | `data/result/alias_clustering/jw_threshold_sweep/jw_sweep_pairs.csv` |
| Tabel + daftar borderline | `data/result/alias_clustering/jw_threshold_sweep/jw_threshold_sweep.md` |
