# Task sweep

Nightly sweep of `memory/tasks.md`. Input:
- `tasks`: parsed task list with status, due date, created date, history
  of "rolled forward" events
- `upcoming_meetings`: next 7 days of meetings with stakes tag

## Output

A short markdown report appended to today's daily note under
`## Task sweep`, plus — only if there's a genuine pattern worth
interrupting the user for — a one-line WhatsApp nudge.

```markdown
## Task sweep

OVERDUE: <N>
STALLED (rolled 5+ times): <list>
HIGH-STAKES AT RISK:
  - Tuesday board call — prep task not started

PROPOSED: <what Stella thinks should happen>
```

## Rules

- Never nudge WhatsApp just because there are overdue items. Only nudge
  if there's a stalled pattern or a high-stakes meeting with unmade prep.
- If nothing is actionable, write the sweep report and return `SILENCE`
  for the nudge.
- Surface at most 3 proposals. More than that is noise.
