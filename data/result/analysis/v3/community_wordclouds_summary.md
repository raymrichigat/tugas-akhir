# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.3365`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.336 → **moderate** — struktur komunitas ada tapi tidak clear-cut. Banyak Person punya koneksi ke beberapa komunitas, konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) berinteraksi luas lintas fase historis.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 8 dari 16 komunitas memenuhi syarat. 8 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 97 anggota, 158 evidence

![wordcloud 0](data/result/analysis/v3/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Abu Jahal, Abu Bakar, Aisyah, Ali bin Abu Thalib, Hamzah bin Abdul Muththalib, Umayyah Bin Khalaf, Khadijah

**Top tokens:** perang(71), allah(33), orang-orang(32), bakar(28), demi(22), umayyah(21), khalaf(21), makkah(20), aisyah(20), bulan(19)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 1 — 61 anggota, 99 evidence

![wordcloud 1](data/result/analysis/v3/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Ali Bin Abu Thalib, Umar Bin Al-Khaththab, Abu Lahab, Ikrimah Bin Abu Jahl, Abu Hurairah, Abu Musa, Ibnu Ummi, Najasyi

**Top tokens:** perang(90), badr(59), ali(27), thalib(21), umayyah(19), bulan(18), peperangan(18), quraisy(17), orang-orang(15), madinah(13)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 2 — 61 anggota, 97 evidence

![wordcloud 2](data/result/analysis/v3/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Amr Bin Umayyah, Abdullah Bin Ubay, Utsman Bin Affan, Abu Sufyan bin Harb, Umar bin Al-Khaththab, Abdullah Bin Jahsy, Abu Azzah, Mush'Ab Bin Umair

**Top tokens:** perang(68), uhud(49), ummu(20), orang(18), orang-orang(17), abdullah(16), al-barra(16), sa'id(15), al-khudri(15), waktu(14)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 3 — 13 anggota, 16 evidence

![wordcloud 3](data/result/analysis/v3/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Abdullah Bin Atik, Jabir bin Abdullah, Sa'D Bin Mu'Adz, Huyai Bin Akhthab, Ibnu Sa'D, Ka'B Bin Zaid Bin An-Najjar, Al-Mundzir Bin Uqbah Bin Amir, Ka'B Bin Asad

**Top tokens:** perang(10), khandaq(6), pasukan(6), ahzab(6), seorang(4), dzul(4), sa'd(4), abdullah(4), peristiwa(4), terjadi(4)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 4 — 5 anggota, 4 evidence

![wordcloud 4](data/result/analysis/v3/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Amr Bin Al-Hadhrami, Abdullah Bin Al-Mughirah, Utbah bin Rabi'ah, Amir Bin Al-Hadhrami, Al-Hakam Bin Kaisan

**Top tokens:** al-hadhrami(6), al-mughirah(4), amr(3), jahl(3), utsman(2), naufal(2), kedua(2), abdullah(2), al-hakam(2), kaisan(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 5 — 3 anggota, 3 evidence

![wordcloud 5](data/result/analysis/v3/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Mush'Ab, Abu Aziz Bin Umair, As'Ad Bin Zurarah

**Top tokens:** mush'ab(4), umair(4), aziz(3), peperangan(2), al-abdari(2), melewati(2), saudaranya(2), sebelah(2), tangannya(2), sedang(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 6 — 3 anggota, 2 evidence

![wordcloud 6](data/result/analysis/v3/community_wordclouds/community_06.png)

**Top tokoh (PageRank):** Syurahbil Bin Hasyim, Abu Zaid, Amr Bin Abdi

**Top tokens:** bendera(4), beralih(4), tangan(4), al-abdari(4), dibunuh(4), quzman(4), zaid(2), amr(2), abdi(2), manaf(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 7 — 3 anggota, 2 evidence

![wordcloud 7](data/result/analysis/v3/community_wordclouds/community_07.png)

**Top tokoh (PageRank):** Tumadhir Bin Al-Ashba, Ummu Abi Salamah, Sa'D Bin Bakr

**Top tokens:** masuk(2), islam(2), abdurrahman(2), menikahi(2), tumadhir(2), al-ashba(2), berjuluk(2), ummu(2), abi(2), salamah(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.