# Permanent record

> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/20260901-1907/ontology.md#durable

The things your librarians must never lose: the small set of facts about this library itself that nothing can work out again from scratch.

Everything in `exfu/` is replaced wholesale when the plugin updates, and `exfu/derived/` is a cache that is safe to delete and rebuild. This folder is neither. **A refresh replaces `exfu/`; it never touches `durable/`, `user/`, or `scopes/`.**

Three tests, all of which must hold before anything is written here:

1. **Unregenerable.** No librarian or script can produce it from material that still exists. Delete it, run every librarian twice: if it comes back, it belonged in `exfu/derived/`. Being expensive to recompute is not the same as being unregenerable.
2. **About the library, not about the world.** It is a fact about this library's installation, migrations, decisions, or operation. Records about a person, company, deal, or a day in the user's life are domain data and belong in a scope's `databases/`.
3. **Append-only, human-readable text.** Markdown or JSONL, every entry dated with a stable id, never rewritten. A wrong entry is corrected by a later entry saying so.

No databases, SQLite, embeddings, or binary blobs. This library syncs through Dropbox or git, where database sidecar files sync out of order and two machines produce a conflicted copy with no merge. If a fast lookup is needed, build it per-machine outside the synced folder and rebuild it from the text.

If a conflicted copy does appear: entries carry ids, so union them, dedupe by id, order by date, and append a note recording the merge rather than deleting the evidence.

| Path | What it holds |
|---|---|
| `ledger/` | The logbook: what has been done to this library, and when |

This is the material worth backing up. Nothing else in the library is irreplaceable.
