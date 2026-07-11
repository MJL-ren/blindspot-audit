# Ledger Lifecycle

Use this reference when a blindspot audit needs durable project memory. The
ledger is the permanent fix for the self-selecting-context problem: once a
blind spot is written into the project, it can never be an unknown unknown
again - and future audits diff against it instead of re-nagging.

## Discover Existing Ledgers

Before creating a new file, search for existing risk or blindspot surfaces.
Prefer the host's native file-search tools (e.g. Glob for
`**/BLINDSPOT_LEDGER.md`, `**/*blindspot*`, `**/*risk*register*`,
`**/*release*checklist*`) - they behave identically across OSes. The CLI
fallback:

```text
rg --files <project-root> -g "BLINDSPOT_LEDGER.md" -g "*blindspot*" -g "*risk*register*" -g "*release*checklist*" -g "!node_modules/**" -g "!runtime/**" -g "!docs/archive/**"
```

Also check normal routing files when present:

- `docs/README.md`
- `docs/INDEX.md`
- `docs/operations/README.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `README.md`
- `AGENTS.md` / `CLAUDE.md`

If an existing ledger is found, use diff-run behavior. Do not create a
duplicate.

If the project uses version control, also check whether the ledger is part
of the durable tracked state (for example with `git ls-files` or the host's
equivalent status view). An untracked ledger is a traceability blind spot:
future checkouts or agents may not see the audit trail even though the file
exists locally.

Check for nested repositories before trusting any git answer: the audit
boundary may contain more than one repo (a parent folder holding a game
repo, a monorepo with vendored repos, a workspace of sibling checkouts).
Run the tracking check inside the repo that owns the ledger path
(`git -C <that-dir> ...`), not the outer folder - the outer repo saying
"untracked" or "clean" proves nothing about the inner one. (Field data: a
parent folder and its game repo gave different answers on the same path.)

## Choose The Ledger Location

Prefer the most discoverable project-local documentation location:

1. `docs/operations/BLINDSPOT_LEDGER.md` when `docs/operations/` exists or
   the findings affect release, operations, safety, billing, support, data
   loss, or recurring audits.
2. `docs/BLINDSPOT_LEDGER.md` when a project has `docs/` but no operations
   folder.
3. `<package-or-app>/docs/BLINDSPOT_LEDGER.md` when the audit boundary is
   one package inside a monorepo and that package has its own docs.
4. `BLINDSPOT_LEDGER.md` at the project root when there is no docs folder.

If two locations are plausible, choose the one future agents are most
likely to read first and mention the assumption.

If the project separates public and private surfaces (a deploy folder, a
publish pipeline, a public-repo export, spoiler-free docs), the ledger must
inherit the PRIVATE side. An audit trail leaking into production or a
public export is itself a blind spot. Cheap checks: the deployed URL for
the ledger path should 404, the export manifest/denylist should cover it,
or the ledger should live outside the published directory entirely. Record
which check was done in the ledger's audit-log notes.

Multi-repo workspaces: a finding that belongs to one repo goes in THAT
repo's ledger (create it there if needed); never let a finding about repo
A live only in repo B's ledger - the next audit of repo A will not see it.
Workspace-crossing findings go in a workspace-level ledger only when the
workspace root is itself a durable, private location.

Sensitive findings vs public ledgers: a ledger committed to a public repo
is published information. Do not write exploitable detail (secret
locations, unpatched attack paths, credential names) into it. In order of
preference: keep the detailed row in a private workspace-level ledger and
put a generalized one-liner in the public one; or generalize the row and
hand the detail to the owner in the report/chat only; or ask the owner
where security detail should live. Record which option was used.

## Create The First Ledger

Use `templates/BLINDSPOT_LEDGER.md` as the starting shape. Write the prose
in the owner's language; keep IDs, status, and awareness values in English.
If the project has its own doc conventions (frontmatter, naming), follow
them so the ledger looks native. Fill:

- project name and path.
- audit date.
- audit mode and host.
- scope boundary.
- project context (intent, users/regions, stage, owner strong/weak areas,
  web-search privacy rule) - collected once via the context intake, every
  item skippable; skips are stored as `skipped (assumption: ...)`.
- inspected surfaces.
- findings table.
- decision packet, if the host could not ask interactive choices.

IDs should be stable and date-based:

```text
BS-YYYYMMDD-01
BS-YYYYMMDD-02
```

IDs are permanent; never renumber. New runs append.

## Route The Ledger

After creating a ledger, make it discoverable if the project already has
routing surfaces.

Common routing edits:

- Add it to `docs/operations/README.md` under document list.
- Add it to `docs/INDEX.md` if that index routes active owner docs.
- Index-style projects: if docs are routed through a maintained index
  surface (`Docs/_Index/README.md`, a `DocIndex.csv` catalog, a wiki
  sidebar), register the ledger there as one entry IN THE PROJECT'S OWN
  FORMAT - a CSV catalog gets a CSV row, not a markdown link.
- Mention it in handoff only when the current next session must act on it.

Do not create broad routing systems just for the ledger. Add one small
pointer to an existing routing file.

After routing, verify the ledger and routing edit are visible in the
project's durable change surface. If they are local-only or untracked, flag
that in the report as a follow-up rather than silently assuming future
agents will see them.

Before finishing the same first run, classify every created ledger, routing
edit, and durable batch handoff:

- `tracked`: the owning repository's `git ls-files` or equivalent confirms it.
- `owner-approved-local-only`: an explicit owner decision or standing ignore
  rule intentionally keeps it local.
- `untracked-pending`: it exists but is neither tracked nor approved local-only.
- `not-versioned`: no version-control boundary is available.

Check the repository that owns each path, including nested repositories. Never
stage automatically. Put every `untracked-pending` artifact in the final report
or Decision Packet with the path and the choices to track it, deliberately keep
it local, or move it. A routing link does not make an untracked target durable.

## Compact Audit Log And Evidence

Keep the Audit Log table scannable. Give each durable run a ledger-local ID:

```text
BA-YYYYMMDD-01
BA-YYYYMMDD-02
```

IDs are unique within the ledger and never renumbered. The Audit Log Notes cell
contains the run ID plus one short result, for example:

`BA-20260711-01; focus/security; completed with limits; details below`

When coverage, verification tier, external research, secret-search scope, or
provider limits would make that cell long, keep the detail in the same ledger:

```markdown
## Audit Evidence

### BA-20260711-01 - focus/security
- Coverage: <surface-matrix result and uninspected/owner-confirm-needed rows>
- Verification: <tiers actually run; proposed checks stay labeled proposed>
- External evidence: <channels and zero-signal/skipped scans>
- Secret search: <manual-heuristic/dedicated-scanner + tree/history/provider coverage>
- Provider connector: <presence/auth/callability/scope/consent without private identifiers>
- Owner response: <awareness/disposition/next-action delta when answered>
```

Do not duplicate full finding evidence in this section. The next audit follows
the run ID from the table to this detail. Apply the ledger's visibility policy:
public or unconfirmed ledgers use generalized wording and omit exploitable
paths, payloads, credential/provider names, and private identifiers. Do not
create a separate sidecar file solely for audit evidence.

For an existing ledger, preserve its table columns and local heading style. Add
an Audit Evidence section only when a compact Notes cell cannot retain the
necessary run limits; otherwise keep the existing shape. This is not permission
for a whole-ledger schema migration.

## Protect Existing Worktree Changes

Before changing an existing ledger, routing file, or durable batch handoff:

1. Identify the repository that owns each target path, including nested repos.
2. Capture `git status --short` in that repository. For the ledger and every
   other target, inspect both unstaged (`git diff -- <path>`) and staged
   (`git diff --cached -- <path>`) changes before editing.
3. Keep the baseline diff/content in session working state, not in a new
   project temp file. If Git is unavailable or the file is untracked, retain a
   read-only content/hash baseline instead.
4. Re-read the current target immediately before editing. Apply a contextual,
   minimal patch to selected rows/sections only; never replace the whole file,
   reset, checkout, or normalize unrelated content.
5. Compare the post-edit target diff with the baseline. Existing hunks must
   remain, and files that were already dirty but outside the chosen targets
   must be unchanged.
6. Run `git diff --check -- <ledger>` and, when staged target changes exist,
   `git diff --cached --check -- <ledger>`. Verify unique `BS-`, `DP-`, and
   `BA-` IDs plus the expected number of new/changed rows and Audit Log entries.

If pre-existing changes cannot be distinguished from the proposed edit, stop
before writing and report the ambiguity. A cleanup or audit request never
authorizes overwriting another session's work.

## Deterministic Audit Follow-Up Guard

Use `scripts/audit_followup_guard.py` for every existing-ledger write outside
`mode: ledger-triage`. Resolve it from the active skill folder. It validates and
previews; it never interprets owner language or edits the ledger.

1. Before the first ledger edit:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" snapshot --project-root "<root>" --ledger "<ledger>"
   ```

   The snapshot lives under `.blindspot-tmp/audit-followup-*`, stores protected
   finding-table headers/order, defined stable IDs, file hash, and hashed
   dirty-target state, but not ledger row prose or diff contents.

2. After writing new audit rows, before the owner interview:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" validate --snapshot "<snapshot>" --ledger "<ledger>"
   ```

   This schema-only validation blocks added/removed/reordered columns in the
   existing finding tables. New Audit Evidence tables remain allowed.
   `--allow-schema-change` is permitted only after the owner explicitly approves
   a ledger schema migration; never infer approval from an audit request.

3. After an explicit owner reply, the agent semantically maps the reply into a
   temporary JSON object inside the snapshot's `audit-followup-*` directory.
   Do NOT use keyword matching or language-specific parsing. Use v1 for
   individual decisions. Use v2 `decisionGroups` when several findings share
   the same awareness, disposition, reason, trigger, batch, and next action;
   the helper expands groups deterministically before preview and rejects an ID
   repeated across groups or individual decisions:

   Schema `blindspot-owner-response.v1` remains supported for the individual
   `decisions` form.

   ```json
   {
     "schema": "blindspot-owner-response.v2",
     "auditRunId": "BA-YYYYMMDD-NN",
     "ownerResponseRecorded": true,
     "expectedFindingIds": ["BS-YYYYMMDD-01", "BS-YYYYMMDD-02"],
     "unmappedReferences": [],
     "decisionGroups": [
       {
         "findingIds": ["BS-YYYYMMDD-01", "BS-YYYYMMDD-02"],
         "awareness": "unknown_unknown",
         "disposition": "deferred",
         "reason": "<owner reason, never a secret value>",
         "recheckTrigger": "<restart trigger>",
         "batchId": "security-batch-YYYYMMDD",
         "batchPath": "docs/SECURITY_BATCH_PLAN_YYYY-MM-DD.md",
         "nextActionRoute": "agent_work",
         "nextAction": "<plain next action>"
       }
     ],
     "decisions": []
   }
   ```

   A ledger using exact `ID`, `Awareness`, and `Status` columns needs no
   adapter. For any localized or custom schema, add an explicit
   `applicationMap`; never guess that a local word means a canonical enum:

   ```json
   {
     "applicationMap": {
       "idColumn": "ID",
       "awarenessColumn": "인지 분류",
       "dispositionColumn": "결정",
       "awarenessValues": {"unknown_unknown": "unknown_unknown"},
       "dispositionValues": {"deferred": "보류"},
       "destinations": {}
     }
   }
   ```

   `destinations` defaults each decision to `row`. Set an ID to `archive` only
   for an explicit `resolved` or `rejected` move. The final guard then confirms
   that the open row disappeared while the stable ID remains defined.

4. Show the owner-response delta before applying it:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" preview --ledger "<ledger>" --data "<response.json>"
   ```

   A blocking preview catches duplicate/unknown IDs, group conflicts,
   unresolved references, conflicting batch paths, unsupported enum values,
   missing skip reasons/triggers, owner follow-ups with no next action, and a
   missing or invalid custom-ledger adapter. Unmentioned findings remain
   unchanged.

   For one explicit awareness-only reply, the helper can prepare the temporary
   v1 response and run the same preview without editing the ledger:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" prepare-awareness --snapshot "<snapshot>" --audit-run "<BA-ID>" --finding "<BS-ID>" --value unknown_known
   ```

   Standard `ID`/`Awareness`/`Status` ledgers need no adapter arguments. For a
   localized/custom table, pass the exact `--id-column`, `--awareness-column`,
   `--disposition-column`, and final `--ledger-awareness-value`; never translate
   column names or enum values by guessing. The command writes its response JSON
   inside the snapshot directory and prints the normal application target. The
   agent still makes the one contextual cell edit, runs final validation, and
   cleans up only after success.

   For 2+ findings deferred to one named security batch, create the mechanical
   handoff skeleton from the validated preview before filling its judgment
   fields. This command never edits the ledger:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" scaffold-security-batch --project-root "<root>" --ledger "<ledger>" --data "<response.json>" --visibility unconfirmed
   ```

   It writes the response's repo-relative `batchPath`, exact verification
   headers, one placeholder row per finding, and a ledger-backlink suggestion.
   Replace the placeholders with one check, one tier, and one evidence channel
   per row before final validation. `public-safe` and `unconfirmed` handoffs use
   generalized detail and reject drive, home, UNC, `file://`, and other local
   absolute paths.

5. After applying only the previewed delta and creating any required durable
   batch handoff/backlink:

   ```text
   python "<skill>/scripts/audit_followup_guard.py" validate --snapshot "<snapshot>" --ledger "<ledger>" --data "<response.json>"
   python "<skill>/scripts/audit_followup_guard.py" cleanup --snapshot "<snapshot>" --confirm-applied
   ```

   Final validation blocks unauthorized schema drift, removed/duplicate stable
   IDs, owner decisions that were not actually written to the mapped ledger
   cells/archive, missing 2+-finding security batch files or ledger backlinks,
   unsafe public handoff paths, missing visibility policy, and verification
   rows that combine multiple tiers or evidence channels. Its output lists the
   applied mapping per finding. Remove the temporary response JSON with the
   snapshot.

If the helper cannot run, perform the same snapshot/header comparison and
owner-visible delta preview manually. Never skip the guard by directly applying
a complex reply.

## Diff Runs, Delta-Only, And Descent

When a ledger exists, treat it as an input rather than truth. Re-check stale or
high-impact rows against current evidence, then classify the run delta as
`new`, `changed`, `confirmed`, `downgraded`, `resolved`, or `needs-decision`.
Do not repeat unchanged pending rows unless they block the current goal.

Preserve local IDs, headings, status language, and prior worktree changes. Move
resolved/rejected open rows to the one-line archive and keep their stable IDs.
If this session remediated a finding, the ledger must not finish while still
describing it as open.

Diff the audit's coverage too. A scan or applicable registered pack that never
ran remains first-run coverage debt even when the project files did not change.
Do not create debt for an inapplicable pack. Read compact Audit Log run IDs and
their Audit Evidence limits before deciding whether coverage exists.

When the owner explicitly asks for "new or changed only", treat that as a
reporting filter unless they also limit the inspection boundary:

- Continue bounded stale/high-impact verification, required coverage-debt work,
  and one normal descent step.
- Never print unchanged finding blocks again. Record only an unchanged count,
  compact coverage result, and any verification that materially changed trust.
- Report genuinely new findings from a previously uninspected applicable
  surface because they are part of the requested delta.
- If the owner instead says "inspect changed files only" or names a concrete
  changed path, that is a scoped inspection boundary. Do not descend outside it.

For a near-zero delta, say so plainly. Do not invent findings. Complete missing
context/coverage, verify prior remediation or time-sensitive sources when
useful, then descend at most one step:

1. highest-value applicable registered pack never run (in a light mode, propose
   it rather than silently expanding).
2. lower-signal/watchlist candidates against current evidence.
3. least-inspected subsystem from the inventory.

Record the descent step in Audit Evidence so the next run continues rather than
repeating it. When all three surfaces are exhausted, state that current depth is
complete and only project/external change can create a new delta.

## Update Existing Ledgers

On later runs:

- Read the ledger first - the `Project Context` section before anything
  else. Refresh only entries that look stale or that the owner reopens;
  items marked `skipped` are respected and never re-asked.
- Record a short run ID/result in the Audit Log Notes cell. Put applied scans
  (external-change, peer expectation, context intake, focus packs), limits, and
  any descent step a zero-delta run took in that run's Audit Evidence entry when
  they do not fit one compact line. Future diff runs use both surfaces to find
  coverage debt and continue the descent instead of repeating it.
- Verify stale or high-impact items against current code/docs.
- Add only new or changed findings.
- Findings that came from the external/web scan keep their source URL in
  the row (Finding or next-check cell). The next audit re-verifies from the
  source instead of re-searching from scratch.
- Scoped audits (a single document, feature, or module) and focus runs
  (`focus: <domain>`) append their delta rows to this project ledger with
  the scope noted in the audit log - they do not get their own ledger
  file.
- Ledger triage (`mode: ledger-triage`) does not add new audit findings.
  It groups existing open rows, skipped/deferred items, resolved candidates,
  and decision packets into owner choices. It may recommend status changes
  but must not apply them from agent judgment. Apply only owner-selected
  and validated decisions, preserve the ledger's local status language, and
  record the board id or structured-choice path in the audit log.
- Mark changed status instead of rewriting history (date the change in the
  status cell).
- Keep local labels and decision terms.
- After an owner awareness reply, update awareness and implementation
  disposition independently and add an Audit Log owner-response note. A later
  batch is `deferred`, not proof of a `deliberate_skip`.
- After a `focus/security` reply explicitly groups two or more findings into a
  later implementation batch, link the lightweight security batch handoff from
  those ledger rows. Keep the ledger as the finding/evidence source of truth;
  the handoff stores only restart order, prerequisite decisions, verification
  matrix, completion criteria, and next-session start. Delete or archive the
  handoff after closeout while preserving the concise result here.

Use these statuses unless the project already has its own:

- `pending`: found, not yet decided.
- `accepted`: user/project accepted the issue.
- `deferred`: intentionally postponed with reason.
- `rejected`: intentionally rejected with reason.
- `resolved`: no longer present or fixed.

Track owner awareness separately from status - it changes the follow-up:

- `unknown_unknown`: owner did not know -> explain + cheapest first step.
- `unknown_known`: owner knew but it was written nowhere -> the fix is
  documentation (a checklist/tracking-doc line), not implementation.
- `unconfirmed`: interview not yet done (non-interactive run).

Implementation disposition is separate:

- `pending`: no implementation decision yet.
- `accepted`: owner accepted it as work to track.
- `deferred`: owner will handle it later or in a named batch.
- `deliberate_skip`: owner intentionally declines it -> move to the skip
  section with reason and a re-check trigger.
- `rejected`: finding is wrong/not applicable or intentionally rejected.
- `resolved`: evidence shows the gap is gone.

Legacy ledgers may have `deliberate_skip` in an awareness column. Preserve it
as a historical combined value and infer its disposition for reading only. Do
not rewrite old rows unless the owner explicitly requests a schema migration.

## Existing Ledger Schema Adapter

The canonical report shape does not authorize changing an established ledger
table. On every update:

1. Preserve existing columns, order, language, enum style, and untouched rows.
2. Write `Priority` and `Confidence` to the report. Add them to the ledger only
   when semantically equivalent columns already exist. A local severity/risk
   column is NOT automatically equivalent to priority, and must not receive
   `now/next/later/watch` values by guesswork.
3. If an awareness-equivalent column exists (`Awareness`, `인지 분류`, or a
   clear local equivalent), write the canonical English awareness value only
   for touched rows. Do not add an awareness column automatically.
4. Map disposition to the ledger's existing Status/Decision column using its
   local values and style. Keep a deliberate skip in the project's skip section
   or established decision representation with reason and trigger.
5. If no semantic destination exists, retain the value in the report and Audit
   Log/decision note rather than creating a new column.
6. New columns, mass normalization, and whole-ledger migration require a
   separate owner decision. Never perform them as a side effect of an audit or
   awareness reply.

Security substate such as current-tree/history/provider/downstream secret
closure belongs in an existing finding, next-check, decision-note, or Audit
Evidence field. It never authorizes four new columns. Keep the overall finding
open until every applicable substate is evidenced or explicitly dispositioned.

For a new ledger created from this skill's template, use the template schema.
For an existing localized ledger, local structure wins. This adapter applies to
normal, focus, post-implementation, and ledger-triage runs.

## Keep The Ledger Compact

A ledger that only grows becomes another hidden document - the exact
problem it exists to solve. Target state: the main findings table holds
only items that still need attention (`pending`, `accepted`, `deferred`).

- Same-session remediation: when a finding is fixed while the session is
  still open, set it to `resolved` with the date before finishing. The
  final report and the ledger must not disagree.
- Temporary ledger-triage decision boards are not ledger history. They live
  under `.blindspot-tmp/ledger-triage-*`, are validated before applying
  decisions, and are deleted after the ledger has the final result. Do not
  route, commit, or cite the HTML board as the durable artifact.
- Cheap checks during triage are evidence for a recommendation, not
  permission to close or downgrade a row. `accepted`, `deferred`,
  `resolved`, `rejected`, archive moves, and awareness rewrites require an
  owner choice first.
- Compress, do not delete: move `resolved` and `rejected` rows out of the
  findings table into a "Resolved archive" section, one line each
  (`ID - title - resolved <date>: <one-line resolution>`). Keep the reason
  on `rejected` items so future runs do not rediscover them as new.
- IDs stay permanent even in the archive; never renumber.
- "Checked and well covered" and "Skipped for now" sections are replaced
  in place on each run (date the section), not accumulated.
- If the archive itself grows long, squash lines older than the last few
  runs into a single count line - the full trail remains in version
  control, the ledger only needs what future runs must not re-report.

Use these diff labels in the audit report:

- `new`
- `changed`
- `confirmed`
- `downgraded`
- `resolved`
- `needs-decision`
