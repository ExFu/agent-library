# Wow template (v0.3.0 sketch)

This is the canonical template for the user's personal `wow` skill. Filled in by `exfu-create-wow` from the install conversation. The output is packaged as a skill-definition (see `exfu/skills/`) and rendered into the user's target platform.

## What wow does

Two jobs:

1. **Navigation map** — how this user's substrate is currently laid out, especially where it diverges from the ExFu defaults. So Claude (or another agent) can find files even when the user has reorganised or extended the structure.
2. **Thin always-on kernel** — high-leverage instructions and short summaries that justify their token cost by being universally relevant for this user.

Discipline: keep wow lean. Anything substantive lives in a file with a pointer from wow.

## Template body (sketch)

```
---
name: {{username}}-wow
description: {{username}}'s personal way of working. Read at session start.
---

# Way of Working — {{username-display}}

## Bootstrap

On activation:
1. Read this skill.
2. Load `exfu/principles/` and apply.
3. Read the substrate-index at `_meta/substrate-index.md`.
4. {{load-other-always-on-skills}}

## Navigation map

### Substrate shape
{{notes-about-deviations-from-default-shape}}

### Active scopes
{{list-of-active-scope-paths}}

### High-traffic files
{{pointers-to-files-the-user-references-often}}

## Always-on kernel

### Communication style
{{captured-preferences}}

### Decision-making defaults
{{captured-preferences}}

### Formatting preferences
{{captured-preferences}}

## Iterating this skill

(Standard guidance about how to update wow as the substrate evolves.)
```

## Difference from v0.2.x wow-template

The v0.2.x template is at `plugin/src/shared/templates/wow-template.md`. The v0.3.0 sketch above:

- Adds the bootstrap step to load `exfu/principles/` (new ontology type).
- Refers to `_meta/substrate-index.md` (carried over).
- Uses the three-tier composition implicitly: navigation map points at `user/`, `scopes/`, and notes any extension or override of ExFu defaults the user has made.

## Why this is a stub in the example

The full template is large. The point of this example is the shape (`exfu/templates/` carries fill-in templates) and the relationship to other ontology types. T2-D and T2-E (in the v0.3.0 plan) will produce the full template content as part of the install-conversation redesign and skill-definition rework.

## Dependencies

- Read by `exfu-create-wow` (a skill, not shown in this example).
- Renders into a per-user skill that lives in the user's Claude install (`~/.claude/skills/` or equivalent), not in the substrate.
