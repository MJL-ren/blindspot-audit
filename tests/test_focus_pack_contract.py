import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "blindspot-audit"
PACKS_ROOT = SKILL_ROOT / "references" / "packs"
REGISTRY_PATH = PACKS_ROOT / "index.md"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
AUDIT_WORKFLOW_PATH = SKILL_ROOT / "references" / "audit-workflow.md"
SECURITY_PACK_PATH = PACKS_ROOT / "security.md"
SECURITY_FIXTURE = REPO_ROOT / "evals" / "fixtures" / "security-boundary-gap"
SECURITY_EXPECTED_PATH = SECURITY_FIXTURE / "EXPECTED.md"
REPORT_TEMPLATE_PATH = SKILL_ROOT / "references" / "report-template.md"
HOST_SURFACES_PATH = SKILL_ROOT / "references" / "host-surfaces.md"
LEDGER_LIFECYCLE_PATH = SKILL_ROOT / "references" / "ledger-lifecycle.md"
LEDGER_TRIAGE_PATH = SKILL_ROOT / "references" / "ledger-triage.md"
LEDGER_TEMPLATE_PATH = SKILL_ROOT / "templates" / "BLINDSPOT_LEDGER.md"
SECURITY_BATCH_TEMPLATE_PATH = SKILL_ROOT / "templates" / "SECURITY_BATCH_PLAN.md"
SECRET_PRESENCE_SCRIPT_PATH = SKILL_ROOT / "scripts" / "secret_presence_scan.py"
AUDIT_FOLLOWUP_GUARD_PATH = SKILL_ROOT / "scripts" / "audit_followup_guard.py"
SAFE_OUTPUT_PATH = SKILL_ROOT / "scripts" / "safe_output.py"
PROJECT_INVENTORY_PATH = SKILL_ROOT / "scripts" / "project_inventory.py"
LEDGER_TRIAGE_BOARD_PATH = SKILL_ROOT / "scripts" / "ledger_triage_board.py"
LEDGER_TRIAGE_EXPECTED_PATH = (
    REPO_ROOT / "evals" / "fixtures" / "ledger-triage-large-ledger" / "EXPECTED.md"
)
README_FILES = [
    "README.md",
    "README.ko.md",
    "README.ja.md",
    "README.zh.md",
    "README.es.md",
]

REGISTRY_ROW = re.compile(
    r"^\| `(?P<focus_id>[a-z0-9]+(?:-[a-z0-9]+)*)` "
    r"\| `(?P<filename>[^`]+\.md)` \|",
    re.MULTILINE,
)

REQUIRED_HEADINGS = [
    "## Activation And Applicability",
    "## Identity Guard",
    "## Surface Map",
    "## Probe Sets",
    "## Boundaries And Stage Fit",
    "## Peer And Current Anchors",
    "## Cheapest Next Checks",
    "## Reporting And Coverage",
]


class FocusPackContractTests(unittest.TestCase):
    def registry_entries(self):
        registry = REGISTRY_PATH.read_text(encoding="utf-8")
        return [match.groupdict() for match in REGISTRY_ROW.finditer(registry)]

    def test_registry_and_pack_directory_match(self):
        entries = self.registry_entries()
        self.assertTrue(entries, "focus-pack registry must contain at least one pack")

        focus_ids = [entry["focus_id"] for entry in entries]
        filenames = [entry["filename"] for entry in entries]
        self.assertEqual(len(focus_ids), len(set(focus_ids)), "duplicate Focus ID")
        self.assertEqual(len(filenames), len(set(filenames)), "duplicate pack filename")

        for entry in entries:
            self.assertEqual(entry["filename"], f'{entry["focus_id"]}.md')

        registered = set(filenames)
        present = {path.name for path in PACKS_ROOT.glob("*.md") if path.name != "index.md"}
        self.assertEqual(registered, present)

    def test_registered_packs_follow_required_contract(self):
        for entry in self.registry_entries():
            with self.subTest(focus_id=entry["focus_id"]):
                path = PACKS_ROOT / entry["filename"]
                text = path.read_text(encoding="utf-8")

                self.assertIn(f'Focus ID: `{entry["focus_id"]}`', text)
                self.assertIn(f'Scope label: `focus/{entry["focus_id"]}`', text)

                positions = []
                for heading in REQUIRED_HEADINGS:
                    self.assertEqual(
                        text.count(heading),
                        1,
                        f"{path.name} must contain exactly one {heading!r}",
                    )
                    positions.append(text.index(heading))
                self.assertEqual(positions, sorted(positions), "required headings are out of order")

    def test_mode_router_uses_registry_before_pack_loading(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        first_hundred_lines = "\n".join(skill.splitlines()[:100])

        self.assertIn("`focus: <domain>`", first_hundred_lines)
        self.assertIn("`references/packs/index.md`", first_hundred_lines)
        self.assertIn("exactly one matching pack", first_hundred_lines)
        self.assertIn("`references/audit-workflow.md`", first_hundred_lines)
        self.assertIn("`references/ledger-triage.md`", first_hundred_lines)
        self.assertIn("## Existing Ledger Write Guard", skill)
        self.assertIn("audit_followup_guard.py", skill)

    def test_entrypoint_stays_bounded_and_routes_detailed_workflow(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        workflow = AUDIT_WORKFLOW_PATH.read_text(encoding="utf-8")

        self.assertLess(len(skill.splitlines()), 500)
        self.assertLess(len(skill.split()), 5000)
        self.assertIn("## Mode Router", skill)
        self.assertIn("## Reference Router", skill)
        self.assertIn("## Inventory And Search Hygiene", workflow)
        self.assertIn("## 8. Report And Close Out", workflow)

    def test_scoped_focus_does_not_clear_project_wide_coverage(self):
        workflow = AUDIT_WORKFLOW_PATH.read_text(encoding="utf-8")
        registry = REGISTRY_PATH.read_text(encoding="utf-8")

        self.assertIn("is partial pack coverage", workflow)
        self.assertIn("do not clear project-wide pack debt", workflow)
        self.assertIn("does not clear project-wide debt", registry)
        self.assertIn("pack ux-ui: partial", registry)

    def test_security_pack_preserves_defensive_safety_boundaries(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertIn("Never echo a secret value", security)
        self.assertIn("Do not test whether a token is\nlive", security)
        self.assertIn("current repository tree", security)
        self.assertIn("Git history and prior artifacts", security)
        self.assertIn("provider-side credential is revoked/rotated", security)
        self.assertIn("Do not construct or run an exploit", security)
        self.assertIn("`static-only`", security)
        self.assertIn("`ephemeral-local`", security)
        self.assertIn("`authorized-dynamic`", security)
        self.assertIn("A general `focus: security` request alone is not that", security)
        self.assertIn("`TestClient` with a dummy secret", security)
        self.assertIn("`TemporaryDirectory`", security)
        self.assertIn("Build this internal matrix", security)
        self.assertIn("`completed with limits`", security)
        self.assertIn("`owner-confirm-needed`", security)
        self.assertIn("Merge candidates into one finding only when ALL three match", security)
        self.assertIn("zero-signal official scan", security)
        self.assertIn("`verified controls:", security)
        self.assertEqual(len(re.findall(r"^### [1-8]\. ", security, re.MULTILINE)), 8)

    def test_security_pack_separates_evidence_and_required_working_tables(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertIn("### Evidence Channels", security)
        self.assertIn("`official-web-readonly`", security)
        self.assertIn("project verification tier may remain `static-only`", security)
        self.assertIn("Never put a credential", security)
        self.assertIn("### Security-Critical Dependency Matrix", security)
        self.assertIn("Lock evidence + exact version", security)
        self.assertIn("### Product Lineage Matrix", security)
        self.assertIn("shipping / maintained snapshot / upstream / retire candidate", security)
        self.assertIn("### Executable Distribution Matrix", security)
        self.assertIn(
            "owner-only / team-shared / external-testers / public-distribution",
            security,
        )
        self.assertIn("### Promise-To-Enforcement Diff", security)
        self.assertIn("Documentation is evidence of intent, not enforcement", security)
        self.assertIn("### Provider Connector State", security)
        for gate in [
            "Presence",
            "Authentication",
            "Callability",
            "Granted scope",
            "Operation consent",
        ]:
            self.assertIn(f"| {gate} |", security)
        self.assertIn("Do not make a speculative provider", security)
        self.assertIn("never imply live\noperation consent", security)

    def test_security_batch_and_two_layer_report_stay_bounded(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")
        report = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        batch = SECURITY_BATCH_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("Use a two-layer owner report", security)
        self.assertIn("without opening the ledger", security)
        self.assertIn("templates/SECURITY_BATCH_PLAN.md", security)
        self.assertIn("## Focus/Security Two-Layer Output", report)
        self.assertIn("two or more findings", report)
        self.assertIn("lightweight security batch handoff", lifecycle)
        self.assertIn("Visibility: unconfirmed", batch)
        self.assertIn("Detail policy: generalized", batch)
        self.assertIn("exactly one check, one verification tier", batch)
        self.assertIn("<one tier only>", batch)
        self.assertNotIn("static-only / ephemeral-local / authorized-dynamic", batch)
        for heading in [
            "## Start Here",
            "## Included Findings",
            "## Execution Order",
            "## Decisions Needed First",
            "## Verification Matrix",
            "## Done When",
            "## Next Session Start",
        ]:
            self.assertIn(heading, batch)
        self.assertNotIn(".blindspot-tmp", batch)

    def test_mixed_owner_response_keeps_followup_out_of_disposition(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        report = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("Apply mixed replies deterministically", report)
        self.assertIn("1-4 to disposition `deferred`", report)
        self.assertIn("5 to\ndisposition `accepted`, route `owner_followup`", report)
        self.assertIn("never as a new\n   disposition enum", report)
        self.assertIn("Interpret global awareness and numbered dispositions", skill)
        self.assertIn("never a disposition", skill)

    def test_ledger_audit_evidence_and_dirty_worktree_contract(self):
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        ledger_template = LEDGER_TEMPLATE_PATH.read_text(encoding="utf-8")
        triage_expected = LEDGER_TRIAGE_EXPECTED_PATH.read_text(encoding="utf-8")

        self.assertIn("## Compact Audit Log And Evidence", lifecycle)
        self.assertIn("BA-YYYYMMDD-01", lifecycle)
        self.assertIn("## Protect Existing Worktree Changes", lifecycle)
        self.assertIn("git status --short", lifecycle)
        self.assertIn("git diff --cached -- <path>", lifecycle)
        self.assertIn("git diff --cached --check -- <ledger>", lifecycle)
        self.assertIn("Existing hunks must\n   remain", lifecycle)
        self.assertIn("stop\nbefore writing", lifecycle)
        self.assertIn("## Audit Evidence", ledger_template)
        self.assertIn("Ledger visibility:", ledger_template)
        self.assertIn("BA-YYYYMMDD-NN", ledger_template)
        self.assertIn("verifies that every prior hunk", triage_expected)

    def test_existing_ledger_followup_guard_is_deterministic(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertTrue(AUDIT_FOLLOWUP_GUARD_PATH.is_file())
        self.assertIn("schema-only validation", skill)
        self.assertIn("## Deterministic Audit Follow-Up Guard", lifecycle)
        for command in [
            "snapshot",
            "prepare-awareness",
            "preview",
            "validate",
            "scaffold-security-batch",
            "cleanup",
        ]:
            self.assertIn(f"audit_followup_guard.py\" {command}", lifecycle)
        self.assertIn("Do NOT use keyword matching", lifecycle)
        self.assertIn("blindspot-owner-response.v1", lifecycle)
        self.assertIn("blindspot-owner-response.v2", lifecycle)
        self.assertIn("applicationMap", lifecycle)
        self.assertIn("mapped ledger", lifecycle)
        self.assertIn("--allow-schema-change", lifecycle)
        self.assertIn("### Owner-Response Completion Gate", security)
        self.assertIn("ledger-only batch section is not a", security)

    def test_no_choice_examples_cover_global_and_partial_owner_replies(self):
        report = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
        host = HOST_SURFACES_PATH.read_text(encoding="utf-8")

        for example in (
            "다 몰랐어",
            "다 알고 있었어",
            "1번과 3번만 알고 있었어",
            "다 몰랐고 다음 보안 정리 때 같이 처리",
        ):
            self.assertIn(example, report)
            self.assertIn(example, host)
        self.assertIn("do not keyword-parse", host)
        self.assertIn("global awareness and numbered dispositions independently", host)

    def test_security_secret_closure_and_locator_partial_contract(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertIn("current-tree=deliberate_skip", security)
        self.assertIn("history-artifact=unconfirmed", security)
        self.assertIn("overall=open", security)
        self.assertIn("--include <relative-path-or-glob>", security)
        self.assertIn("--exclude <relative-path-or-glob>", security)
        self.assertIn("--max-files 5000 --time-budget 8", security)
        self.assertIn("returns `status: partial`", security)
        self.assertIn("`--include-generated`", security)
        self.assertIn("`--include-ignored`", security)
        self.assertIn("external-repos", security)
        self.assertIn("tracked files plus unignored untracked files", security)
        self.assertIn("Do not claim secret closure for a shipped", security)

    def test_security_provider_not_applicable_is_not_unconfirmed(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertIn("provider connector: not-applicable", security)
        self.assertIn("surface is genuinely absent", security)
        self.assertIn("never that it was not\ninspected", security)

    def test_all_console_helpers_share_safe_output_contract(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertTrue(SAFE_OUTPUT_PATH.is_file())
        self.assertIn("C0/C1", security)
        for path in (
            PROJECT_INVENTORY_PATH,
            LEDGER_TRIAGE_BOARD_PATH,
            AUDIT_FOLLOWUP_GUARD_PATH,
            SECRET_PRESENCE_SCRIPT_PATH,
        ):
            with self.subTest(helper=path.name):
                self.assertIn(
                    "from safe_output import safe_display_text",
                    path.read_text(encoding="utf-8"),
                )

    def test_copied_console_helpers_require_and_accept_safe_output_companion(self):
        for helper in (
            PROJECT_INVENTORY_PATH,
            LEDGER_TRIAGE_BOARD_PATH,
            AUDIT_FOLLOWUP_GUARD_PATH,
            SECRET_PRESENCE_SCRIPT_PATH,
        ):
            with self.subTest(helper=helper.name), tempfile.TemporaryDirectory() as temp:
                target = Path(temp) / helper.name
                shutil.copy2(helper, target)
                missing = subprocess.run(
                    [sys.executable, str(target), "--help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertNotEqual(missing.returncode, 0)
                self.assertIn("safe_output.py", missing.stdout + missing.stderr)

                shutil.copy2(SAFE_OUTPUT_PATH, Path(temp) / SAFE_OUTPUT_PATH.name)
                paired = subprocess.run(
                    [sys.executable, str(target), "--help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
                self.assertEqual(
                    paired.returncode,
                    0,
                    paired.stdout + paired.stderr,
                )

    def test_references_do_not_use_retired_entrypoint_names_or_ghost_tools(self):
        reference_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL_ROOT / "references").rglob("*.md")
        )
        for retired in (
            "SKILL.md Ground Rule",
            "SKILL.md Workflow step",
            "SKILL.md Guardrails",
            "SKILL.md fresh-eyes scan",
            "send_user_message",
            "`known_known`",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, reference_text)

    def test_security_pack_routes_secret_search_through_redacted_helper(self):
        security = SECURITY_PACK_PATH.read_text(encoding="utf-8")

        self.assertTrue(SECRET_PRESENCE_SCRIPT_PATH.is_file())
        self.assertIn("scripts/secret_presence_scan.py", security)
        self.assertIn("never\n  matched values or surrounding text", security)
        self.assertIn("manual-heuristic", security)
        self.assertIn("dedicated-scanner", security)

    def test_awareness_and_disposition_are_independent(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        report = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        ledger_template = LEDGER_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "Awareness: unknown_unknown | unknown_known | unconfirmed", report
        )
        self.assertIn(
            "Disposition: pending | accepted | deferred | deliberate_skip | rejected | resolved",
            report,
        )
        self.assertIn("`unknown_unknown + deferred`", skill)
        self.assertIn("Legacy ledgers may have `deliberate_skip`", lifecycle)
        self.assertIn(
            "Record owner awareness as `unknown_unknown`, `unknown_known`, or `unconfirmed`.",
            ledger_template,
        )
        self.assertNotIn(
            "Record owner awareness as `unknown_unknown`, `unknown_known`, `deliberate_skip`",
            ledger_template,
        )

    def test_choice_capability_uses_callable_now(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        hosts = HOST_SURFACES_PATH.read_text(encoding="utf-8")
        triage = LEDGER_TRIAGE_PATH.read_text(encoding="utf-8")

        for state in ["`advertised`", "`callable-now`", "`mode-gated`", "`unavailable`"]:
            self.assertIn(state, hosts)
        self.assertIn("Only `callable-now` makes the current run choice-capable", hosts)
        self.assertIn("Do not\nmake a speculative tool call", hosts)
        self.assertIn("callable now", skill)
        self.assertIn("`callable-now`", triage)
        self.assertIn("mode-gated", triage)
        self.assertIn("at most 4 questions per call", hosts)
        self.assertIn("never 7 questions in one call", triage)

    def test_entrypoint_names_helpers_and_two_snapshot_guard(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        hosts = HOST_SURFACES_PATH.read_text(encoding="utf-8")

        for helper in (
            "project_inventory.py",
            "audit_followup_guard.py",
            "ledger_triage_board.py",
            "secret_presence_scan.py",
            "safe_output.py",
        ):
            self.assertIn(helper, skill)
        self.assertIn("copy the selected helper and `safe_output.py` together", skill)
        self.assertIn("pre-delta snapshot", lifecycle)
        self.assertIn("new owner-response snapshot", lifecycle)
        self.assertIn("cleanup --snapshot \"<pre-delta-snapshot-file>\" --discard", skill)
        self.assertIn("schema-only snapshot;\n   `--discard`", skill)
        self.assertIn("If validation is BLOCKED", skill)
        self.assertIn("`--discard` is accepted", lifecycle)
        self.assertIn("Run `cleanup --discard` only after a VALID", lifecycle)
        self.assertIn("ledger-snapshot.json` **file**", lifecycle)
        self.assertIn("Repeat `--finding`", lifecycle)
        self.assertIn('"dispositionMatchModes": {"deferred": "annotated"}', lifecycle)
        self.assertIn("same-turn sequencing", hosts)
        self.assertIn("file-tool copy is intact", hosts)
        self.assertIn("--response \"<mounted-response-json>\"", hosts)

        triage = LEDGER_TRIAGE_PATH.read_text(encoding="utf-8")
        self.assertIn("Cowork does not mount the owner's Downloads", triage)
        self.assertIn("instead of the default `--collect-response`", triage)

    def test_existing_ledger_adapter_preserves_local_schema(self):
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        expected = LEDGER_TRIAGE_EXPECTED_PATH.read_text(encoding="utf-8")

        self.assertIn("## Existing Ledger Schema Adapter", lifecycle)
        self.assertIn("NOT automatically equivalent to priority", lifecycle)
        self.assertIn("Do not add an awareness column automatically", lifecycle)
        self.assertIn("New columns, mass normalization", lifecycle)
        self.assertIn("Does not add Priority/Confidence/Awareness columns", expected)
        self.assertIn("schema migration remains a separate owner decision", expected)

    def test_security_fixture_grades_followup_and_coverage_contracts(self):
        expected = SECURITY_EXPECTED_PATH.read_text(encoding="utf-8")

        self.assertIn("`TestClient`/temporary-state", expected)
        self.assertIn("`completed with limits`", expected)
        self.assertIn("overall coverage is `partial`", expected)
        self.assertIn("enforcement point, remediation owner/surface, and", expected)
        self.assertIn("every finding becomes awareness `unknown_unknown`", expected)
        self.assertIn("disposition/local status `deferred`", expected)
        self.assertIn("No finding becomes\n`deliberate_skip`", expected)
        self.assertIn("`official-web-readonly`", expected)
        self.assertIn("promise-to-enforcement", expected)
        self.assertIn("lightweight security batch handoff", expected)
        self.assertIn("compact owner-visible table", expected)
        self.assertIn("## Mixed Owner Follow-Up Acceptance", expected)
        self.assertIn("route `owner_followup`", expected)
        self.assertIn("## Durable Ledger Acceptance", expected)
        self.assertIn("one `BA-YYYYMMDD-NN` run ID", expected)
        self.assertIn("preserves every prior hunk", expected)
        self.assertIn("audit_followup_guard.py", expected)
        self.assertIn("schema-only validation", expected)
        self.assertIn("owner-response delta preview", expected)
        self.assertIn("four\n  independent secret-closure", expected)
        self.assertIn(
            "owner-only / team-shared / external-testers / public-distribution",
            expected,
        )
        self.assertIn("`status: partial`", expected)
        self.assertIn("`not-applicable` line", expected)
        self.assertIn("Search-Hygiene generated/reference/vendor paths", expected)
        self.assertIn("exact machine-readable cells", expected)
        self.assertIn("raw terminal/direction controls", expected)

    def test_security_fixture_is_synthetic_and_parseable(self):
        expected_files = {
            ".github/workflows/preview.yml",
            "EXPECTED.md",
            "README.md",
            "app.py",
            "docs/SECURITY_NOTES.md",
            "scripts/release_preview.py",
        }
        present = {
            path.relative_to(SECURITY_FIXTURE).as_posix()
            for path in SECURITY_FIXTURE.rglob("*")
            if path.is_file()
        }
        self.assertEqual(present, expected_files)

        for relative_path in ["app.py", "scripts/release_preview.py"]:
            source = (SECURITY_FIXTURE / relative_path).read_text(encoding="utf-8")
            compile(source, str(SECURITY_FIXTURE / relative_path), "exec")

        notes = (SECURITY_FIXTURE / "docs" / "SECURITY_NOTES.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("credential value is not included in this fixture", notes)

    def test_readme_translations_document_security_focus_and_sources(self):
        for relative_path in README_FILES:
            with self.subTest(readme=relative_path):
                readme = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("## Focus: Security", readme)
                self.assertIn("cloudflare/security-audit-skill", readme)
                self.assertIn("gitleaks/gitleaks", readme)
                self.assertIn("microsoft/agent-governance-toolkit", readme)

    def test_ledger_triage_never_composes_with_focus(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("`ledger-triage`: maintain an existing", skill)
        self.assertIn("`ledger-triage` never composes with\n`focus`", skill)

    def test_repeat_focus_delta_only_and_durability_contracts_are_discoverable(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        workflow = AUDIT_WORKFLOW_PATH.read_text(encoding="utf-8")
        lifecycle = LEDGER_LIFECYCLE_PATH.read_text(encoding="utf-8")
        report = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("the same focus as before", skill)
        self.assertIn(
            "Reuse the most recent registered Focus ID only when exactly one prior focus",
            workflow,
        )
        self.assertIn("do not infer from another project or host", workflow)
        self.assertIn("new or changed only", lifecycle)
        self.assertIn("Never print unchanged finding blocks again", lifecycle)
        self.assertIn("inspect changed files only", lifecycle)
        self.assertIn("Durability: <tracked | owner-approved-local-only", report)
        self.assertIn("unchanged omitted", report)


if __name__ == "__main__":
    unittest.main()
