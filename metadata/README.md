# `metadata/` — canonical org-shared metadata registry

`org-profile.yaml` is the **single canonical registry** for the org's shared,
non-version metadata — the facts that used to be hand-copied across repos and
drifted silently on every rename or URL change. The design decision this
implements is [ADR 0014](https://github.com/ai-agent-assembly/agent-assembly/blob/main/docs/src/adr/0014-canonical-metadata-registry-and-drift-gate.md)
(canonical metadata registry & drift gate); read it for the rationale and the
public/private boundary rules. Version metadata is out of scope here — it is
owned by ADR 0013.

## What the registry owns

`org-profile.yaml` holds these sections, each value with **exactly one owner**
(no consumer may re-declare a value the registry owns):

| Section | Holds | Owner note |
|---|---|---|
| `org` | the org slug (`ai-agent-assembly`) | slug's single owner — `product` does **not** repeat it |
| `product` | product / org display names, published (legacy) security email | `product.security_email` is the historical `.dev` alias; canonical `.com` now lives under `contacts.security.primary` |
| `schema_version` | version of the contact/mail/security blocks below | consumers fail clearly on an incompatible bump; validated present + integer ≥ 1 |
| `contacts` | canonical public contact addresses per audience (security/support/maintainers/privacy/billing) — `primary` (`.com`) + optional `legacy_aliases` (`.dev`) | a `primary` must be `.com`; `.dev` only under `legacy_aliases` |
| `mail_domains` | `human` / `legacy_human` / `transactional` mail-domain names | the human mailbox domain vs. the isolated transactional subdomain |
| `transactional_from` | machine-sent sender identities (`default`/`verification`/`notifications`) on the transactional domain | distinct from human contact addresses |
| `mail_platform` | intended provider + activation state (`*_status` ∈ {planned, in_progress, active}) | **NOTHING is live**; this publishes intent, not tenant state |
| `security_policy` | structured security-response SLAs (`acknowledgement`, `initial_assessment`) as `value`/`unit` | structured, not English prose; units ∈ {business_days, calendar_days, hours} |
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

## Contact, mail, and security-policy schema (AAASM-5519)

The registry publishes the org's **public contact and mail identity facts** so
they have one structured owner instead of being hand-copied into `SECURITY.md`,
`SUPPORT.md`, websites, and package manifests. It carries **public identity
facts only** — never live tenant state, never private operational data, never a
secret. The blocks are versioned by the top-level `schema_version`.

The schema keeps these layers deliberately distinct so a consumer can never
conflate them:

| Concept | Where | Example |
|---|---|---|
| Canonical public contact identity | `contacts.<audience>.primary` | `security@agent-assembly.com` |
| Legacy compatibility identity | `contacts.<audience>.legacy_aliases[]` | `security@agent-assembly.dev` |
| Human mailbox domain | `mail_domains.human` (+ `legacy_human`) | `agent-assembly.com` |
| Contact-routing / transactional domain | `mail_domains.transactional` | `mail.agent-assembly.com` |
| Transactional sender identity | `transactional_from.*` | `no-reply@mail.agent-assembly.com` |
| Intended provider | `mail_platform.intended_provider` | `Google Workspace` |
| Activation state | `mail_platform.*_status` | `planned` |
| Security-response targets | `security_policy.*` (`value`/`unit`) | `2 business_days` |
| Public / private / secret visibility | see the source-of-truth table below | — |

A canonical `primary` is always `.com`; a `.dev` address is only ever a
`legacy_aliases` entry. Asking for `primary` therefore never returns a legacy
address. `mail_platform` publishes **intent only** — no mailbox, alias, MX,
SPF/DKIM/DMARC, or provider tenant is live; do not read `intended_provider` as
"active" or a status as "verified/sending".

### Source of truth per layer

Each fact class has exactly one owning system. This registry owns **only** the
published public-identity layer; it is not the authority for anything else:

| Layer | Owns | Not owned here |
|---|---|---|
| **Workspace Admin Console** | account objects — mailboxes, aliases, group membership, super-admin/recovery identities | never in the registry |
| **Terraform (DNS)** | MX / SPF / DKIM / DMARC / CNAME records and zones | never in the registry |
| **This public identity registry** (`org-profile.yaml`) | published identity facts: canonical/legacy contact addresses, mail-domain names, transactional From identities, structured security SLAs, intended provider + activation state | — |
| **Private runbook** | operational facts: escalation/on-call assignments, PagerDuty routing, provider account IDs, private reporting destinations, private repo topology | never in the registry |
| **Secret manager** | passwords, recovery codes, API/Cloudflare/SMTP credentials, OAuth client secrets, DKIM **private** material, service tokens, encryption keys | never in the registry |

### Validation and leakage guard

`scripts/generate_org_profile.py` **validates** the schema before producing any
artifact, and the drift gate runs the same generator in `--check` mode — so
malformed or leakage-prone input **fails CI** rather than being published. It
checks: email/domain format; `primary`-vs-`legacy` semantics (a `primary` must
be `.com`, `.dev` only under `legacy_aliases`); address uniqueness;
transactional-From addresses on the transactional domain; structured SLA
`value`/`unit` presence and vocabulary; and a **forbidden-private-pattern
guard** that rejects any key or value shaped like a recovery/admin/on-call
identity, phone number, account id, token, or DKIM private-key blob. On any
violation the generator exits non-zero with a descriptive message. Unit and
leakage tests live in `scripts/test_contact_schema.py`.

### Changing a shared contact value

1. Edit the relevant block in `org-profile.yaml` (e.g. `contacts.support.primary`).
   Keep a `primary` on `.com`; move any retired address into `legacy_aliases`.
2. Regenerate (`python3 scripts/generate_org_profile.py`) and commit the
   registry change **and** the regenerated `generated/registry.json` together.
3. Downstream consumers regenerate from the projection: the contact/SECURITY/
   SUPPORT/website/package rollout is **AAASM-5520**, and the staged Workspace
   MX cutover that actually activates these identities is **AAASM-5523** — both
   are separate Stories that consume this registry; neither is done here.

## Generated artifacts

`scripts/generate_org_profile.py` derives these artifacts from the registry:

- **`../profile/README.md`** — the org front door. The generator rewrites the
  bounded `<!-- BEGIN GENERATED: repo_table -->` and `install_channels` regions;
  everything outside those markers is hand-authored prose.
- **`../SECURITY.md`** — the `<!-- BEGIN GENERATED: security_contact -->` region
  carries the canonical `.com` reporting address, the structured
  acknowledgement / initial-assessment SLAs, and the labeled legacy-alias note
  (AAASM-5520). Supported-versions and disclosure prose stay hand-authored.
- **`../SUPPORT.md`** — the `<!-- BEGIN GENERATED: support_contacts -->` region
  carries the support + security `.com` contact addresses (AAASM-5520).
- **`generated/registry.json`** — a machine-readable, **visibility-filtered**
  projection of the shared facts (public repos only, identity fields only) that
  cross-repo consumers read instead of hand-copying a value. It is **generated —
  do not edit by hand**; change the registry and regenerate.

The generated contact blocks state **intent only**: no `.com` mailbox is live
yet (`mail_platform.*_status == planned`). The legacy `.dev` addresses continue
to receive via Cloudflare Email Routing during the transition, and the rendered
note says so — it never claims the `.com` identity is live-sending.

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
