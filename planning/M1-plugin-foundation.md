# M1 -- Plugin foundation (retrospective)

This is a backwards-looking milestone capturing what was delivered from project inception through v0.2.8, plus the design work that set up v0.3.0. Written after the fact so future agents understand the project's history and current state without rediscovering it.

**Status:** complete. Everything described here is shipped or committed.

---

## Why

ExFu's original delivery model -- a guided install conversation that fetches skills from `exfu.ai/clients/` URLs at runtime -- breaks on corporate networks and can't support teams sharing a substrate. The plugin model fixes both: everything ships bundled, works local-first, nothing phones home.

This milestone's audience was Al (sole builder) and the install agents that run inside the plugins. Its purpose was to prove the plugin model works end-to-end: build system, three variant plugins, working installs, distribution via the website.

## How

Rapid iteration over three days (May 5-7, 2026), working from a full planning corpus (T1 overview, seven T2 workstreams, eight cross-cuts). Design docs written first, implementation followed. The build system was built early so every change could be tested as a real plugin install.

After v0.2.8 shipped, two separate design sessions explored the v0.3.0 substrate redesign (May 21 and June 9). These produced divergent designs that were reconciled on June 9 into a unified set of resolved decisions.

## What was delivered

### Three plugins (v0.2.0 through v0.2.8)

- **exfu-solo** -- individuals, Box storage default
- **exfu-team** -- team joiners, git storage, two-layer (personal + shared)
- **exfu-team-admin** -- substrate champions, strict superset of team with provisioning and compliance tooling

Admin/member split enforced at the plugin boundary, not a runtime conversation branch.

### Build system

`plugin/build/build.sh <variant|all> [--dist]` composes shared + variant source into built plugins. `--dist` writes versioned zips to `public/downloads/` for the website to serve. No dependencies beyond bash, cp, find, zip, and jq or python3.

### Shared skills and resources

18 skills audited (see `audit-skills-and-resources.md`): substrate (boot sequence), exfu-start (front door), install variants, box-filesystem-management, git-substrate-sync, setup-inbox, setup-reminders, setup-writing-styles, exfu-create-wow, skill-packaging, exfu-guides, exfu-migrate-from-fetch-model. Plus admin-only skills for team-admin.

Scheduled tasks: daily-briefing, substrate-index (nightly folder map), box-cleanup.

Resources: substrate guide, primer, diagrams (warm earth-tone infographics), templates, ecosystem reference catalogue.

### Website

Download/install page serving three plugin variants. Astro 6.1.4, TypeScript strict, Netlify, Plausible analytics.

### v0.2.0 substrate structure

Top-level: orgs/, teams/, personal folders. Two-layer PII model (Layer 1 file-based/auditable, Layer 2 PII runtime-only). CLAUDE.md guard file preventing mounting without the substrate skill. This structure is what v0.3.0 replaces.

### v0.3.0 design work

Three design artifacts produced across two sessions:

1. **v0.3.0pre-direction.md** (May 21) -- full direction doc with five T2 workstreams, 13 open questions, convention-snapshot model, scopes-as-leaves, rich scope.md
2. **v0.3.0-substrate-revision.md** (June 9) -- fresh design doc with uniform scopes, thin pointers, recursive nesting, minimal scope.md
3. **plugin/example/** (May 21) -- ~50-file worked prototype following the pre-direction model

These diverged on five structural points. The **v0.3.0-reconciliation.md** (June 9) audits the divergences and records how each was resolved. The reconciliation is the definitive v0.3.0 reference -- not either design doc alone.

### Skills audit

`audit-skills-and-resources.md` (May 21) -- audited all 18 skills. Found 2 critical descriptions, 11 needing work, 5 good. Key findings: insider-vocabulary triggers, missing Why in descriptions, bodies leading with constraints not rationale.

---

## What carries forward

- The **planning corpus** (T1, T2s, cross-cuts) remains valid for domain context. Milestones now handle sequencing.
- The **build system** works and will be extended for v0.3.0's versioned exfu/ structure.
- The **skills audit** identifies what needs fixing and feeds directly into M2 work.
- The **reconciliation audit** is the starting point for M2 -- all structural decisions are resolved.
- The **example prototype** needs rebuilding to match the resolved v0.3.0 decisions.

---

## Where this plan lives

- This file: `plugin/planning/M1-plugin-foundation.md`
- T1 overview: `plugin/planning/T1-overview.md`
- Reconciliation (v0.3.0 decisions): `plugin/planning/v0.3.0-reconciliation.md`
- Skills audit: `plugin/planning/audit-skills-and-resources.md`
