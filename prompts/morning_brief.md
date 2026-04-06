# Morning brief

9am WhatsApp brief. Input payload:
- `today`: date
- `calendar`: today's meetings
- `overdue`: overdue tasks from memory/tasks.md
- `due_today`: tasks due today
- `needs_prep`: high-stakes meetings today without a brief yet
- `wrap_last_night`: yesterday's evening wrap, if present

## Output

One WhatsApp message. Phone-friendly. If there's genuinely nothing to
say, return the exact string `SILENCE` and nothing else — the script
will skip sending.

```
☀️ <Weekday> <Mon DD>

TOP 3
1. ...
2. ...
3. ...

CALENDAR
- HH:MM <title> (with <attendee>)
- ...

FLAGS
- <overdue, unprepped, anything that needs attention before laptop opens>
```

## Rules

- Maximum 3 items in TOP 3, even if there are more priorities. Force the
  pick.
- Drop the CALENDAR section if the day is empty.
- Drop the FLAGS section if there's nothing to flag.
- Never more than ~200 words.
