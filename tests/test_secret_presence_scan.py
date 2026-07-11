import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "blindspot-audit"
    / "scripts"
    / "secret_presence_scan.py"
)

SPEC = importlib.util.spec_from_file_location("blindspot_secret_presence_scan", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
SCAN_MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCAN_MODULE
SPEC.loader.exec_module(SCAN_MODULE)


class SecretPresenceScanTests(unittest.TestCase):
    def run_helper(self, project_root: Path, *arguments: str):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--project-root",
                str(project_root),
                *arguments,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_tree_scan_reports_locations_without_values_or_context(self):
        sentinel = "ghp_" + "A" * 36
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            secret_path = project / f"leak-{sentinel}.env"
            secret_path.write_text(
                f"SERVICE_API_TOKEN={sentinel}\n",
                encoding="utf-8",
            )
            (project / "example.env").write_text(
                "SERVICE_API_TOKEN=${SERVICE_API_TOKEN}\n",
                encoding="utf-8",
            )

            completed = self.run_helper(project, "--format", "json")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn(sentinel, completed.stdout)
        self.assertNotIn(sentinel, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["schema"], "blindspot-secret-presence.v1")
        self.assertTrue(result["valuesSuppressed"])
        candidates = result["scopes"]["currentTree"]["candidates"]
        self.assertGreaterEqual(len(candidates), 2)
        self.assertIn("github-token-shape", {item["category"] for item in candidates})
        self.assertIn(
            "secret-named-assignment", {item["category"] for item in candidates}
        )
        self.assertTrue(any("[REDACTED]" in item["path"] for item in candidates))
        for candidate in candidates:
            self.assertTrue(
                {"value", "match", "snippet", "context"}.isdisjoint(candidate)
            )
        self.assertEqual(
            result["scopes"]["provider"]["status"], "owner-confirm-needed"
        )

    def test_tree_scan_defaults_to_search_hygiene_but_explicit_include_opts_in(self):
        sentinel = "sk-proj-" + "B" * 32
        copied_repo_sentinel = "gho_" + "D" * 32
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            (project / ".blindspot-tmp").mkdir(parents=True)
            (project / "node_modules" / "package").mkdir(parents=True)
            (project / "external_repos" / "maintained-copy").mkdir(parents=True)
            (project / "external-repos" / "ignored-copy").mkdir(parents=True)
            (project / ".blindspot-tmp" / "response.txt").write_text(
                sentinel,
                encoding="utf-8",
            )
            (project / "node_modules" / "package" / "fixture.txt").write_text(
                sentinel,
                encoding="utf-8",
            )
            (project / "external_repos" / "maintained-copy" / "config.env").write_text(
                f"COPY_TOKEN={copied_repo_sentinel}\n",
                encoding="utf-8",
            )
            (project / "external-repos" / "ignored-copy" / "config.env").write_text(
                f"COPY_TOKEN={copied_repo_sentinel}\n",
                encoding="utf-8",
            )
            (project / "README.md").write_text("No credentials here.\n", encoding="utf-8")

            completed = self.run_helper(project, "--format", "json")
            opted_in = self.run_helper(
                project,
                "--include",
                "external_repos/**",
                "--format",
                "json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(opted_in.returncode, 0, opted_in.stderr)
        self.assertNotIn(sentinel, completed.stdout)
        self.assertNotIn(copied_repo_sentinel, completed.stdout)
        result = json.loads(completed.stdout)
        self.assertFalse(result["scopes"]["currentTree"]["candidates"])
        self.assertIn("external-repos", result["excludedDirectories"])
        self.assertIn("external_repos", result["excludedDirectories"])
        self.assertIn("node_modules", result["excludedDirectories"])

        self.assertNotIn(copied_repo_sentinel, opted_in.stdout)
        opted_in_result = json.loads(opted_in.stdout)
        candidates = opted_in_result["scopes"]["currentTree"]["candidates"]
        self.assertTrue(candidates)
        self.assertTrue(
            all(item["path"].startswith("external_repos/") for item in candidates)
        )
        self.assertEqual(
            opted_in_result["filters"]["include"], ["external_repos/**"]
        )

    @unittest.skipUnless(shutil.which("git"), "Git is required for ignored scan test")
    def test_git_tree_scan_does_not_read_ignored_clone_and_can_opt_in_narrowly(self):
        sentinel = "ghp_" + "I" * 32
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            self.run_git(project, "init", "-q")
            (project / ".gitignore").write_text("external-repos/\n", encoding="utf-8")
            (project / "README.md").write_text("No credentials.\n", encoding="utf-8")
            copied = project / "external-repos" / "large-clone"
            copied.mkdir(parents=True)
            for index in range(20):
                (copied / f"secret-{index}.env").write_text(
                    f"TOKEN={sentinel}\n", encoding="utf-8"
                )

            completed = self.run_helper(
                project,
                "--max-files",
                "5",
                "--time-budget",
                "0",
                "--format",
                "json",
            )
            opted_in = self.run_helper(
                project,
                "--include",
                "external-repos/**",
                "--include-ignored",
                "--time-budget",
                "0",
                "--format",
                "json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn(sentinel, completed.stdout)
        result = json.loads(completed.stdout)
        current = result["scopes"]["currentTree"]
        self.assertEqual(current["status"], "scanned")
        self.assertEqual(current["enumerationMode"], "git-index-plus-unignored")
        self.assertEqual(current["gitIgnoredPolicy"], "excluded-not-enumerated")
        self.assertFalse(current["candidates"])

        self.assertEqual(opted_in.returncode, 0, opted_in.stderr)
        self.assertNotIn(sentinel, opted_in.stdout)
        opted_in_result = json.loads(opted_in.stdout)
        opted_in_current = opted_in_result["scopes"]["currentTree"]
        self.assertEqual(opted_in_current["enumerationMode"], "filesystem-explicit-ignored")
        self.assertTrue(opted_in_current["candidates"])
        self.assertTrue(
            all(
                item["path"].startswith("external-repos/")
                for item in opted_in_current["candidates"]
            )
        )

    def test_include_ignored_requires_explicit_include_filter(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            completed = self.run_helper(project, "--include-ignored")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("requires at least one --include", completed.stderr)

    def test_include_exclude_filters_keep_coverage_and_values_suppressed(self):
        keep_secret = "ghp_" + "E" * 32
        excluded_secret = "ghp_" + "F" * 32
        outside_secret = "ghp_" + "G" * 32
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            (project / "Tools" / "skip").mkdir(parents=True)
            (project / "App").mkdir(parents=True)
            (project / "Tools" / "keep.env").write_text(
                f"KEEP_TOKEN={keep_secret}\n", encoding="utf-8"
            )
            (project / "Tools" / "skip" / "ignored.env").write_text(
                f"SKIP_TOKEN={excluded_secret}\n", encoding="utf-8"
            )
            (project / "App" / "outside.env").write_text(
                f"APP_TOKEN={outside_secret}\n", encoding="utf-8"
            )

            completed = self.run_helper(
                project,
                "--include",
                "Tools/**",
                "--exclude",
                "Tools/skip/**",
                "--time-budget",
                "0",
                "--format",
                "json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        for secret in (keep_secret, excluded_secret, outside_secret):
            self.assertNotIn(secret, completed.stdout)
        result = json.loads(completed.stdout)
        candidates = result["scopes"]["currentTree"]["candidates"]
        self.assertTrue(candidates)
        self.assertTrue(all(item["path"] == "Tools/keep.env" for item in candidates))
        self.assertEqual(result["filters"]["include"], ["Tools/**"])
        self.assertEqual(result["filters"]["exclude"], ["Tools/skip/**"])

    def test_max_files_returns_partial_results_instead_of_failing(self):
        sentinels = []
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            for index in range(5):
                secret = "ghp_" + str(index) * 32
                sentinels.append(secret)
                (project / f"secret-{index}.env").write_text(
                    f"TOKEN_{index}={secret}\n", encoding="utf-8"
                )

            completed = self.run_helper(
                project,
                "--max-files",
                "2",
                "--time-budget",
                "0",
                "--format",
                "json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        for secret in sentinels:
            self.assertNotIn(secret, completed.stdout)
        result = json.loads(completed.stdout)
        scope = result["scopes"]["currentTree"]
        self.assertEqual(scope["status"], "partial")
        self.assertEqual(scope["stopReason"], "max-files")
        self.assertEqual(scope["itemsScanned"], 2)
        self.assertTrue(scope["candidates"])
        self.assertTrue(scope["recommendedResumeScope"])

    def test_time_budget_returns_partial_coverage(self):
        sentinel = "ghp_" + "H" * 32
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            (project / "secret.env").write_text(
                f"SERVICE_TOKEN={sentinel}\n", encoding="utf-8"
            )
            with mock.patch.object(
                SCAN_MODULE.time,
                "monotonic",
                side_effect=[0.0, 2.0],
            ):
                result = SCAN_MODULE.build_result(
                    project,
                    scope="tree",
                    max_file_bytes=1_000_000,
                    max_files=100,
                    max_history_blobs=100,
                    time_budget=1.0,
                    includes=[],
                    excludes=[],
                    include_noisy=False,
                )

        serialized = json.dumps(result, ensure_ascii=True)
        self.assertNotIn(sentinel, serialized)
        scope = result["scopes"]["currentTree"]
        self.assertEqual(scope["status"], "partial")
        self.assertEqual(scope["stopReason"], "time-budget")

    def test_hostile_display_controls_are_escaped_without_hiding_normal_unicode(self):
        hostile = "폴더\x1b]8;;https://example.invalid\x07링크\u202e/file.env"

        rendered = SCAN_MODULE._safe_relative_path(hostile)

        self.assertIn("폴더", rendered)
        self.assertIn("\\x1b", rendered)
        self.assertIn("\\x07", rendered)
        self.assertIn("\\u202e", rendered)
        self.assertNotIn("\x1b", rendered)
        self.assertNotIn("\u202e", rendered)

    @unittest.skipUnless(shutil.which("git"), "Git is required for history scan test")
    def test_history_scan_is_separate_and_never_prints_old_value(self):
        sentinel = "github_pat_" + "C" * 40
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            self.run_git(project, "init", "-q")
            self.run_git(project, "config", "user.email", "fixture@example.invalid")
            self.run_git(project, "config", "user.name", "Fixture")

            config = project / "config.env"
            config.write_text(f"SERVICE_TOKEN={sentinel}\n", encoding="utf-8")
            self.run_git(project, "add", "config.env")
            self.run_git(project, "commit", "-q", "-m", "fixture old value")

            config.write_text(
                "SERVICE_TOKEN=${SERVICE_TOKEN}\n",
                encoding="utf-8",
            )
            self.run_git(project, "add", "config.env")
            self.run_git(project, "commit", "-q", "-m", "fixture remove value")

            completed = self.run_helper(
                project,
                "--scope",
                "history",
                "--max-history-blobs",
                "100",
                "--format",
                "json",
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn(sentinel, completed.stdout)
        self.assertNotIn(sentinel, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["scopes"]["currentTree"]["status"], "not-requested")
        history = result["scopes"]["gitHistory"]
        self.assertEqual(history["status"], "scanned")
        self.assertTrue(history["candidates"])
        self.assertTrue(
            all(item["location"] == "git-history" for item in history["candidates"])
        )
        self.assertTrue(all(len(item["objectId"]) == 12 for item in history["candidates"]))
        self.assertIn("values suppressed", result["auditLogNote"])

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
