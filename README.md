# reels-montaj — Claude Code uchun professional Reels montaj plugin'i

Gapiruvchi odam videosini (talking-head) Instagram Reels / TikTok / Shorts uchun **1080x1920** professional montaj qiladi.
Siz videoni berasiz, Claude esa: nutqni matnga o'tkazadi, so'zma-so'z kinetik matn qo'yadi, gapga mos UI-sahnalar quradi
(odam yumaloq kartaga aylanib, atrofida kalendar / xarita / bildirishnoma / sertifikat chiqadi), hook'ni odam orqasiga yozadi,
ovozni tozalaydi va ozgina SFX qo'shadi.

## O'rnatish (1 marta)

Claude Code ichida:

```
/plugin marketplace add MJony05/reels-montaj
/plugin install reels-montaj@reels-montaj
```

> **Git yo'q yoki GitHub kerak emas bo'lsa** (masalan yangi Mac): zip'ni oching va [INSTALL-MAC.md](INSTALL-MAC.md) dagi oddiy yo'ldan foydalaning.

Keyin kerakli dasturlarni o'rnatish (Claude o'zi tekshiradi, **avval sizdan ruxsat so'raydi**):

```
/reels-montaj:setup
```

Bu buyruq: ffmpeg (Mac'da Homebrew orqali), alohida Python muhiti (`~/.reels-montaj/venv`), kerakli paketlar
(numpy, opencv, pillow, playwright, onnxruntime, faster-whisper; Apple Silicon'da tez Whisper — mlx-whisper) ni tekshiradi va o'rnatadi.
Katta modellar (Whisper ~3 GB, odamni kesish ~15 MB) alohida, ruxsat bilan yuklanadi.

## Ishlatish

Claude Code'da videoning papkasida shunday yozing:

> `video.mov` ni Instagram uchun montaj qilib ber. Brend nomi: ..., maqsad: ...

Claude skill'ni o'zi tanlaydi: videoni ko'radi, nutqni matnga o'tkazadi, reja tuzadi (`plan.json`), sahnalarni chizadi (`scenes.html`),
qoralama chiqaradi, tekshiradi va `out/final.mp4` + `out/final_light.mp4` ni beradi.

## Yangilash
`python3 ~/.claude/skills/reels-montaj/scripts/update.py` (skill papkadan o'rnatilgan bo'lsa; git kerak emas) yoki `/plugin marketplace update reels-montaj` (plugin sifatida o'rnatilgan bo'lsa).

## Talablar
- macOS (Apple Silicon yoki Intel), Windows yoki Linux; ~6 GB bo'sh joy (modellar bilan ~10 GB)
- Python 3.10+, ffmpeg, Google Chrome (yo'q bo'lsa playwright chromium yuklanadi)
- Internet (Google Fonts va modellar uchun, birinchi marta)

## Tezlik
Kompyuterga bog'liq. Apple Silicon (M1+) oddiy noutbukdan ~2-4 barobar tez. 45-50 soniyalik video: render ~5-10 daqiqa,
Whisper ~1-2 daqiqa (mlx) yoki ~5-10 daqiqa (CPU). Dizaynni `render.py --draft` bilan tez tekshirib, oxirida bir marta yakuniy render qiling.

## Holati
- **Windows'da to'liq sinalgan** (toza Python muhitida, 16 soniyalik namuna: 480/480 kadr, ovoz sinxroni, -14 LUFS).
- **macOS uchun yozilgan, lekin hali Mac'da sinalmagan** (Homebrew ffmpeg, alohida venv, mlx-whisper, Chrome yo'li). Birinchi ishga tushirishda
  kichik tuzatish kerak bo'lishi mumkin; Claude xatoni o'zi tuzatadi. Muammo chiqsa issue oching.
- After Effects / DaVinci Resolve bilan bog'lanmagan (ular kerak emas). Keyinchalik qo'shilishi mumkin.

## Tuzilma
```
.claude-plugin/marketplace.json
plugins/reels-montaj/
  .claude-plugin/plugin.json
  commands/setup.md                    /reels-montaj:setup
  skills/reels-montaj/
    SKILL.md                           ish tartibi va qoidalar
    scripts/                           setup, probe, transcribe, segment, capture, voice_sfx, compose, render, qc
    templates/motion.html              kinetik matn dvigateli
    examples/                          plan.example.json, scenes.example.html
    references/                        uslub qoidalari, plan sxemasi, muammolar
```

## Model tavsiyasi
Odatda **Sonnet** yetadi. Yangi murakkab sahna dizayni, sababi noaniq nosozlik yoki juda buzuq nutq matni bo'lsa, o'sha qadam uchun **Opus**.
Batafsil: `SKILL.md` ichidagi "Model tanlash".

## Litsenziya
MIT. Odamni kesish uchun [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) modeli (GPL-3.0) alohida yuklanadi va repo'ga qo'shilmagan;
nutq uchun [faster-whisper](https://github.com/SYSTRAN/faster-whisper) / [mlx-whisper](https://github.com/ml-explore/mlx-examples) ishlatiladi.
