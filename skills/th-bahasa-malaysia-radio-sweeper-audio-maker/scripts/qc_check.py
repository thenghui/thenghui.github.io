#!/usr/bin/env python3
"""QC a finished imaging master.

Checks duration, peak, dead air, voice-to-bed balance and (optionally) runs ASR over the
whole mix to prove every line survives the bed.

Examples
  qc_check.py --wav out/demo.wav --mp3 out/demo.mp3 --asr
  qc_check.py --wav out/demo.wav --voice-window 1.5-4 --voice-window 9.5-13 --bed-window 54-58
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import wave

import numpy as np


def read_wav(path: str):
    with wave.open(path, "rb") as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    return (x.reshape(-1, ch).mean(axis=1) if ch > 1 else x), sr


def rms_db(x) -> float:
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def profile(x, sr, win=0.5):
    n = int(win * sr)
    return [(i / sr, rms_db(x[i:i + n])) for i in range(0, max(1, len(x) - n), n)]


def loudness(path: str) -> dict:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    s = out[out.rfind("Summary:"):]
    grab = lambda p: (lambda m: float(m.group(1)) if m else None)(re.search(p, s))
    return {"I": grab(r"I:\s+(-?[\d.]+) LUFS"), "LRA": grab(r"LRA:\s+(-?[\d.]+) LU"),
            "Peak": grab(r"Peak:\s+(-?[\d.]+) dBFS")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--mp3")
    ap.add_argument("--voice-window", action="append", default=[], metavar="START-END")
    ap.add_argument("--bed-window", action="append", default=[], metavar="START-END",
                    help="music-only window from the SAME arrangement section as the voice window")
    ap.add_argument("--duck-db", type=float, default=9.6,
                    help="duck depth used by the mix (0.33 linear = 9.6 dB)")
    ap.add_argument("--asr", action="store_true")
    ap.add_argument("--asr-model", default=os.path.expanduser("~/.cache/whisper.cpp/ggml-small.bin"))
    ap.add_argument("--lang", default="ms")
    args = ap.parse_args()

    x, sr = read_wav(args.wav)
    dur = len(x) / sr
    print(f"duration      {dur:.2f} s")
    print(f"sample peak   {20 * np.log10(np.max(np.abs(x)) + 1e-9):.2f} dBFS")

    prof = profile(x, sr)
    tail = max(1, int(3.0 / 0.5))  # ignore the final decay when looking for dead air
    body = prof[:-tail] if len(prof) > tail else prof
    gaps = [(t, r) for t, r in body if r < -35]
    print(f"lowest 0.5 s  {min(r for _, r in prof):.1f} dBFS at {min(prof, key=lambda z: z[1])[0]:.1f} s")
    if gaps:
        print(f"WARN dead air below -35 dBFS at: {', '.join(f'{t:.1f}s' for t, _ in gaps[:8])}")
    else:
        print("no dead air    (no 0.5 s window below -35 dBFS before the tail)")

    def span(arg):
        a, b = (float(v) for v in arg.split("-"))
        return rms_db(x[int(a * sr):int(b * sr)])

    voices = [span(w) for w in args.voice_window]
    beds = [span(w) for w in args.bed_window]
    if voices:
        print(f"voice windows {', '.join(f'{v:.1f}' for v in voices)} dBFS")
    if beds:
        print(f"bed windows   {', '.join(f'{v:.1f}' for v in beds)} dBFS")
    if voices and beds:
        bed_under = np.mean(beds) - args.duck_db
        sep = np.mean(voices) - bed_under
        verdict = "OK" if sep >= 6 else ("THIN" if sep >= 3 else "TOO LOW — raise VO or deepen duck")
        print(f"bed @ full    {np.mean(beds):.1f} dBFS (reference window)")
        print(f"bed @ duck    {bed_under:.1f} dBFS (reference minus {args.duck_db:.1f} dB)")
        print(f"separation    {sep:.1f} dB between voice and ducked bed ({verdict}; target >= 6 dB)")

    print(f"loudness      {loudness(args.wav)}")
    if args.mp3:
        print(f"mp3 loudness  {loudness(args.mp3)}")

    if args.asr:
        if not os.path.exists(args.asr_model):
            print("ASR skipped: model not found at", args.asr_model)
            return
        out = subprocess.run(
            ["whisper-cli", "-m", args.asr_model, "-l", args.lang, "-nt", "-f", args.wav],
            capture_output=True, text=True).stdout.strip()
        print("\nASR transcript:\n" + (out or "(no speech detected)"))
        print("\nRead the transcript against script.md: every line must appear, in order.")


if __name__ == "__main__":
    main()
