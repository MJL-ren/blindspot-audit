# Expected Behavior - frontend-ux-gap (weak-domain escalation + ux-ui focus pack)

The README profiles the owner as backend-strong and frontend-weak, with a
real web surface about to widen (team of 8 -> whole company, some on
phones). The tracked gaps (TODO/README) are backend-only, so every UI gap
is untracked. This fixture is graded in two runs.

## Run A - full audit ("Run a blindspot audit on this project.")

### Pass criteria

- The owner profile notes frontend/UX as a weak area (readable from the
  README - `inferred`, not asked).
- The report emits the weak-domain escalation meta-finding for UX/UI: it
  says plainly that the UI surface was only skimmed, and prescribes a
  `focus: ux-ui` run as the cheapest next check - OR (deep mode) the run
  inline-loads the ux-ui pack and reports concrete UI findings itself.
- The un-run pack is recorded as coverage debt in the ledger/audit-log
  proposal.
- Real untracked findings may share the cap (legitimate examples: job
  names are rendered into HTML unescaped; "open to the whole company next
  month" with no support/feedback channel decided). Tracked items (rate
  limiting, DB backup) are filtered per Ground Rule 1.
- Both trust sections present.

### Fail criteria

- No mention of the UI/UX domain anywhere in the report - the audit
  treated the skim as coverage despite an owner-inverse weak domain with
  a large surface (this is the exact regression this fixture exists to
  catch).
- The security finding (unescaped rendering) is treated as having
  "covered" the frontend - a code finding does not discharge the UX
  domain.
- Rate limiting or DB backup reported as discoveries (they are tracked).
- Reading this EXPECTED.md and citing it as project evidence.

## Run B - focus run ("Run a blindspot audit with focus: ux-ui.")

### Pass criteria

- Loads the ux-ui pack; scope line says `focus/ux-ui`; findings append as
  delta rows, no second ledger.
- Concrete gaps found among (3-7 cap still applies; each with evidence,
  consequence, cheapest check): fixed ~1180px layout with no viewport
  meta while phone use is stated in the README; fetch calls with no
  loading or error handling (a failed request silently shows nothing);
  Delete with no confirmation or undo; controls are clickable `div`s with
  `outline: none` - keyboard and screen-reader users cannot operate the
  page; no empty state for zero jobs; no evidence anyone decided about
  dark mode / appearance.
- Findings are phrased as awareness/decision questions in plain words
  ("on-call engineers on phones will see a broken layout"), never as
  aesthetic taste or feature orders.
- The pack run is recorded in the audit log so coverage tracking sees the
  domain as covered.

### Fail criteria

- Aesthetic/taste findings ("colors look dated", "use a nicer font") or
  differentiator suggestions (add charts, add auth).
- Prescriptions written as implementation orders instead of decisions or
  cheapest checks.
- Running heavy tooling uninvited (the pack proposes axe/Lighthouse as
  the owner's checks; it does not run them).
- Reading this EXPECTED.md and citing it as project evidence.
