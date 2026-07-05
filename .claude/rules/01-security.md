# Security

> **Scope note:** this file (and the rest of `.claude/rules/`) is **advisory
> guidance** for AI-assisted development discovered from this baseline —
> Epic AAASM-3926 ("Org-level Claude Code Governance Scaffold") separately
> owns *hard, deterministic* enforcement (allow/deny lists, eventually a
> `.claude/settings.json`) for this org. Don't duplicate that scope here, and
> don't create a `.claude/settings.json` from this ticket.

Applies across all `ai-agent-assembly` repos, for any AI coding tool.

## Secrets, credentials, and PII

- Never commit `.env` files, API keys, tokens, private keys, or any other
  credential material — check `git status`/`git diff` before every commit for
  files that look like secrets.
- Never paste secrets, credentials, or PII into a prompt, a commit message, a
  PR description, or a Jira comment. If a secret is discovered in the repo or
  history, stop and escalate (see `04-agent-escalation.md`) rather than
  trying to scrub it yourself — history rewrites need explicit engineer
  sign-off.
- Treat CI logs and error output the same way: don't echo environment
  variables or config that may contain secrets into a tool call or a report.

## Dangerous commands

- Never pipe remote content directly into a shell (`curl | bash` or
  equivalent).
- Never use `--no-verify` (or any other hook-skipping flag) to bypass
  pre-commit or pre-push hooks.
- Never force-push to `main`/`master`/a release branch, under any
  circumstance. Force-push on a feature branch requires explicit engineer
  confirmation.
- Never run destructive operations (`git reset --hard`, `git clean -fd`,
  dropping/truncating a database table, deleting files) without explicit
  engineer confirmation.

## When in doubt

If a task appears to require any of the above, stop and ask instead of
guessing — see `04-agent-escalation.md` for how to phrase the escalation.
