# Meeting follow-through

You are processing meeting notes pulled from the note-taker (Granola or
similar). Input is the raw notes plus attendee list. Output is a JSON
object:

```json
{
  "summary": "<2-3 sentence summary>",
  "user_tasks": [
    {"text": "...", "due": "YYYY-MM-DD or null", "project": "..."}
  ],
  "others_commitments": [
    {"person_slug": "...", "text": "...", "due": "YYYY-MM-DD or null"}
  ],
  "decisions": ["..."],
  "memory_updates": {
    "people": [
      {"slug": "...", "append": "<one-line relationship update>"}
    ],
    "memory_md": "<one-line update, or empty string>"
  }
}
```

## Rules

- Distinguish user tasks from commitments others made. This is the most
  important distinction in the whole system — getting it wrong means the
  user chases themselves for things other people owe them, or vice versa.
- Use slugs from `config/people.yml` — never free-text names in
  `person_slug`.
- Only propose `memory_md` updates for things that will still matter in a
  month. Everything else goes in daily notes or people files.
- Never invent due dates. If the notes don't say, use `null`.
