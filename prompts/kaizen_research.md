# Kaizen research

Friday afternoon. Scan what other Claude Code / agent builders have
shipped this week and cross-reference it with the user's own frictions
from the daily notes.

## Input

- `external`: a list of findings (posts, repos, writeups) collected by
  `scripts/kaizen_research.py` over the last 7 days
- `frictions`: aggregated entries from the `Frictions` sections of the
  last 7 daily notes
- `memory_md`: the current `MEMORY.md` contents
- `system_map`: a dump of `scripts/` filenames and one-line descriptions

## Output

Write `memory/kaizen-research-YYYY-MM-DD.md` with:

```markdown
# Kaizen — <date>

## External signal (top 5)
1. <title> — <1-line summary> — <why it's relevant to our system>
   source: <url>

## This week's frictions
- <aggregated friction>, seen <N> times

## Proposed changes (for Sunday review)
### Change: <short name>
- Problem: ...
- Option A: ...
- Option B: ...
- Recommendation: ...
- Risk / what we lose: ...
```

## Rules

- Be ruthless about relevance. If an external finding doesn't map to a
  live friction, cut it.
- Proposals should be small. If a change requires a full refactor,
  say so explicitly — usually the right move is a smaller, testable cut.
- Don't propose adding complexity to paper over a friction. Prefer
  removing things.
- Maximum 5 proposals. Fewer is better.
