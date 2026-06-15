#!/usr/bin/env python3
"""
build_paraphrase_notebook.py — emit notebook Colab: generate augmentasi PARAFRASE (LLM open-weight,
TANPA API) LALU GABUNG dengan mention-replacement (v2) jadi SATU file augmentasi final.

Output notebook : src/pseudo_labelling/SRL-NER/augment_combined_colab.ipynb
Output data (di Colab/Drive): train_augmented_final.csv = train + mention-aug + paraphrase-aug

Mekanisme parafrase: LLM tulis-ulang kalimat tapi entitas dipertahankan persis; label BIO
diproyeksikan ulang via pencocokan token; hasil yang entitasnya hilang/ambigu DIBUANG (guard).
Fokus kalimat kelas minoritas (EVENT/TIME/I-LOCATION). No-GPU di sini (cuma nulis notebook).
"""
from __future__ import annotations
import json
from pathlib import Path

MD_TITLE = r"""# Augmentasi GABUNGAN: mention-replacement + parafrase (LLM open-weight)

Menghasilkan **satu** file augmentasi final = `train.csv` + augmentasi *mention-replacement*
(`train_augmented_v2`, sudah ada) + augmentasi *parafrase* (LLM, dibuat di sini). LLM **tanpa API** —
model open-weight dijalankan di Colab (GPU, 4-bit). Parafrase menjaga entitas persis lalu label BIO
diproyeksikan ulang; hasil yang entitasnya hilang/ambigu **dibuang** (guard).

**Pakai:**
1. Runtime > Change runtime type > **GPU** (T4 cukup untuk 4-bit).
2. Pastikan `train.csv` DAN `train_augmented_v2.csv` ada di `MyDrive/TA-Sirah/` (dua-duanya di bundle).
3. (Kalau model Llama/SahabatAI ter-gate) `!huggingface-cli login` di sel terpisah.
4. Run all → cek sel validasi sampel → download `train_augmented_final.zip`.
5. **Setelah ini** baru jalankan notebook POS untuk mengisi `pos_tag` pada `train_augmented_final.csv`.

> Jujur: parafrase entity-preserving wajar banyak ke-*discard* (sehat). Wajib cek sampel sebelum dipakai."""

INSTALL = r"""!pip install -q -U transformers accelerate bitsandbytes"""

CONFIG = r"""import os
from google.colab import drive
drive.mount('/content/drive')

# === Model open-weight (jalan di Colab GPU, TANPA API) ===
MODEL_NAME = "GoToCompany/llama3-8b-cpt-sahabatai-v1-instruct"   # Indonesian-specialized 8B
# Fallback tanpa gating:  MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
# Llama/SahabatAI mungkin perlu: !huggingface-cli login  (accept license di HF dulu)

DATASET_DIR = '/content/drive/MyDrive/TA-Sirah'
TRAIN_CSV   = os.path.join(DATASET_DIR, 'train.csv')
V2_CSV      = os.path.join(DATASET_DIR, 'train_augmented_v2.csv')      # mention-replacement (sudah ada)
PARA_CSV    = os.path.join(DATASET_DIR, 'train_augmented_paraphrase.csv')  # intermediate parafrase
FINAL_CSV   = os.path.join(DATASET_DIR, 'train_augmented_final.csv')   # <-- GABUNGAN, dipakai skenario S4

N_PARAPHRASE = 1                     # parafrase per kalimat minoritas
MINOR_TYPES  = {'EVENT', 'TIME'}     # fokus kelas minoritas
FOCUS_ILOC   = True
SEED = 42
print('train.csv             :', os.path.exists(TRAIN_CSV))
print('train_augmented_v2.csv:', os.path.exists(V2_CSV), '(wajib ada untuk gabungan)')"""

LOAD = r"""import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
set_seed(SEED)

bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                         bnb_4bit_compute_dtype=torch.bfloat16)
tok = AutoTokenizer.from_pretrained(MODEL_NAME)
llm = AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb, device_map='auto')
if tok.pad_token_id is None:
    tok.pad_token_id = tok.eos_token_id
print('loaded:', MODEL_NAME)"""

RECON = r"""import pandas as pd, re
df = pd.read_csv(TRAIN_CSV, dtype=str, keep_default_na=False)

def chunk_rows(d):
    return [(tid, g['token'].astype(str).tolist(), g['label'].astype(str).tolist())
            for tid, g in d.groupby('text_id', sort=False)]

def entities(labs):
    ents=[]; i=0; n=len(labs)
    while i < n:
        if labs[i].startswith('B-'):
            typ=labs[i][2:]; j=i+1
            while j < n and labs[j] == 'I-'+typ: j+=1
            ents.append((typ, i, j)); i=j
        else:
            i+=1
    return ents

_QH = re.compile(r"\(\s*[A-Z][\w\s'-]*:\s*\d")   # guard Quran/hadits (Surah: ayat)

def is_minor(labs):
    if any(t in MINOR_TYPES for t,_,_ in entities(labs)): return True
    if FOCUS_ILOC and any(l == 'I-LOCATION' for l in labs): return True
    return False

chunks  = chunk_rows(df)
targets = [(tid,toks,labs) for tid,toks,labs in chunks
           if is_minor(labs) and not _QH.search(' '.join(toks))]
print(f'target parafrase (kalimat minoritas): {len(targets)} dari {len(chunks)} chunk')"""

FN = r"""def find_sub(seq, sub, used):
    L=len(sub)
    for s in range(0, len(seq)-L+1):
        if seq[s:s+L]==sub and not any(used[s:s+L]):
            return s
    return None

def gen_paraphrase(text, entity_strs):
    keep = '; '.join('"'+e+'"' for e in entity_strs)
    msgs = [
        {'role':'system','content':'Anda penulis bahasa Indonesia yang teliti.'},
        {'role':'user','content':(
            'Tulis ulang kalimat berikut dalam bahasa Indonesia dengan makna SAMA '
            'tetapi susunan dan pilihan kata berbeda. '
            'WAJIB mempertahankan frasa berikut PERSIS apa adanya '
            '(jangan diubah, diterjemahkan, atau dihapus): ' + keep + '. '
            'Jawab HANYA satu kalimat hasil, tanpa penjelasan dan tanpa tanda kutip.\n\n'
            'Kalimat: ' + text)},
    ]
    ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors='pt').to(llm.device)
    with torch.no_grad():
        out = llm.generate(ids, max_new_tokens=256, do_sample=True, temperature=0.7,
                           top_p=0.9, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()

def reproject(para, ent_specs):
    ptoks = para.split()
    labels = ['O']*len(ptoks); used=[False]*len(ptoks)
    for typ, etoks in ent_specs:
        pos = find_sub(ptoks, etoks, used)
        if pos is None:
            return None
        labels[pos] = 'B-'+typ
        for k in range(pos+1, pos+len(etoks)): labels[k] = 'I-'+typ
        for k in range(pos, pos+len(etoks)):   used[k] = True
    return ptoks, labels"""

RUN = r"""from tqdm import tqdm
new_rows=[]; kept=0; discarded=0
for tid, toks, labs in tqdm(targets):
    text = ' '.join(toks)
    ent_specs   = [(typ, toks[i:j]) for typ,i,j in entities(labs)]
    entity_strs = [' '.join(e[1]) for e in ent_specs]
    for k in range(N_PARAPHRASE):
        para = gen_paraphrase(text, entity_strs)
        if (not para) or (para.strip() == text.strip()):
            discarded+=1; continue
        res = reproject(para, ent_specs)
        if res is None:
            discarded+=1; continue
        ptoks, plabs = res
        ntid = tid + '_para' + str(k+1)
        for idx,(t,l) in enumerate(zip(ptoks, plabs), start=1):
            new_rows.append({'text_id':ntid, 'id':ntid+'.'+str(idx).zfill(3),
                             'token':t, 'pos_tag':'NN', 'label':l})
        kept+=1
print('parafrase disimpan:', kept, '| dibuang (guard):', discarded)"""

SAVE = r"""para_aug = pd.DataFrame(new_rows, columns=['text_id','id','token','pos_tag','label'])
pd.concat([df, para_aug], ignore_index=True).to_csv(PARA_CSV, index=False)   # intermediate (transparansi)

# === GABUNG JADI SATU: train + mention-replacement(v2) + paraphrase ===
orig_ids = set(df['text_id'])
v2 = pd.read_csv(V2_CSV, dtype=str, keep_default_na=False)
mention_aug = v2[~v2['text_id'].isin(orig_ids)]          # baris augmented mention SAJA (train asli tak digandakan)
final = pd.concat([df, mention_aug, para_aug], ignore_index=True)
final.to_csv(FINAL_CSV, index=False)

print('FINAL ->', FINAL_CSV)
print(f'  baris {len(final)} = train {len(df)} + mention-aug {len(mention_aug)} + paraphrase-aug {len(para_aug)}')
print('  B-EVENT:', (final['label']=='B-EVENT').sum(), '| B-TIME:', (final['label']=='B-TIME').sum())"""

VALIDATE = r"""# Validasi manual sampel parafrase (WAJIB dilihat: entitas utuh & makna masuk akal)
for sid in para_aug['text_id'].unique()[:12]:
    g = para_aug[para_aug['text_id']==sid]
    print(sid, '->', ' '.join(g['token'].tolist()))
    print('   entitas:', [t for t,l in zip(g['token'],g['label']) if l!='O'])
print()
import zipfile
from google.colab import files
z = '/content/train_augmented_final.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(FINAL_CSV, arcname='train_augmented_final.csv')
files.download(z)"""

CELLS = [
    ("markdown", MD_TITLE), ("code", INSTALL), ("code", CONFIG), ("code", LOAD),
    ("code", RECON), ("code", FN), ("code", RUN), ("code", SAVE), ("code", VALIDATE),
]


def to_source(text: str) -> list[str]:
    lines = text.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


def main() -> None:
    repo = Path(__file__).resolve()
    while repo.parent != repo and not (repo / "CLAUDE.md").exists():
        repo = repo.parent
    out = repo / "src/pseudo_labelling/SRL-NER/augment_combined_colab.ipynb"
    cells = []
    for ctype, content in CELLS:
        c = {"cell_type": ctype, "metadata": {}, "source": to_source(content)}
        if ctype == "code":
            c["execution_count"] = None
            c["outputs"] = []
        cells.append(c)
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[ok]", out.relative_to(repo), "| cells:", len(cells))


if __name__ == "__main__":
    main()
