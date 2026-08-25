# Context boundary

Advisory guidance (see `01-security.md` for the enforcement-vs-guidance
distinction). Applies to any AI coding tool working across `ai-agent-assembly`
repos.

## Secrets and credentials are out of context boundary

- Don't read `.env` files, credential files, API tokens, or private keys into
  a prompt "just to check" — if their contents matter, describe the
  situation without pasting the value.
- Don't paste secrets/credentials into commit messages, PR descriptions,
  code comments, or Jira comments, even temporarily "to be removed later."
- If a task genuinely requires inspecting a secret's value (e.g. debugging an
  auth failure), do it through a mechanism that doesn't echo the value into
  the conversation transcript or any artifact that gets committed.
- Never run a broad environment enumeration (`env`, `printenv`, `env | grep
  <pattern>`, etc.) as a diagnostic step near a secret-bearing process —
  a pattern that matches the *name* still prints the *value* into tool
  output, which lands in the conversation transcript regardless of intent.
  When the question is "is this configured?", answer it with a check whose
  output cannot contain the value itself:
  - presence only: `[ -n "$VAR" ]` / `test -n "$VAR"`
  - boolean configured/not-configured, not the content
  - variable *names* only (`env | cut -d= -f1`), never `name=value` pairs
  - host/target mappings without the credential half (e.g. print which
    hosts a `host=key` map covers, never the `key`)
  - file mode/ownership (`stat`, `ls -l`) instead of reading a credential
    file's contents
  - a cryptographic digest of the value, only where that's actually useful
    and the digest itself isn't sensitive
  This applies to Dogfooding/QA diagnostics as much as to any other secret-
  handling step — a session running near a real disposable or production
  credential must not enumerate environment values "just to check config
  state."

## Cross-repo boundaries

This is a **multi-repo org** — several repos are private
(`cloud`, `agent-assembly-enterprise`) and several are public
(`agent-assembly`, the SDKs, `.github`, docs sites). When working across
repos in the same session:

- Don't copy or paraphrase a private repo's code, comments, internal
  discussion, or file contents into a public repo's commit, PR description,
  code comment, or issue.
- Don't reference private-repo ticket details, architecture notes, or
  business context in a public-repo artifact beyond what's already public
  (e.g. the public Jira ticket number and title are fine; a private repo's
  internal implementation notes are not).
- If a change genuinely needs to reference cross-repo context, link the
  public ticket rather than inlining private content.

## General principle

Treat anything that isn't already meant to be public (secrets, private-repo
internals, unpublished business context) as outside the boundary of what
belongs in a prompt, a commit, a PR, or any other artifact an AI agent
produces — when unsure whether something crosses this line, leave it out and
ask (see `04-agent-escalation.md`).
