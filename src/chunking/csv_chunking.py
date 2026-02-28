import re
import pandas as pd

csv = r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\preprocess_result\csv_result\sirah_simple_clean.csv"
df = pd.read_csv(csv, sep=";", encoding="utf-8-sig")

def split_chunks_grouped(text: str, max_chars=1500):
    if not isinstance(text, str) or not text.strip():
        return []
    t = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+", t)

    chunks = []
    buf = ""
    for s in sents:
        s = s.strip()
        if not s:
            continue
        if len(buf) + 1 + len(s) <= max_chars:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = s
    if buf:
        chunks.append(buf)
    return chunks

rows = []
for idx, r in df.iterrows():
    chunks = split_chunks_grouped(r["teks_clean"])
    if not chunks:
        continue
    for i, c in enumerate(chunks, start=1):
        rows.append({
            "doc_id": idx,
            "chunk_index": i,
            "judul_bab": r["judul_bab"],
            "judul_sub_bab": r["judul_sub_bab"],
            "halaman": r["halaman"],
            "teks_chunk": c
        })

df_chunks = pd.DataFrame(rows)
df_chunks.to_csv(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah\data\preprocess_result\csv_result\sirah_chunks_final.csv", index=False, sep=";", encoding="utf-8-sig")
print("Chunks:", len(df_chunks))
df_chunks.head()
