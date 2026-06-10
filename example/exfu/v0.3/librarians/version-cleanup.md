---
name: version-cleanup
cadence: weekly
reads:
  - "exfu/derived/index.json"
  - "exfu/"
writes: []
depends_on:
  - nightly-index
description: Identifies convention base versions no longer referenced by any scope
---

# Version cleanup librarian

Keeps the exfu/ directory tidy by identifying convention versions that no scope references any more. When a user migrates their scopes from v0.3 to a later version, the old convention base still sits in `exfu/` -- dead weight that should be surfaced, never silently deleted.

## Instructions

1. Read `exfu/derived/index.json` and collect every exfu version pin in use across all scopes.

2. List the version directories that actually exist under `exfu/` (e.g. `v0.3`, `v0.6`), and read `exfu/latest.txt` if present.

3. Compare. A version directory is unreferenced if:
   - No scope's `exfu:` pin points at it, and
   - `latest.txt` does not point at it.

4. Delete nothing. If you find unreferenced versions, say so in your detail line when recording (e.g. "v0.2 unreferenced by any scope; candidate for removal") so the next interactive session can offer the cleanup to the user. If everything is referenced, record success with "all versions referenced".

If the index looks stale (no scopes, or older than the last nightly run should allow), record this librarian as failure with a note rather than reasoning from bad data.

## What it touches

- Reads: `exfu/derived/index.json`, `exfu/latest.txt`, version directory names
- Writes: nothing. Removal is always a user decision in an interactive session.

## Why it matters

Version drift is slow and silent. Nobody notices an orphaned convention directory until the substrate feels cluttered. A weekly check keeps the cost at one detail line.
