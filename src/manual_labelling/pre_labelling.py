"""
Semi-Automatic Entity Pre-Labelling untuk Dataset Sirah Nabawiyah
Deteksi entitas PERSON, EVENT, LOCATION, TIME menggunakan regex & keyword matching.
Output: CSV pre-annotated yang tinggal direview/koreksi manual.
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_SEED = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\manual_labelling\sirah_manual_seed.csv")
OUT_PRE = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\manual_labelling\sirah_prelabelled.csv")

# ── PERSON patterns ──────────────────────────────────────────────────────────
# Daftar nama tokoh utama Sirah Nabawiyah (case-sensitive)
PERSON_EXACT = [
    # Nabi & julukan
    "Rasulullah", "Nabi Muhammad", "Muhammad",
    # Keluarga Nabi
    "Khadijah", "Khadijah binti Khuwailid", "Aisyah",
    "Fatimah", "Ali bin Abu Thalib", "Ali bin Abi Thalib", "Ali",
    "Hamzah", "Hamzah bin Abdul Muththalib",
    "Abu Thalib", "Abbas bin Abdul Muththalib", "Al-Abbas",
    "Abdullah bin Abdul Muththalib", "Abdul Muththalib",
    "Aminah binti Wahb", "Halimah",
    "Hasan", "Husain", "Ja'far bin Abu Thalib",
    "Abu Sufyan bin Al-Harits bin Abdul Muththalib",
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
    "Abdullah bin Abu Rabi'ah",
    # Istri Nabi lain
    "Hafshah", "Ummu Salamah", "Zainab",
    "Shafiyyah", "Juwairiyah",
    "Maimunah", "Maimunah binti Al-Harits Al-Amiriyah", "Maimunah binti Al-Harits Al- Amiriyah",
    # Musuh & tokoh Quraisy
    "Abu Jahal", "Abu Lahab", "Abu Sufyan bin Harb",
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

# ── Improved regex untuk nama Arab dengan nasab ──────────────────────────────
# Menangani pola: Name bin Al-Something, Name bin Abdul Something, dst.
#
# Atom nama: kata kapital, opsional diawali artikel Arab (Al-, Ash-, An-, dst.)
_ART = r"(?:(?:Al|An|Ash|As|Ats|Ad|Ar|Az|At|Adz)-)"
_ATOM = r"(?:" + _ART + r")?[A-Z][a-z']+(?:'[a-z]*)?"
#
# Setelah bin/binti, nama bisa compound: "Abdul Muththalib", "Abu Thalib"
_COMPOUND = r"(?:Abdul|Abu|Abul|Abi|Ummu|Ibnu)"
_POST_BIN = r"(?:" + _COMPOUND + r"\s+" + _ATOM + r"|" + _ATOM + r")"
_NASAB = r"\s+(?:bin|binti)\s+" + _POST_BIN
#
# Nama lengkap: harus punya compound prefix (Abu/Ummu/...) ATAU minimal satu nasab (bin/binti)
_PERSON_BIN_RE = re.compile(
    r"\b((?:Abu|Ummu|Ibnu|Ibnul|Abul)\s+" + _ATOM + r"(?:" + _NASAB + r")*"
    r"|" + _ATOM + r"(?:" + _NASAB + r")+)"
)

# Pola nama terpotong: berakhir dengan "bin Al", "bin Abu", dsb.
_TRUNCATED_SUFFIX_RE = re.compile(
    r"\s+(?:bin|binti)\s+(?:Al|An|Ash|As|Ats|Ad|Ar|Az|At|Adz|Abu|Abul|Abi|Abdul)$"
)
# Pola untuk memperluas nama terpotong dari teks berikutnya
# \s* setelah hyphen menangani artefak OCR seperti "An- Nu'man"
_EXTEND_RE = re.compile(
    r"(-\s*[A-Z][a-z']+(?:'[a-z]*)?|\s+[A-Z][a-z']+(?:'[a-z]*)?)"
)

# ── Rantai nasab panjang (genealogi) ─────────────────────────────────────────
# Pada silsilah "X bin Y bin Z bin ..." (mis. nasab Nabi di awal kitab), tiap nama
# adalah ORANG BERBEDA, jadi dipecah jadi PERSON terpisah & kata "bin" jadi O.
# Hanya aktif untuk RANTAI KONTINU >=_GENEAL_MIN_LINKS "bin" beruntun, di mana
# antar-"bin" hanya boleh ada nama + koma + "(yang namanya X)" + "atau Y" — BUKAN
# kata lain/angka. Ini memisahkan silsilah asli (A bin B bin C bin D...) dari
# DAFTAR orang ("1. A bin B ke X 2. C bin D ...") supaya nama biasa
# ("Ali bin Abu Thalib", "Uyainah bin Hishn") TIDAK ikut terpecah.
_GENEAL_MIN_LINKS = 6     # ambang konservatif: hanya nasab asli yang sepanjang ini
# Atom nama: compound ("Abdul Muththalib", "Abdu Manaf") atau atom tunggal.
_NAME_ATOM_RE = re.compile(
    r"(?:Abdul|Abdu|Abul|Abu|Abi|Ummu|Ibnu)\s+" + _ATOM
    + r"|" + _ATOM
)
# Nama tunggal untuk dipakai di pola rantai (compound prefix opsional).
_GNAME = r"(?:(?:Abdul|Abdu|Abul|Abu|Abi|Ummu|Ibnu)\s+)?" + _ATOM
# Satu mata rantai: pemisah sempit (paren/koma) + "bin X" + opsional "atau Y".
_CHAIN_LINK = (
    r"(?:\s*\([^)]*\))?\s*,?\s*(?:bin|binti)\s+" + _GNAME
    + r"(?:\s+atau\s+" + _GNAME + r")?"
)
_GENEALOGY_RE = re.compile(
    r"\b" + _GNAME + r"(?:" + _CHAIN_LINK + r"){" + str(_GENEAL_MIN_LINKS) + r",}"
)

# ── EVENT patterns ───────────────────────────────────────────────────────────
EVENT_EXACT = [
    # Perang
    "Perang Badr", "Perang Badar",
    "Perang Uhud",
    "Perang Khandaq", "Perang Ahzab", "Perang Al-Khandaq",
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

# Pattern generik perang/ghazwah/sariyah.
#
# Kata ke-2 setelah nama medan HANYA diambil bila benar-benar bagian nama event:
#   - kepala multi-kata : "Bani X", "Dzul X", "Dzatur X", "Hamra'ul X"
#   - kualifier ukuran  : "Badr Kubra", "Badr Ula", "Badr Shughra"
# Selain itu berhenti di 1 kata, supaya tidak menyedot PERSON/kata umum di
# belakangnya ("Perang Badr Aisyah", "Perang Khaibar Bekas" → cukup "Perang Badr"/
# "Perang Khaibar"). Trigger "perang"/"ghazwah" case-insensitive ([Pp]/[Gg]) agar
# bentuk huruf kecil ("perang Mu'tah") tetap tertangkap (kapitalisasi bukan penentu).
_EVENT_HEAD = r"(?:Bani|Banu|Dzul|Dzu|Dzatur|Dzatu|Dzi|Hamra'ul)"
_EVENT_QUAL = r"(?:Kubra|Ula|Shughra|Sughra|Akhir|Pertama|Kedua|Ketiga)"
_CAPWORD = r"[A-Z][a-z']+(?:-[A-Z][a-z']+)*"   # incl. nama berhyphen: "Al-Yamamah"
_EVENT_PERANG_RE = re.compile(
    r"\b([Pp]erang\s+(?:"
    + _EVENT_HEAD + r"\s+" + _CAPWORD              # Perang Bani Nadhir
    + r"|" + _CAPWORD + r"\s+" + _EVENT_QUAL       # Perang Badr Kubra
    + r"|" + _CAPWORD                              # Perang Badr (1 kata)
    + r"))"
)
_EVENT_GHAZWAH_RE = re.compile(
    r"\b([Gg]hazwah\s+(?:"
    + _EVENT_HEAD + r"\s+" + _CAPWORD
    + r"|" + _CAPWORD + r"\s+" + _EVENT_QUAL
    + r"|" + _CAPWORD
    + r"))"
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
]


# ── Matching engine ──────────────────────────────────────────────────────────
def find_exact_matches(text, patterns, label):
    """Cari semua kemunculan pattern eksak di teks."""
    results = []
    for pat in patterns:
        # Escape regex special chars in pattern.
        # Pakai lookaround (?<!\w)...(?!\w) — bukan \b — agar term yang berakhir
        # apostrof tetap match. "\bIsra'\b" GAGAL (tak ada word-boundary setelah
        # "'"); inilah akar 15 tambalan auto_isra_coverage. Lookaround memperbaikinya.
        escaped = re.escape(pat)
        for m in re.finditer(r"(?<!\w)" + escaped + r"(?!\w)", text):
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
            grp = 1 if m.lastindex else 0
            results.append({
                "entity_text": m.group(grp),
                "label": label,
                "start_char": m.start(grp),
                "end_char": m.end(grp),
            })
    return results


_INDO_STOPWORDS = {
    "Kemudian", "Lalu", "Wahai", "Maka", "Setelah", "Ketika", "Dengan",
    "Tentang", "Adapun", "Namun", "Sedangkan", "Menurut", "Bahkan",
    "Kepada", "Karena", "Terhadap", "Sementara", "Begitu", "Akhirnya",
    "Oleh", "Untuk", "Dalam", "Pada", "Dari", "Seperti", "Hingga",
    "Tanpa", "Selain", "Sebelum", "Sesudah", "Sambil", "Seraya",
    "Tatkala", "Tiba", "Saat", "Demi", "Bersama", "Bukan", "Tetapi",
    "Akan", "Jika", "Bila", "Walau", "Sekalipun", "Supaya", "Agar",
    "Antara", "Sekitar", "Berkata", "Mereka", "Merasa",
    "Sebab", "Padahal", "Bahwa", "Yakni", "Yaitu", "Rupanya",
    "Tanya", "Sesungguhnya", "Sungguh", "Sebenarnya", "Malah", "Justru", "Apalagi",
}

# Kata pertama tiap nama PERSON (untuk guard FP "perang <PERSON>").
# Battle tidak dinamai dari individu; "pasukan perang Kisra" bukan nama event.
_PERSON_FIRST = {p.split()[0] for p in PERSON_EXACT}


def find_person_bin(text):
    """Deteksi nama dengan 'bin/binti' yang belum tercakup di list eksak."""
    results = []
    for m in _PERSON_BIN_RE.finditer(text):
        name = m.group(1).strip()
        end_pos = m.end()

        if len(name) <= 5:  # skip yang terlalu pendek
            continue

        # Skip jika kata pertama adalah stopword bahasa Indonesia
        first_word = name.split()[0]
        if first_word in _INDO_STOPWORDS:
            continue

        # Perbaiki nama terpotong: "Ka'b bin Al" → "Ka'b bin Al-Khaththab"
        if _TRUNCATED_SUFFIX_RE.search(name):
            rest = text[end_pos:]
            ext = _EXTEND_RE.match(rest)
            if ext:
                name += ext.group(1)
                end_pos += ext.end()
                # Coba extend sekali lagi untuk compound seperti
                # "bin Abdul" + " " + "Muththalib"
                rest2 = text[end_pos:]
                ext2 = _EXTEND_RE.match(rest2)
                if ext2 and not ext2.group(1).startswith("-"):
                    name += ext2.group(1)
                    end_pos += ext2.end()

        results.append({
            "entity_text": name.strip(),
            "label": "PERSON",
            "start_char": m.start(),
            "end_char": end_pos,
        })
    return results


def find_genealogy_persons(text):
    """Deteksi rantai nasab panjang & pecah jadi PERSON per-nama (bin = O).

    Mengembalikan (regions, entities):
      - regions: daftar (start, end) span genealogi (untuk filter overlap di pemanggil)
      - entities: tiap nama diri di dalam region sebagai PERSON terpisah
    """
    regions, ents = [], []
    for m in _GENEALOGY_RE.finditer(text):
        s, e = m.start(), m.end()
        regions.append((s, e))
        # Tiap nama diri di dalam rantai (termasuk alias "(yang namanya X)") = PERSON.
        for nm in _NAME_ATOM_RE.finditer(text, s, e):
            ents.append({
                "entity_text": nm.group(0),
                "label": "PERSON",
                "start_char": nm.start(),
                "end_char": nm.end(),
            })
    return regions, ents


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


def _normalize_quotes(text):
    """Normalisasi karakter kutip unicode ke ASCII standar."""
    text = text.replace('\u2018', "'").replace('\u2019', "'")  # ' '
    text = text.replace('\u201C', '"').replace('\u201D', '"')  # " "
    text = text.replace('\u0060', "'")  # `
    text = text.replace('\u00B4', "'")  # ´
    return text


# ── Kamus koreksi OCR: apostrof INTERNAL yang hilang jadi spasi ───────────────
# Ditemukan dari data (entitas dikenal yang ter-split; versi benar dominan).
# WAJIB length-preserving (len kunci == len nilai) supaya offset karakter tetap
# valid — hanya apostrof internal (bukan ujung kata seperti "Isra'").
# Urut: kunci lebih panjang dulu agar tidak saling memotong.
_OCR_APOS_MAP = {
    "Mush ab": "Mush'ab",
    "Rabi ah": "Rabi'ah",
    "Isma il": "Isma'il",
    "Asy ari": "Asy'ari",
    "Ka bah": "Ka'bah",
    "Mu adz": "Mu'adz",
    "Ma qal": "Ma'qal",
    "Tha if": "Tha'if",
    "Mas ud": "Mas'ud",
    "As ad": "As'ad",
    "Sa d": "Sa'd",
    "Ka b": "Ka'b",
}
assert all(len(k) == len(v) for k, v in _OCR_APOS_MAP.items()), \
    "Koreksi OCR apostrof harus length-preserving (jaga offset)."
_OCR_APOS_RE = [
    (re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)"), v)
    for k, v in _OCR_APOS_MAP.items()
]


def _normalize_ocr_apostrophe(text):
    """Sambung balik nama ber-apostrof yang ter-split OCR ("Tha if" -> "Tha'if")."""
    for rx, v in _OCR_APOS_RE:
        text = rx.sub(v, text)
    return text


def normalize_text(text):
    """Normalisasi gabungan (kutip unicode + apostrof OCR). Length-preserving."""
    return _normalize_ocr_apostrophe(_normalize_quotes(text))


def extract_entities(text):
    """Ekstrak semua entitas dari teks."""
    if not isinstance(text, str) or not text.strip():
        return []
    text = normalize_text(text)

    all_ents = []

    # 0. Deteksi rantai nasab panjang (genealogi) — tiap nama jadi PERSON terpisah.
    geneal_regions, geneal_ents = find_genealogy_persons(text)

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

    # 8a. Di region genealogi: buang PERSON span normal (exact/bin) yang overlap,
    #     ganti dengan atom per-nama hasil find_genealogy_persons (bin = O).
    if geneal_regions:
        def _in_geneal(s, e):
            return any(s < gr_e and e > gr_s for gr_s, gr_e in geneal_regions)
        all_ents = [
            x for x in all_ents
            if not (x["label"] == "PERSON" and _in_geneal(x["start_char"], x["end_char"]))
        ]
        all_ents.extend(geneal_ents)

    # 8. Post-processing: bersihkan noise prefix yang lolos
    cleaned = []
    for ent in all_ents:
        name = ent["entity_text"]
        first_word = name.split()[0] if name else ""
        if first_word in _INDO_STOPWORDS and " " in name:
            # Strip prefix noise, perbaiki start_char
            stripped = name[len(first_word):].strip()
            ent["start_char"] += len(name) - len(stripped)
            ent["entity_text"] = stripped

        # Guard: buang FP "perang <PERSON>" 1-kata (mis. "pasukan perang Kisra").
        if ent["label"] == "EVENT":
            m = re.match(r"[Pp]erang\s+(\S+)$", ent["entity_text"])
            if m and m.group(1) in _PERSON_FIRST:
                continue

        cleaned.append(ent)

    # Deduplicate
    return deduplicate_entities(cleaned)


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
        # Normalisasi (kutip + apostrof OCR) length-preserving. Teks ter-normalisasi
        # disimpan ke output supaya offset entitas & tokenisasi downstream konsisten.
        text = normalize_text(str(row.get("teks_chunk", "")))
        entities = extract_entities(text)

        base = {col: row.get(col, "") for col in base_cols}
        base["teks_chunk"] = text

        if entities:
            chunks_with_ents += 1
            for ent in entities:
                r = {**base}
                r["entity_text"] = ent["entity_text"]
                r["label"] = ent["label"]
                r["notes"] = ""
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
