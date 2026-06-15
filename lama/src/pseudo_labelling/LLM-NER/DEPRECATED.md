# ⚠️ DEPRECATED — LLM-NER Tidak Dipakai

**Status:** Dibatalkan per **2026-05-03** atas keputusan pembimbing (Bu Diana).

**Sumber keputusan:** `revisi_dosen.md` (revisi putaran 2), baris 9:
> *"LLM-NER tidak jadi digunakan, jadinya menggunakan SRL-NER saja"*

---

## Apa yang ada di folder ini?

Folder ini berisi implementasi **LLM-NER** (Instruction Fine-Tuning + QLoRA) yang mengikuti metodologi thesis Andrian (5025211079). Implementasi sudah selesai sampai tahap siap-run di GPU (Colab/Kaggle), **tetapi tidak akan dipakai** di TA final.

| Subfolder / File | Isi | Status |
|---|---|---|
| `asli/` | Penerapan asli Andrian (baseline supervised single-shot) | ❌ Tidak dipakai |
| `pseudo/` | Versi TA dengan iterative self-training (kontribusi orisinal) | ❌ Tidak dipakai |
| `PENJELASAN_THESIS_ANDRIAN.md` | Dokumentasi pemahaman metodologi Andrian | 📚 Arsip referensi |

---

## Kenapa dipertahankan, bukan dihapus?

1. **Bukti effort di laporan TA** — implementasi ini sudah masuk Bab 3 sebelumnya. Bisa disebut singkat di Bab 4 sebagai "eksplorasi yang tidak masuk pipeline final".
2. **Referensi metodologi** — `PENJELASAN_THESIS_ANDRIAN.md` tetap berguna sebagai bahan baca metodologi LLM-based NER untuk Bahasa Indonesia.
3. **Kemungkinan revisi balik** — kalau ada perubahan arah dari pembimbing, kode siap pakai.

---

## Apa yang dipakai sekarang?

**SRL-NER** (BERT iterative self-training) — di folder `src/pseudo_labelling/SRL-NER/`.

Lihat `CLAUDE.md` (root) section **[2026-05-03] Revisi Dosen Putaran 2** untuk konteks lengkap dan task list lanjutan terkait SRL-NER (skenario threshold, unbalanced handling, dll.).

---

## Aturan untuk Claude / kontributor masa depan

- **Jangan menjalankan / men-train / men-deploy** apapun di folder ini tanpa konfirmasi user terlebih dahulu.
- **Boleh dibaca** sebagai referensi metodologi.
- **Jangan dihapus** tanpa konfirmasi user.
- Kalau user bertanya soal LLM-NER, ingatkan keputusan dibatalkan dan arahkan ke SRL-NER.
