"""Nightly task sweep — pattern detection and optional WhatsApp nudge."""

from __future__ import annotations

from datetime import date

from scripts.common import append_to_daily_note, call_claude, load_prompt, send_whatsapp
from scripts.tasks import load_tasks, overdue, stalled
from scripts.calendar_util import meetings_range


def main() -> None:
    tasks = load_tasks()
    payload = {
        "today": date.today().isoformat(),
        "overdue": overdue(tasks),
        "stalled": stalled(tasks),
        "upcoming_meetings": meetings_range(days=7),
    }
    output = call_claude(load_prompt("task_sweep"), payload)
    if not output:
        return

    # The prompt asks Claude to produce a markdown report and, optionally,
    # a trailing line starting with "NUDGE:" with the WhatsApp one-liner.
    report_lines: list[str] = []
    nudge: str | None = None
    for line in output.splitlines():
        if line.strip().startswith("NUDGE:"):
            nudge = line.split("NUDGE:", 1)[1].strip()
        else:
            report_lines.append(line)
    append_to_daily_note("Task sweep", "\n".join(report_lines))
    if nudge:
        send_whatsapp(nudge)


if __name__ == "__main__":
    main()
