# Audit Workflow

Use this reference for every normal, quick, deep, planning,
post-implementation, interview, scoped, or focus audit. Do not use it for
`mode: ledger-triage`; that mode reads `ledger-triage.md` instead.

## Contents

- Modes and scope
- Inventory and search hygiene
- Define the map
- Gather and classify evidence
- Apply lenses and focus packs
- Fresh-eyes external scan
- Convert candidates into findings
- Interview and report
- Execution guardrails

## Modes And Scope

- `quick`: read the ledger, core owner docs, and inventory; return only the
  highest-signal findings. Propose deeper packs/checks instead of silently
  expanding the run.
- `deep`: inspect representative code/content paths, tests, configs, operations,
  and current outside expectations. Prefer existing verification artifacts over
  rerunning heavy commands.
- `interview`: ask one question at a time when an answer changes architecture,
  workflow, scope, or risk. Do not turn it into a checklist interrogation.
- `planning`: surface decisions that could change data models, interfaces, UX,
  operations, cost, scope, or verification before implementation.
- `post-implementation`: read implementation notes when present, then compare
  plan, diff, tests, and runtime evidence. A short optional comprehension check
  may reveal an explanation gap; it is not a grade.
- `focus: <domain>`: preserve the base mode but narrow the domain. Read the pack
  registry and load exactly one registered pack.

Default scope is the whole project. When the owner names one document, feature,
module, or subfolder, use a scoped audit:

- Read that target and its direct references instead of forcing a full-tree
  inventory.
- Read the project ledger and append scoped delta rows to it. Do not create a
  per-document ledger. If no project ledger exists, propose rows inline.
- Use target-owned tracking docs plus the project ledger as the known-work
  filter.
- Run external research only for questions the target raises.
- Keep the same 3-7 cap, ranked by consequences for the target's next action.

A focus run covers that domain across the whole project. A domain plus a named
file/module is partial pack coverage. Record the uninspected applicable surface
and do not clear project-wide pack debt.

State the actual scope in the report and Audit Log. A later whole-project run
must be able to tell what this run did not inspect.

### Same-Focus Resolution

An explicit registered Focus ID always wins. If the owner says "same focus",
"previous focus", or an equivalent phrase without naming it:

1. Read the current ledger's Audit Log and linked Audit Evidence.
2. Reuse the most recent registered Focus ID only when exactly one prior focus
   is the clear referent in the current project/context.
3. If multiple recent registered focuses are plausible, ask one short
   disambiguation question through the current host adapter.
4. If no durable focus record exists, do not infer from another project or host
   memory; ask or state that no prior focus can be resolved.
5. Record the reused canonical scope as `focus/<id>` in the new run.

## Inventory And Search Hygiene

Use bounded searches. Generated files, archives, caches, copied repositories,
and runtime artifacts can consume the audit budget and create false framework or
secret signals.

Default excludes for broad `rg`/glob/file walks unless the scope explicitly
targets them:

```text
!.git/**
!node_modules/**
!.venv/**
!dist/**
!build/**
!runtime/**
!external-repos/**
!external_repos/**
!vendor/**
!docs/archive/**
!docs/research/**
!docs/sources/**
!data/external/raw/**
```

Also exclude engine-generated trees unless they are the subject: Unity
`Library`, `Temp`, `Obj`, `Logs`, `UserSettings`, `*.meta`; Unreal `Binaries`,
`DerivedDataCache`, `Intermediate`, `Saved`; Godot `.godot`, `.import`; Xcode
`DerivedData`.

The bundled inventory and secret-location helpers use tracked files plus
unignored untracked files in Git repositories and report their enumeration
mode. They do not silently claim coverage of ignored files. Opt an ignored path
in only with a narrow explicit include.

If an inventory is truncated, do not use absence claims from it. Rerun against
owner docs and source/config directories or raise the bound deliberately. Use
the inventory as a map for targeted reads, never as evidence by itself.

## 1. Define The Map

State goal, project type, maturity, and boundary in 2-4 lines. Mark assumptions.
Weight lenses toward the owner's weak or unfamiliar areas, where blind spots
cluster.

### Project Context Intake

Collect context once and store it only in the ledger's `Project Context`:

- public/private/commercial intent.
- target users and regions.
- stage and deadline.
- owner strong and weak areas.
- web-search privacy rule.
- standing decisions or must-not-change boundaries.

Use this ladder:

1. If directly readable from files, record `inferred (evidence: <path>)`
   without asking. Let the owner correct it later.
2. If plausible but uncertain, continue under a labeled assumption and fold one
   confirmation into the interview.
3. If absent and materially important, ask compactly on a callable choice host.
   On a no-choice host, continue with assumptions and add the optional Context
   check defined in `host-surfaces.md`.

Every question is skippable. Record `skipped (assumption: ...)` and do not ask
again unless reopened. Generalize personal attributes into relevant strong/weak
areas. Apply the ledger visibility rule to inferred context.

Do not copy the owner profile into host-local memory, `CLAUDE.md`, `AGENTS.md`,
or another agent-specific surface. If a host convention needs a note, write a
pointer to the ledger, not a second copy that can drift.

## 2. Gather Evidence

Read self-awareness surfaces first: README, TODO, roadmap, checklist, decision,
design, synopsis/outline, issue, and existing ledger files. They are evidence of
the owner's map and the primary known-work filter.

Sample the strongest project-specific evidence next:

- package/build/deploy configuration and lockfiles.
- application/content entry points and major data flows.
- tests, CI, release, restore, and operational docs.
- schemas, migrations, storage, exports, and backups.
- prompts, agent/skill files, permissions, and runtime boundaries.
- user-facing screens, flows, content, or public promises when applicable.

Tag claims internally:

- `observed`: directly present in inspected files/output.
- `absent`: expected artifact not found in the inspected boundary.
- `inferred`: likely from structure or convention.
- `question`: requires owner, runtime, provider, or specialist confirmation.

Read existing results before running commands. Short read-only checks are fine;
follow the execution guardrails below for everything else.

## 3. Classify The Project

Choose one or more project archetypes from `archetypes.md`. Hybrid projects may
need several. Apply only lenses that fit the actual stage: a prototype does not
need enterprise ceremony, but public exposure, credentials, private data, paid
actions, or unrecoverable work can matter early.

## 4. Apply Lenses And Packs

Use `lenses.md` for breadth. A normal whole-project audit does not load domain
packs automatically; pack detail can crowd out larger cross-domain findings.

Load one registered pack when:

1. the owner explicitly requests `focus: <registered-id>`, or
2. the mode is `deep`, the owner is weak in a matching substantial domain, and
   one owner-inverse pack is the highest-value inline descent.

If the requested domain has no pack, use ordinary lenses, disclose
`no registered pack loaded`, and do not mark pack coverage complete.

When a substantial weak-owner domain was only skimmed, emit one meta-finding
rather than pretending the skim was depth. Name the surface and prescribe the
registered focus run or a bounded specialist check. Record applicable un-run
packs as coverage debt through `ledger-lifecycle.md`.

## 5. Fresh-Eyes External Scan

When web access exists and current outside facts can change the result,
time-box two questions:

1. What do healthy projects of this category treat as standard equipment now?
2. What changed in roughly the last 6-12 months in platform rules, law, market,
   conventions, dependencies, or tooling?

Search category terms only. Keep source tiers separate:

- official/primary sources may support a claim directly.
- community reports and aggregators are leads; verify against a primary source
  or leave them as explicitly unverified watch material.

Walk existing findings and documented frictions for newly cheap solutions. A
new capability that materially reduces an already tracked problem is a stale
assumption candidate, not free-form feature brainstorming.

### Peer Expectation Scan

For a full audit with web access, inspect 2-3 named representative peers when
user/category expectations matter. A gap enters the main findings only when:

1. all selected peers provide it.
2. users would notice and be disappointed by its absence.
3. it fits the current project stage.

The result is a decision: meet the expectation or deliberately skip it with a
reason. Differentiators, trends, and nice-to-haves are not blindspot findings.
On diff runs, repeat the peer scan only when never run or when category/stage
changed.

Without web access, skip the scan, disclose the limit, and leave time-sensitive
claims unverified.

## 6. Convert Candidates Into Findings

For each candidate, ask:

- Is the consequence plausible for this project?
- Is it absent from owner tracking docs and the existing ledger?
- Is it material at this stage?
- Can it be explained plainly and closed by a cheap next check?
- Does it fit within the 3-7 cap better than competing candidates?

Each retained finding includes consequence, evidence, uncertainty, cheapest
check, owner/decision surface, priority, confidence, pre-interview awareness
`unconfirmed`, and pre-decision disposition `pending`.

Priority, confidence, awareness, and disposition are canonical English enums in
the report. Existing ledgers preserve their own schema through
`ledger-lifecycle.md`; report columns do not authorize migration.

## 7. Interview The Owner

Present every finding before the question. The owner must understand each item
without opening another file. Label choices by everyday consequence, not an ID
or internal shorthand.

Use the host adapter:

- callable-now structured UI: ask one compact classification question and omit
  the numbered fallback.
- no callable UI: finish the report, keep awareness `unconfirmed`, and put the
  exact numbered awareness check from `report-template.md` last.

Interpret awareness and disposition independently. Re-explain unclear items
before classification. Apply global awareness statements to all referenced
findings and numbered dispositions only to their named subset. Do not keyword
parse owner language; encode its meaning into the structured response schema.

After the owner answers, update only the delta and future re-report behavior.
Do not rerun the audit unless the reply changes scope or evidence.

## 8. Report And Close Out

Lead with the highest-signal findings and include:

- checked and well covered.
- skippable for now with triggers.
- limitations and uninspected surfaces.
- ledger delta and durability status.
- awareness question or results.

Write in the owner's conversation language. Keep the report self-contained when
the host is read-only or no durable ledger received full records.

For every created ledger, routing edit, or durable batch handoff, verify its
owning repository and classify durability before finishing:

- `tracked`: `git ls-files` or the equivalent confirms durable tracking.
- `owner-approved-local-only`: an explicit standing owner decision/ignore rule
  intentionally keeps it local.
- `untracked-pending`: it exists but is neither tracked nor approved local-only.
- `not-versioned`: no version-control boundary is available; report the limit.

Never stage automatically. Put `untracked-pending` in the final report or
Decision Packet with the exact path and the choice to track, ignore deliberately,
or move it. A first run is not complete while durability is silently unknown.

## Execution Guardrails

- Do not modify project code merely because an audit found a gap. Remediation
  requires an explicit fix request.
- Do not run builds, full suites, deploys, scanners, project-code probes,
  credentialed/provider actions, destructive commands, or paid work uninvited.
  Propose the decisive check or ask when authorization is required.
- Do not claim a problem solely from file absence. State what the absence
  suggests and how to verify it.
- Do not demand CI, release process, compliance, or enterprise controls from a
  project that does not claim the corresponding reliability or exposure.
- Do not echo secrets or private records. Do not test a discovered credential.
- Verify current external claims with authoritative sources; otherwise label
  them unverified.
- Investigate contradictions before reporting. A disagreement may expose the
  real blind spot or a defect in the audit helper.
- Keep durable artifacts discoverable through existing routing surfaces, but do
  not invent a documentation system solely for this audit.
