# Review Under-Annotation (sudah disaring dari sub-span & coverage bias)
> Read-only. `[[...]]` = kemunculan yang **tidak tercakup span gold mana pun** (miss riil).

**Total miss riil:** 110  | **kapital (kandidat kuat):** 24  | huruf-kecil (cek kata umum): 86

**Miss kapital per suggested-label:** EVENT=24

> Urut: yang punya miss-kapital terbanyak dulu (paling mungkin entitas asli yang ke-skip).

| surface | suggested | miss riil | kapital | kecil |
|---|---|---:|---:|---:|
| isra | EVENT | 24 | 24 | 0 |
| hijrah | EVENT | 81 | 0 | 81 |
| hasan | PERSON | 2 | 0 | 2 |
| abu awanah | PERSON | 2 | 0 | 2 |
| hari tasyriq | TIME | 1 | 0 | 1 |
| abu thalib | PERSON | 0 | 0 | 0 |
| ka'b | PERSON | 0 | 0 | 0 |
| zaid | PERSON | 0 | 0 | 0 |
| badr | LOCATION | 0 | 0 | 0 |
| umayyah | PERSON | 0 | 0 | 0 |
| uhud | LOCATION | 0 | 0 | 0 |
| khalid | PERSON | 0 | 0 | 0 |
| utsman | PERSON | 0 | 0 | 0 |
| ramadhan | TIME | 0 | 0 | 0 |
| jabir | PERSON | 0 | 0 | 0 |
| rabi'ul awwal | TIME | 0 | 0 | 0 |
| mu'adz | PERSON | 0 | 0 | 0 |
| as'ad | PERSON | 0 | 0 | 0 |
| syawwal | TIME | 0 | 0 | 0 |
| bulan rabi'ul awwal | TIME | 0 | 0 | 0 |
| sa'd bin mu | PERSON | 0 | 0 | 0 |
| utbah | PERSON | 0 | 0 | 0 |
| muharram | TIME | 0 | 0 | 0 |
| bulan muharram | TIME | 0 | 0 | 0 |
| abu na | PERSON | 0 | 0 | 0 |
| bulan syawwal | TIME | 0 | 0 | 0 |
| bulan shafar | TIME | 0 | 0 | 0 |
| khandaq | LOCATION | 0 | 0 | 0 |
| sya'ban | TIME | 0 | 0 | 0 |
| usamah | PERSON | 0 | 0 | 0 |
| dzul hijjah | TIME | 0 | 0 | 0 |
| rajab | TIME | 0 | 0 | 0 |
| penaklukan makkah | EVENT | 0 | 0 | 0 |
| bulan rajab | TIME | 0 | 0 | 0 |
| baiat aqabah | EVENT | 0 | 0 | 0 |
| abu sa | PERSON | 0 | 0 | 0 |
| muth'im bin adi | PERSON | 0 | 0 | 0 |
| abul huqaiq | PERSON | 0 | 0 | 0 |
| abu jahl | PERSON | 0 | 0 | 0 |
| rabi'ul akhir | TIME | 0 | 0 | 0 |
| bulan dzul hijjah | TIME | 0 | 0 | 0 |
| utbah bin rabi | PERSON | 0 | 0 | 0 |
| perang bu | EVENT | 0 | 0 | 0 |
| ibnu sa | PERSON | 0 | 0 | 0 |
| ibnu qami | PERSON | 0 | 0 | 0 |
| asad bin abdul uzza | PERSON | 0 | 0 | 0 |
| shafiyyah | PERSON | 0 | 0 | 0 |
| bulan rabi'ul akhir | TIME | 0 | 0 | 0 |
| khabbab | PERSON | 0 | 0 | 0 |
| abu sa'd | PERSON | 0 | 0 | 0 |
| mi'raj | EVENT | 0 | 0 | 0 |
| amir bin sha'sha | PERSON | 0 | 0 | 0 |
| al-muththalib bin abdi | PERSON | 0 | 0 | 0 |
| al-ash bin wa | PERSON | 0 | 0 | 0 |
| tsabit bin qais | PERSON | 0 | 0 | 0 |
| tahun 11 h | TIME | 0 | 0 | 0 |
| nadhr bin al-harits | PERSON | 0 | 0 | 0 |
| harun | PERSON | 0 | 0 | 0 |
| aban bin sa'id | PERSON | 0 | 0 | 0 |

---

## Contoh konteks per surface (maks 6)

### isra → **EVENT**  (miss 24: 24 kapital / 0 kecil)
- 🔠 `000035-002` … uturan beliau dalam hadits tentang [[Isra]]' . Sebagian pakar menambahi dengan
- 🔠 `000013-005` … an, dalam surat An-Nahl: 58-59, Al-[[Isra]] : 31, dan At-Takwir: 8. Tetapi hal
- 🔠 `000080-001` … diannya, yaitu sebagai berikut: 1. [[Isra]]' terjadi pada tahun tatkala Allah
- 🔠 `000080-001` … i menurut pendapat Ath-Thabari. 2. [[Isra]]' terjadi lima tahun setelah diutus
- 🔠 `000080-001` … nurutAn-Nawawi dan Al-Qurthubi. 3. [[Isra]]' terjadi pada malam tanggal 27 bul
- 🔠 `000080-001` … shurfuri. 4. Ada yang berpendapat, [[Isra]]' terjadi enam bulan sebelum hijrah

### hijrah → **EVENT**  (miss 81: 0 kapital / 81 kecil)
- 🔡 `000083-007` … Khandaq pada tahun kelima setelah [[hijrah]] Sebelum tiba musim haji tahun keti
- 🔡 `000074-003` … at tentang orang-orang Muslim yang [[hijrah]] ke Habasyah "Dan orang-orang yang
- 🔡 `000080-001` … , Isra' terjadi enam bulan sebelum [[hijrah]], atau pada bulan Muharram tahun da
- 🔡 `000080-001` … terjadi setahun dua bulan setelah [[hijrah]]. tepatnya pada bulan Muharram tahu
- 🔡 `000080-001` … pat, Isra' terjadi setahun sebelum [[hijrah]], atau pada bulan Rabi'ul Awwal tah
- 🔡 `000099-001` … pada bulan Dzul-Qa'dah tahun dari [[hijrah]] 2. Tahapan masa perdamaian dengan

### hasan → **PERSON**  (miss 2: 0 kapital / 2 kecil)
- 🔡 `000086-002` … i dengan kalian." 122 Dengan isnad [[hasan]]. Al-Hakim dan Ibnu Hibban menshahi
- 🔡 `000359-009` … bu Dawud meriwayatkan dengan isnad [[hasan]] dari Sira' binti Nabhan, dia berka

### abu awanah → **PERSON**  (miss 2: 0 kapital / 2 kecil)
- 🔡 `000284-003` … a shalat dua rakaat. Dalam riwayat [[abu Awanah]] disebutkan, "Pedang beliau jatuh d
- 🔡 `000284-004` … Dalam riwayat [[abu Awanah]] disebutkan, "Pedang beliau jatuh d

### hari tasyriq → **TIME**  (miss 1: 0 kapital / 1 kecil)
- 🔡 `000361-001` … rat An-Nashr pada pertengahan hari-[[hari tasyriq]]. Sebenarnya semua ini bisa dikenal
