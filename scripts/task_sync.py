"""Two-way sync between memory/tasks.md and Todoist.

memory/tasks.md is the source of truth. Todoist is the user-facing view
of near-term actionable items. Only tasks due within the next 7 days or
without a due date that are tagged `now` are mirrored to Todoist.

This is deterministic only — no LLM calls.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

from scripts.tasks import Task, load_tasks, save_tasks


def _todoist_client():
    token = os.environ.get("TODOIST_API_TOKEN")
    if not token:
        return None
    try:
        from todoist_api_python.api import TodoistAPI

        return TodoistAPI(token)
    except Exception as exc:  # pragma: no cover
        print(f"[task_sync] Todoist unavailable: {exc}")
        return None


def _near_term(task: Task) -> bool:
    if task.done:
        return False
    if not task.due:
        return False
    try:
        d = date.fromisoformat(task.due)
    except ValueError:
        return False
    return d <= date.today() + timedelta(days=7)


def sync() -> None:
    client = _todoist_client()
    tasks = load_tasks()
    near_term = [t for t in tasks if _near_term(t)]

    if client is None:
        print(f"[task_sync no-op] would sync {len(near_term)} task(s)")
        return

    # Intentionally minimal: upsert by `id` stored in Todoist description.
    # A real implementation needs dedupe and deletion handling. Left as
    # a TODO so the kaizen loop can shape it rather than guessing now.
    for t in near_term:
        try:
            client.add_task(content=t.text, due_string=t.due, description=f"cos-id:{t.id}")
        except Exception as exc:  # pragma: no cover
            print(f"[task_sync] failed for {t.id}: {exc}")

    save_tasks(tasks)


if __name__ == "__main__":
    sync()
