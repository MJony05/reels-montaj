"""voice_sfx.py — 1) ovozni tozalash (de-clip, shovqin, EQ, de-ess, kompressor, limiter)  2) ozgina SFX  3) -14 LUFS -> work/audio_sfx.wav
SFX qoidasi: KAM va ma'noli. Masshtab (yaqin/uzoq) kesishlariga ovoz QO'YILMAYDI. Faqat:
  - karta-sahnaga kirishda 'vush'  (plan.sfx.whoosh_scenes, standart: true)
  - muhim lahzalarda past 'boom'   (plan.sfx.booms = [t, ...])      - UI obyekti chiqqanda yumshoq 'pop' (plan.sfx.pops = [t, ...])
  - sanagichda 'tik'                (plan.sfx.ticks = [[t0, t1, n], ...])"""
import os, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

SR = 48000; rng = np.random.default_rng(5)
CHAIN = ("adeclip,highpass=f=80,afftdn=nr=9:nf=-50:tn=1,equalizer=f=220:t=q:w=1.1:g=-2,equalizer=f=3200:t=q:w=1:g=2.2,"
         "deesser=i=0.35,acompressor=threshold=-21dB:ratio=3:attack=6:release=130:makeup=3,alimiter=limit=0.9:level=disabled,"
         "loudnorm=I=-15:TP=-1.5:LRA=7")


def whoosh(dur=0.5, amp=0.16):
    n = int(dur * SR); t = np.linspace(0, 1, n); noise = rng.standard_normal(n)
    a = 1 - np.exp(-2 * np.pi * (250 + 6000 * t ** 2) / SR); y = np.zeros(n); s = 0.0
    for i in range(n): s += a[i] * (noise[i] - s); y[i] = s
    y *= np.sin(np.pi * np.clip(t * 0.9 + 0.05, 0, 1)) ** 2 * (t ** 0.6)
    return (y / np.abs(y).max() * amp).astype(np.float32)


def boom(dur=0.5, amp=0.26):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(42 + 90 * np.exp(-t * 22)) / SR) * np.exp(-t * 8) + np.sin(2 * np.pi * 170 * t) * np.exp(-t * 26) * 0.5
    y[:int(.002 * SR)] *= np.linspace(0, 1, int(.002 * SR)); return (y / np.abs(y).max() * amp).astype(np.float32)


def pop(dur=0.13, amp=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(520 * np.exp(-t * 14) + 260) / SR) * np.exp(-t * 34); y[:int(.002 * SR)] *= np.linspace(0, 1, int(.002 * SR))
    return (y * amp).astype(np.float32)


def tick(dur=0.04, amp=0.08):
    n = int(dur * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 120) * amp).astype(np.float32)


if __name__ == "__main__":
    plan = C.load_plan(); sfx = plan.get("sfx", {}); work = C.workdir()
    ff = C.ffmpeg(); clean = os.path.join(work, "voice_clean.wav")
    chain = CHAIN if plan.get("audio", {}).get("clean", True) else "loudnorm=I=-15:TP=-1.5:LRA=7"
    subprocess.run([ff, "-v", "error", "-y", "-i", plan["source"], "-vn", "-af", chain, "-ar", str(SR), "-ac", "2", clean], check=True)
    ev = []
    if sfx.get("whoosh_scenes", True): ev += [(s["s"] - 0.30, "wh") for s in plan["scenes"]]
    ev += [(t, "bm") for t in sfx.get("booms", [])] + [(t, "pp") for t in sfx.get("pops", [])]
    for t0, t1, n in sfx.get("ticks", []): ev += [(t0 + (t1 - t0) * i / n, "tk") for i in range(1, n + 1)]
    snd = {"wh": whoosh(), "bm": boom(), "pp": pop(), "tk": tick()}
    w = wave.open(clean); ch = w.getnchannels()
    v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, ch) / 32768
    mix_s = np.zeros(len(v), np.float32)
    for t, k in ev:
        i = max(0, int(t * SR)); s = snd[k]; seg = s[:max(0, len(mix_s) - i)]; mix_s[i:i + len(seg)] += seg
    mix = np.clip(v + mix_s[:, None] * float(sfx.get("gain", 1.0)), -1, 1)
    fo = int(0.4 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    pre = os.path.join(work, "_pre.wav"); o = wave.open(pre, "wb"); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((mix * 32767).astype(np.int16).tobytes()); o.close()
    subprocess.run([ff, "-v", "error", "-y", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR), os.path.join(work, "audio_sfx.wav")], check=True)
    print(f"ovoz tayyor: {len(ev)} SFX hodisa -> work/audio_sfx.wav")
