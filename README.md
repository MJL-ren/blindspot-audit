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

It is especially useful for AI-assisted and vibe-coded projects where the
owner moved fast, shipped ideas quickly, and now needs a calm pass over what
may have been missed.

## Install in 60 seconds

| You use | One line |
| --- | --- |
| Any coding agent — Claude Code, Codex, OpenCode, Cursor, ~70 hosts | `npx skills add MJL-ren/blindspot-audit` |
| Claude Code, with managed updates | `/plugin marketplace add MJL-ren/blindspot-audit` then `/plugin install blindspot-audit@blindspot-audit` |
| Claude desktop app / Cowork — no terminal | Download [blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill), attach it in chat, click **Save skill** |

Then try your first prompt:

```text
Run a blindspot audit on this project. What am I missing that I don't even know to ask about?
```

The `npx` route uses [vercel-labs/skills](https://github.com/vercel-labs/skills):
it installs the whole skill folder and sends anonymous install telemetry
(opt out with `DISABLE_TELEMETRY=1`). The skill itself never touches the
network on its own — see [SECURITY.md](./SECURITY.md). More routes —
per-project installs, Codex marketplace, offline scripts, letting your
agent do it — in [Install](#install).

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
- Narrows on demand: a `focus: ux-ui` run loads a deep probe pack for that
  one domain, and full audits flag weak-domain surfaces they only skimmed
  (an engineer-owner's UI, a designer-owner's operations) instead of
  silently passing them. More packs over time.
- Keeps a durable `BLINDSPOT_LEDGER.md` — the audit's notebook file in
  your project; later runs diff against it and
  report only what's new or changed, so re-runs feel like progress instead
  of nagging - and when nothing changed, the run descends one tier deeper
  (un-run packs, watchlist re-checks, least-inspected subsystem) instead
  of coming back empty.

![Blindspot Audit audit flow](./docs/assets/readme/en/audit-flow.png)

## What a finding looks like

A weak audit says "No GDPR Article 13 privacy notice." This skill is built
to say it so you can recognize and act on it:

```markdown
1. The site collects email addresses but never tells people what happens
   to them
   - In plain terms: when a site stores personal data like emails, most
     regions require a short public note (a "privacy policy") saying what
     is collected and how to get it deleted. It is a page, not a lawsuit -
     but its absence can become one.
   - Why it matters: the signup form is live and EU visitors can reach it;
     this is the kind of gap that is cheap now and expensive after launch.
   - Cheapest check: read one privacy-policy generator's output (10 min)
     and confirm with a professional before launch - this audit is a
     scout, not a lawyer.
```

Five full synthetic reports live in
[examples/sample-reports/](./examples/sample-reports/) — start with
[weak-vs-strong.md](./examples/sample-reports/weak-vs-strong.md), which
shows the same three findings written to fail and to pass. Real reports
are written in whatever language you work in; only IDs and status values
stay English.

## Your first audit

1. Ask in plain words (prompts in [Using It](#using-it)).
2. On a first run the skill asks 1–2 short context questions — every one
   skippable.
3. You get 3–7 ranked findings, plus what is already well covered and
   what you can safely skip for now.
4. It asks which findings you already knew about — a known gap gets a
   checklist line instead of a lecture.
5. It leaves ONE file behind: `BLINDSPOT_LEDGER.md`, the audit's notebook
   in your project. Re-runs read it and report only what changed. The
   file is yours — commit it, or add it to `.gitignore`.

## Why not just ask "what am I missing?"

A plain "review my project" prompt starts from zero every time: it
re-discovers what you already track, lectures where a checklist line
would do, and forgets everything by the next session. This skill filters
your own tracking docs out of the findings, interviews you so known gaps
are treated differently from real blind spots, and diffs against the
ledger so re-runs report progress instead of repeating themselves.

How to know it is working: a re-run reports deltas, not the same list
twice; findings name a concrete consequence and the cheapest next check,
never a generic best practice; and every release is graded against real
field runs — see [evals/RUNS.md](./evals/RUNS.md).

## Focus: UX/UI

![Blindspot Audit UX/UI focus](./docs/assets/readme/en/ux-ui-focus.png)

`focus: ux-ui` is for projects with real user-facing screens where a broad
audit would only skim the interface. It walks screens, flows, states, inputs,
accessibility, and feedback as blind-spot questions: what was never decided,
where users may get stuck, and what cheap check would make the gap visible.

Use it when a full audit flags UX/UI as coverage debt, or when the owner is
strong elsewhere and wants a deeper pass on the user surface.

This is not a generic quality checklist. The question it answers is:
"Given this specific project, what are we probably not seeing yet?"

## Ledger Triage

`mode: ledger-triage` is for a project that already has a busy
`BLINDSPOT_LEDGER.md`. It does not run a new audit. It reads the existing
ledger, groups open rows into quick cleanup, safe accepts, bundled
decisions, owner-detail questions, external confirmations, and items that
need a simpler explanation.

On hosts without a structured choice UI, large triage batches can use a
temporary self-contained HTML decision board under `.blindspot-tmp/`. The
owner selects answers in the browser, the agent validates the response JSON,
applies only the chosen ledger updates, then deletes the temporary board.
Recommendations in the board are not applied until the owner chooses them.

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

The three recommended routes are in
[Install in 60 seconds](#install-in-60-seconds) above. Everything below
is the full menu — no route here requires the others.

### Any coding agent — one line (npx)

[vercel-labs/skills](https://github.com/vercel-labs/skills) detects your
installed agents (Claude Code, Codex, OpenCode, Cursor, and ~70 more) and
installs the whole skill folder for each:

```bash
npx skills add MJL-ren/blindspot-audit
```

Anonymous install telemetry can be disabled with `DISABLE_TELEMETRY=1`.

### Let your agent install it

Copy this prompt into Codex, Claude Code, OpenCode, or another coding agent.
The agent should read this repository and install the skill for the current
host or project.

```text
Install and configure Blindspot Audit for this agent environment:
https://github.com/MJL-ren/blindspot-audit

Read the repository README.md and AGENTS.md first, then install using the documented skill route that fits this host and scope: the installer script, the Claude desktop .skill, or a safe manual copy. If a permission or safety guard blocks writing the skill into the agent's config directory, don't silently stop - ask me to approve the permission, or offer the plugin marketplace route as a managed fallback.

Do not modify unrelated project files. After installation, tell me which route you used, the installed path or plugin name, how to update it later, and the exact prompt I can use to run a deep blindspot audit.
```

### Claude Code — plugin marketplace (one-liner, with updates)

Inside Claude Code, run:

```text
/plugin marketplace add MJL-ren/blindspot-audit
/plugin install blindspot-audit@blindspot-audit
```

No clone needed, and updates arrive via `/plugin marketplace update blindspot-audit`.
(`blindspot-audit@blindspot-audit` reads as `<plugin>@<marketplace>` —
plugin and marketplace happen to share the name here, so it is not a typo.)

### Codex — plugin marketplace

Inside Codex, add the Git marketplace and install the plugin:

```bash
codex plugin marketplace add MJL-ren/blindspot-audit --ref main
codex plugin add blindspot-audit@blindspot-audit
```

In the ChatGPT desktop app, open `Codex > Plugins > Installed` to inspect
or manage the installed plugin. If you use the CLI or want to force a
marketplace refresh, run:

```bash
codex plugin marketplace upgrade blindspot-audit
codex plugin add blindspot-audit@blindspot-audit
```

Start a new Codex task after installing or upgrading so the plugin skills are loaded.

### Script installs (clone first)

The script routes below need a local clone. All installers have PowerShell
(`.ps1`) and Bash (`.sh`) versions. On macOS/Linux use the `.sh` scripts
(run `chmod +x scripts/*.sh` once if needed); on Windows use `.ps1` from
PowerShell, or the `.sh` versions from Git Bash / WSL.

```bash
git clone https://github.com/MJL-ren/blindspot-audit.git
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

### Codex — manual skill install

Installs to the current Codex user skill directory, `~/.agents/skills`.
A custom destination can be passed as an argument. If the installer finds
a same-name copy under legacy `~/.codex/skills` or `$CODEX_HOME/skills`, it
warns but does not delete it automatically.

```powershell
.\scripts\install-codex.ps1
```

```bash
./scripts/install-codex.sh
```

### Claude desktop app / Cowork

Download the latest package directly —
[blindspot-audit.skill](https://github.com/MJL-ren/blindspot-audit/releases/latest/download/blindspot-audit.skill)
(or use `dist/blindspot-audit.skill` from a clone) — open it in the Claude
desktop app (attach it in chat) and click **Save skill**. No terminal
needed — this is the easiest route for non-developers.

If you installed it as a marketplace **plugin** inside the desktop app
instead, restarting the app is not enough to update it. Open the plugin
management screen and click **Update**, or run `/plugin marketplace update
blindspot-audit` from Claude Code or another compatible plugin CLI.

### Manual install

Copy the `skills/blindspot-audit` folder into any of:

```text
~/.claude/skills/blindspot-audit                    # Claude Code personal + OpenCode
<project>/.claude/skills/blindspot-audit            # Claude Code project + OpenCode
~/.agents/skills/blindspot-audit                    # Codex personal
<project>/.agents/skills/blindspot-audit            # Codex project
<project>/.opencode/skills/blindspot-audit          # OpenCode native (project)
~/.config/opencode/skills/blindspot-audit           # OpenCode native (global)
```

Current Codex documentation uses `.agents/skills`. Older
`~/.codex/skills` or `$CODEX_HOME/skills` copies may still appear in some
installations, but keeping the same skill in both places can expose
duplicate entries.

Then start a new agent session (or refresh) so the skill is picked up.

## Update

Use the same route you installed with:

- Claude Code plugin marketplace: run `/plugin marketplace update
  blindspot-audit`, then start a new Claude Code session.
- ChatGPT desktop app Codex plugin marketplace: open `Codex > Plugins >
  Installed` to inspect or manage the plugin. To force a CLI refresh, run
  `codex plugin marketplace upgrade blindspot-audit`, then `codex plugin
  add blindspot-audit@blindspot-audit`, and start a new Codex task.
- Claude desktop app marketplace plugin: click **Update** in the app's
  plugin management screen; restarting the app alone does not update it.
  The compatible CLI route is `/plugin marketplace update blindspot-audit`.
- Script installs: pull the latest repo, then re-run the same installer you
  used. The scripts replace the installed `blindspot-audit` folder instead
  of merging, so renamed or deleted files do not linger.
- Claude desktop app `.skill`: get the latest `dist/blindspot-audit.skill`
  and save it again in the app.
- Manual installs: replace the whole `skills/blindspot-audit` folder. Do
  not copy only `SKILL.md`; this skill also needs `references/`, `scripts/`,
  and `templates/`.

```bash
git pull
./scripts/install-claude-user.sh      # or the installer you used before
```

```powershell
git pull
.\scripts\install-claude-user.ps1     # or the installer you used before
```

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

## Contributing

Bug reports and field-run notes are welcome — please use the
[issue form](https://github.com/MJL-ren/blindspot-audit/issues/new/choose),
which asks for the host, skill version, and mode up front. New skills,
packs, or large feature PRs are generally not accepted: the audit core
stays small and field-tested. Open an issue first if you think something
is missing.

## Attribution

This project was inspired by the unknown-unknowns workflow described in
[A Field Guide to Fable: Finding Your Unknowns](https://x.com/trq212/status/2073100352921215386)
by Thariq (@trq212) of the Claude Code team. The implementation, wording,
templates, and scripts in this repository are original work.

The `ux-ui` focus pack's probe structure was informed by these open
projects, consulted as reference-only local clones under `external_repos/`
(untracked); all pack text is original:

- [mistyhx/frontend-design-audit](https://github.com/mistyhx/frontend-design-audit)
  (MIT) - 15-heuristic frontend audit skill with code-level violation
  patterns and a severity model.
- [raintree-technology/hig-doctor](https://github.com/raintree-technology/hig-doctor)
  (MIT for structure/tooling; HIG text © Apple - not copied) -
  detection-category taxonomy for appearance, access, and device checks.
- [Community-Access/accessibility-agents](https://github.com/Community-Access/accessibility-agents)
  (MIT) - accessibility audit agent patterns.

## Security

What the scripts do, what never touches the network, and how to report
concerns privately: see [SECURITY.md](./SECURITY.md).

## License

MIT License. See [LICENSE](./LICENSE).
