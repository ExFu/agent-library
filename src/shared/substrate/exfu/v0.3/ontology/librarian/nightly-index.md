---
name: nightly-index
cadence: nightly
scripts:
  - scheduled-tasks/substrate-index/index.py
reads:
  - "*/scope.md"
  - "*/agent.md"
writes:
  - "exfu/derived/index.json"
depends_on: []
description: Walks the substrate and regenerates the global scope index
---

# Nightly index librarian

The canonical ExFu-shipped librarian. Regenerates the global index so that any agent entering the substrate gets the whole picture in one file read: every scope, where it sits, what it contains, which conventions it follows. Typically the first librarian in the nightly cadence because others depend on a fresh index.

## Instructions

1. Run the index script, which ships with the ExFu plugin:

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <substrate-root>
   ```

   The walking and JSON generation are deterministic; the script is the tool for that. Do not hand-build the index.

2. Check the result. The script writes `exfu/derived/index.json` and prints a summary. Sanity-check it:
   - The scope count should be plausible (not zero on an established substrate, not wildly different from the last run).
   - Every scope should resolve an exfu version pin.
   - If the script errored or the output looks wrong, this run is a failure; say what looked wrong in your detail line.

3. Note anomalies worth the user's attention in your detail line: scopes with no `scope.md`, version pins pointing at convention directories that don't exist, a scope count that jumped unexpectedly.

## What it touches

- Reads: every scope.md and agent.md in the substrate (read-only, via the script)
- Writes: `exfu/derived/index.json` (overwritten each run)

## Why it matters

Without the index, an agent has to walk the entire directory tree to understand what exists. With it, one read gives the complete map. Stale indexes are worse than no index -- they misdirect with confidence -- which is why this runs nightly and first.
