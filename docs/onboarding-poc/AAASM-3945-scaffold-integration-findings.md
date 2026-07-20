# AAASM-3945 — Scaffold integration findings

Epic AAASM-3938 (org-level AI onboarding POC) has, as of this ticket, five
prior subtasks (AAASM-3939 through AAASM-3944) each landed on its own
stacked branch/PR in this repo, but no single branch has all of them
together — 3941 (rules) and 3942 (skills) both fork from 3940 without
merging into each other, and likewise 3943/3944 (scripts) fork from 3940
independently. This ticket's job is to actually combine everything once,
locally, and confirm the full scaffold works end-to-end before it all lands
on `master` — plus do a read-only survey of how a few real org repos look
against that scaffold today.

**This ticket makes no code changes to the scaffold itself and modifies no
repo other than `.github`.** It is a documentation-only deliverable
recording what was tested and observed. The integration checkout used for
testing was a disposable local worktree/branch
(`tmp/aaasm-3938-integration-test`, forked from
`v0.1.0/AAASM-3944/build_validation_script` with `v0.1.0/AAASM-3941/design_claude_rules`
and `v0.1.0/AAASM-3942/design_claude_skills` merged on top) — it was never
pushed and has since been deleted (`git worktree remove` + `git branch -D`).

## 1. End-to-end integration test result: PASS, no bugs found

Combined tree (`CLAUDE.md`/`AGENTS.md` + `.claude/WORKSPACE.md` + real
`.claude/rules/*.md` (6 files) + real `.claude/skills/*.md` (7 files) +
`scripts/bootstrap-ai-workspace.sh` + `scripts/validate-ai-workspace.sh`):

1. Merging `v0.1.0/AAASM-3941/design_claude_rules` and
   `v0.1.0/AAASM-3942/design_claude_skills` on top of
   `v0.1.0/AAASM-3944/build_validation_script` produced **zero merge
   conflicts** — the three branches touch disjoint file sets
   (`.claude/rules/*`, `.claude/skills/*`, `scripts/*` respectively), aside
   from `CLAUDE.md`, which 3941 updates additively (adds a line noting
   `.claude/rules/` is now populated) and which the auto-merge resolved
   cleanly with no manual intervention.
2. `scripts/bootstrap-ai-workspace.sh --dry-run /tmp/aaasm-3938-workspace-test`
   reported the correct planned actions (create workspace `.claude/` +
   `.claude/commands`, symlink `CLAUDE.md`, `AGENTS.md`, `.claude/rules`,
   `.claude/skills`) with no errors.
3. Running it for real (`bootstrap-ai-workspace.sh
   /tmp/aaasm-3938-workspace-test`, no `--dry-run`) created all six items
   (`created=6 updated=0 skipped=1 failed=0` — the one skip is the
   already-existing workspace root directory, which is expected since we
   pre-created it with `mkdir -p` for the test).
4. `scripts/validate-ai-workspace.sh /tmp/aaasm-3938-workspace-test`
   reported `missing=0 broken=0 override=0 ok=4` and exited `0` — every
   symlink resolves to the real `.claude/rules/01-security.md` …
   `06-audit-trail.md` and `.claude/skills/choose-repo.md` …
   `task-intake.md` files (confirmed with `find -L`), not placeholders, and
   `CLAUDE.md`/`AGENTS.md` resolve to the real org-baseline content.
5. Re-running `bootstrap-ai-workspace.sh` a second time against the same
   target confirmed idempotency: all seven items reported `[skipped]
   ... already exists/already linked (up to date)`, `created=0 updated=0
   skipped=7 failed=0`.

**No bugs or friction were found.** In particular, the concern flagged in
this ticket's brief — that a prior agent might have only tested
`bootstrap`/`validate` against placeholder rule/skill content and that real
filenames or a real rules/skills directory shape could reveal a
relative-path or globbing assumption that breaks — did not materialize.
Both scripts operate on `.claude/rules` and `.claude/skills` as whole
directories (single `ensure_symlink`/`check_item` per directory, not
per-file), so the actual file count and names inside those directories are
irrelevant to script correctness. `bootstrap-ai-workspace.sh`'s
`SCRIPT_DIR` resolution (`cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd`)
correctly resolved to the merged worktree root, not to any individual
source branch's checkout, confirming the "symlink back to this repo
checkout" design (documented in the script's own header comment) survives
a multi-branch merge.

No follow-up bugfix ticket is needed as a result of this test.

## 2. Per-repo survey (read-only, no edits made)

Representative sample: `agent-assembly` (core Rust monorepo), `python-sdk`
(language SDK), `docs` (docs site). Checked from each repo's
real path under `/Users/bryant/Bryant-Developments/AI-agent-assembly/`,
cross-checked manually (`find`/`ls`) and via
`scripts/validate-ai-workspace.sh <workspace> <repo>...`'s informational
per-repo report, which agreed exactly with the manual check in all three
cases:

| Repo | `.claude/CLAUDE.md` | `AGENTS.md` | `.claude/rules/` override? | `.claude/skills/` override? |
|---|---|---|---|---|
| `agent-assembly` | Present (131 lines) | Absent | No — directory does not exist | No — directory does not exist |
| `python-sdk` | Present (147 lines) | Absent | No — directory does not exist | No — directory does not exist |
| `docs` | Present (129 lines) | Absent | No — directory does not exist | No — directory does not exist |

Findings:

- All three repos already have their own `.claude/CLAUDE.md` with
  repo-specific build/test/lint commands, matching what this workspace's
  own root `CLAUDE.md` documents. This was expected and is unchanged by
  this ticket.
- All three repos are **missing `AGENTS.md`** (or any Codex-equivalent
  file). This is an **expected gap**, not a defect: `AGENTS.md` is a new
  concept this org baseline just introduced in AAASM-3940, and no per-repo
  rollout of it has happened yet. It surfaces here for visibility, not as
  something this ticket fixes.
- **No override conflicts exist.** None of the three repos has a
  `.claude/rules/` or `.claude/skills/` directory of its own, so there is
  nothing that could currently shadow the org baseline's
  `.claude/rules/*.md` or `.claude/skills/*.md` once a contributor bootstraps
  their workspace. This is expected, since both directories are brand new
  (AAASM-3941/3942) and no repo has had a reason to add a repo-local
  override yet.

## 3. Explicit scope statement

**No repo other than `ai-agent-assembly/.github` was modified by this
ticket.** The per-repo survey above is read-only documentation of the
current state of `agent-assembly`, `python-sdk`, and `docs`
against the org onboarding scaffold. Per this ticket's acceptance criteria
("add repo-local overrides only where necessary"): no genuine, safe,
in-scope gap requiring an override was found in any of the three surveyed
repos, and even if one had been found, creating/editing files in another
repo is explicitly out of scope for this `.github`-repo ticket — that would
be separate, repo-owned follow-up work tracked under Epic AAASM-3938 (e.g.
a future per-repo `AGENTS.md` rollout), not something this ticket performs.
