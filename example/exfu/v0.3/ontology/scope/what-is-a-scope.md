# What is a scope

A scope is a bounded working context. It's the single structural concept in the substrate -- everything is a scope. A project is a scope. A team is a scope. A client engagement is a scope. Your personal workspace is a scope.

## What makes something a scope

A directory is a scope if it contains a `scope.md` file. That file is the boundary marker -- it declares the scope's name, purpose, parent, and which ExFu convention version it follows.

## What's inside a scope

Every scope has the same internal shape: a set of standard folder-types (ontology/, context/, docs/, skills/, librarians/, todo/, reminders/, inbox/, databases/, visualisations/). Not every scope uses every folder-type -- most scopes only have the ones they need. But an agent entering any scope at any depth knows where to look.

## Special scopes

Two scopes sit at fixed positions in the substrate root:

- **exfu/** -- the convention base. Owned by the ExFu plugin. Internally structured like a scope but not a scope itself (no scope.md). Contains the definitions and defaults that all other scopes reference.
- **user/** -- your personal workspace. A real scope (has scope.md) for personal context, definitions, and defaults that apply across everything you do.

Everything else lives under **scopes/** at the root.

## What a scope is NOT

- Not an org chart. Scopes don't have to map to teams or departments. A scope is any bounded context you want to work within.
- Not permanent. Scopes can be created, archived, or deleted as work evolves.
- Not isolated. A scope knows about its parent (declared in scope.md) and can reference definitions from ancestor scopes, the user scope, and the exfu convention base.
