---
name: team-box-folder-provisioning
description: Walks the substrate champion through creating and sharing the Box folders that form the team's shared substrate. Invoked by exfu-install-team-admin when the champion picks Box as their team's storage backend. The champion provisions one or more Box folders — one per org, one per team, one per scope — and walks colleagues through accepting the shared-folder invitations. Each folder has its own sharing configuration because different scopes have different access groups. Use this skill when the champion says "I picked Box for the team", "set up the team's Box folders", "create the team folders in Box", or when the install-team-admin skill routes here from Step 6 Path B. This skill covers one-time provisioning only; ongoing folder creation and sharing is handled by team-box-folders; ongoing file operations are handled by box-filesystem-management.
---

# Team Box folder provisioning

Box doesn't work like git. There's no single repo everyone clones. Instead, a team's substrate in Box is a set of folders — each independently created, each with its own sharing configuration, because different scopes involve different groups of people. This skill walks the champion through that reality.

This is a one-time setup. By the end, the folders will exist, be structured correctly, be shared with the right people, and be documented so future champions and team members can navigate them.

---

## Why multiple folders

The substrate guide's scope model maps to Box as one folder per scope level:

- **Org folder** — holds org-wide context (public positioning, conventions shared across all teams in the org). Shared with everyone in the org. Create one per org the team belongs to.
- **Team folder** — holds team-level context (ways of working, role conventions, shared databases, shared skills). Shared with all team members.
- **Scope folders** — one per active project, deal, or ongoing work area. Each holds that scope's context, planning, and generated content. Shared only with the people working on that scope — which is often a subset of the team.
- **Personal folders** — one per team member, not shared with anyone. Holds their `context/me/`, personal scopes, and anything that's theirs alone.

The champion creates the org folder (if needed), the team folder, and the initial scope folders. Personal folders are each member's own responsibility.

---

## How to use Box for this

Box's own documentation is the authoritative source for UI steps, because the interface changes. Check https://support.box.com for current guidance on:

- Creating a folder (search "create folder Box")
- Sharing a folder with collaborators (search "invite collaborators Box")
- Setting permission levels — Viewer, Editor, Co-owner (search "Box permission levels")
- The difference between a shared folder and a collaborated folder

Don't rely on steps written here for the exact UI. The concepts below are stable; the button locations are not.

---

## What to set up

**Step 1 — Create the team folder.**
Name it something clear: `[team-name]-substrate` or `[team-name]-shared`. Inside, create the standard substrate structure: `context/`, `databases/`, `skills/`, `scopes/`, `_meta/`.

Under `context/`, add `context/team-[name]/` with a starting `ways-of-working.md`. This is the most important file — every team member's Claude reads it.

**Step 2 — Create the org folder (if needed).**
If the team belongs to one or more orgs, create a separate org-level folder per org. Inside: `context/org-[name]/` with org-wide positioning and conventions. Share this with everyone in the org, not just this team.

**Step 3 — Create initial scope folders.**
For each active project or work area the team has right now, create a scope folder. Name it after the scope: `[scope-name]/`. Inside: `context/`, `planning/`, `generated/`. Share each one only with the people working on it.

**Step 4 — Set sharing for each folder.**
- Team folder: share with all team members. Editor access is standard; Co-owner for the champion.
- Org folder: share with everyone in the org. Viewer access is usually appropriate.
- Scope folders: share with the relevant subset. Editor access for active contributors; Viewer for observers.

**Step 5 — Document the folder structure.**
Create `_meta/folder-map.md` in the team folder. List every folder, what it's for, and who has access. This is the map future champions and team members use to navigate the substrate. Update it when folders are added or sharing changes. Example structure:

```
# Team substrate — folder map

## Team folder: [team-name]-substrate
Shared with: all team members (Editor)
Purpose: team-level context and shared conventions

## Org folder: [org-name]-context
Shared with: all [org-name] staff (Viewer)
Purpose: org-wide conventions and positioning

## Scope folders
- scopes/[scope-1]/   Shared with: Alice, Bob, Carol (Editor)
- scopes/[scope-2]/   Shared with: Alice, Dave (Editor)
```

**Step 6 — Confirm Box Drive is set to always-available.**
On each team member's machine, the shared folders should be set to always available offline (right-click in Finder, "Make Available Offline"). This prevents the offline-caching issue where Claude reads a file and gets empty content because Box hasn't downloaded it yet. Include this step in the joiner onboarding pack.

---

## Joiner experience

Each joiner receives Box shared-folder invitations — one per folder they've been added to. They accept each invitation. The team folder appears in their Box account. They set it to always-available offline. The `install-team` skill then connects their Claude to the folders present in their Box account.

There is no single clone URL. Joiners may receive multiple invitations if they're on several scopes.

---

## Hard constraints

- Personal substrate stays in a folder that is not shared with anyone. The substrate guide's `context/me/` and personal scopes belong there. Don't put them in the team folder.
- No credentials, government IDs, financial details, or regulated PII in any shared Box folder. Same hygiene rules as anywhere else in the substrate.
- Audit your sharing configuration periodically. When people leave teams or scopes, remove them from the relevant folders.

---

## When you're done

Return to `exfu-install-team-admin`. The storage step is complete. Continue with shared-substrate seeding (Step 7).
