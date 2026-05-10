"""
Alias Clustering — Sirah Nabawiyah
Mengelompokkan variasi nama entitas ke bentuk kanonik.

Pendekatan:
  1. Manual clusters — entitas yang sudah pasti merujuk ke orang/tempat/event sama
  2. Pattern matching — nama pendek yang merupakan bagian dari nama panjang
  3. Jaro-Winkler similarity — safety net untuk variasi ejaan

Input : sirah_prelabelled.csv
Output: alias_map.json       — {entity_text: canonical_name}
        alias_clusters.md    — laporan untuk review manual
"""

import json
import re
import pandas as pd
from pathlib import Path
from collections import defaultdict

# ── Konfigurasi ──────────────────────────────────────────────────────────────
BASE_DIR = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_CSV = BASE_DIR / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
OUT_DIR = BASE_DIR / "data" / "result" / "alias_clustering"
OUT_JSON = OUT_DIR / "alias_map.json"
OUT_MD = OUT_DIR / "alias_clusters.md"

JW_THRESHOLD = 0.93  # Jaro-Winkler threshold (dinaikkan dari 0.85 Rayssa karena
                      # nama Arab banyak yang strukturnya mirip tapi beda orang)

# ── Jaro-Winkler (implementasi mandiri) ─────────────────────────────────────

def jaro_similarity(s1: str, s2: str) -> float:
    """Hitung Jaro similarity antara dua string."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    return (matches / len1 + matches / len2 +
            (matches - transpositions / 2) / matches) / 3


def jaro_winkler(s1: str, s2: str, p: float = 0.1) -> float:
    """Hitung Jaro-Winkler similarity."""
    jaro = jaro_similarity(s1, s2)
    # Hitung common prefix (max 4 karakter)
    prefix = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return jaro + prefix * p * (1 - jaro)


# ── Manual Clusters ──────────────────────────────────────────────────────────
# Format: { canonical_name: [alias1, alias2, ...] }
# Alias yang PASTI merujuk ke entitas yang sama.

PERSON_CLUSTERS = {
    "Muhammad": [
        "Rasulullah", "Nabi Muhammad", "Muhammad SAW", "Nabi SAW",
        "Muhammad bin Abdullah",
    ],
    "Abu Bakar": [
        "Abu Bakar Ash-Shiddiq",
    ],
    "Umar bin Al-Khaththab": [
        "Umar", "Ibnul Khaththab",
    ],
    "Utsman bin Affan": [
        "Utsman",
    ],
    "Ali bin Abu Thalib": [
        "Ali", "Ali bin Abi Thalib",
    ],
    "Khadijah": [
        "Khadijah binti Khuwailid",
    ],
    "Hamzah bin Abdul Muththalib": [
        "Hamzah",
    ],
    "Zaid bin Haritsah": [
        "Zaid",
    ],
    "Bilal bin Rabah": [
        "Bilal",
    ],
    "Khalid bin Al-Walid": [
        "Khalid", "Khalid bin Walid",
    ],
    "Abu Sufyan bin Harb": [
        "Abu Sufyan", "Abu Sofyan",
    ],
    "Abu Jahal": [
        "Abu Jahl", "Abu Jahal bin Hisyam",
    ],
    "Najasyi": [
        "An-Najasyi",
    ],
    "Ka'b bin Al-Asyraf": [
        "Ibnul Asyraf",
    ],
    "Abdullah bin Ubay bin Salul": [
        "Abdullah bin Ubay",
    ],
    "Mush'ab bin Umair": [
        "Mush'ab",
    ],
    "Abdullah bin Rawahah": [
        "Ibnu Rawahah",
    ],
    "Al-Abbas bin Abdul Muththalib": [
        "Al-Abbas",
    ],
    "Waraqah bin Naufal": [
        "Waraqah", "Waraqah bin Naufal bin Asad bin Abdul Uzza",
    ],
    "Abu Dzar Al-Ghifari": [
        "Abu Dzar", "Abu Dzarr",
    ],
    "Utbah bin Rabi'ah": [
        "Utbah", "Utbah bin Rabi",
    ],
    "Usamah bin Zaid": [
        "Usamah",
    ],
    "As'ad bin Zurarah": [
        "As'ad",
    ],
    "Usaid bin Hudhair": [
        "Usaid",
    ],
    "Jabir bin Abdullah": [
        "Jabir",
    ],
    "Abu Ubaidah bin Al-Jarrah": [
        "Abu Ubaidah",
    ],
    "Sa'd bin Mu'adz": [
        "Sa'd bin Mua'dz", "Sa'd bin Mu'ad", "Sa'd bin Mu'",
    ],
    "Anas bin Malik": [
        # Tidak ada alias pendek karena "Anas" bisa ambigu
    ],
    "Mu'adz bin Jabal": [
        "Mu'adz",
    ],
    "Ka'b bin Malik": [
        "Ka'b",  # Ka'b tanpa bin biasanya merujuk Ka'b bin Malik
    ],
    "Ibnu Hisyam": [
        "Ibnu Hasyim",  # kemungkinan typo OCR
    ],
    "Khabbab bin Al-Aratt": [
        "Khabbab",
    ],
    "Sa'd bin Ubadah": [
        # "Sa'd" ambigu (banyak Sa'd), jadi tidak dialiaskan
    ],
    "Abdullah bin Mas'ud": [
        "Ibnu Mas'ud",
    ],
    "Abdullah bin Abbas": [
        "Ibnu Abbas",
    ],
    "Abdullah bin Umar": [
        "Ibnu Umar",
    ],
    "Ikrimah bin Abu Jahal": [
        "Ikrimah bin Abu Jahl",
    ],
    "Amr bin Al-Ash": [
        "Amru bin Al-Ash",
    ],
    "Az-Zubair bin Al-Awwam": [
        "Zubair bin Al-Awwam",
    ],
    "Isa bin Maryam": [
        "Isa",
    ],
    "Musa bin Imran": [
        "Musa",
    ],
    "Harun bin Imran": [
        "Harun",
    ],
    "Hasan bin Ali": [
        "Hasan",
    ],
    "Husain bin Ali": [
        "Husain",
    ],
    "Suhail bin Amr": [
        # tidak ada alias pendek
    ],
    "Sa'd bin Abu Waqqash": [
        "Sa'd bin Abi Waqqash",
    ],
    "Tsabit bin Qais bin Syammas": [
        "Tsabit bin Qaiz",
    ],
    "Ilyas bin Mudhar": [
        "Ilyas bin Mudha",
    ],
    "Abu Salamah bin Abdul Asad": [
        "Abu Salamah",
    ],
    "Shafiyyah binti Huyai bin Akhthab": [
        "Shafiyyah",
    ],
    "Ka'b bin Asad": [
        "Ka'b bin As'",
    ],
    "Abu Sufyan bin Al-Harits bin Abdul Muththalib": [
        "Abu Sufyan bin Al-Harits",
    ],
    "Abul Bakhtari bin Hisyam": [
        "Abul Bakhtari",
    ],
    "Rifa'ah bin Abdul Mundzir": [
        "Rifa'ah bin Abdul Mundzir bin Subair",
    ],
}

LOCATION_CLUSTERS = {
    "Tha'if": ["Thaif"],
    "Ka'bah": ["Baitullah"],
    "Yatsrib": ["Yastrib"],
}

EVENT_CLUSTERS = {
    "Perang Badr": ["Perang Badar"],
    "Fathul Makkah": ["Fathu Makkah", "Futuh Makkah", "Penaklukan Makkah"],
    "Perang Khandaq": ["Perang Ahzab", "Perang Al-Khandaq"],
    "Haji Wada'": ["Haji Wada"],
    "Baiat Aqabah Kubra": ["Baiat Aqabah Kedua"],
    "Isra' Mi'raj": ["Isra' dan Mi'raj"],
    # OCR artifacts: apostrophe hilang → nama terpotong
    "Perang Bu'ats": ["Perang Bu"],
    "Ghazwah Mu'tah": ["Ghazwah Mu"],
}


# ── EXCLUDE PAIRS — entitas yang mirip tapi BEDA orang/tempat ────────────────
# Mencegah false positive dari Jaro-Winkler
EXCLUDE_PAIRS = {
    # Beda orang bernama Sa'd
    ("Sa'd bin Mu'adz", "Sa'd bin Ubadah"),
    ("Sa'd bin Mu'adz", "Sa'd bin Abu Waqqash"),
    ("Sa'd bin Ubadah", "Sa'd bin Abu Waqqash"),
    ("Sa'd bin Mu'adz", "Sa'd bin Bakr"),
    ("Sa'd bin Mu'adz", "Sa'd bin Zaid"),
    ("Sa'd bin Mu'adz", "Sa'd bin Khaitsamah"),
    # Beda Abdullah
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Rawahah"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Mas'ud"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Abbas"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Umar"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Salam"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Jahsy"),
    ("Abdullah bin Ubay bin Salul", "Abdullah bin Jubair"),
    # Beda Amr
    ("Amr bin Al-Ash", "Amr bin Luhay"),
    ("Amr bin Al-Ash", "Amr bin Umayyah"),
    # Beda Abu
    ("Abu Bakar", "Abu Jahal"),
    ("Abu Bakar", "Abu Lahab"),
    ("Abu Bakar", "Abu Sufyan bin Harb"),
    ("Abu Bakar", "Abu Thalib"),
    ("Abu Bakar", "Abu Bakrah"),
    ("Abu Bakar", "Abu Bara'"),
    ("Abu Bakar", "Abu Bara"),
    ("Abu Sa'd", "Abu Sa'id"),
    ("Abu Sa'd", "Abu Said"),
    ("Abu Sa'd", "Abu Sa'ida"),
    # Beda Ka'b
    ("Ka'b bin Malik", "Ka'b bin Al-Asyraf"),
    ("Ka'b bin Malik", "Ka'b bin Asad"),
    ("Ka'b bin Malik", "Ka'b bin Zuhair"),
    # Beda Zaid
    ("Zaid bin Haritsah", "Zaid bin Tsabit"),
    ("Zaid bin Haritsah", "Zaid bin Arqam"),
    # Beda Zainab
    ("Zainab binti Jahsy", "Zainab binti Khuzaimah"),
    # Beda Umayyah
    ("Umayyah bin Khalaf", "Shafwan bin Umayyah"),
    # Beda Muhammad
    ("Muhammad", "Muhammad bin Maslamah"),
    ("Muhammad", "Muhammad bin Abdul Wahhab"),
    ("Muhammad bin Abdullah", "Muhammad bin Abdul Wahhab"),
    ("Muhammad bin Abdullah", "Muhammad bin Maslamah"),
    # Beda Al-Abbas / Al-Aswad
    ("Al-Abbas bin Abdul Muththalib", "Al-Aswad bin Abdul Muththalib"),
    ("Al-Abbas", "Al-Aswad bin Abdul Muththalib"),
    ("Al-Abbas", "Al-Aswad bin Al-Muththalib"),
    ("Al-Abbas bin Al-Muththalib", "Al-Aswad bin Al-Muththalib"),
    ("Al-Abbas bin Abdul Muthalib", "Al-Aswad bin Abdul Muththalib"),
    # Beda Abdullah bin Abu X
    ("Abdullah bin Abu Rabi'ah", "Abdullah bin Abu Umayyah"),
    ("Abdullah bin Abu Rabi'ah", "Abdullah bin Umayyah"),
    # Beda Asad / As'ad (nama Arab berbeda)
    ("Asad bin Khuzaimah", "As'ad bin Khuzaimah"),
    # Beda perang
    ("Perang Badr", "Perang Badr Shughra"),
    ("Perang Badr", "Perang Badr Kubra"),
    ("Perang Badr", "Perang Buwath"),
    ("Perang Badr Kubra", "Perang Badr Shughra"),
    ("Perang Uhud", "Perang Hunain"),
    ("Perang Khaibar", "Perang Khandaq"),
    ("Perang Bu'ats", "Perang Buwath"),
}


def _is_excluded(name_a: str, name_b: str) -> bool:
    """Cek apakah pasangan nama ada di EXCLUDE_PAIRS."""
    return (name_a, name_b) in EXCLUDE_PAIRS or (name_b, name_a) in EXCLUDE_PAIRS


# ── Build alias map ──────────────────────────────────────────────────────────

def build_alias_map(df: pd.DataFrame) -> dict:
    """
    Bangun mapping {entity_text → canonical_name} dari:
    1. Manual clusters (pasti benar)
    2. Pattern matching (nama pendek ⊂ nama panjang)
    3. Jaro-Winkler (variasi ejaan)
    """
    alias_map = {}
    cluster_info = defaultdict(lambda: {"canonical": "", "members": set(), "method": ""})

    # Hitung frekuensi per (entity_text, label)
    freq = df.groupby(["entity_text", "label"]).size().reset_index(name="count")

    # ── Tahap 1: Manual clusters ──
    manual_clusters = {
        "PERSON": PERSON_CLUSTERS,
        "LOCATION": LOCATION_CLUSTERS,
        "EVENT": EVENT_CLUSTERS,
    }

    for label, clusters in manual_clusters.items():
        for canonical, aliases in clusters.items():
            # Canonical → dirinya sendiri
            alias_map[f"{label}::{canonical}"] = canonical
            cluster_info[f"{label}::{canonical}"]["canonical"] = canonical
            cluster_info[f"{label}::{canonical}"]["members"].add(canonical)
            cluster_info[f"{label}::{canonical}"]["method"] = "manual"
            for alias in aliases:
                alias_map[f"{label}::{alias}"] = canonical
                cluster_info[f"{label}::{canonical}"]["members"].add(alias)

    # ── Tahap 2: Jaro-Winkler (variasi ejaan) ──
    # Hanya untuk mendeteksi typo/OCR artifact, BUKAN untuk mengelompokkan nama berbeda.
    # Aturan ketat:
    #   - Threshold tinggi (0.90)
    #   - Skip jika "bin/binti" mengarah ke patronymic berbeda
    #   - Skip jika compound prefix (Abu/Ummu/Ibnu) diikuti kata berbeda
    _COMPOUND_RE = re.compile(r"^(?:Abu|Abul|Ummu|Ibnu|Ibnul)\s+(.+)")

    def _get_distinctive_part(name: str) -> str:
        """Ambil bagian pembeda dari nama (setelah compound prefix)."""
        m = _COMPOUND_RE.match(name)
        return m.group(1) if m else name

    def _get_patronymic(name: str) -> str:
        """Ambil bagian setelah 'bin/binti' pertama."""
        parts = re.split(r"\s+(?:bin|binti)\s+", name, maxsplit=1)
        return parts[1] if len(parts) > 1 else ""

    for label in ["PERSON", "EVENT", "LOCATION"]:
        label_entities = freq[freq["label"] == label].copy()
        names = sorted(label_entities["entity_text"].tolist())

        for i, name_a in enumerate(names):
            key_a = f"{label}::{name_a}"
            canon_a = alias_map.get(key_a, name_a)

            for j in range(i + 1, len(names)):
                name_b = names[j]
                key_b = f"{label}::{name_b}"
                canon_b = alias_map.get(key_b, name_b)

                # Skip jika sudah di-cluster sama
                if canon_a == canon_b:
                    continue

                # Skip excluded pairs
                if _is_excluded(name_a, name_b) or _is_excluded(canon_a, canon_b):
                    continue

                # Guard: jika keduanya compound prefix (Abu X vs Abu Y),
                # cek bagian pembeda — harus very similar
                dist_a = _get_distinctive_part(name_a)
                dist_b = _get_distinctive_part(name_b)
                if dist_a != name_a and dist_b != name_b:
                    # Keduanya punya compound prefix
                    if jaro_winkler(dist_a, dist_b) < 0.90:
                        continue

                # Guard: jika keduanya punya bin/binti, patronymic harus mirip
                pat_a = _get_patronymic(name_a)
                pat_b = _get_patronymic(name_b)
                if pat_a and pat_b:
                    if jaro_winkler(pat_a, pat_b) < 0.85:
                        continue
                # Guard: jika satu punya bin/binti dan satu tidak, skip
                # (beda level spesifisitas = kemungkinan beda orang)
                elif pat_a or pat_b:
                    continue

                # Guard: panjang nama tidak boleh beda terlalu jauh (maks 20%)
                len_ratio = min(len(name_a), len(name_b)) / max(len(name_a), len(name_b))
                if len_ratio < 0.80:
                    continue

                sim = jaro_winkler(name_a, name_b)
                if sim >= JW_THRESHOLD:
                    # Pilih yang frekuensi lebih tinggi sebagai canonical
                    freq_a = freq[(freq["entity_text"] == name_a) & (freq["label"] == label)]["count"].sum()
                    freq_b = freq[(freq["entity_text"] == name_b) & (freq["label"] == label)]["count"].sum()

                    if freq_a >= freq_b:
                        canonical = canon_a
                        alias_map[key_b] = canonical
                        cluster_info[f"{label}::{canonical}"]["members"].add(name_b)
                    else:
                        canonical = canon_b
                        alias_map[key_a] = canonical
                        cluster_info[f"{label}::{canonical}"]["members"].add(name_a)

                    cluster_info[f"{label}::{canonical}"]["canonical"] = canonical
                    cluster_info[f"{label}::{canonical}"]["members"].add(name_a)
                    cluster_info[f"{label}::{canonical}"]["members"].add(name_b)
                    if not cluster_info[f"{label}::{canonical}"]["method"]:
                        cluster_info[f"{label}::{canonical}"]["method"] = "jaro-winkler"

    return alias_map, dict(cluster_info)


def resolve_alias(entity_text: str, label: str, alias_map: dict) -> str:
    """Resolve nama entitas ke bentuk kanonik."""
    key = f"{label}::{entity_text}"
    return alias_map.get(key, entity_text)


# ── Output ───────────────────────────────────────────────────────────────────

def generate_report(alias_map: dict, cluster_info: dict, df: pd.DataFrame) -> str:
    """Generate laporan alias clusters dalam markdown."""
    lines = []
    lines.append("# Alias Clusters — Sirah Nabawiyah")
    lines.append("")
    lines.append("Auto-generated oleh `alias_clustering.py`. Review sebelum dipakai di Neo4j.")
    lines.append("")

    # Hitung frekuensi
    freq = df.groupby(["entity_text", "label"]).size().reset_index(name="count")
    freq_dict = {}
    for _, row in freq.iterrows():
        freq_dict[(row["entity_text"], row["label"])] = row["count"]

    # Statistik
    n_mapped = sum(1 for k, v in alias_map.items() if k.split("::", 1)[1] != v)
    lines.append(f"**Total entity text yang di-alias:** {n_mapped}")
    lines.append("")

    # Per label
    for label in ["PERSON", "LOCATION", "EVENT", "TIME"]:
        clusters = {}
        for key, info in cluster_info.items():
            if key.startswith(f"{label}::") and len(info["members"]) > 1:
                clusters[key] = info

        if not clusters:
            continue

        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## {label} ({len(clusters)} clusters)")
        lines.append("")

        # Sort clusters by total frequency
        sorted_clusters = sorted(
            clusters.items(),
            key=lambda x: sum(freq_dict.get((m, label), 0) for m in x[1]["members"]),
            reverse=True,
        )

        for i, (key, info) in enumerate(sorted_clusters, 1):
            canonical = info["canonical"]
            method = info["method"]
            members = sorted(info["members"], key=lambda m: -freq_dict.get((m, label), 0))

            total_freq = sum(freq_dict.get((m, label), 0) for m in members)
            lines.append(f"### {i}. {canonical} (total: {total_freq}x) [{method}]")

            for m in members:
                f = freq_dict.get((m, label), 0)
                marker = " **← canonical**" if m == canonical else ""
                lines.append(f"  - `{m}` ({f}x){marker}")
            lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("ALIAS CLUSTERING — Sirah Nabawiyah")
    print("=" * 60)

    # 1. Load data
    print("\n[1/4] Loading data...")
    df = pd.read_csv(IN_CSV, sep=";", encoding="utf-8-sig").fillna("")
    df["entity_text"] = df["entity_text"].astype(str).str.strip()
    df = df[df["entity_text"] != ""]
    print(f"  {len(df)} rows, {df['entity_text'].nunique()} unique entities")

    # 2. Build alias map
    print("\n[2/4] Building alias clusters...")
    alias_map, cluster_info = build_alias_map(df)

    n_mapped = sum(1 for k, v in alias_map.items() if k.split("::", 1)[1] != v)
    n_clusters = sum(1 for info in cluster_info.values() if len(info["members"]) > 1)
    print(f"  {n_mapped} entities mapped ke alias")
    print(f"  {n_clusters} clusters ditemukan")

    # 3. Simpan alias_map.json
    print("\n[3/4] Saving alias map...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Simpan versi bersih (tanpa prefix label::)
    clean_map = {}
    for key, canonical in alias_map.items():
        label, name = key.split("::", 1)
        if name != canonical:  # hanya simpan yang berubah
            if label not in clean_map:
                clean_map[label] = {}
            clean_map[label][name] = canonical

    OUT_JSON.write_text(json.dumps(clean_map, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved to: {OUT_JSON}")

    # 4. Generate report
    print("\n[4/4] Generating report...")
    report = generate_report(alias_map, cluster_info, df)
    OUT_MD.write_text(report, encoding="utf-8")
    print(f"  Saved to: {OUT_MD}")

    # Ringkasan per label
    print(f"\nRingkasan:")
    for label in ["PERSON", "LOCATION", "EVENT", "TIME"]:
        label_map = clean_map.get(label, {})
        print(f"  {label}: {len(label_map)} alias -> canonical")


if __name__ == "__main__":
    main()
