"""Gmail triage across one or more accounts.

Pulls unread messages, sends a batch to Claude with prompts/email_triage.md,
and routes the decisions:
  - action     -> creates a task
  - reply_draft-> saves a draft under memory/drafts/
  - archive    -> marks as read (no send, no delete)
  - receipt    -> appends to memory/expenses-QX-YYYY.md
  - surface    -> appends to today's daily note under "Email surfaced"
"""

from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import date
from pathlib import Path

from scripts.common import MEMORY_DIR, append_to_daily_note, call_claude, load_prompt, write_file
from scripts.tasks import Task, load_tasks, save_tasks

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
DRAFTS_DIR = MEMORY_DIR / "drafts"


def _gmail_service(account: str):
    # Expects one credential file per account at
    # config/secrets/gmail_<account>.json, produced by your OAuth flow.
    from pathlib import Path as _P

    path = _P("config/secrets") / f"gmail_{account}.json"
    if not path.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(str(path), SCOPES)
        return build("gmail", "v1", credentials=creds, cache_discovery=False)
    except Exception as exc:  # pragma: no cover
        print(f"[gmail no-op] {account}: {exc}")
        return None


def _summarize_message(svc, msg_id: str) -> dict:
    msg = svc.users().messages().get(userId="me", id=msg_id, format="metadata",
                                      metadataHeaders=["From", "Subject", "Date"]).execute()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    return {
        "message_id": msg_id,
        "sender": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "snippet": msg.get("snippet", ""),
        "thread_id": msg.get("threadId"),
    }


def _fetch_unread(account: str, limit: int = 30) -> list[dict]:
    svc = _gmail_service(account)
    if svc is None:
        return []
    resp = svc.users().messages().list(userId="me", q="is:unread", maxResults=limit).execute()
    return [_summarize_message(svc, m["id"]) for m in resp.get("messages", [])]


def _apply_decision(account: str, decision: dict) -> None:
    svc = _gmail_service(account)
    mid = decision.get("message_id")
    kind = decision.get("decision")

    if kind == "action" and decision.get("task"):
        tasks = load_tasks()
        t = decision["task"]
        tasks.append(
            Task(
                id=str(uuid.uuid4())[:8],
                text=t["text"],
                created=date.today().isoformat(),
                due=t.get("due"),
                project="email",
                history=[f"{date.today().isoformat()} from email {mid}"],
            )
        )
        save_tasks(tasks)

    elif kind == "reply_draft" and decision.get("draft"):
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        write_file(DRAFTS_DIR / f"{mid}.md", decision["draft"])

    elif kind == "receipt" and decision.get("receipt"):
        r = decision["receipt"]
        quarter = r.get("quarter", f"Q?-{date.today().year}")
        path = MEMORY_DIR / f"expenses-{quarter}.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else f"# Expenses {quarter}\n\n"
        line = f"- {date.today().isoformat()} {r.get('vendor','')} — {r.get('amount','')}\n"
        write_file(path, existing + line)

    elif kind == "surface":
        append_to_daily_note("Email surfaced", f"- {decision.get('reason','')} ({mid})")

    # Mark read in all cases except reply_draft (user hasn't responded yet)
    if kind in {"action", "archive", "receipt", "surface"} and svc is not None:
        try:
            svc.users().messages().modify(
                userId="me", id=mid, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        except Exception as exc:  # pragma: no cover
            print(f"[gmail] mark read failed {mid}: {exc}")


def main() -> None:
    accounts = os.environ.get("GMAIL_ACCOUNTS", "personal").split(",")
    prompt = load_prompt("email_triage")
    for account in accounts:
        account = account.strip()
        if not account:
            continue
        messages = _fetch_unread(account)
        if not messages:
            continue
        raw = call_claude(prompt, {"messages": messages}, max_tokens=4096)
        if not raw:
            continue
        try:
            decisions = json.loads(raw)
        except json.JSONDecodeError:
            print(f"[triage_email] bad JSON from Claude for {account}")
            continue
        for d in decisions:
            _apply_decision(account, d)


if __name__ == "__main__":
    main()
