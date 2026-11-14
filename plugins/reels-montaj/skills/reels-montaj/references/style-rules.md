# Uslub qoidalari (real loyihalarda o'rganilgan)

Bu qoidalar "motion-dizayner darajasi" namunalarini kadrma-kadr o'lchab va mijoz izohlari asosida yig'ilgan. Yangi videoda ham shu darajani ushla.

## Professional ko'rinishning 6 belgisi
1. **Matn markazda va so'zma-so'z.** Har so'z aytilgan paytda xira -> aniq bo'lib chiqadi (blur+siljish+masshtab, 0.3 s). Kalit so'z katta va rangli (~104 px, w700), bog'lovchi so'zlar kichik va xira (~42 px), o'rtasi ~70 px (w600). Matn ko'krak balandligida, eng pastga yopishmagan. Oq matn ham, rangli matn ham to'q kontur bilan (har qanday fonda o'qilsin).
2. **Bitta brend palitrasi.** Bitta aksent rang (+ neytral). Videoning tusiga mos: indigo yorug'lik bo'lsa to'q sariq/ko'k aksent; do'kon ichi issiq bo'lsa ko'k/yashil. Faqat ma'qullangan rang.
3. **Grafik sahnalar gapni aynan ko'rsatadi** (videoning ~30-45%): "bir oy nazariy, bir oy amaliy" -> kalendar kartalari; "300 dollar" -> bildirishnoma + sanagich; "Samarqandda" -> xarita + pin; "sertifikat" -> sertifikat kartasi. Ovoz davom etadi.
4. **Odam hech qachon yo'qolmaydi**: to'liq ekrandan yumaloq kartaga kichrayadi (karta-morph), atrofida sahna quriladi; so'ng kartadan to'liq ekranga qaytadi. Bu eng kuchli o'tish (oddiy iris/blok o'tishdan ustun).
5. **Tez ritm**: har 2-4 s da yangilik. Jonli obyektlar: pin tushadi, sanagich sanaydi, konfetti, kartalar bir-birining ketidan chiqadi.
6. **Ovoz**: musiqasiz bo'lsa ham toza va tekis (-14 LUFS), SFX kam va ma'noli.

## Bitta uzluksiz kadrni jonlantirish (b-roll yo'q bo'lsa)
- Ovozni KESMA. Jumla/so'z boshlarida masshtabni almashtir: 1.00 -> 1.18 -> 1.28 -> 1.00 ... (har kadrda sekin +0.045 yaqinlashish, kesishda +0.05 "punch").
- Markaz yuzda (anchor). 1.28 dan oshirma — yumshab qoladi (yaqin kadrda yengil keskinlik beriladi).
- Hook: birinchi 1.5 s da eng kuchli da'vo odam ORQASIDA katta matn bo'lib chiqadi (RVM maskasi). Raqam to'liq o'qilishi kerak: matn pastki chekkasi bilan boshning tepasiga ozgina kirsin, o'rtadagi raqamni bosh to'smasin.

## Mijoz fikrlaridan kelib chiqqan taqiqlar
- Odamni yashil/neon rangga bo'yama, neon kontur bilan ajratma (mijoz yoqtirmadi). Odam rangi tabiiy qolsin.
- Emoji-stikerlar qo'yma ("videoni oddiy qilib qo'yadi").
- Matn katta va qalin ("jirniy") bo'lmasin: kalit ~104 px w700, glow zaif yoki yo'q.
- Kalit so'z rangi fonga mos o'qilsin: qorong'u fonda yorqin (kontur bilan), och fonda to'q rang.
- Har masshtab kesishida "vush/swish" qo'yma — juda ko'p takrorlanadi. SFX faqat sahnaga kirishda, muhim lahzada, UI obyektda.
- Brend nomini foydalanuvchidan so'ra va tasdiqlat (peshtoqdagi yozuv brend bo'lmasligi mumkin; Whisper noto'g'ri eshitadi).
- Narx/raqam/da'volarni (daromad, "eng katta", "kafolat") tasdiqlatmasdan ommaga chiqarma.

## Xavfsiz joylashuv (Instagram)
- Kenglik: matn <= 880 px markazda (telefon pleyer chetni kesadi). Pastki ~350 px Instagram UI bilan to'la; subtitr bottom ~300-330 px.
- Yuqori ~200 px ham UI uchun band: muhim narsani u yerga qo'yma (hook matni ~y 130-400, bosh tepasidan yuqori).
- Matn yuz va og'izga tegmasin; qo'l/ko'ylak ustida bo'lsa pastki qorayish va kontur o'qilishni ta'minlasin.

## Reja shabloni (49 s ga misol)
0-1.8 hook (odam orqasida narx) + salom | 1.8-6.9 keng/yaqin masshtab, kinetik matn | 6.9-10.7 sahna 1 (xarita) | 10.7-13.5 to'liq ekran | 13.5-23.9 sahna 2 (kalendar -> bildirishnoma) | 24-36.5 to'liq ekran, kalit so'zlar | 36.6-40.7 sahna 3 (sertifikat) | 40.7-49.5 CTA, hold matn.
