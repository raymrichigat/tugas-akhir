# Referensi Paper: Social Network Analysis & Weighted Relations pada Knowledge Graph

**Konteks:** Rujukan untuk Tugas Akhir — Knowledge Graph Sirah Nabawiyah
**Disusun:** 2026-04-24

---

## A. Social Network Analysis pada Teks Islam (Hadits / Sirah)

### 1. Social Network Analysis of Hadith Narrators from Sahih Bukhari
- **Penulis:** Aurangzeb et al.
- **Publikasi:** Journal of King Saud University – Computer and Information Sciences (2021)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1319157821000215) | [arXiv](https://arxiv.org/abs/2102.02009) | [IEEE Xplore](https://ieeexplore.ieee.org/document/9348299/)
- **Ringkasan:** Membangun social network dari rantai perawi hadits Sahih Bukhari. Jaringan perawi direpresentasikan sebagai graf sosial. Ditemukan bahwa jaringan bersifat **scale-free network** dan berhasil mengidentifikasi 16 komunitas perawi. Perawi berpengaruh diidentifikasi dari generasi Sahabah dan generasi berikutnya. Jaringan awalnya berpusat di **Makkah dan Madinah**, kemudian bergeser ke Kufa, Baghdad, dan Asia Tengah.
- **Relevansi untuk TA:**
  - Metodologi sangat mirip: sama-sama menganalisis jaringan tokoh Islam dari teks historis
  - Metrik yang digunakan: degree centrality, betweenness centrality, community detection — sama dengan yang kita implementasikan di `sna_analysis.py`
  - Hasil 16 komunitas perawi bisa dibandingkan dengan komunitas tokoh Sirah kita (juga 16 komunitas!)
  - Pola geografis (Makkah → Madinah) paralel dengan periodisasi bab dalam Sirah

### 2. QASiNa: Religious Domain Question Answering using Sirah Nabawiyah
- **Penulis:** (Tim peneliti NLP Bahasa Indonesia)
- **Publikasi:** arXiv (2023)
- **Link:** [arXiv PDF](https://arxiv.org/pdf/2310.08102)
- **Ringkasan:** Dataset QA (Question Answering) yang dikompilasi dari literatur **Sirah Nabawiyah dalam Bahasa Indonesia**. Menunjukkan pendekatan komputasional modern untuk mempelajari biografi Nabi Muhammad.
- **Relevansi untuk TA:**
  - Sumber data yang sama: Sirah Nabawiyah berbahasa Indonesia
  - Menunjukkan ada penelitian NLP aktif pada domain Sirah
  - Bisa dijadikan rujukan bahwa pendekatan komputasional pada Sirah valid secara akademis

### 3. Multi-IsnadSet (MIS) for Sahih Muslim Hadith with Chain of Narrators
- **Publikasi:** ScienceDirect (2024)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2352340924004086)
- **Ringkasan:** Multi-directed graph structure yang merepresentasikan interaksi kompleks antar perawi hadits. Corpus hadits didesain sebagai **knowledge graph** menggunakan ontologi SemanticHadith, menghasilkan RDF-based hadith knowledge graph dari enam koleksi hadits utama.
- **Relevansi untuk TA:**
  - Sama-sama membangun knowledge graph dari teks Islam
  - Pendekatan ontologi bisa menjadi referensi untuk struktur knowledge graph Sirah
  - Menunjukkan bahwa representasi graf untuk teks Islam sudah established

---

## B. Character Network Analysis pada Teks Naratif

### 4. Character Networks and Centrality
- **Penulis:** Labatut & Bost
- **Publikasi:** EPFL Infoscience
- **Link:** [EPFL](https://infoscience.epfl.ch/entities/publication/748b23d5-6065-40fe-b272-f3800058b224) | [ResearchGate](https://www.researchgate.net/publication/272438832_Character_Networks_and_Centrality)
- **Ringkasan:** Membangun **character network** dari teks naratif di mana vertex = karakter dan edge = interaksi. Menggunakan empat metrik centrality: **degree, closeness, betweenness, dan eigenvector**. Betweenness centrality berfungsi sebagai ukuran kontrol karakter terhadap alur narasi.
- **Relevansi untuk TA:**
  - Metodologi yang sama persis: membangun graf karakter dari teks naratif
  - Empat metrik centrality yang digunakan identik dengan implementasi kita
  - Interpretasi betweenness centrality sebagai "kontrol atas narasi" bisa diterapkan pada analisis tokoh Sirah (Muhammad memiliki betweenness 0.4147)

### 5. Network Extraction and Analysis of Character Relationships in Chinese Literary Works
- **Publikasi:** PMC / MDPI (2022)
- **Link:** [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9124099/)
- **Ringkasan:** Ekstraksi dan analisis jaringan karakter dari karya sastra Tiongkok. Relasi dibangun berdasarkan **co-occurrence** dua nama dalam satu kalimat/paragraf. Jaringan bersifat **undirected dan weighted**, dengan weight dihitung dari jumlah co-occurrence. Fitur jaringan yang dianalisis: degree distribution, density, clustering coefficient, shortest path length, diameter, dan centrality.
- **Relevansi untuk TA:**
  - Pendekatan co-occurrence sangat mirip: kita juga membangun relasi berdasarkan co-participation dalam event yang sama
  - Weighted graph dengan co-occurrence frequency = konsep yang sama dengan `build_person_coparticipation_graph()` kita
  - Metrik jaringan yang dianalisis sama (density, components, centrality)

### 6. Measuring Centrality in Film Narratives using Dynamic Character Interaction Networks
- **Publikasi:** Social Networks / ScienceDirect (2020)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378873320300228)
- **Ringkasan:** Mengukur centrality karakter dalam narasi film menggunakan **dynamic network** yang menghormati urutan waktu (time-ordering). Argumen utama: ukuran pentingnya karakter harus berbasis representasi jaringan dinamis karena urutan dan sequence sentral dalam narasi.
- **Relevansi untuk TA:**
  - Konsep dynamic network relevan untuk relasi PRECEDES (kronologi event) yang sudah kita implementasikan
  - Periodisasi Sirah (Makkah → Madinah) bisa dianalisis sebagai dynamic network

### 7. Extraction and Analysis of Fictional Character Networks: A Survey
- **Penulis:** Labatut & Bost
- **Publikasi:** ACM Computing Surveys, Vol. 52 No. 5
- **Link:** [ACM](https://dl.acm.org/doi/abs/10.1145/3344548)
- **Ringkasan:** Survey komprehensif tentang ekstraksi dan analisis jaringan karakter dari teks fiksi. Mencakup: NER untuk identifikasi karakter, co-reference resolution, pembangunan graf, analisis centrality, community detection, dan aplikasi (summarization, classification, role detection).
- **Relevansi untuk TA:**
  - Survey yang paling komprehensif tentang pipeline character network — bisa jadi rujukan utama untuk Bab 2 (Tinjauan Pustaka)
  - Pipeline yang disurvei (NER → co-reference → graph → analysis) paralel dengan pipeline TA kita (NER → alias clustering → relation extraction → SNA)

### 8. Unsupervised Cluster Analyses of Character Networks in Fiction: Community Structure and Centrality
- **Publikasi:** ScienceDirect (2019)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S095070511830491X)
- **Ringkasan:** Analisis clustering tak-terawasi pada jaringan karakter menggunakan community detection. Menghubungkan community structure dengan centrality measures untuk mengidentifikasi peran karakter dalam narasi.
- **Relevansi untuk TA:**
  - Community detection + centrality = kombinasi yang sama dengan `sna_analysis.py` kita
  - Interpretasi komunitas sebagai "kelompok/faksi" relevan untuk analisis Sirah (Muslim vs oposisi Quraisy)

---

## C. Weighted Relations pada Knowledge Graph

### 9. Weight-Aware Tasks for Evaluating Knowledge Graph Embeddings
- **Publikasi:** Knowledge-Based Systems / ScienceDirect (2025)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0950705125006422)
- **Ringkasan:** Memperkenalkan **weight-aware evaluation tasks** untuk knowledge graph embedding: weight-aware link prediction dan weight-aware triple classification. Kritik terhadap metode evaluasi existing yang mengabaikan distribusi bobot global dari knowledge graph.
- **Relevansi untuk TA:**
  - Langsung relevan: kita sudah mengimplementasikan pembobotan relasi (0.0–1.0) pada edges.csv
  - Menunjukkan bahwa weighted KG adalah area penelitian aktif dan penting
  - Bisa dijadikan justifikasi akademis untuk revisi dosen poin 1 (pembobotan relasi)

### 10. Relation and Fact Type Supervised Knowledge Graph Embedding via Weighted Scores
- **Publikasi:** Springer Nature Link
- **Link:** [Springer](https://link.springer.com/chapter/10.1007/978-3-030-32381-3_21)
- **Ringkasan:** KG embedding yang memperhitungkan tipe relasi dan fakta melalui weighted scoring. Model SACN menggunakan **Weighted Graph Convolutional Network (WGCN)** yang membuat trade-off berbeda untuk tipe relasi berbeda.
- **Relevansi untuk TA:**
  - Konsep weighted scoring per relation type relevan dengan implementasi kita (proximity score + period score)
  - Justifikasi bahwa relasi berbeda perlu bobot berbeda

### 11. Co-occurrence Graph Convolutional Networks with Approximate Entailment for Knowledge Graph Embedding
- **Publikasi:** Applied Soft Computing / ScienceDirect (2024)
- **Link:** [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1568494624014406)
- **Ringkasan:** Model **NoGE** yang mengintegrasikan co-occurrence antar entitas dan relasi dengan membangun graf tunggal berisi entitas dan relasi sebagai node individual. Edge weight dihitung dari **co-occurrence frequency**. Mengekstrak dan mengkuantifikasi korelasi dari seluruh knowledge graph.
- **Relevansi untuk TA:**
  - Co-occurrence frequency sebagai edge weight = konsep yang sama dengan co-participation weight kita
  - Validasi akademis bahwa frekuensi co-occurrence valid sebagai bobot relasi

### 12. Knowledge Graph Construction: Extraction, Learning, and Evaluation
- **Publikasi:** Applied Sciences / MDPI (2025)
- **Link:** [MDPI](https://www.mdpi.com/2076-3417/15/7/3727)
- **Ringkasan:** Survey tentang konstruksi knowledge graph mencakup tiga fase: extraction (NER + RE), learning (KG embedding + reasoning), dan evaluation. Mencakup teknik state-of-the-art untuk setiap fase.
- **Relevansi untuk TA:**
  - Survey komprehensif yang bisa dirujuk untuk Bab 2 tentang Knowledge Graph Construction
  - Pipeline extraction (NER → RE) sama dengan pipeline TA kita

---

## D. Community Detection dan Analisis Jaringan

### 13. Louvain Method for Community Detection
- **Penulis:** Blondel et al.
- **Publikasi:** University of Louvain / Journal of Statistical Mechanics (2008)
- **Link:** [Louvain Official](https://perso.uclouvain.be/vincent.blondel/research/louvain.html) | [Wikipedia](https://en.wikipedia.org/wiki/Louvain_method)
- **Ringkasan:** Metode greedy optimization untuk community detection pada jaringan berskala besar. Mengoptimasi **modularity** — ukuran seberapa padat koneksi internal komunitas dibandingkan koneksi acak. Dua fase: (1) node dikelompokkan berdasarkan perubahan modularity, (2) graf direinterpretasi sehingga komunitas menjadi node individual.
- **Relevansi untuk TA:**
  - Algoritma yang kita gunakan di `detect_communities()` — wajib dirujuk
  - Hasil: 16 komunitas tokoh Sirah dengan modularity optimization

### 14. From Louvain to Leiden: Guaranteeing Well-Connected Communities
- **Publikasi:** Scientific Reports / Nature (2019)
- **Link:** [Nature](https://www.nature.com/articles/s41598-019-41695-z)
- **Ringkasan:** Perbaikan atas Louvain: algoritma Leiden mengatasi masalah komunitas yang terhubung lemah (arbitrarily badly connected). Leiden menjamin komunitas yang well-connected.
- **Relevansi untuk TA:**
  - Bisa disebut sebagai limitasi + future work: migrasi dari Louvain ke Leiden
  - Menunjukkan awareness terhadap kelemahan metode yang dipilih

### 15. A Guide for Choosing Community Detection Algorithms in Social Network Studies
- **Publikasi:** PMC (2020)
- **Link:** [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7508227/)
- **Ringkasan:** Panduan pemilihan algoritma community detection berdasarkan karakteristik data dan pertanyaan penelitian. Membahas Louvain, Leiden, Infomap, Label Propagation, dan lainnya.
- **Relevansi untuk TA:**
  - Justifikasi pemilihan Louvain untuk jaringan Sirah kita
  - Perbandingan dengan metode lain untuk diskusi Bab 5

---

## E. Relation Extraction dan NER untuk Knowledge Graph

### 16. Information Extraction Pipelines for Knowledge Graphs
- **Publikasi:** Knowledge and Information Systems / Springer (2022)
- **Link:** [Springer](https://link.springer.com/article/10.1007/s10115-022-01826-x)
- **Ringkasan:** Pipeline information extraction untuk knowledge graph: NER, relation extraction, entity linking, coreference resolution. Membandingkan pendekatan rule-based, statistical, dan neural.
- **Relevansi untuk TA:**
  - Pipeline IE yang dibahas sama dengan pipeline TA kita
  - Bisa dijadikan rujukan untuk Bab 2 tentang arsitektur pipeline

### 17. A Comprehensive Survey on Relation Extraction: Recent Advances and New Frontiers
- **Publikasi:** ACM Computing Surveys
- **Link:** [ACM](https://dl.acm.org/doi/full/10.1145/3674501)
- **Ringkasan:** Survey terbaru tentang relation extraction mencakup: sentence-level RE, document-level RE, few-shot RE, dan open RE. Teknik: dependency parsing, co-occurrence analysis, GCN, attention mechanism.
- **Relevansi untuk TA:**
  - Survey komprehensif tentang RE — rujukan utama untuk Bab 2
  - Pendekatan proximity-based RE yang kita gunakan termasuk dalam kategori co-occurrence analysis

---

## Ringkasan Relevansi per Revisi Dosen

| Revisi | Paper Paling Relevan |
|--------|---------------------|
| **Revisi 1: Pembobotan Relasi** | #9 (Weight-Aware KG), #10 (Weighted Scores), #11 (Co-occurrence GCN) |
| **Revisi 3: Relasi Person-Person** | #4 (Character Networks), #5 (Chinese Literary Networks), #7 (Character Network Survey) |
| **Revisi 3: Relasi Event Kronologis** | #6 (Dynamic Character Networks), #3 (Multi-IsnadSet) |
| **Revisi 4: SNA** | #1 (Hadith Narrators SNA), #4 (Character Centrality), #13 (Louvain), #8 (Community + Centrality) |
| **Pipeline KG secara umum** | #12 (KG Construction Survey), #16 (IE Pipelines), #17 (RE Survey) |
| **Konteks Sirah/Islam** | #1 (Hadith SNA), #2 (QASiNa), #3 (Multi-IsnadSet) |

---

## Kata Kunci untuk Pencarian Lanjutan

Jika ingin mencari paper tambahan, gunakan kombinasi kata kunci berikut:

1. **SNA + Teks Islam:**
   - `"social network analysis" hadith narrators centrality`
   - `"knowledge graph" Islamic text "named entity recognition"`
   - `"character network" historical narrative biography`

2. **Weighted Relations:**
   - `"weighted knowledge graph" relation extraction evaluation`
   - `"co-occurrence" weight "knowledge graph embedding"`
   - `"proximity-based" relation extraction NER`

3. **Community Detection:**
   - `"community detection" Louvain "character network"`
   - `"modularity optimization" social network narrative`

4. **Character Network dari Teks Historis:**
   - `"character network" "historical text" centrality extraction`
   - `"narrative network" "social structure" literary analysis`
   - `"co-participation" graph "event extraction"`
