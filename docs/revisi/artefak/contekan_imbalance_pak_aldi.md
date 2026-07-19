# Contekan: Menjelaskan Klaim Imbalance ke Pak Aldi (penguji, #6 & #7)

> Pegangan saat sidang revisi. Poin Pak Aldi: (#7) rasio 18:1 → 9:1 belum tentu seimbang;
> (#6) bedakan weighted-CE / SCL / augmentasi + tunjukkan distribusi.
> **Sikap: akui koreksi dengan percaya diri, lalu buktikan tekniknya tetap berhasil.**

---

## 1 kalimat (kalau cuma sempat sekali bicara)

> "Betul Pak, 17,4:1 menjadi 8,8:1 **belum seimbang** — dan saya sudah perbaiki klaimnya jadi
> *'mengurangi/menangani ketimpangan'*, bukan *'menyeimbangkan'*. Bukti augmentasi tetap
> menangani ketimpangan bukan dari rasio mencapai 1:1, tapi dari **naiknya F1 kelas minoritas**."

---

## Alur penjelasan (3 langkah)

**1. Akui dulu (jangan defensif).**
> "Pak Aldi benar. Menurunkan rasio tidak sama dengan menyeimbangkan. Di revisi, kalimat
> 'augmentasi menyeimbangkan kelas' saya ganti jadi 'augmentasi mengurangi/menangani ketimpangan
> kelas, meskipun distribusi antarkelas belum seimbang.'"

**2. Buktikan tekniknya tetap bekerja (INI KUNCI).**
> "Keberhasilan menangani ketimpangan saya ukur dari kinerja kelas minoritas, bukan dari
> tercapainya 1:1. Setelah augmentasi, F1 naik paling besar justru di kelas minoritas: TIME
> 0,80 → 0,90 dan EVENT 0,93 → 0,95, sementara mayoritas PERSON tetap terjaga (0,97 → 0,98).
> Model jadi lebih adil ke kelas jarang — itulah tujuan penanganan ketimpangan."

**3. Sandarkan ke literatur (kalau ditekan).**
> "Sejalan literatur: Henning dkk. (2023) menyebut augmentasi metode menangani ketimpangan yang
> sering lebih unggul dari resampling/modifikasi loss; Nemoto dkk. (2024) untuk NER menegaskan
> keberhasilan diukur dari naiknya kelas minoritas tanpa mengorbankan mayoritas — bukan rasio 1:1."

---

## Angka pegangan (F1 baseline → augmentasi, gold terkoreksi)

| Kelas | Baseline | Augmentasi | Δ |
|---|---:|---:|---:|
| PERSON (mayoritas) | 0,969 | 0,984 | +0,015 |
| LOCATION | 0,953 | 0,976 | +0,023 |
| EVENT (minoritas) | 0,934 | 0,954 | +0,020 |
| TIME (minoritas) | 0,798 | 0,904 | **+0,106** |

Rasio PERSON:EVENT: **17,4:1 → 8,8:1** (berkurang, belum 1:1).
Distribusi token sesudah: PERSON 8.311 / LOCATION 1.875 / TIME 1.107 / EVENT 943.

---

## Antisipasi pertanyaan Pak Aldi

| Kalau ditanya… | Jawab |
|---|---|
| "Berapa rasio yang disebut seimbang?" | "Tidak ada ambang baku, Pak. ≈1:1 baru benar-benar seimbang. Data saya 8,8:1 masih timpang, saya nyatakan apa adanya." |
| "Kalau masih timpang, buat apa augmentasi?" | "Tujuannya mengangkat kelas minoritas, dan itu tercapai — TIME naik +0,11. Rasio tidak harus 1:1 untuk itu." |
| "Kenapa PERSON (mayoritas) ikut naik?" | "Efek samping: kalimat minoritas hampir selalu memuat PERSON, jadi ikut terduplikasi. Tapi minoritas naik lebih tajam, jadi rasio tetap membaik." |
| "Beda augmentasi / weighted-CE / contrastive?" (#6) | "Augmentasi = menambah data; weighted-CE = mengubah bobot loss; contrastive = mengubah representasi. Augmentasi menang di data saya — Henning dkk. juga mencatat augmentasi sering paling efektif." |

---

## Yang HARUS dihindari

- ❌ "Data sudah seimbang / tidak lagi imbalance."
- ❌ Menyebut angka ambang "tidak imbalance" seolah dari jurnal (tidak ada yang baku).
- ✅ Cukup: "berkurang, belum seimbang, **tapi kelas minoritas terbukti terangkat**."

---

## Rujukan (≤5 tahun)

- Henning, S., Beluch, W., Fraser, A., & Friedrich, A. (2023). *A Survey of Methods for Addressing
  Class Imbalance in Deep-Learning Based NLP.* EACL 2023.
- Nemoto, S., Kitada, S., & Iyatomi, H. (2024). *Majority or Minority: Data Imbalance Learning
  Method for Named Entity Recognition.* arXiv:2401.11431 (juga IEEE Xplore 10816423).
