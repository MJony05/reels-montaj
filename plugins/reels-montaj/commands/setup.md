---
description: Reels montaj uchun kerakli dasturlarni tekshiradi va (ruxsat bilan) o'rnatadi
---

Reels montaj skilli uchun muhitni tayyorla. Skill papkasi: `reels-montaj` skilli joylashgan papka (`skills/reels-montaj`), skriptlar `scripts/` ichida.

1. `python <skill>/scripts/setup.py --check` ni ishga tushir va natijani foydalanuvchiga qisqa ko'rsat (nima bor, nima yo'q).
2. Hammasi OK bo'lsa — shuni ayt va tugat.
3. Yetishmayotgan narsalar bo'lsa, FOYDALANUVCHIDAN RUXSAT SO'RA: nima o'rnatilishi (ffmpeg, alohida Python muhiti `~/.reels-montaj/venv`, paketlar: numpy, opencv-python, pillow, playwright, onnxruntime, faster-whisper; Apple Silicon'da mlx-whisper), taxminiy hajm (~1 GB) va bo'sh joy yetarliligi. Mac'da Homebrew yo'q bo'lsa avval https://brew.sh ni o'rnatish kerakligini ayt (o'zing o'rnatma).
4. Rozilik olgach: `python <skill>/scripts/setup.py --install`. Xato bo'lsa sababini tushuntir va tuzat.
5. Odam orqasidagi matn (hook) kerakmi so'ra; kerak bo'lsa ruxsat bilan `python <skill>/scripts/setup.py --models rvm` (~15 MB). Whisper modeli (~3 GB) hozir yuklanmaydi — birinchi transkripsiyada, yana ruxsat bilan.
6. `--check` ni qayta yurgizib tasdiqla. Natijani 3-4 qatorda ayt.
