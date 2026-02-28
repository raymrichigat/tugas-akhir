"""
Semi-Automatic Entity Pre-Labelling untuk Dataset Sirah Nabawiyah
Deteksi entitas PERSON, EVENT, LOCATION, TIME menggunakan regex & keyword matching.
Output: CSV pre-annotated yang tinggal direview/koreksi manual.
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_SEED = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\chunking_result\sirah_manual_seed.csv")
OUT_PRE = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\chunking_result\sirah_prelabelled.csv")

# ── PERSON patterns ──────────────────────────────────────────────────────────
# Daftar nama tokoh utama Sirah Nabawiyah (case-sensitive)
PERSON_EXACT = [
    # Nabi & julukan
    "Rasulullah", "Nabi Muhammad", "Muhammad",
    # Keluarga Nabi
    "Khadijah", "Khadijah binti Khuwailid", "Aisyah",
    "Fatimah", "Ali bin Abu Thalib", "Ali",
    "Hamzah", "Hamzah bin Abdul Muththalib",
    "Abu Thalib", "Abbas bin Abdul Muththalib", "Al-Abbas",
    "Abdullah bin Abdul Muththalib", "Abdul Muththalib",
    "Aminah binti Wahb", "Halimah",
    "Hasan", "Husain",
    # Khulafaur Rasyidin & sahabat utama
    "Abu Bakar", "Abu Bakar Ash-Shiddiq",
    "Umar bin Al-Khaththab", "Umar",
    "Utsman bin Affan", "Utsman",
    "Zaid bin Haritsah", "Zaid",
    "Bilal", "Bilal bin Rabah",
    "Salman Al-Farisi", "Salman",
    # Sahabat lain
    "Sa'd bin Mu'adz", "Sa'd bin Ubadah", "Sa'd bin Abu Waqqash",
    "Abdurrahman bin Auf", "Thalhah bin Ubaidillah",
    "Zubair bin Al-Awwam", "Abu Ubaidah bin Al-Jarrah",
    "Mush'ab bin Umair", "Mush'ab",
    "Khalid bin Al-Walid", "Khalid",
    "Amr bin Al-Ash", "Abu Hurairah",
    "Ubay bin Ka'b", "Mu'adz bin Jabal", "Mu'adz",
    "Abu Dzar", "Abu Dzar Al-Ghifari",
    "Anas bin Malik", "Jabir bin Abdullah", "Jabir",
    "Khabbab bin Al-Aratt", "Khabbab",
    "Abdullah bin Mas'ud", "Ibnu Mas'ud",
    "Abdullah bin Abbas", "Ibnu Abbas",
    "Abdullah bin Umar", "Ibnu Umar",
    "Abdullah bin Ubay", "Abdullah bin Ubay bin Salul",
    "Abdullah bin Rawahah",
    "Ubadah bin Ash-Shamit",
    "Usamah bin Zaid", "Usamah",
    "As'ad bin Zurarah", "As'ad",
    "Al-Barra' bin Ma'rur", "Al-Barra'",
    "Usaid bin Hudhair", "Usaid",
    "Ka'b bin Malik", "Ka'b",
    "Sa'd bin Ar-Rabi'",
    "Rifa'ah bin Abdul Mundzir",
    "Al-Mundzir bin Amr",
    "Sa'd bin Khaitsamah",
    "Abul Haitsam bin At-Taihan",
    "Al-Abbas bin Ubadah",
    "Abdullah bin Amr bin Haram",
    "Al-Muth'im bin Adi",
    "Al-Harits bin Harb",
    "Siba bin Arfazhah",
    "Zaid bin Tsabit",
    # Istri Nabi lain
    "Hafshah", "Ummu Salamah", "Zainab",
    "Shafiyyah", "Juwairiyah", "Maimunah",
    # Musuh & tokoh Quraisy
    "Abu Jahal", "Abu Lahab", "Abu Sufyan",
    "Utbah bin Rabi'ah", "Utbah",
    "Syaibah bin Rabi'ah",
    "Walid bin Al-Mughirah",
    "Umayyah bin Khalaf", "Umayyah",
    "Ubay bin Khalaf",
    "Hind binti Utbah",
    "Ikrimah bin Abu Jahal",
    "Suhail bin Amr",
    "Al-Akhnas bin Syariq",
    "Al-Aswad bin Al-Muththalib",
    "Amr bin Luhay",
    # Tokoh lain
    "Waraqah bin Naufal", "Waraqah",
    "Jibril", "Musa", "Ibrahim", "Isa", "Isma'il",
    "Adam", "Nuh", "Yusuf", "Harun", "Idris",
    "Yahya bin Zakaria", "Isa bin Maryam",
    "Harun bin Imran", "Musa bin Imran",
    "Dzu Nuwas", "Abrahah",
    "As'ad Abu Karib",
    "Bukhtanashar",
    "Najasyi", "An-Najasyi",
    "Heraklius", "Kisra",
    "Farwah bin Amr Al-Judzami",
    "Rabi'ah bin Umayyah",
    "Qais bin Al-Aslat",
    "Nasibah binti Ka'b",
    # Perawi & ulama yang disebut
    "Ibnu Hisyam", "Ibnu Ishaq", "Ibnu Sa'd",
    "Ibnu Hajar", "Ibnul Qayyim",
    "An-Nawawi", "Al-Qurthubi",
    "Ath-Thabari", "Al-Baihaqi",
    "Abu Dawud", "Abu Qatadah",
    "Sa'id bin Al-Musayyab",
    "As-Samhudi",
    "Al-Khadhri",
    "Ummul Khair", "Ummu Jamil",
]

# Pattern untuk menangkap nama dengan "bin/binti" yang belum ada di list
_PERSON_BIN_RE = re.compile(
    r"\b([A-Z][a-z']+(?:\s+(?:bin|binti|Abu|Ummu|Ibnu|Ibnul|Abul)\s+[A-Z][a-z']+(?:\s+(?:bin|binti)\s+[A-Z][a-z']+)?))"
)

# ── EVENT patterns ───────────────────────────────────────────────────────────
EVENT_EXACT = [
    # Perang
    "Perang Badr", "Perang Badar",
    "Perang Uhud",
    "Perang Khandaq", "Perang Ahzab",
    "Perang Khaibar",
    "Perang Hunain",
    "Perang Tabuk",
    "Perang Mu'tah",
    "Perang Hamra'ul Asad",
    # Penaklukan
    "Fathu Makkah", "Penaklukan Makkah",
    # Perjanjian
    "Perjanjian Hudaibiyah",
    "Piagam Madinah",
    # Baiat
    "Baiat Aqabah", "Baiat Aqabah Pertama", "Baiat Aqabah Kedua",
    "Baiat Aqabah Kubra",
    # Hijrah
    "Hijrah", "Hijrah ke Habasyah", "Hijrah ke Madinah",
    # Isra Mi'raj
    "Isra'", "Mi'raj", "Isra' dan Mi'raj", "Isra' Mi'raj",
    # Haji
    "Haji Wada'", "Haji Wada",
    # Lainnya
    "Futuh Makkah",
    "Pemboikotan di Syi'b Abu Thalib",
    "Tahun Duka Cita", "Tahun Kesedihan",
    "Nuzulul Quran",
    "Fathul Makkah",
]

# Pattern generik perang/ghazwah/sariyah
_EVENT_PERANG_RE = re.compile(
    r"\b(Perang\s+[A-Z][a-z']+(?:\s+[A-Z][a-z']+)?)"
)
_EVENT_GHAZWAH_RE = re.compile(
    r"\b(Ghazwah\s+[A-Z][a-z']+(?:\s+[A-Z][a-z']+)?)"
)

# ── LOCATION patterns ────────────────────────────────────────────────────────
LOCATION_EXACT = [
    # Kota utama
    "Makkah", "Madinah", "Yastrib", "Yatsrib",
    "Thaif", "Tha'if",
    "Habasyah", "Najran",
    # Tempat suci & landmark
    "Ka'bah", "Baitullah", "Masjidil Haram", "Baitul Maqdis",
    "Gua Hira", "Gua Hira'", "Gua Tsur",
    "Jabal Nur", "Jabal Uhud",
    "Bukit Shafa", "Bukit Marwah", "Shafa", "Marwah",
    "Sumur Zamzam", "Zamzam",
    "Arafah", "Muzdalifah", "Mina",
    "Aqabah",
    # Wilayah
    "Hijaz", "Syam", "Yaman", "Irak", "Najd",
    "Tihamah", "Palestina", "Mesir",
    "Habasyah", "Persia",
    "Jazirah Arab",
    # Tempat spesifik
    "Badr", "Uhud", "Khandaq", "Khaibar", "Hunain",
    "Hudaibiyah", "Tabuk",
    "Dzul Hulaifah", "Dzu Thuwa'",
    "Al-Jurf", "Al-Kudr",
    "Qudaid",
    "Wadi Nakhlah",
    "Babilonia", "Babilon",
    # Pasar
    "Ukazh", "Majinnah", "Dzil-Majaz",
    # Sungai
    "Nil", "Eufrat",
    # Tempat lain
    "Sidratul Muntaha", "Al-Baitul-Ma'mur",
    "Laut Merah",
]

# ── TIME patterns ─────────────────────────────────────────────────────────────
# Bulan Hijriah
BULAN_HIJRIAH = [
    "Muharram", "Shafar", "Rabi'ul Awwal", "Rabi'ul Akhir",
    "Jumadil Ula", "Jumadil Akhir", "Jumada",
    "Rajab", "Sya'ban", "Ramadhan",
    "Syawwal", "Dzul Qa'dah", "Dzul Hijjah",
    "Dzul Qi'dah",
]

# Regex patterns untuk waktu
_TIME_PATTERNS = [
    # tahun X Hijriah/Masehi/Nubuwah/SM
    re.compile(r"\b(tahun\s+(?:ke[\s-]?)?\d+(?:\s+(?:Hijriyah|Hijriah|Masehi|SM|H|M|dari\s+nubuwah|setelah\s+hijrah|sebelum\s+hijrah))?)"),
    # tanggal X bulan
    re.compile(r"\b(tanggal\s+\d+\s+(?:dari\s+)?(?:bulan\s+)?\w+)"),
    # bulan + tahun
    re.compile(r"\b(bulan\s+(?:" + "|".join(BULAN_HIJRIAH) + r")(?:\s+(?:tahun\s+)?\d+\s*(?:H|Hijriyah|Hijriah)?)?)"),
    # hari Senin/Selasa/dll
    re.compile(r"\b(hari\s+(?:Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu|Tasyriq|kurban|tarwiyah))"),
    # X tahun sebelum/setelah
    re.compile(r"\b(\d+\s+tahun\s+(?:sebelum|setelah|sesudah)\s+\w+)"),
    # malam tanggal X
    re.compile(r"\b(malam\s+tanggal\s+\d+\s+(?:dari\s+)?(?:bulan\s+)?\w+)"),
    # Lailatul Qadr
    re.compile(r"\b(Lailatul[\s-]Qadr)"),
    re.compile(r"\b(Lailatul[\s-]Qadar)"),
    # pertengahan hari Tasyriq
    re.compile(r"\b(pertengahan\s+hari[\s-]hari\s+Tasyriq)"),
    # musim haji tahun
    re.compile(r"\b(musim\s+haji\s+(?:tahun\s+)?(?:ke[\s-]?)?\w+)"),
]


# ── Matching engine ──────────────────────────────────────────────────────────
def find_exact_matches(text, patterns, label):
    """Cari semua kemunculan pattern eksak di teks."""
    results = []
    for pat in patterns:
        # Escape regex special chars in pattern
        escaped = re.escape(pat)
        for m in re.finditer(r"\b" + escaped + r"\b", text):
            results.append({
                "entity_text": m.group(0),
                "label": label,
                "start_char": m.start(),
                "end_char": m.end(),
            })
    return results


def find_regex_matches(text, regex_list, label):
    """Cari semua kemunculan regex pattern di teks."""
    results = []
    for rx in regex_list:
        for m in rx.finditer(text):
            results.append({
                "entity_text": m.group(1) if m.lastindex else m.group(0),
                "label": label,
                "start_char": m.start(),
                "end_char": m.end(),
            })
    return results


def find_person_bin(text):
    """Deteksi nama dengan 'bin/binti' yang belum tercakup di list eksak."""
    results = []
    for m in _PERSON_BIN_RE.finditer(text):
        name = m.group(1).strip()
        if len(name) > 5:  # skip yang terlalu pendek
            results.append({
                "entity_text": name,
                "label": "PERSON",
                "start_char": m.start(),
                "end_char": m.end(),
            })
    return results


def find_time_bulan(text):
    """Deteksi nama bulan Hijriah di teks."""
    results = []
    for bulan in BULAN_HIJRIAH:
        escaped = re.escape(bulan)
        for m in re.finditer(r"\b" + escaped + r"\b", text):
            results.append({
                "entity_text": m.group(0),
                "label": "TIME",
                "start_char": m.start(),
                "end_char": m.end(),
            })
    return results


def deduplicate_entities(entities):
    """
    Hapus duplikat dan overlap.
    Jika ada overlap, pilih yang lebih panjang (lebih spesifik).
    """
    if not entities:
        return []

    # Urutkan: paling panjang dulu, lalu posisi awal
    entities.sort(key=lambda e: (-len(e["entity_text"]), e["start_char"]))

    kept = []
    used_spans = []

    for ent in entities:
        s, e = ent["start_char"], ent["end_char"]
        # Cek apakah overlap dengan span yang sudah diambil
        overlap = False
        for us, ue in used_spans:
            if s < ue and e > us:  # overlap
                overlap = True
                break
        if not overlap:
            kept.append(ent)
            used_spans.append((s, e))

    # Sort by position
    kept.sort(key=lambda x: x["start_char"])
    return kept


def extract_entities(text):
    """Ekstrak semua entitas dari teks."""
    if not isinstance(text, str) or not text.strip():
        return []

    all_ents = []

    # 1. PERSON - exact match (paling panjang dulu)
    persons_sorted = sorted(PERSON_EXACT, key=len, reverse=True)
    all_ents.extend(find_exact_matches(text, persons_sorted, "PERSON"))

    # 2. PERSON - bin/binti pattern
    all_ents.extend(find_person_bin(text))

    # 3. EVENT - exact match
    events_sorted = sorted(EVENT_EXACT, key=len, reverse=True)
    all_ents.extend(find_exact_matches(text, events_sorted, "EVENT"))

    # 4. EVENT - Perang/Ghazwah regex
    all_ents.extend(find_regex_matches(text, [_EVENT_PERANG_RE, _EVENT_GHAZWAH_RE], "EVENT"))

    # 5. LOCATION - exact match
    locations_sorted = sorted(LOCATION_EXACT, key=len, reverse=True)
    all_ents.extend(find_exact_matches(text, locations_sorted, "LOCATION"))

    # 6. TIME - regex patterns
    all_ents.extend(find_regex_matches(text, _TIME_PATTERNS, "TIME"))

    # 7. TIME - bulan Hijriah
    all_ents.extend(find_time_bulan(text))

    # Deduplicate
    return deduplicate_entities(all_ents)


# ── Pipeline utama ───────────────────────────────────────────────────────────
def main():
    # 1. Baca seed CSV
    df = pd.read_csv(IN_SEED, sep=";", encoding="utf-8-sig").fillna("")
    df.columns = df.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip()
    print(f"Chunks dibaca: {len(df)}")

    # Kolom dasar
    base_cols = ["chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab", "halaman", "teks_chunk"]

    # 2. Proses setiap chunk
    rows = []
    total_entities = 0
    chunks_with_ents = 0

    for _, row in df.iterrows():
        text = str(row.get("teks_chunk", ""))
        entities = extract_entities(text)

        base = {col: row.get(col, "") for col in base_cols}

        if entities:
            chunks_with_ents += 1
            for ent in entities:
                r = {**base}
                r["entity_text"] = ent["entity_text"]
                r["label"] = ent["label"]
                r["notes"] = "auto"
                r["start_char"] = ent["start_char"]
                r["end_char"] = ent["end_char"]
                rows.append(r)
                total_entities += 1
        else:
            # Chunk tanpa entitas: tetap masukkan 1 baris kosong
            r = {**base}
            r["entity_text"] = ""
            r["label"] = ""
            r["notes"] = ""
            r["start_char"] = ""
            r["end_char"] = ""
            rows.append(r)

    # 3. Buat DataFrame output
    out_cols = base_cols + ["entity_text", "label", "notes", "start_char", "end_char"]
    df_out = pd.DataFrame(rows, columns=out_cols)

    # 4. Statistik
    print(f"\nTotal entitas terdeteksi: {total_entities}")
    print(f"Chunks dengan entitas: {chunks_with_ents}/{len(df)}")

    label_counts = df_out[df_out["label"] != ""]["label"].value_counts()
    print(f"\nDistribusi label:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")

    # 5. Simpan
    df_out.to_csv(OUT_PRE, index=False, sep=";", encoding="utf-8-sig")
    print(f"\nOutput disimpan ke: {OUT_PRE}")

    # 6. Preview
    sample = df_out[df_out["label"] != ""].head(15)
    print(f"\nPreview 15 entitas pertama:")
    for _, r in sample.iterrows():
        print(f"  [{r['label']:8s}] {r['entity_text']:<35s} (chunk: {r['chunk_id']})")


if __name__ == "__main__":
    main()
