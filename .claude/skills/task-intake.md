# Skill: task-intake

**When to use:** you have a JIRA ticket (project `AAASM`) and need to go from
"assigned" to "actually writing code."

> To **create** a ticket (fields, title, type-correct description, Fix version),
> use the `ticket-authoring` skill instead — this skill is for a ticket that
> already exists.

## Steps

1. **Read the ticket and its Epic.** Don't work from the ticket summary alone
   — read the full description and acceptance criteria, then open the parent
   Epic for the broader goal the ticket serves. If the ticket is a Subtask,
   also read the parent Story.
2. **Confirm the repo.** Check the Component field
   (`customfield_10041`) — see the `choose-repo` skill if it's unset or looks
   wrong.
3. **Check for blocking dependencies.** Look for:
   - JIRA issue links (`blocks` / `is blocked by`).
   - Prior tickets in the same Epic that this one is stacked on (common in
     this org — see the branch-naming note below).
   - An open PR from a dependency ticket that hasn't merged yet. If your
     ticket depends on unmerged work, branch off that PR's branch, not off
     the default branch (stacked branches) — note this explicitly in your PR
     description ("Depends on #NN").
4. **Transition the ticket to In Progress** and **comment that you're
   starting work**, including which branch/worktree you're using. This is
   the signal to other contributors (and other agents working the same
   Epic) that the ticket is claimed.
5. **Determine the branch name**: `<release-or-phase>/<ticket>/<type>/<short_summary>`
   (see `CLAUDE.md` / `AGENTS.md` for the full convention and type values).
   If stacking on a dependency branch, branch from that branch's tip, not
   from the default branch.
6. **Create the worktree** for the branch (see `setup-dev-env` and
   `contribution-guide` for the mechanics) and only then start implementing.

## Do not

- Do not start writing code before the ticket is transitioned to In Progress
  — this org relies on that state to avoid duplicate work across agents.
- Do not assume no dependency exists just because the ticket doesn't
  explicitly say so — check the Epic for sibling tickets that touch the same
  files or same directory, especially when multiple agents work an Epic
  concurrently.
- Do not rename the ticket or reinterpret its scope from your own reading of
  the description — if the described work seems off, comment and ask rather
  than silently redefining it.
