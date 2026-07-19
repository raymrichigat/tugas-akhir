# Definisi Chunk / Token / Subtoken / Batch + Penyelarasan BIO↔Subtoken (Bu Nanik #3 & #4)

> Menjawab: (a) bedakan chunk/token/subtoken/batch; (b) cara label BIO diselaraskan dengan
> subtoken (strategi subtoken pertama + `-100`). Kode & contoh dari implementasi nyata
> (`srl_ner_sirah_0.9_colab.ipynb`, tokenizer `indolem/indobert-base-uncased`).

## 1. Definisi (dari unit terbesar ke terkecil)

| Istilah | Definisi | Contoh |
|---|---|---|
| **Chunk** | potongan teks (bisa beberapa kalimat) hasil chunking; **unit yang diberikan ke model** | satu `teks_chunk`, mis. `000008-001` |
| **Token (kata)** | unit kata/tanda baca hasil tokenisasi awal; **unit yang diberi label BIO** | `Rasulullah`, `Madinah`, `Mush'ab` |
| **Subtoken** | pecahan token oleh tokenizer WordPiece IndoBERT; **unit yang benar-benar diproses model** | `Umair` → `uma`, `##ir` |
| **Batch** | kumpulan beberapa sequence (chunk ter-tokenisasi) yang diproses bersamaan saat pelatihan | mis. 16 chunk sekaligus (batch size 16) |

Model IndoBERT melakukan **token classification atas satu urutan token yang berkonteks** (satu
chunk), bukan mengklasifikasikan tiap kata terpisah tanpa konteks. Panjang maksimum sequence =
**512 subtoken** (`model_max_length=512`, `truncation=True`).

## 2. Contoh nyata: satu kata bisa pecah jadi beberapa subtoken

Kalimat contoh (token → subtoken oleh `indolem/indobert-base-uncased`):

| Token (kata) | Subtoken hasil WordPiece |
|---|---|
| Rasulullah | `rasulullah` |
| pergi | `pergi` |
| ke | `ke` |
| Madinah | `madinah` |
| bersama | `bersama` |
| **Mush'ab** | `mush`, `'`, `ab` (3 subtoken) |
| bin | `bin` |
| **Umair** | `uma`, `##ir` (2 subtoken; `##` = penanda lanjutan) |

> Catatan: tokenizer ini **uncased**, sehingga huruf kapital dinormalisasi (Rasulullah →
> `rasulullah`). Ini relevan untuk perbandingan model cased vs uncased.

## 3. Penyelarasan label BIO ↔ subtoken (strategi subtoken pertama + `-100`)

Karena label ada di tingkat **token (kata)** sedangkan model memproses **subtoken**, label
diselaraskan: **hanya subtoken pertama tiap kata yang diberi label; subtoken lanjutan dan token
khusus (`[CLS]`/`[SEP]`) diberi `-100`** (diabaikan fungsi kerugian). Implementasi (`word_ids()`):

```python
tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased", model_max_length=512)

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples['tokens'], truncation=True, is_split_into_words=True)
    labels = []
    for i, label in enumerate(examples['label']):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:                      # token khusus [CLS]/[SEP]
                label_ids.append(-100)
            elif word_idx != previous_word_idx:       # subtoken PERTAMA sebuah kata
                label_ids.append(label[word_idx])
            else:                                     # subtoken lanjutan
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs
```

**Hasil penyelarasan untuk contoh di atas:**

| Subtoken | word_id | Label |
|---|---|---|
| `[CLS]` | — | `-100` (special) |
| `rasulullah` | 0 | **B-PERSON** |
| `pergi` | 1 | O |
| `ke` | 2 | O |
| `madinah` | 3 | **B-LOCATION** |
| `bersama` | 4 | O |
| `mush` | 5 | **B-PERSON** |
| `'` | 5 | `-100` (lanjutan) |
| `ab` | 5 | `-100` (lanjutan) |
| `bin` | 6 | **I-PERSON** |
| `uma` | 7 | **I-PERSON** |
| `##ir` | 7 | `-100` (lanjutan) |
| `[SEP]` | — | `-100` (special) |

Saat evaluasi, prediksi diambil dari subtoken pertama tiap kata lalu digabung kembali menjadi
entitas tingkat-kata.

---

### Sumber (reproduksibilitas)

| Artefak | Berkas |
|---|---|
| Fungsi tokenisasi + penyelarasan | `src/pseudo_labelling/SRL-NER/srl_ner_sirah_0.9_colab.ipynb` (`tokenize_and_align_labels`) |
| Tokenizer | `indolem/indobert-base-uncased` (`model_max_length=512`, `is_split_into_words=True`) |
