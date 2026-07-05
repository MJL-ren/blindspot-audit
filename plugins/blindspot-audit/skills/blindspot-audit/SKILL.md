---
name: blindspot-audit
description: "Project-level blind spot audit that finds what the owner is missing without knowing it: unknown unknowns, hidden risks, missing decisions, stale assumptions, and questions the user did not know to ask. Works on any kind of project - software, games, novels and creative writing, research, content, business plans. Use when the user asks for a blindspot pass, unknown unknowns audit, what they may be missing, a readiness/gap/health check beyond their own checklist, cross-project sanity checks, unfamiliar-domain planning, or post-implementation review. Also use for equivalent non-English requests about missed gaps, blind spots, or overlooked launch/project risks. Trigger even when the user never says audit."
---

# Blindspot Audit

## Purpose

Find the gap between the user's map of a project and the project's real
territory. Turn unknown unknowns into concrete known unknowns the user can
inspect, answer, test, or intentionally defer.

A project's context is self-selecting: the owner can only write down what
they already know, so every README, TODO, and plan encodes the map they
carry in their head - and an AI working from those files inherits the same
blind spots. This audit deliberately imports reference frames from OUTSIDE
the project to measure that gap.

This skill is not a generic quality checklist. It should identify what is
unusually important for this specific project, at this specific stage, with
evidence from the repo or provided artifacts. The audit succeeds when the
owner says "I didn't even know I should be thinking about that" at least
once - AND feels calmer afterward, because they now also know what they can
safely ignore.

## Core Model

Classify findings with the four-unknowns frame:

- Known knowns: what the prompt, docs, code, or plans already state.
- Known unknowns: open questions already visible in docs, TODOs, plans,
  comments, or user wording.
- Unknown knowns: things the user would recognize if shown, but has not
  verbalized or written down yet.
- Unknown unknowns: missing concepts, hidden constraints, or unasked
  questions the project shape implies.

The frame matters because the prescription differs: an unknown known needs a
checklist line, not a lecture; an unknown unknown needs a short explanation
and the cheapest first step. Good output does not claim certainty. It
exposes candidates and gives the cheapest next check.

## Ground Rules

These exist because the failure mode of this skill is not "missing a gap" -
it is becoming a generic checklist nag that gets ignored.

1. **The project's own tracking docs are a filter, not a source of
   findings.** Anything already in the README / TODO / roadmap / checklist /
   issue list is a KNOWN unknown. Never report it as a discovery. (Field
   data: this filter typically cuts the candidate list by more than half and
   is the main reason owners trust the report.)
2. **Cap top findings at 3-7**, ranked by impact x likelihood the owner is
   truly unaware. Overflow goes to a short "Lower-signal watchlist" or the
   ledger - never into the main list.
3. **Absence alone is not a finding.** "You have no X" only counts if you can
   state the concrete consequence for THIS project and the cheapest first
   step toward closing it.
4. **Always include the two trust sections:** "Checked and well covered" and
   "Skippable for now" (each skip with an explicit re-check trigger). They
   prevent anxiety and rescanning, and they are how the owner learns the
   report can be trusted.
5. **Hedge regulated domains.** For legal, tax, or regulatory findings, state
   what you found and its source, then say plainly that a professional must
   confirm it. You are a scout, not a lawyer or accountant.

## Modes

- `quick`: read docs and project inventory, return the top blind spots.
- `deep`: inspect representative code paths, tests, configs, and docs before
  ranking findings.
- `interview`: ask one question at a time when the answer would change
  architecture, workflow, scope, or risk.
- `post-implementation`: compare a completed change, notes, diffs, and tests
  to find remaining unknowns.
- `planning`: before implementation, surface decisions likely to change data
  models, interfaces, UX flows, operations, or verification.

Infer the mode from the user's wording. If the user asks to run it now, do
not ask mode questions unless the audit boundary is impossible to infer.

## Quick Start

1. Identify the project root and audit boundary.
2. Run the inventory helper when a filesystem project is available. The
   script lives in this skill's own folder - resolve it relative to this
   SKILL.md:

```bash
python <this-skill-folder>/scripts/project_inventory.py <project-root> --format md
```

Use `--include-generated` only when runtime outputs, generated reports,
logs, or cached artifacts are part of the audit question.

If the skill folder is not reachable from the shell (some hosts mount
plugins outside the sandbox - e.g. Cowork), copy the script into the
session workspace with the file tools and run that copy, or fall back to a
manual directory listing. See `references/host-surfaces.md`.

3. Read only the relevant references:
   - `references/archetypes.md`: choose project type and expected blind spots.
   - `references/lenses.md`: derive and apply audit lenses.
   - `references/host-surfaces.md`: adapt questions and outputs to Claude
     Code, Codex, OpenCode, CLI, or chat-only surfaces.
   - `references/ledger-lifecycle.md`: discover, create, route, or update a
     durable blindspot ledger.
   - `references/report-template.md`: format the result.
4. Discover or initialize the blindspot ledger:
   - If a prior ledger exists, read it before searching (diff-run rules
     apply - see Ledger And Diff Runs).
   - If no ledger exists and the host can write files, create
     `BLINDSPOT_LEDGER.md` in the best project-local documentation location
     unless the user requested read-only/chat-only output.
   - If no ledger exists and the host cannot write files, include the
     proposed path and first ledger entry in the report.
5. Inspect the strongest evidence files from the inventory: README/AGENTS,
   plans, package configs, app entry points, test configs, CI, env examples,
   schemas, prompts, agent/skill files, and runtime docs.
6. Run the fresh-eyes external scan (see Workflow step 5) when the host has
   web access.
7. Rank findings, interview the owner where possible, produce the report,
   and update the ledger.

## Host Surface Policy

The audit core should work the same across Claude Code, Codex, OpenCode,
CLI, and plain chat. Only the interaction style changes. See
`references/host-surfaces.md` for per-host details.

- Choice-capable hosts (Claude Code `AskUserQuestion`, OpenCode `question`):
  when a decision changes architecture, workflow, scope, or risk - and for
  the owner-awareness interview - ask one short 2-3 option question and
  record the selected option in the report or ledger.
- Codex or chat-only hosts: do not block on non-critical questions. Continue
  with the safest reversible assumption, mark it as an assumption, and
  include a `Decision packet` with the options the user should choose later.
- Hosts without web access: skip the fresh-eyes external scan, say so
  explicitly in the report, and flag time-sensitive domains (regulation,
  platform policy, pricing) as unverified rather than asserting them from
  training knowledge.
- File-writing hosts: for project audits, create or update a ledger by
  default unless the user requested read-only/chat-only output. Mention the
  path and routing edit in the report.
- Read-only or public-share hosts: return a portable report with
  commands/checks the user can run.

Ask immediately only when continuing would be risky, destructive, expensive,
or likely to produce misleading results.

## Ledger And Diff Runs

First run:

1. Choose the best durable location for `BLINDSPOT_LEDGER.md` using
   `references/ledger-lifecycle.md`.
2. Create the ledger from `templates/BLINDSPOT_LEDGER.md` when file writes
   are appropriate.
3. Add the ledger to the nearest routing surface, such as an operations
   README, docs index, or handoff pointer, when that routing file already
   exists.
4. Record the audit scope, mode, evidence boundaries, and first findings.

When a project already has a blindspot ledger:

1. Treat the ledger as an input, not as truth. Re-check high-impact or stale
   findings against current code/docs.
2. Classify output as `new`, `changed`, `confirmed`, `downgraded`,
   `resolved`, or `needs-decision`.
3. Do not repeat unchanged pending items unless they block the current goal.
   This is what makes repeated runs feel like progress instead of nagging.
4. If the ledger is new but not routed from an index, handoff, or operations
   README, flag that as a discoverability blind spot.
5. Preserve the ledger's local status language and IDs when updating it.
6. If findings were remediated during the session, set them to `resolved`
   (with date) before finishing - the ledger must not describe already
   fixed problems.
7. Keep the ledger compact: move `resolved`/`rejected` rows into a one-line
   archive section. IDs are compressed, never deleted or renumbered. See
   `references/ledger-lifecycle.md`.

Good ledgers make future audits cheaper. Bad ledgers become another hidden
document, so always check discoverability.

## Search Hygiene

Use bounded searches. Blindspot audits often touch broad repos, and noisy
generated files can create false confidence or waste context.

Default excludes for `rg` and similar tools unless the audit explicitly
targets those areas:

```text
!.git/**
!node_modules/**
!.venv/**
!dist/**
!build/**
!runtime/**
!external_repos/**
!vendor/**
!docs/archive/**
!docs/research/**
!docs/sources/**
!data/external/raw/**
```

Prefer targeted paths and `--glob` excludes over repo-wide scans. If a broad
scan returns huge generated files, stop and rerun with a tighter boundary
before using the result.

## Workflow

### 1. Define The Map

State the user's apparent goal, project type, maturity, and your audit
boundary in 2-4 lines. Mark assumptions explicitly. Include an owner
profile:

- Solo or team? What is the owner clearly expert in, and - more useful -
  NOT expert in? Blind spots cluster in the owner's non-expert areas, so
  weight those lenses up.
- Hobby or commercial? Private or public? Commercial or public intent
  activates legal, tax, and market lenses that would be pure noise for a
  private hobby project. If intent is not readable from the files, ask
  before scanning (one short question) - guessing wrong on intent wastes
  the whole audit.

### 2. Gather Evidence

Use the inventory helper plus targeted reads. Read the project's
self-awareness surfaces first (README, TODO, roadmap, checklists, design
docs, synopsis/outline) - they are both your best profile source and your
noise filter (Ground Rule 1). Prefer evidence over broad speculation. Tag
evidence as:

- observed: directly present in files or outputs.
- absent: expected artifact not found in the inspected scope.
- inferred: likely from structure, naming, or conventions.
- question: requires user or domain-owner confirmation.

### 3. Classify The Territory

Choose one or more archetypes from `references/archetypes.md`. Do not force
the project into one category if it is hybrid.

### 4. Run Lenses

Apply only lenses that fit the project stage. A prototype does not need
enterprise compliance, but it may still need data-loss boundaries, secret
handling, or recoverability.

### 5. Fresh-Eyes External Scan

When the host has web access, do time-boxed research on two questions:

1. What do healthy projects of this category treat as standard equipment
   **right now**?
2. What changed in the last 6-12 months - regulation, platform policy,
   market or genre conventions, tooling - that this project's documents
   could not possibly contain?

Question 2 is disproportionately valuable: time-dependent changes are
structurally invisible to both the repo and the owner's memory. (Field data:
in early runs the single highest-impact findings - an AI-content labeling
law taking effect the following month, a payment provider acquisition that
invalidated a documented plan - all came from this step.) Cite sources for
anything found here. Without web access, skip and disclose (see Host Surface
Policy).

### 6. Convert Blind Spots Into Checks

For every finding, include:

- what may be missing.
- why it matters for this project.
- evidence.
- cheapest next check.
- likely owner or decision surface.
- priority: now, next, later, or watch.
- confidence: high, medium, low.

Drop candidates that appear in the project's own tracking docs (Ground Rule
1), keep the top 3-7, and move the rest to the watchlist or ledger.

### 7. Interview The Owner

Present the findings, then ask which ones the owner already knew about (a
single multi-select question works well on choice-capable hosts). Classify
each finding:

| Awareness | Meaning | Prescription |
|---|---|---|
| `unknown_unknown` | Owner did not know | Explain why it matters here + cheapest first step |
| `unknown_known` | Owner knew, but it is written nowhere | The fix is documentation, not implementation - get it into their tracking docs so agents and future sessions can see it |
| `deliberate_skip` | Owner considered it and chose not to | Move to the skip list WITH the reason and a re-check trigger |

(Field data: in early runs roughly half of top findings turned out to be
`unknown_known` - real gaps in the repo, but not in the owner's head. The
distinction changes the follow-up entirely.)

On hosts that cannot ask, mark every awareness value `unconfirmed`, embed
the interview questions in the report, and put open decisions in a
`Decision packet`.

### 8. Keep The Output Useful

Lead with the highest-signal blind spots. Always include the two trust
sections (Ground Rule 4). Write the report and ledger prose in the language
the owner is using in conversation; keep IDs, status, and awareness values
in English so re-runs stay diffable across sessions and languages. Format
per `references/report-template.md`.

## Guardrails

- Do not present generic best practices as findings unless the project
  evidence makes them relevant.
- Do not re-report items that already exist in the ledger or the project's
  own tracking docs.
- Do not require heavy process for personal experiments or early prototypes.
- Do not make code changes unless the user explicitly asks for remediation.
- Do not claim something is broken solely because a file is absent; say what
  the absence suggests and how to confirm.
- Treat absent CI, tests, release docs, or deployment files as a blind spot
  only when the project claims repeatable delivery, shared handoff, or
  production-like reliability. Personal notes and early prototypes may not
  need them.
- Do not bury the user in every possible risk. Rank by project fit, blast
  radius, reversibility, and likelihood.
- When the user is non-expert in the domain, include short teaching notes
  for unfamiliar blind spots.
- When a finding depends on current external platform behavior, verify with
  official docs or current research before treating it as fact; without web
  access, present it as unverified.
- Remember that the inventory helper is only a map. Use it to choose
  evidence files, not as proof by itself. If sampled files, generated
  artifacts, archives, or external repos matter, say so and rerun with a
  tighter boundary or `--include-generated`.
- If two evidence sources disagree, investigate the contradiction before
  reporting. The contradiction may be the real blind spot, or it may be a
  bug in the audit tooling.
- If creating a durable report or ledger, also check whether future agents
  can discover it from the project's normal routing docs.

## During Implementation

When the audit is attached to an implementation task, ask the implementing
agent to keep an `implementation-notes.md` or `implementation-notes.html`
file with:

- assumptions made.
- deviations from the plan.
- edge cases encountered.
- tradeoffs chosen.
- open questions.

Use those notes during post-implementation audits.
