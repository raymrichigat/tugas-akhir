"""
Relation Extraction dari Data Pre-Labelled Sirah Nabawiyah
Menghasilkan nodes.csv dan edges.csv untuk konstruksi Knowledge Graph di Neo4j.

Input : sirah_prelabelled.csv (entitas hasil pre-labelling)
Output: nodes.csv  - daftar entitas unik (node)
        edges.csv  - daftar relasi antar entitas (edge)
"""

import re
import json
import hashlib
import pandas as pd
from pathlib import Path
from collections import defaultdict

from period_mapping import (
    load_toc, build_event_period_map,
    compute_proximity_score, compute_period_score, compute_relation_weight,
    is_in_primary_period,
)

# ── Konfigurasi Path ─────────────────────────────────────────────────────────
BASE_DIR = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_PRELABELLED = BASE_DIR / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
IN_ALIAS_MAP = BASE_DIR / "data" / "result" / "alias_clustering" / "alias_map.json"
OUT_DIR = BASE_DIR / "data" / "result" / "relation_result"
OUT_NODES = OUT_DIR / "nodes.csv"
OUT_EDGES = OUT_DIR / "edges.csv"


# ── Alias Normalisasi ────────────────────────────────────────────────────────

def load_alias_map(filepath: Path) -> dict:
    """Load alias map dari alias_clustering.py output."""
    if not filepath.exists():
        print(f"  WARNING: {filepath} tidak ditemukan, pakai tanpa alias")
        return {}
    data = json.loads(filepath.read_text(encoding="utf-8"))
    # Flatten: {label: {name: canonical}} → {label::name: canonical}
    flat = {}
    for label, mapping in data.items():
        for name, canonical in mapping.items():
            flat[f"{label}::{name}"] = canonical
    return flat


def normalize_name(text, label, alias_map):
    """Normalisasi nama entitas ke bentuk kanonik menggunakan alias map."""
    if not isinstance(text, str):
        return str(text).strip()

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    key = f"{label}::{text}"
    return alias_map.get(key, text)


def generate_node_id(name, label):
    """Generate ID unik untuk node berdasarkan nama dan label."""
    key = f"{label}::{name}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


# ── Proximity & Context ─────────────────────────────────────────────────────

def split_into_sentences(text):
    """Pecah teks menjadi kalimat berdasarkan tanda baca akhir."""
    if not isinstance(text, str):
        return []
    # Split di titik, tanda tanya, tanda seru
    # Tetapi hindari split di singkatan umum (Mr., Dr., dll)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def get_sentence_at_position(text, pos):
    """Dapatkan kalimat yang mengandung posisi karakter tertentu."""
    sentences = split_into_sentences(text)
    current_pos = 0
    for sent in sentences:
        sent_start = text.find(sent, current_pos)
        if sent_start == -1:
            continue
        sent_end = sent_start + len(sent)
        if sent_start <= pos < sent_end:
            return sent, sent_start, sent_end
        current_pos = sent_end
    return text, 0, len(text)


def are_in_same_context(ent1_start, ent1_end, ent2_start, ent2_end, text, max_distance=200):
    """
    Cek apakah dua entitas berada dalam konteks yang sama:
    1. Dalam kalimat yang sama, ATAU
    2. Dalam jarak < max_distance karakter
    """
    # Cek kalimat yang sama
    sent1, _, _ = get_sentence_at_position(text, ent1_start)
    sent2, _, _ = get_sentence_at_position(text, ent2_start)
    if sent1 == sent2:
        return True

    # Cek kedekatan posisi
    # Hitung jarak antara ujung terdekat kedua entitas
    distance = min(
        abs(ent1_start - ent2_end),
        abs(ent2_start - ent1_end),
    )
    return distance < max_distance


def extract_evidence(text, ent1_start, ent1_end, ent2_start, ent2_end, context_window=50):
    """Ekstrak cuplikan teks yang mengandung kedua entitas sebagai bukti relasi."""
    start = max(0, min(ent1_start, ent2_start) - context_window)
    end = min(len(text), max(ent1_end, ent2_end) + context_window)

    evidence = text[start:end].strip()
    # Tambahkan ellipsis jika terpotong
    if start > 0:
        evidence = "..." + evidence
    if end < len(text):
        evidence = evidence + "..."

    return evidence


# ── Contextual Guards ──────────────────────────────────────────────────────
# Menyaring false positive dari proximity-based extraction
# dengan mengecek evidence teks di sekitar entitas.

# Perawi/penulis kitab yang BUKAN tokoh sejarah Sirah
KNOWN_NARRATORS = {
    "Ibnu Hisyam", "Ibnu Ishaq", "Ath-Thabari", "An-Nawawi",
    "Ibnul Qayyim", "Al-Khadhri", "Abu Dawud", "Ibnu Sa'd",
    "Al-Waqidi",
}

# Pola-pola INVALID untuk OCCURRED_AT (lokasi bukan tempat kejadian)
_OCCURRED_AT_INVALID_PATTERNS = [
    r"wakil\s+(?:beliau\s+)?di\s+{loc}",
    r"(?:kembali|pulang)\s+(?:lagi\s+)?ke\s+{loc}",
    r"kepulangan\s+.*?ke\s+{loc}",
    r"keluar\s+dari\s+{loc}",
    r"penduduk\s+{loc}",
    r"(?:berangkat|berasal)\s+dari\s+(?:\w+\s+){{0,2}}{loc}",
    r"berpencar\s+ke\s+{loc}",
    r"datang\s+ke\s+{loc}",
    r"pergi\s+(?:.*?\s+)?ke\s+{loc}",
    r"di\s+{loc}\s+dulu",
    r"orang-orang\s+(?:musyrik|kafir|munafik)\s+{loc}",
    r"raja-raja\s+{loc}",
    r"(?:tinggal|menetap)\s+(?:.*?\s+)?di\s+{loc}",
    r"membeli\s+.*?di\s+{loc}",
    r"menyerang\s+(?:pinggiran\s+)?{loc}",
    r"(?:harta\s+rampasan|ghanimah).*?(?:adalah|yaitu)\s+{loc}",
    r"(?:seluruh|di\s+seluruh)\s+{loc}",
    r"antara\s+\w[\w\s]*?dan\s+{loc}",
    r"(?:masuk|melarikan\s+diri|pelarian.*?masuk)\s+ke\s+{loc}",
    r"menuju\s+(?:ke\s+)?{loc}",
    r"(?:langit|ufuk)\s+{loc}",
    r"surat\s+dari\s+.*?{loc}",
    r"bergabung\s+dengan\s+{loc}",
    r"tiba\s+di\s+{loc}",
    r"sedang\s+berada\s+di\s+{loc}",
    r"sepulang\s+(?:.*?\s+)?dari\s+{loc}",
    r"sekembalinya\s+dari\s+{loc}",
    r"perjalanan\s+pulang\s+ke\s+{loc}",
    r"bergerak\s+ke\s+arah\s+.*?{loc}",
    r"(?:setelah|sejak|sebelum)\s+(?:perang\s+)?(?:penaklukan|penaklukkan)\s+{loc}",
    r"yang\s+berada\s+di\s+{loc}",
    r"(?:dalam\s+)?(?:penaklukkan|penaklukan)\s+{loc}",
]

# Pola-pola INVALID untuk OCCURRED_ON (waktu bukan waktu event)
_OCCURRED_ON_INVALID_PATTERNS = [
    r"(?:kembali|pulang|kepulangan)\s+.*?(?:pada|akhir)\s+.*?{time}",
    r"meninggal\s+(?:dunia\s+)?(?:pada|di)\s+.*?{time}",
    r"(?:setelah|seusai|sesudah|sepulang)\s+.*?(?:pada|di)\s+.*?{time}",
]


def is_invalid_involved_in(person_name, evidence):
    """Cek apakah PERSON benar-benar terlibat dalam EVENT.
    Returns True jika relasi INVALID (harus di-skip)."""

    # 1. Known narrators/penulis kitab
    if person_name in KNOWN_NARRATORS:
        return True

    # 2. Referensi ayat Al-Quran: "(Yusuf: 90)"
    if re.search(r"\(\s*" + re.escape(person_name) + r"\s*:\s*\d+\s*\)", evidence):
        return True

    # 3. Disebutkan meninggal dunia (bukan partisipasi event)
    if re.search(re.escape(person_name) + r"\s+(?:ini\s+)?meninggal\s+dunia", evidence):
        return True

    return False


# Variasi ejaan lokasi yang sering muncul dalam teks
_SPELLING_VARIANTS = {
    "Yatsrib": ["Yastrib"],
    "Yastrib": ["Yatsrib"],
}


def _get_loc_variants(loc_name):
    """Dapatkan variasi ejaan lokasi."""
    variants = [loc_name]
    if loc_name in _SPELLING_VARIANTS:
        variants.extend(_SPELLING_VARIANTS[loc_name])
    return variants


def is_invalid_occurred_at(event_name, loc_name, evidence):
    """Cek apakah LOCATION benar-benar tempat kejadian EVENT.
    Returns True jika relasi INVALID (harus di-skip)."""

    # Nama event mengandung lokasi → selalu valid
    if loc_name.lower() in event_name.lower():
        return False

    # Event adalah penaklukan lokasi ini → valid
    if re.search(r"(?:Fath|fath|penakluk)", event_name, re.IGNORECASE):
        for loc_v in _get_loc_variants(loc_name):
            loc_esc = re.escape(loc_v)
            if re.search(rf"(?:penaklukkan|penaklukan|menaklukkan)\s+{loc_esc}",
                         evidence, re.IGNORECASE):
                return False

    # Cek pola-pola invalid (coba semua variasi ejaan)
    for loc_v in _get_loc_variants(loc_name):
        loc_esc = re.escape(loc_v)
        for pattern in _OCCURRED_AT_INVALID_PATTERNS:
            pat = pattern.replace("{loc}", loc_esc)
            if re.search(pat, evidence, re.IGNORECASE):
                return True

    return False


def is_invalid_occurred_on(event_name, time_name, evidence):
    """Cek apakah TIME benar-benar waktu EVENT.
    Returns True jika relasi INVALID (harus di-skip)."""
    time_esc = re.escape(time_name)
    for pattern in _OCCURRED_ON_INVALID_PATTERNS:
        pat = pattern.replace("{time}", time_esc)
        if re.search(pat, evidence, re.IGNORECASE):
            return True
    return False


# ── Person-Person Relation Patterns ───────────────────────────────────────────

KELUARGA_PATTERNS = [
    (r"(?:putra|puteri|anak)\s+(?:dari\s+)?{person}", "anak"),
    (r"{person}\s+(?:bin|binti|ibnu)\s+", "anak"),
    (r"(?:ayah|bapak|ibu|ibunda)\s+(?:dari\s+)?{person}", "orangtua"),
    (r"(?:istri|suami|isteri)\s+(?:dari\s+)?{person}", "pasangan"),
    (r"(?:menikah|menikahi|mengawini)\s+(?:dengan\s+)?{person}", "pasangan"),
    (r"(?:saudara|saudari|adik|kakak)\s+(?:dari\s+)?{person}", "saudara"),
    (r"(?:paman|bibi)\s+(?:dari\s+)?{person}", "paman/bibi"),
    (r"(?:cucu|keponakan)\s+(?:dari\s+)?{person}", "cucu/keponakan"),
]

SAHABAT_PATTERNS = [
    (r"(?:sahabat|teman)\s+(?:dekat\s+)?(?:dari\s+)?{person}", "sahabat"),
    (r"(?:membela|menolong|mendukung|membantu)\s+{person}", "sekutu"),
    (r"(?:bersama|bersekutu|bergabung)\s+(?:dengan\s+)?{person}", "sekutu"),
    (r"(?:setia|loyal)\s+(?:kepada|terhadap)\s+{person}", "sahabat"),
]

MUSUH_PATTERNS = [
    (r"(?:musuh|lawan|penentang)\s+(?:dari\s+)?{person}", "musuh"),
    (r"(?:memerangi|menyerang|melawan|membunuh)\s+{person}", "musuh"),
    (r"(?:menentang|memusuhi|membenci)\s+{person}", "musuh"),
    (r"(?:berperang|bertempur)\s+(?:melawan\s+)?{person}", "musuh"),
]


def _spans_overlap(start1, end1, start2, end2):
    """Cek apakah dua span overlap (bagian dari satu nama)."""
    return start1 < end2 and start2 < end1


def is_invalid_person_person(person1_name, person2_name, evidence):
    """Cek apakah relasi Person-Person invalid.
    Returns True jika harus di-skip."""

    # 1. Sama canonical name
    if person1_name == person2_name:
        return True

    # 2. Known narrators
    if person1_name in KNOWN_NARRATORS or person2_name in KNOWN_NARRATORS:
        return True

    # 3. Satu adalah substring dari yang lain (misalnya "Abu Bakar" dan "Abu Bakar Ash-Shiddiq")
    if person1_name in person2_name or person2_name in person1_name:
        return True

    return False


def _match_person_person_pattern(text, person_name, patterns):
    """Cek apakah teks mengandung pola relasi dengan person tertentu.
    Returns: (relation_type, subtype) atau None."""
    p_esc = re.escape(person_name)
    for pattern_template, subtype in patterns:
        pattern = pattern_template.replace("{person}", p_esc)
        if re.search(pattern, text, re.IGNORECASE):
            return subtype
    return None


def build_person_person_relations(df):
    """
    Bangun relasi Person↔Person dari co-occurrence + pattern matching.
    Returns: list of relation dicts.
    """
    relations = []
    grouped = df.groupby("chunk_id")

    for chunk_id, chunk_df in grouped:
        chunk_text = chunk_df.iloc[0].get("teks_chunk", "")
        halaman = chunk_df.iloc[0].get("halaman", "")

        persons = chunk_df[chunk_df["label"] == "PERSON"]
        if len(persons) < 2:
            continue

        person_list = persons.to_dict("records")

        for i in range(len(person_list)):
            for j in range(i + 1, len(person_list)):
                p1 = person_list[i]
                p2 = person_list[j]

                # Skip jika span overlap (bagian dari satu nama panjang)
                if _spans_overlap(p1["start_char"], p1["end_char"],
                                  p2["start_char"], p2["end_char"]):
                    continue

                # Skip invalid pairs
                if is_invalid_person_person(p1["canonical_name"], p2["canonical_name"],
                                            chunk_text):
                    continue

                # Cek proximity
                if not are_in_same_context(p1["start_char"], p1["end_char"],
                                           p2["start_char"], p2["end_char"],
                                           chunk_text, max_distance=150):
                    continue

                evidence = extract_evidence(
                    chunk_text, p1["start_char"], p1["end_char"],
                    p2["start_char"], p2["end_char"]
                )

                # Coba match pattern untuk menentukan tipe relasi
                matched = False

                # Cek KELUARGA
                for person_a, person_b in [(p1, p2), (p2, p1)]:
                    subtype = _match_person_person_pattern(
                        evidence, person_b["canonical_name"], KELUARGA_PATTERNS
                    )
                    if subtype:
                        relations.append({
                            "source_name": person_a["canonical_name"],
                            "source_label": "PERSON",
                            "relation_type": "KELUARGA",
                            "relation_subtype": subtype,
                            "target_name": person_b["canonical_name"],
                            "target_label": "PERSON",
                            "chunk_id": chunk_id,
                            "evidence": evidence,
                            "halaman": halaman,
                        })
                        matched = True
                        break

                if matched:
                    continue

                # Cek SAHABAT
                for person_a, person_b in [(p1, p2), (p2, p1)]:
                    subtype = _match_person_person_pattern(
                        evidence, person_b["canonical_name"], SAHABAT_PATTERNS
                    )
                    if subtype:
                        relations.append({
                            "source_name": person_a["canonical_name"],
                            "source_label": "PERSON",
                            "relation_type": "SAHABAT",
                            "relation_subtype": subtype,
                            "target_name": person_b["canonical_name"],
                            "target_label": "PERSON",
                            "chunk_id": chunk_id,
                            "evidence": evidence,
                            "halaman": halaman,
                        })
                        matched = True
                        break

                if matched:
                    continue

                # Cek MUSUH
                for person_a, person_b in [(p1, p2), (p2, p1)]:
                    subtype = _match_person_person_pattern(
                        evidence, person_b["canonical_name"], MUSUH_PATTERNS
                    )
                    if subtype:
                        relations.append({
                            "source_name": person_a["canonical_name"],
                            "source_label": "PERSON",
                            "relation_type": "MUSUH",
                            "relation_subtype": subtype,
                            "target_name": person_b["canonical_name"],
                            "target_label": "PERSON",
                            "chunk_id": chunk_id,
                            "evidence": evidence,
                            "halaman": halaman,
                        })
                        break

    print(f"  Person-Person relations found: {len(relations)}")
    return relations


# ── Event-Event Chronology ────────────────────────────────────────────────────

def build_event_chronology(nodes_df, event_period_map):
    """
    Bangun relasi PRECEDES antar EVENT berdasarkan urutan BAB (kronologis).

    1. Ambil EVENT nodes yang punya mapped BAB
    2. Sort by page_start BAB
    3. Event berurutan → relasi PRECEDES
    4. Filter: hanya event dengan frequency >= 2
    """
    relations = []

    # Ambil EVENT nodes yang ter-mapped dan frequent
    event_nodes = nodes_df[nodes_df["label"] == "EVENT"].copy()
    event_nodes = event_nodes[event_nodes["frequency"] >= 2]

    chronological_events = []
    for _, event in event_nodes.iterrows():
        period = event_period_map.get(event["name"])
        if period is not None:
            chronological_events.append({
                "name": event["name"],
                "page_start": period["page_start"],
                "bab_title": period["bab_title"],
            })

    # Sort by page_start (kronologis)
    chronological_events.sort(key=lambda x: x["page_start"])

    # Deduplicate: jangan hubungkan event dari BAB yang sama
    seen_bab_starts = set()
    unique_events = []
    for ev in chronological_events:
        if ev["page_start"] not in seen_bab_starts:
            unique_events.append(ev)
            seen_bab_starts.add(ev["page_start"])

    # Bangun relasi PRECEDES
    for i in range(len(unique_events) - 1):
        ev_a = unique_events[i]
        ev_b = unique_events[i + 1]

        relations.append({
            "source_name": ev_a["name"],
            "source_label": "EVENT",
            "relation_type": "PRECEDES",
            "relation_subtype": "",
            "target_name": ev_b["name"],
            "target_label": "EVENT",
            "chunk_id": "",
            "evidence": f"{ev_a['name']} (BAB: {ev_a['bab_title']}) -> {ev_b['name']} (BAB: {ev_b['bab_title']})",
            "halaman": f"{ev_a['page_start']}",
        })

    print(f"  Event chronology relations: {len(relations)}")
    return relations


# ── Main Pipeline ────────────────────────────────────────────────────────────

def load_and_prepare_data(filepath, alias_map):
    """Load CSV pre-labelled dan siapkan data."""
    df = pd.read_csv(filepath, sep=";", encoding="utf-8-sig")
    df.columns = df.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip()

    # Filter baris yang punya label valid
    valid_labels = {"PERSON", "EVENT", "LOCATION", "TIME"}
    df = df[df["label"].isin(valid_labels)].copy()

    # Konversi start_char dan end_char ke integer
    df["start_char"] = pd.to_numeric(df["start_char"], errors="coerce").fillna(0).astype(int)
    df["end_char"] = pd.to_numeric(df["end_char"], errors="coerce").fillna(0).astype(int)

    # Normalisasi nama entitas menggunakan alias map
    df["canonical_name"] = df.apply(
        lambda row: normalize_name(row["entity_text"], row["label"], alias_map), axis=1
    )

    # Statistik alias resolution
    n_resolved = (df["entity_text"] != df["canonical_name"]).sum()

    print(f"Data loaded: {len(df)} entitas valid")
    print(f"Alias resolved: {n_resolved} entitas")
    print(f"Distribusi label:")
    for label, count in df["label"].value_counts().items():
        n_unique = df[df["label"] == label]["canonical_name"].nunique()
        print(f"  {label}: {count} mentions, {n_unique} unique (setelah alias)")

    return df


def build_relations(df):
    """Bentuk relasi antar entitas berdasarkan chunk."""
    relations = []
    chunks_with_events = 0
    chunks_without_events = 0

    # Kelompokkan entitas per chunk
    grouped = df.groupby("chunk_id")

    for chunk_id, chunk_df in grouped:
        # Ambil teks chunk (sama untuk semua baris di chunk)
        chunk_text = chunk_df.iloc[0].get("teks_chunk", "")
        halaman = chunk_df.iloc[0].get("halaman", "")

        # Pisahkan entitas berdasarkan label
        events = chunk_df[chunk_df["label"] == "EVENT"]
        persons = chunk_df[chunk_df["label"] == "PERSON"]
        locations = chunk_df[chunk_df["label"] == "LOCATION"]
        times = chunk_df[chunk_df["label"] == "TIME"]

        if len(events) == 0:
            chunks_without_events += 1
            continue

        chunks_with_events += 1

        for _, event in events.iterrows():
            ev_start = event["start_char"]
            ev_end = event["end_char"]
            ev_name = event["canonical_name"]

            # PERSON → EVENT (INVOLVED_IN)
            for _, person in persons.iterrows():
                p_start = person["start_char"]
                p_end = person["end_char"]

                if are_in_same_context(p_start, p_end, ev_start, ev_end, chunk_text):
                    evidence = extract_evidence(
                        chunk_text, p_start, p_end, ev_start, ev_end
                    )
                    # Guard: filter perawi, ayat, kematian
                    if is_invalid_involved_in(person["canonical_name"], evidence):
                        continue
                    prox_score = compute_proximity_score(
                        p_start, p_end, ev_start, ev_end, chunk_text
                    )
                    relations.append({
                        "source_name": person["canonical_name"],
                        "source_label": "PERSON",
                        "relation_type": "INVOLVED_IN",
                        "relation_subtype": "",
                        "target_name": ev_name,
                        "target_label": "EVENT",
                        "chunk_id": chunk_id,
                        "evidence": evidence,
                        "halaman": halaman,
                        "proximity_score": prox_score,
                    })

            # EVENT → LOCATION (OCCURRED_AT)
            for _, location in locations.iterrows():
                l_start = location["start_char"]
                l_end = location["end_char"]

                if are_in_same_context(ev_start, ev_end, l_start, l_end, chunk_text):
                    evidence = extract_evidence(
                        chunk_text, ev_start, ev_end, l_start, l_end
                    )
                    # Guard: filter lokasi yang bukan tempat kejadian
                    if is_invalid_occurred_at(ev_name, location["canonical_name"], evidence):
                        continue
                    prox_score = compute_proximity_score(
                        ev_start, ev_end, l_start, l_end, chunk_text
                    )
                    relations.append({
                        "source_name": ev_name,
                        "source_label": "EVENT",
                        "relation_type": "OCCURRED_AT",
                        "relation_subtype": "",
                        "target_name": location["canonical_name"],
                        "target_label": "LOCATION",
                        "chunk_id": chunk_id,
                        "evidence": evidence,
                        "halaman": halaman,
                        "proximity_score": prox_score,
                    })

            # EVENT → TIME (OCCURRED_ON)
            for _, time in times.iterrows():
                t_start = time["start_char"]
                t_end = time["end_char"]

                if are_in_same_context(ev_start, ev_end, t_start, t_end, chunk_text):
                    evidence = extract_evidence(
                        chunk_text, ev_start, ev_end, t_start, t_end
                    )
                    # Guard: filter waktu yang bukan waktu event
                    if is_invalid_occurred_on(ev_name, time["canonical_name"], evidence):
                        continue
                    prox_score = compute_proximity_score(
                        ev_start, ev_end, t_start, t_end, chunk_text
                    )
                    relations.append({
                        "source_name": ev_name,
                        "source_label": "EVENT",
                        "relation_type": "OCCURRED_ON",
                        "relation_subtype": "",
                        "target_name": time["canonical_name"],
                        "target_label": "TIME",
                        "chunk_id": chunk_id,
                        "evidence": evidence,
                        "halaman": halaman,
                        "proximity_score": prox_score,
                    })

    print(f"\nChunks dengan EVENT: {chunks_with_events}")
    print(f"Chunks tanpa EVENT : {chunks_without_events}")
    print(f"Total relasi mentah: {len(relations)}")

    return relations


def deduplicate_relations(relations, event_period_map=None):
    """
    Deduplikasi relasi:
    Jika source, target, dan relation_type sama, gabungkan evidence dan chunk_id.
    Hitung weight dari max(proximity_score) + period_score.
    """
    if event_period_map is None:
        event_period_map = {}

    dedup = {}

    for rel in relations:
        key = (rel["source_name"], rel["source_label"],
               rel["relation_type"],
               rel["target_name"], rel["target_label"])

        if key not in dedup:
            dedup[key] = {
                "source_name": rel["source_name"],
                "source_label": rel["source_label"],
                "relation_type": rel["relation_type"],
                "relation_subtype": rel.get("relation_subtype", ""),
                "target_name": rel["target_name"],
                "target_label": rel["target_label"],
                "chunk_ids": [rel["chunk_id"]] if rel["chunk_id"] else [],
                "evidences": [rel["evidence"]],
                "halaman": [str(rel["halaman"])] if rel.get("halaman") else [],
                "proximity_scores": [rel.get("proximity_score", 0.3)],
            }
        else:
            if rel["chunk_id"] and rel["chunk_id"] not in dedup[key]["chunk_ids"]:
                dedup[key]["chunk_ids"].append(rel["chunk_id"])
                dedup[key]["evidences"].append(rel["evidence"])
            if rel.get("halaman") and str(rel["halaman"]) not in dedup[key]["halaman"]:
                dedup[key]["halaman"].append(str(rel["halaman"]))
            dedup[key]["proximity_scores"].append(rel.get("proximity_score", 0.3))
            # Update relation_subtype jika belum ada
            if not dedup[key]["relation_subtype"] and rel.get("relation_subtype"):
                dedup[key]["relation_subtype"] = rel["relation_subtype"]

    # Flatten ke list of dicts + hitung weight
    result = []
    for key, val in dedup.items():
        # Best proximity score dari semua occurrences
        best_proximity = max(val["proximity_scores"]) if val["proximity_scores"] else 0.3

        # Determine event name untuk period score
        event_name = None
        if val["source_label"] == "EVENT":
            event_name = val["source_name"]
        elif val["target_label"] == "EVENT":
            event_name = val["target_name"]

        # Period score
        halaman_str = " | ".join(val["halaman"]) if val["halaman"] else ""
        if event_name:
            per_score = compute_period_score(halaman_str, event_name, event_period_map)
        else:
            per_score = 0.25  # Relasi tanpa EVENT (Person-Person) → skor netral

        weight = compute_relation_weight(best_proximity, per_score)

        # Determine periode_bab
        periode_bab = ""
        if event_name and event_name in event_period_map:
            periode_bab = event_period_map[event_name]["bab_title"]

        result.append({
            "source_name": val["source_name"],
            "source_label": val["source_label"],
            "relation_type": val["relation_type"],
            "relation_subtype": val["relation_subtype"],
            "target_name": val["target_name"],
            "target_label": val["target_label"],
            "chunk_id": " | ".join(val["chunk_ids"]),
            "evidence": val["evidences"][0],  # Ambil evidence pertama saja
            "halaman": " | ".join(val["halaman"]),
            "frequency": max(len(val["chunk_ids"]), 1),
            "weight": weight,
            "periode_bab": periode_bab,
        })

    print(f"Relasi setelah deduplikasi: {len(result)}")
    return result


def build_nodes(df, event_period_map=None):
    """Bangun daftar node unik dari entitas, termasuk periode_bab untuk EVENT."""
    if event_period_map is None:
        event_period_map = {}

    node_map = {}

    for _, row in df.iterrows():
        name = row["canonical_name"]
        label = row["label"]
        original = row["entity_text"]
        chunk_id = row["chunk_id"]

        key = (label, name)

        if key not in node_map:
            node_map[key] = {
                "node_id": generate_node_id(name, label),
                "name": name,
                "label": label,
                "aliases": set(),
                "chunk_ids": set(),
                "frequency": 0,
            }

        node_map[key]["frequency"] += 1
        node_map[key]["chunk_ids"].add(str(chunk_id))
        if original != name:
            node_map[key]["aliases"].add(original)

    # Convert sets ke strings + tambah periode info untuk EVENT
    result = []
    for key, val in node_map.items():
        node = {
            "node_id": val["node_id"],
            "name": val["name"],
            "label": val["label"],
            "aliases": " | ".join(sorted(val["aliases"])) if val["aliases"] else "",
            "chunk_ids": " | ".join(sorted(val["chunk_ids"])),
            "frequency": val["frequency"],
            "periode_bab": "",
            "page_range": "",
        }

        # Tambah info periode untuk EVENT
        if val["label"] == "EVENT" and val["name"] in event_period_map:
            period = event_period_map[val["name"]]
            node["periode_bab"] = period["bab_title"]
            node["page_range"] = f"{period['page_start']}-{period['page_end']}"

        result.append(node)

    # Sort by label lalu frequency descending
    result.sort(key=lambda x: (x["label"], -x["frequency"]))

    print(f"\nTotal node unik: {len(result)}")
    for label in ["PERSON", "EVENT", "LOCATION", "TIME"]:
        count = sum(1 for n in result if n["label"] == label)
        print(f"  {label}: {count}")

    return result


def print_sample_relations(edges_df, n=10):
    """Tampilkan sample relasi untuk verifikasi."""
    print(f"\n{'='*80}")
    print(f"SAMPLE {n} RELASI:")
    print(f"{'='*80}")

    for rel_type in ["INVOLVED_IN", "OCCURRED_AT", "OCCURRED_ON",
                      "KELUARGA", "SAHABAT", "MUSUH", "PRECEDES"]:
        subset = edges_df[edges_df["relation_type"] == rel_type].head(n)
        if len(subset) == 0:
            continue
        print(f"\n-- {rel_type} ({len(edges_df[edges_df['relation_type'] == rel_type])} total) --")
        for _, row in subset.iterrows():
            src = f"[{row['source_label']}] {row['source_name']}"
            tgt = f"[{row['target_label']}] {row['target_name']}"
            print(f"  {src} --> {rel_type} --> {tgt}")
            # Tampilkan evidence yang dipersingkat
            ev = str(row["evidence"])[:100]
            if len(str(row["evidence"])) > 100:
                ev += "..."
            # Replace Unicode arrows for Windows console compatibility
            ev = ev.replace("\u2192", "->")
            print(f"    Evidence: {ev}")
            print()


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Relation Extraction Sirah")
    ap.add_argument("--input", type=Path, default=IN_PRELABELLED,
                    help="Path ke prelabelled CSV (default: sirah_prelabelled.csv)")
    ap.add_argument("--out-nodes", type=Path, default=OUT_NODES,
                    help="Output nodes CSV path")
    ap.add_argument("--out-edges", type=Path, default=OUT_EDGES,
                    help="Output edges CSV path")
    args = ap.parse_args()

    print("=" * 60)
    print("RELATION EXTRACTION - Sirah Nabawiyah")
    print("  (dengan pembobotan, relasi Person-Person, kronologi Event)")
    print("=" * 60)
    print(f"  input    : {args.input}")
    print(f"  out_nodes: {args.out_nodes}")
    print(f"  out_edges: {args.out_edges}")

    # 1. Load data & alias map
    print("\n[1/8] Loading data...")
    alias_map = load_alias_map(IN_ALIAS_MAP)
    print(f"  Alias map: {len(alias_map)} entries loaded")
    df = load_and_prepare_data(args.input, alias_map)

    # 2. Load TOC & build period map (untuk pembobotan)
    print("\n[2/8] Loading TOC & building period map...")
    toc = load_toc()
    print(f"  TOC: {len(toc)} BAB loaded")

    # Build nodes dulu (sementara tanpa period map) untuk event period mapping
    nodes_temp = build_nodes(df)
    nodes_temp_df = pd.DataFrame(nodes_temp)
    event_period_map = build_event_period_map(toc, nodes_temp_df)
    print(f"  Events mapped to BAB: {len(event_period_map)}")

    # 3. Build nodes (final, dengan period info)
    print("\n[3/8] Building node list (with period info)...")
    nodes = build_nodes(df, event_period_map)

    # 4. Build event-centric relations (INVOLVED_IN, OCCURRED_AT, OCCURRED_ON)
    print("\n[4/8] Building event-centric relations...")
    relations_raw = build_relations(df)

    # 5. Build Person-Person relations (KELUARGA, SAHABAT, MUSUH)
    print("\n[5/8] Building Person-Person relations...")
    person_relations = build_person_person_relations(df)

    # 6. Gabungkan semua relasi + deduplicate
    print("\n[6/8] Deduplicating all relations...")
    all_relations = relations_raw + person_relations
    relations_dedup = deduplicate_relations(all_relations, event_period_map)

    # 7. Build Event chronology (PRECEDES) — setelah deduplicate
    print("\n[7/8] Building Event chronology (PRECEDES)...")
    nodes_df = pd.DataFrame(nodes)
    chrono_relations = build_event_chronology(nodes_df, event_period_map)

    # Tambahkan weight untuk PRECEDES (selalu 1.0 — kronologis pasti)
    for rel in chrono_relations:
        rel["weight"] = 1.0
        rel["frequency"] = 1

    relations_dedup.extend(chrono_relations)

    # 8. Save output
    print("\n[8/8] Saving output...")
    args.out_nodes.parent.mkdir(parents=True, exist_ok=True)

    nodes_df.to_csv(args.out_nodes, index=False, sep=";", encoding="utf-8-sig")
    print(f"  Nodes saved to: {args.out_nodes}")

    edges_df = pd.DataFrame(relations_dedup)
    edges_df.to_csv(args.out_edges, index=False, sep=";", encoding="utf-8-sig")
    print(f"  Edges saved to: {args.out_edges}")

    # Statistik akhir
    print(f"\n{'='*60}")
    print("RINGKASAN STATISTIK")
    print(f"{'='*60}")
    print(f"Total node unik    : {len(nodes_df)}")
    print(f"Total edge unik    : {len(edges_df)}")
    if len(edges_df) > 0:
        print(f"\nDistribusi relasi:")
        for rel_type, count in edges_df["relation_type"].value_counts().items():
            print(f"  {rel_type}: {count}")

        # Statistik weight
        print(f"\nDistribusi weight:")
        print(f"  Mean  : {edges_df['weight'].mean():.3f}")
        print(f"  Median: {edges_df['weight'].median():.3f}")
        print(f"  Min   : {edges_df['weight'].min():.3f}")
        print(f"  Max   : {edges_df['weight'].max():.3f}")

        # Berapa yang punya periode_bab
        n_with_period = (edges_df["periode_bab"] != "").sum()
        print(f"\nEdges dengan periode_bab: {n_with_period}/{len(edges_df)}")

    # Sample relasi
    if len(edges_df) > 0:
        print_sample_relations(edges_df, n=5)

    print(f"\n{'='*60}")
    print("SELESAI!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
