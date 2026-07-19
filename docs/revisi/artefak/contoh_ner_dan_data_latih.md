# Artefak Revisi Sidang — Contoh NER (input→BIO→node) & Bentuk Data Latih

> Menjawab **Dosen-2 poin 1** (kontribusi NER terlihat konkret: kalimat→token→BIO→entitas→node)
> dan **Dosen-2 poin 2** (tampilkan satu record data latih yang sebenarnya).
> Semua contoh **diambil dari data nyata repo** (bukan ilustrasi karangan): teks Sirah hasil
> OCR + label BIO gold + prediksi model pemenang **S4-augmentation** pada data uji.

---

## Bagian 1 — Contoh alur NER: kalimat → token → BIO → entitas → node (Dosen-2 #1)

**Kalimat sumber** (data uji, chunk `000083-007`, hal. 199–202, bab *Baiat Aqabah Pertama*):

> "… **Mush'ab bin Umair** kembali ke **Makkah** …"

Kalimat ini dipilih karena strukturnya sepadan dengan contoh yang diminta dosen
("Rasulullah pergi ke Madinah"): satu tokoh (PERSON) berpindah ke satu tempat (LOCATION).

### Langkah 1 — Tokenisasi (level kata/tanda baca)

| No | Token |
|---:|---|
| 1 | Mush'ab |
| 2 | bin |
| 3 | Umair |
| 4 | kembali |
| 5 | ke |
| 6 | Makkah |

### Langkah 2 — Prediksi label BIO per token (output model NER)

| Token | Label BIO (prediksi model) | Keterangan |
|---|---|---|
| Mush'ab | **B-PERSON** | awal entitas PERSON |
| bin | **I-PERSON** | lanjutan entitas PERSON |
| Umair | **I-PERSON** | lanjutan entitas PERSON |
| kembali | O | bukan entitas |
| ke | O | bukan entitas |
| Makkah | **B-LOCATION** | awal entitas LOCATION |

> Catatan: pada contoh ini prediksi model **sama persis** dengan label acuan (gold) —
> jadi kutipan ini benar-benar mewakili keluaran model, bukan hanya anotasi manual.

### Langkah 3 — Ekstraksi entitas (penggabungan token B-/I- yang berurutan)

| Entitas | Tipe |
|---|---|
| Mush'ab bin Umair | PERSON |
| Makkah | LOCATION |

### Langkah 4 — Pembentukan node & relasi pada knowledge graph

Entitas hasil NER **belum langsung menjadi graf**; ia menjadi *kandidat node* yang kemudian
dinormalisasi dan dihubungkan pada tahap konstruksi knowledge graph:

```
(:Person {nama: "Mush'ab bin Umair"})
(:Location {nama: "Makkah"})

(:Person {nama:"Mush'ab bin Umair"}) -[:BERADA_DI / co-occurrence]-> (:Location {nama:"Makkah"})
```

Alur ini menegaskan pemisahan tugas: **NER menghasilkan entitas**, sedangkan **relasi
antar-node dibentuk pada tahap konstruksi KG** (co-occurrence + normalisasi alias), bukan oleh
model NER itu sendiri.

---

## Bagian 2 — Bentuk satu record data latih yang sebenarnya (Dosen-2 #2)

Satu record data latih = **satu chunk** (potongan teks yang memuat beberapa kalimat), lengkap
dengan `chunk_id`, metadata sumber, daftar token, POS-tag, dan label BIO. Contoh berikut adalah
record nyata `000384-001`.

### Metadata record

| Field | Nilai |
|---|---|
| `chunk_id` | `000384-001` |
| `doc_id` / `chunk_index` | 384 / 1 |
| Halaman sumber | 613 |
| Judul bab | RUMAH TANGGA NABAWI |
| Judul sub-bab | Shafiyah binti Huyai bin Akhthab |

### Teks asli chunk

> "Dia berasal dari Bani Israil, yang sebelumnya dia salah seorang dari tawanan Khaibar. Lalu
> Rasulullah memilihnya untuk diri beliau sendiri. membebaskannya dan menikahinya setelah
> penaklukkan Khaibar pada tahun 7 H."

### Daftar token + POS-tag + label BIO (record utuh, 34 token)

| No | Token | POS | Label BIO |
|---:|---|---|---|
| 1 | Dia | PRON | O |
| 2 | berasal | VERB | O |
| 3 | dari | ADP | O |
| 4 | Bani | PROPN | O |
| 5 | Israil | PROPN | O |
| 6 | , | PUNCT | O |
| 7 | yang | PRON | O |
| 8 | sebelumnya | ADV | O |
| 9 | dia | PRON | O |
| 10 | salah | ADJ | O |
| 11 | seorang | DET | O |
| 12 | dari | ADP | O |
| 13 | tawanan | NOUN | O |
| 14 | **Khaibar** | PROPN | **B-LOCATION** |
| 15 | . | PUNCT | O |
| 16 | Lalu | SCONJ | O |
| 17 | **Rasulullah** | PROPN | **B-PERSON** |
| 18 | memilihnya | VERB | O |
| 19 | untuk | ADP | O |
| 20 | diri | PRON | O |
| 21 | beliau | PRON | O |
| 22 | sendiri | DET | O |
| 23 | . | PUNCT | O |
| 24 | membebaskannya | VERB | O |
| 25 | dan | CCONJ | O |
| 26 | menikahinya | VERB | O |
| 27 | setelah | ADP | O |
| 28 | penaklukkan | NOUN | O |
| 29 | **Khaibar** | PROPN | **B-EVENT** |
| 30 | pada | ADP | O |
| 31 | **tahun** | NOUN | **B-TIME** |
| 32 | **7** | NUM | **I-TIME** |
| 33 | **H** | NOUN | **I-TIME** |
| 34 | . | PUNCT | O |

Semua token di atas berasal dari **satu chunk yang sama** (bukan potongan token acak yang tak
berhubungan). Format inilah yang benar-benar diberikan ke model: urutan token berlabel BIO,
disertai `text_id` (chunk_id) sebagai penanda konteks.

### Entitas yang terkandung dalam record ini

| Entitas | Tipe |
|---|---|
| Khaibar (token 14) | LOCATION |
| Rasulullah (token 17) | PERSON |
| Khaibar (token 29) | EVENT |
| tahun 7 H (token 31–33) | TIME |

### Poin penting yang bisa ditekankan di buku (mendukung Dosen-2 #3)

Kata **"Khaibar"** muncul dua kali dengan **label berbeda**: sebagai **LOCATION** pada
"tawanan **Khaibar**" (menunjuk tempat) dan sebagai **EVENT** pada "penaklukkan **Khaibar**"
(menunjuk peristiwa). Perbedaan label untuk kata permukaan yang sama ini hanya mungkin karena
IndoBERT melakukan klasifikasi token **dengan mempertimbangkan konteks kalimat**, bukan
mengklasifikasikan setiap kata secara terpisah. Contoh ini sekaligus menjawab pertanyaan dosen
tentang peran konteks pada token classification.

---

### Sumber data (untuk reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Token + label BIO (train) | `data/result/pseudo-labelling/SRL-NER/train.csv` |
| POS-tag asli (UPOS) | `data/result/pseudo-labelling/SRL-NER/train_postag.csv` |
| Metadata chunk (bab/sub-bab/halaman/teks) | `data/result/chunking_result/sirah_chunks_final.csv` |
| Token + gold + prediksi (uji, S4-augmentation) | `data/result/pseudo-labelling/SRL-NER/test.csv` + `.../done_newest/augmentation/.../*-incorrect.xlsx` |
