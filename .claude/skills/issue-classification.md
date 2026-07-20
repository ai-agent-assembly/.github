# Skill: issue-classification

**When to use:** triaging a new issue or ticket before it gets a repo, an
Epic, or a Subtask assigned — figure out what kind of work it actually is
first.

## 1. Bug, feature, docs, or environment/tooling blocker?

Mirror the distinction this org already draws in `CLAUDE.md`'s CI-reality
note: not every red signal is a product bug.

| Signal | Classification | Action |
|---|---|---|
| Code produces wrong output, crashes, or violates a documented contract | **Product bug** | File as a Bug-type ticket against the owning repo. |
| CI/infra fails for a reason unrelated to the code under test (e.g. GitHub Actions billing-block, a flaky external dependency, a missing local toolchain) | **Environment/tooling blocker** | Do not file as a product bug. Confirm via job annotations or reproduction; note it as infra and validate locally instead of treating it as a code defect. |
| New capability requested that doesn't exist yet | **Feature** | File as a Story (or Subtask if small and unambiguous) with acceptance criteria. |
| Content is missing, wrong, or unclear in docs/README/spec | **Docs** | File as a docs-type ticket against the repo that owns that content (see `choose-repo` — usually `agent-assembly-docs`/`inner-document`, or the monorepo for the Protocol Specification). |

If unsure whether something is a genuine product bug versus an environment
artifact, reproduce it locally before filing — don't file from CI logs alone.

## 2. Which repo/component?

Use the `choose-repo` skill. Set the ticket's Component field
(Jira's native `components` field) to the owning repo — this is a 1:1 mapping and other
skills/agents rely on it being accurate.

## 3. Epic or standalone?

- **Needs an Epic** when the work is part of a larger initiative already
  tracked (check for an existing Epic in the same problem space before
  creating a new one), or when it will require multiple Stories/Subtasks
  across more than one PR.
- **Standalone** (a single Story or even a single Subtask with no parent
  Epic) when the fix is small, self-contained, and unlikely to spawn related
  follow-up work — e.g. a single-file bugfix or a doc correction.
- When several related bugs surface from the same root cause (e.g. the same
  class of bug found in multiple repos during a sweep), consider grouping
  them under one Epic rather than filing fully independent tickets — makes
  the pattern visible instead of scattered.

## 4. File it

Once you know the **type**, the **repo/component**, and **Epic-or-standalone**,
author the ticket with the `ticket-authoring` skill — it covers the short
intent-carrying title, the type-correct description schema (Story = user-facing,
Task = technical, Bug = expected/actual/repro/env), the required fields
(Components, Labels, Assignee, Story points, Team, Fix version, Start/Due), and
the **Fix-version rule** (development work targets the *next* version).

## Do not

- Do not file an environment/infra failure as a product bug — it pollutes
  the bug backlog and produces misleading trend data.
- Do not create a new Epic when an applicable one already exists — search
  first.
- Do not leave the Component field unset "to decide later" — set it at
  triage time, even if it's a best guess that gets corrected.
