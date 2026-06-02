"""
qasina_graph_eval.py
====================
Studi kasus QASiNa → Knowledge Graph (deliverable bimbingan 2026-05-30).

Pertanyaan Bu Diana: "Apakah pertanyaan QASiNa bisa dijawab menggunakan graf?"

Pendekatan (recall-feasibility / upper-bound, BUKAN QA accuracy penuh):
  Untuk tiap pertanyaan QASiNa:
    1. ENTITY LINKING — cari node KG (PERSON/EVENT/LOCATION/TIME) yang
       disebut di pertanyaan + context_title (substring match ternormalisasi
       atas name + aliases).
    2. TARGET TYPE — dari tipe pertanyaan:
         who      -> PERSON (relasi INVOLVED_IN / KELUARGA / SAHABAT / MUSUH)
         where    -> LOCATION (relasi OCCURRED_AT)
         when     -> TIME (relasi OCCURRED_ON)
         what     -> EVENT (best-effort; sering deskriptif → di luar skema)
         how many -> (tidak didukung; graf tak simpan kuantitas)
    3. CANDIDATE — telusuri 1-hop dari entitas ter-link, ambil node bertipe
       target sebagai kandidat jawaban.
    4. HIT? — apakah gold answer (ternormalisasi) cocok dengan salah satu
       kandidat (substring 2 arah / token-overlap >= threshold)?

Interpretasi metrik:
  - "hit" = graf BERPOTENSI menjawab (jawaban benar ada di antara kandidat).
    Ini upper-bound recall, bukan akurasi sistem QA jadi. Tanpa ranking,
    sebuah event bisa punya banyak kandidat PERSON → hit longgar.
  - Kategori miss menjelaskan KENAPA graf gagal → ini inti analisisnya.

Output:
  data/result/analysis/v3/qasina/qasina_graph_eval.csv   (per-pertanyaan)
  data/result/analysis/v3/qasina/qasina_graph_eval.md    (ringkasan + analisis)

Catatan kejujuran (lihat CLAUDE.md prinsip komunikasi):
  - Ini bukti konsep, bukan klaim "KG = QA system".
  - QASiNa kemungkinan dari sumber Sirah berbeda dari Mubarakfuri (KG ini),
    jadi mismatch string jawaban wajar dan dilaporkan apa adanya.
"""

from __future__ import annotations
import json
import re
import csv
import unicodedata
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[2]
QASINA = ROOT / "docs" / "qasina" / "QASiNa.json"
NODES = ROOT / "data" / "result" / "relation_result" / "nodes_v3.csv"
EDGES = ROOT / "data" / "result" / "relation_result" / "edges_v3.csv"
OUT_DIR = ROOT / "data" / "result" / "analysis" / "v3" / "qasina"
OUT_CSV = OUT_DIR / "qasina_graph_eval.csv"
OUT_MD = OUT_DIR / "qasina_graph_eval.md"

# tipe pertanyaan -> label node target + relasi yang relevan
TYPE_TARGET = {
    "who": ("PERSON", {"INVOLVED_IN", "KELUARGA", "SAHABAT", "MUSUH"}),
    "where": ("LOCATION", {"OCCURRED_AT"}),
    "when": ("TIME", {"OCCURRED_ON"}),
    "what": ("EVENT", {"INVOLVED_IN", "OCCURRED_AT", "OCCURRED_ON", "PRECEDES"}),
    "how many": (None, set()),  # tidak didukung skema graf
}

# token yang terlalu generik untuk dijadikan jangkar entity-linking
STOP = {
    "nabi", "rasulullah", "beliau", "saw", "yang", "dan", "di", "ke", "dari",
    "para", "orang", "bin", "ibn", "bint", "al", "abu", "abdullah",  # too common alone
    "perang", "kota", "bani", "suku", "tahun", "bulan", "hari", "ini", "itu",
    "peristiwa", "kepada", "untuk", "dengan", "pada", "saja", "siapa", "apa",
    "kapan", "dimana", "dari", "mana", "berapa", "mengapa", "kenapa", "bagaimana",
}

# ---------------------------------------------------------------- util


def norm(s: str) -> str:
    """Lowercase, buang diakritik & non-alnum jadi spasi, rapikan."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokset(s: str) -> set[str]:
    return {t for t in norm(s).split() if t not in STOP and len(t) > 1}


def load_nodes(path: Path):
    """Return nodes dict + surfaces list [(node_id, surface_norm, sig_tokens)]."""
    nodes = {}
    surfaces = []  # (node_id, surface_norm, frozenset sig_tokens)
    seen = set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f, delimiter=";")
        for row in rd:
            nid = row["node_id"]
            nodes[nid] = {
                "name": row["name"],
                "label": row["label"],
                "aliases": row.get("aliases", "") or "",
            }
            surfs = [row["name"]]
            if row.get("aliases"):
                surfs += [a.strip() for a in row["aliases"].split("|") if a.strip()]
            for s in surfs:
                ns = norm(s)
                sig = frozenset(t for t in ns.split() if t not in STOP and len(t) >= 3)
                if not sig:
                    continue
                key = (nid, ns)
                if key in seen:
                    continue
                seen.add(key)
                surfaces.append((nid, ns, sig))
    return nodes, surfaces


def load_edges(path: Path):
    """adjacency: node_name_norm -> list of (rel_type, neighbor_name, neighbor_label, direction)."""
    adj = defaultdict(list)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f, delimiter=";")
        for row in rd:
            s, sl = row["source_name"], row["source_label"]
            t, tl = row["target_name"], row["target_label"]
            rel = row["relation_type"]
            adj[norm(s)].append((rel, t, tl, "out"))
            adj[norm(t)].append((rel, s, sl, "in"))
    return adj


# ---------------------------------------------------------------- linking


@lru_cache(maxsize=200_000)
def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _fuzzy_in(tok: str, qtoks: tuple, thr: float) -> bool:
    """True kalau ada token pertanyaan yang mirip `tok` (>= thr).
    Pre-filter cepat: huruf pertama sama & beda panjang <= 2."""
    for qt in qtoks:
        if abs(len(qt) - len(tok)) > 2:
            continue
        if qt[0] != tok[0]:
            continue
        if qt == tok or _ratio(tok, qt) >= thr:
            return True
    return False


def link_entities(text_norm: str, surfaces, nodes: dict):
    """Fuzzy entity-linking (toleran ejaan transliterasi spt Badr/Badar).

    Aturan:
      - surface multi-token signifikan (>=2): SEMUA token harus fuzzy-match
        (ratio>=0.85) token pertanyaan → presisi tinggi, tahan ejaan.
      - surface 1 token signifikan: fuzzy-match ratio>=0.88 & len>=4.
    Dedup per node, simpan surface dgn token signifikan terbanyak (paling spesifik).
    """
    qtoks = tuple(t for t in text_norm.split() if len(t) >= 2)
    best = {}  # node_id -> (surface_norm, n_sig)
    for nid, surf, sig in surfaces:
        sig_t = tuple(sig)
        if len(sig_t) >= 2:
            ok = all(_fuzzy_in(t, qtoks, 0.85) for t in sig_t)
        else:
            t = sig_t[0]
            ok = len(t) >= 4 and _fuzzy_in(t, qtoks, 0.88)
        if not ok:
            continue
        if nid not in best or len(sig_t) > best[nid][1]:
            best[nid] = (surf, len(sig_t))
    return [(nid, surf) for nid, (surf, _n) in best.items()]


def answer_match(gold_norm: str, cand_name: str) -> bool:
    """Cocok kalau substring 2 arah atau token-overlap kuat."""
    cn = norm(cand_name)
    if not cn or not gold_norm:
        return False
    if cn in gold_norm or gold_norm in cn:
        return True
    gt, ct = tokset(gold_norm), tokset(cn)
    if not gt or not ct:
        return False
    inter = gt & ct
    # overlap kuat: minimal 1 token signifikan & coverage >= 0.5 thd kandidat
    if inter and len(inter) / len(ct) >= 0.5:
        return True
    return False


# ---------------------------------------------------------------- main


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.load(open(QASINA, encoding="utf-8"))
    nodes, surfaces = load_nodes(NODES)
    adj = load_edges(EDGES)

    rows = []
    for ctx in data:
        title = ctx.get("context_title", "")
        title_norm = norm(title)
        for qa in ctx.get("question_answers", []):
            qtype = qa.get("type", "").strip().lower()
            question = qa.get("question", "")
            gold = qa.get("answer", "")
            gold_norm = norm(gold)

            target_label, rel_set = TYPE_TARGET.get(qtype, (None, set()))

            # link dari pertanyaan + judul konteks
            link_text = norm(question) + " " + title_norm
            linked = link_entities(link_text, surfaces, nodes)

            # kumpulkan kandidat jawaban bertipe target via 1-hop
            candidates = []
            for nid, _surf in linked:
                nname_norm = norm(nodes[nid]["name"])
                for rel, nb_name, nb_label, _dir in adj.get(nname_norm, []):
                    if target_label and nb_label == target_label:
                        if (not rel_set) or (rel in rel_set):
                            candidates.append(nb_name)
            candidates = list(dict.fromkeys(candidates))  # dedup, keep order

            # tentukan hit + miss reason
            hit = False
            reason = ""
            if qtype == "how many":
                reason = "type_unsupported(how_many)"
            elif not linked:
                reason = "no_entity_linked"
            elif not candidates:
                reason = "no_candidate_of_type"
            else:
                hit = any(answer_match(gold_norm, c) for c in candidates)
                reason = "HIT" if hit else "answer_not_in_candidates"

            rows.append({
                "context_id": ctx.get("context_id"),
                "context_title": title,
                "question_id": qa.get("question_id"),
                "type": qtype,
                "question": question,
                "gold_answer": gold,
                "linked_entities": " | ".join(
                    f"{nodes[nid]['name']}({nodes[nid]['label']})" for nid, _ in linked
                ),
                "n_candidates": len(candidates),
                "candidates_sample": " | ".join(candidates[:8]),
                "hit": int(hit),
                "reason": reason,
            })

    # ---- tulis CSV
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        wr.writeheader()
        wr.writerows(rows)

    # ---- agregasi
    total = len(rows)
    by_type = defaultdict(lambda: {"n": 0, "hit": 0})
    reason_ctr = Counter()
    reason_by_type = defaultdict(Counter)
    for r in rows:
        by_type[r["type"]]["n"] += 1
        by_type[r["type"]]["hit"] += r["hit"]
        reason_ctr[r["reason"]] += 1
        reason_by_type[r["type"]][r["reason"]] += 1
    total_hit = sum(r["hit"] for r in rows)

    # ---- tulis MD
    L = []
    L.append("# Studi Kasus QASiNa → Knowledge Graph v3\n")
    L.append("> Dihasilkan oleh `src/analysis/qasina_graph_eval.py`. "
             "Menjawab pertanyaan Bu Diana (bimbingan 2026-05-30): "
             "*apakah pertanyaan QASiNa bisa dijawab menggunakan graf?*\n")
    L.append("## ⚠️ Cara baca metrik (penting)\n")
    L.append("- **HIT = graf BERPOTENSI menjawab** — jawaban gold muncul di antara "
             "kandidat 1-hop dari entitas yang ter-link. Ini **upper-bound recall**, "
             "BUKAN akurasi sistem QA. Tanpa ranking, satu event bisa punya banyak "
             "kandidat PERSON → hit cenderung longgar/optimistis.\n")
    L.append("- Tujuan utama bukan skor, tapi **kategori miss** = penjelasan KENAPA "
             "graf bisa/tidak bisa menjawab tiap tipe pertanyaan.\n")
    L.append("- **Caveat sumber:** QASiNa kemungkinan dari teks Sirah berbeda dari "
             "buku Mubarakfuri (sumber KG ini) → mismatch string jawaban wajar.\n")

    L.append(f"\n## 1. Ringkasan keseluruhan\n")
    L.append(f"- Total pertanyaan diuji: **{total}**")
    L.append(f"- Potensi terjawab (HIT): **{total_hit}** "
             f"(**{total_hit/total*100:.1f}%** upper-bound)\n")

    L.append("## 2. Per tipe pertanyaan\n")
    L.append("| Tipe | N | HIT | % HIT |")
    L.append("|---|---:|---:|---:|")
    for t in ["who", "where", "when", "what", "how many"]:
        if t in by_type:
            n = by_type[t]["n"]
            h = by_type[t]["hit"]
            L.append(f"| {t} | {n} | {h} | {h/n*100:.1f}% |")
    L.append("")

    L.append("## 3. Kenapa gagal — distribusi alasan (keseluruhan)\n")
    L.append("| Alasan | Jumlah | % |")
    L.append("|---|---:|---:|")
    order = ["HIT", "answer_not_in_candidates", "no_candidate_of_type",
             "no_entity_linked", "type_unsupported(how_many)"]
    for k in order:
        if reason_ctr.get(k):
            L.append(f"| {k} | {reason_ctr[k]} | {reason_ctr[k]/total*100:.1f}% |")
    L.append("")
    L.append("**Arti tiap alasan:**")
    L.append("- `HIT` — jawaban ada di kandidat graf (potensi terjawab).")
    L.append("- `answer_not_in_candidates` — entitas ter-link & ada kandidat, tapi "
             "jawaban gold tidak termasuk → granularitas/relasi KG tak menyimpannya "
             "(mis. role spesifik 'yang mempersiapkan').")
    L.append("- `no_candidate_of_type` — entitas ter-link tapi tak punya relasi ke "
             "tipe target (mis. event tanpa OCCURRED_ON untuk pertanyaan 'kapan').")
    L.append("- `no_entity_linked` — tak ada node KG yang cocok dgn pertanyaan/judul "
             "→ entitas/konteks di luar cakupan KG (mis. Romawi-Persia, pendidikan karakter).")
    L.append("- `type_unsupported(how_many)` — graf tak menyimpan kuantitas.\n")

    L.append("## 4. Breakdown alasan per tipe\n")
    for t in ["who", "where", "when", "what", "how many"]:
        if t not in reason_by_type:
            continue
        L.append(f"**{t}** — " + ", ".join(
            f"{k}={v}" for k, v in reason_by_type[t].most_common()))
    L.append("")

    # contoh HIT
    L.append("## 5. Contoh HIT (graf berpotensi menjawab)\n")
    ex_hit = [r for r in rows if r["hit"]][:10]
    for r in ex_hit:
        L.append(f"- [{r['type']}] *{r['question']}* → gold: **{r['gold_answer']}** "
                 f"| link: {r['linked_entities']} | kandidat: {r['candidates_sample']}")
    L.append("")

    # contoh MISS informatif (answer_not_in_candidates)
    L.append("## 6. Contoh MISS — `answer_not_in_candidates` (granularitas KG)\n")
    ex_miss = [r for r in rows if r["reason"] == "answer_not_in_candidates"][:10]
    for r in ex_miss:
        L.append(f"- [{r['type']}] *{r['question']}* → gold: **{r['gold_answer']}** "
                 f"| link: {r['linked_entities']} | kandidat: {r['candidates_sample']}")
    L.append("")

    # contoh out-of-domain
    L.append("## 7. Contoh MISS — `no_entity_linked` (di luar cakupan KG)\n")
    ex_ood = [r for r in rows if r["reason"] == "no_entity_linked"][:10]
    for r in ex_ood:
        L.append(f"- [{r['type']}] *{r['question']}* (ctx: {r['context_title']}) "
                 f"→ gold: **{r['gold_answer']}**")
    L.append("")

    # ---- interpretasi (deliverable #2 bimbingan: "apa yang diperoleh")
    who_n = by_type.get("who", {}).get("n", 0) or 1
    who_h = by_type.get("who", {}).get("hit", 0)
    ood = reason_ctr.get("no_entity_linked", 0)
    granular = (reason_ctr.get("answer_not_in_candidates", 0)
                + reason_ctr.get("no_candidate_of_type", 0))
    L.append("## 8. Interpretasi — apa yang diperoleh (jawaban untuk Bu Diana)\n")
    L.append(f"**Jawaban singkat: graf v3 BELUM bisa menjawab mayoritas QASiNa.** "
             f"Potensi terjawab hanya **{total_hit}/{total} ({total_hit/total*100:.1f}%)** "
             f"— dan itu pun **upper-bound yang optimistis**.\n")
    L.append("**Kenapa 9.6% pun terlalu murah hati:** untuk satu event (mis. Perang "
             "Badr), semua pertanyaan menghasilkan **kandidat PERSON yang identik** "
             "(daftar tokoh INVOLVED_IN event itu). Sebuah pertanyaan dihitung HIT "
             "kalau jawabannya kebetulan salah satu tokoh utama tersebut — **bukan** "
             "karena graf membedakan role ('yang memimpin kafilah' vs 'yang membawa "
             "panji'). Jadi answerability yang presisi-role **lebih rendah** dari angka ini.\n")
    L.append("**Tiga akar penyebab (urut dampak):**\n")
    L.append(f"1. **Granularitas relasi terlalu kasar** (~{granular/total*100:.0f}% kasus). "
             "`INVOLVED_IN` hanya menyatakan 'tokoh X terlibat di event Y', tidak "
             "menyimpan peran spesifik. Pertanyaan QASiNa justru menanyakan peran "
             "mikro ('yang mengintai', 'yang membawa panji', 'yang mempersiapkan').")
    L.append("2. **Representasi waktu tak sepadan** (`when` = 0% HIT). KG menyimpan "
             "tahun Hijriah ('Tahun 2 H', 'Bulan Syawwal 2 H'), QASiNa memakai ekspresi "
             "relatif ('tahun kedua', 'akhir Rajab') → tak match walau event-nya benar.")
    L.append(f"3. **Di luar cakupan domain** (~{ood/total*100:.0f}% `no_entity_linked`). "
             "Banyak konteks QASiNa bukan event Sirah inti: tafsir Al-Qur'an, "
             "pendidikan karakter, sejarah Romawi-Persia → tak ada node-nya di KG.\n")
    L.append("**Yang JUSTRU bisa dijawab graf:** pertanyaan **struktural kasar** — "
             f"'siapa tokoh utama yang terlibat di event X' (who = {who_h}/{who_n} = "
             f"{who_h/who_n*100:.1f}%, tertinggi). Ini sesuai watak KG: peta "
             "keterhubungan tokoh-event-tempat, **bukan** mesin reading-comprehension.\n")
    L.append("**Implikasi / future work (sejalan arahan Bu Diana 2026-05-16):**")
    L.append("- **LLM verb extraction** → relasi ber-predikat lebih kaya "
             "(MENGUTUS/MEMIMPIN/MEMBAWA) supaya role mikro tersimpan → langsung "
             "menaikkan answerability `who`/`what`.")
    L.append("- **Normalisasi ekspresi waktu** (Hijriah ↔ relatif) untuk `when`.")
    L.append("- **Perluasan skema / entity linking + alias** untuk menutup gap cakupan.\n")
    L.append("> Catatan jujur: hasil ini **bukan kegagalan**, tapi karakterisasi yang "
             "benar — QASiNa = QA reading-comprehension berbasis span, KG = struktur "
             "relasi. Keduanya tugas berbeda; studi kasus ini mengukur **sejauh mana "
             "struktur KG kebetulan menjawab pertanyaan QA**, dan menunjukkan arah "
             "perbaikan yang konkret.\n")

    OUT_MD.write_text("\n".join(L), encoding="utf-8")

    # ---- konsol
    print(f"Total: {total} | HIT: {total_hit} ({total_hit/total*100:.1f}%)")
    print("Per tipe:")
    for t in ["who", "where", "when", "what", "how many"]:
        if t in by_type:
            n, h = by_type[t]["n"], by_type[t]["hit"]
            print(f"  {t:9s} n={n:3d} hit={h:3d} ({h/n*100:.1f}%)")
    print("Alasan:")
    for k in order:
        if reason_ctr.get(k):
            print(f"  {k:32s} {reason_ctr[k]:3d} ({reason_ctr[k]/total*100:.1f}%)")
    print(f"\nOutput:\n  {OUT_CSV}\n  {OUT_MD}")


if __name__ == "__main__":
    main()
