# Run Log

One row per graded run - fixture or real project. Real projects are
named by category only (AGENTS.md privacy rule; this file is public).
Format documented in `README.md` ("Recording runs").

| Date | Skill version | Host / model | Target | Verdict | Notes |
| --- | --- | --- | --- | --- | --- |
| 2026-07-08 | 0.6.0 | Codex / GPT-5 | skill distribution repository (ledger-triage self run) | pass with notes | No-choice HTML board created and served, 5 owner decisions validated, owner note preserved as a plan constraint, and implementation-heavy choices routed through a temporary plan. This run is not a clean large-ledger fixture grade because the grading key was read in-session. |
| 2026-07-06 | 0.5.0 | Claude Code / Opus | commercial symbolic-reading web app (focus/ux-ui, diff run) | pass with notes | Focus targeting, pack probes, coverage-debt clearing, credit sections, and the 4-option interview split all worked; findings landed behavioral, not checklist. Deviations fixed in 0.5.1: aggregator-only category evidence with no named peers, unlabeled source tiers, non-canonical values (`now~next`, localized awareness), pre-interview awareness guesses. |
| 2026-07-06 | 0.5.1 | Claude Code / Opus | artist portfolio + commission site (focus/ux-ui, diff run) | pass with notes | All three 0.5.1 fixes held in the field: named peer walk with direct fetches (and it prevented a false pricing finding by proving "inquire-only" is peer-normal), tiered sources with cross-tier hedging, canonical values + `unconfirmed` before the interview. 4/6 findings landed unknown_unknown; context answer (customer regions) correctly re-weighted an existing ledger item. New drift: owner profile duplicated into host-local memory uninvited (fixed in 0.5.2 context-canon rule). |
