# Skill: contribution-guide

**When to use:** you've completed `task-intake` and `setup-dev-env` and are
ready to implement and land a change in any `ai-agent-assembly` repo.

## Flow

1. **Worktree.** Develop the ticket in a dedicated git worktree branched off
   the latest default branch (or off a dependency's branch, if stacked — see
   `task-intake`), so the main checkout stays clean and multiple tickets can
   be worked concurrently. Remove the worktree after the PR merges.
2. **Implement.** Change only what the ticket describes. Read the target
   repo's `.claude/CLAUDE.md` for architecture constraints before touching
   unfamiliar code.
3. **Commit atomically.** One logical unit per commit — one new file, one
   function, one property change. Format:
   ```
   <emoji> (<scope>): <imperative summary>
   ```
   (gitmoji.dev conventions; see `CLAUDE.md` for the emoji table). Each
   commit should be independently understandable and the repo should build
   at every commit (bisectable). Never bundle a feature with a refactor of
   surrounding code, and never bundle new code with its own tests in the
   same commit — tests are their own commit.
4. **Push to the canonical remote** — confirmed in `setup-dev-env`, not
   assumed to be `origin`.
5. **Open a PR using the repo's PR template** (`.github/PULL_REQUEST_TEMPLATE.md`
   in that repo, or the org default in this repo). Title format:
   ```
   [<ticket>] <emoji> (<scope>): <summary>
   ```
   Base branch is always the repo's default branch (`master` or `main` —
   confirmed in `setup-dev-env`), never another feature branch, even for
   stacked work — note the stacking dependency in the PR body instead
   (e.g. "Depends on #NN, not yet merged").
6. **Request review.** At least one approval from the required team is
   needed before merge (Pioneer team, per `CLAUDE.md`).
7. **Never merge directly.** All changes land through PR review — this
   applies even for trivial changes and even when you have push access to
   the default branch.

## Do not

- Do not force-push during active review.
- Do not skip pre-commit hooks (`--no-verify`) without explicit confirmation.
- Do not open a PR against another feature branch as the base — always
  target the default branch, and call out stacking in the description.
- Do not merge your own PR, even if CI is green and the change looks small.
