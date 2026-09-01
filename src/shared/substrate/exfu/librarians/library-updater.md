---
name: library-updater
cadence: on-update
kind: librarian
description: Applies pending library migrations after a plugin update, and records every outcome in the ledger
reads:
  - "exfu/migrations/"
  - "durable/ledger/migrations.md"
writes:
  - "durable/ledger/migrations.md"
requires_user_decision: true
---

# Library updater librarian

Releases change the shape of a library. Something has to carry installed libraries across, and that work has to be recorded -- otherwise no agent can answer "what state is this library actually in?" without inspecting the filesystem and guessing.

This librarian is that something. It is **not scheduled**, and that is deliberate: a plugin update does not touch the library, it changes what is installed alongside it. There is no update hook, so nothing can run at update time. The boot skill notices the gap at the start of the next session and hands here.

Follows: exfu/20260901-1907/ontology.md#migrations

## Instructions

### 1. Establish what is pending

1. List `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/migrations/`. Each filename stem is a migration id (`YYYYMMDD-HHMM-slug`), so sorting the names sorts them into application order.
2. Read `durable/ledger/migrations.md`. Every id recorded there -- with any outcome, including `not-applicable` -- has been dealt with.
3. Pending = shipped minus recorded, in id order.

**If `durable/` does not exist,** this is a library from before the permanent record convention. Do not treat that as "everything is pending". Create the container and the logbook inside it -- `durable/readme.md`, then `durable/ledger/` with `migrations.md` and `install.md`, all from the shipped templates -- then continue to step 2, which decides what genuinely applies by looking at the library rather than at the absent record. The same applies if `durable/` is there but `durable/ledger/` is not: create what is missing, record nothing retrospectively.

**If the ledger records ids this plugin does not ship,** the library is ahead of this surface. Another surface (Claude Code and Cowork have separate plugin installs, and either may auto-update) has already moved it forward. **Stop.** Tell the user this surface's plugin is older than their library and needs updating first. Do not attempt structural work against a shape this plugin does not understand.

### 2. Test each pending migration against the library itself

For each pending migration in order, read its `applies_when:` and evaluate it **against actual library structure** -- never against the ledger alone. The ledger says what is believed; the filesystem says what is true.

- Precondition met: it applies. Continue to step 3.
- Precondition not met: record `not-applicable` with a one-line reason and move on. This is the normal case for a library that was created after the change, or that a user already migrated by hand.
- **Precondition and ledger disagree** (the ledger says applied but the structure is old, or the reverse): stop and report the facts. Do not resolve it by interpretation -- a confident narrative that explains the divergence away is exactly the failure mode to distrust. Only the user knows their true setup. Resume on their say-so.

### 3. Apply, one at a time, in order

Migrations are ordered because later ones assume earlier ones landed. Never batch them and never reorder.

A migration deploys plugin-owned content, and the boundary is stated positively: **a refresh replaces `exfu/`; it never touches `durable/`, `user/`, or `scopes/`.** The only write outside `exfu/` any migration makes is appending to the logbook. If a migration body asks for more than that, stop and report it rather than running it.

For each:

1. Say in one plain line what is about to change and why. Library language, not substrate jargon.
2. If the migration is marked `requires_user_decision: true`, or any step of it is destructive, get an explicit yes first. Report what will happen before it happens, not after.
3. Run the body. Where it names a script, the script is the tool for the mechanical part -- run it, then check the result yourself. The script never replaces the judgment.
4. Verify the migration's own stated success condition.
5. Record the outcome in `durable/ledger/migrations.md` **before starting the next one**. A half-applied run that stops must leave an accurate record of exactly how far it got.

If a migration fails, stop the whole run. Record `failed` with what happened. Do not continue to later migrations against a library in a half-known state.

### 4. Record decisions, not just outcomes

When a migration asks the user something, write the answer into the ledger entry. A later agent that can see the decision does not re-ask a settled question, and does not silently choose differently.

## Ledger entry format

Append to `durable/ledger/migrations.md`:

```markdown
## <migration-id>
- considered: <ISO date>
- by: <actor> (<surface>), plugin <version>
- outcome: applied | not-applicable | failed | skipped
- notes: <what happened, and any decision the user made>
```

## What it touches

- Reads: the shipped migrations, `durable/ledger/migrations.md`, and whatever each migration's `applies_when` inspects
- Writes: `durable/ledger/migrations.md` always; each migration writes whatever its own frontmatter declares

## Why it matters

Without it, every release that changes shape either strands existing libraries or needs a bespoke one-off skill that knows nothing about any other. With it, a library can always answer what has been done to it, and by which version.
