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
else
  DESTINATION="$HOME/.agents/skills"
fi

mkdir -p "$DESTINATION"
DESTINATION="$(cd "$DESTINATION" && pwd -P)"

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

LEGACY_DESTINATIONS=("$HOME/.codex/skills")
if [[ -n "${CODEX_HOME:-}" ]]; then
  LEGACY_DESTINATIONS+=("$CODEX_HOME/skills")
fi

SEEN_LEGACY_PATHS="|"
for LEGACY_DESTINATION in "${LEGACY_DESTINATIONS[@]}"; do
  LEGACY_INSTALL_PATH="$LEGACY_DESTINATION/blindspot-audit"
  if [[ ! -d "$LEGACY_INSTALL_PATH" ]]; then
    continue
  fi

  LEGACY_DESTINATION="$(cd "$LEGACY_DESTINATION" && pwd -P)"
  if [[ "$LEGACY_DESTINATION" == "$DESTINATION" || "$SEEN_LEGACY_PATHS" == *"|$LEGACY_DESTINATION|"* ]]; then
    continue
  fi
  SEEN_LEGACY_PATHS+="$LEGACY_DESTINATION|"

  echo "Warning: Legacy Codex skill copy found at: $LEGACY_DESTINATION/blindspot-audit" >&2
  echo "Current Codex uses ~/.agents/skills by default, and same-name copies can both appear." >&2
  echo "This installer does not delete legacy copies; remove or migrate it manually after confirming the new install." >&2
done
