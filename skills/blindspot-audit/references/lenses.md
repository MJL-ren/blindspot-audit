# Audit Lenses

Use these lenses selectively. The goal is to find what the project is likely
missing, not to score every category.

## How To Derive Lenses (works for any project)

Unknown unknowns cannot be enumerated directly, but they can be triangulated
by looking at the same project through several independent reference frames.
The named lenses below are these four frames pre-applied; when a project
fits none of them cleanly, apply the frames yourself:

1. **Domain table-stakes.** Picture a healthy, shipped, successful peer of
   this project. What does it have that this project doesn't? What would a
   reviewer of that category check within the first five minutes?
2. **Lifecycle.** What does the NEXT stage demand that the current stage
   does not? Pre-release projects fail on release mechanics; launched
   projects fail on operations; growing ones fail on things that don't
   scale.
3. **Role walk.** Walk the project past a row of specialists - security
   engineer, lawyer, accountant, designer, operations person, marketer,
   editor, community manager. For each: what is the FIRST thing they would
   point at? Keep only the roles the owner isn't.
4. **Owner inverse.** Whatever the owner is best at is the best-covered
   area; blind spots concentrate in the complement. A designer's project
   will be beautiful and unmonitored; an engineer's will be tested and
   unmarketed; a writer's will be well-plotted and unbacked-up.

## User And Workflow Lens

- Is the main user journey visible from entry to outcome?
- Are empty, loading, failed, retry, undo, and recovery states considered?
- Is there a human review point where output quality or user trust depends on judgment?
- Can a new user or future session understand what to do first?

## Data And State Lens

- What data is created, modified, deleted, cached, exported, or restored?
- Are identity, ownership, versioning, duplication, and migration rules clear?
- Is destructive action recoverable or intentionally final?
- Are comparison anchors stable enough for future review?

## Security And Boundary Lens

- Are secrets, tokens, private files, prompts, user data, and external connectors bounded?
- Are permissions and trust boundaries clear?
- Could untrusted text, files, model output, or external webpages change instructions?
- Are defensive security tasks separated from offensive or policy-sensitive paths when needed?

## AI And Agent Lens

- What can the model decide without asking?
- Where must human judgment outrank model judgment?
- Are model outputs logged, replayable, comparable, or reviewable?
- Is fallback behavior defined when the preferred model refuses, fails, changes, or becomes too expensive?
- Are prompts, skills, and memory surfaces aligned, or can they drift?
- If AI output reaches end users or the public: do AI-content disclosure or labeling rules apply in the operating regions?

## Verification Lens

- What feedback loop proves the work actually functions?
- Are there cheap smoke tests before expensive full tests?
- Are tests tied to user-facing behavior, not only implementation details?
- Can future agents reproduce the check from documented commands?
- Is test coverage lopsided - one layer heavily tested while another (often the UI or the newest surface) has none?

## Operations And Failure Lens

- What happens when dependencies, APIs, auth, rate limits, files, network, or local services fail?
- Are logs, diagnostics, rollback, backups, and cleanup paths visible?
- Is there a manual recovery path for the most likely failure?
- Is the project resilient to partially completed agent work?
- When it breaks for a real user, how does the owner find out? Is there any support or contact channel?

## Cost And Performance Lens

- What operations can explode in token use, runtime, API cost, memory, storage, or browser automation time?
- Are expensive paths cached, bounded, sampled, or explicitly accepted?
- Are large files, large repos, long conversations, and generated artifacts handled deliberately?

## Product And Business Lens

- Is the real audience clear: personal, internal, public, paid, client, enterprise, or research?
- Are pricing, licensing, support burden, legal/brand claims, and promise boundaries considered where relevant?
- Does the project need a decision log or public/private split?
- Are draft-only, private, spoiler, or internal notes prevented from becoming public artifacts by accident?
- After launch, how would the owner know if anyone uses it, or where they give up?

## Maintainability Lens

- Can another session understand the current state without reading the whole repo?
- Are plans, docs, implementation, tests, and actual runtime behavior aligned?
- Are duplicated concepts, stale docs, or hidden conventions likely to mislead the next agent?

## Domain Fit Lens

- What would an experienced person in this project category ask that the current docs do not answer?
- What quality bar does the user only recognize when shown examples?
- What reference implementation, screenshot, existing module, dataset, or external source would reduce ambiguity?
- What do USERS of this category take for granted? Pick 2-3 representative
  peers and walk their user-visible surface: which features/elements do all
  of them have that this project lacks? (Table stakes only - see the peer
  expectation scan in SKILL.md; differentiator ideas are not findings.)
- Is the absence a decision the owner made, or an expectation they never
  knew existed? The prescription is "decide to meet it or skip it on
  record", not "build it".

## External Change Lens

Time-dependent by nature - pair with the fresh-eyes web scan in the
workflow. These cannot be answered from the repo alone:

- Did regulation change in the operating regions (AI-content labeling, data
  protection, disclosure rules, age rating, tax thresholds)?
- Did a platform the project depends on change policy, pricing, ownership,
  or requirements (store rules, contest calendars, API deprecations,
  provider acquisitions)?
- Did the market or genre move (new conventions, saturated positioning,
  shifted reader/player expectations)?
- Is any research or provider comparison in the project's docs older than a
  few months in a fast-moving area? The document's conclusion may be stale
  even if its method was sound.
