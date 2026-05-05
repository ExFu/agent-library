# T2 — Shared skills and resources

The foundation all three plugins build on. Most of what ships in any plugin is the same content; the divergent parts (storage skill, install entrypoint, team-admin-specific resources) are handled in their own T2s.

Anchors back to: `T1-overview.md`, `cross-cut-storage-architecture.md`, `cross-cut-brand-voice.md`, `cross-cut-teaching-artefacts.md`, `cross-cut-ecosystem-references.md`.

---

## Why

All three plugins do most of the same things. They all need an orchestrator skill that triages user need. They all ship the bedrock skills that let Claude work with the user's setup. They all ship the optional skills (`reminders`, `inbox`, `writing-styles`) that users adopt à la carte. They all ship the substrate guide, the substrate primer, the teaching-artefacts catalogue, the ecosystem reference catalogue. They all produce a personal `wow` for the user.

If we duplicate this content into each plugin's source folder we double the maintenance burden and guarantee drift. If we share it cleanly we maintain one source of truth and let each plugin's build pull from it. This T2 designs that shared layer.

---

## How

### What is shared, what isn't

**Shared (this T2 covers):**
- `exfu` (orchestrator skill — triages and routes)
- `exfu:guides` (surfaces reference material)
- `exfu:create-wow` (generates the user's personal `wow` from a template)
- `skill-packaging` (utility for the user's own custom skill development)
- `substrate` (boot skill — orients Claude at session start)
- `reminders` (optional)
- `inbox` (optional)
- `writing-styles` (optional)
- `scope-skills` template (used by either plugin's install conversation when scopes are created)
- `daily-briefing` scheduled task (with hooks all three plugins can extend)
- `wow` template
- Substrate guide (`substrate-guide.md`)
- Substrate primer (`the-substrate-primer.md`)
- ExFu primer (`exfu-primer.md`)
- Teaching-artefacts catalogue (the index + the substrate diagram + future shared diagrams)
- Ecosystem reference catalogue
- Brand-voice guidance (the `writing-styles` anti-slop layer carries the rules)

**Not shared (handled in solo / team / team-admin T2s):**
- The storage skill (`box-filesystem-management` for solo, `git-substrate-sync` for team and team-admin)
- The storage-related scheduled tasks (`box-cleanup` for solo)
- The install entrypoint skill (`exfu:install-solo`, `exfu:install-team`, `exfu:install-team-admin`)
- Team-admin-only resources (compliance briefing, admin-vs-user diagrams, seniority diagrams, role-capture templates)

Note: `git-substrate-sync` is shared between the team and team-admin plugins. One source file (`plugin/src/team/skills/git-substrate-sync/`) is bundled into both at build time.

### Source-of-truth structure

A `shared/` folder under `plugin/src/` holds the canonical version of every shared component. Each plugin's source folder contains only its plugin-specific content. The build pipeline assembles each plugin from `shared/` + the plugin's specific folder.

Proposed layout:

```
plugin/src/
  shared/
    skills/
      exfu/SKILL.md
      exfu_guides/SKILL.md
      exfu_create-wow/SKILL.md
      skill-packaging/SKILL.md
      substrate/SKILL.md
      reminders/SKILL.md
      inbox/SKILL.md
      writing-styles/SKILL.md
    scheduled-tasks/
      daily-briefing/TASK.md
    templates/
      wow-template.md
      scope-skill-template.md
    resources/
      substrate-guide.md
      the-substrate-primer.md
      exfu-primer.md
      ecosystem-references.md
      teaching-artefacts.md
      diagrams/
        substrate-diagram.png
      widgets/
        (none yet)
  solo/
    skills/
      exfu_install-solo/SKILL.md
      box-filesystem-management/SKILL.md
    scheduled-tasks/
      box-cleanup/
        TASK.md
        cleanup.py
    manifest.json
  team/
    skills/
      exfu_install-team/SKILL.md
      git-substrate-sync/SKILL.md
    resources/
      diagrams/
        personal-vs-team-skills.png
    manifest.json
  team-admin/
    skills/
      exfu_install-team-admin/SKILL.md
      team-repo-provisioning/SKILL.md
      team-shared-skills-authoring/SKILL.md
      team-onboard-member/SKILL.md
    resources/
      compliance-briefing.md
      diagrams/
        admin-plane-vs-user-domain.png
        seniority-and-trust-roles.png
    manifest.json
```

The build pipeline (T2-build-and-distribution) is what knows how to combine `shared/` with `solo/`, `team/`, or `team-admin/` to produce a plugin file. For team-admin, the build also pulls `git-substrate-sync` from the `team/` source folder.

### Approach to porting from current `public/clients/`

Most of these skills exist already at `public/clients/<name>/SKILL.md`. The work is mostly:

1. **Move** to `plugin/src/shared/` (or `plugin/src/solo/`, `plugin/src/team/` for the divergent ones).
2. **Refresh** descriptions where the new orchestrator's triage logic depends on them.
3. **Remove fetch-from-URL behaviour** that assumed the install agent could reach `exfu.ai/clients/`. In a plugin world the skills are pre-installed; instructions reference local paths or the plugin's resource folder.
4. **Reframe** install instructions inside the install entrypoint skills (handled in solo/team T2s) so that "package this skill and present to user" becomes "this skill is already available, here's how to enable/configure it for your setup".

The substrate guide, the primer, and the ExFu primer largely move as-is, possibly with light edits to remove references to the old fetch model.

### Three skills that don't exist yet

- **`exfu` (orchestrator).** Front-door skill. Triggers on phrases like "exfu", "install", "set up my Claude", "start my ExFu setup". Body of the skill: ask the user briefly what they're here for (install, getting reference material, picking up where they left off), route to the right sub-skill, or just answer their question if it's small enough.
- **`exfu:guides`.** Loads on "how does X work", "explain X", "what is the substrate", and similar — *if* the user has gone deep enough that the install conversation should hand off to reference. Surfaces relevant content from the substrate guide, primer, ecosystem catalogue, or teaching artefacts catalogue.
- **`exfu:create-wow`.** Pulls the wow template, customises it lightly with what's known about the user (their about-me content from `context/me/`, any preferences they've stated, the navigation map for their substrate as it stands), packages it, presents to the user for install. Invoked by install-solo, install-team, and install-team-admin during the install flow; can also be invoked later if the user wants a substantial wow regeneration.

These three are net-new design work. The rest is porting and refining.

### Decision: how skills reference content

Skills currently reference content via URLs (`https://exfu.ai/clients/...`). Inside the plugin those URLs don't exist. Options:

- **Local paths**, e.g. `<plugin-root>/resources/substrate-guide.md`. Cleanest for plugin-only content. Requires the skill to know its own plugin-relative path.
- **Pre-resolved**, where the install entrypoint loads the relevant content into the conversation context up front, and downstream skills don't need to fetch.
- **Hybrid**, where small things are inline in the skill body and large reference content is pointed at by a local path.

Recommendation: local paths for resource files, inline for short reference, plus a small convention that any skill citing a local path uses a placeholder like `{{plugin_root}}/resources/...` that the install entrypoint resolves at runtime if the local path can't be discovered automatically.

This needs validation against Anthropic's plugin format conventions (research file pending) but the principle of "no external fetches once installed" is firm.

---

## What — components inventory and notes

### `exfu` (orchestrator skill)

**New design.** Description triggers on install/setup/exfu phrases. Body:
- Asks the user briefly: "What brings you in? Doing your initial setup, picking up where you left off, just want to read about how things work?"
- Routes:
  - "Initial setup" → loads `exfu:install-solo`, `exfu:install-team`, or `exfu:install-team-admin` (the orchestrator detects the plugin variant from whichever install skill is present).
  - "Pick up where I left off" → loads `substrate` (which orients to whatever's in the user's setup currently).
  - "Reference / how does X work" → loads `exfu:guides`.

Should be small. The orchestrator's job is routing, not doing the work itself.

### `exfu:guides`

**New design.** Description triggers on architecture-deep questions. Body: knows the index of reference content (substrate guide, primer, ExFu primer, ecosystem catalogue, teaching artefacts catalogue). Pulls the relevant section of the relevant document into the conversation, paraphrased for the question, with a pointer to the canonical source if the user wants depth.

### `exfu:create-wow`

**New design.** Description triggers when the install flow reaches the wow-creation moment, or when the user explicitly says "rebuild my wow / regenerate my way of working". Body:
- Reads the wow template from the plugin's `templates/` resources.
- Reads `context/me/about.md` (and other relevant `context/me/` files) for personal seeds.
- Reads the user's existing `wow` if there is one, and merges.
- Customises the template lightly with what's known.
- Uses `skill-packaging` to package and present to the user.

### `skill-packaging`

**Port from `public/clients/skill-packaging`.** Refresh: the skill is now pre-installed via plugin, so its description should make clear it's a utility for *creating new skills*, not for installing the bundled ones. Otherwise content stays.

### `substrate`

**Port from `public/clients/substrate`.** Refresh: where the current version says "fetch the substrate-guide from `exfu.ai`", change to "read the substrate-guide from your knowledge base's `context/ways-of-working/` folder, which the install set up for you, or from the plugin resources at `{{plugin_root}}/resources/substrate-guide.md` for definitions". The boot behaviour stays.

### `reminders`, `inbox`, `writing-styles`

**Port from `public/clients/`.** Refresh fetch-URL references. Otherwise content stays.

### `scope-skills` template

**Port.** Used by the install entrypoint skills when creating scopes during the install. The template itself doesn't change.

### `daily-briefing` scheduled task

**Port from `public/clients/daily-briefing`.** The task prompt is largely shared. The team plugin may want to add team-specific briefing content (e.g., shared scope updates, team-channel digests); the shared base supports that as an extension point rather than a different task.

### `wow` template

**Port from `public/clients/wow/SKILL.md` (template content).** This is the template `exfu:create-wow` reads. Lives in `templates/`, not `skills/`, because it's not itself an installable skill — it's the source for ones that get generated per-user.

### Substrate guide, primer, ExFu primer

**Port from `public/clients/ways-of-working/substrate-guide.md`, the substrate primer (currently in `outputs/`), and the ExFu primer (also in `outputs/`)**. Small refresh to remove fetch-model references. Substrate primer and ExFu primer move into the plugin source from outputs.

### Teaching-artefacts catalogue

**New file.** `resources/teaching-artefacts.md`. Index of available diagrams and widgets, what each teaches, when to surface, source attribution. Initial entry: the substrate diagram. Grows as new artefacts are added.

### Ecosystem references catalogue

**New file.** `resources/ecosystem-references.md`. Curated list of Anthropic and community resources (Claude 101, Cowork course, superpowers, oh-my-claude, etc.) plus the deep-research-as-a-move pattern. The `exfu:guides` skill reads from this.

### Brand-voice content

The voice rules already live in `writing-styles/SKILL.md`. The cross-cut document references them. No new component; just the shared skill carries them.

---

## T3 candidates

Each of these is a coherent unit of work that a Claude Code agent can execute against once T3 plans are written:

- `T3-orchestrator-skill.md` — design and write the `exfu` skill.
- `T3-guides-skill.md` — design and write the `exfu:guides` skill.
- `T3-create-wow-skill.md` — design and write the `exfu:create-wow` skill plus the wow template refinement.
- `T3-port-existing-skills.md` — bulk port of `skill-packaging`, `substrate`, `reminders`, `inbox`, `writing-styles`, `scope-skills` template into the new source tree, with the fetch-model refresh.
- `T3-shared-resources.md` — port of substrate guide, primers, plus authoring of teaching-artefacts catalogue and ecosystem-references catalogue.
- `T3-shared-scheduled-tasks.md` — daily-briefing port plus the extension-point design for team-specific briefing additions.
- `T3-skill-content-conventions.md` — the local-path-vs-URL convention for in-plugin resource references; finalise after research file on plugin format closes.

These can largely run in parallel once the plugin-format research is closed, with the convention work (`T3-skill-content-conventions.md`) ideally done first because the others assume it.

---

## Open questions

- **Triage in `exfu` orchestrator.** Should it ask the user explicitly ("what brings you in?"), or detect from context? Both work; explicit is more robust at the cost of a small added beat. Probably explicit at v1, refine later if it feels clunky.
- **`exfu:guides` granularity.** Does it surface whole reference docs, or paraphrased answers? Probably both, depending on the question — the skill body decides per-question. Worth a sketch.
- **Daily briefing extension hooks.** What's the cleanest way for the team plugin to add team-specific briefing items without forking the task? Probably the task body invites the install agent to add team-specific sections at install time, written into the user's task prompt rather than the shared template.
- **`exfu:create-wow` and substrate state.** When `create-wow` runs, what existing state does it read? About-me, role (if a team install captured it), tools.md, any earlier wow if present. Worth designing the read-set explicitly.
- **Plugin-format conventions.** Local paths, the `{{plugin_root}}` placeholder, manifest format — pending research, will inform the exact shape of `T3-skill-content-conventions.md`.
- **What happens if multiple plugins are installed?** Edge case but worth thinking about: a user who tries to install more than one. The orchestrator should detect and surface the conflict, recommend uninstalling the others. Team and team-admin cannot coexist. Flag for solo, team, and team-admin T2s to handle. Note: a user upgrading from team to team-admin should use the `exfu:upgrade-from-team-to-admin` skill, which handles the transition cleanly.
