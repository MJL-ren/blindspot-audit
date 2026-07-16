# Owner-Response Guard

Load this reference only after an explicit owner reply to a normal, quick,
deep, scoped, planning, post-implementation, or focus audit. `ledger-triage`
uses its own response contract instead. Before this point, the audit delta must
already have passed the pre-interview schema guard in `ledger-lifecycle.md`, and
that pre-delta snapshot must have been deleted with `cleanup --discard`.

Use `scripts/audit_followup_guard.py`. It validates and previews; it never
interprets owner language or edits the ledger.

## 1. Create The Owner-Response Snapshot

Create a **new** snapshot of the current ledger before preparing or applying
the reply:

```text
python "<skill>/scripts/audit_followup_guard.py" snapshot --project-root "<root>" --ledger "<ledger>"
```

The new snapshot contains the audit's `BA-` run and finding IDs. Use only its
printed `ledger-snapshot.json` path for `prepare-awareness`, final validation,
and cleanup. Do not reuse the earlier pre-delta snapshot.

## 2. Map The Reply Without Keyword Parsing

Semantically map the owner's reply into temporary JSON inside the new snapshot
directory. Do NOT use keyword matching or language-specific parsing. Use
`blindspot-owner-response.v1` for individual decisions. Use grouped
`blindspot-owner-response.v2` when several findings share the same awareness,
disposition, reason, trigger, batch, and next action. The helper expands groups
deterministically and rejects duplicate IDs across groups and individual rows.

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

A ledger using exact `ID`, `Awareness`, and `Status` columns needs no adapter.
For a localized or custom schema, add an explicit `applicationMap`; never guess
that a local word means a canonical enum:

```json
{
  "applicationMap": {
    "idColumn": "ID",
    "awarenessColumn": "인지 분류",
    "dispositionColumn": "결정",
    "awarenessValues": {"unknown_unknown": "unknown_unknown"},
    "dispositionValues": {"deferred": "보류"},
    "dispositionMatchModes": {"deferred": "annotated"},
    "destinations": {}
  }
}
```

Match modes default to `exact`. Use `annotated` only when the established local
status appends a date or reason after a clear separator, such as
`보류(2026-07-12: 다음 묶음)`. Standard `ID`/`Awareness`/`Status` ledgers accept
this safe annotated disposition form automatically. Prefix lookalikes such as
`deferredish` never match. Keep awareness matching exact.

`destinations` defaults each decision to `row`. Set an ID to `archive` only for
an explicit `resolved` or `rejected` move. Final validation then confirms that
the open row disappeared while the stable ID remains defined.

## 3. Preview Before Editing

Show the owner-response delta before applying it:

```text
python "<skill>/scripts/audit_followup_guard.py" preview --ledger "<ledger>" --data "<response.json>"
```

A blocking preview catches duplicate or unknown IDs, group conflicts,
unresolved references, conflicting batch paths, unsupported enum values,
missing skip reasons or triggers, owner follow-ups with no next action, and a
missing or invalid custom-ledger adapter. Unmentioned findings stay unchanged.

For one or more findings sharing one explicit awareness-only reply, the helper
can prepare temporary v1 JSON and run the same preview without editing the
ledger. Repeat `--finding` for every included ID:

```text
python "<skill>/scripts/audit_followup_guard.py" prepare-awareness --snapshot "<owner-response-snapshot-file>" --audit-run "<BA-ID>" --finding "<BS-ID-1>" --finding "<BS-ID-2>" --value unknown_known
```

Standard `ID`/`Awareness`/`Status` ledgers need no adapter arguments. For a
localized or custom table, pass the exact `--id-column`, `--awareness-column`,
`--disposition-column`, and final `--ledger-awareness-value`; never translate
them by guessing. Use this shortcut only when every included finding shares
the same awareness and no disposition change. Mixed replies use normal v1/v2
JSON. The command writes inside the snapshot directory and never edits the
ledger.

## 4. Scaffold A Required Security Batch

For 2+ findings deferred to one named security batch, create the mechanical
handoff skeleton from the validated preview before filling judgment fields:

```text
python "<skill>/scripts/audit_followup_guard.py" scaffold-security-batch --project-root "<root>" --ledger "<ledger>" --data "<response.json>" --visibility unconfirmed
```

This command never edits the ledger. It writes the response's repo-relative
`batchPath`, exact verification headers, one placeholder row per finding, and
a ledger-backlink suggestion. Replace placeholders with one check, one tier,
and one evidence channel per row before final validation. `public-safe` and
`unconfirmed` handoffs use generalized detail and reject drive, home, UNC,
`file://`, and other local absolute paths.

## 5. Apply, Validate, And Clean Up

Apply only the previewed delta and create any required durable batch handoff
and ledger backlink. Then run:

```text
python "<skill>/scripts/audit_followup_guard.py" validate --snapshot "<owner-response-snapshot-file>" --ledger "<ledger>" --data "<response.json>"
python "<skill>/scripts/audit_followup_guard.py" cleanup --snapshot "<owner-response-snapshot-file>" --confirm-applied
```

Final validation blocks unauthorized schema drift, removed or duplicate stable
IDs, decisions not written to mapped cells or archive destinations, missing
security batch files/backlinks, unsafe public paths, missing visibility policy,
and verification rows that combine multiple tiers or evidence channels.
`--confirm-applied` works only after successful owner-response validation; the
helper rejects `--discard` in this phase. Its output lists the applied mapping
per finding. Cleanup removes the temporary response with its snapshot.

The `.blindspot-tmp` safety root may remain with its generated `.gitignore` and
no run directories. That marker intentionally keeps future temporary guard
artifacts out of Git; it is not an unfinished response.

If the helper cannot run, perform the same snapshot/header comparison and
owner-visible delta preview manually. Never skip the guard by directly applying
a complex reply.
