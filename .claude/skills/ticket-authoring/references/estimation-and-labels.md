# Estimation scale & label taxonomy

Canonical values for AAASM tickets. Keep both small and consistent.

## Story points (`customfield_10016`) — Fibonacci

Estimate **effort + uncertainty**, not hours. Story/Task/Bug carry points; an
Epic has none (its points = the **sum of its children**).

| Pts | Size | Rule of thumb |
|---|---|---|
| **1** | trivial | one file / one mechanical change; < ½ day; no unknowns |
| **2** | small | a couple of files or one cohesive change; ~½–1 day |
| **3** | moderate | multi-file change or a small refactor + tests; 1–2 days |
| **5** | large | a substantial slice; touches several modules; ~½ sprint |
| **8** | very large | broad or uncertain — **strongly consider splitting** |
| **13** | too big | do **not** implement as one ticket — split into Stories/Tasks |

Guidance: if you're between two values, round up. Anything ≥ 8 should be
decomposed before work starts. Bugs are pointed by fix effort, not severity.

## Labels — canonical taxonomy

Lowercase kebab-case. Apply **at least one work-type** label; add
source/severity/lifecycle where they apply; keep the set tight (usually 2–4).

**Work type** (pick ≥1): `feature` · `bug` · `refactor` · `tech-debt` ·
`test` · `docs` · `config` · `ci` · `security` · `coverage` · `performance`

**Source / tooling** (how it was found): `sonarcloud` · `codeql` ·
`dependabot` · `finding` · `analysis`

**Severity** (findings/bugs): `sev-high` · `sev-medium` · `sev-low`

**Lifecycle**: `follow-up` · `blocked` · `spike`

**Initiative** — per-program tags added as needed, e.g. `user-journey-sim`,
`track-nondev` (existing). Reuse an existing initiative tag; don't invent
near-duplicates.

Do **not** duplicate structured fields as labels (no `epic`, no repo names —
repo goes in Components; type is the issue type).

### Examples
- SonarCloud maintainability cleanup Story: `sonarcloud`, `tech-debt`
- IaC security fix: `sonarcloud`, `tech-debt`, `security`
- Coverage-wiring follow-up: `sonarcloud`, `coverage`, `follow-up`
- Verification-found defect: `bug`, `finding`, `sev-medium`
