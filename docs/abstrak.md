# Abstrak Tugas Akhir

> Pendekatan *Named-Entity Recognition* dalam Pembangunan *Knowledge Graph* Sirah Nabawiyah
> Genta Putra Prayoga (5025221040) — S1 Teknik Informatika ITS
> Pembimbing: Dini Adni Navastara, S.Kom., M.Sc. · Ko-pembimbing: Ratih Nur Esti Anggraini, S.Kom., M.Sc., Ph.D.

Ketentuan: 3 paragraf (Bab 1–2 / Bab 3 / Bab 4), maksimum 200 kata. Angka dari hasil terakhir (F1 augmentation 0,9581; graf Person 208 node; 15 komunitas; modularitas Louvain 0,3851).

---

## ABSTRAK (Bahasa Indonesia)

Sirah Nabawiyah merupakan sumber sejarah yang kaya namun tersaji dalam bentuk teks naratif tidak terstruktur, sehingga keterhubungan antar tokoh dan peristiwa di dalamnya sulit ditelusuri secara sistematis. Penelitian ini membangun *knowledge graph* dari buku Sirah Nabawiyah berbahasa Indonesia untuk merepresentasikan entitas tokoh, peristiwa, waktu, dan lokasi beserta relasinya. Pendekatan yang digunakan adalah *Named-Entity Recognition* (NER) berbasis model bahasa IndoBERT dengan pelatihan mandiri iteratif (*iterative self-training*), yang hasilnya disimpan dalam basis data graf Neo4j dan dianalisis menggunakan *Social Network Analysis* (SNA).

Metodologi disusun sebagai rangkaian tahap, yaitu ekstraksi teks melalui OCR, prapemrosesan, dan pemecahan teks; pelabelan semi-otomatis berbasis aturan dan gazetteer sebagai data benih; pelatihan model NER yang diperbanyak melalui *iterative self-training*; penyatuan variasi nama dengan *alias clustering*; serta pembentukan relasi antar-entitas yang diperkaya periodisasi peristiwa. Graf akhir dikonstruksi di Neo4j lalu dievaluasi melalui analisis jaringan dan pengujian fungsional kueri.

Pada peningkatan kualitas NER, pendekatan terbaik dicapai teknik *augmentation* dengan *F1-score* 0,9581 dan perbaikan terbesar pada kelas minoritas. *Knowledge graph* akhir memuat 208 tokoh dalam 15 komunitas naratif (modularitas Louvain 0,3851) dengan Nabi Muhammad sebagai pusat jaringan. Hasil ini menunjukkan pendekatan berbasis IndoBERT dengan *iterative self-training* mampu membangun *knowledge graph* Sirah Nabawiyah yang keterhubungan antar entitasnya dapat ditelusuri secara sistematis.

**Kata kunci:** Knowledge Graph, Named-Entity Recognition, IndoBERT, Sirah Nabawiyah, Social Network Analysis, Neo4j

---

## ABSTRACT (English)

Sirah Nabawiyah is a rich historical source, yet presented as unstructured narrative text, making the connections among its figures and events difficult to trace systematically. This study builds a knowledge graph from the Indonesian-language book of Sirah Nabawiyah to represent person, event, time, and location entities and their relationships. The approach uses Named-Entity Recognition (NER) based on the IndoBERT model with iterative self-training; results are stored in Neo4j and analyzed using Social Network Analysis (SNA).

The methodology comprises several stages: text extraction through OCR, preprocessing, and chunking; semi-automatic labeling based on rules and a gazetteer as seed data; NER model training expanded via iterative self-training; name consolidation through alias clustering; and inter-entity relation formation enriched with event periodization. The final graph is constructed in Neo4j and evaluated through network analysis and functional query testing.

The best result came from the augmentation technique, with an F1-score of 0.9581 and the greatest gain on minority classes. The final knowledge graph contains 208 figures across 15 narrative communities (Louvain modularity 0.3851), with Prophet Muhammad at the network's center. These results show that the IndoBERT-based NER approach with iterative self-training can build a Sirah Nabawiyah knowledge graph whose entity connections are systematically traceable.

**Keywords:** Knowledge Graph, Named-Entity Recognition, IndoBERT, Sirah Nabawiyah, Social Network Analysis, Neo4j

---

## Catatan

- Framing metode sengaja ditulis **"NER berbasis IndoBERT dengan iterative self-training"** (akurat sesuai implementasi), bukan klaim "SRL parsing". Jika judul/proposal mengharuskan istilah "SRL", dapat diselipkan menjadi "mengadaptasi kerangka self-training dari pendekatan SRL".
- Kata kunci di luar hitungan 200 kata.
- Saat port ke LaTeX template ITS b201lab: abstrak ID → `abstrak/abstrak-id.tex`, abstrak EN → `abstrak/abstrak-en.tex` (cek nama berkas persis di template).
