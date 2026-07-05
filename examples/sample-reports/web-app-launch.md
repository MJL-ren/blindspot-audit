# Sample Report - Web App About To Go Public

Synthetic example. Project, paths, and findings are invented.

Setting: "PlateNote", a recipe-sharing web app built by a solo backend
engineer as a side project, about to be shared publicly for the first
time. Choice-capable host; interview completed.

---

**Blindspot Audit**

Scope: `~/dev/platenote` - deep mode, full project. Inventory + 14
evidence files read. Fresh-eyes web scan: ran (category-only queries).
Project shape: frontend app + backend API hybrid; pre-launch; solo owner,
expert in backend/testing, non-expert in legal, operations-after-launch,
and product positioning (lenses weighted accordingly). Public,
non-commercial for now (owner-confirmed at intake).
Ledger: created `docs/BLINDSPOT_LEDGER.md` + routed from `docs/README.md`.
Counts: 4 new.

Top blind spots (4):

1. The signup form stores emails, but nothing tells users what happens to
   them
   - In plain terms: once real people's emails land in your database, most
     regions expect a short public privacy note and a way to be deleted.
     A page and a delete query, not a legal project.
   - Why it matters: launch makes this real on day one; EU visitors can
     reach the form (observed: `signup.tsx`, no policy page in routes).
   - Evidence: observed + absent.
   - Cheapest check: draft the note from a reputable template (30 min);
     have a professional confirm - this audit is a scout, not a lawyer.
   - Priority: now | Confidence: high | Awareness: unknown_unknown

2. If the app breaks after launch, nobody finds out
   - In plain terms: an error tracker is a service that emails you when
     users hit crashes you never saw. Without one, the first report is an
     annoyed stranger - or silence.
   - Why it matters: solo project, no support channel (absent: no error
     reporting dependency, no contact route); the failure mode is quiet
     abandonment, not a bug report.
   - Cheapest check: wire the free tier of any error tracker (1 hr) or at
     minimum an uncaught-exception email hook.
   - Priority: now | Confidence: high | Awareness: unknown_unknown

3. The database has no backup story
   - Why it matters: user-created recipes become irreplaceable data the
     moment strangers arrive; the deploy config shows a single container
     volume (observed: `compose.yml`) and no dump schedule (absent).
   - Cheapest check: one nightly `pg_dump` to object storage + one manual
     restore drill before launch.
   - Priority: now | Confidence: high | Awareness: unknown_known - owner
     knew, written nowhere; prescription is a line in `docs/OPERATIONS.md`,
     which did not exist yet (created as part of ledger routing).

4. Peers all have password reset; PlateNote does not
   - In plain terms: peer expectation gap - checked 3 comparable small
     recipe/notes apps; all offer "forgot password". Users treat its
     absence as broken, not minimal.
   - Why it matters: table stakes at public stage; support burden lands on
     the owner's inbox otherwise.
   - Cheapest check: decide - implement magic-link reset, or record a
     deliberate skip with "invite-only beta" as the stated reason.
   - Priority: next | Confidence: medium | Awareness: unknown_unknown

Checked and well covered:
- Backend test suite is real and passing (observed: 84 tests, CI green) -
  the owner's expert area, as expected.
- Secrets are env-injected, none committed (checked `.env.example`, git
  history sample).
- README onboarding is genuinely good: a stranger could run it.

Skippable for now:
- Horizontal scaling - single-node is fine below thousands of users;
  re-check when: sustained traffic or paid tier.
- i18n - English-only is a positioning choice at this stage; re-check
  when: non-English user feedback appears.

Interview (completed):
- 1, 2, 4 = unknown_unknown; 3 = unknown_known (now documented).

Known unknowns to ask next:
- Is "non-commercial" stable? Ads or paid tiers would activate tax and
  consumer-law lenses that were deliberately left out of this audit.

Ledger delta:
- new: BS-20260706-01..04 (as above)
