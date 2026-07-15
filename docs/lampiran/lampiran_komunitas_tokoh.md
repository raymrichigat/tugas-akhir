# Lampiran — Data Komunitas Jaringan Tokoh

Lampiran ini merinci keanggotaan komunitas pada proyeksi jaringan antar tokoh (137 tokoh peserta peristiwa, ber-*scope*; lihat Subbab 4.5). Analisis komunitas dilaporkan pada Subbab 4.5.3 dengan modularitas **Q = 0,2831 (8 komunitas)** dan dibandingkan terhadap *greedy modularity* (*Adjusted Rand Index* 0,47). Dua kelompok terbesar (66 dan 47 anggota) memuat mayoritas tokoh; sisanya berupa kelompok kecil dan pasangan periferal yang terbentuk dari tokoh yang berbagi sedikit peristiwa spesifik. Data ini menjadi dasar Gambar 4.19 (sub-graf komunitas terbesar, `community = 0`, 66 anggota).

Skor sentralitas dan keanggotaan dihitung pada pipeline analisis (NetworkX, `src/analysis/sna_analysis.py --version v4_scoped`); sumber: `data/result/analysis/v4_scoped/sna_metrics.csv` (kolom `community`). ID komunitas diurutkan menurut ukuran menurun (0 = terbesar). Daftar tokoh di dalam tiap komunitas diurutkan menurut *PageRank* menurun.

Catatan: pada modularitas serendah Q = 0,2831 batas antar-kelompok melembut, sehingga label karakter di bawah bersifat interpretasi tokoh yang menonjol, bukan pemisahan faksi yang bersih (tokoh Muslim dan Quraisy dapat berada dalam satu komunitas karena sama-sama terhubung melalui peristiwa yang sama, mis. Perang Badr atau Uhud). Sejumlah nama juga merupakan perawi atau penulis sejarah (mis. Al-Baihaqi, Ibnul Jauzi, Al-Qurthubi, Ibnu Hajar) yang muncul karena disebut di teks, bukan pelaku peristiwa; ini keterbatasan ekstraksi yang sama seperti dibahas pada Subbab 4.5.2.

## Tabel L.1 — Ringkasan Komunitas

| Komunitas | Jumlah anggota | Tokoh menonjol | Karakter dominan |
|:---:|:---:|---|---|
| 0 | 66 | Muhammad, Ali bin Abu Thalib, Umar bin Al-Khaththab, Abu Bakar, Aisyah, Utsman bin Affan | Lingkar Muslim inti: Nabi, sahabat, dan keluarga dekat |
| 1 | 47 | Abu Jahal, Abu Sufyan bin Harb, Hamzah bin Abdul Muththalib, Zaid bin Haritsah, Abu Lahab | Komunitas campuran: oposisi Quraisy bercampur tokoh Muslim yang banyak terlibat peperangan |
| 2 | 7 | Musailamah, Urwah bin Mas'ud, Ka'b bin Zuhair | Kelompok kecil seputar diplomasi dan penyair |
| 3 | 3 | Tsabit bin Qais bin Syammas, Az-Zabir bin Batha, Iyas bin Mu'adz | Klaster periferal dari episode spesifik |
| 4 | 3 | Nu'man bin Qail, Al-Harits bin Abdi, Mu'adz bin Jabal | Klaster periferal dari episode spesifik |
| 5 | 3 | Abu Rafi', Abdullah bin Unais, Abdullah bin Atik | Klaster periferal dari episode spesifik |
| 6 | 2 | Kurz bin Jabir, Sa'd bin Abu Waqqash | Pasangan periferal |
| 7 | 2 | Usamah bin Zaid, Mirdas bin Nuhaik | Pasangan periferal |
| 8 | 2 | Nu'aim bin Ma'ud, Sulaith bin An-Nu'man | Pasangan periferal |
| 9 | 2 | Abu Bashir, Abu Jandal | Pasangan periferal |

Catatan: komunitas 2 sampai 9 berukuran kecil (2 sampai 7 anggota) dan umumnya terbentuk dari tokoh yang berbagi satu atau sedikit peristiwa spesifik, sehingga terpisah dari dua komunitas besar (0 dan 1). Sebagaimana dibahas pada Subbab 4.5.3, pada modularitas serendah ini sejumlah tokoh oposisi dan tokoh perang saling tercampur di dalam komunitas yang sama.

## Tabel L.2 — Keanggotaan Lengkap per Komunitas

| Komunitas | Jml | Anggota (urut *PageRank* menurun) |
|:---:|:---:|---|
| 0 | 66 | Muhammad; Ali bin Abu Thalib; Umar bin Al-Khaththab; Abu Bakar; Aisyah; Utsman bin Affan; Amr bin Umayyah; Hasan bin Ali; Abdullah bin Ubay bin Salul; Mush'ab bin Umair; Ibnu Hajar; Jabir bin Abdullah; Ka'b bin Al-Asyraf; Abu Salamah bin Abdul Asad; Abdullah bin Jahsy; Khalid bin Al-Walid; As'ad bin Zurarah; Qais bin Abu Hazim; Rafi' bin Khadij; Musa bin Uqbah; Samurah bin Jundab; Sulaith; Thalhah bin Ubaidillah; Ummu Aiman; Bakar Ash-Shidddiq; Ummu Sa'd; Ummu Salamah; As'ad bin Khuzaimah; Naf' bin Jubair; Urwah bin Az-Zubair; Al-Barra'; Abu Thalhah; Abu Dujanah; Al-Barra' bin Azib; Salamah bin Al-Akwa'; Jibril; Abu Musa; Abu Hurairah; Sa'd bin Mu'adz; Amir bin Al-Akwa'; Ja'far bin Abu Thalib; Al-Miqdad bin Amr; Khadijah; Zainab binti Jahsy; Huyai bin Akhthab; Al-Qurthubi; Al-Mundzir bin Uqbah bin Amir; Musa bin Imran; Al-Baihaqi; Ibnul Jauzi; Abu Ubaidah bin Al-Jarrah; Adam; Ka'b bin Malik; Sallam bin Abul Huqaiq; Ummu Misthah; Sa D bin Mu Adz; Ibnu Qami'ah; Ka'b bin Asad; Ashhamah bin Al-Aijar; Ibnu Ummi; Martsad bin Abu Martsad; Al-Miqdad bin Al-Aswad; Amir bin Fuhairah; Abdullah bin Uraiqith; Malik bin Auf; Imran bin Amr |
| 1 | 47 | Abu Jahal; Abu Sufyan bin Harb; Abu Azzah; Khunais bin Hudzafah; Zainab; Zaid bin Haritsah; Ummu Kultsum; Husain bin Ali; Abdurrahman; Hamzah bin Abdul Muththalib; Abu Lahab; Shafwan bin Umayyah; Thu'aimah bin Adi; Umayyah bin Khalaf; Bilal bin Rabah; Najasyi; An-Nadhr bin Al-Harits; Wahb bin Umair; Umair bin Wahb; Abdurrahman bin Auf; Ikrimah bin Abu Jahal; Amr bin Al-Ash; Abdullah bin Abu Bakar; Al-Aswad bin Al-Muththalib; Ali bin Umayyah; Ubadah bin Ash-Shamit; Zaid bin Ad-Dastinah; Uqbah bin Al-Harits; Ukkasyah bin Mihshan; Al-Abbas bin Abdul Muththalib; Jubair bin Muth'im; Siba bin Arfazhah; Abu Lubabah bin Abdul; Abul Ash; Abdullah bin Abbas; Ummul Fadhl; Wahsy bin Harb; Umayyah; Hakim bin Hizam; Abul Bakhtari bin Hisyam; Abu Thalib; Abu Shafwan; Budail bin Zarqa'; Abu Hudzaifah; Utbah bin Rabi'ah; Salamah bin Abu Salamah; Musafi' bin Abdi |
| 2 | 7 | Musailamah; Urwah bin Mas'ud; Ka'b bin Zuhair; Bujair bin Zuhair; Syaima' binti Al-Harits; Mu'adz bin Amr; Jabalah bin Al-Aiham |
| 3 | 3 | Tsabit bin Qais bin Syammas; Az-Zabir bin Batha; Iyas bin Mu'adz |
| 4 | 3 | Nu'man bin Qail; Al-Harits bin Abdi; Mu'adz bin Jabal |
| 5 | 3 | Abu Rafi'; Abdullah bin Unais; Abdullah bin Atik |
| 6 | 2 | Kurz bin Jabir; Sa'd bin Abu Waqqash |
| 7 | 2 | Usamah bin Zaid; Mirdas bin Nuhaik |
| 8 | 2 | Nu'aim bin Ma'ud; Sulaith bin An-Nu'man |
| 9 | 2 | Abu Bashir; Abu Jandal |

> Sumber data: `data/result/analysis/v4_scoped/sna_metrics.csv` (kolom `community`). Untuk menampilkannya di Neo4j Browser, jalankan `data/result/neo4j/set_community_v4.cypher` (menulis properti `community` per simpul) setelah `import_sirah_v4_hybrid.cypher`, lalu kueri `MATCH (p:Person) WHERE p.community IS NOT NULL RETURN p.community AS komunitas, count(*) AS jumlah, collect(p.name) AS anggota ORDER BY p.community;`. Neo4j hanya menampilkan; perhitungan komunitas dilakukan di Python.
