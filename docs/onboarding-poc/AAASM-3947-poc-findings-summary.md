# AAASM-3947 — POC findings summary for ArcheWeave extraction

Epic AAASM-3938 (org-level AI onboarding POC). This is the final ticket of
the Epic: pure synthesis of what AAASM-3939 through AAASM-3946 built and
found, aimed at a reader (the ArcheWeave project owner) deciding what to
extract out of this POC into a reusable, cross-org product. **No new
scripts or scaffold content were written for this ticket** — every claim
below cites the mechanical test (AAASM-3945) or the qualitative dogfooding
pass (AAASM-3946) that established it.

---

## 1. Effective artifacts

These proved genuinely useful, with a specific test or observation behind
each claim (not just "seems fine"):

- **`.claude/WORKSPACE.md` (3939)** — the layout doc itself was never
  falsified: 3945's full merge-and-run test and 3946's dogfooding both
  operated exactly per the layout it describes (workspace root with
  symlinked `CLAUDE.md`/`AGENTS.md`/`.claude/rules`/`.claude/skills`, one
  subdirectory per cloned repo). The one place it diverges from reality is
  the override-detection claim — see §4, not a knock against the layout
  design itself.
- **`choose-repo.md` (3942)** — 3946 ran two concrete routing tasks through
  its decision table ("fix a typo in the Python SDK docs" and "add a new
  gateway policy rule") plus a third hypothetical in Scenario 4
  (`AAASM-9999`, a gateway policy bug) and all three resolved to the
  correct repo unambiguously, with no dead ends. This is the single
  clearest "worked exactly as designed" result in the whole POC.
- **`bootstrap-ai-workspace.sh` (3943)** — 3945's end-to-end test and
  3946's repeat run against a fresh `/tmp` scratch workspace both matched
  the script's own `README.md`/`--help` exactly: correct `--dry-run` vs.
  real-run parity, correct counts (`created=N updated=0 skipped=0
  failed=0` on first run), and confirmed idempotent on re-run (`created=0
  ... skipped=7 failed=0`, 3945). The symlink-over-copy design decision
  (documented in the script's own header) was validated concretely: 3945
  confirmed `SCRIPT_DIR` resolution survives being run from a multi-branch
  merged checkout rather than any single source branch.
- **`validate-ai-workspace.sh` (3944)** — reported accurate results in
  every real run (`missing=0 broken=0 override=0 ok=4`, 3945; same in
  3946's Scenario 1/3 runs), and its exit-code contract (0 = safe CI gate)
  held up under test. Its one substantive gap is the override-detection
  claim, addressed as a defect below rather than as "ineffective" — the
  parts of the script that were exercised behaved exactly as documented.
- **`02-git-workflow.md` (3941)** — 3946's Scenario 4 specifically credits
  it for giving a literal, runnable command
  (`git worktree add -b <new-branch> <path> <dependency-branch>`) for the
  stacked-branch case, rather than just prose describing the convention.
- **`04-agent-escalation.md` (3941)** — 3946 found its three-part
  escalation template (blocking / tried / decision-needed) well-specified,
  and noted approvingly that it's scoped as a guardrail that correctly
  *wouldn't* fire for a well-scoped task — a sign the trigger condition is
  reasonable, not just the template content.
- **`task-intake.md` (3942)** — both the general five-step onboarding flow
  (3946 Scenario 1) and the ticket-specific version (Scenario 4: read
  ticket → confirm repo via Component field → check dependencies →
  transition + comment → branch/worktree) were exercised and judged
  "complete and ordered correctly," with no missing step found for either
  the first-time-contributor or the ticket-pickup path.

## 2. Low-value or high-maintenance artifacts

Being honest, per the ticket's ask — not everything justified its own file:

- **The 6-way split of `.claude/rules/*.md` is only partly earning its
  keep.** Two files (`02-git-workflow.md`, `04-agent-escalation.md`) were
  independently praised in 3946 for concrete, actionable content. But
  3946's own "returning maintainer" scenario gave `06-audit-trail.md` a
  blunt "modest help, not a real accelerant" verdict — it mostly restates
  conventions (gitmoji commits, `[<ticket>]` PR titles) that are already
  self-evident from `git log`/PR list, with no runnable command or index
  behind it. That specific file adds a filename and a maintenance surface
  without adding a capability beyond what's already implicit elsewhere.
  Whether the fix is "merge it into a smaller file" or "give it a
  discovery command" is a productization judgment call, not something this
  ticket resolves — but the current 6-file split should not be assumed
  correct by default.
- **`AGENTS.md`'s "entry point, not a knowledge dump" design is currently
  too thin in exactly the wrong place.** 3946's side-by-side comparison
  (see §3) found `AGENTS.md` fully duplicates the *factual* content that's
  cheap to duplicate (repo map, string formats, JIRA field IDs) but has
  **zero inline content** for two items that are genuine org policy, not
  Claude-Code mechanics: `05-context-boundary.md`'s private/public
  cross-repo rule, and `06-audit-trail.md`'s two-comment Jira cadence. A
  Codex session has no on-demand fallback to discover these — the
  asymmetry described in §3 means the current AGENTS.md size is arguably
  wrong in the specific dimension that matters most (policy Codex would
  otherwise silently miss), even though it's "right-sized" for the facts
  it does carry. This is not an argument for a bigger knowledge-dump
  AGENTS.md across the board — just that these two specific gaps should be
  closed (folded into Improvement item 6 below).
- **All 7 `.claude/skills/*.md` procedural playbooks have zero equivalent
  for Codex**, by design (3946's comparison: "no equivalent at all"). This
  is flagged here as a maintenance-cost fact, not a defect: every future
  edit to a skill's *procedure* (as opposed to its underlying facts) is
  Claude-Code-only leverage. Worth knowing going into productization so
  the split of "what goes in a skill" vs. "what goes in AGENTS.md" is a
  deliberate call each time, not an accident of which file was open.

## 3. Claude Code vs. Codex differences

3946 ran a direct side-by-side comparison (see its "Claude Code vs. Codex
comparison" section) and the structural picture is:

- **Claude Code** gets two tiers: always-loaded `CLAUDE.md`/`AGENTS.md`
  facts, *plus* on-demand `.claude/rules/*.md` and `.claude/skills/*.md`
  (procedures and deeper policy) that get pulled in when relevant.
- **Codex** gets exactly one tier: whatever is physically written into
  `AGENTS.md`. There is no on-demand fallback — `.claude/rules/` and
  `.claude/skills/` have, per 3946, "no equivalent at all" for Codex.

**This asymmetry is structural, not a bug** — it's an accurate reflection
of what each tool's loader actually does (`.claude/WORKSPACE.md`'s own
"Claude Code and Codex discovery assumptions" section documents this
correctly). But it has a direct consequence for productization: **because
Codex has no on-demand fallback, `AGENTS.md` maintenance carries higher
stakes than any single rule or skill file** — a gap in a `.claude/rules/`
file costs a Claude Code session one skipped detail; the same gap in
`AGENTS.md`, if that content doesn't exist anywhere else Codex can reach,
costs every Codex session working in that repo. 3946's finding that
`05-context-boundary.md` and `06-audit-trail.md` content is currently
invisible to Codex (§2 above) is the concrete instance of this general
risk, and should be treated as the first thing to close before treating
`AGENTS.md` as "done."

## 4. Verified defect carried forward

**3946 found and mechanically verified a real mismatch** (not a
suspicion, not an untested path) between what `.claude/WORKSPACE.md`
documents and what `validate-ai-workspace.sh` actually does:

- `.claude/WORKSPACE.md`'s "Override model" section states: *"A repo-local
  rule or skill with the same filename as an org-level one... the
  validation script (AAASM-3944) flags overrides so they're visible, not
  silent."*
- 3946 tested this directly: created a fake repo directory with its own
  `.claude/rules/01-security.md` (a genuine per-file override of an
  org-level rule filename) and ran `validate-ai-workspace.sh <workspace>
  <fake-repo>` against it. **Result: `override=0`, no indication of the
  shadowed file.** The script's repo-path check only looks for the
  *existence* of `.claude/CLAUDE.md`/`AGENTS.md` at a repo's root — it
  never inspects a repo's own `.claude/rules/` or `.claude/skills/`
  contents for filename collisions against the org baseline.

**Recommendation (flagging both options, not deciding for the epic
owner):**
1. Extend `validate-ai-workspace.sh` to actually walk a repo's
   `.claude/rules/*.md` and `.claude/skills/*.md` and report filename
   collisions against the org baseline as overrides, so the script's
   behavior matches the doc's claim; **or**
2. Correct `.claude/WORKSPACE.md`'s override-model wording to state
   plainly that per-file rule/skill overrides are not currently detected
   by tooling and rely on the natural "nearest-directory-wins" read
   behavior of Claude Code/Codex, with detection as a stated future gap
   rather than a documented-as-shipped capability.

Either is a legitimate fix; shipping neither leaves a documented capability
that doesn't exist, which is the worse of the two states.

## 5. Scripts → CLI commands

- **`bootstrap-ai-workspace.sh` is a strong candidate for `archeweave
  init`.** It has a single clear responsibility (install/symlink the
  baseline into a workspace root), a stable, minimal interface
  (`<workspace-root-path> [--dry-run]`), was proven idempotent and
  side-effect-free under repeat runs (3945), and the semantics
  (`created`/`updated`/`skipped`/`failed` counters) map directly onto what
  users expect from a project scaffolding `init` command.
- **`validate-ai-workspace.sh` is a strong candidate for `archeweave
  doctor`.** Its exit-code contract (0 = healthy, 1 = missing/broken) is
  already CI-gate-shaped, and its output categories (missing / broken /
  override / ok) map cleanly onto a `doctor`-style health report. It
  should not become a CLI subcommand *before* the defect in §4 is
  resolved — a `doctor` command with a documented check that silently
  no-ops would ship the same trust gap at CLI scale instead of script
  scale.
- Both scripts are currently self-contained, dependency-free bash with no
  network calls (by design, noted in both scripts' own headers) — this is
  a property worth preserving if/when they're reimplemented as CLI
  subcommands rather than adding new runtime dependencies casually.
- Nothing else in the POC (the rule/skill markdown files, `WORKSPACE.md`)
  is script-shaped; they're content, not behavior, and have no obvious CLI
  translation — they'd remain as templated files an `archeweave init`
  installs, not as subcommands themselves.

## 6. Artifacts → reusable ArcheWeave templates

**Generalizes cleanly to any org (the *shapes*, not this org's content):**

- The `.claude/WORKSPACE.md` layout model itself (workspace root +
  symlinked baseline + per-repo clones + override-by-filename resolved via
  nearest-directory-wins) is org-agnostic — it doesn't reference anything
  `ai-agent-assembly`-specific in its structure.
- The **shape** of the 6-file `.claude/rules/` split (security /
  git-workflow / coding-standards / agent-escalation / context-boundary /
  audit-trail) is a reasonable generic taxonomy any multi-repo org could
  reuse as category headers, even though (per §2) whether 6 files vs. fewer
  is the right count should be re-judged per adopting org rather than
  copied uncritically.
- The **shape** of the 7-file `.claude/skills/` playbooks (onboard-org,
  choose-repo, setup-dev-env, task-intake, contribution-guide, pr-review,
  issue-classification) is a generalizable procedural taxonomy — "how does
  a new contributor get oriented," "how do I pick the right repo," "how do
  I pick up a ticket" are universal multi-repo-org questions.
- `bootstrap-ai-workspace.sh` / `validate-ai-workspace.sh`'s *mechanics*
  (symlink-not-copy install, dry-run/real-run parity, missing/broken/
  override/ok classification) generalize directly — the install source and
  target paths are already parameterized as script arguments, not
  hard-coded.
- The **AGENTS.md vs. CLAUDE.md dual-file pattern** (one Codex-facing entry
  point kept in sync with one Claude-Code-facing baseline on shared
  content) is itself a reusable template shape, independent of this org's
  specific facts.

**Hard-coded to `ai-agent-assembly` — needs templating before reuse:**

- The **repo map** (`agent-assembly`, `python-sdk`, `node-sdk`,
  `go-sdk`, cloud/enterprise/spec placeholders) in both `CLAUDE.md` and
  `AGENTS.md` — this is the single largest chunk of org-specific content
  and the main thing `choose-repo.md`'s decision table depends on.
- **JIRA field IDs** (the native `components` field for Component,
  `customfield_10001` for Team, `customfield_10020` for Sprint,
  `customfield_10016` for Story Points) and the `lightning-dust-mite`
  Atlassian Cloud id — entirely specific to this org's Jira instance and
  would break silently if copied verbatim into another org's `AGENTS.md`.
- The **remote-naming gotcha** (`remote` vs. `origin`, `origin` sometimes
  being a personal fork, lowercase-vs-uppercase org id) is a fact about
  *this org's* git remote conventions, not a universal pattern — a
  template would need this reworded as "detect and document your own
  remote-naming convention here" rather than shipped as this org's
  specific values.
- The **CI-billing-block "CI reality" note** is an operational fact about
  this org's current GitHub Actions billing state, not a generalizable
  policy — it would need to become a "document your org's known CI
  quirks here" placeholder.
- Branch/commit/PR string *conventions themselves* (gitmoji, ticket-number
  bracket format) are somewhat this-org-specific by adoption, even though
  the underlying idea (a fixed, machine-parseable convention) generalizes;
  an adopting org would substitute their own convention rather than
  inherit gitmoji specifically.

## 7. Recommended next productization steps

1. Resolve the §4 defect first (`validate-ai-workspace.sh` vs.
   `WORKSPACE.md`'s override claim) before promoting either script to a
   CLI subcommand — shipping a `doctor` command with a known-false claim
   baked in is worse than shipping it late.
2. Split the artifact set into "template shape" (§6, generalizable) vs.
   "this-org fill-in" (§6, hard-coded) explicitly, and design the
   `archeweave init` scaffolding step around that split (i.e., prompt for
   or config-file the org-specific values rather than hand-editing
   copied files).
3. Re-evaluate the `.claude/rules/` 6-file split and the `AGENTS.md`
   thinness gap (§2) as part of the same pass — don't port the current
   file boundaries mechanically; decide file granularity based on what
   each adopting org's Codex-vs-Claude-Code usage actually needs.
4. Prototype `archeweave init` / `archeweave doctor` as thin wrappers
   around the existing bash logic first, rather than a full rewrite, to
   preserve the zero-network/zero-dependency property validated in this
   POC.
5. Only after 1–4, consider the "Epic-state" tooling gap 3946 flagged
   (returning-maintainer story, Improvement item 12 below) as a distinct,
   separately-scoped feature — it's real but is a different kind of
   capability (session/state tooling) than the onboarding-scaffold work
   this Epic covered.

## 8. Candidate follow-up tickets

The following is a consolidated, deduplicated list of 3946's 12 numbered
improvement items, restated as ticket-sized units. **Filing these in Jira
is a follow-up action for the epic owner — this ticket does not create any
Jira tickets.**

1. Update `onboard-org.md` to drop the "once AAASM-3943 ships / exact CLI
   interface TBD" hedge (the script has shipped with a stable interface)
   and add a step covering `validate-ai-workspace.sh`, which no skill file
   currently mentions.
2. Add explicit steps and exact invocation for both
   `bootstrap-ai-workspace.sh` and `validate-ai-workspace.sh` to
   `setup-dev-env.md` — the skill most on-the-nose for local workspace
   setup currently names neither script.
3. Fix the override-detection mismatch between `.claude/WORKSPACE.md` and
   `validate-ai-workspace.sh`'s actual behavior (see §4 above) — either
   implement per-file collision detection or correct the doc's claim.
4. Add an org-level worktree **directory**-naming convention to
   `02-git-workflow.md` (only branch naming is currently standardized),
   so sibling worktree directory names don't drift between contributors,
   agents, or tools.
5. Add a `<release-or-phase>` resolution mechanism to `02-git-workflow.md`
   (env var / marker file / Jira milestone field, or similar) for a
   brand-new ticket with no existing anchor branch — currently only a
   worked example exists.
6. Inline at least a one-paragraph summary of `05-context-boundary.md`'s
   private/public cross-repo rule and `06-audit-trail.md`'s Jira
   start/PR-opened comment cadence directly into `AGENTS.md`, since both
   are org-wide policy that Codex sessions currently cannot discover on
   their own (see §3).
7. Add a CI check that keeps the scaffold internally consistent — e.g.
   `CLAUDE.md`/`AGENTS.md` stay in sync on shared sections, skills that
   reference script names match the scripts' actual `--help` output, and
   `validate-ai-workspace.sh` runs clean against a checked-in fixture —
   to prevent drift like items 1–2 from recurring silently.
8. Add a version pin or changelog to the org-baseline files themselves
   (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/*.md`, `.claude/skills/*.md`)
   so a breaking change (e.g. to branch naming or a JIRA field ID) doesn't
   propagate silently to every downstream repo with no notice.
9. Track a follow-up to verify the override-detection path (item 3) against
   a real repo once one actually needs a per-file override — so far it has
   only been exercised synthetically (3946's throwaway fake-repo test; 3945
   found zero existing overrides in the three surveyed repos).
10. Once PR #25 through this ticket's PR actually land on `master`
    (presumably as sequential merges), run a lightweight post-merge smoke
    check (fresh clone → `bootstrap` → `validate`) to confirm GitHub's real
    merge sequence didn't resolve anything differently than the local
    disposable merges used throughout this Epic's testing.
11. Add one worked ambiguous-case example to `choose-repo.md`'s decision
    table for a task that plausibly spans two rows (e.g. "improve the SDK
    error message shown when it can't reach the gateway" — could be
    `python-sdk`-side or `agent-assembly`/`aa-runtime`-side), to reduce
    back-and-forth beyond the current default of "ask."
12. Make an explicit Epic-level scope decision on whether a lightweight
    "current state of this Epic across its stacked branches/PRs" command
    (wrapping `gh pr list` + `git branch --list` + a Jira JQL query)
    belongs in this org scaffold at all, given the returning-maintainer
    story today is two advisory markdown files with no equivalent to this
    user's own global session-continuity tooling
    (`workflow-state.sh`/`decision-log.sh`/`session-memory.sh`). This is a
    scope call, not a defect.

Re-consolidated from 3946's original 12 items 1:1 (no items were merged or
dropped) — see AAASM-3946-dogfooding-notes.md's own "Improvement items"
section for the original wording and full context on each.
