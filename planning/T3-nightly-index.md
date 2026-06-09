# T3 -- Nightly index

Update the substrate-index librarian to produce a single global index in exfu/derived/, with sections per exfu version in use. The index is the whole-substrate map that agents and the visualisation depend on.

**Parents:** `T2-substrate-architecture.md` (domain), `T2-shared-skills-and-resources.md` (the index librarian is a shared skill), `M2-substrate-redesign.md` (milestone)
**Prerequisites:** T3-convention-base, T3-scope-model, T3-versioning (the structure must exist before it can be indexed)
**Status:** not started.

---

## Why

Without the index, an agent entering the substrate has to walk the entire directory tree to understand what exists. With a few scopes that's fine. With twenty scopes across nested levels, it's slow and expensive in context tokens.

The global index gives any agent a whole-substrate picture in one read: every scope, its tree position, which folder-types are populated, version pins, and ontology chain. It also feeds the HTML visualisation (a separate deliverable, M3 or later).

The current substrate-index scheduled task (v0.2.x, `index.py`) maps the old orgs/teams structure. It needs to be rewritten for the scope-based model.

---

## What to build

### 1. Index schema

The index is JSON. It lives at `exfu/derived/index.json`.

```json
{
  "generated": "2026-06-10T02:00:00Z",
  "substrate_root": "/path/to/substrate",
  "exfu_versions": {
    "v0.3": {
      "is_latest": true,
      "scopes_using": ["Acme", "Q3 Renewal", "Side Project"]
    }
  },
  "scopes": [
    {
      "name": "Alastair",
      "path": "user/",
      "type": "user",
      "parent": null,
      "exfu_version": null,
      "folder_types": {
        "ontology": "data",
        "context": "data",
        "todo": "pointer",
        "reminders": "empty",
        "inbox": "data",
        "skills": "data",
        "librarians": "empty",
        "docs": "empty",
        "databases": "empty",
        "visualisations": "empty"
      }
    },
    {
      "name": "Acme",
      "path": "scopes/acme/",
      "type": "scope",
      "parent": "root",
      "exfu_version": "v0.3",
      "folder_types": {
        "ontology": "data",
        "context": "data",
        "todo": "pointer",
        "docs": "data"
      },
      "children": [
        {
          "name": "Q3 Renewal",
          "path": "scopes/acme/scopes/q3-renewal/",
          "type": "scope",
          "parent": "Acme",
          "exfu_version": "v0.3",
          "folder_types": {
            "context": "data",
            "todo": "data"
          }
        }
      ]
    }
  ]
}
```

**Scope entry fields:**
- `name` -- from scope.md frontmatter
- `path` -- relative to substrate root
- `type` -- "user", "scope", or "exfu"
- `parent` -- parent scope name (null for user, "root" for top-level scopes)
- `exfu_version` -- the version pin from scope.md (null for user)
- `folder_types` -- map of folder-type name to status:
  - `"data"` -- directory exists and contains files beyond agent.md/readme.md
  - `"pointer"` -- directory exists, agent.md indicates external system
  - `"empty"` -- directory exists but contains only agent.md/readme.md (or is absent)
- `children` -- nested array of child scopes (recursive)

**Top-level fields:**
- `generated` -- ISO 8601 timestamp
- `substrate_root` -- absolute path
- `exfu_versions` -- summary of version directories, which is latest, which scopes use each

### 2. Folder-type status detection

The indexer determines status for each folder-type:

- **"data"**: directory exists and contains at least one file that isn't agent.md or readme.md
- **"pointer"**: directory exists and agent.md contains keywords indicating external storage ("tasks are in", "lives in", "managed by", "use the ... connector"). Simple heuristic -- scan for pointer-pattern phrases.
- **"empty"**: directory doesn't exist, or exists but only contains agent.md/readme.md with no pointer indicators
- Only include folder-types that are present (data or pointer) or that are in the standard catalogue. Don't list custom folder-types that are empty.

### 3. Implementation approach

The existing `index.py` (in `plugin/src/shared/scheduled-tasks/substrate-index/`) walks the filesystem and produces the index. Rewrite it to:

1. Find the substrate root (same detection as current: look for exfu/ directory)
2. Read exfu/ to discover version directories, resolve `latest`
3. Walk user/ -- read scope.md, scan folder-types
4. Walk scopes/ recursively -- for each scope.md found, read frontmatter, scan folder-types, recurse into scopes/ subdirectory
5. Assemble the JSON structure
6. Write to exfu/derived/index.json

**Language:** Python 3 (consistent with existing index.py). No dependencies beyond stdlib. The scheduled task runs nightly via the substrate-index cron.

### 4. What changes from v0.2.x index

| v0.2.x | v0.3.0 |
|---|---|
| Walks orgs/, teams/, scopes/ separately | Walks user/ + scopes/ uniformly |
| No version awareness | Tracks exfu version pins per scope |
| Flat scope list | Nested tree (children arrays) |
| No folder-type status | Reports data/pointer/empty per folder-type |
| Output location varies | Always exfu/derived/index.json |

### 5. Error handling

- Missing scope.md frontmatter fields: use sensible defaults (name = directory name, parent = "unknown", exfu_version = null)
- Malformed YAML: skip the scope, log a warning
- Permission errors: skip the directory, log a warning
- The index should always be produced, even if partial. A partial index is more useful than no index.

---

## Acceptance criteria

1. `exfu/derived/index.json` is produced by running the updated index script
2. The index contains every scope in the substrate with correct tree nesting
3. Each scope entry includes name, path, type, parent, exfu_version, folder_types
4. Folder-type status correctly distinguishes data, pointer, and empty
5. Version summary tracks which versions exist and which scopes use each
6. The index is valid JSON and parseable by the visualisation (when built)
7. The script handles edge cases gracefully (missing frontmatter, permissions, malformed YAML)
8. The example prototype's index.json (T3-example-prototype) matches what this script would produce for that substrate

---

## Files to create/modify

- `plugin/src/shared/scheduled-tasks/substrate-index/index.py` -- rewrite
- `plugin/example/exfu/derived/index.json` -- example output (cross-reference T3-example-prototype)
- Convention base `exfu/v0.3/librarians/nightly-index.md` -- librarian definition (cross-reference T3-convention-base)

---

## Where this plan lives

- This file: `plugin/planning/T3-nightly-index.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`, `plugin/planning/T2-shared-skills-and-resources.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
