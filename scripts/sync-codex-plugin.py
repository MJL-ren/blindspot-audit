#!/usr/bin/env python3
"""Sync the canonical skill source into the Codex plugin bundle."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_NAME = "blindspot-audit"
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_ignore(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        path = Path(name)
        if name in EXCLUDED_DIRS or path.suffix in EXCLUDED_SUFFIXES:
            ignored.add(name)
    return ignored


def assert_child_path(child: Path, parent: Path) -> None:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    try:
        child_resolved.relative_to(parent_resolved)
    except ValueError as exc:
        raise SystemExit(f"Refusing to modify path outside plugin root: {child_resolved}") from exc


def sync_codex_plugin(repo_root: Path) -> Path:
    source = repo_root / "skills" / SKILL_NAME
    plugin_root = repo_root / "plugins" / SKILL_NAME
    target = plugin_root / "skills" / SKILL_NAME

    if not source.exists():
        raise SystemExit(f"Skill source not found: {source}")
    if not plugin_root.exists():
        raise SystemExit(f"Codex plugin root not found: {plugin_root}")

    assert_child_path(target, plugin_root)

    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=should_ignore)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync skills/blindspot-audit into the Codex plugin bundle.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args()

    target = sync_codex_plugin(args.repo_root.resolve())
    print(f"Synced Codex plugin skill copy: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
