# AGENTS.md — org-wide baseline (ai-agent-assembly)

Compact, always-on instructions for Codex (and any other `AGENTS.md`-reading tool)
across **all** repos in the [`ai-agent-assembly`](https://github.com/orgs/ai-agent-assembly/repositories)
org. This is the Codex-facing counterpart to this repo's `CLAUDE.md` — the two are
kept in sync on shared, org-wide policy. Each repo may have its own `AGENTS.md`
with repo-specific commands and gotchas; that file takes precedence when you are
working inside that repo, and it should reference this baseline instead of
repeating it.

> This file is intentionally an entry point, not a knowledge dump. If a repo has
> its own `AGENTS.md` or `.claude/CLAUDE.md`, read that first — it overrides or
> extends what's here for that repo.

## The product in one paragraph

AI Agent Assembly enforces governance on AI agents through **three independently-
deployable interception layers**: (1) the **SDK layer** (in-process shims in the
language SDKs over the `aa-sdk-client` crate), (2) the **sidecar proxy** (`aa-proxy`,
MitM of outbound HTTPS), and (3) **eBPF** (kernel uprobes, Linux-only). The
**gateway** (`aa-gateway`) is the brain (registry, policy engine, budgets); the
**runtime** (`aa-runtime`) is the authoritative enforcement point; the **CLI**
ships the `aasm` binary. See `profile/README.md` for the full repo map.

## Repo map (which repo does what)

| Repo | Role |
|---|---|
| `agent-assembly` | Core Rust monorepo — gateway, policy, eBPF, proxy, FFI, CLI, dashboard. **Source of truth** for protocol + the shared `aa-*` crates. |
| `python-sdk` / `node-sdk` / `go-sdk` | Language SDKs (thin FFI shim over `aa-sdk-client`, pinned by git SHA) |
| `cloud` | SaaS / cloud control plane (FastAPI + React + Rust persistence) |
| `agent-assembly-enterprise` | Enterprise Rust extensions (SaaS-only) |
| `examples` | Runnable governance demo scenarios |
| `e2e-public` / `e2e-private` | Cross-repo + private e2e suites |
| `docs` / `internal-docs` | Public docs site / internal docs site |
| `homebrew-tap` | Homebrew tap for the `aasm` CLI |
| `.github` / `.github-private` | Org community-health, reusable workflow-templates, this baseline |
| `agent-assembly-spec` | **Archived** — the protocol spec lives in the `agent-assembly` monorepo |

## Conventions that apply regardless of which AI tool is used

These are org policy, not Claude-Code-specific — follow them from Codex the same
as from Claude Code:

- **Commits:** `<emoji> (<scope>): <imperative summary>` (gitmoji.dev). One logical
  unit per commit; bisectable; utils/mocks/tests are separate preceding commits.
- **Branch:** `<release-or-phase>/<ticket>/<type>/<short_summary>` —
  e.g. `v0.0.1/AAASM-42/feat/add_agent_registry`. Types: feat/fix/refactor/test/docs/
  config/deps/remove/lint.
- **PR title:** `[<ticket>] <emoji> (<scope>): <summary>`; body follows the repo's PR
  template; ≥1 Pioneer-team approval. **Never merge to base directly — PR only.**
- **Worktrees:** develop each ticket in a worktree off the latest default branch so
  the main checkout stays clean; remove the worktree after merge.

## Git remotes & default branches (these vary per repo — always detect)

- The **canonical remote** (the one pointing at `ai-agent-assembly/<repo>`) is named
  **`remote`** in some checkouts and **`origin`** in others; a local `origin` is
  sometimes a personal fork (notably `go-sdk`). Run `git remote -v` and push to the
  one pointing at `ai-agent-assembly`. **Never assume `origin`.**
- **Default branch:** `main` is the canonical org-wide default across all repos
  (the archived, empty `agent-assembly-spec` is the only non-substantive edge).
  Confirm with `git ls-remote --symref <remote> HEAD`.
- The org id is **lowercase `ai-agent-assembly`** everywhere (Cargo git URLs, Go
  module paths, Codecov slugs, docs). An `AI-agent-assembly` remote URL is an old
  casing that redirects — harmless on push, but write lowercase in code/docs.

## CI reality

GitHub Actions is frequently **billing-blocked** (private repos always; intermittently
org-wide): jobs abort in ~2–11s with a "recent account payments have failed" message,
and downstream checks (SonarCloud) then fail for lack of artifacts. **Confirm via the
job annotations**, treat it as infra (not a code failure), and **validate locally**
rather than waiting on CI. Never `--no-verify`; never force-push.

## JIRA (project AAASM)

- Cloud: `lightning-dust-mite.atlassian.net`. Hierarchy Epic → Story → Subtask
  (one Subtask ≈ one commit) + a `Verify …` subtask per Story.
- **Component** (Jira's native `components` field) = the GitHub repo, 1:1,
  value = the **org-relative repo name**, short and lowercase, not org-prefixed
  (e.g. `docs`, `python-sdk`, `.github` — not `ai-agent-assembly/docs`).
  **Team** (`customfield_10001`) = Pioneer.

## Project policy

- **Self-hosted deployment is out of scope product-wide** — enterprise ships via SaaS
  only. Don't propose Helm/Terraform/air-gapped/migration work.
- **The Protocol Specification stays in the `agent-assembly` monorepo** — not in the
  archived `agent-assembly-spec` repo.

## Rules & skills (Claude-Code-specific tooling, org policy applies to Codex too)

- `.claude/rules/` and `.claude/skills/` hold reusable rule and skill definitions
  written for Claude Code's skill system. They are reserved but empty as of this
  commit — AAASM-3941 and AAASM-3942 populate them. Codex has no native equivalent
  loader for these files, but where a rule/skill encodes **org policy** (e.g. commit
  conventions, PR structure, CI triage) rather than Claude-Code mechanics, that
  policy still applies to work done via Codex — read the file directly if in doubt.
- See `.claude/WORKSPACE.md` for how this baseline and those directories get
  installed into a contributor's local multi-repo workspace.

## Full detail

For the long-form version of this baseline (product architecture in more depth,
documentation-comment philosophy, etc.), see this repo's `CLAUDE.md` — the content
overlaps by design; this file exists so a Codex session has everything it needs
without reading a Claude-Code-specific file.
