# Pedoman Penulisan Buku TA — Genta Putra Prayoga

> Rujukan tunggal aturan penulisan. Semua bab (`bab/*.tex`) harus patuh ini. Dibuat 2026-06-16.

## Format & template
- Pakai template **b201lab/template-buku-ta-its** (mengikuti **SK Rektor ITS No. 280 Tahun 2022**). **Jangan** ubah mesin format (margin, font, penomoran, daftar isi) di `main.tex`/`titlesec`.
- Penomoran bab/gambar/tabel, daftar isi, daftar gambar/tabel/kode otomatis dari template.

## Bahasa & gaya
- **TANPA em dash (`—`) sama sekali.** Ganti dengan koma, tanda kurung, atau pecah jadi dua kalimat. (Di LaTeX: jangan tulis `---`.)
- **Layman terms.** Hindari penjelasan terlalu teknis. Saat istilah teknis pertama muncul, jelaskan singkat dengan bahasa sederhana. Utamakan pembaca non-pakar paham.
- Bahasa Indonesia baku (PUEBI). Istilah asing ditulis *italic* (`\emph{...}`).
- Hindari kalimat berbelit; satu ide per kalimat bila bisa.

## Sitasi & sumber
- Gaya **APA author-year** via `biblatex` (`style=apa, backend=biber`). Pakai `\parencite{key}` (kutipan dalam kurung) atau `\textcite{key}` (nama jadi bagian kalimat).
- Semua sumber masuk `pustaka/pustaka.bib`.
- **Jangan mengarang sumber** (judul/penulis/tahun/jurnal). Hanya sitasi sumber nyata yang ada di Daftar Pustaka. Untuk klaim historis Sirah, rujuk teks Mubarakfuri (terjemahan Kathur Suhardi) atau tandai belum terverifikasi.

## Susunan buku (disepakati 2026-06-16)
Front matter: Daftar Isi, Daftar Gambar, Daftar Tabel, Daftar Kode Sumber.

- **BAB 1 Pendahuluan** — 1.1 Latar Belakang, 1.2 Rumusan Masalah, 1.3 Batasan Masalah, 1.4 Tujuan, 1.5 Manfaat. (TIDAK ada Sistematika Penulisan.)
- **BAB 2 Tinjauan Pustaka** — 2.1 Hasil Penelitian Terdahulu, 2.2 Dasar Teori.
- **BAB 3 Metodologi** — 3.1 Perancangan Sistem (sub-bab lain menyusul; tunggu konfirmasi).
- **BAB 4 Hasil dan Pembahasan** — (sub-bab menyusul; tunggu konfirmasi).
- **BAB 5 Kesimpulan dan Saran**.

Back matter: Daftar Pustaka, Lampiran, Biodata Penulis.

## Catatan isi (khusus proyek ini)
- NER final = **SRL-based saja** (LLM-NER dibatalkan). Jangan sebut LLM-NER sebagai bagian metode final.
- SNA termasuk ruang lingkup (analisis graf).
- Pembimbing: **Dini Adni Navastara, S.Kom., M.Sc.**; Ko-pembimbing: **Ratih Nur Esti Anggraini, S.Kom., M.Sc., Ph.D.**
