#!/usr/bin/env python3
"""Tests for the visibility filter in scripts/generate_org_profile.py.

The generated profile/README.md and metadata/generated/registry.json are both
PUBLIC artifacts (ADR 0014): a private repo's slug/metadata must never leak into
either. These tests pin that invariant for both the repo table and the registry
projection, and assert the fail-closed default (a repo whose visibility marker
is missing or malformed is treated as private and dropped, not published).

Stdlib-only, matching the generator — run with `python3 -m pytest scripts/` or
plain `python3 scripts/test_generate_org_profile.py`.
"""

from __future__ import annotations

import json

import generate_org_profile as gen


def _public_repo(slug: str) -> dict:
    return {
        "slug": slug,
        "repo": f"ai-agent-assembly/{slug}",
        "default_branch": "master",
        "role": f"{slug} role",
        "visibility": "public",
    }


def _private_repo(slug: str) -> dict:
    r = _public_repo(slug)
    r["visibility"] = "private"
    return r


def test_repo_table_excludes_private_repo() -> None:
    repos = [_public_repo("agent-assembly"), _private_repo("cloud")]
    table = gen.render_repo_table(repos)

    assert "agent-assembly" in table
    # A private repo's slug must never appear in the public README table.
    assert "cloud" not in table


def test_repo_table_includes_public_repo() -> None:
    table = gen.render_repo_table([_public_repo("python-sdk")])
    assert "python-sdk" in table


def test_repo_table_fails_closed_on_missing_visibility() -> None:
    # A repo added without an explicit visibility marker must be dropped, not
    # published — the filter fails closed rather than fail-open.
    repo = _public_repo("mystery")
    del repo["visibility"]
    # Absent visibility is treated as non-public and dropped (matches
    # render_registry_json): the filter requires an explicit "public" marker.
    assert "mystery" not in gen.render_repo_table([repo])

    # A malformed/unknown visibility value is likewise excluded from the public table.
    repo["visibility"] = "internal"
    assert "mystery" not in gen.render_repo_table([repo])


def test_registry_json_excludes_private_repo() -> None:
    # Mirror-of-record for the sibling artifact: the registry projection already
    # filters private repos; assert it so both public artifacts stay in lockstep.
    data = {"repos": [_public_repo("agent-assembly"), _private_repo("cloud")]}
    projection = json.loads(gen.render_registry_json(data))
    slugs = [r["slug"] for r in projection["repos"]]
    assert slugs == ["agent-assembly"]


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
