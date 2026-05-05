---
name: wow
description: The user's personal way of working. Claude loads this skill at the start of every session to learn how THIS user's substrate is laid out (the navigation map) and to pick up the thin always-on kernel of instructions and summaries that apply universally. Triggers on "wow", "way of working", on fresh sessions, or when referenced in Global Instructions. Auto-loads the `substrate` skill and any other always-on skills on activation.
---

# Way of Working (personal)

This is the user's personal `wow` skill — generated during setup and maintained as the user's substrate evolves. It is distinct from the generic `substrate` skill: `substrate` carries the shared architecture; `wow` carries the things specific to *this* user.

`wow` does two jobs. Most of what makes Claude useful for this user lives in substrate **files** (`context/`, `scopes/`, `databases/`). `wow` does *not* hold that material. `wow` holds:

1. **The navigation map** — how this user's substrate is currently shaped, especially where it diverges from the standard ExFu starter, so Claude can find files even when the user has reorganised or extended the structure.
2. **A thin always-on kernel** — high-leverage instructions and summaries where the token cost of always-loading is justified by importance, and where forcing a separate file load every session would hurt.

The discipline: keep `wow` lean. Anything substantive belongs in a file, with `wow` knowing where to point.

---

## Bootstrap — what to do at session start

### 1. Load the `substrate` skill

On activation, load the `substrate` skill. It does the heavy lifting — finds the Box knowledge base, reads the ways-of-working guide, orients to the current folder, checks reminders and inbox. Everything needed to be substrate-aware.

### 2. Load any other always-on skills

The user's preferred always-on skills go here. If a skill stops being routinely useful, remove it. If a new skill becomes central, add it.

- `reminders` (time-triggered surfacing)
- `inbox` (frictionless capture)
- `writing-styles` (voice/tone for drafting)
- any `scope-<name>` skills the user wants always-on for current priorities

### 3. Apply the navigation map and the always-on kernel

Read the two sections below. The navigation map tells you how this user's substrate is laid out today. The always-on kernel is the thin set of universally-applicable instructions Claude should always have in mind.

---

## Navigation map

Where things live in this user's substrate, especially where it differs from the ExFu starter. Update this section whenever the user invents new structures, reorganises existing ones, or adds files Claude should know about by default. The map is meant to grow.

### Substrate shape

- The substrate currently follows the standard ExFu starter layout: `context/`, `scopes/`, `databases/`, `scratch/`, plus `_meta/` and `_trash/`.
- *(Note any deviations or additions here as they emerge — e.g. "scopes are organised under `scopes/clients/<client-name>/`", or "user has added a top-level `references/` folder for industry research".)*

### High-traffic files Claude should know exist

Pointers to specific files Claude should be aware of without having to discover them:

- `context/me/tools.md` — the user's tool inventory, what's connected via MCP, what isn't.
- `context/me/writing-style.md` — the user's writing voice profile.
- `scratch/named-workflow.md` — the workflow the user named at install time, kept for continuity across sessions.
- *(Add new pointers here as new high-traffic files emerge.)*

### Active scopes

- *(List scope skills + folder paths as they're created, e.g. "`scope-acme-deal` → `scopes/acme-deal/`". This grows during setup and beyond.)*

---

## Always-on kernel

Thin. High-leverage. Things that justify their token cost by being universally relevant. If a section grows past a handful of lines, that's a sign it should be pulled out into a file with a pointer here instead.

### Communication style

- *(e.g. "Skip preambles. Get to the point. Assume mutual goodwill.")*
- *(e.g. "No tickbox choices — make the suggestion and ask for a response in ordinary conversation.")*
- *(e.g. "No sycophantic openers. No 'that changes everything' framing.")*

### Decision-making defaults

- *(e.g. "When several paths are reasonable, pick one and say why, rather than laying out options.")*
- *(e.g. "If something would cost real time or money, surface the trade-off before acting.")*

### Formatting preferences

- *(e.g. "Prose over bullets for explanations. Bullets OK for lists of things.")*
- *(e.g. "Short code blocks inline. Long ones in artifacts.")*

### Substrate-evolution defaults

How this user wants the substrate maintained as it grows. Conventions about how Claude should propose, explain, and execute structural changes.

- *(e.g. "Before creating a new top-level folder, surface the proposal first — don't just create it.")*
- *(e.g. "When a `scratch/` file becomes a recurring reference, propose promoting it to `context/` or a scope.")*

---

## Iterating this skill

This skill is a living document. Two flavours of update will come up regularly:

- **Structural changes to the substrate** — the user invents a new folder, restructures scopes, adds a custom database, reorganises context. Update the navigation map. This is the primary reason `wow` exists: without it, future Claude instances can't find the user's evolved structure.
- **Recurring corrections** — the user pushes back on the same behaviour more than once, or confirms a non-obvious approach as right. Add it to the always-on kernel. One-off corrections do *not* go in `wow`.

To update: edit this file, then repackage and reinstall the skill (see the `skill-packaging` skill for how).

Keep the list of always-load skills (bootstrap section 2) honest. If a skill stops being routinely useful, remove it. If a new skill becomes central, add it. The point of `wow` is to make every fresh Claude session immediately useful — not to load everything possible.

What does **not** belong in `wow`:

- The user's named workflow logic. That lives in connectors, scheduled tasks, scopes, or its own dedicated skill.
- Detailed information about the user. That goes in `context/me/` files; `wow` points at them.
- One-off preferences or situational requests.
- Anything that's grown past a handful of lines — pull it out into a file and replace it with a pointer.
