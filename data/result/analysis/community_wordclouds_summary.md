# Community Wordcloud + Interpretasi — Knowledge Graph Sirah

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — wordcloud per komunitas Louvain + interpretasi semantik + arti Q-value.

## Tentang Q-value Louvain (Modularity)

**Q (recomputed, weighted) = `0.3170`**

Modularity Q (Newman & Girvan 2004) mengukur seberapa kuat struktur komunitas dibanding edge yang acak (random rewiring null model):
- **Q ≈ 0**     : tidak ada struktur komunitas (graf homogen / acak).
- **Q ≈ 0.3**   : struktur lemah-moderate. Komunitas terlihat tapi banyak inter-cluster edges.
- **Q ≈ 0.4-0.7**: struktur kuat — clear-cut komunitas.
- **Q > 0.7**   : sangat kuat (jarang di network natural).

Interpretasi untuk Sirah: Q=0.317 → **moderate** — struktur komunitas ada tapi tidak clear-cut. Banyak Person punya koneksi ke beberapa komunitas, konsisten dengan Sirah dimana sahabat (mis. Abu Bakar, Umar) berinteraksi luas lintas fase historis.

Untuk konteks: di S2 graf-pengujian sebelumnya, Louvain proper Q=0.327 vs Greedy Q=0.320 vs Girvan-Newman Q=0.024. Louvain proper > Girvan-Newman konsisten — algoritma divisive Girvan-Newman tidak cocok untuk dense graph.


## Komunitas yang Di-render Wordcloud

Filter: minimal 3 anggota. 8 dari 16 komunitas memenuhi syarat. 8 komunitas dengan <3 anggota di-skip (korpus evidence terlalu kecil).

### Komunitas 0 — 74 anggota, 123 evidence

![wordcloud 0](data/result/analysis/community_wordclouds/community_00.png)

**Top tokoh (PageRank):** Muhammad, Abu Jahal, Abu Sufyan bin Harb, Abu Azzah, Amr bin Umayyah, Abu Bakar, Aisyah, Abu Salamah bin Abdul Asad

**Top tokens:** perang(54), orang-orang(23), bakar(22), umayyah(21), uhud(21), jahal(20), pergi(20), tahun(18), bertanya(18), makkah(17)

**Interpretasi (proposal):** **Komunitas inti Rasulullah + sahabat utama + lawan Quraisy.** Mengandung Muhammad sebagai PageRank tertinggi global, ditambah sahabat dekat (Abu Bakar, Aisyah) dan tokoh musuh utama (Abu Jahal, Abu Sufyan). Token "perang/uhud/badr/makkah" dominan → komunitas ini menutupi **fase peperangan besar Madinah** (P8-P10) dan interaksi Mekkah-Madinah. Karena 74 anggota = 43% Person network, komunitas ini cenderung jadi "everyone-talks-to-Muhammad" supercluster — wajar dalam Sirah karena Nabi adalah hub semua relasi.

### Komunitas 1 — 39 anggota, 58 evidence

![wordcloud 1](data/result/analysis/community_wordclouds/community_01.png)

**Top tokoh (PageRank):** Utsman bin Affan, Zainab, Abu Musa, Abu Hurairah, Hamzah bin Abdul Muththalib, Hakim bin Hizam, Ibnu Ummi, Abu Lahab

**Top tokens:** perang(53), badr(36), bulan(17), quraisy(15), ali(14), fathimah(12), dinikahi(11), umayyah(10), peperangan(10), umair(10)

**Interpretasi (proposal):** **Cluster Perang Badr + jaringan keluarga Nabi.** Token "badr" + "perang" + "quraisy" dominan, dengan tokoh kunci Hamzah (paman Nabi yang syahid di Uhud), Utsman (sahabat senior, menantu Nabi), Zainab/Fathimah (putri Nabi). Mix antara faksi yang terlibat **Perang Badr (P8)** dengan **jalur keluarga inti** (token "dinikahi" + nama-nama putri Nabi). Hipotesis: edge KELUARGA + INVOLVED_IN Perang Badr secara koincidental me-cluster sahabat dan keluarga yang sama-sama muncul dalam kedua tipe relasi.

### Komunitas 2 — 26 anggota, 43 evidence

![wordcloud 2](data/result/analysis/community_wordclouds/community_02.png)

**Top tokoh (PageRank):** Ali bin Abu Thalib, Abdullah bin Ubay bin Salul, Umar bin Al-Khaththab, Zaid bin Haritsah, Mush'ab bin Umair, Abdullah bin Atik, Sa'd bin Mu'adz, Ka'b bin Asad

**Top tokens:** perang(33), ali(16), thalib(12), zaid(11), allah(10), masuk(9), bani(9), islam(8), hingga(8), bulan(8)

**Interpretasi (proposal):** **Cluster sahabat Madinah + ekspansi militer akhir.** Tokoh utama Ali bin Abu Thalib (PageRank tinggi), Umar (khalifah ke-2), Zaid bin Haritsah (komandan Mu'tah, P12), Mush'ab bin Umair (duta dakwah ke Madinah pra-Hijrah), dan Abdullah bin Ubay bin Salul (pemimpin munafiqin Madinah). Token "bani/islam/masuk" → tema **konsolidasi Madinah + interaksi dengan kabilah Yahudi/Arab Madinah** (Bani Quraizah, Bani Mushthaliq dll, P10-P12). Mix komandan ekspansi + kepala kabilah yang berinteraksi dengan negara Madinah.

### Komunitas 3 — 6 anggota, 5 evidence

![wordcloud 3](data/result/analysis/community_wordclouds/community_03.png)

**Top tokoh (PageRank):** Rifa'ah bin Abdul Mundzir, Ubadah bin Ash-Shamit bin Qais, Sa'd bin Ubadah bin Dulaim, Al-Mundzir bin Amr bin Khunais, Usaid bin Hudhair bin Sammak, Sa'd bin Khaitsamah bin Al-Harits

**Top tokens:** sa'd(8), amr(6), ubadah(5), khunais(5), usaid(5), hudhair(5), sammak(5), khaitsamah(5), al-harits(5), rifa'ah(5)

**Interpretasi (proposal):** **Cluster delegasi Anshar Baiat Aqabah Kubra (P5-P6, pra-Hijrah).** Semua tokoh adalah **Naqib (kepala suku) Anshar** yang dipilih Nabi sebagai perwakilan 12 kabilah Madinah saat Baiat Aqabah Kubra. Token didominasi nama orang (kebanyakan nasab "bin X bin Y") karena evidence text di komunitas ini berisi daftar Naqib. Cluster kecil tapi semantically very tight — represent satu peristiwa historis spesifik.

### Komunitas 4 — 4 anggota, 4 evidence

![wordcloud 4](data/result/analysis/community_wordclouds/community_04.png)

**Top tokoh (PageRank):** Ibrahim, Isma'il, Mudhadh bin Amr, Muhammad bin Abdullah bin Abdul Muththalib bin Hasyim

**Top tokens:** isma'il(6), memilih(6), ibrahim(4), allah(3), wanita(2), keluarga(2), lagi(2), hasyim(2), bersabda(2), sesungguhnya(2)

**Interpretasi (proposal):** **Cluster nasab Pra-Islam (P0-P1).** Nabi Ibrahim, Isma'il, dan tokoh latar belakang Arab pra-Hijrah (Mudhadh = leluhur Jurhum). Muhammad muncul di sini dengan nasab penuh (alias) karena edge KELUARGA dengan Hasyim/Abdul Muththalib — beda dengan nama kanonik di komunitas 0. Token "memilih/keluarga" → tema **silsilah + pemilihan keturunan** (Ibrahim → Isma'il → Quraisy → Muhammad).

### Komunitas 5 — 3 anggota, 3 evidence

![wordcloud 5](data/result/analysis/community_wordclouds/community_05.png)

**Top tokoh (PageRank):** Khadijah, Waraqah bin Naufal, Zaid bin Haritsah bin Syurahbil

**Top tokens:** khadijah(5), paman(3), membawa(2), pergi(2), menemui(2), waraqah(2), naufal(2), asad(2), abdul(2), uzza(2)

**Interpretasi (proposal):** **Cluster awal kenabian (P2 — Awal Kenabian).** Khadijah (istri pertama), Waraqah bin Naufal (paman Khadijah, ahli kitab yang konfirmasi kenabian), dan Zaid bin Haritsah dengan nasab penuh (anak angkat Nabi pra-bebas). Token "menemui/membawa" → narasi **Khadijah membawa Nabi menemui Waraqah** setelah wahyu pertama. Cluster kecil tapi penting historis — represent moment validation kenabian.

### Komunitas 6 — 3 anggota, 2 evidence

![wordcloud 6](data/result/analysis/community_wordclouds/community_06.png)

**Top tokoh (PageRank):** Abdullah bin Al-Mughirah, Amar bin Al-Hadhrami, Al-Hakam bin Kaisan

**Top tokens:** al-mughirah(4), al-hadhrami(2), utsman(2), naufal(2), kedua(2), abdullah(2), al-hakam(2), kaisan(2), budak(2), bani(2)

**Interpretasi (proposal):** **Cluster Sariyyah Nakhlah (P7, pre-Badr).** Amar bin Al-Hadhrami dibunuh di Sariyyah Nakhlah (Rajab 2H), Al-Hakam bin Kaisan ditawan, Abdullah bin Al-Mughirah/Naufal terkait. Cluster terisolasi karena Sariyyah Nakhlah peristiwa kecil tapi controversial (pembunuhan di bulan haram) — pemainnya jarang muncul di event lain.

### Komunitas 7 — 3 anggota, 2 evidence

![wordcloud 7](data/result/analysis/community_wordclouds/community_07.png)

**Top tokoh (PageRank):** Syurahbil bin Hasyim, Abu Zaid, Amr bin Abdi

**Top tokens:** bendera(4), beralih(4), tangan(4), al-abdari(4), dibunuh(4), quzman(4), zaid(2), amr(2), abdi(2), manaf(2)

**Interpretasi (proposal):** **Cluster pembawa bendera Quraisy di Perang Uhud (P9).** Token "bendera/beralih/tangan/dibunuh" + nama-nama Bani Abdari (klan Quraisy yang turun-temurun jadi pembawa bendera perang) → narasi terkenal "bendera Quraisy berpindah tangan dari satu Abdari ke Abdari lain karena setiap pembawa bendera dibunuh" di Perang Uhud. Cluster kecil tapi semantically sharp.


## Catatan Implementasi

- Stopwords: 100+ kata Indonesia umum + filler Sirah (bin, abu, ibnu, rasulullah, nabi, saw, hadits, riwayat).
- Tokenization: regex `\b[A-Za-z'\-]+\b` lower-cased, drop token <3 char.
- Evidence di-attribute ke komunitas source Person — kalau source bukan Person (mis. Event-Time OCCURRED_ON), evidence skip.
- Wordcloud max 80 words, layout deterministic seed 42.
- Interpretasi semantik per komunitas **wajib diisi manual** — bukan sesuatu yang bisa di-auto dari token frequency saja.