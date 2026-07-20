#!/usr/bin/env python3
"""Hardcoded-metadata drift lint (ADR 0014, the lint-flag-on-hardcoded-value mode).

The org has two drift-gate mechanisms (ADR 0014, Decision §3). The generation
gate (`scripts/generate_org_profile.py --check`, wired by
`.github/workflows/org-profile-drift.yml`) covers artifacts that can host a
bounded generated region. This lint is the second mechanism — the guard for
free prose and scattered references where a generated block is impractical. It
fails CI when a metadata value the canonical registry *supersedes* is
hand-typed anywhere in the tree outside an explicit allowlist of
legitimate/definitional locations.

Why a superseded-literal scan rather than a generic "any registry value copied
outside the registry" scan: the drift the 2026-07 audit (ADR 0014 Appendix A)
actually found is *stale* values that contradict the registry — pre-rename repo
slugs (AAASM-4341 residue) and a Jira field id the registry records as null.
Those are the values a hand edit reintroduces, so those are what the gate must
catch. Each stale literal is paired with the registry-owned value that replaces
it, and — where the registry publicly owns that value — the canonical side is
asserted against `metadata/generated/registry.json` at startup. So a future
rename updates the registry and this table together; the lint cannot silently
drift away from the registry it defends.

stdlib only (no PyYAML) so it runs on a bare CI runner. Usage:

    python3 scripts/check_metadata_drift.py     # scan tree; exit 1 on drift
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_JSON = REPO_ROOT / "metadata" / "generated" / "registry.json"

# This script and the workflow that runs it hold the stale literals as data, so
# they are never scanned as content.
SELF_PATHS = {
    "scripts/check_metadata_drift.py",
    ".github/workflows/metadata-drift.yml",
}


@dataclass(frozen=True)
class Rule:
    """A superseded metadata literal and the registry value that replaces it.

    ``allow`` lists path prefixes where the stale literal may legitimately
    appear because the file *documents* that it is superseded (e.g. the
    ticket-authoring skill recording that ``customfield_10041`` is null, or the
    registry's own explanatory note). ``anchor`` names how ``canonical`` is
    validated against the registry: ``public_slug`` (must be a public repo slug
    in registry.json), ``jira_components`` (registry's components field),
    ``url`` (must appear among registry ``urls`` values), or ``none`` (canonical
    is a private repo slug that, per the context-boundary rules, is not carried
    in the public registry — so it cannot be registry-checked).
    """

    literal: str
    canonical: str
    why: str
    anchor: str
    allow: tuple[str, ...] = field(default_factory=tuple)


# Shared rationale for every AAASM-4341 pre-rename slug rule.
_RENAME_4341 = "repo renamed (AAASM-4341)"

# The rename map (AAASM-4341) + the drifted Jira field + the drifted installer
# alias. `agent-assembly-enterprise` and `agent-assembly-spec` deliberately KEEP
# their prefixed names and are intentionally absent here.
RULES: tuple[Rule, ...] = (
    Rule("agent-assembly-cloud", "cloud", _RENAME_4341, "none"),
    Rule("agent-assembly-examples", "examples", _RENAME_4341, "public_slug"),
    Rule("agent-assembly-docs", "docs", _RENAME_4341, "public_slug"),
    Rule("agent-assembly-integration-tests", "e2e-public", _RENAME_4341, "none"),
    Rule("agent-assembly-private-e2e", "e2e-private", _RENAME_4341, "none"),
    Rule(
        "customfield_10041",
        "the native `components` field",
        "customfield_10041 is null on AAASM; Components is the native field",
        "jira_components",
        allow=(
            ".claude/skills/ticket-authoring/",
            "metadata/org-profile.yaml",
            "metadata/README.md",
        ),
    ),
    Rule(
        "install.ai-agent-assembly.dev",
        "tool.agent-assembly.dev",
        "installer alias is registry urls.installer_alt (ADR 0007/0008)",
        "url",
    ),
)


class ConfigError(RuntimeError):
    """The lint's own table has drifted from the registry it defends."""


def load_registry() -> dict:
    if not REGISTRY_JSON.exists():
        raise ConfigError(
            f"{REGISTRY_JSON.relative_to(REPO_ROOT)} is missing — run "
            "scripts/generate_org_profile.py first."
        )
    return json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))


def _url_values(registry: dict) -> set[str]:
    out: set[str] = set()
    for v in (registry.get("urls") or {}).values():
        if isinstance(v, str):
            out.add(v)
        elif isinstance(v, dict):  # docs_sdk_base
            out.update(str(x) for x in v.values())
    return out


def assert_registry_anchors(registry: dict) -> None:
    """Fail loudly if a rule's canonical value no longer matches the registry.

    This is what keeps the lint honest: it enforces the registry's *current*
    values, so it cannot outlive a rename or a URL change the registry made.
    """
    public_slugs = {r.get("slug") for r in (registry.get("repos") or [])}
    components_field = (registry.get("jira") or {}).get("components_field")
    urls = _url_values(registry)

    for rule in RULES:
        if rule.anchor == "public_slug" and rule.canonical not in public_slugs:
            raise ConfigError(
                f"rule for {rule.literal!r} expects canonical slug "
                f"{rule.canonical!r}, absent from registry repos[]."
            )
        if rule.anchor == "jira_components" and components_field != "components":
            raise ConfigError(
                f"rule for {rule.literal!r} expects jira.components_field "
                f"'components', registry has {components_field!r}."
            )
        if rule.anchor == "url" and not any(rule.canonical in u for u in urls):
            raise ConfigError(
                f"rule for {rule.literal!r} expects canonical URL host "
                f"{rule.canonical!r}, absent from registry urls."
            )


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [p for p in out.split("\0") if p]


def _allowed(rule: Rule, relpath: str) -> bool:
    return any(relpath.startswith(prefix) for prefix in rule.allow)


def scan() -> list[str]:
    violations: list[str] = []
    for relpath in tracked_files():
        if relpath in SELF_PATHS:
            continue
        try:
            text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue  # binary or unreadable — no metadata literals to lint
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule in RULES:
                if rule.literal in line and not _allowed(rule, relpath):
                    violations.append(
                        f"{relpath}:{lineno}: hardcoded {rule.literal!r} — use "
                        f"{rule.canonical} instead ({rule.why})"
                    )
    return violations


def main() -> int:
    try:
        registry = load_registry()
        assert_registry_anchors(registry)
    except ConfigError as exc:
        print(f"metadata-drift lint config error: {exc}", file=sys.stderr)
        return 2

    violations = scan()
    if not violations:
        print(
            "No hardcoded metadata drift found "
            f"({len(RULES)} superseded literals checked against the registry)."
        )
        return 0

    print("Hardcoded metadata that contradicts the registry (ADR 0014):", file=sys.stderr)
    for v in violations:
        print(f"  {v}", file=sys.stderr)
    print(
        "\nEdit metadata/org-profile.yaml (regenerate) or reference the registry "
        "value shown above; do not hand-type a superseded literal.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
