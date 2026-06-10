# Overnight handover: claude-exfu substrate build

2026-06-10, overnight session. Status: substrate built and tested; recipes below need you to execute them. Nothing committed, nothing installed, old vault untouched.

## What exists now

**`Box-Box/claude-exfu/`** is a live v0.3 substrate root, populated from the old `claude` vault (which was not modified in any way and remains the fallback):

- 11 scopes: `user/` (Alastair) plus Work, Swoop, ZapMap (under a `clients/` grouping folder), Lope, LinkedIn (nested in Lope), ExFu, Prompt Loom, Germany Trip, Sailing, MX5 Hunt.
- Convention base `exfu/v0.3/` deployed, `latest.txt` pointer, root `CLAUDE.md` guard.
- All todo folders are ClickUp pointers. Work scope carries the people/opportunities CRM (filenames kept verbatim so `[[Name]]` wikilinks resolve) with new `schema.md` files. Compliance calendar lives in `scopes/work/reminders/`.
- New ontologies: `user/ontology/ways-of-working.md`, `user/ontology/personal-logs.md`, `scopes/work/ontology/crm-vocabulary.md`.
- MX5 scanner rebuilt as a librarian at `scopes/mx5-hunt/librarians/mx5-scanner.md` (+ procedure file). **Left unregistered** pending your confirmation the hunt is still live.
- Full old-to-new mapping and known rough edges: `claude-exfu/user/docs/migration-from-claude-vault.md`.
- Two inbox items await decisions: old skill drafts, and a stale-reminders review.

**Tested end to end:** `index.py` (11 scopes indexed), `librarians.py due/record`, `dashboard-generator.py` all ran clean against the real substrate. The nightly trio (nightly-index, inbox-triage, dashboard-generator) is registered and has one successful run each; registry and log are live in `exfu/derived/`. Dashboard at `exfu/derived/dashboard/index.html`.

## Recipes for you to execute

### 1. Install your wow skill

Source written at `claude-exfu/user/skills/wow/SKILL.md` (navigation map for the new substrate + your always-on kernel).

In a Claude session with the plugin skills available: "Package `user/skills/wow/SKILL.md` from my substrate with skill-packaging", install the resulting `.skill` via the UI, then add `wow` to Global Instructions so it loads every session.

### 2. Create the nightly-librarians scheduled task

Claude Desktop > Cowork > Scheduled > + New task, Daily 03:00. Paste this (paths already filled in; they point at the repo checkout since the plugin isn't marketplace-installed):

> You are the nightly librarian session for the ExFu substrate at /Users/al/Library/CloudStorage/Box-Box/claude-exfu.
>
> Librarians are maintenance jobs defined as agent instructions. You are the agent: you read each due librarian's definition and carry out its instructions yourself. Where a definition tells you to run a script, that script is a tool -- run it, check the result, and apply judgment to what comes back.
>
> 1. Find out what is due:
>
> python3 /Users/al/Studio/projects/exfu_website/plugin/src/shared/scheduled-tasks/nightly-librarians/librarians.py due /Users/al/Library/CloudStorage/Box-Box/claude-exfu nightly
>
> 2. For each librarian listed, in the order given: read its definition file (the definition: path in the output; the body below the frontmatter is your instructions), do the work it describes, then record the outcome before moving on:
>
> python3 /Users/al/Studio/projects/exfu_website/plugin/src/shared/scheduled-tasks/nightly-librarians/librarians.py record /Users/al/Library/CloudStorage/Box-Box/claude-exfu <name> --status success|failure|skipped --detail "one line of what happened"
>
> Note: where a definition references a script via ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/..., resolve that to /Users/al/Studio/projects/exfu_website/plugin/src/shared/scheduled-tasks/.
>
> 3. If a librarian fails: record the failure with what went wrong, record anything that depends on it as skipped, and continue with the independent ones. Do not try to repair a failing librarian.
>
> 4. Finish with a short summary: what ran, what changed, and anything that needs my attention.
>
> Write only inside /Users/al/Library/CloudStorage/Box-Box/claude-exfu. Treat the scripts as read-and-execute tools.

Caveat: these paths assume the worktree branch is merged to the main checkout (the scripts also exist unmerged-identical there already at 6e918eb, so the task works immediately).

### 3. Decisions waiting on you

- **MX5 scanner**: still hunting? If yes, say "install the mx5-scanner librarian" in a substrate-aware session (the install-librarian skill handles registration). If no, delete `scopes/mx5-hunt/librarians/` contents or the whole scope.
- **Inbox items** in `claude-exfu/user/inbox/`: old vault skill drafts (regenerate vs fold vs drop) and the stale reminders review.
- **Cutover**: once you're happy, the old `claude` vault should stop being the live target (point Obsidian and any old skills at `claude-exfu`, or archive the old vault). Until then both exist; nothing breaks.

### 4. Optional buffet (when ready)

`setup-reminders`, `setup-inbox`, `setup-writing-styles` skills can generate your personal `alastair-*` always-on skills against the new substrate; the wow skill's bootstrap section has slots for them.

## Repo work done alongside (uncommitted, this worktree)

- Team + team-admin install skill rewrites for v0.3: see git diff (`plugin/src/team/skills/exfu-install-team/SKILL.md`, `plugin/src/team-admin/skills/exfu-install-team-admin/SKILL.md`). Both follow the rewritten solo skill's structure: migration check, diagrams, storage paths, convention base deployment, user scope via scope-setup, first working scope, CLAUDE.md guard, librarian registration via install-librarian, first index run, wow via exfu-create-wow, buffet. Team-specific beats kept (onboarding pack, two-layer calibration, champion provisioning/seeding/IT briefing/onboarding prep), reframed to v0.3: the shared layer is itself a v0.3 substrate (own convention base, team scope holding ways-of-working.md + team-members.md, own guard); storage choice recorded in user scope context instead of `_meta/storage-backend.md`; no README.md-per-folder; no em-dashes.
- Residual v0.2 sweep: remaining references in `exfu-start` are migration-detection signals (correct), and in `substrate-guide.md` are historical changelog entries (correct). Nothing else to change.
- Verified: `plugin/build/build.sh all` builds all three variants clean, SKILL.md frontmatter validation passes.
- Nothing committed per your standing instruction.
