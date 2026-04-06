"""Shared utilities for Chief of Staff scripts.

Design rule: this module does deterministic work only — path resolution,
file I/O, env loading, Claude API calls, WhatsApp delivery. No judgment.
Any script that needs synthesis or prioritization should build a payload
here and hand it to `call_claude` with a prompt from `prompts/`.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(os.environ.get("CHIEF_OF_STAFF_HOME", Path(__file__).resolve().parent.parent))
MEMORY_DIR = ROOT / "memory"
PEOPLE_DIR = ROOT / "people"
PROMPTS_DIR = ROOT / "prompts"
CONFIG_DIR = ROOT / "config"


def today_iso() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def daily_note_path(day: str | None = None) -> Path:
    return MEMORY_DIR / f"{day or today_iso()}.md"


def read_file(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def append_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        if path.exists() and path.stat().st_size > 0 and not text.startswith("\n"):
            f.write("\n")
        f.write(text)


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_prompt(name: str) -> str:
    return read_file(PROMPTS_DIR / f"{name}.md")


def load_yaml(path: Path) -> dict:
    import yaml

    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# --- Claude ---------------------------------------------------------------

def call_claude(prompt: str, payload: dict[str, Any], *, max_tokens: int = 2048) -> str:
    """Call Claude with a prompt template and a JSON payload.

    Returns the model's text output. If no ANTHROPIC_API_KEY is set, returns
    an empty string so callers can treat this as a no-op during setup.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    model = os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")

    user_content = (
        f"{prompt}\n\n---\n\nPayload:\n```json\n"
        f"{json.dumps(payload, indent=2, default=str)}\n```"
    )

    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user_content}],
    )
    return "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")


# --- WhatsApp -------------------------------------------------------------

def send_whatsapp(text: str) -> bool:
    """Send a WhatsApp message via Twilio. Returns True on success, False on
    no-op (missing creds) or empty body. Never raises on missing config."""
    text = (text or "").strip()
    if not text or text == "SILENCE":
        return False

    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    sender = os.environ.get("TWILIO_WHATSAPP_FROM")
    recipient = os.environ.get("WHATSAPP_TO")
    if not all([sid, token, sender, recipient]):
        # No-op during setup: print so the cron log shows it
        print(f"[whatsapp no-op] {text[:200]}")
        return False

    from twilio.rest import Client

    client = Client(sid, token)
    client.messages.create(from_=sender, to=recipient, body=text)
    return True


# --- Daily note helper ----------------------------------------------------

def append_to_daily_note(section: str, body: str, day: str | None = None) -> None:
    """Append a section to today's daily note, creating it if missing."""
    path = daily_note_path(day)
    existing = read_file(path)
    if not existing:
        existing = f"# {day or today_iso()}\n"
        write_file(path, existing)
    append_file(path, f"\n## {section}\n{body.strip()}\n")
