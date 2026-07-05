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

1. <finding title>
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
`5 is wrong` when that applies.
```

Suggested Korean prompt:

```markdown
인지 확인:
이미 알고 있던 항목 번호만 답해주세요. 적지 않은 번호는 이번 audit에서 새로 드러난 항목으로 둡니다.

예: `1번, 3번 알고 있어`

특수한 경우: `2번은 문서에 있음`, `4번은 일부러 보류`, `5번은 아님`
```

Interpret number-only replies as `unknown_known`, omitted numbers as
`unknown_unknown`, documented/tracked replies as `known_known` or
downgraded/resolved, intentional deferrals as `deliberate_skip`, and wrong
items as rejected/resolved. If the owner later replies, update the ledger
statuses/awareness values and report only that delta.
