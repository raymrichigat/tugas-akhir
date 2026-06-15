#!/usr/bin/env python3
"""
review_under_annotation.py — saring kandidat under-annotation jadi DAFTAR REVIEW yang bersih.

Masalah: `under_annotation_candidates.csv` cuma punya coverage mentah, yang BIAS karena
banyak kemunculan "tak ter-label" sebenarnya = sub-span nama lebih panjang (sudah tercakup)
atau kata umum. Script ini (READ-ONLY, tidak mengubah gold) memilah tiap kemunculan:

  - covered  : overlap dengan span gold lain  -> BUKAN miss (diabaikan)
  - miss riil: kemunculan word-bounded yang TIDAK tercakup span apa pun

Untuk tiap surface juga ditebak `suggested_label` = label mayoritas saat surface itu
DILABELI di tempat lain, dan miss dipisah kapital vs huruf-kecil (kapital = lebih mungkin
proper-noun entitas; huruf-kecil = lebih mungkin kata umum).

Output:
  data/result/analysis/label_audit/under_annotation_review.md   (untuk dibaca/di-review)
  data/result/analysis/label_audit/under_annotation_review.csv  (per-kemunculan, untuk apply by-rule)

Jalankan: venv\\Scripts\\python src\\manual_labelling\\review_under_annotation.py
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def to_int(x):
    try:
        return int(float(str(x).strip()))
    except (ValueError, TypeError):
        return None


def main() -> None:
    repo = find_repo_root(Path(__file__))
    gold_path = repo / "data/result/manual_labelling/sirah_prelabelled.csv"
    cand_path = repo / "data/result/analysis/label_audit/under_annotation_candidates.csv"
    out_md = repo / "data/result/analysis/label_audit/under_annotation_review.md"
    out_csv = repo / "data/result/analysis/label_audit/under_annotation_review.csv"

    df = pd.read_csv(gold_path, sep=";", dtype=str, keep_default_na=False)
    cands = pd.read_csv(cand_path, dtype=str, keep_default_na=False)["surface"].tolist()

    # teks per chunk (ambil teks_chunk pertama yang tidak kosong)
    chunk_text: dict[str, str] = {}
    labeled_spans: dict[str, list] = defaultdict(list)  # chunk_id -> [(s,e,label,text)]
    surface_label: dict[str, Counter] = defaultdict(Counter)  # lower(entity) -> label counter

    for _, r in df.iterrows():
        cid = r["chunk_id"]
        txt = r["teks_chunk"]
        if cid not in chunk_text and txt.strip():
            chunk_text[cid] = txt
        s, e = to_int(r["start_char"]), to_int(r["end_char"])
        lab = r["label"].strip()
        ent = r["entity_text"].strip()
        if s is not None and e is not None and lab:
            labeled_spans[cid].append((s, e, lab, ent))
            if ent:
                surface_label[ent.lower()][lab] += 1

    def suggest_label(surface: str) -> str:
        # 1) exact match entity == surface
        if surface in surface_label and surface_label[surface]:
            return surface_label[surface].most_common(1)[0][0]
        # 2) entity yang MENGANDUNG surface sebagai kata
        pat = re.compile(rf"(?<!\w){re.escape(surface)}(?!\w)", re.IGNORECASE)
        agg = Counter()
        for ent_l, c in surface_label.items():
            if pat.search(ent_l):
                agg.update(c)
        return agg.most_common(1)[0][0] if agg else "?"

    per_surface = []
    occ_rows = []  # untuk CSV
    for surface in cands:
        pat = re.compile(rf"(?<!\w){re.escape(surface)}(?!\w)", re.IGNORECASE)
        sug = suggest_label(surface)
        misses = []  # (chunk_id, actual_text, is_cap, context)
        for cid, txt in chunk_text.items():
            spans = labeled_spans.get(cid, [])
            for m in pat.finditer(txt):
                s, e = m.start(), m.end()
                covered = any(not (e <= ls or s >= le) for (ls, le, _, _) in spans)
                if covered:
                    continue
                actual = txt[s:e]
                is_cap = actual[:1].isupper()
                ctx = txt[max(0, s - 35):s] + "[[" + actual + "]]" + txt[e:e + 35]
                ctx = " ".join(ctx.split())
                misses.append((cid, actual, is_cap, ctx))
                occ_rows.append({
                    "surface": surface, "suggested_label": sug, "chunk_id": cid,
                    "matched_text": actual, "is_capitalized": is_cap,
                    "start": s, "end": e, "context": ctx,
                })
        n = len(misses)
        ncap = sum(1 for _, _, c, _ in misses if c)
        per_surface.append({
            "surface": surface, "suggested_label": sug,
            "real_miss": n, "cap": ncap, "lower": n - ncap, "examples": misses[:6],
        })

    per_surface.sort(key=lambda d: (d["cap"], d["real_miss"]), reverse=True)

    # ---- tulis CSV per-kemunculan ----
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["surface", "suggested_label", "chunk_id",
                                          "matched_text", "is_capitalized", "start", "end", "context"])
        w.writeheader()
        w.writerows(occ_rows)

    # ---- tulis MD review ----
    total_miss = sum(d["real_miss"] for d in per_surface)
    total_cap = sum(d["cap"] for d in per_surface)
    by_label = Counter()
    for r in occ_rows:
        if r["is_capitalized"]:
            by_label[r["suggested_label"]] += 1

    lines = []
    lines.append("# Review Under-Annotation (sudah disaring dari sub-span & coverage bias)\n")
    lines.append("> Read-only. `[[...]]` = kemunculan yang **tidak tercakup span gold mana pun** (miss riil).\n")
    lines.append(f"\n**Total miss riil:** {total_miss}  | **kapital (kandidat kuat):** {total_cap}  "
                 f"| huruf-kecil (cek kata umum): {total_miss - total_cap}\n")
    lines.append(f"\n**Miss kapital per suggested-label:** "
                 + ", ".join(f"{k}={v}" for k, v in by_label.most_common()) + "\n")
    lines.append("\n> Urut: yang punya miss-kapital terbanyak dulu (paling mungkin entitas asli yang ke-skip).\n")
    lines.append("\n| surface | suggested | miss riil | kapital | kecil |\n|---|---|---:|---:|---:|\n")
    for d in per_surface:
        lines.append(f"| {d['surface']} | {d['suggested_label']} | {d['real_miss']} | {d['cap']} | {d['lower']} |\n")

    lines.append("\n---\n\n## Contoh konteks per surface (maks 6)\n")
    for d in per_surface:
        if d["real_miss"] == 0:
            continue
        lines.append(f"\n### {d['surface']} → **{d['suggested_label']}**  "
                     f"(miss {d['real_miss']}: {d['cap']} kapital / {d['lower']} kecil)\n")
        for cid, actual, is_cap, ctx in d["examples"]:
            flag = "🔠" if is_cap else "🔡"
            lines.append(f"- {flag} `{cid}` … {ctx}\n")

    out_md.write_text("".join(lines), encoding="utf-8")

    # ---- ringkasan console ----
    print(f"[ok] {out_md.relative_to(repo)}")
    print(f"[ok] {out_csv.relative_to(repo)}")
    print(f"\nTotal miss riil (setelah saring sub-span): {total_miss}  | kapital: {total_cap}")
    print("Miss kapital per suggested-label:", dict(by_label.most_common()))
    print(f"\n{'surface':<22}{'sug':>10}{'miss':>6}{'cap':>5}{'low':>5}")
    for d in per_surface[:25]:
        print(f"{d['surface']:<22}{d['suggested_label']:>10}{d['real_miss']:>6}{d['cap']:>5}{d['lower']:>5}")


if __name__ == "__main__":
    main()
