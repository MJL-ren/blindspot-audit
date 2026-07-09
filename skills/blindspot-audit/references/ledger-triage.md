# Ledger Triage

Use this reference for `mode: ledger-triage`: a post-audit maintenance mode
that turns a growing `BLINDSPOT_LEDGER.md` into a small set of owner
decisions and safe cleanup actions. It is not a new blindspot audit.

## Purpose

Ledger triage exists because a good ledger can still become too heavy for
the owner to act on. The mode reads existing findings, decision packets,
skipped items, and archives, then groups them by the kind of action needed.
It should reduce cognitive load, not discover more work.

The mode succeeds when the owner can handle many ledger rows in one pass:
approve easy cleanup, make a few bundled decisions, ask for simpler
explanations where needed, and leave only the real unresolved choices open.

## Consent Gate

Ledger triage is a decision collection workflow. It is NOT permission for
the agent to decide outcomes.

Do not interpret requests like "clean up the ledger", "organize the ledger",
"proceed with ledger decisions", or localized equivalents as permission to
mark rows `accepted`, `deferred`, `resolved`, `rejected`, move rows to the
archive, rewrite awareness values, or close decision-packet items.

The agent may inspect, group, run cheap read-only checks, and recommend an
action. It must not apply a ledger decision until one of these exists:

- a structured choice-tool answer from the owner.
- a validated `blindspot-triage-response.json` from the HTML decision board.
- an explicit owner reply that names the row or option to apply.

If there is no owner response yet, the correct end state is "decision board
created" or "decision packet waiting", with the ledger unchanged except for
temporary-board files outside docs. This protects users who want to approve
every AI-recommended decision, even small cleanup.

## Mode Boundary

- Do not run the normal fresh-eyes scan.
- Do not create new blindspot findings unless the ledger itself is broken
  in a way that blocks triage (for example, unreadable rows or no stable
  IDs). Report those as triage blockers, not project findings.
- Do not make implementation changes to the target project.
- Do not mass-normalize local status language. Preserve the ledger's
  existing style and only update rows the owner selected.
- Do not treat `safe_accept`, `quick_cleanup`, or a cheap verification as
  authorization. They mean "safe to recommend to the owner", not "safe for
  the agent to apply."
- Do not delete the ledger's history. Compress resolved/rejected rows per
  `ledger-lifecycle.md`.

## Inputs To Read

Read the existing ledger first, including:

- `Project Context`
- `Audit Log`
- open `Findings`
- `Resolved Archive`
- `Skipped For Now`
- `Decision Packet`

Then, when a row looks stale or likely resolved, do the cheapest
repo-local verification needed to avoid applying a wrong cleanup. Do not
run builds, tests, network scans, or expensive checks only for triage; put
those in the decision board as owner-confirmation or next checks.

## Triage Categories

Use these categories in the decision board or structured-choice prompts:

- `quick_cleanup`: already resolved, duplicated, rejected, or stale enough
  to archive after a cheap verification.
- `safe_accept`: low-risk tracking or documentation follow-up that the
  owner can approve with one click.
- `decision_bundle`: several rows depend on one product, operations,
  release, or positioning decision.
- `needs_owner_detail`: the right action depends on the owner's preference,
  audience, budget, timing, or appetite for scope.
- `needs_external_confirmation`: legal, tax, security, payment, platform,
  provider, or regulation items that need a primary source or professional
  confirmation before the ledger can close them.
- `needs_reexplain`: the item is too unfamiliar or jargon-heavy for the
  owner to classify confidently.

Each group names the recommended action, but the owner must be able to pick
a different option without rewriting prose by hand.

## Plain-Language Requirement

Rows marked `unknown_unknown`, `unconfirmed`, localized equivalents such as
`미확인`, or anything in the owner's weak domain need a beginner explanation.
Include:

- what the ledger row actually says, summarized in the owner's language so
  the owner does not need to open `BLINDSPOT_LEDGER.md` beside the board.
- what it means, in everyday words.
- why it matters for this project.
- what the owner can choose.
- which choice is recommended and why.

Do not use internal labels as user-facing explanations. "Resolved
candidate" means nothing to a beginner; say "this looks already fixed, but
I need one quick confirmation before archiving it."

The HTML board must make each item understandable on its own. Use
`ledgerLocation` or `ledgerSection` for source position, `ledgerSummary`
for the actual row content, `plainExplanation` for what the item means,
`whyItMatters` for why it matters, and `decisionQuestion` for the choice
the owner is making. Do not label the explanation "beginner explanation"
or "explain like I am new"; just write it plainly.

Keep metadata out of the readable content. Do not write `ledgerSummary` as
"Findings has ... as BS-123 pending" or localized equivalents such as
"Findings에는 ... BS-123이 pending으로 남아 있습니다." Put the source in
`ledgerLocation`/`ledgerSection`; put only the issue or decision itself in
`ledgerSummary`.

Choice options also need plain tradeoffs. A good option says both what will
happen and what will stay unchanged. Avoid showing raw enum labels such as
`accepted`, `resolved_candidate`, `pending`, or `unknown_unknown` as the
main user-facing text when the owner's language is not English.

Write for a non-specialist owner, roughly middle-school reading level in
the owner's language. Avoid unexplained shorthand and imported terms in
visible text. For example, prefer "purchase/contact button" over "CTA";
"send the form without leaving the page" over "AJAX"; "screen-reader
description" over "ARIA"; and "movement-reduction setting" over
`prefers-reduced-motion`.

## Host Behavior

Prefer the host's native decision UI in this precedence order: a structured
choice tool first (Cowork and Claude Code both have one - it is the
least-effort surface for the owner); then, on a file-writing host with no
choice tool, the HTML decision board; then a numbered reply for
read-only/chat-only hosts or when the owner asked for no temporary files.
The board is a fallback, not the default on hosts that can ask directly.

### Structured Choice Hosts

Use the host's choice tool (for example `AskUserQuestion`) for decisions
before editing the ledger. Triage is bundle-first, not row-first: group the
ledger before asking, so the host's small per-question option cap (Cowork
and Claude Code cap at 4 options plus a built-in "Other") rarely bites. Good
grouping collapses a 20-row ledger into roughly 4-7 questions - one or two
question rounds - not 20.

- `quick_cleanup` and `safe_accept`: one multiSelect question each -
  "Which of these should I apply? (recommended: all)", one option per row,
  the owner unchecks any to skip. Many rows become one question.
- `decision_bundle`: one single-select question per bundle, since the rows
  share one decision. Recommended action first, then 1-2 alternatives.
- `needs_owner_detail`: one question per row, but there are usually few.
  Recommended action first plus 1-2 alternatives; "I don't understand this
  one" arrives through the built-in Other path and becomes `needs_reexplain`.
- `needs_external_confirmation`: one multiSelect - "OK to mark these as
  waiting on outside confirmation?"
- `needs_reexplain`: not a question. Re-explain in chat, leave awareness
  `unconfirmed`.

Per row you never need all six actions as options: show the recommended
action first, 1-2 alternatives, and let Other carry the rest. When a single
group still exceeds the option cap, split it across question rounds rather
than dropping the overflow, and run rounds in priority order (blocking or
highest-impact decisions first).

If, after grouping, there are still more independent decisions than a couple
of rounds can hold comfortably, do not silently drop any and do not switch
to a board on your own. Ask the owner: "there are a lot of separate
decisions here - keep going in batches, or should I build a one-page board
you fill in at once?" Only build a board on a choice-capable host if the
owner chooses it.

Record choices in the ledger's audit log and update only selected rows after
the owner answers.

### No-Choice File-Writing Hosts

This is the fallback for surfaces with no structured choice tool (for
example Codex); on a host that has a choice tool, use the section above
instead. When the host can write files but cannot present a structured
choice UI, create an HTML decision board with
`scripts/ledger_triage_board.py` whenever there is any meaningful ledger
decision to apply. Use the board even for small "obvious" cleanup unless the
owner explicitly asked for chat-only or read-only output.

Default flow:

1. Prepare a board input JSON from the grouped triage results. To avoid
   writing it from scratch, draft a scaffold from the ledger first:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" draft --project-root "<project-root>" --ledger "<ledger-path>" --out "<triage-input.json>" --language "<owner-language>"
```

   The draft is only a scaffold. Review and rewrite plain explanations,
   recommendations, options, `executionKind`, and any implementation hints
   before creating the board. Draft output is marked `draftOnly: true`, and
   `create` refuses it until that marker is removed after review. Use
   `--allow-unreviewed-draft` only for explicit tests or debugging.
   The draft parser accepts English and localized ledger tables, including
   Korean headings such as `발견 항목`, `결정 묶음`, and `감사 이력`, and
   Korean columns such as `결정`, `인지 분류`, and `후속 제안`. If a
   localized ledger still fails to draft, fall back to ID-pattern table rows
   (`BS-...` / `DP-...`) rather than writing every item from memory. When
   the ledger text or follow-up says the owner already confirmed closure
   (`닫아도 됨`, `신경 안 써도 됨`, similar wording), the draft may recommend
   `resolved_candidate`; require a short evidence note only when that
   option needs owner proof, such as a token revocation or account setting
   confirmation.
   Add `--include-ledger-hygiene` when the ledger has summary sections that
   may be stale, such as `Checked And Well Covered`, `Audit Log`, version
   summaries, test counts, or Latest release notes. Those become internal
   `ledger_section` maintenance candidates with `executionKind` set to
   `cheap_verification`. Review current manifests, tests, and release state
   before presenting them to the owner.
2. Run:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" create --project-root "<project-root>" --ledger "<ledger-path>" --data "<triage-input.json>" --serve --write-url "<url-file>" --write-board-dir "<board-dir-file>"
```

   `create --serve` makes the board and starts the localhost server in the
   foreground. Use the host's background process support when the session
   needs to keep working, then read `--write-url` and `--write-board-dir`.
   Add `--write-pid` when the host needs to record the server process id for
   diagnostics only.

3. If the board was already created without `--serve`, serve it on localhost
   when the host allows it. This is the default because the owner should be
   done after pressing submit; the response writes directly into the board
   directory.

```text
python "<skill-folder>/scripts/ledger_triage_board.py" serve --board-dir "<board-dir>" --write-url "<url-file>" --write-board-dir "<board-dir-file>" --write-pid "<pid-file>"
```

   If localhost serving is impossible, the same HTML still works as a
   static file. In that fallback the browser downloads a response JSON.
   Do not ask the owner to move it by hand; collect it with the helper.
   `serve` writes `server-state.json` in the board directory. Cleanup uses
   that file's board id, board dir, localhost URL, and shutdown token to stop
   only the matching board server; it does not kill an arbitrary PID.

4. After the owner says the response is ready, run:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>"
```

   If the response was downloaded instead of server-saved, use one of:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --collect-response
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --collect-response --response-dir "<downloads-or-other-folder>"
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --response "<downloaded-response-json>"
```

   `--collect-response` searches for matching
   `blindspot-triage-response*.json` files, verifies board id, ledger path,
   and ledger hash, chooses the newest `completedAt` when multiple matching
   downloads exist, copies the chosen file into the board directory as
   `blindspot-triage-response.json`, then runs normal validation. The
   separate helper command is available for the same collection step:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" collect-response --board-dir "<board-dir>" --from "<downloads-or-other-folder>"
```

`validate` also prints the recommended next workflow:
`reexplain_first`, `apply_directly`, or `temporary_plan_required`. It also
summarizes each selected decision with action, execution kind, bucket,
canonical status, intent detail, and whether an owner note is present.
Treat owner notes on
implementation, external-confirmation, or owner-followup items as execution
constraints.

For ledger editing support without letting the helper edit the ledger, ask
for temporary suggestions:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --write-ledger-suggestions
```

The helper writes `<board-dir>/ledger-triage-ledger-suggestions.md` with
selected-row wording hints and an Audit Log draft. It is a temporary work
file and disappears with the board directory during cleanup.

When validate reports implementation work, ask the helper for a temporary
plan scaffold instead of writing it from scratch:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --write-plan
```

The helper writes `<board-dir>/ledger-triage-application-plan.md`. Edit and
execute that plan, then delete it after the durable ledger result is
recorded.

5. Route the validated response through the post-response workflow below.
6. Apply decisions, implementation work, or re-explanations according to
   that workflow.
7. Run cleanup only after all selected decisions have been handled or
   safely recorded:

```text
python "<skill-folder>/scripts/ledger_triage_board.py" cleanup --board-dir "<board-dir>" --confirm-applied
```

The board directory lives under `<project-root>/.blindspot-tmp/`. It is a
temporary workspace artifact, not documentation, and must not be committed.
If `server-state.json` exists, `cleanup --confirm-applied` shuts down the
matching localhost server through its token endpoint before deleting the
directory.

Do not write an Audit Log row, status change, archive move, or triage note
before validation. The board itself is the pre-decision artifact.

### Small Or Read-Only Runs

If the host cannot write files, or the owner explicitly asks for no
temporary HTML files, use a compact numbered reply format instead of HTML.
Keep the final answer short and include exact reply examples. Do not edit
the ledger until the owner replies.

## Board Input Shape

The agent prepares this JSON and passes it to the helper:

```json
{
  "schema": "blindspot-triage-board.v1",
  "boardId": "ledger-triage-20260708-01",
  "createdAt": "2026-07-08T00:00:00+00:00",
  "language": "ko",
  "projectName": "Example",
  "groups": [
    {
      "groupId": "release-decisions",
      "category": "decision_bundle",
      "title": "Public release decisions",
      "plainSummary": "These rows all depend on what 'public release' means.",
      "recommendedAction": "defer",
      "items": [
        {
          "ledgerId": "BS-20260708-01",
          "shortTitle": "Release means two different things",
          "ledgerSection": "Findings",
          "ledgerSummary": "The project uses one release label for both internal activation and public launch.",
          "plainExplanation": "The ledger uses one release label for both internal activation and public launch.",
          "whyItMatters": "Future agents may close the wrong gate if this stays blurry.",
          "decisionQuestion": "Should this stay open until the public release plan is written?",
          "currentStatus": "pending",
          "currentAwareness": "unconfirmed",
          "recommendedAction": "defer",
          "executionKind": "ledger_only",
          "implementationHint": "",
          "options": [
            {
              "optionId": "defer-public-release-plan",
              "action": "defer",
              "label": "Decide later with a release plan",
              "tradeoff": "Keeps the row visible until the public release plan opens.",
              "status": "deferred",
              "intentDetail": "public_release_plan",
              "recommended": true
            }
          ]
        }
      ]
    }
  ]
}
```

`projectRoot`, `ledgerPath`, and `ledgerHash` are filled or verified by the
helper at create time.

Items may include optional internal `itemType`: `ledger_row` (default) or
`ledger_section`. Use `ledger_section` only for agent maintenance work on
ledger sections themselves, such as stale summary wording, version notes,
test-count summaries, or release notes. Do not expose `itemType` as a
user-facing label; the owner should see plain titles such as "refresh the
ledger summary after checking the current version."

Use `executionKind` to describe what happens if the owner accepts the
recommendation:

- `ledger_only`: only ledger status, archive, wording, or next-check updates.
- `cheap_verification`: read-only verification before ledger cleanup.
- `implementation_plan`: code, docs, config, runbook, UI, data, or multi-step
  project work is expected; a temporary execution plan is required.
- `external_confirmation`: provider, legal, payment, platform, account, or
  professional confirmation is needed before closure.
- `owner_followup`: another owner preference/detail is needed before work can
  be executed.

Set `implementationHint` when `executionKind` is `implementation_plan` so the
later temporary plan starts from the right work surface. Keep it short and
owner-facing.

Put canonical `status` and free-form `intentDetail` on the specific option
that should carry them, not on the item as a general default. Allowed
status values are `pending`, `accepted`, `deferred`, `rejected`,
`resolved`, or empty. Use `intentDetail` for details such as
`korea_included`, `minimum_privacy_notice`, or `secret-cleanup`. Older
`statusIntent` inputs are accepted only as a compatibility path and split
into `status` + `intentDetail` when possible. `keep_pending` and
`needs_reexplain` must always submit empty `status` and `intentDetail`.
Validation fails if a response action carries the wrong status/detail pair
for the selected option. When two options share the same action, give each
one a distinct `optionId`; the response carries `action`, `optionId`,
`status`, and `intentDetail` so `accept` option A cannot be confused with
`accept` option B.

For `resolved_candidate`, require an owner note only when owner evidence is
actually needed. Set option-level `noteRequired: true` for secret/token
revocation, provider/account checks, legal/platform confirmation, or any
case where the owner must supply proof. Leave it omitted or false for
ledger-only duplicate cleanup or cheap repo-local verification that the
applying agent can perform after validation.
When a note is required, validation checks only that the note is non-empty
after trimming whitespace. Do not parse the note for keywords such as
"confirmed", "revoked", or localized equivalents; users may answer in any
language, and meaning belongs to the applying agent's review step, not the
submit gate.

For secret, token, API key, PAT, credential, or private-key findings, do not
close on "current file looks fixed" alone. The helper adds a secret
checklist to board data and temporary plans: scan the current working tree,
scan Git history or old commits, and leave the row open or blocked if
rotation/history cleanup is not confirmed.

## Response Interpretation

The helper validates `blindspot-triage-response.json`; only then may the
agent apply it. Treat response actions as owner choices, not agent
judgment.

The response may include only selected rows. Rows omitted from `decisions[]`
are not errors; they mean "do not touch this row yet." Leave omitted rows
unchanged and do not count them as applied decisions.

### Post-Response Workflow

After validation, classify selected decisions before touching the ledger.
The owner already made choices; this step decides how to execute those
choices safely.

1. If any selected decision has action `needs_reexplain`, handle those
   first. Do not apply the other selected decisions yet, do not cleanup the
   board directory, and do not edit the ledger except for an owner-requested
   clarification note. The other selected choices remain saved in the
   validated response JSON. Explain the unclear items in simpler words and
   wait for the owner to either update the board or say to continue with the
   saved choices.
2. If all selected decisions are simple ledger maintenance, apply them
   directly after any required cheap verification. Simple work means status
   changes, archive moves, clearer next-check wording, rejected/skipped
   records, or recording an external-confirmation wait state. It does not
   touch project implementation files.
3. If any selected decision requires implementation or multi-step work
   outside the ledger, create a temporary execution plan before changing
   implementation files. Use the board directory:
   `<board-dir>/ledger-triage-application-plan.md`. The plan is a temporary
   work surface, not project documentation and not commit scope.

The temporary execution plan must include:

- board id and selected ledger IDs.
- the owner choices being executed.
- work buckets: ledger-only, cheap verification, implementation,
  external/owner blocked.
- files or project areas expected to change.
- ordered steps, stop conditions, and verification.
- the exact ledger result to record after the work.
- cleanup checklist for the temporary plan and board directory.

After implementation is complete, delete the temporary plan. Preserve the
durable result only in `BLINDSPOT_LEDGER.md`: selected choices, actual
changes made, verification outcome, unresolved blockers, and cleanup result.
Ledger-only choices may appear in the temporary plan for context, but they
must be labeled as ledger-only and should not get fake file-edit TODOs.
If implementation is blocked by missing account access, provider/legal
confirmation, or owner detail, delete the temporary plan after recording the
blocker and next trigger in the ledger. Do not leave temporary planning files
behind unless the owner explicitly asks to keep them.

### Action Meanings

Allowed actions:

- `accept`: mark accepted, document the approved next step, or execute the
  accepted implementation through the workflow above.
- `defer`: mark deferred with the owner's reason or trigger.
- `resolved_candidate`: verify cheaply, then move to `Resolved Archive`;
  if verification is not possible, leave pending and record the note. The
  HTML board blocks submission only when the selected option needs owner
  proof, such as secret rotation, account settings, legal/platform checks,
  or another external confirmation.
- `reject`: move to rejected/archive with the reason.
- `keep_pending`: leave open, optionally improving the next-check wording.
- `needs_reexplain`: do not change the ledger status; answer the owner in
  simpler words and keep awareness `unconfirmed`.

After applying decisions, add an `Audit Log` row for `mode: ledger-triage`
with board id, number of decisions applied, whether temporary files were
cleaned up, and whether a temporary execution plan was created and deleted.
The helper's `cleanup --confirm-applied` prints an Audit Log suggestion;
adapt that line to the ledger's local wording instead of inventing it from
memory. For localized boards, the helper may print a localized suggestion;
still preserve the ledger's existing table columns and wording.
