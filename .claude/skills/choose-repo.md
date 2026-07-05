# Skill: choose-repo

**When to use:** you know *what* needs to change but not *which* org repo it
belongs in. Get this right before branching — cross-repo confusion is the
most common source of wasted PRs in this org.

## Decision tree

Start from the task, not the repo you happen to be sitting in:

1. **Does a JIRA ticket exist?** Check its Component field
   (`customfield_10041`) first — it is a 1:1 mapping to the GitHub repo
   (`ai-agent-assembly/<repo>`) and is authoritative. Don't second-guess it
   from the ticket title; if it looks wrong, ask rather than silently
   re-routing (see `feedback_repo_routing` class of mistakes: don't trust a
   title-based guess over the Component field, and don't trust the Component
   field blindly either if the described work clearly doesn't match it —
   flag the mismatch).
2. **No ticket, or ticket has no Component set** — use the work itself:

   | Task looks like... | Repo |
   |---|---|
   | Gateway, policy engine, eBPF, proxy, FFI, CLI (`aasm`), dashboard, or any shared `aa-*` crate | `agent-assembly` |
   | Python-specific SDK shim/packaging/docs | `python-sdk` |
   | Node/TypeScript-specific SDK shim/packaging/docs | `node-sdk` |
   | Go-specific SDK shim/packaging/docs | `go-sdk` |
   | Public docs site content | `agent-assembly-docs` |
   | Internal/private docs site content | `inner-document` |
   | Cloud control plane (FastAPI/React/persistence) | `agent-assembly-cloud` |
   | Enterprise-only Rust extensions | `agent-assembly-enterprise` |
   | Runnable demo/sample code | `agent-assembly-examples` |
   | Cross-repo or private e2e test suites | `agent-assembly-integration-tests` / `agent-assembly-private-e2e` |
   | Homebrew formula/tap | `homebrew-agent-assembly` |
   | Org community-health files, reusable CI workflow templates, org-level AI baseline (`CLAUDE.md`/`AGENTS.md`/`.claude/`) | `.github` (this repo) or `.github-private` |
   | Protocol/spec content | `agent-assembly` monorepo — **not** `agent-assembly-spec` (archived; see project policy in `CLAUDE.md`) |

3. **Task spans more than one repo** (e.g. an API changes in
   `agent-assembly` and a consumer must follow in `python-sdk`) — this is
   cross-repo work. Don't split it into unrelated single-repo tickets without
   coordination; that's what `cross-repo-coordinator` (a global skill, not
   org-specific) is for.
4. **Still ambiguous** — read the repo map table in `CLAUDE.md` /
   `AGENTS.md` (`## Repo map`) for the one-line role of every repo, or ask
   rather than guessing.

## Do not

- Do not assume the repo you're currently checked out in is the right one
  just because that's where the session started.
- Do not put spec work in `agent-assembly-spec` — it's archived by policy.
- Do not propose Helm/Terraform/self-hosted infra tickets for any repo —
  out of scope product-wide (see `CLAUDE.md` project policy).
