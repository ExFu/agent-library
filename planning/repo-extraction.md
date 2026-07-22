# repo-extraction -- standalone exfu_plugin repo and marketplace

**Status:** Adopted (approved by Al in plan mode, 2026-07-22). Repo-side landed
(genesis + marketplace commits); website-side removal branch merge-gated on Al.

Anchor for the extraction of the plugin sub-project out of `exfu_website` into
this standalone repo. Full plan reviewed and approved in-session; this document
records the operative decisions so the repo self-orients.

## Why

The plugin ecosystem outgrew its sub-project status: it versions independently
of the website, its planning corpus dominates the shared APV log's plugin
strand, and distribution wants to be a proper Claude plugin marketplace rather
than hand-published zips. A standalone repo also dogfoods APV project
attachment on a fresh repo.

## How (the four decisions, Al's rulings 2026-07-22)

1. **History: git subtree split.** The new repo carries only the ~44 commits
   that touched `plugin/` (42 of 43 pre-split commits were pure), with the old
   `plugin/` contents at root. SHAs are rewritten; nothing validates them. The
   website repo keeps the full interleaved history as archive.
2. **APV: fresh init + carry-forward.** New empty log via `apv init`; the
   still-open plugin-strand entities are re-established here with provenance
   attributes naming the source repo and log. Historic plugin events remain in
   the website log. The website log gets a closing decision recording the split.
3. **Distribution: proper Claude marketplace.** Root
   `.claude-plugin/marketplace.json` (name `exfu`), composed plugin dirs
   committed under `plugins/`, installable by directory path now and by repo
   slug once a remote exists. `build.sh --dist` keeps producing zips (now into
   gitignored `dist/`) for the website download flow.
4. **Remote: local only for now.** No GitHub repo created as part of the
   extraction.

## What

- Phase 1: subtree split -> `/Users/al/Studio/projects/exfu_plugin`, verified
  by tree diff against the source repo's `plugin/` (tracked content identical).
- Phase 2: `apv init --at=all --accept-claude-md`, plugin enablement in
  `.claude/settings.json`, carry-forward capture (this block).
- Phase 3: cleanup commit (this one) + marketplace commit (marketplace.json,
  build.sh retarget to `plugins/` and `dist/`, composed output committed).
- Phase 4 (website repo): `git rm -r plugin` on a branch, closing capture,
  merge to main only on Al's explicit go-ahead. Install page and published
  zips deliberately untouched.

## Carried-forward entities

- `proposal-multi-provider` (plan, draft) with its operator ruling
- `v0.5-dashboard-action-basket` (plan, live; v0.5.0 shipped, release/publish
  tail still open)
- Inbox items: `2026-07-20.team-plugin-rot-audit`,
  `2026-07-20.dashboard-improvement-shortlist`,
  `2026-07-20.account-side-migration-checklist`,
  `2026-07-21.stray-scope-md-at-scopes-root`
