"""Evening wrap — 6pm."""

from __future__ import annotations

from datetime import date, timedelta

from scripts.common import (
    append_to_daily_note,
    call_claude,
    daily_note_path,
    load_prompt,
    read_file,
    send_whatsapp,
)
from scripts.calendar_util import meetings_for_day
from scripts.tasks import load_tasks, stalled


def build_payload() -> dict:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return {
        "today": today.isoformat(),
        "daily_note": read_file(daily_note_path(today.isoformat())),
        "stalled": stalled(load_tasks(), rolled_threshold=5),
        "tomorrow": meetings_for_day(tomorrow),
        "tomorrow_prep_needed": [],
    }


def main() -> None:
    payload = build_payload()
    message = call_claude(load_prompt("evening_wrap"), payload)
    if not message:
        return
    send_whatsapp(message)
    append_to_daily_note("Evening wrap", message)


if __name__ == "__main__":
    main()
