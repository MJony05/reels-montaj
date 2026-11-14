"""segment.py [--frames N] [--reset t1,t2] — RVM bilan odam maskasi -> work/mask/m_%04d.png (540x960).
Faqat 'odam orqasida matn' (plan.hook) uchun kerak, shuning uchun odatda dastlabki 60-90 kadr yetarli (CPU'da ~4 kadr/s).
Model: setup.py --models rvm"""
import argparse, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import cv2, numpy as np, onnxruntime as ort

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--plan", default="plan.json"); a.add_argument("--frames", type=int, default=0)
    a.add_argument("--reset", default=""); o = a.parse_args()
    plan = C.load_plan(o.plan); fps = plan["fps"]; N = o.frames or plan["hook"].get("frames", 0) or plan["nframes"]
    model = os.path.join(C.models_dir(), "rvm_mobilenetv3_fp32.onnx")
    if not os.path.exists(model): sys.exit("[xato] RVM modeli yo'q: python setup.py --models rvm")
    reset_at = {round(float(t) * fps) for t in o.reset.split(",") if t}
    out = C.workdir("mask"); w_, h_ = 720, 1280
    so = ort.SessionOptions(); so.intra_op_num_threads = max(2, (os.cpu_count() or 4) - 1)
    prov = [p for p in ("CoreMLExecutionProvider", "CPUExecutionProvider") if p in ort.get_available_providers()][-1:]   # xavfsiz: CPU
    sess = ort.InferenceSession(model, so, providers=prov)
    z = lambda: np.zeros((1, 1, 1, 1), np.float32); rec = [z() for _ in range(4)]; dr = np.array([0.375], np.float32)
    dec = subprocess.Popen([C.ffmpeg(), "-v", "error", "-i", plan["source"], "-vf", C.decode_filter(fps) + f",scale={w_}:{h_}", "-frames:v", str(N), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n, t0, FB = 0, time.time(), w_ * h_ * 3
    while True:
        buf = dec.stdout.read(FB)
        if len(buf) < FB: break
        if n in reset_at: rec = [z() for _ in range(4)]
        src = (np.frombuffer(buf, np.uint8).reshape(h_, w_, 3).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        fgr, pha, *rec = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dr})
        m = cv2.resize(pha[0, 0], (540, 960), interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(out, f"m_{n:04d}.png"), np.clip(m * 255, 0, 255).astype(np.uint8)); n += 1
    dec.wait(); print(f"maska: {n} kadr, {time.time() - t0:.0f}s -> {out}")
