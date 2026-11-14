"""transcribe.py video [--lang uz] [--model large-v3] [--prompt "lug'at"] [--backend auto|mlx|faster] [--out words.json]
Nutqni so'z vaqtlari bilan matnga o'tkazadi. Apple Silicon'da mlx-whisper (tez), boshqalarda faster-whisper.

Eslatma: o'zbekchani Whisper yomon taniydi. Natijani TO'G'RI matn deb hisoblama — kamida 2 xil sozlama bilan solishtir
(--lang uz, --prompt bilan, --lang tr/ru), keyin matnni o'zing tuzat va raqam/ism/da'volarni foydalanuvchiga tasdiqlat."""
import argparse, json, os, subprocess, sys, tempfile, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np


def load_audio(video):
    wav = os.path.join(tempfile.gettempdir(), "reels_voice16k.wav")
    subprocess.run([C.ffmpeg(), "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    w = wave.open(wav); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a                                                    # numpy massiv (faster-whisper'ning av xatosini chetlab o'tadi)


def run_faster(a, o):
    from faster_whisper import WhisperModel
    m = WhisperModel(o.model, device="cpu", compute_type="int8")
    kw = dict(language=None if o.lang == "auto" else o.lang, word_timestamps=True, condition_on_previous_text=False, beam_size=5, vad_filter=False)
    if o.prompt: kw["initial_prompt"] = o.prompt
    segs, info = m.transcribe(a, **kw)
    return [{"s": s.start, "e": s.end, "t": s.text, "w": [{"w": x.word, "s": x.start, "e": x.end} for x in s.words]} for s in segs], info.language


def run_mlx(a, o):
    import mlx_whisper
    repo = "mlx-community/whisper-large-v3-mlx" if o.model == "large-v3" else (o.model if "/" in o.model else f"mlx-community/whisper-{o.model}-mlx")
    kw = dict(path_or_hf_repo=repo, word_timestamps=True, condition_on_previous_text=False)
    if o.lang != "auto": kw["language"] = o.lang
    if o.prompt: kw["initial_prompt"] = o.prompt
    r = mlx_whisper.transcribe(a, **kw)
    return [{"s": s["start"], "e": s["end"], "t": s["text"], "w": [{"w": x["word"], "s": x["start"], "e": x["end"]} for x in s.get("words", [])]} for s in r["segments"]], r.get("language", o.lang)


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("video"); p.add_argument("--lang", default="uz"); p.add_argument("--model", default="large-v3")
    p.add_argument("--prompt", default=""); p.add_argument("--backend", default="auto"); p.add_argument("--out", default="words.json")
    o = p.parse_args()
    a = load_audio(o.video)
    backend = o.backend
    if backend == "auto":
        try:
            import mlx_whisper; backend = "mlx" if C.IS_MAC_ARM else "faster"
        except ImportError: backend = "faster"
    print(f"[{backend}] model={o.model} lang={o.lang}", flush=True)
    segs, lang = (run_mlx if backend == "mlx" else run_faster)(a, o)
    for s in segs: print(f"[{s['s']:6.2f}-{s['e']:6.2f}] {s['t']}")
    json.dump({"language": lang, "segments": segs}, open(o.out, "w", encoding="utf-8"), ensure_ascii=False)
    print("saqlandi:", o.out)
