#!/usr/bin/env python3
"""Build a radio imaging sequence: synthesised bed + processed voice + designed exits.

Reads a JSON config (see assets/config.example.json), mixes the VO stems produced by
tts_gemini.py onto a synthesised 4-on-the-floor bed, ducks the music under every read,
and writes a raw 44.1 kHz stereo WAV for master_export.py.

No samples, no loops, no commercial audio: every sound here is generated from
oscillators and filtered noise.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
rng = np.random.default_rng(20261109)

VO_CHAIN = (
    "highpass=f=90,"
    "equalizer=f=165:t=q:w=1.0:g=2.0,"
    "equalizer=f=480:t=q:w=1.2:g=-1.5,"
    "equalizer=f=3400:t=q:w=1.1:g=2.5,"
    "treble=g=1.5:f=9500,"
    "acompressor=threshold=-18dB:ratio=3:attack=8:release=120:makeup=2.5dB,"
    "loudnorm=I=-18:TP=-3:LRA=7"
)


# ---------------------------------------------------------------- DSP primitives
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a_n - d_n - r_n)
    env = np.concatenate([
        np.linspace(0, 1, max(1, a_n), endpoint=False),
        np.linspace(1, s, max(1, d_n), endpoint=False),
        np.full(s_n, s),
        np.linspace(s, 0, max(1, r_n)),
    ])
    return np.pad(env, (0, max(0, n - len(env))))[:n]


def osc(freq, dur, kind="sine", detune=0.0):
    t = t_axis(dur)
    f = freq * (1.0 + detune)
    if kind == "sine":
        return np.sin(2.0 * np.pi * f * t)
    if kind == "saw":
        phase = (t * f) % 1.0
        return (2.0 * phase - 1.0) * 0.55
    if kind == "square":
        phase = (t * f) % 1.0
        return np.where(phase < 0.5, 0.5, -0.5)
    raise ValueError(kind)


def lp(x, cutoff, order=2):
    sos = butter(order, min(cutoff, SR / 2 - 200), btype="low", fs=SR, output="sos")
    return sosfilt(sos, x)


def hp(x, cutoff, order=2):
    sos = butter(order, max(cutoff, 20), btype="high", fs=SR, output="sos")
    return sosfilt(sos, x)


def bp(x, lo, hi, order=2):
    sos = butter(order, [max(lo, 20), min(hi, SR / 2 - 200)], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def kick(dur=0.38):
    t = t_axis(dur)
    f = 52 + 140 * np.exp(-t / 0.028)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR)
    click = hp(rng.normal(0, 1, len(t)), 3200) * np.exp(-t / 0.003) * 0.35
    return (body * np.exp(-t / 0.095) + click) * 0.95


def sub_drop(dur=1.4):
    t = t_axis(dur)
    f = 110 * np.exp(-t / 0.32) + 32
    return lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.38), 160) * 0.95


def kompang(dur=0.22):
    t = t_axis(dur)
    noise = bp(rng.normal(0, 1, len(t)), 750, 5200) * np.exp(-t / 0.038)
    thump = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.045) * 0.65
    return (noise * 0.72 + thump) * 0.88


def clap(dur=0.26):
    t = t_axis(dur)
    out = np.zeros_like(t)
    for off in (0.0, 0.008, 0.016, 0.026):
        i = int(off * SR)
        seg = bp(rng.normal(0, 1, len(t) - i), 1400, 4600)
        seg *= np.exp(-np.arange(len(seg)) / (0.012 * SR))
        out[i:] += seg * (0.95 if off == 0 else 0.55)
    return out * 0.52


def hat(dur=0.08, open_=False):
    t = t_axis(dur)
    return hp(rng.normal(0, 1, len(t)), 7200) * np.exp(-t / (0.052 if open_ else 0.016)) * 0.25


def bass(note, dur):
    t = t_axis(dur)
    f = midi(note)
    x = 0.68 * np.sin(2 * np.pi * f * t) + 0.32 * osc(f, dur, "saw")
    return lp(x, 400) * adsr(len(t), 0.006, 0.05, 0.65, 0.08) * 0.90


def pad(notes, dur):
    out = np.zeros(int(dur * SR))
    for n in notes:
        for dt in (-0.005, 0.0, 0.006):
            out += osc(midi(n), dur, "saw", detune=dt)
    out = lp(out / (len(notes) * 3), 2200)
    return out * adsr(len(out), 0.16, 0.15, 0.82, 0.32) * 0.50


def pluck(note, dur=0.45):
    t = t_axis(dur)
    f = midi(note)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) \
        + 0.22 * np.sin(2 * np.pi * 3 * f * t)
    return x * np.exp(-t / 0.13) * 0.38


def riser(dur=1.5):
    t = t_axis(dur)
    x = rng.normal(0, 1, len(t))
    out = np.zeros_like(x)
    for i in range(16):
        seg = slice(int(i * len(t) / 16), int((i + 1) * len(t) / 16))
        out[seg] = bp(x[seg], 350 * (1 + i * 0.3), 1000 * (1 + i * 0.45))
    return out * (np.linspace(0.02, 1.0, len(t)) ** 2.2) * 0.48


def exit_impact(dur=2.0, chord_notes=(57, 60, 64, 69)):
    t = t_axis(dur)
    out = np.zeros(int(dur * SR))
    for n in chord_notes:
        f = midi(n)
        out += (lp(osc(f, dur, "saw") + osc(f, dur, "sine"), 3000)
                * adsr(len(t), 0.002, 0.08, 0.28, 0.55)) * 0.24
    out += hp(rng.normal(0, 1, len(t)), 4200) * np.exp(-t / 0.42) * 0.38
    sub = sub_drop(min(dur, 1.2))
    out[:len(sub)] += sub * 0.72
    k = kompang(0.24)
    out[:len(k)] += k * 0.58
    return out


def logo():
    """Three-note station logo, E5 - F#5 - A5. Keep pitch and timbre fixed everywhere."""
    notes, dur = [(76, 0.00), (78, 0.24), (81, 0.48)], 1.45
    out = np.zeros(int(dur * SR))
    for n, off in notes:
        seg = osc(midi(n), dur - off, "sine") * adsr(int((dur - off) * SR), 0.004, 0.04, 0.55, 0.45)
        i = int(off * SR)
        out[i:i + len(seg)] += seg * 0.36
    k = kompang(0.25)
    out[:len(k)] += k * 0.55
    return out


def add_st(buf, x, i, gain=1.0):
    n = buf.shape[1]
    if i >= n or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    end = min(n, i + len(x))
    buf[0, i:end] += x[:end - i] * gain
    buf[1, i:end] += x[:end - i] * gain


def add_pan(buf, x, i, gain=1.0, pan=0.5):
    n = buf.shape[1]
    if i >= n:
        return
    end = min(n, i + len(x))
    if end <= i:
        return
    buf[0, i:end] += x[:end - i] * gain * (1.0 - pan) * np.sqrt(2)
    buf[1, i:end] += x[:end - i] * gain * pan * np.sqrt(2)


# ---------------------------------------------------------------- Bed
def build_bed(cfg):
    bpm = float(cfg["bpm"])
    total = float(cfg["total"])
    beat, bar = 60.0 / bpm, 4 * 60.0 / bpm
    arr = cfg.get("arrangement", {})
    intro_until = float(arr.get("intro_until", 0.0))
    drums_from = float(arr.get("drums_from", intro_until))
    full_from = float(arr.get("full_from", drums_from))
    intro_gain = float(arr.get("intro_pad_gain", 2.85))
    pad_gain = float(arr.get("pad_gain", 0.62))
    breakdowns = [tuple(b) for b in arr.get("breakdowns", [])]
    chords = [tuple(c) for c in cfg["chords"]]
    hook = cfg.get("hook", [69, 72, 76, 74, 72, 69, 74, 76])

    n = int(total * SR)
    music = np.zeros((2, n))
    send = np.zeros((2, n))

    bar_i, pos = 0, 0.0
    while pos < total - 1.0:
        ch = chords[bar_i % len(chords)]
        i0 = int(pos * SR)
        intro = pos < intro_until
        breakdown = any(a <= pos < a + d for a, d in breakdowns)
        drums = pos >= drums_from and not breakdown
        full = pos >= full_from and not breakdown

        p = pad(ch, bar + 0.3)
        add_st(music, p * (intro_gain if intro else pad_gain), i0)
        if intro:
            add_st(send, p, i0, 0.20)
            # sparse pulse keeps the ident moving without stealing the read
            add_st(music, kick(0.40), i0, 0.50)
            add_st(music, kick(0.40), int((pos + 2 * beat) * SR), 0.34)
            add_st(music, sub_drop(0.9), i0, 0.22)

        if drums:
            for b in (0.0, 1.0, 2.0, 3.0):
                add_st(music, kick(), int((pos + b * beat) * SR), 0.88)
            for b in (1.0, 3.0):
                add_st(music, kompang(), int((pos + b * beat) * SR), 0.60)
                if full:
                    add_st(music, clap(), int((pos + b * beat) * SR), 0.48)
            for i8 in range(8):
                add_pan(music, hat(open_=(i8 == 7)), int((pos + i8 * beat / 2) * SR),
                        0.70 if i8 % 2 == 0 else 0.40, pan=0.6 if i8 % 2 == 0 else 0.4)
            add_st(music, bass(ch[0] - 12, beat * 1.4), i0)
            add_st(music, bass(ch[0] - 12, beat * 0.9), int((pos + 2 * beat) * SR), 0.78)

        if full:
            for k, off in enumerate((0.0, 1.5, 2.0, 3.5)):
                pl = pluck(hook[(bar_i * 2 + k) % len(hook)])
                i = int((pos + off * beat) * SR)
                add_st(music, pl, i, 0.42)
                add_st(send, pl, i, 0.24)

        pos += bar
        bar_i += 1

    for ex in cfg.get("exits", []):
        add_st(music, exit_impact(1.6), int(float(ex) * SR), 0.78)
        add_st(music, riser(1.4), int((float(ex) - 1.45) * SR), 0.50)

    fin = cfg.get("final_exit")
    if fin:
        at = float(fin["at"]) if isinstance(fin, dict) else float(fin)
        chord = tuple(fin.get("chord", [57, 60, 64, 69, 76, 81])) if isinstance(fin, dict) else \
            (57, 60, 64, 69, 76, 81)
        tail = float(fin.get("tail", 2.9)) if isinstance(fin, dict) else 2.9
        add_st(music, exit_impact(tail, chord_notes=chord), int(at * SR), 0.95)
        add_st(music, riser(1.9), int((at - 1.95) * SR), 0.60)

    ir_len = int(0.9 * SR)
    ti = np.arange(ir_len) / SR
    for c in (0, 1):
        ir = lp(rng.normal(0, 1, ir_len) * np.exp(-ti / 0.3), 5500)
        music[c] += fftconvolve(send[c], ir)[:n] * 0.05
    return music


# ---------------------------------------------------------------- Voice
def prep_voice(path: str, workdir: str) -> np.ndarray:
    dst = os.path.join(workdir, os.path.basename(path))
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", path, "-af", VO_CHAIN,
         "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst],
        check=True,
    )
    with wave.open(dst, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    env = np.abs(hp(x, 120))
    k = int(0.01 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    live = np.where(env > max(np.max(env) * 0.02, 1e-4))[0]
    if len(live):
        x = x[max(0, live[0] - int(0.04 * SR)):min(len(x), live[-1] + int(0.10 * SR))]
    return x


def duck_envelope(events, n, depth):
    env = np.ones(n)
    for start, dur in events:
        a, b = int(start * SR), int((start + dur) * SR)
        a, b = max(0, a), min(n, b)
        if b > a:
            env[a:b] = depth
    k = int(0.08 * SR)
    return np.convolve(env, np.ones(k) / k, mode="same")[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--vo-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-voice-process", action="store_true",
                    help="read stems as-is (they must already be 44.1 kHz mono)")
    ap.add_argument("--print-timeline", action="store_true")
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    mix_cfg = cfg.get("mix", {})
    bed_gain = float(mix_cfg.get("bed_gain", 0.80))
    duck = float(mix_cfg.get("duck", 0.33))
    vo_rms = float(mix_cfg.get("vo_rms_db", -17.5))
    peak = float(mix_cfg.get("peak", 0.92))

    music = build_bed(cfg) * bed_gain
    n = music.shape[1]
    for c in (0, 1):
        music[c] -= bp(music[c], 1800, 4800) * 0.35

    workdir = tempfile.mkdtemp(prefix="sweeper_vo_")
    vo_bus, fx = np.zeros((2, n)), np.zeros((2, n))
    events, timeline = [], []

    for item in cfg.get("voice", []):
        stem = os.path.join(args.vo_dir, item["file"])
        if not os.path.exists(stem):
            sys.exit(f"missing voice stem: {stem}")
        if args.no_voice_process:
            x, sr = _read_wav_mono(stem)
            x = _resample_to_sr(x, sr)
        else:
            x = prep_voice(stem, workdir)
        rms = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = np.clip(x * (10 ** (vo_rms / 20) / rms), -0.98, 0.98)
        at = float(item["at"])
        add_st(vo_bus, x, int(at * SR), 1.0)
        dur = len(x) / SR
        events.append((at, dur))
        timeline.append({"element": item.get("name", item["file"]), "at": round(at, 2),
                         "duration": round(dur, 2)})

    for t in cfg.get("logos", []):
        add_st(fx, logo(), int(float(t) * SR), 0.55)

    mix = music * duck_envelope(events, n, duck) + vo_bus + fx
    mix = np.tanh(mix * 0.9) / 0.9
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * peak

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with wave.open(args.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix.T, -1, 1) * 32767).astype(np.int16).tobytes())

    print(f"raw mix: {args.out}  ({mix.shape[1] / SR:.2f}s, {n / SR:.1f}s bed)")
    if args.print_timeline:
        print(json.dumps({"bpm": cfg["bpm"], "total": cfg["total"],
                          "exits": cfg.get("exits", []),
                          "final_exit": cfg.get("final_exit"),
                          "placements": timeline}, indent=1))


def _read_wav_mono(path: str):
    with wave.open(path, "rb") as w:
        ch, sr = w.getnchannels(), w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    return data / 32768.0, sr


def _resample_to_sr(x: np.ndarray, sr: int) -> np.ndarray:
    if sr == SR or not len(x):
        return x
    from math import gcd
    from scipy.signal import resample_poly
    g = gcd(SR, sr)
    return resample_poly(x, SR // g, sr // g)


if __name__ == "__main__":
    main()
