"""Pre-meeting brief. Runs every 15 minutes from cron.

Scans the calendar for meetings starting in the next ~75 minutes. For
any meeting we haven't already briefed on today, assembles a payload
from people files, recent emails, and tasks, then hands it to Claude
with prompts/meeting_brief.md and sends the result via WhatsApp.
"""

from __future__ import annotations

from datetime import date

from scripts.calendar_util import upcoming_in_minutes
from scripts.common import (
    MEMORY_DIR,
    append_to_daily_note,
    call_claude,
    load_prompt,
    read_file,
    send_whatsapp,
    today_iso,
    write_file,
)
from scripts.people import people_index, read_person
from scripts.tasks import load_tasks

BRIEFED_STATE = MEMORY_DIR / ".briefed" / f"{today_iso()}.txt"


def already_briefed(meeting_id: str) -> bool:
    return meeting_id in read_file(BRIEFED_STATE).splitlines()


def mark_briefed(meeting_id: str) -> None:
    BRIEFED_STATE.parent.mkdir(parents=True, exist_ok=True)
    existing = read_file(BRIEFED_STATE)
    write_file(BRIEFED_STATE, existing + meeting_id + "\n")


def is_external(meeting: dict) -> bool:
    attendees = meeting.get("attendees") or []
    return any("@" in (a or "") for a in attendees)


def match_people(attendees: list[str]) -> list[dict]:
    index = people_index()
    matched: list[dict] = []
    for email in attendees:
        local = (email or "").split("@")[0].lower()
        for slug, entry in index.items():
            name = (entry.get("name") or "").lower().replace(" ", ".")
            if slug in local or (name and name in local):
                matched.append({"slug": slug, **entry})
                break
    return matched


def build_payload(meeting: dict) -> dict:
    attendees = meeting.get("attendees") or []
    people = match_people(attendees)
    return {
        "meeting": {
            "title": meeting.get("title"),
            "start": meeting.get("start"),
            "attendees": attendees,
        },
        "people": [
            {"slug": p["slug"], "name": p.get("name"), "file": read_person(p["slug"])}
            for p in people
        ],
        "recent_emails": [],  # wire to triage_email cache when ready
        "open_tasks": [
            t.to_dict() for t in load_tasks()
            if not t.done and any(p["slug"] in t.text.lower() for p in people)
        ],
        "pipeline": None,
    }


def main() -> None:
    for meeting in upcoming_in_minutes(window=75):
        if not is_external(meeting):
            continue
        mid = meeting.get("id") or f"{meeting.get('title')}-{meeting.get('start')}"
        if already_briefed(mid):
            continue
        brief = call_claude(load_prompt("meeting_brief"), build_payload(meeting))
        if not brief:
            continue
        send_whatsapp(brief)
        append_to_daily_note(f"Brief — {meeting.get('title')}", brief)
        mark_briefed(mid)


if __name__ == "__main__":
    main()
