# Audit trail

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). This describes the *existing* lightweight pattern this Epic
(AAASM-3938 and its prior subtasks AAASM-3939/3940) already follows — it does
not introduce a new or heavier mechanism.

## Goal

AI-performed work should be traceable back to the ticket that requested it,
using the tools already in place (git, GitHub, Jira) rather than a separate
logging system.

## The pattern

- **Commit messages** reference the change's scope via the gitmoji format
  (`<emoji> (<scope>): <summary>`) and land on a branch named with the ticket
  (`<version-or-phase>/<ticket>/<short_summary>`) — the ticket is always
  derivable from the branch a commit lives on.
- **PRs** link the Jira ticket explicitly: the PR title starts with
  `[<ticket>]`, and the PR body's Jira Ticket section links directly to it
  (`https://lightning-dust-mite.atlassian.net/browse/<ticket>`).
- **Jira gets a short comment trail** at the two points that matter for
  anyone reconstructing what happened without reading git history:
  - A "starting work" comment when a worktree/branch is created for the
    ticket (what's being done, which branch).
  - A "PR opened" comment once the PR is up (link to the PR, and — for
    stacked work — which other PRs it depends on).
- For **stacked/dependent tickets** (like this Epic's chain), each PR
  description states what it's stacked on (e.g. "Depends on #25 and #26")
  so the dependency order is visible without reconstructing it from branch
  names.

## What this doesn't require

- No separate audit log, dashboard, or tracking file — git + GitHub + Jira
  are the system of record.
- No additional Jira status transitions beyond what the normal ticket
  workflow already requires.
- No commentary at every intermediate step — the two comments above (start,
  PR opened) are sufficient; don't narrate routine work.
