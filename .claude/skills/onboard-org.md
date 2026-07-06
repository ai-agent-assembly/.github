# Skill: onboard-org

**When to use:** you (human or AI) are working in the `ai-agent-assembly` org
for the first time this session — either a fresh machine, a fresh contributor,
or a fresh agent context with no prior memory of this org.

## Steps

1. **Read the org baseline.** Claude Code: read `CLAUDE.md` at the root of
   whichever repo you're in (it links back to `.github`'s `CLAUDE.md` as the
   canonical source). Codex or any other `AGENTS.md`-reading tool: read
   `AGENTS.md` instead — same content, Codex-facing. Do not skip this even if
   the task looks small; it covers commit/branch/PR conventions, remote
   naming, CI reality, and JIRA field mapping you will need immediately. Also
   read `.claude/rules/01-security.md` specifically before writing any code —
   of everything in `.claude/rules/`, it's the one with real blast radius if
   skipped.
2. **Confirm the workspace layout**, if you're operating from a multi-repo
   workspace root rather than a single repo checkout — see
   `.claude/WORKSPACE.md` in `.github` for the expected layout
   (`~/ai-agent-assembly/<repo>/` siblings, org files installed at the root).
3. **Pick the repo relevant to your task** — see the `choose-repo` skill for
   the decision tree. Don't guess from the ticket title alone; check the
   ticket's Component field first.
4. **Bootstrap your local workspace.** The org baseline (`CLAUDE.md`,
   `AGENTS.md`, `.claude/rules/`, `.claude/skills/`) installs into a
   workspace root via:
   ```
   ./scripts/bootstrap-ai-workspace.sh <workspace-root-path> [--dry-run]
   ```
   run from a local clone of `.github`. It symlinks the baseline in (so a
   later `git pull` in `.github` propagates automatically) and never
   clobbers a file that isn't the symlink it expects — see
   `scripts/README.md` for the full behavior.
5. **Validate the bootstrap worked.** Run
   `./scripts/validate-ai-workspace.sh <workspace-root-path>` (optionally
   passing one or more repo paths for a lightweight repo-level check too) —
   it reports missing files, broken symlinks, and any local override, with a
   non-zero exit if something's actually broken.
6. **Read the target repo's own `.claude/CLAUDE.md` (or `AGENTS.md`)** before
   writing any code. Repo-local files override or extend the org baseline for
   that repo — build/test/lint commands, directory conventions, and gotchas
   live there, not in the org baseline.

## Do not

- Do not restate org policy (commit format, branch format, remote naming,
  JIRA fields) in task output — link back to `CLAUDE.md`/`AGENTS.md` instead.
- Do not assume a repo's default branch or canonical remote name — both vary
  per repo. Confirm with `git remote -v` and
  `git ls-remote --symref <remote> HEAD` (see `setup-dev-env`).
