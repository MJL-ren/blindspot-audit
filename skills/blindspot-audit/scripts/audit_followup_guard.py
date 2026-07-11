#!/usr/bin/env python3
"""Validate blindspot owner-response application without editing the ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from safe_output import safe_display_text
except ModuleNotFoundError as exc:
    if exc.name != "safe_output":
        raise
    raise SystemExit(
        "error: audit_followup_guard.py requires safe_output.py in the same directory; "
        "copy both packaged files together."
    ) from exc


SNAPSHOT_SCHEMA = "blindspot-audit-ledger-snapshot.v1"
OWNER_RESPONSE_SCHEMAS = {
    "blindspot-owner-response.v1",
    "blindspot-owner-response.v2",
}
STABLE_ID_PATTERN = re.compile(r"\b(?:BS|DP|BA)-\d{8}-\d+\b")
BA_ID_PATTERN = re.compile(r"^BA-\d{8}-\d+$")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")

ALLOWED_AWARENESS = {"unknown_unknown", "unknown_known", "unconfirmed"}
ALLOWED_DISPOSITIONS = {
    "pending",
    "accepted",
    "deferred",
    "deliberate_skip",
    "rejected",
    "resolved",
}
ALLOWED_NEXT_ACTION_ROUTES = {
    "none",
    "owner_followup",
    "agent_work",
    "external_confirmation",
}
ALLOWED_VERIFICATION_TIERS = {
    "static-only",
    "ephemeral-local",
    "authorized-dynamic",
}
ALLOWED_EVIDENCE_CHANNELS = {
    "repository",
    "existing-artifact",
    "official-web-readonly",
    "community-web-readonly",
    "owner-provider-confirmation",
}
ALLOWED_VISIBILITY = {"private", "public-safe", "unconfirmed"}
ALLOWED_DETAIL_POLICY = {"full", "generalized"}

DECISION_KEYS = {
    "findingId",
    "awareness",
    "disposition",
    "reason",
    "recheckTrigger",
    "batchId",
    "batchPath",
    "nextActionRoute",
    "nextAction",
}
DECISION_GROUP_KEYS = (DECISION_KEYS - {"findingId"}) | {"findingIds"}
APPLICATION_MAP_KEYS = {
    "idColumn",
    "awarenessColumn",
    "dispositionColumn",
    "awarenessValues",
    "dispositionValues",
    "awarenessMatchModes",
    "dispositionMatchModes",
    "destinations",
}
ALLOWED_APPLICATION_DESTINATIONS = {"row", "archive"}
ALLOWED_MATCH_MODES = {"exact", "annotated"}
ANNOTATION_PREFIXES = (
    "(",
    " (",
    "[",
    " [",
    "{",
    " {",
    ":",
    " - ",
    " — ",
    " – ",
)
SNAPSHOT_FILENAME = "ledger-snapshot.json"


class GuardError(RuntimeError):
    """A safe user-facing guard failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuardError(f"JSON input could not be read or parsed: {path}") from exc
    if not isinstance(value, dict):
        raise GuardError("JSON input must be an object.")
    return value


def resolve_snapshot_input(value: Path) -> Path:
    """Resolve a snapshot marker file, accepting its containing directory too."""
    try:
        resolved = value.expanduser().resolve(strict=True)
    except OSError as exc:
        raise GuardError(f"Snapshot path does not exist: {value}") from exc
    if resolved.is_dir():
        marker = resolved / SNAPSHOT_FILENAME
        if not marker.is_file():
            raise GuardError(
                "Snapshot directory does not contain ledger-snapshot.json; "
                "pass the snapshotPath printed by the snapshot command."
            )
        return marker
    if not resolved.is_file():
        raise GuardError(
            "Snapshot must be the ledger-snapshot.json file printed by the "
            "snapshot command, or its containing directory."
        )
    return resolved


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def resolve_inside(root: Path, value: Path, *, must_exist: bool) -> Path:
    try:
        resolved_root = root.resolve(strict=True)
        resolved = value.resolve(strict=must_exist)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise GuardError("Requested path must stay inside the project root.") from exc
    return resolved


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
    if not text.startswith("|"):
        return []
    if text.endswith("|"):
        text = text[1:-1]
    else:
        text = text[1:]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in text:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            current.append(character)
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    cells.append("".join(current).strip())
    return cells


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_PATTERN.fullmatch(cell) for cell in cells)


def extract_markdown_tables(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    tables: list[dict[str, Any]] = []
    heading = ""
    index = 0

    while index < len(lines):
        heading_match = re.match(r"^#{1,6}\s+(.+?)\s*$", lines[index])
        if heading_match:
            heading = heading_match.group(1)

        if index + 1 >= len(lines):
            break
        headers = split_markdown_row(lines[index])
        separator = split_markdown_row(lines[index + 1])
        if not headers or len(headers) != len(separator) or not is_separator_row(separator):
            index += 1
            continue

        rows: list[list[str]] = []
        cursor = index + 2
        while cursor < len(lines):
            row = split_markdown_row(lines[cursor])
            if not row:
                break
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            rows.append(row[: len(headers)])
            cursor += 1

        tables.append(
            {
                "index": len(tables),
                "heading": heading,
                "headers": headers,
                "rows": rows,
            }
        )
        index = cursor

    return tables


def table_schemas(text: str) -> list[dict[str, Any]]:
    return [
        {
            "index": table["index"],
            "heading": table["heading"],
            "headers": table["headers"],
        }
        for table in extract_markdown_tables(text)
    ]


def protected_finding_table_schemas(text: str) -> list[dict[str, Any]]:
    """Capture only tables that define findings, preserving localized headings."""
    heading_occurrences: dict[str, int] = defaultdict(int)
    protected: list[dict[str, Any]] = []
    for table in extract_markdown_tables(text):
        occurrence = heading_occurrences[table["heading"]]
        heading_occurrences[table["heading"]] += 1
        finding_ids = [
            row[0].strip()
            for row in table["rows"]
            if row and re.fullmatch(r"BS-\d{8}-\d+", row[0].strip())
        ]
        if not finding_ids:
            continue
        protected.append(
            {
                "heading": table["heading"],
                "headingOccurrence": occurrence,
                "headers": table["headers"],
                "baselineFindingIds": finding_ids,
            }
        )
    return protected


def defined_stable_ids(text: str) -> list[str]:
    definitions: list[str] = []
    for table in extract_markdown_tables(text):
        for row in table["rows"]:
            if not row:
                continue
            first_cell = row[0].strip()
            if STABLE_ID_PATTERN.fullmatch(first_cell):
                definitions.append(first_cell)

    for line in text.splitlines():
        match = re.match(r"^\s*(?:#{1,6}\s+|[-*+]\s+)((?:BS|DP|BA)-\d{8}-\d+)\b", line)
        if match:
            definitions.append(match.group(1))
    return definitions


def run_git(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[bytes] | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    return completed


def git_baseline(ledger: Path) -> dict[str, Any]:
    repository = run_git(ledger.parent, ["rev-parse", "--show-toplevel"])
    if repository is None or repository.returncode != 0:
        return {"available": False}

    try:
        repo_root = Path(repository.stdout.decode("utf-8").strip()).resolve(strict=True)
        relative = ledger.resolve(strict=True).relative_to(repo_root).as_posix()
    except (OSError, ValueError):
        return {"available": False}

    status = run_git(repo_root, ["status", "--short", "--", relative])
    unstaged = run_git(repo_root, ["diff", "--", relative])
    staged = run_git(repo_root, ["diff", "--cached", "--", relative])
    tracked = run_git(repo_root, ["ls-files", "--error-unmatch", "--", relative])
    if status is None or unstaged is None or staged is None or tracked is None:
        return {"available": False}

    return {
        "available": True,
        "repoRoot": str(repo_root),
        "ledgerRelativePath": relative,
        "tracked": tracked.returncode == 0,
        "hadTargetStatus": bool(status.stdout.strip()),
        "hadUnstagedChanges": bool(unstaged.stdout),
        "hadStagedChanges": bool(staged.stdout),
        "statusHash": sha256_bytes(status.stdout),
        "unstagedDiffHash": sha256_bytes(unstaged.stdout),
        "stagedDiffHash": sha256_bytes(staged.stdout),
    }


def default_snapshot_path(project_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    return (
        project_root
        / ".blindspot-tmp"
        / f"audit-followup-{timestamp}-{token}"
        / "ledger-snapshot.json"
    )


def validate_snapshot_destination(project_root: Path, destination: Path) -> Path:
    resolved = resolve_inside(project_root, destination, must_exist=False)
    expected_parent = project_root.resolve() / ".blindspot-tmp"
    try:
        relative = resolved.relative_to(expected_parent)
    except ValueError as exc:
        raise GuardError("Snapshot must live under .blindspot-tmp/audit-followup-*.") from exc
    if not relative.parts or not relative.parts[0].startswith("audit-followup-"):
        raise GuardError("Snapshot directory must match audit-followup-*.")
    return resolved


def create_snapshot(project_root: Path, ledger: Path, destination: Path) -> dict[str, Any]:
    root = project_root.resolve(strict=True)
    ledger_path = resolve_inside(root, ledger, must_exist=True)
    if not ledger_path.is_file():
        raise GuardError("Ledger path must be a file.")
    destination = validate_snapshot_destination(root, destination)
    ensure_tmp_gitignore(root / ".blindspot-tmp")

    ledger_text = ledger_path.read_text(encoding="utf-8")
    ids = defined_stable_ids(ledger_text)
    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "snapshotId": uuid.uuid4().hex,
        "createdAt": utc_now(),
        "projectRoot": str(root),
        "ledgerPath": str(ledger_path),
        "ledgerRelativePath": ledger_path.relative_to(root).as_posix(),
        "ledgerHash": sha256_text(ledger_text),
        "tableSchemas": table_schemas(ledger_text),
        "protectedFindingTableSchemas": protected_finding_table_schemas(ledger_text),
        "definedStableIds": sorted(set(ids)),
        "duplicateDefinedIds": sorted(
            stable_id for stable_id, count in Counter(ids).items() if count > 1
        ),
        "gitBaseline": git_baseline(ledger_path),
        "validatedAt": None,
    }
    write_json(destination, snapshot)
    return {"snapshotPath": str(destination), "snapshot": snapshot}


def optional_string(value: Any, field: str, errors: list[str]) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        errors.append(f"{field} must be a string or null")
        return ""
    return value.strip()


def expand_decision_inputs(
    data: dict[str, Any],
    schema: str,
    errors: list[str],
) -> list[tuple[str, dict[str, Any]]]:
    expanded: list[tuple[str, dict[str, Any]]] = []

    decisions_raw = data.get("decisions", [])
    if not isinstance(decisions_raw, list):
        errors.append("decisions must be an array")
        decisions_raw = []
    for index, raw in enumerate(decisions_raw, start=1):
        prefix = f"decisions[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be an object")
            continue
        expanded.append((prefix, raw))

    groups_raw = data.get("decisionGroups", [])
    if schema == "blindspot-owner-response.v1":
        if "decisionGroups" in data:
            errors.append("decisionGroups requires blindspot-owner-response.v2")
        groups_raw = []
    elif not isinstance(groups_raw, list):
        errors.append("decisionGroups must be an array")
        groups_raw = []

    for group_index, raw_group in enumerate(groups_raw, start=1):
        prefix = f"decisionGroups[{group_index}]"
        if not isinstance(raw_group, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unknown_keys = set(raw_group) - DECISION_GROUP_KEYS
        if unknown_keys:
            errors.append(
                f"{prefix} has unknown fields: {', '.join(sorted(unknown_keys))}"
            )
        finding_ids = raw_group.get("findingIds")
        if not isinstance(finding_ids, list) or not finding_ids:
            errors.append(f"{prefix}.findingIds must be a non-empty array")
            continue
        common = {key: value for key, value in raw_group.items() if key != "findingIds"}
        for id_index, finding_id in enumerate(finding_ids, start=1):
            raw = dict(common)
            raw["findingId"] = finding_id
            expanded.append((f"{prefix}.findingIds[{id_index}]", raw))

    if not expanded:
        errors.append("decisions or decisionGroups must contain at least one decision")
    return expanded


def normalize_value_map(
    value: Any,
    field: str,
    allowed_keys: set[str],
    errors: list[str],
) -> dict[str, str]:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {}
    result: dict[str, str] = {}
    for key, mapped in value.items():
        if key not in allowed_keys:
            errors.append(f"{field} has unsupported canonical value: {key}")
            continue
        if not isinstance(mapped, str) or not mapped.strip():
            errors.append(f"{field}.{key} must be a non-empty string")
            continue
        result[key] = mapped.strip()
    return result


def normalize_match_modes(
    value: Any,
    field: str,
    allowed_keys: set[str],
    errors: list[str],
) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {}
    result: dict[str, str] = {}
    for key, mode in value.items():
        if key not in allowed_keys:
            errors.append(f"{field} has unsupported canonical value: {key}")
            continue
        if mode not in ALLOWED_MATCH_MODES:
            errors.append(f"{field}.{key} must be exact or annotated")
            continue
        result[key] = mode
    return result


def normalize_application_map(
    value: Any,
    decision_ids: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append("applicationMap must be an object")
        return None
    unknown_keys = set(value) - APPLICATION_MAP_KEYS
    if unknown_keys:
        errors.append(
            "applicationMap has unknown fields: " + ", ".join(sorted(unknown_keys))
        )

    columns: dict[str, str] = {}
    for field in ("idColumn", "awarenessColumn", "dispositionColumn"):
        columns[field] = optional_string(value.get(field), f"applicationMap.{field}", errors)
        if not columns[field]:
            errors.append(f"applicationMap.{field} is required")

    awareness_values = normalize_value_map(
        value.get("awarenessValues", {}),
        "applicationMap.awarenessValues",
        ALLOWED_AWARENESS,
        errors,
    )
    disposition_values = normalize_value_map(
        value.get("dispositionValues", {}),
        "applicationMap.dispositionValues",
        ALLOWED_DISPOSITIONS,
        errors,
    )
    awareness_match_modes = normalize_match_modes(
        value.get("awarenessMatchModes"),
        "applicationMap.awarenessMatchModes",
        ALLOWED_AWARENESS,
        errors,
    )
    disposition_match_modes = normalize_match_modes(
        value.get("dispositionMatchModes"),
        "applicationMap.dispositionMatchModes",
        ALLOWED_DISPOSITIONS,
        errors,
    )

    destinations_raw = value.get("destinations", {})
    destinations: dict[str, str] = {}
    if not isinstance(destinations_raw, dict):
        errors.append("applicationMap.destinations must be an object")
    else:
        for finding_id, destination in destinations_raw.items():
            if finding_id not in decision_ids:
                errors.append(
                    f"applicationMap.destinations has unknown decision ID: {finding_id}"
                )
                continue
            if destination not in ALLOWED_APPLICATION_DESTINATIONS:
                errors.append(
                    f"applicationMap.destinations.{finding_id} must be row or archive"
                )
                continue
            destinations[finding_id] = destination

    return {
        **columns,
        "awarenessValues": awareness_values,
        "dispositionValues": disposition_values,
        "awarenessMatchModes": awareness_match_modes,
        "dispositionMatchModes": disposition_match_modes,
        "destinations": destinations,
    }


def validate_owner_response(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    schema = data.get("schema")
    if schema not in OWNER_RESPONSE_SCHEMAS:
        errors.append(
            "schema must be blindspot-owner-response.v1 or "
            "blindspot-owner-response.v2"
        )
        schema = ""
    if data.get("ownerResponseRecorded") is not True:
        errors.append("ownerResponseRecorded must be true before preview/application")

    audit_run_id = data.get("auditRunId")
    if not isinstance(audit_run_id, str) or not BA_ID_PATTERN.fullmatch(audit_run_id):
        errors.append("auditRunId must match BA-YYYYMMDD-NN")

    expected_raw = data.get("expectedFindingIds")
    if not isinstance(expected_raw, list) or not expected_raw:
        errors.append("expectedFindingIds must be a non-empty array")
        expected_ids: list[str] = []
    else:
        expected_ids = []
        for value in expected_raw:
            if not isinstance(value, str) or not re.fullmatch(r"BS-\d{8}-\d+", value):
                errors.append("expectedFindingIds contains an invalid finding ID")
                continue
            expected_ids.append(value)
        if len(expected_ids) != len(set(expected_ids)):
            errors.append("expectedFindingIds contains duplicates")

    unmapped = data.get("unmappedReferences", [])
    if not isinstance(unmapped, list):
        errors.append("unmappedReferences must be an array")
    elif unmapped:
        errors.append("unmappedReferences must be resolved before ledger edits")

    expanded_inputs = expand_decision_inputs(data, schema, errors)
    decisions: list[dict[str, Any]] = []
    seen: set[str] = set()

    for prefix, raw in expanded_inputs:
        unknown_keys = set(raw) - DECISION_KEYS
        if unknown_keys:
            errors.append(f"{prefix} has unknown fields: {', '.join(sorted(unknown_keys))}")

        finding_id = raw.get("findingId")
        if not isinstance(finding_id, str) or not re.fullmatch(r"BS-\d{8}-\d+", finding_id):
            errors.append(f"{prefix}.findingId is invalid")
            continue
        if finding_id in seen:
            errors.append(f"duplicate decision for {finding_id}")
            continue
        seen.add(finding_id)
        if expected_ids and finding_id not in expected_ids:
            errors.append(f"decision ID is not in expectedFindingIds: {finding_id}")

        awareness = raw.get("awareness")
        if awareness is not None and awareness not in ALLOWED_AWARENESS:
            errors.append(f"{finding_id}: invalid awareness")
        disposition = raw.get("disposition")
        if disposition is not None and disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{finding_id}: invalid disposition")

        reason = optional_string(raw.get("reason"), f"{prefix}.reason", errors)
        trigger = optional_string(
            raw.get("recheckTrigger"), f"{prefix}.recheckTrigger", errors
        )
        batch_id = optional_string(raw.get("batchId"), f"{prefix}.batchId", errors)
        batch_path = optional_string(raw.get("batchPath"), f"{prefix}.batchPath", errors)
        route = raw.get("nextActionRoute", "none")
        if route not in ALLOWED_NEXT_ACTION_ROUTES:
            errors.append(f"{finding_id}: invalid nextActionRoute")
            route = "none"
        next_action = optional_string(
            raw.get("nextAction"), f"{prefix}.nextAction", errors
        )

        if awareness is None and disposition is None and route == "none":
            errors.append(f"{finding_id}: decision has no awareness, disposition, or next action")
        if disposition == "deliberate_skip" and (not reason or not trigger):
            errors.append(f"{finding_id}: deliberate_skip requires reason and recheckTrigger")
        if disposition == "deferred" and not (reason or trigger or batch_id):
            errors.append(f"{finding_id}: deferred requires reason, trigger, or batchId")
        if disposition == "resolved" and not reason:
            errors.append(f"{finding_id}: resolved requires an evidence/reason summary")
        if route == "owner_followup" and not next_action:
            errors.append(f"{finding_id}: owner_followup requires nextAction")
        if route != "none" and not next_action:
            errors.append(f"{finding_id}: nextActionRoute requires nextAction")
        if batch_id and disposition != "deferred":
            errors.append(f"{finding_id}: batchId is allowed only with deferred disposition")
        if batch_path and not batch_id:
            errors.append(f"{finding_id}: batchPath requires batchId")

        decision = {
            "findingId": finding_id,
            "awareness": awareness,
            "disposition": disposition,
            "reason": reason,
            "recheckTrigger": trigger,
            "batchId": batch_id,
            "batchPath": batch_path,
            "nextActionRoute": route,
            "nextAction": next_action,
        }
        decisions.append(decision)

    expected_order = {finding_id: index for index, finding_id in enumerate(expected_ids)}
    decisions.sort(
        key=lambda item: (
            expected_order.get(item["findingId"], len(expected_order)),
            item["findingId"],
        )
    )

    application_map = normalize_application_map(
        data.get("applicationMap"),
        {item["findingId"] for item in decisions},
        errors,
    )

    omitted = sorted(set(expected_ids) - seen)
    if omitted:
        warnings.append("No response delta for: " + ", ".join(omitted))

    batches: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        if decision["batchId"]:
            batches[decision["batchId"]].append(decision)

    batch_requirements: list[dict[str, Any]] = []
    for batch_id, batch_decisions in sorted(batches.items()):
        paths = {item["batchPath"] for item in batch_decisions if item["batchPath"]}
        if len(paths) > 1:
            errors.append(f"batch {batch_id} has conflicting batchPath values")
        path = next(iter(paths), "")
        if len(batch_decisions) >= 2 and not path:
            errors.append(f"batch {batch_id} has 2+ deferred findings but no batchPath")
        if len(batch_decisions) == 1:
            warnings.append(f"batch {batch_id} has one finding; durable handoff is optional")
        batch_requirements.append(
            {
                "batchId": batch_id,
                "findingIds": [item["findingId"] for item in batch_decisions],
                "batchPath": path,
                "handoffRequired": len(batch_decisions) >= 2,
            }
        )

    return {
        "schema": "blindspot-owner-response-preview.v1",
        "ownerResponseSchema": schema,
        "auditRunId": audit_run_id,
        "ledgerEdits": "none-preview-only",
        "decisions": decisions,
        "applicationMap": application_map,
        "batchRequirements": batch_requirements,
        "warnings": warnings,
        "errors": errors,
        "valid": not errors,
    }


def render_preview(preview: dict[str, Any]) -> str:
    lines = [
        "Owner response delta preview",
        f"Audit run: {preview.get('auditRunId') or '-'}",
        "Ledger edits: none (preview only)",
        "",
        "ID | Awareness | Disposition | Next route | Batch | Reason/trigger",
        "--- | --- | --- | --- | --- | ---",
    ]
    for decision in preview["decisions"]:
        reason_state = "/".join(
            value
            for value in (
                "reason" if decision["reason"] else "",
                "trigger" if decision["recheckTrigger"] else "",
            )
            if value
        ) or "-"
        lines.append(
            " | ".join(
                [
                    safe_display_text(decision["findingId"]),
                    safe_display_text(decision["awareness"] or "unchanged"),
                    safe_display_text(decision["disposition"] or "unchanged"),
                    safe_display_text(decision["nextActionRoute"]),
                    safe_display_text(decision["batchId"] or "-"),
                    reason_state,
                ]
            )
        )
    if preview["batchRequirements"]:
        lines.extend(["", "Batch requirements:"])
        for batch in preview["batchRequirements"]:
            required = "required" if batch["handoffRequired"] else "optional"
            lines.append(
                f"- {safe_display_text(batch['batchId'])}: {required}; "
                f"IDs={safe_display_text(','.join(batch['findingIds']))}; "
                f"path={safe_display_text(batch['batchPath'] or '-')}"
            )
    if preview.get("applicationMappings"):
        lines.extend(["", "Application targets:"])
        for mapping in preview["applicationMappings"]:
            lines.append(
                f"- {safe_display_text(mapping['findingId'])}: "
                f"{safe_display_text(mapping['destination'])} via "
                f"{safe_display_text(mapping['adapter'])} adapter"
            )
    if preview["warnings"]:
        lines.extend(
            ["", "Warnings:"]
            + [f"- {safe_display_text(item)}" for item in preview["warnings"]]
        )
    if preview["errors"]:
        lines.extend(
            ["", "Blocking errors:"]
            + [f"- {safe_display_text(item)}" for item in preview["errors"]]
        )
    lines.append("")
    lines.append("Result: VALID" if preview["valid"] else "Result: BLOCKED")
    return "\n".join(lines)


def schema_changes(before: list[dict[str, Any]], after_text: str) -> list[str]:
    changes: list[str] = []
    after_by_heading: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table in extract_markdown_tables(after_text):
        after_by_heading[table["heading"]].append(table)

    for protected in before:
        heading = protected["heading"]
        occurrence = protected["headingOccurrence"]
        candidates = after_by_heading.get(heading, [])
        if occurrence >= len(candidates):
            changes.append(
                f"protected finding table removed under heading {heading!r} "
                f"(occurrence {occurrence + 1})"
            )
            continue
        current = candidates[occurrence]
        if protected["headers"] != current["headers"]:
            changes.append(
                f"finding table headers changed under heading {heading!r}: "
                f"{protected['headers']} -> {current['headers']}"
            )
    return changes


def parse_field(text: str, name: str) -> str:
    match = re.search(rf"(?mi)^{re.escape(name)}:\s*([^\r\n]+)$", text)
    return match.group(1).strip() if match else ""


def normalize_table_header(value: str) -> str:
    return " ".join(value.strip().strip("`").casefold().split())


def verification_column_indexes(table: dict[str, Any]) -> dict[str, int] | None:
    normalized = [normalize_table_header(value) for value in table["headers"]]
    required = {
        "finding": "finding",
        "tier": "verification tier",
        "channel": "evidence channel",
    }
    if not all(header in normalized for header in required.values()):
        return None
    if any(normalized.count(header) != 1 for header in required.values()):
        return None
    return {key: normalized.index(header) for key, header in required.items()}


def canonical_enum_cell(value: str, allowed: set[str]) -> str | None:
    normalized = value.strip().strip("`")
    return normalized if normalized in allowed else None


def local_path_markers(text: str, project_root: Path) -> list[str]:
    markers: list[str] = []
    patterns = (
        ("Windows drive path", re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]")),
        ("file URL", re.compile(r"(?i)\bfile://")),
        ("UNC path", re.compile(r"(?:^|[\s(`'\"])\\\\[^\\\s]+[\\/]", re.MULTILINE)),
        ("UNC-style path", re.compile(r"(?<!:)//[A-Za-z0-9._-]+/")),
        ("local home path", re.compile(r"(?i)(?:^|[\s(`'\"])/(?:users|home|root)/", re.MULTILINE)),
        ("tilde home path", re.compile(r"(?:^|[\s(`'\"])~[\\/]", re.MULTILINE)),
    )
    for label, pattern in patterns:
        if pattern.search(text):
            markers.append(label)

    root_variants = {
        str(project_root),
        str(project_root).replace("\\", "/"),
    }
    if any(value and value in text for value in root_variants):
        markers.append("project absolute path")
    return sorted(set(markers))


def normalized_cell(value: str) -> str:
    return value.strip().strip("`").strip()


def mapped_value_matches(actual: str, expected: str, mode: str) -> bool:
    if actual == expected:
        return True
    if mode != "annotated":
        return False
    return any(actual.startswith(expected + prefix) for prefix in ANNOTATION_PREFIXES)


def application_column_indexes(
    table: dict[str, Any],
    adapter: dict[str, Any],
) -> dict[str, int] | None:
    normalized = [normalize_table_header(value) for value in table["headers"]]
    requested = {
        "id": normalize_table_header(adapter["idColumn"]),
        "awareness": normalize_table_header(adapter["awarenessColumn"]),
        "disposition": normalize_table_header(adapter["dispositionColumn"]),
    }
    if not all(value in normalized for value in requested.values()):
        return None
    if any(normalized.count(value) != 1 for value in requested.values()):
        return None
    return {key: normalized.index(value) for key, value in requested.items()}


def standard_application_adapter(ledger_text: str) -> dict[str, Any] | None:
    candidate = {
        "idColumn": "ID",
        "awarenessColumn": "Awareness",
        "dispositionColumn": "Status",
        "awarenessValues": {value: value for value in ALLOWED_AWARENESS},
        "dispositionValues": {value: value for value in ALLOWED_DISPOSITIONS},
        "awarenessMatchModes": {},
        "dispositionMatchModes": {
            value: "annotated" for value in ALLOWED_DISPOSITIONS
        },
        "destinations": {},
    }
    if any(
        application_column_indexes(table, candidate) is not None
        for table in extract_markdown_tables(ledger_text)
    ):
        return candidate
    return None


def validate_applied_decisions(
    ledger_text: str,
    preview: dict[str, Any],
    *,
    compare_values: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    decisions = [
        decision
        for decision in preview.get("decisions", [])
        if decision.get("awareness") is not None
        or decision.get("disposition") is not None
    ]
    if not decisions:
        return [], []

    adapter = preview.get("applicationMap")
    adapter_source = "explicit"
    if adapter is None:
        adapter = standard_application_adapter(ledger_text)
        adapter_source = "standard"
    if adapter is None:
        return [], [
            "ledger uses a non-standard finding schema; response applicationMap "
            "must name the exact ID, awareness, and disposition columns plus "
            "canonical-to-ledger value mappings"
        ]

    tables_with_indexes: list[tuple[dict[str, Any], dict[str, int]]] = []
    for table in extract_markdown_tables(ledger_text):
        indexes = application_column_indexes(table, adapter)
        if indexes is not None:
            tables_with_indexes.append((table, indexes))
    if not tables_with_indexes:
        return [], [
            "applicationMap columns do not match one finding table in the ledger"
        ]

    errors: list[str] = []
    mappings: list[dict[str, Any]] = []
    defined_ids = set(defined_stable_ids(ledger_text))

    for decision in decisions:
        finding_id = decision["findingId"]
        destination = adapter.get("destinations", {}).get(finding_id, "row")
        mapping: dict[str, Any] = {
            "findingId": finding_id,
            "adapter": adapter_source,
            "destination": destination,
            "tableHeading": None,
            "awareness": None,
            "disposition": None,
        }
        matches: list[tuple[dict[str, Any], dict[str, int], list[str]]] = []
        for table, indexes in tables_with_indexes:
            for row in table["rows"]:
                if normalized_cell(row[indexes["id"]]) == finding_id:
                    matches.append((table, indexes, row))

        if destination == "archive":
            if decision.get("disposition") not in {"resolved", "rejected"}:
                errors.append(
                    f"{finding_id}: archive destination requires resolved or rejected disposition"
                )
            if compare_values:
                if matches:
                    errors.append(
                        f"{finding_id}: expected archive destination but finding row is still open"
                    )
                if finding_id not in defined_ids:
                    errors.append(
                        f"{finding_id}: archive destination no longer defines the stable ID"
                    )
            mapping["disposition"] = {
                "expected": decision.get("disposition"),
                "actual": "archive" if compare_values and not matches else "open-row",
                "applied": (not matches and finding_id in defined_ids) if compare_values else None,
            }
            if decision.get("awareness") is not None:
                mapping["awareness"] = {
                    "expected": decision["awareness"],
                    "actual": "not-retained-in-archive",
                    "applied": None,
                }
            mappings.append(mapping)
            continue

        if len(matches) != 1:
            if not matches:
                errors.append(f"{finding_id}: application target row was not found")
            else:
                errors.append(f"{finding_id}: application target row is ambiguous")
            mappings.append(mapping)
            continue

        table, indexes, row = matches[0]
        mapping["tableHeading"] = table["heading"]
        for axis, value_key, mode_key, index_key, column_key in (
            (
                "awareness",
                "awarenessValues",
                "awarenessMatchModes",
                "awareness",
                "awarenessColumn",
            ),
            (
                "disposition",
                "dispositionValues",
                "dispositionMatchModes",
                "disposition",
                "dispositionColumn",
            ),
        ):
            canonical = decision.get(axis)
            if canonical is None:
                continue
            expected = adapter[value_key].get(canonical)
            if expected is None:
                errors.append(
                    f"{finding_id}: applicationMap has no {axis} value for {canonical}"
                )
                mapping[axis] = {
                    "column": adapter[column_key],
                    "expected": None,
                    "actual": normalized_cell(row[indexes[index_key]]),
                    "applied": False if compare_values else None,
                }
                continue
            actual = normalized_cell(row[indexes[index_key]])
            match_mode = adapter.get(mode_key, {}).get(canonical, "exact")
            applied = (
                mapped_value_matches(actual, expected, match_mode)
                if compare_values
                else None
            )
            mapping[axis] = {
                "column": adapter[column_key],
                "expected": expected,
                "actual": actual,
                "matchMode": match_mode,
                "applied": applied,
            }
            if compare_values and not applied:
                errors.append(
                    f"{finding_id}: {axis} was not applied; expected {expected!r}, "
                    f"found {actual!r}"
                )
        mappings.append(mapping)

    return mappings, errors


def validate_batch_handoff(
    project_root: Path,
    ledger_text: str,
    requirement: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not requirement["handoffRequired"]:
        return errors
    raw_path = requirement["batchPath"]
    if not raw_path:
        return [f"batch {requirement['batchId']}: batchPath is required"]

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    try:
        batch_path = resolve_inside(project_root, candidate, must_exist=True)
    except GuardError:
        return [f"batch {requirement['batchId']}: path is missing or outside project root"]
    if ".blindspot-tmp" in batch_path.parts:
        errors.append(f"batch {requirement['batchId']}: durable handoff cannot live in .blindspot-tmp")
        return errors
    if not batch_path.is_file():
        return [f"batch {requirement['batchId']}: batchPath is not a file"]

    relative = batch_path.relative_to(project_root).as_posix()
    if batch_path.name not in ledger_text and relative not in ledger_text:
        errors.append(f"batch {requirement['batchId']}: ledger backlink is missing")

    batch_text = batch_path.read_text(encoding="utf-8")
    visibility = parse_field(batch_text, "Visibility")
    detail_policy = parse_field(batch_text, "Detail policy")
    if visibility not in ALLOWED_VISIBILITY:
        errors.append(f"batch {requirement['batchId']}: invalid or missing Visibility")
    if detail_policy not in ALLOWED_DETAIL_POLICY:
        errors.append(f"batch {requirement['batchId']}: invalid or missing Detail policy")
    if visibility in {"public-safe", "unconfirmed"} and detail_policy != "generalized":
        errors.append(
            f"batch {requirement['batchId']}: public-safe/unconfirmed requires generalized detail"
        )
    if visibility in {"public-safe", "unconfirmed"}:
        path_markers = local_path_markers(batch_text, project_root)
        if path_markers:
            errors.append(
                f"batch {requirement['batchId']}: public-safe/unconfirmed handoff "
                "contains local absolute path markers: " + ", ".join(path_markers)
            )

    finding_ids = requirement["findingIds"]
    for finding_id in finding_ids:
        if finding_id not in batch_text:
            errors.append(f"batch {requirement['batchId']}: missing finding {finding_id}")

    verification_tables: list[tuple[dict[str, Any], dict[str, int]]] = []
    for table in extract_markdown_tables(batch_text):
        indexes = verification_column_indexes(table)
        if indexes is not None:
            verification_tables.append((table, indexes))
    if not verification_tables:
        errors.append(
            f"batch {requirement['batchId']}: verification matrix with canonical "
            "Finding, Verification tier, and Evidence channel headers is missing"
        )
        return errors

    covered_ids: set[str] = set()
    for table, indexes in verification_tables:
        for row in table["rows"]:
            finding_cell = row[indexes["finding"]]
            row_ids = {
                finding_id for finding_id in finding_ids if finding_id in finding_cell
            }
            if not row_ids:
                continue
            tier = canonical_enum_cell(
                row[indexes["tier"]], ALLOWED_VERIFICATION_TIERS
            )
            channel = canonical_enum_cell(
                row[indexes["channel"]], ALLOWED_EVIDENCE_CHANNELS
            )
            if tier is None:
                errors.append(
                    f"batch {requirement['batchId']}: verification row for "
                    f"{','.join(sorted(row_ids))} must contain exactly one tier "
                    "in the Verification tier cell"
                )
            if channel is None:
                errors.append(
                    f"batch {requirement['batchId']}: verification row for "
                    f"{','.join(sorted(row_ids))} must contain exactly one evidence "
                    "channel in the Evidence channel cell"
                )
            if tier is not None and channel is not None:
                covered_ids.update(row_ids)
    for finding_id in sorted(set(finding_ids) - covered_ids):
        errors.append(
            f"batch {requirement['batchId']}: no valid verification row for {finding_id}"
        )
    return errors


def security_batch_scaffold_text(
    *,
    audit_run_id: str,
    batch_id: str,
    finding_ids: list[str],
    ledger_relative: str,
    batch_relative: str,
    visibility: str,
    detail_policy: str,
) -> str:
    included_rows = "\n".join(
        f"| {finding_id} | <everyday consequence> | <target surface/copies> | "
        "deferred | <decision or none> |"
        for finding_id in finding_ids
    )
    verification_rows = "\n".join(
        f"| {finding_id} | <one smallest closing check> | <choose one tier> | "
        "<choose one channel> | <observable result> | pending |"
        for finding_id in finding_ids
    )
    return f"""# Security Batch: {batch_id}

Status: deferred
Source audit: {audit_run_id}
Owner decision: The included findings were deferred as one named security batch.
Ledger: {ledger_relative}
Visibility: {visibility}
Detail policy: {detail_policy}

This is a lightweight restart document. Keep detailed evidence in the ledger.
Do not add secret values, private payloads, or unnecessary provider identifiers.

## Start Here

Read the included ledger rows, confirm that their evidence is still current,
then continue from the first unchecked execution step. Do not rerun a full
blindspot audit unless the owner asks for one.

## Included Findings

| ID | Everyday consequence | Target surface/copies | Current disposition | Depends on |
| --- | --- | --- | --- | --- |
{included_rows}

## Execution Order

1. <contain or close the highest-impact exposed boundary>
2. <update shared enforcement or dependency points>
3. <finish lower-risk hardening and documentation>

## Decisions Needed First

- <decision, owner, options, and default if already chosen>

## Verification Matrix

Use one check, one verification tier, and one evidence channel per row. Repeat
a finding ID when it needs separate repository and provider checks. Replace the
placeholders below before final validation.

| Finding | Check | Verification tier | Evidence channel | Pass condition | Result |
| --- | --- | --- | --- | --- | --- |
{verification_rows}

## Done When

- Every included ID has a boundary-specific or copy-specific verification result.
- Provider/runtime unknowns are confirmed or remain open with an owner and trigger.
- The ledger records the owner choice, result, and final disposition.
- This file is deleted or archived after its restart value is gone.

## Next Session Start

Continue the security batch in `{batch_relative}`. Read `{ledger_relative}` and
the included IDs first, then execute the next unchecked step. Do not open a new
audit or change unrelated ledger rows.
"""


def scaffold_security_batch(
    project_root: Path,
    ledger: Path,
    response_path: Path,
    *,
    batch_id: str | None,
    visibility: str,
    detail_policy: str,
) -> dict[str, Any]:
    root = project_root.resolve(strict=True)
    ledger_path = resolve_inside(root, ledger, must_exist=True)
    response = load_json(response_path)
    preview = validate_owner_response(response)
    if not preview["valid"]:
        raise GuardError(
            "Owner response is not structurally valid: " + "; ".join(preview["errors"])
        )

    requirements = [
        requirement
        for requirement in preview["batchRequirements"]
        if requirement["handoffRequired"]
    ]
    if batch_id:
        requirements = [
            requirement
            for requirement in requirements
            if requirement["batchId"] == batch_id
        ]
    if not requirements:
        raise GuardError("No 2+-finding deferred security batch matches the request.")
    if len(requirements) > 1:
        raise GuardError("Multiple security batches exist; pass --batch-id.")
    requirement = requirements[0]
    raw_batch_path = requirement["batchPath"]
    if not raw_batch_path:
        raise GuardError("Selected security batch has no batchPath.")

    batch_candidate = Path(raw_batch_path)
    if not batch_candidate.is_absolute():
        batch_candidate = root / batch_candidate
    batch_path = resolve_inside(root, batch_candidate, must_exist=False)
    if ".blindspot-tmp" in batch_path.parts:
        raise GuardError("Security batch handoff must be durable, not temporary.")
    if batch_path.exists():
        raise GuardError("Security batch handoff already exists; refusing to overwrite it.")
    if visibility not in ALLOWED_VISIBILITY:
        raise GuardError("Visibility is invalid.")
    if detail_policy not in ALLOWED_DETAIL_POLICY:
        raise GuardError("Detail policy is invalid.")
    if visibility in {"public-safe", "unconfirmed"} and detail_policy != "generalized":
        raise GuardError("public-safe/unconfirmed requires generalized detail.")

    ledger_relative = ledger_path.relative_to(root).as_posix()
    batch_relative = batch_path.relative_to(root).as_posix()
    content = security_batch_scaffold_text(
        audit_run_id=preview["auditRunId"],
        batch_id=requirement["batchId"],
        finding_ids=requirement["findingIds"],
        ledger_relative=ledger_relative,
        batch_relative=batch_relative,
        visibility=visibility,
        detail_policy=detail_policy,
    )
    if visibility in {"public-safe", "unconfirmed"} and local_path_markers(
        content, root
    ):
        raise GuardError("Generated public-safe scaffold unexpectedly contains a local path.")
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    batch_path.write_text(content, encoding="utf-8")
    backlink = (
        f"- Security batch `{requirement['batchId']}`: "
        f"[{batch_path.name}]({batch_relative})"
    )
    return {
        "schema": "blindspot-security-batch-scaffold.v1",
        "batchId": requirement["batchId"],
        "batchPath": str(batch_path),
        "batchRelativePath": batch_relative,
        "findingIds": requirement["findingIds"],
        "ledgerBacklinkSuggestion": backlink,
        "visibility": visibility,
        "detailPolicy": detail_policy,
    }


def validate_application(
    snapshot_path: Path,
    ledger_override: Path | None,
    response_path: Path | None,
    *,
    allow_schema_change: bool,
) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise GuardError("Snapshot schema is invalid.")
    project_root = Path(str(snapshot.get("projectRoot", ""))).resolve(strict=True)
    ledger_path = Path(str(snapshot.get("ledgerPath", "")))
    if ledger_override is not None:
        ledger_path = ledger_override
    ledger_path = resolve_inside(project_root, ledger_path, must_exist=True)
    if str(ledger_path) != str(Path(str(snapshot.get("ledgerPath", ""))).resolve(strict=True)):
        raise GuardError("Ledger path does not match the snapshot.")

    if response_path is not None:
        response = load_json(response_path)
        preview = validate_owner_response(response)
    else:
        response = {}
        preview = {
            "errors": [],
            "warnings": [],
            "batchRequirements": [],
        }
    errors = list(preview["errors"])
    warnings = list(preview["warnings"])
    ledger_text = ledger_path.read_text(encoding="utf-8")

    for finding_id in response.get("expectedFindingIds", []):
        if isinstance(finding_id, str) and finding_id not in ledger_text:
            errors.append(f"ledger no longer contains expected finding: {finding_id}")

    protected_schemas = snapshot.get("protectedFindingTableSchemas")
    if not isinstance(protected_schemas, list):
        raise GuardError("Snapshot is missing protected finding-table schemas.")
    changes = schema_changes(protected_schemas, ledger_text)
    if changes and not allow_schema_change:
        errors.extend(["schema change blocked: " + item for item in changes])
    elif changes:
        warnings.extend(["approved schema change: " + item for item in changes])

    current_ids = defined_stable_ids(ledger_text)
    duplicate_ids = sorted(
        stable_id for stable_id, count in Counter(current_ids).items() if count > 1
    )
    if duplicate_ids:
        errors.append("duplicate defined IDs: " + ", ".join(duplicate_ids))
    missing_ids = sorted(set(snapshot.get("definedStableIds", [])) - set(current_ids))
    if missing_ids:
        errors.append("baseline IDs were removed: " + ", ".join(missing_ids))

    applied_mappings: list[dict[str, Any]] = []
    if response_path is not None:
        applied_mappings, application_errors = validate_applied_decisions(
            ledger_text,
            preview,
            compare_values=True,
        )
        errors.extend(application_errors)

    for requirement in preview["batchRequirements"]:
        errors.extend(validate_batch_handoff(project_root, ledger_text, requirement))

    result = {
        "schema": "blindspot-audit-followup-validation.v1",
        "validationKind": "owner-response" if response_path is not None else "schema-only",
        "snapshotId": snapshot.get("snapshotId"),
        "ledgerPath": str(ledger_path),
        "schemaChanges": changes,
        "newDefinedIds": sorted(set(current_ids) - set(snapshot.get("definedStableIds", []))),
        "appliedMappings": applied_mappings,
        "warnings": warnings,
        "errors": errors,
        "valid": not errors,
    }
    if result["valid"]:
        snapshot["validatedAt"] = utc_now()
        snapshot["validatedLedgerHash"] = sha256_text(ledger_text)
        snapshot["validatedResponseHash"] = (
            sha256_bytes(response_path.read_bytes()) if response_path is not None else None
        )
        write_json(snapshot_path, snapshot)
    return result


def render_validation(result: dict[str, Any]) -> str:
    lines = [
        "Audit follow-up validation",
        f"Kind: {result['validationKind']}",
        f"Ledger: {safe_display_text(result['ledgerPath'])}",
        f"Schema changes: {len(result['schemaChanges'])}",
        f"New defined IDs: {len(result['newDefinedIds'])}",
    ]
    if result.get("appliedMappings"):
        lines.append("Applied mappings:")
        for mapping in result["appliedMappings"]:
            axis_parts = []
            for axis in ("awareness", "disposition"):
                detail = mapping.get(axis)
                if not detail:
                    continue
                state = detail.get("applied")
                state_label = "applied" if state is True else "mismatch" if state is False else "planned"
                axis_parts.append(
                    f"{axis}={safe_display_text(detail.get('actual'))} ({state_label})"
                )
            lines.append(
                f"- {safe_display_text(mapping['findingId'])}: "
                f"{safe_display_text(mapping['destination'])}; "
                + ("; ".join(axis_parts) or "destination checked")
            )
    if result["warnings"]:
        lines.extend(
            ["Warnings:"]
            + [f"- {safe_display_text(item)}" for item in result["warnings"]]
        )
    if result["errors"]:
        lines.extend(
            ["Blocking errors:"]
            + [f"- {safe_display_text(item)}" for item in result["errors"]]
        )
    lines.append("Result: VALID" if result["valid"] else "Result: BLOCKED")
    return "\n".join(lines)


def prepare_awareness_response(
    snapshot_path: Path,
    audit_run_id: str,
    finding_ids: list[str],
    awareness: str,
    output_path: Path | None,
    *,
    id_column: str | None,
    awareness_column: str | None,
    disposition_column: str | None,
    ledger_awareness_value: str | None,
) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise GuardError("Snapshot schema is invalid.")

    project_root = Path(str(snapshot.get("projectRoot", ""))).resolve(strict=True)
    resolved_snapshot = resolve_inside(project_root, snapshot_path, must_exist=True)
    snapshot_dir = resolved_snapshot.parent
    expected_parent = project_root / ".blindspot-tmp"
    if (
        snapshot_dir.parent != expected_parent
        or not snapshot_dir.name.startswith("audit-followup-")
    ):
        raise GuardError("Unsafe audit-followup snapshot path.")

    ledger_path = resolve_inside(
        project_root,
        Path(str(snapshot.get("ledgerPath", ""))),
        must_exist=True,
    )
    ledger_text = ledger_path.read_text(encoding="utf-8")
    if sha256_text(ledger_text) != snapshot.get("ledgerHash"):
        raise GuardError(
            "Ledger changed after the snapshot; create a new snapshot before preparing awareness."
        )
    if audit_run_id not in set(STABLE_ID_PATTERN.findall(ledger_text)):
        raise GuardError(f"Audit run is not defined in the snapshot: {audit_run_id}")
    if len(finding_ids) != len(set(finding_ids)):
        raise GuardError("--finding contains duplicate finding IDs.")
    defined_ids = set(snapshot.get("definedStableIds", []))
    missing_findings = [
        finding_id for finding_id in finding_ids if finding_id not in defined_ids
    ]
    if missing_findings:
        raise GuardError(
            "Findings are not defined in the snapshot: " + ", ".join(missing_findings)
        )

    adapter_values = (
        id_column,
        awareness_column,
        disposition_column,
        ledger_awareness_value,
    )
    if any(value is not None for value in adapter_values) and not all(
        isinstance(value, str) and value.strip() for value in adapter_values
    ):
        raise GuardError(
            "Custom ledger preparation requires --id-column, --awareness-column, "
            "--disposition-column, and --ledger-awareness-value together."
        )

    response: dict[str, Any] = {
        "schema": "blindspot-owner-response.v1",
        "auditRunId": audit_run_id,
        "ownerResponseRecorded": True,
        "expectedFindingIds": finding_ids,
        "unmappedReferences": [],
        "decisions": [
            {
                "findingId": finding_id,
                "awareness": awareness,
                "disposition": None,
                "reason": "",
                "recheckTrigger": "",
                "batchId": "",
                "batchPath": "",
                "nextActionRoute": "none",
                "nextAction": "",
            }
            for finding_id in finding_ids
        ],
    }
    if all(isinstance(value, str) and value.strip() for value in adapter_values):
        response["applicationMap"] = {
            "idColumn": str(id_column).strip(),
            "awarenessColumn": str(awareness_column).strip(),
            "dispositionColumn": str(disposition_column).strip(),
            "awarenessValues": {awareness: str(ledger_awareness_value).strip()},
            "dispositionValues": {},
            "destinations": {},
        }

    preview = validate_owner_response(response)
    mappings, application_errors = validate_applied_decisions(
        ledger_text,
        preview,
        compare_values=False,
    )
    preview["applicationMappings"] = mappings
    preview["errors"].extend(application_errors)
    preview["valid"] = not preview["errors"]

    default_name = (
        f"owner-response-{finding_ids[0]}-awareness.json"
        if len(finding_ids) == 1
        else f"owner-response-{len(finding_ids)}-findings-awareness.json"
    )
    destination = output_path or Path(default_name)
    if not destination.is_absolute():
        destination = snapshot_dir / destination
    destination = resolve_inside(project_root, destination, must_exist=False)
    if destination.parent != snapshot_dir or destination.suffix.casefold() != ".json":
        raise GuardError("Prepared response must be a JSON file inside the snapshot directory.")
    if destination == resolved_snapshot:
        raise GuardError("Prepared response cannot overwrite the snapshot marker.")
    if destination.exists():
        raise GuardError("Prepared response already exists; do not overwrite it implicitly.")

    if preview["valid"]:
        write_json(destination, response)

    return {
        "schema": "blindspot-awareness-response-preparation.v1",
        "snapshotId": snapshot.get("snapshotId"),
        "ledgerPath": str(ledger_path),
        "ledgerEdits": "none-preview-only",
        "responsePath": str(destination) if preview["valid"] else None,
        "response": response,
        "preview": preview,
        "valid": preview["valid"],
    }


def render_awareness_preparation(result: dict[str, Any]) -> str:
    lines = [
        "Awareness response prepared",
        f"Ledger: {safe_display_text(result['ledgerPath'])}",
        "Ledger edits: none (preview only)",
    ]
    if result.get("responsePath"):
        lines.append(f"Response: {safe_display_text(result['responsePath'])}")
    lines.extend(["", render_preview(result["preview"])])
    return "\n".join(lines)


def cleanup_snapshot(
    snapshot_path: Path,
    *,
    confirm_applied: bool,
    discard: bool,
) -> Path:
    if not confirm_applied and not discard:
        raise GuardError(
            "cleanup requires --discard for a validated pre-delta snapshot or "
            "--confirm-applied after owner-response application"
        )
    snapshot = load_json(snapshot_path)
    if (
        snapshot.get("schema") != SNAPSHOT_SCHEMA
        or not snapshot.get("validatedAt")
    ):
        raise GuardError("Snapshot was not successfully validated.")
    has_owner_response = snapshot.get("validatedResponseHash") is not None
    if discard and has_owner_response:
        raise GuardError(
            "An owner-response snapshot cannot use --discard; use "
            "--confirm-applied after the validated decisions were applied."
        )
    if confirm_applied and not has_owner_response:
        raise GuardError(
            "A schema-only pre-delta snapshot has no applied owner response; "
            "use --discard."
        )
    project_root = Path(str(snapshot.get("projectRoot", ""))).resolve(strict=True)
    resolved_snapshot = resolve_inside(project_root, snapshot_path, must_exist=True)
    board_dir = resolved_snapshot.parent
    expected_parent = project_root / ".blindspot-tmp"
    if board_dir.parent != expected_parent or not board_dir.name.startswith(
        "audit-followup-"
    ):
        raise GuardError("Unsafe audit-followup cleanup path.")
    shutil.rmtree(board_dir)
    return board_dir


def output_result(value: dict[str, Any], text_value: str, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(text_value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview and validate owner-response ledger application."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot")
    snapshot.add_argument("--project-root", required=True)
    snapshot.add_argument("--ledger", required=True)
    snapshot.add_argument("--out")
    snapshot.add_argument("--format", choices=("text", "json"), default="text")

    preview = subparsers.add_parser("preview")
    preview.add_argument("--ledger", required=True)
    preview.add_argument("--data", required=True)
    preview.add_argument("--format", choices=("text", "json"), default="text")

    prepare_awareness = subparsers.add_parser("prepare-awareness")
    prepare_awareness.add_argument("--snapshot", required=True)
    prepare_awareness.add_argument("--audit-run", required=True)
    prepare_awareness.add_argument(
        "--finding",
        action="append",
        required=True,
        help="Finding ID; repeat for findings that share the same awareness value",
    )
    prepare_awareness.add_argument(
        "--value",
        choices=tuple(sorted(ALLOWED_AWARENESS)),
        required=True,
    )
    prepare_awareness.add_argument("--id-column")
    prepare_awareness.add_argument("--awareness-column")
    prepare_awareness.add_argument("--disposition-column")
    prepare_awareness.add_argument("--ledger-awareness-value")
    prepare_awareness.add_argument("--out")
    prepare_awareness.add_argument(
        "--format", choices=("text", "json"), default="text"
    )

    validate = subparsers.add_parser("validate")
    validate.add_argument("--snapshot", required=True)
    validate.add_argument("--ledger")
    validate.add_argument("--data")
    validate.add_argument("--allow-schema-change", action="store_true")
    validate.add_argument("--format", choices=("text", "json"), default="text")

    scaffold = subparsers.add_parser("scaffold-security-batch")
    scaffold.add_argument("--project-root", required=True)
    scaffold.add_argument("--ledger", required=True)
    scaffold.add_argument("--data", required=True)
    scaffold.add_argument("--batch-id")
    scaffold.add_argument(
        "--visibility",
        choices=tuple(sorted(ALLOWED_VISIBILITY)),
        default="unconfirmed",
    )
    scaffold.add_argument(
        "--detail-policy",
        choices=tuple(sorted(ALLOWED_DETAIL_POLICY)),
        default="generalized",
    )
    scaffold.add_argument("--format", choices=("text", "json"), default="text")

    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--snapshot", required=True)
    cleanup_mode = cleanup.add_mutually_exclusive_group()
    cleanup_mode.add_argument("--confirm-applied", action="store_true")
    cleanup_mode.add_argument(
        "--discard",
        action="store_true",
        help="Delete a successfully schema-validated pre-delta snapshot",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            root = Path(args.project_root).expanduser().resolve(strict=True)
            ledger = Path(args.ledger).expanduser()
            if not ledger.is_absolute():
                ledger = root / ledger
            destination = Path(args.out).expanduser() if args.out else default_snapshot_path(root)
            if not destination.is_absolute():
                destination = root / destination
            result = create_snapshot(root, ledger, destination)
            text_value = (
                "Ledger guard snapshot created: "
                f"{safe_display_text(result['snapshotPath'])}\n"
                f"Tables: {len(result['snapshot']['tableSchemas'])}; "
                f"defined IDs: {len(result['snapshot']['definedStableIds'])}; "
                f"dirty target: {bool(result['snapshot']['gitBaseline'].get('hadTargetStatus'))}"
            )
            output_result(result, text_value, args.format)
            return 0

        if args.command == "preview":
            ledger = Path(args.ledger).expanduser().resolve(strict=True)
            response = load_json(Path(args.data).expanduser().resolve(strict=True))
            preview = validate_owner_response(response)
            ledger_text = ledger.read_text(encoding="utf-8")
            for finding_id in response.get("expectedFindingIds", []):
                if isinstance(finding_id, str) and finding_id not in ledger_text:
                    preview["errors"].append(
                        f"ledger does not contain expected finding: {finding_id}"
                    )
            mappings, application_errors = validate_applied_decisions(
                ledger_text,
                preview,
                compare_values=False,
            )
            preview["applicationMappings"] = mappings
            preview["errors"].extend(application_errors)
            preview["valid"] = not preview["errors"]
            output_result(preview, render_preview(preview), args.format)
            return 0 if preview["valid"] else 3

        if args.command == "prepare-awareness":
            result = prepare_awareness_response(
                resolve_snapshot_input(Path(args.snapshot)),
                args.audit_run,
                args.finding,
                args.value,
                Path(args.out).expanduser() if args.out else None,
                id_column=args.id_column,
                awareness_column=args.awareness_column,
                disposition_column=args.disposition_column,
                ledger_awareness_value=args.ledger_awareness_value,
            )
            output_result(
                result,
                render_awareness_preparation(result),
                args.format,
            )
            return 0 if result["valid"] else 3

        if args.command == "validate":
            snapshot_path = resolve_snapshot_input(Path(args.snapshot))
            ledger = (
                Path(args.ledger).expanduser().resolve(strict=True)
                if args.ledger
                else None
            )
            result = validate_application(
                snapshot_path,
                ledger,
                (
                    Path(args.data).expanduser().resolve(strict=True)
                    if args.data
                    else None
                ),
                allow_schema_change=args.allow_schema_change,
            )
            output_result(result, render_validation(result), args.format)
            return 0 if result["valid"] else 3

        if args.command == "scaffold-security-batch":
            root = Path(args.project_root).expanduser().resolve(strict=True)
            ledger = Path(args.ledger).expanduser()
            if not ledger.is_absolute():
                ledger = root / ledger
            result = scaffold_security_batch(
                root,
                ledger,
                Path(args.data).expanduser().resolve(strict=True),
                batch_id=args.batch_id,
                visibility=args.visibility,
                detail_policy=args.detail_policy,
            )
            text_value = (
                "Security batch scaffold created: "
                f"{safe_display_text(result['batchPath'])}\n"
                f"Included findings: {len(result['findingIds'])}\n"
                "Ledger backlink suggestion: "
                f"{safe_display_text(result['ledgerBacklinkSuggestion'])}\n"
                "Fill the decision and verification placeholders before final validation."
            )
            output_result(result, text_value, args.format)
            return 0

        if args.command == "cleanup":
            removed = cleanup_snapshot(
                resolve_snapshot_input(Path(args.snapshot)),
                confirm_applied=args.confirm_applied,
                discard=args.discard,
            )
            action = (
                "Discarded validated pre-delta snapshot directory"
                if args.discard
                else "Deleted applied owner-response snapshot directory"
            )
            print(f"{action}: {safe_display_text(removed)}")
            return 0

        raise GuardError("Unknown command.")
    except (GuardError, OSError) as exc:
        message = str(exc) if isinstance(exc, GuardError) else "A required file could not be read."
        print(f"error: {safe_display_text(message)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
