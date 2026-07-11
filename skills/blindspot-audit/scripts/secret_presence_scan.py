#!/usr/bin/env python3
"""Locate likely secret presence without printing matched values or context."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from safe_output import safe_display_text
except ModuleNotFoundError as exc:
    if exc.name != "safe_output":
        raise
    raise SystemExit(
        "error: secret_presence_scan.py requires safe_output.py in the same directory; "
        "copy both packaged files together."
    ) from exc


SCHEMA = "blindspot-secret-presence.v1"
DEFAULT_MAX_FILE_BYTES = 1_000_000
DEFAULT_MAX_FILES = 5_000
DEFAULT_MAX_HISTORY_BLOBS = 2_000
DEFAULT_TIME_BUDGET_SECONDS = 8.0
EXCLUDED_DIRECTORIES = {
    ".blindspot-tmp",
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}
DEFAULT_NOISY_DIRECTORIES = {
    "build",
    "dist",
    "external-repos",
    "external_repos",
    "runtime",
    "vendor",
}
DEFAULT_NOISY_PATHS = {
    "data/external/raw",
    "docs/archive",
    "docs/research",
    "docs/sources",
}

TOKEN_PATTERNS = (
    (
        "private-key-material",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("github-token-shape", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github-token-shape", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai-key-shape", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key-shape", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "jwt-shape",
        re.compile(
            r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\."
            r"[A-Za-z0-9_-]{10,}\b"
        ),
    ),
    ("slack-token-shape", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("stripe-live-key-shape", re.compile(r"\b[rs]k_live_[A-Za-z0-9]{16,}\b")),
    ("google-api-key-shape", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "credential-in-url",
        re.compile(r"\bhttps?://[^\s/:@]+:[^@\s]+@", re.IGNORECASE),
    ),
)

SECRET_NAME = (
    r"(?:secret|token|password|passwd|pwd|api[_-]?key|private[_-]?key|"
    r"client[_-]?secret|access[_-]?key)"
)
ASSIGNMENT_PATTERN = re.compile(
    rf"(?i)(?P<identifier>[A-Za-z][A-Za-z0-9_.-]{{0,80}}"
    rf"{SECRET_NAME}[A-Za-z0-9_.-]{{0,40}})\s*[\"']?\s*[:=]\s*"
    rf"(?P<value>.+)$"
)
PLACEHOLDER_MARKERS = (
    "${",
    "{{",
    "<secret",
    "<token",
    "change-me",
    "changeme",
    "dummy",
    "example",
    "getenv(",
    "not-set",
    "os.environ",
    "os.getenv",
    "placeholder",
    "process.env",
    "redacted",
    "replace-me",
    "replace_me",
)
PLACEHOLDER_VALUES = {"", "none", "null", "secret", "token", "undefined", "xxxxx"}


class SafeScanError(RuntimeError):
    """An error whose message is safe to show without command output."""


class SafeScanTimeout(RuntimeError):
    """A bounded command reached the configured internal time budget."""


@dataclass(frozen=True)
class Candidate:
    location: str
    path: str
    line: int
    category: str
    identifier: str | None = None
    object_id: str | None = None

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "location": self.location,
            "path": self.path,
            "line": self.line,
            "category": self.category,
        }
        if self.identifier:
            result["identifier"] = self.identifier
        if self.object_id:
            result["objectId"] = self.object_id
        return result


def _redact_known_shapes(value: str) -> str:
    sanitized = safe_display_text(value)
    for _, pattern in TOKEN_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


def _safe_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    return _redact_known_shapes(normalized)


def _is_excluded(relative_path: str) -> bool:
    parts = PurePosixPath(relative_path.replace("\\", "/")).parts
    return any(part in EXCLUDED_DIRECTORIES for part in parts)


def _is_default_noisy(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/").strip("/")
    parts = PurePosixPath(normalized).parts
    if any(part in DEFAULT_NOISY_DIRECTORIES for part in parts):
        return True
    return any(
        normalized == prefix or normalized.startswith(prefix + "/")
        for prefix in DEFAULT_NOISY_PATHS
    )


def _normalize_pattern(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def _matches_pattern(relative_path: str, pattern: str) -> bool:
    relative = relative_path.replace("\\", "/").strip("/")
    normalized = _normalize_pattern(pattern)
    if not normalized:
        return False
    if not any(character in normalized for character in "*?["):
        return relative == normalized or relative.startswith(normalized + "/")
    return fnmatch.fnmatchcase(relative, normalized) or PurePosixPath(relative).match(
        normalized
    )


def _path_selected(
    relative_path: str,
    includes: list[str],
    excludes: list[str],
    include_noisy: bool,
) -> bool:
    if _is_excluded(relative_path):
        return False
    if excludes and any(_matches_pattern(relative_path, item) for item in excludes):
        return False
    explicitly_included = bool(includes) and any(
        _matches_pattern(relative_path, item) for item in includes
    )
    if _is_default_noisy(relative_path) and not include_noisy and not explicitly_included:
        return False
    if includes and not explicitly_included:
        return False
    return True


def _directory_may_match_include(relative_path: str, includes: list[str]) -> bool:
    if not includes:
        return False
    directory = relative_path.replace("\\", "/").strip("/")
    for raw_pattern in includes:
        pattern = _normalize_pattern(raw_pattern)
        wildcard_index = min(
            (pattern.find(character) for character in "*?[" if character in pattern),
            default=len(pattern),
        )
        prefix = pattern[:wildcard_index].rstrip("/")
        if not prefix or prefix.startswith(directory + "/") or directory.startswith(prefix + "/"):
            return True
        if directory == prefix:
            return True
    return False


def _resume_scope(relative_path: str) -> str:
    safe = _safe_relative_path(relative_path)
    parts = PurePosixPath(safe).parts
    if not parts:
        return "<project-root>"
    if len(parts) == 1:
        return parts[0]
    return parts[0] + "/**"


def _deadline_reached(deadline: float | None) -> bool:
    return deadline is not None and time.monotonic() >= deadline


def _remaining_seconds(deadline: float | None) -> float | None:
    if deadline is None:
        return None
    return max(0.0, deadline - time.monotonic())


def _looks_like_placeholder(raw_value: str) -> bool:
    value = raw_value.strip().rstrip(",;").strip().strip("\"'").strip()
    lowered = value.lower()
    if len(value) < 8 or lowered in PLACEHOLDER_VALUES:
        return True
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def _scan_text(
    text: str,
    *,
    location: str,
    path: str,
    object_id: str | None = None,
) -> list[Candidate]:
    candidates: set[Candidate] = set()
    safe_path = _safe_relative_path(path)

    for line_number, line in enumerate(text.splitlines(), start=1):
        for category, pattern in TOKEN_PATTERNS:
            if pattern.search(line):
                candidates.add(
                    Candidate(
                        location=location,
                        path=safe_path,
                        line=line_number,
                        category=category,
                        object_id=object_id,
                    )
                )

        assignment = ASSIGNMENT_PATTERN.search(line)
        if assignment and not _looks_like_placeholder(assignment.group("value")):
            candidates.add(
                Candidate(
                    location=location,
                    path=safe_path,
                    line=line_number,
                    category="secret-named-assignment",
                    identifier=_redact_known_shapes(assignment.group("identifier")),
                    object_id=object_id,
                )
            )

    return sorted(
        candidates,
        key=lambda item: (
            item.location,
            item.path,
            item.line,
            item.category,
            item.identifier or "",
            item.object_id or "",
        ),
    )


def _decode_text(data: bytes) -> str | None:
    if b"\x00" in data[:8192]:
        return None
    return data.decode("utf-8", errors="ignore")


def _blank_scope(status: str) -> dict[str, object]:
    return {
        "status": status,
        "enumerationMode": None,
        "gitIgnoredPolicy": None,
        "coverageNote": None,
        "matchedItems": 0,
        "itemsScanned": 0,
        "itemsSkipped": 0,
        "itemsExcluded": 0,
        "truncated": False,
        "stopReason": None,
        "lastPath": None,
        "recommendedResumeScope": None,
        "candidates": [],
    }


def _mark_partial(
    result: dict[str, object],
    *,
    reason: str,
    relative_path: str | None,
) -> None:
    result["status"] = "partial"
    result["truncated"] = True
    result["stopReason"] = reason
    if relative_path:
        result["lastPath"] = _safe_relative_path(relative_path)
        result["recommendedResumeScope"] = _resume_scope(relative_path)


def _git_visible_tree_files(
    root: Path,
    deadline: float | None,
) -> list[Path] | None:
    """Return tracked plus unignored untracked files, or None outside Git."""
    timeout = _remaining_seconds(deadline)
    if timeout is not None and timeout <= 0:
        raise SafeScanTimeout("time-budget")
    try:
        repository = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SafeScanTimeout("time-budget") from exc
    except OSError:
        return None
    if repository.returncode != 0:
        return None

    try:
        repo_root = Path(os.fsdecode(repository.stdout.strip())).resolve(strict=True)
        root_prefix = root.relative_to(repo_root)
    except (OSError, ValueError):
        return None

    arguments = [
        "git",
        "-C",
        str(repo_root),
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        root_prefix.as_posix() if root_prefix.parts else ".",
    ]
    timeout = _remaining_seconds(deadline)
    if timeout is not None and timeout <= 0:
        raise SafeScanTimeout("time-budget")
    try:
        listed = subprocess.run(
            arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SafeScanTimeout("time-budget") from exc
    except OSError:
        return None
    if listed.returncode != 0:
        return None

    files: list[Path] = []
    for raw_path in listed.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = repo_root / os.fsdecode(raw_path)
        try:
            path.relative_to(root)
        except ValueError:
            continue
        files.append(path)
    return sorted(set(files), key=lambda value: value.as_posix().casefold())


def _iter_tree_files(
    root: Path,
    excludes: list[str],
    includes: list[str],
    include_noisy: bool,
):
    for current_root, directories, filenames in os.walk(root, followlinks=False):
        current = Path(current_root)
        kept_directories = []
        for directory in sorted(directories):
            candidate = current / directory
            try:
                relative = candidate.relative_to(root).as_posix()
            except ValueError:
                continue
            if (
                candidate.is_symlink()
                or _is_excluded(relative)
                or (
                    _is_default_noisy(relative)
                    and not include_noisy
                    and not _directory_may_match_include(relative, includes)
                )
                or any(_matches_pattern(relative, item) for item in excludes)
            ):
                continue
            kept_directories.append(directory)
        directories[:] = kept_directories
        for filename in sorted(filenames):
            yield current / filename


def scan_current_tree(
    root: Path,
    max_file_bytes: int,
    max_files: int,
    deadline: float | None,
    includes: list[str],
    excludes: list[str],
    include_noisy: bool,
    include_ignored: bool = False,
) -> dict[str, object]:
    result = _blank_scope("scanned")
    candidates: list[Candidate] = []

    if include_ignored:
        paths: Iterable[Path] = _iter_tree_files(
            root, excludes, includes, include_noisy
        )
        result["enumerationMode"] = "filesystem-explicit-ignored"
        result["gitIgnoredPolicy"] = "targeted-opt-in"
        result["coverageNote"] = (
            "Filesystem enumeration was explicitly enabled for selected ignored "
            "paths; include filters bound the scope."
        )
    else:
        try:
            git_files = _git_visible_tree_files(root, deadline)
        except SafeScanTimeout:
            result["enumerationMode"] = "git-index-plus-unignored"
            result["gitIgnoredPolicy"] = "excluded-not-enumerated"
            result["coverageNote"] = "Git-aware enumeration exceeded the time budget."
            _mark_partial(
                result,
                reason="time-budget",
                relative_path="<tree-enumeration>",
            )
            return result
        if git_files is None:
            paths = _iter_tree_files(root, excludes, includes, include_noisy)
            result["enumerationMode"] = "filesystem-fallback"
            result["gitIgnoredPolicy"] = "not-evaluated"
            result["coverageNote"] = (
                "Git index unavailable; bounded filesystem enumeration used with "
                "hard Search Hygiene exclusions."
            )
        else:
            paths = git_files
            result["enumerationMode"] = "git-index-plus-unignored"
            result["gitIgnoredPolicy"] = "excluded-not-enumerated"
            result["coverageNote"] = (
                "Tracked files and unignored untracked files were inspected; "
                "Git-ignored paths were excluded without reading their contents."
            )

    for path in paths:
        try:
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if not _path_selected(relative, includes, excludes, include_noisy):
                result["itemsExcluded"] = int(result["itemsExcluded"]) + 1
                continue
            result["matchedItems"] = int(result["matchedItems"]) + 1
            if _deadline_reached(deadline):
                _mark_partial(result, reason="time-budget", relative_path=relative)
                break
            processed = int(result["itemsScanned"]) + int(result["itemsSkipped"])
            if processed >= max_files:
                _mark_partial(result, reason="max-files", relative_path=relative)
                break
            if path.stat().st_size > max_file_bytes:
                result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
                result["lastPath"] = _safe_relative_path(relative)
                continue
            data = path.read_bytes()
        except (OSError, ValueError):
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            continue

        text = _decode_text(data)
        if text is None:
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            result["lastPath"] = _safe_relative_path(relative)
            continue
        result["itemsScanned"] = int(result["itemsScanned"]) + 1
        result["lastPath"] = _safe_relative_path(relative)
        candidates.extend(
            _scan_text(text, location="current-tree", path=relative)
        )

    result["candidates"] = [candidate.as_dict() for candidate in candidates]
    return result


def _run_git(
    root: Path,
    arguments: Iterable[str],
    *,
    input_data: bytes | None = None,
    deadline: float | None = None,
):
    timeout = _remaining_seconds(deadline)
    if timeout is not None and timeout <= 0:
        raise SafeScanTimeout("time-budget")
    try:
        return subprocess.run(
            ["git", "-C", str(root), *arguments],
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SafeScanTimeout("time-budget") from exc
    except OSError as exc:
        raise SafeScanError("Git is unavailable for the requested history scan.") from exc


def scan_git_history(
    root: Path,
    max_file_bytes: int,
    max_history_blobs: int,
    deadline: float | None,
    includes: list[str],
    excludes: list[str],
    include_noisy: bool,
) -> dict[str, object]:
    result = _blank_scope("scanned")
    candidates: list[Candidate] = []

    try:
        inside = _run_git(
            root, ["rev-parse", "--is-inside-work-tree"], deadline=deadline
        )
    except SafeScanTimeout:
        _mark_partial(result, reason="time-budget", relative_path="<history-enumeration>")
        return result
    if inside.returncode != 0 or inside.stdout.strip() != b"true":
        result["status"] = "not-a-git-repository"
        return result

    try:
        objects = _run_git(
            root, ["rev-list", "--objects", "--all"], deadline=deadline
        )
    except SafeScanTimeout:
        _mark_partial(result, reason="time-budget", relative_path="<history-enumeration>")
        return result
    if objects.returncode != 0:
        raise SafeScanError("Git history enumeration failed.")

    try:
        checked = _run_git(
            root,
            ["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)"],
            input_data=objects.stdout,
            deadline=deadline,
        )
    except SafeScanTimeout:
        _mark_partial(result, reason="time-budget", relative_path="<history-metadata>")
        return result
    if checked.returncode != 0:
        raise SafeScanError("Git object metadata inspection failed.")

    seen_blobs: set[str] = set()
    for raw_line in checked.stdout.decode("utf-8", errors="replace").splitlines():
        parts = raw_line.split(" ", 3)
        if len(parts) < 3:
            continue
        object_id, object_type, raw_size = parts[:3]
        raw_path = parts[3] if len(parts) == 4 and parts[3] else "<unknown>"
        if object_type != "blob" or object_id in seen_blobs:
            continue
        seen_blobs.add(object_id)
        if not _path_selected(raw_path, includes, excludes, include_noisy):
            result["itemsExcluded"] = int(result["itemsExcluded"]) + 1
            continue
        result["matchedItems"] = int(result["matchedItems"]) + 1
        if _deadline_reached(deadline):
            _mark_partial(result, reason="time-budget", relative_path=raw_path)
            break
        try:
            object_size = int(raw_size)
        except ValueError:
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            continue
        if object_size > max_file_bytes:
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            result["lastPath"] = _safe_relative_path(raw_path)
            continue
        processed = int(result["itemsScanned"]) + int(result["itemsSkipped"])
        if processed >= max_history_blobs:
            _mark_partial(result, reason="max-history-blobs", relative_path=raw_path)
            break

        try:
            blob = _run_git(
                root, ["cat-file", "blob", object_id], deadline=deadline
            )
        except SafeScanTimeout:
            _mark_partial(result, reason="time-budget", relative_path=raw_path)
            break
        if blob.returncode != 0:
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            continue
        text = _decode_text(blob.stdout)
        if text is None:
            result["itemsSkipped"] = int(result["itemsSkipped"]) + 1
            result["lastPath"] = _safe_relative_path(raw_path)
            continue
        result["itemsScanned"] = int(result["itemsScanned"]) + 1
        result["lastPath"] = _safe_relative_path(raw_path)
        candidates.extend(
            _scan_text(
                text,
                location="git-history",
                path=raw_path,
                object_id=object_id[:12],
            )
        )

    result["candidates"] = [candidate.as_dict() for candidate in candidates]
    return result


def _scope_summary(label: str, scope: dict[str, object]) -> str:
    status = str(scope["status"])
    if status not in {"scanned", "partial"}:
        return f"{label} {status}"
    candidates = len(scope["candidates"])
    partial = (
        f"; partial ({scope['stopReason']}); resume {scope['recommendedResumeScope']}"
        if status == "partial"
        else ""
    )
    return (
        f"{label} {status}; matched {scope['matchedItems']}; scanned "
        f"{scope['itemsScanned']}; skipped {scope['itemsSkipped']}; excluded "
        f"{scope['itemsExcluded']}; enumeration "
        f"{scope.get('enumerationMode') or 'not-applicable'}; "
        f"{candidates} candidate locations{partial}"
    )


def build_result(
    root: Path,
    *,
    scope: str,
    max_file_bytes: int,
    max_files: int,
    max_history_blobs: int,
    time_budget: float,
    includes: list[str],
    excludes: list[str],
    include_noisy: bool,
    include_ignored: bool = False,
) -> dict[str, object]:
    current_tree = _blank_scope("not-requested")
    git_history = _blank_scope("not-requested")
    deadline = time.monotonic() + time_budget if time_budget > 0 else None

    if scope in {"tree", "both"}:
        current_tree = scan_current_tree(
            root,
            max_file_bytes,
            max_files,
            deadline,
            includes,
            excludes,
            include_noisy,
            include_ignored,
        )
    if scope in {"history", "both"}:
        git_history = scan_git_history(
            root,
            max_file_bytes,
            max_history_blobs,
            deadline,
            includes,
            excludes,
            include_noisy,
        )

    audit_note = (
        "secret search: manual-heuristic; "
        f"{_scope_summary('current-tree', current_tree)}; "
        f"{_scope_summary('history', git_history)}; values suppressed; "
        f"default-noisy-paths {'included' if include_noisy else 'excluded'}; "
        "provider owner-confirm-needed"
    )
    return {
        "schema": SCHEMA,
        "classification": "manual-heuristic",
        "valuesSuppressed": True,
        "bounds": {
            "maxFileBytes": max_file_bytes,
            "maxFiles": max_files,
            "maxHistoryBlobs": max_history_blobs,
            "timeBudgetSeconds": time_budget,
        },
        "filters": {
            "include": includes,
            "exclude": excludes,
            "includeNoisy": include_noisy,
            "includeIgnored": include_ignored,
        },
        "excludedDirectories": sorted(
            EXCLUDED_DIRECTORIES
            | (set() if include_noisy else DEFAULT_NOISY_DIRECTORIES)
        ),
        "defaultNoisyPaths": sorted(DEFAULT_NOISY_PATHS),
        "limitation": (
            "Candidate presence only. This helper does not prove that a value is live, "
            "that history is fully remediated, or that no other secret exists."
        ),
        "scopes": {
            "currentTree": current_tree,
            "gitHistory": git_history,
            "provider": {
                "status": "owner-confirm-needed",
                "candidates": [],
                "note": "This helper never contacts providers or tests credentials.",
            },
        },
        "auditLogNote": audit_note,
    }


def render_text(result: dict[str, object]) -> str:
    scopes = result["scopes"]
    assert isinstance(scopes, dict)
    lines = [
        "Secret presence locator",
        "classification: manual-heuristic",
        "values: suppressed",
        (
            "bounds: max-file-bytes="
            f"{result['bounds']['maxFileBytes']} max-files="
            f"{result['bounds']['maxFiles']} max-history-blobs="
            f"{result['bounds']['maxHistoryBlobs']} time-budget="
            f"{result['bounds']['timeBudgetSeconds']}s"
        ),
        "include filters: " + (", ".join(result["filters"]["include"]) or "<all>"),
        "exclude filters: " + (", ".join(result["filters"]["exclude"]) or "<none>"),
        "default noisy/generated paths: "
        + ("included" if result["filters"]["includeNoisy"] else "excluded unless explicitly included"),
        "Git-ignored paths: "
        + (
            "targeted include enabled"
            if result["filters"]["includeIgnored"]
            else "excluded in Git-aware mode"
        ),
        "excluded directories: " + ", ".join(result["excludedDirectories"]),
    ]
    for key, label in (("currentTree", "current-tree"), ("gitHistory", "history")):
        scope = scopes[key]
        assert isinstance(scope, dict)
        lines.append(_scope_summary(label, scope))
        for candidate in scope["candidates"]:
            assert isinstance(candidate, dict)
            details = [
                f"- {candidate['location']} {candidate['path']}:{candidate['line']}",
                f"category={candidate['category']}",
            ]
            if candidate.get("identifier"):
                details.append(f"identifier={candidate['identifier']}")
            if candidate.get("objectId"):
                details.append(f"object={candidate['objectId']}")
            lines.append(" ".join(details))
    provider = scopes["provider"]
    assert isinstance(provider, dict)
    lines.append(f"provider: {provider['status']}")
    lines.append(f"Audit Log: {result['auditLogNote']}")
    lines.append(f"Limitation: {result['limitation']}")
    return "\n".join(lines)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report likely secret locations without printing matched values."
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--scope", choices=("tree", "history", "both"), default="tree")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Relative path or glob to include; repeatable.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Relative path or glob to exclude; repeatable.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=positive_int,
        default=DEFAULT_MAX_FILE_BYTES,
    )
    parser.add_argument(
        "--max-files",
        type=positive_int,
        default=DEFAULT_MAX_FILES,
    )
    parser.add_argument(
        "--max-history-blobs",
        type=positive_int,
        default=DEFAULT_MAX_HISTORY_BLOBS,
    )
    parser.add_argument(
        "--time-budget",
        type=nonnegative_float,
        default=DEFAULT_TIME_BUDGET_SECONDS,
        help="Internal seconds before returning partial coverage; 0 disables.",
    )
    parser.add_argument(
        "--include-generated",
        "--include-noisy",
        dest="include_noisy",
        action="store_true",
        help=(
            "Include generated/reference/vendor paths normally skipped by Search "
            "Hygiene. An explicit --include path also opts that path in."
        ),
    )
    parser.add_argument(
        "--include-ignored",
        action="store_true",
        help=(
            "Permit filesystem enumeration of Git-ignored files selected by at "
            "least one explicit --include filter."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        if args.include_ignored and not any(value.strip() for value in args.include):
            raise SafeScanError("--include-ignored requires at least one --include filter.")
        root = Path(args.project_root).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise SafeScanError("Project root is not a directory.")
        result = build_result(
            root,
            scope=args.scope,
            max_file_bytes=args.max_file_bytes,
            max_files=args.max_files,
            max_history_blobs=args.max_history_blobs,
            time_budget=args.time_budget,
            includes=[_normalize_pattern(value) for value in args.include if value.strip()],
            excludes=[_normalize_pattern(value) for value in args.exclude if value.strip()],
            include_noisy=args.include_noisy,
            include_ignored=args.include_ignored,
        )
    except SafeScanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("error: project root or scan input could not be read.", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
