# Bug description template — defect report

A Bug reports **observed incorrect behaviour**. Voice: factual and
reproducible. The reader must be able to reproduce it and know when it's fixed.

Title: `[<scope>] <the wrong behaviour>` (imperative/symptom, ≤ ~10 words).
E.g. `[dashboard] Policy panel throws on empty date range`.

## Sections (use these headings)

**Summary** — one sentence: what's wrong and where.

**Expected result** — what *should* happen (the correct behaviour).

**Actual / current result** — what happens instead. Quote exact error
text/stack/log lines verbatim; attach screenshot for UI defects.

**Reproduction steps** — numbered, minimal, deterministic:
1. …
2. …
3. → observe <wrong result>

**Test environment** — the conditions the bug was seen under:
- OS + version · Browser + version (for FE) · App/build/release version
  (e.g. rc.5) · SDK/runtime version · relevant config/flags · data/account state.

**Impact / scope** — who/what is affected, severity, frequency (always / race /
specific inputs), any workaround. Set the native `priority` to mirror the
verified `sev-*` label (High/Medium/Low) — see the priority↔severity rule in
`estimation-and-labels.md`.

**Root cause** — fill once known (which code, why); link the offending
line(s)/commit.

**Acceptance criteria** — how "fixed" is proven:
- The reproduction steps now yield the **expected result**.
- A **regression test** covers the case and fails on the old code.
- No new defect introduced; relevant gates green.

**Regression risk / related** — nearby behaviour to re-check; linked tickets.

> Fix version = **next** version — the fix ships in the next release, even if the
> bug was found while verifying the current one. A verification Epic therefore
> mixes under-test Stories with next-version Bugs. See SKILL §5.
