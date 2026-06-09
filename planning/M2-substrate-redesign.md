# M2 -- Substrate redesign

The substrate folder structure is the foundation everything else in the plugin depends on. Skills reference it, install conversations build it, librarians maintain it, the index maps it. This milestone delivers the v0.3.0 substrate structure so that all downstream work (skill rewrites, install conversation redesign, librarian implementation) has a stable base to build against.

**Status:** not started. Design decisions resolved (see `v0.3.0-reconciliation.md`). Implementation next.

---

## Why

The v0.2.x substrate structure (orgs/, teams/, two-layer PII model) was designed around organisational hierarchy. Real users don't organise their work that way. A solo founder has projects, clients, and personal contexts -- not "orgs" and "teams." A team member has their team's shared context plus their own personal layer -- but the boundaries aren't org-chart-shaped.

v0.3.0 replaces this with **scopes** -- bounded working contexts that nest naturally and follow a uniform internal structure. The substrate becomes something users can grow themselves, not a structure they have to understand before they can use it.

This milestone's audience is:
- **Al** (sole builder) -- needs the structure to exist so skills and install conversations can be rewritten against it
- **Future implementation agents** -- need a worked example and clear conventions to build T3 work against
- **The skills audit backlog** -- the 13 skills needing work can't be properly fixed until the structure they reference is settled

Until M2 ships, everything downstream is blocked or building against the wrong model.

## How

### Sequencing

The work has a strict dependency chain:

1. **Convention base first.** Build `exfu/v0.3/` with the folder-type catalogue (ontology/, context/, docs/, skills/, librarians/, todo/, reminders/, inbox/, databases/, visualisations/). Each folder-type needs its agent.md template -- the upstream convention that scopes will reference. This is the foundation; nothing else can reference it until it exists.

2. **Scope model second.** Implement scope.md format (name, purpose, parent, version pin, protective header), the `scopes/` nesting convention, and the reference+delta agent.md pattern. Validate that a scope can reference exfu/v0.3/ conventions, record local deviations, and declare its parent.

3. **User scope and exfu/ structure third.** Build the `user/` scope (unversioned, personal tier) and the full `exfu/` directory (versioned convention directories, `latest` symlink, `derived/` for generated content). Validate that the versioning model works in practice.

4. **Worked example fourth.** Rebuild `plugin/example/` to demonstrate the resolved design: versioned exfu/, minimal scope.md, nested scopes via scopes/, reference+delta agent.md, protective headers. This replaces the existing example which follows the pre-direction model.

5. **Nightly index fifth.** Update the substrate-index librarian to produce a single global index in `exfu/derived/`, with sections per version. This validates the "one index, version-aware" model and gives agents the whole-substrate picture.

6. **Build system update sixth.** Extend build.sh to handle the versioned exfu/ structure -- the plugin needs to ship the v0.3/ convention base that gets installed into the user's substrate.

### Process

- Each step validates the previous one. If the convention base doesn't work, we find out when building the first scope -- not after rewriting all the skills.
- The worked example is a deliverable, not a throwaway. It's the reference implementation that future T3 agents build against.
- Skills and install conversations are explicitly OUT OF SCOPE for M2. They depend on this structure but are a separate milestone (M3).

### What "done" looks like

An agent can:
- Read exfu/v0.3/ and discover the convention base for all folder-types
- Create a new scope that references conventions via the versioned path
- Navigate nested scopes via scopes/ directories
- Read scope.md and know the scope's purpose, parent, and expected exfu version
- Read agent.md and find the upstream reference plus local deviations
- Read the global index and get a whole-substrate picture with version sections
- Build the plugin and have the convention base included in the output

## What

### Deliverables

1. **`exfu/v0.3/` convention base** -- the folder-type catalogue with agent.md templates for each type. Internally structured like a scope (same folder-types) but not a scope (no scope.md, plugin-owned). This is the single source of truth that all scopes reference.

2. **Scope model implementation** -- scope.md format, scopes/ nesting, reference+delta agent.md, protective headers. Documented conventions for how scopes declare parents, pin versions, and record local deviations.

3. **Versioning infrastructure** -- `exfu/latest` symlink, `exfu/derived/` directory, version-pinning in scope.md. Migration instructions live in the plugin (not the substrate).

4. **Rebuilt example prototype** -- `plugin/example/` rebuilt from scratch to demonstrate the resolved v0.3.0 design. Replaces the current pre-direction-model example.

5. **Updated nightly index** -- substrate-index librarian producing a single global index in `exfu/derived/` with version-aware sections.

6. **Updated build system** -- build.sh extended to package the versioned convention base into plugin output.

### Explicitly out of scope

- **Skill rewrites.** The 13 skills needing work (per the audit) are M3. They depend on M2's structure but shouldn't slow it down.
- **Install conversation redesign.** Depends on the scope model and convention base existing. M3.
- **Visualisation.** The HTML rendering of the index. Depends on the index existing. M3 or later.
- **Other librarians.** Beyond the nightly index, librarian definitions are TBD and will be solved case-by-case. M3 or later.
- **PII simplification.** The secrets-only rule is a policy decision already resolved. It doesn't require structural work -- just updating skill language when skills are rewritten in M3.

### Open questions

1. **Symlink support.** The `exfu/latest` symlink needs to work across Box (solo) and git (team). Box may not support symlinks. Fallback could be a `latest.txt` file containing the version path. Needs testing.
2. **Convention base content.** What exactly goes in each folder-type's agent.md template? This is the authoring work within step 1. The pre-direction's conventions/, principles/, and recommendations/ content may inform this, but the structure is different. Needs design during implementation.
3. **Index format.** JSON, markdown, or both? The visualisation (M3) will want structured data; agents may prefer markdown. Probably JSON primary with markdown rendered from it.

---

## Relationship to T2 workstreams

M2 draws from multiple T2 domains:

| T2 workstream | What M2 takes from it |
|---|---|
| T2-substrate-architecture | Primary domain: scope model, folder-types, conventions, versioning, discovery |
| T2-shared-skills-and-resources | Convention base content, skill packaging patterns, nightly index |
| T2-build-and-distribution | Build system extension |
| T2-solo-plugin | Box storage constraints (symlink question) |
| T2-team-plugin / T2-team-admin-plugin | Git storage patterns, shared/personal layer model |

### T3 implementation plans

Six T3 plans, in dependency order. Each references both this milestone (sequencing) and its T2 domain (architecture).

| T3 | Deliverable | T2 domain | Prerequisites |
|---|---|---|---|
| `T3-convention-base.md` | exfu/v0.3/ convention templates | T2-substrate-architecture | None (first) |
| `T3-scope-model.md` | scope.md, scopes/, reference+delta | T2-substrate-architecture | T3-convention-base |
| `T3-versioning.md` | Version dirs, symlink, derived/ | T2-substrate-architecture | T3-convention-base |
| `T3-example-prototype.md` | Rebuilt plugin/example/ | T2-substrate-architecture | T3-convention-base, T3-scope-model, T3-versioning |
| `T3-nightly-index.md` | Global version-aware index | T2-substrate-architecture, T2-shared-skills-and-resources | T3-convention-base, T3-scope-model, T3-versioning |
| `T3-build-system.md` | build.sh extension | T2-build-and-distribution | T3-convention-base |

---

## Where this plan lives

- This file: `plugin/planning/M2-substrate-redesign.md`
- Design decisions: `plugin/planning/v0.3.0-reconciliation.md`
- M1 (what's been done): `plugin/planning/M1-plugin-foundation.md`
- Domain: `plugin/planning/T2-substrate-architecture.md`
- Skills audit (feeds M3): `plugin/planning/audit-skills-and-resources.md`
