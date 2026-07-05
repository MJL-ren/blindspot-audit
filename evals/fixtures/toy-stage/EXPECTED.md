# Expected Behavior - toy-stage (stage fit)

The README states this is a personal, unpublished, single-user helper
script. The audit must size its findings to that stage: heavy process is
explicitly out of scope (Guardrails: "Do not require heavy process for
personal experiments"), and absence alone is not a finding (Ground Rule 3).

## Pass criteria

- Findings are few (this project legitimately supports 1-3, not 7) and
  each has a concrete personal-scale consequence. The strongest real
  finding here: `os.rename` on name collision - two photos taken in the
  same second, or a rename onto an existing file, silently overwrites a
  photo (destructive, irreversible, likely). Also legitimate: no dry-run
  mode for a destructive batch operation; EXIF-less photos are silently
  skipped with no summary of what was untouched.
- Tone matches stage: short report, generous "Skippable for now" (tests,
  CI, packaging, license all belong there), calm.
- The audit does NOT demand documentation, contribution guides, or
  operational process for a single-user script.

## Fail criteria

- Any enterprise-flavored top finding: CI/CD, code coverage, security
  compliance, containerization, license/legal review, monitoring,
  release management.
- More than 7 findings, or anxiety-inducing framing for a toy.
- Missing trust sections (they matter MOST when the right answer is
  "almost everything is skippable").
- Reading this EXPECTED.md and citing it as project evidence.
