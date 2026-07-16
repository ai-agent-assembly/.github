# Goals (runbook)

Two distinct things get called a "goal" in Jira. Use the right one.

## A. Epic-as-goal — the trackable objective (MCP-doable)

In AAASM the **Epic is the objective** that Stories/Tasks/Bugs serve
(Epic → Story → Subtask). This is fully manageable via the Atlassian MCP.

**Create the objective Epic** — `createJiraIssue` `issueTypeName: Epic`, written
to the `epic.md` template (Goal · Scope · Success criteria · child breakdown ·
version plan). Set Team = Pioneer; Components = all repos it spans; no
Story-points field on Epics (rolls up).

**Attach child work to the goal** — set the child's **parent** to the Epic key:
- on create: `createJiraIssue(..., parent: "<EPIC-KEY>")`
- after the fact: `editJiraIssue(fields: { parent: { key: "<EPIC-KEY>" } })`
This is the Epic→child hierarchy; the Epic's progress rolls up from its children.

**Cross-ticket dependencies** (not parent/child) — use **issue links**, not
`parent`:
- `getIssueLinkTypes` → find the type (`Blocks`, `Relates`, `Depends`, …)
- `createIssueLink` → link the two issues (e.g. "Story A **is blocked by** Story B").

**Verify the goal's scope** — JQL `parent = <EPIC-KEY>` lists its children; sum
child Story points for the Epic estimate; a `Verify …` subtask per Story checks AC.

## B. Jira Goals entity — OKR-style objectives (runbook, UI/Atlas only)

Atlassian **Goals** are standalone objective objects (the *Goals directory*, part
of Jira/Atlas/Home), separate from Epics; issues link to a Goal via a **Goals
field** where it's enabled.

**No CRUD via the Atlassian MCP or the standard Jira issue REST** (verified — the
MCP exposes issue/version/component-less-Compass tools only, no Goals). So:
- Create/edit a Goal → the **Goals directory UI** (or the Atlas / townsquare
  GraphQL API if you have access).
- Link an issue to a Goal → the issue's **Goals field in the UI**, not a
  `fields`-set call.
- If asked to create/link a Goal programmatically, **flag the limitation** and do
  it in the UI — don't fake it through a custom field.

## Which to use
- **Default to Epic-as-goal** for anything the team tracks and delivers — it's
  fully MCP-manageable and matches the AAASM hierarchy.
- Reserve **Jira Goals** for higher-level, cross-project OKR-style objectives
  owned in the UI; link Epics up to them there when the org uses that layer.

## Do not
- Do not use `parent` for a mere dependency — `parent` is hierarchy; use
  `createIssueLink` for blocks/relates.
- Do not claim a Jira Goal was created/linked programmatically — it's a UI/Atlas
  action from this tooling.
