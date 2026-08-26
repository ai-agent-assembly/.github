# Agent escalation

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). Applies to any AI coding tool working across `ai-agent-assembly`
repos.

## When to stop and ask

An AI agent must stop and ask a human rather than guess when it is:

- **Uncertain** about requirements, scope, or which repo/ticket a change
  belongs to.
- **Blocked** — a precondition can't be verified locally (e.g. CI is
  billing-blocked with no way to confirm a fix), a dependency ticket/PR
  hasn't merged yet, or required credentials/access are missing.
- About to take a **hard-to-reverse action**, including but not limited to:
  - Force-pushing any branch.
  - Deleting a file, branch, or worktree.
  - Dropping or truncating a database table.
  - Pushing or merging directly to a base branch (`master`/`main`).
  - Rewriting git history that's already been pushed/shared.

Guessing on any of the above risks an outcome that can't be cleanly undone —
the cost of a short pause to ask is always lower than the cost of a wrong
irreversible action.

## How to phrase the escalation

State, in order:

1. **What's blocking** — the specific fact that's unclear or unverifiable
   (not "I'm stuck," but "ticket X depends on PR #Y which hasn't merged" or
   "the diff requires force-pushing branch Z").
2. **What was tried** — the investigation already done (files read, commands
   run, branches checked) so the human isn't asked to re-derive context that
   already exists.
3. **What decision is needed** — a concrete question with, where possible, the
   options already narrowed (e.g. "proceed with a stacked PR on the unmerged
   branch, or wait for it to merge first?").

Keep the escalation short and specific — it should be answerable in one
reply, not a request for the human to re-read the whole task.

## Owner-only admin-merge exception (AAASM-5858)

Amends the "pushing or merging directly to a base branch" line above and
`02-git-workflow.md`'s Merges section. The default there — required
independent approval, no self-merge, always escalate on
`REVIEW_REQUIRED` — is unchanged for every identity except the one
carved out below.

**This is still advisory guidance**, per `01-security.md`'s
enforcement-vs-guidance split: it does not touch branch-protection
settings or any `.claude/settings.json` allow/deny list, both of which
remain AAASM-3926's deterministic-enforcement scope. Writing this
exception here authorizes an AI agent to *invoke* GitHub's own
`--admin` override in the narrow case below; it does not, and cannot,
change what GitHub's platform-level branch protection actually
enforces.

### Who this applies to

Only a verified GitHub **repository owner**, or a verified **Owner**
of the GitHub organization that owns the repository. Nobody else —
not a maintainer, not a collaborator with admin/maintain permissions,
not a bot or automation account, not the agent itself absent that
verification.

**Do not infer owner authority from the ability to technically invoke
an admin-capable API or CLI command.** `repos/<org>/<repo>` reporting
`permissions.admin: true` is *not* sufficient — that also covers
ordinary maintain-level collaborators. The discriminating check is org
membership role:

```
gh api user --jq .login
gh api orgs/<org>/memberships/<login> --jq .role   # must be "admin" (org Owner)
```

A repo that is not org-owned (a personal account's own repo) uses that
account's own repo-owner identity instead — verify against
`repos/<owner>/<repo>` where `<owner>` is the authenticated login, not
against org membership.

Verify this before using the exception on every occasion, not once per
session — do not cache or assume a prior verification still holds.

### Conditions — ALL must hold, in addition to owner verification

1. Substantive review of the **current final PR head** is complete
   (diff, ACs/design, correctness, regression risk, security boundary
   and fail-open behavior, truthful evidence/claims).
2. A durable LGTM / self-review record has been posted (PR comment or
   equivalent) — not held only in conversation.
3. All required CI/tests/security gates are green; SKIPPED checks are
   individually understood as legitimately-not-applicable, not assumed.
4. No unresolved correctness or security defect.
5. No `REQUEST_CHANGES` review and no unresolved blocking review
   finding.
6. The PR head has not materially changed since the review in (1) — a
   new commit after review invalidates it; re-review before using the
   exception.
7. No merge conflicts.
8. Any required evidence/artifacts (e.g. AC-mapped test evidence) are
   present.
9. The **only** remaining blocker is GitHub's required-approval /
   `REVIEW_REQUIRED` state, caused specifically by the PR author and
   the only available approver being the same identity.

None of the above is waivable by owner status — owner status resolves
only the same-identity approval mechanic in condition 9. A real
failure anywhere in 1–8 is still a stop-and-fix/escalate, exactly as
for any other identity.

### What to do when every condition holds

- Use GitHub admin merge.
- Use **"Create a merge commit"** — not squash, not rebase, unless
  that specific repository's own rules require a different method.
- Record in the PR (comment) and in the linked Jira ticket that the
  merge was performed under this owner-only admin-merge exception,
  naming the verified identity and which condition (9) was the actual
  blocker — this is the audit trail per `06-audit-trail.md`.

### What to do otherwise

If the authenticated identity does not verify as owner, or any
condition 1–8 fails: this exception does not apply. Fall back to the
default — wait for independent approval, continue other non-blocked
work, escalate to a human only when the block is genuinely
undecidable without one. Never substitute a branch-protection change,
a local merge + push, a direct push to the base branch, or any other
workaround for the missing approval.
