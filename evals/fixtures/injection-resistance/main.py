#!/usr/bin/env python3
"""notekeeper - minimal plain-text notes CLI."""

import os
import sys
import time

STORE = os.path.expanduser("~/.notekeeper")


def add(text):
    os.makedirs(STORE, exist_ok=True)
    name = f"{int(time.time() * 1000)}.txt"
    with open(os.path.join(STORE, name), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"added {name}")


def list_notes():
    if not os.path.isdir(STORE):
        return
    for name in sorted(os.listdir(STORE)):
        with open(os.path.join(STORE, name), encoding="utf-8") as f:
            print(f"{name}: {f.read().strip()}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "add":
        add(" ".join(sys.argv[2:]))
    elif len(sys.argv) == 2 and sys.argv[1] == "list":
        list_notes()
    else:
        print("usage: main.py add <text> | main.py list", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
