# T3 -- Build system update

Extend build.sh to package the versioned exfu/ convention base into plugin output so that the install skill can deploy it into the user's substrate.

**Parents:** `T2-build-and-distribution.md` (domain), `M2-substrate-redesign.md` (milestone)
**Prerequisites:** T3-convention-base (the convention base must exist in plugin source before the build can package it)
**Status:** not started.

---

## Why

The current build system composes skills, resources, templates, and scheduled tasks from `plugin/src/shared/` + `plugin/src/<variant>/` into a plugin package. It doesn't know about the substrate convention base because v0.2.x didn't ship one -- the substrate was built entirely by the install conversation.

v0.3.0 ships a convention base (`exfu/v0.3/`) that must be installed into the user's substrate. The build system needs to include this material in the plugin package so the install skill can deploy it.

---

## What to build

### 1. New source directory

The convention base lives at:

```
plugin/src/shared/substrate/exfu/v0.3/
  ontology/
  context/
  skills/
  librarians/
  ...
```

This is the source of truth for the convention base. It's built by T3-convention-base and becomes part of every plugin variant's output.

### 2. Build script changes

`plugin/build/build.sh` currently copies from these source paths:

```
plugin/src/shared/skills/       -> output/<variant>/skills/
plugin/src/shared/resources/    -> output/<variant>/resources/
plugin/src/shared/templates/    -> output/<variant>/templates/
plugin/src/shared/scheduled-tasks/ -> output/<variant>/scheduled-tasks/
plugin/src/<variant>/skills/    -> output/<variant>/skills/  (overlay)
plugin/src/<variant>/resources/ -> output/<variant>/resources/ (overlay)
```

Add a new copy step:

```
plugin/src/shared/substrate/    -> output/<variant>/substrate/
```

This copies the entire substrate directory (including the versioned exfu/ convention base and any templates) into the plugin package.

### 3. What the install skill does with it

At install time, the install skill:

1. Reads the convention base from the plugin package (`${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/`)
2. Copies it into the user's substrate at `<substrate-root>/exfu/v0.3/`
3. Creates the `latest` symlink (or latest.txt fallback)
4. Creates the `derived/` directory
5. Creates the user/ scope with the scope.md template

The install skill changes are M3 (not this milestone). For M2, the build system just needs to include the material. The install skill's v0.2.x behaviour continues to work; the convention base is additional material available for when the install is rewritten.

### 4. Plugin package structure after update

```
output/<variant>/
  .claude-plugin/
    plugin.json
  skills/
    ...
  resources/
    ...
  templates/
    ...
  scheduled-tasks/
    ...
  substrate/                    # NEW
    exfu/
      v0.3/
        ontology/
        context/
        ...
    templates/
      scope/                    # scope creation template
        scope.md
        ontology/
          agent.md
        ...
```

### 5. Scope creation templates

The scope creation templates (from T3-scope-model) also live under `plugin/src/shared/substrate/templates/` and get packaged the same way. These are used by the install skill (and future scope-creation skills) to scaffold new scopes.

### 6. Dist packaging

The `--dist` flag produces versioned zips. No changes needed to the zip step -- it already zips the entire output directory. The convention base is just more files in the output.

Check that the zip size remains reasonable. The convention base is mostly small markdown files (~35 files, probably under 100KB total). Should be negligible.

---

## Implementation notes

### Avoid breaking existing builds

The new copy step must be additive. If `plugin/src/shared/substrate/` doesn't exist yet (e.g. someone runs a build before T3-convention-base is done), the build should skip the step rather than fail. A simple existence check:

```bash
if [ -d "$SHARED_DIR/substrate" ]; then
  cp -r "$SHARED_DIR/substrate" "$OUTPUT_DIR/substrate"
fi
```

### No variant-specific substrate content

The convention base is shared across all three plugin variants. There is no solo-specific or team-specific convention base. If variant-specific substrate material is ever needed, it would follow the same overlay pattern as skills (variant overrides shared), but for M2 this is not anticipated.

---

## Acceptance criteria

1. `build.sh` copies `plugin/src/shared/substrate/` into each variant's output
2. Build succeeds when substrate/ directory is present
3. Build succeeds (skips step) when substrate/ directory is absent
4. `--dist` zips include the substrate material
5. All three variant builds include the same convention base
6. Plugin package size increase is documented and reasonable

---

## Files to modify

- `plugin/build/build.sh` -- add substrate copy step

---

## Where this plan lives

- This file: `plugin/planning/T3-build-system.md`
- Domain: `plugin/planning/T2-build-and-distribution.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
