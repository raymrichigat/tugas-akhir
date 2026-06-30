"""
build_gold_audit_apply_review.py
================================
Bangun TABEL REVIEW aman untuk meng-apply gold_audit (NON-MODEL, lokal).

Kenapa perlu: token gold_audit harus dipetakan ke posisi karakter di teks_chunk
(gold span-level). Pemetaan ini RAWAN untuk token pendek/umum -> jadi kita TIDAK
auto-apply. Skrip ini cuma membuat tabel yang:
  - meng-align keputusan .md dengan .csv via URUTAN baris (entry ke-k <-> csv ke-k),
    sehingga text_id (chunk) selalu benar (memperbaiki bug "cid=?").
  - melokasikan token pakai BATAS KATA + disambiguasi tetangga.
  - memberi STATUS tiap baris supaya reviewer fokus ke yang ragu:
      OK_UNIK          : 1 kemunculan, jelas, current != target  -> aman
      OK_KONTEKS       : banyak kemunculan, terpilih via tetangga -> cek sekilas
      SUDAH_BENAR      : current label == target                 -> no-op (skip)
      CURIGA_KATA_UMUM : token huruf kecil / kata umum           -> WAJIB cek
      AMBIGU_MULTI     : banyak kemunculan, tetangga tak menolong -> WAJIB cek
      TAK_KETEMU       : token tak ditemukan di teks             -> WAJIB cek
  - kolom `acc` diisi reviewer: Y (apply) / N (tolak) / kosong (ikut default).
    Default saat apply: OK_UNIK & OK_KONTEKS -> apply; lainnya -> skip.

Output: gold_review/gold_audit_apply_review.{csv,md}
"""

import re
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
sys.path.insert(0, str(ROOT / "src/manual_labelling"))
from pre_labelling import normalize_text

GOLD = ROOT / "data/result/manual_labelling/sirah_prelabelled.csv"
CSV = ROOT / "data/result/manual_labelling/gold_review/gold_audit.csv"
MD = ROOT / "data/result/manual_labelling/gold_review/gold_audit.md"
OUT_CSV = ROOT / "data/result/manual_labelling/gold_review/gold_audit_apply_review.csv"
OUT_MD = ROOT / "data/result/manual_labelling/gold_review/gold_audit_apply_review.md"


def parse_md_entries(path):
    """Pecah .md jadi blok per-entry (urut). Tiap entry: token, gold, model,
    keputusan, koreksi (jika ada)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # indeks baris header entry
    heads = [i for i, ln in enumerate(lines)
             if re.match(r"^\*\*(.+?)\*\*\s*\(gold=", ln.strip())]
    entries = []
    for k, hi in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        block = "\n".join(lines[hi:end])
        h = re.match(r"^\*\*(.+?)\*\*\s*\(gold=\`(.+?)\`\s*vs model=\`(.+?)\`\)",
                     lines[hi].strip())
        token, gold, model = h.group(1), h.group(2), h.group(3)
        kep = kor = ""
        km = re.search(r"keputusan:\s*([A-Za-z_]+)", block)
        if km:
            kep = km.group(1)
        rm = re.search(r"koreksi:\s*([A-Za-z\-_]+)", block)
        if rm:
            kor = rm.group(1)
        # konteks line (mengandung 〚 〛) -> kunci alignment ke .csv
        konteks = ""
        for ln in lines[hi:end]:
            if "〚" in ln:
                konteks = ln.strip()
                break
        entries.append({"token": token, "gold": gold, "model": model,
                        "keputusan": kep, "koreksi": kor, "konteks": konteks})
    return entries


def build_chunk_index(gold_df):
    teks, spans = {}, {}
    for _, r in gold_df.iterrows():
        cid = r["chunk_id"]
        if r["teks_chunk"]:
            teks.setdefault(cid, normalize_text(r["teks_chunk"]))
        if r["label"]:
            try:
                spans.setdefault(cid, []).append(
                    (int(float(r["start_char"])), int(float(r["end_char"])), r["label"]))
            except (ValueError, TypeError):
                pass
    return teks, spans


def neighbors(konteks):
    mm = re.search(r"〚(.+?)〛", konteks)
    if not mm:
        return "", "", ""
    tok = mm.group(1)
    left = konteks[:mm.start()].replace("...", " ").split()
    right = konteks[mm.end():].replace("...", " ").split()
    return (left[-1] if left else ""), tok, (right[0] if right else "")


def locate(teks, token, lw, rw):
    """Kembalikan (start, end, status_lokasi, jumlah_kandidat)."""
    if not teks:
        return None, None, "TAK_KETEMU", 0
    # batas kata: token bisa mengandung -,',. -> pakai lookaround non-\w
    cands = [m.start() for m in re.finditer(r"(?<!\w)" + re.escape(token) + r"(?!\w)", teks)]
    if not cands:
        return None, None, "TAK_KETEMU", 0
    if len(cands) == 1:
        s = cands[0]
        return s, s + len(token), "UNIK", 1
    best, bestsc = None, -1
    for s in cands:
        pre = teks[max(0, s - 40):s]
        post = teks[s + len(token):s + len(token) + 40]
        sc = (1 if lw and lw in pre else 0) + (1 if rw and rw in post else 0)
        if sc > bestsc:
            bestsc, best = sc, s
    if bestsc <= 0:
        s = cands[0]
        return s, s + len(token), "AMBIGU_MULTI", len(cands)
    return best, best + len(token), "KONTEKS", len(cands)


def cur_label(spans, cid, s, e):
    for ss, ee, lab in spans.get(cid, []):
        if s < ee and e > ss:
            return ("B-" if s == ss else "I-") + lab
    return "O"


def main():
    g = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    g.columns = [c.replace("﻿", "").strip() for c in g.columns]
    teks_idx, span_idx = build_chunk_index(g)

    cdf = pd.read_csv(CSV, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    cdf.columns = [c.replace("﻿", "").strip() for c in cdf.columns]
    entries = parse_md_entries(MD)

    print(f"entry .md: {len(entries)}  baris .csv: {len(cdf)}")

    # Alignment by KONTEKS (string 〚token〛 identik di .md dan .csv).
    def norm(s):
        return re.sub(r"\s+", " ", str(s).replace("...", " ")).strip()
    csv_by_ctx = {}
    for _, cr in cdf.iterrows():
        csv_by_ctx.setdefault(norm(cr["konteks"]), cr)

    rows = []
    n_align_fail = 0
    for i, ent in enumerate(entries):
        if ent["keputusan"] != "GOLD_SALAH":
            continue  # MODEL_SALAH / AMBIGU / kosong -> tidak mengubah gold
        crow = csv_by_ctx.get(norm(ent["konteks"]))
        if crow is None:
            n_align_fail += 1
            rows.append({"no": i + 1, "chunk": "?", "token": ent["token"],
                         "target": ent["koreksi"], "current": "", "status": "ALIGN_ERROR",
                         "acc": "", "konteks_ditemukan": "(konteks .md tak cocok .csv)"})
            continue
        cid = crow["text_id"]
        target = ent["koreksi"]
        teks = teks_idx.get(cid, "")
        lw, tok, rw = neighbors(crow["konteks"])
        tok = tok or ent["token"]
        s, e, locstat, ncand = locate(teks, tok, lw, rw)

        if s is None:
            status, found = "TAK_KETEMU", ""
        else:
            cl = cur_label(span_idx, cid, s, e)
            found = teks[max(0, s - 30):s] + "〚" + teks[s:e] + "〛" + teks[e:e + 30]
            if cl == target:
                status = "SUDAH_BENAR"
            elif tok[:1].islower():
                status = "CURIGA_KATA_UMUM"
            elif locstat == "UNIK":
                status = "OK_UNIK"
            elif locstat == "KONTEKS":
                status = "OK_KONTEKS"
            else:
                status = "AMBIGU_MULTI"
        rows.append({"no": i + 1, "chunk": cid, "token": tok, "target": target,
                     "current": (cl if s is not None else ""), "status": status,
                     "acc": "", "konteks_ditemukan": found.replace("\n", " ")})

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, sep=";", encoding="utf-8-sig", index=False)

    # ringkas
    print("\n=== ringkasan status ===")
    print(out["status"].value_counts().to_string())

    # markdown enak-baca, dikelompokkan per status
    order = ["CURIGA_KATA_UMUM", "AMBIGU_MULTI", "TAK_KETEMU", "ALIGN_ERROR",
             "OK_UNIK", "OK_KONTEKS", "SUDAH_BENAR"]
    md = ["# Review apply gold_audit", "",
          "Isi kolom `acc`: **Y**=apply, **N**=tolak, kosong=ikut default "
          "(OK_UNIK & OK_KONTEKS di-apply; selain itu di-skip).", "",
          "Token bermasalah ditandai 〚...〛 pada konteks yang DITEMUKAN di teks asli "
          "(verifikasi apakah lokasinya benar).", ""]
    for st in order:
        sub = out[out["status"] == st]
        if len(sub) == 0:
            continue
        md.append(f"\n## {st} ({len(sub)})\n")
        for _, r in sub.iterrows():
            md.append(f"- **[{r['no']}]** `{r['chunk']}` **{r['token']}** "
                      f"({r['current']} → {r['target']}) `acc: ___`  \n"
                      f"  {r['konteks_ditemukan']}")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"\nReview CSV : {OUT_CSV.name}")
    print(f"Review MD  : {OUT_MD.name}")


if __name__ == "__main__":
    main()
