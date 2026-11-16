"""preview.py --times 1.0,6.5,12.3,... [--plan plan.json]
Tanlangan lahzalarning TO'LIQ kompozit kadrlarini (karta-morph, sahna, matn, hook) tez chiqaradi -> work/preview.jpg.
To'liq renderdan oldin dizaynni tekshirish uchun (1 kadr ~ 3-5 s). Loyiha papkasidan ishga tushiring."""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from capture import build_page

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--times", required=True); ap.add_argument("--plan", default="plan.json"); ap.add_argument("--cols", type=int, default=7)
    o = ap.parse_args(); plan = C.load_plan(o.plan); fps = plan["fps"]
    times = [float(x) for x in o.times.split(",")]; frames = [min(int(round(t * fps)), plan["nframes"] - 1) for t in times]
    hook = plan["hook"].get("frames", 0)
    for d in ("ov", "bg", "ovb", "mask", "preview"): C.workdir(d)
    page = build_page(plan)
    in_scene = lambda t: any(s["s"] - 0.7 <= t <= s["e"] + 0.7 for s in plan["scenes"])
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try: br = p.chromium.launch(channel="chrome")
        except Exception: br = p.chromium.launch()
        pages = {}
        def get(layer):
            if layer not in pages:
                pg = br.new_page(viewport={"width": C.W, "height": C.H}, device_scale_factor=1)
                pg.goto("file:///" + page.replace("\\", "/").lstrip("/")); pg.evaluate(f"document.body.classList.add('L{layer}')")
                pg.wait_for_function("window.READY===true", timeout=90000); pages[layer] = pg
            return pages[layer]
        for n in frames:
            t = n / fps; jobs = [("fg", "ov")] + ([("bg", "bg")] if in_scene(t) else []) + ([("back", "ovb")] if n < hook else [])
            for layer, d in jobs:
                pg = get(layer); pg.evaluate(f"renderFrame({n}/{fps})"); pg.screenshot(path=os.path.join("work", d, f"ov_{n:04d}.png"), omit_background=True)
        br.close()
    if any(n < hook for n in frames) and not os.path.exists(os.path.join("work", "mask", f"m_{hook - 1:04d}.png")):
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "segment.py"), "--plan", o.plan], check=True)
    S = os.path.dirname(os.path.abspath(__file__)); ff = C.ffmpeg(); ps = []
    for n in frames:
        out = os.path.join("work", "preview", f"p_{n:04d}.mp4")
        ps.append(subprocess.Popen([sys.executable, os.path.join(S, "compose.py"), "--plan", o.plan, "--f0", str(n), "--f1", str(n + 1), "--out", out, "--crf", "20", "--video-only"], stdout=subprocess.DEVNULL))
        if len(ps) >= 4: [q.wait() for q in ps]; ps = []
    [q.wait() for q in ps]
    for i, n in enumerate(frames):
        subprocess.run([ff, "-v", "error", "-y", "-i", os.path.join("work", "preview", f"p_{n:04d}.mp4"), "-frames:v", "1", "-vf", "scale=270:-1", os.path.join("work", "preview", f"s_{i:02d}.png")])
    rows = -(-len(frames) // o.cols)
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "1", "-i", os.path.join("work", "preview", "s_%02d.png"), "-vf", f"tile={o.cols}x{rows}", "-frames:v", "1", os.path.join("work", "preview.jpg")])
    print("tayyor: work/preview.jpg  (kadrlar:", ", ".join(f"{t:g}s" for t in times), ")")
