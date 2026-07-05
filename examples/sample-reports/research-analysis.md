# Sample Report - Research Analysis Heading To A Paper

Synthetic example. Project, paths, and findings are invented.

Setting: "reef-acoustics", a solo researcher's analysis of underwater
sound recordings, aiming at a journal submission. Owner is expert in the
science and statistics, non-expert in software/data engineering.
Choice-capable host; interview completed. Scoped note: owner asked for a
quick mode pass.

---

**Blindspot Audit**

Scope: `~/research/reef-acoustics` - quick mode, full project. Inventory +
9 evidence files. Fresh-eyes web scan: targeted only (venue mechanics);
category-only queries.
Project shape: research/analysis archetype; drafting stage; solo owner
strong in domain + stats, weak in data plumbing (owner-inverse weights
reproducibility and provenance up, methodology down).
Ledger: created `BLINDSPOT_LEDGER.md` at root (no docs/ folder). Counts:
4 new.

Top blind spots (4):

1. The figures cannot be regenerated from the raw data
   - In plain terms: the path from recordings to Figure 3 currently runs
     through six notebooks executed in a remembered order. Reproducing it
     is archaeology, and reviewers increasingly ask for exactly that.
   - Why it matters: observed - `notebooks/` has 14 files, 6 with
     hardcoded local paths; absent - no run-all script, no environment
     file. One `KeyError` away from unfixable figures during revision.
   - Cheapest check: one `make figures` (or `run_all.py`) that executes
     the real chain end-to-end once, today, while memory is fresh.
   - Priority: now | Confidence: high | Awareness: unknown_known - owner
     knew and winced; prescription is documentation + the script, now in
     the ledger.

2. Raw recordings exist in exactly one place
   - Why it matters: `data/raw/` (38 GB, observed) sits on one external
     drive; derived data is regenerable, raw is not - it is fieldwork.
   - Cheapest check: one cold copy (cloud or second drive) + a checksum
     manifest; an afternoon.
   - Priority: now | Confidence: high | Awareness: unknown_unknown

3. A third of the dataset has unclear reuse terms
   - In plain terms: 12 of the recordings came from a collaborator's
     older project (observed: `data/raw/ext_*`, no accompanying terms).
     Journals ask who may publish derived results from shared data.
   - Cheapest check: one email to the collaborator confirming reuse +
     citation expectations; file the reply in the repo.
   - Priority: next | Confidence: medium | Awareness: unknown_unknown

4. The target journal's mechanics are assumed, not checked
   - Why it matters: the draft targets a specific venue (observed:
     `draft/paper.md` header) but nothing records its data-availability
     policy, length caps, or submission-window realities - the fresh-eyes
     check found the venue now REQUIRES public data deposits for this
     article type (source: journal author guidelines - official tier).
   - Cheapest check: 20 minutes on the author guidelines; note the three
     hard constraints in the draft header. Finding 3 becomes a blocker if
     deposit is mandatory - the two interact.
   - Priority: next | Confidence: high | Awareness: unknown_unknown

Checked and well covered:
- Methodology and stats are documented to a level this audit cannot
  improve (owner's expert area - noted, not lectured).
- Literature notes are current and cited with links (`notes/lit.md`).
- Version control covers code and draft; only data sits outside it, which
  is normal at this size.

Skippable for now:
- Packaging the pipeline for strangers (containers etc.) - no external
  users exist; re-check when: the paper is accepted and deposit is
  prepared.
- Automated tests for analysis code - the run-all script from finding 1
  is the right first verification layer at this stage.

Interview (completed):
- 1 = unknown_known; 2, 3, 4 = unknown_unknown.

Known unknowns to ask next:
- If the deposit requirement applies, does the collaborator agreement
  (finding 3) permit PUBLIC release, not just reuse?

Ledger delta:
- new: BS-20260706-01..04
