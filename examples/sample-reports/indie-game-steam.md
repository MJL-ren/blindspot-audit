# Sample Report - Indie Game Heading To Steam

Synthetic example. Project, paths, and findings are invented.

Setting: "Lanternfall", a Unity roguelike by a solo dev (strong in
programming, first-ever commercial release), targeting Steam in ~4 months.
No-choice host (chat-only agent); awareness left unconfirmed with a
numbered check.

---

**Blindspot Audit**

Scope: `D:\games\lanternfall` - deep mode, full project (engine-generated
dirs excluded by inventory). Fresh-eyes web scan: ran (category-only:
"indie game first Steam release checklist", "Steam store page
requirements"; the game's title was never searched - Ground Rule 7).
Project shape: game prototype→pre-release; solo owner, commercial intent
confirmed in `GDD.md`; owner-inverse weights publishing/legal/store
mechanics up, code quality down.
Ledger: created `Docs/BLINDSPOT_LEDGER.md` (repo root has no docs/;
project uses `Docs/`). Counts: 5 new.

Top blind spots (5):

1. Steam's paperwork has waiting periods the schedule ignores
   - In plain terms: before any wishlist page exists, Steam requires a
     paid app registration and identity/tax review that can take weeks,
     and the store page itself needs review time. These are calendar
     items, not tasks.
   - Why it matters: `GDD.md` plans "store page at beta" 3 weeks before
     launch - the observed timeline has no slack for Steam's own clocks
     (source: Steamworks onboarding docs - official tier).
   - Cheapest check: register the app this week; the fee is sunk either
     way and it starts every other clock.
   - Priority: now | Confidence: high | Awareness: unconfirmed

2. Save files have no version number, so every update can eat old saves
   - In plain terms: writing a tiny "save format v1" field now lets future
     code load old saves; without it, players who update mid-run lose
     progress and refund.
   - Evidence: observed - `SaveManager.cs` serializes raw structs, no
     version field; absent - no migration path anywhere.
   - Cheapest check: add one int field + a default-migration branch (1 hr)
     before more save-touching features land.
   - Priority: now | Confidence: high | Awareness: unconfirmed

3. The asset folder mixes bought, free, and unknown-license files
   - Why it matters: commercial release makes every "free download" font
     and SFX a license question; `Assets/ThirdParty/` has 41 files and no
     provenance list (observed). Community forums disagree on several
     packs' terms (community tier - leads only, not treated as fact).
   - Cheapest check: a `CREDITS.md` pass - one line per third-party asset:
     source, license, link. Unknowns get replaced or bought.
   - Priority: next | Confidence: medium | Awareness: unconfirmed

4. Nobody outside the dev has played it, and launch is the first playtest
   - In plain terms: playtesting is not QA - it is discovering that
     strangers do not read minds. The first external run always finds
     onboarding walls the author cannot see.
   - Why it matters: roguelike peers live or die on first-run clarity;
     stage-appropriate now (core loop is playable - see below).
   - Cheapest check: 3 strangers, screen-recorded first 15 minutes, no
     coaching.
   - Priority: next | Confidence: high | Awareness: unconfirmed

5. Selling into Korea triggers a ratings step the plan never mentions
   - In plain terms: some regions require an age rating before commercial
     release; in Korea that is GRAC (self-designation via Steam's process
     for most indie cases, but it must be answered, not ignored).
   - Why it matters: `GDD.md` lists Korean as a launch language, so the
     region is in scope by the project's own plan. Regulated domain: a
     professional or the platform's official flow must confirm specifics.
   - Cheapest check: read Steam's content-rating questionnaire once and
     note intended answers in the GDD (source: official docs tier).
   - Priority: later | Confidence: medium | Awareness: unconfirmed

Checked and well covered:
- Core loop is playable start-to-death today (ran the observed build log,
  not a fresh build - Guardrails) - rare and genuinely ahead of schedule.
- Cut-list exists and is honest (`Docs/CUTLIST.md`).
- Code quality, structure, tests: strong - owner's expert area, kept
  concise per Ground Rule 6.

Skippable for now:
- Localization implementation - strings are already table-driven; actual
  translation waits until content freeze. Re-check when: content freeze.
- Achievements/trading cards - post-launch platform features. Re-check
  when: first update planning.

Awareness check:
Reply with the numbers you already knew. Omitted numbers stay classified
as newly surfaced by this audit.
Examples: `1, 3` or `I already knew 1 and 3`. If one is unclear, reply
like `5?` and I will re-explain it more simply.

Decision packet:
1. Store page timing
   Recommended: register now, draft page at alpha
   Options: register now / keep current plan (3 weeks pre-launch) - risks
   Steam-side delays landing on launch day
   Why it matters: every Steam clock starts at registration.

Ledger delta:
- new: BS-20260706-01..05
