---
name: inbox-triage
cadence: nightly
reads:
  - "exfu/derived/index.json"
  - "*/inbox/"
writes:
  - "*/inbox/triage-summary.md"
depends_on:
  - nightly-index
description: Summarises and suggests triage for items sitting in inbox folders across scopes
---

# Inbox triage librarian

Keeps inbox folders from becoming bottomless pits. Inbox is for quick capture; if items sit there too long, the inbox stops being useful. This librarian surfaces what's accumulating and suggests where things might go -- it does not move or delete anything, because final triage needs the user's judgment.

## Instructions

1. Read `exfu/derived/index.json` to find scopes whose inbox folder is data-bearing (not pointer-only, not empty).

2. For each such inbox, read the items (skip any existing `triage-summary.md` -- that's your own output from last time).

3. Write a fresh `triage-summary.md` into that inbox folder (overwrite the old one) containing:
   - How many items, and how old the oldest is.
   - One line per item: what it appears to be, and a suggested destination if one is obvious (a scope's context/, docs/, todo/ -- use the index and the item's content to judge).
   - Flag anything older than 14 days as stale.

   Keep it scannable: short lines, no essays. Top the file with the protective note convention if the folder's agent.md asks for one.

4. Do not move, rename, or delete the user's items. Suggest; never act on the suggestions.

5. In your detail line when recording, note the totals (e.g. "3 inboxes summarised, 7 items, 2 stale") so the next interactive session can mention it to the user.

If no inbox has content, there is nothing to do -- record success with a detail like "all inboxes empty".

## What it touches

- Reads: the global index, then inbox folders across all scopes
- Writes: `triage-summary.md` in each non-empty inbox folder (and nothing else)

## Why it matters

Quick capture only works if someone sweeps up behind it. This librarian is the sweep: the user opens an inbox and finds a fresh, dated summary of what's waiting, instead of an undifferentiated pile.
