# Folder type: librarians/

Scheduled maintenance definitions for this scope. Where you describe what should happen automatically to keep the scope tidy and current.

**Analogy:** cron jobs.

## Default behaviour

Librarian definitions describe maintenance tasks: sweep the inbox, reconcile todos with the external tracker, archive stale content, update the index. Each definition is a file explaining what the librarian does, when it runs, and what it touches.

Librarians are *agent instructions*, not running code. On the appropriate schedule, an agent reads each definition and carries out the work, calling scripts as tools where a definition says to.

## Store-or-point

- **Stored:** Librarian definition files describing maintenance tasks for this scope.
- **Pointer:** "This scope's maintenance is handled by the parent scope's librarians."

## Boundaries

- Librarians are *maintenance automation*. Ad hoc agent capabilities go in skills/. Task tracking goes in todo/. Background info goes in context/.
- A librarian should be idempotent -- running it twice produces the same result as running it once.

See also: `exfu/v0.3/ontology/librarian/` for the full definition of what a librarian is.
