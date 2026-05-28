# Manual Validation — LLM Verb Extraction Sample (10 items)

**Tanggal:** 2026-05-28
**Source:** `data/result/llm_verb_extraction/verb_extraction_{events,triplets}.csv`
**Reviewer:** human-in-the-loop validation untuk Bu Diana
**Tujuan:** assess apakah LLM verb extraction reliable untuk **scale-up** sebagai solusi false-positive INVOLVED_IN (lihat `validation_amr_bin_umayyah.md`).

## Metodologi validasi

Untuk setiap sample, cross-check 4 kriteria:

1. **Subject/object real entity?** — Bukan kata ganti ("dia", "mereka") atau noun phrase generik
2. **Verb describe historical action?** — Bukan verb kognitif/percakapan biasa
3. **Context_text mendukung claim?** — Verb betul-betul ada di kalimat yang dirujuk
4. **Tidak duplicate dengan edges_v2/v3?** — Apakah sudah ke-cover INVOLVED_IN existing

Rating per item:
- ✅ **VALID** — semua kriteria pass, edge baru yang berguna
- ⚠️ **PARTIAL** — claim benar tapi over-extraction atau ambigu
- ❌ **WRONG** — hallucination atau salah baca

Sample N=10 (5 EVENT + 5 triplet, mix high/low confidence) dari N=46 total output LLM.

---

## EVENT Candidates (5 sample)

### #1 — `000131-002` "Pembunuhan Utbah oleh Hamzah dan Ali" (conf 0.95)

**LLM output:**
> verb=`membunuh`, subject=`Hamzah dan Ali bin Abu Thalib`, context: "Kemudian Hamzah dan Ali menghampiri Utbah lalu membunuhnya."

**Verifikasi vs teks chunk:**
> "Kemudian Hamzah dan Ali menghampiri Utbah lalu membunuhnya."

✅ **Verb match** — exact phrase di teks.
✅ **Historical action** — Pembunuhan duel Perang Badr (real event).
⚠️ **Subject** — "Hamzah dan Ali bin Abu Thalib" adalah **dual-subject single string** — bermasalah untuk graph schema (1 EVENT node butuh 1 subject, atau split jadi 2 INVOLVED_IN).

**Verdict: ⚠️ PARTIAL VALID** — fakta benar, tapi format dual-subject perlu **post-processing**: split jadi 2 row (Hamzah / Ali masing-masing). Detail historis context Mubarakfuri: Utbah dibunuh setelah Hamzah & Ali selesaikan duel masing-masing (Syaibah / Al-Walid), lalu mereka menghampiri Utbah yang masih bertarung dengan Ubaidah. Klaim LLM **konsisten** dengan narasi.

**Duplicate check:** edges_v3.csv punya `Hamzah → INVOLVED_IN → Perang Badr` (proximity-based). Triplet baru `Hamzah → MEMBUNUH → Utbah` adalah **edge baru yang lebih informatif** (predikat-spesifik vs INVOLVED_IN generik).

---

### #2 — `000131-002` "Wafatnya Ubaidah bin Al-Harits di Ash-Shafra'" (conf 0.95)

**LLM output:**
> verb=`meninggal`, subject=`Ubaidah bin Al-Harits`, context: "Dia sama sekali tidak mengeluh hingga meninggal dunia di Ash-Shafra', empat atau lima hari setelah Perang Badr"

**Verifikasi:**
> "Dia sama sekali tidak mengeluh hingga meninggal dunia di Ash-Shafra', empat atau lima hari setelah Perang Badr, di tengah perjalanan pulang ke Madinah."

✅ Verb match (meninggal).
✅ Historical (kematian sahabat senior pasca duel Perang Badr).
✅ Subject = real PERSON.
✅ **Tidak duplicate** — edges_v3 tidak punya edge "MENINGGAL_DI" untuk Ubaidah.

**Verdict: ✅ VALID** — kandidat EVENT entity baru (label_aksi: "Wafat Ubaidah") + bisa jadi triplet `Ubaidah --MENINGGAL_DI--> Ash-Shafra'`. Sudah ada di triplets row #14 dengan label MENINGGAL_DI (LOCATION). Konsisten.

---

### #3 — `000142-002` "Eksekusi An-Nadhr bin Al-Harits di Ash-Shafra'" (conf 0.95)

**LLM output:**
> verb=`dipenggal`, subject=`Ali bin Abu Thalib`, context: "Setiba di Ash-Shafra', An-Nadhr bin Al-Harits diperintahkan untuk dibunuh... Akhirnya dia dipenggal oleh Ali bin Abu Thalib."

**Verifikasi:**
> "Setiba di Ash-Shafra', An-Nadhr bin Al-Harits diperintahkan untuk dibunuh, karena dia adalah pembawa bendera pasukan musyrikin... Akhirnya dia dipenggal oleh Ali bin Abu Thalib."

✅ Verb match (dipenggal).
✅ Historical (eksekusi tawanan pasca Badr — kontroversi di literatur Sirah, dicatat dengan jelas oleh Mubarakfuri).
✅ Subject Ali real PERSON.
⚠️ **Subject role ambigu** — "diperintahkan oleh" Muhammad (sebagai komandan), "dieksekusi oleh" Ali. LLM ambil eksekutor, OK. Tapi triplets row #21 sudah catat ini juga (`Ali → MEMBUNUH → An-Nadhr`).

**Verdict: ✅ VALID** — kandidat EVENT baru "Eksekusi An-Nadhr" + triplet sudah lengkap. Tidak duplicate v3.

**Catatan:** Mubarakfuri eksplisit menyebut An-Nadhr sebagai "pemuka Quraisy yang amat jahat" — context historis konsisten dengan teks aslinya.

---

### #4 — `000254-002` "Pengutusan Amr sebagai utusan ke Raja Uman" (conf 0.85)

**LLM output:**
> verb=`mengutus`, subject=`Muhammad`, context: "Aku berkata di hadapannya, 'Aku adalah utusan Rasulullah untuk menghadap tuan dan saudara tuan.'"

**Verifikasi:**
> "Aku berkata di hadapannya, 'Aku adalah utusan Rasulullah untuk menghadap tuan dan saudara tuan.'"

✅ Subject Muhammad real (implisit dari "Rasulullah").
✅ Verb `mengutus` valid (terbukti dari "utusan Rasulullah").
⚠️ **Verb tidak literal di teks** — kalimat aslinya **tidak punya** kata kerja "mengutus". LLM **infer** dari "utusan". Ini reasonable inference, bukan hallucination.
✅ Historical action.

**Verdict: ⚠️ PARTIAL VALID** — claim benar (Muhammad mengutus Amr ke Raja Uman, ini fakta historis yang well-attested), tapi verb di-infer bukan ekstraksi literal. Untuk scale-up, perlu **flag inferred-vs-literal** sebagai field tambahan.

**Catatan ke validasi Amr:** Ini mengkonfirmasi finding sebelumnya bahwa **Amr Bin Umayyah real prominent** sebagai kurir diplomatik Nabi (Najasyi + Raja Uman). Yang artifactial adalah PR rank di Person network, **bukan** keberadaannya di KG.

---

### #5 — `000140-003` "Penyerangan Abu Rafi' oleh Abu Lahab" (conf 0.90)

**LLM output:**
> verb=`memukul`, subject=`Abu Lahab`, context: "Abu Lahab mengangkat tangannya tinggi-tinggi lalu memukulkan ke mukaku dengan keras..."

**Verifikasi:**
> "Lalu aku (Abu Rafi') mengangkat batu pembatas Zamzam... Abu Lahab mengangkat tangannya tinggi-tinggi lalu memukulkan ke mukaku dengan keras. Aku hendak melawannya, namun dia membanting tubuhku ke tanah, kemudian menindihiku sambil melancarkan pukulan bertubi-tubi."

✅ Verb match (memukulkan).
✅ Historical — insiden ekspresif setelah berita kekalahan Quraisy di Badr.
✅ Subject & object real PERSON.
✅ **Edge baru** — Abu Lahab → MEMUKUL → Abu Rafi' tidak ada di edges_v3.

**Verdict: ✅ VALID** — kandidat EVENT baru ("Insiden Zamzam: Abu Lahab vs Abu Rafi'") + triplet bersih.

**Insight:** Edge ini **tidak mungkin** ditangkap proximity-based (Abu Lahab tidak INVOLVED_IN event bernama; insiden ini adalah micro-event tanpa label proper noun di teks). **Ini contoh konkret keuntungan LLM verb extraction.**

---

## SVO Triplets (5 sample)

### #6 — `000131-002` Hamzah → MEMBUNUH → Syaibah bin Rabi'ah (conf 0.75)

**LLM output:**
> verb=`MEMBUNUH`, context: "Hamzah dan Ali tidak terlalu kesulitan melibas lawan tandingnya."

**Verifikasi:**
> "Ubaidah... berhadapan dengan Utbah, Hamzah berhadapan dengan Syaibah dan Ali berhadapan dengan Al-Walid... Hamzah dan Ali tidak terlalu kesulitan **melibas lawan tandingnya**."

⚠️ **Verb tidak literal** — teks pakai "melibas lawan tandingnya", bukan "membunuh". LLM infer "melibas → membunuh" dari context Perang Badr (duel = sampai mati).
✅ **Pairing benar** — Hamzah memang berduel dengan Syaibah (dari kalimat sebelumnya).
✅ **Historical accuracy** — Mubarakfuri di chapter Perang Badr lain (yang tidak masuk chunk ini) konfirmasi Hamzah membunuh Syaibah dalam duel. Ini fakta well-known.

**Verdict: ⚠️ PARTIAL VALID** — kebenaran historis benar, **tapi inference di luar context_text yang LLM kutip**. Confidence 0.75 terkalibrasi dengan baik (LLM sendiri ragu).

**Implikasi scale-up:** untuk kalimat dengan inferred verb, hanya terima kalau confidence ≥ 0.85, atau filter via second-pass verification.

---

### #7 — `000131-002` Ali → MEMBUNUH → Al-Walid (conf 0.75)

Sama persis pattern dengan #6 — pairing duel benar, verb di-infer dari "melibas". Verdict: ⚠️ PARTIAL VALID.

**Catatan:** ini menunjukkan pattern LLM — **konsistensi paired inference** (kalau Hamzah membunuh, otomatis Ali juga membunuh karena teks "Hamzah dan Ali" parallel construction). Pattern ini perlu di-aware-i untuk false-positive risk di kasus parallel yang **bukan** symmetric.

---

### #8 — `000254-002` Najasyi → MEMELUK_ISLAM → Muhammad (conf 0.70)

**LLM output:**
> verb=`MEMELUK_ISLAM`, object=`Muhammad`, context: "Lalu aku mengabarkan kepadanya bahwa Najasyi sudah masuk Islam."

**Verifikasi:**
> "Lalu aku mengabarkan kepadanya bahwa Najasyi sudah masuk Islam."

⚠️ **Schema problem** — "MEMELUK_ISLAM" bukan binary relation (subject -[verb]-> object). Najasyi memeluk Islam adalah **unary fact** tentang Najasyi, **bukan** relation Najasyi-Muhammad. LLM coba force-fit ke triplet schema → output salah.
✅ Subject Najasyi real (kasus historis Raja Habasyah yang masuk Islam).
❌ Object Muhammad **tidak appropriate** — Najasyi tidak "memeluk Islam ke" Muhammad. Yang benar: Najasyi → MASUK_ISLAM (unary, atau object = "Islam" sebagai concept).

**Verdict: ❌ WRONG** — schema mismatch. Ini contoh LLM over-fit ke binary relation requirement.

**Implikasi:** prompt template perlu dipertegas — **unary fact tidak boleh dipaksa jadi triplet**. Atau tambah label `:Concept` untuk objek seperti Islam.

---

### #9 — `000142-002` Abu Bakar → MENAHAN → Uqbah bin Abu Mu'aith (conf 0.85)

**LLM output:**
> verb=`MENAHAN`, context: "Selagi dia hampir dibunuh, Abu Bakar menahannya."

**Verifikasi:**
> "Selagi dia hampir dibunuh, Abu Bakar menahannya."

✅ Verb match (menahannya).
✅ Subject Abu Bakar real.
✅ Object Uqbah real (dari koreferensi "dia hampir dibunuh" yang di-bind ke Uqbah dari kalimat sebelumnya).
⚠️ **Semantik tidak jelas** — "menahan" di konteks ini bisa berarti "intervensi minta jangan dibunuh" atau "menahan tubuh untuk dibunuh". Mubarakfuri tidak eksplisit, tapi konteks menunjukkan **intervensi belas kasih** (Abu Bakar coba mencegah eksekusi).
✅ **Edge baru** — tidak duplicate v3.

**Verdict: ✅ VALID dengan caveat** — fakta benar, tapi label "MENAHAN" perlu disambiguasi (intervene_to_save vs physically_hold). LLM tidak salah baca, hanya verb-nya inheren ambigu di Bahasa Indonesia.

**Implikasi:** untuk schema KG, lebih baik label spesifik seperti `MENCEGAH_PEMBUNUHAN` (kalau jelas dari context) daripada `MENAHAN` generik.

---

### #10 — `000080-010` Isra' → BERTUJUAN_KE → Baitul Maqdis (conf 0.85)

**LLM output:**
> verb=`BERTUJUAN_KE`, subject_label=`EVENT`, object_label=`LOCATION`, context: "Allah mengisyaratkan bahwa Isra' itu merupakan perjalanan ke Baitul Maqdis."

**Verifikasi:**
> "Dengan susunan kalimat ini Allah mengisyaratkan bahwa Isra' itu merupakan perjalanan ke Baitul Maqdis."

✅ Verb match (perjalanan ke = bertujuan ke, paraphrased).
✅ Subject Isra' real EVENT entity (sudah ada di nodes_v3 sebagai EVENT).
✅ Object Baitul Maqdis real LOCATION.
✅ Historical (well-attested di Sirah).
✅ **Edge type berbeda** — `EVENT-LOCATION` via predikat selain OCCURRED_AT. Schema baru: `BERTUJUAN_KE` (destination) bisa beda dengan `OCCURRED_AT` (event location).

**Verdict: ✅ VALID** — kasus paling menarik karena subject = EVENT (bukan PERSON). Membuktikan LLM verb extraction bisa **enrich event-location semantic relations**, tidak terbatas Person-Person/Person-Event.

**Implikasi:** schema KG bisa di-expand dengan predikat-predikat semantik EVENT-LOCATION beyond OCCURRED_AT (e.g. `BERTUJUAN_KE`, `BERAKHIR_DI`, `BERANGKAT_DARI`).

---

## Ringkasan Validasi

| # | Sample | Conf LLM | Verdict | Catatan |
|---|---|---:|---|---|
| 1 | EVENT: Hamzah&Ali membunuh Utbah | 0.95 | ⚠️ PARTIAL | Dual-subject, perlu split |
| 2 | EVENT: Wafat Ubaidah di Ash-Shafra' | 0.95 | ✅ VALID | Edge baru, bersih |
| 3 | EVENT: Eksekusi An-Nadhr | 0.95 | ✅ VALID | Sudah ke-cover di triplet |
| 4 | EVENT: Pengutusan Amr ke Raja Uman | 0.85 | ⚠️ PARTIAL | Verb inferred (bukan literal) |
| 5 | EVENT: Penyerangan Abu Rafi' oleh Abu Lahab | 0.90 | ✅ VALID | Micro-event, **proximity miss** |
| 6 | TRIPLET: Hamzah membunuh Syaibah | 0.75 | ⚠️ PARTIAL | Verb inferred dari "melibas" |
| 7 | TRIPLET: Ali membunuh Al-Walid | 0.75 | ⚠️ PARTIAL | Same as #6 |
| 8 | TRIPLET: Najasyi memeluk Islam → Muhammad | 0.70 | ❌ **WRONG** | Schema mismatch (unary force-fit) |
| 9 | TRIPLET: Abu Bakar menahan Uqbah | 0.85 | ✅ VALID | Verb ambigu tapi correct extraction |
| 10 | TRIPLET: Isra' bertujuan ke Baitul Maqdis | 0.85 | ✅ VALID | EVENT-LOCATION semantik baru |

**Skor:**
- ✅ VALID: **5/10 (50%)**
- ⚠️ PARTIAL VALID: **4/10 (40%)** — claim benar tapi perlu post-processing
- ❌ WRONG: **1/10 (10%)** — schema force-fit

**Effective valid (VALID + PARTIAL with simple fix): 9/10 (90%)** — encouraging, tapi perlu pipeline cleanup.

---

## Findings & Implikasi

### 1. **LLM verb extraction terbukti efektif untuk micro-events**

Sample #5 (insiden Abu Lahab vs Abu Rafi' di Zamzam) **tidak mungkin** ditangkap oleh proximity-based extraction karena tidak ada nama EVENT yang ko-okur. Ini adalah keuntungan unik LLM — bisa identifikasi event kontekstual tanpa dependent ke pre-existing EVENT NER.

### 2. **Pattern false-positive yang perlu di-aware**

- **Parallel construction inference** (#6, #7): "Hamzah dan Ali..." → LLM extract simetris meski teks ambigu.
- **Inferred verb dari konteks** (#4, #6, #7): verb yang tidak literal di kalimat tapi reasonable historical inference. Confidence 0.75-0.85 terkalibrasi.
- **Schema force-fit** (#8): unary fact dipaksa jadi binary triplet. **Perbaikan:** prompt tambah opsi `relation_type=null` atau `unary_fact` field.

### 3. **Verb-extraction lebih kaya dari proximity INVOLVED_IN**

Triplet di sample #1, #5, #9, #10 punya **semantic predicate** (MEMBUNUH, MEMUKUL, MENAHAN, BERTUJUAN_KE) — informasi yang tidak ada di edge INVOLVED_IN generik di v3. Ini direct upgrade pipeline relation extraction.

### 4. **Confirmation finding Amr Bin Umayyah**

Sample #4 (Pengutusan Amr ke Raja Uman) konfirmasi: Amr **memang** sahabat dengan misi diplomatik penting. PR rank #2 di v3 bukan karena tokoh ini tidak prominent, tapi karena **proximity-based relation extraction over-attribute INVOLVED_IN ke event mega**. **Solusi LLM verb extraction langsung address akar masalah** (false-positive INVOLVED_IN).

### 5. **Effort scale-up estimation**

- 10 chunks → ~46 candidates → ~50% directly usable, ~40% needs post-processing.
- Untuk full Sirah (1094 chunks): kasar 10× = ~5000 candidate → manageable manual review.
- API cost (Claude Sonnet): ~5000 chunks × 2k tokens avg = 10M tokens ≈ $30 (input) + $15 (output) ≈ $45 total.
- Bottleneck: **manual post-processing** (split dual-subject, filter inferred-verb low-conf, fix schema mismatch). Estimasi 5-10 jam human review untuk full corpus.

---

## Rekomendasi untuk Bimbingan

### Yang bisa di-claim:
1. ✅ **POC LLM verb extraction valid** — 90% effective rate (VALID + PARTIAL).
2. ✅ **Solusi false-positive INVOLVED_IN teridentifikasi** — bukan teoretis lagi, sudah ada eksperimen.
3. ✅ **Discovery micro-events** yang tidak mungkin via NER (sample #5).
4. ✅ **Semantic predicate enrichment** — upgrade dari INVOLVED_IN generik ke MEMBUNUH/MEMUKUL/dst.

### Yang perlu honest disclosure:
- ⚠️ Schema mismatch ada (10% wrong rate).
- ⚠️ Inferred verb confidence 0.7-0.85 perlu second-pass filter.
- ⚠️ Sample N=10 belum representative; need scale-up untuk angka final.

### Future work yang direkomendasikan:
1. **Scale-up ke 50 chunks** via batch chat (gratis, ~25 menit). Aim: confidence calibration curve.
2. **Pipeline integration:** verb-triplets dengan conf ≥ 0.85 + manual review → merge ke `edges_v4.csv`.
3. **Schema extension:** tambah `unary_fact` field di prompt; `:Concept` label untuk Islam/Iman/dst.
4. **Hybrid pipeline:** proximity (recall tinggi) + LLM verb (precision tinggi) → ensemble.

---

## Status untuk dokumen TA

- ✅ Layak masuk **Bab 4 (Hasil)** sebagai sub-section "POC LLM Verb Extraction".
- ✅ Layak jadi **Bab 5 (Future Work)** sebagai recommended scale-up.
- 📝 Tabel rating 10-sample bisa langsung dipakai sebagai tabel evaluasi.
