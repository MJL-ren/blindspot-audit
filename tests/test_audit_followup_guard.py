import json
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
    / "audit_followup_guard.py"
)

FINDING_IDS = [f"BS-20260711-{index:02d}" for index in range(1, 6)]


def ledger_text(
    *,
    confidence_column: bool = False,
    batch_link: str = "",
    evidence_table: bool = False,
    owner_decisions_applied: bool = False,
) -> str:
    confidence_header = " | Confidence" if confidence_column else ""
    confidence_separator = " | ---" if confidence_column else ""
    confidence_value = " | high" if confidence_column else ""
    rows = []
    for index, finding_id in enumerate(FINDING_IDS, start=1):
        awareness = "unknown_unknown" if owner_decisions_applied else "unconfirmed"
        disposition = (
            "deferred" if index <= 4 else "accepted"
        ) if owner_decisions_applied else "pending"
        rows.append(
            f"| {finding_id} | 테스트 항목 {index} | next | {awareness} | "
            f"{disposition} | 확인 필요{confidence_value} |"
        )
    rows_text = "\n".join(rows)
    evidence = """

| 범위 | 상태 |
| --- | --- |
| 저장소 | 확인 완료 |
""" if evidence_table else ""
    return f"""# Blindspot Ledger

## 감사 이력

| 날짜 | 모드 | 메모 |
| --- | --- | --- |
| 2026-07-11 | focus/security | BA-20260711-01; completed with limits |

## 발견 항목

| ID | 내용 | 심각도 | 인지 분류 | 결정 | 후속 제안{confidence_header} |
| --- | --- | --- | --- | --- | ---{confidence_separator} |
{rows_text}

## Audit Evidence

### BA-20260711-01 - focus/security

- Coverage: repository inspected; provider confirmation remains.
{batch_link}
{evidence}
"""


def mixed_response(batch_path: str) -> dict:
    decisions = []
    for finding_id in FINDING_IDS[:4]:
        decisions.append(
            {
                "findingId": finding_id,
                "awareness": "unknown_unknown",
                "disposition": "deferred",
                "reason": "다음 보안 묶음에서 처리",
                "recheckTrigger": "묶음 작업 시작 시",
                "batchId": "security-local-tools-20260711",
                "batchPath": batch_path,
                "nextActionRoute": "agent_work",
                "nextAction": "묶음 문서 순서대로 처리",
            }
        )
    decisions.append(
        {
            "findingId": FINDING_IDS[4],
            "awareness": "unknown_unknown",
            "disposition": "accepted",
            "reason": "provider 연결부터 확인",
            "recheckTrigger": "",
            "batchId": "",
            "batchPath": "",
            "nextActionRoute": "owner_followup",
            "nextAction": "connector 설치, 인증, 현재 호출 가능 여부 확인",
        }
    )
    return {
        "schema": "blindspot-owner-response.v1",
        "auditRunId": "BA-20260711-01",
        "ownerResponseRecorded": True,
        "expectedFindingIds": FINDING_IDS,
        "unmappedReferences": [],
        "decisions": decisions,
        "applicationMap": {
            "idColumn": "ID",
            "awarenessColumn": "인지 분류",
            "dispositionColumn": "결정",
            "awarenessValues": {
                "unknown_unknown": "unknown_unknown"
            },
            "dispositionValues": {
                "deferred": "deferred",
                "accepted": "accepted"
            },
            "destinations": {},
        },
    }


def standard_ledger_text(awareness: str = "unconfirmed", status: str = "pending") -> str:
    return f"""# Blindspot Ledger

## Audit Log

| Date | Scope | Notes |
| --- | --- | --- |
| 2026-07-11 | focus/security | BA-20260711-01; completed with limits |

## Findings

| ID | Finding | Priority | Awareness | Status | Next check / owner |
| --- | --- | --- | --- | --- | --- |
| {FINDING_IDS[0]} | Test item | next | {awareness} | {status} | Check it |

## Resolved Archive
"""


class AuditFollowupGuardTests(unittest.TestCase):
    def run_guard(self, *arguments: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def create_snapshot(self, project: Path, ledger: Path) -> Path:
        completed = self.run_guard(
            "snapshot",
            "--project-root",
            str(project),
            "--ledger",
            str(ledger),
            "--format",
            "json",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return Path(json.loads(completed.stdout)["snapshotPath"])

    def write_response(self, project: Path, value: dict) -> Path:
        path = project / "owner-response.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def write_batch(
        self,
        project: Path,
        *,
        combined_tiers: bool = False,
        check_mentions_repository: bool = False,
    ) -> Path:
        batch = project / "Docs" / "Security_Batch_Local_Tools_2026-07-11.md"
        batch.parent.mkdir(exist_ok=True)
        rows = []
        for index, finding_id in enumerate(FINDING_IDS[:4]):
            tier = "static-only + authorized-dynamic" if combined_tiers else "static-only"
            channel = (
                "repository + owner-provider-confirmation"
                if combined_tiers
                else "repository"
            )
            check = f"확인 {finding_id}"
            if check_mentions_repository and index == 0:
                check = "repository source와 공식 action provenance 대조"
                channel = "official-web-readonly"
            rows.append(f"| {finding_id} | {check} | {tier} | {channel} | pending |")
        batch.write_text(
            """# Security Batch

Visibility: unconfirmed
Detail policy: generalized

## Included Findings

"""
            + "\n".join(f"- {finding_id}" for finding_id in FINDING_IDS[:4])
            + """

## Verification Matrix

| Finding | Check | Verification tier | Evidence channel | Result |
| --- | --- | --- | --- | --- |
"""
            + "\n".join(rows)
            + "\n",
            encoding="utf-8",
        )
        return batch

    def test_mixed_preview_and_validated_batch_flow(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)

            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))
            preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertIn("Ledger edits: none (preview only)", preview.stdout)
            self.assertIn("owner_followup", preview.stdout)
            self.assertIn("security-local-tools-20260711: required", preview.stdout)

            batch = self.write_batch(project)
            ledger.write_text(
                ledger_text(
                    batch_link=f"- Batch: [{batch.name}]({batch_relative})",
                    owner_decisions_applied=True,
                ),
                encoding="utf-8",
            )
            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertIn("Result: VALID", validated.stdout)

            refused = self.run_guard("cleanup", "--snapshot", str(snapshot))
            self.assertNotEqual(refused.returncode, 0)
            cleaned = self.run_guard(
                "cleanup",
                "--snapshot",
                str(snapshot),
                "--confirm-applied",
            )
            self.assertEqual(cleaned.returncode, 0, cleaned.stderr)
            self.assertFalse(snapshot.parent.exists())

    def test_prepare_awareness_uses_standard_guard_without_editing_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(standard_ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            before = ledger.read_bytes()

            prepared = self.run_guard(
                "prepare-awareness",
                "--snapshot",
                str(snapshot),
                "--audit-run",
                "BA-20260711-01",
                "--finding",
                FINDING_IDS[0],
                "--value",
                "unknown_known",
                "--format",
                "json",
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            result = json.loads(prepared.stdout)
            response = Path(result["responsePath"])
            self.assertEqual(ledger.read_bytes(), before)
            self.assertEqual(response.parent, snapshot.parent)
            self.assertEqual(result["ledgerEdits"], "none-preview-only")
            self.assertEqual(
                result["response"]["decisions"][0]["awareness"],
                "unknown_known",
            )
            self.assertNotIn("applicationMap", result["response"])

            ledger.write_text(
                standard_ledger_text(awareness="unknown_known"),
                encoding="utf-8",
            )
            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertIn("unknown_known (applied)", validated.stdout)

    def test_prepare_awareness_requires_exact_custom_adapter(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)

            blocked = self.run_guard(
                "prepare-awareness",
                "--snapshot",
                str(snapshot),
                "--audit-run",
                "BA-20260711-01",
                "--finding",
                FINDING_IDS[0],
                "--value",
                "unknown_known",
                "--format",
                "json",
            )
            self.assertEqual(blocked.returncode, 3)
            blocked_result = json.loads(blocked.stdout)
            self.assertIsNone(blocked_result["responsePath"])
            self.assertIn(
                "non-standard finding schema",
                "\n".join(blocked_result["preview"]["errors"]),
            )

            prepared = self.run_guard(
                "prepare-awareness",
                "--snapshot",
                str(snapshot),
                "--audit-run",
                "BA-20260711-01",
                "--finding",
                FINDING_IDS[0],
                "--value",
                "unknown_known",
                "--id-column",
                "ID",
                "--awareness-column",
                "인지 분류",
                "--disposition-column",
                "결정",
                "--ledger-awareness-value",
                "알고 있었음",
                "--format",
                "json",
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            result = json.loads(prepared.stdout)
            self.assertEqual(
                result["response"]["applicationMap"]["awarenessValues"],
                {"unknown_known": "알고 있었음"},
            )
            self.assertEqual(
                result["preview"]["applicationMappings"][0]["adapter"],
                "explicit",
            )

    def test_prepare_awareness_refuses_partial_adapter_and_external_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(standard_ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)

            partial = self.run_guard(
                "prepare-awareness",
                "--snapshot",
                str(snapshot),
                "--audit-run",
                "BA-20260711-01",
                "--finding",
                FINDING_IDS[0],
                "--value",
                "unknown_known",
                "--id-column",
                "ID",
            )
            self.assertEqual(partial.returncode, 2)
            self.assertIn("requires --id-column", partial.stderr)

            external = self.run_guard(
                "prepare-awareness",
                "--snapshot",
                str(snapshot),
                "--audit-run",
                "BA-20260711-01",
                "--finding",
                FINDING_IDS[0],
                "--value",
                "unknown_known",
                "--out",
                str(project / "owner-response.json"),
            )
            self.assertEqual(external.returncode, 2)
            self.assertIn("inside the snapshot directory", external.stderr)

    def test_final_validation_blocks_unapplied_owner_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))
            batch = self.write_batch(project)
            ledger.write_text(
                ledger_text(batch_link=f"- Batch: [{batch.name}]({batch_relative})"),
                encoding="utf-8",
            )

            blocked = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )

        self.assertEqual(blocked.returncode, 3)
        self.assertIn("awareness was not applied", blocked.stdout)
        self.assertIn("disposition was not applied", blocked.stdout)
        self.assertIn("found 'unconfirmed'", blocked.stdout)
        self.assertIn("found 'pending'", blocked.stdout)

    def test_standard_schema_applies_without_explicit_application_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(standard_ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            response = self.write_response(
                project,
                {
                    "schema": "blindspot-owner-response.v1",
                    "auditRunId": "BA-20260711-01",
                    "ownerResponseRecorded": True,
                    "expectedFindingIds": [FINDING_IDS[0]],
                    "unmappedReferences": [],
                    "decisions": [
                        {
                            "findingId": FINDING_IDS[0],
                            "awareness": "unknown_unknown",
                            "disposition": "deferred",
                            "reason": "Handle later",
                            "recheckTrigger": "Next security batch",
                            "nextActionRoute": "none",
                            "nextAction": "",
                        }
                    ],
                },
            )
            ledger.write_text(
                standard_ledger_text("unknown_unknown", "deferred"),
                encoding="utf-8",
            )

            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )

        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
        self.assertIn("Applied mappings:", validated.stdout)
        self.assertIn("unknown_unknown (applied)", validated.stdout)
        self.assertIn("deferred (applied)", validated.stdout)

    def test_grouped_v2_and_expanded_v1_have_same_decision_preview(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            v1_value = mixed_response(batch_relative)
            v1_path = project / "owner-response-v1.json"
            v1_path.write_text(json.dumps(v1_value), encoding="utf-8")

            grouped = dict(v1_value)
            grouped["schema"] = "blindspot-owner-response.v2"
            grouped["decisions"] = [v1_value["decisions"][-1]]
            group_common = dict(v1_value["decisions"][0])
            group_common.pop("findingId")
            grouped["decisionGroups"] = [
                {"findingIds": FINDING_IDS[:4], **group_common}
            ]
            grouped_path = project / "owner-response-v2.json"
            grouped_path.write_text(json.dumps(grouped), encoding="utf-8")

            v1_preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(v1_path),
                "--format",
                "json",
            )
            v2_preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(grouped_path),
                "--format",
                "json",
            )

            duplicated = dict(grouped)
            duplicated["decisions"] = [
                v1_value["decisions"][0],
                v1_value["decisions"][-1],
            ]
            duplicate_path = project / "owner-response-v2-duplicate.json"
            duplicate_path.write_text(json.dumps(duplicated), encoding="utf-8")
            duplicate_preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(duplicate_path),
            )

        self.assertEqual(v1_preview.returncode, 0, v1_preview.stderr)
        self.assertEqual(v2_preview.returncode, 0, v2_preview.stderr)
        self.assertEqual(
            json.loads(v1_preview.stdout)["decisions"],
            json.loads(v2_preview.stdout)["decisions"],
        )
        self.assertEqual(duplicate_preview.returncode, 3)
        self.assertIn("duplicate decision", duplicate_preview.stdout)

    def test_custom_schema_requires_explicit_application_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            response_value = mixed_response(
                "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            )
            response_value.pop("applicationMap")
            response = self.write_response(project, response_value)

            preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )

        self.assertEqual(preview.returncode, 3)
        self.assertIn("non-standard finding schema", preview.stdout)

    def test_security_batch_scaffold_uses_relative_paths_and_exact_headers(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "Docs" / "BLINDSPOT_LEDGER.md"
            ledger.parent.mkdir()
            ledger.write_text(ledger_text(), encoding="utf-8")
            batch_relative = "Docs/SECURITY_BATCH_PLAN_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))

            scaffolded = self.run_guard(
                "scaffold-security-batch",
                "--project-root",
                str(project),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
                "--visibility",
                "public-safe",
                "--format",
                "json",
            )
            result = json.loads(scaffolded.stdout)
            batch = Path(result["batchPath"])
            content = batch.read_text(encoding="utf-8")

        self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr)
        self.assertIn(
            "| Finding | Check | Verification tier | Evidence channel | Pass condition | Result |",
            content,
        )
        self.assertTrue(all(finding_id in content for finding_id in FINDING_IDS[:4]))
        self.assertIn("Docs/BLINDSPOT_LEDGER.md", content)
        self.assertIn("Docs/SECURITY_BATCH_PLAN_2026-07-11.md", content)
        self.assertNotIn(str(project), content)
        self.assertIn("ledgerBacklinkSuggestion", result)

    def test_public_safe_batch_rejects_local_absolute_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))
            batch = self.write_batch(project)
            batch.write_text(
                batch.read_text(encoding="utf-8")
                + "\n## Next Session Start\n\nContinue in `C:\\Users\\Example\\project`.\n",
                encoding="utf-8",
            )
            ledger.write_text(
                ledger_text(
                    batch_link=f"- Batch: [{batch.name}]({batch_relative})",
                    owner_decisions_applied=True,
                ),
                encoding="utf-8",
            )

            blocked = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )

        self.assertEqual(blocked.returncode, 3)
        self.assertIn("contains local absolute path markers", blocked.stdout)
        self.assertIn("Windows drive path", blocked.stdout)

    def test_schema_drift_is_blocked_without_migration_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)

            ledger.write_text(ledger_text(confidence_column=True), encoding="utf-8")
            blocked = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
            )
            self.assertEqual(blocked.returncode, 3)
            self.assertIn("Kind: schema-only", blocked.stdout)
            self.assertIn("schema change blocked", blocked.stdout)
            self.assertIn("Confidence", blocked.stdout)

            approved = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--allow-schema-change",
            )
            self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
            self.assertIn("approved schema change", approved.stdout)

    def test_new_audit_evidence_table_does_not_count_as_finding_schema_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)

            ledger.write_text(ledger_text(evidence_table=True), encoding="utf-8")
            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertIn("Schema changes: 0", validated.stdout)

    def test_preview_blocks_conflicts_and_incomplete_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            response = {
                "schema": "blindspot-owner-response.v1",
                "auditRunId": "BA-20260711-01",
                "ownerResponseRecorded": True,
                "expectedFindingIds": FINDING_IDS,
                "unmappedReferences": ["7"],
                "decisions": [
                    {
                        "findingId": FINDING_IDS[0],
                        "awareness": "unknown_known",
                        "disposition": "deliberate_skip",
                        "reason": "의도적으로 생략",
                        "recheckTrigger": "",
                        "nextActionRoute": "owner_followup",
                        "nextAction": "",
                    },
                    {
                        "findingId": FINDING_IDS[0],
                        "awareness": "unknown_unknown",
                        "disposition": "deferred",
                    },
                    {
                        "findingId": "BS-20260711-99",
                        "awareness": "unknown_unknown",
                        "disposition": "accepted",
                    },
                ],
            }
            response_path = self.write_response(project, response)
            preview = self.run_guard(
                "preview",
                "--ledger",
                str(ledger),
                "--data",
                str(response_path),
            )
        self.assertEqual(preview.returncode, 3)
        self.assertIn("unmappedReferences", preview.stdout)
        self.assertIn("duplicate decision", preview.stdout)
        self.assertIn("deliberate_skip requires reason and recheckTrigger", preview.stdout)
        self.assertIn("owner_followup requires nextAction", preview.stdout)
        self.assertIn("not in expectedFindingIds", preview.stdout)

    def test_batch_validation_rejects_combined_tiers_and_channels(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))
            batch = self.write_batch(project, combined_tiers=True)
            ledger.write_text(
                ledger_text(
                    batch_link=f"- Batch: [{batch.name}]({batch_relative})",
                    owner_decisions_applied=True,
                ),
                encoding="utf-8",
            )

            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )
        self.assertEqual(validated.returncode, 3)
        self.assertIn("exactly one tier", validated.stdout)
        self.assertIn("exactly one evidence channel", validated.stdout)

    def test_batch_validation_reads_only_canonical_tier_and_channel_cells(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            ledger = project / "BLINDSPOT_LEDGER.md"
            ledger.write_text(ledger_text(), encoding="utf-8")
            snapshot = self.create_snapshot(project, ledger)
            batch_relative = "Docs/Security_Batch_Local_Tools_2026-07-11.md"
            response = self.write_response(project, mixed_response(batch_relative))
            batch = self.write_batch(project, check_mentions_repository=True)
            ledger.write_text(
                ledger_text(
                    batch_link=f"- Batch: [{batch.name}]({batch_relative})",
                    owner_decisions_applied=True,
                ),
                encoding="utf-8",
            )

            validated = self.run_guard(
                "validate",
                "--snapshot",
                str(snapshot),
                "--ledger",
                str(ledger),
                "--data",
                str(response),
            )
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
        self.assertIn("Result: VALID", validated.stdout)


if __name__ == "__main__":
    unittest.main()
