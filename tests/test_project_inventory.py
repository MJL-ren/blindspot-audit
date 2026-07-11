import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "blindspot-audit"
    / "scripts"
    / "project_inventory.py"
)

SPEC = importlib.util.spec_from_file_location("blindspot_project_inventory", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
INVENTORY_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INVENTORY_MODULE
SPEC.loader.exec_module(INVENTORY_MODULE)


class ProjectInventoryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("git"), "Git is required for inventory test")
    def test_git_inventory_excludes_ignored_external_repository_without_truncation(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            self.run_git(project, "init", "-q")
            (project / ".gitignore").write_text("external-repos/\n", encoding="utf-8")
            (project / "README.md").write_text("# Fixture\n", encoding="utf-8")
            copied = project / "external-repos" / "large-clone"
            copied.mkdir(parents=True)
            for index in range(30):
                (copied / f"Dockerfile-{index}").write_text(
                    "FROM scratch\n", encoding="utf-8"
                )

            result = INVENTORY_MODULE.build_inventory(project, max_files=5)

        self.assertEqual(result["enumeration_mode"], "git-index-plus-unignored")
        self.assertTrue(result["git_ignored_excluded"])
        self.assertFalse(result["truncated"])
        self.assertEqual(result["file_count_sampled"], 2)
        self.assertNotIn("Docker", result["frameworks"])
        self.assertIn("Git-ignored paths were excluded", result["coverage_note"])

    def test_filesystem_fallback_hard_excludes_both_external_repo_spellings(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            (project / "README.md").write_text("# Fixture\n", encoding="utf-8")
            for directory in ("external-repos", "external_repos"):
                copied = project / directory / "copy"
                copied.mkdir(parents=True)
                (copied / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")

            result = INVENTORY_MODULE.build_inventory(project, max_files=5)

        self.assertEqual(result["enumeration_mode"], "filesystem-fallback")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["file_count_sampled"], 1)
        self.assertNotIn("Docker", result["frameworks"])

    def run_git(self, root: Path, *arguments: str):
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, f"git {' '.join(arguments)} failed")


if __name__ == "__main__":
    unittest.main()
