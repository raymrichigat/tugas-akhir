"""
detect_temporal_relations.py
============================
Deteksi **temporal relations intra-sentence** antar EVENT (revisi Bu Diana cluster #1,
2026-05-03):

  > "Temporal dalam satu kalimat (?) perlu di deteksi (bisa dilihat dari urutan
  > kejadian di Sirah / urutan bab nya)"

Pendekatan: rule-based pattern matching pada kalimat yang mengandung 2+ EVENT.

Temporal cues Bahasa Indonesia:
  - PRECEDES : "sebelum", "sebelumnya", "menjelang", "pra-"  (X sebelum Y → X PRECEDES Y)
  - PRECEDES : "kemudian", "lalu", "berikutnya"              (X kemudian Y → X PRECEDES Y)
  - inverted : "setelah", "sesudah", "pasca-"                (X setelah Y → Y PRECEDES X)
  - CONCURRENT: "saat", "ketika", "pada saat", "tatkala",
                "selama", "bersamaan dengan"                 (X saat Y → X CONCURRENT Y)

Rule (uniform untuk semua pattern):
  - R = event yang berada IMMEDIATELY AFTER cue word (= reference)
  - S = event lainnya dalam kalimat (= subject)
  - Berdasarkan cue_type:
      'before'    : S PRECEDES R
      'then'      : S PRECEDES R   (semantically same as before, beda gramatika)
      'after'     : R PRECEDES S   (inverted)
      'during'    : S CONCURRENT R

Aturan ini handle baik:
  - "X sebelum Y"  (cue di tengah)
  - "Sebelum X, Y" (cue di awal)
  - "X kemudian Y"
  - "Setelah X, Y"
  - dst.

Input:
  - data/result/chunking_result/sirah_chunks_final.csv
  - data/result/relation_result/nodes_v2.csv (untuk daftar EVENT vocab)
  - data/result/relation_result/edges_v2.csv (untuk compare dengan PRECEDES existing)

Output:
  - data/result/relation_result/temporal_relations.csv
  - data/result/relation_result/temporal_summary.md
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
CHUNKS_CSV = BASE_DIR / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
NODES_CSV = BASE_DIR / "data" / "result" / "relation_result" / "nodes_v2.csv"
EDGES_CSV = BASE_DIR / "data" / "result" / "relation_result" / "edges_v2.csv"
OUT_CSV = BASE_DIR / "data" / "result" / "relation_result" / "temporal_relations.csv"
OUT_MD = BASE_DIR / "data" / "result" / "relation_result" / "temporal_summary.md"


# ── Temporal cue lexicon ─────────────────────────────────────────────────────
TEMPORAL_CUES = {
    "before": [
        "sebelum", "sebelumnya", "menjelang",
    ],
    "then": [
        "kemudian", "lalu", "berikutnya", "akhirnya",
        "setelah itu", "setelahnya",   # semantically "then", urutan event implisit
    ],
    "after": [
        "setelah", "sesudah", "pasca",
    ],
    "during": [
        "saat", "ketika", "pada saat", "tatkala", "selama",
        "bersamaan dengan", "bersama dengan", "di kala",
    ],
}

# Hindari false-positive "setelah" yang sebenarnya "setelah itu" (then), karena beda semantik.
# Solusi: cek "setelah itu" dulu (then), baru "setelah" (after).
_CUE_ORDER = ["setelah itu", "setelahnya", "bersamaan dengan", "bersama dengan",
              "pada saat", "di kala"]
# Sisanya lookup biasa


# ── Sentence splitter ────────────────────────────────────────────────────────
_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"])")


def split_sentences(text: str) -> list[tuple[int, int, str]]:
    """
    Split text into sentences. Returns list of (start_char, end_char, sentence_text).
    Char offsets relative to original `text`.
    """
    if not isinstance(text, str):
        return []
    sentences = []
    start = 0
    for m in _SENT_END.finditer(text):
        end = m.start()
        sent = text[start:end].strip()
        if sent:
            sentences.append((start, end, sent))
        start = m.end()
    # Last sentence
    if start < len(text):
        sent = text[start:].strip()
        if sent:
            sentences.append((start, len(text), sent))
    return sentences


# ── Event mention finder ─────────────────────────────────────────────────────
def build_event_pattern(event_names: list[str]) -> re.Pattern:
    """
    Compile single regex untuk match semua event name secara case-insensitive
    dengan word-boundary. Sort by length descending agar yang panjang match dulu
    (mis. "Perang Badr Kubra" sebelum "Perang Badr").
    """
    sorted_names = sorted(event_names, key=len, reverse=True)
    escaped = [re.escape(n) for n in sorted_names]
    pattern = r"\b(" + "|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


def find_event_mentions(sentence: str, event_pattern: re.Pattern,
                        name_canonical: dict[str, str]) -> list[tuple[int, int, str]]:
    """
    Returns list of (start_char, end_char, canonical_name).

    name_canonical: dict {lowercase_name: canonical_name} untuk pulih ke ejaan asli.
    """
    matches = []
    for m in event_pattern.finditer(sentence):
        matched_text = m.group(0)
        canonical = name_canonical.get(matched_text.lower(), matched_text)
        matches.append((m.start(), m.end(), canonical))
    # Sort by position
    matches.sort(key=lambda x: x[0])
    # Dedupe: kalau 2 match overlap, ambil yang lebih panjang (sudah handled by regex sort,
    # tapi back-up untuk safety)
    deduped = []
    for s, e, name in matches:
        if deduped and s < deduped[-1][1]:
            continue   # overlap, skip
        deduped.append((s, e, name))
    return deduped


# ── Temporal cue finder ──────────────────────────────────────────────────────
def find_temporal_cues(sentence: str) -> list[tuple[int, int, str, str]]:
    """
    Returns list of (start, end, cue_word, cue_type).

    Prioritize multi-word cues ("setelah itu", "pada saat") over single-word
    ("setelah", "saat") supaya tidak dobel-match.
    """
    found = []
    consumed = set()   # set of char indices yang sudah "ditutupi" cue

    # Order: longer first
    all_cues = []
    for cue_type, words in TEMPORAL_CUES.items():
        for w in words:
            all_cues.append((w, cue_type, len(w)))
    all_cues.sort(key=lambda x: -x[2])   # longest first

    for word, cue_type, _ in all_cues:
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
        for m in pattern.finditer(sentence):
            # Cek tidak overlap dengan cue yang lebih panjang
            if any(i in consumed for i in range(m.start(), m.end())):
                continue
            found.append((m.start(), m.end(), word, cue_type))
            consumed.update(range(m.start(), m.end()))

    found.sort(key=lambda x: x[0])
    return found


# ── Apply temporal rule ──────────────────────────────────────────────────────
def apply_rule(cue_type: str, S: str, R: str) -> tuple[str, str, str] | None:
    """
    Rule:
      - 'before' atau 'then' : S PRECEDES R
      - 'after'              : R PRECEDES S
      - 'during'             : S CONCURRENT R

    Returns (source, relation_type, target) atau None untuk unknown cue.
    """
    if S == R:
        return None
    if cue_type in ("before", "then"):
        return (S, "PRECEDES", R)
    elif cue_type == "after":
        return (R, "PRECEDES", S)
    elif cue_type == "during":
        # Normalize order untuk CONCURRENT (symmetric) — alphabetic
        a, b = sorted([S, R])
        return (a, "CONCURRENT", b)
    return None


_HYPOTHETICAL_MARKERS = re.compile(
    r"\b(kemungkinan|boleh jadi|barangkali|seandainya|andaikata|mungkin saja|"
    r"tidak menutup kemungkinan|kalau saja)\b",
    re.IGNORECASE,
)


def _are_aliases(name_a: str, name_b: str, alias_groups: list[set]) -> bool:
    """Cek apakah 2 nama event termasuk alias group yang sama."""
    for group in alias_groups:
        if name_a in group and name_b in group:
            return True
    return False


# Manual alias groups untuk EVENT — pasangan yang merujuk same event meskipun nama beda.
# Bisa diperluas kalau ada finding alias lain.
_EVENT_ALIAS_GROUPS: list[set[str]] = [
    {"Baiat Aqabah", "Baiat Aqabah Kubra"},          # Baiat Aqabah Pertama vs Kedua (=Kubra)
                                                      # NB: secara historis berbeda (Pertama vs Kedua),
                                                      # tapi di NER teks-nya sering ambigu — drop relasi antar keduanya
    {"Perang Badr", "Perang Badr Kubra"},            # alias dari same event
    {"Perang Mu'tah", "Ghazwah Mu'tah"},             # ghazwah = perang
    {"Ghazwah Dzatu Qarad", "Perang Dzatur Riqa'"},  # potentially aliased post-review
    {"Isra' Mi'raj", "Isra'", "Mi'raj"},             # split events
]


def infer_relations_from_sentence(
    sentence: str,
    event_pattern: re.Pattern,
    name_canonical: dict[str, str],
) -> list[dict]:
    """
    Extract temporal relations dari satu kalimat.

    Returns list of dict: {source, target, relation_type, cue, cue_type, evidence}
    """
    # Skip kalimat hipotetis/spekulatif (mengandung "kemungkinan", "boleh jadi", dst).
    # Kalimat seperti ini sering kontain multiple events tapi BUKAN temporal assertion.
    if _HYPOTHETICAL_MARKERS.search(sentence):
        return []

    events = find_event_mentions(sentence, event_pattern, name_canonical)
    if len(events) < 2:
        return []

    cues = find_temporal_cues(sentence)
    if not cues:
        return []

    relations = []
    for cue_start, cue_end, cue_word, cue_type in cues:
        # R = first event AFTER cue (event yang start >= cue_end)
        # S = event lainnya (terdekat sebelum cue, atau kalau cue di awal, event ke-2)
        events_after = [ev for ev in events if ev[0] >= cue_end]
        events_before = [ev for ev in events if ev[1] <= cue_start]

        if not events_after:
            continue   # cue di akhir kalimat, no event mengikuti

        R = events_after[0][2]   # nearest event after cue

        # S = event yang BUKAN R. Strategi:
        #   - Kalau cue di awal kalimat (no event before): pakai events_after[1] sebagai S
        #     karena pattern "[cue] [R], [S]" valid (mis. "Setelah Hudaibiyah, Khaibar").
        #   - Kalau cue di tengah/akhir kalimat (ada event before): pakai event before sebagai S.
        #     JANGAN fallback ke events_after[1] kalau cue di tengah — terlalu banyak false-positive
        #     pada kalimat hipotetis/meta ("Sebab ada kemungkinan ... setelah X ... ketika Y...").
        cue_at_start = (cue_start < 30)   # heuristik: cue di 30 char pertama = awal kalimat
        if events_before:
            S = events_before[-1][2]
        elif cue_at_start and len(events_after) >= 2:
            S = events_after[1][2]
        else:
            continue   # cue di tengah tanpa event before, skip (avoid false-positive)

        rel = apply_rule(cue_type, S, R)
        if rel is None:
            continue

        src, rel_type, tgt = rel

        # Alias filter: skip kalau source & target merujuk same event
        if _are_aliases(src, tgt, _EVENT_ALIAS_GROUPS):
            continue

        relations.append({
            "source": src,
            "target": tgt,
            "relation_type": rel_type,
            "cue": cue_word,
            "cue_type": cue_type,
            "evidence": sentence[:250] + ("..." if len(sentence) > 250 else ""),
        })

    return relations


# ── Pipeline ────────────────────────────────────────────────────────────────
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print(f"[load] {NODES_CSV.name}")
    nodes_df = pd.read_csv(NODES_CSV, sep=";", encoding="utf-8-sig").fillna("")
    event_names = nodes_df[nodes_df["label"] == "EVENT"]["name"].tolist()
    print(f"  {len(event_names)} EVENT names")

    # Lookup map lowercase → canonical
    name_canonical = {n.lower(): n for n in event_names}
    event_pattern = build_event_pattern(event_names)

    print(f"[load] {CHUNKS_CSV.name}")
    chunks_df = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8")
    print(f"  {len(chunks_df)} chunks")

    # Process each chunk
    all_relations = []
    sentence_count = 0
    sentence_with_events = 0
    sentence_with_temporal = 0

    for _, row in chunks_df.iterrows():
        text = str(row.get("teks_chunk", ""))
        chunk_id = row.get("chunk_id", "")
        halaman = row.get("halaman", "")

        sentences = split_sentences(text)
        for s_start, s_end, sent in sentences:
            sentence_count += 1
            events_in_sent = find_event_mentions(sent, event_pattern, name_canonical)
            if len(events_in_sent) >= 2:
                sentence_with_events += 1
            rels = infer_relations_from_sentence(sent, event_pattern, name_canonical)
            if rels:
                sentence_with_temporal += 1
                for r in rels:
                    r["chunk_id"] = chunk_id
                    r["halaman"] = halaman
                    all_relations.append(r)

    print(f"\n[stats]")
    print(f"  total sentences           : {sentence_count}")
    print(f"  sentences with 2+ events  : {sentence_with_events}")
    print(f"  sentences with temporal   : {sentence_with_temporal}")
    print(f"  raw relations extracted   : {len(all_relations)}")

    # Aggregate: dedup by (source, relation_type, target), keep evidence list
    agg: dict[tuple, dict] = {}
    for r in all_relations:
        key = (r["source"], r["relation_type"], r["target"])
        if key not in agg:
            agg[key] = {
                "source": r["source"],
                "relation_type": r["relation_type"],
                "target": r["target"],
                "cue_words": set(),
                "cue_types": set(),
                "evidences": [],
                "chunk_ids": set(),
                "frequency": 0,
            }
        entry = agg[key]
        entry["cue_words"].add(r["cue"])
        entry["cue_types"].add(r["cue_type"])
        entry["evidences"].append(r["evidence"])
        entry["chunk_ids"].add(r["chunk_id"])
        entry["frequency"] += 1

    # Write CSV
    rows = []
    for key, info in agg.items():
        rows.append({
            "source": info["source"],
            "relation_type": info["relation_type"],
            "target": info["target"],
            "frequency": info["frequency"],
            "cue_words": ", ".join(sorted(info["cue_words"])),
            "cue_types": ", ".join(sorted(info["cue_types"])),
            "chunk_ids": " | ".join(sorted(info["chunk_ids"])),
            "evidences": " ||| ".join(info["evidences"][:3]),   # max 3 evidence
        })
    out_df = pd.DataFrame(rows).sort_values(["relation_type", "frequency"], ascending=[True, False])
    out_df.to_csv(OUT_CSV, sep=";", index=False, encoding="utf-8-sig")
    print(f"\n[write] {OUT_CSV.name} ({len(out_df)} unique relations)")

    # Compare with existing PRECEDES (from edges_v2.csv)
    print(f"\n[compare] vs existing PRECEDES in edges_v2.csv...")
    edges_df = pd.read_csv(EDGES_CSV, sep=";", encoding="utf-8-sig").fillna("")
    existing_precedes = set()
    for _, e in edges_df[edges_df["relation_type"] == "PRECEDES"].iterrows():
        existing_precedes.add((e["source_name"], e["target_name"]))

    new_precedes = set()
    for _, r in out_df[out_df["relation_type"] == "PRECEDES"].iterrows():
        new_precedes.add((r["source"], r["target"]))

    intersection = new_precedes & existing_precedes
    only_new = new_precedes - existing_precedes
    only_existing = existing_precedes - new_precedes

    print(f"  existing PRECEDES (page-order): {len(existing_precedes)}")
    print(f"  new PRECEDES (intra-sentence) : {len(new_precedes)}")
    print(f"  intersection (confirmed)      : {len(intersection)}")
    print(f"  only intra-sentence (NEW)     : {len(only_new)}")
    print(f"  only page-order (uncovered)   : {len(only_existing)}")

    n_concurrent = (out_df["relation_type"] == "CONCURRENT").sum()
    print(f"  CONCURRENT relations (baru)   : {n_concurrent}")

    # Write summary markdown
    lines = [
        "# Temporal Relations — Intra-Sentence Detection",
        "",
        "Hasil deteksi temporal relations antar EVENT dalam satu kalimat menggunakan",
        "pendekatan rule-based dengan temporal cues Bahasa Indonesia.",
        "",
        "Metode mengikuti revisi Bu Diana cluster #1 (2026-05-03): "
        '*"Temporal dalam satu kalimat perlu di deteksi (bisa dilihat dari urutan kejadian di Sirah)"*.',
        "",
        "## 1. Statistik Ekstraksi",
        "",
        f"| Metric | Count |",
        f"|---|---:|",
        f"| Total kalimat di chunks | {sentence_count} |",
        f"| Kalimat dengan 2+ EVENT | {sentence_with_events} |",
        f"| Kalimat dengan temporal cue | {sentence_with_temporal} |",
        f"| Raw relations diekstrak | {len(all_relations)} |",
        f"| Unique relations setelah dedup | {len(out_df)} |",
        f"| PRECEDES intra-sentence | {len(new_precedes)} |",
        f"| CONCURRENT (relasi baru) | {n_concurrent} |",
        "",
        "## 2. Comparison: Intra-Sentence vs Page-Order PRECEDES",
        "",
        "PRECEDES sebelumnya dibangun dari **urutan halaman BAB** (page-order chronology).",
        "Sekarang ditambahkan PRECEDES dari **kalimat eksplisit** (intra-sentence).",
        "",
        f"| Source | Count | Catatan |",
        f"|---|---:|---|",
        f"| Page-order PRECEDES (existing edges_v2.csv) | {len(existing_precedes)} | Berbasis page_start event |",
        f"| Intra-sentence PRECEDES (new) | {len(new_precedes)} | Berbasis cue \"sebelum/setelah/kemudian\" |",
        f"| **Intersection** (kedua metode confirm) | **{len(intersection)}** | Strong evidence — multi-source |",
        f"| Only intra-sentence (NEW finding) | {len(only_new)} | Tidak terdeteksi page-order — kemungkinan event dalam BAB sama |",
        f"| Only page-order (uncovered by sentence) | {len(only_existing)} | Tidak ada kalimat eksplisit yang link 2 event ini |",
        "",
    ]

    if intersection:
        lines.append("### 2.1 Confirmed by both methods (top 10)")
        lines.append("")
        for src, tgt in sorted(intersection)[:10]:
            lines.append(f"- `{src}` → `{tgt}`")
        lines.append("")

    if only_new:
        lines.append("### 2.2 New PRECEDES (intra-sentence only)")
        lines.append("")
        for src, tgt in sorted(only_new):
            sub = out_df[(out_df["source"] == src) & (out_df["target"] == tgt) &
                         (out_df["relation_type"] == "PRECEDES")]
            if len(sub) > 0:
                freq = sub.iloc[0]["frequency"]
                cue = sub.iloc[0]["cue_words"]
                lines.append(f"- `{src}` → `{tgt}` (freq={freq}, cue=\"{cue}\")")
        lines.append("")

    lines += [
        "## 3. Top 15 by Frequency",
        "",
        "| Source | Relation | Target | Freq | Cue Words |",
        "|---|---|---|---:|---|",
    ]
    top15 = out_df.nlargest(15, "frequency")
    for _, r in top15.iterrows():
        lines.append(
            f"| {r['source']} | {r['relation_type']} | {r['target']} | {r['frequency']} | {r['cue_words']} |"
        )

    lines += [
        "",
        "## 4. Cue Type Distribution",
        "",
        "| Cue Type | Count |",
        "|---|---:|",
    ]
    cue_count = defaultdict(int)
    for _, r in out_df.iterrows():
        for ct in str(r["cue_types"]).split(", "):
            cue_count[ct.strip()] += 1
    for ct, cnt in sorted(cue_count.items(), key=lambda x: -x[1]):
        lines.append(f"| {ct} | {cnt} |")

    lines += [
        "",
        "## 5. Limitasi & Catatan",
        "",
        "- **Rule-based**: tidak handle anaphora atau coreference (mis. \"setelah itu\" yang merujuk event di kalimat sebelumnya).",
        "- **Word-boundary match**: event yang nama-nya substring dari event lain (mis. \"Perang Badr\" vs \"Perang Badr Kubra\") di-handle via length-sorted regex.",
        "- **Cue ambiguous**: \"setelah\" vs \"setelah itu\" — \"setelah itu\" dipetakan sebagai \"then\" (urutan event implicit), \"setelah\" sebagai \"after\" (inverted). Aturan ini dipakai supaya \"X setelah itu Y\" tidak salah interpretasi.",
        "- **Event vocab**: pakai 36 EVENT dari nodes_v2.csv post-review. Event noise/ambigu sudah di-R sebelumnya.",
        "- **No confidence score** sementara — tiap relasi dianggap valid kalau cue + 2 events match. Future: tambah skor confidence berdasarkan jumlah cue alternatif atau parse tree.",
        "",
        "## 6. Integrasi ke Knowledge Graph",
        "",
        "Hasil ini bisa di-merge ke `edges_v2.csv` sebagai tambahan relasi PRECEDES & CONCURRENT.",
        "Rekomendasi: gunakan **union** dari page-order dan intra-sentence PRECEDES untuk maximum recall,",
        "dengan kolom `source_method` untuk track asal-usul relasi.",
        "",
        f"File source: `{OUT_CSV.name}` ({len(out_df)} unique relations)",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"[write] {OUT_MD.name}")


if __name__ == "__main__":
    main()
