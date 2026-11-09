#!/usr/bin/env python3
"""Gemini 3.8 Flash TTS client for radio imaging.

Stages:
  design  Create a persistent persona voice (`POST /v1beta/voices`, type=prompted).
  say     Synthesise one line.
  synth   Synthesise every line in a JSON file (rate-limited, resumable).
  voices  List stored voices.

The API key is read from $GEMINI_API_KEY, or from --key-file. It is never written
to an output file or echoed in logs.

Docs: https://ai.google.dev/gemini-api/docs/speech-generation
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave

API = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.8-flash-tts"
RATE_LIMIT_WAIT = 25.0


def api_key(args) -> str:
    if getattr(args, "key_file", None):
        with open(args.key_file) as f:
            return f.read().strip()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        if getattr(args, "dry_run", False):
            return "dry-run"
        sys.exit("No API key. Set GEMINI_API_KEY, or pass --key-file.")
    return key


def request(path: str, payload: dict | None, key: str, method: str = "POST",
            retries: int = 8, timeout: int = 240) -> dict:
    url = f"{API}/{path}"
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("x-goog-api-key", key)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:800]
            if e.code in (429, 500, 503) and attempt < retries - 1:
                wait = RATE_LIMIT_WAIT if e.code == 429 else min(2 ** attempt * 2, 30)
                print(f"  {e.code} — waiting {wait:.0f}s", flush=True)
                time.sleep(wait)
                continue
            raise SystemExit(f"HTTP {e.code} on {path}: {detail}") from None
    raise SystemExit("retries exhausted")


def extract_audio(resp: dict) -> str | None:
    audio = None
    for step in resp.get("steps", []):
        if step.get("type") != "model_output":
            continue
        for item in step.get("content", []):
            if item.get("type") == "audio" and item.get("data"):
                audio = item["data"]
    return audio


def wav_duration(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate()


def cmd_design(args) -> None:
    payload = {
        "store": True,
        "voice": {
            "model": args.model,
            "type": "prompted",
            "display_name": args.name,
            "gender": args.gender,
            "language_code": args.language,
            "prompted": {"input": args.persona},
        },
    }
    if args.dry_run:
        print(json.dumps(payload, indent=1))
        return
    resp = request("voices", payload, api_key(args))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(resp, f, indent=1)
    if args.sample and resp.get("sample_audio", {}).get("data"):
        with open(args.sample, "wb") as f:
            f.write(base64.b64decode(resp["sample_audio"]["data"]))
    print(f"voice_id: {resp.get('id')}  language: {resp.get('language_code')}  "
          f"saved: {args.out}")


def build_synth_payload(model: str, voice: str, text: str, style: str) -> dict:
    return {
        "model": model,
        "input": [{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{"type": "speech_metadata", "style": style}],
            }],
        }],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }


def synth_one(args, key: str, text: str, style: str, out: str) -> None:
    payload = build_synth_payload(args.model, args.voice, text, style)
    if args.dry_run:
        print(json.dumps(payload, indent=1))
        return
    resp = request("interactions", payload, key)
    data = extract_audio(resp)
    if not data:
        raise SystemExit(f"no audio in response: {json.dumps(resp)[:400]}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(base64.b64decode(data))


def cmd_say(args) -> None:
    key = api_key(args)
    text = args.text if args.text else open(args.text_file).read().strip()
    synth_one(args, key, text, args.style, args.out)
    print(f"wrote {args.out} ({wav_duration(args.out):.2f}s)")


def cmd_synth(args) -> None:
    key = api_key(args)
    lines = json.load(open(args.lines))
    os.makedirs(args.out_dir, exist_ok=True)
    meta = []
    for i, item in enumerate(lines):
        name = item["name"]
        out = os.path.join(args.out_dir, f"{name}.wav")
        if args.resume and os.path.exists(out) and os.path.getsize(out) > 20000:
            print(f"{name:14s} cached")
        else:
            if args.dry_run:
                synth_one(args, key, item["text"], item.get("style", ""), out)
                continue
            synth_one(args, key, item["text"], item.get("style", ""), out)
            print(f"{name:14s} {wav_duration(out):6.2f}s")
            if i < len(lines) - 1:
                time.sleep(args.throttle)
        meta.append({
            "name": name, "file": out, "duration": round(wav_duration(out), 3),
            "text": item["text"], "style": item.get("style", ""),
        })
    if not args.dry_run:
        with open(os.path.join(args.out_dir, "vo_meta.json"), "w") as f:
            json.dump(meta, f, indent=1, ensure_ascii=False)
        total = sum(m["duration"] for m in meta)
        print(f"{len(meta)} lines, {total:.1f}s of speech")


def cmd_voices(args) -> None:
    resp = request(f"voices?page_size={args.limit}", None, api_key(args), method="GET")
    for v in resp.get("voices", []):
        print(f"{v.get('id'):32s} {v.get('display_name','')[:28]:28s} "
              f"{v.get('language_code',''):6s} {v.get('type','')}")


def add_common(p):
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--key-file", help="file holding the API key (default: $GEMINI_API_KEY)")
    p.add_argument("--dry-run", action="store_true", help="print the request, spend no quota")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("design", help="create a persistent persona voice")
    add_common(d)
    d.add_argument("--out", required=True, help="voice.json output path")
    d.add_argument("--sample", help="save the sample_audio preview here")
    d.add_argument("--persona", required=True)
    d.add_argument("--name", default="Imaging voice")
    d.add_argument("--language", default="en-MY")
    d.add_argument("--gender", default="female", choices=["female", "male", "neutral"])
    d.set_defaults(func=cmd_design)

    s = sub.add_parser("say", help="synthesise one line")
    add_common(s)
    s.add_argument("--voice", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--style", default="")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--text-file")
    s.set_defaults(func=cmd_say)

    b = sub.add_parser("synth", help="synthesise every line in a JSON file")
    add_common(b)
    b.add_argument("--voice", required=True)
    b.add_argument("--lines", required=True)
    b.add_argument("--out-dir", required=True)
    b.add_argument("--throttle", type=float, default=21.0,
                   help="seconds between calls (free tier: 3/min)")
    b.add_argument("--no-resume", dest="resume", action="store_false",
                   help="regenerate files that already exist")
    b.set_defaults(func=cmd_synth, resume=True)

    v = sub.add_parser("voices", help="list stored voices")
    add_common(v)
    v.add_argument("--limit", type=int, default=30)
    v.set_defaults(func=cmd_voices)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
