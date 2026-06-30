# Contoh Kesalahan per Entitas — Pola & Bukti Data

> Untuk ditunjukkan ke Bu Dini Adni. Tujuannya memperlihatkan **pola kesalahan**
> pada gold data NER per tipe entitas, dengan **contoh nyata** dari teks.
>
> **Catatan sumber:**
> - 🟦 *gold* / *korpus* = murni dari data (tanpa model).
> - 🟨 *audit* = ditemukan via ketidaksepakatan model **lama** vs gold —
>   dipakai HANYA sebagai **alat menemukan** gold yang aneh (diagnostik), bukan
>   hasil final. Akan diperiksa ulang setelah semua model dilatih ulang.
> - Status: ✅ sudah diperbaiki di kode · ⚠️ limitasi OCR · 🔍 perlu review manual.

---

## Gambaran umum (kenapa kelas tertentu lebih sering salah)

Distribusi entitas pada gold sangat timpang — ini akar utama: kelas dengan data
sedikit (EVENT, TIME) paling rawan salah.

| Entitas | Jumlah | Porsi |
|---|---:|---:|
| PERSON | 4.089 | 67,6 % |
| LOCATION | 1.437 | 23,8 % |
| TIME | 307 | 5,1 % |
| EVENT | 216 | 3,6 % |

Rasio **PERSON : EVENT ≈ 19 : 1**. Urutan kualitas pengenalan mengikuti urutan
jumlah data ini.

---

## 1. PERSON

| Pola kesalahan | Contoh nyata (konteks) | Sumber | Status |
|---|---|---|---|
| **Honorifik tak ikut** | "…Mukhtashar Siratir-Rasul **〚Shalallahu Alaihi wa Sallam〛**…" — gold=O, model menandai PERSON | 🟨 audit | 🔍 (langka; 1× di judul kitab) |
| **Nama langka kelewat** | "…pemusnahan mereka di tangan **〚Bukhtanashar〛**…" — gold benar PERSON, model gagal | 🟨 audit | 🔍 few-shot |
| **Nama terpotong** | "**Khalid bin** 〚dia berkata〛…", "Rabi'ah bin Umayyah **bin** 〚Setelah〛" — rantai nasab putus di batas kalimat | 🟦 korpus | 🔍 |
| **Apostrof hilang (OCR)** | "Rabi **ah**" → seharusnya **Rabi'ah**; "Ma **qal**" → **Ma'qal** | 🟦 korpus | ✅ kamus koreksi |
| **Spasi hilang (OCR)** | "**SyaikhAbdullah**", "riwayatAbu" (dua kata menempel) | 🟦 korpus | ⚠️ limitasi |

---

## 2. LOCATION

| Pola kesalahan | Contoh nyata (konteks) | Sumber | Status |
|---|---|---|---|
| **Ambigu LOCATION vs EVENT** | "…penjelasan dari Allah tentang **peperangan 〚Badr〛**…" → di sini Badr = peristiwa, bukan tempat | 🟦 gold | 🔍 review 145 kasus |
| **Lokasi kelewat** | "…tidak boleh masuk **〚Baitul-Haram〛**…", "…berlalu dari Shan'a hingga **〚Hadhramaut〛**…" — gold=O | 🟨 audit | 🔍 |
| **Tanda baca menempel** | "…dibawa ke **Babilonia.**" (titik nempel jadi bagian token) | 🟦 korpus | ✅ dipisah saat tokenisasi |
| **Apostrof hilang (OCR)** | "Tha **if**" → seharusnya **Tha'if** | 🟦 korpus | ✅ kamus koreksi |
| **Nama langka di-miss model** | "Babilon", "Babilonia" — gold benar, model lama gagal | 🟨 audit | (model, bukan gold) |

---

## 3. EVENT  *(kelas paling kecil — 3,6 %)*

| Pola kesalahan | Contoh nyata | Sumber | Status |
|---|---|---|---|
| **Over-extension** (menyedot kata sesudahnya) | "**Perang Badr Aisyah**" (Aisyah=orang), "Perang Khaibar Bekas", "Perang Uhud Jabal" | 🟦 gold | ✅ dipangkas → "Perang Badr" dst. |
| **Bias kapitalisasi** | "**Perang** Badr" (kapital) → EVENT, tapi "**perang** Badr" (kecil) → O | 🟦 gold | ✅ kini case-insensitive |
| **Nama event langka kelewat** | "…bab **〚Ghazwah Dzatu Qarad〛**…" — gold EVENT, model gagal | 🟨 audit | 🔍 few-shot |
| **FP "perang \<orang\>"** | "…pasukan **perang Kisra**…" (Kisra=orang, bukan medan) | 🟦 gold | ✅ guard ditambah |

---

## 4. TIME  *(kelas kecil — 5,1 %)*

| Pola kesalahan | Contoh nyata (konteks) | Sumber | Status |
|---|---|---|---|
| **Batas frasa B/I tak rapi** | "…malam **〚tanggal〛** 21 **〚dari〛** bulan Ramadhan" — model pecah/awali ulang frasa waktu | 🟨 audit | 🔍 |
| **Awal frasa waktu kelewat** | "…bertemu di Aqabah pada **〚pertengahan〛** hari-hari…", "**〚malam〛** tanggal 21…" — gold=O di kata pembuka | 🟨 audit | 🔍 |
| **Noise OCR di tengah frasa** | "bulan Rabi'ul **4.** Awwal" (angka nyelip memutus "Rabi'ul Awwal") | 🟦 korpus | ⚠️ limitasi |
| **Tahun terpotong (OCR)** | "…Dzul Hijjah **tahu 9 H**…" ("tahun" kehilangan huruf, tahun tak tertangkap utuh) | 🟦 korpus | ⚠️ limitasi |

---

## Benang merah (untuk disampaikan ke Bu Dini)

1. **Mayoritas kesalahan = soal DETEKSI/BATAS, bukan salah TIPE.** Model jarang
   bingung PERSON vs LOCATION; yang sering = terlewat, kelebihan, atau batas
   entitas geser.
2. **Kelas minoritas (EVENT, TIME) paling rawan** — konsekuensi langsung dari
   data timpang 19 : 1.
3. **Banyak "kesalahan" sebenarnya akar OCR/gold**, bukan model: apostrof hilang,
   tanda baca menempel, kapitalisasi tak konsisten. Sebagian besar **sudah
   diperbaiki** di putaran ini; sisanya (kata menempel, huruf hilang) **diakui
   sebagai limitasi OCR** secara terbuka.
4. **Ambiguitas LOCATION↔EVENT** (Badr/Uhud tempat vs peristiwa) butuh
   keputusan manual per konteks — sedang di-review (145 kasus).

> Angka pengenalan final (F1 per kelas) akan dilaporkan **setelah semua model
> dilatih ulang** di atas gold yang sudah diperbaiki.
