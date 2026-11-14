# Muammolar va yechimlar

| belgi | sabab / yechim |
|---|---|
| `ffmpeg topilmadi` | `python setup.py --install` (Mac: Homebrew kerak). O'rnatgach yangi terminal oching (PATH). `REELS_FFMPEG=/yo'l/ffmpeg` bilan ham ko'rsatish mumkin |
| Mac: `externally-managed-environment` | Homebrew Python global pip ni bloklaydi. Skriptlar alohida muhitdan (`~/.reels-montaj/venv`) ishlaydi — `setup.py --install` uni yaratadi. Hech qachon `--break-system-packages` ishlatmang |
| faster-whisper: `open() got an unexpected keyword argument 'metadata_errors'` | `av` versiyasi mos emas. transcribe.py audio'ni numpy massiv qilib beradi — o'sha skriptni ishlating |
| Whisper o'zbekchani buzadi | `--lang uz` + lug'at `--prompt`, yana `--lang tr`/`ru` bilan solishtiring; mazmunga qarab to'g'rilang. Gap bilan prompt BERMANG (takrorlaydi) |
| Apple Silicon'da Whisper sekin | `setup.py --install` mlx-whisper o'rnatadi (avtomatik tanlanadi). Qo'lda: `transcribe.py --backend mlx` |
| render: xotira to'ldi / jarayonlar yiqildi | parallel jarayonlarni kamaytiring: `render.py --workers 2 --chunks 3`. Har compose jarayoni ~1 GB |
| yakuniy videoda 4 kadr kam / sinxron buzilgan | mux'da `-shortest` ishlatilgan. render.py ishlatmaydi; qo'lda qilsangiz ham ishlatmang. `qc.py` kadr sonini tekshiradi |
| `bg/ov_####.png` topilmadi, karta ostida fon yo'q | sahna oynasi (`plan.scenes`) bilan kadr diapazoni mos emas: render.py bg kadrlarini sahna oynasi ±0.7 s uchun chiqaradi |
| matnda so'zlar yopishib ketgan | shablonda `.w{margin:0 .14em}` bor; scenes.html ichida `.w` stilini o'zgartirmang |
| Chrome topilmadi | `setup.py --install` playwright chromium ni yuklaydi (~150 MB). Chrome bo'lsa avtomatik ishlatiladi |
| shrift (Inter Tight) yuklanmadi | internet kerak (Google Fonts). Internet yo'q bo'lsa tizim shrifti (Helvetica Neue/Segoe UI) ishlatiladi — o'lchamlar biroz farq qiladi |
| odam maskasida chetlari titraydi | `segment.py` bitta uzluksiz kadrda reset qilmaydi; kadr almashganda `--reset 5.1,12.7` bering |
| asosiy disk to'ldi | Whisper keshi (`~/.cache/huggingface`, ~3 GB): `HF_HOME=<boshqa disk>` bilan yuklang; tugagach keshni o'chirishni foydalanuvchiga taklif qiling |
| hook matni raqamni bosh to'sadi | `plan.hook` matnini boshdan yuqoriroq qo'ying (templates `.blk.back{top}`), shrift kichikroq |

## Tezlik
Kompyuterga bog'liq: Apple Silicon (M1+) oddiy noutbukdan ~2-4x tez. 45-50 s video uchun render ~5-10 daqiqa; Whisper (mlx) ~1-2 daqiqa, faster-whisper CPU ~5-10 daqiqa.
Dizaynni qoralama (`--draft`) bilan tekshiring, yakuniy render'ni oxirida bir marta qiling.
