# Report Template

Use a compact answer-first shape. Write the report in the language the owner
is using in conversation; keep IDs, status, and awareness values in English.
The owner's conversation language wins even when every file read during the
audit is in another language - do not let source-file language leak into the
report. (Field data: an audit over an all-English repo replied to a Korean
owner in English.)
The two trust sections ("Checked and well covered", "Skippable for now") are
not optional - they are how the owner learns the report can be trusted, and
they prevent the next audit from rescanning settled ground.

```markdown
**Blindspot Audit**

Scope: <project/path + mode (+ focus/<domain> when narrowed) + what was
inspected + scans applied this run (external-change / peer expectation /
context intake / focus packs) + any coverage debt cleared (scans or packs
that had never run on this project before) + descent step taken, when a
zero-delta run went deeper under ledger-lifecycle.md Diff Runs rules>
Project shape: <archetype(s), stage, owner profile, assumptions>
Ledger: <created path | read path | proposed path only> + <new/changed/confirmed/downgraded/resolved counts>
Audit run: <BA-YYYYMMDD-NN when durable Audit Evidence is used>
Durability: <tracked | owner-approved-local-only | untracked-pending | not-versioned> - <what the owner must do next, if anything>

Security priority snapshot (focus/security with 5-7 findings only):
- now: <N> - <largest immediate consequence in one sentence>
- next: <N> - <gate to close before the next exposure/stage>
- verified controls: <one important boundary already working>

Top blind spots (3-7):

1. <finding title - everyday words for what can happen, not the technical
   term for it>
   - In plain terms: <one or two sentences a newcomer to this domain would
     understand: what the thing IS, anchored to something familiar. Include
     whenever the finding sits outside the owner's expert areas; omit for
     findings squarely inside their expertise>
   - Why it matters: <project-specific consequence, not a generic rule>
   - Evidence: <observed | absent | inferred | question> <file/path or note;
     source links for external claims>
   - Cheapest check: <small command, file read, prototype, question, or test>
   - Priority: now | next | later | watch
   - Confidence: high | medium | low
   - Awareness: unknown_unknown | unknown_known | unconfirmed
   - Disposition: pending | accepted | deferred | deliberate_skip | rejected | resolved
   - Owner / next action: <who acts next + plain action; keep internal routes
     such as owner_followup out of the disposition field>
   - Secret closure: <when applicable only: current-tree / history-artifact /
     provider / downstream + overall; keep independent>

2. ...

Checked and well covered:
- <what exists and is healthy, with evidence - give real credit>

Skippable for now:
- <item> - <reason> - re-check when: <trigger>

Interview:
- <the awareness questions, or the classified results once answered>

Awareness check:
- <FALLBACK ONLY - include when no structured choice tool is callable in the
  current mode; on callable-now hosts run the multi-select interview through the tool
  instead and omit this section entirely>
- <ask for finding numbers the owner already knew; do not require internal labels>

Context check:
- <include only when project context is missing or stale AND no structured
  choice UI; compact numbered questions (C1, C2...), every one skippable
  with "pass" - a skip keeps the labeled assumption and is not re-asked>

Known unknowns to ask next:
- <one question whose answer changes architecture/scope/risk>

Lower-signal watchlist:
- <short bullets, optional - overflow beyond the 3-7 cap goes here>

Decision packet:
- <optional: decisions that could not be asked interactively>

Ledger delta:
- new: <ids/titles>
- changed: <ids/titles>
- confirmed: <ids/titles>
- downgraded/resolved: <ids/titles>
- unchanged omitted: <count when the owner requested delta-only reporting;
  do not repeat those finding bodies>
```

## Focus/Security Two-Layer Output

When the complete finding records were written to a durable ledger, the chat
report may replace repeated full metadata blocks with the security pack's
self-contained compact table. Group rows by the action they imply, not by
unexplained technical categories. Every row still states the everyday
consequence and cheapest next check; a bare ID/title is not enough. The
awareness interview follows the visible compact rows.

Do not use the compact form when the ledger was not updated, the host is
read-only/chat-only, or the owner would need to open another file to understand
the finding. In those cases, keep the complete finding blocks in chat.

## Canonical Values

`Priority`, `Confidence`, `Awareness`, and `Disposition` take exactly the
listed values in the REPORT, in English, whatever language the rest of the
report is written in - one value per finding, never ranges and never localized placeholders. (Field
data: a run emitted `now~next` and a localized "will ask" awareness
value; both break ledger diffing across sessions and languages.)

Before the awareness interview has actually happened, `Awareness` is
always `unconfirmed`. Do not pre-fill guesses on callable-now hosts -
a wrong pre-label anchors the owner (field data: a finding pre-labeled
`unknown_known` turned out to be `unknown_unknown` at interview).
Before the owner makes an implementation decision, `Disposition` is
`pending`. Timing language changes disposition, not awareness.

The report schema does not force a ledger schema migration. Existing ledgers
use the adapter in `references/ledger-lifecycle.md`; priority and severity are
not assumed equivalent.

External sources cited in the report keep the source tiers separated
(primary sources vs community leads - `audit-workflow.md` section 5), and
category-expectation findings name the actual peers walked.

## Post-Interview Mapping

Parse awareness and implementation disposition as independent axes. One owner
sentence may update either or both:

| Owner reply | Awareness result | Disposition result |
| --- | --- | --- |
| "I did not know any of these" | all `unknown_unknown` | unchanged (`pending` unless separately stated) |
| "I knew all of these" | all `unknown_known` unless already documented | unchanged |
| "Handle these together later" | unchanged | `deferred` with batch/re-check note |
| "I did not know; handle them together later" | `unknown_unknown` | `deferred` |
| "I intentionally will not do this" | keep stated/previous awareness | `deliberate_skip` with reason + re-check trigger |
| "This is already in the docs" | no new awareness enum; merge with the known item or reject the duplicate | preserve existing local decision, or resolve/reject with evidence |
| "This is not true / does not apply" | preserve as correction context | `rejected` or `resolved` with evidence note |
| "I do not understand this" | `unconfirmed` | unchanged until re-explained |

Apply mixed replies deterministically:

1. Apply an all-findings awareness clause to every referenced finding.
2. Apply numbered/ranged disposition clauses only to those finding numbers.
3. A more specific numbered clause overrides a broader disposition clause for
   that item; it never changes the item's awareness by itself.
4. Keep disposition unchanged for items omitted from every disposition clause.
5. Store `owner_followup`, `agent_work`, or `external_confirmation` as an
   internal next-action route plus a plain owner-facing action, never as a new
   disposition enum.

Example: "I did not know any. Put 1-4 in the next security batch, and I will
check the provider connection for 5." maps all five to awareness
`unknown_unknown`; 1-4 to disposition `deferred` with one batch link; and 5 to
disposition `accepted`, route `owner_followup`, next action "check connector
presence, authentication, and current callability." Do not apply the batch
disposition or link to 5.

After a reply, update the finding awareness, local decision/status, Audit Log
owner-response note, and future re-report behavior. `pending`, `accepted`, and
`deferred` rows remain open but are not re-raised as new; `deliberate_skip`
returns only at its trigger; merged, rejected, and resolved items are not
re-reported unless evidence changes.

Before those edits, encode the semantic mapping as individual
`blindspot-owner-response.v1` decisions or grouped v2 decisions and show the
Existing Ledger Write Guard preview from
`references/owner-response-guard.md`. The helper validates structure and
conflicts; it does not parse the owner's natural language. Apply only the
previewed IDs, leave omitted IDs unchanged, and require final validation to
compare those decisions with the actual ledger cells or archive destinations.

For `focus/security`, an explicit decision to handle two or more findings in
one later batch also creates the lightweight durable handoff defined by
`templates/SECURITY_BATCH_PLAN.md`, when the host can write files. Link it from
the ledger; do not route this owner decision through ledger-triage or a
temporary implementation plan. A vague "later" or one deferred item does not
create another document.

Legacy ledgers may contain `deliberate_skip` in an Awareness column. Read it as
a historical combined value and preserve it untouched; write new decisions on
the separate disposition/local-status axis rather than mass-migrating history.

## Ledger-Triage Output

Use this compact shape for `mode: ledger-triage` instead of the normal
blindspot report. Do not include top new findings. Before owner choices are
collected, report the decision board or packet and state that the ledger has
not been changed.

```markdown
**Ledger Triage**

Ledger: <path>
Mode: ledger-triage
Decision collection: <structured choice | HTML board path/id | numbered reply>
Ledger edits: <none yet - waiting for owner choices | applied after validated response>

Grouped items:
- quick_cleanup: <count + IDs>
- safe_accept: <count + IDs>
- decision_bundle: <count + IDs>
- needs_owner_detail: <count + IDs>
- needs_external_confirmation: <count + IDs>
- needs_reexplain: <count + IDs>

Recommended decisions waiting for owner:
- <ID>: recommended <action> - <plain tradeoff>

Applied decisions:
- <only after owner choice/validated response: ID -> action/status result>

Needs simpler explanation:
- <ID>: <plain-language follow-up, status unchanged>

Temp cleanup:
- <not used | cleaned <board id> | kept because <reason>>
```

## Tone

- Be direct and calm. The audit should leave the owner calmer, not more
  anxious - knowing what to ignore is half the value.
- Prefer "this may be missing" over "this is broken" unless verified.
- Teach unfamiliar concepts briefly when the user may not know the domain.
- For legal/tax/regulatory items, name the source and say a professional
  must confirm - the audit is a scout, not a lawyer.
- Stop at the current decision point. Do not force implementation unless
  asked.

## Writing Findings The Owner Can Actually Recognize

Unknown-unknown findings are, by definition, about things the owner may
never have encountered. A jargon title does not convert the unknown - it
just renames it, and the owner cannot even classify it in the interview.
The test for every finding: could the owner retell it to a friend after one
read? This principle is language-independent - apply it in whatever
language the owner speaks.

- Title = the everyday-words consequence, not the mechanism's proper name.
- First use of an unavoidable term gets a one-line "which is..." definition.
- Anchor to something the owner already knows (a familiar checkbox form, a
  store listing they have seen, a backup they already make).
- Scale to the owner profile: a payments expert does not need "MoR" spelled
  out; a first-time indie dev does.
- Category expectation gaps (peer expectation scan) name the peers checked
  and phrase the cheapest check as a decision - "peers X, Y, Z all have
  reading history; decide to add it or skip it on record" - never as a
  feature order.

Example (from a real run - a solo dev new to shipping, Unity game headed
to Steam):

Weak - renamed unknown, owner cannot classify it:

```markdown
1. No Steam AI content disclosure matrix for the local-embedding pipeline.
```

Strong - same finding, recognizable on first read:

```markdown
1. Steam will ask "did you use AI to make this game?" and we have no
   prepared answer
   - In plain terms: when you submit a game, Steam shows a short required
     form asking whether AI was used to create content players see, and how.
     Your store page displays part of the answer. It is a set of checkboxes,
     not a legal document - but a wrong or missing answer can delay review.
   - Why it matters: this project generates some player-visible content
     with a local AI model, which is exactly what the form asks about.
   - Cheapest check: read Steam's AI disclosure questions once (5 minutes)
     and note the intended answers in the GDD.
```

## No Structured Choice UI

When the host cannot present a choice question, do not stop the audit just
to ask what the owner already knew. Return the report with `Awareness:
unconfirmed` on each finding and place the numbered awareness check as the
report's FINAL element - a closing question is what invites a reply, and a
first-time user who never answers leaves every finding `unconfirmed`
forever.

The check is a template, not a suggestion to paraphrase (field data: a
run once compressed it to "tell me the ledger IDs you knew, later" - the
natural reply rate of that sentence is zero). Include all of:

- The report's finding NUMBERS (1, 2, 3) - never ledger IDs and never
  internal labels like `unknown_known`.
- Reply examples in the owner's language, including the qualifier forms
  and the number-plus-question-mark path.
- One motivation line: answering is optional, but classified findings
  stop being re-raised as new by future audits.

Use the owner's language, but keep Arabic numerals from the report because
they are compact and work across languages.

Suggested English prompt:

```markdown
Awareness check:
Reply with the numbers you already knew. Omitted numbers stay classified as
newly surfaced by this audit.

Examples: `1, 3`, `I already knew 1 and 3`, `I did not know any`, or `I knew all`

Optional: say `2 is already in docs`, `4 was new to me; handle it in the
next security batch`, `6 is deliberately skipped because this stays offline`,
or `5 is wrong` when that applies. If a finding is unclear, reply with its
number and a question mark (`3?`) and I will re-explain it more simply.

Answering is optional - the audit stands either way - but whatever you
classify will not be re-raised as new by future audits.
```

Suggested Korean prompt:

```markdown
인지 확인:
이미 알고 있던 항목 번호만 답해주세요. 적지 않은 번호는 이번 audit에서 새로 드러난 항목으로 둡니다.

전체 답변 예:
- `다 몰랐어`
- `다 알고 있었어`
- `1번과 3번만 알고 있었어`
- `다 몰랐고 다음 보안 정리 때 같이 처리`

특수한 경우: `2번은 문서에 있음`, `4번은 몰랐고 다음 보안 정리 때 같이 처리`,
`6번은 오프라인 전용이라 일부러 하지 않음`, `5번은 아님`
이해가 안 되는 항목은 `3번?`처럼 물음표를 붙여주시면 더 쉽게 다시 설명해 드립니다.

답하지 않아도 감사는 유효하지만, 답해주신 항목은 다음 감사가 새 발견처럼
다시 꺼내지 않습니다.
```

Interpret number-only replies as `unknown_known` and omitted numbers as
`unknown_unknown`. Documented/tracked replies are filtered, merged, or rejected
as duplicates; known known is a conceptual quadrant, not a stored awareness
enum. Later/batched replies set disposition `deferred` without
changing awareness; only an explicit decision not to act sets disposition
`deliberate_skip` with a reason and trigger. Wrong items become
rejected/resolved. A number with a question mark (`3?`, `3번?`,
"what is 3") means the finding was not understood: re-explain it more
simply (SKILL.md Core Invariant 5), keep it `unconfirmed`, and only classify after the
owner responds to the plainer version. If the owner later replies, update
awareness and disposition through the local ledger adapter, record the
owner-response Audit Log note, and report only that delta.

Treat these phrases as semantic examples for the agent, not parser keywords.
Equivalent wording in every owner language has the same meaning. A global
awareness clause applies to all findings, while a numbered disposition clause
changes only those numbers. For example, "I did not know any; handle 1 and 3
later" means all findings are `unknown_unknown`, while only 1 and 3 become
`deferred`.
