# Perbandingan Alias Clustering — Punyaku vs. Thesis Rayssa

> Pendukung keputusan **Dosen-2 poin 6** (istilah "alias clustering" dipertanyakan). Rayssa
> Ravelia (`lama/TA-RayssaRavelia-5025211219 (Revised).pdf`, Subbab 3.1.7) adalah rujukan
> metodologi alias clustering-ku (kode `src/alias_clustering/alias_clustering.py` baris 28 bahkan
> mencatat *"threshold dinaikkan dari 0.85 Rayssa"*). Perbandingan ini menjelaskan kenapa
> proses **punyaku lebih tepat disebut "normalisasi alias"**, bukan "clustering" penuh seperti Rayssa.

---

## Ringkasan perbedaan

| Aspek | **Rayssa (cerita rakyat)** | **Punyaku (Sirah)** |
|---|---|---|
| Sifat proses | **Algoritma clustering inkremental** (bangun cluster, tiap entitas baru `c` dibandingkan ke cluster yang sudah ada `k`, buat cluster baru bila tak cocok) — punya diagram alir (Gambar 3.18–3.21) | **Kamus manual + safety-net string similarity.** Cluster kanonik sudah didefinisikan manual; Jaro-Winkler hanya menangkap variasi ejaan/typo OCR |
| Basis pengelompokan | POINTERS (peran: ibu/raja/puteri) + suffix similarity; jalur terpisah WithPointer vs WithoutPointer | Daftar kanonik→alias yang di-hardcode per label (PERSON/LOCATION/EVENT) |
| Metrik kemiripan | Jaccard **dan** Jaro-Winkler (threshold), + substring untuk token pendek | Jaro-Winkler saja, threshold **0,93** (dinaikkan dari 0,85 Rayssa karena nama Arab banyak mirip beda orang) |
| Cegah salah gabung | `EXCLUDE_PAIRS` (conflict meaning: sulung↔bungsu, tua↔muda) | `EXCLUDE_PAIRS` (beda orang: Sa'd bin Mu'adz↔Sa'd bin Ubadah, dll) + guard patronim `bin/binti`, compound `Abu/Ibnu`, rasio panjang |
| Komponen semantik | **Word Sense Mapping** (sinonim: ibu/bunda/mama → role "ibu") | Tidak ada WSM terpisah — pengetahuan sinonim (Rasulullah→Muhammad) di-encode langsung di kamus manual |
| **Evaluasi hasil** | **Ada** — Pairwise Precision / Recall / F1 terhadap labelled dataset | **Tidak ada** — hanya `alias_clusters.md` untuk review manual |
| Cakupan | Per cerita (`story_id`) | Global lintas dokumen (satu buku) |

---

## Implikasi untuk revisi (kenapa punyaku ≠ "clustering" Rayssa)

Penguji menilai istilah "clustering" menyiratkan **algoritma pembentukan cluster + penentuan
jumlah cluster + pemilihan hasil terbaik + metrik evaluasi cluster** (silhouette, SSE, dsb.).

- **Rayssa memenuhi sebagian besar syarat itu**: algoritma inkremental bernyawa + **evaluasi
  Pairwise P/R/F1**. Jadi Rayssa relatif aman memakai istilah "alias clustering".
- **Punyaku tidak**: intinya adalah **kamus normalisasi manual** yang sudah menetapkan bentuk
  kanonik, ditambah **Jaro-Winkler sebagai jaring pengaman** untuk variasi ejaan. Tidak ada
  algoritma pembentukan cluster otomatis, tidak ada penentuan jumlah cluster, dan **tidak ada
  metrik evaluasi cluster**.

**Rekomendasi (sesuai saran penguji):** ganti istilah menjadi
**"normalisasi alias berbasis Jaro-Winkler similarity dan validasi manual"** (atau
"pengelompokan alias berbasis kemiripan"). Ini lebih jujur menggambarkan yang benar-benar
dilakukan dan **menghindari pertanyaan lanjutan** soal silhouette score / SSE / pemilihan jumlah
cluster yang memang tidak dipakai.

> Jika ingin tetap memakai istilah "clustering", konsekuensinya harus **menambahkan evaluasi
> cluster** (mis. Pairwise Precision/Recall/F1 terhadap sampel alias berlabel — persis yang
> dilakukan Rayssa). Ini pekerjaan tambahan; opsi rename jauh lebih ringan dan tetap benar.

---

### Sumber

| Artefak | Berkas |
|---|---|
| Metodologi alias clustering Rayssa | `lama/TA-RayssaRavelia-5025211219 (Revised).pdf` Subbab 3.1.7 (hal. konten 115–127) |
| Implementasi alias clustering-ku | `src/alias_clustering/alias_clustering.py` |
| Output alias-ku | `data/result/alias_clustering/alias_map.json` + `alias_clusters.md` |
