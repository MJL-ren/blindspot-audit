#!/usr/bin/env python3
"""Verify dist/blindspot-audit.skill contains the current skill source files."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import zipfile
from pathlib import Path


def load_builder(repo_root: Path):
    builder_path = repo_root / "scripts" / "build-skill-package.py"
    spec = importlib.util.spec_from_file_location("build_skill_package", builder_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load builder script: {builder_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_entries(repo_root: Path, builder) -> dict[str, bytes]:
    source = repo_root / "skills" / builder.SKILL_NAME
    if not source.exists():
        raise SystemExit(f"Skill source not found: {source}")

    entries: dict[str, bytes] = {}
    for path in sorted(source.rglob("*")):
        if not builder.should_include(path):
            continue
        archive_path = f"{builder.SKILL_NAME}/{path.relative_to(source).as_posix()}"
        entries[archive_path] = builder.package_bytes(path)
    return entries


def verify_package(repo_root: Path) -> int:
    builder = load_builder(repo_root)
    package_path = repo_root / "dist" / f"{builder.SKILL_NAME}.skill"
    if not package_path.exists():
        print(f"Package not found: {package_path}", file=sys.stderr)
        return 1

    expected = expected_entries(repo_root, builder)

    with zipfile.ZipFile(package_path) as archive:
        actual_names = sorted(info.filename for info in archive.infolist() if not info.is_dir())
        expected_names = sorted(expected)

        if actual_names != expected_names:
            missing = sorted(set(expected_names) - set(actual_names))
            extra = sorted(set(actual_names) - set(expected_names))
            if missing:
                print("Missing package entries:", file=sys.stderr)
                for name in missing:
                    print(f"  - {name}", file=sys.stderr)
            if extra:
                print("Unexpected package entries:", file=sys.stderr)
                for name in extra:
                    print(f"  - {name}", file=sys.stderr)
            return 1

        mismatched = []
        for name, expected_bytes in expected.items():
            if archive.read(name) != expected_bytes:
                mismatched.append(name)

    if mismatched:
        print("Package entries differ from source:", file=sys.stderr)
        for name in mismatched:
            print(f"  - {name}", file=sys.stderr)
        return 1

    print(f"Verified {package_path} ({len(expected)} entries)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the committed Claude desktop .skill package.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args()
    return verify_package(args.repo_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
