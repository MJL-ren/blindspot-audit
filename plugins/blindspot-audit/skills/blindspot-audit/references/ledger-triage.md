# Ledger Triage

Use this reference for `mode: ledger-triage`: a post-audit maintenance mode
that turns a growing `BLINDSPOT_LEDGER.md` into a small set of owner decisions
and safe cleanup actions. It is not a new blindspot audit.

## Purpose

Ledger triage exists because a good ledger can still become too heavy for the
owner to act on. The mode reads existing findings, decision packets, skipped
items, and archives, then groups them by the kind of action needed. It should
reduce cognitive load, not discover more work.

The mode succeeds when the owner can handle many ledger rows in one pass:
approve easy cleanup, make a few bundled decisions, ask for simpler
explanations where needed, and leave only the real unresolved choices open.

## Consent Gate

Ledger triage is a decision collection workflow. It is NOT permission for the
agent to decide outcomes.

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
- Do not create new blindspot findings unless the ledger itself is broken in a
  way that blocks triage, such as unreadable rows or no stable IDs. Report those
  as triage blockers, not project findings.
- Do not make implementation changes to the target project before the owner
  selects an action that explicitly requires implementation.
- Do not mass-normalize local status language. Preserve the ledger's existing
  style and only update rows the owner selected.
- Do not treat `safe_accept`, `quick_cleanup`, or a cheap verification as
  authorization. They mean "safe to recommend", not "safe to apply."
- Do not delete ledger history. Compress resolved/rejected rows per
  `ledger-lifecycle.md`.

## Inputs To Read

Read the existing ledger first, including:

- `Project Context`
- `Audit Log`
- open `Findings`
- `Resolved Archive`
- `Skipped For Now`
- `Decision Packet`

When a row looks stale or likely resolved, do only the cheapest repo-local
verification needed to avoid a wrong recommendation. Do not run builds, tests,
network scans, or expensive checks merely for triage; present them as owner
confirmation or next checks.

## Triage Categories

Use these categories in structured questions or a decision board:

- `quick_cleanup`: already resolved, duplicated, rejected, or stale enough to
  archive after a cheap verification.
- `safe_accept`: low-risk tracking or documentation follow-up the owner can
  approve with one action.
- `decision_bundle`: several rows depend on one product, operations, release,
  or positioning decision.
- `needs_owner_detail`: the right action depends on owner preference, audience,
  budget, timing, or appetite for scope.
- `needs_external_confirmation`: legal, tax, security, payment, platform,
  provider, or regulation items that need authoritative confirmation.
- `needs_reexplain`: the item is too unfamiliar or jargon-heavy for the owner
  to classify confidently.

Each group names the recommended action, but the owner must be able to choose a
different option without rewriting prose by hand.

## Plain-Language Requirement

Rows marked `unknown_unknown`, `unconfirmed`, localized equivalents such as
`미확인`, or anything in the owner's weak domain need a self-contained plain
explanation. Include:

- what the ledger row actually says in the owner's language.
- what it means in everyday words.
- why it matters for this project.
- what the owner can choose.
- which choice is recommended and why.

Do not use internal labels as visible explanations. "Resolved candidate" means
nothing to a beginner; say "this looks already fixed, but I need one quick
confirmation before archiving it."

Keep metadata out of readable content. Put source position and stable IDs in
small metadata; put only the issue or decision itself in the summary. Every
choice says what will happen and what stays unchanged. Avoid raw enums such as
`accepted`, `resolved_candidate`, `pending`, or `unknown_unknown` as the main
visible text when the owner's language is not English.

Write for a non-specialist owner, roughly middle-school reading level. Avoid
unexplained shorthand and imported terms. Prefer "purchase/contact button" over
"CTA", "send the form without leaving the page" over "AJAX", "screen-reader
description" over "ARIA", and "movement-reduction setting" over
`prefers-reduced-motion`.

## Host Behavior

Use this precedence:

1. a structured choice tool that is `callable-now`.
2. on a file-writing host with no callable choice tool, the HTML decision board.
3. a numbered reply for read-only/chat-only hosts or when the owner requested
   no temporary files.

An `advertised` but `mode-gated` tool is not callable for this run. Treat it the
same as `unavailable` until the current host mode actually permits the call; do
not probe it speculatively.

The board is a fallback, not the default on hosts that can ask directly.

### Structured Choice Hosts

Use the host's choice tool only when it is callable in the current mode, before
editing the ledger. Triage is bundle-first, not row-first. In the tested Claude
adapter, each call allows at most 4 questions and each question allows 4 options
plus a built-in "Other". Collapse a 20-row ledger into roughly 4-7 questions
across one or two calls, never 7 questions in one call. Other hosts follow their
current callable schema.

Option labels obey the self-sufficiency rule in `host-surfaces.md`: each option
says in plain words what the row is and what applying it would do. A bare ledger
ID or topic shorthand is not an understandable option.

- `quick_cleanup` and `safe_accept`: one multiSelect question each, with one
  option per row and the recommended set stated clearly.
- `decision_bundle`: one single-select question per bundle; recommended action
  first, then 1-2 alternatives.
- `needs_owner_detail`: one question per row; recommended action plus 1-2
  alternatives.
- `needs_external_confirmation`: one multiSelect for the rows that should wait
  on outside confirmation.
- `needs_reexplain`: re-explain in chat and leave awareness `unconfirmed`.

Per row, show the recommended action and 1-2 useful alternatives; use Other for
unusual corrections. Split groups across calls rather than dropping overflow.
If independent decisions still exceed two comfortable rounds, ask whether the
owner wants continued batches or a one-page board. Do not switch surfaces on
your own.

Record the choices and update only selected rows after the owner answers. A
choice-capable run must not load `ledger-triage-board.md` or generate HTML unless
the owner selected that fallback.

### No-Choice File-Writing Hosts

Read `references/ledger-triage-board.md` now and follow its complete board,
response, application, and cleanup contract. This core file intentionally omits
those mechanics so choice-capable hosts are not pulled toward the fallback.

### Small Or Read-Only Runs

If the host cannot write files, or the owner explicitly asks for no temporary
HTML files, use a compact numbered reply. Include exact reply examples and keep
the ledger unchanged until the owner responds.

## Applying Collected Decisions

Regardless of the collection surface:

1. Apply only explicit owner choices. Omitted rows remain unchanged.
2. If any selected item needs re-explanation, explain those first and preserve
   the other collected choices without applying them yet.
3. Apply simple ledger-only maintenance after any required cheap verification.
4. For implementation or multi-step work, create a temporary execution plan
   before touching project files. A board run uses its board directory. A
   structured-choice run uses a temporary `ledger-triage-*` directory under
   `<project-root>/.blindspot-tmp/`. Neither location is documentation or commit
   scope.
5. Record the owner choices, actual work, verification, unresolved blockers,
   and cleanup result concisely in `BLINDSPOT_LEDGER.md`.
6. Delete the temporary plan and directory after completion or after recording
   a durable blocker and re-check trigger.

The temporary plan includes selected IDs, owner choices, work buckets, expected
files/areas, ordered steps, stop conditions, verification, intended ledger
result, and cleanup checklist. Ledger-only choices may appear for context but
must not receive fake file-edit tasks.

After applying decisions, add one `mode: ledger-triage` Audit Log entry with the
collection path, number of decisions applied, implementation-plan lifecycle,
and cleanup result. Preserve the ledger's existing columns, status labels, and
wording.
