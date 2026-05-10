# Validasi Semua Relasi (Proximity-based)

Validasi false positive dari ketiga tipe relasi.

## Mekanisme Proximity

Dua entitas dianggap berelasi jika memenuhi **salah satu** syarat:

1. Berada dalam **kalimat yang sama**, ATAU
2. Jarak antar entitas **< 200 karakter**

Relasi yang terbentuk:

- **INVOLVED_IN**: PERSON dekat EVENT → person terlibat dalam event
- **OCCURRED_AT**: EVENT dekat LOCATION → event terjadi di lokasi
- **OCCURRED_ON**: EVENT dekat TIME → event terjadi pada waktu

Setelah proximity check, diterapkan **contextual guard** berupa
pattern-matching pada evidence untuk menyaring false positive.

## Ringkasan Keseluruhan

| Tipe Relasi | Total | Valid | Invalid | Review | % Invalid |
|-------------|-------|-------|---------|--------|-----------|
| INVOLVED_IN | 153 | 19 | 0 | 134 | 0.0% |
| OCCURRED_AT | 34 | 18 | 0 | 16 | 0.0% |
| OCCURRED_ON | 39 | 27 | 0 | 12 | 0.0% |
| **TOTAL** | **226** | **64** | **0** | **162** | **0.0%** |

---

## INVOLVED_IN

Total: 153 | Valid: 19 | Invalid: 0 | Review: 134

| No | Source (PERSON) | Target (EVENT) | Status | Alasan | Evidence (kutipan) |
|----|--------------------|---------------------|--------|--------|-------------------|
| 1 | Imran bin Amr | Hijrah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...erhijrah bisa dibagi menjadi empat golongan: Uzd. Hijrah mereka langsung dipimpin pemuka dan pemi... |
| 2 | Jabalah bin Al-Aiham | Perang Yarmuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...bagai kaki tangan imperium Romawi, hingga meletus Perang Yarmuk pada tahun 13 H. Raja mereka yang... |
| 3 | Umar bin Al-Khaththab | Perang Yarmuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...bagai kaki tangan imperium Romawi, hingga meletus Perang Yarmuk pada tahun 13 H. Raja mereka yang... |
| 4 | Bukhtanashar | Perang Bukhtanashar | Valid | Partisipasi aktif dalam event | ...p di langit Makkah sejak masa itu. Buktinya, saat Bukhtanashar berperang melawan bangsa Arab di D... |
| 5 | Jursyum bin Jalhamah | Perang Bukhtanashar | Valid | Disebutkan aktif pada saat event | ...i Jurhum. Bani Adnan berpencar ke Yaman pada saat Perang Bukhtanashar II (tahun 587 SM.), lalu pe... |
| 6 | Harb bin Umayyah | Perang Fijar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Pada usia lima belas tahun, meletus Perang Fijar antara pihak Quraisy bersama Kinanah, berhadapan de... |
| 7 | Muhammad | Perang Fijar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n beralih ke pihak Quraisy dan Kinanah. Dinamakan Perang Fijar, karena terjadi pelanggaran terhad... |
| 8 | Musa bin Imran | Mi'raj | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ..., yaitu di atas lapisan-lapisan langit pada malam Mi'raj, berisi kewajiban shalat dan lain-lainny... |
| 9 | Amr bin Al-Ash | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n riwayat Ibnu Ishaq. Yang lain menyebutkan bahwa Amr bin Al-Ash diutus kepada Najasyi setelah Pe... |
| 10 | Najasyi | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...in menyebutkan bahwa Amr bin Al-Ash diutus kepada Najasyi setelah Perang Badr. |
| 11 | Ubay bin Khalaf | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...sa orang lain, dan justru hanya memangsa dirinya. Ubay bin Khalaf pernah mengancam akan membunuh ... |
| 12 | Muhammad | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ah bin Khalaf saat masih di Makkah, Aku mendengar Rasulullah bersabda, Sesungguhnya orang-orang M... |
| 13 | Abu Jahal | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...bersumpah tidak akan keluar dari Makkah. Tatkala Abu Jahal mengajaknya pergi saat Perang Badr, di... |
| 14 | Abu Sufyan bin Harb | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Makkah. Tatkala Abu Jahal mengajaknya pergi saat Perang Badr, dia membeli seekor onta paling bagu... |
| 15 | Abu Bakar | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...dan orang-orang sudah sepi, mereka pergi memapah Abu Bakar, hingga tiba di tempat Rasulullah . 10... |
| 16 | Muhammad | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ka pergi memapah Abu Bakar, hingga tiba di tempat Rasulullah . 108 Benih-benih cinta dan kasih ya... |
| 17 | Urwah bin Az-Zubair | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...elah meriwayatkan kisah ini dengan sanadnya, dari Urwah bin Az-Zubair, bahwa Aisyah pernah bertan... |
| 18 | Aisyah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...dengan sanadnya, dari Urwah bin Az-Zubair, bahwa Aisyah pernah bertanya kepada Nabi ,"Pernakah en... |
| 19 | Ibnu Abdi | Perang Uhud | Valid | Disebutkan aktif pada saat event | ...galami suatu hari yang lebih berat daripada waktu Perang Uhud?" Beliau menjawab, Aku sudah mendap... |
| 20 | Yalail bin Abdi | Perang Uhud | Valid | Disebutkan aktif pada saat event | ...galami suatu hari yang lebih berat daripada waktu Perang Uhud?" Beliau menjawab, Aku sudah mendap... |
| 21 | Abu Rasulullah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...melindungi siapa pun yang engkau lindungi," kata Abu Rasulullah senantiasa teringat perlindungan ... |
| 22 | Iyas bin Mu'adz | Perang Bu'ats | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...etibanya di Yastrib (Madinah), dia terbunuh dalam Perang Bu'ats. Adapun keislamannya terjadi pada... |
| 23 | Muhammad | Isra' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...nul Qayyim berkata, "Menurut riwayat yang shahih. Rasulullah di Isra'kan dengan jasadnya. Dari Ma... |
| 24 | Jibril | Isra' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...kata, "Menurut riwayat yang shahih. Rasulullah di Isra'kan dengan jasadnya. Dari Masjidil Haram k... |
| 25 | Jibril | Mi'raj | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n di Sidratul Muntaha. Jadi beliau pernah melihat Jibril dalam dua rupa aslinya, sekali tatkala d... |
| 26 | Qais bin Al-Aslat | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Di antara mereka ada Qais bin Al-Aslat, seorang penyair yang selalu ditaati kaumnya. Dia sangat berp... |
| 27 | Mush'ab bin Umair | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...peran menghalangi mereka masuk Islam, hingga saat Perang Khandaq pada tahun kelima setelah hijrah... |
| 28 | Muhammad | Baiat Aqabah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Setelah terjadinya peristiwa Baiat Aqabah kedua, dan Islam berhasil memancangkan tonggak negara di t... |
| 29 | Muhammad | Hijrah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ang diperoleh Islam semenjak dakwah dimulai, maka Rasulullah dan orang-orang Muslim diperkenankan... |
| 30 | Abu Salamah bin Abdul Asad | Baiat Aqabah Kubra | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...eka: 1. Yang pertama kali melakukan hijrah adalah Abu Salamah, yaitu setahun sebelum Baiat Aqabah... |
| 31 | Muhammad | Baiat Aqabah Kubra | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...isa hijrah. Dua bulan lebih beberapa hari setelal Baiat Aqabah Kubra, tak seorang pun dari orang-... |
| 32 | Abu Bakar | Baiat Aqabah Kubra | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...isa hijrah. Dua bulan lebih beberapa hari setelal Baiat Aqabah Kubra, tak seorang pun dari orang-... |
| 33 | Ali bin Abu Thalib | Baiat Aqabah Kubra | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...isa hijrah. Dua bulan lebih beberapa hari setelal Baiat Aqabah Kubra, tak seorang pun dari orang-... |
| 34 | Abu Bakar | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...iman, Abdullah bin Abu Bakar dan seluruh keluarga Abu Bakar, termasuk pula Aisyah. Sementara Zain... |
| 35 | Aisyah | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...kar dan seluruh keluarga Abu Bakar, termasuk pula Aisyah. Sementara Zainab, putri beliau masih ti... |
| 36 | Zainab | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...luarga Abu Bakar, termasuk pula Aisyah. Sementara Zainab, putri beliau masih tinggal bersama suam... |
| 37 | Abul Ash | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...nab, putri beliau masih tinggal bersama suaminya, Abul Ash di Makkah. Zainab belum memungkinkan u... |
| 38 | Muhammad | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...emungkinkan untuk hijrah, dan baru hijrah setelah Perang Badr Aisyah berkata, Tatkala Rasulullah ... |
| 39 | Bilal bin Rabah | Perang Badr Aisyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...emungkinkan untuk hijrah, dan baru hijrah setelah Perang Badr Aisyah berkata, Tatkala Rasulullah ... |
| 40 | Abdullah bin Ubay bin Salul | Perang Bu'ats | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...beberapa pertimbangan. Tokoh kelompok ini adalah Abdullah bin Ubay. Sebelum itu, tepatnya seusai ... |
| 41 | Muhammad | Perang Bu'ats | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...auh-jauh waktu. Mereka juga mempunyai andil dalam Perang Bu ats, karena masing-masing berkomplot ... |
| 42 | Al-Miqdad bin Amr | Perang Abwa' | Valid | Pembawa bendera perang | ...Bendera Sa'd berwarna putih dan pembawanya adalah Al-Miqdad bin Amr. Perang Abwa' atau Waddan. Pa... |
| 43 | Muhammad | Perang Abwa' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...na putih dan pembawanya adalah Al-Miqdad bin Amr. Perang Abwa' atau Waddan. Pada bulan Shafar 2 H... |
| 44 | Sa'd bin Ubadah | Perang Abwa' | Valid | Terlibat dalam pengangkatan wakil | ...na putih dan pembawanya adalah Al-Miqdad bin Amr. Perang Abwa' atau Waddan. Pada bulan Shafar 2 H... |
| 45 | Muhammad | Perang Buwath | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...s Ini merupakan peperangan pertama yang dilakukan Rasulullah Kepergiannya untuk tujuan peperangan... |
| 46 | Hamzah bin Abdul Muththalib | Perang Buwath | Valid | Pembawa bendera perang | ...dera perang berwarna putih, dan pembawanya adalah Hamzah bin Abdul Muththalib. 5. Perang Buwath. ... |
| 47 | Umayyah bin Khalaf | Perang Buwath | Valid | Pemimpin/komandan dalam event | ...pembawanya adalah Hamzah bin Abdul Muththalib. 5. Perang Buwath. Pada bulan Rabi'ul Awwal 2 H ata... |
| 48 | Sa'd bin Mu'adz | Perang Safawan | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...kali ini tidak terjadi apa-apa. Beliau mengangkat Sa'd bin Mua'dz sebagai wakil beliau di Madinah... |
| 49 | Kurz bin Jabir | Perang Safawan | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...h, dan pembawanya adalah Sa d bin Abi Waqqash. 6. Perang Safawan. Pada bulan Rabi'ul Awwal 2 H be... |
| 50 | Zaid bin Haritsah | Perang Badr Ula | Valid | Terlibat dalam pengangkatan wakil | ...agi tanpa ada peperangan. Perang ini bisa disebut Perang Badr Ula (pertama). Kali ini beliau meng... |
| 51 | Ali bin Abu Thalib | Perang Badr Ula | Valid | Pembawa bendera perang | ...agi tanpa ada peperangan. Perang ini bisa disebut Perang Badr Ula (pertama). Kali ini beliau meng... |
| 52 | Zaid bin Haritsah | Perang Dzul Usyairah | Valid | Terlibat dalam pengangkatan wakil | ...ng Badr Ula (pertama). Kali ini beliau mengangkat Zaid bin Haritsah sebagai wakil beliau di Madin... |
| 53 | Ali bin Abu Thalib | Perang Dzul Usyairah | Valid | Pembawa bendera perang | ...ndera perang berwana putih, dan pembawanya adalah Ali bin Abu Thalib. 7. Perang Dzul Usyairah. Pa... |
| 54 | Muhammad | Perang Dzul Usyairah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...tih, dan pembawanya adalah Ali bin Abu Thalib. 7. Perang Dzul Usyairah. Pada bulan Jumadal Ula da... |
| 55 | Kurz bin Jabir | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ataupun yang dipimpin Rasulullah sendiri sebelum Perang Badr. Dalam satu peperangan pun tidak ter... |
| 56 | Abdullah bin Jahsy | Perang Badr Beberapa | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...haq dan batil. Insiden yang dipicu satuan pasukan Abdullah bin Jahsy merupakan pukulan yang telak... |
| 57 | Hakim bin Hizam | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mata air melainkan pasti mereka terbunuh, kecuali Hakim bin Hizam. Dia tidak terbunuh dan setelah... |
| 58 | Umair bin Wahb | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...a, "Tidak. Demi yang telah menyelamatkan aku dari Perang Badr." Setelah pasukan Quraisy agak tena... |
| 59 | Abdurrahman bin Auf | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...menyedot darahnya lewat tangan dua pemuda Anshar. Abdurrahman bin Auf menuturkan, "Tatkala aku se... |
| 60 | Ukkasyah bin Mihshan | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ngi daripada membiarkan mereka tetap hidup." Pada Perang Badr itu pedang Ukkasyah bin Mihshan Al-... |
| 61 | Mush'ab bin Umair | Perang Riddah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...erangan bersama beliau, hingga dia terbunuh dalam Perang Riddah, dan saat itu pun pedang tersebut... |
| 62 | Abu Aziz bin Umair | Perang Riddah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...erangan bersama beliau, hingga dia terbunuh dalam Perang Riddah, dan saat itu pun pedang tersebut... |
| 63 | Al-Abbas bin Abdul Muththalib | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ntu Rasulullah berkata, "Dulu aku adalah pembantu Al-Abbas. Saat itu Islam sudah masuk kepada beb... |
| 64 | Abu Lahab | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Namun Al-Abbas menyembunyikan keislamannya. Saat Perang Badr, Abu Lahab tidak ikut serta. Ketika ... |
| 65 | Siba bin Arfazhah | Perang Badr | Valid | Terlibat dalam pengangkatan wakil | ...tujuh hari sepulang dari Badr. Beliau mengangkat Siba bin Arfazhah sebagai wakil beliau di Madina... |
| 66 | Ibnu Ummi | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Madinah. Namun menurut pendapat lain, dia adalah Ibnu Ummi Lokasi Perang Badr 163 Zadul-Ma'ad, 2/... |
| 67 | Shafwan bin Umayyah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...reka, yaitu Nabi Selang tak seberapa lama sesudah Perang Badr, Umair bin Wahb Al-Jumahi duduk-dud... |
| 68 | Wahb bin Umair | Perang Badr | Valid | Korban/tawanan dalam event | ...dan para sahabat selagi masih di Makkah. Anaknya, Wahb bin Umair menjadi tawanan Perang Badr. Saa... |
| 69 | Umar bin Al-Khaththab | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Setelah itu dia berangkat hingga tiba di Madinah. Umar bin Al-Khaththab yang sedang membicarakan ... |
| 70 | Abdullah bin Abbas | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...lalu. Abu Dawud dan lain-lainya meriwayatkan dari Ibnu Abbas $, dia berkata. "Setelah Rasulullah ... |
| 71 | Abu Lubabah bin Abdul | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Terjadi pada bulan Dzul Hijjah, dua bulan setelah Perang Badr. Urusan di Madinah beliau serahkan ... |
| 72 | Furat bin Hayyan | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...pasukan, setelah mengambil seperlimanya. Kemudian Furat bin Hayyan masuk Islam di hadapan beliau.... |
| 73 | Ikrimah bin Abu Jahal | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n paling getol mengadakan persiapan perang adalah Ikrimah bin Abu Jahl, Shafwan bin Umayyah, Abu ... |
| 74 | Abdullah bin Abu Rabi'ah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ahl, Shafwan bin Umayyah, Abu Sufyan bin Harb dan Abdullah bin Abu Rabi'ah Tindakan pertama yang ... |
| 75 | Hamzah bin Abdul Muththalib | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...tokoh kelompok yang sangat berantusias ini adalah Hamzah bin Abdul Muththalib, paman Rasulullah ,... |
| 76 | Ali bin Abu Thalib | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...llah. Dan, Allah mempunyai karunia yang besar. " (Ali Rasulullah berada di Hamra'ul Asad tiga har... |
| 77 | Abu Azzah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ebelum kembali ke Madinah, beliau dapat menangkap Abu Azzah Al-Jumahi, yang pada saat Perang Badr... |
| 78 | Abu Azzah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...bantu seorang pun untuk memerangi beliau. Rupanya Abu Azzah ingkar janji, karena dia membangkitka... |
| 79 | Abu Sufyan bin Harb | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...kin kuat setelah kita tahu keputusan yang diambil Abu Sufyan, karena dia mengetahui Rasulullah da... |
| 80 | As'ad bin Zurarah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...abut eksistensinya. Belum genap dua bulan setelah Perang Uhud, Bani As'ad sudah menggelar persiap... |
| 81 | Abu Salamah bin Abdul Asad | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...infeksi pada luka yang didapatakannya pada waktu Perang Uhud, tak lama kemudian Abu Salamah menin... |
| 82 | Zaid bin Haritsah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...nolak, akhirnya orang itu dibunuh. Mereka membawa Zaid dan Khubaib ke Makkah dan menjualnya disan... |
| 83 | Hujair bin Abu Ihab | Perang Badr | Valid | Disebutkan aktif pada saat event | ...e Makkah dan menjualnya disana Padahal pada waktu Perang Badr, keduanya telah menghabisi sekian b... |
| 84 | Zaid bin Ad-Dastinah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Makkah saat itu tidak ada buah anggur. Sedangkan Zaid bin Ad-Datsinah dibeli Shafwan bin Umayyah,... |
| 85 | Ka'b bin Zaid bin An-Najjar | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mbunuh tanpa ada seorang pun yang tersisa, selain Ka'b bin Zaid bin An-Najjar. Dia pura-pura mati... |
| 86 | Amr bin Umayyah | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...a dia bisa selamat dan tetap hidup sampai meletus Perang Khandaq. Sementara itu Amr bin Umayyah A... |
| 87 | Al-Mundzir bin Uqbah bin Amir | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...a dia bisa selamat dan tetap hidup sampai meletus Perang Khandaq. Sementara itu Amr bin Umayyah A... |
| 88 | Amr bin Umayyah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n budak wanita yang mengaku dulunya milik ibunya. Amr bin Umayyah pergi ke Madinah hendak menemui... |
| 89 | Ka'b bin Al-Asyraf | Perang Bani Qainuqa' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ntara mereka dan kaum muslimin, sekalipun setelah Perang Bani Qainuqa' dan terbunuhnya Ka'b bin A... |
| 90 | Ka'b bin Al-Asyraf | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ipun setelah Perang Bani Qainuqa' dan terbunuhnya Ka'b bin Al-Asyraf mereka selalu dicekam ketaku... |
| 91 | Abu Hurairah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ilangkan terlebih sebelum kaum Muslimin terjun ke Perang Badr (yang kedua). Tidak benar Perang Dz... |
| 92 | Abu Musa | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ilangkan terlebih sebelum kaum Muslimin terjun ke Perang Badr (yang kedua). Tidak benar Perang Dz... |
| 93 | Muhammad | Perang Dzatur Riqa' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n terjun ke Perang Badr (yang kedua). Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah... |
| 94 | Abu Hurairah | Perang Dzatur Riqa' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n terjun ke Perang Badr (yang kedua). Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah... |
| 95 | Abu Musa | Perang Dzatur Riqa' | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n terjun ke Perang Badr (yang kedua). Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah... |
| 96 | Muhammad | Perang Khaibar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah terjadi pada bulan Rabi'ul Awwal atau... |
| 97 | Abu Hurairah | Perang Khaibar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...a bulan Rabi'ul Awwal atau Jumadil Ula itu. Sebab Abu Hurairah dan Abu Musa Al-Asy ari ikut berga... |
| 98 | Abu Musa | Perang Khaibar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...wwal atau Jumadil Ula itu. Sebab Abu Hurairah dan Abu Musa Al-Asy ari ikut bergabung dalam pepera... |
| 99 | Muhammad | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ya ada beberapa shalat yang tak sempat dikerjakan Rasulullah dan orang-orang Muslim. Di dalam Ash... |
| 100 | Jabir bin Abdullah | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...-orang Muslim. Di dalam Ashahihain disebutan dari Jabir bahwa Umar bin Al-Khaththab muncul pada w... |
| 101 | Umar bin Al-Khaththab | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...m. Di dalam Ashahihain disebutan dari Jabir bahwa Umar bin Al-Khaththab muncul pada waktu Perang ... |
| 102 | Ali bin Abu Thalib | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...t dilaksanakan. Di dalam riwayat Al-Bukhari, dari Ali, dari Nabi , beliau bersabda pada waktu Per... |
| 103 | Ali bin Abu Thalib | Perang Bani Quraizhah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...dari Quraisy dan Ghathafan. Tetapi perlu diingat, Perang Bani Quraizhah adalah peperangan urat sy... |
| 104 | Az-Zubair bin Al-Awwam | Perang Bani Quraizhah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...dari Quraisy dan Ghathafan. Tetapi perlu diingat, Perang Bani Quraizhah adalah peperangan urat sy... |
| 105 | Sa'd bin Mu'adz | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ..." jawab mereka. Beliau bersabda, "Serahkan kepada Sa'd bin Mu'adz." "Kami ridha," kata mereka Saa... |
| 106 | Huyai bin Akhthab | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...h bersama mereka Salah seorang di antara penjahat Perang Ahzab adalah Huyai bin Akhthab, ayah Sha... |
| 107 | Ka'b bin Asad | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...h bersama mereka Salah seorang di antara penjahat Perang Ahzab adalah Huyai bin Akhthab, ayah Sha... |
| 108 | Tsabit bin Qais bin Syammas | Perang Bu'ats | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ..., lalu masuk Islam dan menjadi sahabat yang baik. Tsabit bin Qaiz $ meminta kepada Rasulullah aga... |
| 109 | Az-Zabir bin Batha | Perang Bu'ats | Valid | Bersama rombongan event | ...Tsabit bin Qaiz $ meminta kepada Rasulullah agar Az-Zabir bin Batha beserta keluarga dan harta be... |
| 110 | Abdullah bin Atik | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mati. Kemudian para sahabat pulang dan menggotong Abdullah bin Atik hingga bertemu Rasulullah . P... |
| 111 | Abul Ash | Fathul Makkah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...g pada hadits dha'if ini, mereka menyatakan bahwa Abul Ash masuk Islam pada akhir tahun kedelapan... |
| 112 | Abdullah bin Ubay bin Salul | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...abung bersama mereka dan membaca Al-Qur an. Namun Abdullah bin Ubay berkata, "Duduk saja di rumah... |
| 113 | Abdullah bin Ubay bin Salul | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...apan pun yang mereka kehendaki, di bawah pimpinan Abdullah bin Ubay. Rencana mereka yang jahat in... |
| 114 | Zainab binti Jahsy | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Rencana mereka yang jahat ini tampak jelas seusai Perang Ahzab, saat Rasulullah menikahi Ummul Mu... |
| 115 | Zaid bin Haritsah | Perang Khandaq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Rencana mereka yang jahat ini tampak jelas seusai Perang Ahzab, saat Rasulullah menikahi Ummul Mu... |
| 116 | Muhammad | Perang Bani Mushthaliq | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...ntas tentang perilaku orang-orang munafik sebelum Perang Bani Mushthaliq. Sementara, Rasulullah m... |
| 117 | Amr bin Umayyah | Perang Tabuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...dia mengirim mereka dengan menumpang dua perahu. Amr bin Umayyah Adh-Dhamri juga ikut dalam rombo... |
| 118 | Muhammad | Perjanjian Hudaibiyah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...n daripada surat-surat lain yang dikirimkan Surat Rasulullah kepada Muqaiqis kepada para raja. Me... |
| 119 | Salamah bin Al-Akwa' | Perjanjian Hudaibiyah | Review | Sahabat perawi: mungkin peserta sekaligus narator | ...ya. Ini merupakan peperangan yang meletus setelah Perjanjian Hudaibiyah dan sebelum Perang Khaiba... |
| 120 | Salamah bin Al-Akwa' | Perang Khaibar | Review | Sahabat perawi: mungkin peserta sekaligus narator | ...meletus setelah Perjanjian Hudaibiyah dan sebelum Perang Khaibar. Al-Bukhari menyebutkan bahwa pe... |
| 121 | Ibnu Al-Akwa' | Ghazwah Dzatu Qarad | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...tiap anak panah kulepas, aku berkata, "Aku adalah Ibnu Al-Akwa'. Ini adalah hari kehinaan bagi ka... |
| 122 | Ibnu Ummi | Perang Khaibar Bekas | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...aat perjalanan pulang ke Madinah. Beliau menunjuk Ibnu Ummi Maktum sebagai wakil beliau di Madina... |
| 123 | Al-Miqdad bin Amr | Perang Khaibar Bekas | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...perangan ini. Sedangkan bendera diserahkan kepada Al-Miqdad bin Amr. Lokasi Perang Khaibar Bekas ... |
| 124 | Amir bin Al-Akwa' | Perang Khaibar | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...syair itu?" Tanya beliau. Orang-orang menjawab, "Amir bin Al-Akwa'." Beliau bersabda, "Allah mera... |
| 125 | Muhammad | Perang Mu'tah | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Setelah Rasulullah mengetahui sikap beberapa kabilah Arab di pinggiran Syam yang berpihak kepada pas... |
| 126 | Abu Bakar | Perang Bani Al | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...au. Tak seorang pun yang mengetahui hal ini. Lalu Abu Bakar datang ke rumah Aisyah dan bertanya, ... |
| 127 | Aisyah | Perang Bani Al | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...engetahui hal ini. Lalu Abu Bakar datang ke rumah Aisyah dan bertanya, "Wahai putriku, untuk apa ... |
| 128 | Muhammad | Perang Bani Al | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ..."Demi Allah, yang seperti ini hanya terjadi pada Perang Bani Al-Ashfar. Kemana yang hendak dituju... |
| 129 | Amr bin Salim | Perang Bani Al | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ..."Demi Allah, yang seperti ini hanya terjadi pada Perang Bani Al-Ashfar. Kemana yang hendak dituju... |
| 130 | Abrahah | Perjanjian Hudaibiyah | Valid | Pemimpin/komandan dalam event | ...t pasukan penunggang gajah (pasukan yang dipimpin Abrahah) menyerang Ka'bah, dengan tujuan untuk ... |
| 131 | Malik bin Auf | Perang Hunain | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...katnya merupakan perpanjangan dan kelanjutan dari Perang Hunain. Sebab mayoritas pelarian Hawazin... |
| 132 | Muhammad | Perang Hunain | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...katnya merupakan perpanjangan dan kelanjutan dari Perang Hunain. Sebab mayoritas pelarian Hawazin... |
| 133 | Muhammad | Perang Tabuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mang beberapa kabilah Arab mengirim utusan kepada Rasulullah setelah perang penaklukan Makkah dan... |
| 134 | Muhammad | Perang Tha'if | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Dulunya dia suka menyerang Rasulullah lewat syair-syairnya. Setelah beliau pulang dari Perang Tha'if... |
| 135 | Ka'b bin Zuhair | Perang Tha'if | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...lewat syair-syairnya. Setelah beliau pulang dari Perang Tha'if pada tahun 8 H, Ka'b bin Zuhair di... |
| 136 | Bujair bin Zuhair | Perang Tha'if | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...lewat syair-syairnya. Setelah beliau pulang dari Perang Tha'if pada tahun 8 H, Ka'b bin Zuhair di... |
| 137 | Urwah bin Mas'ud | Perang Tha'if | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...elakang keislaman mereka, karena pemimpin mereka, Urwah bin Mas'ud, Ats-Tsaqafi membuntuti Rasulu... |
| 138 | Al-Harits bin Abdi | Perang Tabuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...9. Surat dari raja-raja Yaman. Sepulang Nabi dari Perang Tabuk, datang surat dari raja-raja Himya... |
| 139 | Nu'man bin Qail | Perang Tabuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...9. Surat dari raja-raja Yaman. Sepulang Nabi dari Perang Tabuk, datang surat dari raja-raja Himya... |
| 140 | Mu'adz bin Jabal | Perang Tabuk | Valid | Pemimpin/komandan dalam event | ...eberapa orang dari sahabat ke sana, yang dipimpin Mu'adz bin Jabal. 10. Utusan dari Hamdan. Para ... |
| 141 | Malik bin An-Namath | Perang Tabuk | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...san ini datang pada tahun 9 H, sepulang Nabi dari Perang Tabuk. Beliau menulis sebuah perjanjian ... |
| 142 | Abul Ash bin Ar-Rabi' | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...tsum, dan Fathimah. Zainab dinikahi anak bibinya, Abul Ash bin Ar-Rabi', sebelum hijrah. Sedangka... |
| 143 | Ummu Kultsum | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...Ar-Rabi', sebelum hijrah. Sedangkan Ruqayyah dan Ummu Kultsum dinikahi Utsman bin Affan tidak sec... |
| 144 | Utsman bin Affan | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...rah. Sedangkan Ruqayyah dan Ummu Kultsum dinikahi Utsman bin Affan tidak secara bersamaan. Sedang... |
| 145 | Hasan bin Ali | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mah dinikahi Ali bin Abu Thalib pada waktu antara Perang Badr dan Uhud. Dari pernikahan Fathimah ... |
| 146 | Husain bin Ali | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...mah dinikahi Ali bin Abu Thalib pada waktu antara Perang Badr dan Uhud. Dari pernikahan Fathimah ... |
| 147 | Zainab | Perang Badr | Valid | Disebutkan aktif pada saat event | ...mah dinikahi Ali bin Abu Thalib pada waktu antara Perang Badr dan Uhud. Dari pernikahan Fathimah ... |
| 148 | Khunais bin Hudzafah | Perang Badr | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Dia ditinggal mati suaminya, Khunais bin Hudzafah As-Sahmi, pada waktu antara Perang Badr dan Uhud, ... |
| 149 | Hilal bin Amir bin Sha'sha'ah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | Dia berasal dari Bani Hilal bin Amir bin Sha'sha'ah, yang dijuluki Ummul Masakin (ibunda orang-orang... |
| 150 | Abdullah bin Jahsy | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...nya terhadap mereka. Sebelum itu dia adalah istri Abdullah bin Jahsy, yang mati syahid pada Peran... |
| 151 | Ummu Salamah | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...rmusuhan beberapa kabilah terhadap Islam. Setelah Ummu Salamah dari Bani Makhzum yang satu perkam... |
| 152 | Abu Jahal | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...h dari Bani Makhzum yang satu perkampungan dengan Abu Jahl dan Khalid bin Walid dinikahi Rasulull... |
| 153 | Khalid bin Al-Walid | Perang Uhud | Review | Proximity match tanpa bukti partisipasi/narasi yang jelas | ...akhzum yang satu perkampungan dengan Abu Jahl dan Khalid bin Walid dinikahi Rasulullah , membuat ... |

---

## OCCURRED_AT

Total: 34 | Valid: 18 | Invalid: 0 | Review: 16

| No | Source (EVENT) | Target (LOCATION) | Status | Alasan | Evidence (kutipan) |
|----|--------------------|---------------------|--------|--------|-------------------|
| 1 | Hijrah | Yaman | Valid | Peristiwa di negeri/wilayah | ...erhijrah bisa dibagi menjadi empat golongan: Uzd. Hijrah mereka langsung dipimpin pemuka dan pemi... |
| 2 | Perang Yarmuk | Syam | Review | Tidak ditemukan pola yang jelas | ...kat mereka sebagai raja bagi semua bangsa Arab di Syam Ibukotanya adalah Dumatul-Jandal. Suku Gha... |
| 3 | Hijrah | Habasyah | Valid | Lokasi tujuan hijrah | ...emerintahkan mereka hijrah untuk kedua kalinya ke Habasyah. Hijrah kali ini lebih sulit daripada ... |
| 4 | Perang Badr | Yatsrib | Review | Tidak ditemukan pola yang jelas | ...Makkah. Tatkala Abu Jahal mengajaknya pergi saat Perang Badr, dia membeli seekor onta paling bagu... |
| 5 | Perang Uhud | Aqabah | Review | Tidak ditemukan pola yang jelas | ...galami suatu hari yang lebih berat daripada waktu Perang Uhud?" Beliau menjawab, Aku sudah mendap... |
| 6 | Perang Bu'ats | Yatsrib | Valid | Peristiwa kematian setelah tiba | ...g benar- benar bagus." Tapi tak lama setibanya di Yastrib (Madinah), dia terbunuh dalam Perang Bu... |
| 7 | Perang Bu'ats | Madinah | Review | Tidak ditemukan pola yang jelas | ...benar bagus." Tapi tak lama setibanya di Yastrib (Madinah), dia terbunuh dalam Perang Bu'ats. Ada... |
| 8 | Perang Khandaq | Yaman | Review | Tidak ditemukan pola yang jelas | ...atau delapan puluh keluarga dari kaumnya setelah Perang Al-Khandaq. Kemudian dia mendapat cobaan ... |
| 9 | Isra' | Masjidil Haram | Valid | Titik awal perjalanan sakral | ...kata, "Menurut riwayat yang shahih. Rasulullah di Isra'kan dengan jasadnya. Dari Masjidil Haram k... |
| 10 | Isra' | Baitul Maqdis | Valid | Tujuan perjalanan sakral | ...kata, "Menurut riwayat yang shahih. Rasulullah di Isra'kan dengan jasadnya. Dari Masjidil Haram k... |
| 11 | Mi'raj | Sidratul Muntaha | Valid | Peristiwa saat berada di lokasi | ...nya, sekali tatkala di bumi dan sekali tatkala di Sidratul Muntaha, wallahu a Peristiwa pembelaha... |
| 12 | Baiat Aqabah Kubra | Aqabah | Valid | Nama event 'Baiat Aqabah Kubra' mengandung lokasi 'Aqabah' | ...Madinah dengan selamat. 127 Begitulah kisah baiat Aqabah kedua yang juga dikenal dengan istilah B... |
| 13 | Baiat Aqabah Kubra | Madinah | Valid | Lokasi tujuan hijrah | ...hijrah adalah Abu Salamah, yaitu setahun sebelum Baiat Aqabah Kubra, seperti yang dikatakan Ibnu ... |
| 14 | Baiat Aqabah Kubra | Makkah | Review | Tidak ditemukan pola yang jelas | ...isa hijrah. Dua bulan lebih beberapa hari setelal Baiat Aqabah Kubra, tak seorang pun dari orang-... |
| 15 | Perang Safawan | Madinah | Review | Tidak ditemukan pola yang jelas | ...h, dan pembawanya adalah Sa d bin Abi Waqqash. 6. Perang Safawan. Pada bulan Rabi'ul Awwal 2 H be... |
| 16 | Perang Badr | Madinah | Review | Tidak ditemukan pola yang jelas | ...a, "Tidak. Demi yang telah menyelamatkan aku dari Perang Badr." Setelah pasukan Quraisy agak tena... |
| 17 | Perang Uhud | Madinah | Valid | Kejadian dekat lokasi | ...tun mereka ke peperangan yang seru, tak jauh dari Madinah, yang dikenal dalam sejarah dengan Pera... |
| 18 | Perang Badr | Badr | Valid | Nama event 'Perang Badr' mengandung lokasi 'Badr' | ...awwal 2 Hijriyah, selang tujuh hari sepulang dari Badr. Beliau mengangkat Siba bin Arfazhah sebag... |
| 19 | Perang Badr | Makkah | Review | Tidak ditemukan pola yang jelas | ...kekalahan yang diderita orang-orang musyrik dalam Perang Badr, mereka semakin dibakar kebencian t... |
| 20 | Perang Uhud Jabal | Uhud | Valid | Nama event 'Perang Uhud Jabal' mengandung lokasi 'Uhud' | ...ghadapi orang-orang Muslim. Inilah yang mengawali Perang Uhud Jabal Uhud |
| 21 | Perang Bani Nadhir | Madinah | Review | Tidak ditemukan pola yang jelas | ...emenangan yang diperoleh orang-orang Muslim dalam Perang Bani Nadhir tanpa pengorbanan apa pun, p... |
| 22 | Perang Khaibar | Khaibar | Valid | Nama event 'Perang Khaibar' mengandung lokasi 'Khaibar' | ...al Abu Hurairal masuk Islam beberapa hari sebelum Perang Khaibar, dan Abu Musa Al-Asy ari bergabu... |
| 23 | Perang Dzatur Riqa' | Khaibar | Review | Tidak ditemukan pola yang jelas | ...dan Abu Musa Al-Asy ari bergabung dengan Nabi di Khaibar. Jadi Perang Dzatur Riqa' terjadi setela... |
| 24 | Perang Khandaq | Khandaq | Valid | Nama event 'Perang Khandaq' mengandung lokasi 'Khandaq' | ...enurut riwayat Ibnu Sa'd, Rasulullah kembali dari Khandaq pada hari Rabu, seminggu sebelum habisn... |
| 25 | Perang Khandaq | Madinah | Review | Tidak ditemukan pola yang jelas | ...umatkan kekuatan lebih kecil yang sedang mekar di Madinah. Sebab bangsa Arab tidak sanggup menghi... |
| 26 | Perjanjian Hudaibiyah | Hudaibiyah | Valid | Nama event 'Perjanjian Hudaibiyah' mengandung lokasi 'Hudaibiyah' | ...egaskan bahwa surat yang ditulis Nabi ini setelah Perjanjian Hudaibiyah. Adapun tentang keabsahan... |
| 27 | Perang Khaibar Bekas | Khaibar | Valid | Nama event 'Perang Khaibar Bekas' mengandung lokasi 'Khaibar' | ...ndera diserahkan kepada Al-Miqdad bin Amr. Lokasi Perang Khaibar Bekas benteng Yahudi Khaibar Bek... |
| 28 | Perang Khaibar | Hudaibiyah | Review | Tidak ditemukan pola yang jelas | Karena bagaimanapun juga, harta rampasan dari Perang Khaibar ini juga tidak lepas dari peran orang-o... |
| 29 | Ghazwah Mu'tah | Syam | Valid | Teks Arab 'dari tanah LOC' | ...sukan Muslimin. Dengan 242 Shahih Al-Bukhari, bab Ghazwah Mu 'tah Min Ardhisi Syam, 2/611. begitu... |
| 30 | Perang Mu'tah | Syam | Valid | Peristiwa di perbatasan lokasi | ...ngetahui sikap beberapa kabilah Arab di pinggiran Syam yang berpihak kepada pasukan Romawi dalam ... |
| 31 | Fathul Makkah | Makkah | Valid | Nama event 'Fathul Makkah' mengandung lokasi 'Makkah' | ...selama kurang lebih dua puluh tahun. Penaklukkan Makkah merupakan hasil paling penting yang dirai... |
| 32 | Fathul Makkah | Jazirah Arab | Review | Tidak ditemukan pola yang jelas | ...hun-tahun itu. Alhasil, perjalanan hari dan udara Jazirah Arab berubah total. Penaklukan Makkah i... |
| 33 | Perang Uhud | Hunain | Review | Tidak ditemukan pola yang jelas | ...nal di dunia. Adapun peristiwa yang terjadi dalam Perang Uhud dan Hunain lebih disebabkan karena ... |
| 34 | Perang Tha'if | Makkah | Review | Tidak ditemukan pola yang jelas | ...lewat syair-syairnya. Setelah beliau pulang dari Perang Tha'if pada tahun 8 H, Ka'b bin Zuhair di... |

---

## OCCURRED_ON

Total: 39 | Valid: 27 | Invalid: 0 | Review: 12

| No | Source (EVENT) | Target (TIME) | Status | Alasan | Evidence (kutipan) |
|----|--------------------|---------------------|--------|--------|-------------------|
| 1 | Perang Yarmuk | tahun 13 H | Valid | Waktu disebutkan di awal sebagai keterangan event | ...bagai kaki tangan imperium Romawi, hingga meletus Perang Yarmuk pada tahun 13 H. Raja mereka yang... |
| 2 | Perang Bukhtanashar | tahun 587 SM | Review | Tidak ditemukan pola yang jelas | ...i Jurhum. Bani Adnan berpencar ke Yaman pada saat Perang Bukhtanashar II (tahun 587 SM.), lalu pe... |
| 3 | Baiat Aqabah Kubra | hari Kamis | Valid | Waktu event dengan konversi kalender | ...kwah Islam, yang tidak lain adalah Muhammad. Pada hari Kamis tanggal 26 Shafar tahun 14 dari nubu... |
| 4 | Baiat Aqabah Kubra | tanggal 26 Shafar | Review | Tidak ditemukan pola yang jelas | ...yang tidak lain adalah Muhammad. Pada hari Kamis tanggal 26 Shafar tahun 14 dari nubuwah, bertepa... |
| 5 | Baiat Aqabah Kubra | tahun 14 dari nubuwah | Review | Tidak ditemukan pola yang jelas | ...dalah Muhammad. Pada hari Kamis tanggal 26 Shafar tahun 14 dari nubuwah, bertepatan dengan tangga... |
| 6 | Baiat Aqabah Kubra | tanggal 12 September | Valid | Waktu event dengan konversi kalender | ...6 Shafar tahun 14 dari nubuwah, bertepatan dengan tanggal 12 September tahun 622 M, atau kira-kir... |
| 7 | Baiat Aqabah Kubra | tahun 622 M | Review | Tidak ditemukan pola yang jelas | ...i nubuwah, bertepatan dengan tanggal 12 September tahun 622 M, atau kira-kira selang dua bulan se... |
| 8 | Perjanjian Hudaibiyah | bulan Ramadhan | Valid | Waktu event dengan konversi kalender | ...angnya. Tahapan ini berakhir dengan dikukuhkannya Perjanjian Hudaibiyah pada bulan Dzul-Qa'dah ta... |
| 9 | Fathul Makkah | bulan Ramadhan | Valid | Waktu event dengan konversi kalender | ...gan para memimpin paganisme, yang berakhir dengan Fathu Makkah pada bulan Ramadhan tahun dari hij... |
| 10 | Perang Abwa' | bulan Shafar 2 H | Valid | Waktu disebutkan di awal sebagai keterangan event | ...na putih dan pembawanya adalah Al-Miqdad bin Amr. Perang Abwa' atau Waddan. Pada bulan Shafar 2 H... |
| 11 | Perang Buwath | bulan Rabi'ul Awwal 2 H | Valid | Waktu keberangkatan event | ...pembawanya adalah Hamzah bin Abdul Muththalib. 5. Perang Buwath. Pada bulan Rabi'ul Awwal 2 H ata... |
| 12 | Perang Safawan | bulan Rabi'ul Awwal 2 H | Valid | Waktu event dengan konversi kalender | ...h, dan pembawanya adalah Sa d bin Abi Waqqash. 6. Perang Safawan. Pada bulan Rabi'ul Awwal 2 H be... |
| 13 | Perang Badr Ula | bulan Jumada | Valid | Waktu event dengan konversi kalender | ...agi tanpa ada peperangan. Perang ini bisa disebut Perang Badr Ula (pertama). Kali ini beliau meng... |
| 14 | Perang Dzul Usyairah | bulan Jumada | Valid | Waktu event dengan konversi kalender | ...tih, dan pembawanya adalah Ali bin Abu Thalib. 7. Perang Dzul Usyairah. Pada bulan Jumadal Ula da... |
| 15 | Perang Badr | bulan Syawwal 2 H | Valid | Teks eksplisit menyebutkan waktu kejadian | ...ngkan Makkah ke Syam. Peperangan ini terjadi pada bulan Syawwal 2 Hijriyah, selang tujuh hari sep... |
| 16 | Perang Badr | bulan Dzul Hijjah | Valid | Teks eksplisit menyebutkan waktu kejadian | ...erangan ini disebut perang As-Sawiq. Terjadi pada bulan Dzul Hijjah, dua bulan setelah Perang Bad... |
| 17 | Perang Uhud | bulan Muharram 3 H | Valid | Waktu disebutkan di awal sebagai keterangan event | ...kan paling besar yang dipimpin Rasulullah sebelum Perang Uhud. Kejadiannya pada bulan Muharram 3 ... |
| 18 | Perang Uhud | bulan Jumada | Valid | Teks eksplisit menyebutkan waktu kejadian | ...upakan mobilitas pasukan terakhir sebelum meletus Perang Uhud. terjadi pada bulan Jumadal Akhirah... |
| 19 | Perang Badr | bulan Jumada | Valid | Teks eksplisit menyebutkan waktu kejadian | ...erakhir sebelum meletus Perang Uhud. terjadi pada bulan Jumadal Akhirah 3 H Gambarannya, orang-or... |
| 20 | Perang Uhud | bulan Rabi'ul Awwal 4 H | Valid | Waktu event dengan konversi kalender | ...senantiasa memperlihatkan permusuhan, hingga pada bulan Rabi'ul Awwal 4 H mereka melakukan konspi... |
| 21 | Perang Uhud | bulan Jumadil Ula | Valid | Waktu event dengan konversi kalender | ...juga ikut-ikut latah untuk menyerang Madinah pada bulan Jumadil Ula Angin yang berhembus dari ara... |
| 22 | Perang Uhud | bulan Muharram 4 H | Valid | Teks eksplisit menyebutkan waktu kejadian | ...rang. Peristiwa ini terjadi tepat munculnya hilal bulan Muharram 4 H. Karena ada infeksi pada luk... |
| 23 | Perang Bani Nadhir | bulan Rabi'ul Awwal 4 H | Valid | Teks eksplisit menyebutkan waktu kejadian | ...at perang sebagai persediaan perang.f sabilillah. Perang Bani Nadhir ini terjadi pada bulan Rabi'... |
| 24 | Perang Badr | bulan Rabi'ul Awwal | Review | Konflik: VALID (Teks eksplisit menyebutkan waktu kejadian) vs INVALID (Waktu yang disangkal/dibantah dalam teks) | ...ilangkan terlebih sebelum kaum Muslimin terjun ke Perang Badr (yang kedua). Tidak benar Perang Dz... |
| 25 | Perang Badr | Jumadil Ula | Review | Konflik: VALID (Teks eksplisit menyebutkan waktu kejadian) vs INVALID (Waktu yang disangkal/dibantah dalam teks) | ...ilangkan terlebih sebelum kaum Muslimin terjun ke Perang Badr (yang kedua). Tidak benar Perang Dz... |
| 26 | Perang Dzatur Riqa' | bulan Rabi'ul Awwal | Review | Konflik: VALID (Teks eksplisit menyebutkan waktu kejadian) vs INVALID (Waktu yang disangkal/dibantah dalam teks) | ...n terjun ke Perang Badr (yang kedua). Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah... |
| 27 | Perang Dzatur Riqa' | Jumadil Ula | Review | Konflik: VALID (Teks eksplisit menyebutkan waktu kejadian) vs INVALID (Waktu yang disangkal/dibantah dalam teks) | ...n terjun ke Perang Badr (yang kedua). Tidak benar Perang Dzatur Riqa' yang dikomandani Rasulullah... |
| 28 | Perang Khaibar | bulan Rabi'ul Awwal | Valid | Teks eksplisit menyebutkan waktu kejadian | ...ur Riqa' yang dikomandani Rasulullah terjadi pada bulan Rabi'ul Awwal atau Jumadil Ula itu. Sebab... |
| 29 | Perang Khaibar | Jumadil Ula | Valid | Teks eksplisit menyebutkan waktu kejadian | ...Rasulullah terjadi pada bulan Rabi'ul Awwal atau Jumadil Ula itu. Sebab Abu Hurairah dan Abu Musa... |
| 30 | Perang Asafan | tahun 4 H | Review | Tidak ditemukan pola yang jelas | ...yang menguatkan bahwa perang ini terjadi setelah tahun 4 H, karena pada saat peperangan itu Nabi ... |
| 31 | Perang Khandaq | bulan Syawwal | Valid | Waktu event dengan konversi kalender | ...ambil kesimpulan bahwa permulaan pengepungan pada bulan Syawwal dan berakhir pada bulan Dzul Qa'd... |
| 32 | Perang Khandaq | bulan Dzul Qa'dah | Review | Tidak ditemukan pola yang jelas | ...Khandaq pada hari Rabu, seminggu sebelum habisnya bulan Dzul Qa'dah. Pasukan Muslim berhadapan de... |
| 33 | Perang Khandaq | bulan Dzul Qa'dah 5 H | Valid | Teks eksplisit menyebutkan waktu kejadian | ...au melepaskan talinya Peperangan ini terjadi pada bulan Dzul Qa'dah 5 H. Adapun pengepungan berja... |
| 34 | Perang Khandaq | Dzul Hijjah | Valid | Teks eksplisit menyebutkan waktu kejadian | ...Peristiwa ini terjadi pada bulan Dzul Qa'dah atau Dzul Hijjah 5 H. Seusai Perang Ahzab dan Bani Q... |
| 35 | Perang Khandaq | tahun 4 H | Valid | Waktu disebutkan di awal sebagai keterangan event | ...ang ada dua kejadian dalam sekali perjalanan pada tahun 4 H. Al-Allamah Al-Manshuri tidak setuju ... |
| 36 | Perang Tha'if | bulan Ramadhan 9 H | Valid | Waktu disebutkan di awal sebagai keterangan event | ...lagi." 8. Utusan dari Tsaqif. Mereka datang pada bulan Ramadhan 9 H, sepulang Rasulullah dari Tab... |
| 37 | Perang Tabuk | tahun 9 H | Valid | Waktu disebutkan di awal sebagai keterangan event | .... Utusan dari Hamdan. Para utusan ini datang pada tahun 9 H, sepulang Nabi dari Perang Tabuk. Bel... |
| 38 | Perang Badr | tahun 3 H | Review | Konflik: VALID (Waktu event dengan konversi kalender) vs INVALID (Waktu pernikahan, bukan waktu event) | ...Khunais bin Hudzafah As-Sahmi, pada waktu antara Perang Badr dan Uhud, lalu dinikahi Rasulullah p... |
| 39 | Perang Uhud | tahun 4 H | Review | Konflik: VALID (Waktu disebutkan di awal sebagai keterangan event) vs INVALID (Waktu pernikahan, bukan waktu event) | ...h istri Abdullah bin Jahsy, yang mati syahid pada Perang Uhud, lalu dinikahi Rasulullah pada tahu... |
