# Story description template — user-facing

A Story describes **value delivered to a user or role**. Voice: outcome-first,
from the user's perspective. AC is **user-observable behaviour**, not internal
mechanics.

Title: `[<scope>] <capability the user gains>` (imperative, ≤ ~10 words).

## Sections (use these headings)

**Goal** — one sentence: the user-visible outcome this Story delivers.

**Background / context** — what exists today, what prompted this, links to the
Epic / related tickets / spec.

**For what & for whom** — the user story line:
`As a <role>, I want <capability>, so that <benefit>.`

**Why** — the value/motivation; why now; what it unblocks or fixes for the user.

**Design rationale** — why this approach over alternatives (constraints, trade-offs).

**Design (what it looks like)** — the intended experience/interface: screens,
flows, states, copy, API shape the user or client sees. Link the design spec
(e.g. `agent-assembly/design/…`) for FE work.

**How (approach)** — the solution direction at a level a reviewer can follow
(not line-by-line implementation — that belongs in child Tasks/Subtasks).

**Expected result / artifact** — what will exist when done (feature live,
endpoint available, page shipped) and how to see it.

**Acceptance criteria** — checklist of **user-observable** conditions:
- `Given <context>, when <action>, then <observable outcome>.`
- Include the negative/edge cases that matter to the user.
- FE Stories: reference the design spec + a runtime check (screenshots).

**Out of scope** — explicitly what this Story does NOT cover.

> Decompose implementation into child Tasks/Subtasks (one ≈ one commit) and a
> `Verify <story> acceptance criteria` subtask. Fix version = **next** for dev
> Stories; = **version under test** for verification Stories (see SKILL §5).
