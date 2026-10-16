# Skills

Reusable agent skills by [Theng Hui](https://thenghui.github.io/). Each skill is a plain folder
(`SKILL.md` + optional `references/`, `scripts/`) that works with any AI coding agent that supports
the Agent Skills convention (Claude Code, Codex CLI, GitHub Copilot CLI, Cursor, Gemini CLI, Kiro, …).

## Available skills

### `th-job-ad-employer-reveal`

Reveal the real hiring company and the people behind a recruitment-agency or "confidential client"
job ad (Randstad, Michael Page, Hays, Adecco, Robert Walters, Persol, …). Finds the same or
near-identical ad on other job platforms (JobStreet, LinkedIn, Indeed, Built In, ACCA Careers,
Jooble/JobLeads/Expertini aggregators), matches the ad's text fingerprints against employer-owned
postings and official careers portals (e.g., Workday), then ranks likely employers by probability
and identifies the agency consultant and client-side contact. Writes a ranked verdict to a
`job-ad-reveal-<slug>.md` file.

**Download:** [`th-job-ad-employer-reveal.zip`](th-job-ad-employer-reveal.zip) ·
**Browse:** [`th-job-ad-employer-reveal/`](th-job-ad-employer-reveal/) ·
**Raw SKILL.md:** [`th-job-ad-employer-reveal/SKILL.md`](th-job-ad-employer-reveal/SKILL.md)

**Install & instructions:** [`th-job-ad-employer-reveal/README.md`](th-job-ad-employer-reveal/README.md)
