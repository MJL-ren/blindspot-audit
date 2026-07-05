# Project Archetypes

Pick the closest archetype or combine several. Use the examples as prompts
for inspection, not as mandatory findings. Weight the areas the owner is NOT
expert in (see the owner-inverse frame in `lenses.md`).

## Frontend App Or Website

Likely blind spots:
- Main user journey exists but empty/error/loading/mobile states are missing.
- Visual direction is specified but component density, text overflow, and responsive constraints are not.
- State transitions are designed in happy-path screenshots only.
- Accessibility, keyboard navigation, and reduced-motion behavior are absent.
- Build and screenshot verification are not documented.
- Test coverage is lopsided: backend tested, UI untested while the UI surface keeps growing.

## AI Agent Or Prompt Workflow

Likely blind spots:
- Human review boundaries are unclear.
- Prompt, memory, skills, and tool instructions can drift.
- Model fallback or refusal behavior is not defined.
- Runs are not replayable because inputs, context hashes, model settings, or outputs are not saved.
- Cost and token use are not bounded.
- AI-generated output that reaches users or the public may fall under AI-content labeling rules in the operating regions.

## Data, Analytics, Or Report Pipeline

Likely blind spots:
- Metric definitions, denominators, exclusion rules, and time windows are not explicit.
- Source freshness and missing-data behavior are unclear.
- Charts/report claims are not tied to reviewed rows or source queries.
- Sampling/truncation may hide important edge cases.
- Reproducibility depends on ad hoc notebooks or chat history.

## Research Or Analysis Project

Likely blind spots:
- Results cannot be regenerated from raw data because the pipeline lives in memory or scattered notebooks.
- External claims and datasets are not traceable to sources with license/citation.
- Raw data is not backed up separately from derived data.
- The current work has drifted from the original question without anyone deciding that.
- Parallel or competing work has not been checked recently.
- Human-subject data lacks consent, anonymization, or retention rules.
- Target venue (journal, conference, report) format and deadline mechanics are unexamined.

## CLI, Library, Or Developer Tool

Likely blind spots:
- Install, upgrade, and first-run flows are not tested.
- Error messages do not tell users how to recover.
- Config paths, env vars, and defaults are not documented.
- Cross-platform behavior, especially Windows paths and shell semantics, is unverified.
- Public API boundaries are mixed with internal helpers.

## Backend, API, Or Integration

Likely blind spots:
- Auth, authorization, idempotency, retries, and rate limits are underspecified.
- External provider failure modes are not represented in tests.
- Migration, rollback, and data cleanup paths are missing.
- Logging may leak secrets or omit correlation details.
- Webhook or callback verification is incomplete.

## Creative Writing (novel / web novel / script / webtoon)

Likely blind spots:
- Manuscript survival: the text lives on one device or account with no
  version history - "restore yesterday's draft" is impossible.
- Continuity debt: no series bible / timeline / name-and-rules tracker, so
  consistency lives entirely in the author's memory and contradictions
  accumulate silently with chapter count (brutal to audit retroactively).
- Positioning: target reader, genre keywords, and comparable titles are not
  written anywhere.
- Platform conventions: the intended venue's formatting rules, upload
  cadence norms, exclusivity/contract clauses, and revenue split are
  assumed rather than researched.
- Retention structure: the opening does not match the venue's drop-off
  reality (e.g., web novel readers deciding within the first chapters), and
  no one outside the author has read it.
- Rights and credits: pen name, copyright notice, cover art contract and
  its AI-generation disclosure rules, quoted or borrowed material.
- Income mechanics (only if monetizing): platform payout requirements and
  tax registration thresholds.

## Creative, Content, Or Brand Project

Likely blind spots:
- Audience, usage surface, and quality bar are implicit.
- Visual consistency relies on taste in chat, not durable references.
- Rights, licensing, printing constraints, and asset provenance are untracked.
- Review artifacts do not show enough alternatives for real choice.
- Final deliverable format is unclear.
- Public/private boundaries are unclear: spoiler material, client-only notes, source references, or draft concepts may leak into public-facing outputs.
- Platform dependency: the audience is reachable through one channel only.
- Ad/sponsorship disclosure rules in the operating region are unexamined.

## Game Or Interactive Prototype

Likely blind spots:
- Core loop is not playable before polish.
- Playtesting loop: nobody outside the developer has played it, and the
  first external playtest is implicitly scheduled for launch.
- Scope control: no cut-list, no minimum shippable definition.
- Asset provenance: music, fonts, sprites, SFX from "free download" sources
  whose licenses were never checked against commercial release; source
  files (PSD/aseprite/tracker) live outside version control.
- Save compatibility: no version field in the save format, so
  mid-development saves break on update.
- Input, failure, restart, and onboarding states are missing.
- Store/platform mechanics: registration fees and waiting periods, page
  assets, demo/festival calendars, age rating requirements (including
  regional boards such as GRAC in Korea), platform cert rules - all with
  long lead times that are invisible until shipping week.
- Performance floor: lowest-spec machine it has actually run on is unknown.
- Accessibility baseline (remapping, colorblind-safe signals, text scaling)
  is cheap early and expensive late.
- Localization readiness: hardcoded strings, font coverage for target
  languages.

## Documentation Or Knowledge Base

Likely blind spots:
- Source of truth and archive boundaries are unclear.
- Docs describe intended behavior but not current implementation reality.
- Entry points, next actions, and ownership are hard to find.
- Stale plans remain mixed with active decisions.
- Future agents cannot tell what is confirmed, proposed, or obsolete.
- Canon/proposal/archive/spoiler boundaries are not durable enough for future readers or agents.

## Personal Automation Or Local Workflow

Likely blind spots:
- Important state lives only in chat, not files the next session will read.
- Local paths, auth state, and machine-specific assumptions are undocumented.
- Automation failure or missed reminder behavior is unclear.
- Sensitive personal data may be stored where it should not be.
- The workflow lacks a small recurring health check.
- Convenience notes, reminders, and research may slowly mix private context with reusable project knowledge.
