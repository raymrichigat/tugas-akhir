# Contoh Konkret Error per Kategori

> token **tebal** = rentang entitas gold. `pred` = tipe yang diprediksi model di rentang itu.


## Tak terdeteksi (false negative murni)


**EVENT:**

- …mereka 229 Lihat Shahih Al-Bukhari, bab **Ghazwah** **Dzatu** **Qarad,** 2/603; Shahih Muslim, 2/113-115; Fatahul Bari,…  (gold=EVENT, pred=O)
- …Muslimin. Dengan 242 Shahih Al-Bukhari, bab **Ghazwah** **Mu** 'tah Min Ardhisi Syam, 2/611. begitu…  (gold=EVENT, pred=O)
- …hijrah untuk kedua kalinya ke Habasyah. **Hijrah** kali ini lebih sulit daripada hijrah…  (gold=EVENT, pred=O)

**TIME:**

- …shalat lima waktu kalian, laksanakan puasa **Ramadhan** kalian, bayarkanlah zakat kalian dengan suka…  (gold=TIME, pred=O)
- …Hal ini terjadi pada hari Senin **bulan** **Rabi'ul** **Awwal.** Abu Bakar berdiri, sementara beliau hanya…  (gold=TIME, pred=O)

**PERSON:**

- …Fi Zhilail-Qur'an, 26/166. 55 Ibnu Hajar **berkata,"Al-Baihaqi** mengisahkan bahwa jangka waktu datangnya mimpi…  (gold=PERSON, pred=O)
- …" **(Ibrahim:** 13-14 Tatkala meletus peperangan yang sengit…  (gold=PERSON, pred=O)
- …pergi.' "Baiklah," jawab Ummul Khair. Maka **Ummu** **Jamil** pergi bersamanya untuk menemui Abu Bakar…  (gold=PERSON, pred=O)
- …Abu 265 Shahih Al-Bukhari, Bab Ba'tsu **Usamah,** 2/612.…  (gold=PERSON, pred=O)
- …agama Masehi. Karena mereka menolak, maka **Dzu** **Nuwas** membuat parit-parit besar yang di dalamnya…  (gold=PERSON, pred=O)
- …dari perak, dengan cetakan yang berbunyi **"Muhammad** Rasul Allah". Cetakan tulisan ini tersusun…  (gold=PERSON, pred=O)
- …bin Nuh E bin Lamk, bin **Matausyalakh** **bin** **Akhnukh** atau Idris , bin Yard, bin…  (gold=PERSON, pred=O)
- …Lamk, bin Matausyalakh bin Akhnukh atau **Idris** , bin Yard, bin Mahla'il, bin…  (gold=PERSON, pred=O)

**LOCATION:**

- …Kepindahan mereka pada masa penaklukan bangsa **Babilon** dan Asyur di Palestina, yang mengakibatkan…  (gold=LOCATION, pred=O)
- …mereka yang ditawan dan dibawa ke **Babilonia.** Sebagian di antara mereka juga ada…  (gold=LOCATION, pred=O)
- …berdiri di hadapan orang-orang di pasar **Ukazh.** Majannah, dan Dzil-Majaz untuk menyampaikan risalah,…  (gold=LOCATION, pred=O)
- …orang-orang di pasar Ukazh. Majannah, dan **Dzil-Majaz** untuk menyampaikan risalah, maka beliau tidak…  (gold=LOCATION, pred=O)
- …pasar-pasar Arab yang sangat terkenal, seperti **Ukazh,** Dzil-Majaz, Majinnah, dan lain-lainnya Tentang perindustrian…  (gold=LOCATION, pred=O)
- …Arab yang sangat terkenal, seperti Ukazh, **Dzil-Majaz,** Majinnah, dan lain-lainnya Tentang perindustrian atau…  (gold=LOCATION, pred=O)
- …yang sangat terkenal, seperti Ukazh, Dzil-Majaz, **Majinnah,** dan lain-lainnya Tentang perindustrian atau kerajinan,…  (gold=LOCATION, pred=O)
- …Zaid. Mereka berangkat hingga tiba di **Al-Jurf,** sejauh satu farsakh dari Madinah. Hanya…  (gold=LOCATION, pred=O)

## Misklasifikasi tipe (boundary benar, tipe salah)


**LOCATION:**

- …yang berpendapat seperti ini menambahkan Abdul **Ka'bah** dan Hajla. Ada yang berpendapat, Abdul…  (gold=LOCATION, pred=PERSON)
- …dan Hajla. Ada yang berpendapat, Abdul **Ka'bah** adalah Al-Muqawwim, dan Hajlah adalah Al…  (gold=LOCATION, pred=PERSON)

## Boundary error (overlap, batas beda)


**EVENT:**

- …menghadapi orang-orang Muslim. Inilah yang mengawali **Perang** **Uhud** **Jabal** Uhud…  (gold=EVENT, pred=EVENT)
- …diserahkan kepada Al-Miqdad bin Amr. Lokasi **Perang** **Khaibar** **Bekas** benteng Yahudi Khaibar Bekas bangunan di…  (gold=EVENT, pred=EVENT/O)
- …untuk hijrah, dan baru hijrah setelah **Perang** **Badr** **Aisyah** berkata, Tatkala Rasulullah sudah tiba di…  (gold=EVENT, pred=EVENT/PERSON)

**TIME:**

- …Rasulullah untuk bertemu di Aqabah pada **pertengahan** **hari-hari** **Tasyriq.** Pada malam hari kami berjanji untuk…  (gold=TIME, pred=O/TIME)
- …hari itu, yaitu pada hari Senin, **malam** **tanggal** **21** **dari** **bulan** **Ramadhan,** atau bertepatan dengan tanggal 10 Agustus…  (gold=TIME, pred=O/TIME)
- …Pada hari Kamis tanggal 26 Shafar **tahun** **14** **dari** **nubuwah,** bertepatan dengan tanggal 12 September tahun…  (gold=TIME, pred=O/TIME)
- …tahun 14 dari nubuwah, bertepatan dengan **tanggal** **12** **September** tahun 622 M, atau kira-kira selang…  (gold=TIME, pred=O/TIME)
- …nubuwah, bertepatan dengan tanggal 12 September **tahun** **622** **M,** atau kira-kira selang dua bulan setengah…  (gold=TIME, pred=O/TIME)
- …Jabir Al-Fihri ke penduduk Urainah pada **bulan** **Syawwal** **6** **H.**…  (gold=TIME, pred=O/TIME)

**PERSON:**

- …122 Dengan isnad hasan. Al-Hakim dan **Ibnu** **Hibban** menshahihkannya. Lihat Mukhtashar Siratir- Rasul, hal.…  (gold=PERSON, pred=O/PERSON)
- …untuk kedua kalinya. Al-Bukhari meriwayatkan dari **Jabir** **bin** **Abdullah,** bahwa dia pernah mendengar Rasulullah menuturkan…  (gold=PERSON, pred=O/PERSON)
- …orang-orang menirukan sabda beliau ini adalah **Rabi'ah** **bin** **Umayyah** **bin** **Setelah** Nabi selesai menyampaikan pidato, turun firman…  (gold=PERSON, pred=O/PERSON)
- …Urusan di Madinah beliau serahkan kepada **Abu** **Lubabah** **bin** **Abdul**…  (gold=PERSON, pred=O/PERSON)
- …keluarga Hasyimiyah, yang dinisbatkan kepada kakeknya, **Hasyim** **bin** **Abdu** Manaf. Oleh karena itu ada baiknya…  (gold=PERSON, pred=PERSON)
- …menikahi Tumadhir bin Al-Ashba', atau berjuluk **Ummu** **Abi** Salamah, putri pemimpin mereka. 2. Satuan…  (gold=PERSON, pred=PERSON)

**LOCATION:**

- …Inilah yang mengawali Perang Uhud Jabal **Uhud**…  (gold=LOCATION, pred=EVENT)
- …mengintai kafilah dagang Quraisy setelah perjanjian **Hudaibiyah.**…  (gold=LOCATION, pred=EVENT)
- …terletak antara Dzu Khasyab dan Dzul **Marwah** pada awal bulan Ramadhan 8 H…  (gold=LOCATION, pred=LOCATION)

## Over-deteksi (false positive murni)


**EVENT:**

- …dan pasukannya, sehingga peperangan ini disebut **perang** **As-Sawiq.** Terjadi pada bulan Dzul Hijjah, dua…  (gold=O, pred=EVENT)
- …Hudzaifah benar-benar terbunuh seorang syahid pada **perang** **Al-Yamamah** 2. Beliau melarang membunuh Abul Bakhtari,…  (gold=O, pred=EVENT)
- …yang patah di tanganku pada waktu **perang** **Mu'tah.** Yang tinggal di tanganku hanya sebatang…  (gold=O, pred=EVENT)
- …bulan Jumadal Akhirah 8 H seusai **perang** **Mu'tah,** dengan tujuan untuk membujuk dan melunakkan…  (gold=O, pred=EVENT)

**TIME:**

- …bertepatan dengan tanggal 10 Agustus 610 **M.** Usia beliau saat itu genap 40…  (gold=O, pred=TIME)
- …mimpi terjadi pada bulan kelahiran beliau, **yaitu** Rabi'ul Awwal, setelah usia beliau genap…  (gold=O, pred=TIME)
- …menemui mereka pada bulan Jumadal Akhirah **8** **H** seusai perang Mu'tah, dengan tujuan untuk…  (gold=O, pred=TIME)
- …Rasulullah menikahinya pada **bulan** **Syawal** tahun kesepuluh dar nubuwah, tepatnya beberapa…  (gold=O, pred=TIME)
- …bin Wahb bersama 25 orang pada **bulan** **Rabi'ul** **4.** Awwal. Pasalnya, Bani Hawazin seringkali mengulurkan…  (gold=O, pred=TIME)

**PERSON:**

- …berhala-berhala itu kepada 16_ Mukhtashar Siratir-Rasul **Shalallahu** **Alaihi** **wa** Sallam, Syaikh Muhammad bin Abdul Wahhab,…  (gold=O, pred=PERSON)
- …Jamil menjawab,"Aku tidak tahu di manaAbu **Bakar** dan Muhammad bin Abdullah berada. Jika…  (gold=O, pred=PERSON)
- …pasukan yang pertama pada khalifah Abu **265** Shahih Al-Bukhari, Bab Ba'tsu Usamah, 2/612.…  (gold=O, pred=PERSON)
- …perutnya yang membesar itu. Para pengikut **Fir** **aun** melewati mereka tatkala digiring ke neraka,…  (gold=O, pred=PERSON)
- …meninggal dunia. Sebagai penggantinya, Kisra mengangkat **lyas** **bin** **Qubaishah** Ath-Thayy'i, dan memerintahkannya mendatangi Hani' bin…  (gold=O, pred=PERSON)
- …Abdul Muththalib mencari wanita dari Bani **Sa** d bin Bakr agar menyusui beliau.…  (gold=O, pred=PERSON)

**LOCATION:**

- …sedang ihram. Mereka tidak boleh masuk **Baitul-Haram** dengan mengenakan kain wol 20 Lihat…  (gold=O, pred=LOCATION)
- …kafilah bisa berlalu dari Shan'a hingga **Hadhramaut** tanpa rasa takut kecuali kepada Allah."…  (gold=O, pred=LOCATION)
- …kafilah bisa berlalu dari Shan'a hingga **Hadhramaut** tanpa rasa takut kecuali kepada Allah."…  (gold=O, pred=LOCATION)
- …beliau memerintahkan untuk kembali ke Madinah **Al-Munawarah** tanpa mengambil waktu untuk istirahat, agar…  (gold=O, pred=LOCATION)
- …eksternal saat kemunculan Islam. Para penguasa **jazirah** tatkala terbitnya matahari Islam, bisa dibagi…  (gold=O, pred=LOCATION)
- …dimotori imperium Romawi untuk menguasai negeri **Arab.** Mereka bekerja sama dengan orang orang…  (gold=O, pred=LOCATION)