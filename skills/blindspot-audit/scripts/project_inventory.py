#!/usr/bin/env python3
"""Create a compact project inventory for blindspot audits."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".turbo",
    ".cache",
    ".idea",
    ".vscode",
    "external_repos",
    "vendor",
    "runtime",
    ".playwright-mcp",
    "coverage",
    ".ipynb_checkpoints",
    "wandb",
    "mlruns",
    "DerivedData",
}

IGNORE_PREFIXES = (
    ".uv-",
    ".tmp",
    "tmp",
)

IGNORE_SUFFIXES = {".meta"}  # Unity sidecar files; thousands per project, zero doc signal

# Engine project roots are detected per-directory during the walk (they are
# often nested, e.g. <repo>/UnityProject/<Game>/), and their generated dirs
# are pruned only under a confirmed engine root - so a non-engine project
# with a folder named "Library" is unaffected.
ENGINE_GENERATED = {
    "unity": ("Library", "Temp", "Obj", "Logs", "UserSettings", "MemoryCaptures", "Build", "Builds"),
    "unreal": ("Binaries", "DerivedDataCache", "Intermediate", "Saved"),
    "godot": (".godot", ".import"),
}

DOC_NAMES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "LICENSE",
}

DOC_EXTS = {".md", ".mdx", ".txt", ".rst"}
# Name patterns that mark a file as documentation wherever it lives.
# Ground Rule 1 (the self-tracking-doc filter) depends on catching these:
# a missed RUNBOOK or FORM doc silently breaks the audit's noise filter.
DOC_NAME_HINTS = (
    "readme",
    "runbook",
    "guide",
    "handbook",
    "manual",
    "howto",
    "form",
    "checklist",
    "policy",
    "plan",
    "spec",
    "notes",
    "faq",
    "todo",
    "roadmap",
)
DOC_PATH_HINTS = ("docs", "doc", "plans", "research", "decisions", "notes", "wiki")

CONFIG_NAMES = {
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "Cargo.toml",
    "go.mod",
    "deno.json",
    "tsconfig.json",
    "vite.config.ts",
    "next.config.js",
    "next.config.ts",
    "docker-compose.yml",
    "Dockerfile",
    # Deploy-platform configs (Cloudflare Pages/Workers, Netlify, Vercel).
    # These are easy to miss because some have no extension at all.
    "_headers",
    "_redirects",
    "_routes.json",
    "wrangler.toml",
    "wrangler.json",
    "wrangler.jsonc",
    "netlify.toml",
    "vercel.json",
}

LOCKFILE_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"}
CLOUDFLARE_PAGES_HINTS = {"_headers", "_redirects", "_routes.json"}

ENV_PATTERNS = (".env", ".env.example", ".env.local", ".env.template")
TEST_HINTS = ("test", "tests", "spec", "__tests__", "playwright", "vitest", "pytest", "jest")
AI_HINTS = ("prompt", "prompts", "agent", "agents", "skill", "skills", "eval", "evals", "model")
SECURITY_HINTS = ("auth", "oauth", "token", "secret", "security", "permission", "policy", "login")
DATA_HINTS = ("schema", "migration", "db", "database", "duckdb", "sqlite", "csv", "parquet")
TEST_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java", ".cs", ".rb", ".php", ".md", ".toml", ".ini", ".yml", ".yaml", ".json"}


def iter_files(root: Path, max_files: int, ignore_dirs: set[str], engine_hints: set[str] | None = None) -> Iterable[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # Per-directory engine detection: prune generated dirs directly under
        # a confirmed engine project root, wherever it is nested.
        pruned: set[str] = set()
        dirset = set(dirnames)
        if {"Assets", "ProjectSettings"} <= dirset:
            if engine_hints is not None:
                engine_hints.add("Unity")
            pruned.update(ENGINE_GENERATED["unity"])
        if any(f.endswith(".uproject") for f in filenames):
            if engine_hints is not None:
                engine_hints.add("Unreal")
            pruned.update(ENGINE_GENERATED["unreal"])
        if "project.godot" in filenames:
            if engine_hints is not None:
                engine_hints.add("Godot")
            pruned.update(ENGINE_GENERATED["godot"])
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ignore_dirs
            and d not in pruned
            and not any(d.startswith(prefix) for prefix in IGNORE_PREFIXES)
        ]
        current = Path(dirpath)
        for filename in filenames:
            if any(filename.endswith(suffix) for suffix in IGNORE_SUFFIXES):
                continue
            path = current / filename
            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path
            if any(part in IGNORE_DIRS for part in rel.parts):
                continue
            count += 1
            if count > max_files:
                return
            yield path


def rel_list(paths: Iterable[Path], root: Path, limit: int = 25) -> list[str]:
    values = []
    for path in paths:
        try:
            values.append(str(path.relative_to(root)).replace("\\", "/"))
        except ValueError:
            values.append(str(path))
        if len(values) >= limit:
            break
    return values


def has_any(text: str, hints: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(h in lower for h in hints)


def is_doc_file(path: Path, root: Path) -> bool:
    if path.name in DOC_NAMES:
        return True
    if path.suffix.lower() not in DOC_EXTS:
        return False
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    # Any root-level markdown/text file is a doc candidate: this is where
    # RUNBOOK.md, ORDER_FORM.md, INTERNAL_README.md style files live.
    if len(rel.parts) == 1:
        return True
    rel_str = str(rel).replace("\\", "/").lower()
    if any(f"/{hint}/" in f"/{rel_str}" or rel_str.startswith(f"{hint}/") for hint in DOC_PATH_HINTS):
        return True
    return has_any(path.stem, DOC_NAME_HINTS)


def is_test_file(path: Path, root: Path) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/").lower()
    parts = set(Path(rel).parts)
    name = path.name.lower()
    if path.suffix.lower() and path.suffix.lower() not in TEST_EXTS:
        return False
    if parts & {"test", "tests", "__tests__"}:
        return True
    if any(marker in name for marker in (".test.", ".spec.", "_test.", "-test.")):
        return True
    return name in {
        "pytest.ini",
        "vitest.config.ts",
        "vitest.config.js",
        "jest.config.js",
        "jest.config.ts",
        "playwright.config.ts",
        "playwright.config.js",
    }


def is_ci_file(path: Path, root: Path) -> bool:
    rel = str(path.relative_to(root)).replace("\\", "/").lower()
    name = path.name.lower()
    if rel.startswith(".github/workflows/"):
        return True
    if rel.startswith(".gitlab-ci"):
        return True
    return name in {
        "ci.yml",
        "ci.yaml",
        "build.yml",
        "build.yaml",
        "azure-pipelines.yml",
        "circleci.yml",
    }


def detect_frameworks(files: list[Path], root: Path) -> list[str]:
    names = {p.name for p in files}
    rels = {str(p.relative_to(root)).replace("\\", "/") for p in files if p.exists()}
    frameworks = []
    if "package.json" in names:
        package = root / "package.json"
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            deps = {}
            deps.update(data.get("dependencies", {}))
            deps.update(data.get("devDependencies", {}))
            for key, label in [
                ("next", "Next.js"),
                ("react", "React"),
                ("vue", "Vue"),
                ("svelte", "Svelte"),
                ("vite", "Vite"),
                ("express", "Express"),
                ("fastify", "Fastify"),
                ("playwright", "Playwright"),
                ("vitest", "Vitest"),
                ("jest", "Jest"),
                ("@anthropic-ai/claude-code", "Claude Code"),
                ("openai", "OpenAI SDK"),
            ]:
                if key in deps:
                    frameworks.append(label)
        except Exception:
            frameworks.append("package.json present")
    if "pyproject.toml" in names:
        frameworks.append("Python/pyproject")
    if "Cargo.toml" in names:
        frameworks.append("Rust/Cargo")
    if "go.mod" in names:
        frameworks.append("Go modules")
    if any(r.startswith(".github/workflows/") for r in rels):
        frameworks.append("GitHub Actions")
    if "Dockerfile" in names or "docker-compose.yml" in names:
        frameworks.append("Docker")
    return sorted(set(frameworks))


def build_inventory(root: Path, max_files: int, include_generated: bool = False) -> dict:
    root = root.resolve()
    ignore_dirs = set(IGNORE_DIRS)
    if include_generated:
        ignore_dirs.discard("runtime")
        ignore_dirs.discard(".playwright-mcp")
    engine_hints: set[str] = set()
    files = list(iter_files(root, max_files=max_files, ignore_dirs=ignore_dirs, engine_hints=engine_hints))
    ext_counts = Counter(p.suffix.lower() or "[none]" for p in files)
    top_dirs = Counter((p.relative_to(root).parts[0] if len(p.relative_to(root).parts) > 1 else ".") for p in files)

    docs = [p for p in files if is_doc_file(p, root)]
    configs = [
        p
        for p in files
        if p.name in CONFIG_NAMES
        or p.name.startswith("wrangler.")
        or (p.name.startswith(".") and has_any(p.name, ("config", "rc")))
    ]
    envs = [p for p in files if p.name in ENV_PATTERNS or p.name.startswith(".env")]
    tests = [p for p in files if is_test_file(p, root)]
    ai_files = [p for p in files if has_any(str(p.relative_to(root)), AI_HINTS) or p.name in {"AGENTS.md", "CLAUDE.md", "SKILL.md"}]
    security_files = [p for p in files if has_any(str(p.relative_to(root)), SECURITY_HINTS)]
    data_files = [p for p in files if has_any(str(p.relative_to(root)), DATA_HINTS)]
    ci_files = [p for p in files if is_ci_file(p, root)]

    # Common-but-missing config hints: presence of one platform artifact
    # often implies a sibling that is worth checking for. These are hints
    # for the auditor, not findings by themselves.
    names = {p.name for p in files}
    config_hints: list[str] = []
    if names & CLOUDFLARE_PAGES_HINTS and not any(n.startswith("wrangler.") for n in names):
        config_hints.append(
            "Cloudflare Pages files (_headers/_redirects/_routes.json) present but no wrangler.* found - deployment config may live only in the dashboard (not versioned)"
        )
    if "package.json" in names and not (names & LOCKFILE_NAMES):
        config_hints.append("package.json present without a lockfile - installs are not reproducible")

    return {
        "root": str(root),
        "file_count_sampled": len(files),
        "max_files": max_files,
        "truncated": len(files) >= max_files,
        "include_generated": include_generated,
        "extensions": ext_counts.most_common(20),
        "top_dirs": top_dirs.most_common(20),
        "frameworks": sorted(set(detect_frameworks(files, root)) | {f"{e} (engine dirs auto-skipped)" for e in engine_hints}),
        "docs": rel_list(docs, root),
        "configs": rel_list(configs, root),
        "config_hints": config_hints,
        "env_files": rel_list(envs, root),
        "tests": rel_list(tests, root),
        "ci": rel_list(ci_files, root),
        "ai_files": rel_list(ai_files, root),
        "security_related": rel_list(security_files, root),
        "data_related": rel_list(data_files, root),
    }


def emit_markdown(inv: dict) -> str:
    lines = [
        f"# Project Inventory",
        "",
        f"- Root: `{inv['root']}`",
        f"- Files sampled: {inv['file_count_sampled']} / max {inv['max_files']}" + (" (truncated)" if inv["truncated"] else ""),
        *(
            [
                "- NOTE: sampling was truncated - docs/code may be underrepresented. "
                "Re-run scoped to the docs and source directories (or raise --max-files) "
                "before trusting absence claims."
            ]
            if inv["truncated"]
            else []
        ),
        f"- Generated/runtime artifacts included: {'yes' if inv['include_generated'] else 'no'}",
        f"- Framework hints: {', '.join(inv['frameworks']) if inv['frameworks'] else 'none detected'}",
        "",
        "## Top directories",
    ]
    lines.extend(f"- `{name}`: {count}" for name, count in inv["top_dirs"][:12])
    lines.append("")
    lines.append("## Extensions")
    lines.extend(f"- `{ext}`: {count}" for ext, count in inv["extensions"][:12])
    for key, title in [
        ("docs", "Docs and plans"),
        ("configs", "Configs"),
        ("config_hints", "Config hints (common-but-missing)"),
        ("env_files", "Env files"),
        ("tests", "Tests"),
        ("ci", "CI"),
        ("ai_files", "AI/prompt/agent files"),
        ("security_related", "Sensitive-name matches (name-based heuristic; in creative projects these are often story/spoiler docs, not security surfaces)"),
        ("data_related", "Data/schema related"),
    ]:
        lines.append("")
        lines.append(f"## {title}")
        values = inv[key]
        if values:
            lines.extend(f"- `{v}`" for v in values)
        else:
            lines.append("- none found in sampled files")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a compact project inventory for blindspot audits.")
    parser.add_argument("root", type=Path, help="Project root to inspect")
    parser.add_argument("--max-files", type=int, default=5000, help="Maximum files to sample")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--include-generated", action="store_true", help="Include common generated/runtime artifact directories")
    args = parser.parse_args()

    if not args.root.exists():
        raise SystemExit(f"Project root does not exist: {args.root}")
    inv = build_inventory(args.root, args.max_files, include_generated=args.include_generated)
    if args.format == "json":
        print(json.dumps(inv, indent=2, ensure_ascii=False))
    else:
        print(emit_markdown(inv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
