# Contekan: Menjelaskan Penanganan Class Imbalance kepada Pak Aldi

> Pegangan saat konsultasi revisi. Fokus pertanyaan Pak Aldi adalah apakah perubahan rasio
> 17,4:1 menjadi 8,8:1 sudah dapat disebut seimbang, bagaimana membedakan augmentasi,
> weighted cross-entropy, dan contrastive learning, serta bagaimana membuktikan bahwa
> teknik yang digunakan benar-benar membantu kelas minoritas.

---

## Jawaban Singkat

> “Betul, Pak. Rasio Person terhadap Event yang berkurang dari 17,4:1 menjadi 8,8:1 belum
> menunjukkan bahwa data telah seimbang. Karena itu, klaimnya saya perbaiki menjadi
> augmentasi **mengurangi ketimpangan antarkelas entitas**, bukan menyeimbangkan seluruh
> distribusi. Keberhasilannya saya nilai dari peningkatan F1 kelas yang lebih jarang, terutama
> Time dari 0,798 menjadi 0,904 dan Event dari 0,934 menjadi 0,954, sementara performa
> Person sebagai kelas entitas terbanyak tetap terjaga.”

Jika ditanya mengenai dominasi token `O`, lanjutkan:

> “Pada tingkat token, kelas `O` tetap dominan, yaitu sekitar 93,5% sebelum augmentasi dan
> 93,0% sesudah augmentasi. Hal ini terjadi karena augmentasi dilakukan terhadap kalimat
> secara utuh sehingga token konteks `O` juga bertambah. Jadi, teknik ini belum menghilangkan
> ketimpangan token `O`, tetapi berhasil mengurangi ketimpangan di antara kelas entitas dan
> meningkatkan kemampuan model mengenali kelas yang lebih jarang.”

---

## Alur Penjelasan

### 1. Akui bahwa rasio belum seimbang

> “Pak Aldi benar bahwa penurunan rasio tidak sama dengan kondisi seimbang. Oleh karena itu,
> kalimat ‘augmentasi menyeimbangkan kelas’ saya ganti menjadi ‘augmentasi mengurangi atau
> menangani ketimpangan antarkelas entitas, meskipun distribusinya masih belum seimbang.’”

Tidak ada ambang universal yang dapat digunakan untuk menyatakan semua dataset sudah
seimbang. Henning et al. (2023) menjelaskan bahwa definisi operasional mengenai seberapa kecil
proporsi suatu kelas sehingga disebut minoritas bergantung pada tugas, dataset, dan jumlah
label. Rasio yang semakin besar menunjukkan ketimpangan yang semakin tinggi, tetapi rasio
tidak harus mencapai tepat 1:1 agar suatu metode dapat memberikan manfaat pada kelas
minoritas.

### 2. Bedakan dua tingkat ketimpangan pada NER

Ketimpangan pada penelitian ini perlu dijelaskan pada dua tingkat:

1. **Ketimpangan token NER**, yaitu token `O` sebagai kelas mayoritas dibandingkan seluruh
   token entitas.
2. **Ketimpangan antarkelas entitas**, yaitu Person sebagai kelas entitas terbanyak dibandingkan
   Event dan Time sebagai kelas entitas yang lebih jarang.

Nemoto et al. menjelaskan bahwa NER memiliki distribusi *long-tail* dengan satu kelas token
mayoritas, yaitu `O`, dan beberapa kelas entitas yang lebih jarang. Oleh karena itu, istilah
“kelas mayoritas” harus digunakan secara hati-hati. `O` adalah kelas mayoritas pada tingkat
token, sedangkan Person adalah kelas terbanyak hanya di antara kelas entitas penelitian ini.

### 3. Tunjukkan perubahan distribusi secara lengkap

| Ukuran distribusi | Sebelum augmentasi | Sesudah augmentasi | Interpretasi |
|---|---:|---:|---|
| Token `O` | 108.815 | 163.352 | Bertambah karena kalimat ditambahkan secara utuh |
| Seluruh token entitas | 7.538 | 12.236 | Contoh token entitas bertambah |
| Rasio `O` : seluruh token entitas | sekitar 14,4:1 | sekitar 13,4:1 | Dominasi `O` hanya sedikit berkurang |
| Proporsi token `O` | sekitar 93,5% | sekitar 93,0% | Distribusi token masih sangat didominasi `O` |
| Rasio Person : Event | sekitar 17,4:1 | sekitar 8,8:1 | Ketimpangan antarkelas entitas berkurang |

Interpretasi yang aman adalah:

> “Augmentasi tidak membuat distribusi token menjadi seimbang karena kelas `O` tetap dominan.
> Namun, augmentasi menambah contoh Event dan Time secara lebih besar secara relatif sehingga
> ketimpangan di antara kelas entitas berkurang.”

### 4. Buktikan manfaatnya melalui performa per kelas

Keberhasilan penanganan ketimpangan tidak dinilai hanya dari perubahan jumlah data. Hasil
per kelas perlu ditampilkan untuk memastikan bahwa kelas yang lebih jarang benar-benar
mengalami peningkatan tanpa penurunan besar pada kelas yang lebih sering muncul.

| Kelas entitas | F1 baseline | F1 augmentasi | Perubahan |
|---|---:|---:|---:|
| Person | 0,969 | 0,984 | +0,015 |
| Location | 0,953 | 0,976 | +0,023 |
| Event | 0,934 | 0,954 | +0,020 |
| Time | 0,798 | 0,904 | **+0,106** |

Berdasarkan angka yang telah dibulatkan tersebut, macro-F1 empat kelas entitas meningkat dari
sekitar 0,914 menjadi 0,955 atau naik sekitar 0,041. Pada naskah final, macro-F1 sebaiknya
dihitung kembali menggunakan nilai asli sebelum pembulatan.

Penjelasan yang dapat digunakan:

> “Peningkatan terbesar terjadi pada Time, yaitu sekitar 0,106. Event juga meningkat sekitar
> 0,020, sedangkan Person dan Location tidak mengalami penurunan. Dengan demikian, manfaat
> augmentasi tidak hanya terlihat dari perubahan rasio, tetapi juga dari peningkatan performa
> kelas entitas yang lebih jarang.”

Hindari kalimat “model menjadi lebih adil”, karena istilah tersebut dapat dianggap sebagai
klaim *algorithmic fairness*. Gunakan “model menjadi lebih baik dalam mengenali kelas yang
lebih jarang.”

### 5. Sandarkan kesimpulan pada literatur secara tepat

> “Henning et al. (2023) mengelompokkan resampling, augmentasi data, dan modifikasi fungsi
> loss sebagai pilihan yang relatif sederhana untuk menangani ketimpangan kelas. Pada
> studi-studi yang mereka tinjau, peningkatan performa yang dilaporkan untuk augmentasi
> cenderung lebih besar daripada resampling atau modifikasi loss. Namun, hasil antarpaper
> tidak dapat dibandingkan secara langsung karena belum terdapat benchmark yang seragam.”

> “Nemoto et al. menunjukkan bahwa evaluasi penanganan imbalance pada NER perlu
> memperhatikan performa kelas entitas tanpa mengabaikan performa kelas `O`. Pada metode
> MoM yang mereka usulkan, performa kelas entitas meningkat tanpa menurunkan performa
> kelas `O`. Dengan prinsip evaluasi yang sama, penelitian ini memeriksa F1 setiap kelas
> entitas setelah augmentasi, bukan hanya perubahan jumlah data.”

Nemoto et al. tidak digunakan sebagai dasar langsung metode augmentasi karena paper tersebut
mengusulkan modifikasi fungsi loss bernama MoM. Paper tersebut digunakan untuk menjelaskan
karakteristik ketimpangan pada NER dan pentingnya menilai performa kelas entitas serta kelas
`O`. Dasar teknik *mention replacement* atau parafrase tetap perlu merujuk pada penelitian
augmentasi NER yang memang menerapkan teknik tersebut.

---

## Perbedaan Tiga Metode yang Diuji

| Metode | Bagian yang diubah | Tujuan utama | Hasil pada penelitian ini |
|---|---|---|---|
| Augmentasi | Data latih | Menambah jumlah dan variasi contoh, terutama pada kelas entitas yang jarang | Memberikan hasil terbaik |
| Weighted cross-entropy | Bobot fungsi loss | Memberikan penalti lebih besar pada kesalahan kelas yang jarang | Meningkatkan false positive dan tidak melampaui baseline |
| Contrastive learning | Ruang representasi | Mendekatkan representasi dengan label sama dan menjauhkan label berbeda | Peningkatannya lebih kecil daripada augmentasi |

Jawaban lisan:

> “Augmentasi bekerja pada data dengan menambahkan contoh baru. Weighted cross-entropy
> tidak menambah data, tetapi mengubah bobot penalti pada fungsi loss. Contrastive learning
> juga tidak mengubah jumlah data secara langsung, melainkan mengatur ruang representasi agar
> contoh berlabel sama lebih dekat. Dalam konfigurasi dan dataset penelitian saya, augmentasi
> memberikan hasil terbaik, tetapi hal tersebut tidak berarti augmentasi selalu menjadi metode
> terbaik untuk seluruh dataset NER.”

---

## Antisipasi Pertanyaan Pak Aldi

| Jika ditanya | Jawaban yang disarankan |
|---|---|
| “Berapa rasio yang disebut seimbang?” | “Tidak ada ambang universal, Pak, karena bergantung pada tugas, dataset, dan label. Rasio mendekati 1:1 menunjukkan distribusi yang lebih setara, tetapi data saya masih timpang sehingga saya tidak menyebutnya seimbang.” |
| “Kalau masih timpang, untuk apa augmentasi?” | “Tujuannya bukan memaksa rasio menjadi 1:1, tetapi menambah contoh kelas yang jarang agar lebih dapat dipelajari. Hal itu terlihat dari kenaikan F1 Time sekitar 0,106 dan Event sekitar 0,020.” |
| “Bukankah kelas mayoritasnya `O`, bukan Person?” | “Benar, Pak. Pada tingkat token, `O` adalah kelas mayoritas. Person hanya merupakan kelas terbanyak di antara empat kelas entitas. Karena itu, saya melaporkan keduanya: rasio `O` terhadap token entitas dan rasio Person terhadap Event.” |
| “Mengapa token `O` ikut bertambah?” | “Augmentasi dilakukan pada kalimat secara utuh agar struktur kalimat dan label BIO tetap valid. Setiap kalimat yang ditambahkan tetap mengandung token konteks `O`, sehingga jumlah `O` ikut meningkat.” |
| “Mengapa Person ikut bertambah?” | “Kalimat yang mengandung Event atau Time sering juga menyebut Person. Ketika kalimat tersebut diaugmentasi, Person dapat ikut bertambah. Namun, Event bertambah lebih besar secara relatif sehingga rasio Person terhadap Event berkurang.” |
| “Apakah berarti augmentasi sudah mengatasi seluruh imbalance?” | “Belum sepenuhnya, Pak. Dominasi token `O` masih tinggi. Kesimpulan saya dibatasi bahwa augmentasi mengurangi ketimpangan antarkelas entitas dan meningkatkan performa kelas yang lebih jarang.” |
| “Mengapa tidak menekan kelas mayoritas?” | “Token `O` tidak dapat dihapus satu per satu karena membentuk konteks dan urutan BIO. Jika pengurangan diperlukan, mekanismenya harus dilakukan pada tingkat pemilihan kalimat atau chunk dengan tetap menjaga distribusi dan konteks.” |
| “Apakah Henning menyatakan augmentasi selalu terbaik?” | “Tidak, Pak. Survei tersebut hanya melaporkan bahwa peningkatan pada studi augmentasi cenderung lebih besar, tetapi juga menegaskan bahwa hasil antarpaper sulit dibandingkan dan bergantung pada tugas.” |
| “Apakah Nemoto menggunakan augmentasi?” | “Tidak. Nemoto mengusulkan metode loss MoM. Saya menggunakan paper tersebut untuk menjelaskan struktur imbalance NER dan pentingnya memantau performa kelas entitas serta kelas `O`, bukan sebagai dasar langsung teknik augmentasi.” |

---

## Contoh Augmentasi yang Perlu Ditampilkan dalam Buku

Contoh berikut harus disesuaikan dengan data augmentasi yang benar-benar dihasilkan oleh
program. Jangan menggunakan contoh buatan apabila kalimat tersebut tidak merepresentasikan
mekanisme implementasi.

### Contoh Mention Replacement

Teks sebelum augmentasi:

> “Rasulullah tiba di Madinah pada bulan Rabiulawal.”

Teks sesudah augmentasi:

> “Abu Bakar tiba di Madinah pada bulan Rabiulawal.”

| Token | Label sebelum | Token pengganti | Label sesudah |
|---|---|---|---|
| Rasulullah | B-PERSON | Abu | B-PERSON |
| — | — | Bakar | I-PERSON |

Penjelasan:

> “Mention replacement mengganti sebuah entitas dengan entitas lain dari kelas yang sama.
> Pergantian dilakukan bersama penyesuaian label BIO sehingga tipe entitas tetap konsisten.
> Token konteks di luar entitas tidak dihapus karena diperlukan untuk mempertahankan struktur
> kalimat.”

Jika metode yang digunakan menargetkan Event atau Time, contoh utama sebaiknya memperlihatkan
pergantian pada kelas tersebut, bukan hanya Person. Hal ini diperlukan agar contoh sesuai dengan
tujuan penguatan kelas minoritas.

---

## Kalimat yang Dapat Dimasukkan ke Buku

> “Ketimpangan kelas pada data NER dianalisis pada dua tingkat. Pada tingkat token, label `O`
> merupakan kelas mayoritas karena mencakup 108.815 token atau sekitar 93,5% dari data sebelum
> augmentasi. Pada tingkat kelas entitas, Person merupakan kelas terbanyak, sedangkan Event dan
> Time memiliki jumlah contoh yang jauh lebih sedikit. Setelah augmentasi, proporsi token `O`
> hanya berubah menjadi sekitar 93,0%, sedangkan rasio token Person terhadap Event berkurang
> dari sekitar 17,4:1 menjadi 8,8:1. Hasil tersebut menunjukkan bahwa augmentasi belum membuat
> distribusi token menjadi seimbang, tetapi berhasil mengurangi ketimpangan di antara kelas
> entitas.”

> “Efektivitas augmentasi selanjutnya dinilai melalui performa per kelas, bukan hanya melalui
> perubahan distribusi data. F1 kelas Time meningkat dari 0,798 menjadi 0,904 dan Event dari
> 0,934 menjadi 0,954. Sementara itu, F1 Person dan Location juga tetap terjaga. Temuan ini
> menunjukkan bahwa penambahan contoh melalui augmentasi membantu model mengenali kelas
> entitas yang lebih jarang pada konfigurasi penelitian ini. Hasil tersebut tidak dimaksudkan untuk
> menyatakan bahwa distribusi telah seimbang atau bahwa augmentasi selalu menjadi metode terbaik
> pada seluruh dataset NER.”

---

## Catatan tentang Gold Standard yang Dikoreksi

Apabila angka hasil berasal dari *gold standard* yang telah dikoreksi, seluruh model dan skenario
harus dievaluasi ulang menggunakan versi data uji yang sama. Koreksi harus didasarkan pada pedoman
anotasi, bukan hanya karena prediksi model berbeda dari label awal. Prosedur koreksi perlu dijelaskan
singkat agar tidak menimbulkan dugaan bahwa label uji diubah untuk menguntungkan model tertentu.

Kalimat yang dapat digunakan:

> “Setelah ditemukan inkonsistensi anotasi pada data uji, koreksi dilakukan berdasarkan pedoman
> anotasi yang sama untuk seluruh kelas. Seluruh skenario kemudian dievaluasi ulang menggunakan
> versi data uji yang telah dikoreksi sehingga hasil tetap dapat dibandingkan secara setara.”

---

## Pernyataan yang Harus Dihindari

- “Data sudah seimbang” atau “data tidak lagi imbalance.”
- “Rasio 8,8:1 sudah termasuk seimbang.”
- “Person adalah kelas mayoritas NER” tanpa menjelaskan bahwa `O` merupakan kelas mayoritas pada tingkat token.
- “Henning membuktikan augmentasi selalu paling efektif.”
- “Nemoto menggunakan augmentasi untuk menyeimbangkan data.”
- “Model menjadi lebih adil terhadap kelas minoritas.”

Gunakan pernyataan berikut:

> “Distribusi masih timpang, khususnya karena dominasi token `O`, tetapi ketimpangan di antara
> kelas entitas berkurang dan performa kelas yang lebih jarang meningkat.”

---

## Rujukan

- Henning, S., Beluch, W., Fraser, A., & Friedrich, A. (2023). *A Survey of Methods for Addressing Class Imbalance in Deep-Learning Based Natural Language Processing*. Proceedings of EACL 2023, 523–540.
- Nemoto, S., Kitada, S., & Iyatomi, H. (2025). *Majority or Minority: Data Imbalance Learning Method for Named Entity Recognition*. IEEE Access, 13. DOI: 10.1109/ACCESS.2024.3522972.

> Catatan: DOI paper Nemoto memuat angka 2024 karena artikel diterbitkan daring pada Desember
> 2024, sedangkan berkas jurnal yang digunakan tercantum dalam IEEE Access Volume 13, 2025.
