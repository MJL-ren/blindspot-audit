# Agent Instructions

This repository packages the `blindspot-audit` skill for AI coding agents
(Claude Code, Codex, OpenCode, and compatible hosts).

## If The User Wants To Install The Skill

Use the scripts when possible:

```powershell
.\scripts\install-claude-user.ps1                                  # Claude Code personal (~/.claude/skills) — also read by OpenCode
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\project"
.\scripts\install-codex.ps1
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

```bash
./scripts/install-claude-user.sh          # Claude Code personal (~/.claude/skills) — also read by OpenCode
./scripts/install-claude-project.sh /path/to/project
./scripts/install-codex.sh
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

Manual install — copy `skills/blindspot-audit` to one of:

- Claude Code personal: `~/.claude/skills/blindspot-audit` (OpenCode reads this too)
- Claude Code project: `<project>/.claude/skills/blindspot-audit` (OpenCode reads this too)
- Codex: `$CODEX_HOME/skills/blindspot-audit`, or `~/.codex/skills/blindspot-audit` when `CODEX_HOME` is unset
- Codex plugin marketplace: `codex plugin marketplace add MJL-ren/blindspot-audit --ref main`, then `codex plugin add blindspot-audit@blindspot-audit`
- OpenCode native: `<project>/.opencode/skills/blindspot-audit` or `~/.config/opencode/skills/blindspot-audit`
- Claude desktop app / Cowork: use `dist/blindspot-audit.skill` (Save skill button)

Do not edit the user's target project except for copying the skill into the
requested skill location.

## If The User Wants To Use The Skill From This Repo

Read `skills/blindspot-audit/SKILL.md` first. Then load only the references
needed for the task:

- `references/archetypes.md`
- `references/lenses.md`
- `references/host-surfaces.md`
- `references/ledger-lifecycle.md`
- `references/report-template.md`

For first project runs, create or propose a `BLINDSPOT_LEDGER.md` in the
best durable project docs location. For later runs, read the existing
ledger first and report the delta.

## If The Skill Itself Changes

1. Bump `version` in `.claude-plugin/plugin.json` and add a `CHANGELOG.md`
   entry.
2. Regenerate `dist/blindspot-audit.skill` so app users stay in sync with
   source users:

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

3. Sync and verify the Codex plugin copy:

```powershell
.\scripts\sync-codex-plugin.ps1
python .\scripts\verify-codex-plugin.py
```

```bash
./scripts/sync-codex-plugin.sh
python3 scripts/verify-codex-plugin.py
```

## If README.md Changes

The four translations (`README.ko.md`, `README.ja.md`, `README.zh.md`,
`README.es.md`) must be updated in the same change. Keep the section
structure identical across all five files so drift is easy to spot.

## If The User Wants To Publish The Repo

Keep the skill folder self-contained and avoid copying article text or
third-party prose into the skill. It is fine to say the project was inspired
by the unknown-unknowns workflow, but keep implementation text original.
