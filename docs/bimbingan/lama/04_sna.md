# Laporan Bimbingan — Bagian 4: Social Network Analysis (SNA)

**Mahasiswa:** Rayssa Ravelia (5025211219)
**Pembimbing:** Prof. Dr. Diana Purwitasari
**Topik TA:** Knowledge Graph Sirah Nabawiyah
**Tanggal laporan:** 30 April 2026

---

## 1. Latar Belakang Revisi

Pada bimbingan sebelumnya, dosen memberi catatan revisi keempat:

> *"Social network analysis → pengujian (degree of centrality, dll) cari yang cocok dengan case Sirah Nabawiyah itu apa."*

**Konteks:** Knowledge Graph yang sudah dibangun (897 nodes, 370 edges) baru bisa di-query secara struktural di Neo4j. Belum ada **analisis kuantitatif** untuk menjawab pertanyaan seperti:
- Siapa tokoh paling sentral / berpengaruh dalam Sirah?
- Siapa yang menjadi "jembatan" antar kelompok / faksi?
- Apakah ada komunitas (cluster) tokoh yang bisa diidentifikasi otomatis?

SNA memberikan jawaban kuantitatif untuk pertanyaan-pertanyaan tersebut.

---

## 2. Definisi & Pemilihan Metrik untuk Case Sirah Nabawiyah

### 2.1 Apa itu SNA?
**Social Network Analysis** = analisis jaringan sosial yang merepresentasikan tokoh sebagai **node** dan hubungan antar mereka sebagai **edge**, lalu menghitung metrik struktural untuk mengidentifikasi pola sosial.

### 2.2 Metrik yang Dipilih (4 metrik centrality + 1 community)

Pemilihan metrik mempertimbangkan **karakter teks Sirah** (narrative-driven, banyak event kolektif, struktur kabilah/aliansi):

| Metrik | Definisi | Pertanyaan untuk Sirah |
|---|---|---|
| **Degree Centrality** | Jumlah koneksi langsung tokoh | Siapa yang paling sering terlibat dengan banyak tokoh lain? |
| **Betweenness Centrality** | Seberapa sering tokoh berada di shortest path antar pasangan tokoh lain | Siapa "jembatan" antar kelompok (misal antara Muhajirin & Anshar, atau Muslimin & Quraisy)? |
| **Closeness Centrality** | Rata-rata kedekatan tokoh ke semua tokoh lain | Siapa yang paling cepat "menjangkau" seluruh jaringan? |
| **PageRank** | Authoritativeness — node yang dirujuk oleh node penting jadi penting juga | Siapa tokoh paling berpengaruh secara hirarkis? |
| **Community Detection (Louvain)** | Greedy modularity → mengelompokkan node yang lebih rapat antar mereka | Apa saja faksi / kelompok besar dalam Sirah? |

**Kenapa 4 metrik centrality, bukan satu?** Karena tiap metrik menjawab pertanyaan berbeda. Tokoh dengan degree tinggi belum tentu betweenness tinggi (banyak teman, tapi bukan penghubung antar kelompok). Triangulasi dari 4 metrik memberi gambaran lebih utuh.

---

## 3. Posisi dalam Pipeline

```
nodes.csv + edges.csv (dari Relation Extraction)
       ↓
  ┌─────────────────────────────────────────┐
  │ build_person_coparticipation_graph()    │
  │   └─ Person↔Person dari shared events   │
  │      + Person-Person langsung           │
  │        (KELUARGA, SAHABAT, MUSUH)       │
  └─────────────────────────────────────────┘
       ↓
  Graph (NetworkX): 174 person nodes
       ↓
  ┌─────────────────────────────────────────┐
  │ compute_centrality_metrics()            │
  │   ├─ Degree, Betweenness, Closeness     │
  │   └─ PageRank (weighted)                │
  └─────────────────────────────────────────┘
       ↓
  ┌─────────────────────────────────────────┐
  │ detect_communities() — Louvain          │
  └─────────────────────────────────────────┘
       ↓
  Output: sna_metrics.csv, sna_summary.md, sna_person_network.png
```

Implementasi: `src/analysis/sna_analysis.py` (NetworkX).

---

## 4. Alur Detail (Step by Step)

### Step 1 — Bangun Person Co-Participation Graph

Input: `edges.csv`. Karena fokus SNA adalah jaringan sosial **antar tokoh**, hanya node Person yang dipakai. Edge dibangun dari 2 sumber:

**(a) Co-participation lewat shared events:**
- Group `INVOLVED_IN` by event → daftar tokoh yang terlibat di event yang sama.
- Untuk tiap pasangan tokoh di event yang sama → tambah edge dengan `weight += 1` per shared event.
- Atribut edge: `relation_type=CO_PARTICIPATION`, `shared_events=[list event]`.

**(b) Relasi Person-Person langsung** (dari Section 03 — KELUARGA, SAHABAT, MUSUH):
- Jika edge sudah ada (sudah co-participate) → tambahkan `weight` & gabung `relation_type`.
- Jika belum ada → tambah edge baru dengan weight & relation_type sesuai.

### Step 2 — Hitung 4 Centrality Metrics

```python
degree      = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G, weight="weight")  # weighted
closeness   = nx.closeness_centrality(G)
pagerank    = nx.pagerank(G, weight="weight")                # weighted
```

Bobot edge (jumlah shared events + weight relasi langsung) dipakai untuk metrik weighted.

### Step 3 — Community Detection (Louvain Greedy Modularity)

```python
from networkx.algorithms.community import greedy_modularity_communities
communities = greedy_modularity_communities(G, weight="weight")
```

Algoritma greedy: gabungkan node yang menambah modularity terbesar, ulangi sampai tidak ada perbaikan. Cocok untuk graph berukuran sedang (<10k node).

### Step 4 — Generate Output

3 file output:
- **`sna_metrics.csv`** — per-node: name, 4 centrality scores, degree count, community ID.
- **`sna_summary.md`** — markdown report: top-20 per metric + daftar komunitas.
- **`sna_person_network.png`** — visualisasi (node size ∝ PageRank, warna = community).

---

## 5. Input dan Output

### Input
| File | Isi |
|---|---|
| `data/result/relation_result/nodes.csv` | 897 nodes (658 PERSON, 41 EVENT, 51 LOCATION, 147 TIME) |
| `data/result/relation_result/edges.csv` | 370 edges dengan kolom `weight` |

### Output
| File | Isi |
|---|---|
| `data/result/analysis/sna_metrics.csv` | 174 baris (tokoh) × 7 kolom (4 centrality + degree + community + name) |
| `data/result/analysis/sna_summary.md` | Ringkasan markdown — top-20 per metrik + 16 komunitas |
| `data/result/analysis/sna_person_network.png` | (optional) butuh `pip install matplotlib` untuk generate |

---

## 6. Hasil

### 6.1 Statistik Graph

| Properti | Nilai |
|---|---|
| Jumlah node (Person) | **174** |
| Jumlah edge | **1.164** |
| Density | 0.0773 (sparse, tipikal social graph) |
| Connected components | 9 |
| Largest component | 157 nodes (90% dari graph) |

> **Catatan:** Dari 658 PERSON di Knowledge Graph, hanya 174 yang muncul di SNA graph. Sisanya tidak punya edge co-participation (cuma muncul di chunk solo) atau relasi Person-Person langsung. Filter ini natural — SNA hanya bermakna untuk node yang punya hubungan.

### 6.2 Top 10 — Degree Centrality (paling banyak koneksi)

| Rank | Nama | Degree | Centrality |
|---|---|---:|---:|
| 1 | **Muhammad** | 105 | 0.6069 |
| 2 | Abu Jahal | 66 | 0.3815 |
| 3 | Ali bin Abu Thalib | 56 | 0.3237 |
| 4 | Abdullah bin Ubay bin Salul | 53 | 0.3064 |
| 5 | Abu Sufyan bin Harb | 53 | 0.3064 |
| 6 | Umar bin Al-Khaththab | 52 | 0.3006 |
| 7 | Abu Azzah | 52 | 0.3006 |
| 8 | Zaid bin Haritsah | 49 | 0.2832 |
| 9 | Utsman bin Affan | 43 | 0.2486 |
| 10 | Zainab | 42 | 0.2428 |

**Interpretasi:** Muhammad muncul dengan 105 koneksi langsung — hampir 2× rank-2 (Abu Jahal). Ini konsisten dengan posisi Beliau sebagai *protagonis sentral* narasi Sirah. Abu Jahal di rank-2 karena banyak terlibat sebagai antagonis di event-event awal kenabian + Perang Badar.

### 6.3 Top 10 — Betweenness Centrality (jembatan antar kelompok)

| Rank | Nama | Betweenness |
|---|---|---:|
| 1 | **Muhammad** | 0.4147 |
| 2 | Abu Jahal | 0.1298 |
| 3 | Utsman bin Affan | 0.0705 |
| 4 | Ali bin Abu Thalib | 0.0688 |
| 5 | Rifa'ah bin Abdul Mundzir | 0.0514 |
| 6 | Aisyah | 0.0454 |
| 7 | Amr bin Umayyah | 0.0416 |
| 8 | Mush'ab bin Umair | 0.0386 |
| 9 | Yusuf | 0.0336 |
| 10 | Umayyah bin Khalaf | 0.0316 |

**Interpretasi:** Muhammad adalah *bridge* paling kritis — 41% shortest path dalam graph melewati Beliau. Aisyah (rank-6) menarik: degree-nya tidak top, tapi betweenness tinggi karena menghubungkan kelompok keluarga Nabi dengan tokoh-tokoh Madinah. Mush'ab bin Umair (rank-8) konsisten dengan perannya sebagai duta Islam pertama ke Madinah.

### 6.4 Top 10 — PageRank (paling authoritative)

| Rank | Nama | PageRank |
|---|---|---:|
| 1 | **Muhammad** | 0.0639 |
| 2 | Abu Jahal | 0.0278 |
| 3 | Ali bin Abu Thalib | 0.0206 |
| 4 | Abdullah bin Ubay bin Salul | 0.0172 |
| 5 | Umar bin Al-Khaththab | 0.0167 |
| 6 | Abu Sufyan bin Harb | 0.0167 |
| 7 | Zaid bin Haritsah | 0.0160 |
| 8 | Abu Azzah | 0.0156 |
| 9 | Amr bin Umayyah | 0.0153 |
| 10 | Utsman bin Affan | 0.0140 |

**Interpretasi:** PageRank menggabungkan kuantitas + kualitas koneksi. Muhammad masih rank-1 dengan margin lebih besar (2.3× rank-2). Top-10 PageRank didominasi sahabat Khulafaur Rasyidin (Ali, Umar, Utsman) dan tokoh utama Quraisy (Abu Jahal, Abu Sufyan, Abdullah bin Ubay) — sesuai dengan struktur narasi Sirah.

### 6.5 Closeness Centrality

| Rank | Nama | Closeness |
|---|---|---:|
| 1 | **Muhammad** | 0.6543 |
| 2 | Abu Jahal | 0.5153 |
| 3 | Ali bin Abu Thalib | 0.5115 |
| 4 | Abdullah bin Ubay bin Salul | 0.4936 |
| 5 | Umar bin Al-Khaththab | 0.4919 |

**Interpretasi:** Muhammad rata-rata berjarak 1/0.65 ≈ 1.5 hop dari semua tokoh lain — artinya hampir semua tokoh dapat dijangkau dengan 1–2 perantara. Konsisten dengan peran sentralnya.

### 6.6 Konvergensi 4 Metrik pada Tokoh Utama

| Tokoh | Degree | Betweenness | Closeness | PageRank | Konvergen? |
|---|:---:|:---:|:---:|:---:|:---:|
| Muhammad | #1 | #1 | #1 | #1 | ✅ Ya |
| Abu Jahal | #2 | #2 | #2 | #2 | ✅ Ya |
| Ali bin Abu Thalib | #3 | #4 | #3 | #3 | ✅ Konvergen |
| Umar bin Al-Khaththab | #6 | #19 | #5 | #5 | ⚠️ Beda di betweenness |

**Insight:** Konvergensi 4 metrik di rank #1–3 menunjukkan validitas hasil — tokoh-tokoh kunci memang dominan di semua dimensi sentralitas, bukan artefak metrik tertentu.

### 6.7 Community Detection — 16 Komunitas

| Komunitas | Anggota | Tokoh Utama |
|---|---:|---|
| **#1** | 74 | Muhammad, Abu Jahal, Abu Sufyan, Abu Azzah, Abu Bakar, Aisyah |
| **#2** | 39 | Utsman bin Affan, Zainab, Abu Hurairah, Abu Musa, Hamzah bin Abdul Muththalib |
| **#3** | 26 | Ali bin Abu Thalib, Umar, Zaid bin Haritsah, Mush'ab bin Umair, Sa'd bin Mu'adz |
| #4 | 6 | Tokoh-tokoh suku Anshar (Rifa'ah, Al-Mundzir, Sa'd bin Ubadah, Usaid bin Hudhair) |
| #5 | 4 | Para Nabi sebelumnya (Ibrahim, Isma'il) + nasab |
| #6 | 3 | Khadijah, Waraqah bin Naufal, Zaid bin Haritsah bin Syurahbil |
| #7-16 | 2-3 | Komunitas-komunitas kecil (kelompok kabilah / silsilah) |

**Insight:**
- **Komunitas #1 (74 anggota)** adalah klaster besar yang berisi *tokoh-tokoh utama Makkah* (Muhammad, sahabat awal, dan musuh-musuh utama Quraisy). Wajar Muhammad ada di sini karena banyak event awal Sirah berlangsung di Makkah.
- **Komunitas #2 (39)** lebih banyak tokoh masa Madinah & Khulafaur Rasyidin pasca-Hijrah.
- **Komunitas #3 (26)** kelompok Ali, Umar, Zaid bin Haritsah — mungkin terkait misi-misi militer & dakwah.
- **Komunitas #5 (Ibrahim & Isma'il)** terisolasi karena hanya muncul di BAB awal yang membahas asal-usul Bangsa Arab.

---

## 7. Manfaat Praktis

1. **Validasi KG:** Konvergensi 4 metrik di tokoh utama (Muhammad #1 di semua) memvalidasi bahwa Knowledge Graph yang dibangun **konsisten dengan ekspektasi historis** — bukan random graph.
2. **Insight kuantitatif untuk laporan:** Dapat dikutip di Bab 4 sebagai bukti bahwa pipeline berhasil meng-capture struktur sosial Sirah.
3. **Visual evidence:** Visualisasi `sna_person_network.png` (setelah matplotlib di-install) bisa jadi figure utama laporan TA.
4. **Foundation untuk analisis lebih lanjut:** Komunitas yang terdeteksi bisa di-cross-check dengan literatur Sirah (apakah komunitas #2 benar-benar dominan masa Madinah?).

---

## 8. Limitasi yang Perlu Di-acknowledge

1. **Hanya 174 dari 658 PERSON** masuk SNA graph — 484 tokoh "dihilangkan" karena tidak punya co-participation. Ini natural tapi perlu ditulis di laporan.
2. **Co-participation dari INVOLVED_IN** sangat bergantung pada **kualitas EVENT extraction**. Jika manual labelling under-extract event, banyak relasi person-person yang hilang.
3. **Louvain greedy** adalah heuristik — community boundary tidak deterministik. Hasil bisa sedikit berbeda jika random seed diubah.
4. **Tidak ada dimensi waktu** — Umar bin Al-Khaththab di-treat sebagai satu node, padahal sebelum & sesudah masuk Islam relasinya berubah (musuh → sahabat).
5. **Visualisasi belum ter-generate** — perlu `pip install matplotlib` lalu re-run script.

---

## 9. Langkah Berikutnya

1. **Install matplotlib & re-run** untuk generate `sna_person_network.png`:
   ```bash
   pip install matplotlib
   python src/analysis/sna_analysis.py
   ```
2. **Cross-validate komunitas** dengan literatur Sirah — minta dosen/expert verify apakah pengelompokan otomatis Louvain masuk akal.
3. **Tambah metrik tambahan opsional** (jika dosen minta): eigenvector centrality, clustering coefficient, k-core decomposition.
4. **Setelah model NER final dijalankan** → re-run SNA dengan output NER (bukan manual labelling). Bandingkan: apakah top-10 tokoh tetap konsisten? Apakah ada tokoh baru yang muncul karena NER menangkap entitas yang missed manual labelling?
5. **Visualisasi per-komunitas** — render PNG terpisah untuk komunitas #1, #2, #3 (yang besar) supaya nama tokoh tidak overlap di figure utama.

---

## 10. File Terkait

| File | Deskripsi |
|---|---|
| `src/analysis/sna_analysis.py` | Pipeline SNA (NetworkX) |
| `data/result/analysis/sna_metrics.csv` | 174 tokoh × 7 metrik |
| `data/result/analysis/sna_summary.md` | Markdown report — top-20 per metrik + 16 komunitas |
| `data/result/analysis/sna_person_network.png` | Visualisasi (belum ter-generate, butuh matplotlib) |
| `referensi_sna_weighted_relations.md` | 17 paper rujukan (SNA teks Islam, character network, Louvain, dll) |
