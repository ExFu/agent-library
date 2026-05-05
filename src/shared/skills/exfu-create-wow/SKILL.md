---
name: exfu-create-wow
description: Use when the install flow reaches the wow-creation step, or when the user explicitly asks to regenerate, rebuild, or substantially update their personal way-of-working skill. Also triggers on "rebuild my wow", "regenerate my way of working", "create my wow skill", or equivalent phrasings.
---

# ExFu Create Wow

Generates the user's personal `wow` skill from the template. Invoked by install entrypoints at the wow-creation moment in the install flow, and available directly if the user wants a substantial regeneration later.

"Substantial regeneration" means: the user's substrate has changed significantly (new scopes, restructured folders, new always-on tools), or the always-on kernel needs a full rethink. Small updates to `wow` — adding a new pointer, tweaking a preference — don't need this skill; the user or install entrypoint can edit `wow` directly.

## Hard constraints

- Do not create a `wow` skill by writing a file to `.claude/`. That is not how skills are installed. Use `skill-packaging` to produce a `.skill` package the user installs via the UI.
- Do not stuff workflow logic into `wow`. Navigation map and thin always-on kernel only. If a section grows past a handful of lines, it belongs in a dedicated file with a pointer in `wow`.
- Do not generate the wow skill without reading the user's existing content first. An out-of-context `wow` is worse than the old one.
- Do not fabricate preferences or context. Use only what you've learned in the current conversation or read from the files listed in the read-set below.

## Read-set — what to read before generating

Gather these before you start:

1. **`${CLAUDE_PLUGIN_ROOT}/templates/wow-template.md`** — the canonical template. This is the structure you're filling in.
2. **The user's existing `wow`** — if there is one, read it. You're merging, not replacing. Preserve anything specific the user has already built in: navigation map entries they've added, always-on kernel items, scope pointers.
3. **`context/me/about.md`** — the user's about-me content. Informs the always-on kernel and gives you the starting shape of the substrate.
4. **Other `context/me/` files** if they exist: `role.md`, `tools.md`, `writing-style.md`. These feed the navigation map (high-traffic file pointers) and the always-on kernel (formatting preferences, communication style).
5. **Substrate folder structure** — scan the top level and `scopes/` to understand what scopes exist. Each active scope is a navigation map entry.

If files are missing — no existing wow, no `context/me/` yet — work with what you have. The template has sensible placeholders; leave them as stubs for the user to fill in later.

## What to customise (and what to leave as stubs)

Customise these sections with what you've read:

- **Navigation map — Substrate shape**: note any structural deviations from the standard ExFu starter layout. If the user has scopes under `scopes/clients/`, note that. If they've added a top-level `references/` folder, note that.
- **Navigation map — Active scopes**: list scope skills and their folder paths for any scopes you can see in the substrate.
- **Navigation map — High-traffic files**: add pointers to files that actually exist. Don't add stubs for files that haven't been created yet.
- **Always-on kernel — Communication style**: if the user expressed communication preferences during the install (short sentences, no preambles, direct responses), capture them. If not, leave the stubs.
- **Bootstrap — Load any other always-on skills**: add skills the user confirmed they want always-on during the install. Remove ones not relevant to their setup.

Leave as stubs everything you don't have real content for. An honest stub beats a fabricated entry.

## Storage layer note

The template has a placeholder for storage-layer notes. Fill this in:

- Solo plugin installs: note that Box is the storage layer and that the knowledge base folder should be kept fully downloaded locally in Box Drive (not space-saver mode).
- Team and team-admin installs: note that git is the storage layer, include the team repo remote URL if you have it.

## Generation process

1. Read everything in the read-set.
2. Draft the customised `wow` by filling in the template with what you've gathered.
3. Before packaging: review the draft. Check that nothing in the always-on kernel is large enough to be a standalone file. Check that the navigation map is accurate for the current substrate state. Check that no workflow logic has crept in.
4. Use `skill-packaging` to package the draft as a `.skill` file.
5. Present the package to the user with a one-line summary of what was customised: e.g. "Your wow includes your about-me context, three active scopes (acme-deal, product-strategy, hiring), and your communication preferences." Then present the install link.
6. After the user installs it, confirm they've added it to Global Instructions so it loads every session.

## After install

Tell the user two things:

1. `wow` is a living document. When they add new scopes, restructure folders, or confirm a preference they want to stick, they should update `wow`. The simplest update is editing the installed skill file directly; a full regeneration (this skill) is for when a lot has changed.
2. They don't need to remember how to update it. Next time Claude is in a session where the substrate has clearly evolved, it can propose a `wow` update.
