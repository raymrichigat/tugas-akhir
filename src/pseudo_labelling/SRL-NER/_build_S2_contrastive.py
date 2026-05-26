"""
_build_S2_contrastive.py
========================
Build skenario **S2 baru (Contrastive Learning + Baseline)** dari baseline notebook
`srl_ner_sirah_0.9_*.ipynb`. Menggantikan rencana lama (`_build_S1.py` class weight
dan `_build_S2.py` adaptive yang sekarang di-arsipkan sebagai legacy).

S2 = Baseline (fix THRESHOLD=0.9, no class weight) + supervised contrastive loss.

Dua sub-skenario yang di-generate:
  - **S2a (SCL)**  — Strict Supervised Contrastive Learning (Eq. 2-3 paper Dewabharata
                     et al., `Contrastive_Learning.pdf`). Positive pair = token dengan
                     label BIO identik dalam batch.
  - **S2b (JSCL)** — Jaccard Similarity Contrastive Learning (Eq. 4-6 paper Dewabharata
                     et al.). Adaptasi sentence-level Jaccard: tiap kalimat punya bag-of-
                     labels BIO (exclude `O`), Jaccard antar kalimat dalam batch,
                     embedding kalimat = mean-pool token embeddings.

Pipeline self-training tetap sama dengan baseline (fix threshold 0.9, 6 iter).
Yang berubah HANYA loss function di Trainer:
    L_total = (1 - λ) · L_CE + λ · L_contrastive

Idempotent. Usage:
  python _build_S2_contrastive.py

Output (6 notebook total):
  srl_ner_sirah_S2a_scl.ipynb           (lokal)
  srl_ner_sirah_S2a_scl_colab.ipynb     (Colab/Drive)
  srl_ner_sirah_S2a_scl_kaggle.ipynb    (Kaggle)
  srl_ner_sirah_S2b_jscl.ipynb          (lokal)
  srl_ner_sirah_S2b_jscl_colab.ipynb    (Colab/Drive)
  srl_ner_sirah_S2b_jscl_kaggle.ipynb   (Kaggle)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

BASE_NOTEBOOKS = [
    "srl_ner_sirah_0.9.ipynb",
    "srl_ner_sirah_0.9_colab.ipynb",
    "srl_ner_sirah_0.9_kaggle.ipynb",
]

# Mapping: (mode, suffix) → output filename pattern. suffix == "S2a_scl" or "S2b_jscl"
SCENARIOS = [
    ("scl",  "S2a_scl",  "S2a (SCL — Strict Supervised Contrastive Learning)"),
    ("jscl", "S2b_jscl", "S2b (JSCL — Jaccard Similarity Contrastive Learning, sentence-level)"),
]


# ════════════════════════════════════════════════════════════════════════════
# CELL TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Contrastive loss helpers (SCL + JSCL — keduanya di-define agar
#       notebook portable kalau mau switch mode tanpa rebuild)
CONTRASTIVE_HELPERS_CELL = """# === [S2] Contrastive Loss Helpers (SCL + JSCL sentence-level) ===
# Mengikuti paper Dewabharata, Santoso, Afiat, Ma'ruf, Gosumolo —
# "Augmentation-Free Semi-Supervised Contrastive Learning for Multi-Label
#  Classification of Indonesian Regulatory Texts" (Contrastive_Learning.pdf, root repo).
#
# SCL  : Eq. 2-3 paper — InfoNCE pada token-pair sekelas BIO.
# JSCL : Eq. 4-6 paper — weighted InfoNCE pada embedding kalimat,
#        weight = Jaccard(bag-of-BIO-labels kalimat-i, kalimat-j).

import torch
import torch.nn.functional as F


def scl_loss_tokens(hidden, labels, tau=0.1):
    \"\"\"
    Token-level Supervised Contrastive Loss (SCL).

    Parameters
    ----------
    hidden : Tensor [B, T, H]
        Last hidden states dari encoder.
    labels : Tensor [B, T]
        BIO label id, -100 = ignore (special tokens / sub-word).
    tau : float
        Temperature InfoNCE.

    Returns
    -------
    Tensor (scalar) — SCL loss.
    \"\"\"
    h = hidden.reshape(-1, hidden.size(-1))         # [N, H]
    y = labels.reshape(-1)                           # [N]
    mask_valid = y != -100
    h, y = h[mask_valid], y[mask_valid]
    if h.size(0) < 2:
        return torch.tensor(0.0, device=hidden.device, requires_grad=True)

    h = F.normalize(h, dim=-1)
    sim = h @ h.T / tau                              # [N, N]

    # Stability: subtract row max
    sim = sim - sim.max(dim=-1, keepdim=True).values.detach()

    # Mask self di denominator (logsumexp)
    diag_mask = torch.eye(sim.size(0), dtype=torch.bool, device=h.device)
    sim_denom = sim.masked_fill(diag_mask, float('-inf'))
    log_prob = sim - torch.logsumexp(sim_denom, dim=-1, keepdim=True)

    pos_mask = (y.unsqueeze(0) == y.unsqueeze(1)).float()
    pos_mask.fill_diagonal_(0)
    n_pos = pos_mask.sum(dim=-1).clamp(min=1)
    loss = -(pos_mask * log_prob).sum(dim=-1) / n_pos
    return loss.mean()


def jscl_loss_sentence(hidden, labels, tau=0.1, exclude_O=True, O_label_id=None):
    \"\"\"
    Sentence-level Jaccard Similarity Contrastive Loss (JSCL).

    Adaptasi paper untuk NER token-level:
      - Anchor = kalimat (mean-pool valid token embeddings).
      - L_i = bag-of-labels BIO unik di kalimat ke-i (opsional exclude 'O').
      - J_ij = |L_i ∩ L_j| / |L_i ∪ L_j| antar kalimat dalam batch.
      - Weighted InfoNCE pada embedding kalimat (Eq. 4-6 paper).

    Parameters
    ----------
    hidden : Tensor [B, T, H]
    labels : Tensor [B, T] BIO label id, -100 = ignore
    tau : float — temperature
    exclude_O : bool — skip label 'O' di bag-of-labels (rekomendasi True)
    O_label_id : int | None — id integer label 'O' di label2id
    \"\"\"
    B, T, H = hidden.shape
    if B < 2:
        return torch.tensor(0.0, device=hidden.device, requires_grad=True)

    mask_valid = (labels != -100).float().unsqueeze(-1)          # [B, T, 1]
    sent_h = (hidden * mask_valid).sum(dim=1) / mask_valid.sum(dim=1).clamp(min=1)
    sent_h = F.normalize(sent_h, dim=-1)                          # [B, H]

    # Build multi-hot bag-of-labels per kalimat
    valid_labels = labels[labels != -100]
    if valid_labels.numel() == 0:
        return torch.tensor(0.0, device=hidden.device, requires_grad=True)
    num_labels = int(valid_labels.max().item()) + 1
    L = torch.zeros(B, num_labels, device=hidden.device)
    for b in range(B):
        valid = labels[b][labels[b] != -100]
        if exclude_O and (O_label_id is not None):
            valid = valid[valid != O_label_id]
        if valid.numel() > 0:
            uniq = valid.unique()
            L[b].scatter_(0, uniq, 1.0)

    # Jaccard antar kalimat
    inter = L @ L.T                                                # [B, B]
    union = L.sum(dim=-1, keepdim=True) + L.sum(dim=-1).unsqueeze(0) - inter
    J = inter / (union + 1e-8)                                     # [B, B]

    # Weighting α_ij = J_ij / (Σ_k≠i J_ik + ε)
    diag_mask = torch.eye(B, dtype=torch.bool, device=hidden.device)
    mask_off_diag = (1 - diag_mask.float())
    J_off = J * mask_off_diag
    alpha = J_off / (J_off.sum(dim=-1, keepdim=True) + 1e-8)

    # Weighted InfoNCE
    sim = sent_h @ sent_h.T / tau                                  # [B, B]
    sim = sim - sim.max(dim=-1, keepdim=True).values.detach()
    sim_denom = sim.masked_fill(diag_mask, float('-inf'))
    log_prob = sim - torch.logsumexp(sim_denom, dim=-1, keepdim=True)

    loss = -(alpha * log_prob * mask_off_diag).sum() / B
    return loss
"""


# ── 2. ContrastiveTrainer (Trainer subclass)
CONTRASTIVE_TRAINER_CODE = """
# === [S2] ContrastiveTrainer — L_total = (1-λ)·L_CE + λ·L_contrastive ===
class ContrastiveTrainer(Trainer):
    \"\"\"
    Custom Trainer yang menambah supervised contrastive loss ke CrossEntropy.

    Knob:
      - lambda_c        : float (0..1) — bobot loss contrastive
      - tau             : float — temperature
      - contrastive_mode: 'scl' atau 'jscl'
      - o_label_id      : int | None — id label 'O' (untuk JSCL exclude_O)
    \"\"\"
    def __init__(self, *args,
                 lambda_c: float = 0.3,
                 tau: float = 0.1,
                 contrastive_mode: str = 'scl',
                 o_label_id=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.lambda_c = lambda_c
        self.tau = tau
        self.contrastive_mode = contrastive_mode
        self.o_label_id = o_label_id

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop('labels')
        outputs = model(**inputs, output_hidden_states=True)
        logits = outputs.logits
        hidden = outputs.hidden_states[-1]

        # Cross-entropy (sama dengan baseline Trainer)
        loss_ce = torch.nn.CrossEntropyLoss(ignore_index=-100)(
            logits.view(-1, model.config.num_labels), labels.view(-1)
        )

        # Contrastive component
        if self.contrastive_mode == 'scl':
            loss_c = scl_loss_tokens(hidden, labels, tau=self.tau)
        elif self.contrastive_mode == 'jscl':
            loss_c = jscl_loss_sentence(
                hidden, labels, tau=self.tau,
                exclude_O=True, O_label_id=self.o_label_id,
            )
        else:
            raise ValueError(f'Unknown contrastive_mode: {self.contrastive_mode!r}')

        loss = (1.0 - self.lambda_c) * loss_ce + self.lambda_c * loss_c
        # IMPORTANT: kalau return_outputs=True, hanya return dict {"logits": logits},
        # bukan ModelOutput penuh. Alasan: outputs ModelOutput membawa hidden_states
        # (karena output_hidden_states=True), dan Trainer downstream akan extract
        # `pred.predictions` jadi tuple (logits, hidden_states_tuple) saat evaluate.
        # Numpy 2.x kemudian raise `inhomogeneous shape` error di
        # `np.argmax(pred.predictions, axis=2)` di compute_metrics.
        # Lihat success run S2a SCL `done_running/.../srl_ner_sirah_S2a_scl_colab_new.ipynb`
        # untuk reference behavior yang work.
        if return_outputs:
            return loss, {"logits": logits}
        return loss


"""


# ── 3. Knob cell template (different default per mode)
def make_knob_cell(mode: str, suffix: str) -> str:
    return f"""# === [S2] Knob Contrastive Learning ===
# Mode: '{mode}' ({'SCL — token-level' if mode == 'scl' else 'JSCL — sentence-level Jaccard'})
CONTRASTIVE_MODE = '{mode}'
LAMBDA_C = 0.3      # bobot loss contrastive: L_total = (1-λ)·L_CE + λ·L_contrastive
TAU      = 0.1      # temperature InfoNCE
O_LABEL_ID = label2id.get('O', None)   # untuk JSCL exclude_O (skip kalau mode='scl')

print(f"[S2/{suffix}] mode={{CONTRASTIVE_MODE}} lambda={{LAMBDA_C}} tau={{TAU}} O_id={{O_LABEL_ID}}")
"""


# ════════════════════════════════════════════════════════════════════════════
# HELPERS (same pattern as _build_S2.py)
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


def build_one(base_path: Path, out_path: Path, mode: str, suffix: str, title_subtitle: str):
    nb = json.loads(base_path.read_text(encoding="utf-8"))

    # Step 1: strip outputs
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None

    # Step 2: rename experiment_name → suffix + path isolation
    suffix_token = suffix.replace("_", "-")   # "S2a-scl" / "S2b-jscl"
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = src_str(c)
        modified = False
        if "experiment_name = f'{_name}-{_type}'" in src:
            src = src.replace(
                "experiment_name = f'{_name}-{_type}'",
                f"experiment_name = f'{{_name}}-{{_type}}-{suffix_token}'",
            )
            modified = True
        replacements = [
            ('"bert-only-sirah-ner-confidence-0.9-misclassified.xlsx"',
             'f"{experiment_name}-confidence-0.9-misclassified.xlsx"'),
            ('"bert-only-sirah-ner-iterative-6"',
             'f"{experiment_name}-iterative-6"'),
        ]
        for old, new in replacements:
            if old in src:
                src = src.replace(old, new)
                modified = True
        if modified:
            set_src(c, src)

    # Step 3: insert contrastive helpers + knob cells SETELAH label2id cell
    label_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code" and "label_list = sorted(df_train" in src_str(c),
    )
    if label_idx == -1:
        raise RuntimeError(f"Cannot find label_list cell in {base_path.name}")

    helpers_cell = make_code_cell(CONTRASTIVE_HELPERS_CELL)
    knob_cell = make_code_cell(make_knob_cell(mode, suffix_token))

    # Idempotent: kalau cell helpers sudah ada (rebuild), replace
    nxt = nb["cells"][label_idx + 1] if label_idx + 1 < len(nb["cells"]) else None
    if nxt and nxt["cell_type"] == "code" and "[S2] Contrastive Loss Helpers" in src_str(nxt):
        nb["cells"][label_idx + 1] = helpers_cell
        nxt2 = nb["cells"][label_idx + 2] if label_idx + 2 < len(nb["cells"]) else None
        if nxt2 and nxt2["cell_type"] == "code" and "[S2] Knob Contrastive" in src_str(nxt2):
            nb["cells"][label_idx + 2] = knob_cell
        else:
            nb["cells"].insert(label_idx + 2, knob_cell)
    else:
        nb["cells"].insert(label_idx + 1, helpers_cell)
        nb["cells"].insert(label_idx + 2, knob_cell)

    # Step 4: modify train_model cell — inject ContrastiveTrainer + ganti Trainer call
    train_idx = find_cell_index(
        nb,
        lambda c: c["cell_type"] == "code"
        and "def train_model" in src_str(c)
        and "DataCollatorForTokenClassification" in src_str(c),
    )
    if train_idx == -1:
        raise RuntimeError(f"Cannot find train_model cell in {base_path.name}")

    src = src_str(nb["cells"][train_idx])
    if "class ContrastiveTrainer" not in src:
        src = src.replace("def train_model(", CONTRASTIVE_TRAINER_CODE.lstrip() + "def train_model(", 1)
    if "trainer = Trainer(" in src:
        src = src.replace("trainer = Trainer(", "trainer = ContrastiveTrainer(")
    OLD_END = "compute_metrics=compute_metrics,\n    )"
    NEW_END = (
        "compute_metrics=compute_metrics,\n"
        "        lambda_c=LAMBDA_C,\n"
        "        tau=TAU,\n"
        "        contrastive_mode=CONTRASTIVE_MODE,\n"
        "        o_label_id=O_LABEL_ID,\n"
        "    )"
    )
    if OLD_END in src and "lambda_c=LAMBDA_C" not in src:
        src = src.replace(OLD_END, NEW_END, 1)
    set_src(nb["cells"][train_idx], src)

    # Step 5: title cell update
    if nb["cells"] and nb["cells"][0]["cell_type"] == "markdown":
        title_src = src_str(nb["cells"][0])
        if "Contrastive" not in title_src:
            new_title = f"# SRL-NER Sirah — {title_subtitle}\n\n" + title_src
            set_src(nb["cells"][0], new_title)

    # Step 6: metadata tag untuk identifikasi
    nb.setdefault("metadata", {})
    nb["metadata"]["sirah_experiment"] = f"S2_contrastive_{mode}"

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

        for mode, scn_suffix, title in SCENARIOS:
            out_name = f"srl_ner_sirah_{scn_suffix}{tail}.ipynb"
            build_one(base, HERE / out_name, mode=mode, suffix=scn_suffix, title_subtitle=title)


if __name__ == "__main__":
    main()
