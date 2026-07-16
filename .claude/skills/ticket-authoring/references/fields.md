# AAASM field reference

Constants and IDs for authoring/editing AAASM tickets via the Atlassian MCP.
Verify anything version-related at run time — the ladder moves.

## Constants
- Site / `cloudId`: `lightning-dust-mite.atlassian.net` (UUID `f15c3ffb-740e-4db1-9b6b-12ccba3e897a`)
- Project key: `AAASM` (id `10006`), board id 7
- Team (`customfield_10001`) = **Pioneer**, bare UUID string:
  `7adda3ef-9e8e-4207-9b9a-c5f4ff942bea`
  (object form and the display name "Pioneer" are both rejected — must be the bare UUID string)

## Field IDs
| Field | Key | Type / notes |
|---|---|---|
| Components | `customfield_10041` | labels-type (array of strings); value = org-relative repo name |
| Story points | `customfield_10016` | number; **Story/Task/Bug only — errors on Epic** |
| Start date | `customfield_10015` | date `YYYY-MM-DD`; not on transition screen |
| Due date | `duedate` | system date `YYYY-MM-DD`; not on transition screen |
| Fix version | `fixVersions` | array of `{"id": "<id>"}` |
| Labels | `labels` | array of kebab strings |
| Team | `customfield_10001` | bare UUID string (see above) |
| Sprint | `customfield_10020` | scalar number |

## Issue type IDs
Task `10032` · Bug `10033` · Story `10034` · Epic `10035` · Subtask `10036`.
Transitions (global): To Do `11`, In Progress `21`, Done `31`
(also "DEV VERIFY" `2`, "IN QA" `3`). Confirm with `getTransitionsForJiraIssue`.

## Components vocabulary (org-relative GitHub repo)
`agent-assembly`, `python-sdk`, `node-sdk`, `go-sdk`, `cloud`,
`agent-assembly-enterprise`, `docs`, `examples`, `official-website`, `arena`,
`saas-infra`, `.github`, `e2e-public`, `e2e-private`, `internal-docs`.
(1:1 with the GitHub repo the ticket targets. New repo → add the value.)

## Resolving the version ladder (Fix version)
The canonical train is **agent-assembly core** (SDKs coupled). To list:
```
getJiraIssueTypeMetaWithFields(cloudId, AAASM, issueTypeId=10034, requiredFieldsOnly=false)
  → fields[].fixVersions.allowedValues   # names like "agent-assembly v0.0.1-rc.6", with released:true/false
```
or via `searchJiraIssuesUsingJql` reading `fixVersions`, or REST
`/rest/api/3/project/AAASM/versions`. Pick the train, find latest
`released:true` = **current**, next `released:false` = **next**.

Known as of 2026-07-16: `agent-assembly v0.0.1-rc.5` (id `10042`, **released**),
`agent-assembly v0.0.1-rc.6` (id `10043`, unreleased = **next**). Per-SDK trains
exist (`python-sdk …`, `node-sdk …`, `go-sdk …`) but coordinated work uses the
core train.

**MCP cannot create versions.** If the next version is genuinely missing, create
it via REST `POST /rest/api/3/version` (needs a token that can reach AAASM —
the shell `JIRA_*` env does **not**; use a credentialed call or ask the operator).

## Access gotcha
Shell `JIRA_URL`/`JIRA_USERNAME`/`JIRA_API_TOKEN` resolve to a different
account (404 on AAASM). All AAASM reads/writes go through the Atlassian MCP.
The MCP edit/create response does **not** echo custom fields — verify with
`searchJiraIssuesUsingJql` requesting the explicit field IDs.
