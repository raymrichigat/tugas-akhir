# Angka migrasi Bab 4.4 → v4 (cleaned) — referensi penulisan

> Sumber: v4_hybrid (KG kanonik, event sudah di-dedup via `clean_v4_events.py`) +
> v4_scoped (graf Person co-participation, nasab-only di-scope keluar via
> `clean_v4_hybrid_genealogy.py`). Model pemenang: **S4-augmentation**.
> Person SNA = `analysis/v4_scoped/`; Event = `analysis/v4_hybrid/event_centrality*`.

## Tabel 4.17 — Statistik jaringan tokoh (v4_scoped)
- Node (Person): 137 | Edge: 1.853 | Density: 0,1989
- Avg clustering (lokal): 0,7100 | Transitivity (global): 0,7957
- Komponen: 5 | Giant: 128 node (93,4%) | Diameter 5 | Avg path: 1,96
- Louvain: **8 komunitas, Q=0,2831** | greedy 10 (Q=0,2607) | Girvan-Newman 16 (Q=0,0301)
- ARI(Louvain, greedy) = 0,4737

## Tabel 4.18 — Top-10 PageRank (degree_cent | closeness | pagerank)
1. Muhammad — 0,7941 | 0,7906 | 0,0509
2. Ali bin Abu Thalib — 0,5735 | 0,6516 | 0,0240
3. Abu Jahal — 0,5515 | 0,6516 | 0,0230
4. Umar bin Al-Khaththab — 0,5809 | 0,6552 | 0,0223
5. Abu Bakar — 0,5441 | 0,6376 | 0,0212
6. Abu Sufyan bin Harb — 0,5368 | 0,6376 | 0,0193
7. Aisyah — 0,5221 | 0,6275 | 0,0186
8. Abu Azzah — 0,5147 | 0,6242 | 0,0161   (artefak clique peperangan, sisa — cf v3)
9. Khunais bin Hudzafah — 0,5147 | 0,6242 | 0,0161  (artefak clique, sisa)
10. Utsman bin Affan — 0,5221 | 0,6308 | 0,0158

## Tabel 4.19 — Top-10 Betweenness (v4_scoped)
1. Muhammad 0,2808 | 2. Jabir bin Abdullah 0,0635 | 3. Ummu Kultsum 0,0548 |
4. Husain bin Ali 0,0548 | 5. Ali bin Abu Thalib 0,0441 | 6. Abdullah bin Ubay bin Salul 0,0393 |
7. Al-Barra' bin Azib 0,0380 | 8. Ibnu Hajar 0,0380 (artefak perawi, cf Ibnu Hisyam v3) |
9. Salamah bin Al-Akwa' 0,0373 | 10. Abu Bakar 0,0294
> Catatan: graf padat (density 0,199, avg path 1,96) → betweenness kurang diskriminatif;
> nama periferal/perawi (Ibnu Hajar) naik. Muhammad tetap dominan mutlak (0,28 ≫ 0,06).

## Komunitas Louvain (v4_scoped, 8 komunitas Q=0,283)
- C1 (66): Muhammad, Ali, Umar, Abu Bakar, Aisyah, Utsman, Amr bin Umayyah, Hasan bin Ali, Abdullah bin Ubay, Mush'ab bin Umair
- C2 (47): Abu Jahal, Abu Sufyan, Khunais, Abu Azzah, Zainab, Zaid bin Haritsah, Ummu Kultsum, Husain bin Ali, Abdurrahman, Hamzah
- C3 (7): Musailamah, Urwah bin Mas'ud, Ka'b bin Zuhair… | C4-C8 kecil (2-3 anggota)

## Tabel 4.20 — Event PageRank (v4_hybrid cleaned, 35 event / 264 edge / density 0,4437 / 4 komponen / giant 32)
1. Perang Badr — PR 0,0965 | deg 27 | freq 53
2. Perang Uhud — 0,0889 | 29 | 43
3. Perang Khandaq — 0,0674 | 28 | 20
4. Perjanjian Hudaibiyah — 0,0442 | 24 | 20
5. Baiat Aqabah Kubra — 0,0424 | 23 | 4
6. Perang Dzul Usyairah — 0,0404 | 23 | 1  (freq-1, inflasi co-participation — caveat)
7. Perang Khaibar — 0,0382 | 21 | 12
8. Perang Bani Al-Ashfar — 0,0353 | 22 | 1  (freq-1)
9. Perang Dzatur Riqa' — 0,0348 | 21 | 2
10. Perang Tha'if — 0,0344 | 22 | 4
- Event betweenness top: Perang Uhud 0,1958 (#1 jembatan), Perang Khandaq 0,1346, Perjanjian Hudaibiyah 0,0264
- **PENTING:** event top-10 v4 = DOMINAN PEPERANGAN, TANPA lifecycle (Kelahiran/Wafat/Wahyu Pertama TIDAK ada di v4 — NER tak menangkap event frasa-verba). Beda dari v3 yang punya lifecycle enrichment manual. Narasi 4.4 event harus diubah: battle-dominated + lifecycle = keterbatasan.

## PENDING (butuh edit skrip v3→v4):
- Tabel 4.21 (G7 lokasi) + 4.22 (G8 lintas fase): `scenario_g7_g8.py` hardcode v3.
- Tabel 4.23 + Gambar 4.16 (G6 studi kasus): `visualize_case_study_events.py` cuma v2/v3.

## Perubahan narasi kunci v3→v4 (untuk rewrite 4.4):
- Density 0,085→0,199 (graf lebih padat, di-scope ke inti peserta) ; avg path 2,53→1,96
- Louvain Q 0,3851→0,2831 (struktur komunitas lebih lemah — inti padat) ; komunitas 15→8
- Top PageRank: Muhammad tetap #1 dominan; artefak nasab (Ma'ad/Matausyalakh/Abdullah) HILANG via scoping; Amr bin Umayyah #12 (bukan lagi top), Abu Azzah/Khunais = sisa artefak clique
- Event: battle-dominated, lifecycle hilang
- Scoping didokumentasikan: `clean_v4_hybrid_genealogy.py` buang PERSON 0-partisipasi-peristiwa (hanya taut nasab); KG kanonik utuh.
