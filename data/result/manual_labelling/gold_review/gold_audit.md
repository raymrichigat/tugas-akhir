# Worksheet Audit Gold (detail per kasus)

> ⚠️ **DIAGNOSTIK SEMENTARA (model LAMA, bukan hasil final).** Dipakai untuk menemukan gold yang kelewat/aneh sebelum retrain. Di-refresh ulang setelah semua model dilatih ulang.

Untuk tiap baris: baca `konteks` (token bermasalah ditandai 〚...〛), lalu di `gold_audit.csv` isi:
- `keputusan`: **GOLD_SALAH** (gold-nya keliru) / **MODEL_SALAH** (gold benar, model yang salah) / **AMBIGU**.
- `koreksi`: kalau GOLD_SALAH, tulis label BIO yang benar (mis. `I-PERSON`, `B-LOCATION`, atau `O`).


## A. gold=O, model=ENTITAS (kandidat gold KELEWAT / model FP) — 63 kasus

**Shalallahu** (gold=`O` vs model=`B-PERSON`) — _usul: HONORIFIK (gold=O, harus ikut PERSON)_  
  ...menyerahkan berhala-berhala itu kepada 16_ Mukhtashar Siratir-Rasul 〚Shalallahu〛 Alaihi wa Sallam , Syaikh Muhammad bin...  
  `keputusan: MODEL_SALAH   koreksi: O`

**Alaihi** (gold=`O` vs model=`I-PERSON`) — _usul: HONORIFIK (gold=O, harus ikut PERSON)_  
  ...berhala-berhala itu kepada 16_ Mukhtashar Siratir-Rasul Shalallahu 〚Alaihi〛 wa Sallam , Syaikh Muhammad bin Abdul...  
  `keputusan: MODEL_SALAH   koreksi: O`

**wa** (gold=`O` vs model=`I-PERSON`) — _usul: HONORIFIK (gold=O, harus ikut PERSON)_  
  ...itu kepada 16_ Mukhtashar Siratir-Rasul Shalallahu Alaihi 〚wa〛 Sallam , Syaikh Muhammad bin Abdul Wahhab...  
  `keputusan: MODEL_SALAH   koreksi: O`

**Baitul-Haram** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...sedang ihram . Mereka tidak boleh masuk 〚Baitul-Haram〛 dengan mengenakan kain wol 20 Lihat Shahih...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**610** (gold=`O` vs model=`I-TIME`) — _usul: OCR/ANGKA (token mengandung digit)_  
  ..., atau bertepatan dengan tanggal 10 Agustus 〚610〛 M . Usia beliau saat itu genap...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**Hadhramaut** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...rombongan kafilah bisa berlalu dari Shan'a hingga 〚Hadhramaut〛 tanpa rasa takut kecuali kepada Allah ."...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**Bakar** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Ummu Jamil menjawab,"Aku tidak tahu di manaAbu 〚Bakar〛 dan Muhammad bin Abdullah berada . Jika...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**265** (gold=`O` vs model=`I-PERSON`) — _usul: OCR/ANGKA (token mengandung digit)_  
  ...satuan pasukan yang pertama pada khalifah Abu 〚265〛 Shahih Al-Bukhari , Bab Ba'tsu Usamah ,...  
  `keputusan: MODEL_SALAH   koreksi: O`

**jazirah** (gold=`O` vs model=`B-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...eksternal saat kemunculan Islam . Para penguasa 〚jazirah〛 tatkala terbitnya matahari Islam , bisa dibagi...  
  `keputusan: MODEL_SALAH   koreksi: O`

**tatkala** (gold=`O` vs model=`I-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...saat kemunculan Islam . Para penguasa jazirah 〚tatkala〛 terbitnya matahari Islam , bisa dibagi menjadi...  
  `keputusan: MODEL_SALAH   koreksi: O`

**IRAQ** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...krisis Tetapi kekuasaan di Hijaz di mata 〚IRAQ〛 RAN bangsa Arab memiliki kehormatan suez tersendiri...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**suez** (gold=`O` vs model=`B-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...mata IRAQ RAN bangsa Arab memiliki kehormatan 〚suez〛 tersendiri . Mereka melihat kekuasaan di Hijaz...  
  `keputusan: MODEL_SALAH   koreksi: O`

**Arab** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...istilah kepemimpinan agama . Mereka Peta Kerajaan 〚Arab〛 Saudi berkuasa di tanah suci dengan sifatnya...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**Saudi** (gold=`O` vs model=`I-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...kepemimpinan agama . Mereka Peta Kerajaan Arab 〚Saudi〛 berkuasa di tanah suci dengan sifatnya sebagai...  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`

**Kalb** (gold=`O` vs model=`I-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ..., tetapi dia justru dibuang ke Darul 〚Kalb〛 dan meninggal di sana . Sistem kerajaan...  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`

**lyas** (gold=`O` vs model=`B-PERSON`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...dunia . Sebagai penggantinya , Kisra mengangkat 〚lyas〛 bin Qubaishah Ath-Thayy'i , dan memerintahkannya mendatangi...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**bin** (gold=`O` vs model=`I-PERSON`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  .... Sebagai penggantinya , Kisra mengangkat lyas 〚bin〛 Qubaishah Ath-Thayy'i , dan memerintahkannya mendatangi Hani'...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Qubaishah** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Sebagai penggantinya , Kisra mengangkat lyas bin 〚Qubaishah〛 Ath-Thayy'i , dan memerintahkannya mendatangi Hani' bin...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Ummul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...orang lain . Keadaan beliau juga digambarkan 〚Ummul〛 Mukminin Khadijah , Beliau membawa bebannya sendiri...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Al-Asyraf** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Muslim itu berhenti di dekat benteng Ka'b 〚Al-Asyraf〛 . Abu Na ilah berbisik-bisik memanggil nama...  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`

**3** (gold=`O` vs model=`I-TIME`) — _usul: OCR/ANGKA (token mengandung digit)_  
  ...Uhud . terjadi pada bulan Jumadal Akhirah 〚3〛 H Gambarannya , orang-orang Quraisy terus dibayangi...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**H** (gold=`O` vs model=`I-TIME`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  .... terjadi pada bulan Jumadal Akhirah 3 〚H〛 Gambarannya , orang-orang Quraisy terus dibayangi keresahan...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**Abdullah** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...anak buahnya untuk menyampaikan surat tersebut ataukah 〚Abdullah〛 sendiri yang menyampaikannya . Siapa pun yang...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Selasa** (gold=`O` vs model=`I-TIME`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Hal ini terjadi pada malam 〚Selasa〛 tanggal 10 Jumadal Rasulullah mengetahuinya lewat pemberitaan...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**Al-Asyaj** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...dan macam-macam minuman . Pemimpin mereka adalah 〚Al-Asyaj〛 Al-Ashri , yang kemudian beliau bersabda tentang...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**perjanjian** (gold=`O` vs model=`B-EVENT`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...tidak lagi mengintai kafilah dagang Quraisy setelah 〚perjanjian〛 Hudaibiyah ....  
  `keputusan: GOLD_SALAH   koreksi: B-EVENT`

**M** (gold=`O` vs model=`I-TIME`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...bulan Februari atau awal bulan Maret 571 〚M〛 . Peristiwa ini merupakan prolog yang dibukakan...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**Manaf** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...dinisbatkan kepada kakeknya , Hasyim bin Abdu 〚Manaf〛 . Oleh karena itu ada baiknya jika...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Az-Zubair** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...ai sepuluh anak laki-laki : Al-Harits , 〚Az-Zubair〛 , Abu Thalib , Abdullah , Hamzah...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Abdul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  .... Mereka yang berpendapat seperti ini menambahkan 〚Abdul〛 Ka'bah dan Hajla . Ada yang berpendapat...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Abdul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...dan Hajla . Ada yang berpendapat , 〚Abdul〛 Ka'bah adalah Al-Muqawwim , dan Hajlah adalah...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Abdullah** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Shafiyyah , Arwa , dan 3 . 〚Abdullah〛 Dia adalah bapak Rasulullah . Ibunya adalah...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Hadramaut** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Shan'a 10 . Ziyad bin Lubaid ke 〚Hadramaut〛 11 . Adi bin Hatim ke Tha'i...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**Salamah** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...bin Al-Ashba' , atau berjuluk Ummu Abi 〚Salamah〛 , putri pemimpin mereka . 2 ....  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**ud** (gold=`O` vs model=`I-PERSON`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...Ghathafan y ang bernama Nu'aim bin Mas 〚ud〛 bin Amir Al Asyja'i y ang menemui...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**bin** (gold=`O` vs model=`I-PERSON`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...y ang bernama Nu'aim bin Mas ud 〚bin〛 Amir Al Asyja'i y ang menemui Rasulullah...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Amir** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...ang bernama Nu'aim bin Mas ud bin 〚Amir〛 Al Asyja'i y ang menemui Rasulullah seraya...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Ummul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  .... Al-Abbas masuk Islam , begitu pula 〚Ummul〛 Fadhl dan aku . Namun Al-Abbas menyembunyikan...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Fadhl** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Al-Abbas masuk Islam , begitu pula Ummul 〚Fadhl〛 dan aku . Namun Al-Abbas menyembunyikan keislamannya...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**wadi** (gold=`O` vs model=`B-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...di balik bukit pasir , di pinggiran 〚wadi〛 Badr ....  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**Ummul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Padahal aku adalah orang yang lemah . 〚Ummul〛 Fadhl bangkit memungut tiang pembatas Zamzam ,...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Fadhl** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...aku adalah orang yang lemah . Ummul 〚Fadhl〛 bangkit memungut tiang pembatas Zamzam , lalu...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Ummul** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Lahab hingga menimbulkan luka yang menganga . 〚Ummul〛 Fadhl berkata , " Engkau berani menyiksa...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Fadhl** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...hingga menimbulkan luka yang menganga . Ummul 〚Fadhl〛 berkata , " Engkau berani menyiksa orang...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**peperangan** (gold=`O` vs model=`B-EVENT`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...Surat ini merupakan penjelasan dari Allah tentang 〚peperangan〛 Badr , yang berbeda jauh dengan penjelasan-penjelasan...  
  `keputusan: GOLD_SALAH   koreksi: B-EVENT`

**Ath-Thabarani** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Diambilkan dari riwayat 〚Ath-Thabarani〛 , bahwa tiga hari sebelum ada informasi...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Dzul** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...perkampungan yang terletak antara Dzu Khasyab dan 〚Dzul〛 Marwah pada awal bulan Ramadhan 8 H...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**ibnu** (gold=`O` vs model=`B-PERSON`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...Islam , Arnab , budak perempuan milik 〚ibnu〛 Khathal yang juga dibunuh , Ummu Sa'd...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Khathal** (gold=`O` vs model=`I-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ..., Arnab , budak perempuan milik ibnu 〚Khathal〛 yang juga dibunuh , Ummu Sa'd yang...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Arnab** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...enam orang perempuan . Tetapi boleh jadi 〚Arnab〛 dan Ummu Sa'd ini adalah biduanita yang...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Abil** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Sekalipun anak 〚Abil〛 Huqaiq sudah menyetujui perjanjian ini , toh...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Judzam** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...bermarkas di sebuah mata air di wilayah 〚Judzam〛 yang disebut As-Salasil , hingga peperangan ini...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**8** (gold=`O` vs model=`I-TIME`) — _usul: OCR/ANGKA (token mengandung digit)_  
  ...untuk menemui mereka pada bulan Jumadal Akhirah 〚8〛 H seusai perang Mu'tah , dengan tujuan...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**H** (gold=`O` vs model=`I-TIME`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...menemui mereka pada bulan Jumadal Akhirah 8 〚H〛 seusai perang Mu'tah , dengan tujuan untuk...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**Beberapa** (gold=`O` vs model=`I-EVENT`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...bara api . Lokasi terjadinya Perang Badr 〚Beberapa〛 ayat yang memerintahkan perang , berarti menunjukkan...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Bahrain** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...d . Kindah . Mereka tinggal di 〚Bahrain〛 , lalu terpaksa meninggalkanya dan akhirnya singgah...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION `

**Hadhramaut** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...lalu terpaksa meninggalkanya dan akhirnya singgah di 〚Hadhramaut〛 . Namun nasib mereka tidak jauh berbeda...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION `

**Bahrain** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...mereka tidak jauh berbeda saat berada di 〚Bahrain〛 , hingga mereka pindah lagi ke Najd...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION `

**timur** (gold=`O` vs model=`B-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...merupakan pintu masuk bagi bangsa-bangsa non-Arab , 〚timur〛 tengah dan timur dekat , terus membentang...  
  `keputusan: MODEL_SALAH   koreksi: O`

**tengah** (gold=`O` vs model=`I-LOCATION`) — _usul: KAPITALISASI/huruf-kecil (gold=O, perlu cek)_  
  ...pintu masuk bagi bangsa-bangsa non-Arab , timur 〚tengah〛 dan timur dekat , terus membentang ke...  
  `keputusan: MODEL_SALAH   koreksi: O`

**India** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...dan timur dekat , terus membentang ke 〚India〛 dan Cina . Setiap benua mempertemukan lautnya...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION `

**Cina** (gold=`O` vs model=`B-LOCATION`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...dekat , terus membentang ke India dan 〚Cina〛 . Setiap benua mempertemukan lautnya dengan Jazirah...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION `

**Hajar** (gold=`O` vs model=`B-PERSON`) — _usul: ANOTASI_KELEWAT (regex tak menangkap nama berkapital)_  
  ...Dia memaksa Ibrahim untuk melenyapkan 〚Hajar〛 dan putranya yang masih kecil , Isma'il...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON `


## B. gold=ENTITAS, model=O (kandidat gold KELEBIHAN / model FN) — 40 kasus

**Babilon** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  .... Kepindahan mereka pada masa penaklukan bangsa 〚Babilon〛 dan Asyur di Palestina , yang mengakibatkan...  
  `keputusan: MODEL_SALAH   koreksi: B-LOCATION`

**Bukhtanashar** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...negeri mereka dan pemusnahan mereka di tangan 〚Bukhtanashar〛 pada tahun 587 SM . Banyak di...  
  `keputusan: gold_SALAH   koreksi: B-LOCATION`

**Babilonia** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...antara mereka yang ditawan dan dibawa ke 〚Babilonia〛 . Sebagian di antara mereka juga ada...  
  `keputusan: gold_SALAH   koreksi: B-LOCATION`

**pertengahan** (gold=`B-TIME` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...kepada Rasulullah untuk bertemu di Aqabah pada 〚pertengahan〛 hari-hari Tasyriq . Pada malam hari kami...  
  `keputusan: MODEL_SALAH   koreksi: B-TIME`

**Al-Barra'** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...." Abul Haitsam bin At-Taihan menyela perkataan 〚Al-Barra'〛 yang masih berbicara dengan Rasulullah , dengan...  
  `keputusan: MODEL_SALAH   koreksi: B-TIME`

**malam** (gold=`B-TIME` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...itu , yaitu pada hari Senin , 〚malam〛 tanggal 21 dari bulan Ramadhan , atau...  
  `keputusan: GOLD_SALAH   koreksi: I-TIME`

**dari** (gold=`I-TIME` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...pada hari Senin , malam tanggal 21 〚dari〛 bulan Ramadhan , atau bertepatan dengan tanggal...  
  `keputusan: MODEL_SALAH   koreksi: I-TIME`

**berkata,"Al-Baihaqi** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Zhilail-Qur'an , 26/166 . 55 Ibnu Hajar 〚berkata,"Al-Baihaqi〛 mengisahkan bahwa jangka waktu datangnya mimpi itu...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Ukazh** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...beliau berdiri di hadapan orang-orang di pasar 〚Ukazh〛 . Majannah , dan Dzil-Majaz untuk menyampaikan...  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`

**Dzil-Majaz** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...di pasar Ukazh . Majannah , dan 〚Dzil-Majaz〛 untuk menyampaikan risalah , maka beliau tidak...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**As-Samau'al** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Kisah tentang Hani' bin Mas'ud Asy-Syaibani , 〚As-Samau'al〛 bin Adiya dan Hajib bin Zararah sudah...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Ukazh** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...pasar-pasar Arab yang sangat terkenal , seperti 〚Ukazh〛 , Dzil-Majaz , Majinnah , dan lain-lainnya...  
  `keputusan: MODEL_SALAH   koreksi: B-LOCATION`

**Dzil-Majaz** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...yang sangat terkenal , seperti Ukazh , 〚Dzil-Majaz〛 , Majinnah , dan lain-lainnya Tentang perindustrian...  
  `keputusan: MODEL_SALAH   koreksi: B-LOCATION`

**Majinnah** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...terkenal , seperti Ukazh , Dzil-Majaz , 〚Majinnah〛 , dan lain-lainnya Tentang perindustrian atau kerajinan...  
  `keputusan: MODEL_SALAH   koreksi: B-LOCATION`

**Al-Jurf** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Zaid . Mereka berangkat hingga tiba di 〚Al-Jurf〛 , sejauh satu farsakh dari Madinah ....  
  `keputusan: MODEL_SALAH   koreksi: B-LOCATION`

**Ramadhan** (gold=`B-TIME` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...shalat lima waktu kalian , laksanakan puasa 〚Ramadhan〛 kalian , bayarkanlah zakat kalian dengan suka...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Dzu** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Masehi . Karena mereka menolak , maka 〚Dzu〛 Nuwas membuat parit-parit besar yang di dalamnya...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Nuwas** (gold=`I-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  .... Karena mereka menolak , maka Dzu 〚Nuwas〛 membuat parit-parit besar yang di dalamnya dinyalahkan...  
  `keputusan: MODEL_SALAH   koreksi: i-PERSON`

**Umayyah** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...panji kaum , yang menjadi wewenang Bani 〚Umayyah〛 . 6 . Al-Qubah , atau penanganan...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Bunyanil-Ka'bah** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...tidak layak diperlihatkan . Shahihul-Bukhari , bab 〚Bunyanil-Ka'bah〛 , 1/540 . 53 Shahihul-Bukhari , 1/3...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Ghazwah** (gold=`B-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...mereka 229 Lihat Shahih Al-Bukhari , bab 〚Ghazwah〛 Dzatu Qarad , 2/603 ; Shahih Muslim...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Dzatu** (gold=`I-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...229 Lihat Shahih Al-Bukhari , bab Ghazwah 〚Dzatu〛 Qarad , 2/603 ; Shahih Muslim ,...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Qarad** (gold=`I-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Lihat Shahih Al-Bukhari , bab Ghazwah Dzatu 〚Qarad〛 , 2/603 ; Shahih Muslim , 2/113-115...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Matausyalakh** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...bin Nuh E bin Lamk , bin 〚Matausyalakh〛 bin Akhnukh atau Idris , bin Yard...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**bin** (gold=`I-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Nuh E bin Lamk , bin Matausyalakh 〚bin〛 Akhnukh atau Idris , bin Yard ,...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Akhnukh** (gold=`I-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...E bin Lamk , bin Matausyalakh bin 〚Akhnukh〛 atau Idris , bin Yard , bin...  
  `keputusan: GOLD_SALAH   koreksi: B-PERSON`

**Idris** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Lamk , bin Matausyalakh bin Akhnukh atau 〚Idris〛 , bin Yard , bin Mahla'il ,...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Shafiyyah** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...atau Al-Baidha , Barrah , Atikah , 〚Shafiyyah〛 , Arwa , dan 3 . Abdullah...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Qudaid** (gold=`B-LOCATION` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  .... sebuah mata air milik mereka di 〚Qudaid〛 . Orang-orang Muslim bersiap-siap untuk berperang ....  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Juwairiyah** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Dalam pembagian harta rampasan dan tawanan , 〚Juwairiyah〛 menjadi bagian Tsabit bin Qais . Tsabit...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Al-Abbas** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...pula Ummul Fadhl dan aku . Namun 〚Al-Abbas〛 menyembunyikan keislamannya . Saat Perang Badr ,...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Al-Abbas** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Manakah orang yang berikrar di bawah pohon?' 〚Al-Abbas〛 menuturkan , " Demi Allah , seakan-akan...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Ghazwah** (gold=`B-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  .... Dengan 242 Shahih Al-Bukhari , bab 〚Ghazwah〛 Mu 'tah Min Ardhisi Syam , 2/611...  
  `keputusan: GOLD_SALAH   koreksi: O`

**Mu** (gold=`I-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...Dengan 242 Shahih Al-Bukhari , bab Ghazwah 〚Mu〛 'tah Min Ardhisi Syam , 2/611 ....  
  `keputusan: GOLD_SALAH   koreksi: O`

**Abul** (gold=`B-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...sana bersama anak keturunannya . Dia dijuluki 〚Abul〛 Muluk Al-Ghassasanah , yang dinisbatkan kepada mata...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Muluk** (gold=`I-PERSON` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...bersama anak keturunannya . Dia dijuluki Abul 〚Muluk〛 Al-Ghassasanah , yang dinisbatkan kepada mata air...  
  `keputusan: MODEL_SALAH   koreksi: I-PERSON`

**622** (gold=`I-TIME` vs model=`O`) — _usul: OCR/ANGKA (token mengandung digit)_  
  ...pada malam Senin , 16 September tahun 〚622〛 M , Abdullah bin Uraiqith datang ke...  
  `keputusan: MODEL_SALAH   koreksi: I-TIME`

**M** (gold=`I-TIME` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...malam Senin , 16 September tahun 622 〚M〛 , Abdullah bin Uraiqith datang ke gua...  
  `keputusan: MODEL_SALAH   koreksi: I-TIME`WW

**Hijrah** (gold=`B-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  ...hijrah untuk kedua kalinya ke Habasyah . 〚Hijrah〛 kali ini lebih sulit daripada hijrah yang...  
  `keputusan: MODEL_SALAH   koreksi: B-EVENT`

**Isra'** (gold=`B-EVENT` vs model=`O`) — _usul: MODEL_MISS atau gold KELEBIHAN (perlu cek konteks)_  
  .... " Ibnu Hajar menuturkan , sebelum 〚Isra'〛 Nabi sudah pernah shalat , begitu pula...  
  `keputusan: MODEL_SALAH   koreksi: B-EVENT`


## C. beda TIPE (kandidat salah-tipe) — 11 kasus

**tanggal** (gold=`I-TIME` vs model=`B-TIME`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ..., yaitu pada hari Senin , malam 〚tanggal〛 21 dari bulan Ramadhan , atau bertepatan...  
  `keputusan: MODEL_SALAH   koreksi: I-TIME`

**bulan** (gold=`I-TIME` vs model=`B-TIME`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...hari Senin , malam tanggal 21 dari 〚bulan〛 Ramadhan , atau bertepatan dengan tanggal 10...  
  `keputusan: MODEL_SALAH   koreksi: I-TIME`

**Kisra** (gold=`B-PERSON` vs model=`I-EVENT`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...untuk memeranginya . Dengan dibantu pasukan perang 〚Kisra〛 . terjadilah peperangan yang dahsyat antara kedua...  
  `keputusan: MODEL_SALAH   koreksi: B-PERSON`

**Hudaibiyah** (gold=`B-LOCATION` vs model=`I-EVENT`) — _usul: AMBIGU_LOC_EVENT (lihat worksheet terpisah)_  
  ...lagi mengintai kafilah dagang Quraisy setelah perjanjian 〚Hudaibiyah〛 ....  
  `keputusan: GOLD_SALAH   koreksi: I-EVENT`

**Bukhtanashar** (gold=`B-PERSON` vs model=`B-LOCATION`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...sekalipun rakyatnya orang-orang Muslim , seperti peristiwa 〚Bukhtanashar〛 pada tahun 587 SM dan orang-orang Romawi...  
  `keputusan: GOLD_SALAH   koreksi: B-LOCATION`

**Ka'bah** (gold=`B-LOCATION` vs model=`I-PERSON`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...Mereka yang berpendapat seperti ini menambahkan Abdul 〚Ka'bah〛 dan Hajla . Ada yang berpendapat ,...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Ka'bah** (gold=`B-LOCATION` vs model=`I-PERSON`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...Hajla . Ada yang berpendapat , Abdul 〚Ka'bah〛 adalah Al-Muqawwim , dan Hajlah adalah Al...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Ka'b** (gold=`B-PERSON` vs model=`B-LOCATION`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...7 . Basyir bin Sufyan ke Bani 〚Ka'b〛 8 . Ibnul Latibah Al-Uzdi ke Bani...  
  `keputusan: GOLD_SALAH   koreksi: I-PERSON`

**Badr** (gold=`B-LOCATION` vs model=`I-LOCATION`) — _usul: AMBIGU_LOC_EVENT (lihat worksheet terpisah)_  
  ...balik bukit pasir , di pinggiran wadi 〚Badr〛 ....  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`

**Badr** (gold=`B-LOCATION` vs model=`I-EVENT`) — _usul: AMBIGU_LOC_EVENT (lihat worksheet terpisah)_  
  ...ini merupakan penjelasan dari Allah tentang peperangan 〚Badr〛 , yang berbeda jauh dengan penjelasan-penjelasan lain...  
  `keputusan: GOLD_SALAH   koreksi: I-EVENT`

**Marwah** (gold=`B-LOCATION` vs model=`I-LOCATION`) — _usul: SALAH_TIPE (gold vs model beda tipe)_  
  ...yang terletak antara Dzu Khasyab dan Dzul 〚Marwah〛 pada awal bulan Ramadhan 8 H agar...  
  `keputusan: GOLD_SALAH   koreksi: I-LOCATION`
