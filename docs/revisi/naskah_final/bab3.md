# Naskah final — BAB 3 (siap copas)

## A. Ganti istilah "alias clustering" → "normalisasi alias"
Ganti di Subbab 3.7.1, Gambar 3.8, Kode Semu 3.8, dan seluruh narasi. Kalimat pembuka subbab:

> Penyatuan variasi nama entitas dilakukan melalui normalisasi alias, yaitu pemetaan berbagai
> variasi penulisan nama ke satu bentuk kanonik. Proses ini memanfaatkan daftar padanan yang
> disusun manual serta ukuran kemiripan string Jaro-Winkler sebagai pengaman, kemudian
> divalidasi manual. Jaro-Winkler di sini berperan sebagai ukuran kemiripan string, bukan sebagai
> algoritma clustering, sehingga keluarannya berupa peta alias, bukan klaster yang dievaluasi.

## B. Contoh Chunking (subbab chunking)

Teks setiap sub-bab dipecah menjadi potongan (chunk) berukuran paling banyak 1500 karakter dengan
mempertahankan batas kalimat, sehingga tidak ada kalimat yang terpotong di tengah. Antar chunk
diberi tumpang tindih (overlap) berupa satu kalimat, yaitu kalimat terakhir suatu chunk diulang
sebagai kalimat pertama chunk berikutnya, agar konteks pada batas antar chunk tidak terputus.
Metadata bab, sub-bab, dan halaman dipertahankan pada setiap chunk. Sebagai contoh, sub-bab
"Kekuasaan di Berbagai Penjuru Arab" (halaman 53–54) yang melebihi 1500 karakter dipecah menjadi
dua chunk. Kalimat "Sehingga adakalanya jika seorang pemimpin murka, sekian ribu mata pedang akan
ikut berbicara tanpa perlu bertanya apa yang membuat pemimpin kabilah itu murka." menjadi kalimat
overlap: kalimat tersebut menutup chunk pertama dan sekaligus membuka chunk kedua.

## C. Definisi Token, Subtoken, Chunk, Batch (subbab tokenisasi)

Perlu dibedakan empat istilah berikut. Chunk adalah potongan teks yang dapat memuat beberapa
kalimat dan menjadi unit yang diberikan ke model. Token atau kata adalah unit hasil tokenisasi awal
yang diberi label BIO. Subtoken adalah pecahan token yang dihasilkan tokenizer WordPiece IndoBERT
dan menjadi unit yang benar-benar diproses model. Batch adalah kumpulan beberapa sequence yang
diproses bersamaan pada satu langkah pelatihan. IndoBERT melakukan klasifikasi token atas satu
urutan token yang memiliki konteks, bukan mengklasifikasikan setiap kata secara terpisah. Panjang
maksimum sequence adalah 512 subtoken.

Karena satu kata dapat dipecah menjadi beberapa subtoken, label BIO yang berada pada tingkat kata
diselaraskan ke tingkat subtoken dengan aturan berikut: hanya subtoken pertama dari setiap kata
yang diberi label, sedangkan subtoken lanjutan dan token khusus ([CLS] dan [SEP]) diberi nilai -100
sehingga diabaikan oleh fungsi kerugian. Sebagai contoh, kata "Umair" dipecah menjadi subtoken
"uma" dan "##ir"; hanya "uma" yang menerima label I-PERSON, sedangkan "##ir" diberi -100. Penyelarasan
ini diimplementasikan menggunakan fungsi word_ids() dari tokenizer.

## D. Dasar Ambang Co-occurrence 200 Karakter (subbab pembentukan relasi)

Dua entitas dianggap berada dalam konteks yang sama apabila berada pada kalimat yang sama atau
berjarak kurang dari 200 karakter satu sama lain. Ambang 200 karakter didasarkan pada karakteristik
korpus. Panjang kalimat pada korpus memiliki median 100 karakter dan sekitar 84,9% kalimat berada
pada 200 karakter atau kurang, sehingga jendela 200 karakter kira-kira menampung satu kalimat penuh
beserta sedikit margin ke kalimat tetangga. Selain itu, sekitar 82,7% pasangan entitas yang
berurutan dalam satu chunk berjarak kurang dari 200 karakter. Kedekatan juga menentukan bobot relasi
secara bertingkat, yaitu 0,4 untuk jarak kurang dari 50 karakter, 0,3 untuk kurang dari 100
karakter, dan 0,2 untuk kurang dari 200 karakter. Dengan demikian, tidak seluruh entitas dalam satu
sub-bab otomatis dihubungkan, melainkan hanya yang memenuhi syarat konteks tersebut. Ambang 200
karakter ini merupakan heuristik yang diadaptasi untuk korpus naratif Sirah.

Sebagai contoh relasi yang benar, kalimat "Abdurrahman bin Auf menuturkan, 'Tatkala aku sedang
berada di tengah barisan pada Perang Badr…'" menghasilkan relasi keterlibatan Abdurrahman bin Auf
pada Perang Badr yang didukung konteks satu kalimat. Sebaliknya, relasi dapat keliru pada tiga pola:
adanya negasi (misalnya "Abu Lahab tidak ikut serta" pada Perang Badr), penyebut yang merupakan
perawi dan bukan pelaku, serta penyebutan peristiwa lain yang kebetulan berdekatan.

## E. Prosedur Pengujian Validitas Semantis (subbab evaluasi fungsional)

Selain memeriksa keterlaksanaan kueri, setiap hasil yang dikembalikan oleh keenam fungsi diperiksa
kesesuaiannya terhadap teks sumber. Unit pemeriksaan mengikuti bentuk keluaran tiap fungsi: pada
F1–F4 berupa pasangan entitas dan relasi; pada F5 berupa jalur tokoh, peristiwa, dan lokasi yang
dinyatakan sesuai hanya apabila kedua relasi pada jalur tersebut didukung teks sumber; dan pada F6
berupa pasangan peristiwa dengan relasi mendahului. Karena satu lokasi pada F5 dapat dicapai melalui
beberapa jalur, unit penilaian adalah 21 jalur yang dikembalikan kueri, bukan 15 lokasi unik. Suatu
hasil dinyatakan valid apabila potongan bukti pada halaman sumber secara langsung mendukung hubungan
yang terbentuk, dan dinyatakan tidak valid apabila bukti menyangkal hubungan, hanya menyebutkan
entitas secara berdekatan, atau merujuk peristiwa lain. Jawaban yang hanya benar sebagian
diperlakukan sebagai tidak valid agar penilaian bersifat ketat. Pemeriksaan dilakukan secara manual
oleh penulis dengan merujuk ke teks terjemahan Al-Mubarakfuri. Sebagai keterbatasan, pemeriksaan
dilakukan oleh satu orang sehingga tidak terdapat pengukuran kesepakatan antar-anotator.

## F. Penanganan Negasi sebagai Keterbatasan

Pembentukan relasi berbasis kedekatan tidak memeriksa negasi. Akibatnya, kalimat yang menyatakan
ketidakterlibatan dapat tetap menghasilkan relasi keterlibatan. Sebagai contoh, kalimat "Saat
Perang Badr, Abu Lahab tidak ikut serta" tetap menghasilkan relasi Abu Lahab terlibat pada Perang
Badr. Deteksi negasi tidak diterapkan pada penelitian ini dan dinyatakan sebagai keterbatasan.

## G. Dasar Pemilihan Hyperparameter (subbab pelatihan model)

Nilai hyperparameter tidak ditetapkan secara sembarang, melainkan diadopsi sebagai nilai awal dari
penelitian acuan yang menangani tugas sejenis, yaitu NER berbasis IndoBERT dengan iterative
self-training pada bahasa Indonesia berdaya rendah (Ariyanto dkk., 2025), lalu diterapkan dan diuji
kembali pada dataset Sirah Nabawiyah. Learning rate 2e-5 dipilih karena merupakan nilai yang umum
efektif untuk model berbasis transformer dan cukup kecil untuk menjaga kestabilan pelatihan. Batch
size 16 dipilih untuk mengoptimalkan pemakaian memori GPU tanpa mengorbankan efisiensi. Pelatihan
dilakukan selama 10 epoch dengan early stopping untuk mencegah overfitting, disertai weight decay
0,01 untuk memperbaiki generalisasi. Ambang confidence 0,9 digunakan pada penyaringan pseudo-label;
pada penelitian acuan, ambang 0,7, 0,8, dan 0,9 telah dibandingkan dan 0,9 memberikan hasil terbaik
karena hanya menerima prediksi berkepercayaan tinggi. Confidence sebuah prediksi dihitung sebagai
rata-rata skor confidence seluruh token dalam teks. Adapun jumlah iterasi self-training dibatasi
maksimal enam iterasi sebagai titik henti praktis karena peningkatan F1 sudah landai; batasan ini
merupakan penyesuaian pada penelitian ini, bukan berasal dari penelitian acuan.

## H. Alur NER ke Knowledge Graph dengan Satu Contoh (subbab konstruksi KG)

Alur konstruksi ditelusuri melalui satu contoh data yang sama. Dari chunk pada halaman 165–168,
kalimat "Tatkala Abu Jahal mengajaknya pergi saat Perang Badr…" ditokenisasi dan diberi label BIO,
sehingga "Abu Jahal" berlabel B-PERSON dan I-PERSON serta "Perang Badr" berlabel B-EVENT dan
I-EVENT. Hasil ekstraksi menghasilkan dua entitas, yaitu Abu Jahal bertipe Person dan Perang Badr
bertipe Event. Kedua nama dinormalisasi ke bentuk kanonik melalui normalisasi alias. Karena kedua
entitas berada dalam satu kalimat, keduanya menjadi pasangan kandidat relasi. Pasangan Person dan
Event dipetakan menjadi relasi INVOLVED_IN dengan bobot sesuai kedekatan. Selanjutnya dibentuk
simpul Abu Jahal dan simpul Perang Badr beserta sisi INVOLVED_IN di antaranya, lalu disimpan ke
Neo4j. Relasi ini tetap dapat ditelusuri ke halaman sumber melalui properti bukti.

## I. Protokol Koreksi Manual (subbab pelabelan)

Pelabelan awal dilakukan secara semi-otomatis menggunakan kamus entitas dan pola ekspresi reguler,
kemudian diperiksa kembali melalui satu pass review manual untuk memperbaiki kualitas anotasi. Cara
semi-otomatis cepat tetapi menghasilkan kesalahan sistematis, yaitu entitas yang terlewat, batas
entitas yang salah, kesalahan tipe (terutama nama yang dapat berupa lokasi atau peristiwa), entitas
palsu, dan nama yang terpecah akibat artefak OCR. Contoh perbaikan meliputi "India" yang semula
tidak teranotasi menjadi Location, kata "610" pada "610 M" yang dimasukkan sebagai bagian entitas
Time, "peperangan Badr" yang semula Location diperbaiki menjadi Event, penyebutan pada rujukan kitab
seperti "bab Ghazwah Dzatu Qarad" yang dibatalkan menjadi bukan entitas, serta "Mush ab" yang
disambung menjadi "Mush'ab". Koreksi mengacu pada pedoman anotasi yang mengunci keputusan pelabelan
dan diterapkan pada satu sumber kebenaran di tingkat span. Koreksi dilakukan oleh penulis sebagai
anotator tunggal, sehingga tidak terdapat anotator kedua maupun pengukuran kesepakatan antar-anotator;
hal ini dinyatakan sebagai keterbatasan.
