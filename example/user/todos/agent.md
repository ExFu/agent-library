---
ontology: todos
applies-to: any-folder-named-todos
copy-on-create: true
default-variant: flat-checklist
snapshot-source: exfu/ontologies/todos/agent.md
snapshot-date: 2026-05-21
---

# Ontology: todos

## Why

People doing work accumulate small commitments faster than they can hold in their head: "follow up with Acme on Friday", "draft the Q3 summary", "ask Sam about the partnership". Without somewhere obvious to put them, they slip. With somewhere obvious but no convention, they pile up in inconsistent shapes and the agent cannot help surface what is due.

A todos folder is the obvious place. The convention captured here is what the agent expects to find and how it interacts with the list.

## How

The default shape (the `flat-checklist` variant) is a single `todos.md` file in the folder, formatted as a markdown checklist with each item on its own line:

```
- [ ] 2026-05-23 — Follow up with Acme on the renewal contract terms.
- [ ] 2026-06-01 — Draft Q3 summary for the leadership offsite.
- [x] 2026-05-15 — (done 2026-05-14) Send signed NDA to Acme.
```

Format conventions:

- Date prefix: `YYYY-MM-DD` is the *due* date (or planned date if soft).
- Optional `(done YYYY-MM-DD)` annotation when an item is completed, before the description.
- Description: one line, plain English. Multi-line descriptions go in a separate scratch file referenced from the item.
- Order: newest at the top, completed items intermixed (they age out naturally).

The agent reads `todos.md` on demand (when the user asks about todos, when the daily briefing runs, when a librarian sweep triggers). It does not load todos at every session start by default; that is the user's call via their `wow`.

## Variants

ExFu ships two default variants of this ontology:

- `flat-checklist` (default) — what this template describes. Suits most cases. **This folder uses this variant.**
- `structured-records` — one file per todo with frontmatter. Suits cases where todos are more like tickets than reminders.

## What the agent does with this folder

- **Add an item**: append to `todos.md` with date prefix and description. Confirm to the user briefly.
- **Surface due/overdue**: when asked, or as part of the daily briefing, scan dates and report what is due today or overdue.
- **Mark complete**: add `(done YYYY-MM-DD)` annotation and toggle the checkbox.
- **Snooze**: change the date prefix to the new target.

## Snapshot note

This file was copied from `exfu/ontologies/todos/agent.md` on 2026-05-21 when this folder was created. The folder follows this snapshot, not whatever the upstream template says today. If the upstream template has evolved and Alastair wants to adopt the changes, he runs a refresh on this folder specifically; otherwise the folder is sovereign.

## Dependencies

- `exfu/ontologies/todos/schema.yaml` — the schema this convention enforces.
- The user's `al-todos` skill (in `~/.claude/skills/`) — handles the day-to-day operations against this folder.
