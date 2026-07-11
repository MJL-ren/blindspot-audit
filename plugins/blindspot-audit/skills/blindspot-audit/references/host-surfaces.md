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
- Interview the owner about awareness through a structured tool only when it is
  callable in the current host mode.
- When the host cannot present a structured choice UI, finish the audit
  anyway and include a numbered awareness check the owner can answer later.
- When running `mode: ledger-triage`, collect decisions through the host's
  structured choice UI only when it is `callable-now`; otherwise use a
  temporary HTML decision board before applying ledger changes. Never treat a
  cleanup request as permission for the agent to choose statuses itself.
- Keep a durable ledger when the host can write files and the user has not
  requested read-only/chat-only output.

## Capability Detection

Classify a structured-choice tool by CURRENT usability, not by whether its
definition appears somewhere in the host:

- `advertised`: the tool is listed or documented, but current-call permission
  is not established.
- `callable-now`: the tool can be invoked in the current host mode and turn.
- `mode-gated`: the tool exists but is restricted to another mode or workflow.
- `unavailable`: no structured choice tool exists.

Only `callable-now` makes the current run choice-capable. `advertised`,
`mode-gated`, and `unavailable` use the no-choice adapter for this run. Do not
make a speculative tool call merely to test availability; use the host's tool
metadata and active-mode instructions. Record the precise limitation in the
Audit Log, for example `structured choice unavailable in current host mode`,
instead of claiming the host has no structured UI at all.

## Structured Choice Tool Adapter

Use this adapter only when a structured choice/question tool such as
`AskUserQuestion`, `question`, or an equivalent UI-native selector is
`callable-now`. Claude Code and OpenCode commonly fit this category, but their
current mode still decides.

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
   findings (SKILL.md Core Invariant 5): a label like "Steam AI disclosure
   matrix" is unclassifiable for an owner who has never seen the term -
   label by the everyday consequence ("Steam's AI question - no answer
   yet") and put the one-line explanation in the option description.
3. Mind both caps in the callable tool schema: options per question and
   questions per call. In the tested Claude adapter, `AskUserQuestion` allows
   at most 4 questions per call and 4 options per question, plus a built-in
   "Other". With 5-7 findings, never silently drop the overflow - split the
   interview across questions/calls, or ask about the top 4 and cover the rest
   with a numbered awareness check in the report. A UI limit must not shrink
   the audit. Other hosts may expose different caps; obey the current callable
   schema rather than assuming Claude's numbers.
4. Record the selected option in the report or ledger.
5. Continue after the answer; do not ask a series of preference questions
   that only refine wording.
6. The numbered awareness check (see the no-choice adapter) is a FALLBACK
   for runs where this tool is not callable now. If it is callable now, use it for the
   awareness interview, the context intake, and the single highest-value
   known-unknown question - and leave the numbered check out of the
   report entirely. (Field data: a choice-capable run once shipped the
   numbered fallback instead of asking through the tool; the concrete
   template below exists so the tool path is never the vaguer option.)
   Interview order: present the findings in the owner-visible chat
   channel BEFORE asking - at least one plain-language line per finding.
   A report saved to a file does not count as "presented": the owner may
   meet the question before ever seeing the file. On hosts that compress
   narration between tool calls (Cowork), write that summary as ordinary
   owner-visible assistant prose immediately before the tool call, following
   the host adapter's same-turn sequencing, or the question arrives before
   any introduction the owner can actually see. (Field data: an
   owner once faced the interview cold and had to open the report file
   to decode the options.)
   Interview shape: one multiSelect question - "Which of these did you
   already know about?" - with one option per finding. Every option must
   pass the self-sufficiency test: an owner who has NOT read the report
   can still classify it from the option alone. Label = the finding's
   everyday-consequence phrase (what can happen, in the owner's words) -
   never a topic shorthand, internal term, or bare ID ("npx route"
   fails; "one-line install exists but the README never mentions it"
   passes). Description = one or two sentences saying what is missing
   and what happens if it stays missing, at the owner's level (SKILL.md Core
   Invariant 5). Assume the host may collapse or hide descriptions until
   interaction (observed on Cowork), so the label must carry the meaning
   alone; finding numbers may ride along as a cross-reference, never as
   the label's meaning. "Already in docs", "deliberately skipped", and
   "wrong" corrections arrive through the built-in Other path. Mind the
   option cap from rule 3.

Good structured-choice output: same findings as the shared core, a decision
log when interactive choices were used, awareness classifications from the
interview, ledger updates that preserve IDs and status language.

## Claude Code CLI Adapter

Claude Code normally has direct filesystem access to personal, project, and
plugin skills. Follow the shared structured-choice adapter, with these path and
execution rules:

- Bind `<skill>` to the active entrypoint's resolved `${CLAUDE_SKILL_DIR}`.
  Execute helpers directly from that folder and verify the requested script and
  `safe_output.py` exist beside each other. Never choose among source, plugin,
  or installed copies by grepping for a helper filename.
- Do not apply the Cowork copy/mirror workaround in a normal local CLI session.
  If the current Claude Code environment actually exposes a synchronized or
  remote mirror, classify that observed capability and use the matching
  sandbox rules instead of assuming local access.
- An invocation with no mode arguments uses `normal`. A named path narrows the
  scope; it does not silently change the depth.
- Use `AskUserQuestion` whenever it is callable now. Present findings in normal
  assistant prose and invoke the question immediately afterward in the same
  turn. In `ledger-triage`, use bundled structured questions and do not load the
  HTML-board reference.
- Shell permission prompts do not authorize combining or skipping lifecycle
  phases. Run each documented snapshot, validation, and cleanup phase with its
  matching flag. Do not add broad permission bypasses merely to reduce prompts.
- Use the HTML board only when structured choice is unavailable now or the
  owner explicitly selects the board for a large independent decision set. If
  serving is needed, use the host's background-process support and the helper's
  `--write-url`/`--write-board-dir` outputs rather than blocking the session on
  a foreground server.

## Cowork (Claude Desktop App) Adapter

Cowork runs the same interactive flow as the structured choice adapter when
`AskUserQuestion` is callable in the active mode. In
`mode: ledger-triage`, use `AskUserQuestion` with the batching scheme in
`references/ledger-triage.md` and strongly prefer it over the HTML board:
the board fits Cowork poorly because the shell sandbox cannot serve a
`localhost` the owner's browser can reach, and the owner's Downloads are not
mounted. If a board is truly unavoidable, present the HTML with the file
view (`present_files`) so it opens on the owner's machine, then have them
drop the response JSON into a mounted path and validate it explicitly with
`validate --board-dir "<board-dir>" --response "<mounted-response-json>"`.
Do not rely on default Downloads collection in Cowork because Downloads is not
mounted into its sandbox.

One interaction quirk changes how the interview is delivered: narration
written between tool calls may be summarized away from the owner. Write the
findings in normal owner-visible assistant prose, then immediately invoke
`AskUserQuestion` after that prose in the **same turn**. Do not end the turn,
promise to ask next time, or wait for another owner message. Cowork renders the prose
before the choice UI when they are emitted in that order. Do not search for or
invent a special message tool that the host does not expose.

Two environment quirks change HOW to gather evidence:

- The installed plugin folder is usually NOT reachable from the shell
  sandbox. To run a packaged executable helper, copy that script **and its
  required companion `safe_output.py`** into the same session-workspace
  directory with file tools, then run the copied helper. This applies to
  `project_inventory.py`, `audit_followup_guard.py`,
  `ledger_triage_board.py`, and `secret_presence_scan.py`. Copying only the
  executable helper is an incomplete installation and must fail with a clear
  companion-file message. For a byte-stable shell handoff, use file tools to
  write both files through Cowork's mounted outputs/session-files area, then
  execute the mounted copies. Do not copy from a stale project mirror or
  reconstruct a helper by pasting text; compare byte size or hash when the host
  exposes both views.
- The shell sandbox works on a synced mirror of the user's folders, while
  the file tools read the real files. On a folder attached mid-session the
  mirror can lag or even truncate file contents. If shell output (`wc`,
  `diff`, `git status`) disagrees with a file-tool read, trust the file
  tools, re-verify, and say which view each claim came from. Never run
  destructive git commands (restore/checkout/clean) from the shell against
  a folder whose mirror freshness has not been verified.
- A mirrored file can end mid-sentence or produce false syntax/test failures.
  Before promoting any shell-observed absence, truncation, corruption, parse
  error, or test failure to a project finding, re-read the exact source with a
  file tool. If the file-tool copy is intact, record a Cowork mirror limitation,
  exclude the shell result from project evidence, and do not report a project
  defect from it.
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

Use this adapter for hosts that can write, inspect, and chat, but do not have a
UI-native multiple-choice question callable in the current mode. This includes
many CLI, API, chat-backed, and mode-gated coding surfaces.

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
- English: `I did not know any`, `I knew all`, or `I already knew 1 and 3`
- Korean: `다 몰랐어`, `다 알고 있었어`, `1번과 3번만 알고 있었어`, or
  `다 몰랐고 다음 보안 정리 때 같이 처리`

Optional qualifiers:
- `2 is already in docs/roadmap.md`
- `4 was new to me; handle it in the next security batch`
- `6 is deliberately skipped because this stays offline`
- `5 is wrong`
```

Interpret replies generously:

- A global all/none awareness statement applies to every finding.
- Numbers only, or "I knew/already knew <numbers>" -> `unknown_known`.
- Omitted numbers -> `unknown_unknown`.
- Already documented or tracked -> treat it as a known-work filter result:
  merge with the existing item or reject the duplicate, and do not invent a
  fourth stored awareness value. Already implemented -> verify the evidence
  and resolve/reject as appropriate. Preserve the existing awareness value
  unless the owner separately states whether they knew.
- Later/batched/postponed -> disposition `deferred`; do not change awareness
  unless the same reply also says whether the owner knew.
- Intentionally declined/will not do -> disposition `deliberate_skip` with
  the stated reason and re-check trigger.
- Wrong/not true/not applicable -> rejected/resolved with a correction note.
- Number plus question mark (`3?`, `3번?`, "what is 3") -> the owner did not
  understand the finding. Re-explain it in plainer terms (SKILL.md Core
  Invariant 5), keep awareness `unconfirmed`, and classify only after they
  respond to the plainer version. Do not count "I don't understand it" as
  "I didn't know about it".

Interpret meaning in the owner's language; do not keyword-parse these example
phrases. Apply global awareness and numbered dispositions independently. For
example, "I did not know any; defer 1 and 3" classifies every finding as
`unknown_unknown` and changes only 1 and 3 to `deferred`.

If the owner replies with classifications, update awareness and disposition
independently, adapt them to the local ledger schema, add an Audit Log
owner-response note, and report only the delta. Do not rerun the whole audit
unless the reply changes scope or evidence.

### Ledger-Triage Decision Boards

In `mode: ledger-triage`, decisions go through the host's native UI in
precedence order: a `callable-now` structured choice tool first (see
the Structured Choice Tool Adapter above and the batching scheme in
`references/ledger-triage.md`); then, on a file-writing host with no choice
tool callable now, a temporary HTML decision board; then a numbered reply for
read-only/chat-only hosts. When the board is selected, read
`references/ledger-triage-board.md` and follow its complete create, serve,
response, application, and cleanup contract. Do not load that board reference
on a choice-capable run merely because ledger triage is active. Cowork's
mounted-response exception is defined in its adapter above.

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
