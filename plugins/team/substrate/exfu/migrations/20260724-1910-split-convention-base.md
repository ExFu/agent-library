---
name: split-convention-base
id: 20260724-1910-split-convention-base
kind: migration
cadence: on-update
description: Lift readme, principles, librarians and skills out of the version directory to unversioned exfu/
plugin: "0.9.0 -> 0.10.0"
conventions: "20260723-1446 -> 20260903-1743"
applies_when: exfu/ has no unversioned librarians/ (or no readme.md, principles.md, skills/) at its top level
requires_user_decision: false
reversible: true
reads:
  - "exfu/"
writes:
  - "exfu/readme.md"
  - "exfu/principles.md"
  - "exfu/librarians/"
  - "exfu/skills/"
  - "exfu/derived/agent-registry.json"
---

# Migration: split the convention base

Follows: exfu/20260903-1743/ontology.md#migrations

## What changes and why

Before this change, a convention version directory held five things: the ontology, the readme, the principles, the shipped librarian definitions, and the skill templates. All five were frozen, because freezing was applied to the whole directory.

Only the ontology was ever the contract. Nothing anchors a `Follows:` line into the other four, so they were locked purely by sitting in the same folder -- which meant a documentation fix needed a whole conventions release, and every mint silently invalidated the `source` paths in `exfu/derived/agent-registry.json`.

After this migration the version directory holds `ontology.md` alone, and the other four live unversioned at `exfu/`, refreshed by ordinary plugin updates. Registry paths stop moving.

## Preconditions

Applies when `exfu/` is **missing** the unversioned copies: no `librarians/`, `readme.md`, `principles.md`, or `skills/` at its top level.

Note the test is the *absence of the target*, not the presence of the old shape. This matters because step 3 deliberately leaves old version directories intact, so "a version directory still contains librarians/" stays true forever and would re-trigger on every check. Testing for what should exist afterwards makes the precondition accurate in both directions: true before, false after.

Does **not** apply to a library installed at `20260903-1743` or later -- those were created in the target shape. Record `not-applicable` and move on.

## Instructions

### 1. Report before touching anything

List what you found: which version directories exist, which of them carry the four items, and what `exfu/latest.txt` names. Say in one plain line what will change:

> "Your library keeps its shipped librarian definitions and reference docs inside a versioned folder. I'm going to move them up one level so they update normally instead of being frozen. Your conventions themselves don't change."

### 2. Deploy the current base from the plugin

Copy from `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/`:

- The version directory (holding `ontology.md`) into `exfu/<that version>/`, if not already present.
- `readme.md`, `principles.md`, `librarians/`, `skills/` into `exfu/` directly.

These are plugin-owned; a straight copy is correct. Do not merge, and do not preserve local edits -- if the user has edited a shipped librarian definition, that is a local librarian and belongs in a scope's `librarians/` folder, not in the plugin's. Flag it if you find one rather than silently overwriting; ask where they want it.

### 3. Leave the old version directories exactly as they are

Do not delete them and do not strip the four items out of them. Scopes pinned to an older version still read their conventions from there, and under the side-by-side model both shapes coexist without conflict.

This migration **adds** the unversioned copies. It does not remove the old ones.

### 4. Re-point the registry

Open `exfu/derived/agent-registry.json`. Any entry whose `source` starts `exfu/<version>/librarians/` becomes `exfu/librarians/` with the same filename. Leave every other field untouched, and leave entries whose source is a scope path alone entirely.

This is the change that stops registry paths breaking on future mints.

### 5. Update `latest.txt` if the plugin ships a newer version

If the plugin's version directory is newer than what `exfu/latest.txt` names, update it. Deciding "newer": identifiers are shortened UTC timestamps, so lexicographic order is chronological order, except that any timestamp identifier beats any legacy `v0.x` one.

Scope pins are **not** changed by this migration. A scope keeps following the version it pinned until its owner migrates it deliberately.

## Success condition

- `exfu/readme.md`, `exfu/principles.md`, `exfu/librarians/` and `exfu/skills/` all exist at the top level of `exfu/`.
- Every registry entry that pointed into a versioned `librarians/` now points at `exfu/librarians/`, and the file it names exists.
- Old version directories are untouched.
- The library's scopes still resolve their conventions: spot-check one `Follows:` line and confirm the file and anchor it names are readable.

## If something goes wrong

Nothing here deletes user content, so the failure mode is a partial copy rather than data loss. Record `failed` with what completed, and leave the library as found. Re-running the migration is safe: every step is idempotent.
