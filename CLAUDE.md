# CLAUDE.md — org-wide baseline (ai-agent-assembly)

Canonical, shared context for Claude Code (and humans) across **all** repos in the
[`ai-agent-assembly`](https://github.com/orgs/ai-agent-assembly/repositories) org.
Each repo also has its own `.claude/CLAUDE.md` with repo-specific commands and
gotchas; those files **reference this baseline** instead of repeating it.

> **Note — this is a convention, not inheritance.** GitHub does not auto-apply a
> CLAUDE.md across repos. Claude Code reads the CLAUDE.md in the repo you are working
> in (plus your machine's global `~/.claude/CLAUDE.md`). This file is the single
> source of truth that per-repo files link to; keep org-universal facts here and
> repo-specific facts in each repo's `.claude/CLAUDE.md`.

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
| `agent-assembly-cloud` | SaaS / cloud control plane (FastAPI + React + Rust persistence) |
| `agent-assembly-enterprise` | Enterprise Rust extensions (SaaS-only) |
| `agent-assembly-examples` | Runnable governance demo scenarios |
| `agent-assembly-integration-tests` / `agent-assembly-private-e2e` | Cross-repo + private e2e suites |
| `agent-assembly-docs` / `inner-document` | Public docs site / internal docs site |
| `homebrew-tap` | Homebrew tap for the `aasm` CLI |
| `.github` / `.github-private` | Org community-health, reusable workflow-templates, this baseline |
| `agent-assembly-spec` | **Archived** — the protocol spec lives in the `agent-assembly` monorepo |

## Universal conventions (each repo's CONTRIBUTING.md is authoritative)

- **Commits:** `<emoji> (<scope>): <imperative summary>` (gitmoji.dev). One logical
  unit per commit; bisectable; utils/mocks/tests are separate preceding commits.
- **Branch:** `<release-or-phase>/<ticket>/<short_summary>` —
  e.g. `v0.0.1/AAASM-42/add_agent_registry`.
- **PR title:** `[<ticket>] <emoji> (<scope>): <summary>`; body follows the repo's PR
  template; ≥1 Pioneer-team approval. **Never merge to base directly — PR only.**
- **Worktrees:** develop each ticket in a worktree off the latest default branch so
  the main checkout stays clean; remove the worktree after merge.

## Git remotes & default branches (these vary per repo — always detect)

- The **canonical remote** (the one pointing at `ai-agent-assembly/<repo>`) is named
  **`remote`** in some checkouts and **`origin`** in others; a local `origin` is
  sometimes a personal fork (notably `go-sdk`). Run `git remote -v` and push to the
  one pointing at `ai-agent-assembly`. **Never assume `origin`.**
- **Default branch varies:** most repos use `master`; `agent-assembly-docs` and
  `inner-document` use `main`. Confirm with `git ls-remote --symref <remote> HEAD`.
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
- **Component** (`customfield_10041`, a label-type field) = the GitHub repo, 1:1,
  value = the **org-relative repo name**, short and lowercase, not org-prefixed
  (e.g. `docs`, `python-sdk`, `.github` — not `ai-agent-assembly/docs`).
  **Team** (`customfield_10001`) = Pioneer.

## Project policy

- **Self-hosted deployment is out of scope product-wide** — enterprise ships via SaaS
  only. Don't propose Helm/Terraform/air-gapped/migration work.
- **The Protocol Specification stays in the `agent-assembly` monorepo** — not in the
  archived `agent-assembly-spec` repo.

## AI tooling: rules, skills, and Codex parity

- Claude Code reads this `CLAUDE.md`; Codex reads the sibling `AGENTS.md` at the
  repo root instead — keep both files in sync on org-wide policy (commit/branch/PR
  conventions, remote-naming, CI reality, JIRA, project policy). `AGENTS.md` is the
  Codex-facing version of this baseline, written to be self-sufficient since Codex
  does not read `CLAUDE.md`.
- `.claude/rules/` and `.claude/skills/` are shared, reusable rule and skill
  definitions that apply across all `ai-agent-assembly` repos — both directories
  are populated (`.claude/rules/` since AAASM-3941, `.claude/skills/` since
  AAASM-3942). Treat each directory as an index: browse it rather than assuming
  a specific filename exists, since new files get added over time.
- See `.claude/WORKSPACE.md` for how these org-level files get installed into a
  contributor's local multi-repo workspace (bootstrap/validation are tracked as
  AAASM-3943/AAASM-3944).

## Documentation conventions — document the WHY, not the WHAT

Comments and docstrings capture intent the code cannot: rationale, constraints,
invariants, non-obvious decisions. Restating what the code already says is noise that
rots out of sync — delete it.

- **Module / package** docs: role in the architecture + key invariants.
- **Public API** docs: the contract — behavior, errors, units, side effects, and any
  threading/async/`unsafe`/ordering constraints (especially the surprising ones).
  Use the language's idiom: rustdoc `//!`/`///`, Google-style Python docstrings,
  TSDoc on exports, godoc doc-comments starting with the identifier name.
- **Inline why-comments:** workarounds, perf-sensitive code, security rationale,
  dependency pins (explain *why* pinned). These are the highest-value comments.
- **Skip:** trivial helpers, getters, type-restating, per-variable docstrings.
- **Big architectural decisions → ADRs**, not scattered docstrings; link code to the
  ADR. Reference existing design specs (`.ai/spec/`, `design/vN/`) rather than copying.

> A new contributor (human or LLM) should read a module's header + a public item's
> doc and understand *why it is the way it is* without reverse-engineering it.
