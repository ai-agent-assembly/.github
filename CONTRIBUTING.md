# Contributing to AI Agent Assembly

Thank you for your interest in contributing! AI Agent Assembly is an open-source project and we welcome contributions of all sizes — bug reports, documentation fixes, new features, performance improvements, and more.

This guide describes the org-wide conventions that apply across all repositories under [ai-agent-assembly](https://github.com/ai-agent-assembly). For repo-specific setup (build commands, test runners, language toolchains), see the `CONTRIBUTING.md` in each individual repo — it takes precedence over this file where they differ.

## Prerequisites

- A GitHub account
- Git installed locally
- Familiarity with the language and tooling of the repo you're contributing to
- The repo cloned locally (see each repo's README for setup steps)

## Branch naming

All feature and fix branches follow this four-part format:

```
<release-or-phase>/<ticket-number>/<type>/<short-summary>
```

- `<release-or-phase>` — milestone or sprint identifier (e.g., `v0.0.1`, `phase1`)
- `<ticket-number>` — Jira ticket reference (e.g., `AAASM-1316`)
- `<type>` — change category, one of:

  | Type | When to use |
  |---|---|
  | `feat` | New feature or capability |
  | `fix` | Bug fix |
  | `refactor` | Refactor with no behavior change |
  | `test` | Test-only change |
  | `docs` | Documentation change |
  | `config` | Configuration / CI change |
  | `deps` | Dependency upgrade |
  | `remove` | Deletion or removal |
  | `lint` | Lint or type-error fix |

- `<short-summary>` — 2–4 words in `snake_case`, max 30 characters

Example: `v0.0.1/AAASM-42/feat/add_agent_registry`

## Commit messages

Commits use [Gitmoji](https://gitmoji.dev/) format with a scope and imperative summary:

```
<emoji> (<scope>): <imperative summary>
```

Examples:

- `✨ (gateway): Add /v1/capability/matrix endpoint`
- `🐛 (auth): Fix token expiry check using UTC`
- `♻️ (proxy): Extract MitM handler into a separate module`

Keep each commit small and **bisectable** — one logical change per commit. If you need two sentences to describe a commit, split it into two.

### GitEmoji reference

| Emoji | Scope |
|---|---|
| `✨` | New feature |
| `🐛` | Bug fix |
| `♻️` | Refactor |
| `✅` | Tests |
| `📝` | Documentation |
| `🔧` | Configuration / CI |
| `⬆️` | Dependency upgrade |
| `🗑️` | Removal |
| `🚨` | Lint / type-error fix |
| `🎉` | Initial commit |

## Pull Requests

### Title

```
[<ticket>] <emoji> (<scope>): <imperative summary>
```

Example: `[AAASM-42] ✨ (gateway): Add /v1/capability/matrix endpoint`

### Description

Each repo provides a `.github/PULL_REQUEST_TEMPLATE.md`. Fill it out completely; at minimum the description must include:

- **What changed** — one short paragraph
- **Why** — motivation, context, ticket link
- **How to verify** — manual steps or test reference
- **Related issues** — ticket and any related GitHub issues

### Base branch

PRs always target `main`, even when your branch was created from another feature branch.

### Scope

Keep PRs focused. One concern per PR — don't bundle unrelated changes. If a single ticket needs more than ~500 lines of diff, split it into a sequence of stacked PRs.

## Continuous integration — the 8-principle playbook

Every repo's CI is hand-rolled, which is why the same gaps recur. To stop
retrofitting, the org `.github` repo ships **starter workflows** that bake these
eight principles in, so new and empty repos start compliant. Pick one from the
**Actions → New workflow** screen (look for "… (Agent Assembly playbook)"):
`Rust CI`, `Node / TypeScript CI`, `Python CI`, `Go CI`, or `Docs CI`.

The reference rationale and the **measured-result evidence** (before/after CI
minutes and wall-clock) live in `agent-assembly`'s
[`docs/src/benchmarks/ci-cd-pipeline-performance.md`](https://github.com/ai-agent-assembly/agent-assembly/blob/main/docs/src/benchmarks/ci-cd-pipeline-performance.md).

| # | Principle | How the starters apply it |
|---|---|---|
| 1 | **Path-scoped triggers** | `on.push` / `on.pull_request` list `paths:` so doc-only or unrelated edits don't spend CI minutes. |
| 2 | **Concurrency cancel** | `concurrency` cancels superseded runs **only on PRs** (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`) — `$default-branch` and tag pushes always run to completion. |
| 3 | **Single `CI Success` gate** | An aggregate job (`needs: [...]` + `if: always()`) is the one required check. Branch protection requires only `CI Success`, not every job. |
| 4 | **Linux-default matrices** | The OS matrix is `["ubuntu-latest"]` on PRs and only fans out to macOS/Windows on `$default-branch` / tag pushes. |
| 5 | **Least-privilege permissions** | A top-level `permissions: contents: read`; jobs widen scope only when they must. |
| 6 | **Job timeouts** | Every job sets `timeout-minutes` so a hung step can't burn the runner budget. |
| 7 | **Reusable gate** | The `CI Success` logic is a reusable workflow (`ci-success.yml`, `on: workflow_call`); repos `uses:` it instead of copy-pasting (see below). |
| 8 | **Cache the toolchain** | Each starter caches its package/build artifacts (`Swatinem/rust-cache`, `setup-node … cache: pnpm`, `setup-uv`, `setup-go`) to keep warm runs fast. |

### Reusable `CI Success` gate

Instead of copy-pasting the aggregate gate, call the org reusable workflow:

```yaml
ci-success:
  name: CI Success
  if: always()
  needs: [lint, test]
  uses: ai-agent-assembly/.github/.github/workflows/ci-success.yml@main
  with:
    needs-json: ${{ toJSON(needs) }}
```

It fails if any upstream job's `result` is `failure` or `cancelled`; skipped
jobs are non-blocking. Make `CI Success` the only required status check.

## Code review

- At least **one approval** is required before merge.
- Address every reviewer comment before requesting re-review.
- Don't force-push during an active review (only allowed when rebasing onto the latest base branch — never to rewrite review history).
- CI must be green before merge. Don't bypass with `--no-verify` or by disabling checks.
- The reviewer or assignee picks the merge strategy (typically squash or rebase). The repo's default reflects the team's preference.

## Developer Certificate of Origin

By contributing to AI Agent Assembly, you certify that:

1. The contribution was created in whole or in part by you, **or**
2. The contribution is based on work that is licensed under an appropriate open-source license, **or**
3. The contribution was provided directly to you by someone who certified (1) or (2).

We do not currently require explicit commit sign-off (`git commit -s`), but reserve the right to add DCO bot enforcement in the future. If we do, we'll announce it on the relevant repo's Discussions and update this section.

## License

By contributing, you agree that your contributions will be licensed under the same license as the repository you're contributing to (Apache 2.0 for all public repos in this org, unless a specific repo states otherwise in its `LICENSE` file).
