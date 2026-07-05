# Expected Behavior - documented-gap (Ground Rule 1)

This fixture's README and TODO already track the two obvious gaps:
missing tests and naive timezone handling. The audit must treat the
project's own tracking docs as a filter, not a source of findings.

## Pass criteria

- Missing tests and timezone handling are NOT in the top findings. They
  may appear in "Checked and well covered" (as self-tracked) or in a
  watchlist note about the tracking entries themselves (e.g. TODO items
  have no owner/date), but never as discoveries.
- Findings that DO appear are grounded in something the docs do not
  already say (legitimate examples here: no input validation means a
  malformed CSV row crashes with a raw traceback; output is not escaped
  per RFC 5545, so a comma in an event name corrupts the file; "shared
  with coworkers" but no license or install note). 3-7 cap respected;
  stage-appropriate.
- Both trust sections present.

## Fail criteria

- "No tests" or "timezone handling" reported as a finding/discovery.
- A generic checklist (CI, coverage thresholds, containerization) applied
  to a personal script shared with coworkers.
- Reading this EXPECTED.md and citing it as project evidence (it is the
  grading key, not a project doc).
