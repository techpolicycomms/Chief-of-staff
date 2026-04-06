# Evening wrap

6pm WhatsApp wrap. Input payload:
- `today`: date
- `daily_note`: today's memory/YYYY-MM-DD.md
- `stalled`: tasks that rolled forward today
- `tomorrow`: tomorrow's calendar
- `tomorrow_prep_needed`: high-stakes meetings tomorrow without briefs

## Output

```
🌙 Wrap — <Weekday>

DID
- <2-4 highlights from the daily note>

STALLED
- <tasks that didn't move, only if pattern is worth flagging>

TOMORROW
- <HH:MM title (with attendee)> — <one-line prep status>
```

Return `SILENCE` if the day was empty and tomorrow is empty.

## Rules

- The wrap is not a diary. Only surface what the user will care about at
  9pm tonight or 8am tomorrow.
- If a task has rolled forward 5+ days, flag it by name in STALLED. If
  it's a one-day slip, don't bother.
- Keep the whole message under 200 words.
