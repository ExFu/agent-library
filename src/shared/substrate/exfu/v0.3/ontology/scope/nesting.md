# Scope nesting

Scopes nest via a dedicated `scopes/` subdirectory. The pattern is self-similar -- it repeats at every level.

## Rules

1. A scope's own folder-types (ontology/, todo/, context/, etc.) sit at the scope's root level.
2. Child scopes ONLY appear inside a `scopes/` subdirectory.
3. `scopes/` is not a folder-type. It has no agent.md or readme.md. It's a structural convention.
4. Grouping folders (directories without scope.md) can appear inside scopes/ for organisation. E.g. `scopes/teams/sales/` where `teams/` is just a grouping folder and `sales/` is the actual scope.
5. Nesting depth is unlimited but practical use rarely exceeds 3 levels.

## Parent declaration

Every nested scope declares its parent in scope.md:

```yaml
parent: Acme
```

This matters when a scope is shared or extracted in isolation -- the agent sees the parent declaration and knows that ontologies, conventions, and context from the parent scope are missing. It can then ask the user for context rather than silently operating with incomplete information.

## Example

```
acme/
  scope.md            # parent: root
  ontology/
  todo/
  scopes/
    sales/
      scope.md        # parent: Acme
      ontology/
      scopes/
        q3-renewal/
          scope.md    # parent: Sales
          context/
          todo/
```

## Why scopes/ and not just nesting loose

Without the `scopes/` boundary, child scope directories mix with folder-type directories. An agent entering a scope can't tell which directories are folder-types (with known conventions) and which are child scopes (with their own independent structure). The `scopes/` directory makes the boundary unambiguous.
