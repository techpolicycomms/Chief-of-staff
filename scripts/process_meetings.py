"""Meeting follow-through: Granola notes -> tasks + people files + memory.

Deduplicates by Granola note ID using memory/.processed_meetings.txt.
LLM handles extraction via prompts/meeting_followup.md; this script only
calls the API, writes files, and pushes tasks to Todoist.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date

import requests

from scripts.common import MEMORY_DIR, append_to_daily_note, call_claude, load_prompt, read_file, write_file
from scripts.people import append_to_person
from scripts.tasks import Task, load_tasks, save_tasks

PROCESSED = MEMORY_DIR / ".processed_meetings.txt"


def _already(note_id: str) -> bool:
    return note_id in read_file(PROCESSED).splitlines()


def _mark(note_id: str) -> None:
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    write_file(PROCESSED, read_file(PROCESSED) + note_id + "\n")


def fetch_granola_notes() -> list[dict]:
    api_key = os.environ.get("GRANOLA_API_KEY")
    base = os.environ.get("GRANOLA_BASE_URL", "https://api.granola.ai")
    if not api_key:
        return []
    try:
        r = requests.get(
            f"{base}/v1/notes",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"since": date.today().isoformat()},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("notes", [])
    except Exception as exc:  # pragma: no cover
        print(f"[granola no-op] {exc}")
        return []


def apply_extraction(extraction: dict) -> None:
    tasks = load_tasks()
    for t in extraction.get("user_tasks", []):
        tasks.append(
            Task(
                id=str(uuid.uuid4())[:8],
                text=t["text"],
                created=date.today().isoformat(),
                due=t.get("due"),
                project=t.get("project", ""),
                history=[f"{date.today().isoformat()} created from meeting"],
            )
        )
    save_tasks(tasks)

    for c in extraction.get("others_commitments", []):
        append_to_person(
            c["person_slug"],
            "Open commitments (they owe)",
            f"{c['text']}"
            + (f" (due {c['due']})" if c.get("due") else "")
            + f" — added {date.today().isoformat()}",
        )

    for update in (extraction.get("memory_updates") or {}).get("people", []) or []:
        append_to_person(update["slug"], "History", update["append"])


def main() -> None:
    prompt = load_prompt("meeting_followup")
    for note in fetch_granola_notes():
        note_id = str(note.get("id"))
        if not note_id or _already(note_id):
            continue
        raw = call_claude(prompt, note)
        if not raw:
            continue
        try:
            extraction = json.loads(raw)
        except json.JSONDecodeError:
            print(f"[process_meetings] bad JSON for note {note_id}")
            continue
        apply_extraction(extraction)
        append_to_daily_note(
            f"Meeting — {note.get('title', note_id)}",
            extraction.get("summary", ""),
        )
        _mark(note_id)


if __name__ == "__main__":
    main()
