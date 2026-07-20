# Dasar Pemilihan Hyperparameter (Pak Aldi #5)

> Menjawab: jangan sekadar "mengikuti notebook"; beri **alasan tiap hyperparameter** + **referensi
> ilmiah** + jelaskan bahwa nilai diadaptasi/diuji ulang di dataset Sirah. Sumber: makalah acuan
> pembimbing/kating (Ariyanto dkk., 2025) + disertasi penulisnya.

## Referensi acuan (peer-reviewed, terverifikasi)

> **Ariyanto, A. D. P., Purwitasari, D., Fatichah, C., Ravana, S. D., Andrian, & Parwata, A. A. Y.
> (2025).** *Transformer-Based Semantic Role Labeling for Crisis Events Using Semi-Supervised
> Learning on Low-Resource Language Twitter Texts.* **IEEE Access.**
> DOI: 10.1109/ACCESS.2025.3604068.

Makalah ini = rujukan "Ariyanto dkk." yang dipakai notebook proyek. Tugas acuannya **sejenis**:
NER/SRL bahasa Indonesia berbasis **IndoBERT** dengan **semi-supervised iterative self-training +
filtering confidence** — kerangka yang sama diadaptasi untuk korpus Sirah. Konfigurasi ini juga
tercantum di disertasi penulis pertama (`lama/7025221021-Doctoral.pdf`).

## Dasar tiap hyperparameter (dari Ariyanto dkk., 2025, Tabel 6)

| Hyperparameter | Nilai | Dasar (dari referensi) |
|---|---|---|
| Learning rate | **2e-5** | "nilai yang umumnya efektif untuk model berbasis transformer"; nilai kecil mencegah gangguan/instabilitas saat pelatihan |
| Batch size | **16** | dipilih untuk mengoptimalkan pemakaian memori GPU tanpa mengorbankan efisiensi komputasi |
| Epoch | **10** | dengan **early stopping** untuk mencegah overfitting |
| Weight decay | **0,01** | menurunkan kompleksitas model & memperbaiki generalisasi |
| Seed | **42** | reprodusibilitas eksperimen |
| Model pra-latih | **IndoBERT** (`indolem/indobert-base-uncased`) | performa terbaik pada tugas acuan (F1 0,863), sama dengan yang dipakai proyek ini |
| Panjang maks. sequence | **512** token | batas arsitektur IndoBERT |
| Ambang confidence self-training | **0,9** | referensi menguji **0,7 / 0,8 / 0,9**; ambang 0,9 = filtering paling ketat → hanya pseudo-label berkualitas tinggi, dan **memberi F1 terbaik (0,863)**. Confidence = **rata-rata** skor confidence token dalam satu teks |

## Cara disajikan di buku (framing yang diminta Pak Aldi)

1. **Bukan** "mengikuti notebook", melainkan: nilai awal **diadopsi dari penelitian acuan
   (Ariyanto dkk., 2025)** yang menangani tugas sejenis (IndoBERT + self-training semi-supervised
   untuk bahasa Indonesia berdaya rendah), lalu **diterapkan dan diuji ulang** pada dataset Sirah
   Nabawiyah.
2. Tiap parameter punya **alasan** (tabel di atas), bukan angka sembarang.
3. Khusus **ambang 0,9**: di referensi sudah dibandingkan 0,7/0,8/0,9 dan 0,9 terbukti terbaik →
   proyek ini mengadopsi 0,9 sebagai ambang filtering pseudo-label.

## Catatan jujur (jangan overclaim)

- **Maksimum iterasi = 6** pada proyek ini **bukan** angka dari referensi. Referensi menjalankan
  self-training secara iteratif hingga data unlabeled terpakai/kondisi berhenti; proyek ini
  **membatasi di 6 iterasi** sebagai titik henti praktis (konvergensi F1 sudah landai). Nyatakan
  ini apa adanya, jangan klaim "6 dari Ariyanto dkk."
- Nilai-nilai lain (lr/batch/epoch/weight decay/seed/threshold) **memang** dari referensi.
- Pak Aldi menyarankan konfirmasi ke peneliti acuan **jika belum ada dokumentasi**. Karena
  konfigurasi ini **sudah terbit** di makalah peer-reviewed (IEEE Access 2025) + disertasi, dasar
  hyperparameter **sudah terpenuhi lewat sitasi** — lebih kuat daripada konfirmasi lisan. Tidak
  perlu konfirmasi tambahan.

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Makalah acuan | `lama/Transformer-Based_Semantic_Role_Labeling_..._Twitter_Texts.pdf` (IEEE Access 2025) |
| Disertasi penulis pertama | `lama/7025221021-Doctoral.pdf` |
| Konfigurasi di proyek | Tabel 3.11 buku (lr 2e-5, batch 16, 10 epoch/iterasi, threshold 0,9, maks 6 iterasi) |
