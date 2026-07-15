# Kartu Contekan Sidang — 1 Layar per Pertanyaan

> Versi kilat dari `jawaban.md`. Format tiap butir: **jurus pembuka** (kalimat aman) → **poin kunci** → *(future work bila perlu)*. Cetak / buka di HP saat sidang.

**3 kalimat penyelamat universal:**
1. "Betul, dan itu sudah saya ungkap sebagai keterbatasan di buku; alasannya lingkup S1, dan saya sarankan ... sebagai pengembangan."
2. "Perlu dibedakan: **kemampuan struktur graf** (layak) vs **presisi tiap sisi** (perlu diperbaiki)."
3. "Akar banyak hal ini sama: **over-ekstraksi `INVOLVED_IN` berbasis kedekatan** → solusi: ekstraksi relasi berbasis **kata kerja + negasi + koreferensi**."

---

## A. NER & Evaluasi
**1. Test dipakai pilih best_model = bias?** → Tak ada kebocoran gradien; protokol **identik untuk semua skenario** → komparasi tetap adil; nilai absolut bisa sedikit optimistis → saran *dev set* terpisah.

**2. Overlap 1 kalimat → bocor latih/uji?** → Split di **level chunk**, chunk utuh hanya 1 sisi; overlap 1 kalimat = porsi token sangat kecil; bisa dihilangkan via *contiguous split*.

**3. 1 anotator, tanpa IAA?** → Konsistensi dijaga **anotasi semi-otomatis (gazetteer+regex)** + pedoman 4 label tetap; **akui** kappa/validasi ahli belum ada → saran anotator kedua + ahli Sirah.

**4. Kenapa disebut "SRL"?** → SRL di sini = **kerangka konsep peran** (pelaku/tempat/waktu/peristiwa), **bukan parser** predikat-argumen; nama ikut paper acuan **Alam 2021** + **Ariyanto/Purwitasari 2025**; implementasi = BERT BIO + aturan + self-training.

**5. Kenapa threshold 0,9 & 6 iterasi?** → 0,9 (rata-rata conf entitas) = **gerbang presisi** penahan error; 6 iter ikut paper acuan + kolam data habis (konvergen); **akui** tak ada noise-correction eksplisit.

**6. Parafrase augmentasi jaga label?** → **Mention replacement** (dominan) ganti entitas **sejenis** → label/batas otomatis aman; parafrase tak menyentuh token entitas; kenaikan merata semua kelas (Event +198%). Paper **Dai & Adel 2020**.

**7. Cased/RoBERTa: komparasi adil?** → Adil **di bawah pipeline sama**; defisitnya = **artefak misalignment label subword** (ada sejak base, meledak di batas B/I Person), **bukan model buruk** → saran perbaiki alignment lalu uji ulang.

## B. KG / SNA / Fungsional
**8. Semua fungsi "tidak sesuai sumber" → kok layak?** → Layak = **mampu jalan + hasil + terlacak** (kriteria 1,2,4 lolos); "tidak" di kriteria 3 karena **FP INVOLVED_IN** (mis. Abu Lahab justru TIDAK ikut Badr). Layak = struktur, bukan presisi edge. Paper **Keet & Khan 2025**.

**9. SNA dari relasi FP → artefak?** → Sudah dimitigasi **pembobotan + scoping** (Amr #2→#12); **validasi balik ke teks** = fitur, bukan cacat; Muhammad dominan di **4 metrik** (tahan). Paper **Adniati 2023**.

**10. Q 0,2831 rendah → dasar "lingkar Muslim inti"?** → Nama = **interpretasi peneliti, bukan label algoritma** (ditulis eksplisit di buku); Q rendah = batas lembut, komunitas = **kedekatan via peristiwa bersama**, bukan faksi. Paper **Anuar 2024**.

## C. Chunking
**11. 1.500 karakter bukan token?** → Chunking di **preprocessing** (sebelum tokenisasi), karakter = ukuran praktis jaga kalimat utuh; 1.500 char ≈ **jauh di bawah 512 token** IndoBERT; batas token ditangani model.

**12. Kalimat > batas chunk?** → Kalimat **tidak dipotong**; jadi 1 chunk tersendiri (boleh melebihi); sangat jarang di teks Sirah.

**13. Kenapa overlap 1 kalimat?** → **Jembatan konteks minimal** di batas chunk + redundansi terkecil; overlap besar = duplikasi tanpa manfaat.

**14. Overlap → hitung ganda di KG?** → **`MERGE` + constraint `name`**: node/edge identik digabung. Bukti buku: **705 catatan → 693 unik** (12 duplikat digabung), evidence tetap disimpan.

## D. Entitas, Alias, Skema
**15. Typo OCR vs variasi nama?** → **Jaro–Winkler + kurasi manual**; kasus ambigu diputus lewat konteks; **akui** sebagian typo bisa lolos.

**16. Bani/kabilah kok PERSON?** → **Keputusan skema**: aktor kolektif berperan sebagai **agen** di narasi (terlibat peristiwa) → paling pas PERSON; **akui** ontologis bukan individu → saran label GROUP/ORG.

**17. Badr/Uhud: lokasi vs peristiwa?** → **Konteks** (IndoBERT) + kata pemicu; ini **ambiguitas nyata teks** → salah-tipe utama = Location↔Event; bukan sekadar kelemahan model.

**18. Kata ganti (beliau) tak jadi entitas?** → **Koreferensi di luar lingkup** (Batasan Masalah); **akui** sebagian relasi hilang → saran tambah coreference resolution.

**19. Muhammad/Nabi/Rasulullah/beliau?** → **Nama/gelar disatukan** ke "Muhammad" (Rasulullah, Nabi SAW, Muhammad SAW, dll. via alias_map); **kata ganti "beliau" tidak** (butuh koreferensi).

**20. Jaro–Winkler 0,93?** → Ambang **tinggi/konservatif** biar hanya varian sangat mirip yang gabung; bobot awalan cocok transliterasi Arab; risiko salah-gabung diredam **kurasi manual**.

**21. Nama terpanjang = kanonik, selalu tepat?** → Tidak; terpanjang = **paling lengkap/membedakan**, bukan paling populer; kasus "Muhammad" dsb. di-override daftar alias manual. Aturan default, bukan mutlak.

**22. Madinah vs Yatsrib kok pisah?** → Alias clustering = **kemiripan string**; Madinah–Yatsrib = **sinonim semantik** (tulisan beda jauh) → tak tergabung; **akui** dominasi Madinah ter-understate → saran kamus alias semantik.

**23. Beda TIME vs PERIOD?** → **TIME** = waktu eksplisit **diekstrak NER** (mis. "tahun 2 H"); **PERIOD** = **15 fase kurasi** (P0–P14) untuk kelompokkan peristiwa top-down. Beda asal & tujuan.

**24. 901 Person tapi 137 di SNA?** → Proyeksi hanya tokoh **terhubung ≥1 peristiwa/relasi eksplisit**; sisanya **nasab-only** → dikeluarkan **dari analisis saja**, tetap ada di KG penuh.

**25. Tahap mana paling banyak error?** → **Ekstraksi relasi** (`INVOLVED_IN` proximity) — paling berdampak (bias sentralitas/komunitas/fungsional). Urutan: **relasi > NER (nama langka) > alias > OCR**. NER sendiri kuat (F1 0,9756).
