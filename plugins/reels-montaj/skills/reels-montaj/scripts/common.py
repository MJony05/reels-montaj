"""common.py — hamma skriptlar uchun umumiy yordamchilar (Mac / Windows / Linux)."""
import glob, json, os, platform, shutil, subprocess, sys

HOME = os.environ.get("REELS_HOME") or os.path.join(os.path.expanduser("~"), ".reels-montaj")
SYSTEM = platform.system()          # Darwin | Windows | Linux
IS_MAC_ARM = SYSTEM == "Darwin" and platform.machine() == "arm64"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920


def venv_python():
    """setup.py yaratgan alohida Python muhiti (Homebrew Python global pip ni bloklaydi)."""
    p = os.path.join(HOME, "venv", "Scripts" if SYSTEM == "Windows" else "bin", "python.exe" if SYSTEM == "Windows" else "python")
    return p if os.path.exists(p) else sys.executable


def find_tool(name):
    """ffmpeg / ffprobe ni topadi: REELS_<NAME> env, PATH, keyin odatiy joylar."""
    env = os.environ.get("REELS_" + name.upper())
    if env and os.path.exists(env): return env
    w = shutil.which(name)
    if w: return w
    cands = []
    if SYSTEM == "Windows":
        la = os.environ.get("LOCALAPPDATA", "")
        cands += glob.glob(os.path.join(la, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "ffmpeg-*", "bin", name + ".exe"))
        cands += glob.glob(os.path.join(la, "Microsoft", "WinGet", "Links", name + ".exe")) + [r"C:\ffmpeg\bin\%s.exe" % name]
    else:
        cands += ["/opt/homebrew/bin/" + name, "/usr/local/bin/" + name, "/usr/bin/" + name]
    for c in cands:
        if os.path.exists(c): return c
    return None


def need(name):
    p = find_tool(name)
    if not p:
        sys.exit(f"[xato] {name} topilmadi. Avval o'rnating:  python setup.py --install")
    return p


def ffmpeg(): return need("ffmpeg")
def ffprobe(): return need("ffprobe")


def probe(path):
    """(davomiylik, kenglik, balandlik, fps, audio bormi)"""
    js = json.loads(subprocess.run([ffprobe(), "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                                    "-of", "json", path], capture_output=True, text=True).stdout)
    v = next(s for s in js["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return float(js["format"]["duration"]), int(v["width"]), int(v["height"]), float(n) / float(d), any(s["codec_type"] == "audio" for s in js["streams"])


def load_plan(path="plan.json"):
    if not os.path.exists(path): sys.exit(f"[xato] {path} topilmadi (loyiha papkasida bo'lishi kerak)")
    plan = json.load(open(path, encoding="utf-8"))
    plan.setdefault("fps", 30)
    plan.setdefault("anchor", [540, 600])
    plan.setdefault("shots", [[0, 1.0]])
    plan.setdefault("scenes", [])
    plan.setdefault("phrases", [])
    plan.setdefault("hook", {"frames": 0})
    plan.setdefault("grade", {"contrast": 1.07, "brightness": 5, "vignette": 0.22})
    plan.setdefault("card", {"x": 90, "y": 140, "w": 900, "h": 570, "r": 52, "face": [540, 650, 964]})
    plan.setdefault("palette", {})
    plan.setdefault("sfx", {})
    plan.setdefault("text", {"bottom": 330, "cap_bottom": 300, "fit_width": 880})
    plan["nframes"] = int(plan["duration"] * plan["fps"] + 1e-6)          # oxirgi to'liq bo'lmagan kadr tushiriladi (manba kadrlari soniga mos)
    return plan


def workdir(sub=""):
    d = os.path.join("work", sub) if sub else "work"
    os.makedirs(d, exist_ok=True)
    return d


def decode_filter(fps):
    """istalgan manba -> 1080x1920 (cover), fps"""
    return f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"


def models_dir():
    d = os.path.join(HOME, "models"); os.makedirs(d, exist_ok=True); return d
