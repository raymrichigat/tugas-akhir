pertanyaan:

1. Anda menyatakan data uji tidak digunakan dalam pelatihan, tetapi skor data uji digunakan untuk memilih best\_model pada setiap iterasi self-training. Apakah penggunaan tersebut tidak menjadikan data uji berfungsi sebagai data validasi dan menyebabkan bias pada nilai F1 akhir?
2. Pembagian data dilakukan pada tingkat chunk untuk mencegah kebocoran data. Namun, setiap chunk memiliki overlap satu kalimat dengan chunk sebelumnya. Bagaimana Anda memastikan kalimat yang sama tidak tersebar ke data latih dan data uji?
3. Ground truth diperoleh melalui koreksi manual oleh peneliti. Tanpa anotator kedua, pengukuran inter-annotator agreement, atau validasi ahli Sirah, bagaimana reliabilitas dan objektivitas anotasi tersebut dapat dibuktikan?
4. Penelitian ini menggunakan istilah “NER berbasis SRL”, tetapi tidak menjalankan pengurai predikat–argumen sebagaimana Semantic Role Labeling pada umumnya. Mengapa pendekatan tersebut tetap disebut berbasis SRL dan bukan NER berbasis aturan serta self-training?
5. Pseudo-label diterima berdasarkan rata-rata confidence entitas minimal 0,9. Mengapa threshold 0,9 dan maksimum enam iterasi dipilih, serta bagaimana Anda memastikan kesalahan pseudo-label tidak terakumulasi pada iterasi berikutnya?
6. Augmentasi melalui mention replacement dan parafrase meningkatkan F1 mikro dari 0,9536 menjadi 0,9756. Bagaimana Anda memastikan parafrase tidak mengubah makna, batas entitas, atau peran semantik kalimat sehingga label hasil augmentasi tetap valid?
7. IndoBERT uncased dinyatakan menghasilkan performa terbaik, tetapi IndoBERT cased dan RoBERTa diduga mengalami masalah penyelarasan label subword. Jika implementasi setiap tokenizer belum sepenuhnya setara, apakah hasil komparasi kelima model tersebut masih dapat disebut perbandingan yang adil?
8. Pada pengujian fungsional, setiap fungsi memiliki setidaknya satu jawaban yang tidak didukung konteks sumber, bahkan pada F5 hanya 3 dari 21 jalur yang didukung secara utuh. Atas dasar apa knowledge graph tersebut dinyatakan layak untuk penelusuran informasi?
9. Analisis SNA dibangun dari relasi yang masih mengandung false positive dan mencampurkan hubungan co-participation dengan relasi langsung seperti keluarga, sahabat, dan musuh. Bagaimana Anda memastikan hasil sentralitas dan komunitas tidak sekadar mencerminkan artefak pembentukan graf?
10. Louvain menghasilkan modularitas 0,2831 dan perbandingannya dengan greedy modularity hanya menghasilkan ARI 0,47. Dengan pemisahan komunitas yang relatif lemah tersebut, seberapa kuat dasar Anda dalam menafsirkan komunitas sebagai “lingkar Muslim inti” atau kelompok tokoh tertentu?
11. Mengapa batas chunk ditentukan berdasarkan 1.500 karakter, bukan berdasarkan jumlah token, padahal IndoBERT memproses masukan dalam satuan token?
12. Apa yang terjadi apabila satu kalimat memiliki panjang lebih dari batas maksimum chunk yang telah ditentukan?
13. Mengapa overlap yang digunakan hanya satu kalimat? Apa dasar pemilihan jumlah overlap tersebut?
14. Jika kalimat overlap muncul dua kali, bagaimana Anda mencegah entitas dan relasi yang sama dihitung dua kali dalam knowledge graph?
15. Bagaimana Anda membedakan kesalahan ketik hasil OCR dengan variasi nama tokoh yang memang benar-benar berbeda?
16. Mengapa kabilah atau kelompok seperti Bani Quraizhah dapat diberi label PERSON, padahal secara ontologis bukan individu?
17. Bagaimana model membedakan kata seperti “Badr”, “Uhud”, dan “Khaibar” ketika kata tersebut dapat merujuk pada lokasi maupun peristiwa?
18. Mengapa kata ganti seperti “beliau”, “dia”, atau “mereka” tidak dimasukkan sebagai entitas Person? Apakah pengabaian kata ganti tidak menyebabkan hubungan antartokoh dan peristiwa menjadi hilang?
19. Jika “Muhammad”, “Nabi”, “Rasulullah”, dan “beliau” merujuk pada tokoh yang sama, mana saja yang berhasil disatukan dan mana yang masih dianggap berbeda?
20. Mengapa Jaro–Winkler menggunakan threshold 0,93? Apa yang terjadi jika dua nama orang berbeda memiliki kemiripan penulisan di atas threshold tersebut?
21. Dalam alias clustering, nama yang lebih panjang diprioritaskan sebagai nama kanonik. Apakah nama terpanjang selalu merupakan nama yang paling tepat atau paling umum dikenal?
22. Mengapa “Madinah” dan “Yatsrib” masih menjadi dua simpul berbeda, padahal penelitian sudah menerapkan alias clustering?
23. Apa perbedaan fungsi node TIME dan node PERIOD? Mengapa keduanya tidak dijadikan satu jenis node waktu?
24. Dari 901 node Person dalam knowledge graph, mengapa hanya 137 tokoh yang masuk ke proyeksi jaringan SNA? Apa yang terjadi pada tokoh lainnya?
25. Jika hasil OCR, NER, alias clustering, dan ekstraksi relasi masing-masing memiliki kemungkinan kesalahan, pada tahap mana kesalahan paling banyak memengaruhi hasil akhir knowledge graph?

