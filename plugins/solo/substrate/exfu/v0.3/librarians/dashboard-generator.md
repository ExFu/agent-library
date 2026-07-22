---
name: dashboard-generator
cadence: nightly
scripts:
  - scheduled-tasks/scheduled-agents/dashboard-generator.py
reads:
  - "exfu/derived/index.json"
  - "exfu/derived/agent-registry.json"
  - "exfu/derived/agent-log.json"
  - "*/todo/"
  - "*/reminders/"
  - "*/inbox/"
writes:
  - "exfu/visualisations/dashboard/index.html"
depends_on:
  - nightly-index
description: Generates the library dashboard, a static HTML page with the scope map, agent health, workspace views, and the instruction basket
---

# Dashboard generator librarian

The substrate is powerful but invisible: the user interacts with it through conversation and never sees the whole picture at once. This librarian produces a single-page HTML dashboard at `exfu/visualisations/dashboard/index.html` -- open one file and see your scopes, their health, what ran overnight, and what's on your plate. It is a snapshot of the last run, not a live feed.

## Instructions

1. Run the generator script, which ships with the ExFu plugin:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/dashboard-generator.py <substrate-root>
   ```

   Assembling HTML from the derived JSON files is deterministic; the script is the tool for that. Do not hand-build the page.

2. Check the result:
   - `exfu/visualisations/dashboard/index.html` exists and was just modified.
   - It is non-trivial in size (an established substrate produces at least several KB).
   - If the script errored, this run is a failure; put the error in your detail line.

3. Run this librarian last in the nightly cadence if you have the choice -- it renders what the others produced, so the freshest inputs make the truest dashboard.

## What the dashboard shows

1. **Substrate map** -- every scope as a card: name, purpose, folder-type population, version pin, parent/child relationships. A conceptual map, not a filesystem tree.
2. **Librarian dashboard** -- registered librarians with health indicators, last run, cadence, and recent history from the log.
3. **Workspace views** -- aggregated todo, reminders, and inbox items across scopes. Data-bearing folders show content; pointer folders show where the data lives instead (e.g. "Managed in ClickUp", linked when the folder names a URL). Reminders group by date: overdue, coming up, the rest.
4. **How it works** -- the core ontology rendered as a visual reference: the folder-type catalogue as cards, the full conventions as collapsible sections.
5. **The Action Basket** -- the page's controls (tick a task, mark for deletion, create forms, ask-about inputs) do not write anything; each queues an editable instruction in a basket the user copies to their AI, or opens as a prefilled Claude Cowork session via deep link. Queued changes render with a dashed "queued" style until an agent actually makes them and regenerates the page.

## What it touches

- Reads: the derived JSON files (index, registry, log) plus todo/, reminders/, and inbox/ content across scopes (via the script)
- Writes: `exfu/visualisations/dashboard/index.html` (overwritten each run)

## Why it matters

It answers three questions in seconds: "What do I have?", "Is it healthy?", and "What's on my plate?"
