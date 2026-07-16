# Subtask description template — one commit-sized unit

A Subtask is the smallest tracked unit under a Story/Task: **one identifiable
piece of work ≈ one commit** (one new file, one function, one property change,
one refactor step, one test). Voice: technical, terse.

Title: `[<scope>] <the one change>` (imperative, ≤ ~8 words).
E.g. `[aa-core] Add AgentId newtype`, `[test] Add UserRepository CRUD tests`.

## Sections (use these headings)

**Goal** — the single change this Subtask makes.

**Details** — the specific edit: file(s), symbol(s), the exact change. Keep it
to what one commit does; if it needs two sentences of "and also", split it.

**Acceptance criteria** — the change exists, is correct, and its gates pass
(tests/type-check/lint green; repo builds — bisectable at this commit).

## Fields / rules
- **Parent** = the Story/Task it belongs to (set `parent`).
- **Team** inherits from the parent (Jira-enforced) — no need to set.
- **Story points** on Subtasks: the parent Story's points = sum of its Subtask
  points (project convention).
- **Fix version** = same as the parent's target (**next** for dev work).
- One Subtask → one PR/commit; commit style `<gitmoji> (<scope>): <summary>`.

## Verification subtask
Each Story should also get a `Verify <story summary> acceptance criteria`
Subtask that runs the Story's AC and opens Bug subtasks for anything failing.
