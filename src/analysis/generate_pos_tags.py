#!/usr/bin/env python3
"""
generate_pos_tags.py — isi kolom `pos_tag` dengan POS riil (Stanza, model `id`)
untuk **Grup C — Ablation POS-tag** (revisi Bu Diana 2026-06-05).

Latar: kolom `pos_tag` di train/test/unlabelled saat ini SEMUA `NN` (placeholder), jadi
POS belum pernah benar-benar dipakai. Script ini mengisinya dengan UPOS riil, di-align
1:1 ke token yang sudah ada (pretokenized — TIDAK mengubah tokenisasi/baris).

Sifat:
  - Idempotent: backup asli ke `<file>.bak_pos` (sekali, tidak ditimpa) sebelum overwrite.
  - Aman: jumlah baris & urutan token tidak berubah; hanya kolom `pos_tag` yang diisi.
  - --dry-run: cek struktur + ringkasan TANPA butuh Stanza (untuk validasi cepat).

Prasyarat (real run, no-GPU tapi perlu install):
    venv\\Scripts\\pip install stanza
    # model id (~sekali, ratusan MB) diunduh otomatis saat pertama jalan, atau:
    venv\\Scripts\\python -c "import stanza; stanza.download('id')"

Contoh:
    # validasi dulu (tanpa Stanza):
    venv\\Scripts\\python src\\analysis\\generate_pos_tags.py --dry-run
    # isi POS riil (semua CSV default):
    venv\\Scripts\\python src\\analysis\\generate_pos_tags.py
    # hanya file tertentu:
    venv\\Scripts\\python src\\analysis\\generate_pos_tags.py --inputs data/result/pseudo-labelling/SRL-NER/test.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, OrderedDict
from pathlib import Path

DEFAULT_REL = [
    "data/result/pseudo-labelling/SRL-NER/train.csv",
    "data/result/pseudo-labelling/SRL-NER/test.csv",
    "data/result/pseudo-labelling/SRL-NER/unlabelled.csv",
    "data/result/pseudo-labelling/SRL-NER/train_augmented_v2.csv",
]
BATCH_CHUNKS = 200  # banyak chunk per panggilan Stanza (kecepatan vs memori)


def find_repo_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / "CLAUDE.md").exists():
            return parent
    return start.resolve().parents[0]


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return reader.fieldnames or [], rows


def group_chunks(rows, text_col: str, token_col: str):
    """Kembalikan OrderedDict text_id -> list token (urutan baris dipertahankan)."""
    chunks: "OrderedDict[str, list]" = OrderedDict()
    for r in rows:
        tid = r[text_col]
        chunks.setdefault(tid, []).append(str(r.get(token_col, "")))
    return chunks


def tag_with_stanza(chunks, pos_col_default="X"):
    """Jalankan Stanza POS pretokenized. Return dict text_id -> list upos (sejajar token)."""
    try:
        import stanza  # noqa
    except ImportError:
        print(
            "[err] Stanza belum terinstall.\n"
            "      Install dulu:  venv\\Scripts\\pip install stanza\n"
            "      (model id diunduh otomatis saat pertama jalan)\n"
            "      Atau cek logika tanpa Stanza:  --dry-run",
            file=sys.stderr,
        )
        sys.exit(2)

    import stanza

    print("[stanza] memuat pipeline id (tokenize,pos) — pretokenized ...")
    try:
        nlp = stanza.Pipeline(
            lang="id",
            processors="tokenize,pos",
            tokenize_pretokenized=True,
            verbose=False,
        )
    except Exception:
        print("[stanza] model 'id' belum ada → mengunduh sekali ...")
        stanza.download("id", verbose=False)
        nlp = stanza.Pipeline(
            lang="id",
            processors="tokenize,pos",
            tokenize_pretokenized=True,
            verbose=False,
        )

    ids = list(chunks.keys())
    out: dict[str, list] = {}
    for start in range(0, len(ids), BATCH_CHUNKS):
        batch_ids = ids[start : start + BATCH_CHUNKS]
        batch_tokens = [chunks[i] or ["_"] for i in batch_ids]
        doc = nlp(batch_tokens)
        sents = doc.sentences
        if len(sents) == len(batch_ids):
            for tid, sent, toks in zip(batch_ids, sents, batch_tokens):
                upos = [w.upos or pos_col_default for w in sent.words]
                out[tid] = _fit_length(upos, len(chunks[tid]), pos_col_default)
        else:
            # fallback per-chunk kalau Stanza menggabung/memecah kalimat
            for tid in batch_ids:
                d = nlp([chunks[tid] or ["_"]])
                upos = [w.upos or pos_col_default for s in d.sentences for w in s.words]
                out[tid] = _fit_length(upos, len(chunks[tid]), pos_col_default)
        print(f"[stanza] {min(start + BATCH_CHUNKS, len(ids))}/{len(ids)} chunk", end="\r")
    print()
    return out


def _fit_length(upos, n, fill):
    """Pastikan panjang upos == jumlah token chunk (potong / pad)."""
    if len(upos) == n:
        return upos
    if len(upos) > n:
        return upos[:n]
    return upos + [fill] * (n - len(upos))


def process_file(path: Path, repo: Path, args, tagger_cache) -> None:
    rel = path.relative_to(repo)
    if not path.exists():
        print(f"[skip] tidak ada: {rel}")
        return

    fields, rows = read_rows(path)
    for need in (args.text_col, args.token_col):
        if need not in fields:
            print(f"[skip] {rel}: kolom '{need}' tidak ada (kolom: {fields})")
            return
    if args.pos_col not in fields:
        # sisipkan kolom pos setelah token bila belum ada
        idx = fields.index(args.token_col) + 1
        fields = fields[:idx] + [args.pos_col] + fields[idx:]

    chunks = group_chunks(rows, args.text_col, args.token_col)
    n_chunks = len(chunks)
    n_tokens = sum(len(v) for v in chunks.values())
    before = Counter(r.get(args.pos_col, "") for r in rows)

    print(f"\n=== {rel} ===")
    print(f"  chunk={n_chunks:,}  token={n_tokens:,}  pos_tag(before)={dict(before)}")

    if args.dry_run:
        print("  [dry-run] OK - struktur valid, Stanza TIDAK dijalankan.")
        return

    if tagger_cache.get("fn") is None:
        tagger_cache["fn"] = tag_with_stanza
    pos_map = tagger_cache["fn"](chunks)

    # tulis balik per baris (urut per text_id, lalu urut baris)
    per_id_iter = {tid: iter(pos_map[tid]) for tid in pos_map}
    new_rows = []
    after = Counter()
    for r in rows:
        tag = next(per_id_iter[r[args.text_col]])
        r[args.pos_col] = tag
        after[tag] += 1
        new_rows.append(r)

    # backup sekali
    bak = path.with_suffix(path.suffix + ".bak_pos")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
        print(f"  backup -> {bak.relative_to(repo)}")

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(new_rows)
    top = ", ".join(f"{k}:{v}" for k, v in after.most_common(6))
    print(f"  [ok] pos_tag terisi. distribusi top: {top}")


def main() -> None:
    repo = find_repo_root(Path(__file__))
    ap = argparse.ArgumentParser(description="Isi kolom pos_tag dengan POS riil (Stanza).")
    ap.add_argument("--inputs", nargs="+", type=Path, default=None,
                    help="Daftar CSV. Default: train/test/unlabelled/train_augmented_v2.")
    ap.add_argument("--text-col", default="text_id")
    ap.add_argument("--token-col", default="token")
    ap.add_argument("--pos-col", default="pos_tag")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validasi struktur tanpa menjalankan Stanza.")
    args = ap.parse_args()

    inputs = args.inputs if args.inputs else [repo / p for p in DEFAULT_REL]
    inputs = [p if p.is_absolute() else (repo / p) for p in inputs]

    tagger_cache: dict = {"fn": None}
    for path in inputs:
        process_file(path, repo, args, tagger_cache)

    if args.dry_run:
        print("\n[dry-run selesai] Untuk isi POS riil: hapus --dry-run (perlu `pip install stanza`).")


if __name__ == "__main__":
    main()
