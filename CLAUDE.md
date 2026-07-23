# ExFu Agent Library -- source for the ExFu Agent Library plugins, published via the public exfu marketplace

## Why this repo exists

The ExFu plugin ecosystem (three plugins installing an "Agent Library" run by
"Agent Librarians"; internal register: substrate) started life as the `plugin/`
sub-project inside the `exfu_website` repo. On 2026-07-22 it was extracted into
this standalone repo (git subtree split, plugin-only history preserved) so it
can evolve, version, and distribute independently. Public distribution runs
through a dedicated marketplace repo, `ExFu/claude-marketplace` (marketplace
name `exfu-agent-library`); this repo (`ExFu/agent-library`) is the plugin source it
publishes. The website repo keeps the full interleaved history as
archive; this repo's planning state was carried forward into a fresh APV log
(see the APV section below and `planning/repo-extraction.md`).

## What is here

- `src/` -- canonical, human-editable plugin source:
  - `src/shared/` -- content composed into every variant (skills, resources, templates, substrate conventions)
  - `src/solo/`, `src/team/`, `src/team-admin/` -- variant-specific content and `.claude-plugin/plugin.json` manifests
- `build/build.sh` -- composes `src/shared/` + `src/<variant>/` into installable plugin dirs
- `plugins/` -- the composed, committed build output; these are the marketplace's plugin sources
- Public distribution runs through the separate **`ExFu/claude-marketplace`** repo
  (marketplace name `exfu-agent-library`), which carries the marketplace manifest and points its
  entries at this repo's `plugins/`. It is the primary install channel for both Claude Code
  and Cowork: `/plugin marketplace add ExFu/claude-marketplace` then
  `/plugin install exfu-agent-library-solo@exfu-agent-library`. This repo does not ship or
  expose a marketplace manifest of its own; distribution is entirely the dedicated
  marketplace repo's concern, and `build.sh` performs no marketplace sync.
- `dist/` -- gitignored versioned zips (`build.sh --dist`) for the website download flow
- `example/` -- a worked example Agent Library used by docs and the dashboard generator
- `planning/` -- the planning corpus (APV-tracked; plain markdown, entity id = filename stem)

## Editing rules

- Edit `src/`, never `plugins/` -- `plugins/` is generated. After changing `src/`,
  run `./build/build.sh all` and commit the regenerated `plugins/` alongside.
- Version bumps touch: the three `src/*/.claude-plugin/plugin.json` manifests and
  `src/shared/resources/CHANGELOG.md`. The marketplace entries live in the separate
  `ExFu/claude-marketplace` repo and are bumped there.
- Sticky-note / product copy: inner monologue tone, never feature specs; no em-dashes.

## Relationship to exfu_website

The website (`/Users/al/Studio/projects/exfu_website`) serves the public install
page and the published download zips in `public/downloads/`. Publishing a release
to the website is a manual step (copy zips from `dist/`, update the install page
versions). The public `ExFu/claude-marketplace` repo is the primary
distribution channel (this repo is the source it publishes from).

<!-- apv:orientation -->
## agent-plan-visualiser (APV) tracking

This repository is tracked by agent-plan-visualiser. The append-only event
log at `.apv/events.jsonl` is the source of truth for planning state;
plans and status prose are secondary. After each logical unit of work and
**before committing**, run /apv-capture to append a sealed event block —
the pre-commit guard rejects uncaptured commits (`git commit --no-verify`
is the sanctioned hatch for capture-free trivia). Land branches on main via
/apv-merge; the gate hooks refuse a main that fails the integrity check.

Skills are plugin-namespaced: /apv-capture may be listed as
`agent-plan-visualiser:apv-capture`. If NEITHER form is available, this
session did not load the plugin (typical in worktree checkouts that lack
`.claude/settings.json`) — read the skill source directly and follow it:
the newest `~/.claude/plugins/cache/*/agent-plan-visualiser/*/skills/apv-capture/SKILL.md`
(same pattern for apv-merge and using-agent-plan-visualiser).
