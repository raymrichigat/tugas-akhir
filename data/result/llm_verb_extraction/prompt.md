# Tugas: Verb Action Extraction dari Teks Sirah Nabawiyah

Anda adalah asisten ekstraksi informasi yang ahli dalam Bahasa Indonesia dan teks
historis Sirah Nabawiyah. Tugas Anda: dari setiap chunk teks yang diberikan,
ekstrak **verb-action** (kata kerja yang menggambarkan peristiwa) bersama
subject (pelaku) dan object (penerima/lawan/lokasi tindakan).

## Tujuan

1. **Kandidat EVENT baru**: verb yang menggambarkan peristiwa terbatas waktu/ruang,
   yang **tidak punya nama proper noun** (mis. "berbaiat di Aqabah", "menyerang
   karavan", "berdoa di Ka'bah"). Bukan verb biasa seperti "berkata", "melihat".

2. **SVO relation triplet**: triplet (subject_entity, verb_relation, object_entity)
   yang bisa di-add ke Knowledge Graph sebagai relasi baru. Subject & object
   harus berupa **named entity** (PERSON, LOCATION, EVENT, atau TIME).

## Aturan Ekstraksi

**Untuk EVENT kandidat:**
- Hanya verb yang menggambarkan **aksi historis** (bertempur, berhijrah, berbaiat,
  bertukar surat, menyerang, mengutus, mendirikan, mengadakan perjanjian).
- **Skip** verb mental/percakapan biasa (berkata, mendengar, memikirkan, melihat,
  bertanya tanpa konteks aksi).
- **Skip** verb yang sudah punya named EVENT di teks (mis. kalau ada "Perang Badr",
  jangan extract lagi "berperang" sebagai EVENT — sudah ke-cover NER).
- Beri "label_aksi" pendek (2-4 kata) yang merangkum peristiwa.

**Untuk SVO triplet:**
- Subject & object harus **named entity** (nama orang, kabilah, lokasi, atau peristiwa
  bernama). Bukan kata ganti ("dia", "mereka") atau noun phrase generik ("orang itu",
  "para sahabat").
- relation_type proposal — gunakan kata kerja kanonik seperti:
  `MENGUTUS, MENYERANG, MENIKAHI, BERBAIAT_KEPADA, BERPERANG_DENGAN, MEMIMPIN,
   MENGUNJUNGI, BERHIJRAH_KE, MENGAJAR, MENERIMA_WAHYU, MENGUMUMKAN, MEMBANGUN,
   MENERIMA_DELEGASI, BERDAMAI_DENGAN, MENGEPUNG`
  Boleh tambah relation_type baru jika perlu, gunakan UPPER_SNAKE_CASE.

## Format Output (WAJIB JSON murni, tanpa markdown fence)

```
{
  "events": [
    {
      "chunk_id": "000123-004",
      "halaman": "266",
      "label_aksi": "Pengiriman delegasi ke Madinah",
      "verb": "mengutus",
      "subject": "Muhammad",
      "context_text": "Rasulullah mengutus Mush'ab bin Umair ke Madinah untuk...",
      "confidence": 0.9
    }
  ],
  "triplets": [
    {
      "chunk_id": "000123-004",
      "halaman": "266",
      "subject_entity": "Muhammad",
      "subject_label": "PERSON",
      "verb_relation": "MENGUTUS",
      "object_entity": "Mush'ab bin Umair",
      "object_label": "PERSON",
      "context_text": "Rasulullah mengutus Mush'ab bin Umair ke Madinah",
      "confidence": 0.9
    }
  ]
}
```

## Instruksi Penting

- Output **JSON valid murni**, tanpa code fence (```), tanpa narrative pengantar
  atau closing.
- Kalau satu chunk tidak ada kandidat, tetap lanjut ke chunk berikutnya, jangan
  paksa output.
- Confidence 0-1: 1 = jelas dari teks, 0.5 = ambigu, 0.3 = tebakan.
- Label entity harus salah satu dari: `PERSON, LOCATION, EVENT, TIME`.
- Bahasa Indonesia untuk semua field.

---

# Chunks Input

## Chunk `000008-001`  (halaman 53-54, sample=phase_P0, period=P0)

**Bab:** KEKUASAAN DAN IMARAH DI KALANGAN BANGSA ARAB  /  **Sub-bab:** Kekuasaan di Berbagai Penjuru Arab

```
Di bagian muka telah kami singgung tentang kepindahan kabilah-kabilah Qahthan dan Adnan. Sementara negeri Arab sendiri terpecah-pecah. Kabilah- kabilah yang berdekatan dengan Hirah mengikuti Raja Ghassan. Hanya saja subordinasi ini hanya sekedar nama, tidak dalam praktiknya. Sedangkan daerah- daerah di Jazirah Arab mempunyai kebebasan secara mutlak. Pada hakikatnya kabilah-kabilah ini mempunyai pemuka-pemuka yang 15 Sirah An-Nabawiyah, Ibnu Hisyam, memimpin kabilahnya masing-masing. Kabilah adalah sebuah pemerintahan kecil yang asas eksistensi politiknya adalah kesatuan fanatisme, adanya manfaat secara timbal balik untuk menjaga daerah, dan menghadang musuh dari luar Kedudukan pemimpin kabilah di tengah kaumnya tak ubahnya kedudukan seorang raja. Anggota kabilah mengikuti apa pun pendapat pemimpinnya tatkala damai maupun perang, tidak ada yang tercecer dari penanganannya, seperti apa pun keadaannya. Dia mempunyai kewenangan hukum dan otoritas pendapat, seperti layaknya seorang pemimpin diktator yang perkasa. Sehingga adakalanya jika seorang pemimpin murka, sekian ribu mata pedang akan ikut berbicara tanpa perlu bertanya apa yang membuat pemimpin kabilah itu murka.
```

## Chunk `000080-010`  (halaman 191-197, sample=phase_P5, period=P5)

**Bab:** ISRA’ DAN MI’RAJ  /  **Sub-bab:** UNLABELED SECTION

```
Padahal tidak begitu hakikatnya. Dengan susunan kalimat ini Allah mengisyaratkan bahwa Isra' itu merupakan perjalanan ke Baitul Maqdis. Sebab orang-orang Yahudi akan dikucilkan dari posisi pengendalian umat manusia, karena kejahatan-kejahatan yang mereka lakukan. sehingga mereka pun tersisih. Kemudian Allah akan mengalihkan posisi itu kepada Rasulullah dan menyatukan dua sentral dakwah keturunan Ibrahim Jadi sudah tiba saatnya untuk mengalihkan kendali kepemimpinan spiritual dari satu umat ke lain umat, dari umat yang sejarahnya dilumuri pengkhianatan, permusuhan, dan kejahatan, beralih ke umat yang dibanjiri kebaikan dan kebajikan, sehingga Rasul-Nya senantiasa mendapatkan wahyu Al-Qur an yang menunjuki kepada jalan yang paling lurus. Tetapi bagaimana kendali kepemimpinan itu bisa beralih, padahal Rasulullah hanya bisa berputar-putar di beberapa gunung di Makkah, dalam keadaan terkucil di tengah manusia? Pertanyaan ini menyingkap tabir tentang hakikat lain, bahwa satu periode dari dakwah Islam akan segera berakhir, lalu akan dimulai periode lain yang perjalanannya berbeda dengan periode yang pertama. Oleh karena itu kita bisa melihat sebagian ayat yang mengandung ancaman dan peringatan yang keras, tertuju kepada orang-orang musyrik seperti firman-Nya, "Dan jika Kami hendak membinasakan suatu negeri, maka Kami perintahkan kepada orang-orang yang hidup mewah di negeri itu (supaya mentaati Allah) tetapi mereka melakukan kedurhakaan dalam negeri itu!
```

## Chunk `000140-003`  (halaman 295-297, sample=phase_P8, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Makkah Menerima Kabar Kekalahan

```
Kami harus berhadapan dengan orang-orang yang berpakaian putih sambil menunggang kuda yang perkasa, berseliweran di antara langit dan bumi. Demi Allah, kuda- kuda itu tidak meninggalkan jejak sedikit pun dan tidak menginjak apa pun." Lalu aku (Abu Rafi') mengangkat batu pembatas Zamzam, sambil berkata, "Demi Allah, itu adalah para malaikat." Abu Lahab mengangkat tangannya tinggi-tinggi lalu memukulkan ke mukaku dengan keras. Aku hendak melawannya, namun dia membanting tubuhku ke tanah, kemudian menindihiku sambil melancarkan pukulan bertubi- tubi. Padahal aku adalah orang yang lemah. Ummul Fadhl bangkit memungut tiang pembatas Zamzam, lalu memukulkannya sekeras-kerasnya ke kepala Abu Lahab hingga menimbulkan luka yang menganga. Ummul Fadhl berkata, "Engkau berani menyiksa orang ini selagi tuannya tidak ada." Setelah itu Abu Lahab beranjak pergi sambil menundukkan muka. Demi Allah, Abu Lahab hanya mampu bertahan hidup tujuh hari setelah itu. Itu pun Allah menimpakan penyakit di sekujur tubuhnya, berupa luka bernanah Padahal bangsa Arab sangat jijik terhadap penyakit ini. Maka sanak saudaranya tidak mau mengurusnya, dan setelah meninggal pun jasadnya ditelantarkan hingga tiga hari. Mereka tidak berani mendekatinya dan tidak berusaha untuk menguburnya. Namun karena mereka takut akan dicemooh sebagai akibat dari tindakannya ini, mereka pun membuatkan sebuah lubang di dekatnya.
```

## Chunk `000254-002`  (halaman 465-469, sample=phase_P11, period=P11)

**Bab:** KORESPONDENSI DENGAN BEBERAPA RAJA DAN AMIR  /  **Sub-bab:** Surat kepada Raja Uman

```
Aku berkata di hadapannya, "Aku adalah utusan Rasulullah untuk menghadap tuan dan saudara tuan." "Temuilah saudaraku terlebih dahulu, karena dia lebih tua dan lebih berkuasa daripada aku. Aku akan mencoba mengantarkan engkau hingga dia bisa membaca suratmu." Kemudian Abd mengajukan beberapa pertanyaan, "Apa yang hendak engkau serukan?" Aku menjawab, "Aku menyeru kepada Allah semata, yang tiada sekutu bagi-Nya, hendaklah tuan melepaskan apa pun yang disembah selain-Nya, hendaklah tuan bersaksi bahwa Muhammad adalah hamba dan Rasul-Nya." "Wahai Amr, engkau adalah putra pemimpin kaummu. Lalu apa saja yang diperbuat ayahmu? Padahal kami sangat salut kepadanya." "Dia meninggal dalam keadaan tidak beriman kepada Muhammad. Padahal aku ingin sekali dia masuk Islam dan membenarkannya. Dulu aku sejalan dan sepemikiran hingga Allah memberikan petunjuk kepadaku untuk masuk Islam." "Sejak kapan engkau mengikutinya?" tanya Abd. "Belum lama," jawabku. "Di mana engkau masuk Islam?" "Di hadapan Najasyi," jawabku. Lalu aku mengabarkan kepadanya bahwa Najasyi sudah masuk Islam. "Lalu bagaimana reaksi kaumnya terhadap kerajaanya?" tanya Abd "Mereka tetap mengakuinya dan mengikutinya," jawabku. "Bagaimana dengan para pendeta dan padri?" tanyanya. "Begitu pun mereka," jawabku. "Hati-hatilah dengan perkataanmu wahai Amr. Sesungguhnya tak ada perangai seseorang yang lebih buruk daripada dusta." "Aku tidak berdusta, dan kami tidak menghalalkan dusta dalam agama kami," jawabku.
```

## Chunk `000358-003`  (halaman 591-593, sample=phase_P14, period=P14)

**Bab:** KEBERHASILAN DAKWAH ISLAM DAN PENGARUHNYA  /  **Sub-bab:** UNLABELED SECTION

```
Pada malam harinya beliau bangun untuk beribadah kepada Allah membaca Al-Qur an dan tunduk kepada Allah seperti yang diperintahkan- Begitulah Rasulullah menjalani kehidupan dalam kancah peperangan yang seakan tidak ada ujungnya selama lebih dari 20 tahun. Selama itu pula beliau tidak pernah lalai terhadap satu urusan tertentu, karena sibuk mengurusi urusan yang lain, hingga akhirnya dakwah Islam berhasil secara gemilang. merambah kawasan yang amat luas, sulit diterima nalar manusia. Seluruh Jazirah Arab tunduk kepada dakwah Islam, debu-debu jahiliyah tidak lagi tampak di udara dan akal yang tadinya menyimpang kini menjadi lurus, sehingga berhala ditinggalkan bahkan dihancurkan. Udara Arab berubah dipenuhi suara-suara tauhid, adzan untuk shalat terdengar memecah angkasa dan sela-sela gurun yang telah dihidupkan iman. Para pengajar Al-Qur an pergi ke arah utara dan selatan, membacakan ayat-ayat di dalam Kitab Allah dan menegakkan hukum hukum-Nya. Berbagai kabilah dan suku yang bertebaran di mana-mana bersatu padu Semua orang keluar terhadap penyembahan hamba kepada penyembahan terhadap Allah. Di sana tidak ada pihak yang merasa dipaksa dan pihak yang memaksa, tuan dan hamba, pejabat dan rakyat, orang zhalim dan dizhalimi Semua manusia adalah hamba Allah, saudara yang saling mencintai dan melaksanakan hukum Allah. Allah telah menyingkirkan gelombang jahiliyah kesombongan dan pengagungan terhadap nenek moyang.
```

## Chunk `000131-002`  (halaman 281-282, sample=perang_badr, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Bara Perang Mulai Menyala

```
Kami tidak membutuhkan kalian. Kami hanya menginginkan kerabat pamanku." Lalu ada di antara orang-orang musyrik itu yang berseru dengan suara lantang, Hai Muhammad, keluarkan orang-orang yang terpandang yang berasal dari kaum kalian." Rasulullah bersabda, "Bangunlah wahai Ubaidah bin Al-Harits, engkau Hamzah dan engkau Ali!" Tatkala tiga orang Muslim ini berdiri dan menghampiri tiga orang musyrik itu, mereka bertanya, "Siapa kalian ini?" Setelah pertanyaan ini dijawab, mereka pun berkata, "Memang kalian orang-orang terpandang." Ubaidah yang paling tua di antara mereka, berhadapan dengan Utbah bin Rabi ah, Hamzah berhadapan dengan Syaibah bin Rabi ah dan Ali berhadapan dengan Al-Walid. 153 Hamzah dan Ali tidak terlalu kesulitan melibas lawan tandingnya. Lain halnya dengan Ubaidah dan lawan tandingnya. Masing-masing saling melancarkan serangan hingga dua kali, dan masing-masing melukai lawannya Kemudian Hamzah dan Ali menghampiri Utbah lalu membunuhnya. Setelah itu mereka berdua memapah tubuh Ubaidah yang sudah lemah, karena kakinya tertebas hingga putus. Dia sama sekali tidak mengeluh hingga meninggal dunia di Ash-Shafra', empat atau lima hari setelah Perang Badr, di tengah perjalanan pulang ke Madinah. Pada saat itu Ali bersumpah kepada Allah, hingga karenanya turun ayat tentang kiprahnya, A:z "Inilah dua golongan (golongan Mukmin dan golongan kafir) yang bertengkar, mereka saling bertengkar karena Rabb mereka. " Kesudahan adu tanding ini merupakan awal yang buruk bagi orang.
```

## Chunk `000127-001`  (halaman 275-276, sample=perang_badr, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Menempati Posisi Lebih Strategis

```
Rasulullah membawa pasukannya ke mata air Badr agar bisa mendahului pasukan orang-orang Quraisy, sehingga mereka bisa menghalangi orang-orang Quraisy untuk menguasai mata air itu. Maka pada petang hari mereka sudah tiba di dekat mata air Badr. Di sinilah Al-Hubab bin Al-Mundzir tampil layaknya seorang penasihat militer, seraya bertanya, "Wahai Rasulullah, bagaimana pendapat engkau tentang keputusan berhenti di tempat ini? Apakah ini tempat berhenti yang diturunkan Allah kepada engkau? Jika begitu keadaannya, maka tidak ada pilihan bagi kami maju atau mundur dari tempat ini. Ataukah in sekedar pendapat, siasat, dan taktik perang?" Beliau menjawab, "Ini adalah pendapatku, siasat, dan taktik perang." Dia berkata, "Wahai Rasulullah, menurutku tidak tepat jika kita berhenti di sini. Pindahkanlah orang-orang ke tempat yang lebih dekat lagi dengan mata air daripada mereka (orang-orang musyrik Makkah). Kita berhenti di tempat itu dan kita timbun kolam-kolam di belakang mereka, lalu kita buat kolam yang kita isi air hingga penuh. Setelah itu kita berperang menghadapi mereka. Kita bisa minum dan mereka tidak bisa." Beliau bersabda, "Engkau telah menyampaikan pendapat yang jitu." Maka Rasulullah memindahkan pasukannya, sehingga jarak mereka dengan mata air lebih dekat lagi daripada pihak musuh. Separoh malam mereka berada di tempat itu, lalu mereka membuat sebuah kolom air dan menimbun kolam-kolam yang lain. Tatkala orang-orang Muslim sudah berhenti di tempat yang dimaksudkan.
```

## Chunk `000142-002`  (halaman 298-299, sample=perang_badr, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Pasukan Nabi Bergerak Menuju Madinah

```
Katakanlah,'Harta perang itu kepunyaan Allah dan Rasul. Sebab itu bertawakalah kepada Allah dan perbaikilah hubungan di antara sesama kalian dan taatlah kepada Allah dan Rasul-Nya jika kalian adalah orang. orang yang beriman. " Setelah tiga hari berada di Badr, pasukan Rasulullah bergerak ke Madinah sambil membawa tawanan dan harta rampasan yang diperoleh dari orang-orang musyrik, yang penanganannya diserahkan kepada Abdullah bin Ka'b. Setelah melewati celah Ash-Shafra', beliau menghentikan pasukan dan membagi harta rampasan di sana secara merata di antara orang-orang Muslim setelah mengambil seperlimanya. Setiba di Ash-Shafra', An-Nadhr bin Al-Harits diperintahkan untuk dibunuh, karena dia adalah pembawa bendera pasukan musyrikin dan dia termasuk pemuka Quraisy yang amat jahat, paling banyak memperdayai Islam dan menyiksa Rasulullah . Akhirnya dia dipenggal oleh Ali bin Abu Thalib Setibanya di Irquzh Zhabyah, beliau juga memerintahkan untuk membunuh Uqbah bin Abu Mu'aith. Di bagian terdahulu sudah kami paparkan tentang penyiksaan terhadap Rasulullah . Dialah yang melontarkan kotoran isi perut binatang yang sudah disembelih ke kepala beliau saat sedang shalat. Dia pula yang menjerat leher beliau dengan mantelnya. Selagi dia hampir dibunuh, Abu Bakar menahannya. Tatkala beliau tetap memerintahkan untuk membunuhnya Uqbah bertanya, "Bagaimana dengan anak-anakku wahai Muhammad?" Beliau menjawab, "Masuk neraka." Lalu dia dibunuh Ashim bin Tsabit Al-Anshari.
```

## Chunk `000140-001`  (halaman 295-297, sample=perang_badr, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Makkah Menerima Kabar Kekalahan

```
Orang-orang musyrik melarikan diri dari kancah Badr dengan berpencar- pencar tak beraturan. Mereka lari terbirit-birit menuju berbagai lembah dan perkampungan, setelah itu menuju ke Makkah dengan kepala tertunduk lesu Karena perasaan malu, mereka tidak tahu bagaimana cara untuk masuk ke Makkah. Ibnu Ishaq menuturkan, bahwa orang yang pertama kali menyampaikan kabar di Makkah tentang kekalahan Quraisy adalah Al-Haisuman bin Abdullah Al-Khuza'i. "Apa yang terjadi di sana?" Orang-orang yang berada di Makkah bertanya kepadanya Dia menjawab, "Utbah bin Rabi'ah, Syaibah bin Rabi'ah, Abul Hakam bin Hisyam, dan Umayyah bin Khalaf mati terbunuh." Dia masih menyebutkan beberapa nama pemimpin yang lain. Tatkala dia menyebutkan nama-nama pemuka Quraisy itu, Shafwan bin Umayyah yang hanya duduk di rumahnya berkata, "Demi Allah, jika dia memikirkan hal ini, maka bertanyalah kepadaku tentang dirinya!!" "Lalu apa yang bisa dilakukan Shafwan bin Umayyah?" tanya mereka. Al-Haisuman menjawab, "Dia hanya duduk di rumahnya, padahal demi Allah, kulihat dengan mata kepalaku sendiri bagaimana ayah dan saudaranya terbunuh." Abu Rafi', pembantu Rasulullah berkata, "Dulu aku adalah pembantu Al-Abbas. Saat itu Islam sudah masuk kepada beberapa anggota keluarga. Al-Abbas masuk Islam, begitu pula Ummul Fadhl dan aku. Namun Al-Abbas menyembunyikan keislamannya. Saat Perang Badr, Abu Lahab tidak ikut serta. Ketika sudah ada kabar tentang kekalahan pasukan Quraisy, maka Allah membuatnya rendah dan hina.
```

## Chunk `000142-001`  (halaman 298-299, sample=perang_badr, period=P8)

**Bab:** PERANG BADR KUBRA  /  **Sub-bab:** Pasukan Nabi Bergerak Menuju Madinah

```
Seusai perang, Rasulullah masih berada di Badr selama tiga hari Sebelum meninggalkan kancah peperangan, terjadi silang pendapat di antara anggota pasukan tentang pembagian harta rampasan. Ketika silang pendapat ini semakin meruncing maka beliau memerintahkan agar semua harta rampasan di tangan mereka diserahkan. Mereka pun menurutinya, lalu turun wahyu yang memecahkan masalah ini. Dari Ubadah bin Ash-Shamit, dia berkata, "Kami pergi bersama Nabi bergabung dalam Perang Badr. Dua pasukan saling berhadapan dan Allah mengalahkan pasukan musuh. Ada segolongan pasukan Muslimin yang mengejar musuh, mengusir dan membunuh. Ada pula sebagian lain y ang meng- uasai harta rampasan yang telah dikumpulkan. Ada pula sebagian lain yang menjaga Rasulullah dan tidak berhadapan langsung dengan musuh. Pada malam harinya, selagi sebagian sudah berkumpul dengan sebagian yang lain mereka yang berhasil mengumpulkan harta rampasan berkata, "Kamilah yang telah mengumpulkan dan siapa pun tidak boleh mengusiknya." Sedangkan mereka yang bertugas mengejar musuh menyahut, "Kalian tidak lebih berhak daripada kami. Kamilah yang sebenarnya telah mengumpulkan harta rampasan itu dan mengalahkan musuh." Sedangkan mereka yang bertugas menjaga beliau berkata, "Kami khawatir musuh akan menyerang beliau, maka sejak awal kami melindungi beliau." Maka kemudian Allah menurunkan ayat, JWJT "Mereka menanyakan kepadamu tentang (pembagian) harta rampasan. Katakanlah,'Harta perang itu kepunyaan Allah dan Rasul.
```


---

Mulai ekstraksi sekarang. Output JSON murni saja.
