# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.4266`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.427 → **kuat** — komunitas terbukti koheren.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 12 dari 21 komunitas memenuhi syarat. 9 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 93 anggota, 235 evidence

![wordcloud 0](data/result/analysis/v4_hybrid/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Ali bin Abu Thalib, Umar bin Al-Khaththab, Abu Bakar, Aisyah, Abu Sufyan bin Harb, Utsman bin Affan, Abu Azzah

**Top tokens:** perang(117), uhud(52), orang-orang(42), ummu(41), abdullah(38), ali(34), thalib(34), binti(33), bakar(32), allah(30)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 1 — 56 anggota, 135 evidence

![wordcloud 1](data/result/analysis/v4_hybrid/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Abdullah, Ma'ad, Fathimah, Yaqzhah, Makhzum, Imran, Amr, A'idz

**Top tokens:** namanya(314), bagian(168), murrah(88), amir(77), ilyas(76), mudhar(75), nizar(74), ma'ad(74), kedua(74), adnan(72)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 2 — 39 anggota, 78 evidence

![wordcloud 2](data/result/analysis/v4_hybrid/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Zaid bin Haritsah, Abu Lahab, Umayyah bin Khalaf, Zainab, Khunais bin Hudzafah, Hamzah bin Abdul Muththalib, Abdurrahman, Shafwan bin Umayyah

**Top tokens:** perang(62), badr(52), quraisy(20), umayyah(20), uhud(15), ali(15), khalaf(14), madinah(14), jubair(14), waktu(13)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 3 — 27 anggota, 41 evidence

![wordcloud 3](data/result/analysis/v4_hybrid/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Matausyalakh, Syalakh, Ibrahim, Isma'il, Adam, Akhnukh, Mahla'il, Idris

**Top tokens:** arfakhsyad(33), sam(33), nuh(33), lamk(33), matausyalakh(33), akhnukh(33), idris(31), yard(30), mahla'il(30), syalakh(25)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 4 — 21 anggota, 32 evidence

![wordcloud 4](data/result/analysis/v4_hybrid/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Abu Jahal, Abdullah bin Al-Mughirah, Umayyah, Hakim bin Hizam, Amr bin Al-Hadhrami, Abul Bakhtari bin Hisyam, Utbah bin Rabi'ah, Abu Thalib

**Top tokens:** umayyah(19), jahal(17), khalaf(16), hisyam(16), abul(12), al-harits(10), orang(9), perang(8), bakhtari(8), allah(8)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 5 — 9 anggota, 10 evidence

![wordcloud 5](data/result/analysis/v4_hybrid/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Mu'adz bin Amr, Musailamah, Bujair bin Zuhair, Ka'b bin Zuhair, Urwah bin Mas'ud, Syaima' binti Al-Harits, bin Amr bin Al-Jamuh, Mu'awwidz bin Ibnu Ishaq

**Top tokens:** perang(9), tha'if(7), amr(7), al-jamuh(6), rampasan(4), mu'adz(4), tahun(3), membunuh(3), harta(3), sepulang(3)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 6 — 7 anggota, 14 evidence

![wordcloud 6](data/result/analysis/v4_hybrid/community_wordclouds/community_06.png)

**Top tokoh (PageRank):** Abu Musa, Abu Hurairah, Amir bin Al-Akwa', Al-Miqdad bin Amr, Salamah bin Al-Akwa', Ja'far bin Abu Thalib, Maimunah binti Al-Harits Al-Amiriyah

**Top tokens:** perang(17), peperangan(11), khaibar(11), musa(10), al-asy(8), ari(8), bergabung(8), terjadi(7), bulan(6), jumadil(6)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 7 — 6 anggota, 5 evidence

![wordcloud 7](data/result/analysis/v4_hybrid/community_wordclouds/community_07.png)

**Top tokoh (PageRank):** Rifa'ah bin Abdul Mundzir, Usaid bin Hudhair bin Sammak, Sa'd bin Khaitsamah bin Al-Harits, Sa'd bin Ubadah bin Dulaim, Ubadah bin Ash-Shamit bin Qais, Al-Mundzir bin Amr bin Khunais

**Top tokens:** sa'd(8), amr(6), ubadah(5), khunais(5), usaid(5), hudhair(5), sammak(5), khaitsamah(5), al-harits(5), rifa'ah(5)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 8 — 3 anggota, 3 evidence

![wordcloud 8](data/result/analysis/v4_hybrid/community_wordclouds/community_08.png)

**Top tokoh (PageRank):** Al-Harits bin Abdi, Mu'adz bin Jabal, Nu'man bin Qail

**Top tokens:** raja-raja(6), surat(4), sepulang(3), perang(3), tabuk(3), datang(3), hamdan(3), yaman(2), himyar(2), al-harits(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 9 — 3 anggota, 2 evidence

![wordcloud 9](data/result/analysis/v4_hybrid/community_wordclouds/community_09.png)

**Top tokoh (PageRank):** Syurahbil bin Hasyim, Abu Zaid, Amr bin Abdi

**Top tokens:** bendera(4), beralih(4), tangan(4), al-abdari(4), dibunuh(4), quzman(4), zaid(2), amr(2), abdi(2), manaf(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 10 — 3 anggota, 3 evidence

![wordcloud 10](data/result/analysis/v4_hybrid/community_wordclouds/community_10.png)

**Top tokoh (PageRank):** Abu Rafi', Abdullah bin Unais, Abdullah bin Atik

**Top tokens:** abdullah(4), peristiwa(3), terjadi(3), rafi(3), atik(2), dzul(2), bersama-sama(2), membunuhnya(2), adapun(2), membunuh(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 11 — 3 anggota, 2 evidence

![wordcloud 11](data/result/analysis/v4_hybrid/community_wordclouds/community_11.png)

**Top tokoh (PageRank):** Tumadhir bin Al-Ashba', Sa'd bin Bakr, Ummu Abi Salamah

**Top tokens:** masuk(2), islam(2), abdurrahman(2), menikahi(2), tumadhir(2), al-ashba(2), berjuluk(2), ummu(2), abi(2), salamah(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.