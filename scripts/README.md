# `scripts/`

Org-level AI onboarding scripts for the `ai-agent-assembly` org (Epic AAASM-3938).
See `.claude/WORKSPACE.md` for the workspace layout these scripts install and
validate against.

## `bootstrap-ai-workspace.sh` (AAASM-3943)

Installs the org AI baseline — `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`,
`.claude/skills/` — from this repo into a contributor's local multi-repo
workspace root, so Claude Code and Codex see shared org context regardless of
which repo they're invoked from.

### Usage

```bash
./scripts/bootstrap-ai-workspace.sh ~/ai-agent-assembly
```

Run it from inside a local clone of `ai-agent-assembly/.github` (the script
locates its own repo checkout automatically, via its own path). The workspace
root path does not need to exist yet — it's created if missing.

### `--dry-run`

Prints exactly what would be created, updated, or skipped without touching the
filesystem:

```bash
./scripts/bootstrap-ai-workspace.sh ~/ai-agent-assembly --dry-run
```

Use this before the first real run, or any time you want to check the current
state of a workspace root against this repo's baseline.

### Symlinks, not copies

The script **symlinks** (does not copy) `CLAUDE.md`, `AGENTS.md`,
`.claude/rules/`, and `.claude/skills/` into the workspace root. This means a
`git pull` in your `.github` checkout is picked up immediately everywhere it's
installed — no need to re-run the script after every org-baseline change.

### Re-running is safe (idempotent)

Running the script again after it already succeeded is a no-op for anything
already correctly installed — those items are reported as `skipped (up to
date)`. If a previously-installed symlink is broken (e.g. you moved or
re-cloned this `.github` repo), the script detects that and relinks it,
reported as `updated`.

### "skipped (local override)"

The script **never overwrites** a file, directory, or symlink at the target
path that isn't already the exact symlink this script would create. If you see
`skipped (local override)` in the summary, it means something already exists
there that doesn't point back at this repo — most commonly because you
intentionally replaced the installed copy with your own local version.

If that's a mistake and you actually want the script to (re-)install the org
baseline there, remove the stale file/symlink yourself first, then re-run the
script:

```bash
rm ~/ai-agent-assembly/CLAUDE.md     # or whichever path was reported
./scripts/bootstrap-ai-workspace.sh ~/ai-agent-assembly
```

The script will not do this removal for you — that's a deliberate safety
choice so a contributor's local override is never silently clobbered.

### Summary output

Every run ends with a per-item report line (`[created]`, `[updated]`,
`[skipped]`, or `[failed]`) plus aggregate counts. The script exits non-zero
if any item failed.

## `validate-ai-workspace.sh` (AAASM-3944, not yet built)

Planned companion script that will check an installed workspace (and each
selected repo inside it) against `.claude/WORKSPACE.md`'s expected layout,
reporting missing files, broken symlinks, and visible repo-local overrides. It
will live alongside `bootstrap-ai-workspace.sh` in this directory once built.
