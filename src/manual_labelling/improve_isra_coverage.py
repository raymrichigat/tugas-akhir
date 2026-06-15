"""
Perbaikan cakupan EVENT 'Isra'' pada gold (additive, defensible) — pelengkap
`improve_event_coverage.py`. Hasil review under-annotation 2026-06-10.

Akar masalah:
  - `pre_labelling.py` hanya punya trigger EVENT untuk pola "Perang/Ghazwah/Sariyah X".
    Peristiwa bernama "Isra'" (Isra' Mi'raj) TIDAK punya trigger → sistematis ke-skip,
    padahal gold SUDAH melabeli "Isra'" sebagai EVENT 3x di bab 000080 (konsisten).

Yang dilakukan (HANYA menambah, tidak menghapus/mengubah label lama):
  - Cari "Isra'" (WAJIB apostrof → otomatis buang "Israil"/"Bani Israil") opsional diikuti
    "Mi'raj" / "dan Mi'raj".
  - EXCLUDE didahului "Al-"/"al-" (rujukan surah Al-Quran "Al-Isra : 31", BUKAN peristiwa).
  - Tambah sebagai EVENT HANYA jika span tidak overlap entitas yang sudah ada.

Catatan kejujuran:
  - Mengubah test gold → angka F1 EVENT berubah (diharapkan naik). Disclosure di Bab 4.
  - Span "Isra'" konsisten dengan gold (000080-002 sudah "Isra'" = EVENT).

Pakai:
  venv\\Scripts\\python.exe src\\manual_labelling\\improve_isra_coverage.py           # dry-run
  venv\\Scripts\\python.exe src\\manual_labelling\\improve_isra_coverage.py --apply   # tulis gold
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
LOG = ROOT / "data" / "result" / "analysis" / "label_audit" / "isra_coverage_added.csv"

# WAJIB apostrof (buang "Israil"); EXCLUDE prefix Al-/al- (buang surah Al-Isra);
# tidak didahului huruf (buang "Kisra"); opsional "(dan) Mi'raj".
NEW_ISRA_RE = re.compile(r"(?<![A-Za-z-])Isra'(?:\s+(?:[Dd]an\s+)?Mi'raj)?")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Tulis perubahan ke gold")
    args = ap.parse_args()

    df = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig").fillna("")
    df.columns = df.columns.astype(str).str.replace("﻿", "", regex=False).str.strip()

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
        return any(s < xe and e > xs for (xs, xe) in existing_spans.get(cid, []))

    added = []
    for cid, text in chunk_text.items():
        new_here: list[tuple[int, int]] = []
        for m in NEW_ISRA_RE.finditer(text):
            s, e = m.start(), m.end()
            et = m.group(0)
            if overlaps(cid, s, e) or any(s < ne and e > ns for ns, ne in new_here):
                continue
            new_here.append((s, e))
            added.append({**chunk_meta[cid], "entity_text": et, "label": "EVENT",
                          "notes": "auto_isra_coverage", "start_char": s, "end_char": e})

    print(f"[dry-run] entitas EVENT 'Isra'' baru yang akan ditambah: {len(added)}")
    if added:
        df_add = pd.DataFrame(added)
        print("  per chunk:", df_add["chunk_id"].value_counts().to_dict())
        print("  contoh (chunk : entity_text : konteks):")
        for row in added:
            cid = row["chunk_id"]; s = row["start_char"]; e = row["end_char"]
            ctx = " ".join(chunk_text[cid][max(0, s - 30):e + 30].split())
            print(f"    {cid}: '{row['entity_text']}'  …{ctx}…")
        LOG.parent.mkdir(parents=True, exist_ok=True)
        df_add.to_csv(LOG, index=False, encoding="utf-8")
        print(f"  log -> {LOG}")

    if not args.apply:
        print("\n(DRY-RUN. Jalankan dengan --apply untuk menulis ke gold.)")
        return

    bak = GOLD.with_suffix(".csv.bak_isracov")
    shutil.copy(GOLD, bak)
    out_cols = list(df.columns)
    df_add_full = pd.DataFrame(added)[
        [c for c in out_cols if c in (meta_cols + ["entity_text", "label", "notes", "start_char", "end_char"])]
    ]
    # append di AKHIR tanpa re-sort → partisi train/test (deterministik) tetap sama.
    df_new = pd.concat([df, df_add_full], ignore_index=True)
    df_new.to_csv(GOLD, sep=";", encoding="utf-8-sig", index=False)
    print(f"\n[APPLY] +{len(added)} EVENT 'Isra''. Backup: {bak.name}. Gold ditulis ulang: {GOLD.name}")


if __name__ == "__main__":
    main()
