# Weekly research digest

Sunday morning. Take a week of X posts and newsletter items collected by
`scripts/research_digest.py`, tier them, filter for relevance, and
produce a readable digest.

## Input

- `items`: list of `{source, tier, title, url, text, engagement}`
- `focus`: top 3 active focus areas from MEMORY.md
- `boost_keywords`, `demote_keywords` from config

## Output

```markdown
# Research digest — week of <date>

## AI researchers
- **<title>** — <2-line takeaway> — [link]

## VCs
- ...

## Founders
- ...

## Operators
- ...
```

## Rules

- Cap each tier at 5 items. Better to leave things out than to flood.
- Skip items whose text has no connection to the user's focus areas or
  boost keywords.
- Never include an item twice even if it appeared in multiple sources —
  merge.
- Bias toward concrete takeaways over vibes. If the takeaway is "this is
  interesting", cut it.
