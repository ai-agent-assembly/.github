# Skill: pr-review

**When to use:** immediately before requesting review on a PR — a final
self-check pass, not a substitute for actual reviewer feedback.

## Checklist

- [ ] **Scope matches the ticket.** `git diff` against the base branch
  touches only what the ticket describes. No drive-by refactors, renames, or
  formatting-only changes to unrelated files bundled in.
- [ ] **No unrelated changes bundled.** If you found and fixed something
  unrelated while working, split it into its own commit/PR/ticket rather
  than folding it in here.
- [ ] **Commit messages follow gitmoji format.** Each commit is
  `<emoji> (<scope>): <imperative summary>`, matches the change it
  describes, and the history is bisectable (repo builds at every commit).
- [ ] **PR title follows the convention:**
  `[<ticket>] <emoji> (<scope>): <summary>`.
- [ ] **PR body follows the repo's PR template** exactly — section headers
  present, Jira ticket linked, checklist items addressed rather than left as
  unchecked boilerplate.
- [ ] **Base branch is correct** — the repo's actual default branch
  (`master` or `main`, confirmed per `setup-dev-env`), not another feature
  branch. If this PR is stacked on an unmerged dependency, that's called out
  explicitly in the Summary (e.g. "Depends on #NN").
- [ ] **Tests run and pass locally**, if the repo has a test suite and the
  change touches tested code. Point at the repo's own `.claude/CLAUDE.md`
  for the exact test command — don't guess.
- [ ] **Lint/format/type-check run and pass locally**, if the repo has that
  tooling configured. Same note — commands are repo-specific.
- [ ] **No secrets, credentials, or `.env` files** in the diff.
- [ ] **No build artifacts, compiled output, or commented-out dead code**
  in the diff.

## Do not

- Do not treat this checklist as a substitute for actually reading your own
  diff line by line — read it once before checking any box.
- Do not check a box you haven't actually verified (e.g. "tests pass") just
  because the change looks trivial.
