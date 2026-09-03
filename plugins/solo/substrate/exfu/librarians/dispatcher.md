---
name: dispatcher
cadence: hourly
scripts:
  - scheduled-tasks/library-index/index.py
reads:
  - "exfu/derived/due.json"
  - "*/docket/triggers.jsonl"
  - "*/docket/channels.jsonl"
  - "durable/ledger/grants.md"
writes:
  - "*/docket/fires.jsonl"
  - "*/docket/signals.jsonl"
  - "*/docket/triggers.jsonl"
depends_on: []
description: The library's cron manager -- finds due triggers in the index and hands each to the handler it names, at the weight it names, recording every fire as a receipt
---

# Dispatcher librarian

Every scope may say, in its docket, that at some moment or on some occurrence something should be assessed by an agent, and how. This librarian is the one place those statements become action. It runs on the hourly cadence with the cheapest model available, because on most runs nothing is due and the whole job is one query.

Follows: exfu/20260903-1825/ontology.md#dispatcher

## Hard constraints

- **Do not boot the library.** Do not load the boot skill, the user's way of working, `context/`, or any docket entry file. Your inputs are the due view and the trigger rows it names. The `assess` text on a trigger is the whole brief.
- **Do not act without an intent receipt**, and do not leave a run without a result receipt for everything you attempted.
- **Do not send through a channel marked `send: auto` unless `durable/ledger/grants.md` holds an active grant for it**, the channel is a `dm`, and its target is the trigger's owner. Everything else is drafted.

## Instructions

1. Refresh the index incrementally and ask for the due view:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/library-index/index.py due <substrate-root> --json
   ```

   The tool prints the triggers that are due now for this actor (owner matches the library's actor, or `any`), each with its handler, channel, target entry (title only), the occurrence id, and the channel's resolved `send` mode after checking grants and caps. If the tool reports the index unavailable, it falls back to `exfu/derived/due.json` and says so; if that file is stale it refuses, and this run records `skipped` with that reason.

2. For each due trigger, in the order printed:
   1. Write the intent receipt: `index.py receipt <substrate-root> <occurrence> intent`.
   2. For `any` triggers in a shared scope, re-read the receipts the tool prints back; if another actor's intent for the same occurrence exists and their handle sorts lower than yours, write a `skipped` result and move on.
   3. Do what the handler says:
      - `deliver`: send the target entry (or the `assess` text when there is none) through the channel. If the resolved mode is `draft`, prepare the message where the connector keeps drafts, or leave it in the receipt as `drafted` for the dashboard's ready-to-send list. If it is `auto`, send it and keep the connector's message id as the idempotency key.
      - `agent`: spawn a sub-agent at the trigger's `weight` (light: the cheapest model; medium: a mid model; heavy: the strongest available) with the `assess` text as its entire brief plus the target entry's title, and wait for its result. The sub-agent reports what it did and any signals it observed or produced.
      - `definition`: run the registered definition named by `ref` as the cadence session would, and record its outcome as this trigger's result.
   4. Write the result receipt: `index.py receipt <substrate-root> <occurrence> result --status <delivered|drafted|failed|skipped|suppressed> [--signals name,...] [--key <idempotency key>]`. The tool appends any reported signals to the scope's `signals.jsonl`, disarms a `once` trigger, and pauses a trigger after three consecutive failures.

3. Record the run with a detail line that counts fires by status (e.g. "4 due: 2 delivered, 1 drafted, 1 skipped (claimed by sam)"). If nothing was due, record success with "nothing due".

## What it touches

- Reads: the due view, trigger and channel rows, the grants ledger
- Writes: receipts and signals, and a trigger row only to disarm a `once` or pause a failing one

## Why it matters

This is what lets a reminder written on a phone at midnight reach the user's Slack at nine, an email check feed a follow-up draft, and a heavy piece of research start itself on the day it was asked for -- each with a receipt saying it happened once.
