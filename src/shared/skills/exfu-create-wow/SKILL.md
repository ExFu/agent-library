---
name: exfu-create-wow
description: Generates the user's personal wow skill -- a short custom skill that loads at every session start, maps out where their substrate is laid out, and carries a thin kernel of always-on instructions. Invoked by install entrypoints at the wow-creation moment in the install flow. Also available directly when the user's substrate has changed significantly and a full regeneration is needed -- not for small edits, which can be made directly to the installed skill. Triggers when an install skill reaches the wow step, or when the user says "my folders have changed since we set this up", "things are different now and you're pointing at old locations", "I want to rebuild my way of working", "my setup has moved around", or any other indication that their substrate has evolved enough to warrant a full regeneration.
---

# ExFu Create Wow

Generates the user's personal `wow` skill from the template. Invoked by install entrypoints at the wow-creation moment in the install flow, and available directly if the user wants a substantial regeneration later.

"Substantial regeneration" means: the user's substrate has changed significantly (new scopes, restructured folders, new always-on tools), or the always-on kernel needs a full rethink. Small updates to `wow` -- adding a new pointer, tweaking a preference -- don't need this skill; the user or install entrypoint can edit `wow` directly.

## Hard constraints

- Do not create a `wow` skill by writing a file to `.claude/`. That is not how skills are installed. Use `skill-packaging` to produce a `.skill` package the user installs via the UI.
- Do not stuff workflow logic into `wow`. Navigation map and thin always-on kernel only. If a section grows past a handful of lines, it belongs in a dedicated file with a pointer in `wow`.
- Do not generate the wow skill without reading the user's existing content first. An out-of-context `wow` is worse than the old one.
- Do not fabricate preferences or context. Use only what you've learned in the current conversation or read from the files listed in the read-set below.

## Read-set -- what to read before generating

Gather these before you start:

1. **`${CLAUDE_PLUGIN_ROOT}/templates/wow-template.md`** -- the canonical template. This is the structure you're filling in.
2. **The user's existing `wow`** -- if there is one, read it. You're merging, not replacing. Preserve anything specific the user has already built in: navigation map entries they've added, always-on kernel items, scope pointers.
3. **`user/context/about-me.md`** -- the user's about-me content. Informs the always-on kernel and gives you the starting shape of the substrate.
4. **Other `user/context/` files** if they exist: role, tools, writing-style. These feed the navigation map (high-traffic file pointers) and the always-on kernel (formatting preferences, communication style).
5. **`user/ontology/ways-of-working.md`** -- the user's personal definitions and working conventions that apply across all scopes.
6. **`exfu/derived/index.json`** -- the global substrate index. This gives you the complete scope tree, folder-type status per scope, and exfu version pins. Use it as the primary source for the navigation map's Active scopes section.
7. **Scope tree** -- scan `scopes/` to confirm what `index.json` reports and catch any scopes created since the last nightly run.

If files are missing -- no existing wow, no `user/context/` yet -- work with what you have. The template has sensible placeholders; leave them as stubs for the user to fill in later.

## What to customise (and what to leave as stubs)

Customise these sections with what you've read:

- **Navigation map -- Substrate shape**: note any structural deviations from the standard v0.3 layout (`exfu/`, `user/`, `scopes/`). If the user has grouping folders under `scopes/` (e.g. `scopes/clients/`), note that. If they've added non-standard folder-types to a scope, note that.
- **Navigation map -- Active scopes**: list scope names, paths, and parent relationships from `exfu/derived/index.json`. Include folder-type status for each (which types are populated, which are pointer-only, which are empty).
- **Navigation map -- High-traffic files**: add pointers to files that actually exist. The baseline set: `user/context/about-me.md`, `user/ontology/ways-of-working.md`, `exfu/derived/index.json`. Add any other `user/context/` files that exist. Don't add stubs for files that haven't been created yet.
- **Always-on kernel -- Communication style**: if the user expressed communication preferences during the install (short sentences, no preambles, direct responses), capture them. If not, leave the stubs.
- **Bootstrap -- Load any other always-on skills**: add skills the user confirmed they want always-on during the install. Remove ones not relevant to their setup.

Leave as stubs everything you don't have real content for. An honest stub beats a fabricated entry.

## Storage layer note

The template has a placeholder for storage-layer notes. Fill this in:

- Solo plugin installs: note that Box is the storage layer and that the knowledge base folder should be kept fully downloaded locally in Box Drive (not space-saver mode).
- Team and team-admin installs: note that git is the storage layer, include the team repo remote URL if you have it.

## Generation process

1. Read everything in the read-set.
2. Draft the customised `wow` by filling in the template with what you've gathered.
3. In the navigation map, include the pointer to `exfu/derived/index.json`. This file is regenerated nightly by the nightly-index librarian and gives Claude a current whole-substrate overview. The pointer should read something like: "`exfu/derived/index.json` -- auto-generated nightly scope map; read at session start for a current overview of what's where."
4. Before packaging: review the draft. Check that nothing in the always-on kernel is large enough to be a standalone file. Check that the navigation map is accurate for the current substrate state. Check that no workflow logic has crept in.
5. Use `skill-packaging` to package the draft as a `.skill` file.
6. Present the package to the user with a one-line summary of what was customised: e.g. "Your wow includes your about-me context, three active scopes (acme, side-project, hiring), and your communication preferences." Then present the install link.
7. After the user installs it, confirm they've added it to Global Instructions so it loads every session.

## Index setup (part of every wow generation)

The nightly-librarians scheduled task runs overnight and regenerates `exfu/derived/index.json` -- the scope-level map that the substrate skill reads at session start. This is a baseline part of every install, not an opt-in.

After packaging the wow skill, do two things:

**First run.** Generate the initial index immediately so the file exists from the start, before the nightly-librarians task has had a chance to run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <substrate-root>
```

Run this with the actual substrate root path. It takes a few seconds and writes `exfu/derived/index.json`. Tell the user briefly: "I'm running a quick scan to generate your first substrate index -- this gives Claude an immediate orientation map."

**Create the scheduled task and hand it to the user to install.** This works the same way as installing the wow skill itself: you create it, the user installs it.

1. Read the task prompt from `${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/TASK.md`.
2. Fill in the user's substrate root path where the prompt expects it. Recommend a nightly cadence (e.g. 03:00 local).
3. Present the customised task to the user the same way you'd hand them any scheduled task to install: "Here's the nightly-librarians task -- install this in Cowork's scheduled tasks; it'll keep your index and librarian registry current overnight."
4. Confirm the user has installed the task before considering the wow step complete.

This step is part of every wow generation -- not optional, not a buffet item. A substrate without a running nightly-librarians task is missing part of its baseline.

## After install

Tell the user two things:

1. `wow` is a living document. When they add new scopes, restructure folders, or confirm a preference they want to stick, they should update `wow`. The simplest update is editing the installed skill file directly; a full regeneration (this skill) is for when a lot has changed.
2. They don't need to remember how to update it. Next time Claude is in a session where the substrate has clearly evolved, it can propose a `wow` update.
