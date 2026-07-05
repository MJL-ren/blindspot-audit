#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE="$REPO_ROOT/skills/blindspot-audit"

if [[ ! -d "$SOURCE" ]]; then
  echo "Skill source not found: $SOURCE" >&2
  exit 1
fi

DESTINATION="${1:-$HOME/.claude/skills}"

mkdir -p "$DESTINATION"
cp -R "$SOURCE" "$DESTINATION/"

echo "Installed blindspot-audit skill to: $DESTINATION/blindspot-audit"
echo "This path is read by Claude Code, and also by OpenCode (Claude-compatible skill path)."
