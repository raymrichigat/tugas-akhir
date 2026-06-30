"""
build_koreksi_showcase.py  (NON-MODEL, lokal)
=============================================
Bangun dokumen "kesalahan -> perbaikan -> hasil" per entitas, untuk ditunjukkan
ke pembimbing/penguji. Sumber: worksheet & review yang sudah dikonfirmasi user.

Output: data/result/manual_labelling/gold_review/koreksi_gold_showcase.{md,csv}
Kolom: kategori | chunk | konteks | label_sebelum | masalah | label_sesudah
"""
import re
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
GR = ROOT / "data/result/manual_labelling/gold_review"
LOC_MD = GR / "location_event_review.md"
REV_CSV = GR / "gold_audit_apply_review.csv"
REV_MD = GR / "gold_audit_apply_review.md"
OUT_MD = GR / "koreksi_gold_showcase.md"
OUT_CSV = GR / "koreksi_gold_showcase.csv"


def clean(s):
    return str(s).replace("〚", "[[").replace("〛", "]]").replace("\n", " ").strip()


# ── 1. LOC<->EVENT (dari location_event_review.md, keputusan EVENT atau O) ──
def parse_loc_event():
    rows = []
    lines = LOC_MD.read_text(encoding="utf-8").splitlines()
    pend = None
    kalimat = ""
    for ln in lines:
        m = re.match(r"^\*\*\[(\d+)\]\*\*.*?chunk\s+([0-9-]+)", ln.strip())
        if m:
            pend = m.group(2); kalimat = ""; continue
        if ln.strip().startswith(">"):
            kalimat = ln.strip().lstrip("> ").strip(); continue
        k = re.search(r"`keputusan:\s*([A-Za-z?]+)\s*`", ln.strip())
        if k and pend:
            kep = k.group(1).upper()
            if kep in ("EVENT", "O"):
                rows.append({
                    "kategori": "Ambiguitas LOCATION vs EVENT",
                    "chunk": pend, "konteks": clean(kalimat),
                    "label_sebelum": "LOCATION",
                    "masalah": "nama medan dibaca sbg tempat, padahal konteks = peristiwa"
                               if kep == "EVENT" else "bukan entitas pada konteks ini",
                    "label_sesudah": kep,
                })
            pend = None
    return rows


# ── 2. gold_audit (dari review csv + acc di review md) ──
def read_acc():
    acc = {}
    for ln in REV_MD.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\*\*\[(\d+)\]\*\*.*?acc:\s*([A-Za-z]*)", ln)
        if m:
            acc[int(m.group(1))] = m.group(2).strip().upper()
    return acc


def parse_gold_audit():
    df = pd.read_csv(REV_CSV, sep=";", encoding="utf-8-sig").fillna("")
    acc = read_acc()
    rows = []
    for _, r in df.iterrows():
        st = r["status"]
        applied = st in ("OK_UNIK", "OK_KONTEKS") or (
            st == "CURIGA_KATA_UMUM" and acc.get(int(r["no"]), "") == "Y")
        if not applied:
            continue
        cur, tgt = r["current"], r["target"]
        if cur == "O" and tgt.startswith("B-"):
            kat, mas = "Entitas kelewat", "tidak ter-anotasi di gold (regex tak menangkap)"
        elif tgt == "O":
            kat, mas = "Salah anotasi (dibuang)", "ditandai entitas padahal bukan"
        elif tgt.startswith("I-"):
            kat, mas = "Batas entitas diperbaiki", "token seharusnya bagian dari entitas sebelumnya"
        else:
            kat, mas = "Salah tipe", "tipe entitas keliru"
        rows.append({"kategori": kat, "chunk": r["chunk"], "konteks": clean(r["konteks_ditemukan"]),
                     "label_sebelum": cur, "masalah": mas, "label_sesudah": tgt})
    return rows


# ── 3. nasab + 4. apostrof (contoh kurasi) ──
def curated():
    nasab = {
        "kategori": "Rantai nasab dipecah",
        "chunk": "000016-001",
        "konteks": "...bin Lamk, bin Matausyalakh bin Akhnukh atau Idris, bin Yard...",
        "label_sebelum": "rantai disambung tak konsisten / 'bin' ikut PERSON",
        "masalah": "tiap leluhur orang berbeda, tapi tergabung jadi 1 span",
        "label_sesudah": "tiap nama = PERSON terpisah, 'bin' = O",
    }
    apos = []
    for k, v in {"Tha if": "Tha'if", "Mas ud": "Mas'ud", "Asy ari": "Asy'ari",
                 "Mush ab": "Mush'ab"}.items():
        apos.append({
            "kategori": "OCR apostrof (nama ter-split)", "chunk": "(banyak)",
            "konteks": f"'{k}' -> '{v}'", "label_sebelum": f"'{k}' (terpisah)",
            "masalah": "apostrof hilang jadi spasi -> nama terpecah",
            "label_sesudah": f"'{v}' (tersambung)"})
    return [nasab] + apos


def main():
    loc = parse_loc_event()
    aud = parse_gold_audit()
    cur = curated()
    allrows = loc + aud + cur
    df = pd.DataFrame(allrows, columns=["kategori", "chunk", "konteks",
                                        "label_sebelum", "masalah", "label_sesudah"])
    df.to_csv(OUT_CSV, sep=";", encoding="utf-8-sig", index=False)

    # ringkas per kategori
    md = ["# Showcase Koreksi Gold (kesalahan → perbaikan → hasil)", "",
          "Dokumen ini menampilkan kesalahan anotasi yang ditemukan, letaknya, "
          "dan hasil perbaikannya. Disusun otomatis dari worksheet review yang "
          "sudah dikonfirmasi.", "",
          "## Ringkasan jumlah koreksi", ""]
    vc = df["kategori"].value_counts()
    for k, v in vc.items():
        md.append(f"- **{k}**: {v}")
    md.append(f"\n**Total: {len(df)} koreksi**\n")
    for kat in vc.index:
        sub = df[df["kategori"] == kat]
        md.append(f"\n## {kat} ({len(sub)})\n")
        md.append("| chunk | konteks | sebelum | masalah | sesudah |")
        md.append("|---|---|---|---|---|")
        for _, r in sub.iterrows():
            kx = r["konteks"][:90].replace("|", "\\|")
            md.append(f"| {r['chunk']} | {kx} | `{r['label_sebelum']}` | "
                      f"{r['masalah']} | `{r['label_sesudah']}` |")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Total koreksi: {len(df)}")
    print(vc.to_string())
    print(f"\n-> {OUT_MD.name}\n-> {OUT_CSV.name}")


if __name__ == "__main__":
    main()
