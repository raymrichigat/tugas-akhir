#!/usr/bin/env python3
"""
jw_threshold_sweep.py — Justifikasi empiris ambang Jaro-Winkler (Bu Ratih #7).

Menguji beberapa nilai ambang (0,85–0,95) pada tahap safety-net JW di
`alias_clustering.py`, memakai guard yang SAMA (compound-prefix, patronymic,
rasio panjang, exclude-pairs). Untuk tiap pasangan nama yang lolos guard,
dicatat skor JW-nya, lalu dilihat pasangan mana yang tergabung di tiap ambang.

Tujuan: menunjukkan bahwa ambang 0,85 (default Rayssa) menggabungkan pasangan
beda-entitas, sedangkan 0,93 menyisakan hanya variasi ejaan/OCR yang sah.

Output: data/result/alias_clustering/jw_threshold_sweep/
  ├── jw_sweep_pairs.csv     (semua pasangan lolos-guard + skor JW + band)
  └── jw_threshold_sweep.md  (tabel jumlah per ambang + daftar pasangan borderline)

Jalankan: venv\\Scripts\\python src\\alias_clustering\\jw_threshold_sweep.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from alias_clustering import (  # noqa: E402
    jaro_winkler, _is_excluded, IN_CSV,
    PERSON_CLUSTERS, LOCATION_CLUSTERS, EVENT_CLUSTERS,
)

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "result" / "alias_clustering" / "jw_threshold_sweep"
THRESHOLDS = [0.85, 0.88, 0.90, 0.92, 0.93, 0.95]

_COMPOUND_RE = re.compile(r"^(?:Abu|Abul|Ummu|Ibnu|Ibnul)\s+(.+)")


def _dist(name):
    m = _COMPOUND_RE.match(name)
    return m.group(1) if m else name


def _pat(name):
    parts = re.split(r"\s+(?:bin|binti)\s+", name, maxsplit=1)
    return parts[1] if len(parts) > 1 else ""


def passes_guards(a, b):
    """Guard identik build_alias_map (selain ambang JW itu sendiri)."""
    if _is_excluded(a, b):
        return False
    da, db = _dist(a), _dist(b)
    if da != a and db != b and jaro_winkler(da, db) < 0.90:
        return False
    pa, pb = _pat(a), _pat(b)
    if pa and pb:
        if jaro_winkler(pa, pb) < 0.85:
            return False
    elif pa or pb:
        return False
    if min(len(a), len(b)) / max(len(a), len(b)) < 0.80:
        return False
    return True


def known_same_pairs():
    """Pasangan yang manual-cluster tandai SAMA (alias<->canonical & antar-alias)."""
    same = set()
    for clusters in (PERSON_CLUSTERS, LOCATION_CLUSTERS, EVENT_CLUSTERS):
        for canon, aliases in clusters.items():
            members = [canon] + list(aliases)
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    same.add(frozenset((members[i], members[j])))
    return same


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_CSV, sep=";", encoding="utf-8-sig").fillna("")
    df["entity_text"] = df["entity_text"].astype(str).str.strip()
    df = df[df["entity_text"] != ""]
    SAME = known_same_pairs()

    rows = []
    for label in ["PERSON", "LOCATION", "EVENT"]:
        names = sorted(df[df["label"] == label]["entity_text"].unique().tolist())
        for i, a in enumerate(names):
            for j in range(i + 1, len(names)):
                b = names[j]
                if not passes_guards(a, b):
                    continue
                sim = jaro_winkler(a, b)
                if sim < THRESHOLDS[0]:
                    continue
                anno = "variasi-sah" if frozenset((a, b)) in SAME else "?"
                rows.append(dict(label=label, nama_a=a, nama_b=b, jw=round(sim, 4), anotasi=anno))

    res = pd.DataFrame(rows).sort_values("jw", ascending=False)
    res.to_csv(OUT_DIR / "jw_sweep_pairs.csv", index=False, encoding="utf-8-sig")

    # tabel jumlah merge per ambang
    counts = {t: int((res["jw"] >= t).sum()) for t in THRESHOLDS}

    L = ["# Justifikasi Empiris Ambang Jaro-Winkler (Bu Ratih #7)\n",
         "> Sweep ambang pada tahap safety-net JW `alias_clustering.py` (guard sama: "
         "compound-prefix, patronymic, rasio panjang, exclude-pairs). "
         "Dihasilkan `jw_threshold_sweep.py`.\n",
         "\n## Jumlah pasangan yang digabung JW per ambang\n",
         "| Ambang | Pasangan tergabung |", "|---:|---:|"]
    for t in THRESHOLDS:
        mark = " ← **dipakai**" if t == 0.93 else (" (default Rayssa)" if t == 0.85 else "")
        L.append(f"| {t:.2f} | {counts[t]}{mark} |")

    band = res[(res["jw"] >= 0.85) & (res["jw"] < 0.93)]
    L += ["",
          f"\n## Pasangan borderline 0,85 ≤ JW < 0,93 ({len(band)} pasangan)\n",
          "> Inilah pasangan yang **akan ikut tergabung jika ambang diturunkan ke 0,85** "
          "tetapi **ditolak pada 0,93**. Kolom `anotasi`: `variasi-sah` = memang satu entitas "
          "(tertangkap manual cluster), `?` = perlu diperiksa (kandidat salah-gabung).\n",
          "| Nama A | Nama B | JW | Label | Anotasi |", "|---|---|---:|---|---|"]
    for _, r in band.iterrows():
        L.append(f"| {r['nama_a']} | {r['nama_b']} | {r['jw']:.4f} | {r['label']} | {r['anotasi']} |")

    merged93 = res[res["jw"] >= 0.93]
    L += ["",
          f"\n## Pasangan yang digabung pada ambang 0,93 ({len(merged93)} pasangan)\n",
          "| Nama A | Nama B | JW | Label | Anotasi |", "|---|---|---:|---|---|"]
    for _, r in merged93.iterrows():
        L.append(f"| {r['nama_a']} | {r['nama_b']} | {r['jw']:.4f} | {r['label']} | {r['anotasi']} |")

    (OUT_DIR / "jw_threshold_sweep.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("Jumlah pasangan tergabung per ambang:")
    for t in THRESHOLDS:
        print(f"  {t:.2f}: {counts[t]}")
    print(f"Borderline 0,85-0,93: {len(band)} pasangan")
    print(f"-> {OUT_DIR/'jw_threshold_sweep.md'}")
    print(f"-> {OUT_DIR/'jw_sweep_pairs.csv'}")


if __name__ == "__main__":
    main()
