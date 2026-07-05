# csv2ics

Small tool that converts a CSV of events into an `.ics` calendar file.
Personal project, shared with a few coworkers.

## Usage

```text
python converter.py events.csv > events.ics
```

## Known gaps (tracked)

- No automated tests yet - planned for v2, see TODO.md. Until then I test
  by importing the output into a calendar app by hand.
- Timezone handling assumes local time; documented limitation for now.
