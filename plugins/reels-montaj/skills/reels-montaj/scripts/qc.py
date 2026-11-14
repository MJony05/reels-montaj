"""qc.py final.mp4 [--plan plan.json] — o'lcham, davomiylik, kadrlar soni, video/ovoz sinxroni, balandlik; 14 ta kalit kadr -> work/qc_sheet.jpg"""
import argparse, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--plan", default="plan.json"); o = ap.parse_args()
    ff, fp = C.ffmpeg(), C.ffprobe()
    dur, w, h, fps, _ = C.probe(o.video)
    fr = subprocess.run([fp, "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", o.video], capture_output=True, text=True).stdout.strip()
    a_d = subprocess.run([fp, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0", o.video], capture_output=True, text=True).stdout.strip()
    e = subprocess.run([ff, "-hide_banner", "-i", o.video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = [l for l in e.splitlines() if l.strip().startswith("I:")][-1].split()[1]; pk = [l for l in e.splitlines() if l.strip().startswith("Peak:")]
    exp = None
    if os.path.exists(o.plan):
        try: exp = C.load_plan(o.plan)["nframes"]
        except Exception: pass
    print(f"o'lcham {w}x{h} {'OK' if (w, h) == (1080, 1920) else '<- 1080x1920 EMAS'} | {dur:.2f}s | kadrlar {fr}" + (f" (kutilgan {exp}) {'OK' if str(exp) == fr else '<- FARQ: kadr yo`qolgan!'}" if exp else ""))
    print(f"ovoz {a_d}s (video {dur:.2f}s) | balandlik {I} LUFS (maqsad -14) | true peak {pk[-1].split()[1] if pk else '?'} dBTP")
    C.workdir(); n = 14; ts = [dur * (i + 0.5) / n for i in range(n)]
    for i, t in enumerate(ts): subprocess.run([ff, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", o.video, "-frames:v", "1", "-vf", "scale=240:-1", os.path.join("work", f"_qc{i:02d}.png")])
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "1", "-i", os.path.join("work", "_qc%02d.png"), "-vf", "tile=7x2", "-frames:v", "1", os.path.join("work", "qc_sheet.jpg")])
    print("kalit kadrlar: work/qc_sheet.jpg  <- OCHIB KO'RING: matn yuzga tegmaydimi, o'qiladimi, qora/qotgan kadr yo'qmi")
