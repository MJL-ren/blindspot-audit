#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE="$REPO_ROOT/skills/blindspot-audit"

if [[ ! -d "$SOURCE" ]]; then
  echo "Skill source not found: $SOURCE" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "Project root does not exist: $PROJECT_ROOT" >&2
  exit 1
fi

DESTINATION="$PROJECT_ROOT/.claude/skills"
mkdir -p "$DESTINATION"
cp -R "$SOURCE" "$DESTINATION/"

echo "Installed blindspot-audit skill to: $DESTINATION/blindspot-audit"

