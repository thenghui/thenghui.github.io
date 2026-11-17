# TH Prompt Smith

Turn a rough request into a **precise, copy-paste-ready prompt** for a coding or other AI agent.

The gap between a vague prompt and a good one is usually one or two facts only you hold. This skill
asks exactly those questions — one at a time, with your best guess offered as the default — then
rewrites the request into a prompt that a fresh agent can act on without a round trip.

## When to use it

- You have a one-liner ("add auth to the app", "clean up the auth code") and want it to land first
  time.
- You are briefing a coding agent, subagent, background agent, or another model.
- An agent keeps misunderstanding you and you want to fix the brief, not the agent.
- You want a prompt that works for writing, research, review or a decision — coding is one mode.

Do not use it to execute the task. This skill only produces the prompt.

## What it does

1. **Reads the request as an agent would** — one line: `Deliverable: <artifact> for <who>, because <why>`.
2. **Asks the minimum** — only questions where two answers would produce materially different
   prompts. Budget 1–3, hard ceiling 5, one question per turn, with a default offered so "yes"
   is a valid reply.
3. **Enriches** — role, task, context, inputs, numbered requirements, constraints and non-goals,
   output contract, definition of done, escalation rule.
4. **Delivers** — one fenced block you can copy, plus `Assumed:` / `Added:` lines so you can see
   what it inferred.

A precise request gets zero questions. "You decide" ends probing.

## Quick start

Ask your agent:

> Use th-prompt-smith on this: "add dark mode to the app"

Or name the destination so the framing matches:

> Use th-prompt-smith to brief a background agent: "migrate the settings page to the new API"

## What you get back

```text
Implement basic authentication in the current app. Inspect the repository first and use it as the
source of truth for the stack, architecture and validation commands.

Requirements
1. Add sign-up, sign-in and sign-out, and protect the existing private routes.
2. Use an already-configured auth provider if one exists; never invent credentials or policies.
3. Add focused tests following nearby conventions and run the relevant checks.

Constraints: keep changes scoped to authentication; no roles, SSO or MFA; no new dependencies
without explanation; do not commit.

Done when the auth flows work, private routes reject unauthenticated users, and the checks pass.

You are unattended. If the repository does not establish a safe auth approach, do not guess —
leave the work compiling and report the blocker.
```

Then:

```text
Assumed: individual accounts; sign-up included; existing private routes are the protection target
Added: repository-first discovery, security constraints, verification step, unattended stop rule
```

## Design discipline

- **Never invents facts** — no file paths, versions, API names or metrics you were not given;
  `<angle-bracket placeholders>` and a `Still open:` line instead.
- **Never widens scope** — precision, not extra features.
- **Length matches difficulty** — 60–120 words for a one-liner, up to 600 for high-stakes work. No
  generic filler like "write clean code".

## References

- `references/gap-taxonomy.md` — candidate gaps per mode (build / fix / change / review /
  research / decide), ranked by whether two answers would change the prompt.
- `references/prompt-patterns.md` — worked before/after examples, per-mode skeletons, and the
  failure modes each guard is designed to prevent.
