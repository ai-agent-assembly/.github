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
    """
    lines: list[str] = [
        "| Repo | Purpose | Version | Base branch health | Activity |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in repos:
        slug = str(r["slug"])
        repo_full = str(r["repo"])
        role = str(r["role"])
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
        name_badge = (
            f"[![{slug}](https://img.shields.io/badge/"
            f"{shielded_slug}-{shielded_tag}-{label_color}?{logo_frag})]"
            f"(https://github.com/{repo_full})"
        )

        version_cell = " ".join(str(v) for v in (r.get("version") or []))
        ci_list = r.get("activity_ci") or []
        # Empty cells render as "| |" (single space between pipes) — matches
        # the existing README convention and avoids "|  |" (double space)
        # that a naive " ".join() on an empty list would produce.
        ci_cell = " ".join(str(v) for v in ci_list) if ci_list else ""
        activity_cell = " ".join(str(v) for v in (r.get("activity_meta") or []))

        parts = [name_badge, role, version_cell, ci_cell, activity_cell]
        # Empty cell => "| |" (single-space) to match the pre-existing rows.
        # A naive f"| {a} | {b} |" would emit "|  |" for an empty cell.
        row = "|"
        for p in parts:
            row += f" {p} |" if p else " |"
        lines.append(row)
    return "\n".join(lines)


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
            "visibility": r.get("visibility", "public"),
        }
        for r in (data.get("repos") or [])
        if (r.get("visibility") or "public") == "public"
    ]
    projection = {
        "_readme": (
            "DO NOT EDIT. Generated by scripts/generate_org_profile.py from "
            "metadata/org-profile.yaml (canonical metadata registry, ADR 0014). "
            "Edit the registry and regenerate; see metadata/README.md."
        ),
        "org": data.get("org"),
        "product": data.get("product", {}),
        "urls": data.get("urls", {}),
        "governance": data.get("governance", {}),
        "jira": data.get("jira", {}),
        "repos": public_repos,
    }
    return json.dumps(projection, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Bounded-section substitution
# ---------------------------------------------------------------------------


def replace_bounded(text: str, block_id: str, new_body: str) -> str:
    """Replace the content between BEGIN/END sentinels for block_id.

    The sentinel lines themselves are preserved. new_body is inserted between
    them, on its own lines, with a single blank line of padding on each side.
    """
    begin_marker = f"<!-- BEGIN GENERATED: {block_id} -->"
    end_marker = f"<!-- END GENERATED: {block_id} -->"

    b = text.find(begin_marker)
    e = text.find(end_marker)
    if b < 0 or e < 0 or e < b:
        raise RuntimeError(
            f"bounded section {block_id!r} not found in profile/README.md — "
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

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_bounded(readme, "repo_table", render_repo_table(data.get("repos", [])))
    readme = replace_bounded(
        readme, "install_channels", render_install_channels(data.get("install_channels", []))
    )

    return {
        README_PATH: readme,
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

    artifacts = build_artifacts()
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
    if REGISTRY_JSON_PATH in drifted:
        REGISTRY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_JSON_PATH.write_text(artifacts[REGISTRY_JSON_PATH], encoding="utf-8")
        print(f"Wrote {REGISTRY_JSON_PATH.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
