# exfu/conventions/

## Purpose

Named, atomic conventions for substrate shape and behaviour. Each convention is its own subfolder containing an `agent.md` template that gets copied into folders where the convention applies.

## Contents

- `readme/` — every folder has a `README.md` with Purpose/Contents/Dependencies (human-facing).
- `scope-folder/` — every scope folder carries `scope.md` (the marker) and follows the scope shape.

(A real install would carry more: naming conventions, the CLAUDE.md guard convention, the changelog rule, the two-layer PII model, etc. This example shows two illustrative atoms.)

## Dependencies

- Used by install agents at folder-creation time (the convention's `agent.md` is copied as a snapshot into the new folder).
- Used by librarians at scheduled-run time (the snapshot tells them what to check for).
- Referenced from `exfu/ontologies/` schemas (an ontology type's schema declares which conventions its folders must follow).

## Why conventions are atoms, not narrative

Two reasons. **Addressability**: a skill or librarian can say "apply the readme convention" by name, instead of restating the rule. **Snapshot-by-copy**: when a folder is created, the relevant convention atom is copied into it as `agent.md`, so the folder carries its own snapshot of the convention that governed its creation. Upstream changes do not silently rewrite past folders.

## Extension

Users may define their own conventions at `user/conventions/<name>/agent.md`. Scopes may define scope-local conventions at `<scope>/conventions/<name>/agent.md`. Three-tier composition: more local wins.
