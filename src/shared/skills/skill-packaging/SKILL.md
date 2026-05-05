---
name: skill-packaging
description: Addendum to the built-in skill-creator skill. Overrides the default installation method. Load alongside skill-creator whenever creating, updating, or packaging skills. Triggers include any instruction to "install a skill", "create a skill", "package a skill", "update a skill", or any step that involves skill installation.
---

# Skill Packaging (addendum to skill-creator)

This skill supplements the built-in `skill-creator` skill. Load both together. The skill-creator handles the content and structure of skills. This skill overrides how they get delivered.

This skill is for creating and packaging *new* custom skills — skills the user designs themselves. The ExFu bedrock skills (substrate, reminders, inbox, writing-styles, etc.) are pre-installed by the plugin and don't need packaging.

## The rule

**Do NOT write skill files to any `.claude` folder.** Not the global `~/.claude/`, not a project `.claude/`, not anywhere in the filesystem. That is not how skills are installed in this substrate.

The only correct method:

1. Create the `.skill` package (a zip with `.skill` extension, containing a folder with `SKILL.md` at root)
2. Present it to the user
3. The user clicks the link and hits **"Save Skill"** to install it

That's it. Claude packages, the user installs.

## Drafts

Keep a copy of any SKILL.md you create or update in `scratch/` in the substrate. The installed version is read-only; the draft is how you iterate across sessions.
