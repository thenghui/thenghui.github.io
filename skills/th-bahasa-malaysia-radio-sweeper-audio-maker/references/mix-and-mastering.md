# Mix and mastering

## 1. Signal flow

```
VO stems (24 kHz mono)
  └─ HPF 90 → EQ → comp → loudnorm −18 LUFS → trim silence → RMS to −17.5 dBFS
                                                              ↓
bed (synthesised 118 BPM) ─→ vocal pocket −3.5 dB @1.8–4.8 kHz ─→ duck ×0.33 under each read
                                                              ↓
logos + exits (parallel FX bus) ────────────────────────────→ sum
                                                              ↓
                                             soft tanh → peak 0.92 → raw WAV
                                                              ↓
                                   two-pass loudnorm −16 LUFS / −1 dBTP → WAV + MP3
```

## 2. Voice chain

```
highpass=f=90
equalizer=f=165:t=q:w=1.0:g=2.0
equalizer=f=480:t=q:w=1.2:g=-1.5
equalizer=f=3400:t=q:w=1.1:g=2.5
treble=g=1.5:f=9500
acompressor=threshold=-18dB:ratio=3:attack=8:release=120:makeup=2.5dB
loudnorm=I=-18:TP=-3:LRA=7
```

Why: radio imaging lives on a car speaker and a phone. Remove everything below 90 Hz, add chest
at 165 Hz, cut the 480 Hz box, and put the intelligibility band at 3.4 kHz. Compression is gentle
because the TTS is already even.

If the read hisses: drop 3.4 kHz to +1.5 dB. If it sounds thin: raise 165 Hz to +2.5 dB. Do not
chase loudness with EQ.

## 3. Ducking

- Depth **0.33 linear = −9.6 dB** under voice, 80 ms ramps.
- Shallower (0.5 / −6 dB) is normal for a mixed music bed; deeper is needed when the voice is
  synthetic and the bed is dense.
- Measure it: `qc_check.py --voice-window a-b --bed-window c-d --duck-db 9.6`. Target ≥ 6 dB
  between the voice window and the *ducked* bed, using a bed window from the same section.

## 4. Designed exits

Place every exit on a bar line. Bar length = `4 × 60 / BPM`:

| BPM | Bar | 4 bars |
| ---: | ---: | ---: |
| 112 | 2.143 s | 8.571 s |
| 118 | 2.034 s | 8.136 s |
| 122 | 1.967 s | 7.869 s |
| 124 | 1.935 s | 7.742 s |

Exit recipe (1.5–2 s total):

1. **Riser** starts 1.4 s before the exit: band-passed noise sweeping 350 Hz → 4 kHz.
2. **Impact** on the downbeat: resolved chord stab + crash choke + 808 sub drop + kompang accent.
3. **No fade.** The next element butt-joins; the impact tail rings under it.
4. Final exit gets a longer tail (2.5–3 s) and a full cadence (Am–F–Dm–E7–Am).

## 5. Loudness

| Item | Target | Why |
| --- | --- | --- |
| Integrated | **−16 LUFS** | Brief standard; survives app and social playback |
| True peak | **≤ −1.0 dBTP** | Codec headroom |
| LRA | 3–9 LU | Higher means the voice is fighting the bed |
| Sample rate | 44.1 kHz / 16-bit | Broadcast master for a demo |

Two-pass command (what `master_export.py` automates):

```bash
ffmpeg -i raw.wav -af loudnorm=I=-16:TP=-1:LRA=9:print_format=json -f null -
# then re-run with measured_I / measured_TP / measured_LRA / measured_thresh / offset + linear=true
```

Verify with `ffmpeg -af ebur128=peak=true -f null -` and quote the summary, not the estimate.

## 6. QC thresholds

| Check | Pass |
| --- | --- |
| Dead air | No 0.5 s window below −35 dBFS before the final 3 s |
| Final tail | Ends on decay, not silence or a cut |
| Voice/bed separation | ≥ 6 dB against the ducked bed |
| WAV vs MP3 loudness | Within 0.3 LU |
| ASR | Every scripted line present, in order |
| Clicks | None audible at section joins; exits sit on bar lines |

## 7. Common faults

| Fault | Cause | Fix |
| --- | --- | --- |
| Intro bed vanishes under the ident | pad-only section too quiet | `intro_pad_gain` 2.5–3.0 |
| Music pumps between lines | duck too deep or ramps too short | try 0.40 / 120 ms |
| Voice sounds distant | presence cut, bed not ducked | +2.5 dB @3.4 kHz, verify duck |
| Clipping on the sum | impacts stack on downbeats | peak trim 0.90–0.92, then loudnorm |
| MP3 quieter than WAV | encoder gain | encode from the mastered WAV, re-measure |
