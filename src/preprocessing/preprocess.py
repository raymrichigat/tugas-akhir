"""
Preprocessing Script untuk Dataset Sirah Nabawiyah
- Filter baris tidak relevan (UNKNOWN BAB, bibliografi)
- Normalisasi teks (whitespace, karakter non-printable)
- Pembersihan gibberish OCR (token aneh, run aneh, kalimat gibberish)
- Filter kalimat footnote/referensi bibliografi
- Ekspor ke CSV bersih
"""

import re
import pandas as pd
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────────────
IN_CSV  = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\preprocessing_result\sirah_simple.csv")
OUT_CSV = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\result\preprocessing_result\sirah_simple_clean.csv")

DROP_UNKNOWN_BAB = True
DROP_BIBLIO      = True
DROP_EMPTY       = True
DROP_TOO_SHORT   = False
MIN_WORDS        = 5

# ── Regex patterns ───────────────────────────────────────────────────────────
# FIX: hapus split pada ':' agar kalimat kutipan/definisi tidak terpotong
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|(?<=;)\s+")
ZWS_RE      = re.compile(r"[\u200b\u200c\u200d\uFEFF]")

# FIX: simbol OCR noise yang bukan tanda baca standar → dibersihkan di light_cleanup
_NOISE_SYMS_RE = re.compile(r"[&{}\|<>\[\]~^]")

# Normalisasi apostrof/ain: semua varian → apostrof standar (')
_APOSTROPHE_RE = re.compile(r"[\u2018\u2019\u201a\u201b\u2032\u02bc\u02bb\u0060\uff07\u02be\u02bf]")

# Fix "Al- Kata" atau "Ar- Kata" → "Al-Kata" / "Ar-Kata" (spasi setelah tanda hubung dihapus)
_AL_AR_SPACE_RE = re.compile(r"\b(A[lr]-)\s+")

# FIX: perluas stripping punctuation/simbol agar O}, &Ku, dll terdeteksi sebagai weird
_TRAILING_PUNC = re.compile(r"[,.:;!?\-\)\(\}\{\|\&~^<>\[\]]+$")
_LEADING_PUNC  = re.compile(r"^[,.:;!?\-\)\(\}\{\|\&~^<>\[\]]+")

# Whitelist singkatan yang valid di teks Sirah
TOKEN_WHITELIST = {
    "SAW", "SWT", "RA", "AS", "QS", "HR", "SM", "AN",
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII",  # FIX: Roman numeral XI-XII (XIII+ aman karena len > 3)
    "DI", "KE", "YA", "LA", "AL", "BI", "WA", "MA", "IN",
    "DAN", "INI", "ITU", "ADA", "HAL",
}

# Kata pendek Indonesia yang sering muncul (2-3 huruf)
COMMON_SHORT_WORDS = {
    "di", "ke", "ya", "la", "mu", "ku", "se", "si", "bi",
    "al", "wa", "ma", "in", "an", "da", "ba", "ha", "ka",
    "dan", "ini", "itu", "ada", "hal", "lah", "pun",
    "dia", "dua", "apa", "tak", "jua", "bin", "abu", "bab",
    "air", "saa", "rak", "sah", "sya", "nya",
    "jam", "san", "raj", "dai", "akh", "ala", "ber",
    # FIX: singkatan umum Indonesia
    "no", "dr", "yg", "tdk", "dgn", "dll", "dst", "dsb", "tsb", "hrs",
}


# ── Fungsi utilitas ──────────────────────────────────────────────────────────
def normalize_ws(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def light_cleanup(text: str) -> str:
    """Cleaning ringan: hapus karakter non-printable, simbol bullet, dan simbol OCR noise."""
    if not isinstance(text, str):
        return ""
    t = "".join(ch for ch in text if ch.isprintable())
    t = t.replace("@", " ").replace("*", " ").replace("#", " ")
    t = t.replace("•", " ").replace("·", " ").replace("●", " ").replace("▪", " ")
    # FIX: hapus simbol OCR noise non-standar (&, {}, |, <>, [], ~, ^)
    t = _NOISE_SYMS_RE.sub(" ", t)
    # Normalisasi apostrof/ain ke apostrof standar (')
    t = _APOSTROPHE_RE.sub("'", t)
    # Fix spasi setelah "Al-" / "Ar-": "Al- Julunda" → "Al-Julunda"
    t = _AL_AR_SPACE_RE.sub(r"\1", t)
    return normalize_ws(t)


def split_sentences(text: str):
    t = normalize_ws(text)
    if not t:
        return []
    return [s.strip() for s in _SENT_SPLIT.split(t) if s.strip()]


# ── Deteksi token aneh ───────────────────────────────────────────────────────
def token_is_weird(t: str) -> bool:
    """
    Deteksi token noise OCR:
    - Angka berdiri sendiri (8, 3)
    - Huruf besar tunggal bukan di whitelist (W, B, L)
    - Campuran lowercase→UPPERCASE (pHI, wJI)
    - Token uppercase pendek ≤3 huruf bukan di whitelist (EL, TJI, KK, GI)
    - Campuran digit + huruf (n1, 8s, t1)
    - Token huruf pendek (≤3 huruf) yang BUKAN kata umum Indonesia (Ug, fts, fs)
    - Token diawali tanda baca (:ebaI)
    """
    t = t.strip()
    if not t:
        return False

    # FIX: perluas stripping agar O}, &Ku, dll terdeteksi dengan benar
    t_clean = _TRAILING_PUNC.sub("", t)
    t_clean = _LEADING_PUNC.sub("", t_clean)

    if not t_clean:
        return True  # token hanya berisi punctuation/simbol

    up = t_clean.upper()

    # Token yang memang valid (singkatan agama, angka Romawi)
    if up in TOKEN_WHITELIST:
        return False

    # Token angka murni → khas noise OCR dalam run gibberish
    if t_clean.isdigit():
        return True

    # Single-letter uppercase (W, B, L, K) → sangat khas noise OCR
    if len(t_clean) == 1 and t_clean.isalpha() and t_clean == t_clean.upper():
        return True

    # Campuran lowercase→UPPERCASE (pHI, wJI) → khas noise OCR
    if re.search(r"[a-z][A-Z]{1,}", t_clean):
        return True

    # Token uppercase pendek ≤3 huruf, bukan di whitelist (EL, TJI, KK, GI)
    if t_clean.isalpha() and t_clean == t_clean.upper() and len(t_clean) <= 3:
        return True

    # Campuran digit + huruf (A1, 1A, t1, 8s) → noise
    if re.search(r"\d", t_clean) and re.search(r"[A-Za-z]", t_clean):
        return True

    # Token 1 huruf lowercase (berdiri sendiri) → kemungkinan besar noise
    if len(t_clean) == 1 and t_clean.isalpha() and t_clean == t_clean.lower():
        return True

    # Token 2-3 huruf yang bukan kata umum Indonesia (Ug, fts, fs, fn, etc)
    if t_clean.isalpha() and 2 <= len(t_clean) <= 3:
        if t_clean.lower() not in COMMON_SHORT_WORDS:
            return True

    # Token diawali tanda baca lalu huruf (:ebaI, .abc) → noise
    if re.match(r"^[.:;,\-\)\(]{1,2}[A-Za-z]", t):
        return True

    return False


def purge_isolated_weird_tokens(text: str) -> str:
    """Hapus token individual yang PASTI noise OCR (mix huruf+digit seperti K1Aq)."""
    if not isinstance(text, str):
        return ""
    toks = text.split()
    kept = []
    for t in toks:
        # FIX: perluas stripping punctuation/simbol
        t_clean = _TRAILING_PUNC.sub("", t)
        t_clean = _LEADING_PUNC.sub("", t_clean)
        # Skip if mixed digit+letter (ALWAYS noise in this domain)
        if (t_clean and re.search(r"\d", t_clean) and re.search(r"[A-Za-z]", t_clean)
                and t_clean.upper() not in TOKEN_WHITELIST):
            continue
        kept.append(t)
    return normalize_ws(" ".join(kept))


def remove_gibberish_runs(text: str, min_run_tokens: int = 4) -> str:
    """
    Hapus segmen berupa run token aneh beruntun (≥min_run_tokens token).
    Diturunkan threshold dari 6 → 4 agar bisa menangkap "Ug 8 B L fts s 8 GI, fs".
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    s = text
    tokens = list(re.finditer(r"\S+", s))
    if not tokens:
        return normalize_ws(s)

    spans_to_remove = []
    run_start = None
    run_len = 0
    run_end = 0

    for m in tokens:
        tok = m.group(0)
        weird = token_is_weird(tok)

        if weird:
            if run_start is None:
                run_start = m.start()
                run_len = 1
            else:
                run_len += 1
            run_end = m.end()
        else:
            if run_start is not None and run_len >= min_run_tokens:
                spans_to_remove.append((run_start, run_end))
            run_start = None
            run_len = 0

    # finalize last run
    if run_start is not None and run_len >= min_run_tokens:
        spans_to_remove.append((run_start, run_end))

    if not spans_to_remove:
        return normalize_ws(s)

    # remove from back to front (biar index aman)
    out = s
    for a, b in reversed(spans_to_remove):
        out = out[:a] + " " + out[b:]

    return normalize_ws(out)


def is_gibberish_sentence(s: str) -> bool:
    """
    Deteksi kalimat yang mayoritas token-nya aneh.
    Threshold diturunkan ke 50%.
    """
    s = normalize_ws(s)
    if not s:
        return True

    toks = re.findall(r"\S+", s)

    if len(toks) >= 5:
        weird_cnt = sum(token_is_weird(t) for t in toks)
        if weird_cnt / len(toks) >= 0.50:
            return True

    # Simbol aneh berderet
    if re.search(r"[^\w\s]{8,}", s):
        return True
    if re.search(r"[\\{}|<>\[\]~^]{2,}", s):
        return True

    return False


def remove_gibberish(text: str):
    """
    1) Hapus run token aneh (segment-level)
    2) Split kalimat lalu buang kalimat yang gibberish atau footnote (sentence-level)
    """
    if not isinstance(text, str):
        return "", 0

    # Hapus invisible chars
    t0 = ZWS_RE.sub("", text)

    # (0) hapus token individual yang pasti noise (mix huruf+digit)
    t0 = purge_isolated_weird_tokens(t0)

    # (1) segment-level removal
    t0 = remove_gibberish_runs(t0, min_run_tokens=3)

    # (2) sentence-level removal (gibberish only)
    sents = split_sentences(t0)
    if not sents:
        return normalize_ws(t0), 0

    kept = []
    dropped = 0
    for s in sents:
        if is_gibberish_sentence(s):
            dropped += 1
        else:
            kept.append(s)

    return normalize_ws(" ".join(kept)), dropped


# ── Pipeline utama ───────────────────────────────────────────────────────────
def main():
    # 1. Baca CSV
    df = pd.read_csv(IN_CSV, sep=";", encoding="utf-8-sig")
    print(f"Rows awal: {len(df)}")

    # 2. Filter baris tidak relevan
    bab_norm = df["judul_bab"].fillna("").astype(str).str.strip().str.lower()
    sub_norm = df["judul_sub_bab"].fillna("").astype(str).str.strip().str.lower()

    mask_drop = pd.Series(False, index=df.index)

    if DROP_UNKNOWN_BAB:
        mask_drop |= bab_norm.eq("unknown bab")

    if DROP_BIBLIO:
        # FIX: hapus capture group agar tidak ada UserWarning dari pandas
        pat_biblio = r"bibliografi|daftar\s+pustaka|bibliography|references|referensi"
        mask_drop |= (
            bab_norm.str.contains(pat_biblio, regex=True, na=False) |
            sub_norm.str.contains(pat_biblio, regex=True, na=False)
        )

    df = df[~mask_drop].copy()
    print(f"Rows setelah filter UNKNOWN/BIBLIO: {len(df)}")

    # 3. Preprocessing
    df["teks"] = df["teks"].fillna("").astype(str)
    df["teks_clean"] = df["teks"].apply(light_cleanup)

    # 4. Buang gibberish OCR + kalimat footnote
    tmp = df["teks_clean"].apply(remove_gibberish)
    df["teks_clean"] = tmp.apply(lambda x: x[0])
    df["gibberish_removed_count"] = tmp.apply(lambda x: x[1])

    # 5. Optional filters
    if DROP_EMPTY:
        df = df[df["teks_clean"].str.strip().ne("")].copy()

    if DROP_TOO_SHORT:
        df["_wc"] = df["teks_clean"].apply(lambda x: len(re.findall(r"\S+", x)))
        df = df[df["_wc"] >= MIN_WORDS].copy()
        df.drop(columns=["_wc"], inplace=True)

    print(f"Rows akhir: {len(df)}")

    # 6. Tampilkan statistik
    total_dropped = df["gibberish_removed_count"].sum()
    print(f"Total kalimat gibberish dibuang: {total_dropped}")

    # 7. Quick check: cari sisa 'Ug 8 B L fts' di output
    check = df["teks_clean"].str.contains("Ug 8 B L fts", na=False)
    if check.any():
        print("⚠️  MASIH ADA gibberish 'Ug 8 B L fts' yang lolos!")
    else:
        print("✅ Gibberish 'Ug 8 B L fts' berhasil dihapus!")

    # 8. Simpan output
    df_final = df[["judul_bab", "judul_sub_bab", "halaman", "teks_clean"]].copy()
    df_final.to_csv(OUT_CSV, index=False, sep=";", encoding="utf-8-sig")
    print(f"Output disimpan ke: {OUT_CSV}")


if __name__ == "__main__":
    main()
