import importlib.util
import json
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT / "skills" / "blindspot-audit" / "scripts" / "safe_output.py"
)
PROJECT_INVENTORY_PATH = (
    REPO_ROOT / "skills" / "blindspot-audit" / "scripts" / "project_inventory.py"
)
SPEC = importlib.util.spec_from_file_location("blindspot_safe_output", SCRIPT_PATH)
safe_output = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(safe_output)


class SafeOutputTests(unittest.TestCase):
    def test_controls_and_directionality_are_visible_but_normal_unicode_remains(self):
        hostile = (
            "정상 이름"
            "\x00\x07\x1b]8;;https://example.invalid\x07링크\x1b]8;;\x07"
            "\r\n\t\x7f\x85\u202e뒤집기\u2066격리\u2028다음"
        )

        rendered = safe_output.safe_display_text(hostile)

        self.assertIn("정상 이름", rendered)
        for expected in (
            "\\x00",
            "\\x07",
            "\\x1b",
            "\\x0d",
            "\\x0a",
            "\\x09",
            "\\x7f",
            "\\x85",
            "\\u202e",
            "\\u2066",
            "\\u2028",
        ):
            self.assertIn(expected, rendered)
        self.assertFalse(
            any(
                unicodedata.category(character)
                in safe_output.UNSAFE_UNICODE_CATEGORIES
                for character in rendered
            )
        )

    def test_project_inventory_escapes_direction_controls_in_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "프로젝트\u202e숨김"
            project.mkdir()
            (project / "README.md").write_text("fixture\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_INVENTORY_PATH),
                    str(project),
                    "--format",
                    "json",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("\u202e", completed.stdout)
        result = json.loads(completed.stdout)
        self.assertIn("\\u202e", result["root"])


if __name__ == "__main__":
    unittest.main()
