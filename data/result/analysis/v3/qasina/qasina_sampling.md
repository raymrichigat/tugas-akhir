# Studi Kasus QASiNa → Knowledge Graph — Sampling

> Deliverable bimbingan 2026-05-30 (Bu Diana: *"sampling saja untuk QASiNa"*).
> Pertanyaan inti: **apakah pertanyaan QASiNa bisa dijawab menggunakan graf?**
> Dokumen ini = penjelasan + contoh **terkurasi** (bisa vs tidak bisa), jalur grafnya
> sudah diverifikasi ke `data/result/relation_result/edges_v3.csv`.
> Evaluasi kuantitatif penuh (500 soal) ada di `qasina_graph_eval.md` sebagai pendukung.

---

## 1. Penjelasan: bagaimana sebuah pertanyaan "dijawab" oleh graf

QASiNa = *Question Answering Sirah Nabawiyah* (66 konteks, 500 soal; tipe **who / what /
where / when / how many**). Cara menjawab dari graf:

```
Pertanyaan  ──(1) cari entitas yang disebut──►  Node KG (PERSON/EVENT/LOCATION/TIME)
                                                      │
                       (2) telusuri relasi sesuai tipe pertanyaan
                                                      ▼
                                              Node jawaban (kandidat)
```

Pemetaan tipe pertanyaan → relasi yang relevan di KG:

| Tipe | Yang dicari | Relasi KG | Bisa? |
|---|---|---|---|
| **who** | PERSON | `INVOLVED_IN`, `KELUARGA`, `SAHABAT`, `MUSUH` | 🟡 sebagian |
| **where** | LOCATION | `OCCURRED_AT` | 🟡 sebagian |
| **when** | TIME | `OCCURRED_ON` | ❌ jarang |
| **what** | EVENT/atribut | (deskriptif) | ❌ kebanyakan |
| **how many** | kuantitas | — (tak ada) | ❌ |

**Inti temuan:** graf hanya menyimpan **relasi struktural kasar** ("tokoh X terlibat di
event Y", "event Y terjadi di Z / pada waktu T"). Jadi graf kuat untuk pertanyaan
*struktural*, tapi lemah untuk pertanyaan *reading-comprehension* yang menanyakan
peran mikro atau detail naratif.

---

## 2. ✅ Contoh BISA dijawab (jawaban tepat lewat relasi yang sesuai)

### Contoh 1 — `where` (lokasi event)
> **Q:** "Dimana Rasulullah menemui Jibril dalam bentuk aslinya ketika Isra' Mi'raj?"
> **Jawaban QASiNa:** *Sidratil Muntaha*

**Jalur graf:**
```
(Mi'Raj : EVENT)  ──OCCURRED_AT──►  (Sidratul Muntaha : LOCATION)
```
✅ **Tepat.** Graf menyimpan lokasi peristiwa ini persis sama dengan gold answer.

---

### Contoh 2 — `who` (tokoh terlibat di event)
> **Q:** "Siapa yang memimpin kafilah Quraisy yang datang dari arah Syam menuju Mekkah?"
> **Jawaban QASiNa:** *Abu Sufyan*

**Jalur graf:**
```
(Abu Sufyan bin Harb : PERSON)  ──INVOLVED_IN──►  (Perang Badr : EVENT)
```
✅ **Tepat.** Graf tahu Abu Sufyan adalah tokoh kunci Perang Badr. (Catatan: graf
menjawab "Abu Sufyan terlibat di Badr"; peran spesifik "memimpin kafilah" tidak
tersimpan, tapi nama jawabannya benar.)

---

### Contoh 3 — `where` (lokasi event)
> **Q:** "Kemanakah Nabi dan sahabatnya hijrah setelah mengadakan perjanjian dengan penduduk Madinah?"
> **Jawaban QASiNa:** *Yasrib (Madinah)*

**Jalur graf:**
```
(Hijrah Ke Madinah : EVENT)  ──OCCURRED_AT──►  (Madinah : LOCATION)
```
✅ **Tepat.** Pola ini berlaku untuk banyak event yang punya `OCCURRED_AT`:
Perjanjian Hudaibiyah→Hudaibiyah, Perang Uhud→Madinah, Perang Khaibar→Khaibar,
Fathul Makkah→Makkah, dst.

---

## 3. 🟡 Contoh BISA SEBAGIAN (jawaban benar tapi peran tak dibedakan graf)

> **Q:** "Siapa yang membawa Rayah (panji) pada Rasul dalam perang Badar?"
> **Jawaban QASiNa:** *Ali*

**Jalur graf:**
```
(Ali bin Abu Thalib : PERSON)  ──INVOLVED_IN──►  (Perang Badr : EVENT)
```
🟡 Jawaban "Ali" **kebetulan benar** karena Ali memang terhubung ke Perang Badr.
**Tapi** graf tidak menyimpan peran "membawa panji" — pertanyaan lain seperti
"siapa yang mengintai Quraisy?" akan mengembalikan **daftar tokoh yang sama**
(semua yang `INVOLVED_IN` Perang Badr). Jadi graf tak bisa **membedakan peran**;
ia hanya tahu *keterlibatan umum*. Inilah kenapa skor "potensi terjawab" (9,6%)
sebetulnya **optimistis**.

---

## 4. ❌ Contoh TIDAK bisa dijawab — dan kenapa

### 4a. Granularitas relasi terlalu kasar (penyebab terbesar, ~72% soal)
Graf tahu *siapa terlibat*, bukan *peran spesifik*.

> **Q:** "Siapa yang diutus oleh Nabi untuk mengintai Quraisy?" → *Abdullah ibn Jahsy*
> **Q:** "Siapa yang mempersiapkan perang Badar sebenarnya?" → *Abu Ubaidah Amir ibn Al-Jarah*

Graf hanya punya `(tokoh) —INVOLVED_IN→ (Perang Badr)`; tidak ada relasi
`MENGINTAI` atau `MEMPERSIAPKAN`. → **tak terjawab presisi.**

### 4b. Representasi waktu tak sepadan (`when` ≈ 0% terjawab)
> **Q:** "Kapan perang Badar terjadi?" → *tahun kedua*

Graf **punya** waktunya: `(Perang Badr) —OCCURRED_ON→ (Bulan Syawwal 2 Hijriyah)`.
Secara makna "2 Hijriyah" = "tahun kedua", **tapi formatnya beda** (Hijriah vs
ekspresi relatif) sehingga tidak cocok secara string. → gagal walau info-nya ada.

### 4c. Di luar cakupan domain KG (~11% soal)
Banyak konteks QASiNa bukan peristiwa Sirah inti — tafsir Al-Qur'an, pendidikan
karakter, sejarah Romawi-Persia — sehingga **tidak ada node**-nya:

> **Q:** "Apa nama lain dari Masjid Aqsha?" → *Bait al-Maqdis*
> **Q:** "Dari mana asal-usul Nabi Ibrahim?" → *kota Ur*
> **Q:** "Berapa kali Masjid Aqsha dihancurkan?" (how many) → graf tak simpan kuantitas

---

## 5. Ringkasan (jawaban untuk Bu Diana)

- **Bisa?** Sebagian kecil. Graf v3 **bisa** menjawab pertanyaan **struktural** —
  *siapa tokoh utama suatu event* (`who`) dan *di mana event terjadi* (`where`) —
  selama event-nya ada di KG.
- **Tidak bisa?** Mayoritas, karena (1) relasi terlalu kasar untuk peran mikro,
  (2) format waktu tak sepadan, (3) banyak konteks di luar domain Sirah inti.
- **Angka pendukung (eval penuh 500 soal):** potensi terjawab **48/500 ≈ 9,6%**
  (who 16,8% tertinggi; when & how-many 0%) — dan itu pun batas atas optimistis.
- **Arah perbaikan (sejalan arahan Bu Diana 2026-05-16):**
  **LLM verb extraction** → relasi ber-predikat (`MEMIMPIN`, `MENGUTUS`, `MEMBAWA`)
  agar peran mikro tersimpan, plus normalisasi format waktu. Ini akan langsung
  menaikkan answerability `who`/`what`/`when`.

> **Catatan jujur:** ini bukan kegagalan, melainkan karakterisasi yang benar —
> QASiNa adalah QA *span-based reading comprehension*, sedangkan KG adalah *struktur
> relasi*. Keduanya tugas berbeda; studi kasus ini mengukur sejauh mana struktur KG
> kebetulan bisa menjawab QA, dan menunjukkan arah pengembangan yang konkret.
