# Perbaikan BAB 5 — hasil akhir

## P-5.1. Kalimat pembuka (Temuan #6) ✅ — dobel "dan"

Saat ini: "Berdasarkan hasil **dan** pengujian **dan** pembahasan yang telah dilakukan, diperoleh
**Kesimpulan** sebagai berikut". Ganti:

> "Berdasarkan hasil pengujian dan pembahasan yang telah dilakukan, diperoleh kesimpulan sebagai
> berikut."

(sekaligus "Kesimpulan" → "kesimpulan" huruf kecil)

## P-5.2. Tambahkan angka validitas semantis ke kesimpulan (Bu Nanik #8, Temuan #6) 🧰

Pertahankan kalimat "layak operasional tetapi belum berdiri sendiri", tambahkan:

> "Seluruh enam skenario kueri berhasil dijalankan sehingga tingkat keberhasilan operasional
> mencapai 100%, dan seluruh hasil dapat ditelusuri melalui metadata evidence dan halaman. Namun,
> tingkat kesesuaian semantis berbeda pada setiap fungsi, dengan nilai tertinggi 82,35% pada F6
> dan nilai terendah 0% pada F4 (rata-rata 31,58%)."

## P-5.3. Saran — bedakan precision-sekarang vs precision/recall/F1-lanjutan (Bu Nanik #9-saran) 🧰

> "Penelitian ini menghitung tingkat kesesuaian jawaban yang dikembalikan kueri (precision
> jawaban). Penelitian selanjutnya dapat menyusun gold standard relasi beranotasi manual untuk
> menghitung precision, recall, dan F1-score seluruh relasi. Recall menyeluruh belum dapat
> dihitung pada penelitian ini karena tidak tersedia daftar lengkap seluruh relasi yang seharusnya."

## P-5.4. Batas klaim SNA (Temuan #4) 📝

Nilai centrality/density/modularity **menggambarkan struktur graf hasil ekstraksi**, tidak otomatis
membuktikan pengaruh historis tokoh atau kebenaran seluruh relasi. Pertahankan batas interpretasi ini.

## P-5.5. Negasi → saran/future work (D2.8) 🧰
Deteksi negasi sebagai future work (`keterbatasan_negasi_relasi.md`).
