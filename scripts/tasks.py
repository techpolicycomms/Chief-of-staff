"""Task store: memory/tasks.md is the source of truth.

Format (one task per block):

    - [ ] <text>
      id: <stable-id>
      created: YYYY-MM-DD
      due: YYYY-MM-DD | null
      project: <name>
      rolled: <count>
      history:
        - YYYY-MM-DD <event>

Completed tasks flip the checkbox to [x]. Never delete tasks — history
matters for the task sweep's stalled-pattern detection.

This module only parses and writes. All judgment (what's overdue worth
nudging about, etc.) lives in prompts/task_sweep.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from scripts.common import MEMORY_DIR, read_file, write_file

TASKS_PATH = MEMORY_DIR / "tasks.md"


@dataclass
class Task:
    id: str
    text: str
    done: bool = False
    created: str = ""
    due: str | None = None
    project: str = ""
    rolled: int = 0
    history: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "done": self.done,
            "created": self.created,
            "due": self.due,
            "project": self.project,
            "rolled": self.rolled,
            "history": list(self.history),
        }


def _parse(raw: str) -> list[Task]:
    tasks: list[Task] = []
    current: Task | None = None
    in_history = False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
            if current:
                tasks.append(current)
            done = stripped.startswith("- [x]")
            text = stripped[5:].strip()
            current = Task(id="", text=text, done=done)
            in_history = False
            continue
        if current is None:
            continue
        if stripped.startswith("history:"):
            in_history = True
            continue
        if in_history and stripped.startswith("-"):
            current.history.append(stripped[1:].strip())
            continue
        in_history = False
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if key == "id":
                current.id = value
            elif key == "created":
                current.created = value
            elif key == "due":
                current.due = None if value in ("null", "") else value
            elif key == "project":
                current.project = value
            elif key == "rolled":
                try:
                    current.rolled = int(value)
                except ValueError:
                    current.rolled = 0
    if current:
        tasks.append(current)
    return tasks


def load_tasks() -> list[Task]:
    return _parse(read_file(TASKS_PATH))


def _format(task: Task) -> str:
    box = "[x]" if task.done else "[ ]"
    lines = [
        f"- {box} {task.text}",
        f"  id: {task.id}",
        f"  created: {task.created}",
        f"  due: {task.due if task.due else 'null'}",
        f"  project: {task.project}",
        f"  rolled: {task.rolled}",
        "  history:",
    ]
    for event in task.history:
        lines.append(f"    - {event}")
    return "\n".join(lines)


def save_tasks(tasks: list[Task]) -> None:
    header = "# Tasks\n\nSource of truth. Near-term items sync to Todoist via task_sync.py.\n\n"
    body = "\n\n".join(_format(t) for t in tasks)
    write_file(TASKS_PATH, header + body + "\n")


# --- Query helpers (deterministic only) ----------------------------------


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def overdue(tasks: list[Task], as_of: date | None = None) -> list[dict[str, Any]]:
    today = as_of or date.today()
    out: list[dict[str, Any]] = []
    for t in tasks:
        if t.done:
            continue
        d = _parse_date(t.due)
        if d and d < today:
            out.append(t.to_dict())
    return out


def due_on(tasks: list[Task], day: date) -> list[dict[str, Any]]:
    return [t.to_dict() for t in tasks if not t.done and _parse_date(t.due) == day]


def stalled(tasks: list[Task], rolled_threshold: int = 5) -> list[dict[str, Any]]:
    return [t.to_dict() for t in tasks if not t.done and t.rolled >= rolled_threshold]
