"""Ensure today's daily note exists with a skeleton.

Run at the start of each day, or let other scripts call `ensure_daily_note`.
"""

from __future__ import annotations

from scripts.common import daily_note_path, read_file, today_iso, write_file

SKELETON = """# {day}

## Meetings

## Email triage

## Tasks

## Decisions

## Threads / context

## Frictions
"""


def ensure_daily_note(day: str | None = None) -> None:
    day = day or today_iso()
    path = daily_note_path(day)
    if not read_file(path):
        write_file(path, SKELETON.format(day=day))


if __name__ == "__main__":
    ensure_daily_note()
