import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SAFETY_SCRIPT = REPO_ROOT / "scripts" / "install-safety.ps1"
INSTALLERS = (
    "install-codex.ps1",
    "install-claude-user.ps1",
    "install-claude-project.ps1",
)
POWERSHELLS = tuple(
    dict.fromkeys(
        value
        for value in (shutil.which("pwsh"), shutil.which("powershell"))
        if value
    )
)


def ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(POWERSHELLS, "PowerShell is required")
class PowerShellInstallSafetyTests(unittest.TestCase):
    def run_ps(self, command: str, executable: str | None = None):
        shell = executable or POWERSHELLS[0]
        return subprocess.run(
            [shell, "-NoProfile", "-NonInteractive", "-Command", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def run_script(
        self,
        script: Path,
        parameter: str,
        value: Path,
        executable: str | None = None,
    ):
        shell = executable or POWERSHELLS[0]
        return subprocess.run(
            [
                shell,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(script),
                parameter,
                str(value),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def create_directory_link(
        self,
        link: Path,
        target: Path,
        executable: str | None = None,
    ):
        item_type = (
            "Junction"
            if os.name == "nt"
            else "SymbolicLink"
        )
        completed = self.run_ps(
            f"New-Item -ItemType {item_type} -Path {ps_quote(link)} "
            f"-Target {ps_quote(target)} -ErrorAction Stop | Out-Null",
            executable,
        )
        if completed.returncode != 0:
            self.skipTest(f"Could not create a test reparse point: {completed.stderr}")

    def remove_directory_link(self, link: Path, executable: str | None = None):
        if not link.exists() and not link.is_symlink():
            return
        if os.name == "nt":
            command = f"[System.IO.Directory]::Delete({ps_quote(link)}, $false)"
        else:
            command = (
                f"Remove-Item -LiteralPath {ps_quote(link)} -Force -ErrorAction Stop"
            )
        completed = self.run_ps(command, executable)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def call_remove_guard(
        self,
        destination: Path,
        executable: str | None = None,
    ):
        return self.run_ps(
            f". {ps_quote(SAFETY_SCRIPT)}; "
            f"Remove-BlindspotInstallSafely -Destination {ps_quote(destination)}",
            executable,
        )

    def test_all_powershell_installers_use_the_shared_guard(self):
        for filename in INSTALLERS:
            with self.subTest(installer=filename):
                text = (REPO_ROOT / "scripts" / filename).read_text(encoding="utf-8")
                self.assertIn('install-safety.ps1', text)
                self.assertIn("Remove-BlindspotInstallSafely", text)
                self.assertNotIn("Remove-Item -LiteralPath $resolved -Recurse", text)

    def test_guard_deletes_only_normal_direct_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            installed = destination / "blindspot-audit"
            installed.mkdir(parents=True)
            (installed / "stale.txt").write_text("stale", encoding="utf-8")

            completed = self.call_remove_guard(destination)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(installed.exists())
            self.assertTrue(destination.exists())

    def test_all_installers_replace_normal_temp_copies(self):
        cases = (
            ("install-codex.ps1", "-Destination", Path("skills")),
            ("install-claude-user.ps1", "-Destination", Path("skills")),
            (
                "install-claude-project.ps1",
                "-ProjectRoot",
                Path("project"),
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, (filename, parameter, relative_target) in enumerate(cases):
                with self.subTest(installer=filename):
                    target = root / f"case-{index}" / relative_target
                    if parameter == "-ProjectRoot":
                        installed = target / ".claude" / "skills" / "blindspot-audit"
                    else:
                        installed = target / "blindspot-audit"
                    installed.mkdir(parents=True)
                    stale = installed / "stale.txt"
                    stale.write_text("stale", encoding="utf-8")

                    completed = self.run_script(
                        REPO_ROOT / "scripts" / filename,
                        parameter,
                        target,
                    )

                    self.assertEqual(
                        completed.returncode,
                        0,
                        completed.stdout + completed.stderr,
                    )
                    self.assertFalse(stale.exists())
                    self.assertTrue((installed / "SKILL.md").is_file())

    def test_guard_refuses_root_reparse_point_and_preserves_outside_sentinel(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "skills"
            outside = root / "outside"
            destination.mkdir()
            outside.mkdir()
            sentinel = outside / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            installed = destination / "blindspot-audit"
            self.create_directory_link(installed, outside)
            try:
                completed = self.call_remove_guard(destination)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("reparse-point install path", completed.stderr)
                self.assertTrue(sentinel.exists())
            finally:
                self.remove_directory_link(installed)

    def test_guard_refuses_nested_reparse_point_and_preserves_outside_sentinel(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "skills"
            installed = destination / "blindspot-audit"
            outside = root / "outside"
            installed.mkdir(parents=True)
            outside.mkdir()
            sentinel = outside / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            link = installed / "linked-cache"
            self.create_directory_link(link, outside)
            try:
                completed = self.call_remove_guard(destination)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("recurse through reparse point", completed.stderr)
                self.assertTrue(sentinel.exists())
                self.assertTrue(installed.exists())
            finally:
                self.remove_directory_link(link)

    def test_root_reparse_guard_on_every_available_powershell(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, executable in enumerate(POWERSHELLS):
                with self.subTest(powershell=executable):
                    destination = root / f"skills-{index}"
                    outside = root / f"outside-{index}"
                    destination.mkdir()
                    outside.mkdir()
                    sentinel = outside / "sentinel.txt"
                    sentinel.write_text("keep", encoding="utf-8")
                    installed = destination / "blindspot-audit"
                    self.create_directory_link(installed, outside, executable)
                    try:
                        completed = self.call_remove_guard(destination, executable)
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertIn("reparse-point install path", completed.stderr)
                        self.assertTrue(sentinel.exists())
                    finally:
                        self.remove_directory_link(installed, executable)


if __name__ == "__main__":
    unittest.main()
