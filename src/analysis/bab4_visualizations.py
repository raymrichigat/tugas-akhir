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
test_c  = count_entities(SRL / "test.csv")
print("train:", train_c, "| test:", test_c)

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
ent = ["Person", "Location", "Time", "Event"]
before_O, after_O = 95277, 139983
before_e = [5559, 1057, 666, 325]
after_e  = [8101, 1885, 1084, 967]

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
    cM = ["#3b6ea5"]*len(labels); cR = ["#9fb8d4"]*len(labels)
    if highlight is not None:
        cM[highlight] = "#c0504d"; cR[highlight] = "#e2877f"
    bM = ax.bar(x - w/2, micro, w, label="F1 mikro", color=cM)
    bR = ax.bar(x + w/2, macro, w, label="F1 macro", color=cR)
    ax.set_ylim(min(min(micro), min(macro))*0.90, 1.0)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=rot)
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
sk1 = ["Baseline", "Weighted-CE", "SCL", "JSCL", "Augmentation"]
plot_agregat("f1_uc1_agregat.png",
             "F1-score Agregat Lima Skenario Penanganan Imbalance (Uji Coba 1)",
             sk1, [0.9481, 0.9393, 0.9512, 0.9434, 0.9581],
             [0.8892, 0.8648, 0.8902, 0.8932, 0.9235], highlight=4, rot=12)
plot_perkelas("f1_uc1_perkelas.png",
              "F1-score per Kelas Lima Skenario Penanganan Imbalance (Uji Coba 1)",
              sk1,
              {"PERSON":  [0.9596, 0.9575, 0.9655, 0.9559, 0.9640],
               "LOCATION":[0.9527, 0.9352, 0.9493, 0.9394, 0.9653],
               "EVENT":   [0.8039, 0.7767, 0.8200, 0.8367, 0.9020],
               "TIME":    [0.8408, 0.7898, 0.8258, 0.8408, 0.8627]}, rot=12)

# ── Uji Coba 2 (5 model) ──────────────────────────────────────────────────────
md2 = ["IndoBERT\nuncased", "cahya\nuncased", "DistilBERT", "IndoBERT\ncased", "RoBERTa"]
plot_agregat("f1_uc2_agregat.png",
             "F1-score Agregat Lima Model Pra-latih (Uji Coba 2)",
             md2, [0.9481, 0.9324, 0.9442, 0.7770, 0.8068],
             [0.8892, 0.8744, 0.8748, 0.6867, 0.7165], highlight=0, figw=7.8)
plot_perkelas("f1_uc2_perkelas.png",
              "F1-score per Kelas Lima Model Pra-latih (Uji Coba 2)",
              md2,
              {"PERSON":  [0.9596, 0.9414, 0.9592, 0.7646, 0.8002],
               "LOCATION":[0.9527, 0.9444, 0.9478, 0.9062, 0.9060],
               "EVENT":   [0.8039, 0.8119, 0.8200, 0.6226, 0.6306],
               "TIME":    [0.8408, 0.8000, 0.7722, 0.4532, 0.5291]}, figw=9.0)

# ── Uji Coba 3 (baseline vs POS-tag) ─────────────────────────────────────────
sk3 = ["Baseline", "POS-tag"]
plot_agregat("f1_uc3_agregat.png",
             "F1-score Agregat Baseline vs Modul POS-tag (Uji Coba 3)",
             sk3, [0.9481, 0.9439], [0.8892, 0.8908], highlight=None, figw=5.4)
plot_perkelas("f1_uc3_perkelas.png",
              "F1-score per Kelas Baseline vs Modul POS-tag (Uji Coba 3)",
              sk3,
              {"PERSON":  [0.9596, 0.9579],
               "LOCATION":[0.9527, 0.9385],
               "EVENT":   [0.8039, 0.8485],
               "TIME":    [0.8408, 0.8182]}, figw=6.6, annot=True)

print("Selesai. Gambar di:", OUT)
for p in sorted(OUT.glob("*.png")):
    print("  -", p.name)
