---
ontology: todos
applies-to: any-folder-named-todos
copy-on-create: true
default-variant: flat-checklist
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

- `flat-checklist` (default) — what this template describes. Suits most cases.
- `structured-records` (not shown in this example) — one file per todo with frontmatter (assignee, status, related-scope, etc.). Suits cases where todos are more like tickets than reminders.

The user chooses the variant at folder creation. This snapshot reflects the variant chosen; switching variants later requires a migration (a librarian can help).

## What the agent does with this folder

- **Add an item**: append to `todos.md` with date prefix and description. Confirm to the user briefly.
- **Surface due/overdue**: when asked, or as part of the daily briefing, scan dates and report what is due today or overdue.
- **Mark complete**: add `(done YYYY-MM-DD)` annotation and toggle the checkbox.
- **Snooze**: change the date prefix to the new target.
- **Defer scope-level pulls**: if the user's substrate has multiple `todos/` folders (user-tier and in scopes), the agent surfaces only what is relevant to the current conversation context. It does not pull all todos from every folder unless asked.

## Why a snapshot

This file is copied into the actual `todos/` folder when it is created. The folder thereafter follows its own copy. If ExFu updates this template later, existing `todos/` folders are not silently rewritten. The user (or a librarian) decides if and when to refresh a specific folder's snapshot.

## Dependencies

- `exfu/ontologies/todos/schema.yaml` — the structural schema this convention enforces.
- `exfu/ontologies/todos/elicitation.md` — the install-agent prompt for offering this ontology type.
- `exfu/principles/concrete-first.md` — applies when introducing the type to the user during install.
