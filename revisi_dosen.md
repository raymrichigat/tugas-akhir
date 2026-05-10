Masukan
- Temporal dalam satu kalimat (?) perlu di deteksi (bisa dilihat dari urutan kejadian di Sirah / urutan bab nya)
- Lalu pembentukan graf, memperhatikan Temporal waktu, baru ke fitur graf nya

Uji coba: 
- Kasus perang badar, diamati keterlibatan nya apa saja lalu diamati graf nya (sampling beberapa event). Kalo misalnya kesalahan dari awal, nanti akan berpengaruh ke perhitungan fitur nya (ambil beberapa contoh 3 atau 5 fitur, dengan periode yang jauh. Tunjukkan dalam graf seperti apa lalu di analisis, untuk yang lain juga seperti apa)

NER : 
- LLM-NER tidak jadi digunakan, jadinya menggunakan SRL-NER saja
- SRL NER ini perlu di definisikan skenario nya seperti apa (seperti thresholdnya saja kah atau ada yang lainnya) 
- Untuk perbandingan Threshold bisa digunakan seperti fix threshold atau adaptif (kalau terlalu rendah akan otomatis diturunkan)
- Kalau mau mengganti model silahkan, tetapi kalau tidak mau ribet bisa myang lainnya dahulu
- Kalau unbalanced perlu di handling dan ini ada berbagai macam(definisikan dulu skenario seperti apa, perlu effort nya lebih lagi)

Graf :
- Perlu uji coba lain selain centrality (community atau lainnya)
- Centrality -> fokus ke node (fokus ke graf gede nya, seperti clustering, ukuran network nya berapa, seperti density, dkk)