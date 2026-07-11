# Security Batch: <plain title>

Status: deferred
Source audit: <date, scope, host>
Owner decision: <owner's batch/defer wording>
Ledger: <path>
Visibility: unconfirmed
Detail policy: generalized

This is a lightweight restart document for security findings the owner chose
to handle together. Keep it while the batch is open. After all work and checks
finish, update the ledger and delete or archive this file according to the
project's normal plan lifecycle.

Set visibility before adding detail:

- `private` may use `full` detail, but still never includes secret values,
  private payloads, or unnecessary account/resource identifiers.
- `public-safe` uses `generalized` detail and omits exploitable paths, payloads,
  credential names, provider identifiers, and unpatched attack recipes.
- `unconfirmed` defaults to `generalized`. Keep any needed private location or
  fuller record as `owner-confirm-needed`; do not guess that the destination is
  private.
- `public-safe` and `unconfirmed` use repository-relative paths only. Do not
  include drive letters, home folders, UNC paths, `file://` links, or usernames.

## Start Here

Read the ledger rows listed below, then verify that their evidence and affected
surfaces have not changed. Do not rerun a full blindspot audit unless the owner
asks for one.

## Included Findings

| ID | Everyday consequence | Target surface/copies | Current disposition | Depends on |
| --- | --- | --- | --- | --- |
| <BS-ID> | <what can happen> | <files/services/lineage rows> | deferred | <decision or none> |

## Execution Order

1. <contain or close the highest-impact exposed boundary>
2. <update shared dependency or enforcement point across affected copies>
3. <finish lower-risk hardening and documentation>

## Decisions Needed First

- <decision, owner, options, and default if already chosen>

## Verification Matrix

Each row contains exactly one check, one verification tier, and only the
evidence channel needed for that check. When one finding needs repository and
provider verification, repeat its ID on separate rows. Never write combined
values such as `static-only + authorized-dynamic` in one row.
Keep the machine-readable headers `Finding`, `Verification tier`, and
`Evidence channel` exactly in English. All descriptions and results may use the
owner's language.

| Finding | Check | Verification tier | Evidence channel | Pass condition | Result |
| --- | --- | --- | --- | --- | --- |
| <BS-ID> | <one smallest closing check> | <one tier only> | <one channel only> | <observable result> | pending |

## Done When

- Every included ID has a copy-specific or boundary-specific verification
  result.
- Provider/runtime unknowns are confirmed or remain explicitly open with an
  owner and trigger.
- The ledger records the owner choice, implementation result, and final
  disposition without copying this whole plan.
- This batch file is deleted or archived after its restart value is gone.

## Next Session Start

Continue the security batch in `<path>`. Read `<ledger path>` and the included
IDs first, then execute the next unchecked step and update the verification
matrix. Do not open a new audit or change unrelated ledger rows.
