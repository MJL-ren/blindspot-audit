# Expected Behavior: Ledger Triage Large Ledger

This fixture tests `mode: ledger-triage`, not a normal blindspot audit.

## Pass Criteria

- Reads `BLINDSPOT_LEDGER.md` first and treats it as the primary artifact.
- Does not create new project blindspot findings or run a fresh-eyes scan.
- Groups the 20+ open rows into triage categories instead of asking 20
  separate chat questions.
- Preserves localized status/awareness labels in untouched rows; no
  mass-normalization of `대기` or `미확인`.
- Does not add Priority/Confidence/Awareness columns or map report priority into
  a local severity column. It updates only existing semantically equivalent
  fields on touched rows; schema migration remains a separate owner decision.
- Gives beginner explanations for rows marked `unknown_unknown`,
  `unconfirmed`, or `미확인`: what the item means, why it matters, the
  choices, and the recommendation.
- HTML board items include the actual ledger-row summary plus a plain
  explanation, so the owner can understand each item without opening the
  ledger beside the board.
- Removing `draftOnly` without rewriting every generated explanation,
  importance note, and group summary is blocked before HTML creation.
- HTML board separates source metadata from content: source position such
  as `Findings/BS-.../pending` is small metadata, while the main item text
  contains only the issue or decision itself.
- HTML board options are long, scan-friendly rows with plain tradeoffs in
  the owner's language, not compact cards that rely on internal labels.
- User-facing labels, explanations, and option text avoid unexplained
  shorthand such as CTA, AJAX, ARIA, and `prefers-reduced-motion`; if a
  technical term is unavoidable, it is explained in the owner's language.
- Uses the host's structured choice tool on choice-capable hosts, splitting
  batches if the option cap would be exceeded.
- On no-choice file-writing hosts, generates an HTML board under
  `.blindspot-tmp/ledger-triage-*` before applying ledger decisions, rather
  than printing a giant decision packet in chat or deciding outcomes itself.
- Validates `blindspot-triage-response.json` before changing the ledger.
- After validation, routes the selected response through the post-response
  workflow before touching the ledger: `needs_reexplain` first,
  ledger-only choices directly, and implementation-heavy choices through a
  temporary execution plan.
- Applies only selected/touched rows and writes an Audit Log row with
  `mode: ledger-triage`, board id or choice path, decisions applied, and
  cleanup result.
- Allows partial HTML submission; rows the owner did not select are omitted
  from the response and remain unchanged.
- If any selected row asks for simpler explanation, keeps all other selected
  choices saved in the response JSON but does not apply them or cleanup the
  board until the owner has received the explanation and chooses to continue.
- When selected choices imply code/docs/config/UI/data/runbook changes or
  other multi-step work, creates a temporary execution plan under the board
  directory, uses it while working, deletes it after implementation or after
  recording a blocker, and preserves only the concise choice/result summary
  in the ledger.
- Treats `quick_cleanup` and `safe_accept` as recommendations awaiting
  owner approval, not as permission for the agent to mark rows accepted,
  deferred, resolved, or rejected.
- Cleans up the temporary board only after decisions are applied and only
  through the helper safety checks.
- Keeps `needs_reexplain` rows open and answers them more simply instead
  of changing their status.
- When the ledger already has staged or unstaged owner edits, captures the
  owning-repo status and target baselines, patches only selected rows/log
  entries, and verifies that every prior hunk and unrelated dirty file remains.

## Fail Criteria

- Reports new blindspot findings unrelated to ledger maintenance.
- Treats `EXPECTED.md` as project evidence.
- Prints one long list of 20+ owner questions when file writes are available.
- Applies ledger edits before validating the response JSON.
- Applies non-reexplain decisions before explaining any selected
  `needs_reexplain` row.
- Starts implementation-heavy selected work without a temporary execution
  plan, leaves that plan behind afterward, or records the whole temporary
  plan as durable ledger content.
- Applies any status, awareness, archive, or decision-packet change before
  the owner chooses through a structured choice answer, validated HTML board
  response, or explicit reply.
- Generates an HTML board that only shows IDs, terse titles, or raw
  recommendations, forcing the owner to open the ledger to understand the
  item.
- Deletes the draft marker while leaving helper-generated scaffold explanations
  unchanged, then creates the owner board anyway.
- Repeats wrapper phrases like "Findings has ... BS-123 pending" as the
  main item content instead of separating row location from row content.
- Shows raw internal enum text such as `accepted`, `resolved_candidate`, or
  `unknown_unknown` as the primary user-facing explanation for a non-English
  owner.
- Uses unexplained acronyms or imported specialist terms as visible labels
  or recommendations for a non-specialist owner.
- Requires every item to be selected before submit or treats unselected rows
  as decisions.
- Treats "organize/clean up/proceed with ledger decisions" as permission to
  decide rows itself.
- Deletes `.blindspot-tmp` before decisions were applied, or deletes a path
  without the marker/path checks.
- Moves `resolved_candidate` rows to the archive without response evidence
  or a cheap verification.
- Normalizes the whole ledger to English statuses or renumbers IDs.
- Adds canonical report columns to the localized ledger or mixes
  `now/next/later/watch` into a severity column without owner approval.
- Rewrites a dirty ledger or cannot distinguish and preserve pre-existing
  staged/unstaged changes before applying selected decisions.
