# T3 -- Convention base (exfu/v0.3/)

Build the versioned convention base that all scopes reference. This is the single source of truth for what each folder-type means and how it behaves by default.

**Parents:** `T2-substrate-architecture.md` (domain), `M2-substrate-redesign.md` (milestone)
**Prerequisites:** None. This is M2's first deliverable -- everything else depends on it.
**Status:** not started.

---

## Why

Every scope's agent.md references upstream conventions via a versioned path (e.g. `exfu/v0.3/ontology/todos/`). Those conventions must exist before any scope can reference them. This T3 creates the convention base -- the "package" that scopes depend on.

The convention base also defines ExFu's opinionated defaults: what a todo is, what a reminder is, how an inbox works, what ontology means. These are the sane defaults that make a fresh scope useful without the user having to configure everything from scratch.

---

## What to build

### Directory structure

```
plugin/src/shared/substrate/exfu/v0.3/
  ontology/
    agent.md              # meta: what ontology means, how to read/write definitions
    readme.md
    scope/                # what a scope is, how nesting works, scope.md format
    folder-types/         # one file per catalogue entry defining its purpose/conventions
    librarian/            # what a librarian is, how they're defined and run
  context/
    agent.md              # what context/ is for, how to maintain it
    readme.md
  docs/
    agent.md              # what docs/ is for, retention vs working docs
    readme.md
  skills/
    agent.md              # what skills/ is for, skill packaging conventions
    readme.md
  librarians/
    agent.md              # how librarian definitions work in this scope
    readme.md
  todo/
    agent.md              # what todo means, store-or-point pattern, task conventions
    readme.md
  reminders/
    agent.md              # what reminders are, how they differ from todos
    readme.md
  inbox/
    agent.md              # what inbox is for, triage conventions, sweep librarian hook
    readme.md
  databases/
    agent.md              # what databases/ is for, schema conventions
    readme.md
  visualisations/
    agent.md              # what visualisations/ is for, sub-folder convention
    readme.md
```

### agent.md template content (for each folder-type)

Each agent.md in the convention base is the *canonical definition* -- the thing that downstream scope agent.md files reference. It must:

1. **Open with the golden circle.** Why this folder-type exists (what problem it solves for the user). How it works (store-or-point, conventions, relationship to other folder-types). What agents should do when they encounter it.

2. **Define the default behaviour.** What an agent should do in a standard folder of this type with no local deviations. This is the behaviour a scope inherits by reference.

3. **Name the boundaries.** What does NOT belong in this folder-type. E.g. "todo/ is for tasks with a completion state. Lightweight time-based nudges belong in reminders/. Uncategorised thoughts belong in inbox/."

4. **Describe the store-or-point pattern** for this folder-type. What a stored version looks like. What a pointer version looks like. Examples of both.

5. **Be concise.** These are read by agents on every scope entry. Target 30-50 lines per agent.md. Rich enough to be useful, lean enough not to bloat context.

### readme.md template content

The same information as agent.md, written for human eyes. Plain language, no agent-specific instructions. Can be shorter -- humans browse; they don't need the full behavioural spec.

### ontology/ special content

The ontology folder in exfu/v0.3/ is special -- it defines the structural vocabulary of the substrate itself:

- **scope/** -- what a scope is, the scope.md format (name, purpose, parent, exfu-version), nesting via scopes/, the parent declaration convention
- **folder-types/** -- one definition file per catalogue entry. Each explains the folder's purpose, default conventions, store-or-point examples, and boundaries with other types
- **librarian/** -- what a librarian is, how definitions work, the nightly index as the canonical example

### Content sources

Draw from:
- `v0.3.0-reconciliation.md` -- the resolved design decisions (authoritative)
- `v0.3.0-substrate-revision.md` -- the folder-type catalogue table and store-or-point description
- `v0.3.0pre-direction.md` -- richer descriptions of conventions, principles, elicitation prompts (adapt, don't copy the structure)
- `plugin/example/exfu/` -- the existing prototype's content (follows pre-direction model, so adapt to new structure)
- `audit-skills-and-resources.md` -- quality guidance (avoid insider vocabulary, lead with Why not constraints)

### What about principles and recommendations?

The pre-direction had dedicated exfu/ folders for principles/ and recommendations/. In the uniform model, these live within the convention base:

- **Principles** (Golden Circle, outcome-framed elicitation, concrete-first, build-by-doing) belong in `exfu/v0.3/context/` as background an agent should know
- **Recommendations** (curated third-party suggestions) belong in `exfu/v0.3/context/` or `exfu/v0.3/docs/` depending on whether they're reference material or active guidance

Decide the specific home during implementation. The key constraint: agents must discover these when reading the exfu/ convention base, so they must be in a folder-type that agents routinely read.

---

## Acceptance criteria

1. `plugin/src/shared/substrate/exfu/v0.3/` exists with all 10 folder-type directories
2. Each folder-type directory contains agent.md and readme.md
3. ontology/ contains structural definitions (scope, folder-types, librarian)
4. Every agent.md follows the golden circle, is 30-50 lines, defines default behaviour, names boundaries, describes store-or-point
5. Every readme.md covers the same ground in human-readable form
6. The content draws from the resolved design decisions, not from either superseded doc alone
7. An agent reading only the convention base can understand: what each folder-type is for, how to behave in it, what store-or-point means, what a scope is, how nesting works

---

## Files to create

All under `plugin/src/shared/substrate/exfu/v0.3/`:
- 10 directories (one per folder-type) x 2 files each = 20 files
- ontology/ subdirectories (scope/, folder-types/, librarian/) with definition files = ~15 additional files
- Estimated total: ~35 files

---

## Where this plan lives

- This file: `plugin/planning/T3-convention-base.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
