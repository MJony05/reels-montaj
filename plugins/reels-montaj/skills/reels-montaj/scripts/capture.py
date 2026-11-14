"""capture.py --layer fg|bg|back --start N --end M --out DIR  — motion qatlami kadrlarini shaffof PNG qilib chiqaradi.
fg   = matn + UI + vinyetka (hamma kadrlar)   bg = sahna foni (faqat sahna oynalarida)   back = odam orqasidagi hook matni
Loyiha papkasidan ishga tushiring (plan.json va ixtiyoriy scenes.html shu yerda)."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def build_page(plan):
    tpl = open(os.path.join(C.SKILL_DIR, "templates", "motion.html"), encoding="utf-8").read()
    frag = open("scenes.html", encoding="utf-8").read() if os.path.exists("scenes.html") else ""
    html = tpl.replace("<!--SCENES_FRAGMENT-->", frag).replace("/*PLAN_JSON*/null", json.dumps(plan, ensure_ascii=False))
    C.workdir(); path = os.path.abspath(os.path.join("work", "page.html"))
    open(path, "w", encoding="utf-8").write(html)
    return path


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--layer", required=True); a.add_argument("--start", type=int, required=True)
    a.add_argument("--end", type=int, required=True); a.add_argument("--out", required=True); a.add_argument("--plan", default="plan.json")
    o = a.parse_args()
    plan = C.load_plan(o.plan); page = build_page(plan); os.makedirs(o.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try: br = p.chromium.launch(channel="chrome")
        except Exception: br = p.chromium.launch()                  # Chrome yo'q bo'lsa playwright'ning chromium'i
        pg = br.new_page(viewport={"width": C.W, "height": C.H}, device_scale_factor=1)
        pg.goto("file:///" + page.replace("\\", "/").lstrip("/")); pg.evaluate(f"document.body.classList.add('L{o.layer}')")
        pg.wait_for_function("window.READY===true", timeout=90000)
        for n in range(o.start, o.end):
            pg.evaluate(f"renderFrame({n}/{plan['fps']})")
            pg.screenshot(path=os.path.join(o.out, f"ov_{n:04d}.png"), omit_background=True)
        br.close()
    print("tayyor", o.layer, o.start, o.end)
