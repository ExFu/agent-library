# Substrate folder index

Auto-generated 2026-05-21 03:00:00 (machine local time). Do not edit by hand.

This is a folder-only map of the substrate. Files are not listed; for that, scan a folder directly. Each folder is annotated with its Purpose and a brief note on what it holds, drawn from the folder's own README.md.

---

## exfu/
**Why:** ExFu-delivered material, materialised at install. Holds the convention, ontology, librarian, principle, and recommendation atoms ExFu ships.
**Holds:** principles/, conventions/, ontologies/, librarians/, recommendations/, skills/, templates/.

### exfu/principles/
**Why:** Agent-runtime behavioural principles. Read by any agent that loads the substrate.
**Holds:** One atom per principle (golden-circle, outcome-framed-elicitation, concrete-first, ...).

### exfu/conventions/
**Why:** Named, atomic conventions for substrate shape and behaviour.
**Holds:** One subfolder per convention type, each containing the convention's agent.md template.

### exfu/ontologies/
**Why:** Definitions of folder types the substrate recognises.
**Holds:** One subfolder per type, each carrying schema, agent.md template, and (for user-facing types) elicitation prompt.

### exfu/librarians/
**Why:** Curation tasks the substrate runs on a schedule to keep itself tidy.
**Holds:** One subfolder per librarian, each with instructions for the daily orchestrator to follow.

### exfu/recommendations/
**Why:** Curated catalogue of third-party connectors, plugins, and skills the install agent surfaces in context.
**Holds:** One file per recommendation.

### exfu/skills/
**Why:** Skill-definitions ExFu ships (provider-agnostic, rendered into Claude or other target platforms).
**Holds:** One subfolder per skill definition. (Empty in this example.)

### exfu/templates/
**Why:** Templates the install agent fills in (wow, scope, etc.).
**Holds:** One template per file.

## user/
**Why:** The personal-tier scope. Holds anything specific to this user that isn't tied to a work area.
**Holds:** scope.md, context/me/, databases/, scratch/, todos/.

### user/context/
**Why:** Standing personal context. Identity-level material, read often, changes slowly.
**Holds:** me/ (about-me, role, preferences).

### user/context/me/
**Why:** Facts about this user that any agent should orient on.
**Holds:** about.md.

### user/databases/
**Why:** Personal structured records the user keeps in the substrate rather than in a SaaS tool.
**Holds:** (no databases yet in this example.)

### user/scratch/
**Why:** Ephemeral working space for personal in-progress material.
**Holds:** (empty in this example.)

### user/todos/
**Why:** Personal todos (cross-scope). User-tier instance of the todos ontology type.
**Holds:** agent.md (convention snapshot), todos.md.

## scopes/
**Why:** Container for all work-area scopes. Arbitrary grouping folders may nest underneath; leaves are scope folders identified by scope.md.
**Holds:** teams/ (one example grouping).

### scopes/teams/
**Why:** Grouping folder for team-related scopes.
**Holds:** sales/ (one example team grouping).

### scopes/teams/sales/
**Why:** Grouping folder for everything related to the Sales team.
**Holds:** team/ (the Sales team-as-scope), projects/ (sub-grouping for Sales projects).

### scopes/teams/sales/team/
**Why:** The Sales team's own scope. Standing context about the team itself.
**Holds:** scope.md, context/.

### scopes/teams/sales/team/context/
**Why:** Standing context for the Sales team.
**Holds:** team-members.md.

### scopes/teams/sales/projects/
**Why:** Sub-grouping folder for active Sales projects.
**Holds:** acme-q3-renewal/ (one example project scope).

### scopes/teams/sales/projects/acme-q3-renewal/
**Why:** Active project scope: Acme Corp's Q3 contract renewal.
**Holds:** scope.md, context/, todos/.

### scopes/teams/sales/projects/acme-q3-renewal/context/
**Why:** Standing context for the Acme Q3 renewal project.
**Holds:** acme-overview.md.

### scopes/teams/sales/projects/acme-q3-renewal/todos/
**Why:** Project todos for the Acme Q3 renewal.
**Holds:** agent.md (convention snapshot), todos.md.

---

*This index is normally regenerated nightly by the `substrate-index` librarian at `exfu/librarians/substrate-index/`. The content above is what a fresh run would produce against this example substrate.*
