"""Google Calendar reads.

Returns plain dicts (not Google API objects) so callers stay dumb. If
credentials aren't configured, every function returns an empty list and
prints a no-op line — this keeps cron jobs functional during setup.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _service():
    creds_path = os.environ.get("GOOGLE_OAUTH_CREDENTIALS")
    if not creds_path or not Path(creds_path).exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(creds_path, SCOPES)
        return build("calendar", "v3", credentials=creds, cache_discovery=False)
    except Exception as exc:  # pragma: no cover
        print(f"[calendar no-op] {exc}")
        return None


def _rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _simplify(event: dict) -> dict[str, Any]:
    start = event.get("start", {})
    end = event.get("end", {})
    return {
        "id": event.get("id"),
        "title": event.get("summary", "(no title)"),
        "start": start.get("dateTime") or start.get("date"),
        "end": end.get("dateTime") or end.get("date"),
        "attendees": [a.get("email") for a in event.get("attendees", [])],
        "location": event.get("location"),
        "description": event.get("description", ""),
    }


def meetings_for_day(day: date) -> list[dict[str, Any]]:
    svc = _service()
    if svc is None:
        return []
    start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    events = (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=_rfc3339(start),
            timeMax=_rfc3339(end),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    return [_simplify(e) for e in events]


def meetings_range(days: int = 7) -> list[dict[str, Any]]:
    today = date.today()
    return [
        m for i in range(days) for m in meetings_for_day(today + timedelta(days=i))
    ]


def upcoming_in_minutes(window: int = 75) -> list[dict[str, Any]]:
    """Meetings starting within the next `window` minutes."""
    svc = _service()
    if svc is None:
        return []
    now = datetime.now(timezone.utc)
    horizon = now + timedelta(minutes=window)
    events = (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=_rfc3339(now),
            timeMax=_rfc3339(horizon),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    return [_simplify(e) for e in events]
