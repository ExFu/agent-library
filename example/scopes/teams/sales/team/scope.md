---
scope: sales-team
type: team-as-scope
parent-grouping: scopes/teams/sales/
created: 2026-05-21
---

# Scope: Sales team (the team itself, not a project)

## What this scope is for

The Sales team's own standing context. Who is on the team, how the team works, what conventions and reference material apply across Sales projects. Read by every session that does Sales work, before opening a specific project scope.

This is distinct from any individual sales project (those live as siblings under `scopes/teams/sales/projects/`). This scope is about the team itself.

## Key entities and relationships

- **Team lead**: Alex Morgan (placeholder; see `context/team-members.md`).
- **Team members**: see `context/team-members.md`.
- **Sibling scopes (projects)**: `scopes/teams/sales/projects/acme-q3-renewal/` and others as they emerge.
- **Parent grouping**: `scopes/teams/sales/` (not itself a scope).

## Conventions specific to this scope

- All Sales projects follow a common scope shape: `scope.md`, `README.md`, `context/`, `todos/`. Other ontology folders adopted as needed.
- Team standups happen weekly; notes go in a `weekly-notes/` folder inside this scope as they accumulate (none yet).

## Related skills and references

- No team-specific skills yet. As patterns emerge ("how Sales drafts proposals", "how Sales tracks pipeline"), they become candidate scope-skills lifted to the team scope.

## Dependencies

- All scopes under `scopes/teams/sales/projects/` reference this scope for team-level context.
- `user/scope.md` references this scope as the team Alastair is on (or works with).
