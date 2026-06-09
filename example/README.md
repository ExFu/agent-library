# ExFu v0.3.0 substrate — worked example

## Purpose

A demonstrative snapshot of what a v0.3.0 ExFu substrate looks like once a user has it installed and has been working in it. This is not a runtime substrate, not a template, and not consumed by the build. It exists so contributors and design reviewers can see the v0.3.0 shape in concrete form instead of inferring it from `plugin/planning/v0.3.0-direction.md`.

Read this file first, then walk the tree. Every folder has its own `README.md` orienting you to what's inside.

## Contents

Substrate root with the three reserved containers populated and one realistic scope path showing the nesting pattern:

- `CLAUDE.md` — the guard file at root.
- `_meta/` — ExFu plumbing (storage backend record, substrate index).
- `_trash/` — soft-delete area (empty here; just shows the placeholder).
- `exfu/` — ExFu-delivered material, materialised at install. Contains examples of every ontology type that ships in the box: principles, conventions, ontologies, librarians, recommendations, skills, templates.
- `user/` — the personal-tier scope. Carries `scope.md` like any other scope. Shows `context/me/`, `databases/`, `scratch/`, and a user-tier `todos/` folder demonstrating the `agent.md` convention snapshot.
- `scopes/` — the work-area scope container. Holds one realistic nested path: `scopes/teams/sales/team/` (the Sales team-as-scope) and `scopes/teams/sales/projects/acme-q3-renewal/` (a project leaf scope under the Sales grouping).

## How to read this example

Three things to notice as you walk it:

1. **Three tiers, same vocabulary.** The ontology types (todos, librarians, etc.) appear at `exfu/` (ExFu defaults), `user/` (personal), and inside scope folders (scope-specific). Same naming convention; precedence is local-first.

2. **`scope.md` is the marker.** Any folder containing `scope.md` is a scope. Find-all-scopes is a recursive search for `scope.md`. The user-tier `user/scope.md` makes the personal layer a scope by shape.

3. **`agent.md` is the convention snapshot.** When a typed folder (e.g. `todos/`) is created, the relevant `agent.md` template from `exfu/conventions/<type>/agent.md` (or `exfu/ontologies/<type>/agent.md`) is *copied* into the new folder. Compare `exfu/ontologies/todos/agent.md` with `user/todos/agent.md` and `scopes/teams/sales/projects/acme-q3-renewal/todos/agent.md` — the latter two are snapshots of the former at the moment the folder was created.

## What this example deliberately omits

To keep the snapshot legible:

- Most ontology types ship only one or two example atoms here; a real `exfu/principles/` would carry more principles, a real `exfu/recommendations/` would carry many more entries, etc.
- The Sales team-as-scope and the Acme project-as-scope have minimal content (just enough to show shape).
- No `_trash/` contents; no real `_meta/substrate-index.md` regeneration; no live librarian runs.
- The user's `wow` skill (installed in Claude as a packaged skill) is not represented here because it lives in `~/.claude/skills/`, not in the substrate. The substrate-side companion of `wow` is the navigation map embedded in `user/scope.md`.

## Dependencies

- `plugin/planning/v0.3.0-direction.md` — the design this example illustrates.
- `plugin/planning/v0.2.0-substrate-revision.md` — what v0.3.0 supersedes structurally.
- `plugin/src/shared/resources/substrate-guide.md` — the current (v0.2.x) shipped guide, for comparison with the new shape.

## Status

Illustrative. Not built by `build.sh`. Not shipped with any plugin variant. Living document; expected to evolve as v0.3.0 design decisions land.
