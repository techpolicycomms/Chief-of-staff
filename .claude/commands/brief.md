---
description: Ad-hoc brief on a person, project, or meeting
argument-hint: <person | project | meeting title>
---

You are producing an ad-hoc brief on: **$ARGUMENTS**

1. Search `people/` for a matching slug and read the file if found.
2. Search `memory/` (daily notes from the last 30 days) and `MEMORY.md`
   for relevant mentions.
3. Search `memory/tasks.md` for related open tasks.
4. If the argument looks like a meeting on the calendar, also scan for
   prior meetings with the same attendees.

Produce a brief in the format from `prompts/meeting_brief.md`. Keep it
phone-sized. If context is thin, start the brief with `⚠ Thin context`.
