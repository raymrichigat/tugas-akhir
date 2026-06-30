"""
fix_time_boundaries.py  (NON-MODEL, lokal)
==========================================
Perbaiki BATAS span TIME yang terpotong / kepecah di gold (sirah_prelabelled.csv).

Akar masalah (regex lama di pre_labelling.py):
  - `tanggal \\d+ \\w+` cuma ambil 1 kata  -> bulan Hijriah multi-kata kepotong
    ("Dzul" seharusnya "Dzul Hijjah"), tahun di ekor ("10 H") tak ikut.
  - gazetteer BULAN_HIJRIAH beda ejaan dgn teks OCR ("Jumada" vs "Jumadal Akhirah").
  - "hari/malam <Hari>" tak digabung dengan "tanggal ..." -> 1 ekspresi jadi 2 span.

Strategi (MURNI perbaikan batas, TIDAK menambah entitas TIME baru):
  1) DATE_RE = regex ekspresi-tanggal yang benar (hari + tanggal + bulan multi-kata
     + ejaan OCR + rentang "atau" + tahun ekor).
  2) Untuk tiap chunk yang SUDAH punya >=1 span TIME: cari match DATE_RE yang
     OVERLAP span TIME eksisting. Semua span TIME yang jatuh di region itu diganti
     1 span = full match DATE_RE (gabung + perpanjang).
  3) Fallback: pasangan TIME bersebelahan dgn gap konektor sederhana
     (spasi / koma / "dari" / "atau") yang tak tertangkap DATE_RE -> tetap digabung.
  4) "dan" (enumerasi bulan beda) & "pada" (preposisi generik) TIDAK auto-gabung;
     dilaporkan di bagian REVIEW supaya bisa dicek manual.

Keputusan user 2026-07-01: cakupan = semua kandidat; rentang "atau" = 1 span.

Default: DRY-RUN (cetak before->after). Pakai --apply untuk menulis + backup + regen BIO.
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

GOLD = ROOT / "data/result/manual_labelling/sirah_prelabelled.csv"
PREP = ROOT / "src/pseudo_labelling/prepare_bert_data.py"
BASE_COLS = ["chunk_id", "doc_id", "chunk_index", "judul_bab", "judul_sub_bab",
             "halaman", "teks_chunk"]

# ── Bulan: multi-kata dulu (alternation greedy), termasuk ejaan OCR yang muncul ──
MONTHS = [
    "Rabi'ul Awwal", "Rabi'ul Akhir", "Rabiul Awwal", "Rabiul Akhir",
    "Jumadal Awwal", "Jumadal Akhirah", "Jumadal Ula", "Jumadal Akhir",
    "Jumadil Ula", "Jumadil Akhir", "Jumadil Awwal", "Jumadil Akhirah",
    "Dzul Qa'dah", "Dzul Qi'dah", "Dzul Hijjah",
    "Muharram", "Shafar", "Safar", "Shafai",
    "Rajab", "Sya'ban", "Syaban", "Ramadhan", "Syawwal", "Jumada",
    # Masehi
    "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
    "Agustus", "September", "Oktober", "November", "Desember",
]
MON = "(?:" + "|".join(re.escape(m) for m in MONTHS) + ")"
DAY = r"(?:Senin|Selasa|Rabu|Kamis|Jum'at|Jumat|Sabtu|Ahad|Minggu)"
YEAR = (r"(?:tahun\s+)?\d+\s*"
        r"(?:Hijriyah|Hijriah|Masehi|nubuwah|SM|H|M|dari\s+nubuwah"
        r"|sebelum\s+hijrah|setelah\s+hijrah|sesudah\s+hijrah)\b")

# cluster waktu-hari fleksibel: "Selasa pagi hari", "malam Selasa", "Hari Senin, malam"
# (toleran kapital di awal kalimat: "Hari", "Malam", dst.)
_TW = r"(?:[Mm]alam|[Pp]agi|[Ss]ore|[Ss]iang|[Hh]ari)"
PRE = r"(?:" + _TW + r"\s+){0,2}(?:" + DAY + r"\s*,?\s*)?(?:" + _TW + r"\s+){0,2}"
TGL = r"(?:tanggal\s+\d+(?:\s+atau\s+\d+)?\s+)?"
MONPART = r"(?:dari\s+)?(?:bulan\s+)?" + MON + r"(?:\s+atau\s+(?:bulan\s+)?" + MON + r")?"
TAIL = r"(?:\s+" + YEAR + r")?"
# Wajib mengandung MIN. satu bulan ATAU "tanggal N" supaya tak match frasa generik.
DATE_RE = re.compile(PRE + TGL + MONPART + TAIL)

# konektor fallback untuk merge 2 TIME bersebelahan (selain DATE_RE)
# "pada" digabung (keputusan user 2026-07-01: 'tahun 5 H pada bulan Syawwal' = 1 rujukan);
# "dan" TIDAK (enumerasi bulan berbeda).
CONNECT_RE = re.compile(r"^[\s,]*(?:dari|atau|pada)?[\s,]*$")
# konektor yang SENGAJA tak di-auto-merge -> review
REVIEW_GAP_RE = re.compile(r"\bdan\b")


def load_gold():
    g = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig", dtype=str).fillna("")
    g.columns = [c.replace("﻿", "").strip() for c in g.columns]
    return g


def chunk_spans(g):
    """text_id -> (teks, list[(s,e,label)])."""
    teks, spans = {}, {}
    for _, r in g.iterrows():
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


def plan_chunk(teks, spans):
    """Kembalikan (new_time_spans, log_lines, review_lines) utk 1 chunk.
    new_time_spans = daftar (s,e) TIME final HASIL koreksi (hanya yg berubah dilaporkan)."""
    times = sorted([(s, e) for s, e, lab in spans if lab == "TIME"])
    if not times:
        return None, [], []
    others = [(s, e, lab) for s, e, lab in spans if lab != "TIME"]

    # 1) Region DATE_RE yang overlap >=1 TIME eksisting
    regions = []
    for m in DATE_RE.finditer(teks):
        rs, re_ = m.start(), m.end()
        # rapikan tepi (buang spasi/koma tepi)
        seg = teks[rs:re_]
        rs += len(seg) - len(seg.lstrip(" ,"))
        re_ -= len(seg) - len(seg.rstrip(" ,"))
        # buang preposisi pembuka — TIME tak boleh diawali "dari/atau/dan/pada/dengan"
        lead = re.match(r"^(?:dari|atau|dan|pada|dengan)\s+", teks[rs:re_])
        if lead:
            rs += lead.end()
        if any(ts < re_ and te > rs for ts, te in times):
            regions.append((rs, re_))

    # 2) Map tiap TIME -> region (kalau ada). Group TIME per region.
    final = []          # span TIME final
    used = [False] * len(times)
    for rs, re_ in regions:
        members = [i for i, (ts, te) in enumerate(times) if ts < re_ and te > rs]
        if not members:
            continue
        for i in members:
            used[i] = True
        # span final = union region & member (region biasanya superset)
        s = min([rs] + [times[i][0] for i in members])
        e = max([re_] + [times[i][1] for i in members])
        final.append((s, e))

    # 3) TIME yang belum ter-region: bawa apa adanya dulu
    for i, (ts, te) in enumerate(times):
        if not used[i]:
            final.append((ts, te))
    final = sorted(set(final))

    # 4) Fallback merge: pasangan final bersebelahan dgn gap konektor sederhana
    merged = []
    review = []
    for span in final:
        if merged:
            ps, pe = merged[-1]
            gap = teks[pe:span[0]]
            if pe <= span[0] and CONNECT_RE.match(gap):
                merged[-1] = (ps, span[1]); continue
        merged.append(span)
    # deteksi sisa pasangan ber-gap "dan"/"pada" utk review (tak digabung)
    for a, b in zip(merged, merged[1:]):
        gap = teks[a[1]:b[0]]
        if 0 <= b[0] - a[1] <= 8 and REVIEW_GAP_RE.search(gap):
            review.append(f"    REVIEW {a}+{b} gap={gap!r}: "
                          f"{teks[a[0]:a[1]]!r} <{gap.strip()}> {teks[b[0]:b[1]]!r}")

    # 5) bandingkan dgn TIME awal -> hanya lapor kalau berubah
    if merged == times:
        return None, [], review
    log = []
    for (s, e) in merged:
        srcs = [t for t in times if t[0] < e and t[1] > s]
        if len(srcs) > 1 or srcs and srcs[0] != (s, e):
            before = " | ".join(repr(teks[ts:te]) for ts, te in srcs)
            log.append(f"    {before}  ->  {teks[s:e]!r}")
    return merged, log, review


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    g = load_gold()
    teks_idx, span_idx = chunk_spans(g)

    changed = {}   # cid -> merged TIME spans
    all_log, all_rev = [], []
    for cid, spans in span_idx.items():
        teks = teks_idx.get(cid, "")
        merged, log, review = plan_chunk(teks, spans)
        if review:
            all_rev.append(cid + ":\n" + "\n".join(review))
        if merged is not None and log:
            changed[cid] = merged
            all_log.append(f"  {cid}\n" + "\n".join(log))

    print("=== KOREKSI BATAS TIME (before -> after) ===")
    print("\n".join(all_log) if all_log else "  (tak ada)")
    print(f"\nChunk terdampak: {len(changed)}")
    if all_rev:
        print("\n=== PERLU REVIEW (gap 'dan'/'pada' — TIDAK digabung otomatis) ===")
        print("\n".join(all_rev))

    if not args.apply:
        print("\n[DRY-RUN] tak ada yang ditulis. Tambah --apply untuk menulis + regen BIO.")
        return

    # Tulis: utk chunk berubah, hapus baris TIME lama, ganti dgn span TIME baru;
    # baris non-TIME chunk itu dipertahankan.
    base_by_chunk = {cid: grp.iloc[0] for cid, grp in g.groupby("chunk_id")}
    keep = g[~g.chunk_id.isin(changed.keys())]
    new_rows = []
    for cid, merged in changed.items():
        teks = teks_idx.get(cid, "")
        base = base_by_chunk[cid]
        # non-TIME tetap
        for _, r in g[(g.chunk_id == cid) & (g.label != "") & (g.label != "TIME")].iterrows():
            new_rows.append(r.to_dict())
        # TIME baru
        for (s, e) in merged:
            row = {c: base[c] for c in BASE_COLS}
            row.update({"entity_text": teks[s:e], "label": "TIME",
                        "notes": "fix_time_boundary", "start_char": s, "end_char": e})
            new_rows.append(row)
        # kalau chunk jadi tak punya entitas sama sekali (mustahil di sini krn ada TIME)
    nb = pd.DataFrame(new_rows, columns=list(g.columns))
    out = pd.concat([keep, nb], ignore_index=True)
    out["_sc"] = pd.to_numeric(out["start_char"], errors="coerce").fillna(-1)
    out = out.sort_values(["chunk_id", "_sc"]).drop(columns="_sc").reset_index(drop=True)

    bak = GOLD.with_suffix(".csv.bak_before_time")
    shutil.copy(GOLD, bak)
    out.to_csv(GOLD, sep=";", encoding="utf-8-sig", index=False)
    print(f"\nBackup: {bak.name} | Gold ditulis: {len(out)} baris")

    print("Regen BIO...")
    r = subprocess.run([sys.executable, str(PREP)], capture_output=True, text=True)
    print(r.stdout[-500:])
    if r.returncode != 0:
        print("REGEN BIO GAGAL:\n", r.stderr[-800:])


if __name__ == "__main__":
    main()
