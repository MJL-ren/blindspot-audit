# Focus Pack: UX/UI

Deep probes for user-facing interface surfaces: web apps, sites, desktop
and mobile app UIs, game menus/HUDs, and tool UIs. Load this file ONLY for
a `focus: ux-ui` run or a weak-domain escalation in `deep` mode (SKILL.md
Workflow step 4). It exists because full audits structurally under-report
this domain: interface gaps are individually "small" and lose the
findings-cap ranking to legal/security/data findings, while owners who are
strong engineers and weak designers never notice the accumulation.

## Identity Guard

This pack does not turn the audit into a UI review tool. Dedicated
review-and-fix tools already do that well; this audit's job stays the
same: find what the OWNER does not know they are missing. Every probe
below is an awareness question in disguise:

- The finding is never "dark mode is missing." It is "no evidence anyone
  DECIDED about dark mode - was this a choice or a blind spot?"
- The prescription is a decision or cheapest check, not an implementation
  order. A recorded "we skip dark mode because X" is a full success.
- Findings still pass the four-unknowns frame, the evidence rule, the
  3-7 cap, stage fit, and the owner-awareness interview. A prototype
  fails the stage test for most polish-level probes - but NOT for the
  awareness question itself, which is free at any stage.

## Probe Sets

Walk each set against the actual surface. Evidence beats speculation:
read the CSS/tokens, grep for the signals listed under Evidence, walk the
rendered flow when the host already has it running. Tag each gap
`observed` / `absent` / `inferred` as usual.

### 1. Device And Viewport Reality

- Does the layout survive a narrow viewport (~360px) and a wide one, or
  is one of them an accident nobody has looked at?
- Text overflow: long names, long titles, other-language strings - do
  they wrap, truncate with a title/tooltip, or break the layout?
- Are touch targets on interactive elements comfortably tappable
  (roughly 44px), or desktop-cursor-sized only?
- Is there any statement of which devices/browsers are supported? An
  undecided support matrix is itself the finding.

Evidence: `@media` queries (their absence in app-level CSS is loud),
viewport meta, fixed pixel widths, `overflow` handling, table layouts on
data-heavy pages.

### 2. Appearance Modes And Comfort

- Light/dark: supported, deliberately single-mode, or never considered?
  (`prefers-color-scheme`, theme tokens, or a recorded skip.)
- Color contrast: is text readable over its actual backgrounds, and does
  any state (hover, disabled, placeholder) drop below readable?
- Motion: do animations respect `prefers-reduced-motion`, or is that
  unconsidered?
- Text scaling: does the UI survive browser zoom / OS font scaling, or
  are containers pixel-locked around text?

Evidence: `prefers-color-scheme` / `prefers-reduced-motion` queries,
hardcoded hex colors vs semantic tokens, `px` font sizes everywhere.

### 3. State Completeness

The happy path always exists; the audit asks about everything else:

- Empty: what does a new user with zero data see - guidance or a void?
- Loading: do async operations show progress, or does the UI freeze-fake?
- Error: when a request fails, does the user learn what happened and what
  to do, or get a raw error / silent nothing?
- Retry/undo/recovery: can a failed or destructive action be retried or
  reversed? Is destructive action confirmed or recoverable?
- Form recovery: does a validation failure or navigation mishap destroy
  everything the user typed?

Evidence: fetch/async call sites with no loading or error branch, forms
with no inline validation, delete handlers with no confirm/undo,
empty-state components (or their absence).

### 4. Flow Integrity

- Walk the main journey entry-to-outcome as a first-time user: is any
  step a dead end, an unexplained wait, or a "now what?" screen?
- Is there a step where the user cannot go back or escape (modal traps,
  irreversible wizards, no cancel)?
- First-run: does a brand-new user know what to do first, or does the UI
  assume the owner's own familiarity?
- After launch: would the owner ever LEARN that users get stuck (any
  feedback channel, error reporting, analytics decision on record)?

### 5. Input And Access

- Keyboard: can the whole main journey be completed without a mouse? Is
  focus visible, or has `outline: none` been sprinkled without a
  replacement?
- Are interactive elements real controls (`button`, `a`, labeled inputs)
  or clickable `div`s invisible to keyboards and screen readers?
- Do images/icons that carry meaning have text alternatives; is color
  ever the only signal for a state?

Evidence: `tabindex` misuse, `onClick` on non-interactive elements,
missing `label`/`aria-label`, `outline: none` without `:focus-visible`,
`alt` coverage. These basics are also the legally exposed subset
(accessibility regulation applies to commercial surfaces in many
regions - hedge per Ground Rule 5 and check current rules via the
fresh-eyes scan).

### 6. Feedback And Affordance

- Does every user action produce visible acknowledgment (button states,
  save confirmations, active nav highlighting)?
- Can users tell what is clickable, what is selected, and where they are?
- Do error messages say how to recover, in the user's language, or leak
  developer vocabulary?

### 7. Consistency And Visual System

- Is there one spacing/type/color scale, or dozens of hardcoded
  one-offs? (Not an aesthetic judgment - an "every future change costs
  more" and "next agent will guess wrong" finding.)
- Do repeated patterns (buttons, cards, dialogs) look and behave the
  same across pages?

## Peer Anchors

For the peer-expectation half of the scan, compare interaction sets
against category-standard component systems rather than taste: Radix
Primitives, GOV.UK Frontend, USWDS, and Carbon document what a dialog,
menu, or form of this category is expected to DO (keyboard behavior,
focus handling, states). The question stays table-stakes: "every peer's
dialog closes on Escape - does this one? did anyone decide?"

The peer walk itself is not delegable to aggregators: NAME the 2-3 real
peers compared (the report template requires it) and walk their
user-visible surface directly. Listicles, "best apps" roundups, and
agency blogs are leads for CHOOSING peers, never the evidence behind a
table-stakes claim - a category-expectation finding backed only by an
aggregator link fails the source-tier rule (SKILL.md fresh-eyes scan).
(Field data: the pack's first run cited two roundup links and named no
peers - the conclusion happened to hold, but the evidence form did not.)

## Cheapest Next Checks (propose, never run uninvited)

Audits observe (SKILL.md Guardrails). Offer these as the finding's
cheapest check, matched to weight:

- Free and instant: resize the window to phone width; tab through the
  main journey; toggle OS dark mode and reduced motion.
- Automated scanners: axe-core / axe DevTools (accessibility), Lighthouse
  (a11y + performance + mobile), as CI or one-off runs the OWNER starts.
- State coverage: Storybook (or equivalent) stories for empty/loading/
  error states - the states that exist in stories tend to exist in code.
- Full review-and-fix: a dedicated frontend design-audit skill or a human
  designer pass, once the owner knows the gaps exist.

Scanners find the mechanical subset (contrast, labels, landmarks); flow
dead-ends, state gaps, and "nobody decided" findings remain this audit's
territory - that split is why both belong in one prescription list.

## Reporting

Focus-run reports follow the normal template with `scope: focus/ux-ui`
in the header. The awareness interview matters MORE here than in full
audits: expect a high share of `unknown_unknown` from engineer-owners and
translate every finding to plain consequences (Ground Rule 6 - "users on
phones see a broken layout", not "no responsive breakpoints"). Record the
pack as run in the audit log's scan notes, so rules 8 and 10 stop
flagging it as coverage debt.
