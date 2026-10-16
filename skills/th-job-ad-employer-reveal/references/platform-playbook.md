# Platform Playbook — where the real client leaks

Concrete, battle-tested recipes for `th-job-ad-employer-reveal`. Verified against real
Malaysian/EU job boards (Oct 2026).

## Search engines

| Engine | Verdict |
|---|---|
| DuckDuckGo in a **real browser** (`https://duckduckgo.com/?q=...`) | **Best.** Quotes + `site:` work. This is the default. |
| `html.duckduckgo.com` / curl | Blocked (anti-bot code page). |
| Google | CAPTCHA for automation (`/sorry/index`). Don't waste turns. |
| Bing (browser **or** curl `&format=rss`) | Effectively ignores `site:` + quotes; returns junk. Avoid. |
| `web_search` tool (if the runtime has one) | Good for discovery + citations; ALWAYS open the cited pages yourself — the synthesis can overstate. |

Exact-phrase searches that paid off: `"Senior Accountant (Data Center)"` (found the ACCA syndication
copy), `site:linkedin.com/jobs <company> "<title>"` (found repeating client postings),
`site:linkedin.com/in` variants (found TA/consultant people).

## JobStreet / SEEK Malaysia (`my.jobstreet.com`)

- Keyword search: `https://my.jobstreet.com/jobs?keywords=<kw>&where=<city>`
- Slug search (canonical): `https://my.jobstreet.com/<keywords-slug>-jobs/in-<Location>`
- Company profile: `https://my.jobstreet.com/companies/<slug>` → "Jobs" tab = the client's **own**
  ads (this is the reveal surface).
- Job page: `https://my.jobstreet.com/job/<id>` → employer name, salary, posted age, "Employer
  questions", company profile link.
- **Access:** curl → 308 redirect → 403 Cloudflare. Must use a real browser (chrome-devtools /
  Playwright MCP). Extract with `scripts/extract_job_cards.js` (avoids 50 KB snapshots).
- Note: agency ads are often NOT mirrored here even when the agency advertises elsewhere;
  the client's direct ads on JobStreet are the prize.

## LinkedIn

- `/jobs/search` → authwall (login required). Don't fight it.
- Public `/jobs/view/<id>` pages: **sometimes readable with a plain fetch** — full JD text comes
  back (verified). Try before giving up.
- Discovery via DDG: `site:linkedin.com/jobs "<job title>" "<company>" Malaysia` and
  `site:my.linkedin.com/jobs "<title>" "<company>"`.
- People via DDG: `site:my.linkedin.com/in "<company>" <function>` /
  `site:linkedin.com/in "<company>" "talent acquisition"`.

## Indeed (`malaysia.indeed.com`)

- Search: `https://malaysia.indeed.com/jobs?q=<kw>&l=<city>` — the results list shows the employer
  ("View all <Employer> jobs") and clusters a company's roles; readable in a browser
  (and sometimes via plain fetch).
- `/viewjob?jk=<id>` frequently hits bot walls (`secure.indeed.com/auth`, Cloudflare "Just a
  moment...") — rely on the search list and cross-board copies instead.

## Workday career portals — the jackpot

- Tenant pattern: `https://<tenant>.wdN.myworkdayjobs.com/<site>` (find the link on the company's
  careers page, e.g. "Search Open Roles").
- Keyword search: `.../<site>?q=accountant` — lists titles, locations, "Posted X Days Ago", req IDs.
- Job page: `.../job/<Location>/<Title>_<ReqID>` — full JD. Compare sentence-by-sentence with the
  agency ad; near-verbatim matches + matching req recency ("Posted 2 Days Ago") = conclusive.
- Also check "Similar Jobs" on the page and the About-the-company blurb at the bottom.

## Association / niche boards

- **ACCA Careers** (`jobs.accaglobal.com`): agencies syndicate the *complete* ad copy including
  salary, agency reference number (e.g. `91M0271684`), posted + closing dates. Employer shown =
  agency — not a client reveal, but metadata gold.
- Also check: `efinancialcareers.my`, `michaelpage.com.my`, `hays.com.my`, `robertwalters.com.my`,
  `adecco.com.my` for duplicates of the same mandate by other agencies.

## Aggregators (often leak the client in the TITLE)

- **Jooble** (`my.jooble.org`): titles often formatted "… at <Company> – <City> – Apply Now!" —
  leaked the client name in our case. Cloudflare "Just a moment..." in browser may or may not pass.
- **JobLeads** (`jobleads.com/my/job/...`) — check titles.
- **Expertini** (`<city>.my.expertini.com/jobs/...`) — public, mirrors many boards incl. LinkedIn-sourced.
- Others: Talent.com, Trovit, Careerjet, foundit.my (ex-Monster), Maukerja.
- Treat aggregator hits as **leads**; confirm on the client-owned posting before ranking high.

## Press / news (for people)

- Launch/investment stories name executives (CEO, Country GM) — useful client-side contacts.
  E.g. The Star / Business Times / TechNode covered DayOne's Johor + KL hub expansion.

## Browser hygiene

- Use the chrome-devtools / Playwright MCP when available; batch navigations to independent pages in
  parallel; extract via `evaluate_script` returning small JSON instead of full snapshots (snapshots
  can be 50 KB+ and get truncated).
- Parallel `close_page` calls can race — list pages again after closing, then finish cleanup.
- Close every tab you opened and restore the originally selected page.
