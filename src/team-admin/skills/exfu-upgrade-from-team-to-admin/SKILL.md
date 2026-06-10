---
name: exfu-upgrade-from-team-to-admin
description: Handles the in-place upgrade for a team member who is becoming their team's substrate champion. They already have the team plugin installed (with its personal substrate, wow skill, and git connection) and are now installing the team-admin plugin to gain the admin-only capabilities -- repo provisioning, shared-skills authoring, compliance briefing, and onboarding-pack generation. This skill replaces the team plugin's bundled skills with the team-admin plugin's, preserving the personal substrate, wow, and team repo connection entirely. Agent-invoked only -- exfu-install-team-admin calls this when it detects an existing team-plugin install. Do not invoke manually.
---

# Upgrade from team to team-admin

A team member becoming their team's substrate champion needs capabilities the team plugin doesn't include: the ability to provision or reconfigure the team's git repo, author skills for the whole team, generate onboarding packs for new joiners, and surface the compliance briefing for IT review. The upgrade path exists so they don't lose what they've built — their personal substrate, their wow skill, their git connection — while gaining the admin layer on top.

You are handling an in-place upgrade: the user has the exfu-team plugin installed and is now installing exfu-team-admin. This skill replaces the team plugin's bundled skills with the admin plugin's, preserving everything else the user has built.

**Hard constraints:**
- NEVER proceed without explicit user confirmation. State clearly what will change and what will be preserved.
- NEVER remove the user's personal substrate, their `wow` skill, or their connection to the team's git remote.
- NEVER run this skill a second time if the upgrade has already completed. Check the post-upgrade state before acting.
- If anything looks wrong during verification, stop and surface the issue to the user. Do not leave the install in a half-upgraded state silently.

---

## Step 1: Detection

This skill is called from `exfu-install-team-admin` when it detects an existing team-plugin install. Detection criteria (any of these indicates the team plugin is present):

- A skill named `install-team` is installed in this Claude environment.
- A skill named `git-substrate-sync` is installed but no skill named `install-team-admin` is.
- The user's global instructions reference the team plugin by name.

If none of these signals are present, this upgrade is not needed. Return to `install-team-admin` and continue the normal install flow.

---

## Step 2: Explain what is happening

Tell the user:

"It looks like you have the exfu-team plugin installed. Team-admin is a strict superset of the team plugin — it includes everything the team plugin does, plus the admin-only skills for provisioning the team repo, authoring shared skills, onboarding members, and briefing IT.

The recommended path is to replace the team plugin with team-admin in place. Here is what changes and what stays the same:

**What changes:**
- The team plugin's bundled skills are removed.
- The team-admin plugin's bundled skills are installed in their place.
- Your `wow` skill's navigation map is updated to reflect the new skills.

**What is preserved:**
- Your personal substrate (context, scopes, databases — all local, untouched).
- Your `wow` skill content (only the navigation map gets updated).
- Your connection to the team's git remote.
- Any shared skills your team has already authored in the team's `skills/` folder.
- All git history.

This is a one-time operation. Confirm to proceed, or say stop to exit and install team-admin separately."

Wait for explicit confirmation before continuing.

---

## Step 3: Remove team-plugin bundled skills

The team plugin's bundled skills are the ones it installed into this Claude environment at install time. They typically include:

- `install-team`
- `git-substrate-sync` (will be reinstalled by team-admin immediately after)
- Any team-plugin-specific onboarding skills

To identify them precisely: look for skills whose source path or description references the exfu-team plugin. Do not remove skills that were authored by the user or the team — only plugin-bundled ones.

Ask Claude Desktop (or the user, if you cannot inspect installed skills directly) to confirm which skills are currently installed. Remove only the team-plugin bundled set.

If you cannot determine which skills are bundled vs user-authored, ask the user to review the list before removal. Err on the side of preserving user content.

---

## Step 4: Install team-admin bundled skills

Install the team-admin plugin's full skill set from `${CLAUDE_PLUGIN_ROOT}/skills/`. This includes:

- `exfu-start` — the front-door orchestrator; detects first-run vs returning user and routes accordingly
- `exfu-install-team-admin` — the full admin install conversation
- `git-substrate-sync` — handles all git operations for the shared layer (same skill as the team plugin, re-bundled from the team-admin source)
- `team-repo-provisioning` — walks the champion through creating or reconfiguring the team's shared substrate repo on their chosen git provider
- `team-shared-skills-authoring` — helps the champion write or refactor skills for the team's shared skills/ folder, enforcing conventions that make skills work for everyone
- `team-onboard-member` — generates personalised onboarding packs for new joiners to paste into their install conversation
- `exfu-guides` — answers architecture and reference questions about the substrate
- `exfu-create-wow` — generates the user's personal way-of-working skill from the template
- `substrate` — the session-bootstrap skill; orients Claude to the knowledge base at the start of every conversation
- All other shared and team-admin skills in the plugin

Install each skill using the standard plugin skill installation method.

---

## Step 5: Update the wow navigation map

The user's `wow` skill contains a navigation map — the list of capabilities and where to find them. It needs to reflect the new admin-only skills.

Read the user's current `wow` skill. Find the section that lists capabilities or skills. Add entries for:

- `team-repo-provisioning` — "Set up or re-provision the team's shared substrate repo"
- `team-shared-skills-authoring` — "Write or refactor a skill for the team's shared skills folder"
- `team-onboard-member` — "Generate an onboarding pack for a new team member"

If there is already an entry for `install-team`, replace it with an entry for `install-team-admin`.

Write the updated `wow` skill back. Do not change anything else in the wow skill — only the navigation map additions above.

---

## Step 6: Verify post-upgrade state

Check the following. Report on each one.

1. **Team-admin skills installed.** Confirm `install-team-admin`, `team-repo-provisioning`, `team-shared-skills-authoring`, and `team-onboard-member` are all present and loadable.

2. **Team-plugin-only skills removed.** Confirm `install-team` is no longer present. (If it is still present, remove it now.)

3. **git-substrate-sync present.** Confirm it is installed. It is needed by both plugins; reinstalling it during the team-admin install is correct.

4. **Personal substrate intact.** Confirm the user's personal context, scopes, and databases are present and unmodified.

5. **Git remote reachable.** Run `git ls-remote [remote-url]`. If it returns refs, connectivity is intact.

6. **wow updated.** Confirm the navigation map includes the new admin-skill entries.

If all checks pass, report: "Upgrade complete. You now have the full team-admin capability surface. Your personal substrate and team connection are intact."

If any check fails, report the specific failure and what to do about it. Do not mark the upgrade complete until all checks pass.

---

## Step 7: Continue the team-admin install

Return to `exfu-install-team-admin`. The upgrade is a pre-flight step — once it completes cleanly, the rest of the install-team-admin conversation proceeds normally from the post-upgrade state. The champion does not need to start from scratch; they can pick up from wherever makes sense (for example, skipping the about-me beat if their personal context is already well set up, and going straight to the admin-specific beats like shared-substrate seeding and onboarding-prep).
