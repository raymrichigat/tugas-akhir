# Jawaban Antisipasi Pertanyaan Sidang — Genta Putra Prayoga (5025221040)

> Disusun dari isi buku final (`docs/Buku-TA-Genta-fixed.pdf`) + data repo. Tiap jawaban: **inti** (kalimat pembuka aman), **argumen**, dan bila perlu **akui jujur** (keterbatasan yang memang tertulis di buku) + **sitasi** paper dari Daftar Pustaka. Prinsip menjawab: jangan defensif berlebihan — banyak pertanyaan ini menyorot keterbatasan yang **sudah kamu tulis jujur di buku**; akui, jelaskan alasan lingkup, tunjuk future work.

---

## A. Metodologi NER & Evaluasi

### 1. Data uji dipakai memilih best_model tiap iterasi → bukankah itu jadi data validasi & membiaskan F1?
**Inti:** Betul bahwa data uji dipantau tiap iterasi, sehingga secara peran ia berfungsi sebagai acuan pemberhentian. Namun klaim utama tesis ini adalah **perbandingan antar-skenario**, dan bias itu berlaku **seragam** untuk semua skenario sehingga tidak menggeser peringkat.
- **Tidak ada kebocoran gradien.** Data uji tidak pernah masuk pelatihan; bobot model tidak pernah di-update dari token uji. Yang terjadi hanya pemilihan iterasi terbaik berdasarkan skor uji.
- **Protokol identik → komparasi adil.** Baseline, weighted-CE, SCL, JSCL, augmentasi, kelima model, dan POS-tag semuanya memakai split dan prosedur pemilihan yang sama. Jadi kesimpulan "augmentasi > baseline" tidak terpengaruh bias absolut.
- **Akui jujur:** nilai F1 absolut bisa sedikit optimistis karena tidak ada *dev set* terpisah. **Perbaikan:** memisahkan *train/dev/test* tiga arah agar pemilihan model murni pada dev. Ini sudah masuk **Saran** (perketat protokol evaluasi).

### 2. Chunk overlap 1 kalimat → bagaimana pastikan kalimat sama tidak tersebar ke latih & uji?
**Inti:** Pemisahan latih/uji dilakukan pada **tingkat chunk** (bukan kalimat), jadi satu chunk utuh hanya masuk salah satu split.
- Karena tiap chunk overlap **satu kalimat** dengan chunk tetangganya, secara teoretis bila dua chunk bertetangga jatuh di split berbeda, satu kalimat penghubung bisa muncul di kedua sisi.
- **Skala dampak kecil:** overlap hanya 1 kalimat per batas chunk (dari chunk hingga 1.500 karakter), jadi porsi token yang mungkin tumpang-tindih sangat kecil terhadap 49.739 token uji, dan hanya di segelintir batas chunk yang kebetulan terbelah.
- **Akui jujur + perbaikan:** untuk menghilangkan sepenuhnya, split dapat dibuat **berdasarkan blok berurutan** (contiguous split) atau overlap dihapus dari salah satu sisi saat splitting. Dampaknya pada F1 diperkirakan kecil, tapi ini keterbatasan yang sah untuk disebut.

### 3. Anotasi satu peneliti, tanpa IAA / validasi ahli Sirah → bagaimana reliabilitasnya?
**Inti:** Reliabilitas dijaga lewat **konsistensi prosedural**, bukan kesepakatan antar-anotator, mengingat keterbatasan sumber daya penelitian S1.
- **Anotasi semi-otomatis** (gazetteer + pola regex) memberi dasar penandaan yang **konsisten dan dapat direproduksi** — aturan yang sama diterapkan seragam ke seluruh korpus, mengurangi subjektivitas per-token.
- **Pedoman tetap 4 label** (Person/Location/Event/Time) dengan definisi operasional yang jelas di Bab 3.
- **Ground truth uji juga sudah dikoreksi ulang** dan dipakai konsisten untuk semua skenario.
- **Akui jujur:** tanpa anotator kedua, **Cohen's/Fleiss' kappa** tidak dapat dihitung, dan validasi historis oleh ahli Sirah belum dilakukan. **Saran:** anotator kedua + pengukuran *inter-annotator agreement* + verifikasi ahli. Ini keterbatasan yang lazim pada tesis berdomain khusus dan sudah diungkap.

### 4. Kenapa disebut "NER berbasis SRL" padahal tidak ada pengurai predikat–argumen?
**Inti:** "SRL" di sini adalah **kerangka konseptual peran semantik**, bukan implementasi *parser* predikat-argumen klasik. Penamaan mengikuti paper acuan metode.
- Ide yang diambil dari SRL: setiap entitas dilihat dari **perannya dalam peristiwa** — pelaku → Person, tempat → Location, waktu → Time, peristiwa → Event. Ini kerangka "siapa melakukan apa, di mana, kapan" khas SRL.
- Implementasinya = **IndoBERT sequence labeling (BIO) + aturan/kamus untuk seed + iterative self-training**, bukan *dependency/semantic parsing* penuh.
- **Sitasi:** kerangka SRL untuk ekstraksi KG dari teks: **Alam, Gangemi, Presutti & Reforgiato Recupero (2021)**, *Semantic role labeling for knowledge graph extraction from text*. Pendekatan semi-supervised SRL berbasis Transformer pada teks bahasa rendah-sumber: **Ariyanto, Purwitasari, Fatichah, dkk. (2025)**, IEEE Access — **ini paper acuan utama metode**.
- **Akui jujur:** istilah yang lebih presisi memang "**ekstraksi entitas berorientasi peran, berbasis aturan + self-training**". Buku sudah mengoreksi Bab 2 agar SRL diposisikan sebagai landasan konsep, bukan parser.

### 5. Kenapa threshold 0,9 dan maksimum 6 iterasi? Bagaimana mencegah akumulasi error pseudo-label?
**Inti:** Threshold tinggi 0,9 dipilih untuk **menjaga presisi pseudo-label** (hanya prediksi sangat yakin yang jadi label), dan 6 iterasi mengikuti praktik paper acuan sekaligus titik konvergensi empiris.
- **Gerbang 0,9 = rata-rata confidence entitas per chunk.** Chunk hanya diterima bila model sangat yakin; chunk ragu-ragu dibuang, sehingga label berisik tidak masuk pelatihan berikutnya. Inilah mekanisme utama penahan akumulasi error.
- **6 iterasi:** mengikuti konfigurasi paper acuan (Ariyanto/Purwitasari 2025) dan secara empiris kolam data tak-berlabel yang lolos gerbang mengecil hingga hampir habis — penambahan iterasi tak lagi memberi data baru berarti.
- **Akui jujur:** tidak ada mekanisme *noise-correction* eksplisit (mis. relabeling / confidence decay); pertahanan hanya threshold tinggi. **Saran:** eksperimen threshold adaptif atau penyaringan pseudo-label bertingkat.
- **Sitasi:** self-training/semi-supervised untuk NER/SRL bahasa rendah-sumber: **Ariyanto dkk. (2025)**.

### 6. Augmentasi (mention replacement + parafrase) menaikkan F1 0,9536→0,9756 — bagaimana pastikan label tetap valid?
**Inti:** Dua teknik berbeda tingkat risikonya; yang dominan (**mention replacement**) **aman-label secara konstruksi**.
- **Mention replacement:** entitas diganti dengan entitas **berjenis sama** dari kamus (Person↔Person, Location↔Location, dst.). Karena tipe dan posisi span dipertahankan, **label BIO otomatis tetap benar** — batas dan peran tidak berubah.
- **Parafrase:** menyusun ulang kalimat sekitar sambil mempertahankan token entitas; entitas tidak ikut diparafrase sehingga span tetap terlacak.
- **Bukti dampak sehat:** kenaikan tersebar ke **semua kelas** (Tabel distribusi token; Event +198%, Time +67%), dan yang paling terangkat adalah kelas minoritas — pola yang konsisten dengan "menambah ragam contoh", bukan menghafal.
- **Sitasi:** **Dai & Adel (2020)**, *An Analysis of Simple Data Augmentation for NER*; **Chen dkk. (2024)** augmentasi untuk NER medis; **Elwing Torres dkk. (2026)** augmentasi NER domain rendah-sumber.
- **Akui jujur:** validasi parafrase dilakukan secara **sampling manual**, bukan pengecekan otomatis 100%. Untuk parafrase yang berisiko menggeser makna, mention replacement yang jadi tulang punggung perbaikan.

### 7. Jika alignment tokenizer belum setara, apakah komparasi 5 model masih adil?
**Inti:** Ini pertanyaan yang tepat, dan **buku sudah menjawabnya secara jujur**: perbandingan dilakukan **di bawah satu pipeline tetap**, dan defisit cased/RoBERTa **teridentifikasi sebagai artefak penyelarasan label**, bukan bukti model lebih buruk.
- **Bukti bahwa itu artefak, bukan kapabilitas model** (Tabel 4.12–4.14 buku):
  - Defisit **ada sejak model dasar** (base), F1 hanya naik tipis lewat self-training → bukan efek self-training.
  - Terkonsentrasi pada **entitas banyak-kata (Person)**; Location satu-kata tetap tinggi.
  - **Kesalahan batas B/I meledak** (±138 token cased, ±133 RoBERTa vs 7–12 uncased), mayoritas pada Person → ciri khas *misalignment* label kata-ke-subword pada tokenizer cased/BPE.
- **Framing jawaban:** "Perbandingan ini **adil sebagai perbandingan di bawah pipeline yang identik**. Yang tidak adil adalah menyimpulkan model cased/RoBERTa buruk untuk NER Sirah — justru temuannya adalah **pipeline pelabelan perlu disesuaikan** per tokenizer."
- **Saran (sudah di buku):** perbaiki fungsi penyelarasan *word-to-subword* lalu uji ulang agar komparasi kapabilitas benar-benar setara.

---

## B. Knowledge Graph, SNA & Uji Fungsional

### 8. Semua fungsi ada hasil tak-didukung sumber (F5 sebagian kecil terdukung) — atas dasar apa KG disebut layak?
**Inti:** Yang dinyatakan layak adalah **kemampuan struktural/relasional graf**, bukan kesempurnaan presisi tiap sisi. Buku secara jujur memberi tanda "tidak" pada kriteria *sesuai sumber* justru untuk menunjukkan transparansi.
- **Empat kriteria uji fungsional** (Tabel 4.28): (1) eksekusi tanpa galat, (2) hasil tidak kosong, (3) sesuai sumber, (4) terlacak. Keenam fungsi **lolos (1), (2), (4)** — graf **mampu** menjalankan keenam pola penelusuran relasional dan tiap jawaban **dapat ditelusuri** ke evidence + halaman.
- **Kriteria (3) sengaja ketat:** satu fungsi dicap "tidak" bila **ada minimal satu** hasil tak-didukung. Penyebabnya seragam: **over-ekstraksi `INVOLVED_IN` berbasis kedekatan** (mis. Abu Lahab muncul di Perang Badr padahal teks justru menyatakan ia *tidak ikut* — negasi belum ditangani; Madinah sebagai tempat keberangkatan, bukan lokasi peristiwa).
- **Pisahkan dua hal:** *kelayakan graf sebagai struktur penelusuran* (terpenuhi) vs *presisi ekstraksi relasi* (masih perlu diperbaiki). Kelemahannya ada di **kualitas edge**, bukan pada kemampuan graf menjawab.
- **Sitasi kerangka:** **Keet & Khan (2025)**, *Characterising Competency Questions for Ontologies* — pengujian fungsional berbasis pertanyaan kompetensi.
- **Saran:** ekstraksi relasi berbasis **kata kerja/predikat** + penanganan negasi → langsung menaikkan kriteria "sesuai sumber".

### 9. SNA dibangun dari relasi ber-false-positive & mencampur co-participation dengan relasi langsung (keluarga/sahabat/musuh) — bagaimana pastikan bukan artefak?
**Inti:** Justru salah satu kontribusi analisis ini adalah **menunjukkan cara mengenali artefak**, bukan menyembunyikannya.
- **Mitigasi yang sudah diterapkan:** (a) **pembobotan** relasi INVOLVED_IN (threshold weight ≥ 0,3) + (b) **scoping** ke 137 tokoh peserta peristiwa. Setelah keduanya, artefak seperti **Amr bin Umayyah turun dari ~#2 ke #12** PageRank.
- **Validasi balik ke teks** (studi kasus Amr): 3 dari 4 relasinya *false positive*; ini memperlihatkan **prosedur untuk memvalidasi** peringkat, bukan menerimanya buta.
- **Ketahanan hasil utama:** dominasi **Muhammad konvergen di keempat metrik** (degree, closeness, PageRank, betweenness) — kesimpulan sentral tidak bergantung pada satu sisi yang rawan.
- **Akui jujur:** benar bahwa proyeksi menggabungkan co-participation dan relasi eksplisit; ini pilihan desain agar jaringan merepresentasikan "kedekatan struktural". **Saran:** analisis terpisah per-jenis relasi + ekstraksi relasi berbasis kata kerja untuk menekan FP.
- **Sitasi:** metrik sentralitas untuk SNA: **Adniati dkk. (2023)**.

### 10. Q=0,2831 & ARI 0,47 (pemisahan lemah) — seberapa kuat dasar menafsirkan "lingkar Muslim inti"?
**Inti:** Buku **tidak meng-over-claim**: penamaan komunitas dinyatakan **eksplisit sebagai interpretasi peneliti**, bukan label otomatis algoritma, dan harus dibaca bersama bukti teks.
- **Makna Q rendah sudah dibahas:** modularitas 0,2831 berarti **batas antar-kelompok lembut** karena banyak tokoh terhubung lewat peristiwa besar (Badr/Uhud) lintas pihak. Karena itu tokoh Muslim & Quraisy bisa berada di satu komunitas → komunitas mencerminkan **kedekatan struktural via peristiwa bersama**, bukan afiliasi sosial/politik.
- **ARI 0,47** dilaporkan apa adanya sebagai "kesamaan tingkat sedang" antar-algoritma — tidak diklaim tinggi.
- **Framing jawaban:** "Nama 'lingkar Muslim inti' adalah **label deskriptif** dari tokoh yang menonjol di komunitas terbesar (Muhammad, Ali, Umar, Abu Bakar, Aisyah, Utsman), bukan klaim bahwa algoritma menemukan faksi. Interpretasi ini saya baca bersama relasi & bukti teks."
- **Sitasi:** **Anuar dkk. (2024)**, *Identifying Communities with Modularity Metric Using Louvain and Leiden* — dasar penggunaan Louvain + interpretasi modularitas.

---

## C. Chunking & Preprocessing

### 11. Kenapa batas chunk 1.500 karakter, bukan token, padahal IndoBERT bekerja per-token?
**Inti:** Chunking terjadi pada tahap **preprocessing teks** (sebelum tokenisasi), sehingga karakter dipakai sebagai **ukuran praktis** untuk menjaga keutuhan kalimat dan keterbacaan; batas token model ditangani terpisah saat pelatihan.
- 1.500 karakter dipilih sebagai proksi yang **aman di bawah batas 512 token** IndoBERT untuk teks Bahasa Indonesia (rata-rata kata ± beberapa karakter; 1.500 karakter jauh di bawah ambang subword 512).
- Tujuan utama chunking bukan mengepas token, melainkan **mempertahankan konteks kalimat utuh** untuk seed labelling & relasi.
- **Akui jujur:** ukuran token akan lebih presisi terhadap batas model; **verifikasi:** rata-rata token per chunk dapat diperiksa < 512 sehingga tidak ada pemotongan berarti. Bisa jadi butir penyempurnaan.

### 12. Apa yang terjadi bila satu kalimat lebih panjang dari batas maksimum chunk?
**Inti:** Kalimat **tidak dipotong** — keutuhan kalimat diprioritaskan. Bila satu kalimat sendiri melebihi 1.500 karakter, ia menjadi satu chunk tersendiri (boleh melebihi batas), bukan dipenggal di tengah.
- Konsekuensinya sangat jarang karena kalimat Sirah terjemahan umumnya jauh di bawah 1.500 karakter.
- **Akui jujur:** untuk kasus ekstrem, chunk semacam itu bisa melampaui 512 token dan terpotong saat tokenisasi model — dampaknya terbatas pada segelintir kalimat sangat panjang.

### 13. Kenapa overlap hanya 1 kalimat? Apa dasarnya?
**Inti:** Overlap 1 kalimat = **jembatan konteks minimal** di batas chunk, menjaga kalimat pertama sebuah chunk tetap punya rujukan ke kalimat sebelumnya, dengan **redundansi sekecil mungkin**.
- Overlap lebih besar menaikkan duplikasi token (memperbesar risiko double-count relasi & biaya komputasi) tanpa tambahan konteks berarti untuk pelabelan entitas yang bersifat lokal.
- **Akui jujur:** angka 1 adalah pilihan pragmatis, bukan hasil *tuning* sistematis; *ablation* jumlah overlap adalah penyempurnaan yang wajar.

### 14. Bila kalimat overlap muncul dua kali, bagaimana cegah entitas/relasi dihitung ganda di KG?
**Inti:** Pemuatan ke Neo4j memakai **`MERGE`** dengan **constraint keunikan `name`**, sehingga entitas identik → **satu node**, dan triple relasi identik (asal, jenis, tujuan) → **satu edge**.
- **Bukti konkret di buku (§4.5.1):** ekstraksi awal menghasilkan **705 catatan relasi**, tetapi **12 di antaranya duplikat** (kombinasi entitas–jenis–entitas sama, ditemukan di beberapa bagian teks); saat `MERGE`, semua digabung → **693 relasi unik**. Inilah mekanisme anti-double-count yang bekerja.
- **Bukti tidak hilang:** meski digabung, **seluruh evidence tiap kemunculan tetap disimpan** sebagai metadata (provenance ganda).
- **Akui jujur:** pada level **frequency/weight**, kemunculan berulang memang dijumlahkan — itu memang disengaja sebagai sinyal kekuatan relasi, bukan bug.

---

## D. Entitas, Alias & Skema

### 15. Bagaimana bedakan typo OCR dengan variasi nama tokoh yang memang beda?
**Inti:** Dibedakan lewat **kombinasi kemiripan string + kurasi manual**, karena tidak ada aturan otomatis sempurna.
- **Alias clustering (Jaro–Winkler)** menyatukan variasi ejaan yang **sangat mirip** (indikasi typo/variasi transliterasi), sementara nama yang berbeda cukup jauh tetap terpisah.
- Kasus ambigu (mirip tapi mungkin beda orang) **diputuskan manual** dengan melihat konteks penyebutan.
- **Akui jujur:** typo OCR yang menghasilkan bentuk mirip nama lain bisa lolos; ini bagian dari keterbatasan yang menyebabkan sebagian nama langka salah/terlewat (sudah dibahas di analisis error Bab 4).

### 16. Kenapa kabilah/Bani (mis. Bani Quraizhah) diberi label PERSON, padahal bukan individu?
**Inti:** Ini **keputusan desain skema**: aktor kolektif diperlakukan sebagai PERSON karena dalam narasi Sirah mereka **berperan sebagai agen** (melakukan/mengalami peristiwa), sama seperti tokoh individu.
- Dengan skema 4 label, memaksa Bani ke Location/Event akan **salah peran**; PERSON paling dekat dengan fungsinya sebagai pelaku dalam relasi INVOLVED_IN/keluarga/musuh.
- **Akui jujur:** secara ontologis Bani ≠ individu. **Penyempurnaan:** menambah label khusus **GROUP/ORG** untuk memisahkan aktor kolektif dari individu — ini future work yang wajar.

### 17. Bagaimana model bedakan "Badr/Uhud/Khaibar" sebagai lokasi vs peristiwa?
**Inti:** Model mengandalkan **konteks kalimat** (IndoBERT kontekstual), tetapi ini memang **ambiguitas semantik nyata** dalam teks — dan itu **jujur diakui** sebagai sumber utama salah-tipe.
- *Confusion matrix* Bab 4 menunjukkan misklasifikasi tipe terkecil di sistem **justru terkonsentrasi pada pasangan Location↔Event** untuk nama-nama ganda ini. Artinya model umumnya benar, salahnya di titik yang memang ambigu bagi pembaca manusia pun.
- Petunjuk konteks: kata pemicu ("Perang ..." → Event; "di ..." / preposisi tempat → Location) membantu, tapi tidak selalu tersedia.
- **Akui jujur:** ini **ambiguitas bawaan teks**, bukan sekadar kelemahan model. Penanganan lanjut: fitur kata-pemicu eksplisit atau disambiguasi berbasis relasi.

### 18. Kenapa kata ganti (beliau/dia/mereka) tidak jadi Person? Tidak-kah relasi jadi hilang?
**Inti:** Penelitian ini **tidak melakukan penyelesaian koreferensi** — itu dinyatakan di **Batasan Masalah**. Kata ganti bukan nama entitas, jadi tidak ditandai.
- **Konsekuensi diakui jujur:** relasi yang subjeknya berupa kata ganti (mis. "beliau mengutus ...") memang bisa **tidak tertangkap** bila nama eksplisitnya jauh. Ini salah satu penyebab relasi lokasi/waktu tipis.
- **Saran (di buku):** menambahkan **coreference resolution** agar kata ganti dipetakan ke tokoh rujukannya → menambah cakupan relasi.

### 19. Muhammad/Nabi/Rasulullah/beliau — mana yang disatukan, mana yang masih beda?
**Inti:** Varian **nama** disatukan; **kata ganti** tidak.
- **Disatukan ke "Muhammad"** (dari `alias_map.json`): Rasulullah, Nabi Muhammad, Muhammad SAW, Nabi SAW, Muhammad bin Abdullah, dll.
- **Tidak disatukan:** kata ganti **"beliau"** — karena bukan entitas bernama dan tanpa koreferensi tidak dapat dipastikan rujukannya secara aman.
- **Akui jujur:** penyatuan alias bekerja pada bentuk **nama/gelar**, bukan pronomina. Menyatukan "beliau" butuh koreferensi (future work, lihat no. 18).

### 20. Kenapa Jaro–Winkler threshold 0,93? Apa yang terjadi bila dua nama beda mirip di atas ambang?
**Inti:** 0,93 dipilih **tinggi/konservatif** agar hanya varian yang benar-benar mirip yang disatukan, meminimalkan penggabungan salah.
- Jaro–Winkler memberi bobot ekstra pada **kesamaan awalan**, cocok untuk variasi transliterasi Arab-Indonesia yang biasanya beda di akhiran/diakritik.
- **Risiko yang ditanyakan nyata:** dua nama berbeda tetapi ejaannya sangat mirip (mis. berbagi awalan panjang) bisa keliru tergabung bila melewati ambang.
- **Mitigasi:** klaster hasil otomatis **dikurasi manual**, dan basis awal memakai **daftar alias manual** + Jaro–Winkler sebagai pelengkap, bukan satu-satunya penentu.
- **Akui jujur:** 0,93 adalah titik keseimbangan empiris presisi–cakupan, bukan hasil optimasi berlabel; sensitivitas ambang bisa diuji lebih lanjut.

### 21. Nama terpanjang jadi kanonik — apakah selalu paling tepat/paling dikenal?
**Inti:** Tidak selalu. Nama terpanjang dipilih karena **paling lengkap & paling membedakan** (mengurangi ambiguitas antar tokoh sedaerah), bukan karena paling populer.
- Contoh: "Ali bin Abu Thalib" (lengkap) dipilih dibanding "Ali" (umum tapi ambigu dengan Ali lain).
- **Akui jujur:** untuk sebagian tokoh, bentuk **pendek justru lebih dikenal** (mis. "Muhammad" vs bentuk panjangnya) — di kasus itu daftar alias manual meng-override agar kanoniknya bentuk yang lazim. Jadi "terpanjang" adalah **aturan default**, bukan mutlak.

### 22. Kenapa "Madinah" & "Yatsrib" masih dua simpul, padahal sudah ada alias clustering?
**Inti:** Karena alias clustering berbasis **kemiripan penulisan (string)**, sedangkan "Madinah" dan "Yatsrib" adalah **sinonim semantik** (nama lama vs baru) yang **tulisannya sangat berbeda** — Jaro–Winkler-nya rendah, jadi tidak tergabung.
- Ini **jujur diakui di buku** (bagian lokasi/G7): akibatnya dominasi Madinah **ter-*understate***; bila digabung, sentralitasnya makin besar.
- **Penyempurnaan:** kamus **alias semantik** (pengetahuan eksternal/gazetteer relasi sinonim), bukan sekadar kemiripan string.

### 23. Apa beda node TIME dan node PERIOD? Kenapa tidak disatukan?
**Inti:** Keduanya beda **asal** dan **granularitas**:
- **TIME** = keterangan waktu **eksplisit yang diekstrak NER** dari teks (mis. "tahun 2 H", "bulan Syawwal") — entitas hasil model, melekat pada peristiwa lewat `OCCURRED_ON`.
- **PERIOD** = **15 fase kronologis kurasi** (P0–P14) yang **tidak ada sebagai kata di teks**, dibuat untuk **mengelompokkan** peristiwa secara top-down (`IN_PERIOD`) agar bisa ditelusuri per-fase.
- Menyatukannya akan mencampur **entitas terekstraksi** dengan **struktur pengelompokan buatan** yang berbeda tujuan. Pemisahan menjaga kejelasan: TIME untuk waktu spesifik, PERIOD untuk fase besar.

### 24. Dari 901 Person, kenapa hanya 137 masuk proyeksi SNA? Ke mana sisanya?
**Inti:** Proyeksi jaringan **hanya menyertakan tokoh yang terhubung ke minimal satu peristiwa** (atau punya relasi eksplisit keluarga/sahabat/musuh), agar analisis mencerminkan **keterlibatan dalam jaringan sosial-peristiwa**.
- Sisanya (~764 tokoh) umumnya **hanya muncul dalam hubungan nasab/silsilah** atau disebut sekilas tanpa terlibat peristiwa — mereka **tetap ada di knowledge graph**, hanya **dikeluarkan dari tahap analisis** proyeksi.
- **Penyaringan ini hanya di tahap analisis** (bukan menghapus data): KG penuh tetap 901 Person.
- **Justifikasi:** memasukkan tokoh nasab-only akan menambah banyak simpul berderajat rendah yang mengaburkan struktur peristiwa yang jadi fokus SNA.

### 25. Dari OCR/NER/alias/ekstraksi relasi — tahap mana paling banyak memengaruhi hasil akhir KG?
**Inti:** **Ekstraksi relasi (INVOLVED_IN berbasis kedekatan)** adalah penyumbang error paling berdampak ke KG & SNA, jauh lebih besar dari NER.
- **NER relatif kuat** (F1 mikro 0,9756) — kualitas node baik; error tersisa terutama pada **nama langka & artefak OCR** (dampak lokal).
- **Alias clustering** memengaruhi konsolidasi node (mis. Yatsrib–Madinah) — dampak menengah, sebagian tak tertangani (sinonim semantik).
- **Ekstraksi relasi** = titik terlemah: aturan **kedekatan/proximity** menghasilkan **over-ekstraksi** (Abu Lahab "di Badr", Amr bin Umayyah artefak) yang langsung membiaskan sentralitas, komunitas, dan uji fungsional (semua fungsi "tidak sesuai sumber").
- **OCR** = paling hulu; errornya mostly termanifestasi sebagai **kesalahan batas/nama langka** di NER, bukan penggerak utama struktur graf.
- **Kesimpulan jujur & prioritas perbaikan:** urutan dampak ≈ **ekstraksi relasi > NER (entitas langka) > alias > OCR**. Karena itu **saran utama** = ganti/lengkapi relasi proximity dengan **ekstraksi berbasis kata kerja + penanganan negasi**.

---

## Catatan strategi umum saat sidang
- **Jangan bertahan mati-matian pada keterbatasan** — banyak pertanyaan (3, 8, 9, 10, 18, 22, 25) menyorot hal yang **sudah kamu tulis jujur**. Akui, jelaskan *kenapa* itu wajar untuk lingkup S1, tunjuk *future work*. Kejujuran = nilai plus.
- **Bedakan tegas:** kemampuan struktur graf (layak) vs presisi edge (perlu diperbaiki); komparasi antar-skenario (adil) vs nilai absolut (bisa optimistis); kerangka SRL (konsep) vs parser SRL (tidak dipakai).
- **Satu benang merah** yang menyatukan banyak jawaban: **over-ekstraksi `INVOLVED_IN` berbasis kedekatan** → solusinya sama: ekstraksi relasi berbasis kata kerja/predikat + penanganan negasi + koreferensi.
- **Paper acuan metode inti:** Ariyanto, Purwitasari, Fatichah, dkk. (2025, IEEE Access) + Alam dkk. (2021) untuk SRL–KG.
