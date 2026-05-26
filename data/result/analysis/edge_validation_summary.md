# Edge Validation via Co-occurrence per Period

**Tanggal:** 2026-05-22

**Latar belakang:** Bu Diana di bimbingan 2026-05-16 minta analisis frekuensi
co-occurrence relasi per period sebagai justifikasi validitas relasi di KG.

**Motivasi:** ekstraksi relasi pakai proximity rule global → menghasilkan relasi
spurious seperti `Perang Uhud --OCCURRED_AT--> Aqabah` (semantically wrong;
Uhud period P9, Aqabah natural period P5).

## Summary

- Total edges di edges_v2.csv: **322**
- KEEP   (high-confidence): **30** (9.3%)
- REVIEW (need manual confirm): **185** (57.5%)
- DROP   (likely spurious): **107** (33.2%)

## Verdict per Relation Type

| relation_type | KEEP | REVIEW | DROP | TOTAL |
|---|---|---|---|---|
| INVOLVED_IN | 12 | 50 | 61 | 123 |
| KELUARGA | 9 | 82 | 0 | 91 |
| MUSUH | 3 | 7 | 0 | 10 |
| OCCURRED_AT | 5 | 10 | 10 | 25 |
| OCCURRED_ON | 1 | 11 | 24 | 36 |
| PRECEDES | 0 | 0 | 12 | 12 |
| SAHABAT | 0 | 25 | 0 | 25 |

## DROP Distribution per Relation

- `INVOLVED_IN`: **61** edges flagged DROP
- `OCCURRED_ON`: **24** edges flagged DROP
- `PRECEDES`: **12** edges flagged DROP
- `OCCURRED_AT`: **10** edges flagged DROP

## Top 15 DROP Edges (most suspicious)

Edge yang **single mention di period yang tidak align** dengan natural period EVENT.

| source_name | relation_type | target_name | total_frequency | dominant_period | event_natural_periods |
|---|---|---|---|---|---|
| Abdullah bin Abu Rabi'ah | INVOLVED_IN | Perang Badr | 1 | P9 | P8 |
| Abdullah bin Jahsy | INVOLVED_IN | Perang Uhud | 1 | None | P9 |
| Abdullah bin Ubay bin Salul | INVOLVED_IN | Perang Badr | 1 | P10 | P8 |
| Abrahah | INVOLVED_IN | Perjanjian Hudaibiyah | 1 | P12 | P11 |
| Abu Azzah | INVOLVED_IN | Perang Badr | 1 | P9 | P8 |
| Abu Bakar | INVOLVED_IN | Perang Uhud | 1 | P4 | P9 |
| Abu Hurairah | INVOLVED_IN | Perang Badr | 1 | P9 | P8 |
| Abu Jahal | INVOLVED_IN | Perang Badr | 1 | P4 | P8 |
| Abu Jahal | INVOLVED_IN | Perang Uhud | 1 | None | P9 |
| Abu Musa | INVOLVED_IN | Perang Badr | 1 | P9 | P8 |
| Abu Rasulullah | INVOLVED_IN | Perang Badr | 1 | P5 | P8 |
| Abul Ash | INVOLVED_IN | Fathul Makkah | 1 | P10 | P12 |
| Abul Ash bin Ar-Rabi' | INVOLVED_IN | Perang Badr | 1 | None | P8 |
| Aisyah | INVOLVED_IN | Perang Uhud | 1 | P5 | P9 |
| Al-Harits bin Abdi | INVOLVED_IN | Perang Tabuk | 1 | P14 | P13 |

## Specific Case: Perang Uhud Relations

Validasi anekdot dari kasus motivasi Bu Diana.

| source_name | relation_type | target_name | total_frequency | dominant_period | alignment_ratio | verdict |
|---|---|---|---|---|---|---|
| Ubay bin Khalaf | INVOLVED_IN | Perang Uhud | 1 | P4 | 0.0 | DROP |
| Abu Bakar | INVOLVED_IN | Perang Uhud | 1 | P4 | 0.0 | DROP |
| Muhammad | INVOLVED_IN | Perang Uhud | 11 | P9 | 0.667 | KEEP |
| Urwah bin Az-Zubair | INVOLVED_IN | Perang Uhud | 1 | P5 | 0.0 | DROP |
| Aisyah | INVOLVED_IN | Perang Uhud | 1 | P5 | 0.0 | DROP |
| Ibnu Abdi | INVOLVED_IN | Perang Uhud | 1 | P5 | 0.0 | DROP |
| Yalail bin Abdi | INVOLVED_IN | Perang Uhud | 1 | P5 | 0.0 | DROP |
| Perang Uhud | OCCURRED_AT | Aqabah | 1 | P5 | 0.0 | DROP |
| Perang Uhud | OCCURRED_AT | Madinah | 3 | P8 | 0.333 | REVIEW |
| Perang Uhud | OCCURRED_ON | bulan Muharram 3 H | 1 | P8 | 0.0 | DROP |
| Perang Uhud | OCCURRED_ON | bulan Jumada | 1 | P8 | 0.0 | DROP |
| Abu Azzah | INVOLVED_IN | Perang Uhud | 1 | P9 | 1.0 | REVIEW |
| Abu Sufyan bin Harb | INVOLVED_IN | Perang Uhud | 4 | P9 | 1.0 | KEEP |
| As'ad bin Zurarah | INVOLVED_IN | Perang Uhud | 1 | P9 | 1.0 | REVIEW |
| Perang Uhud | OCCURRED_ON | bulan Rabi'ul Awwal 4 H | 1 | P9 | 1.0 | REVIEW |
| Perang Uhud | OCCURRED_ON | bulan Jumadil Ula | 1 | P9 | 1.0 | REVIEW |
| Abu Salamah bin Abdul Asad | INVOLVED_IN | Perang Uhud | 1 | P9 | 1.0 | REVIEW |
| Perang Uhud | OCCURRED_ON | bulan Muharram 4 H | 1 | P9 | 1.0 | REVIEW |
| Amr bin Umayyah | INVOLVED_IN | Perang Uhud | 1 | P9 | 1.0 | REVIEW |
| Ka'b bin Al-Asyraf | INVOLVED_IN | Perang Uhud | 1 | P9 | 1.0 | REVIEW |
| Perang Uhud | OCCURRED_AT | Hunain | 1 | P13 | 0.0 | DROP |
| Hilal bin Amir bin Sha'sha'ah | INVOLVED_IN | Perang Uhud | 1 | None | 0.0 | DROP |
| Abdullah bin Jahsy | INVOLVED_IN | Perang Uhud | 1 | None | 0.0 | DROP |
| Perang Uhud | OCCURRED_ON | tahun 4 H | 1 | None | 0.0 | DROP |
| Ummu Salamah | INVOLVED_IN | Perang Uhud | 1 | None | 0.0 | DROP |
| Abu Jahal | INVOLVED_IN | Perang Uhud | 1 | None | 0.0 | DROP |
| Khalid bin Al-Walid | INVOLVED_IN | Perang Uhud | 1 | None | 0.0 | DROP |
| Fathul Makkah | PRECEDES | Perang Uhud | 1 | None | 0.0 | DROP |

## Implikasi & Next Action

1. **Filter strict:** drop 107 edges → edges_v3.csv punya 215 edges. Trade-off: edges turun 33.2%, semantic accuracy naik.
2. **Manual review 185 REVIEW edges** sebelum apply ke v3 — terutama
   yang freq>=2 tapi period mismatch (kemungkinan ada nuansa naratif).
3. **Fix proximity extraction** di `relation_extraction.py`:
   - Tambah period-aware filter saat scanning kalimat
   - Jangan create edge antara entitas dari period yang jauh berbeda
4. **Validasi case study:** Perang Uhud-Aqabah, Perang Uhud-Hunain confirmed
   spurious. Run pattern check serupa untuk Perang Badr, Perjanjian Hudaibiyah, dll.

## Catatan Jujur

- **Heuristic verdict bukan ground truth** — kasus borderline (event yang valid
  spans multiple periods, mis. Perjanjian Hudaibiyah berimplikasi sampai Fathu
  Makkah) bisa false-flag DROP. Wajib manual review sebelum apply.
- **Edges tanpa EVENT** (PERSON-PERSON KELUARGA, dll) tidak bisa di-validate
  via period alignment — fallback frequency-only. Kasus seperti family relation
  yang cuma single-mention butuh manual review.
- **Page_range EVENT** di nodes_v2 kadang melebar ke beberapa period (mis.
  Perang Khaibar 473-492 = P11 saja). Tapi event yang spans 2-3 period akan
  match ke semua period itu (overlap detection).
