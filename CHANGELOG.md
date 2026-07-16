# Changelog

All notable changes to the blindspot-audit skill and this repository.

## [0.7.2] - 2026-07-16

### Added

- Added `references/owner-response-guard.md` as a delayed-load contract for
  post-interview response mapping, preview, localized application maps,
  security-batch scaffolding, final validation, and cleanup.
- Added explicit progressive-loading guidance for host adapters, including
  conditional Cowork `send_user_message` use and byte-verified direct execution
  from a recognized project-level skill mirror, with fail-closed copy-both
  fallback for stale or same-sized-but-different mirrors.

### Changed

- Slimmed the entrypoint guard and frontmatter description while preserving
  normal, focus, ledger-triage, consent, and natural-language trigger behavior.
- Made ledger-triage question batching deterministic when owner-detail rows
  exceed the active question budget.
- Clarified that cleanup intentionally retains `.blindspot-tmp/.gitignore` as a
  safety marker when no run directories remain.

## [0.7.1] - 2026-07-14

### Added

- Added a transparent Blindspot Audit icon with distinct light- and dark-theme
  contrast, and registered it for both standalone skill installs and Codex
  marketplace plugin surfaces so every supported Codex install path shows the
  same identity.

### Changed

- Extended the Codex plugin verifier to reject missing, unsafe, non-square, or
  non-alpha PNG interface assets before release.

## [0.7.0] - 2026-07-12

### Added

- Added `references/packs/index.md` as the canonical focus-pack registry and
  shared extension contract. It defines runtime routing, applicability,
  required pack sections, the finding gate, coverage-note behavior, and the
  registration steps future domain packs must satisfy.
- Added `focus: security`, a defensive read-mostly pack for trust boundaries,
  identity, authorization, untrusted input, secret lifecycle, sensitive data,
  software supply chains, secure failure, detection, and incident readiness.
  It redacts credential material, separates current-tree/history/provider/
  downstream closure, and prohibits active testing without authorization.
- Added the `security-boundary-gap` behavior fixture to grade root-cause
  consolidation, owner-doc filtering, secret-closure evidence, stage fit,
  positive controls, and the no-exploitation boundary.
- Added contract tests that keep registered Focus IDs, pack filenames, source
  files, canonical scope labels, required section order, and the early
  `SKILL.md` mode router aligned.
- Added deterministic security verification tiers (`static-only`,
  owner-approved `ephemeral-local`, and separately authorized dynamic checks),
  plus an internal boundary-coverage matrix and explicit completion states.
- Added a value-suppressing `secret_presence_scan.py` helper for bounded
  current-tree and separately approved Git-history location checks. It emits
  only sanitized metadata, distinguishes manual heuristics from dedicated
  scanners, and leaves provider state for owner confirmation.
- Added a lightweight durable security-batch template for explicit
  multi-finding deferrals, with restart order, prerequisite decisions,
  verification matrix, completion criteria, and closeout lifecycle.
- Added `audit_followup_guard.py` with existing-ledger schema snapshots,
  schema-only validation before interviews, language-independent structured
  owner-response previews, final ID/batch/backlink validation, and safe temp
  cleanup. It never edits the ledger or keyword-parses owner language.
- Added grouped `blindspot-owner-response.v2` decisions with deterministic v1
  expansion, conflict detection, explicit localized-ledger application maps,
  and per-finding applied-state output while retaining v1 compatibility.
- Added `scaffold-security-batch` to generate the exact durable batch headers,
  included IDs, verification placeholders, repo-relative restart pointers, and
  ledger-backlink suggestion without editing the ledger.
- Added shared `safe_output.py` console/log escaping for all four packaged
  helpers. Repository-controlled C0/C1, terminal escape, line-separator, and
  Unicode direction/format controls are rendered visibly without damaging
  normal owner-language text.
- Added a shared PowerShell install-removal guard. All three PowerShell
  installers now prove direct-child containment and refuse root or nested
  junction/symlink/reparse-point deletion before recursively replacing an
  install.
- Added GitHub Actions Dependabot updates and pinned all workflow actions to
  verified full commit SHAs with read-only package-job permissions; only the
  release job retains `contents: write`.
- Added `prepare-awareness` as a short, guarded path for one or more findings
  sharing an explicit awareness-only owner reply. Repeatable finding arguments
  prepare a temporary v1 response and the same application preview without
  editing the ledger, while custom/localized schemas still require explicit
  column and value adapters.
- Added a maintainer-only testing-copy sync script that reproduces the canonical
  skill content at an explicit `blindspot-audit-testing` target while preserving
  its distinct trigger and Codex display identity.

### Changed

- Focus routing now resolves only registered pack IDs, loads one pack per
  focused pass, keeps multi-focus requests as separate passes, and explicitly
  disambiguates overlapping aliases instead of guessing. Generic unregistered
  domains and path-limited partial focuses are recorded without clearing
  project-wide pack coverage by accident.
- Coverage debt now applies only when a registered pack's own applicability
  rules match a substantial project surface. It is no longer possible to read
  the registry as a requirement that every project run every pack.
- The existing `ux-ui` pack now follows the common contract with explicit
  activation, surface mapping, stage-fit boundaries, current-source anchors,
  and coverage recording while preserving its established probe behavior.
- All README translations and bilingual prompt examples now document the
  defensive `focus: security` workflow and credit the MIT-licensed reference
  projects that informed its structure without copying their prose.
- Owner awareness and implementation disposition are now independent axes, so
  "I did not know; handle it in the next batch" records
  `unknown_unknown + deferred`, never an intentional skip. Existing localized
  ledger schemas remain authoritative and are not auto-migrated.
- Host adapters now distinguish advertised, callable-now, mode-gated, and
  unavailable structured-choice tools. Only a tool callable in the current
  mode is used; the other cases take the documented no-choice fallback.
- Security findings merge only when their enforcement point, remediation
  owner/surface, and cheapest closing check all match. Long security reports
  gain a three-line owner summary, and external calibration now starts with
  official stack/provider advisories before community leads.
- Security runs now record project interaction and external evidence on
  separate axes, build conditional locked-dependency, product-lineage, and
  promise-to-enforcement working tables, and use a compact owner-facing chat
  layer only when full self-contained records were written to the ledger.
- Provider checks now pass through separate presence, authentication,
  current-mode callability, granted-scope, and per-run consent gates. Mixed
  owner replies apply global awareness and numbered dispositions independently;
  `owner_followup` remains a next-action route rather than a disposition.
- Security batch handoffs now declare visibility/detail policy and require one
  check, one tier, and one evidence channel per verification row. Audit Log rows
  use compact `BA-` run IDs with detailed limits in an in-ledger Audit Evidence
  section.
- All existing-ledger writes now require owning-repo dirty-worktree baselines,
  contextual target patches, preservation checks for prior hunks/unrelated
  files, whitespace validation, and stable-ID/row-count verification.
- Existing-ledger follow-up now uses separate pre-delta and owner-response
  snapshots, accepts either the printed snapshot marker file or its containing
  directory, and reports a missing marker directly instead of a generic JSON
  parse failure. Schema-only snapshots use `cleanup --discard`, while
  owner-response snapshots require `cleanup --confirm-applied`; swapped modes
  are rejected.
- Final application checks preserve established annotated status forms such as
  `deferred(reason)` through bounded match modes without accepting prefix
  lookalikes. Known-work filtering no longer invents a non-canonical awareness
  enum for already documented items.
- Cowork and other sandbox adapters now copy `safe_output.py` beside every
  packaged executable helper, use byte-stable mounted output paths, recheck
  shell-observed truncation with file tools before creating findings, and honor
  both per-call question caps and per-question option caps. Cowork interviews
  now invoke structured questions immediately after owner-visible prose in the
  same turn, and board fallbacks validate mounted response paths explicitly.
- Windows PowerShell subprocess tests now tolerate the host console's legacy
  encoding without turning valid installer output into decode errors.
- BLOCKED pre-delta schema checks now document their recovery path: repair and
  revalidate, or use the explicitly approved schema-migration flag, before
  discarding the snapshot. Ledger-triage board instructions now repeat Cowork's
  mounted-response exception beside the generic Downloads collection commands.
- Security secret closure now preserves current-tree, history/artifact,
  provider, and downstream substates independently, and executable/update
  surfaces are prioritized by their own owner/team/tester/public audience.
- The redacted secret locator now supports repeatable include/exclude filters,
  file and history-blob caps, an internal time budget, and value-free partial
  coverage/resume output instead of losing bounded results to host timeout.
- The secret locator's first pass now follows Search Hygiene by excluding noisy
  generated/reference/vendor paths. Explicit `--include` paths or
  `--include-generated` opt those surfaces back in for separate artifact or
  product-lineage checks.
- Project inventory and current-tree secret scans now use Git tracked files plus
  unignored untracked files when possible, report their enumeration mode, and
  avoid reading ignored clones/caches. Narrow `--include-ignored` scans require
  an explicit include filter.
- Provider connector evidence may now be `not-applicable(reason)` when the
  surface is genuinely absent instead of filling every gate with misleading
  `unconfirmed` values.
- Public security documentation now describes the exact read/write/loopback/
  cleanup boundary of four executable helpers plus their safe-output support
  module. All README translations disclose temporary ledger files and the
  optional loopback board, while the public bug form requires sensitive-output
  redaction and links directly to private vulnerability reporting.
- `SKILL.md` is now a bounded cross-host entrypoint with the complete mode and
  reference router in its first 100 lines. Detailed normal/focus audit procedure
  moved to `references/audit-workflow.md` for progressive disclosure on Codex,
  Claude Code, OpenCode, and compatible hosts.
- Plain audit invocations now default explicitly to `normal`; `scoped` is a
  boundary modifier, and an unnamed focus composes with `normal` instead of an
  undefined implicit depth.
- Claude Code now has a dedicated CLI adapter that resolves helpers from the
  active `${CLAUDE_SKILL_DIR}`, avoids Cowork-only copy workarounds, keeps
  structured questions in the same turn, and documents portable Python launcher
  fallbacks. Helper command examples use one `<skill>` path convention.
- Ledger-triage keeps its consent, grouping, and structured-choice contract in a
  short core reference. The HTML board lifecycle moved to a conditional
  reference that choice-capable hosts do not load unless the owner selects it.
- Repeat-run routing now resolves an unnamed "same focus" only from one clear
  registered focus in the current project ledger. Explicit delta-only reporting
  suppresses unchanged finding bodies without weakening bounded verification or
  coverage work, while changed-path-only requests remain a true scope boundary.
- First-run closeout now classifies each created ledger, routing file, and
  durable handoff as tracked, owner-approved local-only, untracked pending, or
  not versioned. The report exposes unresolved durability without staging files
  automatically.

### Fixed

- Security-batch validation now identifies its machine-readable headers and
  reads only the `Finding`, `Verification tier`, and `Evidence channel` cells.
  A normal word such as `repository` in the check or pass-condition prose no
  longer creates a false second evidence channel.
- Final owner-response validation now compares each canonical decision with the
  actual standard-ledger cell or an explicit custom-schema adapter/archive
  destination. A valid JSON response can no longer pass while the ledger still
  contains its old awareness and status values.
- Search Hygiene now excludes both `external_repos` and `external-repos`, and
  public-safe or visibility-unconfirmed security batch handoffs reject local
  absolute paths.
- Testing-copy refreshes no longer silently lose the `-testing` skill name,
  explicit-only description, display name, or default invocation prompt.
- Ledger-triage board creation now retains language-independent review hashes
  for helper-generated explanation fields. Removing `draftOnly` without
  rewriting the scaffold no longer produces an owner-facing board full of
  generic or untranslated draft text.

Field driver: a multi-surface application security focus run found seven
useful unknown-unknowns while exposing ambiguity around local probes, owner
follow-up mapping, coverage completion, and candidate consolidation. A second
multi-repository desktop/cloud run confirmed those fixes and exposed the need
for safer secret-location evidence, locked-version and copy-lineage working
state, durable batch restart notes, and a shorter owner-facing report. A third
public-site/serverless run confirmed the batch flow while exposing provider
connection-state ordering, mixed owner routing, batch visibility, compact audit
evidence, and dirty-worktree preservation needs. A fourth commercial-game plus
owner-only-tooling run caught actual ledger schema drift, manual complex-reply
application, an initially missed batch handoff, multi-axis secret closure, and
an unbounded secret-locator timeout. A fifth self-audit of a skill-distribution
repository confirmed the follow-up guard end to end and exposed a real
verification-cell false block, Search-Hygiene drift, stale public helper
promises, unsafe terminal display characters, mutable privileged Actions, a
public-report redaction gap, and insufficient PowerShell deletion containment.
A sixth static-site tooling run confirmed the strengthened follow-up flow while
exposing ignored-clone inventory pollution, unapplied owner decisions that could
still validate, repeated batch JSON, and hand-written public handoff paths.

## [0.6.6] - 2026-07-10

### Fixed

- Codex direct-install scripts now default to the current user skill
  directory, `~/.agents/skills`, while keeping explicit custom destinations
  available. They warn about same-name copies in legacy `~/.codex/skills` or
  `$CODEX_HOME/skills` locations without deleting user files automatically.
- All five README translations and the repository agent instructions now
  document both Codex personal and project `.agents/skills` locations. Legacy
  locations are described only as compatibility leftovers that may create
  duplicate entries.
- Codex plugin instructions now point to `Codex > Plugins > Installed` in the
  ChatGPT desktop app and retain the supported marketplace CLI refresh route.
  A regression test protects the new install paths and management guidance.

## [0.6.5] - 2026-07-10

### Fixed

- The structured-choice awareness interview now carries the same
  no-generic-descriptions discipline the 0.6.0 HTML board got: every
  option must pass a self-sufficiency test (an owner who has not read the
  report can classify it from the option alone), labels state the
  finding's everyday consequence instead of a topic shorthand or bare ID,
  and options are written assuming the host may hide descriptions until
  interaction. Field driver: in a distribution-repo self run the
  interview options used two-word internal shorthands, so the owner had
  to open the report file just to answer.
- "Present the findings, then interview" is now explicit about WHERE:
  findings must appear in the owner-visible chat channel before the
  question. On hosts that summarize narration between tool calls
  (Cowork), the findings summary routes through the user-visible message
  channel first.
- Ledger-triage structured-choice batching now points at the same option
  self-sufficiency rule, so triage questions cannot regress into bare-ID
  options.

## [0.6.4] - 2026-07-09

### Fixed

- Resolved-candidate choices now require an owner evidence note only when the
  selected option explicitly sets `noteRequired`, or when the item needs
  external/owner confirmation or secret-related proof. Ledger-only cleanup
  candidates can submit without an owner note and still require the applying
  agent to perform cheap verification before archiving.
- The HTML board now looks up note fields by dataset value instead of CSS
  selector escaping, so response construction is more robust for ledger IDs
  with punctuation.
- Required owner notes are accepted as any non-empty text in any language.
  The submit gate does not parse notes for confirmation, revocation, or
  other keywords; the applying agent reviews note meaning after validation.

## [0.6.3] - 2026-07-09

### Changed

- Updated the HTML ledger-triage decision board's default visual theme to a
  stronger choice-board layout: dark header chrome, light workbench body,
  yellow primary actions, purple selected states, larger choice tiles, and
  clearer state panels. The production template remains self-contained and
  does not include theme-lab labels, external fonts, CDNs, or network calls.

## [0.6.2] - 2026-07-09

### Added

- `ledger_triage_board.py create --serve` now creates the HTML decision board
  and starts the localhost submit server in one foreground command. Both
  `create --serve` and `serve` support `--write-url`, `--write-pid`, and
  `--write-board-dir` for hosts that run the server detached.
- The board server writes `server-state.json`, and cleanup shuts down only
  the matching localhost server through its shutdown token before deleting
  the temporary board directory.
- Board items now support an internal `itemType` field for agent-only ledger
  section maintenance. `draft --include-ledger-hygiene` can scaffold stale
  version, test-count, release, and audit-log summary checks as hidden
  `ledger_section` candidates.
- `validate --write-ledger-suggestions` writes a temporary
  `ledger-triage-ledger-suggestions.md` file with selected ledger edit hints
  and an Audit Log draft without modifying `BLINDSPOT_LEDGER.md`.

### Changed

- HTML submit success and download fallback copy now tells the owner the
  response is saved or downloaded, they can tell the agent the answers are
  ready, and the tab can be closed. The copy was updated across ko/en/ja/zh/es.
- Ledger-triage instructions now prefer `create --serve` for no-choice
  file-writing hosts and document server-state cleanup, hygiene drafting,
  internal `itemType`, and temporary ledger-suggestion files.

## [0.6.1] - 2026-07-09

### Fixed

- Added a root `pytest.ini` so `python -m pytest` collects only this repo's
  `tests/` folder instead of trying to recurse into local reference clones
  under `external_repos/`.

### Changed

- Added a short `Mode Router` near the top of `SKILL.md` so hosts that read
  the first 100-200 lines first can route `ledger-triage`, `deep`, `quick`,
  `focus: ux-ui`, planning, post-implementation, and interview runs before
  scanning the longer workflow details.

## [0.6.0] - 2026-07-08

Ledger growth became its own maintenance problem: once a good
`BLINDSPOT_LEDGER.md` accumulates many open rows, asking the owner to
classify them one by one in chat becomes too slow. This release adds a
dedicated triage mode and a no-choice-host decision board.

### Added

- `mode: ledger-triage`: a maintenance mode that reads an existing ledger
  and groups open findings, skipped/deferred rows, resolved candidates, and
  decision packets into quick cleanup, safe accept, decision bundle,
  owner-detail, external-confirmation, and needs-reexplain categories. It
  does not run a new blindspot audit or create new project findings.
- `references/ledger-triage.md`: the triage workflow, category definitions,
  beginner-explanation rules for `unknown_unknown` / `unconfirmed` /
  localized unknown rows, host routing, board input shape, response
  interpretation, and ledger update rules.
- Temporary HTML decision board for no-choice hosts:
  `templates/ledger-triage-board.html` plus
  `scripts/ledger_triage_board.py`. The helper creates
  `.blindspot-tmp/ledger-triage-*`, optionally serves it on localhost,
  validates `blindspot-triage-response.json`, and safely deletes temporary
  files only after decisions were applied.
- Helper automation for repeat ledger triage: `draft` scaffolds board input
  JSON from existing ledger tables, `validate --write-plan` writes a
  temporary application-plan skeleton, and cleanup prints an Audit Log
  suggestion after deleting the temporary board.
- Response collection helpers for static-board fallbacks: `validate
  --response`, `validate --collect-response`, and `collect-response` import
  downloaded response JSONs from a known path or Downloads-like folder,
  choose the newest matching `completedAt` when duplicates exist, and then
  run the same board/ledger validation path.
- Unit checks for the ledger-triage helper, including self-contained HTML,
  response validation failures, hash mismatch, marker/path safety, and
  cleanup refusal without `--confirm-applied`.
- `evals/fixtures/ledger-triage-large-ledger/`: a 20+ row synthetic ledger
  fixture that requires grouped triage, beginner explanations, structured
  choice routing, HTML-board routing on no-choice hosts, validated response
  application, and safe cleanup.
- `evals/RUNS.md` now records a 0.6.0 self-run of the ledger-triage HTML
  board flow, including validation and temporary-plan routing.

### Fixed

- `draft` output is now marked `draftOnly: true`, and `create` refuses that
  unreviewed scaffold unless the marker is removed after review or
  `--allow-unreviewed-draft` is passed explicitly for tests/debugging.
- Secret cleanup detection is now limited to concrete secret-value patterns
  or secret terms in exposure contexts, so normal phrases such as password
  reset copy, API docs, and token budgets do not trigger Git-history secret
  scan guidance.
- `draft` now handles localized ledger tables such as Korean `발견 항목`,
  `결정 묶음`, and `감사 이력`, with Unicode-aware header matching so
  Korean `상태`, `인지 상태`, and `항목` columns are parsed correctly.
- `draft` now also uses Korean `결정`, `인지 분류`, and `후속 제안`
  columns to seed current status, awareness, follow-up explanation, and
  close/reject/defer recommendation hints.

### Changed

- Host adapters now route decision-heavy no-choice ledger triage through
  the HTML board instead of a giant numbered reply.
- Ledger-triage host precedence is now explicit: on hosts with a structured
  choice tool (Cowork, Claude Code), collect decisions through that tool
  using a bundle-first batching scheme (one multiSelect per cleanup group,
  one question per decision bundle, priority-ordered rounds) so the 4-option
  cap rarely bites; the HTML board is the fallback for file-writing hosts
  with no choice tool, and a numbered reply is for read-only/chat-only
  hosts. The Cowork adapter now warns that the isolated sandbox cannot serve
  a reachable `localhost` and the owner's Downloads are unmounted, so
  `AskUserQuestion` is strongly preferred there over the board.
- Ledger triage is now explicitly consent-gated: "clean up" or "organize"
  means prepare recommendations and collect owner choices, not apply
  `accepted` / `deferred` / archive decisions from the agent's own
  judgment.
- Ledger-triage mode inference now covers natural follow-up requests to
  organize, close, process, handle, decide, or go through existing ledger
  findings/items/rows after an audit, even when the owner does not know the
  internal mode name.
- The HTML decision board now embeds a plain ledger-row summary for every
  item, uses localized status/action labels, presents options as
  scan-friendly rows with tradeoffs, and allows partial submission so
  unselected rows remain unchanged.
- Ledger decision boards now separate row metadata from readable content
  (`Findings/ID/status` stays small while the main text contains only the
  issue), and Korean boards rewrite common specialist shorthand such as
  CTA, AJAX, ARIA, and `prefers-reduced-motion` into plainer owner-facing
  wording.
- Post-response triage now routes validated choices before applying work:
  any `needs_reexplain` choice pauses other saved decisions for explanation,
  simple ledger-only choices apply directly, and implementation-heavy choices
  require a temporary execution plan that is deleted after the outcome is
  recorded in the ledger.
- HTML board submit now treats localhost server-save as the normal path.
  If a host blocks server save, the fallback download uses a board-specific
  filename and tells the owner to leave it in Downloads so the helper can
  collect it instead of asking the owner to move files around.
- Decision responses now separate canonical `status` from free-form
  `intentDetail`, while older `statusIntent` inputs remain a compatibility
  path. Secret/token-related closure paths now surface current-tree and Git
  history checks before a row is treated as resolved.
- Decision responses now include `optionId` so multiple choices with the
  same action, such as two different `accept` paths, validate against the
  exact selected option instead of collapsing by action alone.
- Temporary application plans now label ledger-only choices as ledger-only
  instead of inventing file-edit TODOs, and validation highlights owner
  notes that may justify a ledger-only closure or deferral.
- `serve` can write its localhost URL to a file with `--write-url`, and
  cleanup prints a localized Audit Log suggestion for localized boards.
- The HTML board now blocks `resolved_candidate` submission, copied JSON,
  and preview JSON until the owner enters a short evidence note.
- Ledger triage board directory names preserve a longer readable board id
  token so multiple temporary boards are easier to distinguish.
- Ledger lifecycle and ledger template now document that triage boards are
  temporary collection surfaces, not durable project artifacts.
- All five READMEs and prompt examples mention `mode: ledger-triage`.
- The skill description now front-loads `BLINDSPOT_LEDGER.md` triage and
  ledger-cleanup trigger language while keeping cross-host, cross-domain
  audit triggers intact.
- Bumped plugin metadata to `0.6.0` (both manifests).

## [0.5.2] - 2026-07-06

Second field run of the focus machinery (an artist portfolio +
commission site, focus/ux-ui diff run, Opus via Claude Code) confirmed
all three 0.5.1 fixes working - the named peer walk even prevented a
false pricing finding by proving "inquire-only" is peer-normal - and
exposed one new drift: the run helpfully copied the owner profile into
host-local memory after writing the ledger.

### Fixed

- Context-canon rule (SKILL.md context intake): the ledger's `Project
  Context` section is the canonical and only home for project context
  and owner profile. Do not fork it into host-local memory (CLAUDE.md
  notes, host memory features) uninvited - a second copy drifts across
  sessions and hosts, the exact surface-alignment failure the AI And
  Agent lens flags in audited projects. If host conventions call for a
  memory note, write a pointer to the ledger, never a restatement.

### Added

- Second field-run row in `evals/RUNS.md` (category-only naming).

### Changed

- Bumped plugin metadata to `0.5.2` (both manifests).

## [0.5.1] - 2026-07-06

First field run of the 0.5.0 focus machinery (a commercial
symbolic-reading web app, focus/ux-ui diff run, Opus via Claude Code):
focus targeting, pack probes, coverage-debt clearing, credit sections,
and the interview split all worked. Three compliance drifts appeared,
all of the known "rule exists but is not marked mandatory" shape.

### Fixed

- Peer walk made explicitly non-delegable (`packs/ux-ui.md`): name the
  2-3 real peers compared; listicles and agency blogs are leads for
  choosing peers, never the evidence behind a table-stakes claim (the
  run backed a category-expectation finding with two roundup links and
  named no peers).
- New Canonical Values section in `references/report-template.md` plus a
  matching line in SKILL.md workflow step 6: priority/confidence/
  awareness are single English enum values even in non-English reports
  (the run emitted `now~next` ranges and a localized awareness
  placeholder), and awareness stays `unconfirmed` until the interview
  happens - a pre-filled guess anchored wrong in the field (a finding
  pre-labeled `unknown_known` was `unknown_unknown` at interview).
- `evals/fixtures/frontend-ux-gap/EXPECTED.md` Run B fail criteria now
  catch aggregator-only category claims, unlabeled source-tier mixing,
  non-canonical values, and pre-interview awareness guesses.

### Added

- `evals/RUNS.md` started with the first recorded field run
  (category-only naming per the AGENTS.md privacy rule).

### Changed

- Bumped plugin metadata to `0.5.1` (both manifests).

## [0.5.0] - 2026-07-06

Owner field feedback from two web-project audits plus repeated
same-project re-runs exposed two structural gaps: audits under-reported
the owner's weak domains (an engineer-owner's UX/UI surface got skimmed,
not probed - domain detail structurally loses the findings-cap ranking to
legal/security/data items), and zero-delta re-runs closed with "nothing
changed" instead of digging into the next tier. Minor bump: this release
adds a new axis (focus runs) rather than refining existing behavior.

### Added

- Focus runs (`focus: <domain>`): modes now compose with an optional
  domain focus that audits one domain's entire surface under the
  scoped-audit rules (SKILL.md Modes + Audit Scope). Findings append to
  the project ledger as delta rows (`scope: focus/<domain>`); never a
  second ledger.
- `references/packs/` - single-domain deep probe sets, loaded ONLY for
  focus runs or weak-domain escalation, never in a normal full audit.
  First pack: `packs/ux-ui.md` (device/viewport reality, appearance
  modes, state completeness, flow integrity, input and access, feedback
  and affordance, visual system), with an explicit identity guard: every
  probe is an awareness/decision question ("no evidence anyone DECIDED
  about dark mode"), never a UI-review fix order, and prescriptions
  propose cheap checks (window resize, tab-through, axe, Lighthouse,
  Storybook state coverage) instead of running them.
- Weak-domain escalation (Workflow step 4): when the owner profile marks
  a domain weak AND the project has a substantial surface there, a full
  audit must not silently skim it - inline-load at most ONE pack (`deep`
  mode, budget allowing) or emit a meta-finding that names the skim and
  prescribes the focus run as the cheapest check. "The owner does not
  know what they do not know about <domain>" is itself an unknown
  unknown; the un-run pack is recorded as coverage debt.
- Descent rule (Ledger And Diff Runs rule 10): a zero-delta run spends
  remaining budget going deeper instead of closing empty - highest-value
  un-run pack first (owner-inverse weighted), then watchlist
  re-examination (candidates that lost the cap ranking get their
  hearing), then the least-inspected subsystem; one step per run,
  recorded in the audit log so the next run continues instead of
  repeating. Explicit floor: when packs, watchlist, and subsystems are
  exhausted, "explored to current depth" is the honest end state -
  descent never becomes finding-invention.
- Coverage debt now includes applicable focus packs (rule 8). Ledger
  audit-log Notes, report scope line, and `ledger-lifecycle.md` record
  packs run and descent steps; `lenses.md` gains a "Lenses vs Focus
  Packs" boundary note.
- `evals/fixtures/frontend-ux-gap/`: two-run fixture - a backend-expert
  owner, an untracked-UX web surface about to widen to phone users. Run
  A (full audit) must emit the escalation meta-finding (a code-level
  security catch does not discharge the UX domain); Run B
  (`focus: ux-ui`) must find concrete state/device/access gaps phrased
  as decisions, not taste.
- `external_repos/` (git-ignored, matching the audit's own Search
  Hygiene excludes) for reference-only clones consulted during pack
  design, with README attribution: mistyhx/frontend-design-audit (MIT),
  raintree-technology/hig-doctor (MIT structure/tooling; HIG text ©
  Apple, not copied), Community-Access/accessibility-agents (MIT).
  Ideas and structure in, prose out.

### Changed

- All five READMEs: focus runs and zero-delta descent in "What It Does",
  reference-repo attribution under Attribution.
- Bumped plugin metadata to `0.5.0` (both manifests).

## [0.4.5] - 2026-07-06

A near-perfect field run on a product project (Codex, deep, no-choice
host) - Project Context created on an older ledger, named-peer scan,
contradiction finding - still compressed the awareness check into a
passing sentence keyed to ledger IDs, which a first-time user would never
answer, leaving every finding `unconfirmed` forever.

### Changed

- The no-choice awareness check is now verbatim-grade, not paraphrasable
  (SKILL.md workflow step 7, `references/report-template.md`,
  `references/host-surfaces.md`): it must be the report's FINAL element,
  use report finding numbers (never ledger IDs or internal labels),
  include reply examples with the qualifier forms and the `3?` path, and
  carry a one-line motivation ("answering is optional, but classified
  findings stop being re-raised as new"). Same failure shape as the
  0.4.2 choice-tool fix: a concrete template not marked mandatory gets
  summarized away.
- Bumped plugin metadata to `0.4.5` (both manifests).

## [0.4.4] - 2026-07-06

A self-audit - the skill run against its own repository (Codex, deep
mode) - validated the 0.4.3 coverage-debt bootstrap in the field and
returned four repository findings; this release closes them.

### Added

- `scripts/check-version-bump.py` + CI step: if skill or package content
  changed since the latest semver tag, the plugin version must be
  bumped - otherwise the release job silently skips and installed users
  never receive the update (the same stale-install failure mode as the
  desktop-app incident). Docs-only changes may still ship without a
  bump.
- `SECURITY.md`, plus a short Security section in all five READMEs and
  the Codex manifest privacy URL now pointing at it: what the scripts
  do, that nothing calls the network or collects telemetry, and how to
  report concerns privately.
- `evals/README.md` "Recording runs": a one-row-per-run `RUNS.md` log
  format so field-run verdicts survive across skill versions. Automated
  CI evals remain deliberately out of scope (live agent + judgment
  required); recorded as a deliberate skip.

### Fixed

- All six install scripts (`install-claude-user`, `install-claude-project`,
  `install-codex`, PowerShell and Bash) now replace the target
  `blindspot-audit` folder (with a path-safety check) instead of
  overwrite-merging into it. Files renamed or deleted upstream no longer
  linger in user installs silently steering agents - reproduced in a
  sandbox before fixing.

### Changed

- Report language rule sharpened (`references/report-template.md`): the
  owner's conversation language wins even when every file read during
  the audit is in another language (field data: an audit over an
  all-English repo replied to a Korean owner in English).
- Bumped plugin metadata to `0.4.4` (both manifests).

## [0.4.3] - 2026-07-06

Field run on a commercial web project (Opus via Claude Code, diff run)
confirmed 0.4.2's choice-tool and zero-delta rules working, and exposed
three refinements: obvious context was inferred but never persisted,
coverage debt went undetected on a ledger with no scan records, and
audits stay defensively risk-only unless opportunity findings are
anchored to something mechanical.

### Added

- Context inference ladder (SKILL.md intake + ledger template): context
  readable from the files is recorded WITHOUT asking as
  `inferred (evidence: <path>)` with an interview line for corrections;
  uncertain context proceeds as a labeled assumption with one folded-in
  confirmation; only context absent from the files gets asked. Personal
  attributes are recorded only as generalized strong/weak areas, and the
  resulting `Project Context` section must be written to the ledger
  whatever the path - inferred-but-unpersisted context forces every
  future run to re-infer it.
- Coverage-debt bootstrap (Ledger And Diff Runs rule 8): a ledger whose
  audit log carries no scan notes (older audit versions) treats EVERY
  scan as never-run; reusing a previous run's scan results never covers
  scans that did not run. The report scope line now states scans applied
  and coverage debt cleared.
- Opportunity probe (fresh-eyes Question 2, External Change lens,
  guardrails): walk the ledger's open findings, watchlist, and documented
  frictions asking "did a platform or tool this project already uses
  ship a capability that dissolves this cheaply?" A tracked friction
  whose solution became cheap is a stale assumption and a legitimate
  finding - the anchor to an already-documented problem is what keeps it
  out of feature-brainstorm territory; the prescription stays a decision.

### Changed

- Bumped plugin metadata to `0.4.3` (both manifests).

## [0.4.2] - 2026-07-06

Two field runs on the same knowledge-base project - a diff run (Opus) and
a full deep re-run (Fable via Claude Code) - exposed three behavior gaps:
the audit diffed the project but never its own coverage, the context
intake wording had a hole on re-runs, and a choice-capable host shipped
the numbered awareness fallback instead of asking through the tool.

### Added

- Coverage-diff rule (SKILL.md Ledger And Diff Runs rule 8, ledger
  template audit log, ledger-lifecycle): each run records which scans it
  applied; diff runs treat scans that have never run on this project
  (peer expectation scan, context intake, external-change scan) as
  first-run work - a zero project delta does not satisfy a scan that
  never happened.
- Zero-delta diff run definition (rule 9): when the project delta is near
  zero, say so plainly; the run earns its keep through remediation
  verification, re-verification of time-sensitive external findings,
  coverage-debt scans, and context intake if the section is missing -
  never through invented findings.
- Concrete multiSelect interview shape in the structured-choice adapter
  (one question, one option per finding labeled by consequence title),
  plus an explicit rule that the numbered awareness check is a fallback
  only and must not appear in reports on choice-capable hosts (matching
  text strengthened in `report-template.md` and SKILL.md workflow
  step 7).

### Changed

- Peer expectation scan is now explicitly mandatory whenever the
  fresh-eyes scan runs on a full audit - it is half of Question 1, not
  optional garnish; diff runs repeat it only when never run or when the
  project's category/stage changed.
- Context intake wording now covers re-runs on ledgers that predate the
  `Project Context` section: if the section is missing, collect it once,
  whatever the run number.
- Source-tier rule: cite the primary source itself, not the aggregator or
  comparison article that led to it.
- Bumped plugin metadata to `0.4.2` (both manifests).

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
  `git update-index --really-refresh` as the fallback. Derived artifacts
  (the packaged `.skill`, the synced plugin copy) are regenerated and
  verified on the owner's machine right before committing - an in-session
  build can package a truncated mirror snapshot that in-session
  verification cannot catch (it compares against the same corrupted view).
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
