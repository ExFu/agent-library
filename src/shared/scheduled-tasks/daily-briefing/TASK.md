---
name: daily-briefing
description: Scheduled task that produces a morning briefing. Pulls due reminders, inbox state, today's calendar, and priority items from connected task tools. Runs daily via Claude Desktop Cowork.
---

# Daily Briefing Scheduled Task

## What this task does

Runs each morning and produces a briefing Cowork session covering:

- **Reminders** -- anything due or overdue from reminders folders across scopes
- **Inbox** -- count of unsorted items across inbox folders
- **Calendar** -- today's events (if a calendar MCP is connected)
- **Tasks** -- priority items (if a task manager MCP is connected)
- **Anything else flagged** -- items pinned in user/context/ or in any active scope's context/

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

1. Load the `wow` skill (the user's personal WoW) so the briefing reflects their defaults. `wow` auto-loads `substrate`, which reads the index and orients to the substrate.
2. Read `exfu/derived/index.json` to find scopes with populated reminders, inbox, and todo folders.
3. Check reminders folders across scopes for anything due or overdue. Show them as a short list.
4. Check inbox folders across scopes. If total unsorted items > 5, flag it's getting full.
5. If a calendar MCP is connected (Google Calendar, Outlook, etc.), list today's events with times. If not, skip this section.
6. If a task manager MCP is connected (Linear, Asana, ClickUp, Notion, Todoist, etc.), pull the user's top priority items due today or overdue. If not, skip.
7. Check `user/context/` and any active scope's context/ for anything pinned for today.
8. Check `exfu/derived/agent-registry.json` for any scheduled-agent health issues (consecutive failures >= 3). If any, add a brief note.

Format as a short morning briefing. Skimmable. No preamble, no sign-off. Plain prose or short lists where useful.

---

## Notes

- The task only runs while Claude Desktop is open
- Each run appears as a Cowork session in the Scheduled sidebar -- past briefings are there to review
- Output lives in that Cowork session; no persistent file is written
- Adjust the prompt as the user's tool stack grows. Start minimal; extend as more MCPs come online.

## Testing

After saving the task, run it manually once from the Scheduled tab to confirm it produces a sensible briefing. If it's empty because nothing is connected yet, that's expected -- it'll fill out as tools are wired up.
