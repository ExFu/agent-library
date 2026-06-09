# exfu/principles/

## Purpose

Agent-runtime behavioural principles. The reasoning patterns ExFu has found useful for agents working in this substrate. Read by any agent that loads the substrate, alongside the user's `wow`.

## Contents

One atom per principle, each a short markdown file:

- `golden-circle.md` — Why before How before What.
- `outcome-framed-elicitation.md` — ask about outcomes, not mechanisms.
- `concrete-first.md` — build before explain.

(A real install would carry more. This is illustrative.)

## Dependencies

- Loaded at session start (or whenever the agent is orienting itself). The user's `wow` typically includes "read the principles before responding to substantive requests".
- Complementary to `cross-cut-brand-voice.md` in the plugin (which is about *how to write*) and to the always-on kernel in the user's `wow` (which is about *this user's preferences*). Principles are about *how to reason*.

## Why these are atoms, not one big document

Each principle stands alone. An agent can load only the relevant ones, reference them by name, or hand them to a user as a teaching artifact. As ExFu discovers more useful patterns, they get added as new atoms; existing ones change rarely. A monolithic principles document would grow stale and would be loaded all-or-nothing.

## Extension

Users may add their own principles at `user/principles/`. Scopes may add scope-specific principles at `<scope>/principles/`. Three-tier composition applies: more local wins. A scope can override an ExFu principle if its work area benefits from a different reasoning pattern.
