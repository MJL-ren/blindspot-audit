# Host Surface Adapters

Use this reference when the same blindspot audit should run across AI coding
hosts, desktop apps, CLI tools, API-backed agents, or plain chat.

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
- When the host cannot present a structured choice UI, finish the audit
  anyway and include a numbered awareness check the owner can answer later.
- When running `mode: ledger-triage`, collect decisions through the host's
  structured choice UI when available; otherwise use a temporary HTML
  decision board before applying ledger changes. Never treat a cleanup
  request as permission for the agent to choose statuses itself.
- Keep a durable ledger when the host can write files and the user has not
  requested read-only/chat-only output.

## Structured Choice Tool Adapter

Use this adapter for hosts that provide a structured choice/question tool
such as `AskUserQuestion`, `question`, or an equivalent UI-native selector.
Claude Code and OpenCode commonly fit this category.

Use the tool sparingly:

1. Ask only questions whose answer changes audit scope, architecture,
   workflow, or risk - plus the owner-awareness interview (one multi-select
   question listing the top findings works well) and, on first runs, the
   Project context intake (one or two compact questions BEFORE evidence
   gathering; every option set includes a "prefer not to say / just infer
   it" path, and a skip is recorded as a labeled assumption, never re-asked
   on later runs).
2. Offer 2-3 clear options, with the recommended option first.
   Option labels and descriptions follow the same plain-language rule as
   findings (SKILL.md Ground Rule 6): a label like "Steam AI disclosure
   matrix" is unclassifiable for an owner who has never seen the term -
   label by the everyday consequence ("Steam's AI question - no answer
   yet") and put the one-line explanation in the option description.
3. Mind the option cap: structured choice tools usually limit options per
   question (Claude Code's `AskUserQuestion` caps at 4, plus a built-in
   "Other"). With 5-7 findings, never silently drop the overflow - either
   split the awareness interview into two questions, or ask about the top 4
   and cover the rest with a numbered awareness check in the report. A UI
   limit must not shrink the audit. (Field data: a 5th finding once went
   uninterviewed exactly this way.)
4. Record the selected option in the report or ledger.
5. Continue after the answer; do not ask a series of preference questions
   that only refine wording.
6. The numbered awareness check (see the no-choice adapter) is a FALLBACK
   for hosts without this tool. If the tool exists, use it for the
   awareness interview, the context intake, and the single highest-value
   known-unknown question - and leave the numbered check out of the
   report entirely. (Field data: a choice-capable run once shipped the
   numbered fallback instead of asking through the tool; the concrete
   template below exists so the tool path is never the vaguer option.)
   Interview shape: one multiSelect question - "Which of these did you
   already know about?" - with one option per finding, labeled by the
   finding's short consequence title; "already in docs", "deliberately
   skipped", and "wrong" corrections arrive through the built-in Other
   path. Mind the option cap from rule 3.

Good structured-choice output: same findings as the shared core, a decision
log when interactive choices were used, awareness classifications from the
interview, ledger updates that preserve IDs and status language.

## Cowork (Claude Desktop App) Adapter

Cowork runs the same interactive flow as the structured choice adapter
(`AskUserQuestion` is available; use it the same way). Two environment
quirks change HOW to gather evidence:

- The installed plugin folder is usually NOT reachable from the shell
  sandbox. To run `scripts/project_inventory.py`, copy the script into the
  session workspace with the file tools first (read from the skill folder,
  write next to the outputs), then run the copy.
- The shell sandbox works on a synced mirror of the user's folders, while
  the file tools read the real files. On a folder attached mid-session the
  mirror can lag or even truncate file contents. If shell output (`wc`,
  `diff`, `git status`) disagrees with a file-tool read, trust the file
  tools, re-verify, and say which view each claim came from. Never run
  destructive git commands (restore/checkout/clean) from the shell against
  a folder whose mirror freshness has not been verified.
- Prefer file tools for all writes (ledger, routing edits). Treat the
  mirror's `.git` as read-only and untrusted: `git log/status/diff` are fine
  for evidence (cross-check surprises against file tools), but do not run
  `git add/commit/restore` from the sandbox - a stale mirror can present a
  corrupt index (observed in the field: "bad signature 0x00000000"). Hand
  the user a copy-paste command block to commit on their machine instead -
  or, if a real-machine executor MCP (e.g. Desktop Commander) is connected,
  run the git commands through it: it uses the user's real files and git
  identity. Note that a failed sandbox git write can leave a stale
  `index.lock` that syncs to the user's real repo and blocks their git;
  if that happens, verify no live git process exists, then remove the
  0-byte lock file.
- Sync lag corrupts commits QUIETLY, in both directions (observed in the
  field, twice in one day). Mirror-side: after file-tool edits, the
  sandbox's `git status`/`git diff HEAD` can claim modified files are
  clean while their contents clearly differ from HEAD - never conclude
  "no changes" from mirror git alone; compare actual contents. Owner-side:
  a file just written in the session (especially a rebuilt binary
  artifact, e.g. a packaged `.skill`) may reach the owner's disk late, so
  their `git add -A` commits new sources with a stale artifact - CI caught
  exactly this mismatch once. Therefore owner-facing commit blocks must
  list the EXACT expected files and require `git status --short` to match
  that list before committing; a missing file means stale index or
  unfinished sync - wait a moment, run `git update-index --really-refresh`,
  and re-check rather than committing blind. For DERIVED artifacts
  (packaged skills, synced copies, built bundles) the only reliable cure
  is not to build them in the session at all: a build can snapshot a
  truncated mirror file, and an in-session verify then blesses the
  corrupted artifact by comparing it against the same corrupted view
  (observed: a packaged file cut off mid-word passed in-session
  verification and failed only in CI). Have the owner regenerate derived
  artifacts on their machine with the project's own build scripts and run
  the verify scripts there, immediately before committing.

## No Structured Choice Tool Adapter

Use this adapter for hosts that can write, inspect, and chat, but cannot
reliably present a UI-native multiple-choice question during normal work.
This includes many CLI, API, and chat-backed coding surfaces.

Use an assumption-first, two-phase flow:

1. Continue with the safest reversible assumption.
2. Mark assumptions in the report.
3. Mark top-finding awareness values `unconfirmed`.
4. Include a numbered awareness check so the owner can classify findings in
   one later message without learning the internal taxonomy.
5. Put unresolved architecture, scope, cost, legal, or destructive choices in
   a `Decision packet`.
6. Ask the user directly only when the answer blocks safe progress or a
   wrong assumption would make the audit misleading.
7. If web access is unavailable, skip the fresh-eyes scan, say so, and mark
   time-sensitive claims (regulation, platform policy, pricing) unverified.

Good no-choice output: compact ranked findings, evidence links or file
paths, `new/changed/confirmed/downgraded/resolved` labels when a ledger
exists, a short list of exact next checks, the ledger path if one was
created or updated, and the numbered awareness check as the report's
FINAL element - reproduced faithfully from
`references/report-template.md` (report finding numbers, reply examples,
qualifier forms, the `3?` path, and the one-line motivation), never
compressed into a passing sentence and never keyed to ledger IDs:

```markdown
Awareness check:
Reply with the numbers you already knew. Omitted numbers stay classified as
newly surfaced by this audit.

Examples:
- English: `1, 3` or `I already knew 1 and 3`
- Korean: `1번, 3번 알고 있어`

Optional qualifiers:
- `2 is already in docs/roadmap.md`
- `4 is intentionally deferred until launch`
- `5 is wrong`
```

Interpret replies generously:

- Numbers only, or "I knew/already knew <numbers>" -> `unknown_known`.
- Omitted numbers -> `unknown_unknown`.
- Already documented, tracked, implemented, or in code -> `known_known` or
  downgraded/resolved, and do not re-report as a discovery.
- Intentionally deferred/skipped/postponed -> `deliberate_skip` with the
  stated reason or trigger.
- Wrong/not true/not applicable -> rejected/resolved with a correction note.
- Number plus question mark (`3?`, `3번?`, "what is 3") -> the owner did not
  understand the finding. Re-explain it in plainer terms (SKILL.md Ground
  Rule 6), keep awareness `unconfirmed`, and classify only after they
  respond to the plainer version. Do not count "I don't understand it" as
  "I didn't know about it".

If the owner replies with classifications, update the ledger and report only
the delta. Do not rerun the whole audit unless the reply changes scope or
evidence.

### Ledger-Triage Decision Boards

In `mode: ledger-triage`, a long numbered reply can become too much for the
owner. When the host can write files and there is any meaningful ledger
decision to apply, create a temporary HTML decision board instead of editing
the ledger from the agent's own judgment:

- Put it under `<project-root>/.blindspot-tmp/ledger-triage-*`, never in
  docs and never in commit scope.
- Generate it with `scripts/ledger_triage_board.py create`; serve it on
  `127.0.0.1` with the helper when localhost is available.
- If serving is impossible, the static HTML downloads or displays
  `blindspot-triage-response.json`. Do not ask the owner to move files by
  hand; have them leave the downloaded JSON in Downloads or the browser's
  chosen folder, then run `validate --collect-response`, `validate
  --response <path>`, or `collect-response` as described in
  `references/ledger-triage.md`.
- Present recommendations in the board. A recommended option is not
  authorization to apply it.
- Run the helper's `validate` command before applying any ledger change.
- Apply only the touched rows, preserving the ledger's local status labels.
- Add one Audit Log row noting `mode: ledger-triage`, board id, decisions
  applied, and cleanup result.
- Delete the board directory only with the helper's `cleanup
  --confirm-applied` after decisions were applied.

Use the normal numbered reply fallback only for read-only/chat-only hosts,
or when the owner explicitly asks not to create temporary HTML files. In
that fallback, do not edit the ledger until the owner replies with the
chosen numbers/options.

When project context is missing or stale (no usable `Project Context`
section in the ledger), append a compact numbered Context check after the
awareness check, answerable in the same single reply. Keep it optional and
obviously skippable - some owners do not want to state intent, audience,
or personal detail, and that choice is respected:

```markdown
Context check (optional - answer any, skip any, or reply "pass"):
C1. Public, commercial, or private project? (current assumption: <assumption>)
C2. Who is it for, and in which regions?
C3. Any deadline or launch window?
C4. Anything I should not search for on the web? (default: category-only,
    no private names)
```

Unanswered or passed items keep their labeled assumptions and are recorded
in the ledger's Project Context section as `skipped (assumption: ...)` -
they are not re-asked on later runs unless the owner reopens them.

## Chat-Only Or Read-Only Adapter

- Chat-only (no file writes): return a portable report; include the
  proposed ledger path and its first entries inline so the user can paste
  them into the project.
- Read-only by user request: never write, even if the host can. Propose the
  ledger location and show the routing edit you would have made.
- Both: fold interview questions into the end of the report and mark
  awareness `unconfirmed`; use the numbered awareness check instead of a
  plain open-ended question.

## OS And Shell Notes

- Prefer the host's native file tools (Glob/Grep/Read or equivalents) over
  shell commands for discovery: they work identically across OSes and avoid
  quoting pitfalls. Shell commands like `rg` are the fallback, not the
  default.
- On Windows, `python` may not be on PATH while the `py` launcher is; try
  `py` if `python` fails. Always quote paths that may contain spaces
  (AppData paths usually do).
- Do not assume `bash` fences imply a POSIX shell; the same command may run
  under PowerShell. Keep commands single-line and quote-safe where possible.

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
