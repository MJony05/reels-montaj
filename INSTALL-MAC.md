# Mac'ga o'rnatish (git va GitHub kerak emas)

Zip'ni Finder'da ikki marta bosib oching (`reels-montaj` papkasi chiqadi, masalan `~/Downloads/reels-montaj`).

## 1-qadam. Homebrew (1 marta)
Yangi Mac'da Homebrew yo'q. Terminal'ni oching va https://brew.sh dagi bitta buyruqni nusxalab ishga tushiring.
U Command Line Tools'ni ham o'rnatadi (ichida git va python3 bor). Tugagach Terminal'ni yoping va qayta oching.

```bash
brew install python@3.12
```

## 2-qadam. Skill'ni Claude Code'ga qo'yish (eng oddiy yo'l)
```bash
mkdir -p ~/.claude/skills
cp -R ~/Downloads/reels-montaj/plugins/reels-montaj/skills/reels-montaj ~/.claude/skills/
```
Claude Code'ni qayta ishga tushiring. Endi video papkasida shunday yozing:

> `video.mov` ni Instagram uchun montaj qilib ber

Claude birinchi marta kerakli dasturlarni (ffmpeg, Python muhiti, paketlar) tekshiradi va **sizdan ruxsat so'rab** o'rnatadi
(Python 3.12 bilan: `python3.12 .../setup.py --install`). Katta modellarni (Whisper ~3 GB, odamni kesish ~15 MB) ham ruxsat bilan yuklaydi.

## Boshqa yo'l: plugin sifatida (papkadan)
Claude Code ichida:
```
/plugin marketplace add ~/Downloads/reels-montaj
/plugin install reels-montaj@reels-montaj
/reels-montaj:setup
```
Agar bu ishlamasa, 2-qadamdagi oddiy yo'ldan foydalaning — ikkalasi ham bir xil ishlaydi.

## Yangilash
Yangi zip kelsa, 2-qadamdagi `cp -R` buyrug'ini qayta bajaring (eski `~/.claude/skills/reels-montaj` ni almashtiring).

## Muammo bo'lsa
Xato matnini Claude'ga ko'rsating: u `references/troubleshooting.md` dan foydalanib tuzatadi. Mac versiyasi hali sinalmagan, shuning uchun
birinchi ishga tushirishda kichik tuzatish kerak bo'lishi mumkin.
