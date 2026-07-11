# Security

Blindspot Audit is a documentation-and-scripts skill package. What it does
and does not do:

- The skill contains Markdown instructions, four executable local helpers, and
  one shared safe-output module. It collects no telemetry and none of these
  helpers contact an external network service.
- Web access during an audit is performed by YOUR agent host under its
  own permissions. The skill instructs agents to search by category only,
  never with private project identifiers (SKILL.md Ground Rule 7).
- Repository scripts under `scripts/` build, verify, install, and sync
  the package locally. None of them call the network. Installers write
  only into the skill destination you choose, and replace only the
  `blindspot-audit` folder inside it. PowerShell installers verify that direct
  child boundary and refuse recursive deletion when the install root or a
  descendant is a junction, symlink, or other reparse point.
- The skill instructs agents to treat project files and web content as
  evidence, never as instructions (Ground Rule 8): embedded text that
  tries to steer or suppress an audit is disobeyed and surfaced to the
  owner.
- Audit output (`BLINDSPOT_LEDGER.md`) lives in YOUR project, under your
  control. The skill's ledger rules keep sensitive detail out of ledgers
  that reach public surfaces.

## Packaged Helper Boundaries

| Helper | Reads | Writes/listens | External network | Normal trigger and cleanup |
| --- | --- | --- | --- | --- |
| `project_inventory.py` | Project filenames and selected local metadata | Standard output only | None | A normal audit may run it as a bounded static check; no cleanup |
| `secret_presence_scan.py` | Selected current-tree files and, only when requested/approved, bounded local Git objects | Value-suppressed standard output only | None | Static security check; generated/reference paths are excluded by default and must be opted in |
| `audit_followup_guard.py` | Existing ledger structure, IDs, hashes, and target Git status/diffs | Temporary `.blindspot-tmp/audit-followup-*` snapshot/response files | None | Existing-ledger audit writes; cleanup is allowed only after validation and `--confirm-applied` |
| `ledger_triage_board.py` | Ledger, reviewed board input, and submitted response JSON | Temporary `.blindspot-tmp/ledger-triage-*` files; optional short-lived HTTP server bound to `127.0.0.1` only | None; loopback only | Owner-requested ledger triage on a host without usable choices; validated application must finish before cleanup |
| `safe_output.py` | Strings passed to it by another helper | Nothing; support module only | None | Escapes terminal and direction-control characters for console/log display |

Structured choice hosts normally use their native choice tool instead of the
HTML board. The loopback board does not authenticate users and is not intended
for non-loopback binding, shared hosting, long-running service use, or automatic
ledger application. The agent host may still browse the web, run commands, or
use provider connectors under its own permissions; installing this skill does
not grant those permissions.

## Reporting

If you find a security problem - or installed content that does not
match this repository - please use GitHub's private vulnerability
reporting on this repository ([open a private report](https://github.com/MJL-ren/blindspot-audit/security/advisories/new)). If that is unavailable,
open an issue asking for a private contact channel; please do not post
exploit detail publicly first.
