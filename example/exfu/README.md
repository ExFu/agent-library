# exfu/

## Purpose

The ExFu-delivered tier of the substrate. Materialised at install from `${CLAUDE_PLUGIN_ROOT}`. The substrate carries its own copy so it stays self-contained: substrates outlive plugin installs, move cleanly between machines, and operate without the plugin if needed.

## Contents

One subfolder per ontology type ExFu ships:

- `principles/` — agent-runtime behavioural principles (Golden Circle, outcome-framed elicitation, etc.). Read by any agent that loads the substrate.
- `conventions/` — named, atomic conventions (the README convention, the scope-folder convention, naming rules, etc.).
- `ontologies/` — definitions of folder types the substrate recognises. Each type has a schema, an `agent.md` template, and (for user-facing types) an elicitation prompt.
- `librarians/` — curation tasks the substrate runs on a schedule.
- `recommendations/` — curated third-party catalogue (connectors, plugins, skills the install agent suggests in context).
- `skills/` — skill-definitions ExFu ships (provider-agnostic; rendered into target platforms at use time).
- `templates/` — templates the install agent fills in (wow, scope, etc.).

## Dependencies

- Sourced from `${CLAUDE_PLUGIN_ROOT}` (the plugin install). Refreshed only by an explicit user-initiated update.
- Read by every other tier (`user/`, `scopes/`) when resolving an ontology type or convention not overridden locally.

## Why this tier exists separately

Three reasons. **Self-containment**: the substrate works without the plugin once installed. **Predictability**: substrate behaviour at install time is captured here and does not silently change when the plugin updates. **Composition**: this is tier 1 of three (ExFu / user / scope); local-tier overrides win, but everything ultimately falls back to here.

## Convention

The user does not edit `exfu/` directly. To extend or override an ontology type, the user adds material at the `user/` tier (e.g. `user/conventions/<name>/agent.md`); to add scope-specific behaviour, at the scope tier. Direct edits to `exfu/` are valid only when the user is deliberately customising their copy of the ExFu defaults and accepts that a future refresh will overwrite.
