# Coding standards

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). These are the cross-repo standards; each repo's own
`.claude/CLAUDE.md` / `AGENTS.md` adds language- and repo-specific detail
(build/test/lint commands, type-checker config, etc.) on top.

## Documentation: WHY, not WHAT

This org's baseline documentation philosophy already lives in this repo's
root `CLAUDE.md`, under "Documentation conventions — document the WHY, not
the WHAT" — read that section rather than restating it here. In short:
comments and docstrings should capture intent the code can't (rationale,
constraints, invariants, non-obvious decisions), not restate what the code
already says.

## Scope discipline

- Make the smallest change that satisfies the ticket. Don't refactor
  surrounding code, rename unrelated things, or reorganize files unless the
  ticket asks for it.
- Don't add features, options, abstractions, or error handling beyond what
  was requested — including for scenarios that can't happen given the
  current callers.
- Don't add backwards-compatibility shims for code that has no callers yet.
- If a change touches more than the ticket's stated scope, stop and confirm
  before proceeding rather than silently expanding it.

## Before proposing changes

- Read the relevant existing code first; don't assume behavior from a
  filename or a similar-looking pattern elsewhere.
- Clarify ambiguous requirements before starting rather than guessing at
  intent.
