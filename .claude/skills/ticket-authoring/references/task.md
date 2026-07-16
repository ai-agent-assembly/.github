# Task description template — developer / technical-facing

A Task is a **technical unit of work for a developer**. Voice: precise and
implementation-oriented. AC is **verifiable/technical**, not user-observable.
(If the thing is best described as value to a user/role, use a Story instead.)

Title: `[<scope>] <technical change>` (imperative, ≤ ~10 words).

## Sections (use these headings)

**Goal** — one sentence: the technical outcome (what the codebase/system will
have that it doesn't now).

**Background** — current state of the relevant code/system, links to the parent
Story/Epic, spec, or prior tickets.

**Technical purpose** — what this enables or fixes at the system level (the
"for what", stated technically).

**Why** — why it's needed now, what it unblocks, cost of not doing it.

**Design decision** — the chosen approach and *why over alternatives*:
data model, module boundaries, interface/signature, invariants to preserve.

**Implementation approach (how to implement)** — concrete steps: files/modules
to touch, functions/types to add or change, migration/rollout, feature flags.
Keep it reviewable; split into Subtasks (one ≈ one commit) if large.

**Expected artifact** — the deliverable: new module/function/endpoint/config,
migration, CI job, etc.

**Acceptance criteria** — **verifiable technical** conditions:
- `<function/endpoint> behaves as <spec>` with the exact contract.
- Tests: new/updated tests pass; regression test for any fix.
- Gates: type-check, lint, build, relevant CI green.
- No behaviour change outside the stated scope.

**Out of scope** — what this Task deliberately does not change.

> Fix version = **next** version (code ships in the next cut; you branch off the
> current base but release forward). See SKILL §5.
