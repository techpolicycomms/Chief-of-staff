# Chief of Staff

An open-source Claude Code setup that acts as a chief of staff. Inspired by
[Ryan Sarver's writeup](https://x.com/rsarver/status/2041148425366843500) of
"Stella", this repo packages the patterns he described into a runnable
starting point you can fork and adapt.

The goal is a system that:

- Never forgets a commitment
- Handles the small stuff without being asked
- Flags the important stuff without being told
- Gets better every week

## Design rules

Two rules drive every decision in this repo:

1. **Memory is a file system, not a database.** All state lives in flat
   markdown files under `memory/` and `people/`. You can read, grep, edit,
   diff, and back up everything with git. There is no abstraction layer
   between you and what the assistant knows.
2. **LLMs handle judgment, scripts handle everything else.** Anything
   deterministic — reading files, calling APIs, sending messages, comparing
   timestamps — lives in Python under `scripts/`. The LLM layer (Claude Code +
   prompts in `prompts/`) handles synthesis, prioritization, drafting, and
   anything that requires reasoning.

When you feel tempted to push deterministic work through the LLM, resist. When
you feel tempted to hardcode judgment into a script, resist.

## What's in here

```
CLAUDE.md            Top-level instructions Claude reads on every session
MEMORY.md            Long-term, curated memory (people, projects, lessons)
memory/              Daily notes, kaizen research, transient state
people/              One markdown file per person — commitments, history
prompts/             Prompt templates invoked by scripts and slash commands
scripts/             Deterministic Python: APIs, file I/O, scheduling glue
config/              Example config files
.claude/commands/    Claude Code slash commands (/brief, /meeting-prep, ...)
```

## The pieces

### Memory layer
- `memory/YYYY-MM-DD.md` — one file per day, written throughout the day by
  `scripts/daily_note.py` and by Claude during sessions.
- `MEMORY.md` — curated, long-lived context. Claude synthesizes this from the
  daily notes on a schedule. Read on startup to orient.
- `people/<name>.md` — per-person file with relationship history, last
  touchpoint, open commitments (theirs and yours), what they care about.

### Meeting prep and follow-through
- `scripts/meeting_prep.py` — 60 minutes before any external meeting, assembles
  context (prior notes, recent email threads, open action items, pipeline
  stage) and sends a brief to WhatsApp.
- `scripts/process_meetings.py` — pulls meeting notes from Granola (or any
  note-taker with an API), deduplicates, extracts action items, routes your
  tasks to Todoist and commitments from others to `people/<name>.md`.

### Task and priority management
- Source of truth: structured markdown in `memory/tasks.md` (full context and
  history).
- Near-term items sync to Todoist via `scripts/task_sync.py`.
- `scripts/task_sweep.py` runs every evening: overdue, stalled, rolled-forward
  patterns, high-stakes meetings with missing prep.

### Information filtering
- `scripts/triage_email.py` — triages personal and work Gmail, surfaces action
  items, drops noise, auto-files receipts, drafts follow-ups in your voice for
  review.
- `scripts/triage_calendar.py` — flags conflicts, unprepped meetings, gaps.

### Operational rhythm
- `scripts/morning_brief.py` — 9am WhatsApp brief: priorities, overdue,
  today's calendar, anything needing attention before you open your laptop.
- `scripts/evening_wrap.py` — 6pm WhatsApp wrap: what happened, what stalled,
  what to prep for tomorrow.
- Silence if there's nothing to say.

### Kaizen loop
- `scripts/kaizen_research.py` — runs Friday. Scans the Claude Code community,
  collects patterns, writes to `memory/kaizen-research-YYYY-MM-DD.md`.
- `/kaizen-review` slash command — run Sunday. Claude summarizes the week's
  research, your frictions from the daily notes, and proposes concrete changes
  to the system itself.

### Research digest
- `scripts/research_digest.py` — weekly digest of tracked X accounts and
  newsletters, tiered (researchers, VCs, founders, operators), scored, and
  filtered.

## Setup

See [SETUP.md](./SETUP.md) for installation, API keys, and cron schedule.

## Status

Early. This is a scaffold that mirrors the architecture described in the
writeup. Scripts are stubs with clear integration points — you'll need to
wire up your own API keys and adapt the prompts to your voice. The whole
point of the kaizen loop is that the system you end up with six months from
now will look nothing like what you start with.

## License

MIT
