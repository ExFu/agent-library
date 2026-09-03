---
name: backlog-sweep
cadence: nightly
reads:
  - "exfu/derived/index.json"
  - "*/docket/agent-backlog.jsonl"
  - "*/inbox/"
writes:
  - "*/docket/backlog-summary.md"
  - "*/inbox/triage-summary.md"
depends_on:
  - nightly-index
description: Summarises and suggests homes for items sitting in agent backlogs across scopes (and in deprecated inbox folders)
---

# Backlog sweep librarian

Keeps agent backlogs from becoming bottomless pits. The backlog is where the user leaves things for their agents to attend to; if items sit there too long, it stops being useful. This librarian surfaces what's accumulating and suggests where things might go -- it does not move, close or delete anything, because final routing needs the user's judgment.

Follows: exfu/20260903-1825/ontology.md#docket

## Instructions

1. Read `exfu/derived/index.json` to find scopes whose docket has a data-bearing `agent-backlog.jsonl`, and scopes still carrying a deprecated `inbox/` folder with content.

2. For each backlog, read the open entries (`status: open`) from `docket/agent-backlog.jsonl`. For a deprecated inbox, read its item files (skip any existing `triage-summary.md`, your own output from last time).

3. Write a fresh summary (overwrite the old one): `docket/backlog-summary.md` beside the backlog, or `inbox/triage-summary.md` for a deprecated inbox, containing:
   - How many open items, and how old the oldest is.
   - One line per item: what it appears to be, and a suggested destination if one is obvious (a scope's context/, its docket's todo or reminders, databases/ -- use the index and the item's `title`, `notes` and `agent_notes` to judge). If an item's `agent_notes` asks for something an agent can simply do (a quick lookup, a one-line reply), say so; do not do it here.
   - Flag anything older than 14 days as stale.

   Keep it scannable: short lines, no essays. Top the file with the protective note convention if the folder's agent.md asks for one.

4. Do not modify the JSONL files, and do not move, rename or delete the user's items. Suggest; never act on the suggestions.

5. In your detail line when recording, note the totals (e.g. "3 backlogs summarised, 7 items, 2 stale; 1 deprecated inbox") so the next interactive session can mention it to the user.

If no backlog has open items, there is nothing to do -- record success with a detail like "all backlogs empty".

## What it touches

- Reads: the global index, then agent backlogs (and deprecated inboxes) across all scopes
- Writes: one summary file per non-empty backlog (and nothing else)

## Why it matters

Leaving things for your agents only works if someone sweeps up behind it. This librarian is the sweep: the user opens a docket and finds a fresh, dated summary of what is waiting for attention, instead of an undifferentiated pile.
