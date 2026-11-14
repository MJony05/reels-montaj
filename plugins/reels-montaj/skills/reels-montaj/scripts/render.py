"""render.py [--plan plan.json] [--workers 3] [--chunks 5] [--crf 16] [--draft]
To'liq render: motion kadrlari (parallel) -> [hook maskasi] -> ovoz+SFX -> kompozit (bo'laklarga bo'lib PARALLEL) -> birlashtirish -> out/final.mp4 + final_light.mp4 -> qc.
--draft: tez qoralama (past sifat crf 28) — dizaynni tekshirish uchun.   Loyiha papkasidan ishga tushiring."""
import argparse, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

S = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable


def run_parallel(cmds, label):
    t0 = time.time(); ps = [subprocess.Popen(c) for c in cmds]
    bad = [c for c, p in zip(cmds, ps) if p.wait() != 0]
    if bad: sys.exit(f"[xato] {label}: {len(bad)} jarayon xato bilan tugadi (yuqoridagi xabarga qarang)")
    print(f"  {label}: {time.time() - t0:.0f}s", flush=True)


def split(a, b, k):
    step = -(-(b - a) // k); return [(i, min(i + step, b)) for i in range(a, b, step)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", default="plan.json"); ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--chunks", type=int, default=0); ap.add_argument("--crf", default="16"); ap.add_argument("--draft", action="store_true"); o = ap.parse_args()
    P = C.load_plan(o.plan); N = P["nframes"]; fps = P["fps"]; T = time.time()
    crf = "28" if o.draft else o.crf; cpu = os.cpu_count() or 4
    chunks = o.chunks or max(2, min(5, cpu // 2))
    for d in ("ov", "bg", "ovb"): C.workdir(d)
    cap = lambda layer, a, b, out: [PY, os.path.join(S, "capture.py"), "--layer", layer, "--start", str(a), "--end", str(b), "--out", out, "--plan", o.plan]
    print(f"render: {N} kadr, {chunks} bo'lak, crf {crf}")
    # 1) motion qatlamlari
    jobs = [cap("fg", a, b, os.path.join("work", "ov")) for a, b in split(0, N, o.workers)]
    for s in P["scenes"]:                                                     # sahna foni faqat sahna oynalarida
        a, b = max(0, int((s["s"] - 0.7) * fps)), min(N, int((s["e"] + 0.7) * fps) + 1); jobs.append(cap("bg", a, b, os.path.join("work", "bg")))
    hn = P["hook"].get("frames", 0)
    if hn: jobs.append(cap("back", 0, hn, os.path.join("work", "ovb")))
    run_parallel(jobs, "motion kadrlari")
    # 2) hook maskasi
    if hn and not os.path.exists(os.path.join("work", "mask", f"m_{hn - 1:04d}.png")):
        run_parallel([[PY, os.path.join(S, "segment.py"), "--plan", o.plan]], "odam maskasi")
    # 3) ovoz
    run_parallel([[PY, os.path.join(S, "voice_sfx.py")]], "ovoz + SFX")
    # 4) kompozit (parallel bo'laklar, faqat video)
    os.makedirs("out", exist_ok=True); cdir = C.workdir("chunks"); lst = []
    jobs = []
    for i, (a, b) in enumerate(split(0, N, chunks)):
        f = os.path.join(cdir, f"c{i}.mp4"); lst.append(os.path.basename(f))
        jobs.append([PY, os.path.join(S, "compose.py"), "--plan", o.plan, "--f0", str(a), "--f1", str(b), "--out", f, "--crf", crf, "--video-only"])
    run_parallel(jobs, "kompozit")
    open(os.path.join(cdir, "list.txt"), "w").write("".join(f"file '{n}'\n" for n in lst))
    ff = C.ffmpeg(); allv = os.path.join(cdir, "all_v.mp4")
    subprocess.run([ff, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(cdir, "list.txt"), "-c", "copy", allv], check=True)
    # DIQQAT: -shortest ISHLATMANG — u oxirgi kadrlarni qirqib tashlaydi
    final = os.path.join("out", "final.mp4")
    subprocess.run([ff, "-v", "error", "-y", "-i", allv, "-i", os.path.join("work", "audio_sfx.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", final, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", os.path.join("out", "final_light.mp4")], check=True)
    print(f"tayyor: out/final.mp4, out/final_light.mp4  (jami {time.time() - T:.0f}s)")
    subprocess.run([PY, os.path.join(S, "qc.py"), os.path.join("out", "final.mp4"), "--plan", o.plan])
