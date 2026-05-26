"""
augment_minor_classes_v2.py
===========================
Sentence-based augmentation untuk kelas minoritas (EVENT, I-LOCATION) di train.csv,
versi **v2 dengan period-aware filtering + blacklist + Quran/hadits guard**.

Latar belakang revisi (2026-05-22):
v1 (`augment_minor_classes.py`) random-swap entity dari pool global tanpa constraint
historis. Validasi manual 20 sample → 85% rusak signifikan (anakronistik massal,
Nabi diganti sahabat, ayat Quran dimodifikasi, dll.). Detail di docs review.

Perbaikan v2:
  1. Period-aware pool      — entity hanya di-swap dengan entity dari period yang sama
                               (PERSON/LOCATION strict; EVENT dengan adjacent ±1/±2
                               fallback karena pool EVENT per-period sangat sparse).
  2. Blacklist replacement  — para Nabi, malaikat, narator/ulama klasik, dan tokoh
                               musuh kunci tidak boleh dipilih sebagai pengganti
                               random.
  3. Quran/hadits guard     — kalimat yang punya pattern `(Surah: ayat)` atau quote
                               panjang di-skip total (tidak di-augment).
  4. Pool sanitization      — strip leading/trailing punctuation (`?"`, `."`, `,`,
                               `(`, `)`, dst). Drop mention 0-length atau hanya
                               punctuation.

Output sampingan:
  - augmentation_log_v2.json   — stats lengkap + diagnostik per filter
  - sample_augmented_v2.txt    — 30 sample untuk re-validasi manual

Idempotent. Usage:
  python augment_minor_classes_v2.py
  python augment_minor_classes_v2.py --n-augment 3 --replace-prob 0.6 --seed 7
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
CHUNKS_CSV = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
PERIOD_JSON = ROOT / "data" / "result" / "relation_result" / "period_mapping.json"

INPUT_CSV = DATA_DIR / "train.csv"
OUTPUT_CSV = DATA_DIR / "train_augmented_v2.csv"
LOG_JSON = DATA_DIR / "augmentation_log_v2.json"
SAMPLE_TXT = DATA_DIR / "sample_augmented_v2.txt"

ENTITY_TYPES = ("PERSON", "LOCATION", "TIME", "EVENT")
MINOR_LABELS = frozenset({"B-EVENT", "I-EVENT", "I-LOCATION"})

# Known broken EVENT mentions yang muncul di train.csv karena OCR/preprocessing artefak
# (mis. "Bu'ats" terpecah jadi token "Bu"/I-EVENT + "ats,"/O → span jadi "Perang Bu").
# Drop dari pool. Match by normalized lower-case.
EVENT_KNOWN_BROKEN = frozenset({
    "perang bu",
})

# Punctuation pattern untuk sanitization mention pool
PUNCT_STRIP = re.compile(r'^[\(\["\'\s]+|[\)\]"\'.,!?:;\s]+$')

# Quran reference pattern: `(Al-A'raf: 31)`, `(Al-Baqarah:189)`, etc.
QURAN_REF_PATTERN = re.compile(r"\([A-Za-z'’‘-]+\s*:\s*\d+\)")

# Blacklist normalized lowercase — entity di set ini tidak boleh jadi target
# replacement (tetap muncul di kalimat asli, hanya tidak di-pick sebagai pengganti).
BLACKLIST_REPLACEMENT = frozenset({
    # Para Nabi
    "adam", "nuh", "ibrahim", "ibrahim x", "musa", "musa bin imran",
    "isa", "isa bin maryam", "harun", "harun bin imran", "idris",
    "yusuf", "yahya", "yahya bin zakaria", "zakaria", "yunus",
    "yunus bin matta", "sulaiman", "daud", "ya'qub", "yaqub",
    "ishaq", "isma'il", "ismail", "ayyub", "syu'aib", "syuaib",
    "luth", "hud", "shalih", "ilyas", "ilyasa", "dzulkifli",
    # Malaikat
    "jibril", "mikail", "israfil", "izrail",
    # Narator/Sumber & Ulama klasik (jangan ditukar dengan sahabat random)
    "aisyah", "khadijah",
    "ath-thabari", "al-qurthubi", "ibnu hisyam", "ibnul qayyim",
    "an-nawawi", "ibnu hajar", "ibnu ishaq", "ibnul musayyab",
    "sa'id bin al-musayyab",
    # Tokoh musuh kunci (jangan dijadikan target — sering cause role-swap historically wrong)
    "amr bin luhay", "abu lahab", "abu jahal",
    "uqbah bin abu mu'ith", "uqbah bin abu mu'aith",
    "zam'ah bin al-aswad",
    # Rasulullah & sebutan langsung (jangan diganti acak)
    "muhammad", "rasulullah", "nabi", "nabi saw",
})


# ────────────────────────────────────────────────────────────────────────────
# Utility
# ────────────────────────────────────────────────────────────────────────────
def normalize_mention(m: str) -> str:
    """Strip surrounding punctuation, lower-case. Untuk dedup pool & blacklist match."""
    cleaned = PUNCT_STRIP.sub('', m).strip()
    return cleaned.lower()


def sanitize_tokens(tokens: list[str]) -> list[str]:
    """Strip surrounding punctuation dari tiap token (in-place safe). Drop empty."""
    out = []
    for tok in tokens:
        cleaned = PUNCT_STRIP.sub('', tok).strip()
        if cleaned:
            out.append(cleaned)
    return out


def extract_spans(labels: list[str]) -> list[tuple[int, int, str]]:
    """Decode BIO → list of (start, end_exclusive, etype). I-X tanpa B-X dianggap B-X."""
    spans: list[tuple[int, int, str]] = []
    i = 0
    n = len(labels)
    while i < n:
        lab = labels[i]
        if not lab or lab == "O" or "-" not in lab:
            i += 1
            continue
        _, etype = lab.split("-", 1)
        j = i + 1
        while j < n and labels[j] == f"I-{etype}":
            j += 1
        spans.append((i, j, etype))
        i = j
    return spans


# ────────────────────────────────────────────────────────────────────────────
# Period mapping
# ────────────────────────────────────────────────────────────────────────────
def load_period_mapping() -> tuple[dict[str, str], list[str]]:
    """
    Returns
    -------
    text_id_to_period : dict[chunk_id, period_id]
    period_order      : list of period_ids in narrative order (P0, P1, ..., P14)
    """
    chunks = pd.read_csv(CHUNKS_CSV, sep=";", encoding="utf-8-sig")
    chunks["first_page"] = chunks["halaman"].astype(str).str.extract(r"^(\d+)").astype(float)

    with open(PERIOD_JSON, encoding="utf-8") as f:
        periods = json.load(f)
    period_order = [p["period_id"] for p in periods]

    text_id_to_period: dict[str, str] = {}
    for _, row in chunks.iterrows():
        if pd.isna(row["first_page"]):
            continue
        page = int(row["first_page"])
        for period in periods:
            if period["page_start"] <= page <= period["page_end"]:
                text_id_to_period[row["chunk_id"]] = period["period_id"]
                break

    return text_id_to_period, period_order


# ────────────────────────────────────────────────────────────────────────────
# Sentence representation
# ────────────────────────────────────────────────────────────────────────────
class Sentence:
    __slots__ = ("text_id", "tokens", "labels", "pos_tags", "period")

    def __init__(self, text_id: str, tokens: list[str], labels: list[str],
                 pos_tags: list[str], period: str | None):
        self.text_id = text_id
        self.tokens = tokens
        self.labels = labels
        self.pos_tags = pos_tags
        self.period = period

    def has_minor(self) -> bool:
        return any(lab in MINOR_LABELS for lab in self.labels)

    def spans(self) -> list[tuple[int, int, str]]:
        return extract_spans(self.labels)


def load_sentences(csv_path: Path, text_id_to_period: dict[str, str]) -> list[Sentence]:
    df = pd.read_csv(csv_path)
    df["token"] = df["token"].fillna("nan").astype(str)
    df["label"] = df["label"].fillna("O").astype(str)
    df["pos_tag"] = df["pos_tag"].fillna("NN").astype(str)

    sentences = []
    for tid, sub in df.groupby("text_id", sort=False):
        sub = sub.sort_values("id")
        tid_str = str(tid)
        sentences.append(Sentence(
            text_id=tid_str,
            tokens=sub["token"].tolist(),
            labels=sub["label"].tolist(),
            pos_tags=sub["pos_tag"].tolist(),
            period=text_id_to_period.get(tid_str),
        ))
    return sentences


# ────────────────────────────────────────────────────────────────────────────
# Pool building (period-aware + sanitized + blacklist filter)
# ────────────────────────────────────────────────────────────────────────────
def build_period_pool(
    sentences: Iterable[Sentence],
) -> tuple[dict[str, dict[str, list[list[str]]]], dict[str, int]]:
    """
    Build pool[period][etype] = list of mentions (each = list of tokens, sanitized).

    Returns
    -------
    pool       : nested dict
    diag       : diagnostics counter
    """
    pool: dict[str, dict[str, list[list[str]]]] = defaultdict(
        lambda: {t: [] for t in ENTITY_TYPES}
    )
    seen: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {t: set() for t in ENTITY_TYPES}
    )
    diag = Counter()

    for sent in sentences:
        if sent.period is None:
            diag["sentences_no_period"] += 1
            continue
        for (s, e, etype) in sent.spans():
            if etype not in ENTITY_TYPES:
                continue
            raw_mention = sent.tokens[s:e]
            sanitized = sanitize_tokens(raw_mention)
            if not sanitized:
                diag["pool_dropped_empty_after_sanitize"] += 1
                continue
            normalized = " ".join(sanitized).lower()
            if not normalized:
                diag["pool_dropped_empty_after_sanitize"] += 1
                continue
            if etype == "PERSON" and normalized in BLACKLIST_REPLACEMENT:
                diag["pool_blacklisted_person"] += 1
                continue
            if etype == "EVENT" and normalized in EVENT_KNOWN_BROKEN:
                diag["pool_dropped_broken_event"] += 1
                continue
            if normalized in seen[sent.period][etype]:
                continue
            seen[sent.period][etype].add(normalized)
            pool[sent.period][etype].append(sanitized)

    return pool, diag


def get_replacement_pool(
    pool: dict[str, dict[str, list[list[str]]]],
    period: str,
    etype: str,
    period_order: list[str],
    *,
    fallback_for_event: bool = True,
    max_radius: int = 2,
) -> list[list[str]]:
    """
    Untuk EVENT: kalau pool[period][EVENT] < 2 mentions, expand ke ±1 lalu ±2 period.
    Untuk PERSON/LOCATION/TIME: strict period only.
    """
    base = pool.get(period, {}).get(etype, [])
    if etype != "EVENT" or not fallback_for_event:
        return base

    if len(base) >= 2:
        return base

    if period not in period_order:
        return base

    idx = period_order.index(period)
    expanded = list(base)
    seen = {" ".join(m).lower() for m in expanded}

    for radius in range(1, max_radius + 1):
        for offset in (-radius, radius):
            neighbor_idx = idx + offset
            if not (0 <= neighbor_idx < len(period_order)):
                continue
            neighbor_period = period_order[neighbor_idx]
            for m in pool.get(neighbor_period, {}).get(etype, []):
                key = " ".join(m).lower()
                if key not in seen:
                    expanded.append(m)
                    seen.add(key)
        if len(expanded) >= 2:
            return expanded

    return expanded


# ────────────────────────────────────────────────────────────────────────────
# Quran/hadits guard
# ────────────────────────────────────────────────────────────────────────────
def has_quran_reference(tokens: list[str]) -> bool:
    """Check if sentence contains `(Surah: ayat)` pattern."""
    text = " ".join(tokens)
    return bool(QURAN_REF_PATTERN.search(text))


def is_quote_heavy(tokens: list[str], threshold: float = 0.3) -> bool:
    """Heuristic: kalau >threshold% token punya quote char, treat as quotation."""
    if not tokens:
        return False
    quote_tokens = sum(1 for t in tokens if '"' in t or "''" in t or "'" in t)
    return quote_tokens > len(tokens) * threshold


def should_skip_sentence(sent: Sentence) -> tuple[bool, str | None]:
    """Returns (skip?, reason)."""
    if has_quran_reference(sent.tokens):
        return True, "quran_reference"
    if is_quote_heavy(sent.tokens):
        return True, "quote_heavy"
    return False, None


# ────────────────────────────────────────────────────────────────────────────
# Augmentation
# ────────────────────────────────────────────────────────────────────────────
def augment_sentence(
    sent: Sentence,
    pool: dict[str, dict[str, list[list[str]]]],
    period_order: list[str],
    *,
    replace_prob: float,
    rng: random.Random,
) -> tuple[list[str], list[str], list[str], int, dict[str, int]]:
    """
    Generate satu variant augmented dari `sent` dengan period-aware constraint.
    Returns (new_tokens, new_labels, new_pos_tags, n_replacements, diag).
    """
    spans = sent.spans()
    new_tokens: list[str] = []
    new_labels: list[str] = []
    new_pos: list[str] = []
    diag = Counter()

    n_replacements = 0
    i = 0
    span_iter = iter(spans)
    next_span = next(span_iter, None)

    while i < len(sent.tokens):
        if next_span is not None and i == next_span[0]:
            s, e, etype = next_span
            original_mention = sent.tokens[s:e]
            orig_normalized = " ".join(sanitize_tokens(original_mention)).lower()

            do_replace = False
            # Bidirectional blacklist: original mention juga tidak boleh diganti.
            # Para Nabi, malaikat, narator/ulama klasik, tokoh musuh kunci, dan
            # Rasulullah/Muhammad — ketika muncul sebagai original mention,
            # biarkan apa adanya (jangan random-swap).
            is_protected_source = (
                etype == "PERSON" and orig_normalized in BLACKLIST_REPLACEMENT
            )
            is_broken_event = (
                etype == "EVENT" and orig_normalized in EVENT_KNOWN_BROKEN
            )
            if is_protected_source:
                diag[f"protected_source_{etype}"] += 1
            if is_broken_event:
                diag["broken_event_skipped"] += 1

            if etype in ENTITY_TYPES and sent.period is not None \
                    and not is_protected_source and not is_broken_event:
                candidates_pool = get_replacement_pool(pool, sent.period, etype, period_order)
                # Filter: exclude self & exclude blacklist (extra safety meskipun pool sudah di-filter)
                candidates = [
                    m for m in candidates_pool
                    if " ".join(m).lower() != orig_normalized
                    and " ".join(m).lower() not in BLACKLIST_REPLACEMENT
                ]
                if len(candidates) >= 1 and rng.random() < replace_prob:
                    do_replace = True
                else:
                    if len(candidates) == 0:
                        diag[f"pool_empty_{etype}"] += 1

            if do_replace:
                replacement = rng.choice(candidates)
                rep_labels = [f"B-{etype}"] + [f"I-{etype}"] * (len(replacement) - 1)
                rep_pos = [sent.pos_tags[s]] * len(replacement)
                new_tokens.extend(replacement)
                new_labels.extend(rep_labels)
                new_pos.extend(rep_pos)
                n_replacements += 1
                diag[f"replaced_{etype}"] += 1
            else:
                new_tokens.extend(original_mention)
                new_labels.extend(sent.labels[s:e])
                new_pos.extend(sent.pos_tags[s:e])
            i = e
            next_span = next(span_iter, None)
        else:
            new_tokens.append(sent.tokens[i])
            new_labels.append(sent.labels[i])
            new_pos.append(sent.pos_tags[i])
            i += 1

    return new_tokens, new_labels, new_pos, n_replacements, dict(diag)


def render_sentence(tokens: list[str], labels: list[str]) -> str:
    return " ".join(f"{t}/{l}" for t, l in zip(tokens, labels))


# ────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ────────────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Augmentation v2 (period-aware) untuk SRL-NER Sirah")
    p.add_argument("--n-augment", type=int, default=2)
    p.add_argument("--replace-prob", type=float, default=0.7)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--input", type=Path, default=INPUT_CSV)
    p.add_argument("--output", type=Path, default=OUTPUT_CSV)
    p.add_argument("--n-samples", type=int, default=30, help="Jumlah sample untuk QA manual")
    args = p.parse_args()

    rng = random.Random(args.seed)

    print("[load] period mapping")
    text_id_to_period, period_order = load_period_mapping()
    print(f"  period order      : {period_order}")
    print(f"  chunks -> period  : {len(text_id_to_period)}")

    print(f"\n[load] {args.input}")
    sentences = load_sentences(args.input, text_id_to_period)
    print(f"  total kalimat     : {len(sentences)}")

    n_with_period = sum(1 for s in sentences if s.period is not None)
    print(f"  with period assign: {n_with_period}")
    print(f"  no period         : {len(sentences) - n_with_period}")

    pool, pool_diag = build_period_pool(sentences)
    print("\n[pool] entity pool sizes per period:")
    print(f"  {'period':<8}", end="")
    for etype in ENTITY_TYPES:
        print(f"{etype:>10}", end="")
    print()
    for period in period_order:
        if period not in pool:
            continue
        print(f"  {period:<8}", end="")
        for etype in ENTITY_TYPES:
            print(f"{len(pool[period][etype]):>10}", end="")
        print()
    print(f"  diag: {dict(pool_diag)}")

    minor_sents = [s for s in sentences if s.has_minor()]
    print(f"\n[minor] {len(minor_sents)} / {len(sentences)} kalimat mengandung label minor")

    # Filter Quran/hadits-guarded sentences
    augmentable = []
    skip_reasons = Counter()
    for s in minor_sents:
        if s.period is None:
            skip_reasons["no_period"] += 1
            continue
        skip, reason = should_skip_sentence(s)
        if skip:
            skip_reasons[reason] += 1
            continue
        augmentable.append(s)
    print(f"\n[filter] augmentable kalimat       : {len(augmentable)}")
    for reason, n in skip_reasons.most_common():
        print(f"  skipped — {reason:<20} {n}")

    pre_dist = Counter(lab for s in sentences for lab in s.labels)
    print("\n[pre-augment] distribusi label train:")
    for lab, cnt in pre_dist.most_common():
        marker = "  *" if lab in MINOR_LABELS else ""
        print(f"  {lab:<14} {cnt:>7}{marker}")

    # Generate augmented
    augmented: list[Sentence] = []
    augmented_text_ids: list[str] = []
    replacements_per_variant: list[int] = []
    aug_diag_total = Counter()
    samples_for_review: list[tuple[Sentence, Sentence]] = []

    for sent in augmentable:
        for k in range(1, args.n_augment + 1):
            new_tokens, new_labels, new_pos, n_repl, diag = augment_sentence(
                sent, pool, period_order,
                replace_prob=args.replace_prob, rng=rng,
            )
            new_tid = f"{sent.text_id}-aug{k}"
            aug_sent = Sentence(new_tid, new_tokens, new_labels, new_pos, sent.period)
            augmented.append(aug_sent)
            augmented_text_ids.append(new_tid)
            replacements_per_variant.append(n_repl)
            aug_diag_total.update(diag)
            if len(samples_for_review) < args.n_samples and n_repl > 0 and k == 1:
                samples_for_review.append((sent, aug_sent))

    print(f"\n[augment] generated {len(augmented)} kalimat")
    if replacements_per_variant:
        print(f"  mean repl/variant : {sum(replacements_per_variant)/len(replacements_per_variant):.2f}")
        print(f"  min / max         : {min(replacements_per_variant)} / {max(replacements_per_variant)}")
    print(f"  per-type stats    : {dict(aug_diag_total)}")

    rows = []
    for sent in sentences + augmented:
        for idx, (tok, lab, pos) in enumerate(zip(sent.tokens, sent.labels, sent.pos_tags), start=1):
            rows.append({
                "text_id": sent.text_id,
                "id": f"{sent.text_id}.{idx:03d}",
                "token": tok,
                "pos_tag": pos,
                "label": lab,
            })
    out_df = pd.DataFrame(rows, columns=["text_id", "id", "token", "pos_tag", "label"])
    out_df.to_csv(args.output, index=False)
    print(f"\n[write] {args.output}")
    print(f"  total token : {len(out_df)}")

    post_dist = Counter(out_df["label"].tolist())
    print("\n[post-augment] distribusi label train_augmented_v2:")
    for lab, cnt in post_dist.most_common():
        delta = cnt - pre_dist.get(lab, 0)
        marker = "  *" if lab in MINOR_LABELS else ""
        print(f"  {lab:<14} {cnt:>7}  (+{delta}){marker}")

    log = {
        "input": str(args.input),
        "output": str(args.output),
        "config": {
            "n_augment": args.n_augment,
            "replace_prob": args.replace_prob,
            "seed": args.seed,
            "minor_labels": sorted(MINOR_LABELS),
            "blacklist_size": len(BLACKLIST_REPLACEMENT),
            "fallback_for_event_radius": 2,
        },
        "stats": {
            "original_sentences": len(sentences),
            "minor_sentences": len(minor_sents),
            "augmentable_sentences": len(augmentable),
            "augmented_sentences": len(augmented),
            "original_tokens": sum(len(s.tokens) for s in sentences),
            "augmented_tokens": sum(len(s.tokens) for s in augmented),
            "mean_replacements_per_variant": (
                sum(replacements_per_variant) / max(1, len(replacements_per_variant))
            ),
        },
        "skip_reasons": dict(skip_reasons),
        "pool_diagnostics": dict(pool_diag),
        "augmentation_diagnostics": dict(aug_diag_total),
        "pool_sizes_per_period": {
            period: {etype: len(pool[period][etype]) for etype in ENTITY_TYPES}
            for period in period_order if period in pool
        },
        "pre_augment_label_distribution": dict(pre_dist),
        "post_augment_label_distribution": dict(post_dist),
        "augmented_text_ids": augmented_text_ids[:50],
    }
    LOG_JSON.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[log]   {LOG_JSON}")

    lines = [
        "# Sample Augmented Sentences v2 — Manual Review",
        f"# config: n_augment={args.n_augment}, replace_prob={args.replace_prob}, "
        f"seed={args.seed}, period_aware=True, blacklist=enabled, quran_guard=enabled",
        f"# {len(samples_for_review)} samples (first variant only, where any replacement happened)",
        "",
    ]
    for i, (orig, aug) in enumerate(samples_for_review, 1):
        lines.append(f"=== Sample {i} (period={orig.period}) ===")
        lines.append(f"[ORIG  {orig.text_id}]  " + render_sentence(orig.tokens, orig.labels))
        lines.append(f"[AUG   {aug.text_id}]  "  + render_sentence(aug.tokens, aug.labels))
        lines.append("")
    SAMPLE_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[sample] {SAMPLE_TXT}")


if __name__ == "__main__":
    main()
