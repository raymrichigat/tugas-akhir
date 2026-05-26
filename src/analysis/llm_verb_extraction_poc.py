"""
llm_verb_extraction_poc.py
===========================
POC LLM verb extraction untuk Knowledge Graph Sirah (revisi Bu Diana 2026-05-16).

Latar belakang:
Bu Diana minta antisipasi support EVENT yang kecil di NER (47 EVENT entity, F1
~0.77) — gunakan LLM untuk extract **verb-action** dari teks Sirah. Verb yang
menggambarkan peristiwa bisa jadi:
  1. Kandidat EVENT entity baru (peristiwa tanpa nama spesifik, mis. "berbaiat",
     "menyerang", "berdoa di Ka'bah").
  2. Kandidat SVO relation triplet (subject_entity --VERB--> object_entity)
     untuk enrich edges_v2.csv.

Pendekatan POC: **single-prompt batch chat** (gratis, reproducible).
- Script ini generate 1 file prompt `.md` yang berisi 10 chunks hybrid
  (5 chunks dari 5 fase berbeda + 5 chunks fokus Perang Badr).
- User paste prompt ke Claude.ai / ChatGPT / Gemini chat → dapat JSON output.
- Paste JSON output kembali ke `responses/llm_verb_response.json`.
- Run script lagi dengan `--parse` untuk parse + dump ke CSV.

Sample selection:
- 5 chunks "fase coverage": 1 per fase (P0, P5, P8, P11, P14) — pick chunk
  yang halamannya tengah-tengah fase + judul bab tidak generic.
- 5 chunks "Perang Badr depth": chunk dari halaman 266-304 yang banyak
  narasi action (filtered by length text > 500 char).

Output (mode=generate):
  - data/result/llm_verb_extraction/prompt.md
  - data/result/llm_verb_extraction/sample_chunks.csv (untuk audit)
  - data/result/llm_verb_extraction/responses/.gitkeep

Output (mode=parse):
  - data/result/llm_verb_extraction/verb_extraction_events.csv
  - data/result/llm_verb_extraction/verb_extraction_triplets.csv
  - data/result/llm_verb_extraction/verb_extraction_summary.md

Idempotent. Usage:
  # Step 1: generate prompt + sample chunks
  python src/analysis/llm_verb_extraction_poc.py --mode generate

  # Step 2: paste prompt ke Claude.ai, save JSON response ke
  #         data/result/llm_verb_extraction/responses/llm_verb_response.json

  # Step 3: parse JSON response → CSV
  python src/analysis/llm_verb_extraction_poc.py --mode parse
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
PERIOD_JSON = ROOT / "data" / "result" / "relation_result" / "period_mapping.json"

OUT_DIR = ROOT / "data" / "result" / "llm_verb_extraction"
PROMPT_MD = OUT_DIR / "prompt.md"
SAMPLE_CSV = OUT_DIR / "sample_chunks.csv"
RESPONSES_DIR = OUT_DIR / "responses"
RESPONSE_FILE = RESPONSES_DIR / "llm_verb_response.json"

EVENTS_CSV = OUT_DIR / "verb_extraction_events.csv"
TRIPLETS_CSV = OUT_DIR / "verb_extraction_triplets.csv"
SUMMARY_MD = OUT_DIR / "verb_extraction_summary.md"

PHASE_COVERAGE_PERIODS = ["P0", "P5", "P8", "P11", "P14"]
BADR_PAGE_START = 266
BADR_PAGE_END = 304
N_BADR_CHUNKS = 5
SEED = 42


def load_periods() -> dict[str, dict]:
    with open(PERIOD_JSON, encoding="utf-8") as f:
        periods = json.load(f)
    return {p["period_id"]: p for p in periods}


def load_chunks() -> pd.DataFrame:
    df = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig")
    df["first_page"] = df["halaman"].astype(str).str.extract(r"^(\d+)").astype(float)
    df["text_len"] = df["teks_chunk"].astype(str).str.len()
    return df


def select_phase_coverage(chunks: pd.DataFrame, periods: dict[str, dict]) -> pd.DataFrame:
    rng = random.Random(SEED)
    rows = []
    for pid in PHASE_COVERAGE_PERIODS:
        p = periods[pid]
        sub = chunks[
            (chunks["first_page"] >= p["page_start"])
            & (chunks["first_page"] <= p["page_end"])
            & (chunks["text_len"] >= 500)
        ].copy()
        if sub.empty:
            print(f"  [WARN] no eligible chunk for {pid} (>500 char)")
            continue
        # Avoid generic intro chunks - prefer middle of period
        mid_page = (p["page_start"] + p["page_end"]) / 2
        sub["dist_to_mid"] = (sub["first_page"] - mid_page).abs()
        sub = sub.sort_values(["dist_to_mid", "text_len"], ascending=[True, False])
        # Random pick among top-5 closest-to-middle for diversity
        candidates = sub.head(5)
        idx = rng.randint(0, len(candidates) - 1)
        chosen = candidates.iloc[idx].to_dict()
        chosen["sample_group"] = f"phase_{pid}"
        chosen["sample_period"] = pid
        chosen["sample_phase"] = p.get("phase", "")
        rows.append(chosen)
    return pd.DataFrame(rows)


def select_badr_depth(chunks: pd.DataFrame) -> pd.DataFrame:
    rng = random.Random(SEED + 1)
    sub = chunks[
        (chunks["first_page"] >= BADR_PAGE_START)
        & (chunks["first_page"] <= BADR_PAGE_END)
        & (chunks["text_len"] >= 500)
    ].copy()
    sub = sub.sort_values("text_len", ascending=False)
    candidates = sub.head(15)  # top 15 longest
    if len(candidates) < N_BADR_CHUNKS:
        chosen = candidates
    else:
        idx_list = rng.sample(range(len(candidates)), N_BADR_CHUNKS)
        chosen = candidates.iloc[idx_list]
    out = chosen.copy()
    out["sample_group"] = "perang_badr"
    out["sample_period"] = "P8"
    out["sample_phase"] = "Fase IV — Periode Peperangan Besar"
    return out


PROMPT_TEMPLATE = """\
# Tugas: Verb Action Extraction dari Teks Sirah Nabawiyah

Anda adalah asisten ekstraksi informasi yang ahli dalam Bahasa Indonesia dan teks
historis Sirah Nabawiyah. Tugas Anda: dari setiap chunk teks yang diberikan,
ekstrak **verb-action** (kata kerja yang menggambarkan peristiwa) bersama
subject (pelaku) dan object (penerima/lawan/lokasi tindakan).

## Tujuan

1. **Kandidat EVENT baru**: verb yang menggambarkan peristiwa terbatas waktu/ruang,
   yang **tidak punya nama proper noun** (mis. "berbaiat di Aqabah", "menyerang
   karavan", "berdoa di Ka'bah"). Bukan verb biasa seperti "berkata", "melihat".

2. **SVO relation triplet**: triplet (subject_entity, verb_relation, object_entity)
   yang bisa di-add ke Knowledge Graph sebagai relasi baru. Subject & object
   harus berupa **named entity** (PERSON, LOCATION, EVENT, atau TIME).

## Aturan Ekstraksi

**Untuk EVENT kandidat:**
- Hanya verb yang menggambarkan **aksi historis** (bertempur, berhijrah, berbaiat,
  bertukar surat, menyerang, mengutus, mendirikan, mengadakan perjanjian).
- **Skip** verb mental/percakapan biasa (berkata, mendengar, memikirkan, melihat,
  bertanya tanpa konteks aksi).
- **Skip** verb yang sudah punya named EVENT di teks (mis. kalau ada "Perang Badr",
  jangan extract lagi "berperang" sebagai EVENT — sudah ke-cover NER).
- Beri "label_aksi" pendek (2-4 kata) yang merangkum peristiwa.

**Untuk SVO triplet:**
- Subject & object harus **named entity** (nama orang, kabilah, lokasi, atau peristiwa
  bernama). Bukan kata ganti ("dia", "mereka") atau noun phrase generik ("orang itu",
  "para sahabat").
- relation_type proposal — gunakan kata kerja kanonik seperti:
  `MENGUTUS, MENYERANG, MENIKAHI, BERBAIAT_KEPADA, BERPERANG_DENGAN, MEMIMPIN,
   MENGUNJUNGI, BERHIJRAH_KE, MENGAJAR, MENERIMA_WAHYU, MENGUMUMKAN, MEMBANGUN,
   MENERIMA_DELEGASI, BERDAMAI_DENGAN, MENGEPUNG`
  Boleh tambah relation_type baru jika perlu, gunakan UPPER_SNAKE_CASE.

## Format Output (WAJIB JSON murni, tanpa markdown fence)

```
{{
  "events": [
    {{
      "chunk_id": "000123-004",
      "halaman": "266",
      "label_aksi": "Pengiriman delegasi ke Madinah",
      "verb": "mengutus",
      "subject": "Muhammad",
      "context_text": "Rasulullah mengutus Mush'ab bin Umair ke Madinah untuk...",
      "confidence": 0.9
    }}
  ],
  "triplets": [
    {{
      "chunk_id": "000123-004",
      "halaman": "266",
      "subject_entity": "Muhammad",
      "subject_label": "PERSON",
      "verb_relation": "MENGUTUS",
      "object_entity": "Mush'ab bin Umair",
      "object_label": "PERSON",
      "context_text": "Rasulullah mengutus Mush'ab bin Umair ke Madinah",
      "confidence": 0.9
    }}
  ]
}}
```

## Instruksi Penting

- Output **JSON valid murni**, tanpa code fence (```), tanpa narrative pengantar
  atau closing.
- Kalau satu chunk tidak ada kandidat, tetap lanjut ke chunk berikutnya, jangan
  paksa output.
- Confidence 0-1: 1 = jelas dari teks, 0.5 = ambigu, 0.3 = tebakan.
- Label entity harus salah satu dari: `PERSON, LOCATION, EVENT, TIME`.
- Bahasa Indonesia untuk semua field.

---

# Chunks Input

{chunks_text}

---

Mulai ekstraksi sekarang. Output JSON murni saja.
"""


def render_prompt(samples: pd.DataFrame) -> str:
    chunk_blocks = []
    for _, row in samples.iterrows():
        block = (
            f"## Chunk `{row['chunk_id']}`  (halaman {row['halaman']}, "
            f"sample={row['sample_group']}, period={row['sample_period']})\n\n"
            f"**Bab:** {row['judul_bab']}  /  **Sub-bab:** {row.get('judul_sub_bab','')}\n\n"
            f"```\n{row['teks_chunk']}\n```\n"
        )
        chunk_blocks.append(block)
    chunks_text = "\n".join(chunk_blocks)
    return PROMPT_TEMPLATE.format(chunks_text=chunks_text)


def cmd_generate():
    print("=" * 60)
    print("LLM VERB EXTRACTION — Generate Prompt")
    print("=" * 60)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    (RESPONSES_DIR / ".gitkeep").touch()

    print("\n[1/4] loading chunks + periods...")
    chunks = load_chunks()
    periods = load_periods()
    print(f"  total chunks  : {len(chunks)}")
    print(f"  total periods : {len(periods)}")

    print("\n[2/4] selecting phase-coverage samples...")
    phase_samples = select_phase_coverage(chunks, periods)
    print(f"  selected: {len(phase_samples)} chunks (1 per phase coverage period)")

    print("\n[3/4] selecting Perang Badr depth samples...")
    badr_samples = select_badr_depth(chunks)
    print(f"  selected: {len(badr_samples)} chunks (Perang Badr region p266-304)")

    samples = pd.concat([phase_samples, badr_samples], ignore_index=True)
    samples_out = samples[
        ["chunk_id", "halaman", "sample_group", "sample_period",
         "sample_phase", "judul_bab", "text_len"]
    ]
    samples_out.to_csv(SAMPLE_CSV, index=False, sep=";", encoding="utf-8-sig")
    print(f"  -> {SAMPLE_CSV}")

    print("\n[4/4] rendering prompt...")
    prompt = render_prompt(samples)
    PROMPT_MD.write_text(prompt, encoding="utf-8")
    n_chars = len(prompt)
    n_words = len(prompt.split())
    print(f"  -> {PROMPT_MD}")
    print(f"  prompt size   : {n_chars:,} chars / ~{n_words:,} words / "
          f"~{n_chars // 4:,} tokens (rough est)")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"1. Buka file: {PROMPT_MD}")
    print(f"2. Copy seluruh isi -> paste ke Claude.ai (atau ChatGPT/Gemini chat).")
    print(f"3. Tunggu output JSON -> copy seluruh JSON output.")
    print(f"4. Save JSON ke: {RESPONSE_FILE}")
    print(f"5. Run: python src/analysis/llm_verb_extraction_poc.py --mode parse")


def cmd_parse():
    print("=" * 60)
    print("LLM VERB EXTRACTION — Parse Response")
    print("=" * 60)

    if not RESPONSE_FILE.exists():
        print(f"\n[ERR] response file tidak ditemukan: {RESPONSE_FILE}")
        print("       Pastikan sudah save JSON output dari LLM ke path itu.")
        return

    raw = RESPONSE_FILE.read_text(encoding="utf-8").strip()
    # Strip code fence kalau LLM lupa instruction
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"\n[ERR] JSON invalid: {e}")
        print("       Edit file response → pastikan JSON murni (tanpa markdown).")
        return

    events = data.get("events", [])
    triplets = data.get("triplets", [])
    print(f"\n  parsed events : {len(events)}")
    print(f"  parsed triplets: {len(triplets)}")

    if events:
        ev_df = pd.DataFrame(events)
        ev_df.to_csv(EVENTS_CSV, index=False, sep=";", encoding="utf-8-sig")
        print(f"  -> {EVENTS_CSV}")

    if triplets:
        tr_df = pd.DataFrame(triplets)
        tr_df.to_csv(TRIPLETS_CSV, index=False, sep=";", encoding="utf-8-sig")
        print(f"  -> {TRIPLETS_CSV}")

    lines: list[str] = []
    lines.append("# LLM Verb Extraction POC — Hasil\n")
    lines.append("**Tanggal:** 2026-05-26\n")
    lines.append("**Latar belakang:** Revisi Bu Diana 2026-05-16 — leverage LLM untuk extract "
                 "verb-action di Sirah, kandidat EVENT entity baru + SVO relation triplets.\n")
    lines.append(f"**Sumber prompt:** `{PROMPT_MD.relative_to(ROOT).as_posix()}`")
    lines.append(f"**Sample chunks:** `{SAMPLE_CSV.relative_to(ROOT).as_posix()}` "
                 "(10 chunks: 5 phase coverage + 5 Perang Badr)\n")
    lines.append(f"**Response file:** `{RESPONSE_FILE.relative_to(ROOT).as_posix()}`\n")
    lines.append("## Ringkasan\n")
    lines.append(f"- Kandidat EVENT  : **{len(events)}**")
    lines.append(f"- SVO triplet     : **{len(triplets)}**\n")

    if events:
        lines.append("## Kandidat EVENT — Top 10 by Confidence\n")
        ev_sorted = sorted(events, key=lambda x: x.get("confidence", 0), reverse=True)[:10]
        lines.append("| Chunk | Hal | Label Aksi | Verb | Subject | Conf |")
        lines.append("|---|---|---|---|---|---:|")
        for e in ev_sorted:
            lines.append(
                f"| {e.get('chunk_id','')} | {e.get('halaman','')} | "
                f"{e.get('label_aksi','')} | {e.get('verb','')} | "
                f"{e.get('subject','')} | {e.get('confidence',0):.2f} |"
            )
        lines.append("")

    if triplets:
        lines.append("## SVO Triplet — Top 10 by Confidence\n")
        tr_sorted = sorted(triplets, key=lambda x: x.get("confidence", 0), reverse=True)[:10]
        lines.append("| Chunk | Subject (label) | Verb | Object (label) | Conf |")
        lines.append("|---|---|---|---|---:|")
        for t in tr_sorted:
            lines.append(
                f"| {t.get('chunk_id','')} | "
                f"{t.get('subject_entity','')} ({t.get('subject_label','')}) | "
                f"{t.get('verb_relation','')} | "
                f"{t.get('object_entity','')} ({t.get('object_label','')}) | "
                f"{t.get('confidence',0):.2f} |"
            )
        lines.append("")

    lines.append("## Manual Validation Checklist\n")
    lines.append("Untuk tiap EVENT/triplet, manual review:")
    lines.append("- [ ] Apakah subject/object benar-benar named entity (bukan kata ganti)?")
    lines.append("- [ ] Apakah verb describe peristiwa historis (bukan internal/cognitive)?")
    lines.append("- [ ] Apakah context_text mendukung claim?")
    lines.append("- [ ] Apakah duplikasi dengan edges_v2.csv yang sudah ada (cek INVOLVED_IN)?")
    lines.append("- [ ] Apakah label_aksi cukup spesifik buat jadi EVENT entity?\n")

    lines.append("## Catatan POC\n")
    lines.append("- Sample N=10 hybrid (5 phase + 5 Badr depth). Bukan random sample.")
    lines.append("- Single-prompt batch chat, structured JSON schema. Reproducible via prompt.md.")
    lines.append("- Untuk scale-up: ganti ke API + iterate per chunk supaya context lebih fokus.")
    lines.append("- LLM cenderung over-extract (false positive) — confidence < 0.7 perlu manual filter.")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {SUMMARY_MD}")

    print("\n" + "=" * 60)
    print("SELESAI — review summary md untuk hasil")
    print("=" * 60)


def main():
    p = argparse.ArgumentParser(description="LLM Verb Extraction POC")
    p.add_argument("--mode", choices=["generate", "parse"], required=True,
                   help="generate = build prompt + sample. parse = parse JSON response.")
    args = p.parse_args()
    if args.mode == "generate":
        cmd_generate()
    else:
        cmd_parse()


if __name__ == "__main__":
    main()
