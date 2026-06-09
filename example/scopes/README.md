# scopes/

## Purpose

Container for all work-area scopes. Not itself a scope (no `scope.md`). Arbitrary grouping folders may nest underneath; leaves are scope folders identified by `scope.md`.

## Contents

- `teams/` — grouping folder for team-related scopes.

Other top-level groupings can appear here as the user adopts them: `clients/`, `projects/`, `programmes/`, `research/`, etc. The starter ontology (see `exfu/ontologies/`) suggests `teams/`, `clients/`, `projects/`, `organisations/` as sane defaults, but the user is free to create or rename groupings as their work demands.

## Dependencies

- Read by every session-start orientation that needs to find a scope.
- The `substrate-index` librarian (in `exfu/librarians/`) catalogues every scope folder discovered here.

## Discovery rule

To find all scopes anywhere in this tree: recursive search for `scope.md` files. Grouping folders are anything in `scopes/` that does *not* have a `scope.md`. The agent does not need to know in advance which folders are scopes and which are grouping; the marker file tells it.

## Nesting

Grouping folders can nest arbitrarily (e.g. `scopes/teams/<team>/projects/<project>/`). Scopes cannot nest inside scopes; a scope is always a leaf. If a scope appears to want children, it should be reshaped: rename the scope as a grouping folder, move the scope content into a child folder, and create sibling child folders for the new scopes.

A librarian (the `scope-shape` checker, not shown in this example) periodically flags any scope that has accidentally become a parent.
