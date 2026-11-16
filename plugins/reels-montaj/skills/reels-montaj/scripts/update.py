"""update.py — skill'ni GitHub'dagi eng yangi versiyaga yangilaydi (git kerak emas).

  python3 update.py                      ~/.claude/skills/reels-montaj ni yangilaydi
  python3 update.py --check              faqat versiyalarni solishtiradi
  python3 update.py --dest <papka>       boshqa joydagi nusxani yangilaydi

Xavfsizlik: eski papka o'chirilmaydi — ~/.reels-montaj/backup/ ga ko'chiriladi. Faqat shu repo'dan (standart MJony05/reels-montaj) yuklaydi
va hech qanday kodni ishga tushirmaydi. Plugin tizimi orqali o'rnatgan bo'lsangiz: `/plugin marketplace update reels-montaj`."""
import argparse, io, os, re, shutil, sys, time, urllib.request, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

SUB = "plugins/reels-montaj/skills/reels-montaj"


def version_of(skill_dir):
    p = os.path.join(skill_dir, "VERSION")
    return open(p, encoding="utf-8").read().strip() if os.path.exists(p) else "noma'lum (eski)"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--repo", default="MJony05/reels-montaj"); ap.add_argument("--branch", default="main")
    ap.add_argument("--dest", default=os.path.join(os.path.expanduser("~"), ".claude", "skills", "reels-montaj")); ap.add_argument("--check", action="store_true")
    o = ap.parse_args(); dest = os.path.abspath(o.dest)
    if os.path.basename(dest) != "reels-montaj" or not os.path.exists(os.path.join(dest, "SKILL.md")):
        sys.exit(f"[to'xtadi] {dest} da reels-montaj skill'i topilmadi (SKILL.md yo'q). Plugin orqali o'rnatgan bo'lsangiz: /plugin marketplace update reels-montaj")
    url = f"https://github.com/{o.repo}/archive/refs/heads/{o.branch}.zip"
    print("yuklanmoqda:", url)
    data = urllib.request.urlopen(url, timeout=60).read()
    z = zipfile.ZipFile(io.BytesIO(data)); top = z.namelist()[0].split("/")[0]; prefix = f"{top}/{SUB}/"
    names = [n for n in z.namelist() if n.startswith(prefix) and not n.endswith("/")]
    if not any(n.endswith("/SKILL.md") for n in names): sys.exit("[xato] arxivda SKILL.md topilmadi — repo tuzilmasi o'zgargan")
    new_v = (z.read(prefix + "VERSION").decode().strip() if prefix + "VERSION" in z.namelist() else "noma'lum")
    old_v = version_of(dest); print(f"joriy: {old_v}  ->  yangi: {new_v}")
    if o.check: sys.exit(0)
    if old_v == new_v and new_v != "noma'lum": print("allaqachon eng yangi versiya."); sys.exit(0)
    bk = os.path.join(C.HOME, "backup"); os.makedirs(bk, exist_ok=True)
    bdir = os.path.join(bk, "reels-montaj-" + time.strftime("%Y%m%d-%H%M%S")); shutil.move(dest, bdir); print("eski nusxa saqlandi:", bdir)
    try:
        for n in names:
            t = os.path.join(dest, n[len(prefix):]); os.makedirs(os.path.dirname(t), exist_ok=True)
            with open(t, "wb") as f: f.write(z.read(n))
        if not re.match(r"---\nname: reels-montaj\n", open(os.path.join(dest, "SKILL.md"), encoding="utf-8").read()): raise RuntimeError("SKILL.md sarlavhasi noto'g'ri")
    except Exception as e:                                                      # xato bo'lsa eskisini qaytaramiz
        shutil.rmtree(dest, ignore_errors=True); shutil.move(bdir, dest); sys.exit(f"[xato] {e}; eski nusxa qaytarildi")
    print(f"tayyor: {dest} ({len(names)} fayl, versiya {new_v}). Claude Code'ni qayta ishga tushiring.")
