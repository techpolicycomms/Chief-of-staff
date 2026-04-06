---
description: Force a meeting prep brief now for a specific attendee
argument-hint: <attendee name or slug>
---

Run a full meeting prep for: **$ARGUMENTS**

1. Read `people/$ARGUMENTS.md` (or search `config/people.yml` if the
   argument is a name, not a slug).
2. Pull the last 3 daily notes for any mention.
3. Pull related open tasks from `memory/tasks.md`.
4. Produce a brief in the format from `prompts/meeting_brief.md`.
5. Print the brief to me — do NOT send via WhatsApp from chat. If I
   want to send it, I'll run `python scripts/meeting_prep.py`.
