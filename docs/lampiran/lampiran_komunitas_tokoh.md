# Lampiran — Data Komunitas Jaringan Tokoh (Louvain)

Lampiran ini merinci hasil deteksi komunitas dengan algoritma Louvain pada proyeksi jaringan antar tokoh (137 tokoh peserta peristiwa, ber-*scope*, lihat Subbab 4.5). Modularitas Q = 0,2831 dengan 8 komunitas bermakna ditambah beberapa pasangan periferal. Data ini menjadi dasar Gambar 4.18 (sub-graf komunitas terbesar) dan pembahasan pada Subbab 4.5.3.

Skor sentralitas dan keanggotaan komunitas dihitung pada pipeline analisis (NetworkX, `src/analysis/sna_analysis.py --version v4_scoped`); sumber: `data/result/analysis/v4_scoped/sna_metrics.csv`.

## Tabel L.1 — Ringkasan Komunitas

| Komunitas | Jumlah anggota | Tokoh utama (urut *PageRank*) | Karakter |
|:---:|:---:|---|---|
| 0 | 66 | Muhammad, Ali bin Abu Thalib, Umar bin Al-Khaththab, Abu Bakar, Aisyah, Utsman bin Affan | Lingkar Muslim inti: Nabi, Khulafa Rasyidin, keluarga, dan banyak sahabat; sebagian tokoh oposisi ikut tercampur karena modularitas rendah |
| 1 | 47 | Abu Jahal, Abu Sufyan bin Harb, Hamzah bin Abdul Muththalib, Zaid bin Haritsah, Abu Lahab | Poros oposisi Quraisy bercampur tokoh Muslim yang aktif pada peperangan besar |
| 2 | 7 | Musailamah, Urwah bin Mas'ud, Ka'b bin Zuhair | Kelompok kecil seputar diplomasi dan penyair |
| 3 | 3 | Tsabit bin Qais bin Syammas, Az-Zabir bin Batha, Iyas bin Mu'adz | Klaster periferal dari episode spesifik |
| 4 | 3 | Nu'man bin Qail, Al-Harits bin Abdi, Mu'adz bin Jabal | Klaster periferal dari episode spesifik |
| 5 | 3 | Abu Rafi', Abdullah bin Unais, Abdullah bin Atik | Klaster periferal dari episode spesifik |
| 6 | 2 | Kurz bin Jabir, Sa'd bin Abu Waqqash | Pasangan periferal |
| 7 | 2 | Usamah bin Zaid, Mirdas bin Nuhaik | Pasangan periferal |
| 8 | 2 | Nu'aim bin Ma'ud, Sulaith bin An-Nu'man | Pasangan periferal |
| 9 | 2 | Abu Bashir, Abu Jandal | Pasangan periferal |

Catatan: komunitas 2 sampai 9 berukuran kecil (2 sampai 7 anggota) dan umumnya terbentuk dari tokoh yang berbagi satu atau sedikit peristiwa spesifik, sehingga terpisah dari dua komunitas besar. Pada modularitas serendah 0,2831, batas antar-kelompok besar (0 dan 1) melembut sehingga sejumlah tokoh oposisi dan tokoh perang saling tercampur, sebagaimana dibahas pada Subbab 4.5.3.

## Tabel L.2 — Keanggotaan Lengkap per Komunitas

**Komunitas 0 (66 anggota):** Muhammad, Ali bin Abu Thalib, Umar bin Al-Khaththab, Abu Bakar, Aisyah, Utsman bin Affan, Amr bin Umayyah, Hasan bin Ali, Abdullah bin Ubay bin Salul, Mush'ab bin Umair, Ibnu Hajar, Jabir bin Abdullah, Ka'b bin Al-Asyraf, Abu Salamah bin Abdul Asad, Abdullah bin Jahsy, Khalid bin Al-Walid, As'ad bin Zurarah, Qais bin Abu Hazim, Rafi' bin Khadij, Musa bin Uqbah, Samurah bin Jundab, Sulaith, Thalhah bin Ubaidillah, Ummu Aiman, Bakar Ash-Shidddiq, Ummu Sa'd, Ummu Salamah, As'ad bin Khuzaimah, Naf' bin Jubair, Urwah bin Az-Zubair, Al-Barra', Abu Thalhah, Abu Dujanah, Al-Barra' bin Azib, Salamah bin Al-Akwa', Jibril, Abu Musa, Abu Hurairah, Sa'd bin Mu'adz, Amir bin Al-Akwa', Ja'far bin Abu Thalib, Al-Miqdad bin Amr, Khadijah, Zainab binti Jahsy, Huyai bin Akhthab, Al-Qurthubi, Al-Mundzir bin Uqbah bin Amir, Musa bin Imran, Al-Baihaqi, Ibnul Jauzi, Abu Ubaidah bin Al-Jarrah, Adam, Ka'b bin Malik, Sallam bin Abul Huqaiq, Ummu Misthah, Sa D bin Mu Adz, Ibnu Qami'ah, Ka'b bin Asad, Ashhamah bin Al-Aijar, Ibnu Ummi, Martsad bin Abu Martsad, Al-Miqdad bin Al-Aswad, Amir bin Fuhairah, Abdullah bin Uraiqith, Malik bin Auf, Imran bin Amr.

**Komunitas 1 (47 anggota):** Abu Jahal, Abu Sufyan bin Harb, Abu Azzah, Khunais bin Hudzafah, Zainab, Zaid bin Haritsah, Ummu Kultsum, Husain bin Ali, Abdurrahman, Hamzah bin Abdul Muththalib, Abu Lahab, Shafwan bin Umayyah, Thu'aimah bin Adi, Umayyah bin Khalaf, Bilal bin Rabah, Najasyi, An-Nadhr bin Al-Harits, Wahb bin Umair, Umair bin Wahb, Uqbah bin Al-Harits, Zaid bin Ad-Dastinah, Ukkasyah bin Mihshan, Ubadah bin Ash-Shamit, Ali bin Umayyah, Abdurrahman bin Auf, Al-Aswad bin Al-Muththalib, Abdullah bin Abu Bakar, Amr bin Al-Ash, Ikrimah bin Abu Jahal, Al-Abbas bin Abdul Muththalib, Jubair bin Muth'im, Siba bin Arfazhah, Abu Lubabah bin Abdul, Wahsy bin Harb, Ummul Fadhl, Abul Ash, Abdullah bin Abbas, Umayyah, Hakim bin Hizam, Abul Bakhtari bin Hisyam, Abu Thalib, Abu Shafwan, Budail bin Zarqa', Abu Hudzaifah, Utbah bin Rabi'ah, Salamah bin Abu Salamah, Musafi' bin Abdi.

**Komunitas 2 (7 anggota):** Musailamah, Urwah bin Mas'ud, Ka'b bin Zuhair, Bujair bin Zuhair, Syaima' binti Al-Harits, Mu'adz bin Amr, Jabalah bin Al-Aiham.

**Komunitas 3 (3 anggota):** Tsabit bin Qais bin Syammas, Az-Zabir bin Batha, Iyas bin Mu'adz.

**Komunitas 4 (3 anggota):** Nu'man bin Qail, Al-Harits bin Abdi, Mu'adz bin Jabal.

**Komunitas 5 (3 anggota):** Abu Rafi', Abdullah bin Unais, Abdullah bin Atik.

**Komunitas 6 (2 anggota):** Kurz bin Jabir, Sa'd bin Abu Waqqash.

**Komunitas 7 (2 anggota):** Usamah bin Zaid, Mirdas bin Nuhaik.

**Komunitas 8 (2 anggota):** Nu'aim bin Ma'ud, Sulaith bin An-Nu'man.

**Komunitas 9 (2 anggota):** Abu Bashir, Abu Jandal.
