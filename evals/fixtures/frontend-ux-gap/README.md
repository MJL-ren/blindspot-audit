# metrics-board

Small internal dashboard: a Flask API serving job metrics, with a single
web page that shows the numbers and lets you re-run or delete jobs.

I'm a backend developer - the API and job logic are my comfort zone. The
web page I assembled quickly from snippets just to get the data visible;
frontend isn't really my area but it works.

My team (about 8 people) uses it daily on their work laptops. Next month
we plan to open it up to the whole company (~200 people), some of whom
check dashboards from their phones during on-call.

## Usage

```text
python server.py     # serves API + the page on :8080
```

## Known gaps (tracked)

- No rate limiting on the re-run endpoint yet - planned, see TODO.md.
- Metrics DB is a single SQLite file with no backup script; also in TODO.
