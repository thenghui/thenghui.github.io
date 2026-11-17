# Prompt Patterns

Worked transformations and per-mode skeletons. Read the example closest to the current request and
copy its **shape**, not its words.

## The core move

Vague requests fail because they omit one of five things. Add exactly the missing ones.

| Missing | Symptom in the output | Fix in the prompt |
|---|---|---|
| Object | Agent edits the wrong place | Name the file, module, or surface |
| Success test | Agent stops at "looks done" | State an observable check |
| Non-goal | Agent over-builds | One line of "do not…" |
| Constraint | Agent picks a stack you cannot run | Name the version, platform, dependency policy |
| Authority | Agent trusts the wrong input | Say which source wins |

## Before / after

### 1. Feature

**Before**
> add dark mode to the app

**After**
> Add a dark-mode toggle to the settings screen at `src/pages/Settings.tsx`, matching the existing
> theme system in `src/theme/` — do not introduce a second theming approach.
>
> Requirements
> 1. Toggle persists across reloads using the same storage helper the language selector uses.
> 2. Defaults to the OS preference on first visit.
> 3. No flash of light theme on load.
>
> Constraints
> - No new dependencies.
> - Existing components keep their current props; add nothing to the shared component API.
>
> Done when
> - The toggle works, persists after reload, and `npm test` passes unmodified.
>
> [assumed: web app, React, storage helper already exists]

What changed: named the surface, killed the duplicate-theming risk, pinned persistence and the
first-paint behaviour, and gave a runnable check.

### 2. Bug fix

**Before**
> the upload is broken

**After**
> Fix the CSV upload on `/import` returning a 500 for files larger than ~2 MB.
>
> Current behaviour: files under 2 MB import fine; larger ones fail with `PayloadTooLargeError` in
> the server log and the client shows a generic error toast.
> Expected: files up to 20 MB import successfully, and anything over 20 MB shows a clear size-limit
> message instead of a toast.
>
> Scope: `src/api/import.ts` and the upload component. Do not change the CSV parser.
>
> Done when
> - `pnpm test src/api/import.test.ts` passes, including a new case for a 20 MB file.
> - Over-limit files return 413 with a human-readable message.
>
> [assumed: body-size limit is set in this service, not at the proxy]

What changed: turned "broken" into a symptom, a boundary, and an expected result.

### 3. Refactor

**Before**
> clean up the auth code

**After**
> Extract the duplicated token-refresh logic from `src/api/client.ts` and `src/api/admin.ts` into a
> single helper in `src/api/auth/refresh.ts`.
>
> Requirements
> - Pure refactor: no behaviour change, no signature change on either exported client.
> - Both call sites use the new helper; delete the old copies.
> - Keep the existing error messages byte-identical.
>
> Constraints
> - Do not change the retry count, backoff timing, or the refresh window.
> - Do not touch the test files; they must pass as-is.
>
> Done when `pnpm test src/api` passes with zero test edits.
>
> [assumed: exactly two call sites]

What changed: "clean" became an invariant plus a proof of it.

### 4. Review

**Before**
> review my changes

**After**
> Review the uncommitted diff against `main` for correctness bugs only — logic errors, race
> conditions, unhandled error paths, and security-relevant mistakes. Ignore style and formatting;
> tooling owns those.
>
> For each finding: file:line, what breaks, a concrete input or sequence that triggers it, and the
> smallest fix. Rank by severity. If you find nothing blocking, say so plainly rather than padding
> with nits.
>
> Do not modify files.

What changed: scoped the lens, demanded a trigger for every claim, and prevented both padding and
unsolicited edits.

### 5. Writing

**Before**
> write a proposal for the client

**After**
> Draft a one-page proposal for <client>, a mid-size manufacturer evaluating AI training for a
> 40-person operations team.
>
> Purpose: get a 30-minute discovery call, not close a sale.
> Structure: the problem in their terms, what we would do in the first engagement, what we need
> from them, next step.
> Voice: plain, direct, no vendor adjectives, no em-dash-heavy marketing cadence.
> Length: 350–450 words. Markdown, no letterhead.
>
> Do not invent client facts, past results, pricing, or testimonials — leave `<placeholders>` for
> anything you cannot source from what I gave you.

What changed: audience, purpose, structure, voice, length, and an explicit ban on fabrication.

## Per-mode skeletons

### Build

```
Implement <feature> in <location>.
Context: <what exists, why this is needed, decisions already made>.
Follow the pattern in <sibling file/module>; do not introduce a new approach for <concern>.
Requirements: 1) … 2) … 3) …   (numbered, observable)
Constraints: no new dependencies; do not change <invariant>; leave <out of scope> alone.
Done when: <test command> passes, <behaviour> is observable, and you have reported <what>.
If <ambiguity> cannot be resolved from the repo, stop and ask rather than choosing.
```

### Fix

```
Fix <symptom> when <trigger>.
Observed: <exact error, log line, or wrong output>.
Expected: <correct behaviour>.
Repro: <steps or failing test>.
Likely surface: <file/module> — verify before editing.
Scope: change only what the fix requires; do not refactor neighbouring code.
Done when <test or manual check> passes and the failure path is covered by a test.
```

### Review

```
Review <scope: diff/PR/file> for <lens>.
Report only <severity threshold>; label anything softer as nit and keep it to one line.
Each finding: location, defect, triggering condition, smallest fix. Rank by severity.
Do not modify files. Do not restate the code back to me.
```

### Background / unattended

```
<Full task as above>
You are running unattended — nobody can answer questions.
If blocked: stop, leave the work in a state that compiles, and report the blocker plus the options
you considered. Do not guess at missing credentials or external state.
Report back: files changed, tests run and their result, anything you assumed, anything left undone.
```

## Common failure modes to design out

| Failure | Prompt guard |
|---|---|
| Agent rewrites unrelated files | "Change only `<paths>`; leave formatting-only diffs alone." |
| Agent adds a dependency | "No new dependencies; use what is already in `<manifest>`." |
| Agent deletes failing tests | "Tests may not be modified; if a test is wrong, say why instead." |
| Agent invents an API | "Verify every function you call exists in the repo before using it." |
| Agent reports success without checking | "Run `<command>` and paste the tail of its output before you claim done." |
| Agent asks nothing and guesses | "If <known ambiguity> remains, stop and ask." |
| Agent asks everything and does nothing | "Make reasonable choices for details not covered here; list them at the end." |

## Anti-patterns in the prompt itself

- Stacked adjectives with no test ("robust, scalable, production-ready").
- Role-play preamble that costs 100 words and changes nothing.
- Restating the request in different words before stating it.
- Enumerating every file in the repo.
- Threatening tone ("DO NOT FAIL", "THIS IS CRITICAL") — it does not improve compliance.
- A definition of done that the agent can satisfy without changing behaviour.
