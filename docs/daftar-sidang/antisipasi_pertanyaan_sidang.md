# Antisipasi Pertanyaan Sidang — Genta Putra Prayoga (5025221040)

> **Cara pakai.** Tiap pertanyaan diberi **jawaban jujur** (bukan jawaban "biar aman"), memakai angka dari `PPT_konten_terbaru.md` (benchmark done_newest + ground-truth uji terkoreksi + KG v4). Tanda **⚠️** = jebakan lanjutan yang mungkin menyusul. Prinsip: **jujur soal keterbatasan lebih kuat daripada terdengar yakin** — penguji menghargai mahasiswa yang paham batas metodenya.
>
> **Aturan emas saat panik:** kalau tidak tahu, bilang *"Itu belum saya uji secara khusus, tapi indikasinya…"* — jangan mengarang angka atau sumber.

---

## A. METODOLOGI & FRAMING BESAR

### A1. "Kenapa pakai Knowledge Graph? Kenapa tidak database biasa / full-text search saja?"
Karena pertanyaan yang ingin dijawab bersifat **relasional**: "siapa terlibat di peristiwa X", "peristiwa apa di lokasi Y", "urutan kronologi". Full-text search hanya menemukan *kata*, bukan *hubungan* antar-entitas. KG menyimpan relasi secara eksplisit sebagai edge sehingga bisa ditelusuri dengan satu kueri graf (Neo4j), tanpa membaca ulang narasi panjang.

### A2. "Apa kontribusi/kebaruan penelitian ini?"
Jujur, kebaruannya **bukan di algoritma NER** (IndoBERT + self-training sudah ada). Kontribusinya:
1. **Penerapan** pipeline NER semi-supervised ke domain baru: teks Sirah Nabawiyah Bahasa Indonesia yang belum punya dataset NER berlabel.
2. Konstruksi **KG Sirah** end-to-end (OCR → NER → relasi → Neo4j) dengan *provenance* per relasi.
3. **Studi perbandingan** tiga uji coba (penanganan imbalance, komparasi model, fitur POS) pada domain few-shot ini, plus **validasi artefak** sentralitas.
- ⚠️ *Jangan* mengklaim "metode baru". Klaim yang bisa dipertahankan: aplikasi + dataset domain + analisis jujur keterbatasan.

### A3. "Kenapa Sirah Nabawiyah? Apa urgensinya?"
Sirah kaya entitas (tokoh, peristiwa, lokasi, waktu) dan relasi historis, tapi tersaji naratif 633 halaman → sulit ditelusuri relasional. Ini domain Bahasa Indonesia yang belum tergarap sebagai KG. Sumber tunggal: Mubarakfuri terjemahan Kathur Suhardi (supaya konsisten).
- ⚠️ **Sensitif:** kalau ditanya akurasi historis, tekankan penelitian ini **memodelkan apa yang tertulis di buku sumber**, bukan memverifikasi kebenaran sejarah/riwayat. KG merefleksikan teks Mubarakfuri, bukan klaim sejarah independen.

### A4. "Kenapa 4 entitas ini (Person/Location/Event/Time)? Kenapa tidak lebih?"
Empat ini cukup untuk menjawab pertanyaan relasional inti Sirah (siapa–apa–di mana–kapan) dan sejalan dengan struktur naratif kronologis. Menambah tipe (mis. OBJECT/ORG) akan memperbanyak kelas minoritas padahal Event & Time saja sudah *few-shot* — menambah risiko tanpa jelas manfaatnya.

---

## B. "SRL" — INI TITIK PALING RAWAN

### B1. "Ini katanya NER berbasis SRL. Mana Semantic Role Labeling-nya? Mana predikat–argumennya?"
**Ini pertanyaan paling berbahaya. Harus jujur.** Yang diimplementasikan **bukan SRL parser penuh** (predicate–argument seperti PropBank). "SRL" di sini dipakai sebagai **landasan konsep/penamaan**: ide bahwa peran semantik dalam kalimat dipetakan ke tipe entitas — pelaku→Person, tempat→Location, keterangan waktu→Time, peristiwa→Event. Realisasinya lewat **pola regex + gazetteer** untuk *seed labelling*, lalu **IndoBERT BIO tagging + iterative self-training**.
- **Cara jawab:** *"Betul, yang saya bangun adalah NER dengan skema IndoBERT BIO. SRL saya pakai sebagai kerangka konseptual pemetaan peran, bukan sebagai parser SRL penuh. Di Bab 3 sudah saya sebut eksplisit 'bukan pengurai predikat–argumen SRL penuh'."*
- ⚠️ Jangan defensif atau mengaku "salah nama". Bilang ini keputusan penamaan yang **sudah didisclosure** di naskah, dan pipeline nyatanya NER berbasis IndoBERT.
- ⚠️ Kalau penguji menekan "berarti judulnya menyesatkan?" → akui keterbatasan penamaan, tawarkan bahwa yang substantif adalah hasil NER-nya, dan disclosure sudah ada.

### B2. "Kenapa tidak pakai SRL tool yang sudah ada untuk Bahasa Indonesia?"
Tool SRL Bahasa Indonesia yang matang & terbuka sangat terbatas, dan domain Sirah (nama Arab, nasab, kabilah) di luar cakupan tool umum. Pendekatan seed regex/gazetteer + self-training lebih terkontrol untuk domain sempit ini.
- ⚠️ Kalau tak yakin ada/tidaknya tool tertentu, jangan mengarang nama tool. Bilang *"sepengetahuan saya belum ada yang cocok untuk domain ini, perlu dicek lagi."*

---

## C. DATA, PREPROCESSING, PELABELAN

### C1. "Berapa besar data latih vs uji? Kenapa split 70:30?"
Test size 0,3 (default umum untuk dataset kecil supaya test cukup representatif). Data uji: **254 chunk, 49.739 token, 1.969 entitas**. Train seed: 590 chunk. Unlabelled (kolam self-training): 250 chunk.

### C2. "Ground truth-nya siapa yang buat? Bagaimana kualitasnya dijamin?"
Semi-otomatis (gazetteer + regex) → **dikoreksi manual** berpedoman 4 label. Jujur: gold **tidak sempurna**. Sudah ditemukan & diperbaiki masalah:
- **Inkonsistensi kapitalisasi** (dulu: "Perang" kapital → EVENT, "perang" kecil → O).
- **Artefak OCR** (tanda baca menempel di batas entitas).
- Ground truth uji **sudah dikoreksi** (putaran perbaikan dari file misclassified) sebelum angka final dihitung.
- ⚠️ **Karena test ikut dikoreksi, F1 angka baru TIDAK bisa langsung dibandingkan dengan angka run lama.** Kalau ditanya "kok beda dengan slide bimbingan dulu" → jawab: test-nya beda (sudah dikoreksi), jadi perbandingan hanya sah **antar-skenario dalam benchmark yang sama**.

### C3. "Anotasi cuma satu orang? Tidak ada inter-annotator agreement?"
Jujur: ya, anotasi tunggal (keterbatasan sumber daya penelitian S1). Tidak ada IAA formal. Mitigasi: pedoman 4 label + koreksi berlapis + audit ground truth uji.
- ⚠️ Ini keterbatasan sah. Akui, jangan tutupi. Masuk ke "saran": validasi multi-anotator.

### C4. "Kenapa chunk maks 1.500 karakter? Kenapa overlap 1 kalimat?"
1.500 karakter menjaga konteks kalimat utuh (kalimat tidak dipotong) sambil muat di context window model. Overlap 1 kalimat mencegah entitas di batas chunk hilang konteks.

---

## D. NER, SELF-TRAINING, F1

### D1. "F1 di entity level itu mikro atau makro?" ✅ (sudah dibahas)
**Angka headline (mis. augmentasi 0,9756) = F1 MIKRO, entity-level, seqeval.** Seqeval default = micro (jumlahkan TP/FP/FN semua kelas dulu). Slide juga menampilkan **Macro** (0,9543 untuk augmentasi) yang lebih rendah karena memberi bobot sama ke kelas minoritas.
- ⚠️ **"Kenapa tinggi banget?"** → karena micro didominasi PERSON (kelas mayoritas). Cerita sebenarnya di **macro / per-kelas**: Event & Time yang rendah, dan itu yang ditangani augmentasi. Tunjukkan kamu paham micro menyembunyikan kelemahan minoritas.
- ⚠️ Perlu diketahui: di dalam notebook, F1 saat training pakai **sklearn token-level `average='weighted'`** (beda dari headline). Yang dilaporkan di buku/slide = **seqeval entity-level micro**. Jangan tertukar.

### D2. "Kenapa iterasi maksimal 6? Apakah dari paper acuan?" ✅ (sudah dibahas)
`N_ITERATIONS=6` **hard-coded**, warisan dari kode acuan (metode Andrian) — yang selnya ditulis manual dan kebetulan berhenti di iter-6, **bukan** kriteria konvergensi teoretis. Paper aslinya merumuskan "ulangi sampai unlabeled pool habis (S=∅)".
- **Jawab aman:** *"6 mengikuti setup acuan. Secara empiris F1 sudah plateau sebelum iter-6 (winner saya konvergen di iter-4), jadi 6 = batas atas yang cukup, bukan angka ajaib. Idealnya berhenti saat pool habis atau F1 validasi berhenti naik."*
- ⚠️ **"Kalau ditambah jadi 10, lebih bagus?"** → kemungkinan besar tidak signifikan; tersisa ~beberapa chunk keras yang tak pernah lolos threshold. Boleh bilang belum diuji ke-10, tapi indikasi plateau kuat.

### D3. "Kenapa threshold pseudo-label 0,9? Kenapa bukan 0,8 atau 0,95?"
0,9 = kompromi: cukup tinggi supaya pseudo-label andal (kurangi noise masuk ke training), tapi tidak terlalu ketat sampai pool tak pernah tumbuh. Kriterianya: **chunk diterima bila rata-rata keyakinan token entitas ≥ 0,9**.
- ⚠️ **"Kenapa rata-rata, bukan minimum per token?"** → rata-rata lebih toleran; minimum akan menolak chunk hanya karena 1 token ragu. Jujur: ini pilihan desain, belum di-sweep sistematis. (Yang di-sweep adalah λ_C contrastive, bukan threshold.)

### D4. "Apa risiko self-training? Bagaimana mencegah error menumpuk (confirmation bias)?"
Risiko: model memperkuat kesalahannya sendiri (pseudo-label salah → dilatih ulang → makin yakin salah). Mitigasi: **threshold tinggi 0,9** (hanya prediksi sangat yakin jadi pseudo-label) + jumlah iterasi terbatas. Jujur: ini mitigasi, bukan jaminan; tetap ada risiko bias terkonfirmasi terutama untuk kelas minoritas.

### D5. "Kenapa IndoBERT uncased, bukan cased?"
Uji coba 2 menunjukkan uncased justru **lebih stabil** di data ini (F1 0,9536 vs cased 0,7774). Hipotesis: cased memicu masalah penyelarasan label kata-ke-subword (lihat D8). Jujur: pilihan uncased juga berarti **kehilangan sinyal kapitalisasi** — yang sebenarnya relevan karena nama diri sering kapital.
- ⚠️ Ini menarik dua arah; siap jelaskan trade-off-nya.

### D6. "Apa itu augmentasi yang dipakai? Kenapa dia menang?"
**Mention replacement (dominan) + parafrase kalimat** yang menjaga entitas. Menang karena menambah **ragam contoh kelas minoritas**: distribusi entitas naik 4.247 → 6.780 (Event **+198%**, Time +67%). F1 mikro 0,9756, dan lonjakan terbesar di **Time 0,80→0,90**.
- ⚠️ **"Bukankah menaikkan data latih otomatis menaikkan F1 — tidak fair?"** → Semua skenario diuji pada **test set identik**; augmentasi hanya mengubah data latih, jadi ini justru variabel yang diuji. Yang membuat sah: test tidak disentuh.
- ⚠️ **Kejujuran penting:** F1 **Event** tertinggi ada di SCL/JSCL (0,9600), bukan augmentasi (0,9542). Augmentasi menang **secara keseimbangan keseluruhan**, bukan di setiap kelas. Sebut ini duluan sebelum penguji menemukannya.

### D7. "Weighted-CE dan JSCL kok di bawah baseline? Bukannya membobot minoritas harusnya membantu?"
Membobot minoritas membuat model **over-deteksi** (FP naik) tanpa menambah **informasi baru** — model jadi agresif menebak minoritas tapi banyak salah. Augmentasi beda: dia menambah **contoh nyata baru**, bukan sekadar menggeser bobot loss.
- **Insight kunci:** "menambah ragam data > mengubah pembobotan loss" — ini simpulan UC1.

### D8. "Kenapa IndoBERT cased & RoBERTa anjlok drastis (0,78 / 0,81)?"
**Framing wajib: ini INDIKASI artefak penyelarasan label kata-ke-subword, BUKAN bukti model buruk.** Tiga bukti:
1. **Bukan efek self-training** — F1 dari base sudah rendah dan cuma naik tipis (cased 0,7608→0,7770). Defisit **sejak awal**.
2. **Terpusat di entitas banyak-kata** (Person & Time); Location (1 kata) tetap tinggi ~0,87.
3. **Boundary B/I meledak**: 138 token (cased) / 133 (RoBERTa) vs 7–12 di uncased; mayoritas di Person.
- ⚠️ **Gunakan kata "indikasi/mengindikasikan", BUKAN "akar masalah terbukti"** — kamu belum melakukan eksperimen kausal khusus (mis. memperbaiki alignment lalu re-run). Jujur soal ini.
- ⚠️ **Jangan bilang "cased/RoBERTa jelek untuk NER"** — itu salah dan bisa dibantah. Yang benar: pada pipeline INI ada dugaan bug alignment.

### D9. "Kenapa POS-tag tidak (banyak) membantu?"
F1 mikro POS 0,9547 ≈ baseline 0,9536 (selisih **+0,0011**, tanpa multi-seed/uji signifikansi). Per-kelas tidak konsisten arahnya (Time naik 0,80→0,84, tapi Location & Event turun). Kesimpulan: **POS redundan** — IndoBERT kontekstual sudah menyerap petunjuk kelas kata, jadi fitur POS eksplisit tak menambah sinyal.
- ⚠️ **Kejujuran penting:** POS yang dipakai **asli** (dari tagger), bukan placeholder `NN`. Jadi hasil "tidak membantu" ini **sah**, bukan artefak fitur palsu. (Dulu sempat ada isu placeholder — sekarang sudah pakai POS asli.)
- ⚠️ Selisih +0,0011 terlalu kecil untuk klaim "POS lebih baik". Jangan over-claim. Bilang "setara/redundan pada konfigurasi yang diuji".

### D10. "Kalau error didominasi deteksi, bukan salah-tipe — apa artinya?"
Confusion antar-tipe hanya **2–6%** dari error. Artinya model **sudah paham membedakan 4 tipe**; tantangan tersisa = keputusan biner **"ini entitas atau bukan"** (FP over-deteksi + FN terlewat). Ini mengarahkan perbaikan ke boundary/deteksi, bukan ke klasifikasi tipe.

---

## E. KNOWLEDGE GRAPH & SNA

### E1. "Bagaimana relasi INVOLVED_IN dibentuk? Ini yang paling rawan."
Dari **co-occurrence / kedekatan teks** (proximity) antara Person dan Event di chunk yang sama. **Ini kelemahan utama yang harus diakui duluan:** proximity ≠ keterlibatan nyata. Contoh gagalnya: **Abu Lahab–Perang Badr** terbentuk `INVOLVED_IN` padahal evidence menyatakan dia tidak ikut.
- **Jawab proaktif:** *"Ini keterbatasan yang saya sadari dan validasi. Solusi tuntasnya ekstraksi relasi berbasis kata kerja — masuk saran future work."*

### E2. "Apa itu modularitas Q? Kenapa Q=0,2831 dianggap ada komunitas?"
Modularitas Q (Louvain) mengukur seberapa kuat graf terbagi jadi kelompok: seberapa padat koneksi **dalam** komunitas dibanding koneksi **antar** komunitas. Rentang praktis ~0 (acak) sampai ~1. **Q=0,2831 tergolong lemah–sedang**: kelompok masih terlihat tapi "melembut" karena jaringan padat (density 0,199). Jujur: Q ini turun dari angka lama (0,385) karena graf sekarang ber-scope & terbobot berbeda.
- ⚠️ **"Q rendah berarti tidak ada komunitas?"** → bukan tidak ada, tapi batas antar-komunitas kabur karena graf padat berpusat satu tokoh (Muhammad terhubung ke ~108 dari 137). Struktur berpusat-tunggal secara alami menurunkan modularitas.

### E3. "Betweenness kok urutannya beda dari PageRank? Yang mana benar?"
Keduanya benar — mengukur **dimensi berbeda**. PageRank/Degree/Closeness = pengaruh/keterhubungan; Betweenness = peran **jembatan** antar-kelompok. Muhammad teratas di **keempatnya** (konvergen). Tapi peringkat #2 dst berbeda karena tokoh yang "berpengaruh" belum tentu "jembatan".
- ⚠️ **"Kenapa Ummu Kultsum/Husain tinggi di betweenness?"** → **hati-hati, ini mungkin artefak**: jaringan padat + rata-rata lintasan hanya 1,96 + sebagian relasi terpengaruh kedekatan teks. Betweenness selain Muhammad **perlu dibaca hati-hati**. Sudah dicatat sebagai catatan jujur di slide.

### E4. "Amr bin Umayyah — jelaskan kasus artefak ini."
Tanpa pembobotan, dia sempat **#2 PageRank** — mencurigakan (bukan tokoh sentral di literatur Sirah). Validasi balik ke teks: **3 dari 4 relasi INVOLVED_IN-nya false positive** (Badr/Uhud/Tabuk; hanya Khandaq legit). Peran nyatanya: **kurir Nabi ke Najasyi** (sudah benar ter-capture di relasi SAHABAT). Setelah pembobotan + scoping, turun ke **#12**.
- **Ini justru poin kuat:** menunjukkan kamu **tidak menelan output mentah** — kamu validasi ke sumber. Simpulan: **peringkat sentralitas wajib divalidasi balik ke teks.**

### E5. "Kenapa peristiwa daur hidup (kelahiran, wahyu, wafat) tidak muncul sentral?"
Karena mereka disebut lewat **frasa kata kerja/deskriptif** ("beliau wafat", "turunnya wahyu") — bukan proper noun — sehingga **tak tertangkap NER** (yang mendeteksi span nama). Jujur: G4 didominasi peperangan karena bias ekstraksi, **bukan** karena perang lebih penting secara historis.
- ⚠️ **Disclosure penting:** kalau di versi sebelumnya kamu pernah menambah 8 lifecycle events manual — sebut kalau ditanya, itu **bukan pure NER**. Di benchmark v4 sekarang, cek dulu apakah lifecycle di-include atau tidak sebelum menjawab.

### E6. "Perbedaan ukuran studi kasus (Badr 44 tokoh vs Tabuk 4) — apa maknanya?"
Mencerminkan **bias cakupan ekstraksi / porsi liputan teks**, **BUKAN** skala historis sebenarnya. Perang Badr diliput sangat detail di buku → banyak entitas ter-ekstrak. Ini keterbatasan yang harus dinyatakan, bukan temuan tentang "peristiwa mana lebih besar".

### E7. "Yatsrib dan Madinah kan tempat sama — kenapa terpisah?"
Betul, "Yatsrib" = nama lama Madinah, **belum tergabung** di alias clustering lokasi. Ini keterbatasan alias yang jujur diakui → masuk saran (perkuat alias lokasi).

### E8. "Alias clustering-nya bagaimana? Jaro-Winkler itu apa?"
Menyatukan variasi ejaan nama ke bentuk kanonik (mis. Rasulullah→Muhammad). Dua tahap otomatis: **(1) daftar klaster manual** (mayoritas aliasing, ~55+ entri kurasi tangan) + **(2) Jaro-Winkler sebagai safety net** untuk typo/artefak OCR yang lolos. Bentuk kanonik dipilih dari nama **berfrekuensi tertinggi**.
- **Jaro-Winkler** = metrik kemiripan string 0–1 (0 beda total, 1 identik). Jaro menghitung karakter cocok + transposisi; Winkler menambah bonus bila **awalan sama** (prefix maks 4, faktor 0,1) — karena kesalahan ejaan lebih sering di belakang kata. Cocok untuk **nama diri**.
- **Threshold 0,93** — dinaikkan dari 0,85 (acuan) karena nama Arab (Sa'd bin X, Abdullah bin Y) strukturnya mirip tapi beda orang; 0,85 terlalu longgar.
- **JW dijaga berlapis**, bukan cuma threshold: (a) blacklist `EXCLUDE_PAIRS` ~50 pasangan "mirip tapi beda orang"; (b) guard patronim (bagian setelah "bin/binti" harus mirip); (c) guard prefix majemuk (Abu/Ummu/Ibnu); (d) beda level spesifisitas (satu ada "bin", satu tidak) → skip; (e) rasio panjang ≥ 0,80.
- ⚠️ **Jebakan kalau penguji baca kode:** docstring menyebut "3 pendekatan" (manual, pattern matching, JW), tapi kode **hanya jalan 2 tahap** (manual + JW). Pattern-matching nama-pendek→panjang dilakukan **manual di dalam daftar klaster**, bukan stage otomatis terpisah. Jangan klaim "3 tahap otomatis" — bilang **2 tahap otomatis + kurasi manual**.
- ⚠️ Jujur: jalur inference NER (v3/v4) sempat melewatkan tahap alias, dikompensasi script cleanup. Alias belum sempurna — **Yatsrib–Madinah** tidak tergabung (JW menilai kemiripan huruf, bukan makna) → bukti keterbatasan, masuk saran.
- ⚠️ Angka "143 variasi → 109 klaster" dari hasil run lama (`alias_clusters.md`) — konfirmasi ulang sebelum menyebutnya.

### E8b. "Kenapa Jaro-Winkler, bukan Levenshtein?"
Levenshtein = jarak edit (jumlah operasi), tidak ternormalisasi dan tak memberi bobot khusus ke awalan. Jaro-Winkler ternormalisasi 0–1 dan sengaja menekankan **prefix** — asal-usulnya memang untuk pencocokan **nama** (record linkage sensus). Karena variasi nama Sirah biasanya beda di tengah/akhir sementara awalan stabil, Jaro-Winkler lebih pas.
- ⚠️ **Kelemahan JW (akui):** menilai kemiripan **permukaan huruf**, bukan makna → gagal untuk alias yang ejaannya jauh tapi merujuk sama (Yatsrib vs Madinah). Itu sebabnya tetap butuh daftar manual.

---

## F. PENGUJIAN FUNGSIONAL (paling sensitif: 0/6)

### F1. "Hasil uji fungsional 0/6 sesuai konteks — bukankah itu berarti graf-nya GAGAL?"
**Bukan.** 0/6 **bukan** berarti semua jawaban salah. Maknanya: **setiap** fungsi (F1–F6) punya **minimal satu** hasil yang tidak didukung konteks sumber. Kriteria "sesuai penuh" sangat ketat (100% hasil harus benar). Faktanya:
- Kueri berhasil dieksekusi: **6/6 ✓**
- Hasil tidak kosong: **6/6 ✓**
- Dapat ditelusuri ke sumber (provenance): **6/6 ✓**
- Seluruh hasil sesuai konteks: **0/6 ✕** (karena minimal 1 hasil meleset per fungsi)
- **Simpulan yang dipertahankan:** graf **layak untuk eksplorasi/penelusuran awal**, tetapi **belum bisa jadi sumber jawaban mandiri** tanpa verifikasi ke teks. Ini kesimpulan jujur, bukan kegagalan.
- ⚠️ **Jangan** bilang "seluruh fungsi berhasil dipenuhi" (itu angka lama yang salah). Framing baru: **operasional berhasil, ketepatan semantis terbatas.**

### F2. "Kenapa tidak diperbaiki dulu supaya 6/6 sebelum sidang?"
Karena akar masalahnya = **INVOLVED_IN berbasis proximity** (E1), yang solusinya butuh ekstraksi berbasis kata kerja — itu **future work** berskala besar, di luar lingkup TA ini. Melaporkan apa adanya lebih jujur daripada menyembunyikan hasil yang tidak sempurna.

### F3. "[PERIKSA] Angka jumlah hasil tiap kueri (58 tokoh, 10 peristiwa, dst) — sudah dari eksekusi nyata?"
- ⚠️ **CEK SEBELUM SIDANG:** pastikan angka F1–F6 di Backup B5 sudah diisi dari eksekusi nyata `functional_test_queries_bab4.cypher` di Neo4j (setelah import v4_hybrid). Kalau belum dijalankan ulang, **jangan sebut angka spesifik** — bilang "perlu saya konfirmasi dari eksekusi terakhir".

---

## G. PERTANYAAN JEBAKAN UMUM

### G1. "Kalau data uji diperbaiki, apakah semua angka lama di proposal/bimbingan jadi salah?"
Angka lama **tidak salah untuk test lama**, tapi **tidak comparable** dengan angka baru (test-nya beda). Yang berlaku untuk buku/sidang = benchmark terbaru (done_newest + gold terkoreksi). Perbandingan hanya sah **antar-skenario dalam benchmark yang sama**.

### G2. "Model terbaikmu F1 0,9756 — kenapa graf-nya masih banyak salah?"
Karena **NER bagus ≠ KG bagus**. F1 mengukur **deteksi entitas** (span benar). Kesalahan graf datang dari **tahap pembentukan relasi** (proximity INVOLVED_IN), bukan dari NER. Tiga hal beda: kualitas **gold**, kualitas **prediksi entitas**, kualitas **relasi** — F1 tinggi hanya menjamin yang kedua.
- **Insight kunci untuk diucapkan:** *"gold ≠ prediksi ≠ KG — tiga lapisan berbeda."*

### G3. "Apakah hasil ini bisa direproduksi / generalisasi ke buku Sirah lain?"
Reproducible pada **sumber yang sama** (Mubarakfuri/Kathur Suhardi) dengan seed=42. Generalisasi ke sumber lain **belum diuji** dan berisiko: filter halaman, alias, dan numbering bab terikat ke edisi ini. Jujur → masuk saran (uji sumber lain).

### G4. "Kenapa tidak pakai LLM saja (GPT/dsb) untuk NER dan relasi?"
Eksplorasi LLM-NER sempat dilakukan tapi **dibatalkan** (keputusan pembimbing) — fokus penuh ke pendekatan IndoBERT + self-training agar terkontrol, reproducible, dan tidak bergantung API berbayar/black-box. Ekstraksi relasi berbasis kata kerja (bisa via LLM) sudah dicatat sebagai future work.
- ⚠️ Jangan meremehkan LLM; framing: pilihan metodologis untuk kontrol & reprodusibilitas, bukan karena LLM tak mampu.

### G5. "Batasan penelitian ini apa saja?" (siapkan daftar ringkas)
1. Satu sumber buku (tak tergeneralisasi).
2. Anotasi tunggal, tanpa IAA.
3. "SRL" = kerangka konsep, bukan parser penuh.
4. INVOLVED_IN berbasis proximity → rawan artefak.
5. Event daur hidup tak tertangkap (frasa verbal).
6. Uji fungsional: operasional ✓, semantis terbatas.
7. Alias belum lengkap (Yatsrib–Madinah).
- Menyebut batasan dengan lancar = sinyal kamu **menguasai** pekerjaanmu.

### G6. "Kalau disuruh melanjutkan, apa yang pertama kamu perbaiki?"
**Ekstraksi relasi berbasis kata kerja** (ganti INVOLVED_IN proximity dengan predikat tindakan) — karena itu akar dari artefak sentralitas **dan** kegagalan uji fungsional sekaligus. Satu perbaikan, dua manfaat.

---

## H. CHECKLIST FINAL SEBELUM SIDANG

- [ ] **[PERIKSA]** Angka uji fungsional F1–F6 dari eksekusi Neo4j nyata (bukan placeholder).
- [ ] Screenshot Neo4j siap: subgraf Badr, ego Muhammad vs Abu Bakar, komunitas, kesalahan Amr, hasil kueri F1.
- [ ] Hafal 3 angka inti: **aug F1 mikro 0,9756**, **baseline 0,9536**, **POS 0,9547**.
- [ ] Hafal statistik test: **254 chunk / 49.739 token / 1.969 entitas**, imbalance **±17,5:1**.
- [ ] Hafal SNA: **137 node / 1.853 edge / density 0,199 / 8 komunitas / Q 0,2831**.
- [ ] Pastikan **tidak** menyebut angka lama (0,9581 / 15 komunitas / Q 0,385 / 258 chunk).
- [ ] Latih jawaban 3 pertanyaan paling rawan: **B1 (mana SRL-nya)**, **F1 (kenapa 0/6)**, **D8 (cased anjlok)**.
- [ ] Latih kalimat kunci: *"gold ≠ prediksi ≠ KG"* dan *"peringkat sentralitas wajib divalidasi ke teks"*.

---

## LAMPIRAN — PENJELASAN MENDALAM: ALIAS CLUSTERING & JARO-WINKLER

> Bahan penjelasan siap-ucap (untuk mendukung jawaban E8/E8b). Bagian **"Cara ngomong"** = kalimat siap ucap. Semua sudah dicek ke `src/alias_clustering/alias_clustering.py`.

### L.1 Apa masalah yang diselesaikan?

Satu tokoh/tempat/peristiwa di teks Sirah punya **banyak ejaan/sebutan**:
- Muhammad = "Rasulullah", "Nabi Muhammad", "Nabi SAW", "Muhammad bin Abdullah"
- Umar = "Umar bin Al-Khaththab", "Ibnul Khaththab"
- Perang Badr = "Perang Badar" (variasi ejaan)
- + artefak OCR: "Perang Bu'ats" terpotong jadi "Perang Bu" (apostrof hilang)

Kalau tidak disatukan, di Knowledge Graph mereka jadi **node berbeda** padahal orang/tempat yang sama → sentralitas terpecah, graf jadi salah. **Alias clustering** menyatukan semua variasi ke **satu bentuk kanonik** (nama baku).

> **Cara ngomong:** *"Satu tokoh bisa disebut banyak cara di teks. Alias clustering menyatukan variasi-variasi itu jadi satu nama baku, supaya di graf tidak jadi node terpisah-pisah."*

### L.2 Dua tahap otomatis + kurasi manual

**Tahap 1 — Daftar klaster manual (sumber utama aliasing).**
Daftar `{nama_baku: [alias1, alias2, ...]}` untuk PERSON (~55 entri), LOCATION, EVENT. Menangkap alias yang **tak bisa ditebak dari ejaan** — mis. "Rasulullah" → "Muhammad" (mustahil dari kemiripan huruf). Termasuk pemetaan nama pendek → panjang ("Umar" → "Umar bin Al-Khaththab") yang dimasukkan manual.

**Tahap 2 — Jaro-Winkler (safety net).**
Jaring pengaman otomatis untuk **typo & artefak OCR** yang lolos dari daftar manual — mis. "Yatsrib" vs "Yastrib", "Sa'd bin Mua'dz" vs "Sa'd bin Mu'adz". Hanya menyapu variasi ejaan, **bukan** menggabungkan nama yang berbeda.

> **Cara ngomong:** *"Aliasing utamanya dari daftar manual yang saya kurasi. Jaro-Winkler hanya safety net otomatis untuk menangkap typo atau kesalahan OCR yang terlewat."*

> ⚠️ **JANGAN bilang "3 tahap otomatis".** Docstring kode menyebut 3 pendekatan (manual, pattern matching, Jaro-Winkler), TAPI pattern-matching nama-pendek-ke-panjang dilakukan **manual di dalam daftar klaster**, bukan stage otomatis. Yang otomatis = **2 tahap** (manual list + JW).

### L.3 Jaro-Winkler itu apa? (bisa dihafal)

Skor kemiripan dua string, **0 sampai 1** (0 = beda total, 1 = identik). Dua lapis:

**Lapis 1 — Jaro:** mengukur (a) berapa **karakter cocok** dan (b) berapa yang **posisinya tertukar** (transposisi). "Cocok" tidak menuntut posisi persis sama — ada toleransi jarak, jadi tahan terhadap typo.

$$sim_{Jaro} = \tfrac{1}{3}\left(\tfrac{m}{|s_1|} + \tfrac{m}{|s_2|} + \tfrac{m-t}{m}\right)$$

m = karakter cocok, t = transposisi/2, |s| = panjang string.

**Lapis 2 — Winkler:** menambah **bonus kalau awalan (prefix) sama**, karena kesalahan ejaan lebih sering di belakang kata (orang jarang salah huruf pertama nama).

$$sim_{JW} = sim_{Jaro} + \ell \cdot p \cdot (1 - sim_{Jaro})$$

ℓ = panjang prefix sama (maks 4), p = 0,1 (faktor skala).

**Sifat penting:** Jaro-Winkler **selalu ≥ Jaro**, dan pasangan yang awalannya identik dapat dorongan skor terbesar → itulah kenapa cocok untuk **nama diri**.

> **Cara ngomong (versi singkat, tanpa rumus):** *"Jaro-Winkler mengukur kemiripan dua nama dari huruf yang cocok dan urutannya, lalu memberi bonus kalau awalannya sama — karena nama biasanya salah ejaan di belakang, bukan di depan. Skornya 0 sampai 1."*

### L.4 Kenapa threshold 0,93?

Acuan memakai **0,85**. Dinaikkan ke **0,93** karena nama Arab strukturnya sangat mirip padahal orang berbeda — "Sa'd bin Mu'adz", "Sa'd bin Ubadah", "Sa'd bin Abu Waqqash" semuanya berskor tinggi tapi **tiga orang berbeda**. Dengan 0,85 mereka bisa keliru tergabung; 0,93 lebih aman.

> **Cara ngomong:** *"Threshold saya naikkan dari 0,85 ke 0,93 karena banyak nama Arab yang mirip tapi orangnya beda — kalau terlalu longgar, tokoh berbeda bisa keliru digabung."*

> ⚠️ Komentar "0.90" di dalam kode itu basi; konstanta asli **0,93**. Angka acuan "0,85" bersumber dari komentar kode (nama "Rayssa") — **konfirmasi dulu** sumbernya sebelum menyebut sebagai sitasi resmi.

### L.5 Kenapa aman dari salah gabung? (kekuatan yang dipamerkan)

Jaro-Winkler dikenal rawan menggabungkan nama beda yang kebetulan mirip. Dikunci dengan **guard berlapis** — threshold 0,93 hanya langkah TERAKHIR:

1. **Blacklist `EXCLUDE_PAIRS`** — ~50 pasangan "mirip tapi beda orang" di-hardcode (Abu Bakar ≠ Abu Jahal, Zaid bin Haritsah ≠ Zaid bin Tsabit, Perang Badr ≠ Perang Badr Kubra).
2. **Guard patronim** — bagian setelah "bin/binti" harus mirip (kalau patronim beda → orang beda).
3. **Guard prefix majemuk** — untuk "Abu X" vs "Abu Y", bagian pembeda (X vs Y) harus sangat mirip.
4. **Beda level spesifisitas** — satu punya "bin", satu tidak → di-skip (kemungkinan beda orang).
5. **Rasio panjang** — panjang dua nama tidak boleh beda > 20%.

> **Cara ngomong:** *"Jaro-Winkler memang rawan salah gabung, makanya saya kunci dengan daftar hitam pasangan eksplisit, plus pengecekan patronim setelah 'bin', dan rasio panjang nama. Threshold 0,93 cuma langkah terakhir setelah semua pengaman itu."*

### L.6 Kelemahan yang HARUS diakui

Jaro-Winkler menilai **kemiripan huruf di permukaan**, bukan **makna**. Jadi gagal untuk alias yang ejaannya jauh tapi merujuk sama:
- **"Yatsrib" vs "Madinah"** — nama lama vs baru kota yang sama, huruf jauh berbeda → **tidak tergabung otomatis**, dan memang belum dimasukkan manual.

Itu sebabnya daftar manual tetap wajib — dan alias belum 100% lengkap. Masuk **saran future work** (perkuat alias lokasi).

> **Cara ngomong:** *"Keterbatasannya, Jaro-Winkler hanya lihat kemiripan huruf, bukan makna. Contohnya Yatsrib dan Madinah itu kota sama tapi ejaannya jauh, jadi tidak tergabung — ini saya catat sebagai perbaikan ke depan."*

### L.7 Contoh konkret dengan SKOR NYATA

> Skor dihitung dengan fungsi `jaro_winkler()` asli dari `alias_clustering.py` (bukan reimplementasi). Threshold gabung = **0,93**.

| Nama A | Nama B | Jaro | prefix | **JaroWinkler** | ≥0,93 | Hasil akhir |
|---|---|---:|---:|---:|:--:|---|
| Perang Badr | Perang Badar | 0,9722 | 4 | **0,9833** | ✓ | digabung |
| Fathul Makkah | Fathu Makkah | 0,9744 | 4 | **0,9846** | ✓ | digabung |
| Abu Sufyan | Abu Sofyan | 0,9333 | 4 | **0,9600** | ✓ | digabung |
| Yatsrib | Yastrib | 0,9524 | 2 | **0,9619** | ✓ | digabung |
| Utsman | Ustman | 0,9444 | 1 | **0,9500** | ✓ | digabung |
| Khalid bin Al-Walid | Khalid bin Walid | 0,9161 | 4 | **0,9497** | ✓ | digabung |
| Perang Badr | Perang Badr Kubra | 0,8824 | 4 | **0,9294** | ✕ | TIDAK (di bawah 0,93 + guard panjang + blacklist) |
| Sa'd bin Mu'adz | Sa'd bin Ubadah | 0,8222 | 4 | **0,8933** | ✕ | TIDAK (di bawah 0,93 + blacklist) |
| Abu Bakar | Abu Jahal | 0,7778 | 4 | **0,8667** | ✕ | TIDAK (di bawah 0,93 + blacklist) |
| Sa'd bin Mu'adz | Sa'd bin Abu Waqqash | 0,7611 | 4 | **0,8567** | ✕ | TIDAK (di bawah 0,93) |
| Rasulullah | Muhammad | 0,4472 | 0 | **0,4472** | ✕ | digabung via **daftar manual** (JW tak bisa) |
| Yatsrib | Madinah | 0,5238 | 0 | **0,5238** | ✕ | TIDAK tergabung (makna sama, huruf jauh) |

**Tiga pelajaran dari angka ini (siap diucapkan):**
1. **Efek bonus Winkler terlihat** — "Perang Badr/Badar" naik dari Jaro 0,9722 → JW 0,9833 karena 4 huruf awal sama. Winkler mengangkat pasangan berawalan sama.
2. **Threshold 0,93 saja sudah menolak mayoritas "beda orang"** — pasangan Sa'd (0,89 & 0,86) dan Abu Bakar/Jahal (0,87) jatuh di bawah 0,93 tanpa perlu blacklist. Blacklist = pengaman ganda.
3. **"Perang Badr Kubra" berskor 0,9294 — nyaris lolos!** Inilah bukti kenapa guard tambahan (rasio panjang + blacklist) penting: ada kasus mirip-tapi-beda yang skornya menempel di ambang.
4. **Alias semantik (Rasulullah→Muhammad = 0,4472; Yatsrib↔Madinah = 0,5238) mustahil ditangkap JW** → membuktikan daftar manual wajib ada.

> ⚠️ Angka di atas hasil hitung nyata per (skrip `compute_jw.py`). Kalau ditanya di sidang, ini bisa dipertanggungjawabkan.

### L.8 Ringkas 30 detik (satu tarikan napas)

*"Alias clustering menyatukan variasi nama jadi satu nama baku supaya tidak jadi node terpisah di graf. Utamanya pakai daftar manual yang saya kurasi; Jaro-Winkler — skor kemiripan string 0–1 yang memberi bonus kalau awalan nama sama — hanya jadi safety net otomatis untuk typo dan OCR, dengan threshold ketat 0,93 plus daftar hitam pasangan mirip-tapi-beda-orang. Keterbatasannya, dia hanya lihat huruf bukan makna, jadi Yatsrib dan Madinah belum tergabung."*

### L.9 Contoh HITUNG PENUH (kalau penguji minta "coba hitungkan")

> Contoh: **"Utsman" vs "Ustman"** (typo tukar huruf). Angka di bawah cocok dengan hasil hitung nyata: Jaro **0,9444** → JW **0,9500**.

**Ide dasar 2 lapis:** Jaro = seberapa banyak huruf cocok + seberapa berantakan urutannya. Winkler = bonus kalau awalan sama.

```
U t s m a n   ← s1 (Utsman)
U s t m a n   ← s2 (Ustman)
```

**Lapis 1 — Jaro:**
- **A. Panjang:** keduanya 6 huruf.
- **B. Jendela pencocokan:** ⌊max(6,6)/2⌋ − 1 = 3 − 1 = **2** (huruf boleh geser ≤2 posisi masih dianggap cocok).
- **C. Huruf cocok (m):** semua 6 huruf punya pasangan dalam jendela → **m = 6**.
- **D. Transposisi (t):** bandingkan urutan huruf cocok — posisi ke-2 (t vs s) dan ke-3 (s vs t) tertukar → 2 huruf salah posisi → **t = 2÷2 = 1**.
- **E. Rumus:**

$$Jaro = \frac{1}{3}\left(\frac{m}{|s_1|} + \frac{m}{|s_2|} + \frac{m-t}{m}\right) = \frac{1}{3}\left(\frac{6}{6} + \frac{6}{6} + \frac{6-1}{6}\right) = \frac{2{,}8333}{3} = \mathbf{0{,}9444}$$

**Lapis 2 — Winkler (bonus awalan):**
- **F. Prefix sama (maks 4):** huruf ke-1 U=U ✓, huruf ke-2 t≠s ✗ → **prefix = 1**.
- **G. Rumus** (p = 0,1):

$$JW = Jaro + \ell \cdot p \cdot (1 - Jaro) = 0{,}9444 + 1 \times 0{,}1 \times (1 - 0{,}9444) = \mathbf{0{,}9500}$$

→ JW 0,9500 **≥ 0,93** → digabung sebagai satu tokoh.

**Kontras — "Rasulullah" vs "Muhammad" = 0,4472:** hampir tak ada huruf cocok dalam jendela + awalan beda (R vs M) → prefix 0, tak ada bonus. **Bukti kenapa alias semantik WAJIB lewat daftar manual** — JW mustahil menangkapnya.

> **Cara ngomong:** *"Jaro-Winkler menghitung berapa huruf cocok dan berapa yang tertukar posisinya, lalu memberi bonus kalau awalan sama. Contohnya 'Utsman' dan 'Ustman' — semua huruf cocok tapi satu pasang tertukar, skornya 0,9444, naik jadi 0,9500 karena huruf awal sama; karena di atas 0,93, keduanya digabung."*

---

## LAMPIRAN — PERHITUNGAN METRIK EVALUASI NER

> Untuk menjawab pertanyaan "dari mana angka F1 itu", "bedanya micro dan macro", "kenapa tinggi/rendah". Semua rumus di bawah **sudah diverifikasi cocok** dengan angka slide (skrip cek: macro = rata-rata F1 per-kelas → match persis untuk Baseline/Augmentasi/POS).

### M.1 Rumus dasar (Precision, Recall, F1)

$$P = \frac{TP}{TP+FP} \qquad R = \frac{TP}{TP+FN} \qquad F1 = \frac{2PR}{P+R} = \frac{2\,TP}{2\,TP + FP + FN}$$

- **TP** (True Positive) = entitas yang diprediksi **benar** (batas + tipe sama persis dengan gold)
- **FP** (False Positive) = model memprediksi entitas yang **tidak ada** di gold (over-deteksi)
- **FN** (False Negative) = entitas gold yang **terlewat** model (tidak terdeteksi)
- **F1** = rata-rata harmonik P & R (menghukum ketimpangan; F1 tinggi hanya jika P **dan** R sama-sama tinggi)

> **Cara ngomong:** *"Precision = dari semua yang saya tebak entitas, berapa yang benar. Recall = dari semua entitas asli, berapa yang berhasil saya tangkap. F1 = rata-rata harmonik keduanya."*

### M.2 Kunci: evaluasi **entity-level (seqeval)**, bukan token-level

Angka headline saya pakai **seqeval span-based**: satu entitas dihitung **TP hanya jika BATAS (span) DAN TIPE cocok persis**. Kalau model menebak "Muhammad" padahal gold "Nabi Muhammad" → **salah**, walau tipenya benar (PERSON). Ini lebih ketat daripada token-level.

> **Cara ngomong:** *"Saya evaluasi di tingkat entitas, bukan per-token. Jadi kalau batas namanya meleset satu kata saja, itu sudah dihitung salah — lebih ketat dan lebih jujur untuk NER."*

### M.3 Contoh hitung konkret (kalimat mainan)

Kalimat: *"Nabi Muhammad hijrah ke Madinah pada tahun kedua Hijriah"*

| Gold (benar) | Prediksi model | Status |
|---|---|---|
| `Nabi Muhammad` = PERSON | `Muhammad` = PERSON | ✕ batas beda → **1 FN + 1 FP** |
| `Madinah` = LOCATION | `Madinah` = LOCATION | ✓ **1 TP** |
| `tahun kedua Hijriah` = TIME | `tahun kedua` = TIME | ✕ batas beda → **1 FN + 1 FP** |
| — | `hijrah` = EVENT | ✕ tak ada di gold → **1 FP** |

Rekap: **TP = 1, FP = 3, FN = 2**

$$P = \frac{1}{1+3} = 0{,}25 \qquad R = \frac{1}{1+2} = 0{,}33 \qquad F1 = \frac{2(1)}{2(1)+3+2} = 0{,}29$$

**Pelajaran:** walau model dapat **tipe** yang benar untuk hampir semua (PERSON, TIME, LOCATION), kesalahan **batas** dan **over-deteksi** menjatuhkan skor. Ini persis temuan utamamu: *error didominasi keputusan deteksi/boundary, bukan salah tipe.*

### M.4 Micro vs Macro (INI yang sering ditanya)

Setelah TP/FP/FN dihitung per-kelas (Person, Location, Event, Time), ada dua cara merangkum:

**MICRO** = jumlahkan **dulu** TP/FP/FN semua kelas, **baru** hitung F1.
$$P_{micro} = \frac{\sum TP}{\sum TP + \sum FP}, \quad \text{dst.}$$
→ Setiap **entitas** berbobot sama → **didominasi kelas mayoritas** (Person = 1.302 dari 1.969 entitas test). **Ini angka headline (mis. 0,9756).**

**MACRO** = hitung F1 **per-kelas dulu**, lalu **rata-rata biasa** (bobot sama tiap kelas).
$$F1_{macro} = \frac{F1_{Person} + F1_{Location} + F1_{Event} + F1_{Time}}{4}$$
→ Setiap **kelas** berbobot sama → kelas minoritas (Event, Time) **ikut menentukan** → **lebih rendah**.

**Verifikasi nyata (augmentasi):**
$$F1_{macro} = \frac{0{,}9835 + 0{,}9755 + 0{,}9542 + 0{,}9038}{4} = 0{,}9543 \;\checkmark \text{ (persis angka slide)}$$

> **Cara ngomong:** *"Micro menjumlahkan semua entitas dulu, jadi didominasi Person yang paling banyak — makanya tinggi, 0,9756. Macro merata-ratakan per-kelas, jadi Event dan Time yang sulit ikut menyeret turun ke 0,9543. Selisih micro–macro itu justru ukuran seberapa timpang performa antar-kelas."*

### M.5 Kenapa selisih micro–macro itu PENTING diceritakan

| Skenario | F1 micro | F1 macro | Selisih | Makna |
|---|---:|---:|---:|---|
| Baseline | 0,9536 | 0,9136 | **0,040** | jomplang — minoritas (Time 0,80) tertinggal jauh |
| Augmentasi | 0,9756 | 0,9543 | **0,021** | selisih **mengecil** → minoritas terangkat (Time 0,90) |

**Inilah bukti kuantitatif klaim UC1:** augmentasi bukan cuma menaikkan micro (+0,022), tapi **mempersempit jurang micro–macro** dari 0,040 → 0,021. Artinya perbaikan **merata ke kelas minoritas**, bukan cuma menebalkan kelas mayoritas.

> **Cara ngomong (poin pamungkas):** *"Yang membuktikan augmentasi berhasil bukan cuma micro-nya naik, tapi jarak micro ke macro menyempit — artinya kelas minoritas yang tadinya tertinggal ikut terangkat."*

### M.6 Antisipasi pertanyaan metrik

- **"Kenapa lapor micro sebagai angka utama?"** → Standar seqeval + mencerminkan performa keseluruhan pada distribusi nyata. Tapi saya **selalu dampingi dengan macro + per-kelas** supaya kelemahan minoritas tidak tersembunyi.
- **"F1 0,97 itu kan tinggi, berarti sudah bagus?"** → Untuk **deteksi entitas** ya; tapi F1 tinggi **tidak menjamin KG benar** — kesalahan graf datang dari tahap relasi (proximity), bukan NER. (lihat G2: gold ≠ prediksi ≠ KG)
- **"Kenapa tidak pakai akurasi (accuracy)?"** → Accuracy menyesatkan untuk data timpang: karena mayoritas token = "O" (bukan entitas), model yang menebak semua "O" bisa dapat accuracy tinggi tanpa menemukan satu entitas pun. F1 (entity-level) tidak tertipu itu.
- **"Rata-rata harmonik, kenapa bukan aritmatika?"** → Harmonik menghukum ketimpangan: kalau P=1,0 tapi R=0,1, rata-rata aritmatika 0,55 (menyesatkan), harmonik hanya 0,18 (jujur). Memaksa **kedua** metrik tinggi.
