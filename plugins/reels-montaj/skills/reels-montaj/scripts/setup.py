"""setup.py — kerakli dasturlarni tekshiradi va (so'ralsa) o'rnatadi.

  python setup.py --check              holatni ko'rsatadi (hech narsa o'zgarmaydi)
  python setup.py --install            yetishmayotgan dasturlarni o'rnatadi (ffmpeg + alohida Python muhiti + paketlar)
  python setup.py --models rvm         odamni kesish modelini (~15 MB) yuklaydi
  python setup.py --print-python       skriptlar ishlatadigan Python yo'lini chiqaradi

DIQQAT: --install / --models foydalanuvchi roziligidan KEYIN ishga tushiriladi (Claude avval so'raydi).
"""
import argparse, os, shutil, subprocess, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

PKGS = ["numpy", "opencv-python", "pillow", "playwright", "onnxruntime", "faster-whisper"]
MLX = ["mlx-whisper"]                                     # faqat Apple Silicon: nutqni ancha tezroq taniydi
RVM_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
RVM_NAME = "rvm_mobilenetv3_fp32.onnx"


def chrome_path():
    cands = {"Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
             "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
             "Linux": ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"]}[C.SYSTEM if C.SYSTEM in ("Darwin", "Windows") else "Linux"]
    return next((p for p in cands if os.path.exists(p)), None)


def has_module(mod):
    py = C.venv_python()
    return subprocess.run([py, "-c", f"import {mod}"], capture_output=True).returncode == 0


def status():
    rows = []
    rows.append(("ffmpeg", bool(C.find_tool("ffmpeg")), C.find_tool("ffmpeg") or hint_ffmpeg()))
    rows.append(("ffprobe", bool(C.find_tool("ffprobe")), C.find_tool("ffprobe") or ""))
    venv = os.path.exists(os.path.join(C.HOME, "venv"))
    rows.append(("Python muhiti", venv, os.path.join(C.HOME, "venv") if venv else "yo'q (--install yaratadi)"))
    for mod, pkg in (("numpy", "numpy"), ("cv2", "opencv-python"), ("PIL", "pillow"), ("playwright", "playwright"), ("onnxruntime", "onnxruntime"), ("faster_whisper", "faster-whisper")):
        rows.append((pkg, venv and has_module(mod), ""))
    if C.IS_MAC_ARM: rows.append(("mlx-whisper (tez Whisper, ixtiyoriy)", venv and has_module("mlx_whisper"), "Apple Silicon"))
    rows.append(("Google Chrome", bool(chrome_path()), chrome_path() or "yo'q -> playwright chromium yuklanadi (~150 MB)"))
    rvm = os.path.join(C.models_dir(), RVM_NAME)
    rows.append(("odamni kesish modeli (RVM)", os.path.exists(rvm), rvm if os.path.exists(rvm) else "yo'q (faqat 'odam orqasida matn' uchun kerak)"))
    free = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    rows.append((f"bo'sh joy (uy papkasi)", free > 6, f"{free:.1f} GB"))
    print(f"Tizim: {C.SYSTEM} {'(Apple Silicon)' if C.IS_MAC_ARM else ''} | REELS_HOME={C.HOME}")
    for name, ok, info in rows: print(f"  [{'OK' if ok else '--'}] {name:38s} {info}")
    return all(ok for n, ok, i in rows if "ixtiyoriy" not in n and "RVM" not in n and "Chrome" not in n)


def hint_ffmpeg():
    return {"Darwin": "yo'q -> brew install ffmpeg", "Windows": "yo'q -> winget install --id Gyan.FFmpeg -e", "Linux": "yo'q -> sudo apt install ffmpeg"}[C.SYSTEM]


def install_ffmpeg():
    if C.find_tool("ffmpeg") and C.find_tool("ffprobe"): return
    if C.SYSTEM == "Darwin":
        if not shutil.which("brew"):
            sys.exit("[to'xtadi] Homebrew yo'q. Avval https://brew.sh dagi buyruqni Terminal'da ishga tushiring, keyin shu buyruqni qayta yuriting.")
        cmd = ["brew", "install", "ffmpeg"]
    elif C.SYSTEM == "Windows":
        cmd = ["winget", "install", "--id", "Gyan.FFmpeg", "-e", "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"]
    else:
        cmd = ["sudo", "apt-get", "install", "-y", "ffmpeg"]
    print("->", " ".join(cmd)); subprocess.run(cmd, check=False)
    if not C.find_tool("ffmpeg"): print("[ogohlantirish] ffmpeg o'rnatildi, lekin yangi terminal ochish kerak bo'lishi mumkin (PATH yangilanishi uchun).")


def pick_python():
    """Python 3.10+ kerak. Yangi Mac'dagi tizim Python'i eski (3.9) bo'lishi mumkin."""
    if sys.version_info >= (3, 10): return sys.executable
    for n in ("python3.13", "python3.12", "python3.11", "python3.10"):
        p = shutil.which(n)
        if p: return p
    sys.exit("[to'xtadi] Python 3.10+ kerak (hozir %s). Mac: `brew install python@3.12`, keyin `python3.12 setup.py --install`" % sys.version.split()[0])


def install_python_env(mlx):
    venv = os.path.join(C.HOME, "venv")
    if not os.path.exists(venv):
        print("-> alohida Python muhiti:", venv); subprocess.run([pick_python(), "-m", "venv", venv], check=True)
    py = C.venv_python(); pk = PKGS + (MLX if mlx else [])
    print("-> paketlar:", " ".join(pk))
    subprocess.run([py, "-m", "pip", "install", "--no-cache-dir", "-q", "--upgrade", "pip"], check=False)
    subprocess.run([py, "-m", "pip", "install", "--no-cache-dir", "-q"] + pk, check=True)
    if not chrome_path():
        print("-> Chrome yo'q: playwright chromium yuklanadi"); subprocess.run([py, "-m", "playwright", "install", "chromium"], check=True)


def get_model(name):
    if name != "rvm": sys.exit("faqat 'rvm' qo'llab-quvvatlanadi (Whisper modeli birinchi transkripsiyada o'zi yuklanadi)")
    dst = os.path.join(C.models_dir(), RVM_NAME)
    if os.path.exists(dst) and os.path.getsize(dst) > 10e6: print("allaqachon bor:", dst); return
    print("-> yuklanmoqda:", RVM_URL); urllib.request.urlretrieve(RVM_URL, dst + ".part")
    if os.path.getsize(dst + ".part") < 10e6: sys.exit("[xato] fayl kutilgandan kichik, qayta urinib ko'ring")
    os.replace(dst + ".part", dst); print("tayyor:", dst, f"({os.path.getsize(dst) / 1e6:.1f} MB)")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--check", action="store_true"); a.add_argument("--install", action="store_true")
    a.add_argument("--models"); a.add_argument("--print-python", action="store_true"); a.add_argument("--no-mlx", action="store_true")
    o = a.parse_args()
    if o.print_python: print(C.venv_python()); sys.exit(0)
    if o.install:
        install_ffmpeg(); install_python_env(C.IS_MAC_ARM and not o.no_mlx)
    if o.models: get_model(o.models)
    ok = status() if (o.check or o.install or not o.models) else True
    sys.exit(0 if ok else 1)
