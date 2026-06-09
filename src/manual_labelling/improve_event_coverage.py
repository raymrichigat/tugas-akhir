"""
Perbaikan cakupan EVENT pada gold (additive, defensible).

Akar masalah (terbukti di audit + pre_labelling.py):
  - `_EVENT_PERANG_RE` / `_EVENT_GHAZWAH_RE` mensyaratkan trigger HURUF KAPITAL
    ("Perang X"), sehingga "perang X" huruf kecil sistematis ke-skip.
  - "Sariyah X" tidak punya regex sama sekali.

Yang dilakukan script ini (HANYA menambah, tidak menghapus/mengubah label lama):
  - Cari pola (perang|ghazwah|sariyah) + ProperNoun (case-INsensitive trigger,
    nama tetap harus kapital agar tidak menangkap "perang itu"/"perang besar").
  - Tambahkan sebagai EVENT HANYA jika span-nya tidak overlap entitas mana pun
    yang sudah ada (konservatif → tidak menimbulkan konflik/overlap).

Catatan kejujuran:
  - Ini perbaikan kecil & terukur, bukan dramatis. Mengubah test gold → angka F1
    akan berubah (diharapkan EVENT naik). Disclosure ini perlu di Bab 4.
  - TIDAK melakukan mass-add (hijrah/ramadhan/badr) karena mayoritas = kata umum /
    sudah ter-cover span lain → akan menambah noise.

Pakai:
  # dry-run (default): hanya lapor apa yang AKAN ditambah
  venv\Scripts\python.exe src\manual_labelling\improve_event_coverage.py
  # apply: tulis sirah_prelabelled.csv (backup .bak_eventcov dibuat)
  venv\Scripts\python.exe src\manual_labelling\improve_event_coverage.py --apply
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
LOG = ROOT / "data" / "result" / "analysis" / "label_audit" / "event_coverage_added.csv"

# atom nama (menangani artikel Arab: As-Sawiq, Al-Yamamah, An-Nadhir)
_ART = r"(?:(?:Al|An|Ash|As|Ats|Ad|Ar|Az|At|Adz)-)?"
_NAME = _ART + r"[A-Z][a-z']+"
# trigger case-insensitive, tapi nama harus Kapital (hindari "perang itu"/"perang besar")
NEW_EVENT_RE = re.compile(
    r"\b((?:[Pp]erang|[Gg]hazwah|[Ss]ariyah)\s+" + _NAME + r"(?:\s+" + _NAME + r")?)"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Tulis perubahan ke gold")
    args = ap.parse_args()

    df = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig").fillna("")
    df.columns = df.columns.astype(str).str.replace("﻿", "", regex=False).str.strip()

    # span existing per chunk + metadata per chunk
    existing_spans: dict[str, list[tuple[int, int]]] = {}
    chunk_text: dict[str, str] = {}
    chunk_meta: dict[str, dict] = {}
    meta_cols = ["chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab", "halaman", "teks_chunk"]

    for r in df.itertuples(index=False):
        cid = getattr(r, "chunk_id")
        if cid not in chunk_text:
            chunk_text[cid] = str(getattr(r, "teks_chunk"))
            chunk_meta[cid] = {c: getattr(r, c) for c in meta_cols}
            existing_spans[cid] = []
        lab = str(getattr(r, "label")).strip()
        sc, ec = str(getattr(r, "start_char")).strip(), str(getattr(r, "end_char")).strip()
        if lab:
            try:
                existing_spans[cid].append((int(float(sc)), int(float(ec))))
            except ValueError:
                pass

    def overlaps(cid, s, e) -> bool:
        for (xs, xe) in existing_spans.get(cid, []):
            if s < xe and e > xs:
                return True
        return False

    added = []
    for cid, text in chunk_text.items():
        new_here: list[tuple[int, int]] = []
        for m in NEW_EVENT_RE.finditer(text):
            s, e = m.start(1), m.end(1)
            et = m.group(1)
            # skip kalau overlap existing ATAU sudah ditambah di chunk ini
            if overlaps(cid, s, e) or any(s < ne and e > ns for ns, ne in new_here):
                continue
            new_here.append((s, e))
            row = {**chunk_meta[cid], "entity_text": et, "label": "EVENT",
                   "notes": "auto_event_coverage", "start_char": s, "end_char": e}
            added.append(row)

    print(f"[dry-run] entitas EVENT baru yang akan ditambah: {len(added)}")
    if added:
        df_add = pd.DataFrame(added)
        # ringkas: distribusi trigger
        df_add["trigger"] = df_add["entity_text"].str.split().str[0].str.lower()
        print("  per trigger:", df_add["trigger"].value_counts().to_dict())
        print("  contoh:")
        for r in df_add.head(20).itertuples(index=False):
            print(f"    {r.chunk_id}: '{r.entity_text}'")
        LOG.parent.mkdir(parents=True, exist_ok=True)
        df_add.drop(columns=["trigger"]).to_csv(LOG, index=False, encoding="utf-8")
        print(f"  log -> {LOG}")

    if not args.apply:
        print("\n(DRY-RUN. Jalankan dengan --apply untuk menulis ke gold.)")
        return

    # apply: backup + append
    bak = GOLD.with_suffix(".csv.bak_eventcov")
    shutil.copy(GOLD, bak)
    out_cols = list(df.columns)
    df_add_full = pd.DataFrame(added)[
        [c for c in out_cols if c in (meta_cols + ["entity_text", "label", "notes", "start_char", "end_char"])]
    ]
    # PENTING: append di AKHIR tanpa re-sort. Urutan first-occurrence tiap chunk
    # harus dipertahankan supaya train_test_split (deterministik, order-dependent)
    # menghasilkan partisi train/test yang SAMA dengan hasil historis.
    df_new = pd.concat([df, df_add_full], ignore_index=True)
    df_new.to_csv(GOLD, sep=";", encoding="utf-8-sig", index=False)
    print(f"\n[APPLY] +{len(added)} EVENT. Backup: {bak.name}. Gold ditulis ulang: {GOLD.name}")


if __name__ == "__main__":
    main()
