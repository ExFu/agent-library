# scopes/teams/

## Purpose

Grouping folder for team-related scopes. Anything that is structured around a team Alastair belongs to or works with lives under here.

## Contents

- `sales/` — grouping for the Sales team. Inside: the team-as-scope (`team/`) and a sub-grouping for Sales projects (`projects/`).

(A real substrate might have multiple teams here, each its own subfolder with the same internal shape.)

## Dependencies

- Each subfolder's content depends on `exfu/conventions/scope-folder/` (when it is a scope) and `exfu/conventions/readme/` (always).
- Team members and conventions referenced from team-scope `context/` files.

## Why `teams/` is a grouping folder, not a scope

A team is not a single work area; it is a *container of* work areas (the team's own standing context, plus the team's projects, plus shared resources). Making `teams/` a grouping folder reflects this. The team-itself-as-context lives in `<team>/team/` as its own leaf scope; the team's projects are sibling leaf scopes under `<team>/projects/`.

This is the pattern Alastair landed on in conversation as the natural shape: the team name is the grouping folder, with a `team/` sub-grouping for the team's own context and a `projects/` sub-grouping for project scopes.
