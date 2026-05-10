"""
Validasi Semua Relasi: INVOLVED_IN, OCCURRED_AT, OCCURRED_ON
Mendeteksi false positive dari proximity-based relation extraction.

Input : edges.csv
Output: validation_all_relations.md
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi Path ─────────────────────────────────────────────────────────
BASE_DIR = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
IN_EDGES = BASE_DIR / "data" / "result" / "relation_result" / "edges.csv"
OUT_MD = BASE_DIR / "data" / "result" / "relation_result" / "validation_all_relations.md"

# Variasi ejaan
SPELLING_VARIANTS = {
    "Yatsrib": ["Yastrib"],
    "Yastrib": ["Yatsrib"],
}


def get_variants(text: str) -> list[str]:
    variants = [text]
    if text in SPELLING_VARIANTS:
        variants.extend(SPELLING_VARIANTS[text])
    return variants


def check_patterns(evidence: str, entity: str, patterns: list) -> tuple[bool, str]:
    for ent_v in get_variants(entity):
        ent_esc = re.escape(ent_v)
        for pat_template, reason in patterns:
            pat = pat_template.replace("{ent}", ent_esc)
            if re.search(pat, evidence, re.IGNORECASE):
                return True, reason
    return False, ""


# ═════════════════════════════════════════════════════════════════════════════
# INVOLVED_IN: PERSON → EVENT
# ═════════════════════════════════════════════════════════════════════════════

INVOLVED_IN_INVALID = [
    # Perawi/narator hadits — hanya kalau bukan sahabat Nabi
    # Sahabat = perawi DAN peserta, jadi hanya tandai untuk known narrators
    (r"(?:diriwayatkan|meriwayatkan|meriwayatkannya)\s+(?:oleh\s+|dari\s+(?:hadits\s+)?)?{ent}",
     "Perawi/narator hadits (perlu cek apakah juga peserta)"),

    # Ibnu Hisyam, Abu Dawud, dll. — referensi kitab
    (r"(?:Sirah\s+An-Nabawiyah|Shahih\s+Al-Bukhari|Zadul\s+Ma'ad|Mukhtashar|Muhadharat|Kitab)[,\s]+{ent}",
     "Referensi kitab/sumber, bukan peserta event"),

    # "menurut pendapat X" / "seperti yang dikatakan X"
    (r"(?:menurut\s+(?:pendapat\s+)?|(?:seperti|sebagaimana)\s+(?:yang\s+)?(?:dikatakan|dituturkan|disebutkan)\s+(?:oleh\s+)?){ent}",
     "Sumber pendapat/riwayat, bukan peserta event"),

    # NOTE: "X berkata/menuturkan" DIHAPUS sebagai invalid pattern
    # Sahabat Nabi sering menuturkan pengalaman perang mereka sendiri
    # Hanya known narrators (ulama) yang ditangani via KNOWN_NARRATORS set

    # "setahun sebelum EVENT" — event sebagai penanda waktu
    # Hanya "setahun", bukan "beberapa hari" (yang bisa berarti partisipasi)
    (r"setahun\s+sebelum\s+.*?{ent}",
     "Event disebut sebagai penanda waktu, bukan keterlibatan"),

    # "setelah EVENT" — orang disebutkan setelah event, bukan ikut
    # Hati-hati: "setelah Perang Badr, X diutus" bisa valid (masih terkait)
    # Hanya invalid jika orang disebutkan JAUH dari konteks event

    # "X meninggal dunia pada ..." — orang sudah mati, bukan peserta
    (r"{ent}\s+(?:ini\s+)?meninggal\s+dunia",
     "Disebutkan dalam konteks kematian, bukan keterlibatan di event"),

    # PERSON = penulis kitab yang sering muncul sebagai referensi
    # (handled by kitab pattern above)

    # "ayat ... (X: 90)" — referensi ayat Al-Quran, bukan person
    (r"\(\s*{ent}\s*:\s*\d+\s*\)",
     "Referensi ayat Al-Quran, bukan peserta event"),

    # "pasukan yang dipimpin X menyerang Y" tapi event = Y (beda event)
    # → terlalu kompleks untuk regex, skip

    # "anak/putra X" — descendant, bukan X yang terlibat
    (r"(?:anak|putra|putri)\s+{ent}",
     "Keturunan yang disebut, bukan orang ini yang terlibat"),

    # "ayah X" — parent reference
    (r"ayah\s+{ent}",
     "Disebut sebagai orang tua, bukan peserta event"),
]

INVOLVED_IN_VALID = [
    # "X ikut/bergabung dalam EVENT"
    (r"{ent}\s+(?:ikut|bergabung|berperang|memimpin|menyerang|bertempur)",
     "Partisipasi aktif dalam event"),

    # "pada waktu EVENT, X melakukan..."
    (r"pada\s+(?:waktu|saat)\s+.*?{ent}",
     "Disebutkan aktif pada saat event"),

    # "X menjadi tawanan / terbunuh dalam EVENT"
    (r"{ent}\s+(?:menjadi\s+tawanan|terbunuh|mati\s+syahid|gugur)",
     "Korban/tawanan dalam event"),

    # "X dipimpin / dikomandani oleh Y"
    (r"(?:dipimpin|dikomandani)\s+(?:oleh\s+)?{ent}",
     "Pemimpin/komandan dalam event"),

    # "pembawanya adalah X" (pembawa bendera)
    (r"pembawanya\s+(?:adalah\s+)?{ent}",
     "Pembawa bendera perang"),

    # "wakil beliau ... X"
    (r"wakil\s+(?:beliau\s+)?(?:di\s+\w+\s+)?(?:adalah\s+)?.*?{ent}",
     "Ditunjuk sebagai wakil"),

    # "X mengangkat Y sebagai wakil"
    (r"{ent}\s+(?:sebagai\s+wakil|mengangkat)",
     "Terlibat dalam pengangkatan wakil"),

    # "X bersama/beserta Y"
    (r"{ent}\s+(?:bersama|beserta)",
     "Bersama rombongan event"),
]

# Nama-nama yang biasanya perawi/penulis kitab (bukan peserta perang)
KNOWN_NARRATORS = {
    "Ibnu Hisyam", "Ibnu Ishaq", "Abu Dawud", "Ath-Thabari",
    "An-Nawawi", "Ibnul Qayyim", "Al-Khadhri", "Ibnu Sa'd",
    "Al-Waqidi",
}


def validate_involved_in(row: pd.Series) -> tuple[str, str]:
    person = row["source_name"]
    event = row["target_name"]
    evidence = str(row["evidence"])

    # Referensi ayat Quran (e.g. "Yusuf: 90") — paling tegas
    if re.search(r"\(\s*" + re.escape(person) + r"\s*:\s*\d+\s*\)", evidence):
        return "Invalid", f"'{person}' adalah referensi ayat Al-Quran"

    # Known narrators/penulis kitab — bukan peserta sejarah
    is_narrator = person in KNOWN_NARRATORS
    if is_narrator:
        return "Invalid", f"'{person}' adalah perawi/penulis kitab, bukan peserta event"

    # Check valid and invalid patterns
    valid_match, valid_reason = check_patterns(evidence, person, INVOLVED_IN_VALID)
    invalid_match, invalid_reason = check_patterns(evidence, person, INVOLVED_IN_INVALID)

    # Jika ada pola "meriwayatkan" tapi person = sahabat Nabi,
    # sahabat bisa meriwayatkan DAN berpartisipasi → skip invalid
    if invalid_match and "perawi" in invalid_reason.lower():
        # Sahabat Nabi yang meriwayatkan → tetap Review, bukan Invalid
        if valid_match:
            return "Valid", valid_reason
        return "Review", f"Sahabat perawi: mungkin peserta sekaligus narator"

    if valid_match and not invalid_match:
        return "Valid", valid_reason
    elif invalid_match and not valid_match:
        return "Invalid", invalid_reason
    elif valid_match and invalid_match:
        return "Review", f"Konflik: VALID ({valid_reason}) vs INVALID ({invalid_reason})"
    else:
        # Default: proximity match tanpa pola jelas → Review
        return "Review", "Proximity match tanpa bukti partisipasi/narasi yang jelas"


# ═════════════════════════════════════════════════════════════════════════════
# OCCURRED_AT: EVENT → LOCATION
# ═════════════════════════════════════════════════════════════════════════════

OCCURRED_AT_INVALID = [
    (r"wakil\s+(?:beliau\s+)?di\s+{ent}",
     "Lokasi tempat wakil ditinggal, bukan lokasi perang"),
    (r"(?:kembali|pulang)\s+(?:lagi\s+)?ke\s+{ent}",
     "Lokasi tujuan kepulangan"),
    (r"kepulangan\s+.*?ke\s+{ent}",
     "Lokasi tujuan kepulangan"),
    (r"keluar\s+dari\s+{ent}",
     "Lokasi keberangkatan"),
    (r"penduduk\s+{ent}",
     "Mengacu penduduk lokasi"),
    (r"(?:berangkat|berasal)\s+dari\s+(?:\w+\s+){0,2}{ent}",
     "Lokasi asal/keberangkatan"),
    (r"berpencar\s+ke\s+{ent}",
     "Lokasi tujuan perpindahan"),
    (r"datang\s+ke\s+{ent}",
     "Lokasi tujuan kedatangan"),
    (r"pergi\s+(?:.*?\s+)?ke\s+{ent}",
     "Lokasi tujuan perjalanan"),
    (r"di\s+{ent}\s+dulu",
     "Referensi peristiwa lampau"),
    (r"orang-orang\s+(?:musyrik|kafir|munafik)\s+{ent}",
     "Mengacu orang dari lokasi"),
    (r"raja-raja\s+{ent}",
     "Mengacu penguasa lokasi"),
    (r"(?:tinggal|menetap)\s+(?:.*?\s+)?di\s+{ent}",
     "Lokasi tempat tinggal"),
    (r"membeli\s+.*?di\s+{ent}",
     "Lokasi pembelian"),
    (r"menyerang\s+(?:pinggiran\s+)?{ent}",
     "Lokasi target serangan"),
    (r"(?:harta\s+rampasan|ghanimah).*?(?:adalah|yaitu)\s+{ent}",
     "Lokasi sebagai harta rampasan"),
    (r"(?:seluruh|di\s+seluruh)\s+{ent}",
     "Deskripsi terlalu umum"),
    (r"antara\s+\w[\w\s]*?dan\s+{ent}",
     "Perbandingan/rentang, bukan lokasi kejadian"),
    (r"(?:masuk|melarikan\s+diri|pelarian.*?masuk)\s+ke\s+{ent}",
     "Lokasi tujuan pelarian"),
    (r"menuju\s+(?:ke\s+)?{ent}",
     "Lokasi tujuan perjalanan"),
    (r"(?:langit|ufuk)\s+{ent}",
     "Lokasi metaforis"),
    (r"surat\s+dari\s+.*?{ent}",
     "Asal surat"),
    (r"bergabung\s+dengan\s+{ent}",
     "Lokasi sebagai pihak"),
    (r"tiba\s+di\s+{ent}",
     "Lokasi kedatangan"),
    (r"sedang\s+berada\s+di\s+{ent}",
     "Lokasi keberadaan seseorang"),
    (r"sepulang\s+(?:.*?\s+)?dari\s+{ent}",
     "Lokasi yang ditinggalkan (sepulang dari)"),
    (r"sekembalinya\s+dari\s+{ent}",
     "Lokasi asal kepulangan"),
    (r"perjalanan\s+pulang\s+ke\s+{ent}",
     "Lokasi tujuan kepulangan"),
    (r"bergerak\s+ke\s+arah\s+.*?{ent}",
     "Lokasi tujuan ekspedisi"),
    (r"(?:setelah|sejak|sebelum)\s+(?:perang\s+)?(?:penaklukan|penaklukkan)\s+{ent}",
     "Merujuk peristiwa penaklukan lain"),
    (r"yang\s+berada\s+di\s+{ent}",
     "Mengacu orang di lokasi"),
    (r"(?:dalam\s+)?(?:penaklukkan|penaklukan)\s+{ent}",
     "Merujuk peristiwa penaklukan lokasi lain"),
]

OCCURRED_AT_VALID = [
    (r"[Ll]okasi\s+.*?{ent}",
     "Teks eksplisit menyebutkan lokasi kejadian"),
    (r"terjadi\s+(?:di|dekat)\s+.*?{ent}",
     "Kejadian terjadi di lokasi"),
    (r"hijrah\s+.*?ke\s+{ent}",
     "Lokasi tujuan hijrah"),
    (r"terbunuh\s+(?:dalam|di)\s+.*?{ent}",
     "Peristiwa kematian di lokasi"),
    (r"[Dd]ari\s+{ent}\s+ke\s+",
     "Titik awal perjalanan sakral"),
    (r"ke\s+{ent}\s*\.\s+[Dd]engan",
     "Tujuan perjalanan sakral"),
    (r"tak\s+jauh\s+dari\s+{ent}",
     "Kejadian dekat lokasi"),
    (r"(?:berperang|pertempuran|peperangan)\s+(?:di|dekat)\s+{ent}",
     "Peperangan di lokasi"),
    (r"tatkala\s+di\s+{ent}",
     "Peristiwa saat berada di lokasi"),
    (r"baiat\s+{ent}",
     "Baiat di lokasi"),
    (r"di\s+negeri\s+{ent}",
     "Peristiwa di negeri/wilayah"),
    (r"di\s+pinggiran\s+{ent}",
     "Peristiwa di perbatasan lokasi"),
    (r"setibanya\s+di\s+{ent}.*?(?:terbunuh|mati\s+syahid)",
     "Peristiwa kematian setelah tiba"),
    (r"[Aa]rdhisi\s+{ent}",
     "Teks Arab 'dari tanah LOC'"),
    (r"semasa\s+\w+.*?{ent}",
     "Peristiwa di wilayah lokasi"),
]


def event_name_contains_loc(event: str, loc: str) -> bool:
    return loc.lower() in event.lower()


def validate_occurred_at(row: pd.Series) -> tuple[str, str]:
    event = row["source_name"]
    loc = row["target_name"]
    evidence = str(row["evidence"])

    if event_name_contains_loc(event, loc):
        return "Valid", f"Nama event '{event}' mengandung lokasi '{loc}'"

    if re.search(r"(?:Fath|fath|penakluk)", event, re.IGNORECASE):
        for loc_v in get_variants(loc):
            loc_esc = re.escape(loc_v)
            if re.search(rf"(?:penaklukkan|penaklukan|menaklukkan)\s+{loc_esc}",
                         evidence, re.IGNORECASE):
                return "Valid", f"Event penaklukan, '{loc}' adalah target"

    valid_match, valid_reason = check_patterns(evidence, loc, OCCURRED_AT_VALID)
    invalid_match, invalid_reason = check_patterns(evidence, loc, OCCURRED_AT_INVALID)

    if valid_match and not invalid_match:
        return "Valid", valid_reason
    elif invalid_match and not valid_match:
        return "Invalid", invalid_reason
    elif valid_match and invalid_match:
        return "Review", f"Konflik: VALID ({valid_reason}) vs INVALID ({invalid_reason})"
    else:
        return "Review", "Tidak ditemukan pola yang jelas"


# ═════════════════════════════════════════════════════════════════════════════
# OCCURRED_ON: EVENT → TIME
# ═════════════════════════════════════════════════════════════════════════════

OCCURRED_ON_INVALID = [
    # "setelah EVENT ... pada TIME" — waktu setelah event (bukan waktu event)
    (r"(?:setelah|seusai|sesudah|sepulang)\s+.*?(?:pada|di)\s+.*?{ent}",
     "Waktu disebutkan setelah event (bukan waktu event itu sendiri)"),

    # "meninggal dunia pada TIME" — waktu kematian, bukan event
    (r"meninggal\s+(?:dunia\s+)?(?:pada|di)\s+.*?{ent}",
     "Waktu kematian seseorang, bukan waktu event"),

    # "X masuk Islam ... pada TIME" — waktu masuk Islam, bukan event
    (r"masuk\s+Islam\s+.*?{ent}",
     "Waktu masuk Islam, bukan waktu event"),

    # "dinikahi ... pada TIME" — waktu pernikahan, bukan event
    (r"(?:dinikahi|menikahi|menikah)\s+.*?(?:pada|di)\s+.*?{ent}",
     "Waktu pernikahan, bukan waktu event"),

    # "Tidak benar EVENT terjadi pada TIME" — waktu yang DISANGKAL
    (r"[Tt]idak\s+benar\s+.*?(?:terjadi|pada)\s+.*?{ent}",
     "Waktu yang disangkal/dibantah dalam teks"),

    # "selang ... setelah EVENT ... pada TIME" — waktu event LAIN
    (r"selang\s+.*?setelah\s+.*?{ent}",
     "Waktu event lain yang disebutkan setelah event utama"),

    # "dua bulan setengah setelah EVENT" + TIME = waktu pertemuan/hijrah
    (r"(?:dua|tiga|empat|lima)\s+(?:bulan|minggu|hari)\s+.*?setelah\s+.*?{ent}",
     "Waktu setelah event, bukan waktu event itu sendiri"),

    # "X kembali ... pada TIME" — waktu kepulangan
    (r"(?:kembali|pulang|kepulangan)\s+.*?(?:pada|akhir)\s+.*?{ent}",
     "Waktu kepulangan, bukan waktu kejadian"),
]

OCCURRED_ON_VALID = [
    # "EVENT pada/di TIME"
    (r"(?:terjadi|berlangsung|meletus|pecah)\s+(?:pada|di|tepat)\s+.*?{ent}",
     "Teks eksplisit menyebutkan waktu kejadian"),

    # "Pada TIME, EVENT ..."
    (r"[Pp]ada\s+{ent}\s*[,.]",
     "Waktu disebutkan di awal sebagai keterangan event"),

    # "EVENT ... pada TIME. Rasulullah pergi..." (deskripsi langsung event)
    (r"[Pp]ada\s+{ent}\s+.*?(?:Rasulullah|beliau)\s+(?:pergi|keluar|berangkat)",
     "Waktu keberangkatan event"),

    # "pada TIME bertepatan dengan ..." (tanggal event dengan konversi kalender)
    (r"(?:[Pp]ada|bertepatan\s+dengan)\s+{ent}",
     "Waktu event dengan konversi kalender"),

    # "EVENT ini terjadi pada TIME"
    (r"ini\s+terjadi\s+(?:pada|di)\s+.*?{ent}",
     "Waktu event eksplisit"),

    # "EVENT pada tahun/bulan TIME"
    (r"pada\s+(?:tahun|bulan)?\s*{ent}",
     "Waktu event disebutkan langsung"),

    # "pengepungan ... berakhir pada TIME"
    (r"(?:berakhir|selesai)\s+(?:pada|di)\s+.*?{ent}",
     "Waktu berakhirnya event"),

    # "Kejadiannya pada TIME"
    (r"[Kk]ejadiannya\s+(?:pada|di)\s+{ent}",
     "Waktu kejadian eksplisit"),
]


def validate_occurred_on(row: pd.Series) -> tuple[str, str]:
    event = row["source_name"]
    time = row["target_name"]
    evidence = str(row["evidence"])

    valid_match, valid_reason = check_patterns(evidence, time, OCCURRED_ON_VALID)
    invalid_match, invalid_reason = check_patterns(evidence, time, OCCURRED_ON_INVALID)

    if valid_match and not invalid_match:
        return "Valid", valid_reason
    elif invalid_match and not valid_match:
        return "Invalid", invalid_reason
    elif valid_match and invalid_match:
        return "Review", f"Konflik: VALID ({valid_reason}) vs INVALID ({invalid_reason})"
    else:
        return "Review", "Tidak ditemukan pola yang jelas"


# ═════════════════════════════════════════════════════════════════════════════
# Output Markdown
# ═════════════════════════════════════════════════════════════════════════════

def truncate(text: str, max_len: int = 80) -> str:
    text = text.replace("|", "/").replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text


def generate_markdown(results: dict[str, pd.DataFrame]) -> str:
    lines = []
    lines.append("# Validasi Semua Relasi (Proximity-based)\n")
    lines.append("Validasi false positive dari ketiga tipe relasi.\n")
    lines.append("## Mekanisme Proximity\n")
    lines.append("Dua entitas dianggap berelasi jika memenuhi **salah satu** syarat:\n")
    lines.append("1. Berada dalam **kalimat yang sama**, ATAU")
    lines.append("2. Jarak antar entitas **< 200 karakter**\n")
    lines.append("Relasi yang terbentuk:\n")
    lines.append("- **INVOLVED_IN**: PERSON dekat EVENT → person terlibat dalam event")
    lines.append("- **OCCURRED_AT**: EVENT dekat LOCATION → event terjadi di lokasi")
    lines.append("- **OCCURRED_ON**: EVENT dekat TIME → event terjadi pada waktu\n")
    lines.append("Setelah proximity check, diterapkan **contextual guard** berupa")
    lines.append("pattern-matching pada evidence untuk menyaring false positive.\n")

    # Grand summary
    lines.append("## Ringkasan Keseluruhan\n")
    lines.append("| Tipe Relasi | Total | Valid | Invalid | Review | % Invalid |")
    lines.append("|-------------|-------|-------|---------|--------|-----------|")

    grand_total = grand_valid = grand_invalid = grand_review = 0
    for rel_type, df in results.items():
        total = len(df)
        valid = len(df[df["status"] == "Valid"])
        invalid = len(df[df["status"] == "Invalid"])
        review = len(df[df["status"] == "Review"])
        pct = invalid / total * 100 if total > 0 else 0
        lines.append(f"| {rel_type} | {total} | {valid} | {invalid} | {review} | {pct:.1f}% |")
        grand_total += total
        grand_valid += valid
        grand_invalid += invalid
        grand_review += review

    pct = grand_invalid / grand_total * 100 if grand_total > 0 else 0
    lines.append(f"| **TOTAL** | **{grand_total}** | **{grand_valid}** | "
                 f"**{grand_invalid}** | **{grand_review}** | **{pct:.1f}%** |")
    lines.append("")

    # Per relation type
    for rel_type, df in results.items():
        lines.append(f"---\n")
        lines.append(f"## {rel_type}\n")

        total = len(df)
        valid = len(df[df["status"] == "Valid"])
        invalid = len(df[df["status"] == "Invalid"])
        review = len(df[df["status"] == "Review"])

        lines.append(f"Total: {total} | Valid: {valid} | Invalid: {invalid} | Review: {review}\n")

        # Full table
        if rel_type == "INVOLVED_IN":
            src_label, tgt_label = "PERSON", "EVENT"
        elif rel_type == "OCCURRED_AT":
            src_label, tgt_label = "EVENT", "LOCATION"
        else:
            src_label, tgt_label = "EVENT", "TIME"

        lines.append(f"| No | Source ({src_label}) | Target ({tgt_label}) | Status | Alasan | Evidence (kutipan) |")
        lines.append("|----|--------------------|---------------------|--------|--------|-------------------|")

        for i, (_, row) in enumerate(df.iterrows(), 1):
            ev = truncate(str(row["evidence"]), 100)
            lines.append(
                f"| {i} | {row['source_name']} | {row['target_name']} | "
                f"{row['status']} | {row['alasan']} | {ev} |"
            )
        lines.append("")

        # Detail Invalid
        invalid_df = df[df["status"] == "Invalid"]
        if len(invalid_df) > 0:
            lines.append(f"### {rel_type} — Detail Invalid\n")
            lines.append(f"| No | Source | Target | Alasan | Evidence |")
            lines.append("|----|---------|---------|---------|---------| ")
            for i, (_, row) in enumerate(invalid_df.iterrows(), 1):
                ev = truncate(str(row["evidence"]))
                lines.append(
                    f"| {i} | {row['source_name']} | {row['target_name']} | "
                    f"{row['alasan']} | {ev} |"
                )
            lines.append("")

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("VALIDASI SEMUA RELASI")
    print("=" * 60)

    df = pd.read_csv(IN_EDGES, sep=";", encoding="utf-8-sig")
    print(f"Total edges: {len(df)}")

    results = {}

    # 1. INVOLVED_IN
    involved = df[df["relation_type"] == "INVOLVED_IN"].copy()
    print(f"\n--- INVOLVED_IN ({len(involved)}) ---")
    inv_results = []
    for _, row in involved.iterrows():
        status, alasan = validate_involved_in(row)
        inv_results.append({**row.to_dict(), "status": status, "alasan": alasan})
    inv_df = pd.DataFrame(inv_results)
    results["INVOLVED_IN"] = inv_df
    for s in ["Valid", "Invalid", "Review"]:
        c = len(inv_df[inv_df["status"] == s])
        print(f"  {s:8s}: {c:3d} ({c/len(inv_df)*100:.1f}%)")

    # 2. OCCURRED_AT
    occurred_at = df[df["relation_type"] == "OCCURRED_AT"].copy()
    print(f"\n--- OCCURRED_AT ({len(occurred_at)}) ---")
    at_results = []
    for _, row in occurred_at.iterrows():
        status, alasan = validate_occurred_at(row)
        at_results.append({**row.to_dict(), "status": status, "alasan": alasan})
    at_df = pd.DataFrame(at_results)
    results["OCCURRED_AT"] = at_df
    for s in ["Valid", "Invalid", "Review"]:
        c = len(at_df[at_df["status"] == s])
        print(f"  {s:8s}: {c:3d} ({c/len(at_df)*100:.1f}%)")

    # 3. OCCURRED_ON
    occurred_on = df[df["relation_type"] == "OCCURRED_ON"].copy()
    print(f"\n--- OCCURRED_ON ({len(occurred_on)}) ---")
    on_results = []
    for _, row in occurred_on.iterrows():
        status, alasan = validate_occurred_on(row)
        on_results.append({**row.to_dict(), "status": status, "alasan": alasan})
    on_df = pd.DataFrame(on_results)
    results["OCCURRED_ON"] = on_df
    for s in ["Valid", "Invalid", "Review"]:
        c = len(on_df[on_df["status"] == s])
        print(f"  {s:8s}: {c:3d} ({c/len(on_df)*100:.1f}%)")

    # 4. Generate markdown
    md = generate_markdown(results)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"\nOutput: {OUT_MD}")

    # 5. Grand summary
    total = sum(len(d) for d in results.values())
    invalid = sum(len(d[d["status"] == "Invalid"]) for d in results.values())
    print(f"\n{'='*60}")
    print(f"GRAND TOTAL: {total} relasi, {invalid} invalid ({invalid/total*100:.1f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
