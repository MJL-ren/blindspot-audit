#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE="$REPO_ROOT/skills/blindspot-audit"

if [[ ! -d "$SOURCE" ]]; then
  echo "Skill source not found: $SOURCE" >&2
  exit 1
fi

if [[ $# -ge 1 ]]; then
  DESTINATION="$1"
elif [[ -n "${CODEX_HOME:-}" ]]; then
  DESTINATION="$CODEX_HOME/skills"
else
  DESTINATION="$HOME/.codex/skills"
fi

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
