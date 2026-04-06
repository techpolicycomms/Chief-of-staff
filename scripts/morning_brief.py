"""Morning brief — 9am.

Assembles a payload (calendar, overdue, due-today, needs-prep, last wrap)
and hands it to Claude with `prompts/morning_brief.md`. Sends to WhatsApp.
"""

from __future__ import annotations

from datetime import date, timedelta

from scripts.common import (
    append_to_daily_note,
    call_claude,
    load_prompt,
    read_file,
    send_whatsapp,
    today_iso,
    MEMORY_DIR,
)
from scripts.tasks import load_tasks, overdue, due_on
from scripts.calendar_util import meetings_for_day
from scripts.daily_note import ensure_daily_note


def build_payload() -> dict:
    tasks = load_tasks()
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    last_wrap_note = read_file(MEMORY_DIR / f"{yesterday}.md")

    return {
        "today": today.isoformat(),
        "calendar": meetings_for_day(today),
        "overdue": overdue(tasks),
        "due_today": due_on(tasks, today),
        "needs_prep": [],  # populated by meeting_prep.py state, if present
        "wrap_last_night": last_wrap_note,
    }


def main() -> None:
    ensure_daily_note()
    payload = build_payload()
    prompt = load_prompt("morning_brief")
    message = call_claude(prompt, payload)
    if not message:
        return
    send_whatsapp(message)
    append_to_daily_note("Morning brief", message)


if __name__ == "__main__":
    main()
