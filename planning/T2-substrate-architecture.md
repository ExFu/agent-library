# T2 -- Substrate architecture

The structural model of the substrate itself: how scopes, folder-types, conventions, versioning, and discovery work. This is the domain that defines what agents build *into* and navigate *through*. Every other T2 workstream (skills, install conversations, build pipeline, teaching artefacts) depends on this architecture being stable.

Anchors back to: `T1-overview.md`, `v0.3.0-reconciliation.md` (definitive design decisions), `v0.3.0-substrate-revision.md` (original design doc), `cross-cut-storage-architecture.md`.

---

## Why

The substrate is the user's installed AI setup -- knowledge base, skills, connectors, scheduled tasks. Its folder structure is the skeleton everything hangs on. Skills reference it. Install conversations build it. Librarians maintain it. The nightly index maps it. Agents discover context by navigating it.

v0.2.x used a multi-concept structural model (orgs/, teams/, scopes/, personal layer) that didn't match how people actually organise work. v0.3.0 replaces this with a uniform scope-based model designed around bounded working contexts rather than organisational hierarchy.

This T2 is the architectural reference for the substrate structure. It doesn't cover what goes *inside* skills (that's T2-shared-skills-and-resources), how plugins are packaged (T2-build-and-distribution), or how install conversations flow (the variant T2s). It covers the structural shape that all of those depend on.

The audience is implementation agents building T3 work against the substrate structure, and future design sessions that need to understand why decisions were made.

---

## How

### Core concepts

All structural decisions below are resolved. See `v0.3.0-reconciliation.md` for the full reasoning behind each.

**Scope.** A bounded working context with a uniform internal structure. Everything is a scope: a project, a team, a client engagement, a personal space. The structural differences between v0.2.x's orgs/, teams/, scopes/, and the personal layer collapse into this one concept. A scope is identified by having a `scope.md` file.

**Folder-type catalogue.** Inside any scope, a standard vocabulary of "where things go." Each folder-type is a discovery convention first, a storage location second. The catalogue:

| Folder | Purpose |
|---|---|
| `ontology/` | What concepts and terms mean in this scope |
| `context/` | Background an agent should know about this scope |
| `docs/` | Captured documents that need keeping |
| `skills/` | Skill definitions or drafts related to this scope |
| `librarians/` | Scheduled maintenance definitions for this scope |
| `todo/` | How this scope handles tasks |
| `reminders/` | How this scope handles lightweight nudges |
| `inbox/` | Where uncategorised thoughts go for this scope |
| `databases/` | Structured data with schemas for this scope |
| `visualisations/` | Agent-created visual outputs (HTML, web views) |

The catalogue is open -- any scope may add folder-types not listed here, defined in that scope's ontology/.

**Store-or-point.** Every folder-type supports a first-class choice: store data locally, or point to an external system. A todo/ folder may contain task files, or its agent.md may say "tasks are in ClickUp." The convention guarantees the location is discoverable; whether data lives there is per-scope, per-user.

**Reference + delta (agent.md).** Convention management follows the package management pattern. agent.md references the upstream convention in exfu/ and records only local deviations. No copying of upstream content. A librarian can detect when the upstream changed and flag it. No automatic propagation -- the user decides when to update.

**Protective headers.** Both scope.md and agent.md open with a guard: "This folder follows ExFu conventions. If you haven't loaded them yet, ask your user to set you up with their WoW or ExFu skills." This catches agents entering the substrate without context.

### Top-level structure

```
substrate/
  exfu/                          # special location, plugin-owned
    v0.3/                        # versioned convention set
      ontology/                  # base vocabulary for the whole substrate
      skills/
      librarians/
      ...                        # same folder-types as any scope
    latest -> v0.3/              # symlink to current version
    derived/                     # unversioned generated content
      index.json                 # single global index
  user/                          # special scope, personal tier, unversioned
    scope.md
    ontology/
    context/
    ...
  scopes/                        # the tree of everything else
    <scope-name>/
      scope.md
      ontology/
      ...
      scopes/                    # child scopes gathered here
        <child-scope>/
          scope.md
          ...
```

**exfu/ is a special location, internally structured like a scope.** Not a scope itself (no scope.md, not user-editable, owned by the plugin). But internally uses the same folder-type catalogue. Agents discover its contents the same way they discover any scope's contents.

**user/ is the personal scope.** Unversioned -- it doesn't pin an exfu version. Migration is by user decision. It's a real scope (has scope.md) but sits at a fixed root position alongside exfu/.

**scopes/ is the tree of everything else.** All user-created scopes live here, nested via their own scopes/ subdirectories.

### Scope nesting

Self-similar recursion. A scope gathers child scopes in its own `scopes/` directory. Child scopes never sit loose among the parent's working folders. Each nested scope explicitly declares its parent in scope.md, so if the scope is shared or extracted, the agent knows something is missing from its ontologies.

### Versioning model

exfu/ is versioned using semver breaking-change boundaries:

- **Pre-1.0:** directory is the minor version (v0.3, v0.6) because pre-1.0 minors can be breaking
- **Post-1.0:** directory is the major version (v1, v3) because only majors break
- Patches and non-breaking minors update in-place within the existing version directory

**Scope pinning.** scope.md declares which exfu version the scope expects. agent.md references the versioned path (e.g. exfu/v0.3/ontology/todos/). New scopes default to `latest`.

**Side-by-side installation.** Plugin updates install the new version directory alongside existing ones and flip the `latest` symlink. Existing scopes keep working against their pinned version.

**Migration instructions live in the plugin, not the substrate.** The plugin ships migration docs that agents read at runtime. The substrate stays clean.

**User scope is unversioned.** user/ doesn't pin a version. Migration is by user decision.

### Ontology model

No automatic cascade. No deterministic precedence rule. Ontology conflicts can be orthogonal, overrides, or extensions -- a cascade rule can't distinguish these.

- **Reading agents** are aware that conflicts may exist. They read all relevant ontologies and use judgement. When genuinely ambiguous, they ask the user.
- **Writing agents** must annotate intent when creating ontologies that touch existing terms -- the annotation is for later consuming agents.
- Ontologies may be lifted (scope definition promoted to user-level) or independently conflict. Best efforts, not perfect state.

### Discovery model

An agent entering the substrate discovers structure through:

1. **scope.md** -- identifies this is a scope, gives name/purpose/parent/version pin
2. **Folder-type directories** -- the agent knows the catalogue; presence of a folder means the scope handles that concern
3. **agent.md in each folder** -- gives the reference to upstream conventions plus local deviations
4. **The global index** (exfu/derived/index.json) -- whole-substrate map showing every scope, its tree position, which folder-types are populated, version pins
5. **Protective headers** -- if an agent arrives without context, the header tells it to get set up first

### The global index

A single index in exfu/derived/, with sections for each exfu version in use. Produced by the nightly index librarian. Gives agents a true whole-substrate picture. Each version's indexing librarian contributes to the global index.

Contents: scope tree, folder-type population status per scope (data-bearing, pointer-only, empty), version pins, ontology chain per scope. The index feeds the HTML substrate visualisation (the first thing to live in a visualisations/ folder).

### Trade-offs being made

- **Uniform vs specialised.** We pick uniform (one scope concept, one folder-type catalogue) at the cost of exfu/ not having dedicated homes for principles, recommendations, conventions as separate concerns (the pre-direction model). These can live as subdirectories within ontology/ or context/ instead.
- **Reference+delta vs snapshots.** We pick lean references at the cost of folders not being fully self-contained. A scope extracted without exfu/ loses its convention base. The protective header makes this visible rather than silent.
- **Accept ontology chaos vs cascade rules.** We pick accepting chaos at the cost of agents needing to use judgement on conflicts rather than following a deterministic rule.
- **Versioned exfu/ vs single exfu/.** We pick versioning at the cost of directory complexity. The benefit is clean migration paths and side-by-side support during transitions.
- **Global index vs per-scope indexes.** We pick one global index at the cost of scopes not being independently navigable without exfu/derived/. The benefit is a true whole-substrate picture, especially for cross-scope referencing.

---

## What

### Components this T2 defines

1. **scope.md format** -- the boundary marker for every scope
2. **Folder-type catalogue** -- the 10 standard types plus the open extension convention
3. **agent.md / readme.md convention** -- reference+delta pattern with protective headers
4. **Versioned exfu/ structure** -- version directories, latest symlink, derived/
5. **Scope nesting convention** -- scopes/ subdirectories, parent declarations
6. **Ontology model** -- no cascade, write-time discipline, conflict awareness
7. **Global index schema** -- what the nightly index produces and where it lives
8. **Discovery model** -- how agents orient in the substrate

### T3 implementation topics (scoped to M2)

Each of these becomes a T3 plan, parented by this T2 and the M2 milestone:

1. **T3-convention-base** -- build exfu/v0.3/ with agent.md templates for each folder-type
2. **T3-scope-model** -- implement scope.md format, scopes/ nesting, reference+delta agent.md
3. **T3-versioning** -- version directories, latest symlink, derived/, scope pinning
4. **T3-example-prototype** -- rebuild plugin/example/ to demonstrate the resolved design
5. **T3-nightly-index** -- global version-aware index (also parents to T2-shared-skills-and-resources)
6. **T3-build-system** -- extend build.sh for versioned convention base (parents to T2-build-and-distribution)

### Dependencies

- **From this T2:** the v0.3.0 design decisions in `v0.3.0-reconciliation.md` are settled. No open structural questions remain for M2 scope.
- **To other T2s:** T2-shared-skills-and-resources depends on this architecture for skill packaging. T2-build-and-distribution depends on this for knowing what to package. The variant T2s (solo, team, team-admin) depend on this for install conversation design (M3, not M2).
- **Cross-cuts:** cross-cut-storage-architecture (Box vs git constraints), cross-cut-planning-approach (milestone/T2/T3 framework).

---

## Open questions

1. **scope.md YAML frontmatter.** The reconciliation says "minimal" but doesn't specify the exact fields. Proposed: name, purpose, parent, exfu-version. Anything else? Status and dates were in the pre-direction model but were rejected as drift-prone. The index captures dynamic state instead.

2. **Folder-type catalogue -- where do principles and recommendations live?** The pre-direction had dedicated exfu/ folders for these. In the uniform model, they'd live within exfu/v0.3/ontology/ or exfu/v0.3/context/. Need to decide the specific home during T3-convention-base.

3. **Symlink portability.** The `exfu/latest` symlink may not work on Box (solo plugin) or on Windows without developer mode. Fallback: a `latest.txt` file containing the version path. Needs testing during T3-versioning.

---

## Where this plan lives

- This file: `plugin/planning/T2-substrate-architecture.md`
- Design decisions: `plugin/planning/v0.3.0-reconciliation.md`
- Original design doc: `plugin/planning/v0.3.0-substrate-revision.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
- T1 overview: `plugin/planning/T1-overview.md`
