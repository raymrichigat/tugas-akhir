"""
_build_S3_1_lambda_sweep.py
============================
Build skenario **S3.1 (λ_C Sweep di S2 SCL)** dari notebook S2a SCL existing.

Konteks: Bimbingan 2026-05-16, Bu Diana approve plan baru — sebelum lompat ke
augmentation (S3.2), tune dulu λ_C di S2 SCL untuk close gap entity-level
(S2 final = 0.950 vs S1 baseline = 0.959). Hipotesis: λ_C=0.3 default terlalu
agresif, λ_C lebih kecil bisa balance antara CE loss (entity boundary) dan
contrastive loss (representasi).

Strategi:
  - Base: `srl_ner_sirah_S2a_scl_*.ipynb` (sudah punya ContrastiveTrainer +
    SCL helpers yang ter-validate dari run S2 sebelumnya).
  - Generate 3 notebook terpisah, satu per nilai λ_C ∈ {0.1, 0.2, 0.3}.
  - Modifikasi minimal: knob cell + experiment_name suffix.
  - Output per-λ_C terisolasi sehingga model & evaluation tidak konflik.

Idempotent. Usage:
  python _build_S3_1_lambda_sweep.py

Output (9 notebook total — 3 λ_C × 3 platform variant):
  srl_ner_sirah_S3_1_scl_lambda01.ipynb           (lokal)
  srl_ner_sirah_S3_1_scl_lambda01_colab.ipynb     (Colab/Drive)
  srl_ner_sirah_S3_1_scl_lambda01_kaggle.ipynb    (Kaggle)
  srl_ner_sirah_S3_1_scl_lambda02.ipynb
  srl_ner_sirah_S3_1_scl_lambda02_colab.ipynb
  srl_ner_sirah_S3_1_scl_lambda02_kaggle.ipynb
  srl_ner_sirah_S3_1_scl_lambda03.ipynb
  srl_ner_sirah_S3_1_scl_lambda03_colab.ipynb
  srl_ner_sirah_S3_1_scl_lambda03_kaggle.ipynb

Catatan tentang λ_C=0.3:
  Run S2a SCL sebelumnya sudah pakai λ_C=0.3 (final Seq F1 entity = 0.950).
  Notebook S3.1-lambda03 di-build untuk konsistensi seed & re-reproducibility,
  tapi user boleh skip run-nya kalau mau hemat GPU (hasil sudah ada di
  done_running/S2_Contrastive_Learning/outputs/).
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# Base notebooks dari S2a SCL (sudah validated)
BASE_NOTEBOOKS = [
    "srl_ner_sirah_S2a_scl.ipynb",
    "srl_ner_sirah_S2a_scl_colab.ipynb",
    "srl_ner_sirah_S2a_scl_kaggle.ipynb",
]

# λ_C sweep values
LAMBDA_VALUES = [
    (0.1, "lambda01"),
    (0.2, "lambda02"),
    (0.3, "lambda03"),
]


# ════════════════════════════════════════════════════════════════════════════
# CELL TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

TIMER_START_CELL = """# === [S3.1] Runtime Timer — START ===
# Catat wall-clock start untuk analisis runtime per skenario (request Bu Diana).
# Mulai diukur dari pre-training sampai akhir evaluation (exclude install &
# data loading karena variability Drive mount).
import time as _time_S31
import datetime as _dt_S31

_t_start_S31 = _time_S31.time()
_iso_start_S31 = _dt_S31.datetime.now().isoformat(timespec='seconds')
print(f"[S3.1 TIMER] start at {_iso_start_S31} (lambda_c={LAMBDA_C})")
"""


TIMER_END_CELL = """# === [S3.1] Runtime Timer — END + write log ===
# Output runtime ke JSON di output_dir untuk komparasi antar lambda_c value.
import json as _json_S31

_t_end_S31 = _time_S31.time()
_total_sec_S31 = _t_end_S31 - _t_start_S31
_iso_end_S31 = _dt_S31.datetime.now().isoformat(timespec='seconds')

_runtime_log = {
    "experiment_name": experiment_name,
    "lambda_c": LAMBDA_C,
    "tau": TAU,
    "contrastive_mode": CONTRASTIVE_MODE,
    "started_at": _iso_start_S31,
    "ended_at": _iso_end_S31,
    "total_seconds": round(_total_sec_S31, 2),
    "total_minutes": round(_total_sec_S31 / 60, 2),
    "total_hours": round(_total_sec_S31 / 3600, 3),
    "iterations": 6,
    "epochs_per_iter": 10,
    "scope": "from pre-training (after data load) to end of evaluation",
}

_runtime_path = os.path.join(eval_dir, f"{experiment_name}-runtime.json")
with open(_runtime_path, "w", encoding="utf-8") as _f:
    _json_S31.dump(_runtime_log, _f, indent=2, ensure_ascii=False)

print(f"[S3.1 TIMER] end at {_iso_end_S31}")
print(f"[S3.1 TIMER] total runtime: {_total_sec_S31:.2f} sec "
      f"= {_total_sec_S31/60:.2f} min "
      f"= {_total_sec_S31/3600:.3f} hours")
print(f"[S3.1 TIMER] log saved to {_runtime_path}")
"""


def make_knob_cell(lambda_c: float, suffix_token: str) -> str:
    """
    Knob cell baru untuk S3.1 — sama dengan S2a SCL tapi LAMBDA_C bisa di-tune.
    """
    return f"""# === [S3.1] Knob Contrastive Learning — λ_C Sweep ===
# Skenario S3.1: tune λ_C di S2 SCL untuk close gap entity-level vs S1 baseline.
# Hipotesis: λ_C=0.3 default terlalu agresif → contrastive over-prioritize per-token
# similarity dengan mengkompromi entity boundary detection. Sweep λ_C ∈ {{0.1, 0.2, 0.3}}.
#
# Variant aktif notebook ini: λ_C = {lambda_c}
CONTRASTIVE_MODE = 'scl'
LAMBDA_C = {lambda_c}    # bobot loss contrastive: L_total = (1-λ)·L_CE + λ·L_contrastive
TAU      = 0.1     # temperature InfoNCE (sama dengan S2)
O_LABEL_ID = label2id.get('O', None)   # tidak dipakai SCL, tapi tetap di-set untuk compat

print(f"[S3.1/{suffix_token}] mode={{CONTRASTIVE_MODE}} lambda={{LAMBDA_C}} tau={{TAU}}")
"""


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def find_cell_index(nb, predicate):
    for i, c in enumerate(nb["cells"]):
        if predicate(c):
            return i
    return -1


def src_str(cell) -> str:
    return "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]


def set_src(cell, text: str):
    cell["source"] = text.splitlines(keepends=True)


def make_code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def build_one(base_path: Path, out_path: Path, lambda_c: float, suffix_token: str,
              title_subtitle: str):
    nb = json.loads(base_path.read_text(encoding="utf-8"))

    # Step 1: strip outputs (idempotent re-build)
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    # Step 2: ganti experiment_name suffix dari S2a-scl → S3-1-scl-{suffix_token}
    # Pattern di S2a: f'{_name}-{_type}-S2a-scl' → ganti jadi S3-1-scl-{suffix_token}
    new_suffix = f"S3-1-scl-{suffix_token}"
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = src_str(c)
        modified = False
        old_suffix = "S2a-scl"
        if old_suffix in src:
            src = src.replace(old_suffix, new_suffix)
            modified = True
        if modified:
            set_src(c, src)

    # Step 3: replace knob cell ([S2] Knob Contrastive Learning) dengan knob S3.1
    knob_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code" and "[S2] Knob Contrastive Learning" in src_str(c),
    )
    if knob_idx == -1:
        raise RuntimeError(f"Cannot find S2 knob cell in {base_path.name}")

    new_knob_src = make_knob_cell(lambda_c, suffix_token)
    set_src(nb["cells"][knob_idx], new_knob_src)

    # Step 4: title cell update
    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        new_title = (
            f"# SRL-NER Sirah — {title_subtitle}\n\n"
            f"Skenario S3.1 — λ_C Sweep di S2 SCL untuk close gap entity-level "
            f"vs S1 baseline.\n\n"
        )
        # Buang heading lama S2a kalau ada
        lines = title_src.split("\n")
        kept = [ln for ln in lines if not ln.strip().startswith("# SRL-NER Sirah")]
        title_src_clean = "\n".join(kept).strip()
        set_src(nb["cells"][0], new_title + title_src_clean + "\n")

    # Step 5: insert TIMER START cell setelah knob ([S3.1] Knob ...) dan TIMER
    # END cell di paling akhir (sebelum trailing empty cells).
    knob_idx_after = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code" and "[S3.1] Knob Contrastive Learning" in src_str(c),
    )
    if knob_idx_after == -1:
        raise RuntimeError(f"Cannot find S3.1 knob cell after replace in {base_path.name}")

    # Idempotent: kalau timer start sudah ada (re-build), replace; kalau belum, insert.
    nxt = nb["cells"][knob_idx_after + 1] if knob_idx_after + 1 < len(nb["cells"]) else None
    if nxt and nxt["cell_type"] == "code" and "[S3.1] Runtime Timer — START" in src_str(nxt):
        nb["cells"][knob_idx_after + 1] = make_code_cell(TIMER_START_CELL)
    else:
        nb["cells"].insert(knob_idx_after + 1, make_code_cell(TIMER_START_CELL))

    # Timer END: hapus existing kalau ada, lalu append setelah cell terakhir non-empty.
    nb["cells"] = [
        c for c in nb["cells"]
        if not (c["cell_type"] == "code" and "[S3.1] Runtime Timer — END" in src_str(c))
    ]
    last_meaningful = -1
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code" and src_str(c).strip():
            last_meaningful = i
    if last_meaningful == -1:
        raise RuntimeError(f"No meaningful code cells in {base_path.name}")
    nb["cells"].insert(last_meaningful + 1, make_code_cell(TIMER_END_CELL))

    # Step 6: metadata tag untuk identifikasi
    nb.setdefault("metadata", {})
    nb["metadata"]["sirah_experiment"] = f"S3_1_lambda_sweep_{suffix_token}"
    nb["metadata"]["sirah_lambda_c"] = lambda_c

    out_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {out_path.name}")


def main():
    for base_name in BASE_NOTEBOOKS:
        base = HERE / base_name
        if not base.exists():
            print(f"SKIP base notebook missing: {base_name}")
            continue

        # Determine variant suffix from base name
        if "_colab" in base_name:
            tail = "_colab"
        elif "_kaggle" in base_name:
            tail = "_kaggle"
        else:
            tail = ""

        for lambda_c, suffix_token in LAMBDA_VALUES:
            title = f"S3.1 (SCL λ_C={lambda_c} — λ_C Sweep)"
            out_name = f"srl_ner_sirah_S3_1_scl_{suffix_token}{tail}.ipynb"
            build_one(
                base, HERE / out_name,
                lambda_c=lambda_c,
                suffix_token=suffix_token,
                title_subtitle=title,
            )


if __name__ == "__main__":
    main()
