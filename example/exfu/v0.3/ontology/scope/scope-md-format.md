# scope.md format

The boundary marker that identifies a directory as a scope. Minimal by design -- the rich picture lives in the global index, not here.

## Format

```yaml
---
name: <scope-name>
purpose: <one-line purpose>
parent: <parent-scope-name or "root">
exfu: v0.3
---
```

Followed by:

```markdown
> This folder follows ExFu conventions. If you haven't loaded them yet,
> ask your user to set you up with their WoW or ExFu skills.

<Optional 2-3 sentence elaboration of purpose.>
```

## Fields

- **name** -- human-readable name. Doesn't need to match the directory name (but usually will).
- **purpose** -- one sentence. What this scope is for. Enough for an agent to decide whether to read deeper.
- **parent** -- the name of the parent scope, or "root" for top-level scopes under scopes/. Makes extraction/sharing safe -- the agent knows something is above it.
- **exfu** -- the ExFu convention version this scope references. New scopes default to whatever `latest` points to. Existing scopes keep their pin until explicitly migrated.

## Special cases

- **user/ scope:** no `exfu:` field. The personal scope is unversioned -- it always reads through `latest`.
- **exfu/ itself:** no scope.md at all. It's a special location, not a scope.

## What scope.md does NOT contain

- Entities, conventions, current state, dependencies (these live in folder-types)
- Status, dates, target-close (captured by the global index or by todo/)
- Arrays of related skills or dependencies (scope.md is a boundary marker, not a knowledge store)
