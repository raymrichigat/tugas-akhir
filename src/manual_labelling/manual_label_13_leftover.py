"""
manual_label_13_leftover.py
============================
Bantu manual labelling 13 chunks yang gagal dapat pseudo-label di iter 6
(saran Bu Diana: sisa yang tidak terdeteksi sebaiknya di-manual saja).

DUA MODE TEMPLATE:

  A. Template KOSONG (label dari nol):
       python manual_label_13_leftover.py --generate-template
     -> 13 chunk metadata + kolom entity kosong, kamu isi semua manual.

  B. Template AUTO-PRELABELLED (semi-auto seperti pre_labelling.py):
       python manual_label_13_leftover.py --auto-prelabel
     -> Apply regex/keyword pre_labelling ke 13 chunks, hasil deteksi sudah
        ter-fill di template. Kamu tinggal REVIEW (verify/koreksi/hapus FP).
     -> Lebih cepat — hanya butuh review, tidak label dari nol.

LANJUTAN (sama untuk kedua mode):

  - Buka template di Excel, isi/koreksi:
      - entity_text : teks entitas EXACT seperti di teks_chunk
      - label       : PERSON / EVENT / TIME / LOCATION (tanpa prefix B-/I-)
      - Kalau chunk punya >1 entitas: copy baris, ubah entity_text/label
      - Kalau chunk tidak ada entitas: biarkan kolom entity kosong
      - start_char/end_char boleh kosong (script auto-hitung saat merge)

  - Merge & rerun pipeline:
      python manual_label_13_leftover.py --merge
    -> Auto-hitung start_char/end_char
    -> Merge ke sirah_prelabelled.csv (backup ke .bak)
    -> Re-run prepare_bert_data.py (skip via --no-prepare)
    -> train.csv ter-update di data/result/pseudo-labelling/SRL-NER/

CATATAN:
  - 13 chunks didapat dari hasil run baseline iter-6:
    src/pseudo_labelling/SRL-NER/done_running/baseline/output/evaluation/bert-only-sirah-ner-iterative-6-below-0.9.xlsx
  - Format CSV: separator semicolon (;), encoding utf-8-sig (Excel-friendly).
"""

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]

BELOW_XLSX  = ROOT / "src" / "pseudo_labelling" / "SRL-NER" / "done_running" / "baseline" / "output" / "evaluation" / "bert-only-sirah-ner-iterative-6-below-0.9.xlsx"
ALL_CHUNKS  = ROOT / "data" / "result" / "chunking_result" / "sirah_chunks_final.csv"
PRELABELLED = ROOT / "data" / "result" / "manual_labelling" / "sirah_prelabelled.csv"
TEMPLATE    = ROOT / "data" / "result" / "manual_labelling" / "manual_labelling_13_leftover_template.csv"
PREPARE_SCRIPT = ROOT / "src" / "pseudo_labelling" / "prepare_bert_data.py"

VALID_LABELS = {"PERSON", "EVENT", "TIME", "LOCATION"}


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_leftover_chunk_ids() -> list[str]:
    """Ambil 13 chunk_id dari hasil baseline iter-6 below."""
    if not BELOW_XLSX.exists():
        sys.exit(f"ERROR: file below tidak ditemukan: {BELOW_XLSX}")
    df = pd.read_excel(BELOW_XLSX)
    return df["text_id"].drop_duplicates().astype(str).tolist()


def find_position(text: str, entity: str) -> tuple[int, int] | None:
    idx = text.find(entity)
    if idx == -1:
        return None
    return idx, idx + len(entity)


# ── Step 1: generate template ────────────────────────────────────────────────
def generate_template():
    chunk_ids = get_leftover_chunk_ids()
    print(f"Found {len(chunk_ids)} leftover chunks: {chunk_ids}")

    if not ALL_CHUNKS.exists():
        sys.exit(f"ERROR: chunks file tidak ditemukan: {ALL_CHUNKS}")
    df_all = pd.read_csv(ALL_CHUNKS, sep=";", encoding="utf-8-sig")

    df_targets = df_all[df_all["chunk_id"].astype(str).isin(chunk_ids)].copy()
    if len(df_targets) != len(chunk_ids):
        missing = set(chunk_ids) - set(df_targets["chunk_id"].astype(str).tolist())
        print(f"PERINGATAN: {len(missing)} chunk_id tidak ditemukan di sirah_chunks_final.csv: {missing}")

    rows = []
    for _, r in df_targets.iterrows():
        rows.append({
            "chunk_id":    r["chunk_id"],
            "teks_chunk":  r["teks_chunk"],
            "judul_bab":   r.get("judul_bab", ""),
            "entity_text": "",
            "label":       "",
            "start_char":  "",
            "end_char":    "",
        })

    template_df = pd.DataFrame(rows, columns=[
        "chunk_id", "teks_chunk", "judul_bab",
        "entity_text", "label", "start_char", "end_char",
    ])

    TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    template_df.to_csv(TEMPLATE, sep=";", encoding="utf-8-sig", index=False)

    print()
    print(f"OK -> Template: {TEMPLATE}")
    print(f"  - {len(template_df)} chunks ready to label")
    print()
    print("CARA ISI:")
    print("  1. Buka file CSV di Excel (sudah UTF-8 BOM)")
    print("  2. Baca kolom 'teks_chunk' (full text chunk)")
    print("  3. Kalau ada entitas (PERSON/EVENT/TIME/LOCATION):")
    print("       - Isi 'entity_text' dengan teks entitas EXACT (case-sensitive)")
    print("       - Isi 'label' dengan PERSON / EVENT / TIME / LOCATION")
    print("       - start_char/end_char biarkan kosong (auto-hitung)")
    print("  4. Kalau >1 entitas dalam 1 chunk: COPY baris, ubah entity_text/label")
    print("  5. Kalau tidak ada entitas: biarkan kolom entity_text & label kosong")
    print()
    print("Setelah selesai isi, jalankan:")
    print(f"  python {Path(__file__).name} --merge")


# ── Step 1b: auto-prelabel (semi-auto seperti pre_labelling.py) ──────────────
def auto_prelabel():
    """Pre-fill template dengan hasil deteksi extract_entities() dari pre_labelling.py.
    User tinggal review/koreksi di Excel."""
    chunk_ids = get_leftover_chunk_ids()
    print(f"Found {len(chunk_ids)} leftover chunks: {chunk_ids}")

    if not ALL_CHUNKS.exists():
        sys.exit(f"ERROR: chunks file tidak ditemukan: {ALL_CHUNKS}")
    df_all = pd.read_csv(ALL_CHUNKS, sep=";", encoding="utf-8-sig")
    df_targets = df_all[df_all["chunk_id"].astype(str).isin(chunk_ids)].copy()

    # Import extract_entities dari pre_labelling.py (sebelahan)
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from pre_labelling import extract_entities
    except ImportError as e:
        sys.exit(f"ERROR: gagal import extract_entities dari pre_labelling.py: {e}")

    rows = []
    auto_per_chunk = {}
    for _, r in df_targets.iterrows():
        cid = str(r["chunk_id"])
        text = str(r["teks_chunk"])
        bab = r.get("judul_bab", "")
        entities = extract_entities(text)
        auto_per_chunk[cid] = len(entities)

        if entities:
            for ent in entities:
                rows.append({
                    "chunk_id":    cid,
                    "teks_chunk":  text,
                    "judul_bab":   bab,
                    "entity_text": ent["entity_text"],
                    "label":       ent["label"],
                    "start_char":  ent["start_char"],
                    "end_char":    ent["end_char"],
                })
        else:
            # Tidak ada deteksi — 1 baris kosong (user mungkin tambah manual)
            rows.append({
                "chunk_id":    cid,
                "teks_chunk":  text,
                "judul_bab":   bab,
                "entity_text": "",
                "label":       "",
                "start_char":  "",
                "end_char":    "",
            })

    template_df = pd.DataFrame(rows, columns=[
        "chunk_id", "teks_chunk", "judul_bab",
        "entity_text", "label", "start_char", "end_char",
    ])

    TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    template_df.to_csv(TEMPLATE, sep=";", encoding="utf-8-sig", index=False)

    total_auto = sum(auto_per_chunk.values())
    print()
    print(f"OK -> Template (auto-prelabelled): {TEMPLATE}")
    print(f"  - {len(chunk_ids)} chunks scanned")
    print(f"  - {total_auto} entities auto-detected")
    print()
    print("Per-chunk auto-detect:")
    for cid, n in auto_per_chunk.items():
        flag = "OK" if n > 0 else "(0 entities — review manual)"
        print(f"  {cid}: {n} entities  {flag}")
    print()
    print("CARA REVIEW:")
    print("  1. Buka file CSV di Excel")
    print("  2. Untuk tiap baris hasil auto-detect:")
    print("       - VERIFIKASI entity_text & label sudah benar")
    print("       - HAPUS BARIS kalau false positive (deteksi salah)")
    print("       - EDIT entity_text/label kalau ada koreksi")
    print("  3. Untuk chunk dengan 0 entitas: cek manual,")
    print("     tambah baris kalau ada entitas yang ter-miss regex")
    print("  4. Setelah selesai review, jalankan:")
    print(f"       python {Path(__file__).name} --merge")


# ── Step 2: merge ────────────────────────────────────────────────────────────
def merge(skip_prepare: bool = False):
    if not TEMPLATE.exists():
        sys.exit(f"ERROR: Template tidak ditemukan di {TEMPLATE}\n"
                 f"Generate dulu: python {Path(__file__).name} --generate-template")

    df_template = pd.read_csv(TEMPLATE, sep=";", encoding="utf-8-sig").fillna("")
    df_template["chunk_id"]    = df_template["chunk_id"].astype(str).str.strip()
    df_template["entity_text"] = df_template["entity_text"].astype(str).str.strip()
    df_template["label"]       = df_template["label"].astype(str).str.strip().str.upper()

    # Validasi label
    df_filled = df_template[df_template["entity_text"] != ""]
    invalid = df_filled[~df_filled["label"].isin(VALID_LABELS)]
    if len(invalid):
        print("ERROR: Ada label tidak valid (harus PERSON/EVENT/TIME/LOCATION):")
        print(invalid[["chunk_id", "entity_text", "label"]].to_string(index=False))
        sys.exit(1)

    # Build entity rows + metadata-only rows untuk chunk tanpa entitas
    chunk_meta: dict[str, dict] = {}
    chunk_entities: dict[str, list[dict]] = {}
    warnings: list[str] = []

    for _, r in df_template.iterrows():
        cid = r["chunk_id"]
        if cid not in chunk_meta:
            chunk_meta[cid] = {
                "chunk_id":   cid,
                "teks_chunk": r["teks_chunk"],
                "judul_bab":  r.get("judul_bab", ""),
            }
            chunk_entities[cid] = []

        entity = r["entity_text"]
        label  = r["label"]
        if not entity or not label:
            continue  # baris kosong (chunk tanpa entitas — akan di-handle di bawah)

        text = str(r["teks_chunk"])
        sc = str(r.get("start_char", "")).strip()
        ec = str(r.get("end_char", "")).strip()

        # Auto-hitung posisi kalau kosong
        if not sc or not ec:
            pos = find_position(text, entity)
            if pos is None:
                warnings.append(
                    f"  - {cid}: entity '{entity}' tidak ditemukan di teks_chunk → SKIP"
                )
                continue
            sc, ec = pos
            occurrences = text.count(entity)
            if occurrences > 1:
                warnings.append(
                    f"  - {cid}: '{entity}' muncul {occurrences}× — pakai posisi pertama. "
                    f"Kalau salah, edit start_char/end_char manual di template."
                )

        chunk_entities[cid].append({
            **chunk_meta[cid],
            "entity_text": entity,
            "label":       label,
            "start_char":  sc,
            "end_char":    ec,
        })

    # Flatten: tiap chunk punya 1+ baris
    new_rows = []
    for cid, ent_list in chunk_entities.items():
        if ent_list:
            new_rows.extend(ent_list)
        else:
            # Chunk tanpa entitas → 1 baris metadata-only
            new_rows.append({
                **chunk_meta[cid],
                "entity_text": "",
                "label":       "",
                "start_char":  "",
                "end_char":    "",
            })

    new_df = pd.DataFrame(new_rows, columns=[
        "chunk_id", "teks_chunk", "judul_bab",
        "entity_text", "label", "start_char", "end_char",
    ])

    if warnings:
        print("PERINGATAN:")
        for w in warnings:
            print(w)
        print()

    # Stats
    n_chunks   = new_df["chunk_id"].nunique()
    n_entities = (new_df["entity_text"] != "").sum()
    n_no_ent   = sum(1 for c in chunk_entities.values() if not c)
    print(f"Stats template:")
    print(f"  - {n_chunks} chunks total")
    print(f"  - {n_entities} entitas ditambahkan")
    print(f"  - {n_no_ent} chunks tanpa entitas (semua O)")
    print()

    # Backup + merge
    if not PRELABELLED.exists():
        sys.exit(f"ERROR: {PRELABELLED} tidak ditemukan")

    df_existing = pd.read_csv(PRELABELLED, sep=";", encoding="utf-8-sig").fillna("")
    df_existing["chunk_id"] = df_existing["chunk_id"].astype(str).str.strip()

    # Buang chunks yang akan di-update (idempotent kalau di-run ulang)
    df_existing = df_existing[~df_existing["chunk_id"].isin(new_df["chunk_id"].unique())]

    df_combined = pd.concat([df_existing, new_df], ignore_index=True)

    backup = PRELABELLED.with_suffix(".csv.bak")
    if backup.exists():
        backup.unlink()
    PRELABELLED.replace(backup)
    print(f"Backup: {backup.name}")

    df_combined.to_csv(PRELABELLED, sep=";", encoding="utf-8-sig", index=False)
    print(f"Merged -> {PRELABELLED.name}: {len(df_combined)} rows total "
          f"({df_combined['chunk_id'].nunique()} chunks)")

    # Re-run prepare_bert_data.py
    if skip_prepare:
        print()
        print("(--no-prepare) skip running prepare_bert_data.py")
        print("Untuk update train.csv, jalankan manual:")
        print(f"  python {PREPARE_SCRIPT}")
        return

    print()
    print("Running prepare_bert_data.py ...")
    print("=" * 60)
    result = subprocess.run([sys.executable, str(PREPARE_SCRIPT)])
    print("=" * 60)
    if result.returncode != 0:
        sys.exit(f"prepare_bert_data.py exit code = {result.returncode}")

    print()
    print("DONE. train.csv / test.csv / unlabelled.csv updated di:")
    print(f"  {ROOT / 'data' / 'result' / 'pseudo-labelling' / 'SRL-NER'}")
    print()
    print("Langkah berikutnya:")
    print("  1. Upload ulang 3 file CSV ke Drive (MyDrive/TA-Sirah/)")
    print("  2. Re-run notebook E1 baseline di Colab dengan seed yang sudah di-update")


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Manual labelling 13 leftover chunks (saran Bu Diana).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run --generate-template dulu, isi di Excel, lalu --merge.",
    )
    parser.add_argument("--generate-template", action="store_true",
                        help="Generate template CSV KOSONG (label dari nol)")
    parser.add_argument("--auto-prelabel", action="store_true",
                        help="Generate template AUTO-PRELABELLED dengan extract_entities dari pre_labelling.py "
                             "(rekomendasi — kamu tinggal review)")
    parser.add_argument("--merge", action="store_true",
                        help="Merge template terisi ke sirah_prelabelled.csv + re-run prepare_bert_data.py")
    parser.add_argument("--no-prepare", action="store_true",
                        help="Skip running prepare_bert_data.py setelah merge (debug only)")
    args = parser.parse_args()

    if args.auto_prelabel:
        auto_prelabel()
    elif args.generate_template:
        generate_template()
    elif args.merge:
        merge(skip_prepare=args.no_prepare)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
