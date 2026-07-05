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

# Replace, don't merge: an overwrite-copy leaves files that were renamed or
# deleted upstream lingering in the install, silently steering agents.
INSTALL_PATH="$DESTINATION/blindspot-audit"
if [[ -e "$INSTALL_PATH" ]]; then
  if [[ "$(basename "$INSTALL_PATH")" != "blindspot-audit" ]]; then
    echo "Refusing to remove unexpected path: $INSTALL_PATH" >&2
    exit 1
  fi
  rm -rf "$INSTALL_PATH"
fi
cp -R "$SOURCE" "$DESTINATION/"

echo "Installed blindspot-audit skill to: $INSTALL_PATH (previous install replaced)"
echo "This path is read by Claude Code, and also by OpenCode (Claude-compatible skill path)."
