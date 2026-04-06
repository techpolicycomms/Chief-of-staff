# Setup

## Prerequisites

- Python 3.11+
- [Claude Code](https://claude.com/claude-code) installed and authenticated
- Accounts + API keys for the integrations you want:
  - Gmail (OAuth credentials)
  - Google Calendar (same OAuth)
  - Todoist (API token)
  - Granola (or any meeting note-taker with an API)
  - WhatsApp delivery — Twilio, WhatsApp Business Cloud API, or similar
  - Anthropic API key (for scheduled scripts that call Claude directly)

You only need the integrations you plan to use. Every script degrades to a
no-op if its env vars are missing.

## Install

```bash
git clone <this repo> chief-of-staff
cd chief-of-staff
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill in .env
```

## Configure persona and voice

- `config/persona.md` — name, tone, what the assistant should and shouldn't do
- `config/voice.md` — samples of your writing so drafts sound like you
- `config/people.yml` — tiered list of people and contexts (LPs, portfolio,
  board, etc.)
- `config/research_sources.yml` — X accounts and newsletters for the weekly
  digest

## Seed memory

Open `MEMORY.md` and fill in the template. Keep it short at first — the
kaizen loop will grow it naturally. Create at least one `people/<name>.md`
file so the meeting-prep flow has something to reference.

## Cron schedule

See `config/cron.example` for the recommended crontab. Minimum useful
schedule:

```
0 9  * * *    python scripts/morning_brief.py
*/15 * * * *  python scripts/meeting_prep.py     # checks next 75 min
*/30 * * * *  python scripts/process_meetings.py
0 18 * * *    python scripts/evening_wrap.py
30 22 * * *   python scripts/task_sweep.py
0 17 * * 5    python scripts/kaizen_research.py  # Friday 5pm
0 8  * * 0    python scripts/research_digest.py  # Sunday 8am
```

## Using it day-to-day

- Start a Claude Code session from the repo root. Claude reads `CLAUDE.md`
  on startup and orients on `MEMORY.md` and today's daily note.
- Use slash commands for common flows:
  - `/brief` — ad-hoc brief on a person, project, or meeting
  - `/meeting-prep <attendee>` — force a meeting brief now
  - `/task-sweep` — run the sweep interactively
  - `/kaizen-review` — Sunday review of the week's research and frictions
  - `/remember <fact>` — capture something to the daily note immediately
- Everything else happens on its cron schedule in the background.

## Backups

Commit `memory/`, `people/`, and `MEMORY.md` to a private git remote daily.
A sample `scripts/backup.sh` is included. Do not commit `.env` or any file
under `config/secrets/`.
