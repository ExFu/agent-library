---
name: team-shared-skills-authoring
description: Teaches the substrate champion the conventions for skills that go in the team's shared skills/ folder, and helps author or refactor them to those conventions. Shared skills are different from personal ones — every team member's Claude loads them, so they must work for everyone without embedding personal assumptions. Use when the champion wants to create a new shared skill, promote a personal skill to shared, or understand what makes a skill safe to share. Triggers on "I've got a skill that would be useful for the whole team, how do I share it?", "how do I make a skill everyone on the team can use?", "I want all my colleagues' Claude to know about X", "write a shared skill", "promote this skill to shared", or any champion intent to publish a skill to the team.
---

# Team shared skills authoring

A skill that works perfectly for one person often fails everyone else when personal assumptions are embedded in it — hardcoded paths, assumed tools, role-specific framing. Shared skills live in the team's git repo and load for every team member's Claude, so they need to be written without those assumptions. This skill exists to catch the difference before it causes problems, and to help the champion author skills that genuinely work for the whole team.

You are helping the substrate champion write or refactor skills for the team's shared `skills/` folder. Shared skills are different from personal skills. Every team member's Claude loads them. They need to work for everyone on the team, not just the person who wrote them.

**Hard constraints:**
- NEVER commit a shared skill that contains a reference to `context/me/` or any personal substrate path.
- NEVER commit a shared skill that embeds facts specific to one person (their timezone, their preferred tools, their working hours, their role title).
- NEVER use the `git-substrate-sync` skill to commit a shared skill that has failed the hygiene checks below.
- If you detect a violation and the champion wants to proceed anyway, state the risk plainly and ask them to confirm. Do not silently comply.

---

## What makes a skill "shared"

A shared skill is one that:

1. **Makes no personal assumptions.** It does not know who is running it. It does not assume a role, a timezone, a preferred communication style, or a working pattern. If those things matter, the skill asks for them or reads them from a team-level resource.

2. **Declares its dependencies.** If the skill needs `context/team-x/ways-of-working.md`, or a particular scope folder to exist, or a specific tool to be installed, it says so up front. Team members' Claudes will load this skill without the context that the champion had when writing it.

3. **Reaches for team resources, not personal ones.** References go to `context/team-x/`, shared scopes under `scopes/`, or shared databases under `databases/`. Not to `context/me/`, not to a personal scope.

4. **Earns its place in git history.** Every version of a shared skill is tracked. Commit messages explain what changed and why. The history is the changelog.

5. **Has a name that is unique in the team's skill set.** Two skills with the same name create unpredictable loading behaviour. Check for collisions before committing.

---

## Pre-commit hygiene checks

Run these checks before every commit of a shared skill. If any check fails, fix it before committing.

**Check 1: No personal paths.**
Search the skill body for any of these patterns:
- `context/me/`
- `context/my-`
- `scratch/`
- Any path that includes the champion's personal name or username

If found: either remove the reference, replace it with a team-level equivalent, or move the skill back to personal.

**Check 2: No personal assumptions embedded in prose.**
Scan for phrases like:
- "the user prefers X"
- "my timezone is"
- "I usually"
- "as noted in my about-me"
- Specific tool names assumed to be installed (unless declared as a dependency)

If found: generalise or parameterise. If the behaviour only makes sense for one person, the skill probably belongs in their personal substrate.

**Check 3: No name collision.**
Check the team's `skills/` folder. If a skill with the same name already exists, resolve the collision before committing. Options: rename the new skill, update the existing one, or merge them. Do not silently overwrite.

**Check 4: Dependencies declared.**
If the skill references a file, folder, tool, or other skill, that dependency is mentioned explicitly near the top of the skill body. Team members should not have to reverse-engineer what a skill needs in order to use it.

---

## Refactoring a personal skill into a shared one

When the champion has a personal skill they want to promote, follow this process.

**Step 1: Read the skill body in full.**
Look for all four hygiene-check items above. List everything that will need to change.

**Step 2: Identify what is personal and what is general.**
Some parts of the skill may be genuinely specific to the champion (their preferences, their context). Those parts either need to be removed, made optional, or converted into parameters the skill asks for at runtime.

**Step 3: Lift the dependencies.**
Replace personal resource paths with team-level ones. For example:
- `context/me/role.md` becomes `context/team-x/role-conventions.md` (if that file exists) or a runtime question.
- A personal scope path becomes a parameter the skill asks for.

**Step 4: Rewrite the description.**
The description controls when Claude loads the skill. A shared skill's description should describe when *any team member* should use it — not just the champion.

**Step 5: Test it in a fresh context.**
Before committing, read the refactored skill as if you are a new team member who joined yesterday and knows nothing about the champion's personal setup. Does it still make sense? Does it still work?

**Step 6: Commit.**
Use the commit pattern below.

---

## Commit pattern

All changes to shared skills use this commit message format:

```
team-skill: [skill-name] — [what changed]
```

Examples:
```
team-skill: scope-template — add dependency declaration for ways-of-working.md
team-skill: meeting-notes — new skill for capturing team meeting outputs
team-skill: client-brief — refactored from personal; removed role assumption
```

The message goes after the `git add`. The `git-substrate-sync` skill handles the actual commit and push — pass it this message format.

---

## Difference from personal skills

Personal skills live in the user's local substrate (not in the team's git repo). They are private, informal, and can be as idiosyncratic as the person wants. They load for that person's Claude sessions and no-one else's.

Shared skills live in the team's `skills/` folder in the git repo. They are public to the team, subject to git history and review, and must work for everyone. The bar for a shared skill is higher precisely because it will be run by Claudes that do not know the author.

The champion should not feel pressure to put every skill in the shared folder. Most skills should stay personal. A skill earns a place in shared when multiple team members would genuinely benefit from the same behaviour.

---

## Example: writing a new shared skill from scratch

Say the team wants a shared skill for logging decisions in a consistent format.

A poor shared skill:
```
# Decision log
Log this decision in my decisions database, using my usual format.
```
This assumes a personal database path and a personal format. It will not work for anyone else.

A good shared skill:
```
# Decision log

Log a team decision in the shared decisions database at databases/decisions.md.

## Format
Date: [today's date]
Decision: [one sentence]
Owner: [person making or owning the decision]
Rationale: [2-3 sentences]
Status: [open / decided / superseded]

## Dependencies
- databases/decisions.md must exist in the team substrate.
  If it does not, create it with a header row before logging.
```

This skill tells Claude exactly where to write, what format to use, and what to do if the dependency is missing. Any team member can run it.

---

## Working with git-substrate-sync

Once a skill passes all hygiene checks and is ready to commit, hand off to `git-substrate-sync`:

1. The file is staged: `git add skills/[skill-name]/SKILL.md`
2. Commit with the pattern above.
3. Push so the team picks it up on their next pull.

The `git-substrate-sync` skill handles merge conflicts and push hygiene. If a conflict arises on the `skills/` folder (two champions edited the same skill), resolve it before pushing — read both versions, decide which change wins or how to merge them, and commit the resolution with a message explaining what you did.
