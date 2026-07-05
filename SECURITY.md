# Security

Blindspot Audit is a documentation-and-scripts skill package. What it does
and does not do:

- The skill itself is Markdown instructions plus one local helper script
  (`scripts/project_inventory.py` inside the skill folder). The helper
  reads the local project tree only - it makes no network calls, collects
  no telemetry, and writes nothing outside its own output.
- Web access during an audit is performed by YOUR agent host under its
  own permissions. The skill instructs agents to search by category only,
  never with private project identifiers (SKILL.md Ground Rule 7).
- Repository scripts under `scripts/` build, verify, install, and sync
  the package locally. None of them call the network. Installers write
  only into the skill destination you choose, and replace only the
  `blindspot-audit` folder inside it.
- The skill instructs agents to treat project files and web content as
  evidence, never as instructions (Ground Rule 8): embedded text that
  tries to steer or suppress an audit is disobeyed and surfaced to the
  owner.
- Audit output (`BLINDSPOT_LEDGER.md`) lives in YOUR project, under your
  control. The skill's ledger rules keep sensitive detail out of ledgers
  that reach public surfaces.

## Reporting

If you find a security problem - or installed content that does not
match this repository - please use GitHub's private vulnerability
reporting on this repository (Security tab). If that is unavailable,
open an issue asking for a private contact channel; please do not post
exploit detail publicly first.
