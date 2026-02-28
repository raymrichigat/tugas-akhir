import json
from pathlib import Path
import pandas as pd

# =========================
# CONFIG
# =========================
JSON_PATH = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\preprocess_result\toc_result\document_full.json")   # path ke JSON kamu
OUT_CSV   = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\preprocess_result\csv_result\sirah_simple.csv")     # output CSV

# =========================
# HELPER: pages -> ranges
# =========================
def pages_to_ranges(pages) -> str:
    """
    Convert [21,22,23,24, 26, 30,31,32] -> "21-24, 26, 30-32"
    """
    if not pages:
        return ""

    # keep only ints, unique, sorted
    nums = sorted({int(p) for p in pages if str(p).strip().isdigit()})
    if not nums:
        return ""

    ranges = []
    start = prev = nums[0]

    for n in nums[1:]:
        if n == prev + 1:
            prev = n
        else:
            # close current range
            if start == prev:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = n

    # close last range
    if start == prev:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{prev}")

    return ", ".join(ranges)

# =========================
# MAIN
# =========================
def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for bab in data:
        judul_bab = (bab.get("bab_title") or "").strip()

        for sub in (bab.get("subbab") or []):
            judul_sub_bab = (sub.get("subbab_title") or "").strip()

            pages = sub.get("pages") or []
            halaman = pages_to_ranges(pages)  # <-- rentang

            content = sub.get("content") or []
            if isinstance(content, list):
                teks = "\n".join([c for c in content if isinstance(c, str)]).strip()
            elif isinstance(content, str):
                teks = content.strip()
            else:
                teks = ""

            rows.append({
                "judul_bab": judul_bab,
                "judul_sub_bab": judul_sub_bab,
                "halaman": halaman,
                "teks": teks
            })

    df = pd.DataFrame(rows)

    # separator ; sesuai permintaan
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig", sep=";")
    print(f"Saved: {OUT_CSV.resolve()} | rows={len(df)}")

if __name__ == "__main__":
    main()
