# Ledger

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/20260903-1743/ontology.md#ledger

This is the logbook: which migrations have been applied, when the library was created, and by which version. It lives inside `durable/`, the library's permanent record. Your librarians write here; you can read it.

Three rules govern this folder:

- **Append-only.** Entries are added, never rewritten. A wrong entry is corrected by a later entry saying so.
- **Never overwritten by an update.** A refresh replaces `exfu/`; it never touches `durable/`, `user/`, or `scopes/`. This is the only record of what state the library is in, and nothing can regenerate it.
- **Not a cache.** `exfu/derived/` is safe to delete and rebuild. This folder is not.

| File | What it records |
|---|---|
| `migrations.md` | Every migration considered, and how it went, scope by scope where a migration works that way |
| `install.md` | When this library was created, by which plugin version and surface |
| `grants.md` | Consent you gave, or took back, for a channel to send automatically |
