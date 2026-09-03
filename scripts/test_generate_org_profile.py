#!/usr/bin/env python3
"""Tests for the visibility filter in scripts/generate_org_profile.py.

The generated profile/README.md and metadata/generated/registry.json are both
PUBLIC artifacts (ADR 0014): a private repo's slug/metadata must never leak into
either. These tests pin that invariant for both the repo table and the registry
projection, and assert the fail-closed default (a repo whose visibility marker
is missing or malformed is treated as private and dropped, not published).

Also covers the bounded-region replace helper (``replace_bounded``) and the
``--check`` gate's negative control (AAASM-5756): a repo's generated region
being entirely removed from a governance doc must make ``--check`` fail
closed (non-zero exit), not silently pass. The ``--check`` tests never touch
this repo's own SECURITY.md/README.md/etc. — ``monkeypatch`` redirects the
generator's module-level path constants to a ``tmp_path`` fixture tree for
the duration of each test, so there is no live-file mutation risk and no
cross-test race.

Stdlib-only, matching the generator — run with `python3 -m pytest scripts/` or
plain `python3 scripts/test_generate_org_profile.py`.
"""

from __future__ import annotations

import json
import re

import pytest

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


# ---------------------------------------------------------------------------
# replace_bounded — malformed-sentinel negative controls
# ---------------------------------------------------------------------------
# A malformed sentinel pair must raise loudly (RuntimeError) rather than
# silently no-op or corrupt the surrounding text — these are the shapes a
# hand-edit of a generated doc could accidentally produce.


def test_replace_bounded_raises_on_missing_end() -> None:
    text = "before\n<!-- BEGIN GENERATED: foo -->\nold\nafter"
    with pytest.raises(RuntimeError):
        gen.replace_bounded(text, "foo", "new")


def test_replace_bounded_raises_on_missing_begin() -> None:
    text = "before\nold\n<!-- END GENERATED: foo -->\nafter"
    with pytest.raises(RuntimeError):
        gen.replace_bounded(text, "foo", "new")


def test_replace_bounded_raises_on_reversed_sentinels() -> None:
    # END appears before BEGIN for the same id — malformed/reversed.
    text = (
        "before\n<!-- END GENERATED: foo -->\nold\n"
        "<!-- BEGIN GENERATED: foo -->\nafter"
    )
    with pytest.raises(RuntimeError):
        gen.replace_bounded(text, "foo", "new")


# ---------------------------------------------------------------------------
# main(["--check"]) — AC#4 negative control: a removed generated region
# ---------------------------------------------------------------------------
# "Remove one repo's generated block and watch the gate go red" — the
# concrete negative control AAASM-5756 asks for. build_artifacts() reads its
# input/output paths from module-level constants (SOT_PATH, README_PATH,
# SECURITY_PATH, SUPPORT_PATH, CODE_OF_CONDUCT_PATH, REGISTRY_JSON_PATH), so
# monkeypatch redirects every one of them to a tmp_path fixture tree for the
# duration of the test — this repo's own live governance docs are never
# touched, and tmp_path's own per-test isolation rules out any cross-test
# race.

_VALID_SOT_YAML = """\
org: ai-agent-assembly
schema_version: 1
product:
  name: "AI Agent Assembly"
contacts:
  security:
    primary: "security@agent-assembly.com"
    legacy_aliases:
      - "security@agent-assembly.dev"
  support:
    primary: "support@agent-assembly.com"
mail_domains:
  human: agent-assembly.com
  legacy_human: agent-assembly.dev
  transactional: mail.agent-assembly.com
transactional_from:
  default: "no-reply@mail.agent-assembly.com"
mail_platform:
  intended_provider: "Google Workspace"
  human_mail_status: planned
  transactional_provider: undecided
  transactional_status: planned
security_policy:
  acknowledgement:
    value: 2
    unit: business_days
  initial_assessment:
    value: 5
    unit: business_days
repos: []
install_channels: []
"""

_VALID_README = """\
# Org profile

<!-- BEGIN GENERATED: repo_table -->
<!-- END GENERATED: repo_table -->

<!-- BEGIN GENERATED: install_channels -->
<!-- END GENERATED: install_channels -->
"""

_VALID_SECURITY_MD = """\
# Security policy

<!-- BEGIN GENERATED: security_contact -->
<!-- END GENERATED: security_contact -->
"""

_VALID_SUPPORT_MD = """\
# Support

<!-- BEGIN GENERATED: support_contacts -->
<!-- END GENERATED: support_contacts -->
"""

_VALID_CODE_OF_CONDUCT_MD = """\
# Code of Conduct

<!-- BEGIN GENERATED: conduct_contact -->
<!-- END GENERATED: conduct_contact -->
"""


def _write_fixture_tree(tmp_path, monkeypatch, *, security_md: str) -> None:
    """Redirect every generator path constant into a tmp_path fixture tree.

    Writes a minimal, valid registry plus valid README/SUPPORT/CODE_OF_CONDUCT
    docs, and the caller-supplied ``security_md`` content — so a single param
    controls just the one thing each test cares about.
    """
    sot_path = tmp_path / "org-profile.yaml"
    sot_path.write_text(_VALID_SOT_YAML, encoding="utf-8")

    readme_path = tmp_path / "README.md"
    readme_path.write_text(_VALID_README, encoding="utf-8")

    security_path = tmp_path / "SECURITY.md"
    security_path.write_text(security_md, encoding="utf-8")

    support_path = tmp_path / "SUPPORT.md"
    support_path.write_text(_VALID_SUPPORT_MD, encoding="utf-8")

    coc_path = tmp_path / "CODE_OF_CONDUCT.md"
    coc_path.write_text(_VALID_CODE_OF_CONDUCT_MD, encoding="utf-8")

    registry_json_path = tmp_path / "registry.json"

    # main()'s "Wrote <path>" messages relative_to() REPO_ROOT, so it must
    # move with the other constants or printing crashes with a ValueError.
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "SOT_PATH", sot_path)
    monkeypatch.setattr(gen, "README_PATH", readme_path)
    monkeypatch.setattr(gen, "SECURITY_PATH", security_path)
    monkeypatch.setattr(gen, "SUPPORT_PATH", support_path)
    monkeypatch.setattr(gen, "CODE_OF_CONDUCT_PATH", coc_path)
    monkeypatch.setattr(gen, "REGISTRY_JSON_PATH", registry_json_path)


def test_check_passes_when_fixture_tree_is_up_to_date(tmp_path, monkeypatch) -> None:
    # Sanity control for the fixture tree itself: with every generated region
    # intact, --check must exit 0 once the artifacts have been generated once.
    _write_fixture_tree(tmp_path, monkeypatch, security_md=_VALID_SECURITY_MD)
    assert gen.main([]) == 0
    assert gen.main(["--check"]) == 0


def test_check_fails_when_security_contact_region_removed(tmp_path, monkeypatch) -> None:
    # AC#4 negative control: remove SECURITY.md's generated region entirely
    # (not just its content — the BEGIN/END sentinels themselves) and prove
    # --check exits non-zero instead of silently passing.
    security_without_generated_region = re.sub(
        r"<!-- BEGIN GENERATED: security_contact -->.*"
        r"<!-- END GENERATED: security_contact -->\n?",
        "",
        _VALID_SECURITY_MD,
        flags=re.DOTALL,
    )
    assert "GENERATED" not in security_without_generated_region

    _write_fixture_tree(
        tmp_path, monkeypatch, security_md=security_without_generated_region
    )
    # replace_bounded() can't find the sentinel at all, so even a plain
    # (non-check) run must fail loudly rather than write a corrupted file.
    with pytest.raises(RuntimeError):
        gen.main([])
    with pytest.raises(RuntimeError):
        gen.main(["--check"])


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
