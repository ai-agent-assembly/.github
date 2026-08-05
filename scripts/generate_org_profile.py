#!/usr/bin/env python3
"""Regenerate bounded blocks in profile/README.md from metadata/org-profile.yaml.

The org profile at profile/README.md is a public front door rendered by
GitHub at github.com/ai-agent-assembly. It carries per-SDK badge tables,
install snippets, and repo-URL references that drift silently every time a
repo is renamed or an SDK package id changes. This script rewrites the two
drift-prone bounded sections from a single source of truth so those refs stay
in lockstep with metadata/org-profile.yaml.

It also emits metadata/generated/registry.json — a machine-readable,
visibility-filtered projection of the widened registry (ADR 0014) that
cross-repo consumers read instead of hand-copying a URL, repo name, or Jira id.
Both artifacts are regenerated from the one registry and drift-gated together.

Bounded sections are delimited by HTML comments (invisible in rendered
Markdown):

    <!-- BEGIN GENERATED: <id> -->
    ...generated content...
    <!-- END GENERATED: <id> -->

The generator is idempotent — running it against an unchanged SoT produces
no diff. CI (.github/workflows/org-profile-drift.yml) enforces that.

Only stdlib is used so this runs in any Python 3.9+ environment without
needing to install PyYAML on top of the CI runner.

Usage:
    python3 scripts/generate_org_profile.py
    python3 scripts/generate_org_profile.py --check    # exit non-zero on drift
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_PATH = REPO_ROOT / "metadata" / "org-profile.yaml"
README_PATH = REPO_ROOT / "profile" / "README.md"

# In-repo governance-doc consumers of the widened contact/security schema
# (AAASM-5520). Each carries bounded <!-- BEGIN/END GENERATED: <id> --> regions
# whose content is rendered from the registry; the surrounding prose stays
# hand-authored. These are drift-gated by the same --check run as the README.
SECURITY_PATH = REPO_ROOT / "SECURITY.md"
SUPPORT_PATH = REPO_ROOT / "SUPPORT.md"
CODE_OF_CONDUCT_PATH = REPO_ROOT / "CODE_OF_CONDUCT.md"

# Machine-readable projection of the registry (ADR 0014) for cross-repo
# consumers and the future hardcoded-value lint. Visibility-filtered: only
# public repos and only the shared facts (no badge/version markdown).
GENERATED_DIR = REPO_ROOT / "metadata" / "generated"
REGISTRY_JSON_PATH = GENERATED_DIR / "registry.json"

# Sentinel format. HTML comments render invisibly on GitHub.
BEGIN_RE = re.compile(r"<!--\s*BEGIN GENERATED:\s*([A-Za-z0-9_.-]+)\s*-->")
END_RE = re.compile(r"<!--\s*END GENERATED:\s*([A-Za-z0-9_.-]+)\s*-->")


# ---------------------------------------------------------------------------
# Minimal YAML subset parser
# ---------------------------------------------------------------------------
# We deliberately avoid a PyYAML dependency. The SoT uses a small subset:
#   - top-level scalar keys
#   - mapping-of-scalars nested under a top-level key
#   - list of mappings under a top-level key
#   - list-of-scalars under a nested key
#   - block scalars introduced by "|" (literal, keep newlines)
#   - "# ..." comments outside of quoted scalars
#   - double-quoted scalars containing ": " (colon-space)
#   - empty inline list "[]"
#
# If the SoT grows beyond this subset the parser will raise clearly.


class YamlError(RuntimeError):
    pass


def _strip_comment(s: str) -> str:
    """Remove trailing '# ...' comment, honoring double-quoted strings."""
    in_quote = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == '"' and (i == 0 or s[i - 1] != "\\"):
            in_quote = not in_quote
        elif c == "#" and not in_quote:
            return s[:i].rstrip()
        i += 1
    return s.rstrip()


def _unquote(v: str) -> Any:
    v = v.strip()
    if not v:
        return ""
    if v.startswith('"') and v.endswith('"') and len(v) >= 2:
        # JSON-ish unescape: \" \\ \n. Applied character-by-character so
        # non-ASCII UTF-8 (em-dash, smart quotes, etc.) passes through
        # untouched — a naive `.decode("unicode_escape")` mis-reads the
        # bytes of a multi-byte UTF-8 code point as latin-1 and corrupts it.
        inner = v[1:-1]
        if "\\" not in inner:
            return inner
        out: list[str] = []
        i = 0
        while i < len(inner):
            c = inner[i]
            if c == "\\" and i + 1 < len(inner):
                nxt = inner[i + 1]
                out.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}.get(nxt, nxt))
                i += 2
                continue
            out.append(c)
            i += 1
        return "".join(out)
    if v == "null":
        return None
    if v == "true":
        return True
    if v == "false":
        return False
    if v == "[]":
        return []
    return v


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _peek_container_kind(raw_lines: list[str], i: int, indent: int) -> Any:
    """Decide the empty container a bare ``key:`` introduces: ``[]`` or ``{}``.

    Peeks at the next non-blank, non-comment line — a more-indented ``- `` line
    means a list; anything else more-indented means a mapping; nothing deeper
    means an empty mapping by convention.
    """
    j = i + 1
    while j < len(raw_lines):
        nxt = raw_lines[j]
        if not nxt.strip() or nxt.lstrip().startswith("#"):
            j += 1
            continue
        nxt_indent = _indent_of(nxt)
        if nxt_indent <= indent:
            return {}
        return [] if nxt.lstrip().startswith("- ") else {}
    return {}


def _collect_block_scalar(
    raw_lines: list[str], i: int, indent: int
) -> tuple[str, int]:
    """Collect a ``|`` literal block scalar. Returns ``(value, next_index)``.

    Lines more-indented than the key are kept verbatim (dedented to the first
    body line's indent); trailing blank lines are clipped, matching YAML's
    default block-scalar clip behavior.
    """
    block_indent: Optional[int] = None
    body_lines: list[str] = []
    j = i + 1
    while j < len(raw_lines):
        blk = raw_lines[j]
        if not blk.strip():
            body_lines.append("")
            j += 1
            continue
        bi = _indent_of(blk)
        if bi <= indent:
            break
        if block_indent is None:
            block_indent = bi
        body_lines.append(blk[block_indent:])
        j += 1
    # Trim trailing blank lines (default clip behavior).
    while body_lines and body_lines[-1] == "":
        body_lines.pop()
    return "\n".join(body_lines) + "\n", j


def _handle_list_item(
    raw_lines: list[str],
    i: int,
    indent: int,
    content: str,
    parent: Any,
    stack: list[tuple[int, Any]],
) -> int:
    """Process a ``- ...`` list item; returns the next line index to read.

    An inline mapping (``- key: value``) opens a new dict on ``parent`` and
    re-feeds the key/value as a virtual line at the same index (returns ``i``
    unchanged so it is re-processed); a scalar item is appended directly.
    """
    if not isinstance(parent, list):
        raise YamlError(f"line {i+1}: list item under non-list container")
    item_body = content[2:].strip()
    if ":" in item_body and not item_body.startswith('"'):
        new_map: dict = {}
        parent.append(new_map)
        stack.append((indent, new_map))
        raw_lines[i] = " " * (indent + 2) + item_body
        return i
    parent.append(_unquote(item_body))
    return i + 1


def _handle_mapping(
    raw_lines: list[str],
    i: int,
    indent: int,
    content: str,
    parent: Any,
    stack: list[tuple[int, Any]],
) -> int:
    """Process a ``key: value`` / ``key:`` line; returns the next line index."""
    if ":" not in content:
        raise YamlError(f"line {i+1}: unrecognized syntax: {content!r}")
    key, _, rest = content.partition(":")
    key = key.strip()
    rest = rest.strip()

    if isinstance(parent, list):
        raise YamlError(
            f"line {i+1}: mapping key inside a list without leading '-'"
        )

    if rest == "":
        container = _peek_container_kind(raw_lines, i, indent)
        parent[key] = container
        stack.append((indent, container))
        return i + 1

    if rest.startswith("|"):
        parent[key], next_i = _collect_block_scalar(raw_lines, i, indent)
        return next_i

    parent[key] = _unquote(rest)
    return i + 1


def parse_yaml(text: str) -> dict:
    """Parse the org-profile.yaml subset described above."""
    # Tokenize into (indent, kind, raw) with comments/blank lines skipped,
    # BUT preserve blank lines and comment lines while inside a block scalar
    # ("|") -- those blank/comment lines are literal content and must be kept.
    raw_lines = text.splitlines()

    root: dict = {}
    # A stack of (indent, container) where container is dict or list.
    stack: list[tuple[int, Any]] = [(-1, root)]

    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i]
        stripped_full = raw.rstrip()
        # Skip pure comment / blank lines at the structural level.
        if not stripped_full.strip() or stripped_full.lstrip().startswith("#"):
            i += 1
            continue

        line = _strip_comment(stripped_full)
        indent = _indent_of(line)
        content = line.strip()

        # Pop stack until parent indent < current indent.
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            raise YamlError(f"line {i+1}: no parent container")

        parent = stack[-1][1]

        if content.startswith("- "):
            i = _handle_list_item(raw_lines, i, indent, content, parent, stack)
        else:
            i = _handle_mapping(raw_lines, i, indent, content, parent, stack)

    return root


# ---------------------------------------------------------------------------
# Block rendering
# ---------------------------------------------------------------------------


def render_repo_table(repos: list[dict]) -> str:
    """Render the full Repository Status table (header + separator + body).

    The header row and separator row are emitted inside the bounded block
    alongside the data rows so the entire GFM table is one contiguous block
    of Markdown. GitHub's GFM parser treats a bare HTML comment between the
    separator and the first data row as a block-level break — putting the
    `<!-- BEGIN GENERATED: ... -->` sentinel there orphans the body and
    causes it to render as a `<p>` under an empty `<thead>`-only table
    (see AAASM-4410). Keeping header + separator + body in one block, with
    the sentinels wrapping the whole table, is the only shape that survives
    GFM parsing.

    Visibility-filtered like render_registry_json (ADR 0014): profile/README.md
    is a public artifact, so a private repo's slug/metadata MUST NOT leak into
    it. The same public-only predicate is applied here — a repo whose
    ``visibility`` is missing or not exactly ``public`` is excluded, so adding a
    private repo to the SoT without a correct ``visibility: private`` marker
    fails closed (dropped) rather than fails open (published).
    """
    lines: list[str] = [
        "| Repo | Purpose | Version | Base branch health | Activity |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in repos:
        if r.get("visibility") != "public":
            continue
        lines.append(_render_repo_row(r))
    return "\n".join(lines)


def _render_repo_name_badge(r: dict) -> str:
    """The shields.io name badge cell linking to the repo."""
    slug = str(r["slug"])
    repo_full = str(r["repo"])
    badge = r.get("badge", {}) or {}
    label_color = str(badge.get("label_color", "000000"))
    logo = str(badge.get("logo", "github"))
    logo_color = badge.get("logo_color")
    tag_prefix = str(badge.get("tag_prefix", ""))

    # shields.io renders "--" as a single dash in badge label paths, so
    # both the slug and the tag_prefix must be escaped the same way when
    # they contain literal dashes. The SoT stores the plain values
    # ("agent-assembly", "org-profile") — escaping is a rendering concern.
    shielded_slug = slug.replace("-", "--")
    shielded_tag = tag_prefix.replace("-", "--")

    logo_frag = f"logo={logo}"
    if logo_color:
        logo_frag += f"&logoColor={logo_color}"
    return (
        f"[![{slug}](https://img.shields.io/badge/"
        f"{shielded_slug}-{shielded_tag}-{label_color}?{logo_frag})]"
        f"(https://github.com/{repo_full})"
    )


def _render_repo_row(r: dict) -> str:
    """One Repository Status table row for a public repo."""
    ci_list = r.get("activity_ci") or []
    # Empty cells render as "| |" (single space between pipes) — matches
    # the existing README convention and avoids "|  |" (double space)
    # that a naive " ".join() on an empty list would produce.
    parts = [
        _render_repo_name_badge(r),
        str(r["role"]),
        " ".join(str(v) for v in (r.get("version") or [])),
        " ".join(str(v) for v in ci_list) if ci_list else "",
        " ".join(str(v) for v in (r.get("activity_meta") or [])),
    ]
    # Empty cell => "| |" (single-space) to match the pre-existing rows.
    # A naive f"| {a} | {b} |" would emit "|  |" for an empty cell.
    row = "|"
    for p in parts:
        row += f" {p} |" if p else " |"
    return row


def render_install_channels(channels: list[dict]) -> str:
    """Render the Install channels subsections."""
    out: list[str] = []
    for ch in channels:
        heading = str(ch["heading"])
        lang = ch.get("lang")
        commands = ch.get("commands") or []
        note = ch.get("note")

        out.append(f"#### {heading}")
        out.append("")

        if lang and commands:
            out.append(f"```{lang}")
            for c in commands:
                out.append(str(c))
            out.append("```")
            out.append("")

        if note:
            note_text = str(note).rstrip("\n")
            out.append(note_text)
            out.append("")

    # Trim trailing blank line so we don't add a spurious extra newline
    # before the closing END sentinel.
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Governance-doc contact/SLA blocks (AAASM-5520)
# ---------------------------------------------------------------------------
# These render the SHARED contact + security-response facts into the bounded
# regions of SECURITY.md / SUPPORT.md so the addresses and SLAs have one owner
# (the registry) instead of being hand-copied. Repo-specific threat-model /
# reporting prose stays OUTSIDE the sentinels and is not touched.
#
# Deliberate wording constraints (AAASM-5514 governance):
#   - The canonical published contact is the `.com` `primary`.
#   - The historical `.dev` alias is labeled legacy-compatibility only.
#   - NOTHING here claims the `.com` mailbox is live/sending: no Workspace tenant
#     exists yet (mail_platform.*_status == "planned"). The legacy `.dev`
#     addresses continue to receive via Cloudflare Email Routing during the
#     transition, so the note points reporters at an address that actually
#     delivers today without over-claiming the `.com` cutover.

# Human-readable unit phrasing for the structured SLA value/unit pairs. Kept as
# a small fixed map (not English baked into the SoT) so the registry stays
# structured and the rendering is the consumer's concern.
_SLA_UNIT_LABELS = {
    "business_days": ("business day", "business days"),
    "calendar_days": ("calendar day", "calendar days"),
    "hours": ("hour", "hours"),
}


def _format_sla(block: dict, where: str) -> str:
    """Render a structured ``{value, unit}`` SLA as human text (e.g. ``2 business days``)."""
    value = _as_int(block["value"], f"{where}.value")
    unit = block["unit"]
    singular, plural = _SLA_UNIT_LABELS[unit]
    return f"{value} {singular if value == 1 else plural}"


def render_security_contact_block(data: dict) -> str:
    """Render the shared SECURITY.md contact + response-target region.

    Emits the canonical `.com` reporting address, a labeled legacy-alias note
    (with the Cloudflare-routing transitional fact so reporters use an address
    that delivers), and the structured acknowledgement / initial-assessment
    SLAs. Repo-specific reporting instructions and threat model stay outside
    the bounded block.
    """
    contacts = data.get("contacts") or {}
    sec = contacts.get("security") or {}
    primary = sec["primary"]
    aliases = sec.get("legacy_aliases") or []
    sp = data.get("security_policy") or {}
    ack = _format_sla(sp["acknowledgement"], "security_policy.acknowledgement")
    assess = _format_sla(
        sp["initial_assessment"], "security_policy.initial_assessment"
    )

    lines = [
        f"Report security vulnerabilities privately to **{primary}**. "
        "Do not open a public issue or discussion for a security report.",
        "",
        "| Response stage | Target |",
        "| --- | --- |",
        f"| Acknowledgement | Within {ack} |",
        f"| Initial assessment | Within {assess} |",
    ]
    if aliases:
        alias_md = ", ".join(f"`{a}`" for a in aliases)
        lines += [
            "",
            f"> **Legacy address.** {alias_md} "
            f"{'remain' if len(aliases) > 1 else 'remains'} a legacy "
            "compatibility alias. During the in-progress migration to the "
            f"canonical `{primary}` identity, the legacy address continues to "
            "receive mail via Cloudflare Email Routing, so a report sent there "
            "still reaches us. The canonical mailbox is not yet live-sending.",
        ]
    return "\n".join(lines)


def render_conduct_contact_block(data: dict) -> str:
    """Render the CODE_OF_CONDUCT.md reporting line.

    The CoC routes conduct reports to the same security mailbox; render the
    canonical `.com` primary so the `.dev` literal is migrated and drift-gated
    like every other consumer. Preserves the existing routing behaviour.
    """
    sec = (data.get("contacts") or {}).get("security") or {}
    primary = sec["primary"]
    return (
        f"Concerns about contributor conduct may be reported to the project "
        f"team at **{primary}**. All reports will be reviewed promptly and "
        "fairly, and the privacy of the reporter will be respected."
    )


def render_support_contacts_block(data: dict) -> str:
    """Render the shared SUPPORT.md contact region (support + security addresses).

    Support is a `.com`-only audience (no legacy alias); security carries the
    same legacy-alias transitional note as SECURITY.md so the two documents
    never diverge on the address to use.
    """
    contacts = data.get("contacts") or {}
    support_primary = (contacts.get("support") or {})["primary"]
    sec = contacts.get("security") or {}
    sec_primary = sec["primary"]
    lines = [
        f"- **Support:** email **{support_primary}** for general product and "
        "integration questions.",
        f"- **Security:** report vulnerabilities privately to **{sec_primary}** "
        "(see [`SECURITY.md`](SECURITY.md)); do not open a public issue.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Contact / mail / security-policy schema validation (AAASM-5519)
# ---------------------------------------------------------------------------
# The widened schema publishes PUBLIC identity facts only. These validators run
# before any projection so malformed or policy-violating input fails LOUDLY
# (non-zero exit, descriptive message) instead of being silently published. Each
# rule maps to an acceptance criterion: address/domain format, primary-vs-legacy
# `.com`/`.dev` semantics, uniqueness, structured SLA presence, and a
# forbidden-private-pattern guard so a recovery/admin identity, account id,
# token, DKIM private material, or phone number can never reach a public
# artifact.

# Canonical org apex domain and its legacy alias. A `primary` contact must live
# on the `.com` apex (or an approved subdomain of it); a `.dev` address is only
# ever allowed under `legacy_aliases`.
CANONICAL_APEX = "agent-assembly.com"
LEGACY_APEX = "agent-assembly.dev"

# Fixed vocabularies the schema is validated against, so a typo fails clearly
# rather than silently misrendering downstream.
SLA_UNITS = frozenset({"business_days", "calendar_days", "hours"})
MAIL_STATUSES = frozenset({"planned", "in_progress", "active"})

# Conservative RFC-5322-subset address / hostname shapes. We do not attempt full
# RFC parsing — we reject anything that is obviously not a plain published
# address/domain, which is enough to catch fat-finger errors and to anchor the
# private-pattern guard below.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._%+-]*@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$")
_DOMAIN_RE = re.compile(r"^([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$")

# Forbidden PRIVATE / SECRET patterns. The public registry must never carry
# operational or secret data (ADR 0014). These match on both keys and values:
#   - local-parts that name a recovery/admin/root/superadmin/on-call identity
#   - phone numbers
#   - obvious token/secret/credential/DKIM-private material
#   - provider account-id shaped keys
# The guard fails closed: a match anywhere in the contact/mail/security blocks
# aborts generation.
_FORBIDDEN_LOCALPARTS = (
    "recovery",
    "admin",
    "administrator",
    "superadmin",
    "super-admin",
    "root",
    "postmaster-recovery",
    "oncall",
    "on-call",
    "pagerduty",
)
_FORBIDDEN_KEY_SUBSTRINGS = (
    "recovery",
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "credential",
    "private_key",
    "privatekey",
    "dkim_private",
    "dkim-private",
    "account_id",
    "account-id",
    "phone",
    "pager",
    "oncall",
    "on_call",
    "on-call",
)
_PHONE_RE = re.compile(r"(?:\+?\d[\s().-]?){7,}")
# High-entropy / secret-shaped literals: long base64/hex-ish runs, PEM headers,
# and DKIM private-key markers. Assembled to catch pasted credentials.
_SECRET_VALUE_RES = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bp=[A-Za-z0-9+/]{40,}={0,2}"),  # DKIM p= public/private blob
    re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"),  # long base64-ish token
    re.compile(r"\b[0-9a-fA-F]{32,}\b"),  # long hex token
)


class SchemaError(RuntimeError):
    """Raised when the widened contact/mail/security schema is invalid."""


def _as_int(value: Any, where: str) -> int:
    """Coerce a parsed scalar to int, or raise SchemaError.

    The minimal YAML parser returns every scalar as a string, so a schema-level
    integer arrives as e.g. "2". Accept a non-negative integer literal; reject
    anything else (floats, prose, empty) with a descriptive message.
    """
    if isinstance(value, bool):  # bool is an int subclass — reject explicitly.
        raise SchemaError(f"{where}: expected an integer, got a boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise SchemaError(f"{where}: expected an integer, got {value!r}")


def _check_no_forbidden_key(key: str, path: str) -> None:
    lowered = key.lower()
    for sub in _FORBIDDEN_KEY_SUBSTRINGS:
        if sub in lowered:
            raise SchemaError(
                f"{path}: forbidden key {key!r} — looks like private/secret "
                f"data (matched {sub!r}); this belongs in the private runbook "
                "or secret manager, never the public registry"
            )


def _check_no_forbidden_value(value: str, path: str) -> None:
    lowered = value.lower()
    for lp in _FORBIDDEN_LOCALPARTS:
        # Match the forbidden identity only as the address local-part, so a
        # legitimate domain label can't false-positive.
        if lowered.startswith(lp + "@") or lowered.startswith(lp + "-@"):
            raise SchemaError(
                f"{path}: forbidden value {value!r} — names a "
                f"recovery/admin/on-call identity ({lp!r}); not publishable"
            )
    if _PHONE_RE.search(value):
        raise SchemaError(
            f"{path}: forbidden value {value!r} — looks like a phone number; "
            "phone contacts are private operational data"
        )
    for rx in _SECRET_VALUE_RES:
        if rx.search(value):
            raise SchemaError(
                f"{path}: forbidden value at {path} — looks like a "
                "token/secret/private-key blob; secrets never go in the registry"
            )


def _walk_forbidden(node: Any, path: str) -> None:
    """Recursively enforce the forbidden-private-pattern guard over a subtree."""
    if isinstance(node, dict):
        for k, v in node.items():
            _check_no_forbidden_key(str(k), f"{path}.{k}")
            _walk_forbidden(v, f"{path}.{k}")
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            _walk_forbidden(item, f"{path}[{idx}]")
    elif isinstance(node, str):
        _check_no_forbidden_value(node, path)


def _validate_email(addr: Any, path: str) -> str:
    if not isinstance(addr, str) or not _EMAIL_RE.match(addr):
        raise SchemaError(f"{path}: {addr!r} is not a valid email address")
    return addr


def _validate_domain(dom: Any, path: str) -> str:
    if not isinstance(dom, str) or not _DOMAIN_RE.match(dom):
        raise SchemaError(f"{path}: {dom!r} is not a valid domain name")
    return dom


def _domain_of(addr: str) -> str:
    return addr.rsplit("@", 1)[-1].lower()


def _is_canonical_com(domain: str) -> bool:
    """True if ``domain`` is the `.com` apex or an approved subdomain of it."""
    return domain == CANONICAL_APEX or domain.endswith("." + CANONICAL_APEX)


def _validate_contact_primary(primary: Any, base: str, seen: set[str]) -> None:
    """Validate a contact block's required, canonical, unique primary address."""
    if primary is None:
        raise SchemaError(f"{base}.primary: required")
    _validate_email(primary, f"{base}.primary")
    dom = _domain_of(primary)
    # Primary-vs-legacy semantics: a canonical AA primary must be `.com`
    # (never `.dev`); a `.dev` address is only allowed under legacy_aliases.
    if dom == LEGACY_APEX or dom.endswith("." + LEGACY_APEX):
        raise SchemaError(
            f"{base}.primary: {primary!r} is a legacy '.dev' address — a "
            "canonical primary must be '.com'; put '.dev' under legacy_aliases"
        )
    if not _is_canonical_com(dom):
        raise SchemaError(
            f"{base}.primary: {primary!r} is not on the canonical "
            f"'{CANONICAL_APEX}' domain"
        )
    if primary.lower() in seen:
        raise SchemaError(f"{base}.primary: {primary!r} is not unique")
    seen.add(primary.lower())


def _validate_contact_aliases(aliases: Any, base: str, seen: set[str]) -> None:
    """Validate a contact block's optional, unique legacy_aliases list."""
    if aliases in (None, ""):
        aliases = []
    if not isinstance(aliases, list):
        raise SchemaError(f"{base}.legacy_aliases: must be a list")
    for idx, alias in enumerate(aliases):
        apath = f"{base}.legacy_aliases[{idx}]"
        _validate_email(alias, apath)
        if alias.lower() in seen:
            raise SchemaError(f"{apath}: {alias!r} is not unique")
        seen.add(alias.lower())


def _validate_contacts(contacts: Any, seen: set[str]) -> None:
    if not isinstance(contacts, dict) or not contacts:
        raise SchemaError("contacts: must be a non-empty mapping of audiences")
    for audience, block in contacts.items():
        base = f"contacts.{audience}"
        if not isinstance(block, dict):
            raise SchemaError(f"{base}: must be a mapping")
        _validate_contact_primary(block.get("primary"), base, seen)
        _validate_contact_aliases(block.get("legacy_aliases", []), base, seen)


def _validate_sla_target(block: Any, base: str) -> None:
    """Validate one SLA target's structured {value, unit} mapping."""
    if not isinstance(block, dict):
        raise SchemaError(f"{base}: required structured value/unit mapping")
    if "value" not in block:
        raise SchemaError(f"{base}.value: required")
    if "unit" not in block:
        raise SchemaError(f"{base}.unit: required (structured, not prose)")
    val = _as_int(block["value"], f"{base}.value")
    if val <= 0:
        raise SchemaError(f"{base}.value: must be a positive integer")
    unit = block["unit"]
    if unit not in SLA_UNITS:
        raise SchemaError(f"{base}.unit: {unit!r} not in {sorted(SLA_UNITS)}")


def _validate_sla(security_policy: Any) -> None:
    if not isinstance(security_policy, dict) or not security_policy:
        raise SchemaError("security_policy: must be a non-empty mapping")
    for target in ("acknowledgement", "initial_assessment"):
        _validate_sla_target(
            security_policy.get(target), f"security_policy.{target}"
        )


def _validate_schema_version(data: dict) -> None:
    # schema_version must be present and a positive integer.
    if "schema_version" not in data:
        raise SchemaError("schema_version: required top-level key is missing")
    if _as_int(data["schema_version"], "schema_version") < 1:
        raise SchemaError("schema_version: must be >= 1")


def _validate_mail_domains(mail_domains: Any) -> None:
    if not isinstance(mail_domains, dict) or not mail_domains:
        raise SchemaError("mail_domains: must be a non-empty mapping")
    _validate_domain(mail_domains.get("human"), "mail_domains.human")
    _validate_domain(mail_domains.get("legacy_human"), "mail_domains.legacy_human")
    _validate_domain(mail_domains.get("transactional"), "mail_domains.transactional")
    if not _is_canonical_com(str(mail_domains["human"]).lower()):
        raise SchemaError("mail_domains.human: must be on the canonical '.com' domain")


def _validate_transactional_from(
    txn: Any, txn_domain: str, seen: set[str]
) -> None:
    if not isinstance(txn, dict) or not txn:
        raise SchemaError("transactional_from: must be a non-empty mapping")
    for key, addr in txn.items():
        path = f"transactional_from.{key}"
        _validate_email(addr, path)
        if _domain_of(addr) != txn_domain:
            raise SchemaError(
                f"{path}: {addr!r} must be on the transactional domain "
                f"'{txn_domain}'"
            )
        if addr.lower() in seen:
            raise SchemaError(f"{path}: {addr!r} is not unique")
        seen.add(addr.lower())


def _validate_mail_platform(mail_platform: Any) -> None:
    if not isinstance(mail_platform, dict) or not mail_platform:
        raise SchemaError("mail_platform: must be a non-empty mapping")
    for status_key in ("human_mail_status", "transactional_status"):
        status = mail_platform.get(status_key)
        if status not in MAIL_STATUSES:
            raise SchemaError(
                f"mail_platform.{status_key}: {status!r} not in "
                f"{sorted(MAIL_STATUSES)}"
            )


def validate_contact_schema(data: dict) -> None:
    """Validate the widened contact/mail/security schema; raise on any problem.

    Runs the forbidden-private-pattern guard first (fail closed on leakage),
    then the structural / semantic rules. Called before projection so a public
    artifact is never produced from invalid input.
    """
    _validate_schema_version(data)

    # Forbidden-private-pattern guard over only the new blocks (the repo table /
    # urls / jira sections are governed elsewhere and legitimately carry ids).
    for section in ("contacts", "mail_domains", "transactional_from",
                    "mail_platform", "security_policy"):
        if section in data:
            _walk_forbidden(data[section], section)

    seen_addrs: set[str] = set()
    _validate_contacts(data.get("contacts"), seen_addrs)

    mail_domains = data.get("mail_domains")
    _validate_mail_domains(mail_domains)
    _validate_transactional_from(
        data.get("transactional_from"),
        str(mail_domains["transactional"]).lower(),
        seen_addrs,
    )
    _validate_mail_platform(data.get("mail_platform"))
    _validate_sla(data.get("security_policy"))


# ---------------------------------------------------------------------------
# Public projection of the contact / mail / security schema
# ---------------------------------------------------------------------------


def _project_contacts_block(data: dict) -> dict:
    """Build the deterministic public projection of the widened schema.

    Only public identity facts are emitted, in insertion order, with SLA/version
    integers coerced from their parsed string form so the JSON carries real
    numbers. This runs AFTER validate_contact_schema, so every field here is
    already known valid and leakage-free.

    Returns an empty dict when the widened schema is absent (no
    ``schema_version`` key), so the projection is purely additive — a registry
    without the AAASM-5519 blocks projects exactly as it did before.
    """
    if "schema_version" not in data:
        return {}

    contacts_out: dict[str, dict] = {}
    for audience, block in (data.get("contacts") or {}).items():
        entry: dict[str, Any] = {"primary": block["primary"]}
        aliases = block.get("legacy_aliases") or []
        if aliases:
            entry["legacy_aliases"] = list(aliases)
        contacts_out[audience] = entry

    security_policy = data.get("security_policy") or {}
    sla_out: dict[str, dict] = {}
    for target, blk in security_policy.items():
        sla_out[target] = {
            "value": _as_int(blk["value"], f"security_policy.{target}.value"),
            "unit": blk["unit"],
        }

    return {
        "schema_version": _as_int(data["schema_version"], "schema_version"),
        "contacts": contacts_out,
        "mail_domains": dict(data.get("mail_domains") or {}),
        "transactional_from": dict(data.get("transactional_from") or {}),
        "mail_platform": dict(data.get("mail_platform") or {}),
        "security_policy": sla_out,
    }


def render_registry_json(data: dict) -> str:
    """Render metadata/generated/registry.json — the shared-metadata projection.

    This is the derived artifact cross-repo consumers read instead of
    hand-copying a URL, repo name, or Jira id. Two ADR 0014 invariants shape it:

    - Visibility filter: a private repo's slug/metadata MUST NOT appear in this
      public artifact, so only ``visibility: public`` repos are projected.
    - Shared-facts only: the README's badge/version/activity markdown is
      presentation, not shared metadata, so it is deliberately excluded — the
      projection carries just the identity fields other repos actually consume.

    Key order is deterministic (insertion order, no sort) so the drift gate's
    byte comparison is stable.
    """
    public_repos = [
        {
            "slug": r.get("slug"),
            "repo": r.get("repo"),
            "default_branch": r.get("default_branch"),
            "role": r.get("role"),
            "visibility": r.get("visibility"),
        }
        for r in (data.get("repos") or [])
        if r.get("visibility") == "public"
    ]
    contact_schema = _project_contacts_block(data)
    projection: dict[str, Any] = {
        "_readme": (
            "DO NOT EDIT. Generated by scripts/generate_org_profile.py from "
            "metadata/org-profile.yaml (canonical metadata registry, ADR 0014). "
            "Edit the registry and regenerate; see metadata/README.md."
        ),
    }
    if contact_schema:
        projection["schema_version"] = contact_schema["schema_version"]
    projection["org"] = data.get("org")
    projection["product"] = data.get("product", {})
    # Public contact/mail/security-policy facts (AAASM-5519). Only the public
    # projection is emitted — no private/internal fields, no secrets. These are
    # inserted after `product` and before `urls` to mirror the SoT order, and
    # only when the widened schema is present (purely additive).
    if contact_schema:
        projection["contacts"] = contact_schema["contacts"]
        projection["mail_domains"] = contact_schema["mail_domains"]
        projection["transactional_from"] = contact_schema["transactional_from"]
        projection["mail_platform"] = contact_schema["mail_platform"]
        projection["security_policy"] = contact_schema["security_policy"]
    projection.update({
        "urls": data.get("urls", {}),
        "governance": data.get("governance", {}),
        "jira": data.get("jira", {}),
        "repos": public_repos,
    })
    return json.dumps(projection, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Bounded-section substitution
# ---------------------------------------------------------------------------


def replace_bounded(text: str, block_id: str, new_body: str, where: str = "profile/README.md") -> str:
    """Replace the content between BEGIN/END sentinels for block_id.

    The sentinel lines themselves are preserved. new_body is inserted between
    them, on its own lines, with a single blank line of padding on each side.
    ``where`` names the file for the not-found error message.
    """
    begin_marker = f"<!-- BEGIN GENERATED: {block_id} -->"
    end_marker = f"<!-- END GENERATED: {block_id} -->"

    b = text.find(begin_marker)
    e = text.find(end_marker)
    if b < 0 or e < 0 or e < b:
        raise RuntimeError(
            f"bounded section {block_id!r} not found in {where} — "
            f"expected {begin_marker!r} ... {end_marker!r}"
        )

    before = text[: b + len(begin_marker)]
    after = text[e:]
    return f"{before}\n{new_body}\n{after}"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def build_artifacts() -> dict[Path, str]:
    """Return every generated artifact as ``{path: desired_content}``.

    Both consumers are driven from the one registry: the org-profile README's
    bounded blocks (the human front door) and metadata/generated/registry.json
    (the machine-readable projection for cross-repo consumers).
    """
    data = parse_yaml(SOT_PATH.read_text(encoding="utf-8"))

    # Validate the widened contact/mail/security schema BEFORE producing any
    # artifact, so malformed or leakage-prone input fails the run (and thus the
    # drift gate) rather than being silently published.
    validate_contact_schema(data)

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_bounded(readme, "repo_table", render_repo_table(data.get("repos", [])))
    readme = replace_bounded(
        readme, "install_channels", render_install_channels(data.get("install_channels", []))
    )

    # In-repo governance docs consume the shared contact/SLA facts through their
    # own bounded regions (AAASM-5520). Rendered from the same validated data so
    # the addresses and response targets can never drift from the registry.
    security = SECURITY_PATH.read_text(encoding="utf-8")
    security = replace_bounded(
        security, "security_contact", render_security_contact_block(data), where="SECURITY.md"
    )
    support = SUPPORT_PATH.read_text(encoding="utf-8")
    support = replace_bounded(
        support, "support_contacts", render_support_contacts_block(data), where="SUPPORT.md"
    )
    coc = CODE_OF_CONDUCT_PATH.read_text(encoding="utf-8")
    coc = replace_bounded(
        coc, "conduct_contact", render_conduct_contact_block(data), where="CODE_OF_CONDUCT.md"
    )

    return {
        README_PATH: readme,
        SECURITY_PATH: security,
        SUPPORT_PATH: support,
        CODE_OF_CONDUCT_PATH: coc,
        REGISTRY_JSON_PATH: render_registry_json(data),
    }


def _read_or_empty(path: Path) -> str:
    """Read ``path``, treating a not-yet-generated artifact as empty (drift)."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if regenerating would change any generated artifact.",
    )
    args = parser.parse_args(argv)

    # A malformed registry (bad YAML subset, or an invalid/leakage-prone
    # contact schema) must fail the gate loudly with a readable message rather
    # than a bare traceback — CI reads stderr.
    try:
        artifacts = build_artifacts()
    except (YamlError, SchemaError) as exc:
        print(f"ERROR: invalid metadata/org-profile.yaml — {exc}", file=sys.stderr)
        return 2
    drifted = [p for p, content in artifacts.items() if _read_or_empty(p) != content]

    if not drifted:
        print("Generated artifacts are up to date with metadata/org-profile.yaml.")
        return 0

    if args.check:
        for p in drifted:
            print(
                f"DRIFT: {p.relative_to(REPO_ROOT)} does not match "
                "metadata/org-profile.yaml.",
                file=sys.stderr,
            )
        print("Run: python3 scripts/generate_org_profile.py", file=sys.stderr)
        return 1

    # Write each generated artifact to its own module-constant path. Referencing
    # the named constants directly (rather than a loop variable) keeps every
    # write sink provably constant — no user-controlled path can reach it, and
    # static taint analysis can see that without guessing.
    if README_PATH in drifted:
        README_PATH.parent.mkdir(parents=True, exist_ok=True)
        README_PATH.write_text(artifacts[README_PATH], encoding="utf-8")
        print(f"Wrote {README_PATH.relative_to(REPO_ROOT)}.")
    if SECURITY_PATH in drifted:
        SECURITY_PATH.parent.mkdir(parents=True, exist_ok=True)
        SECURITY_PATH.write_text(artifacts[SECURITY_PATH], encoding="utf-8")
        print(f"Wrote {SECURITY_PATH.relative_to(REPO_ROOT)}.")
    if SUPPORT_PATH in drifted:
        SUPPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SUPPORT_PATH.write_text(artifacts[SUPPORT_PATH], encoding="utf-8")
        print(f"Wrote {SUPPORT_PATH.relative_to(REPO_ROOT)}.")
    if CODE_OF_CONDUCT_PATH in drifted:
        CODE_OF_CONDUCT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CODE_OF_CONDUCT_PATH.write_text(artifacts[CODE_OF_CONDUCT_PATH], encoding="utf-8")
        print(f"Wrote {CODE_OF_CONDUCT_PATH.relative_to(REPO_ROOT)}.")
    if REGISTRY_JSON_PATH in drifted:
        REGISTRY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_JSON_PATH.write_text(artifacts[REGISTRY_JSON_PATH], encoding="utf-8")
        print(f"Wrote {REGISTRY_JSON_PATH.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
