# Ledger Triage HTML Decision Board

Read this reference only when `ledger-triage.md` routes a file-writing host to
the HTML fallback, or when an owner on a choice-capable host explicitly selects
the one-page board. Do not load it merely because `mode: ledger-triage` is
active.

## Contents

- Board boundary
- Draft and review
- Create and serve
- Collect and validate
- Board input shape
- Response and application workflow
- Cleanup

## Board Boundary

The board collects owner choices. It never authorizes the agent to choose an
outcome and the helper never edits `BLINDSPOT_LEDGER.md`.

- Put it under `<project-root>/.blindspot-tmp/ledger-triage-*`, never in docs or
  commit scope.
- Do not write a status, archive move, awareness change, or Audit Log result
  before the response validates.
- Recommendations are visible suggestions, not pre-approved decisions.
- Omitted response rows mean "leave unchanged".
- Keep every title, explanation, option, and tradeoff understandable without
  opening the ledger.

## 1. Draft And Review

Draft a scaffold from the existing ledger instead of retyping every row:

```text
python "<skill>/scripts/ledger_triage_board.py" draft --project-root "<project-root>" --ledger "<ledger-path>" --out "<triage-input.json>" --language "<owner-language>"
```

The draft parser accepts English and localized ledger tables, including Korean
headings such as `발견 항목`, `결정 묶음`, and `감사 이력`, and columns such as
`결정`, `인지 분류`, and `후속 제안`. If a localized table still fails, use its
`BS-...` or `DP-...` ID rows as the fallback source rather than reconstructing
items from memory.

Draft output is a scaffold, not owner-ready text:

- It carries `draftOnly: true` and internal `_draftReview` hashes.
- Rewrite every generated `plainExplanation`, `whyItMatters`, and group summary.
- Review recommendations, options, `executionKind`, and implementation hints.
- Keep `_draftReview` while editing; it lets `create` detect unchanged generic
  text. Remove `draftOnly` only after review.
- Existing closure wording may support a `resolved_candidate` recommendation,
  but owner-supplied proof still needs a note when applicable.

Add `--include-ledger-hygiene` to `draft` when summaries such as Checked And
Well Covered, Audit Log, version, test count, or latest release may be stale.
Those become internal `ledger_section` candidates with
`executionKind: cheap_verification`; verify the current facts before presenting
them.

## 2. Create And Serve

Create the board and start its localhost server:

```text
python "<skill>/scripts/ledger_triage_board.py" create --project-root "<project-root>" --ledger "<ledger-path>" --data "<triage-input.json>" --serve --write-url "<url-file>" --write-board-dir "<board-dir-file>"
```

`create --serve` runs in the foreground. Use the host's background-process
support when the session must continue, then read `--write-url` and
`--write-board-dir`. Add `--write-pid` only for diagnostics.

`create` rejects an unreviewed draft. For explicit tests or debugging only,
append `--allow-unreviewed-draft` to the **create** command. Never use that flag
to skip owner-facing review in a real run.

If the board was created without `--serve`, start it separately:

```text
python "<skill>/scripts/ledger_triage_board.py" serve --board-dir "<board-dir>" --write-url "<url-file>" --write-board-dir "<board-dir-file>" --write-pid "<pid-file>"
```

The server binds to localhost and writes `server-state.json`. Cleanup uses its
board ID, directory, URL, and shutdown token; it never kills an arbitrary PID.

If localhost is impossible, open the self-contained HTML as a static file. The
browser downloads a response JSON. Do not ask the owner to inspect or rewrite
that JSON.

## 3. Collect And Validate

After the owner says the response is ready, validate the server-saved file:

```text
python "<skill>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>"
```

For a downloaded response, use one explicit path or collect matching files:

```text
python "<skill>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --response "<downloaded-response-json>"
python "<skill>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --collect-response --response-dir "<downloads-or-other-folder>"
python "<skill>/scripts/ledger_triage_board.py" collect-response --board-dir "<board-dir>" --from "<downloads-or-other-folder>"
```

`--collect-response` verifies board ID, ledger path, and ledger hash, chooses the
newest `completedAt` when duplicates match, copies it into the board directory,
then validates normally. Cowork does not mount the owner's Downloads; use a
mounted response path and explicit `validate --response` there instead of the
default `--collect-response` Downloads scan, as required by `host-surfaces.md`.

Validation prints one workflow:

- `reexplain_first`
- `apply_directly`
- `temporary_plan_required`

It also summarizes action, option, execution kind, bucket, canonical status,
intent detail, and owner-note presence. Treat owner notes on implementation,
external confirmation, and owner follow-up items as execution constraints.

Generate temporary ledger wording suggestions without editing the ledger:

```text
python "<skill>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --write-ledger-suggestions
```

When validation requires implementation work, generate the temporary plan:

```text
python "<skill>/scripts/ledger_triage_board.py" validate --board-dir "<board-dir>" --write-plan
```

Both files stay inside the board directory and disappear during cleanup.

## Board Input Shape

The reviewed JSON passed to `create` follows this shape:

```json
{
  "schema": "blindspot-triage-board.v1",
  "boardId": "ledger-triage-YYYYMMDD-01",
  "createdAt": "<ISO-8601>",
  "language": "<owner-language>",
  "projectName": "<project>",
  "groups": [
    {
      "groupId": "release-decisions",
      "category": "decision_bundle",
      "title": "Public release decisions",
      "plainSummary": "These rows depend on what public release means.",
      "recommendedAction": "defer",
      "items": [
        {
          "ledgerId": "BS-YYYYMMDD-01",
          "shortTitle": "Release means two different things",
          "ledgerSection": "Findings",
          "ledgerSummary": "One label covers internal activation and public launch.",
          "plainExplanation": "The project treats two different milestones as one.",
          "whyItMatters": "A later session may close the wrong release gate.",
          "decisionQuestion": "Should this stay open until the public release plan exists?",
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
              "tradeoff": "Keeps the row visible until that plan opens.",
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

The helper fills or verifies `projectRoot`, `ledgerPath`, and `ledgerHash` at
create time.

Optional internal `itemType` values are `ledger_row` (default) and
`ledger_section`. Never expose that label to the owner.

Allowed `executionKind` values:

- `ledger_only`
- `cheap_verification`
- `implementation_plan`
- `external_confirmation`
- `owner_followup`

Set `implementationHint` for `implementation_plan`. Put canonical `status` and
free-form `intentDetail` on each option, not on the item. Allowed statuses are
`pending`, `accepted`, `deferred`, `rejected`, `resolved`, or empty.
`keep_pending` and `needs_reexplain` always submit empty status and intent.

Give options sharing one action distinct `optionId` values. The response carries
`action`, `optionId`, `status`, and `intentDetail`, preventing one accept path
from being mistaken for another. Older `statusIntent` remains compatibility
input only.

For `resolved_candidate`, set `noteRequired: true` only when owner evidence is
actually required, such as secret rotation, provider/account state, or an
external legal/platform check. Validation checks only for non-whitespace text;
it never keyword-parses the owner's language.

Secret-related closure needs separate current-tree, Git-history/artifact,
provider, and downstream checks. Do not close merely because the current file
looks clean.

## Response And Application Workflow

The helper validates `blindspot-triage-response.v1`. Only then may the agent
apply selected decisions. Omitted rows remain unchanged.

1. If any action is `needs_reexplain`, explain those first. Preserve the other
   choices in the validated response; do not apply or clean up yet.
2. If all choices are ledger-only maintenance, apply them after required cheap
   verification.
3. If any choice requires implementation or multi-step work, create or complete
   `<board-dir>/ledger-triage-application-plan.md` before editing project files.
4. If work is blocked by owner, provider, legal, payment, or platform state,
   record the blocker and re-check trigger in the ledger instead of pretending
   completion.
5. Delete the temporary plan after completion or durable blocker recording.

The temporary plan includes board ID, selected ledger IDs, owner choices, work
buckets, expected files/areas, ordered steps, stop conditions, verification,
intended ledger result, and cleanup checklist. Ledger-only context must not get
fake file-edit tasks.

Action meanings:

- `accept`: track or execute the accepted next step.
- `defer`: retain with owner reason or trigger.
- `resolved_candidate`: verify cheaply, then archive; if verification is not
  possible, leave open and record the blocker.
- `reject`: archive with the owner reason.
- `keep_pending`: leave open, optionally improving the next check.
- `needs_reexplain`: keep status unchanged and explain more plainly.

The durable ledger records selected choices, actual changes, verification,
remaining blockers, and cleanup. Add one `mode: ledger-triage` Audit Log row
with board ID, applied decision count, temporary-plan lifecycle, and cleanup
result. Preserve local columns and wording.

## Cleanup

Run cleanup only after every selected decision was applied or safely recorded:

```text
python "<skill>/scripts/ledger_triage_board.py" cleanup --board-dir "<board-dir>" --confirm-applied
```

Cleanup shuts down only the matching token-authenticated local server, deletes
the board, response, suggestions, and temporary plan, and prints an Audit Log
suggestion. Adapt that suggestion to the ledger's existing schema. The board is
temporary workflow state, never durable history.
