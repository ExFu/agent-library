---
name: docket-compact
cadence: nightly
scripts:
  - scheduled-tasks/library-index/index.py
reads:
  - "exfu/derived/index.json"
  - "*/docket/"
writes:
  - "*/docket/archive.jsonl"
  - "*/docket/todo.jsonl"
  - "*/docket/reminders.jsonl"
  - "*/docket/agent-backlog.jsonl"
  - "*/docket/triggers.jsonl"
  - "*/docket/signals.jsonl"
  - "*/docket/fires.jsonl"
depends_on:
  - nightly-index
description: Keeps every docket small and consistent -- archives closed entries, folds sync conflicts, sweeps expired signals, receipts and orphaned mixins, and emits entry-completed signals
---

# Docket compaction librarian

A docket is read whole, from any surface, including a phone through the storage connector. That only stays cheap if the active files stay small and consistent. This librarian is the housekeeping that makes the one-file-per-collection rule safe over time.

Follows: exfu/20260903-1825/ontology.md#docket-mechanics

## Instructions

1. Run the compaction tool, which ships with the ExFu plugin:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/library-index/index.py compact <substrate-root>
   ```

   It performs, for every docket in the index, the deterministic parts in this order and prints what it did:
   - **Fold conflicted copies.** Any `<file> (conflicted copy ...).jsonl` sibling is unioned by `id` into its file: highest `revision`, then latest `updated`, then lexically lowest writer handle wins for mutable rows; immutable rows (signals, receipts) are simply unioned. The sibling is then removed and the fold is noted in the run detail.
   - **Archive.** Entries with `status` `done` or `archived` whose `updated` is more than 30 days old move from the three entry files into `archive.jsonl`, gaining `kind`.
   - **Emit `entry-completed` signals.** For every entry whose status changed to `done` or `archived` since the last run (the index keeps the previous status), append a signal named `entry-completed:<entry id>` unless one already exists for that transition.
   - **Sweep mixins.** Trigger rows whose `target` has been closed or missing for more than 30 days are disarmed and moved to `archive.jsonl`.
   - **Sweep signals** older than 30 days and **receipts** older than 90 days.

2. Check the result. The tool prints per-docket counts (folded, archived, signalled, swept). Sanity-check them: a fold count above zero is worth a line in your detail so the user knows a sync conflict happened and was resolved; an archive count that is a large fraction of a docket suggests the user has stopped closing things, which the daily briefing may want to mention.

3. Never edit a JSONL file by hand in this librarian. If the tool errors, the run is a failure; put the error in your detail line and leave the files as they were.

## What it touches

- Reads: the global index and every docket
- Writes: the docket files listed above, in place, and only in the ways described

## Why it matters

Without compaction the active files grow without bound, sync conflicts accumulate as siblings nobody reads, and orphaned triggers point at entries that no longer exist. With it, a docket read from a phone is always small, and the corkboard of signals never fills up.
