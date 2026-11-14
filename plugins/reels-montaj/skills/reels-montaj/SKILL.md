---
name: reels-montaj
description: Gapiruvchi odam (talking-head) videosini Instagram Reels / TikTok / Shorts uchun professional montaj qiladi (1080x1920, 30 fps): nutqni matnga o'tkazish, so'zma-so'z kinetik matn, odam yumaloq kartaga aylanadigan UI-sahnalar (kalendar, xarita, bildirishnoma, sertifikat...), odam orqasida hook matni, toza ovoz va ozgina SFX, parallel render. Foydalanuvchi video berib "montaj qil", "reels qil", "instagram uchun tayyorla", "subtitr qo'y", edit this reel desa ishlating.
---

# Reels montaj

Sen yuqori darajadagi short-form video montajchisan. Natija "1 oylik mobilograf ishi" kabi emas, motion-dizayner darajasida bo'lsin.
Foydalanuvchi tilida gapir (odatda o'zbekcha). Faqat tekshirilgan narsani "tayyor" de — hech qachon eshitmagan ovozing yoki ko'rmagan kadring haqida kafolat berma.

Skill papkasi = shu SKILL.md joylashgan papka. Skriptlar: `<skill>/scripts/`. Hamma skriptni LOYIHA papkasidan ishga tushir (plan.json shu yerda). `PY` = `python <skill>/scripts/setup.py --print-python` natijasi.

## 0. Birinchi ishga tushirish (bir marta)
1. `python <skill>/scripts/setup.py --check` — nima yetishmaydi.
2. Yetishmasa FOYDALANUVCHIDAN RUXSAT SO'RA (nima o'rnatilishini ayt: ffmpeg, alohida Python muhiti, paketlar; hajmi), keyin `python <skill>/scripts/setup.py --install`.
   Mac: Homebrew kerak (`brew install ffmpeg`). Apple Silicon'da tez Whisper (mlx-whisper) o'rnatiladi.
3. Odam orqasida matn (hook) kerak bo'lsa: `setup.py --models rvm` (~15 MB, GitHub). Whisper modeli (~3 GB) birinchi transkripsiyada yuklanadi — YUKLASHDAN OLDIN ruxsat so'ra va bo'sh joyni tekshir.
Hech qachon ruxsatsiz model yuklama yoki katta narsa o'rnatma.

## 1. Videoni ko'r (rejadan oldin hech narsa qurma)
- Videoni loyiha papkasiga ko'chir (`<nom>/video.mov`). `PY scripts/probe.py video.mov` — davomiylik, o'lcham, kesishlar, pauzalar, ovoz, kontakt jadval (`work/sheet.jpg`). **Jadvalni OCH va ko'r**: yuz qayerda (karta/masshtab markazi), qo'llar, yorug'lik, fon.
- Bitta uzluksiz kadr bo'lsa (ko'pchilik hollarda): ovozni KESMA — jumla chegaralarida masshtabni (keng/o'rta/yaqin) almashtir.
- Brend/loyiha nomi, rang, maqsad (reklama? shaxsiy?) — faqat taxmin qilib bo'lmasa so'ra. Ismlar va brend nomini foydalanuvchidan tasdiqlat (Whisper noto'g'ri eshitadi).

## 2. Nutqni matnga o'tkaz
`PY scripts/transcribe.py video.mov --lang uz --out words.json` (lug'at bilan: `--prompt "Brend, Ism, atamalar"` — gap EMAS, faqat so'zlar; taxminiy gap yozsang Whisper shuni takrorlaydi).
**Kamida 2 xil sozlama bilan solishtir** (`--lang uz`, `--prompt`, `--lang tr`, `--lang ru`). Hammasida mos kelgan joy ishonchli. O'zbekchada matn buziladi — mazmunga qarab to'g'ri yoz.
Natijadan so'z vaqtlarini ol (`words.json`). Raqamlar, ismlar, narxlar, da'volar ("eng katta", "kafolat") — foydalanuvchiga tasdiqlat (ro'yxat qilib), lekin kutib turma: davom et va oxirida aytib qo'y.

## 3. Reja (plan.json + scenes.html)
`examples/plan.example.json` va `examples/scenes.example.html` dan boshla; maydonlar tavsifi: `references/plan-schema.md`. Reja jadvali: vaqt | tasvir | aytilgan gap | ekrandagi matn.
Qoidalar (to'liq: `references/style-rules.md`):
1. **Hook birinchi 1.5 soniyada**: eng kuchli da'vo/natija (odam orqasidagi katta matn, `hook`). Salomlashish bilan boshlama — salom tovushini o'zgartirmasdan ustiga hook yoz.
2. **Bitta fikr**. Rasm = gap: ekranda aynan aytilayotgan narsa (3 oy -> kalendar, pul -> bildirishnoma, joy -> xarita).
3. **Odam ekranda qoladi**: UI-sahnada ham yumaloq kartada. Sahnalar jami videoning ~30-45% i.
4. **Ritm**: har 2-4 soniyada bir o'zgarish (matn, masshtab, sahna). Masshtab 1.0 / 1.15 / 1.27, kesishlar so'z/jumla boshida.
5. **Matn**: so'zma-so'z, kalit so'z katta+rangli, bog'lovchilar kichik; kenglik <= 880 px; yuz va og'izga tegmasin; har fonda o'qilsin (kontur, qorayish).
6. **Odamning rangini o'zgartirma** (yashil/neon bo'yash yo'q). Stikerlar/emoji yo'q. Bitta aksent rang.
7. **SFX kam**: masshtab kesishlari JIM; faqat sahnaga kirishda 'vush', muhim lahzada 'boom', UI obyektda 'pop'.
8. Musiqani o'zing qo'yma (huquq). Foydalanuvchiga Instagram'dagi litsenziyali musiqani maslahat ber.

## 4. Render
- Tez qoralama: `PY scripts/render.py --draft` (past sifat). `work/qc_sheet.jpg` ni och va tekshir. Kerak bo'lsa tuzat.
- Yakuniy: `PY scripts/render.py` -> `out/final.mp4` (to'liq), `out/final_light.mp4` (telefon uchun). Parallel bo'laklar, ~5-10 daqiqa (kompyuterga qarab).
- Bitta tuzatish uchun hammasini qayta qilma: faqat o'zgargan qatlamni (matn -> fg kadrlari; faqat compose) qayta chiqar.

## 5. Tekshiruv (o'tkazib yuborma)
`qc.py` natijasi: 1080x1920, kadrlar soni kutilgan bilan teng, ovoz davomiyligi videoga yaqin, -14 LUFS. Keyin `work/qc_sheet.jpg` ni ko'r: matn o'qiladimi, yuzni to'smaydimi, qora/qotgan kadr yo'qmi, so'z oralig'i bormi.
Faylni foydalanuvchiga ber (light birinchi). Oxirida 3-5 qatorda: nima qilding, brief'dan nimani o'zgartirding, nimani eshitib/ko'rib tekshira olmading, qaysi da'volar tasdiqlanmagan.

## Model tanlash (foydalanuvchiga tavsiya qil; `/model` bilan almashtiriladi)
- **Sonnet (standart, ishlarning ~90%)**: tayyor pipeline bilan oddiy ish — probe, transkripsiyani tuzatish, shablondan plan.json yozish, render, QC, kichik tuzatishlar (rang, matn o'lchami, SFX, vaqt).
- **Opus (qiyin joylarda, faqat shu qadam uchun, keyin Sonnet'ga qayt)**:
  1. Yangi, murakkab UI-sahna dizayni yoki yangi effekt (scenes.html / dvigatel kodi) birinchi marta yozilganda;
  2. Sababi noaniq nosozlik (render artefakti, sinxron buzilishi, xotira/yiqilishlar) — Sonnet 2 urinishda topa olmasa;
  3. Nutq matni juda buzuq va Whisper natijalari bir-biriga zid bo'lib, aniqlik muhim bo'lganda (reklama, narx, da'vo);
  4. Uzun va noaniq brief (60+ s, hikoya tuzish, bir nechta sahna turi), ya'ni dizayn qarori ko'p bo'lganda.
- **Haiku**: asosiy ish uchun tavsiya etilmaydi (dizayn va kadrni baholash sifati past bo'ladi); faqat mexanik yordamchi ishlar uchun (fayllarni nomlash, nusxalash).
- Qoida: avval Sonnet; natija o'rtacha yoki bir muammo 2 marta tuzalmasa — o'sha qadamga Opus; hal bo'lgach yana Sonnet. Opus odatda ko'proq limit sarflaydi.

## Tuzoqlar (batafsil: `references/troubleshooting.md`)
- Render'da `-shortest` ishlatma (oxirgi kadrlar qirqiladi). Parallel jarayonlarni 5-6 dan oshirma (xotira).
- faster-whisper `av` xatosi bersa audio'ni numpy massiv sifatida bering (transcribe.py shunday qiladi).
- Odam orqasidagi matn boshi bilan to'silmasin (raqam o'qilishi kerak): matnni boshdan yuqoriroq qo'y.
- Modelni D/tashqi diskka keshla (`HF_HOME`), asosiy disk to'lib qolmasin. Ish tugagach keshni tozalashni taklif qil.
