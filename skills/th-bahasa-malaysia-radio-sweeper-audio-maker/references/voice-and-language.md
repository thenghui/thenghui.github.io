# Voice and language

## 1. How Gemini 3.8 Flash TTS reads your script

| Field | What it does | What it must not contain |
| --- | --- | --- |
| `text` | Verbatim transcript | Stage directions, parentheticals, "say this warmly" |
| `speech_metadata.style` | Sustained tone across the whole turn | Age, gender, accent, names — those are voice-design traits |
| Inline tags in `text` | Point-in-time pauses, breaths, reactions | Sound effects; only human vocalisations work |

Tags that are safe and useful for imaging: `<short pause>`, `<long pause>`, `<breath>`,
`<sigh>`, `<chuckle>`, `<throat-clearing>`.

The guide is explicit: **long persona paragraphs in `style` cause voice drift**. Design the
persona once, then keep every `style` string to 3–8 words.

## 2. Designing the persona

The persona prompt should describe only traits that never change:

> *A warm, friendly 30-year-old Malaysian English speaker with a natural Manglish-influenced
> cadence, gentle pitch, and casual conversational tone.*

For a native-BM presenter instead:

> *A confident Malaysian radio presenter in her early 30s, native Bahasa Malaysia speaker from
> the Klang Valley, warm chest tone, relaxed street-smart delivery, never formal.*

Set `language_code` deliberately:

| Persona language | `language_code` | Result on a BM script |
| --- | --- | --- |
| Malaysian English | `en-MY` | BM words with English-influenced rhythm — the Manglish read |
| Native BM | `ms-MY` | Conventional BM broadcast cadence |
| Indonesian | `id-ID` | Wrong vowel colour for Malaysia; avoid unless briefed |

`gender` is a required decision. If the brief does not state one, choose, then **record the
assumption in `credits.md`**.

## 3. Manglish without caricature

Use particles where a Kuala Lumpur speaker actually uses them. One or two per read, not five.

| Particle | Function | Example |
| --- | --- | --- |
| `lah` | softener, emphasis | "Sama la kita." |
| `kan` | seeking agreement | "Korang tengah drive, kan?" |
| `tau` | intimacy, "you know" | "Jangan miss, tau!" |
| `jom` | invitation | "Jom, layan." |
| `memang` | affirmation | "Memang ngam dengan pagi korang." |
| `giler` | intensifier (youth) | "Lagu dia giler best." |
| `korang` | second person plural | "Ini station korang." |

English nouns that Malay radio actually code-switches: *drive*, *miss*, *update*, *traffic*,
*single*, *hit*. Do not translate these into textbook BM — it reads like a government ad.

Avoid: `anda` (stiff, distance), full formal syntax, and stacking three particles in one clause.

## 4. Style strings that work

| Element | Style string |
| --- | --- |
| Station ident | `warm, smiling, casual radio delivery` |
| Sweeper | `friendly and conversational, like talking to a friend in the car` |
| Short ID | `bright, casual and confident` |
| TOH / opener | `warm and energetic, natural Malaysian conversational cadence` |
| Promo | `playful and inviting, conversational` |
| Final tag | `warm, gentle and smiling` |

Reuse the exact same string every time you regenerate that element, so a rebuild sounds like the
first pass.

## 5. Pronunciation and phrasing pitfalls

- **Station names with initials** are usually spelled out by the model: "Hot FM" → "Hot EFF-em".
  Check the sample; if it says "Hot fm" as a word, respell phonetically in `text` (`Hot Ef Em`)
  and keep the written form in the script document.
- **Numbers**: write "lapan pagi", not "8 pagi", when you want the Malay word. The model may
  read digits in English.
- **Acronyms in BM** (TOH, DJ, MV) are read as English letters — acceptable on Malaysian radio.
- **"Live"** is ambiguous; write "laif" if you need the English pronunciation.
- **Sibilance** rises with `bright` styles; if it hisses, drop presence EQ by 1 dB rather than
  changing the performance.

## 6. Consistency checklist

- [ ] One `voice_...` ID across every line
- [ ] Same `style` string per element across rebuilds
- [ ] No second voice unless the brief explicitly asks for a dialogue
- [ ] Sample auditioned before spending quota on six lines
- [ ] Voice ID, model name and persona prompt recorded in `treatment.md`
