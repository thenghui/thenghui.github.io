---
layout: default
title: Skills
---

# Skills

Reusable agent skills by [Theng Hui](https://thenghui.github.io/).

## th-job-ad-employer-reveal

Reveal the real employer and hiring contacts behind a "confidential client" recruitment-agency
job ad — cross-platform ad fingerprinting across JobStreet, LinkedIn, Indeed, careers portals
(e.g., Workday), and aggregators.

- 📦 [Download the skill (zip)](th-job-ad-employer-reveal.zip)
- 📄 [Read SKILL.md](th-job-ad-employer-reveal/SKILL.md)
- 📁 [Browse the folder](th-job-ad-employer-reveal/)
- 📝 [Install & usage instructions](th-job-ad-employer-reveal/README.md)

## th-bahasa-malaysia-radio-sweeper-audio-maker

Produce a broadcast-plausible Bahasa Malaysia radio imaging sequence — station ident, sweeper, short ID, TOH opener, promo sting and a transition into music — with a synthetic Malaysian voice (Gemini 3.8 Flash TTS) over a synthesised music bed, then master to −16 LUFS / −1 dBTP and package the WAV/M.

- 📦 [Download the skill (zip)](th-bahasa-malaysia-radio-sweeper-audio-maker.zip)
- 📄 [Read SKILL.md](th-bahasa-malaysia-radio-sweeper-audio-maker/SKILL.md)
- 📁 [Browse the folder](th-bahasa-malaysia-radio-sweeper-audio-maker/)
- 📝 [Install & usage instructions](th-bahasa-malaysia-radio-sweeper-audio-maker/README.md)

### Quick install

Unpack the zip into your agent's skills folder, e.g. Claude Code:

```bash
curl -fsSL https://thenghui.github.io/skills/th-job-ad-employer-reveal.zip -o /tmp/skill.zip \
  && unzip -oq /tmp/skill.zip -d ~/.claude/skills/ \
  && rm /tmp/skill.zip
```

See the [install instructions](README.md) for Codex CLI, GitHub Copilot CLI, Cursor, Gemini CLI
and Kiro folders, plus usage examples.
