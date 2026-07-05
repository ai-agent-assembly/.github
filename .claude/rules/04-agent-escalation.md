# Agent escalation

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). Applies to any AI coding tool working across `ai-agent-assembly`
repos.

## When to stop and ask

An AI agent must stop and ask a human rather than guess when it is:

- **Uncertain** about requirements, scope, or which repo/ticket a change
  belongs to.
- **Blocked** — a precondition can't be verified locally (e.g. CI is
  billing-blocked with no way to confirm a fix), a dependency ticket/PR
  hasn't merged yet, or required credentials/access are missing.
- About to take a **hard-to-reverse action**, including but not limited to:
  - Force-pushing any branch.
  - Deleting a file, branch, or worktree.
  - Dropping or truncating a database table.
  - Pushing or merging directly to a base branch (`master`/`main`).
  - Rewriting git history that's already been pushed/shared.

Guessing on any of the above risks an outcome that can't be cleanly undone —
the cost of a short pause to ask is always lower than the cost of a wrong
irreversible action.

## How to phrase the escalation

State, in order:

1. **What's blocking** — the specific fact that's unclear or unverifiable
   (not "I'm stuck," but "ticket X depends on PR #Y which hasn't merged" or
   "the diff requires force-pushing branch Z").
2. **What was tried** — the investigation already done (files read, commands
   run, branches checked) so the human isn't asked to re-derive context that
   already exists.
3. **What decision is needed** — a concrete question with, where possible, the
   options already narrowed (e.g. "proceed with a stacked PR on the unmerged
   branch, or wait for it to merge first?").

Keep the escalation short and specific — it should be answerable in one
reply, not a request for the human to re-read the whole task.
