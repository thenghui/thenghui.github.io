# th-job-ad-employer-reveal

Reveal the real hiring company and the people behind a recruitment-agency or "confidential client"
job ad (Randstad, Michael Page, Hays, Adecco, Robert Walters, Persol, …).

The skill fetches the ad, extracts text fingerprints, finds the same or near-identical ad on other
job platforms (JobStreet, LinkedIn, Indeed, Built In, ACCA Careers, Jooble/JobLeads/Expertini
aggregators), matches them against employer-owned postings and official careers portals (e.g.,
Workday), then returns a ranked verdict per employer plus the agency consultant and client-side
contacts. The final report is written to `job-ad-reveal-<slug>.md`.

**Download:** [`th-job-ad-employer-reveal.zip`](https://thenghui.github.io/skills/th-job-ad-employer-reveal.zip) ·
**Source:** [`th-job-ad-employer-reveal/`](https://github.com/thenghui/thenghui.github.io/tree/main/skills/th-job-ad-employer-reveal)

## Install

Unpack the zip into the folder your agent loads skills from:

| Agent | Skills folder |
|---|---|
| Claude Code | `~/.claude/skills/` |
| OpenAI Codex CLI | `~/.codex/skills/` |
| GitHub Copilot CLI | `~/.copilot/skills/` |
| Cursor | `~/.cursor/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Kiro | `~/.kiro/skills/` |

One-liner (swap the destination folder for your agent):

```bash
curl -fsSL https://thenghui.github.io/skills/th-job-ad-employer-reveal.zip -o /tmp/skill.zip \
  && unzip -oq /tmp/skill.zip -d ~/.claude/skills/ \
  && rm /tmp/skill.zip
```

Verify:

```bash
head -20 ~/.claude/skills/th-job-ad-employer-reveal/SKILL.md
```

Alternatively, download the zip in a browser and unzip it into the folder above, or just tell your
agent: *"Install the skill from https://thenghui.github.io/skills/th-job-ad-employer-reveal.zip into
your skills folder."*

Some agents also load project-scoped skills — copy the folder into your project's skills folder
(e.g. `.claude/skills/`) instead if you prefer per-project installs.

## Use

Start a new agent session and paste the agency job-ad URL (or a screenshot):

> Who is the real employer behind this recruitment-agency job ad, and who are the hiring contacts? &lt;URL&gt;

Other things to ask:

- "Find the same or similar ads for this job on other platforms."
- "Shortlist the candidate employers, ranked by probability."
- "Who is the named consultant on this ad, and can I find their LinkedIn?"

The agent returns a ranked verdict plus a `job-ad-reveal-<slug>.md` report. Public sources only —
it never bypasses logins or paywalls.

## Notes

- No API keys or special setup needed for the core workflow; the agent's own web access does the work.
- Not for: applying to jobs, résumé/CV writing, salary benchmarking, or creating job ads.
- The optional `scripts/reveal_batch.sh` batch runner needs the GitHub Copilot CLI (headless) and
  `python3` (or `jq`); the browser helper `scripts/extract_job_cards.js` is pasted into the agent's
  browser tools.
- Re-download the zip to pick up the latest version.
