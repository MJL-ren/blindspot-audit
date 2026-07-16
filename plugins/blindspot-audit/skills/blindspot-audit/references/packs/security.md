# Focus Pack: Security

Focus ID: `security`

Scope label: `focus/security`

Contents: [Activation](#activation-and-applicability) |
[Identity](#identity-guard) | [Surface](#surface-map) |
[Probes](#probe-sets) | [Boundaries](#boundaries-and-stage-fit) |
[Anchors](#peer-and-current-anchors) | [Checks](#cheapest-next-checks) |
[Reporting](#reporting-and-coverage)

## Activation And Applicability

Use this pack when the project has at least one material security boundary:
untrusted input, network exposure, user or machine identities, private data,
credentials, paid or destructive actions, executable releases, privileged
automation, external providers, or a build/deploy pipeline with write access.
The project may be software, a game, a content service, a research pipeline, or
an agent workflow; the boundary and consequence matter more than the stack.

Do not create standing pack debt for an offline, single-user, disposable
artifact that accepts no untrusted input, holds no credentials or private data,
and ships no executable output. Ordinary backup, privacy, or file-permission
questions may still fit the broad lenses without requiring this pack. A focus
limited to one service, repository, or feature is partial coverage.

Neighboring domains keep their own ownership:

- `privacy` asks whether personal data should be collected, retained, shared,
  or deleted; security asks whether unauthorized actors can reach or alter it.
- `data-integrity` asks whether data is correct, complete, and reproducible;
  security owns deliberate tampering and provenance across a trust boundary.
- `ai-agent` asks what an agent may decide or do; security owns untrusted input,
  credentials, and privileged sinks used by that agent.
- `ux-ui` owns whether security decisions are understandable and usable; this
  pack owns whether the underlying control is actually enforced.

### Owner-Response Completion Gate

After the awareness interview, load `references/owner-response-guard.md` and
use the Existing Ledger Write Guard in `SKILL.md` before applying the response.
Use grouped owner-response v2 when several findings share one batch decision,
and require final validation to show their actual applied ledger mappings. If
two or more findings become `deferred` under the same named batch, the run is
not complete until the
durable `SECURITY_BATCH_PLAN` exists, the affected rows or their shared batch
note link back to it, and final guard validation passes. Generate its mechanical
skeleton with
`python "<skill>/scripts/audit_followup_guard.py" scaffold-security-batch`;
a ledger-only batch section is not a substitute. `owner_followup` remains a next-action
route, never a disposition.

## Identity Guard

This is a defensive, read-mostly awareness audit, not a penetration test. Do
not send attack payloads, probe public hosts, attempt login, use discovered
credentials, brute-force anything, trigger webhooks, upload files, modify
provider settings, install scanners, or run exploit code without explicit
authorization and the normal command guardrails. A code path that looks weak is
a candidate until its real boundary and runtime behavior are confirmed.

Never echo a secret value into chat, a report, a ledger, a command, or another
tool. Name the file/setting and redact the value. Do not test whether a token is
live. Provider-side revocation or rotation belongs to the owner or an authorized
operator, and the report should explain that plainly.

Console/log output from bundled helpers must pass untrusted paths, owner notes,
request lines, and other repository-controlled strings through
`scripts/safe_output.py`. It renders C0/C1, DEL, terminal escape, line-separator,
and Unicode direction/format controls as visible escapes while preserving normal
owner-language text. Structured JSON/HTML still uses its format's escaping;
secret-value redaction remains an additional secret-locator responsibility.

The pack does not certify compliance or promise that a project is secure. A
deliberate, bounded trust decision can be a complete answer. Findings still
pass the four-unknowns frame, owner-doc filter, evidence rule, stage fit, 3-7
cap, and awareness interview. Explain unfamiliar security terms through the
everyday consequence before naming the term.

### Verification Tiers

Classify every security check before running it. The tier does not change by
host:

1. `static-only` - code, config, manifests, existing logs/results, and already
   produced artifacts are read without executing project code. This is the
   default allowed tier.
2. `ephemeral-local` - project code is executed with synthetic/dummy input in a
   temporary or in-memory state, in-process or loopback only. It requires
   explicit owner approval unless the current request already says safe local
   probes are allowed. A general `focus: security` request alone is not that
   approval.
3. `authorized-dynamic` - any public/staging project host, real account or
   credential, provider API/runtime/account call, scanner, aggressive/
   attack-shaped payload, or persistent environment. It always requires
   separate explicit authorization with target and limits. Reading a public
   official documentation page is the evidence channel below, not this tier.

An `ephemeral-local` check is allowed only when ALL are true:

- dummy values only; no real secret, account, user record, or private payload.
- `TemporaryDirectory`, in-memory store, or equivalent isolated state.
- in-process or loopback only; external network and providers disabled/mocked.
- sanitized environment with no ambient production credentials.
- one to three narrow probes tied to one candidate.
- no persistent repo, database, cache, or generated-file change; cleanup is
  verified afterward.
- command/probe shape, result, and cleanup are recorded in the report.

`TestClient` with a dummy secret and `TemporaryDirectory` is always
`ephemeral-local`, never `static-only`. If isolation or startup side effects
cannot be established, raise it to `authorized-dynamic` or leave it as the
cheapest proposed check. Existing test logs are static evidence; rerunning a
test executes code and follows the tiers above.

### Evidence Channels

Record where evidence came from on a separate axis from the verification tier:

- `repository`: current files, manifests, lockfiles, and Git metadata.
- `existing-artifact`: already-produced logs, reports, builds, or scan output.
- `official-web-readonly`: official framework, provider, package, platform, or
  advisory pages fetched without touching the project runtime.
- `community-web-readonly`: community reports used only as leads.
- `owner-provider-confirmation`: an owner or authorized operator checks a
  provider/runtime setting that the repository cannot prove.

Reading an official advisory on the web does not execute the project, so the
project verification tier may remain `static-only`; the network evidence
channel is still recorded separately. Search with component names, locked
versions, advisory IDs, and public stack terms only. Never put a credential,
private URL, private payload, unpublished project/client name, or other
sensitive identifier into a web query. Ask before a query would need private
context. Record skipped or zero-signal research too, for example:

`project verification: static-only; external evidence: official-web-readonly; community scan: not needed`

### Provider Connector State

Before discussing token scope, TTL, rotation, or a live provider operation,
record these five gates independently and in order:

| Gate | Values | Meaning |
| --- | --- | --- |
| Presence | present / absent / unconfirmed | connector/plugin is visible in the current app installation |
| Authentication | connected / disconnected / unconfirmed | its prior authentication link appears alive |
| Callability | callable-now / mode-gated / unavailable / unconfirmed | the current host mode can invoke it now |
| Granted scope | known / owner-confirm-needed | account/resource permission boundary is understood without exposing identifiers |
| Operation consent | not-authorized / read-only-authorized / live-authorized-with-limits | what this owner allowed for this run |

When no provider connector or connector-mediated operation is applicable to the
audited scope, record one compact line instead:

`provider connector: not-applicable (<plain reason>)`

Do not fill all five gates with `unconfirmed` merely to complete the template.
`not-applicable` means the surface is genuinely absent, never that it was not
inspected. If a provider exists but the current host has no connector, record
Presence `absent`; Authentication and Callability may be `not-applicable`, while
provider configuration still stays separately `owner-confirm-needed` when it
matters.

Use host metadata, installed-plugin state, and explicit owner information for
Presence, Authentication, and Callability. Do not make a speculative provider
tool call just to test connection. A disconnected or unavailable connector is a
coverage/operation limitation, not a vulnerability. Excessive or unexplained
granted scope can become a finding only after the connector identity and
intended use are established. `callable-now` and `connected` never imply live
operation consent.

If the owner explicitly asks the agent to re-check connection state, treat that
as bounded `read-only-authorized` owner/provider confirmation for the named
connection check only. It does not authorize data reads, writes, deployment,
token rotation, or other live actions. Generalize account, zone, tenant, and
resource identifiers in public or visibility-unconfirmed records.

## Surface Map

Map the system before judging individual lines:

- assets: what must not be disclosed, changed, deleted, impersonated, or made
  unavailable.
- actors: anonymous users, members, admins, operators, services, CI jobs,
  plugins, agents, and external providers.
- trust boundaries: browser/server, client/API, process/file, repo/CI,
  application/provider, public/private export, and human/automation.
- entry points: routes, commands, uploads, file reads, webhooks, queues, URLs,
  prompts, imports, environment variables, and configuration.
- enforcement points: authentication, authorization, validation, sandboxing,
  approvals, database queries, output encoding, and provider policy.
- identity and secret stores: session settings, environment-variable names,
  key stores, CI secret references, service accounts, and recovery paths.
- software supply path: dependency manifests, lockfiles, build scripts, CI
  triggers and permissions, third-party actions, artifacts, and deployment.
- detection and recovery: security-relevant logs, alerts, patch/update path,
  incident contact, rollback, backups, and credential rotation.

Keep evidence locations distinct:

1. current repository tree.
2. Git history and prior artifacts.
3. deployed runtime and provider-side configuration.
4. owner or specialist confirmation.

One location cannot prove another. Read existing security notes, findings, and
incident records first so known work is filtered rather than rediscovered.

Build this internal matrix before ranking candidates. It is working state, not
a new durable project document unless the owner asks for it:

| Boundary | Protected asset | Entry point | Enforcement point | Repo evidence | Runtime/provider evidence | State | Finding IDs | Limitation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <subsystem/trust crossing> | <what can be harmed> | <input/actor> | <where control should hold> | <inspected paths> | <evidence or confirmation needed> | inspected / owner-confirm-needed / uninspected / skipped | <IDs or none> | <what was not observable> |

Use the matrix to determine overall coverage consistently:

- `completed with limits`: every applicable repository-inspectable subsystem
  is `inspected`; provider/deployed-runtime rows may remain
  `owner-confirm-needed` when named explicitly in limits.
- `partial`: any applicable repository subsystem is `uninspected`, or the owner
  narrowed the focus to only part of the project.
- `skipped`: the owner skipped an applicable boundary with reason and re-check
  trigger.
- `owner-confirm-needed` is a row state/coverage qualifier, not evidence that
  the whole repository pass is partial.

Build the following smaller working tables when their applicability condition
is met. Do not publish them as new project documents or fill unknown cells with
guesses.

### Security-Critical Dependency Matrix

Use when a shipped or privileged boundary depends on locked third-party code.
Cover direct or security-critical transitive dependencies, not every package in
the graph:

| Dependency | Lock evidence + exact version | Reachable use/boundary | Official advisory | Affected range | Patched range | Product copies | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <component> | <lockfile/path + version> | <where it can execute or receive input> | <official URL/ID or none found> | <range or unconfirmed> | <range or unconfirmed> | <lineage rows> | affected / not affected / owner-confirm-needed |

Read the exact locked/resolved version rather than only a loose manifest
constraint. An advisory match becomes a finding only after version range,
reachable use, deployment, and relevant mitigation are checked.

### Product Lineage Matrix

Use when the same product, component, or vulnerable code appears in multiple
repositories or copied directories:

| Lineage cluster | Copy | Role | Shipping state | Maintenance state | Remediation owner/surface | Closing check | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <shared origin> | <repo/path> | shipping / maintained snapshot / upstream / retire candidate | <current exposure> | <active/frozen/unknown> | <who and where> | <copy-specific verification> | update / retire / owner-confirm-needed |

A lineage cluster prevents a copy from being forgotten; it does not erase
copy-specific evidence or closure. Use one root finding only when the shared
implementation, remediation decision, and verification family also satisfy the
merge rule in Reporting. Otherwise keep separate finding IDs under one visible
lineage cluster.

### Executable Distribution Matrix

Use for every executable, installer, updater, extension, bridge, script bundle,
or downloadable tool that can cross a machine/user boundary. Do not inherit the
main product's commercial/public status automatically:

| Executable/update surface | Audience | Distribution/update path | Signing/trust boundary | Repository evidence | Owner confirmation | Priority effect |
| --- | --- | --- | --- | --- | --- | --- |
| <artifact/tool> | owner-only / team-shared / external-testers / public-distribution | <local copy, private share, store, updater, download> | <who can replace/run it> | <build/release/update paths> | confirmed / owner-confirm-needed | watch/skip candidate or now/next candidate |

An `owner-only` unsigned tool with no external updater or sharing boundary is
normally a `watch`/intentional-skip candidate. The same control gap on an
artifact sent to teammates, testers, customers, or a public updater can become
`next` or `now` based on replacement and execution impact. Re-evaluate whenever
audience or update path changes.

### Promise-To-Enforcement Diff

Use whenever README, AGENTS, security notes, UI copy, runbooks, or provider docs
make a security promise:

| Promise source | Plain promise | Enforcement point | Repository evidence | Runtime/provider evidence | Result |
| --- | --- | --- | --- | --- | --- |
| <path/section> | <what users/operators are told is protected> | <where the control must actually hold> | <code/config that enforces it, or absent> | <evidence or confirmation needed> | matched / mismatch candidate / owner-confirm-needed |

Documentation is evidence of intent, not enforcement. Promote a mismatch only
when the promise is current and the missing or contradictory enforcement has a
concrete consequence.

## Probe Sets

### 1. Assets, Actors, And Trust Boundaries

- What concrete harm can happen here: private material exposed, another user
  impersonated, money spent, content altered, releases replaced, or work lost?
- Is the real exposure local, team-only, internet-facing, embedded in another
  product, or reachable through automation? Do docs and deployment agree?
- Which actors are intentionally trusted, and where does code enforce the line
  between them? Is a UI convention being mistaken for a boundary?
- Are the most important security decisions written anywhere, or does each
  maintainer and agent have to infer them again?

Evidence: route and command entry points, deployment/config files, role names,
data stores, public/private docs, provider references, and actual enforcement
code. A diagram is not enforcement, and a missing diagram is not itself a
finding when the boundary is clear in code and operations.

### 2. Identity, Login, Session, And Recovery

- Which humans and machines need identities, and which surfaces are
  intentionally anonymous or public?
- Can sessions or tokens outlive the person, device, job, or purpose that
  created them? Is logout/offboarding real, or only a UI state?
- Do account recovery, password reset, invite, email change, and multi-factor
  recovery preserve the same identity boundary as normal login?
- Are default credentials, shared accounts, long-lived service keys, or human
  use of automation identities intentional and bounded?
- For a high-impact account, has stronger authentication been consciously
  chosen or skipped based on actual risk rather than habit?

Evidence: authentication middleware, session/cookie settings, token lifetime
and scopes, recovery routes, invite flows, service-account configuration, and
provider settings named in docs. Provider-only settings remain
`owner-confirm-needed` until the owner or an authorized connector check confirms
them.

### 3. Authorization And High-Impact Actions

- After identity is known, does the server check role, ownership, tenant, and
  object access on every protected read and write, or only hide controls in the
  client?
- Can a user change an ID, path, request field, or job name to reach another
  user's object or an admin-only action?
- Are delete, publish, payment, deployment, export, key creation, and permission
  changes bounded by the exact action the owner approved?
- If policy, approval, or identity lookup fails or times out, is the action
  denied/pending, or silently allowed?
- Can a delegated service, plugin, CI job, or agent gain more authority than the
  caller that launched it?

Evidence: server-side guards, ownership filters, role/policy tables, route
decorators, service-account scopes, CI permissions, approval records, and
fail-open fallback branches. Intentionally trusted admins doing documented
admin work are not a boundary bypass.

### 4. Untrusted Input, Interpretation, And Output

- Where can outside text or bytes become database syntax, shell commands,
  templates, HTML, file paths, URLs, code, serialized objects, or model/tool
  instructions?
- Is validation performed at the boundary that knows the rules, and is output
  encoded for the place it will be used rather than merely checked once?
- Can uploads, archive extraction, imports, or user-chosen paths escape their
  intended directory or become executable/public content?
- Do fetched URLs, redirects, webhooks, callbacks, and message queues verify
  destination, origin, signature, replay, size, and timeout where those matter?
- Do parser failures and exceptional conditions stop safely, or skip the
  security check and continue?

Evidence: database/query APIs, command execution, template escaping, path joins,
URL fetchers, upload handlers, deserializers, webhook checks, exception
branches, and size/time limits. Do not construct or run an exploit to prove the
candidate; propose an authorized test when static evidence is not enough.

### 5. Secrets And Non-Human Credentials

- Where can keys, tokens, passwords, signing material, and connection strings
  appear: source, local config, Git history, CI, logs, screenshots, generated
  artifacts, backups, or provider dashboards?
- Are secrets scoped, short-lived, rotated, and separated by environment, or
  can one credential cross development, production, users, and services?
- If a secret was exposed, was it revoked or rotated at the provider, or only
  deleted from the current file?
- Can former collaborators, old jobs, forks, cached artifacts, or deleted
  services still use a credential?
- Are ignores and scanner baselines narrow enough to suppress one known false
  positive without hiding an entire path or class of future exposure?

Treat these as four independent closure checks:

1. current tree no longer exposes the value.
2. Git history and retained artifacts are understood.
3. provider-side credential is revoked/rotated or proven non-sensitive.
4. logs, deployments, caches, and downstream copies are handled.

Record those states independently in an existing decision/next-check cell or
Audit Evidence note; do not add ledger columns automatically. Example:

`secret closure: provider=resolved; current-tree=deliberate_skip(reason+trigger); history-artifact=unconfirmed(re-check trigger); downstream=owner-confirm-needed; overall=open`

Provider revocation can close live account access without cleaning repository
or artifact residue. Conversely, deleting the current string cannot prove
provider revocation. Keep `overall=open` while any required axis is unconfirmed,
deferred, or owner-confirm-needed; use `resolved` only when every applicable
axis has evidence or an explicit, triggered owner disposition.

Evidence: secret references and variable names, ignore rules, CI configuration,
incident notes, rotation docs, and provider confirmation. Never put the value
itself in evidence. A dedicated scanner can compare current-tree and history
results, but scanning is a proposed check unless the owner authorizes it.

### 6. Sensitive Data And Cryptographic Boundaries

- Which credentials, private records, personal material, or valuable project
  data cross networks, enter logs, sit in backups, or reach third parties?
- Are passwords stored with an established password-hashing facility rather
  than reversible encryption or a general fast hash?
- Is transport/storage protection provided by a known platform boundary, and
  is anyone responsible for keys, rotation, restore, and provider access?
- Can debug output, errors, analytics, support exports, or backups reveal more
  than the normal product surface?
- Is custom cryptography or home-grown token/signature logic being trusted
  where a maintained framework or provider facility should own the boundary?

Evidence: schema and field names, logging calls, backup/export paths, framework
security settings, password/token helpers, TLS/provider docs, and key
references. Do not demand encryption everywhere: connect it to actual data,
exposure, and threat. Collection/retention purpose remains a privacy question.

### 7. Dependencies, Builds, CI, And Release Integrity

- Can an untrusted branch, pull request, package script, plugin, or downloaded
  artifact execute while write credentials or release permissions are present?
- Are CI permissions and secrets limited to the event and job that need them?
  Is fork/untrusted-contributor behavior understood?
- Are dependency sources, lock/provenance decisions, update ownership, and
  vulnerability-advisory checks appropriate for what the project ships?
- Are third-party actions, installers, and build inputs pinned or otherwise
  reviewed strongly enough for their privilege and update path?
- Can someone distinguish the artifact that was reviewed from a later or
  locally modified build that gets published?

Evidence: workflow triggers, job permissions, checkout target, secret exposure,
dependency manifests/lockfiles, install scripts, action/image references,
artifact checks, release notes, and existing advisory results. An old or
unpinned dependency alone is not a vulnerability; name the reachable boundary
or the missing update/provenance decision. Complete the security-critical
dependency matrix before claiming that a locked version is affected or fixed.

### 8. Secure Failure, Detection, And Response

- Do production defaults close risky debug, anonymous, test, and sample paths,
  or can a missing setting silently enable them?
- When authentication, signature verification, policy, storage, or a provider
  fails, does the protected action stop safely?
- Would the owner learn about repeated access failures, privilege changes,
  suspicious exports, secret use, release changes, or disabled controls without
  manually reading every log?
- Do logs contain enough actor/action/result context to investigate while
  avoiding credentials and excessive private data?
- Is there a realistic path to contain, patch, rotate, notify, restore, and
  verify after an incident? Who owns that decision?
- Are abuse limits tied to a plausible exposed operation, or copied in as a
  generic requirement with no threat or user consequence?

Evidence: production config, exception branches, audit events, alerting rules,
security contact/reporting docs, dependency-update process, incident notes,
rollback/restore instructions, and provider logs. Missing enterprise incident
process is not a finding for a tiny prototype; inability to revoke its one
production key can still be one.

## Boundaries And Stage Fit

- No login is not a finding for intentionally public read-only content. No
  role system is not a finding for a genuinely single-user local tool.
- Multi-factor authentication, encryption at rest, a web application firewall,
  formal threat modeling, and a security operations team are not universal
  requirements. Tie each candidate to the project's actors, assets, exposure,
  and stage.
- Early prototypes can defer broad hardening, but public exposure, real
  credentials, private user data, paid/destructive actions, and privileged CI
  make some boundaries real before product polish.
- Test fixtures, examples, documentation snippets, generated files, vendored
  code, and obvious placeholders produce false positives. Confirm reachability
  and deployment before promoting them.
- Classify every executable/update surface by its actual audience. Do not raise
  an owner-only local helper to public-product urgency merely because another
  executable in the same repository ships commercially.
- A missing defense-in-depth layer is not a confirmed vulnerability when the
  primary control is sound. Put useful hardening in the watchlist unless a
  concrete consequence and awareness gap justify the main findings cap.
- Dependency age, a scanner warning, or a CVE name is not enough. Verify the
  affected version, reachable feature, deployment, upstream advisory, and
  mitigation status before claiming exposure.
- Do not assign dramatic severity or CVSS-like certainty from static suspicion.
  Rank by concrete impact, exposure, likelihood, reversibility, and evidence.
- Report controls that are genuinely well covered. Security reports that only
  accumulate alarms make it harder for the owner to recognize what matters.

## Peer And Current Anchors

Use official current sources to calibrate, not to dump a universal checklist:

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
  for application verification requirements appropriate to the project's
  architecture and assurance needs.
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/) as a current awareness
  map for web application risk categories, not proof of complete coverage.
- [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf/publications)
  for lifecycle, development environment, component, release, and vulnerability
  response questions. Distinguish current final publications from drafts.
- [CISA Secure by Design](https://www.cisa.gov/securebydesign) for secure
  defaults, ownership of user outcomes, transparency, and recurring weakness
  classes.
- Official framework, language, cloud/provider, package-advisory, and upstream
  project sources for the exact stack being inspected.

Verify the current version and publication status during the run. Community
posts, scanner output, and breach write-ups are leads; confirm a project-specific
claim against source code, official documentation, an upstream advisory, or an
authorized owner/provider check.

For `focus: security`, run the external scan in this order:

1. Official security documentation and advisories for the frameworks, cloud
   services, package ecosystems, and platforms actually present.
2. Official changes from roughly the last 6-12 months that alter those exact
   boundaries, defaults, support windows, or advisories.
3. Community/recent sources only when a concrete project candidate needs a new
   incident, bypass, or exploitation lead.
4. Promote a community lead only after official/upstream or project evidence
   confirms it; otherwise label it unverified watchlist material or drop it.
5. Record a zero-signal official scan in the Audit Log so later runs know it
   happened; do not fill the report with unrelated general security news.

## Cheapest Next Checks

Propose the smallest check that can change the decision; do not run
side-effectful, networked, credentialed, or expensive checks uninvited.

- Free/read-only: trace one high-impact action from entry point to enforcement;
  compare declared roles with server-side checks; inspect production defaults,
  CI triggers/permissions, secret variable names, lockfiles, and existing logs.
- Redacted secret-presence locator: use
  `python "<skill>/scripts/secret_presence_scan.py" --project-root "<root>" --scope tree`
  when a current-tree heuristic would change the decision.
  It reports only sanitized path, line, identifier, and pattern category - never
  matched values or surrounding text. The helper is a bounded manual heuristic,
  not proof that no secret exists. Its first pass follows Search Hygiene by
  excluding large generated/reference/vendor paths such as `external_repos`,
  `external-repos`, `vendor`, `dist`, `build`, and `runtime`. In Git repositories
  the current-tree pass enumerates tracked files plus unignored untracked files,
  reports that mode, and never reads Git-ignored clone/cache contents by default.
  Opt a deliberate noisy path back in with `--include <relative-path-or-glob>`.
  For an ignored path, combine that narrow filter with `--include-ignored`; the
  helper rejects an unbounded `--include-ignored`. Use `--include-generated` for
  a separate generated/shipping-artifact pass. Do not claim secret closure for a shipped
  artifact that was excluded, including an ignored or generated artifact. Add
  narrower exclusions with repeatable
  `--exclude <relative-path-or-glob>`;
  the default `--max-files 5000 --time-budget 8` returns `status: partial`
  rather than disappearing at a host timeout. Partial JSON preserves scanned,
  skipped, excluded, candidate, stop-reason, last-safe-path, and recommended
  resume-scope coverage without values. Its `history`/`both` scope is still
  `static-only`, but may be expensive; run it only when explicitly requested or
  approved with `--max-history-blobs` and a time budget. Provider state always
  remains `owner-provider-confirmation`.
- Owner confirmation: check a provider dashboard for token revocation, MFA,
  service-account scope, webhook secret, production exposure, or alert delivery.
  Never ask the owner to paste a secret value into chat.
- Ephemeral local verification: after explicit approval, use one to three
  isolated dummy-input probes under the `ephemeral-local` contract above. Stop
  and reclassify if startup touches ambient credentials, providers, or persistent
  state.
- Focused automation: propose Gitleaks or an equivalent with current-tree and
  Git-history scans kept separate; OSV-Scanner or the ecosystem's advisory tool;
  OpenSSF Scorecard for repository supply-chain signals; and stack-specific
  static analysis. These are `authorized-dynamic` unless separately authorized,
  even when they run locally. Review false positives and avoid broad ignore rules.
  Audit Log notes distinguish `manual-heuristic` from `dedicated-scanner` and
  always state tree/history/provider coverage without including a match value.
- Verification standard: select only the applicable OWASP ASVS controls or
  framework security guidance instead of treating every control as mandatory.
- Authorized dynamic check: use a staging environment, test account, bounded
  request, and explicit permission. Record target, limits, and cleanup before
  any action.
- Specialist depth: threat modeling, code-assisted security review, or a
  professional penetration test when public exposure, money, sensitive data,
  regulated use, or a high-impact boundary warrants it.

## Reporting And Coverage

Use `scope: focus/security`. Lead with 3-7 root boundary or missing-decision
findings, not every suspicious line. Cluster related symptoms for presentation,
but merge them only under the rule below. For each finding, distinguish what is
directly observed, what is a candidate interpretation, what needs
runtime/provider confirmation, and what the owner can decide now.

Merge candidates into one finding only when ALL three match:

1. the enforcement point that failed or lacks a decision.
2. the remediation owner and code/config/operational surface.
3. the cheapest verification test that would close the candidate.

If any differs, keep separate finding identities even when the possible harm is
similar. Related findings may share a presentation cluster, but not evidence,
ledger IDs, or closure. The 3-7 cap moves lower-signal distinct candidates to
the watchlist; it never justifies over-merging them.

For copied repositories or product snapshots, the lineage cluster is the
presentation group. Merge its copies into one root finding only when they share
the vulnerable implementation, remediation decision/owner, and closing-test
family. Keep a per-copy update-or-retire disposition and verification result
even inside a merged root finding.

When there are 5-7 findings, put this three-line snapshot before the details:

- `now: <N> - <largest immediate consequence in one sentence>`
- `next: <N> - <gate to close before the next exposure/stage>`
- `verified controls: <one important boundary already working>`

Use a two-layer owner report when a durable ledger received the full finding
records:

1. Owner-visible chat: the snapshot, adaptive plain-language groups (for
   example immediate dependency exposure, direct code boundary, and later
   follow-up), plus a compact metadata table.
2. Ledger: complete evidence, cheapest check, priority, confidence, awareness,
   disposition, and source links for every finding.

| ID | What can happen | Evidence anchor | Owner / next action | Priority / Confidence | Awareness / Disposition |
| --- | --- | --- | --- | --- | --- |
| <ID> | <self-contained everyday consequence> | <short path/advisory pointer> | <who + plain cheapest next action> | <canonical values> | <canonical values> |

The compact layer must still let an owner understand and classify every item
without opening the ledger. On read-only/chat-only hosts, or when no durable
ledger received the details, include the full finding blocks in chat instead.

When the owner explicitly says that two or more findings will be handled as one
later batch, create a lightweight durable handoff from
`templates/SECURITY_BATCH_PLAN.md`. Before choosing its path or adding details,
inherit the most restrictive visibility of the ledger, destination repository,
and public export path under `references/ledger-lifecycle.md`. Set `Visibility`
and `Detail policy` in the file. When visibility is unconfirmed, default to
`generalized`, omit exploitable paths/payloads/credential and provider names,
and leave any needed private destination as `owner-confirm-needed` rather than
guessing. Prefer the project's existing private plan/docs location; otherwise
place a public-safe generalized handoff beside the ledger with a clear
date/title. Even `private/full` never contains secret values.

After the owner-response preview is valid, prefer
`python "<skill>/scripts/audit_followup_guard.py" scaffold-security-batch` over
copying the template by hand. It uses the response's repo-relative `batchPath`, preserves the canonical
verification headers, emits one placeholder row per included ID, and returns a
ledger-backlink suggestion. Fill the consequence, target, execution order,
exact check, tier, channel, and pass condition before final validation. The
scaffold never edits the ledger. For `public-safe` or `unconfirmed` visibility,
final validation rejects drive, home, UNC, `file://`, and other local absolute
paths; use repository-relative paths only.

This is not the temporary ledger-triage application plan and does not require
the HTML decision board. Link its included IDs from the ledger and keep detailed
evidence in the ledger rather than duplicating it. In its verification matrix,
one row has one check, one tier, and one needed evidence channel; repeat a
finding ID across rows for repository and provider checks. Do not create a batch
file from vague timing language or a single deferred row. On a read-only host,
include the same compact handoff in the response without claiming a file was
written. After the batch closes, preserve the concise result in the ledger and
delete/archive the handoff according to local plan lifecycle.

Write in the owner's language at a non-specialist level: describe what another
person or system could do before terms such as authorization, injection,
provenance, or fail-open. Awareness choices must be understandable without
reading source code. Redact all credential material and avoid reproducing
private payloads or records in the report or ledger.

If evidence suggests a currently exposed credential or an immediately reachable
public boundary, stop expanding that sensitive evidence, surface it clearly as
`now`, and propose containment/revocation without testing it. A
`resolved_candidate` for a secret remains open until the relevant current-tree,
history/artifact, provider, and downstream checks are supported by evidence.

Record one short `BA-YYYYMMDD-NN` result in the Audit Log row. When the run has
multiple coverage, verification, external-research, secret-search, or provider
dimensions, put the following details under that run ID in the ledger's Audit
Evidence section. Apply the same private/public-safe visibility policy as the
findings and batch handoff:

- `pack security: completed with limits; repo boundaries <inspected>; owner-confirm-needed <runtime/provider rows>`
- `pack security: partial; scope <service/feature>; remaining <boundaries>`
- `pack security: not applicable; no material security boundary`
- `pack security: skipped by owner; re-check when <exposure trigger>`
- `pack security: coverage debt; material boundary, pack not yet run`

The detailed evidence entry also records verification tiers actually run,
external evidence channels, manual-heuristic versus dedicated secret scan
coverage, the five provider connector gates, and the owner-response delta. Do
not make the Audit Log table cell carry all of those clauses or duplicate full
finding evidence there.

Security batch verification tables are machine-readable working state. Keep the
headers `Finding`, `Verification tier`, and `Evidence channel` exactly as written
in the bundled template; write checks, pass conditions, and surrounding prose in
the owner's language. The guard reads only those exact cells, never matching
enum-looking words from the rest of a row.

All applicable repository-inspectable boundaries must be inspected for
`completed with limits`; provider/runtime confirmation may remain named in the
limits. Any uninspected applicable repository subsystem makes the result
`partial`. Always include concrete positive controls in "Checked and well
covered" and stage-appropriate deferrals in "Skippable for now."
