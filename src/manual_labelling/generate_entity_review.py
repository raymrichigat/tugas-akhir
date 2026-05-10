"""
Generate Entity Review — Sirah Nabawiyah
Membaca sirah_prelabelled.csv dan menghasilkan entity_review.md
berisi:
  1. Daftar masalah yang perlu diperbaiki (noise prefix, nama terpotong, variasi)
  2. Daftar unik entitas per label, diurutkan berdasarkan frekuensi
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_CSV  = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\manual_labelling\sirah_prelabelled.csv")
OUT_MD  = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\manual_labelling\entity_review.md")

LABEL_ORDER = ["PERSON", "LOCATION", "EVENT", "TIME"]

# Prefix noise: kata-kata Indonesia yang seharusnya tidak jadi bagian entitas
NOISE_PREFIXES = [
    "Sesungguhnya", "Ternyata", "Suruh", "Kekhawatiran", "Sakit",
    "Adapun", "Barisan", "Kemudian", "Lalu", "Maka", "Ketika",
    "Sementara", "Bahwa", "Wahai", "Hai", "Yaitu", "Adalah",
    "Setelah", "Sebelum", "Seperti", "Hingga", "Tentang",
    "Antara", "Berkata", "Datang", "Pergi", "Demikian",
    "Diantara", "Sedangkan", "Begitu", "Inilah", "Itulah",
    "Pasukan", "Jamil",
]

# Pola nama terpotong: berakhir dengan "bin Al", "bin Abu", dsb tanpa nama lanjutan
TRUNCATED_PATTERN = re.compile(
    r".+\s(bin|binti)\s(Al|Abu|An|Abi|Ash|Ad|As|Ats)$", re.IGNORECASE
)


# ── Fungsi deteksi masalah ──────────────────────────────────────────────────

def find_noise_prefix(df: pd.DataFrame) -> list[dict]:
    """Cari entitas yang mengandung prefix noise (kata Indonesia nyasar)."""
    issues = []
    seen = set()
    for _, row in df.iterrows():
        ent = row["entity_text"]
        if ent in seen:
            continue
        for prefix in NOISE_PREFIXES:
            if ent.startswith(prefix + " ") and len(ent) > len(prefix) + 1:
                seen.add(ent)
                freq = len(df[df["entity_text"] == ent])
                suggestion = ent[len(prefix) + 1:].strip()
                issues.append({
                    "entity": ent,
                    "label": row["label"],
                    "freq": freq,
                    "suggestion": suggestion,
                    "chunk_ids": df[df["entity_text"] == ent]["chunk_id"].unique()[:3],
                })
                break
    return issues


def find_truncated_names(df: pd.DataFrame) -> list[dict]:
    """Cari nama yang terpotong (berakhir di 'bin Al', 'bin Abu', dsb)."""
    issues = []
    seen = set()
    for _, row in df.iterrows():
        ent = row["entity_text"]
        if ent in seen:
            continue
        if TRUNCATED_PATTERN.match(ent):
            seen.add(ent)
            freq = len(df[df["entity_text"] == ent])
            issues.append({
                "entity": ent,
                "label": row["label"],
                "freq": freq,
                "chunk_ids": df[df["entity_text"] == ent]["chunk_id"].unique()[:3],
            })
    # Urutkan berdasarkan frekuensi (tertinggi dulu)
    issues.sort(key=lambda x: -x["freq"])
    return issues


def find_event_variations(df: pd.DataFrame) -> list[dict]:
    """Cari variasi event yang kemungkinan merujuk ke event yang sama."""
    events = df[df["label"] == "EVENT"]["entity_text"].unique()
    groups = {}

    for e in events:
        # Normalisasi: hapus "Perang ", "Al-", spasi ganda
        base = e.replace("Perang ", "").replace("Al-", "").strip()
        for f in events:
            if e != f:
                base_f = f.replace("Perang ", "").replace("Al-", "").strip()
                if base == base_f or base in f or base_f in e:
                    key = min(e, f)
                    if key not in groups:
                        groups[key] = set()
                    groups[key].add(e)
                    groups[key].add(f)

    issues = []
    reported = set()
    for key, group in groups.items():
        frozen = frozenset(group)
        if frozen not in reported:
            reported.add(frozen)
            freq_info = []
            for name in sorted(group):
                freq = len(df[df["entity_text"] == name])
                freq_info.append(f'"{name}" (x{freq})')
            issues.append({"variants": sorted(group), "freq_info": freq_info})

    return issues


def find_location_variations(df: pd.DataFrame) -> list[dict]:
    """Cari variasi lokasi yang kemungkinan sama."""
    known_variations = [
        (["Tha'if", "Thaif"], "Variasi transliterasi"),
        (["Yatsrib", "Yastrib"], "Variasi ejaan (keduanya = Madinah kuno)"),
    ]
    locs = set(df[df["label"] == "LOCATION"]["entity_text"].unique())
    issues = []
    for variants, note in known_variations:
        found = [v for v in variants if v in locs]
        if len(found) > 1:
            freq_info = []
            for name in found:
                freq = len(df[df["entity_text"] == name])
                freq_info.append(f'"{name}" (x{freq})')
            issues.append({"variants": found, "note": note, "freq_info": freq_info})
    return issues


# ── Generate markdown ────────────────────────────────────────────────────────

def generate_review(df: pd.DataFrame) -> str:
    lines = []
    lines.append("# Entity Review — Sirah Nabawiyah")
    lines.append("")
    lines.append("Auto-generated. Cek masalah di bawah, lalu perbaiki di `sirah_prelabelled.csv`.")
    lines.append("")

    # ── BAGIAN 1: MASALAH YANG PERLU DIPERBAIKI ──
    lines.append("---")
    lines.append("")
    lines.append("# MASALAH YANG PERLU DIPERBAIKI")
    lines.append("")

    # 1a. Prefix noise
    noise = find_noise_prefix(df)
    lines.append(f"## 1. Prefix Noise ({len(noise)} entitas)")
    lines.append("")
    lines.append("Entitas yang mengandung kata Indonesia yang seharusnya bukan bagian dari nama.")
    lines.append("")
    if noise:
        lines.append("| No | Entity | Label | Freq | Saran Perbaikan | Contoh chunk_id |")
        lines.append("|---|---|---|---|---|---|")
        for i, issue in enumerate(noise, 1):
            chunks = ", ".join(str(c) for c in issue["chunk_ids"])
            lines.append(
                f'| {i} | {issue["entity"]} | {issue["label"]} | {issue["freq"]} '
                f'| **{issue["suggestion"]}** | {chunks} |'
            )
    else:
        lines.append("Tidak ada masalah ditemukan.")
    lines.append("")

    # 1b. Nama terpotong
    truncated = find_truncated_names(df)
    lines.append(f"## 2. Nama Terpotong ({len(truncated)} entitas)")
    lines.append("")
    lines.append("Nama yang berakhir di 'bin Al', 'bin Abu', dsb — kemungkinan terpotong saat labelling.")
    lines.append("Perlu dicek di teks aslinya dan dilengkapi nama lengkapnya.")
    lines.append("")
    if truncated:
        lines.append("| No | Entity | Label | Freq | Contoh chunk_id |")
        lines.append("|---|---|---|---|---|")
        for i, issue in enumerate(truncated, 1):
            chunks = ", ".join(str(c) for c in issue["chunk_ids"])
            lines.append(
                f'| {i} | {issue["entity"]} | {issue["label"]} | {issue["freq"]} '
                f'| {chunks} |'
            )
    else:
        lines.append("Tidak ada masalah ditemukan.")
    lines.append("")

    # 1c. Variasi event
    event_vars = find_event_variations(df)
    lines.append(f"## 3. Variasi Event ({len(event_vars)} grup)")
    lines.append("")
    lines.append("Event yang kemungkinan merujuk ke peristiwa yang sama tapi beda penulisan.")
    lines.append("")
    if event_vars:
        for i, issue in enumerate(event_vars, 1):
            lines.append(f"{i}. {' vs '.join(issue['freq_info'])}")
    else:
        lines.append("Tidak ada masalah ditemukan.")
    lines.append("")

    # 1d. Variasi lokasi
    loc_vars = find_location_variations(df)
    lines.append(f"## 4. Variasi Lokasi ({len(loc_vars)} grup)")
    lines.append("")
    if loc_vars:
        for i, issue in enumerate(loc_vars, 1):
            lines.append(f"{i}. {' vs '.join(issue['freq_info'])} — {issue['note']}")
    else:
        lines.append("Tidak ada masalah ditemukan.")
    lines.append("")

    # ── BAGIAN 2: DAFTAR ENTITAS LENGKAP ──
    lines.append("---")
    lines.append("")
    lines.append("# DAFTAR ENTITAS LENGKAP")
    lines.append("")

    df_ent = df[df["label"].astype(str).str.strip().ne("") & df["entity_text"].astype(str).str.strip().ne("")]

    for label in LABEL_ORDER:
        subset = df_ent[df_ent["label"] == label]
        counts = subset["entity_text"].value_counts()
        n_unique = len(counts)

        lines.append(f"## {label} ({n_unique} unique entities)")
        lines.append("")
        lines.append("| No | Entity | Jumlah |")
        lines.append("|---|---|---|")

        for i, (entity, count) in enumerate(counts.items(), start=1):
            # Tandai entitas bermasalah
            flag = ""
            if any(entity.startswith(p + " ") for p in NOISE_PREFIXES):
                flag = " ⚠️ NOISE"
            elif TRUNCATED_PATTERN.match(entity):
                flag = " ⚠️ TERPOTONG"
            lines.append(f"| {i} | {entity}{flag} | {count} |")

        lines.append("")

    return "\n".join(lines)


def main():
    df = pd.read_csv(IN_CSV, sep=";", encoding="utf-8-sig").fillna("")
    df["entity_text"] = df["entity_text"].astype(str).str.strip()
    df = df[df["entity_text"] != ""]
    print(f"Rows dibaca: {len(df)}")

    md = generate_review(df)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Output disimpan ke: {OUT_MD}")

    # Ringkasan
    df_ent = df[df["label"].astype(str).str.strip().ne("")]
    for label in LABEL_ORDER:
        subset = df_ent[df_ent["label"] == label]
        n_unique = subset["entity_text"].nunique()
        n_total  = len(subset)
        print(f"  {label:<10}: {n_unique} unique, {n_total} total kemunculan")

    # Ringkasan masalah
    noise = find_noise_prefix(df)
    truncated = find_truncated_names(df)
    print(f"\n  MASALAH DITEMUKAN:")
    print(f"    Prefix noise   : {len(noise)} entitas")
    print(f"    Nama terpotong : {len(truncated)} entitas")


if __name__ == "__main__":
    main()
