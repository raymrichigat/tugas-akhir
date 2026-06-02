# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.3328`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.333 → **moderate** — struktur komunitas ada tapi tidak clear-cut. Banyak Person punya koneksi ke beberapa komunitas, konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) berinteraksi luas lintas fase historis.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 6 dari 12 komunitas memenuhi syarat. 6 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 93 anggota, 161 evidence

![wordcloud 0](data/result/analysis/v3/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Ali bin Abu Thalib, Abu Bakar, Abu Jahal, Aisyah, Hamzah bin Abdul Muththalib, Ka'b bin Malik, Khadijah

**Top tokens:** perang(72), allah(31), ali(31), bakar(28), orang-orang(26), thalib(23), bulan(22), aisyah(20), binti(20), membunuh(19)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 1 — 60 anggota, 108 evidence

![wordcloud 1](data/result/analysis/v3/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Amr Bin Umayyah, Abdullah bin Ubay bin Salul, Umar bin Al-Khaththab, Utsman bin Affan, Abu Sufyan bin Harb, Abdullah bin Jahsy, Abu Azzah, Jabir bin Abdullah

**Top tokens:** perang(72), uhud(47), ummu(22), umar(21), orang(21), orang-orang(20), umair(17), abdullah(17), waktu(16), sa'id(16)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 2 — 55 anggota, 84 evidence

![wordcloud 2](data/result/analysis/v3/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Zaid bin Haritsah, Abu Lahab, Ikrimah bin Abu Jahal, Abu Hurairah, Abu Musa, Ibnu Ummi, Najasyi, Hakim Bin Hizam

**Top tokens:** perang(79), badr(56), umayyah(23), bulan(18), quraisy(17), makkah(14), peperangan(14), zaid(13), ali(12), abdurrahman(12)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 3 — 11 anggota, 13 evidence

![wordcloud 3](data/result/analysis/v3/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Abdullah Bin Atik, Sa'd bin Mu'adz, Ibnu Sa'd, Al-Mundzir Bin Uqbah Bin Amir, Huyai Bin Akhthab, Qais Bin Al-Aslat, Ka'B Bin Asad, Zainab Binti Jahsy

**Top tokens:** perang(11), ahzab(6), khandaq(5), sa'd(5), seorang(4), terjadi(4), sementara(4), bulan(4), dzul(4), abdullah(4)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 4 — 5 anggota, 5 evidence

![wordcloud 4](data/result/analysis/v3/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Amar bin Al-Hadhrami, Abdullah Bin Al-Mughirah, Utbah bin Rabi'ah, Al-Hakam Bin Kaisan, Amir Bin Al-Hadhrami

**Top tokens:** al-hadhrami(6), al-mughirah(4), amr(3), demi(3), allah(3), jahl(3), utsman(2), naufal(2), kedua(2), abdullah(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 5 — 3 anggota, 2 evidence

![wordcloud 5](data/result/analysis/v3/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Syurahbil Bin Hasyim, Amr Bin Abdi, Abu Zaid

**Top tokens:** bendera(4), beralih(4), tangan(4), al-abdari(4), dibunuh(4), quzman(4), zaid(2), amr(2), abdi(2), manaf(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.