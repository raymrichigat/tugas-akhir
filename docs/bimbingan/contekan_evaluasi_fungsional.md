# Contekan: Evaluasi Fungsional Knowledge Graph

> Untuk bimbingan. Pegangan saat menjelaskan ke dosen.

---

## 1 kalimat (kalau cuma sempat ngomong sekali)

> "Evaluasi fungsional membuktikan graf saya **bisa dipakai menjawab pertanyaan penelusuran** — saya ajukan kueri seperti 'siapa terlibat di Perang Badar', graf menjawab dengan benar dan bisa dilacak balik ke sumbernya."

---

## Bedanya dari 2 evaluasi lain (poin pembuka)

| Evaluasi | Menjawab pertanyaan | Alat ukur |
|---|---|---|
| Kualitas NER | Seberapa **akurat** model mengenali entitas? | F1 (0,9537) |
| SNA (struktur) | Bagaimana **bentuk** jaringannya? | Sentralitas, komunitas |
| **Fungsional** ← ini | Apakah graf **layak dipakai** menelusuri hubungan? | Kueri jalan & benar |

Kalimat kunci: *"Kalau dua evaluasi lain menilai akurasi dan bentuk graf, fungsional menilai kegunaannya."*

---

## Analogi

> Seperti menguji mesin pencari. Bukan mengukur seberapa bagus hasilnya, tapi membuktikan: kalau saya ketik pertanyaan, mesinnya jalan dan mengembalikan jawaban yang benar.

---

## Contoh konkret (tunjukkan ini)

**Kueri Q1: "Siapa saja yang terlibat dalam Perang Badar?"**
Graf mengembalikan **63 tokoh**, tiap baris lengkap dengan halaman sumber:

| Tokoh | Halaman | Bukti teks |
|---|---|---|
| Muhammad | 165–168, … | "...Aku mendengar Rasulullah..." |
| Abu Bakar | 231–232 | "...seluruh keluarga Abu Bakar..." |
| Abu Jahal | 165–168 | "...Tatkala Abu Jahal... saat Perang..." |
| Abu Sufyan bin Harb | 300–302, … | "...saat Perang..." |
| Bilal bin Rabah | 231–232 | "...hijrah setelah Perang..." |

Poin penting: *pertanyaan ini tidak bisa dijawab dari CSV biasa, harus menelusuri relasi antar node. Itulah alasan data disusun jadi graf.*

6 skenario kueri yang diuji: (1) tokoh, (2) lokasi, (3) waktu, (4) tokoh-peristiwa, (5) **multi-hop**, (6) kronologi.

---

## 4 kriteria penilaian tiap kueri

1. **Jalan tanpa error** → skema graf konsisten.
2. **Hasil tidak kosong** → data ada & saling terhubung.
3. **Sesuai sumber** (cek manual ke teks) → jawaban benar, bukan sekadar muncul.
4. **Bisa dilacak** (`evidence`, `halaman`, `chunk_id`) → bisa dipertanggungjawabkan ke teks Sirah.

---

## Antisipasi pertanyaan dosen

| Kalau ditanya… | Jawab |
|---|---|
| Bedanya sama SNA? | "SNA menilai struktur (siapa paling sentral). Fungsional menilai kegunaan (bisa nggak graf menjawab pertanyaan)." |
| Kenapa kueri, bukan angka? | "Cara satu-satunya bertanya ke knowledge graph ya lewat kueri. Keberhasilan diukur dari bisa-tidaknya menjawab." |
| Tahu dari mana jawabannya benar? | "Validasi manual ke teks Mubarakfuri lewat `evidence` + `halaman` di tiap relasi." |
| Ada hasil yang salah? | (jujur) "Ada beberapa tokoh yang kurang tepat masuk karena ketangkap kedekatan kata. Justru kriteria 'sesuai sumber' yang menangkap kasus ini." |

> **Jujur soal artefak:** contoh nama seperti "Amr bin Al-Ash", "Najasyi", "Ja'far" ikut masuk ke Perang Badar padahal *false-positive* dari ekstraksi berbasis kedekatan kata. Jangan disembunyikan — ini bukti evaluasinya jujur dan kriteria validasi manual memang bekerja.
