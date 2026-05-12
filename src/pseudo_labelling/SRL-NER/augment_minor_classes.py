"""
augment_minor_classes.py
========================
Sentence-based augmentation untuk **kelas minoritas** (EVENT, I-LOCATION) di train.csv.

Strategi: **Mention Replacement** (Dai & Adel, COLING 2020).

Algoritma:
  1. Parse train.csv → grouping per kalimat (text_id).
  2. Identifikasi entity spans (B-X / I-X) per kalimat.
  3. Bangun entity pool global per tipe: PERSON, LOCATION, TIME, EVENT.
  4. Tandai "minor sentences" — kalimat yang mengandung B-EVENT, I-EVENT, atau I-LOCATION.
     (Distribusi label paling minoritas di Sirah berdasarkan §1.2 srl_ner_skenario.md.)
  5. Untuk tiap minor sentence × N_AUGMENT variant:
       - Untuk tiap entity dalam kalimat, dengan probabilitas REPLACE_PROB
         substitute mention dengan entity sekelas dari pool (random).
       - Reassign id token & label BIO sesuai mention pengganti.
  6. Append augmented sentences ke training data dengan text_id baru
     `<original>-aug<k>` (k=1..N).
  7. Tulis output → train_augmented.csv (format identik dengan train.csv).

Output sampingan (untuk QA manual):
  - augmentation_log.json  — stats per minor type, daftar text_id augmented
  - sample_augmented.txt   — 20 pasang (original, augmented) untuk review semantic drift

Idempotent. Usage:
  python augment_minor_classes.py
  python augment_minor_classes.py --n-augment 3 --replace-prob 0.6 --seed 7

Default:
  N_AUGMENT     = 2     # variant per minor sentence
  REPLACE_PROB  = 0.7   # prob substitute tiap entity (regardless of type)
  RANDOM_SEED   = 42
  MINOR_LABELS  = {"B-EVENT", "I-EVENT", "I-LOCATION"}
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]   # ...\TA_sirah
DATA_DIR = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER"
INPUT_CSV = DATA_DIR / "train.csv"
OUTPUT_CSV = DATA_DIR / "train_augmented.csv"
LOG_JSON = DATA_DIR / "augmentation_log.json"
SAMPLE_TXT = DATA_DIR / "sample_augmented.txt"

ENTITY_TYPES = ("PERSON", "LOCATION", "TIME", "EVENT")
MINOR_LABELS = frozenset({"B-EVENT", "I-EVENT", "I-LOCATION"})


# ────────────────────────────────────────────────────────────────────────────
# Entity span extraction (BIO decoding)
# ────────────────────────────────────────────────────────────────────────────
def extract_spans(labels: list[str]) -> list[tuple[int, int, str]]:
    """
    Decode label BIO → list of (start_idx, end_idx_exclusive, entity_type).
    Catatan: I-X tanpa B-X sebelumnya tetap di-treat sebagai start of X (toleran).
    """
    spans: list[tuple[int, int, str]] = []
    i = 0
    n = len(labels)
    while i < n:
        lab = labels[i]
        if lab == "O" or lab is None or (isinstance(lab, float)):
            i += 1
            continue
        if "-" not in lab:
            i += 1
            continue
        _prefix, etype = lab.split("-", 1)
        j = i + 1
        while j < n and labels[j] == f"I-{etype}":
            j += 1
        spans.append((i, j, etype))
        i = j
    return spans


# ────────────────────────────────────────────────────────────────────────────
# Sentence representation
# ────────────────────────────────────────────────────────────────────────────
class Sentence:
    __slots__ = ("text_id", "tokens", "labels", "pos_tags")

    def __init__(self, text_id: str, tokens: list[str], labels: list[str], pos_tags: list[str]):
        self.text_id = text_id
        self.tokens = tokens
        self.labels = labels
        self.pos_tags = pos_tags

    def has_minor(self) -> bool:
        return any(lab in MINOR_LABELS for lab in self.labels)

    def spans(self) -> list[tuple[int, int, str]]:
        return extract_spans(self.labels)


def load_sentences(csv_path: Path) -> list[Sentence]:
    df = pd.read_csv(csv_path)
    df["token"] = df["token"].fillna("nan").astype(str)
    df["label"] = df["label"].fillna("O").astype(str)
    df["pos_tag"] = df["pos_tag"].fillna("NN").astype(str)

    sentences = []
    for tid, sub in df.groupby("text_id", sort=False):
        sub = sub.sort_values("id")
        sentences.append(Sentence(
            text_id=str(tid),
            tokens=sub["token"].tolist(),
            labels=sub["label"].tolist(),
            pos_tags=sub["pos_tag"].tolist(),
        ))
    return sentences


def build_entity_pool(sentences: Iterable[Sentence]) -> dict[str, list[list[str]]]:
    """Pool: dict[type → list of mentions, masing-masing = list of tokens]."""
    pool: dict[str, list[list[str]]] = {t: [] for t in ENTITY_TYPES}
    seen: dict[str, set[str]] = {t: set() for t in ENTITY_TYPES}
    for sent in sentences:
        for (s, e, etype) in sent.spans():
            mention = tuple(sent.tokens[s:e])
            key = " ".join(mention).lower()
            if etype in pool and key not in seen[etype]:
                pool[etype].append(list(mention))
                seen[etype].add(key)
    return pool


# ────────────────────────────────────────────────────────────────────────────
# Augmentation
# ────────────────────────────────────────────────────────────────────────────
def augment_sentence(
    sent: Sentence,
    pool: dict[str, list[list[str]]],
    *,
    replace_prob: float,
    rng: random.Random,
) -> tuple[list[str], list[str], list[str], int]:
    """
    Generate satu variant augmented dari `sent`.

    Returns
    -------
    (new_tokens, new_labels, new_pos_tags, n_replacements)
    """
    spans = sent.spans()
    new_tokens: list[str] = []
    new_labels: list[str] = []
    new_pos: list[str] = []

    n_replacements = 0
    i = 0
    span_iter = iter(spans)
    next_span = next(span_iter, None)

    while i < len(sent.tokens):
        if next_span is not None and i == next_span[0]:
            s, e, etype = next_span
            original_mention = sent.tokens[s:e]
            do_replace = (
                etype in pool
                and len(pool[etype]) > 1                   # ada alternatif lain
                and rng.random() < replace_prob
            )
            if do_replace:
                # pilih mention pengganti yang BEDA dari original (case-insensitive)
                orig_key = " ".join(original_mention).lower()
                candidates = [m for m in pool[etype] if " ".join(m).lower() != orig_key]
                if not candidates:
                    candidates = pool[etype]
                replacement = rng.choice(candidates)
                # build BIO labels: B-X, I-X, I-X, ...
                rep_labels = [f"B-{etype}"] + [f"I-{etype}"] * (len(replacement) - 1)
                # pos_tag: reuse first POS dari original (semua entity di Sirah pakai "NN" anyway)
                rep_pos = [sent.pos_tags[s]] * len(replacement)
                new_tokens.extend(replacement)
                new_labels.extend(rep_labels)
                new_pos.extend(rep_pos)
                n_replacements += 1
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

    return new_tokens, new_labels, new_pos, n_replacements


def render_sentence(tokens: list[str], labels: list[str]) -> str:
    """Pretty-print: 'Pada/O bulan/B-TIME Dzul/I-TIME ...'."""
    return " ".join(f"{t}/{l}" for t, l in zip(tokens, labels))


# ────────────────────────────────────────────────────────────────────────────
# Main pipeline
# ────────────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Sentence augmentation untuk kelas minoritas SRL-NER Sirah")
    p.add_argument("--n-augment", type=int, default=2, help="Variant per minor sentence (default: 2)")
    p.add_argument("--replace-prob", type=float, default=0.7,
                   help="Probabilitas substitute tiap entity (default: 0.7)")
    p.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    p.add_argument("--input", type=Path, default=INPUT_CSV)
    p.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = p.parse_args()

    rng = random.Random(args.seed)

    print(f"[load] {args.input}")
    sentences = load_sentences(args.input)
    print(f"  total kalimat: {len(sentences)}")

    pool = build_entity_pool(sentences)
    print("[pool] entity pool sizes (unique mentions):")
    for etype, mentions in pool.items():
        print(f"  {etype:<10} {len(mentions):>5}")

    minor_sents = [s for s in sentences if s.has_minor()]
    print(f"\n[minor] {len(minor_sents)} / {len(sentences)} kalimat mengandung label minor "
          f"({sorted(MINOR_LABELS)})")

    # Label distribution sebelum
    pre_dist = Counter(lab for s in sentences for lab in s.labels)
    print("\n[pre-augment] distribusi label train:")
    for lab, cnt in pre_dist.most_common():
        pct = 100 * cnt / sum(pre_dist.values())
        marker = "  *" if lab in MINOR_LABELS else ""
        print(f"  {lab:<14} {cnt:>7}  {pct:>5.2f}%{marker}")

    # Generate augmented sentences
    augmented: list[Sentence] = []
    replacements_per_variant: list[int] = []
    augmented_text_ids: list[str] = []
    samples_for_review: list[tuple[Sentence, Sentence]] = []

    for sent in minor_sents:
        for k in range(1, args.n_augment + 1):
            new_tokens, new_labels, new_pos, n_repl = augment_sentence(
                sent, pool, replace_prob=args.replace_prob, rng=rng,
            )
            new_tid = f"{sent.text_id}-aug{k}"
            aug_sent = Sentence(new_tid, new_tokens, new_labels, new_pos)
            augmented.append(aug_sent)
            augmented_text_ids.append(new_tid)
            replacements_per_variant.append(n_repl)
            if len(samples_for_review) < 20 and n_repl > 0 and k == 1:
                samples_for_review.append((sent, aug_sent))

    print(f"\n[augment] generated {len(augmented)} kalimat ({args.n_augment} variant × {len(minor_sents)} minor)")
    print(f"  mean replacements per variant : {sum(replacements_per_variant)/max(1,len(replacements_per_variant)):.2f}")
    print(f"  min / max replacements         : "
          f"{min(replacements_per_variant) if replacements_per_variant else 0} / "
          f"{max(replacements_per_variant) if replacements_per_variant else 0}")

    # Combine original + augmented, output ke CSV
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
    print(f"  total token : {len(out_df)} ({len(out_df) - sum(len(s.tokens) for s in sentences)} dari augmentasi)")

    # Post-augment distribution
    post_dist = Counter(out_df["label"].tolist())
    print("\n[post-augment] distribusi label train_augmented:")
    for lab, cnt in post_dist.most_common():
        pct = 100 * cnt / sum(post_dist.values())
        delta = cnt - pre_dist.get(lab, 0)
        marker = "  *" if lab in MINOR_LABELS else ""
        print(f"  {lab:<14} {cnt:>7}  {pct:>5.2f}%  (+{delta}){marker}")

    # Log JSON
    log = {
        "input": str(args.input),
        "output": str(args.output),
        "config": {
            "n_augment": args.n_augment,
            "replace_prob": args.replace_prob,
            "seed": args.seed,
            "minor_labels": sorted(MINOR_LABELS),
        },
        "stats": {
            "original_sentences": len(sentences),
            "minor_sentences": len(minor_sents),
            "augmented_sentences": len(augmented),
            "original_tokens": sum(len(s.tokens) for s in sentences),
            "augmented_tokens": sum(len(s.tokens) for s in augmented),
            "mean_replacements_per_variant": (
                sum(replacements_per_variant) / max(1, len(replacements_per_variant))
            ),
        },
        "pool_sizes": {t: len(pool[t]) for t in ENTITY_TYPES},
        "pre_augment_label_distribution": dict(pre_dist),
        "post_augment_label_distribution": dict(post_dist),
        "augmented_text_ids": augmented_text_ids[:50],   # preview first 50
    }
    LOG_JSON.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[log]   {LOG_JSON}")

    # Sample for manual review
    lines = [
        "# Sample Augmented Sentences — Manual Review",
        f"# config: n_augment={args.n_augment}, replace_prob={args.replace_prob}, seed={args.seed}",
        f"# {len(samples_for_review)} samples (first variant only, where any replacement happened)",
        "",
    ]
    for i, (orig, aug) in enumerate(samples_for_review, 1):
        lines.append(f"=== Sample {i} ===")
        lines.append(f"[ORIG  {orig.text_id}]  " + render_sentence(orig.tokens, orig.labels))
        lines.append(f"[AUG   {aug.text_id}]  "  + render_sentence(aug.tokens, aug.labels))
        lines.append("")
    SAMPLE_TXT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[sample] {SAMPLE_TXT}")


if __name__ == "__main__":
    main()
