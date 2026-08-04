#!/usr/bin/env python3
"""Tests for the widened contact/mail/security schema (AAASM-5519).

The schema in metadata/org-profile.yaml publishes PUBLIC identity facts only.
scripts/generate_org_profile.py must (a) parse and VALIDATE it — accepting a
well-formed schema and rejecting malformed / policy-violating input with a
clear, non-zero failure — and (b) project ONLY the public facts into
metadata/generated/registry.json, never a private/internal field, secret, or
private repo name.

These tests pin every one of those guarantees:
  - a valid widened schema parses + validates + projects;
  - several invalid cases each raise SchemaError (bad email, '.dev' primary,
    missing SLA unit, a planted private-looking key);
  - the registry.json projection carries the public contacts and excludes
    anything private;
  - a leakage test proves the generator cannot emit a private repo name, a
    recovery/admin identity, or a secret-shaped literal.

Stdlib `unittest` only, matching the generator's stdlib-only constraint. Run
with `python3 -m unittest discover -s scripts` (or `python3 -m unittest
scripts.test_contact_schema`). No secret-shaped literal is embedded as source;
any token-like fixture is assembled at runtime by concatenation so it cannot
trip push protection.
"""

from __future__ import annotations

import copy
import json
import unittest

import generate_org_profile as gen


def _valid_schema() -> dict:
    """A minimal well-formed widened schema (parsed shape: scalars as strings)."""
    return {
        "schema_version": "1",
        "org": "ai-agent-assembly",
        "product": {"name": "AI Agent Assembly"},
        "contacts": {
            "security": {
                "primary": "security@agent-assembly.com",
                "legacy_aliases": ["security@agent-assembly.dev"],
            },
            "support": {"primary": "support@agent-assembly.com"},
            "maintainers": {
                "primary": "team@agent-assembly.com",
                "legacy_aliases": ["team@agent-assembly.dev"],
            },
        },
        "mail_domains": {
            "human": "agent-assembly.com",
            "legacy_human": "agent-assembly.dev",
            "transactional": "mail.agent-assembly.com",
        },
        "transactional_from": {
            "default": "no-reply@mail.agent-assembly.com",
            "verification": "verify@mail.agent-assembly.com",
        },
        "mail_platform": {
            "intended_provider": "Google Workspace",
            "human_mail_status": "planned",
            "transactional_provider": "undecided",
            "transactional_status": "planned",
        },
        "security_policy": {
            "acknowledgement": {"value": "2", "unit": "business_days"},
            "initial_assessment": {"value": "5", "unit": "business_days"},
        },
    }


class ValidSchemaTest(unittest.TestCase):
    def test_valid_schema_validates(self) -> None:
        # A well-formed widened schema must validate without raising.
        gen.validate_contact_schema(_valid_schema())

    def test_valid_schema_projects_public_facts(self) -> None:
        data = _valid_schema()
        gen.validate_contact_schema(data)
        # add a repos list so render_registry_json has repos to filter.
        data["repos"] = [
            {
                "slug": "agent-assembly",
                "repo": "ai-agent-assembly/agent-assembly",
                "default_branch": "main",
                "role": "core",
                "visibility": "public",
            }
        ]
        proj = json.loads(gen.render_registry_json(data))
        # schema_version and SLA values are real integers in the projection.
        self.assertEqual(proj["schema_version"], 1)
        self.assertIsInstance(proj["schema_version"], int)
        self.assertEqual(proj["security_policy"]["acknowledgement"]["value"], 2)
        self.assertIsInstance(
            proj["security_policy"]["acknowledgement"]["value"], int
        )
        # Public canonical contacts are present.
        self.assertEqual(
            proj["contacts"]["security"]["primary"],
            "security@agent-assembly.com",
        )
        self.assertEqual(
            proj["contacts"]["security"]["legacy_aliases"],
            ["security@agent-assembly.dev"],
        )
        self.assertEqual(proj["mail_domains"]["human"], "agent-assembly.com")
        self.assertEqual(
            proj["transactional_from"]["default"],
            "no-reply@mail.agent-assembly.com",
        )
        # Activation state is published but planned — nothing claimed live.
        self.assertEqual(proj["mail_platform"]["human_mail_status"], "planned")


class InvalidSchemaTest(unittest.TestCase):
    def test_bad_email_rejected(self) -> None:
        data = _valid_schema()
        data["contacts"]["security"]["primary"] = "not-an-email"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_dev_as_primary_rejected(self) -> None:
        # A '.dev' address may only appear under legacy_aliases, never primary.
        data = _valid_schema()
        data["contacts"]["security"]["primary"] = "security@agent-assembly.dev"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_missing_sla_unit_rejected(self) -> None:
        data = _valid_schema()
        del data["security_policy"]["acknowledgement"]["unit"]
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_unknown_sla_unit_rejected(self) -> None:
        data = _valid_schema()
        data["security_policy"]["acknowledgement"]["unit"] = "fortnights"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_missing_schema_version_rejected(self) -> None:
        data = _valid_schema()
        del data["schema_version"]
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_duplicate_address_rejected(self) -> None:
        data = _valid_schema()
        # Reuse the security primary as the support primary — not unique.
        data["contacts"]["support"]["primary"] = "security@agent-assembly.com"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_transactional_from_off_domain_rejected(self) -> None:
        data = _valid_schema()
        # A transactional From on the human domain, not the transactional one.
        data["transactional_from"]["default"] = "no-reply@agent-assembly.com"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_planted_private_key_rejected(self) -> None:
        # A key that looks like private/operational data must abort generation.
        data = _valid_schema()
        data["contacts"]["security"]["recovery_email"] = (
            "someone@example.com"
        )
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_planted_admin_identity_value_rejected(self) -> None:
        data = _valid_schema()
        data["contacts"]["support"]["primary"] = "admin@agent-assembly.com"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_planted_phone_number_rejected(self) -> None:
        data = _valid_schema()
        data["mail_platform"]["contact_phone"] = "+1 (555) 867-5309"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)


class LeakageTest(unittest.TestCase):
    """Prove the public generator cannot emit private repos / secrets."""

    def test_private_repo_excluded_from_projection(self) -> None:
        data = _valid_schema()
        data["repos"] = [
            {
                "slug": "agent-assembly",
                "repo": "ai-agent-assembly/agent-assembly",
                "default_branch": "main",
                "role": "core",
                "visibility": "public",
            },
            {
                "slug": "cloud-control-plane",
                "repo": "ai-agent-assembly/cloud-control-plane",
                "default_branch": "main",
                "role": "private control plane",
                "visibility": "private",
            },
        ]
        rendered = gen.render_registry_json(data)
        # The private repo's slug must not appear anywhere in the JSON bytes.
        self.assertNotIn("cloud-control-plane", rendered)
        proj = json.loads(rendered)
        self.assertEqual([r["slug"] for r in proj["repos"]], ["agent-assembly"])

    def test_secret_shaped_value_rejected(self) -> None:
        # Construct a token-like literal at runtime so no secret-shaped string
        # is committed as source (avoids tripping push protection).
        fake_token = "AKIA" + ("A1B2C3D4" * 6)  # >= 40 base64-ish chars
        data = _valid_schema()
        data["mail_platform"]["smtp_credential"] = fake_token
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_dkim_private_material_rejected(self) -> None:
        pem = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
        data = _valid_schema()
        data["mail_platform"]["dkim"] = pem
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)

    def test_recovery_key_name_rejected(self) -> None:
        data = _valid_schema()
        data["mail_platform"]["recovery_contact"] = "someone@example.com"
        with self.assertRaises(gen.SchemaError):
            gen.validate_contact_schema(data)


class ContactBlockRenderTest(unittest.TestCase):
    """Render tests for the AAASM-5520 governance-doc contact/SLA blocks."""

    def test_security_block_publishes_com_primary(self) -> None:
        block = gen.render_security_contact_block(_valid_schema())
        self.assertIn("security@agent-assembly.com", block)
        # Structured SLAs render as human text.
        self.assertIn("Within 2 business days", block)
        self.assertIn("Within 5 business days", block)

    def test_security_block_labels_dev_as_legacy_and_not_live(self) -> None:
        block = gen.render_security_contact_block(_valid_schema())
        # The .dev alias is present but explicitly labeled legacy compatibility,
        # and the block must NOT claim the .com mailbox is live-sending.
        self.assertIn("security@agent-assembly.dev", block)
        self.assertIn("legacy compatibility alias", block)
        self.assertIn("Cloudflare Email Routing", block)
        self.assertIn("not yet live-sending", block)

    def test_support_block_uses_com_addresses(self) -> None:
        block = gen.render_support_contacts_block(_valid_schema())
        self.assertIn("support@agent-assembly.com", block)
        self.assertIn("security@agent-assembly.com", block)
        # Support is .com-only — no legacy .dev alias leaks into support prose.
        self.assertNotIn("support@agent-assembly.dev", block)

    def test_sla_singular_pluralization(self) -> None:
        data = _valid_schema()
        data["security_policy"]["acknowledgement"] = {
            "value": "1",
            "unit": "business_days",
        }
        block = gen.render_security_contact_block(data)
        self.assertIn("Within 1 business day", block)
        self.assertNotIn("Within 1 business days", block)


if __name__ == "__main__":
    unittest.main()
