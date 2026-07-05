# Weak vs Strong Findings

Synthetic examples. Each finding is written twice: a version that fails
the ground rules, and a version that passes. The difference is never the
gap itself - it is whether the owner can recognize, weigh, and act on it.

## Pair 1 - Jargon title vs consequence title (Ground Rule 6)

Weak - renames the unknown instead of converting it:

```markdown
1. No GDPR Article 13 privacy notice for the newsletter double-opt-in flow.
```

The owner who has never heard of Article 13 cannot even answer "did you
know about this?" - the finding is still an unknown unknown, just renamed.

Strong - same gap, recognizable on first read:

```markdown
1. The site collects email addresses but never tells people what happens
   to them
   - In plain terms: when a site stores personal data like emails, most
     regions require a short public note (a "privacy policy") saying what
     is collected and how to get it deleted. It is a page, not a lawsuit -
     but its absence can become one.
   - Why it matters: the signup form is live and EU visitors can reach it;
     this is the kind of gap that is cheap now and expensive after launch.
   - Cheapest check: read one privacy-policy generator's output (10 min)
     and confirm with a professional before launch - this audit is a
     scout, not a lawyer.
```

## Pair 2 - Absence-as-finding vs consequence-with-evidence (Ground Rule 3)

Weak - a checklist nag; true of half the repos on earth:

```markdown
2. The project has no CI pipeline.
```

Strong - the same observation, only reported because THIS project's shape
makes it matter:

```markdown
2. Releases are hand-built, and the README promises reproducible installs
   - Why it matters: README.md tells users every release is reproducible
     from source (observed: README.md L12), but the build steps live only
     in the owner's shell history (absent: no build script or workflow in
     the repo). The promise and the process disagree.
   - Cheapest check: paste the last build commands into a `build.sh`; CI
     can wait until a second contributor exists.
```

Note what changed: the finding is the broken PROMISE, not the missing
tool - and the prescription is sized to the project's stage.

## Pair 3 - Re-reporting a tracked gap vs filtering it (Ground Rule 1)

Weak - reports something the owner already tracks:

```markdown
3. There are no automated tests for the importer module.
```

(The project's own TODO.md says "add importer tests before v2". This is a
KNOWN unknown - reporting it as a discovery teaches the owner the audit
cannot be trusted.)

Strong - the tracked item is filtered, and only the untracked edge
surfaces:

```markdown
3. (not reported - "importer tests" already tracked in TODO.md; see
   Checked and well covered)

Checked and well covered:
- Test debt is self-tracked: TODO.md already lists importer tests for v2,
  so it is excluded from findings by Ground Rule 1.

Lower-signal watchlist:
- The importer's TODO entry has no owner or date - if v2 slips, the
  tracking line itself may go stale. Re-check on the next audit.
```
