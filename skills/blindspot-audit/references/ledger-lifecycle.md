# Ledger Lifecycle

Use this reference when a blindspot audit needs durable project memory. The
ledger is the permanent fix for the self-selecting-context problem: once a
blind spot is written into the project, it can never be an unknown unknown
again - and future audits diff against it instead of re-nagging.

## Discover Existing Ledgers

Before creating a new file, search for existing risk or blindspot surfaces:

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

## Create The First Ledger

Use `templates/BLINDSPOT_LEDGER.md` as the starting shape. Write the prose
in the owner's language; keep IDs, status, and awareness values in English.
If the project has its own doc conventions (frontmatter, naming), follow
them so the ledger looks native. Fill:

- project name and path.
- audit date.
- audit mode and host.
- scope boundary.
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
- Mention it in handoff only when the current next session must act on it.

Do not create broad routing systems just for the ledger. Add one small
pointer to an existing routing file.

## Update Existing Ledgers

On later runs:

- Read the ledger first.
- Verify stale or high-impact items against current code/docs.
- Add only new or changed findings.
- Mark changed status instead of rewriting history (date the change in the
  status cell).
- Keep local labels and decision terms.

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
- `deliberate_skip`: owner considered and declined -> move to the skip
  section with the reason and a re-check trigger.
- `unconfirmed`: interview not yet done (non-interactive run).

## Keep The Ledger Compact

A ledger that only grows becomes another hidden document - the exact
problem it exists to solve. Target state: the main findings table holds
only items that still need attention (`pending`, `accepted`, `deferred`).

- Same-session remediation: when a finding is fixed while the session is
  still open, set it to `resolved` with the date before finishing. The
  final report and the ledger must not disagree.
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
