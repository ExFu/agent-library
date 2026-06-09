# scopes/teams/sales/

## Purpose

Grouping folder for everything related to the Sales team. The team's own standing context lives in `team/` (a leaf scope); active sales projects live as leaf scopes under `projects/`.

## Contents

- `team/` — the Sales team-as-scope. Carries `scope.md`. Holds team members, working conventions, shared reference material.
- `projects/` — sub-grouping for active Sales projects. Each project is a leaf scope.

## Dependencies

- `team/context/team-members.md` — referenced by projects when they mention a team member's involvement.
- `projects/<project>/scope.md` files cross-link to the team scope via dependency notes.

## Why this two-folder split

Two reasons. **Avoiding scope-in-scope**: the team has its own standing context (worth a scope's worth of shape) AND its projects (each their own scope). Putting both under a single Sales scope would require nesting scopes, which the v0.3.0 convention forbids. Splitting into `team/` and `projects/` keeps both as proper leaves.

**Clarity at a glance**: a contributor landing in `scopes/teams/sales/` immediately sees "this is the team's own stuff" and "this is the team's work". Two folders, two clear purposes.
