# Epic description template — rollup

An Epic groups related Stories/Tasks/Bugs toward one larger goal. Voice:
strategic; the "why" and the shape, not implementation detail.

Title: `<goal in a phrase>` (short; no `[scope]` needed, or use a broad area).

## Sections (use these headings)

**Goal** — the overarching outcome; the single sentence success looks like.

**Scope** — what's in and what's out at the Epic level; the repos/areas touched.

**Background / context** — motivation, prior work, spec/ADR links, constraints
and decisions that bound the children.

**Success criteria** — measurable, Epic-level "done": the thresholds/outcomes
all children collectively achieve.

**Child breakdown** — the Stories/Tasks/Bugs (or a plan for them), ideally a
small table. Note ownership per repo/component.

**Version plan** — which release(s) the work targets. **A verification/test Epic
may span versions**: its verify-Story children carry the *under-test* version,
its Bug children carry *next*. A development Epic is single-version (next).

**Risks / dependencies** — cross-ticket or cross-repo ordering, external blockers.

## Fields
- No **Story points** field on Epics (rolls up from children — sum the children).
- **Components** = all repos the Epic spans (multi-value).
- **Fix version** = the primary target version; individual children may differ
  per the version plan above.
