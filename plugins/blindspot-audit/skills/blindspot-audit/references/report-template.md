# Report Template

Use a compact answer-first shape. Write the report in the language the owner
is using in conversation; keep IDs, status, and awareness values in English.
The two trust sections ("Checked and well covered", "Skippable for now") are
not optional - they are how the owner learns the report can be trusted, and
they prevent the next audit from rescanning settled ground.

```markdown
**Blindspot Audit**

Scope: <project/path + mode + what was inspected + whether the fresh-eyes
web scan ran>
Project shape: <archetype(s), stage, owner profile, assumptions>
Ledger: <created path | read path | proposed path only> + <new/changed/confirmed/downgraded/resolved counts>

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
   - Awareness: unknown_unknown | unknown_known | deliberate_skip | unconfirmed

2. ...

Checked and well covered:
- <what exists and is healthy, with evidence - give real credit>

Skippable for now:
- <item> - <reason> - re-check when: <trigger>

Interview:
- <the awareness questions, or the classified results once answered>

Awareness check:
- <include only when no structured choice UI was available>
- <ask for finding numbers the owner already knew; do not require internal labels>

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
unconfirmed` on each finding and include a short numbered awareness check.

Use the owner's language, but keep Arabic numerals from the report because
they are compact and work across languages. Do not require internal labels
like `unknown_known` from the owner.

Suggested English prompt:

```markdown
Awareness check:
Reply with the numbers you already knew. Omitted numbers stay classified as
newly surfaced by this audit.

Examples: `1, 3` or `I already knew 1 and 3`

Optional: say `2 is already in docs`, `4 is intentionally deferred`, or
`5 is wrong` when that applies. If a finding is unclear, reply with its
number and a question mark (`3?`) and I will re-explain it more simply.
```

Suggested Korean prompt:

```markdown
인지 확인:
이미 알고 있던 항목 번호만 답해주세요. 적지 않은 번호는 이번 audit에서 새로 드러난 항목으로 둡니다.

예: `1번, 3번 알고 있어`

특수한 경우: `2번은 문서에 있음`, `4번은 일부러 보류`, `5번은 아님`
이해가 안 되는 항목은 `3번?`처럼 물음표를 붙여주시면 더 쉽게 다시 설명해 드립니다.
```

Interpret number-only replies as `unknown_known`, omitted numbers as
`unknown_unknown`, documented/tracked replies as `known_known` or
downgraded/resolved, intentional deferrals as `deliberate_skip`, and wrong
items as rejected/resolved. A number with a question mark (`3?`, `3번?`,
"what is 3") means the finding was not understood: re-explain it more
simply (Ground Rule 6), keep it `unconfirmed`, and only classify after the
owner responds to the plainer version. If the owner later replies, update
the ledger statuses/awareness values and report only that delta.
