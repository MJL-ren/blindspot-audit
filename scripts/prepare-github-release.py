#!/usr/bin/env python3
"""Prepare GitHub Release metadata from the canonical plugin version.

The repository version lives in .claude-plugin/plugin.json. This helper
uses that version, finds the previous semver tag, and writes release notes
from every CHANGELOG.md entry newer than that tag.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


VERSION_HEADING_RE = re.compile(r"^##\s*\[(\d+\.\d+\.\d+)\](?:\s*-\s*(.*))?\s*$", re.MULTILINE)
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise SystemExit(f"Version must be x.y.z, got {version!r}")
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise SystemExit(f"Version must be numeric x.y.z, got {version!r}") from exc


def tag_version_tuple(tag: str) -> tuple[int, int, int] | None:
    match = TAG_RE.match(tag.strip())
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def git_tags(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "tag", "--list", "v[0-9]*"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def previous_tag(repo_root: Path, current_version: str) -> str | None:
    current = version_tuple(current_version)
    candidates: list[tuple[tuple[int, int, int], str]] = []
    for tag in git_tags(repo_root):
        parsed = tag_version_tuple(tag)
        if parsed is not None and parsed < current:
            candidates.append((parsed, tag))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def changelog_sections(changelog: str) -> dict[str, str]:
    matches = list(VERSION_HEADING_RE.finditer(changelog))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(changelog)
        sections[match.group(1)] = changelog[start:end].strip() + "\n"
    return sections


def selected_sections(changelog: str, current_version: str, previous: str | None) -> list[str]:
    current = version_tuple(current_version)
    previous_version = tag_version_tuple(previous) if previous else None
    sections = changelog_sections(changelog)
    if current_version not in sections:
        raise SystemExit(f"CHANGELOG.md has no section for current version {current_version}")

    selected: list[str] = []
    for match in VERSION_HEADING_RE.finditer(changelog):
        version = match.group(1)
        parsed = version_tuple(version)
        if parsed > current:
            continue
        if previous_version is not None and parsed <= previous_version:
            break
        selected.append(sections[version])

    if not selected:
        raise SystemExit("No CHANGELOG.md sections selected for release notes")
    return selected


def write_github_output(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def prepare_release(repo_root: Path, notes_file: Path, github_output: Path | None) -> int:
    canonical_path = repo_root / ".claude-plugin" / "plugin.json"
    changelog_path = repo_root / "CHANGELOG.md"
    package_path = repo_root / "dist" / "blindspot-audit.skill"

    if not canonical_path.exists():
        print(f"Missing canonical plugin manifest: {canonical_path}", file=sys.stderr)
        return 1
    if not changelog_path.exists():
        print(f"Missing CHANGELOG.md: {changelog_path}", file=sys.stderr)
        return 1
    if not package_path.exists():
        print(f"Missing release asset: {package_path}", file=sys.stderr)
        return 1

    version = load_json(canonical_path).get("version")
    if not isinstance(version, str) or not version:
        print(f"Missing version in {canonical_path}", file=sys.stderr)
        return 1

    current_tag = f"v{version}"
    previous = previous_tag(repo_root, version)
    sections = selected_sections(changelog_path.read_text(encoding="utf-8"), version, previous)

    if previous:
        intro = f"This release includes all CHANGELOG.md entries after `{previous}`."
    else:
        intro = "This release includes all available CHANGELOG.md entries for this version line."

    body = "\n\n".join(
        [
            intro,
            "The Claude desktop `.skill` package is attached as a release asset.",
            *sections,
        ]
    )
    notes_file.parent.mkdir(parents=True, exist_ok=True)
    notes_file.write_text(body.rstrip() + "\n", encoding="utf-8")

    outputs = {
        "version": version,
        "tag": current_tag,
        "previous_tag": previous or "",
        "notes_file": notes_file.as_posix(),
    }
    if github_output is not None:
        write_github_output(github_output, outputs)

    print(f"Prepared release {current_tag}")
    if previous:
        print(f"Included changelog entries after {previous}")
    else:
        print("No previous semver tag found")
    print(f"Wrote notes to {notes_file}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare GitHub Release metadata from CHANGELOG.md.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--notes-file",
        type=Path,
        default=Path("release-notes.md"),
        help="Release notes output path.",
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="Optional GitHub Actions output file path.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    notes_file = args.notes_file
    if not notes_file.is_absolute():
        notes_file = repo_root / notes_file

    return prepare_release(repo_root, notes_file, args.github_output)


if __name__ == "__main__":
    raise SystemExit(main())
