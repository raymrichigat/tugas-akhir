# Skenario Pengujian Graf + Referensi — G1/G2/G3/G4

**Tanggal:** 2026-05-04
**Konteks:** Menjawab revisi Bu Diana di `revisi_dosen.md` (poin Graf + Uji Coba):
> *"Perlu uji coba lain selain centrality (community atau lainnya)"*
> *"Centrality -> fokus ke node (fokus ke graf gede nya, seperti clustering, ukuran network nya berapa, seperti density, dkk)"*
> *"Kasus perang badar, diamati keterlibatan nya apa saja lalu diamati graf nya (sampling beberapa event)... ambil beberapa contoh 3 atau 5 fitur, dengan periode yang jauh"*

Dokumen ini = **bahan diskusi** sebelum implementasi tambahan ke `src/analysis/sna_analysis.py`. Setelah disetujui Bu Diana, eksperimen yang dipilih akan diimplementasikan.

> **Ruang lingkup:** TA fokus ke **4 cluster pengujian (G1/G2/G3/G4)**. Graf hanya dijalankan pada hasil **NER terbaik (E4 dari `srl_ner_skenario.md`)** — tidak ada perbandingan graf antar E1/E3/E4 untuk simplicity.

---

## 1. Kondisi saat ini (baseline SNA)

**File implementasi:** `src/analysis/sna_analysis.py`
**Output saat ini:** `data/result/analysis/sna_metrics.csv`, `sna_summary.md`, (`sna_person_network.png` butuh matplotlib)

### 1.1 Statistik graf saat ini (Person co-participation)

| Aspek | Nilai |
|---|---:|
| Jumlah node (Person) | **174** |
| Jumlah edge | **1,164** |
| Density | **0.0773** |
| Connected components | **9** |
| Largest component | **157 nodes** |

### 1.2 Yang sudah dihitung (G1 — Node-level)

| Metrik | Top tokoh |
|---|---|
| Degree centrality | Muhammad (105 koneksi, 0.6069) |
| Betweenness centrality | Muhammad (0.4147), Abu Jahal (0.1298) |
| Closeness centrality | Muhammad (0.6543) |
| PageRank | Muhammad (0.0639), Abu Jahal (0.0278) |

### 1.3 Yang sudah dihitung (G3 — sebagian)

- Community detection: **Louvain (greedy modularity)** → 16 komunitas
  - Komunitas 1 (74 anggota): Muhammad, Abu Jahal, Abu Sufyan, Abu Bakar, Aisyah
  - Komunitas 2 (39 anggota): Utsman, Hamzah, Abu Lahab, Hakim bin Hizam
  - Komunitas 3 (26 anggota): Ali, Umar, Zaid bin Haritsah, Mush'ab
  - Komunitas 4–16: 2–6 anggota (fragmented)

### 1.4 Gap saat ini (per revisi Bu Diana)

- **Graph-level metrics tidak lengkap**: hanya density + components, belum ada clustering coefficient, transitivity, assortativity, average path length
- **Community detection hanya 1 metode** (Louvain) — Bu Diana minta uji coba metode lain
- **Belum ada studi kasus event sampling** — penting untuk validasi pipeline (kalau salah dari awal, fitur graf jadi salah)

---

## 2. Skenario G1 — Node-level Metrics (sudah ada, perlu konfirmasi cukup)

### 2.A Yang sudah dihitung
- **Degree centrality** — siapa paling banyak koneksi
- **Betweenness centrality** — siapa bridge antar kelompok
- **Closeness centrality** — siapa paling sentral
- **PageRank** — siapa paling authoritative (weighted)

### 2.B Pertimbangan tambahan (opsional)
- **Eigenvector centrality** — alternatif PageRank, sering disitir bareng (Labatut & Bost 2014)
- **Katz centrality** — varian PageRank dengan β regularization

**Rekomendasi:** 4 metrik existing sudah cukup standar (sesuai paper Aurangzeb et al. 2021 untuk SNA hadits + Labatut & Bost untuk character networks). Kalau Bu Diana minta tambah, eigenvector paling cepat (~5 baris kode).

---

## 3. Skenario G2 — Graph-level Metrics (BARU)

Berdasarkan revisi Bu Diana: "fokus ke graf gede nya, seperti clustering, ukuran network nya berapa, seperti density, dkk."

### 3.A Metrik yang akan ditambah

| Metrik | Definisi | Interpretasi untuk Sirah |
|---|---|---|
| **Density** ✅ sudah | edges aktual / edges maksimal | 0.0773 = jaringan **sparse** (wajar untuk historical narrative) |
| **Average clustering coefficient** | Rata-rata local clustering per node | Tinggi → tokoh cenderung berkelompok rapat |
| **Global clustering coefficient (transitivity)** | 3 × triangles / triplets | Tinggi → "teman dari teman juga teman" — komunitas erat |
| **Assortativity (degree)** | Korelasi degree antar tetangga | Positif → hub berhubungan dgn hub (Muhammad ↔ Abu Bakar); negatif → hub berhubungan dgn periferal |
| **Average shortest path length** | Rata-rata jarak antar pasang node | Pendek (~3-4) → world is small; Sirah expected ~3-5 |
| **Diameter** | Jarak terjauh antar 2 node | Estimasi ukuran "dunia" Sirah |
| **Number of connected components** ✅ sudah | 9 komponen | Sudah dihitung |
| **Giant component size** ✅ sudah | 157/174 = 90.2% | Sudah dihitung |
| **Network size (n_nodes, n_edges)** ✅ sudah | 174 nodes, 1164 edges | Sudah dihitung |

### 3.B Implementasi (sketsa kode)

```python
# Tambahan ke src/analysis/sna_analysis.py
def compute_graph_level_metrics(G):
    """Hitung graph-level metrics (selain centrality)."""
    metrics = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "density": nx.density(G),
        "avg_clustering": nx.average_clustering(G, weight="weight"),
        "transitivity": nx.transitivity(G),  # global clustering coefficient
        "degree_assortativity": nx.degree_assortativity_coefficient(G),
        "n_components": nx.number_connected_components(G),
    }

    # Path metrics — hanya valid kalau connected
    if nx.is_connected(G):
        metrics["diameter"] = nx.diameter(G)
        metrics["avg_path_length"] = nx.average_shortest_path_length(G)
    else:
        # Hitung di giant component saja
        giant = max(nx.connected_components(G), key=len)
        G_giant = G.subgraph(giant)
        metrics["giant_component_size"] = len(giant)
        metrics["diameter_giant"] = nx.diameter(G_giant)
        metrics["avg_path_length_giant"] = nx.average_shortest_path_length(G_giant)

    return metrics
```

**Output:** tambahan section `## Graph-level Metrics` di `sna_summary.md` + 1 row di tabel summary.
**Effort:** ~1 jam coding (1 fungsi + integrasi ke main).

---

## 4. Skenario G3 — Community Detection Comparison (BARU)

Berdasarkan revisi Bu Diana: "Perlu uji coba lain selain centrality (community atau lainnya)" — sudah ada Louvain, perlu uji metode lain untuk perbandingan.

### 4.A Algoritma yang akan dibandingkan

| Algoritma | Kompleksitas | Kekuatan | Kelemahan |
|---|---|---|---|
| **Louvain (greedy modularity)** ✅ sudah | O(n log n) | Cepat, dipakai luas | Bisa hasilkan komunitas terputus (Traag et al. 2019) |
| **Leiden** ⭐ rekomendasi | O(n log n) | Komunitas connected guaranteed, modularity lebih tinggi | Implementasi via library tambahan |
| **Girvan-Newman** | O(m²n) | Hierarchical, intuitif (edge betweenness) | Lambat untuk graf besar (174 nodes ~OK, tapi limit) |
| **Label Propagation** | O(m) | Sangat cepat, tidak deterministik | Tidak optimal modularity-wise |

**Rekomendasi:** **3 algoritma** — Louvain (existing) + Leiden + Girvan-Newman. Skip Label Propagation (kurang reliable, hasilnya tidak konsisten antar run).

### 4.B Metrik perbandingan

Untuk bandingkan antar algoritma:
- **Modularity score** (Q) — semakin tinggi semakin baik partisi
- **Number of communities** — apakah grain ukurannya masuk akal?
- **Largest community size** — apakah ada komunitas dominan?
- **Silhouette-like measure** (jika applicable)
- **Runtime** — penting untuk justifikasi pemilihan

**Tabel hasil yang diharapkan:**

| Algoritma | n_komunitas | Modularity Q | Largest comm | Runtime |
|---|---:|---:|---:|---:|
| Louvain ✅ | 16 | ? | 74 | ? |
| Leiden | ? | ? | ? | ? |
| Girvan-Newman | ? | ? | ? | ? |

### 4.C Implementasi (sketsa kode)

```python
# Tambahan ke src/analysis/sna_analysis.py
def detect_communities_multi(G):
    """Deteksi komunitas dengan 3 algoritma + bandingkan."""
    import time
    from networkx.algorithms.community import (
        greedy_modularity_communities,
        girvan_newman,
        modularity,
    )
    results = {}

    # 1. Louvain (existing)
    t0 = time.time()
    louvain = list(greedy_modularity_communities(G, weight="weight"))
    results["louvain"] = {
        "communities": louvain,
        "n": len(louvain),
        "modularity": modularity(G, louvain, weight="weight"),
        "runtime": time.time() - t0,
    }

    # 2. Leiden (butuh `pip install python-louvain` atau `igraph` + `leidenalg`)
    try:
        import igraph as ig
        import leidenalg
        t0 = time.time()
        G_ig = ig.Graph.from_networkx(G)
        partition = leidenalg.find_partition(G_ig, leidenalg.ModularityVertexPartition)
        leiden_comms = [set(G_ig.vs[node]["_nx_name"] for node in comm) for comm in partition]
        results["leiden"] = {
            "communities": leiden_comms,
            "n": len(leiden_comms),
            "modularity": modularity(G, leiden_comms, weight="weight"),
            "runtime": time.time() - t0,
        }
    except ImportError:
        print("WARN: leidenalg/igraph tidak terinstall, skip Leiden")

    # 3. Girvan-Newman (top-K split untuk dapat partisi)
    t0 = time.time()
    gn_gen = girvan_newman(G)
    # Ambil partisi dengan modularity tertinggi (max 20 split)
    best_q, best_comm = -1, None
    for i, comm in enumerate(gn_gen):
        if i >= 20: break
        q = modularity(G, comm, weight="weight")
        if q > best_q:
            best_q, best_comm = q, list(comm)
    results["girvan_newman"] = {
        "communities": best_comm,
        "n": len(best_comm) if best_comm else 0,
        "modularity": best_q,
        "runtime": time.time() - t0,
    }

    return results
```

**Output:** tambahan section `## Community Detection Comparison` di `sna_summary.md` + tabel + visualisasi 3 partisi side-by-side (opsional).
**Effort:** ~3 jam coding (Leiden butuh install package + handle conversion igraph ↔ networkx).
**Dependency baru:** `pip install igraph leidenalg`.

---

## 5. Skenario G4 — Studi Kasus 3 Event Sampling (BARU)

Berdasarkan revisi Bu Diana: "Kasus perang badar, diamati keterlibatan nya apa saja lalu diamati graf nya (sampling beberapa event)... ambil beberapa contoh 3 atau 5 fitur, dengan periode yang jauh."

### 5.A Pemilihan 3 event (periode menyebar)

| # | Event | Periode | Bab | Alasan dipilih |
|---|---|---|---|---|
| **G4.1** | **Hijrah ke Habasyah** | ~5 BH (sebelum Hijrah) | Hijrah ke Habasyah | Periode Mekah, fase persecution awal — small network expected |
| **G4.2** | **Perang Badar** ⭐ anchor | 2 H | Perang Badar Kubra | Anchor dari Bu Diana — Madinah awal, jaringan diuji aktif |
| **G4.3** | **Fathu Makkah** | 8 H | Fathu Makkah | Periode klimaks — large network expected, banyak tokoh |

**Justifikasi spasi temporal:** Hijrah Habasyah (~615 M) → Perang Badar (624 M) → Fathu Makkah (630 M). Span ~15 tahun, mencakup 3 fase utama Sirah.

### 5.B Yang dianalisis per event

Untuk setiap event:

1. **Daftar keterlibatan** (Person yang INVOLVED_IN event)
   - Dari `edges.csv` filter `target_name == event_name AND relation_type == "INVOLVED_IN"`
   - Sertakan `weight` masing-masing (proximity + period score)

2. **Sub-graf event** (Person-only, terbatas pada event ini + 1-hop neighbors)
   - Node: semua Person yang terlibat di event + tetangga langsung mereka
   - Edge: relasi antar mereka (KELUARGA/SAHABAT/MUSUH + co-participation di event lain)
   - Visualisasi: sub-graf dengan node berwarna (anggota event vs. tetangga)

3. **Metrik sub-graf**
   - Density sub-graf
   - Top 5 by degree, betweenness, PageRank (di sub-graf)
   - Community detection sub-graf (Louvain)

4. **Analisis kualitatif**
   - Apakah daftar keterlibatan masuk akal secara historis? (Cross-check dengan literatur)
   - Apakah tokoh sentral di sub-graf cocok dengan ekspektasi sejarah?
   - Apakah komunitas sub-graf merefleksikan faksi (Muslim vs. Quraisy vs. Munafiq)?

### 5.C Implementasi (sketsa kode)

```python
# File baru: src/analysis/sna_event_case_study.py
EVENTS_TO_ANALYZE = [
    "Hijrah ke Habasyah",
    "Perang Badar",
    "Fathu Makkah",
]

def case_study_event(edges_df, nodes_df, event_name, G_full):
    """Analisis sub-graf untuk satu event."""
    # 1. Daftar keterlibatan
    involved = edges_df[
        (edges_df["target_name"] == event_name) &
        (edges_df["relation_type"] == "INVOLVED_IN")
    ]
    persons_in_event = set(involved["source_name"].unique())
    print(f"[{event_name}] {len(persons_in_event)} tokoh terlibat")

    # 2. Sub-graf: tokoh terlibat + 1-hop neighbors
    nodes_subgraph = set(persons_in_event)
    for p in persons_in_event:
        if p in G_full:
            nodes_subgraph.update(G_full.neighbors(p))
    G_sub = G_full.subgraph(nodes_subgraph).copy()

    # 3. Metrik sub-graf
    sub_metrics = {
        "n_nodes": G_sub.number_of_nodes(),
        "n_edges": G_sub.number_of_edges(),
        "density": nx.density(G_sub),
        "n_persons_in_event": len(persons_in_event),
    }

    # 4. Top 5 centrality di sub-graf
    pr_sub = nx.pagerank(G_sub, weight="weight")
    top5_pr = sorted(pr_sub.items(), key=lambda x: -x[1])[:5]

    # 5. Visualisasi (highlight anggota event)
    visualize_subgraph(G_sub, persons_in_event, event_name, OUT_DIR)

    return {
        "event": event_name,
        "metrics": sub_metrics,
        "top5_pagerank": top5_pr,
        "involved_list": sorted(persons_in_event),
    }
```

**Output:**
- `data/result/analysis/case_studies/perang_badar.md`, `hijrah_habasyah.md`, `fathu_makkah.md`
- Sub-graf PNG: `case_studies/{event}_subgraph.png`
- Tabel agregat: `case_studies/comparison.csv` (3 event × metrik)

**Effort:** ~3-4 jam coding (loop + visualisasi + write reports).

---

## 6. Hubungan dengan Skenario SRL-NER (Opsi A)

**Keputusan (sesuai diskusi 2026-05-04):** Graf hanya dijalankan pada hasil **NER terbaik (E4 dari `srl_ner_skenario.md`)**.

**Implikasi:**
- Tidak ada perbandingan G1-G4 antar E1/E3/E4
- Bab 4 SRL-NER (perbandingan E1/E3/E4) **terpisah** dari Bab 4 Graf
- Pipeline:
  ```
  E4 (NER terbaik) → infer ke seluruh sirah_chunks_final.csv
                  → re-run relation extraction (dengan temporal-aware nanti)
                  → re-run sna_analysis.py (G1-G4)
                  → studi kasus 3 event (G4)
  ```

**Konsekuensi alur kerja:**
1. SRL-NER dulu (E1/E3/E4 → pilih terbaik)
2. Inferensi NER terbaik ke seluruh data Sirah
3. Re-run relation extraction
4. Re-run SNA dengan tambahan G2/G3
5. Studi kasus G4

Jadi **G1–G4 belum bisa dijalankan sebelum SRL-NER selesai dan inferensi final dilakukan.** Ini blocker yang penting untuk Bu Diana ketahui.

---

## 7. Referensi Paper Pendukung (2021–2026)

> **Catatan:** Paper umum SNA Islamic texts + character networks sudah ada di `referensi_sna_weighted_relations.md` (17 paper, dibuat 2026-04-24). Dokumen ini hanya menambahkan paper baru yang **spesifik** untuk G2/G3/G4.

### 7.A Community Detection Comparison (untuk G3)

#### A.1 — From Louvain to Leiden: Guaranteeing Well-Connected Communities ⭐⭐
- **Penulis & Tahun:** Traag, Waltman, van Eck, Scientific Reports 2019
- **Link:** https://www.nature.com/articles/s41598-019-41695-z
- **Inti:** Identifikasi flaw fundamental Louvain: bisa hasilkan komunitas **terputus** (disconnected). Leiden algorithm = perbaikan dengan refinement step yang menjamin komunitas connected.
- **Plus untuk G3 Sirah:**
  - Justifikasi langsung kenapa harus pakai Leiden, bukan Louvain saja
  - Sirah punya 9 connected components → kasus realistis untuk reproduksi masalah Louvain
  - Open access (Nature)
- **Minus / catatan:** 2019 (sebelum range 2021), tapi ini paper foundational yang harus disitir

#### A.2 — Comparative Analysis of Community Detection Algorithms on SNAP Social Circles
- **Penulis & Tahun:** arxiv 2025
- **Link:** https://arxiv.org/abs/2502.04341
- **Inti:** Komparasi lengkap Louvain vs Leiden vs Girvan-Newman vs Label Propagation vs lainnya di dataset benchmark.
- **Plus untuk G3 Sirah:**
  - Tabel komparasi langsung bisa direplikasi struktur metriknya
  - 2025 — fresh
- **Minus / catatan:** Arxiv preprint, dataset bukan literary text

#### A.3 — Evaluation of Community Detection on Real-World Networks
- **Penulis & Tahun:** Springer SNAM 2024
- **Link:** https://link.springer.com/article/10.1007/s13278-024-01324-8
- **Inti:** Evaluasi metode community detection pada real-world networks (bukan synthetic). Membandingkan modularity, runtime, scalability.
- **Plus untuk G3 Sirah:**
  - Real-world (bukan benchmark sintetis) — closer ke kondisi Sirah
  - Memberi metrik perbandingan standar yang bisa dipakai di tabel G3.B
- **Minus / catatan:** Paywalled (akses ITS)

#### A.4 — A Case Study Comparing Twitter Communities by Louvain and Leiden
- **Penulis & Tahun:** ACM WWW Companion 2024
- **Link:** https://dl.acm.org/doi/10.1145/3589335.3651892
- **Inti:** Perbandingan praktis Louvain vs Leiden di kasus nyata (Twitter perang Ukraina 2022). Menunjukkan dampak perbedaan algoritma terhadap interpretasi komunitas.
- **Plus untuk G3 Sirah:**
  - Format "case study perbandingan" — bisa dijadikan template Bab 4 Sirah
  - Real-world, bukan benchmark
- **Minus / catatan:** Paywalled, domain Twitter ≠ historical text

### 7.B Graph-Level Metrics & Character Networks (untuk G2)

#### B.1 — Network Extraction and Analysis of Character Relationships in Chinese Literary Works
- **Penulis & Tahun:** PMC 2022
- **Link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC9124099/
- **Inti:** Membangun character network dari karya sastra Tiongkok dengan metrik: degree distribution, density, clustering coefficient, shortest path, diameter, centrality.
- **Plus untuk G2 Sirah:**
  - **Sangat relevan** — character network + literary text + suite metrik graph-level identik dengan yang Sirah butuh
  - Sudah ada di `referensi_sna_weighted_relations.md` (paper #5), tapi disitir ulang khusus untuk G2
- **Minus / catatan:** Domain sastra Tiongkok (fiksi) ≠ historical narrative

#### B.2 — Extraction and Analysis of Fictional Character Networks: A Survey
- **Penulis & Tahun:** Labatut & Bost, ACM Computing Surveys 2019
- **Link:** https://arxiv.org/abs/1907.02704
- **Inti:** Survey komprehensif character networks: ekstraksi, metrik, analisis, application.
- **Plus untuk G2 Sirah:**
  - **Wajib disitir** sebagai overview di Bab 2 (sub-bab character network)
  - Memberi taxonomi metrik graph-level + node-level untuk character network
- **Minus / catatan:** 2019 (sebelum range 2021), tapi seminal — must-cite

### 7.C Studi Kasus Event-based Sub-graph (untuk G4)

#### C.1 — Aurangzeb et al. Hadith Narrators Network ⭐⭐
- **Penulis & Tahun:** Aurangzeb et al., J. King Saud Univ. CIS 2021
- **Link:** https://www.sciencedirect.com/science/article/pii/S1319157821000215
- **Inti:** SNA hadits Sahih Bukhari → 16 communities (kebetulan sama dengan Sirah!), pola geografis Makkah-Madinah-Kufa-Baghdad.
- **Plus untuk G4 Sirah:**
  - **Paling dekat dengan TA** — SNA Islamic texts dengan komunitas + analisis periodisasi
  - Sudah di `referensi_sna_weighted_relations.md` paper #1, perlu disitir lagi untuk G4
- **Minus / catatan:** Hadits chains ≠ event-based co-participation, tapi metodologi mirip

> Catatan untuk G4 (event sampling): tidak banyak paper yang spesifik membahas "sub-graf per event" dari historical text. Paling dekat = analisis komunitas geografis di Aurangzeb et al. Justifikasi G4 lebih ke **revisi Bu Diana langsung** + **validasi pipeline** (kalau salah dari awal, fitur graf jadi salah) daripada precedent literatur.

### 7.D Top 5 Sitasi Prioritas (untuk Bab 2 Graf)

1. **A.1 — Traag et al. 2019 (Louvain → Leiden)** ⭐⭐ — wajib untuk justifikasi G3
2. **B.2 — Labatut & Bost Survey 2019** ⭐⭐ — wajib untuk overview character network
3. **C.1 — Aurangzeb et al. 2021** ⭐⭐ — paling dekat domain (Islamic texts)
4. **B.1 — Chinese Literary Networks 2022** — character network + suite metrik
5. **A.4 — Twitter Louvain vs Leiden Case Study 2024** — template Bab 4

---

## 8. Pertanyaan & Bahan Diskusi untuk Bu Diana

### 8.1 Pertanyaan klarifikasi

1. **Setuju dengan scope 4 cluster (G1+G2+G3+G4)?** Atau ada yang mau ditambah/kurangi?
2. **G2 — graph-level metrics:** 7 metrik (density, clustering avg, transitivity, assortativity, diameter, avg path, components) sudah cukup, atau perlu lebih?
3. **G3 — community detection:** 3 algoritma (Louvain + Leiden + Girvan-Newman) sudah cukup, atau perlu tambah Label Propagation / Spectral?
4. **G4 — pemilihan 3 event:**
   - Saya usulkan: Hijrah ke Habasyah, Perang Badar, Fathu Makkah
   - Alternatif yang Bu Diana pertimbangkan?
5. **Opsi A (graf hanya pakai NER E4)** sudah tepat, atau Bu Diana minta perbandingan graf antar E1/E3/E4 juga?
6. **Format output Bab 4:** sub-bab "Pengujian Graf" terpisah dari "Pengujian NER", atau jadi satu?

### 8.2 Bahan diskusi dengan rujukan paper

- **Justifikasi G2:** rujuk B.1 (Chinese Lit) + B.2 (Labatut Survey) — character network suite metrik
- **Justifikasi G3 (perlu Leiden):** rujuk A.1 (Traag 2019) — Louvain bisa hasilkan komunitas terputus
- **Justifikasi G4 (event sampling):** alasan utama = revisi Bu Diana langsung + validasi pipeline; pendamping = C.1 (Aurangzeb) sebagai metodologi SNA Islamic texts
- **Konteks domain:** rujuk paper SNA Islamic texts di `referensi_sna_weighted_relations.md` (Aurangzeb hadits, MIS, dll.)

---

## 9. Implementasi (setelah skenario disepakati)

### 9.1 Estimasi effort

| Cluster | File yang berubah | Estimasi |
|---|---|---|
| G1 (sudah ada) | — | 0 jam |
| G2 (graph-level) | `src/analysis/sna_analysis.py` (1 fungsi baru) | ~1 jam |
| G3 (community comparison) | `src/analysis/sna_analysis.py` (1 fungsi baru, install igraph+leidenalg) | ~3 jam |
| G4 (event sampling) | `src/analysis/sna_event_case_study.py` (file baru) | ~3-4 jam |
| Update `sna_summary.md` template | Re-format output | ~1 jam |

**Total estimasi:** ~8-9 jam coding + ~30 menit run.

### 9.2 Prasyarat penting

**G1-G4 tidak bisa dijalankan sebelum:**
1. ✅ SRL-NER E1+E3+E4 selesai (lihat `srl_ner_skenario.md`)
2. ✅ NER terbaik (E4) dipilih
3. ✅ Inferensi NER terbaik ke seluruh `sirah_chunks_final.csv`
4. ✅ Re-run relation extraction (dengan temporal-aware dari revisi #1)
5. **DAN BARU** → re-run SNA dengan G1-G4

### 9.3 Dependency baru

```bash
pip install igraph leidenalg matplotlib
```

Untuk Leiden algorithm + visualisasi sub-graf.

---

## 10. Output yang Diharapkan

### 10.1 File output

```
data/result/analysis/
├── sna_metrics.csv                       (existing, diperbarui)
├── sna_summary.md                        (existing, diperbarui dengan G2 + G3)
├── sna_person_network.png                (existing)
├── community_comparison.csv              (G3 — baru)
├── community_comparison.png              (G3 — baru, visualisasi 3 partisi)
└── case_studies/                         (G4 — folder baru)
    ├── hijrah_habasyah.md
    ├── hijrah_habasyah_subgraph.png
    ├── perang_badar.md
    ├── perang_badar_subgraph.png
    ├── fathu_makkah.md
    ├── fathu_makkah_subgraph.png
    └── comparison.csv
```

### 10.2 Tabel hasil utama (untuk Bab 4)

**Tabel G2 — Graph-level Metrics:**

| Metrik | Nilai | Interpretasi |
|---|---:|---|
| Density | 0.0773 | Sparse network (wajar untuk historical narrative) |
| Avg clustering coefficient | ? | ? |
| Transitivity (global clustering) | ? | ? |
| Degree assortativity | ? | ? (positif → hub-hub; negatif → hub-periferal) |
| Diameter (giant component) | ? | ? |
| Avg shortest path | ? | ? |

**Tabel G3 — Community Detection Comparison:**

| Algoritma | n_komunitas | Modularity Q | Largest comm | Runtime |
|---|---:|---:|---:|---:|
| Louvain | 16 | ? | 74 | ? |
| Leiden | ? | ? | ? | ? |
| Girvan-Newman | ? | ? | ? | ? |

**Tabel G4 — Event Sub-graph Comparison:**

| Event | Periode | n_persons | n_edges | Density | Top tokoh (PageRank) |
|---|---|---:|---:|---:|---|
| Hijrah ke Habasyah | ~5 BH | ? | ? | ? | ? |
| Perang Badar | 2 H | ? | ? | ? | ? |
| Fathu Makkah | 8 H | ? | ? | ? | ? |

### 10.3 Analisis kualitatif

Untuk Bab 4, perlu jawaban:
- Apakah Sirah punya struktur **scale-free** seperti Aurangzeb et al. di hadits?
- Apakah Leiden memperbaiki community detection dibanding Louvain (modularity lebih tinggi, komunitas connected)?
- Untuk 3 event: apakah keterlibatan dan tokoh sentral cocok dengan ekspektasi sejarah?
- Apakah ukuran sub-graf event berkorelasi dengan periode (Mekah kecil → Madinah besar)?
