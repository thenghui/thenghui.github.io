---
name: th-bahasa-malaysia-radio-sweeper-audio-maker
description: "Produce a broadcast-plausible Bahasa Malaysia radio imaging sequence — station ident, sweeper, short ID, TOH opener, promo sting and a transition into music — with a synthetic Malaysian voice (Gemini 3.8 Flash TTS) over a synthesised music bed, then master to −16 LUFS / −1 dBTP and package the WAV/MP3 with script, treatment and AI disclosure. Use when asked to make a BM radio sweeper, station ID, station imaging demo, TOH opener or promo sting, or to re-voice an imaging package with a Malaysian persona. Not for full songs, artist features, jingle melodies, podcast editing, transcription, or mixing existing commercial recordings."
metadata:
  short-description: Bahasa Malaysia radio sweeper/imaging audio — Gemini TTS voice + synth bed + master
---

# Bahasa Malaysia Radio Sweeper / Imaging Audio Maker

Build one short imaging sequence that sounds like a station, not a voice-over on a loop:
**ident → sweeper → short ID → TOH/opener → promo → transition into music.**

Everything is generated: the voice by Gemini 3.8 Flash TTS, the bed and effects by synthesis.
Nothing is sampled, so the output can be circulated internally without clearance risk — and every
AI element is labelled in `credits.md`.

## Success condition

A folder containing:

1. `<name>.wav` — 44.1 kHz / 16-bit master, **−16 LUFS integrated, ≤ −1 dBTP**;
2. `<name>.mp3` — 320 kbps listening copy, same loudness;
3. `script.md` — timecodes, verbatim lines, the `style` string sent per line;
4. `treatment.md` — voice, music, pacing, exits, mix, measured loudness;
5. `credits.md` — asset sources, AI disclosure, assumptions, rights position.

…and a QC pass showing every line is intelligible over the bed (ASR or a human listen) and there
is no dead air between elements.

## Preflight

```bash
scripts/py -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)"
ffmpeg -version | head -1
printf '%s' "$GEMINI_API_KEY" | head -c 4      # must start with AIza or AQ.
```

`scripts/py` is a thin wrapper: on first use it builds a venv in
`~/.cache/th-bahasa-malaysia-radio-sweeper-audio-maker/venv` and installs numpy/scipy there,
so the skill never depends on the agent's global Python and never ships a venv. Needs network
once.

- **Required:** `python3` (3.9+), `ffmpeg` with `loudnorm` + `ebur128`. numpy/scipy come from
  the wrapper's cached venv.
- **Required for VO:** a Google AI Studio key with access to `gemini-3.8-flash-tts`.
- **Optional QC:** `whisper-cli` with a ggml model (`~/.cache/whisper.cpp/ggml-small.bin`).
- Read `references/voice-and-language.md` before writing any line, and
  `references/mix-and-mastering.md` before touching gain.

## Workflow

### 0. Fix the brief in six answers

| Question | Default if the client does not say |
| --- | --- |
| Station name + slogan | Use only a slogan you can point to in the client's own material. If you cannot, write around it — never invent one. |
| Language mix | Full Bahasa Malaysia with Manglish cadence (`korang`, `kan`, `tau`, `jom`, `memang`) |
| Persona | Warm, friendly 30-year-old Malaysian, gentle pitch, casual — see §Voice |
| Duration | 60–75 s, six elements of one 4-bar phrase each at 118 BPM |
| Music | Malay pop-dance / synth-pop CHR, 112–124 BPM, A minor, Am–F–C–G |
| Delivery | WAV + MP3 + script + treatment + credits |

**Do not invent** show names, presenter names, artist features, prize details, listening figures or
slogans. If a name cannot be verified in the client's own material or on the station's public site,
write a generic tease or ask — never carry an unverified name into audio.

### 1. Write the lines

Copy `assets/lines.example.json` and replace the text. One JSON object per element:

```json
{"name": "id_main", "style": "warm, smiling, casual radio delivery",
 "text": "Hot FM. Muzik yang hangat, sepanjang hari. <short pause> Yang Terhangat, Yang Terbaik."}
```

Rules that matter (full detail in `references/script-patterns.md`):

- **`text` is a verbatim transcript.** Put sustained tone in `style`; put pauses and breaths in
  `text` as `<short pause>`, `<breath>`, `<sigh>`. Never write stage directions like "(warmly)".
- **Short `style` strings only** — 3–8 words. Long persona paragraphs cause voice drift.
- **One speaker.** Do not stack voices on a sweeper; that is what makes imaging sound disjointed.
- **8 seconds per element**, written to about 5.5–6.5 s to leave room for the exit.
- **Name the station early and often** — head of the read, and again mid-read.

### 2. Design the voice once

```bash
scripts/py scripts/tts_gemini.py design --out work/voice.json --sample work/voice_sample.wav \
  --persona "A warm, friendly 30-year-old Malaysian English speaker with a natural \
Manglish-influenced cadence, gentle pitch, and casual conversational tone." \
  --language en-MY --gender female
```

Returns a persistent `voice_...` ID plus a sample. **Reuse that ID for every line** — this is how
the six reads sound like one person. Voice design also fixes age, accent and timbre, which must
never be pushed through `style`.

### 3. Synthesise the reads

```bash
scripts/py scripts/tts_gemini.py synth --voice voice_xxxx --lines work/lines.json --out-dir work/vo
```

- Free tier is **3 requests/minute**: the script waits 21 s between calls and backs off 25 s on
  HTTP 429. Six lines ≈ 3 minutes.
- Existing non-empty WAVs are skipped, so a failed run resumes without re-spending quota.
- Raw output is 24 kHz mono WAV; the mixer resamples. Do not hand-edit the files.

### 4. Build the bed and mix

```bash
scripts/py scripts/build_sweeper_pack.py --config assets/config.example.json \
  --vo-dir work/vo --out work/raw.wav
```

The builder is config-driven: tempo, total length, chord loop, arrangement flags, voice
placements, logo hits and exits. See `assets/config.example.json` for the schema and a complete
66 s example.

Non-negotiables the builder enforces or you must set:

- **Every element ends on a designed exit** on a bar line — chord stab, sub drop, kompang hit,
  riser. **No fades anywhere.**
- **Voice sits above the bed**, not in it: bed ducked to ≈0.33 linear (−9.6 dB) under each read.
- **The music transition is real**: 12–17 s with no voice before the final cadence.
- **The logo appears in every element** at the same pitch (E5–F♯5–A5 unless the station has one).

### 5. Master

```bash
scripts/py scripts/master_export.py --in work/raw.wav \
  --wav out/station_imaging_v1.wav --mp3 out/station_imaging_v1.mp3
```

Two-pass `loudnorm` to −16 LUFS / −1 dBTP / LRA 9, 44.1 kHz 16-bit, 320 kbps MP3. The script prints
the measured integrated loudness, true peak and LRA from `ebur128`.

### 6. QC before you deliver

```bash
scripts/py scripts/qc_check.py --wav out/station_imaging_v1.wav --mp3 out/station_imaging_v1.mp3 --asr
```

Checks, in order: duration; true peak; 0.5 s RMS profile (flags any gap below −35 dBFS that is not
the final decay tail); voice-to-bed balance in nominated windows; ASR of the whole mix so you can
prove every line survives the bed.

`--asr` uses `whisper-cli -l ms`. Expect small-model spelling errors ("Korang" → "Kau orang"); what
you are checking is that **all six lines appear, in order, unobscured**.

### 7. Package

Write `script.md`, `treatment.md`, `credits.md` from the templates in
`references/delivery-pack.md`. Minimum content:

- **script.md** — element table with timecodes, verbatim lines, the exact `style` string per line,
  what a human presenter should change.
- **treatment.md** — model + voice ID, persona, post chain, music spec, exit table, measured
  loudness, reproduction commands.
- **credits.md** — every asset's source, explicit **"the voice is synthetic"**, assumptions
  (gender, language code, tempo, placeholder time checks), and the rights position.

## Voice defaults

| Setting | Value |
| --- | --- |
| Model | `gemini-3.8-flash-tts` |
| Endpoint | `POST /v1beta/interactions`, `response_format={"type":"audio"}` |
| Identity | `POST /v1beta/voices` — `type=prompted`, `store=true`, returns `voice_...` |
| Persona | "Warm, friendly 30-year-old Malaysian English speaker, natural Manglish-influenced cadence, gentle pitch, casual conversational tone" |
| Language | `en-MY` for an English persona reading BM; `ms-MY` if the client wants native BM |
| Gender | **Ask or assume and record it** — the persona text usually does not specify |
| Style | 3–8 words per line, reused verbatim across sections |
| Voice chain | HPF 90 Hz → 165 Hz +2 → 480 Hz −1.5 → 3.4 kHz +2.5 → 9.5 kHz +1.5 → 3:1 comp → −18 LUFS |

## Mix defaults

| Parameter | Value |
| --- | --- |
| Bed RMS (music-only) | ≈ −14.5 dBFS |
| Voice RMS | −17.5 dBFS per read |
| Duck under voice | 0.33 linear (−9.6 dB), 80 ms ramps |
| Vocal pocket | −3.5 dB at 1.8–4.8 kHz on the music bus only |
| Bus | soft `tanh`, then peak trim to 0.92 |
| Master | −16 LUFS, −1 dBTP, LRA 9 |

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| 429 `Rate limit exceeded ... 3 requests per minute` | free tier | wait 25 s; keep throttle at 21 s |
| Voice drifts between lines | long `style`/persona re-sent per line | shorten `style`; keep one voice ID |
| "short pause" is spoken aloud | tag placed in `style` or spelled wrong | put `<short pause>` in `text`, keep tags in English |
| Voice sounds buried | bed not ducked / voice too low | check the QC balance windows; target voice ≥6 dB over bed |
| Bed disappears under the ident | pad-only intro too quiet | raise `intro_pad_gain` (2.5–3.0) and keep the kick pulse |
| Harsh sibilance | presence EQ too high for the voice | reduce 3.4 kHz to +1.5 dB, add de-esser |
| Click at a section join | impact not on a bar line | place exits at `bar × 2.034 s` for 118 BPM |
| Ends on silence | tail trimmed | keep 2.5–3 s after the final cadence |

## Files

- `scripts/tts_gemini.py` — Voice design, single read, batch synthesis (rate-limited, resumable).
- `scripts/build_sweeper_pack.py` — config-driven bed synthesis, VO processing, ducking, mix.
- `scripts/master_export.py` — two-pass loudnorm master, WAV + MP3 export, measurement report.
- `scripts/qc_check.py` — duration, peak, gap detection, voice-to-bed windows, optional ASR.
- `scripts/py` — cached-venv Python wrapper (numpy/scipy), so no global install is required.
- `references/voice-and-language.md` — persona prompts, Manglish patterns, style strings.
- `references/script-patterns.md` — the six element templates with BM examples.
- `references/mix-and-mastering.md` — gain staging, exits, EQ chain, loudness targets.
- `references/delivery-pack.md` — script/treatment/credits templates.
- `assets/lines.example.json`, `assets/config.example.json` — working examples.
