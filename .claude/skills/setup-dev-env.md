# Skill: setup-dev-env

**When to use:** setting up a local machine (or a fresh worktree) to work on
one or more `ai-agent-assembly` repos.

## Checklist

1. **Clone the relevant repo(s).** Use `choose-repo` to confirm which
   repo(s) you actually need before cloning everything. If you're following
   the multi-repo workspace layout (`.claude/WORKSPACE.md`), clone into the
   sibling-directory layout described there rather than nesting repos inside
   each other.
2. **Bootstrap the org AI baseline into your workspace root**, from a local
   `.github` clone:
   ```
   ./scripts/bootstrap-ai-workspace.sh <workspace-root-path>
   ./scripts/validate-ai-workspace.sh <workspace-root-path>
   ```
   The first installs `CLAUDE.md`/`AGENTS.md`/`.claude/rules/`/`.claude/skills/`
   as symlinks (safe to re-run, never clobbers a local override); the second
   confirms the install is complete and reports anything missing or broken.
   See `scripts/README.md` for full flag/output details.
3. **Verify git remote naming before you push anything.** The canonical
   remote (pointing at `ai-agent-assembly/<repo>`) is named `remote` in some
   checkouts and `origin` in others — a local `origin` is sometimes a
   personal fork (notably in `go-sdk`). Run:
   ```
   git remote -v
   ```
   and confirm which remote name resolves to `ai-agent-assembly/<repo>`.
   **Never assume `origin`.** Also confirm the default branch — most repos
   use `master`, but `agent-assembly-docs` and `inner-document` use `main`:
   ```
   git ls-remote --symref <remote> HEAD
   ```
4. **Install the per-repo toolchain.** Each repo owns its own install/build/
   test/lint commands in its `.claude/CLAUDE.md` (and usually its `README.md`
   or `CONTRIBUTING.md`) — don't duplicate those commands here; they drift.
   Read that repo's file and run its documented install step (e.g. `cargo
   build`, `uv sync`, `pnpm install`, `go mod download` — check the actual
   repo, don't assume).
5. **Confirm pre-commit hooks are installed**, if the repo uses them (check
   for a `.pre-commit-config.yaml`, `lefthook.yml`, or similar). Run the
   repo's documented install command for its hook manager. Never bypass
   hooks with `--no-verify` without explicit confirmation from the person
   who asked for the work.
6. **Confirm CI health on the default branch** before branching off it — see
   the CI reality note in `CLAUDE.md` (GitHub Actions is frequently
   billing-blocked; treat that as infra, not a code failure, and validate
   locally instead of waiting on CI).

## Do not

- Do not hardcode `origin` as the push remote in scripts or muscle memory —
  it varies per repo and per contributor's fork setup.
- Do not copy another repo's install commands into this one's setup — always
  defer to that repo's own `.claude/CLAUDE.md`.
