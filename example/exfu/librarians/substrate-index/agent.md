---
convention: librarian
applies-to: any-folder-under-a-librarians-folder
copy-on-create: true
---

# Convention: librarian

## Why

Background curation work on the substrate should be pluggable, discoverable by convention, and runnable by a single daily orchestrator task. Otherwise every new background job becomes its own scheduled task (a maintenance burden on the user) and there is no consistent way for users or wrappers to add their own.

## How

A librarian is a folder that lives under any `librarians/` folder in the substrate. The folder name is the librarian's name. The folder contains everything the daily orchestrator needs to run it.

Required:

- `README.md` — human-facing description of what this librarian does, when, and why.
- `agent.md` — this convention snapshot.

Recommended:

- `instructions.md` — a markdown prompt the orchestrator follows. The orchestrator is an agent; the prompt tells it what to do.

Optional (depending on what the librarian does):

- Scripts (Python, shell, etc.) the orchestrator invokes.
- Config files (YAML, JSON) the script or instructions read.
- A `state/` subfolder for librarian-internal state (last-run timestamp, cached diffs, etc.).

The orchestrator's contract: walk `exfu/librarians/`, `user/librarians/`, and every `<scope>/librarians/` folder. For each librarian found, read its `instructions.md` (or, if absent, fall back to a default behaviour from the librarian's `README.md`) and execute. Surface the librarian's output in the daily report.

## What the daily orchestrator does

Once per day (the cadence is set at install, typically overnight):

1. Discover all librarian folders across the three tiers.
2. For each, run its instructions. Independently — one librarian's failure does not block another.
3. Aggregate output into a daily report.
4. If anything wants user attention (a structure suggestion, a conflict, a stale-folder flag), surface it in the user's morning briefing.

## Snapshot semantics

This file is copied into every librarian folder at creation time. The librarian thereafter follows its own copy. If the orchestrator's contract changes in a future ExFu version, existing librarians keep working under their snapshot until the user opts into a refresh.

## Why "librarians" as the discovery word

Any folder named `librarians/` is a container for librarians. Same type-folder-discoverability rule as every other ontology type in v0.3.0. The orchestrator does not need a registry; the filesystem is the registry.
