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
cp -R "$SOURCE" "$DESTINATION/"

echo "Installed blindspot-audit skill to: $DESTINATION/blindspot-audit"

