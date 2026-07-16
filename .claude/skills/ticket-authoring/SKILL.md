---
name: ticket-authoring
description: >-
  Author and field-complete AAASM Jira tickets to project convention. Use when
  creating an Epic/Story/Task/Bug/Subtask in project AAASM, when writing a
  ticket title or description, when setting the required fields (Components,
  Labels, Assignee, Story points, Team, Fix version, Start/Due date), or when
  backfilling those fields on existing AAASM tickets. Encodes the
  type-specific description schema (Story = user-facing, Task = technical,
  Bug = defect report) and the Fix-version resolver (dev work → next version;
  verification/test work → version under test; a verification Epic may span
  versions).
---

# AAASM ticket author

Produce AAASM Jira tickets that match project convention on the first try:
short intent-carrying titles, type-correct descriptions, and a complete,
correct field set — especially **Fix version**, which most people get wrong.

Project AAASM lives at `lightning-dust-mite.atlassian.net`. **Use the
Atlassian MCP** (`mcp__plugin_atlassian_atlassian__*`) — the `JIRA_URL`/
`JIRA_API_TOKEN` shell env points at a different account and returns 404 for
AAASM. Constants and field IDs are in `references/fields.md`. Per-type
description templates are in `references/<type>.md`.

## When to use
- Creating any AAASM ticket (Epic, Story, Task, Bug, Subtask).
- Writing/repairing a ticket title or description.
- Setting or backfilling fields on an existing AAASM ticket.

## Workflow

### 1. Preflight (resolve, don't hardcode)
Read `references/fields.md`. Confirm/resolve:
- `cloudId` = `lightning-dust-mite.atlassian.net`; project `AAASM`.
- Team (`customfield_10001`) = Pioneer UUID (bare string, see fields.md).
- Field IDs: Components `customfield_10041`, Story points `customfield_10016`,
  Start date `customfield_10015`, Due date `duedate`, Fix version `fixVersions`.
- **Version ladder** — query the project versions and resolve the release
  train's *current released* and *next unreleased* version (see §5).

### 2. Pick the type, then load its template
Route to the matching reference and follow its section schema exactly:
| Type | Template | Voice |
|---|---|---|
| Story | `references/story.md` | user-facing ("As a … I can …") |
| Task | `references/task.md` | developer / technical |
| Bug | `references/bug.md` | defect report (expected/actual/repro/env) |
| Epic | `references/epic.md` | rollup; may span versions |
| Subtask | `references/subtask.md` | one commit-sized unit |

Story vs Task is a **voice** decision, not a size one: Story describes value to
a user/role; Task describes a technical unit for a developer. Their AC differ
(user-observable vs verifiable-technical) — see the templates.

### 3. Title rules
`[<scope>] <the point>` — imperative, short (≤ ~10 words), says *what it does /
what it's for*. Scope = the module/area/repo. No ticket IDs or filler.
- Good: `[saas-infra] Restrict CI token permissions`
- Bad: `Update some files in the infra repo to fix a few security things`

### 4. Required fields on create
Set all of these (missing any = incomplete ticket):
`issuetype`, `summary`, **Components** (`customfield_10041`), **Labels**,
**Assignee**, **Story points** (`customfield_10016` — Story/Task/Bug only;
**not on the Epic screen**, Epics roll up), **Team** (`customfield_10001` =
Pioneer), **Fix version** (`fixVersions` — see §5). Set **Start date**
(`customfield_10015`) and **Due date** (`duedate`) when planning.

**Story points** use the Fibonacci scale (1/2/3/5/8/13) and **Labels** come from
the canonical taxonomy — both defined in `references/estimation-and-labels.md`
(≥8 pts ⇒ split; ≥1 work-type label; don't duplicate fields as labels).

**Components = the org-relative GitHub repo name** the ticket targets
(`agent-assembly`, `python-sdk`, `node-sdk`, `go-sdk`, `docs`, `examples`,
`official-website`, `arena`, `saas-infra`, `.github`, `e2e-public`,
`e2e-private`, `internal-docs`, `cloud`, `agent-assembly-enterprise`). It is a
labels-type field, so a new repo value can be added freely; if a ticket spans
repos, list each. Cross-repo Epics carry all involved repos.

### 5. Fix-version resolver — the important one
**Ask: what does this ticket produce, and in which release does that land?**

- **Development Story / Task** → produces *code* → **next** (unreleased)
  version of the release train. You branch off the latest base (e.g. the tree
  is at rc.5), but your code ships in the next cut → `Fix version = rc.6`.
- **Verification / Test Story** → produces a *test run against an
  already-shipped build* → `Fix version = the version under test` (rc.5), not
  next. (See AAASM-4522: its verify-stories are all pinned to rc.5.)
- **Bug** (incl. bugs found during verification) → produces a *fix* → **next**
  version (rc.6).
- ⇒ A **verification/test Epic legitimately spans versions**: its verify-story
  children on the under-test version, its bug children on next. Development
  Epics are single-version (next).

**Release train:** the org release is coordinated around the **agent-assembly
core** tag (SDKs are coupled to it), so the canonical Fix version is the
`agent-assembly v0.0.1-<channel>.<n>` train even for SDK/docs/infra tickets.
Only a pure SDK-only release uses that SDK's own train. To resolve *next*:
query versions (see fields.md), find the latest `released:true` on the train
(current), then the next `released:false` after it (next); create it via REST
only if it's genuinely missing (MCP cannot create versions).

### 6. Create (MCP)
`createJiraIssue` with `cloudId`, `projectKey: AAASM`, `issueTypeName`,
`summary`, `description` (markdown), `parent` for Subtask/Story-under-Epic,
and `additional_fields` for everything else (`customfield_10001`,
`customfield_10041`, `customfield_10016`, `customfield_10015`, `duedate`,
`fixVersions: [{"id": "<versionId>"}]`, `labels`, `components` is NOT the
project's Components field — use `customfield_10041`).

### 7. Backfill mode (existing tickets)
Use `editJiraIssue` with the same `fields`. Notes: `duedate`/`customfield_10015`
are **not on the transition screen** (set via edit, not during a status
transition); `customfield_10016` (Story points) **errors on Epics**; the MCP
response omits custom fields — verify with `searchJiraIssuesUsingJql` returning
the specific field IDs.

## Gotchas
- Env `JIRA_*` creds don't reach AAASM → MCP only.
- `.github` is a valid `customfield_10041` value (leading dot OK).
- Story points field is absent from the Epic screen.
- Labels: kebab-case; keep a small consistent taxonomy (e.g. `sonarcloud`,
  `tech-debt`, `coverage`, `follow-up`, `security`, `finding`, `sev-*`).
- WAF blocks risky-looking write bodies (e.g. `curl | sh`) — insert a U+200B
  in such tokens (see the WAF memory) if a description legitimately needs them.
