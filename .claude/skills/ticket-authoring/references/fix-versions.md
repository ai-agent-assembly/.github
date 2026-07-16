# Fix Version lifecycle (runbook)

Managing the AAASM release **versions** the Fix Version field points at. The
`SKILL.md` Fix-version resolver decides *which* version a ticket gets; this
covers *managing the versions themselves* — list, resolve next, create, release.

**Tooling reality (verified 2026-07-16):** the Atlassian MCP has **no Jira
version tool**. Reads can go through `getJiraIssueTypeMetaWithFields`
(`fixVersions.allowedValues`) or REST GET; **create/release/delete are REST
only** (`/rest/api/3/version…`) and need a token that can reach AAASM.
The shell `JIRA_*` env creds **404 on AAASM** — so version writes are run by
whoever holds an AAASM-scoped token (or the release workflow), not from this
environment. Don't invent a version create path that doesn't exist; if the next
version is missing and you can't create it, **flag it and ask the release owner**.

## The version train
Canonical Fix Version = the **agent-assembly core** train
(`agent-assembly v0.0.1-<channel>.<n>`), even for SDK/docs/infra tickets (the
release is coordinated on the core tag). Per-SDK trains
(`python-sdk …`, `node-sdk …`, `go-sdk …`) exist but are used only for a pure
SDK-only release. Project id = `10006`.

## List / resolve current + next
```
# via REST (paginated), or getJiraIssueTypeMetaWithFields fixVersions.allowedValues
GET  /rest/api/3/project/AAASM/versions
```
Sort the train; latest `released:true` = **current**, next `released:false` =
**next**. (2026-07-16: rc.5 id 10042 released = current; rc.6 id 10043 = next.)

## Create the next version (REST — needs a credentialed token)
Only when the next version genuinely doesn't exist yet.
```
POST /rest/api/3/version
Content-Type: application/json
{
  "name": "agent-assembly v0.0.1-rc.7",
  "projectId": 10006,
  "description": "agent-assembly release v0.0.1-rc.7",
  "released": false
}
```
Auth = Basic `email:api_token` for an account with *Administer Projects* /
manage-versions on AAASM. Verify with the list call; then use the returned `id`
in `fixVersions: [{"id": "<id>"}]`.

## Release a version on ship (REST)
When the release actually cuts:
```
PUT /rest/api/3/version/{id}
{ "released": true, "releaseDate": "YYYY-MM-DD" }
```
After this, the *next* unreleased version becomes the new target for
development tickets (per the Fix-version resolver).

## Archive / delete (rare — care)
```
PUT    /rest/api/3/version/{id}   { "archived": true }     # hide old versions
DELETE /rest/api/3/version/{id}?moveFixIssuesTo=<otherId>  # reassign, don't orphan
```
Deleting a version that tickets reference orphans their Fix Version — always
pass `moveFixIssuesTo`. Prefer **archive** over delete for shipped versions.

## Do not
- Do not set a ticket's Fix Version to a version that doesn't exist — create it
  first (or ask the release owner), don't leave the field blank.
- Do not `DELETE` a version without `moveFixIssuesTo`.
- Do not claim a version was created from this environment if you only had the
  MCP / the 404-ing env creds — say it needs the release owner's token.
