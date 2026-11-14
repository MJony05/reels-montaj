"""compose.py --f0 A --f1 B --out chunk.mp4 [--crf 16] [--video-only]
Manba video + masshtab ritmi (plan.shots) + grade + hook (odam orqasida matn) + KARTA-MORPH (plan.scenes) + motion qatlami (work/ov, work/bg).
Kadr oralig'i [f0, f1) — render.py shu skriptni bir necha bo'lakka bo'lib parallel yurgizadi."""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import cv2, numpy as np

W, H = C.W, C.H


def ease(x): x = min(1, max(0, x)); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def over(f, png):
    ov = cv2.imread(png, cv2.IMREAD_UNCHANGED)
    if ov is None: return f
    if ov.shape[2] == 3: ov = np.dstack([ov, np.full((H, W), 255, np.uint8)])          # to'liq yopiq kadr: alfa kanali yo'q
    al = ov[..., 3:4].astype(np.float32) / 255.0
    return f * (1 - al) + ov[..., :3].astype(np.float32) * al


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", default="plan.json"); ap.add_argument("--f0", type=int, required=True)
    ap.add_argument("--f1", type=int, required=True); ap.add_argument("--out", required=True); ap.add_argument("--crf", default="16")
    ap.add_argument("--video-only", action="store_true"); o = ap.parse_args()
    P = C.load_plan(o.plan); FPS = P["fps"]; DUR = P["duration"]; AX, AY = P["anchor"]
    SHOTS = [tuple(s) for s in P["shots"]]; SC = [(s["s"], s["e"]) for s in P["scenes"]]
    cx_, cy_, cw_, ch_, cr_ = [P["card"][k] for k in ("x", "y", "w", "h", "r")]; FACE = P["card"]["face"]; HOOKN = P["hook"].get("frames", 0)
    G = P["grade"]; FADE = P.get("fade_out", 0.4)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1 - G["vignette"] * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.42) / (H / 2)) ** 2), 0.6, 1)[..., None]

    def prog(t):
        for s, e in SC:
            a, b, c, d = s - .20, s + .35, e - .40, e + .15
            if a <= t < b: return ease((t - a) / (b - a))
            if b <= t < c: return 1.0
            if c <= t <= d: return 1 - ease((t - c) / (d - c))
        return 0.0

    def grade(img, sharp):
        if sharp: img = np.clip(img + 0.5 * (img - cv2.GaussianBlur(img, (0, 0), 1.6)), 0, 255)
        return (img - 128) * G["contrast"] + 128 + G["brightness"]

    def rrect(cx, cy, rw, rh, r):
        x0, x1 = max(0, int(cx - rw / 2) - 3), min(W, int(cx + rw / 2) + 4); y0, y1 = max(0, int(cy - rh / 2) - 3), min(H, int(cy + rh / 2) + 4)
        m = np.zeros((H, W), np.float32)
        if x1 <= x0 or y1 <= y0: return m
        px, py = xx[y0:y1, x0:x1], yy[y0:y1, x0:x1]
        qx, qy = np.abs(px - cx) - (rw / 2 - r), np.abs(py - cy) - (rh / 2 - r)
        m[y0:y1, x0:x1] = np.clip(0.5 - (np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r), 0, 1)
        return m

    NF = o.f1 - o.f0; ff = C.ffmpeg(); t0 = o.f0 / FPS
    dec = subprocess.Popen([ff, "-v", "error", "-ss", f"{t0:.4f}", "-i", P["source"], "-frames:v", str(NF), "-vf", C.decode_filter(FPS), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    base = [ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    venc = ["-c:v", "libx264", "-preset", "medium", "-crf", o.crf, "-pix_fmt", "yuv420p"]
    if o.video_only: cmd = base + venc + [o.out]
    else: cmd = base + ["-ss", f"{t0:.4f}", "-i", os.path.join("work", "audio_sfx.wav"), "-map", "0:v", "-map", "1:a"] + venc + ["-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", o.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    k_, FB = 0, W * H * 3
    while True:
        buf = dec.stdout.read(FB)
        if len(buf) < FB: break
        n = o.f0 + k_; k_ += 1; t = n / FPS
        fr0 = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        i = max(j for j in range(len(SHOTS)) if SHOTS[j][0] <= t); a, bz = SHOTS[i]
        b = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
        z = bz + 0.045 * min(1, (t - a) / max(1.0, b - a))                      # sekin yaqinlashish
        if a > 0: z += 0.05 * max(0.0, 1 - (t - a) / 0.22) ** 2                 # kesish 'punch'
        p = prog(t)
        if p < 0.001:                                                            # ---- to'liq ekran ----
            fr = cv2.warpAffine(fr0, np.float32([[z, 0, (1 - z) * AX], [0, z, (1 - z) * AY]]), (W, H), flags=cv2.INTER_CUBIC) if z > 1.0005 else fr0
            g = grade(fr.astype(np.float32), z > 1.1) * vig; f = g
            if n < HOOKN:                                                        # hook: katta matn odam ORQASIDA
                ob = cv2.imread(os.path.join("work", "ovb", f"ov_{n:04d}.png"), cv2.IMREAD_UNCHANGED); mh = cv2.imread(os.path.join("work", "mask", f"m_{n:04d}.png"), cv2.IMREAD_GRAYSCALE)
                if ob is not None and ob.shape[2] == 4 and ob[..., 3].max() > 0 and mh is not None:
                    mh = np.clip((mh.astype(np.float32) / 255 - 0.06) * 1.12, 0, 1)
                    if z > 1.0005: mh = cv2.warpAffine(mh, np.float32([[z, 0, (1 - z) * AX / 2], [0, z, (1 - z) * AY / 2]]), (540, 960), flags=cv2.INTER_LINEAR)
                    m = cv2.resize(mh, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]; ab = ob[..., 3:4].astype(np.float32) / 255.0
                    f = (g * (1 - ab) + ob[..., :3].astype(np.float32) * ab) * (1 - m) + g * m
        else:                                                                    # ---- karta-morph ----
            bg = cv2.imread(os.path.join("work", "bg", f"ov_{n:04d}.png"), cv2.IMREAD_UNCHANGED)
            M0 = np.float32([[z, 0, (1 - z) * AX], [0, z, (1 - z) * AY]])
            canvas = bg[..., :3].astype(np.float32) if bg is not None else grade(cv2.warpAffine(fr0, M0, (W, H)).astype(np.float32), False)
            wx, wy, ww = AX - AX / z + W / (2 * z), AY - AY / z + H / (2 * z), W / z       # to'liq ekrandagi ko'rinadigan oyna markazi/kengligi
            L = lambda u, v: u + (v - u) * p
            rw_, rh_ = L(W, cw_), L(H, ch_); rcx = L(W / 2, cx_ + cw_ / 2); rcy = L(H / 2, cy_ + ch_ / 2) + (np.sin(t * 2.2) * 4 if p > .99 else 0); rad = cr_ * p
            win_w = L(ww, FACE[2]); win_h = win_w * rh_ / rw_; win_cx = L(wx, FACE[0]); win_cy = L(wy, FACE[1]); sx = rw_ / win_w
            Mt = np.float32([[sx, 0, rcx - rw_ / 2 - (win_cx - win_w / 2) * sx], [0, sx, rcy - rh_ / 2 - (win_cy - win_h / 2) * sx]])
            warped = grade(cv2.warpAffine(fr0, Mt, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32), sx > 1.1)
            mk = rrect(rcx, rcy, rw_, rh_, rad)[..., None]
            if p < 0.995:
                kx = int(1 + 28 * (1 - abs(2 * p - 1)) ** 2) | 1
                if kx > 3: warped = cv2.GaussianBlur(warped, (kx, 1), 0)             # morph paytida harakat xiraligi
            sh = cv2.GaussianBlur(rrect(rcx, rcy + 26, rw_, rh_, rad), (0, 0), 34)[..., None] * 0.42 * min(1.0, p * 3)
            f = (canvas * (1 - sh)) * (1 - mk) + warped * mk
        f = over(f, os.path.join("work", "ov", f"ov_{n:04d}.png"))
        if t > DUR - FADE: f = f * max(0.0, (DUR - t) / FADE)
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait(); print("kadr", k_, "->", o.out)
