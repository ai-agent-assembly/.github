# Org-level AI workspace layout (AAASM-3938 onboarding POC)

Defines how a local machine should be laid out so Claude Code, Codex, and other
AI coding tools can discover shared `ai-agent-assembly` org context without a
human re-explaining it every session, while every repo keeps the ability to
override or extend that context locally.

## Layout

```text
~/ai-agent-assembly/                  # workspace root (not itself a git repo)
├── CLAUDE.md                         # symlink/copy of .github's CLAUDE.md
├── AGENTS.md                         # symlink/copy of .github's AGENTS.md
├── .claude/
│   ├── rules/                        # symlink/copy of .github's .claude/rules
│   ├── skills/                       # symlink/copy of .github's .claude/skills
│   └── commands/                     # reserved for future org-level commands
├── .github/                          # clone of ai-agent-assembly/.github (source of truth)
├── agent-assembly/                   # clone of ai-agent-assembly/agent-assembly
├── python-sdk/                       # clone of ai-agent-assembly/python-sdk
├── node-sdk/                         # clone of ai-agent-assembly/node-sdk
├── go-sdk/                           # clone of ai-agent-assembly/go-sdk
└── <other-repo>/                     # any other org repo the contributor has cloned
```

## Responsibilities

### Workspace root (`~/ai-agent-assembly/`)

- Holds **installed copies** of the org baseline (`CLAUDE.md`, `AGENTS.md`,
  `.claude/rules/`, `.claude/skills/`), placed there by the bootstrap script
  (AAASM-3943) — never hand-edited in place, since a re-run of the script
  overwrites them from source.
- Is a plain directory, not a git repository. It exists only so AI tools
  invoked from the workspace root (rather than from inside one repo) still see
  org-wide context.
- Contains one subdirectory per cloned org repo, named to match the repo.

### Each repo root (e.g. `agent-assembly/`, `python-sdk/`)

- Owns its own `.claude/CLAUDE.md` / `AGENTS.md` with repo-specific commands,
  build/test/lint instructions, and gotchas.
- Repo-local files **reference** the org baseline instead of duplicating it —
  see the existing convention already documented in `.github`'s own
  `CLAUDE.md` ("Each repo also has its own `.claude/CLAUDE.md` ... those files
  reference this baseline instead of repeating it").
- A repo-local rule or skill with the same filename as an org-level one in
  `.claude/rules/` or `.claude/skills/` **overrides** it for that repo; the
  validation script (AAASM-3944) flags overrides so they're visible, not
  silent.

### `ai-agent-assembly/.github` repo — role

- **Source of truth** for every org-level AI artifact: `CLAUDE.md`,
  `AGENTS.md`, `.claude/rules/`, `.claude/skills/`. All edits to org-wide AI
  context happen here, through normal PR review, never by hand-editing the
  installed copies in a workspace root.
- Also the **bootstrap source**: `AAASM-3943`'s script reads from a local
  clone of this repo (or fetches it) and installs/symlinks its artifacts into
  the workspace root.
- Already hosts org community-health files (`CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `CONTRIBUTING.md`) and reusable CI workflow templates —
  the AI scaffold lives alongside those as one more org-wide default.

## Override model

1. Org baseline (`.github`) defines the default.
2. Bootstrap script installs it into the workspace root.
3. A repo may add its own `.claude/CLAUDE.md`, `.claude/rules/*.md`, or
   `.claude/skills/*.md` that takes precedence *for that repo* — Claude Code
   and Codex both resolve context from the current working directory outward,
   so a repo-local file is naturally read before/instead of the workspace-root
   copy once you `cd` into the repo.
4. Nothing is deleted or merged automatically — an override is a distinct file
   that shadows the org-level one by filename; the validation script reports
   which org-level files are shadowed so the override is a visible, reviewable
   decision instead of silent drift.

## Claude Code and Codex discovery assumptions

- **Claude Code** reads the `CLAUDE.md` in the current working directory (repo
  root) plus the user's global `~/.claude/CLAUDE.md`. It does **not** reach
  across repos or fetch `.github` automatically — this is a convention enforced
  by the bootstrap/validation scripts, not a platform feature. `.claude/rules/`
  and `.claude/skills/` are loaded on demand from whatever `.claude/` directory
  is nearest the working directory.
- **Codex** reads `AGENTS.md` the same way — nearest-directory-wins, no
  cross-repo auto-discovery. The org baseline `AGENTS.md` (AAASM-3940) must
  therefore be physically present (installed by bootstrap) in any directory a
  contributor expects Codex to pick it up from.
- Both tools are blind to files that exist only in the remote `.github` repo
  and not in a local clone or installed copy — this is why the bootstrap
  script (AAASM-3943), not a README instruction, is the actual delivery
  mechanism for org-wide context.

## Consumers of this doc

- AAASM-3943 (bootstrap script): installs the four artifacts above into the
  layout defined here.
- AAASM-3944 (validation script): checks the workspace root and each selected
  repo match this layout and reports missing files, broken symlinks, and
  visible overrides.
