# user/todos/

## Purpose

Alastair's personal todos. Cross-scope: things that do not belong to a specific work area. Scope-specific todos (e.g. for the Acme renewal) live in the scope's own `todos/` folder.

## Contents

- `agent.md` — the convention snapshot copied from `exfu/ontologies/todos/agent.md` at folder creation (2026-05-21).
- `todos.md` — the checklist itself. Uses the `flat-checklist` variant.

## Dependencies

- `exfu/ontologies/todos/` — original convention source (snapshot here).
- The user's `al-todos` skill — handles operations against this file.
- The daily briefing librarian (not shown in this example) reads `todos.md` to surface what is due.

## Why a personal todos folder, separate from scope-specific ones

Some things do not belong to a scope. "Renew my driving license", "book a haircut", "follow up with Sam (not work-related)". Putting them in any work scope is wrong; putting them in a third-party task manager means the agent has to reach across systems. The personal todos folder is the obvious home.

The agent surfaces personal and scope todos separately. When Alastair asks "what's on my plate?", he gets both, grouped clearly.
