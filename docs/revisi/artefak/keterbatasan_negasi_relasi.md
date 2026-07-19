# Artefak Revisi Sidang — Keterbatasan: Kesalahan Relasi akibat Negasi (D2.8)

> Menjawab **Dosen-2 poin 8**. Keputusan: **ditulis sebagai keterbatasan penelitian**, bukan
> diimplementasikan deteksi negasinya. Dokumen ini menyediakan **contoh nyata dari KG** +
> kuantifikasi + rumusan keterbatasan yang siap dimasukkan ke Bab 3/4/5.

---

## 1. Akar masalah

Relasi `INVOLVED_IN` (PERSON–EVENT) dibentuk dengan pendekatan **co-occurrence berbasis
kedekatan** (proximity ~200 karakter): jika sebuah PERSON dan sebuah EVENT muncul berdekatan
dalam teks, keduanya dihubungkan. Pendekatan ini **tidak memeriksa makna kata kerja penghubung
maupun keberadaan negasi**, sehingga kalimat yang justru menyatakan **ketidakterlibatan** tetap
menghasilkan relasi keterlibatan.

## 2. Contoh nyata dari knowledge graph (terkonfirmasi)

Edge berikut **benar-benar ada** di KG final (`edges_v4_scoped.csv`, juga di `edges_v3.csv`):

> **`Abu Lahab` —[:INVOLVED_IN]→ `Perang Badr`** (weight 0,5)

Namun kalimat sumber (evidence) yang memicunya justru menyatakan sebaliknya:

> "… Namun Al-Abbas menyembunyikan keislamannya. **Saat Perang Badr, Abu Lahab tidak ikut
> serta.** Ketika sudah ada kabar tentang…" — (hal. 295–297, chunk `000140-001`)

Secara historis pun benar bahwa Abu Lahab **tidak** ikut Perang Badr, sehingga relasi
`Abu Lahab → INVOLVED_IN → Perang Badr` adalah **relasi palsu (false positive)** yang murni
muncul dari kedekatan tekstual antara nama "Abu Lahab" dan "Perang Badr" dalam satu kalimat
bernegasi.

Contoh lain yang terdeteksi dari pola serupa:

| Relasi terbentuk | Kalimat sumber (inti) | Masalah |
|---|---|---|
| Abu Lahab → INVOLVED_IN → Perang Badr | "Saat Perang Badr, Abu Lahab **tidak ikut serta**" | negasi keterlibatan |
| Sa'd bin Mu'adz → INVOLVED_IN → Perang Khandaq | "Sa'd bin Mu'adz berada di Madinah dan **tidak ikut** pergi ke Bani Qainuqa'" | negasi + event yang dirujuk berbeda |

## 3. Kuantifikasi (seberapa sering)

Pada KG final terdapat **206 relasi `INVOLVED_IN`**. Dari penelusuran kalimat evidence:

- **4 relasi** memiliki pola negasi-keterlibatan eksplisit ("tidak/tak/belum + ikut/hadir/turut")
  di sekitar relasi — kandidat kuat *false positive* akibat negasi.
- **60 relasi** mengandung *kata* negasi apa pun ("tidak", "bukan", "tanpa", dll.) di jendela
  evidence-nya. Angka ini **batas atas** — tidak semuanya salah, karena banyak kata negasi tidak
  menegasikan keterlibatan (mis. "tidak lama kemudian"). Perlu pemeriksaan manual untuk
  memastikan mana yang benar-benar keliru.

Artinya, kesalahan akibat negasi **nyata ada** namun **berjumlah kecil** relatif terhadap total
relasi — konsisten untuk dinyatakan sebagai keterbatasan, bukan cacat besar yang membatalkan hasil.

## 4. Rumusan keterbatasan (siap ditulis di buku)

> **Keterbatasan.** Metode pembentukan relasi pada penelitian ini menggunakan pendekatan
> co-occurrence berbasis kedekatan tanpa analisis negasi maupun peran kata kerja penghubung.
> Akibatnya, kalimat yang menyatakan ketidakterlibatan dapat tetap menghasilkan relasi
> keterlibatan yang keliru — sebagaimana ditemukan pada relasi `Abu Lahab → INVOLVED_IN →
> Perang Badr` yang bersumber dari kalimat "Saat Perang Badr, Abu Lahab tidak ikut serta".
> Penanganan negasi (misalnya deteksi kata negasi dan validasi kata kerja relasional) berada di
> luar cakupan penelitian ini dan menjadi arah pengembangan selanjutnya untuk meningkatkan
> ketepatan semantik relasi.

**Penempatan di buku:** Bab 3 (catatan keterbatasan metode relasi) · Bab 4 (saat membahas
ketepatan relasi + contoh) · Bab 5 (saran/future work: deteksi negasi).

---

### Sumber data (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Edge false-positive + evidence | `data/result/relation_result/edges_v4_scoped.csv` (juga `edges_v3.csv`) |
| Chunk sumber | `000140-001` (hal. 295–297) di `data/result/chunking_result/sirah_chunks_final.csv` |
