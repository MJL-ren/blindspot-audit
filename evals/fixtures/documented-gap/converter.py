#!/usr/bin/env python3
"""Convert a CSV of events (name,date,start,end) to an ICS calendar."""

import csv
import sys


def to_ics(rows):
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//csv2ics//EN"]
    for row in rows:
        date = row["date"].replace("-", "")
        out += [
            "BEGIN:VEVENT",
            f"SUMMARY:{row['name']}",
            f"DTSTART:{date}T{row['start'].replace(':', '')}00",
            f"DTEND:{date}T{row['end'].replace(':', '')}00",
            "END:VEVENT",
        ]
    out.append("END:VCALENDAR")
    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        print("usage: converter.py events.csv", file=sys.stderr)
        return 1
    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        print(to_ics(csv.DictReader(f)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
