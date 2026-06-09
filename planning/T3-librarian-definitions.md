# T3 -- Librarian definitions and registry

Update the convention base librarian format to be machine-parseable, create the registry schema, and update existing librarian definitions with structured frontmatter.

**Parents:** `T2-librarian-framework.md` (domain), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-convention-base (phase 1, complete)
**Status:** not started.

---

## Why

The current librarian definitions (`nightly-index.md`, `version-cleanup.md`, `what-is-a-librarian.md`) are human-readable markdown. A runner can't parse them to know what to execute, in what order, or at what cadence. The librarian framework needs structured metadata alongside the prose.

The registry is the other half: it tracks what's actually installed (vs merely defined), when each last ran, and whether it's healthy. Without it, the runner would have to scan the entire substrate for definitions on every run.

---

## What to build

### 1. Structured definition format

Add YAML frontmatter to librarian definition files:

```yaml
---
name: nightly-index
cadence: nightly
implementation: python-script
script: scheduled-tasks/substrate-index/index.py
reads:
  - "*/scope.md"
  - "*/agent.md"
writes:
  - "exfu/derived/index.json"
depends_on: []
description: Walks the substrate and regenerates the global scope index
---
```

**Fields:**
- `name` -- unique identifier (kebab-case)
- `cadence` -- one of: nightly, weekly, hourly, on-demand
- `implementation` -- one of: python-script, shell, skill, mcp-tool
- `script` / `command` / `skill` / `tool` -- the implementation target (field name matches implementation type)
- `reads` -- glob patterns of what the librarian reads (for documentation and conflict detection)
- `writes` -- paths the librarian writes to
- `depends_on` -- list of librarian names that must run before this one within the same cadence
- `description` -- one-line summary for the registry and dashboard

### 2. Update existing definitions

Update these files in the convention base with YAML frontmatter:

- `exfu/v0.3/ontology/librarian/nightly-index.md` -- add frontmatter for the index librarian
- `exfu/v0.3/ontology/librarian/version-cleanup.md` -- add frontmatter for the cleanup librarian
- `exfu/v0.3/ontology/librarian/what-is-a-librarian.md` -- update to describe the structured format

### 3. Registry schema

Create `exfu/v0.3/ontology/librarian/registry-schema.md` documenting the JSON schema for `exfu/derived/librarian-registry.json`.

The registry tracks:
- Each installed librarian: name, cadence, implementation details, source definition path, enabled flag, install timestamp, last run, last status, consecutive failure count
- Each active cadence: which scheduled task backs it, last run timestamp

### 4. Run log schema

Document the JSON schema for `exfu/derived/librarian-log.json`:
- Array of run records, each with cadence, start/end timestamps, and per-librarian results
- Capped at 90 days (the runner trims older entries on each write)

### 5. Convention base agent.md updates

Update `exfu/v0.3/librarians/agent.md` to reference the structured format. An agent reading this folder should understand: what a librarian definition looks like, how to write one, how the registry works.

---

## Acceptance criteria

1. Every librarian definition in the convention base has valid YAML frontmatter
2. `what-is-a-librarian.md` describes the structured format with examples
3. Registry schema is documented and a skeleton `librarian-registry.json` is defined
4. Run log schema is documented
5. `librarians/agent.md` references the new format
6. An agent reading the convention base can write a correctly-formed librarian definition without further guidance

---

## Files to create/modify

- Modify: `exfu/v0.3/ontology/librarian/nightly-index.md`
- Modify: `exfu/v0.3/ontology/librarian/version-cleanup.md`
- Modify: `exfu/v0.3/ontology/librarian/what-is-a-librarian.md`
- Modify: `exfu/v0.3/librarians/agent.md`
- Create: `exfu/v0.3/ontology/librarian/registry-schema.md`
- Create: `exfu/v0.3/ontology/librarian/run-log-schema.md`

---

## Where this plan lives

- This file: `plugin/planning/T3-librarian-definitions.md`
- Domain: `plugin/planning/T2-librarian-framework.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
