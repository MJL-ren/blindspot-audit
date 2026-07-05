#!/usr/bin/env python3
"""Fail when skill/package content changed since the latest semver tag without a version bump.

Rationale: plugin hosts only deliver updates when the manifest version
string changes. If skill content ships on main while the version stays at
the latest release, the release job silently skips and installed users
keep running the old skill - the exact stale-install failure mode this
repo has been bitten by. Docs-only changes may ship without a bump.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

GUARDED_PREFIXES = (
    "skills/blindspot-audit/",
    "plugins/blindspot-audit/",
    "dist/",
)

SEMVER_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def run(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def parse_version(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        raise SystemExit(f"Unrecognized version string: {version!r}")
    return tuple(int(part) for part in match.groups())


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = parse_version(manifest["version"])

    tags: list[tuple[tuple[int, int, int], str]] = []
    for line in run("git", "tag", "--list").splitlines():
        match = SEMVER_TAG.match(line.strip())
        if match:
            tags.append((tuple(int(part) for part in match.groups()), line.strip()))

    if not tags:
        print("No semver tags found; skipping version-bump guard (bootstrap state).")
        return 0

    latest_version, latest_tag = max(tags)

    if current < latest_version:
        print(
            f"Manifest version {manifest['version']} is BEHIND the latest tag {latest_tag}.",
            file=sys.stderr,
        )
        return 1

    changed = run("git", "diff", "--name-only", f"{latest_tag}..HEAD").splitlines()
    guarded = sorted(path for path in changed if path.startswith(GUARDED_PREFIXES))

    if guarded and current == latest_version:
        print(
            f"Skill/package content changed since {latest_tag} but the plugin version is "
            f"still {manifest['version']}. Users only receive updates when the version "
            "string changes - bump .claude-plugin/plugin.json and the Codex manifest, and "
            "add a CHANGELOG entry. Changed guarded files:",
            file=sys.stderr,
        )
        for path in guarded:
            print(f"  - {path}", file=sys.stderr)
        return 1

    if guarded:
        print(
            f"Version bumped ({latest_tag} -> v{manifest['version']}) with "
            f"{len(guarded)} guarded file(s) changed - OK."
        )
    else:
        print(f"No guarded content changed since {latest_tag} - OK (version {manifest['version']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
