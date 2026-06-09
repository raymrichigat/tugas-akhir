# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.3600`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.360 → **moderate** — struktur komunitas ada tapi tidak clear-cut. Banyak Person punya koneksi ke beberapa komunitas, konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) berinteraksi luas lintas fase historis.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 9 dari 15 komunitas memenuhi syarat. 6 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 64 anggota, 113 evidence

![wordcloud 0](data/result/analysis/v3/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Khadijah, Hamzah bin Abdul Muththalib, Jibril, Ka'b bin Malik, Ibnu Hajar, Abu Thalib, Ibnu Hisyam

**Top tokens:** perang(54), orang-orang(22), bulan(19), binti(18), terjadi(17), allah(16), khadijah(16), ka'b(15), peperangan(14), al-harits(14)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 1 — 45 anggota, 100 evidence

![wordcloud 1](data/result/analysis/v3/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Umar bin Al-Khaththab, Abu Sufyan bin Harb, Utsman bin Affan, Abu Azzah, Mush'ab bin Umair, Zaid bin Haritsah, Abdullah bin Ubay bin Salul, Amr Bin Umayyah

**Top tokens:** perang(71), uhud(32), orang(20), umar(18), abdullah(18), orang-orang(18), umair(15), ummu(15), waktu(13), mush'ab(13)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 2 — 41 anggota, 59 evidence

![wordcloud 2](data/result/analysis/v3/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Abu Lahab, Ikrimah bin Abu Jahal, Umayyah Bin Khalaf, Abdurrahman, Najasyi, Shafwan Bin Umayyah, Thu'Aimah Bin Adi, Bilal bin Rabah

**Top tokens:** perang(48), badr(41), umayyah(24), khalaf(14), quraisy(14), abdurrahman(12), jubair(12), makkah(11), membunuh(9), uhud(9)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 3 — 21 anggota, 44 evidence

![wordcloud 3](data/result/analysis/v3/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Ali bin Abu Thalib, Abu Bakar, Aisyah, Abu Jahal, Zainab, Tumadhir Bin Al-Ashba, Mu'Awwidz Bin Ibnu Ishaq, Abu Ayyub

**Top tokens:** bakar(21), ali(21), perang(20), aisyah(17), thalib(14), allah(12), amr(10), hijrah(9), demi(9), al-jamuh(9)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 4 — 7 anggota, 8 evidence

![wordcloud 4](data/result/analysis/v3/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Musailamah, Bujair Bin Zuhair, Ka'B Bin Zuhair, Urwah Bin Mas'Ud, Asy-Syaima' Binti Al-Harits, Mas'Ud Bin Amr, Jabalah Bin Al-Aiham

**Top tokens:** perang(9), tha'if(7), tahun(3), membunuh(3), sepulang(3), zuhair(3), romawi(2), yarmuk(2), masuk(2), islam(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 5 — 7 anggota, 7 evidence

![wordcloud 5](data/result/analysis/v3/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Abu Sa'id, Nasibah Binti Ka'B, Ummu Ammarah, Malik Bin Sinan, Sahl Bin Hanif, Qatadah Bin An-Nu'Man, Hathib bin Abi Balta'ah

**Top tokens:** sa'id(7), al-khudri(7), thalib(6), sahl(6), hanif(6), malik(6), sinan(6), ummu(6), ammarah(6), nasibah(6)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 6 — 5 anggota, 5 evidence

![wordcloud 6](data/result/analysis/v3/community_wordclouds/community_06.png)

**Top tokoh (PageRank):** Amar bin Al-Hadhrami, Abdullah Bin Al-Mughirah, Utbah bin Rabi'ah, Al-Hakam Bin Kaisan, Amir Bin Al-Hadhrami

**Top tokens:** al-hadhrami(6), al-mughirah(4), amr(3), demi(3), allah(3), jahl(3), utsman(2), naufal(2), kedua(2), abdullah(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 7 — 3 anggota, 2 evidence

![wordcloud 7](data/result/analysis/v3/community_wordclouds/community_07.png)

**Top tokoh (PageRank):** Syurahbil Bin Hasyim, Abu Zaid, Amr Bin Abdi

**Top tokens:** bendera(4), beralih(4), tangan(4), al-abdari(4), dibunuh(4), quzman(4), zaid(2), amr(2), abdi(2), manaf(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_

### Komunitas 8 — 3 anggota, 3 evidence

![wordcloud 8](data/result/analysis/v3/community_wordclouds/community_08.png)

**Top tokoh (PageRank):** Abu Rafi', Abdullah Bin Unais, Abdullah Bin Atik

**Top tokens:** abdullah(4), peristiwa(3), terjadi(3), rafi(3), atik(2), dzul(2), bersama-sama(2), membunuhnya(2), adapun(2), membunuh(2)

**Interpretasi (manual fill):** _[isi manual berdasarkan top tokens + tokoh utama — fase apa, tema apa, lokasi dominan]_


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.