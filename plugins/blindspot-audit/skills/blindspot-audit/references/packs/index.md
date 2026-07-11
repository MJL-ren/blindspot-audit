# Focus Pack Registry And Contract

Read this file before loading any domain focus pack. It is the canonical
registry of implemented packs and the shared contract for adding another one.
A focus pack adds depth to the normal blindspot workflow; it does not replace
the four-unknowns frame, evidence rules, findings cap, owner interview, or
ledger behavior in `SKILL.md`.

## Contents

- Runtime routing
- Available packs
- Required pack sections
- Finding gate
- Coverage notes
- Adding a pack

## Runtime Routing

1. Resolve the audit mode first. `ledger-triage` never loads a focus pack.
2. Normalize the requested domain to a registered Focus ID. An explicit Focus
   ID wins. Aliases help interpret natural language but never change the
   canonical ID or scope label; when aliases overlap across packs, use the
   owner's stated surface to disambiguate and ask only if the boundary would
   materially change the run.
3. Load exactly one registered pack per focused pass. Even in `deep` mode, do
   not combine packs into a broad checklist; use the highest-value
   owner-inverse domain and leave the rest as coverage debt or later focus runs.
4. If the owner explicitly requests multiple registered focuses, treat them as
   separate focused passes in the stated order, with a separate scope, findings
   cap, and Audit Log run/evidence record for each. Do not merge their probe sets or imply that
   one completed the other's coverage. Filter each later pass against findings
   already produced so neighboring packs do not create duplicate ledger rows.
5. A focus may be narrowed to a file, module, or feature when the owner says so.
   Record that as partial pack coverage; it does not clear project-wide debt for
   the rest of the applicable surface.
6. For an explicit registered focus, load the matching pack whether the base
   mode is `quick`, `deep`, `planning`, `post-implementation`, or `interview`.
   The base mode still controls inspection depth and interaction style.
7. If the requested domain is not registered, do not invent a pack or pretend
   a nearby pack covers it. Run a generic domain-scoped pass with the ordinary
   lenses when useful, disclose `no registered pack loaded` in the scope and
   Audit Log/Audit Evidence, and do not mark any pack as completed.
8. Weak-domain escalation may prescribe or inline-load only a registered pack.
   For an unregistered specialist domain, prescribe a bounded specialist check
   instead of a nonexistent `focus` pack.
9. If the owner says "same focus", "previous focus", or equivalent wording
   without naming an ID, read the current project's Audit Log and linked Audit
   Evidence. Reuse the most recent registered Focus ID only when it is the one
   clear referent. If multiple prior focuses are plausible, ask one short
   disambiguation question. If no durable prior focus exists, do not infer from
   another project, host memory, or the agent's recollection.

## Available Packs

| Focus ID | Pack file | Apply when | Natural-language aliases |
| --- | --- | --- | --- |
| `ux-ui` | `ux-ui.md` | The project has a meaningful user-facing visual or interactive surface. | UX, UI, interface, usability, accessibility, frontend experience |
| `security` | `security.md` | The project has untrusted input, identities, credentials, private data, network exposure, executable releases, or privileged automation. | security, cybersecurity, appsec, secure by design, authentication, permissions, secrets, supply-chain security |

A pack is available only when both its registry row and file exist. The Focus
ID is lowercase kebab-case, the file is `<focus-id>.md`, and the ledger scope is
always `focus/<focus-id>`.

## Required Pack Sections

Every pack must keep these exact second-level headings, in this order. The
content under them stays domain-specific.

1. `## Activation And Applicability`
   - Define the material surface that makes the pack relevant.
   - Name clear not-applicable cases so every project does not inherit every
     pack as debt.
   - Name neighboring domains and the handoff boundary where overlap could
     otherwise create duplicate or contradictory findings.
   - State the canonical Focus ID and `focus/<id>` scope near the top.
2. `## Identity Guard`
   - Explain how the pack remains a blindspot audit rather than becoming a
     scanner, specialist review, compliance claim, feature brainstorm, or
     implementation order.
   - Keep owner awareness and deliberate skips as successful outcomes.
3. `## Surface Map`
   - Name the artifacts, boundaries, flows, roles, and runtime surfaces to
     sample before probing.
   - Distinguish repository evidence from external or owner-only confirmation.
4. `## Probe Sets`
   - Use 4-8 compact groups of awareness questions.
   - Pair questions with concrete evidence signals where useful. Absence is a
     candidate signal, not proof.
   - Prefer questions that change a decision over encyclopedic coverage.
5. `## Boundaries And Stage Fit`
   - Name common false positives, early-stage exemptions, and conditions that
     raise or lower urgency.
   - Separate mechanical checks from human or specialist judgment.
6. `## Peer And Current Anchors`
   - Explain which peers, standards, official sources, or current external
     facts can calibrate the domain.
   - Method references may be stable; time-sensitive claims must be verified
     during the run. Community sources remain leads until a primary source
     confirms them.
7. `## Cheapest Next Checks`
   - Offer checks from free/read-only through specialist review.
   - Observe the normal expensive-command and authorization guardrails. Packs
     propose scanners, builds, deploys, destructive tests, or paid reviews;
     they do not run them uninvited.
8. `## Reporting And Coverage`
   - Restate the canonical scope, owner-language requirement, and any
     domain-specific explanation need.
   - Say what to record under the compact Audit Log run ID and linked Audit Evidence so later runs can distinguish
     completed (including explicit owner-confirm-needed limits), partial, not
     applicable, owner-skipped, and still-unrun coverage.

## Finding Gate

A pack probe becomes a finding only when all of these hold:

1. The project has a material surface to which the probe applies.
2. Evidence makes the consequence plausible for this project.
3. The item is not already a known unknown in owner docs or the ledger.
4. It fits the project's current stage or has a reason it cannot safely wait.
5. It is a missing decision or likely awareness gap, not merely a missing tool
   or fashionable feature.
6. The report can explain it in the owner's language and name a cheapest next
   check.

The normal 3-7 findings cap applies across the whole focused run, not per probe
set. A pack is a search instrument, not a checklist scorecard.

## Coverage Notes

Use the pack's applicability section before creating coverage debt. A registered
pack becomes standing debt only when the project has a substantial matching
surface, the pack has never run, and the owner has not skipped it on record.

Record one plain scan note using the canonical ID, for example:

- `pack ux-ui: completed; inspected <surfaces>; limits <limits>`
- `pack ux-ui: partial; scope <path/feature>; remaining <surfaces>`
- `pack ux-ui: not applicable; no material user-facing interface`
- `pack ux-ui: skipped by owner; re-check when <trigger>`
- `pack ux-ui: coverage debt; substantial interface, pack not yet run`

A generic unregistered-domain pass records `no registered pack loaded` and
never clears a registered pack's debt. Each pack defines which applicable
surfaces are repository-inspectable and which require owner/runtime/provider
confirmation. Mark it completed only after every applicable inspectable surface
was covered; external-only confirmation may remain as explicit limits when the
pack permits. A path-limited or otherwise constrained repository run stays
partial.

## Adding A Pack

1. Choose one stable lowercase kebab-case Focus ID.
2. Add `<focus-id>.md` and a registry row in the same change.
3. Satisfy every required section and the finding gate without copying
   third-party prose into the skill.
4. Add a focused eval fixture with both applicable and false-positive pressure.
5. Run a clean live-agent focus pass before calling the pack stable.
6. Sync the Codex plugin copy, rebuild the `.skill` package, and run the full
   repository verification gates.
