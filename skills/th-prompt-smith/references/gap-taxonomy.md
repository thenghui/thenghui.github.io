# Gap Taxonomy

The candidate questions, by mode. Use this to decide **what** might be missing, never as a
checklist to march through — most entries must resolve to a default instead of a question.

## Ranking rule

For each candidate gap, ask: *would two plausible answers produce materially different prompts?*

- **Yes, and the wrong guess wastes the agent's whole run** → ask it.
- **Yes, but the agent can recover cheaply** → default it, mark `[assumed: …]`.
- **No** → do not ask, do not mark, leave it out.

## Universal gaps

| Gap | Why it changes the prompt | Default when unanswered |
|---|---|---|
| Deliverable | Determines the entire output contract | Ask — this is never worth assuming |
| Definition of done | Without it the agent stops at "looks right" | Ask, or default to "existing tests pass, no new lint errors" |
| Non-goals | Agents over-build by default | Default to "no unrequested features or dependencies" |
| Audience | Changes depth, tone, jargon | Default to the user themselves |
| Authority of inputs | Decides whether to trust a file, a doc, or memory | Default to "the repo is the source of truth" |

## Build

- Stack and versions — default: infer from the repo; ask only if the repo is empty or mixed.
- Target location — default: wherever the analogous code already lives.
- Existing patterns to follow — default: nearest sibling module.
- Test policy — default: mirror the file's neighbourhood; ask only if the repo has no tests at all.
- Data model or schema changes — worth asking when it implies a migration.
- Auth, secrets, external services — worth asking, since guessing invents unavailable
  infrastructure.
- Definition of done — ask unless the request already states observable behaviour.

## Fix

- **Exact symptom** — ask. "Broken" is not a request.
- **Reproduction steps** — ask if absent; without a repro the agent will guess.
- **Expected vs actual** — ask; this is the single highest-value fix question.
- **Full error text** — ask if the user only summarised it.
- **When it last worked** — default to "unknown; assume it never worked".
- **Blast radius** — default to "minimal; do not refactor surrounding code".
- **Failed attempts** — ask only if the user volunteers a history; otherwise leave the agent free.

## Change (refactor / migrate / upgrade)

- **Invariants** — ask. Which behaviour must be bit-identical?
- **Compatibility surface** — default to "no public API change".
- **Migration strategy** — default to "all at once, in one commit, tests green".
- **Rollback** — default to "revert the commit"; ask only for data migrations.
- **Scope boundary** — default to "only the named module".

## Review

- **What to review** — ask if not obvious: diff, PR, whole file, design.
- **Lens** — default to correctness and bugs, not style.
- **Severity rubric** — default to "report only issues you would block a merge for, plus explicitly
  labelled nits".
- **Explicit ignores** — default to "ignore formatting handled by tooling".

## Research / write

- **Audience and purpose** — ask; single biggest determinant of the output.
- **Depth and length** — default to the shortest form that answers the question.
- **Tone and voice** — default to the user's own register from the conversation.
- **Sources** — ask only if citations are required.
- **Structure** — default to the conventional shape for the artifact.
- **Recency** — ask if the answer decays (prices, versions, policies).

## Decide

- **The options on the table** — ask if the framing is open-ended.
- **Criteria and weights** — ask; "best" is meaningless without it.
- **Constraints** — budget, time, team size, existing commitments.
- **Reversibility** — default to "prefer the reversible choice".
- **Appetite for risk** — default to the user's demonstrated conservatism.

## Anti-questions

Never ask these:

- "Can you give me more details?" — no information, all cost.
- "What are your requirements?" — shifts your work back to the user.
- "Shall I proceed?" — a permission request, not a gap.
- "Do you want it to be good?" — implies a choice nobody would make.
- Anything whose answer is a filename the agent will open in its first tool call.

## Escalation

If after three answers the request is still ambiguous in a way that changes the deliverable, stop
asking. State the ambiguity in one sentence, propose the narrowest interpretation that is still
useful, and build the prompt around it with `[assumed: …]`. A slightly wrong-but-explicit prompt
beats a fifth question.
