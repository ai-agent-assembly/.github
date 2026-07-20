# `metadata/` — canonical org-shared metadata registry

`org-profile.yaml` is the **single canonical registry** for the org's shared,
non-version metadata — the facts that used to be hand-copied across repos and
drifted silently on every rename or URL change. The design decision this
implements is [ADR 0014](https://github.com/ai-agent-assembly/agent-assembly/blob/master/docs/src/adr/0014-canonical-metadata-registry-and-drift-gate.md)
(canonical metadata registry & drift gate); read it for the rationale and the
public/private boundary rules. Version metadata is out of scope here — it is
owned by ADR 0013.

## What the registry owns

`org-profile.yaml` holds these sections, each value with **exactly one owner**
(no consumer may re-declare a value the registry owns):

| Section | Holds | Owner note |
|---|---|---|
| `org` | the org slug (`ai-agent-assembly`) | slug's single owner — `product` does **not** repeat it |
| `product` | product / org display names, published security email | — |
| `urls` | canonical marketing/app/api/docs/status/installer hosts + per-SDK docs bases | **values owned by ADR 0007/0008**; stored here, not re-decided |
| `governance` | the `.github` default branch + baseline-doc link base | stops `main` vs `master` link drift |
| `jira` | public coordination constants (site, project key/id, board id, custom-field IDs) | Components is the **native** field — `customfield_10041` is null on AAASM |
| `repos[]` | per-repo `slug` / `repo` / `default_branch` / `visibility` / `role` + badge/version/activity | badges/versions are README presentation, not shared metadata |
| `install_channels[]` | install-snippet definitions for the profile README | — |

**Visibility boundary.** Every `repos[]` entry carries `visibility: public |
private`. A generated **public** artifact must never emit a private repo's slug
or metadata, so the generator filters on this flag. Private repos are simply not
listed in this public file at all — and no secret or private-repo internal ever
belongs here (see ADR 0014's forbidden designs).

## Generated artifacts

`scripts/generate_org_profile.py` derives two artifacts from the registry:

- **`../profile/README.md`** — the org front door. The generator rewrites the
  bounded `<!-- BEGIN GENERATED: repo_table -->` and `install_channels` regions;
  everything outside those markers is hand-authored prose.
- **`generated/registry.json`** — a machine-readable, **visibility-filtered**
  projection of the shared facts (public repos only, identity fields only) that
  cross-repo consumers read instead of hand-copying a value. It is **generated —
  do not edit by hand**; change the registry and regenerate.

## Changing a shared value

1. Edit `org-profile.yaml` (for a URL, follow ADR 0007/0008 → registry → consumers).
2. Regenerate both artifacts:
   ```bash
   python3 scripts/generate_org_profile.py
   ```
3. Commit the registry change **and** the regenerated artifacts together.

Never hand-type a value the registry owns into another file, and never hand-edit
a generated artifact.

## Drift gate

`.github/workflows/org-profile-drift.yml` runs the generator in `--check` mode on
every PR/push that touches the registry, the generator, or a generated artifact
(and weekly). `--check` regenerates in memory and exits non-zero on any diff,
without writing — so a stale README or `registry.json` fails CI:

```bash
python3 scripts/generate_org_profile.py --check   # exit 0 = in sync, 1 = drift
```

## Scope

This is the **foundation** (AAASM-4913): the widened registry, the generator, the
`registry.json` projection, and the drift gate. Converting the many hand-copied
usages across the other repos to consume the registry (and the ADR's
hardcoded-value lint for free prose) is the **rollout**, tracked separately as
AAASM-4914 — it is deliberately not done here.
