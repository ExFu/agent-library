---
name: reminders
description: Manage the user's lightweight reminder system. Use when the user wants to be nudged about something at a future point, asks to see their reminder list, or wants to complete or snooze a reminder. Also called by the substrate skill at session start to surface anything due or overdue. Triggers on "remind me to X", "don't let me forget", "don't let that slip", "I'll forget this", "flag this for [date]", "ping me about this next week", "what did I say I'd follow up on?", "what have I got coming up?", or any time the user wants to ensure something surfaces later.
---

# Reminders

Lightweight reminder system. Not a task manager. Reminders are Claude's own nudges to the user ("ask me Monday if I still want to pursue Acme") — separate from whatever task tool they actually use.

## Where the data lives

`databases/reminders/reminders.md` — a single markdown checklist, newest entries at the top.

If the file or the folder doesn't exist, create them on first use. Create `databases/reminders/README.md` alongside the data file describing what this folder is for. Then proceed.

## File format

```
- [ ] 2026-04-21 — Ask me if I still want to pursue the Acme deal. (low priority, monday review)
- [ ] 2026-04-25 — Check Rachel's feedback on the pitch deck.
- [x] 2026-04-15 — (done 2026-04-14) Tax filing deadline.
```

- Unchecked = pending
- Checked = completed, kept for reference
- Date after `[ ]` = when to surface
- Content after the dash = what to remind, optional parenthetical context

## Actions

### Create

Triggers: "remind me to X on Y", "don't let me forget Z", "flag this for [date]"

1. Parse the date. Resolve natural language ("monday", "next week", "in three days") to YYYY-MM-DD using today's date.
2. Prepend a new line to `databases/reminders/reminders.md`.
3. Confirm: "Reminder saved for [date]: [what]."

### Check (called on session load by `substrate`)

1. Read the file.
2. Find anything unchecked where date ≤ today.
3. If none, don't mention reminders — silence is fine.
4. If any, present a short list at the top of the session:

```
Due reminders:
- 2026-04-20 — [what]
- 2026-04-18 — [what] (overdue)

Want to action any of these?
```

If more than five are due or overdue, summarise rather than dump the list: "Six reminders due or overdue — want to see them?"

### Complete

Triggers: "I did X", "checked off X", "done with [reminder]"

Flip `[ ]` to `[x]` on the matching line. Prepend `(done YYYY-MM-DD)` after the dash.

### Snooze / reschedule

Triggers: "push that to Friday", "move X to next week"

Update the date on the matching line. No other change.

### Purge completed

Quarterly, offer to remove completed entries older than 90 days. Move them via the standard `_DELETED_` delete workflow rather than hard-delete.

## Conventions

- New reminders go at the top of the file
- Don't add reminders for things that belong in a real task manager (project work, multi-step deliverables). If the user's request looks task-shaped, ask: "This sounds like a task — want me to add it to [their task tool] instead of reminders?"
- Don't spam on load. Use the summary form above if there are more than five.
- Keep the file flat. One line per reminder.

## Dependencies

- `substrate` skill delegates to this skill on session load
- If `daily-briefing` is installed, it also delegates reminder surfacing to this skill
