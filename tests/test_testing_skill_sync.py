import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "skills" / "blindspot-audit"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync-testing-skill.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
IDENTITY_FILES = {Path("SKILL.md"), Path("agents/openai.yaml")}


def content_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
    }


@unittest.skipUnless(POWERSHELL, "PowerShell is required")
class TestingSkillSyncTests(unittest.TestCase):
    def run_sync(self, target: Path):
        return subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(SYNC_SCRIPT),
                "-TargetPath",
                str(target),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_sync_keeps_content_identical_except_testing_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills" / "blindspot-audit-testing"
            completed = self.run_sync(target)
            self.assertEqual(
                completed.returncode,
                0,
                completed.stdout + completed.stderr,
            )

            self.assertEqual(content_files(SOURCE), content_files(target))
            for relative in content_files(SOURCE) - IDENTITY_FILES:
                with self.subTest(file=str(relative)):
                    self.assertEqual(
                        (SOURCE / relative).read_bytes(),
                        (target / relative).read_bytes(),
                    )

            skill = (target / "SKILL.md").read_text(encoding="utf-8")
            interface = (target / "agents" / "openai.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn("name: blindspot-audit-testing", skill)
            self.assertIn("$blindspot-audit-testing", skill)
            self.assertIn('display_name: "Blindspot Audit - Testing"', interface)
            self.assertIn('default_prompt: "Use $blindspot-audit-testing', interface)

    def test_resync_removes_stale_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills" / "blindspot-audit-testing"
            target.mkdir(parents=True)
            stale = target / "stale.txt"
            stale.write_text("stale", encoding="utf-8")

            completed = self.run_sync(target)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertFalse(stale.exists())
            self.assertTrue((target / "SKILL.md").is_file())

    def test_sync_refuses_non_testing_leaf(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills" / "blindspot-audit"
            target.mkdir(parents=True)
            sentinel = target / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")

            completed = self.run_sync(target)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("must end with blindspot-audit-testing", completed.stderr)
            self.assertTrue(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
