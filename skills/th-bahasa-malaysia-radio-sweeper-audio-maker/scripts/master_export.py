#!/usr/bin/env python3
"""Two-pass EBU R128 master and export: WAV 44.1/16 + 320 kbps MP3.

Targets -16 LUFS integrated, -1 dBTP true peak, LRA 9 by default.
Prints the measured values with ffmpeg's ebur128 so the delivery can be quoted.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys


def parse_loudnorm(stderr: str) -> dict:
    start = stderr.find("{")
    end = stderr.rfind("}")
    if start < 0 or end < 0:
        sys.exit("could not parse loudnorm measurement")
    return json.loads(stderr[start:end + 1])


def measure(path: str) -> dict:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path,
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    summary = out[out.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    lra = re.search(r"LRA:\s+(-?[\d.]+) LU", summary)
    peak = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary)
    tp = re.search(r"True peak:\s*\n?\s*Peak:\s+(-?[\d.]+)", out)
    return {
        "integrated_lufs": float(i.group(1)) if i else None,
        "lra_lu": float(lra.group(1)) if lra else None,
        "sample_peak_dbfs": float(peak.group(1)) if peak else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--wav", required=True)
    ap.add_argument("--mp3", required=True)
    ap.add_argument("--lufs", type=float, default=-16.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--lra", type=float, default=9.0)
    ap.add_argument("--bitrate", default="320k")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.wav)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.mp3)), exist_ok=True)

    p1 = subprocess.run(
        ["ffmpeg", "-hide_banner", "-y", "-i", args.src,
         "-af", f"loudnorm=I={args.lufs}:TP={args.tp}:LRA={args.lra}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    m = parse_loudnorm(p1.stderr)
    print(f"input: {m['input_i']} LUFS, {m['input_tp']} dBTP, LRA {m['input_lra']}")

    norm = (f"loudnorm=I={args.lufs}:TP={args.tp}:LRA={args.lra}:"
            f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}:linear=true")

    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", args.src,
                    "-af", norm, "-ar", "44100", "-c:a", "pcm_s16le", args.wav], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", args.wav,
                    "-b:a", args.bitrate, args.mp3], check=True)

    wav_m, mp3_m = measure(args.wav), measure(args.mp3)
    print(f"WAV  {os.path.basename(args.wav)}: {wav_m['integrated_lufs']} LUFS, "
          f"LRA {wav_m['lra_lu']} LU, peak {wav_m['sample_peak_dbfs']} dBFS")
    print(f"MP3  {os.path.basename(args.mp3)}: {mp3_m['integrated_lufs']} LUFS, "
          f"peak {mp3_m['sample_peak_dbfs']} dBFS")
    if abs((wav_m["integrated_lufs"] or 0) - args.lufs) > 0.5:
        print("WARN: integrated loudness missed the target by more than 0.5 LU")


if __name__ == "__main__":
    main()
