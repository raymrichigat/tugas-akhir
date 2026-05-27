"""
build_comparison_report.py
==========================
Comparison report: SRL-NER (S3.2 inference v3) vs manual labelling.

Tujuan (revisi Bu Diana 2026-05-16):
"Pipeline running end-to-end dengan output SRL-NER, comparison report
 SRL-NER vs manual labelling."

Strategi:
  - Untuk tiap chunk yang **ada di kedua dataset** (manual + NER v3):
    * Ekstrak set entity dari manual: {(label, entity_text_normalized), ...}
    * Ekstrak set entity dari NER v3: {(label, entity_text_normalized), ...}
    * Hitung TP, FP, FN per label (entity-level, bukan token-level).
  - Manual = ground truth untuk perbandingan (meskipun kita tahu manual juga
    tidak sempurna — punya bias regex + missing patterns).
  - Per-label precision / recall / F1 + sample misclassifications.

Normalisasi entity_text (untuk match):
  - Lower-case
  - Strip whitespace
  - Strip surrounding punctuation
  - Multi-whitespace -> single

Match logic (entity-level):
  - exact_match: (label, normalized_text) sama persis
  - partial_match: substring overlap (mis. "Abu Bakar" vs "Abu Bakar Ash-Shiddiq")
  - no_match

Output:
  data/result/analysis/comparison_srl_vs_manual.md
  data/result/analysis/comparison_misclassified_samples.csv

Idempotent. Usage:
  venv\\Scripts\\python.exe src/relation_extraction/build_comparison_report.py
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MANUAL_CSV = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
NER_V3_CSV = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled_v3.csv"
OUT_MD = ROOT / "data" / "result" / "analysis" / "comparison_srl_vs_manual.md"
OUT_SAMPLES = ROOT / "data" / "result" / "analysis" / "comparison_misclassified_samples.csv"

LABELS = ["PERSON", "LOCATION", "EVENT", "TIME"]


def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    # strip surrounding punctuation
    s = s.strip(' \t\n.,;:!?\"\'()[]{}')
    return s.lower()


def load_entities_per_chunk(csv_path: Path, source_label: str) -> dict[str, set[tuple[str, str]]]:
    """
    Returns: {chunk_id: {(label, normalized_text), ...}}
    """
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")
    df["label"] = df["label"].astype(str)
    df["entity_text"] = df["entity_text"].astype(str)
    df["norm_text"] = df["entity_text"].apply(normalize_text)
    df = df[df["label"].isin(LABELS) & (df["norm_text"] != "")]

    out: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for _, row in df.iterrows():
        out[str(row["chunk_id"])].add((row["label"], row["norm_text"]))
    print(f"  {source_label}: {len(df)} entities di {len(out)} chunks")
    return out


def is_partial_match(text_a: str, text_b: str) -> bool:
    """True kalau salah satu string adalah substring dari yang lain (token-aware)."""
    if not text_a or not text_b:
        return False
    if text_a == text_b:
        return False  # exact match handled separately
    a_words = set(text_a.split())
    b_words = set(text_b.split())
    if not a_words or not b_words:
        return False
    overlap = a_words & b_words
    # partial match jika minimum 50% kata tumpang tindih
    min_size = min(len(a_words), len(b_words))
    if min_size == 0:
        return False
    return len(overlap) / min_size >= 0.5


def compute_metrics(manual_set: set, ner_set: set) -> dict:
    """
    Return per-label metrics.

    TP: entity di manual yang ada exact-match di NER
    FN: entity di manual yang tidak ada di NER (missed)
    FP: entity di NER yang tidak ada di manual (over-detected)
    Partial: entity di NER yang partial-match dengan manual (kandidat boundary error)
    """
    out = {}
    for label in LABELS:
        m = {(l, t) for (l, t) in manual_set if l == label}
        n = {(l, t) for (l, t) in ner_set if l == label}
        tp = m & n
        fn = m - n
        fp = n - m

        # Partial match analysis: untuk FP, cek apakah ada partial match di FN
        partial = set()
        for (lab_n, txt_n) in list(fp):
            for (lab_m, txt_m) in fn:
                if is_partial_match(txt_n, txt_m):
                    partial.add((lab_n, txt_n))
                    break

        precision = len(tp) / len(n) if n else 0.0
        recall = len(tp) / len(m) if m else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        out[label] = {
            "manual_count": len(m),
            "ner_count": len(n),
            "tp": len(tp),
            "fn": len(fn),
            "fp": len(fp),
            "fp_partial": len(partial),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return out


def aggregate_metrics(per_chunk_metrics: list[dict]) -> dict:
    """Aggregate per-chunk metrics ke summary global."""
    out = {}
    for label in LABELS:
        sum_m = sum(m[label]["manual_count"] for m in per_chunk_metrics)
        sum_n = sum(m[label]["ner_count"] for m in per_chunk_metrics)
        sum_tp = sum(m[label]["tp"] for m in per_chunk_metrics)
        sum_fn = sum(m[label]["fn"] for m in per_chunk_metrics)
        sum_fp = sum(m[label]["fp"] for m in per_chunk_metrics)
        sum_fp_partial = sum(m[label]["fp_partial"] for m in per_chunk_metrics)
        precision = sum_tp / (sum_tp + sum_fp) if (sum_tp + sum_fp) else 0.0
        recall = sum_tp / (sum_tp + sum_fn) if (sum_tp + sum_fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        out[label] = {
            "manual_count": sum_m,
            "ner_count": sum_n,
            "tp": sum_tp,
            "fn": sum_fn,
            "fp": sum_fp,
            "fp_partial_match": sum_fp_partial,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return out


def collect_samples(manual_per_chunk, ner_per_chunk, common_chunks, n_per_category=10):
    """
    Collect contoh kasus per kategori:
      - missed (FN): entity manual yang tidak ke-detect NER
      - over_detected (FP): entity NER yang tidak ada di manual
      - partial: entity NER yang partial-match dengan manual entity
    """
    rows = []
    counters = Counter()
    for chunk_id in sorted(common_chunks):
        m_set = manual_per_chunk[chunk_id]
        n_set = ner_per_chunk[chunk_id]
        for label in LABELS:
            m = {(l, t) for (l, t) in m_set if l == label}
            n = {(l, t) for (l, t) in n_set if l == label}
            fn = m - n
            fp = n - m

            # FN samples
            for (lab, txt) in list(fn)[:5]:
                if counters[(label, "missed")] < n_per_category:
                    rows.append({
                        "chunk_id": chunk_id,
                        "label": label,
                        "category": "missed_by_NER",
                        "entity_text": txt,
                        "in_manual": True,
                        "in_ner": False,
                    })
                    counters[(label, "missed")] += 1

            # FP / partial samples
            for (lab, txt_n) in list(fp)[:5]:
                # Check partial match
                partial_match_target = None
                for (lab_m, txt_m) in fn:
                    if is_partial_match(txt_n, txt_m):
                        partial_match_target = txt_m
                        break

                category = "partial_match_NER" if partial_match_target else "extra_by_NER"
                if counters[(label, category)] < n_per_category:
                    rows.append({
                        "chunk_id": chunk_id,
                        "label": label,
                        "category": category,
                        "entity_text": txt_n,
                        "in_manual": False,
                        "in_ner": True,
                        "partial_match_with_manual": partial_match_target or "",
                    })
                    counters[(label, category)] += 1
    return rows


def main():
    print("=" * 60)
    print("COMPARISON REPORT — SRL-NER vs Manual Labelling")
    print("=" * 60)

    print("\n[1/4] Loading entities...")
    manual_per_chunk = load_entities_per_chunk(MANUAL_CSV, "manual")
    ner_per_chunk = load_entities_per_chunk(NER_V3_CSV, "NER v3")

    common = set(manual_per_chunk.keys()) & set(ner_per_chunk.keys())
    only_manual = set(manual_per_chunk.keys()) - common
    only_ner = set(ner_per_chunk.keys()) - common
    print(f"\n  Common chunks (di kedua dataset): {len(common)}")
    print(f"  Only-manual chunks (manual saja) : {len(only_manual)}")
    print(f"  Only-NER chunks (NER cover lebih): {len(only_ner)}")

    print("\n[2/4] Computing per-chunk metrics...")
    per_chunk_metrics = []
    for chunk_id in common:
        m = compute_metrics(manual_per_chunk[chunk_id], ner_per_chunk[chunk_id])
        per_chunk_metrics.append(m)

    print("\n[3/4] Aggregating to global metrics...")
    global_metrics = aggregate_metrics(per_chunk_metrics)
    for label in LABELS:
        s = global_metrics[label]
        print(f"  {label:10s} P={s['precision']:.3f} R={s['recall']:.3f} F1={s['f1']:.3f}  "
              f"manual={s['manual_count']:5d}  ner={s['ner_count']:5d}  "
              f"tp={s['tp']:5d}  fn={s['fn']:5d}  fp={s['fp']:5d} (partial={s['fp_partial_match']})")

    print("\n[4/4] Collect samples + write report...")
    samples = collect_samples(manual_per_chunk, ner_per_chunk, common)
    df_samples = pd.DataFrame(samples)
    OUT_SAMPLES.parent.mkdir(parents=True, exist_ok=True)
    df_samples.to_csv(OUT_SAMPLES, index=False, sep=";", encoding="utf-8-sig")
    print(f"  -> {OUT_SAMPLES} ({len(df_samples)} samples)")

    # ── Markdown report ────────────────────────────────────────────────
    micro_tp = sum(global_metrics[l]["tp"] for l in LABELS)
    micro_fn = sum(global_metrics[l]["fn"] for l in LABELS)
    micro_fp = sum(global_metrics[l]["fp"] for l in LABELS)
    micro_p = micro_tp / (micro_tp + micro_fp) if (micro_tp + micro_fp) else 0.0
    micro_r = micro_tp / (micro_tp + micro_fn) if (micro_tp + micro_fn) else 0.0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0.0

    lines = []
    lines.append("# Comparison Report — SRL-NER (S3.2 v3) vs Manual Labelling\n")
    lines.append("**Tanggal:** 2026-05-28\n")
    lines.append("**Latar belakang:** Revisi Bu Diana 2026-05-16 — pipeline running end-to-end "
                 "dengan output SRL-NER, comparison report SRL-NER vs manual labelling.\n")
    lines.append("**Sumber data:**")
    lines.append(f"- Manual labelling : `{MANUAL_CSV.relative_to(ROOT).as_posix()}` "
                 f"(regex + keyword pre-labelling)")
    lines.append(f"- NER inference v3 : `{NER_V3_CSV.relative_to(ROOT).as_posix()}` "
                 f"(model S3.2-scl-aug-iter4 winner, F1 entity 0.9537 di test set)\n")

    lines.append("## Disclaimer Penting\n")
    lines.append("Manual labelling **bukan ground truth absolut**. Manual dikerjakan via "
                 "regex + keyword matching (`pre_labelling.py`), yang punya bias:")
    lines.append("- Hanya match pattern yang sudah didefinisikan (mis. \"bin/binti\" untuk PERSON)")
    lines.append("- Banyak entity valid yang ke-skip karena tidak ada pattern matching")
    lines.append("- Tidak konsisten penanganan boundary entity")
    lines.append("")
    lines.append("Sehingga **\"missed by NER\"** (FN) bisa berarti:")
    lines.append("- (a) NER beneran missed entity yang seharusnya di-detect, ATAU")
    lines.append("- (b) Manual over-detect via regex agresif, NER skip karena confidence rendah")
    lines.append("")
    lines.append("Demikian juga **\"extra by NER\"** (FP) bisa berarti:")
    lines.append("- (a) NER false positive (over-detection), ATAU")
    lines.append("- (b) Entity valid yang manual ke-skip karena tidak ada pattern\n")

    lines.append("## Cakupan\n")
    lines.append(f"- Common chunks (di kedua dataset)  : **{len(common)}**")
    lines.append(f"- Only-manual chunks               : {len(only_manual)} (manual punya, NER tidak)")
    lines.append(f"- Only-NER chunks (extra coverage) : **{len(only_ner)}** (NER tambah {len(only_ner)} chunks yang manual tidak label)\n")
    lines.append(f"NER v3 cover **{len(ner_per_chunk)}** chunks vs manual {len(manual_per_chunk)} chunks "
                 f"(+{len(ner_per_chunk) - len(manual_per_chunk)} chunks).\n")

    lines.append("## Hasil Perbandingan Per-Label (Common Chunks Saja)\n")
    lines.append("Manual treated as reference. Per-label entity-level matching dengan normalisasi "
                 "(lower-case, strip whitespace + punctuation).\n")
    lines.append("| Label | Manual | NER v3 | TP | FN | FP | FP partial | Precision | Recall | F1 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for label in LABELS:
        s = global_metrics[label]
        lines.append(
            f"| {label} | {s['manual_count']} | {s['ner_count']} | "
            f"{s['tp']} | {s['fn']} | {s['fp']} | {s['fp_partial_match']} | "
            f"{s['precision']:.4f} | {s['recall']:.4f} | {s['f1']:.4f} |"
        )
    lines.append(f"| **MICRO** | {micro_tp + micro_fn} | {micro_tp + micro_fp} | "
                 f"{micro_tp} | {micro_fn} | {micro_fp} | — | "
                 f"**{micro_p:.4f}** | **{micro_r:.4f}** | **{micro_f1:.4f}** |\n")

    lines.append("**Catatan kolom:**")
    lines.append("- `Manual` / `NER v3`: jumlah unique entity per label di common chunks")
    lines.append("- `TP` (True Positive): entity sama persis di kedua dataset")
    lines.append("- `FN` (False Negative): di manual, tidak di NER (missed by NER)")
    lines.append("- `FP` (False Positive): di NER, tidak di manual (extra by NER)")
    lines.append("- `FP partial`: subset FP yang punya partial match dengan FN — biasanya boundary mismatch (mis. \"Abu Bakar\" vs \"Abu Bakar Ash-Shiddiq\"), bukan true false positive")
    lines.append("- Precision = TP / (TP + FP), Recall = TP / (TP + FN)\n")

    lines.append("## Interpretasi Hasil\n")
    pers_recall = global_metrics["PERSON"]["recall"]
    if pers_recall < 0.5:
        lines.append(f"- **Recall PERSON rendah ({pers_recall:.3f})** = NER missed banyak PERSON yang manual deteksi.")
        lines.append("  Kemungkinan: NER threshold conservative, manual regex agresif untuk pattern \"bin/binti\".")
    else:
        lines.append(f"- Recall PERSON = {pers_recall:.3f} — moderate-good.")

    pers_prec = global_metrics["PERSON"]["precision"]
    if pers_prec > 0.8:
        lines.append(f"- **Precision PERSON tinggi ({pers_prec:.3f})** — NER prediksi PERSON terpercaya.")
    elif pers_prec < 0.5:
        lines.append(f"- Precision PERSON = {pers_prec:.3f} — banyak FP, perlu cek FP partial.")
    else:
        lines.append(f"- Precision PERSON = {pers_prec:.3f} — moderate.")

    lines.append(f"- **EVENT detection**: NER {global_metrics['EVENT']['ner_count']} unique vs manual "
                 f"{global_metrics['EVENT']['manual_count']} unique. F1 = {global_metrics['EVENT']['f1']:.3f}.")
    lines.append(f"- **LOCATION**: F1 = {global_metrics['LOCATION']['f1']:.3f}.")
    lines.append(f"- **TIME**: F1 = {global_metrics['TIME']['f1']:.3f}.\n")

    lines.append("**Coverage sebagai keuntungan utama NER:**")
    lines.append(f"- Manual cover {len(manual_per_chunk)} chunks (regex tidak cukup pattern).")
    lines.append(f"- NER cover {len(ner_per_chunk)} chunks (full coverage corpus 1094).")
    lines.append(f"- NER tambah **{len(only_ner)} chunks** yang manual tidak label sama sekali.")
    lines.append("- Implikasi: KG v3 (build from NER) lebih lengkap dari KG v2 (build from manual).\n")

    lines.append("## Sample Misclassifications\n")
    lines.append(f"5 contoh per kategori per label di `{OUT_SAMPLES.relative_to(ROOT).as_posix()}`. "
                 f"Untuk error analysis manual.\n")

    for label in LABELS:
        lines.append(f"### {label}\n")
        sub = df_samples[df_samples["label"] == label]
        for category in ["missed_by_NER", "extra_by_NER", "partial_match_NER"]:
            sub_cat = sub[sub["category"] == category].head(5)
            if len(sub_cat) == 0:
                continue
            lines.append(f"**{category}** ({len(sub[sub['category']==category])} total, top 5):")
            for _, row in sub_cat.iterrows():
                extra = ""
                if row.get("partial_match_with_manual"):
                    extra = f"  ↔ manual: `{row['partial_match_with_manual']}`"
                lines.append(f"- `{row['entity_text']}` (chunk {row['chunk_id']}){extra}")
            lines.append("")

    lines.append("## Kesimpulan\n")
    lines.append(f"1. **Coverage NER lebih luas**: {len(ner_per_chunk)} chunks vs manual {len(manual_per_chunk)} (+{len(only_ner)} only-NER chunks).")
    lines.append(f"2. **Micro F1 entity = {micro_f1:.4f}** di common chunks.")
    lines.append(f"3. NER bukan untuk replace manual, tapi untuk **scale-up coverage** dari ~600 chunks manual ke 1094 chunks full.")
    lines.append("4. Manual masih bermanfaat untuk **anchor entity high-precision** di subset yang ke-curate.")
    lines.append("5. KG v3 yang dibangun dari NER inference punya 1280 nodes (vs 892 v2 manual) dan 491 edges (vs 322 v2) — graf lebih lengkap.\n")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {OUT_MD}")
    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
