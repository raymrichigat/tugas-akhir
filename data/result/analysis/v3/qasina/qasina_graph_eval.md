# Studi Kasus QASiNa → Knowledge Graph v3

> Dihasilkan oleh `src/analysis/qasina_graph_eval.py`. Menjawab pertanyaan Bu Diana (bimbingan 2026-05-30): *apakah pertanyaan QASiNa bisa dijawab menggunakan graf?*

## ⚠️ Cara baca metrik (penting)

- **HIT = graf BERPOTENSI menjawab** — jawaban gold muncul di antara kandidat 1-hop dari entitas yang ter-link. Ini **upper-bound recall**, BUKAN akurasi sistem QA. Tanpa ranking, satu event bisa punya banyak kandidat PERSON → hit cenderung longgar/optimistis.

- Tujuan utama bukan skor, tapi **kategori miss** = penjelasan KENAPA graf bisa/tidak bisa menjawab tiap tipe pertanyaan.

- **Caveat sumber:** QASiNa kemungkinan dari teks Sirah berbeda dari buku Mubarakfuri (sumber KG ini) → mismatch string jawaban wajar.


## 1. Ringkasan keseluruhan

- Total pertanyaan diuji: **500**
- Potensi terjawab (HIT): **48** (**9.6%** upper-bound)

## 2. Per tipe pertanyaan

| Tipe | N | HIT | % HIT |
|---|---:|---:|---:|
| who | 226 | 38 | 16.8% |
| where | 38 | 1 | 2.6% |
| when | 20 | 0 | 0.0% |
| what | 178 | 9 | 5.1% |
| how many | 38 | 0 | 0.0% |

## 3. Kenapa gagal — distribusi alasan (keseluruhan)

| Alasan | Jumlah | % |
|---|---:|---:|
| HIT | 48 | 9.6% |
| answer_not_in_candidates | 145 | 29.0% |
| no_candidate_of_type | 216 | 43.2% |
| no_entity_linked | 53 | 10.6% |
| type_unsupported(how_many) | 38 | 7.6% |

**Arti tiap alasan:**
- `HIT` — jawaban ada di kandidat graf (potensi terjawab).
- `answer_not_in_candidates` — entitas ter-link & ada kandidat, tapi jawaban gold tidak termasuk → granularitas/relasi KG tak menyimpannya (mis. role spesifik 'yang mempersiapkan').
- `no_candidate_of_type` — entitas ter-link tapi tak punya relasi ke tipe target (mis. event tanpa OCCURRED_ON untuk pertanyaan 'kapan').
- `no_entity_linked` — tak ada node KG yang cocok dgn pertanyaan/judul → entitas/konteks di luar cakupan KG (mis. Romawi-Persia, pendidikan karakter).
- `type_unsupported(how_many)` — graf tak menyimpan kuantitas.

## 4. Breakdown alasan per tipe

**who** — no_candidate_of_type=105, answer_not_in_candidates=53, HIT=38, no_entity_linked=30
**where** — no_candidate_of_type=29, answer_not_in_candidates=5, no_entity_linked=3, HIT=1
**when** — no_candidate_of_type=14, answer_not_in_candidates=5, no_entity_linked=1
**what** — answer_not_in_candidates=82, no_candidate_of_type=68, no_entity_linked=19, HIT=9
**how many** — type_unsupported(how_many)=38

## 5. Contoh HIT (graf berpotensi menjawab)

- [who] *Siapa yang menjadi penyebab terjadinya perang Badar Kubra?* → gold: **Sariyah Abdullah Ibn Jahsy** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang diutus oleh Nabi untuk mengintai Quraisy?* → gold: **Abdullah ibn Jahsy** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa saja yang tersesat di daerah Ma'dan?* → gold: **Sa'd Ibn Abul Waqash dan Utbah ibn Ghazawan** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang memimpin kafilah Quraisy yang datang dari arah Syam menuju Mekkah?* → gold: **Abu Sufyan** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Syam(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa saja nama-nama orang Quraisy yang tergabung dalam rombongan kafilah Quraisy?* → gold: **Makhramah Ibn Naufal dan Amr Ibn Al-Ash ibn Wa'il ibn Hisyam** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang mensunnahkan sahabatnya untuk menghalangi kafilah Quraisy?* → gold: **Muhammad** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang sangat takut dan mengumpulkan Quraisy agar menyelamatkan rombongannya?* → gold: **Abu Sufyan** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang Abu Sufyan perintahkan untuk mengumpulkan Quraisy dan menyelamatkan rombongannya?* → gold: **Ibn Amr Al-Ghifari** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Abu Sufyan bin Harb(PERSON) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa yang bermimpi tiga malam sebelum kedatangan diam-diam?* → gold: **Atikah binti Abdul Muttalib** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [who] *Siapa saudara Atikah yang diceritakan mimpi tersebut?* → gold: **Al-Abbas** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar

## 6. Contoh MISS — `answer_not_in_candidates` (granularitas KG)

- [when] *Kapan perang Badar terjadi?* → gold: **tahun kedua** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Bulan Syawwal 2 Hijriyah | Bulan Dzul Hijjah | Bulan Jumadal | Bulan Rabi'Ul Awwal | Jumadil Ula | Tahun 3 H
- [what] *Apa saja macam-macam perang Badar yang terjadi?* → gold: **perang badar pertama, perang badar kubra, dan perang badar yang terakhir (Ghazwah al-Sawiq)** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Hijrah Ke Madinah | Perang Uhud | Perang Badr
- [who] *Siapa yang mempersiapkan perang Badar sebenarnya?* → gold: **Abu Ubaidah Amir ibn Al-Jarah** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [what] *Apa yang terdapat dalam rombongan unta Quraisy?* → gold: **Amr ibn Al-Khadlrami, Utsman ibn Al-Mughirah, Naufal, Al-Hakam Ibn Kisan, dan Ukasyah Ibn Mihshan** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Hijrah Ke Madinah | Perang Uhud | Perang Badr
- [when] *Kapan para sariyah Islam melakukan perundingan?* → gold: **akhir Rajab** | link: Perang Badr(EVENT) | Badr(LOCATION) | kandidat: Bulan Syawwal 2 Hijriyah | Bulan Dzul Hijjah | Bulan Jumadal | Bulan Rabi'Ul Awwal | Jumadil Ula | Tahun 3 H
- [where] *Dimana Abu Sufyan mencari tau tentang keberadaan sahabatnya dan Nabi Muhammad?* → gold: **dekat Hijaz** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Abu Sufyan bin Harb(PERSON) | Muhammad(PERSON) | Muhammad Bin Ka'B(PERSON) | kandidat: Yatsrib | Madinah | Makkah | Badr | Hijir | Habasyah | Tihamah
- [who] *Sahabat diinstruksikan oleh Rasulullah untuk menghalangi siapa?* → gold: **Quraisy** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Rasululah(PERSON) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [what] *Apa reaksi Abu Sufyan setelah mengetahui bahwa sahabat Nabi akan menghalangi kafilahnya?* → gold: **sangat takut** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Abu Sufyan bin Harb(PERSON) | kandidat: Hijrah Ke Madinah | Perang Uhud | Perang Badr | Perang As-Sawiq | Perang Sawiq
- [who] *Siapa yang memberitahu keadaan rombongan Abu Sufyan?* → gold: **dlamdlam** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | Abu Sufyan bin Harb(PERSON) | kandidat: Amr bin Al-Ash | Najasyi | Ja'Far | Muhammad | Abu Jahal | Abu Sufyan bin Harb | Abu Rasulullah | Abu Bakar
- [when] *Kapan peristiwa ini terjadi?* → gold: **pada hari senin malam kedelapan bulan Ramadhan** | link: Perang Badr(EVENT) | Perang Badr Kubra(EVENT) | Badr(LOCATION) | kandidat: Bulan Syawwal 2 Hijriyah | Bulan Dzul Hijjah | Bulan Jumadal | Bulan Rabi'Ul Awwal | Jumadil Ula | Tahun 3 H

## 7. Contoh MISS — `no_entity_linked` (di luar cakupan KG)

- [what] *Apa nama lain dari Masjid Aqsha?* (ctx: Masjid Aqsha di Bait al-Maqdis (1)) → gold: **Bait al-Maqdis**
- [what] *Apa yang dilambangkan ketika Nabi menjadi imam shalat untuk seluruh para Rasul di Masjid Aqsha?* (ctx: Masjid Aqsha di Bait al-Maqdis (1)) → gold: **persamaan dasar dan kontinuitas agama Allah**
- [who] *Siapa yang disebut sebagai nabi dua Qiblat?* (ctx: Masjid Aqsha di Bait al-Maqdis (1)) → gold: **Muhammad**
- [what] *Apa yang dijelaskan dalam surat al Isra' 4-8?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **perjalanan Masjid Aqsha**
- [where] *Dimana keterangan mengenai perjalanan Masjid Aqsha diangkat dalam al-Qur'an?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **surat al Isra' 4-8**
- [what] *Apa yang ditakdirkan bagi Anak cucu Isra'il dalam Kitab?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **membuat kerusakan di muka bumi ini dua kali**
- [who] *Siapakah yang dikirim oleh Allah pada saat hukuman bagi kedua kejahatan itu?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **hamba-hamba Kami yang mempunyai kekuatan yang besar**
- [what] *Apa yang terjadi pada kedua pengerusakan yang ditakdirkan bagi Anak cucu Isra'il?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **penghancuran Masjid Aqsha dan terhinanya bangsa Yahudi**
- [what] *Apa yang terjadi pada Masjid Aqsha?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **penghancuran sebanyak dua kali**
- [what] *Surat apa yang mengangkat keterangan tentang Masjid Aqsha?* (ctx: Masjid Aqsha di Bait al-Maqdis (2)) → gold: **surat al Isra'**

## 8. Interpretasi — apa yang diperoleh (jawaban untuk Bu Diana)

**Jawaban singkat: graf v3 BELUM bisa menjawab mayoritas QASiNa.** Potensi terjawab hanya **48/500 (9.6%)** — dan itu pun **upper-bound yang optimistis**.

**Kenapa 9.6% pun terlalu murah hati:** untuk satu event (mis. Perang Badr), semua pertanyaan menghasilkan **kandidat PERSON yang identik** (daftar tokoh INVOLVED_IN event itu). Sebuah pertanyaan dihitung HIT kalau jawabannya kebetulan salah satu tokoh utama tersebut — **bukan** karena graf membedakan role ('yang memimpin kafilah' vs 'yang membawa panji'). Jadi answerability yang presisi-role **lebih rendah** dari angka ini.

**Tiga akar penyebab (urut dampak):**

1. **Granularitas relasi terlalu kasar** (~72% kasus). `INVOLVED_IN` hanya menyatakan 'tokoh X terlibat di event Y', tidak menyimpan peran spesifik. Pertanyaan QASiNa justru menanyakan peran mikro ('yang mengintai', 'yang membawa panji', 'yang mempersiapkan').
2. **Representasi waktu tak sepadan** (`when` = 0% HIT). KG menyimpan tahun Hijriah ('Tahun 2 H', 'Bulan Syawwal 2 H'), QASiNa memakai ekspresi relatif ('tahun kedua', 'akhir Rajab') → tak match walau event-nya benar.
3. **Di luar cakupan domain** (~11% `no_entity_linked`). Banyak konteks QASiNa bukan event Sirah inti: tafsir Al-Qur'an, pendidikan karakter, sejarah Romawi-Persia → tak ada node-nya di KG.

**Yang JUSTRU bisa dijawab graf:** pertanyaan **struktural kasar** — 'siapa tokoh utama yang terlibat di event X' (who = 38/226 = 16.8%, tertinggi). Ini sesuai watak KG: peta keterhubungan tokoh-event-tempat, **bukan** mesin reading-comprehension.

**Implikasi / future work (sejalan arahan Bu Diana 2026-05-16):**
- **LLM verb extraction** → relasi ber-predikat lebih kaya (MENGUTUS/MEMIMPIN/MEMBAWA) supaya role mikro tersimpan → langsung menaikkan answerability `who`/`what`.
- **Normalisasi ekspresi waktu** (Hijriah ↔ relatif) untuk `when`.
- **Perluasan skema / entity linking + alias** untuk menutup gap cakupan.

> Catatan jujur: hasil ini **bukan kegagalan**, tapi karakterisasi yang benar — QASiNa = QA reading-comprehension berbasis span, KG = struktur relasi. Keduanya tugas berbeda; studi kasus ini mengukur **sejauh mana struktur KG kebetulan menjawab pertanyaan QA**, dan menunjukkan arah perbaikan yang konkret.
