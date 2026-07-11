import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_FILES = (
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh.md",
    "README.es.md",
)


class PublicSecuritySurfaceTests(unittest.TestCase):
    def test_security_document_matches_packaged_helper_boundaries(self):
        security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")

        for helper in (
            "project_inventory.py",
            "secret_presence_scan.py",
            "audit_followup_guard.py",
            "ledger_triage_board.py",
            "safe_output.py",
        ):
            self.assertIn(f"`{helper}`", security)
        self.assertIn("four executable local helpers", security)
        self.assertIn("`127.0.0.1` only", security)
        self.assertIn("junction, symlink, or other reparse point", security)
        self.assertIn("collects no telemetry", security)
        self.assertRegex(security, r"does\s+not grant those permissions")
        self.assertIn("security/advisories/new", security)
        self.assertNotIn("plus one local helper script", security)

    def test_all_readmes_disclose_temp_files_and_loopback_without_permission_claims(self):
        for filename in README_FILES:
            with self.subTest(readme=filename):
                text = (REPO_ROOT / filename).read_text(encoding="utf-8")
                self.assertIn("127.0.0.1", text)
                self.assertIn("SECURITY.md", text)
                self.assertTrue(
                    any(term in text for term in ("temporary", "임시", "一時", "临时", "temporales"))
                )

    def test_public_bug_form_requires_redaction_and_links_private_reporting(self):
        form = (
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"
        ).read_text(encoding="utf-8")

        for term in ("secrets", "tokens", "private paths", "private payloads", "ledger"):
            self.assertIn(term, form)
        self.assertIn("security/advisories/new", form)
        self.assertIn("id: public-redaction", form)
        self.assertRegex(
            form,
            r"(?s)id: public-redaction.*?required: true",
        )


if __name__ == "__main__":
    unittest.main()
