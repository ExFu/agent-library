---
name: inbox
description: Lightweight quick-capture for thoughts, links, and loose items the user wants to save without deciding where they belong yet. Use when the user says "save this", "add to inbox", "capture that", "don't lose this thought", when they ask what's in their inbox, when they want to process or sort it, or at session start (called by the substrate skill) to flag pending items.
---

# Inbox

Quick-capture log. Things the user wants to dump out of their head without deciding where they belong.

Distinct from reminders. Reminders are time-triggered ("ping me about this on [date]"). Inbox is place-agnostic quick capture ("don't let this thought fall out").

## Where the data lives

`databases/inbox/inbox.md` — a plain markdown log, newest entries at the top, each timestamped.

If the file or the folder doesn't exist, create them on first use. Create `databases/inbox/README.md` alongside the data file describing what this folder is for. Then proceed.

## File format

```
2026-04-20 11:02 — remember to check if Sam's responded about the partnership
2026-04-20 09:14 — idea: offer ExFu as a monthly retainer, not just one-off
2026-04-19 22:47 — https://example.com/article — read later, thinking about onboarding
```

Timestamp: `YYYY-MM-DD HH:MM` in the user's local time.

## Actions

### Capture

Triggers: "save this", "add to inbox", "don't lose that", "capture this"

1. Get a timestamp (user's local time).
2. Prepend a new line to `databases/inbox/inbox.md`.
3. Confirm briefly: "Saved to inbox." (Keep it short — capture should feel frictionless.)

### Review / process

Triggers: "what's in my inbox", "process inbox", "sort my inbox", "clear the inbox"

1. Read the file.
2. For each entry, help the user decide where it belongs:
   - **Reminder?** → hand to the reminders skill, remove from inbox.
   - **Task?** → add to their task manager (via MCP if connected; otherwise flag for them), remove from inbox.
   - **Scope-specific thought?** → move to the relevant `scopes/[name]/` folder, remove from inbox.
   - **Draft or working file?** → move to `scratch/`, remove from inbox.
   - **Noise?** → remove.
   - **Actionable right now?** → do it, then remove.
3. Save remaining items (if any).

### Count (called on session load by `substrate`)

1. Read the file.
2. Count non-empty lines.
3. If 0, say nothing.
4. If >0, mention briefly: "Inbox has [n] items. Want to process them?"
5. Don't force processing — just flag. Capture without friction matters more than a clean inbox.

## Conventions

- Newest first
- No categorisation in the inbox itself — the point is frictionless dump
- Process weekly at minimum; longer than that and it becomes a junk drawer
- If a captured item is obviously actionable right now (quick reply, one-click check), do it rather than file it
- Keep the file flat. Don't subdivide. Inbox is a single stream.

## Dependencies

- `substrate` skill delegates to this skill on session load
- The processing step may hand items to the `reminders` skill or the user's task manager MCP
