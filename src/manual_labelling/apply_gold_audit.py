"""
apply_gold_audit.py
===================
Terapkan keputusan gold_audit (GOLD_SALAH) ke sirah_prelabelled.csv sebagai
operasi SPAN, berdasar tabel review yang sudah dikonfirmasi.

Aturan apply-set:
  - status OK_UNIK / OK_KONTEKS         -> apply (default), kecuali acc=N
  - status CURIGA_KATA_UMUM             -> apply hanya jika acc=Y
  - status SUDAH_BENAR / TAK_KETEMU / AMBIGU_MULTI / ALIGN_ERROR -> skip

Operasi span (target koreksi):
  - B-XXX : tambah entitas baru [s,e] label XXX
  - I-XXX : sambung ke entitas XXX tepat sebelum token (toleransi <=3 char non-word
            spt ", "/" "); kalau tak ada -> jadi entitas baru (fallback)
  - O     : potong/buang bagian span yang menutupi token

Default: DRY-RUN (cetak rencana). Pakai --apply untuk menulis + backup + regen BIO.
"""

import re
import sys
import shutil
import argparse
import subprocess
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
sys.path.insert(0, str(ROOT / "src/manual_labelling"))
from pre_labelling import normalize_text
from build_gold_audit_apply_review import (
    parse_md_entries, neighbors, locate, build_chunk_index)

GOLD = ROOT / "data/result/manual_labelling/sirah_prelabelled.csv"
CSV = ROOT / "data/result/manual_labelling/gold_review/gold_audit.csv"
MD = ROOT / "data/result/manual_labelling/gold_review/gold_audit.md"
REVIEW_MD = ROOT / "data/result/manual_labelling/gold_review/gold_audit_apply_review.md"
PREP = ROOT / "src/pseudo_labelling/prepare_bert_data.py"

BASE_COLS = ["chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab",
             "halaman", "teks_chunk"]


def norm(s):
    return re.sub(r"\s+", " ", str(s).replace("...", " ")).strip()


def read_acc(path):
    """no -> acc (Y/N) dari review .md."""
    acc = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\*\*\[(\d+)\]\*\*.*?acc:\s*([A-Za-z]*)", ln)
        if m:
            acc[int(m.group(1))] = m.group(2).strip().upper()
    return acc


def cur_span(spans, s, e):
    for idx, (ss, ee, lab) in enumerate(spans):
        if s < ee and e > ss:
            return idx
    return -1


def build_edits():
    """Kembalikan list edit ter-apply: dict(no,cid,s,e,target,status)."""
    g = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    g.columns = [c.replace("﻿", "").strip() for c in g.columns]
    teks_idx, span_idx = build_chunk_index(g)

    cdf = pd.read_csv(CSV, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    cdf.columns = [c.replace("﻿", "").strip() for c in cdf.columns]
    csv_by_ctx = {}
    for _, cr in cdf.iterrows():
        csv_by_ctx.setdefault(norm(cr["konteks"]), cr)

    entries = parse_md_entries(MD)
    acc = read_acc(REVIEW_MD)

    edits = []
    used = set()  # (cid, start) yang sudah dipakai -> hindari 2 edit ke posisi sama
    for i, ent in enumerate(entries):
        no = i + 1
        if ent["keputusan"] != "GOLD_SALAH":
            continue
        crow = csv_by_ctx.get(norm(ent["konteks"]))
        if crow is None:
            continue
        cid = crow["text_id"]
        target = ent["koreksi"]
        teks = teks_idx.get(cid, "")
        lw, tok, rw = neighbors(crow["konteks"])
        tok = tok or ent["token"]
        s, e, locstat, ncand = locate(teks, tok, lw, rw)
        if s is None:
            continue
        # Penugasan occurrence unik: kalau posisi ini sudah dipakai edit lain,
        # ambil kemunculan token berikutnya yang belum terpakai (kasus "Ummul Fadhl" 2x).
        if (cid, s) in used:
            for m in re.finditer(r"(?<!\w)" + re.escape(tok) + r"(?!\w)", teks):
                if (cid, m.start()) not in used:
                    s, e = m.start(), m.start() + len(tok)
                    break
        used.add((cid, s))
        cl_idx = cur_span(span_idx.get(cid, []), s, e)
        cl = "O"
        if cl_idx >= 0:
            ss, ee, lab = span_idx[cid][cl_idx]
            cl = ("B-" if s == ss else "I-") + lab
        # status
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
        # apply-set decision
        a = acc.get(no, "")
        if status in ("OK_UNIK", "OK_KONTEKS"):
            take = (a != "N")
        elif status == "CURIGA_KATA_UMUM":
            take = (a == "Y")
        else:
            take = False
        if take:
            edits.append({"no": no, "cid": cid, "s": s, "e": e,
                          "target": target, "token": tok, "status": status})
    return g, teks_idx, edits


def _carve(spans, os_, oe):
    """Buang region [os_,oe] dari semua span (hapus label lama di token itu)."""
    new = []
    for (ss, ee, lab) in spans:
        if not (os_ < ee and oe > ss):
            new.append((ss, ee, lab)); continue
        if os_ <= ss and oe >= ee:
            continue  # buang total
        if os_ <= ss < oe < ee:
            new.append((oe, ee, lab))
        elif ss < os_ < ee <= oe:
            new.append((ss, os_, lab))
        else:  # tengah -> split
            new.append((ss, os_, lab)); new.append((oe, ee, lab))
    return sorted(new)


def apply_chunk(spans, teks, edits):
    """spans: list[(s,e,label)]; edits utk chunk ini. Return spans baru."""
    spans = sorted(spans)
    # 1) Carve SEMUA region token edit dari span lama (buang label lama; tangani
    #    reassignment spt Ka'bah B-LOCATION -> I-PERSON & semua target O).
    for ed in edits:
        spans = _carve(spans, ed["s"], ed["e"])
    # 2) add/extend (urut posisi); O sudah selesai di carve.
    for ed in sorted([x for x in edits if x["target"] != "O"], key=lambda x: x["s"]):
        s, e = ed["s"], ed["e"]
        lab = ed["target"].split("-", 1)[1]
        pos = ed["target"][:1]  # B / I
        if pos == "I":
            # sambung ke span label sama yang berakhir <=3 char (spasi/koma) sebelum s
            attached = False
            for k, (ss, ee, l2) in enumerate(spans):
                if l2 == lab and ee <= s and (s - ee) <= 3:
                    spans[k] = (ss, e, lab); attached = True; break
            if not attached:
                spans.append((s, e, lab))  # fallback -> jadi entitas baru
        else:
            spans.append((s, e, lab))
        spans = sorted(spans)
    # 3) bersihkan: buang span kosong, trim whitespace di tepi
    out = []
    for (ss, ee, lab) in spans:
        txt = teks[ss:ee]
        l = ss + (len(txt) - len(txt.lstrip()))
        r = ee - (len(txt) - len(txt.rstrip()))
        if r > l:
            out.append((l, r, lab))
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    g, teks_idx, edits = build_edits()
    print(f"Edit ter-apply: {len(edits)}")
    from collections import Counter
    print("per status:", dict(Counter(e["status"] for e in edits)))
    print("per target:", dict(Counter(e["target"] for e in edits)))

    by_chunk = {}
    for ed in edits:
        by_chunk.setdefault(ed["cid"], []).append(ed)
    print(f"chunk terdampak: {len(by_chunk)}")

    # rebuild rows utk chunk terdampak
    g2 = g.copy()
    base_by_chunk = {cid: grp.iloc[0] for cid, grp in g.groupby("chunk_id")}
    new_rows = []
    log = []
    for cid, eds in by_chunk.items():
        teks = teks_idx.get(cid, "")
        cur = []
        for _, r in g[(g.chunk_id == cid) & (g.label != "")].iterrows():
            try:
                cur.append((int(float(r.start_char)), int(float(r.end_char)), r.label))
            except (ValueError, TypeError):
                pass
        after = apply_chunk(cur, teks, eds)
        # cek overlap (harus 0)
        ov = any(a[0] < b[1] and b[0] < a[1]
                 for i, a in enumerate(after) for b in after[i + 1:])
        log.append((cid, len(cur), len(after),
                    [e["token"] + "→" + e["target"] for e in eds], ov))
        base = base_by_chunk[cid]
        if after:
            for (s, e, lab) in after:
                row = {c: base[c] for c in BASE_COLS}
                row.update({"entity_text": teks[s:e], "label": lab, "notes": "gold_audit",
                            "start_char": s, "end_char": e})
                new_rows.append(row)
        else:
            # chunk jadi tanpa entitas -> tetap sisakan 1 baris kosong (konvensi gold)
            row = {c: base[c] for c in BASE_COLS}
            row.update({"entity_text": "", "label": "", "notes": "",
                        "start_char": "", "end_char": ""})
            new_rows.append(row)

    print("\n=== rencana per chunk (token→target) ===")
    n_ov = 0
    for cid, nb, na, toks, ov in log:
        flag = "  [!!OVERLAP]" if ov else ""
        n_ov += int(ov)
        print(f"  {cid}: span {nb}->{na} | {toks}{flag}")
    print(f"\nChunk dgn overlap: {n_ov} (harus 0)")

    if not args.apply:
        print("\n[DRY-RUN] tidak ada yang ditulis. Tambah --apply untuk menulis.")
        return

    # tulis: hapus baris chunk terdampak, ganti dgn new_rows
    keep = g2[~g2.chunk_id.isin(by_chunk.keys())]
    nb = pd.DataFrame(new_rows, columns=list(g2.columns))
    out = pd.concat([keep, nb], ignore_index=True)
    # urutkan biar rapi: by chunk_id lalu start_char
    out["_sc"] = pd.to_numeric(out["start_char"], errors="coerce").fillna(-1)
    out = out.sort_values(["chunk_id", "_sc"]).drop(columns="_sc").reset_index(drop=True)

    bak = GOLD.with_suffix(".csv.bak_before_audit")
    shutil.copy(GOLD, bak)
    out.to_csv(GOLD, sep=";", encoding="utf-8-sig", index=False)
    print(f"\nBackup: {bak.name}  | Gold ditulis: {len(out)} baris")

    print("Regen BIO...")
    r = subprocess.run([sys.executable, str(PREP)], capture_output=True, text=True)
    print(r.stdout[-600:])
    if r.returncode != 0:
        print("REGEN BIO GAGAL:\n", r.stderr[-800:])


if __name__ == "__main__":
    main()
