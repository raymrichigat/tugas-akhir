"""
bab4_visualizations.py
======================
Gambar pendukung Bab 4. SEMUA diagram batang (bar chart), skala linear.
F1 agregat dan F1 per-entitas DIPISAH menjadi gambar tersendiri (per uji coba).
Angka diambil PERSIS dari tabel Bab 4 (hasil_pembahasan.md).

Output PNG -> data/result/analysis/bab4_viz/
  eda_imbalance.png          batang berkelompok (EDA: entitas per kelas)
  augmentasi_distribusi.png  batang 2 panel: O | entitas (Tabel 4.8)
  f1_uc1_agregat.png   + f1_uc1_perkelas.png   (Tabel 4.1 / 4.2)
  f1_uc2_agregat.png   + f1_uc2_perkelas.png   (Tabel 4.9 / 4.10)
  f1_uc3_agregat.png   + f1_uc3_perkelas.png   (Tabel 4.14 / 4.15)

Catatan: legend per-kelas diletakkan DI LUAR area plot (kanan) supaya
keterangan PERSON/LOCATION/EVENT/TIME selalu jelas, termasuk pada UC3 yang
hanya punya 2 skenario.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(r"E:\2_Kehidupan-Kuliah\10_tugas-akhir\repo-TA\TA_preprocess\TA_sirah")
SRL  = BASE / "data/result/pseudo-labelling/SRL-NER"
OUT  = BASE / "data/result/analysis/bab4_viz"
OUT.mkdir(parents=True, exist_ok=True)

# bersihkan file F1 gabungan versi lama agar tidak membingungkan
for old in ["f1_uji_coba_1.png", "f1_uji_coba_2.png", "f1_uji_coba_3.png"]:
    (OUT / old).unlink(missing_ok=True)

plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "figure.dpi": 150, "savefig.bbox": "tight",
})

KELAS = ["PERSON", "LOCATION", "EVENT", "TIME"]
WARNA = {"PERSON": "#3b6ea5", "LOCATION": "#4c9f70",
         "EVENT": "#c0504d", "TIME": "#e0a458"}


def fnum(v):
    return f"{int(v):,}".replace(",", ".")


# ─────────────────────────────────────────────────────────────────────────────
# 1. EDA IMBALANCE — batang berkelompok (train vs test), linear
# ─────────────────────────────────────────────────────────────────────────────
def count_entities(csv_path):
    lab = pd.read_csv(csv_path)["label"].astype(str)
    return {k: int((lab == f"B-{k}").sum()) for k in KELAS}

train_c = count_entities(SRL / "train.csv")
# Data uji: pakai jumlah entitas pada gold TERKOREKSI (Bu Dini 2026-07-10), bukan
# test.csv mentah, agar konsisten dengan support Tabel 4.1/4.2 (EVENT 75, rasio 17,4:1).
# Hitungan B- pada gold terkoreksi (recompute_gt_corrected.build_corrected_gold):
test_c  = {"PERSON": 1302, "LOCATION": 474, "EVENT": 75, "TIME": 113}
print("train:", train_c, "| test (gold terkoreksi):", test_c)

fig, ax = plt.subplots(figsize=(7.6, 4.4))
x = np.arange(len(KELAS)); w = 0.38
b1 = ax.bar(x - w/2, [train_c[k] for k in KELAS], w, label="Data latih (train)", color="#3b6ea5")
b2 = ax.bar(x + w/2, [test_c[k]  for k in KELAS], w, label="Data uji (test)",  color="#9fb8d4")
ax.set_ylabel("Jumlah entitas")
ax.set_xticks(x); ax.set_xticklabels(KELAS)
ax.set_title("Distribusi Jumlah Entitas per Kelas: Ketimpangan Kelas (Imbalance)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+30, fnum(b.get_height()),
                ha="center", va="bottom", fontsize=8)
r_tr = train_c["PERSON"]/min(train_c.values())
r_te = test_c["PERSON"]/min(test_c.values())
ax.legend(frameon=False, title=f"rasio imbalance ≈ {r_tr:.0f}:1 (train), {r_te:.0f}:1 (test)")
ax.margins(y=0.15)
fig.savefig(OUT / "eda_imbalance.png"); plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 2. DISTRIBUSI AUGMENTASI — 2 panel batang linear: (a) O, (b) entitas
# ─────────────────────────────────────────────────────────────────────────────
# Angka done_newest (gold terkoreksi): train.csv vs train_augmented_final.csv
# (mention replacement + parafrase). Token-level (B+I) per kelas; O = bukan entitas.
ent = ["Person", "Location", "Time", "Event"]
before_O, after_O = 108815, 163352
before_e = [5519, 1038, 664, 317]
after_e  = [8311, 1875, 1107, 943]

fig, (axO, axE) = plt.subplots(1, 2, figsize=(11, 4.4),
                               gridspec_kw={"width_ratios": [0.7, 1.7]})
bo = axO.bar(["Sebelum", "Sesudah"], [before_O, after_O],
             color=["#9aa0a6", "#c0504d"], width=0.6)
axO.set_title("(a) Kelas O (bukan entitas)"); axO.set_ylabel("Jumlah token")
for b in bo:
    axO.text(b.get_x()+b.get_width()/2, b.get_height()+1500, fnum(b.get_height()),
             ha="center", va="bottom", fontsize=9)
axO.margins(y=0.15)
xe = np.arange(len(ent)); w = 0.38
be1 = axE.bar(xe - w/2, before_e, w, label="Sebelum", color="#9aa0a6")
be2 = axE.bar(xe + w/2, after_e,  w, label="Sesudah", color="#4c9f70")
axE.set_xticks(xe); axE.set_xticklabels(ent)
axE.set_ylabel("Jumlah token (B+I)")
axE.set_title("(b) Kelas entitas: Event naik paling tajam (+198%)")
axE.legend(frameon=False)
for bars in (be1, be2):
    for b in bars:
        axE.text(b.get_x()+b.get_width()/2, b.get_height()+30, fnum(b.get_height()),
                 ha="center", va="bottom", fontsize=8)
axE.margins(y=0.12)
fig.suptitle("Distribusi Label Token Data Latih Sebelum dan Sesudah Augmentasi",
             fontweight="bold")
fig.savefig(OUT / "augmentasi_distribusi.png"); plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# F1 — fungsi terpisah: (a) agregat  dan  (b) per kelas
# ─────────────────────────────────────────────────────────────────────────────
def plot_agregat(fname, judul, labels, micro, macro, highlight=None, rot=0, figw=7.2):
    fig, ax = plt.subplots(figsize=(figw, 4.4))
    x = np.arange(len(labels)); w = 0.36
    # Warna KONSISTEN dengan legenda: F1 mikro selalu biru, F1 macro selalu biru muda
    # (revisi Pak Aldi #8). Pemenang ditandai dengan MEN-BOLD nama model/langkahnya
    # pada sumbu-x -- bukan lewat warna berbeda maupun hatch.
    bM = ax.bar(x - w/2, micro, w, label="F1 mikro", color="#3b6ea5")
    bR = ax.bar(x + w/2, macro, w, label="F1 macro", color="#9fb8d4")
    ax.set_ylim(min(min(micro), min(macro))*0.90, 1.0)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot)
    if highlight is not None:
        ax.get_xticklabels()[highlight].set_fontweight("bold")
    ax.set_ylabel("F1-score"); ax.set_title(judul)
    ax.legend(frameon=False, fontsize=9)
    for bars in (bM, bR):
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.003,
                    f"{b.get_height():.3f}".replace(".", ","),
                    ha="center", va="bottom", fontsize=7.5)
    fig.savefig(OUT / fname); plt.close(fig)


def plot_perkelas(fname, judul, labels, perkelas, rot=0, figw=8.4, annot=False):
    fig, ax = plt.subplots(figsize=(figw, 4.6))
    x = np.arange(len(labels)); wk = 0.19
    for i, k in enumerate(KELAS):
        bars = ax.bar(x + (i-1.5)*wk, perkelas[k], wk, label=k, color=WARNA[k])
        if annot:
            for b in bars:
                ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.006,
                        f"{b.get_height():.3f}".replace(".", ","),
                        ha="center", va="bottom", fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot)
    ax.set_ylabel("F1-score"); ax.set_title(judul)
    ax.grid(axis="y", ls=":", alpha=0.4)
    # legend DI LUAR plot (kanan) -> keterangan kelas selalu jelas
    ax.legend(title="Kelas entitas", frameon=False, fontsize=9,
              loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.savefig(OUT / fname); plt.close(fig)


# ── Uji Coba 1 (5 skenario) ──────────────────────────────────────────────────
# Angka = ground-truth uji TERKOREKSI (Bu Dini 2026-07-10),
# sumber: data/result/analysis/gt_corrected_2026_07_10/recompute_gt_corrected_results.md
# (identik Tabel 4.1/4.2 di docs/bab4/hasil_pembahasan.md).
sk1 = ["Baseline", "Weighted-CE", "SCL", "JSCL", "Augmentation"]
plot_agregat("f1_uc1_agregat.png",
             "F1-score Agregat Lima Skenario Penanganan Imbalance (Uji Coba 1)",
             sk1, [0.9536, 0.9480, 0.9546, 0.9451, 0.9756],
             [0.9136, 0.9156, 0.9236, 0.9062, 0.9543], highlight=4, rot=12)
plot_perkelas("f1_uc1_perkelas.png",
              "F1-score per Kelas Lima Skenario Penanganan Imbalance (Uji Coba 1)",
              sk1,
              {"PERSON":  [0.9690, 0.9616, 0.9687, 0.9611, 0.9835],
               "LOCATION":[0.9530, 0.9432, 0.9488, 0.9467, 0.9755],
               "EVENT":   [0.9342, 0.9231, 0.9600, 0.9600, 0.9542],
               "TIME":    [0.7983, 0.8347, 0.8170, 0.7572, 0.9038]}, rot=12)

# ── Uji Coba 2 (5 model) ──────────────────────────────────────────────────────
# Angka = ground-truth uji TERKOREKSI (Tabel 4.9/4.10).
md2 = ["IndoBERT\nuncased", "cahya\nuncased", "DistilBERT", "IndoBERT\nphase-1", "RoBERTa"]
plot_agregat("f1_uc2_agregat.png",
             "F1-score Agregat Lima Model Pra-latih (Uji Coba 2)",
             md2, [0.9536, 0.9286, 0.9353, 0.7774, 0.8069],
             [0.9136, 0.8811, 0.8852, 0.6893, 0.7490], highlight=0, figw=7.8)
plot_perkelas("f1_uc2_perkelas.png",
              "F1-score per Kelas Lima Model Pra-latih (Uji Coba 2)",
              md2,
              {"PERSON":  [0.9690, 0.9493, 0.9581, 0.7843, 0.8135],
               "LOCATION":[0.9530, 0.9232, 0.9232, 0.8717, 0.8766],
               "EVENT":   [0.9342, 0.9315, 0.9116, 0.5549, 0.7654],
               "TIME":    [0.7983, 0.7203, 0.7479, 0.5461, 0.5404]}, figw=9.0)

# ── Uji Coba 3 (baseline vs POS-tag) ─────────────────────────────────────────
# Angka = ground-truth uji TERKOREKSI (Tabel 4.14/4.15). POS-tag kini sedikit di
# atas baseline pada micro (0,9547 vs 0,9536), praktis setara.
sk3 = ["Baseline", "POS-tag"]
plot_agregat("f1_uc3_agregat.png",
             "F1-score Agregat Baseline vs Modul POS-tag (Uji Coba 3)",
             sk3, [0.9536, 0.9547], [0.9136, 0.9217], highlight=None, figw=5.4)
plot_perkelas("f1_uc3_perkelas.png",
              "F1-score per Kelas Baseline vs Modul POS-tag (Uji Coba 3)",
              sk3,
              {"PERSON":  [0.9690, 0.9693],
               "LOCATION":[0.9530, 0.9466],
               "EVENT":   [0.9342, 0.9333],
               "TIME":    [0.7983, 0.8376]}, figw=6.6, annot=True)

print("Selesai. Gambar di:", OUT)
for p in sorted(OUT.glob("*.png")):
    print("  -", p.name)
