# T3 -- Scope model

Implement the scope.md format, scopes/ nesting convention, reference+delta agent.md pattern, and protective headers. This makes the scope concept concrete and buildable.

**Parents:** `T2-substrate-architecture.md` (domain), `M2-substrate-redesign.md` (milestone)
**Prerequisites:** T3-convention-base (the convention base must exist for agent.md files to reference it)
**Status:** not started.

---

## Why

The scope is the single structural concept in v0.3.0. Everything else -- discovery, nesting, convention management, the index -- depends on scopes having a predictable shape. This T3 defines what that shape is in implementation-ready detail so that every scope created (by install conversations, by users, by agents) follows the same conventions.

---

## What to build

### 1. scope.md format

The boundary marker that identifies a directory as a scope. Minimal by design -- the rich picture lives in the global index, not here.

```markdown
---
name: <scope-name>
purpose: <one-line purpose>
parent: <parent-scope-name or "root">
exfu: v0.3
---

> This scope follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

<Optional 2-3 sentence elaboration of purpose. Not required.>
```

**Fields:**
- `name` -- the scope's human-readable name. Does not need to match the directory name (but usually will).
- `purpose` -- one sentence. What this scope is for. Enough for an agent to decide whether to read deeper.
- `parent` -- the name of the parent scope, or "root" for top-level scopes under scopes/. This is what makes extraction/sharing safe -- the agent knows something is above it.
- `exfu` -- the exfu version this scope's conventions reference. New scopes default to whatever `latest` points to. Existing scopes keep their pin until explicitly migrated.

**What scope.md does NOT contain:**
- Entities, conventions, current state, dependencies (these live in folder-types)
- Status, dates, target-close (these are captured by the global index or by todo/)
- YAML arrays of related skills or dependencies (scope is a boundary marker, not a knowledge store)

### 2. user/ scope.md

The user scope is special: unversioned, personal, sits at the substrate root.

```markdown
---
name: <username>
purpose: Personal workspace and global defaults
parent: none
---

> This scope follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.
```

No `exfu:` field. user/ doesn't pin a version -- it's always current. Migration is by user decision.

### 3. scopes/ nesting convention

A scope gathers child scopes in a dedicated `scopes/` subdirectory. Rules:

- A scope's own folder-types (ontology/, todo/, context/, etc.) sit at the scope's root level
- Child scopes ONLY appear inside `scopes/`
- `scopes/` is not a folder-type -- it's a structural convention. It has no agent.md or readme.md
- Grouping folders (directories without scope.md) can appear inside scopes/ for organisation. E.g. `scopes/teams/sales/` where `teams/` is just a grouping folder and `sales/` is the actual scope
- Nesting depth is unlimited but practical use rarely exceeds 3 levels

Example:
```
acme/
  scope.md                 # name: Acme, parent: root
  ontology/
  context/
  todo/
  scopes/
    sales/
      scope.md             # name: Sales, parent: Acme
      ontology/
      todo/
      scopes/
        q3-renewal/
          scope.md          # name: Q3 Renewal, parent: Sales
          context/
          todo/
```

### 4. Reference+delta agent.md pattern

Every folder-type directory inside a scope contains an agent.md that follows this pattern:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/todo.md

Local deviations:
- Tasks are tracked in ClickUp, not stored locally
- Use the ClickUp MCP connector for read/write
- Tag all tasks with scope name "acme-sales"
```

**Structure:**
1. Protective header (blockquote, always first)
2. `Follows:` line naming the upstream convention by versioned path
3. `Local deviations:` section listing only what differs from upstream. If nothing differs, omit this section entirely

**A folder with no deviations:**
```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

Follows: exfu/v0.3/ontology/folder-types/context.md
```

That's it. Two lines plus the header. The agent reads the upstream convention for full behaviour.

**readme.md** follows the same pattern but in human language. Can be even shorter:
```markdown
Context for the Acme account. See ExFu conventions for details.
```

### 5. Protective headers

The blockquote header appears in both scope.md and agent.md. Its job is to catch agents that wander into the substrate without having loaded ExFu skills/context. The exact wording:

> This folder follows ExFu conventions. If you haven't loaded them yet, ask your user to set you up with their WoW or ExFu skills.

Consistent across every file. Not customised per scope or folder-type.

---

## Implementation notes

### Where these conventions are documented

The scope model conventions live in two places:

1. **In the convention base** (T3-convention-base): `exfu/v0.3/ontology/scope/` defines what a scope is, the scope.md format, nesting rules, the reference+delta pattern. This is what agents read at runtime.

2. **In the install skills** (M3, not this milestone): the install conversation creates scopes following these conventions. The conventions must be stable before install skills are rewritten.

### Templates for scope creation

Create templates that an agent (or the install conversation) can use to scaffold a new scope:

- `plugin/src/shared/templates/scope/` -- a minimal scope directory with scope.md template and empty folder-type directories with stub agent.md files

These templates are used at scope-creation time, not installed into the substrate. They live in the plugin source.

---

## Acceptance criteria

1. scope.md format is documented and a template exists
2. user/ scope.md format is documented (unversioned variant)
3. scopes/ nesting convention is documented with examples
4. reference+delta agent.md pattern is documented with examples (with and without deviations)
5. Protective header wording is finalised and consistent
6. A scope-creation template exists in plugin/src/shared/templates/scope/
7. An agent reading the documentation can create a correctly-formed scope without further guidance

---

## Files to create/modify

- `plugin/src/shared/templates/scope/scope.md` -- template
- `plugin/src/shared/templates/scope/ontology/agent.md` -- stub
- `plugin/src/shared/templates/scope/context/agent.md` -- stub
- `plugin/src/shared/templates/scope/docs/agent.md` -- stub
- `plugin/src/shared/templates/scope/skills/agent.md` -- stub
- `plugin/src/shared/templates/scope/librarians/agent.md` -- stub
- `plugin/src/shared/templates/scope/todo/agent.md` -- stub
- `plugin/src/shared/templates/scope/reminders/agent.md` -- stub
- `plugin/src/shared/templates/scope/inbox/agent.md` -- stub
- `plugin/src/shared/templates/scope/databases/agent.md` -- stub
- `plugin/src/shared/templates/scope/visualisations/agent.md` -- stub
- `plugin/src/shared/templates/scope/readme.md` -- stub
- Update convention base ontology/scope/ with the finalised format (cross-reference T3-convention-base)

---

## Where this plan lives

- This file: `plugin/planning/T3-scope-model.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
