# library-migrations -- a convention for updating a library over time

**Status:** Adopted (Al, 2026-07-24, in session). Closes the gap left open by
`conventions-lock-boundary.md`: no standalone upgrade path existed for a library
already installed. Companion to that note -- it drew the line between frozen and
evolving; this one governs how a library crosses that line safely.

## Why

Every release that changes shape needs someone to move existing libraries onto
it, and nothing owns that job. The split-base change (0.9.0) landed with no way
for an installed library to adopt it: `exfu-migrate-to-dropbox` covers the case
only incidentally, during a storage move. That is not an oversight in one
release, it is a missing concept -- and it becomes urgent the moment libraries
exist that aren't Al's.

Ad hoc migration skills (`exfu-migrate-to-dropbox`, `exfu-migrate-from-fetch-model`)
each encode one transition and know nothing about each other. Nothing records
what has been applied to a given library, so no agent can answer "what state is
this library actually in?" without inspecting the filesystem and guessing.

## Decisions

### 1. Migrations are boot-detected, not scheduled

**Al's ruling, and it corrects the first sketch.** A plugin update does not
touch the library: it changes what is installed alongside it. There is no update
hook, so nothing *can* run at update time. The first opportunity to notice is the
next session that loads `exfu-library`.

So the trigger is **detection at boot**, and execution is a procedure the user
consents to -- not an unattended cadence run. The scheduled-agent *definition
format* is still the right shape for the file (YAML frontmatter over an
instruction body, `scripts:` for mechanical legwork), but `cadence` becomes
`on-update` and the registry does not schedule it.

Two consequences Al identified:

- **Auto-update makes the plugin move silently.** The library must therefore
  carry its own stamp of what has been applied, and the check must run at boot
  rather than trusting anyone to notice a version bump.
- **Claude Code and Cowork are separate surfaces with separate plugin
  installs.** The same library can be opened from two surfaces on different
  versions. A library migrated by 0.9.0 and then opened by an 0.8.0 surface must
  be detected as *ahead*, and that surface must decline structural work rather
  than operate on a shape it does not understand.

### 2. Durable state gets its own top-level folder: `durable/`, holding `ledger/`

**Al's ruling.** The ledger cannot live in `exfu/`: that directory is
plugin-owned and refreshed wholesale on update, so one careless refresh destroys
the only record of what state the library is in. It cannot live in
`exfu/derived/` either -- that is defined as a disposable cache, and the ledger
is the one thing in the system that categorically cannot be regenerated.

**Refined in the same session, and this corrects the first sketch.** That sketch
put `ledger/` itself at the top level. Al judged the name too specific for a root
position: more stateful things will need to survive outside `exfu/` over time --
he named long-lived databases and SQLite -- and each would otherwise arrive
arguing for a root entry of its own, leaving the root a list of tenants that says
nothing about what they have in common. So the top-level entry is the *category*.
`durable/` sits beside `exfu/`, `user/`, and `scopes/`; the ledger is its first
tenant, at `durable/ledger/`. Not a scope (no scope.md), not a folder-type, and
it exists exactly once, at the root.

**Why `durable` won.** The corpus had already chosen the word. Before anyone
tried to name a folder, "durable" was doing exactly this job in eleven places --
the substrate guide, the ontology, `exfu/readme.md`, the boot skill, and all
three install skills -- every one of them describing the library's durable record
of what has been done to it. Naming the folder after the word the writing already
reached for costs nothing to learn. It also pairs against `derived`: one is
rebuilt, the other is kept, and between them the two words state the whole rule.

`state/` was the obvious alternative, and rejecting it matters. The ontology
already points that word somewhere else -- "Current state belongs in the derived
index, the dashboard, and the content itself", in the authoring rule that forbids
descriptors from carrying state. A root `state/` would make the file every agent
reads cold contradict itself on its own vocabulary. The ledger's own name stands
as chosen, for the same precision as before; still rejected for it are `_state`
(the underscore convention was retired with `_meta/` and `_trash/`), `derived`
(taken, and means the opposite), and `history` (suggests git-like versioning).

User-facing register: `durable/` is the library's "permanent record" and the
ledger is "your library's logbook". Librarians never say "durable" to a user.

**The membership test.** Three conditions, all of which must hold before anything
is written to `durable/`:

- **Unregenerable.** No librarian or script can reproduce it from material that
  still exists. Delete it, run every librarian twice, and see whether it comes
  back. Regeneration *cost* is deliberately not part of the test: expensive to
  recompute belongs in `exfu/derived/`.
- **About the library, not about the world.** It only means anything as a fact
  about this library's installation, migration, decisions, or operation. Records
  about a person, company, deal, or a day in the user's life are domain data and
  belong in a scope's `databases/`.
- **Append-only, human-readable text.** Markdown or JSONL, dated, stable ids,
  never rewritten in place. This condition keeps the other two honest: it
  excludes databases, embeddings, mutable counters, and config by construction
  rather than by judgement -- which is also why the SQLite that prompted the
  generalisation does not itself belong here.

**The carve-out is stated positively, never as an exception list.** Every skill
that refreshes, copies, or migrates a library says it in this form:

> **A refresh replaces `exfu/`. It never touches `durable/`, `user/`, or `scopes/`.**

This is not a style preference. An exception list grows silently wrong -- each
new durable thing is a fresh chance to forget an entry, and a forgotten entry
destroys the one category of file that cannot be recovered. Naming what a refresh
*may* replace has no such failure mode. This is not hypothetical: a live
data-loss bug of exactly this kind -- an exception list that had gone stale --
was found and fixed in `exfu-migrate-to-dropbox`, which now states the rule
positively at its structural-comparison step.

Contents:

- `durable/ledger/migrations.md` -- append-only record of applied migrations
- `durable/ledger/install.md` -- when the library was created, by which plugin version and surface
- `durable/ledger/readme.md` -- what the folder is and the never-overwrite rule
- `durable/readme.md` -- the membership test and the never-delete rule

Materialise on demand applies: `durable/` gains nothing beyond `ledger/` until a
second genuine tenant exists.

**No migration is required for this change.** The root-level `ledger/` shape was
never published -- the commits carrying it are unpushed and the marketplace pins
no version to them -- so no library in the world has one. A library either
predates the concept entirely (no `durable/`, no `ledger/`) or is created in the
current shape. Writing a compatibility path for a shape that never shipped would
be inventing a case to maintain forever.

### 3. Migration identity is a timestamp, ordering is lexicographic

`<YYYYMMDD-HHMM>-<slug>.md`, reusing the property the conventions scheme already
relies on: lexicographic order is chronological order. The filename stem is the
id (path-as-identity, consistent with the planning corpus and with OKF).

Frontmatter carries the version movement so an agent can explain what a
migration is *for* without reading the body:

```yaml
---
name: split-convention-base
id: 20260724-1749-split-convention-base
kind: migration
description: Lift readme/principles/librarians/skills out of the version directory
plugin: "0.8.0 -> 0.9.0"
conventions: "20260723-1446 -> 20260724-1749"   # omit when no conventions change
applies_when: A version directory under exfu/ contains principles.md
requires_user_decision: false
reversible: true
---
```

`conventions:` is present only when the migration accompanies a mint -- that is
the "deep version upgrade" case; its absence marks a general update.

### 4. The three non-obvious rules

- **Fresh installs seed, they do not replay.** A new library is already in the
  target state. If pending were computed as `shipped - applied`, every new
  install would run the entire history against a library that never had the old
  shape. Install stamps every shipped migration as `not-applicable (fresh
  install at <version>)`. This is the failure mode that would bite hardest as
  clients onboard.
- **`applies_when` is evaluated against real state, not the ledger.** Users
  half-migrate, restore backups, hand-edit. The ledger says what we believe; a
  precondition check on actual structure says what is true. When they disagree,
  report the discrepancy and stop -- the same discipline
  `exfu-migrate-to-dropbox` already applies to divergence.
- **Retirement from day one.** Migrations accumulate. A documented floor: the
  plugin ships migrations back to a stated minimum, and anything older is told
  to reinstall. Cheap to decide now, awkward once there are thirty.

### 5. Executing safely

These are agent-executed structural changes, which can fail in ways a script
cannot. Design constraints:

- `scripts:` carries the mechanical parts; the body verifies the result
- destructive steps report first and require confirmation
- `requires_user_decision: true` marks migrations that must not run unattended
- every outcome is written to the ledger *including decisions taken*, so a later
  agent does not re-ask a question the user already answered

## Enactment

1. Mint a new convention version carrying: the `durable/` location and the ledger
   inside it, the migration concept and definition format, and the updater's
   remit. (Al pre-approved the mint.)
2. Ship `exfu/migrations/` and `exfu/librarians/library-updater.md`.
3. Write the first migration: `20260724-1749-split-convention-base`.
4. Boot-time detection in `exfu-library`, including the ahead/behind surface check.
5. Ledger seeding in the three install skills.
6. Example library gains `durable/`; rebuild.
