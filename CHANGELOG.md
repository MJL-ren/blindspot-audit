# Changelog

All notable changes to the blindspot-audit skill and this repository.

## [0.3.1] - 2026-07-05

Field feedback from the first registered Cowork run (World_Lore audit).

### Added

- Cowork (Claude desktop app) adapter in `references/host-surfaces.md`:
  plugin folder may not be shell-reachable (copy scripts via file tools),
  shell sandbox mirror can lag or truncate files on mid-session folders
  (trust file tools; never run destructive git from an unverified mirror).
- "Keep The Ledger Compact" rules in `references/ledger-lifecycle.md` plus
  matching SKILL.md diff-run steps: same-session remediation must be marked
  `resolved` before finishing, and closed items compress into a one-line
  Resolved Archive so the ledger never grows unbounded.
- `Resolved Archive` section in `templates/BLINDSPOT_LEDGER.md`.
- SKILL.md Quick Start note for hosts where the skill folder is not
  shell-accessible.

### Changed

- `project_inventory.py`: the security-keyword section is now labeled as a
  name-based heuristic to avoid false alarms on creative files (e.g.
  `Reveals_And_Secrets.md` in a story project).
- Bumped plugin metadata to `0.3.1`.

## [0.3.0] - 2026-07-05

### Added

- Codex plugin marketplace support:
  `codex plugin marketplace add MJL-ren/blindspot-audit --ref main`, then
  `codex plugin add blindspot-audit@blindspot-audit`.
- Codex plugin bundle under `plugins/blindspot-audit/`, with a validated
  `.codex-plugin/plugin.json` and a synced skill copy.
- `sync-codex-plugin` and `verify-codex-plugin` scripts, plus CI coverage for
  the Codex plugin marketplace and skill-copy consistency.

### Changed

- Bumped plugin metadata to `0.3.0`.
- Updated all READMEs and `AGENTS.md` with Codex plugin install and maintenance
  instructions.

## [0.2.0] - 2026-07-05

### Added

- Claude Code plugin marketplace support: `/plugin marketplace add MJL-ren/blindspot-audit`
  (`.claude-plugin/marketplace.json` + `plugin.json`).
- Multilingual READMEs (English, Korean, Japanese, Simplified Chinese, Spanish)
  with a language switcher and a copy-paste "Quick AI Install" prompt.
- `build-skill-package` scripts (`.py` / `.ps1` / `.sh`) and a refreshed
  `dist/blindspot-audit.skill` for Claude desktop app users.
- `install-claude-user` scripts — Claude Code personal install
  (`~/.claude/skills`), also read by OpenCode.
- GitHub Actions CI for `dist/blindspot-audit.skill` source/package content
  consistency plus Bash and PowerShell script syntax checks.
- This changelog.

### Changed

- Merged the Claude-side audit design into the skill core: self-tracking-doc
  filter, 3-7 finding cap with mandatory trust sections, fresh-eyes external
  change scan, owner-awareness interview (`unknown_known` findings get a
  documentation prescription, not a lecture), cross-host adapters
  (Claude Code / Codex / OpenCode / chat-only, including a no-web fallback),
  and a portable inventory-script path.
- Naturalness fixes in the Japanese and Spanish READMEs.

## [0.1.0] - 2026-07-05

### Added

- Initial public structure: the skill itself (`SKILL.md`, references,
  templates, project inventory script), installers for Codex and Claude Code
  project scope, MIT license, English/Korean READMEs.
