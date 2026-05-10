"""
Period Mapping — Pemetaan EVENT ke BAB utama buku Sirah Nabawiyah.

Membaca toc_groundtruth.json (61 BAB) dan memetakan setiap EVENT node
ke BAB utamanya berdasarkan fuzzy matching judul BAB.
Digunakan oleh relation_extraction.py untuk menghitung period score pada pembobotan relasi.
"""

import json
from pathlib import Path
from difflib import SequenceMatcher

# ── Konfigurasi Path ─────────────────────────────────────────────────────────
BASE_DIR = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
TOC_PATH = BASE_DIR / "data" / "toc_groundtruth.json"


def load_toc(filepath=TOC_PATH):
    """
    Baca TOC groundtruth dan hitung page_end tiap BAB.
    page_end BAB ke-i = page_start BAB ke-(i+1) - 1.
    BAB terakhir: page_end = 633 (total halaman buku).

    Returns: list of dict — [{title, page_start, page_end, subbab: [...]}, ...]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        toc_raw = json.load(f)

    # Hanya ambil level BAB
    babs = [entry for entry in toc_raw if entry.get("level") == "BAB"]

    # Hitung page_end
    for i, bab in enumerate(babs):
        if i + 1 < len(babs):
            bab["page_end"] = babs[i + 1]["page_start"] - 1
        else:
            bab["page_end"] = 633  # Halaman terakhir buku

    return babs


def _normalize_for_matching(text):
    """Normalisasi teks untuk fuzzy matching: lowercase, strip, collapse spaces."""
    return " ".join(text.lower().strip().split())


def _match_score(event_name, bab_title):
    """
    Hitung skor kecocokan antara nama EVENT dan judul BAB.
    Menggunakan kombinasi substring check dan SequenceMatcher.

    Returns: float 0.0–1.0
    """
    ev_norm = _normalize_for_matching(event_name)
    bab_norm = _normalize_for_matching(bab_title)

    # Exact substring match (case-insensitive) → skor tinggi
    if ev_norm in bab_norm or bab_norm in ev_norm:
        return 0.95

    # SequenceMatcher ratio
    return SequenceMatcher(None, ev_norm, bab_norm).ratio()


def build_event_period_map(toc, nodes_df):
    """
    Petakan setiap EVENT node ke BAB utamanya berdasarkan fuzzy match judul.

    Args:
        toc: list of BAB dicts dari load_toc()
        nodes_df: DataFrame nodes (kolom: name, label, ...)

    Returns:
        dict — {event_name: {"bab_title": str, "page_start": int, "page_end": int}}
        Hanya EVENT yang match dengan threshold >= 0.5
    """
    event_nodes = nodes_df[nodes_df["label"] == "EVENT"]
    event_period_map = {}

    # Kumpulkan semua judul BAB + subbab
    bab_entries = []
    for bab in toc:
        bab_entries.append({
            "title": bab["title"],
            "page_start": bab["page_start"],
            "page_end": bab["page_end"],
        })
        for sub in bab.get("subbab", []):
            bab_entries.append({
                "title": sub["title"],
                "page_start": sub["page_start"],
                "page_end": bab["page_end"],  # subbab punya page_end sama dengan BAB induknya
            })

    for _, event in event_nodes.iterrows():
        event_name = event["name"]
        best_score = 0.0
        best_bab = None

        for entry in bab_entries:
            score = _match_score(event_name, entry["title"])
            if score > best_score:
                best_score = score
                best_bab = entry

        if best_score >= 0.5 and best_bab is not None:
            event_period_map[event_name] = {
                "bab_title": best_bab["title"],
                "page_start": best_bab["page_start"],
                "page_end": best_bab["page_end"],
            }

    return event_period_map


def is_in_primary_period(halaman_str, event_period):
    """
    Cek apakah halaman chunk berada di range BAB utama event.

    Args:
        halaman_str: string halaman dari chunk (bisa "266" atau "266 | 267")
        event_period: dict dari event_period_map — {"bab_title", "page_start", "page_end"}

    Returns: bool
    """
    if event_period is None:
        return False

    page_start = event_period["page_start"]
    page_end = event_period["page_end"]

    # Parse halaman (bisa multi-page separated by " | ")
    try:
        pages = [int(p.strip()) for p in str(halaman_str).split("|") if p.strip().isdigit()]
    except (ValueError, AttributeError):
        return False

    return any(page_start <= p <= page_end for p in pages)


def compute_proximity_score(ent1_start, ent1_end, ent2_start, ent2_end, text):
    """
    Hitung proximity score (0.0–0.5) berdasarkan kedekatan posisi dua entitas.

    - Same sentence → 0.5
    - Jarak < 50 char → 0.4
    - Jarak < 100 char → 0.3
    - Jarak < 200 char → 0.2
    - Lainnya → 0.1
    """
    from relation_extraction import split_into_sentences, get_sentence_at_position

    # Cek kalimat yang sama
    sent1, _, _ = get_sentence_at_position(text, ent1_start)
    sent2, _, _ = get_sentence_at_position(text, ent2_start)
    if sent1 == sent2:
        return 0.5

    # Hitung jarak
    distance = min(
        abs(ent1_start - ent2_end),
        abs(ent2_start - ent1_end),
    )

    if distance < 50:
        return 0.4
    elif distance < 100:
        return 0.3
    elif distance < 200:
        return 0.2
    else:
        return 0.1


def compute_period_score(halaman_str, event_name, event_period_map):
    """
    Hitung period score (0.0–0.5) berdasarkan apakah chunk berada di BAB utama event.

    - Chunk ada di BAB utama event → 0.5
    - Event tidak punya mapped BAB → 0.25 (neutral)
    - Chunk di luar BAB utama → 0.0
    """
    event_period = event_period_map.get(event_name)

    if event_period is None:
        return 0.25  # Event tidak ter-mapping → skor netral

    if is_in_primary_period(halaman_str, event_period):
        return 0.5

    return 0.0


def compute_relation_weight(proximity_score, period_score):
    """
    Gabungkan proximity + period score menjadi weight final (0.0–1.0).
    """
    return round(proximity_score + period_score, 2)


# ── CLI untuk debugging ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import pandas as pd

    print("Loading TOC...")
    toc = load_toc()
    print(f"  {len(toc)} BAB loaded")

    # Coba dengan nodes.csv jika ada
    nodes_path = BASE_DIR / "data" / "result" / "relation_result" / "nodes.csv"
    if nodes_path.exists():
        nodes_df = pd.read_csv(nodes_path, sep=";", encoding="utf-8-sig")
        print(f"\nBuilding event period map from {len(nodes_df)} nodes...")
        event_map = build_event_period_map(toc, nodes_df)
        print(f"  {len(event_map)} events mapped to BAB")

        for event_name, period in sorted(event_map.items(), key=lambda x: x[1]["page_start"]):
            print(f"  {event_name:40s} → {period['bab_title'][:50]:50s} (hal. {period['page_start']}-{period['page_end']})")
    else:
        print(f"\n  {nodes_path} belum ada — jalankan relation_extraction.py dulu")
