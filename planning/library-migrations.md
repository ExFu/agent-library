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

### 2. Durable state gets its own top-level folder: `ledger/`

**Al's ruling.** The ledger cannot live in `exfu/`: that directory is
plugin-owned and refreshed wholesale on update, so one careless refresh destroys
the only record of what state the library is in. It cannot live in
`exfu/derived/` either -- that is defined as a disposable cache, and the ledger
is the one thing in the system that categorically cannot be regenerated.

`ledger/` is a new top-level location beside `exfu/`, `user/`, and `scopes/`.
Not a scope (no scope.md). Never written by a plugin refresh. Append-only.

Naming: chosen for precision -- an append-only record of what has been applied.
Rejected `_state` (the underscore convention was retired with `_meta/` and
`_trash/`), `derived` (taken, and means the opposite), `history` (suggests
git-like versioning). In the user-facing register it is "your library's
logbook". *If Al prefers another name, it is a one-command rename plus a mint.*

Contents:

- `ledger/migrations.md` -- append-only record of applied migrations
- `ledger/install.md` -- when the library was created, by which plugin version and surface
- `ledger/readme.md` -- what the folder is and the never-overwrite rule

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

1. Mint a new convention version carrying: the `ledger/` location, the migration
   concept and definition format, and the updater's remit. (Al pre-approved the
   mint.)
2. Ship `exfu/migrations/` and `exfu/librarians/library-updater.md`.
3. Write the first migration: `20260724-1749-split-convention-base`.
4. Boot-time detection in `exfu-library`, including the ahead/behind surface check.
5. Ledger seeding in the three install skills.
6. Example library gains `ledger/`; rebuild.
