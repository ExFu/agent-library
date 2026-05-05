---
name: exfu-migrate-from-fetch-model
description: Use when an install entrypoint detects that the user already has an ExFu setup installed via the old fetch model (fetching skills from exfu.ai/clients/ URLs). Signals include: a wow skill already present, substrate skill installed as a packaged .skill file rather than via plugin, or substrate folder structure already in place (context/me/, scopes/, databases/). Do not invoke this on a clean install.
---

# ExFu Migrate from Fetch Model

Handles users who already have an ExFu install set up via the old fetch model. This skill surfaces only when migration signals are detected. Its job is to replace the old fetched-skill installations with plugin-managed equivalents while leaving the user's personal content entirely untouched.

This is a one-shot skill. It runs once. After it completes, the user is fully on the plugin model and this skill doesn't need to run again.

## Hard constraints

- Do not proceed without explicit user confirmation. Show them what you found and what you're going to do before touching anything.
- Do not touch the user's personal content: `context/`, `scopes/`, `databases/`, `scratch/`, their `wow` content, any file they created. Migration is about replacing the skill packaging, not the substrate.
- Do not delete old skills without first confirming the plugin-managed equivalent exists and is ready to install.
- Do not attempt migration if you cannot confidently identify which old skills are present. Surface what you found, explain your uncertainty, and let the user decide.

## Detection — what to look for

Before invoking this skill, the install entrypoint should have detected at least one of these signals. Verify them:

1. **Packaged wow skill present** — a `wow` skill exists installed in the user's Claude setup, and it was packaged as a `.skill` file rather than coming from the plugin. Indicator: the wow's content references the old URL pattern (`exfu.ai/clients/`) or doesn't mention the plugin as its source.

2. **Substrate bedrock skills installed via old model** — any of these skills are present as user-installed `.skill` packages rather than plugin-managed: `substrate`, `skill-packaging`, `box-filesystem-management`, `reminders`, `inbox`, `writing-styles`. The presence of these as standalone installed skills (not the ones pre-loaded by this plugin) is the key signal.

3. **Substrate folder structure exists** — `context/me/` folder present, or `scopes/` folder present, or `databases/` folder present. This on its own isn't enough to trigger migration (the user may have created these folders independently), but combined with signal 1 or 2 it's strong.

## Confirmation step — required before proceeding

When signals are detected, surface a clear summary to the user. Example:

> "Looks like you already have an ExFu setup. I can see [list what you found: e.g. your wow skill, the substrate skill, and your context/me/ folder]. The plugin includes updated versions of these bundled skills. Migration will:
>
> - Replace your installed copies of [list the old skills] with plugin-managed versions
> - Leave your wow content, your context/me/ files, your scopes, and everything else you've built completely untouched
> - Update the navigation map in your wow skill to note that the bundled skills now come from the plugin
>
> Your personal substrate stays exactly as it is. Confirm to proceed, or say no if you want to check anything first."

Wait for explicit confirmation. If the user says no or wants to check something first, pause and help them check. Do not proceed unilaterally.

## Migration steps

Once confirmed:

### 1. Document what's present

Before making changes, note what you found:
- Which old-model skills are installed (by name)
- Whether a wow skill exists and what's in its navigation map
- Current substrate folder structure (just the top-level shape, not contents)

### 2. Install plugin-managed equivalents

The plugin already contains updated versions of all the bedrock skills. They are available as part of the plugin — the user doesn't need to fetch anything. Confirm each one is available before proceeding.

Skills to confirm and install fresh from the plugin:
- `substrate` (now plugin-managed)
- `skill-packaging` (now plugin-managed)
- `box-filesystem-management` for solo installs, or `git-substrate-sync` for team installs
- `reminders` (if the user had the old version installed)
- `inbox` (if the user had the old version installed)
- `writing-styles` (if the user had the old version installed)

Use `skill-packaging` to present each plugin-managed skill to the user for install. Install in the same order as a fresh install: `skill-packaging` first, then the rest.

### 3. Remove old fetched-skill installations

After each plugin-managed version is confirmed installed, remove the old packaged version. Ask the user to delete the old `.skill` install from their Claude settings, or help them navigate to it. Do not move on to the next skill until the current one is cleanly swapped.

### 4. Update the wow navigation map

Open the user's existing `wow` skill content. In the navigation map section, add a note:

```
Bundled skills (substrate, skill-packaging, box-filesystem-management, reminders, inbox, writing-styles) are now plugin-managed via the ExFu plugin. They no longer need to be installed separately.
```

If the wow previously had notes about fetching from `exfu.ai/clients/`, remove those references — they no longer apply. Repackage and present the updated `wow` for reinstall.

### 5. Verify

After migration, confirm:
- The `substrate` skill loads correctly (try loading it and checking that it can find the knowledge base).
- The user's `context/me/` folder is intact and its contents are unchanged.
- The `wow` skill loads and its navigation map is accurate.
- Any scopes the user had set up are still visible and accessible.

If anything looks wrong, stop and surface it clearly. Don't paper over problems.

## After migration

Tell the user two things:

1. Migration is complete. Their personal substrate — everything they built — is exactly as it was. The only change is where the bundled skills come from (the plugin, not fetched packages). Future updates to those skills will come through plugin version updates, not manual reinstalls.

2. If anything feels off in the next few sessions, they should reach Alastair at `al@exfu.ai`. Migration edge cases are real and worth knowing about.
