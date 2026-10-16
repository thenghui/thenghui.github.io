---
name: th-job-ad-employer-reveal
description: "Reveal the real hiring company and the people behind a recruitment-agency or 'confidential client' job ad (Randstad, Michael Page, Hays, Adecco, Robert Walters, Persol, etc.). Finds the same or near-identical ad on other job platforms (JobStreet, LinkedIn, Indeed, Built In, ACCA Careers, Jooble/JobLeads/Expertini aggregators) and matches the ad's text fingerprints against employer-owned postings and official careers portals (e.g., Workday), then ranks likely employers by probability and identifies the agency consultant and client-side contacts. Use when given an agency job-ad URL or screenshot and asked who the real company / hiring person is, to find duplicates or similar ads of a job on other platforms, or to shortlist candidate employers. Not for applying to jobs, résumé/CV writing, salary benchmarking, or creating job ads."
metadata:
  short-description: Agency job ad → real employer + hiring contacts via cross-platform ad fingerprinting
---

# TH Job-Ad Employer Reveal

De-anonymise a "confidential client" recruitment ad: which company is really hiring, where the same
job is advertised elsewhere, and who the humans are on both sides.

## Success condition

A ranked verdict (highest → lowest probability) containing:

1. **Real employer** — backed by a verbatim/near-verbatim text match to a client-owned posting
   (official careers portal, company-branded job-board ad) or an equally strong anchor set;
2. **Evidence links** — the specific ads on other platforms that prove it;
3. **People** — agency consultant (named on the ad) + client-side hiring contacts found or inferred;
4. **Ruled-out candidates** — near-miss ads/employers, so the user sees what was excluded and why.

Write the final output into a Markdown file (see step 6) and also present it in the chat.

Never assert an employer from vibes: require **≥2 independent anchors** and show a quote-comparison
table. A single shared buzzword stack (SAP S/4HANA, SOX…) is weak; a matched sentence is strong; a
matched *closing line* or "about the company" blurb is near-conclusive.

## Workflow

### 1. Capture the ad verbatim

Fetch the full ad text (plain fetch first; a real browser for Cloudflare-protected boards). The
paraphrase trick is that the agency rewrites the client's JD — exact fragments survive in both, so
you need the complete text, not a summary.

### 2. Extract fingerprints

- "About the company" blurb (footprint claims: "rapidly expanding", "Asia and Europe", …)
- Unique sentences and the **closing apply line** ("If you're ready to grow with one of the
  fastest-moving companies in …")
- Buzzword stack: full-set accounting, month-end close, IFRS/US GAAP, SOX, SAP S/4HANA, Big 4/MNC,
  multi-entity / multi-currency
- Salary band, reference number, posted/closing dates
- Consultant name / phone (the person to call — capture the phone digits exactly)

### 3. Exact-phrase hunt

Search the most distinctive fragments **in quotes**:

- Best: DuckDuckGo **in a real browser** — `https://duckduckgo.com/?q=%22<exact+sentence>%22`;
  its `site:` operator works.
- Also try `"<job title>" "<candidate company>"` and `site:linkedin.com/jobs "<title>" "<company>"`.
- Google = CAPTCHA for automation; Bing ignores `site:`/quotes in practice; server-side DDG/curl
  often blocked. If the runtime has a `web_search` tool, use it for discovery — but re-verify every
  cited page yourself before trusting it.

### 4. Platform sweep

Check each platform for client-owned ads (see `references/platform-playbook.md` for URLs, access
quirks, extraction recipes):

| Platform | What it reveals |
|---|---|
| Client careers portal (often Workday: `<tenant>.wdN.myworkdayjobs.com`) | **The employer itself** — the agency ad is usually a rewrite of one of these reqs |
| JobStreet / SEEK (`my.jobstreet.com`) | Client-owned ads under the company profile; job pages show employer, salary, "Employer questions" |
| LinkedIn jobs | Client-owned postings (auth-walled search; reach via DDG `site:`; `/jobs/view/<id>` pages sometimes fetchable directly) |
| Indeed (`malaysia.indeed.com`) | Search list shows employer names; `/viewjob` often bot-blocked |
| Built In / association boards (ACCA Careers, eFinancialCareers) | Full JD text (great for phrase matching); association boards often carry the **agency's** copy incl. salary + reference no. |
| Aggregators (Jooble, JobLeads, Expertini, Talent.com, foundit, Maukerja) | Sometimes leak the client name **in the ad title** — check before discounting |

Match on three axes: near-verbatim phrase(s) + company self-description vs the ad's "about the
company" + posting-date proximity ("Posted 2 days ago" ≈ fresh campaign).

### 5. People hunt

- **Agency side:** the consultant name/phone on the ad → search `"<phone>"` and
  `"<name>" <agency> linkedin`.
- **Client side:** ads rarely name the hiring manager. Find the hiring function's leadership via
  DDG `site:linkedin.com/in "<company>" <finance|HR> <city>`, company press releases (launch stories
  name CEOs/country GMs), and careers-page "Introduce Yourself" / TA contacts.
- Recommend the user ask the consultant "is this the <Company> <hub> role?" — consultants confirm
  for serious candidates.

### 6. Report (ranked)

Write the final output into a Markdown file in the working directory — name it
`job-ad-reveal-<slug>.md`, where `<slug>` is the real employer (or the job title if the verdict is
unconfirmed) — then summarise the verdict in the chat with a link to the file. The file contains,
in this order:

1. **Verdict** — real employer + confidence + the quote-comparison table (agency ad vs client ad).
2. **Ad list, ranked** — platform → ad title/URL → match score (10/10 = same ad; 9/10 = same JD text,
   sibling req; 8/10 = same team/hub; ≤7/10 = same industry).
3. **People** — consultant (name, phone, LinkedIn) + client-side contacts.
4. **Ruled out** — distractors with one-line reasons.
5. **Caveats** — what couldn't be verified (auth-walled sources, timing assumptions).

## Gotchas learned in the field

- JobStreet, Jooble and Indeed-viewjob are **Cloudflare-protected** — curl/web_fetch get 403/410;
  drive a real browser instead, then close/restore the tabs you opened.
- The same ad on another board with the **agency** as employer (e.g., ACCA Careers showing
  "Randstad Malaysia") is syndication, NOT client reveal — but it yields salary + agency reference numbers.
- The killer move: the **client's own careers portal** (Workday) contains the same JD the agency
  paraphrased — keyword-search the portal and compare sentences.
- Watch for title collisions: competitors in the same industry post similar-looking roles with
  different wording — only near-verbatim matches count as evidence.
- Timing is an anchor: "posted 2 days ago" on the client portal vs a fresh agency campaign.
- Public sources only; never bypass logins or ToS.

## Files

- `references/platform-playbook.md` — per-platform recipes (URLs, access method, extraction, what it reveals).
- `scripts/extract_job_cards.js` — drop-in browser `evaluate_script` to pull job cards (title/company/location/link) from SEEK/JobStreet-style and generic list pages.
- `scripts/reveal_batch.sh` — batch runner (macOS-friendly bash): feed a list of agency job ads (one per line — URL, saved ad-text file, or free text with an optional `| note`) and it runs one headless Copilot agent per ad, then aggregates the verdicts into a table. Per ad it writes `ad.md`, `report.md`, `result.json`, `prompt.md`, `agent.log`, `session.md`; batch-wide it writes `summary.md` + `summary.csv` with top employer, client PIC and contact details. Usage:
  ```bash
  scripts/reveal_batch.sh --check                        # prerequisites
  scripts/reveal_batch.sh -i ads.txt -o reveal-out       # one ad after another
  scripts/reveal_batch.sh -i ads.txt -o reveal-out -j 3  # 3 ads in parallel
  scripts/reveal_batch.sh -i ads.txt -o reveal-out --batch   # single --fleet run
  ```
