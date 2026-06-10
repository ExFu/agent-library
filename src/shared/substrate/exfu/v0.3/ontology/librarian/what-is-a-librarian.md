# What is a librarian

A librarian is a scheduled maintenance agent that keeps part of the substrate tidy and current. Librarians run on a schedule (nightly, weekly, or on-trigger), perform a defined maintenance task, and are idempotent -- running one twice produces the same result as running it once.

## How librarians work

A librarian definition is a file in a scope's `librarians/` folder. It is *agent instructions*: a markdown file an agent reads cold and acts on. It describes:

1. **What it does** -- the maintenance task, as instructions in plain language
2. **What it touches** -- which folders, files, or external systems
3. **When it runs** -- the schedule (nightly, weekly, etc.) or trigger condition
4. **What it produces** -- any output files, reports, or state changes

A scheduled task (one per cadence) is the execution environment: Claude in that session reads each due definition and carries out the work itself, with judgment. Where a definition references a script, the script is a tool the agent calls -- deterministic legwork like walking the tree or rendering HTML -- never a replacement for the agentic work.

## ExFu-shipped librarians

The convention base ships definitions for:

- **Nightly index** -- walks the entire substrate and regenerates the global index at `exfu/derived/index.json`. See `nightly-index.md` in this directory.
- **Inbox sweep** -- reviews inbox/ items across scopes and offers to triage them (definition TBD).
- **Version cleanup** -- checks whether old exfu/ version directories are still referenced by any scope and flags unreferenced versions for deletion (definition TBD).

## Scope-level librarians

Any scope can define its own librarians for scope-specific maintenance: reconciling todos with an external tracker, archiving stale context, refreshing a database from an API. These definitions live in the scope's `librarians/` folder and follow the same format.
