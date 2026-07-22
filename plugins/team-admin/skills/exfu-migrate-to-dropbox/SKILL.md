---
name: exfu-migrate-to-dropbox
description: Migrates an existing ExFu substrate from Box (or any pre-0.4 storage location) to Dropbox, and brings the installed artefacts up to 0.4 conventions -- refreshed convention base, the renamed exfu-library guard, retired Box workaround machinery (_trash/, _DELETED_ prefixes, box-cleanup), and updated wow references. Use when a user says "move my library to Dropbox", "I copied my substrate to Dropbox", "migrate off Box", "finish the Dropbox move", or when the exfu-library skill detects a legacy Box-backed substrate. Also the upgrade path for any 0.3 substrate after updating to the 0.4 plugin.
---

# Migrate to Dropbox (and to 0.4)

This skill moves a substrate's storage from Box to Dropbox and upgrades its installed artefacts to 0.4. The two go together because 0.4 is the release that retired the Box machinery.

Principles for the whole run:

- **The old Box copy is never modified.** It becomes the read-only fallback. Don't write to it, don't clean it up, don't delete it. If something goes wrong mid-migration, the Box copy is the recovery path.
- **Confirm each destructive step.** Overwriting the guard, deleting `_trash/`, removing registry entries -- each gets a one-line explanation and a yes before it happens.
- **Fix forward in the new copy only.** Any correction happens on the Dropbox side.
- **Narrate as you go.** One step at a time: say what's next and why, do it, show the result.

## Step 0 -- Identify the true source, then confirm access

**Identify the source root before comparing anything, and confirm it with the user.** Old Box setups often contain several similarly named folders from earlier eras (a pre-ExFu vault, a stale sibling from an earlier install, the real root). Comparing against the wrong one produces convincing nonsense. Do all three checks:

1. Read the user's wow for the declared substrate root. It is the user's own statement of where they live.
2. List the candidate folders (e.g. everything matching claude/exfu names in the Box mount) and note each one's most recent modification time.
3. Read `exfu/derived/agent-registry.json` in each candidate AND in the Dropbox copy, and compare `last_run` stamps. The root the scheduled runs are actually writing is the live one -- and if that is still the Box side, the cutover has not happened yet, whatever anyone assumes.

Then say plainly which folder you believe is the source and why, and get the user's confirmation before proceeding. Do not substitute memory of prior sessions for this check.

You need filesystem access to both roots in this session. Use `request_cowork_directory` if either isn't reachable. If the user hasn't copied anything yet, have them copy the whole substrate folder to Dropbox in Finder / File Explorer first (a plain drag-copy is right; don't copy file-by-file through a connector). Wait for Dropbox to finish syncing before continuing.

## Step 1 -- Verify the copy

Compare the Dropbox copy against the Box original before touching anything:

1. Recursively count files and directories in each root (ignore `.DS_Store` and other OS noise, and ignore `_trash/` -- it is deliberately not coming along).
2. Compare the top-level structure: `CLAUDE.md`, `exfu/`, `user/`, `scopes/` must all be present on the Dropbox side.
3. Spot-check a handful of the most recently modified files: same size and content on both sides.
4. Report the comparison plainly. If content files are missing, list them and copy the gaps (Box -> Dropbox, one direction only) before continuing.
5. Derived files that differ (`exfu/derived/`, `exfu/visualisations/`) are expected when the old root's scheduled tasks are still running -- the old side will be a run ahead. Leave them alone; do not copy them across. Step 8 regenerates the new root's derived state from scratch.

**If the comparison shows meaningful divergence rather than a clean copy** -- structural differences, each side carrying files the other lacks, registry stamps that contradict the assumed story -- do not interpret your way past it. **Stop and surface the facts to the user, then wait.** The likeliest explanations are that you compared against the wrong source folder (see Step 0) or that the cutover is incomplete (scheduled tasks still writing the old root). A confident narrative that explains the divergence away is exactly the failure mode to distrust: only the user knows their true setup. Never copy "missing" files across on your own interpretation -- deliberate deletions look identical to accidental gaps from the outside. Resume only on the user's say-so.

## Step 2 -- Refresh the convention base

The `exfu/<version>/` directory is plugin-owned. Replace the Dropbox copy's `exfu/v0.3/` with the current plugin's version:

- Copy `${CLAUDE_PLUGIN_ROOT}/substrate/exfu/v0.3/` over `exfu/v0.3/` at the new root.
- Leave `exfu/latest.txt` as is (it should say `v0.3`; the conventions version has not changed in 0.4).
- Leave `exfu/derived/` and `exfu/visualisations/` alone -- they are the user's generated state.

## Step 3 -- Rewrite the CLAUDE.md guard

The guard text changed in 0.4 (the boot skill is now `exfu-library`). Overwriting the guard requires the user's confirmation -- explain in one line, get the yes, then replace the guard at the new root with exactly:

```
# Don't use this folder

This is the root of an ExFu Agent Library (internally: a substrate).

Do not read, write, or otherwise interact with the contents of this folder
unless your session has loaded the exfu-library skill (or a derivative
that knows the library's conventions).

If you've accidentally been pointed here, stop and ask the user to either:
- Load the exfu-library skill, or
- Work in a different location.

This protects the library from being treated as a generic working folder.
```

## Step 4 -- Retire the Box machinery

With confirmation, in the Dropbox copy only:

1. Delete `_trash/` if it was copied across (nothing in it is live content; the Box original still has it).
2. Find and resolve any `_DELETED_`-prefixed files: they were pending deletion under the old workaround, so delete them (they also still exist in the Box original).
3. Delete `_meta/cleanup.py` and the `_meta/` folder if present (v0.2 leftovers).
4. Open `exfu/derived/agent-registry.json`. If a box-cleanup entry is registered, remove it. Leave every other entry untouched.

## Step 5 -- Update the wow

Read the wow source at `user/skills/wow/` in the new root:

1. Replace any Box paths with the new Dropbox path.
2. If it names `substrate` as the skill it auto-loads, change that to `exfu-library`.
3. Where it glosses vocabulary, align with the 0.4 registers: "your library" and "your librarians" user-facing; "substrate" internal. Don't rewrite the user's own content -- only the references and glosses.
4. Repackage and reinstall via `skill-packaging` so the installed copy matches the source. The user removes the old installed wow and installs the new package.

## Step 6 -- Record the change

Append a short note to the storage record in `user/context/` (wherever the storage choice is recorded; create `user/context/storage.md` if nowhere records it): the date, the move from Box to Dropbox, the old root kept as read-only fallback, and the new root path.

## Step 7 -- Account-side checklist

These live in the user's Claude account, not in the files, so you cannot change them here. Emit this checklist explicitly and walk the user through what applies:

- **Global Instructions:** the substrate root path noted there must be updated to the Dropbox path.
- **Working folder access:** grant Claude access to the Dropbox folder; the Box folder grant can stay (read-only fallback) or be removed later.
- **Connectors:** the Dropbox MCP connector should be connected; the Box connector is no longer needed for the library.
- **Scheduled tasks:** every scheduled task whose prompt contains the old path (nightly-agents, daily-briefing, any custom ones) needs its prompt edited to the new path. If a box-cleanup task exists, delete the task itself.
- **Personal skills:** any personally installed skill that mentions the Box path (the wow is handled in Step 5; check others such as personal reminders or inbox skills) needs its source updated in `user/skills/` and reinstalling.

## Step 8 -- Verify the result

1. Run the index against the new root: `python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/substrate-index/index.py <new-root>` and confirm it writes `exfu/derived/index.json` cleanly.
2. Load `exfu-library` against the new root and confirm the boot sequence completes: backend detected as Dropbox-backed, index read, scopes surfaced, no missing-file errors.
3. Regenerate the dashboard if the user wants the visual confirmation: `python3 ${CLAUDE_PLUGIN_ROOT}/scheduled-tasks/scheduled-agents/dashboard-generator.py <new-root>`.
4. **Cutover completeness.** The migration is not done until the scheduled tasks write the new root. After the user repoints the task prompts (Step 7), check the next run's `last_run` stamps in the Dropbox copy's registry. Until that first Dropbox-rooted run lands, the old root is still the live substrate -- treat it as live, not as a fallback yet.
5. Tell the user what changed, what stayed, where the live root currently is, and that the Box copy freezes into the read-only fallback only once the cutover check passes.
