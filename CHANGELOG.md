# Changelog

All notable changes to the blindspot-audit skill and this repository.

## [0.3.4] - 2026-07-05

Field feedback from the first registered Claude Code run (grenomj-v3 audit,
Opus review): the thinking frame held; all friction was in tooling and host
adaptation.

### Fixed

- `project_inventory.py` doc detection (Ground Rule 1's foundation): any
  root-level `.md`/`.mdx`/`.txt`/`.rst` is now a doc candidate, and
  RUNBOOK/GUIDE/FORM/HANDBOOK/CHECKLIST/NOTES-style names are recognized
  anywhere in the tree. Previously `COMMISSION_ORDER_RUNBOOK.md` at root was
  counted in extensions but missed by the docs section, silently weakening
  the self-tracking-doc filter.
- `project_inventory.py` config detection: Cloudflare Pages/Workers,
  Netlify, and Vercel files (`_headers`, `_redirects`, `_routes.json`,
  `wrangler.*`, `netlify.toml`, `vercel.json`) are now recognized, plus a
  new "Config hints (common-but-missing)" section (e.g. Pages files without
  `wrangler.*`, `package.json` without a lockfile).

### Added

- Structured-choice option cap rule in `references/host-surfaces.md`:
  Claude Code's `AskUserQuestion` caps options at 4, so 5-7 findings must
  split into two questions or fall back to the numbered awareness check -
  a UI limit must not shrink the audit.
- Public/private boundary rule for ledger placement (SKILL.md +
  `references/ledger-lifecycle.md`): the ledger inherits the project's
  PRIVATE side; verify it stays out of deploys/exports (404 check or export
  denylist).
- OS and shell notes in `references/host-surfaces.md`: prefer native file
  tools over `rg`, `py` launcher fallback on Windows, quote paths with
  spaces.
- Skill-folder glob fallback in SKILL.md Quick Start
  (`**/blindspot-audit/scripts/project_inventory.py`).

### Changed

- Quick Start inventory command fence changed from `bash` to `text` with
  quoted paths (the same command may run under PowerShell).
- Bumped plugin metadata to `0.3.4`.

## [0.3.3] - 2026-07-05

Follow-up usability pass for hosts without a structured choice UI.

### Changed

- Replaced the no-choice awareness packet with a numbered awareness check:
  owners can reply with `1, 3`, `I already knew 1 and 3`, or localized
  variants such as `1번, 3번 알고 있어`.
- Added parsing guidance for short qualifiers: documented/tracked,
  intentionally deferred, and wrong/not applicable items.
- Kept structured choice tool behavior unchanged; this change only affects
  no-choice/chat/API-style surfaces.
- Bumped plugin metadata to `0.3.3`.

## [0.3.2] - 2026-07-05

Field feedback from the first registered plugin run on a host without a
structured choice UI.

### Added

- A generalized "No Structured Choice Tool" flow in `references/host-surfaces.md`:
  finish the audit, mark awareness as `unconfirmed`, include an
  `Awareness reply format`, and update the ledger later from the owner's
  one-message classifications instead of blocking the audit.
- `Awareness reply format` guidance in `references/report-template.md`.
- Ledger traceability guidance in `references/ledger-lifecycle.md`: when a
  project uses version control, check whether the ledger and routing edits
  are part of the durable tracked state, not just present on disk.

### Changed

- Reframed host guidance around capabilities (`structured choice tool`,
  `no structured choice tool`, `read-only`) instead of one product-specific
  adapter.
- Updated the ledger template host column to use generic host-surface labels.
- Bumped plugin metadata to `0.3.2`.

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
