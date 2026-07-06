# Skill: pr-reviewer

**When to use:** you've been asked to *review* a PR — yours or someone
else's, already open — not to write one. This is the reviewer's side of the
exchange; `pr-review` is the author's self-check before requesting review.
Don't conflate the two: this skill assumes the PR already exists and may
have CI results, and its output is a review comment, not a code change
(unless the requester separately asks you to also fix what you find).

## 1. CI status

Check every reported status, not just the overall summary:

- If everything is green, move on.
- If something is red, confirm *why* before deciding it's real. The org's
  known GitHub Actions billing-block completes a check-suite in a few
  seconds with **zero jobs** (`gh api repos/<org>/<repo>/commits/<sha>/check-suites`
  or the job annotations will show this) — treat that as infra, not a code
  failure, per `CLAUDE.md`'s CI-reality note. A downstream check (SonarQube,
  Codecov) stuck `queued` or failing only because it never got artifacts
  from a billing-blocked Actions run falls under the same exception.
- Anything else red — a test, lint, type-check, or build job that actually
  ran and failed — is a real failure. Fix it (if asked to) or block the
  review on it (if only asked to review).
- Coverage/SonarQube-style acceptance gates that fail on their own merits
  (not as a billing-block symptom) can be called out but don't have to block
  approval — flag them as a judgment call for whoever merges, per whatever
  the requester told you about acceptable-to-ignore categories.

## 2. Scope vs. ticket

Read the actual ticket (description, acceptance criteria, and comment
history — not just the title) and the PR description, then check the real
diff against both:

- Does the PR cover every acceptance criterion? List them and mark each one
  met/not-met with evidence (a file, a line, a test) — don't just assert
  "looks complete."
- Does the PR do *only* what the ticket describes, or is something unrelated
  bundled in (a drive-by refactor, an unrelated fix, a formatting pass on
  untouched files)?
- If the PR's own description claims something ("tested X", "verified Y"),
  don't take it at face value — re-derive or spot-check it yourself where
  practical (e.g. re-run the diff, re-check the file the description
  references). Trust but verify.

## 3. Side effects and correctness

Read the diff itself, not a summary of it:

- Does any change touch code, config, or docs outside what the ticket
  describes? Check other files/repos that shouldn't have been touched
  (`git status --porcelain` in adjacent repos if the change could plausibly
  have spread there).
- For any existing (not brand-new) function, file, or behavior being
  modified: does the change preserve everything it isn't supposed to change?
  A diff that's "purely additive" should be verified as such (e.g. `git diff
  <pre-change-ref> <post-change-ref> -- <file>` showing only insertions), not
  assumed from the PR description.
- For scripts or code with real runtime behavior, don't just read it — run
  it (dry-run, a scratch/temp target, existing test suite) if that's
  feasible without side effects on shared state.

## 4. Security

Check against `.claude/rules/01-security.md` directly, not just skim for
"anything security-related in the title":

- No secrets, credentials, tokens, or `.env` contents in the diff.
- No dangerous patterns introduced: `curl | bash`, `eval` on untrusted
  input, `--no-verify`, force-push to a shared branch, unvalidated
  input reaching a shell command or SQL query, newly-added write access to
  something that didn't have it before.
- For a script or tool that writes to the filesystem or network: confirm it
  fails safe (doesn't silently overwrite/clobber, doesn't proceed past a
  failed precondition) rather than trusting a comment that says it does.

## 5. Frontend validation

If the PR touches any FE code (component, page, styling, client-side logic):

- Check the design spec (e.g. `design/vN/` in the target repo) if one
  exists, and confirm the implementation matches it.
- Use the Playwright MCP tooling to actually load the affected page(s) and
  exercise the changed behavior — don't approve FE changes on code reading
  alone.
- Capture a screenshot (or short recording) of the validated state. If the
  repo has a design/validation-report folder, save it there; otherwise note
  in the review comment where the evidence lives.
- If the PR touches no FE surface, say so explicitly in the review comment
  rather than silently omitting the section — it should read as "N/A,
  confirmed" not "skipped."

## 6. Leave the record

Post a PR comment (not a silent verdict) covering all five checks above,
even when everything passed — "checked, found nothing" is still a useful
record. Structure: CI status → scope-vs-ticket → side effects/correctness →
security → frontend (or N/A) → a clear recommendation (ready to merge /
mergeable with a named caveat / blocked on X). Do not approve or merge the
PR yourself unless the requester has explicitly given you that authority —
default to reporting findings and letting the ticket owner decide, per this
org's auto-merge policy.

## Do not

- Do not treat every red CI check as the billing-block without confirming
  it via check-suite/job-annotation evidence first.
- Do not accept a PR description's claims ("tested", "verified", "no side
  effects") without independently checking at least a sample of them.
- Do not skip the security check because the PR "doesn't look like security
  work" — the highest-risk changes are often the ones not framed that way.
- Do not skip Playwright validation for FE changes because the change looks
  small — small FE diffs break rendering just as often as large ones.
- Do not merge or approve on your own authority unless explicitly told to.
