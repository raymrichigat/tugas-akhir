#!/usr/bin/env python3
"""
regen_paraphrase_clean.py — Regenerasi 6 chunk paraphrase augmentasi dengan versi BERSIH
(parafrase struktur kalimat, SEMUA mention entitas dipertahankan persis dari chunk base).

Metode label-alignment yang menjamin BIO benar:
  - Ambil daftar entitas (tipe + surface) per chunk base dari train.csv (urut kemunculan).
  - Parafrase ditulis sudah TER-TOKENISASI (dipisah spasi, tanda baca token tersendiri),
    dengan setiap mention entitas ditulis persis sama seperti di base.
  - Skrip menyusuri token parafrase, mencocokkan tiap entitas base secara berurutan
    (contiguous match), memberi B-/I- pada token entitas, sisanya O. Assertion memastikan
    setiap entitas base ketemu → kalau tidak, error (bukan diam-diam salah).

Menulis hasil ke `train_augmented_final.csv` menggantikan baris `<base>_para1` yang lama.
Backup dibuat sebelum menimpa.

Jalankan: venv\\Scripts\\python src\\pseudo_labelling\\SRL-NER\\regen_paraphrase_clean.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
from seqeval.metrics.sequence_labeling import get_entities

ROOT = Path(__file__).resolve().parents[3]
TRAIN = ROOT / "data" / "result" / "pseudo-labelling" / "SRL-NER" / "train.csv"
FINAL = (ROOT / "data" / "result" / "manual_labelling" / "gold_review" /
         "training_bundle_corrected_gold_20260704" / "train_augmented_final" /
         "train_augmented_final.csv")

# Parafrase bersih — sudah ter-tokenisasi (spasi = pemisah token; tanda baca = token sendiri).
# Mention entitas ditulis PERSIS seperti di base, urutan & jumlah sama.
PARAS: dict[str, str] = {
    "000151-002":
        "Akibat tindakan dan kesewenang-wenangan mereka , Rasulullah pun mengumpulkan mereka , "
        "lalu menasihati dan mengajak mereka kepada petunjuk , serta memperingatkan agar mereka "
        "tidak menebar permusuhan maupun berbuat sesuka hati . Namun peringatan dan nasihat itu "
        "mereka abaikan begitu saja . Abu Dawud dan periwayat lainnya menuturkan dari Ibnu Abbas "
        "bahwa dia berkata , setelah Rasulullah meraih kemenangan atas Quraisy dalam Perang Badr "
        "dan kembali ke Madinah , beliau mengumpulkan mereka di pasar Bani Qainuqa' . Beliau "
        "bersabda , wahai kaum Yahudi , masuklah Islam sebelum kalian mengalami apa yang menimpa "
        "Quraisy . Mereka menjawab , hai Muhammad , janganlah engkau tertipu oleh dirimu sendiri "
        "hanya karena berhasil mengalahkan sebagian orang Quraisy yang tidak pandai berperang ; "
        "seandainya engkau memerangi kami , barulah engkau tahu siapa lawan yang sesungguhnya .",
    "000215-003":
        "Padahal penetapan syariat shalat khauf untuk pertama kalinya justru terjadi pada saat "
        "Perang Asafan . Padahal tidak ada perbedaan pendapat bahwa Perang Asafan berlangsung "
        "setelah Perang Khandaq , yang terjadi pada akhir tahun itu .",
    "000216-002":
        "Karena rasa takut telah menyelimuti hati para prajuritnya , mereka pun kembali ke Makkah "
        "tanpa sempat bertempur , dan tak seorang pun membantah pendapatnya . Kaum Muslimin "
        "menanti kedatangan pasukan Quraisy di Badr selama delapan hari . Selama itu mereka "
        "berdagang dan memperoleh keuntungan yang cukup , lalu kembali ke Madinah dengan nama "
        "harum dan wibawa yang disegani . Peristiwa ini kemudian dikenal sebagai Perang Badr yang "
        "dijanjikan , Perang Badr yang kedua , Perang Badr yang terakhir , atau Perang Badr Shughra .",
    "000358-003":
        "Pada malam hari beliau bangun beribadah kepada Allah , membaca Al-Qur'an dan tunduk "
        "sebagaimana diperintahkan . Demikianlah Rasulullah menjalani hidupnya di tengah "
        "peperangan yang seakan tak berujung selama lebih dari dua puluh tahun , tanpa pernah "
        "melalaikan satu urusan karena sibuk mengurus urusan lain , hingga dakwah Islam akhirnya "
        "berhasil gemilang dan menjangkau wilayah yang amat luas . Seluruh Jazirah Arab tunduk "
        "kepada dakwah Islam , debu jahiliyah tak lagi tampak , akal yang menyimpang menjadi lurus , "
        "dan berhala pun ditinggalkan bahkan dihancurkan . Udara Arab dipenuhi suara tauhid , adzan "
        "berkumandang memecah angkasa , dan berbagai kabilah yang tadinya berpencar kini bersatu "
        "dalam penghambaan kepada Allah .",
    "000358-005":
        "Sekalipun di sana terdapat agama samawi , agama itu telah kehilangan kekuatannya , tak "
        "lagi memiliki kuasa , dan telah tercemar oleh penyimpangan serta pengubahan , sehingga "
        "yang tersisa hanyalah upacara kaku tanpa ruh kehidupan . Setelah dakwah Islam hadir "
        "memainkan perannya , ruh manusia dapat terlepas dari ilusi dan khurafat , dari perhambaan "
        "dan perbudakan , dari kerusakan , noda , dan penyimpangan . Manusia pun bebas dari "
        "kezhaliman , perpecahan , perbedaan kelas , kesewenangan penguasa , dan tipu daya para "
        "dukun . Dakwah ini membangun dunia di atas kehormatan , kebersihan , kebebasan , "
        "pengetahuan , keyakinan , keimanan , dan keadilan bagi semua orang . Melalui tahap-tahap "
        "perkembangan itu , Jazirah Arab menyaksikan kebangkitan penuh barakah yang belum pernah "
        "terjadi sepanjang sejarah manusia .",
    "000366-001":
        "Pada hari Sabtu atau Ahad , Nabi merasa badannya agak ringan . Dengan dipapah dua orang "
        "lelaki , beliau keluar rumah untuk menunaikan shalat zhuhur , sementara saat itu Abu Bakar "
        "tengah mengimami orang-orang . Melihat beliau datang , Abu Bakar bergeser mundur ke "
        "belakang , tetapi beliau memberi isyarat kepada Abu Bakar agar tidak usah mundur . Beliau "
        "bersabda , dudukkanlah aku di samping Abu Bakar . Maka keduanya mendudukkan beliau di sisi "
        "Abu Bakar , lalu Abu Bakar shalat mengikuti shalat beliau seraya mengeraskan takbir agar "
        "terdengar oleh orang-orang .",
}


def base_entities(train: pd.DataFrame, base_id: str) -> list[tuple[str, list[str]]]:
    """Daftar (tipe, [token surface]) entitas base, urut kemunculan."""
    s = train[train["text_id"] == base_id].reset_index(drop=True)
    toks = s["token"].astype(str).tolist()
    labs = s["label"].astype(str).tolist()
    out = []
    for t, a, e in get_entities(labs):
        out.append((t, toks[a:e + 1]))
    return out


def align_labels(para_tokens: list[str], ents: list[tuple[str, list[str]]]) -> list[str]:
    """Beri label BIO ke token parafrase dengan mencocokkan entitas base berurutan."""
    labels = ["O"] * len(para_tokens)
    pos = 0
    for etype, etoks in ents:
        L = len(etoks)
        found = -1
        j = pos
        while j <= len(para_tokens) - L:
            if para_tokens[j:j + L] == etoks:
                found = j
                break
            j += 1
        assert found >= 0, (f"Entitas {etype} {etoks} TIDAK ditemukan di parafrase "
                            f"(mulai pos {pos}). Perbaiki teks parafrase.")
        labels[found] = f"B-{etype}"
        for k in range(1, L):
            labels[found + k] = f"I-{etype}"
        pos = found + L
    return labels


def main() -> None:
    train = pd.read_csv(TRAIN)
    train["token"] = train["token"].astype(str)
    fin = pd.read_csv(FINAL)
    fin["text_id"] = fin["text_id"].astype(str)

    new_rows = []
    for base_id, para in PARAS.items():
        ents = base_entities(train, base_id)
        toks = para.split()
        labs = align_labels(toks, ents)
        pid = f"{base_id}_para1"
        for i, (tok, lab) in enumerate(zip(toks, labs), start=1):
            new_rows.append({"text_id": pid, "id": f"{pid}.{i:03d}",
                             "token": tok, "pos_tag": "NN", "label": lab})
        n_ent = sum(1 for l in labs if l.startswith("B-"))
        print(f"{pid}: {len(toks)} token, {n_ent} entitas (base {len(ents)}) "
              f"{'OK' if n_ent == len(ents) else 'MISMATCH!'}")

    # backup
    bak = FINAL.with_suffix(".csv.bak_pre_paraphrase_clean")
    if not bak.exists():
        shutil.copy2(FINAL, bak)
        print(f"[backup] -> {bak.name}")

    para_ids = {f"{b}_para1" for b in PARAS}
    kept = fin[~fin["text_id"].isin(para_ids)].copy()
    out = pd.concat([kept, pd.DataFrame(new_rows)], ignore_index=True)
    out.to_csv(FINAL, index=False)
    print(f"[OK] tulis {FINAL.name}: {len(fin)} -> {len(out)} baris "
          f"(hapus {len(fin)-len(kept)} para lama, tambah {len(new_rows)} para bersih)")

    # distribusi entitas sesudah
    def counts(df):
        lab = df["label"].astype(str)
        return {t: int(lab.str.contains(t).sum()) for t in ["PERSON", "LOCATION", "EVENT", "TIME"]}
    print("[distribusi entitas train_augmented_final SESUDAH regen]", counts(out))


if __name__ == "__main__":
    main()
