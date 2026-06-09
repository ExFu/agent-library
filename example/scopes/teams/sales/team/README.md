# scopes/teams/sales/team/

## Purpose

The Sales team's own standing context. Who is on the team, how the team works, what conventions apply across the team's projects.

## Contents

- `scope.md` — the scope marker and agent-facing reference. Read this first for the structured view.
- `context/` — team-level context: members, working conventions, shared reference material.

## Dependencies

- Sibling scopes under `scopes/teams/sales/projects/` reference this for team-level context (members, conventions).
- `user/scope.md` lists Sales as a team Alastair works with.

## Why this is `team/` inside `sales/`

The Sales team itself has standing context worth a scope's worth of shape. The team's projects also each want to be scopes. Putting both under a single `sales/` scope would nest scopes inside scopes (not allowed in v0.3.0). The shape `sales/team/` + `sales/projects/<project>/` makes both proper leaf scopes under the `sales/` grouping folder.
