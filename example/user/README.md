# user/

## Purpose

The personal-tier scope. Alastair's standing context, personal todos and notes, scratch space. Anything specific to him that is not tied to a particular work area.

This folder is a scope by shape (carries `scope.md`) and a reserved name (`user/`) by convention. The reserved name lets the resolver always find the personal tier without searching.

## Contents

- `scope.md` — the scope marker and agent-facing reference. Read this first for the structured view.
- `context/` — standing personal context. Holds `me/about.md` and anything else identity-level.
- `databases/` — personal structured records. Empty so far.
- `scratch/` — ephemeral working space. Empty so far.
- `todos/` — personal todos (cross-scope). Uses the `flat-checklist` variant of the todos ontology.

## Dependencies

- `exfu/` — referenced for principles, conventions, and ontology definitions. Local overrides (none currently) would go in `user/principles/`, `user/conventions/`, etc.
- `scopes/` — the work areas. This folder is *about* the user; `scopes/` is where the user's work happens. The two are complementary.

## How agents should treat this folder

Read `scope.md` first. It is the structured reference. This README is the human framing; it should be enough to orient a human visitor in a few seconds.

When a user asks "do you know who I am?" or similar, this is the folder to load first.
