# scopes/teams/sales/projects/acme-q3-renewal/todos/

## Purpose

Active follow-ups and tasks for the Acme Q3 renewal. Anything that needs to happen to move this renewal toward close by 30 September 2026.

## Contents

- `agent.md` — the convention snapshot copied from `exfu/ontologies/todos/agent.md` at scope creation (2026-04-15).
- `todos.md` — the checklist itself. Uses the `flat-checklist` variant.

## Dependencies

- `exfu/ontologies/todos/` — original convention source (snapshot here).
- The user's `al-todos` skill — handles operations against this file.
- The daily briefing librarian reads `todos.md` to surface what is due.

## Why a scope-specific todos folder

This renewal has its own pace and its own commitments. Mixing them with Alastair's personal todos (`user/todos/`) or with other Sales projects' todos would lose the context that makes each item actionable. The agent groups todos by scope when surfacing them, so the user sees clear bundles ("Acme: 3 due today; Northwind: 1 overdue; personal: 2 soft due") rather than one undifferentiated list.
