# -*- coding: utf-8 -*-
"""Gambar 3.9 (Bab 3): ilustrasi subgraf hasil contoh berjalan.

Contoh benang merah: kalimat "Tatkala Abu Jahal mengajaknya pergi saat Perang Badr..."
-> node Abu Jahal (:Person) --INVOLVED_IN--> node Perang Badr (:Event).

Output: data/result/analysis/bab3_viz/contoh_subgraf.png
Reproduksi: python src/analysis/contoh_subgraf_bab3.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path("data/result/analysis/bab3_viz")
OUT.mkdir(parents=True, exist_ok=True)

C_PERSON = "#2f6f9f"   # biru
C_EVENT = "#b5651d"    # oranye-cokelat
EDGE = "#444444"

fig, ax = plt.subplots(figsize=(9.2, 3.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis("off")


def node(cx, cy, w, h, color, lines):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.18",
        linewidth=1.6, edgecolor=color, facecolor=color + "22",
    )
    ax.add_patch(box)
    n = len(lines)
    for i, (txt, wt, sz) in enumerate(lines):
        yy = cy + h / 2 - (h / (n + 1)) * (i + 1)
        ax.text(cx, yy, txt, ha="center", va="center",
                fontsize=sz, fontweight=wt, color="#111111")


# Node kiri: Abu Jahal (:Person)
node(2.1, 2.0, 3.0, 1.7, C_PERSON, [
    ("Abu Jahal", "bold", 13),
    (":Person", "normal", 10),
])

# Node kanan: Perang Badr (:Event) + atribut periode
node(7.7, 2.0, 3.6, 1.9, C_EVENT, [
    ("Perang Badr", "bold", 13),
    (":Event", "normal", 10),
    ('periode: "Perang Badr & Dampaknya"', "normal", 8.5),
])

# Sisi berarah INVOLVED_IN
arrow = FancyArrowPatch((3.65, 2.0), (5.85, 2.0),
                        arrowstyle="-|>", mutation_scale=20,
                        linewidth=1.8, color=EDGE)
ax.add_patch(arrow)
ax.text(4.75, 2.35, "INVOLVED_IN", ha="center", va="bottom",
        fontsize=10.5, fontweight="bold", color=EDGE)
ax.text(4.75, 1.68, "(bobot menurut kedekatan)", ha="center", va="top",
        fontsize=8.5, color="#666666")

# Catatan bukti
ax.text(5.0, 0.35,
        "properti evidence: halaman 165-168  (dapat ditelusuri kembali ke teks sumber)",
        ha="center", va="center", fontsize=8.5, style="italic", color="#555555")

fig.tight_layout()
out = OUT / "contoh_subgraf.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
print("saved:", out)
