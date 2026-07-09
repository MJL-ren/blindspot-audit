#!/usr/bin/env python3
"""Create and manage temporary ledger-triage HTML decision boards.

The board is a no-choice-host fallback: it collects owner decisions in a
browser and emits a JSON file the agent can validate before applying ledger
edits. It never edits the ledger itself.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import os
import re
import secrets
import shutil
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BOARD_SCHEMA = "blindspot-triage-board.v1"
RESPONSE_SCHEMA = "blindspot-triage-response.v1"
MARKER_SCHEMA = "blindspot-triage-tmp.v1"
MARKER_NAME = "BLINDSPOT_TRIAGE_TMP.json"
HTML_NAME = "ledger-triage-board.html"
RESPONSE_NAME = "blindspot-triage-response.json"
PLAN_NAME = "ledger-triage-application-plan.md"
SERVER_STATE_NAME = "server-state.json"
SERVER_STATE_SCHEMA = "blindspot-triage-server.v1"
LEDGER_SUGGESTIONS_NAME = "ledger-triage-ledger-suggestions.md"
ALLOWED_ACTIONS = {
    "accept",
    "defer",
    "resolved_candidate",
    "reject",
    "keep_pending",
    "needs_reexplain",
}
ALLOWED_AWARENESS = {
    "unknown_unknown",
    "unknown_known",
    "deliberate_skip",
    "unconfirmed",
}
ALLOWED_EXECUTION_KINDS = {
    "ledger_only",
    "cheap_verification",
    "implementation_plan",
    "external_confirmation",
    "owner_followup",
}
ALLOWED_STATUSES = {
    "",
    "pending",
    "accepted",
    "deferred",
    "rejected",
    "resolved",
}
ALLOWED_ITEM_TYPES = {
    "ledger_row",
    "ledger_section",
}
ACTION_DEFAULT_STATUS = {
    "accept": "accepted",
    "defer": "deferred",
    "resolved_candidate": "resolved",
    "reject": "rejected",
    "keep_pending": "",
    "needs_reexplain": "",
}
LOCALIZED_UNCONFIRMED = {"미확인", "未確認", "未确认", "sin confirmar"}
OPEN_LEDGER_STATUSES = {
    "",
    "pending",
    "accepted",
    "deferred",
    "unconfirmed",
    "대기",
    "대기 중",
    "수용됨",
    "보류",
    "보류됨",
    "미확인",
}
SECRET_VALUE_PATTERNS = re.compile(
    r"(ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----|"
    r"xox[baprs]-[A-Za-z0-9-]+)",
    re.IGNORECASE,
)
SECRET_CONTEXT_TERMS = re.compile(
    r"\b(api[ _-]?key|client[ _-]?secret|credential(?:s)?|private[ _-]?key|"
    r"access[ _-]?token|auth[ _-]?token|bearer[ _-]?token|refresh[ _-]?token|"
    r"github[ _-]?token|github[ _-]?pat|personal[ _-]?access[ _-]?token|"
    r"pat[ _-]?token)\b",
    re.IGNORECASE,
)
SECRET_EXPOSURE_TERMS = re.compile(
    r"\b(exposed|leaked|appeared|committed|checked[ _-]?in|history|old[ _-]?commit|"
    r"repo(?:sitory)?|readme|file|note|log|env|rotation|rotate|cleanup)\b",
    re.IGNORECASE,
)


def looks_like_exposed_secret(text: str) -> bool:
    value = str(text or "")
    if SECRET_VALUE_PATTERNS.search(value):
        return True
    if not SECRET_CONTEXT_TERMS.search(value):
        return False
    return bool(SECRET_EXPOSURE_TERMS.search(value))
KO_OWNER_TEXT_REPLACEMENTS = [
    (r"판매\s*CTA", "판매 안내 버튼"),
    (r"보조\s*CTA", "보조 안내 버튼"),
    (r"(?<![A-Za-z])AJAX\s*제출(?![A-Za-z])", "페이지를 떠나지 않고 문의를 보내는 방식"),
    (r"(?<![A-Za-z])CTA(?![A-Za-z])", "주요 안내 버튼"),
    (r"(?<![A-Za-z])AJAX(?![A-Za-z])", "페이지를 떠나지 않고 보내는 방식"),
    (r"(?<![A-Za-z])ARIA(?![A-Za-z])", "화면읽기 프로그램용 설명"),
    (r"focus trap|포커스 트랩", "키보드 초점이 팝업 밖으로 새지 않게 하는 처리"),
    (r"prefers-reduced-motion|reduced-motion", "움직임 줄이기 설정"),
    (r"smooth scroll", "부드럽게 스크롤되는 움직임"),
    (r"(?<![A-Za-z])hover\s*확대", "마우스를 올렸을 때 커지는 효과"),
    (r"(?<![A-Za-z])hover(?![A-Za-z])", "마우스를 올렸을 때 생기는 효과"),
    (r"(?<![A-Za-z])fade(?![A-Za-z])", "서서히 나타나거나 사라지는 효과"),
    (r"카운트업", "숫자가 올라가는 효과"),
    (r"접근성\s*패스", "접근성 점검"),
    (r"UX\s*패스", "사용 흐름 점검"),
    (r"(?<![A-Za-z])CSS(?![A-Za-z])", "CSS(화면 스타일 코드)"),
    (r"동작 줄이기 설정", "움직임 줄이기 설정"),
    (r"\bdry-run\b", "실제로 바꾸기 전 미리보기"),
    (r"Time Travel", "일정 기간 되돌리기 기능"),
    (r"offsite export", "다른 곳에 따로 저장한 백업 파일"),
    (r"wrangler d1 export", "D1 데이터를 내보내는 명령"),
    (r"(?<![A-Za-z0-9])D1(?![A-Za-z0-9])", "D1(주문 데이터를 넣어 둔 데이터베이스)"),
    (r"Formspree", "Formspree(문의폼을 받아주는 외부 서비스)"),
    (r"Resolved Archive", "해결된 항목 보관함"),
    (r"Decision archive", "끝난 결정 보관함"),
    (r"Decision Packet", "결정 묶음"),
    (r"\bFindings\b", "발견 항목"),
    (r"(?<![A-Za-z])accepted/resolved(?![A-Za-z])", "수용됨/해결됨"),
    (r"(?<![A-Za-z])accepted(?![A-Za-z])", "수용됨"),
    (r"(?<![A-Za-z])resolved(?![A-Za-z])", "해결됨"),
    (r"(?<![A-Za-z])pending(?![A-Za-z])", "대기 중"),
    (r"(?<![A-Za-z])archive(?![A-Za-z])", "보관함"),
    (r"(?<![A-Za-z])skip\s*기록", "이번에는 하지 않기로 기록"),
    (r"(?<![A-Za-z])skip(?![A-Za-z])", "이번에는 하지 않기로 표시"),
    (r"(?<![A-Za-z])ledger(?![A-Za-z])", "원장"),
    (r"(?<![A-Za-z])board(?![A-Za-z])", "선택판"),
    (r"(?<![A-Za-z])audit(?![A-Za-z])", "점검"),
    (r"버튼가", "버튼이"),
    (r"버튼는", "버튼은"),
    (r"버튼를", "버튼을"),
]
DEFAULT_OPTIONS = {
    "ko": [
        {
            "action": "accept",
            "label": "추천대로 기록하기",
            "tradeoff": "이 항목을 이 선택판의 추천 방향으로 원장에 기록합니다. 무엇을 하기로 한 것인지 나중에 다시 볼 수 있게 남깁니다.",
        },
        {
            "action": "defer",
            "label": "나중에 다시 보기",
            "tradeoff": "지금 정하지 않습니다. 대신 언제 다시 볼지, 어떤 일이 생기면 다시 볼지 적어 둡니다.",
        },
        {
            "action": "resolved_candidate",
            "label": "이미 해결된 후보로 보기",
            "tradeoff": "이미 끝난 일처럼 보인다는 뜻입니다. 에이전트가 간단한 확인을 한 번 더 한 뒤에만 완료 보관함으로 옮깁니다.",
        },
        {
            "action": "reject",
            "label": "이 프로젝트에는 맞지 않음",
            "tradeoff": "이 항목은 하지 않기로 하거나, 현재 프로젝트에는 해당 없다고 기록합니다. 이유를 남기면 다음 점검이 다시 묻지 않습니다.",
        },
        {
            "action": "keep_pending",
            "label": "그대로 열어 두기",
            "tradeoff": "아직 판단하지 않습니다. 원장의 현재 상태를 그대로 두고 다음에 다시 볼 수 있게 남깁니다.",
        },
        {
            "action": "needs_reexplain",
            "label": "설명을 다시 받기",
            "tradeoff": "무슨 뜻인지 아직 애매하다는 신호입니다. 상태는 바꾸지 않고, 에이전트가 더 쉬운 말로 다시 설명해야 합니다.",
        },
    ],
    "en": [
        {
            "action": "accept",
            "label": "Record the recommendation",
            "tradeoff": "Apply the recommended ledger outcome and leave a clear note about what was accepted.",
        },
        {
            "action": "defer",
            "label": "Decide later",
            "tradeoff": "Do not decide now. Record when or why to revisit this item so it does not disappear.",
        },
        {
            "action": "resolved_candidate",
            "label": "Treat as likely resolved",
            "tradeoff": "This looks finished, but the agent must still do a cheap check before moving it to the archive.",
        },
        {
            "action": "reject",
            "label": "Not for this project",
            "tradeoff": "Record that this item does not apply, or that you intentionally chose not to do it.",
        },
        {
            "action": "keep_pending",
            "label": "Leave it open",
            "tradeoff": "Do not decide yet. Keep the current ledger row open for a future pass.",
        },
        {
            "action": "needs_reexplain",
            "label": "Ask for a clearer explanation",
            "tradeoff": "Do not change the ledger status. The agent should explain the item again in plainer language.",
        },
    ],
    "ja": [
        {
            "action": "accept",
            "label": "推奨どおり記録する",
            "tradeoff": "この項目を推奨された方向で台帳に記録します。あとで何を受け入れたのか分かるように残します。",
        },
        {
            "action": "defer",
            "label": "あとで決める",
            "tradeoff": "今は決めません。いつ、または何が起きたら見直すかを残します。",
        },
        {
            "action": "resolved_candidate",
            "label": "解決済み候補にする",
            "tradeoff": "すでに終わっていそうな項目です。archive に移す前に、エージェントが安い確認をもう一度行います。",
        },
        {
            "action": "reject",
            "label": "このプロジェクトには不要",
            "tradeoff": "この項目は該当しない、またはやらないと記録します。理由を残すと次回また聞かれにくくなります。",
        },
        {
            "action": "keep_pending",
            "label": "開いたままにする",
            "tradeoff": "まだ判断しません。現在の台帳状態を保ちます。",
        },
        {
            "action": "needs_reexplain",
            "label": "説明をもう一度受ける",
            "tradeoff": "意味がまだ分かりにくいという合図です。状態は変えず、もっと簡単な説明を求めます。",
        },
    ],
    "zh": [
        {
            "action": "accept",
            "label": "按推荐记录",
            "tradeoff": "把这个项目按推荐方向写入台账，并留下之后能看懂的记录。",
        },
        {
            "action": "defer",
            "label": "以后再决定",
            "tradeoff": "现在不做决定。记录什么时候或在什么条件下重新查看。",
        },
        {
            "action": "resolved_candidate",
            "label": "作为可能已解决处理",
            "tradeoff": "它看起来已经完成，但 agent 还需要做一次低成本确认，之后才能归档。",
        },
        {
            "action": "reject",
            "label": "不适用于本项目",
            "tradeoff": "记录这个项目不适用，或你明确决定不做。留下原因可避免下次重复提出。",
        },
        {
            "action": "keep_pending",
            "label": "保持未处理",
            "tradeoff": "暂时不判断，保持当前台账状态，之后再看。",
        },
        {
            "action": "needs_reexplain",
            "label": "需要更清楚的解释",
            "tradeoff": "不改变状态。让 agent 用更容易理解的方式重新解释。",
        },
    ],
    "es": [
        {
            "action": "accept",
            "label": "Registrar la recomendación",
            "tradeoff": "Aplica el resultado recomendado en el ledger y deja claro qué se aceptó.",
        },
        {
            "action": "defer",
            "label": "Decidir después",
            "tradeoff": "No decide ahora. Registra cuándo o por qué volver a revisar este punto.",
        },
        {
            "action": "resolved_candidate",
            "label": "Parece resuelto",
            "tradeoff": "Parece terminado, pero el agente debe hacer una verificación barata antes de archivarlo.",
        },
        {
            "action": "reject",
            "label": "No aplica a este proyecto",
            "tradeoff": "Registra que este punto no aplica o que se decidió no hacerlo.",
        },
        {
            "action": "keep_pending",
            "label": "Dejar abierto",
            "tradeoff": "No decide todavía. Mantiene la fila abierta para revisarla después.",
        },
        {
            "action": "needs_reexplain",
            "label": "Pedir una explicación más clara",
            "tradeoff": "No cambia el estado. El agente debe explicarlo de forma más simple.",
        },
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_project_and_ledger(project_root: Path, ledger: Path) -> tuple[Path, Path]:
    root = project_root.resolve()
    ledger_path = ledger if ledger.is_absolute() else root / ledger
    ledger_path = ledger_path.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project root is not a directory: {root}")
    if not ledger_path.exists() or not ledger_path.is_file():
        raise SystemExit(f"Ledger file not found: {ledger_path}")
    if not is_relative_to(ledger_path, root):
        raise SystemExit(f"Ledger must be inside project root: {ledger_path}")
    return root, ledger_path


def default_option_for_action(language: str, action: str) -> dict[str, str]:
    for option in default_options_for_language(language):
        if option["action"] == action:
            return option
    return {"action": action, "label": action, "tradeoff": ""}


def split_legacy_status_intent(value: Any, action: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if not text:
        return "", ""
    if ":" in text:
        possible_status, detail = text.split(":", 1)
        possible_status = possible_status.strip()
        if possible_status in ALLOWED_STATUSES:
            return possible_status, detail.strip()
    if text in ALLOWED_STATUSES:
        return text, ""
    return ACTION_DEFAULT_STATUS.get(action, ""), text


def normalize_status_detail(
    source: dict[str, Any],
    action: str,
    inherited_status: str = "",
    inherited_intent_detail: str = "",
) -> tuple[str, str]:
    status = str(source.get("status") or "").strip()
    intent_detail = str(
        source.get("intentDetail")
        or source.get("decisionNote")
        or source.get("intent")
        or ""
    ).strip()
    if not status and not intent_detail and source.get("statusIntent"):
        status, intent_detail = split_legacy_status_intent(source.get("statusIntent"), action)
    if not status:
        status = inherited_status
    if not intent_detail:
        intent_detail = inherited_intent_detail
    if not status and action not in {"keep_pending", "needs_reexplain"}:
        status = ACTION_DEFAULT_STATUS.get(action, "")
    if action in {"keep_pending", "needs_reexplain"}:
        status = ""
        intent_detail = ""
    if status not in ALLOWED_STATUSES:
        raise SystemExit(f"Unknown status for action {action!r}: {status!r}")
    return status, intent_detail


def normalize_option(
    option: dict[str, Any],
    recommended: str,
    language: str,
    inherited_status: str = "",
    inherited_intent_detail: str = "",
    index: int = 0,
) -> dict[str, Any]:
    action = option.get("action")
    if action not in ALLOWED_ACTIONS:
        raise SystemExit(f"Unknown option action: {action!r}")
    fallback = default_option_for_action(language, str(action))
    if action == recommended:
        status, intent_detail = normalize_status_detail(
            option, str(action), inherited_status, inherited_intent_detail
        )
    else:
        status, intent_detail = normalize_status_detail(option, str(action))
    raw_option_id = str(option.get("optionId") or option.get("id") or "").strip()
    if raw_option_id:
        option_id = safe_path_token(raw_option_id)
    else:
        option_id = safe_path_token(
            "-".join(
                str(part)
                for part in (
                    action,
                    status,
                    intent_detail,
                    option.get("label") or fallback.get("label") or "",
                    index + 1,
                )
                if part
            )
        )
    normalized = {
        "optionId": option_id,
        "action": action,
        "label": owner_facing_text(language, option.get("label") or fallback.get("label") or action),
        "tradeoff": owner_facing_text(
            language,
            option.get("tradeoff")
            or option.get("plainDescription")
            or fallback.get("tradeoff")
            or ""
        ),
        "status": status,
        "intentDetail": intent_detail,
    }
    if option.get("recommended") or action == recommended:
        normalized["recommended"] = True
    return normalized


def safe_path_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value.strip())
    cleaned = cleaned.strip("-_")
    token = (cleaned or secrets.token_hex(4))[:48].strip("-_")
    return token or secrets.token_hex(4)


def normalize_awareness(value: Any) -> str:
    text = str(value or "unconfirmed").strip()
    if text in ALLOWED_AWARENESS:
        return text
    if text in LOCALIZED_UNCONFIRMED:
        return "unconfirmed"
    return "unconfirmed"


def default_execution_kind(category: str) -> str:
    if category == "needs_external_confirmation":
        return "external_confirmation"
    if category == "quick_cleanup":
        return "cheap_verification"
    return "ledger_only"


def normalize_execution_kind(value: Any, category: str) -> str:
    kind = str(value or default_execution_kind(category)).strip()
    if kind not in ALLOWED_EXECUTION_KINDS:
        raise SystemExit(f"Unknown executionKind: {kind!r}")
    return kind


def normalize_item_type(value: Any) -> str:
    item_type = str(value or "ledger_row").strip()
    if item_type not in ALLOWED_ITEM_TYPES:
        raise SystemExit(f"Unknown itemType: {item_type!r}")
    return item_type


def language_key(language: str) -> str:
    text = language.lower()
    if text.startswith("ko"):
        return "ko"
    if text.startswith("ja"):
        return "ja"
    if text.startswith("zh"):
        return "zh"
    if text.startswith("es"):
        return "es"
    return "en"


def default_options_for_language(language: str) -> list[dict[str, str]]:
    return DEFAULT_OPTIONS[language_key(language)]


def owner_facing_text(language: str, value: Any) -> str:
    text = str(value or "").strip()
    if language_key(language) != "ko":
        return text
    for pattern, replacement in KO_OWNER_TEXT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def infer_ledger_section(item: dict[str, Any], ledger_summary: str) -> str:
    section = str(item.get("ledgerSection") or item.get("section") or "").strip()
    if section:
        return section
    summary = ledger_summary.strip()
    for candidate in ("Findings", "Decision Packet", "Resolved Archive", "Skipped For Now"):
        if summary.startswith(candidate):
            return candidate
    if summary.startswith("원장"):
        return "Ledger"
    return "Ledger"


def clean_korean_ledger_summary(summary: str, ledger_id: str, status: str) -> str:
    text = summary.strip()
    status_pattern = re.escape(status.strip()) if status.strip() else r"[^.。]+"
    id_pattern = re.escape(ledger_id)
    wrappers = [
        rf"^(?:Findings|Decision Packet|Resolved Archive|Skipped For Now)(?:에는|에)\s*(?P<body>.+?)\s*{id_pattern}(?:이|가)?\s*(?:{status_pattern})?(?:으로|로)?\s*남아 있습니다\.?\s*(?P<rest>.*)$",
        rf"^원장(?:에는|에)\s*(?P<body>.+?)(?:항목|결정)(?:이|가)?\s*(?:{status_pattern})(?:으로|로)?\s*남아 있습니다\.?\s*(?P<rest>.*)$",
    ]
    for pattern in wrappers:
        match = re.match(pattern, text)
        if not match:
            continue
        body = match.group("body").strip()
        rest = match.groupdict().get("rest", "").strip()
        if body.endswith("하라는"):
            body = body[:-3] + "할지"
        elif body.endswith("다는"):
            body = body[:-1]
        elif body.endswith(("이라는", "라는")):
            body = re.sub(r"(이라는|라는)$", "", body).strip()
        body = re.sub(r"결정하$", "결정", body).strip()
        return f"{body} {rest}".strip()
    return text


def clean_ledger_summary(language: str, summary: str, ledger_id: str, status: str) -> str:
    if language_key(language) == "ko":
        summary = clean_korean_ledger_summary(summary, ledger_id, status)
    return owner_facing_text(language, summary)


def ledger_location(item: dict[str, Any], section: str, ledger_id: str, status: str) -> str:
    explicit = str(item.get("ledgerLocation") or "").strip()
    if explicit:
        return explicit
    parts = [section or "Ledger", ledger_id]
    if status:
        parts.append(status)
    return "/".join(parts)


def secret_checklist_for_text(text: str) -> list[str]:
    if not looks_like_exposed_secret(text):
        return []
    return [
        "Scan the current working tree for the exposed secret or token pattern.",
        "Scan Git history or old commits for the same secret or token pattern.",
        "Leave the row open or blocked if history still contains the secret and rotation/history cleanup is not confirmed.",
    ]


def normalize_board_data(raw: dict[str, Any], root: Path, ledger: Path) -> dict[str, Any]:
    if raw.get("schema") != BOARD_SCHEMA:
        raise SystemExit(f"Board input schema must be {BOARD_SCHEMA!r}")

    board_id = str(raw.get("boardId") or f"board-{secrets.token_hex(4)}")
    language = str(raw.get("language") or "en")
    ledger_hash = sha256_file(ledger)
    groups = raw.get("groups")
    if not isinstance(groups, list) or not groups:
        raise SystemExit("Board input must include a non-empty groups list")

    normalized_groups = []
    item_ids: list[str] = []
    for group in groups:
        if not isinstance(group, dict):
            raise SystemExit("Each group must be an object")
        group_id = str(group.get("groupId") or f"group-{len(normalized_groups) + 1}")
        category = str(group.get("category") or "decision_bundle")
        items = group.get("items")
        if not isinstance(items, list) or not items:
            raise SystemExit(f"Group {group_id!r} must include non-empty items")
        normalized_items = []
        for item in items:
            if not isinstance(item, dict):
                raise SystemExit(f"Group {group_id!r} has a non-object item")
            ledger_id = str(item.get("ledgerId") or "").strip()
            if not ledger_id:
                raise SystemExit(f"Group {group_id!r} has an item without ledgerId")
            if ledger_id in item_ids:
                raise SystemExit(f"Duplicate ledgerId in board input: {ledger_id}")
            recommended = str(item.get("recommendedAction") or "keep_pending")
            if recommended not in ALLOWED_ACTIONS:
                raise SystemExit(f"Item {ledger_id} has unknown recommendedAction: {recommended!r}")
            item_status, item_intent_detail = normalize_status_detail(item, recommended)
            raw_options = item.get("options")
            if not isinstance(raw_options, list) or not raw_options:
                raw_options = default_options_for_language(language)
            options = []
            option_ids: set[str] = set()
            for option_index, option in enumerate(raw_options):
                if not isinstance(option, dict):
                    raise SystemExit(f"Item {ledger_id} has a non-object option")
                normalized_option = normalize_option(
                    option,
                    recommended,
                    language,
                    item_status,
                    item_intent_detail,
                    option_index,
                )
                if normalized_option["optionId"] in option_ids:
                    raise SystemExit(
                        f"Item {ledger_id} has duplicate optionId: {normalized_option['optionId']}"
                    )
                option_ids.add(normalized_option["optionId"])
                options.append(normalized_option)
            if recommended not in {option["action"] for option in options}:
                normalized_option = normalize_option(
                    {"action": recommended, "recommended": True},
                    recommended,
                    language,
                    item_status,
                    item_intent_detail,
                    -1,
                )
                if normalized_option["optionId"] in option_ids:
                    raise SystemExit(
                        f"Item {ledger_id} has duplicate optionId: {normalized_option['optionId']}"
                    )
                options.insert(0, normalized_option)
            ledger_summary = str(
                item.get("ledgerSummary")
                or item.get("ledgerText")
                or item.get("finding")
                or ""
            ).strip()
            if not ledger_summary:
                raise SystemExit(f"Item {ledger_id} must include ledgerSummary/finding/ledgerText")
            current_status = str(item.get("currentStatus") or "")
            section = infer_ledger_section(item, ledger_summary)
            secret_checklist = secret_checklist_for_text(
                " ".join(
                    [
                        ledger_summary,
                        str(item.get("shortTitle") or ""),
                        str(item.get("plainExplanation") or ""),
                        str(item.get("whyItMatters") or ""),
                        str(item.get("implementationHint") or ""),
                    ]
                )
            )
            implementation_hint = str(item.get("implementationHint") or "")
            if secret_checklist and not implementation_hint:
                implementation_hint = "Before closing, verify both current files and Git history for exposed secrets."
            normalized = {
                "ledgerId": ledger_id,
                "itemType": normalize_item_type(item.get("itemType")),
                "shortTitle": owner_facing_text(language, item.get("shortTitle") or ledger_id),
                "ledgerLocation": ledger_location(item, section, ledger_id, current_status),
                "ledgerSummary": clean_ledger_summary(language, ledger_summary, ledger_id, current_status),
                "plainExplanation": owner_facing_text(language, item.get("plainExplanation") or ""),
                "whyItMatters": owner_facing_text(language, item.get("whyItMatters") or ""),
                "decisionQuestion": owner_facing_text(language, item.get("decisionQuestion") or ""),
                "executionKind": normalize_execution_kind(
                    item.get("executionKind")
                    or item.get("applicationKind")
                    or item.get("postResponseKind")
                    or group.get("executionKind"),
                    category,
                ),
                "implementationHint": implementation_hint,
                "risk": str(item.get("risk") or ""),
                "currentStatus": current_status,
                "currentAwareness": str(item.get("currentAwareness") or "unconfirmed"),
                "recommendedAction": recommended,
                "status": item_status,
                "intentDetail": item_intent_detail,
                "secretChecklist": secret_checklist,
                "responseAwareness": normalize_awareness(
                    item.get("responseAwareness") or item.get("currentAwareness") or "unconfirmed"
                ),
                "options": options,
            }
            if normalized["currentAwareness"] in {"unknown_unknown", "unconfirmed", *LOCALIZED_UNCONFIRMED}:
                if not normalized["plainExplanation"] or not normalized["whyItMatters"]:
                    raise SystemExit(
                        f"Item {ledger_id} is unknown/unconfirmed and needs plainExplanation and whyItMatters"
                    )
            normalized_items.append(normalized)
            item_ids.append(ledger_id)
        normalized_groups.append(
            {
                "groupId": group_id,
                "title": owner_facing_text(language, group.get("title") or group_id),
                "plainSummary": owner_facing_text(language, group.get("plainSummary") or ""),
                "category": category,
                "recommendedAction": str(group.get("recommendedAction") or ""),
                "items": normalized_items,
            }
        )

    return {
        "schema": BOARD_SCHEMA,
        "boardId": board_id,
        "createdAt": str(raw.get("createdAt") or utc_now()),
        "language": language,
        "title": str(raw.get("title") or "Blindspot Ledger Triage"),
        "projectName": str(raw.get("projectName") or root.name),
        "projectRoot": str(root),
        "ledgerPath": str(ledger),
        "ledgerHash": ledger_hash,
        "groups": normalized_groups,
        "_itemIds": item_ids,
    }


def render_html(template_path: Path, board_data: dict[str, Any]) -> str:
    template = template_path.read_text(encoding="utf-8")
    data_for_html = strip_internal_board_fields(
        {key: value for key, value in board_data.items() if not key.startswith("_")}
    )
    payload = json.dumps(data_for_html, ensure_ascii=False)
    # Script content cannot contain a literal closing script tag.
    payload = payload.replace("</", "<\\/")
    return template.replace("__TRIAGE_BOARD_DATA_JSON__", payload)


def strip_internal_board_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_internal_board_fields(child)
            for key, child in value.items()
            if key != "itemType"
        }
    if isinstance(value, list):
        return [strip_internal_board_fields(child) for child in value]
    return value


def ensure_tmp_gitignore(tmp_root: Path) -> None:
    tmp_root.mkdir(parents=True, exist_ok=True)
    gitignore = tmp_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")
        return
    lines = gitignore.read_text(encoding="utf-8").splitlines()
    if "*" not in {line.strip() for line in lines}:
        gitignore.write_text("\n".join(lines).rstrip() + "\n*\n", encoding="utf-8")


def split_markdown_row(line: str) -> list[str]:
    text = line.strip()
    if not text.startswith("|") or "|" not in text[1:]:
        return []
    return [cell.strip() for cell in text.strip("|").split("|")]


def is_markdown_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def normalize_header(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def table_value(row: dict[str, str], *names: str) -> str:
    wanted = {normalize_header(name) for name in names}
    for key, value in row.items():
        if normalize_header(key) in wanted:
            return value.strip()
    return ""


def slugify_group_id(value: str) -> str:
    token = safe_path_token(value.lower().replace(" ", "-"))
    return token or "ledger-items"


def canonical_ledger_section(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    lowered = text.lower()
    normalized = normalize_header(text)
    if lowered in {"findings", "finding"} or normalized in {"발견항목", "발견", "점검항목"}:
        return "Findings"
    if lowered in {"decision packet", "decisions"} or normalized in {
        "결정묶음",
        "결정패킷",
        "결정항목",
        "결정대기",
    }:
        return "Decision Packet"
    if lowered in {"resolved archive", "resolved"} or normalized in {
        "해결된항목보관함",
        "해결항목",
        "해결됨",
        "해결보관함",
    }:
        return "Resolved Archive"
    if lowered in {"skipped for now", "skipped"} or normalized in {
        "일단건너뜀",
        "나중에보기",
        "보류항목",
    }:
        return "Skipped For Now"
    if lowered in {"audit log", "audit history"} or normalized in {"감사이력", "점검이력", "기록"}:
        return "Audit Log"
    return text


def first_sentence(value: str, limit: int = 80) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if not text:
        return "Ledger item"
    sentence = re.split(r"(?<=[.!?。])\s+", text, maxsplit=1)[0]
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip() + "..."


def close_cue_present(value: str) -> bool:
    text = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    if not text:
        return False
    return bool(
        re.search(
            r"(닫아도\s*됨|닫아도\s*됩니다|닫기|해결\s*처리|해결됨|이미\s*해결|"
            r"완료|신경\s*안\s*써도|학습\s*제외|확인했으니\s*해결|"
            r"can\s*close|close\s*this|already\s*resolved|resolved|done)",
            text,
        )
    )


def reject_cue_present(value: str) -> bool:
    text = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    if not text:
        return False
    return bool(re.search(r"(해당\s*없|하지\s*않|안\s*함|거절|제외|not\s*applicable|reject)", text))


def defer_cue_present(value: str) -> bool:
    text = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    if not text:
        return False
    return bool(re.search(r"(보류|나중|추후|다음에|defer|later)", text))


def status_is_open(value: str) -> bool:
    text = str(value or "").strip().lower()
    if text in {"resolved", "rejected", "closed", "done", "해결", "해결됨", "거절", "거절됨"}:
        return False
    return True


def classify_draft_item(section: str, text: str, status: str) -> tuple[str, str]:
    lowered = f"{section} {text} {status}".lower()
    if section == "Decision Packet":
        return "decision_bundle", "owner_followup"
    if re.search(r"\b(legal|privacy|terms|refund|payment|provider|platform|policy|compliance)\b", lowered):
        return "needs_external_confirmation", "external_confirmation"
    if looks_like_exposed_secret(lowered):
        return "quick_cleanup", "cheap_verification"
    if status.lower() in {"accepted", "수용됨"}:
        return "safe_accept", "ledger_only"
    if status.lower() in {"deferred", "보류", "보류됨"}:
        return "decision_bundle", "ledger_only"
    return "decision_bundle", "ledger_only"


def infer_draft_status(row: dict[str, str], section: str) -> str:
    status = table_value(row, "Status", "상태", "처리 상태", "상태값")
    if not status and section != "Decision Packet":
        status = table_value(row, "결정", "처리")
    return status


def infer_draft_recommendation(status: str, awareness: str, ledger_summary: str, followup: str) -> str:
    combined = " ".join(str(part or "") for part in (status, awareness, ledger_summary, followup))
    if close_cue_present(combined):
        return "resolved_candidate"
    if reject_cue_present(combined):
        return "reject"
    if defer_cue_present(combined):
        return "defer"
    lowered_status = status.lower()
    if lowered_status in {"accepted", "수용됨", "승인", "승인됨"}:
        return "accept"
    if lowered_status in {"deferred", "보류", "보류됨"}:
        return "defer"
    return "keep_pending"


def draft_explanation(language: str, ledger_summary: str = "", followup: str = "") -> tuple[str, str, str]:
    summary = first_sentence(ledger_summary, 120)
    followup_text = first_sentence(followup, 120)
    if language_key(language) == "ko":
        explanation = (
            f"원장에 적힌 핵심 내용은 '{summary}'입니다. 이 항목을 계속 열어 둘지, "
            "확인 후 해결 후보로 볼지, 하지 않기로 기록할지 정하면 됩니다."
            if summary != "Ledger item"
            else "이 항목은 기존 원장에 열려 있는 항목입니다. 계속 추적할지, 확인 후 닫을지, 하지 않기로 기록할지 정하면 됩니다."
        )
        why = (
            f"원장에 적힌 후속 제안은 '{followup_text}'입니다. 방향을 정해두면 다음 점검에서 같은 질문을 반복하지 않습니다."
            if followup_text != "Ledger item"
            else "이 항목을 그대로 두면 다음 점검에서도 계속 다시 보게 됩니다. 지금 방향만 정해도 원장이 훨씬 읽기 쉬워집니다."
        )
        return (
            explanation,
            why,
            "이 항목을 이번에 어떻게 처리할까요?",
        )
    explanation = (
        f"The ledger item says: '{summary}'. Decide whether to keep tracking it, defer it, reject it, or treat it as resolved after verification."
        if summary != "Ledger item"
        else "This is an open item from the existing ledger. Decide whether to keep tracking it, defer it, reject it, or treat it as resolved after verification."
    )
    why = (
        f"The ledger's suggested next step is: '{followup_text}'. Recording a direction prevents the next audit from asking the same question again."
        if followup_text != "Ledger item"
        else "If this stays open without a decision, future audits will keep surfacing it. Even a small owner choice can make the ledger easier to use."
    )
    return (
        explanation,
        why,
        "How should this item be handled now?",
    )


def parse_markdown_sections(text: str) -> list[tuple[str, str, list[str]]]:
    sections: list[tuple[str, str, list[str]]] = []
    current_raw = ""
    current = ""
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        heading = re.match(r"^##+\s+(.+?)\s*$", raw_line)
        if heading:
            if current_raw:
                sections.append((canonical_ledger_section(current_raw), current_raw, current_lines))
            current_raw = heading.group(1).strip()
            current = canonical_ledger_section(current_raw)
            current_lines = []
            continue
        if current_raw:
            current_lines.append(raw_line)
    if current_raw:
        sections.append((current, current_raw, current_lines))
    return sections


def hygiene_signal_lines(lines: list[str]) -> list[str]:
    signals = []
    pattern = re.compile(
        r"(?:\b\d+\.\d+\.\d+\b|\bv\d+\.\d+\.\d+\b|latest|release|릴리스|"
        r"version|버전|pytest|unittest|test|테스트|검증|통과|\d+\s*개)",
        re.IGNORECASE,
    )
    for line in lines:
        text = re.sub(r"\s+", " ", line.strip(" -")).strip()
        if text and pattern.search(text):
            signals.append(text)
    return signals


def draft_hygiene_items(ledger: Path, language: str) -> list[dict[str, Any]]:
    text = ledger.read_text(encoding="utf-8")
    items: list[dict[str, Any]] = []
    for section, raw_section, lines in parse_markdown_sections(text):
        if section not in {"Checked And Well Covered", "Audit Log"}:
            continue
        signals = hygiene_signal_lines(lines)
        if not signals:
            continue
        preview = "; ".join(first_sentence(signal, 140) for signal in signals[:4])
        today = datetime.now().strftime("%Y%m%d")
        suffix = len(items) + 1
        if language_key(language) == "ko":
            summary = f"{raw_section} 섹션에 버전, 테스트, 릴리스, 검증 결과처럼 시간이 지나면 낡을 수 있는 문구가 있습니다: {preview}"
            explanation = (
                "이 항목은 특정 발견 하나가 아니라 원장 섹션 자체의 상태 점검입니다. "
                "현재 코드와 릴리스 상태를 확인한 뒤, 오래된 요약 문구만 고치면 됩니다."
            )
            why = "다음 세션이 오래된 버전이나 테스트 개수를 기준으로 판단하지 않게 막아줍니다."
            question = "이 원장 요약 섹션을 현재 상태 기준으로 다시 확인할까요?"
            label = "확인 후 원장 요약 갱신하기"
            tradeoff = "현재 버전, 테스트, 릴리스 상태를 확인한 뒤 원장 요약 문구만 고칩니다."
            keep_label = "지금은 그대로 두기"
            keep_tradeoff = "원장은 바꾸지 않습니다. 대신 다음 세션이 오래된 요약을 다시 볼 수 있습니다."
            explain_label = "왜 갱신해야 하는지 설명받기"
            explain_tradeoff = "원장은 건드리지 않고, 어떤 문구가 왜 낡았을 수 있는지 먼저 설명합니다."
        else:
            summary = (
                f"The {raw_section} section contains version, test, release, or verification text "
                f"that can go stale: {preview}"
            )
            explanation = (
                "This is not a single finding row. It is a ledger-section hygiene check: "
                "verify the current project state, then refresh only stale summary wording."
            )
            why = "It prevents future sessions from relying on outdated version numbers, test counts, or release status."
            question = "Should this ledger summary section be checked and refreshed?"
            label = "Check and refresh the ledger summary"
            tradeoff = "Verify current version, tests, and release state, then update only the ledger summary wording."
            keep_label = "Leave it unchanged for now"
            keep_tradeoff = "Do not change the ledger. A later session may still see the stale summary."
            explain_label = "Explain why this matters"
            explain_tradeoff = "Do not change the ledger; explain which wording may be stale first."
        items.append(
            {
                "category": "quick_cleanup",
                "item": {
                    "ledgerId": f"LEDGER-HYGIENE-{today}-{suffix:02d}",
                    "itemType": "ledger_section",
                    "shortTitle": f"{raw_section} summary refresh",
                    "ledgerSection": section,
                    "ledgerLocation": f"{raw_section} / hygiene candidate",
                    "ledgerSummary": summary,
                    "plainExplanation": explanation,
                    "whyItMatters": why,
                    "decisionQuestion": question,
                    "executionKind": "cheap_verification",
                    "implementationHint": "Verify current manifests, tests, package checks, and release/latest status before editing this ledger section.",
                    "currentStatus": "hygiene-candidate",
                    "currentAwareness": "unconfirmed",
                    "recommendedAction": "accept",
                    "risk": "next",
                    "options": [
                        {
                            "optionId": "refresh-ledger-summary",
                            "action": "accept",
                            "label": label,
                            "tradeoff": tradeoff,
                            "status": "accepted",
                            "intentDetail": "refresh_ledger_summary",
                            "recommended": True,
                        },
                        {
                            "optionId": "keep-ledger-summary",
                            "action": "keep_pending",
                            "label": keep_label,
                            "tradeoff": keep_tradeoff,
                            "status": "",
                            "intentDetail": "",
                        },
                        {
                            "optionId": "reexplain-ledger-summary",
                            "action": "needs_reexplain",
                            "label": explain_label,
                            "tradeoff": explain_tradeoff,
                            "status": "",
                            "intentDetail": "",
                        },
                    ],
                },
            }
        )
    return items


def parse_ledger_tables(ledger: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    section = ""
    raw_section = ""
    headers: list[str] | None = None
    pending_header: list[str] | None = None
    for raw_line in ledger.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##+\s+(.+?)\s*$", raw_line)
        if heading:
            raw_section = heading.group(1).strip()
            section = canonical_ledger_section(raw_section)
            headers = None
            pending_header = None
            continue
        cells = split_markdown_row(raw_line)
        if not cells:
            headers = None
            pending_header = None
            continue
        if is_markdown_separator(cells):
            headers = pending_header
            pending_header = None
            continue
        if headers is None:
            pending_header = cells
            continue
        padded = cells + [""] * max(0, len(headers) - len(cells))
        row = dict(zip(headers, padded[: len(headers)]))
        row["_section"] = section
        row["_sectionRaw"] = raw_section
        rows.append(row)
    return rows


def draft_item_from_row(row: dict[str, str], language: str) -> dict[str, Any] | None:
    section = row.get("_section", "")
    if section in {"Audit Log", "Resolved Archive", "Skipped For Now"}:
        return None
    ledger_id = table_value(row, "ID", "Id", "식별자", "항목 ID", "항목ID")
    if not ledger_id:
        return None
    if not re.match(r"^(BS|DP)-\d{8}-\d+", ledger_id):
        return None
    status = infer_draft_status(row, section)
    if not status_is_open(status):
        return None
    if section == "Decision Packet":
        summary = table_value(row, "Decision", "Finding", "What", "결정", "항목", "내용", "요약")
        recommended_text = table_value(
            row, "Recommended option", "Recommended", "Recommendation", "추천", "권장 선택", "권장안"
        )
        options_text = table_value(row, "Options", "Choices", "선택지", "옵션")
        why = table_value(row, "Why it matters", "Why", "왜 중요한가", "이유")
        followup = table_value(
            row,
            "Next check / owner",
            "Next check",
            "Owner",
            "Follow-up",
            "Followup",
            "후속 제안",
            "후속제안",
            "다음 확인",
            "다음확인",
            "확인",
            "제안",
        )
        ledger_summary = summary
        if recommended_text:
            ledger_summary += f" Recommended: {recommended_text}."
        if options_text:
            ledger_summary += f" Options: {options_text}."
        if why:
            ledger_summary += f" Why: {why}."
        if followup:
            ledger_summary += f" Next: {followup}."
    else:
        summary = table_value(
            row,
            "Finding",
            "Decision",
            "Item",
            "항목",
            "발견",
            "내용",
            "문제",
            "요약",
            "사각지대",
        )
        followup = table_value(
            row,
            "Next check / owner",
            "Next check",
            "Owner",
            "Follow-up",
            "Followup",
            "후속 제안",
            "후속제안",
            "다음 확인",
            "다음확인",
            "확인",
            "제안",
        )
        ledger_summary = summary
        if followup:
            ledger_summary += f" Next: {followup}."
    if not ledger_summary.strip():
        return None
    awareness = table_value(
        row,
        "Awareness",
        "인지 상태",
        "인지",
        "인식 상태",
        "인지 분류",
        "인지분류",
        "Awareness classification",
    ) or "unconfirmed"
    priority = table_value(row, "Priority", "Risk", "우선순위", "위험도", "중요도")
    category, execution_kind = classify_draft_item(section, ledger_summary, status)
    recommended_action = infer_draft_recommendation(status, awareness, ledger_summary, followup)
    explanation, why_it_matters, decision_question = draft_explanation(language, summary or ledger_summary, followup)
    item = {
        "ledgerId": ledger_id,
        "shortTitle": first_sentence(summary or ledger_summary),
        "ledgerSection": section or "Ledger",
        "ledgerSummary": ledger_summary.strip(),
        "plainExplanation": explanation,
        "whyItMatters": why_it_matters,
        "decisionQuestion": decision_question,
        "executionKind": execution_kind,
        "currentStatus": status,
        "currentAwareness": awareness,
        "recommendedAction": recommended_action,
        "risk": priority,
    }
    if looks_like_exposed_secret(ledger_summary):
        item["implementationHint"] = "Before closing, verify both current files and Git history for exposed secrets."
    elif followup and execution_kind in {"implementation_plan", "external_confirmation", "owner_followup", "cheap_verification"}:
        item["implementationHint"] = followup
    return {"category": category, "item": item}


def command_draft(args: argparse.Namespace) -> int:
    root, ledger = resolve_project_and_ledger(args.project_root, args.ledger)
    language = str(args.language or "en")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in parse_ledger_tables(ledger):
        drafted = draft_item_from_row(row, language)
        if not drafted:
            continue
        grouped.setdefault(drafted["category"], []).append(drafted["item"])
    if getattr(args, "include_ledger_hygiene", False):
        for drafted in draft_hygiene_items(ledger, language):
            grouped.setdefault(drafted["category"], []).append(drafted["item"])
    if not grouped:
        raise SystemExit("No open Findings or Decision Packet rows found for draft board input")

    titles = {
        "quick_cleanup": "Quick cleanup candidates",
        "safe_accept": "Safe accept candidates",
        "decision_bundle": "Decision bundle",
        "needs_external_confirmation": "External confirmation items",
        "needs_owner_detail": "Owner detail needed",
        "needs_reexplain": "Needs clearer explanation",
    }
    if language_key(language) == "ko":
        titles.update(
            {
                "quick_cleanup": "빠르게 정리할 후보",
                "safe_accept": "승인하면 추적 가능한 항목",
                "decision_bundle": "묶어서 결정할 항목",
                "needs_external_confirmation": "외부 확인이 필요한 항목",
                "needs_owner_detail": "사용자 판단이 필요한 항목",
                "needs_reexplain": "다시 설명이 필요한 항목",
            }
        )
    groups = []
    for category, items in grouped.items():
        groups.append(
            {
                "groupId": slugify_group_id(category),
                "category": category,
                "title": titles.get(category, category),
                "plainSummary": "Drafted from existing ledger rows. Review explanations, recommendations, and options before creating the board.",
                "items": items,
            }
        )
    data = {
        "schema": BOARD_SCHEMA,
        "draftOnly": True,
        "boardId": str(args.board_id or f"ledger-triage-{root.name}-{datetime.now().strftime('%Y%m%d')}"),
        "language": language,
        "title": str(args.title or "Blindspot Ledger Triage"),
        "projectName": str(args.project_name or root.name),
        "groups": groups,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out, data)
    print(f"Wrote draft board input: {args.out}")
    print(f"Drafted {sum(len(group['items']) for group in groups)} item(s) in {len(groups)} group(s).")
    print("Review and edit plain explanations, recommendations, options, and executionKind before create.")
    return 0


def command_create(args: argparse.Namespace) -> int:
    root, ledger = resolve_project_and_ledger(args.project_root, args.ledger)
    raw = load_json(args.data)
    if raw.get("draftOnly") is True and not getattr(args, "allow_unreviewed_draft", False):
        raise SystemExit(
            "Board input is marked draftOnly. Review and rewrite explanations/options first, "
            "then remove draftOnly or pass --allow-unreviewed-draft for an explicit test-only override."
        )
    board_data = normalize_board_data(raw, root, ledger)
    short_id = safe_path_token(board_data["boardId"])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tmp_root = root / ".blindspot-tmp"
    ensure_tmp_gitignore(tmp_root)
    board_dir = tmp_root / f"ledger-triage-{timestamp}-{short_id}"
    board_dir.mkdir(parents=True, exist_ok=False)

    template_path = Path(__file__).resolve().parents[1] / "templates" / "ledger-triage-board.html"
    html = render_html(template_path, board_data)
    html_path = board_dir / HTML_NAME
    html_path.write_text(html, encoding="utf-8")

    marker = {
        "schema": MARKER_SCHEMA,
        "boardId": board_data["boardId"],
        "createdAt": board_data["createdAt"],
        "projectRoot": str(root),
        "ledgerPath": str(ledger),
        "ledgerHash": board_data["ledgerHash"],
        "htmlFile": HTML_NAME,
        "responseFile": RESPONSE_NAME,
        "itemIds": board_data["_itemIds"],
    }
    write_json(board_dir / MARKER_NAME, marker)
    write_json(board_dir / "board-data.json", {key: value for key, value in board_data.items() if not key.startswith("_")})

    print(f"Created ledger triage board: {html_path}")
    print(f"Board directory: {board_dir}")
    write_optional_text_file(getattr(args, "write_board_dir", None), str(board_dir))
    if getattr(args, "serve", False):
        return command_serve(
            argparse.Namespace(
                board_dir=board_dir,
                port=getattr(args, "port", 0),
                write_url=getattr(args, "write_url", None),
                write_pid=getattr(args, "write_pid", None),
                write_board_dir=getattr(args, "write_board_dir", None),
            )
        )
    return 0


def write_optional_text_file(path: Optional[Path], value: str) -> None:
    if not path:
        return
    target = path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8")


class TriageHandler(http.server.SimpleHTTPRequestHandler):
    board_dir: Path
    shutdown_token: str = ""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        print(f"[ledger-triage-board] {format % args}", file=sys.stderr)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self.path = f"/{HTML_NAME}"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/shutdown":
            self.handle_shutdown()
            return
        if parsed.path != "/api/triage-response":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        write_json(self.board_dir / RESPONSE_NAME, payload)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(b'{"ok": true}\n')

    def handle_shutdown(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        if str(payload.get("token") or "") != self.shutdown_token:
            self.send_error(403, "Invalid shutdown token")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(b'{"ok": true, "shutdown": true}\n')
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def command_serve(args: argparse.Namespace) -> int:
    board_dir = args.board_dir.resolve()
    marker = read_marker(board_dir)
    if not (board_dir / marker["htmlFile"]).exists():
        raise SystemExit(f"Missing board HTML: {board_dir / marker['htmlFile']}")

    class BoundTriageHandler(TriageHandler):
        pass

    BoundTriageHandler.board_dir = board_dir
    shutdown_token = secrets.token_urlsafe(32)
    BoundTriageHandler.shutdown_token = shutdown_token
    handler = functools.partial(BoundTriageHandler, directory=str(board_dir))

    class Server(http.server.ThreadingHTTPServer):
        allow_reuse_address = True

    with Server(("127.0.0.1", args.port), handler) as server:
        host, port = server.server_address
        url = f"http://{host}:{port}/"
        write_server_state(board_dir, marker, url, shutdown_token)
        print(f"Open {url}")
        write_optional_text_file(getattr(args, "write_url", None), url)
        write_optional_text_file(getattr(args, "write_pid", None), str(os.getpid()))
        write_optional_text_file(getattr(args, "write_board_dir", None), str(board_dir))
        if getattr(args, "write_url", None):
            print(f"Wrote board URL: {args.write_url.resolve()}")
        if getattr(args, "write_pid", None):
            print(f"Wrote server PID: {args.write_pid.resolve()}")
        if getattr(args, "write_board_dir", None):
            print(f"Wrote board directory: {args.write_board_dir.resolve()}")
        print("Press Ctrl+C after the owner submits the response.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped ledger triage board server")
    return 0


def write_server_state(board_dir: Path, marker: dict[str, Any], url: str, shutdown_token: str) -> Path:
    state = {
        "schema": SERVER_STATE_SCHEMA,
        "boardId": marker.get("boardId"),
        "boardDir": str(board_dir.resolve()),
        "url": url,
        "pid": os.getpid(),
        "shutdownToken": shutdown_token,
        "createdAt": utc_now(),
    }
    path = board_dir / SERVER_STATE_NAME
    write_json(path, state)
    return path


def shutdown_server_from_state(board_dir: Path, marker: dict[str, Any]) -> bool:
    state_path = board_dir / SERVER_STATE_NAME
    if not state_path.exists():
        return False
    state = load_json(state_path)
    if state.get("schema") != SERVER_STATE_SCHEMA:
        raise SystemExit(f"Server state schema must be {SERVER_STATE_SCHEMA!r}")
    if state.get("boardId") != marker.get("boardId"):
        raise SystemExit("Server state boardId does not match marker")
    state_board_dir = Path(str(state.get("boardDir") or "")).resolve()
    if state_board_dir != board_dir.resolve():
        raise SystemExit("Server state boardDir does not match cleanup target")
    token = str(state.get("shutdownToken") or "")
    if not token:
        raise SystemExit("Server state is missing shutdown token")
    parsed = urlparse(str(state.get("url") or ""))
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or not parsed.port:
        raise SystemExit("Server state URL must be localhost HTTP")
    endpoint = f"http://{parsed.hostname}:{parsed.port}/api/shutdown"
    payload = json.dumps({"token": token}).encode("utf-8")
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=3) as response:
            if response.status != 200:
                raise SystemExit(f"Server shutdown failed with HTTP {response.status}")
    except HTTPError as exc:
        raise SystemExit(f"Server shutdown rejected the stored token with HTTP {exc.code}") from exc
    except URLError as exc:
        print(f"Server state found but no running board server responded: {exc.reason}")
        return False
    print("Stopped ledger triage board server from server-state.json")
    return True


def read_marker(board_dir: Path) -> dict[str, Any]:
    marker_path = board_dir / MARKER_NAME
    if not marker_path.exists():
        raise SystemExit(f"Missing marker file: {marker_path}")
    marker = load_json(marker_path)
    if marker.get("schema") != MARKER_SCHEMA:
        raise SystemExit(f"Marker schema must be {MARKER_SCHEMA!r}")
    return marker


def validate_board_dir_shape(board_dir: Path, marker: dict[str, Any]) -> tuple[Path, Path]:
    root = Path(str(marker.get("projectRoot", ""))).resolve()
    ledger = Path(str(marker.get("ledgerPath", ""))).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Marker projectRoot is not a directory: {root}")
    if not ledger.exists() or not ledger.is_file():
        raise SystemExit(f"Marker ledgerPath is not a file: {ledger}")
    if not is_relative_to(ledger, root):
        raise SystemExit("Marker ledgerPath is outside projectRoot")
    expected_parent = root / ".blindspot-tmp"
    if board_dir.parent.resolve() != expected_parent.resolve():
        raise SystemExit(f"Board directory must be directly under {expected_parent}")
    if not board_dir.name.startswith("ledger-triage-"):
        raise SystemExit("Board directory name must start with ledger-triage-")
    if not is_relative_to(board_dir.resolve(), root):
        raise SystemExit("Board directory is outside projectRoot")
    return root, ledger


def parse_completed_at(value: Any) -> float:
    text = str(value or "").strip()
    if not text:
        return 0.0
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def default_response_search_dir() -> Path:
    downloads = Path.home() / "Downloads"
    return downloads if downloads.exists() else Path.home()


def validate_response_identity(response: dict[str, Any], marker: dict[str, Any], source: Path) -> None:
    if response.get("schema") != RESPONSE_SCHEMA:
        raise SystemExit(f"{source} schema must be {RESPONSE_SCHEMA!r}")
    if response.get("boardId") != marker.get("boardId"):
        raise SystemExit(f"{source} boardId does not match marker")
    if str(response.get("ledgerPath")) != str(marker.get("ledgerPath")):
        raise SystemExit(f"{source} ledgerPath does not match marker")
    if response.get("ledgerHash") != marker.get("ledgerHash"):
        raise SystemExit(f"{source} ledgerHash does not match marker")


def copy_response_to_board(board_dir: Path, response_path: Path) -> Path:
    marker = read_marker(board_dir)
    validate_board_dir_shape(board_dir.resolve(), marker)
    source = response_path.resolve()
    if not source.exists() or not source.is_file():
        raise SystemExit(f"Response file not found: {source}")
    response = load_json(source)
    validate_response_identity(response, marker, source)
    destination = board_dir / RESPONSE_NAME
    write_json(destination, response)
    if source == destination.resolve():
        print(f"Using response JSON already in board directory: {destination}")
    else:
        print(f"Copied response JSON into board directory: {source} -> {destination}")
    return destination


def collect_response_to_board(board_dir: Path, response_dir: Optional[Path] = None) -> Path:
    marker = read_marker(board_dir)
    validate_board_dir_shape(board_dir.resolve(), marker)
    search_dir = (response_dir or default_response_search_dir()).resolve()
    if not search_dir.exists() or not search_dir.is_dir():
        raise SystemExit(f"Response search directory not found: {search_dir}")

    paths: dict[Path, None] = {}
    for pattern in (RESPONSE_NAME, "blindspot-triage-response*.json"):
        for path in search_dir.glob(pattern):
            if path.is_file():
                paths[path.resolve()] = None

    candidates: list[tuple[float, float, Path, dict[str, Any]]] = []
    skipped = 0
    for path in paths:
        try:
            response = load_json(path)
            validate_response_identity(response, marker, path)
        except SystemExit:
            skipped += 1
            continue
        candidates.append((parse_completed_at(response.get("completedAt")), path.stat().st_mtime, path, response))

    if not candidates:
        detail = f" ({skipped} response-shaped file(s) did not match this board)" if skipped else ""
        raise SystemExit(f"No matching response JSON found in {search_dir}{detail}")

    candidates.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
    _completed, _mtime, chosen_path, chosen_response = candidates[0]
    destination = board_dir / RESPONSE_NAME
    write_json(destination, chosen_response)
    if len(candidates) > 1:
        print(
            f"Found {len(candidates)} matching response JSON files; "
            f"selected newest completedAt: {chosen_path}"
        )
    else:
        print(f"Found matching response JSON: {chosen_path}")
    print(f"Copied response JSON into board directory: {chosen_path} -> {destination}")
    return destination


def validate_response(board_dir: Path, *, check_current_ledger_hash: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    marker = read_marker(board_dir)
    _root, ledger = validate_board_dir_shape(board_dir.resolve(), marker)
    board_data = load_board_data(board_dir)
    if check_current_ledger_hash:
        current_hash = sha256_file(ledger)
        if current_hash != marker.get("ledgerHash"):
            raise SystemExit("Ledger hash changed since the board was created; regenerate the board or inspect manually")

    response_path = board_dir / RESPONSE_NAME
    if not response_path.exists():
        raise SystemExit(
            f"Missing response file: {response_path}. "
            "If the browser downloaded it, run validate with --collect-response or --response <path>."
        )
    response = load_json(response_path)
    if response.get("schema") != RESPONSE_SCHEMA:
        raise SystemExit(f"Response schema must be {RESPONSE_SCHEMA!r}")
    if response.get("boardId") != marker.get("boardId"):
        raise SystemExit("Response boardId does not match marker")
    if str(response.get("ledgerPath")) != str(marker.get("ledgerPath")):
        raise SystemExit("Response ledgerPath does not match marker")
    if response.get("ledgerHash") != marker.get("ledgerHash"):
        raise SystemExit("Response ledgerHash does not match marker")

    item_id_list = marker.get("itemIds") or []
    item_ids = set(item_id_list)
    if len(item_ids) != len(item_id_list):
        raise SystemExit("Marker itemIds must be unique")
    decisions = response.get("decisions")
    if not isinstance(decisions, list):
        raise SystemExit("Response decisions must be a list")
    if not decisions:
        raise SystemExit("Response decisions must include at least one selected item")
    option_by_id: dict[str, dict[str, dict[str, Any]]] = {}
    options_by_action: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for group in board_data.get("groups") or []:
        if not isinstance(group, dict):
            continue
        for item in group.get("items") or []:
            if not isinstance(item, dict):
                continue
            ledger_id = str(item.get("ledgerId") or "")
            option_by_id[ledger_id] = {}
            options_by_action[ledger_id] = {}
            for option in item.get("options") or []:
                if isinstance(option, dict):
                    option_id = str(option.get("optionId") or "")
                    action = str(option.get("action") or "")
                    if option_id:
                        option_by_id[ledger_id][option_id] = option
                    options_by_action[ledger_id].setdefault(action, []).append(option)
    seen_decisions = set()
    for decision in decisions:
        if not isinstance(decision, dict):
            raise SystemExit("Each response decision must be an object")
        ledger_id = decision.get("ledgerId")
        if ledger_id not in item_ids:
            raise SystemExit(f"Response includes unknown ledgerId: {ledger_id!r}")
        if ledger_id in seen_decisions:
            raise SystemExit(f"Response includes duplicate ledgerId: {ledger_id!r}")
        seen_decisions.add(ledger_id)
        action = decision.get("action")
        if action not in ALLOWED_ACTIONS:
            raise SystemExit(f"Response includes unknown action for {ledger_id}: {action!r}")
        option_id = str(decision.get("optionId") or "").strip()
        if option_id:
            option = option_by_id.get(str(ledger_id), {}).get(option_id)
            if not option:
                raise SystemExit(f"Response optionId {option_id!r} is not an offered option for {ledger_id}")
            if option.get("action") != action:
                raise SystemExit(
                    f"Response optionId {option_id!r} action mismatch for {ledger_id}: "
                    f"expected {option.get('action')!r}, got {action!r}"
                )
        else:
            action_options = options_by_action.get(str(ledger_id), {}).get(str(action), [])
            if len(action_options) > 1:
                raise SystemExit(
                    f"Response for {ledger_id} action {action!r} is ambiguous; include optionId"
                )
            option = action_options[0] if action_options else None
        if not option:
            raise SystemExit(f"Response action {action!r} is not an offered option for {ledger_id}")
        awareness = decision.get("awareness")
        if awareness not in ALLOWED_AWARENESS:
            raise SystemExit(f"Response includes unknown awareness for {ledger_id}: {awareness!r}")
        if action in {"keep_pending", "needs_reexplain"} and any(
            str(decision.get(field) or "").strip()
            for field in ("status", "intentDetail", "statusIntent")
        ):
            raise SystemExit(f"{ledger_id} action {action!r} must not include status or intentDetail")
        response_status, response_intent_detail = normalize_status_detail(decision, str(action))
        expected_status, expected_intent_detail = normalize_status_detail(option, str(action))
        if response_status != expected_status or response_intent_detail != expected_intent_detail:
            raise SystemExit(
                f"{ledger_id} status/intentDetail mismatch for action {action!r}: "
                f"expected {expected_status!r}/{expected_intent_detail!r}, "
                f"got {response_status!r}/{response_intent_detail!r}"
            )
        if action == "resolved_candidate" and not str(decision.get("note") or "").strip():
            raise SystemExit(f"{ledger_id} is resolved_candidate and needs a note/evidence")
    return marker, response


def load_board_data(board_dir: Path) -> dict[str, Any]:
    path = board_dir / "board-data.json"
    if not path.exists():
        raise SystemExit(f"Missing board data file: {path}")
    data = load_json(path)
    if data.get("schema") != BOARD_SCHEMA:
        raise SystemExit(f"Board data schema must be {BOARD_SCHEMA!r}")
    return data


def one_line_preview(value: Any, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def response_application_review(board_dir: Path, response: dict[str, Any]) -> dict[str, Any]:
    board_data = load_board_data(board_dir)
    item_map: dict[str, dict[str, Any]] = {}
    for group in board_data.get("groups") or []:
        for item in group.get("items") or []:
            if isinstance(item, dict):
                item_map[str(item.get("ledgerId"))] = item

    buckets = {
        "needs_reexplain": [],
        "implementation_plan": [],
        "cheap_verification": [],
        "external_confirmation": [],
        "owner_followup": [],
        "ledger_only": [],
    }
    decision_summaries = []
    note_constraints = []
    closure_notes = []
    secret_checks = []
    for decision in response.get("decisions") or []:
        ledger_id = str(decision.get("ledgerId"))
        action = str(decision.get("action"))
        item = item_map.get(ledger_id, {})
        execution_kind = str(item.get("executionKind") or "ledger_only")
        if action == "needs_reexplain":
            bucket = "needs_reexplain"
        elif action == "resolved_candidate":
            bucket = "cheap_verification"
        elif action in {"defer", "reject", "keep_pending"}:
            bucket = "ledger_only"
        elif action == "accept" and execution_kind in buckets:
            bucket = execution_kind
        else:
            bucket = "ledger_only"
        buckets[bucket].append(ledger_id)
        note = one_line_preview(decision.get("note") or "")
        status, intent_detail = normalize_status_detail(decision, action)
        summary = {
            "ledgerId": ledger_id,
            "itemType": str(item.get("itemType") or "ledger_row"),
            "title": str(item.get("shortTitle") or ledger_id),
            "ledgerSection": str(item.get("ledgerSection") or ""),
            "ledgerLocation": str(item.get("ledgerLocation") or ""),
            "ledgerSummary": one_line_preview(item.get("ledgerSummary") or ""),
            "action": action,
            "bucket": bucket,
            "executionKind": execution_kind,
            "status": status,
            "intentDetail": intent_detail,
            "note": note,
            "implementationHint": str(item.get("implementationHint") or ""),
            "secretChecklist": item.get("secretChecklist") or [],
        }
        decision_summaries.append(summary)
        if note and bucket in {"implementation_plan", "external_confirmation", "owner_followup"}:
            note_constraints.append(summary)
        if note and bucket == "ledger_only" and action in {"defer", "reject", "keep_pending"}:
            closure_notes.append(summary)
        if summary["secretChecklist"] and action in {"accept", "resolved_candidate"}:
            secret_checks.append(summary)

    if buckets["needs_reexplain"]:
        workflow = "reexplain_first"
    elif buckets["implementation_plan"]:
        workflow = "temporary_plan_required"
    else:
        workflow = "apply_directly"

    return {
        "schema": "blindspot-triage-application-review.v1",
        "boardId": response.get("boardId"),
        "language": str(board_data.get("language") or "en"),
        "workflow": workflow,
        "buckets": buckets,
        "selectedCount": len(response.get("decisions") or []),
        "decisions": decision_summaries,
        "noteConstraints": note_constraints,
        "closureNotes": closure_notes,
        "secretChecks": secret_checks,
    }


def format_decision_line(decision: dict[str, Any]) -> str:
    status = decision.get("status") or "-"
    detail = decision.get("intentDetail") or "-"
    note = f" note: {decision['note']}" if decision.get("note") else ""
    return (
        f"- {decision['ledgerId']} - {decision.get('title') or decision['ledgerId']}: "
        f"action={decision['action']}; bucket={decision['bucket']}; "
        f"status={status}; intentDetail={detail}; executionKind={decision['executionKind']}.{note}"
    )


def target_area_line(decision: dict[str, Any]) -> str:
    if decision["bucket"] == "ledger_only":
        return f"- {decision['ledgerId']}: ledger only; no project file change expected."
    if decision["bucket"] == "cheap_verification":
        return f"- {decision['ledgerId']}: read-only verification before ledger cleanup."
    if decision["bucket"] == "external_confirmation":
        return f"- {decision['ledgerId']}: external/provider/account confirmation; no local file target yet."
    if decision["bucket"] == "owner_followup":
        return f"- {decision['ledgerId']}: owner detail needed before file targets are known."
    hint = decision.get("implementationHint") or "TODO: identify files or project areas before editing."
    return f"- {decision['ledgerId']}: {hint}"


def write_application_plan(board_dir: Path, marker: dict[str, Any], review: dict[str, Any]) -> Path:
    plan_path = board_dir / PLAN_NAME
    lines = [
        "# Ledger Triage Application Plan",
        "",
        f"- board id: {marker.get('boardId')}",
        f"- ledger: {marker.get('ledgerPath')}",
        f"- workflow: {review['workflow']}",
        f"- selected decisions: {review['selectedCount']}",
        "",
        "## Selected Decisions",
        "",
    ]
    lines.extend(format_decision_line(decision) for decision in review["decisions"])
    lines.extend(["", "## Work Buckets", ""])
    for bucket, ids in review["buckets"].items():
        lines.append(f"- {bucket}: {', '.join(ids) if ids else '-'}")
    lines.extend(["", "## Target Files Or Areas", ""])
    for decision in review["decisions"]:
        lines.append(target_area_line(decision))
    lines.extend(["", "## Owner Notes As Constraints", ""])
    if review["noteConstraints"]:
        for decision in review["noteConstraints"]:
            lines.append(f"- {decision['ledgerId']}: {decision['note']}")
    else:
        lines.append("- No owner note constraints were submitted.")
    lines.extend(["", "## Ledger-Only Owner Notes", ""])
    if review["closureNotes"]:
        for decision in review["closureNotes"]:
            lines.append(f"- {decision['ledgerId']}: {decision['note']}")
    else:
        lines.append("- No ledger-only closure notes were submitted.")
    lines.extend(["", "## Secret Handling Checklist", ""])
    if review["secretChecks"]:
        for decision in review["secretChecks"]:
            lines.append(f"- {decision['ledgerId']}:")
            for item in decision.get("secretChecklist") or []:
                lines.append(f"  - [ ] {item}")
    else:
        lines.append("- No secret-specific checklist was detected.")
    lines.extend(
        [
            "",
            "## Ordered Steps",
            "",
            "1. Re-read the selected ledger rows and this response summary.",
            "2. Apply only the selected decisions. Do not touch unselected ledger rows.",
            "3. Run cheap verification before any resolved-candidate or secret-related closure.",
            "4. Record blockers instead of guessing when provider, legal, account, or owner detail is missing.",
            "5. Update only the durable ledger result after work is complete.",
            "",
            "## Stop Conditions",
            "",
            "- Stop if the current ledger hash changed in a way not explained by the selected work.",
            "- Stop if a required account, provider, legal, or owner detail is missing.",
            "- Stop if secret history still contains exposed credentials and rotation/history cleanup is not confirmed.",
            "- Stop if implementation scope grows beyond the selected decisions.",
            "",
            "## Verification",
            "",
            "- [ ] Validate changed files or docs touched by the selected decisions.",
            "- [ ] Re-run any cheap checks named in the ledger rows.",
            "- [ ] Confirm `BLINDSPOT_LEDGER.md` records selected choices, actual outcome, blockers, and cleanup result.",
            "",
            "## Cleanup",
            "",
            f"- [ ] Delete this temporary plan after the durable ledger result is recorded: `{PLAN_NAME}`.",
            "- [ ] Run helper cleanup with `--confirm-applied` only after selected decisions are applied or safely recorded.",
        ]
    )
    plan_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return plan_path


def ledger_suggestion_line(decision: dict[str, Any]) -> str:
    status = decision.get("status") or "-"
    detail = decision.get("intentDetail") or "-"
    note = f"; owner note: {decision['note']}" if decision.get("note") else ""
    if decision.get("itemType") == "ledger_section":
        return (
            f"- {decision['ledgerId']}: review `{decision.get('ledgerLocation') or decision.get('ledgerSection')}` "
            f"and update only stale ledger-section wording after verification "
            f"(action={decision['action']}; status={status}; intentDetail={detail}{note})."
        )
    return (
        f"- {decision['ledgerId']}: update only this ledger row/archive entry "
        f"(action={decision['action']}; status={status}; intentDetail={detail}{note})."
    )


def write_ledger_suggestions(board_dir: Path, marker: dict[str, Any], review: dict[str, Any]) -> Path:
    path = board_dir / LEDGER_SUGGESTIONS_NAME
    lines = [
        "# Ledger Triage Ledger Suggestions",
        "",
        f"- board id: {marker.get('boardId')}",
        f"- ledger: {marker.get('ledgerPath')}",
        f"- selected decisions: {review['selectedCount']}",
        "",
        "These are temporary suggestions for the applying agent. They do not edit the ledger.",
        "",
        "## Suggested Ledger Edits",
        "",
    ]
    lines.extend(ledger_suggestion_line(decision) for decision in review["decisions"])
    lines.extend(
        [
            "",
            "## Audit Log Draft",
            "",
            audit_log_suggestion(marker, review["selectedCount"], (board_dir / PLAN_NAME).exists(), review.get("language", "en")),
            "",
            "## Safety Notes",
            "",
            "- Apply only selected decisions from the validated response.",
            "- Leave omitted rows unchanged.",
            "- Delete this suggestions file with the board directory after durable ledger results are recorded.",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def audit_log_suggestion(
    marker: dict[str, Any], selected_count: int, plan_existed: bool, language: str = "en"
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    if language_key(language) == "ko":
        plan_note = "임시 계획이 있었음; 삭제 또는 결과 기록 확인 필요" if plan_existed else "남은 임시 계획 없음"
        return (
            f"{today} | <호스트> | ledger-triage | <범위> | board {marker.get('boardId')}; "
            f"선택 {selected_count}건 적용 또는 안전 기록; 임시 선택판 정리 완료; {plan_note}."
        )
    plan_note = (
        "temporary plan existed; confirm deleted or outcome recorded" if plan_existed else "no temporary plan remaining"
    )
    return (
        f"{today} | <host> | ledger-triage | <scope> | board {marker.get('boardId')}; "
        f"{selected_count} selected decision(s) applied or safely recorded; "
        f"temp cleanup completed; {plan_note}."
    )


def command_validate(args: argparse.Namespace) -> int:
    board_dir = args.board_dir.resolve()
    if getattr(args, "response", None):
        copy_response_to_board(board_dir, args.response)
    elif getattr(args, "collect_response", False):
        collect_response_to_board(board_dir, getattr(args, "response_dir", None))

    marker, response = validate_response(board_dir)
    review = response_application_review(board_dir, response)
    print(
        f"Validated {len(response['decisions'])} decisions for board {marker['boardId']} "
        f"({board_dir})"
    )
    print(f"Next workflow: {review['workflow']}")
    if review["buckets"]["needs_reexplain"]:
        print("Re-explain first: " + ", ".join(review["buckets"]["needs_reexplain"]))
    if review["buckets"]["implementation_plan"]:
        print("Temporary plan required: " + ", ".join(review["buckets"]["implementation_plan"]))
    print("Selected decisions:")
    for decision in review["decisions"]:
        note_flag = " note=yes" if decision["note"] else " note=no"
        status = decision["status"] or "-"
        intent_detail = decision["intentDetail"] or "-"
        print(
            f"- {decision['ledgerId']}: action={decision['action']} "
            f"executionKind={decision['executionKind']} bucket={decision['bucket']} "
            f"status={status} intentDetail={intent_detail}{note_flag}"
        )
    if review["noteConstraints"]:
        print("Plan/external constraints from owner notes:")
        for decision in review["noteConstraints"]:
            print(f"- {decision['ledgerId']}: {decision['note']}")
    if review["closureNotes"]:
        print("Owner notes that may justify ledger-only closure or deferral:")
        for decision in review["closureNotes"]:
            print(f"- {decision['ledgerId']}: {decision['note']}")
    if review["secretChecks"]:
        print("Secret cleanup checks before closure:")
        for decision in review["secretChecks"]:
            print(f"- {decision['ledgerId']}: scan current tree and Git history before marking resolved")
    if getattr(args, "write_plan", False):
        if review["workflow"] == "reexplain_first":
            print("Skipped plan draft: re-explain selected items first.")
        else:
            plan_path = write_application_plan(board_dir, marker, review)
            print(f"Wrote temporary application plan draft: {plan_path}")
    if getattr(args, "write_ledger_suggestions", False):
        suggestions_path = write_ledger_suggestions(board_dir, marker, review)
        print(f"Wrote temporary ledger suggestions: {suggestions_path}")
    return 0


def command_collect_response(args: argparse.Namespace) -> int:
    collect_response_to_board(args.board_dir.resolve(), getattr(args, "response_dir", None))
    return 0


def command_cleanup(args: argparse.Namespace) -> int:
    if not args.confirm_applied:
        raise SystemExit("Refusing cleanup without --confirm-applied")
    board_dir = args.board_dir.resolve()
    marker = read_marker(board_dir)
    validate_board_dir_shape(board_dir, marker)
    if not (board_dir / RESPONSE_NAME).exists():
        raise SystemExit("Refusing cleanup before response JSON exists")
    # Require a valid response before deleting the temporary decision board.
    # The ledger may already have changed because the decisions were applied.
    marker, response = validate_response(board_dir, check_current_ledger_hash=False)
    review = response_application_review(board_dir, response)
    plan_existed = (board_dir / PLAN_NAME).exists()
    suggestions_existed = (board_dir / LEDGER_SUGGESTIONS_NAME).exists()
    shutdown_server_from_state(board_dir, marker)
    shutil.rmtree(board_dir)
    print(f"Deleted temporary ledger triage board: {board_dir}")
    if suggestions_existed:
        print(f"Deleted temporary ledger suggestions: {LEDGER_SUGGESTIONS_NAME}")
    print("Audit Log suggestion:")
    print(audit_log_suggestion(marker, review["selectedCount"], plan_existed, review.get("language", "en")))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and validate Blindspot ledger-triage boards.")
    sub = parser.add_subparsers(dest="command", required=True)

    draft = sub.add_parser("draft", help="Draft board input JSON from an existing ledger")
    draft.add_argument("--project-root", type=Path, required=True)
    draft.add_argument("--ledger", type=Path, required=True)
    draft.add_argument("--out", type=Path, required=True)
    draft.add_argument("--language", default="en")
    draft.add_argument("--board-id", default="")
    draft.add_argument("--project-name", default="")
    draft.add_argument("--title", default="")
    draft.add_argument(
        "--include-ledger-hygiene",
        action="store_true",
        help="Add internal ledger_section candidates for stale version/test/release summary wording.",
    )
    draft.set_defaults(func=command_draft)

    create = sub.add_parser("create", help="Create a temporary HTML decision board")
    create.add_argument("--project-root", type=Path, required=True)
    create.add_argument("--ledger", type=Path, required=True)
    create.add_argument("--data", type=Path, required=True)
    create.add_argument("--serve", action="store_true", help="Serve the created board on localhost in the foreground.")
    create.add_argument("--port", type=int, default=0)
    create.add_argument("--write-url", type=Path, help="Write the served URL to this file when --serve is used.")
    create.add_argument("--write-pid", type=Path, help="Write the serving process PID to this file when --serve is used.")
    create.add_argument("--write-board-dir", type=Path, help="Write the created board directory to this file.")
    create.add_argument(
        "--allow-unreviewed-draft",
        action="store_true",
        help="Explicitly create a board from draftOnly scaffold input; intended for tests and debugging.",
    )
    create.set_defaults(func=command_create)

    serve = sub.add_parser("serve", help="Serve a board on localhost so submit can save response JSON")
    serve.add_argument("--board-dir", type=Path, required=True)
    serve.add_argument("--port", type=int, default=0)
    serve.add_argument("--write-url", type=Path, help="Write the served URL to this file for detached hosts")
    serve.add_argument("--write-pid", type=Path, help="Write the serving process PID to this file for detached hosts")
    serve.add_argument("--write-board-dir", type=Path, help="Write the served board directory to this file")
    serve.set_defaults(func=command_serve)

    validate = sub.add_parser("validate", help="Validate response JSON against marker and ledger hash")
    validate.add_argument("--board-dir", type=Path, required=True)
    validate.add_argument("--response", type=Path, help="Copy this response JSON into the board directory before validating")
    validate.add_argument(
        "--collect-response",
        action="store_true",
        help="Find the newest matching downloaded response JSON before validating",
    )
    validate.add_argument(
        "--response-dir",
        type=Path,
        help="Directory to search with --collect-response; defaults to the user's Downloads folder",
    )
    validate.add_argument("--write-plan", action="store_true")
    validate.add_argument("--write-ledger-suggestions", action="store_true")
    validate.set_defaults(func=command_validate)

    collect = sub.add_parser("collect-response", help="Find and copy a downloaded response JSON into a board directory")
    collect.add_argument("--board-dir", type=Path, required=True)
    collect.add_argument(
        "--from",
        dest="response_dir",
        type=Path,
        help="Directory to search; defaults to the user's Downloads folder",
    )
    collect.set_defaults(func=command_collect_response)

    cleanup = sub.add_parser("cleanup", help="Delete a temporary board after its decisions were applied")
    cleanup.add_argument("--board-dir", type=Path, required=True)
    cleanup.add_argument("--confirm-applied", action="store_true")
    cleanup.set_defaults(func=command_cleanup)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
