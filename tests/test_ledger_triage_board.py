import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "skills" / "blindspot-audit" / "scripts" / "ledger_triage_board.py"

spec = importlib.util.spec_from_file_location("ledger_triage_board", HELPER_PATH)
ledger_triage_board = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ledger_triage_board)


class LedgerTriageBoardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()
        self.ledger = self.project / "BLINDSPOT_LEDGER.md"
        self.ledger.write_text("# Ledger\n\n| ID | Finding |\n| --- | --- |\n| BS-1 | Test |\n", encoding="utf-8")
        self.data = self.project / "triage-input.json"
        self.data.write_text(json.dumps(self.board_data(), ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def board_data(self):
        return {
            "schema": "blindspot-triage-board.v1",
            "boardId": "ledger-triage-test",
            "language": "ko",
            "groups": [
                {
                    "groupId": "g1",
                    "category": "quick_cleanup",
                    "title": "Cleanup",
                    "plainSummary": "Rows that look easy to close.",
                    "items": [
                        {
                            "ledgerId": "BS-1",
                            "shortTitle": "판매 CTA 설정",
                            "ledgerSummary": "Findings에는 CTA가 AJAX 제출을 쓰지 않고 prefers-reduced-motion을 무시한다는 BS-1이 pending으로 남아 있습니다.",
                            "plainExplanation": "CTA와 AJAX가 무엇인지 모르면 선택이 어렵습니다.",
                            "whyItMatters": "사용자가 사이트에서 어디를 눌러야 하는지 헷갈릴 수 있습니다.",
                            "decisionQuestion": "CTA 방향을 지금 정할까?",
                            "executionKind": "ledger_only",
                            "currentStatus": "pending",
                            "currentAwareness": "미확인",
                            "recommendedAction": "keep_pending",
                            "risk": "low",
                        }
                    ],
                }
            ],
        }

    def create_board(self):
        ledger_triage_board.command_create(
            SimpleNamespace(project_root=self.project, ledger=self.ledger, data=self.data)
        )
        boards = [
            path
            for path in (self.project / ".blindspot-tmp").glob("ledger-triage-*")
            if (path / ledger_triage_board.MARKER_NAME).exists()
        ]
        self.assertEqual(1, len(boards))
        return boards[0]

    def response_payload(self, board_dir, **overrides):
        marker = json.loads((board_dir / ledger_triage_board.MARKER_NAME).read_text(encoding="utf-8"))
        response = {
            "schema": "blindspot-triage-response.v1",
            "boardId": marker["boardId"],
            "ledgerPath": marker["ledgerPath"],
            "ledgerHash": marker["ledgerHash"],
            "completedAt": "2026-07-08T00:00:00Z",
            "decisions": [
                {
                    "ledgerId": "BS-1",
                    "action": "keep_pending",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                }
            ],
        }
        response.update(overrides)
        return response

    def write_response(self, board_dir, path=None, **overrides):
        response = self.response_payload(board_dir, **overrides)
        target = path or (board_dir / ledger_triage_board.RESPONSE_NAME)
        target.write_text(
            json.dumps(response, ensure_ascii=False), encoding="utf-8"
        )
        return target

    def test_create_html_is_self_contained_and_escaped(self):
        board_dir = self.create_board()
        self.assertEqual("*", (self.project / ".blindspot-tmp" / ".gitignore").read_text(encoding="utf-8").strip())
        html = (board_dir / ledger_triage_board.HTML_NAME).read_text(encoding="utf-8").lower()
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("<script src", html)
        self.assertNotIn("<link", html)
        self.assertNotIn("@import", html)
        self.assertNotIn("쉽게 말하면", html)
        self.assertNotIn("recommend:", html)
        self.assertIn("항목의 이해를 위한 설명", html)
        self.assertIn("선택하지 않은 항목", html)
        self.assertIn("다운로드 폴더에 그대로", html)
        self.assertIn("blindspot-triage-response-${safedownloadtoken(data.boardid)}.json", html)
        self.assertIn("ledger-triage-test", html)
        self.assertIn("findings/bs-1/pending", html)
        self.assertNotIn("findings에는", html)
        self.assertIn("주요 안내 버튼", html)
        self.assertIn("미확인", html)
        self.assertIn("선택 후 처리", html)
        self.assertIn("확인 근거 메모가 필요합니다", html)

        board_data = json.loads((board_dir / "board-data.json").read_text(encoding="utf-8"))
        item = board_data["groups"][0]["items"][0]
        self.assertEqual("Findings/BS-1/pending", item["ledgerLocation"])
        self.assertNotIn("Findings에는", item["ledgerSummary"])
        self.assertNotIn("BS-1", item["ledgerSummary"])
        self.assertNotIn("CTA", item["ledgerSummary"])
        self.assertIn("움직임 줄이기 설정", item["ledgerSummary"])
        keep_open = next(entry for entry in item["options"] if entry["action"] == "keep_pending")
        self.assertEqual("", keep_open["status"])
        self.assertEqual("", keep_open["intentDetail"])

    def test_english_board_uses_english_default_options(self):
        english = self.board_data()
        english["language"] = "en"
        self.data.write_text(json.dumps(english, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        board_data = json.loads((board_dir / "board-data.json").read_text(encoding="utf-8"))
        labels = [option["label"] for option in board_data["groups"][0]["items"][0]["options"]]
        self.assertIn("Record the recommendation", labels)
        self.assertIn("Ask for a clearer explanation", labels)

    def test_korean_custom_options_are_owner_facing(self):
        custom = self.board_data()
        custom["groups"][0]["items"][0]["options"] = [
            {
                "action": "accept",
                "label": "보조 CTA 추가 방향",
                "tradeoff": "AJAX 제출과 ARIA 보강을 다음 작업에 둡니다.",
                "recommended": True,
            }
        ]
        self.data.write_text(json.dumps(custom, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        board_data = json.loads((board_dir / "board-data.json").read_text(encoding="utf-8"))
        options = board_data["groups"][0]["items"][0]["options"]
        option = next(entry for entry in options if entry["action"] == "accept")
        self.assertNotIn("CTA", option["label"])
        self.assertNotIn("AJAX", option["tradeoff"])
        self.assertNotIn("ARIA", option["tradeoff"])
        self.assertIn("보조 안내 버튼", option["label"])
        self.assertIn("페이지를 떠나지 않고 문의를 보내는 방식", option["tradeoff"])
        self.assertIn("화면읽기 프로그램용 설명", option["tradeoff"])

    def test_option_id_disambiguates_same_action_options(self):
        custom = self.board_data()
        item = custom["groups"][0]["items"][0]
        item["recommendedAction"] = "accept"
        item["options"] = [
            {
                "optionId": "accept-minimal",
                "action": "accept",
                "label": "최소 고지로 처리",
                "tradeoff": "원장에 최소 처리로 남깁니다.",
                "status": "accepted",
                "intentDetail": "minimal",
            },
            {
                "optionId": "accept-full",
                "action": "accept",
                "label": "전체 작업으로 처리",
                "tradeoff": "원장에 전체 작업으로 남깁니다.",
                "status": "accepted",
                "intentDetail": "full",
                "recommended": True,
            },
        ]
        self.data.write_text(json.dumps(custom, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "optionId": "accept-full",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "full",
                    "note": "",
                }
            ],
        )
        _marker, response = ledger_triage_board.validate_response(board_dir)
        self.assertEqual("accept-full", response["decisions"][0]["optionId"])

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "full",
                    "note": "",
                }
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.validate_response(board_dir)

    def test_create_requires_ledger_summary(self):
        missing = self.board_data()
        missing["groups"][0]["items"][0].pop("ledgerSummary")
        self.data.write_text(json.dumps(missing, ensure_ascii=False), encoding="utf-8")

        with self.assertRaises(SystemExit):
            ledger_triage_board.command_create(
                SimpleNamespace(project_root=self.project, ledger=self.ledger, data=self.data)
            )

    def test_validate_then_cleanup_after_ledger_change(self):
        board_dir = self.create_board()
        self.write_response(board_dir)
        ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))
        self.ledger.write_text(self.ledger.read_text(encoding="utf-8") + "\nApplied decision.\n", encoding="utf-8")
        ledger_triage_board.command_cleanup(SimpleNamespace(board_dir=board_dir, confirm_applied=True))
        self.assertFalse(board_dir.exists())

    def test_validate_failures(self):
        board_dir = self.create_board()
        self.write_response(board_dir, boardId="wrong-board")
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

    def test_validate_can_import_external_response_path(self):
        board_dir = self.create_board()
        external = self.project / "downloaded-response.json"
        self.write_response(board_dir, path=external)
        (board_dir / ledger_triage_board.RESPONSE_NAME).unlink(missing_ok=True)

        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir, response=external))
        output = stream.getvalue()
        self.assertIn("Copied response JSON into board directory", output)
        self.assertTrue((board_dir / ledger_triage_board.RESPONSE_NAME).exists())

    def test_collect_response_chooses_latest_matching_download(self):
        board_dir = self.create_board()
        downloads = self.project / "Downloads"
        downloads.mkdir()
        self.write_response(
            board_dir,
            path=downloads / "blindspot-triage-response.json",
            completedAt="2026-07-08T00:00:00Z",
        )
        self.write_response(
            board_dir,
            path=downloads / "blindspot-triage-response (1).json",
            completedAt="2026-07-08T00:05:00Z",
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "defer",
                    "awareness": "unconfirmed",
                    "status": "deferred",
                    "intentDetail": "",
                    "note": "",
                }
            ],
        )

        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_validate(
                SimpleNamespace(board_dir=board_dir, collect_response=True, response_dir=downloads)
            )
        output = stream.getvalue()
        copied = json.loads((board_dir / ledger_triage_board.RESPONSE_NAME).read_text(encoding="utf-8"))
        self.assertIn("Found 2 matching response JSON files", output)
        self.assertEqual("defer", copied["decisions"][0]["action"])

    def test_status_and_intent_detail_must_match_selected_option(self):
        intent_board = self.board_data()
        item = intent_board["groups"][0]["items"][0]
        item["recommendedAction"] = "accept"
        item["statusIntent"] = "accepted:minimum_privacy_notice"
        self.data.write_text(json.dumps(intent_board, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        board_data = json.loads((board_dir / "board-data.json").read_text(encoding="utf-8"))
        options = board_data["groups"][0]["items"][0]["options"]
        accept_option = next(entry for entry in options if entry["action"] == "accept")
        defer_option = next(entry for entry in options if entry["action"] == "defer")
        pending_option = next(entry for entry in options if entry["action"] == "keep_pending")
        self.assertEqual("accepted", accept_option["status"])
        self.assertEqual("minimum_privacy_notice", accept_option["intentDetail"])
        self.assertEqual("deferred", defer_option["status"])
        self.assertEqual("", defer_option["intentDetail"])
        self.assertEqual("", pending_option["status"])
        self.assertEqual("", pending_option["intentDetail"])

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "minimum_privacy_notice",
                    "note": "",
                }
            ],
        )
        ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "defer",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "minimum_privacy_notice",
                    "note": "",
                }
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "keep_pending",
                    "awareness": "unconfirmed",
                    "statusIntent": "accepted:minimum_privacy_notice",
                    "note": "",
                }
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.write_response(board_dir)
        self.ledger.write_text(self.ledger.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.ledger.write_text("# Ledger\n\n| ID | Finding |\n| --- | --- |\n| BS-1 | Test |\n", encoding="utf-8")
        (board_dir / ledger_triage_board.RESPONSE_NAME).write_text("{bad json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "unknown_action",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                }
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

    def test_cleanup_refuses_without_confirm_or_safe_shape(self):
        board_dir = self.create_board()
        self.write_response(board_dir)
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_cleanup(SimpleNamespace(board_dir=board_dir, confirm_applied=False))

        unsafe = Path(self.tmp.name) / "ledger-triage-unsafe"
        unsafe.mkdir()
        marker = json.loads((board_dir / ledger_triage_board.MARKER_NAME).read_text(encoding="utf-8"))
        (unsafe / ledger_triage_board.MARKER_NAME).write_text(json.dumps(marker), encoding="utf-8")
        (unsafe / ledger_triage_board.RESPONSE_NAME).write_text(
            (board_dir / ledger_triage_board.RESPONSE_NAME).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_cleanup(SimpleNamespace(board_dir=unsafe, confirm_applied=True))

    def test_missing_marker_and_resolved_candidate_note_required(self):
        missing_marker = self.project / ".blindspot-tmp" / "ledger-triage-missing-marker"
        missing_marker.mkdir(parents=True)
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=missing_marker))

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "resolved_candidate",
                    "awareness": "unconfirmed",
                    "status": "resolved",
                    "intentDetail": "",
                    "note": "",
                }
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

    def test_create_refuses_duplicate_ledger_ids(self):
        duplicate = self.board_data()
        duplicate["groups"][0]["items"].append(dict(duplicate["groups"][0]["items"][0]))
        self.data.write_text(json.dumps(duplicate, ensure_ascii=False), encoding="utf-8")

        with self.assertRaises(SystemExit):
            ledger_triage_board.command_create(
                SimpleNamespace(project_root=self.project, ledger=self.ledger, data=self.data)
            )

    def test_validate_allows_partial_but_rejects_duplicate_decisions(self):
        two_items = self.board_data()
        second = dict(two_items["groups"][0]["items"][0])
        second["ledgerId"] = "BS-2"
        second["shortTitle"] = "Second row"
        second["ledgerSummary"] = "BS-2 is another open ledger row that the owner can leave untouched."
        two_items["groups"][0]["items"].append(second)
        self.data.write_text(json.dumps(two_items, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(board_dir)
        ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "keep_pending",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                },
                {
                    "ledgerId": "BS-1",
                    "action": "defer",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                },
            ],
        )
        with self.assertRaises(SystemExit):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))

    def test_application_review_routes_simple_decisions_directly(self):
        board_dir = self.create_board()
        self.write_response(board_dir)
        _marker, response = ledger_triage_board.validate_response(board_dir)
        review = ledger_triage_board.response_application_review(board_dir, response)
        self.assertEqual("apply_directly", review["workflow"])
        self.assertEqual(["BS-1"], review["buckets"]["ledger_only"])

    def test_application_review_prioritizes_reexplain_over_saved_choices(self):
        two_items = self.board_data()
        second = dict(two_items["groups"][0]["items"][0])
        second["ledgerId"] = "BS-2"
        second["shortTitle"] = "Second row"
        second["ledgerSummary"] = "Findings에는 두 번째 항목이 pending으로 남아 있습니다."
        second["executionKind"] = "implementation_plan"
        two_items["groups"][0]["items"].append(second)
        self.data.write_text(json.dumps(two_items, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                },
                {
                    "ledgerId": "BS-2",
                    "action": "needs_reexplain",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "",
                },
            ],
        )
        _marker, response = ledger_triage_board.validate_response(board_dir)
        review = ledger_triage_board.response_application_review(board_dir, response)
        self.assertEqual("reexplain_first", review["workflow"])
        self.assertEqual(["BS-2"], review["buckets"]["needs_reexplain"])
        self.assertEqual(["BS-1"], review["buckets"]["ledger_only"])

    def test_application_review_requires_temp_plan_for_implementation_accept(self):
        implementation = self.board_data()
        implementation["groups"][0]["items"][0]["executionKind"] = "implementation_plan"
        implementation["groups"][0]["items"][0]["implementationHint"] = "Update the form flow and verification notes."
        implementation["groups"][0]["items"][0]["recommendedAction"] = "accept"
        implementation["groups"][0]["items"][0]["status"] = "accepted"
        implementation["groups"][0]["items"][0]["intentDetail"] = "implementation"
        self.data.write_text(json.dumps(implementation, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "implementation",
                    "note": "",
                }
            ],
        )
        _marker, response = ledger_triage_board.validate_response(board_dir)
        review = ledger_triage_board.response_application_review(board_dir, response)
        self.assertEqual("temporary_plan_required", review["workflow"])
        self.assertEqual(["BS-1"], review["buckets"]["implementation_plan"])

    def test_validate_output_summarizes_notes_for_plan_constraints(self):
        implementation = self.board_data()
        item = implementation["groups"][0]["items"][0]
        item["executionKind"] = "implementation_plan"
        item["recommendedAction"] = "accept"
        item["status"] = "accepted"
        item["intentDetail"] = "implementation"
        self.data.write_text(json.dumps(implementation, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "implementation",
                    "note": "Do not publish provider setup hints in public docs.",
                }
            ],
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir))
        output = stream.getvalue()
        self.assertIn("Selected decisions:", output)
        self.assertIn("action=accept", output)
        self.assertIn("executionKind=implementation_plan", output)
        self.assertIn("Plan/external constraints from owner notes:", output)
        self.assertIn("Do not publish provider setup hints", output)

    def test_board_directory_preserves_readable_project_token(self):
        readable = self.board_data()
        readable["boardId"] = "cardmonster-ledger-triage-01"
        self.data.write_text(json.dumps(readable, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.assertIn("cardmonster-ledger-triage-01", board_dir.name)

    def test_draft_from_ledger_creates_scaffold_json(self):
        self.ledger.write_text(
            "\n".join(
                [
                    "# Ledger",
                    "",
                    "## Findings",
                    "",
                    "| ID | Finding | Priority | Awareness | Status | Next check / owner |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| BS-20260708-01 | GitHub PAT token appeared in an old setup note. | now | unknown_unknown | pending | Check current tree and history. |",
                    "",
                    "## Decision Packet",
                    "",
                    "| ID | Decision | Recommended option | Options | Why it matters | Status |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| DP-20260708-01 | Public launch wording | Use private beta | private beta / public beta | Prevents wrong launch gate closure | pending |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        out = self.project / "triage-draft.json"

        ledger_triage_board.command_draft(
            SimpleNamespace(
                project_root=self.project,
                ledger=self.ledger,
                out=out,
                language="en",
                board_id="cardmonster-draft",
                project_name="",
                title="",
            )
        )

        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(data["draftOnly"])
        item_ids = [
            item["ledgerId"]
            for group in data["groups"]
            for item in group["items"]
        ]
        self.assertIn("BS-20260708-01", item_ids)
        self.assertIn("DP-20260708-01", item_ids)
        secret_item = next(
            item
            for group in data["groups"]
            for item in group["items"]
            if item["ledgerId"] == "BS-20260708-01"
        )
        self.assertEqual("cheap_verification", secret_item["executionKind"])
        self.assertIn("Git history", secret_item["implementationHint"])

    def test_draft_from_korean_ledger_sections_and_headers(self):
        self.ledger.write_text(
            "\n".join(
                [
                    "# 렛저",
                    "",
                    "## 발견 항목",
                    "",
                    "| ID | 항목 | 위험도 | 인지 분류 | 결정 | 후속 제안 |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| BS-20260709-01 | 문의폼 성공 화면이 사이트 안에 없어 사용자가 제출 결과를 놓칠 수 있음 | next | unknown_known | 대기 | 닫아도 됨 |",
                    "",
                    "## 감사 이력",
                    "",
                    "| 날짜 | 호스트 | 모드 | 결과 |",
                    "| --- | --- | --- | --- |",
                    "| 2026-07-09 | Codex | deep | BS-20260709-01 발견 |",
                    "",
                    "## Resolved Archive",
                    "",
                    "| ID | Finding | Awareness | Status |",
                    "| --- | --- | --- | --- |",
                    "| BS-20260709-02 | Already done | unknown_known | resolved |",
                    "",
                    "## 결정 묶음",
                    "",
                    "| ID | 결정 | 추천 | 선택지 | 왜 중요한가 | 상태 |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| DP-20260709-01 | 공개 전 안내 문구 결정 | 비공개 베타 | 비공개 베타 / 공개 베타 | 공개 범위가 흔들리지 않게 함 | 대기 |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        out = self.project / "triage-draft-ko.json"

        ledger_triage_board.command_draft(
            SimpleNamespace(
                project_root=self.project,
                ledger=self.ledger,
                out=out,
                language="ko",
                board_id="korean-draft",
                project_name="",
                title="",
            )
        )

        data = json.loads(out.read_text(encoding="utf-8"))
        item_ids = [
            item["ledgerId"]
            for group in data["groups"]
            for item in group["items"]
        ]
        self.assertIn("BS-20260709-01", item_ids)
        self.assertIn("DP-20260709-01", item_ids)
        self.assertNotIn("BS-20260709-02", item_ids)
        item = next(
            item
            for group in data["groups"]
            for item in group["items"]
            if item["ledgerId"] == "BS-20260709-01"
        )
        self.assertEqual("Findings", item["ledgerSection"])
        self.assertEqual("대기", item["currentStatus"])
        self.assertEqual("unknown_known", item["currentAwareness"])
        self.assertEqual("resolved_candidate", item["recommendedAction"])
        self.assertIn("문의폼 성공 화면", item["ledgerSummary"])
        self.assertIn("문의폼 성공 화면", item["plainExplanation"])
        self.assertIn("닫아도 됨", item["whyItMatters"])

    def test_create_refuses_draft_only_scaffold_without_override(self):
        self.ledger.write_text(
            "\n".join(
                [
                    "# Ledger",
                    "",
                    "## Findings",
                    "",
                    "| ID | Finding | Priority | Awareness | Status | Next check / owner |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| BS-20260708-01 | GitHub PAT token appeared in an old setup note. | now | unknown_unknown | pending | Check current tree and history. |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        out = self.project / "triage-draft.json"
        ledger_triage_board.command_draft(
            SimpleNamespace(
                project_root=self.project,
                ledger=self.ledger,
                out=out,
                language="en",
                board_id="draft-guard",
                project_name="",
                title="",
            )
        )

        with self.assertRaises(SystemExit):
            ledger_triage_board.command_create(
                SimpleNamespace(project_root=self.project, ledger=self.ledger, data=out)
            )

        ledger_triage_board.command_create(
            SimpleNamespace(
                project_root=self.project,
                ledger=self.ledger,
                data=out,
                allow_unreviewed_draft=True,
            )
        )

    def test_secret_detection_ignores_common_non_secret_phrases(self):
        false_positives = [
            "Password reset email copy still needs owner review.",
            "API docs should explain how examples are formatted.",
            "Token budget is tight for long prompt examples.",
        ]
        for text in false_positives:
            with self.subTest(text=text):
                self.assertEqual([], ledger_triage_board.secret_checklist_for_text(text))
                self.assertEqual(
                    ("decision_bundle", "ledger_only"),
                    ledger_triage_board.classify_draft_item("Findings", text, "pending"),
                )

        true_positive = "A GitHub PAT token appeared in an old setup note and may still exist in history."
        self.assertTrue(ledger_triage_board.secret_checklist_for_text(true_positive))
        self.assertEqual(
            ("quick_cleanup", "cheap_verification"),
            ledger_triage_board.classify_draft_item("Findings", true_positive, "pending"),
        )

    def test_validate_write_plan_outputs_secret_checklist(self):
        implementation = self.board_data()
        item = implementation["groups"][0]["items"][0]
        item["ledgerSummary"] = "A GitHub PAT token appeared in a setup note and may still exist in history."
        item["executionKind"] = "implementation_plan"
        item["recommendedAction"] = "accept"
        item["status"] = "accepted"
        item["intentDetail"] = "secret-cleanup"
        self.data.write_text(json.dumps(implementation, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "secret-cleanup",
                    "note": "Do not mark resolved until history is checked.",
                }
            ],
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir, write_plan=True))
        output = stream.getvalue()
        plan = board_dir / ledger_triage_board.PLAN_NAME
        self.assertTrue(plan.exists())
        plan_text = plan.read_text(encoding="utf-8")
        self.assertIn("Secret cleanup checks before closure", output)
        self.assertIn("Git history", plan_text)
        self.assertIn("Do not mark resolved", plan_text)

    def test_write_plan_marks_ledger_only_without_file_todo(self):
        two_items = self.board_data()
        implementation = dict(two_items["groups"][0]["items"][0])
        implementation["ledgerId"] = "BS-2"
        implementation["shortTitle"] = "Implementation row"
        implementation["ledgerSummary"] = "A docs change is needed."
        implementation["executionKind"] = "implementation_plan"
        implementation["implementationHint"] = "Update docs/contact.md."
        implementation["recommendedAction"] = "accept"
        implementation["status"] = "accepted"
        implementation["intentDetail"] = "docs"
        two_items["groups"][0]["items"].append(implementation)
        self.data.write_text(json.dumps(two_items, ensure_ascii=False), encoding="utf-8")

        board_dir = self.create_board()
        self.write_response(
            board_dir,
            decisions=[
                {
                    "ledgerId": "BS-1",
                    "action": "keep_pending",
                    "awareness": "unconfirmed",
                    "status": "",
                    "intentDetail": "",
                    "note": "학습 제외 처리해 놨으니 신경 안 써도 됨",
                },
                {
                    "ledgerId": "BS-2",
                    "action": "accept",
                    "awareness": "unconfirmed",
                    "status": "accepted",
                    "intentDetail": "docs",
                    "note": "",
                },
            ],
        )
        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_validate(SimpleNamespace(board_dir=board_dir, write_plan=True))
        output = stream.getvalue()
        plan_text = (board_dir / ledger_triage_board.PLAN_NAME).read_text(encoding="utf-8")
        self.assertIn("Owner notes that may justify ledger-only closure or deferral:", output)
        self.assertIn("학습 제외 처리", output)
        self.assertIn("BS-1: ledger only; no project file change expected.", plan_text)
        self.assertIn("BS-2: Update docs/contact.md.", plan_text)

    def test_cleanup_prints_audit_log_suggestion(self):
        english = self.board_data()
        english["language"] = "en"
        self.data.write_text(json.dumps(english, ensure_ascii=False), encoding="utf-8")
        board_dir = self.create_board()
        self.write_response(board_dir)

        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_cleanup(SimpleNamespace(board_dir=board_dir, confirm_applied=True))
        output = stream.getvalue()
        self.assertIn("Audit Log suggestion:", output)
        self.assertIn("temp cleanup completed", output)
        self.assertFalse(board_dir.exists())

    def test_cleanup_prints_korean_audit_log_suggestion_for_korean_board(self):
        board_dir = self.create_board()
        self.write_response(board_dir)

        stream = io.StringIO()
        with redirect_stdout(stream):
            ledger_triage_board.command_cleanup(SimpleNamespace(board_dir=board_dir, confirm_applied=True))
        output = stream.getvalue()
        self.assertIn("<호스트>", output)
        self.assertIn("선택 1건", output)
        self.assertIn("임시 선택판 정리 완료", output)


if __name__ == "__main__":
    unittest.main()
