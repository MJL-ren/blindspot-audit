import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
DEPENDABOT_PATH = REPO_ROOT / ".github" / "dependabot.yml"


class GitHubActionsSecurityTests(unittest.TestCase):
    def test_external_actions_are_pinned_to_full_commit_sha(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        uses = re.findall(r"(?m)^\s*uses:\s*([^\s#]+)(?:\s*#\s*(.+))?$", workflow)

        self.assertTrue(uses)
        for reference, comment in uses:
            with self.subTest(reference=reference):
                self.assertRegex(reference, r"^[^@\s]+@[0-9a-f]{40}$")
                self.assertRegex(comment or "", r"^v\d+\.\d+\.\d+$")
        self.assertNotRegex(workflow, r"(?m)^\s*uses:\s*[^\s]+@v\d+")

    def test_jobs_use_least_privilege_permissions(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

        package = workflow.split("  package-and-script-checks:", 1)[1].split(
            "  publish-release:", 1
        )[0]
        release = workflow.split("  publish-release:", 1)[1]
        self.assertIn("permissions:\n      contents: read", package)
        self.assertNotIn("contents: write", package)
        self.assertIn("permissions:\n      contents: write", release)

    def test_dependabot_tracks_pinned_github_actions(self):
        config = DEPENDABOT_PATH.read_text(encoding="utf-8")

        self.assertIn('package-ecosystem: "github-actions"', config)
        self.assertIn('directory: "/"', config)
        self.assertIn('interval: "weekly"', config)


if __name__ == "__main__":
    unittest.main()
