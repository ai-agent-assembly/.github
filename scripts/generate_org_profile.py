#!/usr/bin/env python3
"""Regenerate bounded blocks in profile/README.md from metadata/org-profile.yaml.

The org profile at profile/README.md is a public front door rendered by
GitHub at github.com/ai-agent-assembly. It carries per-SDK badge tables,
install snippets, and repo-URL references that drift silently every time a
repo is renamed or an SDK package id changes. This script rewrites the two
drift-prone bounded sections from a single source of truth so those refs stay
in lockstep with metadata/org-profile.yaml.

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
import re
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_PATH = REPO_ROOT / "metadata" / "org-profile.yaml"
README_PATH = REPO_ROOT / "profile" / "README.md"

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

        parent_indent, parent = stack[-1]

        if content.startswith("- "):
            # List item. Parent must be a list — or we need to convert here.
            if not isinstance(parent, list):
                raise YamlError(f"line {i+1}: list item under non-list container")
            item_body = content[2:].strip()
            if ":" in item_body and not item_body.startswith('"'):
                # Inline mapping start: "- key: value" or "- key:"
                # Treat as start of a new dict that also gets this key.
                new_map: dict = {}
                parent.append(new_map)
                stack.append((indent, new_map))
                # Feed the key/value line back into the loop by inserting a
                # virtual line at the same indent + 2.
                virtual = " " * (indent + 2) + item_body
                raw_lines[i] = virtual
                continue  # re-process without advancing i
            else:
                # Scalar list item
                parent.append(_unquote(item_body))
                i += 1
                continue

        # Key: value or Key:
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
            # Container follows. Peek next non-blank line for '-' vs 'k:'.
            j = i + 1
            container: Any = None
            while j < len(raw_lines):
                nxt = raw_lines[j]
                if not nxt.strip() or nxt.lstrip().startswith("#"):
                    j += 1
                    continue
                nxt_indent = _indent_of(nxt)
                if nxt_indent <= indent:
                    # No children — empty mapping by convention.
                    container = {}
                    break
                if nxt.lstrip().startswith("- "):
                    container = []
                else:
                    container = {}
                break
            if container is None:
                container = {}
            parent[key] = container
            stack.append((indent, container))
            i += 1
            continue

        if rest.startswith("|"):
            # Block scalar (literal). Collect lines indented > current indent.
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
            parent[key] = "\n".join(body_lines) + "\n"
            i = j
            continue

        # Simple scalar
        parent[key] = _unquote(rest)
        i += 1

    return root


# ---------------------------------------------------------------------------
# Block rendering
# ---------------------------------------------------------------------------


def render_repo_table(repos: list[dict]) -> str:
    """Render the Repository Status table rows.

    Only the data rows are generated. The header + separator remain in the
    static prelude of the section (outside the bounded block), so a future
    columns change stays visible in review.
    """
    lines: list[str] = []
    for r in repos:
        slug = str(r["slug"])
        repo_full = str(r["repo"])
        role = str(r["role"])
        badge = r.get("badge", {}) or {}
        label_color = str(badge.get("label_color", "000000"))
        logo = str(badge.get("logo", "github"))
        logo_color = badge.get("logo_color")
        tag_prefix = str(badge.get("tag_prefix", ""))

        # shields.io renders "--" as a single dash in badge label paths.
        shielded_slug = slug.replace("-", "--")

        logo_frag = f"logo={logo}"
        if logo_color:
            logo_frag += f"&logoColor={logo_color}"
        name_badge = (
            f"[![{slug}](https://img.shields.io/badge/"
            f"{shielded_slug}-{tag_prefix}-{label_color}?{logo_frag})]"
            f"(https://github.com/{repo_full})"
        )

        version_cell = " ".join(str(v) for v in (r.get("version") or []))
        ci_list = r.get("activity_ci") or []
        ci_cell = " ".join(str(v) for v in ci_list) if ci_list else ""
        activity_cell = " ".join(str(v) for v in (r.get("activity_meta") or []))

        lines.append(
            f"| {name_badge} | {role} | {version_cell} | {ci_cell} | {activity_cell} |"
        )
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


def generate() -> str:
    sot_text = SOT_PATH.read_text(encoding="utf-8")
    data = parse_yaml(sot_text)

    readme = README_PATH.read_text(encoding="utf-8")

    repo_body = render_repo_table(data.get("repos", []))
    readme = replace_bounded(readme, "repo_table", repo_body)

    install_body = render_install_channels(data.get("install_channels", []))
    readme = replace_bounded(readme, "install_channels", install_body)

    return readme


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if regenerating would change profile/README.md.",
    )
    args = parser.parse_args(argv)

    new_readme = generate()
    current = README_PATH.read_text(encoding="utf-8")

    if new_readme == current:
        print("profile/README.md is up to date with metadata/org-profile.yaml.")
        return 0

    if args.check:
        print(
            "DRIFT: profile/README.md does not match metadata/org-profile.yaml.\n"
            "Run: python3 scripts/generate_org_profile.py",
            file=sys.stderr,
        )
        return 1

    README_PATH.write_text(new_readme, encoding="utf-8")
    print(f"Wrote {README_PATH.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
