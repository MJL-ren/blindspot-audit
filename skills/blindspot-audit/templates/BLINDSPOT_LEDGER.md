---
status: active
lifecycle_class: ledger
canonical_owner: <path/to/BLINDSPOT_LEDGER.md>
review_trigger: "blindspot audit rerun, release readiness change, major architecture/workflow change, or user decision on an open item"
---

# Blindspot Audit Ledger

This ledger keeps recurring blindspot audit findings, decisions, and
follow-up checks from disappearing between sessions. Once a blind spot is
recorded here it stays visible to every future session, and future audits
diff against this file instead of re-reporting.

Write the prose sections in the project owner's language; keep IDs, status,
and awareness values in English so runs stay diffable.

## Operating Rules

- Read this ledger before each new blindspot audit.
- Verify stale or high-impact items against current project evidence before repeating them.
- Add new or changed findings only; do not duplicate unchanged pending items.
- Record decisions as `pending`, `accepted`, `deferred`, `rejected`, or `resolved`.
- Record owner awareness as `unknown_unknown`, `unknown_known`, `deliberate_skip`, or `unconfirmed`.
- Keep rejected/deferred items with the reason so future audits do not rediscover them as new.
- Keep the Findings table for open items only; move `resolved`/`rejected` rows to the Resolved Archive as one-liners (IDs never renumber).

## Audit Log

| Date | Host | Mode | Scope | Notes |
| --- | --- | --- | --- | --- |
| <YYYY-MM-DD> | <Claude Code/Codex/OpenCode/CLI/chat> | <quick/deep/interview/planning/post-implementation> | <project/path or boundary> | <inspected surfaces, web scan yes/no, limits> |

## Findings

| ID | Finding | Priority | Awareness | Status | Next check / owner |
| --- | --- | --- | --- | --- | --- |
| BS-YYYYMMDD-01 | <what may be missing + concrete consequence + evidence pointer> | now/next/later/watch | unknown_unknown/unknown_known/deliberate_skip/unconfirmed | pending | <cheapest next check> |

## Resolved Archive

One line per closed item, moved here from Findings. Keep the ID and the
reason; squash lines older than the last few runs into a count line if this
section grows long.

- BS-YYYYMMDD-NN - <title> - resolved <date>: <one-line resolution>

## Checked And Well Covered (as of <date>)

- <what exists and is healthy, with evidence paths - prevents future audits from rescanning settled ground>

## Skipped For Now (with re-check triggers)

- <item> - <reason> - re-check when: <trigger>

## Decision Packet

Use this section when the host could not ask an interactive choice or when
the decision should happen later.

| ID | Decision | Recommended option | Options | Why it matters | Status |
| --- | --- | --- | --- | --- | --- |
| DP-YYYYMMDD-01 | <decision title> | <option> | <option A / option B / option C> | <what changes> | pending |
