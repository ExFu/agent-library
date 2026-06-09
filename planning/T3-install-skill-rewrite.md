# T3 -- Install skill rewrite

Rewrite all three install variant skills (solo, team, team-admin) for the v0.3 scope-based substrate model.

**Parents:** `T2-solo-plugin.md`, `T2-team-plugin.md`, `T2-team-admin-plugin.md` (domains), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-scope-setup-skill (scope creation is delegated to it), T3-install-librarian-skill (librarian registration during install)
**Status:** not started.

---

## Why

The three install skills (`exfu-install-solo`, `exfu-install-team`, `exfu-install-team-admin`) are the front door for every new user. They currently build a v0.2.x substrate: orgs/, teams/, README.md-based conventions, no scope.md, no convention base. Every structural assumption is wrong for v0.3.

The install conversation is the highest-impact rewrite in M2. Until it's done, no new user gets a v0.3 substrate.

---

## What to build

### 1. Shared install structure

All three variants share a core flow, with variant-specific branches:

```
1. First-run detection (existing substrate? migration needed?)
2. Storage setup (Box for solo, git for team variants)
3. Convention base deployment
   - Copy exfu/v0.3/ from plugin into substrate
   - Create exfu/latest.txt (and symlink where supported)
   - Create exfu/derived/
4. User scope creation (delegate to scope-setup skill)
   - About-me capture -> context/about-me.md
   - Ways-of-working capture -> ontology/ways-of-working.md
   - Optional folder-types (todo, reminders, inbox with sane defaults)
5. First working scope (delegate to scope-setup skill)
   - "What are you working on right now?"
   - Create one scope to demonstrate the pattern
6. Librarian registration (delegate to install-librarian skill)
   - Register nightly-index librarian
   - Register dashboard-generator librarian (when M2.1 ships)
7. WoW skill generation (delegate to exfu-create-wow)
8. Optional skills buffet (inbox, reminders, writing-styles)
9. Summary and next steps
```

### 2. Solo variant differences

- Storage: Box folder detection/creation, Box filesystem skill
- No shared layer; everything is personal
- Symlink fallback: always use latest.txt (Box may not support symlinks)

### 3. Team variant differences

- Storage: connect to existing git repo (URL from onboarding pack or user input)
- Pull shared layer, create personal layer on top
- Respect shared conventions already in the repo
- git-substrate-sync skill activation

### 4. Team-admin variant differences

- Storage: create new git repo OR connect to existing
- Shared layer authoring (conventions, shared skills)
- Team onboarding pack generation
- Compliance briefing resource
- All admin-only skills activated

### 5. Migration detection

When the install detects a v0.2.x substrate:
- Offer migration (separate skill, potentially T3-migration)
- Or fresh install alongside (v0.2 and v0.3 coexist briefly)
- Do not silently overwrite v0.2 content

### 6. Convention base deployment

The install copies the convention base from the plugin package:

```
${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/  ->  <substrate>/exfu/v0.3/
```

Creates:
- `exfu/latest.txt` with "v0.3"
- `exfu/latest` symlink (if supported)
- `exfu/derived/` directory

This is the step that makes scope creation possible: the convention base must exist before any scope can reference it.

---

## Acceptance criteria

1. Solo install creates a working v0.3 substrate with user/ scope and at least one working scope
2. Team install connects to a shared repo and creates a personal layer with v0.3 structure
3. Team-admin install creates a shared repo with v0.3 structure and admin tooling
4. Convention base is deployed correctly from plugin package
5. Nightly index librarian is registered during install
6. WoW skill is generated with v0.3-aware content
7. Migration from v0.2 is detected and handled (at minimum: warned, not destroyed)
8. A user completing the install has a substrate that matches the example prototype

---

## Files to modify

- `plugin/src/solo/skills/exfu-install-solo/SKILL.md` + content
- `plugin/src/team/skills/exfu-install-team/SKILL.md` + content
- `plugin/src/team-admin/skills/exfu-install-team-admin/SKILL.md` + content
- `plugin/src/shared/skills/exfu-start/SKILL.md` + content (routing logic)

---

## Where this plan lives

- This file: `plugin/planning/T3-install-skill-rewrite.md`
- Domains: `plugin/planning/T2-solo-plugin.md`, `plugin/planning/T2-team-plugin.md`, `plugin/planning/T2-team-admin-plugin.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
