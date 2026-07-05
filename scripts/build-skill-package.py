#!/usr/bin/env python3
"""Build dist/blindspot-audit.skill from skills/blindspot-audit."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


SKILL_NAME = "blindspot-audit"
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def build_package(repo_root: Path) -> Path:
    source = repo_root / "skills" / SKILL_NAME
    if not source.exists():
        raise SystemExit(f"Skill source not found: {source}")

    dist = repo_root / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    output = dist / f"{SKILL_NAME}.skill"

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not should_include(path):
                continue
            archive.write(path, Path(SKILL_NAME) / path.relative_to(source))

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Claude desktop .skill package.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args()

    output = build_package(args.repo_root.resolve())
    print(f"Built {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

