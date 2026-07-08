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
import re
import secrets
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


BOARD_SCHEMA = "blindspot-triage-board.v1"
RESPONSE_SCHEMA = "blindspot-triage-response.v1"
MARKER_SCHEMA = "blindspot-triage-tmp.v1"
MARKER_NAME = "BLINDSPOT_TRIAGE_TMP.json"
HTML_NAME = "ledger-triage-board.html"
RESPONSE_NAME = "blindspot-triage-response.json"
PLAN_NAME = "ledger-triage-application-plan.md"
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
    normalized = {
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
            for option in raw_options:
                if not isinstance(option, dict):
                    raise SystemExit(f"Item {ledger_id} has a non-object option")
                options.append(
                    normalize_option(
                        option,
                        recommended,
                        language,
                        item_status,
                        item_intent_detail,
                    )
                )
            if recommended not in {option["action"] for option in options}:
                options.insert(
                    0,
                    normalize_option(
                        {"action": recommended, "recommended": True},
                        recommended,
                        language,
                        item_status,
                        item_intent_detail,
                    ),
                )
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
    data_for_html = {key: value for key, value in board_data.items() if not key.startswith("_")}
    payload = json.dumps(data_for_html, ensure_ascii=False)
    # Script content cannot contain a literal closing script tag.
    payload = payload.replace("</", "<\\/")
    return template.replace("__TRIAGE_BOARD_DATA_JSON__", payload)


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
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def table_value(row: dict[str, str], *names: str) -> str:
    wanted = {normalize_header(name) for name in names}
    for key, value in row.items():
        if normalize_header(key) in wanted:
            return value.strip()
    return ""


def slugify_group_id(value: str) -> str:
    token = safe_path_token(value.lower().replace(" ", "-"))
    return token or "ledger-items"


def first_sentence(value: str, limit: int = 80) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if not text:
        return "Ledger item"
    sentence = re.split(r"(?<=[.!?。])\s+", text, maxsplit=1)[0]
    if len(sentence) <= limit:
        return sentence
    return sentence[: limit - 1].rstrip() + "..."


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


def draft_explanation(language: str) -> tuple[str, str, str]:
    if language_key(language) == "ko":
        return (
            "이 항목은 기존 원장에 열려 있는 항목입니다. 내용을 확인한 뒤 계속 추적할지, 나중으로 미룰지, 하지 않기로 할지, 확인 후 해결 처리할지 고르면 됩니다.",
            "이 항목을 그대로 두면 다음 점검에서도 계속 다시 보게 됩니다. 지금 방향만 정해도 원장이 훨씬 읽기 쉬워집니다.",
            "이 항목을 이번에 어떻게 처리할까요?",
        )
    return (
        "This is an open item from the existing ledger. Decide whether to keep tracking it, defer it, reject it, or treat it as resolved after verification.",
        "If this stays open without a decision, future audits will keep surfacing it. Even a small owner choice can make the ledger easier to use.",
        "How should this item be handled now?",
    )


def parse_ledger_tables(ledger: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    section = ""
    headers: list[str] | None = None
    pending_header: list[str] | None = None
    for raw_line in ledger.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##+\s+(.+?)\s*$", raw_line)
        if heading:
            section = heading.group(1).strip()
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
        rows.append(row)
    return rows


def draft_item_from_row(row: dict[str, str], language: str) -> dict[str, Any] | None:
    section = row.get("_section", "")
    ledger_id = table_value(row, "ID", "Id")
    if not ledger_id:
        return None
    if not re.match(r"^(BS|DP)-\d{8}-\d+", ledger_id):
        return None
    status = table_value(row, "Status", "상태")
    if not status_is_open(status):
        return None
    if section == "Decision Packet":
        summary = table_value(row, "Decision", "Finding", "What")
        recommended_text = table_value(row, "Recommended option", "Recommended", "Recommendation")
        options_text = table_value(row, "Options", "Choices")
        why = table_value(row, "Why it matters", "Why")
        ledger_summary = summary
        if recommended_text:
            ledger_summary += f" Recommended: {recommended_text}."
        if options_text:
            ledger_summary += f" Options: {options_text}."
        if why:
            ledger_summary += f" Why: {why}."
    else:
        summary = table_value(row, "Finding", "Decision", "Item")
        ledger_summary = summary
    if not ledger_summary.strip():
        return None
    awareness = table_value(row, "Awareness", "인지 상태") or "unconfirmed"
    priority = table_value(row, "Priority", "Risk", "우선순위")
    category, execution_kind = classify_draft_item(section, ledger_summary, status)
    explanation, why_it_matters, decision_question = draft_explanation(language)
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
        "recommendedAction": "keep_pending",
        "risk": priority,
    }
    if looks_like_exposed_secret(ledger_summary):
        item["implementationHint"] = "Before closing, verify both current files and Git history for exposed secrets."
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
    return 0


class TriageHandler(http.server.SimpleHTTPRequestHandler):
    board_dir: Path

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        print(f"[ledger-triage-board] {format % args}", file=sys.stderr)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", ""}:
            self.path = f"/{HTML_NAME}"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
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


def command_serve(args: argparse.Namespace) -> int:
    board_dir = args.board_dir.resolve()
    marker = read_marker(board_dir)
    if not (board_dir / marker["htmlFile"]).exists():
        raise SystemExit(f"Missing board HTML: {board_dir / marker['htmlFile']}")

    class BoundTriageHandler(TriageHandler):
        pass

    BoundTriageHandler.board_dir = board_dir
    handler = functools.partial(BoundTriageHandler, directory=str(board_dir))

    class Server(http.server.ThreadingHTTPServer):
        allow_reuse_address = True

    with Server(("127.0.0.1", args.port), handler) as server:
        host, port = server.server_address
        print(f"Open http://{host}:{port}/")
        print("Press Ctrl+C after the owner submits the response.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped ledger triage board server")
    return 0


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
    option_map: dict[str, dict[str, dict[str, Any]]] = {}
    for group in board_data.get("groups") or []:
        if not isinstance(group, dict):
            continue
        for item in group.get("items") or []:
            if not isinstance(item, dict):
                continue
            ledger_id = str(item.get("ledgerId") or "")
            option_map[ledger_id] = {}
            for option in item.get("options") or []:
                if isinstance(option, dict):
                    option_map[ledger_id][str(option.get("action") or "")] = option
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
        option = option_map.get(str(ledger_id), {}).get(str(action))
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
            "title": str(item.get("shortTitle") or ledger_id),
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
        "workflow": workflow,
        "buckets": buckets,
        "selectedCount": len(response.get("decisions") or []),
        "decisions": decision_summaries,
        "noteConstraints": note_constraints,
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
        hint = decision.get("implementationHint") or "TODO: identify files or project areas before editing."
        lines.append(f"- {decision['ledgerId']}: {hint}")
    lines.extend(["", "## Owner Notes As Constraints", ""])
    if review["noteConstraints"]:
        for decision in review["noteConstraints"]:
            lines.append(f"- {decision['ledgerId']}: {decision['note']}")
    else:
        lines.append("- No owner note constraints were submitted.")
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


def audit_log_suggestion(marker: dict[str, Any], selected_count: int, plan_existed: bool) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    plan_note = "temporary plan existed; confirm deleted or outcome recorded" if plan_existed else "no temporary plan remaining"
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
    shutil.rmtree(board_dir)
    print(f"Deleted temporary ledger triage board: {board_dir}")
    print("Audit Log suggestion:")
    print(audit_log_suggestion(marker, review["selectedCount"], plan_existed))
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
    draft.set_defaults(func=command_draft)

    create = sub.add_parser("create", help="Create a temporary HTML decision board")
    create.add_argument("--project-root", type=Path, required=True)
    create.add_argument("--ledger", type=Path, required=True)
    create.add_argument("--data", type=Path, required=True)
    create.add_argument(
        "--allow-unreviewed-draft",
        action="store_true",
        help="Explicitly create a board from draftOnly scaffold input; intended for tests and debugging.",
    )
    create.set_defaults(func=command_create)

    serve = sub.add_parser("serve", help="Serve a board on localhost so submit can save response JSON")
    serve.add_argument("--board-dir", type=Path, required=True)
    serve.add_argument("--port", type=int, default=0)
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
