# Bahasa Malaysia Radio Sweeper / Imaging Audio Maker

Build a short Bahasa Malaysia radio imaging sequence — station ident, sweeper, short ID, TOH
opener, promo sting and a transition into music — with a synthetic Malaysian voice over a
synthesised music bed, mastered to −16 LUFS / −1 dBTP.

Everything is generated: the voice by **Gemini 3.8 Flash TTS**, the music and effects by
synthesis. No samples, no commercial tracks, no cloned voices.

## What it produces

| File | Contents |
| --- | --- |
| `station_imaging_v1.wav` | 44.1 kHz / 16-bit master, −16 LUFS, ≤ −1 dBTP |
| `station_imaging_v1.mp3` | 320 kbps listening copy |
| `script.md` | Timecodes, verbatim lines, exact style strings |
| `treatment.md` | Voice, music, exits, mix, measured loudness, repro commands |
| `credits.md` | Asset sources, AI disclosure, assumptions, rights position |

## Install

```bash
git clone https://github.com/thenghui/thenghui.github.io.git   # or download the zip
mkdir -p ~/.codex/skills
cp -R th-bahasa-malaysia-radio-sweeper-audio-maker ~/.codex/skills/
ln -s ~/.codex/skills/th-bahasa-malaysia-radio-sweeper-audio-maker ~/.copilot/skills/
ln -s ~/.codex/skills/th-bahasa-malaysia-radio-sweeper-audio-maker ~/.claude/skills/
```

Any agent that reads `SKILL.md` from a skills folder can use it: GitHub Copilot CLI, Claude Code,
Codex CLI, Cursor, Gemini CLI, Kiro.

## Requirements

- `python3` 3.9+ and `ffmpeg` (with `loudnorm` and `ebur128`)
- A Google AI Studio key with access to `gemini-3.8-flash-tts` in `GEMINI_API_KEY`
- Optional: `whisper-cli` + `ggml-small.bin` for the ASR quality check

`scripts/py` bootstraps numpy/scipy into `~/.cache/th-bahasa-malaysia-radio-sweeper-audio-maker/venv`
on first run, so no global Python packages are needed.

## Quick start

```bash
export GEMINI_API_KEY=AIza...

# 1. persona
scripts/py scripts/tts_gemini.py design --out work/voice.json --sample work/sample.wav \
  --persona "A warm, friendly 30-year-old Malaysian English speaker with a natural \
Manglish-influenced cadence, gentle pitch, and casual conversational tone."

# 2. six reads (free tier: 3 requests/minute, ~3 minutes)
scripts/py scripts/tts_gemini.py synth --voice voice_xxxx \
  --lines assets/lines.example.json --out-dir work/vo

# 3. bed + mix
scripts/py scripts/build_sweeper_pack.py --config assets/config.example.json \
  --vo-dir work/vo --out work/raw.wav

# 4. master
scripts/py scripts/master_export.py --in work/raw.wav \
  --wav out/station_imaging_v1.wav --mp3 out/station_imaging_v1.mp3

# 5. QC
scripts/py scripts/qc_check.py --wav out/station_imaging_v1.wav --asr
```

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/tts_gemini.py` | Voice design, single line, batch synthesis (resumable, rate-limited) |
| `scripts/build_sweeper_pack.py` | Config-driven bed synthesis, VO processing, ducking, mix |
| `scripts/master_export.py` | Two-pass loudnorm, WAV + MP3, measurement report |
| `scripts/qc_check.py` | Dead air, peak, voice/bed separation, optional ASR transcript |
| `scripts/py` | Cached-venv Python wrapper |

## Non-negotiables

- Never invent show names, artists, prizes, slogans or listening figures.
- One voice per sequence; no stacked VO.
- Every element ends on a designed exit on a bar line; no fades.
- Every AI element is labelled, including the voice.

Docs: `references/voice-and-language.md`, `references/script-patterns.md`,
`references/mix-and-mastering.md`, `references/delivery-pack.md`.
