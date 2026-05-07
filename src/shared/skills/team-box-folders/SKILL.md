---
name: team-box-folders
description: Guides team members and champions through ongoing Box folder work in a team substrate — creating new scope folders, sharing folders with colleagues, understanding existing folder structure, coordinating access changes when people join or leave projects. This is not the initial provisioning step (that is team-box-folder-provisioning, for champions only). This skill covers the day-to-day folder work any team member needs to do after setup is complete. Triggers on phrases like "create a folder for the [project] team", "share this folder with my colleague", "set up a new scope folder in Box", "who has access to the X folder?", "I need to give [person] access to the [folder]", "create a Box folder for [project]", "someone new is joining the project, can they see our Box folder?", "how do I remove someone from the folder?", "what folders does our team use?", or any instruction about Box folder creation, sharing, or access within a team context.
---

# Team Box Folders

Teams using Box for their substrate create folders over time. A new project starts, so a new scope folder is needed. A colleague joins mid-project and needs access. Someone leaves and their access should be revoked. This skill gives any team member a clear path through that ongoing work.

This is not the initial provisioning step. If you are a champion setting up the team's Box folders for the first time, use `team-box-folder-provisioning` instead. Come back here for all subsequent folder work.

---

## How Box folders map to team structure

Your team's substrate in Box is a set of folders, each with its own access configuration:

- **Org folder** — shared with everyone in the org. Holds org-wide context and conventions.
- **Team folder** — shared with all team members. Holds team context, ways of working, shared conventions.
- **Scope folders** — one per project, deal, or ongoing work area. Shared only with the people working on that scope. A scope folder is often a subset of the team.
- **Personal folder** — yours alone. Not shared with anyone.

The champion created the initial structure. You are building on it as the team's work evolves.

---

## Creating a new scope folder

When a new project, deal, or work area starts and needs its own Box home:

**1. Check the existing folder map first.**
Before creating anything, check `_meta/folder-map.md` in the team folder. A folder for this scope may already exist, or the champion may have left a placeholder for it. If you are unsure, check with your champion before creating.

**2. Create the folder in the right place.**
Scope folders live inside the team folder or alongside it, depending on your team's structure. Ask your champion if you are not sure where new scope folders should go. See https://support.box.com for current Box UI steps on creating folders.

**3. Set up the substrate structure inside the new folder.**
Every scope folder should have this structure from the start:

```
[scope-name]/
  README.md            ← create this first, before anything else
  context/             ← hard convention; holds standing context for this scope
  planning/            ← optional; working docs, plans, proposals
  generated/           ← optional; Claude output, drafts, processed content
  databases/           ← optional; scope-specific reference data
```

Write the `README.md` first. It should explain: what this scope is, who is working on it, and which other folders or repos it relates to. Three sections: Purpose, Contents, Dependencies.

**4. Update the folder map.**
Add the new scope folder to `_meta/folder-map.md` in the team folder. Include: folder name, who has access, and what it is for. Keep this map current — it is the reference every team member's Claude uses to navigate the substrate.

**5. Share the folder (see Sharing patterns below).**

---

## Sharing a folder with new colleagues

When someone joins a project or needs access to a folder:

1. Get their Box account email address.
2. Share the specific folder with them via Box's collaborator invitation. See https://support.box.com for current steps (search "invite collaborators Box").
3. Set the right permission level:
   - **Editor** — for active contributors who will read and write files.
   - **Viewer** — for people who only need to read.
   - **Co-owner** — for other champions managing the folder structure.
4. Tell them to accept the invitation and set the folder to always available offline (right-click in Finder, "Make Available Offline"). This prevents the offline-caching issue where Box hasn't downloaded files yet and they come back empty.
5. Update `_meta/folder-map.md` to reflect the new access.

Share the most specific folder that covers what the person needs. If they are working on one scope, share that scope folder — not the whole team folder.

---

## Understanding existing folder structure

If you are new to the team or joining an existing project:

1. Start with `_meta/folder-map.md` in the team folder. It lists every folder, what it is for, and who has access. If it is missing or out of date, ask your champion.
2. Inside each folder, start with the `README.md` at the root. It explains purpose, contents, and dependencies.
3. The `context/` folder inside any scope is the richest source of standing context. Read it before doing substantive work in that scope.

If you cannot find a folder that should exist, or if you are not sure whether you have the right access, check with your champion rather than creating a duplicate folder.

---

## Revoking access when someone leaves a project or the team

When a person leaves a scope or the team:

1. Remove them from the relevant scope folders in Box. See https://support.box.com for current steps (search "remove collaborator Box").
2. If they are leaving the team entirely, remove them from the team folder as well.
3. Update `_meta/folder-map.md` to reflect the change.

Do this promptly. Stale access is a hygiene risk. The champion should have a clear process for this; if yours does not, propose one.

---

## Sharing patterns

| Folder type  | Who to share with               | Typical permission |
|-------------|--------------------------------|--------------------|
| Org folder   | Everyone in the org             | Viewer             |
| Team folder  | All team members                | Editor             |
| Scope folder | People working on that scope    | Editor             |
| Personal     | No one                          | (not shared)       |

These are the defaults. Your team may have variations. Check `context/team-[name]/ways-of-working.md` in the team folder for your team's specific conventions.

---

## Hard constraints

- **Write the README before adding anything else to a new folder.** A folder without a README is navigational debt from day one.
- **Do not share any folder that contains personal substrate.** If `context/me/` exists anywhere in a folder tree, do not share that folder with anyone. Personal substrate stays personal.
- **Do not put credentials, government IDs, financial account numbers, or regulated personal information in any shared Box folder.** If you are not sure whether something counts, treat it as if it does.
- **Revoke access promptly when someone leaves.** Do not leave it for later.

---

## After folders are set up

Once a folder exists and is shared, ongoing file work (reading, writing, organising files inside the folders) is handled by `box-filesystem-management`.
