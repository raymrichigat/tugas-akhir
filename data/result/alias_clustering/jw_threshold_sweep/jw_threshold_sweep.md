# Justifikasi Empiris Ambang Jaro-Winkler (Bu Ratih #7)

> Sweep ambang pada tahap safety-net JW `alias_clustering.py` (guard sama: compound-prefix, patronymic, rasio panjang, exclude-pairs). Dihasilkan `jw_threshold_sweep.py`.


## Jumlah pasangan yang digabung JW per ambang

| Ambang | Pasangan tergabung |
|---:|---:|
| 0.85 | 359 (default Rayssa) |
| 0.88 | 183 |
| 0.90 | 137 |
| 0.92 | 115 |
| 0.93 | 103 ← **dipakai** |
| 0.95 | 90 |


## Pasangan borderline 0,85 ≤ JW < 0,93 (256 pasangan)

> Inilah pasangan yang **akan ikut tergabung jika ambang diturunkan ke 0,85** tetapi **ditolak pada 0,93**. Kolom `anotasi`: `variasi-sah` = memang satu entitas (tertangkap manual cluster), `?` = perlu diperiksa (kandidat salah-gabung).

| Nama A | Nama B | JW | Label | Anotasi |
|---|---|---:|---|---|
| Al-Abbas bin Abdul Muthalib | Al-Abbas bin Abdul Selain | 0.9299 | PERSON | ? |
| Salaman | Salman | 0.9278 | PERSON | ? |
| Perang Asafan | Perang Safawan | 0.9264 | EVENT | ? |
| Perang Badr Kubra | Perang Badr Ula | 0.9263 | EVENT | ? |
| Utbah bin Rabi'ah | Uthbah bin Rabi' | 0.9253 | PERSON | ? |
| Taimi bin Murrah | Tamim bin Murrah | 0.9222 | PERSON | ? |
| Umayyah bin Zaid | Usamah bin Zaid | 0.9211 | PERSON | ? |
| Al-Abbas bin Abdul Muththalib | Al-Abbas bin Al-Muththalib | 0.9207 | PERSON | ? |
| Al-Aswad bin Abdul Muththalib | Al-Aswad bin Al-Muththalib | 0.9207 | PERSON | ? |
| Perang Tabuk | Perang Yarmuk | 0.9205 | EVENT | ? |
| Perang Buwath | Perang Mu'tah | 0.9203 | EVENT | ? |
| Perang Bu'ats | Perang Mu'tah | 0.9203 | EVENT | ? |
| Ubaid bin Ka'b | Ubay bin Ka'b | 0.9196 | PERSON | ? |
| Perang Khaibar | Perang Khunain | 0.9143 | EVENT | ? |
| Perang Bani Qainuqa' | Perang Bani Quraizhah | 0.9143 | EVENT | ? |
| Abu Dujanah | Ibnu Dujanah | 0.9141 | PERSON | ? |
| Judzamah binti Al-Harits | Ramlah binti Al-Harits | 0.9141 | PERSON | ? |
| Perang Badr | Perang Fijar | 0.9136 | EVENT | ? |
| Perang Abwa' | Perang Ahzab | 0.9133 | EVENT | ? |
| Perang Bani Nadhir | Perang Bani Quraizhah | 0.9114 | EVENT | ? |
| perang Bani Nadhir | perang Bani Quraizhah | 0.9114 | EVENT | ? |
| Yahzan | Yalhan | 0.9111 | PERSON | ? |
| Al-Muth'im bin Adi | Al-Muththalib bin Abdi | 0.9107 | PERSON | ? |
| Abbas bin Abdul Muthalib | Al-Abbas bin Abdul Muthalib | 0.9104 | PERSON | ? |
| Perang Ahzab | Perang Khaibar | 0.9095 | EVENT | ? |
| Utbah bin Ghazwan | Uthbah bin Ghazwan | 0.9068 | PERSON | ? |
| Suhail bin Amr | Thufail bin Amr | 0.9061 | PERSON | ? |
| Sa'd bin Zaid | Sa'id bin Zaid | 0.9026 | PERSON | ? |
| Musafi' bin Thalhah bin Abu Thalhah | Utsman bin Thalhah bin Abu Thalhah | 0.9021 | PERSON | ? |
| Perang Badr | Perang Bu'ats | 0.9021 | EVENT | ? |
| Perang Badr | Perang Bu ats | 0.9021 | EVENT | ? |
| Perang Badr | Perang Yarmuk | 0.9021 | EVENT | ? |
| Al-Abbas bin Al-Muththalib | Al-Aswad bin Abdul Muththalib | 0.9001 | PERSON | ? |
| Perang Ahzab | Perang Tabuk | 0.9000 | EVENT | ? |
| Al-Harits bin Amr | Haritsah bin Amr | 0.8995 | PERSON | ? |
| Malik bin Auf | Salim bin Auf | 0.8974 | PERSON | ? |
| Amir bin Lu'ay | Amr bin Luhay | 0.8969 | PERSON | ? |
| Perang Khunain | Perang Tha'if | 0.8967 | EVENT | ? |
| Perang Khaibar | Perang Tha'if | 0.8967 | EVENT | ? |
| Perang Bani Al-Ashfar | Perang Bani Nadhir | 0.8962 | EVENT | ? |
| Perang Khandaq | Perang Khunain | 0.8961 | EVENT | ? |
| An-Najasyi | An-Nawawi | 0.8956 | PERSON | ? |
| Perang Bani Nadhir | Perang Bani Qainuqa' | 0.8956 | EVENT | ? |
| Jabal Nur | Jabal Uhud | 0.8956 | LOCATION | ? |
| Madinah | Majinnah | 0.8952 | LOCATION | ? |
| Abbad bin Bisri | Abdullah bin Bisri | 0.8944 | PERSON | ? |
| Saru' | Sarugh | 0.8933 | PERSON | ? |
| Perang Bani Mushthaliq | Perang Bani Quraizhah | 0.8929 | EVENT | ? |
| Hudzaifah bin Al-Yaman | Khudzaifah bin Al-Yaman | 0.8924 | PERSON | ? |
| Perang Badr | Perang Uhud | 0.8909 | EVENT | ? |
| Perang Bani Mushthaliq | Perang Bani Nadhir | 0.8897 | EVENT | ? |
| Perang Fijar | Perang Khaibar | 0.8895 | EVENT | ? |
| Ghalib bin Abdullah | Jabir bin Abdullah | 0.8895 | PERSON | ? |
| Perang Abwa' | Perang Tha'if | 0.8885 | EVENT | ? |
| Perang Ahzab | Perang Asafan | 0.8885 | EVENT | ? |
| Perang Ahzab | Perang Tha'if | 0.8885 | EVENT | ? |
| Perang Fijar | Perang Riddah | 0.8885 | EVENT | ? |
| Perang Fijar | Perang Yarmuk | 0.8885 | EVENT | ? |
| Perang Abwa' | Perang Buwath | 0.8885 | EVENT | ? |
| Perang Abwa' | Perang Asafan | 0.8885 | EVENT | ? |
| Perang Tabuk | Perang Tha'if | 0.8885 | EVENT | ? |
| Abdullah bin Al-Mughirah | Abu Umayyah bin Al-Mughirah | 0.8884 | PERSON | ? |
| perang Mu'tah | perang Tha'if | 0.8877 | EVENT | ? |
| Perang Bu ats | Perang Mu'tah | 0.8877 | EVENT | ? |
| Perang Riddah | Perang Tha'if | 0.8877 | EVENT | ? |
| Perang Mu'tah | Perang Tha'if | 0.8877 | EVENT | ? |
| Perang Badr Ula | Perang Bani Nadhir | 0.8870 | EVENT | ? |
| Perang Bani Mushthaliq | Perang Bani Qainuqa' | 0.8867 | EVENT | ? |
| Perang Al-Khandaq | Perang Khaibar | 0.8866 | EVENT | ? |
| Abdul Ka'bah | Abu Kabsyah | 0.8848 | PERSON | ? |
| Al-Harits bin Amir | Haritsah bin Amr | 0.8843 | PERSON | ? |
| Abu Sa'd | Ibnu Sa'd | 0.8843 | PERSON | ? |
| Abu Umar | Ibnu Umar | 0.8843 | PERSON | ? |
| Ummu Qirfah | Ummul Khair | 0.8828 | PERSON | ? |
| Ummu Sa'd | Ummul Fadhl | 0.8828 | PERSON | ? |
| Suhail bin Amr | Syurahbil bin Amr | 0.8828 | PERSON | ? |
| Ummu Hani | Ummul Khair | 0.8828 | PERSON | ? |
| Hammas bin Qais | Haudzah bin Qais | 0.8800 | PERSON | ? |
| Ubaid | Usaid | 0.8800 | PERSON | ? |
| Abqar | Aibar | 0.8800 | PERSON | ? |
| Perang Badr | Perang Riddah | 0.8799 | EVENT | ? |
| Perang Buwath | Perang Uhud | 0.8799 | EVENT | ? |
| Perang Mu'tah | Perang Uhud | 0.8799 | EVENT | ? |
| Perang Riddah | Perang Uhud | 0.8799 | EVENT | ? |
| Najasyi | Nasyid | 0.8794 | PERSON | ? |
| Halimah | Hamzah | 0.8794 | PERSON | ? |
| Perang Badr | Perang Tabuk | 0.8788 | EVENT | ? |
| Perang Ahzab | Perang Uhud | 0.8788 | EVENT | ? |
| Perang Tabuk | Perang Uhud | 0.8788 | EVENT | ? |
| Perang Abwa' | Perang Badr | 0.8788 | EVENT | ? |
| Perang Ahzab | Perang Badr | 0.8788 | EVENT | ? |
| Perang Khaibar | Perang Tabuk | 0.8786 | EVENT | ? |
| Perang Ahzab | Perang Khunain | 0.8786 | EVENT | ? |
| Perang Ahzab | Perang Khandaq | 0.8786 | EVENT | variasi-sah |
| Perang Abwa' | Perang Tabuk | 0.8778 | EVENT | ? |
| Abdullah bin Rabi'ah | Utbah bin Rabi'ah | 0.8775 | PERSON | ? |
| Harb bin Umayyah | Hilal bin Umayyah | 0.8774 | PERSON | ? |
| Ka'b bin Umari | Wahb bin Umair | 0.8770 | PERSON | ? |
| Perang Buwath | Perang Hunain | 0.8769 | EVENT | ? |
| Perang Buwath | Perang Riddah | 0.8769 | EVENT | ? |
| Perang Bu'ats | Perang Hunain | 0.8769 | EVENT | ? |
| Perang Bu ats | Perang Hunain | 0.8769 | EVENT | ? |
| Perang Asafan | Perang Tha'if | 0.8769 | EVENT | ? |
| Perang Hunain | Perang Mu'tah | 0.8769 | EVENT | ? |
| Perang Mu'tah | Perang Riddah | 0.8769 | EVENT | ? |
| Perang Hunain | Perang Tha'if | 0.8769 | EVENT | ? |
| Abdullah bin Abu Bakar | Abdurrahman bin Abu Bakar | 0.8768 | PERSON | ? |
| Perang Khaibar | Perang Riddah | 0.8767 | EVENT | ? |
| Perang Khandaq | Perang Riddah | 0.8767 | EVENT | ? |
| Perang Khunain | Perang Riddah | 0.8767 | EVENT | ? |
| Perang Asafan | Perang Khandaq | 0.8767 | EVENT | ? |
| Perang Badr Ula | Perang Khandaq | 0.8762 | EVENT | ? |
| Asad bin Rabi'ah | Nashr bin Rabi'ah | 0.8757 | PERSON | ? |
| Aishar | Aisyah | 0.8756 | PERSON | ? |
| Dhirar bin Al-Khaththab | Umar bin Al-Khaththab | 0.8752 | PERSON | ? |
| Dhirar bin Al-Khaththab | Uamr bin Al-Khaththab | 0.8752 | PERSON | ? |
| Al-Abbas bin Abdul Muththalib | Al-Aswad bin Al-Muththalib | 0.8751 | PERSON | ? |
| Qushay bin Kilab | Zuhrah bin Kilab | 0.8750 | PERSON | ? |
| Malik bin Murrah | Tamim bin Murrah | 0.8750 | PERSON | ? |
| Perang Dzatur Riqa' | Perang Dzul Usyairah | 0.8746 | EVENT | ? |
| Perang Badr Shughra | Perang Bani Nadhir | 0.8744 | EVENT | ? |
| Abdullah bin Az-Zubair | Abdurrahman bin Az-Zabir | 0.8732 | PERSON | ? |
| Perang Bani Al-Ashfar | Perang Bani Mushthaliq | 0.8728 | EVENT | ? |
| Perang Bani Al-Ashfar | Perang Bani Quraizhah | 0.8724 | EVENT | ? |
| Al-Harits bin Amr | Al-Miqdad bin Amr | 0.8722 | PERSON | ? |
| Mush'ab bin Umair | Wahb bin Umair | 0.8721 | PERSON | ? |
| Perang Badr Kubra | Perang Khaibar | 0.8709 | EVENT | ? |
| Perang Badr Ula | Perang Fijar | 0.8700 | EVENT | ? |
| Perang Badr | Perang Hunain | 0.8685 | EVENT | ? |
| Perang Badr | Perang Mu'tah | 0.8685 | EVENT | ? |
| Perang Bu ats | Perang Uhud | 0.8685 | EVENT | ? |
| Perang Uhud | Perang Yarmuk | 0.8685 | EVENT | ? |
| Perang Badr | Perang Tha'if | 0.8685 | EVENT | ? |
| Perang Tha'if | Perang Uhud | 0.8685 | EVENT | ? |
| Perang Bu'ats | Perang Uhud | 0.8685 | EVENT | ? |
| Dzul Hulaifah | Dzul Marwah | 0.8685 | LOCATION | ? |
| Perang Asafan | Perang Badr | 0.8685 | EVENT | ? |
| Perang Al-Khandaq | Perang Khunain | 0.8684 | EVENT | ? |
| Judzamah binti Al-Harits | Lubabah binti Al-Harits | 0.8676 | PERSON | ? |
| Tamim bin Adi | Zaid bin Adi | 0.8675 | PERSON | ? |
| Perang Badr Shughra | Perang Bani Quraizhah | 0.8674 | EVENT | ? |
| Amr bin Umayyah | Harb bin Umayyah | 0.8674 | PERSON | ? |
| Ummu Jamil | Ummul Khair | 0.8673 | PERSON | ? |
| Ummu Jamil | Ummul Fadhl | 0.8673 | PERSON | ? |
| Ummu Mani' | Ummul Khair | 0.8673 | PERSON | ? |
| Al-Abbas bin Abdul Selain | Al-Aswad bin Abdul Asad | 0.8672 | PERSON | ? |
| Perang Badr Ula | Perang Bu ats | 0.8672 | EVENT | ? |
| Perang Safawan | Perang Tha'if | 0.8670 | EVENT | ? |
| Perang Bu ats | Perang Khunain | 0.8670 | EVENT | ? |
| Perang Bu'ats | Perang Khunain | 0.8670 | EVENT | ? |
| Perang Hunain | Perang Khaibar | 0.8670 | EVENT | ? |
| Perang Khandaq | Perang Tha'if | 0.8670 | EVENT | ? |
| Perang Khaibar | Perang Yarmuk | 0.8670 | EVENT | ? |
| Perang Asafan | Perang Khaibar | 0.8670 | EVENT | ? |
| Syaibah | Syalakh | 0.8667 | PERSON | ? |
| Perang Abwa' | Perang Fijar | 0.8667 | EVENT | ? |
| Perang Khunain | Perang Mu'tah | 0.8667 | EVENT | ? |
| Al-Abbas | Al-Asyaj | 0.8667 | PERSON | ? |
| Perang Ahzab | Perang Fijar | 0.8667 | EVENT | ? |
| Tarih | Zarih | 0.8667 | PERSON | ? |
| Perang Fijar | Perang Tabuk | 0.8667 | EVENT | ? |
| Al-Jurf | Al-Kudr | 0.8667 | LOCATION | ? |
| Iyas bin Mu'adz | Sa'd bin Mu'adz | 0.8667 | PERSON | ? |
| Perang Buwath | Perang Khunain | 0.8667 | EVENT | ? |
| Amir | Amru | 0.8667 | PERSON | ? |
| Perang Badr Kubra | Perang Bani Nadhir | 0.8666 | EVENT | ? |
| Perang Abwa' | Perang Mu'tah | 0.8662 | EVENT | ? |
| Perang Hunain | Perang Tabuk | 0.8662 | EVENT | ? |
| Perang Bu ats | Perang Tabuk | 0.8662 | EVENT | ? |
| Perang Ahzab | Perang Buwath | 0.8662 | EVENT | ? |
| Perang Bu'ats | Perang Tabuk | 0.8662 | EVENT | ? |
| Perang Fijar | Perang Tha'if | 0.8662 | EVENT | ? |
| Perang Buwath | Perang Tabuk | 0.8662 | EVENT | ? |
| Perang Fijar | Perang Hunain | 0.8662 | EVENT | ? |
| Perang Abwa' | Perang Bu'ats | 0.8662 | EVENT | ? |
| Perang Ahzab | Perang Mu'tah | 0.8662 | EVENT | ? |
| Perang Mu'tah | Perang Tabuk | 0.8662 | EVENT | ? |
| Perang Ahzab | Perang Riddah | 0.8662 | EVENT | ? |
| Ummul Fadhl | Ummul Khair | 0.8659 | PERSON | ? |
| Perang Khandaq | Perang Safawan | 0.8657 | EVENT | ? |
| Majdi bin Amr | Mas'ud bin Amr | 0.8655 | PERSON | ? |
| Quraisy bin Kilab | Qushay bin Kilab | 0.8631 | PERSON | ? |
| Al-Harits bin Amir | Al-Miqdad bin Amr | 0.8623 | PERSON | ? |
| Lubabah binti Al-Harits | Ramlah binti Al-Harits | 0.8615 | PERSON | ? |
| Perang Badr Shughra | Perang Bani Mushthaliq | 0.8604 | EVENT | ? |
| Ashim bin Adi | Muth'im bin Adi | 0.8598 | PERSON | ? |
| Ashim bin Adi | Hasyim bin Abdi | 0.8598 | PERSON | ? |
| Mas'ud bin Amr | Mudhadh bin Amr | 0.8596 | PERSON | ? |
| Abbad bin Bisyr | Abdullah bin Bisri | 0.8596 | PERSON | ? |
| Perang Badr Kubra | Perang Khandaq | 0.8593 | EVENT | ? |
| Perang Bani Qainuqa' | Perang Dzatur Riqa' | 0.8588 | EVENT | ? |
| perang As-Sawiq | perang Tha'if | 0.8585 | EVENT | ? |
| Perang Asafan | Perang Badr Ula | 0.8585 | EVENT | ? |
| Perang Badr Ula | Perang Bu'ats | 0.8585 | EVENT | ? |
| Perang Badr Ula | Perang Buwath | 0.8585 | EVENT | ? |
| Perang Badr Ula | Perang Yarmuk | 0.8585 | EVENT | ? |
| Mu'awwidz bin Al-Harits | Ziyad bin Al-Harits | 0.8583 | PERSON | ? |
| Imran bin Amru | Sakran bin Amru | 0.8579 | PERSON | ? |
| Aiham | Aishar | 0.8578 | PERSON | ? |
| Mudhar | Murrah | 0.8578 | PERSON | ? |
| Abdul Ka'bah | Abu Ma'bad | 0.8578 | PERSON | ? |
| Hamdan | Hasan | 0.8578 | PERSON | ? |
| Aibar | Aishar | 0.8578 | PERSON | ? |
| Dhirar bin Al-Khaththab | Umar bin Al-Kahththab | 0.8577 | PERSON | ? |
| Perang Khaibar | Perang Safawan | 0.8571 | EVENT | ? |
| Al-Muhajir bin Abu Umayyah | Al-Muththalib bin Abu Wada'ah | 0.8568 | PERSON | ? |
| Abdu Manaf | Abdul Ka'bah | 0.8567 | PERSON | ? |
| Perang Buwath | Perang Fijar | 0.8564 | EVENT | ? |
| Perang Abwa' | Perang Riddah | 0.8564 | EVENT | ? |
| Perang Ahzab | Perang Yarmuk | 0.8564 | EVENT | ? |
| Perang Bu ats | Perang Fijar | 0.8564 | EVENT | ? |
| Perang Ahzab | Perang Hunain | 0.8564 | EVENT | ? |
| Perang Abwa' | Perang Hunain | 0.8564 | EVENT | ? |
| Perang Riddah | Perang Tabuk | 0.8564 | EVENT | ? |
| Perang Bu'ats | Perang Fijar | 0.8564 | EVENT | ? |
| Perang Abwa' | Perang Bu ats | 0.8564 | EVENT | ? |
| Perang Ahzab | Perang Bu'ats | 0.8564 | EVENT | ? |
| Perang Asafan | Perang Tabuk | 0.8564 | EVENT | ? |
| Perang Fijar | Perang Mu'tah | 0.8564 | EVENT | ? |
| Perang Ahzab | Perang Bu ats | 0.8564 | EVENT | ? |
| Perang Abwa' | Perang Yarmuk | 0.8564 | EVENT | ? |
| Perang Asafan | Perang Fijar | 0.8564 | EVENT | ? |
| Perang Fijar | Perang Khunain | 0.8563 | EVENT | ? |
| Perang Abwa' | Perang Safawan | 0.8563 | EVENT | ? |
| Perang Khunain | Perang Tabuk | 0.8563 | EVENT | ? |
| Perang Abwa' | Perang Khaibar | 0.8563 | EVENT | ? |
| Perang Badr Ula | Perang Khaibar | 0.8562 | EVENT | ? |
| Abu Salamah | Ummu Salamah | 0.8561 | PERSON | ? |
| Al-Miqdad bin Amr | Al-Mundzir bin Amr | 0.8560 | PERSON | ? |
| Perang Al-Khandaq | Perang Bani Al-Ashfar | 0.8552 | EVENT | ? |
| Abdullah bin Abu Umayyah | Al-Muhajir bin Abu Umayyah | 0.8548 | PERSON | ? |
| Perang Asafan | Perang Bu ats | 0.8547 | EVENT | ? |
| Perang Asafan | Perang Bu'ats | 0.8547 | EVENT | ? |
| Perang Mu'tah | Perang Yarmuk | 0.8547 | EVENT | ? |
| Perang Asafan | Perang Hunain | 0.8547 | EVENT | ? |
| Perang Buwath | Perang Yarmuk | 0.8547 | EVENT | ? |
| Perang Buwath | Perang Tha'if | 0.8547 | EVENT | ? |
| Perang Bu'ats | Perang Yarmuk | 0.8547 | EVENT | ? |
| Perang Hunain | Perang Yarmuk | 0.8547 | EVENT | ? |
| Perang Bu'ats | Perang Tha'if | 0.8547 | EVENT | ? |
| Perang Hunain | Perang Riddah | 0.8547 | EVENT | ? |
| Perang Bu ats | Perang Yarmuk | 0.8547 | EVENT | ? |
| Ummu Qirfah | Ummul Fadhl | 0.8545 | PERSON | ? |
| Ummu Ma'bad | Ummul Fadhl | 0.8545 | PERSON | ? |
| Perang Bani Al-Ashfar | Perang Bani Qainuqa' | 0.8538 | EVENT | ? |
| Perang Badr Kubra | Perang Bani Quraizhah | 0.8537 | EVENT | ? |
| Auf bin Al-Harits | Nadhr bin Al-Harits | 0.8535 | PERSON | ? |
| Al-Baihaqi | Al-Barra' | 0.8533 | PERSON | ? |
| Perang Bani Quraizhah | Perang Dzul Usyairah | 0.8529 | EVENT | ? |
| Al-Harits bin Abdi | Al-Muth'im bin Adi | 0.8524 | PERSON | ? |
| Abu Sa'id | Ibnu Sa'd | 0.8519 | PERSON | ? |
| Muth'im bin Adi | Thu'aimah bin Adi | 0.8515 | PERSON | ? |
| perang Al-Yamamah | perang As-Sawiq | 0.8510 | EVENT | ? |
| Gua Hira | Gua Tsur | 0.8500 | LOCATION | ? |
| Ashim bin Tsabit | Zaid bin Tsabit | 0.8500 | PERSON | ? |
| Al-Haisuman bin Abdullah | Al-Harits bin Abdul Uzza | 0.8500 | PERSON | ? |


## Pasangan yang digabung pada ambang 0,93 (103 pasangan)

| Nama A | Nama B | JW | Label | Anotasi |
|---|---|---:|---|---|
| Abul Haitsam bin At-Taihan | Abul Haritsam bin At-Taihan | 0.9926 | PERSON | ? |
| Umar bin Al-Kahththab | Umar bin Al-Khaththab | 0.9905 | PERSON | ? |
| Uqbah bin Abu Mu'aith | Uqbah bin Abu Mu'ith | 0.9905 | PERSON | ? |
| Zaid bin Ad-Dastinah | Zaid bin Ad-Datsinah | 0.9900 | PERSON | ? |
| Salamah bin Al-Akwa | Salamah bin Al-Akwa' | 0.9900 | PERSON | ? |
| Utsman bin Abu Ash | Utsman bin Abul Ash | 0.9895 | PERSON | ? |
| Al-Harits bin Amir | Al-Harits bin Amr | 0.9889 | PERSON | ? |
| Khalad bin Suwaid | Khallad bin Suwaid | 0.9889 | PERSON | ? |
| Sa'd bin Ubadah | Sa'd bin Ubaidah | 0.9875 | PERSON | ? |
| Ilyas bin Mudha | Ilyas bin Mudhar | 0.9875 | PERSON | variasi-sah |
| Hani bin Mas'ud | Hani' bin Mas'ud | 0.9875 | PERSON | ? |
| Mudhadh bin Amr | Mudhadh bin Amru | 0.9875 | PERSON | ? |
| Abdullah bin Uraiqith | Abullah bin Uraiqith | 0.9873 | PERSON | ? |
| Sa'd bin Mua'dz | Sa'd bin Muadz | 0.9867 | PERSON | ? |
| Amar bin Al-Hadhrami | Amr bin Al-Hadhrami | 0.9867 | PERSON | ? |
| Sa'd bin Mu'adz | Sa'd bin Muadz | 0.9867 | PERSON | ? |
| Sa'd bin Mu'adz | Sa'd bin Mua'dz | 0.9867 | PERSON | variasi-sah |
| Sa'd bin Mu'ad | Sa'd bin Mu'adz | 0.9867 | PERSON | variasi-sah |
| Sakran bin Amr | Sakran bin Amru | 0.9867 | PERSON | ? |
| Al-Abbas bin Abdul Muthalib | Al-Abbas bin Abdul Muththalib | 0.9862 | PERSON | ? |
| Imran bin Amr | Imran bin Amru | 0.9857 | PERSON | ? |
| Uamr bin Al-Khaththab | Umar bin Al-Khaththab | 0.9857 | PERSON | ? |
| Sa'ad bin Ubadah | Sa'd bin Ubadah | 0.9854 | PERSON | ? |
| Amr bin Al-Ash | Amru bin Al-Ash | 0.9844 | PERSON | variasi-sah |
| Hathib bin Abi Balta'ah | Hathib bin Abu Balta'ah | 0.9826 | PERSON | ? |
| Az-Zubair bin Al-Awwam | Az-Zubair bin Al-Awwan | 0.9818 | PERSON | ? |
| Ibnu Abbas | Ibnul Abbas | 0.9818 | PERSON | ? |
| Ustman bin Affan | Utsman bin Affan | 0.9812 | PERSON | ? |
| Umar bin Al-Khathab | Umar bin Al-Khaththab | 0.9810 | PERSON | ? |
| Abu Bakar | Abu Bakkar | 0.9800 | PERSON | ? |
| Sa'd bin Abi Waqqash | Sa'd bin Abu Waqqash | 0.9800 | PERSON | variasi-sah |
| Khabbab bin Al-Aratt | Khabbab bin Al-Art | 0.9800 | PERSON | ? |
| Abu Sa'id | Abu Sa'ida | 0.9800 | PERSON | ? |
| Ibnu Haja | Ibnu Hajar | 0.9800 | PERSON | ? |
| Amir bin Sha'sha' | Amir bin Sha'sha'ah | 0.9789 | PERSON | ? |
| Gua Hira | Gua Hira' | 0.9778 | LOCATION | ? |
| Abdullah bin Jahsi | Abdullah bin Jahsy | 0.9778 | PERSON | ? |
| Ibnu Sa'd | Ibnu Sad | 0.9778 | PERSON | ? |
| Asad bin Khuzaimah | Asad bin Khuzainah | 0.9778 | PERSON | ? |
| Abu Dzar | Abu Dzarr | 0.9778 | PERSON | variasi-sah |
| Ibnu Abu | Ibnu Abul | 0.9778 | PERSON | ? |
| Abu Bara | Abu Bara' | 0.9778 | PERSON | ? |
| Abu Sa'id | Abu Said | 0.9778 | PERSON | ? |
| Abu Rafi | Abu Rafi' | 0.9778 | PERSON | ? |
| Abu Raf' | Abu Rafi' | 0.9778 | PERSON | ? |
| Abu Raf' | Abu Raff' | 0.9778 | PERSON | ? |
| Abu Lahab | Abu Lahb | 0.9778 | PERSON | ? |
| Abu Jahal | Abu Jahl | 0.9778 | PERSON | variasi-sah |
| Hadhramaut | Hadramaut | 0.9767 | LOCATION | ? |
| Abu Qasim | Abul Qasim | 0.9767 | PERSON | ? |
| Hassan bin Tsabir | Hassan bin Tsabit | 0.9765 | PERSON | ? |
| Utbah bin Rabi' | Utbah bin Rabi'ah | 0.9765 | PERSON | ? |
| Abu Amir | Abu Amr | 0.9750 | PERSON | ? |
| Tsabit bin Qais | Tsabit bin Qaiz | 0.9733 | PERSON | ? |
| Abbad bin Bisri | Abbad bin Bisyr | 0.9733 | PERSON | ? |
| Hindun binti Utbah | Hindun binti Uthbah | 0.9728 | PERSON | ? |
| Sa'd bin Mu'ad | Sa'd bin Mua'dz | 0.9724 | PERSON | variasi-sah |
| Al-Aqra' bin Habis | Al-Aqra' bin Habislah | 0.9714 | PERSON | ? |
| Sa'd bin Mu' | Sa'd bin Mu'ad | 0.9714 | PERSON | variasi-sah |
| Uamr bin Al-Khaththab | Umar bin Al-Kahththab | 0.9714 | PERSON | ? |
| Sa'd bin Mu'ad | Sa'd bin Muadz | 0.9714 | PERSON | ? |
| Muhammad bin Maslamah | Muhammad bin Salamah | 0.9710 | PERSON | ? |
| Sa'ad bin Ubadah | Sa'd bin Ubaidah | 0.9708 | PERSON | ? |
| Umar bin Al-Kahththab | Umar bin Al-Khathab | 0.9704 | PERSON | ? |
| Ath-Thabarani | Ath-Thabari | 0.9692 | PERSON | ? |
| Perang Bu ats | Perang Bu'ats | 0.9692 | EVENT | ? |
| Perang Bani Quraizhah | perang Bani Quraizhah | 0.9683 | EVENT | ? |
| Perjanjian Hudaibiyah | perjanjian Hudaibiyah | 0.9683 | EVENT | ? |
| Abdullah bin Abu Umayyah | Abdullah bin Umayyah | 0.9667 | PERSON | ? |
| Kurs bin Jabir | Kurz bin Jabir | 0.9667 | PERSON | ? |
| Abu Hurairah | Abu Hurairal | 0.9667 | PERSON | ? |
| Perang Al-Khandaq | Perang Khandaq | 0.9647 | EVENT | variasi-sah |
| Perang Bani Nadhir | perang Bani Nadhir | 0.9630 | EVENT | ? |
| Iyas bin Qubaishah | lyas bin Qubaishah | 0.9630 | PERSON | ? |
| Abdullah bin Jad'an | Abdullah bin Jud'an | 0.9623 | PERSON | ? |
| Yastrib | Yatsrib | 0.9619 | LOCATION | variasi-sah |
| Tha'if | Thaif | 0.9611 | LOCATION | variasi-sah |
| Abu Bakrah | Abu Bara | 0.9600 | PERSON | ? |
| Sa'd bin Mu' | Sa'd bin Mua'dz | 0.9600 | PERSON | variasi-sah |
| Abu Sofyan | Abu Sufyan | 0.9600 | PERSON | variasi-sah |
| Sa'd bin Mu' | Sa'd bin Mu'adz | 0.9600 | PERSON | variasi-sah |
| Abu Sa'ida | Abu Said | 0.9600 | PERSON | ? |
| Abu Sufy | Abu Sufyan | 0.9600 | PERSON | ? |
| As'ad bin Khuzaimah | Asad bin Khuzainah | 0.9571 | PERSON | ? |
| Utbah bin Rabi' | Uthbah bin Rabi' | 0.9567 | PERSON | ? |
| Shafiyah binti Huyai bin Akhthab | Shafiyyah binti Huyai bin Akhthab | 0.9564 | PERSON | ? |
| Aus bin Khaili | Aus bin Khauli | 0.9560 | PERSON | ? |
| Perang Hunain | Perang Khunain | 0.9560 | EVENT | ? |
| Uamr bin Al-Khaththab | Umar bin Al-Khathab | 0.9556 | PERSON | ? |
| Abu Raff' | Abu Rafi' | 0.9556 | PERSON | ? |
| Perang Mu'tah | perang Mu'tah | 0.9487 | EVENT | ? |
| Perang Tha'if | perang Tha'if | 0.9487 | EVENT | ? |
| Khalid bin Al-Walid | Walid bin Al-Walid | 0.9464 | PERSON | ? |
| Amr bin Salamah | Amr bin Salim | 0.9446 | PERSON | ? |
| Al-Muth'im bin Adi | Muth'im bin Adi | 0.9444 | PERSON | ? |
| Zaid bin Haritsah | Zaid binti Haritsah | 0.9437 | PERSON | ? |
| Ali bin Abi Thalib | Ali bin Abu Thalib | 0.9425 | PERSON | variasi-sah |
| An-Nadhar bin Al-Harits | An-Nadhr bin Al-Harits | 0.9413 | PERSON | ? |
| Al-Harits bin Umair | Al-Haritsah bin Umair | 0.9388 | PERSON | ? |
| Perang Bu ats | Perang Buwath | 0.9385 | EVENT | ? |
| Abdullah bin Ubay bin Salul | Abdullan bin Ubay bin Salul | 0.9352 | PERSON | ? |
| Ubaidah bin Al-Harits bin Abdul Muththalib | Ubaidah bin Al-Harits bin Al-Muththalib bin Abdi | 0.9344 | PERSON | ? |
| Nahisy | Nahits | 0.9333 | PERSON | ? |
