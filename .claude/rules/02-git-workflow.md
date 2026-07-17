# Git workflow

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). Applies across all `ai-agent-assembly` repos.

## Branch naming

```
<version-or-phase>/<ticket>/<type>/<short_summary>
```

- `<version-or-phase>` — the milestone/sprint identifier (e.g. `v0.1.0`,
  `phase1`).
- `<ticket>` — the exact Jira ticket reference (e.g. `AAASM-3941`).
- `<type>` — the change category: `feat`, `fix`, `refactor`, `test`, `docs`,
  `config`, `deps`, `remove`, or `lint`.
- `<short_summary>` — 2-4 words in `snake_case`, max ~30 characters.

Example: `v0.1.0/AAASM-3941/docs/design_claude_rules`.

## Worktrees

- One git worktree per ticket, so the main checkout stays clean and multiple
  tickets can be developed concurrently without branch-switching.
- If the ticket **depends on** another ticket whose branch hasn't merged yet,
  stack your worktree's branch on top of that dependency's branch (`git
  worktree add -b <new-branch> <path> <dependency-branch>`) instead of the
  default branch. Otherwise, branch from the latest default branch.
- Remove the worktree after the PR merges.

## Commits

- Atomic: one logical unit of work per commit (one new file, one function,
  one property change). If it takes two sentences to describe, split it.
- Gitmoji format: `<emoji> (<scope>): <imperative summary>` — see each repo's
  `CONTRIBUTING.md` for the GitEmoji reference table.
- The repository must build/pass at every commit (bisectable) — don't split a
  commit in a way that leaves it broken.

## Merges

- **Never push directly to the base branch** (`master`/`main`) — all changes
  land through a PR, even trivial ones.
- Never merge your own PR locally and push the merge; let the platform's PR
  merge do it, after required approval.

## Pull requests

- Title: `[<ticket>] <emoji> (<scope>): <summary>`.
- Body follows the repo's `.github/PULL_REQUEST_TEMPLATE.md` structure
  exactly — don't freelance a different layout.
- Base branch is always the repo's default branch, even if your branch was
  stacked on another feature branch — call out the stacking/dependency in the
  PR description so reviewers know what else needs to merge first.
