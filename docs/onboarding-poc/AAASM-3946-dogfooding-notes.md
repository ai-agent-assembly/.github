# AAASM-3946 — Onboarding dogfooding notes

Epic AAASM-3938. This ticket is the qualitative-evaluation counterpart to
AAASM-3945's integration test: 3945 confirmed the scaffold *assembles and
runs* cleanly; this ticket actually reads the produced artifacts cold and
exercises them from four contributor personas, to surface friction that a
mechanical pass-through-the-scripts test cannot catch.

**Method.** Read the full combined scaffold: root `CLAUDE.md` / `AGENTS.md`
(from `v0.1.0/AAASM-3945/apply_scaffold_to_repos`), `.claude/WORKSPACE.md`,
all 6 `.claude/rules/*.md` and all 7 `.claude/skills/*.md` (read directly off
`v0.1.0/AAASM-3941/design_claude_rules` and
`v0.1.0/AAASM-3942/design_claude_skills`, since neither exists yet on the
3945 tip — same diamond-branch situation 3945 already documented), and both
scripts' `--help` output and source. For the four scenarios below, actually
ran `scripts/bootstrap-ai-workspace.sh` and `scripts/validate-ai-workspace.sh`
against scratch `/tmp` directories, using the same disposable-merge technique
3945 used (merge 3941 + 3942 onto a copy of the 3945 tip, in a throwaway
branch/worktree, never pushed, deleted before finishing:
`tmp/aaasm-3946-dogfood-integration`, removed via `git worktree remove` +
`git branch -D`). **No repo other than `.github` was touched, and no
disposable branch was pushed.**

---

## Scenario 1: First-time contributor

Started cold from `onboard-org.md`, as instructed.

**What worked:**
- The 5-step flow (read baseline → confirm workspace layout → pick repo →
  bootstrap → read target repo's own file) is a sensible, linear order and
  each step names the exact file/skill to consult next — no dead ends.
- `choose-repo.md`'s decision table resolved both concrete examples the
  ticket brief asked for cleanly, with no ambiguity:
  - *"fix a typo in the Python SDK docs"* → row "Python-specific SDK
    shim/packaging/docs" → `python-sdk`.
  - *"add a new gateway policy rule"* → row "Gateway, policy engine, eBPF,
    proxy, FFI, CLI (`aasm`), dashboard, or any shared `aa-*` crate"
    → `agent-assembly`.
- Actually ran `bootstrap-ai-workspace.sh <workspace> --dry-run` then for
  real, then `validate-ai-workspace.sh <workspace>`, exactly per
  `scripts/README.md`'s documented invocation. Matched the README exactly:
  `--dry-run` printed the same planned actions as the real run performed,
  the real run reported `created=7 updated=0 skipped=0 failed=0`, and
  validate reported `missing=0 broken=0 override=0 ok=4` / exit `0`.

**What was confusing / stale:**
- `onboard-org.md` step 4 says: *"Bootstrap your local workspace, **once
  `AAASM-3943` ships**... (exact CLI interface TBD — check the script's own
  `--help` once it exists rather than assuming flags here)."* AAASM-3943 has
  since shipped (it's a dependency of this very ticket's branch chain), but
  this skill file was never revisited to drop the hedge and state the actual
  interface (`bootstrap-ai-workspace.sh <workspace-root-path> [--dry-run]`).
  A first-time contributor reading this skill today gets told to go check
  `--help` themselves instead of just being told the interface — extra
  friction for no reason, since the interface is now a known, stable fact.
- `onboard-org.md` never mentions `validate-ai-workspace.sh` at all, and
  neither does any other skill file (confirmed with
  `grep -rn "validate-ai-workspace" .claude/skills/` — zero hits). A
  first-time contributor following the skills literally would install the
  scaffold but never learn there's a second script to confirm the install
  worked.
- Important caveat for whoever reads this next: none of AAASM-3939 through
  3945 (or this ticket) have landed on `master` yet. A contributor who
  clones `ai-agent-assembly/.github` at `master` **today** gets none of this
  scaffold — every successful run described here and in AAASM-3945 used a
  disposable local merge of still-unmerged branches. The very first
  "real" first-time-contributor experience only happens after PR #25 through
  this ticket's PR land (see Improvement item 10).

---

## Scenario 2: Returning maintainer

Assessed `06-audit-trail.md` and `04-agent-escalation.md`'s sibling
`task-intake.md` critically, per the brief's instruction to be honest if the
answer is "not really."

**Honest verdict: modest help, not a real accelerant.**

- `audit-trail.md` mostly *describes* conventions that already exist
  elsewhere (gitmoji commits on ticket-named branches, `[<ticket>]`-prefixed
  PR titles, two Jira comments). None of this is a discovery *tool* — it's
  documentation of a convention a returning maintainer would reconstruct
  just as fast by reading `git log --oneline` and the PR list, since the
  convention is already baked into every branch/commit/PR name. It gives no
  runnable command and no index of "what's the current state of Epic X" —
  a returning maintainer still has to manually run `git branch -a`, `gh pr
  list`, and a Jira JQL query themselves; nothing in the scaffold packages
  that into one step.
- `task-intake.md` is somewhat more useful: its dependency-check step
  ("look for JIRA issue links, prior tickets in the same Epic this one is
  stacked on, an open PR from a dependency ticket that hasn't merged yet")
  is a genuinely useful forcing function for someone who's been away and
  might not remember which siblings in the Epic already merged. But it still
  gives no concrete command to answer that question — no JQL snippet, no
  `gh pr list --search` example, no `git branch --list 'v0.1.0/AAASM-39*'`.
  It tells you *what* to check, not *how* to check it quickly.
- By contrast, this user's own global `~/.claude/CLAUDE.md` ships real
  session-continuity tooling (`workflow-state.sh`, `decision-log.sh`,
  `session-memory.sh`, a circuit breaker) that actually answers "where did I
  leave off" mechanically. The org-level scaffold has no equivalent — two
  advisory markdown files is a much lighter bar. Not necessarily wrong (the
  global tooling is a different layer), but worth being explicit that the
  org scaffold does not close this gap on its own (see Improvement item 12).

---

## Scenario 3: Workspace setup

Followed `setup-dev-env.md`'s checklist and cross-checked it against what
the two scripts actually require, per the ticket brief's specific ask
("does it correctly explain the two scripts, their exact invocation, and
workspace path argument?").

**Answer: no — it doesn't mention either script.**

- `setup-dev-env.md`'s 5-item checklist (clone repos → verify remote naming
  → install per-repo toolchain → confirm pre-commit hooks → confirm CI
  health) is accurate and matches what `CLAUDE.md`/`AGENTS.md` say about
  remote-naming and CI reality. Step 1 references `.claude/WORKSPACE.md` for
  the sibling-directory layout, but **never names `bootstrap-ai-workspace.sh`
  or `validate-ai-workspace.sh`, their arguments, or that they exist at
  all** — despite this being the skill most obviously about "set up my
  local workspace." A contributor following only `setup-dev-env.md` would
  correctly clone repos into the right layout, but would have to separately
  discover the scripts exist (only `onboard-org.md` mentions one of them,
  with stale hedge language — see Scenario 1).
- Actually ran both scripts end-to-end against `/tmp/aaasm-3946-scratch-
  workspace` (see Scenario 1) — mechanically both scripts work exactly as
  their own `README.md`/`--help` describe. The gap is purely in
  `setup-dev-env.md` not pointing at them.
- Tested the override model concretely, since 3945 flagged that only a
  synthetic test had been done. `.claude/WORKSPACE.md`'s "Override model"
  section states: *"A repo-local rule or skill with the same filename as an
  org-level one... the validation script (AAASM-3944) flags overrides so
  they're visible, not silent."* I created a fake repo directory with its
  own `.claude/rules/01-security.md` (a real per-file override of an
  org-level rule filename) and passed it to
  `validate-ai-workspace.sh <workspace> <fake-repo>`. **The script reported
  `override=0` and gave no indication of the shadowed file** — its
  optional repo-path check only looks for the *existence* of
  `.claude/CLAUDE.md` and `AGENTS.md` at the repo root; it never inspects a
  repo's own `.claude/rules/` or `.claude/skills/` contents for filename
  collisions with the org baseline. This is a real, verified gap between
  what `WORKSPACE.md` documents and what `validate-ai-workspace.sh` actually
  does (see Improvement item 3) — not just an untested-but-probably-fine
  path, an actually-incorrect claim.

---

## Scenario 4: Task preparation

Walked a hypothetical `AAASM-9999: fix a bug in aa-gateway policy
evaluation` through `task-intake.md` → `02-git-workflow.md` →
`04-agent-escalation.md`.

**What worked:**
- `task-intake.md`'s steps (read ticket + Epic/Story → confirm repo via
  Component field, falling back to `choose-repo` → check blocking
  dependencies → transition to In Progress + comment → determine branch name
  → create worktree) are complete and ordered correctly. For this
  hypothetical, `choose-repo.md` resolves `agent-assembly` immediately (same
  "gateway, policy engine" row as Scenario 1's second example).
- `02-git-workflow.md` gives the literal `git worktree add -b <new-branch>
  <path> <dependency-branch>` command for the stacked case, not just prose —
  genuinely actionable.
- `04-agent-escalation.md`'s three-part escalation template (what's
  blocking / what was tried / what decision is needed) is well-specified
  and, correctly, wouldn't even need to fire for a well-scoped bug fix like
  this one — it's appropriately scoped as a guardrail, not a mandatory step.

**What's missing — two concrete gaps that would force a guess or a question:**
1. **No resolution order for `<release-or-phase>`.** `02-git-workflow.md`
   only gives a worked example (`v0.1.0/AAASM-3941/design_claude_rules`); it
   never states how to determine the *current* phase prefix for a brand-new
   ticket that isn't already anchored to an existing branch. This user's own
   global `~/.claude/CLAUDE.md` documents an explicit resolution order
   (env var → `.claude/.current-release` file → ticket's Jira milestone
   field) for exactly this problem; the org-level scaffold has no equivalent,
   so an agent picking up `AAASM-9999` cold has to guess or ask every time.
2. **No worktree *directory*-naming convention at the org level.**
   `02-git-workflow.md` and the skills specify *branch* naming precisely, but
   never specify what the sibling worktree directory itself should be called
   (only branch name is standardized). Again, the user's own global
   `~/.claude/CLAUDE.md` has a documented convention for this
   (`<repo>-<release>-<ticket>-<type>-<summary>`); nothing in `.github`'s
   scaffold mirrors it, so worktree directory names can drift between
   contributors, agents, or tools with no way to tell from the directory
   name alone which branch it tracks without checking.

---

## Claude Code vs. Codex comparison

`AGENTS.md` is explicit that `.claude/rules/` and `.claude/skills/` are
Claude-Code-specific constructs with "no native equivalent loader" for
Codex. Comparing content side-by-side:

**Genuinely duplicated in `AGENTS.md` (Codex loses nothing here):** product
paragraph, repo map, commit/branch/PR string formats, remote-naming quirk
(`remote` vs `origin`, lowercase org id), CI-billing-block reality, JIRA
field IDs (Component `customfield_10041`, Team `customfield_10001`),
self-hosting/spec-location project policy.

**Present only in `.claude/rules/*.md`, with zero inline content in
`AGENTS.md`** — a Codex session has no way to discover these exist except by
being told to go read the directory manually, and `AGENTS.md`'s own wording
("Codex has no native equivalent loader for these files") could easily read
as "don't bother looking there":
- `05-context-boundary.md`'s private-vs-public cross-repo rule (don't
  paraphrase a private repo's internals into a public repo's commit/PR/
  comment) — a real, non-trivial org policy given several repos in this org
  are private and several public, and it exists in exactly one place.
- `04-agent-escalation.md`'s structured escalation-phrasing template.
- `06-audit-trail.md`'s two-comment Jira cadence (starting-work,
  PR-opened) and the "state what you're stacked on" convention for PRs.
- `01-security.md`'s explicit dangerous-command list (`curl | bash`,
  `--no-verify`, force-push, `git reset --hard`/`clean -fd`) — CLAUDE.md's
  "CI reality" section only covers `--no-verify`/force-push in passing;
  the fuller list lives only in the rule file.

**Present only as `.claude/skills/*.md` procedural playbooks, with no
equivalent at all for Codex:** all 7 skills. `AGENTS.md` gives Codex the raw
facts but no step-by-step procedure — e.g. nothing tells a Codex session
that a ticket must be transitioned to "In Progress" *before* code is written
(only in `task-intake.md`), or gives it the `pr-review.md` self-check list
before opening a PR. A Codex session reconstructing the same workflow from
`AGENTS.md` alone would have to infer the procedure from the facts, with
higher risk of skipping a step a Claude Code session gets handed explicitly.

**Conclusion: `AGENTS.md` is self-sufficient for facts, not for process or
for two specific policy areas (context boundary, audit-trail cadence) that
currently exist only in Claude-Code-only files.** See Improvement item 6.

---

## Improvement items (for AAASM-3947 to triage)

1. Update `onboard-org.md` step 4 to drop the "once AAASM-3943 ships /
   exact CLI interface TBD" hedge now that the script exists with a known,
   stable interface (`bootstrap-ai-workspace.sh <workspace-root-path>
   [--dry-run]`), and add a step covering `validate-ai-workspace.sh`
   (currently absent from every skill file).
2. Add explicit steps + exact invocation for both
   `bootstrap-ai-workspace.sh` and `validate-ai-workspace.sh` to
   `setup-dev-env.md` — currently the skill most on-the-nose for "set up my
   local workspace" never names either script.
3. Fix the mismatch between `.claude/WORKSPACE.md`'s override-model claim
   ("the validation script flags [per-file rule/skill] overrides") and
   `validate-ai-workspace.sh`'s actual behavior (verified: it only checks
   workspace-root-level items and, for repo paths, only whether
   `.claude/CLAUDE.md`/`AGENTS.md` exist — it never inspects a repo's own
   `.claude/rules/*.md` or `.claude/skills/*.md` for filename collisions
   with the org baseline). Either implement the per-file check or correct
   the `WORKSPACE.md` claim.
4. Add an org-level worktree **directory**-naming convention (only branch
   naming is currently standardized in `02-git-workflow.md`), so worktree
   sibling-directory names don't drift between contributors/agents/tools.
5. Add a `<release-or-phase>` resolution mechanism for `02-git-workflow.md`
   (env var / marker file / Jira milestone field, or similar) — currently
   only a worked example exists, with no way to determine the current phase
   prefix for a brand-new ticket without guessing or asking.
6. Inline at least a one-paragraph summary of `05-context-boundary.md`'s
   private/public cross-repo rule and `06-audit-trail.md`'s Jira
   start/PR-opened comment cadence into `AGENTS.md` — both are org-wide
   policy, not Claude-Code mechanics, but currently exist only in
   Claude-Code-only files with just a generic "read the file directly if in
   doubt" pointer.
7. Add a CI check that keeps the scaffold internally consistent going
   forward — e.g. that `CLAUDE.md`/`AGENTS.md` stay in sync on shared
   sections, that skills referencing script names match the scripts'
   actual `--help` output, and that `validate-ai-workspace.sh` runs clean
   against a checked-in fixture. Without this, drift like items 1–2 above
   will keep recurring silently every time a dependency ticket ships after
   the skill referencing it was written.
8. Add a version pin or changelog on the org-baseline files themselves
   (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, `.claude/skills/*.md`).
   A breaking change (e.g. to the branch-naming convention or the JIRA
   Component field ID) currently propagates silently to every downstream
   repo the next time its symlink is read, with no changelog entry for a
   downstream maintainer to notice.
9. The override model has only been exercised synthetically (this ticket's
   throwaway fake-repo test, and 3945's read-only survey which found zero
   existing overrides in `agent-assembly`/`python-sdk`/`agent-assembly-
   docs`). Track a natural follow-up to verify the override path against a
   real repo once any repo actually needs one — until then, item 3 above is
   unverified against a real end-to-end case.
10. The full chain has never been tested against `master` post-merge —
    every integration test so far (3945's and this one) used a disposable
    local merge of still-unmerged branches. Once PR #25 through this
    ticket's PR actually land on `master` (presumably as separate,
    sequential PR merges rather than one octopus merge), do a lightweight
    post-merge smoke check (`bootstrap`/`validate` from a fresh clone of
    `master`) to confirm GitHub's actual merge sequence didn't resolve
    anything differently than the local disposable merges did.
11. `choose-repo.md`'s decision table resolves clean examples well but gives
    no tie-breaking guidance for a task that plausibly spans two rows (e.g.
    "improve the error message shown when the SDK can't reach the gateway"
    could be `python-sdk`-side or `agent-assembly`/`aa-runtime`-side).
    "Ask" is a fine default, but one worked ambiguous-case example would
    reduce back-and-forth.
12. Decide, at the Epic level, whether a lightweight "what's the current
    state of this Epic across all its stacked branches/PRs" command (e.g.
    wrapping `gh pr list` + `git branch --list` + a Jira JQL query) belongs
    in this org scaffold, given the returning-maintainer story today is
    just two advisory markdown files with no equivalent to the user's own
    global session-continuity tooling (`workflow-state.sh`,
    `decision-log.sh`, `session-memory.sh`). Not a defect — just an
    explicit scope call this Epic hasn't made yet.
