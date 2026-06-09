---
scope: user
type: personal-tier
created: 2026-05-21
storage-backend: local
---

# Scope: user (personal tier)

## What this scope is for

The personal layer of this substrate. Everything specific to Alastair that is not tied to a particular work area lives here: standing context about him, his preferences, his personal todos and notes, his scratch space.

This scope is identified by the reserved name `user/` so the resolver always knows where the personal tier lives. The agent treats it like any other scope (it carries `scope.md`, follows the scope shape), but its top-level position alongside `scopes/` is structural, not user-chosen.

## Key entities and relationships

- **Alastair** (the user) — see `context/me/about.md` for standing facts.
- **WhaleyBear Ltd** — his company.
- **ExFu** — the venture this substrate supports work on. Has its own scope at `scopes/.../exfu/` in a real substrate (not shown in this example).
- **Sales team / Acme Q3 renewal** — see `scopes/teams/sales/` for the working scope.

## Conventions adopted at this scope

- `context/me/` — populated with about-me.
- `todos/` — personal todos (cross-scope). Variant: `flat-checklist`.
- `databases/` — empty so far; reserved for personal structured records (contacts, etc.) if Alastair adopts them.
- `scratch/` — empty so far.

## Always-on kernel pointers

These are surfaced from `user/wow` (the user's wow skill, which lives in the Claude install, not in the substrate). Repeated here for substrate-side reference:

- Communication: short sentences, no preambles, no em-dashes, plain language.
- Decision-making: when several paths are reasonable, pick one and say why.
- Substrate evolution: surface structural changes before making them.

## Dependencies

- All scopes under `scopes/` (the user is the owner of every scope in this substrate; this scope is the "what's specifically about me" rather than the work).
- `exfu/principles/` — read on activation.
- `exfu/conventions/scope-folder/agent.md` — the convention this scope was created from.

## Related skills

- `al-wow` — the user's wow skill (lives in `~/.claude/skills/`).
- `al-todos` — user's todos handling skill (lives in `~/.claude/skills/`; reads from `user/todos/`).
- `al-writing-styles` — voice profile skill (lives in `~/.claude/skills/`; reads from `user/context/me/writing-style.md` once created).
