# Librarians

## Why

Substrates drift without maintenance. Inboxes fill up, indexes go stale, external systems fall out of sync. Librarians are the scheduled maintenance that keeps things tidy without the user having to remember.

## How

Each file in this folder defines a maintenance task: what it does, what it touches, when it runs, what it produces. Definitions are agent instructions -- on schedule, Claude in the cadence's scheduled session reads each one and does the work, calling scripts as tools where a definition says to.

In the ExFu convention base, this folder defines the nightly index librarian. Scopes define their own librarians for scope-specific maintenance.

### Store-or-point

- **Stored:** Librarian definition files.
- **Pointer:** "This scope's maintenance is handled by the parent scope's librarians."

### Boundaries

- Librarians are *scheduled maintenance*. Ad hoc capabilities go in skills/. Tasks go in todo/. See `exfu/v0.3/ontology/librarian/` for the full librarian concept.

## What an agent should do

1. Read librarian definitions to understand what maintenance runs for this scope.
2. Don't run librarians ad hoc unless the user asks -- they're designed for scheduled execution.
3. When defining new librarians, make them idempotent.
