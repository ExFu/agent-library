---
convention: scope-folder
applies-to: any-folder-marked-as-scope
copy-on-create: true
---

# Convention: Scope folder shape

## Why

Scopes are the substrate's unit of bounded work. The agent needs to recognise them anywhere in the tree, and the user (or future agents) need to know what a scope folder contains without having to learn each one individually. A shared shape makes scopes interchangeable for agents and predictable for humans.

## How

A scope folder is identified by the presence of a `scope.md` file at its root. That marker doubles as the scope's agent-facing reference (entities, current work, conventions, dependencies on ontology atoms).

Required contents:

- `scope.md` — the marker and the agent-facing reference. See `exfu/templates/scope-template.md` (not shown in this example) for the template.
- `README.md` — human-facing description (Purpose/Contents/Dependencies).
- `context/` — standing context for this scope. Required (HARD convention). Other ontology-typed folders (todos, sops, contacts, databases) are adopted as needed.

Optional contents (adopted as the work demands):

- `todos/`, `sops/`, `contacts/`, `databases/`, `librarians/`, `ontologies/`, `conventions/`, `skills/`, etc.
- Any other ontology-typed folder, materialised as a snapshot.
- Free-form working files (in scope root or in subfolders) the user creates as the work happens.

Discovery: to find all scopes in the substrate, recursively search for `scope.md` files. The user-tier scope at `user/scope.md` is included by this same rule.

## What

When the agent creates a scope folder:

1. Create the folder.
2. Write `scope.md` using the scope template (filled in with what the conversation has captured).
3. Write `README.md` with Purpose/Contents/Dependencies.
4. Create `context/` and write its `README.md`.
5. For any ontology type the user has opted into via elicitation, create that typed folder and copy the relevant `agent.md` snapshot in.

When the agent encounters an existing scope folder: read `scope.md` first (it carries the structured reference), then `README.md` (human framing), then walk `context/` and any other typed folders as needed.

## Constraint: no scope inside a scope

A scope folder cannot contain another scope folder. Grouping folders can nest; scopes are leaves. If a scope needs to "contain" related scopes, it should be reshaped into a grouping folder with sub-scopes alongside it.

A librarian (the `scope-shape` checker, not shipped in this example) periodically flags any scope folder that has accidentally become a parent to another scope, with a suggested restructure.
