# Version cleanup librarian

Keeps the exfu/ directory tidy by identifying convention versions that are no longer referenced by any scope.

## What it does

1. Reads the global index (`exfu/derived/index.json`) to find every exfu version pin in use across all scopes.
2. Lists version directories that exist in `exfu/` (e.g. v0.3, v0.6).
3. Compares the two lists.
4. Flags any version directory that is:
   - Not referenced by any scope's `exfu:` pin
   - Not pointed to by `latest`
5. Surfaces unreferenced versions to the user and offers to remove them (with confirmation).

## What it touches

- Reads: `exfu/derived/index.json`, `exfu/latest` (or `latest.txt`), version directory names
- Writes: nothing automatically. Deletion requires user confirmation.

## When it runs

Periodically, after the nightly index has been refreshed. Less frequent than the index itself -- weekly or on-demand is sufficient.

## Why it matters

When a user migrates all their scopes from v0.3 to v0.6, the v0.3 convention base still sits in `exfu/`. It's not hurting anything, but it's dead weight. This librarian surfaces the cleanup opportunity without silently deleting anything.
