---
name: daily-briefing
description: Scheduled task that produces a morning briefing. Pulls due reminders and what fired overnight from the docket, the agent-backlog count, today's calendar, and priority items from connected task tools. Runs daily via Claude Desktop Cowork.
---

# Daily Briefing Scheduled Task

## What this task does

Runs each morning and produces a briefing Cowork session covering:

- **Reminders** -- anything due or overdue from the docket, across scopes
- **Overnight** -- what fired since yesterday's briefing (delivered, drafted, failed), and any reminder rule that has stopped
- **Agent backlog** -- how many things are waiting for the user's agents
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

1. Load the `wow` skill (the user's personal WoW) so the briefing reflects their defaults. `wow` auto-loads `exfu-library`, which reads the index and orients to the substrate.
2. Read `exfu/derived/index.json` to find scopes with a data-bearing `docket/`, and any scope still listing the deprecated `todo/`, `reminders/` or `inbox/` folders.
3. Reminders due or overdue. Read `exfu/derived/due.json` if it is fresh (its `source_hashes` match the docket files it names); otherwise run `python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/library-index/index.py due <library root> --json` to refresh it. Show what is due today or overdue as a short list. Do not deliver anything or write receipts: the dispatcher and the session-start check do that; this is a read-only view. If a personal `<username>-docket` skill is installed, its surface-on-load preferences apply here too.
4. What fired overnight. Read the last 24 hours of result receipts from each docket's `fires.jsonl`: one line per fire in plain words ("Slack: chased the Acme questionnaire, sent 09:00"; "email check ran, nothing new"). Call out any `failed` or `suppressed` result, and any trigger whose `status` is `paused` (three failures in a row) -- a reminder rule that has stopped is exactly what a morning briefing is for.
5. Agent backlog. Count open entries in `docket/agent-backlog.jsonl` across scopes; if any docket has a `backlog-summary.md` from the overnight sweep, lift its stale count. If the total is more than 5, flag it's getting full.
6. Deprecated folders, labelled as such. For any scope the index still lists with `reminders/` or `inbox/`: read the reminder lines whose natural-language rule fires today, and count inbox items. Show them under a one-line heading like "still in the old reminders and inbox folders" so the user knows which shape they came from; a scope mid-migration can have both.
7. If a calendar MCP is connected (Google Calendar, Outlook, etc.), list today's events with times. If not, skip this section.
8. If a task manager MCP is connected (Linear, Asana, ClickUp, Notion, Todoist, etc.), pull the user's top priority items due today or overdue. If not, skip. A docket whose `agent.md` says `todo: tracked in <tool>` tells you which tool to ask.
9. Check `user/context/` and any active scope's context/ for anything pinned for today.
10. Check `exfu/derived/agent-registry.json` for any scheduled-agent health issues (consecutive failures >= 3). If any, add a brief note. If the dispatcher is not registered and the library has reminders with channels, say once that reminders only reach those channels once the hourly dispatcher is set up.

Format as a short morning briefing. Skimmable. No preamble, no sign-off. Plain prose or short lists where useful.

---

## Notes

- The task only runs while Claude Desktop is open
- Each run appears as a Cowork session in the Scheduled sidebar -- past briefings are there to review
- Output lives in that Cowork session; no persistent file is written
- Adjust the prompt as the user's tool stack grows. Start minimal; extend as more MCPs come online.
- Cowork scheduled tasks run in the cloud without the local filesystem, so `index.py` may not be runnable there; `exfu/derived/due.json` and the docket's JSONL files are text and read fine through the storage connector. That is why the briefing reads and never writes receipts.

## Testing

After saving the task, run it manually once from the Scheduled tab to confirm it produces a sensible briefing. If it's empty because nothing is connected yet, that's expected -- it'll fill out as tools are wired up.
