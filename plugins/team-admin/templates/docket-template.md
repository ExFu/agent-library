---
name: {{username}}-docket
description: {{username}}'s docket -- what is open for them and when it gets heard. Use when {{username}} wants to be nudged about something later, wants to capture a thought without sorting it, wants to leave something for their agents to attend to, asks what is due or what has piled up, or wants to complete, snooze or drop an entry. Also called by the exfu-library skill at session start to surface anything due. Triggers on "remind me to X", "don't let me forget", "flag this for [date]", "ping me about this next week", "save this", "capture that", "jot this down", "leave this for my agents", "have my agents look at", "what's due?", "what's on my docket?", "what have I got coming up?", "what's in my backlog?", "process my backlog", or any time the user wants something to surface later or wants frictionless capture.
---

**About this template:** This file is a template used by `setup-docket` to generate each user's personal docket skill. The frontmatter above is what the generated skill's frontmatter will look like. When `setup-docket` runs, it fills in this template with the user's actual preferences and packages the result as their personal docket skill.

---

# Docket -- {{username}}

The docket is the list of what is open: tasks, reminders, and things left for agents to attend to. This skill is the user's everyday way in and out of it. It is not a task manager (most people already have one, and the docket's `todo` file is often a pointer to it) and it is not the dispatcher (a librarian does the firing). It captures, surfaces, completes and snoozes.

## Where the data lives

`{{docket_path}}/` inside the library. Three entry files, one JSON object per line:

- `todo.jsonl` -- tasks, things with a completion state
- `reminders.jsonl` -- nudges, things with a surface time or condition
- `agent-backlog.jsonl` -- things left for agents to attend to (never the user's own in-tray)

and beside them `triggers.jsonl` (when and how an entry gets heard), `signals.jsonl`, `fires.jsonl` (receipts of what fired) and `channels.jsonl` (how the docket reaches {{username}}). If `{{docket_path}}/agent.md` says a file is tracked elsewhere (`todo: tracked in ClickUp`), that file does not exist locally: send tasks to that tool instead.

Reach the files the way this session reaches the library: the filesystem when it is mounted, otherwise the storage connector by path (`get_file_content`, then `create_file` to overwrite the whole file). Both work; the files are small by design. If an entry file does not exist yet, create it on first entry. Never create the folder itself; `scope-setup` does that.

## Record shape

```json
{"id":"20260903T141200Z-7F3A9QK2MB","title":"Chase the Acme security questionnaire","notes":"Sent 20 Aug, Priya said end of month.","agent_notes":"Only surface after the Acme call has happened.","status":"open","created":"2026-09-03T14:12:00Z","updated":"2026-09-03T14:12:00Z","revision":1,"keywords":["acme","security questionnaire","priya"]}
```

- `title` short; `notes` for {{username}}; `agent_notes` for agents: anything about timing, conditions or dependencies in plain prose ("only show when", "if no reply by Friday, suggest escalating"). No other fields: priority, tags and recurrence are prose in `agent_notes`.
- `status` is `open`, `done` (completed) or `archived` (closed without doing).
- `id`: UTC timestamp `YYYYMMDDTHHMMSSZ`, a hyphen, then ten random characters from `0-9A-HJKMNP-TV-Z`. Every id is unique across the whole library.
- `keywords`: three to six words a future search would use. Write them at save time; they are how the docket is found without a search model.
- Editing an entry: rewrite its line with the change, `updated` set to now, `revision` incremented. Never delete a line; set `status` instead. Never touch a line you did not mean to change.

A **reminder** is a `reminders.jsonl` entry plus a trigger in `triggers.jsonl`:

```json
{"id":"20260903T150200Z-A91CQ7ZP4R","target":{"type":"docket-entry","scope":"{{scope_name}}","id":"<entry id>"},"assess":"Surface this reminder.","when":{"mode":"once","at":"2026-09-10T09:00:00","tz":"{{tz}}"},"on":null,"handler":{"kind":"deliver","weight":"light","ref":null},"channel":null,"owner":"{{username}}","status":"armed","created":"...","updated":"...","revision":1}
```

- `when.mode` is `once` (an instant in `at`, zone `tz`), `cron` (a 5-field spec in `spec`, zone `tz`) or `on-signal` (fire when the signal named in `on` appears).
- A rule in words ("every other Monday", "first working day of the month") is resolved now, once, into a `cron` spec or a `once` instant; keep the words in `assess` so a person can see what was meant.
- `channel` is the name of a channel in `channels.jsonl` (or a parent scope's); leave `null` for "tell me in session and on the dashboard".
- Triggers are authored here and fired by the dispatcher librarian; this skill never writes to `fires.jsonl` except during the session-start check (below).

## Actions

### Remind

Triggers: "remind me to X on Y", "don't let me forget Z", "flag this for [date]", "ping me about this next week"

1. Resolve the time in {{username}}'s zone (`{{tz}}`): "Monday" is the coming Monday at 09:00 unless they said a time; "next week" is Monday 09:00; "in three days" is the same time three days on. A repeating rule becomes a `cron` spec.
2. Append the entry to `reminders.jsonl` and its trigger to `triggers.jsonl`. If they named a channel ("on Slack"), set it.
3. Confirm in one line: "Reminder set for Tue 10 Sep, 09:00: chase the Acme questionnaire."
4. If the request is task-shaped (project work, multi-step deliverable), ask once: "This sounds like a task. Want it in [their task tool] instead?"

### Capture

Triggers: "save this", "capture that", "jot this down", "don't lose this thought", "leave this for my agents", "have my agents look at"

1. Append to `agent-backlog.jsonl`: `title` from their words, `notes` anything extra, `agent_notes` what an agent should do with it if they said ("find out whether", "draft a reply", "file it with the Acme notes").
2. Confirm in three words or fewer: "Captured." Capture should feel frictionless.

### Add a task

Triggers: "add a task", "todo: X"

If `agent.md` points tasks elsewhere, add it there (via that tool's connector if connected; otherwise say where it should go). Otherwise append to `todo.jsonl`.

### What's due (called on session load by `exfu-library`)

1. Read `exfu/derived/due.json` if it is present and fresh (its `source_hashes` match the current files; on a filesystem session simply run `python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/library-index/index.py due <library root> --json`, which refreshes it).
2. For each due trigger whose resolved channel is `pull` or absent: write an intent receipt (`python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/library-index/index.py receipt <library root> <occurrence> intent`), present the entry, write the result receipt (`... receipt <library root> <occurrence> result --status delivered`). Triggers with a real channel are left to the dispatcher; do not deliver them twice.
3. Then, briefly: overdue and due reminders as a short list; the count of open backlog entries ("3 things waiting for your agents"); any paused triggers or undelivered/suppressed receipts from the last day. If none of this applies, say nothing. More than five due items: summarise ("Six reminders due -- want to see them?").

{{surface_on_load}}

### Complete / drop

Triggers: "done with X", "I did X", "drop that reminder", "forget about X"

Rewrite the entry's line with `status: done` (or `archived` for dropped), `updated` now, `revision` + 1. Append a signal `{"id": <new id>, "name": "entry-completed:<entry id>", "at": now, "scope": "{{scope_name}}", "source": "{{username}}-docket", "payload": ""}` to `signals.jsonl` so anything waiting on completion can fire. Its triggers are left alone; the compaction librarian sweeps them.

### Snooze

Triggers: "push that to Friday", "move X to next week", "remind me again in a week"

Rewrite the trigger's line with the new `when` (`updated` now, `revision` + 1). Nothing else changes.

### Review the backlog

Triggers: "what's in my backlog", "process my backlog", "what have I left for the agents"

Read `agent-backlog.jsonl` (open entries) and, if present, `backlog-summary.md` beside it (the sweep librarian's suggestions). For each entry, help {{username}} decide: do it now if it is quick; turn it into a reminder or a task; move its substance to the scope it belongs to (context/, databases/); or drop it. Mark entries `done` or `archived` as they are dealt with.

## Conventions

{{conventions}}

- Newest entries at the bottom of each file (append), so ids stay in order.
- Keep `title` short and `agent_notes` honest: an agent reading it cold should know what to do.
- Do not add reminders for things that belong in a real task manager.
- Do not spam on load; the summary form past five items.
- Never write a secret into any docket file.

## Dependencies

- `exfu-library` delegates to this skill on session load.
- `daily-briefing`, if installed, delegates reminder surfacing to this skill.
- The `dispatcher` librarian fires triggers with channels; the `docket-compact` librarian keeps the files small; the `backlog-sweep` librarian writes `backlog-summary.md`.
