# Blindspot Audit

Blindspot Audit is a portable AI-agent skill that finds what a project's
owner is missing without knowing it: unknown unknowns, hidden risks, missing
decisions, stale assumptions, and questions nobody thought to ask.

It works on any kind of project — software, games, novels and creative
writing, research, content, business plans — and runs on Claude Code, Codex,
OpenCode, the Claude desktop app, and plain chat. The audit core is shared;
each host only adapts how it asks questions and writes results.

[한국어 README](./README.ko.md)

## What It Does

- Profiles the project (type, stage, owner's expertise, hobby vs commercial
  intent) and reads its self-tracking docs first — anything the owner
  already tracks is filtered out, never reported as a "discovery".
- Sweeps the project with archetype-specific lenses, recording evidence for
  what exists as carefully as what's absent.
- Runs a fresh-eyes web scan for recent external changes (regulation,
  platform policy, market/genre shifts) that no project document could
  contain — historically the highest-impact findings come from here.
- Reports 3–7 ranked findings, never an unbounded checklist, and always
  includes two trust sections: "checked and well covered" and "skippable
  for now" with re-check triggers.
- Interviews the owner about which findings they already knew — a gap the
  owner knows about needs a checklist line, not a lecture.
- Keeps a durable `BLINDSPOT_LEDGER.md`; later runs diff against it and
  report only what's new or changed, so re-runs feel like progress instead
  of nagging.

This is not a generic quality checklist. The question it answers is:
"Given this specific project, what are we probably not seeing yet?"

## Repository Layout

```text
blindspot-audit/
  AGENTS.md
  README.md
  README.ko.md
  LICENSE
  dist/
    blindspot-audit.skill        # one-click install for the Claude desktop app
  examples/
    prompts.md
  scripts/
    install-claude-user.ps1 / .sh
    install-claude-project.ps1 / .sh
    install-codex.ps1 / .sh
  skills/
    blindspot-audit/
      SKILL.md
      references/
      scripts/
      templates/
```

## Install

All installers have PowerShell (`.ps1`) and Bash (`.sh`) versions. On
macOS/Linux use the `.sh` scripts (run `chmod +x scripts/*.sh` once if
needed); on Windows use `.ps1` from PowerShell, or the `.sh` versions from
Git Bash / WSL.

```bash
git clone https://github.com/<your-name>/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — personal (recommended; also covers OpenCode)

Installs to `~/.claude/skills`, which both Claude Code and OpenCode read.
One install, two hosts.

```powershell
.\scripts\install-claude-user.ps1
```

```bash
./scripts/install-claude-user.sh
```

### Claude Code — single project

Installs to `<project>/.claude/skills` (also read by OpenCode in that
project).

```powershell
.\scripts\install-claude-project.ps1 -ProjectRoot "C:\path\to\your-project"
```

```bash
./scripts/install-claude-project.sh /path/to/your-project
```

### Codex

Installs to `$CODEX_HOME/skills` when `CODEX_HOME` is set, otherwise
`~/.codex/skills`. A custom destination can be passed as an argument.

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude desktop app / Cowork

Open `dist/blindspot-audit.skill` in the Claude desktop app (attach it in
chat) and click **Save skill**. No terminal needed — this is the easiest
route for non-developers.

### Manual install

Copy the `skills/blindspot-audit` folder into any of:

```text
~/.claude/skills/blindspot-audit                    # Claude Code personal + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code project + OpenCode
~/.codex/skills/blindspot-audit                     # Codex
<project>/.opencode/skills/blindspot-audit          # OpenCode native (project)
~/.config/opencode/skills/blindspot-audit           # OpenCode native (global)
```

Then start a new agent session (or refresh) so the skill is picked up.

## Using It

On Claude Code and OpenCode, just ask naturally — the skill triggers from
its description:

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

On Codex, referencing the skill explicitly is most reliable:

```text
Use $blindspot-audit in deep mode on this project. Create or update the BLINDSPOT_LEDGER.md and give me only the highest-signal findings.
```

More examples (English and Korean) in [examples/prompts.md](./examples/prompts.md).

## How It Handles Different Agent Hosts

- Choice-capable host (Claude Code, OpenCode): asks one short question only
  when the answer changes the work, plus a single multi-select question for
  the owner-awareness interview.
- Codex / chat-only host: never blocks on questions — continues with a safe
  reversible assumption and leaves a `Decision packet` to answer later.
- Host without web access: skips the fresh-eyes scan and says so, instead
  of asserting stale knowledge about regulations or platforms.
- File-writing host: creates or updates `BLINDSPOT_LEDGER.md` by default.
- Read-only host: returns a portable report with proposed ledger entries.

## Attribution

This project was inspired by the unknown-unknowns workflow described in
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
by Thariq (@trq212) of the Claude Code team. The implementation, wording,
templates, and scripts in this repository are original work.

## License

MIT License. See [LICENSE](./LICENSE).
