# exfu/librarians/

## Purpose

Curation tasks that look after the substrate. A single daily scheduled task fans out across every discoverable `librarians/` folder (ExFu-tier, user-tier, and inside scopes) and runs each librarian's instructions. The substrate stays tidy without the user having to do it by hand.

## Contents

- `substrate-index/` — regenerates `_meta/substrate-index.md` from the current folder tree.

(A real install would carry more: cleanup of `_trash/`, scope-shape conformance checking, stale-folder flagging, structure-suggestion proposals, team-sync conflict detection. This example shows one illustrative librarian.)

## Shape of a librarian

Each librarian is a subfolder containing:

- `README.md` — human-facing description (Purpose/Contents/Dependencies).
- `agent.md` — convention snapshot for what a librarian is and how the daily orchestrator should run it.
- Plus whatever the librarian actually does: a Python script, a markdown prompt, a YAML config, or some combination. The shape inside the librarian folder is the librarian's own concern.

## Dependencies

- The daily scheduled task (one task per substrate, registered at install) walks `exfu/librarians/`, `user/librarians/`, and every scope's `librarians/` folder. For each one found, it follows the instructions there.
- Read by the install agent at install time (the substrate-index librarian is registered immediately so the index exists from day one).

## Why librarians are pluggable

Three reasons. **Extensibility**: users (and wrapping plugins) can add their own librarians by dropping a folder here. No code change. **Locality**: a scope can have its own scope-specific librarian (e.g. "summarise this scope's recent notes weekly") without affecting the wider substrate. **Discoverability**: any folder named `librarians/` is one, anywhere in the tree.

## Why "librarians" as the name

A librarian's job is custodianship: cataloguing, surfacing what is relevant, retiring what is stale, suggesting reorganisations. The metaphor fits the role better than "scheduled tasks" (mechanism-framed) or "background jobs" (technical and opaque to users).

Per the outcome-framed elicitation principle, the install agent does not typically ask the user "do you want a librarian?". Librarians are infrastructure; they are materialised silently and just run. The user benefits without having to think about them.
