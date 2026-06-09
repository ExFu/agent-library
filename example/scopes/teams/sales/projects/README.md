# scopes/teams/sales/projects/

## Purpose

Sub-grouping folder for active Sales projects. Each project is a leaf scope (carries `scope.md`).

## Contents

- `acme-q3-renewal/` — Acme Corp's Q3 contract renewal. Active.

(A real Sales team would have several projects here at any one time: new business pitches, renewals, expansions, onboardings. Each gets its own scope folder.)

## Dependencies

- Each project scope references `scopes/teams/sales/team/` for team-level context (members, conventions).
- Each project scope may reference org-level context if the team is part of a larger organisation.

## Why this is a sub-grouping, not a scope

`projects/` is a container for many scopes. It has no standing context of its own; the team-level context is one level up at `sales/team/`. A grouping folder is the right shape.

## Naming convention for project scopes

- Lowercase, hyphen-separated.
- Date or sequence prefix optional; usually the project name alone is enough.
- Examples: `acme-q3-renewal`, `beta-industries-pitch`, `northwind-expansion`, `contoso-onboarding`.
