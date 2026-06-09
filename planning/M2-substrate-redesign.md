# M2 -- Substrate redesign

The substrate folder structure is the foundation everything else in the plugin depends on. Skills reference it, install conversations build it, librarians maintain it, the index maps it. This milestone delivers the v0.3.0 substrate structure and rewrites the skills that interact with it.

**Status:** Phase 1 complete (9 June 2026). Phase 2 in planning.

---

## Why

The v0.2.x substrate structure (orgs/, teams/, two-layer PII model) was designed around organisational hierarchy. Real users don't organise their work that way. A solo founder has projects, clients, and personal contexts, not "orgs" and "teams." A team member has their team's shared context plus their own personal layer, but the boundaries aren't org-chart-shaped.

v0.3.0 replaces this with **scopes**, bounded working contexts that nest naturally and follow a uniform internal structure. The substrate becomes something users can grow themselves, not a structure they have to understand before they can use it.

Until M2 ships completely, every user-facing skill is talking to the wrong model.

## How

### Phasing

**Phase 1 (complete):** Structural foundation. The convention base, scope model, versioning infrastructure, example prototype, nightly index rewrite, and build system update. Everything an agent needs to understand the v0.3 substrate exists.

**Phase 2 (current):** Making it usable. Librarian framework, scope setup skill with sane defaults, install skill rewrites, substrate/wow/guides skill rewrites. Everything a real user needs to actually use v0.3.

### Phase 1 deliverables (done)

1. **Convention base** -- `exfu/v0.3/` with 39 files: 10 folder-type agent.md/readme.md pairs, ontology definitions (scope, folder-types, librarians), principles, recommendations.
2. **Scope templates** -- 12 files in `templates/scope/` for scaffolding new scopes with reference+delta agent.md pattern.
3. **Versioning infrastructure** -- version-resolution.md, version-cleanup librarian definition.
4. **Example prototype** -- 80-file browsable substrate demonstrating all 10 design decisions.
5. **Nightly index** -- index.py rewritten for scope-based model, JSON output.
6. **Build system** -- build.sh extended to package substrate into plugin output.

### Phase 2 deliverables (planned)

7. **Librarian framework** -- Structured definition format, cadence-based runner, registry, install-librarian skill. See `T2-librarian-framework.md`.
8. **Scope setup skill** -- Guided scope creation with sane defaults for todo, reminders, inbox. See `T3-scope-setup-skill.md`.
9. **Install skill rewrite** -- All three install variants rewritten for v0.3 scope model. See `T3-install-skill-rewrite.md`.
10. **Substrate/wow/guides rewrite** -- Session bootstrap chain rewritten for v0.3. See `T3-substrate-skill-rewrite.md`.

### Process

- Phase 1 validates the structure. Phase 2 validates the user experience.
- Librarian framework before skill rewrites, because install skills need to register the nightly index librarian.
- Scope setup skill before install rewrite, because install uses scope setup.

### What "done" looks like

A new user can:
- Install the plugin and walk through a v0.3-aware install conversation
- End up with a working substrate (exfu/ convention base, user/ scope, at least one working scope)
- Have the nightly index librarian running
- Create new scopes with guided setup (including sane defaults for todo/reminders/inbox)
- Start a new session and have the substrate skill orient correctly to the scope-based model

## What

### T3 implementation plans (phase 2)

| T3 | Deliverable | T2 domain | Prerequisites |
|---|---|---|---|
| `T3-librarian-definitions.md` | Structured definition format, registry schema | T2-librarian-framework | T3-convention-base (phase 1) |
| `T3-nightly-runner.md` | Cadence-based librarian runner | T2-librarian-framework | T3-librarian-definitions |
| `T3-install-librarian-skill.md` | Skill to register librarians | T2-librarian-framework | T3-librarian-definitions |
| `T3-scope-setup-skill.md` | SetupScope skill, sane defaults | T2-substrate-architecture | T3-convention-base (phase 1) |
| `T3-install-skill-rewrite.md` | Install skills for v0.3 | T2-solo-plugin, T2-team-plugin, T2-team-admin-plugin | T3-scope-setup-skill, T3-install-librarian-skill |
| `T3-substrate-skill-rewrite.md` | substrate + wow + guides for v0.3 | T2-shared-skills-and-resources | T3-convention-base (phase 1) |

### Explicitly out of scope (M3 or later)

- **Custom librarian implementations** beyond the nightly index. Definitions and framework ship in M2; individual librarians are added incrementally.
- **Migration from v0.2.x.** Existing users with v0.2 substrates need a migration path. This depends on M2 being stable first.
- **Team-specific substrate patterns.** Shared/personal layer conventions for team substrates. Depends on M2's scope model being validated in solo first.

---

## Relationship to M2.1

M2.1 (ExFu Dashboard) is a parallel milestone that can begin once phase 1 is complete (the index exists). It delivers visual tools for substrate state, librarian health, and sane-default folder content. See `M2.1-exfu-dashboard.md`.

---

## Where this plan lives

- This file: `plugin/planning/M2-substrate-redesign.md`
- Design decisions: `plugin/planning/v0.3.0-reconciliation.md`
- M1 (what's been done): `plugin/planning/M1-plugin-foundation.md`
- Phase 1 domain: `plugin/planning/T2-substrate-architecture.md`
- Phase 2 domains: `plugin/planning/T2-librarian-framework.md`, `plugin/planning/T2-exfu-dashboard.md`
- Skills audit (feeds M3): `plugin/planning/audit-skills-and-resources.md`
