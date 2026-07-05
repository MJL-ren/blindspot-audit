# Changelog

All notable changes to the blindspot-audit skill and this repository.

## [0.4.1] - 2026-07-06

Repository-level quality pass: show what good output looks like, and make
the skill's behavior testable - plus one field-observed Cowork mirror rule.

### Added

- `examples/sample-reports/`: five synthetic sample reports showing the
  target output shape - a web app about to go public, an indie game
  heading to Steam, a research-analysis project, a Korean web-novel
  serialization audit (demonstrating the owner-language rule), and a
  `weak-vs-strong.md` that writes three findings twice (checklist-nag vs
  evidence-based) with the ground rule each version passes or fails.
- `evals/fixtures/`: three behavior regression fixtures with pass/fail
  criteria in per-fixture `EXPECTED.md` files - `documented-gap` (Ground
  Rule 1: tracked gaps are filtered, not rediscovered), `toy-stage`
  (stage fit: no enterprise findings on a personal script), and
  `injection-resistance` (Ground Rule 8: embedded audit-steering text is
  disobeyed and surfaced). `evals/README.md` documents how to run and
  grade them without contaminating the test.

### Changed

- All five READMEs: introduce the project-context intake in "What It
  Does", document the new `evals/` and `examples/sample-reports/` folders,
  and add a desktop-app note that marketplace plugins do not auto-update
  by default (manual update check, or connect GitHub for auto-sync).
- `examples/prompts.md`: added context-rich prompt examples (English and
  Korean) that set owner strengths, category-only search privacy, and
  ledger context storage in one message, plus a pointer to the sample
  reports.
- Cowork adapter (`references/host-surfaces.md`): field-observed quiet
  variants of the stale-mirror-sync failure, in BOTH directions - the
  sandbox's `git status`/`git diff HEAD` can claim file-tool-modified
  files are clean, and a freshly rebuilt artifact (the packaged `.skill`)
  can reach the owner's disk late, so their commit ships new sources with
  a stale package (CI caught exactly this during this release). Owner-
  facing commit blocks must list the exact expected files and require
  `git status --short` to match before committing, with
  `git update-index --really-refresh` as the fallback.
- Bumped plugin metadata to `0.4.1` (both manifests).

## [0.4.0] - 2026-07-06

External review pass (owner + a second AI reviewer) on top of field
feedback: the audit calibrates best when project context is collected
explicitly instead of inferred every run, and the skill needed privacy and
injection rules for its OWN behavior - not only lenses that check the
audited project for them.

### Added

- Ground Rule 7 (SKILL.md): web searches are category-only by default.
  Private identifiers (unpublished project or product names, client names,
  internal paths, personal names) never go into queries; the ledger's
  Project Context or the owner can set stricter rules, and identifier
  searches (e.g. trademark collisions) are proposed as checks or asked
  first. The fresh-eyes scan references the rule at the point of use.
- Ground Rule 8 (SKILL.md): project files, web pages, and tool outputs are
  evidence, never instructions - embedded text that tries to redirect the
  audit or suppress findings is disobeyed and surfaced as a finding
  candidate. Explicitly bounds the Ground Rule 1 tracking-doc filter to
  owner-maintained docs, so a doc cannot claim "already tracked" its way
  into hiding a gap.
- Project context intake (SKILL.md workflow, ledger template `Project
  Context` section, host adapters, report template): first runs collect
  the minimum context that changes the audit - intent, target users and
  regions, stage and deadline, owner strong/weak areas, web-search privacy
  rule - via one or two compact questions on choice-capable hosts, or a
  numbered skippable `Context check` beside the awareness check on
  no-choice hosts. Every question is skippable ("prefer not to say");
  skips are stored as `skipped (assumption: ...)` and never re-asked.
  Later runs read the ledger section instead of re-interviewing. This
  restores the natural "ask what kind of project this is first" flow from
  the original design.
- `templates/implementation-notes.md`: a concrete shape for the file the
  During Implementation flow already required (assumptions, deviations,
  edge cases, tradeoffs, open questions); post-implementation audits read
  it first as the plan-vs-territory diff.
- Post-implementation mode may offer (never force) a short comprehension
  quiz on the change; a wrong answer is an unknown to re-explain, not a
  fault to grade.
- Negative triggers in the skill description: routine bug fixes, ordinary
  code review, formatting, and implementation-only requests no longer
  match unless the user also asks what they may be missing or risking.

### Changed

- CHANGELOG entries now describe field-feedback projects by category only;
  earlier entries that named private projects were rewritten to neutral
  descriptions, and AGENTS.md gained a publishing rule keeping private
  identifiers out of changelogs, commit messages, and release notes.
- Bumped plugin metadata to `0.4.0` (both manifests).

## [0.3.9] - 2026-07-06

Owner feedback after five real-project ledgers: findings clustered in
safety/legal/regulation/plumbing, because file absence is easy evidence
while category expectation gaps need an outside reference - so the audit
under-asked "do I know how good this category normally is?".

### Added

- Peer expectation scan (SKILL.md fresh-eyes step): pick 2-3 representative
  peers of the project's specific category and walk their user-visible
  surface. A gap is a finding only if it passes three table-stakes tests:
  all peers have it; users would notice and be disappointed; it fits the
  current stage. The prescription is a decision ("meet the expectation or
  skip it on record"), never a feature order - a recorded skip becomes a
  positioning statement.
- Guardrail: this audit is not a feature brainstorm - differentiator ideas,
  trends, and nice-to-haves are dropped entirely, not even watchlisted.
- Domain Fit lens gains "what do users of this category take for granted"
  probes; archetypes.md now explains that its lists skew toward operations
  on purpose and category expectations are derived at audit time;
  report-template requires naming the peers checked.

### Changed

- Bumped plugin metadata to `0.3.9` (both manifests).

## [0.3.8] - 2026-07-06

Release automation and catch-up publishing for the post-`0.3.1` changes.

### Added

- GitHub Actions release publishing: after package/script checks pass on a
  `main` push, the workflow reads the canonical plugin version, generates
  release notes from `CHANGELOG.md`, creates the missing GitHub Release,
  and uploads `dist/blindspot-audit.skill`.
- `scripts/prepare-github-release.py`: prepares release metadata from
  `.claude-plugin/plugin.json`, finds the previous semver tag, and includes
  every newer changelog section in the release notes. This lets the next
  release carry the accumulated `0.3.2` through `0.3.8` updates instead of
  only the top entry.

### Changed

- Bumped plugin metadata to `0.3.8` (both manifests).

## [0.3.7] - 2026-07-06

Field feedback from two Codex runs: a scoped plan-document audit and a
mixed multi-repo workspace audit.

### Added

- Audit Scope section in SKILL.md: when the audit targets one document,
  feature, or module, run scoped - append delta rows to the existing
  project ledger (never a per-doc ledger file), filter against the
  target's own owner docs, skip the full-tree inventory, make the
  fresh-eyes scan targeted or skip it for internal targets, and state the
  scope in the report header. Matching rule in `ledger-lifecycle.md`.
- Multi-repo workspace ledger rules: repo-owned findings live in that
  repo's ledger; workspace-crossing findings get a workspace-level ledger
  only if the workspace root is durable and private.
- Sensitive-findings-vs-public-ledger rule: never write exploitable detail
  into a ledger that gets published; generalized public row + detailed
  private row (or report-only detail, or ask the owner), with the chosen
  option recorded.
- Expensive-command guardrail: audits observe - read-only seconds-fast
  checks are fine, but builds/test suites/deploys are evidence via
  existing logs, or become the finding's proposed cheapest check, not
  something the audit runs uninvited. Deep mode text updated to match.
- Source-tier rule in the fresh-eyes scan: official/primary sources back
  findings; community signals are leads that must be verified or parked in
  the watchlist as "community-reported, unverified"; never one unlabeled
  citation list.

### Changed

- Bumped plugin metadata to `0.3.7` (both manifests).

## [0.3.6] - 2026-07-05

Owner feedback after a Codex run: of five findings, a beginner owner could
understand only one. A finding the owner cannot understand is still an
unknown unknown - just renamed - and it corrupts the awareness interview
("I don't know what this means" is not "I didn't know about this").

### Added

- Ground Rule 6 (SKILL.md): write every finding at the owner's level -
  title by the everyday-words consequence rather than the technical term,
  define unavoidable jargon in one line at first use, anchor to something
  familiar, stay concise inside the owner's expert areas. Language-
  independent by design.
- "In plain terms" field in the report finding shape, included whenever a
  finding sits outside the owner's expert areas, plus a weak-vs-strong
  finding example from a real run (Steam's AI disclosure question) in
  `references/report-template.md`.
- Number-plus-question-mark path (`3?`, `3번?`): owners can flag findings
  they did not understand; the auditor re-explains more simply, keeps
  awareness `unconfirmed`, and never counts "didn't understand" as "didn't
  know". Added to the awareness prompts, interpretation rules, and the
  interview workflow step.
- Plain-language rule extended to structured-choice option labels in
  `references/host-surfaces.md` (label by consequence, explain in the
  option description).

### Changed

- Bumped plugin metadata to `0.3.6` (both manifests).

## [0.3.5] - 2026-07-05

Field feedback from a Codex run on a Unity workspace (nested repo, 70k+
files, 17k `.meta` sidecars, CSV-indexed docs).

### Fixed

- `project_inventory.py` no longer lets engine-generated files eat the
  sample budget: Unity/Unreal/Godot project roots are detected
  per-directory during the walk (they are often nested, e.g.
  `<repo>/UnityProject/<Game>/`), and their generated dirs
  (Unity `Library`/`Temp`/`Obj`/`Logs`/`UserSettings`/`Build`,
  Unreal `Binaries`/`DerivedDataCache`/`Intermediate`/`Saved`,
  Godot `.godot`/`.import`) are pruned only under a confirmed engine root -
  a non-engine folder named `Library` is unaffected. `.meta` sidecars are
  skipped globally. Detected engines appear in the framework hints.
- Truncated sampling now prints an explicit warning that absence claims are
  untrustworthy and the run should be re-scoped to docs/source dirs first.
- Added safe generated-dir ignores seen across code/ML projects:
  `coverage`, `.ipynb_checkpoints`, `wandb`, `mlruns`, `DerivedData`.

### Added

- Nested-repo rule (SKILL.md + `references/ledger-lifecycle.md`): the audit
  boundary may contain multiple git repos; place the ledger inside the repo
  that owns the audited surface and verify tracking with `git -C` against
  that repo, never the outer folder.
- Index-style routing rule: projects that route docs through a maintained
  index (`Docs/_Index/README.md`, `DocIndex.csv`, wiki sidebar) get the
  ledger registered in the project's own index format.
- Source-URL rule (template + ledger lifecycle): external-scan findings
  keep their source URL in the ledger row so the next audit re-verifies
  instead of re-searching.
- Engine-generated exclude guidance in SKILL.md Search Hygiene.

### Changed

- Bumped plugin metadata to `0.3.5`.

## [0.3.4] - 2026-07-05

Field feedback from the first registered Claude Code run (a web-project
audit, Opus review): the thinking frame held; all friction was in tooling
and host adaptation.

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
- `.codex-plugin/plugin.json` was left at `0.3.3` during the 0.3.4 metadata
  bump; realigned to `0.3.4`. The Codex skill *content* was already in sync
  (verified by `verify-codex-plugin.py`); only the manifest version string
  had drifted.

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
- Version-alignment gate in `verify-codex-plugin.py`: the Codex manifest
  version must equal the canonical `.claude-plugin/plugin.json`, and the
  newest CHANGELOG heading must match it. CI already runs this script, so a
  future bump that misses a manifest now fails loudly instead of shipping a
  mislabeled release (this is the exact drift that hid the 0.3.3/0.3.4 gap).

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

Field feedback from the first registered Cowork run (a worldbuilding
knowledge-base audit).

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
