# LLM Verb Extraction POC — Hasil

**Tanggal:** 2026-05-26

**Latar belakang:** Revisi Bu Diana 2026-05-16 — leverage LLM untuk extract verb-action di Sirah, kandidat EVENT entity baru + SVO relation triplets.

**Sumber prompt:** `data/result/llm_verb_extraction/prompt.md`
**Sample chunks:** `data/result/llm_verb_extraction/sample_chunks.csv` (10 chunks: 5 phase coverage + 5 Perang Badr)

**Response file:** `data/result/llm_verb_extraction/responses/llm_verb_response.json`

## Ringkasan

- Kandidat EVENT  : **18**
- SVO triplet     : **28**

## Kandidat EVENT — Top 10 by Confidence

| Chunk | Hal | Label Aksi | Verb | Subject | Conf |
|---|---|---|---|---|---:|
| 000140-003 | 295-297 | Pemukulan Abu Lahab oleh Ummul Fadhl di Zamzam | memukulkan | Ummul Fadhl | 0.95 |
| 000140-003 | 295-297 | Kematian Abu Lahab pasca Perang Badr | meninggal | Abu Lahab | 0.95 |
| 000131-002 | 281-282 | Pembunuhan Utbah bin Rabi'ah oleh Hamzah dan Ali | membunuh | Hamzah dan Ali bin Abu Thalib | 0.95 |
| 000131-002 | 281-282 | Wafatnya Ubaidah bin Al-Harits di Ash-Shafra' | meninggal | Ubaidah bin Al-Harits | 0.95 |
| 000142-002 | 298-299 | Eksekusi An-Nadhr bin Al-Harits di Ash-Shafra' | dipenggal | Ali bin Abu Thalib | 0.95 |
| 000142-002 | 298-299 | Eksekusi Uqbah bin Abu Mu'aith di Irquzh Zhabyah | dibunuh | Ashim bin Tsabit Al-Anshari | 0.95 |
| 000140-001 | 295-297 | Penyampaian kabar kekalahan Quraisy di Makkah | menyampaikan | Al-Haisuman bin Abdullah Al-Khuza'i | 0.95 |
| 000140-003 | 295-297 | Penyerangan Abu Rafi' oleh Abu Lahab | memukul | Abu Lahab | 0.90 |
| 000254-002 | 465-469 | Masuk Islam Amr di hadapan Najasyi | masuk Islam | Amr | 0.90 |
| 000254-002 | 465-469 | Masuk Islam Raja Najasyi | masuk Islam | Najasyi | 0.90 |

## SVO Triplet — Top 10 by Confidence

| Chunk | Subject (label) | Verb | Object (label) | Conf |
|---|---|---|---|---:|
| 000140-003 | Ummul Fadhl (PERSON) | MEMUKUL | Abu Lahab (PERSON) | 0.95 |
| 000131-002 | Ubaidah bin Al-Harits (PERSON) | BERTANDING_DENGAN | Utbah bin Rabi'ah (PERSON) | 0.95 |
| 000131-002 | Hamzah (PERSON) | BERTANDING_DENGAN | Syaibah bin Rabi'ah (PERSON) | 0.95 |
| 000131-002 | Ali bin Abu Thalib (PERSON) | BERTANDING_DENGAN | Al-Walid (PERSON) | 0.95 |
| 000131-002 | Hamzah (PERSON) | MEMBUNUH | Utbah bin Rabi'ah (PERSON) | 0.95 |
| 000131-002 | Ali bin Abu Thalib (PERSON) | MEMBUNUH | Utbah bin Rabi'ah (PERSON) | 0.95 |
| 000131-002 | Ubaidah bin Al-Harits (PERSON) | MENINGGAL_DI | Ash-Shafra' (LOCATION) | 0.95 |
| 000142-002 | Muhammad (PERSON) | BERGERAK_KE | Madinah (LOCATION) | 0.95 |
| 000142-002 | Ali bin Abu Thalib (PERSON) | MEMBUNUH | An-Nadhr bin Al-Harits (PERSON) | 0.95 |
| 000142-002 | Muhammad (PERSON) | MEMERINTAHKAN_BUNUH | Uqbah bin Abu Mu'aith (PERSON) | 0.95 |

## Manual Validation Checklist

Untuk tiap EVENT/triplet, manual review:
- [ ] Apakah subject/object benar-benar named entity (bukan kata ganti)?
- [ ] Apakah verb describe peristiwa historis (bukan internal/cognitive)?
- [ ] Apakah context_text mendukung claim?
- [ ] Apakah duplikasi dengan edges_v2.csv yang sudah ada (cek INVOLVED_IN)?
- [ ] Apakah label_aksi cukup spesifik buat jadi EVENT entity?

## Catatan POC

- Sample N=10 hybrid (5 phase + 5 Badr depth). Bukan random sample.
- Single-prompt batch chat, structured JSON schema. Reproducible via prompt.md.
- Untuk scale-up: ganti ke API + iterate per chunk supaya context lebih fokus.
- LLM cenderung over-extract (false positive) — confidence < 0.7 perlu manual filter.