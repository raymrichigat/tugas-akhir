"""
Audit kualitas manual labelling (gold) — read-only, tidak mengubah data.

Menjawab kebutuhan: "cek kembali manual labelling agar tidak salah deteksi lagi"
sebelum re-run pipeline. Mendeteksi inkonsistensi yang menurunkan kualitas gold:

  1. OFFSET   : teks_chunk[start:end] != entity_text (drift posisi / OCR)
  2. PUNCT    : span entitas mengandung tanda baca di ujung (artefak OCR)
  3. CONFLICT : surface (teks entitas) yang sama dilabeli >1 kelas berbeda
  4. UNDER    : surface yang dilabeli di sebagian tempat tapi ke-skip di tempat lain
                (termasuk pola kapitalisasi: 'Perang X' kapital terlabel,
                 'perang X' huruf kecil ke-skip — akar masalah regex pre_labelling.py)
  5. DUP/OVL  : span duplikat / tumpang tindih dalam satu chunk
  6. SUSPECT  : entitas mencurigakan (1 huruf, angka saja, hanya tanda baca)

Sumber gold: data/result/manual_labelling/sirah_prelabelled.csv  (sep=';')
  kolom: chunk_id; ...; teks_chunk; entity_text; label; notes; start_char; end_char

Output: data/result/analysis/label_audit/
  label_audit_report.md          (ringkasan + contoh)
  conflict_surface_label.csv      (CONFLICT)
  offset_mismatch.csv             (OFFSET)
  punctuation_spans.csv           (PUNCT)
  under_annotation_candidates.csv (UNDER)
  duplicate_overlap.csv           (DUP/OVL)

Jalankan (dari root):
    venv\Scripts\python.exe src\manual_labelling\audit_labels.py
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis" / "label_audit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PUNCT_EDGE = re.compile(r"^[\W_]+|[\W_]+$", re.UNICODE)
# Apostrof ' adalah bagian SAH transliterasi Arab (Isra', Tha'if, Al-Akwa') → BUKAN error.
# Yang dianggap artefak OCR hanya titik/koma/titik-koma/dll.
TRAIL_PUNCT = re.compile(r"[.,;:!?)\]]$")
LEAD_PUNCT = re.compile(r"^[(\[]")
TRAIL_APOS = re.compile(r"['\"]$")


def norm_surface(s: str) -> str:
    """Normalisasi surface untuk pembanding: lowercase + strip tanda baca ujung."""
    return PUNCT_EDGE.sub("", str(s).strip().lower())


def load_gold() -> pd.DataFrame:
    df = pd.read_csv(GOLD, sep=";", encoding="utf-8-sig").fillna("")
    # baris entitas saja (punya label)
    df = df[df["label"].astype(str).str.strip() != ""].copy()
    for c in ("start_char", "end_char"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["start_char", "end_char"])
    df["start_char"] = df["start_char"].astype(int)
    df["end_char"] = df["end_char"].astype(int)
    df["entity_text"] = df["entity_text"].astype(str)
    df["label"] = df["label"].astype(str).str.strip()
    return df.reset_index(drop=True)


def md_table(headers, rows) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return f"{line}\n{sep}\n{body}"


def main() -> None:
    df = load_gold()
    n_ent = len(df)
    chunk_text = (
        df.drop_duplicates("chunk_id").set_index("chunk_id")["teks_chunk"].astype(str).to_dict()
    )
    print(f"[load] {n_ent} entitas di {df['chunk_id'].nunique()} chunk")

    # ---------- 1. OFFSET mismatch ----------
    off_rows = []
    for r in df.itertuples(index=False):
        text = str(getattr(r, "teks_chunk"))
        sliced = text[r.start_char:r.end_char]
        if sliced != r.entity_text:
            off_rows.append({
                "chunk_id": r.chunk_id, "label": r.label,
                "entity_text": r.entity_text, "sliced": sliced,
                "start_char": r.start_char, "end_char": r.end_char,
            })
    df_off = pd.DataFrame(off_rows)
    df_off.to_csv(OUT_DIR / "offset_mismatch.csv", index=False, encoding="utf-8")

    # ---------- 2. PUNCT in span ----------
    pun_rows = []
    n_apos = 0
    for r in df.itertuples(index=False):
        et = r.entity_text.strip()
        trail = bool(TRAIL_PUNCT.search(et))
        lead = bool(LEAD_PUNCT.search(et))
        if TRAIL_APOS.search(et) and not trail and not lead:
            n_apos += 1  # apostrof valid (transliterasi) — tidak dihitung error
            continue
        if trail or lead:
            pun_rows.append({
                "chunk_id": r.chunk_id, "label": r.label, "entity_text": r.entity_text,
                "trailing": trail, "leading": lead,
            })
    df_pun = pd.DataFrame(pun_rows)
    df_pun.to_csv(OUT_DIR / "punctuation_spans.csv", index=False, encoding="utf-8")
    pun_by_label = df_pun.groupby("label").size().to_dict() if len(df_pun) else {}

    # ---------- 3. CONFLICT surface -> label ----------
    surf_labels = defaultdict(Counter)
    for r in df.itertuples(index=False):
        surf_labels[norm_surface(r.entity_text)][r.label] += 1
    conf_rows = []
    for surf, labs in surf_labels.items():
        if len([l for l in labs if labs[l] > 0]) > 1 and surf:
            total = sum(labs.values())
            major = labs.most_common(1)[0]
            conf_rows.append({
                "surface": surf, "n_total": total,
                "labels": "; ".join(f"{k}={v}" for k, v in labs.most_common()),
                "majority": major[0], "majority_share": round(major[1] / total, 2),
            })
    df_conf = pd.DataFrame(conf_rows).sort_values("n_total", ascending=False) if conf_rows else pd.DataFrame()
    df_conf.to_csv(OUT_DIR / "conflict_surface_label.csv", index=False, encoding="utf-8")

    # ---------- 4. UNDER-annotation ----------
    # 4a. pola 'perang/ghazwah/sariyah X' (akar masalah regex kapitalisasi)
    labeled_spans = defaultdict(list)  # chunk_id -> list (start,end)
    for r in df.itertuples(index=False):
        labeled_spans[r.chunk_id].append((r.start_char, r.end_char))

    def covered(cid, pos) -> bool:
        for (s, e) in labeled_spans.get(cid, []):
            if s <= pos < e:
                return True
        return False

    EVENT_TRIGGER = re.compile(r"\b([Pp]erang|[Gg]hazwah|[Ss]ariyah)\s+([A-Z][\w'-]+)")
    trig_rows = []
    for cid, text in chunk_text.items():
        for m in EVENT_TRIGGER.finditer(text):
            pos = m.start()
            is_lower = m.group(1)[0].islower()
            trig_rows.append({
                "chunk_id": cid, "match": m.group(0), "lowercase_trigger": is_lower,
                "labeled": covered(cid, pos),
            })
    df_trig = pd.DataFrame(trig_rows)

    # 4b. surface under-coverage umum (proper-noun yang ter-label di sebagian tempat)
    #     hitung: berapa kali surface muncul di seluruh teks vs berapa kali ter-label.
    labeled_surface_count = Counter(norm_surface(r.entity_text) for r in df.itertuples(index=False))
    # surface kandidat: yang pernah dilabeli PERSON/LOCATION/EVENT, panjang >=4, multi-huruf
    cand_surfaces = {
        s for s, c in labeled_surface_count.items()
        if len(s) >= 4 and c >= 2 and re.search(r"[a-z]", s) and " " not in s[:0] or len(s) >= 4
    }
    all_text_joined = "\n".join(chunk_text.values())
    under_rows = []
    for surf in sorted(cand_surfaces):
        if not surf or len(surf) < 4:
            continue
        try:
            occ = len(re.findall(r"\b" + re.escape(surf) + r"\b", all_text_joined, flags=re.IGNORECASE))
        except re.error:
            continue
        lab = labeled_surface_count[surf]
        if occ >= 3 and lab / occ < 0.6:  # muncul cukup sering tapi <60% terlabel
            under_rows.append({
                "surface": surf, "occurrences_in_text": occ, "labeled": lab,
                "coverage": round(lab / occ, 2),
            })
    df_under = pd.DataFrame(under_rows).sort_values(
        ["occurrences_in_text"], ascending=False) if under_rows else pd.DataFrame()
    df_under.to_csv(OUT_DIR / "under_annotation_candidates.csv", index=False, encoding="utf-8")

    # ---------- 5. DUPLICATE / OVERLAP ----------
    dup_rows = []
    for cid, grp in df.groupby("chunk_id"):
        spans = sorted([(int(r.start_char), int(r.end_char), r.label, r.entity_text)
                        for r in grp.itertuples(index=False)])
        for i in range(len(spans)):
            s1, e1, l1, t1 = spans[i]
            for j in range(i + 1, len(spans)):
                s2, e2, l2, t2 = spans[j]
                if s2 >= e1:
                    break
                kind = "DUP" if (s1 == s2 and e1 == e2) else "OVERLAP"
                dup_rows.append({
                    "chunk_id": cid, "kind": kind,
                    "a": f"[{s1}:{e1}] {l1} '{t1}'", "b": f"[{s2}:{e2}] {l2} '{t2}'",
                })
    df_dup = pd.DataFrame(dup_rows)
    df_dup.to_csv(OUT_DIR / "duplicate_overlap.csv", index=False, encoding="utf-8")

    # ---------- 6. SUSPECT ----------
    susp_rows = []
    for r in df.itertuples(index=False):
        et = r.entity_text.strip()
        core = PUNCT_EDGE.sub("", et)
        if len(core) <= 1 or core.isdigit() or core == "":
            susp_rows.append({"chunk_id": r.chunk_id, "label": r.label, "entity_text": r.entity_text})
    df_susp = pd.DataFrame(susp_rows)

    # ===================== REPORT =====================
    L = []
    L.append("# Audit Kualitas Manual Labelling (Gold)\n")
    L.append("> Read-only. Sumber: `data/result/manual_labelling/sirah_prelabelled.csv`. "
             "Script: `src/manual_labelling/audit_labels.py`. **Belum mengubah apa pun** — "
             "ini daftar kandidat untuk di-review sebelum perbaikan + re-run.\n")
    L.append(f"\nTotal entitas gold: **{n_ent}** di **{df['chunk_id'].nunique()} chunk**. "
             f"Distribusi: " + ", ".join(f"{k} {v}" for k, v in df['label'].value_counts().items()) + ".\n")

    L.append("\n## Ringkasan temuan\n")
    summ = [
        ["1. Offset mismatch (slice ≠ entity_text)", len(df_off), "offset_mismatch.csv"],
        ["2. Span dgn tanda baca di ujung", len(df_pun), "punctuation_spans.csv"],
        ["3. Konflik surface→label (>1 kelas)", len(df_conf), "conflict_surface_label.csv"],
        ["4. Kandidat under-annotation", len(df_under), "under_annotation_candidates.csv"],
        ["5. Duplikat/overlap span", len(df_dup), "duplicate_overlap.csv"],
        ["6. Entitas mencurigakan", len(df_susp), "(inline)"],
    ]
    L.append(md_table(["Temuan", "Jumlah", "File"], summ))

    # detail 1
    L.append("\n## 1. Offset mismatch\n")
    if len(df_off):
        L.append(f"{len(df_off)} entitas: `teks_chunk[start:end]` ≠ `entity_text` "
                 "(posisi geser → token salah ke-label saat konversi BIO). Contoh:\n")
        for r in df_off.head(8).itertuples(index=False):
            L.append(f"- `{r.chunk_id}` {r.label}: entity_text=`{r.entity_text}` vs "
                     f"slice=`{r.sliced}` [{r.start_char}:{r.end_char}]")
    else:
        L.append("✅ Tidak ada — offset semua konsisten.")

    # detail 2
    L.append("\n## 2. Tanda baca di dalam span (artefak OCR)\n")
    L.append(f"**{len(df_pun)}** entitas dengan titik/koma/kurung di ujung (kandidat artefak OCR). "
             f"Per kelas: " + (", ".join(f"{k} {v}" for k, v in pun_by_label.items()) or "—") + ".\n")
    L.append(f"\n> Catatan: {n_apos} entitas berakhiran apostrof (`Isra'`, `Tha'if`, `Al-Akwa'`) "
             "**TIDAK** dihitung sebagai error — itu transliterasi Arab yang sah.\n")
    L.append("Contoh:\n")
    for r in df_pun.head(8).itertuples(index=False):
        L.append(f"- `{r.chunk_id}` {r.label}: `{r.entity_text}`")

    # detail 3
    L.append("\n## 3. Konflik surface → label\n")
    if len(df_conf):
        L.append("Surface (teks) sama dilabeli >1 kelas. Yang `majority_share` rendah = "
                 "perlu dicek (mungkin salah satu salah). Top 15:\n")
        rows = [[r.surface, r.n_total, r.labels, r.majority, r.majority_share]
                for r in df_conf.head(15).itertuples(index=False)]
        L.append(md_table(["surface", "total", "label (count)", "majority", "share"], rows))
    else:
        L.append("✅ Tidak ada konflik surface→label.")

    # detail 4
    L.append("\n## 4. Under-annotation (akar masalah kapitalisasi)\n")
    if len(df_trig):
        n_lower = int(df_trig["lowercase_trigger"].sum())
        n_lower_unlabeled = int(((df_trig["lowercase_trigger"]) & (~df_trig["labeled"])).sum())
        n_upper = int((~df_trig["lowercase_trigger"]).sum())
        n_upper_labeled = int(((~df_trig["lowercase_trigger"]) & (df_trig["labeled"])).sum())
        L.append(
            f"Pola `perang/ghazwah/sariyah` + kata kapital di seluruh gold:\n"
            f"- Trigger **kapital** (`Perang X`): {n_upper}, ter-label EVENT: {n_upper_labeled} "
            f"({100*n_upper_labeled/max(n_upper,1):.0f}%)\n"
            f"- Trigger **huruf kecil** (`perang X`): {n_lower}, **tidak** ter-label: "
            f"{n_lower_unlabeled} ({100*n_lower_unlabeled/max(n_lower,1):.0f}%)\n"
            f"\n→ Konsisten dengan regex `pre_labelling.py` `_EVENT_PERANG_RE` yang mensyaratkan "
            f"`Perang` kapital. Mention huruf kecil sistematis ke-skip di gold.\n"
        )
        ex = df_trig[(df_trig["lowercase_trigger"]) & (~df_trig["labeled"])].head(8)
        for r in ex.itertuples(index=False):
            L.append(f"- `{r.chunk_id}`: …`{r.match}`… (huruf kecil, tak ter-label)")
    L.append(f"\nSelain itu, {len(df_under)} surface proper-noun muncul ≥3× di teks tapi "
             "<60% ter-label (lihat `under_annotation_candidates.csv`). Top 10:\n")
    if len(df_under):
        rows = [[r.surface, r.occurrences_in_text, r.labeled, r.coverage]
                for r in df_under.head(10).itertuples(index=False)]
        L.append(md_table(["surface", "muncul", "terlabel", "coverage"], rows))

    # detail 5 & 6
    L.append("\n## 5. Duplikat / overlap span\n")
    L.append(f"{len(df_dup)} pasang. " + ("Contoh:" if len(df_dup) else "✅ Tidak ada."))
    for r in df_dup.head(8).itertuples(index=False):
        L.append(f"- `{r.chunk_id}` {r.kind}: {r.a}  ⟷  {r.b}")
    L.append("\n## 6. Entitas mencurigakan (1 huruf / angka saja)\n")
    L.append(f"{len(df_susp)}. " + ("Contoh:" if len(df_susp) else "✅ Tidak ada."))
    for r in df_susp.head(10).itertuples(index=False):
        L.append(f"- `{r.chunk_id}` {r.label}: `{r.entity_text}`")

    L.append("\n## Rekomendasi urutan perbaikan\n")
    L.append(
        "1. **Offset & duplikat** → fix struktural dulu (paling jelas salah).\n"
        "2. **Konflik surface→label** dengan share rendah → review manual, samakan.\n"
        "3. **Tanda baca di span** → trim (bisa otomatis, tapi cek dulu yang sah seperti `Tha'if`).\n"
        "4. **Under-annotation** → keputusan kebijakan: mau case-insensitive untuk EVENT? "
        "Ini menambah entitas → ubah angka. **Diskusikan dengan Bu Diana** karena mengubah test gold.\n"
        "5. Setelah fix → re-run `prepare_bert_data.py` (instan) → re-train (GPU).\n"
    )

    (OUT_DIR / "label_audit_report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"[OK] report -> {OUT_DIR / 'label_audit_report.md'}")
    print(f"  offset={len(df_off)} punct={len(df_pun)} conflict={len(df_conf)} "
          f"under={len(df_under)} dup={len(df_dup)} suspect={len(df_susp)}")


if __name__ == "__main__":
    main()
