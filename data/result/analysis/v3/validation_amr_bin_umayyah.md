# Validasi Tokoh — "Amr Bin Umayyah" Rank #2 by PageRank di v3

**Konteks:** SNA v3 (`sna_metrics.csv`) menempatkan **Amr Bin Umayyah** di rank #2 PageRank (PR=0.0148, deg=119, community=0), tepat di bawah Nabi Muhammad. Posisi ini mengejutkan secara historis — tokoh yang biasanya rank #2-5 di literatur Sirah adalah Khulafa Rasyidin (Abu Bakar, Umar, Utsman, Ali). Pertanyaan validasi: apakah ini real centrality atau artifact metodologi?

## Verdict singkat

**Artifact, bukan real centrality.** Rank #2 PR muncul karena proximity-based relation extraction salah meng-attribute 3 dari 4 INVOLVED_IN event Amr (Perang Badr, Uhud, Tabuk → false positive; hanya Khandaq yang legit). False INVOLVED_IN ini bikin dia ke-co-participate dengan ratusan Person yang sebenarnya bukan rekan partisipasinya.

## Evidence

### Statistik node v3

| Field | Nilai |
|---|---|
| node_id | `79d8bc0c75e0` |
| label | PERSON |
| frequency | 11 (chunk-mention) |
| unique chunks | 9 |
| degree (Person co-participation) | 119 |
| PageRank | 0.01476 (rank #2) |
| Betweenness | 0.0380 |
| Community | 0 (sama dengan Muhammad) |

### Kenapa degree 119

INVOLVED_IN ke 4 event:

| Event | Total Person INVOLVED_IN | Verifikasi |
|---|---:|---|
| Perang Badr | 63 | ❌ False — kalimat tentang **Uqbah** (yang ayahnya dibunuh Khubaib di Badr); Amr cuma muncul di kalimat sebelumnya soal pencurian jasad Khubaib |
| Perang Uhud | 52 | ❌ False — "korban yang sama dengan Perang Uhud" adalah **perbandingan numerik**, bukan partisipasi |
| Perang Khandaq | 17 | ✅ Real — survivor insiden Raji', hadir di Khandaq |
| Perang Tabuk | 6 | ❌ False — evidence text justru cerita Amr balik dari Najasyi ke Khaibar; Tabuk mention sebagai **timestamp wafat Najasyi** |

Union 4 event = **118 unique Person** + 1 dari SAHABAT-Salamah langsung = **degree 119**. Di antaranya 88+ di antaranya seharusnya **bukan** rekan partisipasinya.

### Evidence text per false-positive

**Perang Badr (false):**
> "...apa orang untuk menjaga jasadnya. Kemudian muncul Amr bin Umayyah Adh-Dhamiri dan pada malam harinya dia dapat mengakali para penjaga, lalu membawa jasadnya untuk dikuburkan. Yang menangani eksekusi terhadap Khubaib adalah Uqbah bin Al-Harits, **yang pada waktu Perang Badr, Khubaib telah membunuh ayahnya Uqbah**..."

→ Konteks "Perang Badr" attached ke Uqbah (alasan dendam), bukan Amr.

**Perang Uhud (false):**
> "...Amr bin Umayyah pergi ke Madinah hendak menemui Rasulullah membawa kabar yang menimpa tujuh puluh orang Muslim, **dengan korban yang sama dengan Perang Uhud. Hanya saja dalam Perang Uhud mereka jelas pergi**..."

→ Kalimat perbandingan jumlah korban (insiden Raji' vs Uhud). Amr sedang **melaporkan**, bukan partisipan Uhud.

**Perang Tabuk (false):**
> "...dia mengirim mereka dengan menumpang dua perahu. Amr bin Umayyah Adh-Dhamri juga ikut dalam rombongan itu, hingga mereka bertemu Nabi yang saat itu sedang berada di Khaibar. **Raja Najasyi ini meninggal dunia pada bulan Rajab tahun 7 H, setelah Perang Tabuk**..."

→ "Perang Tabuk" adalah anchor temporal untuk wafatnya Najasyi, bukan event yang Amr ikuti. (Tabuk = tahun 9 H, Najasyi wafat 7 H — kalimat ini sebenarnya factually inconsistent di teks Mubarakfuri, tapi itu issue lain.)

## Real role Amr Bin Umayyah Adh-Dhamri

Berdasarkan teks Mubarakfuri yang sudah di-OCR:

1. **Sahabat (Bani Dhamrah)** — bukan kaum Quraisy
2. **Survivor insiden Raji'** (8 orang dikirim Nabi mengajar, 7 syahid, Amr satu-satunya selamat)
3. **Kurir Nabi → Raja Najasyi** — kirim surat akhir tahun 6 H atau awal 7 H. Sudah ke-capture dengan tepat di edge SAHABAT-Najasyi (lihat row 441 `edges_v3.csv`).
4. **Mission ke Bani Asad** bersama Salamah bin Abu Salamah, bulan Syawwal 6 H. Sudah ke-capture di edge SAHABAT-Salamah (row 438).
5. **Hadir di Perang Khandaq** (real).

Jadi tokoh **memang sahabat senior dengan misi diplomatik penting**, tapi **bukan top-2 figure** di Sirah.

## Implikasi metodologi

1. **Proximity-based INVOLVED_IN over-generates false positives** ketika Person dan Event ko-okur dalam window kecil tapi semantik kalimatnya bukan "partisipasi" (perbandingan, anchor temporal, konteks latar belakang).
2. **Co-participation graph multiplier effect**: 1 false INVOLVED_IN ke event besar → puluhan false co-participation edges → spike degree → spike PageRank.
3. **Tokoh real top-2/3** mestinya **Abu Bakar / Umar / Ali / Aisyah**. Mereka memang muncul di top-10 v3 (rank 5/10/7/6), tapi degraded dari rank 2-5.

## Rekomendasi (post-bimbingan)

1. **Filter INVOLVED_IN dengan SRL verb extraction** — terima edge hanya kalau predicat kalimat memang verb partisipasi (`memimpin`, `ikut`, `bertempur`, `hadir`) bukan nominalisasi temporal/komparasi.
2. **Adjust weight INVOLVED_IN by chunk frequency**: kalau Person muncul di 9 chunks tapi 4 chunks langsung jadi INVOLVED_IN ke 4 event berbeda, kemungkinan over-extraction.
3. **Manual curation top-50 PR** sebelum klaim final — cocokkan dengan literatur Sirah.

## Status untuk bimbingan

- ⚠️ **Disclose ke Bu Diana**: rank #2 Person PR di v3 adalah artifact, bukan finding. Top-10 lain (Khulafa Rasyidin) tetap valid.
- ✅ Hipotesis "NER scale-up = comprehensive coverage" tetap valid; issue di **relation extraction** (proximity heuristic), bukan di **NER**.
- 📝 Catat sebagai **limitation Bab 4** dan future work.
