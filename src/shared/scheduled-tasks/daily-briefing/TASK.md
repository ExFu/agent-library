---
name: daily-briefing
description: Scheduled task that produces a morning briefing. Pulls due reminders, inbox state, today's calendar, and priority items from connected task tools. Runs daily via Claude Desktop Cowork.
---

# Daily Briefing Scheduled Task

## What this task does

Runs each morning and produces a briefing Cowork session covering:

- **Reminders** — anything due or overdue
- **Inbox** — count of items to process
- **Calendar** — today's events (if a calendar MCP is connected)
- **Tasks** — priority items (if a task manager MCP is connected)
- **Anything else flagged** — items pinned in `context/me/` or in any active scope

## One-time setup

1. Open Claude Desktop
2. Go to the **Cowork** tab
3. Click **Scheduled** in the left sidebar
4. Click **+ New task** in the upper right
5. Paste the task prompt below
6. Set the schedule to **Daily**, at a time that suits the user (07:00 is common)
7. Click **Save**

The briefing runs automatically each day while Claude Desktop is open. If missed (laptop closed, machine asleep), it runs next time the app opens.

## Task prompt

Paste the following as the task prompt:

---

Produce this morning's briefing.

1. Load the `wow` skill (the user's personal WoW) so the briefing reflects their defaults. `wow` auto-loads `substrate`, which reads the ways-of-working guide and surfaces reminders/inbox.
2. Use the `reminders` skill to surface anything due or overdue. Show them as a short list.
3. Use the `inbox` skill to check the count. If >5 items, flag it's getting full.
4. If a calendar MCP is connected (Google Calendar, Outlook, etc.), list today's events with times. If not, skip this section.
5. If a task manager MCP is connected (Linear, Asana, ClickUp, Notion, Todoist, etc.), pull the user's top priority items due today or overdue. If not, skip.
6. Check `context/me/` and any active scope READMEs for anything pinned for today.

Format as a short morning briefing. Skimmable. No preamble, no sign-off. Plain prose or short lists where useful.

---

## Notes

- The task only runs while Claude Desktop is open
- Each run appears as a Cowork session in the Scheduled sidebar — past briefings are there to review
- Output lives in that Cowork session; no persistent file is written. If the user wants a rolling log, they can ask Claude to also write the briefing to `scratch/briefings/YYYY-MM-DD.md` — but that's optional, not default.
- Adjust the prompt as the user's tool stack grows. Start minimal; extend as more MCPs come online.

## Testing

After saving the task, run it manually once from the Scheduled tab to confirm it produces a sensible briefing. If it's empty because nothing is connected yet, that's expected — it'll fill out as tools are wired up.
