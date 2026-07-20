# Contoh Berjalan NER → Knowledge Graph (satu data yang sama) — Bu Nanik #5 & Bu Dini #7

> Menjawab: alur runtut dari **satu contoh data yang sama** — teks → chunk → BIO → entitas →
> normalisasi → pasangan → relasi → node/edge → Neo4j. Data nyata dari pipeline (chunk
> `000071-003`, hal 165–168).

## Tahap 1 — Teks Sirah (dalam satu chunk)

Chunk `000071-003` (Bab: "Faktor-faktor yang Menguatkan Kesabaran…", hal 165–168) memuat kalimat:

> "Tatkala **Abu Jahal** mengajaknya pergi saat **Perang Badr**, dia membeli seekor onta paling
> bagus di Makkah…"

## Tahap 2 — Chunk → token + label BIO

Kalimat ditokenisasi (tingkat kata) lalu diberi label BIO (potongan relevan):

| Token | Tatkala | Abu | Jahal | mengajaknya | pergi | saat | Perang | Badr |
|---|---|---|---|---|---|---|---|---|
| BIO | O | **B-PERSON** | **I-PERSON** | O | O | O | **B-EVENT** | **I-EVENT** |

(Di dalam model, tiap kata dipecah jadi subtoken dan hanya subtoken pertama yang diberi label —
lihat `definisi_token_subtoken.md`.)

## Tahap 3 — Entitas hasil NER (gabung B-/I-)

| Entitas | Tipe |
|---|---|
| Abu Jahal | PERSON |
| Perang Badr | EVENT |

## Tahap 4 — Normalisasi alias (ke bentuk kanonik)

Variasi ejaan disatukan ke nama kanonik (`alias_map.json`):

- `Abu Jahl` → **Abu Jahal** (PERSON)
- `Perang Badar` → **Perang Badr** (EVENT)

Pada contoh ini nama sudah kanonik, jadi tidak berubah — tetapi mekanismenya memastikan penyebutan
lain di korpus dipetakan ke simpul yang sama.

## Tahap 5 — Pemilihan pasangan entitas (co-occurrence)

Kedua entitas berada dalam **satu kalimat** (jarak < 200 karakter) → memenuhi syarat konteks yang
sama (`are_in_same_context`), sehingga menjadi **kandidat pasangan relasi**.

## Tahap 6 — Penentuan jenis & bobot relasi

Pasangan **PERSON – EVENT** dipetakan ke relasi **`INVOLVED_IN`**. Karena kedua entitas berdekatan,
diberi **bobot** sesuai tingkat kedekatan (di `edges_v4_scoped.csv`: `weight = 0,5`).

## Tahap 7 — Pembentukan node & edge

| Elemen | Nilai |
|---|---|
| Node 1 | `Abu Jahal` (:Person) |
| Node 2 | `Perang Badr` (:Event) |
| Edge | `(Abu Jahal) -[:INVOLVED_IN {weight:0.5, halaman:"165-168", chunk_id:"000071-003"}]-> (Perang Badr)` |

## Tahap 8 — Penyimpanan ke Neo4j (Cypher)

```cypher
MERGE (p:Person {name: "Abu Jahal"})
MERGE (e:Event  {name: "Perang Badr"})
MERGE (p)-[r:INVOLVED_IN]->(e)
  SET r.weight = 0.5,
      r.halaman = "165-168",
      r.chunk_id = "000071-003",
      r.evidence = "...Tatkala Abu Jahal mengajaknya pergi saat Perang Badr...";
```

Setelah tersimpan, relasi ini dapat ditelusuri lewat kueri fungsional (mis. F1: "siapa terlibat
Perang Badar?") dan tetap **dapat dilacak** ke halaman sumber melalui properti `evidence`/`halaman`.

---

### Catatan jujur
Contoh ini adalah relasi yang **benar** (Abu Jahal memang tokoh Quraisy pada Perang Badar). Namun
karena pembentukan relasi berbasis kedekatan, sebagian relasi lain bisa **keliru** (mis. negasi
"Abu Lahab tidak ikut serta" di chunk `000140-001` tetap terbentuk) — lihat
`keterbatasan_negasi_relasi.md` dan evaluasi validitas semantis.

### Sumber (reproduksibilitas)

| Tahap | Berkas |
|---|---|
| Teks/chunk | `data/result/chunking_result/sirah_chunks_final.csv` (`000071-003`) |
| Normalisasi alias | `data/result/alias_clustering/alias_map.json` |
| Relasi & bobot | `data/result/relation_result/edges_v4_scoped.csv` |
| Node | `data/result/relation_result/nodes_v4_scoped.csv` |
| Impor Neo4j | `data/result/neo4j/` (skrip Cypher v4) |
