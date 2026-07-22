---
name: team-dropbox-folder-provisioning
description: Walks the substrate champion through creating and sharing the Dropbox folders that form the team's shared Agent Library. Invoked by exfu-install-team-admin when the champion picks Dropbox as their team's storage backend. The champion provisions one or more Dropbox folders -- one per org, one per team, one per scope -- and walks colleagues through accepting the shared-folder invitations. Each folder has its own sharing configuration because different scopes have different access groups. Use this skill when the champion says "I picked Dropbox for the team", "set up the team's Dropbox folders", "create the team folders in Dropbox", or when the install-team-admin skill routes here from the storage step's Dropbox path. This skill covers one-time provisioning only; ongoing file operations are handled by exfu-dropbox-storage.
---

# Team Dropbox folder provisioning

Dropbox doesn't work like git. There's no single repo everyone clones. Instead, a team's shared library in Dropbox is a set of folders -- each independently created, each with its own sharing configuration, because different scopes involve different groups of people. This skill walks the champion through that reality.

This is a one-time setup. By the end, the folders will exist, be structured correctly, be shared with the right people, and be documented so future champions and team members can navigate them.

---

## Why multiple folders

The substrate guide's scope model maps to Dropbox as one folder per scope level:

- **Org folder** -- holds org-wide context (public positioning, conventions shared across all teams in the org). Shared with everyone in the org. Create one per org the team belongs to.
- **Team folder** -- holds team-level context (ways of working, role conventions, shared databases, shared skills). Shared with all team members.
- **Scope folders** -- one per active project, deal, or ongoing work area. Each holds that scope's context, planning, and generated content. Shared only with the people working on that scope -- which is often a subset of the team.
- **Personal folders** -- one per team member, not shared with anyone. Holds their personal library: user scope, personal scopes, anything that's theirs alone.

The champion creates the org folder (if needed), the team folder, and the initial scope folders. Personal folders are each member's own responsibility.

---

## How to use Dropbox for this

Dropbox's own documentation is the authoritative source for UI steps, because the interface changes. Check https://help.dropbox.com for current guidance on:

- Creating and sharing a folder (search "share a folder Dropbox")
- Permission levels -- can edit vs can view (search "shared folder permissions Dropbox")
- Managing shared-folder membership (search "manage shared folder members Dropbox")

Don't rely on steps written here for the exact UI. The concepts below are stable; the button locations are not.

---

## What to set up

**Step 1 -- Create the team folder.**
Name it something clear: `[team-name]-library` or `[team-name]-shared`. Leave it empty. The install conversation seeds it through the champion's synced Dropbox folder: the folder structure and ground rules (`exfu/`), the team's scope under `scopes/` with its ways-of-working, and the guard file. Don't invent structure here.

**Step 2 -- Create the org folder (if needed).**
If the team belongs to one or more orgs, create a separate org-level folder per org. Inside: `context/org-[name]/` with org-wide positioning and conventions. Share this with everyone in the org, not just this team.

**Step 3 -- Plan the scope folders.**
Shared work areas live under `scopes/` in the team folder and are created during the install's seeding step (the scope-setup skill builds each one to the current conventions, with content). Your job here is the access plan: which scopes exist now, and who should see each one. Note that Dropbox only supports a shared folder inside another shared folder in limited configurations -- when a scope needs a *narrower* group than the team, create it as its own top-level shared folder rather than nesting it inside the team folder, and record where it lives in the access map.

**Step 4 -- Set sharing for each folder.**
- Team folder: share with all team members. "Can edit" access is standard; the champion is the folder owner.
- Org folder: share with everyone in the org. "Can view" access is usually appropriate.
- Scope folders: share with the relevant subset. "Can edit" for active contributors; "can view" for observers.

**Step 5 -- Document who can see what.**
Dropbox access is invisible from inside the folder tree, so record it. Write the access map into the team scope's context (e.g. `scopes/[team-name]/context/dropbox-access-map.md`, once the install has seeded that scope): every shared folder, what it's for, and who has access. Future champions and members navigate sharing from this file; update it when folders are added or sharing changes. Example structure:

```
# Team library -- access map

## Team folder: [team-name]-library
Shared with: all team members (can edit)
Purpose: team-level context and shared conventions

## Org folder: [org-name]-context
Shared with: all [org-name] staff (can view)
Purpose: org-wide conventions and positioning

## Scope folders
- scopes/[scope-1]/    Shared with: Alice, Bob, Carol (can edit)
- [scope-2]-library/   Shared with: Alice, Dave (can edit; own top-level folder, narrower group than team)
```

**Step 6 -- Confirm the folders stay hydrated.**
On each team member's machine, the shared folders should be set to always available offline (right-click, "Make Available Offline"). This prevents the online-only issue where Claude reads a file and gets empty content because Dropbox hasn't downloaded it yet. Include this step in the joiner onboarding pack.

---

## Joiner experience

Each joiner receives Dropbox shared-folder invitations -- one per folder they've been added to. They accept each invitation. The folder appears in their Dropbox. They set it to always available offline. The `install-team` skill then connects their Claude to the folders present in their Dropbox.

There is no single clone URL. Joiners may receive multiple invitations if they're on several scopes.

---

## Hard constraints

- Personal library stays in a folder that is not shared with anyone. The user scope and personal scopes belong there. Don't put them in the team folder.
- No credentials, government IDs, financial details, or regulated PII in any shared Dropbox folder. Same hygiene rules as anywhere else in the substrate.
- Audit your sharing configuration periodically. When people leave teams or scopes, remove them from the relevant folders.
- Concurrent edits produce Dropbox "conflicted copy" files rather than merges. Keep shared files focused and single-author where possible; reconcile conflicted copies promptly (the exfu-dropbox-storage skill covers how).

---

## When you're done

Return to `exfu-install-team-admin`. The storage step is complete. Continue with shared-substrate seeding (Step 7).
