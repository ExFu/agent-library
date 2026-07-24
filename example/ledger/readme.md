# Ledger

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/20260724-1831/ontology.md#ledger

This is the library's record of what has been done to it: which migrations have been applied, when the library was created, and by which version. Your librarians write here; you can read it.

Three rules govern this folder:

- **Append-only.** Entries are added, never rewritten. A wrong entry is corrected by a later entry saying so.
- **Never overwritten by an update.** Everything in `exfu/` is replaced when the plugin updates. This folder is not, and must not be -- it is the only record of what state the library is in, and nothing can regenerate it.
- **Not a cache.** `exfu/derived/` is safe to delete and rebuild. This folder is not.

| File | What it records |
|---|---|
| `migrations.md` | Every migration considered, and how it went |
| `install.md` | When this library was created, by which plugin version and surface |
