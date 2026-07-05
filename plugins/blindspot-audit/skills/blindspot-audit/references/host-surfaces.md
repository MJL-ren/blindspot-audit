# Host Surface Adapters

Use this reference when the same blindspot audit should run across Claude
Code, Codex, OpenCode, CLI tools, or plain chat.

## Shared Core

All hosts should do the same core work:

- Define scope, owner profile, and assumptions.
- Inspect project evidence before ranking findings.
- Separate observed facts, absences, inferences, and questions.
- Filter out anything the project's own tracking docs already cover.
- Run the fresh-eyes external scan when web access exists; disclose when it
  does not.
- Convert each blind spot into the cheapest next check.
- Interview the owner about awareness when the host allows it.
- Keep a durable ledger when the host can write files and the user has not
  requested read-only/chat-only output.

## Claude Code Adapter

The `AskUserQuestion` tool shows interactive choice questions. Use it
sparingly:

1. Ask only questions whose answer changes audit scope, architecture,
   workflow, or risk - plus the owner-awareness interview (one multi-select
   question listing the top findings works well).
2. Offer 2-3 clear options, with the recommended option first.
3. Record the selected option in the report or ledger.
4. Continue after the answer; do not ask a series of preference questions
   that only refine wording.

Good Claude Code output: same findings as the shared core, a decision log
when interactive choices were used, awareness classifications from the
interview, ledger updates that preserve IDs and status language.

## Codex Adapter

Codex often cannot show arbitrary multiple-choice questions during normal
work, and may run without web access. Use an assumption-first flow:

1. Continue with the safest reversible assumption.
2. Mark assumptions in the report.
3. Put unresolved choices in a `Decision packet` and mark awareness values
   `unconfirmed`.
4. Ask the user directly only when the answer blocks safe progress.
5. If web access is unavailable, skip the fresh-eyes scan, say so, and mark
   time-sensitive claims (regulation, platform policy, pricing) unverified.

Good Codex output: compact ranked findings, evidence links or file paths,
`new/changed/confirmed/downgraded/resolved` labels when a ledger exists, a
short list of exact next checks, and the ledger path if one was created.

## OpenCode Adapter

OpenCode provides a `question` tool for interactive choices - use it the
same way as the Claude Code adapter (options explicit, one question call at
a time). Notes:

- OpenCode discovers skills from `.opencode/skills/` and
  `~/.config/opencode/skills/`, and also reads Claude-compatible paths
  (`.claude/skills/`, `~/.claude/skills/`), so this skill may have arrived
  through either route - behavior is identical.
- Some OpenCode setups auto-continue when a turn looks unfinished; prefer
  the `question` tool over plain-text option lists so the user's choice is
  not skipped.

## Chat-Only Or Read-Only Adapter

- Chat-only (no file writes): return a portable report; include the
  proposed ledger path and its first entries inline so the user can paste
  them into the project.
- Read-only by user request: never write, even if the host can. Propose the
  ledger location and show the routing edit you would have made.
- Both: fold interview questions into the end of the report and mark
  awareness `unconfirmed`.

## Decision Packet Template

Use this when the host cannot ask interactive choices or when the user
asked for a non-blocking audit.

```markdown
Decision packet:

1. <decision title>
   Recommended: <option>
   Options:
   - <option A>: <tradeoff>
   - <option B>: <tradeoff>
   - <option C>: <tradeoff>
   Why it matters: <what changes if chosen>
```
