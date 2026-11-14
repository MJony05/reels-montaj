"""probe.py video — davomiylik, o'lcham, fps; kesish joylari (sahna o'zgarishi); pauzalar; ovoz balandligi; 1 kadr/s kontakt jadval -> work/sheet_*.jpg"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

if __name__ == "__main__":
    v = sys.argv[1]; dur, w, h, fps, has_a = C.probe(v)
    print(f"{os.path.basename(v)}: {dur:.2f}s  {w}x{h}  {fps:.2f}fps  audio={'bor' if has_a else 'YOQ'}  {'vertikal' if h > w else 'GORIZONTAL (cover bilan kesiladi)'}")
    ff = C.ffmpeg()
    sc = subprocess.run([ff, "-v", "info", "-i", v, "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", sc)]
    print("kesish joylari (sahna o'zgarishi):", [round(c, 2) for c in cuts] or "yo'q -> bitta uzluksiz kadr (masshtab ritmi bilan jonlantiring)")
    if has_a:
        e = subprocess.run([ff, "-hide_banner", "-i", v, "-af", "silencedetect=noise=-38dB:d=0.25,ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        pa = re.findall(r"silence_start: ([0-9.]+)", e); du = re.findall(r"silence_duration: ([0-9.]+)", e)
        print("pauzalar (>=0.25s):", [f"{float(a):.2f}(+{float(b):.2f})" for a, b in zip(pa, du)] or "yo'q")
        li = [l for l in e.splitlines() if l.strip().startswith(("I:", "Peak:"))]
        print("ovoz:", " | ".join(" ".join(l.split()) for l in li[-2:]))
    C.workdir(); out = os.path.join("work", "sheet.jpg")
    cols = 10; rows = max(1, min(6, int(dur) // cols + 1))
    subprocess.run([ff, "-v", "error", "-y", "-i", v, "-vf", f"fps=1,scale=180:-1,tile={cols}x{rows}", "-frames:v", "1", out])
    print("kontakt jadval:", out, "(OCHIB ko'ring: kadrlash, yorug'lik, qayerda yuz/qo'l)")
