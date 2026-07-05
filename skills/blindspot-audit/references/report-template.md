# Report Template

Use a compact answer-first shape. Write the report in the language the owner
is using in conversation; keep IDs, status, and awareness values in English.
The two trust sections ("Checked and well covered", "Skippable for now") are
not optional — they are how the owner learns the report can be trusted, and
they prevent the next audit from rescanning settled ground.

```markdown
**Blindspot Audit**

Scope: <project/path + mode + what was inspected + whether the fresh-eyes
web scan ran>
Project shape: <archetype(s), stage, owner profile, assumptions>
Ledger: <created path | read path | proposed path only> + <new/changed/confirmed/downgraded/resolved counts>

Top blind spots (3–7):

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
- <what exists and is healthy, with evidence — give real credit>

Skippable for now:
- <item> — <reason> — re-check when: <trigger>

Interview:
- <the awareness questions, or the classified results once answered>

Known unknowns to ask next:
- <one question whose answer changes architecture/scope/risk>

Lower-signal watchlist:
- <short bullets, optional — overflow beyond the 3–7 cap goes here>

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
  anxious — knowing what to ignore is half the value.
- Prefer "this may be missing" over "this is broken" unless verified.
- Teach unfamiliar concepts briefly when the user may not know the domain.
- For legal/tax/regulatory items, name the source and say a professional
  must confirm — the audit is a scout, not a lawyer.
- Stop at the current decision point. Do not force implementation unless
  asked.
