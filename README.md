# Blindspot Audit

[English](./README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | [简体中文](./README.zh.md) | [Español](./README.es.md)

![Blindspot Audit hero](./docs/assets/readme/en/hero.png)

Blindspot Audit is a portable AI-agent skill that finds what a project's
owner is missing without knowing it: unknown unknowns, hidden risks, missing
decisions, stale assumptions, and questions nobody thought to ask.

It works on any kind of project — software, games, novels and creative
writing, research, content, business plans — and runs on Claude Code, Codex,
OpenCode, the Claude desktop app, and plain chat. The audit core is shared;
each host only adapts how it asks questions and writes results.

## Quick AI Install

Copy this prompt into Codex, Claude Code, OpenCode, or another coding agent.
The agent should read this repository and install the skill for the current
host or project.

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then choose the documented install route that fits this host and install scope: marketplace/plugin, Claude desktop .skill, installer script, or safe manual copy.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

## What It Does

![Four unknowns frame](./docs/assets/readme/en/four-unknowns.png)

- Profiles the project (type, stage, owner's expertise, hobby vs commercial
  intent) and reads its self-tracking docs first — anything the owner
  already tracks is filtered out, never reported as a "discovery".
- Collects the minimum project context on the first run (public/commercial
  intent, audience and regions, stage, owner strengths — every question
  skippable) and stores it in the ledger's `Project Context` section, so
  later runs read it instead of re-asking.
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

![Blindspot Audit audit flow](./docs/assets/readme/en/audit-flow.png)

This is not a generic quality checklist. The question it answers is:
"Given this specific project, what are we probably not seeing yet?"

## Repository Layout

```text
blindspot-audit/
  .agents/
    plugins/marketplace.json     # Codex plugin marketplace
  .claude-plugin/
    marketplace.json / plugin.json  # Claude Code plugin marketplace
  AGENTS.md
  CHANGELOG.md
  README.md
  README.ko.md
  README.ja.md
  README.zh.md
  README.es.md
  LICENSE
  dist/
    blindspot-audit.skill        # one-click install for the Claude desktop app
  evals/
    fixtures/                    # behavior regression fixtures with EXPECTED criteria
  examples/
    prompts.md
    sample-reports/              # synthetic reports showing the target output shape
  scripts/
    build-skill-package.py / .ps1 / .sh
    install-claude-user.ps1 / .sh
    install-claude-project.ps1 / .sh
    install-codex.ps1 / .sh
    sync-codex-plugin.py / .ps1 / .sh
    verify-codex-plugin.py
  plugins/
    blindspot-audit/
      .codex-plugin/plugin.json  # Codex plugin manifest
      skills/blindspot-audit/
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
git clone https://github.com/MJL-ren/blindspot-audit.git
cd blindspot-audit
```

### Claude Code — plugin marketplace (one-liner, with updates)

Inside Claude Code, run:

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

No clone needed, and updates arrive via `/plugin marketplace update blindspot-audit`.

### Codex — plugin marketplace

Inside Codex, add the Git marketplace and install the plugin:

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

To refresh later:

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

Start a new Codex thread after installing or upgrading so the plugin skills are loaded.

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

### Codex — manual skill install

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

If you installed it as a marketplace **plugin** inside the desktop app
instead, plugin updates are not automatic by default: run the plugin's
update check from the app's plugin management screen, or connect your
GitHub account there to enable automatic sync with this repository.

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

![BLINDSPOT_LEDGER repeat audit](./docs/assets/readme/en/ledger-diff.png)

## Maintainers

After changing `skills/blindspot-audit`, rebuild the Claude desktop package:

```powershell
.\scripts\build-skill-package.ps1
```

```bash
./scripts/build-skill-package.sh
```

Then sync and verify the Codex plugin copy:

```powershell
.\scripts\sync-codex-plugin.ps1
python .\scripts\verify-codex-plugin.py
```

```bash
./scripts/sync-codex-plugin.sh
python3 scripts/verify-codex-plugin.py
```

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
