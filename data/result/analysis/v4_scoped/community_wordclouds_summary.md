# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.2607`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.261 → **moderate** — struktur komunitas ada tapi tidak clear-cut. Banyak Person punya koneksi ke beberapa komunitas, konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) berinteraksi luas lintas fase historis.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 6 dari 10 komunitas memenuhi syarat. 4 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 66 anggota, 174 evidence

![wordcloud 0](data/result/analysis/v4_scoped/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Ali bin Abu Thalib, Umar bin Al-Khaththab, Abu Bakar, Aisyah, Utsman bin Affan, Amr bin Umayyah, Hasan bin Ali

**Top tokens:** perang(118), uhud(41), orang-orang(38), ali(29), bulan(27), terjadi(25), waktu(25), bakar(25), allah(24), badr(23)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 1 — 47 anggota, 94 evidence

![wordcloud 1](data/result/analysis/v4_scoped/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Abu Jahal, Abu Sufyan bin Harb, Abu Azzah, Khunais bin Hudzafah, Zainab, Zaid bin Haritsah, Ummu Kultsum, Husain bin Ali

**Top tokens:** perang(69), badr(52), umayyah(36), quraisy(24), khalaf(21), makkah(19), orang(17), jahal(16), sufyan(16), bulan(15)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 2 — 7 anggota, 8 evidence

![wordcloud 2](data/result/analysis/v4_scoped/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Musailamah, Urwah bin Mas'ud, Ka'b bin Zuhair, Bujair bin Zuhair, Syaima' binti Al-Harits, Mu'adz bin Amr, Jabalah bin Al-Aiham

**Top tokens:** perang(9), tha'if(7), tahun(3), membunuh(3), sepulang(3), zuhair(3), romawi(2), yarmuk(2), masuk(2), islam(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 3 — 3 anggota, 3 evidence

![wordcloud 3](data/result/analysis/v4_scoped/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Tsabit bin Qais bin Syammas, Az-Zabir bin Batha, Iyas bin Mu'adz

**Top tokens:** tsabit(4), az-zabir(4), perang(3), bu'ats(3), yastrib(2), qaiz(2), meminta(2), batha(2), beserta(2), keluarga(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 4 — 3 anggota, 3 evidence

![wordcloud 4](data/result/analysis/v4_scoped/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Nu'man bin Qail, Al-Harits bin Abdi, Mu'adz bin Jabal

**Top tokens:** raja-raja(6), surat(4), sepulang(3), perang(3), tabuk(3), datang(3), hamdan(3), yaman(2), himyar(2), al-harits(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 5 — 3 anggota, 3 evidence

![wordcloud 5](data/result/analysis/v4_scoped/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Abu Rafi', Abdullah bin Unais, Abdullah bin Atik

**Top tokens:** abdullah(4), peristiwa(3), terjadi(3), rafi(3), atik(2), dzul(2), bersama-sama(2), membunuhnya(2), adapun(2), membunuh(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.