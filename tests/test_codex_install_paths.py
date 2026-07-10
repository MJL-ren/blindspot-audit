import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_FILES = [
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh.md",
    "README.es.md",
]


class CodexInstallPathTests(unittest.TestCase):
    def read(self, relative_path):
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def test_powershell_installer_defaults_to_agents_skills(self):
        script = self.read("scripts/install-codex.ps1")

        self.assertIn('$Destination = Join-Path $HOME ".agents\\skills"', script)
        self.assertIn("Legacy Codex skill copy found", script)
        self.assertIn('Join-Path $HOME ".codex\\skills"', script)
        self.assertNotIn('$Destination = Join-Path $HOME ".codex\\skills"', script)
        self.assertNotIn('$Destination = Join-Path $env:CODEX_HOME "skills"', script)

    def test_bash_installer_defaults_to_agents_skills(self):
        script = self.read("scripts/install-codex.sh")

        self.assertIn('DESTINATION="$HOME/.agents/skills"', script)
        self.assertIn("Legacy Codex skill copy found", script)
        self.assertIn('LEGACY_DESTINATIONS=("$HOME/.codex/skills")', script)
        self.assertNotIn('DESTINATION="$HOME/.codex/skills"', script)
        self.assertNotIn('DESTINATION="$CODEX_HOME/skills"', script)

    def test_readmes_use_current_codex_skill_locations(self):
        legacy_manual_path = re.compile(
            r"(?m)^~/.codex/skills/blindspot-audit\s+#"
        )
        current_project_path = re.compile(
            r"(?m)^<[^>]+>/.agents/skills/blindspot-audit\s+#"
        )

        for relative_path in README_FILES:
            with self.subTest(readme=relative_path):
                readme = self.read(relative_path)
                self.assertIn("~/.agents/skills/blindspot-audit", readme)
                self.assertIsNotNone(current_project_path.search(readme))
                self.assertIn("Codex > Plugins > Installed", readme)
                self.assertIsNone(legacy_manual_path.search(readme))

    def test_agent_instructions_use_current_codex_skill_locations(self):
        instructions = self.read("AGENTS.md")

        self.assertIn("~/.agents/skills/blindspot-audit", instructions)
        self.assertIn("<project>/.agents/skills/blindspot-audit", instructions)
        self.assertNotIn("- Codex: `$CODEX_HOME/skills", instructions)


if __name__ == "__main__":
    unittest.main()
