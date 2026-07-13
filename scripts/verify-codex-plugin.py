#!/usr/bin/env python3
"""Verify the Codex plugin bundle, marketplace metadata, and version alignment."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
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


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def verify_png_asset(plugin_root: Path, field: str, relative_path: object) -> list[str]:
    """Verify a manifest PNG asset without adding an image-library dependency."""
    if not isinstance(relative_path, str) or not relative_path:
        return [f"plugin.json interface.{field} must be a non-empty path"]

    root = plugin_root.resolve()
    asset = (root / relative_path).resolve()
    try:
        asset.relative_to(root)
    except ValueError:
        return [f"plugin.json interface.{field} must stay inside the plugin root"]

    if not asset.is_file():
        return [f"plugin.json interface.{field} asset is missing: {relative_path}"]
    if asset.suffix.lower() != ".png":
        return [f"plugin.json interface.{field} must point to a PNG asset"]

    header = asset.read_bytes()[:26]
    if len(header) < 26 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return [f"plugin.json interface.{field} is not a valid PNG: {relative_path}"]

    width, height = struct.unpack(">II", header[16:24])
    color_type = header[25]
    errors: list[str] = []
    if width != height or width < 256:
        errors.append(
            f"plugin.json interface.{field} PNG must be square and at least 256px; "
            f"found {width}x{height}"
        )
    if color_type not in {4, 6}:
        errors.append(
            f"plugin.json interface.{field} PNG must have an alpha channel for theme-safe rendering"
        )
    return errors


def compare_skill_copy(repo_root: Path) -> list[str]:
    source = repo_root / "skills" / SKILL_NAME
    target = repo_root / "plugins" / SKILL_NAME / "skills" / SKILL_NAME
    errors: list[str] = []

    if not source.exists():
        return [f"Missing canonical skill source: {source}"]
    if not target.exists():
        return [f"Missing Codex plugin skill copy: {target}"]

    source_files = {
        path.relative_to(source).as_posix(): path
        for path in sorted(source.rglob("*"))
        if should_include(path)
    }
    target_files = {
        path.relative_to(target).as_posix(): path
        for path in sorted(target.rglob("*"))
        if should_include(path)
    }

    missing = sorted(set(source_files) - set(target_files))
    extra = sorted(set(target_files) - set(source_files))
    if missing:
        errors.append("Missing Codex plugin skill entries: " + ", ".join(missing))
    if extra:
        errors.append("Unexpected Codex plugin skill entries: " + ", ".join(extra))

    for name in sorted(set(source_files) & set(target_files)):
        if source_files[name].read_bytes() != target_files[name].read_bytes():
            errors.append(f"Codex plugin skill entry differs from source: {name}")

    return errors


def verify_plugin_manifest(repo_root: Path) -> list[str]:
    path = repo_root / "plugins" / SKILL_NAME / ".codex-plugin" / "plugin.json"
    if not path.exists():
        return [f"Missing Codex plugin manifest: {path}"]

    manifest = load_json(path)
    errors: list[str] = []
    required = {
        "name": SKILL_NAME,
        "description": str,
        "version": str,
        "skills": "./skills/",
    }
    for key, expected in required.items():
        if isinstance(expected, str):
            if manifest.get(key) != expected:
                errors.append(f"plugin.json {key!r} must be {expected!r}")
        elif not isinstance(manifest.get(key), expected):
            errors.append(f"plugin.json {key!r} must be a {expected.__name__}")

    author = manifest.get("author")
    if not isinstance(author, dict) or not author.get("name"):
        errors.append("plugin.json author.name is required")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json interface object is required")
    else:
        for key in ["displayName", "shortDescription", "longDescription", "developerName", "category"]:
            if not interface.get(key):
                errors.append(f"plugin.json interface.{key} is required")
        prompts = interface.get("defaultPrompt")
        if not isinstance(prompts, list) or not prompts:
            errors.append("plugin.json interface.defaultPrompt must be a non-empty list")
        elif any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in prompts[:3]):
            errors.append("plugin.json interface.defaultPrompt entries must be strings of 128 chars or fewer")
        plugin_root = path.parent.parent
        for field in ["composerIcon", "logo"]:
            errors.extend(verify_png_asset(plugin_root, field, interface.get(field)))

    if "[TODO:" in path.read_text(encoding="utf-8"):
        errors.append("plugin.json contains a TODO placeholder")

    return errors


def verify_marketplace(repo_root: Path) -> list[str]:
    path = repo_root / ".agents" / "plugins" / "marketplace.json"
    if not path.exists():
        return [f"Missing Codex marketplace manifest: {path}"]

    marketplace = load_json(path)
    errors: list[str] = []
    if marketplace.get("name") != SKILL_NAME:
        errors.append(f"marketplace name must be {SKILL_NAME!r}")
    if marketplace.get("interface", {}).get("displayName") != "Blindspot Audit":
        errors.append("marketplace interface.displayName must be 'Blindspot Audit'")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append("marketplace plugins must be a list")
        return errors

    entry = next((plugin for plugin in plugins if plugin.get("name") == SKILL_NAME), None)
    if entry is None:
        errors.append(f"marketplace missing {SKILL_NAME!r} plugin entry")
        return errors

    if entry.get("source") != {"source": "local", "path": f"./plugins/{SKILL_NAME}"}:
        errors.append("marketplace source must point at ./plugins/blindspot-audit")
    if entry.get("policy", {}).get("installation") != "AVAILABLE":
        errors.append("marketplace policy.installation must be AVAILABLE")
    if entry.get("policy", {}).get("authentication") != "ON_INSTALL":
        errors.append("marketplace policy.authentication must be ON_INSTALL")
    if entry.get("category") != "Productivity":
        errors.append("marketplace category must be Productivity")

    return errors


def verify_version_alignment(repo_root: Path) -> list[str]:
    """Assert the Codex manifest and CHANGELOG agree with the canonical version.

    The canonical version lives in .claude-plugin/plugin.json. The Codex
    manifest version is maintained by hand - sync-codex-plugin.py only copies
    skill files, not the manifest - so a release bump can silently miss it
    (it did between 0.3.3 and 0.3.4). This gate fails CI loudly instead of
    shipping a mislabeled release.
    """
    canonical_path = repo_root / ".claude-plugin" / "plugin.json"
    if not canonical_path.exists():
        return [f"Missing canonical plugin manifest: {canonical_path}"]

    canonical_version = load_json(canonical_path).get("version")
    if not isinstance(canonical_version, str) or not canonical_version:
        return [f"Canonical version missing or not a string in {canonical_path}"]

    errors: list[str] = []

    codex_path = repo_root / "plugins" / SKILL_NAME / ".codex-plugin" / "plugin.json"
    if codex_path.exists():
        codex_version = load_json(codex_path).get("version")
        if codex_version != canonical_version:
            errors.append(
                f"Codex plugin.json version {codex_version!r} != canonical "
                f"{canonical_version!r} (.claude-plugin/plugin.json); bump both together."
            )

    changelog_path = repo_root / "CHANGELOG.md"
    if not changelog_path.exists():
        errors.append(f"Missing CHANGELOG.md: {changelog_path}")
    else:
        match = re.search(
            r"^##\s*\[(\d+\.\d+\.\d+)\]",
            changelog_path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if match is None:
            errors.append("CHANGELOG.md has no '## [x.y.z]' version heading")
        elif match.group(1) != canonical_version:
            errors.append(
                f"CHANGELOG.md newest entry {match.group(1)!r} != canonical "
                f"{canonical_version!r}; add a CHANGELOG entry for the release."
            )

    return errors


def verify(repo_root: Path) -> int:
    errors = []
    errors.extend(verify_plugin_manifest(repo_root))
    errors.extend(verify_marketplace(repo_root))
    errors.extend(verify_version_alignment(repo_root))
    errors.extend(compare_skill_copy(repo_root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Verified Codex plugin marketplace and skill copy")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Codex plugin metadata and synced skill copy.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args()
    return verify(args.repo_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
