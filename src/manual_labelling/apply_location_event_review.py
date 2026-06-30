"""
apply_location_event_review.py
==============================
Terapkan keputusan worksheet LOCATION-vs-EVENT (diisi manual di
`location_event_review.md`) ke `sirah_prelabelled.csv`.

Mekanisme pemetaan
------------------
Worksheet di-generate `generate_location_event_review.py` dengan meng-ekstrak
SETIAP kemunculan standalone DUAL_TERMS (Badr/Uhud/...) lalu MENGURUTKAN
(entity_text, chunk_id) dan menomori [1..N]. Skrip ini MEN-DERIVE ULANG daftar
kandidat itu (dengan start_char) dari gold yang SUDAH diregen, lalu meng-align
per-nomor dengan keputusan di .md. Aman selama daftar kandidat identik
(genealogi/apostrof tidak menyentuh DUAL_TERMS) — diverifikasi via assert.

Keputusan:
  LOCATION -> biarkan (sudah LOCATION)
  EVENT    -> ubah label baris gold jadi EVENT
  O        -> hapus baris entitas (bukan entitas)
"""

import re
import shutil
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
GOLD = ROOT / "data/result/manual_labelling/sirah_prelabelled.csv"
MD = ROOT / "data/result/manual_labelling/gold_review/location_event_review.md"

DUAL_TERMS = [
    "Badr", "Uhud", "Khandaq", "Khaibar", "Hunain",
    "Hudaibiyah", "Tabuk", "Ahzab", "Mu'tah", "Bu'ats", "Fijar",
]


def is_bare(text: str) -> bool:
    t = str(text).strip().lower()
    return any(t == d.lower() for d in DUAL_TERMS)


def derive_candidates(df):
    """Replika logika generator: bare DUAL_TERMS + start_char, sort (entity, chunk)."""
    rows = []
    for idx, r in df.iterrows():
        if r["label"] == "" or not is_bare(r["entity_text"]):
            continue
        try:
            sc = int(float(r["start_char"]))
        except (ValueError, TypeError):
            continue
        rows.append({"row_idx": idx, "chunk_id": r["chunk_id"],
                     "entity_text": r["entity_text"], "start_char": sc})
    cand = pd.DataFrame(rows).sort_values(
        ["entity_text", "chunk_id"], kind="stable").reset_index(drop=True)
    return cand


def parse_md(path):
    """Kembalikan list (no, chunk_id, entity_text, keputusan) urut nomor."""
    text = path.read_text(encoding="utf-8")
    out = {}
    cur_entity = None
    pending = None  # (no, chunk_id, entity_text)
    for line in text.splitlines():
        h = re.match(r"^##\s+(.+)$", line.strip())
        if h:
            cur_entity = h.group(1).strip()
            continue
        m = re.match(r"^\*\*\[(\d+)\]\*\*.*?chunk\s+([0-9-]+)", line.strip())
        if m:
            pending = (int(m.group(1)), m.group(2), cur_entity)
            continue
        k = re.search(r"`keputusan:\s*([A-Za-z?]+)\s*`", line.strip())
        if k and pending:
            no, cid, ent = pending
            out[no] = (cid, ent, k.group(1).strip().upper())
            pending = None
    return [out[n] for n in sorted(out)]


def main():
    df = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    df.columns = [c.replace("﻿", "").strip() for c in df.columns]

    cand = derive_candidates(df)
    decisions = parse_md(MD)

    print(f"Kandidat di gold (re-derive): {len(cand)}")
    print(f"Keputusan di .md           : {len(decisions)}")
    assert len(cand) == len(decisions), "Jumlah kandidat != keputusan — ABORT (cek regen)."

    # Verifikasi alignment per-nomor (chunk_id + entity_text harus cocok)
    mismatch = []
    for i, (cid, ent, kep) in enumerate(decisions):
        c = cand.iloc[i]
        if c["chunk_id"] != cid or c["entity_text"].strip().lower() != ent.strip().lower():
            mismatch.append((i + 1, cid, ent, c["chunk_id"], c["entity_text"]))
    if mismatch:
        print("\n[!!] MISALIGNMENT (5 pertama):")
        for mm in mismatch[:5]:
            print("   md:", mm[:3], " gold:", mm[3:])
        raise SystemExit("Alignment gagal — ABORT, tidak ada perubahan ditulis.")

    # Backup
    bak = GOLD.with_suffix(".csv.bak_before_loc")
    shutil.copy(GOLD, bak)
    print(f"Backup: {bak.name}")

    # Apply
    n_event = n_o = n_loc = 0
    drop_idx = []
    for i, (cid, ent, kep) in enumerate(decisions):
        ridx = cand.iloc[i]["row_idx"]
        if kep == "EVENT":
            df.at[ridx, "label"] = "EVENT"
            n_event += 1
        elif kep == "O":
            drop_idx.append(ridx)
            n_o += 1
        else:  # LOCATION (atau ?-tak-diisi -> diperlakukan LOCATION/biarkan)
            n_loc += 1

    if drop_idx:
        df = df.drop(index=drop_idx).reset_index(drop=True)

    df.to_csv(GOLD, sep=";", encoding="utf-8-sig", index=False)
    print(f"\nApplied -> EVENT: {n_event} | O(drop): {n_o} | LOCATION(biarkan): {n_loc}")
    print(f"Gold disimpan: {GOLD.name}  (baris: {len(df)})")


if __name__ == "__main__":
    main()
