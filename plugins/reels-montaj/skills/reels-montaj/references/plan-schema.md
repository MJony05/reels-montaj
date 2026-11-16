# plan.json maydonlari

Loyiha papkasida `plan.json` (+ ixtiyoriy `scenes.html`). Vaqtlar soniyada, manba video vaqtida (montajda ovoz kesilmaydi, shuning uchun chiqish vaqti bilan bir xil).

| maydon | tavsif |
|---|---|
| `source` | manba video fayli (loyiha papkasiga nisbatan). Istalgan o'lcham: 1080x1920 ga "cover" bilan kesiladi |
| `duration` | davomiylik (s). `probe.py` ko'rsatadi |
| `fps` | 30 (standart) |
| `palette` | `accent_dark` (qorong'u kadrdagi kalit so'z rangi, ochiq-yorqin), `accent_light` (och sahnadagi to'qroq rang), `hook_color` (odam orqasidagi narx), `ink`, `bg_light` (sahna foni), `ui`/`ui2` (UI shakllari aksenti), `shade` ("r,g,b" — pastki qorayish rangi, videoning qorong'u tusiga yaqin) |
| `anchor` | `[x, y]` — standart masshtab markazi (yuz). Kadr 1080x1920 da yuzning markazi |
| `shots` | `[[boshlanish_s, masshtab], ...]` yoki `[boshlanish_s, masshtab, markaz_x, markaz_y]` (kadr turi o'zgarsa va yuz boshqa joyda bo'lsa, har kadrga o'z yuz markazini bering) — masshtab jadvali. 1.0 keng / ~1.15 o'rta / ~1.27 yaqin; har bir kesishda kichik "punch". Kesishlarni jumla/so'z boshiga qo'y |
| `card` | karta-morph: `x,y,w,h,r` (karta joyi va burchak radiusi), `face:[markaz_x, markaz_y, kenglik]` — kartada ko'rinadigan manba oynasi (yuz markazi atrofida) |
| `scenes` | `[{id, s, e, faces?}]` (`faces: [[t, markaz_x, markaz_y, kenglik], ...]` — shu sahnada kartada ko'rinadigan manba oynasi; yuz kichik bo'lsa kenglikni kamaytiring, masalan 700) — UI-sahna oynalari. Shu vaqtda odam kartaga kichrayadi, orqada `bg_<id>` foni ko'rinadi. Kirish: s-0.20..s+0.35, chiqish: e-0.40..e+0.15 |
| `hook` | `{frames: N}` — dastlabki N kadrda `back` iboralari odam ORQASIDA chiqadi (RVM maskasi kerak). 0 = yo'q |
| `grade` | `{contrast, brightness, vignette}` — standart 1.07 / 5 / 0.22 |
| `text` | `{bottom, cap_bottom, fit_width}` — subtitr zonasi (pastdan px) va maksimal kenglik (880) |
| `phrases` | kinetik matn, pastda |
| `sfx` | `{whoosh_scenes, booms:[t], pops:[t], ticks:[[t0,t1,n]], gain}` — KAM bo'lsin |
| `audio` | `{clean:true}` — ovozni tozalash zanjiri (shovqin, de-ess, kompressor). Allaqachon toza bo'lsa `false` |

## phrases
```json
{ "s": 6.86, "e": 10.68, "cap": 1, "lt": 1, "l": [["va@6.92", "*Samarqandda@7.04"], ["~eng yaxshisi@8.08"]] }
```
- `s`,`e` — iboraning ko'rinish oralig'i. `l` — qatorlar, har biri so'zlar ro'yxati.
- `*so'z` — kalit (katta, rangli), `~so'z` — kichik, oddiy — o'rta. `so'z@12.34` — so'z paydo bo'ladigan vaqt (Whisper so'z vaqtlaridan ol; yozilmasa belgilar soniga qarab taqsimlanadi). `"bir oy *nazariy"` — bir elementda bir necha so'z, `*` dan keyingilari kalit.
- `cap: 1` — kichikroq subtitr (UI-sahna ichida), `lt: 1` — och fon uchun qora matn, `hold: 1` — iboradan keyin ham ekranda qoladi (oxirgi ibora), `back: 1` — odam ORQASIDAGI hook qatlami (`hook.frames` bilan birga).
- Qator kengligi 880 px dan oshsa avtomatik kichrayadi. Odatda 2-3 qator, har qator 2-4 so'z.

## scenes.html (UI-sahnalar)
Har video uchun yangidan yoziladi (namuna: `examples/scenes.example.html`). Shartlar:
1. Har obyekt `class="ui"` (konfetti kabi nuqtalar `class="dot"`), `position:absolute`, 1080x1920 kanvasda.
2. Karta y=140..710 da turadi (plan.card). UI ni y=780..1500 ga qo'y; subtitr pastda (y~1560+). Hamma narsa 880 px keng zonada, chetlarga yaqin emas (telefon pleyer chetni kesadi).
3. `window.sceneFrame = function(t, h){...}` — har kadrda chaqiriladi. `h.pop(el, t, boshlanish, {dx,dy,rot,s0,d})` — chiqish animatsiyasi (opacity+scale+blur), `h.fadeOut(el, t, t0, d)`, `h.clamp`, `h.ioCub`, `h.oExp`, `h.oBack`, `h.$(id)`.
4. Obyekt vaqtini gapdagi so'z vaqtiga bog'la (rasm = so'z). Sahnadan chiqishdan ~0.4 s oldin hamma narsani so'ndir (`fadeOut`).
5. Sahna g'oyalari: kalendar/oy kartalari (muddat), xarita+pin (joy), bildirishnoma+sanagich (pul), sertifikat (hujjat), checklist (afzalliklar), reyting/yulduzlar (sifat), grafik (o'sish), chat-bubble (savol/javob). Emoji ISHLATMA.
