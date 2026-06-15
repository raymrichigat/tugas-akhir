# Skenario Baru NER (revisi Bu Diana 2026-06-05) — Lineup Terkunci

> Dibuat 2026-06-09. Semua skenario di bawah dijalankan di **gold dikoreksi** (lihat `../bimbingan/2026-06-11.md` Bagian 3b). Training penuh = **pasca-11-Juni**. Dokumen ini = desain + kode siap-paste untuk membangun notebook tiap skenario.

## Lineup final (terkunci)

**Grup A — Penanganan imbalance** (backbone IndoBERT, self-training THRESHOLD=0.9):
| Kode | Skenario | Yang diuji | Asal |
|---|---|---|---|
| S1 | Baseline | tanpa penanganan imbalance | lama ✓ |
| S2 | **Weighted Cross-Entropy** | bobot kelas pada loss | **baru** |
| S3 | Contrastive Learning (SCL, λ=0.3) | bentuk representasi (≈ pembobotan) | lama ✓ (eks-S2a) |
| S4 | Augmentation (mention replacement v2) | tambah data riil | lama ✓ (eks-S3.2, winner) |

**Grup B — Perbandingan backbone** (pakai config terbaik Grup A):

> **Koreksi 2026-06-15:** baseline aktual = **`indolem/indobert-base-uncased` (UNCASED)** — terverifikasi di notebook S1 (`done_running/S1_baseline/notebook/...`, line tokenizer + model_name). Klaim sebelumnya "baseline = indobenchmark cased" **keliru**. Maka semua backbone di bawah adalah **pembanding tambahan**, bukan baseline. Model **cased** (`indobenchmark/indobert-base-p1`) adalah satu-satunya yang benar-benar mengisolasi efek kapitalisasi (baseline + 2 cahya di bawah semuanya uncased).

| Backbone | Casing | Peran | Notebook | Asal |
|---|---|---|---|---|
| `indolem/indobert-base-uncased` | uncased | **BASELINE (S1)** | `srl_ner_sirah_0.9_colab.ipynb` | base live |
| `indobenchmark/indobert-base-p1` | **cased** | pembanding inti casing | `srl_ner_sirah_GrupB_cased_colab.ipynb` | regen 2026-06-15 |
| `cahya/bert-base-indonesian-1.5G` | uncased | pembanding antar-model uncased | `srl_ner_sirah_GrupB_cahya_colab.ipynb` | manual 2026-06-10 |
| `cahya/distilbert-base-indonesian` | uncased | uncased, lebih kecil/cepat | `srl_ner_sirah_GrupB_distilbert_colab.ipynb` | manual 2026-06-10 |
| `cahya/roberta-base-indonesian-1.5G` | case-preserving (BPE) | pembanding **arsitektur** (BERT vs RoBERTa) | `srl_ner_sirah_GrupB_roberta_colab.ipynb` | regen 2026-06-15 |

> Notebook digenerate oleh `src/pseudo_labelling/SRL-NER/build_grupB_backbone.py` (`cased` / `cahya` / `cahya-distil` / `roberta`) — pure swap `MODEL_NAME` dari **base live `srl_ner_sirah_0.9_colab.ipynb`** (yang sudah ber-patch "auto-detect iterasi terakhir" + runtime timer). Script otomatis: strip `metadata.widgets` (anti-bloat), dan khusus `roberta` menambah `add_prefix_space=True` di sel tokenizer (wajib untuk byte-level BPE + `is_split_into_words=True`). Output Colab diisolasi ke `output_<slug>`. `GrupB_cahya` & `GrupB_distilbert` dibuat manual 2026-06-10 dari base yang sama → tidak perlu regenerate.

**Grup C — Ablation POS-tag**: config terbaik **dengan** vs **tanpa** POS-tag riil.

> Yang **keluar** dari tabel final: S3.1 λ-sweep (tuning, bukan skenario), S2b JSCL (jadi pembanding internal CL). Evaluasi semua: **F1 macro + per-kelas EVENT/TIME** (bukan hanya micro).

---

## S2 — Weighted Cross-Entropy

### ⚠️ Catatan sejarah (jujur)
Class weighting **sudah pernah dicoba** (legacy `done_running/legacy_class_weight_adaptive/`, run 2026-05-07): **precision kolaps** (EVENT F1 stuck ~0.83, S2-lama precision 0.74). Penyebab: bobot terlalu ekstrem. **Maka S2 baru pakai bobot tempered (sqrt), bukan balanced mentah.** Skenario ini justru bertujuan jadi pembanding terkontrol head-to-head dengan CL & Augmentation (persis yang Bu Diana minta).

### Bobot kelas
Sudah dihitung dari train dikoreksi → `data/result/pseudo-labelling/SRL-NER/class_weights.json`.
- `balanced_raw`: ekstrem (I-LOCATION 158×, B-EVENT 77×) — **jangan dipakai langsung**.
- `sqrt_tempered_norm_O1` (**rekomendasi**): O=1, B-PERSON 5.7×, B-EVENT 25×, I-LOCATION 36×.

### Kode (paste ke notebook, ganti `Trainer` biasa)
```python
import json, torch
from transformers import Trainer

# 1. load bobot + susun sesuai urutan id2label MODEL (underscore: B_EVENT, dst.)
cw = json.load(open("class_weights.json", encoding="utf-8"))["sqrt_tempered_norm_O1"]
def dash(u):  # B_EVENT -> B-EVENT
    return u.replace("_", "-", 1) if u[:2] in ("B_", "I_") else u
weights = [cw[dash(model.config.id2label[i])] for i in range(model.config.num_labels)]
class_weights = torch.tensor(weights, dtype=torch.float)

class WeightedLossTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=class_weights.to(outputs.logits.device), ignore_index=-100)
        loss = loss_fct(outputs.logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# 2. pakai WeightedLossTrainer alih-alih Trainer (sisanya identik S1)
```
> Tip: kalau precision turun tajam → kecilkan bobot (mis. pakai akar pangkat 4: `weight**0.5` lagi) atau cap di nilai maks (mis. min(w, 10)).

---

## Grup B — Perbandingan backbone

Cukup ganti `MODEL_NAME` + tokenizer; pipeline lain identik.
```python
# MODEL_NAME = "indolem/indobert-base-uncased"           # BASELINE aktual (uncased)
MODEL_NAME = "indobenchmark/indobert-base-p1"            # pembanding cased (isolasi casing)
# MODEL_NAME = "cahya/bert-base-indonesian-1.5G"         # atau "cahya/distilbert-base-indonesian" (uncased)
```

> ⚠️ **Hanya pakai backbone berupa BASE LM (foundation), bukan model yang sudah di-fine-tune NER** (mis. `*-NER`, `*-ner-v*`). Model yang sudah NER membawa skema label lain (umumnya PER/ORG/LOC tanpa EVENT/TIME) → itu skenario *transfer learning*, **bukan** perbandingan backbone, dan harus diframe terpisah. Lihat catatan di bawah.
**Catatan penting (nyambung temuan kapitalisasi):** model `cahya` **uncased** → huruf dikecilkan, sinyal kapital hilang. Ini justru eksperimen menarik: menguji seberapa besar NER bergantung pada kapitalisasi. Pastikan `AutoTokenizer.from_pretrained(MODEL_NAME)` (do_lower_case otomatis ikut model). DistilBERT: kelas `AutoModelForTokenClassification` tetap jalan, lebih cepat.

---

## Grup C — Ablation POS-tag

**Status saat ini:** kolom `pos_tag` di CSV semua `NN` (placeholder) → POS belum pernah benar-benar dipakai. Untuk menguji "berpengaruh/tidak", perlu POS **riil**.

### Langkah 1 — generate POS riil (no-GPU, perlu install)
POS tagger Indonesia belum terinstall. Opsi: **Stanza** (punya model `id`).
```powershell
venv\Scripts\pip install stanza
```
```python
import stanza; stanza.download("id")
nlp = stanza.Pipeline("id", processors="tokenize,pos", tokenize_pretokenized=True)
# untuk tiap chunk: kirim list token (sudah ter-split), ambil upos per token
```
> Aku bisa siapkan script `generate_pos_tags.py` yang mengisi kolom `pos_tag` riil (align ke token existing) kalau Stanza sudah diinstall — tinggal bilang.

### Langkah 2 — integrasi (pilih salah satu)
1. **POS embedding concat** (paling "POS sebelum model" secara harfiah): tambah `nn.Embedding(n_pos, d_pos)`, concat ke output BERT sebelum classifier. Perlu subclass model — **paling berat**, paling defensible.
2. **POS sebagai token tambahan** (lebih ringan): sisipkan tag sebelum kata (`[NN] Madinah`) — lebih lemah secara metodologi.

Rekomendasi: mulai opsi 1 minimal (embedding kecil d_pos=16, concat) untuk jawab "berpengaruh/tidak". Ini ablation, jadi yang penting **dengan vs tanpa** di config yang sama.

---

## Protokol evaluasi (semua skenario)
- Data: **gold dikoreksi** (train/test/unlabelled/augmented yang sudah di-regenerate).
- Metrik utama: **F1 macro** + **F1 EVENT** + **F1 TIME** (kelas minoritas), micro sebagai sekunder.
- Re-eval lokal tanpa GPU: `evaluate_seqeval.py --model <path> --tag <nama>`.
- Bandingkan head-to-head di test yang sama → tabel Bab 4.
