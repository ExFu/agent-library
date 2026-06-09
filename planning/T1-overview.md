# T1 — Overview

The shared anchor for everyone working on any part of this plan. Keeps us aligned on Why, How, and What at the project level, and lays out the parallelisable workstreams that become T2 plans.

---

## Why

People doing knowledge work are increasingly relying on Claude as a working collaborator, not a chatbot. To make that real — persistent memory, real context, access to their tools, a way of working they can grow themselves — they need an installed setup. The current ExFu install delivers that one-to-one in a guided session, with the install agent fetching and packaging skills on the fly from `exfu.ai/clients/`.

That model breaks in two cases that are starting to matter:

- **Corporate networks** that block outbound fetches to arbitrary URLs. The install agent can't reach the source files, the install fails. Many of the people ExFu most wants to reach work in exactly these environments.
- **Teams** trying to operate together with shared substrate elements. Cloud-drive-based sharing is unreliable; the conversation around team install is also genuinely different from a personal install (IT restrictions, role-in-org capture, shared git repo, distribution to colleagues).

We're building three plugins to solve both:

- A **solo plugin** for individual users (founders, senior operators, solo professionals).
- A **team-admin plugin** for substrate champions inside a team — the people setting up the team's shared substrate, designing shared conventions, briefing IT/security, onboarding colleagues.
- A **team plugin** for everyone else on the team — joiners who connect to an existing team substrate, install their personal layer on top, and read/write the shared layer through it.

Each ships as a single installable bundle, working entirely from local content once installed. Distribution becomes one download, not many fetches.

The admin/member split is a hard separation, not a conversation branch. Some organisations will not want all team members to have the admin tooling at all — repo provisioning, compliance briefing, ability to write the team's shared skills folder. Splitting at the plugin boundary makes the access control explicit: you don't have admin capability if you don't have the admin plugin installed. This protects against accidental privilege escalation in conversation and keeps the member install lean.

The transformation we're delivering doesn't change. Users walk away with a working setup *and* the confidence to extend it themselves. The chief-of-staff framing remains the mental-model unlock. Build-by-doing remains the install discipline. What changes is the delivery mechanism and the team-aware variant.

---

## How

### Principles

- **Three plugins, fully separate.** Solo, team-admin, and team diverge in too many ways (storage architecture, install conversation shape, governance, role concepts, capability boundaries) to force unification. Each plugin is its own product, independently versioned, independently downloaded. Team-admin is a strict superset of team in capability, but the split is enforced at the plugin boundary so capability cannot leak to users who shouldn't have it.
- **Concrete-first, abstract-later.** The install conversation builds the substrate as a byproduct of useful conversation moves. The plugin doesn't change this; if anything it lets the conversation focus more on the moves and less on the plumbing.
- **Trust the agent.** Plugin content is rich context plus hard constraints, not procedural scripts. Install agents are Claude; treat them accordingly.
- **Plain language with users.** Internal vocabulary (substrate, scope, JTBD, discoverability asymmetry) stays internal. User-facing language uses the parts (knowledge base, skills, tools, things on a timer) and the chief-of-staff framing.
- **Ecosystem-aware.** ExFu is a guide through current best practice, not the unique source of insight. Reference Anthropic's own resources, well-respected community skills (superpowers, oh-my-claude), and teach the deep-research-as-a-move pattern so users don't depend on the plugin for current best practice.
- **Local-first.** Both plugins assume local-controlled data flow once installed. Nothing phones home to ExFu. This matters for compliance and for autonomy.

### Architectural shape

Each plugin contains:

- A small set of **entrypoint skills** that the user (or their Claude) loads to start the install or guidance flow.
  - `exfu` — orchestrator, triages user need.
  - `exfu:install-solo` (solo plugin), `exfu:install-team-admin` (team-admin plugin), or `exfu:install-team` (team plugin) — the install conversation, one per plugin.
  - `exfu:guides` — reference and teaching material.
  - `exfu:create-wow` — generates the user's personal `wow` from the template.
- The **bedrock skills** ported from `public/clients/` (`skill-packaging`, `box-filesystem` for solo or `git-substrate-sync` for both team variants, `substrate`, etc.).
- The **optional skills** users adopt à la carte (`reminders`, `inbox`, `writing-styles`, `scope-skills` template).
- The **scheduled tasks** (`daily-briefing`, cleanup, plus team-variant-specific tasks like git-sync nudges).
- The **resources** — substrate guide, primer, diagrams, templates, ecosystem reference catalogue.

All three plugins share most components; the differences are in the install entrypoint, the storage skill, and variant-specific additions. Team-admin additionally ships admin-only skills (`team-repo-provisioning`, `team-shared-skills-authoring`, `team-onboard-member`) and the compliance briefing resource. The team plugin ships none of those.

### Trade-offs being made

- **Bundle vs fetch.** Bundling everything makes the plugin self-contained but means updates require a new plugin install. Fetching keeps content fresh but breaks in restricted networks. We pick bundle. Updates land via plugin version bumps.
- **Plugin count.** One plugin would simplify maintenance but force compromises in the install conversation and break the admin/member capability boundary. Two plugins (solo + unified team) handles solo cleanly but still forces a runtime conversation branch that some organisations cannot tolerate. Three plugins (solo + team-admin + team) triples maintenance but each one is clean and the access boundary is enforced by what's installed rather than what the agent decides at runtime. We pick three. Shared content (most of the plugin in each case) lives in a single source folder and is composed into each variant at build time, which keeps the maintenance multiplier well below 3x.
- **Box (solo) vs git (team-admin and team).** Different mechanisms for different needs. Box keeps solo familiar despite known offline-caching issues; git gives teams reliable propagation and history. The cost is two storage skills to maintain. The benefit is each plugin's flow makes sense for its users. Team-admin and team share the git skill — the difference between them is what each can *do* against the repo, not how they connect to it.
- **Trust agent vs prescribe procedure.** We pick trust the agent — rich context plus hard constraints. Cost: occasional install variance. Benefit: agent-felt-dumb installs go away, the discipline scales as Claude improves.

### Dependencies and cross-cuts

These are settled (or getting settled) as cross-cut concerns before T2 starts:

- **Planning approach** (`cross-cut-planning-approach.md`) — golden-circle, three-tier, side-quests welcome, deep-research at decision points.
- **Brand voice** (`cross-cut-brand-voice.md`) — direct, warm, banlist of AI-slop patterns.
- **Teaching artefacts** (`cross-cut-teaching-artefacts.md`) — extensible catalogue, multiple diagrams to come.
- **Storage architecture** (`cross-cut-storage-architecture.md`) — Box for solo v1 with caveats and a research task; git for teams.
- **Plugin distribution** (`cross-cut-plugin-distribution.md`) — Anthropic plugin format, download from `exfu.ai`, semver, manual updates v1.
- **Compliance** (`cross-cut-compliance.md`) — ISO 27001-friendly defaults; team plugin ships a compliance briefing.
- **Ecosystem references** (`cross-cut-ecosystem-references.md`) — curated catalogue plus deep-research-as-a-move pattern.
- **Future explorations** (`cross-cut-future-explorations.md`) — graph/obsidian, custom hosted agents, multi-substrate, etc.

### Approach to teaching content

Teaching artefacts (diagrams, live HTML widgets, worked examples) are a first-class deliverable, not decoration. The install conversation reaches for them at calibration moments. The catalogue is extensible; we ship more as the conversation surfaces a need.

Initial teaching artefacts known to be needed:

- Substrate overview (exists, refresh inside the plugin).
- Agent typology (chat / cowork / coding / custom hosted) — to calibrate users on the lay of the land and where ExFu fits.
- Personal vs team skills and instructions — for the team plugin.
- Admin plane vs user domain — for the team plugin.
- Seniority and trust roles — for the team plugin.

---

## What — candidate T2 workstreams

These are the parallelisable workstreams. Each gets its own T2 plan. Names are working titles.

1. **`T2-solo-plugin.md`** — design and content of the solo plugin: install-solo entrypoint, bedrock and optional skills, scheduled tasks, resources, the install conversation shape. Storage assumed Box-with-caveats per cross-cut.

2. **`T2-team-admin-plugin.md`** — design and content of the team-admin plugin: install-team-admin entrypoint, repo provisioning, shared-skills authoring, team-onboarding helper, the compliance briefing resource, the admin-specific install conversation shape. Bundles the git-sync skill (shared with the team plugin).

3. **`T2-team-plugin.md`** — design and content of the team plugin: install-team entrypoint, joiner-flavoured install conversation, personal-layer-on-top-of-team substrate setup, git-sync skill (shared). No admin tooling, no repo provisioning, no IT briefing. Strict subset of team-admin's capability surface.

4. **`T2-shared-skills-and-resources.md`** — the components all three plugins use (orchestrator skill, guides skill, create-wow, the bedrock skills minus storage, the optional skills, the substrate guide and primer, ecosystem reference catalogue). Single source of truth, composed into each plugin build.

5. **`T2-teaching-artefacts.md`** — production of diagrams and live HTML widgets, the catalogue mechanism, source attribution. Serves all three plugins; some artefacts are admin-only.

6. **`T2-build-and-distribution.md`** — the build pipeline (source → plugin file), the download page on `exfu.ai`, versioning, update notification, archives. Now produces three plugin files.

7. **`T2-website-changes.md`** — the new download/install page (now offering three plugins), retiring the old `public/clients/*` URLs (or redirecting them), any marketing copy.

8. **`T2-substrate-architecture.md`** — the structural model of the substrate itself: scopes, folder-type catalogue, convention management (reference+delta), versioning, ontology model, discovery, the global index. Added for v0.3.0; this is the domain that defines what agents build into and navigate through.

9. **`T2-librarian-framework.md`** — the librarian lifecycle: structured definition format (YAML frontmatter), cadence-based grouping (nightly/weekly/hourly/on-demand), the registry (`exfu/derived/librarian-registry.json`), the runner that executes registered librarians in dependency order, the run log, health tracking, scope-level librarians. Covers install-librarian skill, nightly runner, and librarian definition standards.

10. **`T2-exfu-dashboard.md`** — a unified ExFu dashboard generated as static HTML into `exfu/derived/dashboard/`. Three views: substrate map (conceptual relationships, not filesystem), librarian dashboard (status, run history, health), and workspace views (todo, reminders, inbox aggregated across scopes). Generated by a dashboard-generator librarian. Sequenced as milestone M2.1 running parallel to M2 phase 2.

Cross-cuts (already in flight) are not T2 workstreams; they're dependencies. New cross-cuts can emerge as T2 work surfaces them.

### Work shape

T2 work can run in parallel across these workstreams once cross-cuts are firm enough not to block them. T3 plans drop out of T2 when the workstream is detailed enough that an implementation agent can act.

We're not writing code in this planning round, so deep-research can wait. When implementation begins, deep-research becomes a routine move at architectural decisions.

---

## Open questions at the T1 level

- **Plugin distribution: marketplace vs direct download.** Need to confirm whether Anthropic operates a third-party plugin marketplace and what listing requires. If yes, that becomes the primary channel. If no, direct download from `exfu.ai` is the channel. Either way the plugin file is the artefact. Research file pending.
- **Solo storage post-Box.** Box stays for v1 but the offline-caching issue is real. The cross-cut has the alternatives to evaluate. A research file should track findings as solo users hit the caching pain in the wild.
- **Migration path for existing ExFu installs.** Users currently set up via the fetch model will need a migration story when they want to move to the plugin. Probably a small one-time skill that surfaces in the plugin's first-run experience: "if you have an existing ExFu install, here's how to bring it forward". T2 of solo and the team variants should each address this.
- **Team-admin and team plugin coexistence.** A user may install the team plugin to join a team, then later become its substrate champion and need team-admin. Probably the team-admin install detects existing team-plugin install and offers an in-place upgrade (replacing the team plugin with team-admin, preserving personal substrate). Worth designing in T2 of team-admin.
- **What if the wrong plugin is installed?** A user installs team-admin who shouldn't have it (intent or accident). The plugin can't enforce org policy on its own — that's the org's distribution control problem (e.g. only the substrate champion is given the team-admin download URL). The plugin can be polite about it on first run ("this is the admin plugin — designed for the substrate champion of your team. If that's not you, install the team plugin instead.").

---

## Where this plan lives

- This file: `plugin/planning/T1-overview.md` -- the durable anchor.
- Cross-cuts: flat, prefixed `cross-cut-...` in the same folder.
- T2 plans: flat, prefixed `T2-...`, one per workstream (domain-oriented).
- Milestones: flat, prefixed `M<n>-...`, one per sequenced delivery goal. T2s describe areas of work; milestones describe what ships and when. See `cross-cut-planning-approach.md` for the full concept.
- T3 plans: flat, prefixed `T3-...`, one per implementation topic. Parented by both a T2 (domain context) and an Mn (sequencing context).
- v0.3.0 design decisions: `v0.3.0-reconciliation.md` is the definitive reference. Supersedes both `v0.3.0pre-direction.md` and `v0.3.0-substrate-revision.md`.
- Research notes: `plugin/planning/research/`, one file per topic.
- Side-quests, reviews, ad-hoc explorations: flat, prefixed `side-quest-...` or `review-...` so they self-organise visually.
- Plugin source: `plugin/src/` -- populated when T2/T3 are firm and implementation begins.
- Built plugin: copied to `public/` for distribution.
