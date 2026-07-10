# `.github`

Community-health, org-profile, reusable workflows, and shared AI-tooling
baseline for the [`ai-agent-assembly`](https://github.com/ai-agent-assembly)
GitHub organization.

## What lives here

| Path | Purpose |
| --- | --- |
| `profile/README.md` | Rendered by GitHub as the [org profile page](https://github.com/ai-agent-assembly) — the public front door |
| `metadata/org-profile.yaml` | Source of truth for the profile's badge tables and install snippets |
| `scripts/generate_org_profile.py` | Regenerates the bounded blocks of `profile/README.md` from the SoT |
| `.github/workflows/org-profile-drift.yml` | CI gate that fails if `profile/README.md` drifts from the SoT |
| `.github/workflows/ci-success.yml` | Reusable "CI Success" aggregate gate for branch-protection |
| `.github/ISSUE_TEMPLATE/` | Org-wide issue templates |
| `.github/PULL_REQUEST_TEMPLATE.md` | Org-wide PR template |
| `.github/CODEOWNERS` | Default reviewers |
| `workflow-templates/` | Starter GitHub Actions workflows for new repos |
| `scripts/bootstrap-ai-workspace.sh` | Installs the org AI baseline into a contributor's local workspace (AAASM-3943) |
| `scripts/validate-ai-workspace.sh` | Validates an installed workspace against the baseline (AAASM-3944) |
| `CLAUDE.md`, `AGENTS.md` | Org-wide AI-tooling baseline (referenced by every repo's local variants) |
| `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md` | Org-wide community-health files |

## Org-profile generation

The org front door at [github.com/ai-agent-assembly](https://github.com/ai-agent-assembly)
is rendered from `profile/README.md`. Two parts of that file are drift-prone:

1. **Repository Status** — one badge-heavy row per public repo. Repo renames,
   default-branch changes, SDK package-id changes all silently break links.
2. **Install channels** — one code snippet per install channel. Renamed
   packages, moved installer URLs, and new channels all need to land in lockstep.

Both blocks are generated from a single source of truth
(`metadata/org-profile.yaml`) by `scripts/generate_org_profile.py`, so a rename
in one place lands in all badge/install references at once.

### How the bounded blocks work

The generator only touches content between HTML-comment sentinels:

```
<!-- BEGIN GENERATED: <id> -->
...generated content...
<!-- END GENERATED: <id> -->
```

Everything outside the sentinels — the org one-paragraph pitch, "Sample code
starts here", Full Production Highlights, Documentation and Community, Release
Notes — stays literal. HTML comments render invisibly on GitHub, so the public
page looks identical before and after.

### Regenerating after editing the SoT

Edit `metadata/org-profile.yaml`, then run:

```sh
python3 scripts/generate_org_profile.py
```

The generator is stdlib-only (Python 3.9+), so it works with the OS `python3`
on macOS, Linux, and any GitHub Actions runner — no `pip install` needed.
Commit both the SoT change and the regenerated README in one PR.

### Drift enforcement

`.github/workflows/org-profile-drift.yml` runs
`python3 scripts/generate_org_profile.py --check` on every PR that touches
the SoT, the generator, the README, or the workflow itself — plus weekly on
schedule to catch hand-edits. The check exits non-zero (with a hint pointing
at the generator command) if regeneration would change the README.

### Adding a new repo or install channel

1. Edit `metadata/org-profile.yaml` — append a new `repos:` entry or
   `install_channels:` entry following the shape of the existing ones.
2. Run `python3 scripts/generate_org_profile.py`.
3. Review the diff to `profile/README.md`, commit both files together.

For a new repo, mirror the pattern that best matches its role: SDK repos use
`tag_prefix: SDK` with the language's brand color; docs / tap / examples repos
each have their own convention documented alongside the existing entries.
