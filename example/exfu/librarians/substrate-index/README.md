# substrate-index librarian

## Purpose

Regenerates `_meta/substrate-index.md` from the current substrate folder tree. Each folder gets a Purpose and Holds entry drawn from its `README.md`. The index gives agents a cheap orientation pass instead of having to walk the tree from scratch.

## Contents

- `agent.md` — the librarian convention snapshot (what makes this a valid librarian).
- `instructions.md` — the prompt the daily orchestrator follows. Tells it to run the index script and report.
- `index.py` — the Python script that does the actual folder walk. (Not reproduced in this example; see the current v0.2.x plugin source at `plugin/src/shared/scheduled-tasks/substrate-index/index.py` for the reference implementation. v0.3.0 generalises it to the three-tier discovery rule.)

(Only the README and agent.md are shown in this example, to illustrate the librarian shape. The instructions and script files exist conceptually.)

## Dependencies

- Reads: every folder in the substrate (recursive walk, skipping `.git/`, `node_modules/`, `_trash/`, and reserved system folders).
- Writes: `_meta/substrate-index.md`.
- Run by: the single daily scheduled task registered at install. The task walks `exfu/librarians/`, `user/librarians/`, and every scope's `librarians/` folder, and runs each librarian it finds.

## Cadence

Once nightly. Idempotent: each run overwrites the previous index cleanly. A manual run is also available (the install agent triggers one immediately after wow is generated, so the index exists from day one).

## Why this is the first librarian ExFu ships

Two reasons. **Orientation cost**: without an index, every agent that loads the substrate has to walk it to know what is there. **Drift detection**: comparing two consecutive indexes surfaces what has changed, which is the foundation other librarians can build on (stale-folder flagging, dependency-check, etc.).
